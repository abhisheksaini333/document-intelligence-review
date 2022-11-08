import unittest,tempfile,pathlib,hashlib,json
from docreview.model_source import fetch_source
class FetchTests(unittest.TestCase):
 def test_verified_local_download(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);source=root/'source';source.write_bytes(b'model')
   manifest={'revision':'a'*40,'files':{'weight.bin':{'url':source.as_uri(),'sha256':hashlib.sha256(b'model').hexdigest()}}}
   fetch_source(manifest,root/'dest');self.assertEqual((root/'dest/weight.bin').read_bytes(),b'model')
   manifest['files']['weight.bin']['sha256']='0'*64
   with self.assertRaises(ValueError):fetch_source(manifest,root/'bad')
