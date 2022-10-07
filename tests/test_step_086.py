import unittest, tempfile, json, pathlib, hashlib, os

from docreview.api import strict_json
class StrictJSONTests(unittest.TestCase):
 def test_ambiguous_objects(self):
  self.assertEqual(strict_json(b'{"x":1}'),{'x':1})
  for content in [b'{"x":1,"x":2}',b'{"x":NaN}',b'{"x":Infinity}']:
   with self.assertRaises(ValueError):strict_json(content)
