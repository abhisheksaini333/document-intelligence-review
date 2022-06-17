import unittest, tempfile, json, pathlib, hashlib, os

from docreview.baseline import train,predict
from docreview.dataset import split
from docreview.fixtures import records
class BaselineTests(unittest.TestCase):
 def test_training(self):
  parts=split(records());model=train(parts['train']);results=predict(model,[r['text'] for r in parts['test']])
  self.assertGreater(sum(p['label']==r['label'] for p,r in zip(results,parts['test'])),30)
  self.assertTrue(all(abs(sum(p['probabilities'].values())-1)<1e-6 for p in results))
