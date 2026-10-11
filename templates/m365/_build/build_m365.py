"""Build the Microsoft 365 and Teams Premium branding kit for ClimbUK, ClimbGroup and Climb27.

    python3 templates/m365/_build/build_m365.py [BUILD_DIR]

Writes HTML pages and a manifest to BUILD_DIR (default build/m365), renders them with generators/render.mjs, then
saves the finished files into templates/m365/ in the size, format and file-size limit each Microsoft upload slot
asks for. The video call backgrounds already in the asset catalogue are rendered from generators/catalogue.py and
copied in beside the new ones, so the organisation backgrounds list holds the whole set.

Every colour comes from tokens/brand.tokens.json (through the generator modules), every logo from logos/, every
photo from photos/. All copy goes through the climb-voice checker.
"""
import io
import json
import math
import pathlib
import re
import shutil
import subprocess
import sys
import zipfile

from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
KIT = HERE.parent
ROOT = KIT.parents[1]
GEN = ROOT / "generators"
sys.path.insert(0, str(GEN))

import catalogue as C  # noqa: E402
import festival_kit as F  # noqa: E402
import illustrations as I  # noqa: E402
import motifs as M  # noqa: E402
import poster_kit as P  # noqa: E402

sys.path.insert(0, str(HERE))
import reactions as R  # noqa: E402

DB, CH, OR, TI, LG, WH = F.DB, F.CH, F.OR, F.TI, F.LG, F.WH
OR_TEXT = "#C55308"      # color.orange.text: small orange text and accents on white (4.6:1)
OR_DEEP = "#8D4419"      # color.orange.deep: AAA orange on white (7.06:1)
OR_GREY = "#D5641E"      # color.orange.large-on-grey
DB_RGB = F.DB_RGB
BRANDS = ("ClimbUK", "ClimbGroup", "Climb27")
SITE = "https://www.climb-uk.com"

# Lines and photos per brand. Lines are the brand lines already used across the kit.
B = {
    "ClimbUK": dict(line=["*Find* your", "[[people]]."], sticker="Find your people",
                    dark_photo="candid/climbteam_01", dark_pos="50% 40%",
                    cards=["candid/joy_02", "candid/crowds_04", "candid/meetings_02"],
                    photos=["candid/joy_02", "candid/crowds_04", "candid/exhibitor_01", "candid/audience_at_stage_02"],
                    hero="bubbles"),
    "ClimbGroup": dict(line=["*Business* with", "a [[party]]."], sticker="Business with a party",
                       dark_photo="candid/vip_and_awards_03", dark_pos="55% 40%",
                       cards=["candid/roundtable_and_workshops_01", "candid/meetings_01", "candid/vip_and_awards_01"],
                       photos=["candid/vip_and_awards_03", "candid/roundtable_and_workshops_01", "candid/meetings_01",
                               "candid/food_and_vendors_01"],
                       hero="lightbulb"),
    "Climb27": dict(line=["Your *business*.", "Bigger [[stage]]."], sticker="30 June and 1 July 2027",
                    dark_photo="candid/stage_speakers_04", dark_pos="55% 45%",
                    cards=["candid/audience_at_stage_02", "candid/stage_speakers_02", "candid/joy_03"],
                    photos=["candid/stage_speakers_04", "candid/audience_at_stage_01", "candid/stage_speakers_02",
                            "candid/crowds_03"],
                    hero="microphone"),
}

# Microsoft 365 app launcher tiles (custom tiles for apps): name, drawing, where it goes.
TILES = [
    ("odoo", "gears", "Odoo", "Our business system: contacts, events, tickets, website and accounts."),
    ("website", "globe", "climb-uk.com", "The public website."),
    ("brand-centre", "book-open", "Brand centre", "Logos, colours, fonts, templates and the brand guidelines."),
    ("tickets", "tickets", "Tickets", "Event tickets and the box office."),
    ("media-kit", "clapperboard", "Media kit", "Photos, video, press and partner downloads."),
]

ASSETS = []


def add(name, w, h, parts, copy=(), scale=1, transparent=False, ground="dark-brown", css="", group="M365"):
    a = P.asset(name, group, "ClimbUK", w, h, parts, list(copy), scale=scale, transparent=transparent,
                ground=ground, css=css)
    ASSETS.append(a)
    return a


def light_tile_svg(brand):
    """The stacked square tile for light grounds: White tile, Climb Orange "Climb", Charcoal second word. Same
    paths as the master tile; only the ground and the second colour change, as the logo rules allow."""
    svg = (C.LOGOS / brand / ("%s_icon.svg" % brand)).read_text(encoding="utf-8")
    # Master order: Dark Brown tile, Climb Orange "Climb", White second word.
    svg = svg.replace('fill="#FFFFFF"', 'fill="#242322"').replace('fill="#1E0F05"', 'fill="#FFFFFF"')
    return svg


def img(src, x, y, w, h=None, extra=""):
    return ('<img class="abs" src="%s" style="left:%.0fpx;top:%.0fpx;width:%.0fpx;%s%s" alt="">'
            % (src, x, y, w, ("height:%.0fpx;" % h) if h else "height:auto;", extra))


# ---------------------------------------------------------------- Teams Premium meeting themes

def theme_logo(brand, mode, build):
    """800x800 square logo (minimum 576x576). Dark theme: the Dark Brown tile. Light theme: the White tile."""
    w = h = 800
    if mode == "dark":
        src = C.logo(brand, "icon")
    else:
        path = build / "src" / ("%s_icon-light.svg" % brand)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(light_tile_svg(brand), encoding="utf-8")
        src = path.as_uri()
    add("%s_teams-theme_logo-%s_800x800" % (brand.lower(), mode), w, h, [img(src, 0, 0, w, h)],
        ground="dark-brown" if mode == "dark" else "white")


def theme_sticker(brand):
    """The headline already carries the brand line, so the sticker carries the dates (Climb27) or the tagline."""
    return B[brand]["sticker"] if brand == "Climb27" else C.TAGLINE


def theme_image(brand, mode, scale, label):
    """Meeting theme image, laid out at the recommended 1440x810. Teams shows it behind the join screen, with the
    theme logo and meeting title at the top centre and the camera and audio panels over the middle (about 22 to 78
    percent across and down), and crops the top and bottom on wide windows. So the middle stays photo and glow only:
    the brand line runs in one line along the bottom band on the solid left half, the sticker sits top left, and the
    photo fills the right half under a fade, where it shows beside the panels. Dark: Dark Brown fade and the orange glow. Light: White fade, Charcoal line with the orange word in
    Orange Text (4.6:1)."""
    w, h = 1440, 810
    b = B[brand]
    K = P.Kit(C, brand, scale)
    dark = mode == "dark"
    rgb = DB_RGB if dark else "255,255,255"
    p = [K.pic(b["dark_photo"], int(w * 0.5), 0, w - int(w * 0.5), h, pos=b["dark_pos"],
               fade=P.fade("to right", 0, 45, 1.0, 0.0, rgb=rgb))]
    if dark:
        p.append(P.glow(w, h, w, 0, w * 0.5, 0.42))
    p.append(F.svg(w, h, M.contours(w, h, seed=21, rings=8, dark=dark, marker=False, cx=-0.05, cy=1.08)))
    line = " ".join(b["line"])
    if dark:
        hd = P.head([line], 96, 632, 52, 620, anchor="top", lh=1.0)
    else:
        hd = P.head([line.replace("[[", "{{").replace("]]", "}}")], 96, 632, 52, 620, anchor="top", colour=CH, lh=1.0)
        hd = hd.replace("{{", '<span style="color:%s">' % OR_TEXT).replace("}}", "</span>")
    p.append(hd)
    p.append(P.sticker(theme_sticker(brand), 96, 110, 24, rot=-3, tone="orange" if dark else "brown"))
    if dark:
        p.append(F.grain_layer(w, h, 31, 0.06))
    copy = [F.plain(l) for l in b["line"]] + [theme_sticker(brand)]
    add("%s_teams-theme_image-%s_%s" % (brand.lower(), mode, label), w, h, p, copy, scale=scale,
        ground="dark-brown" if dark else "white")


# ---------------------------------------------------------------- Organisation backgrounds

FESTIVAL = ["spotlight", "summit", "orbit", "network", "ascent-light", "contours-light"]
CALM = ["calm-dark", "calm-light", "calm-glow", "calm-white"]


def bg_festival(brand, motif):
    """More backgrounds in the catalogue festival style: glow, contours, chevrons, slabs and house drawings at the
    edges, the centre calm for the person, the logo top left. The -light pair sits on Light Grey with the drawings in
    Orange Text."""
    w, h = 3840, 2160
    name = "%s_teams-bg_%s_%dx%d" % (brand.lower(), motif, w, h)
    Bd = P.BRANDS[brand]
    heroes, extras = Bd["heroes"], Bd["extras"]
    seed = {"ClimbUK": 1, "ClimbGroup": 2, "Climb27": 3}[brand]
    centre = (w / 2 - 980, h / 2 - 760, w / 2 + 980, h / 2 + 760)
    logo_zone = (0, 0, w * 0.26, h * 0.22)
    sticker_text = Bd["sticker"]
    p, ground, logo = [], "dark-brown", "reversed-dark"
    if motif == "spotlight":
        # A beam of stage light from the top edge, the hero lit at the bottom right.
        p.append(P.glow(w, h, w * 0.78, -h * 0.1, w * 0.55, 0.48))
        p.append(P.glow(w, h, w * 0.85, h, w * 0.3, 0.22))
        p.append(F.svg(w, h, M.contours(w, h, seed=40 + seed, rings=8, dark=True, marker=False, cx=0.8, cy=-0.12)))
        p.append(P.hero(heroes[2], w - 900, h - 920, 720, rot=7,
                        ghosts=[(-0.55, -0.6, 0.55, -16, 0.18), (0.2, -1.1, 0.45, 14, 0.12)]))
        p.append(P.scatter(extras, (60, h * 0.45, w * 0.24, h - 260), 3, (240, 320), seed=40 + seed, avoid=[centre]))
        p.append(P.sticker(sticker_text, 150, h - 280, 66, rot=-4))
    elif motif == "summit":
        # The ascent turned round: the slab and chevrons climb from the bottom left, the hero top right.
        p.append(P.slab_poly([(0, h - 1050), (1150, h), (0, h)], OR))
        p.append(P.chevrons(80, h - 120, 480, steps=3, colour=DB, w=w, h=h))
        p.append(P.glow(w, h, w * 0.08, h * 0.88, w * 0.42, 0.38))
        p.append(F.svg(w, h, M.contours(w, h, seed=44 + seed, rings=9, dark=True, marker=False, cx=1.0, cy=0.05)))
        p.append(P.hero(heroes[0], w - 920, 200, 700, rot=-5,
                        ghosts=[(-0.4, 0.6, 0.5, 12, 0.18), (-0.1, 1.05, 0.38, -18, 0.12)]))
        p.append(P.scatter(extras, (w * 0.78, h * 0.5, w - 60, h - 60), 3, (230, 300), seed=44 + seed, avoid=[centre]))
        p.append(P.sticker(sticker_text, 150, h - 300, 66, rot=4, side="right"))
    elif motif == "orbit":
        # Contour rings from the top right corner, drawings along the bottom edge like a festival line-up.
        p.append(F.svg(w, h, M.contours(w, h, seed=48 + seed, rings=15, dark=True, marker=True, cx=1.04, cy=-0.04)))
        p.append(P.glow(w, h, w, 0, w * 0.4, 0.34))
        p.append(F.svg(w, h, M.slabs(w, h, corners=("bl",), length=w * 0.2, thick=h * 0.05)))
        for k, (x, sz, r) in enumerate([(w * 0.05, 360, -8), (w * 0.72, 420, 6), (w * 0.86, 360, -10)]):
            p.append(I.place(extras[(k + seed) % len(extras)], x, h - sz - 150, sz, rotate=r, opacity=0.3, seed=k))
        p.append(P.hero(heroes[1], w - 860, 180, 620, rot=-8, ghosts=[(-0.5, 0.7, 0.5, 14, 0.16)]))
        p.append(P.sticker(sticker_text, 150, 150, 62, rot=3, side="right"))
    elif motif == "network":
        # Joined dots along the top and bottom edges, a glow in two corners, two drawings, no photos.
        p.append(F.svg(w, h, M.connections(w, h, seed=52 + seed, dots=24, dark=True, region=(0.28, 0.0, 0.98, 0.15)), "opacity:.6"))
        p.append(F.svg(w, h, M.connections(w, h, seed=53 + seed, dots=22, dark=True, region=(0.02, 0.86, 0.72, 1.0)), "opacity:.6"))
        p.append(P.glow(w, h, 0, h, w * 0.38, 0.3))
        p.append(P.glow(w, h, w, 0, w * 0.38, 0.3))
        p.append(P.hero(heroes[3], w - 880, h - 960, 700, rot=6,
                        ghosts=[(-0.3, -0.7, 0.55, -14, 0.2), (0.35, -1.1, 0.42, 12, 0.14)]))
        p.append(P.hero(extras[1], 130, h - 820, 520, rot=-9, ghosts=[(0.5, -0.6, 0.55, 16, 0.18)]))
        p.append(P.sticker(sticker_text, 150, h - 290, 64, rot=-5))
    elif motif == "ascent-light":
        p.append(F.svg(w, h, M.contours(w, h, seed=56 + seed, rings=9, dark=False, marker=False, cx=0.0, cy=0.1)))
        p.append(P.slab_poly([(w - 1250, h), (w, h - 1120), (w, h)], OR))
        p.append(P.chevrons(w - 520, h - 120, 520, steps=3, colour=DB, w=w, h=h))
        p.append(P.hero(heroes[3], w - 900, 180, 700, rot=0, ghost_ink=OR_TEXT,
                        ghosts=[(-0.35, 0.55, 0.5, 10, 0.22), (-0.62, 0.95, 0.36, 18, 0.15)]))
        p.append(P.scatter(extras, (60, h * 0.3, w * 0.24, h - 400), 3, (240, 320), seed=56 + seed, ink=OR_TEXT,
                           opacity=(0.3, 0.45), avoid=[centre, logo_zone]))
        p.append(P.sticker(sticker_text, 150, h - 300, 66, rot=-4, tone="brown"))
        ground, logo = "light-grey", "full-colour-grey"
    else:  # contours-light
        p.append(F.svg(w, h, M.contours(w, h, seed=60 + seed, rings=14, dark=False, marker=True, cx=-0.02, cy=1.04)))
        p.append(F.svg(w, h, M.slabs(w, h, corners=("br",), length=w * 0.22, thick=h * 0.06)))
        p.append(P.scatter(extras, (w * 0.76, 120, w - 60, h * 0.78), 4, (230, 320), seed=60 + seed, ink=OR_TEXT,
                           opacity=(0.3, 0.45), avoid=[centre]))
        p.append(I.place(heroes[1], 140, h - 880, 700, rotate=8, ink=OR_TEXT, ground=LG))
        p.append(P.sticker(sticker_text, 150, 150, 66, rot=3, side="right"))
        ground, logo = "light-grey", "full-colour-grey"
    p.append(F.grain_layer(w, h, 90 + seed, 0.06 if ground == "dark-brown" else 0.03))
    p.append(F.logo_img(C, brand, logo, w * 0.04, h * 0.06, w * 0.15))
    a = add(name, w, h, p, [sticker_text], group="Backgrounds", ground="dark-brown")
    if ground == "light-grey":
        a["extra_css"] += ".canvas{background:%s !important}" % LG


POSTER_PHOTOS = {
    "ClimbUK": ["joy_01", "crowds_01", "exhibitor_02", "meetings_03", "audience_at_stage_01", "climbteam_02"],
    "ClimbGroup": ["vip_and_awards_02", "roundtable_and_workshops_02", "meetings_02", "food_and_vendors_01",
                   "stage_speakers_02", "vip_and_awards_04"],
    "Climb27": ["stage_speakers_01", "audience_at_stage_02", "crowds_02", "joy_03", "stage_speakers_03", "joy_04"],
}
POSTER_COUNT = 6


def bg_poster(brand, kind, i):
    """Backgrounds in the meeting theme style. The left side is solid ground with the logo, the brand line and the
    sticker, all inside the 4:3 centre crop Teams uses for gallery tiles (12.5 to 87.5 percent across) and above the
    name label; the right side carries a Climb26 photo under a fade (kind "photo") or a house drawing in the glow
    (kind "drawing"). The middle stays quiet for the person. The last two of each kind are light."""
    w, h = 3840, 2160
    dark = i < POSTER_COUNT - 2
    name = "%s_teams-bg_%s-%d_%dx%d" % (brand.lower(), kind, i + 1, w, h)
    b = B[brand]
    Bd = P.BRANDS[brand]
    K = P.Kit(C, name)
    rgb = DB_RGB if dark else "255,255,255"
    x0 = w * 0.135
    p = []
    if kind == "photo":
        p.append(K.pic("candid/" + POSTER_PHOTOS[brand][i], int(w * 0.5), 0, w - int(w * 0.5), h, pos="50% 40%",
                       fade=P.fade("to right", 0, 45, 1.0, 0.0, rgb=rgb)))
        if dark:
            p.append(P.glow(w, h, w, 0, w * 0.45, 0.3))
    else:
        drawings = Bd["heroes"] + Bd["extras"][:2]
        if dark:
            p.append(P.glow(w, h, w * 0.82, h * 0.35, w * 0.4, 0.42))
        p.append(F.svg(w, h, M.contours(w, h, seed=70 + i, rings=10, dark=dark, marker=False, cx=1.02, cy=0.4 + 0.1 * (i % 3))))
        ink = None if dark else OR_TEXT
        p.append(P.hero(drawings[i], w * 0.66, h * 0.24, 820, rot=(-6, 5, -3, 7, -5, 4)[i], ghost_ink=ink,
                        ghosts=[(-0.35, 0.8, 0.5, 14, 0.18), (0.55, 0.95, 0.4, -16, 0.13), (0.15, -0.3, 0.35, 10, 0.12)])
                 if dark else I.place(drawings[i], w * 0.66, h * 0.24, 820, rotate=(-6, 5, -3, 7, -5, 4)[i], ink=OR_TEXT, ground=WH))
    p.append(F.svg(w, h, M.contours(w, h, seed=80 + i, rings=7, dark=dark, marker=False, cx=-0.08, cy=1.1)))
    line = b["line"]
    words, rows = " ".join(line).split(), [""]
    for wd in words:  # stack short rows so the line stays big inside the narrow band beside the person
        plain = re.sub(r"[*\[\]]", "", rows[-1] + " " + wd).strip()
        rows[-1:] = [(rows[-1] + " " + wd).strip()] if len(plain) <= 10 or not rows[-1] else [rows[-1], wd]
    stack = rows
    if dark:
        hd = P.head(stack, x0, h * 0.2, 220, 1000, anchor="top", lh=0.98)
    else:
        hd = P.head([l.replace("[[", "{{").replace("]]", "}}") for l in stack], x0, h * 0.2, 220, 1000, anchor="top",
                    colour=CH, lh=0.98)
        hd = hd.replace("{{", '<span style="color:%s">' % OR_TEXT).replace("}}", "</span>")
    p.append(hd)
    p.append(P.sticker(theme_sticker(brand), x0, h * 0.66, 60, rot=-3, tone="orange" if dark else "brown"))
    if dark:
        p.append(F.grain_layer(w, h, 100 + i, 0.05))
    p.append(F.logo_img(C, brand, "reversed-dark" if dark else "full-colour-light", x0, h * 0.08, w * 0.13))
    copy = [F.plain(l) for l in line] + [theme_sticker(brand)]
    a = add(name, w, h, p, copy, group="Backgrounds", ground="dark-brown")
    if not dark:
        a["extra_css"] += ".canvas{background:%s !important}" % WH


def bg_calm(brand, mode):
    """Calm background for everyday calls: one motif and the logo, nothing else. Dark: Dark Brown with contours and
    a corner glow. Light: Light Grey with grey-tone contours, an orange slab and the grey-ground logo."""
    w, h = 3840, 2160
    name = "%s_teams-bg_calm-%s_%dx%d" % (brand.lower(), mode, w, h)
    if mode == "dark":
        p = [F.svg(w, h, M.contours(w, h, seed=31, rings=13, dark=True, marker=False, cx=1.04, cy=1.06)),
             P.glow(w, h, w, 0, w * 0.5, 0.4),
             P.hero(B[brand]["hero"], w - 860, h - 900, 640, rot=-6, ghosts=[(-0.45, -0.55, 0.6, 14, 0.16)]),
             F.grain_layer(w, h, 51, 0.05),
             F.logo_img(C, brand, "reversed-dark", w * 0.04, h * 0.06, w * 0.15)]
        ground = "dark-brown"
    elif mode == "glow":
        p = [P.glow(w, h, w, h, w * 0.55, 0.42),
             F.svg(w, h, M.connections(w, h, seed=34, dots=18, dark=True, region=(0.7, 0.55, 0.99, 0.97)), "opacity:.5"),
             P.chevrons(w - 420, h - 110, 300, steps=3, colour=OR, w=w, h=h),
             F.grain_layer(w, h, 53, 0.05),
             F.logo_img(C, brand, "reversed-dark", w * 0.04, h * 0.06, w * 0.15)]
        ground = "dark-brown"
    elif mode == "white":
        p = [F.svg(w, h, M.slabs(w, h, corners=("bl", "tr"), length=w * 0.18, thick=h * 0.045)),
             I.place(B[brand]["hero"], w - 760, h - 780, 560, rotate=-6, ink=OR_TEXT, ground=WH, opacity=0.5),
             F.logo_img(C, brand, "full-colour-light", w * 0.04, h * 0.06, w * 0.15)]
        ground = "white"
    else:
        p = [F.svg(w, h, M.contours(w, h, seed=32, rings=13, dark=False, marker=False, cx=1.04, cy=1.06)),
             F.svg(w, h, M.slabs(w, h, corners=("br",), length=w * 0.22, thick=h * 0.05)),
             F.logo_img(C, brand, "full-colour-grey", w * 0.04, h * 0.06, w * 0.15)]
        ground = "light-grey"
    a = add(name, w, h, p, group="Backgrounds", ground="dark-brown")
    if ground in ("light-grey", "white"):
        a["extra_css"] += ".canvas{background:%s !important}" % (LG if ground == "light-grey" else WH)


# ---------------------------------------------------------------- Organisation theme, sign-in page, app tiles

def wordmark(brand, variant, w, h, name, ground="transparent"):
    """A logo fitted inside w x h, centred, on a transparent ground."""
    r = C.logo_ratio(brand, variant)
    lw = min(w, h / r)
    lh = lw * r
    add(name, w, h, [F.logo_img(C, brand, variant, (w - lw) / 2, (h - lh) / 2, lw)], transparent=True)


def tile(key, drawing, size, name, outline=False, safe=1.0):
    """App tile: a full-bleed Dark Brown square with the drawing in Climb Orange, centred inside the safe area.
    outline: the white drawing alone on a transparent ground (Teams app bar icon)."""
    d = size * 0.78 * safe
    weight = 2.4 if size <= 64 else (1.6 if size <= 200 else 1.2)
    if outline:
        p = [I.place(drawing, (size - d) / 2, (size - d) / 2, d, weight=weight, ink=WH, ground="rgba(0,0,0,0)")]
        add(name, size, size, p, transparent=True)
    else:
        p = [I.place(drawing, (size - d) / 2, (size - d) / 2, d, weight=weight)]
        add(name, size, size, p, ground="dark-brown")


def monogram_tile(size, name, safe=1.0):
    inner = size * safe
    off = (size - inner) / 2
    add(name, size, size, ['<div class="abs" style="inset:0;background:%s"></div>' % DB,
                           img(C.logo("ClimbUK", "icon-monogram"), off, off, inner, inner)])


def signin_background():
    """Sign-in page background, 1920x1080 under 300 KB: Climb26 crowd photo under a Dark Brown fade, orange glow
    corners. The sign-in box sits in the middle, so the photo shows at the sides."""
    w, h = 1920, 1080
    K = P.Kit(C, "signin")
    shade = ("radial-gradient(ellipse 34%% 60%% at 50%% 50%%, rgba(%s,.92) 0%%, rgba(%s,.75) 60%%, rgba(%s,.45) 100%%)"
             % ((DB_RGB,) * 3))
    p = [K.pic("candid/audience_at_stage_03", 0, 0, w, h, pos="50% 45%", fade=shade),
         P.glow(w, h, w, 0, w * 0.45, 0.4), P.glow(w, h, 0, h, w * 0.3, 0.25),
         F.grain_layer(w, h, 61, 0.05)]
    add("entra_signin-background_1920x1080", w, h, p)


def build_pages(build):
    P.CSS_C[0] = F.css(C, ".doodle{pointer-events:none}")
    for brand in BRANDS:
        for mode in ("dark", "light"):
            theme_logo(brand, mode, build)
            theme_image(brand, mode, 1, "1440x810")
            theme_image(brand, mode, 3840 / 1440, "3840x2160")
        for motif in FESTIVAL:
            bg_festival(brand, motif)
        for mode in CALM:
            bg_calm(brand, mode.split("-")[1])
        for kind in ("photo", "drawing"):
            for i in range(POSTER_COUNT):
                bg_poster(brand, kind, i)
        # Organisation theme logos: shown in the navigation bar, scaled to fit 200x48.
        wordmark(brand, "reversed-dark", 200, 48, "%s_m365-logo-default_200x48" % brand.lower())
        wordmark(brand, "mono-white", 200, 48, "%s_m365-logo-alternative_200x48" % brand.lower())
    R.pages(lambda name, w, h, parts, transparent=False: add(name, w, h, parts, transparent=transparent), I)
    for key, drawing, _, _ in TILES:
        for s in (60, 120, 240):
            tile(key, drawing, s, "m365-tile_%s_%dx%d" % (key, s, s))
    for s in (60, 120, 240):
        monogram_tile(s, "m365-tile_climb_%dx%d" % (s, s), safe=0.9)
    # Teams app (Odoo): colour icon 192 with the drawing inside the 120x120 safe area, outline icon 32.
    tile("odoo", "gears", 192, "teams-app_odoo_color_192x192", safe=120 / (192 * 0.78))
    tile("odoo", "gears", 32, "teams-app_odoo_outline_32x32", outline=True, safe=1.1)
    # Sign-in page (Microsoft Entra company branding).
    signin_background()
    wordmark("ClimbUK", "full-colour-light", 245, 36, "entra_banner-logo_245x36")
    wordmark("ClimbUK", "full-colour-light", 245, 36, "entra_header-logo_245x36")
    add("entra_square-logo-dark_240x240", 240, 240, [img(C.logo("ClimbUK", "icon"), 0, 0, 240, 240)])
    path = build / "src" / "ClimbUK_icon-light.svg"
    add("entra_square-logo-light_240x240", 240, 240, [img(path.as_uri(), 0, 0, 240, 240)], ground="white")
    monogram_tile(32, "entra_favicon_32x32")


# ---------------------------------------------------------------- write, render, save

def write(build):
    (build / "html").mkdir(parents=True, exist_ok=True)
    problems, manifest = [], []
    for a in ASSETS:
        text = " ".join(a.get("copy", []))
        problems += ["%s: %s" % (a["name"], p[2]) for p in C.check_copy.check(text)]
        path = build / "html" / (a["name"] + ".html")
        path.write_text(C.page(a), encoding="utf-8")
        manifest.append({"name": a["name"], "w": a["w"], "h": a["h"], "scale": a.get("scale", 1),
                         "transparent": a.get("transparent", False), "group": a["group"], "html": str(path)})
    (build / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    return problems


def save_jpeg(src, dst, limit=None, quality=90):
    im = Image.open(src).convert("RGB")
    dst.parent.mkdir(parents=True, exist_ok=True)
    q = quality
    while True:
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=q, optimize=True, progressive=True)
        if not limit or buf.tell() <= limit or q <= 40:
            break
        q -= 4
    dst.write_bytes(buf.getvalue())
    return q


def save_png(src, dst, limit=None, colours=None):
    im = Image.open(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if colours:
        im = im.convert("RGBA").quantize(colours, method=Image.Quantize.FASTOCTREE)
    im.save(dst, "PNG", optimize=True)
    if limit and dst.stat().st_size > limit and not colours:
        for c in (256, 128, 64, 32):
            Image.open(src).convert("RGBA").quantize(c, method=Image.Quantize.FASTOCTREE).save(dst, "PNG", optimize=True)
            if dst.stat().st_size <= limit:
                break
    return dst.stat().st_size


def min_svg(src, dst):
    """Copy a logo master with coordinates rounded to one decimal place, so it fits the 10 KB logo limit."""
    svg = src.read_text(encoding="utf-8")
    svg = re.sub(r"(\d+\.\d)\d+", r"\1", svg)
    svg = re.sub(r"\s+", " ", svg)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(svg, encoding="utf-8")


def teams_app(out, png):
    """Teams app package for Odoo: a personal tab that opens the Odoo web client, zipped with its two icons."""
    d = out / "teams-app-odoo"
    d.mkdir(parents=True, exist_ok=True)
    shutil.copy(png / "teams-app_odoo_color_192x192.png", d / "color.png")
    shutil.copy(png / "teams-app_odoo_outline_32x32.png", d / "outline.png")
    manifest = {
        "$schema": "https://developer.microsoft.com/en-us/json-schemas/teams/v1.19/MicrosoftTeams.schema.json",
        "manifestVersion": "1.19",
        "version": "1.0.0",
        "id": "5f0b6f2e-6a1d-4c27-9b0e-27c1a1b2c327",
        "developer": {"name": "ClimbGroup", "websiteUrl": SITE, "privacyUrl": SITE + "/privacy",
                      "termsOfUseUrl": SITE + "/terms"},
        "name": {"short": "Odoo", "full": "Odoo for ClimbUK"},
        "description": {"short": "Contacts, events, tickets and the website in one place.",
                        "full": "Opens our Odoo business system in Teams: contacts, events, tickets, website and accounts."},
        "icons": {"color": "color.png", "outline": "outline.png"},
        "accentColor": DB,
        "staticTabs": [{"entityId": "odoo", "name": "Odoo", "contentUrl": SITE + "/odoo",
                        "websiteUrl": SITE + "/odoo", "scopes": ["personal"]}],
        "permissions": ["identity"],
        "validDomains": ["www.climb-uk.com", "climb-uk.com"],
    }
    (d / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    with zipfile.ZipFile(out / "teams-app-odoo.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for n in ("manifest.json", "color.png", "outline.png"):
            z.write(d / n, n)


def render(build, filt=None):
    cmd = ["node", str(GEN / "render.mjs"), str(build)] + ([filt] if filt else [])
    subprocess.run(cmd, check=True)


def catalogue_backgrounds(build):
    """Render the twelve video call backgrounds from the asset catalogue (four layouts per brand)."""
    cat = build / "catalogue"
    subprocess.run([sys.executable, str(GEN / "catalogue.py"), str(cat)], check=False, stdout=subprocess.DEVNULL)
    render(cat, "call-bg")
    return cat / "png"


def save(build):
    png = build / "png"
    out = KIT
    report = []
    for brand in BRANDS:
        low = brand.lower()
        t = out / "teams-themes" / brand
        for mode in ("dark", "light"):
            n = save_png(png / ("%s_teams-theme_logo-%s_800x800.png" % (low, mode)), t / ("%s_theme-logo-%s_800x800.png" % (low, mode)))
            report.append((t / ("%s_theme-logo-%s_800x800.png" % (low, mode)), n, 5 * 1024 * 1024))
            for size in ("1440x810", "3840x2160"):
                dst = t / ("%s_theme-image-%s_%s.jpg" % (low, mode, size))
                save_jpeg(png / ("%s_teams-theme_image-%s_%s.png" % (low, mode, size)), dst, limit=5 * 1024 * 1024)
                report.append((dst, dst.stat().st_size, 5 * 1024 * 1024))
        bgd = out / "teams-backgrounds" / brand
        for f in sorted(png.glob("%s_teams-bg_*.png" % low)):
            dst = bgd / (f.stem + ".jpg")
            save_jpeg(f, dst, quality=88)
            report.append((dst, dst.stat().st_size, None))
        o = out / "org-theme"
        for kind in ("default", "alternative"):
            dst = o / ("%s_m365-logo-%s_200x48.png" % (low, kind))
            n = save_png(png / dst.name, dst, limit=10 * 1024 - 1)
            report.append((dst, n, 10 * 1024))
        variant = {"default": "reversed-dark", "alternative": "mono-white"}
        for kind, v in variant.items():
            dst = o / ("%s_m365-logo-%s.svg" % (low, kind))
            min_svg(C.LOGOS / brand / ("%s_%s.svg" % (brand, v)), dst)
            report.append((dst, dst.stat().st_size, 10 * 1024))
    # Catalogue call backgrounds, copied in beside the new ones.
    cat = catalogue_backgrounds(build)
    for f in sorted(cat.glob("*_call-bg_*.png")):
        brand = {"climb27": "Climb27", "climbuk": "ClimbUK", "climbgroup": "ClimbGroup"}[f.name.split("_")[0]]
        dst = out / "teams-backgrounds" / brand / (f.stem.replace("_call-bg_", "_teams-bg_") + ".jpg")
        save_jpeg(f, dst, quality=88)
        report.append((dst, dst.stat().st_size, None))
    # Branded reactions: Like, Heart, Applause, Laugh and Surprised, in the orange and dark sets.
    old = out / "teams-themes" / "reaction"
    if old.exists():
        shutil.rmtree(old)
    for f in R.compose(png, out / "teams-themes" / "reactions"):
        report.append((f, f.stat().st_size, None))
    # App tiles.
    at = out / "app-tiles"
    for f in sorted(png.glob("m365-tile_*.png")):
        save_png(f, at / f.name.replace("m365-tile_", ""))
    teams_app(out, png)
    # Sign-in page.
    e = out / "sign-in-page"
    dst = e / "climbuk_signin-background_1920x1080.jpg"
    save_jpeg(png / "entra_signin-background_1920x1080.png", dst, limit=300 * 1024 - 1)
    report.append((dst, dst.stat().st_size, 300 * 1024))
    for src, name, limit in [("entra_banner-logo_245x36", "climbuk_banner-logo_245x36.png", 50 * 1024),
                             ("entra_header-logo_245x36", "climbuk_header-logo_245x36.png", 10 * 1024),
                             ("entra_square-logo-dark_240x240", "climbuk_square-logo-dark_240x240.png", 50 * 1024),
                             ("entra_square-logo-light_240x240", "climbuk_square-logo-light_240x240.png", 50 * 1024),
                             ("entra_favicon_32x32", "climbuk_favicon_32x32.png", 5 * 1024)]:
        n = save_png(png / (src + ".png"), e / name, limit=limit - 1)
        report.append((e / name, n, limit))
    bad = [(p, n, l) for p, n, l in report if l and n >= l]
    for p, n, l in bad:
        print("[m365] OVER LIMIT %s: %d bytes (limit %d)" % (p.relative_to(ROOT), n, l))
    print("[m365] %d files checked against their size limits, %d over" % (len(report), len(bad)))
    return not bad


def main(argv):
    build = pathlib.Path(argv[0] if argv else ROOT / "build" / "m365").resolve()
    build.mkdir(parents=True, exist_ok=True)
    build_pages(build)
    problems = write(build)
    for p in problems:
        print("[m365] COPY PROBLEM " + p)
    if problems:
        return 1
    render(build)
    return 0 if save(build) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
