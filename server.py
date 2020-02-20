import os
import sys
import logging
import json
from json.decoder import JSONDecodeError
from http.server import BaseHTTPRequestHandler, HTTPServer

from response import (
    ConvertResponse,
    ValueErrorResponse,
    NotFoundResponse,
    InvalidKeyResponse,
    MethodNotAllowedResponse
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
HOST = os.getenv('HOST') or 'localhost'
PORT = os.getenv('PORT') or 8000


class CurrencyConverterRequestHandler(BaseHTTPRequestHandler):

    """
    Class handle only `POST` request with parameter `amount` in request.
    For example valid request to sevice if it running on localhost and port
    8000 using `httpie` python app:
        - http POST http://loaclhost:8000/convert/ amount=10
    """

    @property
    def default_log_text(self):
        """Default log text to start log message."""
        return '{version} - {path} - Request from client {address} '.format(
            version=self.request_version,
            path=self.path,
            address=self.client_address
        )

    def not_allowed_response(self, method: str) -> None:
        """Create `MethodNotAllowedResponse` and handle request."""
        logger.error(
            self.default_log_text +
            'with method {method} not allowed.'.format(method=method)
        )
        return MethodNotAllowedResponse(self).handle()

    def do_GET(self) -> None:
        return self.not_allowed_response('GET')

    def do_PUT(self) -> None:
        return self.not_allowed_response('PUT')

    def do_HEAD(self) -> None:
        return self.not_allowed_response('HEAD')

    def do_POST(self) -> None:
        """
        Process request to convert passed amount. Only working with
        path `/convert/`.
        """
        if self.path == '/convert/':

            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)

            try:
                post_data = json.loads(body)
                amount = post_data.get('amount')

                if amount:
                    try:
                        logger.info(
                            self.default_log_text +
                            'to convert {amount} USD'.format(
                                address=self.client_address,
                                amount=amount
                            )
                        )
                        return ConvertResponse(self).handle(float(amount))
                    except ValueError:
                        logger.info(
                            self.default_log_text +
                            'to convert unappropriate type: {type} '
                            'value: {value}'.format(
                                address=self.client_address,
                                type=type(amount),
                                value=amount
                            )
                        )
                        return ValueErrorResponse(self).handle(amount)
                else:
                    logger.info(
                        self.default_log_text +
                        'with invalid `POST` parameters: {post_data}'.format(
                            address=self.client_address,
                            type=type(amount),
                            post_data=post_data
                        )
                    )
                    return InvalidKeyResponse(self).handle()
            except JSONDecodeError:
                logger.info(
                    self.default_log_text +
                    'without any parameters'.format(
                        address=self.client_address,
                    )
                )
                return InvalidKeyResponse(self).handle()
        else:
            logger.info(
                self.default_log_text +
                '{path} not found'.format(path=self.path)
            )
            return NotFoundResponse(self).handle(self.path)


if __name__ == '__main__':
    address = (HOST, PORT)
    http_server = HTTPServer(address, CurrencyConverterRequestHandler)
    try:
        logger.info('Server started')
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()
        logger.info('Server stopped')
