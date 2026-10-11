"""Tests for the skill packages, the Copilot agent package and the open-in links.

Run: python3 -m unittest discover -s ai/tests
"""

import io
import json
import os
import re
import sys
import unittest
import urllib.parse
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "agents"))

import build_agent_kits as kits  # noqa: E402


def front_matter(text):
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return match.group(1) if match else ""


class SkillPackageTest(unittest.TestCase):
    def test_each_skill_zip_holds_one_folder_with_skill_md_on_top(self):
        for name in kits.BRAND_SKILLS:
            names = zipfile.ZipFile(io.BytesIO(kits.make_zip(kits.skill_entries(name)))).namelist()
            self.assertIn("%s/SKILL.md" % name, names)
            self.assertTrue(all(n.startswith(name + "/") for n in names), names)

    def test_no_package_carries_the_private_rules(self):
        for path, data in kits.outputs().items():
            if path.endswith(".zip"):
                names = zipfile.ZipFile(io.BytesIO(data)).namelist()
                self.assertFalse([n for n in names if "private_rules" in n or n.endswith(".pyc")], path)

    def test_zips_are_the_same_bytes_every_build(self):
        first = kits.outputs()
        self.assertEqual(first, kits.outputs())

    def test_brand_skill_front_matter_has_no_plain_value_strict_yaml_rejects(self):
        # npx skills reads front matter with a strict YAML parser and skips a skill it cannot read.
        for name in kits.BRAND_SKILLS:
            with open(os.path.join(kits.ROOT, kits.SKILLS_DIR, name, "SKILL.md"), encoding="utf-8") as handle:
                matter = front_matter(handle.read())
            self.assertIn("name: %s" % name, matter)
            for line in matter.split("\n"):
                found = re.match(r"^([a-z][\w-]*): (.+)$", line)
                if found and not found.group(2).startswith(("'", '"', "|", ">")):
                    self.assertNotIn(": ", found.group(2), "%s: quote %s" % (name, found.group(1)))
                    self.assertNotIn(" #", found.group(2), "%s: quote %s" % (name, found.group(1)))


class SkillsLockTest(unittest.TestCase):
    def test_lock_lists_every_house_skill_and_no_brand_skill(self):
        lock = json.loads(kits.skills_lock())
        base = os.path.join(kits.ROOT, kits.SKILLS_DIR)
        present = {n for n in os.listdir(base) if os.path.isfile(os.path.join(base, n, "SKILL.md"))}
        self.assertEqual(set(lock["skills"]), present - set(kits.BRAND_SKILLS))
        self.assertEqual(lock["version"], 1)


class CopilotPackageTest(unittest.TestCase):
    def setUp(self):
        self.files = {name: data for name, data, _ in kits.copilot_entries()}

    def test_package_has_manifest_agent_and_both_icons(self):
        self.assertEqual(set(self.files), {"manifest.json", "declarativeAgent.json", "color.png", "outline.png"})
        manifest = json.loads(self.files["manifest.json"])
        self.assertEqual(manifest["icons"], {"color": "color.png", "outline": "outline.png"})
        self.assertEqual(manifest["copilotAgents"]["declarativeAgents"][0]["file"], "declarativeAgent.json")
        self.assertRegex(manifest["id"], r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
        self.assertLessEqual(len(manifest["name"]["short"]), 30)
        self.assertLessEqual(len(manifest["description"]["short"]), 80)

    def test_icons_are_the_sizes_the_store_needs(self):
        def png_size(data):
            self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
            return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")

        self.assertEqual(png_size(self.files["color.png"]), (192, 192))
        self.assertEqual(png_size(self.files["outline.png"]), (32, 32))

    def test_agent_stays_inside_the_declarative_agent_limits(self):
        agent = json.loads(self.files["declarativeAgent.json"])
        self.assertEqual(agent["version"], "v1.5")
        self.assertLessEqual(len(agent["name"]), 100)
        self.assertLessEqual(len(agent["description"]), 1000)
        self.assertTrue(0 < len(agent["instructions"]) <= 8000)
        self.assertLessEqual(len(agent["conversation_starters"]), 12)
        for capability in agent["capabilities"]:
            if capability["name"] == "WebSearch":
                self.assertLessEqual(len(capability["sites"]), 4)
                for site in capability["sites"]:
                    parsed = urllib.parse.urlparse(site["url"])
                    self.assertEqual(parsed.scheme, "https")
                    self.assertFalse(parsed.query)
                    self.assertLessEqual(len([p for p in parsed.path.split("/") if p]), 2, site["url"])

    def test_instructions_are_ascii_without_long_dashes(self):
        text = json.loads(self.files["declarativeAgent.json"])["instructions"]
        text.encode("ascii")


class OpenInTest(unittest.TestCase):
    def setUp(self):
        self.data = kits.open_in()

    def test_every_target_has_a_label_link_and_honest_how(self):
        ids = [t["id"] for t in self.data["targets"]]
        self.assertEqual(ids, ["claude", "claude-code", "codex", "copilot"])
        for target in self.data["targets"]:
            self.assertTrue(target["label"].startswith("Open in "))
            self.assertTrue(target["how"])
            (target["label"] + target["how"] + target["install"]).encode("ascii")

    def test_links_carry_a_prompt_that_names_both_skills(self):
        for target in self.data["targets"]:
            parsed = urllib.parse.urlparse(target["url"])
            query = urllib.parse.parse_qs(parsed.query)
            prompt = (query.get("q") or query.get("prompt"))[0]
            for name in kits.BRAND_SKILLS:
                self.assertIn(name, prompt, target["id"])
        code = urllib.parse.parse_qs(urllib.parse.urlparse(self.data["targets"][1]["url"]).query)
        self.assertEqual(code["repositories"], [kits.REPOSITORY])

    def test_install_commands_name_the_repository(self):
        self.assertEqual(self.data["install"]["every agent"], "npx skills add Climb-Group/Brand-System")


if __name__ == "__main__":
    unittest.main()
