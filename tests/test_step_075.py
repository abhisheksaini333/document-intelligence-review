import unittest, tempfile, json, pathlib, hashlib, os

from docreview.feedback import merge_training_feedback
class FeedbackLeakTests(unittest.TestCase):
 def test_guard(self):
  train=[{'id':'a','family':'one','text':'invoice','label':'invoice'}];held=[{'id':'b','family':'two','text':'held out'}]
  with self.assertRaises(ValueError):merge_training_feedback(train,[{'id':'c','family':'two','text':'changed','label':'receipt'}],held)
  with self.assertRaises(ValueError):merge_training_feedback(train,[{'id':'c','family':'three','text':'held out','label':'receipt'}],held)
  self.assertEqual(len(merge_training_feedback(train,[{'id':'c','family':'three','text':'new','label':'receipt'}],held)),2)
