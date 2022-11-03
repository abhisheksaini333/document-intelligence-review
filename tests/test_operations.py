import unittest,subprocess,sys,tempfile,json,pathlib
class OperationsTests(unittest.TestCase):
 def test_feedback_command(self):
  with tempfile.TemporaryDirectory() as d:
   result=subprocess.run([sys.executable,'-m','docreview','feedback','--data',d],capture_output=True,text=True)
   self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(json.loads(result.stdout),[])
