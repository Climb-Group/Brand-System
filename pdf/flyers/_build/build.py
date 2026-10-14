"""Climb27 print pieces: A5 flyer (2 sides), 800x2000mm roller banner, 85x55mm business card.

Writes one HTML page per piece (laid out in mm, 3mm bleed on every edge), with photos pre-cropped, faded and
sized for print by Pillow, then prints each page to PDF with Chromium and sets the TrimBox and BleedBox.

    python3 build.py [--pack /path/to/Brand-System] [--phone "07..."] [--email "..."]

Colours are the brand tokens (tokens/brand.tokens.json). Copy follows the climb-voice skill and its checker; the
dates, tagline and website come from copy/shared.copy.md.
"""
import argparse
import html
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import segno
from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
IMG = HERE / "img"
COPY = OUT / "copy"

# Copy files: the words of each piece live in pdf/flyers/copy/*.copy.md (climb-voice references/copy-files.md).
sys.path.insert(0, str(HERE.parents[2] / ".agents" / "skills" / "climb-voice" / "scripts"))
import copy_md  # noqa: E402

# Brand tokens
DB, CH, OR, TI, LG, WH = "#1E0F05", "#242322", "#E8712A", "#F2AE86", "#E9E9E9", "#FFFFFF"
DB_RGB = (30, 15, 5)
OR_RGB = (232, 113, 42)

SHARED = copy_md.load(COPY / "shared.copy.md")
DATES = SHARED.one("dates").text
TAGLINE = SHARED.one("tagline").text
URL = SHARED.one("website").text
TICKETS = "https://www.climb-uk.com/shop/category/climb27-tickets-24?utm_source=print&utm_medium=%s&utm_campaign=climb27"
CARD_QR = "https://www.climb-uk.com/shop"
BLEED = 3.0


def photo(section):
    """A photo section of a copy file as (photo name, (focus x, focus y))."""
    x, y = section["focus"].split(",")
    return section["name"], (float(x), float(y))


# ---------------------------------------------------------------- helpers

def bake(pack, photo, w_mm, h_mm, ppi, name, pos=(0.5, 0.5), fade=None):
    """Crop a photo to cover w x h mm, size it for ppi (never upscaled), and burn in a fade.
    fade: list of (axis, start, end, rgb, a0, a1): alpha runs a0 -> a1 between start and end (0..1 of the axis)."""
    src = pack / "photos" / (photo + ".jpg")
    if not src.exists():
        src = pack / "photos" / "candid" / (photo + ".jpg")
    im = Image.open(src).convert("RGB")
    sw, sh = im.size
    tw, th = w_mm / 25.4 * ppi, h_mm / 25.4 * ppi
    scale = max(tw / sw, th / sh)
    if scale > 1:                       # never upscale: keep the crop at source pixels
        cw, ch = tw / scale, th / scale
        ow, oh = int(round(cw)), int(round(ch))
    else:
        cw, ch = tw / scale, th / scale
        ow, oh = int(round(tw)), int(round(th))
    x0 = (sw - cw) * pos[0]
    y0 = (sh - ch) * pos[1]
    im = im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((ow, oh), Image.LANCZOS)
    if fade:
        a = np.asarray(im).astype(np.float32)
        for axis, s, e, rgb, a0, a1 in fade:
            n = a.shape[1] if axis == "x" else a.shape[0]
            t = np.clip((np.arange(n) / max(n - 1, 1) - s) / max(e - s, 1e-6), 0, 1)
            t = t * t * (3 - 2 * t)  # smoothstep
            al = a0 + (a1 - a0) * t
            al = al[None, :, None] if axis == "x" else al[:, None, None]
            a = a * (1 - al) + np.array(rgb, np.float32)[None, None, :] * al
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    IMG.mkdir(exist_ok=True)
    out = IMG / (name + ".jpg")
    im.save(out, quality=92, dpi=(ppi, ppi))
    eff = min(ow / w_mm * 25.4, oh / h_mm * 25.4)
    print("  %-28s %5dx%-5d px  %4.0f ppi at %.0fx%.0fmm" % (name, ow, oh, eff, w_mm, h_mm))
    return out


def glow(w_mm, h_mm, ppi, name, cx, cy, r, strength=0.55):
    """A Dark Brown ground with a soft Climb Orange stage glow, baked to an image."""
    w, h = int(w_mm / 25.4 * ppi), int(h_mm / 25.4 * ppi)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt((xx / w - cx) ** 2 * (w / h) ** 2 + (yy / h - cy) ** 2) / r
    t = np.clip(1 - d, 0, 1) ** 2 * strength
    a = np.array(DB_RGB, np.float32)[None, None, :] * (1 - t[..., None]) + np.array(OR_RGB, np.float32) * t[..., None]
    IMG.mkdir(exist_ok=True)
    out = IMG / (name + ".jpg")
    Image.fromarray(a.astype(np.uint8)).save(out, quality=92)
    return out


def logo(pack, brand, variant):
    s = (pack / "logos" / brand / ("%s_%s.svg" % (brand, variant))).read_text()
    vb = s.split('viewBox="')[1].split('"')[0].split()
    return s[s.index("<svg"):], float(vb[2]) / float(vb[3])


def logo_tag(pack, brand, variant, x, y, w, extra=""):
    svg, ratio = logo(pack, brand, variant)
    svg = svg.replace("<svg ", '<svg style="width:100%;height:100%;display:block" ', 1)
    return '<div class="abs" style="left:%smm;top:%smm;width:%smm;height:%.3fmm;%s">%s</div>' % (x, y, w, w / ratio, extra, svg)


def qr_svg(data, dark=DB):
    q = segno.make(data, error="m")
    rows = [list(r) for r in q.matrix]
    n = len(rows)
    d = "".join("M%d %dh1v1h-1z" % (x, y) for y, r in enumerate(rows) for x, v in enumerate(r) if v)
    return ('<svg viewBox="0 0 %d %d" shape-rendering="crispEdges" style="width:100%%;height:100%%;display:block">'
            '<title>QR code</title><path fill="%s" d="%s"/></svg>' % (n, n, dark, d))


def illo(pack, name, color=OR):
    s = (pack / "illustrations" / (name + ".svg")).read_text()
    s = s[s.index("<svg"):]
    return s.replace("<svg ", '<svg style="width:100%%;height:100%%;display:block;color:%s" ' % color, 1)


def chevron(color):
    return ('<svg viewBox="0 0 100 100" style="width:100%%;height:100%%;display:block"><path d="M18 12 L78 50 L18 88 L34 50 Z" '
            'fill="%s"/></svg>' % color)


def page(pack, w, h, body, title):
    fonts = pack / "fonts" / "ttf"
    ff = []
    for fam, files in (("Montserrat", [("Regular", 400, "normal"), ("Italic", 400, "italic"), ("SemiBold", 600, "normal"),
                                       ("Bold", 700, "normal"), ("BoldItalic", 700, "italic"), ("ExtraBold", 800, "normal"),
                                       ("ExtraBoldItalic", 800, "italic"), ("Black", 900, "normal")]),
                       ("Open Sans", [("Regular", 400, "normal"), ("Italic", 400, "italic"), ("SemiBold", 600, "normal"),
                                      ("Bold", 700, "normal")])):
        for f, wt, st in files:
            ff.append("@font-face{font-family:'%s';src:url('%s');font-weight:%d;font-style:%s}"
                      % (fam, (fonts / ("%s-%s.ttf" % (fam.replace(" ", ""), f))).as_uri(), wt, st))
    css = """
@page{size:%smm %smm;margin:0}
html,body{margin:0;padding:0}
body{width:%smm;height:%smm;position:relative;overflow:hidden;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.abs{position:absolute}
.disp{font-family:Montserrat;font-weight:800;text-transform:uppercase;letter-spacing:-0.01em;line-height:1.0;margin:0}
.body{font-family:'Open Sans'}
.mont{font-family:Montserrat}
.o{color:%s}
em{font-style:italic}
img.ph{position:absolute;display:block;object-fit:cover}
""" % (w, h, w, h, OR)
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>%s</title><style>%s%s</style></head>'
            '<body>%s</body></html>' % (html.escape(title), "".join(ff), css, body))


def img(path, x, y, w, h, extra=""):
    return '<img class="ph" alt="" src="%s" style="left:%smm;top:%smm;width:%smm;height:%smm;%s">' % (path.as_uri(), x, y, w, h, extra)


# ---------------------------------------------------------------- flyer (A5, two sides)

FLYER_ITEMS = [
    ("people", "Connect",
     "Find your people: founders, business leaders, advisers, the public sector and investors looking for real deal flow."),
    ("lightbulb", "Learn",
     "Fresh insight and practical ideas from fellow founders and the people building and backing growing businesses."),
    ("growth-bars", "Grow",
     "Build relationships that open doors, and leave with a clear next step for your business."),
    ("handshake", "Belong",
     "Join a community that shares what works and sends each other work, long after the festival."),
    ("microphone", "Experience",
     "Main stage moments, roundtables, workshops, Investor Speed Networking and the after parties."),
]


def flyer(pack):
    W, H = 148 + 2 * BLEED, 210 + 2 * BLEED
    b = BLEED
    m = b + 10  # 10mm in from trim (5mm safe zone plus air)
    # Front
    hero_h = 122
    hero = bake(pack, "climb_isn_founders_hero", W, hero_h, 300, "flyer_front_hero", pos=(0.5, 0.35),
                fade=[("y", 0.0, 0.35, DB_RGB, 0.78, 0.0)])
    f = [img(hero, 0, 0, W, hero_h)]
    f.append(logo_tag(pack, "Climb27", "reversed-dark", m, b + 10, 52))
    cut = 112
    f.append('<div class="abs" style="left:0;top:%smm;width:%smm;height:%smm;background:%s;'
             'clip-path:polygon(0 12mm,100%% 0,100%% 100%%,0 100%%)"></div>' % (cut - 12, W, H - cut + 12, OR))
    # sticker on the cut edge
    f.append('<div class="abs mont" style="left:%smm;top:%smm;transform:rotate(-3.5deg);background:%s;color:%s;'
             'font-weight:800;font-size:10.5pt;letter-spacing:.04em;text-transform:uppercase;padding:2.2mm 4mm;'
             'border-radius:1.5mm">%s</div>' % (m + 52, cut - 13, DB, WH, DATES))
    f.append('<h1 class="abs disp" style="left:%smm;top:%smm;width:%smm;font-size:39pt;color:%s;line-height:.98">'
             'Your business.<br><em>Bigger</em> <span style="color:%s">stage.</span></h1>' % (m, cut + 8, W - 2 * m, WH, DB))
    f.append('<div class="abs mont" style="left:%smm;top:%smm;width:%smm;font-weight:700;font-size:14pt;color:%s;line-height:1.2">'
             '%s</div>' % (m, cut + 44, W - 2 * m, WH, TAGLINE))
    f.append('<div class="abs" style="left:%smm;top:%smm;width:16mm;height:1.6mm;border-radius:1mm;background:%s"></div>'
             % (m, cut + 56, DB))
    band = H - b - 30
    f.append('<div class="abs" style="left:0;top:%smm;width:%smm;height:%smm;background:%s"></div>' % (band, W, H - band, DB))
    f.append('<div class="abs mont" style="left:%smm;top:%smm;color:%s;font-weight:700;font-size:9pt;letter-spacing:.14em;'
             'text-transform:uppercase">Get your ticket</div>' % (m, band + 7, TI))
    f.append('<div class="abs mont" style="left:%smm;top:%smm;color:%s;font-weight:800;font-size:20pt;letter-spacing:-.01em">'
             '%s</div>' % (m, band + 12, WH, URL))
    f.append(logo_tag(pack, "ClimbUK", "reversed-dark", W - m - 34, band + 13.5, 34))
    front = page(pack, W, H, "\n".join(f), "Climb27 flyer front")

    # Back
    r = ['<div class="abs" style="inset:0;background:%s"></div>' % DB]
    gl = glow(W, H, 150, "flyer_back_glow", 1.05, -0.05, 0.75, 0.45)
    r.append(img(gl, 0, 0, W, H))
    _, ratio = logo(pack, "Climb27", "reversed-dark")
    r.append('<h2 class="abs disp" style="left:%smm;top:%smm;width:%smm;font-size:21pt;color:%s;line-height:1.04">'
             'When you attend <span style="display:inline-block;width:38mm;height:%.2fmm;vertical-align:-0.6mm">%s</span><br>'
             'you\'ll come away with<br><span class="o">so much more</span> than<br>you <em>imagined</em>.</h2>'
             % (m, b + 11, W - 2 * m, WH, 38 / ratio,
                logo(pack, "Climb27", "reversed-dark")[0].replace("<svg ", '<svg style="width:100%;height:100%;display:block" ', 1)))
    y = b + 50
    for icon, head, text in FLYER_ITEMS:
        r.append('<div class="abs" style="left:%smm;top:%smm;width:13mm;height:13mm">%s</div>' % (m - 1, y - 1, illo(pack, icon)))
        r.append('<div class="abs disp" style="left:%smm;top:%smm;font-size:13pt;color:%s;text-transform:none;letter-spacing:0">'
                 '%s<span class="o">.</span></div>' % (m + 16, y, WH, head))
        r.append('<div class="abs body" style="left:%smm;top:%smm;width:%smm;font-size:9pt;line-height:1.38;color:%s">%s</div>'
                 % (m + 16, y + 6.2, W - 2 * m - 16, WH, html.escape(text)))
        y += 20
    # photo strip
    py, ph = y + 1, 31
    gap = 2.5
    big = 60
    small = (W - 2 * m - big - 2 * gap) / 2
    shots = [("climb_recap_01", big, (0.45, 0.4)), ("audience_at_stage_02", small, (0.5, 0.4)),
             ("roundtable_and_workshops_01", small, (0.55, 0.4))]
    x = m
    for i, (p, w, pos) in enumerate(shots):
        r.append(img(bake(pack, p, w, ph, 300, "flyer_back_%d" % i, pos=pos), x, py, w, ph, "border-radius:2mm"))
        x += w + gap
    band = H - b - 26
    r.append('<div class="abs" style="left:0;top:%smm;width:%smm;height:%smm;background:%s"></div>' % (band, W, H - band, OR))
    r.append('<div class="abs disp" style="left:%smm;top:%smm;font-size:16pt;color:%s">Get your <em>ticket</em></div>'
             % (m, band + 6, WH))
    r.append('<div class="abs mont" style="left:%smm;top:%smm;font-weight:800;font-size:14pt;color:%s">%s</div>'
             % (m, band + 13, WH, URL))
    r.append('<div class="abs mont" style="left:%smm;top:%smm;font-weight:700;font-size:8.5pt;color:%s">%s</div>'
             % (m, band + 19.5, DB, DATES))
    qs = 19
    r.append('<div class="abs" style="left:%smm;top:%smm;width:%smm;height:%smm;background:%s;border-radius:1.5mm;padding:1.6mm;'
             'box-sizing:border-box">%s</div>' % (W - m - qs, band + 3.5, qs, qs, WH, qr_svg(TICKETS % "flyer")))
    r.append('<div class="abs mont" style="left:%smm;top:%smm;width:24mm;text-align:right;font-weight:700;font-size:7.5pt;'
             'line-height:1.25;color:%s">Scan for<br>tickets</div>' % (W - m - qs - 27, band + 9, DB))
    back = page(pack, W, H, "\n".join(r), "Climb27 flyer back")
    return W, H, [front, back]


# ---------------------------------------------------------------- roller banner (800x2000mm)

def banner(pack):
    W, H = 800 + 2 * BLEED, 2000 + 2 * BLEED
    b = BLEED
    m = b + 60
    PPI = 150
    p = ['<div class="abs" style="inset:0;background:%s"></div>' % DB]
    head_h = 400
    p.append(img(glow(W, head_h, 60, "banner_head_glow", 0.95, 0.0, 0.9, 0.5), 0, 0, W, head_h))
    p.append(logo_tag(pack, "Climb27", "reversed-dark", m, b + 70, 430))
    _, ratio = logo(pack, "Climb27", "reversed-dark")
    ly = b + 70 + 430 / ratio
    p.append('<div class="abs mont" style="left:%smm;top:%smm;font-weight:800;font-size:66pt;color:%s;letter-spacing:-.005em">'
             '%s</div>' % (m, ly + 22, OR, DATES))
    qs = 170
    qx = W - m - qs + 20
    p.append('<div class="abs" style="left:%smm;top:%smm;width:%smm;height:%smm;background:%s;border-radius:8mm;padding:12mm;'
             'box-sizing:border-box">%s</div>' % (qx, b + 55, qs, qs, WH, qr_svg(TICKETS % "roller-banner")))
    p.append('<div class="abs mont" style="left:%smm;top:%smm;width:%smm;text-align:center;font-weight:800;font-size:44pt;'
             'line-height:1.1;color:%s">Scan for<br><em>tickets</em></div>' % (qx - 10, b + 55 + qs + 10, qs + 20, WH))
    p.append('<div class="abs" style="left:%smm;top:%smm;width:70mm;height:7mm;border-radius:4mm;background:%s"></div>'
             % (m, 300, OR))
    p.append('<div class="abs mont" style="left:%smm;top:%smm;width:%smm;font-weight:700;font-size:84pt;color:%s;line-height:1.1">'
             '%s</div>' % (m, 316, W - 2 * m, WH, TAGLINE))

    rows = [
        ("audience_at_stage_03", DB, (0.5, 0.45),
         '<div class="disp" style="font-size:112pt;color:%s;text-transform:none;letter-spacing:-.01em">Build what <span class="o">matters</span>.</div>'
         '<div class="body" style="margin-top:22mm;font-size:58pt;font-style:italic;line-height:1.35;color:%s">"The event is for anyone '
         'looking to scale their business - connecting the right people in a way that just works"</div>' % (WH, WH)),
        ("climb_recap_01", OR, (0.4, 0.4),
         '<div class="disp" style="font-size:92pt;color:%s;text-transform:none;line-height:1.08">Content for high-growth and '
         'scaling companies</div><div class="body" style="margin-top:20mm;font-size:58pt;font-weight:600;line-height:1.35;color:%s">'
         'Roundtables, workshops and main stage moments that help you take the next step.</div>' % (WH, WH)),
        ("climbteam_01", CH, (0.5, 0.5), None),
        ("roundtable_and_workshops_01", OR, (0.5, 0.45),
         '<div class="body" style="font-size:80pt;font-style:italic;font-weight:600;line-height:1.3;color:%s">"For networking this is '
         '<b style="font-family:Montserrat;font-weight:800">THE BOMB</b>"</div>'
         '<div class="body" style="margin-top:22mm;font-size:60pt;font-style:italic;font-weight:600;line-height:1.35;color:%s">"It was '
         'great to see the insights and expertise from investors alongside ambition and talent of founders"</div>' % (WH, WH)),
    ]
    bullets = ["Find your people: founders, advisers and partners",
               "Find investors looking for real deal flow",
               "Build relationships that lead to partnerships and insight"]
    bl = "".join('<div style="display:flex;gap:9mm;align-items:flex-start;margin-bottom:%smm"><div style="flex:0 0 20mm;height:22mm;'
                 'margin-top:3mm">%s</div><div class="mont" style="font-weight:700;font-size:56pt;line-height:1.15;color:%s">%s</div></div>'
                 % (13 if i < 2 else 0, chevron(OR), WH, t) for i, t in enumerate(bullets))
    rows[2] = (rows[2][0], CH, rows[2][2], bl)
    y0, rh = head_h, 290
    half = W / 2
    for i, (ph, bg, pos, content) in enumerate(rows):
        y = y0 + i * rh
        photo_right = i % 2 == 0
        px, tx = (half, 0) if photo_right else (0, half)
        p.append(img(bake(pack, ph, half, rh, PPI, "banner_row_%d" % i, pos=pos), px, y, half, rh))
        pad_out, pad_in = 60 + b, 40
        lpad, rpad = (pad_out, pad_in) if photo_right else (pad_in, pad_out)
        p.append('<div class="abs" style="left:%smm;top:%smm;width:%smm;height:%smm;background:%s;box-sizing:border-box;'
                 'padding:0 %smm 0 %smm;display:flex;flex-direction:column;justify-content:center">%s</div>'
                 % (tx, y, half, rh, bg, rpad, lpad, content))
    by = y0 + len(rows) * rh
    bh = 220
    p.append('<div class="abs" style="left:0;top:%smm;width:%smm;height:%smm;background:%s"></div>' % (by, W, bh, DB))
    p.append(img(bake(pack, "audience_at_stage_01", 500, bh, PPI, "banner_scaling", pos=(0.3, 0.3),
                      fade=[("x", 0.45, 1.0, DB_RGB, 0.0, 1.0)]), 0, by, 500, bh))
    p.append('<div class="abs disp" style="right:%smm;top:%smm;width:430mm;text-align:right;font-size:100pt;color:%s;line-height:1.02">'
             'For businesses <em>serious</em> about <span class="o">scaling</span>.</div>' % (m, by + 52, WH))
    fy = by + bh
    p.append('<div class="abs" style="left:0;top:%smm;width:%smm;height:%smm;background:%s"></div>' % (fy, W, H - fy, OR))
    p.append(logo_tag(pack, "Climb27", "mono-white", m, fy + 32, 200))
    p.append('<div class="abs mont" style="left:%smm;top:%smm;font-weight:700;font-size:40pt;line-height:1.3;color:%s">%s<br>%s</div>'
             % (m, fy + 32 + 200 / ratio + 14, WH, TAGLINE, DATES))
    p.append('<div class="abs mont" style="right:%smm;top:%smm;font-weight:800;font-size:96pt;color:%s;letter-spacing:-.01em">%s</div>'
             % (m, fy + 52, WH, URL))
    assert fy + 150 < H - b - 60, "footer text runs into the bottom of the banner"
    return W, H, [page(pack, W, H, "\n".join(p), "Climb27 roller banner")]


# ---------------------------------------------------------------- business card (85x55mm)

def card(pack, name, phone, email, ground):
    W, H = 85 + 2 * BLEED, 55 + 2 * BLEED
    b = BLEED
    m = b + 6.3
    if ground == "orange":
        bg, ink, sub, url, lg = OR, DB, DB, DB, ("ClimbUK", "mono-white")
    else:
        bg, ink, sub, url, lg = DB, WH, LG, TI, ("ClimbUK", "reversed-dark")
    c = ['<div class="abs" style="inset:0;background:%s"></div>' % bg]
    c.append('<div class="abs mont" style="left:%smm;top:%smm;font-weight:700;font-size:13pt;color:%s;letter-spacing:-.005em">%s</div>'
             % (m, b + 12.6, ink, html.escape(name)))
    c.append('<div class="abs mont" style="left:%smm;top:%smm;font-weight:400;font-size:8pt;line-height:1.5;color:%s">%s<br>%s</div>'
             % (m, b + 21.6, sub, html.escape(phone), html.escape(email)))
    c.append('<div class="abs mont" style="left:%smm;top:%smm;font-weight:700;font-size:9pt;color:%s">www.%s</div>'
             % (m, b + 37.6, url, URL))
    qs = 21.5
    qx = W - b - 6.4 - qs
    c.append('<div class="abs" style="left:%smm;top:%smm;width:%smm;height:%smm;background:%s;padding:1.5mm;box-sizing:border-box">%s</div>'
             % (qx, b + 9.8, qs, qs, WH, qr_svg(CARD_QR, dark=DB)))
    c.append(logo_tag(pack, lg[0], lg[1], qx, b + 9.8 + qs + 2.6, qs))
    return W, H, page(pack, W, H, "\n".join(c), "%s business card" % name)


# ---------------------------------------------------------------- print to PDF

RENDER_JS = r"""
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
(async () => {
  const jobs = JSON.parse(process.argv[2]);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const j of jobs) {
    await page.goto('file://' + j.html, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    await page.pdf({ path: j.pdf, width: j.w + 'mm', height: j.h + 'mm', printBackground: true, preferCSSPageSize: true });
    if (j.png) {
      await page.setViewportSize({ width: Math.round(j.w * 96 / 25.4), height: Math.round(j.h * 96 / 25.4) });
      await page.screenshot({ path: j.png, scale: 'css' });
    }
  }
  await browser.close();
})();
"""


def set_boxes(pdf, bleed):
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import RectangleObject
    r, w = PdfReader(str(pdf)), PdfWriter()
    k = bleed / 25.4 * 72
    for pg in r.pages:
        x0, y0, x1, y1 = [float(v) for v in pg.mediabox]
        pg.bleedbox = RectangleObject([x0, y0, x1, y1])
        pg.trimbox = RectangleObject([x0 + k, y0 + k, x1 - k, y1 - k])
        pg.artbox = pg.trimbox
        w.add_page(pg)
    w.add_metadata({"/Title": pdf.stem, "/Author": "ClimbUK"})
    with open(pdf, "wb") as f:
        w.write(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", default=str(Path(__file__).resolve().parents[3]))
    ap.add_argument("--name", default="Your Name")
    ap.add_argument("--phone", default="07000 000000")
    ap.add_argument("--email", default="name@climb-group.com")
    a = ap.parse_args()
    pack = Path(a.pack)
    H = HERE / "html"
    H.mkdir(exist_ok=True)
    (HERE / "previews").mkdir(exist_ok=True)
    jobs = []

    def add(stem, w, h, doc, pdf=True):
        f = H / (stem + ".html")
        f.write_text(doc)
        jobs.append(dict(html=str(f), pdf=str(HERE / "pages" / (stem + ".pdf")), w=w, h=h,
                         png=str(HERE / "previews" / (stem + ".png"))))

    (HERE / "pages").mkdir(exist_ok=True)
    print("Photos:")
    w, h, (front, back) = flyer(pack)
    add("flyer_front", w, h, front)
    add("flyer_back", w, h, back)
    w, h, (bn,) = banner(pack)
    add("banner", w, h, bn)
    slug = a.name.lower().replace(" ", "-")
    for g in ("orange", "dark"):
        w, h, doc = card(pack, a.name, a.phone, a.email, g)
        add("card_%s" % g, w, h, doc)
    js = HERE / "render.cjs"
    js.write_text(RENDER_JS)
    subprocess.run(["node", str(js), json.dumps(jobs)], check=True)
    from pypdf import PdfWriter, PdfReader
    outs = {
        "climb27_flyer_a5.pdf": ["flyer_front", "flyer_back"],
        "climb27_roller-banner_800x2000mm.pdf": ["banner"],
        "climbuk_business-card_%s_orange_85x55mm.pdf" % slug: ["card_orange"],
        "climbuk_business-card_%s_dark_85x55mm.pdf" % slug: ["card_dark"],
    }
    for name, stems in outs.items():
        wr = PdfWriter()
        for s in stems:
            for pg in PdfReader(str(HERE / "pages" / (s + ".pdf"))).pages:
                wr.add_page(pg)
        with open(OUT / name, "wb") as f:
            wr.write(f)
        set_boxes(OUT / name, BLEED)
        print("wrote", name)


if __name__ == "__main__":
    sys.exit(main())
