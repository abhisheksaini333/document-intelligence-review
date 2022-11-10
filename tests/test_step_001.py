import unittest, tempfile, json, pathlib, hashlib, os

from docreview.domain import Box, Token


class GeometryTests(unittest.TestCase):
    def test_bounds_and_tokens(self):
        self.assertEqual(Box(10, 20, 30, 40).area, 1200)
        self.assertEqual(Token("total", 95, Box(1, 2, 3, 4), 2).page, 2)
        for args in [(-1, 0, 2, 3), (0, 0, 0, 1)]:
            with self.assertRaises(ValueError):
                Box(*args)
        with self.assertRaises(ValueError):
            Token("x", 101, Box(0, 0, 1, 1), 1)
