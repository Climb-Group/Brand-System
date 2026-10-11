# Logos

Master logos for ClimbUK, ClimbGroup and Climb27. Every file is a vector master (SVG) with PNG exports, and each
brand has the same set of variants.

## Colours

- **"Climb":** Climb Orange `#E8712A`.
- **UK, Group and 27:** Charcoal `#242322` on light backgrounds, white on dark backgrounds.
- **Mono dark version:** Charcoal.
- **Solid grounds:** White, Dark Brown `#1E0F05` (the brand ground) and Climb Orange.

## Transparent first

Every logo, icon and app icon is transparent by default, so it sits on any platform's own background. Each family
also comes on the three solid grounds, for places that need a filled shape (app stores, slide masters, platforms
that flatten transparency to black):

| Ground | Logo colours | File suffix |
|---|---|---|
| Transparent (the default) | As the variant: full colour, reversed, grey or mono | none |
| White | Climb Orange with Charcoal | `-on-white` |
| Dark Brown | Climb Orange with White | `-on-ground` |
| Climb Orange | One-colour white | `-on-orange` |

The solid wordmark and tagline files carry the full clear space (the height of the large C) on every edge, so they
can be dropped in as they are. Favicons, web app icons and app launcher tiles follow the same
rule; they are in the app icon kit, next to this folder.

## Which file to use

| File | Use it on |
|---|---|
| `<Brand>_reversed-dark.svg` | **The default.** Dark Brown (orange 6.06:1) and Charcoal (5.10:1) backgrounds, and dark photography |
| `<Brand>_full-colour-light.svg` | White backgrounds (orange 3.08:1) |
| `<Brand>_full-colour-grey.svg` | Light Grey `#E9E9E9` backgrounds. Uses the deeper orange `#D5641E` (3.05:1), because Climb Orange is too light on grey |
| `<Brand>_mono-dark.svg` | One-colour Charcoal on light backgrounds: single-colour print, embossing, partner listings |
| `<Brand>_mono-white.svg` | One-colour white on dark, orange or busy photo backgrounds |
| `<Brand>_icon.svg` | Stacked wordmark on a transparent square, for light backgrounds: social avatars and anything 64px or larger |
| `<Brand>_icon-reversed.svg` | The stacked wordmark on a transparent square, for dark backgrounds |
| `<Brand>_icon-monogram.svg` | The li monogram in Climb Orange on a transparent square: favicons, app icons and anything under 64px. Reads on light and dark backgrounds. The mark is the same for every brand |
| `<Brand>_tagline-lockup.svg` | Wordmark with "The Festival for Business Growth", for light backgrounds |
| `<Brand>_tagline-lockup-reversed.svg` | The same lockup for Dark Brown, Charcoal and dark photography |
| `<Brand>_logo-on-white.svg`, `-on-ground.svg`, `-on-orange.svg` | The wordmark on a solid White, Dark Brown or Climb Orange rectangle, clear space included |
| `<Brand>_tagline-lockup-on-white.svg`, `-on-ground.svg`, `-on-orange.svg` | The tagline lockup on a solid ground, clear space included |
| `<Brand>_icon-on-white.svg`, `-on-ground.svg`, `-on-orange.svg` | The stacked icon on a solid square. `-on-ground` is the Dark Brown tile |
| `<Brand>_icon-monogram-on-white.svg`, `-on-ground.svg`, `-on-orange.svg` | The li monogram on a solid square. `-on-ground` is the Dark Brown tile |
| `PNG/<Brand>_<variant>_{512,1024,2048}.png` | Raster exports, named by pixel width. Use the SVG wherever the software accepts it |
| `<Brand>_contact-sheet.png` | Every transparent variant on White, Light Grey, Dark Brown and Charcoal, with contrast results |

Each contact sheet marks every pairing as PASS or FAIL against the 3:1 contrast minimum for graphics (WCAG 2.2,
1.4.11). Never use a pairing marked FAIL.

## Clear space and minimum size

- **Clear space:** keep a clear margin around the whole logo, ® included, equal to the height of the large "C" in Climb.
  As a share of logo height that is about 1.0 for the ClimbUK and Climb27 wordmarks and 0.83 for ClimbGroup;
  for the tagline lockups it is 0.70 (ClimbUK), 0.715 (Climb27) and 0.58 (ClimbGroup).
  Nothing else (text, other logos, image edges) goes inside it.
- **Minimum sizes:**
  - Wordmarks: 120px wide on screen, 30mm in print.
  - Tagline lockups: 240px or 60mm, so the tagline stays readable.
  - Stacked icon: 64px.
  - Monogram: down to 16px.

## Don't

- Recolour, outline, stretch, rotate or redraw the logo, or set the wordmark in a font.
- Add shadows, glows, gradients or bevels to the logo itself. Effects belong to the layout around it.
- Put the full-colour logo on Light Grey or on orange. Use the grey version on grey, and mono white on orange.
- Put a transparent icon on a ground it was not made for: the light `icon` on dark, `icon-reversed` on light, or the
  orange monogram on Climb Orange. Use the `-on-orange` file there.
- Place the logo on a busy part of a photo. Put it on a calm area, or darken the photo behind it first.
- Lock the logo up with other marks or slogans, beyond the tagline lockups supplied here.
