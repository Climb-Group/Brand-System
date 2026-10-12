"""Build the live component previews for the ClimbUK brand hub.

    python3 components/build_components.py [--bootstrap DIR]

Reads the website blocks (climb_website_brand/views/snippets/climb_snippets.xml) and their styles
(climb_website_brand/static/src/scss/climb_brand.scss) and writes, under components/hub/:

    bundle.css                     every component style, coloured from the brand tokens (var(--climb-orange) ...)
    bundle.js                      window.ClimbUK: the theme switch, the marquee, and every component's markup
    index.d.ts                     the bundle's API, as documentation
    <Component>/preview.html       one live component in a few states, theme aware (folder = JS identifier)
    <Component>/README.md          when and how to use it

The previews use neutral class names (climb-p1 .. climb-p5 for the five presets, climb-fade for a photo fade,
climb-photo-bg for a photo ground), so the same markup works on any site that loads bundle.css and the token CSS.
Sections marked data-climb-theme follow the light and dark theme: "ground" is preset 3 on dark and preset 1 on
light, "alt" is preset 5 on dark and preset 2 on light. Photo sections, orange bands and the close stay as they are.

Needs: sass and bootstrap 5.3.3 (npm i sass bootstrap@5.3.3), and blobs.json (photo and logo file -> hub URL).
"""
import argparse
import copy
import json
import pathlib
import re
import subprocess
import sys

from bs4 import BeautifulSoup

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
# The website blocks live in the website repository; point --module at its climb_website_brand folder.
MODULE = REPO.parent / "climb-group-odoo" / "climb_website_brand"
OUT = HERE / "hub"
BLOBS = json.loads((HERE / "blobs.json").read_text())
GLYPHS = REPO / "generators" / "social-icons" / "glyphs"

# Exact token colours: compiled hex -> token var. Order matters only for readability.
HEX_TOKENS = {
    "#e8712a": "climb-orange", "#c55308": "orange-text", "#b04902": "orange-text-on-grey",
    "#d5641e": "orange-large-on-grey", "#f2ae86": "orange-tint", "#a94b12": "link-on-white",
    "#843a0e": "link-on-grey", "#1e0f05": "dark-brown", "#242322": "charcoal", "#e9e9e9": "light-grey",
    "#4d5b7c": "body-slate",
}

THEME_JS = (
    "var r=document.documentElement,m={ground:['climb-p3','climb-p1'],alt:['climb-p5','climb-p2'],sig:['climb-p5','climb-p1']};"
    "function theme(root){root=root||document;var l=r.getAttribute('data-theme')==='light';"
    "root.querySelectorAll('[data-climb-theme]').forEach(function(e){var p=m[e.getAttribute('data-climb-theme')];"
    "if(!p)return;e.classList.remove(p[0],p[1]);e.classList.add(p[l?1:0]);});}"
    "function marquee(root){(root||document).querySelectorAll('.climb-marquee-row').forEach(function(w){if(w.classList.contains('is-live'))return;"
    "var t=w.querySelector('.climb-marquee-track');if(!t)return;var c=t.cloneNode(true);c.setAttribute('aria-hidden','true');"
    "w.appendChild(c);w.classList.add('is-live');});}"
    "var watching=false;function mount(root){theme(root);marquee(root);if(!watching){watching=true;"
    "new MutationObserver(function(){theme(document);}).observe(r,{attributes:true,attributeFilter:['data-theme']});}}"
)

PREVIEW_JS = "window.ClimbUK&&ClimbUK.mount(document);"


def ident(name):
    """Component folder and export name: "Hero with ticket" -> HeroWithTicket."""
    return "".join(w[:1].upper() + w[1:] for w in re.split(r"[^A-Za-z0-9]+", name) if w)


def bundle_js(comps):
    """One classic script assigning window.ClimbUK. Each component is a function that returns its markup as an
    element (props: {theme: "dark"|"light"}), plus .html for the raw markup; mount() applies the theme switch."""
    header = {"format": 4, "namespace": "ClimbUK", "components": [{"name": ident(c["name"])} for c in comps]}
    parts = ["/* @ds-bundle: %s */" % json.dumps(header, separators=(",", ":")),
             "(function(){", THEME_JS,
             "function make(html,meta){var f=function(props){var d=document.createElement('div');d.innerHTML=html;"
             "var el=d.firstElementChild;if(props&&props.theme){el.querySelectorAll('[data-climb-theme]').forEach(function(e){"
             "var p=m[e.getAttribute('data-climb-theme')];if(p){e.classList.remove(p[0],p[1]);e.classList.add(p[props.theme==='light'?1:0]);}});}"
             "else{theme(el);}marquee(el);return el;};f.html=html;f.group=meta[0];f.summary=meta[1];f.title=meta[2];return f;}",
             "var C={};"]
    for c in comps:
        body = c["body"].strip()
        assert "</script" not in body.lower() and "<!--" not in body, c["name"]
        parts.append("C[%s]=make(%s,%s);" % (json.dumps(ident(c["name"])), json.dumps(body),
                                             json.dumps([c["group"], c["subtitle"], c["name"]])))
    parts.append("var api={version:'1.0.0',presets:m,applyTheme:theme,startMarquees:marquee,mount:mount};"
                 "for(var k in C)api[k]=C[k];window.ClimbUK=api;})();")
    return "\n".join(parts) + "\n"


def index_dts(comps):
    lines = ["/** ClimbUK components: plain HTML and CSS, no framework. Load tokens.css and bundle.css, then bundle.js. */",
             "export interface ClimbComponentProps {", "  /** Force a theme; default follows <html data-theme>. */",
             "  theme?: 'dark' | 'light';", "}",
             "export interface ClimbComponent {", "  (props?: ClimbComponentProps): HTMLElement;",
             "  /** The component's markup. */", "  html: string;", "  group: string;", "  summary: string;", "  title: string;", "}"]
    for c in comps:
        lines.append("/** %s */\nexport type %sProps = ClimbComponentProps;" % (c["subtitle"], ident(c["name"])))
    lines += ["export interface ClimbUK {",
              "  /** Swap preset classes on [data-climb-theme] elements to match <html data-theme>. */",
              "  applyTheme(root?: ParentNode): void;", "  /** Duplicate each logo marquee track so it loops. */",
              "  startMarquees(root?: ParentNode): void;", "  /** applyTheme + startMarquees, and follow later theme changes. */",
              "  mount(root?: ParentNode): void;"]
    lines += ["  %s: ClimbComponent;" % ident(c["name"]) for c in comps]
    lines += ["}", "declare global { interface Window { ClimbUK: ClimbUK } }", ""]
    return "\n".join(lines)


STUB = """
@import "%(bs)s/functions";
@import "%(bs)s/variables";
@import "%(bs)s/variables-dark";
@import "%(bs)s/maps";
@import "%(bs)s/mixins";
@import "%(bs)s/utilities";
@import "%(bs)s/root";
@import "%(bs)s/reboot";
@import "%(bs)s/type";
@import "%(bs)s/images";
@import "%(bs)s/containers";
@import "%(bs)s/grid";
@import "%(bs)s/buttons";
@import "%(bs)s/helpers";
@import "%(bs)s/utilities/api";
@import "%(tokens)s";
body{background:transparent;color:var(--text);font-family:var(--font-body);margin:0}
h1,h2,h3,h4{font-family:var(--font-display);font-weight:700}
h2{font-size:clamp(2rem,2vw + 1rem,2.5rem)}
@each $i, $bg, $tx, $hd, $ln, $bf, $bt in
  (1,var(--white),var(--body-slate),var(--charcoal),var(--link-on-white),var(--climb-orange),var(--white)),
  (2,var(--light-grey),var(--body-slate),var(--charcoal),var(--link-on-grey),var(--climb-orange),var(--white)),
  (3,var(--dark-brown),var(--white),var(--white),var(--orange-tint),var(--climb-orange),var(--white)),
  (4,var(--climb-orange),var(--white),var(--white),var(--white),var(--white),var(--charcoal)),
  (5,var(--charcoal),var(--light-grey),var(--white),var(--orange-tint),var(--climb-orange),var(--white)) {
  .o_cc#{$i}{background-color:$bg;color:$tx;
    h1,h2,h3,h4{color:$hd} a:not(.btn){color:$ln}
    .btn-primary{--bs-btn-bg:#{$bf};--bs-btn-border-color:#{$bf};--bs-btn-color:#{$bt};--bs-btn-hover-bg:#{$bf};--bs-btn-hover-border-color:#{$bf};--bs-btn-hover-color:#{$bt};--bs-btn-active-bg:#{$bf};--bs-btn-active-color:#{$bt}}
    .btn-outline-secondary{--bs-btn-color:#{$hd};--bs-btn-border-color:#{$hd};--bs-btn-hover-color:#{$hd};--bs-btn-hover-bg:transparent;--bs-btn-hover-border-color:#{$hd};--bs-btn-disabled-color:#{$hd};--bs-btn-disabled-border-color:#{$hd}}}
}
section{position:relative;overflow:hidden}
.oe_img_bg{background-size:cover;background-repeat:no-repeat}
.o_we_bg_filter{position:absolute;inset:0}
section>.container{position:relative;z-index:1}
.o_we_shape{position:absolute;inset:0;background-repeat:no-repeat;pointer-events:none}
@each $n in 0,8,16,24,32,40,48,64,80,96,112,128 { .pt#{$n}{padding-top:#{$n}px} .pb#{$n}{padding-bottom:#{$n}px} }
@import "%(scss)s";
@import "%(a11y)s";
"""

# Class renames: builder-specific names in the website module -> neutral names in the hub bundle.
RENAMES = [
    (r"o_climb_website_brand_Climb_0(\d)", r"climb-shape-0\1"),
    (r"o_we_bg_filter", "climb-fade"),
    (r"oe_img_bg", "climb-photo-bg"),
    (r"o_bg_img_center", "climb-photo-center"),
    (r"o_we_shape", "climb-shape"),
    (r"o_cc(\d)", r"climb-p\1"),
    (r",?\.o_wblog_post_content|,?\.o_mail_body_mailing", ""),
]


def neutral(text):
    for a, b in RENAMES:
        text = re.sub(a, b, text)
    return text


def build_css(bootstrap):
    stub = STUB % {"bs": bootstrap, "tokens": MODULE / "static/src/scss/_climb_tokens.scss",
                   "scss": MODULE / "static/src/scss/climb_brand.scss",
                   "a11y": MODULE / "static/src/scss/climb_a11y.scss"}
    tmp = OUT / "_stub.scss"
    tmp.write_text(stub)
    css = subprocess.run(["npx", "--no-install", "sass", "--no-source-map", "--quiet-deps", "--style=compressed",
                          "--load-path", str(pathlib.Path(bootstrap).parents[1]), str(tmp)],
                         capture_output=True, text=True, cwd=str(pathlib.Path(bootstrap).parents[2]))
    tmp.unlink()
    if css.returncode:
        sys.exit(css.stderr)
    css = css.stdout
    css = re.sub(r"@charset \"UTF-8\";", "", css).lstrip("\ufeff")
    css = re.sub(r"\.o_cc(?=[\s,{:.>])(?!\d)", ".climb-preset", css)

    def tok(m):
        h = m.group(0).lower()
        if len(h) == 4:
            h = "#" + "".join(c * 2 for c in h[1:])
        return "var(--%s)" % HEX_TOKENS[h] if h in HEX_TOKENS else m.group(0)
    css = re.sub(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b", tok, css)
    css = neutral(css) + "\n" + shape_css()
    css = css.replace("</style", "")
    header = ("/* ClimbUK components. Load after the token CSS. Presets: .climb-p1 White, .climb-p2 Light Grey, "
              ".climb-p3 Dark Brown, .climb-p4 Climb Orange, .climb-p5 Charcoal. */\n")
    return header + css


SHAPE_POS = {1: "right bottom;background-size:cover", 2: "center top;background-size:cover",
             3: "right center;background-size:cover", 4: "right bottom;background-size:auto 60%",
             5: "right bottom;background-size:100% auto"}


def shape_css():
    """The five Climb section shapes as background images, coloured Climb Orange."""
    import base64
    rules = []
    for svg in sorted((MODULE / "static/shapes/Climb").glob("0*.svg")):
        n = int(svg.stem)
        data = re.sub(r"#[0-9A-Fa-f]{6}", "#E8712A", svg.read_text())
        rules.append(".climb-shape-%02d{background-image:url('data:image/svg+xml;base64,%s');background-position:%s}"
                     % (n, base64.b64encode(data.encode()).decode(), SHAPE_POS.get(n, "center")))
    return "\n".join(rules)


def blob(path):
    name = path.rsplit("/", 1)[-1]
    name = re.sub(r"^climb_", "climb26_", name)
    return BLOBS["photos"].get(name, path)


def partner_tile(i):
    names = ["Partner", "Your logo", "Exhibitor", "Partner", "Backer", "Your logo"]
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 80"><rect x="1" y="1" width="238" height="78" rx="12" '
           'fill="none" stroke="#8a8a8a" stroke-width="2" stroke-dasharray="6 6"/><text x="120" y="50" text-anchor="middle" '
           'font-family="Montserrat,Arial,sans-serif" font-weight="700" font-size="24" fill="#8a8a8a">%s</text></svg>'
           % names[i % len(names)])
    import base64
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def load_sections():
    xml = (MODULE / "views/snippets/climb_snippets.xml").read_text()
    out = {}
    for tid, sec in re.findall(r'<template id="(\w+)"[^>]*>\s*(<section.*?</section>)', xml, re.S):
        sec = re.sub(r"<(div|p|span|i)([^>]*)/>", r"<\1\2></\1>", sec)
        out[tid] = clean(sec)
    return out


def clean(html):
    soup = BeautifulSoup(html, "html.parser")
    li = [0]
    for el in soup.find_all(True):
        cls = el.get("class") or []
        cls = [c for c in cls if c not in ("o_animate", "o_anim_fade_in", "o_anim_from_bottom", "o_anim_from_right",
                                           "o_anim_from_left", "o_translate_inline", "climb-rise", "o_cc")]
        if cls:
            el["class"] = cls
        elif el.has_attr("class"):
            del el["class"]
        for a in ("loading", "data-oe-shape-data"):
            if el.has_attr(a):
                del el[a]
        if el.name == "a" and el.has_attr("href"):
            el["href"] = "#"
        if el.name == "img" and el.has_attr("src"):
            if "/web/image/" in el["src"]:
                el["src"] = partner_tile(li[0])
                li[0] += 1
            else:
                el["src"] = blob(el["src"])
        if el.has_attr("style") and "animation-delay" in el["style"]:
            st = re.sub(r"animation-delay:\s*\d+ms;?\s*", "", el["style"]).strip()
            if st:
                el["style"] = st
            else:
                del el["style"]
        if el.has_attr("style") and "url(" in el["style"]:
            el["style"] = re.sub(r"url\('([^']+)'\)", lambda m: "url('%s')" % blob(m.group(1)), el["style"])
    sec = soup.find("section")
    cls = sec.get("class", [])
    if "oe_img_bg" not in cls:
        if "o_cc1" in cls or "o_cc3" in cls:
            sec["data-climb-theme"] = "ground"
        elif "o_cc2" in cls or "o_cc5" in cls:
            sec["data-climb-theme"] = "alt"
    return neutral(str(soup))


THEMED = {}


def wrap_ground(inner, theme="ground", pad="pt48 pb48", extra=""):
    preset = "climb-p3" if theme == "ground" else "climb-p5"
    return ('<section class="s_climb_kit %s %s %s" data-climb-theme="%s"><div class="container">%s</div></section>'
            % (preset, pad, extra, theme, inner))


def pick(section_html, selector, n=None):
    soup = BeautifulSoup(section_html, "html.parser")
    els = soup.select(selector)
    return "".join(str(e) for e in (els[:n] if n else els))


def glyph(name):
    svg = (GLYPHS / ("%s.svg" % name)).read_text()
    svg = re.sub(r"<title>.*?</title>", "", svg)
    return svg.replace("<svg ", '<svg fill="currentColor" aria-hidden="true" ')


def components(S):
    """(name, group, subtitle, height, body, readme). Body is the root element (sections or a frame)."""
    C = []

    def add(name, group, subtitle, height, body, readme, width=1280):
        C.append(dict(name=name, group=group, subtitle=subtitle, height=height, body=body, readme=readme, width=width))

    # ---------------------------------------------------------------- Foundations
    presets = "".join(
        '<section class="s_climb_kit climb-p%d pt40 pb40"%s><div class="container"><p class="climb-eyebrow">Preset %d %s</p>'
        '<h3 class="climb-statement climb-statement-sm">Find your <span class="climb-accent"><em>people</em></span></h3>'
        '<p>%s <a href="#">A link in running text</a>.</p><p class="climb-ctas"><a href="#" class="btn btn-primary">Get your ticket</a>'
        '<a href="#" class="btn btn-outline-secondary">Partner with ClimbUK</a></p></div></section>'
        % (i, THEMED.get(i, ""), i, n, t) for i, n, t in [
            (1, "White", "Reading-heavy pages, forms and the release ladder."),
            (2, "Light Grey", "A quiet change of pace between dark sections."),
            (3, "Dark Brown", "The default ground. Dark first."),
            (4, "Climb Orange", "Calls to action and the close. White text is large only."),
            (5, "Charcoal", "Ticket and audience sections, the second dark ground.")])
    add("Presets", "Foundations", "The five grounds, each with its own text, link and button colours", 900,
        '<div>%s</div>' % presets,
        "The five presets are the only grounds a ClimbUK section uses. Each one sets the heading, body, link, accent and "
        "button colours together, so a section never mixes them by hand.\n\n"
        "| Preset | Ground | Use |\n| --- | --- | --- |\n| 1 | White | Reading-heavy pages, forms, the release ladder |\n"
        "| 2 | Light Grey | A quiet change of pace between dark sections |\n| 3 | Dark Brown | The default ground |\n"
        "| 4 | Climb Orange | Calls to action and the close, large white text only |\n| 5 | Charcoal | Tickets and audience sections |\n\n"
        "Add the class `climb-p1` to `climb-p5` to a section. In this hub, sections on presets 1, 2, 3 and 5 follow the theme "
        "toggle; preset 4 and photo sections stay as they are in both themes.")

    add("Headline", "Foundations", "Uppercase display lines with one orange word and one italic word", 520,
        wrap_ground(
            '<p class="climb-eyebrow">Climb27 / The Festival for Business Growth</p>'
            '<h1 class="climb-display">Your business. Bigger <span class="climb-accent"><em>stage</em></span>.</h1>'
            '<h2 class="climb-statement climb-ruled">Not a <em>conference</em>. A <span class="climb-accent">festival</span> for business growth.</h2>'
            '<h3 class="climb-statement climb-statement-sm">ClimbAwards: be the name behind the <em>moment</em></h3>'
            '<p class="lead climb-lead">Lead text: one or two sentences that say what happens, for whom, and what to do next.</p>'),
        "Headlines are the poster voice: uppercase, tight, and short enough to read in one look.\n\n"
        "- `climb-display` for the one hero line on a page; `climb-statement` for section lines; add `climb-statement-sm` for a "
        "smaller one beside a photo.\n- Give one word `climb-accent` (orange) and one word `<em>` (italic). Never more than one of each.\n"
        "- `climb-ruled` adds the short orange rule above the line.\n- `climb-eyebrow` sits above a headline: edition, date or audience.\n"
        "- `climb-lead` is the promise line under it, at most 36 words.")

    btns = "".join(
        '<section class="s_climb_kit climb-p%d pt32 pb32"><div class="container"><p class="climb-ctas">'
        '<a href="#" class="btn btn-primary btn-lg">Get your ticket</a><a href="#" class="btn btn-outline-secondary btn-lg">Partner with ClimbUK</a>'
        '<a href="#" class="btn btn-primary">Book a call</a><span class="btn btn-outline-secondary disabled" aria-disabled="true">Sold out</span>'
        '</p><p class="climb-pull"><a href="#">Not sure which Climb27 is yours? Pick your route</a></p></div></section>' % i
        for i in (3, 1, 4, 5))
    add("Button", "Actions", "Pill buttons with a spring hover, one primary per view, and the pull link", 560,
        '<div>%s</div>' % btns,
        "Buttons are pills in Montserrat Bold with an action verb: Get your ticket, Book a call, Apply to speak.\n\n"
        "- One `btn btn-primary` per view. A second action is `btn btn-outline-secondary`.\n"
        "- `btn-lg` in heroes and closes, the default size elsewhere.\n- A closed offer shows a disabled outline button that says Sold out, "
        "only when it is true.\n- The pull link (`climb-pull`) is the soft third action under the buttons: a question that routes people.\n"
        "- On Climb Orange (preset 4) the primary button turns White with Charcoal text.\n- Hover lifts with the spring easing; "
        "focus shows a 3px orange outline. Both stop under reduced motion.")

    add("Eyebrow", "Foundations", "Small uppercase labels and the orange rule", 300,
        wrap_ground('<p class="climb-eyebrow">Climb27 / 30 June &amp; 1 July 2027</p><p class="climb-eyebrow">Who it is for</p>'
                    '<h2 class="climb-statement climb-ruled">Pick your <span class="climb-accent">ticket</span></h2>'),
        "The eyebrow is the small uppercase line above a headline: the edition, the date or the audience. Keep it under six words. "
        "Use `climb-ruled` on the headline for the short orange rule.")

    add("Sticker", "Festival devices", "Tilted stickers that pin to a card or photo corner", 360,
        wrap_ground('<div class="d-flex flex-wrap gap-5 align-items-center pt16 pb16">'
                    '<p class="climb-sticker">VIP</p><p class="climb-sticker">Climb27</p><p class="climb-sticker climb-sticker-dark">#ClimbUK</p>'
                    '<div class="climb-photo" style="max-width:320px"><img src="%s" class="img img-fluid" alt="Guests at the drinks reception">'
                    '<p class="climb-sticker">VIP</p></div></div>' % blob("climb_awards_winners.jpg")),
        "Stickers are the festival's stamps: one or two words, tilted, pinned to the corner of a photo or a ticket.\n\n"
        "- `climb-sticker` is Climb Orange with Dark Brown text; `climb-sticker-dark` is Dark Brown with orange text.\n"
        "- `climb-sticker-pin` pins it to the top corner of its card.\n- One sticker per card. Words only, never a sentence.")

    add("Tags", "Festival devices", "Outlined tags for formats and topics, and the live label", 260,
        wrap_ground('<div class="climb-tags"><p class="climb-tag">Fireside chat</p><p class="climb-tag">Panel</p>'
                    '<p class="climb-tag">Masterclass</p><p class="climb-tag">Roundtable</p></div>'
                    '<p class="climb-ticket-kicker climb-live">Tickets on sale now</p>'),
        "Tags name formats and topics. They are outlined, never filled, so they do not compete with buttons.\n\n"
        "The live label (`climb-live`) adds a pulsing orange dot. Use it only for something that is happening now: tickets on sale, "
        "a live stream, doors open. The pulse stops under reduced motion.")

    photo = blob("climb_awards_winners.jpg")
    add("Outline numerals", "Festival devices", "Giant outlined numbers for section numbers and big stats", 1480,
        '<div>'
        '<section class="s_climb_kit climb-p3 pt96 pb96" style="background:linear-gradient(90deg,rgba(30,15,5,.96) 35%%,rgba(30,15,5,.7)),url(%s) center/cover;">'
        '<div class="container"><div class="climb-numbered"><p class="climb-outline-num" aria-hidden="true">05</p>'
        '<div><p class="climb-eyebrow">Chapter five</p><h2 class="climb-statement"><em>Real</em> <span class="climb-accent">photos</span></h2></div></div></div></section>'
        % photo
        + wrap_ground('<div class="climb-numbered"><p class="climb-outline-num climb-outline-num-sm" aria-hidden="true">01</p>'
                      '<h3 class="climb-statement climb-statement-sm">Find your <span class="climb-accent">people</span></h3></div>'
                      '<div class="climb-numbered pt32"><p class="climb-outline-num climb-outline-num-sm" aria-hidden="true">02</p>'
                      '<h3 class="climb-statement climb-statement-sm">Grow your <em>business</em></h3></div>')
        + wrap_ground('<div class="climb-stats"><div><p class="climb-outline-num climb-outline-num-sm">2</p><p class="climb-stat-label">Days of business growth</p></div>'
                      '<div><p class="climb-outline-num climb-outline-num-sm">27</p><p class="climb-stat-label">The next edition</p></div></div>', theme="alt")
        + '<section class="s_climb_kit climb-p3 pt48 pb48"><p class="climb-outline-marquee" aria-hidden="true">Find your people / Grow your business / Find your people</p></section>'
        '</div>',
        "Outline numerals are giant numbers drawn as an orange outline with no fill. They number chapters and sections and carry the "
        "odd big stat, like a festival poster.\n\n"
        "- `climb-outline-num`: Montserrat ExtraBold (800), upright, tabular figures, letter spacing -0.04em, line height 0.8, no fill "
        "and a Climb Orange stroke of about 1% of the size (4px at 380px). `climb-outline-num-sm` is the stat size with a 2px stroke. "
        "Never go below a 2px stroke.\n"
        "- Best on a dark ground or over a photo on a Dark Brown fade. On White or Light Grey the stroke turns to the darker text orange; "
        "on Climb Orange it turns White.\n"
        "- Section numbers are two digits (01 to 10) and decorative: mark them `aria-hidden` and put the real heading in text beside them "
        "(`climb-numbered` lines them up).\n"
        "- A stat number stays readable text with its label underneath in words. With `data-climb-size=\"aaa\"` the stat fills solid.\n"
        "- Use one size of outline numeral per view. Never outline words or headlines with it; the only outlined words are the quiet marquee.\n"
        "- `climb-outline-marquee`: a giant italic uppercase line in Orange Tint at 35% with a 2px stroke, running off the edge behind a "
        "section. Decorative only, so `aria-hidden`, and never the only place the words appear.\n"
        "- In design apps: same font, weight and tracking, fill none, stroke Climb Orange centred at about 1% of the point size.")

    # ---------------------------------------------------------------- Tickets and stands
    ticket = pick(S["s_climb_hero_ticket"], ".climb-ticket")
    partner = pick(S["s_climb_ticket_band"], ".climb-ticket")
    add("Ticket card", "Tickets and stands", "The glass ticket with stub notches, highlighted and on orange", 640,
        '<div>' + wrap_ground('<div class="row g-5 align-items-start"><div class="col-lg-6">%s</div></div>' % ticket) +
        '<section class="s_climb_kit climb-p4 climb-glow pt48 pb48"><div class="container"><div class="row"><div class="col-lg-6">%s</div></div></div></section></div>'
        % partner,
        "The ticket card is the thing people pick up: a glass card with stub notches, a sticker and one button.\n\n"
        "- `climb-ticket` on dark grounds; add `climb-ticket-hl` for the one ticket to pick (orange edge and glow).\n"
        "- On Climb Orange it turns Dark Brown.\n- Kicker, name, three short benefits, one button. Prices go on offer cards.\n"
        "- `climb-levels` lists packages with a note on the right (passes, sizes).")

    offers = pick(S["s_climb_tickets"], ".climb-offers")
    add("Offer cards", "Tickets and stands", "Ticket offers: the pick, the rest, and a closed release", 620,
        wrap_ground(offers, "alt"),
        "Offer cards sit side by side so people can compare. One is highlighted, the rest are equal.\n\n"
        "- `climb-offer-hl` is the offer to pick: orange edge, glow and a filled kicker, never raised, so its button stays on the row's line.\n"
        "- `is-soldout` dashes the edge, strikes the price and disables the button. Use it only when that release is truly closed.\n"
        "- `climb-was` shows the full price struck through; `climb-remaining` shows how many are left, only from live stock.\n"
        "- Prices always say inc VAT. No false scarcity: never write last few, hurry or selling fast.")

    ladder = pick(S["s_climb_ticket_ladder"], ".climb-ladder")
    add("Release ladder", "Tickets and stands", "Price releases as rising steps: past, now and next", 520,
        wrap_ground(ladder),
        "The release ladder shows that the price rises with every release, and where today sits on it.\n\n"
        "- Each `climb-ladder-step` sets `--climb-step` (1, 2, 3 ...) so its cap rises.\n"
        "- `is-past` greys the cap and strikes the price; `is-current` fills it orange with a glow and the left pill; `is-next` dashes it.\n"
        "- States are written in words as well as shown (Closed, On sale now, Next), never colour alone.\n"
        "- On phones the ladder turns into a vertical rail.")

    stands = pick(S["s_climb_stands"], ".climb-offers")
    add("Stand cards", "Tickets and stands", "Exhibition stands with an outlined floor plan and stock", 600,
        wrap_ground(stands),
        "Stand cards show the exhibition space. The outlined plan (`climb-plan-1`, `-2`, `-4`) shows the footprint at a glance.\n\n"
        "- `climb-left` shows stock left, from live stock only. A sold-out stand uses `is-soldout`.\n"
        "- Name, size, what is included, price inc VAT, one button.")

    team = pick(S["s_climb_tickets"], ".climb-team")
    add("Group offer", "Tickets and stands", "The orange band for teams and groups", 260,
        wrap_ground(team, "alt"),
        "The group offer is one orange band under the ticket offers: bring the team, one line, one Dark Brown button.")

    # ---------------------------------------------------------------- Cards
    moments = pick(S["s_climb_moments"], ".row.g-4")
    add("Moment card", "Cards", "Photo cards for the big moments", 560,
        wrap_ground(moments),
        "Moment cards show what happens: a real Climb26 photo, a short name, one sentence. Three in a row. "
        "Photos lift slightly on hover.")

    aud = pick(S["s_climb_audiences"], ".row.g-4")
    add("Audience card", "Cards", "Photo cards that route each audience to its page", 520,
        wrap_ground(aud, "alt"),
        "Audience cards let each audience pick themselves. The whole card is the link. Four in a row on desktop, two on tablets, "
        "one on phones. The line under the name is the audience's own reason to come.")

    quotes = pick(S["s_climb_photo_wall"], ".row.g-4.pt48")
    add("Quote", "Cards", "Testimonials from named, real people", 400,
        wrap_ground(quotes),
        "Quotes come only from named, real people who agreed to them, with their role and company. Never invent a quote, a name or a company.")

    lineup = pick(S["s_climb_lineup"], ".climb-lineup")
    add("Lineup", "Cards", "A festival poster lineup of names in three sizes", 420,
        wrap_ground('<div class="row"><div class="col-lg-8">%s</div></div>' % lineup),
        "The lineup sets names like a festival poster: the biggest names first, three sizes, separated by orange slashes. "
        "Only names that are confirmed or that appeared at a past edition, labelled as such.")

    # ---------------------------------------------------------------- Photo fades and sections
    fades = "".join(S[k] for k in ("s_climb_band", "s_climb_band_heat", "s_climb_band_orange"))
    add("Photo fade", "Sections", "Brown, Heat and Orange fades over Climb26 photos", 1900, '<div>%s</div>' % fades,
        "A photo fade puts a real photo behind the words and fades it to a brand colour on the side the words sit.\n\n"
        "- **Brown**: Dark Brown from the left and to a solid foot, so cards can sit on it. The Business with a party section.\n"
        "- **Heat**: Dark Brown on the left, warming to orange light on the right. For the evening and the after parties.\n"
        "- **Orange**: Climb Orange washing over the photo. Never over faces; use objects, stages and crowds from behind.\n"
        "- Words sit where the fade is 85% or more. End on solid colour. Flip the fade (270deg) to put words on the right.\n"
        "- Photo fades stay dark (or orange) in both themes.")

    for key, name, sub, h, readme in [
        ("s_climb_hero", "Hero", "Full-bleed stage photo with the poster line", 820,
         "The hero opens a page: a full-bleed Climb26 stage photo faded from the left, an eyebrow, one display line, a lead, two buttons and the pull link."),
        ("s_climb_hero_ticket", "Hero with ticket", "The hero with a glass ticket to pick up", 820,
         "The hero with a ticket adds the glass ticket card on the right, for pages built around one ticket."),
        ("s_climb_moments", "Moments", "Statement, lead and three moment cards", 1000,
         "Moments sells the feeling: one statement with an italic word, a lead, three moment cards and two buttons."),
        ("s_climb_photo_wall", "Photo wall", "A mosaic of Climb26 photos and two quotes", 1300,
         "The photo wall shows the last edition: one big tile with a sticker, a wall of squares and two quotes from people who were there."),
        ("s_climb_ticket_band", "Ticket band", "Climb Orange band with a Dark Brown ticket", 640,
         "The ticket band is the partner pitch on Climb Orange: one big line, a lead, one button and a Dark Brown ticket listing the packages."),
        ("s_climb_tickets", "Tickets", "Offers, the release ladder, the group offer and the pull link", 1500,
         "The tickets section is the order on a ticket page: the offers, the release ladder, the group offer and a pull link for anyone still choosing."),
        ("s_climb_ticket_ladder", "Ticket ladder section", "The release ladder on its own", 520,
         "The release ladder as its own section, for a pricing page or under a hero."),
        ("s_climb_stands", "Stands", "Exhibition stands with plans and stock", 760,
         "The stands section sells exhibition space with outlined plans and live stock."),
        ("s_climb_lineup", "Speaker lineup", "Apply to speak, with the poster lineup", 760,
         "The speaker lineup invites people to apply, with format tags and the poster lineup of previous speakers."),
        ("s_climb_logo_marquee", "Logo marquee", "Rows of partner logos drifting past", 560,
         "The logo marquee shows partners, exhibitors and attendees as two rows drifting in opposite directions with faded edges. "
         "It pauses on hover and stops under reduced motion. Logos sit in a neutral tone and go to colour on hover."),
        ("s_climb_audiences", "Audience chooser", "Four audience cards on Charcoal", 760,
         "The audience chooser asks what brings you to ClimbUK and routes each audience to its own page."),
        ("s_climb_moment", "Moment", "A big photo with a sticker and one line", 640,
         "Moment is one photo, one sticker, one line and one button. Use it to put one thing in the spotlight, like the ClimbAwards."),
        ("s_climb_close", "Close", "Climb Orange close with the last question", 560,
         "The close ends every ticket page on Climb Orange: the last question, the dates and one clear next step in Dark Brown."),
        ("s_climb_divider", "Divider", "Rising chevrons between two sections", 200,
         "The divider is a low band of rising chevrons between two sections. Match its preset to the section above."),
    ]:
        add(name, "Sections", sub, h, S[key], readme)

    # ---------------------------------------------------------------- Brand
    L = BLOBS["logos"]
    logo_rows = "".join(
        '<div class="climb-logo-row"><img class="climb-on-dark" src="%s" alt="%s logo"><img class="climb-on-light" src="%s" alt="%s logo">'
        '<img class="climb-on-dark climb-logo-icon" src="%s" alt=""><img class="climb-on-light climb-logo-icon" src="%s" alt=""></div>'
        % (L["%s_reversed-dark.svg" % b], b, L["%s_full-colour-light.svg" % b], b,
           L["%s_icon-monogram.svg" % b], L["%s_icon-monogram.svg" % b]) for b in ("ClimbUK", "Climb27", "ClimbGroup"))
    add("Logo", "Brand", "The right logo for the theme: reversed on dark, full colour on light", 520,
        wrap_ground('<div class="climb-logos">%s</div>' % logo_rows),
        "Use the reversed logo on Dark Brown, Charcoal and photos; the full-colour logo on White and Light Grey; the mono logos "
        "on Climb Orange. This preview switches with the theme toggle.\n\n"
        "- Clear space: the height of the large C in Climb on every side.\n- Minimum width: 120px on screen, 30mm in print.\n"
        "- The li monogram is for favicons and app icons; the stacked tile is for social avatars.\n- Never recolour, stretch, outline or "
        "put the logo on a busy part of a photo.")

    icons = "".join('<a href="#" class="climb-social" aria-label="%s">%s</a>' % (n.title(), glyph(n))
                    for n in ("linkedin", "instagram", "tiktok", "facebook", "mail", "phone", "globe", "ticket", "calendar"))
    add("Social icons", "Brand", "Round icon buttons for socials and contact", 300,
        wrap_ground('<div class="climb-socials">%s</div><div class="climb-socials climb-socials-quiet">%s</div>' % (icons, icons)),
        "Social and contact icons are round buttons: Climb Orange with a Dark Brown glyph, or quiet outlines on busy grounds. "
        "Every icon is a link with a text label for screen readers. The PNG set for email signatures is in the Signature downloads.")

    sig = signature_html(BLOBS["signature"], L)
    add("Email signature", "Brand", "The full signature block: contact, logo and icons, notice, photo banner, legal line", 640,
        '<section class="s_climb_kit climb-p5 pt32 pb32" data-climb-theme="sig"><div class="container">%s</div></section>' % sig,
        "The email signature is one block, top to bottom: the sign-off; name, role, a Book a meeting link, phone numbers, email and "
        "website; the logo with a row of outlined social icons on the right; the help note that routes enquiries; the campaign "
        "banner; and the confidentiality line. Everything except the logo, icons and banner is live text.\n\n"
        "It reads on white and on dark mail clients: on white, links are Link on White; on dark, links are Climb Orange and the "
        "logo switches to the reversed version (this preview switches with the theme). Download the HTML template, the outline "
        "icons and the Email banners. Swap the banner with the campaign and link it to that campaign's page.")

    add("Elevation", "Foundations", "Shadows and glows from flat to floating", 360,
        wrap_ground('<div class="climb-elev">%s</div>' % "".join(
            '<div style="box-shadow:var(--shadow-%s)"><b>%s</b><span>%s</span></div>' % (k, k, u) for k, u in [
                ("0", "Flat"), ("1", "Cards at rest"), ("2", "Hover"), ("3", "Menus"), ("4", "Dialogs"),
                ("glow", "The pick"), ("ticket", "Ticket card"), ("button-glow", "Primary hover")])),
        "Elevation is soft and warm: shadows are Dark Brown, never black, and the pick glows orange. Use the shadow tokens, not "
        "your own values.")

    add("Motion", "Foundations", "Rise, spring and the marquee drift", 360,
        wrap_ground('<div class="climb-motion"><div><i class="m-rise"></i><b>Rise</b><span>Entrances</span></div>'
                    '<div><i class="m-spring"></i><b>Spring</b><span>Hover and press</span></div>'
                    '<div><i class="m-pulse"></i><b>Pulse</b><span>Live label</span></div>'
                    '<div><i class="m-drift"></i><b>Drift</b><span>Marquee</span></div></div>'),
        "Motion is punchy and short: things rise into place, buttons spring, live labels pulse, logos drift. Use the duration and "
        "easing tokens. Everything stops or becomes a simple fade under reduced motion.")
    return C


def signature_html(sig, logos):
    E = BLOBS["email"]
    icons = "".join('<a href="#" aria-label="ClimbUK on %s"><img src="%s" width="24" height="24" alt=""></a>'
                    % (n, E["icon_%s_orange_outline@2x.png" % k]) for k, n in (
                        ("facebook", "Facebook"), ("x", "X"), ("bluesky", "Bluesky"), ("instagram", "Instagram"),
                        ("linkedin", "LinkedIn")))
    return ('<div class="climb-sig"><p>Kind regards,</p>'
            '<div class="climb-sig-top"><div><p class="climb-sig-name">Alex Morgan</p><p>Partnerships Lead</p>'
            '<p><a href="#">Book a meeting with me</a></p>'
            '<p><b>T:</b> 0300 123 4567 &nbsp; <b>M:</b> 07700 900123</p>'
            '<p><a href="#">alex.morgan@climb-uk.com</a> | <a href="#">climb-uk.com</a></p></div>'
            '<div class="climb-sig-brand"><img class="climb-on-dark" src="%s" alt="ClimbUK"><img class="climb-on-light" src="%s" alt="ClimbUK">'
            '<div class="climb-sig-icons">%s</div></div></div>'
            '<p class="climb-sig-note">To help us respond quickly, non-sales enquiries go through our <a href="#">Helpdesk</a> before email. '
            'For partnerships, email <a href="#">partnerships@climb-uk.com</a>; for exhibiting, <a href="#">exhibitors@climb-uk.com</a>.</p>'
            '<a href="#"><img class="climb-sig-banner" src="%s" width="720" alt="Climb27. Your business. Bigger stage. Get your ticket."></a>'
            '<p class="climb-sig-legal">This email and any attachments are confidential and meant only for the person they are addressed to. '
            'If it reached you by mistake, please tell the sender and delete it.</p></div>'
            % (logos["ClimbUK_reversed-dark.svg"], logos["ClimbUK_full-colour-light.svg"], icons,
               E["climb27_email-banner_bigger-stage-dark_1440x410.jpg"]))


EXTRA_CSS = """
.climb-on-light{display:none}
[data-theme="light"] .climb-on-light{display:block}
[data-theme="light"] .climb-on-dark{display:none}
.climb-logos{display:grid;gap:2.5rem}
.climb-logo-row{display:flex;align-items:center;gap:3rem}
.climb-logo-row img{height:64px;width:auto}
.climb-logo-row img.climb-logo-icon{height:64px}
.climb-socials{display:flex;flex-wrap:wrap;gap:.75rem;margin-bottom:1rem}
.climb-social{display:inline-flex;align-items:center;justify-content:center;width:3rem;height:3rem;border-radius:50%;background:var(--climb-orange);color:var(--dark-brown)!important;transition:transform var(--duration-fast,150ms) var(--easing-spring,ease)}
.climb-social:hover{transform:translateY(-3px) scale(1.06)}
.climb-social svg{width:1.4rem;height:1.4rem}
.climb-socials-quiet .climb-social{background:transparent;color:currentColor!important;border:2px solid currentColor}
.climb-sig{font-family:var(--font-body);font-size:14px;line-height:1.6;max-width:720px}
.climb-sig p{margin:0}
.climb-sig a{text-decoration:underline}
.climb-p1 .climb-sig{color:var(--body-slate)} .climb-p1 .climb-sig a{color:var(--link-on-white)!important}
.climb-p5 .climb-sig{color:var(--light-grey)} .climb-p5 .climb-sig a{color:var(--climb-orange)!important}
.climb-sig-top{display:flex;justify-content:space-between;gap:2rem;margin:1rem 0}
.climb-sig-name{font-family:var(--font-display);font-weight:700;font-size:16px}
.climb-p1 .climb-sig-name{color:var(--charcoal)} .climb-p5 .climb-sig-name{color:var(--white)}
.climb-sig-top>div:first-child{flex:1 1 auto}
.climb-sig-brand{flex:0 0 220px}
.climb-sig-brand>img{width:200px;margin-left:auto}
.climb-sig-brand>img.climb-on-dark{display:block}
[data-theme="light"] .climb-sig-brand>img.climb-on-dark{display:none}
[data-theme="light"] .climb-sig-brand>img.climb-on-light{display:block}
.climb-sig-icons img{width:24px;height:24px}
.climb-sig-icons{display:flex;gap:8px;justify-content:flex-end;margin-top:14px}
.climb-sig-note{font-style:italic;margin-bottom:12px!important}
.climb-sig-banner{width:100%;height:auto;display:block}
.climb-sig-legal{font-size:11px;opacity:.75;margin-top:10px!important}
.climb-elev{display:grid;grid-template-columns:repeat(4,1fr);gap:1.5rem}
.climb-elev div{background:var(--surface-alt);border-radius:var(--radius-card);padding:1.25rem;display:flex;flex-direction:column;gap:.25rem}
.climb-elev b{font-family:var(--font-display);color:var(--ink)}
.climb-elev span{font-size:14px;color:var(--text-muted)}
.climb-motion{display:grid;grid-template-columns:repeat(4,1fr);gap:1.5rem}
.climb-motion div{background:var(--surface-alt);border-radius:var(--radius-card);padding:1.25rem;display:flex;flex-direction:column;gap:.25rem;overflow:hidden}
.climb-motion b{font-family:var(--font-display);color:var(--ink)}
.climb-motion span{font-size:14px;color:var(--text-muted)}
.climb-motion i{display:block;width:2.5rem;height:2.5rem;border-radius:.6rem;background:var(--climb-orange);margin-bottom:.75rem}
.m-rise{animation:climb-demo-rise 2.4s var(--easing-rise,cubic-bezier(.2,.8,.2,1)) infinite}
.m-spring{animation:climb-demo-spring 1.6s var(--easing-spring,cubic-bezier(.34,1.56,.64,1)) infinite alternate}
.m-pulse{border-radius:50%!important;animation:climb-pulse 1.6s ease-out infinite}
.m-drift{animation:climb-demo-drift 4s linear infinite}
@keyframes climb-demo-rise{0%{opacity:0;transform:translateY(24px)}40%,100%{opacity:1;transform:none}}
@keyframes climb-demo-spring{from{transform:scale(1)}to{transform:scale(1.18) translateY(-6px)}}
@keyframes climb-demo-drift{from{transform:translateX(-3rem)}to{transform:translateX(12rem)}}
@media (prefers-reduced-motion: reduce){.m-rise,.m-spring,.m-pulse,.m-drift{animation:none}}
.climb-outline-num{display:block;margin:0;font-family:var(--climb-font-family-display,Montserrat,sans-serif);font-weight:800;font-style:normal;font-size:clamp(7.5rem,22vw,23.75rem);line-height:.8;letter-spacing:-.04em;font-variant-numeric:tabular-nums;color:transparent;-webkit-text-stroke:4px var(--climb-orange)}
.climb-outline-num-sm{font-size:clamp(4rem,9vw,7.5rem);-webkit-text-stroke-width:2px}
.climb-p1 .climb-outline-num,.climb-p2 .climb-outline-num{-webkit-text-stroke-color:var(--orange-text)}
.climb-p4 .climb-outline-num{-webkit-text-stroke-color:var(--white)}
@supports not (-webkit-text-stroke:1px){.climb-outline-num{color:var(--climb-orange)}}
@media (forced-colors:active){.climb-outline-num{color:CanvasText;-webkit-text-stroke:0}}
[data-climb-size="aaa"] .climb-outline-num-sm{color:currentColor;-webkit-text-stroke:0}
.climb-numbered{display:flex;flex-wrap:wrap;align-items:flex-end;gap:1.5rem 2.5rem}
.climb-numbered .climb-statement{margin-bottom:0}
.climb-stats{display:flex;flex-wrap:wrap;gap:2rem 4rem}
.climb-stat-label{margin:.75rem 0 0;font-family:var(--climb-font-family-display,Montserrat,sans-serif);font-weight:700;font-size:1rem;letter-spacing:.08em;text-transform:uppercase}
.climb-outline-marquee{margin:0;overflow:hidden;white-space:nowrap;font-family:var(--climb-font-family-display,Montserrat,sans-serif);font-weight:800;font-style:italic;font-size:clamp(3rem,7vw,5.75rem);line-height:1;text-transform:uppercase;color:transparent;-webkit-text-stroke:2px rgba(242,174,134,.35)}
"""


def main():
    global MODULE
    ap = argparse.ArgumentParser()
    ap.add_argument("--bootstrap", default=str(pathlib.Path.cwd() / "node_modules/bootstrap/scss"))
    ap.add_argument("--module", default=str(MODULE), help="path to the website module that holds the blocks")
    args = ap.parse_args()
    MODULE = pathlib.Path(args.module).resolve()
    OUT.mkdir(exist_ok=True)
    css = build_css(args.bootstrap) + EXTRA_CSS
    (OUT / "bundle.css").write_text(css)
    S = load_sections()
    comps = components(S)
    for c in comps:
        d = OUT / ident(c["name"])
        d.mkdir(exist_ok=True)
        body = c["body"]
        assert "odoo" not in body.lower(), c["name"]
        (d / "preview.html").write_text(
            '<!-- @dsCard group="%s" height=%d width=%d subtitle="%s" -->\n%s\n<script>%s</script>\n'
            % (c["group"], c["height"], c["width"], c["subtitle"], body, PREVIEW_JS))
        (d / "README.md").write_text("# %s\n\n%s\n" % (c["name"], c["readme"]))
    (OUT / "bundle.js").write_text(bundle_js(comps))
    (OUT / "index.d.ts").write_text(index_dts(comps))
    (OUT / "components.json").write_text(json.dumps([dict({k: c[k] for k in ("name", "group", "subtitle")}, id=ident(c["name"])) for c in comps], indent=1))
    print("[components] %d components, bundle.css %d KB" % (len(comps), len(css) // 1024))


if __name__ == "__main__":
    main()
