import unittest, tempfile, json, pathlib, hashlib, os

from docreview.feedback import select_examples


class SelectionTests(unittest.TestCase):
    def test_uncertainty_and_dedup(self):
        rows = [
            {"id": "a", "digest": "1", "probabilities": {"a": 0.5, "b": 0.5}},
            {"id": "b", "digest": "1", "probabilities": {"a": 0.5, "b": 0.5}},
            {"id": "c", "digest": "2", "probabilities": {"a": 0.99, "b": 0.01}},
        ]
        self.assertEqual([r["id"] for r in select_examples(rows, 10)], ["a", "c"])
