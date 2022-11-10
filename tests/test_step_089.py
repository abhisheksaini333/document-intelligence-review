import unittest, tempfile, json, pathlib, hashlib, os

from docreview.backup import snapshot, restore
from docreview.pipeline import Pipeline
from docreview.fixtures import render, records


class RestoreTests(unittest.TestCase):
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            d = pathlib.Path(d)
            p = Pipeline(d / "data")
            image = render(records()[0], d / "i.png")
            row = p.ingest(image.read_bytes(), "i")
            snapshot(p.directory, d / "backup")
            restore(d / "backup", d / "restored")
            new = Pipeline(d / "restored")
            self.assertEqual(
                new.process(row["id"])["payload"]["fields"]["total"]["value"], "110.00"
            )
            with self.assertRaises(ValueError):
                restore(d / "backup", d / "restored")
