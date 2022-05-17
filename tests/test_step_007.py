import unittest, tempfile, json, pathlib, hashlib, os

from docreview.ingest import save_image
class StorageTests(unittest.TestCase):
 def test_duplicate_and_private_permissions(self):
  with tempfile.TemporaryDirectory() as d:
   content=b'\x89PNG\r\n\x1a\n' + b'x'*40
   a=save_image(d,content); b=save_image(d,content)
   self.assertEqual(a,b); self.assertEqual(a.read_bytes(),content)
   self.assertEqual(a.stat().st_mode & 0o777,0o600)
   self.assertEqual(len(list(pathlib.Path(d).iterdir())),1)
