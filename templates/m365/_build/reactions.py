"""Branded meeting reactions for Teams Premium: Like, Heart, Applause, Laugh and Surprised, each a static 100x100
PNG and a 51-frame animated sprite (100x5100, 24 fps, frames 0 to 9 fade in, key moment at frame 23, frames 41 to
50 fade out), as Microsoft asks for every reaction a theme replaces.

Two sets share one drawing each:
- orange: a Climb Orange disc with the drawing in Dark Brown (6.06:1).
- dark: a Dark Brown disc ringed in Climb Orange with the drawing in Climb Orange (6.06:1).

Like, Heart and Applause use the house drawings (thumbs-up, heart, applause). Laugh and Surprised turn the disc into
a face. Each reaction is rendered as layers at 400x400 (disc, drawing, effects) and the frames are composed here.
"""
import math

from PIL import Image

DB, OR, TI = "#1E0F05", "#E8712A", "#F2AE86"
SIZE = 400
DISC = 300            # disc diameter inside the 400 frame, so effects have room around it
REACTIONS = ("like", "heart", "applause", "laugh", "surprised")
SETS = {"orange": dict(disc=OR, ink=DB, ring=None, fx=OR), "dark": dict(disc=DB, ink=OR, ring=OR, fx=OR)}

FACES = {
    # Laugh: closed, upturned eyes and a wide open D mouth with a tongue.
    "laugh": ('<path d="M60 82 q16 -22 32 0 M108 82 q16 -22 32 0" fill="none" stroke="{ink}" stroke-width="13" '
              'stroke-linecap="round"/>'
              '<path d="M52 104 H148 Q146 168 100 168 Q54 168 52 104 Z" fill="{ink}"/>'
              '<path d="M78 150 Q100 136 122 150 Q112 164 100 164 Q88 164 78 150 Z" fill="{disc}" opacity=".55"/>'),
    # Surprised: raised brows, round eyes and an O mouth.
    "surprised": ('<path d="M56 56 q18 -14 36 -4 M108 52 q18 -10 36 4" fill="none" stroke="{ink}" stroke-width="11" '
                  'stroke-linecap="round"/>'
                  '<ellipse cx="76" cy="88" rx="13" ry="16" fill="{ink}"/><ellipse cx="124" cy="88" rx="13" ry="16" fill="{ink}"/>'
                  '<ellipse cx="100" cy="142" rx="22" ry="28" fill="{ink}"/>'),
}
HOUSE = {"like": "thumbs-up", "heart": "heart", "applause": "applause"}


def _wrap(body):
    return '<svg class="abs" style="left:0;top:0" viewBox="0 0 %d %d" width="%d" height="%d">%s</svg>' % (
        SIZE, SIZE, SIZE, SIZE, body)


def pages(add, I):
    """Add the layer pages: per set a disc, per set and reaction a drawing, and the shared effect layers."""
    c = SIZE / 2
    for key, s in SETS.items():
        ring = ('<circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" stroke-width="16"/>' % (c, c, DISC / 2 - 8, s["ring"])
                if s["ring"] else "")
        add("rx_%s_disc" % key, SIZE, SIZE, [_wrap('<circle cx="%d" cy="%d" r="%d" fill="%s"/>%s' % (c, c, DISC / 2, s["disc"], ring))],
            transparent=True)
        for r in REACTIONS:
            if r in FACES:
                body = FACES[r].format(ink=s["ink"], disc=s["disc"])
                d = DISC * 0.86
                layer = ('<svg class="abs" style="left:%.0fpx;top:%.0fpx" viewBox="0 0 200 200" width="%.0f" height="%.0f">%s</svg>'
                         % (c - d / 2, c - d / 2, d, d, body))
            else:
                d = DISC * 0.74
                layer = I.place(HOUSE[r], c - d / 2, c - d / 2, d, weight=2.0, ink=s["ink"], ground=s["disc"])
            add("rx_%s_%s" % (key, r), SIZE, SIZE, [layer], transparent=True)
    # Effects: a burst of short rays around the disc, and a small heart.
    rays = []
    for i in range(10):
        a = math.radians(i * 36 + 18)
        r0, r1 = DISC / 2 + 18, DISC / 2 + 46
        rays.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" stroke-width="14" stroke-linecap="round"/>'
                    % (c + r0 * math.cos(a), c + r0 * math.sin(a), c + r1 * math.cos(a), c + r1 * math.sin(a), OR))
    add("rx_fx_burst", SIZE, SIZE, [_wrap("".join(rays))], transparent=True)
    add("rx_fx_heart", SIZE, SIZE, [_wrap('<path d="M200 250 C120 190 140 130 180 140 C192 143 198 152 200 160 '
                                          'C202 152 208 143 220 140 C260 130 280 190 200 250 Z" fill="%s"/>' % OR)],
        transparent=True)


def _ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def _bump(f, centre, width):
    return math.exp(-((f - centre) / float(width)) ** 2)


def _place(frame, layer, scale=1.0, rot=0.0, dx=0.0, dy=0.0, alpha=1.0):
    if alpha <= 0.01:
        return
    im = layer
    if rot:
        im = im.rotate(rot, resample=Image.BICUBIC, center=(SIZE / 2, SIZE / 2))
    if abs(scale - 1.0) > 0.001:
        k = max(1, int(SIZE * scale))
        im = im.resize((k, k), Image.LANCZOS)
    if alpha < 1.0:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    off = (int((SIZE - im.width) / 2 + dx), int((SIZE - im.height) / 2 + dy))
    if im.width > SIZE:
        crop = ((im.width - SIZE) // 2 - int(dx), (im.height - SIZE) // 2 - int(dy))
        im = im.crop((crop[0], crop[1], crop[0] + SIZE, crop[1] + SIZE))
        off = (0, 0)
    frame.alpha_composite(im, off)


def frame(kind, f, disc, ink, burst, heart):
    """One 400x400 frame of a reaction at frame f (0 to 50)."""
    fr = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    if f < 10:
        a, s = _ease((f + 1) / 10.0), 0.55 + 0.45 * _ease((f + 1) / 10.0)
    elif f > 40:
        a, s = 1 - _ease((f - 40) / 10.0), 1 - 0.15 * _ease((f - 40) / 10.0)
    else:
        a, s = 1.0, 1.0
    rot, irot, iscale, dy, fx = 0.0, 0.0, 1.0, 0.0, 0.0
    if kind == "like":
        # The thumb swings up from tilted and lands with a bounce at the key moment.
        t = (f - 4) / 19.0
        irot = 28 * (1 - _ease(t)) - 8 * _bump(f, 23, 3) if f < 30 else 0
        iscale = 1 + 0.18 * _bump(f, 23, 3)
        fx = _bump(f, 25, 4)
    elif kind == "heart":
        # Two beats, the first at the key moment; a small heart floats up.
        iscale = 1 + 0.22 * _bump(f, 23, 2.2) + 0.14 * _bump(f, 30, 2.2)
        fx = _bump(f, 26, 7)
    elif kind == "applause":
        # Hands clap: quick alternating tilts, strongest at the key moment, a burst on the big clap.
        amp = 14 * max(_bump(f, 23, 9), 0.0) if 10 <= f <= 40 else 0
        irot = amp * math.sin((f - 10) * math.pi / 3)
        iscale = 1 + 0.12 * _bump(f, 23, 2.5)
        fx = _bump(f, 23, 3)
    elif kind == "laugh":
        # The whole face bounces and rocks.
        env = _bump(f, 23, 10) if 8 <= f <= 42 else 0
        dy = -26 * env * abs(math.sin((f - 8) * math.pi / 6))
        rot = 9 * env * math.sin((f - 8) * math.pi / 6)
        fx = 0
    elif kind == "surprised":
        # A jump in size at the key moment with a burst, then a small shake while it settles.
        s *= 1 + 0.2 * _bump(f, 23, 2.6)
        rot = 5 * math.sin(f * 1.7) * _bump(f, 28, 4)
        fx = _bump(f, 24, 3)
    if fx > 0.02 and kind in ("like", "applause", "surprised"):
        _place(fr, burst, scale=s * (0.92 + 0.12 * fx), alpha=a * fx)
    _place(fr, disc, scale=s, rot=rot, dy=dy, alpha=a)
    _place(fr, ink, scale=s * iscale, rot=rot + irot, dy=dy, alpha=a)
    if fx > 0.02 and kind == "heart":
        # Two small hearts float up past the top corners, in front of the disc.
        rise = 30 * max(0.0, (f - 18) / 27.0)
        _place(fr, heart, scale=0.36, dx=132, dy=-100 - rise, alpha=a * fx)
        _place(fr, heart, scale=0.28, dx=-138, dy=-80 - rise * 0.8, alpha=a * fx * 0.85)
    return fr


def compose(png, out):
    """Write <set>/<reaction>_static_100x100.png and <set>/<reaction>_animated_100x5100.png for both sets."""
    load = lambda n: Image.open(png / (n + ".png")).convert("RGBA")
    burst, heart = load("rx_fx_burst"), load("rx_fx_heart")
    written = []
    for key in SETS:
        disc = load("rx_%s_disc" % key)
        d = out / key
        d.mkdir(parents=True, exist_ok=True)
        for r in REACTIONS:
            ink = load("rx_%s_%s" % (key, r))
            still = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
            still.alpha_composite(disc)
            still.alpha_composite(ink)
            # The static reaction fills the frame a little more than the animated one at rest.
            still = still.crop((24, 24, SIZE - 24, SIZE - 24)).resize((100, 100), Image.LANCZOS)
            still.save(d / ("%s_static_100x100.png" % r), optimize=True)
            sheet = Image.new("RGBA", (100, 5100), (0, 0, 0, 0))
            for f in range(51):
                sheet.alpha_composite(frame(r, f, disc, ink, burst, heart).resize((100, 100), Image.LANCZOS), (0, f * 100))
            sheet.save(d / ("%s_animated_100x5100.png" % r), optimize=True)
            written += [d / ("%s_static_100x100.png" % r), d / ("%s_animated_100x5100.png" % r)]
    return written
