"""Bring edits made in the Brand System library in the Brand Centre into this repository.

The library is the source of truth (Jonathan, 2026-10-25): the sync only pulls. GitHub runs this script, so no
computer has to be on.

    python3 tools/brand_centre/sync.py pull       # library edits -> the working tree (the workflow commits them)
    python3 tools/brand_centre/sync.py mark       # after the commit lands: record the library as matching main
    python3 tools/brand_centre/sync.py status     # list library edits, change nothing
    python3 tools/brand_centre/sync.py seed       # copy main into the library, by hand only (see below)

The script talks to the library through rclone. BRAND_CENTRE_REMOTE names the remote (default ":onedrive:",
set up from the RCLONE_ONEDRIVE_* variables the workflow passes). It keeps a manifest of the library's own file
hashes in .brand-centre-sync/manifest.json in the library. An edit is any library file whose hash differs from
the manifest, any file the manifest does not list, and any listed file that has gone. Comparing against the
library's own hashes, never against git, matters because SharePoint rewrites some files as it stores them (it
adds metadata to HTML and Office files), so their bytes never match the repository even when nobody has touched
them. `pull` saves the listing it compared, and `mark` writes that listing as the new manifest once the edits are
on main, so an edit made in the library while a run is going is still found by the next run.

`seed` is the only command that writes pack files to the library. It is for a new or emptied library, or a lost
manifest, and is never run automatically.

internal/ never leaves the Brand Centre. Team-only material and the internal tools that extend the brand system
live in internal folders in the Brand System library, beside the pack: at the top, or beside the part a tool
extends (templates/internal/). Every listing here leaves out any folder named internal, at any depth, and pull
also skips any file .gitignore keeps out of the repository.
"""
import json
import os
import subprocess
import sys
import tempfile

REMOTE = os.environ.get("BRAND_CENTRE_REMOTE", ":onedrive:")
STATE_DIR = ".brand-centre-sync"
MANIFEST = STATE_DIR + "/manifest.json"
# What `pull` compared, kept for `mark`: on the runner, outside the checkout.
LISTING = os.environ.get("BRAND_CENTRE_LISTING", os.path.join(tempfile.gettempdir(), "brand-centre-listing.json"))
# GitHub refuses files over 100 MB; a bigger file in the library stays there and is reported.
MAX_BYTES = 95 * 1024 * 1024
# Never synced in either direction: team-only material, the sync's own state, and the files apps leave behind.
EXCLUDES = (
    "internal/**", "/%s/**" % STATE_DIR, "/.git/**", "/.github/**",
    "~$*", ".~lock.*#", ".DS_Store", "Thumbs.db", "desktop.ini", "*.tmp",
)
FILTER_ARGS = [arg for pattern in EXCLUDES for arg in ("--exclude", pattern)]


def rclone(*args, capture=False, input_text=None):
    """Run rclone quietly. File names stay out of the log unless capture is set."""
    out = subprocess.run(["rclone", "--quiet", *args], check=True, text=True, input=input_text,
                         stdout=subprocess.PIPE if capture else None)
    return out.stdout if capture else ""


def git(*args):
    return subprocess.run(["git", *args], check=True, text=True, stdout=subprocess.PIPE).stdout


def excluded(path):
    """True for a path the sync must never touch (mirrors EXCLUDES)."""
    parts = path.split("/")
    name = parts[-1]
    if "internal" in parts[:-1] or parts[0] in (STATE_DIR, ".git", ".github"):
        return True
    return (name.startswith("~$") or (name.startswith(".~lock.") and name.endswith("#"))
            or name in (".DS_Store", "Thumbs.db", "desktop.ini") or name.endswith(".tmp"))


def file_hash(entry):
    hashes = entry.get("Hashes") or {}
    return hashes.get("quickxor") or next(iter(sorted(hashes.values())), "") or "size:%d" % entry.get("Size", 0)


def remote_listing():
    """{path: {"hash", "size"}} for every file in the library, exclusions left out."""
    raw = rclone("lsjson", "--recursive", "--files-only", "--hash", *FILTER_ARGS, REMOTE, capture=True)
    return {e["Path"]: {"hash": file_hash(e), "size": e.get("Size", 0)}
            for e in json.loads(raw or "[]") if not excluded(e["Path"])}


def read_manifest():
    try:
        return json.loads(rclone("cat", REMOTE + MANIFEST, capture=True) or "{}")
    except subprocess.CalledProcessError:
        return {}


def write_manifest(commit, files):
    body = json.dumps({"commit": commit, "files": files}, indent=1, sort_keys=True)
    rclone("rcat", REMOTE + MANIFEST, input_text=body)


def save_listing(listing, path=None):
    with open(path or LISTING, "w") as fh:
        json.dump(listing, fh, sort_keys=True)


def load_listing(path=None):
    with open(path or LISTING) as fh:
        return json.load(fh)


def find_edits(manifest_files, listing):
    """Compare the library with the manifest saved at the last mark or seed.

    Returns (changed, deleted): paths added or changed in the library, and paths removed from it. Pure, so the
    tests can run it without a library.
    """
    changed = sorted(p for p, f in listing.items() if manifest_files.get(p, {}).get("hash") != f["hash"])
    deleted = sorted(p for p in manifest_files if p not in listing and not excluded(p))
    return changed, deleted


def seed_files(tracked):
    """The tracked files a seed copies to the library: everything but the excluded paths. Pure, for the tests."""
    return sorted(p for p in tracked if p and not excluded(p))


def ignored_by_git(paths):
    """The paths .gitignore keeps out of the repository (private rules, build output)."""
    if not paths:
        return set()
    out = subprocess.run(["git", "check-ignore", "--no-index", "--stdin"], text=True, input="\n".join(paths),
                         stdout=subprocess.PIPE)
    return set(filter(None, out.stdout.split("\n")))


def pull():
    """Copy library edits into the working tree. Prints how many files changed; the workflow commits them."""
    manifest = read_manifest()
    if not manifest.get("commit"):
        print("No manifest in the library yet: seed it first.")
        return 0
    listing = remote_listing()
    save_listing(listing)
    changed, deleted = find_edits(manifest.get("files", {}), listing)
    skipped_ignored = ignored_by_git(changed)
    too_big = [p for p in changed if listing[p]["size"] > MAX_BYTES]
    changed = [p for p in changed if p not in skipped_ignored and p not in too_big]
    if changed:
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
            fh.write("\n".join(changed) + "\n")
        try:
            rclone("copy", "--files-from", fh.name, REMOTE, ".")
        finally:
            os.unlink(fh.name)
    for path in deleted:
        if os.path.exists(path):
            git("rm", "--quiet", "--", path)
    print("Library edits: %d changed, %d removed." % (len(changed), len(deleted)))
    if skipped_ignored:
        print("Left in the library, kept out of git by .gitignore: %d file(s)." % len(skipped_ignored))
    if too_big:
        print("Left in the library, over GitHub's file size limit: %s" % ", ".join(too_big))
    return 0


def mark():
    """Record the library as matching main: the listing `pull` compared becomes the manifest.

    Run only after the edits that pull found are on main. Files pull left in the library (git-ignored or too
    big) are recorded too, so they are reported once, not on every run.
    """
    if not os.path.exists(LISTING):
        return 0  # pull found no manifest, so there is nothing to record
    head = git("rev-parse", "HEAD").strip()
    write_manifest(head, load_listing())
    print("The library is recorded as matching %s." % head[:7])
    return 0


def seed():
    """Copy main into the library and save a fresh manifest. By hand only: for a new or emptied library, or a
    lost manifest. Only files the library lacks are copied: a file already there is never replaced, because the
    library is the source of truth, and because SharePoint refuses to replace the HTML and Office files it has
    rewritten ("upload session was not found", "Item not found")."""
    head = git("rev-parse", "HEAD").strip()
    upload = seed_files(git("ls-files").split("\n"))
    if upload:
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
            fh.write("\n".join(upload) + "\n")
        try:
            # SharePoint adds metadata to HTML and Office files as it stores them, so the stored size and hash
            # never match what was sent; without these flags rclone calls every such upload corrupted.
            rclone("copy", "--files-from", fh.name, "--ignore-existing", "--ignore-size", "--ignore-checksum", ".",
                   REMOTE)
        finally:
            os.unlink(fh.name)
    write_manifest(head, remote_listing())
    print("Copied main to the library: %d file(s), at %s." % (len(upload), head[:7]))
    return 0


def status():
    manifest = read_manifest()
    if not manifest.get("commit"):
        print("No manifest in the library yet.")
        return 0
    changed, deleted = find_edits(manifest.get("files", {}), remote_listing())
    print("Library matches %s. Edits: %d changed, %d removed." % (manifest["commit"][:7], len(changed), len(deleted)))
    for path in changed:
        print("  changed  %s" % path)
    for path in deleted:
        print("  removed  %s" % path)
    return 0


def main(argv):
    mode = argv[1] if len(argv) > 1 else ""
    if mode == "pull":
        return pull()
    if mode == "mark":
        return mark()
    if mode == "seed":
        return seed()
    if mode == "status":
        return status()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
