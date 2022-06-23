import unittest, tempfile, json, pathlib, hashlib, os

from docreview.pipeline import Pipeline
from docreview.fixtures import render,records
class PipelineTests(unittest.TestCase):
 def test_image_to_review(self):
  with tempfile.TemporaryDirectory() as d:
   p=render(records()[0],pathlib.Path(d)/'i.png');service=Pipeline(pathlib.Path(d)/'data');r=service.ingest(p.read_bytes(),'invoice.png');done=service.process(r['id'])
   self.assertEqual(done['payload']['fields']['total']['value'],'110.00');self.assertEqual(done['payload']['pages'],[1])
