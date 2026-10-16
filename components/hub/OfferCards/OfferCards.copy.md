---
copy: component-offer-cards
deliverable: The Offer cards component preview for the brand hub, live HTML, and its usage notes
build: components/build_components.py
source: mirror
files: preview.html README.md
---

# Offer cards

<!-- note: A mirror of the words in this component. The build takes the preview's words from the website blocks
and from components/build_components.py, and needs the website module, sass and Bootstrap to run, so the words
still live there; change them there and rebuild. Sections run in page order. -->

<!-- note: Kept verbatim, as printed, but these lines break the copy rules (reported for review, not fixed):
  readme.item 'soldout': scarcity claim
  readme.item 'last few': scarcity claim
  readme.item 'selling fast': scarcity claim
  section-1.eyebrow 'Sold out': scarcity claim
  section-1.text: not ASCII (U+00A3)
  section-1.text 'Sold out': scarcity claim
-->

## Card

<!-- @card.title -->
Offer cards

<!-- @card.group height=620 width=1280 -->
Tickets and stands

<!-- @card.subtitle -->
Ticket offers: the pick, the rest, and a closed release

## Usage notes

<!-- @readme.text -->
Offer cards sit side by side so people can compare. One is highlighted, the rest are equal.

<!-- @readme.item -->
`climb-offer-hl` is the offer to pick: orange edge, glow and a filled kicker, never raised, so its button stays on the row's line.

<!-- @readme.item -->
`is-soldout` dashes the edge, strikes the price and disables the button. Use it only when that release is truly closed.

<!-- @readme.item -->
`climb-was` shows the full price struck through; `climb-remaining` shows how many are left, only from live stock.

<!-- @readme.item -->
Prices always say inc VAT. No false scarcity: never write last few, hurry or selling fast.

## Preview

<!-- @section-1.eyebrow -->
Sold out

<!-- @section-1.heading -->
Super Early Bird

<!-- @section-1.text -->
£120 inc VAT

<!-- @section-1.text -->
The first release of standard two-day tickets. It went first.

<!-- @section-1.text -->
Sold out

<!-- @section-1.eyebrow -->
For you

<!-- @section-1.heading -->
Standard two-day

<!-- @section-1.text -->
£175 inc VAT

<!-- @section-1.text -->
Full price £480

<!-- @section-1.text -->
199 left at this price

<!-- @section-1.text -->
Both days, every session, the grand opening and the after parties.

<!-- @section-1.button -->
Get standard ticket

<!-- @section-1.heading -->
One-day

<!-- @section-1.text -->
£252 inc VAT

<!-- @section-1.text -->
One full day of sessions and meetings. Choose your day when you buy.

<!-- @section-1.button -->
Get one-day ticket

<!-- @section-1.heading -->
VIP

<!-- @section-1.text -->
£360 inc VAT

<!-- @section-1.text -->
Both days plus the VIP drinks reception and the ClimbAwards.

<!-- @section-1.button -->
Get VIP ticket
