import unittest, tempfile, json, pathlib, hashlib, os

from docreview.calibration import choose_threshold
class ThresholdTests(unittest.TestCase):
 def test_risk_constraint(self):
  result=choose_threshold(['a','b'],[{'label':'a','confidence':.9},{'label':'a','confidence':.6}],max_risk=0)
  self.assertEqual(result['coverage'],.5);self.assertGreater(result['threshold'],.6)
