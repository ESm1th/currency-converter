import json
from abc import ABC, abstractmethod
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler


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
        Method used handlers converter class to process conversation from
        passed `USD` amount argument to `RUB` amount. Format response and
        send it to client.
        """
        converter = self.handler.converter

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
        Method uses handler to response to `ValueError`. It format response,
        add `error` to response data and send it to client.
        """
        error = (
            'Value of <amount> key in POST request should be '
            'a digit, but <{passed}> were passed.'
        ).format(passed=amount)
        self.send({'error': error})


class JsonDecodeErrorResponse(Response):

    """
    Class represent `400 BAD REQUEST` response with error from
    `JSONDecodeError` exception.
    """

    status_code = HTTPStatus.BAD_REQUEST

    def handle(self) -> None:
        """
        Method uses handler to response to `JSONDecodeError`. It format
        response, add `error` to response data and send it to client.
        """
        error = 'POST request should be used with parameter <amount>.'
        self.send({'error': error})
