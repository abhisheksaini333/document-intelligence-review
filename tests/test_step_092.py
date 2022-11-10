import unittest, tempfile, json, pathlib, hashlib, os

from docreview.transformer import TransformerClassifier


class TransformerIntegrityTests(unittest.TestCase):
    def test_reject_missing_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                TransformerClassifier(d)
