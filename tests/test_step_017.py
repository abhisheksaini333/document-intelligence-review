import unittest, tempfile, json, pathlib, hashlib, os

from docreview.extraction import extract
from docreview.domain import Token, Box


class ExtractTests(unittest.TestCase):
    def test_fields(self):
        tokens = [
            Token("Total:", 99, Box(0, 0, 50, 20), 1),
            Token("$110.00", 98, Box(60, 0, 100, 20), 1),
        ]
        fields = extract(tokens)
        self.assertEqual(fields["total"]["value"], "110.00")
        self.assertEqual(fields["total"]["box"]["width"], 160)
