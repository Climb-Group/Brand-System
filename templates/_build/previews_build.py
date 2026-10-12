"""Contact sheets of every Office template, rendered through LibreOffice, plus LibreOffice template copies
(.ott, .ots, .otp) for people who do not use Microsoft Office.

Per brand: <Brand>_Word.jpg, <Brand>_Excel.jpg and <Brand>_PowerPoint.jpg show the first set as before; the catalogue
templates get a sheet per app and group (<Brand>_Word-company.jpg, <Brand>_Word-events.jpg, <Brand>_Excel-company.jpg,
<Brand>_Excel-events.jpg, <Brand>_Decks.jpg) and the co-branded versions <Brand>_External.jpg. Converting every file to
PDF is also the proof that it opens.

python3 previews_build.py [Brand ...]
python3 previews_build.py --new [Brand ...]   only the catalogue sheets and copies, leaving the first set's sheets alone
python3 previews_build.py --sheets [Brand ...]  the catalogue sheets only, no LibreOffice copies
"""
import glob
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

import brand as B
import catalog as K

PREV = os.path.join(B.OUT, "_preview")


def soffice(args, cwd):
    subprocess.run(["soffice", "--headless"] + args, cwd=cwd, check=True, capture_output=True, timeout=600)


def pdf_pages(pdf, dpi=50):
    tmp = tempfile.mkdtemp(dir=os.path.dirname(pdf))
    subprocess.run(["pdftoppm", "-r", str(dpi), "-png", pdf, os.path.join(tmp, "p")], check=True)
    pages = [Image.open(p).convert("RGB") for p in sorted(glob.glob(os.path.join(tmp, "p-*.png")))]
    shutil.rmtree(tmp)
    return pages


def sheet(images, cols, cell_w, gap=16, bg=(36, 35, 34)):
    cells = []
    for im in images:
        h = int(im.height * cell_w / im.width)
        cells.append(im.resize((cell_w, h), Image.LANCZOS))
    ch = max(c.height for c in cells)
    rows = (len(cells) + cols - 1) // cols
    out = Image.new("RGB", (cols * cell_w + (cols + 1) * gap, rows * ch + (rows + 1) * gap), bg)
    for i, c in enumerate(cells):
        out.paste(c, (gap + (i % cols) * (cell_w + gap), gap + (i // cols) * (ch + gap)))
    return out


def catalogue_sheets(b, work, dest):
    """One sheet per app and group for the templates after the first set, and one for the co-branded versions."""
    def pages(row, n):
        return pdf_pages(os.path.join(work, row["app"], K.stem(b, row) + ".pdf"), 50 if row["app"] != "powerpoint" else 60)[:n]
    for app, label, cols, cell_w, n in (("word", "Word", 4, 420, 1), ("excel", "Excel", 2, 760, 1)):
        for group in ("Company", "Events"):
            rows = K.rows(app, b, external=False, original=False, group=group)
            if not rows:
                continue
            ims = []
            for row in rows:
                ims += pages(row, n)
            sheet(ims, cols, cell_w).save(os.path.join(dest, "%s_%s-%s.jpg" % (b, label, group.lower())), quality=86)
    ims = []
    for row in K.rows("powerpoint", b, external=False, original=False):
        ims += pages(row, 2)
    sheet(ims, 4, 480).save(os.path.join(dest, "%s_Decks.jpg" % b), quality=86)
    ims = []
    for row in K.rows(brand=b, external=True):
        ims += pages(row, 2 if row["app"] == "powerpoint" else 1)
    sheet(ims, 4, 480).save(os.path.join(dest, "%s_External.jpg" % b), quality=86)


def main():
    args = sys.argv[1:]
    new_only = args[:1] in (["--new"], ["--sheets"])
    copies = args[:1] != ["--sheets"]
    brands = (args[1:] if new_only else args) or list(B.BRANDS)
    dest = os.path.join(B.OUT, "office", "previews")
    os.makedirs(dest, exist_ok=True)
    for b in brands:
        work = tempfile.mkdtemp(prefix="prev_", dir=B.OUT)
        files = sorted(glob.glob(os.path.join(PREV, b + "_*.pptx")) + glob.glob(os.path.join(PREV, b + "_*.docx")) +
                       glob.glob(os.path.join(PREV, b + "_*.xlsx")))
        if new_only:
            first = {K.stem(b, r) for r in K.rows(brand=b, original=True)}
            files = [f for f in files if os.path.splitext(os.path.basename(f))[0] not in first]
        # One folder per app: a Word and an Excel template can share a name (the exhibitor risk assessment).
        for app, ext in K.DOC_EXT.items():
            d = os.path.join(work, app)
            os.makedirs(d)
            batch = [f for f in files if f.endswith("." + ext)]
            for f in batch:
                shutil.copy(f, d)
            if batch:
                soffice(["--convert-to", "pdf"] + [os.path.basename(f) for f in batch], d)
        if not new_only:
            deck = pdf_pages(os.path.join(work, "powerpoint", "%s_Presentation_16x9.pdf" % b), 60)
            sheet(deck, 3, 640).save(os.path.join(dest, "%s_PowerPoint.jpg" % b), quality=86)
            docs = []
            for name in ("Report", "Proposal", "Letterhead", "Press-release", "Meeting-notes"):
                pages = pdf_pages(os.path.join(work, "word", "%s_%s.pdf" % (b, name)), 50)
                docs += pages[:1] if name not in ("Report", "Proposal") else [pages[0], pages[2]]
            sheet(docs, 4, 420).save(os.path.join(dest, "%s_Word.jpg" % b), quality=86)
            books = []
            for name in ("Event-budget", "Partner-pipeline", "Run-sheet", "Content-calendar"):
                books += pdf_pages(os.path.join(work, "excel", "%s_%s.pdf" % (b, name)), 50)[:1]
            sheet(books, 2, 760).save(os.path.join(dest, "%s_Excel.jpg" % b), quality=86)
        catalogue_sheets(b, work, dest)
        shutil.rmtree(work)

        if not copies:
            continue
        # LibreOffice template copies, the co-branded versions included.
        lo = os.path.join(B.OUT, "office", "libreoffice", b)
        os.makedirs(lo, exist_ok=True)
        src = glob.glob(os.path.join(B.OUT, "office", b, "*", "*.*tx"))
        if new_only:
            src = [f for f in src if os.path.splitext(os.path.basename(f))[0] not in first]
        for f in src:
            ext = {".dotx": "ott", ".xltx": "ots", ".potx": "otp"}[os.path.splitext(f)[1]]
            soffice(["--convert-to", ext, "--outdir", lo, f], lo)
        print(b, len(src))


if __name__ == "__main__":
    main()
