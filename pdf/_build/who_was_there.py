"""Builds the Climb27 Who was there pack (16:9 pages) as HTML, ready for contrast.cjs and render.cjs.

Every printed word comes from pdf/brochures/climb27_who-was-there.copy.md, which copies the public Who was there
page word for word: the partners, sessions, speakers, organisations and quotes from Climb25 and Climb26. The pack
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
.lineup{font-size:22px;line-height:1.6;text-align:justify;hyphens:none}
.lineup b{font-family:Montserrat;font-weight:800;text-transform:uppercase;letter-spacing:-.005em}
.lineup i{font-style:normal;font-weight:800;margin:0 .45em}
.s.wh .lineup b{color:var(--ch)} .s.wh .lineup span{color:#404C68} .s.wh .lineup i{color:var(--ot)}
.s.gr .lineup b{color:var(--ch)} .s.gr .lineup span{color:#404C68} .s.gr .lineup i{color:#B04902}
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
    bk.add("gr", header("wwt.names") + logo_grid(C["wwt.names.logos"], 120, 340, 1680, 610, 11))


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
        head += '<p class="intro" style="position:absolute;left:120px;top:196px;width:1200px">%s</p>' % t(C[key + ".intro"])
        top = 270
    size = (lambda q: b.qsize(q, 30, 22)) if sum(len(q[0]) for q in got) < 1300 else (lambda q: b.qsize(q, 23, 20))
    bk.add(cls, head + b.stretch_cols(got, 3, style, size, "left:120px;right:120px;top:%dpx;bottom:130px" % top))


def speaker_chunks(weights):
    """The speakers split into runs whose lengths follow weights (the first page also holds the headline)."""
    n = len(weights)
    marks = [sum(weights[:i + 1]) / sum(weights) for i in range(n)]
    people = [p + [""] * (2 - len(p)) for p in C["wwt.speakers.items"]]  # some speakers gave no role
    sizes = [len(p[0]) + len(p[1]) + 4 for p in people]
    total, chunks, cur, run = sum(sizes), [], [], 0
    for p, w in zip(people, sizes):
        if cur and len(chunks) < n - 1 and run + w / 2 > total * marks[len(chunks)]:
            chunks.append(cur)
            cur = []
        cur.append(p)
        run += w
    chunks.append(cur)
    assert [p for c in chunks for p in c] == people, "the lineup dropped or repeated a speaker"
    return chunks


def speaker_page(bk, cls, people, first):
    """The speakers as a festival lineup: names in bold capitals, each with the role they gave, split by orange
    slashes."""
    body = '<i aria-hidden="true">/</i>'.join(("<b>%s</b> <span>%s</span>" % (t(p[0]), t(p[1])) if p[1] else "<b>%s</b>" % t(p[0])) for p in people)
    if first:
        head = header("wwt.speakers", 54, 1100, top=70)
    else:
        head = '<div style="position:absolute;left:120px;top:80px"><div class="eb" style="font-size:22px">%s</div></div>' % t(C["wwt.speakers.eyebrow"])
    bk.add(cls, head + '<div class="lineup" style="position:absolute;left:120px;right:120px;top:%dpx">%s</div>'
           % (240 if first else 150, body))


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
    bk = Pack("climb27_who-was-there", "Who was there at Climb25 and Climb26", "wwt.none")
    sp = speaker_chunks([0.88, 1, 1, 1])
    cover(bk)                                               # 1
    names_page(bk)                                          # 2
    quote_page(bk, "ch", "wwt.quotes26", P26[0], True)      # 3
    partners_page(bk)                                       # 4
    quote_page(bk, "gr", "wwt.quotes26", P26[1], False)     # 5
    sessions_page(bk)                                       # 6
    quote_page(bk, "wh", "wwt.quotes26", P26[2], False)     # 7
    speaker_page(bk, "gr", sp[0], True)                     # 8
    quote_page(bk, "ch", "wwt.quotes25", P25[0], True)      # 9
    speaker_page(bk, "wh", sp[1], False)                    # 10
    quote_page(bk, "gr", "wwt.quotes25", P25[1], False)     # 11
    speaker_page(bk, "wh", sp[2], False)                    # 12
    quote_page(bk, "ch", "wwt.quotes25", P25[2], False)     # 13
    speaker_page(bk, "wh", sp[3], False)                    # 14
    room_pages(bk, ["gr", "ch"])                            # 15, 16
    close(bk)                                               # 17
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
    said = {q[0] for q in Q26 + Q25}
    with open(os.path.join(b.HERE, "brochures_printed.txt"), "a", encoding="utf-8") as f:
        f.write("\n".join(s for s in dict.fromkeys(b.PRINTED) if s not in said) + "\n")


if __name__ == "__main__":
    sys.exit(main())
