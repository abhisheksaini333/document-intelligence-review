import unittest, tempfile, json, pathlib, hashlib, os

from docreview.store import Store,Conflict
class ResultStateTests(unittest.TestCase):
 def test_state_guard(self):
  with tempfile.TemporaryDirectory() as d:
   s=Store(pathlib.Path(d)/'s');r=s.create('a'*64,'x','x');s.result(r['id'],1,{'text':'keep'})
   with self.assertRaises(Conflict):s.result(r['id'],2,{'text':'overwrite'})
   self.assertEqual(s.get(r['id'])['payload']['text'],'keep')
