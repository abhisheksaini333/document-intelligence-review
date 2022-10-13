import unittest, tempfile, json, pathlib, hashlib, os

from docreview.store import Store
class CrashBudgetTests(unittest.TestCase):
 def test_expired_crashes(self):
  with tempfile.TemporaryDirectory() as d:
   s=Store(pathlib.Path(d)/'s');r=s.create('a'*64,'x','x')
   for instant in [1,3,5]:self.assertIsNotNone(s.claim('crashing',now=instant,lease_seconds=1))
   self.assertIsNone(s.claim('new',now=7));self.assertEqual(s.get(r['id'])['status'],'failed')
