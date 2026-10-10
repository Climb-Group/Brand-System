"""Run with: python3 -m unittest discover -s tokens/tests"""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import build_tokens as B  # noqa: E402


class TokenTests(unittest.TestCase):
    def setUp(self):
        self.tree = B.load()

    def test_every_promised_pair_passes(self):
        _, failures = B.check_pairs(self.tree)
        self.assertEqual(failures, [], "pairs below threshold: %r" % failures)

    def test_ratio_matches_the_audit(self):
        # The October 2026 audit measured white on Climb Orange at 3.08:1 and the old orange at 2.94:1.
        self.assertAlmostEqual(B.ratio("#FFFFFF", "#E8712A"), 3.08, places=2)
        self.assertLess(B.ratio("#FFFFFF", "#EC752A"), 3.0)

    def test_old_orange_is_gone(self):
        values = [str(v).upper() for _, v in B.flatten(self.tree)]
        self.assertNotIn("#EC752A", values)

    def test_references_resolve(self):
        for path, value in B.flatten(self.tree):
            self.assertFalse(isinstance(value, str) and value.startswith("{"), "unresolved %s" % ".".join(path))

    def test_generated_files_are_current(self):
        css, scss = B.render(self.tree)
        self.assertEqual(B.CSS_OUT.read_text(encoding="utf-8"), css)
        self.assertEqual(B.SCSS_OUT.read_text(encoding="utf-8"), scss)


if __name__ == "__main__":
    unittest.main()
