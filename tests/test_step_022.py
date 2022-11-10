import unittest, tempfile, json, pathlib, hashlib, os

from docreview.metrics import classification


class MetricsTests(unittest.TestCase):
    def test_scores(self):
        s = classification(["a", "a", "b", "b"], ["a", "b", "b", "b"])
        self.assertAlmostEqual(s["accuracy"], 0.75)
        self.assertAlmostEqual(s["macro_f1"], 0.7333333333333)
        self.assertEqual(s["confusion"], [[1, 1], [0, 2]])
