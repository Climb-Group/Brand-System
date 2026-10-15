"""The layouts each PowerPoint deck after the presentation template carries, and the org chart drawing.

The example slides and every word on them live in the deck's copy file, one per brand:
office/<Brand>/powerpoint/<Brand>_<Name>.copy.md (or office/<Brand>/external/ for a co-branded version), read by
copy_samples.slides. DECKS is keyed by (catalogue name, external?) and holds:
    layouts   the layouts the deck carries, in order (None: all 19 of the presentation template, plus extra)
    extra     extra layouts from pptx_build.EXTRA

In a copy file [[word]] is Climb Orange and *word* is italic. Every number is a slot; every name is a slot.
"""
from xml.sax.saxutils import escape

import brand as B


# ---------- shapes for the org chart ----------

def org_box(t, x, y, w, h, name, role, top=False):
    fill = B.CHARCOAL if top else B.GREY
    colour, sub = (B.WHITE, B.TINT) if top else (B.CHARCOAL, B.SLATE_GREY)
    body = ('<p:txBody><a:bodyPr anchor="ctr" lIns="91440" rIns="91440"><a:normAutofit/></a:bodyPr><a:lstStyle/>'
            '<a:p><a:pPr algn="ctr"/><a:r><a:rPr lang="en-GB" sz="1400" b="1"><a:solidFill><a:srgbClr val="%s"/></a:solidFill>'
            '<a:latin typeface="%s"/></a:rPr><a:t>%s</a:t></a:r></a:p>'
            '<a:p><a:pPr algn="ctr"/><a:r><a:rPr lang="en-GB" sz="1200"><a:solidFill><a:srgbClr val="%s"/></a:solidFill>'
            '<a:latin typeface="%s"/></a:rPr><a:t>%s</a:t></a:r></a:p></p:txBody>'
            % (colour, B.DISPLAY, escape(name), sub, B.BODY, escape(role)))
    t.shape(x, y, w, h, '<a:solidFill><a:srgbClr val="%s"/></a:solidFill>' % fill, geom="roundRect",
            adj='<a:gd name="adj" fmla="val 12000"/>', name="Org box: %s" % name, text=body)


def org_line(t, x, y, w, h):
    t.shape(x, y, w, h, '<a:solidFill><a:srgbClr val="%s"/></a:solidFill>' % B.SLATE, name="Org line")


def org_chart(t, sections):
    """The org chart boxes: the top box, a box per head and a team box under each, from the slide's org- sections."""
    top = [s for s in sections if s.path.endswith(".org-top")][0]
    heads = [s for s in sections if s.path.endswith(".org-head")]
    team = [s for s in sections if s.path.endswith(".org-team")][0]
    bw, bh = 2.6, 0.95
    cx = 13.333 / 2
    org_box(t, cx - bw / 2, 2.35, bw, bh, top.title, top.text, top=True)
    org_line(t, cx - 0.02, 3.3, 0.04, 0.4)
    xs = [1.4, 4.3, 7.2, 10.1]
    org_line(t, xs[0] + bw / 2, 3.7, xs[-1] - xs[0], 0.04)
    for k, x in enumerate(xs):
        org_line(t, x + bw / 2 - 0.02, 3.7, 0.04, 0.35)
        org_box(t, x, 4.05, bw, bh, heads[k].title, heads[k].text)
        org_line(t, x + bw / 2 - 0.02, 5.0, 0.04, 0.3)
        org_box(t, x, 5.3, bw, bh, team.title, team.text)


EXTERNAL_LAYOUTS = ["Co-branded title", "Agenda (light)", "Title and content", "Title and content (light)",
                    "Two columns (light)", "Section (orange)", "Big statement", "Big numbers", "Quote", "Full photo",
                    "Holding", "Up next", "Co-branded end"]
EXTERNAL_EXTRA = ("Holding", "Up next", "Co-branded title", "Co-branded end")

DECKS = {
    ("Investor-pitch-deck", False): dict(),
    ("Sales-deck", False): dict(),
    ("Quarterly-business-review", False): dict(),
    ("Board-presentation", False): dict(),
    ("Project-kick-off", False): dict(),
    ("Training-deck", False): dict(),
    ("All-hands", False): dict(),
    ("Org-chart", False): dict(),
    ("Partner-prospectus", False): dict(),
    ("Stage-holding-slides", False): dict(extra=("Holding", "Up next", "Logo grid (light)")),
    ("Speaker-slides", False): dict(),
    ("Investor-pitch-deck", True): dict(layouts=EXTERNAL_LAYOUTS, extra=EXTERNAL_EXTRA),
    ("Stage-holding-slides", True): dict(layouts=EXTERNAL_LAYOUTS, extra=EXTERNAL_EXTRA),
    ("Speaker-slides", True): dict(layouts=EXTERNAL_LAYOUTS, extra=EXTERNAL_EXTRA),
}

# Special fills a slide marker can name (fill=org-chart): drawn after the slide's placeholders.
FILLS = {"org-chart": org_chart}
