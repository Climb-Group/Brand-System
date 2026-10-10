"""Background art for the Office templates, drawn from the motif recipes and rendered with Chromium.

python3 art.py   ->   OUT/_art/*.png|jpg
"""
import json
import os
import subprocess
import sys

from PIL import Image

import brand as B
import motifs as M

ART = os.path.join(B.OUT, "_art")
TMP = os.path.join(ART, "_html")

FONT_CSS = """
body{margin:0} *{box-sizing:border-box}
"""


def page(w, h, body, bg="transparent", extra_css=""):
    return ('<!doctype html><html><head><meta charset="utf-8"><style>%s html,body{width:%dpx;height:%dpx;background:%s;'
            'overflow:hidden}%s</style></head><body>%s</body></html>' % (FONT_CSS, w, h, bg, extra_css, body))


def svg(w, h, inner):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
            'style="position:absolute;left:0;top:0">%s</svg>' % (w, h, w, h, inner))


def glow(cx, cy, rx, ry, colour="#E8712A", opacity=0.45, uid="g"):
    return ('<defs><radialGradient id="%s"><stop offset="0" stop-color="%s" stop-opacity="%.2f"/>'
            '<stop offset="1" stop-color="%s" stop-opacity="0"/></radialGradient></defs>'
            '<ellipse cx="%d" cy="%d" rx="%d" ry="%d" fill="url(#%s)"/>' % (uid, colour, opacity, colour, cx, cy, rx, ry, uid))


def photo_fade(photos, w, h, top_h, fade_to="#1E0F05", y0=0):
    """A row of real photos across the top, faded into the ground below. y0 leaves a solid band for the logo."""
    n = len(photos)
    cells = []
    if n == 3:
        boxes = [(0, 0, w * 0.5, top_h * 0.52), (w * 0.5, 0, w * 0.5, top_h * 0.52), (0, top_h * 0.52, w, top_h * 0.48)]
    elif n == 2:
        boxes = [(0, 0, w * 0.55, top_h), (w * 0.55, 0, w * 0.45, top_h)]
    else:
        boxes = [(0, 0, w, top_h)]
    boxes = [(x, y0 + y * (top_h - y0) / top_h, bw, bh * (top_h - y0) / top_h) for x, y, bw, bh in boxes]
    for (x, y, bw, bh), p in zip(boxes, photos):
        cells.append('<div style="position:absolute;left:%dpx;top:%dpx;width:%dpx;height:%dpx;'
                     'background:url(file://%s) center/cover;outline:%dpx solid %s"></div>'
                     % (x, y, bw + 1, bh + 1, B.photo(p), max(2, w // 300), fade_to))
    cells.append('<div style="position:absolute;left:0;top:%dpx;width:%dpx;height:%dpx;'
                 'background:linear-gradient(to bottom, rgba(30,15,5,0) 0%%, rgba(30,15,5,.55) 45%%, %s 100%%)"></div>'
                 % (top_h * 0.45, w, top_h * 0.56, fade_to))
    return "".join(cells)


def jobs():
    W, H = 3840, 2160
    J = []

    def add(name, w, h, html, transparent=False, fmt="jpg"):
        J.append(dict(name=name, w=w, h=h, html=html, transparent=transparent, fmt=fmt))

    # Slides, 16:9 at 4K.
    add("slide_title", W, H, page(W, H, svg(W, H,
        M.stage_light(W, H, seed=4, beams=3, uid="a") +
        M.peak(W, H, x0=0.38, base=0.9, summit=(0.78, 0.52), seed=3, colour="#E8712A", opacity=0.55) +
        M.slabs(W, H, corners=("br",), length=W * 0.2, thick=H * 0.05) +
        M.grain(W, H, seed=2, opacity=0.05)), bg="#1E0F05"))
    add("slide_dark", W, H, page(W, H, svg(W, H,
        glow(W * 0.95, H * 1.02, W * 0.42, H * 0.5, opacity=0.32) +
        M.slabs(W, H, corners=("tl",), length=W * 0.09, thick=H * 0.022) +
        M.grain(W, H, seed=5, opacity=0.04)), bg="#1E0F05"))
    add("slide_charcoal", W, H, page(W, H, svg(W, H,
        M.contours(W, H, seed=7, rings=14, dark=True, marker=True, cx=0.92, cy=0.95) +
        M.slabs(W, H, corners=("tl",), length=W * 0.09, thick=H * 0.022)), bg="#242322"))
    add("slide_light", W, H, page(W, H, svg(W, H,
        M.contours(W, H, seed=9, rings=10, dark=False, marker=False, cx=1.0, cy=1.05) +
        M.slabs(W, H, corners=("tl",), length=W * 0.09, thick=H * 0.022)), bg="#FFFFFF"))
    add("slide_section", W, H, page(W, H, svg(W, H,
        M.ascent(W, H, W * 0.64, H * 1.04, H * 1.1, steps=6, colour="rgba(30,15,5,0.14)", kind="chevrons") +
        M.slabs(W, H, corners=("bl",), length=W * 0.26, thick=H * 0.06, colour="#1E0F05")), bg="#E8712A"))
    add("slide_quote", W, H, page(W, H, svg(W, H,
        M.connections(W, H, seed=11, dots=40, dark=True, region=(0.55, 0.05, 0.98, 0.95)) +
        glow(W * 0.05, H * 0.0, W * 0.35, H * 0.45, opacity=0.25, uid="q") +
        M.grain(W, H, seed=6, opacity=0.04)), bg="#1E0F05"))
    add("slide_end", W, H, page(W, H, svg(W, H,
        M.stage_light(W, H, seed=12, beams=4, uid="e") +
        glow(W * 0.5, H * 0.5, W * 0.45, H * 0.4, opacity=0.18, uid="e2") +
        M.peak(W, H, x0=0.0, base=0.95, summit=(0.5, 0.74), seed=5, colour="#E8712A", opacity=0.45) +
        M.grain(W, H, seed=7, opacity=0.05)), bg="#1E0F05"))
    add("slide_stats", W, H, page(W, H, svg(W, H,
        M.ascent(W, H, W * 0.0, H * 1.0, H * 0.32, steps=5, colour="rgba(232,113,42,0.16)") +
        glow(W, 0, W * 0.4, H * 0.5, opacity=0.22, uid="s") +
        M.grain(W, H, seed=8, opacity=0.04)), bg="#1E0F05"))

    # A4 portrait covers and inner pages at 200 dpi (1654x2339).
    aw, ah = 1654, 2339
    covers = {"ClimbUK": ["crowd_wide", "band_stage", "drinks_reception"],
              "ClimbGroup": ["expo_floor", "consultants_expert"],
              "Climb27": ["stage_region", "awards_winners", "isn_founders_hero"]}
    for b, ph in covers.items():
        add("a4_cover_%s" % b, aw, ah, page(aw, ah, photo_fade(ph, aw, ah, ah * 0.62, y0=ah * 0.1) + svg(aw, ah,
            M.contours(aw, ah, seed=3, rings=9, dark=True, marker=False, cx=0.95, cy=1.0) +
            M.slabs(aw, ah, corners=("br",), length=aw * 0.34, thick=ah * 0.028) +
            M.grain(aw, ah, seed=3, opacity=0.05)), bg="#1E0F05"))
    # Letterhead corner marks (transparent), placed by the Word header.
    add("a4_slab_br", 900, 90, page(900, 90, svg(900, 90, M.slabs(900, 90, corners=("br",), length=900, thick=90))),
        transparent=True, fmt="png")
    add("a4_slab_tl", 600, 60, page(600, 60, svg(600, 60, M.slabs(600, 60, corners=("tl",), length=600, thick=60))),
        transparent=True, fmt="png")
    add("rule_short", 256, 24, page(256, 24, '<div style="width:256px;height:24px;border-radius:12px;background:#E8712A"></div>'),
        transparent=True, fmt="png")
    # A4 section divider band for reports (Dark Brown band with contours), full width 2480x700.
    add("a4_band", 2480, 620, page(2480, 620, svg(2480, 620,
        M.contours(2480, 620, seed=21, rings=10, dark=True, marker=True, cx=0.9, cy=1.2) +
        M.slabs(2480, 620, corners=("br",), length=620, thick=40)), bg="#1E0F05"))

    # Spreadsheet header banners with the reversed logo.
    for b in B.BRANDS:
        bw, bh = 3000, 300
        lr = Image.open(B.logo(b, "reversed-dark")).size
        lh = 120
        lw = lh * lr[0] / lr[1]
        add("xl_banner_%s" % b, bw, bh, page(bw, bh, svg(bw, bh,
            glow(bw * 0.85, 0, bw * 0.3, bh * 1.6, opacity=0.35, uid="x") +
            M.slabs(bw, bh, corners=("br",), length=bw * 0.12, thick=bh * 0.12)) +
            '<img src="file://%s" style="position:absolute;left:70px;top:%dpx;height:%dpx;width:%dpx">'
            % (B.logo(b, "reversed-dark"), (bh - lh) // 2, lh, lw), bg="#1E0F05"), fmt="png")
    return J


def main():
    os.makedirs(TMP, exist_ok=True)
    only = sys.argv[1:]
    J = [j for j in jobs() if not only or any(o in j["name"] for o in only)]
    run = []
    for j in J:
        hp = os.path.join(TMP, j["name"] + ".html")
        with open(hp, "w") as f:
            f.write(j["html"])
        run.append(dict(html=hp, out=os.path.join(TMP, j["name"] + ".png"), w=j["w"], h=j["h"], transparent=j["transparent"]))
    jp = os.path.join(TMP, "jobs.json")
    json.dump(run, open(jp, "w"))
    subprocess.run(["node", os.path.join(B.ROOT, "render.mjs"), jp], check=True)
    for j, r in zip(J, run):
        im = Image.open(r["out"])
        if j["fmt"] == "jpg":
            im.convert("RGB").save(os.path.join(ART, j["name"] + ".jpg"), quality=86, optimize=True, progressive=True)
        else:
            im.save(os.path.join(ART, j["name"] + ".png"), optimize=True)
        print(j["name"], im.size)


if __name__ == "__main__":
    main()
