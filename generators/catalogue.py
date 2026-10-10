"""Build the ClimbUK asset catalogue as HTML pages, one per asset, ready to render to PNG.

    python3 generators/catalogue.py [OUT_DIR]     # writes OUT_DIR/html/*.html and manifest.json
    node generators/render.mjs OUT_DIR             # renders OUT_DIR/png/*.png

Resolution rule: 4K by default, always the highest resolution available, never upscale. Platform-sized assets
(social headers, concept packs, the email footer) are laid out at the platform size and rendered at 2x device
scale ("scale" in the manifest), and their file names carry the real pixel size.

Every asset is a ground preset, one motif family, a logo master and at most one display line, following the
climb-visual-style skill. All copy passes the climb-voice checker with the venue embargo on.
"""
import html
import re
import json
import pathlib
import sys

import motifs as M

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
LOGOS = ROOT / "logos"
PHOTOS = ROOT / "photos"
FONTS = ROOT / "fonts"
sys.path.insert(0, str(ROOT / ".agents" / "skills" / "climb-voice" / "scripts"))
import check_copy  # noqa: E402

GROUND = {"dark-brown": "#1E0F05", "charcoal": "#242322", "orange": "#E8712A", "white": "#FFFFFF"}
DATES = "30 June and 1 July 2027"
TAGLINE = "The Festival for Business Growth"

FONT_CSS = """
@font-face{font-family:Montserrat;font-weight:700;src:url('%(f)s/montserrat-latin-700-normal.woff2')}
@font-face{font-family:Montserrat;font-weight:800;src:url('%(f)s/montserrat-latin-800-normal.woff2')}
@font-face{font-family:'Open Sans';font-weight:400;src:url('%(f)s/open-sans-latin-400-normal.woff2')}
@font-face{font-family:'Open Sans';font-weight:600;src:url('%(f)s/open-sans-latin-600-normal.woff2')}
"""


def motif_svg(kind, w, h, seed, dark=True, **kw):
    if kind == "contours":
        return M.contours(w, h, seed=seed, dark=dark, **kw)
    if kind == "stage-light":
        return M.stage_light(w, h, seed=seed, uid="sl%d" % seed)
    if kind == "connections":
        return M.connections(w, h, seed=seed, dark=dark)
    if kind == "ascent":
        size = min(w, h) * 0.34
        return (M.contours(w, h, seed=seed, rings=8, dark=dark, marker=False, cx=0.1, cy=1.05)
                + M.ascent(w, h, w * 0.62, h * 0.88, size, steps=5))
    if kind == "wayfinding":
        # Stacked Ascent chevrons as the direction arrow, top left above the line.
        size = w * 0.5
        return M.ascent(w, h, w * 0.08, h * 0.31, size, steps=3, kind="chevrons")
    raise ValueError(kind)


def logo(brand, variant="reversed-dark"):
    return (LOGOS / brand / ("%s_%s.svg" % (brand, variant))).as_uri()


def logo_ratio(brand, variant):
    """Height over width of a logo master, from its viewBox."""
    svg = (LOGOS / brand / ("%s_%s.svg" % (brand, variant))).read_text(encoding="utf-8")
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', svg).group(1).split()]
    return vb[3] / vb[2]


def page(asset):
    w, h = asset["w"], asset["h"]
    transparent = asset.get("transparent", False)
    ground = "transparent" if transparent else GROUND[asset.get("ground", "dark-brown")]
    dark = asset.get("ground", "dark-brown") != "white"
    scale = min(w, h) / 1080
    parts = []
    if asset.get("motif"):
        parts.append('<svg class="bg" viewBox="0 0 %d %d" width="%d" height="%d">%s</svg>'
                     % (w, h, w, h, motif_svg(asset["motif"], w, h, asset.get("seed", 1), dark,
                                              **asset.get("motif_args", {}))))
    if asset.get("logo"):
        lw = asset.get("logo_w", 0.16) * w
        x, y = asset.get("logo_at", (0.05, 0.07))
        parts.append('<img class="logo" src="%s" style="left:%.0fpx;top:%.0fpx;width:%.0fpx" alt="">'
                     % (logo(asset["brand"], asset.get("logo_variant", "reversed-dark")), x * w, y * h, lw))
    if asset.get("headline"):
        x, y = asset.get("text_at", (0.05, 0.62))
        size = asset.get("headline_px", 96) * scale
        head = html.escape(asset["headline"]).replace("[[", '<mark>').replace("]]", "</mark>")
        sub = ('<p class="sub" style="font-size:%.0fpx">%s</p>' % (max(size * 0.3, 26 * scale), html.escape(asset["sub"]))
               if asset.get("sub") else "")
        anchor = ("bottom:%.0fpx" % (asset["text_bottom"] * h)) if "text_bottom" in asset else ("top:%.0fpx" % (y * h))
        parts.append('<div class="copy" style="left:%.0fpx;%s;max-width:%.0fpx">'
                     '<h1 style="font-size:%.0fpx">%s</h1>%s</div>'
                     % (x * w, anchor, asset.get("text_w", 0.6) * w, size, head, sub))
    if asset.get("extra_html"):
        parts.append(asset["extra_html"])
    css = FONT_CSS % {"f": FONTS.as_uri()} + """
html,body{margin:0;padding:0;background:transparent}
.canvas{position:relative;overflow:hidden;width:%dpx;height:%dpx;background:%s;color:#fff}
.bg{position:absolute;inset:0}
.logo{position:absolute;height:auto}
.copy{position:absolute}
h1{font-family:Montserrat;font-weight:800;text-transform:uppercase;line-height:1.02;letter-spacing:-0.01em;margin:0}
mark{background:#E8712A;color:#fff;padding:0 .12em;box-decoration-break:clone;-webkit-box-decoration-break:clone}
.sub{font-family:'Open Sans';font-weight:600;color:#F2AE86;margin:.6em 0 0;letter-spacing:.02em}
""" % (w, h, ground) + asset.get("extra_css", "")
    return ('<!doctype html><html><head><meta charset="utf-8"><title>%s</title><style>%s</style></head>'
            '<body><div class="canvas">%s</div></body></html>' % (asset["name"], css, "\n".join(parts)))


def size_name(w, h, s=1):
    return "%dx%d" % (w * s, h * s)


PACKS = [
    ("find-your-people", "connections", "Find your [[people]]"),
    ("main-stage-moments", "stage-light", "Main stage [[moments]]"),
    ("bigger-stage", "contours", "Your business. Bigger [[stage]]."),
]


def lower_third():
    """Name bar bottom left inside title safe, edition bug top right, transparent everywhere else."""
    w, h = 3840, 2160
    html_ = ('<div class="lt"><div class="rule"></div><div class="bar">'
             '<div class="nm">Speaker Name</div><div class="role">Role, Company</div></div></div>')
    css = """
.lt{position:absolute;left:%dpx;bottom:%dpx}
.rule{width:128px;height:12px;border-radius:6px;background:#E8712A;margin:0 0 28px}
.bar{background:#1E0F05;border-left:20px solid #E8712A;padding:44px 96px 48px 64px}
.nm{font-family:Montserrat;font-weight:800;text-transform:uppercase;font-size:120px;line-height:1.02;letter-spacing:-0.01em;color:#fff}
.role{font-family:'Open Sans';font-weight:600;font-size:64px;line-height:1.3;color:#F2AE86;margin-top:16px}
""" % (w * 0.06, h * 0.1)
    return dict(name="climb27_lower-third_speaker_%dx%d" % (w, h), group="Stage and screens", brand="Climb27",
                motif=None, w=w, h=h, transparent=True, logo=True, logo_w=0.1, logo_at=(0.86, 0.07),
                extra_html=html_, extra_css=css, copy=["Speaker Name", "Role, Company"])


def sting_end(w, h):
    """End frame of the logo sting: tagline lockup centred under stage light, dates beneath."""
    lw = 0.56 if w > h else 0.8
    lh = lw * w * logo_ratio("Climb27", "tagline-lockup-reversed")
    top = (h - lh) / 2 - h * 0.03
    css = """
.dates{position:absolute;left:0;right:0;top:%dpx;text-align:center;font-family:'Open Sans';font-weight:600;
font-size:%dpx;color:#F2AE86;letter-spacing:.02em}
""" % (top + lh + h * 0.04, 0.05 * min(w, h))
    return dict(name="climb27_sting-end-frame_stage-light_%dx%d" % (w, h), group="Stage and screens", brand="Climb27",
                motif="stage-light", w=w, h=h, seed=61, logo=True, logo_variant="tagline-lockup-reversed",
                logo_w=lw, logo_at=((1 - lw) / 2, top / h),
                extra_html='<div class="dates">%s</div>' % DATES, extra_css=css, copy=[DATES])


def wayfinding(key, line, seed):
    w, h = 2160, 3840
    return dict(name="climb27_wayfinding_%s_%dx%d" % (key, w, h), group="Stage and screens", brand="Climb27",
                motif="wayfinding", w=w, h=h, seed=seed, logo=True, logo_w=0.5, logo_at=(0.08, 0.86),
                headline=line, headline_px=170, text_at=(0.08, 0.38), text_w=0.84)


EMAIL_BANNERS = [
    # key, brand, headline with the emphasis word in [[ ]], subline, five photos left to right, dark ground.
    # Half dark (Dark Brown band), half primary (Climb Orange band); mostly ClimbUK and ClimbGroup in the corner.
    ("bigger-stage", "Climb27", "Your business. Bigger [[stage]].",
     "Climb27. 30 June and 1 July 2027. The Festival for Business Growth.",
     ["climb_band_stage", "climb_expo_floor", "climb_isn_founders_hero", "climb_awards_trophies", "climb_crowd_wide"],
     True),
    ("get-your-ticket", "Climb27", "Get your [[ticket]].",
     "Climb27. 30 June and 1 July 2027. Today's price is the lowest it will be.",
     ["climb_crowd_wide", "climb_band_stage", "climb_expo_floor", "climb_awards_winners", "climb_drinks_reception"],
     False),
    ("find-your-people", "ClimbUK", "Find your [[people]].",
     "Two days with the founders, investors and advisers who move businesses forward.",
     ["climb_drinks_reception", "climb_isn_founders_hero", "climb_consultants_expert", "climb_isn_investors_hero",
      "climb_crowd_wide"], True),
    ("main-stage-moments", "ClimbUK", "Main stage [[moments]].",
     "The grand opening, the ClimbAwards and the after parties.",
     ["climb_stage_region", "climb_awards_winners", "climb_band_stage", "climb_awards_trophies", "climb_drinks_reception"],
     False),
    ("partner", "ClimbUK", "Partner with [[ClimbUK]].",
     "Meetings with the right people, in rooms built for business.",
     ["climb_expo_floor", "climb_consultants_expert", "climb_isn_investors_hero", "climb_stage_region",
      "climb_drinks_reception"], True),
    ("exhibit", "ClimbUK", "Exhibit at [[Climb27]].",
     "Put your team in front of the businesses that buy what you do.",
     ["climb_expo_floor", "climb_crowd_wide", "climb_consultants_expert", "climb_isn_founders_hero",
      "climb_band_stage"], False),
    ("business-with-a-party", "ClimbGroup", "Business with a [[party]].",
     "Main stage moments, real advice and the people who move businesses forward.",
     ["climb_band_stage", "climb_drinks_reception", "climb_awards_winners", "climb_crowd_wide", "climb_stage_region"],
     True),
    ("festival", "ClimbGroup", "The Festival for [[Business Growth]].",
     "Find your people at Climb27. 30 June and 1 July 2027.",
     ["climb_crowd_wide", "climb_awards_trophies", "climb_isn_founders_hero", "climb_band_stage", "climb_expo_floor"],
     False),
]


def email_banner(key, brand, line, sub, photos, scale, dark=False):
    """720x205 campaign banner under the email signature: a copy band with the logo top right, a strip of five
    event photos cut to cover, and a thin Climb Orange foot. Orange band: white headline (well above the 19px
    bold rule), one Dark Brown word, Dark Brown subline. Dark variant: Dark Brown band, orange word, Orange Tint
    subline, reversed logo."""
    w, h = 720, 205
    band, foot, gap = 92, 8, 3
    strip = h - band - foot
    head = html.escape(line).replace("[[", '<span class="em">').replace("]]", "</span>")
    variant = "reversed-dark" if dark else "mono-white"
    tiles = "".join('<div class="ph" style="background-image:url(\'%s\')"></div>' % (PHOTOS / (p + ".jpg")).as_uri()
                    for p in photos)
    html_ = ('<div class="band"><div class="txt"><h1 class="hl">%s</h1><p class="sl">%s</p></div>'
             '<div class="brand"><img src="%s" alt=""><span>www.climb-uk.com</span></div></div>'
             '<div class="strip">%s</div><div class="foot"></div>'
             # Long headlines step down from 27px until they clear the logo column (never below 20px).
             '<script>document.fonts.ready.then(function(){var h=document.querySelector(".hl"),s=27;'
             'while(h.scrollWidth>h.clientWidth&&s>20){s-=0.5;h.style.fontSize=s+"px";}});</script>'
             % (head, html.escape(sub), logo(brand, variant), tiles))
    ink, em, sl = ("#FFFFFF", "#E8712A", "#F2AE86") if dark else ("#FFFFFF", "#1E0F05", "#1E0F05")
    css = """
.band{position:absolute;left:0;top:0;width:%(w)dpx;height:%(band)dpx;display:flex;align-items:center}
.txt{position:absolute;left:24px;top:0;bottom:0;width:516px;display:flex;flex-direction:column;justify-content:center}
.hl{font-family:Montserrat;font-weight:800;text-transform:uppercase;font-size:27px;line-height:1.02;
letter-spacing:-0.01em;color:%(ink)s;margin:0;white-space:nowrap;overflow:hidden}
.hl .em{color:%(em)s}
.sl{font-family:'Open Sans';font-weight:600;font-size:13px;line-height:1.35;color:%(sl)s;margin:7px 0 0}
.brand{position:absolute;right:24px;top:16px;width:132px;display:flex;flex-direction:column;align-items:flex-end}
.brand img{display:block;width:132px;height:auto}
.brand span{font-family:Montserrat;font-weight:700;font-size:12px;letter-spacing:.02em;color:%(sl)s;margin-top:7px}
.strip{position:absolute;left:0;top:%(band)dpx;width:%(w)dpx;height:%(strip)dpx;display:flex;gap:%(gap)dpx}
.ph{flex:1;background-size:cover;background-position:center}
.foot{position:absolute;left:0;bottom:0;width:%(w)dpx;height:%(foot)dpx;background:#E8712A}
""" % dict(w=w, band=band, strip=strip, gap=gap, foot=foot, ink=ink, em=em, sl=sl)
    name = "%s_email-banner_%s%s_%s" % (brand.lower(), key, "-dark" if dark else "", size_name(w, h, scale))
    return dict(name=name, group="Email banners", brand=brand, motif=None, w=w, h=h, scale=scale,
                ground="dark-brown" if dark else "orange", extra_html=html_, extra_css=css,
                copy=[line.replace("[[", "").replace("]]", ""), sub, "www.climb-uk.com"])


def assets():
    out = []
    # Calls, Wallpapers, Social and Print and merch: festival poster layouts with the hand drawn line layer.
    import poster_kit
    out += poster_kit.assets(sys.modules[__name__])
    # Stage: holding and walk-in slides, one line each, readable from the back of the room.
    for key, motif, line in PACKS:
        out.append(dict(name="climb27_holding-slide_%s_3840x2160" % key, group="Stage and screens", brand="Climb27",
                        motif=motif, w=3840, h=2160, seed=52, logo=True, logo_w=0.2, logo_at=(0.06, 0.09),
                        headline=line, sub=DATES + ". " + TAGLINE + ".", headline_px=150,
                        text_at=(0.06, 0), text_bottom=0.11, text_w=0.8,
                        motif_args={"cx": 0.95, "cy": 0.22} if motif == "contours" else {}))
    out.append(lower_third())
    out.append(sting_end(3840, 2160))
    out.append(sting_end(2160, 3840))
    out.append(wayfinding("find-your-people", "Find your [[people]]", 71))
    out.append(wayfinding("main-stage-moments", "Main stage [[moments]]", 72))
    # Email banners: the 720x205 campaign strip under the signature, at 2x and 4x.
    for scale in (2, 4):
        for key, brand, line, sub, photos, dark in EMAIL_BANNERS:
            out.append(email_banner(key, brand, line, sub, photos, scale, dark=dark))
    # Festival kit: name cards, share tiles, affiliate tickets, photo pull-up, document covers, table signs.
    import festival_kit
    out += festival_kit.assets(sys.modules[__name__])
    return out


def main(argv):
    out_dir = pathlib.Path(argv[0] if argv else "build").resolve()
    (out_dir / "html").mkdir(parents=True, exist_ok=True)
    manifest, problems = [], []
    for a in assets():
        text = " ".join([a.get(k, "") for k in ("headline", "sub")] + a.get("copy", []))
        text = text.replace("[[", "").replace("]]", "")
        problems += ["%s: %s (%s)" % (a["name"], p[2], p[3]) for p in check_copy.check(text)]
        path = out_dir / "html" / (a["name"] + ".html")
        path.write_text(page(a), encoding="utf-8")
        manifest.append({"name": a["name"], "w": a["w"], "h": a["h"], "scale": a.get("scale", 1),
                         "transparent": a.get("transparent", False), "group": a["group"], "html": str(path),
                         **({"set": a["set"]} if a.get("set") else {})})
    footer = (HERE / "email" / "footer.html").read_text(encoding="utf-8")
    text = re.sub(r"<!--.*?-->|<[^>]+>|&[a-z]+;", " ", footer, flags=re.S)
    problems += ["email footer: %s (%s)" % (p[2], p[3]) for p in check_copy.check(text)]
    footer = footer.replace("LOGO_URL", logo("ClimbUK")).replace(
        "DOODLES_URL", (out_dir / "png" / "climbuk_email-footer-doodles_1200x192.png").as_uri())
    path = out_dir / "html" / "climbuk_email-footer_1200.html"
    path.write_text('<!doctype html><html><head><meta charset="utf-8"><style>%s body{margin:0}'
                    '.canvas{width:600px}</style></head><body><div class="canvas">%s</div></body></html>'
                    % (FONT_CSS % {"f": FONTS.as_uri()}, footer), encoding="utf-8")
    manifest.append({"name": "climbuk_email-footer_1200", "w": 600, "h": 400, "scale": 2, "transparent": False,
                     "group": "Social", "html": str(path)})
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    import poster_kit
    for n in poster_kit.NOTES:
        print("[catalogue] RESOLUTION " + n)
    for p in problems:
        print("[catalogue] COPY PROBLEM " + p)
    print("[catalogue] %d assets written to %s" % (len(manifest), out_dir))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
