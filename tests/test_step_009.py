import unittest, tempfile, json, pathlib, hashlib, os

from docreview.store import Store
class QueueTests(unittest.TestCase):
 def test_queue(self):
  with tempfile.TemporaryDirectory() as d:
   s=Store(pathlib.Path(d)/'s');s.create('a'*64,'a.png','x');s.create('b'*64,'b.png','x')
   self.assertEqual(len(s.list(limit=1)),1);self.assertEqual(len(s.list(status='approved')),0)
   with self.assertRaises(ValueError): s.list(limit=1001)
   with self.assertRaises(ValueError): s.list(status='invalid')
