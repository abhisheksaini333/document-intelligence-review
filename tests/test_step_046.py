import unittest, tempfile, json, pathlib, hashlib, os

from docreview.store import Store
class SourceEvidenceTests(unittest.TestCase):
 def test_original_value_survives(self):
  with tempfile.TemporaryDirectory() as d:
   s=Store(pathlib.Path(d)/'s');r=s.create('a'*64,'a','x');s.result(r['id'],1,{'fields':{'total':{'value':'10.00','confidence':.5}}})
   row=s.review(r['id'],2,{'total':'20'},'invoice','alice','save');self.assertEqual(row['payload']['fields']['total']['source_value'],'10.00')
   row=s.review(r['id'],3,{'total':'30'},'invoice','alice','save');self.assertEqual(row['payload']['fields']['total']['source_value'],'10.00')
