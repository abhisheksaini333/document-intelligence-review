import unittest, tempfile, json, pathlib, hashlib, os

from docreview.backup import snapshot
from docreview.pipeline import Pipeline
from docreview.fixtures import records, render


class SnapshotTests(unittest.TestCase):
    def test_live_snapshot(self):
        with tempfile.TemporaryDirectory() as d:
            p = Pipeline(pathlib.Path(d) / "data")
            image = render(records()[0], pathlib.Path(d) / "i.png")
            p.ingest(image.read_bytes(), "i")
            target = snapshot(p.directory, pathlib.Path(d) / "snapshot")
            self.assertTrue((target / "manifest.json").exists())
            self.assertEqual(len(list((target / "images").iterdir())), 1)
            with self.assertRaises(ValueError):
                snapshot(p.directory, target)
