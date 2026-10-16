---
copy: component-headline
deliverable: The Headline component preview for the brand hub, live HTML, and its usage notes
build: components/build_components.py
source: mirror
files: preview.html README.md
---

# Headline

<!-- note: A mirror of the words in this component. The build takes the preview's words from the website blocks
and from components/build_components.py, and needs the website module, sass and Bootstrap to run, so the words
still live there; change them there and rebuild. Sections run in page order. -->

## Card

<!-- @card.title -->
Headline

<!-- @card.group height=520 width=1280 -->
Foundations

<!-- @card.subtitle -->
Uppercase display lines with one orange word and one italic word

## Usage notes

<!-- @readme.text -->
Headlines are the poster voice: uppercase, tight, and short enough to read in one look.

<!-- @readme.item -->
`climb-display` for the one hero line on a page; `climb-statement` for section lines; add `climb-statement-sm` for a smaller one beside a photo.

<!-- @readme.item -->
Give one word `climb-accent` (orange) and one word `<em>` (italic). Never more than one of each.

<!-- @readme.item -->
`climb-ruled` adds the short orange rule above the line.

<!-- @readme.item -->
`climb-eyebrow` sits above a headline: edition, date or audience.

<!-- @readme.item -->
`climb-lead` is the promise line under it, at most 36 words.

## Preview

<!-- @section-1.eyebrow -->
Climb27 / The Festival for Business Growth

<!-- @section-1.headline -->
Your business. Bigger [[*stage*]].

<!-- @section-1.heading -->
Not a *conference*. A [[festival]] for business growth.

<!-- @section-1.heading -->
ClimbAwards: be the name behind the *moment*

<!-- @section-1.text -->
Lead text: one or two sentences that say what happens, for whom, and what to do next.
