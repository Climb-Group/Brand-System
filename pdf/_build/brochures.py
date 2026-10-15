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
from PIL import Image

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
        self.reserved = set()  # only handed out when named exactly, never through a * pattern

    def take(self, who):
        """The quote from one named source, moved up so it is handed out now and never again."""
        rest = self.quotes[self.qi:]
        q = next(q for q in rest if q[1] == who)
        rest.remove(q)
        self.quotes[self.qi:] = [q] + rest
        return self.quote()

    def quote(self):
        if self.qi >= len(self.quotes):
            raise SystemExit("ran out of quotes in the copy file")
        q = self.quotes[self.qi]
        self.qi += 1
        return q

    def photo(self, *names, shape=None):
        """The first unused file among names; a name ending in * matches every file with that prefix.

        With shape (the tile's width over its height), a photo that would lose more than a third of its
        width or height to the crop is passed over, so a conversation or a logo wall is never cut in half.
        Only when no named photo fits the shape does the first unused one win."""
        if shape:
            for name in names:
                f = self._first(name, lambda f: fits(f, shape))
                if f:
                    return f
        for name in names:
            f = self._first(name)
            if f:
                return f
        raise SystemExit("no unused photo among %s" % (names,))

    def _first(self, name, ok=lambda f: True):
        folder, _, stem = name.rpartition("/")
        folder = folder + "/" if folder else P
        if stem.endswith("*"):
            found = [f for f in sorted(os.path.basename(f) for f in glob.glob(os.path.join(HERE, folder, stem)))
                     if folder + f not in self.reserved]
        else:
            found = [stem] if os.path.exists(os.path.join(HERE, folder, stem)) else []
        taken = {look(u) for u in self.used}
        for f in found:
            if folder + f not in self.used and look(folder + f) not in taken and ok(folder + f):
                self.used.add(folder + f)
                return folder + f
        return None


_SIZES = {}
_LOOKS = {}


def look(src):
    """An average hash of the photo, so the same picture saved under two names counts as one."""
    if src not in _LOOKS:
        with Image.open(os.path.join(HERE, src)) as im:
            px = im.convert("L").resize((16, 16)).tobytes()
        mean = sum(px) / len(px)
        _LOOKS[src] = bytes(p > mean for p in px)
    return _LOOKS[src]


def fits(src, shape, keep=0.67):
    """True when a cover crop of src into a tile of this shape keeps at least keep of its width and height."""
    if src not in _SIZES:
        with Image.open(os.path.join(HERE, src)) as im:
            _SIZES[src] = im.size
    w, h = _SIZES[src]
    return min(shape / (w / h), (w / h) / shape) >= keep


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
            out.append(tile(pool.photo(*names, shape=pw / rh), tx, ty, pw, rh))
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
    if cls == "qbox":
        size = max(size, 19)  # white on Climb Orange: 19px bold at least
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
        self.marks = []
        self.pool = Pool(quotes_key)

    def add(self, cls, inner, foot=True):
        self.pages.append((cls, inner, foot))
        self.marks.append(self.pool.qi)

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
        # Two quotes from the same person or organisation never share a page or sit on neighbouring pages.
        # A source is each part of the attribution except roles such as "Climb26 exhibitor".
        def who(q):
            return [p.strip().lower() for p in q[1].split(",") if not re.search(r"\b(exhibitor|partner)\b", p, re.I)]
        starts = [0] + self.marks[:-1]
        sources = [{p for q in quotes[a:b] for p in who(q)} for a, b in zip(starts, self.marks)]
        for n, here in enumerate(sources):
            per_page = [p for q in quotes[starts[n]:self.marks[n]] for p in who(q)]
            if len(per_page) != len(set(per_page)):
                raise SystemExit("%s quotes one source twice on page %d" % (self.slug, n + 1))
            # Nor within two pages, so a reader never meets one source in quotes one after the other.
            for back in (1, 2):
                if n >= back and here & sources[n - back]:
                    raise SystemExit("%s quotes %s on pages %d and %d"
                                     % (self.slug, ", ".join(sorted(here & sources[n - back])), n - back + 1, n + 1))
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
.qbox figcaption{color:var(--w);font-weight:700;font-size:19px}
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
.cardx .img{position:relative;flex:none;height:300px;background:var(--ch)}
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
.stepsbig .step h3{font-size:36px} .stepsbig .step p{font-size:25px;margin-top:20px}
.steps2 .step{padding:0 0 0 200px;min-height:120px} .steps2 .step .numo{font-size:130px;top:-4px} .steps2 .step p{margin-top:10px}
.s.or .step h3,.s.or .step p{color:var(--db)} .s.or .numo{-webkit-text-stroke-color:var(--db)}
.s.gr .step h3,.s.wh .step h3{color:var(--ch)} .s.gr .step p,.s.wh .step p{color:#404C68}
.icard{display:flex;flex-direction:column;gap:12px;background:var(--ch);border-radius:14px;padding:32px 32px 34px;border:1.5px solid rgba(255,255,255,.08)}
.icard h3{font-family:Montserrat;font-weight:800;font-size:28px;text-transform:uppercase;letter-spacing:-.005em}
.icard p{font-size:20px;line-height:1.5;color:var(--lg)}
.s.wh .icard,.s.gr .icard{background:#fff;border:0;box-shadow:0 4px 12px rgba(var(--ink),.1),0 2px 4px rgba(var(--ink),.06)}
.s.wh .icard h3,.s.gr .icard h3{color:var(--ch)} .s.wh .icard p,.s.gr .icard p{color:#404C68}
.s.ch .icard:not(.hi),.s.ch .cardx{background:rgba(255,255,255,.09);border:1.5px solid rgba(255,255,255,.16);border-top:6px solid var(--o)}
.pcard{position:relative;display:flex;flex-direction:column;align-items:center;text-align:center;justify-content:center;
  background:#fff;border-radius:16px;padding:50px 26px 16px;box-shadow:0 4px 12px rgba(var(--ink),.1),0 2px 4px rgba(var(--ink),.06);border-bottom:6px solid var(--o)}
.pcard .pin{position:absolute;top:-46px;left:50%;width:92px;height:92px;border-radius:50%;background:var(--o);border:5px solid #fff;--doodle-ground:var(--o);
  display:flex;align-items:center;justify-content:center;box-shadow:0 6px 14px rgba(232,113,42,.35)}
.pcard h3{font-family:Montserrat;font-weight:800;font-size:26px;text-transform:uppercase;letter-spacing:-.005em;color:var(--ch)}
.pcard p{font-size:19px;line-height:1.4;color:#404C68;margin-top:6px;max-width:440px}
.icard.hi,.s.wh .icard.hi,.s.gr .icard.hi{background:var(--o);border:0;box-shadow:none}
.icard.hi h3,.icard.hi p,.s.wh .icard.hi h3,.s.wh .icard.hi p{color:var(--w)} .icard.hi p{font-weight:700}
.s.gr .list li,.s.wh .list li{color:#404C68}
.s.or .list li{color:var(--db)} .s.or .list li::before{border-color:var(--db)}
.arrow{font-family:Montserrat;font-weight:800;color:var(--db)}
.fade-cover{background:linear-gradient(90deg,rgba(var(--ink),.82),rgba(var(--ink),.6) 38%,rgba(var(--ink),.12) 62%,rgba(var(--ink),0) 78%),
  linear-gradient(180deg,rgba(var(--ink),0) 70%,rgba(var(--ink),.8))}
"""


# ---------------------------------------------------------------- shared pages

def cover(bk, line1, line2, img, pos, style="", fade="fade-hero"):
    inner = (photo(img, pos, style) + '<div class="layer %s"></div><div class="glow"></div>' % fade
             + '<div style="position:absolute;left:120px;top:96px">%s</div>' % logo("Climb27", "reversed-dark", 92)
             + '<div style="position:absolute;left:120px;top:340px">%s'
               '<div class="mont" style="margin-top:34px;font-weight:700;font-size:44px;color:var(--w)">%s</div>'
               '<div class="rule" style="margin-top:30px"></div></div>' % (labels([line1, line2], 132), t(C["shared.tagline"]))
             + '<div style="position:absolute;left:120px;bottom:110px"><span class="sticker" style="font-size:34px">%s</span></div>'
             % t(C["shared.dates"])
             + '<div class="mont" style="position:absolute;right:120px;bottom:70px;font-weight:800;font-size:30px;color:var(--w)">%s</div>' % t(C["shared.site"]))
    bk.add("db", inner, foot=False)


# Page 2 photos, in collage order: varied stands, so shots of one area's stands never sit side by side.
# The owner's picks of general expo traffic; the two shots of one group sit apart.
WHAT_PHOTOS = (B + "expo_floor_maf-238.jpg", B + "expo_floor_maf-341.jpg", B + "expo_floor_maf-244.jpg",
               B + "expo_floor_maf-242.jpg", B + "expo_floor_052a3113.jpg", B + "expo_floor_maf-339.jpg",
               B + "expo_floor_maf-342.jpg")
# The owner's picks per stand size, the zones and setup day; handed out only where a page names them.
POD_PHOTOS = (B + "stand_display_in-use.jpg", B + "expo_floor_dsc03145.jpg", B + "expo_floor_dsc03098.jpg",
              B + "expo_floor_dsc03083.jpg", B + "expo_floor_maf-428.jpg")
DISPLAY_PHOTOS = (B + "expo_floor_maf-344.jpg", B + "expo_floor_052a2042.jpg")
EXPO_PHOTOS = (B + "expo_floor_maf-432.jpg", B + "expo_floor_maf-435.jpg", B + "expo_floor_dsc03182.jpg")
SIZE_PHOTOS = ((B + "expo_floor_maf-431.jpg", B + "expo_floor_dsc03044.jpg"),
               (B + "expo_floor_maf-234.jpg", B + "expo_floor_dsc03152.jpg"),
               (B + "expo_floor_maf-410.jpg", B + "stand_pod_03.jpg"))
ZONE_PHOTOS = (B + "branding_052a3130.jpg", B + "branding_maf-448.jpg", B + "branding_052a3125.jpg",
               B + "branding_maf-404.jpg", B + "branding_maf-395.jpg", B + "branding_maf-389.jpg")
SETUP_PHOTOS = (B + "setup_maf-1.jpg", B + "setup_052a0597.jpg", B + "setup_052a0617.jpg")
PICKS = set(POD_PHOTOS + DISPLAY_PHOTOS + EXPO_PHOTOS + sum(SIZE_PHOTOS, ()) + ZONE_PHOTOS + SETUP_PHOTOS
            + (B + "expo_floor_maf-415.jpg",))
# The partner brochure's page 2 shows the festival a partner puts its name to: stages, awards, crowds and a few stands.
PARTNER_WHAT_PHOTOS = (B + "stage_020726080climb26.jpg", B + "awards_052a3981.jpg", B + "stage_maf-317.jpg",
                       B + "busk_maf-168.jpg", B + "festival_busy_052a3708.jpg", B + "stage_maf-519.jpg",
                       B + "expo_stand_natwest_busy.jpg")
# Talks held on a stand: right for nothing in these brochures, which show stages for talks and stands for meetings.
STAND_TALKS = {B + "expo_floor_052a3109.jpg"}
# Photos the owner asked us not to use in the brochures.
SET_ASIDE = {B + "stage_020726018climb26.jpg", B + "expo_floor_052a5456.jpg", B + "entrance_arrivals.jpg"}


def what(bk, names, first=WHAT_PHOTOS):
    """White page: what Climb27 is, beside a wall of photos, with one quote under the words."""
    names = tuple(first) + tuple(names)
    rows = "".join('<div class="row" style="margin-top:20px;align-items:center">%s<p style="margin:0;font-size:21px">%s</p></div>'
                   % (illo(icon, size=54), t(f[0])) for icon, f in zip(("calendar", "people", "shopfront"), C["shared.what.facts"]))
    photos = collage(bk.pool, 960, 80, 840, 860, [[("h", 1.15), 3, 2], [2, 2, 2], [2, 3]], names)
    q = bk.pool.quote()
    inner = ('<div style="position:absolute;left:120px;top:90px;width:770px">%s'
             '<p class="copy" style="margin-top:26px;font-size:22px">%s</p>%s'
             '<div style="margin-top:40px">%s</div></div>%s'
             % (head(C["shared.what.eyebrow"], C["shared.what.headline"], 64, 770), t(C["shared.what.body"]), rows,
                quote(q, qsize(q, 26, 19), "qbox"), photos))
    bk.add("wh", inner)


def stretch_cols(qs, k, style_of, size_of, box, gap=20, pad="26px 30px"):
    """Quotes in k columns that all reach the bottom of the box: each column takes the next quote while it is the
    shortest, and its boxes grow to fill it, so no column stops early and leaves a gap above the footer."""
    cols, load = [[] for _ in range(k)], [0] * k
    for i, q in enumerate(qs):
        c = load.index(min(load))
        cols[c].append(quote(q, size_of(q), style_of(i, q), "flex:1 1 auto;display:flex;flex-direction:column;justify-content:center;padding:%s" % pad))
        load[c] += len(q[0]) + 120
    inner = "".join('<div style="flex:1;display:flex;flex-direction:column;gap:%dpx;min-width:0">%s</div>' % (gap, "".join(c)) for c in cols)
    return '<div style="position:absolute;%s;display:flex;gap:%dpx">%s</div>' % (box, gap, inner)


def wall(bk, cls, eyebrow, headline, names, n_quotes, layout):
    """A page of quotes in two columns, with photos beside them."""
    qs = [bk.pool.quote() for _ in range(n_quotes)]
    styles = ["qbox", "qwhite" if cls == "db" else "qdark", "qdark" if cls == "wh" else "qwhite"]
    cells = "".join('<div style="break-inside:avoid;margin-bottom:20px">%s</div>' % quote(q, qsize(q, 24, 18), styles[i % 3])
                    for i, q in enumerate(qs))
    if layout == "a":
        # One quote set large on the left over two photos, the rest in two columns on the right.
        first, rest = qs[0], qs[1:]
        cells = "".join('<div style="break-inside:avoid;margin-bottom:20px">%s</div>' % quote(q, qsize(q, 23, 19), styles[(i + 1) % 3])
                        for i, q in enumerate(rest))
        feature = ('<div class="qabs" style="left:120px;top:290px;width:760px">%s</div>'
                   % quote(first, qsize(first, 40, 30), "qbox", "padding:40px 44px"))
        pics = feature + collage(bk.pool, 120, 610, 760, 330, [[1, 1]], names)
        grid = stretch_cols(rest, 2, lambda i, q: styles[(i + 1) % 3], lambda q: qsize(q, 23, 19), "left:920px;right:120px;top:290px;bottom:130px")
    else:
        pics = collage(bk.pool, 1300, 96, 500, 844, [[1, 1], [("h", 1.3), 1], [1, 1]], names)
        grid = stretch_cols(qs, 2, lambda i, q: styles[i % 3], lambda q: qsize(q, 24, 19), "left:120px;width:1150px;top:290px;bottom:130px")
    inner = '<div style="position:absolute;left:120px;top:96px">%s</div>%s%s' % (head(eyebrow, headline, 66, 1150), pics, grid)
    bk.add(cls, inner)


def quote_page(bk, cls, eyebrow, headline, n_quotes):
    """A page that is all quotes, in three columns."""
    qs = [bk.pool.quote() for _ in range(n_quotes)]
    def style(i, q):
        if len(q[0]) < 120 and i % 3 == 0:
            return "qbox"
        return "qdark" if i % 2 else "qwhite"
    cells = "".join('<div style="break-inside:avoid;margin-bottom:18px">%s</div>' % quote(q, qsize(q, 23, 20), style(i, q), "padding:26px 30px")
                    for i, q in enumerate(qs))
    inner = ('<div style="position:absolute;left:120px;top:80px">%s</div>' % head(eyebrow, headline, 60, 1600)
             + (stretch_cols(qs, 4, style, lambda q: qsize(q, 20, 19), "left:120px;right:120px;top:230px;bottom:130px", 16, "20px 24px")
                if len(qs) > 11 else stretch_cols(qs, 3, style, lambda q: qsize(q, 23, 20), "left:120px;right:120px;top:250px;bottom:130px")))
    bk.add(cls, inner)


def photo_page(bk, cls, eyebrow, headline, names, n_quotes=0):
    """A page of photos; with no quotes the wall runs the full width of the page."""
    qs = [bk.pool.quote() for _ in range(n_quotes)]
    head_html = '<div style="position:absolute;left:120px;top:80px">%s</div>' % head(eyebrow, headline, 60, 1600)
    if not qs:
        bk.add(cls, head_html + collage(bk.pool, 120, 230, 1680, 720, [[2, 1, 1, 1], [1, 1, 2], [1, 2, 1, 1]], names))
        return
    side = "".join('<div style="margin-bottom:20px">%s</div>' % quote(q, qsize(q, 26, 21), ("qbox", "qwhite")[i % 2]) for i, q in enumerate(qs))
    inner = (head_html
             + collage(bk.pool, 120, 250, 1180, 700, [[2, 1, 1], [1, 1, 1], [1, 2]], names)
             + '<div style="position:absolute;left:1330px;right:120px;top:250px;bottom:130px;display:flex;flex-direction:column;justify-content:flex-start">%s</div>' % side)
    bk.add(cls, inner)


def cta(bk, line1, line2, button, qr_line, img, campaign, pos="center 35%"):
    """Closing page as a festival poster: a full photo fading into Dark Brown, one huge centred headline with its
    button, and a footer row with the edition mark, the contact lines and the QR code."""
    inner = (photo(img, pos)
             + '<div class="layer" style="background:linear-gradient(180deg,rgba(var(--ink),.1) 0%,rgba(var(--ink),.7) 42%,var(--db) 68%)"></div>'
             + '<div style="position:absolute;left:120px;right:120px;top:340px;text-align:center">'
               '<div class="mont" style="font-weight:900;font-size:150px;line-height:.98;text-transform:uppercase;letter-spacing:-.02em;color:var(--w)">'
               '%s<br><em style="color:var(--o)">%s</em></div>'
               '<div style="margin-top:44px"><span class="ctabtn" style="font-size:38px">%s</span></div></div>'
             % (t(line1), t(line2), t(button))
             + '<div style="position:absolute;left:120px;right:120px;bottom:70px;display:flex;align-items:center;justify-content:space-between;'
               'border-top:2px solid rgba(255,255,255,.2);padding-top:30px">'
             # The edition mark leads on its own; ClimbUK is never set beside it.
             + logo("Climb27", "reversed-dark", 56)
             + '<div class="mont" style="color:var(--w);font-weight:700;font-size:28px;line-height:1.5;text-align:center">%s<br>%s'
               '<div style="font-family:Open Sans;font-weight:600;font-size:19px;color:var(--tint);margin-top:6px">%s</div></div>'
             % (t(C["shared.contact"]), t(C["shared.url"]), t(C["shared.vat"]))
             + '<div style="display:flex;align-items:center;gap:20px"><div class="mont" style="color:var(--w);font-weight:800;font-size:22px;width:160px;text-align:right">%s</div>'
               '<div style="background:var(--w);padding:10px;border-radius:10px">%s</div></div></div>'
             % (t(qr_line), qr(QR_URL % campaign, 150)))
    bk.add("db", inner, foot=False)


# ---------------------------------------------------------------- exhibitor

EXHIBITOR_PHOTOS = (B + "expo_floor_*", P + "exhibitor_*", B + "expo_stand_*", B + "expo_stands_*", P + "climb_recap_04.jpg", B + "floor_joy.jpg",
                    B + "entrance_arrivals.jpg", P + "meetings_*", P + "joy_*", P + "crowds_*", P + "food_and_vendors_*", P + "media_*")


def stand_page(bk, cls, key, names, size_text, unit=None, render=None):
    """One stand: the words on the left at reading size, a large photo, a second photo or render, and a quote that fills its cell."""
    pool = bk.pool
    items = C["exhibitor.%s.includes" % key]
    many = len(items) > 5
    inc = "".join("<li>%s</li>" % t(i[0]) for i in items)
    price = '<div class="price" style="margin-top:30px">%s%s</div>' % (
        t(C["exhibitor.%s.price" % key]), ("<small>%s</small>" % t(unit)) if unit else "")
    strap_col = "#7A3B16" if cls == "gr" else "var(--deep)"
    text = ('<div style="position:absolute;left:120px;top:96px;width:740px">'
            '<span class="tag" style="font-size:20px;color:%s">%s</span>'
            '<div style="margin-top:26px">%s</div>'
            '<div class="mont" style="margin-top:28px;font-weight:800;font-size:34px;color:%s;line-height:1.2">%s</div>'
            '<p class="copy" style="margin-top:18px;font-size:24px;line-height:1.5">%s</p>'
            '<div class="mont" style="margin-top:28px;font-weight:800;font-size:22px;letter-spacing:.14em;text-transform:uppercase;color:var(--ch)">Includes</div>'
            '<ul class="list copy" style="margin-top:14px;font-size:24px;line-height:1.35;%s">%s</ul>%s</div>'
            % (strap_col, t(C["exhibitor.%s.eyebrow" % key]), labels([C["exhibitor.%s.name" % key]], 72, ital_last=False), strap_col,
               t(C["exhibitor.%s.strap" % key]), t(C["exhibitor.%s.body" % key]),
               "columns:2;column-gap:32px;font-size:22px" if many else "", inc, price))
    big = tile(pool.photo(*names), 940, 96, 860, 440)
    if render:
        low = ('<div class="tile" style="left:940px;top:560px;width:420px;height:384px;background:#fff">'
               '<div style="position:absolute;inset:18px;background:url(%s) center/contain no-repeat"></div></div>' % render)
    else:
        low = tile(pool.photo(*names), 940, 560, 420, 384)
    q = pool.quote()
    right = ('<div class="qabs" style="left:1384px;top:560px;width:416px;height:384px;display:flex">%s</div>'
             % quote(q, qsize(q, 28, 21), "qbox", "flex:1;display:flex;flex-direction:column;justify-content:center"))
    dims = t(re.sub(r"^[Ff]rom ", "", size_text)).replace(" x ", "x")
    if len(dims) > 6:  # a long size goes on two lines so it stays inside the circle
        dims = dims.replace("x", "<br>x ", 1)
    badge = '<div class="badge" style="left:850px;top:430px;font-size:%dpx"><small>%s</small>%s</div>' % (
        28 if "<br>" in dims else 32, "from" if size_text.lower().startswith("from") else "size", dims)
    bk.add(cls, text + big + low + right + badge)


def setup_page(bk, cls, key, after):
    """How simple it is: three steps on the left; setup day photos beside the finished stand on the right."""
    pool = bk.pool
    steps = "".join('<div class="step"><div class="numo" aria-hidden="true">%02d</div><h3>%s</h3><p>%s</p></div>' % (i, t(a), t(b))
                    for i, (a, b) in enumerate(C["%s.setup.steps" % key], 1))
    stick = lambda txt, x, y: '<div style="position:absolute;left:%dpx;top:%dpx;z-index:3"><span class="sticker" style="font-size:24px">%s</span></div>' % (x, y, t(txt))
    inner = ('<div style="position:absolute;left:120px;top:96px;width:820px">%s<p class="copy" style="margin-top:22px;font-size:25px">%s</p></div>'
             '<div class="steps2" style="position:absolute;left:120px;width:820px;top:470px;bottom:130px;display:flex;flex-direction:column;justify-content:space-between">%s</div>'
             % (head(C["%s.setup.eyebrow" % key], C["%s.setup.headline" % key], 68, 820), t(C["%s.setup.intro" % key]), steps)
             + tile(pool.photo(SETUP_PHOTOS[0]), 1000, 96, 520, 380) + tile(pool.photo(SETUP_PHOTOS[1]), 1538, 96, 262, 181)
             + tile(pool.photo(SETUP_PHOTOS[2]), 1538, 295, 262, 181) + tile(pool.photo(after), 1000, 512, 800, 432)
             + stick(C["exhibitor.setup.before"], 1020, 116) + stick(C["exhibitor.setup.after"], 1020, 532))
    bk.add(cls, inner)


def sizes_page(bk, cls):
    """Expo stand sizes side by side, two photos of each, so a reader sees what the room looks like."""
    pool = bk.pool
    cols = []
    for i, ((size, line), names) in enumerate(zip(C["exhibitor.sizes.items"], SIZE_PHOTOS)):
        x = 120 + i * 573
        cols.append('<div style="position:absolute;left:%dpx;top:330px;width:533px">'
                    '<div class="mont" style="font-weight:800;font-size:40px;color:var(--w);text-transform:uppercase">%s</div>'
                    '<div style="font-size:22px;color:var(--lg);margin-top:6px">%s</div></div>' % (x, t(size), t(line))
                    + tile(pool.photo(names[0]), x, 450, 533, 236) + tile(pool.photo(names[1]), x, 704, 533, 236))
    inner = ('<div style="position:absolute;left:120px;top:96px">%s<p class="copy" style="margin-top:20px;font-size:25px;max-width:1500px">%s</p></div>'
             % (head(C["exhibitor.sizes.eyebrow"], C["exhibitor.sizes.headline"], 68, 1600), t(C["exhibitor.sizes.intro"])) + "".join(cols))
    bk.add(cls, inner)


def exhibitor():
    bk = Brochure("climb27_exhibitor-brochure", "Exhibit at Climb27", "exhibitor.quotes")
    pool = bk.pool
    # Pod photos belong on the pod pages only; a second shot of the same pod is never shown.
    pool.reserved.update({B + "expo_floor_dsc03090.jpg"} | PICKS)
    pool.used.add(B + "expo_floor_maf-233.jpg")
    pool.used.update(STAND_TALKS | SET_ASIDE)
    # 1 Cover: an exhibitor team having fun on their stand, set in the right half so the words never cover a face.
    cover(bk, C["exhibitor.cover.line1"], C["exhibitor.cover.line2"], pool.photo(B + "expo_stand_girls-and-tech.jpg"), "center 45%", "", "fade-cover")
    # 2 What Climb27 is, beside a wall of exhibitor photos.
    what(bk, EXHIBITOR_PHOTOS)

    # 3 Why exhibit, on Charcoal: orange grounds carry big words only, never small text.
    reasons = "".join('<div class="row" style="margin-bottom:24px">%s<div><h3>%s</h3><p>%s</p></div></div>'
                      % (illo(r[0], size=66), t(r[1]), t(r[2])) for r in C["exhibitor.why.reasons"])
    q = pool.quote()
    # The hammer swing gets a tile close to its own shape, held to the top, so the hammer and both faces stay in.
    inner = (tile(pool.photo(B + "expo_stand_think-big.jpg"), 120, 96, 700, 400, "center top")
             + collage(pool, 120, 514, 700, 202, [[1, 1]], EXHIBITOR_PHOTOS)
             + '<div class="qabs" style="left:120px;top:740px;width:700px">%s</div>' % quote(q, qsize(q, 28, 20), "qbox")
             + '<div style="position:absolute;left:900px;top:90px;width:900px">%s<div style="margin-top:34px">%s</div></div>'
             % (head(C["exhibitor.why.eyebrow"], C["exhibitor.why.headline"], 72, 900), reasons))
    bk.add("ch", inner)

    # 4 Stand options, each with a real photo. The colour wheel stand is a starter pod, whatever its file name says.
    cards = []
    for key, names in (("pod", POD_PHOTOS[:1]), ("display", DISPLAY_PHOTOS[:1]),
                       ("expo", EXPO_PHOTOS[:1]), ("market", (P + "food_and_vendors_01.jpg",) + EXHIBITOR_PHOTOS)):
        unit = C.get("exhibitor.%s.unit" % key)
        # Every card has the same parts in the same order, and the unit line is always there, so the prices form one line.
        cards.append('<div class="cardx"><div class="img" style="height:200px">%s</div><div class="body"><div class="k">%s</div><h3>%s</h3>'
                     '<div class="d" style="font-weight:700;color:var(--ch)">%s</div><div class="d" style="margin-top:8px">%s</div>'
                     '<div class="end">%s<small>%s</small></div></div></div>'
                     % (photo(pool.photo(*(names + EXHIBITOR_PHOTOS))), t(C["exhibitor.%s.eyebrow" % key]), t(C["exhibitor.%s.name" % key]),
                        t(C["exhibitor.%s.size" % key]), t(C["exhibitor.%s.card" % key]), t(C["exhibitor.%s.price" % key]),
                        t(unit) if unit else "&nbsp;"))
    inner = ('<div style="position:absolute;left:120px;top:96px">%s<p class="copy" style="margin-top:20px;font-size:25px">%s</p></div>'
             '<div class="cards" style="left:120px;right:120px;top:380px;bottom:130px;grid-template-columns:repeat(4,1fr)">%s</div>'
             % (head(C["exhibitor.stands.eyebrow"], C["exhibitor.stands.headline"], 72, 1500), t(C["exhibitor.stands.intro"]), "".join(cards)))
    bk.add("gr", inner)

    # 5-7 One page per stand. The starter pod shows the standard pods; the custom-built pods show what an expo stand can become.
    stand_page(bk, "wh", "pod", POD_PHOTOS[1:] + EXHIBITOR_PHOTOS,
               C["exhibitor.pod.size"])
    stand_page(bk, "gr", "display", DISPLAY_PHOTOS[1:] + EXHIBITOR_PHOTOS,
               C["exhibitor.display.size"], render=B + "stand_display_render.jpg")
    stand_page(bk, "wh", "expo", EXPO_PHOTOS[1:] + EXHIBITOR_PHOTOS,
               C["exhibitor.expo.size"], unit=C["exhibitor.expo.unit"])
    # 8 Every expo size, 9 how simple the day is.
    sizes_page(bk, "ch")
    setup_page(bk, "wh", "exhibitor", B + "expo_floor_maf-415.jpg")

    # 8 The marketplace has its own page, on Light Grey.
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
             + collage(pool, 1060, 90, 740, 540, [[1, 1, 1], [1, 1], [1, 1]],
                       (B + "festival_busy_*", P + "food_and_vendors_*", P + "crowds_*", P + "joy_*", B + "expo_floor_busy.jpg",
                        B + "floor_joy.jpg", B + "entrance_arrivals.jpg", P + "climb_recap_*") + EXHIBITOR_PHOTOS)
             + '<div class="qabs" style="left:1060px;top:654px;width:740px">%s</div>' % quote(q, qsize(q, 26, 19), "qbox"))
    bk.add("gr", inner)

    # 9 Extras, with the print partner.
    items = "".join('<div class="icard" style="padding:24px 26px">%s<h3 style="font-size:26px">%s</h3><p style="font-size:21px">%s</p></div>'
                    % (illo(i[0], size=52), t(i[1]), t(i[2])) for i in C["exhibitor.extras.items"])
    pr = C["exhibitor.extras.print"][0]
    items += ('<div class="icard hi" style="padding:24px 26px">%s<h3 style="font-size:26px">%s</h3><p style="font-size:21px">%s</p></div>'
              % (illo("gift-box", color="var(--w)", size=52), t(pr[0]), t(pr[1])))
    q = pool.quote()
    inner = ('<div class="glow tl"></div><div style="position:absolute;left:120px;top:96px">%s<p class="copy" style="margin-top:20px;font-size:25px;max-width:1300px">%s</p></div>'
             '<div class="cards" style="left:120px;width:1100px;top:340px;bottom:140px;grid-template-columns:repeat(3,1fr)">%s</div>'
             % (head(C["exhibitor.extras.eyebrow"], C["exhibitor.extras.headline"], 72, 1500), t(C["exhibitor.extras.intro"]), items)
             + tile(pool.photo(B + "print_stand_instantprint.jpg", *EXHIBITOR_PHOTOS), 1250, 340, 550, 380)
             + '<div class="qabs" style="left:1250px;top:740px;width:550px;height:200px;display:flex">%s</div>'
             % quote(q, qsize(q, 24, 20), "qbox", "flex:1;display:flex;flex-direction:column;justify-content:center"))
    bk.add("ch", inner)

    # 10 A page of quotes, 11 a page of photos.
    quote_page(bk, "gr", C["shared.proof.eyebrow"], C["shared.proof.headline"], 13)
    photo_page(bk, "ch", C["exhibitor.proof2.eyebrow"], C["exhibitor.proof2.headline"],
               EXHIBITOR_PHOTOS + (P + "crowds_*", P + "joy_*"))

    # 14 Book a call, on a poster of the expo floor from above.
    cta(bk, C["exhibitor.cta.line1"], C["exhibitor.cta.line2"], C["exhibitor.cta.button"], C["exhibitor.cta.qr"],
        pool.photo(B + "expo_stands_overhead_02.jpg", B + "expo_hall_wide.jpg", *EXHIBITOR_PHOTOS), "exhibitor", "center 30%")
    return bk


# ---------------------------------------------------------------- partner

PARTNER_PHOTOS = (B + "expo_floor_*", B + "expo_stand_*", B + "entrance_arrivals.jpg", B + "floor_joy.jpg", P + "exhibitor_*",
                  P + "vip_and_awards_*", P + "stage_speakers_*", P + "audience_at_stage_*", P + "meetings_*", P + "joy_*",
                  P + "crowds_*", P + "roundtable_and_workshops_*", P + "climb_recap_*", P + "media_*")


# Page 5, in collage order, all from the latest edition: the kiosks, a whole zone and its welcome panel,
# the event app, the VIP suite and the partner cars outside.
# The branding upgrades page shows kiosks, lanyards and the app; the zone photos stay for the zones page.
OWN_PHOTOS = (B + "branding_maf-381.jpg", B + "kiosk_lanyards.jpg", B + "branding_dsc02963.jpg", B + "branding_maf-26.jpg")


def partner():
    bk = Brochure("climb27_partner-brochure", "Partner with Climb27", "partner.quotes")
    pool = bk.pool
    pool.used.update(STAND_TALKS | SET_ASIDE)
    pool.reserved.update(PICKS)
    cover(bk, C["partner.cover.line1"], C["partner.cover.line2"], pool.photo(P + "stage_speakers_02.jpg"), "center 35%")
    what(bk, PARTNER_PHOTOS, PARTNER_WHAT_PHOTOS)

    # 3 Why partner, on Light Grey beside a photo wall.
    cols = "".join('<div class="step" style="padding-top:190px"><div class="numo" aria-hidden="true" style="font-size:210px">%02d</div><h3>%s</h3><p>%s</p></div>'
                   % (n, t(p[0]), t(p[1])) for n, p in enumerate(C["partner.why.points"], 1))
    q = pool.quote()
    inner = ('<div style="position:absolute;left:120px;top:96px">%s</div>' % head(C["partner.why.eyebrow"], C["partner.why.headline"], 78, 1100)
             + '<div style="position:absolute;left:120px;width:1080px;top:420px;display:grid;grid-template-columns:repeat(3,1fr);gap:46px" class="stepsbig">%s</div>' % cols
             + collage(pool, 1260, 96, 540, 640, [[1], [1, 1]], PARTNER_PHOTOS)
             + '<div class="qabs" style="left:1260px;top:760px;width:540px;height:180px;display:flex">%s</div>'
             % quote(q, qsize(q, 26, 20), "qbox", "flex:1;display:flex;flex-direction:column;justify-content:center"))
    bk.add("gr", inner)

    # 4 How it works, on Charcoal: steps 01 to 03 down the left; 04, the quote and two photos on the right.
    steps = ['<div class="step"><div class="numo" aria-hidden="true">%02d</div><h3>%s</h3><p>%s</p></div>'
             % (n, t(s_[0]), t(s_[1])) for n, s_ in enumerate(C["partner.how.steps"], 1)]
    q = pool.quote()
    inner = ('<div style="position:absolute;left:120px;top:96px">%s</div>'
             '<div class="steps2" style="position:absolute;left:120px;width:880px;top:270px;bottom:130px;display:flex;flex-direction:column;justify-content:space-between">%s</div>'
             % (head(C["partner.how.eyebrow"], C["partner.how.headline"], 76, 1680), "".join(steps[:3]))
             # Each photo at its own shape, so the zone sign and the logo wall show whole.
             + tile(pool.photo(B + "branding_052a3123.jpg"), 1060, 620, 220, 330)
             + tile(pool.photo(B + "branding_052a3128.jpg"), 1300, 620, 500, 330)
             + '<div class="steps2" style="position:absolute;left:1060px;width:740px;top:270px">%s</div>' % steps[3]
             + '<div class="qabs" style="left:1060px;top:410px;width:740px;height:180px;display:flex">%s</div>'
             % quote(q, qsize(q, 22, 19), "qbox", "flex:1;display:flex;flex-direction:column;justify-content:center"))
    bk.add("ch", inner)

    # 5 What comes with every partnership, on Light Grey.
    # Each card wears its icon as a pin: a tilted Dark Brown badge over the top edge, the words centred below.
    items = "".join('<div class="pcard"><div class="pin" style="transform:translateX(-50%%) rotate(%ddeg)">%s</div><h3>%s</h3><p>%s</p></div>'
                    % ((-6, 5, -3, 4, -5, 6, -4, 3, -6)[n], illo(i[0], color="var(--w)", size=58), t(i[1]), t(i[2]))
                    for n, i in enumerate(C["partner.included.items"]))
    inner = ('<div style="position:absolute;left:120px;top:96px">%s</div>' % head(C["partner.included.eyebrow"], C["partner.included.headline"], 64, 1680)
             + '<div class="cards" style="left:120px;right:120px;top:280px;bottom:150px;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(3,1fr);gap:62px 40px">%s</div>' % items)
    bk.add("gr", inner)

    # What a partner can own, three by two. What every partnership includes has its own page.
    items = "".join('<div class="icard">%s<h3>%s</h3><p>%s</p></div>' % (illo(i[0], size=68), t(i[1]), t(i[2])) for i in C["partner.own.items"])
    inner = ('<div style="position:absolute;left:120px;top:96px">%s</div>' % head(C["partner.own.eyebrow"], C["partner.own.headline"], 64, 1140)
             + '<div class="cards" style="left:120px;width:1120px;top:250px;bottom:130px;grid-template-columns:repeat(3,1fr)">%s</div>' % items
             + collage(pool, 1280, 96, 520, 844, [[("h", 1.1), 1], [("h", .9), 1, 1], [("h", 1.1), 1]], OWN_PHOTOS + PARTNER_PHOTOS))
    bk.add("wh", inner)

    # The event app, on Light Grey: what a partner can add, beside two photos of the app in use.
    rows = "".join('<div class="row" style="align-items:flex-start;gap:20px">%s<div><h3 style="font-size:24px">%s</h3><p style="font-size:19px">%s</p></div></div>'
                   % (illo(i[0], size=52), t(i[1]), t(i[2])) for i in C["partner.app.items"])
    inner = ('<div style="position:absolute;left:120px;top:96px;width:1160px">%s'
             '<p class="copy" style="margin-top:20px;font-size:23px">%s</p></div>'
             % (head(C["partner.app.eyebrow"], C["partner.app.headline"], 64, 1160), t(C["partner.app.intro"]))
             + '<div style="position:absolute;left:120px;width:1160px;top:440px;bottom:130px;display:grid;grid-template-columns:1fr 1fr;gap:16px 40px;align-content:space-between">%s</div>' % rows
             + collage(pool, 1340, 96, 460, 844, [[1], [1]], (B + "branding_maf-402.jpg", B + "festival_busy_maf-452.jpg") + PARTNER_PHOTOS))
    bk.add("gr", inner)

    # Session screens and the ticket, on white: run by us in every session room, beside stage photos.
    rows = "".join('<div class="row" style="align-items:flex-start;gap:24px">%s<div><h3 style="font-size:30px">%s</h3><p style="font-size:24px;margin-top:6px">%s</p></div></div>'
                   % (illo(i[0], color="#C55308", size=80), t(i[1]), t(i[2])) for i in C["partner.sessions.items"])
    inner = ('<div style="position:absolute;left:120px;top:96px;width:1160px">%s'
             '<p class="copy" style="margin-top:20px;font-size:26px">%s</p></div>'
             % (head(C["partner.sessions.eyebrow"], C["partner.sessions.headline"], 64, 1160), t(C["partner.sessions.intro"]))
             + '<div style="position:absolute;left:120px;width:1160px;top:340px;bottom:140px;display:grid;grid-template-columns:1fr 1fr;gap:30px 48px;align-content:space-between">%s</div>' % rows
             + collage(pool, 1340, 96, 460, 844, [[1], [1]], (B + "band_052a4629.jpg", B + "stage_dsc06150.jpg", B + "stage_maf-278.jpg", B + "stage_*") + PARTNER_PHOTOS))
    bk.add("wh", inner)

    # Headline Partner, on Charcoal: the extras down the left, a stage photo and a quote on the right.
    rows = "".join('<div class="row" style="margin-top:44px;align-items:center">%s<div><h3>%s</h3><p style="font-size:23px">%s</p></div></div>'
                   % (illo(i[0], size=72), t(i[1]), t(i[2])) for i in C["partner.headline.items"])
    q = pool.quote()
    inner = ('<div style="position:absolute;left:120px;top:96px;width:900px">%s'
             '<p class="copy" style="margin-top:24px;font-size:25px">%s</p>%s</div>'
             % (head(C["partner.headline.eyebrow"], C["partner.headline.headline"], 70, 900), t(C["partner.headline.intro"]), rows)
             + tile(pool.photo(B + "festival_busy_maf-75.jpg", B + "stage_*", *PARTNER_PHOTOS), 1080, 96, 720, 520)
             + '<div class="qabs" style="left:1080px;top:640px;width:720px;height:300px;display:flex">%s</div>'
             % quote(q, qsize(q, 28, 22), "qbox", "flex:1;display:flex;flex-direction:column;justify-content:center"))
    bk.add("ch", inner)

    # NatWest, the multi-year partner, on Light Grey.
    q1 = pool.take("NatWest")
    q2 = pool.quote()
    inner = ('<div style="position:absolute;left:120px;top:96px;width:820px">%s'
             '<p class="copy" style="margin-top:28px;font-size:27px">%s</p>'
             '<div style="margin-top:40px">%s</div><div style="margin-top:20px">%s</div></div>'
             % (head(C["partner.natwest.eyebrow"], C["partner.natwest.headline"], 70, 820), t(C["partner.natwest.body"]),
                quote(q1, qsize(q1, 30, 24), "qbox"), quote(q2, qsize(q2, 26, 22), "qwhite"))
             + tile(pool.photo(B + "expo_stand_natwest.jpg", B + "expo_stand_natwest_02.jpg"), 1000, 96, 800, 533)
             # A QR code to the announcement video, on a Dark Brown card beside the photos.
             + '<div style="position:absolute;left:1000px;top:653px;width:800px;height:287px;background:var(--db);border-radius:12px;'
               'display:flex;align-items:center;gap:36px;padding:0 40px">'
               '<div style="border-radius:10px;overflow:hidden;flex:none">%s</div><div>'
               '<p class="mont" style="font-weight:800;font-size:34px;line-height:1.1;text-transform:uppercase;color:var(--w)">%s</p>'
               '<p style="font-size:22px;margin-top:12px;color:var(--lg)">%s</p></div></div>'
             % (qr(C["partner.natwest.video.url"], 170), t(C["partner.natwest.video.title"]), t(C["partner.natwest.video.line"])))
    bk.add("gr", inner)

    # 7 Zones, on Charcoal: the zones in words on the left, Climb26's branded zones on the right.
    zones = "".join('<div class="icard" style="padding:28px 30px"><h3>%s</h3><p>%s</p></div>' % (t(z[0]), t(z[1]))
                    for z in C["partner.zones.items"])
    zp = [pool.photo(n) for n in ZONE_PHOTOS]
    inner = ('<div class="glow tl"></div><div style="position:absolute;left:120px;top:96px;width:880px">%s<p class="copy" style="margin-top:20px;font-size:24px">%s</p></div>'
             '<div class="cards" style="left:120px;width:880px;top:400px;bottom:130px;grid-template-columns:1fr 1fr">%s</div>'
             % (head(C["partner.zones.eyebrow"], C["partner.zones.headline"], 76, 880), t(C["partner.zones.intro"]), zones)
             # The portrait zone sign gets a portrait tile.
             + tile(zp[0], 1060, 96, 313, 470) + tile(zp[1], 1391, 96, 409, 226) + tile(zp[2], 1391, 340, 409, 226)
             + tile(zp[3], 1060, 584, 361, 360) + tile(zp[4], 1439, 584, 361, 170) + tile(zp[5], 1439, 772, 361, 172))
    bk.add("ch", inner)
    # 8 How simple the day is, on white.
    setup_page(bk, "wh", "partner", B + "branding_maf-382.jpg")

    # 9 Sessions and awards, on Light Grey.
    stage_names = [(P + "roundtable_and_workshops_02.jpg",), (P + "climb_awards_winners.jpg",), (P + "stage_speakers_03.jpg",)]
    offers = "".join('<div class="cardx"><div class="img" style="height:390px">%s</div><div class="body"><h3>%s</h3>'
                     '<div class="d">%s</div><div class="end">%s</div></div></div>'
                     % (photo(pool.photo(*(n + PARTNER_PHOTOS))), t(o[1]), t(o[2]), t(o[3]))
                     for n, o in zip(stage_names, C["partner.stage.items"]))
    inner = ('<div style="position:absolute;left:120px;top:96px">%s</div>'
             '<div class="cards" style="left:120px;right:120px;top:300px;bottom:130px;grid-template-columns:repeat(3,1fr)">%s</div>'
             % (head(C["partner.stage.eyebrow"], C["partner.stage.headline"], 70, 1680), offers))
    bk.add("gr", inner)

    # 9 Add more, on white.
    # The same pin cards as the included page.
    items = "".join('<div class="pcard"><div class="pin" style="transform:translateX(-50%%) rotate(%ddeg)">%s</div><h3>%s</h3><p>%s</p></div>'
                    % ((5, -4, 6, -6, 3, -5)[n], illo(i[0], color="var(--w)", size=58), t(i[1]), t(i[2]))
                    for n, i in enumerate(C["partner.more.items"]))
    q = pool.quote()
    inner = ('<div style="position:absolute;left:120px;top:96px">%s</div>' % head(C["partner.more.eyebrow"], C["partner.more.headline"], 76, 1100)
             + '<div class="cards" style="left:120px;width:1120px;top:380px;bottom:140px;grid-template-columns:repeat(3,1fr);grid-template-rows:1fr 1fr;gap:72px 28px">%s</div>' % items
             + tile(pool.photo(*PARTNER_PHOTOS), 1280, 96, 520, 500)
             + '<div class="qabs" style="left:1280px;top:620px;width:520px;height:320px;display:flex">%s</div>'
             % quote(q, qsize(q, 26, 20), "qbox", "flex:1;display:flex;flex-direction:column;justify-content:center"))
    bk.add("wh", inner)

    # 10-11 In their words.
    quote_page(bk, "gr", C["shared.proof.eyebrow"], C["shared.proof.headline"], 13)
    photo_page(bk, "ch", C["partner.proof2.eyebrow"], C["partner.proof2.headline"],
               # One photo of each kind of moment, and only one from the awards.
               (B + "stage_maf-665.jpg", B + "food_052a2866.jpg", B + "outdoor_dsc06298.jpg", P + "stage_speakers_01.jpg",
                B + "awards_052a4029.jpg", P + "joy_*", B + "festival_busy_maf-479.jpg", P + "crowds_*", B + "festival_busy_maf-30.jpg",
                P + "audience_at_stage_01.jpg", B + "stage_maf-278.jpg", B + "festival_busy_*", P + "crowds_*") + PARTNER_PHOTOS)

    cta(bk, C["partner.cta.line1"], C["partner.cta.line2"], C["partner.cta.button"], C["partner.cta.qr"],
        pool.photo(B + "stage_020726049climb26.jpg", P + "climb_crowd_wide.jpg", *PARTNER_PHOTOS), "partner", "center 20%")
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
