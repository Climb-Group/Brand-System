"""Package the templates and the install scripts into one zip for device management.

Output: templates/dist/Climb-Templates-<version>.zip, laid out as

    Climb-Templates-<version>/
      VERSION
      README.md            (from install/README.md)
      payload/fonts/       Montserrat and Open Sans TTF + licences
      payload/office/<Brand>/   .dotx .xltx .potx
      payload/themes/      .thmx + Theme Colors/ + Theme Fonts/
      payload/libreoffice/<Brand>/
      payload/video/       Resolve .drfx, LUT, Premiere XML, stills, captions
      windows/ macos/ linux/

The motion clips are not included (600 MB); they ship as their own release download.
"""
import os
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.dirname(HERE)
INSTALL = os.path.join(TPL, "install")
BRANDS = ("ClimbUK", "ClimbGroup", "Climb27")


def version():
    with open(os.path.join(INSTALL, "VERSION")) as f:
        return f.read().strip()


def files(root, skip=()):
    for d, dirs, fs in os.walk(root):
        dirs[:] = sorted(x for x in dirs if x not in skip)
        for f in sorted(fs):
            yield os.path.join(d, f)


def entries():
    """Yield (source path, path inside payload/)."""
    office = os.path.join(TPL, "office")
    for p in files(os.path.join(office, "_shared", "fonts")):
        yield p, "fonts/" + os.path.basename(p)
    for b in BRANDS:
        for app in ("word", "excel", "powerpoint"):
            for p in files(os.path.join(office, b, app)):
                yield p, "office/%s/%s" % (b, os.path.basename(p))
        for p in files(os.path.join(office, "libreoffice", b)):
            yield p, "libreoffice/%s/%s" % (b, os.path.basename(p))
    theme = os.path.join(office, "_shared", "office-theme")
    for p in files(theme):
        yield p, "themes/" + os.path.relpath(p, theme).replace(os.sep, "/")
    video = os.path.join(TPL, "video")
    for b in BRANDS:
        for p in files(os.path.join(video, b, "davinci-resolve"), skip=("setting-files",)):
            yield p, "video/resolve/" + os.path.basename(p)
        for p in files(os.path.join(video, b, "premiere-pro")):
            yield p, "video/premiere/" + os.path.basename(p)
        for p in files(os.path.join(video, b, "stills")):
            yield p, "video/stills/%s/%s" % (b, os.path.basename(p))
    for p in files(os.path.join(video, "_shared", "luts")):
        if p.endswith(".cube"):
            yield p, "video/luts/" + os.path.basename(p)
    for p in files(os.path.join(video, "_shared", "captions")):
        yield p, "video/captions/" + os.path.basename(p)
    for p in files(os.path.join(video, "_shared", "stills")):
        yield p, "video/stills/_shared/" + os.path.basename(p)


def zinfo(name, mode):
    zi = zipfile.ZipInfo(name, date_time=(2026, 10, 10, 0, 0, 0))
    zi.external_attr = (0o100000 | mode) << 16
    zi.compress_type = zipfile.ZIP_DEFLATED
    return zi


def main():
    v = version()
    top = "Climb-Templates-%s/" % v
    out_dir = os.path.join(TPL, "dist")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "Climb-Templates-%s.zip" % v)
    n = 0
    with zipfile.ZipFile(out, "w") as z:
        def add(src, arc, mode=0o644):
            nonlocal n
            with open(src, "rb") as f:
                data = f.read()
            if src.startswith(INSTALL):
                data = data.replace(b"@VERSION@", v.encode())
            z.writestr(zinfo(top + arc, mode), data)
            n += 1
        add(os.path.join(INSTALL, "VERSION"), "VERSION")
        add(os.path.join(INSTALL, "README.md"), "README.md")
        for osdir in ("windows", "macos", "linux"):
            for p in files(os.path.join(INSTALL, osdir)):
                mode = 0o755 if p.endswith(".sh") else 0o644
                add(p, osdir + "/" + os.path.relpath(p, os.path.join(INSTALL, osdir)).replace(os.sep, "/"), mode)
        seen = set()
        for src, arc in entries():
            if arc in seen:
                sys.exit("duplicate payload path: " + arc)
            seen.add(arc)
            add(src, "payload/" + arc)
    print("%s: %d files, %.1f MB" % (out, n, os.path.getsize(out) / 1e6))
    if len(sys.argv) > 1:
        shutil.copy2(out, sys.argv[1])
        print("copied to", sys.argv[1])


if __name__ == "__main__":
    main()
