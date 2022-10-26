import unittest,tempfile,pathlib,json,threading
from urllib.request import urlopen
from docreview.api import create_server
class EvaluationAPITests(unittest.TestCase):
 def test_report_available(self):
  with tempfile.TemporaryDirectory() as d:
   pathlib.Path(d,'evaluation.json').write_text(json.dumps({'scope':'synthetic','models':{}}));s=create_server(d,port=0);t=threading.Thread(target=s.serve_forever,daemon=True);t.start()
   try:
    with urlopen(f'http://127.0.0.1:{s.server_port}/api/evaluation') as r:self.assertEqual(json.load(r)['scope'],'synthetic')
   finally:s.shutdown();s.server_close();t.join()
