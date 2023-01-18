import unittest, tempfile, pathlib, json, math, os
from unittest.mock import patch, Mock

class Maintenance(unittest.TestCase):

    def test_dir01(self):
        from docreview.domain import Field,Box
        base=dict(name='total',value='1',confidence=.8,page=1,box=None,method='ocr')
        for name,value in [('page',True),('page',1.5),('confidence',True),('confidence','1'),('box',{}),('method','')]:
            with self.assertRaises(ValueError):Field(**{**base,name:value})
        self.assertEqual(Field(**base).page,1)
