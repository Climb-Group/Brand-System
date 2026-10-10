# Asset catalogue

Generates ClimbUK, ClimbGroup and Climb27 assets from the brand tokens, the logo masters in `../logos/` and the five motif families in `motifs.py` (built to `.agents/skills/climb-visual-style/references/elements.md`).

```bash
python3 generators/catalogue.py build/assets      # HTML per asset, copy-checked, plus manifest.json
node generators/render.mjs build/assets           # PNGs in build/assets/png
node generators/render.mjs build/assets call-bg   # only names containing "call-bg"
node generators/render.mjs build/assets set=festival-kit           # only the festival kit
node generators/render.mjs build/assets "^climb27_share,group=Print and merch"
```

The filter is a comma separated list and an asset renders when any item matches: a plain word matches names that contain it, `^prefix` matches the start of the name, `group=Name` a manifest group and `set=name` a manifest set (the festival kit entries carry `set: festival-kit`). Pages that shrink lines to fit flag the body when they are done, and `render.mjs` waits for that before the screenshot.

`render.mjs` needs Playwright and Chromium. Set `CHROMIUM_PATH` to use a specific browser, or `PLAYWRIGHT_MODULE` when Playwright is installed outside the project. `catalogue.py` exits 1 if any copy on an asset breaks the climb-voice rules (the venue embargo is on). No asset carries a venue, city or location name.

## Resolution rule

4K by default, always the highest resolution available, never upscale. Screen and stage pieces are laid out at their full pixel size. Pieces with a fixed platform size (social headers, concept packs, the email footer) are laid out at the platform size and rendered at 2x device scale: each manifest entry has a `scale`, `render.mjs` opens one browser context per scale, and the file name carries the real pixel size (for example `_2256x382` for the 1128x191 LinkedIn company banner). Entries marked `transparent` are saved with no background. Print pieces are rendered as sRGB previews at the stated dpi; the printer still gets CMYK PDF artwork with bleed (see `../guidelines/print.md`).

## What it makes

| Group | Set | Sizes (pixels) | Brands |
| --- | --- | --- | --- |
| Calls | Video call backgrounds, four layouts per brand (stage-light: corner glow and hero drawing; contours: contour field, slab and drawings; connections: duotone photo edges; ascent: orange slab with chevrons). Logo top left, the centre 1800x1400 kept calm, a sticker and drawings in the margins | 3840x2160 | Climb27, ClimbUK, ClimbGroup |
| Wallpapers | Desktop wallpapers: stage-light is photo led (tilted photo cards over a blurred duotone), contours is type led, connections is illustration led (a hero drawing with satellites on dashed links), ascent is an orange slab with a rocket. The left fifth stays quiet for icons | 2560x1440, 3840x2160, 5120x2880 | Climb27, ClimbUK, ClimbGroup |
| Wallpapers | Phone wallpapers, the same four ideas; the top quarter (clock) and the bottom 12 percent (dock) stay clear | 1179x2556, 1440x3120 | Climb27, ClimbUK |
| Social | LinkedIn company banner, X header, Facebook cover (2x): brand line, hero drawing and photos, inside each platform's safe area (page logo or avatar bottom left on LinkedIn and X, side crop on Facebook phones) | 2256x382, 3000x1000, 3280x1248 | Climb27, ClimbUK, ClimbGroup |
| Social | Share kit: "See you there" personal LinkedIn banner (2x), a ticket card in the right two thirds | 3168x792 | Climb27 |
| Social | Concept packs: Find Your People (bubbles), Main Stage Moments (microphone), Bigger Stage (rocket); post, story and LinkedIn square each with its own layout (2x) | post 2160x2700, story 2160x3840, LinkedIn 2400x2400 | Climb27 |
| Social | Email footer preview (2x; the live version is HTML, `email/footer.html`) | 1200 wide | ClimbUK |
| Stage and screens | Holding and walk-in slides, one per concept line | 3840x2160 | Climb27 |
| Stage and screens | Lower third, speaker name and role placeholders, edition bug top right, transparent PNG | 3840x2160 | Climb27 |
| Stage and screens | Logo sting end frame, tagline lockup and dates | 3840x2160, 2160x3840 | Climb27 |
| Stage and screens | Wayfinding screens with Ascent chevrons: Find Your People, Main Stage Moments | 2160x3840 | Climb27 |
| Print and merch | A2 posters at 150 dpi, one per concept line, each with its own layout: photo cards under the bubbles, a giant microphone under the stage light, a rocket leaving an orange slab | 2480x3508 | Climb27 |
| Print and merch | Pull-up banner 850x2000mm at 100 dpi: line, photo cards, rocket and microphone, QR ticket card; bottom 300mm free of text | 3346x7874 | Climb27 |
| Print and merch | Badge A6 at 300 dpi: name, company, ghosted drawings in the top band, a cut orange "Delegate" role band | 1240x1748 | Climb27 |
| Print and merch | Lanyard strap 900x20mm at 300 dpi: monogram, wordmark and drawings repeating | 10630x236 | Climb27 |
| Print and merch | Tote 380x420mm at 150 dpi, Dark Brown: all over drawing pattern with "Find your people" on a ticket | 2244x2480 | Climb27 |
| Print and merch | T-shirt back print 300x400mm at 150 dpi for dark garments, transparent PNG: one big drawing, the line and the mark | 1772x2362 | Climb27 |
| Print and merch | Sticker sheet A4 at 300 dpi: die cut stickers of the drawings and lines (preview; the cut path is a separate layer for the printer) | 2480x3508 | Climb27 |
| Email banners | Campaign banner under the signature, 720x205 layout at 2x and 4x: Bigger Stage, Find Your People, Main Stage Moments, Get Your Ticket (Climb27), Partner (ClimbUK), Festival (ClimbGroup), plus a Dark Brown version of Bigger Stage | 1440x410, 2880x820 | Climb27, ClimbUK, ClimbGroup |
| Stage and screens | Festival kit: speaker name card, huge two line name with the pill bar, role line with an italic company, slab corner, grain | 3840x2160 | Climb27 |
| Stage and screens | Festival kit: speaker name card with a photo slot faded to Dark Brown (Climb26 stand-in photo) | 3840x2160 | Climb27 |
| Stage and screens | Festival kit: lower third v2, Dark Brown name panel with the pill bar, slab and edition mark, transparent PNG | 3840x2160 | Climb27 |
| Social | Festival kit: share tiles "I'm attending Climb27", "I'm speaking", "I'm exhibiting", "We're partnering at Climb27"; one layout, only the verb and the role sticker change; photo slot faded to Dark Brown, ticket card at the foot with the dates (2x) | post 2160x2700, story 2160x3840 | Climb27 |
| Social | Festival kit: affiliate "Just joined" ticket card, affiliate logo chip, `{Your code}` printed in the stub (2x) | post 2160x2700, story 2160x3840 | Climb27 |
| Social | Festival kit: speaker announcement, name card style over a faded photo (2x) | 2160x2700 | Climb27 |
| Print and merch | Festival kit: photo pull-up banner v2, 850x2000mm at 100 dpi: checkerboard of photos and Dark Brown or Climb Orange panels with chevron bullets, QR ticket card at eye level, URL band, bottom 300mm left empty | 3346x7874 | Climb27 |
| Print and merch | Festival kit: document covers A4 at 300 dpi, "Exhibitor agreement" and "Partner proposal", photo collage faded to Dark Brown | 2480x3508 | Climb27 |
| Print and merch | Festival kit: meeting table signs, A5 flat at 300 dpi and A4 tent card face (297x105mm) at 300 dpi, tables 1 to 3 as samples, optional Hosted by slot (shown on 1 and 2) | 1748x2480, 3508x1240 | Climb27 |

For a download kit, convert the opaque PNGs to JPG at quality 90 and keep the transparent ones (both lower thirds, t-shirt) as PNG, in one folder per group: Calls, Wallpapers, Social, Stage and screens, Print and merch, Email banners.

## Hand drawn illustrations

`illustrations.py` draws our own set of line objects tied to the messages, and `illustrations/` holds each one as a clean standalone SVG (200x200 box). Run `python3 generators/illustrations.py` to rewrite the files after a change.

| Drawing | Message |
| --- | --- |
| microphone, spotlight, stage, record | Main stage moments, speaking, DJ sets |
| badge (text slot: EXHIBITOR, SPEAKER, PARTNER, DELEGATE) | Roles; `badge-speaker.svg`, `badge-partner.svg` and `badge-delegate.svg` are ready made |
| tickets, calendar (30 June and 1 July) | Get your ticket, save the dates |
| bubbles, people, handshake, coffee, glasses | Find your people, meetings, after parties |
| rocket, chart, summit, lightbulb, megaphone | Your business. Bigger stage. Growth, ideas, announcements |
| envelope, clipboard, laptop, phone, pin | Inbox, agenda, the ClimbGroup Event App, where to be (never a place name) |
| trophy | ClimbAwards |
| sneaker, sparkles, arrow | Merch and small accents |

How they are drawn: each object is a set of plain paths that the code turns into a pen line, one weight with round caps, gentle wobble, closed shapes that overrun their start, a second loose pass on some strokes, and small orange fills printed slightly off register with detail cut back in the ground colour. No venue or building appears in the set.

Colour: the line and the fills use `currentColor`, which defaults to Climb Orange through `--doodle-ink`; cut lines use `--doodle-ground` (default Dark Brown). Set either variable on the SVG or a parent to recolour, for example White at low opacity for a ghost on a photo.

How to use them (the rule the layouts follow): one hero drawing tied to the message, with two or three ghosted copies behind it (the same drawing, rotated, 12 to 30 percent opacity, smaller or larger), never behind or touching the type. In code: `I.svg(name, label=...)` returns inline markup, `I.place(name, x, y, size, rotate=, opacity=)` an absolutely positioned copy; in `poster_kit.py`, `hero()` places a drawing with its ghosts, `scatter()` spreads drawings through a margin while avoiding given boxes, and `pattern()` makes an all over merch pattern.

## Poster kit

`poster_kit.py` builds Calls, Wallpapers, Social and Print and merch (`catalogue.assets()` calls it). It reuses the festival kit devices (ticket cards, stickers, display lines with `[[orange]]` and `*italic*` words, grain) and adds: `glow()` for the orange stage glow from a corner, `head()` for the display lines with the short orange rule and an eyebrow, `slab_poly()` for diagonal cuts, `chevrons()`, `date_ticket()` for a ticket with the edition mark, dates and URL, and `Kit.pic()` for photos (cover crop, optional duotone, blur, tilt, fade and shadow). Sticker positions can be measured from the right edge (`side="right"`) so long labels never leave the canvas.

Photo resolution: the Climb26 photos are 1600px wide. Crisp photos sit in tilted photo cards no larger than the source; anywhere a photo has to cover more (full bleed on 4K and 5K screens, call background edges, story backgrounds), it is blurred, set as a duotone or held under a heavy fade. `Kit.pic()` checks every crisp photo and `catalogue.py` prints a `RESOLUTION` line for any shown above its own size, so a new layout cannot slip an upscale through. Swap in full resolution photography for final print files.

## Email banners and the signature

The email banners (`email_banner()` and `EMAIL_BANNERS` in `catalogue.py`) follow one layout: a copy band 92px deep with the uppercase headline in White and one word in Dark Brown, a Dark Brown subline, and the mono white logo top right with www.climb-uk.com under it; then a strip of five real Climb26 photos from `climb_website_brand/static/src/img/`, cut to cover with 3px gaps; then an 8px Climb Orange foot. The text column stops short of the logo column, and a long headline steps down from 27px (never below 20px) so it never runs into the logo. The `-dark` variant swaps the band to Dark Brown with the emphasis word in Climb Orange, an Orange Tint subline and the reversed logo, for audiences that read mostly in dark mode. Files are named `<brand>_email-banner_<key>_<size>.jpg`; host the 1440x410 file and show it at width 720.

```bash
python3 generators/catalogue.py build/assets
node generators/render.mjs build/assets email-banner
```

`email/signature-template.html` is the signature that carries the banner: a table layout up to 720px wide with live text. Left column: "Kind regards,", name, role, a "Book a meeting with me" link, T: and M: numbers, email and climb-uk.com. Right column: the ClimbUK wordmark over a row of outline icons (Facebook, X, Bluesky, Instagram, LinkedIn). Under it: the italic Helpdesk notice, the banner linking to `{Campaign link}`, and a small confidentiality line. Placeholders are in braces; images point at `{Hosted URL}`. Inline colours are preset 1 (White ground); a dark colour scheme block switches text to Light Grey, links to Climb Orange and the wordmark to the reversed file. The comment at the top of the file explains the choice.

The outline icons are made by `social-icons/build_social_icons.mjs` (run it with `--outline` to build only them): a rounded square drawn as a 2px line at 24px with the glyph inside, in Orange, White and Charcoal, as `icon_<name>_<colour>_outline.svg` plus `@2x` and `@3x` PNG, for facebook, x, bluesky, instagram, linkedin, tiktok, youtube, email, phone, website and book. Orange reads on White and on Charcoal (3.1:1 and 5.1:1); use Charcoal on White when you need more contrast, White on dark grounds.

## Festival kit

`festival_kit.py` builds the templates that came out of the Climb26 design review (ideas carried into our own style, no artwork copied). `catalogue.assets()` calls it, so the copy checker and the manifest cover it like any other asset. It adds three finishing marks to `motifs.py`:

- `slabs()`: angled Climb Orange corner slabs whose cut edge runs at the Ascent chevron slope (`CHEVRON_SLOPE`, 0.9). One or two corners, never four.
- `peak()`: one contour line that walks in from the edge, climbs a shoulder to a summit and drops away at the chevron slope. Used quietly (White at 16 percent) behind the table numbers.
- `grain()`: fine film grain from an SVG `feTurbulence` filter at low opacity, for flat dark grounds on screens and print. Kept off social tiles and email.

Devices it shares across the kit:

- Pill bar: a rounded Climb Orange bar laid across the top of the letters of the first name line. One per layout; it does not replace the orange word in a display line.
- Ticket card (`ticket()`): Charcoal body with semicircle stub notches, a dashed tear line and a Climb Orange stub, with the stub on the right or at the bottom.
- QR placeholder (`qr()`): a neutral QR-like square labelled QR in the middle. It does not scan; swap in the real code before print.
- Stickers: Climb Orange with Dark Brown text, tilted -3 degrees, naming the role (Speaker, Attendee, Exhibitor, Partner, Just joined).
- Display lines: `[[word]]` is the orange word and `*word*` the italic word. Long names and lines shrink to fit their box (class `fit`), and lines in a `fitgroup` share one size.

Placeholders are in braces and are swapped per person before export: `{First name}`, `{Last name}`, `{Speaker name}`, `{Role}`, `{Company}`, `{Your name}`, `{Session title}`, `{Affiliate logo}`, `{Your code}` (required on every affiliate card), `{Zone name}` and `{Host logo}`. Photo slots use Climb26 photos from `climb_website_brand/static/src/img/` as stand-ins; those are 1600px wide, so put in the person's own photo at full resolution for final files. Italic Montserrat 700 and 800 and Open Sans 600 live in `fonts/` next to this file (OFL, same release as `../fonts/`).

Table signs: render any table number by calling `table_sign(C, n, "a5" or "tent", hosted)`; the tent face prints on both sides of an A4 sheet scored in the middle. On the pull-up banner the eye level ticket sits 400 to 600mm from the top, and the URL band ends above the 300mm cassette line (the build asserts it).

Add a surface by adding an entry to `assets()` in `catalogue.py`: a name following `<brand>_<surface>_<variant>_<size>`, its group, the size, a `scale` if it is a platform size, a motif, the logo position and, if it has words, one headline with the highlighted word in `[[ ]]`. Placeholder words that are not a headline go in `copy` so the checker sees them. Finished files are not committed; copy them to the Brand Center folder under `_2026 Brand System/Exports/`.
