import unittest, tempfile, json, pathlib, hashlib, os

from docreview.calibration import temperature_scale, choose_temperature


class TemperatureTests(unittest.TestCase):
    def test_fit(self):
        self.assertAlmostEqual(temperature_scale({"a": 0.8, "b": 0.2}, 1)["a"], 0.8)
        rows = [{"a": 0.99, "b": 0.01}, {"a": 0.99, "b": 0.01}]
        chosen = choose_temperature(["a", "b"], rows)
        self.assertGreater(chosen["temperature"], 1)
