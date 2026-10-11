#!/usr/bin/env python3
"""Build the app icon kit: favicons, web app icons and Microsoft 365 app launcher tiles.

    python3 app-icons/_build/build_app_icons.py

Every file comes transparent first (the default, so it sits on any platform's own background) and again on the
three solid grounds: White, Dark Brown and Climb Orange.

    app-icons/favicons/            transparent favicon.svg, favicon.ico, PNG favicons and web app icons
    app-icons/favicons/<ground>/   the same set on white, ground (Dark Brown) or orange
    app-icons/app-tiles/           transparent Microsoft 365 app launcher tiles, 60, 120 and 240 px
    app-icons/app-tiles/<ground>/  the same tiles on white, ground or orange

The favicons are the li monogram from logos/ClimbUK/ClimbUK_icon-monogram.svg (the mark is the same for every
brand). The tiles are house drawings from generators/illustrations.py plus a monogram tile. Colours come from
tokens/brand.tokens.json. Needs rsvg-convert and Pillow; the Tickets drawing carries text set in Montserrat
Bold, outlined here from logos/_build/Montserrat-Bold.ttf so no font needs installing.
"""
import io
import json
import pathlib
import re
import shutil
import subprocess
import sys

from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
KIT = HERE.parent
ROOT = KIT.parent
sys.path.insert(0, str(ROOT / "generators"))
sys.path.insert(0, str(ROOT / "logos" / "_build"))

import illustrations as I  # noqa: E402
from textpath import text_path  # noqa: E402

TOKENS = json.loads((ROOT / "tokens" / "brand.tokens.json").read_text())


def colour(name):
    return TOKENS["color"]["brand"][name]["$value"]


ORANGE, BROWN, WHITE = colour("orange"), colour("dark-brown"), colour("white")

# Ground name, fill (None = transparent), mark colour, cut-line colour for the drawings.
# On Climb Orange the mark turns white (orange on orange would vanish), as the logos do.
GROUNDS = [
    ("transparent", None, ORANGE, BROWN),
    ("white", WHITE, ORANGE, BROWN),
    ("ground", BROWN, ORANGE, BROWN),
    ("orange", ORANGE, WHITE, ORANGE),
]

# Microsoft 365 app launcher tiles: file key, drawing, tile name, description (for the README table).
TILES = [
    ("odoo", "gears", "Odoo", "Our business system: contacts, events, tickets, website and accounts."),
    ("website", "globe", "climb-uk.com", "The public website."),
    ("brand-centre", "book-open", "Brand centre", "Logos, colours, fonts, templates and the brand guidelines."),
    ("tickets", "tickets", "Tickets", "Event tickets and the box office."),
    ("media-kit", "clapperboard", "Media kit", "Photos, video, press and partner downloads."),
]
TILE_SIZES = (60, 120, 240)
FAVICON_PNG = (16, 32, 48)
APP_PNG = {"apple-touch-icon": 180, "icon-192": 192, "icon-512": 512}


def monogram_paths():
    """The four bars of the li monogram, as <path> elements in its 1000-unit square."""
    src = (ROOT / "logos" / "ClimbUK" / "ClimbUK_icon-monogram.svg").read_text()
    g = re.search(r'<g fill="[^"]+"( transform="[^"]+")>(.*?)</g>', src, re.S)
    return g.group(1), g.group(2)


def monogram_svg(size, fill, mark, scale=1.0):
    """The monogram in a size x size box. scale shrinks it about the centre (maskable icons keep it inside the
    middle 80 per cent circle)."""
    tf, paths = monogram_paths()
    inner = '<g fill="%s"%s>%s</g>' % (mark, tf, paths)
    if scale != 1.0:
        off = 500 * (1 - scale)
        inner = '<g transform="translate(%.1f %.1f) scale(%.4f)">%s</g>' % (off, off, scale, inner)
    bg = '<rect width="1000" height="1000" fill="%s"/>' % fill if fill else ""
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" width="%d" height="%d">'
            '<title>Climb li monogram</title>%s%s</svg>\n' % (size, size, bg, inner))


TEXT = re.compile(r'<text x="([\d.]+)" y="([\d.]+)" transform="(rotate\([^)]*\))" text-anchor="middle" '
                  r'(?:textLength="([\d.]+)" lengthAdjust="spacingAndGlyphs" )?style="[^"]*font-size:([\d.]+)px;'
                  r'[^"]*fill:([^;]+);[^"]*">([^<]*)</text>')


def outline_text(body):
    """Swap each drawing label for its outline, so the tile looks the same without the font installed."""
    def repl(m):
        x, y, rot, length, size, fill, value = m.groups()
        d, tw, _ = text_path(value)
        ky = float(size) / 1000
        kx = float(length) / tw if length else ky
        return ('<g transform="%s"><path fill="%s" transform="translate(%.2f %s) scale(%.5f %.5f)" d="%s"/></g>'
                % (rot, fill, float(x) - tw * kx / 2, y, kx, ky, d))
    return TEXT.sub(repl, body)


# Below 64 px an anti-aliased render blurs the two 3.5 per cent gaps in the i, so the small favicons are drawn
# on whole pixels instead: the l and the three pieces of the i, inclusive pixel boxes.
PIXEL_BARS = {
    16: [(5, 2, 6, 13), (9, 2, 10, 4), (9, 6, 10, 11), (9, 13, 10, 13)],
    32: [(8, 4, 13, 27), (17, 4, 22, 10), (17, 13, 22, 23), (17, 26, 22, 27)],
    48: [(15, 7, 22, 40), (26, 7, 33, 16), (26, 19, 33, 35), (26, 38, 33, 40)],
}


def pixel_monogram(size, fill, mark):
    from PIL import ImageDraw
    img = Image.new("RGBA", (size, size), fill or (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for box in PIXEL_BARS[size]:
        draw.rectangle(box, fill=mark)
    return img


def drawing_svg(drawing, size, fill, ink, ground):
    """A house drawing centred on a size x size tile, at 78 per cent of the tile like the existing tiles. Lines
    are drawn heavier at small sizes so they hold up at 60 px."""
    weight = 2.4 if size <= 64 else (1.6 if size <= 200 else 1.2)
    body = I.inner(drawing, weight=weight)
    body = body.replace("currentColor", ink).replace("var(--doodle-ground,%s)" % I.GROUND, ground)
    body = outline_text(body)
    assert "<text" not in body, drawing
    d = 200 / 0.78
    off = (d - 200) / 2
    bg = '<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="%s"/>' % (-off, -off, d, d, fill) if fill else ""
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%.2f %.2f %.2f %.2f" width="%d" height="%d">%s%s</svg>\n'
            % (-off, -off, d, d, size, size, bg, body))


def render(svg, size):
    png = subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size)], input=svg.encode(),
                         capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(png)).convert("RGBA")


def save_png(img, path, opaque):
    path.parent.mkdir(parents=True, exist_ok=True)
    if opaque:
        img = img.convert("RGB")
    img.save(path, optimize=True)


def folder(base, ground):
    return base if ground == "transparent" else base / ground


def build_favicons(out):
    written = []
    for ground, fill, mark, _ in GROUNDS:
        d = folder(out / "favicons", ground)
        d.mkdir(parents=True, exist_ok=True)
        svg = monogram_svg(1000, fill, mark)
        (d / "favicon.svg").write_text(svg)
        written.append(d / "favicon.svg")
        small = {s: pixel_monogram(s, fill, mark) for s in FAVICON_PNG}
        for s, img in small.items():
            p = d / ("favicon-%dx%d.png" % (s, s))
            save_png(img, p, fill is not None)
            written.append(p)
        small[48].save(d / "favicon.ico", sizes=[(s, s) for s in FAVICON_PNG],
                       append_images=[small[16], small[32]])
        written.append(d / "favicon.ico")
        for name, s in APP_PNG.items():
            p = d / ("%s-%dx%d.png" % (name, s, s) if name == "apple-touch-icon" else "%s.png" % name)
            save_png(render(monogram_svg(s, fill, mark), s), p, fill is not None)
            written.append(p)
        if fill:  # maskable icons are always filled: Android crops them to its own shape
            p = d / "icon-maskable-512.png"
            save_png(render(monogram_svg(512, fill, mark, scale=0.72), 512), p, True)
            written.append(p)
    return written


def build_tiles(out):
    written = []
    for ground, fill, ink, cut in GROUNDS:
        d = folder(out / "app-tiles", ground)
        for key, drawing, _, _ in TILES:
            for s in TILE_SIZES:
                p = d / ("%s_%dx%d.png" % (key, s, s))
                save_png(render(drawing_svg(drawing, s, fill, ink, cut), s), p, fill is not None)
                written.append(p)
        for s in TILE_SIZES:  # the plain monogram tile, mark at 90 per cent of the master's size
            p = d / ("climb_%dx%d.png" % (s, s))
            save_png(render(monogram_svg(s, fill, ink, scale=0.9), s), p, fill is not None)
            written.append(p)
    return written


def contact_sheet(out):
    """Every tile at 120 px on its own ground, transparent ones shown on white and on Dark Brown."""
    keys = [t[0] for t in TILES] + ["climb"]
    rows = [("transparent", WHITE), ("transparent", BROWN), ("white", None), ("ground", None), ("orange", None)]
    cell, pad = 120, 16
    sheet = Image.new("RGB", (pad + len(keys) * (cell + pad), pad + len(rows) * (cell + pad)), "#BDBDBD")
    for r, (ground, under) in enumerate(rows):
        for c, key in enumerate(keys):
            tile = Image.open(folder(out / "app-tiles", ground) / ("%s_120x120.png" % key)).convert("RGBA")
            x, y = pad + c * (cell + pad), pad + r * (cell + pad)
            if under:
                sheet.paste(under, (x, y, x + cell, y + cell))
            sheet.paste(tile, (x, y), tile)
    p = out / "app-tiles_contact-sheet.png"
    sheet.save(p, optimize=True)
    return p


def main():
    for sub in ("favicons", "app-tiles"):
        if (KIT / sub).exists():
            shutil.rmtree(KIT / sub)
    files = build_favicons(KIT) + build_tiles(KIT)
    files.append(contact_sheet(KIT))
    print("[app-icons] %d files in %s" % (len(files), KIT.relative_to(ROOT)))


if __name__ == "__main__":
    main()
