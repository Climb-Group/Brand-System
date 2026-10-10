"""Build the previews/ contact sheets from a rendered asset catalogue.

Usage: python3 tools/contact_sheet.py BUILD_DIR [DATE]
BUILD_DIR is the folder catalogue.py and render.mjs wrote (manifest.json and png/).
Writes previews/redesign-<group>-DATE.jpg, festival-kit-DATE.jpg and email-banners-DATE.jpg.
"""
import json
import pathlib
import sys
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
GROUND = (29, 15, 4)
INK = (232, 113, 42)
FONT = ROOT / "fonts"


def font(size):
    for p in sorted(FONT.rglob("*.ttf")):
        if "OpenSans" in p.name and "Regular" in p.name:
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def sheet(assets, png, out, width=2400, cols=3, pad=24, label=28):
    cell = (width - pad * (cols + 1)) // cols
    f = font(18)
    tiles = []
    for a in assets:
        im = Image.open(png / (a["name"] + ".png")).convert("RGB")
        im.thumbnail((cell, cell))
        tiles.append((a["name"], im))
    rows = [tiles[i:i + cols] for i in range(0, len(tiles), cols)]
    heights = [max(t[1].height for t in r) + label for r in rows]
    S = Image.new("RGB", (width, sum(heights) + pad * (len(rows) + 1)), GROUND)
    d = ImageDraw.Draw(S)
    y = pad
    for r, h in zip(rows, heights):
        for i, (name, im) in enumerate(r):
            x = pad + i * (cell + pad)
            S.paste(im, (x, y))
            d.text((x, y + im.height + 4), name, fill=INK, font=f)
        y += h + pad
    S.save(out, quality=85, optimize=True)
    print(out.relative_to(ROOT), S.size, len(assets))


def main(argv):
    build = pathlib.Path(argv[0])
    date = argv[1] if len(argv) > 1 else "2026-10-10"
    m = json.load(open(build / "manifest.json"))
    png = build / "png"
    P = ROOT / "previews"
    core = lambda g: [a for a in m if a["group"] == g and a.get("set") != "festival-kit"]
    sheet(core("Calls"), png, P / f"redesign-calls-{date}.jpg", cols=4)
    sheet([a for a in core("Wallpapers") if a["w"] == 3840], png, P / f"redesign-wallpapers-{date}.jpg", cols=4)
    sheet(core("Social"), png, P / f"redesign-social-{date}.jpg", cols=3)
    sheet(core("Print and merch") + core("Stage and screens"), png, P / f"redesign-print-and-merch-{date}.jpg", cols=4)
    sheet([a for a in m if a.get("set") == "festival-kit"], png, P / f"festival-kit-{date}.jpg", cols=4)
    sheet(core("Email banners"), png, P / f"email-banners-{date}.jpg", width=1440, cols=2)


if __name__ == "__main__":
    main(sys.argv[1:])
