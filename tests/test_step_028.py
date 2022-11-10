import unittest, tempfile, json, pathlib, hashlib, os

from docreview.benchmark import baseline_benchmark


class BenchmarkTests(unittest.TestCase):
    def test_report(self):
        with tempfile.TemporaryDirectory() as d:
            r = baseline_benchmark(d)
            self.assertEqual(
                r["split_sizes"], {"train": 108, "calibration": 36, "test": 36}
            )
            self.assertGreater(r["test"]["macro_f1"], 0.9)
            self.assertTrue(r["reload_equal"])
            self.assertEqual(len(r["dataset_sha256"]), 64)
