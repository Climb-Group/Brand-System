"""Every word on the filming and photo release, read from release.copy.md beside this file.

Change the words in release.copy.md, then rebuild. This module only gives them the names build.py uses.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".agents", "skills", "climb-voice", "scripts"))
import copy_md  # noqa: E402

DOC = copy_md.load(os.path.join(HERE, "release.copy.md"))


def w(key):
    """The text of one section."""
    return DOC.one(key).text


def items(key):
    """The list items of one section."""
    return [re.sub(r"^- ", "", line) for line in w(key).split("\n")]


def headline(text):
    """[[word]] is orange and *word* italic: [(text, None | "italic" | "orange"), ...]."""
    out = []
    for m in re.finditer(r"\[\[([^\]]+)\]\]|\*([^*]+)\*|([^*\[]+)", text):
        orange, italic, plain = m.groups()
        out.append((orange, "orange") if orange else (italic, "italic") if italic else (plain, None))
    return out


VERSION = w("version")

EYEBROW = w("page-1.eyebrow")
HEADLINE = headline(w("page-1.headline"))
INTRO = w("page-1.intro")

SUMMARY_TITLE = w("summary.title")
SUMMARY = items("summary")

DETAILS_TITLE = w("details.title")
HANDLES_TITLE = w("handles.title")
HANDLES_NOTE = w("handles.note")
TAG_CONSENT = w("tag-consent")

CHOICES_TITLE = w("choices.title")
CHOICES_NOTE = w("choices.note")
NEWSLETTER = w("newsletter")
AFFILIATE = w("affiliate")
VIDEO_FREE = w("video.free")
VIDEO_PAID = w("video.paid")  # followed by a price box
VIDEO_PAID_AFTER = w("video.paid-after")
COPY_NOTE = w("copy-note")

RELEASE_TITLE = w("release.title")
CLAUSES = [(s.title, s.text) for s in DOC.all("clause")]

SIGN_TITLE = w("sign.title")
SIGN_LEAD = w("sign.lead")
GUARDIAN_TITLE = w("guardian.title")
TEAM_LABEL = w("team.label")

FOOTER = w("footer").replace("{version}", VERSION)

VIDEO_CLAUSE_FREE = w("video.clause-free")
VIDEO_CLAUSE_PAID = w("video.clause-paid")

# Field labels, hints and tooltips.
REQUIRED = w("field.required")
OPTIONAL = w("field.optional")
FULL_NAME = w("details.full-name")
EMAIL = w("details.email")
PHONE = w("details.phone")
EVENT = w("details.event")
EVENT_TOOLTIP = w("details.event-tooltip")
ALL_OPTIONAL = w("handles.all-optional")
HANDLES = [(s["key"], s.title, s.text) for s in DOC.all("handle")]  # (field key, label, hint)
HANDLE_TOOLTIP = w("handle.tooltip")  # {label} {hint}
CURRENCY = w("video.currency")
FEE_TOOLTIP = w("video.fee-tooltip")
NEXT = w("page-1.next")
SIGNATURE = w("sign.signature")
PRINT_NAME = w("sign.print-name")
DATE = w("sign.date")
DATE_HINT = w("sign.date-hint")
DATE_TOOLTIP = w("sign.date-tooltip")
GUARDIAN_SIGNATURE = w("sign.guardian-tooltip")
TEAM_HINT = w("team.hint")
PAGE = w("footer.page")  # {page}

# Document properties.
META_TITLE = w("meta.title")
META_AUTHOR = w("meta.author")
META_SUBJECT = w("meta.subject")
META_CREATOR = w("meta.creator")

# The words of release-text.md that are not on the form.
TEXT_TITLE = w("text-file.title")
TEXT_LEAD = w("text-file.lead")
TEXT_PAGE_1 = w("text-file.page-1")
TEXT_PAGE_2 = w("text-file.page-2")
TEXT_FREE = w("text-file.free")
TEXT_PAID = w("text-file.paid")
TEXT_AMOUNT = w("text-file.amount")
TEXT_PAID_INSTEAD = w("text-file.paid-instead")
