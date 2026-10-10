"""Makes the outline fonts: Montserrat ExtraBold, upright and italic, with overlapping contours merged.

Montserrat's glyphs are drawn from overlapping shapes. Filled, that is invisible; drawn as an outline
(no fill, an orange stroke) every overlap shows as a stray line inside the figure. This writes
copies with the overlaps removed, which the book uses for outline numerals and outline marquees.
Needs fontTools, skia-pathops and brotli. Output: fonts/montserrat-800-outline[-italic].woff2
"""
import os

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.ttLib.removeOverlaps import removeOverlaps

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "..")
TEXT = "".join(chr(c) for c in range(0x20, 0x7F))
JOBS = [("fonts/montserrat-latin-800-normal.woff2", "montserrat-800-outline.woff2"),
        ("generators/fonts/montserrat-latin-800-italic.woff2", "montserrat-800-outline-italic.woff2")]

for src, out in JOBS:
    font = TTFont(os.path.join(FONTS, src))
    opts = subset.Options()
    opts.layout_features = ["kern", "tnum", "lnum"]
    sub = subset.Subsetter(opts)
    sub.populate(text=TEXT)
    sub.subset(font)
    removeOverlaps(font)
    for rec in font["name"].names:
        if rec.nameID in (1, 16):
            rec.string = "Montserrat Outline"
    font.flavor = "woff2"
    path = os.path.join(HERE, "fonts", out)
    font.save(path)
    print(path)
