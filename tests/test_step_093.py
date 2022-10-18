import unittest, tempfile, json, pathlib, hashlib, os

from docreview.api import create_server
from urllib.request import Request,urlopen
from urllib.error import HTTPError
import threading
class DependencyErrorTests(unittest.TestCase):
 def test_unavailable_image(self):
  with tempfile.TemporaryDirectory() as d:
   s=create_server(d,port=0);row=s.pipeline.store.create('a'*64,'x','/private/missing/image');t=threading.Thread(target=s.serve_forever,daemon=True);t.start()
   try:
    with self.assertRaises(HTTPError) as caught:urlopen(Request(f'http://127.0.0.1:{s.server_port}/api/documents/{row["id"]}/process',data=b'{}',headers={'Content-Type':'application/json'}))
    self.assertEqual(caught.exception.code,503);self.assertNotIn('/private',caught.exception.read().decode())
   finally:s.shutdown();s.server_close();t.join()
