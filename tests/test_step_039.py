import unittest, tempfile, json, pathlib, hashlib, os

from docreview.api import create_server
from docreview.fixtures import render, records
from urllib.request import urlopen, Request
import threading, base64


class UploadTests(unittest.TestCase):
    def test_upload(self):
        with tempfile.TemporaryDirectory() as d:
            p = render(records()[0], pathlib.Path(d) / "x.png")
            s = create_server(pathlib.Path(d) / "data", port=0)
            t = threading.Thread(target=s.serve_forever, daemon=True)
            t.start()
            try:
                data = json.dumps(
                    {
                        "filename": "invoice.png",
                        "image": base64.b64encode(p.read_bytes()).decode(),
                    }
                ).encode()
                with urlopen(
                    Request(
                        f"http://127.0.0.1:{s.server_port}/api/documents",
                        data=data,
                        headers={"Content-Type": "application/json"},
                    )
                ) as r:
                    self.assertEqual(json.load(r)["status"], "queued")
            finally:
                s.shutdown()
                s.server_close()
                t.join()
