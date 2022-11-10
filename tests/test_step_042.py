import unittest, tempfile, json, pathlib, hashlib, os

from docreview.api import create_server
from urllib.request import urlopen
import threading


class ExportAPITests(unittest.TestCase):
    def test_exports(self):
        with tempfile.TemporaryDirectory() as d:
            s = create_server(d, port=0)
            t = threading.Thread(target=s.serve_forever, daemon=True)
            t.start()
            try:
                with urlopen(f"http://127.0.0.1:{s.server_port}/api/feedback") as r:
                    self.assertEqual(json.load(r), [])
            finally:
                s.shutdown()
                s.server_close()
                t.join()
