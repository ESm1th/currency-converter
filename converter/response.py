import json
from abc import ABC, abstractmethod
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler

from converter import CurrencyConverter


converter = CurrencyConverter()


class Response(ABC):

    """Base response class."""

    status_code: str

    def __init__(self, handler: BaseHTTPRequestHandler) -> None:
        self.handler = handler
        super().__init__()

    def send(self, data: dict) -> None:
        """Setting appropriate headers and status for response."""
        self.handler.send_response(self.status_code)
        self.handler.send_header('Content-Type', 'application/json')
        self.handler.end_headers()
        self.handler.wfile.write(bytes(json.dumps(data), 'utf-8'))

    @abstractmethod
    def handle(self, *args) -> None:
        pass


class ConvertResponse(Response):

    """Class represent `200 OK` response with converted data."""

    status_code = HTTPStatus.OK

    def handle(self, amount: float) -> None:
        """
        Method used `converter` object to process conversation from
        passed `USD` amount argument to `RUB` amount. Format response and
        send it to client.
        """
        if not converter.check_rate():
            converter.update()

        response_data = converter.convert(amount)
        self.send(response_data)


class ValueErrorResponse(Response):

    """
    Class represents `400 BAD REQUEST` response with error from
    `ValueError` exception.
    """

    status_code = HTTPStatus.BAD_REQUEST

    def handle(self, amount: str) -> None:
        """
        Method uses handler to respond to `ValueError`. It format response,
        add `error` to response data and send it to client.
        """
        error = (
            'Value of <amount> key in POST request should be '
            'a digit, but <{passed}> were passed.'
        ).format(passed=amount)
        self.send({'error': error})


class InvalidKeyResponse(Response):

    """
    Class represent `400 BAD REQUEST` response with error when client send bad
    data to POST request. For example the valid key for url is `amount`, but
    client sent request with another key.

    Example with `httpie` module:
        - valid: http POST http://host:port/convert/ amount=10
        - invalid: http POST http://host:port/convert/ bad_key=...
    """

    status_code = HTTPStatus.BAD_REQUEST

    def handle(self) -> None:
        """
        Method uses handler to respond to invalid request. It format
        response, add `error` to response data and send it to client.
        """
        error = 'POST request should be used with parameter <amount>.'
        self.send({'error': error})


class NotFoundResponse(Response):

    """
    Class represent `404 NOT FOUND` response with error when route for path
    does not exist.
    """

    status_code = HTTPStatus.NOT_FOUND

    def handle(self, path: str) -> None:
        """
        Method uses handler to respond to request when route does not exist.
        It format response, add `error` to response data and send it to client.
        """
        error = 'Path {url_pice} does not exist.'.format(url_pice=path)
        self.send({'error': error})


class MethodNotAllowedResponse(Response):

    """
    Class represent `405 Method Not Allowed` response with error when client
    used method that not allowed by server.
    """

    status_code = HTTPStatus.METHOD_NOT_ALLOWED

    def handle(self) -> None:
        """
        Method uses handler to respond to request when client used method that
        not allowed by server. It format response, add `error` to response data
        and send it to client.
        """
        error = "Request method not allowed."
        self.send({'error': error})
