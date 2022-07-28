import unittest, tempfile, json, pathlib, hashlib, os

from docreview.pipeline import Pipeline
from docreview.store import Conflict
class ReprocessTests(unittest.TestCase):
 def test_no_overwrite(self):
  with tempfile.TemporaryDirectory() as d:
   p=Pipeline(d);r=p.store.create('a'*64,'x','missing');p.store.result(r['id'],1,{'text':'reviewed','fields':{}})
   with self.assertRaises(Conflict):p.process(r['id'])
   self.assertEqual(p.store.get(r['id'])['payload']['text'],'reviewed')
