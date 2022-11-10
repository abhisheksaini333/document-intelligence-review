import unittest, tempfile, json, pathlib, hashlib, os


class BentoServiceTests(unittest.TestCase):
    def test_service_registration(self):
        import service

        self.assertIn("classify", service.svc.apis)
        self.assertIn("model", service.svc.apis)
