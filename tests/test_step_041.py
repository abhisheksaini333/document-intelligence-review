import unittest, tempfile, json, pathlib, hashlib, os

from docreview.api import create_server
from urllib.request import urlopen
import threading


class ImageAPITests(unittest.TestCase):
    def test_image_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            from docreview.fixtures import render, records

            p = render(records()[0], pathlib.Path(d) / "x.png")
            s = create_server(pathlib.Path(d) / "data", port=0)
            r = s.pipeline.ingest(p.read_bytes(), "x.png")
            t = threading.Thread(target=s.serve_forever, daemon=True)
            t.start()
            try:
                with urlopen(
                    f'http://127.0.0.1:{s.server_port}/api/documents/{r["id"]}/image'
                ) as response:
                    self.assertEqual(response.read(), p.read_bytes())
                    self.assertEqual(response.headers["Content-Type"], "image/png")
            finally:
                s.shutdown()
                s.server_close()
                t.join()
