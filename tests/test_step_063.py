import unittest, tempfile, json, pathlib, hashlib, os

from docreview.tracking import restore_run
from docreview.baseline import train,save
from docreview.fixtures import records
class TrackingRestoreTests(unittest.TestCase):
 def test_mlflow_restore(self):
  from docreview.tracking import track_baseline
  with tempfile.TemporaryDirectory() as d:
   result=track_baseline(pathlib.Path(d)/'output',pathlib.Path(d)/'mlruns')
   loaded=restore_run(pathlib.Path(d)/'mlruns',result['run_id']);self.assertEqual(list(loaded.classes_),['invoice','purchase_order','receipt'])
