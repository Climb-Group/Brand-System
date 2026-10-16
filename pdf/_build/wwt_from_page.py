"""Writes pdf/brochures/climb27_who-was-there.copy.md from the Who was there page on the ClimbUK website.

The pack prints the page word for word, so when the page changes, run this against the page's QWeb view (the
who_was_there.xml template in the website repository) and rebuild:

    python3 pdf/_build/wwt_from_page.py path/to/who_was_there.xml

The eyebrows, two headlines and the closing page are the pack's own words and live in PACK below. Quotes written
before a festival (about what it would be, not what it was) stay on the website but are left out of print; their
sources are in BEFORE.
"""
import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "brochures", "climb27_who-was-there.copy.md")

# Sources whose quotes on the page were written before the festival they name.
BEFORE = {"Phil Witcherley", "Henrietta Newble", "Mudrik Zubeir Ahmed", "Medilink North of England Limited",
          "NatWest Group", "Rebecca Holden"}

# section id on the page: (key in the copy file, eyebrow, headline override or None to use the page's)
SECTIONS = [
    ("featured-logos", "wwt.names", "Partners, speakers and sessions", None),
    ("partners", "wwt.partners", "Partners and exhibitors", "Backed by [[partners]] who _return_"),
    ("sessions", "wwt.sessions", "On stage at Climb26", None),
    ("climb26-testimonials", "wwt.quotes26", "In their words", None),
    ("speakers", "wwt.speakers", "Who spoke", None),
    ("in-the-room", "wwt.room", "Everyone who came", None),
    ("climb25-testimonials", "wwt.quotes25", "In their words", None),
    ("speaker-organisations", "wwt.orgs", "Who spoke", None),
    ("climb24-testimonials", "wwt.quotes24", "In their words", None),
    ("climb24-speakers", "wwt.speakers24", "Who spoke", None),
    ("climb23-testimonials", "wwt.quotes23", "In their words", None),
    ("climb23-sessions", "wwt.sessions23", "On stage at Climb23", None),
    ("climb23-speakers", "wwt.speakers23", "Who spoke", None),
]

# The partners section lists four groups; the first is the main list, the rest get their own keys.
PARTNER_GROUPS = ["wwt.partners", "wwt.partners24", "wwt.exhibitors24", "wwt.partners23"]

PACK = {
    "wwt.cover.headline": "[[Who]] was _there_",
    "wwt.cta.line1": "Join them at",
    "wwt.cta.line2": "Climb27",
    "wwt.cta.button": "Partner with ClimbUK",
    "wwt.cta.qr": "Scan to book a call",
}


def text(s):
    """Inline markup to copy-file text: <em> becomes _word_, other tags drop, entities decode, spaces fold."""
    s = re.sub(r"<em>(.*?)</em>", r"_\1_", s, flags=re.S)
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def logos(body):
    out = []
    for src, alt in re.findall(r'<img src="/climb27/logos/([^"]+)"[^>]*alt="([^"]*)"', body):
        out.append([src, text(alt)] if alt.strip() else [src])
    return out


def items(body):
    return [text(li) for li in re.findall(r"<li>(.*?)</li>", body, re.S)]


def people(body):
    """'<strong>Name</strong>, role' to [name, role]; a speaker with no role keeps the name alone."""
    out = []
    for li in re.findall(r"<li>(.*?)</li>", body, re.S):
        m = re.match(r"\s*<strong>(.*?)</strong>\s*,?\s*(.*)", li, re.S)
        out.append([text(m.group(1))] + ([text(m.group(2))] if text(m.group(2)) else []))
    return out


def quotes(body):
    kept, left = [], []
    for q, by in re.findall(r'climb-quote-text">(.*?)</p>\s*<p class="climb-quote-by">(.*?)</p>', body, re.S):
        m = re.match(r"\s*<strong>(.*?)</strong>(.*)", by, re.S)
        name, role = text(m.group(1)), text(m.group(2))
        (left if name in BEFORE else kept).append([text(q), name] + ([role] if role else []))
    return kept, left


def build(xml):
    secs = dict(re.findall(r'<section id="([^"]+)"[^>]*>(.*?)</section>', xml, re.S))
    intro = re.search(r'<section aria-labelledby="who-was-there-title".*?</section>', xml, re.S).group(0)
    out = [("wwt.cover.eyebrow", text(re.search(r'climb-eyebrow">(.*?)</p>', intro, re.S).group(1))),
           ("wwt.cover.headline", PACK["wwt.cover.headline"]),
           ("wwt.cover.intro", text(re.search(r"climb-social-proof-intro\">(.*?)</p>", intro, re.S).group(1)))]
    notes = {}
    for sid, key, eyebrow, headline in SECTIONS:
        if sid not in secs:
            continue
        body = secs[sid]
        out.append((key + ".eyebrow", eyebrow))
        out.append((key + ".headline", headline or text(re.search(r"<h2[^>]*>(.*?)</h2>", body, re.S).group(1))))
        lead = re.search(r'climb-social-proof-lead">(.*?)</p>', body, re.S)
        if lead:
            out.append((key + ".intro", text(lead.group(1))))
        if "testimonials" in sid:
            kept, left = quotes(body)
            out.append((key + ".items", kept))
            note = "quote | name | role and organisation. Word for word from the website, [...] included."
            if left:
                note += (" Left out of print because they were written before the festival, not about it: %s."
                         % ", ".join(sorted({q[1] for q in left})))
            notes[key + ".items"] = note
        elif sid in ("featured-logos", "in-the-room"):
            out.append((key + ".logos", logos(body)))
            notes[key + ".logos"] = "logo file | organisation, in the order the website shows them; a file alone has no name on the page"
        elif sid == "sessions":
            cards = re.findall(r'<div class="climb-proof-card">(.*?)</div>', body, re.S)
            rows = []
            for c in cards:
                title = text(re.search(r"<h3[^>]*>(.*?)</h3>", c, re.S).group(1))
                logo = re.search(r'/climb27/logos/([^"]+)"', c)
                rows.append([title] + ([logo.group(1)] if logo else []))
            out.append((key + ".items", rows))
            notes[key + ".items"] = "session title | logo file where we hold one"
        elif sid == "partners":
            groups = re.split(r'<h3 class="climb-social-proof-h3">', body)[1:]
            for gkey, g in zip(PARTNER_GROUPS, groups):
                title, _, rest = g.partition("</h3>")
                out.append((gkey + ".title", text(title)))
                out.append((gkey + ".items", [[n] for n in items(rest)]))
        elif "speakers" in sid:
            out.append((key + ".items", people(body)))
            notes[key + ".items"] = "name | role and organisation as they gave it"
        else:
            out.append((key + ".items", [[n] for n in items(body)]))
    for k in ("wwt.cta.line1", "wwt.cta.line2", "wwt.cta.button", "wwt.cta.qr"):
        out.append((k, PACK[k]))

    lines = ["---", "title: Who was there, Climb23 to Climb26", "output: pdf/brochures/climb27_who-was-there.pdf",
             "build: pdf/_build/build_brochures.sh",
             "note: Every word printed in the Who was there pack comes from this file. It is written by "
             "pdf/_build/wwt_from_page.py from the public Who was there page on the ClimbUK website, word for word; "
             "change the page and run the script rather than editing the lists here. Logo files are in "
             "pdf/brochures/_build/logos.", "---", ""]
    for key, value in out:
        lines.append("## " + key)
        if key in notes:
            lines.append("<!-- note: %s -->" % notes[key])
        if isinstance(value, list):
            lines += ["- " + " | ".join(row) for row in value]
        else:
            lines.append(value)
        lines.append("")
    return "\n".join(lines)


def main(argv):
    if len(argv) != 1:
        print(__doc__)
        return 2
    with open(argv[0], encoding="utf-8") as f:
        page = build(f.read())
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print("wrote", os.path.relpath(OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
