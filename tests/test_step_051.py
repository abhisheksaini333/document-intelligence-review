import unittest, tempfile, json, pathlib, hashlib, os

from docreview.store import Store,Conflict
class RecoveryTests(unittest.TestCase):
 def test_restart_fencing(self):
  with tempfile.TemporaryDirectory() as d:
   path=pathlib.Path(d)/'s';s=Store(path);r=s.create('a'*64,'x','x');old=s.claim('dead',now=1,lease_seconds=2);new=Store(path).claim('new',now=4)
   self.assertGreater(new['version'],old['version'])
   with self.assertRaises(Conflict):s.result(r['id'],old['version'],{})
   self.assertEqual(s.lease(r['id'])['attempts'],2)
