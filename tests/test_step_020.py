import unittest, tempfile, json, pathlib, hashlib, os

from docreview.dataset import audit_split, fingerprint, split
from docreview.fixtures import records


class LeakageTests(unittest.TestCase):
    def test_leaks(self):
        parts = split(records())
        audit_split(parts)
        self.assertEqual(fingerprint(records()), fingerprint(list(reversed(records()))))
        parts["test"][0] = dict(parts["train"][0])
        with self.assertRaises(ValueError):
            audit_split(parts)
