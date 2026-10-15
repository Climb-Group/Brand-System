"""Read the template copy files (*.copy.md) for the builders.

Every word a template prints lives in a copy file beside the template (the standard is
.agents/skills/climb-voice/references/copy-files.md). The builders keep only layout and logic and read the words through
these helpers:

    doc = copy_io.load("office/ClimbUK/word/ClimbUK_Memo.copy.md")   # a path from templates/, or absolute
    copy_io.rich(doc.one("cover.title").text)    # [[word]] -> {word} and *word* -> _word_, the builders' rich text
    copy_io.html(text)                           # the same marks as spans with the o and i classes, for the HTML art
    copy_io.items(section)                       # the list items of a section, without their markers
    copy_io.table(doc, section)                  # the pipe table of a section: [[cell, ..], ..] (header row first)

In a copy file [[word]] is the highlight (Climb Orange) and *word* is italic. {Field} is a value the build or a mail
merge fills in, such as {brand} or a merge field.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.dirname(HERE)
REPO = os.path.dirname(TEMPLATES)
sys.path.insert(0, os.path.join(REPO, ".agents", "skills", "climb-voice", "scripts"))
import copy_md  # noqa: E402

CopyError = copy_md.CopyError
_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
_HIGHLIGHT = re.compile(r"\[\[((?:\[[^\]]*\]|[^\[\]])+)\]\]")
_ITALIC = re.compile(r"\*([^*]+)\*")
_CACHE = {}


def path(*parts):
    """A path under templates/."""
    return os.path.join(TEMPLATES, *parts)


def load(p):
    """A parsed copy file (cached). Relative paths are from templates/."""
    full = p if os.path.isabs(p) else path(p)
    if full not in _CACHE:
        _CACHE[full] = copy_md.load(full)
    return _CACHE[full]


def rich(text):
    """Copy file marks to the builders' rich text: [[word]] is {word} (orange), *word* is _word_ (italic)."""
    if text is None:
        return None
    return _ITALIC.sub(r"_\1_", _HIGHLIGHT.sub(r"{\1}", text))


def html(text):
    """Copy file marks to the HTML the video and image builds draw: [[word]] and *word* as spans with the o and i
    classes, a hard line break as <br>."""
    if text is None:
        return None
    text = _HIGHLIGHT.sub(r"<span class='o'>\1</span>", text)
    return _ITALIC.sub(r"<span class='i'>\1</span>", text).replace("\n", "<br>")


def items(section):
    """The list items of a section, in order, without their '- ' or '1. ' markers."""
    if not section.text:
        return []
    return [_ITEM.sub("", line, count=1) for line in section.text.split("\n")]


def raw_lines(doc, section):
    """The lines of a section as written in the file (for tables, which the parser joins into one line)."""
    with open(doc.where, encoding="utf-8") as f:
        lines = f.read().split("\n")
    out = []
    for line in lines[section.line:]:
        s = line.strip()
        if s.startswith("<!--") or re.match(r"^#{1,2}\s", s):
            break
        out.append(line)
    return out


def _cells(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", s)]


def table(doc, section):
    """The pipe table of a section as rows of cells, header row first; the '| --- |' rule line is dropped."""
    rows = []
    for line in raw_lines(doc, section):
        if not line.strip().startswith("|"):
            continue
        cells = _cells(line)
        if all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
            continue
        rows.append(cells)
    return rows


def floats(value):
    """A comma list setting such as widths=10.0,6.6, as floats."""
    return [float(x) for x in value.split(",")] if value else None


def fill(text, **values):
    """Fill the {name} slots the build owns, such as {brand}."""
    for k, v in values.items():
        text = text.replace("{%s}" % k, v)
    return text
