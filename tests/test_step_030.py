import unittest, tempfile, json, pathlib, hashlib, os

from docreview.review import validate_corrections
class CorrectionTests(unittest.TestCase):
 def test_validation(self):
  self.assertEqual(validate_corrections({'total':'$20'},'invoice'),{'total':'20.00'})
  for fields,label in [({'evil':'x'},'invoice'),({'date':'02/03/2022'},'invoice'),({},'other')]:
   with self.assertRaises(ValueError): validate_corrections(fields,label)
