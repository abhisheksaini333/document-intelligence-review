import unittest, tempfile, json, pathlib, hashlib, os

from docreview.pipeline import Pipeline
from docreview.registry import Registry
from docreview.baseline import train
from docreview.fixtures import records,render
class RegistryPipelineTests(unittest.TestCase):
 def test_classified_ocr(self):
  with tempfile.TemporaryDirectory() as d:
   r=Registry(pathlib.Path(d)/'registry');r.install('one',train(records()),{});r.activate('one',0);p=Pipeline(d);image=render(records()[0],pathlib.Path(d)/'x.png');row=p.ingest(image.read_bytes(),'x');done=p.process(row['id']);self.assertEqual(done['payload']['prediction']['label'],'invoice');self.assertEqual(done['payload']['model_version'],'one')
