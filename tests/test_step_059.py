import unittest, tempfile, json, pathlib, hashlib, os

from docreview.registry import Registry
from docreview.baseline import train
from docreview.fixtures import records
class RollbackTests(unittest.TestCase):
 def test_rollback(self):
  with tempfile.TemporaryDirectory() as d:
   r=Registry(d);m=train(records());r.install('v1',m,{});r.install('v2',m,{});r.activate('v1',0);r.activate('v2',1);self.assertEqual(r.rollback(2)['version'],'v1')
   self.assertEqual(r.classify(['Invoice payment due'])['version'],'v1')
