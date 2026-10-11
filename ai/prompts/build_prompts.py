"""Build the ClimbUK prompt library exports and the plugin packages from the prompt files.

    python3 ai/prompts/build_prompts.py            write everything below
    python3 ai/prompts/build_prompts.py --check    exit 1 if any of it is out of date or a prompt breaks a rule

The source of truth is one Markdown file per prompt in ai/prompts/library/<task type>/,
plus the brand rules in ai/prompts/brand/. Everything else is compiled from them:

- ai/prompts/dist/copilot/climbuk-prompts.csv, the Microsoft 365 Copilot organisational
  prompts import file (the columns and order of Microsoft's prompt-import-template.csv);
- ai/prompts/dist/prompts.json and ai/prompts/dist/PROMPTS.md, the whole library for any
  assistant, as data and as a page to read and copy from;
- ai/prompts/dist/*.zip, the prompts as slash commands or prompt files for Claude Code,
  Codex, Cursor, GitHub Copilot in VS Code and Gemini CLI;
- ai/packages/climb-prompts.zip, the prompt library as an Agent Skill;
- ai/packages/cowork/<skill>.zip, each brand skill with SKILL.md at the top, for a
  Microsoft 365 Copilot Cowork skill upload;
- ai/packages/climbuk-brand-plugin.zip, a Claude plugin (skills and commands);
- ai/packages/climbuk-brand-plugin-m365.zip, a Microsoft 365 Copilot Cowork plugin
  (app manifest with agentSkills).

Zips are deterministic, so --check compares bytes. Standard library only.
"""
import csv
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "ai", "agents"))
sys.path.insert(0, os.path.join(ROOT, ".agents", "skills", "climb-voice", "scripts"))

import build_agent_kits as kits  # noqa: E402
import check_copy  # noqa: E402

LIBRARY = "ai/prompts/library"
BRAND = "ai/prompts/brand"
DIST = "ai/prompts/dist"
PACKAGES = "ai/packages"
COPILOT_ICONS = "ai/agents/copilot"
VERSION = "1.0.0"
PLUGIN = "climbuk-brand"
PROMPT_SKILL = "climb-prompts"
M365_PLUGIN_ID = "45718227-8557-441b-9890-749c458f632a"

# Microsoft's supported task types, in the order the import flyout lists them.
TASK_TYPES = (
    "Analyze", "Ask", "Assist", "Catch up", "Code", "Create", "Design",
    "Edit", "Execute", "Find", "Learn", "Prepare", "Schedule", "Understand",
)
APPS = ("Copilot web", "Copilot work")
BRAND_KINDS = {"none": (), "voice": ("voice",), "visual": ("visual",), "both": ("voice", "visual")}
FIELDS = ("title", "description", "display", "task", "department", "apps", "brand", "locale")
# Microsoft 365 organisational prompt limits (characters), and the import cap per file.
LIMITS = {"title": 35, "display": 132, "prompt": 8000, "department": 120, "description": 200}
PER_FILE = 100
CSV_HEADER = ["Title", "Description", "Display Prompt", "Prompt Text", "Products", "Department", "Task Type", "Locale"]
PLACEHOLDER = re.compile(r"\{\{([a-z][a-z0-9_]*)\}\}")
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


class PromptError(Exception):
    pass


def task_folder(task):
    return task.lower().replace(" ", "-")


def parse(path):
    """One prompt file: simple 'key: value' front matter, then the prompt text."""
    text = open(path, encoding="utf-8").read()
    match = re.match(r"^---\n(.*?)\n---\n\n?(.*)$", text, re.S)
    if not match:
        raise PromptError("%s: no front matter" % path)
    meta = {}
    for line in match.group(1).split("\n"):
        key, sep, value = line.partition(": ")
        if not sep or key not in FIELDS:
            raise PromptError("%s: unknown front matter line %r" % (path, line))
        meta[key] = value.strip()
    missing = [f for f in FIELDS if not meta.get(f)]
    if missing:
        raise PromptError("%s: missing %s" % (path, ", ".join(missing)))
    meta["slug"] = os.path.splitext(os.path.basename(path))[0]
    meta["body"] = match.group(2).strip()
    meta["path"] = os.path.relpath(path, ROOT).replace(os.sep, "/")
    return meta


def brand_rules(kind):
    return [open(os.path.join(ROOT, BRAND, name + ".md"), encoding="utf-8").read().strip() for name in BRAND_KINDS[kind]]


def prompt_text(p):
    """The full prompt: the task, then the brand rules it needs."""
    parts = [p["body"]]
    rules = brand_rules(p["brand"])
    if rules:
        parts.append("Brand rules: " + " ".join(rules))
    return "\n\n".join(parts)


def placeholders(p):
    seen = []
    for name in PLACEHOLDER.findall(p["body"]):
        if name not in seen:
            seen.append(name)
    return seen


def problems(p, slugs):
    """Every rule a prompt breaks, as strings."""
    found = []
    where = p["path"]
    if not SLUG.match(p["slug"]):
        found.append("%s: file name must be kebab-case" % where)
    if slugs.count(p["slug"]) > 1:
        found.append("%s: another prompt has the same file name" % where)
    if p["task"] not in TASK_TYPES:
        found.append("%s: task %r is not a supported task type" % (where, p["task"]))
    elif os.path.basename(os.path.dirname(where)) != task_folder(p["task"]):
        found.append("%s: belongs in %s/%s/" % (where, LIBRARY, task_folder(p["task"])))
    apps = [a.strip() for a in p["apps"].split(",")]
    if not apps or any(a not in APPS for a in apps) or len(set(apps)) != len(apps):
        found.append("%s: apps must be from %s" % (where, ", ".join(APPS)))
    if p["brand"] not in BRAND_KINDS:
        found.append("%s: brand must be one of %s" % (where, ", ".join(BRAND_KINDS)))
        return found
    if not re.match(r"^[a-z]{2}-[A-Z]{2}$", p["locale"]):
        found.append("%s: locale must look like en-GB" % where)
    values = dict(p, prompt=prompt_text(p))
    for field, limit in LIMITS.items():
        if len(values[field]) > limit:
            found.append("%s: %s is %d characters; the limit is %d" % (where, field, len(values[field]), limit))
    if "{{" in p["display"] or "{{" in p["title"]:
        found.append("%s: the title and display prompt are shown to people, so they carry no placeholders" % where)
    if re.search(r"\{\{(?![a-z][a-z0-9_]*\}\})", p["body"]):
        found.append("%s: placeholders are {{lower_snake_case}}" % where)
    for field in ("title", "description", "display", "department"):
        for _line, _col, word, why, _snippet in check_copy.check(p[field], False):
            found.append("%s: %s: '%s' - %s" % (where, field, word, why))
    for field in ("title", "description", "display"):
        if any(ord(c) > 127 for c in p[field]):
            found.append("%s: %s must be ASCII" % (where, field))
    return found


def load():
    prompts = []
    base = os.path.join(ROOT, LIBRARY)
    for directory in sorted(os.listdir(base)):
        folder = os.path.join(base, directory)
        if not os.path.isdir(folder):
            continue
        for name in sorted(os.listdir(folder)):
            if name.endswith(".md"):
                prompts.append(parse(os.path.join(folder, name)))
    order = {t: i for i, t in enumerate(TASK_TYPES)}
    prompts.sort(key=lambda p: (order.get(p["task"], 99), p["slug"]))
    return prompts


def validate(prompts):
    slugs = [p["slug"] for p in prompts]
    found = [problem for p in prompts for problem in problems(p, slugs)]
    covered = {p["task"] for p in prompts}
    found += ["no prompt for task type %r" % t for t in TASK_TYPES if t not in covered]
    return found


# ---------------------------------------------------------------- exports


def copilot_csv(rows):
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\r\n")
    writer.writerow(CSV_HEADER)
    for p in rows:
        writer.writerow([
            p["title"], p["description"], p["display"], prompt_text(p),
            ", ".join(a.strip() for a in p["apps"].split(",")), p["department"], p["task"], p["locale"],
        ])
    # Excel's "CSV UTF-8" carries a byte order mark, like Microsoft's template.
    return ("﻿" + buffer.getvalue()).encode("utf-8")


def copilot_files(prompts):
    if len(prompts) <= PER_FILE:
        return {DIST + "/copilot/climbuk-prompts.csv": copilot_csv(prompts)}
    files = {}
    for n, start in enumerate(range(0, len(prompts), PER_FILE), 1):
        files["%s/copilot/climbuk-prompts-%d.csv" % (DIST, n)] = copilot_csv(prompts[start:start + PER_FILE])
    return files


def library_json(prompts):
    data = {
        "name": "ClimbUK prompt library",
        "version": VERSION,
        "repository": kits.REPOSITORY,
        "task_types": list(TASK_TYPES),
        "prompts": [
            {
                "id": p["slug"],
                "title": p["title"],
                "description": p["description"],
                "display_prompt": p["display"],
                "prompt": prompt_text(p),
                "placeholders": placeholders(p),
                "supported_apps": [a.strip() for a in p["apps"].split(",")],
                "department": p["department"],
                "task_type": p["task"],
                "locale": p["locale"],
                "brand": p["brand"],
                "source": p["path"],
            }
            for p in prompts
        ],
    }
    return (json.dumps(data, indent=2) + "\n").encode()


def library_markdown(prompts):
    lines = [
        "# ClimbUK prompt library",
        "",
        "Generated from `%s` by `ai/prompts/build_prompts.py`. Do not edit this file: edit the prompt file and rebuild." % LIBRARY,
        "",
        "Copy a prompt into any assistant and replace each `{{placeholder}}` with your details. %d prompts across %d task types." % (len(prompts), len(TASK_TYPES)),
        "",
    ]
    for task in TASK_TYPES:
        lines += ["## %s" % task, ""]
        for p in [p for p in prompts if p["task"] == task]:
            lines += [
                "### %s" % p["title"],
                "",
                p["description"],
                "",
                "- Display prompt: %s" % p["display"],
                "- Department: %s" % p["department"],
                "- Supported apps: %s" % p["apps"],
                "- Source: `%s`" % p["path"],
                "",
                "```text",
                prompt_text(p),
                "```",
                "",
            ]
    return ("\n".join(lines).rstrip() + "\n").encode()


def human(name):
    return name.replace("_", " ")


def bracketed(text):
    return PLACEHOLDER.sub(lambda m: "[%s]" % human(m.group(1)), text)


def yaml_string(value):
    return json.dumps(value)


def command_markdown(p, arguments):
    """A slash command file for Claude Code (arguments=True) or Cursor."""
    names = placeholders(p)
    head = ["---", "description: %s" % yaml_string(p["description"])]
    if arguments and names:
        head.append("argument-hint: %s" % yaml_string(" ".join("[%s]" % human(n) for n in names)))
    head.append("---")
    body = bracketed(prompt_text(p))
    if names:
        if arguments:
            body += "\n\nDetails from me: $ARGUMENTS"
        body += "\n\nIf any detail in square brackets above is missing, ask me for it before you start."
    return ("\n".join(head) + "\n\n" + body + "\n").encode()


def codex_markdown(p):
    names = placeholders(p)
    head = ["---", "description: %s" % yaml_string(p["description"])]
    if names:
        head.append("argument-hint: %s" % yaml_string(" ".join("%s=<%s>" % (n.upper(), human(n)) for n in names)))
    head.append("---")
    body = PLACEHOLDER.sub(lambda m: "$" + m.group(1).upper(), prompt_text(p))
    return ("\n".join(head) + "\n\n" + body + "\n").encode()


def vscode_markdown(p):
    head = ["---", "description: %s" % yaml_string(p["description"]), "---"]
    body = PLACEHOLDER.sub(lambda m: "${input:%s:%s}" % (m.group(1), human(m.group(1))), prompt_text(p))
    return ("\n".join(head) + "\n\n" + body + "\n").encode()


def gemini_toml(p):
    body = bracketed(prompt_text(p))
    if placeholders(p):
        body += "\n\nDetails from me: {{args}}\n\nIf any detail in square brackets above is missing, ask me for it before you start."
    if "'''" in body:
        raise PromptError("%s: ''' cannot appear in a prompt" % p["path"])
    return ("description = %s\nprompt = '''\n%s\n'''\n" % (json.dumps(p["description"]), body)).encode()


def command_zips(prompts):
    def zipped(path_for, render):
        return kits.make_zip([(path_for(p), render(p), False) for p in prompts])

    return {
        DIST + "/claude-code-commands.zip": zipped(lambda p: ".claude/commands/climb/%s.md" % p["slug"], lambda p: command_markdown(p, True)),
        DIST + "/codex-prompts.zip": zipped(lambda p: "prompts/climb-%s.md" % p["slug"], codex_markdown),
        DIST + "/cursor-commands.zip": zipped(lambda p: ".cursor/commands/climb-%s.md" % p["slug"], lambda p: command_markdown(p, False)),
        DIST + "/vscode-prompt-files.zip": zipped(lambda p: ".github/prompts/climb-%s.prompt.md" % p["slug"], vscode_markdown),
        DIST + "/gemini-cli-commands.zip": zipped(lambda p: ".gemini/commands/climb/%s.toml" % p["slug"], gemini_toml),
    }


# ---------------------------------------------------------------- the prompt skill


def prompt_skill_files(prompts):
    """The climb-prompts skill: SKILL.md plus one reference file per task type."""
    description = (
        "The ClimbUK prompt library: %d house prompts for ClimbUK, ClimbGroup and Climb27 work, one set per task type "
        "(analyse, ask, assist, catch up, code, create, design, edit, execute, find, learn, prepare, schedule, understand). "
        "Use it when someone asks for help with a ClimbUK marketing, sales, partnership, events or design task, asks which "
        "prompts exist, or wants a ready-made prompt to start from. Pair it with climb-voice for words and "
        "climb-visual-style for anything visual." % len(prompts)
    )
    lines = [
        "---",
        "name: %s" % PROMPT_SKILL,
        "description: %s" % yaml_string(description),
        "license: Proprietary",
        "metadata:",
        "  owner: ClimbGroup marketing",
        "  version: %s" % yaml_string(VERSION),
        "---",
        "",
        "# ClimbUK prompt library",
        "",
        "Generated from the brand pack. Each prompt is a tested starting point for one ClimbUK job.",
        "",
        "## How to use it",
        "",
        "1. Match the request to a task type and a prompt in the table below.",
        "2. Open `references/<task type>.md` and read that prompt in full.",
        "3. Fill each `{{placeholder}}` from what the person already said; ask for anything still missing, in one message.",
        "4. Do the work the prompt describes, following its brand rules. Load climb-voice for any words and climb-visual-style for anything visual when they are available.",
        "5. Say which prompt you used, so the person can find it again.",
        "",
        "If nothing fits, follow the closest prompt's shape: the task, the inputs, a numbered output and the brand rules.",
        "",
        "## Prompts",
        "",
        "| Task type | Prompt | What it does | Reference |",
        "| --- | --- | --- | --- |",
    ]
    for p in prompts:
        lines.append("| %s | %s | %s | `references/%s.md` |" % (p["task"], p["title"], p["description"], task_folder(p["task"])))
    files = [("SKILL.md", ("\n".join(lines) + "\n").encode())]
    for task in TASK_TYPES:
        ref = ["# %s prompts" % task, ""]
        for p in [p for p in prompts if p["task"] == task]:
            ref += [
                "## %s" % p["title"],
                "",
                p["description"],
                "",
                "Display prompt: %s" % p["display"],
                "",
                "Placeholders: %s" % (", ".join("`{{%s}}`" % n for n in placeholders(p)) or "none"),
                "",
                "```text",
                prompt_text(p),
                "```",
                "",
            ]
        files.append(("references/%s.md" % task_folder(task), ("\n".join(ref).rstrip() + "\n").encode()))
    return files


def skill_payload(name, prompts):
    """(path inside the skill, bytes, executable) for a brand skill or the prompt skill."""
    if name == PROMPT_SKILL:
        return [(path, data, False) for path, data in prompt_skill_files(prompts)]
    out = []
    for relative, full in kits.skill_files(name):
        with open(full, "rb") as handle:
            out.append((relative, handle.read(), os.access(full, os.X_OK)))
    return out


def all_skills():
    return list(kits.BRAND_SKILLS) + [PROMPT_SKILL]


def icons():
    out = []
    for icon in ("color.png", "outline.png"):
        with open(os.path.join(ROOT, COPILOT_ICONS, icon), "rb") as handle:
            out.append((icon, handle.read(), False))
    return out


PLUGIN_DESCRIPTION = (
    "The ClimbUK brand voice, visual style and prompt library for ClimbUK, ClimbGroup and Climb27 work: "
    "write, review, design and plan on brand."
)


def claude_plugin(prompts):
    manifest = {
        "name": PLUGIN,
        "version": VERSION,
        "description": PLUGIN_DESCRIPTION,
        "author": {"name": "ClimbGroup marketing", "email": "marketing@climb-uk.com"},
        "homepage": "https://climb-uk.com/brand",
        "repository": "https://github.com/%s" % kits.REPOSITORY,
        "license": "Proprietary",
        "keywords": ["climbuk", "brand", "prompts", "voice", "design"],
    }
    entries = [(".claude-plugin/plugin.json", (json.dumps(manifest, indent=2) + "\n").encode(), False)]
    for name in all_skills():
        entries += [("skills/%s/%s" % (name, path), data, ex) for path, data, ex in skill_payload(name, prompts)]
    entries += [("commands/%s.md" % p["slug"], command_markdown(p, True), False) for p in prompts]
    return kits.make_zip(entries)


def m365_plugin(prompts):
    manifest = {
        "$schema": "https://developer.microsoft.com/json-schemas/teams/v1.28/MicrosoftTeams.schema.json",
        "manifestVersion": "1.28",
        "version": VERSION,
        "id": M365_PLUGIN_ID,
        "developer": {
            "name": "ClimbGroup",
            "websiteUrl": "https://climb-uk.com/brand",
            "privacyUrl": "https://climb-uk.com/privacy",
            "termsOfUseUrl": "https://climb-uk.com/terms",
        },
        "name": {"short": "ClimbUK Brand", "full": "ClimbUK Brand skills for Copilot Cowork"},
        "description": {
            "short": "Write, design and plan on brand for ClimbUK, ClimbGroup and Climb27.",
            "full": PLUGIN_DESCRIPTION + " Carries the climb-voice, climb-visual-style and climb-prompts skills.",
        },
        "icons": {"color": "color.png", "outline": "outline.png"},
        "accentColor": "#1E0F05",
        "agentSkills": [{"folder": "./skills/%s" % name} for name in all_skills()],
    }
    entries = [("manifest.json", (json.dumps(manifest, indent=2) + "\n").encode(), False)] + icons()
    for name in all_skills():
        entries += [("skills/%s/%s" % (name, path), data, ex) for path, data, ex in skill_payload(name, prompts)]
    return kits.make_zip(entries)


def outputs(prompts=None):
    prompts = load() if prompts is None else prompts
    files = {}
    files.update(copilot_files(prompts))
    files[DIST + "/prompts.json"] = library_json(prompts)
    files[DIST + "/PROMPTS.md"] = library_markdown(prompts)
    files.update(command_zips(prompts))
    # Claude takes a skill zip as one folder with SKILL.md inside it; Cowork wants SKILL.md at the top.
    files["%s/%s.zip" % (PACKAGES, PROMPT_SKILL)] = kits.make_zip(
        [("%s/%s" % (PROMPT_SKILL, path), data, ex) for path, data, ex in skill_payload(PROMPT_SKILL, prompts)]
    )
    for name in all_skills():
        files["%s/cowork/%s.zip" % (PACKAGES, name)] = kits.make_zip(skill_payload(name, prompts))
    files[PACKAGES + "/climbuk-brand-plugin.zip"] = claude_plugin(prompts)
    files[PACKAGES + "/climbuk-brand-plugin-m365.zip"] = m365_plugin(prompts)
    return files


def main(argv):
    prompts = load()
    found = validate(prompts)
    if found:
        print("Prompt problems:\n  " + "\n  ".join(found))
        return 1
    stale = []
    expected = outputs(prompts)
    for path, data in sorted(expected.items()):
        full = os.path.join(ROOT, path)
        current = open(full, "rb").read() if os.path.exists(full) else None
        if current == data:
            continue
        stale.append(path)
        if "--check" not in argv:
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "wb") as handle:
                handle.write(data)
    # A CSV left over from a larger library would be imported twice.
    copilot_dir = os.path.join(ROOT, DIST, "copilot")
    for name in sorted(os.listdir(copilot_dir)) if os.path.isdir(copilot_dir) else []:
        path = "%s/copilot/%s" % (DIST, name)
        if path not in expected:
            stale.append(path)
            if "--check" not in argv:
                os.remove(os.path.join(ROOT, path))
    if "--check" in argv and stale:
        print("Out of date (run: python3 ai/prompts/build_prompts.py):\n  " + "\n  ".join(stale))
        return 1
    print("%d prompts. " % len(prompts) + ("Prompt exports are up to date." if not stale else "Wrote %d files: %s" % (len(stale), ", ".join(stale))))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
