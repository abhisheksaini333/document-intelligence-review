import unittest, tempfile, json, pathlib, hashlib, os

from docreview.api import create_server
from urllib.request import urlopen
import threading


class APITests(unittest.TestCase):
    def test_real_http(self):
        with tempfile.TemporaryDirectory() as d:
            server = create_server(d, port=0)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                with urlopen(
                    f"http://127.0.0.1:{server.server_port}/api/documents"
                ) as r:
                    self.assertEqual(json.load(r), [])
            finally:
                server.shutdown()
                server.server_close()
                thread.join()
