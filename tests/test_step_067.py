import unittest, tempfile, json, pathlib, hashlib, os

from docreview.transformer import verify_source


class SourceTests(unittest.TestCase):
    def test_hashes(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d)
            (p / "config.json").write_text("{}")
            m = {
                "revision": "a" * 40,
                "files": {"config.json": {"sha256": hashlib.sha256(b"{}").hexdigest()}},
            }
            (p / "source-manifest.json").write_text(json.dumps(m))
            self.assertEqual(verify_source(p)["revision"], "a" * 40)
            (p / "config.json").write_text("bad")
            with self.assertRaises(ValueError):
                verify_source(p)
