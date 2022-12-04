import unittest, tempfile, pathlib
from docreview.feedback import retrain_feedback


class FeedbackTrainingTests(unittest.TestCase):
    def test_reviewed_labels_retrain_on_fixed_holdout(self):
        row = {
            "id": "reviewed-1",
            "family": "new-vendor",
            "text": "Invoice payment due for consulting services",
            "label": "invoice",
        }
        with tempfile.TemporaryDirectory() as d:
            report = retrain_feedback([row], d)
            self.assertEqual(report["training_count"], 109)
            self.assertEqual(report["test"]["count"], 36)
            self.assertTrue(pathlib.Path(d, "model", "manifest.json").exists())

    def test_unassigned_family_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                retrain_feedback(
                    [
                        {
                            "id": "x",
                            "family": None,
                            "text": "invoice",
                            "label": "invoice",
                        }
                    ],
                    d,
                )


class FamilyReviewTests(unittest.TestCase):
    def test_reviewed_family_exports_and_blocks_holdout_retraining(self):
        from docreview.store import Store
        from docreview.feedback import export_corrections

        with tempfile.TemporaryDirectory() as d:
            s = Store(pathlib.Path(d) / "db")
            row = s.create("a" * 64, "x", "x")
            s.result(
                row["id"], 1, {"fields": {}, "text": "Novel vendor invoice payment due"}
            )
            s.review(
                row["id"],
                2,
                {"number": "I", "date": "2022-12-01", "total": "10"},
                "invoice",
                "alice",
                "approve",
                family="invoice-layout-4",
            )
            exported = export_corrections(s)
            self.assertEqual(exported[0]["family"], "invoice-layout-4")
            with self.assertRaises(ValueError):
                retrain_feedback(exported, pathlib.Path(d) / "model")
