import unittest, tempfile, json, pathlib, hashlib, os

from docreview.ocr_evaluation import evaluate_ocr
from docreview.fixtures import records
class OCRFieldEvaluationTests(unittest.TestCase):
 def test_scoped_real_ocr(self):
  with tempfile.TemporaryDirectory() as d:
   report=evaluate_ocr([records()[0]],d);self.assertGreater(report['fields']['accuracy'],.8);self.assertEqual(report['count'],1);self.assertTrue(report['pages'][0]['sha256'])
