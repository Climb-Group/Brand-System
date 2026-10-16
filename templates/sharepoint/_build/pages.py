"""The SharePoint brand centre: every page, its sections and its copy. One source for the script, the guide and the
copy check. Text is HTML for the SharePoint text web part (h2, h3, p, ul, a, strong only).

{SITE} is the site address, {A} and {B} the two marketing content sites, {P} the brand pack download.

The words live in the copy files in templates/sharepoint/pages/: one per page (its title, description, text sections,
hero tiles and quick links) and menu.copy.md (the top menu). This module reads them into PAGES and NAV.
"""
import html
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
COPY = HERE.parent / "pages"
sys.path.insert(0, str(REPO / ".agents" / "skills" / "climb-voice" / "scripts"))
import copy_md  # noqa: E402





def link(href, text):
    return '<a href="%s">%s</a>' % (href, text)


def inline(text):
    """Copy file marks to the text web part's HTML: **bold** and [words](address)."""
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: link(m.group(2), m.group(1)), text)


def column(sec):
    """One column of a text section as HTML: its heading, then paragraphs, lists and #### subheadings."""
    out = ""
    if sec.title:
        tag = sec.get("heading", "h2")
        out += "<%s>%s</%s>" % (tag, inline(sec.title), tag)
    for block in (sec.text or "").split("\n\n"):
        lines = block.split("\n")
        if block.startswith("#### "):
            out += "<h3>%s</h3>" % inline(block[5:])
        elif all(line.startswith("- ") for line in lines):
            out += "<ul>%s</ul>" % "".join("<li>%s</li>" % inline(line[2:]) for line in lines)
        elif block:
            out += "<p>%s</p>" % inline(block)
    return out


PAGES = {}


def page(slug, title, description, sections, tiles=None, hero=None):
    PAGES[slug] = {"slug": slug, "title": title, "description": description, "sections": sections,
                   "tiles": tiles or [], "hero": hero}


# A section: (layout, emphasis, [column html, ...]). layout: OneColumn, TwoColumn, ThreeColumn.
# emphasis: 0 none, 1 neutral, 2 soft, 3 strong (strong takes the theme's dark ground).

def load(path):
    doc = copy_md.load(str(path))
    sections = []
    for sec in doc.sections:
        if sec.path == "section":
            sections.append((sec["layout"], int(sec["emphasis"]), []))
        elif sec.path == "section.column":
            sections[-1][2].append(column(sec))
    hero = [(h.title, h["page"], h.text) for h in doc.all("hero")] or None
    tiles = doc.maybe("quick-links")
    page(path.name[:-len(".copy.md")], doc.one("page.title").text, doc.one("page.description").text, sections,
         tiles=tiles["pages"].split() if tiles else None, hero=hero)


for _path in sorted((p for p in COPY.glob("*.copy.md") if p.name != "menu.copy.md"),
                    key=lambda p: int(copy_md.load(str(p)).meta["order"])):
    load(_path)

MENU = copy_md.load(str(COPY / "menu.copy.md"))
# (menu label, [page slugs]) ; a group with one page links straight to it
NAV = [(g.title, g["pages"].split()) for g in MENU.all("menu.group")]


def nav_label(slug):
    return PAGES[slug]["title"] if slug != "home" else MENU.one("menu.home").text
