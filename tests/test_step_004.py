import unittest, tempfile, json, pathlib, hashlib, os

from docreview.normalize import document_date


class DateTests(unittest.TestCase):
    def test_dates(self):
        self.assertEqual(document_date("2022-06-19"), "2022-06-19")
        self.assertEqual(document_date("19 Jun 2022"), "2022-06-19")
        for bad in ["02/03/2022", "2022-02-30"]:
            with self.assertRaises(ValueError):
                document_date(bad)
