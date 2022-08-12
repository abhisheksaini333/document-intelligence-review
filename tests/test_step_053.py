import unittest, tempfile, json, pathlib, hashlib, os

from docreview.worker import once
from docreview.pipeline import Pipeline
from docreview.fixtures import render,records
class WorkerTests(unittest.TestCase):
 def test_worker(self):
  with tempfile.TemporaryDirectory() as d:
   p=Pipeline(pathlib.Path(d)/'data');image=render(records()[0],pathlib.Path(d)/'x.png');row=p.ingest(image.read_bytes(),'x')
   self.assertEqual(once(p,'worker')['status'],'review');self.assertIsNone(once(p,'worker'));self.assertEqual(p.store.get(row['id'])['payload']['fields']['total']['value'],'110.00')
