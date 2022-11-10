import unittest, tempfile, json, pathlib, hashlib, os

from docreview.pipeline import Pipeline
from docreview.fixtures import records, render


class SourceIntegrityTests(unittest.TestCase):
    def test_modified_image(self):
        with tempfile.TemporaryDirectory() as d:
            p = Pipeline(pathlib.Path(d) / "data")
            image = render(records()[0], pathlib.Path(d) / "a.png")
            row = p.ingest(image.read_bytes(), "a")
            replacement = render(records()[1], pathlib.Path(d) / "b.png")
            pathlib.Path(row["image_path"]).write_bytes(replacement.read_bytes())
            with self.assertRaisesRegex(ValueError, "integrity"):
                p.process(row["id"])
