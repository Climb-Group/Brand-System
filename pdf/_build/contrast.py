"""Report text under WCAG 2.2 AA contrast in the printed pages.

Reads what contrast.cjs captured: every run of text with its colour and box,
and each page with the text hidden. The background is measured behind each
run, and the run passes when 95% of the pixels behind the middle of it give at least 4.5:1
(3:1 for large text: 24px, or 18.66px bold).

    node contrast.cjs OUT ./*.html && python3 contrast.py OUT
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image


def lum(rgb):
    c = rgb / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return c[..., 0] * 0.2126 + c[..., 1] * 0.7152 + c[..., 2] * 0.0722


def parse(col):
    v = [float(x) for x in re.findall(r"[\d.]+", col)]
    return np.array(v[:3]), (v[3] if len(v) > 3 else 1.0)


def main(out):
    out = Path(out)
    report = json.loads((out / "runs.json").read_text())
    fails = []
    for name, pages in report.items():
        for pg in pages:
            im = np.asarray(Image.open(out / ("%s-%d.png" % (name, pg["page"]))).convert("RGB")).astype(float)
            H, W = im.shape[:2]
            for r in pg["runs"]:
                rgb, a = parse(r["color"])
                a *= float(r["opacity"])
                if a < 0.05:
                    continue  # outline numerals and other decorative text
                # Measure the middle of the line box: stickers are tilted, so the corners of their
                # boxes reach past the sticker onto the page behind.
                mx, my = r["w"] * 0.25, r["h"] * 0.3
                x0, y0 = max(0, int(r["x"] + mx)), max(0, int(r["y"] + my))
                x1, y1 = min(W, int(r["x"] + r["w"] - mx)), min(H, int(r["y"] + r["h"] - my))
                if x1 <= x0 or y1 <= y0:
                    continue
                bg = im[y0:y1, x0:x1].reshape(-1, 3)
                fg = rgb * a + bg * (1 - a)
                lf, lb = lum(fg), lum(bg)
                ratio = (np.maximum(lf, lb) + 0.05) / (np.minimum(lf, lb) + 0.05)
                worst = float(np.percentile(ratio, 5))
                large = r["size"] >= 24 or (r["size"] >= 18.66 and r["weight"] >= 700)
                need = 3.0 if large else 4.5
                if worst < need:
                    fails.append((name, pg["page"], worst, need, r["size"], r["text"]))
    for f in fails:
        print("%-30s p%-3d %.2f:1 (needs %.1f, %gpx)  %s" % f)
    total = sum(len(p["runs"]) for pages in report.values() for p in pages)
    print("%d text runs checked, %d under AA" % (total, len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
