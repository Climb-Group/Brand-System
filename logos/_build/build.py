#!/usr/bin/env python3
"""Build 2026 master logos from the normalised source SVGs."""
import os, re, subprocess, io
from lxml import etree
from PIL import Image

S = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(S, ".."))  # logos
NS = "http://www.w3.org/2000/svg"

ORANGE, ORANGE_GREY, BROWN, CHAR, GREY, WHITE = "#E8712A", "#D5641E", "#1E0F05", "#242322", "#E9E9E9", "#FFFFFF"
OLD_ORANGE = "#ec752a"

BRANDS = {
    "ClimbUK": "vc_climbuk.svg",
    "ClimbGroup": "vc_climbgroup.svg",
    "Climb27": "vc_climb27.svg",
}
STACKED = {"ClimbGroup": "vc_climbgroup_stacked.svg"}


def lum(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a, b):
    a, b = sorted([lum(a), lum(b)])
    return (b + 0.05) / (a + 0.05)


def load(fn):
    """Return (viewBox w,h, [(d, role)]) where role is 'climb' (orange) or 'suffix'."""
    t = etree.parse(os.path.join(S, fn))
    root = t.getroot()
    w, h = (float(v) for v in root.get("viewBox").split()[2:])
    paths = []
    for p in root.iter("{%s}path" % NS):
        fill = (p.get("fill") or "").lower()
        if fill in ("", "none"):
            continue
        paths.append((p.get("d"), "climb" if fill == OLD_ORANGE else "suffix"))
    return w, h, paths


def svg_doc(vb, body, extra=""):
    x, y, w, h = vb
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x:.2f} {y:.2f} {w:.2f} {h:.2f}" '
            f'width="{w:.2f}" height="{h:.2f}" fill-rule="nonzero">{extra}{body}</svg>\n')


def group(paths, role, colour, transform=""):
    ds = "".join(f'<path d="{d}"/>' for d, r in paths if role in (None, r))
    tf = f' transform="{transform}"' if transform else ""
    return f'<g fill="{colour}"{tf}>{ds}</g>'


def bbox(paths, w, h, role=None):
    """Pixel-accurate bbox in viewBox units by rasterising."""
    scale = 6000 / max(w, h)
    doc = svg_doc((0, 0, w, h), group(paths, role, "#000"))
    png = subprocess.run(["rsvg-convert", "-z", str(scale)], input=doc.encode(),
                         capture_output=True, check=True).stdout
    im = Image.open(io.BytesIO(png)).getchannel("A")
    x0, y0, x1, y1 = im.getbbox()
    return x0 / scale, y0 / scale, (x1 - x0) / scale, (y1 - y0) / scale


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    assert not os.path.exists(path) or path.startswith(OUT), path
    with open(path, "w") as f:
        f.write(text)


def png_exports(svg_path, pngdir, stem):
    os.makedirs(pngdir, exist_ok=True)
    for wpx in (512, 1024, 2048):
        subprocess.run(["rsvg-convert", "-w", str(wpx), svg_path, "-o",
                        os.path.join(pngdir, f"{stem}_{wpx}.png")], check=True)


# The three solid grounds every logo, icon and tile also comes on. Transparent is the default; these are for
# places that need a filled square or rectangle (app stores, slides, platforms that flatten transparency).
GROUNDS = {"white": WHITE, "ground": BROWN, "orange": ORANGE}

VARIANTS = [
    # key, label, kind, climb colour, suffix colour, intended background, solid ground (None = transparent)
    ("full-colour-light", "Full colour (light)", "word", ORANGE, CHAR, WHITE, None),
    ("reversed-dark", "Reversed (dark-first)", "word", ORANGE, WHITE, BROWN, None),
    ("mono-dark", "Mono dark", "word", CHAR, CHAR, WHITE, None),
    ("mono-white", "Mono white", "word", WHITE, WHITE, BROWN, None),
    ("icon", "Square icon", "icon", ORANGE, CHAR, WHITE, None),
    ("icon-reversed", "Square icon reversed", "icon", ORANGE, WHITE, BROWN, None),
    ("full-colour-grey", "Full colour (Light Grey)", "word", ORANGE_GREY, CHAR, GREY, None),
    ("icon-monogram", "Monogram icon (under 64px)", "monogram", ORANGE, ORANGE, None, None),
    ("tagline-lockup", "Tagline lockup", "tagline", ORANGE, CHAR, WHITE, None),
    ("tagline-lockup-reversed", "Tagline lockup reversed", "tagline", ORANGE, WHITE, BROWN, None),
    # Solid grounds: full colour on White, reversed on Dark Brown, one-colour white on Climb Orange.
    ("logo-on-white", "Logo on White", "word", ORANGE, CHAR, WHITE, WHITE),
    ("logo-on-ground", "Logo on Dark Brown", "word", ORANGE, WHITE, BROWN, BROWN),
    ("logo-on-orange", "Logo on Climb Orange", "word", WHITE, WHITE, ORANGE, ORANGE),
    ("tagline-lockup-on-white", "Tagline lockup on White", "tagline", ORANGE, CHAR, WHITE, WHITE),
    ("tagline-lockup-on-ground", "Tagline lockup on Dark Brown", "tagline", ORANGE, WHITE, BROWN, BROWN),
    ("tagline-lockup-on-orange", "Tagline lockup on Climb Orange", "tagline", WHITE, WHITE, ORANGE, ORANGE),
    ("icon-on-white", "Square icon on White", "icon", ORANGE, CHAR, WHITE, WHITE),
    ("icon-on-ground", "Square icon on Dark Brown", "icon", ORANGE, WHITE, BROWN, BROWN),
    ("icon-on-orange", "Square icon on Climb Orange", "icon", WHITE, WHITE, ORANGE, ORANGE),
    ("icon-monogram-on-white", "Monogram on White", "monogram", ORANGE, ORANGE, WHITE, WHITE),
    ("icon-monogram-on-ground", "Monogram on Dark Brown", "monogram", ORANGE, ORANGE, BROWN, BROWN),
    ("icon-monogram-on-orange", "Monogram on Climb Orange", "monogram", WHITE, WHITE, ORANGE, ORANGE),
]
TAGLINE = "The Festival for Business Growth"


def rect(w, h, ground, x=0, y=0):
    return f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{ground}"/>' if ground else ""


def c_height(paths, w, h):
    """Height of the large C in Climb (the leftmost orange shape): the clear space on every edge."""
    climb = [p for p in paths if p[1] == "climb"]
    first = min(path_bboxes(climb, w, h), key=lambda b: b[0])
    return first[3]


def on_ground(vb, body, clear, ground):
    """Grow the view box by the clear space on every edge and fill it with the ground."""
    x, y, bw, bh = vb
    nvb = (x - clear, y - clear, bw + 2 * clear, bh + 2 * clear)
    return nvb, rect(nvb[2], nvb[3], ground, nvb[0], nvb[1]) + body


def path_bboxes(paths, w, h):
    return [bbox([p], w, h) for p in paths]


def build_monogram(w, h, paths, colour=ORANGE, ground=None):
    """The shared li mark (the 'l' and the stencilled 'i' of Climb): orange on a transparent square by default,
    or on a solid ground."""
    climb = [p for p in paths if p[1] == "climb"]
    cb = bbox(climb, w, h)
    picked = [p for p, b in zip(climb, path_bboxes(climb, w, h))
              if 0.2 <= (b[0] - cb[0]) / cb[2] <= 0.45]
    assert len(picked) == 4, len(picked)  # l + three pieces of the i
    mb = bbox(picked, w, h)
    size = 1000
    k = size * 0.70 / mb[3]
    tx = (size - mb[2] * k) / 2 - mb[0] * k
    ty = (size - mb[3] * k) / 2 - mb[1] * k
    body = (rect(size, size, ground)
            + group(picked, None, colour, f"translate({tx:.2f} {ty:.2f}) scale({k:.5f})"))
    return svg_doc((0, 0, size, size), body, "<title>Climb li monogram</title>")


def build_tagline(brand, w, h, paths, c1, c2, label, ground=None):
    """Wordmark with the tagline set in Montserrat Bold (outlined) beneath, matched to the wordmark width."""
    from textpath import text_path
    allb = bbox(paths, w, h)
    cb = bbox(paths, w, h, "climb")
    # the registered mark is the small suffix shape at the top right; keep it out of the width
    word = [p for p, b in zip(paths, path_bboxes(paths, w, h))
            if not (p[1] == "suffix" and b[3] < 0.3 * allb[3] and b[0] > allb[0] + 0.85 * allb[2])]
    wb = bbox(word, w, h)
    d, tw, cap = text_path(TAGLINE)
    k = wb[2] / tw
    gap = cb[3] * 0.16
    base = allb[1] + allb[3] + gap + cap * k
    tag = f'<path fill="{c2}" transform="translate({wb[0]:.2f} {base:.2f}) scale({k:.5f})" d="{d}"/>'
    full_h = base + 0.25 * cap * k  # room for descenders (g, w baseline)
    x0, y0 = allb[0], allb[1]
    vb = (x0, y0, allb[2], full_h - y0)
    body = group(paths, "climb", c1) + group(paths, "suffix", c2) + tag
    if ground:
        vb, body = on_ground(vb, body, c_height(paths, w, h), ground)
    return svg_doc(vb, body, f"<title>{brand} logo with tagline, {label}</title>")


def without_reg(paths, w, h):
    """The paths minus the registered mark: the small suffix shape, well under a third of the letter height.
    Icons centre on this, so the mark hangs outside the optical centre instead of pulling the word off it."""
    bs = path_bboxes(paths, w, h)
    tall = max(b[3] for p, b in zip(paths, bs) if p[1] == "suffix")
    return [p for p, b in zip(paths, bs) if not (p[1] == "suffix" and b[3] < 0.3 * tall and b[2] < 0.3 * tall)]


def build_icon(brand, w, h, paths, c1=ORANGE, c2=WHITE, ground=None):
    """Square icon, stacked 'Climb' over suffix, centred and drawn without the registered mark. Transparent by
    default, or on a solid ground."""
    if brand in STACKED:
        sw, sh, sp = load(STACKED[brand])
        sp = without_reg(sp, sw, sh)
        cb = bbox(sp, sw, sh, "climb")
        xb = bbox(sp, sw, sh, "suffix")
        src_paths, (cx, cy, cw, ch), (sx, sy, sw_, sh_) = sp, cb, xb
        # stacked source already laid out: treat as one block
        allb = bbox(without_reg(sp, sw, sh), sw, sh)
        size = 1000
        target_w = size * 0.72
        k = target_w / allb[2]
        if allb[3] * k > size * 0.72:
            k = size * 0.72 / allb[3]
        tx = (size - allb[2] * k) / 2 - allb[0] * k
        ty = (size - allb[3] * k) / 2 - allb[1] * k
        tf = f"translate({tx:.2f} {ty:.2f}) scale({k:.5f})"
        body = rect(size, size, ground) + group(sp, "climb", c1, tf) + group(sp, "suffix", c2, tf)
        return svg_doc((0, 0, size, size), body)
    paths = without_reg(paths, w, h)
    cb = bbox(paths, w, h, "climb")
    xb = bbox(paths, w, h, "suffix")
    size = 1000
    k = size * 0.72 / cb[2]
    gap = cb[3] * 0.10
    total_h = (cb[3] + gap + xb[3]) * k
    top = (size - total_h) / 2
    c_tx = (size - cb[2] * k) / 2 - cb[0] * k
    c_ty = top - cb[1] * k
    s_tx = (size - xb[2] * k) / 2 - xb[0] * k
    s_ty = top + (cb[3] + gap) * k - xb[1] * k
    body = (rect(size, size, ground)
            + group(paths, "climb", c1, f"translate({c_tx:.2f} {c_ty:.2f}) scale({k:.5f})")
            + group(paths, "suffix", c2, f"translate({s_tx:.2f} {s_ty:.2f}) scale({k:.5f})"))
    return svg_doc((0, 0, size, size), body)


def main():
    report = []
    for brand, fn in BRANDS.items():
        w, h, paths = load(fn)
        vb = bbox(paths, w, h)
        bdir = os.path.join(OUT, brand)
        files = {}
        for key, label, kind, c1, c2, bg, ground in VARIANTS:
            if kind == "icon":
                doc = build_icon(brand, w, h, paths, c1, c2, ground)
            elif kind == "monogram":
                doc = build_monogram(w, h, paths, c1, ground)
            elif kind == "tagline":
                doc = build_tagline(brand, w, h, paths, c1, c2, label, ground)
            else:
                box, body = vb, group(paths, "climb", c1) + group(paths, "suffix", c2)
                if ground:
                    box, body = on_ground(vb, body, c_height(paths, w, h), ground)
                doc = svg_doc(box, body, f"<title>{brand} logo, {label}</title>")
            p = os.path.join(bdir, f"{brand}_{key}.svg")
            write(p, doc)
            png_exports(p, os.path.join(bdir, "PNG"), f"{brand}_{key}")
            files[key] = p
        report.append((brand, files))
    return report


if __name__ == "__main__":
    for brand, files in main():
        print(brand, *files.values(), sep="\n  ")
