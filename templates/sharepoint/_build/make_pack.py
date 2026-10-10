"""Write pages.json, copy.txt and the page guide for the SharePoint brand centre pack. Usage: make_pack.py PACK OUT"""
import html, json, re, shutil, sys
from pathlib import Path
from pages import PAGES, NAV

PACK, OUT = Path(sys.argv[1]), Path(sys.argv[2])
HERE = Path(__file__).parent

data = {"nav": [{"label": l, "pages": p} for l, p in NAV], "pages": []}
for slug, pg in PAGES.items():
    data["pages"].append({
        "slug": slug, "title": pg["title"], "description": pg["description"],
        "banner": "climbuk_sharepoint-banner_%s_1920x1080.jpg" % slug,
        "sections": [{"layout": l, "emphasis": e, "columns": cols} for l, e, cols in pg["sections"]],
    })
(OUT / "pages.json").write_text(json.dumps(data, indent=1) + "\n")


def text(h):
    h = re.sub(r"</(h2|h3|p|li)>", "\n", h)
    return html.unescape(re.sub(r"<[^>]+>", "", h))


copy = []
for pg in PAGES.values():
    copy += [pg["title"], pg["description"]] + [text(c) for _, _, cols in pg["sections"] for c in cols]
    copy += ["%s. %s" % (t, d) for t, _, d in (pg["hero"] or [])]
(OUT / "copy.txt").write_text("\n".join(copy))

# Page guide: one table per page for the parts added by hand.
lines = []
for slug, pg in PAGES.items():
    lines.append("### %s (`%s.aspx`)\n" % (pg["title"], slug))
    lines.append("%s\n" % pg["description"])
    if pg["hero"]:
        lines.append("**Hero web part** (full width section at the top, layout Tiles, five tiles):\n")
        lines.append("| Tile | Image | Link | Description |\n| --- | --- | --- | --- |")
        for t, target, d in pg["hero"]:
            lines.append("| %s | `banners/climbuk_sharepoint-banner_%s_1920x1080.jpg` | `SitePages/%s.aspx` | %s |"
                         % (t, target, target, d))
        lines.append("")
    if pg["tiles"]:
        lines.append("**Quick links** (one column section after the first text section, layout Filmstrip):\n")
        lines.append("| Title | Image | Link |\n| --- | --- | --- |")
        for t in pg["tiles"]:
            lines.append("| %s | `quick-link-tiles/climbuk_sharepoint-tile_%s_1200x675.jpg` | `SitePages/%s.aspx` |"
                         % (PAGES[t]["title"], t, t))
        lines.append("")
(OUT / "_page-guide.md").write_text("\n".join(lines))

shutil.copy(HERE / "build-brand-centre.ps1", OUT)
fonts = OUT / "brand-fonts"
fonts.mkdir(exist_ok=True)
(OUT / "licences").mkdir(exist_ok=True)
for f in PACK.glob("templates/office/_shared/fonts/*"):
    shutil.copy(f, fonts if f.suffix == ".ttf" else OUT / "licences")
build = OUT / "_build"
build.mkdir(exist_ok=True)
for f in ("build_sharepoint_assets.py", "render.mjs", "pages.py", "make_pack.py", "build-brand-centre.ps1"):
    shutil.copy(HERE / f, build)
shutil.rmtree(OUT / "_html", ignore_errors=True)
print("pages:", len(PAGES))
