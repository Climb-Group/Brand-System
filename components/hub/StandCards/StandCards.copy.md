---
copy: component-stand-cards
deliverable: The Stand cards component preview for the brand hub, live HTML, and its usage notes
build: components/build_components.py
source: mirror
files: preview.html README.md
---

# Stand cards

<!-- note: A mirror of the words in this component. The build takes the preview's words from the website blocks
and from components/build_components.py, and needs the website module, sass and Bootstrap to run, so the words
still live there; change them there and rebuild. Sections run in page order. -->

<!-- note: Kept verbatim, as printed, but these lines break the copy rules (reported for review, not fixed):
  readme.item 'soldout': scarcity claim
  section-1.text: not ASCII (U+00B2)
  section-1.text: not ASCII (U+00A3)
-->

## Card

<!-- @card.title -->
Stand cards

<!-- @card.group height=600 width=1280 -->
Tickets and stands

<!-- @card.subtitle -->
Exhibition stands with an outlined floor plan and stock

## Usage notes

<!-- @readme.text -->
Stand cards show the exhibition space. The outlined plan (`climb-plan-1`, `-2`, `-4`) shows the footprint at a glance.

<!-- @readme.item -->
`climb-left` shows stock left, from live stock only. A sold-out stand uses `is-soldout`.

<!-- @readme.item -->
Name, size, what is included, price inc VAT, one button.

## Preview

<!-- @section-1.text -->
59 left

<!-- @section-1.heading -->
Sales Space

<!-- @section-1.text -->
2m x 2m, 4 m²

<!-- @section-1.text -->
£4,000 inc VAT

<!-- @section-1.text -->
Big enough to make noise. Room to pitch, demo and deal.

<!-- @section-1.button -->
Book this stand: Sales Space

<!-- @section-1.text -->
9 left

<!-- @section-1.heading -->
Starter Pod

<!-- @section-1.text -->
Pod

<!-- @section-1.text -->
£1,000 inc VAT

<!-- @section-1.text -->
The smallest footprint on the floor: a pod to meet from, with the same reach.

<!-- @section-1.button -->
Book this stand: Starter Pod

<!-- @section-1.text -->
2 left

<!-- @section-1.heading -->
Display Space

<!-- @section-1.text -->
Display

<!-- @section-1.text -->
£2,000 inc VAT

<!-- @section-1.text -->
A display footprint for a product that speaks for itself.

<!-- @section-1.button -->
Book this stand: Display Space
