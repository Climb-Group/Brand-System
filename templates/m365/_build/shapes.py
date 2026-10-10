"""Festival shape layouts for the Teams meeting backgrounds: soft blobs in Climb Orange, Charcoal and a ground tone,
with hand-cut marks (dots, dashes, heat lines, tiles, targets, pills) scattered over them, in the spirit of the
Climb26 call backgrounds. Photos and house drawings sit on top as accents only.

Each layout lists its blobs in 1920x1080 units (drawn at 3840x2160). The module keeps a low resolution colour map
of the blobs so every mark and the logo can pick the colour that reads on whatever is under it, and so the build
can check that the middle of the frame, where the person sits, stays calm.
"""
import math
import random

from PIL import Image, ImageDraw

DB, CH, OR, LG, WH = "#1E0F05", "#242322", "#E8712A", "#E9E9E9", "#FFFFFF"
# The ground tone: White at 12 percent over Charcoal (a tone of the ground, as the visual style allows). TONE is
# only the colour map key for it; the drawing uses Charcoal plus TONE_CSS.
TONE = "#3E3D3C"
TONE_CSS = "rgba(255,255,255,.12)"
K = 2          # 1920x1080 layout units to 3840x2160 pixels
MAP = 8        # colour map is 1/8 of the layout size

# What reads on each colour: (mark colour, logo variant).
ON = {
    OR: (CH, "mono-white"),
    CH: (OR, "reversed-dark"),
    TONE: (OR, "reversed-dark"),
    DB: (OR, "reversed-dark"),
    WH: (OR, "full-colour-light"),
}


def blob_points(cx, cy, rx, ry, seed, n=8, wobble=0.22, rot=0.0):
    """Points round a soft, lobed outline: the radius follows two slow waves plus a little jitter, so the shapes
    flow like the Climb26 blobs rather than reading as ellipses. n sets the base point count."""
    rnd = random.Random(seed)
    n = max(n, 14)
    p2, p3 = rnd.uniform(0, 2 * math.pi), rnd.uniform(0, 2 * math.pi)
    w2, w3 = wobble * rnd.uniform(0.8, 1.3), wobble * rnd.uniform(0.4, 0.9)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        r = 1 + w2 * math.sin(2 * a + p2) + w3 * math.sin(3 * a + p3) + rnd.uniform(-0.04, 0.04)
        x, y = math.cos(a) * rx * r, math.sin(a) * ry * r
        c, s = math.cos(rot), math.sin(rot)
        pts.append((cx + x * c - y * s, cy + x * s + y * c))
    return pts


def _beziers(pts):
    """Closed Catmull-Rom spline through pts as cubic Bezier segments."""
    n = len(pts)
    segs = []
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        segs.append((p1, c1, c2, p2))
    return segs


def blob_path(pts):
    segs = _beziers(pts)
    d = ["M%.0f %.0f" % (segs[0][0][0] * K, segs[0][0][1] * K)]
    for _, c1, c2, p2 in segs:
        d.append("C%.0f %.0f %.0f %.0f %.0f %.0f" % (c1[0] * K, c1[1] * K, c2[0] * K, c2[1] * K, p2[0] * K, p2[1] * K))
    return " ".join(d) + "Z"


def blob_poly(pts, steps=12):
    out = []
    for p1, c1, c2, p2 in _beziers(pts):
        for k in range(steps):
            t = k / steps
            a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t ** 2, t ** 3
            out.append((a * p1[0] + b * c1[0] + c * c2[0] + d * p2[0], a * p1[1] + b * c1[1] + c * c2[1] + d * p2[1]))
    return out


class Field:
    """Blobs drawn in order over a ground, with a colour map for picking contrast."""

    def __init__(self, ground, seed):
        self.ground, self.seed = ground, seed
        self.svg = []
        self.map = Image.new("RGB", (1920 // MAP, 1080 // MAP), ground)
        self.draw = ImageDraw.Draw(self.map)

    def blob(self, colour, cx, cy, rx, ry, n=8, wobble=0.3, rot=0.0, k=0):
        pts = blob_points(cx, cy, rx, ry, self.seed * 31 + k, n, wobble, rot)
        d = blob_path(pts)
        if colour == TONE:
            # Opaque tone: Charcoal with White at 12 percent on top, so it covers what is under it.
            self.svg.append('<path d="%s" fill="%s"/><path d="%s" fill="%s"/>' % (d, CH, d, TONE_CSS))
        else:
            self.svg.append('<path d="%s" fill="%s"/>' % (d, colour))
        self.draw.polygon([(x / MAP, y / MAP) for x, y in blob_poly(pts)], fill=colour)

    def band(self, colour, d_layout, poly):
        """Any other filled shape: an SVG path in layout units and a matching polygon for the colour map."""
        self.svg.append('<path d="%s" fill="%s" transform="scale(%d)"/>' % (d_layout, colour, K))
        self.draw.polygon([(x / MAP, y / MAP) for x, y in poly], fill=colour)

    def under(self, x, y):
        px = self.map.getpixel((min(max(int(x / MAP), 0), self.map.width - 1),
                                min(max(int(y / MAP), 0), self.map.height - 1)))
        return "#%02X%02X%02X" % px

    def uniform(self, x0, y0, x1, y1):
        """The one colour under a box, or None when it is mixed."""
        box = self.map.crop((int(x0 / MAP), int(y0 / MAP), int(x1 / MAP) + 1, int(y1 / MAP) + 1))
        cols = box.getcolors(4096)
        if len(cols) == 1:
            return "#%02X%02X%02X" % cols[0][1]
        return None

    def calm_share(self, x0, y0, x1, y1, colour):
        box = self.map.crop((int(x0 / MAP), int(y0 / MAP), int(x1 / MAP), int(y1 / MAP)))
        hexes = {("#%02X%02X%02X" % c): n for n, c in box.getcolors(4096)}
        return hexes.get(colour, 0) / float(box.width * box.height)

    def body(self):
        return "".join(self.svg)


def mark_colour(field, x, y):
    return ON.get(field.under(x, y), (OR, None))[0]


# ---------------------------------------------------------------- marks, in layout units, centred on (x, y)

def _g(x, y, rot, body):
    return '<g transform="translate(%.0f %.0f) rotate(%.0f) scale(%d)">%s</g>' % (x * K, y * K, rot, K, body)


def dots(x, y, c, rot=-25, s=1.0):
    return _g(x, y, rot, "".join('<ellipse cx="%.0f" cy="0" rx="%.1f" ry="%.1f" fill="%s"/>' % (i * 62 * s, 23 * s, 19 * s, c)
                                 for i in (-1, 0, 1)))


def dashes(x, y, c, rot=0, s=1.0):
    out = []
    for i in range(5):
        a = math.radians(-140 + i * 25)
        a2 = a + math.radians(15)
        r = 150 * s
        out.append('<path d="M%.0f %.0f A%.0f %.0f 0 0 1 %.0f %.0f" stroke="%s" stroke-width="%.0f" fill="none" stroke-linecap="round"/>'
                   % (r * math.cos(a), r * math.sin(a) + r, r, r, r * math.cos(a2), r * math.sin(a2) + r, c, 15 * s))
    return _g(x, y, rot, "".join(out))


def heat(x, y, c, rot=0, s=1.0):
    out = []
    for i in (-1, 0, 1):
        dx = i * 70 * s
        out.append('<path d="M%.0f %.0f c-24 -20 -24 -40 0 -58 c24 -18 24 -38 0 -58" transform="translate(%.0f 0)" '
                   'stroke="%s" stroke-width="%.0f" fill="none" stroke-linecap="round"/>' % (0, 58 * s, dx, c, 18 * s))
    return _g(x, y, rot, "".join(out))


def tile(x, y, c, rot=0, s=1.0):
    return _g(x, y, rot, '<rect x="%.0f" y="%.0f" width="%.0f" height="%.0f" rx="%.0f" fill="%s"/>'
              % (-70 * s, -65 * s, 140 * s, 130 * s, 12 * s, c))


def bricks(x, y, c, rot=0, s=1.0):
    r = ['<rect x="%.0f" y="%.0f" width="%.0f" height="%.0f" rx="%.0f" fill="%s"/>' % (bx * s, by * s, 92 * s, 58 * s, 10 * s, c)
         for bx, by in ((-110, -62), (15, -62), (-45, 18))]
    return _g(x, y, rot, "".join(r))


def target(x, y, c, rot=0, s=1.0):
    b = ('<circle r="%.0f" fill="none" stroke="%s" stroke-width="%.0f"/><circle r="%.0f" fill="%s"/>'
         % (52 * s, c, 18 * s, 20 * s, c))
    for q in range(4):
        b += ('<path d="M%.0f %.0f A%.0f %.0f 0 0 1 %.0f %.0f" transform="rotate(%d)" stroke="%s" stroke-width="%.0f" '
              'fill="none"/>' % (-58 * s, -62 * s, 86 * s, 86 * s, 58 * s, -62 * s, q * 90, c, 14 * s))
    return _g(x, y, rot, b)


def cross(x, y, c, rot=0, s=1.0):
    return _g(x, y, rot, '<path d="M%.0f %.0f L%.0f %.0f M%.0f %.0f L%.0f %.0f" stroke="%s" stroke-width="%.0f" '
              'stroke-linecap="round"/>' % (-60 * s, -55 * s, 60 * s, 55 * s, 60 * s, -55 * s, -60 * s, 55 * s, c, 30 * s))


def smile(x, y, c, rot=0, s=1.0):
    return _g(x, y, rot, '<path d="M%.0f %.0f Q%.0f %.0f %.0f %.0f" stroke="%s" stroke-width="%.0f" fill="none" '
              'stroke-linecap="round"/>' % (-150 * s, 0, -20 * s, 140 * s, 110 * s, -60 * s, c, 34 * s))


def pills(x, y, c, rot=-30, s=1.0):
    r = ['<rect x="%.0f" y="%.0f" width="%.0f" height="%.0f" rx="%.0f" fill="%s"/>' % (-75 * s, oy * s, 150 * s, 36 * s, 6 * s, c)
         for oy in (-50, 14)]
    return _g(x, y, rot, "".join(r))


def drop(x, y, c, rot=0, s=1.0):
    """A speech-bubble drop: a disc with one square corner."""
    r = 55 * s
    return _g(x, y, rot, '<path d="M0 %.0f A%.0f %.0f 0 1 1 %.0f 0 L%.0f %.0f Z" fill="%s"/>' % (-r, r, r, -r, -r, -r, c))


MARKS = dict(dots=dots, dashes=dashes, heat=heat, tile=tile, bricks=bricks, target=target, cross=cross, smile=smile,
             pills=pills, drop=drop)


def marks(field, spec):
    """spec: (name, x, y, rot, size[, colour]). Colour defaults to whatever reads on the blob under the mark;
    pills are Light Grey on dark grounds, the way the Climb26 set used cream."""
    out = []
    for item in spec:
        name, x, y, rot, s = item[:5]
        c = item[5] if len(item) > 5 else mark_colour(field, x, y)
        if name == "pills" and len(item) <= 5 and field.under(x, y) in (CH, TONE, DB):
            c = LG
        out.append(MARKS[name](x, y, c, rot, s))
    return "".join(out)


# ---------------------------------------------------------------- layouts
# Person zone: the middle 900x700 of the 1920x1080 frame (x 510 to 1410, y 190 to 890) stays one calm colour.
# Logo zone: top left, x 60 to 420, y 50 to 150 (layout units).

PERSON = (510, 190, 1410, 890)
LOGO = (50, 40, 430, 160)


def funky(seed, ground=CH):
    """The Funky set: Charcoal with orange and tone blobs crowding the edges and a tone blob behind the person."""
    f = Field(ground, seed)
    f.blob(TONE, 330, 1000, 300, 200, k=1)
    f.blob(TONE, 1780, 980, 260, 160, k=2)
    f.blob(OR, -40, 600, 300, 300, k=3)
    f.blob(OR, 1780, 260, 360, 320, k=4, rot=0.4)
    f.blob(OR, 1480, 1040, 340, 160, k=5)
    f.blob(OR, 760, 1080, 260, 140, k=6)
    f.blob(OR, 980, -40, 320, 130, k=7)
    f.blob(TONE, 960, 540, 600, 400, wobble=0.14, k=8)
    m = [("dots", 140, 330, -25, 1.0), ("dashes", 980, 40, 0, 1.0), ("heat", 1560, 80, 0, 1.0),
         ("pills", 1690, 640, -30, 1.0), ("tile", 1820, 520, 0, 1.0), ("target", 1700, 920, 0, 1.0),
         ("bricks", 820, 1010, 0, 0.9), ("tile", 230, 880, 0, 0.9), ("cross", 120, 640, 10, 0.8),
         ("smile", 1300, 1010, -10, 0.8)]
    return f, m


def wavy(seed):
    """The Wavy set: big soft corners, orange top right and bottom left, Charcoal the other two, on the tone."""
    f = Field(TONE, seed)
    f.blob(OR, 120, 1020, 520, 330, k=1, rot=-0.2)
    f.blob(OR, 1860, -40, 520, 360, k=2, rot=0.3)
    f.blob(CH, 1900, 940, 420, 420, k=3)
    f.blob(CH, 380, 40, 680, 260, k=4, rot=0.1, wobble=0.18)
    m = [("dots", 1560, 380, -25, 0.8), ("heat", 300, 830, 0, 0.9), ("tile", 1740, 860, 8, 0.8),
         ("cross", 240, 280, 0, 0.7)]
    return f, m


def simple_light(seed):
    """The Simple set: White with one big orange arc on the left edge and a Charcoal corner bottom right."""
    f = Field(WH, seed)
    f.band(OR, "M0 300 C180 420 120 820 230 1080 L0 1080 Z",
           [(0, 300), (90, 380), (150, 600), (180, 850), (230, 1080), (0, 1080)])
    f.band(CH, "M1920 640 C1820 860 1620 1000 1380 1080 L1920 1080 Z",
           [(1920, 640), (1840, 820), (1700, 950), (1520, 1040), (1380, 1080), (1920, 1080)])
    m = [("dashes", 1700, 120, 20, 0.8), ("dots", 1600, 560, -25, 0.7)]
    return f, m


def shapes_light(seed):
    """The Shapes set: White with orange and Charcoal blobs at the edges and Charcoal marks."""
    f = Field(WH, seed)
    f.blob(OR, 1150, 30, 480, 140, k=1, rot=-0.05)
    f.blob(CH, 1880, 120, 220, 200, k=2)
    f.blob(CH, 1820, 820, 260, 340, k=3, rot=0.3)
    f.blob(CH, 200, 1020, 380, 200, k=4, rot=-0.2)
    f.blob(OR, 1100, 1080, 330, 180, k=5)
    m = [("cross", 1460, 200, 0, 0.8), ("dots", 300, 760, 90, 0.7, CH), ("drop", 1700, 520, 0, 0.7, CH),
         ("smile", 160, 520, -30, 0.8), ("dots", 230, 300, -25, 0.6, CH)]
    return f, m


def orange_pop(seed):
    """The Pop set: Climb Orange ground with Charcoal and Dark Brown blobs and Light Grey pills."""
    f = Field(OR, seed)
    f.blob(CH, 1820, 160, 360, 260, k=1, rot=0.3)
    f.blob(DB, 100, 900, 380, 300, k=2)
    f.blob(CH, 1700, 1040, 300, 180, k=3)
    f.blob(DB, 820, 1120, 260, 120, k=4)
    m = [("pills", 1700, 380, -30, 1.0, LG), ("dots", 260, 600, -25, 0.9, CH), ("target", 1820, 760, 0, 0.9, CH),
         ("heat", 1100, 90, 0, 0.9, CH), ("bricks", 260, 900, 0, 0.8), ("tile", 1660, 1000, 6, 0.7)]
    return f, m


def sticker_field(seed):
    """The Sticker set: Dark Brown with tone blobs at the edges, for house drawings and photo cards on top."""
    f = Field(DB, seed)
    f.blob(TONE, 60, 620, 300, 300, k=1)
    f.blob(TONE, 1800, 900, 380, 320, k=2)
    f.blob(OR, 1880, 120, 200, 160, k=3)
    f.blob(OR, 80, 1060, 260, 120, k=4)
    m = [("dashes", 960, 60, 0, 0.9), ("dots", 1640, 500, -25, 0.8), ("cross", 380, 980, 0, 0.6)]
    return f, m


LAYOUTS = dict(funky=funky, wavy=wavy, simple=simple_light, shapes=shapes_light, pop=orange_pop,
               stickers=sticker_field)
