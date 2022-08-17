import unittest, tempfile, json, pathlib, hashlib, os

from docreview.registry import Registry
from docreview.baseline import train
from docreview.fixtures import records
class ActivationTests(unittest.TestCase):
 def test_compare_and_swap(self):
  with tempfile.TemporaryDirectory() as d:
   r=Registry(d);r.install('v1',train(records()),{});self.assertEqual(r.activate('v1',0)['revision'],1)
   with self.assertRaises(ValueError):r.activate('v1',0)
   self.assertEqual(r.active()['version'],'v1')
