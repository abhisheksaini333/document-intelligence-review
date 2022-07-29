import unittest, tempfile, json, pathlib, hashlib, os

from docreview.api import static_asset
class StaticTests(unittest.TestCase):
 def test_paths(self):
  with tempfile.TemporaryDirectory() as d:
   pathlib.Path(d,'index.html').write_text('hello');self.assertEqual(static_asset(d,'/')[0],b'hello')
   with self.assertRaises(ValueError):static_asset(d,'/../private')
   with self.assertRaises(ValueError):static_asset(d,'/%2e%2e/private')
