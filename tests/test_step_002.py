import unittest, tempfile, json, pathlib, hashlib, os

from docreview.normalize import normalize_text
class TextTests(unittest.TestCase):
 def test_unicode_and_lines(self):
  self.assertEqual(normalize_text('ＡＣＭＥ   Co'+chr(13)+chr(10)+' Total:'+chr(9)+'10.00'+chr(0)), 'ACME Co'+chr(10)+'Total: 10.00')
