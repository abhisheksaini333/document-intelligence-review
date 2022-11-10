import unittest, tempfile, json, pathlib, hashlib, os

from docreview.api import create_server
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import threading


class ReviewAPITests(unittest.TestCase):
    def test_conflict(self):
        with tempfile.TemporaryDirectory() as d:
            s = create_server(d, port=0)
            r = s.pipeline.store.create("a" * 64, "x", "x")
            s.pipeline.store.result(r["id"], 1, {"fields": {}})
            t = threading.Thread(target=s.serve_forever, daemon=True)
            t.start()
            try:
                data = json.dumps(
                    {
                        "version": 1,
                        "fields": {},
                        "label": "invoice",
                        "reviewer": "alice",
                        "action": "save",
                    }
                ).encode()
                with self.assertRaises(HTTPError) as c:
                    urlopen(
                        Request(
                            f'http://127.0.0.1:{s.server_port}/api/documents/{r["id"]}/review',
                            data=data,
                            headers={"Content-Type": "application/json"},
                        )
                    )
                self.assertEqual(c.exception.code, 409)
            finally:
                s.shutdown()
                s.server_close()
                t.join()
