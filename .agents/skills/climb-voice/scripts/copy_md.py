"""Read, check and extract ClimbUK copy files (*.copy.md).

A copy file holds every word of one deliverable (a flyer, a PDF, a banner, a template) as plain
Markdown, so people can review and edit the words without touching the design. Design sections
are marked with one-line HTML comments, which Markdown viewers hide:

    <!-- @front.headline -->
    Scale with the [[right people]] in the *room*.

    <!-- @reason icon=people -->
    ### Find your people
    Fellow founders one step ahead.

The full standard is in references/copy-files.md next to this script.

Usage:
    python3 copy_md.py words FILE    # print only the words, as a reader sees them
    python3 copy_md.py json FILE     # print the parsed sections as JSON, for scripts
    python3 copy_md.py coverage [ROOT]   # list every deliverable that no copy file covers
    python3 check_copy.py FILE       # check a copy file: its markers, then its words against the copy rules

Exit code 1 when a file breaks the standard. Standard library only.
"""
import json
import re
import sys
from pathlib import Path

ID = r"[a-z0-9]+(?:-[a-z0-9]+)*"
PATH = ID + r"(?:\." + ID + r")*"
MARKER = re.compile(r"^<!--\s*@(?P<path>\S+)(?P<settings>.*?)\s*-->\s*$")
SETTING = re.compile(r'\s+(?P<key>[a-z0-9]+(?:-[a-z0-9]+)*)=(?:"(?P<quoted>[^"]*)"|(?P<bare>[^\s"]+))')
COMMENT = re.compile(r"<!--.*?-->", re.S)
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
FRONT_KEY = re.compile(r"^(?P<key>[a-z0-9]+(?:-[a-z0-9]+)*):\s*(?P<value>.*?)\s*$")
REQUIRED = ("copy", "deliverable")


class CopyError(ValueError):
    """A copy file that breaks the standard. Carries the file and line."""

    def __init__(self, where, line, message):
        super().__init__("%s:%d: %s" % (where, line, message))
        self.line = line


class Section:
    """One marked design section: its path, its settings and its words."""

    def __init__(self, path, settings, line):
        self.path = path
        self.settings = settings
        self.line = line
        self.title = None
        self.text = ""

    def __getitem__(self, key):
        return self.settings[key]

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def as_dict(self):
        return dict(path=self.path, settings=self.settings, title=self.title, text=self.text, line=self.line)

    def __repr__(self):
        return "Section(%r, %r, title=%r, text=%r)" % (self.path, self.settings, self.title, self.text)


class CopyDoc:
    """A parsed copy file: front matter in meta, sections in file order, reviewer notes."""

    def __init__(self, where, meta, sections, notes):
        self.where = where
        self.meta = meta
        self.sections = sections
        self.notes = notes

    def all(self, path):
        return [s for s in self.sections if s.path == path]

    def one(self, path):
        found = self.all(path)
        if len(found) != 1:
            line = found[1].line if found else 1
            raise CopyError(self.where, line, "expected one '@%s' section, found %d" % (path, len(found)))
        return found[0]

    def maybe(self, path):
        found = self.all(path)
        if len(found) > 1:
            raise CopyError(self.where, found[1].line, "expected at most one '@%s' section, found %d" % (path, len(found)))
        return found[0] if found else None

    def words(self, path, default=None):
        """The text of a section, or default when the file has no such section."""
        s = self.maybe(path)
        return default if s is None else s.text

    def as_dict(self):
        return dict(meta=self.meta, sections=[s.as_dict() for s in self.sections], notes=self.notes)


def _front_matter(where, lines):
    """Return (meta, index of the first body line). Front matter is 'key: value' lines between '---'."""
    if not lines or lines[0].strip() != "---":
        raise CopyError(where, 1, "a copy file starts with front matter: '---', then 'copy:' and 'deliverable:' lines, then '---'")
    meta = {}
    for i in range(1, len(lines)):
        line = lines[i]
        if line.strip() == "---":
            for key in REQUIRED:
                if not meta.get(key):
                    raise CopyError(where, 1, "front matter needs '%s:'" % key)
            if not re.fullmatch(ID, meta["copy"]):
                raise CopyError(where, 2, "'copy:' is a lowercase id with hyphens, such as climb27-flyer-investors")
            return meta, i + 1
        if not line.strip():
            continue
        m = FRONT_KEY.match(line)
        if not m:
            raise CopyError(where, i + 1, "front matter lines are 'key: value' with a lowercase key")
        if m["key"] in meta:
            raise CopyError(where, i + 1, "'%s' is set twice" % m["key"])
        meta[m["key"]] = m["value"]
    raise CopyError(where, 1, "front matter is not closed with '---'")


def _settings(where, line_no, raw):
    settings, pos = {}, 0
    for m in SETTING.finditer(raw):
        if m.start() != pos:
            break
        if m["key"] in settings:
            raise CopyError(where, line_no, "setting '%s' is given twice" % m["key"])
        settings[m["key"]] = m["quoted"] if m["quoted"] is not None else m["bare"]
        pos = m.end()
    if raw[pos:].strip():
        raise CopyError(where, line_no, "cannot read settings '%s': write key=value or key=\"two words\"" % raw[pos:].strip())
    return settings


def _join(lines):
    """Markdown paragraphs, joined with a blank line between them.

    Soft-wrapped lines join with a space. A line ending in a backslash (or two spaces) is a hard
    line break and keeps its newline, and list items keep their own lines."""
    paragraphs, current = [], None
    for line in lines + [""]:
        if not line.strip():
            if current is not None:
                paragraphs.append(current)
                current = None
            continue
        hard = line.endswith("\\") or line.endswith("  ")
        piece = line.rstrip()[:-1].rstrip() if line.rstrip().endswith("\\") else line.strip()
        if LIST_ITEM.match(line):
            piece = line.rstrip()
        if current is None:
            current = piece
        elif current.endswith("\n"):
            current += piece
        elif LIST_ITEM.match(line):
            current += "\n" + piece
        else:
            current += " " + piece
        if hard:
            current += "\n"
    return "\n\n".join(p.rstrip("\n") for p in paragraphs)


def _finish(section, lines):
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines:
        h = HEADING.match(lines[0])
        if h and len(h.group(1)) >= 3:
            section.title = h.group(2)
            lines = lines[1:]
    section.text = _join(lines)


def parse(text, where="<copy>"):
    """Parse the text of a copy file. Raises CopyError when it breaks the standard."""
    lines = text.splitlines()
    meta, start = _front_matter(where, lines)
    sections, notes = [], []
    current, body = None, []
    i = start
    while i < len(lines):
        line, line_no = lines[i], i + 1
        stripped = line.strip()
        if stripped.startswith("<!--"):
            m = MARKER.match(stripped)
            if m:
                if not re.fullmatch(PATH, m["path"]):
                    raise CopyError(where, line_no, "section name '%s': lowercase words with hyphens, dots between levels, such as front.headline" % m["path"])
                if current is not None:
                    _finish(current, body)
                current, body = Section(m["path"], _settings(where, line_no, m["settings"]), line_no), []
                sections.append(current)
                i += 1
                continue
            if stripped.startswith("<!--@") or stripped.startswith("<!-- @"):
                raise CopyError(where, line_no, "a section marker sits on its own line: <!-- @name key=value -->")
            # Any other comment is a note for reviewers, and may run over several lines.
            end = i
            while "-->" not in lines[end]:
                end += 1
                if end == len(lines):
                    raise CopyError(where, line_no, "comment is not closed with '-->'")
            note = "\n".join(lines[i:end + 1]).strip()[4:-3].strip()
            notes.append(dict(line=line_no, text=re.sub(r"^note:\s*", "", note)))
            i = end + 1
            continue
        if "<!--" in line:
            raise CopyError(where, line_no, "put comments and markers on their own line")
        h = HEADING.match(line)
        if h and len(h.group(1)) <= 2:
            # Page and part headings are for people reading the file; they end the open section.
            if current is not None:
                _finish(current, body)
            current, body = None, []
        elif current is not None:
            body.append(line)
        elif stripped and not h:
            raise CopyError(where, line_no, "words outside a section: start the section with a marker such as <!-- @intro -->")
        i += 1
    if current is not None:
        _finish(current, body)
    return CopyDoc(where, meta, sections, notes)


def load(path):
    path = Path(path)
    return parse(path.read_text(encoding="utf-8"), str(path))


# Files a person reads, prints or opens in an editor: each one needs a copy file that covers it.
DELIVERABLE = {".pdf", ".svg", ".png", ".jpg", ".jpeg", ".webp", ".ico", ".gif", ".tif", ".tiff",
               ".docx", ".dotx", ".dotm", ".odt", ".ott", ".xlsx", ".xltx", ".xltm", ".ods", ".ots",
               ".pptx", ".potx", ".potm", ".odp", ".otp", ".thmx", ".drfx", ".html", ".mp4", ".mov", ".srt", ".cube"}
# Folders that hold sources, tooling or build output rather than deliverables.
NOT_DELIVERED = {"_build", "tests", "node_modules", "graphify-out", "tools", "build"}


def covered(doc, root):
    """The files a copy file covers: its 'output' paths (from the pack root) and its 'files' globs (from its own folder).

    'output' holds one or more paths or globs separated by spaces: the finished file and its editable source, such
    as a PDF and its layered SVGs. A copy file covers every file that carries the same words: a template in each of
    its formats, a logo on each ground, an image at each size. Raises CopyError when a path or glob finds nothing."""
    root, here = Path(root), Path(doc.where).parent
    found = []
    for pattern in doc.meta.get("output", "").split():
        matches = sorted(p for p in root.glob(pattern) if p.is_file())
        if not matches:
            raise CopyError(doc.where, 1, "'output:' %s does not exist" % pattern)
        found += matches
    for pattern in doc.meta.get("files", "").split():
        matches = sorted(p for p in here.glob(pattern) if p.is_file())
        if not matches:
            raise CopyError(doc.where, 1, "'files:' pattern %s matches no file" % pattern)
        found += matches
    return [p.resolve() for p in found]


def deliverables(paths, root):
    """The paths, from a list relative to root, that are deliverables and so need a copy file."""
    out = []
    for p in paths:
        parts = Path(p).parts
        if Path(p).suffix.lower() not in DELIVERABLE or any(x.startswith(".") or x in NOT_DELIVERED for x in parts[:-1]):
            continue
        out.append((Path(root) / p).resolve())
    return out


def coverage(root, tracked):
    """(uncovered deliverables, problems) for a pack whose files, relative to root, are tracked."""
    problems, have = [], set()
    for p in tracked:
        if p.endswith(".copy.md"):
            try:
                have.update(covered(load(Path(root) / p), root))
            except CopyError as e:
                problems.append(str(e))
    return [d for d in deliverables(tracked, root) if d not in have], problems


def words_only(text):
    """The text with front matter and comments blanked out, keeping every line and column in place.

    check_copy.py runs on this, so its line numbers still point into the copy file."""
    lines = text.split("\n")
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            done = lines[i].strip() == "---"
            lines[i] = ""
            if done:
                break
        lines[0] = ""
    text = "\n".join(lines)
    return COMMENT.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


def plain(text):
    """Words as a reader sees them: highlight brackets and emphasis stars removed."""
    return re.sub(r"\*{1,2}(.+?)\*{1,2}", r"\1", text.replace("[[", "").replace("]]", ""))


def reader_words(doc):
    out = []
    for s in doc.sections:
        out += [plain(t) for t in (s.title, s.text) if t]
    return "\n".join(out)


def _tracked(root):
    import subprocess
    out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=root,
                         capture_output=True, text=True, check=True).stdout
    return out.split("\n")[:-1]


def main(argv):
    if argv[:1] == ["coverage"]:
        root = Path(argv[1] if len(argv) > 1 else ".").resolve()
        missing, problems = coverage(root, _tracked(root))
        for p in problems:
            print(p)
        for m in missing:
            print("%s: no copy file covers it" % m.relative_to(root))
        print("[copy-md] %d file%s without a copy file" % (len(missing), "" if len(missing) == 1 else "s"))
        return 1 if missing or problems else 0
    if len(argv) != 2 or argv[0] not in ("words", "json"):
        print(__doc__)
        return 2
    cmd, path = argv
    try:
        doc = load(path)
    except CopyError as e:
        print(e)
        return 1
    print(reader_words(doc) if cmd == "words" else json.dumps(doc.as_dict(), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
