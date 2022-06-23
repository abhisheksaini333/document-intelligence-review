import unittest, tempfile, json, pathlib, hashlib, os

from docreview.store import Store,Conflict
class ResultTests(unittest.TestCase):
 def test_version(self):
  with tempfile.TemporaryDirectory() as d:
   s=Store(pathlib.Path(d)/'s');r=s.create('a'*64,'a','x');got=s.result(r['id'],1,{'text':'invoice','fields':{}})
   self.assertEqual(got['version'],2)
   with self.assertRaises(Conflict): s.result(r['id'],1,{})
