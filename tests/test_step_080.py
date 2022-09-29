import unittest, tempfile, json, pathlib, hashlib, os

import subprocess,sys
class BenchmarkCliTests(unittest.TestCase):
 def test_benchmark_help(self):
  p=subprocess.run([sys.executable,'-m','docreview','benchmark','--help'],capture_output=True,text=True);self.assertEqual(p.returncode,0);self.assertIn('--source',p.stdout);self.assertIn('--epochs',p.stdout)
