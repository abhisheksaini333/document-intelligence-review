import unittest, tempfile, json, pathlib, hashlib, os

from docreview.store import Store
class IntakeTests(unittest.TestCase):
 def test_restart_and_duplicates(self):
  with tempfile.TemporaryDirectory() as d:
   path=pathlib.Path(d)/'db.sqlite'; s=Store(path)
   row=s.create('a'*64,'first.png','/image/path')
   again=s.create('a'*64,'second.png','/other')
   self.assertEqual(row['id'],again['id']); self.assertEqual(again['filename'],'first.png')
   self.assertEqual(Store(path).get(row['id'])['status'],'queued')
