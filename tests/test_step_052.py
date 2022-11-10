import unittest, tempfile, json, pathlib, hashlib, os

from docreview.store import Store


class RetryTests(unittest.TestCase):
    def test_retry_budget(self):
        with tempfile.TemporaryDirectory() as d:
            s = Store(pathlib.Path(d) / "s")
            r = s.create("a" * 64, "x", "x")
            for n in range(3):
                claim = s.claim("w")
                s.fail(r["id"], claim["version"], "OCR failed")
            self.assertEqual(s.get(r["id"])["status"], "failed")
            self.assertIsNone(s.claim("w"))
            self.assertEqual(s.lease(r["id"])["attempts"], 3)
