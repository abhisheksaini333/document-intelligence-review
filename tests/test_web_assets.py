import unittest, pathlib, tempfile
from docreview.api import web_root


class WheelAssetsTests(unittest.TestCase):
    def test_packaged_assets_fallback(self):
        with tempfile.TemporaryDirectory() as d:
            d = pathlib.Path(d)
            package = d / "lib/docreview"
            package.mkdir(parents=True)
            (package / "web").mkdir()
            (package / "web/index.html").write_text("site")
            self.assertEqual(web_root(package), package / "web")
