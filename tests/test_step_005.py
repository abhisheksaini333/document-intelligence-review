import unittest, tempfile, json, pathlib, hashlib, os

from docreview.fixtures import records


class FixtureTests(unittest.TestCase):
    def test_families(self):
        rows = records()
        self.assertEqual(len(rows), 180)
        self.assertEqual(len({r["id"] for r in rows}), 180)
        self.assertEqual(
            {r["label"] for r in rows}, {"invoice", "purchase_order", "receipt"}
        )
        self.assertEqual(len({r["family"] for r in rows}), 15)
        self.assertTrue(all(r["fields"]["total"] for r in rows))
