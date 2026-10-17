---
copy: template-sharepoint-book-components
deliverable: SharePoint brand book page: Components | ClimbUK brand centre
files: ../brand-book/components.html
source: mirror
---

# Components | ClimbUK brand centre

<!-- note: A mirror. This is the SharePoint copy of the brand book, made by the brand centre's own build, the same one that makes the brand centre pages on the website, so its words live there: change them there and rebuild the pack. Each section is the text under one heading on the page, in page order, as it prints. The menu, header and footer are the same on every page and are in index.copy.md. -->

<!-- note: Copy rules this mirror breaks, as the checker reports them (line numbers before this note was added). Many are the voice guide's own examples of what not to write; fix the rest where the words live: line 155 'Sold out' (scarcity claim); line 227 'soldout' (scarcity claim); line 239 'last few' (scarcity claim); line 239 'selling fast' (scarcity claim); line 291 'soldout' (scarcity claim); line 307 'biggest' (unsupported superlative or size claim); line 359 'Climb' ('Climb' on its own). -->

<!-- @top -->
Components | ClimbUK brand centre

Skip to the content

Find a component

<!-- @use-them-anywhere -->
### Use them anywhere
Load the token CSS, the component stylesheet and script from the Tokens downloads. Call

ClimbUK.mount()

once; every block marked

data-climb-theme

then follows the page theme. Or copy any block's HTML into your page builder as it is.

Tokens downloads

No component matches that search.

<!-- @foundations -->
### Foundations
The five presets are the only grounds a ClimbUK section uses. Each one sets the heading, body, link, accent and button colours together, so a section never mixes them by hand.

How to use it

Preset

Ground

Use

1

White

Reading-heavy pages, forms, the release ladder

2

Light Grey

A quiet change of pace between dark sections

3

Dark Brown

The default ground

4

Climb Orange

Calls to action and the close, large white text only

5

Charcoal

Tickets and audience sections

Add the class

climb-p1

to

climb-p5

to a section. In this hub, sections on presets 1, 2, 3 and 5 follow the theme toggle; preset 4 and photo sections stay as they are in both themes.

Headlines are the poster voice: uppercase, tight, and short enough to read in one look.

How to use it

climb-display

for the one hero line on a page;

climb-statement

for section lines; add

climb-statement-sm

for a smaller one beside a photo.

Give one word

climb-accent

(orange) and one word

<em>

(italic). Never more than one of each.

climb-ruled

adds the short orange rule above the line.

climb-eyebrow

sits above a headline: edition, date or audience.

climb-lead

is the promise line under it, at most 36 words.

The eyebrow is the small uppercase line above a headline: the edition, the date or the audience. Keep it under six words. Use

climb-ruled

on the headline for the short orange rule.

Elevation is soft and warm: shadows are Dark Brown, never black, and the pick glows orange. Use the shadow tokens, not your own values.

Motion is punchy and short: things rise into place, buttons spring, live labels pulse, logos drift. Use the duration and easing tokens. Everything stops or becomes a simple fade under reduced motion.

<!-- @actions -->
### Actions
Buttons are pills in Montserrat Bold with an action verb: Get your ticket, Book a call, Apply to speak.

How to use it

One

btn btn-primary

per view. A second action is

btn btn-outline-secondary

.

btn-lg

in heroes and closes, the default size elsewhere.

A closed offer shows a disabled outline button that says Sold out, only when it is true.

The pull link (

climb-pull

) is the soft third action under the buttons: a question that routes people.

On Climb Orange (preset 4) the primary button turns White with Charcoal text.

Hover lifts with the spring easing; focus shows a 3px orange outline. Both stop under reduced motion.

<!-- @festival-devices -->
### Festival devices
Stickers are the festival's stamps: one or two words, tilted, pinned to the corner of a photo or a ticket.

How to use it

climb-sticker

is Climb Orange with Dark Brown text;

climb-sticker-dark

is Dark Brown with orange text.

climb-sticker-pin

pins it to the top corner of its card.

One sticker per card. Words only, never a sentence.

Tags name formats and topics. They are outlined, never filled, so they do not compete with buttons.

How to use it

The live label (

climb-live

) adds a pulsing orange dot. Use it only for something that is happening now: tickets on sale, a live stream, doors open. The pulse stops under reduced motion.

<!-- @tickets-and-stands -->
### Tickets and stands
The ticket card is the thing people pick up: a glass card with stub notches, a sticker and one button.

How to use it

climb-ticket

on dark grounds; add

climb-ticket-hl

for the one ticket to pick (orange edge and glow).

On Climb Orange it turns Dark Brown.

Kicker, name, three short benefits, one button. Prices go on offer cards.

climb-levels

lists packages with a note on the right (passes, sizes).

Offer cards sit side by side so people can compare. One is highlighted, the rest are equal.

How to use it

climb-offer-hl

is the offer to pick: orange edge, glow and a filled kicker, never raised, so its button stays on the row's line.

is-soldout

dashes the edge, strikes the price and disables the button. Use it only when that release is truly closed.

climb-was

shows the full price struck through;

climb-remaining

shows how many are left, only from live stock.

Prices always say inc VAT. No false scarcity: never write last few, hurry or selling fast.

The release ladder shows that the price rises with every release, and where today sits on it.

How to use it

Each

climb-ladder-step

sets

--climb-step

(1, 2, 3 ...) so its cap rises.

is-past

greys the cap and strikes the price;

is-current

fills it orange with a glow and the left pill;

is-next

dashes it.

States are written in words as well as shown (Closed, On sale now, Next), never colour alone.

On phones the ladder turns into a vertical rail.

Stand cards show the exhibition space. The outlined plan (

climb-plan-1

,

-2

,

-4

) shows the footprint at a glance.

How to use it

climb-left

shows stock left, from live stock only. A sold-out stand uses

is-soldout

.

Name, size, what is included, price inc VAT, one button.

The group offer is one orange band under the ticket offers: bring the team, one line, one Dark Brown button.

<!-- @cards -->
### Cards
Moment cards show what happens: a real Climb26 photo, a short name, one sentence. Three in a row. Photos lift slightly on hover.

Audience cards let each audience pick themselves. The whole card is the link. Four in a row on desktop, two on tablets, one on phones. The line under the name is the audience's own reason to come.

Quotes come only from named, real people who agreed to them, with their role and company. Never invent a quote, a name or a company.

The lineup sets names like a festival poster: the biggest names first, three sizes, separated by orange slashes. Only names that are confirmed or that appeared at a past edition, labelled as such.

<!-- @sections -->
### Sections
A photo fade puts a real photo behind the words and fades it to a brand colour on the side the words sit.

How to use it

Brown: Dark Brown from the left and to a solid foot, so cards can sit on it. The Business with a party section.

Heat: Dark Brown on the left, warming to orange light on the right. For the evening and the after parties.

Orange: Climb Orange washing over the photo. Never over faces; use objects, stages and crowds from behind.

Words sit where the fade is 85% or more. End on solid colour. Flip the fade (270deg) to put words on the right.

Photo fades stay dark (or orange) in both themes.

The hero opens a page: a full-bleed Climb26 stage photo faded from the left, an eyebrow, one display line, a lead, two buttons and the pull link.

The hero with a ticket adds the glass ticket card on the right, for pages built around one ticket.

Moments sells the feeling: one statement with an italic word, a lead, three moment cards and two buttons.

The photo wall shows the last edition: one big tile with a sticker, a wall of squares and two quotes from people who were there.

The ticket band is the partner pitch on Climb Orange: one big line, a lead, one button and a Dark Brown ticket listing the packages.

The tickets section is the order on a ticket page: the offers, the release ladder, the group offer and a pull link for anyone still choosing.

The release ladder as its own section, for a pricing page or under a hero.

The stands section sells exhibition space with outlined plans and live stock.

The speaker lineup invites people to apply, with format tags and the poster lineup of previous speakers.

The logo marquee shows partners, exhibitors and attendees as two rows drifting in opposite directions with faded edges. It pauses on hover and stops under reduced motion. Logos sit in a neutral tone and go to colour on hover.

The audience chooser asks what brings you to ClimbUK and routes each audience to its own page.

Moment is one photo, one sticker, one line and one button. Use it to put one thing in the spotlight, like the ClimbAwards.

The close ends every ticket page on Climb Orange: the last question, the dates and one clear next step in Dark Brown.

The divider is a low band of rising chevrons between two sections. Match its preset to the section above.

<!-- @brand -->
### Brand
Use the reversed logo on Dark Brown, Charcoal and photos; the full-colour logo on White and Light Grey; the mono logos on Climb Orange. This preview switches with the theme toggle.

How to use it

Clear space: the height of the large "C" in Climb on every side.

Minimum width: 120px on screen, 30mm in print.

The li monogram is for favicons and app icons; the stacked tile is for social avatars.

Never recolour, stretch, outline or put the logo on a busy part of a photo.

Social and contact icons are round buttons: Climb Orange with a Dark Brown glyph, or quiet outlines on busy grounds. Every icon is a link with a text label for screen readers. The PNG set for email signatures is in the Signature downloads.

The email signature is one block, top to bottom: the sign-off; name, role, a Book a meeting link, phone numbers, email and website; the logo with a row of outlined social icons on the right; the help note that routes enquiries; the campaign banner; and the confidentiality line. Everything except the logo, icons and banner is live text.

How to use it

It reads on white and on dark mail clients: on white, links are Link on White; on dark, links are Climb Orange and the logo switches to the reversed version (this preview switches with the theme). Download the HTML template, the outline icons and the Email banners. Swap the banner with the campaign and link it to that campaign's page.
