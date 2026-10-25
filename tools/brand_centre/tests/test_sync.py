"""Tests for the Brand Centre sync's decisions. They need no library and no rclone."""
import os
import sys
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


class PlanPushTest(unittest.TestCase):
    def test_first_push_sends_every_tracked_file_but_internal(self):
        tracked = ["README.md", "internal/README.md", "logos/a.svg", ".github/workflows/check.yml", ""]
        self.assertEqual(sync.plan_push(None, [], tracked), (["README.md", "logos/a.svg"], []))

    def test_later_push_sends_only_the_diff(self):
        tracked = ["README.md", "logos/a.svg", "logos/new.svg"]
        diff = ["M\tREADME.md", "A\tlogos/new.svg", "D\tlogos/old.svg", ""]
        self.assertEqual(sync.plan_push("abc", diff, tracked), (["README.md", "logos/new.svg"], ["logos/old.svg"]))

    def test_rename_removes_old_path_and_sends_new_one(self):
        tracked = ["guidelines/new.md"]
        diff = ["R100\tguidelines/old.md\tguidelines/new.md"]
        self.assertEqual(sync.plan_push("abc", diff, tracked), (["guidelines/new.md"], ["guidelines/old.md"]))

    def test_push_never_touches_internal(self):
        diff = ["M\tinternal/README.md", "D\tinternal/notes.md"]
        self.assertEqual(sync.plan_push("abc", diff, ["internal/README.md"]), ([], []))


class ExcludedTest(unittest.TestCase):
    def test_excluded_paths(self):
        for path in ("internal/notes.md", ".brand-centre-sync/manifest.json", ".git/config",
                     "templates/~$Letterhead.dotx", "pdf/.~lock.flyer.odt#", "photos/Thumbs.db",
                     "photos/.DS_Store", "a/desktop.ini", "upload.tmp"):
            self.assertTrue(sync.excluded(path), path)

    def test_pack_paths_are_synced(self):
        for path in ("README.md", "logos/climbuk.svg", "guidelines/voice.md", "photos/internal-shots.jpg"):
            self.assertFalse(sync.excluded(path), path)


if __name__ == "__main__":
    unittest.main()
