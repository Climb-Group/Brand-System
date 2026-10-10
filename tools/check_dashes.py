"""Fail when a tracked text file contains an em dash or an en dash. Use a hyphen-minus instead.

    python3 tools/check_dashes.py
"""
import subprocess
import sys

SUFFIXES = (".md", ".py", ".mjs", ".js", ".json", ".yml", ".css", ".scss", ".html", ".svg", ".txt")
DASHES = (chr(0x2013), chr(0x2014))
# Third-party or generated output that carries its own text (the component CSS bundles Bootstrap).
SKIP = ("components/hub/",)


def main():
    files = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True).stdout.split("\n")
    bad = 0
    for name in files:
        if not name.endswith(SUFFIXES) or name.startswith(SKIP):
            continue
        try:
            lines = open(name, encoding="utf-8").read().split("\n")
        except (OSError, UnicodeDecodeError):
            continue
        for n, line in enumerate(lines, 1):
            if any(d in line for d in DASHES):
                print("%s:%d: em or en dash" % (name, n))
                bad += 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
