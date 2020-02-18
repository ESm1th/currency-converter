import sys
import logging
import json
from json.decoder import JSONDecodeError
from http.server import BaseHTTPRequestHandler, HTTPServer

from converter import CurrencyConverter
from response import (
    ConvertResponse,
    ValueErrorResponse,
    JsonDecodeErrorResponse
)


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
PORT = 8080


class CurrencyConverterRequestHandler(BaseHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        self.converter = CurrencyConverter()
        super().__init__(*args, **kwargs)

    def do_POST(self):
        if self.path == '/convert/':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)

            try:
                post_data = json.loads(body)
                amount = post_data.get('amount')

                try:
                    ConvertResponse(self).handle(float(amount))
                except ValueError:
                    ValueErrorResponse(self).handle(amount)

            except JSONDecodeError:
                JsonDecodeErrorResponse(self).handle()
        else:
            JsonDecodeErrorResponse(self).handle()


if __name__ == '__main__':
    address = (HOST, PORT)
    http_server = HTTPServer(address, CurrencyConverterRequestHandler)
    try:
        logger.info('Server started')
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()
        logger.info('Server stopped')