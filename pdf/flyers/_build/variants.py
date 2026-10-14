"""Four more general Climb27 A5 flyers for people who are new to ClimbUK, one per brand theme, each with its own
layout, photos, icons and motif family (climb-visual-style: Connections, Stage Light, the Ascent, Contours).

    python3 variants.py [--pack /path/to/Brand-System]
"""
import argparse
import html
import json
import math
import os
import random
import re
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import build as B
from build import BLEED, CH, DB, DB_RGB, OR, OR_RGB, TI, WH, DATES

QR = "https://www.climb-uk.com/?utm_source=flyer&utm_campaign=climb27#climb27_choose"
W, H = 148 + 2 * BLEED, 210 + 2 * BLEED
b, m = BLEED, BLEED + 10
PX = 10  # motif SVG units per mm

sys_path = None


def motifs(pack):
    import sys
    sys.path.insert(0, str(pack / "generators"))
    import motifs as M
    return M


def rich(s, hl=OR):
    s = html.escape(s)
    s = re.sub(r"\[\[(.+?)\]\]", r'<span style="color:%s">\1</span>' % hl, s)
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)


def plain(s):
    return s.replace("[[", "").replace("]]", "").replace("*", "")


def svg_layer(inner, x=0, y=0, w=W, h=H, extra=""):
    return ('<svg class="abs" aria-hidden="true" style="left:%smm;top:%smm;width:%smm;height:%smm;%s" viewBox="0 0 %d %d">%s</svg>'
            % (x, y, w, h, extra, w * PX, h * PX, inner))


def stage_light_img(name, seed=3, ppi=150):
    """Stage Light baked to an image: Climb Orange beams fanning down from above, Orange Tint glow, fine grain."""
    w, h = int(W / 25.4 * ppi), int(H / 25.4 * ppi)
    rnd = random.Random(seed)
    base = Image.new("RGB", (w, h), DB_RGB)
    beams = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(beams)
    sx, sy = w * 0.68, -h * 0.12
    reach = math.hypot(w, h) * 1.2
    for a in (-30, -12, 14):
        spread = rnd.uniform(7, 11)
        pts = [(sx, sy)]
        for e in (a - spread / 2, a + spread / 2):
            r = math.radians(90 + e)
            pts.append((sx + reach * math.cos(r), sy + reach * math.sin(r)))
        d.polygon(pts, fill=150)
    beams = beams.filter(ImageFilter.GaussianBlur(w / 60))
    yy = np.linspace(1, 0, h)[:, None] ** 1.4
    al = np.asarray(beams, np.float32) / 255 * yy * 0.75
    gx, gy = np.mgrid[0:h, 0:w]
    glow = np.clip(1 - np.hypot((gy - sx) / (w * 0.35), (gx - 0) / (h * 0.16)), 0, 1) ** 2 * 0.55
    a = np.asarray(base, np.float32)
    a = a * (1 - al[..., None]) + np.array(OR_RGB, np.float32) * al[..., None]
    a = a * (1 - glow[..., None]) + np.array((242, 174, 134), np.float32) * glow[..., None]
    a += np.random.default_rng(seed).normal(0, 3.0, a.shape)
    out = B.IMG / (name + ".jpg")
    B.IMG.mkdir(exist_ok=True)
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(out, quality=92)
    return out


def sticker(x, y, text, bg=OR, ink=DB, rot=-3.5):
    return ('<div class="abs mont" style="left:%smm;top:%smm;transform:rotate(%sdeg);background:%s;color:%s;font-weight:800;'
            'font-size:10pt;letter-spacing:.04em;text-transform:uppercase;padding:2.2mm 4mm;border-radius:1.5mm;'
            '">%s</div>' % (x, y, rot, bg, ink, html.escape(text)))


def rule(x, y, colour=OR):
    return '<div class="abs" style="left:%smm;top:%smm;width:16mm;height:1.6mm;border-radius:1mm;background:%s"></div>' % (x, y, colour)


def eyebrow(x, y, text, colour=TI):
    return ('<div class="abs mont" style="left:%smm;top:%smm;font-weight:800;font-size:9.5pt;letter-spacing:.14em;'
            'text-transform:uppercase;color:%s">%s</div>' % (x, y, colour, html.escape(text)))


def headline(x, y, w, h, s, size=44, hl=OR, colour=WH):
    return ('<h1 class="abs disp" data-fit="1" style="left:%smm;top:%smm;width:%smm;height:%smm;font-size:%spt;color:%s;'
            'line-height:.98">%s</h1>' % (x, y, w, h, size, colour, rich(s, hl)))


def sub(x, y, w, text, colour=WH, size=11.5):
    return ('<div class="abs body" style="left:%smm;top:%smm;width:%smm;font-size:%spt;line-height:1.35;font-weight:600;color:%s">%s</div>'
            % (x, y, w, size, colour, html.escape(text)))


def front_band(pack, cta, bg=CH):
    band = H - b - 26
    return ('<div class="abs" style="left:0;top:%smm;width:%smm;height:%smm;background:%s"></div>' % (band, W, H - band, bg)
            + eyebrow(m, band + 6, cta)
            + '<div class="abs mont" style="left:%smm;top:%smm;color:%s;font-weight:800;font-size:20pt;letter-spacing:-.01em">'
              'climb-uk.com</div>' % (m, band + 11, WH)
            + B.logo_tag(pack, "ClimbUK", "reversed-dark", W - m - 34, band + 12.5, 34))


# ---------------------------------------------------------------- the four fronts

def front_people(pack, M, v):
    f = ['<div class="abs" style="inset:0;background:%s"></div>' % DB]
    f.append(B.img(B.bake(pack, "crowds_04", W, 114, 300, "var_people_hero", pos=(0.5, 0.3),
                          fade=[("y", 0.0, 0.12, DB_RGB, 1.0, 0.0), ("y", 0.6, 1.0, DB_RGB, 0.0, 1.0)]), 0, 20, W, 114))
    f.append(svg_layer(M.connections(W * PX, H * PX, seed=27, dots=26, dark=True, region=(0.58, 0.6, 0.97, 0.83))))
    f.append(B.logo_tag(pack, "Climb27", "reversed-dark", m, b + 10, 52))
    f.append(sticker(W - m - 62, 104, "Founders. Investors. Advisers."))
    f.append(rule(m, 124))
    f.append(eyebrow(m, 128.5, DATES))
    f.append(headline(m, 135, W - 2 * m, 30, v["head"], 50))
    f.append(sub(m, 168, 82, v["sub"]))
    f.append(front_band(pack, plain(v["cta"])))
    return f


def front_stage(pack, M, v):
    f = [B.img(stage_light_img("var_stage_light"), 0, 0, W, H)]
    f.append(B.img(B.bake(pack, "stage_speakers_03", W, 96, 300, "var_stage_hero", pos=(0.5, 0.4),
                          fade=[("y", 0.0, 0.12, DB_RGB, 1.0, 0.0), ("y", 0.55, 1.0, DB_RGB, 0.0, 1.0)]), 0, 20, W, 96))
    f.append(B.logo_tag(pack, "Climb27", "reversed-dark", m, b + 10, 52))
    # Outline numerals: decorative, beside the real heading.
    f.append('<div class="abs" aria-hidden="true" style="right:%smm;top:84mm;font-family:Montserrat;font-weight:800;font-size:140pt;'
             'line-height:.8;letter-spacing:-.04em;color:transparent;-webkit-text-stroke:0.55mm %s">27</div>' % (m - 4, OR))
    f.append(rule(m, 124))
    f.append(eyebrow(m, 128.5, DATES))
    f.append(headline(m, 135, W - 2 * m, 30, v["head"], 48))
    f.append(sub(m, 168, 92, v["sub"]))
    f.append(front_band(pack, plain(v["cta"])))
    return f


def front_bigger(pack, M, v):
    top = 104
    f = ['<div class="abs" style="inset:0;background:%s"></div>' % DB]
    f.append('<div class="abs" style="left:0;top:0;width:%smm;height:%smm;background:%s"></div>' % (W, top + 10, OR))
    f.append(svg_layer(M.ascent(W * PX, H * PX, (W - m - 26) * PX, 44 * PX, 32 * PX, steps=5, colour="rgba(255,255,255,.28)",
                                kind="chevrons")))
    f.append(B.logo_tag(pack, "Climb27", "mono-white", m, b + 10, 52))
    f.append(rule(m, 38, DB))
    f.append(eyebrow(m, 42.5, DATES, DB))
    f.append('<h1 class="abs disp" style="left:%smm;top:50mm;width:%smm;font-size:34pt;color:%s;line-height:1.02">'
             'Your business.<br><em>Bigger</em> <span style="background:%s;padding:0 2.2mm;box-decoration-break:clone;'
             '-webkit-box-decoration-break:clone">stage.</span></h1>' % (m, W - 2 * m, WH, DB))
    f.append(sub(m, 79, 110, v["sub"], DB, 12))
    f.append(B.img(B.bake(pack, "audience_at_stage_01", W, H - top, 300, "var_bigger_photo", pos=(0.4, 0.35)), 0, top, W, H - top,
                   "clip-path:polygon(0 10mm,100% 0,100% 100%,0 100%)"))
    f.append(sticker(W - m - 50, top - 4, "Two days. One festival.", DB, WH))
    f.append(front_band(pack, plain(v["cta"]), DB))
    return f


def front_party(pack, M, v):
    f = ['<div class="abs" style="inset:0;background:%s"></div>' % DB]
    f.append(svg_layer(M.contours(W * PX, H * PX, seed=12, rings=11, dark=True, marker=True, cx=0.92, cy=0.78)))
    g, y0, top = 2, 22, 118
    bw = 94
    f.append(B.img(B.bake(pack, "vip_and_awards_01", bw, top - y0, 300, "var_party_big", pos=(0.62, 0.3)), 0, y0, bw, top - y0))
    sw = W - bw - g
    sh = (top - y0 - g) / 2
    f.append(B.img(B.bake(pack, "climb_recap_02", sw, sh, 300, "var_party_s1", pos=(0.5, 0.3)), bw + g, y0, sw, sh))
    f.append(B.img(B.bake(pack, "climb_drinks_reception", sw, sh, 300, "var_party_s2", pos=(0.7, 0.5)), bw + g, y0 + sh + g, sw, sh))
    f.append(B.logo_tag(pack, "Climb27", "reversed-dark", m, b + 6, 46))
    f.append(sticker(m + 50, top - 6, DATES))
    f.append(rule(m, 128))
    f.append(eyebrow(m, 132.5, "New to ClimbUK?"))
    f.append(headline(m, 139, W - 2 * m, 30, v["head"], 46))
    f.append(sub(m, 170, 84, v["sub"]))
    f.append(front_band(pack, plain(v["cta"])))
    return f


VARIANTS = [
    dict(slug="find-your-people", front=front_people, back="connections",
         head="Find *your* [[people]].",
         sub="Two days with the founders, investors and advisers who help businesses grow.",
         cta="Find *your* people", back_head="Two days. The *right* [[people]].",
         strip=[("joy_02", (0.5, 0.4)), ("meetings_02", (0.5, 0.4)), ("climb_recap_03", (0.5, 0.3))],
         items=[
             ("people", "Advice from one step ahead",
              "Founders and leaders a step further on, who will tell you what worked and what they would change."),
             ("money-bag", "Investors looking for deal flow",
              "Angels, funds and lenders who come to find their next deal."),
             ("briefcase", "Advisers and experts",
              "Professional services firms and advisers with answers you can use the next morning."),
             ("round-table", "Roundtables and workshops",
              "Small rooms and practical advice on what growing businesses face next."),
             ("cheers-bottles", "The after parties",
              "The conversations keep going when the sessions end."),
         ]),
    dict(slug="main-stage-moments", front=front_stage, back="stage",
         head="[[Main stage]] *moments*.",
         sub="Big announcements, the ClimbAwards and the stories behind growing businesses.",
         cta="Find *your* moment", back_head="Two days of *big* [[moments]].",
         strip=[("climb_awards_winners", (0.5, 0.4)), ("climb_isn_investors_hero", (0.5, 0.4)), ("audience_at_stage_02", (0.5, 0.4))],
         items=[
             ("microphone", "The main stage",
              "Founders and investors sharing what worked, in short, sharp sessions."),
             ("stopwatch", "Investor Speed Networking",
              "A round of short conversations with investors from your sector. Add it to your ticket."),
             ("medal", "The ClimbAwards",
              "Celebrating the businesses and people driving growth."),
             ("round-table", "Roundtables and workshops",
              "Small rooms, practical advice and a clear next step for your business."),
             ("party-popper", "The after parties",
              "Where the conversations of the day carry on."),
         ]),
    dict(slug="bigger-stage", front=front_bigger, back="ascent",
         head="Your business. *Bigger* [[stage]].",
         sub="The Festival for Business Growth: two days to take your business to its next stage.",
         cta="Find *your* stage", back_head="Your *next* [[step]] starts here.",
         strip=[("meetings_03", (0.5, 0.4)), ("roundtable_and_workshops_02", (0.5, 0.4)), ("exhibitor_02", (0.5, 0.4))],
         items=[
             ("rocket", "Sessions for your next stage",
              "New markets, hiring and funding, for businesses already trading."),
             ("money-bag", "Funding that fits",
              "Investors for the whole funding journey, from first cheque onwards, looking for businesses at your stage."),
             ("target", "Practical advice",
              "Ideas you can act on the next morning, from people who have done it."),
             ("handshake", "Connections that lead to work",
              "Firms, advisers and fellow founders who share what works and send each other work."),
             ("tickets", "A ticket for every stage",
              "Start-up and professional tickets, and teams of four or more save 25%."),
         ]),
    dict(slug="business-with-a-party", front=front_party, back="contours",
         head="*Business* with a [[party]].",
         sub="Two days of ideas, deals and good company at the Festival for Business Growth.",
         cta="Find *your* Climb27", back_head="Two days. *One* [[community]].",
         strip=[("food_and_vendors_01", (0.5, 0.4)), ("climb_recap_04", (0.5, 0.3)), ("joy_04", (0.5, 0.4))],
         items=[
             ("sparkles", "Festival energy",
              "Stages, food, drink and good company, with business at the heart of it."),
             ("lightbulb", "Ideas you can use",
              "Practical sessions from the people building and backing growing businesses."),
             ("people", "A community",
              "People here share what they have learned and send each other work."),
             ("medal", "The ClimbAwards",
              "Celebrating the businesses and people driving growth."),
             ("compass", "Where you fit",
              "Scan the code, pick who you are, and see what Climb27 means for you."),
         ]),
]


def back(pack, M, v):
    kind = v["back"]
    if kind == "stage":
        r = [B.img(stage_light_img("var_stage_light_back", seed=8), 0, 0, W, H)]
    elif kind == "ascent":
        r = ['<div class="abs" style="inset:0;background:%s"></div>' % CH]
        r.append(svg_layer(M.ascent(W * PX, H * PX, (W - 52) * PX, 44 * PX, 26 * PX, steps=4, colour=OR)))
    else:
        r = ['<div class="abs" style="inset:0;background:%s"></div>' % DB]
        if kind == "connections":
            r.append(svg_layer(M.connections(W * PX, H * PX, seed=5, dots=16, dark=True, region=(0.66, 0.02, 0.98, 0.2))))
        else:
            r.append(svg_layer(M.contours(W * PX, H * PX, seed=4, rings=9, dark=True, marker=True, cx=1.0, cy=0.0)))
    r.append(rule(m, b + 11))
    r.append(eyebrow(m, b + 15.5, "New to ClimbUK?"))
    r.append('<h2 class="abs disp" style="left:%smm;top:%smm;width:%smm;font-size:25pt;color:%s;line-height:1.02">%s</h2>'
             % (m, b + 22, 96 if kind == "ascent" else W - 2 * m, WH, rich(v["back_head"])))
    y = b + 47
    for icon, head, text in v["items"]:
        r.append('<div class="abs" style="left:%smm;top:%smm;width:13mm;height:13mm">%s</div>' % (m - 1, y - 1, B.illo(pack, icon)))
        r.append('<div class="abs disp" style="left:%smm;top:%smm;font-size:13pt;color:%s;text-transform:none;letter-spacing:0">'
                 '%s<span class="o">.</span></div>' % (m + 16, y, WH, html.escape(head)))
        r.append('<div class="abs body" style="left:%smm;top:%smm;width:%smm;font-size:9pt;line-height:1.38;color:%s">%s</div>'
                 % (m + 16, y + 6.2, W - 2 * m - 16, WH, html.escape(text)))
        y += 20
    py, ph, gap, big = y + 1.5, 29, 2.5, 60
    small = (W - 2 * m - big - 2 * gap) / 2
    x = m
    for i, ((p, pos), w) in enumerate(zip(v["strip"], (big, small, small))):
        r.append(B.img(B.bake(pack, p, w, ph, 300, "var_%s_%d" % (v["slug"], i), pos=pos), x, py, w, ph, "border-radius:2mm"))
        x += w + gap
    band = H - b - 26
    assert py + ph < band - 1, v["slug"]
    r.append('<div class="abs" style="left:0;top:%smm;width:%smm;height:%smm;background:%s"></div>' % (band, W, H - band, OR))
    r.append('<div class="abs disp" style="left:%smm;top:%smm;font-size:16pt;color:%s">%s</div>' % (m, band + 5.5, WH, rich(v["cta"], WH)))
    r.append('<div class="abs mont" style="left:%smm;top:%smm;font-weight:800;font-size:12pt;color:%s">climb-uk.com</div>'
             % (m, band + 12.6, WH))
    r.append('<div class="abs mont" style="left:%smm;top:%smm;font-weight:700;font-size:8.5pt;color:%s">%s</div>'
             % (m, band + 18.6, DB, DATES))
    qs = 19
    r.append('<div class="abs" style="left:%smm;top:%smm;width:%smm;height:%smm;background:%s;border-radius:1.5mm;padding:1.6mm;'
             'box-sizing:border-box">%s</div>' % (W - m - qs, band + 3.5, qs, qs, WH, B.qr_svg(QR)))
    r.append('<div class="abs mont" style="left:%smm;top:%smm;width:30mm;text-align:right;font-weight:700;font-size:7.5pt;'
             'line-height:1.25;color:%s">Scan and pick<br>who you are</div>' % (W - m - qs - 33, band + 9, DB))
    return r


def main():
    import segments as S
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", default=str(Path(__file__).resolve().parents[3]))
    a = ap.parse_args()
    pack = Path(a.pack)
    M = motifs(pack)
    hd, pg, out = B.HERE / "html", B.HERE / "pages", B.OUT / "general"
    for d in (hd, pg, out):
        d.mkdir(exist_ok=True)
    jobs, copy = [], []
    for v in VARIANTS:
        for side, parts in (("front", v["front"](pack, M, v)), ("back", back(pack, M, v))):
            f = hd / ("var_%s_%s.html" % (v["slug"], side))
            f.write_text(B.page(pack, W, H, "\n".join(parts), "Climb27 flyer, %s, %s" % (v["slug"], side)))
            jobs.append(dict(html=str(f), pdf=str(pg / ("var_%s_%s.pdf" % (v["slug"], side))), w=W, h=H))
        copy += [plain(v["head"]), v["sub"], plain(v["cta"]), plain(v["back_head"]), "Scan and pick who you are"]
        copy += ["%s. %s" % (h, t) for _, h, t in v["items"]]
    copy += ["Founders. Investors. Advisers.", "Two days. One festival.", "New to ClimbUK?"]
    (B.HERE / "variant_copy.txt").write_text("\n".join(copy) + "\n")
    (B.HERE / "render_seg.cjs").write_text(S.RENDER_JS)
    (B.HERE / "jobs.json").write_text(json.dumps(jobs))
    subprocess.run(["node", str(B.HERE / "render_seg.cjs"), str(B.HERE / "jobs.json")], check=True)
    from pypdf import PdfReader, PdfWriter
    for i, v in enumerate(VARIANTS, 2):
        wr = PdfWriter()
        for side in ("front", "back"):
            for p in PdfReader(str(pg / ("var_%s_%s.pdf" % (v["slug"], side)))).pages:
                wr.add_page(p)
        name = out / ("climb27_flyer_general-%d_%s_a5.pdf" % (i, v["slug"]))
        with open(name, "wb") as fh:
            wr.write(fh)
        B.set_boxes(name, BLEED)
        print("wrote", name.name)


if __name__ == "__main__":
    main()
