# Climb27 flyers

A5 flyers for Climb27 (30 June and 1 July 2027), printed on both sides, ready to send to a printer.

| File | Who it is for |
| --- | --- |
| `segments/climb27_flyer_<audience>_a5.pdf` | One flyer per audience: scaling companies, professional services, founders raising investment, universities, investors, the public sector, advisers and consultants, incubators and accelerators. Each has its own headline, five reasons, photos and a QR code to that audience's page on climb-uk.com. |
| `segments/climb27_flyer_what-is-climbuk_a5.pdf` | People who are new to ClimbUK: what it is, who comes and where they fit. |
| `general/climb27_flyer_general-<n>_<theme>_a5.pdf` | Four more flyers for people who are new to ClimbUK, one per brand theme: Find your people, Main stage moments, Your business. Bigger stage, and Business with a party. Their QR codes go to the climb-uk.com homepage, where the reader picks who they are. |

Contact sheets of every front and back are in `previews/`.

## Print specification

- A5, 148 x 210 mm trimmed, with 3 mm bleed on every edge. TrimBox and BleedBox are set.
- Fonts are embedded. Text, logos and QR codes are vectors.
- Photos are 300 ppi at their printed size.
- Colours are sRGB from the brand tokens. Ask the printer to convert to CMYK and to send a proof. Climb Orange is Pantone 158 C (CMYK 0 65 90 0).

## Rebuild

```bash
python3 pdf/flyers/_build/segments.py
python3 pdf/flyers/_build/variants.py
```

Add `--only <audience>` to `segments.py` to rebuild one flyer. Both scripts need Python 3 with Pillow, numpy, segno and pypdf, and Node with Playwright (Chromium) on `NODE_PATH`. They read the fonts, logos, illustrations and photos from this pack, write one HTML page per side, print it to PDF and set the print boxes.

- The copy for each audience is in `SEGMENTS` in `segments.py`, and the copy for the general flyers is in `VARIANTS` in `variants.py`. Each run writes the copy to a text file; run the climb-voice checker over it.
- `build.py` holds the shared helpers: photo cropping and fades, logos, QR codes and the print boxes. It also builds the A5 event flyer, the roller banner and the business card.

## What they follow

- Tokens: the colours and type in `tokens/brand.tokens.json` (Dark Brown, Charcoal, Climb Orange, Tint, Light Grey; Montserrat and Open Sans).
- Skills: climb-visual-style for the layout, headlines, icons and motifs, and climb-voice for the copy.
- Every headline opens on a positive line, with one orange word and one italic word.
- The icons are the house illustrations, and each flyer uses one motif family.
- Logos and text never sit over a face.
