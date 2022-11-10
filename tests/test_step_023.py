import unittest, tempfile, json, pathlib, hashlib, os

from docreview.baseline import train, predict, save, load
from docreview.fixtures import records


class ArtifactTests(unittest.TestCase):
    def test_parity(self):
        model = train(records()[:24] + records()[60:84])
        with tempfile.TemporaryDirectory() as d:
            save(model, d, {"dataset": "abc"})
            self.assertEqual(
                predict(model, ["invoice due"]), predict(load(d), ["invoice due"])
            )
            p = pathlib.Path(d) / "model.joblib"
            p.write_bytes(p.read_bytes() + b"bad")
            with self.assertRaises(ValueError):
                load(d)
