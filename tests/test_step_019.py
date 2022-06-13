import unittest, tempfile, json, pathlib, hashlib, os

from docreview.dataset import split
from docreview.fixtures import records
class SplitTests(unittest.TestCase):
 def test_holdout(self):
  p=split(records());self.assertEqual([len(p[k]) for k in ('train','calibration','test')],[108,36,36])
  groups=[{r['family'] for r in p[k]} for k in p];self.assertFalse(groups[0]&groups[1] or groups[0]&groups[2] or groups[1]&groups[2])
