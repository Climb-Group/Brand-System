"""Festival poster layouts for the Calls, Wallpapers, Social and Print and merch groups. Called from
catalogue.assets(); every entry is a normal catalogue asset dict (the copy checker and render.mjs treat it like any
other).

The pieces share the energy of the web components: real Climb26 photos under Dark Brown or orange fades, an orange
stage glow from one corner, uppercase Montserrat display lines with one orange word and one italic word, the short
orange rule, tilted stickers, ticket cards with stub notches, diagonal slabs and fine grain. On top of that sits the
hand drawn line layer from illustrations.py: one hero drawing tied to the message, with ghosted, rotated copies
behind it for depth, always clear of the type.

Photos are 1600px wide. Where a photo would be shown larger than that (4K and 5K screens, posters), it is used
blurred, as a duotone or behind a heavy fade, and crisp photos sit in tilted photo cards no bigger than the source.
pic() checks this and prints a note for any crisp photo shown above its own size.
"""
import html
import math
import random
import struct

import festival_kit as F
import illustrations as I
import motifs as M

DB, CH, OR, TI, WH = F.DB, F.CH, F.OR, F.TI, F.WH
DB_RGB, OR_RGB = F.DB_RGB, "232,113,42"
URL = F.URL
rich, plain = F.rich, F.plain

NOTES = []          # resolution notes, printed by catalogue.main()
_SIZES = {}


# ---------------------------------------------------------------- shared helpers

def _jpeg_size(path):
    if path not in _SIZES:
        with open(path, "rb") as f:
            data = f.read()
        i = 2
        while i < len(data):
            marker, length = data[i + 1], struct.unpack(">H", data[i + 2:i + 4])[0]
            if 0xC0 <= marker <= 0xC3:
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                _SIZES[path] = (w, h)
                break
            i += 2 + length
    return _SIZES[path]


class Kit:
    """Holds the catalogue module and the device scale of the piece being built (for the resolution check)."""

    def __init__(self, C, name, scale=1):
        self.C, self.name, self.scale = C, name, scale

    def pic(self, photo, x, y, w, h, pos="center", fade=None, duo=False, blur=0, rot=0, radius=0, shadow=False,
            opacity=1.0, frame=None, z=""):
        """A photo cut to cover. duo: greyscale under Climb Orange (a duotone). blur in px. A crisp photo (no blur,
        no duotone, opacity above 0.5) shown larger than its source is noted in NOTES."""
        path = self.C.PHOTOS / (photo + ".jpg")
        pw, ph = _jpeg_size(path)
        up = max(w / pw, h / ph) * self.scale
        if up > 1.08 and not duo and blur < 2 and opacity > 0.5:
            NOTES.append("%s: %s shown at %.2fx its size" % (self.name, photo, up))
        filt = []
        if duo:
            filt.append("grayscale(1) contrast(1.15) brightness(.95)")
        if blur:
            filt.append("blur(%.1fpx)" % blur)
        inset = "-%dpx" % (blur * 3) if blur else "0"
        layers = ['<div class="abs" style="inset:%s;background:url(\'%s\') %s/cover no-repeat;%s"></div>'
                  % (inset, path.as_uri(), pos, ("filter:%s" % " ".join(filt)) if filt else "")]
        if duo:
            layers.append('<div class="abs" style="inset:0;background:%s;mix-blend-mode:multiply"></div>' % OR)
        if fade:
            layers.append('<div class="abs" style="inset:0;background:%s"></div>' % fade)
        box = ("left:%.0fpx;top:%.0fpx;width:%.0fpx;height:%.0fpx;overflow:hidden;opacity:%.2f;border-radius:%.0fpx;%s%s%s%s"
               % (x, y, w, h, opacity, radius, "transform:rotate(%.1fdeg);" % rot if rot else "",
                  "box-shadow:0 %.0fpx %.0fpx rgba(0,0,0,.55);" % (h * 0.04, h * 0.12) if shadow else "",
                  "outline:%s;" % frame if frame else "", z))
        return '<div class="abs" style="%s">%s</div>' % (box, "".join(layers))


def glow(w, h, cx, cy, r, strength=0.55, colour=OR_RGB):
    """Orange stage glow: a soft radial light centred at (cx, cy) in px, radius r."""
    return ('<div class="abs" style="left:%.0fpx;top:%.0fpx;width:%.0fpx;height:%.0fpx;pointer-events:none;'
            'background:radial-gradient(circle at %.0fpx %.0fpx, rgba(%s,%.2f) 0%%, rgba(%s,%.2f) %.0fpx, rgba(%s,0) %.0fpx)"></div>'
            % (0, 0, w, h, cx, cy, colour, strength, colour, strength * 0.35, r * 0.45, colour, r))


def fade(direction, a, b, start=0.0, end=1.0, rgb=DB_RGB):
    return "linear-gradient(%s, rgba(%s,%.2f) %d%%, rgba(%s,%.2f) %d%%)" % (direction, rgb, start, a, rgb, end, b)


def rule(x, y, size):
    """The short orange rule, sized from the display type it sits over."""
    return ('<div class="abs" style="left:%.0fpx;top:%.0fpx;width:%.0fpx;height:%.0fpx;border-radius:%.0fpx;background:%s"></div>'
            % (x, y, size * 1.1, size * 0.09, size * 0.045, OR))


def head(lines, x, y, size, width, eyebrow=None, sub=None, sub_size=None, anchor="top", align="left",
         rule_on=True, colour=WH, sub_colour=TI, lh=0.95):
    """Display lines sharing one size (each shrinks to fit width), an eyebrow and the short rule above, a subline
    below. lines use [[orange]] and *italic*."""
    top = []
    if eyebrow or rule_on:
        pieces = []
        if rule_on:
            pieces.append('<span style="display:inline-block;width:%.0fpx;height:%.0fpx;border-radius:%.0fpx;background:%s;'
                          'vertical-align:middle;margin-right:%.0fpx"></span>'
                          % (size * 1.0, size * 0.085, size * 0.045, OR, size * 0.22 if eyebrow else 0))
        if eyebrow:
            pieces.append('<span class="lab" style="font-size:%.0fpx;color:%s;vertical-align:middle">%s</span>'
                          % (size * 0.2, TI, html.escape(eyebrow)))
        top.append('<div style="margin-bottom:%.0fpx;line-height:1;text-align:%s">%s</div>' % (size * 0.3, align, "".join(pieces)))
    body = "".join('<div class="disp fit" style="font-size:%.0fpx;width:%.0fpx;line-height:%.2f;color:%s;text-align:%s">%s</div>'
                   % (size, width, lh, colour, align, rich(l)) for l in lines)
    subhtml = ('<div class="body" style="font-size:%.0fpx;color:%s;margin-top:%.0fpx;line-height:1.3;text-align:%s">%s</div>'
               % (sub_size or size * 0.22, sub_colour, size * 0.32, align, rich(sub)) if sub else "")
    pos = ("left:%.0fpx;%s:%.0fpx" % (x, anchor, y))
    return '<div class="abs" style="%s;width:%.0fpx">%s<div class="fitgroup">%s</div>%s</div>' % (
        pos, width, "".join(top), body, subhtml)


def sticker(text, x, y, size, rot=-4, tone="orange", anchor="top", side="left"):
    """A tilted sticker. side="right" measures x from the right edge, so long labels never run off the canvas."""
    bg, fg = {"orange": (OR, DB), "brown": (DB, WH), "white": (WH, DB)}[tone]
    return ('<div class="sticker" style="%s:%.0fpx;%s:%.0fpx;font-size:%.0fpx;padding:%.0fpx %.0fpx;background:%s;color:%s;'
            'transform:rotate(%.1fdeg);transform-origin:%s bottom;box-shadow:0 %.0fpx %.0fpx rgba(0,0,0,.35)">%s</div>'
            % (side, x, anchor, y, size, size * 0.36, size * 0.55, bg, fg, rot, side, size * 0.12, size * 0.4,
               html.escape(text)))


def hero(name, x, y, size, rot=0, ghosts=(), label=None, seed=0, weight=1.0, ghost_ink=None):
    """One drawing tied to the message plus ghosted, rotated copies behind it. Each ghost is (dx, dy, scale, rot,
    opacity) with dx, dy as fractions of size from the hero's top left."""
    out = []
    for i, (dx, dy, k, r, o) in enumerate(ghosts):
        out.append(I.place(name, x + dx * size, y + dy * size, size * k, rotate=r, opacity=o, seed=seed + 11 + i,
                           label=label, weight=weight / max(k, 0.6) ** 0.35, ink=ghost_ink))
    out.append(I.place(name, x, y, size, rotate=rot, seed=seed, label=label, weight=weight))
    return "".join(out)


def scatter(names, box, n, size, seed, opacity=(0.14, 0.3), avoid=(), rot=25, weight=1.0, ink=None, tries=600):
    """Drawings spread through box (x0, y0, x1, y1) without touching each other or any rect in avoid."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    placed, out = [], []
    lo, hi = size if isinstance(size, tuple) else (size, size)
    k = 0
    while len(placed) < n and k < tries:
        k += 1
        s = rnd.uniform(lo, hi)
        x, y = rnd.uniform(x0, max(x0, x1 - s)), rnd.uniform(y0, max(y0, y1 - s))
        r = (x, y, x + s, y + s)
        pad = s * 0.08
        if any(not (r[2] + pad < a[0] or r[0] - pad > a[2] or r[3] + pad < a[1] or r[1] - pad > a[3]) for a in avoid):
            continue
        if any(not (r[2] + pad < a[0] or r[0] - pad > a[2] or r[3] + pad < a[1] or r[1] - pad > a[3]) for a in placed):
            continue
        placed.append(r)
        name = names[len(placed) % len(names)]
        out.append(I.place(name, x, y, s, rotate=rnd.uniform(-rot, rot), opacity=rnd.uniform(*opacity),
                           seed=len(placed), weight=weight, ink=ink))
    return "".join(out)


def pattern(names, w, h, cell, seed, opacity=1.0, rot=30, weight=1.0, ink=None, offset=0.5):
    """An all-over pattern of drawings on a staggered grid with a little jitter, for merch."""
    rnd = random.Random(seed)
    out = []
    rows = int(h / cell) + 2
    cols = int(w / cell) + 2
    k = 0
    for j in range(-1, rows):
        for i in range(-1, cols):
            x = (i + (offset if j % 2 else 0)) * cell + rnd.uniform(-0.08, 0.08) * cell
            y = j * cell + rnd.uniform(-0.08, 0.08) * cell
            s = cell * rnd.uniform(0.62, 0.74)
            out.append(I.place(names[(k * 7 + j) % len(names)], x, y, s, rotate=rnd.uniform(-rot, rot),
                               opacity=opacity, seed=k, weight=weight, ink=ink))
            k += 1
    return "".join(out)


def slab_poly(points, colour=OR, extra=""):
    """A flat shape cut with clip-path, points as px pairs; used for diagonal slabs and cut panels."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
    poly = ",".join("%.0fpx %.0fpx" % (p[0] - x0, p[1] - y0) for p in points)
    return ('<div class="abs" style="left:%.0fpx;top:%.0fpx;width:%.0fpx;height:%.0fpx;background:%s;clip-path:polygon(%s);%s"></div>'
            % (x0, y0, x1 - x0, y1 - y0, colour, poly, extra))


def chevrons(x, y, size, steps=3, colour=DB, w=None, h=None):
    return F.svg(w, h, M.ascent(w, h, x, y, size, steps=steps, colour=colour, kind="chevrons"), "pointer-events:none")


def date_ticket(C, x, y, w, h, brand="Climb27", uid="dt", stub_text=URL, main=None, fill=CH):
    """A ticket card with the edition mark and the dates in the body and the URL in the Climb Orange stub."""
    logo_h = h * 0.3
    lw = logo_h / C.logo_ratio(brand, "reversed-dark")
    room = w * 0.7 - 2 * h * 0.2 - lw - h * 0.18
    fs = min(h * 0.19, room / (len(C.DATES) * 0.56))
    main = main or ('<div style="display:flex;align-items:center;gap:%.0fpx"><img src="%s" style="width:%.0fpx;display:block" alt="">'
                    '<span class="body" style="font-size:%.0fpx;color:#fff;line-height:1.2;white-space:nowrap">%s</span></div>'
                    % (h * 0.18, C.logo(brand, "reversed-dark"), lw, fs, C.DATES))
    stub = ('<div class="lab" style="font-size:%.0fpx;color:#1E0F05;text-align:center;letter-spacing:.04em;white-space:nowrap">%s</div>'
            % (h * 0.16, html.escape(stub_text)))
    return F.ticket(x, y, w, h, w * 0.7, main, stub, fill=fill, stroke="rgba(255,255,255,.16)", stub_fill=OR, uid=uid,
                    pad=h * 0.2)


def asset(name, group, brand, w, h, parts, copy, scale=1, transparent=False, ground="dark-brown", css=""):
    return dict(name=name, group=group, brand=brand, w=w, h=h, scale=scale, transparent=transparent, ground=ground,
                motif=None, extra_html="\n".join(parts) + F.FIT_JS, extra_css=CSS_C[0] + css, copy=copy)


CSS_C = [""]


# ---------------------------------------------------------------- brand content

BRANDS = {
    "Climb27": dict(sticker="30 June and 1 July 2027", lines=["Your *business*.", "Bigger [[stage]]."],
                    eyebrow="Climb27", heroes=["spotlight", "tickets", "microphone", "rocket"],
                    extras=["badge", "glasses", "trophy", "calendar", "bubbles", "sparkles"],
                    photos=["climb_band_stage", "climb_crowd_wide", "climb_awards_winners", "climb_stage_region"]),
    "ClimbUK": dict(sticker="Find your people", lines=["*Find* your", "[[people]]."],
                    eyebrow="The Festival for Business Growth", heroes=["microphone", "bubbles", "handshake", "chart"],
                    extras=["coffee", "people", "lightbulb", "tickets", "glasses", "sparkles"],
                    photos=["climb_crowd_wide", "climb_drinks_reception", "climb_isn_founders_hero", "climb_awards_winners"]),
    "ClimbGroup": dict(sticker="Business with a party", lines=["*Business* with", "a [[party]]."],
                       eyebrow="The Festival for Business Growth", heroes=["glasses", "lightbulb", "people", "summit"],
                       extras=["record", "megaphone", "chart", "laptop", "handshake", "sparkles"],
                       photos=["climb_drinks_reception", "climb_awards_trophies", "climb_expo_floor", "climb_band_stage"]),
}


# ---------------------------------------------------------------- Calls

def call_bg(C, brand, i, motif):
    """3840x2160. The centre 1800x1400 stays calm for the person; the edges carry the glow, the drawings and a
    sticker; the logo sits top left."""
    w, h = 3840, 2160
    name = "%s_call-bg_%s_%dx%d" % (brand.lower(), motif, w, h)
    K = Kit(C, name)
    B = BRANDS[brand]
    centre = (w / 2 - 980, h / 2 - 760, w / 2 + 980, h / 2 + 760)
    logo_box = (0, 0, w * 0.24, h * 0.2)
    p = []
    copy = [B["sticker"]]
    heroes = B["heroes"]
    if motif == "stage-light":
        p.append(glow(w, h, w * 1.0, 0, w * 0.62, 0.5))
        p.append(glow(w, h, 0, h, w * 0.35, 0.22))
        p.append(F.svg(w, h, M.contours(w, h, seed=11, rings=9, dark=True, marker=False, cx=1.02, cy=-0.05)))
        p.append(hero(heroes[0], w - 980, 140, 760, rot=-6,
                      ghosts=[(-0.5, 0.75, 0.7, 18, 0.2), (0.35, 1.05, 0.55, -20, 0.14), (-0.1, -0.35, 0.5, 10, 0.12)]))
        p.append(scatter(B["extras"], (60, h * 0.5, w * 0.25, h - 80), 4, (240, 330), seed=3, avoid=[centre]))
        p.append(sticker(B["sticker"], 160, h - 280, 70, rot=-4, side="right"))
    elif motif == "contours":
        p.append(F.svg(w, h, M.contours(w, h, seed=12, rings=14, dark=True, marker=True, cx=-0.02, cy=1.04)))
        p.append(F.svg(w, h, M.slabs(w, h, corners=("br",), length=w * 0.22, thick=h * 0.06)))
        p.append(glow(w, h, w, h, w * 0.4, 0.35))
        p.append(hero(heroes[1], 120, h - 900, 720, rot=8,
                      ghosts=[(0.55, -0.5, 0.6, -14, 0.18), (0.95, 0.25, 0.45, 22, 0.13)]))
        p.append(scatter(B["extras"], (w * 0.76, 120, w - 60, h * 0.78), 5, (230, 320), seed=5, avoid=[centre]))
        p.append(sticker(B["sticker"], 150, 150, 66, rot=3, side="right"))
    elif motif == "connections":
        # Photo edges: blurred duotone columns (the source is 1600px wide, so a crisp photo would be upscaled).
        cw = 1020
        p.append(K.pic(B["photos"][0], 0, 0, cw, h, pos="60% 40%", duo=True, blur=5,
                       fade=fade("to right", 0, 100, 0.25, 1)))
        p.append(K.pic(B["photos"][1], w - cw, 0, cw, h, pos="40% 40%", duo=True, blur=5,
                       fade=fade("to left", 0, 100, 0.25, 1)))
        p.append(F.svg(w, h, M.connections(w, h, seed=13, dots=26, dark=True, region=(0.3, 0.0, 0.7, 0.16)), "opacity:.6"))
        p.append(hero(heroes[2], w - 860, h - 980, 700, rot=-8,
                      ghosts=[(-0.25, -0.75, 0.6, 16, 0.22), (0.4, -1.15, 0.45, -12, 0.15)]))
        p.append(hero(B["extras"][0], 120, h - 760, 520, rot=10, ghosts=[(0.5, -0.65, 0.6, -18, 0.2)]))
        p.append(sticker(B["sticker"], 150, h - 300, 66, rot=-5))
        logo_box = None
    else:  # ascent
        p.append(slab_poly([(w - 1250, h), (w, h - 1120), (w, h)], OR))
        p.append(chevrons(w - 520, h - 120, 520, steps=3, colour=DB, w=w, h=h))
        p.append(glow(w, h, w * 0.92, h * 0.85, w * 0.45, 0.4))
        p.append(F.svg(w, h, M.contours(w, h, seed=14, rings=8, dark=True, marker=False, cx=0.0, cy=0.1)))
        p.append(hero(heroes[3], w - 900, 180, 700, rot=0,
                      ghosts=[(-0.35, 0.55, 0.5, 10, 0.18), (-0.62, 0.95, 0.36, 18, 0.12)]))
        p.append(scatter(B["extras"], (60, h * 0.3, w * 0.24, h - 60), 3, (240, 320), seed=7,
                         avoid=[centre, (0, h - 480, 1720, h)]))
        p.append(date_ticket(C, 110, h - 420, 1560, 300, brand, uid="ct", fill=DB) if brand == "Climb27" else
                 sticker(B["sticker"], 150, h - 300, 66, rot=-4))
        if brand == "Climb27":
            copy += [C.DATES, URL]
    p.append(F.grain_layer(w, h, 70 + i, 0.06))
    p.append(F.logo_img(C, brand, "reversed-dark", w * 0.04, h * 0.06, w * 0.15))
    return asset(name, "Calls", brand, w, h, p, copy, ground="charcoal" if motif == "ascent" else "dark-brown")


# ---------------------------------------------------------------- Wallpapers

def links(cx, cy, pts, w, h, sw):
    """Dashed hand drawn links from a hero to its satellites (the connections idea, drawn loosely)."""
    out = []
    rnd = random.Random(int(cx + cy))
    for (x, y) in pts:
        mx, my = (cx + x) / 2 + rnd.uniform(-1, 1) * 0.12 * abs(x - cx), (cy + y) / 2 + rnd.uniform(-1, 1) * 0.12 * abs(y - cy)
        out.append('<path d="M%.0f %.0f Q%.0f %.0f %.0f %.0f" fill="none" stroke="%s" stroke-opacity=".45" stroke-width="%.1f" '
                   'stroke-linecap="round" stroke-dasharray="%.1f %.1f"/>' % (cx, cy, mx, my, x, y, OR, sw, sw * 0.2, sw * 3))
    return F.svg(w, h, "".join(out), "pointer-events:none")


def constellation(hero_name, extras, cx, cy, size, orbit, seed, angles=(200, 250, 300, 345, 30, 120), sat=0.34):
    """A hero drawing with satellites around it on dashed links: the illustration led layout."""
    pts, parts = [], []
    for i, a in enumerate(angles[:len(extras)]):
        r = orbit * (0.9 + 0.2 * ((i * 37) % 10) / 10)
        x = cx + r * math.cos(math.radians(a))
        y = cy + r * math.sin(math.radians(a))
        pts.append((x, y))
        s = size * sat * (0.85 + 0.3 * ((i * 53) % 10) / 10)
        parts.append(I.place(extras[i], x - s / 2, y - s / 2, s, rotate=((i * 29) % 40) - 20, opacity=0.95, seed=seed + i))
    return pts, "".join(parts)


def desktop(C, brand, i, motif, w, h):
    u = w / 2560
    name = "%s_desktop_%s_%dx%d" % (brand.lower(), motif, w, h)
    K = Kit(C, name)
    B = BRANDS[brand]
    p, copy = [], []
    logo_at = (w * 0.86, h * 0.89)
    if motif == "stage-light":  # photo led
        p.append(K.pic(B["photos"][0], w * 0.3, 0, w * 0.7, h, pos="center 35%", duo=True, blur=10 * u,
                       fade=fade("to left", 10, 95, 0.0, 1)))
        p.append(glow(w, h, w, 0, w * 0.55, 0.5))
        cw = w * 0.3
        p.append(K.pic(B["photos"][1], w * 0.47, h * 0.14, cw, cw * 0.62, pos="center 40%", rot=-4, radius=14 * u,
                       shadow=True))
        cw2 = w * 0.24
        p.append(K.pic(B["photos"][2], w * 0.66, h * 0.45, cw2, cw2 * 0.66, pos="center 35%", rot=5, radius=14 * u,
                       shadow=True))
        p.append(sticker(B["sticker"], w * 0.455, h * 0.115, 30 * u, rot=-6))
        p.append(hero(B["heroes"][0], w * 0.565, h * 0.56, w * 0.13, rot=-6,
                      ghosts=[(-0.65, -0.2, 0.7, 14, 0.25), (-1.05, 0.35, 0.5, -18, 0.16)]))
        copy.append(B["sticker"])
    elif motif == "contours":  # type led
        p.append(F.svg(w, h, M.contours(w, h, seed=21, rings=13, dark=True, marker=True, cx=1.0, cy=1.05)))
        p.append(glow(w, h, w * 0.9, 0, w * 0.45, 0.32))
        p.append(F.svg(w, h, M.slabs(w, h, corners=("br",), length=w * 0.2, thick=h * 0.05)))
        sub = C.TAGLINE + "." if brand == "Climb27" else "Climb27. " + C.DATES + "."
        p.append(head(B["lines"], w * 0.3, h * 0.3, 190 * u, w * 0.6, eyebrow=B["eyebrow"], sub=sub, sub_size=34 * u))
        p.append(hero(B["heroes"][1], w * 0.8, h * 0.2, w * 0.11, rot=8, ghosts=[(-0.55, -0.45, 0.55, -16, 0.18)]))
        p.append(sticker(B["sticker"] if brand != "Climb27" else "Get your ticket", w * 0.3, h * 0.84, 30 * u, rot=-4))
        copy += [plain(" ".join(B["lines"])), B["eyebrow"], sub, B["sticker"], "Get your ticket"]
        logo_at = (w * 0.86, h * 0.07)
    elif motif == "connections":  # illustration led
        p.append(glow(w, h, w * 0.95, h * 1.0, w * 0.6, 0.45))
        p.append(glow(w, h, w * 0.6, h * 0.45, w * 0.25, 0.12))
        cx, cy, s = w * 0.62, h * 0.48, w * 0.2
        pts, sats = constellation(B["heroes"][2], B["extras"], cx, cy, s, w * 0.21, seed=3)
        p.append(links(cx, cy, pts, w, h, 5 * u))
        p.append(I.place(B["heroes"][2], cx - s * 1.1, cy - s * 1.0, s * 2.2, rotate=12, opacity=0.08, seed=9))
        p.append(sats)
        p.append(I.place(B["heroes"][2], cx - s / 2, cy - s / 2, s, rotate=-4, seed=1))
        p.append(sticker(B["sticker"], cx - s * 0.2, cy + s * 0.55, 30 * u, rot=-4))
        copy.append(B["sticker"])
    else:  # ascent
        p.append(slab_poly([(w * 0.42, h), (w, h * 0.32), (w, h)], OR))
        p.append(chevrons(w * 0.83, h * 0.93, w * 0.12, steps=3, colour=DB, w=w, h=h))
        p.append(F.svg(w, h, M.contours(w, h, seed=24, rings=9, dark=True, marker=False, cx=0.3, cy=-0.1)))
        p.append(glow(w, h, w * 0.7, h * 0.65, w * 0.35, 0.3))
        p.append(hero(B["heroes"][3], w * 0.5, h * 0.12, w * 0.16, rot=0,
                      ghosts=[(-0.42, 0.5, 0.6, 8, 0.2), (-0.75, 0.95, 0.4, 16, 0.12)]))
        if brand == "Climb27":
            p.append(date_ticket(C, w * 0.56, h * 0.74, w * 0.32, w * 0.06, brand, uid="dk", fill=DB))
            copy += [C.DATES, URL]
        else:
            p.append(sticker(B["sticker"], w * 0.62, h * 0.8, 34 * u, rot=-4, tone="brown"))
            copy.append(B["sticker"])
        logo_at = (w * 0.86, h * 0.07)
    p.append(F.grain_layer(w, h, 80 + i, 0.05))
    p.append(F.logo_img(C, brand, "reversed-dark", logo_at[0], logo_at[1], w * 0.1))
    return asset(name, "Wallpapers", brand, w, h, p, copy, ground="charcoal" if motif == "ascent" else "dark-brown")


def phone(C, brand, i, motif, w, h):
    """Clock area (top 25 percent) and dock (bottom 12 percent) stay clear of anything busy."""
    u = w / 1179
    name = "%s_phone_%s_%dx%d" % (brand.lower(), motif, w, h)
    K = Kit(C, name)
    B = BRANDS[brand]
    p, copy = [], []
    logo_w = w * 0.3
    logo_xy = ((w - logo_w) / 2, h * 0.815)
    if motif == "stage-light":
        p.append(K.pic(B["photos"][0], 0, h * 0.2, w, h * 0.8, pos="center", duo=True, blur=8 * u,
                       fade="linear-gradient(to bottom, rgba(%s,1) 0%%, rgba(%s,.2) 30%%, rgba(%s,.5) 75%%, rgba(%s,1) 100%%)"
                       % (DB_RGB, DB_RGB, DB_RGB, DB_RGB)))
        p.append(glow(w, h, w, h * 0.22, w * 0.9, 0.4))
        p.append(K.pic(B["photos"][1], w * 0.08, h * 0.31, w * 0.76, w * 0.5, pos="center 40%", rot=-5, radius=18 * u, shadow=True))
        p.append(K.pic(B["photos"][2], w * 0.26, h * 0.5, w * 0.66, w * 0.44, pos="center 35%", rot=5, radius=18 * u, shadow=True))
        p.append(sticker(B["sticker"], w * 0.06, h * 0.293, 40 * u, rot=-6))
        p.append(hero(B["heroes"][0], w * 0.04, h * 0.6, w * 0.34, rot=-8, ghosts=[(1.9, -0.95, 0.45, 18, 0.2)]))
        copy.append(B["sticker"])
    elif motif == "contours":
        p.append(F.svg(w, h, M.contours(w, h, seed=31, rings=12, dark=True, marker=True, cx=0.9, cy=0.92)))
        p.append(glow(w, h, 0, h * 0.3, w * 0.9, 0.3))
        lines = B["lines"]
        p.append(head(lines, w * 0.08, h * 0.37, 170 * u, w * 0.84, eyebrow=None, rule_on=True, lh=0.98))
        p.append(hero(B["heroes"][1], w * 0.6, h * 0.53, w * 0.3, rot=8, ghosts=[(-0.6, 0.3, 0.6, -14, 0.2)]))
        p.append(sticker(B["sticker"] if brand != "Climb27" else C.DATES, w * 0.08, h * 0.565, 38 * u, rot=-4))
        copy += [plain(" ".join(lines)), B["sticker"], C.DATES]
    elif motif == "connections":
        p.append(glow(w, h, w * 0.5, h * 0.5, w * 0.9, 0.3))
        cx, cy, s = w * 0.5, h * 0.52, w * 0.42
        pts, sats = constellation(B["heroes"][2], B["extras"][:5], cx, cy, s, w * 0.36, seed=5,
                                  angles=(215, 270, 325, 30, 150), sat=0.42)
        p.append(links(cx, cy, pts, w, h, 5 * u))
        p.append(I.place(B["heroes"][2], cx - s, cy - s, s * 2, rotate=14, opacity=0.08, seed=9))
        p.append(sats)
        p.append(I.place(B["heroes"][2], cx - s / 2, cy - s / 2, s, rotate=-4, seed=1))
        copy.append(B["sticker"])
        p.append(sticker(B["sticker"], w * 0.2, h * 0.7, 38 * u, rot=-4))
    else:
        p.append(slab_poly([(0, h * 0.78), (w, h * 0.56), (w, h), (0, h)], OR))
        p.append(chevrons(w * 0.62, h * 0.8, w * 0.28, steps=3, colour=DB, w=w, h=h))
        p.append(glow(w, h, w * 0.5, h * 0.6, w * 0.8, 0.3))
        p.append(hero(B["heroes"][3], w * 0.28, h * 0.3, w * 0.5, rot=0,
                      ghosts=[(-0.35, 0.45, 0.55, 10, 0.18), (0.75, -0.1, 0.35, -12, 0.12)]))
        logo_xy = (w * 0.08, h * 0.83)
        logo_w = w * 0.3
    p.append(F.grain_layer(w, h, 90 + i, 0.05))
    variant = "reversed-dark" if motif != "ascent" else "mono-white"
    p.append(F.logo_img(C, brand, variant, logo_xy[0], logo_xy[1], logo_w))
    return asset(name, "Wallpapers", brand, w, h, p, copy)


# ---------------------------------------------------------------- Social

HEADER_LINES = {"Climb27": "Your *business*. Bigger [[stage]].", "ClimbUK": "*Find* your [[people]].",
                "ClimbGroup": "*Business* with a [[party]]."}


def linkedin_company(C, brand):
    """1128x191 at 2x. The page logo covers the bottom left, so the left fifth carries only glow and ghosts; the
    line and the hero drawing sit in the centre 800x120."""
    w, h = 1128, 191
    name = "%s_linkedin-company_contours_%dx%d" % (brand.lower(), w * 2, h * 2)
    K = Kit(C, name, 2)
    B = BRANDS[brand]
    line = HEADER_LINES[brand]
    p = [F.svg(w, h, M.contours(w, h, seed=41, rings=9, dark=True, marker=False, cx=0.05, cy=0.9)),
         K.pic(B["photos"][1], w * 0.66, 0, w * 0.34, h, pos="center 35%",
               fade="linear-gradient(to right, rgba(%s,1) 0%%, rgba(%s,.2) 45%%, rgba(%s,0) 100%%)" % (DB_RGB, DB_RGB, DB_RGB)),
         glow(w, h, w * 0.62, h * 1.1, 260, 0.45),
         I.place(B["heroes"][0], 20, -10, 150, rotate=-14, opacity=0.14, seed=4),
         head([line], 190, 50, 42, 470, rule_on=True),
         hero(B["heroes"][0], 650, 28, 128, rot=-6, ghosts=[(-0.55, 0.3, 0.6, 14, 0.2)]),
         sticker(B["sticker"] if brand != "Climb27" else "Get your ticket", 20, 18, 13, rot=4, side="right")]
    copy = [plain(line), B["eyebrow"], C.DATES, B["sticker"], "Get your ticket"]
    return asset(name, "Social", brand, w, h, p, copy, scale=2)


def x_header(C, brand):
    """1500x500 at 2x. Avatar bottom left; the line sits inside the centre 1000x300; a slanted photo wall runs
    off the right edge."""
    w, h = 1500, 500
    name = "%s_x-header_stage-light_%dx%d" % (brand.lower(), w * 2, h * 2)
    K = Kit(C, name, 2)
    B = BRANDS[brand]
    p = [glow(w, h, 0, h, 620, 0.42), glow(w, h, w * 0.66, 0, 420, 0.28)]
    tiles = B["photos"][:3]
    x0, tw, skew = 1000, 230, 120
    for k, ph in enumerate(tiles):
        x = x0 + k * (tw + 10) - 60
        poly = [(x + skew, 0), (x + skew + tw, 0), (x + tw, h), (x, h)]
        p.append('<div class="abs" style="left:%.0fpx;top:0;width:%.0fpx;height:%.0fpx;clip-path:polygon(%s)">%s</div>'
                 % (x, tw + skew, h, ",".join("%.0fpx %.0fpx" % (a - x, b) for a, b in poly),
                    K.pic(ph, 0, 0, tw + skew, h, pos="center 35%",
                          fade="linear-gradient(to bottom, rgba(%s,0) 55%%, rgba(%s,.7) 100%%)" % (DB_RGB, DB_RGB))))
    p.append(slab_poly([(x0 - 60 - 22, h), (x0 - 60 + skew - 22, 0), (x0 - 60 + skew - 6, 0), (x0 - 60 - 6, h)], OR))
    p.append(head([HEADER_LINES[brand]], 270, 150, 64, 640, eyebrow=B["eyebrow"] if brand != "Climb27" else C.DATES))
    p.append(hero(B["heroes"][0], 800, 250, 190, rot=-8, ghosts=[(-0.55, -0.9, 0.55, 14, 0.18), (-1.1, 0.15, 0.45, -16, 0.12)]))
    p.append(sticker(B["sticker"] if brand != "Climb27" else URL, 90, 60, 22, rot=4, side="right"))
    p.append(F.logo_img(C, brand, "reversed-dark", 270, 64, 170))
    copy = [plain(HEADER_LINES[brand]), B["eyebrow"], C.DATES, B["sticker"], URL]
    return asset(name, "Social", brand, w, h, p, copy, scale=2)


def facebook_cover(C, brand):
    """1640x624 at 2x. Phones crop the sides, so the line and the hero sit in the centre; photos and ghosts fill
    the edges."""
    w, h = 1640, 624
    name = "%s_facebook-cover_connections_%dx%d" % (brand.lower(), w * 2, h * 2)
    K = Kit(C, name, 2)
    B = BRANDS[brand]
    p = [K.pic(B["photos"][2], 0, 0, 420, h, pos="center", duo=True, fade=fade("to right", 0, 100, 0.2, 1)),
         K.pic(B["photos"][0], w - 420, 0, 420, h, pos="center", duo=True, fade=fade("to left", 0, 100, 0.2, 1)),
         glow(w, h, w / 2, h * 1.05, 700, 0.42),
         F.svg(w, h, M.connections(w, h, seed=43, dots=22, dark=True, region=(0.25, 0.0, 0.75, 0.22)), "opacity:.5")]
    p.append(head([HEADER_LINES[brand]], 330, 300, 74, 760, eyebrow=B["eyebrow"] if brand != "Climb27" else C.DATES))
    p.append(hero(B["heroes"][2], 1110, 150, 260, rot=-6, ghosts=[(0.55, -0.35, 0.55, 16, 0.2)]))
    p.append(F.logo_img(C, brand, "reversed-dark", 330, 150, 220))
    p.append(scatter(B["extras"], (40, 40, 360, h - 40), 3, (110, 140), seed=6, opacity=(0.5, 0.7)))
    p.append(sticker(B["sticker"] if brand != "Climb27" else "Get your ticket", 340, h - 110, 22, rot=-4, side="right"))
    copy = [plain(HEADER_LINES[brand]), B["eyebrow"], C.DATES, B["sticker"], "Get your ticket"]
    return asset(name, "Social", brand, w, h, p, copy, scale=2)


def youtube_banner(C, brand, tone):
    """2560x1440, the YouTube channel art. TVs show it all, desktops a 2560x423 band and phones only the centre
    1546x423, so the logo and the line sit inside that safe area; photos, glow and ghosts fill the rest.
    tone "dark" is Dark Brown with the orange word; "orange" is a Climb Orange ground with Dark Brown type, the
    emphasis word in White and the mono dark logo."""
    w, h = 2560, 1440
    sx, sy, sw, sh = (w - 1546) // 2, (h - 423) // 2, 1546, 423
    name = "%s_youtube-banner_%s_%dx%d" % (brand.lower(), tone, w, h)
    K = Kit(C, name, 1)
    B = BRANDS[brand]
    line = HEADER_LINES[brand]
    dark = tone == "dark"
    p = []
    if dark:
        p.append(K.pic(B["photos"][0], 0, 0, w, h, pos="center 40%", duo=True, blur=6,
                       fade="radial-gradient(ellipse at center, rgba(%s,.92) 0%%, rgba(%s,.78) 45%%, rgba(%s,.35) 100%%)"
                       % (DB_RGB, DB_RGB, DB_RGB)))
        p.append(glow(w, h, w * 0.5, h * 0.62, 900, 0.4))
    else:
        p.append('<div class="abs" style="left:0;top:0;width:%dpx;height:%dpx;background:%s"></div>' % (w, h, OR))
        p.append(scatter(B["extras"], (80, 80, w - 80, sy - 60), 6, (150, 200), seed=9, opacity=(0.18, 0.28), ink=DB))
    # band photos left and right of the safe area, so the desktop crop still shows real people
    for k, ph in enumerate(B["photos"][1:3]):
        x = 60 if k == 0 else sx + sw + 60
        p.append(K.pic(ph, x, sy, sx - 120, sh, pos="center 35%", radius=18, rot=-3 if k == 0 else 3,
                       duo=not dark, fade=None if dark else fade("to bottom", 0, 100, 0.0, 0.25)))
    ink = DB if not dark else WH
    p.append(head([line], sx + 60, sy + 130, 118, 1100, eyebrow=B["eyebrow"] if brand != "Climb27" else C.DATES,
                  colour=ink, sub_colour=ink, rule_on=dark))
    p.append(F.logo_img(C, brand, "reversed-dark" if dark else "mono-dark", sx + 60, sy + 30, 260))
    if dark:
        p.append(hero(B["heroes"][0], sx + sw - 330, sy + 70, 260, rot=-6, ghosts=[(-0.6, 0.2, 0.5, 14, 0.18)]))
    else:
        p.append(I.place(B["heroes"][0], sx + sw - 330, sy + 70, 260, rotate=-6, ink=DB))
    css = "" if dark else ".o{color:%s !important}.lab{color:%s !important}" % (WH, DB)
    copy = [plain(line), B["eyebrow"], C.DATES]
    return asset(name, "Social", brand, w, h, p, copy, scale=1, css=css)


def see_you(C):
    """1584x396 at 2x, the personal LinkedIn banner for the team, speakers and partners. The profile photo sits
    bottom left, so everything that matters is in the right two thirds."""
    w, h = 1584, 396
    name = "climb27_linkedin-personal_see-you_%dx%d" % (w * 2, h * 2)
    K = Kit(C, name, 2)
    p = [K.pic("climb_crowd_wide", 0, 0, w, h, pos="center 40%", duo=True, blur=3,
               fade="linear-gradient(to right, rgba(%s,.55) 0%%, rgba(%s,.85) 45%%, rgba(%s,1) 70%%)" % (DB_RGB, DB_RGB, DB_RGB)),
         glow(w, h, w * 0.55, h, 520, 0.4)]
    p.append(hero("tickets", 520, 90, 230, rot=-10, ghosts=[(-0.55, -0.25, 0.6, 16, 0.22), (-0.95, 0.45, 0.45, -10, 0.14)]))
    tx, ty, tw, th = 790, 58, 730, 280
    main = ('<div class="lab" style="font-size:17px;color:#F2AE86">Climb27</div>'
            '<div class="disp" style="font-size:66px;margin-top:10px">%s</div>'
            '<div class="body" style="font-size:22px;color:#fff;margin-top:14px">%s</div>'
            % (rich("See *you* [[there]]."), C.DATES))
    stub = ('<div style="display:flex;flex-direction:column;align-items:center;gap:14px"><img src="%s" style="width:150px" alt="">'
            '<div class="lab" style="font-size:15px;color:#1E0F05;letter-spacing:.06em">%s</div></div>'
            % (C.logo("Climb27", "mono-white"), URL))
    p.append(F.ticket(tx, ty, tw, th, tw - 220, main, stub, fill=CH, stroke="rgba(255,255,255,.16)", stub_fill=OR,
                      uid="sy", pad=42, r=24, notch=26))
    p.append(sticker("I'm going", tx - 10, ty - 24, 22, rot=-5))
    copy = ["Climb27", "See you there.", C.DATES, URL, "I'm going"]
    return asset(name, "Social", "Climb27", w, h, p, copy, scale=2)


PACKS = {
    # key: display lines, hero drawing, ghosts and extras, crisp photo, second photo, glow corner
    "find-your-people": dict(lines=["*Find* your", "[[people]]."], hero="bubbles",
                             extras=["coffee", "handshake", "people"], photo="climb_crowd_wide",
                             photo2="climb_drinks_reception"),
    "main-stage-moments": dict(lines=["Main *stage*", "[[moments]]."], hero="microphone",
                               extras=["spotlight", "trophy", "record"], photo="climb_band_stage",
                               photo2="climb_awards_trophies"),
    "bigger-stage": dict(lines=["Your *business*.", "Bigger [[stage]]."], hero="rocket",
                         extras=["chart", "megaphone", "summit"], photo="climb_stage_region", photo2="climb_expo_floor"),
}


def _cut_photo(K, photo, w, ph, yl, yr, pos, top=0):
    """The photo full bleed above a diagonal from (0, yl) to (w, yr), fading into Dark Brown towards the cut, with
    a soft dark band at the top for the logo. top starts the photo lower (stories keep the logo on plain ground). Nothing below the cut, so stickers and drawings never sit on a face."""
    clip = "polygon(0 0,%dpx 0,%dpx %dpx,0 %dpx)" % (w, w, yr - top, yl - top)
    return ('<div class="abs" style="left:0;top:%dpx;width:%dpx;height:%dpx;clip-path:%s">%s</div>'
            % (top, w, ph - top, clip, K.pic(photo, 0, 0, w, ph - top, pos=pos,
                                  fade="linear-gradient(to bottom, rgba(%s,.75) 0%%, rgba(%s,0) 24%%, rgba(%s,0) 60%%, rgba(%s,.9) 100%%)"
                                  % (DB_RGB, DB_RGB, DB_RGB, DB_RGB))))


def pack_post(C, key):
    """1080x1350 at 2x: the photo runs full bleed across the top, fades into Dark Brown and ends on an orange
    diagonal slab. The dates and the hero drawing sit under the slab, the line below, the ticket at the foot."""
    w, h = 1080, 1350
    P = PACKS[key]
    name = "climb27_post_%s_%dx%d" % (key, w * 2, h * 2)
    K = Kit(C, name, 2)
    yl, yr = 690, 590
    p = [_cut_photo(K, P["photo"], w, yl, yl, yr, "center 30%"),
         slab_poly([(0, yl - 4), (w, yr - 4), (w, yr + 14), (0, yl + 14)], OR),
         glow(w, h, w, h, 620, 0.3)]
    p.append(F.logo_img(C, "Climb27", "reversed-dark", 64, 64, 280))
    p.append(hero(P["hero"], 860, 625, 150, rot=-8, ghosts=[(-0.7, 0.2, 0.5, 16, 0.2)]))
    p.append(sticker(C.DATES, 64, 716, 28, rot=-3))
    p.append(head(P["lines"], 64, 800, 130, 952, rule_on=False, sub=C.TAGLINE + ".", sub_size=32))
    p.append(date_ticket(C, 64, h - 64 - 130, 952, 130, uid="pp", stub_text=URL,
                         main='<div class="lab" style="font-size:30px;color:#fff;letter-spacing:.06em">Get your ticket</div>'))
    copy = [C.DATES, plain(" ".join(P["lines"])), C.TAGLINE, "Get your ticket", URL]
    return asset(name, "Social", "Climb27", w, h, p, copy, scale=2)


def pack_story(C, key):
    """1080x1920 at 2x. Nothing in the top 250 or the bottom 340. The logo sits on plain ground, the photo runs
    full bleed under it and ends on an orange diagonal slab; the dates and the drawing sit under it, the line below."""
    w, h = 1080, 1920
    P = PACKS[key]
    name = "climb27_story_%s_%dx%d" % (key, w * 2, h * 2)
    K = Kit(C, name, 2)
    yl, yr = 930, 800
    p = [_cut_photo(K, P["photo"], w, yl, yl, yr, "center 35%", top=400),
         glow(w, h, 0, 300, 700, 0.35),
         slab_poly([(0, yl - 4), (w, yr - 4), (w, yr + 16), (0, yl + 16)], OR),
         glow(w, h, w, h, 760, 0.3)]
    p.append(F.logo_img(C, "Climb27", "reversed-dark", 90, 280, 300))
    p.append(hero(P["hero"], 830, 840, 170, rot=-10, ghosts=[(-0.75, 0.25, 0.5, 18, 0.2)]))
    p.append(sticker(C.DATES, 90, 962, 30, rot=-3))
    p.append(head(P["lines"], 90, 1050, 128, 900, rule_on=True, sub=C.TAGLINE + ".", sub_size=32))
    p.append(scatter(P["extras"], (40, h - 320, w - 40, h - 30), 3, (190, 230), seed=8, opacity=(0.16, 0.26)))
    p.append(date_ticket(C, 90, h - 340 - 116, 900, 116, uid="ps", stub_text=URL,
                         main='<div class="lab" style="font-size:30px;color:#fff;letter-spacing:.06em">Get your ticket</div>'))
    copy = [C.DATES, plain(" ".join(P["lines"])), C.TAGLINE, "Get your ticket", URL]
    return asset(name, "Social", "Climb27", w, h, p, copy, scale=2)


def pack_square(C, key):
    """1200x1200 at 2x for LinkedIn: a photo panel cut on the diagonal at the top right, an orange slab along the
    cut, the hero drawing bridging the cut, the line at the foot."""
    w, h = 1200, 1200
    P = PACKS[key]
    name = "climb27_linkedin_%s_%dx%d" % (key, w * 2, h * 2)
    K = Kit(C, name, 2)
    ph = 560
    cut = [(560, 0), (w, 0), (w, ph), (380, ph)]
    p = [F.svg(w, h, M.contours(w, h, seed=51, rings=10, dark=True, marker=False, cx=-0.05, cy=1.05)),
         '<div class="abs" style="left:380px;top:0;width:820px;height:%dpx;clip-path:polygon(%s)">%s</div>'
         % (ph, ",".join("%.0fpx %.0fpx" % (a - 380, b) for a, b in cut),
            K.pic(P["photo"], 0, 0, 820, ph, pos="center 30%",
                  fade="linear-gradient(to bottom, rgba(%s,0) 60%%, rgba(%s,.6) 100%%)" % (DB_RGB, DB_RGB))),
         slab_poly([(536, 0), (560, 0), (380, ph), (356, ph)], OR),
         slab_poly([(380, ph), (w, ph), (w, ph + 18), (362, ph + 18)], OR),
         glow(w, h, 0, 0, 640, 0.4)]
    p.append(F.logo_img(C, "Climb27", "reversed-dark", 72, 76, 320))
    p.append(sticker(C.DATES, 72, 210, 28, rot=-4))
    p.append(hero(P["hero"], 150, 330, 330, rot=-6, ghosts=[(0.75, -0.55, 0.5, 14, 0.2), (-0.3, -0.15, 0.55, -16, 0.22)]))
    p.append(head(P["lines"], 72, 690, 134, 1056, rule_on=True, sub=C.TAGLINE + ". " + URL, sub_size=30))
    for k, nm in enumerate(P["extras"][1:]):
        p.append(I.place(nm, w - 230 - k * 170, h - 230 + k * 40, 150, rotate=10 - k * 20, opacity=0.35, seed=k))
    copy = [C.DATES, plain(" ".join(P["lines"])), C.TAGLINE, URL]
    return asset(name, "Social", "Climb27", w, h, p, copy, scale=2)


def footer_strip(C):
    """600x96 at 2x on Charcoal: the drawings drifting along the top of the marketing email footer. Decoration
    only (the footer's words stay live text), so it carries no copy."""
    w, h = 600, 96
    name = "climbuk_email-footer-doodles_%dx%d" % (w * 2, h * 2)
    names = ["bubbles", "microphone", "tickets", "coffee", "rocket", "glasses", "trophy", "people", "megaphone"]
    p = ['<div class="abs" style="inset:0;background:linear-gradient(100deg, rgba(%s,0) 40%%, rgba(%s,.22) 100%%)"></div>'
         % (OR_RGB, OR_RGB)]
    for k, nm in enumerate(names):
        s = 64 + (k * 37) % 18
        p.append(I.place(nm, 18 + k * 64, 14 + (k % 2) * 8, s, rotate=((k * 29) % 36) - 18,
                         opacity=1.0 if k in (0, 4, 6) else 0.45, seed=k, ground=CH, weight=1.2))
    return asset(name, "Social", "ClimbUK", w, h, p, [], scale=2, ground="charcoal")


# ---------------------------------------------------------------- Print and merch

def foot_ticket(C, x, y, w, h, uid):
    return date_ticket(C, x, y, w, h, uid=uid, stub_text=URL,
                       main='<div class="lab" style="font-size:%.0fpx;color:#fff;letter-spacing:.06em">Get your ticket</div>'
                       '<div class="body" style="font-size:%.0fpx;color:#F2AE86;margin-top:%.0fpx">%s</div>'
                       % (h * 0.2, h * 0.15, h * 0.06, C.DATES))


def poster(C, key):
    """A2 at 150 dpi. Each concept gets its own layout: a photo wall under conversation bubbles, a giant
    microphone under the stage light, a rocket leaving an orange slab."""
    w, h = 2480, 3508
    P = PACKS[key]
    name = "climb27_poster-a2_%s_%dx%d" % (key, w, h)
    K = Kit(C, name)
    m = 180
    p = []
    if key == "find-your-people":
        p += [F.svg(w, h, M.contours(w, h, seed=53, rings=12, dark=True, marker=False, cx=1.05, cy=0.55)),
              glow(w, h, 0, h * 0.25, w * 0.8, 0.4),
              K.pic(P["photo"], 200, 760, 1500, 1000, pos="center 30%", rot=-4, radius=36, shadow=True),
              K.pic(P["photo2"], 1020, 1420, 1260, 840, pos="center", rot=5, radius=36, shadow=True),
              sticker(C.DATES, 240, 700, 70, rot=-6),
              hero(P["hero"], 1460, 300, 860, rot=-6, ghosts=[(-0.55, 0.05, 0.55, 16, 0.25), (-1.3, -0.12, 0.4, -12, 0.16)]),
              I.place("coffee", 120, 1820, 520, rotate=-10, seed=2)]
        ty = 2340
    elif key == "main-stage-moments":
        p += [F.svg(w, h, M.stage_light(w, h * 0.7, seed=5, uid="psl")),
              glow(w, h, w * 0.6, 0, w * 0.7, 0.45)]
        for k, (ph, x, y, r) in enumerate((("climb_band_stage", 120, 1540, -6), ("climb_awards_trophies", 880, 1640, 4),
                                           ("climb_crowd_wide", 1620, 1520, -3))):
            p.append(K.pic(ph, x, y, 760, 520, pos="center 35%", rot=r, radius=26, shadow=True))
        p.append(hero("microphone", 520, 200, 1350, rot=-4, ghosts=[(-0.32, 0.25, 0.5, 20, 0.2), (0.95, 0.35, 0.45, -20, 0.18)]))
        p.append(I.place("spotlight", 1800, 360, 560, rotate=-8, opacity=0.9, seed=4))
        p.append(sticker("Main stage moments", 160, 2120, 66, rot=-4))
        ty = 2340
    else:
        p += [slab_poly([(w * 0.7, h), (w, h * 0.76), (w, h)], OR),
              chevrons(w * 0.87, h * 0.975, w * 0.09, steps=3, colour=DB, w=w, h=h),
              F.svg(w, h, M.contours(w, h, seed=55, rings=10, dark=True, marker=False, cx=-0.05, cy=0.0)),
              glow(w, h, w, h * 0.45, w * 0.7, 0.35),
              K.pic(P["photo"], 180, 860, 1450, 966, pos="center 40%", rot=-5, radius=36, shadow=True),
              sticker(C.DATES, 220, 800, 70, rot=-6),
              hero("rocket", 1420, 420, 1000, rot=0, ghosts=[(-0.32, 0.55, 0.5, 8, 0.25), (-0.6, 0.98, 0.34, 14, 0.15)]),
              I.place("chart", 1820, 1700, 480, rotate=8, opacity=0.9, seed=3)]
        ty = 2160
    p.append(F.logo_img(C, "Climb27", "reversed-dark", m, 190, 760))
    p.append('<div class="abs lab" style="right:%dpx;top:240px;font-size:52px;color:#F2AE86">%s</div>' % (m, URL))
    p.append(head(P["lines"], m, ty, 300, w - 2 * m, rule_on=True, sub=C.TAGLINE + ".", sub_size=72))
    tw = w - 2 * m - (330 if key == "bigger-stage" else 0)
    p.append(foot_ticket(C, m, h - m - 300, tw, 300, "pf"))
    p.append(F.grain_layer(w, h, 53, 0.07))
    copy = [C.DATES, plain(" ".join(P["lines"])), C.TAGLINE, "Get your ticket", URL, "Main stage moments"]
    return asset(name, "Print and merch", "Climb27", w, h, p, copy)


def pullup(C):
    """850x2000mm at 100 dpi. Nothing in the bottom 300mm (the cassette)."""
    w, h = 3346, 7874
    name = "climb27_pullup-banner_bigger-stage_%dx%d" % (w, h)
    K = Kit(C, name)
    safe = h - int(300 * h / 2000)
    m = 260
    p = [F.svg(w, h, M.contours(w, h, seed=54, rings=16, dark=True, marker=True, cx=0.85, cy=0.95)),
         glow(w, h, w, 0, w * 0.9, 0.45), glow(w, h, 0, h * 0.55, w * 0.7, 0.25)]
    p.append(F.logo_img(C, "Climb27", "reversed-dark", m, 260, 1900))
    p.append('<div class="abs body" style="left:%dpx;top:760px;font-size:110px;color:#F2AE86">%s.</div>' % (m, C.TAGLINE))
    p.append(head(["Your *business*.", "Bigger [[stage]]."], m, 1080, 330, w - 2 * m, rule_on=True))
    p.append(K.pic("climb_crowd_wide", m - 40, 2250, 1560, 1100, pos="center 40%", rot=-4, radius=48, shadow=True))
    p.append(K.pic("climb_band_stage", 1500, 3650, 1560, 1040, pos="center", rot=4, radius=48, shadow=True))
    p.append(sticker(C.DATES, m, 2190, 96, rot=-6))
    p.append(hero("rocket", 1800, 2000, 1300, ghosts=[(-0.3, 0.55, 0.5, 8, 0.22), (-0.55, 0.95, 0.35, 14, 0.14)]))
    p.append(hero("microphone", 140, 3600, 1250, rot=-6, ghosts=[(0.62, 0.66, 0.42, 18, 0.2)]))
    ty, th = 5060, 1200
    main = ('<div class="lab" style="font-size:84px;color:#F2AE86">Get your ticket</div>'
            '<div class="disp" style="font-size:210px;margin:30px 0 34px;text-transform:none">%s</div>'
            '<div class="body" style="font-size:96px;color:#fff;line-height:1.3">%s</div>' % (URL, C.DATES))
    stub = ('<div style="display:flex;flex-direction:column;align-items:center">%s'
            '<div class="lab" style="font-size:66px;color:#1E0F05;margin-top:40px;letter-spacing:.08em">Scan for <em>tickets</em></div></div>'
            % F.qr(640))
    p.append(F.ticket(m, ty, w - 2 * m, th, (w - 2 * m) - 1000, main, stub, fill=CH, stroke="rgba(255,255,255,.16)",
                      stub_fill=OR, uid="pu1", pad=130, r=64, notch=72))
    p.append(sticker("Find your people", m + 60, ty - 70, 92, rot=-4, tone="white"))
    p.append(scatter(["tickets", "bubbles", "trophy", "glasses", "spotlight", "chart"], (120, ty + th + 120, w - 120, safe - 80),
                     4, (520, 640), seed=12, opacity=(0.35, 0.55)))
    p.append(F.grain_layer(w, h, 54, 0.07))
    assert ty + th <= safe - 300, "ticket runs into the bottom 300mm"
    copy = [C.TAGLINE, "Your business. Bigger stage.", C.DATES, "Get your ticket", URL, "Scan for tickets", "Find your people"]
    return asset(name, "Print and merch", "Climb27", w, h, p, copy)


def badge(C):
    """A6 at 300 dpi. Name well above 28pt (117px), drawings ghosted in the top band away from the name, an
    orange role band with a cut top edge."""
    w, h = 1240, 1748
    name = "climb27_badge-a6_delegate_%dx%d" % (w, h)
    band = h * 0.2
    p = [glow(w, h, w, 0, w * 0.9, 0.35),
         scatter(["bubbles", "tickets", "coffee", "microphone", "glasses", "people", "sparkles"], (20, 20, w - 20, h * 0.33),
                 6, (170, 220), seed=4, opacity=(0.12, 0.2), avoid=[(80, 80, 760, 300)]),
         F.logo_img(C, "Climb27", "reversed-dark", 100, 120, 640),
         hero("people", 870, 120, 290, rot=6),
         '<div class="abs" style="left:100px;top:%dpx;width:1040px"><div class="disp fit" style="font-size:176px;width:1040px">'
         'First Name</div><div class="body" style="font-size:84px;color:#F2AE86;margin-top:36px">Company</div></div>' % (h * 0.36),
         slab_poly([(0, h - band + 60), (w, h - band - 40), (w, h), (0, h)], OR),
         '<div class="abs disp" style="left:100px;bottom:%dpx;font-size:124px;color:#fff;letter-spacing:.02em">Delegate</div>' % (band * 0.26),
         chevrons(w * 0.76, h - band * 0.22, band * 0.62, steps=3, colour=DB, w=w, h=h),
         sticker("Find your people", 100, h * 0.66, 56, rot=-4, tone="white")]
    p.append(F.grain_layer(w, h, 55, 0.06))
    return asset(name, "Print and merch", "Climb27", w, h, p, ["First Name", "Company", "Delegate", "Find your people"])


def lanyard(C):
    """900x20mm at 300 dpi: the li monogram, the wordmark and the drawings repeating along the strap."""
    w, h = 10630, 236
    name = "climb27_lanyard-strap_repeat_%dx%d" % (w, h)
    word_h = 104
    word_w = word_h / C.logo_ratio("Climb27", "reversed-dark")
    doodles = ["microphone", "tickets", "bubbles", "rocket", "glasses", "trophy"]
    items = []
    k = 0
    x = 60
    while x < w - 600:
        items.append('<img src="%s" style="height:168px" alt="">' % C.logo("Climb27", "icon-monogram"))
        items.append('<img src="%s" style="height:%dpx" alt="">' % (C.logo("Climb27", "reversed-dark"), word_h))
        items.append(I.svg(doodles[k % len(doodles)], seed=k, style="width:200px;height:200px;flex:none;transform:rotate(%ddeg)"
                           % (-12 if k % 2 else 10)))
        x += 168 + word_w + 200 + 3 * 90
        k += 1
    html_ = '<div class="abs" style="inset:0;display:flex;align-items:center;justify-content:space-evenly">%s</div>' % "".join(items)
    return asset(name, "Print and merch", "Climb27", w, h, [html_], [])


def tote(C):
    """Tote print 380x420mm at 150 dpi on Dark Brown: the drawings as an all over pattern, the line on a ticket."""
    w, h = 2244, 2480
    name = "climb27_tote_find-your-people_%dx%d" % (w, h)
    names = ["bubbles", "coffee", "tickets", "microphone", "handshake", "glasses", "rocket", "people", "lightbulb",
             "badge", "trophy", "megaphone", "sneaker", "record"]
    p = [pattern(names, w, h, 420, seed=7, opacity=1.0, weight=1.15)]
    tw, th = 1640, 1000
    tx, ty = (w - tw) / 2, (h - th) / 2
    p.append('<div class="abs" style="left:%.0fpx;top:%.0fpx;width:%dpx;height:%dpx;background:%s;border-radius:60px;'
             'box-shadow:0 0 0 70px %s"></div>' % (tx, ty, tw, th, DB, DB))
    p.append(F.svg(w, h, '<g transform="translate(%.0f %.0f)">%s</g>'
                   % (tx, ty, F.ticket_shape(tw, th, th * 0.74, "h", r=60, notch=56, fill=DB, stroke=OR, uid="tt"))))
    p.append(head(["*Find* your", "[[people]]."], tx + 120, ty + 110, 230, tw - 240, rule_on=True))
    p.append(F.logo_img(C, "Climb27", "reversed-dark", tx + 120, ty + th * 0.74 + 70, 560))
    p.append('<div class="abs lab" style="left:%.0fpx;top:%.0fpx;font-size:54px;color:#F2AE86">%s</div>'
             % (tx + 760, ty + th * 0.74 + 92, URL))
    return asset(name, "Print and merch", "Climb27", w, h, p, ["Find your people.", URL])


def tshirt(C):
    """Back print 300x400mm at 150 dpi for dark garments, transparent: one big drawing, the line, the mark."""
    w, h = 1772, 2362
    name = "climb27_tshirt-print_logo_%dx%d" % (w, h)
    p = [hero("bubbles", 130, 40, 1500, rot=-4, weight=0.9),
         I.place("sparkles", 40, 1180, 300, rotate=10, seed=3),
         I.place("sparkles", 1430, 60, 300, rotate=-10, seed=5),
         head(["*Find* your", "[[people]]."], 130, 1450, 270, 1510, rule_on=True),
         F.logo_img(C, "Climb27", "reversed-dark", 130, 2100, 700),
         '<div class="abs lab" style="left:900px;top:2140px;font-size:50px;color:#F2AE86;white-space:nowrap">%s</div>' % C.DATES]
    return asset(name, "Print and merch", "Climb27", w, h, p, ["Find your people.", C.DATES], transparent=True)


def sticker_sheet(C):
    """A4 at 300 dpi: a die cut sticker sheet of the drawings and lines, each on a Dark Brown blob with a white cut
    line. A preview; the printer gets the cut path as a separate layer."""
    w, h = 2480, 3508
    name = "climb27_sticker-sheet_doodles_%dx%d" % (w, h)
    p = []
    stickers = []
    rows = [(140, ["microphone", "tickets", "rocket"]), (1150, ["trophy", "glasses", "bubbles"]),
            (2160, [("badge", "SPEAKER"), "sneaker", ("badge", "PARTNER")]), (3020, ["coffee", "record", "lightbulb"])]
    for r, (y, items) in enumerate(rows):
        size = 560 if r < 3 else 380
        for c, it in enumerate(items):
            kind, content = it if isinstance(it, tuple) else ("doodle", it)
            x = [160, 960, 1760][c] + (90 if r == 3 else 0) + (40 if r % 2 else 0)
            stickers.append((kind, content, x, y + (c % 2) * 40, size, [-8, 5, -4, 7][(r + c) % 4]))
    stickers += [("text", "Find your [[people]]", 180, 820, 0, -4), ("text", "I'm going", 1700, 860, 0, 5),
                 ("text", "Bigger [[stage]]", 260, 1830, 0, 3), ("logo", "Climb27", 1380, 1800, 0, -5),
                 ("text", "Main stage [[moments]]", 420, 2830, 0, -3)]
    for kind, content, x, y, size, rot in stickers:
        if kind in ("doodle", "badge"):
            pad = size * 0.06
            p.append('<div class="abs" style="left:%.0fpx;top:%.0fpx;width:%.0fpx;height:%.0fpx;border-radius:50%%;background:%s;'
                     'box-shadow:0 0 0 14px #fff,0 18px 40px rgba(0,0,0,.35);transform:rotate(%ddeg)"></div>'
                     % (x - pad, y - pad, size + 2 * pad, size + 2 * pad, DB, rot))
            p.append(I.place("badge" if kind == "badge" else content, x + size * 0.05, y + size * 0.05, size * 0.9,
                             rotate=rot, seed=3, label=content if kind == "badge" else None))
        elif kind == "text":
            p.append('<div class="abs disp" style="left:%dpx;top:%dpx;font-size:96px;padding:34px 48px;background:%s;'
                     'border-radius:30px;box-shadow:0 0 0 14px #fff,0 18px 40px rgba(0,0,0,.35);transform:rotate(%ddeg);'
                     'white-space:nowrap">%s</div>' % (x, y, DB if "[[" in content else OR, rot,
                                                       rich(content) if "[[" in content else
                                                       '<span style="color:%s">%s</span>' % (DB, html.escape(content))))
        else:
            p.append('<div class="abs" style="left:%dpx;top:%dpx;padding:44px 64px;background:%s;border-radius:34px;'
                     'box-shadow:0 0 0 14px #fff,0 18px 40px rgba(0,0,0,.35);transform:rotate(%ddeg)">'
                     '<img src="%s" style="width:420px;display:block" alt=""></div>' % (x, y, DB, rot, C.logo(content, "reversed-dark")))
    copy = ["Find your people", "Bigger stage", "Main stage moments", "I'm going", "SPEAKER", "PARTNER"]
    return asset(name, "Print and merch", "Climb27", w, h, p, copy, ground="charcoal")


# ---------------------------------------------------------------- assembly

def assets(C):
    CSS_C[0] = F.css(C, """
.doodle{pointer-events:none}
""")
    out = []
    motifs4 = ["stage-light", "contours", "connections", "ascent"]
    for brand in ("Climb27", "ClimbUK", "ClimbGroup"):
        for i, motif in enumerate(motifs4):
            out.append(call_bg(C, brand, i, motif))
    for brand in ("Climb27", "ClimbUK", "ClimbGroup"):
        for i, motif in enumerate(motifs4):
            for (w, h) in [(2560, 1440), (3840, 2160), (5120, 2880)]:
                out.append(desktop(C, brand, i, motif, w, h))
    for brand in ("Climb27", "ClimbUK"):
        for i, motif in enumerate(motifs4):
            for (w, h) in [(1179, 2556), (1440, 3120)]:
                out.append(phone(C, brand, i, motif, w, h))
    for brand in ("Climb27", "ClimbUK", "ClimbGroup"):
        out += [linkedin_company(C, brand), x_header(C, brand), facebook_cover(C, brand),
                youtube_banner(C, brand, "dark"), youtube_banner(C, brand, "orange")]
    out.append(see_you(C))
    out.append(footer_strip(C))
    for key in PACKS:
        out += [pack_post(C, key), pack_story(C, key), pack_square(C, key)]
    for key in PACKS:
        out.append(poster(C, key))
    out += [pullup(C), badge(C), lanyard(C), tote(C), tshirt(C), sticker_sheet(C)]
    return out
