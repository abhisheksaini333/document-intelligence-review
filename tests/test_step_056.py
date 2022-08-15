import unittest, tempfile, json, pathlib, hashlib, os

from docreview.tracking import track_baseline
class TrackingTests(unittest.TestCase):
 def test_real_mlflow(self):
  with tempfile.TemporaryDirectory() as d:
   result=track_baseline(pathlib.Path(d)/'output',pathlib.Path(d)/'mlruns')
   self.assertTrue(result['run_id']);self.assertGreater(result['metrics']['macro_f1'],.9);self.assertTrue(result['artifacts'])
