import unittest, tempfile, json, pathlib, hashlib, os

from docreview.feedback import select_examples
class SelectionTests(unittest.TestCase):
 def test_uncertainty_and_dedup(self):
  rows=[{'id':'a','digest':'1','probabilities':{'a':.5,'b':.5}},{'id':'b','digest':'1','probabilities':{'a':.5,'b':.5}},{'id':'c','digest':'2','probabilities':{'a':.99,'b':.01}}]
  self.assertEqual([r['id'] for r in select_examples(rows,10)],['a','c'])
