"""Build the 16:9 PowerPoint templates (.potx) for each brand from raw OOXML: the presentation template (19 layouts, 14
example slides from copy_samples.py) and every deck in catalog.py (the same master, the layouts each deck needs, and
its example slides from deck_samples.py).

Dark first: the master is Dark Brown with White text; the Light layouts override the colour map for reading-heavy
slides. Every layout has a title placeholder (screen readers announce it), logos carry alt text, and backgrounds and
motifs are background fills or shapes marked decorative.

python3 pptx_build.py [Brand ...]              build every template for the brands given (default: all)
python3 pptx_build.py --only Sales-deck ...   build only the named templates
python3 pptx_build.py --copy                  print every string a reader sees, for check_copy.py
"""
import os
import sys
import zipfile
from xml.sax.saxutils import escape

from PIL import Image

import brand as B
import catalog as K
import copy_io as CI
import copy_samples as C
import deck_samples as D
import ooxml_theme as T

EMU = 914400
W, H = 13.333, 7.5
SW, SH = 12192000, 6858000
M = 0.75
ART = os.path.join(B.OUT, "_art")
LAYOUT_COPY = "office/powerpoint-layouts.copy.md"


def P(key):
    """A placeholder prompt or a shared line from office/powerpoint-layouts.copy.md."""
    return CI.load(LAYOUT_COPY).one(key).text


def host_line(b):
    """The host line on the co-branded layouts: Speaking at Climb27, or at a ClimbGroup event."""
    event = P("cobrand.event-group") if b == "ClimbGroup" else b
    return CI.fill(P("cobrand.host"), verb=P("cobrand.verb-speaking"), event=event)

NS = ('xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
      'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"')
DECOR = ('<a:extLst><a:ext uri="{C183D7F6-B498-43B3-948B-1728B52AA6E4}">'
         '<adec:decorative xmlns:adec="http://schemas.microsoft.com/office/drawing/2017/decorative" val="1"/></a:ext></a:extLst>')
XML = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'


def e(v):
    return int(round(v * EMU))


def xfrm(x, y, w, h, rot=0):
    r = ' rot="%d"' % int(rot * 60000) if rot else ""
    return '<a:xfrm%s><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>' % (r, e(x), e(y), e(w), e(h))


def solid(hexv=None, scheme=None, alpha=None):
    a = '<a:alpha val="%d"/>' % int(alpha * 1000) if alpha is not None else ""
    if scheme:
        return '<a:solidFill><a:schemeClr val="%s">%s</a:schemeClr></a:solidFill>' % (scheme, a)
    return '<a:solidFill><a:srgbClr val="%s">%s</a:srgbClr></a:solidFill>' % (hexv, a)


def rpr(sz=None, b=None, i=None, cap=None, spc=None, font=None, colour=None, scheme=None, tag="a:defRPr", extra=""):
    attrs = ' lang="en-GB"' if tag == "a:rPr" else ""
    if sz:
        attrs += ' sz="%d"' % int(sz * 100)
    if b is not None:
        attrs += ' b="%d"' % b
    if i is not None:
        attrs += ' i="%d"' % i
    if cap:
        attrs += ' cap="%s"' % cap
    if spc is not None:
        attrs += ' spc="%d"' % spc
    inner = ""
    if colour or scheme:
        inner += solid(colour, scheme)
    if font:
        inner += '<a:latin typeface="%s"/>' % font
    return "<%s%s>%s%s</%s>" % (tag, attrs, inner, extra, tag)


def lvl(n=1, sz=20, font=None, b=None, i=None, cap=None, spc=None, colour=None, scheme=None, algn="l", ln=None,
        bullet=None, marL=0, indent=0, before=0, after=0):
    lnspc = '<a:lnSpc><a:spcPct val="%d"/></a:lnSpc>' % int(ln * 1000) if ln else ""
    sp = '<a:spcBef><a:spcPts val="%d"/></a:spcBef><a:spcAft><a:spcPts val="%d"/></a:spcAft>' % (before * 100, after * 100)
    if bullet:
        bu = '<a:buClr><a:srgbClr val="%s"/></a:buClr><a:buFont typeface="Arial"/><a:buChar char="%s"/>' % bullet
    else:
        bu = "<a:buNone/>"
    return ('<a:lvl%dpPr marL="%d" indent="%d" algn="%s">%s%s%s%s</a:lvl%dpPr>'
            % (n, e(marL), e(indent), algn, lnspc, sp, bu,
               rpr(sz, b, i, cap, spc, font, colour, scheme), n))


def body_pr(anchor="t", ins=(0, 0, 0, 0), autofit="none", wrap=True):
    fit = {"norm": "<a:normAutofit/>", "shape": "<a:spAutoFit/>", "none": "<a:noAutofit/>"}[autofit]
    return ('<a:bodyPr vert="horz" wrap="%s" lIns="%d" tIns="%d" rIns="%d" bIns="%d" anchor="%s" rtlCol="0">%s</a:bodyPr>'
            % ("square" if wrap else "none", e(ins[0]), e(ins[1]), e(ins[2]), e(ins[3]), anchor, fit))


class Tree:
    """Collects shapes for one spTree with unique ids and picture relationships."""

    def __init__(self):
        self.n = 1
        self.items = []
        self.rels = []  # (rid, target)
        self.phs = {}  # (type, idx) -> spPr and text styles, so slides can repeat them for apps without layout support
        self.layout = None

    def nid(self):
        self.n += 1
        return self.n

    def media(self, target):
        rid = "rId%d" % (len(self.rels) + 2)
        self.rels.append((rid, target))
        return rid

    def ph(self, name, typ, idx, x, y, w, h, lst="", prompt=None, anchor="t", fill="", rot=0, geom="rect",
           autofit="none", ins=(0, 0, 0, 0), paras=None):
        t = ' type="%s"' % typ if typ else ""
        ix = ' idx="%d"' % idx if idx is not None else ""
        cp = ' hasCustomPrompt="1"' if prompt else ""
        self.phs[(typ, idx)] = dict(sppr='%s<a:prstGeom prst="%s"><a:avLst/></a:prstGeom>%s' % (xfrm(x, y, w, h, rot), geom, fill),
                                    bodypr=body_pr(anchor, ins, autofit), lst=lst)
        body = ""
        if typ != "pic" or prompt:
            if paras is not None:
                ps = paras
            elif prompt:
                ps = '<a:p><a:r><a:rPr lang="en-GB"/><a:t>%s</a:t></a:r></a:p>' % escape(prompt)
            else:
                ps = '<a:p><a:endParaRPr lang="en-GB"/></a:p>'
            body = '<p:txBody>%s<a:lstStyle>%s</a:lstStyle>%s</p:txBody>' % (body_pr(anchor, ins, autofit), lst, ps)
        self.items.append(
            '<p:sp><p:nvSpPr><p:cNvPr id="%d" name="%s"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
            '<p:nvPr><p:ph%s%s%s/></p:nvPr></p:nvSpPr><p:spPr>%s<a:prstGeom prst="%s"><a:avLst/></a:prstGeom>%s</p:spPr>%s</p:sp>'
            % (self.nid(), escape(name), t, ix, cp, xfrm(x, y, w, h, rot), geom, fill, body))

    def pic(self, path, x, y, w=None, h=None, descr="", decorative=False, name="Logo"):
        iw, ih = Image.open(path).size
        if w is None:
            w = h * iw / ih
        if h is None:
            h = w * ih / iw
        rid = self.media(path)
        dec = DECOR if decorative else ""
        self.items.append(
            '<p:pic><p:nvPicPr><p:cNvPr id="%d" name="%s" descr="%s">%s</p:cNvPr><p:cNvPicPr><a:picLocks noChangeAspect="1"/>'
            '</p:cNvPicPr><p:nvPr userDrawn="1"/></p:nvPicPr><p:blipFill><a:blip r:embed="%s"/><a:stretch><a:fillRect/></a:stretch>'
            '</p:blipFill><p:spPr>%s<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>'
            % (self.nid(), name, escape(descr), dec, rid, xfrm(x, y, w, h)))
        return w, h

    def shape(self, x, y, w, h, fill, geom="rect", rot=0, name="Decoration", adj="", text="", line=""):
        tx = text or '<p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr lang="en-GB"/></a:p></p:txBody>'
        self.items.append(
            '<p:sp><p:nvSpPr><p:cNvPr id="%d" name="%s">%s</p:cNvPr><p:cNvSpPr/><p:nvPr userDrawn="1"/></p:nvSpPr>'
            '<p:spPr>%s<a:prstGeom prst="%s"><a:avLst>%s</a:avLst></a:prstGeom>%s%s</p:spPr>%s</p:sp>'
            % (self.nid(), name, DECOR if not text else "", xfrm(x, y, w, h, rot), geom, adj, fill,
               line or "<a:ln><a:noFill/></a:ln>", tx))

    def gradient(self, x, y, w, h, stops, ang=0, name="Photo fade"):
        """A Dark Brown fade laid over a photo: stops are (pos 0..1, hex, alpha 0..100)."""
        gs = "".join('<a:gs pos="%d"><a:srgbClr val="%s"><a:alpha val="%d"/></a:srgbClr></a:gs>' % (p * 100000, c, a * 1000)
                     for p, c, a in stops)
        fill = '<a:gradFill rotWithShape="1"><a:gsLst>%s</a:gsLst><a:lin ang="%d" scaled="0"/></a:gradFill>' % (gs, ang * 60000)
        self.shape(x, y, w, h, fill, name=name)

    def xml(self):
        return ('<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr>'
                '<a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm>'
                '</p:grpSpPr>%s</p:spTree>' % "".join(self.items))


# Colour maps. Master is dark first; Light layouts flip it and point links at Orange Deep.
DARK_MAP = ('bg1="dk1" tx1="lt1" bg2="dk2" tx2="lt2" accent1="accent1" accent2="accent2" accent3="accent3" '
            'accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"')
LIGHT_MAP = ('bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" '
             'accent4="accent4" accent5="accent5" accent6="accent6" hlink="accent4" folHlink="accent4"')

# Text styles, reused by layouts.
EYEBROW_DARK = lvl(sz=14, font=B.BODY, b=1, cap="all", spc=300, colour=B.TINT)
EYEBROW_LIGHT = lvl(sz=14, font=B.BODY, b=1, cap="all", spc=300, colour=B.ORANGE_TEXT)
FOOT = lvl(sz=11, font=B.BODY, colour=B.GREY)
FOOT_LIGHT = lvl(sz=11, font=B.BODY, colour=B.SLATE)


def title_lst(sz, colour=None, font=B.DISPLAY_XB, algn="l", ln=95):
    return lvl(sz=sz, font=font, b=0, cap="all", spc=-50, colour=colour, algn=algn, ln=ln)


def body_lst(sz=20, colour=None, light=False):
    c = colour or (B.SLATE if light else B.WHITE)
    bul = B.ORANGE_TEXT if light else B.ORANGE
    return (lvl(1, sz=sz, font=B.BODY, colour=c, ln=125, bullet=(bul, "\u25A0"), marL=0.32, indent=-0.32, after=8) +
            lvl(2, sz=sz - 2, font=B.BODY, colour=c, ln=125, bullet=(bul, "\u2022"), marL=0.7, indent=-0.3, after=6) +
            lvl(3, sz=sz - 4, font=B.BODY, colour=c, ln=125, bullet=(bul, "-"), marL=1.05, indent=-0.28, after=4))


def plain_lst(sz, colour, font=B.BODY, b=None, i=None, algn="l", ln=120, cap=None, spc=None):
    return lvl(sz=sz, font=font, b=b, i=i, colour=colour, algn=algn, ln=ln, cap=cap, spc=spc)


def footer(t, b, light=False):
    lst = FOOT_LIGHT if light else FOOT
    t.ph("Slide Number", "sldNum", 12, M, 6.92, 0.6, 0.32, lst=lst, anchor="ctr",
         paras='<a:p><a:fld id="{B6F15528-21DE-4FAA-801E-634DDDAF4B2B}" type="slidenum"><a:rPr lang="en-GB"/><a:t>&lt;#&gt;</a:t></a:fld></a:p>')
    t.ph("Footer", "ftr", 11, M + 0.7, 6.92, 6.0, 0.32, lst=lst, anchor="ctr")
    lg = B.logo(b, "full-colour-light" if light else "reversed-dark", 512)
    iw, ih = Image.open(lg).size
    h = 0.26
    t.pic(lg, W - M - h * iw / ih, 6.95, h=h, descr=CI.fill(P("alt.logo"), brand=b))


def eyebrow(t, x, y, w, light=False, prompt=P("default.eyebrow"), idx=13):
    t.ph("Eyebrow", "body", idx, x, y, w, 0.4, lst=EYEBROW_LIGHT if light else EYEBROW_DARK, prompt=prompt, anchor="b",
         autofit="none")


def rule(t, x, y, w=0.9):
    t.shape(x, y, w, 0.07, solid(B.ORANGE), geom="roundRect", adj='<a:gd name="adj" fmla="val 50000"/>', name="Orange rule")


def sticker(t, x, y, w=2.1, prompt=P("default.sticker"), idx=30):
    """Tilted Climb Orange sticker with White bold label (large text rule: 14pt bold and up)."""
    t.ph("Sticker", "body", idx, x, y, w, 0.5, rot=-4, fill=solid(B.ORANGE),
         lst=lvl(sz=16, font=B.DISPLAY, b=1, cap="all", spc=100, colour=B.WHITE, algn="ctr"),
         prompt=prompt, anchor="ctr", autofit="none", ins=(0.12, 0.04, 0.12, 0.04))


def layouts(b, names=None, extra=()):
    """Each layout: (name, background art or None, light?, builder(tree)). names keeps only those layouts, in that
    order; extra appends layouts from EXTRA (holding slides, logo grids, co-branded title and end cards)."""
    info = B.BRANDS[b]
    L = []

    def add(name, bg, light, fn, typ="cust"):
        L.append(dict(name=name, bg=bg, light=light, fn=fn, typ=typ))

    def title(t):
        t.pic(B.logo(b, "reversed-dark", 1024), M, 0.6, h=0.5, descr=CI.fill(P("alt.logo"), brand=b))
        eyebrow(t, M, 1.3, 8.5, prompt=P("title.eyebrow"))
        t.ph("Title", "ctrTitle", None, M, 2.1, 11.2, 3.2, lst=title_lst(60, font=B.DISPLAY_BLACK, ln=92), anchor="b",
             prompt=P("title.title"))
        t.ph("Subtitle", "subTitle", 1, M, 5.42, 8.0, 0.85, lst=plain_lst(20, B.GREY), prompt=P("title.subtitle"))
        t.ph("Date line", "body", 14, M, 6.38, 8.0, 0.45, lst=plain_lst(16, B.TINT, b=1),
             prompt=info["edition"] or P("title.date-line"))
    add("Title", "slide_title", False, title, "title")

    def title_photo(t):
        t.ph("Photo", "pic", 15, 6.2, 0, W - 6.2, H, prompt=P("title-photo.photo"))
        t.pic(B.logo(b, "reversed-dark", 1024), M, 0.6, h=0.45, descr=CI.fill(P("alt.logo"), brand=b))
        eyebrow(t, M, 2.2, 5.0)
        t.ph("Title", "title", None, M, 2.65, 5.2, 2.7, lst=title_lst(48, font=B.DISPLAY_BLACK, ln=92), anchor="t",
             prompt=P("title-photo.title"))
        t.ph("Subtitle", "body", 1, M, 5.4, 5.0, 1.0, lst=plain_lst(18, B.GREY), prompt=P("title-photo.subtitle"))
        t.shape(0, H - 0.32, 3.4, 0.32, solid(B.ORANGE), geom="snip1Rect", rot=0, adj='<a:gd name="adj" fmla="val 100000"/>',
                name="Slab")
        sticker(t, 6.55, 0.55)
    add("Title with photo", "slide_dark", False, title_photo)

    def section(t):
        t.ph("Section number", "body", 13, M, 0.9, 5.0, 2.4, lst=lvl(sz=160, font=B.DISPLAY_BLACK, colour=B.WHITE, ln=85),
             prompt=P("section.section-number"), anchor="t", autofit="none")
        t.ph("Title", "title", None, M, 3.45, 8.2, 2.2, lst=title_lst(60, colour=B.WHITE, font=B.DISPLAY_BLACK, ln=92),
             prompt=P("section.title"), anchor="t")
        t.ph("Subtitle", "body", 1, M, 5.6, 7.5, 0.6, lst=plain_lst(20, B.WHITE, b=1), prompt=P("section.subtitle"))
    add("Section (orange)", "slide_section", False, section)

    def content(light):
        def f(t):
            eyebrow(t, M, 0.55, 10, light=light)
            rule(t, M, 1.05)
            t.ph("Title", "title", None, M, 1.2, W - 2 * M, 1.1, lst=title_lst(36, colour=B.CHARCOAL if light else None),
                 prompt=P("content.title"), anchor="t")
            t.ph("Content", None, 1, M, 2.45, W - 2 * M, 4.25, lst=body_lst(20, light=light),
                 paras=None, prompt=P("content.content"))
            footer(t, b, light)
        return f
    add("Title and content", "slide_dark", False, content(False), "obj")
    add("Title and content (light)", "slide_light", True, content(True), "obj")

    def two(light):
        def f(t):
            eyebrow(t, M, 0.55, 10, light=light)
            rule(t, M, 1.05)
            t.ph("Title", "title", None, M, 1.2, W - 2 * M, 1.0, lst=title_lst(36, colour=B.CHARCOAL if light else None),
                 prompt=P("two-columns.title"), anchor="t")
            cw = (W - 2 * M - 0.6) / 2
            for k, x in enumerate((M, M + cw + 0.6)):
                t.ph("Column heading %d" % (k + 1), "body", 16 + k, x, 2.4, cw, 0.5,
                     lst=plain_lst(20, B.ORANGE_TEXT if light else B.ORANGE, font=B.DISPLAY, b=1, cap="all"),
                     prompt=P("two-columns.column-heading"), autofit="none")
                t.ph("Column %d" % (k + 1), None, 1 + k * 1 if k == 0 else 2, x, 2.95, cw, 3.75, lst=body_lst(18, light=light),
                     prompt=P("two-columns.column"))
            footer(t, b, light)
        return f
    add("Two columns", "slide_dark", False, two(False), "twoObj")
    add("Two columns (light)", "slide_light", True, two(True), "twoObj")

    def statement(t):
        rule(t, M, 1.75, 1.2)
        t.ph("Statement", "title", None, M, 1.95, 10.8, 3.4, lst=title_lst(60, font=B.DISPLAY_BLACK, ln=92),
             prompt=P("statement.statement"), anchor="t")
        t.ph("Line", "body", 1, M, 5.45, 9, 0.7, lst=plain_lst(20, B.GREY), prompt=P("statement.line"))
        footer(t, b)
    add("Big statement", "slide_charcoal", False, statement)

    def stats(t):
        eyebrow(t, M, 0.55, 10)
        rule(t, M, 1.05)
        t.ph("Title", "title", None, M, 1.2, W - 2 * M, 1.0, lst=title_lst(36), prompt=P("big-numbers.title"), anchor="t")
        cw = (W - 2 * M - 1.0) / 3
        for k in range(3):
            x = M + k * (cw + 0.5)
            t.ph("Number %d" % (k + 1), "body", 20 + k, x, 2.6, cw, 1.6, lst=lvl(sz=88, font=B.DISPLAY_BLACK, colour=B.ORANGE, ln=90),
                 prompt=P("big-numbers.number"), autofit="none", anchor="b")
            t.shape(x, 4.3, 0.6, 0.06, solid(B.TINT), name="Rule")
            t.ph("Number label %d" % (k + 1), "body", 23 + k, x, 4.5, cw, 1.6, lst=plain_lst(18, B.WHITE),
                 prompt=P("big-numbers.number-label"))
        footer(t, b)
    add("Big numbers", "slide_stats", False, stats)

    def quote(t):
        t.shape(M, 0.9, 1.1, 1.1, "", name="Quote mark",
                text='<p:txBody><a:bodyPr wrap="none" lIns="0" tIns="0" rIns="0" bIns="0"/><a:lstStyle/><a:p>'
                     '<a:r>%s<a:t>\u201C</a:t></a:r></a:p></p:txBody>' % rpr(150, 0, font=B.DISPLAY_BLACK, colour=B.ORANGE, tag="a:rPr"))
        t.ph("Quote", "body", 1, M, 2.15, 7.4, 3.0, lst=lvl(sz=32, font=B.DISPLAY, b=1, colour=B.WHITE, ln=115),
             prompt=P("quote.quote"), anchor="t")
        rule(t, M, 5.35)
        t.ph("Title", "title", None, M, 5.5, 7.4, 0.55, lst=plain_lst(20, B.WHITE, font=B.DISPLAY, b=1, cap="all"),
             prompt=P("quote.title"), anchor="t", autofit="none")
        t.ph("Role", "body", 13, M, 6.02, 7.4, 0.45, lst=plain_lst(16, B.TINT, i=1), prompt=P("quote.role"), autofit="none")
    add("Quote", "slide_quote", False, quote)

    def full_photo(t):
        t.ph("Photo", "pic", 15, 0, 0, W, H - 1.55, prompt=P("full-photo.photo"))
        sticker(t, M, 0.55, prompt=P("full-photo.sticker"))
        t.ph("Title", "title", None, M, H - 1.4, 8.6, 0.75, lst=title_lst(32), prompt=P("full-photo.title"), anchor="ctr",
             autofit="none")
        t.ph("Caption", "body", 1, M, H - 0.68, 8.6, 0.45, lst=plain_lst(14, B.GREY), prompt=P("full-photo.caption"),
             autofit="none")
        lg = B.logo(b, "reversed-dark", 512)
        iw, ih = Image.open(lg).size
        t.pic(lg, W - M - 0.34 * iw / ih, H - 0.98, h=0.34, descr=CI.fill(P("alt.logo"), brand=b))
    add("Full photo", "slide_dark", False, full_photo)

    def wall(t):
        t.ph("Photo 1", "pic", 15, 5.0, 0, 5.0, H, prompt=P("photo-wall.photo-1"))
        t.ph("Photo 2", "pic", 16, 10.08, 0, W - 10.08, H / 2 - 0.04, prompt=P("photo-wall.photo-2"))
        t.ph("Photo 3", "pic", 17, 10.08, H / 2 + 0.04, W - 10.08, H / 2 - 0.04, prompt=P("photo-wall.photo-3"))
        eyebrow(t, M, 1.6, 3.8)
        t.ph("Title", "title", None, M, 2.05, 3.9, 2.6, lst=title_lst(36, font=B.DISPLAY_BLACK), prompt=P("photo-wall.title"),
             anchor="t")
        t.ph("Text", "body", 1, M, 4.7, 3.8, 1.6, lst=plain_lst(16, B.GREY), prompt=P("photo-wall.text"))
        lg = B.logo(b, "reversed-dark", 512)
        t.pic(lg, M, 0.6, h=0.32, descr=CI.fill(P("alt.logo"), brand=b))
    add("Photo wall", "slide_dark", False, wall)

    def person(t):
        t.ph("Photo", "pic", 15, 0, 0, 5.4, H, prompt=P("speaker.photo"))
        t.shape(5.4 - 0.08, 0, 0.08, H, solid(B.ORANGE), name="Edge")
        eyebrow(t, 6.2, 1.6, 6.3, prompt=P("speaker.eyebrow"))
        t.ph("Title", "title", None, 6.2, 2.05, 6.4, 2.3, lst=title_lst(54, font=B.DISPLAY_BLACK, ln=90),
             prompt=P("speaker.title"), anchor="t")
        t.shape(6.2, 4.42, 1.6, 0.12, solid(B.ORANGE), geom="roundRect", adj='<a:gd name="adj" fmla="val 50000"/>', name="Pill bar")
        t.ph("Role", "body", 18, 6.2, 4.7, 6.4, 0.5, lst=plain_lst(20, B.TINT, i=1, b=1), prompt=P("speaker.role"), autofit="none")
        t.ph("Session", "body", 1, 6.2, 5.3, 6.3, 1.2, lst=plain_lst(18, B.GREY), prompt=P("speaker.session"))
        footer(t, b)
    add("Speaker", "slide_dark", False, person)

    def agenda(light):
        def f(t):
            eyebrow(t, M, 0.55, 10, light=light, prompt=P("agenda.eyebrow"))
            rule(t, M, 1.05)
            t.ph("Title", "title", None, M, 1.2, W - 2 * M, 1.0, lst=title_lst(36, colour=B.CHARCOAL if light else None),
                 prompt=P("agenda.title"), anchor="t")
            t.ph("Times", "body", 19, M, 2.45, 1.9, 4.2,
                 lst=lvl(sz=20, font=B.DISPLAY, b=1, colour=B.ORANGE_TEXT if light else B.ORANGE, ln=125, after=14),
                 prompt=P("agenda.times"))
            t.ph("Items", "body", 1, M + 2.0, 2.45, W - 2 * M - 2.0, 4.2,
                 lst=lvl(sz=20, font=B.BODY, colour=B.SLATE if light else B.WHITE, ln=125, after=14),
                 prompt=P("agenda.items"))
            footer(t, b, light)
        return f
    add("Agenda", "slide_dark", False, agenda(False))
    add("Agenda (light)", "slide_light", True, agenda(True))

    def title_only(light):
        def f(t):
            eyebrow(t, M, 0.55, 10, light=light)
            rule(t, M, 1.05)
            t.ph("Title", "title", None, M, 1.2, W - 2 * M, 1.0, lst=title_lst(36, colour=B.CHARCOAL if light else None),
                 prompt=P("title-only.title"), anchor="t")
            footer(t, b, light)
        return f
    add("Title only", "slide_dark", False, title_only(False), "titleOnly")
    add("Title only (light)", "slide_light", True, title_only(True), "titleOnly")

    def blank(t):
        t.ph("Title", "title", None, M, -1.2, 6, 0.8, lst=title_lst(28), prompt=P("blank.title"))
    add("Blank", "slide_dark", False, blank, "blank")

    def end(t):
        lk = B.logo(b, "tagline-lockup-reversed", 2048)
        iw, ih = Image.open(lk).size
        w = 6.4
        t.pic(lk, (W - w) / 2, 1.0, w=w, descr=CI.fill(P("alt.lockup"), brand=b, line=info["line"]))
        t.ph("Title", "title", None, 1.5, 3.25, W - 3.0, 1.2, lst=title_lst(48, font=B.DISPLAY_BLACK, algn="ctr"),
             prompt=P("end-card.title"), anchor="ctr")
        t.ph("Date line", "body", 13, 1.5, 4.45, W - 3.0, 0.5, lst=plain_lst(20, B.GREY, algn="ctr", b=1),
             prompt=info["edition"] or P("end-card.date-line"))
        t.ph("Button", "body", 14, (W - 4.2) / 2, 5.25, 4.2, 0.8, geom="roundRect", fill=solid(B.ORANGE),
             lst=lvl(sz=22, font=B.DISPLAY, b=1, cap="all", spc=50, colour=B.WHITE, algn="ctr"),
             prompt=info["url"], anchor="ctr", autofit="none")
    add("End card", "slide_end", False, end)
    for name in extra:
        EXTRA[name](b, add)
    if names:
        by = {l["name"]: l for l in L}
        L = [by[n] for n in names]
    return L


def _holding(b, add):
    def f(t):
        t.pic(B.logo(b, "reversed-dark", 1024), M, 0.6, h=0.5, descr=CI.fill(P("alt.logo"), brand=b))
        t.ph("Title", "title", None, M, 1.9, W - 2 * M, 3.0, lst=title_lst(80, font=B.DISPLAY_BLACK, algn="ctr", ln=90),
             prompt=P("holding.title"), anchor="ctr", autofit="norm")
        t.ph("Line", "body", 1, 1.5, 5.1, W - 3.0, 0.9, lst=plain_lst(28, B.GREY, algn="ctr"),
             prompt=P("holding.line"))
        t.ph("Footer line", "body", 13, M, 6.6, W - 2 * M, 0.5, lst=plain_lst(18, B.TINT, algn="ctr", b=1),
             prompt=B.BRANDS[b]["line"], autofit="none")
    add("Holding", "slide_title", False, f)


def _up_next(b, add):
    def f(t):
        eyebrow(t, M, 0.55, 8, prompt=P("up-next.eyebrow"))
        rule(t, M, 1.05)
        t.ph("Title", "title", None, M, 1.3, 8.0, 2.6, lst=title_lst(44, font=B.DISPLAY_BLACK, ln=92), prompt=P("up-next.title"),
             anchor="t")
        t.ph("Speakers", "body", 1, M, 4.1, 8.0, 2.2, lst=plain_lst(24, B.WHITE, ln=125), prompt=P("up-next.speakers"))
        t.ph("Time", "body", 14, 9.1, 1.3, 3.5, 1.6, lst=lvl(sz=72, font=B.DISPLAY_BLACK, colour=B.ORANGE, algn="r", ln=90),
             prompt=P("up-next.time"), anchor="t", autofit="none")
        t.ph("Stage", "body", 15, 9.1, 3.0, 3.5, 0.6, lst=plain_lst(20, B.TINT, algn="r", b=1, cap="all", spc=100),
             prompt=P("up-next.stage"), autofit="none")
        footer(t, b)
    add("Up next", "slide_dark", False, f)


def _logo_grid(b, add):
    def f(t):
        eyebrow(t, M, 0.55, 10, light=True, prompt=P("logo-grid.eyebrow"))
        rule(t, M, 1.05)
        t.ph("Title", "title", None, M, 1.2, W - 2 * M, 1.0, lst=title_lst(36, colour=B.CHARCOAL), prompt=P("logo-grid.title"),
             anchor="t")
        cw, chh, gap = 2.6, 1.5, 0.45
        for k in range(8):
            x = M + (k % 4) * (cw + gap)
            y = 2.6 + (k // 4) * (chh + gap)
            t.ph("Logo %d" % (k + 1), "pic", 15 + k, x, y, cw, chh, prompt=P("logo-grid.logo"))
        footer(t, b, light=True)
    add("Logo grid (light)", "slide_light", True, f)


def _cobrand_title(b, add):
    host = host_line(b)

    def f(t):
        t.ph("Your logo", "pic", 15, M, 0.55, 3.4, 1.2, prompt=P("cobrand-title.your-logo"))
        lg = B.logo(b, "reversed-dark", 1024)
        iw, ih = Image.open(lg).size
        t.pic(lg, W - M - 0.5 * iw / ih, 0.55, h=0.5, descr=CI.fill(P("alt.logo"), brand=b))
        t.ph("Host line", "body", 13, 7.0, 1.15, W - M - 7.0, 0.45, lst=plain_lst(14, B.TINT, algn="r", b=1, cap="all", spc=300),
             prompt=host, autofit="none")
        t.ph("Title", "ctrTitle", None, M, 2.3, 11.2, 2.8, lst=title_lst(54, font=B.DISPLAY_BLACK, ln=92), anchor="b",
             prompt=P("cobrand-title.title"))
        t.ph("Subtitle", "subTitle", 1, M, 5.25, 9.0, 0.8, lst=plain_lst(22, B.GREY), prompt=P("cobrand-title.subtitle"))
        t.ph("Date line", "body", 14, M, 6.2, 9.0, 0.5, lst=plain_lst(16, B.TINT, b=1), prompt=B.BRANDS[b]["edition"] or P("cobrand-title.date-line"))
    add("Co-branded title", "slide_title", False, f, "title")


def _cobrand_end(b, add):
    host = host_line(b)

    def f(t):
        t.ph("Your logo", "pic", 15, (W - 3.4) / 2, 0.9, 3.4, 1.2, prompt=P("cobrand-end.your-logo"))
        t.ph("Title", "title", None, 1.5, 2.5, W - 3.0, 1.2, lst=title_lst(48, font=B.DISPLAY_BLACK, algn="ctr"),
             prompt=P("cobrand-end.title"), anchor="ctr")
        t.ph("Contact", "body", 13, 1.5, 3.8, W - 3.0, 1.2, lst=plain_lst(20, B.GREY, algn="ctr", ln=130),
             prompt=P("cobrand-end.contact"))
        t.ph("Host line", "body", 14, 1.5, 5.4, W - 3.0, 0.5, lst=plain_lst(16, B.TINT, algn="ctr", b=1, cap="all", spc=300),
             prompt=host, autofit="none")
        lg = B.logo(b, "reversed-dark", 1024)
        iw, ih = Image.open(lg).size
        t.pic(lg, (W - 0.5 * iw / ih) / 2, 6.1, h=0.5, descr=CI.fill(P("alt.logo"), brand=b))
    add("Co-branded end", "slide_end", False, f)


EXTRA = {"Holding": _holding, "Up next": _up_next, "Logo grid (light)": _logo_grid, "Co-branded title": _cobrand_title,
         "Co-branded end": _cobrand_end}


def layout_xml(spec, tree):
    bg = ""
    if spec["bg"]:
        rid = tree.media(os.path.join(ART, spec["bg"] + ".jpg"))
        bg = ('<p:bg><p:bgPr><a:blipFill dpi="0" rotWithShape="1"><a:blip r:embed="%s"/><a:srcRect/><a:stretch><a:fillRect/>'
              '</a:stretch></a:blipFill><a:effectLst/></p:bgPr></p:bg>' % rid)
    cm = ('<p:clrMapOvr><a:overrideClrMapping %s/></p:clrMapOvr>' % LIGHT_MAP if spec["light"]
          else '<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>')
    return (XML + '<p:sldLayout %s type="%s" preserve="1" userDrawn="1"><p:cSld name="%s">%s%s</p:cSld>%s</p:sldLayout>'
            % (NS, spec["typ"], escape(spec["name"]), bg, tree.xml(), cm))


def master_xml(b, tree, layout_ids):
    tree.ph("Title", "title", None, M, 1.2, W - 2 * M, 1.0, prompt=P("master.title"))
    tree.ph("Text", "body", 1, M, 2.45, W - 2 * M, 4.25, prompt=P("master.text"))
    tree.ph("Footer", "ftr", 3, M + 0.7, 6.92, 6.0, 0.32)
    tree.ph("Slide Number", "sldNum", 4, M, 6.92, 0.6, 0.32,
            paras='<a:p><a:fld id="{B6F15528-21DE-4FAA-801E-634DDDAF4B2B}" type="slidenum"><a:rPr lang="en-GB"/><a:t>&lt;#&gt;</a:t></a:fld></a:p>')
    ids = "".join('<p:sldLayoutId id="%d" r:id="%s"/>' % (2147483649 + i, rid) for i, rid in enumerate(layout_ids))
    title_style = ('<p:titleStyle>%s</p:titleStyle>' % lvl(sz=36, font=B.DISPLAY_XB, cap="all", spc=-50, scheme="tx1", ln=95))
    body_style = '<p:bodyStyle>%s</p:bodyStyle>' % body_lst(20).replace('<a:srgbClr val="FFFFFF"/>', '<a:schemeClr val="tx1"/>')
    other = '<p:otherStyle>%s</p:otherStyle>' % lvl(sz=18, font=B.BODY, scheme="tx1")
    return (XML + '<p:sldMaster %s><p:cSld><p:bg><p:bgPr>%s<a:effectLst/></p:bgPr></p:bg>%s</p:cSld><p:clrMap %s/>'
            '<p:sldLayoutIdLst>%s</p:sldLayoutIdLst><p:txStyles>%s%s%s</p:txStyles></p:sldMaster>'
            % (NS, solid(B.DARK), tree.xml(), DARK_MAP, ids, title_style, body_style, other))


def slide_xml(spec, tree):
    cm = ('<p:clrMapOvr><a:overrideClrMapping %s/></p:clrMapOvr>' % LIGHT_MAP if spec["light"]
          else '<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>')
    return XML + '<p:sld %s><p:cSld>%s</p:cSld>%s</p:sld>' % (NS, tree.xml(), cm)


def rels(items):
    """items: [(rid, type, target)]"""
    base = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/"
    return (XML + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">%s</Relationships>'
            % "".join('<Relationship Id="%s" Type="%s%s" Target="%s"/>' % (r, base + t if "://" not in t else t, "", tg)
                      for r, t, tg in items))


def copy_path(b, row):
    """The copy file with the example slides of one template."""
    return CI.path(K.copy_file(b, row))


def build(b, out_path, template=True, deck=None, words=None):
    """deck: None for the presentation template, else a deck spec from deck_samples.DECKS. words: the copy file with
    the example slides."""
    specs = layouts(b, deck.get("layouts") if deck else None, deck.get("extra", ()) if deck else ())
    files = {}
    media = {}  # source path -> media name

    def media_name(path):
        if path not in media:
            ext = os.path.splitext(path)[1].lower()
            media[path] = "image%d%s" % (len(media) + 1, ext)
        return media[path]

    # Layouts.
    lay_trees = []
    for i, s in enumerate(specs, 1):
        t = Tree()
        s["fn"](t)
        x = layout_xml(s, t)
        files["ppt/slideLayouts/slideLayout%d.xml" % i] = x
        r = [("rId1", "slideMaster", "../slideMasters/slideMaster1.xml")]
        r += [(rid, "image", "../media/" + media_name(p)) for rid, p in t.rels]
        files["ppt/slideLayouts/_rels/slideLayout%d.xml.rels" % i] = rels(r)
        lay_trees.append(t)
    # Master.
    mt = Tree()
    lids = ["rId%d" % (i + 1) for i in range(len(specs))]
    files["ppt/slideMasters/slideMaster1.xml"] = master_xml(b, mt, lids)
    r = [(lids[i], "slideLayout", "../slideLayouts/slideLayout%d.xml" % (i + 1)) for i in range(len(specs))]
    r.append(("rId%d" % (len(specs) + 1), "theme", "../theme/theme1.xml"))
    files["ppt/slideMasters/_rels/slideMaster1.xml.rels"] = rels(r)
    files["ppt/theme/theme1.xml"] = T.theme_xml("%s Slides" % b, hlink=B.TINT)

    # Sample slides.
    by_name = {s["name"]: (i + 1, s) for i, s in enumerate(specs)}
    slides = C.slides(words, D.FILLS)
    for k, (lname, fill) in enumerate(slides, 1):
        li, spec = by_name[lname]
        t = Tree()
        t.layout = lay_trees[li - 1]
        fill(t, spec)
        files["ppt/slides/slide%d.xml" % k] = slide_xml(spec, t)
        r = [("rId1", "slideLayout", "../slideLayouts/slideLayout%d.xml" % li)]
        r += [(rid, "image", "../media/" + media_name(p)) for rid, p in t.rels]
        files["ppt/slides/_rels/slide%d.xml.rels" % k] = rels(r)

    n_sl = len(slides)
    pres_rels = [("rId1", "slideMaster", "slideMasters/slideMaster1.xml")]
    pres_rels += [("rId%d" % (k + 1), "slide", "slides/slide%d.xml" % k) for k in range(1, n_sl + 1)]
    nxt = n_sl + 2
    pres_rels += [("rId%d" % nxt, "theme", "theme/theme1.xml"), ("rId%d" % (nxt + 1), "presProps", "presProps.xml"),
                  ("rId%d" % (nxt + 2), "viewProps", "viewProps.xml"), ("rId%d" % (nxt + 3), "tableStyles", "tableStyles.xml")]
    files["ppt/_rels/presentation.xml.rels"] = rels(pres_rels)
    sld_ids = "".join('<p:sldId id="%d" r:id="rId%d"/>' % (255 + k, k + 1) for k in range(1, n_sl + 1))
    files["ppt/presentation.xml"] = (
        XML + '<p:presentation %s saveSubsetFonts="1"><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/>'
        '</p:sldMasterIdLst><p:sldIdLst>%s</p:sldIdLst><p:sldSz cx="%d" cy="%d"/><p:notesSz cx="6858000" cy="9144000"/>'
        '<p:defaultTextStyle>%s</p:defaultTextStyle></p:presentation>'
        % (NS, sld_ids, SW, SH, lvl(sz=18, scheme="tx1")))
    files["ppt/presProps.xml"] = XML + '<p:presentationPr %s/>' % NS
    files["ppt/viewProps.xml"] = XML + ('<p:viewPr %s><p:normalViewPr><p:restoredLeft sz="15620"/><p:restoredTop sz="94660"/>'
                                        '</p:normalViewPr><p:gridSpacing cx="76200" cy="76200"/></p:viewPr>' % NS)
    files["ppt/tableStyles.xml"] = (XML + '<a:tblStyleLst xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
                                    'def="{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}"/>')
    files["docProps/core.xml"] = (
        XML + '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>%s</dc:title><dc:creator>%s</dc:creator>'
        '<dc:language>en-GB</dc:language></cp:coreProperties>' % (escape(deck["title"]) if deck else b + " presentation", b))
    files["docProps/app.xml"] = (XML + '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">'
                                 '<Application>Microsoft Office PowerPoint</Application><Company>ClimbGroup</Company></Properties>')
    files["_rels/.rels"] = rels([("rId1", "officeDocument", "ppt/presentation.xml"),
                                 ("rId2", "http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties",
                                  "docProps/core.xml"),
                                 ("rId3", "extended-properties", "docProps/app.xml")])
    main_ct = ("application/vnd.openxmlformats-officedocument.presentationml.template.main+xml" if template
               else "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml")
    ov = [("/ppt/presentation.xml", main_ct),
          ("/ppt/slideMasters/slideMaster1.xml", "application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"),
          ("/ppt/theme/theme1.xml", "application/vnd.openxmlformats-officedocument.theme+xml"),
          ("/ppt/presProps.xml", "application/vnd.openxmlformats-officedocument.presentationml.presProps+xml"),
          ("/ppt/viewProps.xml", "application/vnd.openxmlformats-officedocument.presentationml.viewProps+xml"),
          ("/ppt/tableStyles.xml", "application/vnd.openxmlformats-officedocument.presentationml.tableStyles+xml"),
          ("/docProps/core.xml", "application/vnd.openxmlformats-package.core-properties+xml"),
          ("/docProps/app.xml", "application/vnd.openxmlformats-officedocument.extended-properties+xml")]
    ov += [("/ppt/slideLayouts/slideLayout%d.xml" % i, "application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml")
           for i in range(1, len(specs) + 1)]
    ov += [("/ppt/slides/slide%d.xml" % k, "application/vnd.openxmlformats-officedocument.presentationml.slide+xml")
           for k in range(1, n_sl + 1)]
    files["[Content_Types].xml"] = (
        XML + '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/>'
        '<Default Extension="jpg" ContentType="image/jpeg"/><Default Extension="jpeg" ContentType="image/jpeg"/>%s</Types>'
        % "".join('<Override PartName="%s" ContentType="%s"/>' % o for o in ov))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", files.pop("[Content_Types].xml"))
        z.writestr("_rels/.rels", files.pop("_rels/.rels"))
        for k, v in files.items():
            z.writestr(k, v)
        for src, name in media.items():
            z.write(src, "ppt/media/" + name)
    return out_path


def all_copy(brands=("ClimbUK", "ClimbGroup", "Climb27")):
    """Every string a reader sees on the example slides and in the placeholder prompts, for the copy checker."""
    import re
    out = []
    for b in brands:
        for row in K.rows("powerpoint", b):
            deck = D.DECKS[(row["name"], row["external"])] if not row["original"] else None
            specs = layouts(b, deck.get("layouts") if deck else None, deck.get("extra", ()) if deck else ())
            trees = []
            for sp in specs:
                t = Tree()
                sp["fn"](t)
                trees.append(t)
                out += re.findall(r"<a:t>([^<]*)</a:t>", t.xml())
            by = {sp["name"]: k for k, sp in enumerate(specs)}
            for lname, fill in C.slides(copy_path(b, row), D.FILLS):
                t = Tree()
                t.layout = trees[by[lname]]
                fill(t, specs[by[lname]])
                out += re.findall(r"<a:t>([^<]*)</a:t>", t.xml())
    from xml.sax.saxutils import unescape
    return [unescape(x) for x in out]


def main():
    args = sys.argv[1:]
    if args[:1] == ["--copy"]:
        print("\n".join(all_copy()))
        return
    only = None
    if args[:1] == ["--only"]:
        only, args = args[1:], []
    brands = args or list(B.BRANDS)
    for b in brands:
        for row in K.rows("powerpoint", b):
            if only and row["name"] not in only:
                continue
            deck = None if row["original"] else dict(D.DECKS[(row["name"], row["external"])], title="%s %s" % (b, row["title"].lower()))
            stem = K.stem(b, row)
            d = os.path.join(B.OUT, "office", K.folder(b, row))
            words = copy_path(b, row)
            p = build(b, os.path.join(d, stem + ".potx"), deck=deck, words=words)
            build(b, os.path.join(B.OUT, "_preview", stem + ".pptx"), template=False, deck=deck, words=words)
            print(p)


if __name__ == "__main__":
    main()
