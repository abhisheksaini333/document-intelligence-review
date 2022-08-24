import unittest, tempfile, json, pathlib, hashlib, os

import subprocess,sys
class ModelCliTests(unittest.TestCase):
 def test_model_cli(self):
  with tempfile.TemporaryDirectory() as d:
   p=subprocess.run([sys.executable,'-m','docreview','train','--output',d],capture_output=True,text=True);self.assertEqual(p.returncode,0,p.stderr);self.assertTrue(pathlib.Path(d,'baseline','manifest.json').exists())
