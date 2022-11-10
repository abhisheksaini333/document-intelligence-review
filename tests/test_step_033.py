import unittest, tempfile, json, pathlib, hashlib, os

from docreview.feedback import export_corrections
from docreview.store import Store


class ExportTests(unittest.TestCase):
    def test_approved_only(self):
        with tempfile.TemporaryDirectory() as d:
            s = Store(pathlib.Path(d) / "s")
            r = s.create("a" * 64, "a", "x")
            s.result(r["id"], 1, {"text": "invoice", "fields": {}})
            self.assertEqual(export_corrections(s), [])
            s.review(
                r["id"],
                2,
                {"number": "I", "date": "2022-07-01", "total": "10"},
                "invoice",
                "alice",
                "approve",
            )
            rows = export_corrections(s)
            self.assertEqual(rows[0]["label"], "invoice")
            self.assertEqual(rows[0]["version"], 3)
