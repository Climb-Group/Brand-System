"""Builds the brand guidelines book (16:9 slides) for ClimbUK, ClimbGroup and Climb27 as HTML, ready for render.mjs."""
import os
import sys

import motifs
from brands import BRANDS, COMMON

HERE = os.path.dirname(os.path.abspath(__file__))
P = "assets/photos/"
W, H = 1920, 1080


def logo(b, variant, h=None, w=None, style=""):
    size = ("height:%dpx;" % h if h else "") + ("width:%dpx;" % w if w else "")
    return '<img src="assets/logos/%s/%s_%s.svg" style="%s%s" alt="%s logo">' % (b, b, variant, size, style, b)


def svg(inner, w=W, h=H, style="position:absolute;inset:0"):
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" style="%s">%s</svg>' % (
        w, h, w, h, style, inner)


def photo(f, fade="fade-brown", pos="center", extra=""):
    return ('<div class="ph" style="background-image:url(%s%s);background-position:%s;%s"></div>'
            '<div class="layer %s"></div>' % (P, f, pos, extra, fade))


class Book:
    def __init__(self, b):
        self.b = b
        self.B = BRANDS[b]
        self.slides = []
        self.section = ""

    def add(self, cls, inner, foot=True):
        self.slides.append((cls, inner, foot, self.section))

    def render(self):
        out = []
        total = len(self.slides)
        for i, (cls, inner, foot, sec) in enumerate(self.slides, 1):
            f = ""
            if foot:
                light = any(c in cls.split() for c in ("wh", "gr"))
                variant = "mono-dark" if light else ("mono-white" if "or" in cls.split() else "reversed-dark")
                if light and variant == "mono-dark":
                    variant = "full-colour-light" if "wh" in cls.split() else "full-colour-grey"
                f = ('<div class="foot">%s<div class="pg"><span>%s</span><b>%02d</b></div></div>'
                     % (logo(self.b, variant, h=30), sec, i))
            out.append('<section class="s %s">%s%s</section>' % (cls, inner, f))
        return out


# ---------------------------------------------------------------- slides

def cover(bk):
    b, B = bk.b, bk.B
    if b == "ClimbGroup":
        inner = (
            svg(motifs.slabs(W, H, corners=("tl", "br"), length=W * 0.3, thick=H * 0.07)
                + motifs.peak(W, H, x0=0.0, base=0.93, summit=(0.47, 0.62), seed=3, colour="#FFFFFF", opacity=0.14))
            + '<div class="glow"></div>'
            + '<div style="position:absolute;right:110px;top:150px;width:700px;height:760px">'
              '<div style="position:absolute;right:0;top:0;width:520px;height:390px;border-radius:14px;overflow:hidden;transform:rotate(3deg);box-shadow:0 30px 80px rgba(0,0,0,.5)">'
              '<div class="ph" style="background-image:url(%sclimb_isn_investors_hero.jpg)"></div></div>'
              '<div style="position:absolute;left:0;top:300px;width:470px;height:330px;border-radius:14px;overflow:hidden;transform:rotate(-3deg);box-shadow:0 30px 80px rgba(0,0,0,.5)">'
              '<div class="ph" style="background-image:url(%sclimb_recap_02.jpg)"></div></div>'
              '<div style="position:absolute;right:30px;top:470px;width:360px;height:290px;border-radius:14px;overflow:hidden;transform:rotate(2deg);box-shadow:0 30px 80px rgba(0,0,0,.5)">'
              '<div class="ph" style="background-image:url(%sclimb_awards_trophies.jpg)"></div></div>'
              '<span class="sticker" style="position:absolute;left:330px;top:250px;font-size:30px">Contracts</span>'
              '<span class="sticker white" style="position:absolute;left:70px;top:640px;font-size:30px;transform:rotate(3deg)">Decks</span>'
              '<span class="sticker dark" style="position:absolute;right:0;top:740px;font-size:30px">Footers</span>'
              '</div>' % (P, P, P)
            + '<div style="position:absolute;left:120px;top:150px">%s</div>' % logo(b, "reversed-dark", h=96)
            + '<div style="position:absolute;left:120px;top:330px;width:1050px">'
              '<div class="eb" style="font-size:26px;margin-bottom:34px">%s</div>'
              '<div class="h" style="font-size:132px">%s</div>'
              '<p class="lead" style="margin-top:40px;max-width:900px;color:var(--lg)">%s</p></div>'
            % (B["cover_eyebrow"], B["cover_h"], B["cover_sub"])
        )
        bk.add("ch", inner, foot=False)
        return
    pos = "center 35%" if b == "Climb27" else "center 40%"
    inner = (
        photo(B["cover_photo"], "fade-hero", pos)
        + '<div class="glow"></div>'
        + '<div style="position:absolute;left:120px;top:96px">%s</div>' % logo(b, "reversed-dark", h=104)
        + '<div style="position:absolute;right:120px;top:110px"><span class="sticker" style="font-size:30px">%s</span></div>' % B["cover_sticker"]
        + '<div style="position:absolute;left:120px;bottom:130px;width:1500px">'
          '<div class="eb" style="font-size:26px;margin-bottom:34px">%s</div>'
          '<div class="h" style="font-size:%dpx;text-shadow:0 2px 12px rgba(0,0,0,.6)">%s</div>'
          '<p class="lead" style="margin-top:40px;max-width:980px">%s</p></div>'
        % (B["cover_eyebrow"], B.get("cover_size", 170), B["cover_h"], B["cover_sub"])
        + svg(motifs.ascent(W, H, 1650, 1000, 150, steps=4, kind="chevrons"))
    )
    bk.add("", inner, foot=False)


SECTIONS = [
    ("01", "The idea", "climb_awards_winners.jpg", 'BUSINESS THAT FEELS LIKE A <span class="o">FESTIVAL</span>'),
    ("02", "Logo", "climb_recap_playlist.jpg", 'ONE MARK. <em>EVERY</em> <span class="o">STAGE</span>.'),
    ("03", "Colour", "climb_awards_trophies.jpg", 'ORANGE <em>LEADS</em>. IT NEVER <span class="o">FLOODS</span>.'),
    ("04", "Type", "climb_consultants_expert.jpg", 'TYPE DOES THE <span class="o">SHOUTING</span>.'),
    ("05", "Graphics", "climb_drinks_reception.jpg", 'CLIMBING, <em>STAGES</em> AND <span class="o">STICKERS</span>.'),
    ("06", "Photography", "climb_recap_04.jpg", 'REAL <em>PEOPLE</em>. REAL <span class="o">LIGHT</span>.'),
    ("07", "Motion and digital", "climb_recap_06.jpg", 'RISE. <em>SETTLE</em>. <span class="o">SPRING</span>.'),
    ("08", "Voice", "climb_isn_founders_hero.jpg", 'HEADLINE <em>ENERGY</em>. ADVISER <span class="o">DISCIPLINE</span>.'),
    ("09", "Out in the world", "climb_expo_floor.jpg", 'PRINT IT. <em>FILM</em> IT. <span class="o">SHARE</span> IT.'),
    ("10", "Everyone", "climb_recap_02.jpg", 'BUILT FOR <span class="o">EVERYONE</span> IN THE <em>ROOM</em>.'),
]


GROUP_PHOTOS = {1: "climb_isn_founders_hero.jpg", 7: "climb_recap_07.jpg"}


def divider(bk, idx):
    n, name, ph, h = SECTIONS[idx]
    if bk.b == "ClimbGroup":
        ph = GROUP_PHOTOS.get(idx, ph)
    bk.section = name
    left = idx % 2 == 0
    inner = (
        photo(ph, "fade-brown" if left else "fade-brown-r", "center 35%")
        + '<div class="glow%s"></div>' % ("" if left else " tl")
        + '<div style="position:absolute;%s:120px;top:110px;font:800 380px/0.8 Montserrat;color:transparent;-webkit-text-stroke:4px var(--o);letter-spacing:-.04em">%s</div>' % ("left" if left else "right", n)
        + '<div style="position:absolute;%s:120px;bottom:150px;width:1250px;%s">'
          '<div class="eb" style="font-size:26px;margin-bottom:30px;%s">%s</div>'
          '<div class="h" style="font-size:118px;text-shadow:0 2px 12px rgba(0,0,0,.6)">%s</div></div>'
        % ("left" if left else "right", "" if left else "text-align:right", "" if left else "justify-content:flex-end", name, h)
    )
    bk.add("", inner)


def contents(bk):
    b = bk.b
    names = [s[1] for s in SECTIONS]
    sizes = [96, 96, 80, 80, 68, 68, 58, 58, 50, 50]
    rows = []
    for i, (n, nm, *_r) in enumerate(SECTIONS):
        rows.append('<span style="font-size:%dpx;white-space:nowrap"><span class="o" style="font-size:.42em;vertical-align:.9em;margin-right:.25em">%s</span>%s</span>' % (sizes[i], n, nm.upper()))
    sep = '<span class="o" style="font-size:60px;margin:0 22px">/</span>'
    poster = sep.join(rows).replace('</span><span class="o" style="font-size:60px', '</span> <span class="o" style="font-size:60px')
    inner = (
        svg(motifs.contours(W, H, seed=7, rings=13, cx=0.9, cy=0.95))
        + '<div class="glow"></div>'
        + '<div class="pad">'
          '<div class="eb" style="font-size:24px">The lineup</div>'
          '<div class="h" style="margin-top:50px;line-height:1.12;max-width:1680px;white-space:normal">%s</div>'
          '<p class="copy" style="position:absolute;bottom:0;left:0;max-width:1100px">Every section is a headline act. Start with the idea, then use the rest when you need it: '
          'a printer needs section 09, a developer needs 07, and anyone writing a single word needs 08.</p></div>' % poster
    )
    bk.add(bk.B["ground"], inner)


def family(bk):
    b = bk.b
    cards = [
        ("ClimbUK", "The brand and the festival", "Posters, the website, socials, signs and everything people see first."),
        ("Climb27", "This year's edition", "Leads on event pieces, with ClimbUK as the endorsement. Climb26 was last year."),
        ("ClimbGroup", "The company name", "Contracts, invoices, legal lines, company decks and the ClimbGroup Event App."),
    ]
    html = ""
    for nm, role, use in cards:
        me = nm == b
        html += ('<div class="card" style="padding:56px 48px;position:relative;%s">'
                 '<div style="height:190px;display:flex;align-items:center;justify-content:center;background:var(--db);border-radius:14px">%s</div>'
                 '<div class="h" style="font-size:40px;margin-top:40px">%s</div>'
                 '<p class="copy" style="margin-top:16px">%s</p>%s</div>'
                 % ("border:3px solid var(--o);box-shadow:0 0 0 8px rgba(232,113,42,.18),0 30px 70px rgba(0,0,0,.4);transform:translateY(-12px)" if me else "",
                    logo(nm, "reversed-dark", h=78), role, use,
                    '<span class="sticker" style="position:absolute;right:-12px;top:-24px;font-size:24px">This book</span>' if me else ""))
    inner = (
        '<div class="glow"></div>'
        + '<div class="pad"><div class="eb" style="font-size:24px">One family</div>'
          '<div class="h" style="font-size:96px;margin-top:30px">ONE <em>FAMILY</em>. ONE <span class="o">FEEL</span>.</div>'
          '<p class="lead" style="margin-top:28px;max-width:1300px">%s</p>'
          '<div class="grid" style="grid-template-columns:repeat(3,1fr);gap:40px;margin-top:70px">%s</div></div>' % (bk.B["role_line"], html)
    )
    bk.add(bk.B["ground"], inner)


def big_idea(bk):
    inner = (
        photo("climb_recap_05.jpg", "fade-brown", "center 30%")
        + '<div class="glow"></div>'
        + '<div class="pad" style="display:flex;flex-direction:column;justify-content:center">'
          '<div class="eb" style="font-size:24px">The big idea</div>'
          '<div class="h" style="font-size:150px;margin-top:36px"><em>BUSINESS</em> WITH<br>A <span class="o">PARTY</span>.</div>'
          '<div class="h" style="font-size:64px;margin-top:28px;color:var(--tint)">NOT A PARTY FOR BUSINESS.</div>'
          '<p class="lead" style="margin-top:44px;max-width:1000px">Every piece has the energy of a headline act and the discipline of a good adviser. '
          'It is exciting <b>and</b> useful, or it is not finished.</p></div>'
        + '<span class="sticker" style="position:absolute;right:170px;top:180px;font-size:34px;transform:rotate(5deg)">Never corporate</span>'
    )
    bk.add("", inner)


def five_rules(bk):
    rules = [
        ("Dark first", "Dark Brown or Charcoal is the default ground. Light grounds are for long reading: documents, long emails and forms."),
        ("Orange leads", "One orange call to action per view. Around it, orange markers: a word, a rule, a sticker, a glow."),
        ("Type shouts", "Montserrat, uppercase, tight. One word orange and one word italic in every display line."),
        ("Real people", "Actual attendees and stage moments, with consent. Dense photo walls, never stock."),
        ("Contrast always", "Pick a ground and use its colour pairs. White on Climb Orange only at 19px bold or larger."),
    ]
    html = "".join(
        '<div style="position:relative;padding-top:20px"><div class="num" style="font-size:150px;opacity:.95">%d</div>'
        '<div class="h" style="font-size:40px;margin-top:20px">%s</div><p class="copy" style="margin-top:16px">%s</p></div>' % (i + 1, t, d)
        for i, (t, d) in enumerate(rules))
    inner = (
        '<div class="glow"></div>'
        + svg(motifs.ascent(W, H, 1500, 300, 220, steps=5, colour="rgba(255,255,255,.06)"))
        + '<div class="pad"><div class="eb" style="font-size:24px">The five rules</div>'
          '<div class="h" style="font-size:96px;margin-top:30px">A FESTIVAL <em>POSTER</em><br>WITH A <span class="o">BUY BUTTON</span>.</div>'
          '<div class="grid" style="grid-template-columns:repeat(5,1fr);gap:48px;margin-top:80px">%s</div></div>' % html
    )
    bk.add(bk.B["ground"], inner)


def logo_master(bk):
    b = bk.b
    inner = (
        '<div class="glow"></div><div class="glow tl" style="opacity:.6"></div>'
        + svg(motifs.contours(W, H, seed=11, rings=12, cx=1.02, cy=1.1))
        + '<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center">%s</div>' % logo(b, "reversed-dark", w=1180)
        + '<div style="position:absolute;left:120px;top:100px"><div class="eb" style="font-size:24px">The master</div></div>'
        + '<p class="copy" style="position:absolute;left:120px;bottom:130px;max-width:900px">'
          '<b>Reversed on dark is the default.</b> Climb Orange "Climb" with White on Dark Brown, Charcoal and dark photography. '
          'Always place the master file: never redraw it, recolour it or set it in a font.</p>'
        + '<span class="sticker" style="position:absolute;right:160px;bottom:150px;font-size:28px">Masters only</span>'
    )
    bk.add("", inner)


def logo_variants(bk):
    b = bk.b
    tiles = [
        ("reversed-dark", "var(--db)", "Reversed", "The default. Dark Brown, Charcoal, dark photos"),
        ("full-colour-light", "#fff", "Full colour", "White grounds"),
        ("full-colour-grey", "var(--lg)", "Full colour for grey", "Light Grey grounds, with a deeper orange"),
        ("mono-white", "var(--o)", "Mono white", "Orange, busy photo and one-colour dark"),
        ("mono-dark", "#fff", "Mono dark", "One-colour print, embossing, partner lists"),
        ("tagline-lockup-reversed", "var(--ch)", "Tagline lockup", "With The Festival for Business Growth. 240px or 60mm and up"),
    ]
    html = "".join(
        '<div><div style="background:%s;border-radius:14px;height:205px;display:flex;align-items:center;justify-content:center;%s">%s</div>'
        '<div class="h" style="font-size:28px;margin-top:22px">%s</div><p class="small" style="margin-top:6px">%s</p></div>'
        % (bg, "border:1.5px solid rgba(255,255,255,.12)" if bg in ("var(--db)", "var(--ch)") else "", logo(b, v, w=380), t, d)
        for v, bg, t, d in tiles)
    inner = (
        '<div class="pad"><div class="eb" style="font-size:24px">Which logo, where</div>'
        '<div class="h" style="font-size:80px;margin-top:26px">PICK THE <em>GROUND</em>, THEN THE <span class="o">LOGO</span>.</div>'
        '<div class="grid" style="grid-template-columns:repeat(3,1fr);gap:36px 40px;margin-top:48px">%s</div></div>' % html
    )
    bk.add(bk.B["ground"], inner)


def logo_space(bk):
    b = bk.b
    inner = (
        '<div class="pad" style="display:grid;grid-template-columns:1.25fr 1fr;gap:90px;align-items:center">'
        '<div style="position:relative;background:var(--db);border-radius:14px;height:640px;display:flex;align-items:center;justify-content:center;border:1.5px solid rgba(255,255,255,.1)">'
        '<div style="position:relative;padding:100px;outline:3px dashed rgba(242,174,134,.75);outline-offset:-3px">%s'
        '<div style="position:absolute;left:0;top:0;width:100px;height:100px;background:rgba(232,113,42,.28)"></div>'
        '<div style="position:absolute;right:0;bottom:0;width:100px;height:100px;background:rgba(232,113,42,.28)"></div>'
        '<span class="mont" style="position:absolute;left:18px;top:28px;font-weight:800;font-size:30px;color:var(--o)">l</span>'
        '<span class="mont" style="position:absolute;right:20px;bottom:28px;font-weight:800;font-size:30px;color:var(--o)">l</span></div>'
        '<span class="sticker" style="position:absolute;left:40px;bottom:36px;font-size:24px">Clear space = height of the l in Climb</span></div>'
        '<div><div class="eb" style="font-size:24px">Room to breathe</div>'
        '<div class="h" style="font-size:80px;margin-top:26px">GIVE IT <em>SPACE</em>. GIVE IT <span class="o">SIZE</span>.</div>'
        '<ul class="list copy" style="margin-top:44px">'
        '<li><b>Clear space</b> on every side equals the height of the l in Climb, the (R) mark included. Nothing else goes inside it.</li>'
        '<li><b>Wordmark</b> at least 120px wide on screen and 30mm in print.</li>'
        '<li><b>Tagline lockup</b> at least 240px or 60mm, so the line stays readable.</li>'
        '<li><b>Below that,</b> switch to the square tile (64px and up) or the monogram (down to 16px).</li></ul></div></div>'
        % logo(b, "reversed-dark", w=640)
    )
    bk.add(bk.B["ground"], inner)


def logo_icons(bk):
    b = bk.b
    inner = (
        '<div class="glow"></div>'
        + '<div class="pad" style="display:grid;grid-template-columns:1fr 1fr;gap:100px;align-items:center">'
          '<div><div class="eb" style="font-size:24px">Square marks</div>'
          '<div class="h" style="font-size:80px;margin-top:26px">SMALL SPACES, <em>BIG</em> <span class="o">PRESENCE</span>.</div>'
          '<ul class="list copy" style="margin-top:44px">'
          '<li><b>The stacked tile</b> is the social avatar and any square 64px or larger.</li>'
          '<li><b>The l! monogram</b> is the favicon, the app icon and anything under 64px. It is the same mark for every brand in the family.</li>'
          '<li><b>Embroidery and laser marking</b> use the tile or the monogram, never the long wordmark.</li></ul></div>'
          '<div style="display:flex;gap:60px;align-items:flex-end;justify-content:center">'
          '<div style="text-align:center">%s<p class="small" style="margin-top:20px">Stacked tile</p></div>'
          '<div style="text-align:center">%s<p class="small" style="margin-top:20px">Monogram</p></div>'
          '<div style="display:flex;flex-direction:column;gap:22px;align-items:center">%s%s%s<p class="small">64, 32, 16</p></div></div></div>'
        % (logo(b, "icon", w=360, style="border-radius:40px;box-shadow:0 30px 80px rgba(0,0,0,.5)"),
           logo(b, "icon-monogram", w=240, style="border-radius:28px;box-shadow:0 30px 80px rgba(0,0,0,.5)"),
           logo(b, "icon-monogram", w=64, style="border-radius:10px"), logo(b, "icon-monogram", w=32, style="border-radius:6px"),
           logo(b, "icon-monogram", w=16, style="border-radius:3px"))
    )
    bk.add(bk.B["ground"], inner)


def logo_donts(bk):
    b = bk.b
    L = "assets/logos/%s/%s_" % (b, b)
    items = [
        ('<img src="%sreversed-dark.svg" style="width:330px;transform:scaleX(1.45)">' % L, "var(--db)", "Stretch or squash it"),
        ('<img src="%sreversed-dark.svg" style="width:330px;transform:rotate(-12deg)">' % L, "var(--db)", "Rotate or tilt it"),
        ('<img src="%sreversed-dark.svg" style="width:330px;filter:hue-rotate(150deg) saturate(1.6)">' % L, "var(--db)", "Recolour it"),
        ('<img src="%sreversed-dark.svg" style="width:330px;filter:drop-shadow(0 0 18px #F2AE86) drop-shadow(8px 10px 0 #000)">' % L, "var(--db)", "Add glows or shadows"),
        ('<img src="%sfull-colour-light.svg" style="width:330px">' % L, "var(--o)", "Full colour on orange"),
        ('<div class="ph" style="background-image:url(%sclimb_recap_07.jpg);border-radius:14px"></div><img src="%sreversed-dark.svg" style="width:330px;position:relative">' % (P, L), "var(--db)", "Busy part of a photo"),
    ]
    html = "".join(
        '<div><div style="position:relative;background:%s;border-radius:14px;height:205px;display:flex;align-items:center;justify-content:center;overflow:hidden;border:1.5px solid rgba(255,255,255,.12)">%s'
        '<div style="position:absolute;right:18px;top:14px;width:58px;height:58px;border-radius:50%%;background:var(--db);border:3px solid var(--o);display:flex;align-items:center;justify-content:center;font:800 40px/1 Montserrat;color:var(--o)">\u00d7</div></div>'
        '<div class="h" style="font-size:28px;margin-top:22px">%s</div></div>' % (bg, el, t)
        for el, bg, t in items)
    inner = (
        '<div class="pad"><div class="eb" style="font-size:24px">Hands off</div>'
        '<div class="h" style="font-size:80px;margin-top:26px">EFFECTS BELONG TO THE <em>LAYOUT</em>, NOT THE <span class="o">LOGO</span>.</div>'
        '<div class="grid" style="grid-template-columns:repeat(3,1fr);gap:36px 40px;margin-top:44px">%s</div></div>' % html
    )
    bk.add(bk.B["ground"], inner)


def edition_mark(bk):
    """Climb27 only: how the edition mark and ClimbUK sit together."""
    inner = (
        photo("climb_isn_investors_hero.jpg", "fade-heat", "center 30%")
        + '<div class="pad" style="display:grid;grid-template-columns:1fr 1fr;gap:90px;align-items:center">'
          '<div><div class="eb" style="font-size:24px">The edition mark</div>'
          '<div class="h" style="font-size:84px;margin-top:26px">THE EDITION <em>LEADS</em>. CLIMBUK <span class="o">ENDORSES</span>.</div>'
          '<ul class="list copy" style="margin-top:44px">'
          '<li><b>Climb27 leads</b> on posters, tickets, socials, signs and screens for this edition.</li>'
          '<li><b>ClimbUK sits quieter:</b> smaller, in a corner or the footer, in one tone if the piece is busy.</li>'
          '<li><b>Dates go next to the mark,</b> never inside it: 30 June and 1 July 2027.</li></ul></div>'
          '<div class="ticket" style="padding:70px 70px 56px">'
          '%s<div class="h" style="font-size:44px;margin-top:40px">YOUR BUSINESS.<br><em>BIGGER</em> <span class="o">STAGE</span>.</div>'
          '<div class="tear" style="margin:46px -70px 40px"><div class="notch" style="left:-23px;top:-24px"></div><div class="notch" style="right:-23px;top:-24px"></div></div>'
          '<div style="display:flex;justify-content:space-between;align-items:center"><div class="mont" style="font-weight:700;font-size:26px">30 June and 1 July 2027</div>%s</div></div></div>'
        % (logo("Climb27", "reversed-dark", w=560), logo("ClimbUK", "mono-white", h=34))
    )
    bk.add("", inner)


def colours(bk):
    sw = [
        ("Climb Orange", "#E8712A", "var(--o)", "var(--db)", "Pantone 158 C / 158 U", "CMYK 0 65 90 0", "RAL 2011 Deep Orange", 2.2),
        ("Dark Brown", "#1E0F05", "var(--db)", "#fff", "Pantone Black 4 C / U", "CMYK 40 70 80 85", "RAL 8022 Black Brown", 2.2),
        ("Charcoal", "#242322", "var(--ch)", "#fff", "Pantone 419 C / U", "CMYK 60 50 50 90", "RAL 9011 Graphite Black", 1.4),
        ("Light Grey", "#E9E9E9", "var(--lg)", "var(--ch)", "Pantone Cool Gray 1 C", "CMYK 0 0 0 10", "RAL 9002 Grey White", 1),
        ("Orange Tint", "#F2AE86", "var(--tint)", "var(--db)", "45% tint of 158", "CMYK 0 35 45 0", "Match on proof", 1),
        ("White", "#FFFFFF", "#fff", "var(--ch)", "Paper", "CMYK 0 0 0 0", "RAL 9016 Traffic White", 1),
    ]
    html = "".join(
        '<div style="flex:%s;background:%s;color:%s;border-radius:14px;padding:36px 32px;display:flex;flex-direction:column;justify-content:flex-end;%s">'
        '<div class="h" style="font-size:34px;color:inherit">%s</div><div class="mont" style="font-weight:700;font-size:30px;margin-top:8px">%s</div>'
        '<div style="font-size:20px;line-height:1.5;margin-top:18px;opacity:.92">%s<br>%s<br>%s</div></div>'
        % (fl, bg, fg, "border:1.5px solid rgba(255,255,255,.14)" if bg in ("var(--db)", "var(--ch)") else "", n, hx, pa, cm, ral)
        for n, hx, bg, fg, pa, cm, ral, fl in sw)
    inner = (
        '<div class="pad"><div class="eb" style="font-size:24px">The palette</div>'
        '<div class="h" style="font-size:80px;margin-top:26px">SIX COLOURS. <em>ONE</em> OF THEM <span class="o">GLOWS</span>.</div>'
        '<div style="display:flex;gap:22px;height:560px;margin-top:56px">%s</div>'
        '<p class="small" style="margin-top:22px">Print values are the nearest published matches. Approve a press proof before the first run of anything that matters.</p></div>' % html
    )
    bk.add(bk.B["ground"], inner)


def presets(bk):
    ps = [
        ("Dark Brown", "The default", "var(--db)", "#fff", "#fff", "var(--tint)", "var(--o)", "var(--o)", "#fff"),
        ("Charcoal", "Second dark", "var(--ch)", "var(--lg)", "#fff", "var(--tint)", "var(--o)", "var(--o)", "#fff"),
        ("Climb Orange", "The big moment", "var(--o)", "#fff", "#fff", "#fff", "var(--db)", "var(--db)", "#fff"),
        ("White", "Long reading", "#fff", "#4A5878", "var(--ch)", "var(--deep)", "var(--o)", "var(--o)", "#fff"),
        ("Light Grey", "Quiet sections", "var(--lg)", "#404C68", "#B04902", "#7A3B16", "#D5641E", "var(--o)", "#fff"),
    ]
    html = "".join(
        '<div style="background:%s;border-radius:14px;padding:40px 34px;height:600px;display:flex;flex-direction:column;%s">'
        '<div class="mont" style="font-weight:700;font-size:18px;letter-spacing:.16em;text-transform:uppercase;color:%s">%s</div>'
        '<div class="h" style="font-size:44px;color:%s;margin-top:18px">%s <span style="color:%s">WORD</span></div>'
        '<p style="font-size:22px;line-height:1.5;color:%s;margin-top:18px">Body text that is easy to read for a whole paragraph. '
        '<span style="color:%s;text-decoration:underline;font-weight:600">A link that says where it goes</span></p>'
        '<div style="margin-top:auto"><span class="btn" style="font-size:22px;background:%s;color:%s;%s">Get your ticket</span></div></div>'
        % (bg, "border:1.5px solid rgba(255,255,255,.14)" if bg in ("var(--db)", "var(--ch)") else "",
           small, sub, head, name.upper().split()[0], large, txt, small, btn, lab,
           "box-shadow:none" if bg == "var(--o)" else "")
        for name, sub, bg, txt, head, small, large, btn, lab in ps)
    inner = (
        '<div class="pad"><div class="eb" style="font-size:24px">Five grounds</div>'
        '<div class="h" style="font-size:80px;margin-top:26px">PICK A <em>GROUND</em>. USE ITS <span class="o">PAIRS</span>.</div>'
        '<div class="grid" style="grid-template-columns:repeat(5,1fr);gap:24px;margin-top:56px">%s</div></div>' % html
    )
    bk.add(bk.B["ground"], inner)


def contrast(bk):
    rows = [
        ("White on Climb Orange", "19px bold or 24px and up only", "var(--o)", "#fff", "Aa"),
        ("Climb Orange on White", "Large words, buttons and marks", "#fff", "var(--o)", "Aa"),
        ("Orange Tint on Dark Brown", "Small orange text and links on dark", "var(--db)", "var(--tint)", "Aa"),
        ("Deep Orange on White", "Small orange text and links on white", "#fff", "var(--deep)", "Aa"),
        ("Climb Orange on Dark Brown", "Any size", "var(--db)", "var(--o)", "Aa"),
    ]
    html = "".join(
        '<div style="display:flex;align-items:center;gap:30px;padding:18px 0;border-bottom:1.5px solid rgba(255,255,255,.1)">'
        '<div style="width:120px;height:90px;border-radius:10px;background:%s;color:%s;display:flex;align-items:center;justify-content:center;font:800 46px Montserrat;border:1.5px solid rgba(255,255,255,.14)">%s</div>'
        '<div><div class="mont" style="font-weight:700;font-size:28px;color:#fff">%s</div><div class="small">%s</div></div></div>'
        % (bg, fg, a, t, d) for t, d, bg, fg, a in rows)
    nevers = ["Light Grey or Body Slate text on any orange", "Orange on orange", "Climb Orange headings on Light Grey",
              "A hover state that gets lighter", "Climb Orange for small text"]
    inner = (
        '<div class="glow"></div>'
        + '<div class="pad" style="display:grid;grid-template-columns:1.1fr 1fr;gap:100px">'
          '<div><div class="eb" style="font-size:24px">Contrast</div>'
          '<div class="h" style="font-size:80px;margin-top:26px">CONTRAST IS <em>NOT</em> <span class="o">OPTIONAL</span>.</div>'
          '<div style="margin-top:40px">%s</div></div>'
          '<div style="padding-top:150px"><div class="h" style="font-size:40px">NEVER</div>'
          '<ul class="list no copy" style="margin-top:30px">%s</ul>'
          '<p class="copy" style="margin-top:40px">Small text means anything under 19px bold or 24px regular: eyebrows, tags, captions and links.</p></div></div>'
        % (html, "".join("<li>%s</li>" % n for n in nevers))
    )
    bk.add(bk.B["ground"], inner)


def typefaces(bk):
    inner = (
        '<div class="pad" style="display:grid;grid-template-columns:1.3fr 1fr;gap:90px">'
        '<div style="position:relative">'
        '<div class="eb" style="font-size:24px">Typefaces</div>'
        '<div class="mont" style="font-weight:800;font-size:440px;line-height:.9;color:#fff;margin-top:30px;letter-spacing:-.03em">A<span class="o" style="font-style:italic">a</span></div>'
        '<div class="h" style="font-size:72px;margin-top:20px">MONTSERRAT</div>'
        '<p class="copy" style="margin-top:14px">Headings and display. Bold by default, Extra Bold for posters and screens. Uppercase, tight leading, a little negative tracking.</p>'
        '<div class="mont" style="font-weight:700;font-size:34px;margin-top:26px;letter-spacing:.02em">ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789</div></div>'
        '<div style="padding-top:120px">'
        '<div style="font-family:Open Sans;font-weight:600;font-size:200px;line-height:.9;color:var(--tint)">Aa</div>'
        '<div class="h" style="font-size:56px;margin-top:30px">OPEN SANS</div>'
        '<p class="copy" style="margin-top:14px">Everything you read: body copy, labels, captions and small print. Regular for reading, Semibold for labels.</p>'
        '<p style="font-size:30px;line-height:1.5;margin-top:30px;color:#fff">Two days with the founders, investors and advisers who move businesses forward.</p>'
        '<p class="small" style="margin-top:34px">Both are free under the SIL Open Font Licence. Arial is the fallback where they cannot load.</p></div></div>'
    )
    bk.add(bk.B["ground"], inner)


def headline_formula(bk):
    inner = (
        '<div class="glow"></div>'
        + '<div class="pad">'
          '<div style="position:relative;margin-top:10px">'
          '<div class="eb" style="font-size:26px">Tracked eyebrow</div>'
          '<div class="h" style="font-size:150px;margin-top:34px">ICONIC <em>MOMENTS</em>.<br>REAL ADVICE.<br>NO <span class="o">FLUFF</span>.</div>'
          '<span class="sticker" style="position:absolute;left:720px;top:-26px;font-size:26px;transform:rotate(4deg)">One word in italic</span>'
          '<span class="sticker" style="position:absolute;left:880px;top:420px;font-size:26px">One word in orange</span></div>'
          '<div class="grid" style="grid-template-columns:repeat(4,1fr);gap:44px;margin-top:60px">'
          '<div><div class="num" style="font-size:60px">3 to 8</div><p class="copy" style="margin-top:8px">words, one idea, in two or three beats.</p></div>'
          '<div><div class="num" style="font-size:60px">1 + 1</div><p class="copy" style="margin-top:8px">one orange word and one italic word per display line.</p></div>'
          '<div><div class="num" style="font-size:60px">0.95</div><p class="copy" style="margin-top:8px">leading, 0.98 to 1.1 for longer lines. Tracking just under zero.</p></div>'
          '<div><div class="num" style="font-size:60px">2 max</div><p class="copy" style="margin-top:8px">sizes of display type on any one view.</p></div></div></div>'
    )
    bk.add(bk.B["ground"], inner)


def type_scale(bk):
    rows = [
        ("Display", "68px / 1.02", 68, 800, True), ("H1", "48px / 1.05", 48, 800, True), ("H2", "40px / 1.08", 40, 800, True),
        ("H3", "22px / 1.2", 22, 700, False), ("Lead", "20px / 1.5", 20, 400, False), ("Body", "16px / 1.6", 16, 400, False),
        ("Small", "14px / 1.5", 14, 400, False), ("Eyebrow", "13px, tracked 0.12em", 13, 600, True),
    ]
    html = "".join(
        '<div style="display:grid;grid-template-columns:220px 300px 1fr;align-items:baseline;padding:9px 0;border-bottom:1.5px solid rgba(74,88,120,.18)">'
        '<div class="mont" style="font-weight:700;font-size:22px;color:var(--deep);text-transform:uppercase;letter-spacing:.12em">%s</div>'
        '<div style="font-size:22px;color:#4A5878">%s</div>'
        '<div style="font-family:%s;font-weight:%d;font-size:%dpx;color:var(--ch);%s">%s</div></div>'
        % (n, m, "Montserrat" if up or w >= 700 else "Open Sans", w, int(sz * 1.3),
           "text-transform:uppercase;letter-spacing:%s" % (".12em" if n == "Eyebrow" else "-.01em") if up else "",
           "Find your people" if up else "Two days. The right rooms. Conversations that move your business.")
        for n, m, sz, w, up in rows)
    inner = (
        '<div class="pad"><div class="eb" style="font-size:24px">Type scale</div>'
        '<div class="h" style="font-size:72px;margin-top:22px">A SCALE THAT <em>READS</em> AT <span class="o">ANY</span> SIZE.</div>'
        '<div style="margin-top:36px">%s</div>'
        '<p class="small" style="margin-top:20px">Web sizes at a 1440px wide screen, shown here at 1.3 times. Nothing is ever smaller than 13px, including legal lines.</p></div>' % html
    )
    bk.add("wh", inner)


def motifs_slide(bk):
    w, h = 520, 312
    tiles = [
        ("The Ascent", "Steps and chevrons: dividers, corners, progress, wayfinding.",
         motifs.ascent(w, h, 50, 240, 150, steps=4, colour="#E8712A") + motifs.ascent(w, h, 360, 240, 170, steps=5, kind="chevrons")),
        ("Contours", "A climbing map: quiet fields on dark grounds, merch and walls.", motifs.contours(w, h, seed=4, rings=11, cx=0.75, cy=0.7)),
        ("Stage Light", "Beams and glow: heroes, screens, video and Main Stage Moments.", None),
        ("Connections", "Dots finding each other: Find Your People and partner pieces.", motifs.connections(w, h, seed=5, dots=26, region=(0.05, 0.08, 0.95, 0.92))),
        ("Peak and slabs", "A summit line and angled corner slabs: covers, name cards and decks.",
         motifs.slabs(w, h, corners=("tl",), length=w * 0.45, thick=h * 0.12) + motifs.peak(w, h, base=0.88, summit=(0.55, 0.35), seed=2, colour="#FFFFFF", opacity=0.5)),
        ("Highlight bar", "A solid orange bar behind one word: the poster version of the orange word.", None),
    ]
    html = ""
    for t, d, art in tiles:
        if t == "Stage Light":
            body = ('<div style="position:absolute;inset:0;background:radial-gradient(260px 140px at 62% 0%,rgba(242,174,134,.7),rgba(242,174,134,0) 70%)"></div>'
                    '<div style="position:absolute;left:47%;top:-20px;width:110px;height:420px;transform-origin:top;transform:rotate(24deg);background:linear-gradient(180deg,rgba(232,113,42,.6),rgba(232,113,42,0));filter:blur(14px)"></div>'
                    '<div style="position:absolute;left:55%;top:-20px;width:120px;height:420px;transform-origin:top;transform:rotate(-4deg);background:linear-gradient(180deg,rgba(232,113,42,.55),rgba(232,113,42,0));filter:blur(14px)"></div>'
                    '<div style="position:absolute;left:62%;top:-20px;width:100px;height:420px;transform-origin:top;transform:rotate(-28deg);background:linear-gradient(180deg,rgba(232,113,42,.5),rgba(232,113,42,0));filter:blur(14px)"></div>')
        elif t == "Highlight bar":
            body = '<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center"><div class="h" style="font-size:64px;text-align:center;line-height:1.15">FIND YOUR<br><span class="bar">PEOPLE</span></div></div>'
        else:
            body = svg(art, w, h)
        html += ('<div><div style="position:relative;height:%dpx;border-radius:14px;overflow:hidden;background:var(--db);border:1.5px solid rgba(255,255,255,.1)">%s</div>'
                 '<div class="h" style="font-size:30px;margin-top:20px">%s</div><p class="small" style="margin-top:4px">%s</p></div>' % (h - 80, body, t, d))
    inner = (
        '<div class="pad"><div class="eb" style="font-size:24px">Graphic language</div>'
        '<div class="h" style="font-size:72px;margin-top:22px">ONE <em>MOTIF</em> FAMILY PER <span class="o">PIECE</span>.</div>'
        '<div class="grid" style="grid-template-columns:repeat(3,1fr);gap:26px 40px;margin-top:34px">%s</div></div>' % html
    )
    bk.add(bk.B["ground"], inner)


def devices(bk):
    b = bk.b
    inner = (
        '<div class="glow"></div>'
        + '<div class="pad">'
          '<div class="eb" style="font-size:24px">Festival devices</div>'
          '<div class="h" style="font-size:72px;margin-top:22px">TWO OR <em>THREE</em> PER PIECE. <span class="o">NEVER ALL</span>.</div>'
          '<div style="position:relative;height:640px;margin-top:40px">'
          # ticket
          '<div class="ticket" style="position:absolute;left:0;top:30px;width:560px;padding:44px 46px 40px">'
          '<span class="tag" style="font-size:18px;color:var(--tint)">Release 1</span>'
          '<div class="h" style="font-size:48px;margin-top:22px">TWO-DAY <span class="o">PASS</span></div>'
          '<p class="copy" style="margin-top:14px">Every session, the grand opening and the after parties.</p>'
          '<div class="tear" style="margin:52px -46px 30px"><div class="notch" style="left:-23px;top:-24px"></div><div class="notch" style="right:-23px;top:-24px"></div></div>'
          '<span class="btn" style="font-size:24px">Get your ticket <span>\u2192</span></span>'
          '<p class="small" style="margin-top:16px">Ticket card: stub notches and a tear line.</p></div>'
          # photo card
          '<div style="position:absolute;left:640px;top:0;width:420px;height:560px;border-radius:14px;overflow:hidden;transform:rotate(-1.5deg);box-shadow:0 30px 70px rgba(0,0,0,.5)">'
          '<div class="ph" style="background-image:url(%sclimb_awards_winners.jpg)"></div><div class="layer fade-card"></div>'
          '<div class="h" style="position:absolute;left:34px;top:34px;font-size:40px">THE <span class="o">CLIMB</span>AWARDS</div>'
          '<p style="position:absolute;left:34px;bottom:30px;right:34px;font-size:22px;line-height:1.4">The walk-up, the trophies, the night people talk about.</p>'
          '<span class="sticker" style="position:absolute;right:20px;top:120px;font-size:22px">Main stage</span></div>'
          # stickers + rule + buttons
          '<div style="position:absolute;left:1140px;top:10px;width:540px">'
          '<div style="display:flex;gap:18px;flex-wrap:wrap"><span class="sticker" style="font-size:28px">VIP</span>'
          '<span class="sticker dark" style="font-size:28px;transform:rotate(3deg);border:2px solid var(--o)">Just joined</span>'
          '<span class="sticker white" style="font-size:28px">Speaker</span></div>'
          '<p class="small" style="margin-top:18px">Stickers: tilted -3 to -4 degrees, slapped on a corner.</p>'
          '<div class="rule" style="margin-top:56px"></div><div class="eb plain" style="font-size:22px;margin-top:18px">Short rule and eyebrow</div>'
          '<div style="margin-top:56px;display:flex;gap:20px"><span class="btn" style="font-size:24px">Become a partner</span><span class="btn ghost" style="font-size:24px">See the agenda</span></div>'
          '<p class="small" style="margin-top:16px">One orange button per view. It glows orange, not grey.</p>'
          '<div class="mont" style="margin-top:56px;font-weight:700;font-size:20px;letter-spacing:.16em;text-transform:uppercase;color:var(--tint)">This is what it looked like last time <span class="chev" style="transform:rotate(135deg);margin-left:10px"></span></div>'
          '<p class="small" style="margin-top:10px">Pull link: hands the reader to the next section.</p></div>'
          '</div></div>' % P
    )
    bk.add(bk.B["ground"], inner)


def lineup(bk):
    names = [("Investor Speed Networking", 74, "#fff"), ("Busk Your Business", 74, "var(--o)"), ("the ClimbAwards", 60, "#fff"),
             ("ClimbHealth", 60, "var(--tint)"), ("Roundtables", 48, "#fff"), ("The grand opening", 48, "var(--o)"), ("After parties", 48, "#fff")]
    sep = '<span style="color:var(--o);font-size:56px">/</span>'
    poster = (" " + sep + " ").join('<span style="font-size:%dpx;color:%s;white-space:nowrap">%s</span>' % (s, c, n.upper()) for n, s, c in names)
    row = lambda txt, d: ('<div style="white-space:nowrap;font:800 54px Montserrat;text-transform:uppercase;color:rgba(255,255,255,.14);transform:translateX(%dpx)">%s</div>' % (d, txt))
    marq = " \u00b7 ".join(["Find Your People", "Main Stage Moments", "Business that feels like a festival"] * 3)
    inner = (
        '<div class="glow"></div>'
        + '<div style="position:absolute;left:0;right:0;top:60px">%s%s</div>' % (row(marq, -120), row(marq, -620))
        + '<div class="pad" style="top:300px">'
          '<div class="eb" style="font-size:24px">Lineups and marquees</div>'
          '<div class="h" style="margin-top:34px;line-height:1.12">%s</div>'
          '<p class="copy" style="margin-top:50px;max-width:1150px">Set names like a festival poster: headline acts first, split by orange slashes or dots. '
          'Logo and name rows drift slowly in alternate directions, so it reads as a crowd. They pause when someone hovers or focuses on them.</p></div>' % poster
    )
    bk.add(bk.B["ground"], inner)


def illustrations(bk, names):
    cells = "".join('<div style="display:flex;align-items:center;justify-content:center"><img src="assets/illus/%s.svg" style="width:118px;height:118px"></div>' % n for n in names)
    inner = (
        '<div class="pad" style="display:grid;grid-template-columns:560px 1fr;gap:70px">'
        '<div><div class="eb" style="font-size:24px">Illustrations</div>'
        '<div class="h" style="font-size:72px;margin-top:22px">DRAWN BY <em>HAND</em>. NEVER <span class="o">CHILDISH</span>.</div>'
        '<ul class="list copy" style="margin-top:40px">'
        '<li><b>One confident stroke,</b> rounded ends and slightly imperfect curves. Never shaky.</li>'
        '<li><b>One solid orange fill</b> with Dark Brown cut lines.</li>'
        '<li><b>Low-opacity back shapes</b> give every icon depth.</li>'
        '<li><b>155 drawings</b> across stage, business, network, festival and ideas, in the downloads.</li></ul></div>'
        '<div style="display:grid;grid-template-columns:repeat(7,1fr);grid-auto-rows:150px;gap:6px;align-content:start">%s</div></div>' % cells
    )
    bk.add(bk.B["ground"], inner)


def photo_shoot(bk):
    tiles = ["climb_awards_winners.jpg", "climb_recap_05.jpg", "climb_recap_02.jpg", "climb_band_stage.jpg", "climb_recap_04.jpg",
             "climb_isn_founders_hero.jpg", "climb_drinks_reception.jpg", "climb_consultants_expert.jpg"]
    wall = ('<div style="display:grid;grid-template-columns:repeat(4,1fr);grid-template-rows:repeat(3,1fr);gap:10px;position:absolute;right:0;top:0;width:1060px;height:1080px">'
            '<div style="grid-column:1/3;grid-row:1/3;background:url(%s%s) center/cover"></div>' % (P, tiles[0])
            + "".join('<div style="background:url(%s%s) center/cover"></div>' % (P, t) for t in tiles[1:])
            + '</div>')
    inner = (
        wall
        + '<div style="position:absolute;left:0;top:0;bottom:0;width:980px;background:linear-gradient(90deg,var(--db) 78%,rgba(30,15,5,0))"></div>'
        + '<div class="pad" style="right:auto;width:780px">'
          '<div class="eb" style="font-size:24px">What to shoot</div>'
          '<div class="h" style="font-size:80px;margin-top:22px">THE <em>REASON</em> TO <span class="o">COME</span>.</div>'
          '<ul class="list copy" style="margin-top:40px">'
          '<li><b>Joy and connection:</b> laughing, leaning in, handshakes mid-conversation.</li>'
          '<li><b>Main Stage Moments:</b> the gesture, the crowd looking up, the band, the awards walk-up.</li>'
          '<li><b>Find Your People:</b> close conversations, speed networking tables, roundtables in full flow.</li>'
          '<li><b>Texture:</b> orange lanyards, badges, drinks being poured, trophies, after party lights.</li>'
          '<li><b>For every wide,</b> three mediums and five close-ups.</li></ul></div>'
        + '<span class="sticker" style="position:absolute;left:1000px;top:640px;font-size:28px">Dense beats sparse</span>'
    )
    bk.add("", inner)


def photo_fades(bk):
    fades = [("fade-brown", "Brown", "Statements and story bands", "climb_recap_02.jpg", 'BUSINESS WITH A <span class="o">PARTY</span>'),
             ("fade-heat", "Heat", "Selling moments: a line, two buttons", "climb_crowd_wide.jpg", 'GET YOUR <span class="o">TICKET</span>'),
             ("fade-orange", "Orange", "One offer on an orange section", "climb_awards_trophies.jpg", 'BRINGING A <span style="color:var(--db)">TEAM</span>?')]
    html = "".join(
        '<div><div style="position:relative;height:520px;border-radius:14px;overflow:hidden">'
        '<div class="ph" style="background-image:url(%s%s)"></div><div class="layer %s"></div>'
        '<div class="h" style="position:absolute;left:40px;bottom:44px;font-size:52px;width:330px">%s</div></div>'
        '<div class="h" style="font-size:32px;margin-top:22px">%s</div><p class="small" style="margin-top:6px">%s</p></div>'
        % (P, f, cls, hl, n, d) for cls, n, d, f, hl in fades)
    inner = (
        '<div class="pad"><div class="eb" style="font-size:24px">Photo fades</div>'
        '<div class="h" style="font-size:72px;margin-top:22px">WORDS ON THE <em>DARK</em> SIDE. <span class="o">ALWAYS</span>.</div>'
        '<div class="grid" style="grid-template-columns:repeat(3,1fr);gap:40px;margin-top:44px">%s</div>'
        '<p class="small" style="margin-top:26px">Text sits where the fade is at least 85%% Dark Brown (or 90%% orange). Orange fades go over things and places, never over faces.</p></div>' % html
    )
    bk.add(bk.B["ground"], inner)


def photo_rules(bk):
    inner = (
        photo("climb_recap_07.jpg", "fade-brown-r", "center 30%")
        + '<div class="pad" style="left:auto;width:900px">'
          '<div class="eb" style="font-size:24px;justify-content:flex-end">Editing and care</div>'
          '<div class="h" style="font-size:80px;margin-top:22px;text-align:right">WARM. <em>BRIGHT</em>. <span class="o">TRUE</span>.</div>'
          '<ul class="list copy" style="margin-top:40px">'
          '<li><b>Full colour,</b> warm white balance, shadows that lean Dark Brown, orange held saturated.</li>'
          '<li><b>Highest resolution:</b> RAW at no less than 4K, 6K is fine, 8K is ideal. Never upscale.</li>'
          '<li><b>Light retouching only.</b> Never change who was there or what happened.</li>'
          '<li><b>Consent:</b> anyone in a marketing close-up has agreed. Honour opt-out lanyards.</li></ul>'
          '<div class="h" style="font-size:36px;margin-top:40px">NEVER</div>'
          '<ul class="list no copy" style="margin-top:20px"><li>Stock handshakes, skylines or laptops</li><li>Empty rooms and rows of empty chairs</li>'
          '<li>Lecterns from the back, slides with no people</li></ul></div>'
    )
    bk.add("", inner)


def motion(bk):
    toks = [("Instant", "100ms", "Hover and press colour"), ("Quick", "160ms", "Buttons, toggles, focus rings"),
            ("Base", "240ms", "Card lift, menus"), ("Slow", "400ms", "Panels, scroll reveals"), ("Stage", "700ms", "Hero entrances, logo reveals")]
    bars = "".join(
        '<div style="display:grid;grid-template-columns:150px 120px 1fr;align-items:center;gap:20px;margin-bottom:22px">'
        '<div class="mont" style="font-weight:700;font-size:24px;text-transform:uppercase;letter-spacing:.1em">%s</div>'
        '<div class="mont" style="font-weight:800;font-size:28px;color:var(--o)">%s</div>'
        '<div><div style="height:16px;border-radius:8px;background:linear-gradient(90deg,var(--o),rgba(232,113,42,.25));width:%dpx"></div><div class="small" style="margin-top:6px">%s</div></div></div>'
        % (n, v, int(v[:-2]) * 0.9 + 30, d) for n, v, d in toks)
    # rise diagram
    steps = "".join('<div style="position:absolute;left:%dpx;bottom:%dpx;width:150px;height:110px;border-radius:14px;background:var(--ch);opacity:%.2f;border:1.5px solid rgba(255,255,255,.12)"></div>'
                    % (i * 175, [0, 26, 44, 52][i], [0.25, 0.5, 0.8, 1][i]) for i in range(4))
    inner = (
        '<div class="glow"></div>'
        + '<div class="pad" style="display:grid;grid-template-columns:1.05fr 1fr;gap:80px">'
          '<div><div class="eb" style="font-size:24px">Motion</div>'
          '<div class="h" style="font-size:62px;margin-top:22px">A FESTIVAL <em>CROWD</em>,<br>NOT A <span class="o">SLIDESHOW</span>.</div>'
          '<ul class="list copy" style="margin-top:40px">'
          '<li><b>Rise, then settle.</b> Entrances travel up and slow down.</li>'
          '<li><b>One thing leads.</b> Everything else is still or follows in a short stagger.</li>'
          '<li><b>Light and crowds move, type holds.</b></li>'
          '<li><b>Touch gets a spring:</b> one small, joyful overshoot.</li>'
          '<li><b>Always optional:</b> reduced motion swaps movement for a quick fade.</li></ul></div>'
          '<div style="padding-top:40px"><div style="position:relative;height:220px;margin-bottom:60px">%s'
          '<span class="sticker" style="position:absolute;left:560px;top:0;font-size:22px">Rise 16px</span></div>%s'
          '<p class="small" style="margin-top:20px">Easing: rise cubic-bezier(0.16, 1, 0.3, 1). Spring cubic-bezier(0.34, 1.56, 0.64, 1). Stagger 60ms, six at most.</p></div></div>'
        % (steps, bars)
    )
    bk.add(bk.B["ground"], inner)


def digital_ui(bk):
    inner = (
        '<div class="pad">'
        '<div class="eb" style="font-size:24px">Digital</div>'
        '<div class="h" style="font-size:66px;margin-top:22px">WHAT YOU <em>TOUCH</em> FLOATS. GROUNDS STAY <span class="o">FLAT</span>.</div>'
        '<div class="grid" style="grid-template-columns:1fr 1fr 1fr;gap:40px;margin-top:56px">'
        '<div class="card" style="padding:44px">'
        '<div class="h" style="font-size:32px">BUTTONS</div>'
        '<div style="margin-top:34px;display:flex;flex-direction:column;gap:22px;align-items:flex-start">'
        '<span class="btn" style="font-size:24px">Get your ticket</span>'
        '<span class="btn" style="font-size:24px;background:var(--ot);transform:translateY(-2px)">Get your ticket</span>'
        '<span class="btn ghost" style="font-size:24px">See the agenda</span></div>'
        '<p class="small" style="margin-top:26px">Primary, its hover (darker, never lighter), and secondary. Pill shaped, 44px tall or more, verbs for labels.</p></div>'
        '<div class="card" style="padding:44px">'
        '<div class="h" style="font-size:32px">FOCUS AND STATES</div>'
        '<div style="margin-top:34px;display:flex;gap:26px;align-items:center">'
        '<span class="btn" style="font-size:24px;outline:3px solid var(--tint);outline-offset:3px">Book a call</span>'
        '<span class="tag" style="font-size:20px;color:var(--tint)">Selected <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:var(--o);margin-left:8px"></span></span></div>'
        '<ul class="list small" style="margin-top:30px"><li>A 3px focus ring, 3px offset, on every focusable item.</li>'
        '<li>Selected means a marker plus a word or icon change. Colour is never the only signal.</li>'
        '<li>Disabled at 40%, and say why.</li></ul></div>'
        '<div class="card" style="padding:44px">'
        '<div class="h" style="font-size:32px">SHAPE</div>'
        '<div style="margin-top:34px;display:flex;gap:22px;align-items:flex-end">'
        '<div style="width:90px;height:90px;border-radius:10px;border:3px solid var(--tint)"></div>'
        '<div style="width:120px;height:120px;border-radius:14px;background:var(--o)"></div>'
        '<div style="width:170px;height:64px;border-radius:999px;border:3px solid #fff"></div></div>'
        '<ul class="list small" style="margin-top:30px"><li>10px for inputs and tags, 14px for cards, pills for buttons.</li>'
        '<li>Sections are square or cut on a diagonal. Never round a section.</li>'
        '<li>Shadows tint Dark Brown, never pure black.</li></ul></div></div>'
        '<p class="copy" style="margin-top:44px">Every value here is a brand token, supplied as JSON, CSS custom properties and SCSS in the downloads.</p></div>'
    )
    bk.add(bk.B["ground"], inner)


def tickets(bk):
    caps = [("Closed", "Early bird", "\u00a3XX", "closed"), ("Open now", "Release 1", "\u00a3XX", "open"), ("Next", "Release 2", "\u00a3XX", "next"), ("Final", "Final release", "\u00a3XX", "final")]
    html = ""
    for i, (state, nm, price, k) in enumerate(caps):
        hgt = 170 + i * 50
        if k == "closed":
            capst = "background:#5a5550;"
        elif k == "open":
            capst = "background:var(--o);box-shadow:0 0 50px rgba(232,113,42,.55);"
        else:
            capst = "border:3px dashed rgba(255,255,255,.5);"
        html += ('<div style="display:flex;flex-direction:column;justify-content:flex-end;align-items:center;position:relative">'
                 '%s<div style="width:100%%;height:%dpx;border-radius:14px 14px 0 0;%s"></div>'
                 '<div style="width:28px;height:28px;border-radius:50%%;background:%s;margin-top:-14px;position:relative;z-index:2;%s"></div>'
                 '<div class="mont" style="font-weight:700;font-size:24px;margin-top:24px;%s">%s</div>'
                 '<div class="mont" style="font-weight:800;font-size:44px;margin-top:6px;%s">%s</div>'
                 '<div class="mont" style="font-weight:700;font-size:20px;letter-spacing:.14em;text-transform:uppercase;margin-top:6px;color:%s">%s</div></div>'
                 % ('<div style="position:absolute;top:-80px;background:#fff;color:var(--db);font:700 20px Montserrat;padding:10px 16px;border-radius:10px;white-space:nowrap">XX left at this price</div>' if k == "open" else "",
                    hgt, capst, "var(--o)" if k in ("closed", "open") else "var(--db)",
                    "box-shadow:0 0 0 8px rgba(232,113,42,.3)" if k == "open" else ("border:3px solid rgba(255,255,255,.5)" if k not in ("closed",) else ""),
                    "opacity:.6" if k == "closed" else "", nm,
                    "text-decoration:line-through;opacity:.6" if k == "closed" else ("color:var(--o)" if k == "open" else ""), price,
                    "var(--o)" if k == "open" else "rgba(255,255,255,.7)", state))
    rail = '<div style="position:absolute;left:0;right:0;bottom:155px;height:6px;background:linear-gradient(90deg,var(--o) 0 37%,rgba(255,255,255,.3) 37%)"></div>'
    inner = (
        '<div class="glow"></div>'
        + '<div class="pad" style="display:grid;grid-template-columns:640px 1fr;gap:90px">'
          '<div><div class="eb" style="font-size:24px">Selling tickets</div>'
          '<div class="h" style="font-size:76px;margin-top:22px">SHOW WHY <em>NOW</em> IS <span class="o">CHEAPEST</span>.</div>'
          '<ul class="list copy" style="margin-top:36px">'
          '<li><b>A way to buy</b> is never more than two scrolls away.</li>'
          '<li><b>The release ladder:</b> closed grey, open orange with what is left at this price, next and final as dashed caps that rise.</li>'
          '<li><b>Sold out stays visible</b> with a dashed outline and the words Sold out. It proves demand.</li>'
          '<li><b>State in words,</b> never colour alone. Prices and stock always come from the shop.</li></ul></div>'
          '<div style="position:relative;padding-top:120px"><div style="position:relative;display:grid;grid-template-columns:repeat(4,1fr);gap:26px;height:620px;align-items:end">%s%s</div>'
          '<span class="sticker white" style="position:absolute;right:0;top:20px;font-size:24px">Example layout</span></div></div>'
        % (html, rail)
    )
    bk.add(bk.B["ground"], inner)


def themes27(bk):
    inner = (
        '<div style="position:absolute;left:0;top:0;bottom:0;width:960px;overflow:hidden">'
        + photo("climb_recap_05.jpg", "fade-bottom", "center 30%")
        + '<div style="position:absolute;left:100px;right:80px;bottom:120px"><div class="eb" style="font-size:24px">Theme one</div>'
          '<div class="h" style="font-size:104px;margin-top:20px">FIND YOUR <span class="o">PEOPLE</span></div>'
          '<p class="lead" style="margin-top:20px">The people you meet are the reason to come. Close conversations, the right rooms, the community that sends each other work.</p></div></div>'
        + '<div style="position:absolute;right:0;top:0;bottom:0;width:960px;overflow:hidden">'
        + photo("climb_consultants_expert.jpg", "fade-bottom", "center 30%")
        + '<div class="glow"></div><div style="position:absolute;left:80px;right:100px;bottom:120px"><div class="eb" style="font-size:24px">Theme two</div>'
          '<div class="h" style="font-size:104px;margin-top:20px">MAIN STAGE <em>MOMENTS</em></div>'
          '<p class="lead" style="margin-top:20px">Short, big moments: sets, announcements, awards and our own formats. Big moments, not keynotes.</p></div></div>'
        + '<div style="position:absolute;left:958px;top:0;bottom:0;width:4px;background:var(--o)"></div>'
        + '<span class="sticker" style="position:absolute;left:800px;top:120px;font-size:30px">Climb27 themes</span>'
    )
    bk.add("", inner)


def share_kit(bk):
    def tile(role, line, ph, rot):
        return ('<div style="position:relative;width:330px;height:430px;flex:none;border-radius:14px;overflow:hidden;transform:rotate(%sdeg);box-shadow:0 30px 70px rgba(0,0,0,.5)">'
                '<div class="ph" style="background-image:url(%s%s);background-position:center 25%%;bottom:40%%"></div>'
                '<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(30,15,5,0) 25%%,var(--db) 58%%)"></div>'
                '<div style="position:absolute;left:22px;top:20px">%s</div>'
                '<div style="position:absolute;left:24px;right:20px;top:200px"><span class="sticker" style="font-size:15px">%s</span>'
                '<div class="h" style="font-size:34px;margin-top:16px">%s</div>'
                '<div style="font-size:15px;margin-top:10px;color:var(--tint)">Your name, Company</div></div>'
                '<div style="position:absolute;left:20px;right:20px;bottom:18px;display:flex;align-items:center;justify-content:space-between;background:var(--ch);border-radius:10px;padding:10px 12px">'
                '%s<span style="background:var(--o);font:800 13px Montserrat;padding:6px 10px;border-radius:6px;text-transform:uppercase">climb-uk.com</span></div></div>'
                % (rot, P, ph, logo("Climb27", "reversed-dark", h=30), role, line, logo("Climb27", "reversed-dark", h=20)))
    inner = (
        '<div class="glow"></div>'
        + '<div class="pad" style="display:grid;grid-template-columns:580px 1fr;gap:40px">'
          '<div><div class="eb" style="font-size:24px">The share kit</div>'
          '<div class="h" style="font-size:76px;margin-top:22px">EVERY GUEST IS A <em>HEADLINE</em> <span class="o">ACT</span>.</div>'
          '<ul class="list copy" style="margin-top:36px">'
          '<li>Every partner, speaker and exhibitor gets a kit: LinkedIn banner, posts, story and square versions, a signature button.</li>'
          '<li>Partners write in their own voice: "We are at Climb27".</li>'
          '<li>Lines partners may use: Official partner of Climb27, Speaking at Climb27, Exhibiting at Climb27.</li></ul></div>'
          '<div style="display:flex;gap:28px;align-items:center;justify-content:center;padding-top:60px">%s%s%s</div></div>'
        % (tile("Attendee", 'I\'M <span class="o">ATTENDING</span><br><em>CLIMB27</em>', "climb_awards_winners.jpg", "-2"),
           tile("Speaker", 'I\'M <span class="o">SPEAKING</span><br>AT <em>CLIMB27</em>', "climb_recap_04.jpg", "1"),
           tile("Partner", 'WE\'RE <span class="o">PARTNERING</span><br>AT <em>CLIMB27</em>', "climb_recap_05.jpg", "3"))
    )
    bk.add("", inner)


def where_group(bk):
    yes = ["Contracts, agreements and proposals", "Invoices, statements and legal lines", "Company decks, reports and documents",
           "Email footers and signatures", "The ClimbGroup Event App", "Job adverts and company pages"]
    no = ["Festival posters, tickets and socials: they lead with ClimbUK or Climb27",
          "Copy that explains who runs or owns what", "A second logo next to ClimbUK on a festival piece"]
    inner = (
        svg(motifs.slabs(W, H, corners=("tr",), length=W * 0.22, thick=H * 0.06))
        + '<div class="glow"></div>'
        + '<div class="pad" style="display:grid;grid-template-columns:1fr 1fr;gap:100px">'
          '<div><div class="eb" style="font-size:24px">Where it appears</div>'
          '<div class="h" style="font-size:84px;margin-top:22px">THE NAME ON THE <em>DOTTED</em> <span class="o">LINE</span>.</div>'
          '<p class="lead" style="margin-top:30px">ClimbGroup is the company name. It signs the paperwork, sends the invoice and owns the app. '
          'It gets the same festival energy as everything else: dark grounds, real photos, one orange word.</p></div>'
          '<div style="padding-top:20px"><div class="h" style="font-size:40px">USE CLIMBGROUP ON</div>'
          '<ul class="list copy" style="margin-top:24px">%s</ul>'
          '<div class="h" style="font-size:40px;margin-top:40px">NOT ON</div>'
          '<ul class="list no copy" style="margin-top:24px">%s</ul></div></div>'
        % ("".join("<li>%s</li>" % y for y in yes), "".join("<li>%s</li>" % n for n in no))
    )
    bk.add("ch", inner)


def documents(bk):
    def page(cover):
        if cover:
            return ('<div style="position:relative;width:400px;height:566px;border-radius:6px;overflow:hidden;background:var(--db);box-shadow:0 30px 70px rgba(0,0,0,.55);transform:rotate(-3deg)">'
                    '<div class="ph" style="background-image:url(%sclimb_expo_floor.jpg);bottom:45%%"></div>'
                    '<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(30,15,5,.2),var(--db) 56%%)"></div>'
                    '%s<div style="position:absolute;left:28px;top:24px">%s</div>'
                    '<div style="position:absolute;left:28px;right:28px;top:330px"><span class="sticker" style="font-size:14px">Partners</span>'
                    '<div class="h" style="font-size:40px;margin-top:14px">PARTNER<br><span class="o">PROPOSAL</span></div>'
                    '<div style="font-size:14px;margin-top:12px;color:var(--lg)">Climb27. 30 June and 1 July 2027.</div></div></div>'
                    % (P, svg(motifs.slabs(400, 566, corners=("br",), length=150, thick=34), 400, 566), logo("ClimbGroup", "reversed-dark", h=26)))
        return ('<div style="position:relative;width:400px;height:566px;border-radius:6px;overflow:hidden;background:#fff;box-shadow:0 30px 70px rgba(0,0,0,.55);transform:rotate(2deg);color:#4A5878;padding:40px 36px">'
                '<div style="display:flex;justify-content:space-between;align-items:center">%s<span style="font:700 11px Montserrat;letter-spacing:.14em;color:var(--deep)">AGREEMENT</span></div>'
                '<div style="width:46px;height:5px;border-radius:3px;background:var(--o);margin-top:40px"></div>'
                '<div class="h" style="font-size:26px;color:var(--ch);margin-top:14px">1. WHAT YOU <span class="o">GET</span></div>'
                '<div style="font-size:13px;line-height:1.6;margin-top:12px">Clear, plain sentences in Open Sans at a size people can read. Headings carry a benefit. Links say where they go.</div>'
                '<div style="height:8px;background:#E9E9E9;border-radius:4px;margin-top:22px"></div><div style="height:8px;background:#E9E9E9;border-radius:4px;margin-top:10px;width:80%%"></div>'
                '<div style="height:8px;background:#E9E9E9;border-radius:4px;margin-top:10px;width:90%%"></div>'
                '<div class="h" style="font-size:26px;color:var(--ch);margin-top:30px">2. KEY <span class="o">DATES</span></div>'
                '<div style="height:8px;background:#E9E9E9;border-radius:4px;margin-top:16px"></div><div style="height:8px;background:#E9E9E9;border-radius:4px;margin-top:10px;width:70%%"></div>'
                '<div style="position:absolute;left:36px;right:36px;bottom:28px;border-top:1px solid #ddd;padding-top:12px;font-size:13px;color:#555">ClimbGroup. Registered details here.</div></div>'
                % logo("ClimbGroup", "full-colour-light", h=22))
    inner = (
        '<div class="glow"></div>'
        + '<div class="pad" style="display:grid;grid-template-columns:1fr 1fr;gap:80px;align-items:center">'
          '<div><div class="eb" style="font-size:24px">Documents and decks</div>'
          '<div class="h" style="font-size:80px;margin-top:22px">A <em>POSTER</em> ON THE FRONT. A <span class="o">PAGE</span> INSIDE.</div>'
          '<ul class="list copy" style="margin-top:36px">'
          '<li><b>Covers are festival:</b> a real photo, a Dark Brown fade, the angled orange slab and a big uppercase title.</li>'
          '<li><b>Inside pages are for reading:</b> White grounds, Body Slate text, Charcoal headings, the short orange rule.</li>'
          '<li><b>Decks:</b> dark title and section slides, light slides for detail. One idea per slide.</li>'
          '<li><b>Legal lines</b> carry the ClimbGroup name and registered details in small type, 13px or 9pt at least.</li></ul></div>'
          '<div style="display:flex;gap:30px;justify-content:center">%s%s</div></div>' % (page(True), page(False))
    )
    bk.add("ch", inner)


def signature(bk):
    b = bk.b
    inner = (
        '<div class="pad" style="display:grid;grid-template-columns:600px 1fr;gap:80px;align-items:center">'
        '<div><div class="eb" style="font-size:24px">Email signatures</div>'
        '<div class="h" style="font-size:76px;margin-top:22px">EVERY EMAIL IS A <span class="o">FLYER</span>.</div>'
        '<ul class="list copy" style="margin-top:36px">'
        '<li>Live text for everything people read, so it works with images off and with screen readers.</li>'
        '<li>One campaign banner, button or sticker, never more. Swap it with each campaign.</li>'
        '<li>Social icons are buttons at 24px, with a 44px version for easier tapping.</li>'
        '<li>Works on light and dark mail themes.</li></ul></div>'
        '<div style="background:#fff;border-radius:14px;padding:50px 54px;color:#4A5878;box-shadow:0 30px 70px rgba(0,0,0,.45)">'
        '<div style="font-size:22px">Kind regards,</div>'
        '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-top:22px">'
        '<div><div class="mont" style="font-weight:700;font-size:30px;color:var(--ch)">Your Name</div>'
        '<div style="font-size:20px;margin-top:4px">Partner Manager</div>'
        '<div style="font-size:20px;margin-top:16px;color:var(--deep);text-decoration:underline;font-weight:600">Book a meeting with me</div>'
        '<div style="font-size:18px;margin-top:14px">T: 0000 000 0000 | climb-uk.com</div></div>'
        '<div style="text-align:right">%s'
        '<div style="display:flex;gap:8px;margin-top:16px;justify-content:flex-end">%s</div></div></div>'
        '<div style="margin-top:30px;height:150px;border-radius:10px;overflow:hidden;position:relative">'
        '<div class="ph" style="background-image:url(%sclimb_crowd_wide.jpg)"></div><div class="layer fade-heat"></div>'
        '<div class="h" style="position:absolute;left:30px;top:30px;font-size:40px">SEE YOU AT <span class="o">CLIMB27</span></div>'
        '<span class="btn" style="position:absolute;left:30px;bottom:22px;font-size:16px;padding:8px 18px">Get your ticket</span></div>'
        '<div style="font-size:14px;margin-top:18px;color:#555">This email and any attachments are confidential.</div></div></div>'
        % (logo(b, "full-colour-light", w=230),
           "".join('<span style="display:inline-block;width:34px;height:34px;border:2px solid var(--o);border-radius:8px;padding:6px">%s</span>' % open(os.path.join(HERE, "assets/social/%s.svg" % g)).read().replace('<svg ', '<svg fill="#C55308" width="18" height="18" ')
                   for g in ("linkedin", "instagram", "tiktok", "x", "bluesky")), P)
    )
    bk.add(bk.B["ground"] or "", inner)


def voice_lines(bk):
    lines = [("Headline energy", "Write like it belongs on a billboard, a stage screen or a festival poster. Short, rhythmic, confident."),
             ("Doing, not dreaming", "Move the reader from inspiration to action. Name the outcome and the next step."),
             ("Curated, not crowded", "Sell the right people in the room and the quality of the conversations. Never sell size."),
             ("Personal, not generic", "Write every piece for one audience. If it could be about any event, rewrite it.")]
    html = "".join('<div><div class="num" style="font-size:110px">0%d</div><div class="h" style="font-size:44px;margin-top:16px">%s</div>'
                   '<p class="copy" style="margin-top:14px">%s</p></div>' % (i + 1, t, d) for i, (t, d) in enumerate(lines))
    inner = (
        '<div class="glow"></div>'
        + '<div class="pad"><div class="eb" style="font-size:24px">The voice in four lines</div>'
          '<div class="h" style="font-size:96px;margin-top:22px">EXCITING <em>AND</em> <span class="o">USEFUL</span>.</div>'
          '<div class="grid" style="grid-template-columns:repeat(4,1fr);gap:56px;margin-top:70px">%s</div></div>' % html
        + '<div style="position:absolute;left:0;right:0;bottom:110px;white-space:nowrap;font:800 italic 92px/1 Montserrat;text-transform:uppercase;color:transparent;-webkit-text-stroke:2px rgba(242,174,134,.35);transform:translateX(-260px)">'
          'Find your people. Then do business with them. Iconic moments. Real advice. No fluff.</div>'
    )
    bk.add(bk.B["ground"], inner)


def voice_rules(bk):
    big = [("No emojis", "Let design and photography carry the energy."), ("No exclamation marks", "Full stops do it with more confidence."),
           ("No dashes", "Use full stops, commas and colons.")]
    rules = ["<b>Full names.</b> ClimbUK, ClimbGroup or the edition, Climb27. Never \u201cClimb\u201d on its own.",
             "<b>No numbers we have not published.</b> No audience sizes or counts of partners or meetings.",
             "<b>No promises we cannot keep.</b> No guarantees, no promised meetings, introductions or funding.",
             "<b>Scarcity only when it is true.</b> Name the release, its price and its state.",
             "<b>No hedges.</b> No TBC, coming soon or we hope. Say what happens, or leave it out.",
             "<b>Real people only.</b> Quotes come from named people who agreed to them.",
             "<b>No vendor names.</b> Say what the reader can do, not what powers it."]
    html = "".join('<div style="text-align:center"><div style="width:150px;height:150px;margin:0 auto;border-radius:50%%;border:6px solid var(--o);position:relative">'
                   '<div style="position:absolute;left:50%%;top:50%%;width:170px;height:6px;background:var(--o);transform:translate(-50%%,-50%%) rotate(-45deg)"></div>'
                   '<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font:800 64px Montserrat;color:#fff">%s</div></div>'
                   '<div class="h" style="font-size:32px;margin-top:22px">%s</div><p class="small" style="margin-top:6px">%s</p></div>'
                   % (g, t, d) for g, (t, d) in zip([":)", "!", "\u2014"], big))
    inner = (
        '<div class="pad" style="display:grid;grid-template-columns:1fr 1fr;gap:90px">'
        '<div><div class="eb" style="font-size:24px">The rules</div>'
        '<div class="h" style="font-size:84px;margin-top:22px">LET THE <em>DESIGN</em> DO THE <span class="o">SHOUTING</span>.</div>'
        '<div class="grid" style="grid-template-columns:repeat(3,1fr);gap:30px;margin-top:70px">%s</div></div>'
        '<ul class="list copy" style="padding-top:40px">%s</ul></div>' % (html, "".join("<li>%s</li>" % r for r in rules))
    )
    bk.add(bk.B["ground"], inner)


def rewrites(bk):
    rows = [("Join thousands of founders at the UK's premier startup event!", "Two days with the founders, investors and advisers who move businesses forward."),
            ("Guaranteed meetings with 50+ investors", "Find investors looking for real deal flow."),
            ("Hear inspiring stories from successful entrepreneurs", "Learn how they grew, and what you can do about it on Monday."),
            ("Exhibit and reach thousands of attendees", "Put your team in front of the businesses that buy what you do."),
            ("Our booking platform makes it easy", "Book your meetings in the event app before you arrive.")]
    html = "".join(
        '<div style="display:grid;grid-template-columns:1fr 80px 1fr;align-items:center;padding:24px 0;border-bottom:1.5px solid rgba(74,88,120,.18)">'
        '<div style="font-size:26px;color:#666;text-decoration:line-through;text-decoration-color:var(--o);text-decoration-thickness:3px">%s</div>'
        '<div style="text-align:center"><span class="chev" style="width:22px;height:22px;border-width:6px;border-color:var(--o)"></span></div>'
        '<div class="mont" style="font-weight:700;font-size:28px;color:var(--ch);line-height:1.3">%s</div></div>' % (a, b) for a, b in rows)
    inner = (
        '<div class="pad"><div class="eb" style="font-size:24px">Rewrites</div>'
        '<div class="h" style="font-size:72px;margin-top:22px">SAME IDEA. <em>BETTER</em> <span class="o">LINE</span>.</div>'
        '<div style="display:grid;grid-template-columns:1fr 80px 1fr;margin-top:40px" class="mont"><div style="font-weight:700;font-size:20px;letter-spacing:.14em;color:#555">BEFORE</div><div></div>'
        '<div style="font-weight:700;font-size:20px;letter-spacing:.14em;color:var(--deep)">AFTER</div></div>%s</div>' % html
    )
    bk.add("wh", inner)


def words(bk):
    rows = [("agenda", "programme, for the schedule"), ("Affiliate Programme", "referral scheme"), ("public sector", "councils"),
            ("connect you with", "introduce you to, matched"), ("fractional leaders", "consultants, when they lead a function"),
            ("fellow founders, peers one step ahead", "other founders"), ("find investors looking for real deal flow", "meet investors, cheque books"),
            ("why your team should come", "can I bring the team?")]
    html = "".join('<div style="display:grid;grid-template-columns:1fr 1fr;padding:15px 0;border-bottom:1.5px solid rgba(255,255,255,.1)">'
                   '<div class="mont" style="font-weight:700;font-size:26px;color:#fff">%s</div><div style="font-size:24px;color:rgba(255,255,255,.65);text-decoration:line-through;text-decoration-color:var(--o)">%s</div></div>' % (a, b) for a, b in rows)
    own = ["The Festival for Business Growth", "Your business. Bigger stage.", "Find Your People", "Main Stage Moments",
           "Iconic moments. Real advice. No fluff.", "Business that feels like a festival."]
    if bk.b == "ClimbGroup":
        own = ["The Festival for Business Growth", "Business that feels like a festival.", "Find your people. Then do business with them.",
               "Meetings with the right people", "Two days. The right rooms. Conversations that move your business."]
    inner = (
        '<div class="glow"></div>'
        + '<div class="pad" style="display:grid;grid-template-columns:1fr 1fr;gap:100px">'
          '<div><div class="eb" style="font-size:24px">Words we use</div>'
          '<div class="h" style="font-size:72px;margin-top:22px;margin-bottom:34px">WRITE <span class="o">THIS</span>. <em>NOT</em> THAT.</div>%s</div>'
          '<div><div class="eb" style="font-size:24px">Lines we own</div>'
          '<div style="margin-top:40px;display:flex;flex-direction:column;gap:26px">%s</div>'
          '<p class="copy" style="margin-top:44px">Programme names are always written this way: Investor Speed Networking, Busk Your Business, the ClimbAwards, ClimbHealth.</p></div></div>'
        % (html, "".join('<div class="h" style="font-size:%dpx;line-height:1.05">%s</div>' % (54 if i < 2 else 42, ('<span class="o">%s</span>' % l) if i == 0 else l) for i, l in enumerate(own)))
    )
    bk.add(bk.B["ground"], inner)


def audiences(bk):
    aud = [("Scaling companies", "Peer to peer, ambitious, practical"), ("Professional services", "Credible and commercial"),
           ("Founders raising", "Candid and founder-first"), ("Universities", "Bring the whole team"),
           ("Investors", "Efficient and selective"), ("Public sector", "Civic and practical"),
           ("Advisers and consultants", "Direct and generous"), ("Fractional leaders", "They take responsibility"),
           ("Incubators and accelerators", "Champion of their cohort")]
    html = "".join('<div class="card" style="padding:30px 32px"><div class="h" style="font-size:30px">%s</div><p class="small" style="margin-top:8px;color:var(--tint)">%s</p></div>' % (a, t) for a, t in aud)
    inner = (
        '<div class="pad" style="display:grid;grid-template-columns:620px 1fr;gap:70px">'
        '<div><div class="eb" style="font-size:24px">Who we talk to</div>'
        '<div class="h" style="font-size:80px;margin-top:22px">ONE PIECE. <em>ONE</em> <span class="o">AUDIENCE</span>.</div>'
        '<p class="copy" style="margin-top:36px">Pick the audience and the channel first. Use their tone and talk about what they need. '
        'Pages for ticket holders and pages for partners stay separate.</p>'
        '<p class="copy" style="margin-top:24px"><b>Every audience can hear:</b> two days, every session, the grand opening and the after parties. '
        'The right people, not the most people.</p></div>'
        '<div class="grid" style="grid-template-columns:repeat(3,1fr);gap:20px;align-content:start;padding-top:20px">%s</div></div>' % html
    )
    bk.add(bk.B["ground"], inner)


def print_merch(bk):
    b = bk.b
    inner = (
        '<div class="pad" style="display:grid;grid-template-columns:1fr 1fr;gap:90px">'
        '<div><div class="eb" style="font-size:24px">Print, merch and signage</div>'
        '<div class="h" style="font-size:76px;margin-top:22px">MAKE IT <em>REAL</em>. MAKE IT <span class="o">MATCH</span>.</div>'
        '<ul class="list copy" style="margin-top:36px">'
        '<li><b>PDF/X-4</b> with fonts embedded, images at 300ppi at final size, 3mm bleed and a 5mm safe zone.</li>'
        '<li><b>Two-colour jobs</b> print Pantone 158 with Black 4 or 419. Big dark areas use rich Dark Brown, not plain black.</li>'
        '<li><b>One finish per piece:</b> soft-touch, spot UV on one line, copper or orange foil, or a deboss.</li>'
        '<li><b>Garments</b> are Dark Brown, Charcoal or black. Orange is for crew, so they are easy to find.</li>'
        '<li><b>Signs:</b> 40mm cap height to read at 10m, 80mm at 20m. Chevrons point the way people turn.</li></ul></div>'
        '<div style="position:relative">'
        '<div style="position:absolute;left:40px;top:40px;width:330px;height:470px;background:var(--db);border-radius:6px;box-shadow:0 30px 70px rgba(0,0,0,.5);transform:rotate(-4deg);overflow:hidden">'
        '<div class="ph" style="background-image:url(%sclimb_band_stage.jpg);bottom:40%%"></div><div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(30,15,5,0) 20%%,var(--db) 60%%)"></div>'
        '<div style="position:absolute;left:22px;top:20px">%s</div>'
        '<div class="h" style="position:absolute;left:24px;bottom:60px;font-size:40px">%s</div>'
        '<div style="position:absolute;left:24px;bottom:26px;font:700 14px Montserrat;color:var(--tint)">climb-uk.com</div></div>'
        '<div style="position:absolute;right:30px;top:0;width:360px;height:420px;border-radius:30px 30px 10px 10px;background:var(--ch);box-shadow:0 30px 70px rgba(0,0,0,.5);display:flex;align-items:center;justify-content:center;transform:rotate(3deg)">%s'
        '<span class="sticker" style="position:absolute;right:-20px;top:30px;font-size:22px">Tote</span></div>'
        '<div style="position:absolute;left:120px;bottom:20px;width:560px;height:96px;border-radius:12px;background:repeating-linear-gradient(90deg,var(--o) 0 140px,var(--o) 140px 280px);display:flex;align-items:center;gap:40px;padding:0 30px;overflow:hidden;transform:rotate(-1deg);box-shadow:0 20px 50px rgba(0,0,0,.4)">%s%s</div>'
        '<p class="small" style="position:absolute;left:120px;bottom:-30px">Woven lanyard: orange ground, logo repeat.</p></div></div>'
        % (P, logo(b, "reversed-dark", h=30), 'WE ARE<br><span class="o">HIRING</span>' if b == "ClimbGroup" else 'FIND YOUR<br><span class="o">PEOPLE</span>', logo(b, "icon", w=200, style="border-radius:20px"),
           logo(b, "mono-white", h=40), logo(b, "mono-white", h=40))
    )
    bk.add(bk.B["ground"], inner)


def video(bk):
    inner = (
        photo("climb_stage_region.jpg", "fade-hero", "center 30%")
        + '<div class="glow"></div>'
        + '<div style="position:absolute;left:120px;top:110px;right:120px;bottom:140px;border:2px solid rgba(255,255,255,.25);border-radius:6px"></div>'
        + '<div style="position:absolute;left:150px;top:140px;font:700 16px Montserrat;letter-spacing:.14em;color:rgba(255,255,255,.7)">TITLE SAFE 5%</div>'
        + '<div style="position:absolute;right:150px;top:140px;opacity:.6">%s</div>' % logo(bk.b, "icon-monogram", w=60)
        + '<div style="position:absolute;left:180px;top:200px;width:900px">'
          '<div class="eb" style="font-size:24px">Video and motion graphics</div>'
          '<div class="h" style="font-size:84px;margin-top:22px">FILM THE <em>FESTIVAL</em>, NOT THE <span class="o">CONFERENCE</span>.</div>'
          '<ul class="list copy" style="margin-top:34px;color:#fff">'
          '<li>Open on a moment, never the logo. The logo sting closes it.</li>'
          '<li>Warm stage light, rich blacks that lean brown, one grade per edition.</li>'
          '<li>4K masters by default, RAW capture at 4K or more. Never upscale.</li>'
          '<li>Captions always on for social. Speech 20dB above music.</li></ul></div>'
        + '<div style="position:absolute;left:180px;bottom:180px;display:flex;align-items:stretch">'
          '<div style="width:8px;background:var(--o)"></div><div style="background:rgba(30,15,5,.85);padding:16px 28px">'
          '<div class="mont" style="font-weight:700;font-size:32px">Speaker Name</div><div style="font-size:22px;color:var(--lg)">Role, Company</div></div></div>'
        + '<span class="sticker" style="position:absolute;left:560px;bottom:240px;font-size:22px">Lower third</span>'
    )
    bk.add("", inner)


def partners(bk):
    b = bk.b
    lead = "ClimbUK" if b != "Climb27" else "Climb27"
    inner = (
        '<div class="glow"></div>'
        + '<div class="pad" style="display:grid;grid-template-columns:1fr 1fr;gap:100px">'
          '<div><div class="eb" style="font-size:24px">Press and partners</div>'
          '<div class="h" style="font-size:80px;margin-top:22px">SIDE BY <em>SIDE</em>. NEVER <span class="o">MERGED</span>.</div>'
          '<ul class="list copy" style="margin-top:36px">'
          '<li><b>Lockup:</b> equal optical height, a 1px rule between, clear space of the l height either side.</li>'
          '<li><b>Partner-led pieces</b> put us on the right. Our pieces put us on the left.</li>'
          '<li><b>On our pieces</b> partner logos sit in one tone, so no brand shouts over another.</li>'
          '<li><b>Never</b> merge the logos, recolour a partner logo in our orange, or promise numbers.</li></ul></div>'
          '<div style="padding-top:60px">'
          '<div class="card" style="height:260px;display:flex;align-items:center;justify-content:center;gap:56px">'
          '<div class="mont" style="font-weight:800;font-size:46px;color:#fff;letter-spacing:.02em;border:3px solid rgba(255,255,255,.6);padding:16px 26px;border-radius:10px">PARTNER</div>'
          '<div style="width:2px;height:110px;background:rgba(255,255,255,.3)"></div>%s</div>'
          '<div class="h" style="font-size:34px;margin-top:50px">LINES PARTNERS MAY USE</div>'
          '<div style="display:flex;flex-wrap:wrap;gap:16px;margin-top:24px">%s</div></div></div>'
        % (logo(lead, "reversed-dark", h=70),
           "".join('<span class="tag" style="font-size:20px;color:var(--tint)">%s</span>' % t for t in
                   ["In partnership with ClimbUK", "Official partner of Climb27", "Headline partner of Climb27", "Speaking at Climb27", "Exhibiting at Climb27"]))
    )
    bk.add(bk.B["ground"], inner)


def accessibility(bk):
    items = [("AA", "everywhere", "Every surface meets WCAG 2.2 AA. AAA themes raise every text pair to 7:1."),
             ("44px", "targets", "Buttons, links, chips and icon buttons. A compact 24px only where space is tight."),
             ("3px", "focus ring", "Always visible on keyboard focus, with a 3px offset."),
             ("13px", "smallest text", "Including micro labels and legal lines. 9pt in print."),
             ("9", "reading grade", "Short sentences, everyday words, one idea each."),
             ("0", "flashes", "Nothing flashes more than three times a second. Motion is always optional.")]
    html = "".join('<div class="card" style="padding:30px 36px"><div class="num" style="font-size:80px">%s</div>'
                   '<div class="h" style="font-size:30px;margin-top:10px">%s</div><p class="copy" style="margin-top:12px;font-size:22px">%s</p></div>' % (n, t, d) for n, t, d in items)
    inner = (
        '<div class="pad"><div class="eb" style="font-size:24px">Accessibility</div>'
        '<div class="h" style="font-size:80px;margin-top:22px">NOBODY STAYS AT THE <em>BACK</em> OF THE <span class="o">ROOM</span>.</div>'
        '<div class="grid" style="grid-template-columns:repeat(3,1fr);gap:24px;margin-top:40px">%s</div>'
        '<p class="copy" style="margin-top:26px">Links say where they go. Alt text says what is happening. Pop-ups can always be closed and never run on a timer.</p></div>' % html
    )
    bk.add(bk.B["ground"], inner)


def downloads(bk):
    kit = ["Logo masters in every variant, SVG and PNG", "Colour tokens as JSON, CSS and SCSS", "Montserrat and Open Sans",
           "155 illustrations", "Templates for documents, decks and social", "Email signature kit and social icons",
           "Photo and video library with credits", "This book and the one-page key rules"]
    inner = (
        '<div class="glow"></div>'
        + svg(motifs.connections(W, H, seed=9, dots=24, region=(0.66, 0.08, 0.97, 0.85)))
        + '<div class="pad" style="width:1100px">'
          '<div class="eb" style="font-size:24px">The downloads</div>'
          '<div class="h" style="font-size:84px;margin-top:22px">EVERYTHING YOU NEED IS IN THE <span class="o">MEDIA KIT</span>.</div>'
          '<ul class="list copy" style="margin-top:40px;columns:2;column-gap:60px">%s</ul>'
          '<div class="card" style="margin-top:50px;padding:36px 40px;display:flex;gap:60px;align-items:center">'
          '<div><div class="mont" style="font-weight:700;font-size:18px;letter-spacing:.16em;color:var(--tint);text-transform:uppercase">Press and partnerships</div>'
          '<div class="mont" style="font-weight:700;font-size:30px;margin-top:10px">%s</div><div class="mont" style="font-weight:700;font-size:30px;margin-top:4px">%s</div></div>'
          '<span class="btn" style="font-size:24px;margin-left:auto">Visit %s</span></div>'
          '<p class="small" style="margin-top:24px">Ask the brand team for anything new rather than making your own, so every piece stays consistent.</p></div>'
        % ("".join("<li>%s</li>" % k for k in kit), COMMON["email"], COMMON["phone"], COMMON["web"])
    )
    bk.add(bk.B["ground"], inner)


def back_cover(bk):
    b, B = bk.b, bk.B
    inner = (
        photo({"ClimbUK": "climb_recap_05.jpg", "Climb27": "climb_crowd_wide.jpg"}.get(b, "climb_awards_winners.jpg"), "fade-hero", "center 35%")
        + '<div class="glow"></div>'
        + '<div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center">'
          '<div class="h" style="font-size:150px;text-shadow:0 2px 12px rgba(0,0,0,.6)">%s</div>'
          '<div style="margin-top:80px">%s</div>'
          '<div class="mont" style="margin-top:40px;font-weight:700;font-size:24px;letter-spacing:.2em;text-transform:uppercase;color:var(--tint)">%s</div></div>'
        % (B["closing_h"], logo(b, "tagline-lockup-reversed", w=620), COMMON["web"])
    )
    bk.add("", inner, foot=False)


ILLUS_ALL = ["microphone", "stage", "trophy", "rocket", "handshake", "people", "ticket-qr", "disco-ball", "megaphone", "lightbulb",
             "coffee", "cheers-bottles", "spotlight", "summit", "ladder", "growth-bars", "target", "confetti-cannon", "badge-speaker",
             "music-notes", "dj-decks", "festival-tent", "string-lights", "money-bag", "chart", "compass", "seedling", "crown",
             "video-camera", "high-five", "pizza-slice", "sunglasses", "medal", "calendar", "headphones"]
ILLUS_GROUP = ["contract", "fountain-pen", "briefcase", "calculator", "pie-chart", "office-block", "handshake", "scales", "laptop",
               "slide-deck", "meeting-table", "certificate", "envelope", "phone", "calendar", "clipboard", "growth-bars", "coin-stack",
               "pound-note", "piggy-bank", "key", "chess-knight", "globe", "notebook", "business-card", "target", "lightbulb",
               "summit", "rocket", "trophy", "people", "coffee", "chain-link", "magnifier", "gears"]
ILLUS_27 = ["stage", "microphone", "lighting-rig", "big-screen", "tickets", "wristband", "stage-pass", "badge-delegate", "badge-partner",
            "badge-speaker", "food-truck", "cocktail", "pint", "disco-ball", "fireworks", "party-popper", "balloons", "bunting",
            "festival-tent", "string-lights", "dj-decks", "record", "applause", "selfie", "goodie-bag", "tote-bag", "bucket-hat",
            "t-shirt", "winners-podium", "trophy", "spotlight-beam", "qr-scan", "high-five", "hello-tag", "sunglasses"]


def build(b):
    bk = Book(b)
    cover(bk)
    bk.section = "Contents"
    contents(bk)
    divider(bk, 0)
    big_idea(bk)
    family(bk)
    if b == "ClimbGroup":
        where_group(bk)
    if b == "Climb27":
        themes27(bk)
    five_rules(bk)
    divider(bk, 1)
    logo_master(bk)
    if b == "Climb27":
        edition_mark(bk)
    logo_variants(bk)
    logo_space(bk)
    logo_icons(bk)
    logo_donts(bk)
    divider(bk, 2)
    colours(bk)
    presets(bk)
    contrast(bk)
    divider(bk, 3)
    typefaces(bk)
    headline_formula(bk)
    type_scale(bk)
    divider(bk, 4)
    motifs_slide(bk)
    devices(bk)
    lineup(bk)
    illustrations(bk, {"ClimbGroup": ILLUS_GROUP, "Climb27": ILLUS_27}.get(b, ILLUS_ALL))
    divider(bk, 5)
    photo_shoot(bk)
    photo_fades(bk)
    photo_rules(bk)
    divider(bk, 6)
    motion(bk)
    digital_ui(bk)
    if b in ("ClimbUK", "Climb27"):
        tickets(bk)
    if b == "ClimbGroup":
        documents(bk)
    divider(bk, 7)
    voice_lines(bk)
    voice_rules(bk)
    rewrites(bk)
    words(bk)
    if b == "ClimbUK":
        audiences(bk)
    divider(bk, 8)
    print_merch(bk)
    video(bk)
    partners(bk)
    if b == "Climb27":
        share_kit(bk)
    if b == "ClimbGroup":
        signature(bk)
    divider(bk, 9)
    accessibility(bk)
    bk.section = "Downloads"
    downloads(bk)
    back_cover(bk)
    title = "%s brand guidelines" % b
    html = ('<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><title>%s</title>'
            '<link rel="stylesheet" href="base.css"><style>@page{size:1920px 1080px;margin:0}</style></head><body>%s</body></html>'
            % (title, "\n".join(bk.render())))
    path = os.path.join(HERE, "%s_brand-guidelines.html" % BRANDS[b]["key"])
    open(path, "w").write(html)
    return path, len(bk.slides)


if __name__ == "__main__":
    for b in (sys.argv[1:] or BRANDS):
        print(*build(b))
