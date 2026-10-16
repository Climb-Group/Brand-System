---
copy: component-ticket-ladder-section
deliverable: The Ticket ladder section component preview for the brand hub, live HTML, and its usage notes
build: components/build_components.py
source: mirror
files: preview.html README.md
---

# Ticket ladder section

<!-- note: A mirror of the words in this component. The build takes the preview's words from the website blocks
and from components/build_components.py, and needs the website module, sass and Bootstrap to run, so the words
still live there; change them there and rebuild. Sections run in page order. -->

<!-- note: Kept verbatim, as printed, but these lines break the copy rules (reported for review, not fixed):
  section-1.item 'About 5% of tickets': do not quote a release's share of tickets: name its state
  section-1.item: not ASCII (U+00A3)
  section-1.item 'About 10% of tickets': do not quote a release's share of tickets: name its state
  section-1.item 'About 15% of tickets': do not quote a release's share of tickets: name its state
  section-1.item 'About 20% of tickets': do not quote a release's share of tickets: name its state
  section-1.item 'About 25% of tickets': do not quote a release's share of tickets: name its state
-->

## Card

<!-- @card.title -->
Ticket ladder section

<!-- @card.group height=520 width=1280 -->
Sections

<!-- @card.subtitle -->
The release ladder on its own

## Usage notes

<!-- @readme.text -->
The release ladder as its own section, for a pricing page or under a hero.

## Preview

<!-- @section-1.heading -->
How the standard ticket price steps up

<!-- @section-1.eyebrow -->
Release pricing

<!-- @section-1.text -->
Each release closes when its tickets go, and the price steps up. Buy in the release that is open now.

<!-- @section-1.item -->
Super Early Bird £120 About 5% of tickets Closed

<!-- @section-1.item -->
199 left at this price Early Adopter £175 About 10% of tickets Open now

<!-- @section-1.item -->
First Release £239 About 15% of tickets Next

<!-- @section-1.item -->
Second Release £300 About 20% of tickets Next

<!-- @section-1.item -->
Penultimate Release £360 About 25% of tickets Next

<!-- @section-1.item -->
Full price £480 Everything else Final
