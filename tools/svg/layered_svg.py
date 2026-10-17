"""Finish a layered SVG written by layered_svg.js, so it opens and edits well in Inkscape and Affinity.

    python3 tools/svg/layered_svg.py RAW.svg OUT.svg      # usually called from a build, through finish()

- Photos from the pack are linked, not embedded: the image is placed full size behind a clip the size of the
  frame, so moving it in an editor changes the crop, and each fade the build burnt in becomes an editable
  gradient rectangle above it. The photo folder must sit where the link points (the pack's photos/ folder).
- Any other image the build generated (glows, stage light, textures) is embedded, scaled to at most 1600px.
- Text stays live text in Montserrat and Open Sans; install them from fonts/ttf before editing.

Standard library plus Pillow (already a build dependency of the print pieces).
"""
import base64
import io
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

from PIL import Image

IMAGE = re.compile(r"<image ([^>]*?)/>")
ATTR = re.compile(r'([\w:-]+)=(?:"([^"]*)"|\'([^\']*)\')')
EMBED_MAX = 1600


def _attrs(s):
    return {m.group(1): m.group(2) if m.group(2) is not None else m.group(3) for m in ATTR.finditer(s)}


def _path(href):
    return Path(unquote(urlparse(href).path))


def _smooth(t):
    return t * t * (3 - 2 * t)


def _fade(gid, fade, x, y, w, h):
    axis, s, e, rgb, a0, a1 = fade
    colour = "rgb(%d,%d,%d)" % tuple(rgb)
    stops = [(0.0, a0)] + [(s + (e - s) * k / 8, a0 + (a1 - a0) * _smooth(k / 8)) for k in range(9)] + [(1.0, a1)]
    stops = "".join('<stop offset="%.4f" stop-color="%s" stop-opacity="%.4f"/>' % (min(max(o, 0), 1), colour, a)
                    for o, a in stops)
    x2, y2 = ("1", "0") if axis == "x" else ("0", "1")
    grad = '<linearGradient id="%s" x1="0" y1="0" x2="%s" y2="%s">%s</linearGradient>' % (gid, x2, y2, stops)
    rect = '<rect x="%s" y="%s" width="%s" height="%s" fill="url(#%s)"/>' % (x, y, w, h, gid)
    return grad, rect


def finish(raw, out, pack):
    """Rewrite the raw SVG text from layered_svg.js and write it to out. Returns the final text."""
    out, pack = Path(out), Path(pack)
    defs, count = [], [0]

    def image(m):
        a = _attrs(m.group(1))
        x, y, w, h = (float(a[k]) for k in ("x", "y", "width", "height"))
        clip = a.get("clip-path")
        src = _path(a["href"])
        if "data-photo" in a:
            meta = json.loads(a["data-photo"])
            sw, sh = meta["size"]
            x0, y0, cw, ch = meta["crop"]
            scale = w / cw
            if not clip:
                count[0] += 1
                defs.append('<clipPath id="frame-%d"><rect x="%s" y="%s" width="%s" height="%s"/></clipPath>' % (count[0], x, y, w, h))
                clip = "url(#frame-%d)" % count[0]
            href = os.path.relpath(pack / meta["photo"], out.parent).replace(os.sep, "/")
            parts = ['<image href="%s" x="%.3f" y="%.3f" width="%.3f" height="%.3f" preserveAspectRatio="none">'
                     '<title>%s</title></image>' % (href, x - x0 * scale, y - y0 * scale, sw * scale, sh * scale, meta["photo"])]
            for i, f in enumerate(meta.get("fade") or []):
                count[0] += 1
                grad, rect = _fade("fade-%d" % count[0], f, x, y, w, h)
                defs.append(grad)
                parts.append(rect)
            return '<g clip-path="%s">%s</g>' % (clip, "".join(parts))
        im = Image.open(src)
        im.thumbnail((EMBED_MAX, EMBED_MAX))
        buf = io.BytesIO()
        kind = "png" if im.mode in ("RGBA", "LA") else "jpeg"
        im.convert("RGBA" if kind == "png" else "RGB").save(buf, kind.upper(), quality=88)
        data = "data:image/%s;base64,%s" % (kind, base64.b64encode(buf.getvalue()).decode())
        cp = ' clip-path="%s"' % clip if clip else ""
        return '<image href="%s" x="%s" y="%s" width="%s" height="%s" preserveAspectRatio="none"%s/>' % (
            data, a["x"], a["y"], a["width"], a["height"], cp)

    text = IMAGE.sub(image, raw)
    text = text.replace("<defs>", "<defs>" + "".join(defs), 1)
    if "file://" in text:
        raise ValueError("%s still points at a build file: %s" % (out, re.search(r"file://[^\"']*", text).group(0)))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return text


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    finish(Path(sys.argv[1]).read_text(encoding="utf-8"), sys.argv[2], Path(__file__).resolve().parents[2])
