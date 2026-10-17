"""The words of the Excel templates, read from their copy files.

Each workbook's words live in its copy file beside it, one per brand: office/<Brand>/excel/<Brand>_<Name>.copy.md (or
office/<Brand>/external/). A section is named for the builder that writes the words and what they say, such as
form.bill-to or expense-claim.travel. Lines set once for every workbook (the status lists, the risk scales, the
drop-down messages) are in office/excel-shared.copy.md.

    use(path)   start a workbook: W reads its copy file first, then the shared one
    W(key)      the words of one section; a list section gives its items
"""
import copy_io

SHARED = "office/excel-shared.copy.md"
_current = None


def use(path):
    global _current
    _current = path


def _text(s):
    if s.text.lstrip().startswith("- "):
        return copy_io.items(s)
    return s.text


def W(key, literal=None):
    """The words for key: from the current workbook's copy file, else from the shared one."""
    for path in ([_current] if _current else []) + [SHARED]:
        s = copy_io.load(path).maybe(key)
        if s is not None:
            return _text(s)
    raise copy_io.CopyError(_current or SHARED, 1, "no '@%s' section for this workbook" % key)
