# PDFs

Shareable PDFs for each brand (ClimbUK, ClimbGroup, Climb27), built from `guidelines/`, `tokens/`, `logos/`, `photos/` and `illustrations/`.

| File | What it is | Size |
| --- | --- | --- |
| `one-page/<brand>_key-rules.pdf` | The key rules everyone must follow: logo, colour, type, voice, photography, accessibility and naming | A4, one page |
| `guidelines/<brand>_brand-guidelines.pdf` | The full brand book: ten sections, from the big idea to print, video, partners and accessibility | 16:9 slides, 1920x1080 |
| `flyers/` | Climb27 flyers: one per audience, plus five for people who are new to ClimbUK. See `flyers/README.md` | A5, both sides, 3 mm bleed |

The ClimbGroup editions use Charcoal grounds and the slab and peak marks, with pages on contracts, documents, decks and email signatures. The Climb27 editions add the themes, the edition mark, ticket pages and the share kit.

## Rebuild

```bash
pdf/_build/build.sh
```

Needs Python 3 and Node with Playwright (Chromium). The script copies the fonts, logos, photos and illustrations from this pack, writes one HTML file per PDF, prints them to PDF and moves them into `one-page/` and `guidelines/`.

- Copy lives in `pdf/_build/brands.py` (per brand) and `book.py` / `keyrules.py` (shared pages). It follows the climb-voice skill; run its checker on any new line.
- Outline numerals and marquees use `pdf/_build/fonts/montserrat-800-outline*.woff2`: Montserrat ExtraBold with its overlapping contours merged, so the stroke draws no stray lines inside the letters. `python3 pdf/_build/outline_font.py` remakes them (needs fontTools, skia-pathops and brotli).
- The renderer bakes CSS gradients into images before printing, because several PDF viewers cannot draw the gradient shadings Chromium writes.
- Before printing, `contrast.cjs` and `contrast.py` measure every run of text against what sits behind it (photos, fades, stickers) and stop the build if any is under WCAG 2.2 AA: 4.5:1, or 3:1 for text of 24px, or 18.66px bold. Faint decorative texture, such as marquee rows, is marked `aria-hidden` and skipped.
- The build sizes photos to 2200px on the long edge before printing. Pages are 1920px wide, so this keeps them sharp and keeps each book under 20 MB.
- Colours and sizes come from the tokens. If a token changes (for example the orange), rebuild.
- The PDFs are public: no repository paths, internal notes or vendor tool names.
