"""Tests for the prompt library, its exports and the plugin packages.

Run: python3 -m unittest discover -s ai/tests
"""

import csv
import io
import json
import os
import re
import sys
import unittest
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "prompts"))

import build_prompts as bp  # noqa: E402


def names(data):
    return zipfile.ZipFile(io.BytesIO(data)).namelist()


class LibraryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prompts = bp.load()
        cls.files = bp.outputs(cls.prompts)

    def test_every_prompt_passes_the_rules(self):
        self.assertEqual(bp.validate(self.prompts), [])

    def test_every_task_type_has_at_least_three_prompts(self):
        for task in bp.TASK_TYPES:
            self.assertGreaterEqual(len([p for p in self.prompts if p["task"] == task]), 3, task)

    def test_rules_catch_a_bad_prompt(self):
        bad = dict(self.prompts[0], title="The biggest event of the year, guaranteed", task="Manage", apps="Copilot app")
        found = " ".join(bp.problems(bad, [bad["slug"]]))
        for expected in ("title is", "not a supported task type", "apps must be", "superlative", "guarantee"):
            self.assertIn(expected, found)

    def test_placeholders_never_reach_the_title_or_display_prompt(self):
        bad = dict(self.prompts[0], display="Write about {{topic}}")
        self.assertTrue(any("placeholders" in p for p in bp.problems(bad, [bad["slug"]])))

    def test_exports_are_current(self):
        for path, data in self.files.items():
            with open(os.path.join(bp.ROOT, path), "rb") as handle:
                self.assertEqual(handle.read(), data, "%s is stale: run python3 ai/prompts/build_prompts.py" % path)

    def test_exports_are_the_same_bytes_every_build(self):
        self.assertEqual(self.files, bp.outputs(self.prompts))


class CopilotCsvTest(unittest.TestCase):
    def setUp(self):
        self.prompts = bp.load()
        data = bp.outputs(self.prompts)[bp.DIST + "/copilot/climbuk-prompts.csv"]
        self.assertTrue(data.startswith(b"\xef\xbb\xbf"), "Microsoft's template is UTF-8 with a byte order mark")
        self.rows = list(csv.reader(io.StringIO(data.decode("utf-8-sig"))))

    def test_header_matches_microsofts_template(self):
        self.assertEqual(self.rows[0], ["Title", "Description", "Display Prompt", "Prompt Text", "Products", "Department", "Task Type", "Locale"])

    def test_one_row_per_prompt_within_the_import_cap(self):
        self.assertEqual(len(self.rows) - 1, len(self.prompts))
        self.assertLessEqual(len(self.rows) - 1, bp.PER_FILE)

    def test_rows_respect_microsofts_limits_and_values(self):
        for title, description, display, text, products, department, task, locale in self.rows[1:]:
            self.assertLessEqual(len(title), 35)
            self.assertLessEqual(len(description), 200)
            self.assertLessEqual(len(display), 132)
            self.assertLessEqual(len(text), 8000)
            self.assertLessEqual(len(department), 120)
            self.assertIn(task, bp.TASK_TYPES)
            self.assertTrue(products and all(p in bp.APPS for p in products.split(", ")), products)
            self.assertTrue(title and display and text and locale)

    def test_brand_rules_are_in_the_prompt_text(self):
        voice = [r for r, p in zip(self.rows[1:], self.prompts) if p["brand"] in ("voice", "both")]
        self.assertTrue(voice)
        for row in voice:
            self.assertIn("climb-voice", row[3])


class AssistantExportTest(unittest.TestCase):
    def setUp(self):
        self.prompts = bp.load()
        self.files = bp.outputs(self.prompts)

    def read(self, archive, member):
        return zipfile.ZipFile(io.BytesIO(self.files[archive])).read(member).decode()

    def test_every_export_has_one_file_per_prompt(self):
        for archive in ("claude-code-commands", "codex-prompts", "cursor-commands", "vscode-prompt-files", "gemini-cli-commands"):
            self.assertEqual(len(names(self.files["%s/%s.zip" % (bp.DIST, archive)])), len(self.prompts), archive)

    def test_placeholders_use_each_tools_own_syntax(self):
        p = next(p for p in self.prompts if p["slug"] == "linkedin-post")
        claude = self.read(bp.DIST + "/claude-code-commands.zip", ".claude/commands/climb/linkedin-post.md")
        self.assertIn("[topic]", claude)
        self.assertIn("$ARGUMENTS", claude)
        self.assertIn("$TOPIC", self.read(bp.DIST + "/codex-prompts.zip", "prompts/climb-linkedin-post.md"))
        self.assertIn("${input:topic:topic}", self.read(bp.DIST + "/vscode-prompt-files.zip", ".github/prompts/climb-linkedin-post.prompt.md"))
        gemini = self.read(bp.DIST + "/gemini-cli-commands.zip", ".gemini/commands/climb/linkedin-post.toml")
        self.assertIn("{{args}}", gemini)
        self.assertNotIn("{{topic}}", gemini)
        self.assertEqual(bp.placeholders(p), ["topic", "audience"])

    def test_json_library_lists_every_prompt(self):
        data = json.loads(self.files[bp.DIST + "/prompts.json"])
        self.assertEqual([p["id"] for p in data["prompts"]], [p["slug"] for p in self.prompts])
        self.assertEqual(data["task_types"], list(bp.TASK_TYPES))


class PluginTest(unittest.TestCase):
    def setUp(self):
        self.prompts = bp.load()
        self.files = bp.outputs(self.prompts)

    def test_cowork_skill_uploads_have_skill_md_at_the_top(self):
        for name in bp.all_skills():
            listed = names(self.files["%s/cowork/%s.zip" % (bp.PACKAGES, name)])
            self.assertIn("SKILL.md", listed)
            self.assertLessEqual(len(listed), 100)
            self.assertFalse([n for n in listed if n.startswith(".") or "/." in n or ".." in n], listed)

    def test_m365_plugin_manifest_lists_each_skill_folder(self):
        archive = zipfile.ZipFile(io.BytesIO(self.files[bp.PACKAGES + "/climbuk-brand-plugin-m365.zip"]))
        manifest = json.loads(archive.read("manifest.json"))
        self.assertEqual(manifest["manifestVersion"], "1.28")
        self.assertLessEqual(len(manifest["agentSkills"]), 20)
        listed = archive.namelist()
        for entry in manifest["agentSkills"]:
            folder = entry["folder"][2:]
            skill = archive.read(folder + "/SKILL.md").decode()
            name = re.search(r"^name: (.+)$", skill, re.M).group(1).strip()
            self.assertEqual(name, folder.split("/")[-1], "Cowork needs the folder name to equal the skill name")
            description = re.search(r"^description: (.+)$", skill, re.M).group(1).strip().strip("'\"")
            self.assertLessEqual(len(description), 1024)
            companions = [n for n in listed if n.startswith(folder + "/") and n != folder + "/SKILL.md"]
            self.assertLessEqual(len(companions), 20, folder)
        for icon in ("color.png", "outline.png"):
            self.assertIn(icon, listed)

    def test_claude_plugin_has_manifest_skills_and_commands(self):
        listed = names(self.files[bp.PACKAGES + "/climbuk-brand-plugin.zip"])
        manifest = json.loads(zipfile.ZipFile(io.BytesIO(self.files[bp.PACKAGES + "/climbuk-brand-plugin.zip"])).read(".claude-plugin/plugin.json"))
        self.assertEqual(manifest["name"], bp.PLUGIN)
        for name in bp.all_skills():
            self.assertIn("skills/%s/SKILL.md" % name, listed)
        self.assertEqual(len([n for n in listed if n.startswith("commands/")]), len(self.prompts))

    def test_no_package_carries_the_private_rules(self):
        for path, data in self.files.items():
            if path.endswith(".zip"):
                self.assertFalse([n for n in names(data) if "private_rules" in n or n.endswith(".pyc")], path)


if __name__ == "__main__":
    unittest.main()
