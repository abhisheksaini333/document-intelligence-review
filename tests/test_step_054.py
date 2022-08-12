import unittest, tempfile, json, pathlib, hashlib, os

from docreview.pipeline import Pipeline
from docreview.store import Conflict
class WorkerFenceTests(unittest.TestCase):
 def test_old_lease(self):
  with tempfile.TemporaryDirectory() as d:
   p=Pipeline(d);r=p.store.create('a'*64,'x','missing');p.store.claim('a',now=1,lease_seconds=1);p.store.claim('b',now=3)
   with self.assertRaises(Conflict):p.process(r['id'],expected_version=2)
