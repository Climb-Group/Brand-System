"""Tests for the AI brand tools. Run: python3 -m unittest discover -s ai/tests"""

import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))

import brand_rules  # noqa: E402

AI_DIR = os.path.join(HERE, "..")


class KitTest(unittest.TestCase):
    def test_every_tool_in_the_kit_runs(self):
        kit = brand_rules.kit()
        self.assertEqual(sorted(t["key"] for t in kit["tools"]), sorted(brand_rules.TOOLS))
        for tool in kit["tools"]:
            result = brand_rules.call(tool["key"], {})
            self.assertIn("ok", result, tool["key"])
            json.dumps(result)

    def test_skills_and_agents_point_at_real_files_and_tools(self):
        kit = brand_rules.kit()
        tool_keys = {t["key"] for t in kit["tools"]}
        skill_keys = set()
        for skill in kit["skills"]:
            skill_keys.add(skill["key"])
            self.assertTrue(os.path.exists(os.path.join(AI_DIR, skill["instructions"])), skill["key"])
            self.assertTrue(set(skill["tools"]) <= tool_keys, skill["key"])
        for agent in kit["agents"]:
            self.assertTrue(os.path.exists(os.path.join(AI_DIR, agent["instructions"])))
            self.assertTrue(set(agent["skills"]) <= skill_keys)

    def test_tool_schemas_give_strings_a_max_length(self):
        for tool in brand_rules.kit()["tools"]:
            params = tool["parameters"]
            self.assertEqual(params["type"], "object")
            self.assertRegex(tool["name"], r"^[a-zA-Z0-9_]{1,64}$")
            self.assertTrue(tool["progress"])
            for name, spec in params["properties"].items():
                if spec["type"] == "string":
                    self.assertIn("maxLength", spec, "%s.%s" % (tool["key"], name))
            self.assertTrue(set(params["required"]) <= set(params["properties"]))

    def test_kit_text_is_ascii_without_dashes(self):
        for root, _dirs, files in os.walk(AI_DIR):
            for name in files:
                if name.endswith(".md") and "tests" not in root:
                    with open(os.path.join(root, name), encoding="utf-8") as handle:
                        text = handle.read()
                    text.encode("ascii")
                    self.assertNotIn(chr(0x2014), text)


class CopyTest(unittest.TestCase):
    def test_banned_copy_fails(self):
        result = brand_rules.call("check_copy", {"text": "Guaranteed meetings with 50+ investors!"})
        self.assertFalse(result["ok"])
        rules = " ".join(p["rule"] for p in result["problems"])
        self.assertIn("guarantee", rules)
        self.assertIn("exclamation", rules)

    def test_long_copy_says_it_was_cut(self):
        cut = "a" * brand_rules.MAX_TEXT + "..."
        result = brand_rules.call("check_copy", {"text": cut})
        self.assertTrue(result["truncated"])
        self.assertIn("first", result["note"])
        self.assertFalse(brand_rules.call("check_copy", {"text": "Get your Climb27 ticket"})["truncated"])

    def test_good_copy_passes(self):
        self.assertTrue(brand_rules.call("check_copy", {"text": "Get your Climb27 ticket"})["ok"])

    def test_venue_embargo_follows_the_platform_flag_only(self):
        text = "See you at the venue"
        self.assertFalse(brand_rules.call("check_copy", {"text": text, "announced": True})["ok"])
        self.assertTrue(brand_rules.call("check_copy", {"text": text}, venue_announced=True)["ok"])


class ColourTest(unittest.TestCase):
    def test_white_on_orange_is_large_only(self):
        normal = brand_rules.call("check_colours", {"foreground": "#FFFFFF", "background": "Climb Orange"})
        large = brand_rules.call("check_colours", {"foreground": "white", "background": "#E8712A", "size": "large"})
        self.assertFalse(normal["passes_aa"])
        self.assertTrue(large["passes_aa"])
        self.assertEqual(normal["preset_for_this_ground"]["name"], "Climb Orange")

    def test_retired_orange_is_called_out(self):
        result = brand_rules.call("check_colours", {"foreground": "#EC752A", "background": "#1E0F05"})
        self.assertTrue(any("retired" in note for note in result["notes"]))
        self.assertEqual(result["foreground_tokens"], [])

    def test_bad_input_is_a_message_not_an_error(self):
        self.assertFalse(brand_rules.call("check_colours", {"foreground": "blue-ish"})["ok"])

    def test_palette_has_five_presets_and_aaa_themes(self):
        result = brand_rules.call("palette", {})
        self.assertEqual(len(result["presets"]), 5)
        self.assertIn("aaa-dark", result["themes"])
        self.assertIn("aaa-light", result["themes"])

    def test_tokens_resolve_aliases(self):
        rows = brand_rules.call("tokens", {"group": "color.link"})["tokens"]
        self.assertTrue(rows)
        self.assertTrue(all(row["value"].startswith("#") for row in rows))


class LogoTest(unittest.TestCase):
    def test_variants_by_ground_and_size(self):
        cases = [
            ({"brand": "ClimbUK", "ground": "dark"}, "reversed-dark"),
            ({"brand": "ClimbUK", "ground": "white"}, "full-colour-light"),
            ({"brand": "ClimbUK", "ground": "light grey"}, "full-colour-grey"),
            ({"brand": "ClimbUK", "ground": "orange"}, "mono-white"),
            ({"brand": "Climb27", "use": "favicon"}, "icon-monogram"),
            ({"brand": "ClimbGroup", "use": "LinkedIn avatar"}, "icon"),
            ({"brand": "ClimbUK", "ground": "dark", "width_px": 90}, "icon"),
            ({"brand": "ClimbUK", "ground": "white", "tagline": True, "width_px": 200}, "full-colour-light"),
        ]
        for args, variant in cases:
            self.assertEqual(brand_rules.call("logo", args)["variant"], variant, args)

    def test_logo_files_exist_in_the_pack(self):
        result = brand_rules.call("logo", {"brand": "Climb27", "ground": "dark"})
        self.assertTrue(os.path.exists(brand_rules.pack_path(result["files"]["vector"])))
        self.assertTrue(result["about"])

    def test_unknown_brand(self):
        self.assertFalse(brand_rules.call("logo", {"brand": "Climb"})["ok"])


class LookupTest(unittest.TestCase):
    def test_surface(self):
        rows = brand_rules.call("surface", {"surface": "LinkedIn post"})["surfaces"]
        self.assertEqual(rows[0]["Size"], "1200x1200 or 1080x1350")

    def test_audience_and_channel(self):
        self.assertIn("Investors", brand_rules.call("audience", {"audience": "investors"})["audiences"][0]["Audience"])
        self.assertIn("LinkedIn", brand_rules.call("channel", {"channel": "linkedin"})["channels"][0]["Channel"])

    def test_guide_finds_a_section(self):
        result = brand_rules.call("guide", {"topic": "ticket pages"})
        self.assertTrue(result["ok"])
        self.assertEqual(result["sections"][0]["section"], "Ticket pages")

    def test_unknown_tool(self):
        self.assertFalse(brand_rules.call("nope", {})["ok"])


if __name__ == "__main__":
    unittest.main()
