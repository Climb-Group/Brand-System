"""Brand tools for AI assistants, in plain Python (standard library only).

Every answer comes from the brand pack itself: the climb-voice and
climb-visual-style skills, their copy checker, the guidelines and
``tokens/brand.tokens.json``. Nothing here re-types a brand value, so the tools
stay right when those files change.

The file runs from the brand pack (``ai/tools/brand_rules.py``) or from a copy
of the pack inside a platform integration: set ``CLIMB_BRAND_PACK`` or call
``set_root()`` when the pack is somewhere else. A copy may drop the leading dot
of ``.agents`` (some packagers skip hidden folders).
"""

import importlib.util
import json
import os
import re

# Pack files the tools read, by key, relative to the pack root.
DOCUMENTS = {
    "voice": ".agents/skills/climb-voice/SKILL.md",
    "audiences": ".agents/skills/climb-voice/references/audiences.md",
    "channels": ".agents/skills/climb-voice/references/channels.md",
    "examples": ".agents/skills/climb-voice/references/examples.md",
    "visual-style": ".agents/skills/climb-visual-style/SKILL.md",
    "elements": ".agents/skills/climb-visual-style/references/elements.md",
    "surfaces": ".agents/skills/climb-visual-style/references/surfaces.md",
    "ui": "guidelines/ui.md",
    "motion": "guidelines/motion.md",
    "photography": "guidelines/photography.md",
    "video": "guidelines/video.md",
    "print": "guidelines/print.md",
    "signatures": "guidelines/signatures.md",
    "press-and-partners": "guidelines/press-and-partners.md",
    "public-voice": "guidelines/voice.md",
    "accessibility": "guidelines/ui.md",
}
TOKENS = "tokens/brand.tokens.json"
CHECKER = ".agents/skills/climb-voice/scripts/check_copy.py"

BRANDS = {
    "climbuk": "ClimbUK",
    "climbgroup": "ClimbGroup",
    "climb27": "Climb27",
}

MAX_TEXT = 20000
MAX_SECTION = 6000

_cache = {}


def _default_root():
    env = os.environ.get("CLIMB_BRAND_PACK")
    if env:
        return env
    here = os.path.dirname(os.path.abspath(__file__))
    for candidate in (
        os.path.join(here, "..", ".."),  # the brand pack: ai/tools/brand_rules.py
        os.path.join(here, "..", "data", "pack"),  # a platform module: lib/ next to data/pack/
    ):
        if os.path.exists(os.path.join(candidate, TOKENS)):
            return os.path.normpath(candidate)
    return os.path.normpath(os.path.join(here, "..", ".."))


ROOT = _default_root()


def set_root(path):
    """Point the tools at a brand pack folder and forget anything cached."""
    global ROOT
    ROOT = path
    _cache.clear()


def pack_path(relative):
    """Absolute path of a pack file, accepting a copy without the leading dot on .agents."""
    first = os.path.join(ROOT, relative)
    if os.path.exists(first) or not relative.startswith("."):
        return first
    return os.path.join(ROOT, relative[1:])


def _read(relative):
    if relative not in _cache:
        with open(pack_path(relative), encoding="utf-8") as handle:
            _cache[relative] = handle.read()
    return _cache[relative]


def checker():
    """The climb-voice copy checker, loaded from the pack."""
    if "checker" not in _cache:
        spec = importlib.util.spec_from_file_location("climb_check_copy", pack_path(CHECKER))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _cache["checker"] = module
    return _cache["checker"]


def _norm(value):
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()


# ---------------------------------------------------------------------------
# Copy


def check_text(text, announced=False):
    """Run the climb-voice checker. Returns problems, hints and a reading level."""
    text = str(text or "")
    # Some platforms cut an over-long argument to its maxLength and add "...".
    truncated = len(text) > MAX_TEXT or (len(text) == MAX_TEXT + 3 and text.endswith("..."))
    text = text[:MAX_TEXT]
    problems = [
        {"line": line, "column": col, "found": found, "rule": why}
        for line, col, found, why, _snippet in checker().check(text, announced)
    ]
    grade, words = checker().reading_level(text)
    hints = [{"found": found, "hint": why} for found, why in checker().word_hints(text)]
    hints += [
        {"found": token, "hint": "spell out on first use, then the short form in brackets"}
        for token in checker().abbreviations(text)
    ]
    reading = None
    if grade is not None:
        reading = {
            "grade": grade,
            "words": words,
            "target": "grade %d or lower" % checker().READING_GRADE_LIMIT,
            "too_hard": grade > checker().READING_GRADE_LIMIT and words > checker().READING_MIN_WORDS,
        }
    return {
        "ok": not problems,
        "venue_embargo": not announced,
        "problems": problems,
        "hints": hints,
        "reading_level": reading,
        "truncated": truncated,
        "note": (
            ("Only the first %d characters were checked: check the rest in further calls. " % MAX_TEXT if truncated else "")
            + "The checker does not judge tone. Re-read against the four voice lines: "
            "headline energy, doing not dreaming, curated not crowded, personal not generic."
        ),
    }


# ---------------------------------------------------------------------------
# Tokens and colour


def tokens():
    if "tokens" not in _cache:
        _cache["tokens"] = json.loads(_read(TOKENS))
    return _cache["tokens"]


def _flatten(node, prefix=""):
    out = {}
    if isinstance(node, dict):
        if "$value" in node or "value" in node:
            out[prefix] = {
                "value": node.get("$value", node.get("value")),
                "description": node.get("$description") or node.get("description") or "",
            }
            return out
        for key, child in node.items():
            if key.startswith("$"):
                continue
            out.update(_flatten(child, "%s.%s" % (prefix, key) if prefix else key))
    return out


def flat_tokens():
    if "flat" not in _cache:
        flat = _flatten(tokens())
        for _ in range(5):
            for item in flat.values():
                value = item["value"]
                if isinstance(value, str):
                    match = re.fullmatch(r"\{([^}]+)\}", value.strip())
                    if match and match.group(1) in flat:
                        item["alias_of"] = match.group(1)
                        item["value"] = flat[match.group(1)]["value"]
        _cache["flat"] = flat
    return _cache["flat"]


def token_groups():
    return sorted({key.split(".")[0] for key in flat_tokens()})


def get_tokens(group="", query=""):
    """Tokens under a group prefix (for example 'color', 'type', 'theme.aaa-dark'), optionally filtered."""
    flat = flat_tokens()
    group = (group or "").strip().lower()
    query = _norm(query)
    rows = []
    for key, item in flat.items():
        if group and not (key == group or key.startswith(group + ".")):
            continue
        if query and query not in _norm(key + " " + item["description"]):
            continue
        if key == "pairs":
            continue
        row = {"token": key, "value": item["value"]}
        if item.get("description"):
            row["description"] = item["description"]
        if item.get("alias_of"):
            row["alias_of"] = item["alias_of"]
        rows.append(row)
    return {
        "ok": bool(rows),
        "groups": token_groups(),
        "tokens": rows[:120],
        "truncated": len(rows) > 120,
        "message": "" if rows else "No token matches. Try one of the groups listed.",
    }


def brand_hexes():
    """Every hex colour in the tokens, mapped to the token names that hold it."""
    out = {}
    for key, item in flat_tokens().items():
        value = item["value"]
        if not key.startswith("color."):
            continue
        if isinstance(value, str) and re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
            out.setdefault(value.upper(), []).append(key)
    return out


def _hex(value):
    value = str(value or "").strip()
    if not value.startswith("#"):
        value = "#" + value
    if re.fullmatch(r"#[0-9A-Fa-f]{3}", value):
        value = "#" + "".join(ch * 2 for ch in value[1:])
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
        return None
    return value.upper()


def _resolve_colour(value):
    """Accept a hex, a token name or a colour's display name ('Climb Orange')."""
    as_hex = _hex(value)
    if as_hex:
        return as_hex
    flat = flat_tokens()
    key = str(value or "").strip()
    if key in flat and _hex(flat[key]["value"]):
        return _hex(flat[key]["value"])
    wanted = _norm(value)
    for token, item in flat.items():
        if not token.startswith("color."):
            continue
        if _norm(token.split(".")[-1]) == wanted or _norm(item["description"].split(".")[0]) == wanted:
            if _hex(item["value"]):
                return _hex(item["value"])
    return None


def _luminance(hex_value):
    def channel(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (int(hex_value[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast_ratio(fg, bg):
    l1, l2 = _luminance(fg), _luminance(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return round((hi + 0.05) / (lo + 0.05), 2)


def check_colours(foreground, background, size="normal"):
    """WCAG 2.2 contrast for a pair, plus whether both colours are brand tokens.

    size: 'normal' (body text), 'large' (24px+, or 19px bold+), 'non-text' (icons, borders).
    """
    fg, bg = _resolve_colour(foreground), _resolve_colour(background)
    if not fg or not bg:
        return {
            "ok": False,
            "message": "Give two colours as hex (#E8712A) or token names (color.brand.orange).",
        }
    size = (size or "normal").strip().lower()
    ratio = contrast_ratio(fg, bg)
    limits = tokens().get("contrast", {})

    def limit(name, default):
        node = limits.get(name, {})
        return float(node.get("$value", node.get("value", default))) if isinstance(node, dict) else default

    if size == "large":
        aa, aaa = limit("large-text", 3.0), limit("aaa-large-text", 4.5)
    elif size in ("non-text", "nontext", "icon"):
        aa, aaa = limit("non-text", 3.0), None
    else:
        size = "normal"
        aa, aaa = limit("normal-text", 4.5), limit("aaa-text", 7.0)
    hexes = brand_hexes()
    result = {
        "ok": ratio >= aa,
        "foreground": fg,
        "background": bg,
        "foreground_tokens": hexes.get(fg, []),
        "background_tokens": hexes.get(bg, []),
        "size": size,
        "ratio": ratio,
        "passes_aa": ratio >= aa,
        "passes_aaa": None if aaa is None else ratio >= aaa,
        "aa_minimum": aa,
        "aaa_minimum": aaa,
    }
    notes = []
    if fg not in hexes or bg not in hexes:
        notes.append("At least one colour is not a brand token. Use token colours only.")
    if fg == "#EC752A" or bg == "#EC752A":
        notes.append("#EC752A is retired. Use Climb Orange #E8712A.")
    if fg == "#FFFFFF" and bg == "#E8712A" and size == "normal":
        notes.append("White on Climb Orange is for 19px bold or larger only (14pt bold in print).")
    suggestion = suggest_for_ground(bg)
    if suggestion:
        result["preset_for_this_ground"] = suggestion
    result["notes"] = notes
    return result


def presets():
    """The five grounds and the colours each one allows, resolved to hex."""
    flat = flat_tokens()
    out = []
    for key in sorted({k.split(".")[1] for k in flat if k.startswith("preset.")}):
        row = {"preset": key}
        for token, item in flat.items():
            if token.startswith("preset.%s." % key):
                row[token.split(".")[-1]] = item["value"]
        out.append(row)
    return out


def themes():
    flat = flat_tokens()
    out = {}
    for token, item in flat.items():
        if token.startswith("theme."):
            _, name, role = token.split(".", 2)
            out.setdefault(name, {})[role] = item["value"]
    return out


def suggest_for_ground(background):
    bg = _resolve_colour(background)
    if not bg:
        return None
    for row in presets():
        if _hex(row.get("background")) == bg:
            return row
    return None


def get_palette(ground=""):
    """Presets and themes, or the one preset for a ground (hex, token or name)."""
    if ground:
        match = suggest_for_ground(ground)
        if match:
            return {"ok": True, "preset": match, "rules": _palette_rules()}
        return {
            "ok": False,
            "message": "That ground is not a brand ground. Use White, Light Grey, Dark Brown, Climb Orange or Charcoal.",
            "presets": presets(),
        }
    return {"ok": True, "presets": presets(), "themes": themes(), "rules": _palette_rules()}


def _palette_rules():
    return [
        "Dark first: Dark Brown #1E0F05 or Charcoal #242322 is the default ground.",
        "One orange button or call to action per section, slide, post or screen.",
        "White on Climb Orange only at 19px bold or larger (14pt bold in print).",
        "Never Light Grey or Body Slate text on any orange; never orange on orange; "
        "never Climb Orange headings on Light Grey; never a lighter hover state.",
        "AAA themes (theme.aaa-dark, theme.aaa-light) exist for every surface that can use them.",
        "#EC752A is retired. Climb Orange is #E8712A.",
    ]


# ---------------------------------------------------------------------------
# Logos

LOGO_VARIANTS = (
    "full-colour-light", "full-colour-grey", "reversed-dark", "mono-dark", "mono-white",
    "tagline-lockup", "tagline-lockup-reversed", "icon", "icon-monogram",
)
LOGOS_README = "logos/README.md"


def _logo_readme():
    """Per-variant use notes and the rule sections, read from logos/README.md."""
    if "logos" not in _cache:
        text = _read(LOGOS_README)
        about = {}
        for _heading, header, cells in _tables(text):
            row = dict(zip(header, cells))
            match = re.search(r"_([a-z-]+)\.svg", row.get("File", ""))
            if match and match.group(1) in LOGO_VARIANTS:
                about[match.group(1)] = row.get("Use it on", "").replace("**", "")
        sections = {heading: body for heading, body in _sections(text)}
        rules = []
        for name, prefix in (("Clear space and minimum size", ""), ("Don't", "Never: ")):
            body = sections.get(name, "")
            rules += [
                prefix + re.sub(r"\s+", " ", line.strip().lstrip("-").strip()).replace("**", "")
                for line in body.splitlines()[1:]
                if line.strip().startswith("-") and not line.strip().endswith(":**")
            ]
        _cache["logos"] = (about, rules)
    return _cache["logos"]


def pick_logo(brand="climbuk", ground="dark", width_px=0, use="", tagline=False, colours=0):
    """Choose the logo master for a brand, ground and size. Notes and rules come from logos/README.md."""
    brand_name = BRANDS.get(_norm(brand).replace(" ", ""))
    if not brand_name:
        return {"ok": False, "message": "Brand must be ClimbUK, ClimbGroup or Climb27."}
    ground_key = _norm(ground)
    use_key = _norm(use)
    width = _int(width_px)
    reasons = []
    if any(word in use_key for word in ("favicon", "app icon", "browser")) or (0 < width < 64):
        variant = "icon-monogram"
        reasons.append("Favicons, app icons and anything under 64px use the l! monogram.")
    elif any(word in use_key for word in ("avatar", "profile", "square")):
        variant = "icon"
        reasons.append("Social avatars and squares of 64px or more use the stacked tile.")
    elif "orange" in ground_key:
        variant = "mono-white"
        reasons.append("On Climb Orange use mono white, never the full-colour logo.")
    elif "grey" in ground_key or "gray" in ground_key:
        variant = "full-colour-grey"
        reasons.append("Light Grey grounds use the grey version, with the deeper orange.")
    elif any(word in ground_key for word in ("white", "light", "paper")):
        if colours == 1:
            variant = "mono-dark"
        else:
            variant = "tagline-lockup" if tagline else "full-colour-light"
        reasons.append("White grounds: Climb Orange with Charcoal.")
    else:
        if colours == 1:
            variant = "mono-white"
        else:
            variant = "tagline-lockup-reversed" if tagline else "reversed-dark"
        reasons.append("Dark grounds and dark photography use the reversed logo (the default).")
    if "photo" in ground_key:
        reasons.append("On a photo, put the logo on a calm area, or darken the photo behind it first.")
    if variant.startswith("tagline") and 0 < width < 240:
        variant = {"tagline-lockup": "full-colour-light", "tagline-lockup-reversed": "reversed-dark"}[variant]
        reasons.append("Tagline lockups need 240px or 60mm, so the plain wordmark is used.")
    if variant not in ("icon", "icon-monogram") and 0 < width < 120:
        variant = "icon-monogram" if width < 64 else "icon"
        reasons.append("Wordmarks need 120px on screen or 30mm in print; below that use a square icon.")
    about, rules = _logo_readme()
    stem = "%s_%s" % (brand_name, variant)
    return {
        "ok": True,
        "brand": brand_name,
        "variant": variant,
        "about": about.get(variant, ""),
        "files": {
            "vector": "logos/%s/%s.svg" % (brand_name, stem),
            "png": ["logos/%s/PNG/%s_%d.png" % (brand_name, stem, size) for size in (512, 1024, 2048)],
        },
        "reasons": reasons,
        "rules": rules + [
            "ClimbUK is the brand on the poster. ClimbGroup is the organisation (footers, legal, corporate decks). "
            "An edition mark (Climb27) leads on event pieces, with ClimbUK as the endorsement.",
        ],
    }


# ---------------------------------------------------------------------------
# Markdown tables (surfaces, audiences, channels) and guide sections


def _tables(markdown):
    """Yield (section heading, header cells, row cells) for every markdown table row."""
    heading = ""
    header = None
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            heading = stripped.lstrip("#").strip()
            header = None
            continue
        if not stripped.startswith("|"):
            header = None
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if header is None:
            header = cells
            continue
        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells if cell):
            continue
        yield heading, header, cells


def _table_lookup(doc, query, limit=8):
    query_n = _norm(query)
    words = [w for w in query_n.split() if len(w) > 1]
    scored = []
    for heading, header, cells in _tables(_read(DOCUMENTS[doc])):
        row = dict(zip(header, cells))
        row["section"] = heading
        hay = _norm(" ".join(cells) + " " + heading)
        first = _norm(cells[0]) if cells else ""
        if not words:
            score = 1
        else:
            score = sum(1 for w in words if w in hay)
            if score and query_n and query_n in first:
                score += 5
        if score:
            scored.append((score, row))
    scored.sort(key=lambda item: -item[0])
    best = scored[0][0] if scored else 0
    return [row for score, row in scored if score == best or not words][:limit]


def get_surface(surface=""):
    rows = _table_lookup("surfaces", surface, limit=40 if not surface else 6)
    return {
        "ok": bool(rows),
        "surfaces": rows,
        "defaults": [
            "Video, photo and screen work is 4K by default. RAW capture no less than 4K, ideally 8K, 6K is fine. Never upscale.",
            "Print is CMYK PDF/X-4 with 3mm bleed unless the printer asks otherwise. Screen is sRGB PNG (JPG for photos, WebP on the web).",
            "File name: <brand>_<surface>_<variant>_<size>.<ext>, for example climb27_zoom-bg_stage-light_1920x1080.png.",
            "Before the venue announcement, nothing public carries the venue or city.",
        ],
        "message": "" if rows else "No surface matches. Ask for a list with an empty surface.",
    }


def get_audience(audience=""):
    rows = _table_lookup("audiences", audience, limit=20 if not audience else 3)
    return {
        "ok": bool(rows),
        "audiences": rows,
        "shared_truths": [
            "Two days, every session, the grand opening and the after parties.",
            "Business that feels like a festival: Find Your People and Main Stage Moments.",
            "Close and personal: the right people, not the most people.",
            "A community: people who share what they have learned and send each other work.",
            "Practical growth you can act on the next morning.",
        ],
        "rule": "Attendee pages and partner pages are separate. Where a row says 'Ask before writing', ask the person before drafting.",
        "message": "" if rows else "No audience matches. Ask for a list with an empty audience.",
    }


def get_channel(channel=""):
    rows = _table_lookup("channels", channel, limit=20 if not channel else 3)
    return {
        "ok": bool(rows),
        "channels": rows,
        "utm": (
            "Every link to an audience page carries utm_source (the platform), utm_medium "
            "(social, email, partner, paid), utm_campaign=climb27 and utm_content (the post or asset name)."
        ),
        "message": "" if rows else "No channel matches. Ask for a list with an empty channel.",
    }


def _sections(markdown):
    current, lines = "", []
    for line in markdown.splitlines():
        if line.startswith("#"):
            if lines:
                yield current, "\n".join(lines).strip()
            current, lines = line.lstrip("#").strip(), [line]
        else:
            lines.append(line)
    if lines:
        yield current, "\n".join(lines).strip()


def read_guide(topic="", document=""):
    """Return the guide sections that best match a topic, from one document or all of them."""
    doc_key = _norm(document).replace(" ", "-")
    docs = [doc_key] if doc_key in DOCUMENTS else list(DOCUMENTS)
    words = [w for w in _norm(topic).split() if len(w) > 2]
    if not words:
        return {
            "ok": True,
            "documents": {key: [h for h, _ in _sections(_read(DOCUMENTS[key])) if h] for key in docs},
            "message": "Name a topic to read a section.",
        }
    scored = []
    for key in docs:
        for heading, body in _sections(_read(DOCUMENTS[key])):
            head_n, body_n = _norm(heading), _norm(body)
            score = sum(3 for w in words if w in head_n) + sum(min(body_n.count(w), 3) for w in words)
            if score:
                scored.append((score, key, heading, body))
    scored.sort(key=lambda item: -item[0])
    out, used = [], 0
    for _score, key, heading, body in scored[:3]:
        body = body[:MAX_SECTION]
        used += len(body)
        if used > MAX_TEXT:
            break
        out.append({"document": key, "section": heading, "text": body})
    return {
        "ok": bool(out),
        "sections": out,
        "message": "" if out else "Nothing matches that topic. Call again with no topic for the list of sections.",
    }


# ---------------------------------------------------------------------------
# One entry point for every tool in ai/kit.json


def _bool(value):
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "y", "on")
    return bool(value)


def _int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


TOOLS = {
    "check_copy": lambda a, announced: check_text(a.get("text"), announced),
    "check_colours": lambda a, _: check_colours(a.get("foreground"), a.get("background"), a.get("size") or "normal"),
    "palette": lambda a, _: get_palette(a.get("ground") or ""),
    "tokens": lambda a, _: get_tokens(a.get("group") or "", a.get("query") or ""),
    "logo": lambda a, _: pick_logo(
        brand=a.get("brand") or "climbuk",
        ground=a.get("ground") or "dark",
        width_px=_int(a.get("width_px")),
        use=a.get("use") or "",
        tagline=_bool(a.get("tagline")),
        colours=_int(a.get("colours")),
    ),
    "surface": lambda a, _: get_surface(a.get("surface") or ""),
    "audience": lambda a, _: get_audience(a.get("audience") or ""),
    "channel": lambda a, _: get_channel(a.get("channel") or ""),
    "guide": lambda a, _: read_guide(a.get("topic") or "", a.get("document") or ""),
}


def call(tool, arguments=None, venue_announced=False):
    """Run a tool by its key in ai/kit.json. ``venue_announced`` comes from the
    platform's own setting, never from the model, so the AI cannot lift the embargo."""
    func = TOOLS.get(tool)
    if not func:
        return {"ok": False, "message": "Unknown brand tool: %s" % tool}
    arguments = arguments if isinstance(arguments, dict) else {}
    return func(arguments, bool(venue_announced))


def kit():
    """The tools, skills and agents in ai/kit.json."""
    if "kit" not in _cache:
        _cache["kit"] = json.loads(_read("ai/kit.json"))
    return _cache["kit"]
