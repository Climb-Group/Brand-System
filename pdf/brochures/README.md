# Climb27 sales brochures

Two brochures for selling Climb27 (30 June and 1 July 2027) and a Who was there pack to send with them, as 16:9 PDFs to send by email or show on screen in a sales call.

| File | Who it is for |
| --- | --- |
| `climb27_exhibitor-brochure.pdf` | Companies taking a stand: why exhibit, the four stand types with a real photo of each, a page for each stand with what it includes and its price, a page of expo stand sizes, a page on how we build the stand so exhibitors just show up, a page on the marketplace (what it is and who it is for), extras for the stand with the print partner, a page of quotes, a page of exhibitor photos and a poster closing page with a QR code to book. 14 pages. |
| `climb27_partner-brochure.pdf` | Partners: what Climb27 is, why partner, how a partnership is built (levels, space options and reach), everything included in every partnership, the branding options, the options in the event app, the session screens and the ticket, the Headline Partner extras, a NatWest spotlight, the zones, how we install the branding before the day, sessions and awards, extra reach, a page of quotes, a page of stage, awards and crowd photos, and a poster closing page with a QR code to book a call. 17 pages. |
| `climb27_who-was-there.pdf` | Anyone weighing up Climb27 who wants to see who came before: one page of the names in the room, the organisations that came back for a second or third edition, the speakers people will know, speakers from well-known organisations, sessions run with well-known companies (Climb23 to Climb26), and 30 quotes (the Climb26 quotes and quotes about ClimbUK in general), with a poster closing page to book a partnership call. It prints a chosen part of the public Who was there page on the ClimbUK website, word for word. 12 pages. |

Contact sheets of every page are in `previews/`.

## The approach

- The layout follows the Climb26 exhibitor brochure: photo-led pages, orange label boxes for the big lines, stand renders with a size badge, and real quotes from people who came.
- Partnerships are sold as options, not fixed tiers. Every partnership is built around what the partner wants, so the partner brochure shows the level (Headline Partner or Partner), the things a partner can own and the extras they can add, and leaves the package to a call.
- No audience sizes, percentages or other figures. Partners and exhibitors are offered meetings with the right people.
- Prices are shown where they are set. All prices are plus VAT.
- Each brochure prints at least 20 real testimonials, and never the same one twice. The quotes are in the copy file in the order they print; the build stops if a brochure has fewer than 20 or repeats one.
- The grounds vary: Dark Brown on two pages at most, and never two pages in a row on the same colour. The build stops if a brochure breaks this.
- Every stand comes with a print voucher from the official print partner, shown on the extras page.

## Change the words

Every printed word is in `climb27_brochures.copy.md`, or `climb27_who-was-there.copy.md` for the Who was there pack. Edit it there and rebuild. The Who was there copy file is written from the website page: when the page changes, run `python3 pdf/_build/wwt_from_page.py <who_was_there.xml>` with the page's template from the website repository, then rebuild. The pack's picks (speakers, sessions, general quotes and the organisations that came back) are lists of names at the top of `wwt_from_page.py`; the script stops if a name is no longer on the page. Its quotes are printed word for word, so the copy checker reads every other line in the pack but not the quotes. In a headline, `[[word]]` is set in Climb Orange and `_word_` in italic. A list is one `- ` line per item, with its parts split by ` | `.

## Rebuild

```bash
NODE_PATH=$(npm root -g) bash pdf/_build/build_brochures.sh
```

Needs Python 3 with Pillow, numpy and segno, and Node with Playwright (Chromium) on `NODE_PATH`. The script:

1. Copies the fonts, the ClimbUK and Climb27 logos, the photos, the illustrations, the images in `_build/img/` and the organisation logos in `_build/logos/` into a working folder.
2. Writes one HTML file per brochure from `pdf/_build/brochures.py` and the copy file, and the Who was there pack from `pdf/_build/who_was_there.py`.
3. Runs every printed word through the climb-voice copy checker and stops on a hard-rule problem.
4. Measures every run of text against what sits behind it and stops if any is under WCAG 2.2 AA.
5. Prints the three PDFs into this folder.

Set `KEEP_HTML=1` to keep the HTML files for review.

## What they follow

- Tokens: the colours and type in `tokens/brand.tokens.json` (Dark Brown, Charcoal, Climb Orange, Tint, Light Grey; Montserrat and Open Sans).
- Skills: climb-visual-style for the layout and climb-voice for the copy.
- Every headline opens on a positive line, with one orange word and one italic word.
- Logos, labels and QR codes never sit over a face; on the closing page the photo sits in its own panel.
- The QR codes go to the partnerships page on www.climb-uk.com, tagged with the brochure they came from.
- The closing page carries the Climb27 mark on its own, never beside the ClimbUK logo. The button sits on the footer's divider, centred on it, and the contact lines sit centred under the button between the mark and the QR code.
- Reading text never sits on an orange page; quotes in orange boxes are white, bold and 19px or larger.
- The venue is not named anywhere until it is announced.

## Common problems

- **The build stops at the copy checker.** A line breaks a climb-voice rule. Fix the line in the copy file, not in the script.
- **The build stops at the contrast check.** It names the page and the text. Move the text onto a solid ground or a stronger fade.
- **A page overflows.** Long copy pushes cards into the footer. Shorten the line in the copy file before changing sizes in the script.
- **The build says the Who was there pack quotes one person twice on a page or on pages close together.** A person with two quotes has one on the first page of their quote group (Climb26, or ClimbUK in general) and one on the last, with other pages between. When a new person with two quotes is picked, check the page order in `build()` in `who_was_there.py`.
- **The build says a brochure prints too few quotes or repeats one.** Add real quotes to `exhibitor.quotes` or `partner.quotes` in the copy file. Never write a quote; copy it word for word from its source.
