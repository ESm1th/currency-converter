import json
import socket
import warnings
from unittest import TestCase
from threading import Thread
from http import HTTPStatus
from http.server import HTTPServer
from http.client import HTTPConnection

from server import CurrencyConverterRequestHandler


class TestAPI(TestCase):

    def setUp(self):
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
        self.connection.request(method, path, body=payload)
        response = self.connection.getresponse()
        self.connection.close()
        return response

    def test_send_valid_request(self):
        data = json.dumps(self.valid_payload)
        response = self.make_request(
            method='POST', path='/convert/',
            payload=data
        )
        self.assertEqual(response.status, HTTPStatus.OK)

    def tearDown(self):
        self.server.shutdown()
