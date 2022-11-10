import unittest, tempfile, json, pathlib, hashlib, os

from docreview.comparison import finalize_comparison


class FinalComparisonTests(unittest.TestCase):
    def test_report_decision(self):
        same = {"classification": {"macro_f1": 1}, "calibration": {"ece": 0.01}}
        report = {
            "models": {
                "baseline": {"calibrated": same},
                "transformer": {"calibrated": same},
            }
        }
        self.assertFalse(finalize_comparison(report)["promotion"]["promote"])
