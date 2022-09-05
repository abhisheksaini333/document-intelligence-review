import unittest, tempfile, json, pathlib, hashlib, os

from docreview.transformer import TrainingConfig
class ConfigTests(unittest.TestCase):
 def test_bounds(self):
  self.assertEqual(TrainingConfig().threads,2)
  for kw in [{'epochs':0},{'batch_size':129},{'max_length':513},{'learning_rate':float('nan')},{'threads':9}]:
   with self.assertRaises(ValueError):TrainingConfig(**kw)
