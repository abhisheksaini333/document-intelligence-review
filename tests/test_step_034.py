import unittest, tempfile, json, pathlib, hashlib, os

from docreview.metrics import calibration


class CalibrationTests(unittest.TestCase):
    def test_confidence_bins(self):
        score = calibration(
            ["a", "b"], [{"a": 0.8, "b": 0.2}, {"a": 0.8, "b": 0.2}], bins=5
        )
        self.assertAlmostEqual(score["ece"], 0.3)
        self.assertAlmostEqual(score["brier"], 0.68)
        self.assertEqual(sum(b["count"] for b in score["bins"]), 2)
