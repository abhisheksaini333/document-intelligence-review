import unittest, tempfile, pathlib, json
from docreview.backup import restore, snapshot
from docreview.pipeline import Pipeline


class BackupIntegrityTests(unittest.TestCase):
    def test_unlisted_file_is_rejected_without_creating_target(self):
        with tempfile.TemporaryDirectory() as d:
            d = pathlib.Path(d)
            p = Pipeline(d / "data")
            (p.directory / "images").mkdir()
            snapshot(p.directory, d / "backup")
            (d / "backup/unlisted").write_text("unexpected")
            with self.assertRaises(ValueError):
                restore(d / "backup", d / "restored")
            self.assertFalse((d / "restored").exists())

    def test_empty_data_snapshot(self):
        with tempfile.TemporaryDirectory() as d:
            d = pathlib.Path(d)
            p = Pipeline(d / "data")
            snapshot(p.directory, d / "backup")
            restore(d / "backup", d / "restored")
            self.assertEqual(Pipeline(d / "restored").store.list(), [])
