"""Build and publish the photo library that the media kit build adds to its exports kit.

    python3 photos/_build/photo_library.py build   --source DIR [--exclude FILE] --out climb-photo-library.zip
    python3 photos/_build/photo_library.py publish --source DIR [--exclude FILE] [--force]
    python3 photos/_build/photo_library.py install-timer --source DIR [--exclude FILE]

The source folder holds one subfolder per candid group, each with JPEG
originals (3840 px). The exclude file lists photos that must never be
published, one `group/filename` per line (`#` starts a comment); by default
it is media-kit-exclude.txt next to the source folder.

build    writes the zip: group folders at the top, JPEGs stored as they are,
         sorted, without the excluded photos.
publish  builds the zip, and when the library changed since the last upload
         (a fingerprint of names, sizes and times kept with the release)
         uploads it to the photo-library release with the exclude list, then
         starts the media kit workflow. Needs the GitHub CLI, signed in.
         The release is public, so a photo that was not in the last upload
         holds the whole publish (exit 2, with a desktop notification) until
         it is screened and publish runs with --approve-new. Removing photos
         or adding exclusions goes out on its own.
install-timer
         writes a systemd user timer that runs publish every hour, so a
         change to the folder reaches the media kit without a command.

Standard library only. The photos stay on the machine that holds them until
publish uploads them; nothing here reads or writes the repository's photos/.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

REPOSITORY = "Climb-Group/Brand-System"
TAG = "photo-library"
ZIP_NAME = "climb-photo-library.zip"
FINGERPRINT_NAME = "climb-photo-library.json"
EXCLUDE_NAME = "media-kit-exclude.txt"
WORKFLOW = "media-kit.yml"
PHOTO_TYPES = (".jpg", ".jpeg")
UNIT = "climb-photo-library"


class LibraryError(Exception):
    pass


def read_excludes(path):
    """The `group/filename` lines of an exclude file, as a set."""
    if not path or not os.path.isfile(path):
        return set()
    names = set()
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.split("#", 1)[0].strip().replace("\\", "/")
            if line:
                names.add(line)
    return names


def library_files(source, excludes):
    """Every photo to publish as (archive name, path), sorted, and the excluded names that were found."""
    if not os.path.isdir(source):
        raise LibraryError("no photo folder at %s" % source)
    found, skipped = [], set()
    for group in sorted(os.listdir(source)):
        folder = os.path.join(source, group)
        if group.startswith(".") or not os.path.isdir(folder):
            continue
        for name in sorted(os.listdir(folder)):
            if name.startswith(".") or not name.lower().endswith(PHOTO_TYPES):
                continue
            arcname = "%s/%s" % (group, name)
            if arcname in excludes:
                skipped.add(arcname)
                continue
            found.append((arcname, os.path.join(folder, name)))
    if not found:
        raise LibraryError("no photos in %s (expected one folder per group)" % source)
    return found, skipped


def fingerprint(files, excludes):
    """Changes when a photo is added, removed, replaced or newly excluded."""
    digest = hashlib.sha256()
    for arcname, path in files:
        info = os.stat(path)
        digest.update(("%s\0%d\0%d\n" % (arcname, info.st_size, info.st_mtime_ns)).encode())
    for name in sorted(excludes):
        digest.update(("exclude\0%s\n" % name).encode())
    return digest.hexdigest()


def write_zip(files, out):
    with zipfile.ZipFile(out, "w", zipfile.ZIP_STORED) as archive:
        for arcname, path in files:
            archive.write(path, arcname)
    with zipfile.ZipFile(out) as archive:
        if archive.testzip() is not None:
            raise LibraryError("%s failed its integrity test" % out)


def build(source, exclude, out):
    excludes = read_excludes(exclude)
    files, skipped = library_files(source, excludes)
    missing = sorted(excludes - skipped)
    write_zip(files, out)
    names = set(zipfile.ZipFile(out).namelist())
    leaked = sorted(names & excludes)
    if leaked:
        raise LibraryError("excluded photos ended up in the zip: %s" % ", ".join(leaked))
    return {"photos": len(files), "excluded": len(skipped), "missing_excludes": missing,
            "bytes": os.path.getsize(out), "fingerprint": fingerprint(files, excludes)}


def gh(*args, check=True, capture=True):
    if not shutil.which("gh"):
        raise LibraryError("the GitHub CLI (gh) is not installed")
    result = subprocess.run(["gh", *args], capture_output=capture, text=True)
    if check and result.returncode != 0:
        raise LibraryError("gh %s failed: %s" % (" ".join(args[:2]), (result.stderr or "").strip()))
    return result


def published_state(repo, workdir):
    """The fingerprint and photo names of the last upload, or (None, None) before the first."""
    result = gh("release", "download", TAG, "--repo", repo, "--pattern", FINGERPRINT_NAME,
                "--dir", workdir, "--clobber", check=False)
    path = os.path.join(workdir, FINGERPRINT_NAME)
    if result.returncode != 0 or not os.path.isfile(path):
        return None, None
    with open(path, encoding="utf-8") as handle:
        state = json.load(handle)
    names = state.get("names")
    return state.get("fingerprint"), set(names) if names is not None else None


def notify(title, body):
    """A desktop notification where one is available; the message is printed either way."""
    print("%s: %s" % (title, body), file=sys.stderr)
    if shutil.which("notify-send"):
        subprocess.run(["notify-send", "--app-name=ClimbUK", title, body], check=False)


def publish(source, exclude, repo, force=False, run_workflow=True, approve_new=False):
    excludes = read_excludes(exclude)
    files, _ = library_files(source, excludes)
    current = fingerprint(files, excludes)
    with tempfile.TemporaryDirectory(prefix="climb-photo-library-") as workdir:
        published, reviewed = published_state(repo, workdir)
        if not force and published == current:
            print("photo library unchanged since the last upload; nothing to do")
            return 0
        # The release is public: a photo nobody has screened is held until someone approves it.
        new = sorted(name for name, _ in files if reviewed is None or name not in reviewed)
        if new and not approve_new:
            notify("Photo library held for review",
                   "%d new photo(s) not yet published: %s. Exclude any that must stay private in %s, "
                   "then run publish with --approve-new." % (len(new), ", ".join(new[:10]) + (" ..." if len(new) > 10 else ""), EXCLUDE_NAME))
            return 2
        out = os.path.join(workdir, ZIP_NAME)
        summary = build(source, exclude, out)
        state = {k: summary[k] for k in ("fingerprint", "photos", "excluded", "bytes")}
        state["names"] = [name for name, _ in files]
        with open(os.path.join(workdir, FINGERPRINT_NAME), "w", encoding="utf-8") as handle:
            json.dump(state, handle, indent=2)
        if gh("release", "view", TAG, "--repo", repo, check=False).returncode != 0:
            gh("release", "create", TAG, "--repo", repo, "--title", "Photo library", "--latest=false",
               "--notes", "Climb26 candid photo library for the media kit build, with the excluded "
               "photos left out. Replaced automatically when the library changes.")
        assets = [out, os.path.join(workdir, FINGERPRINT_NAME)]
        if exclude and os.path.isfile(exclude):
            staged = os.path.join(workdir, EXCLUDE_NAME)
            shutil.copyfile(exclude, staged)
            assets.append(staged)
        gh("release", "upload", TAG, *assets, "--repo", repo, "--clobber", capture=False)
        print("uploaded %d photos (%d excluded, %.0f MB) to %s" % (
            summary["photos"], summary["excluded"], summary["bytes"] / 1e6, TAG))
        for name in summary["missing_excludes"]:
            print("warning: %s is in the exclude list but not in the folder" % name)
        if run_workflow:
            gh("workflow", "run", WORKFLOW, "--repo", repo, "--ref", "main")
            print("started the media kit workflow")
    return 0


def install_timer(source, exclude, repo):
    if not sys.platform.startswith("linux"):
        raise LibraryError("install-timer writes systemd units; on other systems run publish from cron or launchd")
    units = os.path.expanduser("~/.config/systemd/user")
    os.makedirs(units, exist_ok=True)
    command = [sys.executable, os.path.abspath(__file__), "publish", "--source", os.path.abspath(source), "--repo", repo]
    if exclude:
        command += ["--exclude", os.path.abspath(exclude)]
    exec_start = " ".join('"%s"' % part for part in command)
    with open(os.path.join(units, UNIT + ".service"), "w", encoding="utf-8") as handle:
        handle.write("[Unit]\nDescription=Publish the ClimbUK photo library when it changes\n"
                     "After=network-online.target\n\n[Service]\nType=oneshot\nExecStart=%s\n" % exec_start)
    with open(os.path.join(units, UNIT + ".timer"), "w", encoding="utf-8") as handle:
        handle.write("[Unit]\nDescription=Check the ClimbUK photo library every hour\n\n"
                     "[Timer]\nOnCalendar=hourly\nPersistent=true\n\n[Install]\nWantedBy=timers.target\n")
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "--user", "enable", "--now", UNIT + ".timer"], check=True)
    print("installed %s.timer; see it with: systemctl --user list-timers %s.timer" % (UNIT, UNIT))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("build", "publish", "install-timer"):
        p = sub.add_parser(name)
        p.add_argument("--source", required=True, help="folder with one subfolder of JPEGs per candid group")
        p.add_argument("--exclude", help="photos never to publish, one group/filename per line "
                       "(default: %s next to the source folder)" % EXCLUDE_NAME)
        p.add_argument("--repo", default=REPOSITORY)
        if name == "build":
            p.add_argument("--out", default=ZIP_NAME)
        if name == "publish":
            p.add_argument("--force", action="store_true", help="upload even when nothing changed")
            p.add_argument("--no-workflow", action="store_true", help="do not start the media kit workflow")
            p.add_argument("--approve-new", action="store_true",
                           help="publish photos that were not in the last upload (after screening them)")
    args = parser.parse_args(argv)
    exclude = args.exclude
    if exclude is None:
        default = os.path.join(os.path.dirname(os.path.abspath(args.source)), EXCLUDE_NAME)
        exclude = default if os.path.isfile(default) else None
    try:
        if args.command == "build":
            summary = build(args.source, exclude, args.out)
            print(json.dumps(summary, indent=2))
            return 0
        if args.command == "publish":
            return publish(args.source, exclude, args.repo, args.force, not args.no_workflow, args.approve_new)
        return install_timer(args.source, exclude, args.repo)
    except LibraryError as error:
        print("photo_library: %s" % error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
