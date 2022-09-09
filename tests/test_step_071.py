import unittest, tempfile, json, pathlib, hashlib, os

from docreview.calibration import temperature_scale,choose_temperature
class TemperatureTests(unittest.TestCase):
 def test_fit(self):
  self.assertAlmostEqual(temperature_scale({'a':.8,'b':.2},1)['a'],.8)
  rows=[{'a':.99,'b':.01},{'a':.99,'b':.01}];chosen=choose_temperature(['a','b'],rows);self.assertGreater(chosen['temperature'],1)
