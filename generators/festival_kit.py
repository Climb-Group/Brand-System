"""Festival kit templates: name cards, share tiles, affiliate tickets, the photo pull-up banner, document covers and
meeting table signs. Called from catalogue.assets(); every entry is a normal catalogue asset dict, so page(),
the copy checker and render.mjs treat it like any other.

Ideas carried over from the Climb26 design tool review (docs only, never the artwork): the pill bar across a name,
angled corner slabs, a summit line, fine grain, one share layout where only the verb changes, a ticket card that
carries an affiliate code, a photo checkerboard banner with a QR at eye level, and table signs where the number is
the hero. All of it is drawn here in the ClimbUK style: Dark Brown ground, Montserrat 800 uppercase with one orange
word, Climb Orange stickers, ticket cards with stub notches, and real Climb26 photos faded to Dark Brown.

Placeholders sit in braces ({Speaker name}, {Your code}); the copy checker sees them as plain words.
"""
import html
import random
import re

import motifs as M

DB, CH, OR, TI, LG, WH = "#1E0F05", "#242322", "#E8712A", "#F2AE86", "#E9E9E9", "#FFFFFF"
DB_RGB = "30,15,5"
URL = "climb-uk.com"

ITALIC_CSS = """
@font-face{font-family:Montserrat;font-weight:700;font-style:italic;src:url('%(f)s/montserrat-latin-700-italic.woff2')}
@font-face{font-family:Montserrat;font-weight:800;font-style:italic;src:url('%(f)s/montserrat-latin-800-italic.woff2')}
@font-face{font-family:'Open Sans';font-weight:600;font-style:italic;src:url('%(f)s/open-sans-latin-600-italic.woff2')}
"""

BASE_CSS = """
.disp{font-family:Montserrat;font-weight:800;text-transform:uppercase;line-height:1.0;letter-spacing:-0.01em;margin:0;color:#fff}
.disp .o{color:#E8712A}
.disp em,.role em{font-style:italic}
.fit{white-space:nowrap}
.body{font-family:'Open Sans';font-weight:600}
.lab{font-family:Montserrat;font-weight:700;text-transform:uppercase;letter-spacing:.14em}
.abs{position:absolute}
.sticker{position:absolute;background:#E8712A;color:#1E0F05;font-family:Montserrat;font-weight:800;text-transform:uppercase;
letter-spacing:.04em;line-height:1;transform:rotate(-3deg);transform-origin:left bottom;white-space:nowrap}
.ph{position:absolute;background-size:cover;background-repeat:no-repeat}
.ph::after{content:"";position:absolute;inset:0}
.pill-host{position:relative;display:inline-block}
.pill{position:absolute;top:.15em;height:.23em;border-radius:.115em;background:#E8712A;left:17%;width:31%}
.chip{display:flex;align-items:center;justify-content:center;background:#FFFFFF;color:#242322;font-family:'Open Sans';
font-weight:600;border-radius:14px}
"""

# Shrink every .fit element until it fits its box (width set inline); lines in one .fitgroup share the smallest size.
FIT_JS = """<script>document.fonts.ready.then(function(){
function fit(e){var s=parseFloat(getComputedStyle(e).fontSize);while(e.scrollWidth>e.clientWidth+1&&s>8){s-=2;e.style.fontSize=s+'px';}return s;}
document.querySelectorAll('.fitgroup').forEach(function(g){var ls=g.querySelectorAll('.fit'),m=1e9;
ls.forEach(function(e){m=Math.min(m,fit(e));});ls.forEach(function(e){e.style.fontSize=m+'px';});});
document.querySelectorAll('.fit:not(.fitgroup .fit)').forEach(fit);document.body.dataset.fit='1';});</script>"""


def rich(text):
    """[[word]] -> orange, *word* -> italic. Escapes everything else."""
    t = html.escape(text, quote=False)
    t = re.sub(r"\[\[(.+?)\]\]", r'<span class="o">\1</span>', t)
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", t)


def plain(text):
    return re.sub(r"\[\[|\]\]|\*", "", text)


def svg(w, h, body, style=""):
    return ('<svg class="abs" style="left:0;top:0;%s" viewBox="0 0 %d %d" width="%d" height="%d">%s</svg>'
            % (style, w, h, w, h, body))


def photo(C, name, x, y, w, h, pos="center", fade="", extra=""):
    """A real photo cut to cover, with a fade layered on top. fade is a CSS background list ending in Dark Brown."""
    url = (C.PHOTOS / (name + ".jpg")).as_uri()
    return ('<div class="ph" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx;background-image:url(\'%s\');'
            'background-position:%s;%s"><div class="abs" style="inset:0;background:%s"></div></div>'
            % (x, y, w, h, url, pos, extra, fade or "none"))


def to_db(direction, a=0, b=100, start_alpha=0.0):
    """Linear fade to solid Dark Brown, from a% to b% in the given direction."""
    return ("linear-gradient(%s, rgba(%s,%.2f) %d%%, rgba(%s,1) %d%%)" % (direction, DB_RGB, start_alpha, a, DB_RGB, b))


def ticket_shape(w, h, tear, orient="v", r=None, notch=None, fill=CH, stroke=None, stub_fill=None, dash=None, uid="t"):
    """A ticket card with semicircle stub notches at the tear line and a dashed tear line. orient 'v': stub on the
    right, tear line at x=tear. orient 'h': stub at the bottom, tear line at y=tear."""
    r = r if r is not None else min(w, h) * 0.06
    n = notch if notch is not None else min(w, h) * 0.06
    if orient == "v":
        d = ("M%(r)s 0 L%(a)s 0 A%(n)s %(n)s 0 0 0 %(b)s 0 L%(wr)s 0 A%(r)s %(r)s 0 0 1 %(w)s %(r)s L%(w)s %(hr)s "
             "A%(r)s %(r)s 0 0 1 %(wr)s %(h)s L%(b)s %(h)s A%(n)s %(n)s 0 0 0 %(a)s %(h)s L%(r)s %(h)s "
             "A%(r)s %(r)s 0 0 1 0 %(hr)s L0 %(r)s A%(r)s %(r)s 0 0 1 %(r)s 0 Z") % dict(
            r=r, n=n, a=tear - n, b=tear + n, w=w, h=h, wr=w - r, hr=h - r)
        line = (tear, n * 1.6, tear, h - n * 1.6)
        stub_rect = (tear, 0, w - tear, h)
    else:
        d = ("M%(r)s 0 L%(wr)s 0 A%(r)s %(r)s 0 0 1 %(w)s %(r)s L%(w)s %(a)s A%(n)s %(n)s 0 0 0 %(w)s %(b)s "
             "L%(w)s %(hr)s A%(r)s %(r)s 0 0 1 %(wr)s %(h)s L%(r)s %(h)s A%(r)s %(r)s 0 0 1 0 %(hr)s L0 %(b)s "
             "A%(n)s %(n)s 0 0 0 0 %(a)s L0 %(r)s A%(r)s %(r)s 0 0 1 %(r)s 0 Z") % dict(
            r=r, n=n, a=tear - n, b=tear + n, w=w, h=h, wr=w - r, hr=h - r)
        line = (n * 1.6, tear, w - n * 1.6, tear)
        stub_rect = (0, tear, w, h - tear)
    sw = max(2, min(w, h) * 0.006)
    dash = dash or sw * 4
    out = ['<path d="%s" fill="%s"/>' % (d, fill)]
    if stub_fill:
        out.append('<clipPath id="%s-stub"><rect x="%.0f" y="%.0f" width="%.0f" height="%.0f"/></clipPath>'
                   '<path d="%s" fill="%s" clip-path="url(#%s-stub)"/>' % ((uid,) + stub_rect + (d, stub_fill, uid)))
    if stroke:
        out.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, stroke, sw))
    tone = DB if stub_fill == OR else "rgba(255,255,255,.45)"
    out.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" stroke-width="%.1f" stroke-dasharray="%.0f %.0f"/>'
               % (line + (tone, sw, dash, dash * 0.8)))
    return "".join(out)


def ticket(x, y, w, h, tear, main_html, stub_html, orient="v", pad=None, **kw):
    pad = pad if pad is not None else min(w, h) * 0.09
    shape = ('<svg class="abs" style="left:0;top:0;overflow:visible" viewBox="0 0 %d %d" width="%d" height="%d">%s</svg>'
             % (w, h, w, h, ticket_shape(w, h, tear, orient, **kw)))
    if orient == "v":
        main_box = "left:%dpx;top:0;width:%dpx;height:%dpx" % (pad, tear - 2 * pad, h)
        stub_box = "left:%dpx;top:0;width:%dpx;height:%dpx" % (tear + pad * 0.7, w - tear - 1.4 * pad, h)
    else:
        main_box = "left:%dpx;top:%dpx;width:%dpx;height:%dpx" % (pad, pad, w - 2 * pad, tear - 2 * pad)
        stub_box = "left:%dpx;top:%dpx;width:%dpx;height:%dpx" % (pad, tear + pad * 0.7, w - 2 * pad, h - tear - 1.4 * pad)
    flex = "display:flex;flex-direction:column;justify-content:center"
    return ('<div class="abs" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx">%s'
            '<div class="abs" style="%s;%s">%s</div><div class="abs" style="%s;%s">%s</div></div>'
            % (x, y, w, h, shape, main_box, flex, main_html, stub_box, flex, stub_html))


def qr(size, seed=7, label="QR"):
    """A neutral QR-like square: three finder marks and a module field in Charcoal on White, labelled QR in the
    middle so nobody mistakes it for a working code. Swap for the real code at print time."""
    rnd = random.Random(seed)
    n = 25
    q = size / (n + 4)
    out = ['<rect width="%.0f" height="%.0f" rx="%.0f" fill="#FFFFFF"/>' % (size, size, q * 0.8)]

    def cell(i, j):
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>' % ((i + 2) * q, (j + 2) * q, q + 0.5, q + 0.5, CH))

    def finder(i0, j0):
        for i in range(7):
            for j in range(7):
                if i in (0, 6) or j in (0, 6) or (2 <= i <= 4 and 2 <= j <= 4):
                    cell(i0 + i, j0 + j)

    finder(0, 0)
    finder(n - 7, 0)
    finder(0, n - 7)
    for i in range(n):
        for j in range(n):
            in_finder = (i < 8 and j < 8) or (i >= n - 8 and j < 8) or (i < 8 and j >= n - 8)
            in_label = 8 <= i <= n - 9 and 9 <= j <= n - 10
            if not in_finder and not in_label and rnd.random() < 0.45:
                cell(i, j)
    lw, lh = q * (n - 16), q * (n - 18)
    out.append('<rect x="%.0f" y="%.0f" width="%.0f" height="%.0f" rx="%.0f" fill="#FFFFFF" stroke="%s" stroke-width="%.1f"/>'
               % ((size - lw) / 2, (size - lh) / 2, lw, lh, q * 0.6, CH, q * 0.25))
    out.append('<text x="%.0f" y="%.0f" text-anchor="middle" dominant-baseline="central" font-family="Montserrat" '
               'font-weight="800" font-size="%.0f" fill="%s">%s</text>' % (size / 2, size / 2 + q * 0.1, lh * 0.62, CH, label))
    return '<svg viewBox="0 0 %.0f %.0f" width="%.0f" height="%.0f" style="display:block">%s</svg>' % (
        size, size, size, size, "".join(out))


def chevron(size, colour=OR):
    """One Ascent chevron as a bullet, pointing up and to the right like the climb."""
    s = size
    return ('<svg viewBox="0 0 %.0f %.0f" width="%.0f" height="%.0f" style="flex:none;display:block">'
            '<polyline points="%.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linecap="square" stroke-linejoin="miter"/></svg>'
            % (s, s, s, s, s * 0.22, s * 0.3, s * 0.62, s * 0.5, s * 0.22, s * 0.7, colour, s * 0.2))


def logo_img(C, brand, variant, x, y, w, extra=""):
    return ('<img class="abs" src="%s" style="left:%.0fpx;top:%.0fpx;width:%.0fpx;height:auto;%s" alt="">'
            % (C.logo(brand, variant), x, y, w, extra))


def grain_layer(w, h, seed, opacity=0.09):
    return svg(w, h, M.grain(w, h, seed=seed, uid="g%d" % seed, opacity=opacity), "pointer-events:none")


def css(C, extra=""):
    return ITALIC_CSS % {"f": (C.HERE / "fonts").as_uri()} + BASE_CSS + extra


# ---------------------------------------------------------------- Stage and screens

def name_block(first, last, size, width, pill=True, role=None, role_px=None, gap=None):
    """Two-line uppercase name sharing one size, pill bar across the top of the first line, role line under."""
    p = '<span class="pill"></span>' if pill else ""
    role_html = ('<div class="role lab" style="font-size:%dpx;letter-spacing:.06em;color:#F2AE86;margin-top:%dpx;'
                 'line-height:1.2">%s</div>' % (role_px, gap or role_px * 0.6, rich(role)) if role else "")
    return ('<div class="fitgroup"><div class="disp fit" style="font-size:%dpx;line-height:.92;width:%dpx">'
            '<span class="pill-host">%s%s</span></div>'
            '<div class="disp fit" style="font-size:%dpx;line-height:.92;width:%dpx">%s</div></div>%s'
            % (size, width, html.escape(first), p, size, width, html.escape(last), role_html))


ROLE = "{Role}, *{Company}*"


def name_card(C, with_photo=False):
    w, h = 3840, 2160
    parts = []
    if with_photo:
        px = int(w * 0.46)
        parts.append(photo(C, "climb_stage_region", px, 0, w - px, h, pos="60% 30%",
                           fade=to_db("to left", 45, 100) + ", linear-gradient(to top, rgba(%s,.9) 0%%, rgba(%s,0) 24%%)"
                           % (DB_RGB, DB_RGB)))
        parts.append(svg(w, h, M.slabs(w, h, corners=("br",), length=w * 0.2, thick=h * 0.07)))
        text_w = int(w * 0.47)
        sticker = '<div class="sticker" style="left:%dpx;top:%dpx;font-size:64px;padding:22px 34px">Speaker</div>' % (
            w * 0.065, h * 0.235)
    else:
        parts.append(svg(w, h, M.slabs(w, h, corners=("tr",), length=w * 0.24, thick=h * 0.075)))
        text_w = int(w * 0.84)
        sticker = ""
    parts.append(grain_layer(w, h, 81))
    parts.append(logo_img(C, "Climb27", "reversed-dark", w * 0.065, h * 0.09, w * 0.15))
    parts.append(sticker)
    parts.append('<div class="abs" style="left:%dpx;top:%dpx">%s</div>'
                 % (w * 0.065, h * (0.36 if with_photo else 0.37),
                    name_block("{First name}", "{Last name}", 420 if not with_photo else 300, text_w,
                               role=ROLE, role_px=110 if not with_photo else 96)))
    parts.append(FIT_JS)
    key = "speaker-photo" if with_photo else "speaker"
    return dict(name="climb27_name-card_%s_%dx%d" % (key, w, h), group="Stage and screens", brand="Climb27",
                motif=None, w=w, h=h, extra_html="\n".join(parts), extra_css=css(C),
                copy=["Speaker", "{First name}", "{Last name}", plain(ROLE)])


def lower_third_v2(C):
    w, h = 3840, 2160
    ph, pw = 400, 2400
    x, y = int(w * 0.06), int(h * 0.9 - ph)
    slab = M.slabs(pw, ph, corners=("tl",), length=260, thick=34)
    logo_w = 470
    inner = ('<div class="abs" style="left:0;top:0;width:%dpx;height:%dpx;background:%s;border-radius:28px;overflow:hidden">'
             '%s<div class="abs" style="left:110px;top:0;height:%dpx;display:flex;flex-direction:column;justify-content:center">'
             '<div class="disp fit" style="font-size:170px;line-height:.92;width:%dpx"><span class="pill-host">{Speaker name}'
             '<span class="pill"></span></span></div>'
             '<div class="role lab" style="font-size:66px;letter-spacing:.06em;color:#F2AE86;margin-top:30px">%s</div></div>'
             '<div class="abs" style="right:%dpx;top:90px;bottom:90px;width:6px;background:rgba(255,255,255,.18)"></div>'
             '%s</div>'
             % (pw, ph, DB, svg(pw, ph, slab), ph, pw - 110 - logo_w - 200, rich(ROLE), logo_w + 130,
                logo_img(C, "Climb27", "reversed-dark", pw - logo_w - 70, (ph - logo_w * C.logo_ratio("Climb27", "reversed-dark")) / 2, logo_w)))
    return dict(name="climb27_lower-third-v2_speaker_%dx%d" % (w, h), group="Stage and screens", brand="Climb27",
                motif=None, w=w, h=h, transparent=True,
                extra_html='<div class="abs" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx">%s</div>%s'
                % (x, y, pw, ph, inner, FIT_JS),
                extra_css=css(C), copy=["{Speaker name}", plain(ROLE)])


# ---------------------------------------------------------------- Social

SHARE = [
    # key, sticker, line 1, line 2 (the verb is the orange word; only it changes)
    ("attending", "Attendee", "I'm [[attending]]", "*Climb27*"),
    ("speaking", "Speaker", "I'm [[speaking]]", "at *Climb27*"),
    ("exhibiting", "Exhibitor", "I'm [[exhibiting]]", "at *Climb27*"),
    ("partnering", "Partner", "We're [[partnering]]", "at *Climb27*"),
]


def small_ticket(C, x, y, w, h, uid):
    """Foot ticket: the edition and the dates in the main body, the URL in the stub."""
    lw = h * 0.36 / C.logo_ratio("Climb27", "reversed-dark")
    main = ('<div style="display:flex;align-items:center;gap:%dpx"><img src="%s" style="width:%dpx;display:block" alt="">'
            '<span class="body" style="font-size:%dpx;color:#fff;line-height:1.25;white-space:nowrap">%s</span></div>'
            % (w * 0.03, C.logo("Climb27", "reversed-dark"), lw, w * 0.029, C.DATES))
    stub = ('<div class="lab" style="font-size:%dpx;color:#1E0F05;text-align:center;letter-spacing:.04em;white-space:nowrap">'
            '%s</div>' % (w * 0.026, URL))
    return ticket(x, y, w, h, w * 0.7, main, stub, fill=CH, stroke="rgba(255,255,255,.16)", stub_fill=OR, uid=uid,
                  pad=h * 0.2)


def share_tile(C, key, label, l1, l2, story=False):
    w, h = (1080, 1920) if story else (1080, 1350)
    top = 250 if story else 0
    ph = 1080 if story else 820
    top_fade = ("rgba(%s,.85) 0%%, rgba(%s,.6) 20%%, rgba(%s,0) 34%%" if story else
                "rgba(%s,.75) 0%%, rgba(%s,.35) 14%%, rgba(%s,0) 26%%") % (DB_RGB, DB_RGB, DB_RGB)
    parts = [photo(C, "climb_awards_winners", 0, 0, w, ph, pos="52% 25%",
                   fade="linear-gradient(to bottom, %s, rgba(%s,0) 55%%, rgba(%s,1) 96%%)" % (top_fade, DB_RGB, DB_RGB))]
    if not story:
        # Stories carry the edition mark on the foot ticket only, so nothing sits on the busy middle of the photo.
        parts.append(logo_img(C, "Climb27", "reversed-dark", 64, top + 64, 300))
    parts.append('<div class="sticker" style="left:64px;top:%dpx;font-size:44px;padding:16px 24px">%s</div>'
                 % (ph - 150, label))
    parts.append('<div class="abs fitgroup" style="left:64px;top:%dpx">'
                 '<h1 class="disp fit" style="font-size:118px;width:952px">%s</h1>'
                 '<h1 class="disp fit" style="font-size:118px;width:952px">%s</h1></div>'
                 % (ph - 40, rich(l1), rich(l2)))
    parts.append('<div class="abs body" style="left:64px;top:%dpx;font-size:34px;color:#F2AE86">{Your name}, {Company}</div>'
                 % (ph + 218))
    ty = (1920 - 340 - 150) if story else (h - 56 - 140)
    parts.append(small_ticket(C, 64, ty, 952, 140 if not story else 150, "st"))
    parts.append(FIT_JS)
    fmt = "story" if story else "post"
    return dict(name="climb27_share-%s_%s_%dx%d" % (fmt, key, w * 2, h * 2), group="Social", brand="Climb27", scale=2,
                motif=None, w=w, h=h, extra_html="\n".join(parts), extra_css=css(C),
                copy=[label, plain(l1), plain(l2), "{Your name}, {Company}", C.DATES, URL])


AFF_HEAD = "Book your Climb27 ticket with my [[code]]"


def affiliate(C, story=False):
    w, h = (1080, 1920) if story else (1080, 1350)
    top = 250 if story else 0
    ph = 900 if story else 640
    parts = [photo(C, "climb_crowd_wide", 0, 0, w, ph, pos="center 40%",
                   fade="linear-gradient(to bottom, rgba(%s,.8) 0%%, rgba(%s,.55) %d%%, rgba(%s,.15) %d%%, rgba(%s,1) 96%%)"
                   % (DB_RGB, DB_RGB, 34 if story else 14, DB_RGB, 48 if story else 30, DB_RGB))]
    parts.append(logo_img(C, "Climb27", "reversed-dark", 64, top + 64, 280))
    tx, tw = 90, 900
    ty = top + 330 if story else 300
    th = 1180 if story else 980
    tear = th - (320 if story else 300)
    main = ('<div class="lab" style="font-size:26px;color:#F2AE86">Climb27 Affiliate Programme</div>'
            '<div class="chip" style="width:%dpx;height:%dpx;margin:34px 0 40px;font-size:34px;outline:4px dashed #242322;'
            'outline-offset:-18px">{Affiliate logo}</div>'
            '<h1 class="disp" style="font-size:%dpx;line-height:1.02">%s</h1>'
            '<div class="body" style="font-size:%dpx;color:#F2AE86;margin-top:26px">%s</div>'
            % (520 if story else 440, 200 if story else 170, 84 if story else 68, rich(AFF_HEAD), 34 if story else 30,
               C.DATES))
    stub = ('<div style="display:flex;align-items:baseline;justify-content:space-between">'
            '<div class="lab" style="font-size:26px;color:#1E0F05">My code</div>'
            '<div class="lab" style="font-size:24px;color:#1E0F05;letter-spacing:.06em;white-space:nowrap">Use it at %s</div></div>'
            '<div class="disp fit" style="font-size:%dpx;width:%dpx;box-sizing:border-box;color:#1E0F05;margin-top:18px;'
            'border:5px dashed #1E0F05;border-radius:16px;padding:22px 30px 16px">{Your code}</div>'
            % (URL, 92 if story else 84, tw - 140))
    parts.append(ticket(tx, ty, tw, th, tear, main, stub, orient="h", fill=CH, stroke="rgba(255,255,255,.16)",
                        stub_fill=OR, uid="aff", pad=70, r=36, notch=40))
    parts.append(FIT_JS)
    parts.append('<div class="sticker" style="left:%dpx;top:%dpx;font-size:46px;padding:16px 26px">Just joined</div>'
                 % (tx - 18, ty - 46))
    fmt = "story" if story else "post"
    return dict(name="climb27_affiliate-%s_just-joined_%dx%d" % (fmt, w * 2, h * 2), group="Social", brand="Climb27",
                scale=2, motif=None, w=w, h=h, extra_html="\n".join(parts), extra_css=css(C),
                copy=["Just joined", "Climb27 Affiliate Programme", "{Affiliate logo}", plain(AFF_HEAD), C.DATES,
                      "My code", "{Your code}", "Use it at " + URL])


def speaker_announcement(C):
    w, h = 1080, 1350
    ph = 760
    parts = [photo(C, "climb_stage_region", 0, 0, w, ph, pos="68% 30%",
                   fade="linear-gradient(to bottom, rgba(%s,1) 0%%, rgba(%s,.97) 15%%, rgba(%s,0) 34%%, rgba(%s,0) 50%%, "
                   "rgba(%s,1) 97%%)" % (DB_RGB, DB_RGB, DB_RGB, DB_RGB, DB_RGB))]
    parts.append(svg(w, h, M.slabs(w, h, corners=("br",), length=w * 0.3, thick=h * 0.035)))
    parts.append(logo_img(C, "Climb27", "reversed-dark", 64, 64, 300))
    parts.append('<div class="sticker" style="left:64px;top:%dpx;font-size:40px;padding:14px 22px">Speaker</div>' % (ph - 130))
    parts.append('<div class="abs" style="left:64px;top:%dpx">%s</div>'
                 % (ph - 20, name_block("{First name}", "{Last name}", 150, 952, role=ROLE, role_px=34, gap=26)))
    parts.append('<div class="abs body" style="left:64px;top:%dpx;width:900px;font-size:32px;line-height:1.35;color:#fff">'
                 '{Session title}<br><span style="color:#F2AE86">%s</span></div>' % (ph + 360, C.DATES))
    parts.append(FIT_JS)
    return dict(name="climb27_speaker-announcement_post_%dx%d" % (w * 2, h * 2), group="Social", brand="Climb27",
                scale=2, motif=None, w=w, h=h, extra_html="\n".join(parts), extra_css=css(C),
                copy=["Speaker", "{First name}", "{Last name}", plain(ROLE), "{Session title}", C.DATES])


# ---------------------------------------------------------------- Print and merch

BANNER_LINES = [
    # photo, panel colour, line with the emphasis word in [[ ]]
    ("climb_crowd_wide", "brown", "Find [[investors]] looking for real deal flow"),
    ("climb_consultants_expert", "orange", "[[Main stage moments]], roundtables and Investor Speed Networking"),
    ("climb_drinks_reception", "brown", "Two days with the [[people]] who move businesses forward"),
]
BANNER_HEAD = "Your business. *Bigger* [[stage]]."


def pullup_v2(C):
    """850x2000mm at 100 dpi. Top: logo, dates, display line. Eye level: QR on a ticket card. Middle: photo
    checkerboard with chevron bullets. URL band above the cassette line; nothing in the bottom 300mm."""
    w, h = 3346, 7874
    mm = h / 2000
    safe = int(h - 300 * mm)
    m = int(w * 0.08)
    parts = [svg(w, h, M.contours(w, h, seed=91, rings=10, dark=True, marker=False, cx=0.82, cy=1.02))]
    lw = w * 0.56
    parts.append(logo_img(C, "Climb27", "reversed-dark", m, 230, lw))
    parts.append('<div class="abs body" style="left:%dpx;top:%dpx;font-size:110px;color:#F2AE86">%s</div>'
                 % (m, 230 + lw * C.logo_ratio("Climb27", "reversed-dark") + 70, C.TAGLINE))
    parts.append('<h1 class="abs disp" style="left:%dpx;top:%dpx;width:%dpx;font-size:228px">%s</h1>'
                 % (m, 1020, w - 2 * m, rich(BANNER_HEAD)))
    # Eye level: 1.4 to 1.6m from the floor, so 400 to 600mm from the top.
    ty, th = int(1520), int(860)
    qs = 560
    main = ('<div class="lab" style="font-size:72px;color:#F2AE86">Tickets</div>'
            '<div class="disp" style="font-size:190px;margin:26px 0 30px;text-transform:none">%s</div>'
            '<div class="body" style="font-size:84px;color:#fff;line-height:1.3">%s</div>' % (URL, C.DATES))
    stub = ('<div style="display:flex;flex-direction:column;align-items:center">%s'
            '<div class="lab" style="font-size:64px;color:#1E0F05;margin-top:40px;letter-spacing:.08em">Scan for <em>tickets</em></div></div>'
            % qr(qs))
    parts.append(ticket(m, ty, w - 2 * m, th, (w - 2 * m) - 900, main, stub, fill=CH, stroke="rgba(255,255,255,.16)",
                        stub_fill=OR, uid="pu", pad=110, r=56, notch=64))
    # Photo checkerboard.
    gy, rows = 2560, 3
    gh = int((safe - 360 - gy) / rows)
    cw = w // 2
    for i, (ph, tone, line) in enumerate(BANNER_LINES):
        y = gy + i * gh
        photo_left = i % 2 == 0
        px = 0 if photo_left else cw
        tx = cw if photo_left else 0
        toward = "to right" if photo_left else "to left"
        parts.append(photo(C, ph, px, y, cw, gh, pos="center",
                           fade="linear-gradient(%s, rgba(%s,0) 70%%, rgba(%s,.85) 100%%)" % (toward, DB_RGB, DB_RGB)))
        bg, ink, em, chev = (OR, WH, DB, DB) if tone == "orange" else (DB, WH, OR, OR)
        text = rich(line).replace('class="o"', 'style="color:%s"' % em)
        parts.append('<div class="abs" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx;background:%s;display:flex;'
                     'align-items:center;padding:0 150px 0 120px;box-sizing:border-box;gap:50px">%s'
                     '<div style="font-family:Montserrat;font-weight:800;font-size:124px;line-height:1.08;color:%s;'
                     'letter-spacing:-.005em">%s</div></div>'
                     % (tx, y, cw, gh, bg, chevron(150, chev), ink, text))
    band_y = gy + rows * gh + 90
    parts.append('<div class="abs" style="left:0;top:%dpx;width:%dpx;height:%dpx;background:%s;display:flex;'
                 'align-items:center;justify-content:center"><span class="disp" style="font-size:150px;'
                 'text-transform:none;letter-spacing:.01em">%s</span></div>' % (band_y, w, 230, OR, URL))
    parts.append(grain_layer(w, h, 92, 0.08))
    assert band_y + 230 <= safe, "URL band runs into the bottom 300mm"
    return dict(name="climb27_pullup-banner-v2_photo-checkerboard_%dx%d" % (w, h), group="Print and merch",
                brand="Climb27", motif=None, w=w, h=h, extra_html="\n".join(parts), extra_css=css(C),
                copy=[C.TAGLINE, C.DATES, plain(BANNER_HEAD), "Tickets", URL, "Scan for tickets"] + [plain(l) for _, _, l in BANNER_LINES])


COVERS = [
    ("exhibitor-agreement", "Exhibitors", "Exhibitor", "[[agreement]]",
     ["climb_expo_floor", "climb_isn_founders_hero", "climb_consultants_expert"]),
    ("partner-proposal", "Partners", "Partner", "[[proposal]]",
     ["climb_isn_investors_hero", "climb_band_stage", "climb_awards_winners"]),
]


def doc_cover(C, key, sticker, l1, l2, photos):
    w, h = 2480, 3508
    m = 200
    head = 420
    cy0, gap = head, 18
    top_h, big_h = 900, 1120
    half = (w - gap) // 2
    tiles = [photo(C, photos[0], 0, cy0, half, top_h, pos="center 35%"),
             photo(C, photos[1], half + gap, cy0, w - half - gap, top_h, pos="center 30%"),
             photo(C, photos[2], 0, cy0 + top_h + gap, w, big_h, pos="center 40%")]
    fade = ('<div class="abs" style="left:0;top:%dpx;width:%dpx;height:%dpx;background:linear-gradient(to bottom, '
            'rgba(%s,0) 40%%, rgba(%s,1) 100%%)"></div>' % (cy0, w, top_h + gap + big_h + 2, DB_RGB, DB_RGB))
    parts = tiles + [fade]
    parts.append(logo_img(C, "Climb27", "reversed-dark", m, 150, 720))
    parts.append('<div class="abs lab" style="right:%dpx;top:180px;font-size:56px;color:#F2AE86;letter-spacing:.08em">%s</div>'
                 % (m, URL))
    ty = cy0 + top_h + gap + big_h - 40
    parts.append('<div class="sticker" style="left:%dpx;top:%dpx;font-size:72px;padding:24px 36px">%s</div>'
                 % (m, ty - 170, sticker))
    parts.append('<div class="abs" style="left:%dpx;top:%dpx"><div class="fitgroup"><h1 class="disp fit" style="font-size:300px;'
                 'width:%dpx">%s</h1><h1 class="disp fit" style="font-size:300px;width:%dpx">%s</h1></div>'
                 '<div class="body" style="font-size:76px;line-height:1.35;color:#F2AE86;margin-top:70px">'
                 'Climb27. %s<br><span style="color:#fff">%s.</span></div></div>'
                 % (m, ty, w - 2 * m, rich(l1), w - 2 * m, rich(l2), C.DATES, C.TAGLINE))
    parts.append(svg(w, h, M.slabs(w, h, corners=("br",), length=w * 0.26, thick=h * 0.035)))
    parts.append(grain_layer(w, h, 93, 0.07))
    parts.append(FIT_JS)
    return dict(name="climb27_doc-cover_%s_%dx%d" % (key, w, h), group="Print and merch", brand="Climb27", motif=None,
                w=w, h=h, extra_html="\n".join(parts), extra_css=css(C),
                copy=[sticker, plain(l1 + " " + l2), "Climb27. " + C.DATES, C.TAGLINE, URL])


def table_sign(C, n, fmt, hosted):
    """Meeting table sign. Dark Brown, one summit contour, the number as the hero, the zone on a ticket stub with a
    QR, and an optional Hosted by chip for the table's host."""
    if fmt == "a5":
        w, h = 1748, 2480
    else:
        w, h = 3508, 1240
    parts = []
    if fmt == "a5":
        parts.append(svg(w, h, M.peak(w, h, x0=0, base=0.58, summit=(0.78, 0.36), seed=n, colour=WH, opacity=0.16,
                                      stroke=8, end=0.62)))
    else:
        parts.append(svg(w, h, M.peak(w, h, x0=0, base=0.9, summit=(0.36, 0.42), seed=n, colour=WH, opacity=0.16,
                                      stroke=8, end=1.05)))
    host = ('<div class="lab" style="font-size:%dpx;color:#F2AE86;margin-top:%dpx">Hosted by</div>'
            '<div class="chip" style="width:%dpx;height:%dpx;margin-top:%dpx;font-size:%dpx;outline:5px dashed #242322;outline-offset:-18px">'
            '{Host logo}</div>')
    zone = ('<div class="lab" style="font-size:%dpx;color:#F2AE86">Zone</div>'
            '<div class="disp" style="font-size:%dpx;margin-top:16px;line-height:1.02">{Zone name}</div>')
    if fmt == "a5":
        m = 140
        parts.append(logo_img(C, "Climb27", "reversed-dark", m, 150, 560))
        parts.append('<div class="abs lab" style="left:%dpx;top:420px;font-size:120px;color:#fff;letter-spacing:.2em">Table</div>' % m)
        parts.append('<div class="abs disp" style="left:%dpx;top:520px;font-size:1240px;line-height:.86;color:#E8712A;'
                     'letter-spacing:-.04em">%d</div>' % (m - 40, n))
        tw, th, ty = w - 2 * m, 760, 1620
        tear = tw - 560
        main = zone % (44, 92) + ((host % (40, 44, 540, 150, 18, 40)) if hosted else "")
        stub = ('<div style="display:flex;flex-direction:column;align-items:center">%s<div class="lab" style="font-size:36px;'
                'color:#1E0F05;margin-top:24px;letter-spacing:.06em;text-align:center">Scan to book</div></div>' % qr(360, seed=n))
        parts.append(ticket(m, ty, tw, th, tear, main, stub, fill=CH, stroke="rgba(255,255,255,.16)", stub_fill=OR,
                            uid="tb", pad=80, r=40, notch=44))
    else:
        m = 170
        parts.append(logo_img(C, "Climb27", "reversed-dark", m, 130, 500))
        parts.append('<div class="abs lab" style="left:%dpx;top:330px;font-size:110px;color:#fff;letter-spacing:.2em">Table</div>' % m)
        parts.append('<div class="abs disp" style="left:%dpx;top:420px;font-size:860px;line-height:.86;color:#E8712A;'
                     'letter-spacing:-.04em">%d</div>' % (m - 30, n))
        tw, th, ty, tx = 1880, 900, 170, w - m - 1880
        tear = tw - 640
        main = zone % (50, 104) + ((host % (44, 60, 600, 170, 20, 44)) if hosted else "")
        stub = ('<div style="display:flex;flex-direction:column;align-items:center">%s<div class="lab" style="font-size:40px;'
                'color:#1E0F05;margin-top:26px;letter-spacing:.06em;text-align:center">Scan to book</div></div>' % qr(420, seed=n))
        parts.append(ticket(tx, ty, tw, th, tear, main, stub, fill=CH, stroke="rgba(255,255,255,.16)", stub_fill=OR,
                            uid="tb", pad=96, r=44, notch=48))
    parts.append(grain_layer(w, h, 94, 0.07))
    label = "a5-flat" if fmt == "a5" else "a4-tent-face"
    return dict(name="climb27_table-sign-%s_table-%d_%dx%d" % (label, n, w, h), group="Print and merch", brand="Climb27",
                motif=None, w=w, h=h, extra_html="\n".join(parts), extra_css=css(C),
                copy=["Table %d" % n, "Zone", "{Zone name}", "Hosted by", "{Host logo}", "Scan to book"])


def assets(C):
    """C is the catalogue module (for PHOTOS, logo(), logo_ratio(), DATES, TAGLINE, HERE)."""
    out = [name_card(C), name_card(C, with_photo=True), lower_third_v2(C)]
    for story in (False, True):
        for key, label, l1, l2 in SHARE:
            out.append(share_tile(C, key, label, l1, l2, story))
        out.append(affiliate(C, story))
    out.append(speaker_announcement(C))
    out.append(pullup_v2(C))
    for key, sticker, l1, l2, photos in COVERS:
        out.append(doc_cover(C, key, sticker, l1, l2, photos))
    for fmt in ("a5", "tent"):
        for n in (1, 2, 3):
            out.append(table_sign(C, n, fmt, hosted=n != 3))
    for a in out:
        a["set"] = "festival-kit"
    return out
