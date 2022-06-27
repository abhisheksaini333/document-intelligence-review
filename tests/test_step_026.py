import unittest, tempfile, json, pathlib, hashlib, os

import subprocess,sys
class DemoTests(unittest.TestCase):
 def test_cli(self):
  with tempfile.TemporaryDirectory() as d:
   p=subprocess.run([sys.executable,'-m','docreview','demo','--data',d],capture_output=True,text=True)
   self.assertEqual(p.returncode,0,p.stderr);self.assertEqual(json.loads(p.stdout)['payload']['fields']['number']['value'],'IN-1101')
