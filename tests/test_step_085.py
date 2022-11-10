import unittest, tempfile, json, pathlib, hashlib, os

from docreview.api import create_server
import socket, threading, time


class DeadlineTests(unittest.TestCase):
    def test_trickle_body_timeout(self):
        with tempfile.TemporaryDirectory() as d:
            server = create_server(d, port=0, request_timeout=0.2)
            t = threading.Thread(target=server.serve_forever, daemon=True)
            t.start()
            try:
                with socket.create_connection(
                    ("127.0.0.1", server.server_port), timeout=2
                ) as client:
                    client.sendall(
                        b"POST /api/documents HTTP/1.1\r\nHost: localhost\r\nContent-Type: application/json\r\nContent-Length: 100\r\n\r\n{"
                    )
                    time.sleep(0.3)
                    response = client.recv(4096)
                    self.assertIn(b"408", response)
            finally:
                server.shutdown()
                server.server_close()
                t.join()
