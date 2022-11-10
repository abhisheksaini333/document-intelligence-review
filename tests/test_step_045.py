import unittest, tempfile, json, pathlib, hashlib, os

from docreview.ingest import preview
from PIL import Image
import io


class PreviewTests(unittest.TestCase):
    def test_tiff_pages(self):
        stream = io.BytesIO()
        Image.new("RGB", (20, 30), "white").save(
            stream,
            format="TIFF",
            save_all=True,
            append_images=[Image.new("RGB", (40, 50), "black")],
        )
        data = stream.getvalue()
        with Image.open(io.BytesIO(preview(data, 2))) as im:
            self.assertEqual(im.size, (40, 50))
            self.assertEqual(im.format, "PNG")
        with self.assertRaises(ValueError):
            preview(data, 3)
