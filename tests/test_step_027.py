import unittest, tempfile, json, pathlib, hashlib, os

from docreview.metrics import field_accuracy
class FieldScoreTests(unittest.TestCase):
 def test_missing(self):
  score=field_accuracy([{'total':'10','date':'2022-05-01'}],[{'total':{'value':'10'}}])
  self.assertEqual(score['accuracy'],.5);self.assertEqual(score['fields']['date']['correct'],0)
