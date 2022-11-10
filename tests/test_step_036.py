import unittest, tempfile, json, pathlib, hashlib, os

from docreview.review import route


class RouteTests(unittest.TestCase):
    def test_abstention(self):
        self.assertIn(
            "uncertain_class",
            route({"prediction": {"confidence": 0.6}, "fields": {}, "issues": []})[
                "reasons"
            ],
        )
        self.assertEqual(
            route(
                {
                    "prediction": {"confidence": 0.99},
                    "fields": {
                        "number": {"value": "I", "confidence": 0.99},
                        "date": {"value": "2022-07-01", "confidence": 0.99},
                        "total": {"value": "10", "confidence": 0.99},
                    },
                    "issues": [],
                }
            )["recommendation"],
            "eligible",
        )
