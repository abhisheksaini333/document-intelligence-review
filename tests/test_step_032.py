import unittest, tempfile, json, pathlib, hashlib, os

from docreview.store import Store
class ApprovalTests(unittest.TestCase):
 def test_block_bad_approval(self):
  with tempfile.TemporaryDirectory() as d:
   s=Store(pathlib.Path(d)/'s');r=s.create('a'*64,'a','x');s.result(r['id'],1,{'fields':{}})
   with self.assertRaises(ValueError): s.review(r['id'],2,{'total':'20'},'invoice','alice','approve')
   self.assertEqual(s.get(r['id'])['version'],2)
   r=s.review(r['id'],2,{'number':'I-1','date':'2022-07-01','total':'20'},'invoice','alice','approve');self.assertEqual(r['status'],'approved')
