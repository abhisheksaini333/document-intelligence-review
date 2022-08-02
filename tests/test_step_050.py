import unittest, tempfile, json, pathlib, hashlib, os

from docreview.store import Store
class LeaseTests(unittest.TestCase):
 def test_single_claim(self):
  with tempfile.TemporaryDirectory() as d:
   s=Store(pathlib.Path(d)/'s');r=s.create('a'*64,'x','x');claimed=s.claim('worker-a',now=100)
   self.assertEqual(claimed['status'],'processing');self.assertIsNone(s.claim('worker-b',now=101));self.assertEqual(claimed['version'],2)
