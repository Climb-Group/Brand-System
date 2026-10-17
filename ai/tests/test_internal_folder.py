"""The internal/ folder holds team-only material that must never be committed.

Run: python3 -m unittest discover -s ai/tests"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / ".agents" / "skills" / "climb-voice" / "scripts"))

import copy_md  # noqa: E402


def ignored(path):
    """True when git ignores path (relative to the pack root)."""
    return subprocess.run(["git", "check-ignore", "-q", "--no-index", path], cwd=ROOT).returncode == 0


class InternalFolder(unittest.TestCase):
    def test_everything_in_internal_is_ignored(self):
        for path in ("internal/testimonial-map/who-was-there-testimonial-map.html",
                     "internal/notes.md", "internal/data.csv", "internal/deep/er/file.pdf"):
            with self.subTest(path=path):
                self.assertTrue(ignored(path), "%s would be committed" % path)

    def test_readme_is_public(self):
        self.assertFalse(ignored("internal/README.md"))
        self.assertTrue((ROOT / "internal" / "README.md").is_file())

    def test_only_the_internal_folder_at_the_root(self):
        # A folder called internal deeper in the pack is ordinary content.
        self.assertFalse(ignored("templates/internal/README.md"))

    def test_checks_skip_internal_files(self):
        folder = ROOT / "internal"
        with tempfile.NamedTemporaryFile(dir=folder, suffix=".pdf") as handle:
            name = "internal/" + Path(handle.name).name
            listed = copy_md._tracked(ROOT)
            self.assertNotIn(name, listed)
            missing, _problems = copy_md.coverage(ROOT, listed)
            self.assertNotIn(Path(handle.name).resolve(), missing)


if __name__ == "__main__":
    unittest.main()
