"""Keep the Brand System library in the Brand Centre and this repository in step.

The library is where people edit the pack. GitHub runs this script, so no computer has to be on.

    python3 tools/brand_centre/sync.py pull       # library edits -> the working tree (the workflow commits them)
    python3 tools/brand_centre/sync.py push       # main -> the library, after every push to main
    python3 tools/brand_centre/sync.py restore    # put main back over library edits not in git
    python3 tools/brand_centre/sync.py status     # list library edits, change nothing

The script talks to the library through rclone. BRAND_CENTRE_REMOTE names the remote (default ":onedrive:",
set up from the RCLONE_ONEDRIVE_* variables the workflow passes). After each push it saves a manifest of the
library's own file hashes in .brand-centre-sync/manifest.json in the library, with the commit it matches. An
edit is then any library file whose hash differs from the manifest, any file the manifest does not list, and
any listed file that has gone. Comparing against the library's own hashes, never against git, matters because
SharePoint rewrites some files as it stores them (it adds metadata to HTML and Office files), so their bytes
never match the repository even when nobody has touched them.

internal/ never leaves the Brand Centre: it lives in another library, and every listing here excludes it too.
"""
import json
import os
import subprocess
import sys
import tempfile

REMOTE = os.environ.get("BRAND_CENTRE_REMOTE", ":onedrive:")
STATE_DIR = ".brand-centre-sync"
MANIFEST = STATE_DIR + "/manifest.json"
# GitHub refuses files over 100 MB; a bigger file in the library stays there and is reported.
MAX_BYTES = 95 * 1024 * 1024
# Never synced in either direction: team-only material, the sync's own state, and the files apps leave behind.
EXCLUDES = (
    "/internal/**", "/%s/**" % STATE_DIR, "/.git/**", "/.github/**",
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
    name = path.rsplit("/", 1)[-1]
    if path.split("/", 1)[0] in ("internal", STATE_DIR, ".git", ".github"):
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


def find_edits(manifest_files, listing):
    """Compare the library with the manifest saved at the last push.

    Returns (changed, deleted): paths added or changed in the library, and paths removed from it. Pure, so the
    tests can run it without a library.
    """
    changed = sorted(p for p, f in listing.items() if manifest_files.get(p, {}).get("hash") != f["hash"])
    deleted = sorted(p for p in manifest_files if p not in listing and not excluded(p))
    return changed, deleted


def plan_push(manifest_commit, diff_lines, tracked):
    """Decide what a push sends, from `git diff --name-status <manifest commit> HEAD` and `git ls-files`.

    Returns (upload, remove). With no manifest commit (the first push, or a lost manifest) every tracked file
    is uploaded. Pure, so the tests can run it.
    """
    tracked = [p for p in tracked if p and not excluded(p)]
    if not manifest_commit:
        return sorted(tracked), []
    upload, remove = set(), set()
    for line in diff_lines:
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status, paths = parts[0], parts[1:]
        if status.startswith("R"):  # a rename removes the old path and adds the new one
            remove.add(paths[0])
            upload.add(paths[1])
        elif status.startswith("D"):
            remove.add(paths[0])
        else:
            upload.add(paths[-1])
    keep = set(tracked)
    return (sorted(p for p in upload if p in keep),
            sorted(p for p in remove if not excluded(p) and p not in keep))


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
        print("No manifest in the library yet: run a push first.")
        return 0
    listing = remote_listing()
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


def push(restore=False):
    """Send main to the library and save a fresh manifest.

    Library edits not yet in git keep their manifest entry, so the next pull still finds them, unless main
    changed the same file (main wins; the workflow commits library edits before it pushes, so this only happens
    when that commit was refused) or restore is set (main goes back over every edit).
    """
    head = git("rev-parse", "HEAD").strip()
    manifest = read_manifest()
    old_files = manifest.get("files", {})
    tracked = git("ls-files").split("\n")
    base = manifest.get("commit")
    if base and subprocess.run(["git", "cat-file", "-e", base + "^{commit}"], stderr=subprocess.DEVNULL).returncode:
        print("The manifest's commit is not in this history: sending every file.")
        base = None
    diff = git("diff", "--name-status", "--no-renames", base, "HEAD").split("\n") if base else []
    upload, remove = plan_push(base, diff, tracked)
    listing = remote_listing() if manifest.get("commit") else {}
    pending_changed, pending_deleted = find_edits(old_files, listing) if listing else ([], [])
    if restore:
        keep = set(p for p in tracked if p and not excluded(p))
        upload = sorted(set(upload) | (set(pending_changed) & keep) | (set(pending_deleted) & keep))
        remove = sorted(set(remove) | (set(pending_changed) - keep))
    if upload:
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
            fh.write("\n".join(upload) + "\n")
        try:
            rclone("copy", "--files-from", fh.name, "--checksum", ".", REMOTE)
        finally:
            os.unlink(fh.name)
    for path in remove:
        subprocess.run(["rclone", "--quiet", "deletefile", REMOTE + path])
    listing = remote_listing()
    sent = set(upload) | set(remove)
    files = {}
    for path, entry in listing.items():
        if path in pending_changed and path not in sent and path in old_files:
            files[path] = old_files[path]  # a library edit not in git yet: keep it findable
        elif path in pending_changed and path not in sent:
            continue  # a file someone added in the library: still an edit
        else:
            files[path] = entry
    for path in pending_deleted:
        if path not in sent and path in old_files:
            files[path] = old_files[path]  # a library delete not in git yet: keep it findable
    write_manifest(head, files)
    print("Sent to the library: %d uploaded, %d removed, at %s." % (len(upload), len(remove), head[:7]))
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
    if mode == "push":
        return push()
    if mode == "restore":
        return push(restore=True)
    if mode == "status":
        return status()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
