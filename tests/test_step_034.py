import unittest, tempfile, json, pathlib, hashlib, os

from docreview.metrics import calibration
class CalibrationTests(unittest.TestCase):
 def test_confidence_bins(self):
  score=calibration(['a','b'],[{'a':.8,'b':.2},{'a':.8,'b':.2}],bins=5)
  self.assertAlmostEqual(score['ece'],.3);self.assertAlmostEqual(score['brier'],.68);self.assertEqual(sum(b['count'] for b in score['bins']),2)
