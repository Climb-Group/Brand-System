---
copy: logos-shared
deliverable: The words every logo file and contact sheet shares: the tagline, the names of the logo versions and the contact sheet labels
build: logos/_build/build.py
source: mirror
---

# Logo words

<!-- note: A mirror of the words in logos/_build/build.py and sheet.py. The builds need tools this copy of the pack
could not run, so they still hold the words; change both until they read this file. -->

<!-- @tagline -->
The Festival for Business Growth

## Version names

<!-- note: Used in each SVG title as '<Brand> logo, <name>', '<Brand> logo with tagline, <name>' for the lockups,
and 'Climb li monogram' for the monogram files. The transparent ones head the contact sheet columns. -->

<!-- @version key=full-colour-light -->
Full colour (light)

<!-- @version key=reversed-dark -->
Reversed (dark-first)

<!-- @version key=mono-dark -->
Mono dark

<!-- @version key=mono-white -->
Mono white

<!-- @version key=icon -->
Square icon

<!-- @version key=icon-reversed -->
Square icon reversed

<!-- @version key=full-colour-grey -->
Full colour (Light Grey)

<!-- @version key=icon-monogram -->
Monogram icon (under 64px)

<!-- @version key=tagline-lockup -->
Tagline lockup

<!-- @version key=tagline-lockup-reversed -->
Tagline lockup reversed

<!-- @version key=logo-on-white -->
Logo on White

<!-- @version key=logo-on-ground -->
Logo on Dark Brown

<!-- @version key=logo-on-orange -->
Logo on Climb Orange

<!-- @version key=tagline-lockup-on-white -->
Tagline lockup on White

<!-- @version key=tagline-lockup-on-ground -->
Tagline lockup on Dark Brown

<!-- @version key=tagline-lockup-on-orange -->
Tagline lockup on Climb Orange

<!-- @version key=icon-on-white -->
Square icon on White

<!-- @version key=icon-on-ground -->
Square icon on Dark Brown

<!-- @version key=icon-on-orange -->
Square icon on Climb Orange

<!-- @version key=icon-monogram-on-white -->
Monogram on White

<!-- @version key=icon-monogram-on-ground -->
Monogram on Dark Brown

<!-- @version key=icon-monogram-on-orange -->
Monogram on Climb Orange

<!-- @title.wordmark -->
{brand} logo, {version}

<!-- @title.tagline -->
{brand} logo with tagline, {version}

<!-- @title.monogram -->
Climb li monogram

## Contact sheet

<!-- @sheet.title -->
{brand} - 2026 master logos

<!-- @sheet.row -->
White

<!-- @sheet.row -->
Light Grey

<!-- @sheet.row -->
Dark Brown

<!-- @sheet.row -->
Charcoal

<!-- note: Each cell's note is worked out from the colours: 'min contrast <ratio>:1 - PASS' at 3:1 or more, else FAIL. -->

<!-- @sheet.cell version=full-colour-light ground="White" -->
min contrast 3.08:1 - PASS

<!-- @sheet.cell version=full-colour-light ground="Light Grey" -->
min contrast 2.53:1 - FAIL

<!-- @sheet.cell version=full-colour-light ground="Dark Brown" -->
min contrast 1.19:1 - FAIL

<!-- @sheet.cell version=full-colour-light ground="Charcoal" -->
min contrast 1.00:1 - FAIL

<!-- @sheet.cell version=reversed-dark ground="White" -->
min contrast 1.00:1 - FAIL

<!-- @sheet.cell version=reversed-dark ground="Light Grey" -->
min contrast 1.21:1 - FAIL

<!-- @sheet.cell version=reversed-dark ground="Dark Brown" -->
min contrast 6.06:1 - PASS

<!-- @sheet.cell version=reversed-dark ground="Charcoal" -->
min contrast 5.10:1 - PASS

<!-- @sheet.cell version=mono-dark ground="White" -->
min contrast 15.69:1 - PASS

<!-- @sheet.cell version=mono-dark ground="Light Grey" -->
min contrast 12.92:1 - PASS

<!-- @sheet.cell version=mono-dark ground="Dark Brown" -->
min contrast 1.19:1 - FAIL

<!-- @sheet.cell version=mono-dark ground="Charcoal" -->
min contrast 1.00:1 - FAIL

<!-- @sheet.cell version=mono-white ground="White" -->
min contrast 1.00:1 - FAIL

<!-- @sheet.cell version=mono-white ground="Light Grey" -->
min contrast 1.21:1 - FAIL

<!-- @sheet.cell version=mono-white ground="Dark Brown" -->
min contrast 18.65:1 - PASS

<!-- @sheet.cell version=mono-white ground="Charcoal" -->
min contrast 15.69:1 - PASS

<!-- @sheet.cell version=icon ground="White" -->
min contrast 3.08:1 - PASS

<!-- @sheet.cell version=icon ground="Light Grey" -->
min contrast 2.53:1 - FAIL

<!-- @sheet.cell version=icon ground="Dark Brown" -->
min contrast 1.19:1 - FAIL

<!-- @sheet.cell version=icon ground="Charcoal" -->
min contrast 1.00:1 - FAIL

<!-- @sheet.cell version=icon-reversed ground="White" -->
min contrast 1.00:1 - FAIL

<!-- @sheet.cell version=icon-reversed ground="Light Grey" -->
min contrast 1.21:1 - FAIL

<!-- @sheet.cell version=icon-reversed ground="Dark Brown" -->
min contrast 6.06:1 - PASS

<!-- @sheet.cell version=icon-reversed ground="Charcoal" -->
min contrast 5.10:1 - PASS

<!-- @sheet.cell version=full-colour-grey ground="White" -->
min contrast 3.70:1 - PASS

<!-- @sheet.cell version=full-colour-grey ground="Light Grey" -->
min contrast 3.05:1 - PASS

<!-- @sheet.cell version=full-colour-grey ground="Dark Brown" -->
min contrast 1.19:1 - FAIL

<!-- @sheet.cell version=full-colour-grey ground="Charcoal" -->
min contrast 1.00:1 - FAIL

<!-- @sheet.cell version=icon-monogram ground="White" -->
min contrast 3.08:1 - PASS

<!-- @sheet.cell version=icon-monogram ground="Light Grey" -->
min contrast 2.53:1 - FAIL

<!-- @sheet.cell version=icon-monogram ground="Dark Brown" -->
min contrast 6.06:1 - PASS

<!-- @sheet.cell version=icon-monogram ground="Charcoal" -->
min contrast 5.10:1 - PASS

<!-- @sheet.cell version=tagline-lockup ground="White" -->
min contrast 3.08:1 - PASS

<!-- @sheet.cell version=tagline-lockup ground="Light Grey" -->
min contrast 2.53:1 - FAIL

<!-- @sheet.cell version=tagline-lockup ground="Dark Brown" -->
min contrast 1.19:1 - FAIL

<!-- @sheet.cell version=tagline-lockup ground="Charcoal" -->
min contrast 1.00:1 - FAIL

<!-- @sheet.cell version=tagline-lockup-reversed ground="White" -->
min contrast 1.00:1 - FAIL

<!-- @sheet.cell version=tagline-lockup-reversed ground="Light Grey" -->
min contrast 1.21:1 - FAIL

<!-- @sheet.cell version=tagline-lockup-reversed ground="Dark Brown" -->
min contrast 6.06:1 - PASS

<!-- @sheet.cell version=tagline-lockup-reversed ground="Charcoal" -->
min contrast 5.10:1 - PASS

<!-- @sheet.footnote -->
Orange #E8712A (was #EC752A); on-grey orange #D5641E; wordmark dark #242322; solid grounds #FFFFFF, #1E0F05, #E8712A. WCAG 1.4.11 graphic threshold 3:1. FAIL cells show where a variant must not be used.
