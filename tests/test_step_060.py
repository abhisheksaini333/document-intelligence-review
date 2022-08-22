import unittest, tempfile, json, pathlib, hashlib, os

from docreview.serving import export_bento
from docreview.baseline import train,save
from docreview.fixtures import records
class BentoTests(unittest.TestCase):
 def test_native_store(self):
  with tempfile.TemporaryDirectory() as d:
   save(train(records()),d,{'dataset':'synthetic'});result=export_bento(d)
   self.assertIn('document_classifier:',result['tag']);self.assertTrue(result['parity'])
