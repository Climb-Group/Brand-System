"""Tests for the local personal preferences file.

Run: python3 -m unittest discover -s ai/tests
"""

import datetime
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "preferences"))

import preferences as prefs  # noqa: E402

DAY = datetime.date(2026, 10, 14)


class FolderTest(unittest.TestCase):
    def test_override_wins(self):
        self.assertEqual(prefs.folder({"CLIMB_PREFERENCES_DIR": "/x"}, "linux"), "/x")

    def test_windows_uses_local_app_data(self):
        got = prefs.folder({"LOCALAPPDATA": "C:\\Users\\a\\AppData\\Local"}, "win32")
        self.assertTrue(got.startswith("C:\\Users\\a\\AppData\\Local"))
        self.assertTrue(got.endswith("climb-preferences"))

    def test_unix_uses_xdg_data_home(self):
        self.assertEqual(prefs.folder({"XDG_DATA_HOME": "/d"}, "linux"), os.path.join("/d", "climb-preferences"))


class AddEntryTest(unittest.TestCase):
    def test_first_entry_creates_title_and_topic(self):
        got = prefs.add_entry("", "reply style", "Lead with the answer.", DAY)
        self.assertEqual(got, prefs.TITLE + "\n\n## Reply style\n- 2026-10-14: Lead with the answer.\n")

    def test_entry_joins_its_topic(self):
        text = prefs.add_entry("", "devices", "Linux first.", DAY)
        text = prefs.add_entry(text, "replies", "Short.", DAY)
        text = prefs.add_entry(text, "devices", "Mac on Wednesday.", DAY)
        lines = text.splitlines()
        devices = lines.index("## Devices")
        self.assertEqual(lines[devices + 1:devices + 3], ["- 2026-10-14: Linux first.", "- 2026-10-14: Mac on Wednesday."])
        self.assertEqual(lines[-2:], ["## Replies", "- 2026-10-14: Short."])

    def test_repeat_is_not_duplicated(self):
        once = prefs.add_entry("", "replies", "Short.", DAY)
        self.assertEqual(prefs.add_entry(once, "replies", "Short.", DAY), once)

    def test_empty_preference_is_refused(self):
        with self.assertRaises(ValueError):
            prefs.add_entry("", "replies", "   ", DAY)

    def test_topic_needs_a_word(self):
        with self.assertRaises(ValueError):
            prefs.topic_heading("!!")


if __name__ == "__main__":
    unittest.main()
