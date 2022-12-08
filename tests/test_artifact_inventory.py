import unittest, tempfile, pathlib
from docreview.artifacts import seal, verify


class ArtifactInventoryTests(unittest.TestCase):
    def test_unlisted_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d)
            (p / "weight.bin").write_bytes(b"good")
            seal(p)
            (p / "config.json").write_text("{}")
            with self.assertRaises(ValueError):
                verify(p)
