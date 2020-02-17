import os
import sys
import json
import logging
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

    def do_GET(self):
        if not self._rate:
            self._rate = self.get_convertion_rate()
        elif self._rate:
            delta = datetime.utcnow() - self._rate['timestamp']
            if delta.seconds >= 18000:
                print('big')
                self._rate = self.get_convertion_rate()
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', self._content_type)
        self.end_headers()
        self.wfile.write(self.convert(1))

    def convert(self, amount: float) -> bytes:
        """Return bytes with data about requested conversation."""
        data = {
            'from': self._rate['base'],
            'amount': amount,
            'to': 'RUB',
            'result': amount * self._rate['rate']
        }
        return bytes(json.dumps(data), 'utf-8')

    def get_convertion_rate(self) -> dict:
        """Send request to free API to get exchange rates from `USD` to all
        other currencies and then return dict with exchange rate for
        only russian `RUB`, `USD` as `base` key currency and timestamp
        for caching purposes."""
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
