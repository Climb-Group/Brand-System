"""List the files the brand centre site holds in the SharePoint copy of the brand book.

The standalone brand book has no files of its own, so every download section points at the website. The script
uploads the Office templates to the Brand templates library and the PDFs to Brand files, so on SharePoint those two
sections list and link those copies instead. The links are relative to the book folder (Site Assets > BrandCentre >
book), so they work on any site. Usage: book_files.py PACK BOOK"""
import html, re, sys
from pathlib import Path
from PIL import Image

BRANDS = ("ClimbUK", "ClimbGroup", "Climb27")
APPS = (("word", "Word"), ("powerpoint", "PowerPoint"), ("excel", "Excel"))
# From the book folder up to the site: SiteAssets/BrandCentre/book/ -> the site root.
SITE = "../../../"
PREVIEW_WIDTH = 880


def away(code):
    return re.compile(r'<p class="cbb-kit-away">These files download from the brand centre on the website: [^\n]*?/brand/%s"[^\n]*?</p>' % code)


def size(path):
    n = path.stat().st_size
    return "%d KB" % round(n / 1024) if n < 1024 * 1024 else "%.1f MB" % (n / 1024 / 1024)


def card(brand, group, name, href, label, path, preview=None):
    look = ('<img src="%s" alt="" loading="lazy" decoding="async">' % preview if preview
            else '<span class="cbb-kit-format">%s</span>' % label)
    return (
        '<li class="cbb-kit-card" data-brand="%(code)s" data-search="%(search)s">'
        '<div class="cbb-kit-preview" data-ground="light">%(look)s</div>'
        '<div class="cbb-kit-body"><p class="cbb-kit-meta"><span class="cbb-kit-tag">%(brand)s</span>'
        '<span>%(group)s</span></p><h3 class="cbb-kit-title">%(name)s</h3>'
        '<div class="cbb-kit-files"><a class="cbb-kit-chip" href="%(href)s" download="" '
        'aria-label="Download %(brand)s %(name)s, %(label)s, %(size)s"><span>%(label)s</span><small>%(size)s</small>'
        '</a></div></div></li>') % dict(
        code=brand.lower(), search=html.escape(("%s %s %s" % (brand, group, name)).lower()), look=look,
        brand=brand, group=group, name=html.escape(name), href=html.escape(href), label=label, size=size(path))


def grid(cards):
    return ('<ul class="cbb-kit-grid" data-cbb-kit-grid="">%s</ul>'
            '<p class="cbb-kit-empty" data-cbb-kit-empty="" hidden="">Nothing here for this brand or search.</p>'
            % "".join(cards))


def templates(pack, book):
    out = book / "thumbs" / "office"
    out.mkdir(parents=True, exist_ok=True)
    cards = []
    for brand in BRANDS:
        for folder, app in APPS:
            src = pack / "templates" / "office" / "previews" / ("%s_%s.jpg" % (brand, app))
            preview = None
            if src.exists():
                with Image.open(src) as im:
                    im = im.convert("RGB")
                    im.thumbnail((PREVIEW_WIDTH, PREVIEW_WIDTH))
                    im.save(out / src.name, quality=82, optimize=True, progressive=True)
                preview = "thumbs/office/" + src.name
            for f in sorted((pack / "templates" / "office" / brand / folder).glob("*.[dpx][ol]tx")):
                name = f.stem.split("_", 1)[1].replace("_", " ").replace("-", " ").capitalize()
                cards.append(card(brand, app, name, "%sBrandTemplates/%s/%s" % (SITE, brand, f.name),
                                  f.suffix[1:].upper(), f, preview))
    note = ('<p class="cbb-kit-away">Word, Excel and PowerPoint also list these under File &gt; New, in your '
            'organisation\'s templates. Video templates and the install package download from the brand centre on '
            'the website: <a href="https://www.climb-uk.com/brand/templates">open them there</a>.</p>')
    return grid(cards) + note


def guidelines(pack, book):
    cards = []
    for kind, group in (("guidelines", "Brand guidelines"), ("one-page", "Key rules")):
        for brand in BRANDS:
            for f in sorted((pack / "pdf" / kind).glob(brand.lower() + "_*.pdf")):
                cards.append(card(brand, "PDF", group, SITE + "BrandFiles/" + f.name, "PDF", f))
    return grid(cards)


def main(pack, book):
    for page, code, make in (("templates.html", "templates", templates), ("guidelines.html", "guidelines", guidelines)):
        path = book / page
        text = path.read_text()
        new, n = away(code).subn(lambda m: make(pack, book), text, count=1)
        if n:
            path.write_text(new)
            print("Listed the site's files on %s" % page)


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
