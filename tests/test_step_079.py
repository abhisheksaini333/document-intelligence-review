import unittest, tempfile, json, pathlib, hashlib, os

from docreview.tracking import track_comparison


class ComparisonTrackingTests(unittest.TestCase):
    def test_log_comparison(self):
        with tempfile.TemporaryDirectory() as d:
            report = {
                "dataset_sha256": "abc",
                "models": {
                    "baseline": {"raw": {"classification": {"macro_f1": 0.9}}},
                    "transformer": {"raw": {"classification": {"macro_f1": 0.8}}},
                },
            }
            result = track_comparison(report, pathlib.Path(d) / "mlruns")
            self.assertEqual(result["metrics"]["transformer_macro_f1"], 0.8)
