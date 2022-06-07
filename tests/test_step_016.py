import unittest, tempfile, json, pathlib, hashlib, os

from docreview.extraction import lines
from docreview.domain import Box,Token
class LineTests(unittest.TestCase):
 def test_order(self):
  w=[Token('20',90,Box(100,20,20,10),1),Token('Total:',95,Box(10,20,40,10),1),Token('Page2',90,Box(0,0,10,10),2)]
  self.assertEqual([x['text'] for x in lines(w)],['Total: 20','Page2']);self.assertEqual(lines(w)[0]['box'].width,110)
