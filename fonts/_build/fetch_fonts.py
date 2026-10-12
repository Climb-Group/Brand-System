"""Fetches the desktop fonts: Montserrat and Open Sans as static TTF and OTF, every style the brand uses.

Web pages use the WOFF2 files in fonts/, but design apps, office suites and brand centres that take
uploaded fonts only accept TTF or OTF. This downloads the official builds from each family's own
repository, pinned to a commit so a re-run gives the same files:

  Montserrat  github.com/JulietaUla/Montserrat  fonts/ttf and fonts/otf (both published upstream)
  Open Sans   github.com/googlefonts/opensans   fonts/ttf (upstream publishes TTF only)

Open Sans has no official OTF, so its OTF files are made here from the official TTF: the TrueType
outlines are redrawn as CFF outlines (every quadratic curve has an exact cubic equal) and the names,
metrics and layout tables are kept. Needs fontTools.

Output: fonts/ttf/<Family>-<Style>.ttf and fonts/otf/<Family>-<Style>.otf
Run:    python3 fonts/_build/fetch_fonts.py
"""
import io
import os
import sys
import urllib.request

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.ttLib import TTFont, newTable

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.dirname(HERE)

MONTSERRAT = "https://raw.githubusercontent.com/JulietaUla/Montserrat/555facfb2a18c72c3c0380f0d9c0f060453a9058/fonts/"
OPEN_SANS = "https://raw.githubusercontent.com/googlefonts/opensans/bd7e37632246368c60fdcbd374dbf9bad11969b6/fonts/ttf/"

# Every style the templates, web fonts and generators use.
MONTSERRAT_STYLES = ["Regular", "Italic", "Medium", "MediumItalic", "SemiBold", "SemiBoldItalic", "Bold",
                     "BoldItalic", "ExtraBold", "ExtraBoldItalic", "Black", "BlackItalic"]
OPEN_SANS_STYLES = ["Regular", "Italic", "SemiBold", "SemiBoldItalic", "Bold", "BoldItalic"]


def download(url):
    with urllib.request.urlopen(url, timeout=60) as resp:
        return resp.read()


def ttf_to_otf(ttf):
    """Returns an OTF (CFF outlines) with the same glyphs, names, metrics and layout as the TTF."""
    font = TTFont(io.BytesIO(ttf), recalcTimestamp=False)
    order = font.getGlyphOrder()
    glyphs = font.getGlyphSet()
    hmtx = font["hmtx"]
    charstrings = {}
    for name in order:
        pen = T2CharStringPen(hmtx[name][0], glyphs)
        glyphs[name].draw(pen)
        charstrings[name] = pen.getCharString()

    names = font["name"]
    family = names.getDebugName(1)
    style = names.getDebugName(2)
    ps_name = names.getDebugName(6)
    full = names.getDebugName(4)
    fb = FontBuilder(font["head"].unitsPerEm, isTTF=False)
    fb.font = font
    for tag in ("glyf", "loca", "fpgm", "prep", "cvt ", "gasp", "hdmx", "LTSH", "VDMX", "DSIG"):
        if tag in font:
            del font[tag]
    fb.setupCFF(ps_name, {"FullName": full, "FamilyName": family, "Weight": style,
                          "version": "%.3f" % font["head"].fontRevision,
                          "Notice": names.getDebugName(0) or ""},
                charstrings, {})
    # CFF fonts carry the short (version 0.5) maxp table.
    font["maxp"] = newTable("maxp")
    font["maxp"].tableVersion = 0x00005000
    font["maxp"].numGlyphs = len(order)
    font.sfntVersion = "OTTO"
    out = io.BytesIO()
    font.save(out)
    return out.getvalue()


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(data)
    print(os.path.relpath(path, FONTS))


def main():
    for style in MONTSERRAT_STYLES:
        for fmt in ("ttf", "otf"):
            name = "Montserrat-%s.%s" % (style, fmt)
            write(os.path.join(FONTS, fmt, name), download(MONTSERRAT + fmt + "/" + name))
    for style in OPEN_SANS_STYLES:
        name = "OpenSans-%s" % style
        ttf = download(OPEN_SANS + name + ".ttf")
        write(os.path.join(FONTS, "ttf", name + ".ttf"), ttf)
        write(os.path.join(FONTS, "otf", name + ".otf"), ttf_to_otf(ttf))
    return 0


if __name__ == "__main__":
    sys.exit(main())
