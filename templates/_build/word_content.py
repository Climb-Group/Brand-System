"""The content of every Word template added after the first set, read from its copy file for word_build.py to lay out.

Each template's words live in one copy file beside it, one per brand: office/<Brand>/word/<Brand>_<Name>.copy.md (or
office/<Brand>/external/ for a co-branded version). The lines every document shares (the contents hint, the clause and
signature furniture) are in office/word-shared.copy.md. This module keeps only the layout choices:

DOCS maps the catalogue name to its kind:
    "plain" (standard header on every page), "cover" (Dark Brown photo cover, then inner pages),
    "landscape" (A4 landscape, used by the certificates) or "landscape-plain"

A copy file has a header.label section (the running header; plain kinds) or the cover.label, cover.title, cover.sub
and cover.meta sections (cover kind), then the body sections in order. Each body section is one block for the
renderer, named body.<block>:

    eyebrow  title  sub  lead  h1  h2  h3  p  callout  small  sigline     one text (a line break in p is a new paragraph)
    bullets  numbers  checklist  sign                                     list items
    kv                                                                    list items "Key: value"
    clauses start=N                                                       list items "N. Heading: what goes here"
    table widths=a,b,..                                                   a pipe table, header row first
    quote, then quote.source                                              the quote and who said it
    big                                                                   ### the number, then the line under it
    cert fields=F1,F2, then cert.after and cert.signer                    a certificate page; {Field} is a merge field
    page  toc                                                             a page break, the contents page

Copy follows the climb-voice skill and passes check_copy.py (python3 word_build.py --copy prints it all).
No venue, no names, no numbers as promises: every fact a person must fill in is a [slot].
"""
import copy_io as C
import catalog as K

DOCS = {
    "Memo": "plain", "Contract": "plain", "Partnership-agreement": "plain", "Award-sponsorship-agreement": "plain",
    "Exhibitor-agreement": "plain", "Non-disclosure-agreement": "plain", "Statement-of-work": "plain",
    "Business-plan": "cover", "Policy": "plain", "Standard-operating-procedure": "plain", "Job-description": "plain",
    "Offer-letter": "plain", "Employee-handbook": "cover", "Brief": "plain", "Case-study": "plain", "Fact-sheet": "plain",
    "Newsletter": "plain", "Certificate": "landscape", "Board-report": "cover", "Terms-and-conditions": "plain",
    "Post-event-report": "cover", "Exhibitor-manual": "cover", "Speaker-brief": "plain", "Host-brief": "plain",
    "Event-risk-assessment": "cover", "Event-day-pack": "cover", "Attendance-certificate": "landscape",
    "Exhibitor-risk-assessment": "landscape-plain",
}

SHARED = "office/word-shared.copy.md"


def shared(path):
    """A line every Word template shares, from office/word-shared.copy.md."""
    return C.load(SHARED).one(path).text


def copy_path(b, row):
    return C.path(K.copy_file(b, row))


def copy_doc(b, row):
    return C.load(copy_path(b, row))


def cover(b, row):
    """The cover lines: label, title, sub and meta."""
    doc = copy_doc(b, row)
    return {k: C.rich(doc.one("cover." + k).text) for k in ("label", "title", "sub", "meta")}


def label(b, row):
    """The running header label, or None for the brand URL."""
    doc = copy_doc(b, row)
    s = doc.maybe("header.label") or doc.maybe("cover.label")
    return C.rich(s.text) if s else None


def _kv(line):
    k, _, v = line.partition(": ")
    return (C.rich(k), C.rich(v))


def blocks(b, row):
    """The block list for the renderer, in the order of the copy file."""
    doc = copy_doc(b, row)
    out = []
    secs = [s for s in doc.sections if s.path.startswith("body.")]
    for s in secs:
        kind = s.path[len("body."):]
        if kind in ("eyebrow", "title", "sub", "lead", "h1", "h2", "h3", "callout", "small", "sigline", "p"):
            out.append((kind, C.rich(s.text)))
        elif kind in ("bullets", "numbers", "checklist"):
            out.append((kind, [C.rich(t) for t in C.items(s)]))
        elif kind == "sign":
            out.append((kind, C.items(s)))
        elif kind == "kv":
            out.append((kind, [_kv(t) for t in C.items(s)]))
        elif kind == "clauses":
            out.append((kind, [_kv(t) for t in C.items(s)], int(s.get("start", 1))))
        elif kind == "table":
            rows = [[C.rich(c) for c in r] for r in C.table(doc, s)]
            widths = C.floats(s.get("widths"))
            out.append(("table", rows[0], rows[1:], widths) if widths else ("table", rows[0], rows[1:]))
        elif kind == "quote":
            out.append(["quote", C.rich(s.text)])
        elif kind == "quote.source":
            out[-1] = tuple(out[-1] + [C.rich(s.text)])
        elif kind == "big":
            out.append(("big", C.rich(s.title), C.rich(s.text)))
        elif kind == "cert":
            fields = [(f, f.replace("_", " ")) for f in s["fields"].split(",")]
            out.append(["cert", C.rich(s.title), C.rich(s.text), None, fields, None])
        elif kind == "cert.after":
            out[-1][3] = s.text.replace("{", "«").replace("}", "»")
        elif kind == "cert.signer":
            out[-1][5] = C.rich(s.text)
            out[-1] = tuple(out[-1])
        elif kind in ("page", "toc"):
            out.append((kind,))
        else:
            raise C.CopyError(doc.where, s.line, "unknown Word block '@%s'" % s.path)
    return out


def all_copy(brands=("ClimbUK", "ClimbGroup", "Climb27"), original=False):
    """Every string a reader sees, for the copy checker (the first set too, with original=True)."""
    import copy_md
    out = [copy_md.reader_words(C.load(SHARED))]
    for b in brands:
        for row in K.rows("word", b, original=None if original else False):
            out.append(copy_md.reader_words(copy_doc(b, row)))
    return out
