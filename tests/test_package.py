import unittest
import docreview


class PackageTests(unittest.TestCase):
    def test_package_version(self):
        self.assertRegex(docreview.__version__, r"^\d+\.\d+\.\d+$")
