"""Tests for the photo library builder.

Run: python3 -m unittest discover -s photos/tests
"""

import json
import os
import sys
import tempfile
import unittest
import zipfile
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "_build"))

import photo_library as library  # noqa: E402


def make_library(root, layout):
    for arcname in layout:
        path = os.path.join(root, *arcname.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as handle:
            handle.write(b"\xff\xd8" + arcname.encode())


class BuildTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.source = os.path.join(self.tmp.name, "Originals")
        make_library(self.source, ["Crowds/a.jpg", "Crowds/b.JPG", "Joy/c.jpeg", "Joy/notes.txt", ".hidden/d.jpg"])
        self.exclude = os.path.join(self.tmp.name, "media-kit-exclude.txt")
        with open(self.exclude, "w") as handle:
            handle.write("# readable badge\nCrowds/b.JPG\nMedia/gone.jpg  # moved\n")

    def tearDown(self):
        self.tmp.cleanup()

    def test_zip_holds_group_folders_without_the_excluded_photos(self):
        out = os.path.join(self.tmp.name, "lib.zip")
        summary = library.build(self.source, self.exclude, out)
        self.assertEqual(zipfile.ZipFile(out).namelist(), ["Crowds/a.jpg", "Joy/c.jpeg"])
        self.assertEqual((summary["photos"], summary["excluded"]), (2, 1))
        self.assertEqual(summary["missing_excludes"], ["Media/gone.jpg"])

    def test_photos_are_stored_not_recompressed(self):
        out = os.path.join(self.tmp.name, "lib.zip")
        library.build(self.source, self.exclude, out)
        for info in zipfile.ZipFile(out).infolist():
            self.assertEqual(info.compress_type, zipfile.ZIP_STORED)

    def test_fingerprint_changes_when_a_photo_or_an_exclusion_changes(self):
        files, _ = library.library_files(self.source, set())
        before = library.fingerprint(files, set())
        self.assertEqual(before, library.fingerprint(files, set()))
        self.assertNotEqual(before, library.fingerprint(files, {"Joy/c.jpeg"}))
        make_library(self.source, ["Joy/new.jpg"])
        files, _ = library.library_files(self.source, set())
        self.assertNotEqual(before, library.fingerprint(files, set()))

    def test_an_empty_or_missing_folder_is_an_error(self):
        with self.assertRaises(library.LibraryError):
            library.library_files(os.path.join(self.tmp.name, "nowhere"), set())
        empty = os.path.join(self.tmp.name, "empty")
        os.makedirs(os.path.join(empty, "Crowds"))
        with self.assertRaises(library.LibraryError):
            library.library_files(empty, set())

    def test_exclude_file_defaults_to_the_one_next_to_the_source(self):
        out = os.path.join(self.tmp.name, "lib.zip")
        with mock.patch("sys.stdout"):
            self.assertEqual(library.main(["build", "--source", self.source, "--out", out]), 0)
        self.assertNotIn("Crowds/b.JPG", zipfile.ZipFile(out).namelist())


class PublishTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.source = os.path.join(self.tmp.name, "Originals")
        make_library(self.source, ["Crowds/a.jpg"])

    def tearDown(self):
        self.tmp.cleanup()

    def fake_gh(self, published, names=None):
        calls = []

        def run(*args, check=True, capture=True):
            calls.append(args)
            result = mock.Mock(returncode=0, stderr="")
            if args[:2] == ("release", "download"):
                if published is None:
                    result.returncode = 1
                else:
                    with open(os.path.join(args[args.index("--dir") + 1], library.FINGERPRINT_NAME), "w") as handle:
                        json.dump({"fingerprint": published, "names": names}, handle)
            return result

        return calls, run

    def test_unchanged_library_uploads_nothing(self):
        files, _ = library.library_files(self.source, set())
        calls, run = self.fake_gh(library.fingerprint(files, set()))
        with mock.patch.object(library, "gh", run), mock.patch("sys.stdout"):
            library.publish(self.source, None, library.REPOSITORY)
        self.assertFalse([c for c in calls if c[:2] == ("release", "upload")])

    def test_changed_library_uploads_and_starts_the_media_kit_build(self):
        calls, run = self.fake_gh("old", names=["Crowds/a.jpg", "Crowds/removed.jpg"])
        with mock.patch.object(library, "gh", run), mock.patch("sys.stdout"):
            self.assertEqual(library.publish(self.source, None, library.REPOSITORY), 0)
        upload = [c for c in calls if c[:2] == ("release", "upload")][0]
        self.assertTrue(any(str(a).endswith(library.ZIP_NAME) for a in upload))
        self.assertIn("--clobber", upload)
        self.assertIn(("workflow", "run", library.WORKFLOW, "--repo", library.REPOSITORY, "--ref", "main"), calls)

    def test_a_new_photo_holds_the_publish_until_approved(self):
        make_library(self.source, ["Joy/new.jpg"])
        calls, run = self.fake_gh("old", names=["Crowds/a.jpg"])
        with mock.patch.object(library, "gh", run), mock.patch("sys.stdout"), \
                mock.patch("sys.stderr"), mock.patch.object(library.shutil, "which", return_value=None):
            self.assertEqual(library.publish(self.source, None, library.REPOSITORY), 2)
        self.assertFalse([c for c in calls if c[:2] == ("release", "upload")])
        calls, run = self.fake_gh("old", names=["Crowds/a.jpg"])
        with mock.patch.object(library, "gh", run), mock.patch("sys.stdout"):
            self.assertEqual(library.publish(self.source, None, library.REPOSITORY, approve_new=True), 0)
        self.assertTrue([c for c in calls if c[:2] == ("release", "upload")])

    def test_the_first_publish_needs_approval(self):
        calls, run = self.fake_gh(None)
        with mock.patch.object(library, "gh", run), mock.patch("sys.stdout"), \
                mock.patch("sys.stderr"), mock.patch.object(library.shutil, "which", return_value=None):
            self.assertEqual(library.publish(self.source, None, library.REPOSITORY), 2)
        self.assertFalse([c for c in calls if c[:2] == ("release", "upload")])

class ReleaseTagTest(unittest.TestCase):
    def test_the_media_kit_workflow_reads_the_release_publish_writes(self):
        workflow = os.path.join(HERE, "..", "..", ".github", "workflows", "media-kit.yml")
        with open(workflow, encoding="utf-8") as handle:
            text = handle.read()
        self.assertEqual(library.TAG, "photo-library-1.0")
        self.assertEqual(text.count("gh release download %s " % library.TAG), 2)


if __name__ == "__main__":
    unittest.main()
