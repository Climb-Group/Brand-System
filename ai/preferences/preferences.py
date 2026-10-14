#!/usr/bin/env python3
"""Keep one person's working preferences on their own machine.

Personal preferences (how someone likes an agent to work with them) never go
into git or a shared memory. They live in one Markdown file in the person's
local app data folder, and a local Graphify graph indexes it next to this
repository's graph, so an agent can query both together. No git or GitHub
account is needed.

Usage:
    python3 ai/preferences/preferences.py path
    python3 ai/preferences/preferences.py add <topic> "<preference>"
    python3 ai/preferences/preferences.py show
    python3 ai/preferences/preferences.py index
    python3 ai/preferences/preferences.py query "<question>"

Set CLIMB_PREFERENCES_DIR to use another folder. The folder is never inside
a synced folder by default: on Windows it is under %LOCALAPPDATA%, elsewhere
under $XDG_DATA_HOME or ~/.local/share.
"""

import datetime
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
WRAPPER = os.path.join(REPO, "tools", "graphify", "graphify")
FILE_NAME = "preferences.md"
TITLE = "# My preferences for agents"
PERSONAL_TAG = "personal-preferences"
REPO_TAG = "climb-brand-system"


def folder(env=None, platform=None):
    """The local folder that holds the preferences file."""
    env = os.environ if env is None else env
    platform = sys.platform if platform is None else platform
    if env.get("CLIMB_PREFERENCES_DIR"):
        return env["CLIMB_PREFERENCES_DIR"]
    if platform.startswith("win"):
        base = env.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), "AppData", "Local")
    else:
        base = env.get("XDG_DATA_HOME") or os.path.join(os.path.expanduser("~"), ".local", "share")
    return os.path.join(base, "climb-preferences")


def topic_heading(topic):
    """A topic as a Markdown heading: 'reply style' becomes '## Reply style'."""
    words = re.sub(r"[^A-Za-z0-9 -]+", " ", topic).split()
    if not words:
        raise ValueError("a topic needs at least one letter or number")
    text = " ".join(words)
    return "## " + text[0].upper() + text[1:]


def add_entry(text, topic, preference, today):
    """Return the file text with a dated preference added under its topic."""
    preference = " ".join(preference.split())
    if not preference:
        raise ValueError("the preference is empty")
    heading = topic_heading(topic)
    line = "- %s: %s" % (today.isoformat(), preference)
    lines = text.splitlines() if text.strip() else [TITLE]
    if line in lines:
        return "\n".join(lines) + "\n"
    if heading not in lines:
        if lines[-1].strip():
            lines.append("")
        lines += [heading, line]
        return "\n".join(lines) + "\n"
    start = lines.index(heading) + 1
    end = start
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    while end > start and not lines[end - 1].strip():
        end -= 1
    lines.insert(end, line)
    return "\n".join(lines) + "\n"


def graphify(*args):
    """Run Graphify through the house wrapper, which keeps its state per user."""
    return subprocess.call(["sh", WRAPPER, "--"] + list(args))


def index(where):
    """Rebuild the personal graph and register it, with this repository's graph."""
    code = graphify("update", where)
    if code:
        return code
    code = graphify("global", "add", os.path.join(where, "graphify-out", "graph.json"), "--as", PERSONAL_TAG)
    if code:
        return code
    return graphify("global", "add", os.path.join(REPO, "graphify-out", "graph.json"), "--as", REPO_TAG)


def main(argv):
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(__doc__.strip())
        return 0
    command, rest = argv[0], argv[1:]
    where = folder()
    path = os.path.join(where, FILE_NAME)
    if command == "path":
        print(path)
        return 0
    if command == "show":
        if os.path.exists(path):
            with open(path, encoding="utf-8") as handle:
                sys.stdout.write(handle.read())
        return 0
    if command == "add":
        if len(rest) != 2:
            print('usage: preferences.py add <topic> "<preference>"', file=sys.stderr)
            return 2
        os.makedirs(where, exist_ok=True)
        old = ""
        if os.path.exists(path):
            with open(path, encoding="utf-8") as handle:
                old = handle.read()
        try:
            new = add_entry(old, rest[0], rest[1], datetime.date.today())
        except ValueError as error:
            print("preferences: %s" % error, file=sys.stderr)
            return 2
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(new)
        print("Saved to %s" % path)
        return index(where)
    if command == "index":
        if not os.path.exists(path):
            print("preferences: nothing saved yet at %s" % path, file=sys.stderr)
            return 1
        return index(where)
    if command == "query":
        if len(rest) != 1:
            print('usage: preferences.py query "<question>"', file=sys.stderr)
            return 2
        global_graph = subprocess.check_output(["sh", WRAPPER, "--", "global", "path"], text=True).strip()
        return graphify("query", rest[0], "--graph", global_graph)
    print("preferences: unknown command %r" % command, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
