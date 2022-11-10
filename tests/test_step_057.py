import unittest, tempfile, json, pathlib, hashlib, os

from docreview.registry import Registry
from docreview.baseline import train
from docreview.fixtures import records


class RegistryTests(unittest.TestCase):
    def test_immutable_install(self):
        with tempfile.TemporaryDirectory() as d:
            r = Registry(d)
            r.install("v1", train(records()), {"source": "test"})
            with self.assertRaises(ValueError):
                r.install("v1", train(records()), {})
            with self.assertRaises(ValueError):
                r.install("../outside", None, {})
            self.assertEqual(r.versions(), ["v1"])
