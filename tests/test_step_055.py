import unittest, tempfile, json, pathlib, hashlib, os

from docreview.store import Store, Conflict


class CancelTests(unittest.TestCase):
    def test_cancel(self):
        with tempfile.TemporaryDirectory() as d:
            s = Store(pathlib.Path(d) / "s")
            r = s.create("a" * 64, "x", "x")
            claim = s.claim("w")
            done = s.cancel(r["id"], claim["version"])
            self.assertEqual(done["status"], "rejected")
            with self.assertRaises(Conflict):
                s.result(r["id"], claim["version"], {})
