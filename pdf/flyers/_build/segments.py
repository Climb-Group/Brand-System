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

UTM = "?utm_source=flyer&utm_campaign=climb27"

# headline: [[word]] is the highlight (Dark Brown on the orange front), *word* is italic.
SEGMENTS = [
    dict(slug="scaling-companies", audience="Scaling companies", noun="business",
         head="Scale with the [[right people]] in the *room*.",
         hero=("crowds_04", (0.5, 0.35)), cta="Get your *ticket*",
         strip=[("climb_recap_03", (0.5, 0.4)), ("meetings_01", (0.5, 0.4)), ("joy_02", (0.5, 0.4))],
         items=[
             ("people", "Find your people",
              "Fellow founders one step ahead, advisers, partners and investors looking for real deal flow."),
             ("lightbulb", "Sessions for your next stage",
              "New markets, talent and leadership, funding options. Built for companies already trading."),
             ("calendar", "Meetings you choose",
              "Book meetings in the ClimbGroup Event App before you arrive, then meet face to face on the day."),
             ("microphone", "Main stage moments",
              "Big moments, roundtables, workshops and the after parties, across two days."),
             ("person-plus", "Bring the team",
              "Each role finds sessions built for their job. Teams of four or more save 25%."),
         ]),
    dict(slug="professional-services", audience="Professional services", noun="firm",
         head="*Your* expertise, in front of the [[businesses that buy it]].",
         hero=("exhibitor_01", (0.5, 0.4)), cta="Get your *ticket*",
         strip=[("exhibitor_02", (0.5, 0.4)), ("meetings_02", (0.5, 0.4)), ("crowds_03", (0.5, 0.4))],
         items=[
             ("briefcase", "New clients",
              "Growing companies that need legal, finance, advisory and technology help, at the moment they need it."),
             ("round-table", "Expertise on show",
              "Roundtables and workshops put you across the table from businesses with a live problem."),
             ("calendar", "Meetings you choose",
              "Book meetings in the ClimbGroup Event App before you arrive, then meet face to face on the day."),
             ("handshake", "Find your people",
              "Fellow firms, advisers and investors to work alongside and send work to."),
             ("person-plus", "Bring the team",
              "Partners, managers and business development each find their own reasons to come."),
         ]),
    dict(slug="founders-seeking-investment", audience="Founders raising investment", noun="raise",
         head="*Raising?* Find investors looking for real [[deal flow]].",
         hero=("climb_isn_investors_hero", (0.5, 0.35)), cta="Get your *ticket*",
         strip=[("meetings_02", (0.5, 0.4)), ("stage_speakers_01", (0.5, 0.4)), ("climb_recap_05", (0.5, 0.4))],
         items=[
             ("money-bag", "Investors looking for deal flow",
              "Angels, funds and lenders from across the whole funding journey come to find their next deal."),
             ("target", "Ready before you pitch",
              "Workshops on pitching, the numbers and the terms, so you know what investors need to see."),
             ("stopwatch", "Investor Speed Networking",
              "A round of short conversations with investors from your sector. Add it to your ticket."),
             ("people", "Fellow founders",
              "Peers who raised before you and will tell you what worked and what they would change."),
             ("ladder", "The next rung",
              "Any stage of your funding journey. Find the investor who fits where your business is now."),
         ]),
    dict(slug="universities", audience="Universities", noun="spinouts",
         head="Put your *spinouts* in front of [[investors]].",
         hero=("exhibitor_03", (0.5, 0.4)), cta="Get your *tickets*",
         strip=[("roundtable_and_workshops_02", (0.5, 0.4)), ("climb_isn_founders_hero", (0.5, 0.4)),
                ("meetings_03", (0.5, 0.4))],
         items=[
             ("rocket", "A stage for your spinouts",
              "Show your spinouts to investors, industry partners and growing businesses."),
             ("money-bag", "Investors looking for deal flow",
              "Angels and funds come to find their next deal. A spinout with a team and a market belongs here."),
             ("compass", "Mentors and advisers",
              "People who have taken companies where your spinouts want to go, ready to share how."),
             ("handshake", "Industry partners",
              "Growing companies and corporates looking for research, talent and new ideas."),
             ("person-plus", "Bring the whole team",
              "Founders, researchers and commercialisation staff each find sessions for their job."),
         ]),
    dict(slug="investors", audience="Investors", noun="deal flow",
         head="Deal flow you can *filter*. Founders [[you choose]].",
         hero=("meetings_02", (0.5, 0.4)), cta="Apply for your *ticket*",
         strip=[("climb_isn_investors_hero", (0.5, 0.4)), ("audience_at_stage_02", (0.5, 0.4)),
                ("climb_drinks_reception", (0.5, 0.4))],
         items=[
             ("magnifier", "See who is coming",
              "Look through the companies attending by stage, sector and region, and pick the ones worth a conversation."),
             ("chat-dots", "You decide who you meet",
              "Founders request meetings. You accept the ones you want and decline the rest."),
             ("stopwatch", "Investor Speed Networking",
              "Opt in for a round of short conversations with founders from your sectors."),
             ("people", "Co-investors in the room",
              "Angels, funds and lenders in one place to compare notes and share deals."),
             ("tickets", "Verified investors are our guests",
              "Apply on the investor page. Once we have verified you, your ticket is issued."),
         ]),
    dict(slug="government-councils", audience="The public sector", noun="businesses",
         head="Bring *your* businesses to [[the room]].",
         hero=("audience_at_stage_03", (0.5, 0.4)), cta="Plan your *delegation*",
         strip=[("roundtable_and_workshops_01", (0.5, 0.4)), ("climb_expo_floor", (0.5, 0.4)),
                ("crowds_01", (0.5, 0.4))],
         items=[
             ("people", "Your businesses, in the room",
              "Bring a delegation of the companies you back for two days of workshops, roundtables and meetings."),
             ("money-bag", "Investors looking for deal flow",
              "Your businesses find angels, funds and lenders looking for their next deal."),
             ("map", "Show your region",
              "Partner with ClimbUK to put your region and its businesses on stage."),
             ("handshake", "Planned with you",
              "A Partner Manager plans your delegation and your presence with you, from first call to the day."),
             ("globe", "The whole ecosystem",
              "Universities, investors, incubators and other public sector teams in one place."),
         ]),
    dict(slug="consultants", audience="Advisers and consultants", noun="practice",
         head="Meet the *people* who [[buy expertise]].",
         hero=("roundtable_and_workshops_01", (0.5, 0.4)), cta="Get your *ticket*",
         strip=[("climb_consultants_expert", (0.5, 0.4)), ("meetings_01", (0.5, 0.4)), ("joy_02", (0.5, 0.4))],
         items=[
             ("briefcase", "Clients with a live problem",
              "Scaling companies, universities and the public sector looking for advice they can act on."),
             ("round-table", "Show what you know",
              "Share your know-how in roundtables, workshops and on stage, with a home in the Advisor Zone."),
             ("handshake", "Partners to bid with",
              "Professional services firms and fellow advisers to build joint bids with."),
             ("calendar", "Meetings you choose",
              "Book meetings in the ClimbGroup Event App before you arrive, then meet face to face on the day."),
             ("people", "A community that sends work",
              "People here share what they have learned and send each other work, long after the festival."),
         ]),
    dict(slug="incubators-accelerators", audience="Incubators and accelerators", noun="cohort",
         head="Put your *cohort* in front of the [[right people]].",
         hero=("climb_isn_founders_hero", (0.5, 0.35)), cta="Get your *tickets*",
         strip=[("climb_recap_01", (0.45, 0.4)), ("meetings_03", (0.5, 0.4)), ("crowds_02", (0.5, 0.4))],
         items=[
             ("people", "Meetings for every founder",
              "Investors, advisers and partners, with meetings booked in the ClimbGroup Event App before they arrive."),
             ("rocket", "A stage for the programme",
              "Partner with ClimbUK for a cohort showcase slot in front of the whole festival."),
             ("lightbulb", "Sessions for their next stage",
              "Workshops on raising, hiring and new markets, for founders already trading."),
             ("globe", "The whole ecosystem",
              "Universities, the public sector, investors and other programmes in one place."),
             ("person-plus", "Bring the cohort",
              "Teams of four or more save 25%, so the whole cohort can come."),
         ]),
    dict(slug="what-is-climbuk", audience="Anyone new to ClimbUK", noun="business",
         eyebrow="New to ClimbUK?", path="climb-uk.com",
         sub="Two days for growing businesses and the people who back them.",
         qr="https://www.climb-uk.com/?utm_source=flyer&utm_campaign=climb27#climb27_choose",
         head="The [[festival]] for business *growth*.",
         hero=("climbteam_01", (0.5, 0.45)), cta="Find *your* Climb27",
         strip=[("audience_at_stage_01", (0.5, 0.4)), ("meetings_01", (0.5, 0.4)), ("crowds_04", (0.5, 0.4))],
         items=[
             ("sparkles", "What ClimbUK is",
              "Two days where founders, investors, advisers, universities and the public sector meet, learn and do business together."),
             ("people", "Who comes",
              "Growing businesses, the investors who back them, the firms that help them and the programmes that support them."),
             ("microphone", "What happens",
              "Main stage moments, roundtables, workshops, Investor Speed Networking, the ClimbAwards and the after parties."),
             ("ladder", "Your next step",
              "Whatever stage your business is at, meet the people who can help with the next one."),
             ("compass", "Where you fit",
              "Scan the code, pick who you are, and see what Climb27 means for you."),
         ]),
]


def rich(s, hl):
    s = html.escape(s)
    s = re.sub(r"\[\[(.+?)\]\]", r'<span style="color:%s">\1</span>' % hl, s)
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)


def plain(s):
    return s.replace("[[", "").replace("]]", "").replace("*", "")


def flyer(pack, s):
    W, H = 148 + 2 * BLEED, 210 + 2 * BLEED
    b, m = BLEED, BLEED + 10
    slug = s["slug"]
    path = s.get("path", "climb-uk.com/for/" + slug)
    qr = s.get("qr", "https://www.climb-uk.com/for/" + slug + UTM)
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
             'text-transform:uppercase;color:%s">%s</div>' % (m, cut + 6, DB, html.escape(s.get("eyebrow", "For " + s["audience"].lower()))))
    f.append('<h1 class="abs disp" data-fit="1" style="left:%smm;top:%smm;width:%smm;height:40mm;font-size:36pt;color:%s;'
             'line-height:1.0">%s</h1>' % (m, cut + 13, W - 2 * m, WH, rich(s["head"], DB)))
    f.append('<div class="abs" style="left:%smm;top:%smm;width:16mm;height:1.6mm;border-radius:1mm;background:%s"></div>'
             % (m, cut + 57, DB))
    f.append('<div class="abs mont" style="left:%smm;top:%smm;width:%smm;font-weight:700;font-size:14pt;color:%s;line-height:1.2">'
             '%s</div>' % (m, cut + 62, W - 2 * m, WH, html.escape(s.get("sub", TAGLINE))))
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
    copy = [s["audience"], plain(s["head"]), s.get("sub", TAGLINE), DATES, plain(s["cta"]), "%s %s" % ("What Climb27 does for your", s["noun"])]
    copy += ["%s. %s" % (h, t) for _, h, t in s["items"]]
    return W, H, front, back, copy


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
    jobs, copy = [], []
    for s in SEGMENTS:
        if a.only and a.only not in s["slug"]:
            continue
        W, H, front, back, c = flyer(pack, s)
        copy += c
        for side, doc in (("front", front), ("back", back)):
            f = hd / ("seg_%s_%s.html" % (s["slug"], side))
            f.write_text(doc)
            jobs.append(dict(html=str(f), pdf=str(pg / ("seg_%s_%s.pdf" % (s["slug"], side))), w=W, h=H, slug=s["slug"]))
    (B.HERE / "segment_copy.txt").write_text("\n".join(copy) + "\n")
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
