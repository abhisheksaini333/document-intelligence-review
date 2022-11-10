import unittest, tempfile, json, pathlib, hashlib, os

from docreview.ingest import identity, image_type


class ImageTests(unittest.TestCase):
    def test_signatures(self):
        self.assertEqual(identity(b"abc"), hashlib.sha256(b"abc").hexdigest())
        self.assertEqual(image_type(b"\x89PNG\r\n\x1a\n" + b"x" * 20), "png")
        with self.assertRaises(ValueError):
            image_type(b"<svg>oops</svg>")
        with self.assertRaises(ValueError):
            identity(b"")
