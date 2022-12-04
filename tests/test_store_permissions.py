import unittest, tempfile, pathlib, concurrent.futures
from docreview.store import Store, Conflict


class PrivateStoreTests(unittest.TestCase):
    def test_database_is_private(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "nested/review.sqlite"
            Store(p)
            self.assertEqual(p.stat().st_mode & 0o777, 0o600)
            self.assertEqual(p.parent.stat().st_mode & 0o777, 0o700)

    def test_only_one_concurrent_review_wins(self):
        with tempfile.TemporaryDirectory() as d:
            s = Store(pathlib.Path(d) / "s")
            r = s.create("a" * 64, "x", "x")
            s.result(r["id"], 1, {"fields": {}})

            def write(name):
                try:
                    s.review(r["id"], 2, {"number": name}, "invoice", name, "save")
                    return True
                except Conflict:
                    return False

            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(write, ["alice", "bob"]))
            self.assertEqual(sum(results), 1)
            self.assertEqual(len(s.events(r["id"])), 1)
