import json
import socket
import warnings
import unittest
from unittest import TestCase
from threading import Thread
from http import HTTPStatus
from http.server import HTTPServer
from http.client import HTTPConnection

from server import CurrencyConverterRequestHandler


class TestAPI(TestCase):

    def setUp(self):
        """
        Create test fixtures:
            - test server in separate thread
            - connection object to send requests with it
            - valid payload for `POST` requests
            - invalid payload for `POST` requests
        """
        warnings.simplefilter('ignore', ResourceWarning)

        host = 'localhost'
        port = self.get_free_port()

        self.server = HTTPServer((host, port), CurrencyConverterRequestHandler)
        server_thread = Thread(target=self.server.serve_forever)
        server_thread.setDaemon(True)
        server_thread.start()

        self.connection = HTTPConnection(host, port=port)
        self.valid_payload = {'amount': 10}
        self.invalid_value_payload = {'amount': 'ten'}

    def get_free_port(self):
        """Return free available port on `localhost`."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', 0))
        _, port = sock.getsockname()
        sock.close()
        return port

    def make_request(self, method='GET', path=None, payload=None):
        """
        Make request with connection with appropriate method, path and payload.
        Parameters:
            - method: default='GET' represent HTTP method
            - path: default=None
        """
        self.connection.request(method, path, body=payload)
        response = self.connection.getresponse()
        self.connection.close()
        return response

    def make_post_convert_request(self, payload: str) -> None:
        """
        Retrun response from `POST` request on `convert` route.
        Parameters:
            - `payload`: json string from python dict.
        """
        return self.make_request(
            method='POST',
            path='/convert/',
            payload=payload
        )

    def test_send_valid_post_convert_request(self):
        data = json.dumps(self.valid_payload)
        response = self.make_post_convert_request(payload=data)
        self.assertEqual(response.status, HTTPStatus.OK)

    def test_converter_convert(self):
        data = json.dumps({'amount': 1})
        unit_response = self.make_post_convert_request(payload=data)
        one_usd = json.loads(unit_response.read()).get('result')

        response = self.make_post_convert_request(
            payload=json.dumps(self.valid_payload)
        )
        response_data = json.loads(response.read())

        self.assertEqual(response.status, HTTPStatus.OK)
        self.assertEqual(
            response_data.get('result'),
            one_usd * self.valid_payload['amount']
        )

    def test_value_error_response(self):
        error = (
            'Value of <amount> key in POST request should be '
            'a digit, but <{passed}> were passed.'
        ).format(passed=self.invalid_value_payload['amount'])

        data = json.dumps(self.invalid_value_payload)
        response = self.make_post_convert_request(payload=data)
        response_data = json.loads(response.read())

        self.assertEqual(response.status, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response_data['error'], error)

    def test_json_decode_error_response(self):
        error = 'POST request should be used with parameter <amount>.'
        data = json.dumps({'value': 10})
        response = self.make_post_convert_request(payload=data)
        response_data = json.loads(response.read())

        self.assertEqual(response.status, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response_data['error'], error)

    def test_path_does_not_exist(self):
        url_path = '/not-exist/'
        response = self.make_request('POST', path=url_path)
        error = 'Path {url_pice} does not exist.'.format(url_pice=url_path)
        response_data = json.loads(response.read())

        self.assertEqual(response.status, HTTPStatus.NOT_FOUND)
        self.assertEqual(response_data['error'], error)

    def test_get_request(self):
        response = self.make_request()
        self.assertEqual(response.status, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_put_request(self):
        response = self.make_request('PUT')
        self.assertEqual(response.status, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_head_request(self):
        response = self.make_request('HEAD')
        self.assertEqual(response.status, HTTPStatus.METHOD_NOT_ALLOWED)

    def tearDown(self):
        self.server.shutdown()


if __name__ == '__main__':
    unittest.main()
