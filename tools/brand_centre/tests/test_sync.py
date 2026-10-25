"""Tests for the Brand Centre sync's decisions. They need no library and no rclone."""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import sync  # noqa: E402


def entry(h, size=10):
    return {"hash": h, "size": size}


class FindEditsTest(unittest.TestCase):
    def test_untouched_library_has_no_edits(self):
        files = {"a.md": entry("1"), "logos/b.png": entry("2")}
        self.assertEqual(sync.find_edits(files, dict(files)), ([], []))

    def test_changed_added_and_removed_files_are_edits(self):
        manifest = {"a.md": entry("1"), "b.md": entry("2"), "c.md": entry("3")}
        listing = {"a.md": entry("1"), "b.md": entry("9"), "new.md": entry("4")}
        self.assertEqual(sync.find_edits(manifest, listing), (["b.md", "new.md"], ["c.md"]))

    def test_sharepoint_rewrite_is_not_an_edit(self):
        # The manifest holds the library's own hash after upload, so a file SharePoint rewrote on the way in
        # matches it, even though its bytes no longer match the repository.
        manifest = {"web/index.html": entry("hash-after-sharepoint-rewrite")}
        listing = {"web/index.html": entry("hash-after-sharepoint-rewrite")}
        self.assertEqual(sync.find_edits(manifest, listing), ([], []))


class SeedFilesTest(unittest.TestCase):
    def test_seed_copies_every_tracked_file_but_internal(self):
        tracked = ["README.md", "internal/README.md", "logos/a.svg", ".github/workflows/check.yml", ""]
        self.assertEqual(sync.seed_files(tracked), ["README.md", "logos/a.svg"])


class ListingTest(unittest.TestCase):
    def test_mark_writes_the_listing_pull_compared(self):
        # An edit made in the library after pull listed it must still be found next run, so mark records the
        # listing pull saved, never a fresh one.
        listing = {"a.md": entry("1"), "logos/b.png": entry("2", 99)}
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "listing.json")
            sync.save_listing(listing, path)
            self.assertEqual(sync.load_listing(path), listing)

    def test_marked_listing_hides_pulled_edits_but_not_later_ones(self):
        pulled = {"a.md": entry("9"), "new.md": entry("4")}
        later = {"a.md": entry("9"), "new.md": entry("5")}
        self.assertEqual(sync.find_edits(pulled, pulled), ([], []))
        self.assertEqual(sync.find_edits(pulled, later), (["new.md"], []))


class ExcludedTest(unittest.TestCase):
    def test_excluded_paths(self):
        for path in ("internal/notes.md", "templates/internal/tool/run.py", ".brand-centre-sync/manifest.json", ".git/config",
                     "templates/~$Letterhead.dotx", "pdf/.~lock.flyer.odt#", "photos/Thumbs.db",
                     "photos/.DS_Store", "a/desktop.ini", "upload.tmp"):
            self.assertTrue(sync.excluded(path), path)

    def test_pack_paths_are_synced(self):
        for path in ("README.md", "logos/climbuk.svg", "guidelines/voice.md", "photos/internal-shots.jpg",
                     "photos/internal"):
            self.assertFalse(sync.excluded(path), path)


if __name__ == "__main__":
    unittest.main()
