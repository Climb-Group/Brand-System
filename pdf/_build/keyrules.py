"""Builds the one-page key rules sheet (A4 portrait) for ClimbUK, ClimbGroup and Climb27 as HTML, ready for render.cjs."""
import os
import sys

import motifs
from brands import BRANDS, COMMON

HERE = os.path.dirname(os.path.abspath(__file__))
P = "assets/photos/"
W, H = 794, 1123

CSS = """
@page{size:210mm 297mm;margin:0}
.a4{width:794px;height:1123px;position:relative;overflow:hidden;background:var(--db)}
.a4.ch{background:var(--ch)}
.hero{position:absolute;left:0;right:0;top:0;height:250px;overflow:hidden}
.rules{position:absolute;left:30px;right:30px;top:262px;bottom:172px;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr 1fr;gap:12px}
.r{background:var(--ch);border:1px solid rgba(255,255,255,.08);border-radius:12px;padding:13px 16px 10px;position:relative;min-width:0;min-height:0;overflow:hidden}
.a4.ch .r{background:#2f2d2b}
.r .t{display:flex;align-items:baseline;gap:10px}
.r .n{font:800 24px/1 Montserrat;color:var(--o)}
.r .tt{font:800 17px/1.05 Montserrat;text-transform:uppercase;color:#fff;letter-spacing:-.01em}
.r ul{list-style:none;margin-top:8px}
.r li{font-size:13px;line-height:1.36;color:var(--lg);padding-left:15px;position:relative;margin-bottom:3px}
.r li::before{content:"";position:absolute;left:0;top:.45em;width:6px;height:6px;border-right:2.5px solid var(--o);border-top:2.5px solid var(--o);transform:rotate(45deg)}
.r li.x::before{border:0;content:"\\00D7";transform:none;top:-.12em;left:0;width:auto;height:auto;color:var(--o);font:800 16px/1 Montserrat}
.r li b{color:#fff;font-weight:700}
.vis{display:flex;gap:6px;align-items:center;margin-top:8px;min-width:0}
.sw{height:26px;border-radius:6px;flex:1;min-width:0}
.name{padding:12px 18px !important;position:absolute;left:30px;right:30px;top:auto;bottom:62px;background:var(--o);border-radius:12px;padding:14px 20px;display:grid;grid-template-columns:150px 1fr 1fr 1fr;gap:16px;align-items:start;color:var(--db)}
.name .k{font:800 13px/1.35 Montserrat;text-transform:uppercase;letter-spacing:.06em}
.name p{font-size:13px;line-height:1.4;color:var(--db)}
.name p b{font-family:Montserrat;font-weight:800}
.bot{position:absolute;left:30px;right:30px;bottom:20px;display:flex;justify-content:space-between;align-items:center;font-size:13px;color:var(--lg)}
.bot b{font-family:Montserrat;color:#fff}
"""


def logo(b, variant, h=None, w=None, style=""):
    size = ("height:%dpx;" % h if h else "") + ("width:%dpx;" % w if w else "")
    return '<img src="assets/logos/%s/%s_%s.svg" style="%s%s" alt="%s logo">' % (b, b, variant, size, style, b)


def card(n, title, items, vis=""):
    lis = "".join('<li class="x">%s</li>' % i[2:] if i.startswith("x ") else "<li>%s</li>" % i for i in items)
    return ('<div class="r"><div class="t"><span class="n">%s</span><span class="tt">%s</span></div>%s<ul>%s</ul></div>'
            % (n, title, vis, lis))


def build(b):
    B = BRANDS[b]
    ground = B["ground"]
    hero_photo = {"ClimbUK": "climb_crowd_wide.jpg", "ClimbGroup": "climb_isn_investors_hero.jpg", "Climb27": "climb_band_stage.jpg"}[b]
    hero = (
        '<div class="hero"><div class="ph" style="background-image:url(%s%s);background-position:center 35%%"></div>'
        '<div class="layer fade-hero"></div><div class="glow"></div>'
        '%s'
        '<div style="position:absolute;left:30px;top:24px">%s</div>'
        '<span class="sticker" style="position:absolute;right:30px;top:28px;font-size:13px">Everyone follows these</span>'
        '<div style="position:absolute;left:30px;bottom:18px;width:720px">'
        '<div class="eb" style="font-size:13px;margin-bottom:10px">The key rules</div>'
        '<div class="h" style="font-size:46px;text-shadow:0 2px 12px rgba(0,0,0,.6)">%s</div>'
        '<p style="font-size:13px;line-height:1.4;margin-top:10px;color:#fff;max-width:600px">%s</p></div></div>'
        % (P, hero_photo,
           '<svg viewBox="0 0 794 330" width="794" height="330" style="position:absolute;inset:0">%s</svg>' % motifs.slabs(794, 330, corners=("br",), length=230, thick=26) if b == "ClimbGroup" else "",
           logo(b, "reversed-dark", h=34), B["sheet_h"],
           "For anyone making anything with the %s name on it: designers, agencies, partners, printers, press and the team. "
           "The brand book has the rest." % B["name"])
    )
    other_ground = "Charcoal" if b == "ClimbGroup" else "Dark Brown"
    cards = [
        card("01", "Logo", [
            "<b>Master files only.</b> Never redraw, recolour, stretch, rotate or add effects.",
            "<b>Reversed on dark is the default.</b> Full colour on White, grey version on Light Grey, mono white on orange.",
            "<b>Clear space:</b> the height of the l in Climb. <b>Minimum:</b> 120px or 30mm, then the tile or l! monogram.",
        ], '<div class="vis"><div style="flex:1.3;background:var(--db);border-radius:7px;height:34px;display:flex;align-items:center;justify-content:center;border:1px solid rgba(255,255,255,.12)">%s</div>'
           '<div style="flex:1.3;background:#fff;border-radius:7px;height:34px;display:flex;align-items:center;justify-content:center">%s</div>'
           '<div style="width:34px;height:34px;flex:none">%s</div></div>'
           % (logo(b, "reversed-dark", h=17), logo(b, "full-colour-light", h=17), logo(b, "icon-monogram", w=34, style="border-radius:6px"))),
        card("02", "Colour", [
            "<b>Dark first:</b> %s is the ground. Light grounds are for long reading." % other_ground,
            "<b>Orange leads, never floods:</b> one orange call to action per view.",
            "<b>White on orange</b> only at 19px bold or 14pt bold and up. Small orange text: Orange Tint on dark, Deep Orange on white.",
        ], '<div class="vis">%s</div>' % "".join(
            '<div class="sw" style="background:%s;%s"></div>' % (bg, bd) for bg, fg, bd, hx in [
                ("var(--o)", "var(--db)", "flex:1.6;", "#E8712A"), ("var(--db)", "#fff", "border:1px solid rgba(255,255,255,.2);", "#1E0F05"),
                ("var(--ch)", "#fff", "border:1px solid rgba(255,255,255,.2);", "#242322"), ("var(--lg)", "var(--ch)", "", "#E9E9E9"),
                ("var(--tint)", "var(--db)", "", "#F2AE86"), ("#fff", "var(--ch)", "", "#FFFFFF")])),
        card("03", "Type", [
            "<b>Montserrat</b> headings: uppercase, tight, 3 to 8 words. <b>Open Sans</b> for reading.",
            "<b>One word orange, one word italic</b> in every display line.",
            "<b>Nothing under 13px</b> on screen or 9pt in print.",
        ], '<div class="vis"><div class="h" style="font-size:19px;line-height:1">ICONIC <em>MOMENTS</em>. REAL ADVICE. NO <span class="o">FLUFF</span>.</div></div>'),
        card("04", "Voice", [
            "<b>Headline energy. Doing, not dreaming. Curated, not crowded. Personal, not generic.</b>",
            "<b>No emojis, exclamation marks or dashes.</b> Full names only, never \u201cClimb\u201d alone.",
            "<b>No unpublished numbers, no guarantees, no hedges.</b> Scarcity only when true.",
            "<b>Real, named people</b> in quotes. Links say where they go.",
        ]),
        card("05", "Photography and graphics", [
            "<b>Real people, real light,</b> warm and full colour, with consent. Never stock.",
            "<b>Words sit on a Dark Brown fade,</b> never on a busy part of a photo.",
            "<b>One motif family</b> and two or three festival devices per piece.",
        ], '<div class="vis" style="gap:5px">%s</div>' % "".join(
            '<div style="flex:1;height:34px;border-radius:7px;background:url(%s%s) center/cover"></div>' % (P, f)
            for f in ("climb_awards_winners.jpg", "climb_recap_05.jpg", "climb_band_stage.jpg", "climb_recap_02.jpg", "climb_drinks_reception.jpg"))),
        card("06", "Everyone in the room", [
            "<b>WCAG 2.2 AA everywhere,</b> AAA where it is easy.",
            "<b>44px targets,</b> a visible focus ring, colour never the only signal.",
            "<b>Plain words,</b> alt text that says what is happening, captions on video.",
            "<b>4K by default,</b> never upscaled. Print PDF/X-4 with 3mm bleed.",
        ]),
    ]
    naming = "".join('<p><b>%s</b> %s</p>' % (k, v) for k, v in B["naming"])
    html = (
        '<section class="a4 %s">%s<div class="rules">%s</div>'
        '<div class="name"><div class="k">Get the<br>name right</div>%s</div>'
        '<div class="bot"><div>%s</div><div><b>%s</b> &nbsp;|&nbsp; %s &nbsp;|&nbsp; <b>%s</b></div></div></section>'
        % (ground, hero, "".join(cards), naming, logo(b, "tagline-lockup-reversed", h=34), COMMON["email"], COMMON["phone"], COMMON["web"])
    )
    title = "%s key rules" % b
    doc = ('<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><title>%s</title>'
           '<link rel="stylesheet" href="base.css"><style>%s</style></head><body>%s</body></html>' % (title, CSS, html))
    path = os.path.join(HERE, "%s_key-rules.html" % B["key"])
    open(path, "w").write(doc)
    return path


if __name__ == "__main__":
    for b in (sys.argv[1:] or BRANDS):
        print(build(b))
