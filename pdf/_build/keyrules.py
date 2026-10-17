"""Builds the one-page key rules sheet (A4 portrait) for ClimbUK, ClimbGroup and Climb27 as HTML, ready for render.cjs.

The words come from pdf/one-page/<brand>_key-rules.copy.md; this script holds only the layout."""
import os
import sys

import motifs
from brands import BRANDS, Words, copy_path, md

HERE = os.path.dirname(os.path.abspath(__file__))
P = "assets/photos/"
W, H = 794, 1123
ALT = ""

CSS = """
@page{size:210mm 297mm;margin:0}
.a4{width:794px;height:1123px;position:relative;overflow:hidden;background:var(--db)}
.a4.ch{background:var(--ch)}
.hero{position:absolute;left:0;right:0;top:0;height:250px;overflow:hidden}
.rules{position:absolute;left:30px;right:30px;top:262px;bottom:186px;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr 1fr;gap:12px}
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
.name{padding:12px 18px !important;position:absolute;left:30px;right:30px;top:auto;bottom:76px;background:var(--o);border-radius:12px;padding:14px 20px;display:grid;grid-template-columns:150px 1fr 1fr 1fr;gap:16px;align-items:start;color:var(--db)}
.name .k{font:800 13px/1.35 Montserrat;text-transform:uppercase;letter-spacing:.06em}
.name p{font-size:13px;line-height:1.4;color:var(--db)}
.name p b{font-family:Montserrat;font-weight:800}
.bot{position:absolute;left:30px;right:30px;bottom:24px;display:flex;justify-content:space-between;align-items:center;font-size:13px;color:var(--lg)}
.bot b{font-family:Montserrat;color:#fff}
"""


def logo(b, variant, h=None, w=None, style=""):
    size = ("height:%dpx;" % h if h else "") + ("width:%dpx;" % w if w else "")
    return '<img src="assets/logos/%s/%s_%s.svg" style="%s%s" alt="%s">' % (b, b, variant, size, style, ALT)


def card(n, title, items, vis=""):
    lis = "".join('<li class="x">%s</li>' % i[2:] if i.startswith("x ") else "<li>%s</li>" % i for i in items)
    return ('<div class="r"><div class="t"><span class="n">%s</span><span class="tt">%s</span></div>%s<ul>%s</ul></div>'
            % (n, title, vis, lis))


def build(b):
    global ALT
    B = BRANDS[b]
    w = Words(copy_path("one-page", "%s_key-rules.copy.md" % B["key"]))
    ALT = w.t("logo.alt")
    ground = B["ground"]
    hero_photo = {"ClimbUK": "climb_crowd_wide.jpg", "ClimbGroup": "climb_recap_03.jpg", "Climb27": "joy_02.jpg"}[b]
    hero = (
        '<div class="hero"><div class="ph" style="background-image:url(%s%s);background-position:center 35%%"></div>'
        '<div class="layer fade-hero"></div><div class="glow"></div>'
        '%s'
        '<div style="position:absolute;left:30px;top:28px">%s</div>'
        '<span class="sticker" style="position:absolute;right:30px;top:28px;font-size:13px">%s</span>'
        '<div style="position:absolute;left:30px;bottom:14px;width:720px">'
        '<div class="eb" style="font-size:13px;margin-bottom:10px">%s</div>'
        '<div class="h" style="font-size:42px;text-shadow:0 2px 12px rgba(0,0,0,.6)">%s</div>'
        '<p style="font-size:13px;line-height:1.4;margin-top:8px;color:#fff;max-width:600px">%s</p></div></div>'
        % (P, hero_photo,
           '<svg viewBox="0 0 794 330" width="794" height="330" style="position:absolute;inset:0">%s</svg>' % motifs.slabs(794, 330, corners=("br",), length=230, thick=26) if b == "ClimbGroup" else "",
           logo(b, "reversed-dark", h=26), w.t("hero.sticker"), w.t("hero.eyebrow"), w.t("hero.headline"), w.t("hero.intro"))
    )
    # What each rule shows under its title, in the order of the rules in the copy file.
    vis = [
        '<div class="vis"><div style="flex:1.3;background:var(--db);border-radius:7px;height:44px;display:flex;align-items:center;justify-content:center;border:1px solid rgba(255,255,255,.12)">%s</div>'
        '<div style="flex:1.3;background:#fff;border-radius:7px;height:44px;display:flex;align-items:center;justify-content:center">%s</div>'
        '<div style="width:44px;height:44px;flex:none">%s</div></div>'
        % (logo(b, "reversed-dark", h=14), logo(b, "full-colour-light", h=14), logo(b, "icon-monogram-on-ground", w=44, style="border-radius:6px")),
        '<div class="vis">%s</div>' % "".join(
            '<div class="sw" style="background:%s;%s"></div>' % (bg, bd) for bg, fg, bd, hx in [
                ("var(--o)", "var(--db)", "flex:1.6;", "#E8712A"), ("var(--db)", "#fff", "border:1px solid rgba(255,255,255,.2);", "#1E0F05"),
                ("var(--ch)", "#fff", "border:1px solid rgba(255,255,255,.2);", "#242322"), ("var(--lg)", "var(--ch)", "", "#E9E9E9"),
                ("var(--tint)", "var(--db)", "", "#F2AE86"), ("#fff", "var(--ch)", "", "#FFFFFF")]),
        '<div class="vis"><div class="h" style="font-size:19px;line-height:1">%s</div></div>' % w.t("rule.type-sample"),
        "",
        '<div class="vis" style="gap:5px">%s</div>' % "".join(
            '<div style="flex:1;height:34px;border-radius:7px;background:url(%s%s) center/cover"></div>' % (P, f)
            for f in ("joy_01.jpg", "crowds_02.jpg", "stage_speakers_02.jpg", "meetings_01.jpg", "food_and_vendors_01.jpg")),
        "",
    ]
    rules = w.secs("rule")
    assert len(rules) == len(vis), "%d rules in the copy file, the layout has %d" % (len(rules), len(vis))
    cards = [card("%02d" % (i + 1), md(r.title), [md(x[2:], quotes=r.get("quotes") == "curly") for x in r.text.split("\n")], v)
             for i, (r, v) in enumerate(zip(rules, vis))]
    naming = "".join('<p><b>%s</b> %s</p>' % (k, v) for k, v in w.pairs("naming.item"))
    html = (
        '<section class="a4 %s">%s<div class="rules">%s</div>'
        '<div class="name"><div class="k">%s</div>%s</div>'
        '<div class="bot"><div>%s</div><div style="text-align:right">%s <b>%s</b> &nbsp;|&nbsp; %s <b>%s</b><br>%s &nbsp;|&nbsp; <b>%s</b></div></div></section>'
        % (ground, hero, "".join(cards), w.t("naming.heading"), naming, logo(b, "tagline-lockup-reversed", h=30),
           w.t("footer.press-label"), w.t("footer.press"), w.t("footer.partners-label"), w.t("footer.partners"), w.t("footer.phone"), w.t("footer.web"))
    )
    doc = ('<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><title>%s</title>'
           '<link rel="stylesheet" href="base.css"><style>%s</style></head><body>%s</body></html>' % (w.t("document.title"), CSS, html))
    path = os.path.join(HERE, "%s_key-rules.html" % B["key"])
    open(path, "w").write(doc)
    return path


if __name__ == "__main__":
    for b in (sys.argv[1:] or BRANDS):
        print(build(b))
