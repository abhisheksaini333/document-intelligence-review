import unittest, tempfile, json, pathlib, hashlib, os

from docreview.comparison import promotion_decision


class PromotionTests(unittest.TestCase):
    def test_no_automatic_win(self):
        b = {"classification": {"macro_f1": 0.9}, "calibration": {"ece": 0.1}}
        same = {"classification": {"macro_f1": 0.9}, "calibration": {"ece": 0.1}}
        self.assertFalse(promotion_decision(b, same)["promote"])
        same["classification"]["macro_f1"] = 0.95
        self.assertTrue(promotion_decision(b, same)["promote"])
