import unittest, tempfile, json, pathlib, hashlib, os

import subprocess,sys
class ServeCliTests(unittest.TestCase):
 def test_options(self):
  p=subprocess.run([sys.executable,'-m','docreview','serve','--help'],capture_output=True,text=True);self.assertEqual(p.returncode,0);self.assertIn('--port',p.stdout)
