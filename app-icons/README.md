# App icons

Favicons, web app icons and app launcher tiles for ClimbUK, ClimbGroup and Climb27. Every file is transparent by
default, so it sits on any platform's own background, and comes again on the three solid grounds.

| Folder | Background |
|---|---|
| `favicons/`, `app-tiles/` | Transparent (the default). The mark is Climb Orange, which reads on light and dark backgrounds |
| `favicons/white/`, `app-tiles/white/` | Solid White, orange mark |
| `favicons/ground/`, `app-tiles/ground/` | Solid Dark Brown `#1E0F05`, orange mark |
| `favicons/orange/`, `app-tiles/orange/` | Solid Climb Orange `#E8712A`, white mark |

## Favicons and web app icons

The li monogram, the same mark for every brand.

| File | Size | Use it for |
|---|---|---|
| `favicon.svg` | Scalable | Modern browsers. Use it first |
| `favicon.ico` | 16, 32 and 48 px in one file | Older browsers and anything that asks for `/favicon.ico` |
| `favicon-16x16.png`, `favicon-32x32.png`, `favicon-48x48.png` | 16, 32, 48 px | Drawn on whole pixels, so the gaps in the i stay sharp |
| `apple-touch-icon-180x180.png` | 180 px | Home screen icon on phones and tablets. Use a solid version here: a transparent one is shown on black |
| `icon-192.png`, `icon-512.png` | 192, 512 px | Web app manifest icons |
| `icon-maskable-512.png` | 512 px | Web app manifest icon the phone crops to its own shape. Solid grounds only, mark inside the middle 80 per cent |

A full example for a web page, transparent favicon with the Dark Brown home screen icon:

```html
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="16x16 32x32 48x48">
<link rel="apple-touch-icon" href="/ground/apple-touch-icon-180x180.png">
<link rel="manifest" href="/site.webmanifest">
```

And in `site.webmanifest`:

```json
{
  "icons": [
    {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
    {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"},
    {"src": "/ground/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}
  ],
  "theme_color": "#1E0F05",
  "background_color": "#1E0F05"
}
```

## App launcher tiles

Square tiles for an app launcher or intranet menu, at 60 px (the usual upload size), 120 px and 240 px. Each is one of
the house drawings in Climb Orange with Dark Brown cut lines; on Climb Orange the drawing is white.

| File | Drawing | For |
|---|---|---|
| `odoo_<size>.png` | Gears | The business system: contacts, events, tickets, website and accounts |
| `website_<size>.png` | Globe | The public website |
| `brand-centre_<size>.png` | Open book | Logos, colours, fonts, templates and the brand guidelines |
| `tickets_<size>.png` | Tickets | Event tickets and the box office |
| `media-kit_<size>.png` | Clapperboard | Photos, video, press and partner downloads |
| `climb_<size>.png` | The li monogram | A plain brand tile |

Most launchers ask for the image as a public link that opens without signing in. The brand centre on the website
serves every tile at a fixed address:

```text
https://www.climb-uk.com/brand/app-tiles/odoo_60x60.png            transparent (the default)
https://www.climb-uk.com/brand/app-tiles/white/odoo_60x60.png      on White
https://www.climb-uk.com/brand/app-tiles/ground/odoo_60x60.png     on Dark Brown
https://www.climb-uk.com/brand/app-tiles/orange/odoo_60x60.png     on Climb Orange
```

The favicons are served the same way under `/brand/favicons/`. `app-tiles_contact-sheet.png` shows every tile at
120 px: the transparent set on White and on Dark Brown, then the three solid sets.

## Rebuild

```bash
python3 logos/_build/build.py                 # the monogram master comes from the logos
python3 app-icons/_build/build_app_icons.py   # everything in this folder
```

Needs Python 3 with Pillow, and `rsvg-convert` (librsvg). The script reads the colours from
`tokens/brand.tokens.json`, the monogram from `logos/ClimbUK/ClimbUK_icon-monogram.svg` and the drawings from
`generators/illustrations.py`, and outlines the one drawing label (ADMIT ONE) from the Montserrat Bold file in
`logos/_build/`, so no font needs installing.

## Common problems

- **A transparent home screen icon shows on black.** Phones fill transparency with black. Use the file from
  `ground/`, `white/` or `orange/` for `apple-touch-icon` and maskable icons.
- **The tile looks blurred at 60 px.** Upload the 60 px file as it is; let the launcher scale the 120 px or 240 px
  files only when it asks for a larger size.
- **The orange mark disappears.** The transparent files are orange; on an orange background use `orange/`.
