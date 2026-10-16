---
copy: component-button
deliverable: The Button component preview for the brand hub, live HTML, and its usage notes
build: components/build_components.py
source: mirror
files: preview.html README.md
---

# Button

<!-- note: A mirror of the words in this component. The build takes the preview's words from the website blocks
and from components/build_components.py, and needs the website module, sass and Bootstrap to run, so the words
still live there; change them there and rebuild. Sections run in page order. -->

<!-- note: Kept verbatim, as printed, but these lines break the copy rules (reported for review, not fixed):
  readme.item 'Sold out': scarcity claim
  section-1.text 'Sold out': scarcity claim
  section-2.text 'Sold out': scarcity claim
  section-3.text 'Sold out': scarcity claim
  section-4.text 'Sold out': scarcity claim
-->

## Card

<!-- @card.title -->
Button

<!-- @card.group height=560 width=1280 -->
Actions

<!-- @card.subtitle -->
Pill buttons with a spring hover, one primary per view, and the pull link

## Usage notes

<!-- @readme.text -->
Buttons are pills in Montserrat Bold with an action verb: Get your ticket, Book a call, Apply to speak.

<!-- @readme.item -->
One `btn btn-primary` per view. A second action is `btn btn-outline-secondary`.

<!-- @readme.item -->
`btn-lg` in heroes and closes, the default size elsewhere.

<!-- @readme.item -->
A closed offer shows a disabled outline button that says Sold out, only when it is true.

<!-- @readme.item -->
The pull link (`climb-pull`) is the soft third action under the buttons: a question that routes people.

<!-- @readme.item -->
On Climb Orange (preset 4) the primary button turns White with Charcoal text.

<!-- @readme.item -->
Hover lifts with the spring easing; focus shows a 3px orange outline. Both stop under reduced motion.

## Preview

<!-- @section-1.button -->
Get your ticket

<!-- @section-1.button -->
Partner with ClimbUK

<!-- @section-1.button -->
Book a call

<!-- @section-1.text -->
Sold out

<!-- @section-1.text -->
Not sure which Climb27 is yours? Pick your route

<!-- @section-2.button -->
Get your ticket

<!-- @section-2.button -->
Partner with ClimbUK

<!-- @section-2.button -->
Book a call

<!-- @section-2.text -->
Sold out

<!-- @section-2.text -->
Not sure which Climb27 is yours? Pick your route

<!-- @section-3.button -->
Get your ticket

<!-- @section-3.button -->
Partner with ClimbUK

<!-- @section-3.button -->
Book a call

<!-- @section-3.text -->
Sold out

<!-- @section-3.text -->
Not sure which Climb27 is yours? Pick your route

<!-- @section-4.button -->
Get your ticket

<!-- @section-4.button -->
Partner with ClimbUK

<!-- @section-4.button -->
Book a call

<!-- @section-4.text -->
Sold out

<!-- @section-4.text -->
Not sure which Climb27 is yours? Pick your route
