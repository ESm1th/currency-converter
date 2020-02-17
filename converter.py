import os
import sys
import logging
import json
from json.decoder import JSONDecodeError
from collections import OrderedDict
from datetime import datetime, timedelta
from http.client import HTTPSConnection
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import TCPServer


# define and set up logger
formatter = logging.Formatter(
    fmt='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d-%m-%Y - %H:%M:%S'
)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)

logger = logging.getLogger('server')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

# server settings
HOST = 'localhost'
PORT = 8000


class CurrencyConverterRequestHandler(BaseHTTPRequestHandler):

    _rate = None
    _content_type = 'application/json'

    def do_POST(self):

        if self.path == '/convert/':
            content_length = int(self.headers['Content-Length']) 
            body = self.rfile.read(content_length)

            try:
                post_data = json.loads(body)
                try:
                    amount = float(post_data.get('amount'))
                    self.check_rate()
                    self.prepare_response(HTTPStatus.OK)
                    self.wfile.write(self.convert(amount))
                except ValueError:
                    self.prepare_response(HTTPStatus.BAD_REQUEST)
                    error = (
                        'Value of <amount> key in POST request should be '
                        'a digit, but <{passed}> were passed.'
                    ).format(passed=post_data.get('amount'))
                    self.wfile.write(
                        self.bad_request(HTTPStatus.BAD_REQUEST, error)
                    )
            except JSONDecodeError:
                self.prepare_response(HTTPStatus.BAD_REQUEST)
                self.wfile.write(
                    self.bad_request(
                        HTTPStatus.BAD_REQUEST,
                        'POST request should be used with parameter <amount>.'
                    )
                )
        else:
            self.prepare_response(HTTPStatus.NOT_FOUND)
            error = (
                'The path <{path}> does not exists.'
            )
            self.wfile.write(
                self.bad_request(HTTPStatus.NOT_FOUND, error)
            )

    def prepare_response(self, status) -> None:
        """Setting appropriate headers and status for response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def check_rate(self) -> None:
        """
        Checking that `self._rate` attribute exists. If exists checks timedelta
        for utcnow() and `self._rate` timestamp attribute. If this value is
        equal or greater then 18000 seconds - updates `self._rate` attrubute,
        otherwise use it as it is now.
        """
        if self._rate:
            delta = datetime.utcnow() - self._rate['timestamp']
            if delta >= 18000:
                self._rate = self.get_convertion_rate()
        else:
            self._rate = self.get_convertion_rate()
    
    def convert(self, amount: float) -> bytes:
        """Returns bytes with data about requested conversation."""
        data = {
            'from': self._rate['base'],
            'amount': amount,
            'to': 'RUB',
            'result': amount * self._rate['rate']
        }
        return bytes(json.dumps(data), 'utf-8')
    
    def bad_request(self, status_code: int, error: str) -> bytes:
        """Returns bytes with data about status code and error message."""
        data = {
            'status_code': status_code,
            'error': error
        }
        return bytes(json.dumps(data), 'utf-8')

    def get_convertion_rate(self) -> dict:
        """
        Send request to free API to get exchange rates from `USD` to all
        other currencies and then return dict with exchange rate for
        only russian `RUB`, `USD` as `base` key currency and timestamp
        for caching purposes.
        """
        connection = HTTPSConnection('api.exchangerate-api.com')
        connection.request('GET', '/v4/latest/USD')
        response = connection.getresponse()
        data = json.loads(response.read())
        return {
            'base': data['base'],  # USD
            'timestamp': datetime.utcnow(),  # for caching purposes
            'rate': data['rates']['RUB']
        }


if __name__ == '__main__':
    address = (HOST, PORT)
    http_server = HTTPServer(address, CurrencyConverterRequestHandler)
    try:
        logger.info('Server started')
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()
        logger.info('Server stopped')
