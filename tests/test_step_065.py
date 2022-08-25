import unittest, tempfile, json, pathlib, hashlib, os

import subprocess,sys
class WorkerCliTests(unittest.TestCase):
 def test_empty_once(self):
  with tempfile.TemporaryDirectory() as d:
   p=subprocess.run([sys.executable,'-m','docreview','worker','--once','--data',d],capture_output=True,text=True);self.assertEqual(p.returncode,0,p.stderr);self.assertEqual(json.loads(p.stdout),None)
