import unittest, tempfile, json, pathlib, hashlib, os

from docreview.artifacts import seal, verify


class SealedArtifactTests(unittest.TestCase):
    def test_modified_weight(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d)
            (p / "weights.bin").write_bytes(b"weights")
            seal(p)
            verify(p)
            (p / "weights.bin").write_bytes(b"changed")
            with self.assertRaises(ValueError):
                verify(p)
