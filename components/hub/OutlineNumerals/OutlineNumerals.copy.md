---
copy: component-outline-numerals
deliverable: The Outline numerals component preview for the brand hub, live HTML, and its usage notes
build: components/build_components.py
source: mirror
files: preview.html README.md
---

# Outline numerals

<!-- note: A mirror of the words in this component. The build takes the preview's words from the website blocks
and from components/build_components.py, and needs the website module, sass and Bootstrap to run, so the words
still live there; change them there and rebuild. Sections run in page order. -->

## Card

<!-- @card.title -->
Outline numerals

<!-- @card.group height=1480 width=1280 -->
Festival devices

<!-- @card.subtitle -->
Giant outlined numbers for section numbers and big stats

## Usage notes

<!-- @readme.text -->
Outline numerals are giant numbers drawn as an orange outline with no fill. They number chapters and sections and carry the odd big stat, like a festival poster.

<!-- @readme.item -->
`climb-outline-num`: Montserrat ExtraBold (800), upright, tabular figures, letter spacing -0.04em, line height 0.8, no fill and a Climb Orange stroke of about 1% of the size (4px at 380px). `climb-outline-num-sm` is the stat size with a 2px stroke. Never go below a 2px stroke.

<!-- @readme.item -->
Best on a dark ground or over a photo on a Dark Brown fade. On White or Light Grey the stroke turns to the darker text orange; on Climb Orange it turns White.

<!-- @readme.item -->
Section numbers are two digits (01 to 10) and decorative: mark them `aria-hidden` and put the real heading in text beside them (`climb-numbered` lines them up).

<!-- @readme.item -->
A stat number stays readable text with its label underneath in words. With `data-climb-size="aaa"` the stat fills solid.

<!-- @readme.item -->
Use one size of outline numeral per view. Never outline words or headlines with it; the only outlined words are the quiet marquee.

<!-- @readme.item -->
`climb-outline-marquee`: a giant italic uppercase line in Orange Tint at 35% with a 2px stroke, running off the edge behind a section. Decorative only, so `aria-hidden`, and never the only place the words appear.

<!-- @readme.item -->
In design apps: same font, weight and tracking, fill none, stroke Climb Orange centred at about 1% of the point size.

## Preview

<!-- @section-1.text -->
05

<!-- @section-1.eyebrow -->
Chapter five

<!-- @section-1.heading -->
*Real* [[photos]]

<!-- @section-2.text -->
01

<!-- @section-2.heading -->
Find your [[people]]

<!-- @section-2.text -->
02

<!-- @section-2.heading -->
Grow your *business*

<!-- @section-3.text -->
2

<!-- @section-3.text -->
Days of business growth

<!-- @section-3.text -->
27

<!-- @section-3.text -->
The next edition

<!-- @section-4.text -->
Find your people / Grow your business / Find your people
