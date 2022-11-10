import unittest, tempfile, json, pathlib, hashlib, os

from docreview.transformer import train_transformer, TrainingConfig


class TrainingValidationTests(unittest.TestCase):
    def test_reject_single_class_before_loading_model(self):
        with self.assertRaisesRegex(ValueError, "two classes"):
            train_transformer(
                [{"label": "invoice", "text": "x"}],
                "missing",
                "unused",
                TrainingConfig(),
            )
