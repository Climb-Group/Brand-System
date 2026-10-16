---
name: climb-visual-style
description: The ClimbUK, ClimbGroup and Climb27 visual identity for anything made to be seen - web sections, emails, social graphics, video, slides, wallpapers, call backgrounds, print, merch, signage and stage screens. Load it whenever you design, generate, lay out, recolour or review a visual asset for these brands, in code or in a design app, and pair it with climb-voice for any words on the asset.
license: Proprietary
metadata:
  owner: ClimbGroup marketing
  tokens: tokens/brand.tokens.json
  version: "1.8"
---

# ClimbUK visual style

**A festival poster with a clear next step.** Full festival: fun, punchy, exciting. Real crowds under stage light, huge uppercase type with one word in orange and one in italic, stickers slapped on, logos and names drifting past, and Climb Orange that glows. Never a corporate conference look. The reference point for ambition is Slush (the atmosphere, never the formats or the artwork); the reference for feel is the Climb27 homepage and the affiliate page (climb-uk.com; original motif vectors in `reference/motifs/`).

All values come from `tokens/brand.tokens.json` (CSS in `tokens.css`, SCSS in `_tokens.scss`). Never type a hex value that is not in that file. `#EC752A` is retired: if you find it, replace it with `#E8712A`.

## The five rules

1. **Dark first.** Default ground is Dark Brown `#1E0F05` or Charcoal `#242322`. Light grounds (White, Light Grey) are for reading-heavy pieces: documents, long emails, forms.
2. **Orange leads, it does not flood.** One orange button or call to action per section, slide, post or screen. Around it, orange markers are welcome: an orange word, the short orange rule, a sticker, a glow. Full orange grounds are for the big moments: the partner pitch, the final call to action.
3. **Type does the shouting.** Montserrat Bold or Black, uppercase for display lines, tight leading (0.98 to 1.1), slightly negative tracking. One word in Climb Orange and one in italic per headline ("THE FESTIVAL FOR BUSINESS *GROWTH*.", with FESTIVAL in orange); every headline opens positive (climb-voice, Headlines and titles). A short orange rule or a tracked eyebrow sits above. Open Sans for everything you read. Never more than two sizes of display type on one view.
4. **Real people, real light.** Photography of actual attendees, speakers and stage moments, with consent: laughing faces, orange lanyards, branded backdrops, crowds, close conversations. Full colour under a Dark Brown fade where text sits; dense photo walls rather than one lonely picture. No stock handshakes, no empty rooms, no generic skylines, and nothing that can be misread out of context (a hug that looks like a struggle). A cover is one photo or a three-photo header (one big, two stacked beside it).
5. **Contrast is not optional.** Pick a preset (below) and use its pairs. White on Climb Orange only at 19px bold or larger (or the print equivalent: 14pt bold). Check anything new against the tokens build.

## Grounds and pairs (the five presets)

| Preset | Ground | Text | Headings | Links | Orange you may use | Primary button |
| --- | --- | --- | --- | --- | --- | --- |
| 1 White | #FFFFFF | Body Slate #4D5B7C | Charcoal #242322 | #A94B12, underlined | Small: #C55308. Large: #E8712A | #E8712A, white 19px bold label |
| 2 Light Grey | #E9E9E9 | Body Slate #4D5B7C | Charcoal #242322 | #843A0E, underlined | Small: #B04902. Large: #D5641E | as preset 1 |
| 3 Dark Brown (default) | #1E0F05 | White | White | Orange Tint #F2AE86 | #E8712A at any size | as preset 1 |
| 4 Climb Orange | #E8712A | White, large only | White | White, underlined | none | White fill, #C55308 label |
| 5 Charcoal | #242322 | Light Grey #E9E9E9 | White | Orange Tint #F2AE86 | #E8712A at any size | as preset 1 |

Never: Light Grey or Body Slate text on any orange; Dark Brown labels on orange buttons (harder to read; use the white 19px bold label); orange on orange; Climb Orange headings on Light Grey; a lighter hover state.

## Accessibility themes and sizes

The baseline is WCAG 2.2 AA, with AAA wherever it is small and easy. Every colour and size has an AAA variant in the tokens, so a piece can switch without new values:

- **Themes:** Dark, Light, AAA-Dark and AAA-Light (`theme.*` in the tokens). On the web set `data-climb-theme="aaa-dark"` (or `dark`, `light`, `aaa-light`) on any element; the short `--climb-*` names re-point to that theme.
- **Sizes:** `data-climb-size="aaa"` switches body and small type, eyebrows, line length and touch targets to their AAA values.
- **Touch targets:** 44px (`layout.target-min`) by default. 24px (`layout.target-compact`) is the WCAG 2.2 AA minimum, kept as a variant for dense rows such as signature icons; use it only where 44px will not fit.
- A live demo of the switches: `accessibility/aaa-demo.html`.

## Graphic language

The motifs all come from the Investor Ladder (a business climbing rung by rung to its next investor) and from the stage, never from sport climbing or mountains. Use one motif family per piece, in Climb Orange or as a tone of the ground (for example white at 8 to 16 percent opacity on Dark Brown). Motifs are decoration: never put meaning only in a motif, and keep text off busy pattern areas.

- **The Ascent.** Rising steps and stacked chevrons: the rungs of the Investor Ladder, read as upward progress. Use as dividers, corner marks, progress bars, frame edges.
- **Contours.** Flowing contour rings spreading out from one point, like growth moving out from a business at the centre. Never drawn as a map or a mountain. Use as large, quiet background fields on dark grounds, on merch and on wall graphics.
- **Stage Light.** Soft beams and glows of Climb Orange and Orange Tint cutting across a dark ground. Use for Main Stage Moments, screens, video and hero images.
- **Connections.** Dots joined by fine lines, people finding each other. Use for Find Your People, networking, partner and audience pieces.
- **Highlight bar.** A solid Climb Orange bar behind or under one word of a headline: the poster and slide version of the orange word.

## Illustrations and icons

The house set is in `illustrations/` (one clean 200x200 SVG per object, with a title and description), drawn by `generators/illustrations.py`. The style: smooth, confident strokes like a tablet pen, round caps and joins, with a soft low-opacity fill shape behind each object for depth. Never crude or wobbly lines. Line and fills use `currentColor` (Climb Orange by default through `--doodle-ink`); cut lines use `--doodle-ground` (Dark Brown by default), so one file works on every preset. Draw a new object in the same generator rather than by hand, so it matches. Square icons sit centred, with no registered mark.

## Festival devices

These carry the energy. Use two or three per piece, not all of them at once.

- **The orange word and the italic word** in a display line.
- **The short orange rule** (4rem by 6px, rounded) above a statement, and tracked uppercase eyebrows.
- **Stickers:** small tags tilted -3 to -4 degrees, Climb Orange with Dark Brown text (or Dark Brown with White), pinned to a card corner or a photo. A sticker on a diagonal cut sits with the cut running through its middle, and a date sticker is big enough to read first.
- **Ticket cards:** a dark glass card with stub notches cut into both sides and a dashed tear line, holding the offer and the one button.
- **Photo cards and walls:** photos with the title on top and the line at the bottom under a Dark Brown fade; a mosaic of squares with one big tile.
- **Lineups and marquees:** names set like a festival poster (biggest first, separated by orange slashes or dots) and logo rows drifting in alternate directions.
- **Cut edges and glow:** a diagonal top edge from one section into the next; an orange stage-light glow in a dark corner; orange glows (not grey shadows) under orange buttons.
- **Photo fades:** a full-width photo faded to Dark Brown on the words' side (or Climb Orange on an orange section), the photo showing through on the other, ending solid so it runs into the next section. Recipes in `guidelines/photography.md`.
- **Ticket progression:** outlined offer cards with one picked out in orange, a release ladder (closed grey, open orange with "left at this price", next as dashed outlines rising with the price) and sold-out states that stay visible. Rules in `guidelines/ui.md`, "Ticket pages".
- **Outline numerals:** giant numbers in Montserrat ExtraBold (800) with no fill and a Climb Orange stroke of about 1% of the size (4px at 380px, never under 2px), letter spacing -0.04em. For section numbers 01 to 10 (decorative, `aria-hidden`, with the real heading in text beside them) and the odd big stat. One size per view, numbers only. Rules in `guidelines/ui.md`, "Outline numerals"; web classes `climb-outline-num`, `climb-outline-num-sm`, `climb-numbered`, `climb-outline-marquee`.
- **Pull links:** a small uppercase line at the foot of a section with a down arrow, handing the reader on.

Motion, elevation and UI states are in `guidelines/` (`motion.md`, `ui.md`); print colours (Pantone, CMYK, RAL) in `print.md`. On the web, all of these are ready-made as live components in `components/hub/` and as website blocks in the website module.

## Where things are in the brand pack

| Need | Folder |
| --- | --- |
| Colours, type, spacing, motion values | `tokens/` |
| Logo masters (SVG, PNG, contact sheets) | `logos/<Brand>/`, each with a README saying which variant suits which ground |
| Illustrations and background shapes | `illustrations/`, `illustrations/shapes/` |
| Social and signature icons, signature buttons | `icons/social/` |
| Event photography (consented) | `photos/` |
| Fonts (OFL) | `fonts/ttf/` and `fonts/otf/` for apps and font uploads, `fonts/*.woff2` for web pages only |
| Live, theme-switchable components | `components/hub/` |
| Asset generators (call backgrounds, wallpapers, social, email, print kits) | `generators/` |
| Previews and contact sheets | `previews/` |
| One-page key rules and the guidelines book per brand (PDF) | `pdf/one-page/`, `pdf/guidelines/` |
| Office and video templates, with install guides | `templates/office/`, `templates/video/` (motion clips in the release download) |
| Tools and skills for AI assistants | `ai/` (`kit.json`, `tools/brand_rules.py`) |
| Media kit downloads and interactive brand pages | `media-kit/`, `web/` |

See `references/elements.md` for how each motif is built and scaled.

## Logo use

- Use the master files only, never a re-drawn or re-coloured copy. Variants: full colour, full colour for Light Grey grounds, reversed (dark grounds, the default), mono dark, mono white, and a tagline lockup with "The Festival for Business Growth" (no dates or places baked in).
- Wordmark colours: Climb Orange `#E8712A` and Charcoal `#242322` on light grounds; Climb Orange and White on dark grounds. On Light Grey use the grey-ground variant (Orange Large on Grey `#D5641E`).
- Square icons: the li monogram for favicons, app icons and anything under 64px; the stacked icon ("Climb / UK", "Climb / Group", "Climb / 27") for social avatars and larger squares.
- Transparent first: logos, icons, favicons and app tiles default to a transparent background; each also comes on solid White, Dark Brown and Climb Orange (`-on-white`, `-on-ground`, `-on-orange`). On orange the mark is one-colour white.
- Clear space: the height of the large "C" in Climb on every side, around the whole logo (registered mark included). Minimum width: 120px on screen, 30mm in print; below that, use the square icon.
- Never stretch, rotate, outline, add effects, or set the logo on a busy part of a photo. On photos, sit it on the darkened area or use the filter.
- ClimbUK is the brand on the poster. ClimbGroup appears as the organisation (footers, legal, corporate decks). An edition mark (Climb27) leads on event pieces, with ClimbUK as the endorsement.

## Making an asset

1. Find the surface in `references/surfaces.md`: size, safe zone, format, and which preset and motif suit it.
2. Start from a brand template, never a blank canvas: Word, Excel and PowerPoint files from `templates/office/<Brand>/`, video titles, lower thirds, LUT and loops from `templates/video/<Brand>/`, and design-app swatches from `tokens/tokens.css`.
3. Lay out: ground or photo, one display line (with its orange word and italic word), one or two festival devices or one motif, the logo in its corner, one call to action if the surface has one.
4. Write any words with the climb-voice skill and run its checker. Before the venue announcement, no venue or city on anything.
5. Check: contrast pairs, safe zone, logo clear space, file name and format from the surface table.

These rules hold on every platform. When the asset is built for a particular platform, also load that platform's own skill if the pack has one (for an Odoo website: `climb-odoo-pages`), and only then.

## Before you finish

- Every colour is a token. No `#EC752A`.
- One orange call to action per view, with orange markers around it, and it still feels like a festival, not a conference.
- Put buttons in their own block (a `p` or `.climb-ctas` row) with at least 24px (`space-5`) above any list or paragraph. Never place a button straight against a list. In a row of cards (offers, stands, plans), every button sits on one shared line: the card is a flex column, its last block gets `margin-top: auto`, and the highlighted card is never raised at rest.
- Text meets its contrast pair at the size it will be seen (screens and signage: check at viewing distance). Hand-held print (flyers, leaflets, programmes) uses 12pt or larger for every line, with bleed of 5% of the shorter trim edge (at least 3mm): see `guidelines/print.md`. Logos sit on a calm ground (a fade or solid), never over hands or faces; move the photo down to make room rather than shrinking the logo.
- On a ticket page the next step (a ticket or call button) is never more than two scrolls away, and release or sold-out states are written in words, not colour alone.
- The file is named `<brand>_<surface>_<variant>_<size>.<ext>`, for example `climb27_zoom-bg_stage-light_1920x1080.png`.
- Anything you show as a preview exists in the brand pack (and the shared brand hub) as a real file, not only as a screenshot. Hub components are live HTML and CSS, so the theme and size switches work on them.
- Any brand preference or decision a person gave you while you worked is now in this skill, its guideline and, where it can be checked, the copy checker (see "The pack learns as it goes" in the brand pack's AGENTS.md). Do not leave it only in a chat or a memory.
