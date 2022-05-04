import unittest, tempfile, json, pathlib, hashlib, os

from docreview.normalize import amount
class AmountTests(unittest.TestCase):
 def test_money(self):
  self.assertEqual(amount('$1,234.50'),'1234.50')
  self.assertEqual(amount('(25.5)'),'-25.50')
  for bad in ['NaN','1,23.45','10.009','free']:
   with self.assertRaises(ValueError): amount(bad)
