"""The five ClimbUK motif families (plus the slab, peak and grain finishing marks) as SVG fragments, drawn to the recipes in
.agents/skills/climb-visual-style/references/elements.md.

Every function takes the canvas size and a seed and returns SVG markup (no outer <svg>), so the same motif can be
placed on any surface. Output is deterministic for a given seed.
"""
import math
import random

ORANGE = "#E8712A"
TINT = "#F2AE86"
WHITE = "#FFFFFF"
DARK = "#1E0F05"


def _tone(ground_is_dark, alpha):
    return ("#FFFFFF" if ground_is_dark else DARK), alpha


def contours(w, h, seed=1, rings=12, dark=True, marker=True, cx=None, cy=None):
    """Topographic contour rings centred off one edge so they run off the canvas."""
    rnd = random.Random(seed)
    cx = w * (0.82 if cx is None else cx)
    cy = h * (0.78 if cy is None else cy)
    unit = max(w, h) / 1920 * 8
    gap = unit * (7 if max(w, h) > 1200 else 4)
    base = gap * 2
    harmonics = [(rnd.randint(2, 5), rnd.uniform(0, math.tau), rnd.uniform(0.04, 0.09)) for _ in range(3)]
    colour, alpha = _tone(dark, 0.12)
    stroke = max(1.0, unit * 0.5)
    marker_ring = rings // 2 if marker else -1
    out = []
    for k in range(rings):
        r0 = base + k * gap * (1 + k * 0.035)
        pts = []
        for i in range(181):
            t = i / 180 * math.tau
            wobble = sum(a * math.sin(n * t + p + k * 0.12) for n, p, a in harmonics)
            r = r0 * (1 + wobble)
            pts.append((cx + r * math.cos(t), cy + r * math.sin(t) * 0.82))
        d = "M" + " L".join("%.1f %.1f" % p for p in pts) + " Z"
        if k == marker_ring:
            out.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, ORANGE, stroke * 1.6))
        else:
            out.append('<path d="%s" fill="none" stroke="%s" stroke-opacity="%.2f" stroke-width="%.1f"/>'
                       % (d, colour, alpha, stroke))
    return "\n".join(out)


def stage_light(w, h, seed=1, beams=3, uid="sl"):
    """Soft beams fanning down from a point above the canvas, with a glow at the source and film grain."""
    rnd = random.Random(seed)
    sx = w * rnd.uniform(0.55, 0.75)
    sy = -h * 0.12
    defs = [
        '<linearGradient id="%s-beam" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="%s" stop-opacity="0.55"/><stop offset="1" stop-color="%s" stop-opacity="0"/>'
        '</linearGradient>' % (uid, ORANGE, ORANGE),
        '<radialGradient id="%s-glow"><stop offset="0" stop-color="%s" stop-opacity="0.7"/>'
        '<stop offset="1" stop-color="%s" stop-opacity="0"/></radialGradient>' % (uid, TINT, TINT),
        '<filter id="%s-blur" x="-20%%" y="-20%%" width="140%%" height="140%%"><feGaussianBlur stdDeviation="%.1f"/></filter>'
        % (uid, max(w, h) / 90),
        '<filter id="%s-grain"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="%d"/>'
        '<feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.035 0"/></filter>' % (uid, seed),
    ]
    shapes = []
    angles = sorted(rnd.uniform(-35, 35) for _ in range(beams))
    reach = math.hypot(w, h) * 1.15
    for a in angles:
        spread = rnd.uniform(6, 11)
        pts = [(sx, sy)]
        for edge in (a - spread / 2, a + spread / 2):
            rad = math.radians(90 + edge)
            pts.append((sx + reach * math.cos(rad), sy + reach * math.sin(rad)))
        shapes.append('<polygon points="%s" fill="url(#%s-beam)" filter="url(#%s-blur)"/>'
                      % (" ".join("%.0f,%.0f" % p for p in pts), uid, uid))
    shapes.append('<ellipse cx="%.0f" cy="%.0f" rx="%.0f" ry="%.0f" fill="url(#%s-glow)"/>'
                  % (sx, max(sy, 0), w * 0.28, h * 0.22, uid))
    shapes.append('<rect width="%d" height="%d" filter="url(#%s-grain)"/>' % (w, h, uid))
    return "<defs>%s</defs>\n%s" % ("".join(defs), "\n".join(shapes))


def connections(w, h, seed=1, dots=34, dark=True, region=(0.5, 0.0, 1.0, 1.0)):
    """Dots joined to their nearest neighbours, with one Climb Orange cluster of three as the marker."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = region
    unit = max(w, h) / 1920 * 8
    pts = []
    tries = 0
    min_gap = math.sqrt(w * h * (x1 - x0) * (y1 - y0) / dots) * 0.55
    while len(pts) < dots and tries < dots * 200:
        tries += 1
        p = (rnd.uniform(x0, x1) * w, rnd.uniform(y0, y1) * h)
        if all(math.dist(p, q) > min_gap for q in pts):
            pts.append(p)
    colour, _ = _tone(dark, 0.2)
    lines, seen = [], set()
    for i, p in enumerate(pts):
        near = sorted(range(len(pts)), key=lambda j: math.dist(p, pts[j]))[1:3]
        for j in near:
            key = (min(i, j), max(i, j))
            if key not in seen:
                seen.add(key)
                q = pts[j]
                lines.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" stroke-opacity="0.16" stroke-width="%.1f"/>'
                             % (p[0], p[1], q[0], q[1], colour, max(1, unit * 0.25)))
    hub = max(range(len(pts)), key=lambda i: -math.dist(pts[i], (w * (x0 + x1) / 2, h * (y0 + y1) / 2)))
    cluster = [hub] + sorted(range(len(pts)), key=lambda j: math.dist(pts[hub], pts[j]))[1:3]
    for a, b in ((cluster[0], cluster[1]), (cluster[0], cluster[2]), (cluster[1], cluster[2])):
        lines.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" stroke-width="%.1f"/>'
                     % (pts[a][0], pts[a][1], pts[b][0], pts[b][1], ORANGE, max(1.5, unit * 0.4)))
    r = max(2.5, unit * 0.75)
    dots_svg = []
    for i, p in enumerate(pts):
        if i in cluster:
            dots_svg.append('<circle cx="%.0f" cy="%.0f" r="%.1f" fill="%s"/>' % (p[0], p[1], r * 1.5, ORANGE))
        else:
            dots_svg.append('<circle cx="%.0f" cy="%.0f" r="%.1f" fill="%s" fill-opacity="0.35"/>' % (p[0], p[1], r, colour))
    return "\n".join(lines + dots_svg)


def ascent(w, h, x, y, size, steps=5, colour=ORANGE, kind="steps"):
    """Rising steps or stacked chevrons, anchored bottom-left at (x, y). size is the overall height."""
    if kind == "chevrons":
        out = []
        gap = size / (steps + 1)
        half = gap * 1.6
        for i in range(steps):
            cy = y - i * gap
            out.append('<polyline points="%.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="none" stroke="%s" stroke-width="%.1f" '
                       'stroke-linecap="square" stroke-linejoin="miter"/>'
                       % (x, cy, x + half, cy - half * 0.9, x + 2 * half, cy, colour, gap * 0.38))
        return "\n".join(out)
    step_h = size / steps
    step_w = step_h * 2
    pts = [(x, y)]
    for i in range(steps):
        pts.append((x + i * step_w, y - (i + 1) * step_h))
        pts.append((x + (i + 1) * step_w, y - (i + 1) * step_h))
    pts += [(x + steps * step_w, y)]
    return '<polygon points="%s" fill="%s"/>' % (" ".join("%.0f,%.0f" % p for p in pts), colour)


def highlight_bar(x, y_baseline, width, cap, colour=ORANGE):
    """The orange bar that sits behind one highlighted word."""
    pad = cap * 0.25
    return '<rect x="%.0f" y="%.0f" width="%.0f" height="%.0f" fill="%s"/>' % (
        x - pad, y_baseline - cap * 1.05, width + 2 * pad, cap * 1.3, colour)


# The Ascent chevron rises 0.9 units for every unit across (see ascent()). Slabs and the peak share that slope so
# the corner marks, the summit line and the chevrons read as one family.
CHEVRON_SLOPE = 0.9


def slabs(w, h, corners=("tl",), length=None, thick=None, colour=ORANGE):
    """Angled Climb Orange slabs cut into one or two corners. Each slab is a band along the top or bottom edge whose
    inner end is cut at the chevron angle. Use one or two corners, never all four."""
    length = length or w * 0.24
    thick = thick or h * 0.075
    run = thick / CHEVRON_SLOPE
    out = []
    for c in corners:
        if c == "tl":
            pts = [(0, 0), (length, 0), (length - run, thick), (0, thick)]
        elif c == "tr":
            pts = [(w, 0), (w - length, 0), (w - length + run, thick), (w, thick)]
        elif c == "bl":
            pts = [(0, h), (length, h), (length - run, h - thick), (0, h - thick)]
        elif c == "br":
            pts = [(w, h), (w - length, h), (w - length + run, h - thick), (w, h - thick)]
        else:
            raise ValueError(c)
        out.append('<polygon points="%s" fill="%s"/>' % (" ".join("%.0f,%.0f" % p for p in pts), colour))
    return "\n".join(out)


def peak(w, h, x0=0.0, base=0.92, summit=(0.3, 0.7), seed=1, colour=ORANGE, opacity=1.0, stroke=None, end=None):
    """One contour line that walks in from the left edge, climbs to a summit and drops away: a mountain outline
    drawn as a single line. The approach wobbles like a contour; the last climb and the descent run at the
    chevron angle. Positions are fractions of the canvas."""
    rnd = random.Random(seed)
    unit = max(w, h) / 1920 * 8
    stroke = stroke or max(2.0, unit * 0.9)
    sx, sy = summit[0] * w, summit[1] * h
    by = base * h
    # Shoulder: a smaller false summit on the approach.
    rise = by - sy
    shx = sx - rise / CHEVRON_SLOPE * 0.95
    shy = sy + rise * 0.42
    dipx = shx + rise * 0.18 / CHEVRON_SLOPE
    dipy = shy + rise * 0.16
    start = (x0 * w, by)
    pts = [start]
    # Contour-like wander from the edge to the foot of the shoulder.
    foot_x = shx - (by - shy) / CHEVRON_SLOPE
    n = 6
    for i in range(1, n):
        t = i / n
        x = start[0] + (foot_x - start[0]) * t
        y = by - rnd.uniform(0, unit * 2.2) * math.sin(t * math.pi)
        pts.append((x, y))
    pts += [(foot_x, by), (shx, shy), (dipx, dipy), (sx, sy)]
    end_y = (end if end is not None else 1.08) * h
    pts.append((sx + (end_y - sy) / CHEVRON_SLOPE, end_y))
    d = "M" + " L".join("%.0f %.0f" % p for p in pts)
    return ('<path d="%s" fill="none" stroke="%s" stroke-opacity="%.2f" stroke-width="%.1f" '
            'stroke-linejoin="miter" stroke-linecap="square"/>' % (d, colour, opacity, stroke))


def grain(w, h, seed=1, uid="grain", opacity=0.07, freq=None):
    """Fine film grain for flat dark grounds (stage screens, video, print backgrounds). White noise at low
    opacity, so it lifts Dark Brown or Charcoal without shifting the hue. Keep it off small social text and email."""
    freq = freq or 0.85
    return ('<defs><filter id="%(u)s" x="0" y="0" width="100%%" height="100%%">'
            '<feTurbulence type="fractalNoise" baseFrequency="%(f).2f" numOctaves="2" seed="%(s)d" stitchTiles="stitch"/>'
            '<feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 %(a).3f 0"/></filter></defs>'
            '<rect width="%(w)d" height="%(h)d" filter="url(#%(u)s)"/>'
            % dict(u=uid, f=freq, s=seed, a=opacity, w=w, h=h))
