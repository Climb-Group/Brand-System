"""Builds the brand guidelines book (16:9 slides) for ClimbUK, ClimbGroup and Climb27 as HTML, ready for render.cjs.

The words come from pdf/guidelines/<brand>_brand-guidelines.copy.md, then pdf/guidelines/brand-guidelines.copy.md
for the pages every book shares. This script holds only the layout."""
import os
import re
import sys

import motifs
from brands import BRANDS, Words, copy_path, md

HERE = os.path.dirname(os.path.abspath(__file__))
P = "assets/photos/"
W, H = 1920, 1080
SHARED = copy_path("guidelines", "brand-guidelines.copy.md")
# The alt text of each brand's logo, from the shared copy file.
ALT = {s["brand"]: md(s.text) for s in Words(SHARED).secs("logo.alt")}
# What prints inside a crossed-out sign on the voice rules page, by its glyph setting.
GLYPHS = {"dash": "\u2014"}


def logo(b, variant, h=None, w=None, style=""):
    size = ("height:%dpx;" % h if h else "") + ("width:%dpx;" % w if w else "")
    return '<img src="assets/logos/%s/%s_%s.svg" style="%s%s" alt="%s">' % (b, b, variant, size, style, ALT[b])


# Clear space around a logo is the height of the large C in Climb, as a share of the logo's height.
CLEAR_C = {"ClimbUK": 1.0, "ClimbGroup": 0.83, "Climb27": 1.0}
CLEAR_C_LOCKUP = {"ClimbUK": 0.70, "ClimbGroup": 0.58, "Climb27": 0.715}


def logo_aspect(b, variant):
    """Width over height of a logo master, read from its viewBox."""
    head = open(os.path.join(HERE, "assets/logos/%s/%s_%s.svg" % (b, b, variant))).read(400)
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', head).group(1).split()]
    return vb[2] / vb[3]


def svg(inner, w=W, h=H, style="position:absolute;inset:0"):
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" style="%s">%s</svg>' % (
        w, h, w, h, style, inner)


def photo(f, fade="fade-brown", pos="center", extra=""):
    return ('<div class="ph" style="background-image:url(%s%s);background-position:%s;%s"></div>'
            '<div class="layer %s"></div>' % (P, f, pos, extra, fade))


def texts(bk, path):
    """Each section of a repeated name as HTML, for two lists that pair up row by row."""
    return [md(s.text, quotes=s.get("quotes") == "curly") for s in bk.w.secs(path)]


def pairs(left, right):
    assert len(left) == len(right), "%d and %d sections do not pair up" % (len(left), len(right))
    return list(zip(left, right))


def lis(items):
    return "".join("<li>%s</li>" % i for i in items)


class Book:
    def __init__(self, b):
        self.b = b
        self.B = BRANDS[b]
        self.w = Words(copy_path("guidelines", "%s_brand-guidelines.copy.md" % self.B["key"]), SHARED)
        self.slides = []
        self.section = ""

    def add(self, cls, inner, foot=True):
        self.slides.append((cls, inner, foot, self.section))

    def render(self):
        out = []
        total = len(self.slides)
        for i, (cls, inner, foot, sec) in enumerate(self.slides, 1):
            f = ""
            if foot:
                light = any(c in cls.split() for c in ("wh", "gr"))
                variant = "mono-dark" if light else ("mono-white" if "or" in cls.split() else "reversed-dark")
                if light and variant == "mono-dark":
                    variant = "full-colour-light" if "wh" in cls.split() else "full-colour-grey"
                f = ('<div class="foot">%s<div class="pg"><span>%s</span><b>%02d</b></div></div>'
                     % (logo(self.b, variant, h=30), sec, i))
            out.append('<section class="s %s">%s%s</section>' % (cls, inner, f))
        return out


# ---------------------------------------------------------------- slides

def cover(bk):
    b, B, w = bk.b, bk.B, bk.w
    if b == "ClimbGroup":
        s1, s2, s3 = w.items("cover.sticker")
        inner = (
            svg(motifs.slabs(W, H, corners=("tl", "br"), length=W * 0.3, thick=H * 0.07)
                + motifs.peak(W, H, x0=0.0, base=0.93, summit=(0.47, 0.62), seed=3, colour="#FFFFFF", opacity=0.14))
            + '<div class="glow"></div>'
            + '<div style="position:absolute;right:110px;top:150px;width:700px;height:760px">'
              '<div style="position:absolute;right:0;top:0;width:520px;height:390px;border-radius:14px;overflow:hidden;transform:rotate(3deg);box-shadow:0 30px 80px rgba(0,0,0,.5)">'
              '<div class="ph" style="background-image:url(%smeetings_01.jpg)"></div></div>'
              '<div style="position:absolute;left:0;top:300px;width:470px;height:330px;border-radius:14px;overflow:hidden;transform:rotate(-3deg);box-shadow:0 30px 80px rgba(0,0,0,.5)">'
              '<div class="ph" style="background-image:url(%sclimb_recap_03.jpg)"></div></div>'
              '<div style="position:absolute;right:30px;top:470px;width:360px;height:290px;border-radius:14px;overflow:hidden;transform:rotate(2deg);box-shadow:0 30px 80px rgba(0,0,0,.5)">'
              '<div class="ph" style="background-image:url(%svip_and_awards_01.jpg)"></div></div>'
              '<span class="sticker" style="position:absolute;left:330px;top:250px;font-size:30px">%s</span>'
              '<span class="sticker white" style="position:absolute;left:70px;top:640px;font-size:30px;transform:rotate(3deg)">%s</span>'
              '<span class="sticker dark" style="position:absolute;right:0;top:740px;font-size:30px">%s</span>'
              '</div>' % (P, P, P, s1, s2, s3)
            + '<div style="position:absolute;left:120px;top:150px">%s</div>' % logo(b, "reversed-dark", h=96)
            + '<div style="position:absolute;left:120px;top:330px;width:1050px">'
              '<div class="eb" style="font-size:26px;margin-bottom:34px">%s</div>'
              '<div class="h" style="font-size:118px">%s</div>'
              '<p class="lead" style="margin-top:40px;max-width:900px;color:var(--lg)">%s</p></div>'
            % (w.t("cover.eyebrow"), w.t("cover.headline"), w.t("cover.lead"))
        )
        bk.add("ch", inner, foot=False)
        return
    pos = "center 35%" if b == "Climb27" else "center 40%"
    inner = (
        photo(B["cover_photo"], "fade-hero", pos)
        # A soft shadow behind the headline keeps it at AA where the fade thins out.
        + '<div class="layer" style="background:radial-gradient(1000px 340px at 32% 66%,rgba(var(--ink),.55),rgba(var(--ink),0) 70%)"></div>'
        + '<div class="glow"></div>'
        + '<div style="position:absolute;left:120px;top:104px">%s</div>' % logo(b, "reversed-dark", h=96)
        + '<div style="position:absolute;right:120px;top:110px"><span class="sticker" style="font-size:30px">%s</span></div>' % w.t("cover.sticker")
        + '<div style="position:absolute;left:120px;bottom:130px;width:1500px">'
          '<div class="eb" style="font-size:26px;margin-bottom:34px">%s</div>'
          '<div class="h" style="font-size:%dpx;text-shadow:0 2px 12px rgba(0,0,0,.6)">%s</div>'
          '<p class="lead" style="margin-top:40px;max-width:980px">%s</p></div>'
        % (w.t("cover.eyebrow"), B.get("cover_size", 170), w.t("cover.headline"), w.t("cover.lead"))
        + svg(motifs.ascent(W, H, 1650, 1000, 150, steps=4, kind="chevrons"))
    )
    bk.add("", inner, foot=False)


# The divider photo of each of the ten sections, in order. Their names and headlines are the '@divider' sections of the copy.
SECTION_PHOTOS = ["climb_awards_winners.jpg", "climb_recap_playlist.jpg", "climb_awards_trophies.jpg", "climb_consultants_expert.jpg",
                  "climb_drinks_reception.jpg", "climb_band_stage.jpg", "climb_isn_investors_hero.jpg", "climb_isn_founders_hero.jpg",
                  "climb_expo_floor.jpg", "crowds_01.jpg"]


def sections(bk):
    """(number, name, photo, headline) for the ten sections."""
    found = bk.w.pairs("divider")
    assert len(found) == len(SECTION_PHOTOS), "%d dividers in the copy, %d photos" % (len(found), len(SECTION_PHOTOS))
    return [("%02d" % (i + 1), nm, ph, h) for i, ((nm, h), ph) in enumerate(zip(found, SECTION_PHOTOS))]


# Per-brand swaps for a section divider photo, by section index.
BRAND_PHOTOS = {
    "ClimbGroup": {1: "climbteam_02.jpg", 7: "stage_speakers_01.jpg"},
    "ClimbUK": {5: "stage_speakers_04.jpg"},
}
# Where a swapped photo has faces high on the right, show its lower part and drop the numeral below the faces.
DIVIDER_FRAME = {"stage_speakers_04.jpg": ("center 100%", 330), "climbteam_02.jpg": ("center 35%", 330)}


def divider(bk, idx):
    n, name, ph, h = sections(bk)[idx]
    ph = BRAND_PHOTOS.get(bk.b, {}).get(idx, ph)
    pos, num_top = DIVIDER_FRAME.get(ph, ("center 35%", 110))
    bk.section = name
    left = idx % 2 == 0
    inner = (
        # Photo stays clear above; the fade only takes the bottom third, where the title sits.
        photo(ph, "fade-divider", pos)
        + '<div class="layer fade-divider-%s"></div>' % ("l" if left else "r")
        + '<div class="glow%s"></div>' % ("" if left else " tl")
        + '<div class="numo" aria-hidden="true" style="position:absolute;%s:120px;top:%dpx;font-size:380px">%s</div>' % ("left" if left else "right", num_top, n)
        + '<div style="position:absolute;%s:120px;bottom:96px;width:1600px;%s">'
          '<div class="eb" style="font-size:24px;margin-bottom:20px;%s">%s</div>'
          '<div class="h" style="font-size:96px;text-shadow:0 2px 12px rgba(0,0,0,.6)">%s</div></div>'
        % ("left" if left else "right", "" if left else "text-align:right", "" if left else "justify-content:flex-end", name, h)
    )
    bk.add("", inner)


def contents(bk):
    """The contents: the ten sections as steps on one rising line, outline numerals above, names below."""
    x0, y0, step_w, rise = 120, 860, 168, 56
    line = ["%d,%d" % (x0, y0)]
    stops = ""
    steps = sections(bk)
    for i, (n, nm, *_r) in enumerate(steps):
        x, y = x0 + i * step_w, y0 - i * rise
        line += ["%d,%d" % (x + step_w, y)]
        if i < len(steps) - 1:
            line += ["%d,%d" % (x + step_w, y - rise)]
        stops += ('<div style="position:absolute;left:%dpx;top:%dpx;width:%dpx">'
                  '<div class="numo" aria-hidden="true" style="font-size:88px;-webkit-text-stroke-width:2.5px;position:absolute;left:16px;bottom:18px">%s</div>'
                  '<div class="mont" style="position:absolute;left:16px;top:22px;width:%dpx;font-weight:700;font-size:18px;line-height:1.2;'
                  'text-transform:uppercase;letter-spacing:.02em;color:#fff">%s</div></div>'
                  % (x, y, step_w, n, step_w - 24, nm))
    inner = (
        svg(motifs.contours(W, H, seed=7, rings=13, cx=0.9, cy=0.95))
        + '<div class="glow"></div>'
        + svg('<polyline points="%s" fill="none" stroke="#E8712A" stroke-width="6" stroke-linejoin="miter"/>' % " ".join(line))
        + stops
        + '<div style="position:absolute;left:120px;top:100px;width:1500px">'
          '<div class="eb" style="font-size:24px">%s</div>'
          '<div class="h" style="font-size:96px;margin-top:30px">%s</div>'
          '<p class="copy" style="margin-top:30px;max-width:900px">%s</p></div>'
        % (bk.w.t("contents.eyebrow"), bk.w.t("contents.headline"), bk.w.t("contents.intro"))
    )
    bk.add(bk.B["ground"], inner)


def family(bk):
    b, w = bk.b, bk.w
    cards = [(s["brand"], md(s.title), md(s.text)) for s in w.secs("family.card")]
    html = ""
    for nm, role, use in cards:
        me = nm == b
        html += ('<div class="card" style="padding:56px 48px;position:relative;%s">'
                 '<div style="height:190px;display:flex;align-items:center;justify-content:center;background:var(--db);border-radius:14px">%s</div>'
                 '<div class="h" style="font-size:40px;margin-top:40px">%s</div>'
                 '<p class="copy" style="margin-top:16px">%s</p>%s</div>'
                 % ("border:3px solid var(--o);box-shadow:0 0 0 8px rgba(232,113,42,.18),0 30px 70px rgba(0,0,0,.4);transform:translateY(-12px)" if me else "",
                    logo(nm, "reversed-dark", h=54), role, use,
                    '<span class="sticker" style="position:absolute;right:-12px;top:-24px;font-size:24px">%s</span>' % w.t("family.sticker") if me else ""))
    inner = (
        '<div class="glow"></div>'
        + '<div class="pad"><div class="eb" style="font-size:24px">%s</div>'
          '<div class="h" style="font-size:96px;margin-top:30px">%s</div>'
          '<p class="lead" style="margin-top:28px;max-width:1300px">%s</p>'
          '<div class="grid" style="grid-template-columns:repeat(3,1fr);gap:40px;margin-top:70px">%s</div></div>'
        % (w.t("family.eyebrow"), w.t("family.headline"), w.t("family.lead"), html)
    )
    bk.add(bk.B["ground"], inner)


def big_idea(bk):
    w = bk.w
    inner = (
        photo("audience_at_stage_02.jpg", "fade-hero", "center 30%")
        + '<div class="glow"></div>'
        + '<div class="pad" style="display:flex;flex-direction:column;justify-content:center">'
          '<div class="eb" style="font-size:24px">%s</div>'
          '<div class="h" style="font-size:150px;margin-top:36px">%s</div>'
          '<div class="h" style="font-size:64px;margin-top:28px;color:var(--tint)">%s</div>'
          '<p class="lead" style="margin-top:44px;max-width:1000px">%s</p></div>'
          % (w.t("big-idea.eyebrow"), w.t("big-idea.headline"), w.t("big-idea.subline"), w.t("big-idea.lead"))
        + '<span class="sticker" style="position:absolute;right:170px;top:180px;font-size:34px;transform:rotate(5deg)">%s</span>' % w.t("big-idea.sticker")
    )
    bk.add("", inner)


def five_rules(bk):
    w = bk.w
    rules = w.pairs("five-rules.rule")
    html = "".join(
        '<div style="position:relative;padding-top:20px"><div class="num" style="font-size:150px;opacity:.95">%d</div>'
        '<div class="h" style="font-size:40px;margin-top:20px">%s</div><p class="copy" style="margin-top:16px">%s</p></div>' % (i + 1, t, d)
        for i, (t, d) in enumerate(rules))
    inner = (
        '<div class="glow"></div>'
        + svg(motifs.ascent(W, H, 1500, 300, 220, steps=5, colour="rgba(255,255,255,.06)"))
        + '<div class="pad"><div class="eb" style="font-size:24px">%s</div>'
          '<div class="h" style="font-size:96px;margin-top:30px">%s</div>'
          '<div class="grid" style="grid-template-columns:repeat(5,1fr);gap:48px;margin-top:80px">%s</div></div>'
        % (w.t("five-rules.eyebrow"), w.t("five-rules.headline"), html)
    )
    bk.add(bk.B["ground"], inner)


def logo_master(bk):
    b, w = bk.b, bk.w
    inner = (
        '<div class="glow"></div><div class="glow tl" style="opacity:.6"></div>'
        + svg(motifs.contours(W, H, seed=11, rings=12, cx=1.02, cy=1.1))
        + '<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center">%s</div>' % logo(b, "reversed-dark", h=170)
        + '<div style="position:absolute;left:120px;top:100px"><div class="eb" style="font-size:24px">%s</div></div>' % w.t("logo-master.eyebrow")
        + '<p class="copy" style="position:absolute;left:120px;bottom:130px;max-width:900px">%s</p>' % w.t("logo-master.body")
        + '<span class="sticker" style="position:absolute;right:160px;bottom:150px;font-size:28px">%s</span>' % w.t("logo-master.sticker")
    )
    bk.add("", inner)


def logo_variants(bk):
    b, w = bk.b, bk.w
    grounds = [("reversed-dark", "var(--db)"), ("full-colour-light", "#fff"), ("full-colour-grey", "var(--lg)"),
               ("mono-white", "var(--o)"), ("mono-dark", "#fff"), ("tagline-lockup-reversed", "var(--ch)")]
    words = w.pairs("logo-variants.tile")
    assert len(words) == len(grounds)
    tiles = [(v, bg, t, d) for (v, bg), (t, d) in zip(grounds, words)]
    html = "".join(
        '<div><div style="background:%s;border-radius:14px;height:205px;display:flex;align-items:center;justify-content:center;%s">%s</div>'
        '<div class="h" style="font-size:28px;margin-top:22px">%s</div><p class="small" style="margin-top:6px">%s</p></div>'
        % (bg, "border:1.5px solid rgba(255,255,255,.12)" if bg in ("var(--db)", "var(--ch)") else "", logo(b, v, h=76 if "lockup" in v else 62), t, d)
        for v, bg, t, d in tiles)
    inner = (
        '<div class="pad"><div class="eb" style="font-size:24px">%s</div>'
        '<div class="h" style="font-size:80px;margin-top:26px">%s</div>'
        '<div class="grid" style="grid-template-columns:repeat(3,1fr);gap:36px 40px;margin-top:48px">%s</div></div>'
        % (w.t("logo-variants.eyebrow"), w.t("logo-variants.headline"), html)
    )
    bk.add(bk.B["ground"], inner)


def logo_space(bk):
    b, t = bk.b, bk.w.t
    w = 640
    c = round(w / logo_aspect(b, "reversed-dark") * CLEAR_C[b])
    inner = (
        '<div class="pad" style="display:grid;grid-template-columns:1.25fr 1fr;gap:90px;align-items:center">'
        '<div style="position:relative;background:var(--db);border-radius:14px;height:640px;display:flex;align-items:center;justify-content:center;border:1.5px solid rgba(255,255,255,.1)">'
        '<div style="position:relative;padding:%dpx;outline:3px dashed rgba(242,174,134,.75);outline-offset:-3px">%s'
        '<div style="position:absolute;left:0;top:0;width:%dpx;height:%dpx;background:rgba(232,113,42,.28)"></div>'
        '<div style="position:absolute;right:0;bottom:0;width:%dpx;height:%dpx;background:rgba(232,113,42,.28)"></div>'
        '<span class="mont" style="position:absolute;left:0;top:0;width:%dpx;line-height:%dpx;text-align:center;font-weight:800;font-size:40px;color:var(--o)">%s</span>'
        '<span class="mont" style="position:absolute;right:0;bottom:0;width:%dpx;line-height:%dpx;text-align:center;font-weight:800;font-size:40px;color:var(--o)">%s</span></div>'
        '<span class="sticker" style="position:absolute;left:40px;bottom:30px;font-size:24px">%s</span></div>'
        '<div><div class="eb" style="font-size:24px">%s</div>'
        '<div class="h" style="font-size:80px;margin-top:26px">%s</div>'
        '<ul class="list copy" style="margin-top:44px">%s</ul></div></div>'
        % (c, logo(b, "reversed-dark", w=w), c, c, c, c, c, c, t("logo-space.mark"), c, c, t("logo-space.mark"),
           t("logo-space.sticker"), t("logo-space.eyebrow"), t("logo-space.headline"), lis(bk.w.items("logo-space.points")))
    )
    bk.add(bk.B["ground"], inner)


def logo_icons(bk):
    b, t = bk.b, bk.w.t
    inner = (
        '<div class="glow"></div>'
        + '<div class="pad" style="display:grid;grid-template-columns:1fr 1fr;gap:100px;align-items:center">'
          '<div><div class="eb" style="font-size:24px">%s</div>'
          '<div class="h" style="font-size:80px;margin-top:26px">%s</div>'
          '<ul class="list copy" style="margin-top:44px">%s</ul></div>'
          '<div style="display:flex;gap:60px;align-items:flex-end;justify-content:center">'
          '<div style="text-align:center">%s<p class="small" style="margin-top:20px">%s</p></div>'
          '<div style="text-align:center">%s<p class="small" style="margin-top:20px">%s</p></div>'
          '<div style="display:flex;flex-direction:column;gap:22px;align-items:center">%s%s%s<p class="small">%s</p></div></div></div>'
        % (t("logo-icons.eyebrow"), t("logo-icons.headline"), lis(bk.w.items("logo-icons.points")),
           logo(b, "icon-on-ground", w=360, style="border-radius:40px;box-shadow:0 30px 80px rgba(0,0,0,.5)"),
           t("logo-icons.tile-caption"),
           logo(b, "icon-monogram-on-ground", w=240, style="border-radius:28px;box-shadow:0 30px 80px rgba(0,0,0,.5)"), t("logo-icons.monogram-caption"),
           logo(b, "icon-monogram-on-ground", w=64, style="border-radius:10px"), logo(b, "icon-monogram-on-ground", w=32, style="border-radius:6px"),
           logo(b, "icon-monogram-on-ground", w=16, style="border-radius:3px"), t("logo-icons.sizes-caption"))
    )
    bk.add(bk.B["ground"], inner)


def logo_donts(bk):
    b = bk.b
    L = "assets/logos/%s/%s_" % (b, b)
    tiles = [
        ('<img src="%sreversed-dark.svg" style="width:290px;transform:scaleX(1.45)">' % L, "var(--db)"),
        ('<img src="%sreversed-dark.svg" style="width:290px;transform:rotate(-12deg)">' % L, "var(--db)"),
        ('<img src="%sreversed-dark.svg" style="width:290px;filter:hue-rotate(150deg) saturate(1.6)">' % L, "var(--db)"),
        ('<img src="%sreversed-dark.svg" style="width:290px;filter:drop-shadow(0 0 18px #F2AE86) drop-shadow(8px 10px 0 #000)">' % L, "var(--db)"),
        ('<img src="%sfull-colour-light.svg" style="width:290px">' % L, "var(--o)"),
        ('<div class="ph" style="background-image:url(%sclimb_recap_07.jpg);border-radius:14px"></div><img src="%sreversed-dark.svg" style="width:290px;position:relative">' % (P, L), "var(--db)"),
    ]
    words = bk.w.items("logo-donts.points")
    assert len(words) == len(tiles)
    items = [(el, bg, t) for (el, bg), t in zip(tiles, words)]
    html = "".join(
        '<div><div style="position:relative;background:%s;border-radius:14px;height:205px;display:flex;align-items:center;justify-content:center;overflow:hidden;border:1.5px solid rgba(255,255,255,.12)">%s</div>'
        '<div style="display:flex;align-items:center;gap:16px;margin-top:20px">'
        '<div style="flex:none;width:44px;height:44px;border-radius:50%%;background:var(--db);border:3px solid var(--o);display:flex;align-items:center;justify-content:center;font:800 30px/1 Montserrat;color:var(--o)" aria-hidden="true">\u00d7</div>'
        '<div class="h" style="font-size:28px">%s</div></div></div>' % (bg, el, t)
        for el, bg, t in items)
    inner = (
        '<div class="pad"><div class="eb" style="font-size:24px">%s</div>'
        '<div class="h" style="font-size:80px;margin-top:26px">%s</div>'
        '<div class="grid" style="grid-template-columns:repeat(3,1fr);gap:36px 40px;margin-top:44px">%s</div></div>'
        % (bk.w.t("logo-donts.eyebrow"), bk.w.t("logo-donts.headline"), html)
    )
    bk.add(bk.B["ground"], inner)


def edition_mark(bk):
    """Climb27 only: how the edition mark and ClimbUK sit together."""
    t = bk.w.t
    inner = (
        photo("stage_speakers_01.jpg", "fade-hero", "center 30%")
        # Text on the left, the ticket low on the right: the photo shows above the ticket.
        + '<div class="pad">'
          '<div style="width:820px;position:absolute;top:0"><div class="eb" style="font-size:24px">%s</div>'
          '<div class="h" style="font-size:76px;margin-top:26px">%s</div>'
          '<ul class="list copy" style="margin-top:44px">%s</ul></div>'
          '<div class="ticket" style="position:absolute;right:0;bottom:0;width:640px;padding:56px 60px 44px">'
          '%s<div class="h" style="font-size:40px;margin-top:44px">%s</div>'
          '<div class="tear" style="margin:36px -60px 32px"><div class="notch" style="left:-23px;top:-24px"></div><div class="notch" style="right:-23px;top:-24px"></div></div>'
          '<div style="display:flex;justify-content:space-between;align-items:center"><div class="mont" style="font-weight:700;font-size:26px">%s</div>%s</div></div></div>'
        % (t("edition.eyebrow"), t("edition.headline"), lis(bk.w.items("edition.points")), logo("Climb27", "reversed-dark", w=300),
           t("edition.ticket-headline"), t("edition.ticket-dates"), logo("ClimbUK", "mono-white", h=30))
    )
    bk.add("", inner)


def colours(bk):
    w = bk.w
    # Ground, text colour and width of each swatch, in the order of the swatches in the copy.
    look = [("var(--o)", "var(--db)", 2.2), ("var(--db)", "#fff", 2.2), ("var(--ch)", "#fff", 1.4),
            ("var(--lg)", "var(--ch)", 1), ("var(--tint)", "var(--db)", 1), ("#fff", "var(--ch)", 1)]
    words = w.lines("colours.swatch")
    assert len(words) == len(look)
    sw = [(n, hx, bg, fg, pa, cm, ral, fl) for (n, (hx, pa, cm, ral)), (bg, fg, fl) in zip(words, look)]
    html = "".join(
        '<div style="flex:%s;background:%s;color:%s;border-radius:14px;padding:36px 32px;display:flex;flex-direction:column;justify-content:flex-end;%s">'
        '<div class="h" style="font-size:34px;color:inherit">%s</div><div class="mont" style="font-weight:700;font-size:30px;margin-top:8px">%s</div>'
        '<div style="font-size:20px;line-height:1.5;margin-top:18px;opacity:.92">%s<br>%s<br>%s</div></div>'
        % (fl, bg, fg, "border:1.5px solid rgba(255,255,255,.14)" if bg in ("var(--db)", "var(--ch)") else "", n, hx, pa, cm, ral)
        for n, hx, bg, fg, pa, cm, ral, fl in sw)
    inner = (
        '<div class="pad"><div class="eb" style="font-size:24px">%s</div>'
        '<div class="h" style="font-size:80px;margin-top:26px">%s</div>'
        '<div style="display:flex;gap:22px;height:560px;margin-top:56px">%s</div>'
        '<p class="small" style="margin-top:22px">%s</p></div>' % (w.t("colours.eyebrow"), w.t("colours.headline"), html, w.t("colours.footnote"))
    )
    bk.add(bk.B["ground"], inner)


def presets(bk):
    w = bk.w
    # The colour pairs of each ground, in the order of the grounds in the copy.
    pairs = [("var(--db)", "#fff", "#fff", "var(--tint)", "var(--o)", "var(--o)", "#fff"),
             ("var(--ch)", "var(--lg)", "#fff", "var(--tint)", "var(--o)", "var(--o)", "#fff"),
             ("var(--o)", "var(--db)", "#fff", "var(--db)", "var(--db)", "var(--db)", "#fff"),
             ("#fff", "#4A5878", "var(--ch)", "var(--deep)", "var(--o)", "var(--o)", "#fff"),
             ("var(--lg)", "#404C68", "var(--ch)", "#7A3B16", "#D5641E", "var(--o)", "#fff")]
    words = w.pairs("presets.ground")
    assert len(words) == len(pairs)
    ps = [(name, sub) + p for (name, sub), p in zip(words, pairs)]
    word, body, link, button = (w.t("presets.sample-" + k) for k in ("word", "body", "link", "button"))
    html = "".join(
        '<div style="background:%s;border-radius:14px;padding:40px 34px;height:600px;display:flex;flex-direction:column;%s">'
        '<div class="mont" style="font-weight:700;font-size:18px;letter-spacing:.16em;text-transform:uppercase;color:%s">%s</div>'
        '<div class="h" style="font-size:44px;color:%s;margin-top:18px">%s <span style="color:%s">%s</span></div>'
        '<p style="font-size:22px;line-height:1.5;color:%s;margin-top:18px">%s '
        '<span style="color:%s;text-decoration:underline;font-weight:600">%s</span></p>'
        '<div style="margin-top:auto"><span class="btn" style="font-size:22px;background:%s;color:%s;%s">%s</span></div></div>'
        % (bg, "border:1.5px solid rgba(255,255,255,.14)" if bg in ("var(--db)", "var(--ch)") else "",
           small, sub, head, name.upper().split()[0], large, word, txt, body, small, link, btn, lab,
           "box-shadow:none" if bg == "var(--o)" else "", button)
        for name, sub, bg, txt, head, small, large, btn, lab in ps)
    inner = (
        '<div class="pad"><div class="eb" style="font-size:24px">%s</div>'
        '<div class="h" style="font-size:80px;margin-top:26px">%s</div>'
        '<div class="grid" style="grid-template-columns:repeat(5,1fr);gap:24px;margin-top:56px">%s</div></div>'
        % (w.t("presets.eyebrow"), w.t("presets.headline"), html)
    )
    bk.add(bk.B["ground"], inner)


def contrast(bk):
    w = bk.w
    # Ground and text colour of each pair, in the order of the pairs in the copy.
    look = [("var(--o)", "#fff"), ("#fff", "var(--o)"), ("var(--db)", "var(--tint)"), ("#fff", "var(--deep)"), ("var(--db)", "var(--o)")]
    words = w.pairs("contrast.pair")
    assert len(words) == len(look)
    rows = [(t, d, bg, fg, w.t("contrast.sample")) for (t, d), (bg, fg) in zip(words, look)]
    html = "".join(
        '<div style="display:flex;align-items:center;gap:30px;padding:18px 0;border-bottom:1.5px solid rgba(255,255,255,.1)">'
        '<div style="width:120px;height:90px;border-radius:10px;background:%s;color:%s;display:flex;align-items:center;justify-content:center;font:800 46px Montserrat;border:1.5px solid rgba(255,255,255,.14)">%s</div>'
        '<div><div class="mont" style="font-weight:700;font-size:28px;color:#fff">%s</div><div class="small">%s</div></div></div>'
        % (bg, fg, a, t, d) for t, d, bg, fg, a in rows)
    nevers = w.items("contrast.never")
    inner = (
        '<div class="glow"></div>'
        + '<div class="pad" style="display:grid;grid-template-columns:1.1fr 1fr;gap:100px">'
          '<div><div class="eb" style="font-size:24px">%s</div>'
          '<div class="h" style="font-size:80px;margin-top:26px">%s</div>'
          '<div style="margin-top:40px">%s</div></div>'
          '<div style="padding-top:150px"><div class="h" style="font-size:40px">%s</div>'
          '<ul class="list no copy" style="margin-top:30px">%s</ul>'
          '<p class="copy" style="margin-top:40px">%s</p></div></div>'
        % (w.t("contrast.eyebrow"), w.t("contrast.headline"), html, w.t("contrast.never-heading"), lis(nevers), w.t("contrast.footnote"))
    )
    bk.add(bk.B["ground"], inner)


def typefaces(bk):
    t = bk.w.t
    inner = (
        '<div class="pad" style="display:grid;grid-template-columns:1.3fr 1fr;gap:90px">'
        '<div style="position:relative">'
        '<div class="eb" style="font-size:24px">%s</div>'
        '<div class="mont" style="font-weight:800;font-size:440px;line-height:.9;color:#fff;margin-top:30px;letter-spacing:-.03em">%s</div>'
        '<div class="h" style="font-size:72px;margin-top:20px">%s</div>'
        '<p class="copy" style="margin-top:14px">%s</p>'
        '<div class="mont" style="font-weight:700;font-size:34px;margin-top:26px;letter-spacing:.02em">%s</div></div>'
        '<div style="padding-top:120px">'
        '<div style="font-family:Open Sans;font-weight:600;font-size:200px;line-height:.9;color:var(--tint)">%s</div>'
        '<div class="h" style="font-size:56px;margin-top:30px">%s</div>'
        '<p class="copy" style="margin-top:14px">%s</p>'
        '<p style="font-size:30px;line-height:1.5;margin-top:30px;color:#fff">%s</p>'
        '<p class="small" style="margin-top:34px">%s</p></div></div>'
        % (t("typefaces.eyebrow"), t("typefaces.display-sample", hl='<span class="o" style="font-style:italic">%s</span>'),
           t("typefaces.display-name"), t("typefaces.display-use"), t("typefaces.display-alphabet"), t("typefaces.text-sample"),
           t("typefaces.text-name"), t("typefaces.text-use"), t("typefaces.text-line"), t("typefaces.footnote"))
    )
    bk.add(bk.B["ground"], inner)


def headline_formula(bk):
    t = bk.w.t
    rules = "".join('<div><div class="num" style="font-size:60px">%s</div><p class="copy" style="margin-top:8px">%s</p></div>' % r
                    for r in bk.w.pairs("formula.rule"))
    inner = (
        '<div class="glow"></div>'
        + '<div class="pad">'
          '<div style="position:relative;margin-top:10px">'
          '<div class="eb" style="font-size:26px">%s</div>'
          '<div class="h" style="font-size:150px;margin-top:34px">%s</div>'
          '<span class="sticker" style="position:absolute;left:720px;top:-26px;font-size:26px;transform:rotate(4deg)">%s</span>'
          '<span class="sticker" style="position:absolute;left:880px;top:420px;font-size:26px">%s</span></div>'
          '<div class="grid" style="grid-template-columns:repeat(4,1fr);gap:44px;margin-top:60px">%s</div></div>'
        % (t("formula.eyebrow"), t("formula.headline"), t("formula.italic-sticker"), t("formula.orange-sticker"), rules)
    )
    bk.add(bk.B["ground"], inner)


def type_scale(bk):
    w = bk.w
    # Size, weight and whether it is set in capitals, for each row in the order of the copy. The last row is the eyebrow.
    look = [(68, 800, True), (48, 800, True), (40, 800, True), (22, 700, False), (20, 400, False), (16, 400, False),
            (14, 400, False), (13, 600, True)]
    words = w.pairs("type-scale.row")
    assert len(words) == len(look)
    rows = [(n, m) + k for (n, m), k in zip(words, look)]
    caps, text = w.t("type-scale.display-sample"), w.t("type-scale.text-sample")
    html = "".join(
        '<div style="display:grid;grid-template-columns:220px 300px 1fr;align-items:baseline;padding:9px 0;border-bottom:1.5px solid rgba(74,88,120,.18)">'
        '<div class="mont" style="font-weight:700;font-size:22px;color:var(--deep);text-transform:uppercase;letter-spacing:.12em">%s</div>'
        '<div style="font-size:22px;color:#4A5878">%s</div>'
        '<div style="font-family:%s;font-weight:%d;font-size:%dpx;color:var(--ch);%s">%s</div></div>'
        % (n, m, "Montserrat" if up or w >= 700 else "Open Sans", w, int(sz * 1.3),
           "text-transform:uppercase;letter-spacing:%s" % (".12em" if i == len(rows) - 1 else "-.01em") if up else "",
           caps if up else text)
        for i, (n, m, sz, w, up) in enumerate(rows))
    inner = (
        '<div class="pad"><div class="eb" style="font-size:24px">%s</div>'
        '<div class="h" style="font-size:72px;margin-top:22px">%s</div>'
        '<div style="margin-top:36px">%s</div>'
        '<p class="small" style="margin-top:20px">%s</p></div>'
        % (bk.w.t("type-scale.eyebrow"), bk.w.t("type-scale.headline"), html, bk.w.t("type-scale.footnote"))
    )
    bk.add("wh", inner)


def motifs_slide(bk):
    w, h = 520, 312
    # The art of each tile, in the order of the tiles in the copy: "light" and "bar" are drawn in HTML.
    arts = [
        motifs.ascent(w, h, 50, 240, 150, steps=4, colour="#E8712A") + motifs.ascent(w, h, 360, 240, 170, steps=5, kind="chevrons"),
        motifs.contours(w, h, seed=4, rings=11, cx=0.75, cy=0.7),
        "light",
        motifs.connections(w, h, seed=5, dots=26, region=(0.05, 0.08, 0.95, 0.92)),
        motifs.slabs(w, h, corners=("tl",), length=w * 0.45, thick=h * 0.12) + motifs.peak(w, h, base=0.88, summit=(0.55, 0.35), seed=2, colour="#FFFFFF", opacity=0.5),
        "bar",
    ]
    words = bk.w.pairs("motifs.tile")
    assert len(words) == len(arts)
    tiles = [(t, d, art) for (t, d), art in zip(words, arts)]
    html = ""
    for t, d, art in tiles:
        if art == "light":
            body = ('<div style="position:absolute;inset:0;background:radial-gradient(260px 140px at 62% 0%,rgba(242,174,134,.7),rgba(242,174,134,0) 70%)"></div>'
                    '<div style="position:absolute;left:47%;top:-20px;width:110px;height:420px;transform-origin:top;transform:rotate(24deg);background:linear-gradient(180deg,rgba(232,113,42,.6),rgba(232,113,42,0));filter:blur(14px)"></div>'
                    '<div style="position:absolute;left:55%;top:-20px;width:120px;height:420px;transform-origin:top;transform:rotate(-4deg);background:linear-gradient(180deg,rgba(232,113,42,.55),rgba(232,113,42,0));filter:blur(14px)"></div>'
                    '<div style="position:absolute;left:62%;top:-20px;width:100px;height:420px;transform-origin:top;transform:rotate(-28deg);background:linear-gradient(180deg,rgba(232,113,42,.5),rgba(232,113,42,0));filter:blur(14px)"></div>')
        elif art == "bar":
            body = ('<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center"><div class="h" style="font-size:64px;text-align:center;line-height:1.15">%s</div></div>'
                    % bk.w.t("motifs.bar-sample", hl='<span class="bar">%s</span>'))
        else:
            body = svg(art, w, h)
        html += ('<div><div style="position:relative;height:%dpx;border-radius:14px;overflow:hidden;background:var(--db);border:1.5px solid rgba(255,255,255,.1)">%s</div>'
                 '<div class="h" style="font-size:30px;margin-top:20px">%s</div><p class="small" style="margin-top:4px">%s</p></div>' % (h - 80, body, t, d))
    inner = (
        '<div class="pad"><div class="eb" style="font-size:24px">%s</div>'
        '<div class="h" style="font-size:72px;margin-top:22px">%s</div>'
        '<div class="grid" style="grid-template-columns:repeat(3,1fr);gap:26px 40px;margin-top:34px">%s</div></div>'
        % (bk.w.t("motifs.eyebrow"), bk.w.t("motifs.headline"), html)
    )
    bk.add(bk.B["ground"], inner)


def devices(bk):
    b, t = bk.b, bk.w.t
    s1, s2, s3 = (md(s.text) for s in bk.w.secs("devices.sticker"))
    inner = (
        '<div class="glow"></div>'
        + '<div class="pad">'
          '<div class="eb" style="font-size:24px">%s</div>'
          '<div class="h" style="font-size:72px;margin-top:22px">%s</div>'
          '<div style="position:relative;height:640px;margin-top:40px">'
          # ticket
          '<div class="ticket" style="position:absolute;left:0;top:30px;width:560px;padding:44px 46px 40px">'
          '<span class="tag" style="font-size:18px;color:var(--tint)">%s</span>'
          '<div class="h" style="font-size:48px;margin-top:22px">%s</div>'
          '<p class="copy" style="margin-top:14px">%s</p>'
          '<div class="tear" style="margin:52px -46px 30px"><div class="notch" style="left:-23px;top:-24px"></div><div class="notch" style="right:-23px;top:-24px"></div></div>'
          '<span class="btn" style="font-size:24px">%s <span>\u2192</span></span>'
          '<p class="small" style="margin-top:16px">%s</p></div>'
          # photo card
          '<div style="position:absolute;left:640px;top:0;width:420px;height:560px;border-radius:14px;overflow:hidden;box-shadow:0 30px 70px rgba(0,0,0,.5)">'
          '<div class="ph" style="background-image:url(%svip_and_awards_03.jpg)"></div><div class="layer fade-card"></div>'
          '<div class="h" style="position:absolute;left:34px;top:34px;font-size:40px">%s</div>'
          '<p style="position:absolute;left:34px;bottom:30px;right:34px;font-size:22px;line-height:1.4">%s</p>'
          '<span class="sticker" style="position:absolute;right:20px;top:120px;font-size:22px">%s</span></div>'
          # stickers + rule + buttons
          '<div style="position:absolute;left:1140px;top:10px;width:540px">'
          '<div style="display:flex;gap:18px;flex-wrap:wrap"><span class="sticker" style="font-size:28px">%s</span>'
          '<span class="sticker dark" style="font-size:28px;transform:rotate(3deg);border:2px solid var(--o)">%s</span>'
          '<span class="sticker white" style="font-size:28px">%s</span></div>'
          '<p class="small" style="margin-top:18px">%s</p>'
          '<div class="rule" style="margin-top:56px"></div><div class="eb plain" style="font-size:22px;margin-top:18px">%s</div>'
          '<div style="margin-top:56px;display:flex;gap:20px"><span class="btn" style="font-size:24px">%s</span><span class="btn ghost" style="font-size:24px">%s</span></div>'
          '<p class="small" style="margin-top:16px">%s</p>'
          '<div class="mont" style="margin-top:56px;font-weight:700;font-size:20px;letter-spacing:.16em;text-transform:uppercase;color:var(--tint)">%s <span class="chev" style="transform:rotate(135deg);margin-left:10px"></span></div>'
          '<p class="small" style="margin-top:10px">%s</p></div>'
          '</div></div>'
        % (t("devices.eyebrow"), t("devices.headline"), t("devices.ticket-tag"), t("devices.ticket-title"), t("devices.ticket-body"),
           t("devices.ticket-button"), t("devices.ticket-caption"), P, t("devices.card-title"), t("devices.card-body"), t("devices.card-sticker"),
           s1, s2, s3, t("devices.sticker-caption"), t("devices.rule-eyebrow"), t("devices.button"), t("devices.second-button"),
           t("devices.button-caption"), t("devices.pull-link"), t("devices.pull-link-caption"))
    )
    bk.add(bk.B["ground"], inner)


def lineup(bk):
    # Size and colour of each act, in the order of the acts in the copy.
    look = [(74, "#fff"), (74, "var(--o)"), (60, "#fff"), (60, "var(--tint)"), (48, "#fff"), (48, "var(--o)"), (48, "#fff")]
    acts = bk.w.items("lineup.acts")
    assert len(acts) == len(look)
    names = [(n, s, c) for n, (s, c) in zip(acts, look)]
    sep = '<span style="color:var(--o);font-size:56px">/</span>'
    poster = (" " + sep + " ").join('<span style="font-size:%dpx;color:%s;white-space:nowrap">%s</span>' % (s, c, n.upper()) for n, s, c in names)
    row = lambda txt, d: ('<div style="white-space:nowrap;font:800 54px Montserrat;text-transform:uppercase;color:rgba(255,255,255,.14);transform:translateX(%dpx)">%s</div>' % (d, txt))
    marq = " \u00b7 ".join(bk.w.items("lineup.marquee") * 3)
    inner = (
        '<div class="glow"></div>'
        + '<div aria-hidden="true" style="position:absolute;left:0;right:0;top:60px">%s%s</div>' % (row(marq, -120), row(marq, -620))
        + '<div class="pad" style="top:300px">'
          '<div class="eb" style="font-size:24px">%s</div>'
          '<div class="h" style="margin-top:34px;line-height:1.12">%s</div>'
          '<p class="copy" style="margin-top:50px;max-width:1150px">%s</p></div>' % (bk.w.t("lineup.eyebrow"), poster, bk.w.t("lineup.body"))
    )
    bk.add(bk.B["ground"], inner)


def illustrations(bk, names):
    cells = "".join('<div style="display:flex;align-items:center;justify-content:center"><img src="assets/illus/%s.svg" style="width:118px;height:118px"></div>' % n for n in names)
    inner = (
        '<div class="pad" style="display:grid;grid-template-columns:560px 1fr;gap:70px">'
        '<div><div class="eb" style="font-size:24px">%s</div>'
        '<div class="h" style="font-size:72px;margin-top:22px">%s</div>'
        '<ul class="list copy" style="margin-top:40px">%s</ul></div>'
        '<div style="display:grid;grid-template-columns:repeat(7,1fr);grid-auto-rows:150px;gap:6px;align-content:start">%s</div></div>'
        % (bk.w.t("illustrations.eyebrow"), bk.w.t("illustrations.headline"), lis(bk.w.items("illustrations.points")), cells)
    )
    bk.add(bk.B["ground"], inner)


# Wide frames zoom in on the people so they read as a tall tile.
CROPS = {"outdoor_seating_01.jpg": "72% 95%/auto 200% no-repeat"}


def photo_shoot(bk):
    tiles = ["climb_recap_05.jpg", "joy_01.jpg", "crowds_02.jpg", "audience_at_stage_01.jpg", "exhibitor_01.jpg",
             "food_and_vendors_01.jpg", "outdoor_seating_01.jpg", "roundtable_and_workshops_01.jpg", "climb_recap_06.jpg"]
    wall = ('<div style="display:grid;grid-template-columns:repeat(4,1fr);grid-template-rows:repeat(3,1fr);gap:10px;position:absolute;right:0;top:0;width:1060px;height:960px">'
            '<div style="grid-column:1/3;grid-row:1/3;background:url(%s%s) center/cover"></div>' % (P, tiles[0])
            + "".join('<div style="background:url(%s%s) %s"></div>' % (P, t, CROPS.get(t, "center/cover")) for t in tiles[1:])
            + '</div>')
    inner = (
        wall
        + '<div style="position:absolute;left:0;top:0;bottom:0;width:980px;background:linear-gradient(90deg,var(--db) 78%,rgba(30,15,5,0))"></div>'
        + '<div class="pad" style="right:auto;width:630px">'
          '<div class="eb" style="font-size:24px">%s</div>'
          '<div class="h" style="font-size:80px;margin-top:22px">%s</div>'
          '<ul class="list copy" style="margin-top:36px;font-size:22px">%s</ul></div>'
          % (bk.w.t("photo-shoot.eyebrow"), bk.w.t("photo-shoot.headline"), lis(bk.w.items("photo-shoot.points")))
        + '<span class="sticker" style="position:absolute;left:1000px;top:590px;font-size:28px">%s</span>' % bk.w.t("photo-shoot.sticker")
    )
    bk.add("", inner)


def photo_fades(bk):
    # Fade, photo and highlight colour of each tile, in the order of the fades in the copy.
    look = [("fade-brown", "stage_speakers_03.jpg", None), ("fade-heat", "crowds_03.jpg", None),
            ("fade-orange", "climbteam_01.jpg" if bk.b == "ClimbGroup" else "climbteam_02.jpg", '<span style="color:var(--db)">%s</span>')]
    samples, words = bk.w.secs("fades.sample"), bk.w.pairs("fades.fade")
    assert len(samples) == len(words) == len(look)
    fades = [(cls, n, d, f, md(s.text, **({"hl": hl} if hl else {}))) for (cls, f, hl), (n, d), s in zip(look, words, samples)]
    html = "".join(
        '<div><div style="position:relative;height:520px;border-radius:14px;overflow:hidden">'
        '<div class="ph" style="background-image:url(%s%s)"></div><div class="layer %s"></div>'
        '<div class="h" style="position:absolute;left:40px;bottom:44px;font-size:52px;width:330px">%s</div></div>'
        '<div class="h" style="font-size:32px;margin-top:22px">%s</div><p class="small" style="margin-top:6px">%s</p></div>'
        % (P, f, cls, hl, n, d) for cls, n, d, f, hl in fades)
    inner = (
        '<div class="pad"><div class="eb" style="font-size:24px">%s</div>'
        '<div class="h" style="font-size:72px;margin-top:22px">%s</div>'
        '<div class="grid" style="grid-template-columns:repeat(3,1fr);gap:40px;margin-top:44px">%s</div>'
        '<p class="small" style="margin-top:26px">%s</p></div>' % (bk.w.t("fades.eyebrow"), bk.w.t("fades.headline"), html, bk.w.t("fades.footnote"))
    )
    bk.add(bk.B["ground"], inner)


def photo_rules(bk):
    inner = (
        '<div style="position:absolute;left:0;top:0;bottom:0;width:900px;overflow:hidden">'
        + photo("stage_speakers_02.jpg", "", "center 30%")
        + '<div class="layer" style="background:linear-gradient(90deg,rgba(30,15,5,0) 55%,var(--db)),linear-gradient(180deg,rgba(30,15,5,0) 72%,var(--db) 90%)"></div></div>'
        + '<div class="pad" style="left:auto;width:820px">'
          '<div class="eb" style="font-size:24px;justify-content:flex-end">%s</div>'
          '<div class="h" style="font-size:80px;margin-top:22px;text-align:right">%s</div>'
          '<ul class="list copy" style="margin-top:40px">%s</ul>'
          '<div class="h" style="font-size:36px;margin-top:40px">%s</div>'
          '<ul class="list no copy" style="margin-top:20px">%s</ul></div>'
          % (bk.w.t("photo-rules.eyebrow"), bk.w.t("photo-rules.headline"), lis(bk.w.items("photo-rules.points")),
             bk.w.t("photo-rules.never-heading"), lis(bk.w.items("photo-rules.never")))
    )
    bk.add("", inner)


def motion(bk):
    toks = [(n, v, d) for n, (v, d) in bk.w.lines("motion.speed")]
    bars = "".join(
        '<div style="display:grid;grid-template-columns:150px 120px 1fr;align-items:center;gap:20px;margin-bottom:22px">'
        '<div class="mont" style="font-weight:700;font-size:24px;text-transform:uppercase;letter-spacing:.1em">%s</div>'
        '<div class="mont" style="font-weight:800;font-size:28px;color:var(--o)">%s</div>'
        '<div><div style="height:16px;border-radius:8px;background:linear-gradient(90deg,var(--o),rgba(232,113,42,.25));width:%dpx"></div><div class="small" style="margin-top:6px">%s</div></div></div>'
        % (n, v, int(v[:-2]) * 0.9 + 30, d) for n, v, d in toks)
    # rise diagram
    steps = "".join('<div style="position:absolute;left:%dpx;bottom:%dpx;width:150px;height:110px;border-radius:14px;background:var(--ch);opacity:%.2f;border:1.5px solid rgba(255,255,255,.12)"></div>'
                    % (i * 175, [0, 26, 44, 52][i], [0.25, 0.5, 0.8, 1][i]) for i in range(4))
    inner = (
        '<div class="glow"></div>'
        + '<div class="pad" style="display:grid;grid-template-columns:1.05fr 1fr;gap:80px">'
          '<div><div class="eb" style="font-size:24px">%s</div>'
          '<div class="h" style="font-size:62px;margin-top:22px">%s</div>'
          '<ul class="list copy" style="margin-top:40px">%s</ul></div>'
          '<div style="padding-top:40px"><div style="position:relative;height:220px;margin-bottom:60px">%s'
          '<span class="sticker" style="position:absolute;left:560px;top:0;font-size:22px">%s</span></div>%s'
          '<p class="small" style="margin-top:20px">%s</p></div></div>'
        % (bk.w.t("motion.eyebrow"), bk.w.t("motion.headline"), lis(bk.w.items("motion.points")), steps, bk.w.t("motion.sticker"), bars,
           bk.w.t("motion.footnote"))
    )
    bk.add(bk.B["ground"], inner)


def digital_ui(bk):
    t = bk.w.t
    inner = (
        '<div class="pad">'
        '<div class="eb" style="font-size:24px">%s</div>'
        '<div class="h" style="font-size:66px;margin-top:22px">%s</div>'
        '<div class="grid" style="grid-template-columns:1fr 1fr 1fr;gap:40px;margin-top:56px">'
        '<div class="card" style="padding:44px">'
        '<div class="h" style="font-size:32px">%s</div>'
        '<div style="margin-top:34px;display:flex;flex-direction:column;gap:22px;align-items:flex-start">'
        '<span class="btn" style="font-size:24px">%s</span>'
        '<span class="btn" style="font-size:24px;background:var(--ot);transform:translateY(-2px)">%s</span>'
        '<span class="btn ghost" style="font-size:24px">%s</span></div>'
        '<p class="small" style="margin-top:26px">%s</p></div>'
        '<div class="card" style="padding:44px">'
        '<div class="h" style="font-size:32px">%s</div>'
        '<div style="margin-top:34px;display:flex;gap:26px;align-items:center">'
        '<span class="btn" style="font-size:24px;outline:3px solid var(--tint);outline-offset:3px">%s</span>'
        '<span class="tag" style="font-size:20px;color:var(--tint)">%s <span style="display:inline-block;width:10px;height:10px;border-radius:50%%;background:var(--o);margin-left:8px"></span></span></div>'
        '<ul class="list small" style="margin-top:30px">%s</ul></div>'
        '<div class="card" style="padding:44px">'
        '<div class="h" style="font-size:32px">%s</div>'
        '<div style="margin-top:34px;display:flex;gap:22px;align-items:flex-end">'
        '<div style="width:90px;height:90px;border-radius:10px;border:3px solid var(--tint)"></div>'
        '<div style="width:120px;height:120px;border-radius:14px;background:var(--o)"></div>'
        '<div style="width:170px;height:64px;border-radius:999px;border:3px solid #fff"></div></div>'
        '<ul class="list small" style="margin-top:30px">%s</ul></div></div>'
        '<p class="copy" style="margin-top:44px">%s</p></div>'
        % (t("digital.eyebrow"), t("digital.headline"), t("digital.buttons-title"), t("digital.button"), t("digital.button"),
           t("digital.second-button"), t("digital.buttons-caption"), t("digital.focus-title"), t("digital.focus-button"),
           t("digital.selected-tag"), lis(bk.w.items("digital.focus-points")), t("digital.shape-title"),
           lis(bk.w.items("digital.shape-points")), t("digital.footnote"))
    )
    bk.add(bk.B["ground"], inner)


def tickets(bk):
    kinds = ["closed", "open", "next", "final"]
    words = bk.w.lines("tickets.release")
    assert len(words) == len(kinds)
    caps = [(state, nm, price, k) for (nm, (state, price)), k in zip(words, kinds)]
    html = ""
    for i, (state, nm, price, k) in enumerate(caps):
        hgt = 170 + i * 50
        if k == "closed":
            capst = "background:#5a5550;"
        elif k == "open":
            capst = "background:var(--o);box-shadow:0 0 50px rgba(232,113,42,.55);"
        else:
            capst = "border:3px dashed rgba(255,255,255,.5);"
        html += ('<div style="display:flex;flex-direction:column;justify-content:flex-end;align-items:center;position:relative">'
                 '%s<div style="width:100%%;height:%dpx;border-radius:14px 14px 0 0;%s"></div>'
                 '<div style="width:28px;height:28px;border-radius:50%%;background:%s;margin-top:-14px;position:relative;z-index:2;%s"></div>'
                 '<div class="mont" style="font-weight:700;font-size:24px;margin-top:24px;%s">%s</div>'
                 '<div class="mont" style="font-weight:800;font-size:44px;margin-top:6px;%s">%s</div>'
                 '<div class="mont" style="font-weight:700;font-size:20px;letter-spacing:.14em;text-transform:uppercase;margin-top:6px;color:%s">%s</div></div>'
                 % ('<div style="position:absolute;top:-80px;background:#fff;color:var(--db);font:700 20px Montserrat;padding:10px 16px;border-radius:10px;white-space:nowrap">%s</div>' % bk.w.t("tickets.left") if k == "open" else "",
                    hgt, capst, "var(--o)" if k in ("closed", "open") else "var(--db)",
                    "box-shadow:0 0 0 8px rgba(232,113,42,.3)" if k == "open" else ("border:3px solid rgba(255,255,255,.5)" if k not in ("closed",) else ""),
                    "opacity:.6" if k == "closed" else "", nm,
                    "text-decoration:line-through;opacity:.6" if k == "closed" else ("color:var(--o)" if k == "open" else ""), price,
                    "var(--o)" if k == "open" else "rgba(255,255,255,.7)", state))
    rail = '<div style="position:absolute;left:0;right:0;bottom:155px;height:6px;background:linear-gradient(90deg,var(--o) 0 37%,rgba(255,255,255,.3) 37%)"></div>'
    inner = (
        '<div class="glow"></div>'
        + '<div class="pad" style="display:grid;grid-template-columns:640px 1fr;gap:90px">'
          '<div><div class="eb" style="font-size:24px">%s</div>'
          '<div class="h" style="font-size:76px;margin-top:22px">%s</div>'
          '<ul class="list copy" style="margin-top:36px">%s</ul></div>'
          '<div style="position:relative;padding-top:120px"><div style="position:relative;display:grid;grid-template-columns:repeat(4,1fr);gap:26px;height:620px;align-items:end">%s%s</div>'
          '<span class="sticker white" style="position:absolute;right:0;top:20px;font-size:24px">%s</span></div></div>'
        % (bk.w.t("tickets.eyebrow"), bk.w.t("tickets.headline"), lis(bk.w.items("tickets.points")), html, rail, bk.w.t("tickets.sticker"))
    )
    bk.add(bk.B["ground"], inner)


def themes27(bk):
    (e1, t1), (e2, t2) = bk.w.pairs("themes.theme")
    (h1, l1), (h2, l2) = t1.split("<br><br>"), t2.split("<br><br>")
    inner = (
        '<div style="position:absolute;left:0;top:0;bottom:0;width:960px;overflow:hidden">'
        + photo("exhibitor_02.jpg", "fade-bottom", "center 30%")
        + '<div style="position:absolute;left:100px;right:80px;bottom:120px"><div class="eb" style="font-size:24px">%s</div>'
          '<div class="h" style="font-size:104px;margin-top:20px">%s</div>'
          '<p class="lead" style="margin-top:20px">%s</p></div></div>' % (e1, h1, l1)
        + '<div style="position:absolute;right:0;top:0;bottom:0;width:960px;overflow:hidden">'
        + photo("stage_speakers_04.jpg", "fade-bottom", "center 40%")
        + '<div class="glow"></div><div style="position:absolute;left:80px;right:100px;bottom:120px"><div class="eb" style="font-size:24px">%s</div>'
          '<div class="h" style="font-size:104px;margin-top:20px">%s</div>'
          '<p class="lead" style="margin-top:20px">%s</p></div></div>' % (e2, h2, l2)
        + '<div style="position:absolute;left:958px;top:0;bottom:0;width:4px;background:var(--o)"></div>'
        + '<span class="sticker" style="position:absolute;left:800px;top:120px;font-size:30px">%s</span>' % bk.w.t("themes.sticker")
    )
    bk.add("", inner)


def share_kit(bk):
    def tile(role, line, ph, rot):
        return ('<div style="position:relative;width:330px;height:430px;flex:none;border-radius:14px;overflow:hidden;transform:rotate(%sdeg);box-shadow:0 30px 70px rgba(0,0,0,.5)">'
                '<div class="ph" style="background-image:url(%s%s);background-position:center 25%%;bottom:40%%"></div>'
                '<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(30,15,5,0) 12%%,rgba(30,15,5,.9) 40%%,var(--db) 50%%)"></div>'
                '<div style="position:absolute;left:42px;top:42px">%s</div>'
                '<div style="position:absolute;left:30px;right:24px;top:190px"><span class="sticker" style="font-size:15px">%s</span>'
                '<div class="h" style="font-size:34px;margin-top:16px">%s</div>'
                '<div style="font-size:15px;margin-top:10px;color:var(--tint)">%s</div></div>'
                '<div style="position:absolute;left:20px;right:20px;bottom:18px;display:flex;align-items:center;justify-content:flex-end;background:var(--ch);border-radius:10px;padding:10px 12px">'
                '<span style="background:var(--o);font:800 13px Montserrat;padding:6px 10px;border-radius:6px;text-transform:uppercase;color:var(--db)">%s</span></div></div>'
                % (rot, P, ph, logo("Climb27", "reversed-dark", h=28), role, line, bk.w.t("share-kit.name"), bk.w.t("share-kit.web")))
    (r1, l1), (r2, l2), (r3, l3) = bk.w.pairs("share-kit.tile")
    inner = (
        '<div class="glow"></div>'
        + '<div class="pad" style="display:grid;grid-template-columns:580px 1fr;gap:40px">'
          '<div><div class="eb" style="font-size:24px">%s</div>'
          '<div class="h" style="font-size:76px;margin-top:22px">%s</div>'
          '<ul class="list copy" style="margin-top:36px">%s</ul></div>'
          '<div style="display:flex;gap:28px;align-items:center;justify-content:center;padding-top:60px">%s%s%s</div></div>'
        % (bk.w.t("share-kit.eyebrow"), bk.w.t("share-kit.headline"), lis(bk.w.items("share-kit.points")),
           tile(r1, l1, "crowds_04.jpg", "-2"), tile(r2, l2, "climb_recap_01.jpg", "1"), tile(r3, l3, "meetings_03.jpg", "3"))
    )
    bk.add("", inner)


def where_group(bk):
    t = bk.w.t
    yes, no = bk.w.items("where.yes"), bk.w.items("where.no")
    inner = (
        svg(motifs.slabs(W, H, corners=("tr",), length=W * 0.22, thick=H * 0.06))
        + '<div class="glow"></div>'
        + '<div class="pad" style="display:grid;grid-template-columns:1fr 1fr;gap:100px">'
          '<div><div class="eb" style="font-size:24px">%s</div>'
          '<div class="h" style="font-size:84px;margin-top:22px">%s</div>'
          '<p class="lead" style="margin-top:30px">%s</p></div>'
          '<div style="padding-top:20px"><div class="h" style="font-size:40px">%s</div>'
          '<ul class="list copy" style="margin-top:24px">%s</ul>'
          '<div class="h" style="font-size:40px;margin-top:40px">%s</div>'
          '<ul class="list no copy" style="margin-top:24px">%s</ul></div></div>'
        % (t("where.eyebrow"), t("where.headline"), t("where.lead"), t("where.yes-heading"), lis(yes), t("where.no-heading"), lis(no))
    )
    bk.add("ch", inner)


def documents(bk):
    t = bk.w.t

    def page(cover):
        if cover:
            return ('<div style="position:relative;width:400px;height:566px;border-radius:6px;overflow:hidden;background:var(--db);box-shadow:0 30px 70px rgba(0,0,0,.55);transform:rotate(-3deg)">'
                    '<div class="ph" style="background-image:url(%sexhibitor_03.jpg);bottom:45%%"></div>'
                    '<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(30,15,5,.2),var(--db) 56%%)"></div>'
                    '%s<div style="position:absolute;left:40px;top:40px">%s</div>'
                    '<div style="position:absolute;left:28px;right:28px;top:330px"><span class="sticker" style="font-size:14px">%s</span>'
                    '<div class="h" style="font-size:40px;margin-top:14px">%s</div>'
                    '<div style="font-size:14px;margin-top:12px;color:var(--lg)">%s</div></div></div>'
                    % (P, svg(motifs.slabs(400, 566, corners=("br",), length=150, thick=34), 400, 566), logo("ClimbGroup", "reversed-dark", h=26),
                       t("documents.cover-sticker"), t("documents.cover-title"), t("documents.cover-line")))
        return ('<div style="position:relative;width:400px;height:566px;border-radius:6px;overflow:hidden;background:#fff;box-shadow:0 30px 70px rgba(0,0,0,.55);transform:rotate(2deg);color:#4A5878;padding:40px 36px">'
                '<div style="display:flex;justify-content:space-between;align-items:center">%s<span style="font:700 11px Montserrat;letter-spacing:.14em;color:var(--deep)">%s</span></div>'
                '<div style="width:46px;height:5px;border-radius:3px;background:var(--o);margin-top:40px"></div>'
                '<div class="h" style="font-size:26px;color:var(--ch);margin-top:14px">%s</div>'
                '<div style="font-size:13px;line-height:1.6;margin-top:12px">%s</div>'
                '<div style="height:8px;background:#E9E9E9;border-radius:4px;margin-top:22px"></div><div style="height:8px;background:#E9E9E9;border-radius:4px;margin-top:10px;width:80%%"></div>'
                '<div style="height:8px;background:#E9E9E9;border-radius:4px;margin-top:10px;width:90%%"></div>'
                '<div class="h" style="font-size:26px;color:var(--ch);margin-top:30px">%s</div>'
                '<div style="height:8px;background:#E9E9E9;border-radius:4px;margin-top:16px"></div><div style="height:8px;background:#E9E9E9;border-radius:4px;margin-top:10px;width:70%%"></div>'
                '<div style="position:absolute;left:36px;right:36px;bottom:28px;border-top:1px solid #ddd;padding-top:12px;font-size:13px;color:#555">%s</div></div>'
                % (logo("ClimbGroup", "full-colour-light", h=22), t("documents.page-label"), t("documents.page-heading"), t("documents.page-body"),
                   t("documents.page-heading-2"), t("documents.page-footer")))
    inner = (
        '<div class="glow"></div>'
        + '<div class="pad" style="display:grid;grid-template-columns:1fr 1fr;gap:80px;align-items:center">'
          '<div><div class="eb" style="font-size:24px">%s</div>'
          '<div class="h" style="font-size:80px;margin-top:22px">%s</div>'
          '<ul class="list copy" style="margin-top:36px">%s</ul></div>'
          '<div style="display:flex;gap:30px;justify-content:center">%s%s</div></div>'
        % (t("documents.eyebrow"), t("documents.headline"), lis(bk.w.items("documents.points")), page(True), page(False))
    )
    bk.add("ch", inner)


def signature(bk):
    b, t = bk.b, bk.w.t
    inner = (
        '<div class="pad" style="display:grid;grid-template-columns:600px 1fr;gap:80px;align-items:center">'
        '<div><div class="eb" style="font-size:24px">%s</div>'
        '<div class="h" style="font-size:76px;margin-top:22px">%s</div>'
        '<ul class="list copy" style="margin-top:36px">%s</ul></div>'
        '<div style="background:#fff;border-radius:14px;padding:50px 54px;color:#4A5878;box-shadow:0 30px 70px rgba(0,0,0,.45)">'
        '<div style="font-size:22px">%s</div>'
        '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-top:22px">'
        '<div><div class="mont" style="font-weight:700;font-size:30px;color:var(--ch)">%s</div>'
        '<div style="font-size:20px;margin-top:4px">%s</div>'
        '<div style="font-size:20px;margin-top:16px;color:var(--deep);text-decoration:underline;font-weight:600">%s</div>'
        '<div style="font-size:18px;margin-top:14px">%s</div></div>'
        '<div style="text-align:right">%s'
        '<div style="display:flex;gap:8px;margin-top:34px;justify-content:flex-end">%s</div></div></div>'
        '<div style="margin-top:30px;height:150px;border-radius:10px;overflow:hidden;position:relative">'
        '<div class="ph" style="background-image:url(%sclimb_recap_02.jpg)"></div><div class="layer fade-heat"></div>'
        '<div class="h" style="position:absolute;left:30px;top:30px;font-size:40px">%s</div>'
        '<span class="btn" style="position:absolute;left:30px;bottom:22px;font-size:20px;padding:8px 18px">%s</span></div>'
        '<div style="font-size:14px;margin-top:18px;color:#555">%s</div></div></div>'
        % (t("signature.eyebrow"), t("signature.headline"), lis(bk.w.items("signature.points")), t("signature.sign-off"),
           t("signature.name"), t("signature.role"), t("signature.link"), t("signature.contact"),
           logo(b, "full-colour-light", w=230),
           "".join('<span style="display:inline-block;width:34px;height:34px;border:2px solid var(--o);border-radius:8px;padding:6px">%s</span>' % open(os.path.join(HERE, "assets/social/%s.svg" % g)).read().replace('<svg ', '<svg fill="#C55308" width="18" height="18" ')
                   for g in ("linkedin", "instagram", "tiktok", "x", "bluesky")), P,
           t("signature.banner-headline"), t("signature.banner-button"), t("signature.legal"))
    )
    bk.add(bk.B["ground"] or "", inner)


def voice_lines(bk):
    lines = bk.w.pairs("voice-lines.line")
    html = "".join('<div><div class="num" style="font-size:110px">0%d</div><div class="h" style="font-size:44px;margin-top:16px">%s</div>'
                   '<p class="copy" style="margin-top:14px">%s</p></div>' % (i + 1, t, d) for i, (t, d) in enumerate(lines))
    inner = (
        '<div class="glow"></div>'
        + '<div class="pad"><div class="eb" style="font-size:24px">%s</div>'
          '<div class="h" style="font-size:96px;margin-top:22px">%s</div>'
          '<div class="grid" style="grid-template-columns:repeat(4,1fr);gap:56px;margin-top:70px">%s</div></div>'
          % (bk.w.t("voice-lines.eyebrow"), bk.w.t("voice-lines.headline"), html)
        + '<div style="position:absolute;left:0;right:0;bottom:130px;white-space:nowrap;font:800 italic 92px/1 Montserrat Outline,Montserrat;text-transform:uppercase;color:transparent;-webkit-text-stroke:2px rgba(242,174,134,.35);transform:translateX(-260px)">'
          '%s</div>' % bk.w.t("voice-lines.marquee")
    )
    bk.add(bk.B["ground"], inner)


def voice_rules(bk):
    signs = bk.w.secs("voice-rules.sign")
    glyphs = [GLYPHS.get(s["glyph"], s["glyph"]) for s in signs]
    big = [(md(s.title), md(s.text)) for s in signs]
    rules = bk.w.items("voice-rules.points")
    html = "".join('<div style="text-align:center"><div style="width:150px;height:150px;margin:0 auto;border-radius:50%%;border:6px solid var(--o);position:relative">'
                   '<div style="position:absolute;left:50%%;top:50%%;width:170px;height:6px;background:var(--o);transform:translate(-50%%,-50%%) rotate(-45deg)"></div>'
                   '<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font:800 64px Montserrat;color:#fff">%s</div></div>'
                   '<div class="h" style="font-size:32px;margin-top:22px">%s</div><p class="small" style="margin-top:6px">%s</p></div>'
                   % (g, t, d) for g, (t, d) in zip(glyphs, big))
    inner = (
        '<div class="pad" style="display:grid;grid-template-columns:1fr 1fr;gap:90px">'
        '<div><div class="eb" style="font-size:24px">%s</div>'
        '<div class="h" style="font-size:84px;margin-top:22px">%s</div>'
        '<div class="grid" style="grid-template-columns:repeat(3,1fr);gap:30px;margin-top:70px">%s</div></div>'
        '<ul class="list copy" style="padding-top:40px">%s</ul></div>'
        % (bk.w.t("voice-rules.eyebrow"), bk.w.t("voice-rules.headline"), html, lis(rules))
    )
    bk.add(bk.B["ground"], inner)


def rewrites(bk):
    rows = pairs(texts(bk, "rewrites.before"), texts(bk, "rewrites.after"))
    html = "".join(
        '<div style="display:grid;grid-template-columns:1fr 80px 1fr;align-items:center;padding:24px 0;border-bottom:1.5px solid rgba(74,88,120,.18)">'
        '<div style="font-size:26px;color:#666;text-decoration:line-through;text-decoration-color:var(--o);text-decoration-thickness:3px">%s</div>'
        '<div style="text-align:center"><span class="chev" style="width:22px;height:22px;border-width:6px;border-color:var(--o)"></span></div>'
        '<div class="mont" style="font-weight:700;font-size:28px;color:var(--ch);line-height:1.3">%s</div></div>' % (a, b) for a, b in rows)
    inner = (
        '<div class="pad"><div class="eb" style="font-size:24px">%s</div>'
        '<div class="h" style="font-size:72px;margin-top:22px">%s</div>'
        '<div style="display:grid;grid-template-columns:1fr 80px 1fr;margin-top:40px" class="mont"><div style="font-weight:700;font-size:20px;letter-spacing:.14em;color:#555">%s</div><div></div>'
        '<div style="font-weight:700;font-size:20px;letter-spacing:.14em;color:var(--deep)">%s</div></div>%s</div>'
        % (bk.w.t("rewrites.eyebrow"), bk.w.t("rewrites.headline"), bk.w.t("rewrites.before-label"), bk.w.t("rewrites.after-label"), html)
    )
    bk.add("wh", inner)


def words(bk):
    w = bk.w
    rows = pairs(texts(bk, "words.use"), texts(bk, "words.instead"))
    html = "".join('<div style="display:grid;grid-template-columns:1fr 1fr;padding:15px 0;border-bottom:1.5px solid rgba(255,255,255,.1)">'
                   '<div class="mont" style="font-weight:700;font-size:26px;color:#fff">%s</div><div style="font-size:24px;color:rgba(255,255,255,.65);text-decoration:line-through;text-decoration-color:var(--o)">%s</div></div>' % (a, b) for a, b in rows)
    own = w.items("words.own")
    inner = (
        '<div class="glow"></div>'
        + '<div class="pad" style="display:grid;grid-template-columns:1fr 1fr;gap:100px">'
          '<div><div class="eb" style="font-size:24px">%s</div>'
          '<div class="h" style="font-size:72px;margin-top:22px;margin-bottom:34px">%s</div>%s</div>'
          '<div><div class="eb" style="font-size:24px">%s</div>'
          '<div style="margin-top:40px;display:flex;flex-direction:column;gap:26px">%s</div>'
          '<p class="copy" style="margin-top:44px">%s</p></div></div>'
        % (w.t("words.eyebrow"), w.t("words.headline"), html, w.t("words.own-eyebrow"), "".join('<div class="h" style="font-size:%dpx;line-height:1.05">%s</div>' % (54 if i < 2 else 42, ('<span class="o">%s</span>' % l) if i == 0 else l) for i, l in enumerate(own)), w.t("words.programmes"))
    )
    bk.add(bk.B["ground"], inner)


def audiences(bk):
    w = bk.w
    aud = w.pairs("audiences.audience")
    html = "".join('<div class="card" style="padding:30px 32px"><div class="h" style="font-size:30px">%s</div><p class="small" style="margin-top:8px;color:var(--tint)">%s</p></div>' % (a, t) for a, t in aud)
    inner = (
        '<div class="pad" style="display:grid;grid-template-columns:620px 1fr;gap:70px">'
        '<div><div class="eb" style="font-size:24px">%s</div>'
        '<div class="h" style="font-size:80px;margin-top:22px">%s</div>'
        '<p class="copy" style="margin-top:36px">%s</p>'
        '<p class="copy" style="margin-top:24px">%s</p></div>'
        '<div class="grid" style="grid-template-columns:repeat(3,1fr);gap:20px;align-content:start;padding-top:20px">%s</div></div>'
        % (w.t("audiences.eyebrow"), w.t("audiences.headline"), w.t("audiences.intro"), w.t("audiences.every"), html)
    )
    bk.add(bk.B["ground"], inner)


def print_merch(bk):
    b, t = bk.b, bk.w.t
    inner = (
        '<div class="pad" style="display:grid;grid-template-columns:1fr 1fr;gap:90px">'
        '<div><div class="eb" style="font-size:24px">%s</div>'
        '<div class="h" style="font-size:76px;margin-top:22px">%s</div>'
        '<ul class="list copy" style="margin-top:36px">%s</ul></div>'
        '<div style="position:relative">'
        '<div style="position:absolute;left:-10px;top:500px;width:250px;height:356px;background:var(--db);border-radius:6px;box-shadow:0 30px 70px rgba(0,0,0,.5);transform:rotate(-5deg);z-index:2;overflow:hidden">'
        '<div class="ph" style="background-image:url(%s%s);top:84px;bottom:36%%;background-position:center 20%%"></div><div style="position:absolute;inset:84px 0 0;background:linear-gradient(180deg,var(--db),rgba(30,15,5,0) 12%%,rgba(30,15,5,0) 45%%,var(--db) 72%%)"></div>'
        '<div style="position:absolute;left:32px;top:30px">%s</div>'
        '<div class="h" style="position:absolute;left:32px;bottom:56px;font-size:32px">%s</div>'
        '<div style="position:absolute;left:32px;bottom:26px;font:700 13px Montserrat;color:var(--tint)">%s</div></div>'
        # Totes: a white canvas bag in Dark Brown and orange, a Dark Brown bag in orange and White. Two colours each.
        '<div style="position:absolute;left:440px;top:150px;width:330px;height:380px;transform:rotate(6deg)">'
        '<div style="position:absolute;left:62px;top:-104px;width:206px;height:150px;border:16px solid var(--o);border-bottom:0;border-radius:110px 110px 0 0"></div>'
        '<div style="position:absolute;inset:0;background:var(--db);border-radius:6px 6px 14px 14px;box-shadow:0 30px 70px rgba(0,0,0,.6),inset 0 0 0 2px rgba(255,255,255,.06);overflow:hidden">'
        '<div style="position:absolute;left:-30px;right:-30px;top:30px;font:italic 800 96px/0.86 \'Montserrat Outline\',Montserrat;color:transparent;-webkit-text-stroke:2px var(--o);letter-spacing:-.04em;white-space:nowrap;transform:rotate(-8deg)">%s</div>'
        '<div class="h" style="position:absolute;left:30px;bottom:74px;font-size:46px;line-height:.95;color:#fff">%s</div>'
        '<div style="position:absolute;left:30px;bottom:30px">%s</div></div></div>'
        '<div style="position:absolute;left:30px;top:120px;width:380px;height:440px;transform:rotate(-3deg)">'
        '<div style="position:absolute;left:78px;top:-118px;width:224px;height:166px;border:18px solid var(--lg);border-bottom:0;border-radius:120px 120px 0 0"></div>'
        '<div style="position:absolute;inset:0;background:var(--w);border-radius:6px 6px 16px 16px;box-shadow:0 34px 80px rgba(0,0,0,.65);overflow:hidden">'
        '<div style="position:absolute;left:-40px;top:22px;font:800 64px/0.9 \'Montserrat Outline\',Montserrat;color:transparent;-webkit-text-stroke:2px var(--o);letter-spacing:-.03em;white-space:nowrap">%s</div>'
        '<div class="h" style="position:absolute;left:34px;top:210px;font-size:64px;line-height:.9;color:var(--db)">%s</div>'
        '<img src="assets/illus/high-five.svg" style="position:absolute;right:20px;top:196px;width:132px;height:132px;transform:rotate(10deg);--doodle-ground:var(--w)">'
        '<div style="position:absolute;left:34px;bottom:26px">%s</div></div>'
        '<span class="sticker" style="position:absolute;right:-26px;top:-20px;font-size:22px;transform:rotate(6deg)">%s</span></div>'
        '<div style="position:absolute;left:280px;bottom:60px;width:500px;height:110px;border-radius:12px;z-index:1;background:repeating-linear-gradient(90deg,var(--o) 0 140px,var(--o) 140px 280px);display:flex;align-items:center;gap:40px;padding:0 36px;overflow:hidden;transform:rotate(-1deg);box-shadow:0 20px 50px rgba(0,0,0,.4)">%s%s</div>'
        '<p class="small" style="position:absolute;left:290px;bottom:10px">%s</p></div></div>'
        % (t("print.eyebrow"), t("print.headline"), lis(bk.w.items("print.points")),
           P, "climbteam_02.jpg" if b == "ClimbGroup" else "joy_03.jpg", logo(b, "reversed-dark", h=30), t("print.poster-headline"), t("print.poster-web"),
           t("print.dark-tote-pattern"), t("print.dark-tote-headline"), logo(b, "mono-white", h=24),
           t("print.white-tote-pattern"), t("print.white-tote-headline", em='<em style="color:var(--ot)">%s</em>'), logo(b, "full-colour-light", h=24),
           t("print.tote-sticker"), logo(b, "mono-white", h=32), logo(b, "mono-dark", h=32), t("print.lanyard-caption"))
    )
    bk.add(bk.B["ground"], inner)


def video(bk):
    t = bk.w.t
    inner = (
        photo("climb_stage_region.jpg", "fade-hero", "center 30%")
        + '<div class="glow"></div>'
        + '<div style="position:absolute;left:120px;top:110px;right:120px;bottom:140px;border:2px solid rgba(255,255,255,.25);border-radius:6px"></div>'
        + '<div style="position:absolute;left:150px;top:140px;font:700 16px Montserrat;letter-spacing:.14em;color:rgba(255,255,255,.7)">%s</div>' % t("video.safe-label")
        + '<div style="position:absolute;right:150px;top:140px;opacity:.6">%s</div>' % logo(bk.b, "icon-monogram-on-ground", w=60)
        + '<div style="position:absolute;left:180px;top:200px;width:900px">'
          '<div class="eb" style="font-size:24px">%s</div>'
          '<div class="h" style="font-size:84px;margin-top:22px">%s</div>'
          '<ul class="list copy" style="margin-top:34px;color:#fff">%s</ul></div>'
          % (t("video.eyebrow"), t("video.headline"), lis(bk.w.items("video.points")))
        + '<div style="position:absolute;left:180px;bottom:180px;display:flex;align-items:stretch">'
          '<div style="width:8px;background:var(--o)"></div><div style="background:rgba(30,15,5,.85);padding:16px 28px">'
          '<div class="mont" style="font-weight:700;font-size:32px">%s</div><div style="font-size:22px;color:var(--lg)">%s</div></div></div>'
          % (t("video.lower-third-name"), t("video.lower-third-role"))
        + '<span class="sticker" style="position:absolute;left:560px;bottom:240px;font-size:22px">%s</span>' % t("video.sticker")
    )
    bk.add("", inner)


def partners(bk):
    b, t = bk.b, bk.w.t
    lead = "ClimbUK" if b != "Climb27" else "Climb27"
    c = round(66 * CLEAR_C[lead])  # clear space: the C height, around the card edge and either side of the rule
    inner = (
        '<div class="glow"></div>'
        + '<div class="pad" style="display:grid;grid-template-columns:1fr 1fr;gap:100px">'
          '<div><div class="eb" style="font-size:24px">%s</div>'
          '<div class="h" style="font-size:80px;margin-top:22px">%s</div>'
          '<ul class="list copy" style="margin-top:36px">%s</ul></div>'
          '<div style="padding-top:60px">'
          '<div class="card" style="display:inline-flex;align-items:center;padding:%dpx;gap:%dpx">'
          '<div class="mont" style="font-weight:800;font-size:38px;line-height:1;color:#fff;letter-spacing:.02em;border:3px solid rgba(255,255,255,.6);padding:11px 20px;border-radius:8px">%s</div>'
          '<div style="width:1px;height:96px;background:rgba(255,255,255,.4)"></div>%s</div>'
          '<div class="h" style="font-size:34px;margin-top:50px">%s</div>'
          '<div style="display:flex;flex-wrap:wrap;gap:16px;margin-top:24px">%s</div></div></div>'
        % (t("partners.eyebrow"), t("partners.headline"), lis(bk.w.items("partners.points")), c, c, t("partners.sample-logo"),
           logo(lead, "reversed-dark", h=66), t("partners.lines-heading"),
           "".join('<span class="tag" style="font-size:20px;color:var(--tint)">%s</span>' % x for x in bk.w.items("partners.lines")))
    )
    bk.add(bk.B["ground"], inner)


def accessibility(bk):
    items = [(n, t, d) for n, (t, d) in bk.w.lines("accessibility.item")]
    html = "".join('<div class="card" style="padding:30px 36px"><div class="num" style="font-size:80px">%s</div>'
                   '<div class="h" style="font-size:30px;margin-top:10px">%s</div><p class="copy" style="margin-top:12px;font-size:22px">%s</p></div>' % (n, t, d) for n, t, d in items)
    inner = (
        '<div class="pad"><div class="eb" style="font-size:24px">%s</div>'
        '<div class="h" style="font-size:80px;margin-top:22px">%s</div>'
        '<div class="grid" style="grid-template-columns:repeat(3,1fr);gap:24px;margin-top:40px">%s</div>'
        '<p class="copy" style="margin-top:26px">%s</p></div>'
        % (bk.w.t("accessibility.eyebrow"), bk.w.t("accessibility.headline"), html, bk.w.t("accessibility.footnote"))
    )
    bk.add(bk.B["ground"], inner)


def downloads(bk):
    t = bk.w.t
    kit = bk.w.items("downloads.kit")
    inner = (
        '<div class="glow"></div>'
        + svg(motifs.connections(W, H, seed=9, dots=24, region=(0.66, 0.08, 0.97, 0.85)))
        + '<div class="pad" style="width:1100px">'
          '<div class="eb" style="font-size:24px">%s</div>'
          '<div class="h" style="font-size:84px;margin-top:22px">%s</div>'
          '<ul class="list copy" style="margin-top:40px;columns:2;column-gap:60px">%s</ul>'
          '<div class="card" style="margin-top:50px;padding:36px 40px;display:flex;gap:60px;align-items:center;width:1440px">'
          '<div><div class="mont" style="font-weight:700;font-size:18px;letter-spacing:.16em;color:var(--tint);text-transform:uppercase">%s</div>'
          '<div class="mont" style="font-weight:700;font-size:28px;margin-top:10px;white-space:nowrap">%s</div>'
          '<div class="mont" style="font-weight:700;font-size:28px;margin-top:4px;white-space:nowrap">%s</div></div>'
          '<div><div class="mont" style="font-weight:700;font-size:18px;letter-spacing:.16em;color:var(--tint);text-transform:uppercase">%s</div>'
          '<div class="mont" style="font-weight:700;font-size:28px;margin-top:10px;white-space:nowrap">%s</div>'
          '<div class="mont" style="font-weight:700;font-size:28px;margin-top:4px;visibility:hidden">-</div></div>'
          '<span class="btn" style="font-size:24px;margin-left:auto">%s</span></div>'
          '<p class="small" style="margin-top:24px">%s</p></div>'
        % (t("downloads.eyebrow"), t("downloads.headline"), lis(kit), t("downloads.press-label"), t("contact.press"), t("contact.phone"),
           t("downloads.partners-label"), t("contact.partners"), t("downloads.button"), t("downloads.footnote"))
    )
    bk.add(bk.B["ground"], inner)


def back_cover(bk):
    b, B = bk.b, bk.B
    inner = (
        photo({"ClimbUK": "climbteam_01.jpg", "Climb27": "climbteam_01.jpg"}.get(b, "roundtable_and_workshops_02.jpg"), "fade-ends", "center 30%")
        + '<div class="glow"></div>'
        + ('<div style="position:absolute;left:0;right:0;top:100px;text-align:center">'
          '<div class="h" style="font-size:124px;text-shadow:0 2px 12px rgba(0,0,0,.6)">%s</div></div>'
          '<div style="position:absolute;left:0;right:0;bottom:90px;display:flex;flex-direction:column;align-items:center">'
          '<div>%s</div>'
          '<div class="mont" style="margin-top:44px;font-weight:700;font-size:24px;letter-spacing:.2em;text-transform:uppercase;color:var(--tint)">%s</div></div>'
        % (bk.w.t("closing.headline"), logo(b, "reversed-dark", h=120), bk.w.t("contact.web")))
    )
    bk.add("", inner, foot=False)


ILLUS_ALL = ["microphone", "stage", "trophy", "rocket", "handshake", "people", "ticket-qr", "disco-ball", "megaphone", "lightbulb",
             "coffee", "cheers-bottles", "spotlight", "summit", "ladder", "growth-bars", "target", "confetti-cannon", "badge-speaker",
             "music-notes", "dj-decks", "festival-tent", "string-lights", "money-bag", "chart", "compass", "seedling", "crown",
             "video-camera", "high-five", "pizza-slice", "sunglasses", "medal", "calendar", "headphones"]
ILLUS_GROUP = ["contract", "fountain-pen", "briefcase", "calculator", "pie-chart", "office-block", "handshake", "scales", "laptop",
               "slide-deck", "meeting-table", "certificate", "envelope", "phone", "calendar", "clipboard", "growth-bars", "coin-stack",
               "pound-note", "piggy-bank", "key", "chess-knight", "globe", "notebook", "business-card", "target", "lightbulb",
               "summit", "rocket", "trophy", "people", "coffee", "chain-link", "magnifier", "gears"]
ILLUS_27 = ["stage", "microphone", "lighting-rig", "big-screen", "tickets", "wristband", "stage-pass", "badge-delegate", "badge-partner",
            "badge-speaker", "food-truck", "cocktail", "pint", "disco-ball", "fireworks", "party-popper", "balloons", "bunting",
            "festival-tent", "string-lights", "dj-decks", "record", "applause", "selfie", "goodie-bag", "tote-bag", "bucket-hat",
            "t-shirt", "winners-podium", "trophy", "spotlight-beam", "qr-scan", "high-five", "hello-tag", "sunglasses"]


def build(b):
    bk = Book(b)
    cover(bk)
    bk.section = bk.w.t("footer.contents")
    contents(bk)
    divider(bk, 0)
    big_idea(bk)
    family(bk)
    if b == "ClimbGroup":
        where_group(bk)
    if b == "Climb27":
        themes27(bk)
    five_rules(bk)
    divider(bk, 1)
    logo_master(bk)
    if b == "Climb27":
        edition_mark(bk)
    logo_variants(bk)
    logo_space(bk)
    logo_icons(bk)
    logo_donts(bk)
    divider(bk, 2)
    colours(bk)
    presets(bk)
    contrast(bk)
    divider(bk, 3)
    typefaces(bk)
    headline_formula(bk)
    type_scale(bk)
    divider(bk, 4)
    motifs_slide(bk)
    devices(bk)
    lineup(bk)
    illustrations(bk, {"ClimbGroup": ILLUS_GROUP, "Climb27": ILLUS_27}.get(b, ILLUS_ALL))
    divider(bk, 5)
    photo_shoot(bk)
    photo_fades(bk)
    photo_rules(bk)
    divider(bk, 6)
    motion(bk)
    digital_ui(bk)
    if b in ("ClimbUK", "Climb27"):
        tickets(bk)
    if b == "ClimbGroup":
        documents(bk)
    divider(bk, 7)
    voice_lines(bk)
    voice_rules(bk)
    rewrites(bk)
    words(bk)
    if b == "ClimbUK":
        audiences(bk)
    divider(bk, 8)
    print_merch(bk)
    video(bk)
    partners(bk)
    if b == "Climb27":
        share_kit(bk)
    if b == "ClimbGroup":
        signature(bk)
    divider(bk, 9)
    accessibility(bk)
    bk.section = bk.w.t("footer.downloads")
    downloads(bk)
    back_cover(bk)
    html = ('<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><title>%s</title>'
            '<link rel="stylesheet" href="base.css"><style>@page{size:1920px 1080px;margin:0}</style></head><body>%s</body></html>'
            % (bk.w.t("document.title"), "\n".join(bk.render())))
    path = os.path.join(HERE, "%s_brand-guidelines.html" % BRANDS[b]["key"])
    open(path, "w").write(html)
    return path, len(bk.slides)


if __name__ == "__main__":
    for b in (sys.argv[1:] or BRANDS):
        print(*build(b))
