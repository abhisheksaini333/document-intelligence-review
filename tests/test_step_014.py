import unittest, tempfile, json, pathlib, hashlib, os

from docreview.ocr import parse_tsv


class TSVTests(unittest.TestCase):
    def test_words(self):
        text = "level\tpage_num\tleft\ttop\twidth\theight\tconf\ttext\n5\t1\t10\t20\t30\t40\t95.5\tTotal\n"
        words = parse_tsv(text)
        self.assertEqual(words[0].confidence, 95.5)
        self.assertEqual(words[0].box.x, 10)
        with self.assertRaises(ValueError):
            parse_tsv("not tsv")
