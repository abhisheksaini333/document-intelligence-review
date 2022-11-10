import unittest, tempfile, json, pathlib, hashlib, os

from docreview.ingest import validate_image
from docreview.fixtures import render, records


class DecodeTests(unittest.TestCase):
    def test_decode(self):
        with tempfile.TemporaryDirectory() as d:
            p = render(records()[0], pathlib.Path(d) / "i.png")
            self.assertEqual(validate_image(p.read_bytes())["pages"], 1)
        with self.assertRaises(ValueError):
            validate_image(b"\x89PNG\r\n\x1a\n" + b"bad")
