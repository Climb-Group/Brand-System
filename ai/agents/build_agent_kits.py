"""Build the packages and links that put the brand skills into an AI assistant.

    python3 ai/agents/build_agent_kits.py            write everything below
    python3 ai/agents/build_agent_kits.py --check    exit 1 if any of it is out of date
    python3 ai/agents/build_agent_kits.py --icons    redraw the Copilot agent icons (needs Pillow)

It writes:

- ai/packages/<skill>.zip for each brand skill, in the layout an assistant takes
  as a skill upload (one folder with SKILL.md at its top);
- ai/packages/climbuk-brand-skills.zip with both skills, for any agent that
  reads a skills folder;
- ai/packages/climbuk-brand-agent-m365.zip, a Microsoft 365 Copilot agent
  package (app manifest, declarative agent, icons) built from ai/agents/copilot/;
- ai/open-in.json, the "Open in" links and install commands that the brand
  centre shows, so every surface uses the same words and addresses;
- skills-lock.json at the repository root, which lists the house skills synced
  into .agents/skills, so `npx skills add Climb-Group/Brand-System` offers only
  the brand skills.

Zips are deterministic (sorted entries, fixed timestamps), so --check compares
bytes. Standard library only, apart from --icons.
"""
import hashlib
import io
import json
import os
import sys
import urllib.parse
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
REPOSITORY = "Climb-Group/Brand-System"
BRANCH = "main"
BRAND_SKILLS = ("climb-voice", "climb-visual-style")
# Brand skills for one platform only. npx skills offers them with the others; the packages and prompts leave them out,
# because they apply only when the work is on that platform.
PLATFORM_SKILLS = ("climb-odoo-pages",)
SKILLS_DIR = ".agents/skills"
PACKAGES = "ai/packages"
COPILOT = "ai/agents/copilot"
# Never packaged: the confidential copy rules stay out of every public file.
SKIP_NAMES = {"private_rules.py", ".DS_Store"}
SKIP_DIRS = {"__pycache__"}
ZIP_DATE = (2026, 1, 1, 0, 0, 0)

RAW = "https://raw.githubusercontent.com/%s/%s" % (REPOSITORY, BRANCH)
GITHUB = "https://github.com/%s" % REPOSITORY


def skill_url(name):
    return "%s/%s/%s/SKILL.md" % (RAW, SKILLS_DIR, name)


def package_url(file_name):
    return "%s/raw/%s/%s/%s" % (GITHUB, BRANCH, PACKAGES, file_name)


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return handle.read()


def skill_files(name):
    """Every file of a skill, as (path inside the skill, absolute path), sorted."""
    base = os.path.join(ROOT, SKILLS_DIR, name)
    found = []
    for directory, dirs, files in os.walk(base):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for file_name in files:
            if file_name in SKIP_NAMES or file_name.endswith(".pyc"):
                continue
            full = os.path.join(directory, file_name)
            found.append((os.path.relpath(full, base).replace(os.sep, "/"), full))
    return sorted(found)


def make_zip(entries):
    """entries: list of (archive name, bytes, executable). Returns the zip bytes."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data, executable in sorted(entries):
            info = zipfile.ZipInfo(name, ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100755 if executable else 0o100644) << 16
            info.create_system = 3
            archive.writestr(info, data)
    return buffer.getvalue()


def skill_entries(name):
    entries = []
    for relative, full in skill_files(name):
        with open(full, "rb") as handle:
            data = handle.read()
        entries.append(("%s/%s" % (name, relative), data, os.access(full, os.X_OK)))
    return entries


def prompts():
    """The prompt each assistant opens with. One source, so they never drift apart."""
    urls = " and ".join(skill_url(name) for name in BRAND_SKILLS)
    use = (
        "Follow them for everything you write or design for ClimbUK, ClimbGroup and the Climb editions. "
        "Then tell me in one line that you are ready, and ask what I want to make."
    )
    return {
        "chat": "Use the ClimbUK brand in this chat. Read these two brand skills in full first: %s. %s" % (urls, use),
        "claude-code": (
            "Load the climb-voice and climb-visual-style skills from this repository and use them for this session. %s" % use
        ),
        "codex": (
            "Install the ClimbUK brand skills with `npx skills add %s --agent codex --global --yes`, "
            "then load climb-voice and climb-visual-style. %s" % (REPOSITORY, use)
        ),
    }


def open_in():
    q = urllib.parse.quote
    p = prompts()
    return {
        "repository": REPOSITORY,
        "skills": [
            {"name": name, "skill": skill_url(name), "download": package_url("%s.zip" % name)} for name in BRAND_SKILLS
        ],
        "targets": [
            {
                "id": "claude",
                "label": "Open in Claude",
                "url": "https://claude.ai/new?q=" + q(p["chat"], safe=""),
                "how": "Opens a new Claude chat with a prompt that has Claude read both brand skills first.",
                "install": "To keep the skills, add the skill zips in Claude under Settings, Capabilities, Skills.",
            },
            {
                "id": "claude-code",
                "label": "Open in Claude Code",
                "url": "https://claude.ai/code?prompt=%s&repositories=%s" % (q(p["claude-code"], safe=""), q(REPOSITORY, safe="")),
                "how": "Starts a Claude Code session on the brand pack, which loads both skills from the repository.",
                "install": "npx skills add %s --agent claude-code" % REPOSITORY,
            },
            {
                "id": "codex",
                "label": "Open in Codex",
                "url": "codex://threads/new?prompt=" + q(p["codex"], safe=""),
                "how": "Opens a new chat in the Codex app with a prompt that installs both skills and loads them.",
                "install": "npx skills add %s --agent codex" % REPOSITORY,
            },
            {
                "id": "chatgpt",
                "label": "Open in ChatGPT",
                "url": "https://chatgpt.com/?q=" + q(p["chat"], safe=""),
                "how": "Opens a new ChatGPT chat with a prompt that has it read both brand skills first.",
                "install": "To keep the skills, add the skill zips to a ChatGPT project or custom GPT as files.",
            },
            {
                "id": "copilot",
                "label": "Open in Microsoft Copilot",
                "url": "https://copilot.microsoft.com/?q=" + q(p["chat"], safe=""),
                "how": "Opens Copilot with a prompt that has it read both brand skills first.",
                "install": "For Microsoft 365 Copilot, add the ClimbUK Brand agent package as a custom app.",
                "download": package_url("climbuk-brand-agent-m365.zip"),
            },
            {
                "id": "gemini",
                "label": "Open in Gemini",
                "url": "https://gemini.google.com/app",
                "copy": p["chat"],
                "how": "Copies the brand prompt and opens Gemini. Paste it in to start.",
                "install": "To keep the skills, add the skill zips to a Gem as knowledge files.",
            },
            {
                "id": "perplexity",
                "label": "Open in Perplexity",
                "url": "https://www.perplexity.ai/search?q=" + q(p["chat"], safe=""),
                "how": "Opens Perplexity with a prompt that has it read both brand skills first.",
            },
            {
                "id": "grok",
                "label": "Open in Grok",
                "url": "https://grok.com/?q=" + q(p["chat"], safe=""),
                "how": "Opens a new Grok chat with a prompt that has it read both brand skills first.",
            },
            {
                "id": "mistral",
                "label": "Open in Le Chat",
                "url": "https://chat.mistral.ai/chat?q=" + q(p["chat"], safe=""),
                "how": "Opens Mistral Le Chat with a prompt that has it read both brand skills first.",
            },
            {
                "id": "deepseek",
                "label": "Open in DeepSeek",
                "url": "https://chat.deepseek.com/",
                "copy": p["chat"],
                "how": "Copies the brand prompt and opens DeepSeek. Paste it in to start.",
            },
        ],
        "install": {
            "every agent": "npx skills add %s" % REPOSITORY,
            "list the skills": "npx skills add %s --list" % REPOSITORY,
            "all skills": package_url("climbuk-brand-skills.zip"),
        },
    }


def copilot_entries():
    manifest = json.loads(read(COPILOT + "/manifest.json"))
    agent = json.loads(read(COPILOT + "/declarativeAgent.json"))
    instructions = read(COPILOT + "/instructions.md").strip()
    if len(instructions) > 8000:
        raise SystemExit("%s/instructions.md is %d characters; the agent limit is 8000" % (COPILOT, len(instructions)))
    agent["instructions"] = instructions
    entries = [
        ("manifest.json", (json.dumps(manifest, indent=2) + "\n").encode(), False),
        ("declarativeAgent.json", (json.dumps(agent, indent=2) + "\n").encode(), False),
    ]
    for icon in ("color.png", "outline.png"):
        with open(os.path.join(ROOT, COPILOT, icon), "rb") as handle:
            entries.append((icon, handle.read(), False))
    return entries


def skills_lock():
    """House skills synced into .agents/skills. npx skills skips a skill that a lock lists."""
    house = {}
    base = os.path.join(ROOT, SKILLS_DIR)
    for name in sorted(os.listdir(base)):
        if name in BRAND_SKILLS + PLATFORM_SKILLS or not os.path.isfile(os.path.join(base, name, "SKILL.md")):
            continue
        digest = hashlib.sha256()
        for relative, full in sorted(skill_files(name)):
            digest.update(relative.encode())
            with open(full, "rb") as handle:
                digest.update(handle.read())
        house[name] = {
            "source": "Resnovas/.github",
            "sourceType": "github",
            "sourceUrl": "https://github.com/Resnovas/.github.git",
            "skillPath": "templates/.agents/skills/%s/SKILL.md" % name,
            "computedHash": digest.hexdigest(),
        }
    return (json.dumps({"version": 1, "skills": house}, indent=2) + "\n").encode()


def outputs():
    files = {}
    for name in BRAND_SKILLS:
        files["%s/%s.zip" % (PACKAGES, name)] = make_zip(skill_entries(name))
    files[PACKAGES + "/climbuk-brand-skills.zip"] = make_zip([e for name in BRAND_SKILLS for e in skill_entries(name)])
    files[PACKAGES + "/climbuk-brand-agent-m365.zip"] = make_zip(copilot_entries())
    files["ai/open-in.json"] = (json.dumps(open_in(), indent=2) + "\n").encode()
    files["skills-lock.json"] = skills_lock()
    return files


def draw_icons():
    """The li monogram from logos/ClimbUK/ClimbUK_icon-monogram.svg: colour on its Dark Brown tile, outline in white."""
    from PIL import Image, ImageDraw

    tokens = json.loads(read("tokens/brand.tokens.json"))

    def colour(name):
        return tokens["color"]["brand"][name]["$value"]

    # The four bars of the monogram in the SVG's 1000-unit box.
    bars = [(311.5, 150.8, 464.7, 849.9), (535.4, 399.4, 688.6, 755.1), (535.4, 790.7, 688.6, 849.9), (535.4, 150.4, 688.6, 363.8)]

    def scaled(size):
        k = size / 1000.0
        return [tuple(round(v * k) for v in bar) for bar in bars]

    color = Image.new("RGB", (192, 192), colour("dark-brown"))
    draw = ImageDraw.Draw(color)
    for box in scaled(192):
        draw.rectangle(box, fill=colour("orange"))
    color.save(os.path.join(ROOT, COPILOT, "color.png"), optimize=True)

    # At 32px the gaps would round away, so the outline bars sit on whole pixels with 2px gaps.
    outline = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(outline)
    for box in [(8, 4, 13, 27), (17, 4, 22, 10), (17, 13, 22, 23), (17, 26, 22, 27)]:
        draw.rectangle(box, fill=(255, 255, 255, 255))
    outline.save(os.path.join(ROOT, COPILOT, "outline.png"), optimize=True)


def main(argv):
    if "--icons" in argv:
        draw_icons()
    stale = []
    for path, data in sorted(outputs().items()):
        full = os.path.join(ROOT, path)
        current = None
        if os.path.exists(full):
            with open(full, "rb") as handle:
                current = handle.read()
        if current == data:
            continue
        stale.append(path)
        if "--check" not in argv:
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "wb") as handle:
                handle.write(data)
    if "--check" in argv and stale:
        print("Out of date (run: python3 ai/agents/build_agent_kits.py):\n  " + "\n  ".join(stale))
        return 1
    print("Agent kits are up to date." if not stale else "Wrote %d files: %s" % (len(stale), ", ".join(stale)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
