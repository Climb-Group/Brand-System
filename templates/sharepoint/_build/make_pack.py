"""Write pages.json, copy.txt and the page guide for the SharePoint brand centre pack, and copy in the brand book,
the web part package and its source. Usage: make_pack.py PACK OUT BOOK SPFX
  BOOK  the standalone brand book (build_brand_book.py --standalone)
  SPFX  the brand book web part project (brand-book-web-part/), built with npm run build"""
import html, json, re, shutil, subprocess, sys
from pathlib import Path
from pages import PAGES, NAV

PACK, OUT, BOOK, SPFX = (Path(a) for a in sys.argv[1:5])
HERE = Path(__file__).parent

data = {"nav": [{"label": l, "pages": p} for l, p in NAV], "pages": []}
for slug, pg in PAGES.items():
    data["pages"].append({
        "slug": slug, "title": pg["title"], "description": pg["description"],
        "banner": "climbuk_sharepoint-banner_%s_1920x1080.jpg" % slug,
        "sections": [{"layout": l, "emphasis": e, "columns": cols} for l, e, cols in pg["sections"]],
    })
# The brand book menu, for the SharePoint top navigation.
index = (BOOK / "index.html").read_text()
data["booknav"] = [
    {"label": re.search(r"data-cbb-menu-btn>([^<]+)<", g).group(1),
     "links": [{"page": u, "title": t} for u, t in re.findall(r'<a href="([a-z0-9-]+)\.html"[^>]*><b>([^<]+)</b>', g)]}
    for g in re.findall(r'<li class="cbb-menu-group">(.*?)</ul>\s*</li>', index, re.S)]


# The SharePoint theme. Fluent needs a full palette: every value is a token or a mix of two tokens.
def tok(path):
    o = json.loads((PACK / "tokens/brand.tokens.json").read_text())
    for k in path.split("."):
        o = o[k]
    return o["$value"]


def mix(a, b, t):
    """t of colour b over colour a."""
    ca, cb = (tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in (a, b))
    return "#%02X%02X%02X" % tuple(round(x + (y - x) * t) for x, y in zip(ca, cb))


primary, white = tok("color.orange.text"), tok("color.brand.white")
charcoal, brown = tok("color.brand.charcoal"), tok("color.brand.dark-brown")
data["theme"] = {"name": "ClimbUK", "palette": {
    "themePrimary": primary,
    "themeLighterAlt": mix(primary, white, .96), "themeLighter": mix(primary, white, .86),
    "themeLight": mix(primary, white, .74), "themeTertiary": tok("color.orange.tint"),
    "themeSecondary": tok("color.orange.large-on-grey"), "themeDarkAlt": tok("color.orange.text-on-grey"),
    "themeDark": tok("color.orange.deep"), "themeDarker": tok("color.orange.deep-on-grey"),
    "neutralLighterAlt": mix(white, charcoal, .02), "neutralLighter": mix(white, charcoal, .04),
    "neutralLight": tok("color.brand.light-grey"), "neutralQuaternaryAlt": mix(white, charcoal, .13),
    "neutralQuaternary": mix(white, charcoal, .16), "neutralTertiaryAlt": mix(white, charcoal, .22),
    "neutralTertiary": mix(white, charcoal, .4), "neutralSecondaryAlt": mix(white, charcoal, .55),
    "neutralSecondary": mix(white, charcoal, .7), "neutralPrimaryAlt": mix(white, charcoal, .85),
    "neutralPrimary": charcoal, "neutralDark": brown, "black": brown, "white": white,
    "primaryBackground": white, "primaryText": charcoal}}
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
for f in ("build_sharepoint_assets.py", "render.mjs", "pages.py", "make_pack.py", "book_files.py", "build-brand-centre.ps1"):
    shutil.copy(HERE / f, build)
shutil.rmtree(OUT / "_html", ignore_errors=True)

# The brand book, the web part package and its source.
shutil.rmtree(OUT / "brand-book", ignore_errors=True)
shutil.copytree(BOOK, OUT / "brand-book")
subprocess.run([sys.executable, str(HERE / "book_files.py"), str(PACK), str(OUT / "brand-book")], check=True)
(OUT / "app").mkdir(exist_ok=True)
shutil.copy(SPFX / "sharepoint/solution/climb-brand-page.sppkg", OUT / "app")
src = OUT / "brand-book-web-part"
shutil.rmtree(src, ignore_errors=True)
shutil.copytree(SPFX, src, ignore=shutil.ignore_patterns(
    "node_modules", "lib", "lib-*", "temp", "dist", "release", "sharepoint", ".heft", "jest-output", "*.log"))
print("pages:", len(PAGES))
