import unittest, tempfile, json, pathlib, hashlib, os

from docreview.metrics import coverage_curve
class CoverageTests(unittest.TestCase):
 def test_curve(self):
  rows=coverage_curve(['a','b'],[{'label':'a','confidence':.9},{'label':'a','confidence':.6}],[0,.8,1])
  self.assertEqual(rows[0]['risk'],.5);self.assertEqual(rows[1]['coverage'],.5);self.assertEqual(rows[1]['risk'],0);self.assertIsNone(rows[2]['risk'])
