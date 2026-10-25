"""Per-brand settings for the brand PDFs, and the reader for their words.

Every printed word lives in a copy file (*.copy.md), never in these scripts:
- pdf/guidelines/brand-guidelines.copy.md: the pages every brand book shares
- pdf/guidelines/<key>_brand-guidelines.copy.md: one brand's own pages and lines, read first
- pdf/one-page/<key>_key-rules.copy.md: one brand's key rules sheet
The standard is .agents/skills/climb-voice/references/copy-files.md.
"""
import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PDF, "..", ".agents", "skills", "climb-voice", "scripts"))
import copy_md  # noqa: E402

BRANDS = {
    "ClimbUK": dict(key="climbuk", ground="", cover_photo="climb_crowd_wide.jpg", cover_size=140),  # Dark Brown
    "ClimbGroup": dict(key="climbgroup", ground="ch", cover_photo="climb_recap_03.jpg"),  # Charcoal
    "Climb27": dict(key="climb27", ground="", cover_photo="joy_02.jpg", cover_size=140),
}

HIGHLIGHT = '<span class="o">%s</span>'


def md(text, hl=HIGHLIGHT, em="<em>%s</em>", em_hl='<em class="o">%s</em>', quotes=False):
    """Copy file marks to HTML: [[x]] the orange word, *x* italic, **x** bold, a hard line break a <br>.

    quotes=True turns straight double quotes into curly ones. Entities such as &pound; print as their character."""
    t = text
    if quotes:
        t = re.sub(r'"([^"]*)"', "\u201c\\1\u201d", t)
    t = re.sub(r"\*\[\[(.+?)\]\]\*", lambda m: em_hl % m.group(1), t)
    t = re.sub(r"\[\[(.+?)\]\]", lambda m: hl % m.group(1), t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"\*(.+?)\*", lambda m: em % m.group(1), t)
    return html.unescape(t.replace("\n", "<br>"))


class Words:
    """The words for one piece: its own copy file first, then any shared copy file behind it.

    A section found in the first file replaces every section of that name in the files behind it."""

    def __init__(self, *paths):
        self.docs = [copy_md.load(p) for p in paths]

    def secs(self, path):
        for d in self.docs:
            found = d.all(path)
            if found:
                return found
        raise copy_md.CopyError(self.docs[0].where, 1, "no '@%s' section in %s" % (path, " or ".join(d.where for d in self.docs)))

    def sec(self, path):
        found = self.secs(path)
        if len(found) != 1:
            raise copy_md.CopyError(self.docs[0].where, found[1].line, "expected one '@%s' section, found %d" % (path, len(found)))
        return found[0]

    def t(self, path, **kw):
        """One section's text as HTML."""
        s = self.sec(path)
        return md(s.text, quotes=s.get("quotes") == "curly", **kw)

    def title(self, path, **kw):
        return md(self.sec(path).title, **kw)

    def items(self, path, **kw):
        """A section that is a Markdown list, as a list of HTML items."""
        s = self.sec(path)
        return [md(re.sub(r"^\s*[-*+]\s+", "", line), quotes=s.get("quotes") == "curly", **kw) for line in s.text.split("\n")]

    def pairs(self, path, **kw):
        """Repeated sections with a title, as (title, text) pairs of HTML."""
        return [(md(s.title, **kw), md(s.text, quotes=s.get("quotes") == "curly", **kw)) for s in self.secs(path)]

    def lines(self, path):
        """Repeated sections with a title, as (title, [each line of the text]) in HTML."""
        return [(md(s.title), [md(x) for x in s.text.split("\n")]) for s in self.secs(path)]


def copy_path(*parts):
    return os.path.join(PDF, *parts)
