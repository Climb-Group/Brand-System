# Climb27 sales brochures

Two brochures for selling Climb27 (30 June and 1 July 2027), as 16:9 PDFs to send by email or show on screen in a sales call.

| File | Who it is for |
| --- | --- |
| `climb27_exhibitor-brochure.pdf` | Companies taking a stand: why exhibit, the four stand types (starter pod, display stand, expo stand and marketplace table) with what each includes and its price, extras for the stand, quotes from Climb26 exhibitors and a QR code to book. 10 pages. |
| `climb27_partner-brochure.pdf` | Partners: why partner, how a partnership is built, the branding options (website, event app, badges, a zone, the VIP space, the kiosks), the zones, sessions and awards, extra reach, quotes and a QR code to book a call. 10 pages. |

Contact sheets of every page are in `previews/`.

## The approach

- The layout follows the Climb26 exhibitor brochure: photo-led pages, orange label boxes for the big lines, stand renders with a size badge, and real quotes from people who came.
- Partnerships are sold as options, not fixed tiers. Every partnership is built around what the partner wants, so the partner brochure shows the level (Headline Partner or Partner), the things a partner can own and the extras they can add, and leaves the package to a call.
- No audience sizes, percentages or other figures. Partners and exhibitors are offered meetings with the right people.
- Prices are shown where they are set. All prices are plus VAT.

## Change the words

Every printed word is in `climb27_brochures.copy.md`. Edit it there and rebuild. In a headline, `[[word]]` is set in Climb Orange and `_word_` in italic. A list is one `- ` line per item, with its parts split by ` | `.

## Rebuild

```bash
NODE_PATH=$(npm root -g) bash pdf/_build/build_brochures.sh
```

Needs Python 3 with Pillow, numpy and segno, and Node with Playwright (Chromium) on `NODE_PATH`. The script:

1. Copies the fonts, the ClimbUK and Climb27 logos, the photos, the illustrations and the images in `_build/img/` into a working folder.
2. Writes one HTML file per brochure from `pdf/_build/brochures.py` and the copy file.
3. Runs every printed word through the climb-voice copy checker and stops on a hard-rule problem.
4. Measures every run of text against what sits behind it and stops if any is under WCAG 2.2 AA.
5. Prints both PDFs into this folder.

Set `KEEP_HTML=1` to keep the HTML files for review.

## What they follow

- Tokens: the colours and type in `tokens/brand.tokens.json` (Dark Brown, Charcoal, Climb Orange, Tint, Light Grey; Montserrat and Open Sans).
- Skills: climb-visual-style for the layout and climb-voice for the copy.
- Every headline opens on a positive line, with one orange word and one italic word.
- Logos, labels and QR codes never sit over a face; on the closing page the photo sits in its own panel.
- The QR codes go to the partnerships page on climb-uk.com, tagged with the brochure they came from.
- The venue is not named anywhere until it is announced.

## Common problems

- **The build stops at the copy checker.** A line breaks a climb-voice rule. Fix the line in the copy file, not in the script.
- **The build stops at the contrast check.** It names the page and the text. Move the text onto a solid ground or a stronger fade.
- **A page overflows.** Long copy pushes cards into the footer. Shorten the line in the copy file before changing sizes in the script.
