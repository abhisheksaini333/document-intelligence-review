import unittest, tempfile, json, pathlib, hashlib, os

from docreview.serving import classify_request
from docreview.registry import Registry
from docreview.baseline import train
from docreview.fixtures import records


class ServingInputTests(unittest.TestCase):
    def test_service_contract(self):
        with tempfile.TemporaryDirectory() as d:
            r = Registry(d)
            r.install("one", train(records()), {})
            r.activate("one", 0)
            self.assertEqual(
                classify_request(r, {"texts": ["invoice payment due"]})["version"],
                "one",
            )
            for bad in [
                {},
                {"texts": "invoice"},
                {"texts": []},
                {"texts": ["x"] * 129},
            ]:
                with self.assertRaises(ValueError):
                    classify_request(r, bad)
