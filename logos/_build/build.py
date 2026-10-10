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


VARIANTS = [
    # key, label, climb colour, suffix colour, intended background
    ("full-colour-light", "Full colour (light)", ORANGE, CHAR, WHITE),
    ("reversed-dark", "Reversed (dark-first)", ORANGE, WHITE, BROWN),
    ("mono-dark", "Mono dark", CHAR, CHAR, WHITE),
    ("mono-white", "Mono white", WHITE, WHITE, BROWN),
    ("icon", "Square icon", None, None, None),
    ("full-colour-grey", "Full colour (Light Grey)", ORANGE_GREY, CHAR, GREY),
    ("icon-monogram", "Monogram icon (under 64px)", None, None, None),
    ("tagline-lockup", "Tagline lockup", ORANGE, CHAR, WHITE),
    ("tagline-lockup-reversed", "Tagline lockup reversed", ORANGE, WHITE, BROWN),
]
TAGLINE = "The Festival for Business Growth"


def path_bboxes(paths, w, h):
    return [bbox([p], w, h) for p in paths]


def build_monogram(w, h, paths):
    """The shared l! mark (the 'l' and the stencilled 'i' of Climb), orange on a Dark Brown tile."""
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
    body = (f'<rect width="{size}" height="{size}" fill="{BROWN}"/>'
            + group(picked, None, ORANGE, f"translate({tx:.2f} {ty:.2f}) scale({k:.5f})"))
    return svg_doc((0, 0, size, size), body, "<title>Climb l! monogram</title>")


def build_tagline(brand, w, h, paths, c1, c2, label):
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
    return svg_doc(vb, group(paths, "climb", c1) + group(paths, "suffix", c2) + tag,
                   f"<title>{brand} logo with tagline, {label}</title>")


def without_reg(paths, w, h):
    """The paths minus the registered mark: the small suffix shape, well under a third of the letter height.
    Icons centre on this, so the mark hangs outside the optical centre instead of pulling the word off it."""
    bs = path_bboxes(paths, w, h)
    tall = max(b[3] for p, b in zip(paths, bs) if p[1] == "suffix")
    return [p for p, b in zip(paths, bs) if not (p[1] == "suffix" and b[3] < 0.3 * tall and b[2] < 0.3 * tall)]


def build_icon(brand, w, h, paths):
    """Square tile, Dark Brown, stacked 'Climb' over suffix, centred and drawn without the registered mark."""
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
        body = (f'<rect width="{size}" height="{size}" fill="{BROWN}"/>'
                + group(sp, "climb", ORANGE, tf) + group(sp, "suffix", WHITE, tf))
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
    body = (f'<rect width="{size}" height="{size}" fill="{BROWN}"/>'
            + group(paths, "climb", ORANGE, f"translate({c_tx:.2f} {c_ty:.2f}) scale({k:.5f})")
            + group(paths, "suffix", WHITE, f"translate({s_tx:.2f} {s_ty:.2f}) scale({k:.5f})"))
    return svg_doc((0, 0, size, size), body)


def main():
    report = []
    for brand, fn in BRANDS.items():
        w, h, paths = load(fn)
        vb = bbox(paths, w, h)
        bdir = os.path.join(OUT, brand)
        files = {}
        for key, label, c1, c2, bg in VARIANTS:
            if key == "icon":
                doc = build_icon(brand, w, h, paths)
            elif key == "icon-monogram":
                doc = build_monogram(w, h, paths)
            elif key.startswith("tagline"):
                doc = build_tagline(brand, w, h, paths, c1, c2, label)
            else:
                doc = svg_doc(vb, group(paths, "climb", c1) + group(paths, "suffix", c2),
                              f"<title>{brand} logo, {label}</title>")
            p = os.path.join(bdir, f"{brand}_{key}.svg")
            write(p, doc)
            png_exports(p, os.path.join(bdir, "PNG"), f"{brand}_{key}")
            files[key] = p
        report.append((brand, files))
    return report


if __name__ == "__main__":
    for brand, files in main():
        print(brand, *files.values(), sep="\n  ")
