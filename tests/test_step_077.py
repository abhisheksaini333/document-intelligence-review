import unittest, tempfile, json, pathlib, hashlib, os

from docreview.performance import measure
class PerformanceTests(unittest.TestCase):
 def test_timing(self):
  result=measure(lambda:['invoice'],repeats=3);self.assertEqual(result['samples'],3);self.assertGreaterEqual(result['p95_ms'],result['median_ms'])
  with self.assertRaises(ValueError):measure(lambda:None,repeats=0)
