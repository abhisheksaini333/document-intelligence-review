import unittest, tempfile, json, pathlib, hashlib, os

from docreview.pipeline import Pipeline
from docreview.fixtures import render,records
class PipelineRouteTests(unittest.TestCase):
 def test_routing(self):
  with tempfile.TemporaryDirectory() as d:
   p=render(records()[0],pathlib.Path(d)/'i.png');service=Pipeline(pathlib.Path(d)/'data');r=service.ingest(p.read_bytes(),'i');done=service.process(r['id']);self.assertIn('unclassified',done['payload']['routing']['reasons'])
