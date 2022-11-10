import unittest, tempfile, json, pathlib, hashlib, os

from docreview.extraction import field_issues


class IssueTests(unittest.TestCase):
    def test_arithmetic(self):
        fields = {
            k: {"value": v}
            for k, v in {
                "number": "X",
                "date": "2022-05-01",
                "subtotal": "100.00",
                "tax": "10.00",
                "total": "111.00",
            }.items()
        }
        self.assertIn("total_mismatch", field_issues(fields))
        fields["total"]["value"] = "110.00"
        self.assertEqual(field_issues(fields), [])
