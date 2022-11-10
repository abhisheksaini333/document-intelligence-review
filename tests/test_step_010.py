import unittest, tempfile, json, pathlib, hashlib, os

from docreview.domain import Field, Box


class FieldTests(unittest.TestCase):
    def test_evidence(self):
        f = Field("total", "30.00", 0.9, 1, Box(1, 2, 3, 4), "spatial")
        self.assertEqual(f.to_dict()["box"]["x"], 1)
        with self.assertRaises(ValueError):
            Field("unknown", "x", 0.9, 1, None, "rule")
        with self.assertRaises(ValueError):
            Field("total", "x", float("nan"), 1, None, "rule")
