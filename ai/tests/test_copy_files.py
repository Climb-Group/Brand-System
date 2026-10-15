"""Tests for copy files (*.copy.md) and their parser. Run: python3 -m unittest discover -s ai/tests"""

import io
import os
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCRIPTS = ROOT / ".agents" / "skills" / "climb-voice" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import check_copy  # noqa: E402
import copy_md  # noqa: E402

SAMPLE = """---
copy: sample-flyer
deliverable: A sample flyer
build: pdf/sample/build.py
---

# Sample flyer

<!-- note: Read this first. -->

## Front

<!-- @front.headline -->
Scale with the [[right people]]
in the *room*.

<!-- @front.photo name=crowds_04 focus=0.5,0.35 -->

<!-- @back.reason icon=people label="Two words" -->
### Find your people
Fellow founders one step ahead.

<!-- @back.reason icon=calendar -->
<!-- note: Check the app name with the events team. -->
### Meetings you choose
Book in the ClimbGroup Event App.

<!-- @back.qr-note -->
Scan and pick\\
who you are

- first
- second
"""


def problem(text):
    """The message of the CopyError that text raises."""
    try:
        copy_md.parse(text, "t.copy.md")
    except copy_md.CopyError as e:
        return str(e)
    raise AssertionError("expected a CopyError")


class ParseTest(unittest.TestCase):
    def setUp(self):
        self.doc = copy_md.parse(SAMPLE, "sample.copy.md")

    def test_front_matter(self):
        self.assertEqual(self.doc.meta, {"copy": "sample-flyer", "deliverable": "A sample flyer", "build": "pdf/sample/build.py"})

    def test_sections_in_order_with_settings(self):
        self.assertEqual([s.path for s in self.doc.sections],
                         ["front.headline", "front.photo", "back.reason", "back.reason", "back.qr-note"])
        self.assertEqual(self.doc.one("front.photo").settings, {"name": "crowds_04", "focus": "0.5,0.35"})
        self.assertEqual(self.doc.all("back.reason")[0]["label"], "Two words")

    def test_soft_wrapped_lines_join_and_markup_is_kept(self):
        self.assertEqual(self.doc.one("front.headline").text, "Scale with the [[right people]] in the *room*.")

    def test_title_and_text(self):
        first, second = self.doc.all("back.reason")
        self.assertEqual((first.title, first.text), ("Find your people", "Fellow founders one step ahead."))
        self.assertEqual((second.title, second.text), ("Meetings you choose", "Book in the ClimbGroup Event App."))

    def test_hard_breaks_and_lists_keep_their_lines(self):
        self.assertEqual(self.doc.one("back.qr-note").text, "Scan and pick\nwho you are\n\n- first\n- second")

    def test_notes_are_kept_apart_from_the_words(self):
        self.assertEqual([n["text"] for n in self.doc.notes], ["Read this first.", "Check the app name with the events team."])
        self.assertNotIn("events team", self.doc.all("back.reason")[1].text)

    def test_a_part_heading_ends_the_open_section(self):
        doc = copy_md.parse("---\ncopy: a\ndeliverable: A\n---\n<!-- @one -->\nWords.\n## Back\n<!-- @two -->\nMore.\n")
        self.assertEqual([s.text for s in doc.sections], ["Words.", "More."])

    def test_words_and_one(self):
        self.assertEqual(self.doc.words("front.subline", "Tagline"), "Tagline")
        with self.assertRaises(copy_md.CopyError):
            self.doc.one("back.reason")

    def test_reader_words_drop_markup(self):
        words = copy_md.reader_words(self.doc)
        self.assertIn("Scale with the right people in the room.", words)
        self.assertNotIn("crowds_04", words)


class ErrorTest(unittest.TestCase):
    HEAD = "---\ncopy: a\ndeliverable: A\n---\n"

    def test_front_matter_is_required(self):
        self.assertIn("front matter", problem("<!-- @a -->\nWords.\n"))
        self.assertIn("deliverable", problem("---\ncopy: a\n---\n"))
        self.assertIn("lowercase id", problem("---\ncopy: Big Name\ndeliverable: A\n---\n"))

    def test_section_names(self):
        self.assertIn("t.copy.md:5:", problem(self.HEAD + "<!-- @Front.Headline -->\nWords.\n"))
        self.assertIn("lowercase words", problem(self.HEAD + "<!-- @front_headline -->\nWords.\n"))

    def test_settings(self):
        self.assertIn("given twice", problem(self.HEAD + "<!-- @a icon=x icon=y -->\n"))
        self.assertIn("cannot read settings", problem(self.HEAD + "<!-- @a icon -->\n"))

    def test_words_outside_a_section(self):
        self.assertIn("outside a section", problem(self.HEAD + "Stray words.\n"))

    def test_markers_on_their_own_line(self):
        self.assertIn("own line", problem(self.HEAD + "<!-- @a -->\nWords <!-- @b --> here.\n"))

    def test_unclosed_comment(self):
        self.assertIn("not closed", problem(self.HEAD + "<!-- note: open\n"))


class CheckerTest(unittest.TestCase):
    def test_words_only_keeps_line_and_column(self):
        text = SAMPLE.replace("Fellow founders", "Guaranteed founders")
        blank = copy_md.words_only(text)
        self.assertEqual(blank.count("\n"), text.count("\n"))
        self.assertNotIn("crowds_04", blank)
        line_no, col = check_copy.check(blank)[0][:2]
        self.assertEqual(text.splitlines()[line_no - 1][col - 1:col + 9], "Guaranteed")

    def test_checker_reads_copy_files(self):
        bad = ROOT / "build" / "test-bad.copy.md"
        bad.parent.mkdir(exist_ok=True)
        try:
            bad.write_text(SAMPLE.replace("Fellow founders", "Guaranteed founders"))
            with redirect_stdout(io.StringIO()) as out:
                self.assertEqual(check_copy.main(["--no-hints", str(bad)]), 1)
            self.assertIn("no guarantees", out.getvalue())
            bad.write_text(SAMPLE.replace("@front.headline", "@Front"))
            with redirect_stdout(io.StringIO()) as out:
                self.assertEqual(check_copy.main(["--no-hints", str(bad)]), 1)
            self.assertIn("section name", out.getvalue())
        finally:
            bad.unlink(missing_ok=True)


class RepositoryTest(unittest.TestCase):
    def files(self):
        out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "*.copy.md"],
                             cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
        return [ROOT / p for p in out]

    def test_every_copy_file_follows_the_standard_and_the_copy_rules(self):
        files = self.files()
        self.assertTrue(files)
        ids = {}
        for path in files:
            doc = copy_md.load(path)
            self.assertNotIn(doc.meta["copy"], ids, "copy id used twice: %s and %s" % (path, ids.get(doc.meta["copy"])))
            ids[doc.meta["copy"]] = path
            if "build" in doc.meta:
                self.assertTrue((ROOT / doc.meta["build"]).exists(), "%s: build %s does not exist" % (path, doc.meta["build"]))
            copy_md.covered(doc, ROOT)
            if doc.meta.get("source") == "mirror":
                continue  # a mirror shows what a build elsewhere prints; its rule breaks are listed in its notes
            problems = check_copy.check(copy_md.words_only(path.read_text(encoding="utf-8")))
            allowed = doc.meta.get("allow", "").lower().split()  # staff-only words the piece must print
            problems = [p for p in problems if p[2].lower() not in allowed]
            self.assertEqual(problems, [], path)

    def test_every_deliverable_has_a_copy_file(self):
        missing, problems = copy_md.coverage(ROOT, copy_md._tracked(ROOT))
        self.assertEqual(problems, [])
        self.assertEqual([str(p.relative_to(ROOT)) for p in missing], [], "files with no copy file covering them")

    def test_example_sections_are_skipped_by_the_checker(self):
        text = "---\ncopy: x\ndeliverable: x\n---\n<!-- @rule.bad example=avoid -->\nWe guarantee it\n\n## Next\n<!-- @rule.good -->\nWe guarantee it\n"
        problems = check_copy.check(copy_md.words_only(text))
        self.assertEqual(len([p for p in problems if "guarantee" in p[3]]), 1)
        self.assertEqual(copy_md.parse(text, "x.copy.md").all("rule.bad")[0].text, "We guarantee it")

    def test_output_takes_several_paths_and_globs(self):
        doc = copy_md.parse("---\ncopy: x\ndeliverable: x\noutput: README.md tokens/*.css\n---\n", str(ROOT / "x.copy.md"))
        got = copy_md.covered(doc, ROOT)
        self.assertIn((ROOT / "README.md").resolve(), got)
        self.assertIn((ROOT / "tokens" / "tokens.css").resolve(), got)
        bad = copy_md.parse("---\ncopy: x\ndeliverable: x\noutput: nothing/*.pdf\n---\n", str(ROOT / "x.copy.md"))
        with self.assertRaises(copy_md.CopyError):
            copy_md.covered(bad, ROOT)


if __name__ == "__main__":
    unittest.main()
