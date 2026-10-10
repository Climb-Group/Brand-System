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
import shapes as S  # noqa: E402

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
    """Meeting theme image, laid out at the recommended 1440x810. Dark: a Climb26 photo under a Dark Brown fade with
    the orange glow and the brand line on the solid side. Light: White ground, tilted photo cards, Charcoal line with
    the orange word in Orange Text (4.6:1, so the line passes even at small display sizes)."""
    w, h = 1440, 810
    b = B[brand]
    K = P.Kit(C, brand, scale)
    p = []
    if mode == "dark":
        p.append(K.pic(b["dark_photo"], int(w * 0.34), 0, w - int(w * 0.34), h, pos=b["dark_pos"],
                       fade=P.fade("to right", 0, 70, 1.0, 0.0)))
        p.append(P.glow(w, h, w, 0, w * 0.5, 0.42))
        p.append(F.svg(w, h, M.contours(w, h, seed=21, rings=8, dark=True, marker=False, cx=-0.05, cy=1.08)))
        p.append(P.head(b["line"], 96, h * 0.5, 92, 600, anchor="top", lh=0.98).replace(
            "top:%.0fpx" % (h * 0.5), "top:%.0fpx;transform:translateY(-50%%)" % (h * 0.5)))
        p.append(P.sticker(theme_sticker(brand), 96, h - 120, 26, rot=-4))
        p.append(F.grain_layer(w, h, 31, 0.06))
        ground = "dark-brown"
    else:
        cards = b["cards"]
        p.append(F.svg(w, h, M.contours(w, h, seed=22, rings=9, dark=False, marker=False, cx=1.05, cy=1.1)))
        p.append(F.svg(w, h, M.slabs(w, h, corners=("br",), length=w * 0.2, thick=h * 0.05)))
        p.append(K.pic(cards[0], 820, 90, 400, 300, rot=-5, radius=18, shadow=True))
        p.append(K.pic(cards[1], 1010, 330, 360, 260, rot=4, radius=18, shadow=True))
        p.append(K.pic(cards[2], 770, 440, 300, 230, rot=-2, radius=18, shadow=True))
        line = [l.replace("[[", "{{").replace("]]", "}}") for l in b["line"]]
        hd = P.head(line, 96, h * 0.5, 92, 600, anchor="top", colour=CH, lh=0.98)
        hd = hd.replace("top:%.0fpx" % (h * 0.5), "top:%.0fpx;transform:translateY(-50%%)" % (h * 0.5))
        hd = hd.replace("{{", '<span style="color:%s">' % OR_TEXT).replace("}}", "</span>")
        p.append(hd)
        p.append(P.sticker(theme_sticker(brand), 96, h - 120, 26, rot=-4, tone="brown"))
        ground = "white"
    copy = [F.plain(l) for l in b["line"]] + [theme_sticker(brand)]
    add("%s_teams-theme_image-%s_%s" % (brand.lower(), mode, label), w, h, p, copy, scale=scale, ground=ground)


# ---------------------------------------------------------------- Organisation backgrounds

SEED = {"ClimbUK": 1, "ClimbGroup": 2, "Climb27": 3}
SHAPE_SETS = ["funky", "wavy", "simple", "shapes", "pop", "stickers", "photo-cards"]
NOTES = []


def bg_shapes(brand, kind):
    """Graphic background in the Climb26 call background style: blobs and marks over the edges, the middle calm for
    the person, the logo top left in whichever variant reads on the shape under it. photo-cards and stickers add
    tilted Climb26 photo cards and house drawings as accents; photos never fill the frame."""
    w, h = 3840, 2160
    name = "%s_teams-bg_%s_%dx%d" % (brand.lower(), kind, w, h)
    b = B[brand]
    seed = SEED[brand]
    field, spec = S.LAYOUTS["funky" if kind == "photo-cards" else kind](seed + (10 if kind == "photo-cards" else 0))
    p = ['<svg class="abs" style="left:0;top:0" viewBox="0 0 %d %d" width="%d" height="%d">%s%s</svg>'
         % (w, h, w, h, field.body(), S.marks(field, spec if kind != "photo-cards" else spec[:6]))]
    K = P.Kit(C, name)
    copy = []
    if kind == "photo-cards":
        cards = b["cards"]
        p.append(K.pic(cards[0], 2900, 120, 820, 560, rot=6, radius=28, shadow=True, frame="14px solid #FFFFFF"))
        p.append(K.pic(cards[1], 3020, 1240, 700, 480, rot=-5, radius=28, shadow=True, frame="14px solid #FFFFFF"))
        p.append(K.pic(cards[2], 150, 1300, 760, 520, rot=-4, radius=28, shadow=True, frame="14px solid #FFFFFF"))
        p.append(P.sticker(b["sticker"], 260, 1220, 60, rot=-5))
        copy.append(b["sticker"])
    elif kind == "stickers":
        drawings = [b["hero"], "sparkles", "tickets", "star", "megaphone", "party-popper"]
        spots = [(3080, 1380, 680, 8), (140, 1000, 500, -12), (2700, 90, 420, 14), (520, 1620, 400, -8),
                 (2150, 40, 300, 18), (2350, 1720, 340, -16)]
        for d, (x, y, sz, r) in zip(drawings, spots):
            ink = S.mark_colour(field, (x + sz / 2) / S.K, (y + sz / 2) / S.K)
            p.append(I.place(d, x, y, sz, rotate=r, weight=1.2, ink=ink, ground=field.under((x + sz / 2) / S.K, (y + sz / 2) / S.K)))
        p.append(K.pic(b["cards"][0], 2860, 520, 640, 460, rot=7, radius=24, shadow=True, frame="12px solid #FFFFFF"))
        p.append(P.sticker(b["sticker"], 180, 1900, 60, rot=-4))
        copy.append(b["sticker"])
    elif kind in ("funky", "pop"):
        p.append(P.sticker(b["sticker"], 160, 1960, 58, rot=-4, tone="brown" if kind == "pop" else "orange"))
        copy.append(b["sticker"])
    p.append(F.grain_layer(w, h, 80 + seed, 0.04))
    under = field.uniform(*S.LOGO)
    if under is None:
        NOTES.append("%s: logo sits over more than one colour" % name)
        under = field.under(S.LOGO[0], S.LOGO[1])
    variant = S.ON.get(under, (None, "reversed-dark"))[1]
    p.append(F.logo_img(C, brand, variant, w * 0.04, h * 0.06, w * 0.15))
    calm = max(field.calm_share(*S.PERSON, c) for c in (S.TONE, S.CH, S.WH, S.OR, S.DB))
    if calm < 0.75:
        NOTES.append("%s: the person zone is only %d%% one colour" % (name, calm * 100))
    ground = {S.CH: "charcoal", S.TONE: "charcoal", S.WH: "white", S.OR: "orange", S.DB: "dark-brown"}[field.ground]
    a = add(name, w, h, p, copy, group="Backgrounds", ground=ground)
    if field.ground == S.TONE:
        a["extra_css"] += ".canvas{background:linear-gradient(%s,%s),%s !important}" % (S.TONE_CSS, S.TONE_CSS, S.CH)


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
    else:
        p = [F.svg(w, h, M.contours(w, h, seed=32, rings=13, dark=False, marker=False, cx=1.04, cy=1.06)),
             F.svg(w, h, M.slabs(w, h, corners=("br",), length=w * 0.22, thick=h * 0.05)),
             F.logo_img(C, brand, "full-colour-grey", w * 0.04, h * 0.06, w * 0.15)]
        ground = "light-grey"
    a = add(name, w, h, p, group="Backgrounds", ground="dark-brown")
    if ground == "light-grey":
        a["extra_css"] += ".canvas{background:%s !important}" % LG


def bg_frosted(brand, kind):
    """Frosted glass background: a transparent PNG. Teams blurs the person's own room through the clear areas and
    keeps the brand graphic sharp. corner: logo on a Dark Brown card top left, slab and chevrons bottom right.
    band: a Dark Brown band along the bottom with the tagline lockup."""
    w, h = 3840, 2160
    name = "%s_teams-bg_frosted-%s_%dx%d" % (brand.lower(), kind, w, h)
    p = []
    if kind == "corner":
        lw = w * 0.15
        lh = lw * C.logo_ratio(brand, "reversed-dark")
        pad = lh * 1.0
        p.append('<div class="abs" style="left:%.0fpx;top:%.0fpx;width:%.0fpx;height:%.0fpx;background:%s;'
                 'border-radius:%.0fpx"></div>' % (w * 0.04 - pad, h * 0.06 - pad, lw + 2 * pad, lh + 2 * pad, DB,
                                                   pad * 0.5))
        p.append(F.logo_img(C, brand, "reversed-dark", w * 0.04, h * 0.06, lw))
        p.append(P.slab_poly([(w - 1100, h), (w, h - 980), (w, h)], OR))
        p.append(P.chevrons(w - 470, h - 110, 470, steps=3, colour=DB, w=w, h=h))
    else:
        bh = h * 0.16
        p.append('<div class="abs" style="left:0;top:%.0fpx;width:%.0fpx;height:%.0fpx;background:%s"></div>'
                 % (h - bh, w, bh, DB))
        p.append('<div class="abs" style="left:0;top:%.0fpx;width:%.0fpx;height:%.0fpx;background:%s"></div>'
                 % (h - bh - 14, w, 14, OR))
        lw = w * 0.3
        lh = lw * C.logo_ratio(brand, "tagline-lockup-reversed")
        p.append(F.logo_img(C, brand, "tagline-lockup-reversed", w * 0.04, h - bh / 2 - lh / 2, lw))
        p.append(P.chevrons(w - 380, h - bh / 2 + 120, 240, steps=3, colour=OR, w=w, h=h))
    add(name, w, h, p, transparent=True, group="Backgrounds")


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
        for kind in SHAPE_SETS:
            bg_shapes(brand, kind)
        bg_calm(brand, "dark")
        bg_calm(brand, "light")
        bg_frosted(brand, "corner")
        bg_frosted(brand, "band")
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
            if "frosted" in f.name:
                dst = bgd / f.name.replace("_teams-bg_", "_teams-bg_")
                save_png(f, dst)
            else:
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
    for n in NOTES:
        print("[m365] LAYOUT " + n)
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
