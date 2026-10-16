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
Q25 = [[q[0], ", ".join(p for p in q[1:] if p)] for q in C["wwt.quotes25.items"]]
Q24 = [[q[0], ", ".join(p for p in q[1:] if p)] for q in C["wwt.quotes24.items"]]
Q23 = [[q[0], ", ".join(p for p in q[1:] if p)] for q in C["wwt.quotes23.items"]]
BOX = 260  # what a quote box's caption and padding take, counted in characters of quote text


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


# Climb26: the five sources quoted twice open the first page and close the third (four pages apart in the pack);
# the singles even the three pages out. Climb25 the same, with Mitchell McCombe on its first and last pages.
T26, O26, S26 = split_pairs(Q26)
P26 = balance([T26, [], S26], O26)
T25, O25, S25 = split_pairs(Q25)
P25 = balance([T25, [], S25], O25)


def runs(rows, weights, size):
    """rows split, in order, into runs whose sizes follow weights (a first page that also holds a headline takes
    less); size(row) is how much room one row takes."""
    marks = [sum(weights[:i + 1]) / sum(weights) for i in range(len(weights))]
    total, chunks, cur, run = sum(size(r) for r in rows), [], [], 0
    for r in rows:
        w = size(r)
        if cur and len(chunks) < len(weights) - 1 and run + w / 2 > total * marks[len(chunks)]:
            chunks.append(cur)
            cur = []
        cur.append(r)
        run += w
    chunks.append(cur)
    assert [r for c in chunks for r in c] == list(rows), "a run dropped or repeated a row"
    return chunks


# Climb24 has 47 quotes from 47 people, in the page's order over five pages of about the same reading.
P24 = runs(Q24, [1, 1, 1, 1, 1], lambda q: len(q[0]) + BOX)

CSS = """
.ltile{display:flex;align-items:center;justify-content:center;background:#fff;border-radius:10px;
  box-shadow:0 2px 6px rgba(var(--ink),.1)}
.ltile img{max-width:100%;max-height:100%;object-fit:contain}
.ltile.dark{background:var(--ch)}
.s.ch .ltile{box-shadow:none}
.names{columns:3;column-gap:40px;font-size:24px;line-height:1.25}
.names li{list-style:none;break-inside:avoid;padding:0 0 8px 1.1em;position:relative;font-weight:600;color:#404C68}
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
.sess{display:flex;flex-direction:column;gap:16px;background:rgba(255,255,255,.09);border:1.5px solid rgba(255,255,255,.16);
  border-top:6px solid var(--o);border-radius:14px;padding:26px 28px}
.sess .chip{height:64px;width:150px;background:#fff;border-radius:8px;padding:10px 14px;display:flex;align-items:center;justify-content:center}
.sess .chip img{max-height:100%;max-width:100%;object-fit:contain}
.sess h3{font-family:Montserrat;font-weight:800;font-size:24px;line-height:1.2;color:var(--w)}
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


def partners_page(bk):
    items = "".join("<li>%s</li>" % t(p[0]) for p in C["wwt.partners.items"])
    tiles = [(B + "stage_natwest_darren-perry.jpg",), (B + "expo_stand_natwest_busy.jpg", B + "expo_stand_natwest.jpg"),
             (B + "print_stand_instantprint.jpg", B + "print_stand_instantprint_02.jpg")]
    inner = (header("wwt.partners", 66, 900, intro=False)
             + '<p class="intro" style="position:absolute;left:120px;top:290px;width:900px">%s</p>' % t(C["wwt.partners.intro"])
             + '<ul class="names" style="position:absolute;left:120px;right:120px;top:440px;columns:4">%s</ul>' % items
             + "".join(b.tile(bk.pool.photo(*names), 1080 + i * 246, 96, 228, 300, "center 30%") for i, names in enumerate(tiles)))
    bk.add("wh", inner)


def sessions_page(bk):
    cards = []
    for s in C["wwt.sessions.items"]:
        chip = ('<div class="chip"><img src="%s%s" alt=""></div>' % (L, html.escape(s[1]))) if len(s) > 1 else ""
        cards.append('<div class="sess">%s<h3>%s</h3></div>' % (chip, t(s[0])))
    grid = ('<div style="position:absolute;left:120px;right:120px;top:300px;bottom:130px;display:grid;'
            'grid-template-columns:repeat(4,1fr);grid-template-rows:repeat(3,1fr);gap:20px">%s'
            '<div class="tile" style="position:relative">%s</div></div>'
            % ("".join(cards), b.photo(bk.pool.photo(B + "stage_maf-317.jpg", B + "stage_maf-278.jpg"), "center")))
    bk.add("ch", header("wwt.sessions") + grid)


def quote_page(bk, cls, key, qs, first):
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
    size = (lambda q: b.qsize(q, 30, 22)) if sum(len(q[0]) for q in got) < 1300 else (lambda q: b.qsize(q, 23, 20))
    bk.add(cls, head + b.stretch_cols(got, 3, style, size, box))


def width(r):
    """Room a lineup entry takes: names are set in bold, about a tenth wider than the role after them."""
    return len(r[0]) * 1.1 + sum(len(x) for x in r[1:]) + 4


def lineup(rows):
    """Names in bold, each with the role they gave, split by orange slashes."""
    return '<i aria-hidden="true">/</i>'.join(
        ("<b>%s</b> <span>%s</span>" % (t(r[0]), t(r[1])) if len(r) > 1 else "<b>%s</b>" % t(r[0])) for r in rows)


def lineup_first(bk, cls, key, rows, intro=True):
    """The first page of a lineup: the headline, then the names."""
    bk.add(cls, header(key, 54, 1100, intro=intro, top=70)
           + '<div class="lineup" style="position:absolute;left:120px;right:120px;top:240px">%s</div>' % lineup(rows))


def lineup_more(bk, cls, key, rows):
    """A lineup page that carries on from an earlier one: the eyebrow, then the names."""
    bk.add(cls, '<div style="position:absolute;left:120px;top:80px"><div class="eb" style="font-size:22px">%s</div></div>' % t(C[key + ".eyebrow"])
           + '<div class="lineup" style="position:absolute;left:120px;right:120px;top:150px">%s</div>' % lineup(rows))


def more_partners_page(bk, cls):
    """The Climb24 partners and exhibitors and the Climb23 partners, each group under its own title."""
    # Three lists on one page: the lineup is set a size down so all of them fit.
    groups = "".join('<div class="grp"%s>%s</div><div class="lineup" style="font-size:20px">%s</div>'
                     % (' style="margin-top:34px"' if i else "", t(C[k + ".title"]), lineup(C[k + ".items"]))
                     for i, k in enumerate(("wwt.partners24", "wwt.exhibitors24", "wwt.partners23")))
    bk.add(cls, '<div style="position:absolute;left:120px;top:80px"><div class="eb" style="font-size:22px">%s</div></div>'
           % t(C["wwt.partners.eyebrow"])
           + '<div style="position:absolute;left:120px;right:120px;top:140px">%s</div>' % groups)


def climb23_page(bk, cls):
    """The Climb23 sessions as a lineup, with the two Climb23 quotes under them."""
    bk.pool.quotes[bk.pool.qi:bk.pool.qi] = Q23
    got = [bk.pool.quote() for _ in Q23]
    quotes = "".join('<div style="flex:1">%s</div>' % b.quote(q, 26, ("qbox", "qwhite")[i % 2], "height:100%;padding:26px 32px")
                     for i, q in enumerate(got))
    bk.add(cls, header("wwt.sessions23", 60, 1100)
           + '<div class="lineup" style="position:absolute;left:120px;right:120px;top:270px">%s</div>' % lineup(C["wwt.sessions23.items"])
           + '<div style="position:absolute;left:120px;top:640px">%s</div>'
           % b.head(C["wwt.quotes23.eyebrow"], C["wwt.quotes23.headline"], 44, 1680)
           + '<div style="position:absolute;left:120px;right:120px;top:780px;bottom:120px;display:flex;gap:20px">%s</div>' % quotes)


def room_pages(bk, grounds):
    logos = C["wwt.room.logos"]
    half = -(-len(logos) // len(grounds))
    for n, cls in enumerate(grounds):
        part = logos[n * half:(n + 1) * half]
        head = header("wwt.room", 54, 1100, intro=(n == 0), top=70)
        bk.add(cls, head + logo_grid(part, 120, 240, 1680, 710, 12, 10, 8))


def close(bk):
    inner = (b.photo(bk.pool.photo(B + "stage_020726080climb26.jpg", B + "crowds_052a3708.jpg"), "center 40%")
             + '<div class="layer" style="background:linear-gradient(180deg,rgba(var(--ink),.1) 0%,rgba(var(--ink),.7) 42%,var(--db) 68%)"></div>'
             + '<div style="position:absolute;left:120px;right:120px;top:300px;text-align:center">'
               '<div class="mont" style="font-weight:900;font-size:150px;line-height:.98;text-transform:uppercase;letter-spacing:-.02em;color:var(--w)">'
               '%s<br><em style="color:var(--o)">%s</em></div>'
               '<div class="mont" style="margin-top:30px;font-weight:700;font-size:40px;color:var(--w)">%s</div>'
               '<div style="margin-top:40px"><span class="ctabtn" style="font-size:38px">%s</span></div></div>'
             % (t(C["wwt.cta.line1"]), t(C["wwt.cta.line2"]), t(C["shared.dates"]), t(C["wwt.cta.button"]))
             + '<div style="position:absolute;left:120px;right:120px;bottom:70px;display:flex;align-items:center;justify-content:space-between;'
               'border-top:2px solid rgba(255,255,255,.2);padding-top:30px">'
             + b.logo("Climb27", "reversed-dark", 56)
             + '<div class="mont" style="color:var(--w);font-weight:700;font-size:28px;line-height:1.5;text-align:center">%s<br>%s</div>'
             % (t(C["shared.contact"]), t(C["shared.url"]))
             + '<div style="display:flex;align-items:center;gap:20px"><div class="mont" style="color:var(--w);font-weight:800;font-size:22px;width:160px;text-align:right">%s</div>'
               '<div style="background:var(--w);padding:10px;border-radius:10px">%s</div></div></div>'
             % (t(C["wwt.cta.qr"]), b.qr(b.QR_URL % "who-was-there", 150)))
    bk.add("db", inner, foot=False)


class Pack(b.Brochure):
    def sources(self, q):
        # Attributions here carry the person's job title after their name ("Founder, ..."), so a source is the
        # name alone: two founders are two people.
        return [q[1].split(",")[0].strip().lower()]


def build():
    C["wwt.none"] = []
    bk = Pack("climb27_who-was-there", "Who was there at Climb23 to Climb26", "wwt.none")
    sp26 = runs(C["wwt.speakers.items"], [0.88, 1, 1, 1], width)
    orgs = runs(C["wwt.orgs.items"], [0.88, 1, 1], width)
    sp24 = runs(C["wwt.speakers24.items"], [0.88, 1, 1], width)
    sp23 = runs(C["wwt.speakers23.items"], [0.88, 1], width)
    cover(bk)                                                       # 1
    names_page(bk)                                                  # 2
    partners_page(bk)                                               # 3
    more_partners_page(bk, "gr")                                    # 4
    sessions_page(bk)                                               # 5
    # Climb26: its quotes between the speaker pages. A source quoted twice is on pages 6 and 10.
    quote_page(bk, "wh", "wwt.quotes26", P26[0], True)              # 6
    lineup_first(bk, "gr", "wwt.speakers", sp26[0])                 # 7
    quote_page(bk, "ch", "wwt.quotes26", P26[1], False)             # 8
    lineup_more(bk, "wh", "wwt.speakers", sp26[1])                  # 9
    quote_page(bk, "gr", "wwt.quotes26", P26[2], False)             # 10
    lineup_more(bk, "ch", "wwt.speakers", sp26[2])                  # 11
    lineup_more(bk, "wh", "wwt.speakers", sp26[3])                  # 12
    room_pages(bk, ["gr", "ch"])                                    # 13, 14
    # Climb25: its quotes between the pages of where speakers came from; Mitchell McCombe on pages 15 and 20.
    quote_page(bk, "wh", "wwt.quotes25", P25[0], True)              # 15
    lineup_first(bk, "gr", "wwt.orgs", orgs[0], intro=False)        # 16
    quote_page(bk, "ch", "wwt.quotes25", P25[1], False)             # 17
    lineup_more(bk, "wh", "wwt.orgs", orgs[1])                      # 18
    lineup_more(bk, "gr", "wwt.orgs", orgs[2])                      # 19
    quote_page(bk, "ch", "wwt.quotes25", P25[2], False)             # 20
    # Climb24, then Climb23.
    quote_page(bk, "wh", "wwt.quotes24", P24[0], True)              # 21
    lineup_first(bk, "gr", "wwt.speakers24", sp24[0])               # 22
    quote_page(bk, "ch", "wwt.quotes24", P24[1], False)             # 23
    lineup_more(bk, "wh", "wwt.speakers24", sp24[1])                # 24
    quote_page(bk, "gr", "wwt.quotes24", P24[2], False)             # 25
    lineup_more(bk, "wh", "wwt.speakers24", sp24[2])                # 26
    quote_page(bk, "ch", "wwt.quotes24", P24[3], False)             # 27
    quote_page(bk, "gr", "wwt.quotes24", P24[4], False)             # 28
    climb23_page(bk, "ch")                                          # 29
    lineup_first(bk, "wh", "wwt.speakers23", sp23[0])               # 30
    lineup_more(bk, "gr", "wwt.speakers23", sp23[1])                # 31
    close(bk)                                                       # 32
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
    said = {q[0] for q in Q26 + Q25 + Q24 + Q23}
    with open(os.path.join(b.HERE, "brochures_printed.txt"), "a", encoding="utf-8") as f:
        f.write("\n".join(s for s in dict.fromkeys(b.PRINTED) if s not in said) + "\n")


if __name__ == "__main__":
    sys.exit(main())
