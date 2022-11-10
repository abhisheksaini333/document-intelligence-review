import unittest, tempfile, json, pathlib, hashlib, os

from docreview.transformer import TransformerClassifier


class TransformerInputTests(unittest.TestCase):
    def test_request_bounds_before_loading_weights(self):
        classifier = object.__new__(TransformerClassifier)
        for texts in [[], ["x"] * 129, [""], [42]]:
            with self.assertRaises(ValueError):
                classifier.predict(texts)
