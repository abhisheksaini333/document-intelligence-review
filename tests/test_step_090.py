import unittest, tempfile, json, pathlib, hashlib, os

from docreview.store import Store


class SearchTests(unittest.TestCase):
    def test_literal_search(self):
        with tempfile.TemporaryDirectory() as d:
            s = Store(pathlib.Path(d) / "s")
            s.create("a" * 64, "invoice 10%.png", "x")
            s.create("b" * 64, "receipt.png", "x")
            self.assertEqual(len(s.search("10%")), 1)
            self.assertEqual(s.search("invoice")[0]["filename"], "invoice 10%.png")
            with self.assertRaises(ValueError):
                s.search("x" * 201)
