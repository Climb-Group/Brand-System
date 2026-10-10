"""Build the SharePoint brand centre artwork: page banners, quick link tiles, site header, logo and footer.

Usage: python3 build_sharepoint_assets.py PACK OUT
PACK is a checkout of the brand pack (with photos/candid), OUT the folder for the finished files.
Lays out each image as HTML from the tokens, photos, shapes and drawings, renders it with headless Chromium and saves
it as JPEG under 300 KB (the SharePoint page image budget) or PNG where transparency matters.
"""
import io, json, subprocess, sys
from pathlib import Path
from PIL import Image

PACK, OUT = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
BUILD = OUT / "_html"
BUILD.mkdir(parents=True, exist_ok=True)

DARK, CHAR, ORANGE, TINT, GREY = "#1E0F05", "#242322", "#E8712A", "#F2AE86", "#E9E9E9"

# slug, photo, focus (CSS object-position), drawing for the quick link tile
PAGES = [
    ("home", "photos/climb_crowd_wide.jpg", "50% 45%", "rocket"),
    ("our-brand", "photos/candid/joy_01.jpg", "50% 40%", "ladder"),
    ("voice", "photos/candid/stage_speakers_01.jpg", "50% 35%", "microphone"),
    ("logos", "photos/candid/vip_and_awards_01.jpg", "50% 40%", "stage-pass"),
    ("colour-and-type", "photos/candid/audience_at_stage_02.jpg", "50% 40%", "pencil"),
    ("photography", "photos/candid/crowds_03.jpg", "50% 45%", "selfie"),
    ("drawings-and-devices", "photos/candid/roundtable_and_workshops_01.jpg", "50% 40%", "lightbulb"),
    ("templates", "photos/candid/meetings_01.jpg", "50% 40%", "slide-deck"),
    ("microsoft-365", "photos/candid/media_01.jpg", "50% 40%", "video-call"),
    ("artwork-library", "photos/candid/exhibitor_01.jpg", "50% 40%", "big-screen"),
    ("guidelines", "photos/climb_stage_region.jpg", "50% 40%", "book-open"),
    ("get-help", "photos/candid/climbteam_01.jpg", "50% 35%", "hand-raised"),
]
EXTRA_TILES = [("downloads", "goodie-bag"), ("brand-hub", "compass"), ("website", "globe"), ("tickets", "tickets")]

FONTS = "".join(
    "@font-face{font-family:'%s';font-weight:%s;font-style:%s;src:url('%s')}" % (fam, w, st, p.as_uri())
    for fam, w, st, p in [
        ("Montserrat", 800, "normal", PACK / "fonts/montserrat-latin-800-normal.woff2"),
        ("Montserrat", 700, "normal", PACK / "fonts/montserrat-latin-700-normal.woff2"),
    ]
)
GRAIN = ("<svg class='grain' xmlns='http://www.w3.org/2000/svg' width='100%' height='100%'><filter id='n'>"
         "<feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/>"
         "<feColorMatrix values='0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 .05 0'/></filter>"
         "<rect width='100%' height='100%' filter='url(#n)'/></svg>")
BASE = ("*{margin:0;padding:0;box-sizing:border-box}html,body{background:%s}"
        ".canvas{position:relative;overflow:hidden;background:%s}"
        ".grain{position:absolute;inset:0;pointer-events:none}" % (DARK, DARK))


def shape(n, opacity, colour="#FFFFFF"):
    svg = (PACK / ("illustrations/shapes/%02d.svg" % n)).read_text()
    svg = svg.replace('stroke="#FFFFFF"', 'stroke="%s"' % colour)
    return "<div style='position:absolute;inset:0;opacity:%s'>%s</div>" % (opacity, svg.replace(
        "<svg ", "<svg style='width:100%;height:100%' ", 1))


def drawing(name, size):
    svg = (PACK / ("illustrations/%s.svg" % name)).read_text()
    return svg.replace('width="200" height="200"', 'width="%d" height="%d"' % (size, size), 1)


jobs = []


def page(name, w, h, body, css="", fmt="jpg", limit=300_000):
    html = BUILD / ("%s.html" % name)
    html.write_text("<!doctype html><meta charset='utf-8'><style>%s%s.canvas{width:%dpx;height:%dpx}%s</style>"
                    "<div class='canvas'>%s</div>" % (FONTS, BASE, w, h, css, body))
    jobs.append({"name": name, "html": str(html), "w": w, "h": h, "fmt": fmt, "limit": limit})


# Page banners: full photo, Dark Brown fade on the lower left where SharePoint sets the page title, an orange stage
# glow in the top right corner, grain. No words: the page title is live text.
for slug, photo, focus, _ in PAGES:
    src = (PACK / photo).as_uri()
    page("banner_%s" % slug, 1920, 1080,
         "<img src='%s' style='position:absolute;inset:0;width:100%%;height:100%%;object-fit:cover;"
         "object-position:%s'>"
         "<div style='position:absolute;inset:0;background:linear-gradient(0deg,rgba(30,15,5,.92) 0%%,"
         "rgba(30,15,5,.55) 34%%,rgba(30,15,5,0) 62%%)'></div>"
         "<div style='position:absolute;inset:0;background:linear-gradient(90deg,rgba(30,15,5,.7) 0%%,"
         "rgba(30,15,5,0) 55%%)'></div>"
         "<div style='position:absolute;right:-260px;top:-300px;width:900px;height:900px;border-radius:50%%;"
         "background:radial-gradient(circle,rgba(232,113,42,.55),rgba(232,113,42,0) 65%%);mix-blend-mode:screen'>"
         "</div>%s" % (src, focus, GRAIN))

# Quick link tiles: one drawing in Climb Orange on Dark Brown, contour rings behind, an orange glow. No words.
for i, (slug, ill) in enumerate([(p[0], p[3]) for p in PAGES] + EXTRA_TILES):
    page("tile_%s" % slug, 1200, 675,
         "%s<div style='position:absolute;left:50%%;top:50%%;width:620px;height:620px;transform:translate(-50%%,-50%%);"
         "border-radius:50%%;background:radial-gradient(circle,rgba(232,113,42,.30),rgba(232,113,42,0) 68%%)'></div>"
         "<div style='position:absolute;left:50%%;top:50%%;transform:translate(-50%%,-50%%);color:%s;"
         "--doodle-ink:%s;--doodle-ground:%s'>%s</div>%s"
         % (shape([1, 2, 4][i % 3], .10), ORANGE, ORANGE, DARK, drawing(ill, 380), GRAIN))

# Section background for full width sections: quiet contours on Dark Brown with a low glow.
page("section_contours-dark", 1920, 1080,
     "%s<div style='position:absolute;left:-300px;bottom:-500px;width:1300px;height:1300px;border-radius:50%%;"
     "background:radial-gradient(circle,rgba(232,113,42,.22),rgba(232,113,42,0) 65%%)'></div>%s" % (shape(1, .09), GRAIN))
page("section_contours-charcoal", 1920, 1080,
     "<div style='position:absolute;inset:0;background:%s'></div>%s%s" % (CHAR, shape(2, .08), GRAIN))

# Site header background (extended header layout): a thin strip with contours and a glow at the right.
page("site_header-background", 2560, 164,
     "%s<div style='position:absolute;right:-200px;top:-500px;width:1100px;height:1100px;border-radius:50%%;"
     "background:radial-gradient(circle,rgba(232,113,42,.45),rgba(232,113,42,0) 62%%)'></div>%s"
     % (shape(5, .14), GRAIN))

# Site logo (square, shown at 64px and below: the li monogram) and footer logo (reversed wordmark).
mono = (PACK / "logos/ClimbUK/ClimbUK_icon-monogram.svg").read_text()
page("site_logo", 192, 192, "<div style='width:192px;height:192px'>%s</div>"
     % mono.replace("<svg ", "<svg style='width:100%;height:100%' ", 1), fmt="png", limit=None)
word = (PACK / "logos/ClimbUK/ClimbUK_reversed-dark.svg").read_text()
page("site_footer-logo", 480, 160, "<div style='position:absolute;inset:28px 40px'>%s</div>"
     % word.replace("<svg ", "<svg style='width:100%;height:100%' ", 1), css="html,body,.canvas{background:transparent}",
     fmt="png", limit=None)

(BUILD / "jobs.json").write_text(json.dumps(jobs))
render = Path(__file__).with_name("render.mjs")
subprocess.run(["node", str(render), str(BUILD / "jobs.json"), str(BUILD / "png")], check=True)

folders = {"banner": "banners", "tile": "quick-link-tiles", "section": "section-backgrounds", "site": "site"}
for job in jobs:
    kind, slug = job["name"].split("_", 1)
    dest = OUT / folders[kind]
    dest.mkdir(parents=True, exist_ok=True)
    im = Image.open(BUILD / "png" / ("%s.png" % job["name"]))
    stem = "climbuk_sharepoint-%s_%s_%dx%d" % (kind, slug, job["w"], job["h"])
    if job["fmt"] == "png":
        im.save(dest / (stem + ".png"), optimize=True)
        continue
    im = im.convert("RGB")
    for q in range(90, 40, -4):
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=q, optimize=True, progressive=True)
        if buf.tell() <= job["limit"]:
            break
    (dest / (stem + ".jpg")).write_bytes(buf.getvalue())
    print("%-70s q%d %d KB" % (stem, q, buf.tell() // 1024))
