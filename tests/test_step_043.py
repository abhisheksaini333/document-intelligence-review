import unittest, tempfile, json, pathlib, hashlib, os

from docreview.api import create_server
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import threading


class AccessTests(unittest.TestCase):
    def test_missing_token(self):
        with tempfile.TemporaryDirectory() as d:
            s = create_server(d, port=0, token="secret")
            t = threading.Thread(target=s.serve_forever, daemon=True)
            t.start()
            try:
                with self.assertRaises(HTTPError) as c:
                    urlopen(
                        Request(
                            f"http://127.0.0.1:{s.server_port}/api/documents",
                            data=b"{}",
                            headers={"Content-Type": "application/json"},
                        )
                    )
                self.assertEqual(c.exception.code, 401)
            finally:
                s.shutdown()
                s.server_close()
                t.join()
