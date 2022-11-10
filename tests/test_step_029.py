import unittest, tempfile, json, pathlib, hashlib, os

from docreview.store import Store


class SummaryTests(unittest.TestCase):
    def test_counts(self):
        with tempfile.TemporaryDirectory() as d:
            s = Store(pathlib.Path(d) / "s")
            s.create("a" * 64, "a", "x")
            self.assertEqual(
                s.summary(),
                {
                    "queued": 1,
                    "processing": 0,
                    "review": 0,
                    "approved": 0,
                    "rejected": 0,
                    "failed": 0,
                },
            )
