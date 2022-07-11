import unittest, tempfile, json, pathlib, hashlib, os

from docreview.review import route
class RouteTests(unittest.TestCase):
 def test_abstention(self):
  self.assertIn('uncertain_class',route({'prediction':{'confidence':.6},'fields':{},'issues':[]})['reasons'])
  self.assertEqual(route({'prediction':{'confidence':.99},'fields':{'total':{'confidence':.99}},'issues':[]})['recommendation'],'eligible')
