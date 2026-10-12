"""Build the brand default files Office opens for a new blank document, deck or workbook.

Output, per brand: templates/office/<Brand>/defaults/

    Normal.dotm          Word: the letterhead header, footer, page setup and styles with an empty body
    Blank.potx           PowerPoint for Windows: the brand deck's master and 19 layouts, no example slides
    Book.xltx            Excel: one empty sheet in the brand theme, Open Sans 11pt
    Default Theme.thmx   PowerPoint for Mac: the brand colours and fonts

Made from the templates the other scripts build (word_build.py, pptx_build.py, theme_build.py),
so run those first. The install package puts these in Defaults/<Brand>/ and set-climb-defaults
(macOS) or Set-ClimbDefaultsUser.ps1 (Windows) copies them into each person's Office folders.
"""
import io
import os
import re
import sys
import zipfile

from openpyxl import Workbook
from openpyxl.styles import Font

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from brand import BRANDS, BODY, OUT  # noqa: E402

OFFICE = os.path.join(OUT, "office")
DOTM_MAIN = "application/vnd.ms-word.template.macroEnabledTemplate.main+xml"
DOTX_MAIN = "application/vnd.openxmlformats-officedocument.wordprocessingml.template.main+xml"
STAMP = (2026, 10, 12, 0, 0, 0)


def read_zip(path):
    with zipfile.ZipFile(path) as z:
        return {n: z.read(n) for n in z.namelist()}


def write_zip(path, parts):
    """Write an OOXML package with [Content_Types].xml first and fixed dates, so rebuilds are byte-stable."""
    order = ["[Content_Types].xml"] + sorted(n for n in parts if n != "[Content_Types].xml")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for n in order:
            zi = zipfile.ZipInfo(n, date_time=STAMP)
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, parts[n])


def normal_dotm(brand, out):
    """The letterhead with its sample letter removed: every new blank document starts on the letterhead."""
    parts = read_zip(os.path.join(OFFICE, brand, "word", "%s_Letterhead.dotx" % brand))
    doc = parts["word/document.xml"].decode("utf-8")
    start = doc.index("<w:body>") + len("<w:body>")
    sect = doc.rindex("<w:sectPr")
    doc = doc[:start] + "<w:p/>" + doc[sect:]
    parts["word/document.xml"] = doc.encode("utf-8")
    ct = parts["[Content_Types].xml"].decode("utf-8")
    if DOTX_MAIN not in ct:
        sys.exit("%s letterhead: unexpected main content type" % brand)
    parts["[Content_Types].xml"] = ct.replace(DOTX_MAIN, DOTM_MAIN).encode("utf-8")
    # the thumbnail shows the sample letter; drop it rather than mislead
    parts.pop("docProps/thumbnail.jpeg", None)
    rels = parts["_rels/.rels"].decode("utf-8")
    parts["_rels/.rels"] = re.sub(r'<Relationship [^>]*Target="docProps/thumbnail\.jpeg"/>', "", rels).encode("utf-8")
    write_zip(out, parts)


def blank_potx(brand, out):
    """The brand deck with its example slides removed, keeping the master, layouts and theme."""
    parts = read_zip(os.path.join(OFFICE, brand, "powerpoint", "%s_Presentation_16x9.potx" % brand))
    pres = parts["ppt/presentation.xml"].decode("utf-8")
    pres = re.sub(r"<p:sldIdLst>.*?</p:sldIdLst>", "", pres, flags=re.S)
    parts["ppt/presentation.xml"] = pres.encode("utf-8")
    rels = parts["ppt/_rels/presentation.xml.rels"].decode("utf-8")
    rels = re.sub(r'<Relationship [^>]*Target="slides/slide\d+\.xml"/>', "", rels)
    parts["ppt/_rels/presentation.xml.rels"] = rels.encode("utf-8")
    for n in [n for n in parts if n.startswith("ppt/slides/")]:
        del parts[n]
    ct = parts["[Content_Types].xml"].decode("utf-8")
    ct = re.sub(r'<Override PartName="/ppt/slides/slide\d+\.xml"[^>]*/>', "", ct)
    parts["[Content_Types].xml"] = ct.encode("utf-8")
    # media only the example slides used
    used = set()
    for n, data in parts.items():
        if n.endswith(".rels"):
            used.update(re.findall(r'Target="\.\./media/([^"]+)"', data.decode("utf-8")))
    for n in [n for n in parts if n.startswith("ppt/media/") and os.path.basename(n) not in used]:
        del parts[n]
    app = parts.get("docProps/app.xml")
    if app:
        parts["docProps/app.xml"] = re.sub(rb"<Slides>\d+</Slides>", b"<Slides>0</Slides>", app)
    write_zip(out, parts)


def book_xltx(brand, out):
    """One empty sheet in the brand theme, so new workbooks use Open Sans and the brand colours."""
    theme = read_zip(os.path.join(OFFICE, "_shared", "office-theme", "%s.thmx" % brand))["theme/theme/theme1.xml"]
    wb = Workbook()
    wb.active.title = "Sheet1"
    wb.loaded_theme = theme
    normal = wb._named_styles["Normal"]
    normal.font = Font(name=BODY, size=11, family=2, scheme="minor")
    wb.template = True
    buf = io.BytesIO()
    wb.save(buf)
    # re-pack with fixed dates
    parts = read_zip(io.BytesIO(buf.getvalue()))
    parts["docProps/core.xml"] = re.sub(rb"<dcterms:(created|modified)([^>]*)>[^<]*</dcterms:\1>",
                                        rb"<dcterms:\1\2>2026-10-12T00:00:00Z</dcterms:\1>", parts["docProps/core.xml"])
    write_zip(out, parts)


def default_theme(brand, out):
    with open(os.path.join(OFFICE, "_shared", "office-theme", "%s.thmx" % brand), "rb") as f:
        data = f.read()
    with open(out, "wb") as f:
        f.write(data)


def main():
    for brand in BRANDS:
        d = os.path.join(OFFICE, brand, "defaults")
        os.makedirs(d, exist_ok=True)
        normal_dotm(brand, os.path.join(d, "Normal.dotm"))
        blank_potx(brand, os.path.join(d, "Blank.potx"))
        book_xltx(brand, os.path.join(d, "Book.xltx"))
        default_theme(brand, os.path.join(d, "Default Theme.thmx"))
        sizes = ", ".join("%s %d KB" % (n, os.path.getsize(os.path.join(d, n)) // 1024) for n in sorted(os.listdir(d)))
        print("%s: %s" % (brand, sizes))


if __name__ == "__main__":
    main()
