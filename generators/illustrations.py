"""Hand drawn line illustrations: our own set of objects tied to the ClimbUK messages (microphone, lanyard badge,
tickets, handshake, rocket and so on), drawn in code so every copy can be placed, rotated and recoloured.

Each drawing is a list of strokes in a 200x200 box. A stroke is a plain geometric path (line, spline, arc,
rounded rectangle) that hand() turns into a pen line: the path is resampled, pushed off its centre line by slow,
smooth wobble, closed shapes overshoot their start like a pen that does not lift exactly where it began, and some
strokes get a second, looser pass. Orange fills sit slightly off register under the line, like a screen print, and
details on a fill are cut back in the ground colour.

    python3 generators/illustrations.py            # writes illustrations/<name>.svg for every drawing

In a layout:

    import illustrations as I
    I.svg("microphone")                       # inline <svg> markup, orange ink, Dark Brown cut lines
    I.svg("badge", label="SPEAKER")           # the badge, the ticket and the calendar carry a text slot
    I.place("rocket", x, y, size, rotate=-8)  # absolutely positioned inline <svg> for an HTML page

Colours come from CSS: the line and the fills use currentColor (default Climb Orange through --doodle-ink) and the
cut lines use --doodle-ground (default Dark Brown), so a ghosted copy is just the same drawing at low opacity.
Output is deterministic for a given seed.
"""
import html
import math
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / "illustrations"
INK = "#E8712A"
GROUND = "#1E0F05"
BOX = 200.0
STROKE = 4.0
WOBBLE = 0.45   # drift in px at full length; the old marker look was about 1.6 with jitter on top
TONE = 0.22     # opacity of the back tone on main shapes, the low layer that gives an icon depth


# ---------------------------------------------------------------- geometry

def _lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def _resample(pts, step):
    """Even spacing along a polyline."""
    out = [pts[0]]
    carry = 0.0
    for a, b in zip(pts, pts[1:]):
        seg = math.dist(a, b)
        if seg == 0:
            continue
        d = step - carry
        while d <= seg:
            out.append(_lerp(a, b, d / seg))
            d += step
        carry = seg - (d - step)
    if math.dist(out[-1], pts[-1]) > step * 0.25:
        out.append(pts[-1])
    return out


def _catmull(pts, n=10, closed=False):
    """Points along a Catmull-Rom spline through pts."""
    if len(pts) < 3:
        return list(pts)
    p = list(pts)
    if closed:
        p = [p[-1]] + p + [p[0], p[1]]
    else:
        p = [p[0]] + p + [p[-1]]
    out = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(p[-2])
    return out


def _rot(pts, deg, c=(100, 100)):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    return [(c[0] + (x - c[0]) * ca - (y - c[1]) * sa, c[1] + (x - c[0]) * sa + (y - c[1]) * ca) for x, y in pts]


# ---------------------------------------------------------------- stroke builders
# Every builder returns a stroke dict. Options: fill ("ink" or "ground" for a filled shape), ink (False for no
# outline), knock (outline in the ground colour, for detail on top of a fill), double (a second loose pass),
# w (stroke width factor), amp (wobble factor).

def _s(pts, closed=False, **kw):
    d = dict(pts=pts, closed=closed, fill=None, ink=True, knock=False, double=False, w=1.0, amp=1.0, dash=None)
    d.update(kw)
    return d


def line(*pts, **kw):
    return _s(list(pts), **kw)


def curve(*pts, closed=False, **kw):
    return _s(_catmull(list(pts), closed=closed), closed=closed, **kw)


def arc(cx, cy, rx, ry, a0=0, a1=360, **kw):
    n = max(12, int(abs(a1 - a0) / 6))
    pts = [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
            cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    closed = abs(a1 - a0) >= 360
    return _s(pts[:-1] if closed else pts, closed=closed, **kw)


def circle(cx, cy, r, **kw):
    return arc(cx, cy, r, r, **kw)


def rrect(x, y, wd, ht, r=8, **kw):
    pts = []
    for cx, cy, a in ((x + wd - r, y + r, -90), (x + wd - r, y + ht - r, 0), (x + r, y + ht - r, 90), (x + r, y + r, 180)):
        pts += [(cx + r * math.cos(math.radians(a + 90 * i / 6)), cy + r * math.sin(math.radians(a + 90 * i / 6)))
                for i in range(7)]
    return _s(pts, closed=True, **kw)


def poly(*pts, **kw):
    return _s(list(pts), closed=True, **kw)


def ticket_outline(x, y, wd, ht, r=9, **kw):
    """A ticket with concave corners (the bite out of each corner)."""
    pts = []
    corners = ((x, y, 0), (x + wd, y, 90), (x + wd, y + ht, 180), (x, y + ht, 270))
    for cx, cy, a in corners:
        pts += [(cx + r * math.cos(math.radians(a - i * 90 / 6)) * 1, cy + r * math.sin(math.radians(a - i * 90 / 6)))
                for i in range(7)]
    return _s(pts, closed=True, **kw)


def text(x, y, size, default, slot="label", width=None, rotate=0, colour="ground", weight=800):
    return dict(text=default, x=x, y=y, size=size, slot=slot, width=width, rotate=rotate, colour=colour, weight=weight)


def layer(strokes, n):
    """Put strokes on layer n (see inner): higher layers are drawn on top of everything below."""
    return [dict(s, layer=n) for s in strokes]


def solid(strokes, n):
    """Strokes on layer n + 1 over a ground cover of their closed shapes on layer n, so they hide what is behind."""
    cover = [dict(s, fill="ground", ink=False, knock=False, double=False) for s in strokes if s.get("closed")]
    return layer(cover, n) + layer(strokes, n + 1)


def turn(strokes, deg, c=(100, 100)):
    """Rotate a group of strokes (text items included) about c."""
    out = []
    for s in strokes:
        s = dict(s)
        if "text" in s:
            (s["x"], s["y"]), = _rot([(s["x"], s["y"])], deg, c)
            s["rotate"] = s["rotate"] + deg
        else:
            s["pts"] = _rot(s["pts"], deg, c)
        out.append(s)
    return out


def shift(strokes, dx, dy, k=1.0, c=(100, 100)):
    out = []
    for s in strokes:
        s = dict(s)
        f = lambda p: (c[0] + (p[0] - c[0]) * k + dx, c[1] + (p[1] - c[1]) * k + dy)
        if "text" in s:
            s["x"], s["y"] = f((s["x"], s["y"]))
            s["size"] *= k
            s["width"] = s["width"] * k if s["width"] else None
        else:
            s["pts"] = [f(p) for p in s["pts"]]
        out.append(s)
    return out


def sparkle(x, y, r, **kw):
    """A four point star made of two crossing ticks."""
    return [line((x - r, y), (x + r, y), **kw), line((x, y - r), (x, y + r), **kw)]


# ---------------------------------------------------------------- the hand

def _noise(rnd, amp):
    """Slow, smooth drift only: a tablet line wanders gently, it does not shake."""
    waves = [(rnd.uniform(70, 160), rnd.uniform(0, math.tau), rnd.uniform(0.6, 1.0)) for _ in range(2)]
    return lambda s: amp * sum(a * math.sin(math.tau * s / lam + ph) for lam, ph, a in waves)


def hand(pts, rnd, amp=1.0, closed=False, overshoot=False):
    """Turn a clean path into a smoothed tablet line: even resample and a slow drift off the centre line.
    Closed shapes meet cleanly; the hand shows in the drift and in the pressure of the stroke, not in wobble."""
    if closed:
        pts = list(pts) + [pts[0]]
    pts = _resample(pts, 2.0)
    if len(pts) < 2:
        return pts
    length = 2.0 * (len(pts) - 1)
    n = _noise(rnd, WOBBLE * amp * min(1.0, 0.35 + length / 160))
    out = []
    for i, p in enumerate(pts):
        a = pts[max(0, i - 1)]
        b = pts[min(len(pts) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        o = n(i * 2.0)
        if closed:
            # Fade the drift to zero at the join so the line closes on itself.
            t = i / max(1, len(pts) - 1)
            o *= min(1.0, t / 0.08, (1 - t) / 0.08)
        out.append((p[0] + nx * o, p[1] + ny * o))
    return out


def _smooth(pts, k=2):
    """A light moving average, the stabiliser a drawing tablet applies."""
    if len(pts) < 5:
        return pts
    out = []
    for i in range(len(pts)):
        a, b = max(0, i - k), min(len(pts), i + k + 1)
        if i < k or i >= len(pts) - k:
            out.append(pts[i])
            continue
        xs = pts[a:b]
        out.append((sum(p[0] for p in xs) / len(xs), sum(p[1] for p in xs) / len(xs)))
    return out


def _cornered(pts, limit=35):
    """True when a path turns a sharp corner; those keep an even, round-joined line instead of a taper."""
    for a, b, c in zip(pts, pts[1:], pts[2:]):
        u, v = (b[0] - a[0], b[1] - a[1]), (c[0] - b[0], c[1] - b[1])
        lu, lv = math.hypot(*u), math.hypot(*v)
        if lu and lv:
            cos = max(-1.0, min(1.0, (u[0] * v[0] + u[1] * v[1]) / (lu * lv)))
            if math.degrees(math.acos(cos)) > limit:
                return True
    return False


def _ribbon(pts, width, rnd, taper=True):
    """An open pen stroke as a filled outline: pressure swells in the middle and lifts off at both ends."""
    if len(pts) < 3:
        return None
    n = len(pts)
    press = _noise(rnd, 0.06)
    left, right = [], []
    total = 2.0 * (n - 1)
    ramp = min(0.3, 14.0 / max(total, 1))
    for i, p in enumerate(pts):
        a = pts[max(0, i - 1)]
        b = pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        t = i / (n - 1)
        if taper:
            e = min(1.0, t / ramp, (1 - t) / ramp)
            f = 0.42 + 0.58 * math.sin(e * math.pi / 2)
        else:
            f = 1.0
        hw = width / 2 * f * (1 + press(i * 2.0))
        left.append((p[0] + nx * hw, p[1] + ny * hw))
        right.append((p[0] - nx * hw, p[1] - ny * hw))

    def cap(c, d0, r):
        # A round cap from one side to the other.
        ang = math.atan2(d0[1], d0[0])
        return [(c[0] + r * math.cos(ang + math.pi * j / 6), c[1] + r * math.sin(ang + math.pi * j / 6)) for j in range(1, 6)]

    e0 = (left[-1][0] - pts[-1][0], left[-1][1] - pts[-1][1])
    r0 = math.hypot(*e0)
    end_cap = cap(pts[-1], e0, r0) if r0 else []
    s0 = (right[0][0] - pts[0][0], right[0][1] - pts[0][1])
    r1 = math.hypot(*s0)
    start_cap = cap(pts[0], s0, r1) if r1 else []
    return left + end_cap + right[::-1] + start_cap


def _d(pts, closed=False):
    """Smooth SVG path data through a dense point list (Catmull-Rom as cubic Beziers)."""
    p = pts[::3] if len(pts) > 9 else pts
    if p[-1] != pts[-1]:
        p = p + [pts[-1]]
    if len(p) < 3:
        return "M%.1f %.1fL%.1f %.1f" % (p[0] + p[-1])
    d = ["M%.1f %.1f" % p[0]]
    ext = [p[0]] + p + [p[-1]]
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append("C%.1f %.1f %.1f %.1f %.1f %.1f" % (c1 + c2 + p2))
    if closed:
        d.append("Z")
    return "".join(d)


# ---------------------------------------------------------------- the drawings

def _mesh(cx, cy, r, gap=11, inset=4):
    """A diagonal lattice cut back into a round mic head: chords at 45 degrees both ways."""
    out = []
    rr = r - inset
    for sgn in (1, -1):
        o = -rr + gap / 2
        while o < rr:
            h = math.sqrt(max(0.0, rr * rr - o * o))
            # The chord at offset o, rotated 45 degrees.
            ux, uy = math.sqrt(0.5), sgn * math.sqrt(0.5)
            nx, ny = -uy, ux
            a = (cx + nx * o - ux * h, cy + ny * o - uy * h)
            b = (cx + nx * o + ux * h, cy + ny * o + uy * h)
            if h > 4:
                out.append(line(a, b, knock=True, w=0.62))
            o += gap
    return out


def _microphone():
    s = [circle(100, 52, 30, fill="ink", ink=True, double=True),
         ] + _mesh(100, 52, 30) + [
         rrect(77, 80, 46, 15, 5),
         line((79, 95), (91, 166), (109, 166), (121, 95)),
         rrect(95, 110, 10, 18, 4, fill="ink"),
         curve((100, 166), (101, 180), (116, 191), (138, 186), (142, 172), (128, 168), (122, 182), (140, 196),
               (172, 194), (192, 182))]
    return turn(s, -24, (100, 110))


def _badge():
    strap = [line((52, 2), (93, 72)), line((70, 2), (101, 60), w=0.8),
             line((148, 2), (107, 72)), line((130, 2), (99, 60), w=0.8)]
    clip = [rrect(91, 66, 18, 16, 3), circle(100, 86, 5, w=0.8)]
    card = [rrect(44, 92, 112, 98, 12, fill="ink", double=True),
            rrect(86, 100, 28, 7, 3.5, knock=True, w=0.7),
            line((60, 166), (140, 166), knock=True, w=0.8),
            line((70, 177), (130, 177), knock=True, w=0.7),
            text(100, 148, 21, "EXHIBITOR", slot="label", width=96)]
    return strap + clip + turn(card, 5, (100, 92))


def _tickets():
    back = [ticket_outline(28, 66, 140, 62, 10), line((132, 72), (132, 122), dash=(5, 6), w=0.8),
            line((44, 86), (110, 86), w=0.7), line((44, 108), (96, 108), w=0.7)]
    front = [ticket_outline(32, 80, 140, 64, 10, fill="ink", double=True),
             line((136, 86), (136, 138), knock=True, dash=(5, 6), w=0.8),
             text(84, 119, 19, "ADMIT ONE", slot="label", width=86)]
    star = sparkle(154, 112, 7, knock=True, w=0.8)
    return turn(back, -16, (100, 96)) + turn(shift(front + star, 0, 14), 9, (100, 110))


def _scallop(a, b, bumps, depth):
    """Points along a to b with rounded bumps bulging to the left of the direction of travel (finger tips)."""
    n = bumps * 12
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    nx, ny = dy / L, -dx / L
    return [(a[0] + dx * i / n + nx * depth * abs(math.sin(math.pi * bumps * i / n)),
             a[1] + dy * i / n + ny * depth * abs(math.sin(math.pi * bumps * i / n))) for i in range(n + 1)]


def _handshake():
    # Two hands shaking, seen from the side. The left hand (tone) reaches in from the left; its fingers curl under
    # the right hand and show below it. The right hand (orange) comes from the right, its fingers wrapping over the
    # back of the left hand. The left thumb lies on top of the right hand. Layers keep every overlap clean.
    left = [poly((40, 84), (70, 80), (98, 82), (122, 88), (130, 110), (122, 132), (96, 138), (66, 136), (40, 132),
                 fill="tone"),
            rrect(14, 76, 26, 66, 6, fill="ink")]
    under = [rrect(108, 126, 40, 13, 6.5, fill="tone")]
    right = [poly((160, 82), (136, 78), (114, 84), (104, 96), (108, 124), (126, 132), (160, 130), fill="ink",
                  ink=False),
             rrect(78, 90, 46, 13, 6.5, fill="ink"), rrect(74, 104, 48, 13, 6.5, fill="ink"),
             rrect(78, 118, 42, 13, 6.5, fill="ink"),
             rrect(160, 74, 26, 66, 6, fill="ink")]
    gaps = [line((108, 103.5), (80, 103.5), knock=True, w=0.6), line((108, 117.5), (82, 117.5), knock=True, w=0.6)]
    thumb = [curve((62, 86), (84, 78), (110, 74), (124, 76), (127, 82), (122, 88), (100, 92), (74, 96),
                   closed=True, fill="tone")]
    s = turn(layer(left, 0) + layer(under, 0) + solid(right, 1) + layer(gaps, 2) + solid(thumb, 3), -6, (100, 108))
    s += sparkle(100, 40, 9) + [line((70, 52), (78, 62), w=0.85), line((130, 52), (122, 62), w=0.85)]
    return s


def _rocket():
    body = [curve((100, 14), (118, 34), (126, 64), (126, 128)),
            curve((100, 14), (82, 34), (74, 64), (74, 128)),
            line((74, 128), (126, 128)),
            poly((84, 40), (100, 14), (116, 40), (122, 48), (78, 48), fill="ink", ink=False),
            line((78, 48), (122, 48), w=0.9),
            circle(100, 76, 13, double=True), circle(100, 76, 6, fill="ink", ink=False),
            line((74, 96), (50, 130), (54, 142), (74, 128)),
            line((126, 96), (150, 130), (146, 142), (126, 128)),
            curve((88, 134), (90, 152), (100, 172), (110, 152), (112, 134), fill="ink"),
            curve((94, 138), (100, 160), (106, 138), knock=True, w=0.8)]
    trail = [line((50, 150), (34, 170)), line((68, 168), (54, 186), w=0.8), line((34, 132), (24, 145), w=0.7)]
    return turn(body, 38, (100, 104)) + trail


def _envelope():
    return [line((30, 86), (100, 40), (170, 86)),
            rrect(50, 52, 100, 84, 4, fill="ink"),
            line((64, 72), (136, 72), knock=True, w=0.8), line((64, 88), (124, 88), knock=True, w=0.8),
            line((64, 104), (130, 104), knock=True, w=0.8),
            rrect(30, 86, 140, 90, 6, double=True),
            line((30, 176), (100, 124), (170, 176)),
            line((30, 88), (84, 134), w=0.8), line((170, 88), (116, 134), w=0.8)]


def _clipboard():
    s = [rrect(44, 30, 112, 156, 12, double=True),
         rrect(74, 18, 52, 26, 7, fill="ink"), circle(100, 26, 4.5, knock=True, w=0.8)]
    for i, y in enumerate((70, 102, 134)):
        s.append(rrect(60, y - 9, 18, 18, 4, fill="ink" if i < 2 else None))
        s.append(line((88, y), (140, y)))
        if i < 2:
            s.append(line((63, y), (68, y + 6), (80, y - 12), w=1.0))
    s.append(line((60, 164), (120, 164), w=0.8))
    return s


def _trophy():
    s = [curve((58, 34), (60, 80), (80, 106), (100, 112), (120, 106), (140, 80), (142, 34), fill="ink"),
         line((56, 34), (144, 34), w=1.0),
         curve((60, 46), (34, 44), (36, 76), (66, 86), w=0.9),
         curve((140, 46), (166, 44), (164, 76), (134, 86), w=0.9),
         line((94, 112), (92, 138)), line((106, 112), (108, 138)),
         poly((78, 138), (122, 138), (130, 160), (70, 160)),
         rrect(60, 160, 80, 22, 4, fill="ink", double=True)]
    s += [line((100, 52), (104, 64), (116, 64), (106, 72), (110, 85), (100, 77), (90, 85), (94, 72), (84, 64),
               (96, 64), (100, 52), knock=True, w=0.8)]
    s += sparkle(30, 22, 7) + sparkle(176, 110, 6) + sparkle(168, 18, 4, w=0.8)
    return s


def _spotlight():
    lamp = [rrect(70, 36, 66, 52, 10, double=True),
            arc(136, 62, 9, 28, -90, 90, fill="ink"),
            line((80, 36), (80, 28)), line((96, 36), (96, 28)), line((112, 36), (112, 28)),
            rrect(56, 48, 14, 28, 4, fill="ink")]
    stand = [circle(103, 62, 6, w=0.9), line((103, 68), (103, 150)), line((76, 190), (103, 150), (130, 190)),
             line((103, 150), (103, 192), w=0.8)]
    # The beam is drawn in the lamp's own frame, fanning out from the lens, and turns with it, so the dashes
    # always follow the direction the light points.
    beam = [line((150, 40), (190, 26), dash=(9, 7), w=0.8), line((150, 84), (194, 102), dash=(9, 7), w=0.8),
            line((154, 62), (196, 62), w=0.6, dash=(3, 9))]
    return turn(lamp + beam, 24, (103, 62)) + stand


def _megaphone():
    s = [line((40, 88), (146, 48)), line((40, 112), (146, 152)),
         rrect(26, 86, 16, 28, 5, fill="ink"),
         arc(148, 100, 14, 52, 0, 360, fill="ink", double=True),
         arc(148, 100, 6, 26, 0, 360, knock=True, w=0.7),
         line((72, 116), (66, 150), (84, 154), (88, 122), w=0.9),
         arc(170, 100, 16, 22, -50, 50), arc(176, 100, 24, 38, -48, 48, w=0.9)]
    return turn(s, -10, (100, 100))


def _coffee():
    return [line((66, 62), (78, 180), (122, 180), (134, 62)),
            rrect(56, 48, 88, 16, 6), rrect(66, 36, 68, 14, 6),
            poly((70, 98), (130, 98), (126, 140), (74, 140), fill="ink"),
            curve((92, 112), (100, 106), (108, 112), (100, 126), (92, 112), knock=True, w=0.7),
            curve((86, 30), (80, 20), (88, 10), (82, 0), w=0.8),
            curve((104, 30), (98, 18), (108, 8), (101, -2), w=0.8)]


def _glass(x, deg):
    g = [curve((x - 18, 30), (x - 16, 70), (x, 92), (x + 16, 70), (x + 18, 30)),
         line((x - 18, 30), (x + 18, 30), w=0.8),
         curve((x - 15, 52), (x - 12, 72), (x, 88), (x + 12, 72), (x + 15, 52), fill="ink", ink=False),
         line((x - 15, 52), (x + 15, 52), w=0.9),
         line((x, 92), (x, 150)),
         arc(x, 154, 20, 5, 0, 360, w=0.9),
         circle(x - 4, 66, 2.2, knock=True, w=0.5), circle(x + 5, 74, 1.6, knock=True, w=0.5)]
    return turn(g, deg, (x, 150))


def _glasses():
    s = _glass(62, 11) + _glass(138, -11)
    s += [line((100, 14), (100, 2)), line((86, 18), (78, 8)), line((114, 18), (122, 8))]
    s += sparkle(36, 40, 6) + sparkle(168, 48, 5)
    return s


def _bubbles():
    return [curve((40, 40), (130, 36), (142, 72), (128, 104), (70, 108), (48, 128), (54, 104), (24, 96), (22, 60),
                  (40, 40), double=True),
            line((48, 62), (116, 62), w=0.9), line((48, 80), (100, 80), w=0.9),
            curve((92, 112), (170, 104), (184, 130), (174, 158), (172, 180), (156, 162), (104, 168), (84, 146),
                  (92, 112), fill="ink"),
            circle(112, 138, 5, fill="ground", ink=False), circle(134, 137, 5, fill="ground", ink=False),
            circle(156, 136, 5, fill="ground", ink=False)]


def _chart():
    s = [line((28, 22), (28, 176), (182, 176)),
         rrect(46, 134, 22, 42, 3), rrect(78, 112, 22, 64, 3), rrect(110, 92, 22, 84, 3),
         rrect(142, 64, 22, 112, 3, fill="ink"),
         line((40, 120), (72, 96), (100, 104), (140, 58), (168, 32), double=True),
         line((150, 30), (170, 30), (168, 50))]
    return s


def _lightbulb():
    s = [curve((80, 128), (78, 112), (60, 96), (58, 70), (72, 38), (100, 28), (128, 38), (142, 70), (140, 96),
               (122, 112), (120, 128), double=True),
         line((80, 128), (120, 128)),
         rrect(80, 132, 40, 26, 6, fill="ink"),
         line((84, 141), (116, 141), knock=True, w=0.7), line((84, 150), (116, 150), knock=True, w=0.7),
         curve((92, 160), (100, 172), (108, 160), w=0.9),
         line((90, 124), (90, 92), (96, 82), (100, 92), (104, 82), (110, 92), (110, 124), w=0.8)]
    for a in (-150, -115, -90, -65, -30):
        r0, r1 = 58, 76
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        s.append(line((100 + r0 * ca, 76 + r0 * sa), (100 + r1 * ca, 76 + r1 * sa), w=0.9))
    return s


def _calendar():
    s = [rrect(28, 42, 144, 140, 12, double=True),
         rrect(28, 42, 144, 36, 10, fill="ink", ink=False),
         line((28, 78), (172, 78)),
         rrect(56, 28, 10, 26, 5, fill="ground"), rrect(134, 28, 10, 26, 5, fill="ground"),
         text(100, 68, 17, "JUNE . JULY", slot="month", width=104),
         text(76, 140, 46, "30", slot="day", colour="ink", width=50),
         text(138, 140, 46, "1", slot="day2", colour="ink")]
    s.append(curve((44, 108), (78, 92), (110, 112), (98, 150), (60, 156), (44, 132), (52, 104), w=0.9))
    for x in (40, 62, 84, 106, 128, 150):
        s.append(circle(x + 6, 170, 1.8, fill="ink", ink=False))
    return s


def _pin():
    return [curve((100, 182), (76, 140), (56, 108), (56, 76), (72, 42), (100, 30), (128, 42), (144, 76), (144, 108),
                  (124, 140), (100, 182), fill="ink", double=True),
            circle(100, 78, 18, fill="ground", ink=False, knock=True, w=0.6),
            arc(100, 186, 46, 9, 200, 340, w=0.8), arc(100, 186, 60, 13, 205, 335, w=0.6)]


def _laptop():
    return [rrect(42, 40, 116, 82, 8, double=True),
            rrect(52, 50, 96, 62, 4, fill="ink", ink=False),
            line((60, 98), (80, 82), (96, 90), (118, 66), (136, 60), knock=True, w=0.9),
            line((28, 128), (172, 128), (186, 152), (14, 152), (28, 128)),
            line((84, 140), (116, 140), w=0.8)]


def _people():
    s = []
    for x, y, r, f in ((52, 74, 17, None), (148, 74, 17, None), (100, 62, 21, "ink")):
        s.append(circle(x, y, r, fill=f))
    s.append(curve((20, 160), (24, 116), (52, 102), (80, 116), (84, 140)))
    s.append(curve((116, 140), (120, 116), (148, 102), (176, 116), (180, 160)))
    s.append(curve((60, 176), (64, 120), (100, 96), (136, 120), (140, 176), fill="ink", double=True))
    s.append(line((10, 176), (190, 176), w=0.8))
    return s


def _stage():
    s = [line((6, 18), (194, 18), w=1.0),
         curve((8, 20), (54, 42), (100, 24), (146, 42), (192, 20), w=0.9),
         # Left drape tied back, right drape the same.
         line((10, 20), (10, 150)), curve((54, 40), (40, 76), (30, 104), (34, 150)),
         curve((22, 30), (24, 90), (20, 150), w=0.6),
         line((190, 20), (190, 150)), curve((146, 40), (160, 76), (170, 104), (166, 150)),
         curve((178, 30), (176, 90), (180, 150), w=0.6),
         rrect(24, 96, 16, 8, 3, fill="ink"), rrect(160, 96, 16, 8, 3, fill="ink"),
         poly((6, 150), (194, 150), (198, 176), (2, 176), fill="ink"),
         line((100, 150), (100, 96)), line((86, 150), (100, 140), (114, 150), w=0.8),
         rrect(95, 82, 10, 16, 4, fill="ink"),
         line((74, 44), (88, 76), dash=(6, 6), w=0.7), line((126, 44), (112, 76), dash=(6, 6), w=0.7)]
    s += sparkle(64, 112, 6) + sparkle(138, 100, 5, w=0.8)
    return s


def _summit():
    return [line((8, 176), (62, 104), (82, 124), (118, 60), (192, 176), double=True),
            poly((104, 84), (118, 60), (132, 84), (124, 80), (116, 88), (110, 82), fill="ink", ink=False),
            line((118, 60), (118, 20)),
            poly((118, 20), (156, 30), (118, 42), fill="ink"),
            line((50, 176), (76, 146), w=0.7), line((140, 176), (126, 150), w=0.7)]


def _record():
    return [circle(92, 104, 74, double=True),
            circle(92, 104, 56, w=0.6), circle(92, 104, 42, w=0.6),
            circle(92, 104, 22, fill="ink"), circle(92, 104, 4, fill="ground", ink=False),
            arc(92, 104, 64, 64, 200, 250, w=0.7),
            line((186, 22), (178, 96), (148, 130)), rrect(176, 12, 18, 18, 5, fill="ink"),
            rrect(138, 124, 18, 12, 3, fill="ink")]


def _sneaker():
    s = [curve((22, 138), (18, 112), (24, 90), (40, 92), (58, 92), (68, 72), (82, 62), (92, 68),
               (112, 88), (136, 102), (164, 112), (186, 124), (192, 140)),
         poly((14, 138), (190, 138), (196, 146), (188, 160), (24, 160), (12, 150), fill="ink", double=True),
         line((26, 150), (180, 150), knock=True, w=0.7, dash=(6, 6)),
         rrect(14, 92, 12, 30, 4, fill="ink"),
         curve((150, 138), (152, 118), (186, 124), w=0.9),
         # Laces across the instep, with a bow.
         line((92, 76), (104, 70), w=0.8), line((102, 86), (114, 78), w=0.8), line((114, 94), (126, 86), w=0.8),
         curve((90, 70), (78, 56), (72, 66), (90, 70), w=0.8), curve((90, 70), (100, 52), (106, 62), (90, 70), w=0.8),
         # Two Ascent chevrons on the side.
         line((52, 130), (74, 110), (96, 130), w=1.1), line((84, 132), (106, 112), (128, 132), w=1.1)]
    s += [line((2, 100), (10, 100), w=0.8), line((0, 114), (10, 114), w=0.8), line((4, 128), (10, 128), w=0.8)]
    return s


def _phone():
    return [rrect(58, 20, 84, 162, 14, double=True),
            line((88, 32), (112, 32), w=0.8),
            rrect(68, 48, 64, 30, 8, fill="ink"),
            line((76, 58), (120, 58), knock=True, w=0.7), line((76, 68), (108, 68), knock=True, w=0.7),
            rrect(68, 88, 52, 22, 8),
            rrect(80, 120, 52, 30, 8, fill="ink"),
            line((88, 130), (124, 130), knock=True, w=0.7), line((88, 140), (112, 140), knock=True, w=0.7),
            circle(100, 166, 5, w=0.8)]


def _sparkles():
    s = sparkle(70, 70, 22, double=True) + sparkle(140, 120, 14) + sparkle(130, 44, 8) + sparkle(56, 146, 9)
    s += [circle(150, 70, 4, fill="ink", ink=False), circle(90, 130, 3, fill="ink", ink=False)]
    return s


def _arrow():
    return [curve((16, 160), (40, 110), (90, 150), (110, 110), (80, 80), (110, 56), (150, 60), (176, 36)),
            line((152, 30), (178, 34), (170, 60))]


DRAWINGS = {
    # name: (builder, what it says)
    "microphone": (_microphone, "Speaking, main stage moments"),
    "badge": (_badge, "Lanyard badge with a role label: EXHIBITOR, SPEAKER, PARTNER, DELEGATE"),
    "tickets": (_tickets, "Admission tickets: get your ticket"),
    "handshake": (_handshake, "Partners, deals, meetings with the right people"),
    "rocket": (_rocket, "Growth, launches, bigger stage"),
    "envelope": (_envelope, "Check your inbox, invitations"),
    "clipboard": (_clipboard, "Agenda, plan your two days"),
    "trophy": (_trophy, "ClimbAwards"),
    "spotlight": (_spotlight, "Stage light, main stage moments"),
    "megaphone": (_megaphone, "Announcements, tell people you are going"),
    "coffee": (_coffee, "Close conversations, meetings"),
    "glasses": (_glasses, "After parties, the drinks reception"),
    "bubbles": (_bubbles, "Conversations, find your people"),
    "chart": (_chart, "Growth, investors"),
    "lightbulb": (_lightbulb, "Ideas, real advice"),
    "calendar": (_calendar, "Save the dates: 30 June and 1 July 2027"),
    "pin": (_pin, "Where to be (never a place name)"),
    "laptop": (_laptop, "Book meetings, the event app, online"),
    "people": (_people, "Find your people"),
    "stage": (_stage, "Main stage moments"),
    "summit": (_summit, "Your business. Bigger stage. The climb"),
    "record": (_record, "DJ sets, after parties"),
    "sneaker": (_sneaker, "Merch, two days on your feet"),
    "phone": (_phone, "The ClimbGroup Event App, sharing"),
    "sparkles": (_sparkles, "Small accent for corners"),
    "arrow": (_arrow, "Hand drawn pointer"),
}



def _load_sets():
    """Extra drawings live in illustration_sets/*.py. Each module has build(k), where k is this module, and returns
    {name: (builder, what it says)}. Names must be new."""
    import importlib.util
    folder = HERE / "illustration_sets"
    for f in sorted(folder.glob("set_*.py")) if folder.exists() else []:
        spec = importlib.util.spec_from_file_location("climb_ill_" + f.stem, f)
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
            entries = mod.build(sys.modules[__name__])
        except Exception as e:  # one broken set must not take the others down
            print("[illustrations] skipped %s: %r" % (f.name, e), file=sys.stderr)
            continue
        for name, entry in entries.items():
            if name in DRAWINGS:
                raise ValueError("%s: drawing %r already exists" % (f.name, name))
            DRAWINGS[name] = entry


_load_sets()


# ---------------------------------------------------------------- rendering

def _text_svg(t, label, ink_var, ground_var):
    value = t["text"]
    if label is not None and t["slot"] == "label":
        value = label
    fill = ground_var if t["colour"] == "ground" else ink_var
    fit = ('textLength="%.1f" lengthAdjust="spacingAndGlyphs" ' % t["width"]
           if t["width"] and len(value) > 3 else "")
    return ('<text x="%.1f" y="%.1f" transform="rotate(%.1f %.1f %.1f)" text-anchor="middle" %s'
            'style="font-family:Montserrat,Arial,sans-serif;font-weight:%d;font-size:%.1fpx;letter-spacing:.02em;fill:%s;stroke:none">%s</text>'
            % (t["x"], t["y"], t["rotate"], t["x"], t["y"], fit, t["weight"], t["size"], fill, html.escape(value)))


def inner(name, seed=0, label=None, weight=1.0, misregister=(0, 0)):
    """The drawing as SVG elements for a 0 0 200 200 viewBox. weight scales the line.

    Layers, back to front: tones (the main shapes filled at low opacity, for depth), solid fills, the line,
    cut lines in the ground colour, text. Open lines are drawn as tapered pen strokes; closed outlines and dashes
    keep an even width."""
    builder = DRAWINGS[name][0]
    rnd = random.Random("%s-%d" % (name, seed))
    ink, ground = "currentColor", "var(--doodle-ground,%s)" % GROUND
    sw = STROKE * weight
    mx, my = misregister
    strokes = builder()
    # A stroke with layer=n (default 0) is drawn after every lower layer, tones, fills and line included, so a
    # front shape with a ground fill hides what is behind it: links pass over and under, hands overlap.
    groups = []
    for n in sorted({s.get("layer", 0) for s in strokes}):
        groups.append(_layer([s for s in strokes if s.get("layer", 0) == n], rnd, label, ink, ground, sw, mx, my))
    return '<g style="stroke-linecap:round;stroke-linejoin:round">%s</g>' % "".join(groups)


def _layer(strokes, rnd, label, ink, ground, sw, mx, my):
    tones, fills, lines, knocks, texts = [], [], [], [], []
    for s in strokes:
        if "text" in s:
            texts.append(_text_svg(s, label, ink, ground))
            continue
        tone = s["fill"] == "tone" or (s["double"] and not s["fill"] and s["closed"])
        if s["fill"] and s["fill"] != "tone":
            pts = _smooth(hand(s["pts"], rnd, s["amp"] * 0.6, closed=True))
            colour = ink if s["fill"] == "ink" else ground
            off = (mx, my) if (s["fill"] == "ink" and s["ink"]) else (0, 0)
            fills.append('<path d="%s" transform="translate(%.1f %.1f)" style="fill:%s;stroke:none"/>'
                         % (_d(pts, True), off[0], off[1], colour))
        if tone:
            pts = _smooth(hand(s["pts"], random.Random(rnd.random()), s["amp"] * 0.6, closed=True))
            tones.append('<path d="%s" style="fill:%s;stroke:none;opacity:%.2f"/>' % (_d(pts, True), ink, TONE))
        if s["ink"] or s["knock"]:
            pts = _smooth(hand(s["pts"], rnd, s["amp"], closed=s["closed"]))
            colour = ground if s["knock"] else ink
            width = sw * s["w"]
            outline = None if (s["closed"] or s["dash"] or _cornered(s["pts"])) else _ribbon(pts, width * 1.12, rnd)
            if outline:
                el = '<path d="%s" style="fill:%s;stroke:none"/>' % (_d(outline, True), colour)
            else:
                dash = (' stroke-dasharray="%.1f %.1f"' % s["dash"]) if s["dash"] else ""
                el = '<path d="%s" style="fill:none;stroke:%s;stroke-width:%.2f"%s/>' % (
                    _d(pts, s["closed"]), colour, width, dash)
            (knocks if s["knock"] else lines).append(el)
    return "".join(tones) + "".join(fills) + "".join(lines) + "".join(knocks) + "".join(texts)


def svg(name, seed=0, label=None, weight=1.0, ink=None, ground=None, cls="doodle", style="", title=None):
    """Inline <svg> markup. ink and ground override --doodle-ink and --doodle-ground for this copy."""
    vars_ = []
    if ink:
        vars_.append("--doodle-ink:%s" % ink)
    if ground:
        vars_.append("--doodle-ground:%s" % ground)
    t = "<title>%s</title>" % html.escape(title) if title else ""
    return ('<svg class="%s" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" '
            'style="overflow:visible;color:var(--doodle-ink,%s);%s%s">%s%s</svg>'
            % (cls, INK, ";".join(vars_) + (";" if vars_ else ""), style, t, inner(name, seed, label, weight)))


def place(name, x, y, size, rotate=0, opacity=1.0, seed=0, label=None, weight=1.0, ink=None, ground=None,
          blur=0, flip=False, extra=""):
    """An absolutely positioned drawing for an HTML layout. x, y are the top left of its 200x200 box in px."""
    tr = "rotate(%.1fdeg)%s" % (rotate, " scaleX(-1)" if flip else "")
    style = ("position:absolute;left:%.0fpx;top:%.0fpx;width:%.0fpx;height:%.0fpx;transform:%s;opacity:%.2f;%s%s"
             % (x, y, size, size, tr, opacity, ("filter:blur(%.1fpx);" % blur) if blur else "", extra))
    return svg(name, seed=seed, label=label, weight=weight, ink=ink, ground=ground, style=style)


def standalone(name, label=None):
    """A clean standalone SVG file: orange line by default, override with --doodle-ink and --doodle-ground."""
    desc = DRAWINGS[name][1]
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200" '
            'style="overflow:visible;color:var(--doodle-ink,%s)">\n<title>%s</title>\n<desc>ClimbUK hand drawn line '
            'illustration: %s. Line and fills use currentColor (default Climb Orange through --doodle-ink); cut lines use '
            '--doodle-ground (default Dark Brown).</desc>\n%s\n</svg>\n'
            % (INK, name, html.escape(desc), inner(name, 0, label)))


def write_all(out=OUT):
    out.mkdir(parents=True, exist_ok=True)
    names = []
    for name in DRAWINGS:
        (out / ("%s.svg" % name)).write_text(standalone(name), encoding="utf-8")
        names.append(name)
    for label in ("SPEAKER", "PARTNER", "DELEGATE"):
        (out / ("badge-%s.svg" % label.lower())).write_text(standalone("badge", label), encoding="utf-8")
        names.append("badge-" + label.lower())
    return names


if __name__ == "__main__":
    written = write_all()
    print("[illustrations] %d SVG files in %s" % (len(written), OUT))
