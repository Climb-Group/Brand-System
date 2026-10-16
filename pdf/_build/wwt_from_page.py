"""Writes pdf/brochures/climb27_who-was-there.copy.md from the Who was there page on the ClimbUK website.

The pack prints the page word for word, so when the page changes, run this against the page's QWeb view (the
who_was_there.xml template in the website repository) and rebuild:

    python3 pdf/_build/wwt_from_page.py path/to/who_was_there.xml

The eyebrows, two headlines and the closing page are the pack's own words and live in PACK below. Quotes written
before a festival (about what it would be, not what it was) stay on the website but are left out of print; their
sources are in BEFORE.

The pack prints a chosen part of the page (the owner's review, 2026-10-16): speakers and sessions people will know,
the organisations that came back, the Climb26 quotes and quotes about ClimbUK in general. The picks are names in
HEADLINERS, KNOWN, SESSIONS23, GENERAL and RETURNERS below; the words printed for each are still the page's.
"""
import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "brochures", "climb27_who-was-there.copy.md")
LOGOS = os.path.join(HERE, "..", "brochures", "_build", "logos")

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

# Speakers people will know, from every edition, with the role and organisation as one of their page entries gives it
# (the edition named, where they gave a better known one there), and their organisation's logo file where we hold one.
# No editions are printed: the page lists Climb25 and Climb26 together, so an edition list would leave some out.
HEADLINERS = [("Tracy Brabin", "wwt.speakers24", "west-yorkshire-combined-authority.jpg"), ("Jonnie Peacock", None, ""),
              ("Emily Cloke", None, "creative-uk.png"), ("Louis Taylor", None, "british-business-bank.png"),
              ("Erin Platts", None, "octopus-investments.png"), ("Jennifer Byrne", None, "microsoft.png"),
              ("Chloe Mayirou", None, "meta.png"), ("Spencer Hudson", None, "sky-sports.png"),
              ("Tanya Arnold", "wwt.speakers24", "bbc.png"), ("Jake Zim", None, "sony.png"),
              ("Hugo Heppell", None, "channel-4.png"), ("Simon McCoy", None, ""), ("Stephanie Millward", None, ""),
              ("Jamie Peacock", None, ""), ("Robbie Hunter Paul", None, ""), ("John Gleasure", None, "dazn.png")]
# Speakers the page lists by name only, with the title printed for them and a sticker naming their sport in place of
# a logo. Titles come from their public profiles, not from the page, so check one before adding it. Jonnie Peacock is
# not in the speaker lists; his Climb26 session title on the page names him ("Paralympic champion Jonnie Peacock").
TITLES = {"Jonnie Peacock": ("Paralympic champion sprinter", "Paralympian"),
          "Stephanie Millward": ("Paralympic champion swimmer", "Paralympian"),
          "Jamie Peacock": ("Former England and Leeds Rhinos captain", "Rugby league"),
          "Robbie Hunter Paul": ("Former Bradford Bulls captain and New Zealand international", "Rugby league")}
# Speakers from organisations people will know, grouped under the organisation (best known first) with its logo
# where we hold one. The heading is the organisation as the page names it; the role drops its trailing organisation.
KNOWN = [("NatWest Group", "natwest-group-plc.png", ["Neil Bellamy", "Rita Collins", "Darren Pirie", "Steve Sankson"]),
         ("Barclays", "barclays.png", ["Mark Northen", "Emma Walsh"]),
         ("Lloyds Banking Group", "lloyds-banking-group.png", ["Arun Aggarwal", "Claudine Reid"]),
         ("Santander UK", "santander-uk.png", ["Gautam Sehgal"]),
         ("Coutts", "coutts-company.png", ["Chris Dale"]),
         ("UBS", "ubs.png", ["Jane Bototh"]),
         ("PwC", "pwc.png", ["Robert Leishman"]),
         ("Walmart Marketplace", "walmart-marketplace.png", ["Jason Perry"]),
         ("Snowflake", "snowflake.png", ["Ian McAleese"]),
         ("Thomson Reuters", "", ["Nick Glicher"]),
         ("British Business Bank", "british-business-bank.png", ["Abs Bulbuliya"]),
         ("Innovate UK", "innovate-uk.png", ["Dean Cook"]),
         ("Department for Business and Trade", "", ["Jonathan Crook"]),
         ("Octopus Ventures", "octopus-investments.png", ["Jebran Raashed"]),
         ("Mercia Ventures", "mercia-asset-management.png", ["Chris Borrett"]),
         ("Northern Gritstone", "northern-gritstone.png", ["Andy Naylor"]),
         ("ScaleUp Institute", "", ["Irene Graham", "Josh Robson"]),
         ("Plexal", "plexal-group-limited.png", ["Jessica Moffatt-Owen"]),
         ("Freeths", "freeths.png", ["Malin Svanberg Larsson"]),
         ("Squire Patton Boggs", "squire-patton-boggs.png", ["Anna Roughley"]),
         ("High Value Manufacturing Catapult", "", ["Alfredo Ramos"]),
         ("Leeds University Business School", "leeds-university-business-school.png", ["Richard Tunstall"])]
# Logos for the sessions, by a substring of the title: every company the title names, where we hold its logo.
SESSION_LOGOS = {"Customer Acquisition with Meta": ["meta.png"],
                 "Scaleup Masterclass": ["barclays.png", "google.png", "plexal-group-limited.png"],
                 "Google AI Build Session": ["google.png", "nocodelab-ai.jpg"],
                 "From Prompt To Full Stack": ["lovable.png", "nocodelab-ai.jpg"],
                 "Scaling into the US for Consumer Brands": ["walmart-marketplace.png"],
                 "Insight to Action": ["walmart-marketplace.png", "infinity-blue-group.png"],
                 "TikTok Changed the Rules": ["tiktok.png"],
                 "LinkedIn ROI": ["linkedin.png"],
                 "Solve It in Bricks": ["lego.png"],
                 "Innovation Competition Winners": ["barclays.png"],
                 "Jonnie Peacock": ["natwest-group-plc.png"],
                 "John Gleasure": ["dazn.png"]}
# Climb23 sessions printed beside the Climb26 ones (a substring of the session's title on the page).
SESSIONS23 = ["John Gleasure"]
# Quotes about ClimbUK in general (Climb23 to Climb25, naming no edition): the source names, all their quotes.
GENERAL = ["Angus Young", "Jeff B. Cohen", "Mitchell McCombe", "Ash Wilks", "Tim Bennett", "Mandy Ridyard",
           "Barry McDonald", "Richard Paxman OBE", "Ian McAleese", "Eddy Davies", "Nina Hinton", "Jennifer Byrne",
           "Talitha Heaton", "Dan Boys", "Harry Baker", "Rachel Fowler",
           "Daniella Wainwright", "Serena Fordham", "Matt Wheeler", "Gary Crotaz"]
# Organisations that came to more than one edition, found by matching the page's lists for Climb23, Climb24 and
# Climb25 and Climb26 (the page lists those two together, so a return between them alone cannot show). Printed as
# the page names them; best known first. Each name is checked against the page when the file is written.
RETURNERS = {
    "three": ["British Business Bank", "Innovate UK", "West Yorkshire Combined Authority", "Leeds City Council",
              "Sure Valley Ventures", "Lifted Ventures", "EHE Ventures"],
    # Google, Meta and Microsoft: their return is on the owner's word (2026-10-16); the lists alone show one edition.
    "two": ["Google", "Meta", "Microsoft", "NatWest Group", "Barclays", "BBC", "Channel 4", "UBS", "Thomson Reuters", "Mishcon de Reya",
            "Lewis Silkin", "Northern Gritstone", "ScaleUp Institute", "Creative UK", "Plexal", "YFM Equity Partners",
            "Leeds University Business School", "University of Sheffield", "South Yorkshire Mayoral Combined Authority",
            "Health Innovation Yorkshire & Humber", "Blacks Solicitors", "Innovation SuperNetwork", "GSG",
            "Samos Investments", "RTC North", "River Capital", "Panintelligence", "Techbuyer", "XR Games",
            "Tech North Advocates", "Tech SY", "The Data Refinery", "The Tech Dept", "Leeds Community Foundation",
            "CREATICITY", "Genio", "Glean", "CRSI", "PinPoint Data Science", "IDS Group", "Clubit Group",
            "Red Line Foundry", "Mind Body Goals", "Strength in you", "Blossom Training", "Fourth Day", "Yaba",
            "ProspHER", "Writebusinessresults"],
}
EDITION = {"wwt.speakers": "Climb26", "wwt.speakers24": "Climb24", "wwt.speakers23": "Climb23"}

PACK = {
    "wwt.cover.headline": "[[Who]] was _there_",
    "wwt.cta.line1": "Join them at",
    "wwt.cta.line2": "Climb27",
    "wwt.cta.button": "Partner with ClimbUK",
    "wwt.cta.qr": "Scan to book a call",
    "wwt.names.headline": "In the room at _ClimbUK_",
    "wwt.back.eyebrow": "Returning partners and guests",
    "wwt.back.headline": "[[Names]] that keep coming _back_",
    "wwt.back.intro": "These organisations partnered with, exhibited at, spoke at or came along to more than one ClimbUK.",
    "wwt.back.three.title": "Back for three editions",
    "wwt.back.two.title": "Back for a second edition",
    "wwt.headliners.eyebrow": "Who spoke",
    "wwt.headliners.headline": "Speakers you'll _know_",
    "wwt.headliners.intro": "Leaders, broadcasters and champions who have spoken at ClimbUK since Climb23.",
    "wwt.known.eyebrow": "Who spoke",
    "wwt.known.headline": "From [[organisations]] you _know_",
    "wwt.known.intro": "Banks, funds, global tech companies and government, on stage at ClimbUK.",
    "wwt.sessionsall.eyebrow": "On stage",
    "wwt.sessionsall.headline": "Sessions with names _you know_",
    "wwt.sessionsall.intro": "A few of the ClimbUK sessions run with well-known companies, from Climb23 to Climb26.",
    "wwt.general.eyebrow": "In their words",
    "wwt.general.headline": "What people say about _ClimbUK_",
    "wwt.general.intro": "Speakers, exhibitors and guests on ClimbUK, quoted word for word.",
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


def picks(got, notes):
    """The pack's chosen sections, built from the page's own entries (see HEADLINERS and the lists after it)."""
    out = []

    def spoke(name):
        return [(k, r) for k in EDITION if k + ".items" in got for r in got[k + ".items"] if r[0] == name]

    def role_of(name, prefer=None):
        hits = spoke(name)
        assert hits, "%s is not a speaker on the page" % name
        role = next((r for k, r in hits if k == prefer), hits[0][1])[1:]
        return role[0] if role else ""

    def logo(f):
        assert not f or os.path.exists(os.path.join(LOGOS, f)), "%s is not in the logos folder" % f
        return f

    def without(role, org):
        """The role with the trailing organisation parts that repeat the heading dropped ("..., NatWest Group")."""
        key = org.split()[0].lower()
        parts = [x.strip() for x in role.split(",")]
        while parts and key in parts[-1].lower() and (len(parts) > 1 or parts[-1].lower().startswith(key)):
            parts.pop()
        return ", ".join(parts)

    listed = " | ".join(" | ".join(map(str, v)) for k, v in got.items() if isinstance(v, list)).lower()
    for key in ("wwt.headliners", "wwt.known"):
        for part in ("eyebrow", "headline", "intro"):
            out.append(("%s.%s" % (key, part), PACK["%s.%s" % (key, part)]))
    def headliner(n, p, f):
        if n in TITLES:
            assert n.lower() in listed, "%s is not on the page" % n
            return [n, TITLES[n][0], logo(f), TITLES[n][1]]
        return [n, role_of(n, p), logo(f), ""]
    out.append(("wwt.headliners.items", [headliner(*h) for h in HEADLINERS]))
    notes["wwt.headliners.items"] = ("name | role and organisation as the page gives it, or the public title in TITLES "
                                     "| logo file | sport sticker (blank where none)")
    rows = []
    for org, f, names in KNOWN:
        assert org.lower() in listed, "%s is not on the page" % org
        rows += [[org, logo(f), n, without(role_of(n), org)] for n in names]
    out.append(("wwt.known.items", rows))
    notes["wwt.known.items"] = ("organisation as the page names it | logo file | name | role as the page gives it, "
                                "without the organisation")
    for part in ("eyebrow", "headline", "intro"):
        out.append(("wwt.sessionsall." + part, PACK["wwt.sessionsall." + part]))

    def session_logos(title):
        hits = [v for k, v in SESSION_LOGOS.items() if k in title]
        return ", ".join(logo(f) for f in hits[0]) if hits else ""
    rows = [[s[0], session_logos(s[0]), "Climb26"] for s in got["wwt.sessions.items"]]
    for want in SESSIONS23:
        hit = [r[0] for r in got.get("wwt.sessions23.items", []) if want in r[0]]
        assert hit, "%s is not a Climb23 session on the page" % want
        rows.append([hit[0], session_logos(hit[0]), "Climb23"])
    out.append(("wwt.sessionsall.items", rows))
    notes["wwt.sessionsall.items"] = "session title | logo files of the companies it names, where we hold them | edition"
    for part in ("eyebrow", "headline", "intro"):
        out.append(("wwt.general." + part, PACK["wwt.general." + part]))
    said = [q for k in ("wwt.quotes25.items", "wwt.quotes24.items", "wwt.quotes23.items") for q in got.get(k, [])]
    rows = [q for g in GENERAL for q in said if q[1] == g]
    assert {q[1] for q in rows} == set(GENERAL), "a GENERAL source has no quote on the page"
    out.append(("wwt.general.items", rows))
    notes["wwt.general.items"] = "quote | name | role and organisation. Word for word from the website, [...] included."
    for part in ("eyebrow", "headline", "intro", "three.title", "two.title"):
        out.append(("wwt.back." + part, PACK["wwt.back." + part]))
    listed = " | ".join(" | ".join(map(str, v)) for k, v in got.items() if isinstance(v, list)).lower()
    for group, names in RETURNERS.items():
        for n in names:
            assert n.lower() in listed, "%s is not on the page" % n
        out.append(("wwt.back.%s.items" % group, [[n] for n in names]))
    notes["wwt.back.three.items"] = ("organisation, as the page names it, found in the page's lists for Climb23, Climb24 "
                                     "and Climb25 or Climb26")
    notes["wwt.back.two.items"] = ("organisation, as the page names it, found in the lists for two of those; Google, "
                                   "Meta and Microsoft on the owner's word")
    return out


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
        out.append((key + ".headline", headline or PACK.get(key + ".headline") or text(re.search(r"<h2[^>]*>(.*?)</h2>", body, re.S).group(1))))
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
    out += picks(dict(out), notes)
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
