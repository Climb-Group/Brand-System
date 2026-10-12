"""The desktop fonts: every brand style ships as TTF and OTF, with the right outlines and names.

Reads the font files with the standard library only, so it runs without fontTools.
"""
import os
import re
import struct
import unittest

FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
STYLES = {
    "Montserrat": ["Regular", "Italic", "Medium", "MediumItalic", "SemiBold", "SemiBoldItalic", "Bold",
                   "BoldItalic", "ExtraBold", "ExtraBoldItalic", "Black", "BlackItalic"],
    "OpenSans": ["Regular", "Italic", "SemiBold", "SemiBoldItalic", "Bold", "BoldItalic"],
}
FAMILY = {"Montserrat": "Montserrat", "OpenSans": "Open Sans"}


def tables(path):
    with open(path, "rb") as fh:
        data = fh.read()
    version, count = struct.unpack(">4sH", data[:6])
    found = {}
    for i in range(count):
        tag, _, offset, length = struct.unpack(">4sIII", data[12 + 16 * i:28 + 16 * i])
        found[tag.decode("latin-1")] = data[offset:offset + length]
    return version, found


def full_name(name_table):
    _, count, strings = struct.unpack(">HHH", name_table[:6])
    for i in range(count):
        platform, encoding, _, name_id, length, offset = struct.unpack(">6H", name_table[6 + 12 * i:18 + 12 * i])
        if name_id == 4 and platform == 3 and encoding == 1:
            return name_table[strings + offset:strings + offset + length].decode("utf-16-be")
    return None


def expected_full_name(family, style):
    words = re.sub(r"(?<=.)Italic$", " Italic", style)
    if style == "Regular":
        return {FAMILY[family], FAMILY[family] + " Regular"}
    return {FAMILY[family] + " " + words}


class DesktopFonts(unittest.TestCase):
    def test_every_style_ships_as_ttf_and_otf(self):
        for family, styles in STYLES.items():
            for style in styles:
                for fmt in ("ttf", "otf"):
                    path = os.path.join(FONTS, fmt, "%s-%s.%s" % (family, style, fmt))
                    self.assertTrue(os.path.isfile(path), path)

    def test_outlines_match_the_format(self):
        for family, styles in STYLES.items():
            for style in styles:
                version, found = tables(os.path.join(FONTS, "ttf", "%s-%s.ttf" % (family, style)))
                self.assertEqual(version, b"\x00\x01\x00\x00")
                self.assertIn("glyf", found)
                version, found = tables(os.path.join(FONTS, "otf", "%s-%s.otf" % (family, style)))
                self.assertEqual(version, b"OTTO")
                self.assertIn("CFF ", found)
                self.assertNotIn("glyf", found)

    def test_names_are_the_official_family_and_style(self):
        for family, styles in STYLES.items():
            for style in styles:
                for fmt in ("ttf", "otf"):
                    _, found = tables(os.path.join(FONTS, fmt, "%s-%s.%s" % (family, style, fmt)))
                    self.assertIn(full_name(found["name"]), expected_full_name(family, style), (family, style, fmt))

    def test_every_web_font_has_a_desktop_style(self):
        weights = {"400": "Regular", "500": "Medium", "600": "SemiBold", "700": "Bold", "800": "ExtraBold", "900": "Black"}
        for name in os.listdir(FONTS):
            m = re.match(r"(montserrat|open-sans)-latin-(\d00)-(normal|italic)\.woff2$", name)
            if not m:
                continue
            family = "Montserrat" if m.group(1) == "montserrat" else "OpenSans"
            style = weights[m.group(2)] + ("Italic" if m.group(3) == "italic" else "")
            self.assertIn(style, STYLES[family], name)


if __name__ == "__main__":
    unittest.main()
