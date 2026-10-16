"""Builds the Climb27 Who was there pack (16:9 pages) as HTML, ready for contrast.cjs and render.cjs.

Every printed word comes from pdf/brochures/climb27_who-was-there.copy.md, which copies the public Who was there
page word for word (wwt_from_page.py writes it): the partners, sessions, speakers, organisations and quotes from
Climb23 to Climb26. The pack
uses the brochure pieces in brochures.py, so it reads as one set with the exhibitor and partner brochures.
Run through build_brochures.sh, which prepares assets/ (logos in assets/wwt/).
"""
import html
import os
import sys

import numpy as np
from PIL import Image

import brochures as b
from brochures import B, C, P, hl, t

WWT = os.path.join(b.PACK, "pdf", "brochures", "climb27_who-was-there.copy.md")
C.update(b.load_copy(WWT))
L = "assets/wwt/"

# The quotes in page order. A source with two quotes has one on the first Climb26 page and one on the last, so the
# same voice never sits on one page or on neighbouring pages (Brochure.check holds the build to it).
Q26 = [[q[0], ", ".join(p for p in q[1:] if p)] for q in C["wwt.quotes26.items"]]
QG = [[q[0], ", ".join(p for p in q[1:] if p)] for q in C["wwt.general.items"]]


def split_pairs(qs):
    """First quote of each source, then the singles, then the second quote of each source."""
    seen, first, second = {}, [], []
    for q in qs:
        name = q[1].split(",")[0]
        seen[name] = seen.get(name, 0) + 1
    count = {}
    for q in qs:
        name = q[1].split(",")[0]
        count[name] = count.get(name, 0) + 1
        (second if count[name] == 2 else first).append(q)
    twice = [q for q in first if seen[q[1].split(",")[0]] == 2]
    once = [q for q in first if seen[q[1].split(",")[0]] == 1]
    return twice, once, second


def balance(fixed, singles):
    """Spread the singles over the pages, longest first onto the page with the fewest characters, so every page
    carries about the same amount of reading."""
    pages = [list(f) for f in fixed]
    for q in sorted(singles, key=lambda q: -len(q[0])):
        min(pages, key=lambda pg: sum(len(x[0]) for x in pg)).append(q)
    return pages


# Climb26: the sources quoted twice open the first of its two quote pages and close the last (six pages apart);
# the singles even the pages out. The quotes about ClimbUK in general the same over three pages, with Mitchell McCombe
# on the first and the last.
# The two longest Climb26 quotes speak about ClimbUK as a whole, so they go with the general quotes, which have three
# pages, and the two Climb26 pages keep room for the rest.
T26, O26, S26 = split_pairs(Q26)
LONG26 = [q for q in O26 if len(q[0]) > 600]
P26 = balance([T26, S26], [q for q in O26 if q not in LONG26])
TG, OG, SG = split_pairs(QG)
# The one short Climb23 quote sits under the longest general quote, on page 8, so that column has no gap at the top.
UNDER = [q for q in OG if q[1].startswith("Gary Crotaz")]
PG = balance([TG, [], SG], [q for q in OG if q not in UNDER] + LONG26)
PG[1] += UNDER

CSS = """
.ltile{display:flex;align-items:center;justify-content:center;background:#fff;border-radius:10px;
  border:2px solid #E9E9E9}
.ltile img{max-width:100%;max-height:100%;object-fit:contain}
.ltile.dark{background:var(--ch)}
.s.ch .ltile{border:0}
.names{columns:3;column-gap:40px;font-size:24px;line-height:1.25}
.names li{list-style:none;break-inside:avoid;padding:0 0 6px 1.1em;position:relative;font-weight:600;color:#404C68}
.names li::before{content:"";position:absolute;left:0;top:.42em;width:.42em;height:.42em;border-right:.14em solid var(--ot);
  border-top:.14em solid var(--ot);transform:rotate(45deg)}
.lineup{font-size:22px;line-height:1.6;hyphens:none}
.lineup b{font-family:Montserrat;font-weight:800;letter-spacing:-.005em}
.lineup i{font-style:normal;font-weight:800;margin:0 .45em}
.s.wh .lineup b{color:var(--ch)} .s.wh .lineup span{color:#404C68} .s.wh .lineup i{color:var(--ot)}
.s.gr .lineup b{color:var(--ch)} .s.gr .lineup span{color:#404C68} .s.gr .lineup i{color:#B04902}
.s.ch .lineup b{color:var(--w)} .s.ch .lineup span{color:var(--lg)} .s.ch .lineup i{color:var(--o)}
.grp{font-family:Montserrat;font-weight:800;font-size:26px;text-transform:uppercase;letter-spacing:.04em;margin:0 0 10px}
.s.wh .grp{color:var(--ot)} .s.gr .grp{color:#B04902} .s.ch .grp{color:var(--tint)}
.sess{display:flex;flex-direction:column;gap:10px;background:rgba(255,255,255,.09);border:1.5px solid rgba(255,255,255,.16);
  border-top:6px solid var(--o);border-radius:14px;padding:18px 24px}
.chips{display:flex;gap:8px}
.sess .chip{height:46px;min-width:52px;max-width:108px;padding:6px 10px}
.chip{height:52px;min-width:72px;max-width:150px;background:#fff;border-radius:8px;padding:8px 12px;display:flex;align-items:center;
  justify-content:center}
.chip img{max-height:100%;max-width:100%;object-fit:contain}
.sess h3{font-family:Montserrat;font-weight:800;font-size:21px;line-height:1.2;color:var(--w)}
.yr{font-family:Montserrat;font-weight:800;font-size:17px;letter-spacing:.12em;text-transform:uppercase}
.s.ch .yr{color:var(--tint)} .s.wh .yr{color:var(--ot)}
.spk{display:flex;align-items:center;gap:18px;background:var(--lg);border-radius:14px;padding:18px 22px;
  border-left:6px solid var(--o)}
.spk .who{flex:1;min-width:0;display:flex;flex-direction:column;gap:6px}
.spk .chip{flex:none;width:92px;min-width:0;height:72px;padding:8px}
.spk .tag{flex:none;width:min-content;background:var(--db);color:var(--w);border-radius:6px;padding:8px 10px;font-family:Montserrat;font-weight:800;font-size:15px;line-height:1.15;letter-spacing:.03em;text-transform:uppercase;text-align:center;transform:rotate(-4deg)}
.spk h3{font-family:Montserrat;font-weight:800;font-size:27px;line-height:1.1;color:var(--ch)}
.spk p{font-size:19px;line-height:1.3;color:#404C68}
.orgs{columns:4;column-gap:36px}
.org{break-inside:avoid;padding:0 0 20px}
.org .head{display:flex;align-items:center;gap:12px;margin-bottom:8px}
.org .chip{height:46px;min-width:0;max-width:116px;padding:5px 8px;border:2px solid #E9E9E9}
.org h3{font-family:Montserrat;font-weight:800;font-size:24px;line-height:1.1;color:var(--ch)}
.org li{list-style:none;font-size:19px;line-height:1.28;color:#404C68;padding:0 0 4px}
.org li b{font-family:Montserrat;font-weight:700;color:var(--ch)}
.intro{font-size:26px;line-height:1.5;color:var(--lg)}
.s.wh .intro,.s.gr .intro{color:#404C68}
"""


def is_light(path):
    """True for a logo drawn in white or near white, which needs a Charcoal tile to be seen."""
    with Image.open(os.path.join(b.HERE, path)) as im:
        a = np.asarray(im.convert("RGBA")).astype(float)
    ink = a[..., :3][a[..., 3] > 128]
    if not len(ink):
        return False
    return ((ink @ [0.2126, 0.7152, 0.0722]) < 200).mean() < 0.03


def logo_grid(logos, x, y, w, h, cols, gap=14, pad=12):
    rows = -(-len(logos) // cols)
    tw = (w - gap * (cols - 1)) / cols
    th = (h - gap * (rows - 1)) / rows
    cells = "".join('<div class="ltile%s" style="padding:%dpx"><img src="%s%s" alt="%s"></div>'
                    % (" dark" if is_light(L + f) else "", pad, L, html.escape(f), html.escape(row[1] if len(row) > 1 else ""))
                    for row in logos for f in row[:1])
    return ('<div style="position:absolute;left:%dpx;top:%dpx;width:%dpx;height:%dpx;display:grid;'
            'grid-template-columns:repeat(%d,1fr);grid-template-rows:repeat(%d,%.1fpx);gap:%dpx">%s</div>'
            % (x, y, w, h, cols, rows, th, gap, cells))


def header(key, size=66, width=1100, intro=True, top=80):
    out = '<div style="position:absolute;left:120px;top:%dpx">%s</div>' % (top, b.head(C[key + ".eyebrow"], C[key + ".headline"], size, width))
    if intro:
        out += ('<p class="intro" style="position:absolute;left:1260px;right:120px;top:%dpx">%s</p>'
                % (top + 40, t(C[key + ".intro"])))
    return out


# ---------------------------------------------------------------- pages

def cover(bk):
    inner = (b.photo(P + "climb_crowd_wide.jpg", "center 40%") + '<div class="layer fade-hero"></div><div class="glow"></div>'
             + '<div style="position:absolute;left:120px;top:96px">%s</div>' % b.logo("Climb27", "reversed-dark", 92)
             + '<div style="position:absolute;left:120px;top:330px;width:1200px">'
               '<div class="eb" style="font-size:24px">%s</div>'
               '<h1 class="h" style="font-size:170px;line-height:.95;margin-top:30px;color:var(--w)">%s</h1>'
               '<div class="rule" style="margin-top:40px"></div>'
               '<p class="intro" style="margin-top:34px;font-size:30px;max-width:980px;color:var(--w)">%s</p></div>'
             % (t(C["wwt.cover.eyebrow"]), hl(C["wwt.cover.headline"]), t(C["wwt.cover.intro"]))
             + '<div class="mont" style="position:absolute;right:120px;bottom:70px;font-weight:800;font-size:30px;color:var(--w)">%s</div>'
             % t(C["shared.site"]))
    bk.add("db", inner, foot=False)


def names_page(bk):
    bk.add("gr", header("wwt.names") + logo_grid(C["wwt.names.logos"], 120, 340, 1680, 610, 12))


def back_page(bk):
    """The organisations that came back: three editions as a lineup, then two editions in columns."""
    three = '<b style="white-space:nowrap">%s</b>' % '</b><i aria-hidden="true">/</i> <b style="white-space:nowrap">'.join(t(n[0]) for n in C["wwt.back.three.items"])
    two = "".join("<li>%s</li>" % t(n[0]) for n in C["wwt.back.two.items"])
    bk.add("wh", header("wwt.back", 60, 1100, top=70)
           + '<div style="position:absolute;left:120px;right:120px;top:300px">'
             '<div class="grp">%s</div><div class="lineup" style="font-size:30px">%s</div>'
             '<div class="grp" style="margin-top:40px">%s</div>'
             '<ul class="names" style="columns:4;column-gap:36px;font-size:23px;margin-top:6px">%s</ul></div>'
           % (t(C["wwt.back.three.title"]), three, t(C["wwt.back.two.title"]), two))


def headliners_page(bk):
    """Speakers people will know, one card each, with their organisation's logo or a sticker naming their sport."""
    def card(r):
        chip = ('<div class="chip"><img src="%s%s" alt=""></div>' % (L, html.escape(r[2]))) if len(r) > 2 and r[2] else ""
        if not chip and len(r) > 3 and r[3]:
            chip = '<div class="tag">%s</div>' % t(r[3])
        role = "<p>%s</p>" % t(r[1]) if r[1] else ""
        return '<div class="spk"><div class="who"><h3>%s</h3>%s</div>%s</div>' % (t(r[0]), role, chip)
    cards = "".join(card(r) for r in C["wwt.headliners.items"])
    bk.add("wh", header("wwt.headliners", 60, 1100, top=70)
           + '<div style="position:absolute;left:120px;right:120px;top:290px;bottom:130px;display:grid;'
             'grid-template-columns:repeat(4,1fr);grid-template-rows:repeat(4,1fr);gap:16px">%s</div>' % cards)


def known_page(bk):
    """Speakers grouped under their organisation, best known first, with its logo where we hold one."""
    groups = {}
    for org, logo, name, role in (r + [""] * (4 - len(r)) for r in C["wwt.known.items"]):
        groups.setdefault(org, (logo, []))[1].append((name, role))
    blocks = []
    for org, (logo, people) in groups.items():
        chip = ('<div class="chip"><img src="%s%s" alt=""></div>' % (L, html.escape(logo))) if logo else ""
        rows = "".join("<li><b>%s</b>%s</li>" % (t(n), (", " + t(r)) if r else "") for n, r in people)
        blocks.append('<div class="org"><div class="head">%s<h3>%s</h3></div><ul>%s</ul></div>' % (chip, t(org), rows))
    bk.add("wh", header("wwt.known", 54, 1100, top=70)
           + '<div class="orgs" style="position:absolute;left:120px;right:120px;top:240px;bottom:140px;column-fill:balance">%s</div>'
           % "".join(blocks))


def sessions_page(bk):
    cards = []
    for s in C["wwt.sessionsall.items"]:
        logos = [f.strip() for f in s[1].split(",") if f.strip()]
        chips = ('<div class="chips">%s</div>' % "".join('<div class="chip"><img src="%s%s" alt=""></div>' % (L, html.escape(f))
                                                         for f in logos)) if logos else ""
        cards.append('<div class="sess"><div class="yr">%s</div>%s<h3>%s</h3></div>' % (t(s[2]), chips, t(s[0])))
    grid = ('<div style="position:absolute;left:120px;right:120px;top:280px;bottom:130px;display:grid;'
            'grid-template-columns:repeat(4,1fr);grid-template-rows:repeat(3,1fr);gap:16px">%s</div>' % "".join(cards))
    bk.add("ch", header("wwt.sessionsall", 54, 1100, top=70) + grid)


def quote_page(bk, cls, key, qs, first, to_first=0):
    bk.pool.quotes[bk.pool.qi:bk.pool.qi] = qs
    got = [bk.pool.quote() for _ in qs]

    def style(i, q):
        if len(q[0]) < 200 and i % 3 == 0:
            return "qbox"
        return ("qdark" if i % 2 else "qwhite") if cls != "ch" else ("qwhite" if i % 2 else "qdark")

    head = header(key, 60, 1680, intro=False)
    top = 220
    if first:
        head += '<p class="intro" style="position:absolute;left:120px;right:120px;top:196px">%s</p>' % t(C[key + ".intro"])
        top = 270
    box = "left:120px;right:120px;top:%dpx;bottom:130px" % top
    if len(got) > 7:
        # Many short quotes: four narrower columns.
        bk.add(cls, head + b.stretch_cols(got, 4, style, lambda q: b.qsize(q, 21, 19), box, 16, "20px 24px"))
        return
    chars = sum(len(q[0]) for q in got)
    size = ((lambda q: b.qsize(q, 30, 22)) if chars < 1300 else (lambda q: b.qsize(q, 23, 20)) if chars < 1900
            else (lambda q: b.qsize(q, 21, 19)))
    bk.add(cls, head + b.stretch_cols(got, 3, style, size, box, to_first=to_first))


def close(bk):
    """The brochures' poster closing page, with the festival dates under the headline."""
    inner = (b.photo(bk.pool.photo(B + "stage_020726080climb26.jpg", B + "crowds_052a3708.jpg"), "center 40%")
             + '<div class="layer" style="background:linear-gradient(180deg,rgba(var(--ink),.1) 0%,rgba(var(--ink),.7) 42%,var(--db) 68%)"></div>'
             + '<div style="position:absolute;left:120px;right:120px;top:290px;text-align:center">'
               '<div class="mont" style="font-weight:900;font-size:150px;line-height:.98;text-transform:uppercase;letter-spacing:-.02em;color:var(--w)">'
               '%s<br><em style="color:var(--o)">%s</em></div>'
               '<div class="mont" style="margin-top:30px;font-weight:700;font-size:40px;color:var(--w)">%s</div></div>'
             % (t(C["wwt.cta.line1"]), t(C["wwt.cta.line2"]), t(C["shared.dates"]))
             + b.cta_footer(C["wwt.cta.button"], "%s<br>%s" % (t(C["shared.contact"]), t(C["shared.url"])),
                            C["wwt.cta.qr"], "who-was-there"))
    bk.add("db", inner, foot=False)


class Pack(b.Brochure):
    def sources(self, q):
        # Attributions here carry the person's job title after their name ("Founder, ..."), so a source is the
        # name alone: two founders are two people.
        return [q[1].split(",")[0].strip().lower()]


def build():
    C["wwt.none"] = []
    bk = Pack("climb27_who-was-there", "Who was there at Climb23 to Climb26", "wwt.none")
    cover(bk)                                                       # 1
    names_page(bk)                                                  # 2 in the room
    back_page(bk)                                                   # 3 who came back
    # The Climb26 quotes on pages 4 and 10 (a source quoted twice on both); the general quotes on 6, 8 and 11.
    quote_page(bk, "ch", "wwt.quotes26", P26[0], True)              # 4
    headliners_page(bk)                                             # 5
    quote_page(bk, "gr", "wwt.general", PG[0], True)                # 6
    known_page(bk)                                                  # 7
    quote_page(bk, "gr", "wwt.general", PG[1], False, len(UNDER))   # 8
    sessions_page(bk)                                               # 9
    quote_page(bk, "wh", "wwt.quotes26", P26[1], False)             # 10
    quote_page(bk, "gr", "wwt.general", PG[2], False)               # 11
    close(bk)                                                       # 12
    return bk


def main():
    bk = build()
    bk.check()
    page = bk.html().replace("</style>", CSS + "</style>", 1)
    with open(os.path.join(b.HERE, bk.slug + ".html"), "w", encoding="utf-8") as f:
        f.write(page)
    print("wrote", bk.slug + ".html", "(%d pages, %d quotes)" % (len(bk.pages), bk.pool.qi))
    # The quotes are other people's words, printed word for word as the website shows them, so the house voice
    # checker (which would ask for "Climb27" in place of "Climb", or drop an exclamation mark) reads every other
    # printed string but not them. The ASCII check still covers them in the copy file.
    said = {q[0] for q in Q26 + QG}
    with open(os.path.join(b.HERE, "brochures_printed.txt"), "a", encoding="utf-8") as f:
        f.write("\n".join(s for s in dict.fromkeys(b.PRINTED) if s not in said) + "\n")


if __name__ == "__main__":
    sys.exit(main())
