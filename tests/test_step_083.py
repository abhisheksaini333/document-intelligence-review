import unittest, tempfile, json, pathlib, hashlib, os

from docreview.store import Store
from docreview.review import validate_corrections
class ReviewValidationTests(unittest.TestCase):
 def test_invalid_versions_and_blank(self):
  with self.assertRaises(ValueError):validate_corrections({'number':'   '},'invoice')
  with tempfile.TemporaryDirectory() as d:
   s=Store(pathlib.Path(d)/'s');r=s.create('a'*64,'x','x');s.result(r['id'],1,{'fields':{}})
   with self.assertRaises(ValueError):s.review(r['id'],2.0,{},'invoice','alice','save')
