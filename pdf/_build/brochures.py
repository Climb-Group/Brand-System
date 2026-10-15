"""Builds the Climb27 exhibitor and partner brochures (16:9 pages) as HTML, ready for contrast.cjs and render.cjs.

Every printed word comes from pdf/brochures/climb27_brochures.copy.md. The layout follows the Climb26 exhibitor
brochure the team liked: photo-led pages, orange label boxes, stand photos with size badges and real quotes, set in
this pack's tokens, type and devices. Grounds change from page to page (white, Light Grey, Climb Orange, Charcoal),
with Dark Brown kept to the cover and one page at most. Each brochure prints at least MIN_QUOTES different quotes and
never repeats one. Run through build_brochures.sh, which prepares assets/.
"""
import glob
import html
import os
import re
import sys

import segno

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.abspath(os.path.join(HERE, "..", ".."))
COPY = os.path.join(PACK, "pdf", "brochures", "climb27_brochures.copy.md")
P = "assets/photos/"
B = "assets/brochure/"
QR_URL = "https://www.climb-uk.com/partnerships?utm_source=brochure&utm_medium=pdf&utm_campaign=climb27_%s"
MIN_QUOTES = 20


# ---------------------------------------------------------------- copy

def load_copy(path=COPY):
    """Read '## key' sections; a section of '- ' lines becomes a list, each line split on ' | '."""
    text = open(path, encoding="utf-8").read()
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    out = {}
    for block in re.split(r"^## ", text, flags=re.M)[1:]:
        key, _, body = block.partition("\n")
        body = body.strip()
        lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
        if lines and all(ln.startswith("- ") for ln in lines):
            out[key.strip()] = [[p.strip() for p in ln[2:].split(" | ")] for ln in lines]
        else:
            out[key.strip()] = " ".join(lines)
    return out


C = load_copy()
PRINTED = []  # every string placed on a page, for the copy checker


def t(s):
    PRINTED.append(s)
    return html.escape(s)


def hl(s):
    """Headline markup: [[word]] in Climb Orange, _word_ in italic."""
    PRINTED.append(re.sub(r"\[\[(.+?)\]\]|_(.+?)_", lambda m: m.group(1) or m.group(2), s))
    s = html.escape(s)
    s = re.sub(r"\[\[(.+?)\]\]", r'<span class="o">\1</span>', s)
    return re.sub(r"_(.+?)_", r"<em>\1</em>", s)


# ---------------------------------------------------------------- pools

class Pool:
    """Hands out photos and quotes so nothing repeats inside one brochure."""

    def __init__(self, quotes_key):
        self.quotes = list(C[quotes_key])
        self.qi = 0
        self.used = set()

    def quote(self):
        if self.qi >= len(self.quotes):
            raise SystemExit("ran out of quotes in the copy file")
        q = self.quotes[self.qi]
        self.qi += 1
        return q

    def photo(self, *names):
        """The first unused file among names; a name ending in * matches every file with that prefix."""
        for name in names:
            folder, _, stem = name.rpartition("/")
            folder = folder + "/" if folder else P
            if stem.endswith("*"):
                found = sorted(os.path.basename(f) for f in glob.glob(os.path.join(HERE, folder, stem)))
            else:
                found = [stem] if os.path.exists(os.path.join(HERE, folder, stem)) else []
            for f in found:
                if folder + f not in self.used:
                    self.used.add(folder + f)
                    return folder + f
        raise SystemExit("no unused photo among %s" % (names,))


# ---------------------------------------------------------------- pieces

def logo(b, variant, h, style=""):
    return '<img src="assets/logos/%s/%s_%s.svg" style="height:%dpx;%s" alt="%s">' % (b, b, variant, h, style, b)


def illo(name, color="var(--o)", size=96):
    s = open(os.path.join(HERE, "assets/illus/%s.svg" % name), encoding="utf-8").read()
    s = s[s.index("<svg"):]
    s = re.sub(r"<title>.*?</title>|<desc>.*?</desc>", "", s, flags=re.S)
    return s.replace("<svg ", '<svg aria-hidden="true" style="width:%dpx;height:%dpx;flex:none;color:%s" ' % (size, size, color), 1)


def qr(data, size):
    q = segno.make(data, error="m")
    rows = [list(r) for r in q.matrix]
    n = len(rows)
    d = "".join("M%d %dh1v1h-1z" % (x, y) for y, r in enumerate(rows) for x, v in enumerate(r) if v)
    return ('<svg viewBox="-2 -2 %d %d" width="%d" height="%d" shape-rendering="crispEdges" style="background:#fff;display:block">'
            '<title>QR code</title><path fill="#1E0F05" d="%s"/></svg>' % (n + 4, n + 4, size, size, d))


def photo(src, pos="center", style=""):
    return '<div class="ph" style="background-image:url(%s);background-position:%s;%s"></div>' % (src, pos, style)


def tile(src, x, y, w, h, pos="center"):
    return '<div class="tile" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx">%s</div>' % (x, y, w, h, photo(src, pos))


def collage(pool, x, y, w, h, rows, names, gap=18):
    """rows: one list of relative widths per row, with an optional ('h', weight) first item for the row height."""
    out = []
    weights = [r[0][1] if r and isinstance(r[0], tuple) else 1 for r in rows]
    rows = [[c for c in r if not isinstance(c, tuple)] for r in rows]
    total_h = h - gap * (len(rows) - 1)
    ty = y
    for r, wt in zip(rows, weights):
        rh = round(total_h * wt / sum(weights))
        total_w = w - gap * (len(r) - 1)
        tx = x
        for cw in r:
            pw = round(total_w * cw / sum(r))
            out.append(tile(pool.photo(*names), tx, ty, pw, rh))
            tx += pw + gap
        ty += rh + gap
    return "".join(out)


def labels(lines, size, cls="lbl", ital_last=True):
    out = []
    for i, line in enumerate(lines):
        body = t(line)
        if ital_last and i == len(lines) - 1:
            body = "<em>%s</em>" % body
        out.append('<div class="%s" style="font-size:%dpx;margin-left:%dpx">%s</div>' % (cls, size, i * size * 0.9, body))
    return "".join(out)


def quote(q, size=30, cls="qbox", style=""):
    text, who = q
    return ('<figure class="quote %s" style="%s"><blockquote style="font-size:%dpx">&ldquo;%s&rdquo;</blockquote>'
            '<figcaption>%s</figcaption></figure>' % (cls, style, size, t(text), t(who)))


def qsize(q, big=34, small=24):
    """Long quotes set smaller so every box keeps to its space."""
    n = len(q[0])
    return big if n < 70 else (big - 4 if n < 120 else (small + 2 if n < 190 else small))


def head(eyebrow, headline, size=86, width=1000):
    return ('<div class="eb" style="font-size:22px">%s</div>'
            '<h2 class="h" style="font-size:%dpx;max-width:%dpx;margin-top:26px">%s</h2>' % (t(eyebrow), size, width, hl(headline)))


class Brochure:
    def __init__(self, slug, title, quotes_key):
        self.slug, self.title, self.pages = slug, title, []
        self.pool = Pool(quotes_key)

    def add(self, cls, inner, foot=True):
        self.pages.append((cls, inner, foot))

    def html(self):
        out = []
        for n, (cls, inner, foot) in enumerate(self.pages, 1):
            f = ""
            if foot:
                c = cls.split()
                variant = ("full-colour-grey" if "gr" in c else "full-colour-light" if "wh" in c
                           else "mono-white" if "or" in c else "reversed-dark")
                f = ('<div class="foot">%s<div class="pg"><span>%s</span><b>%02d</b></div></div>'
                     % (logo("Climb27", variant, 30), t(C["shared.tagline"]), n))
            out.append('<section class="s %s">%s%s</section>' % (cls, inner, f))
        return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>%s</title>'
                '<link rel="stylesheet" href="base.css"><style>%s</style></head><body>%s</body></html>'
                % (html.escape(self.title), CSS, "".join(out)))

    def check(self):
        quotes = self.pool.quotes[:self.pool.qi]
        if len(quotes) < MIN_QUOTES:
            raise SystemExit("%s prints %d quotes; the rule is at least %d" % (self.slug, len(quotes), MIN_QUOTES))
        if len({q[0] for q in quotes}) != len(quotes):
            raise SystemExit("%s repeats a quote" % self.slug)
        grounds = [c.split()[0] for c, _, _ in self.pages]
        if grounds.count("db") > 2:
            raise SystemExit("%s uses Dark Brown on %d pages; keep it to two" % (self.slug, grounds.count("db")))
        for a, b in zip(grounds, grounds[1:]):
            if a == b:
                raise SystemExit("%s has two %s pages in a row" % (self.slug, a))


CSS = """
@page{size:1920px 1080px;margin:0}
.s.db{background:var(--db)}
.lbl{display:table;background:var(--o);color:var(--w);font-family:Montserrat;font-weight:800;text-transform:uppercase;
  letter-spacing:-.015em;line-height:1;padding:.12em .28em .14em;margin-bottom:.08em}
.lbl em{font-style:italic}
.lbl.dark{background:var(--db)}
.s.or .h .o{color:var(--db)}
.s.gr .h .o{color:#D5641E}
.s.or .eb{color:var(--db)}
.tile{position:absolute;overflow:hidden;border-radius:12px}
.quote{margin:0}
.quote blockquote{font-family:Montserrat;font-weight:700;line-height:1.24;letter-spacing:-.005em}
.quote figcaption{font-size:19px;margin-top:14px;font-weight:600}
.qbox{background:var(--o);color:var(--w);padding:32px 36px;border-radius:12px}
.qbox figcaption{color:var(--db)}
.qdark{background:var(--db);color:var(--w);padding:32px 36px;border-radius:12px}
.qdark figcaption{color:var(--tint)}
.qwhite{background:var(--w);color:var(--ch);padding:32px 36px;border-radius:12px;box-shadow:0 4px 14px rgba(var(--ink),.12)}
.qwhite figcaption{color:var(--deep)}
.qabs{position:absolute}
.badge{position:absolute;width:180px;height:180px;border-radius:50%;background:var(--o);color:var(--w);display:flex;
  flex-direction:column;align-items:center;justify-content:center;font-family:Montserrat;font-weight:800;font-size:32px;
  line-height:1;text-align:center;box-shadow:0 14px 40px rgba(var(--or),.45)}
.badge small{font-size:19px;font-weight:700;margin-bottom:6px}
.price{display:inline-flex;align-items:baseline;gap:14px;white-space:nowrap;background:var(--db);color:var(--w);font-family:Montserrat;font-weight:800;
  font-size:52px;padding:14px 26px;border-radius:10px}
.price small{font-size:22px;font-weight:700;color:var(--tint)}
.row{display:flex;gap:28px;align-items:flex-start}
.row h3{font-family:Montserrat;font-weight:800;font-size:28px;text-transform:uppercase;letter-spacing:-.005em;color:var(--w)}
.row p{font-size:21px;line-height:1.5;color:var(--lg);margin-top:6px}
.s.wh .row h3,.s.gr .row h3{color:var(--ch)} .s.wh .row p,.s.gr .row p{color:#404C68}
.s.or .row h3{color:var(--db)} .s.or .row p{color:var(--db)}
.cards{position:absolute;display:grid;gap:26px}
.cardx{display:flex;flex-direction:column;background:var(--ch);border-radius:14px;overflow:hidden;border:1.5px solid rgba(255,255,255,.08)}
.cardx .img{position:relative;flex:none;height:300px;background:#2f2d2b}
.cardx .body{display:flex;flex-direction:column;flex:1;padding:28px 30px 30px}
.cardx .k{font-family:Montserrat;font-weight:700;font-size:18px;letter-spacing:.16em;text-transform:uppercase;color:var(--tint)}
.cardx h3{font-family:Montserrat;font-weight:800;font-size:34px;text-transform:uppercase;letter-spacing:-.01em;margin-top:10px;line-height:1}
.cardx .d{font-size:21px;line-height:1.5;color:var(--lg);margin-top:12px}
.cardx .end{margin-top:auto;padding-top:22px;display:flex;flex-direction:column;gap:6px;font-family:Montserrat;font-weight:800;font-size:40px;color:var(--w)}
.cardx .end small{font-size:19px;font-weight:700;color:var(--tint)}
.s.wh .cardx,.s.gr .cardx{background:#fff;border:0;box-shadow:0 4px 12px rgba(var(--ink),.1),0 2px 4px rgba(var(--ink),.06)}
.s.wh .cardx h3,.s.gr .cardx h3,.s.wh .cardx .end,.s.gr .cardx .end{color:var(--ch)}
.s.wh .cardx .d,.s.gr .cardx .d{color:#404C68}
.s.wh .cardx .k,.s.gr .cardx .k,.s.wh .cardx .end small,.s.gr .cardx .end small{color:var(--deep)}
.ctabtn{display:inline-flex;align-items:center;font-family:Montserrat;font-weight:800;font-size:32px;border-radius:999px;
  background:var(--w);color:var(--ot);padding:22px 40px;white-space:nowrap;box-shadow:0 14px 40px rgba(var(--ink),.25)}
.step{position:relative;padding-top:150px}
.step .numo{position:absolute;top:0;left:-6px;font-size:190px}
.step h3{font-family:Montserrat;font-weight:800;font-size:32px;text-transform:uppercase;line-height:1.05;letter-spacing:-.01em}
.step p{font-size:22px;line-height:1.5;margin-top:16px}
.s.or .step h3,.s.or .step p{color:var(--db)} .s.or .numo{-webkit-text-stroke-color:var(--db)}
.s.gr .step h3,.s.wh .step h3{color:var(--ch)} .s.gr .step p,.s.wh .step p{color:#404C68}
.icard{display:flex;flex-direction:column;gap:12px;background:var(--ch);border-radius:14px;padding:32px 32px 34px;border:1.5px solid rgba(255,255,255,.08)}
.icard h3{font-family:Montserrat;font-weight:800;font-size:28px;text-transform:uppercase;letter-spacing:-.005em}
.icard p{font-size:20px;line-height:1.5;color:var(--lg)}
.s.wh .icard,.s.gr .icard{background:#fff;border:0;box-shadow:0 4px 12px rgba(var(--ink),.1),0 2px 4px rgba(var(--ink),.06)}
.s.wh .icard h3,.s.gr .icard h3{color:var(--ch)} .s.wh .icard p,.s.gr .icard p{color:#404C68}
.icard.hi,.s.wh .icard.hi,.s.gr .icard.hi{background:var(--o);border:0;box-shadow:none}
.icard.hi h3,.icard.hi p,.s.wh .icard.hi h3,.s.wh .icard.hi p{color:var(--db)}
.s.gr .list li,.s.wh .list li{color:#404C68}
.s.or .list li{color:var(--db)} .s.or .list li::before{border-color:var(--db)}
.arrow{font-family:Montserrat;font-weight:800;color:var(--db)}
"""


# ---------------------------------------------------------------- shared pages

def cover(bk, line1, line2, img, pos):
    inner = (photo(img, pos) + '<div class="layer fade-hero"></div><div class="glow"></div>'
             + '<div style="position:absolute;left:120px;top:96px">%s</div>' % logo("Climb27", "reversed-dark", 92)
             + '<div style="position:absolute;left:120px;top:340px">%s'
               '<div class="mont" style="margin-top:34px;font-weight:700;font-size:44px;color:var(--w)">%s</div>'
               '<div class="rule" style="margin-top:30px"></div></div>' % (labels([line1, line2], 132), t(C["shared.tagline"]))
             + '<div style="position:absolute;left:120px;bottom:110px"><span class="sticker" style="font-size:34px">%s</span></div>'
             % t(C["shared.dates"])
             + '<div class="mont" style="position:absolute;right:120px;bottom:70px;font-weight:800;font-size:30px;color:var(--w)">climb-uk.com</div>')
    bk.add("db", inner, foot=False)


def what(bk, names):
    """White page: what Climb27 is, beside a wall of photos, with one quote under the words."""
    rows = "".join('<div class="row" style="margin-top:20px;align-items:center">%s<p style="margin:0;font-size:21px">%s</p></div>'
                   % (illo(icon, size=54), t(f[0])) for icon, f in zip(("calendar", "people", "shopfront"), C["shared.what.facts"]))
    photos = collage(bk.pool, 960, 80, 840, 860, [[("h", 1.15), 3, 2], [2, 2, 2], [2, 3]], names)
    q = bk.pool.quote()
    inner = ('<div style="position:absolute;left:120px;top:90px;width:770px">%s'
             '<p class="copy" style="margin-top:26px;font-size:22px">%s</p>%s</div>%s'
             '<div class="qabs" style="left:120px;bottom:130px;width:770px">%s</div>'
             % (head(C["shared.what.eyebrow"], C["shared.what.headline"], 72, 770), t(C["shared.what.body"]), rows, photos,
                quote(q, qsize(q, 26, 19), "qbox")))
    bk.add("wh", inner)


def wall(bk, cls, eyebrow, headline, names, n_quotes, layout):
    """A page of quotes in two columns, with photos beside them."""
    qs = [bk.pool.quote() for _ in range(n_quotes)]
    styles = ["qbox", "qwhite" if cls == "db" else "qdark", "qdark" if cls == "wh" else "qwhite"]
    cells = "".join('<div style="break-inside:avoid;margin-bottom:20px">%s</div>' % quote(q, qsize(q, 24, 18), styles[i % 3])
                    for i, q in enumerate(qs))
    if layout == "a":
        pics = collage(bk.pool, 120, 290, 500, 650, [[1], [1, 1]], names)
        grid = '<div style="position:absolute;left:650px;right:120px;top:290px;bottom:130px;columns:2;column-gap:20px">%s</div>' % cells
    else:
        pics = collage(bk.pool, 1300, 96, 500, 844, [[1, 1], [("h", 1.3), 1], [1, 1]], names)
        grid = '<div style="position:absolute;left:120px;width:1150px;top:290px;bottom:130px;columns:2;column-gap:20px">%s</div>' % cells
    inner = '<div style="position:absolute;left:120px;top:96px">%s</div>%s%s' % (head(eyebrow, headline, 66, 1150), pics, grid)
    bk.add(cls, inner)


def cta(bk, line1, line2, button, qr_line, img, campaign):
    """Closing page in the Climb26 manner: an orange photo ground, the QR code centred in a white card beside the big lines."""
    inner = (photo(img, "center 35%") + '<div class="layer" style="background:rgba(var(--or),.88)"></div>'
             + '<div style="position:absolute;left:160px;top:240px;width:380px;height:440px;background:#fff;border-radius:16px;'
               'display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18px;'
               'box-shadow:0 20px 50px rgba(var(--ink),.25)">%s'
               '<div class="mont" style="font-weight:800;font-size:24px;color:#1E0F05;text-align:center">%s</div></div>'
             % (qr(QR_URL % campaign, 300), t(qr_line))
             + '<div style="position:absolute;left:600px;top:250px">%s</div>' % labels([line1, line2], 104, "lbl dark")
             + '<div style="position:absolute;left:600px;top:540px;display:flex;align-items:center;gap:22px">'
               '<span class="arrow" style="font-size:44px" aria-hidden="true">&larr;</span><span class="ctabtn">%s</span></div>' % t(button)
             + '<div class="mont" style="position:absolute;left:600px;top:670px;font-weight:700;font-size:30px;color:var(--db);line-height:1.5">%s<br>%s</div>'
             % (t(C["shared.contact"]), t(C["shared.url"]))
             + '<div style="position:absolute;left:160px;bottom:110px;display:flex;gap:48px;align-items:center">%s%s</div>'
             % (logo("Climb27", "mono-white", 60), logo("ClimbUK", "mono-white", 44))
             + '<div style="position:absolute;right:120px;bottom:116px;font-size:21px;color:var(--db);font-weight:600">%s</div>' % t(C["shared.vat"]))
    bk.add("or", inner, foot=False)


# ---------------------------------------------------------------- exhibitor

EXHIBITOR_PHOTOS = (B + "expo_floor_*", P + "exhibitor_*", B + "expo_stand_*", B + "expo_stands_*", P + "climb_recap_04.jpg", B + "floor_joy.jpg",
                    B + "entrance_arrivals.jpg", P + "meetings_*", P + "joy_*", P + "crowds_*", P + "food_and_vendors_*", P + "media_*")


def stand_page(bk, cls, key, names, size_text, unit=None, render=None):
    pool = bk.pool
    inc = "".join("<li>%s</li>" % t(i[0]) for i in C["exhibitor.%s.includes" % key])
    many = len(C["exhibitor.%s.includes" % key]) > 7
    price = '<div class="price" style="margin-top:22px">%s%s</div>' % (
        t(C["exhibitor.%s.price" % key]), ("<small>%s</small>" % t(unit)) if unit else "")
    strap_col = "#7A3B16" if cls == "gr" else "var(--deep)"
    text = ('<div style="position:absolute;left:120px;top:80px;width:640px">'
            '<span class="tag" style="font-size:18px;color:%s">%s</span>'
            '<div style="margin-top:26px">%s</div>'
            '<div class="mont" style="margin-top:24px;font-weight:800;font-size:30px;color:%s;line-height:1.2">%s</div>'
            '<p class="copy" style="margin-top:16px;font-size:22px">%s</p>'
            '<div class="mont" style="margin-top:20px;font-weight:800;font-size:20px;letter-spacing:.14em;text-transform:uppercase;color:var(--ch)">Includes</div>'
            '<ul class="list copy" style="margin-top:10px;font-size:20px;line-height:1.4;%s">%s</ul>%s</div>'
            % (strap_col, t(C["exhibitor.%s.eyebrow" % key]), labels([C["exhibitor.%s.name" % key]], 66, ital_last=False), strap_col,
               t(C["exhibitor.%s.strap" % key]), t(C["exhibitor.%s.body" % key]),
               "columns:2;column-gap:28px" if many else "", inc, price))
    mid = tile(pool.photo(*names), 800, 80, 600, 560)
    if render:
        low = ('<div class="tile" style="left:800px;top:664px;width:290px;height:276px;background:#fff">'
               '<div style="position:absolute;inset:14px;background:url(%s) center/contain no-repeat"></div></div>' % render)
    else:
        low = tile(pool.photo(*names), 800, 664, 290, 276)
    low += tile(pool.photo(*names), 1110, 664, 290, 276)
    q = pool.quote()
    right = (tile(pool.photo(*names), 1424, 80, 376, 400)
             + '<div class="qabs" style="left:1424px;top:504px;width:376px">%s</div>' % quote(q, qsize(q, 24, 18), "qbox"))
    badge = '<div class="badge" style="left:1010px;top:562px"><small>%s</small>%s</div>' % (
        "from" if size_text.lower().startswith("from") else "size", t(re.sub(r"^[Ff]rom ", "", size_text)).replace(" x ", "x"))
    bk.add(cls, text + mid + low + right + badge)


def exhibitor():
    bk = Brochure("climb27_exhibitor-brochure", "Exhibit at Climb27", "exhibitor.quotes")
    pool = bk.pool
    # 1 Cover: the stand sits to the right, clear of the words.
    cover(bk, C["exhibitor.cover.line1"], C["exhibitor.cover.line2"], pool.photo(B + "expo_stand_screen-demo.jpg"), "80% 40%")
    # 2 What Climb27 is, beside a wall of exhibitor photos.
    what(bk, EXHIBITOR_PHOTOS)

    # 3 Why exhibit, on orange.
    reasons = "".join('<div class="row" style="margin-bottom:24px">%s<div><h3>%s</h3><p>%s</p></div></div>'
                      % (illo(r[0], color="var(--db)", size=66), t(r[1]), t(r[2])) for r in C["exhibitor.why.reasons"])
    q = pool.quote()
    inner = (collage(pool, 120, 96, 700, 580, [[("h", 1.2), 1], [1, 1]], EXHIBITOR_PHOTOS)
             + '<div class="qabs" style="left:120px;top:700px;width:700px">%s</div>' % quote(q, qsize(q, 28, 20), "qdark")
             + '<div style="position:absolute;left:900px;top:90px;width:900px">%s<div style="margin-top:34px">%s</div></div>'
             % (head(C["exhibitor.why.eyebrow"], C["exhibitor.why.headline"], 72, 900), reasons))
    bk.add("or", inner)

    # 4 Stand options, each with a real photo.
    cards = []
    for key, names in (("pod", (B + "stand_pod_growth-hub.jpg",)), ("display", (B + "stand_display_in-use.jpg",)),
                       ("expo", (B + "expo_stand_natwest.jpg",)), ("market", (P + "food_and_vendors_01.jpg",) + EXHIBITOR_PHOTOS)):
        size = C.get("exhibitor.%s.size" % key, "")
        unit = C.get("exhibitor.%s.unit" % key)
        desc = size or C["exhibitor.market.body"].split(".")[0] + "."
        cards.append('<div class="cardx"><div class="img" style="height:240px">%s</div><div class="body"><div class="k">%s</div><h3>%s</h3>'
                     '<div class="d">%s</div><div class="end">%s%s</div></div></div>'
                     % (photo(pool.photo(*(names + EXHIBITOR_PHOTOS))), t(C["exhibitor.%s.eyebrow" % key]), t(C["exhibitor.%s.name" % key]),
                        t(desc), t(C["exhibitor.%s.price" % key]), ("<small>%s</small>" % t(unit)) if unit else ""))
    inner = ('<div style="position:absolute;left:120px;top:96px">%s<p class="copy" style="margin-top:20px;font-size:25px">%s</p></div>'
             '<div class="cards" style="left:120px;right:120px;top:380px;bottom:130px;grid-template-columns:repeat(4,1fr)">%s</div>'
             % (head(C["exhibitor.stands.eyebrow"], C["exhibitor.stands.headline"], 72, 1500), t(C["exhibitor.stands.intro"]), "".join(cards)))
    bk.add("gr", inner)

    # 5-7 One page per stand.
    stand_page(bk, "wh", "pod", (B + "stand_pod_*", B + "stand_starter-pod_in-use.jpg") + EXHIBITOR_PHOTOS,
               C["exhibitor.pod.size"], render=B + "stand_starter-pod_render.jpg")
    stand_page(bk, "gr", "display", (B + "stand_display_in-use*", B + "expo_stand_activation.jpg") + EXHIBITOR_PHOTOS,
               C["exhibitor.display.size"], render=B + "stand_display_render.jpg")
    stand_page(bk, "wh", "expo", (B + "expo_stand_think-big.jpg", B + "expo_stands_overhead*") + EXHIBITOR_PHOTOS,
               C["exhibitor.expo.size"], unit=C["exhibitor.expo.unit"])

    # 8 The marketplace has its own page.
    who = "".join("<li>%s</li>" % t(w[0]) for w in C["exhibitor.market.who"])
    inc = "".join("<li>%s</li>" % t(w[0]) for w in C["exhibitor.market.includes"])
    q = pool.quote()
    inner = ('<div style="position:absolute;left:120px;top:90px;width:860px">'
             '<div class="eb" style="font-size:22px">%s</div>'
             '<h2 class="h" style="font-size:76px;margin-top:26px">%s</h2>'
             '<p style="margin-top:26px;font-size:23px;line-height:1.55;color:var(--db)">%s</p>'
             '<div style="display:flex;gap:40px;margin-top:28px">'
             '<div style="flex:1.2"><div class="mont" style="font-weight:800;font-size:20px;letter-spacing:.14em;text-transform:uppercase;color:var(--db)">%s</div>'
             '<ul class="list" style="margin-top:14px;font-size:20px;line-height:1.4">%s</ul></div>'
             '<div style="flex:1"><div class="mont" style="font-weight:800;font-size:20px;letter-spacing:.14em;text-transform:uppercase;color:var(--db)">Includes</div>'
             '<ul class="list" style="margin-top:14px;font-size:20px;line-height:1.4">%s</ul></div></div>'
             '<div class="price" style="margin-top:22px">%s<small>%s</small></div></div>'
             % (t(C["exhibitor.market.name"]), hl(C["exhibitor.market.strap"]), t(C["exhibitor.market.body"]),
                t(C["exhibitor.market.who.eyebrow"]), who, inc, t(C["exhibitor.market.price"]), t(C["exhibitor.market.unit"]))
             + collage(pool, 1060, 90, 740, 540, [[1, 1], [1]], (P + "food_and_vendors_*", P + "outdoor_seating_*") + EXHIBITOR_PHOTOS)
             + '<div class="qabs" style="left:1060px;top:654px;width:740px">%s</div>' % quote(q, qsize(q, 26, 19), "qwhite"))
    bk.add("or", inner)

    # 9 Extras, with the print partner.
    items = "".join('<div class="icard" style="padding:24px 26px">%s<h3 style="font-size:24px">%s</h3><p style="font-size:19px">%s</p></div>'
                    % (illo(i[0], size=52), t(i[1]), t(i[2])) for i in C["exhibitor.extras.items"])
    pr = C["exhibitor.extras.print"][0]
    items += ('<div class="icard hi" style="padding:24px 26px">%s<h3 style="font-size:24px">%s</h3><p style="font-size:19px">%s</p></div>'
              % (illo("gift-box", color="var(--db)", size=52), t(pr[0]), t(pr[1])))
    q = pool.quote()
    inner = ('<div class="glow tl"></div><div style="position:absolute;left:120px;top:96px">%s<p class="copy" style="margin-top:20px;font-size:25px;max-width:1300px">%s</p></div>'
             '<div class="cards" style="left:120px;width:1100px;top:340px;bottom:140px;grid-template-columns:repeat(3,1fr)">%s</div>'
             % (head(C["exhibitor.extras.eyebrow"], C["exhibitor.extras.headline"], 72, 1500), t(C["exhibitor.extras.intro"]), items)
             + tile(pool.photo(B + "print_stand_instantprint.jpg", *EXHIBITOR_PHOTOS), 1250, 340, 550, 300)
             + '<div class="qabs" style="left:1250px;top:660px;width:550px">%s</div>' % quote(q, qsize(q, 24, 18), "qbox"))
    bk.add("ch", inner)

    # 10-11 In their words.
    wall(bk, "gr", C["shared.proof.eyebrow"], C["shared.proof.headline"], EXHIBITOR_PHOTOS, 7, "a")
    wall(bk, "db", C["exhibitor.proof2.eyebrow"], C["exhibitor.proof2.headline"], EXHIBITOR_PHOTOS, 6, "b")

    # 12 Book a call.
    cta(bk, C["exhibitor.cta.line1"], C["exhibitor.cta.line2"], C["exhibitor.cta.button"], C["exhibitor.cta.qr"],
        pool.photo(B + "expo_hall_wide.jpg", *EXHIBITOR_PHOTOS), "exhibitor")
    return bk


# ---------------------------------------------------------------- partner

PARTNER_PHOTOS = (B + "expo_floor_*", B + "expo_stand_*", B + "entrance_arrivals.jpg", B + "floor_joy.jpg", P + "exhibitor_*",
                  P + "vip_and_awards_*", P + "stage_speakers_*", P + "audience_at_stage_*", P + "meetings_*", P + "joy_*",
                  P + "crowds_*", P + "roundtable_and_workshops_*", P + "climb_recap_*", P + "media_*")


def partner():
    bk = Brochure("climb27_partner-brochure", "Partner with Climb27", "partner.quotes")
    pool = bk.pool
    cover(bk, C["partner.cover.line1"], C["partner.cover.line2"], pool.photo(P + "stage_speakers_02.jpg"), "center 35%")
    what(bk, PARTNER_PHOTOS)

    # 3 Why partner, on Light Grey beside a photo wall.
    cols = "".join('<div class="step" style="padding-top:140px"><div class="numo" aria-hidden="true" style="font-size:160px">%02d</div><h3>%s</h3><p>%s</p></div>'
                   % (n, t(p[0]), t(p[1])) for n, p in enumerate(C["partner.why.points"], 1))
    q = pool.quote()
    inner = ('<div style="position:absolute;left:120px;top:96px">%s</div>' % head(C["partner.why.eyebrow"], C["partner.why.headline"], 78, 1100)
             + '<div style="position:absolute;left:120px;width:1080px;top:380px;display:grid;grid-template-columns:repeat(3,1fr);gap:46px">%s</div>' % cols
             + collage(pool, 1260, 96, 540, 540, [[1], [1, 1]], PARTNER_PHOTOS)
             + '<div class="qabs" style="left:1260px;top:660px;width:540px">%s</div>' % quote(q, qsize(q, 24, 18), "qbox"))
    bk.add("gr", inner)

    # 4 How it works, on orange.
    steps = "".join('<div class="step"><div class="numo" aria-hidden="true">%02d</div><h3>%s</h3><p>%s</p></div>'
                    % (n, t(s[0]), t(s[1])) for n, s in enumerate(C["partner.how.steps"], 1))
    q = pool.quote()
    inner = ('<div style="position:absolute;left:120px;top:96px">%s</div>'
             '<div style="position:absolute;left:120px;right:120px;top:360px;display:grid;grid-template-columns:repeat(4,1fr);gap:56px">%s</div>'
             '<div class="qabs" style="left:120px;right:120px;top:770px">%s</div>'
             % (head(C["partner.how.eyebrow"], C["partner.how.headline"], 80, 1500), steps, quote(q, qsize(q, 26, 20), "qdark")))
    bk.add("or", inner)

    # 5 What a partner can own; the website is included with every partnership.
    inc = C["partner.own.included"][0]
    items = ('<div class="icard hi">%s<h3>%s</h3><p>%s</p></div>' % (illo(inc[0], color="var(--db)", size=68), t(inc[1]), t(inc[2]))
             + "".join('<div class="icard">%s<h3>%s</h3><p>%s</p></div>' % (illo(i[0], size=68), t(i[1]), t(i[2])) for i in C["partner.own.items"]))
    inner = ('<div style="position:absolute;left:120px;top:96px">%s</div>' % head(C["partner.own.eyebrow"], C["partner.own.headline"], 76, 1100)
             + '<div class="cards" style="left:120px;width:1120px;top:340px;bottom:130px;grid-template-columns:repeat(3,1fr)">%s</div>' % items
             + collage(pool, 1280, 96, 520, 844, [[1], [1, 1], [1]], (B + "kiosk_lanyards.jpg",) + PARTNER_PHOTOS))
    bk.add("wh", inner)

    # 6 In their words, with a wall of exhibitor photos.
    wall(bk, "gr", C["partner.proof3.eyebrow"], C["partner.proof3.headline"], PARTNER_PHOTOS, 6, "a")

    # 7 Zones, on Charcoal.
    zone_names = [(P + "climb_consultants_expert.jpg",), (P + "meetings_02.jpg",), (P + "exhibitor_01.jpg",), (P + "media_01.jpg",)]
    zones = "".join('<div class="cardx"><div class="img" style="height:300px">%s</div><div class="body"><h3>%s</h3><div class="d">%s</div></div></div>'
                    % (photo(pool.photo(*(n + PARTNER_PHOTOS))), t(z[0]), t(z[1])) for n, z in zip(zone_names, C["partner.zones.items"]))
    pitch = C["partner.zones.pitch"][0]
    inner = ('<div class="glow tl"></div><div style="position:absolute;left:120px;top:96px">%s<p class="copy" style="margin-top:20px;font-size:25px;max-width:1300px">%s</p></div>'
             '<div class="cards" style="left:120px;right:120px;top:380px;height:500px;grid-template-columns:repeat(4,1fr)">%s</div>'
             '<div style="position:absolute;left:120px;top:910px;display:flex;align-items:center;gap:24px">'
             '<span class="sticker" style="font-size:24px;transform:rotate(-3deg)">%s</span>'
             '<span class="mont" style="font-weight:800;font-size:30px;color:var(--w)">%s</span></div>'
             % (head(C["partner.zones.eyebrow"], C["partner.zones.headline"], 76, 1300), t(C["partner.zones.intro"]), zones, t(pitch[0]), t(pitch[1])))
    bk.add("ch", inner)

    # 8 Sessions and awards, on Light Grey.
    stage_names = [(P + "roundtable_and_workshops_02.jpg",), (P + "climb_awards_winners.jpg",), (P + "stage_speakers_03.jpg",)]
    offers = "".join('<div class="cardx"><div class="img" style="height:250px">%s</div><div class="body">%s<h3 style="margin-top:16px">%s</h3>'
                     '<div class="d">%s</div><div class="end">%s</div></div></div>'
                     % (photo(pool.photo(*(n + PARTNER_PHOTOS))), illo(o[0], size=56), t(o[1]), t(o[2]), t(o[3]))
                     for n, o in zip(stage_names, C["partner.stage.items"]))
    inner = ('<div style="position:absolute;left:120px;top:96px">%s</div>'
             '<div class="cards" style="left:120px;right:120px;top:300px;bottom:130px;grid-template-columns:repeat(3,1fr)">%s</div>'
             % (head(C["partner.stage.eyebrow"], C["partner.stage.headline"], 76, 1500), offers))
    bk.add("gr", inner)

    # 9 Add more, on white.
    items = "".join('<div class="icard">%s<h3>%s</h3><p>%s</p></div>' % (illo(i[0], color="#C55308", size=64), t(i[1]), t(i[2]))
                    for i in C["partner.more.items"])
    q = pool.quote()
    inner = ('<div style="position:absolute;left:120px;top:96px">%s</div>' % head(C["partner.more.eyebrow"], C["partner.more.headline"], 76, 1100)
             + '<div class="cards" style="left:120px;width:1120px;top:300px;bottom:130px;grid-template-columns:repeat(3,1fr)">%s</div>' % items
             + tile(pool.photo(*PARTNER_PHOTOS), 1280, 96, 520, 460)
             + '<div class="qabs" style="left:1280px;top:580px;width:520px">%s</div>' % quote(q, qsize(q, 24, 18), "qbox"))
    bk.add("wh", inner)

    # 10-11 In their words.
    wall(bk, "db", C["shared.proof.eyebrow"], C["shared.proof.headline"], PARTNER_PHOTOS, 5, "b")
    wall(bk, "gr", C["partner.proof2.eyebrow"], C["partner.proof2.headline"], PARTNER_PHOTOS, 5, "a")

    cta(bk, C["partner.cta.line1"], C["partner.cta.line2"], C["partner.cta.button"], C["partner.cta.qr"],
        pool.photo(P + "climb_crowd_wide.jpg", *PARTNER_PHOTOS), "partner")
    return bk


def main():
    for bk in (exhibitor(), partner()):
        bk.check()
        with open(os.path.join(HERE, bk.slug + ".html"), "w", encoding="utf-8") as f:
            f.write(bk.html())
        print("wrote", bk.slug + ".html", "(%d pages, %d quotes)" % (len(bk.pages), bk.pool.qi))
    # Everything printed, one string per line, for the climb-voice checker.
    with open(os.path.join(HERE, "brochures_printed.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(dict.fromkeys(PRINTED)) + "\n")


if __name__ == "__main__":
    sys.exit(main())
