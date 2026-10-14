"""Climb27 A5 flyer, one version per audience (the eight audiences of the climb-uk.com audience chooser).

Same layout as climb27_flyer_a5.pdf: front photo and display line on orange, back with five reasons, a photo
strip and a QR code to that audience's page on climb-uk.com.

    python3 segments.py [--pack /path/to/Brand-System]
"""
import argparse
import html
import json
import os
import re
import subprocess
from pathlib import Path

import build as B
from build import BLEED, DB, DB_RGB, OR, TI, WH, DATES, TAGLINE, URL



def from_copy(path):
    """One flyer's words, photos and icons, from its copy file in copy/segments/."""
    d = B.copy_md.load(path)
    link = d.one("back.link")
    return dict(slug=path.name[:-len(".copy.md")], order=int(d.meta["order"]), audience=d.one("audience").text,
                noun=d.one("back.noun").text, eyebrow=d.one("front.eyebrow").text, sub=d.words("front.subline", TAGLINE),
                head=d.one("front.headline").text, hero=B.photo(d.one("front.photo")), cta=d.one("button").text,
                strip=[B.photo(p) for p in d.all("back.photo")],
                items=[(r["icon"], r.title, r.text) for r in d.all("back.reason")],
                path=link.text, qr=link["qr"])


# headline: [[word]] is the highlight (Dark Brown on the orange front), *word* is italic.
SEGMENTS = sorted((from_copy(p) for p in (B.COPY / "segments").glob("*.copy.md")), key=lambda s: s["order"])


def rich(s, hl):
    s = html.escape(s)
    s = re.sub(r"\[\[(.+?)\]\]", r'<span style="color:%s">\1</span>' % hl, s)
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", s).replace("\n", "<br>")


def plain(s):
    return s.replace("[[", "").replace("]]", "").replace("*", "").replace("\n", " ")


def flyer(pack, s):
    W, H = 148 + 2 * BLEED, 210 + 2 * BLEED
    b, m = BLEED, BLEED + 10
    slug = s["slug"]
    path, qr = s["path"], s["qr"]
    # Front
    hero_h = 122
    hero = B.bake(pack, s["hero"][0], W, hero_h, 300, "seg_%s_hero" % slug, pos=s["hero"][1],
                  fade=[("y", 0.0, 0.35, DB_RGB, 0.78, 0.0)])
    f = [B.img(hero, 0, 0, W, hero_h)]
    f.append(B.logo_tag(pack, "Climb27", "reversed-dark", m, b + 10, 52))
    cut = 112
    f.append('<div class="abs" style="left:0;top:%smm;width:%smm;height:%smm;background:%s;'
             'clip-path:polygon(0 12mm,100%% 0,100%% 100%%,0 100%%)"></div>' % (cut - 12, W, H - cut + 12, OR))
    f.append('<div class="abs mont" style="left:%smm;top:%smm;transform:rotate(-3.5deg);background:%s;color:%s;'
             'font-weight:800;font-size:10.5pt;letter-spacing:.04em;text-transform:uppercase;padding:2.2mm 4mm;'
             'border-radius:1.5mm">%s</div>' % (m + 52, cut - 13, DB, WH, DATES))
    f.append('<div class="abs mont" style="left:%smm;top:%smm;font-weight:800;font-size:10pt;letter-spacing:.14em;'
             'text-transform:uppercase;color:%s">%s</div>' % (m, cut + 6, DB, html.escape(s["eyebrow"])))
    f.append('<h1 class="abs disp" data-fit="1" style="left:%smm;top:%smm;width:%smm;height:40mm;font-size:36pt;color:%s;'
             'line-height:1.0">%s</h1>' % (m, cut + 13, W - 2 * m, WH, rich(s["head"], DB)))
    f.append('<div class="abs" style="left:%smm;top:%smm;width:16mm;height:1.6mm;border-radius:1mm;background:%s"></div>'
             % (m, cut + 57, DB))
    f.append('<div class="abs mont" style="left:%smm;top:%smm;width:%smm;font-weight:700;font-size:14pt;color:%s;line-height:1.2">'
             '%s</div>' % (m, cut + 62, W - 2 * m, WH, html.escape(s["sub"])))
    band = H - b - 26
    f.append('<div class="abs" style="left:0;top:%smm;width:%smm;height:%smm;background:%s"></div>' % (band, W, H - band, DB))
    f.append('<div class="abs mont" style="left:%smm;top:%smm;color:%s;font-weight:700;font-size:9pt;letter-spacing:.14em;'
             'text-transform:uppercase">%s</div>' % (m, band + 6, TI, html.escape(plain(s["cta"]))))
    f.append('<div class="abs mont" style="left:%smm;top:%smm;color:%s;font-weight:800;font-size:20pt;letter-spacing:-.01em">'
             '%s</div>' % (m, band + 11, WH, URL))
    f.append(B.logo_tag(pack, "ClimbUK", "reversed-dark", W - m - 34, band + 12.5, 34))
    front = B.page(pack, W, H, "\n".join(f), "Climb27 flyer for %s, front" % s["audience"])

    # Back
    r = ['<div class="abs" style="inset:0;background:%s"></div>' % DB]
    r.append(B.img(B.glow(W, H, 150, "flyer_back_glow", 1.05, -0.05, 0.75, 0.45), 0, 0, W, H))
    svg, ratio = B.logo(pack, "Climb27", "reversed-dark")
    svg = svg.replace("<svg ", '<svg style="width:100%;height:100%;display:block" ', 1)
    r.append('<h2 class="abs disp" style="left:%smm;top:%smm;width:%smm;font-size:24pt;color:%s;line-height:1.04">'
             'What <span style="display:inline-block;width:43mm;height:%.2fmm;vertical-align:-0.7mm">%s</span><br>'
             'does for <em>your</em><br><span class="o">%s</span>.</h2>'
             % (m, b + 11, W - 2 * m, WH, 43 / ratio, svg, html.escape(s["noun"])))
    y = b + 47
    for icon, head, text in s["items"]:
        r.append('<div class="abs" style="left:%smm;top:%smm;width:13mm;height:13mm">%s</div>' % (m - 1, y - 1, B.illo(pack, icon)))
        r.append('<div class="abs disp" style="left:%smm;top:%smm;font-size:13pt;color:%s;text-transform:none;letter-spacing:0">'
                 '%s<span class="o">.</span></div>' % (m + 16, y, WH, html.escape(head)))
        r.append('<div class="abs body" style="left:%smm;top:%smm;width:%smm;font-size:9pt;line-height:1.38;color:%s">%s</div>'
                 % (m + 16, y + 6.2, W - 2 * m - 16, WH, html.escape(text)))
        y += 20.5
    py, ph, gap, big = y + 1.5, 31, 2.5, 60
    small = (W - 2 * m - big - 2 * gap) / 2
    x = m
    for i, ((p, pos), w) in enumerate(zip(s["strip"], (big, small, small))):
        r.append(B.img(B.bake(pack, p, w, ph, 300, "seg_%s_%d" % (slug, i), pos=pos), x, py, w, ph, "border-radius:2mm"))
        x += w + gap
    band = H - b - 26
    assert py + ph < band - 1, "photo strip runs into the band on %s" % slug
    r.append('<div class="abs" style="left:0;top:%smm;width:%smm;height:%smm;background:%s"></div>' % (band, W, H - band, OR))
    r.append('<div class="abs disp" style="left:%smm;top:%smm;font-size:16pt;color:%s">%s</div>'
             % (m, band + 5.5, WH, rich(s["cta"], WH)))
    r.append('<div class="abs mont" style="left:%smm;top:%smm;font-weight:800;font-size:11pt;color:%s">%s</div>'
             % (m, band + 12.6, WH, path))
    r.append('<div class="abs mont" style="left:%smm;top:%smm;font-weight:700;font-size:8.5pt;color:%s">%s</div>'
             % (m, band + 18.6, DB, DATES))
    qs = 19
    r.append('<div class="abs" style="left:%smm;top:%smm;width:%smm;height:%smm;background:%s;border-radius:1.5mm;padding:1.6mm;'
             'box-sizing:border-box">%s</div>' % (W - m - qs, band + 3.5, qs, qs, WH, B.qr_svg(qr)))
    back = B.page(pack, W, H, "\n".join(r), "Climb27 flyer for %s, back" % s["audience"])
    return W, H, front, back


RENDER_JS = r"""
const { chromium } = require('playwright');
(async () => {
  const jobs = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const j of jobs) {
    await page.goto('file://' + j.html, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    await page.evaluate(() => {
      for (const el of document.querySelectorAll('[data-fit]')) {
        let fs = parseFloat(getComputedStyle(el).fontSize);
        const box = el.clientHeight;
        el.style.height = 'auto';
        while ((el.scrollHeight > box || el.scrollWidth > el.clientWidth) && fs > 10) { fs -= 0.5; el.style.fontSize = fs + 'px'; }
      }
    });
    await page.pdf({ path: j.pdf, width: j.w + 'mm', height: j.h + 'mm', printBackground: true, preferCSSPageSize: true });
  }
  await browser.close();
})();
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", default=str(Path(__file__).resolve().parents[3]))
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    pack = Path(a.pack)
    hd, pg, out = B.HERE / "html", B.HERE / "pages", B.OUT / "segments"
    for d in (hd, pg, out):
        d.mkdir(exist_ok=True)
    jobs = []
    for s in SEGMENTS:
        if a.only and a.only not in s["slug"]:
            continue
        W, H, front, back = flyer(pack, s)
        for side, doc in (("front", front), ("back", back)):
            f = hd / ("seg_%s_%s.html" % (s["slug"], side))
            f.write_text(doc)
            jobs.append(dict(html=str(f), pdf=str(pg / ("seg_%s_%s.pdf" % (s["slug"], side))), w=W, h=H, slug=s["slug"]))
    (B.HERE / "render_seg.cjs").write_text(RENDER_JS)
    (B.HERE / "jobs.json").write_text(json.dumps(jobs))
    subprocess.run(["node", str(B.HERE / "render_seg.cjs"), str(B.HERE / "jobs.json")], check=True)
    from pypdf import PdfReader, PdfWriter
    for s in SEGMENTS:
        if a.only and a.only not in s["slug"]:
            continue
        wr = PdfWriter()
        for side in ("front", "back"):
            for p in PdfReader(str(pg / ("seg_%s_%s.pdf" % (s["slug"], side)))).pages:
                wr.add_page(p)
        name = out / ("climb27_flyer_%s_a5.pdf" % s["slug"])
        with open(name, "wb") as fh:
            wr.write(fh)
        B.set_boxes(name, BLEED)
        print("wrote", name.name)


if __name__ == "__main__":
    main()
