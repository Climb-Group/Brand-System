"""Set a line of text as one SVG path (outlines), with GPOS pair kerning. Avoids a harfbuzz dependency."""
import os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Montserrat-Bold.ttf")


def _kern_table(font):
    """{(left, right): x_advance_adjust} from the GPOS 'kern' feature (PairPos formats 1 and 2)."""
    pairs, classed = {}, []
    gpos = font["GPOS"].table
    idx = {i for fr in gpos.FeatureList.FeatureRecord if fr.FeatureTag == "kern" for i in fr.Feature.LookupListIndex}
    for i in sorted(idx):
        lookup = gpos.LookupList.Lookup[i]
        for st in lookup.SubTable:
            if lookup.LookupType == 9:
                st = st.ExtSubTable
            if getattr(st, "LookupType", 2) != 2 and lookup.LookupType not in (2, 9):
                continue
            cov = st.Coverage.glyphs
            if st.Format == 1:
                for g, ps in zip(cov, st.PairSet):
                    for r in ps.PairValueRecord:
                        v = getattr(r.Value1, "XAdvance", 0) or 0
                        pairs.setdefault((g, r.SecondGlyph), v)
            elif st.Format == 2:
                classed.append((set(cov), st.ClassDef1.classDefs, st.ClassDef2.classDefs, st.Class1Record))
    return pairs, classed


def _kern(pairs, classed, a, b):
    if (a, b) in pairs:
        return pairs[(a, b)]
    for cov, c1, c2, recs in classed:
        if a in cov:
            v = recs[c1.get(a, 0)].Class2Record[c2.get(b, 0)].Value1
            return getattr(v, "XAdvance", 0) or 0
    return 0


def text_path(text, font_path=FONT):
    """Return (d, width, ascent_of_caps) in font units, baseline at y=0, y down."""
    font = TTFont(font_path)
    cmap, gs, hmtx = font.getBestCmap(), font.getGlyphSet(), font["hmtx"]
    pairs, classed = _kern_table(font)
    pen = SVGPathPen(gs)
    x, prev = 0, None
    for ch in text:
        g = cmap[ord(ch)]
        if prev:
            x += _kern(pairs, classed, prev, g)
        gs[g].draw(TransformPen(pen, (1, 0, 0, -1, x, 0)))
        x += hmtx[g][0]
        prev = g
    return pen.getCommands(), x, font["OS/2"].sCapHeight
