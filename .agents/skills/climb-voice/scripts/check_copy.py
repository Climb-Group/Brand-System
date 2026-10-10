"""Check ClimbUK copy against the brand's hard rules.

Usage:
    python3 check_copy.py FILE [FILE ...]
    python3 check_copy.py --announced FILE     # after the Climb27 venue announcement
    python3 check_copy.py --no-hints FILE      # hard rules only, no reading level or abbreviation hints
    echo "text" | python3 check_copy.py -

Exit code 1 when a rule is broken (hard rules and vague link text). Reading level and
abbreviation lines are hints: they print as "hint" and do not change the exit code.
Tone is not checked: read the climb-voice skill for that.
The ban list mirrors docs/climb27-for-pages/deploy/lint_copy.py; keep both in step.
"""
import re
import sys

# (pattern, reason). Patterns run case-insensitively on the text.
ALWAYS = [
    (r"[\u2013\u2014]", "em or en dash: use a hyphen-minus, a comma or a full stop"),
    (r"!", "exclamation mark"),
    (r"[\U0001F300-\U0001FAFF\u2600-\u27BF]", "emoji"),
    (r"[\u2122\u00AE]", "trademark symbol"),
    (r"(?<![.\w-])climb(?![-.\w])", "'Climb' on its own: write Climb27, ClimbUK, ClimbGroup or ClimbAwards"),
    (r"\bclimb app\b", "the app is the ClimbGroup Event App"),
    (r"\bthousands\b", "attendance claim"),
    (r"\b\d+\s*(\+\s*)?(meetings|investors|partners|attendees|delegates)\b", "a number of meetings, investors, partners or attendees"),
    (r"\bpremier\b|\bbiggest\b|\blargest\b|\bthe best\b|bigger than ever", "unsupported superlative or size claim"),
    (r"sold\s*out|last\s+few|selling fast|limited spaces", "scarcity claim"),
    (r"guarantee", "no guarantees"),
    (r"(access|introductions?) to (top |leading )?investors|investor access", "investor-access promise"),
    (r"to be confirmed|\btbc\b|being finalised|being confirmed|coming soon|subject to|we hope", "hedge wording: state what happens"),
    (r"we never|we do not promise", "defensive wording: say what ClimbUK does and stop"),
    (r"\bplaceholder\b|\blorem\b|\bdraft\b", "status label leaked into copy"),
    (r"run by climbgroup|climbgroup runs|runs climbuk|organisation (that runs|behind) climbuk", "company structure line: say what the reader gets instead"),
    (r"\bodoo\b|\bcanva\b|\bcvent\b|\bstripe\b|\bhubspot\b", "vendor name in customer-facing copy"),
    (r"\bclinic(?!ian)", "clinics are roundtables or workshops"),
    (r"keynote", "big moments, not keynotes: name the format instead"),
    # Sales and partner review of the Climb27 pages, October 2026.
    (r"eyes open", "reads as a warning: 'Find investors looking for real deal flow'"),
    (r"\bin (their|your|our) patch\b", "slang: say 'across their region' or name the place"),
    (r"cheque\s?books?", "jargon: say what investors want, deal flow"),
    (r"seat on the stage", "investors come to meet companies; do not offer them the stage"),
    (r"budget to solve it", "not needed: drop the budget line"),
    (r"\bat least three\b", "say 'follow-ups that matter', not 'at least three'"),
    (r"referral (scheme|programme|program)|doubling down on referrals", "it is the affiliate programme"),
    (r"\bmeet (the )?investors\b|ready to invest", "reads as a promised meeting: 'Find investors looking for real deal flow', 'Investors here to find their next deal'"),
    (r"\b(un)?matched\b", "say 'brought to you' or 'connect'; never 'matched' or 'unmatched'"),
    (r"about \d+\s*% of tickets", "do not quote a release's share of tickets: name its state"),
]

# Case-sensitive rules.
CASED = [
    (r"\b[Pp]artner manager\b", "job title: Partner Manager"),
]

# Preferred words. Printed as hints, because each has legitimate uses elsewhere.
WORD_HINTS = [
    (r"\bprogramme\b", "for the event schedule write 'agenda'; 'programme' is for the affiliate programme and accelerator programmes"),
    (r"\bcouncils\b", "on pages and menus write 'public sector'"),
    (r"\bintroduc(e|es|ed|ing|tion|tions)\b", "prefer 'connect you with': we do not promise personal introductions"),
    (r"\bconsultants?\b", "if they take responsibility for a function, they are fractional leaders, not consultants"),
]

BEFORE_ANNOUNCEMENT = [
    (r"somewhere\s+new", "venue hint is banned"),
    (r"\bvenue\b", "no venue mention before the announcement"),
]

# Rules that name embargoed or confidential things (the venue, internal targets, legal matters) are kept
# out of this public repository. Put them in private_rules.py next to this script (git-ignored), or point
# CLIMB_PRIVATE_RULES at a file, defining PRIVATE_ALWAYS and PRIVATE_BEFORE_ANNOUNCEMENT as lists of
# (pattern, reason). The checker adds them when the file is there.
def _load_private():
    import importlib.util
    import os
    path = os.environ.get("CLIMB_PRIVATE_RULES") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "private_rules.py")
    if not os.path.isfile(path):
        return
    spec = importlib.util.spec_from_file_location("climb_private_rules", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    ALWAYS.extend(getattr(mod, "PRIVATE_ALWAYS", []))
    BEFORE_ANNOUNCEMENT.extend(getattr(mod, "PRIVATE_BEFORE_ANNOUNCEMENT", []))


_load_private()

# Vague link text (WCAG 2.4.9 Link Purpose). A link says where it goes: "See the Climb27 lineup".
# A phrase in straight or curly double quotes is treated as a quoted example (as in a style guide)
# and skipped.
VAGUE_LINK_WHY = "vague link text: say where the link goes (for example 'See the Climb27 lineup')"
VAGUE_PHRASES = r"\b(click here|read more|learn more|find out more|more info(rmation)?)\b"
# "here" alone is only a problem as the whole link text: markdown [here](...) or HTML <a ...>here</a>.
VAGUE_HERE = r"\[\s*(here|this|this link|link)\s*\]\(|<a\b[^>]*>\s*(here|this|this link|link)\s*</a>"

# All-caps tokens a reader already knows, or that are spelled out in the brand book.
ABBREVIATION_ALLOWLIST = {
    "UK", "CPD", "AI", "VIP", "SME", "SMEs", "QR", "DJ", "CEO", "PR", "AV", "B2B", "FAQ", "OK",
    "TV", "PDF", "URL", "WCAG", "AA", "AAA",
}
READING_GRADE_LIMIT = 9
READING_MIN_WORDS = 80


def _quoted(text, start, end):
    before = text[start - 1] if start > 0 else ""
    after = text[end] if end < len(text) else ""
    return before in "\"\u201c" and after in "\"\u201d"


def _problem(text, m, why):
    start = text.rfind("\n", 0, m.start()) + 1
    line_no = text.count("\n", 0, m.start()) + 1
    col = m.start() - start + 1
    snippet = text[max(0, m.start() - 30):m.end() + 30].replace("\n", " ")
    return (line_no, col, m.group(0), why, snippet)


def check(text, announced=False):
    """Hard-rule problems as (line, column, found, reason, snippet), sorted."""
    rules = ALWAYS + ([] if announced else BEFORE_ANNOUNCEMENT)
    problems = []
    for pattern, why in rules:
        for m in re.finditer(pattern, text, flags=re.IGNORECASE):
            problems.append(_problem(text, m, why))
    for pattern, why in CASED:
        for m in re.finditer(pattern, text):
            problems.append(_problem(text, m, why))
    problems += check_links(text)
    return sorted(problems)


def check_links(text):
    """Vague link text, in the same tuple shape as check()."""
    problems = []
    for m in re.finditer(VAGUE_PHRASES, text, flags=re.IGNORECASE):
        if not _quoted(text, m.start(), m.end()):
            problems.append(_problem(text, m, VAGUE_LINK_WHY))
    for m in re.finditer(VAGUE_HERE, text, flags=re.IGNORECASE):
        problems.append(_problem(text, m, VAGUE_LINK_WHY))
    return problems


def _prose(text):
    """Strip markup so only reading text is left: code, tags, link targets, table rows, headings."""
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"<(script|style)\b.*?</\1>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"\]\([^)]*\)", "]", text)
    text = re.sub(r"https?://\S+|\b[\w.-]+@[\w.-]+\b", " ", text)
    lines = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("|") or s.startswith("#") or s.startswith("---"):
            continue
        s = re.sub(r"^([-*+>]|\d+\.)\s+", "", s)
        lines.append(s.replace("*", "").replace("_", " ").replace("[", "").replace("]", ""))
    return "\n".join(lines)


def _syllables(word):
    word = word.lower()
    if len(word) <= 3:
        return 1
    word = re.sub(r"(?:[^laeiouy]es|ed|[^laeiouy]e)$", "", word)
    word = re.sub(r"^y", "", word)
    return max(1, len(re.findall(r"[aeiouy]{1,2}", word)))


def reading_level(text):
    """(Flesch-Kincaid grade, word count) for the body copy in text, or (None, words)."""
    prose = _prose(text)
    # A line without its own full stop (a list item, a short line) still ends a sentence.
    sentences = [s for s in re.split(r"[.?!]+(?:\s|$)|\n+", prose) if re.search(r"[A-Za-z]", s)]
    words = re.findall(r"[A-Za-z][A-Za-z'-]*", prose)
    if not words or not sentences:
        return None, len(words)
    syll = sum(_syllables(w) for w in words)
    grade = 0.39 * len(words) / len(sentences) + 11.8 * syll / len(words) - 15.59
    return round(grade, 1), len(words)


def abbreviations(text):
    """First use of each all-caps token not in the allowlist and not spelled out in brackets."""
    prose = _prose(text)
    seen, hints = set(), []
    for m in re.finditer(r"(?<![\w-])([A-Z]{2,5})(s?)(?![\w-])", prose):
        token = m.group(1) + m.group(2)
        if token in seen or token in ABBREVIATION_ALLOWLIST or m.group(1) in ABBREVIATION_ALLOWLIST:
            continue
        seen.add(token)
        # "small and medium-sized businesses (SMEs)" counts as spelled out.
        if prose[max(0, m.start() - 1):m.start()] == "(" and prose[m.end():m.end() + 1] == ")":
            continue
        hints.append(token)
    return hints


def word_hints(text):
    """First use of each preferred-word pattern, as (found, reason)."""
    found = []
    prose = _prose(text)
    for pattern, why in WORD_HINTS:
        m = re.search(pattern, prose, flags=re.IGNORECASE)
        if m:
            found.append((m.group(0), why))
    return found


def main(argv):
    announced = "--announced" in argv
    hints = "--no-hints" not in argv
    paths = [a for a in argv if a not in ("--announced", "--no-hints")]
    if not paths:
        print(__doc__)
        return 2
    failed = False
    for path in paths:
        text = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
        for line_no, col, found, why, snippet in check(text, announced):
            failed = True
            print("%s:%d:%d: '%s' - %s ... %s ..." % (path, line_no, col, found, why, snippet))
        if not hints:
            continue
        grade, words = reading_level(text)
        if grade is not None:
            note = ""
            if grade > READING_GRADE_LIMIT and words > READING_MIN_WORDS:
                note = " - hint: above grade %d, use shorter sentences and plainer words" % READING_GRADE_LIMIT
            print("%s: reading level: grade %.1f (%d words)%s" % (path, grade, words, note))
        for word, why in word_hints(text):
            print("%s: hint: '%s' - %s" % (path, word, why))
        for token in abbreviations(text):
            print("%s: hint: '%s' - spell out on first use, then the short form in brackets" % (path, token))
    if not failed:
        print("[climb-voice] OK: no hard-rule problems%s" % ("" if announced else " (venue embargo on)"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
