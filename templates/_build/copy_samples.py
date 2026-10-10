"""Sample slides for the PowerPoint templates, in the ClimbUK voice (checked with climb-voice check_copy.py).

Rich text: {word} is Climb Orange, _word_ is italic. A new line starts a new paragraph.
"""
import re
from xml.sax.saxutils import escape

from PIL import Image

import brand as B

COPY = {
    "ClimbUK": dict(
        eyebrow="ClimbUK",
        title="Not a conference. A {festival} for _business_ growth.",
        sub="Two days of main stage moments, roundtables and the people who move businesses forward.",
        date="climb-uk.com",
        end="See you {there}",
        end_line="The Festival for Business Growth",
    ),
    "ClimbGroup": dict(
        eyebrow="ClimbGroup",
        title="We build the {stage} for _UK_ growth.",
        sub="Festivals, programmes and the communities that keep growing between them.",
        date="Company presentation",
        end="Thank {you}",
        end_line="marketing@climb-group.com",
    ),
    "Climb27": dict(
        eyebrow="Climb27",
        title="Your business. _Bigger_ {stage}.",
        sub="The Festival for Business Growth.",
        date="30 June and 1 July 2027",
        end="See you at {Climb27}",
        end_line="30 June and 1 July 2027",
    ),
}


def runs(text, base_colour=None, orange=B.ORANGE, sz=None):
    out = []
    for tok in re.split(r"(\{[^}]+\}|_[^_]+_)", text):
        if not tok:
            continue
        colour, ital = base_colour, None
        if tok.startswith("{"):
            tok, colour = tok[1:-1], orange
        elif tok.startswith("_") and tok.endswith("_") and len(tok) > 2:
            tok, ital = tok[1:-1], 1
        attrs = ' lang="en-GB"' + (' i="1"' if ital else "") + (' sz="%d"' % (sz * 100) if sz else "")
        fill = '<a:solidFill><a:srgbClr val="%s"/></a:solidFill>' % colour if colour else ""
        out.append('<a:r><a:rPr%s dirty="0">%s</a:rPr><a:t>%s</a:t></a:r>' % (attrs, fill, escape(tok)))
    return "".join(out)


def paras(text, **kw):
    lines = text if isinstance(text, list) else text.split("\n")
    return "".join('<a:p>%s</a:p>' % runs(l, **kw) for l in lines)


def _layout_ph(t, typ, idx):
    ph = t.layout.phs.get((typ, idx))
    if ph is None:
        raise KeyError("layout has no placeholder %s %s" % (typ, idx))
    return ph


def sph(t, typ, idx, text, **kw):
    """A slide placeholder linked to its layout. Position and text styles are repeated on the slide so apps that only
    partly read layouts (LibreOffice, Google Slides, Keynote) still show the sample as designed."""
    ph = _layout_ph(t, typ, idx)
    ty = ' type="%s"' % typ if typ else ""
    ix = ' idx="%d"' % idx if idx is not None else ""
    t.items.append('<p:sp><p:nvSpPr><p:cNvPr id="%d" name="%s %s"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
                   '<p:nvPr><p:ph%s%s/></p:nvPr></p:nvSpPr><p:spPr>%s</p:spPr><p:txBody>%s<a:lstStyle>%s</a:lstStyle>%s'
                   '</p:txBody></p:sp>'
                   % (t.nid(), typ or "body", idx, ty, ix, ph["sppr"], ph["bodypr"], ph["lst"], paras(text, **kw)))


def sphoto(t, idx, photo, box, descr):
    """Fill a picture placeholder, cropping the photo to the box (x, y, w, h in inches)."""
    path = B.photo(photo)
    iw, ih = Image.open(path).size
    _, _, bw, bh = box
    ia, ba = iw / ih, bw / bh
    if ia > ba:
        cut = (1 - ba / ia) / 2
        src = '<a:srcRect l="%d" r="%d"/>' % (cut * 100000, cut * 100000)
    else:
        cut = (1 - ia / ba) / 2
        src = '<a:srcRect t="%d" b="%d"/>' % (cut * 100000, cut * 100000)
    rid = t.media(path)
    ph = _layout_ph(t, "pic", idx)
    t.items.append('<p:pic><p:nvPicPr><p:cNvPr id="%d" name="Photo %d" descr="%s"/><p:cNvPicPr><a:picLocks noGrp="1" '
                   'noChangeAspect="1"/></p:cNvPicPr><p:nvPr><p:ph type="pic" idx="%d"/></p:nvPr></p:nvPicPr><p:blipFill>'
                   '<a:blip r:embed="%s"/>%s<a:stretch><a:fillRect/></a:stretch></p:blipFill><p:spPr>%s</p:spPr></p:pic>'
                   % (t.nid(), idx, escape(descr), idx, rid, src, ph["sppr"]))


W, H = 13.333, 7.5


def slides(b):
    c = COPY[b]
    S = []

    def s(layout):
        def deco(fn):
            S.append((layout, fn))
            return fn
        return deco

    @s("Title")
    def _(t, spec):
        sph(t, "body", 13, c["eyebrow"])
        sph(t, "ctrTitle", None, c["title"])
        sph(t, "subTitle", 1, c["sub"])
        sph(t, "body", 14, c["date"])

    @s("Title with photo")
    def _(t, spec):
        sphoto(t, 15, "crowd_wide", (6.2, 0, W - 6.2, H), "A packed festival crowd watching the main stage")
        sph(t, "body", 13, "Find your people")
        sph(t, "title", None, "The room where {deals} _start_.")
        sph(t, "body", 1, "Founders, investors and partners in one place, with the time to talk properly.")
        sph(t, "body", 30, "Main stage")

    @s("Section (orange)")
    def _(t, spec):
        sph(t, "body", 13, "01")
        sph(t, "title", None, "Why it _works_")
        sph(t, "body", 1, "The stage, the room and the follow-ups.")

    @s("Title and content")
    def _(t, spec):
        sph(t, "body", 13, "The day")
        sph(t, "title", None, "What happens on the {day}")
        sph(t, None, 1, ["Main stage moments from founders who have done it",
                         "Roundtables where you bring the problem and leave with a plan",
                         "Speed networking with investors looking for real deal flow",
                         "An after party that keeps the conversation going"])

    @s("Two columns (light)")
    def _(t, spec):
        sph(t, "body", 13, "Who it is for")
        sph(t, "title", None, "Two ways to get {more} from it")
        sph(t, "body", 16, "For founders")
        sph(t, "body", 17, "For partners")
        sph(t, None, 1, ["Learn from people a few steps ahead", "Find investors looking for real deal flow",
                         "Leave with follow-ups that matter"])
        sph(t, None, 2, ["Put your brand in front of the people you want to reach",
                         "Host a roundtable on the problem you solve", "Meet the room, not just the stand"])

    @s("Big statement")
    def _(t, spec):
        sph(t, "title", None, "Business {growth} with a _party_.")
        sph(t, "body", 1, "Real conversations, real stage light, real follow-ups.")

    @s("Big numbers")
    def _(t, spec):
        sph(t, "body", 13, "At a glance")
        sph(t, "title", None, "The festival in {numbers}")
        sph(t, "body", 20, "2")
        sph(t, "body", 23, "days of main stage moments, roundtables and the after party")
        sph(t, "body", 21, "00")
        sph(t, "body", 24, "Your number here, with its source in the speaker notes")
        sph(t, "body", 22, "00")
        sph(t, "body", 25, "One fact per number, never a guess")

    @s("Quote")
    def _(t, spec):
        sph(t, "body", 1, "Put the quote here, word for word, exactly as it was said.")
        sph(t, "title", None, "First name Last name")
        sph(t, "body", 13, "Role, Company")

    @s("Full photo")
    def _(t, spec):
        sphoto(t, 15, "band_stage", (0, 0, W, H - 1.55), "The band playing on the main stage under orange light")
        sph(t, "body", 30, "Climb26")
        sph(t, "title", None, "The band opens the {main stage}")
        sph(t, "body", 1, "Climb26, the opening of day one")

    @s("Photo wall")
    def _(t, spec):
        sphoto(t, 15, "awards_winners", (5.0, 0, 5.0, H), "ClimbAwards winners celebrating on stage")
        sphoto(t, 16, "drinks_reception", (10.08, 0, W - 10.08, H / 2), "Drinks being served at the evening reception")
        sphoto(t, 17, "expo_floor", (10.08, H / 2, W - 10.08, H / 2), "People talking at stands on the expo floor")
        sph(t, "body", 13, "Climb26")
        sph(t, "title", None, "Moments worth {coming} back for")
        sph(t, "body", 1, "The ClimbAwards walk-up, the reception and the busiest expo floor of the year.")

    @s("Speaker")
    def _(t, spec):
        sph(t, "body", 13, "Speaker")
        sph(t, "title", None, "First name\nLast name")
        sph(t, "body", 18, "Role, _Company_")
        sph(t, "body", 1, "Session title, main stage, 11:00")

    @s("Agenda (light)")
    def _(t, spec):
        sph(t, "body", 13, "Agenda")
        sph(t, "title", None, "How the day {runs}")
        sph(t, "body", 19, ["09:00", "09:30", "11:00", "13:00", "15:00", "18:00"])
        sph(t, "body", 1, ["Doors open, coffee and badges", "Opening on the main stage", "Roundtables and workshops",
                           "Lunch on the expo floor", "Investor speed networking", "ClimbAwards and the after party"])

    @s("Title and content (light)")
    def _(t, spec):
        sph(t, "body", 13, "Before you start")
        sph(t, "title", None, "Using this {template}")
        sph(t, None, 1, ["Install Montserrat and Open Sans from the fonts folder first",
                         "Pick a layout from Home, Layout: dark first, light for reading-heavy slides",
                         "One orange word and one italic word per headline, one orange button per slide",
                         "Use real photos with consent, never stock handshakes",
                         "Keep text at 18pt or larger and give every slide a title, so screen readers can find it"])

    @s("End card")
    def _(t, spec):
        sph(t, "title", None, c["end"])
        sph(t, "body", 13, c["end_line"])
        sph(t, "body", 14, B.BRANDS[b]["url"])

    return S
