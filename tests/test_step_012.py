import unittest, tempfile, json, pathlib, hashlib, os

from docreview.fixtures import render,records
class RasterTests(unittest.TestCase):
 def test_render(self):
  from PIL import Image
  with tempfile.TemporaryDirectory() as d:
   p=render(records()[0],pathlib.Path(d)/'i.png')
   with Image.open(p) as img: self.assertEqual(img.size,(1500,1000))
