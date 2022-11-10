import unittest, tempfile, json, pathlib, hashlib, os

from docreview.store import Store, Conflict


class ReviewTests(unittest.TestCase):
    def test_stale_edits(self):
        with tempfile.TemporaryDirectory() as d:
            s = Store(pathlib.Path(d) / "s")
            r = s.create("a" * 64, "a", "x")
            s.result(r["id"], 1, {"fields": {}})
            r = s.review(r["id"], 2, {"total": "$10"}, "invoice", "alice", "save")
            self.assertEqual(r["version"], 3)
            self.assertEqual(r["payload"]["fields"]["total"]["value"], "10.00")
            with self.assertRaises(Conflict):
                s.review(r["id"], 2, {}, "receipt", "bob", "save")
            self.assertEqual(len(s.events(r["id"])), 1)
