"""Contact sheets of every Office template, rendered through LibreOffice, plus LibreOffice template copies
(.ott, .ots, .otp) for people who do not use Microsoft Office.

python3 previews_build.py [Brand ...]
"""
import glob
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

import brand as B

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


def main():
    brands = sys.argv[1:] or list(B.BRANDS)
    dest = os.path.join(B.OUT, "office", "previews")
    os.makedirs(dest, exist_ok=True)
    for b in brands:
        work = tempfile.mkdtemp(prefix="prev_", dir=B.OUT)
        files = sorted(glob.glob(os.path.join(PREV, b + "_*.pptx")) + glob.glob(os.path.join(PREV, b + "_*.docx")) +
                       glob.glob(os.path.join(PREV, b + "_*.xlsx")))
        for f in files:
            shutil.copy(f, work)
        soffice(["--convert-to", "pdf"] + [os.path.basename(f) for f in files], work)
        deck = pdf_pages(os.path.join(work, "%s_Presentation_16x9.pdf" % b), 60)
        sheet(deck, 3, 640).save(os.path.join(dest, "%s_PowerPoint.jpg" % b), quality=86)
        docs = []
        for name in ("Report", "Proposal", "Letterhead", "Press-release", "Meeting-notes"):
            pages = pdf_pages(os.path.join(work, "%s_%s.pdf" % (b, name)), 50)
            docs += pages[:1] if name not in ("Report", "Proposal") else [pages[0], pages[2]]
        sheet(docs, 4, 420).save(os.path.join(dest, "%s_Word.jpg" % b), quality=86)
        books = []
        for name in ("Event-budget", "Partner-pipeline", "Run-sheet", "Content-calendar"):
            books += pdf_pages(os.path.join(work, "%s_%s.pdf" % (b, name)), 50)[:1]
        sheet(books, 2, 760).save(os.path.join(dest, "%s_Excel.jpg" % b), quality=86)
        shutil.rmtree(work)

        # LibreOffice template copies.
        lo = os.path.join(B.OUT, "office", "libreoffice", b)
        os.makedirs(lo, exist_ok=True)
        src = glob.glob(os.path.join(B.OUT, "office", b, "*", "*.*tx"))
        for f in src:
            ext = {".dotx": "ott", ".xltx": "ots", ".potx": "otp"}[os.path.splitext(f)[1]]
            soffice(["--convert-to", ext, "--outdir", lo, f], lo)
        print(b, len(src))


if __name__ == "__main__":
    main()
