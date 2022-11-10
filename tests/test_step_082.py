import unittest, tempfile, json, pathlib, hashlib, os

from docreview.review import route


class CompleteRouteTests(unittest.TestCase):
    def test_missing_fields(self):
        result = route({"prediction": {"confidence": 0.99}, "fields": {}, "issues": []})
        self.assertIn("missing_total", result["reasons"])
