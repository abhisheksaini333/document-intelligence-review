import unittest, tempfile, json, pathlib, hashlib, os

from docreview.comparison import evaluate_predictions
class ComparisonTests(unittest.TestCase):
 def test_shared_metrics(self):
  rows=[{'label':'a'},{'label':'b'}];preds=[{'label':'a','confidence':.9,'probabilities':{'a':.9,'b':.1}},{'label':'b','confidence':.9,'probabilities':{'a':.1,'b':.9}}]
  result=evaluate_predictions(rows,preds);self.assertEqual(result['classification']['macro_f1'],1);self.assertEqual(result['coverage'][0]['coverage'],1)
