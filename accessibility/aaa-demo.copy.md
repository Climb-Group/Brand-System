---
copy: accessibility-aaa-demo
deliverable: The AAA demo page, the website today next to the WCAG 2.2 AAA version for items E9 and E12
source: mirror
files: aaa-demo.html
---

# AAA demos

<!-- note: The page is written by hand, so this file mirrors its words: change both. The middle dots in the
eyebrows and specs print as a middle dot; here they are written as a hyphen-minus. -->

<!-- @page.title -->
ClimbUK AAA Demos

## Header

<!-- @header.eyebrow -->
WCAG 2.2 AAA, items E9 and E12

<!-- @header.headline -->
Two changes to *see* before you decide

<!-- @header.intro -->
Each demo shows the website today next to the AAA version. Switch the ground to check both light and dark sections.

## E9

<!-- @e9.eyebrow -->
E9 - 1.4.8 Visual presentation

<!-- @e9.heading -->
Line spacing and *line length*

<!-- @e9.lead -->
AAA asks for body text with line spacing of at least 1.5, paragraph gaps at least 1.5 times that, lines under 80
characters, no justified text and no tiny print. Headlines are exempt and keep their tight poster look.

<!-- @e9.controls.label -->
Section ground

<!-- @e9.control -->
Dark ground

<!-- @e9.control -->
Light ground

<!-- @e9.panel.tag panel=today -->
Today

<!-- @e9.panel.specs panel=today -->
16px - line 1.35 - gap 0.75em - full width - 11px small print

<!-- @e9.panel.tag panel=aaa -->
AAA

<!-- @e9.panel.specs panel=aaa -->
18px - line 1.6 - gap 1.6em - 66 characters max - 15px small print

<!-- note: The sample below prints in both panels. -->

<!-- @e9.sample.eyebrow -->
For partners

<!-- @e9.sample.heading -->
Meet the right people

<!-- @e9.sample.text -->
Climb27 brings growing businesses, investors and the people who back them into one place for two days. Partners get
delegate passes, a stage moment and a stand where the conversations happen.

<!-- @e9.sample.text -->
Book meetings before you arrive through the event app, then spend the day in rooms built for business.

<!-- @e9.sample.link -->
See partner packages

<!-- @e9.sample.small-print -->
Packages are limited and allocated in order of booking.

<!-- @e9.legend -->
The AAA block ships as the **climb-aaa** section class and the **aaa-type-*** tokens, so it can be switched on per
section rather than everywhere.

## E12

<!-- @e12.eyebrow -->
E12 - 2.4.12 Focus not obscured

<!-- @e12.heading -->
Nothing hides under the *sticky* header

<!-- @e12.lead -->
When someone tabs to a link or follows a jump link, the browser scrolls it to the very top of the window, which is
right where the sticky header sits. The fix tells the browser to stop that far below the top. It changes nothing for
mouse users scrolling normally.

<!-- @e12.controls.label -->
Header offset

<!-- @e12.control -->
Today

<!-- @e12.control -->
With the fix

<!-- @e12.control -->
Jump to tickets

<!-- @e12.control -->
Tab to the next link

<!-- @e12.control -->
Back to top

<!-- @e12.result state=hidden -->
Hidden: the header covers it.

<!-- @e12.result state=visible -->
Visible: it sits below the header.

<!-- @e12.example.label -->
Example page with a sticky header

<!-- @e12.example.brand -->
ClimbUK

<!-- @e12.example.header -->
Sticky header

<!-- @e12.example.block -->
### Main stage moments
Two days of talks from founders who have done it.

<!-- @e12.example.link -->
See the lineup

<!-- @e12.example.block -->
### Find your people
Partner meetings, roundtables and the after party.

<!-- @e12.example.link -->
Book meetings

<!-- @e12.example.block -->
### Tickets
Early bird prices rise with every release.

<!-- @e12.example.link -->
Get your ticket

<!-- @e12.example.block -->
### Exhibit
Stands sell in order of booking.

<!-- @e12.example.link -->
See the stands

<!-- @e12.example.block -->
### Partner
Meetings with the right people.

<!-- @e12.example.link -->
Partner with ClimbUK

<!-- @e12.legend -->
In the website this is one line, **scroll-padding-top** set to the header height, already added to the brand
stylesheet.

## Footer

<!-- @footer -->
Reply in the thread with E9 yes or no. E12 is in place, and this demo shows what it changes.
