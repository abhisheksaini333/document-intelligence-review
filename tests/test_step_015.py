import unittest, tempfile, json, pathlib, hashlib, os

from docreview.ocr import recognize
from docreview.fixtures import render,records
class OCRTests(unittest.TestCase):
 def test_real_ocr(self):
  with tempfile.TemporaryDirectory() as d:
   p=render(records()[0],pathlib.Path(d)/'i.png');words=recognize(p)
   self.assertIn('INVOICE',[w.text for w in words]);self.assertTrue(all(w.box.area>0 for w in words))
   with self.assertRaises(ValueError): recognize(p,timeout=0)
