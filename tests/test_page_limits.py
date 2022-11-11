import unittest, io
from PIL import Image
from docreview.ingest import validate_image


class PageLimitTests(unittest.TestCase):
    def test_later_tiff_page_is_checked(self):
        stream = io.BytesIO()
        Image.new("RGB", (10, 10)).save(
            stream,
            format="TIFF",
            compression="tiff_deflate",
            save_all=True,
            append_images=[Image.new("RGB", (5000, 5000))],
        )
        with self.assertRaises(ValueError):
            validate_image(stream.getvalue())
