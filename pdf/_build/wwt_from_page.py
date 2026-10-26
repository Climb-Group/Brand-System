"""Writes pdf/brochures/climb27_who-was-there.copy.md from the Who was there page on the ClimbUK website.

Both sales brochures end with the "In the room at ClimbUK" page: the page's featured logos, word for word. When the
page changes, run this against the page's QWeb view (the who_was_there.xml template in the website repository) and
rebuild the brochures:

    python3 pdf/_build/wwt_from_page.py path/to/who_was_there.xml

The eyebrow and headline are the brochures' own words and live in PACK below. The separate Who was there pack is no
longer made (the owner's call, 2026-10-20): the rest of the page stays on the website only.
"""
import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "brochures", "climb27_who-was-there.copy.md")

# In-the-room logos added to the page's featured logos so the page ends on a full row of 12.
NAMES_FILL = ["ebay.png", "bbc-sport.png", "coutts-company.png", "digital-catapult.png"]
# Featured logos the brochures leave out (the owner's call, 2026-10-26), each swapped in place for an in-the-room logo.
NAMES_SWAP = {"clubit-group.png": "royal-mail.png", "wainwright-consulting-limited.png": "taylor-wessing.png"}

PACK = {
    "wwt.names.eyebrow": "Partners, speakers and sessions",
    "wwt.names.headline": "In the room at _ClimbUK_",
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


def build(xml):
    secs = dict(re.findall(r'<section id="([^"]+)"[^>]*>(.*?)</section>', xml, re.S))
    body = secs["featured-logos"]
    lead = re.search(r'climb-social-proof-lead">(.*?)</p>', body, re.S)
    got = logos(body)
    room = {r[0]: r for r in logos(secs["in-the-room"])}
    assert all(f in room for f in NAMES_FILL), "a NAMES_FILL logo is not in the page's in-the-room logos"
    got += [room[f] for f in NAMES_FILL if f not in {r[0] for r in got}]
    assert all(f in room for f in NAMES_SWAP.values()), "a NAMES_SWAP logo is not in the page's in-the-room logos"
    got = [room[NAMES_SWAP[r[0]]] if r[0] in NAMES_SWAP else r for r in got]
    assert len(got) % 12 == 0, "the logos do not fill whole rows of 12: %d" % len(got)
    out = [("wwt.names.eyebrow", PACK["wwt.names.eyebrow"]), ("wwt.names.headline", PACK["wwt.names.headline"]),
           ("wwt.names.intro", text(lead.group(1))), ("wwt.names.logos", got)]
    notes = {"wwt.names.logos": "logo file | organisation, in the order the website shows them; a file alone has no "
                                "name on the page; the last ones are NAMES_FILL picks from the in-the-room logos, and NAMES_SWAP "
                                "logos stand in for featured ones the brochures leave out"}

    lines = ["---", "copy: climb27-who-was-there", "title: In the room at ClimbUK",
             "deliverable: The In the room at ClimbUK page near the end of the exhibitor and partner brochures",
             "output: pdf/brochures/climb27_exhibitor-brochure.pdf pdf/brochures/climb27_partner-brochure.pdf",
             "build: pdf/_build/build_brochures.sh",
             "source: mirror",
             "note: The In the room at ClimbUK page in both brochures prints this file. It is written by "
             "pdf/_build/wwt_from_page.py from the public Who was there page on the ClimbUK website, word for word; "
             "change the page and run the script rather than editing the list here. Logo files are in "
             "pdf/brochures/_build/logos.", "---", ""]
    for key, value in out:
        lines.append("<!-- @%s -->" % key)
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
