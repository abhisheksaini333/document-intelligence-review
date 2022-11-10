import unittest, tempfile, json, pathlib, hashlib, os

import subprocess, sys


class CliTests(unittest.TestCase):
    def test_cli(self):
        p = subprocess.run(
            [sys.executable, "-m", "docreview", "--version"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(p.returncode, 0)
        self.assertIn("0.1.0", p.stdout)
        p = subprocess.run(
            [sys.executable, "-m", "docreview", "fixtures"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(len(json.loads(p.stdout)), 180)
