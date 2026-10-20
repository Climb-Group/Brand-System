# Digital UI

For UI engineers and web designers. Values are the brand tokens, in the downloads as JSON (`brand.tokens.json`), CSS custom properties (`tokens.css`, `--climb-*`) and SCSS variables (`_tokens.scss`, `$climb-*`), so any platform can use them.

## Layout

- Breakpoints follow Bootstrap 5: `sm` 576, `md` 768, `lg` 992, `xl` 1200, `xxl` 1400.
- Content container is at most `layout-container` (1320px). On promotional pages, cards and subtitles, body text never runs wider than `layout-measure` (68ch, or `aaa-measure` 66ch in AAA layouts). Written pieces (blog posts, news, newsletters and articles) run to the full content width, because readers who open them expect a written page.
- 12-column grid with a `layout-gutter` (24px) gap. Sections are full bleed; content sits in the container.
- Vertical rhythm comes from the space scale: 4, 8, 12, 16, 24, 32, 48, 64, and `space-section` (96px) between web sections (64px on phones).
- Asymmetry is welcome: a 7 and 5 split, or a heading in 8 columns with nothing beside it, reads more like a festival poster than three equal columns.
- Long sales pages stay short to read. Under the hero, a row of jump links (44px targets) to each part of the page. Each audience gets a photo card (photo, name, its reason in one line, the whole card a link) leading to a short page of its own: why it suits them, three quotes from people like them, the questions they ask first, the three options we recommend for them (a first pick, one to add, one to go further), then one next step. A quotes section always shows three quotes; borrow a nearby audience's quote to make three. Related option sets share one section of tabs instead of a section each. Photo cards sit two across on phones, four on desktop, with titles that wrap between words.

## Surfaces and elevation

Elevation says what floats above what. Grounds stay flat (colour and photos do the work); the things you pick up float: photo cards, the ticket card, stickers and the primary button.

| Level | Light grounds | Dark grounds | Use |
| --- | --- | --- | --- |
| 0 | `shadow-0` (none) | flat | Sections, banners, most cards on dark |
| 1 | `shadow-1` | Charcoal on Dark Brown plus `shadow-hairline-dark` | Resting cards, inputs, chips |
| 2 | `shadow-2` | as 1, plus `shadow-2` at double opacity | Hovered cards, sticky header, dropdowns |
| 3 | `shadow-3` | Charcoal plus hairline plus `shadow-3` | Menus, popovers, floating ticket bar |
| 4 | `shadow-4` | as 3 with a Dark Brown 70% scrim behind | Modals and dialogs only |

- Shadows are tinted with Dark Brown, never pure black.
- On dark grounds a shadow alone disappears: raise a surface by moving it one step lighter (Dark Brown to Charcoal) and adding the hairline.
- Orange things glow orange, not grey: the primary button carries `0 8px 24px` Climb Orange at 35%, deepening on hover.
- The featured ticket card carries `0 18px 50px` black at 45% plus a 4px Climb Orange ring at 20%.
- `shadow-glow` and the `climb-glow` section class are the stage light: a soft orange radial at the bottom right of a dark section, or white light top left and Dark Brown depth bottom right on Climb Orange.
- Text over photos gets a `0 2px 12px` black text shadow at 60%.

## Shape

- `radius-small` 10px for inputs, tags and small buttons; `radius-card` 14px for cards, images and panels; `radius-pill` for primary buttons and chips.
- Section edges are square or cut: a diagonal top edge (`climb-cut-left`, `climb-cut-right`, at most 4rem of rise) hands one section to the next. Use a motif shape for other shaped edges. Never round a section.
- Stickers are `radius-small` tags tilted -4 degrees; tags are pill outlines.

## Interactive states

| State | Rule |
| --- | --- |
| Hover | Darker, never lighter: Climb Orange to Orange Text, Orange Text to `#B04902`. Cards lift by `motion-distance-lift` and move up one elevation level. `motion-duration-instant` for colour, `quick` for lift. |
| Pressed | Back to resting position, colour stays dark. No scale-down below 0.98. |
| Focus | 3px outline with a 3px offset, always visible on keyboard focus (`:focus-visible`): Orange Tint on dark grounds, Dark Brown on light grounds and on Climb Orange (see Accessibility, beyond AA). Never remove an outline without replacing it. |
| Disabled | 40% opacity on the control and `not-allowed` cursor; the label still meets 3:1 against the ground. Prefer explaining why over disabling. |
| Selected | Climb Orange marker (bar, dot or underline) plus a text or icon change. Colour is never the only signal. |

## Buttons

- Primary: Climb Orange pill with its orange glow, White label, Montserrat Bold 19px or larger (the contrast rule), min height `layout-target-min` (44px). One per section. On a Climb Orange ground the primary turns Dark Brown with a White label.
- Secondary: a 2px outline pill, White on dark grounds and Dark Brown on light ones, filling solid on hover.
- Pull link: the small uppercase tracked link at the foot of a section with a down arrow, handing the reader to the next section ("This is what it looked like last time").
- Text link actions: underlined, with an arrow (U+2192) after the label for "go somewhere" links.
- In a row of cards, every button sits on the same line at the bottom of its card, whatever the text above (see Offer cards).
- Labels are verbs, as in the Voice section: "Get your ticket", "Become a partner", "See what you get". No "Click here", no "Submit".

## Forms

- Labels above fields, always visible; placeholder text is a hint, never the label.
- Inputs: `radius-small`, 1px Body Slate border on light grounds, 48px tall, 16px text (stops iOS zoom).
- Errors: Orange Text message under the field with an icon and words that say how to fix it. Do not rely on a red or orange border alone.
- Success: a short line in the voice ("You are on the list."), not a modal.

## Icons

- Line icons on a 24px grid, 2px stroke, square caps and mitred joins, so they match the Ascent chevrons. Fill only for the selected state.
- Icon colour follows text colour. Orange only for the one marker in a view.
- The Ascent chevron doubles as the arrow icon for wayfinding and "next".
- Social icons and signature buttons are in the Signature downloads (see Email signatures).

## Data and numbers

- Charts use Climb Orange for the one series that matters and tones of the ground's ink (100%, 60%, 30%) for the rest. Never a rainbow.
- Big numbers in Montserrat ExtraBold (800). Public copy follows the voice rules: no attendance, meeting or investment figures in marketing.

### Outline numerals

Giant numbers drawn as an outline with no fill, for chapter and section numbers and the odd big stat.

- Montserrat ExtraBold (800), upright, tabular figures, letter spacing -0.04em, line height 0.8.
- No fill and a Climb Orange stroke of about 1% of the type size: 4px at 380px. Never thinner than 2px.
- Best on a dark ground or over a photo on a Dark Brown fade. On White or Light Grey use the darker text orange for the stroke; on Climb Orange use White.
- Section numbers are two digits, 01 to 10. They are decoration, so screen readers skip them and the real heading sits beside them in text.
- A stat keeps its number as readable text with a label underneath in words. In the AAA size set the stat fills solid.
- One size of outline numeral per view, and only for numbers. Headlines are never outlined.
- The quiet marquee is the one outlined line of words: giant italic uppercase in Orange Tint at 35% with a 2px stroke, running off the edge behind a section. It is decoration and never the only place the words appear.
- In design apps: the same font, weight and tracking, fill none, stroke Climb Orange centred at about 1% of the point size.
- On the web: `climb-outline-num` (and `climb-outline-num-sm` for stats), `climb-numbered` to sit a number beside its heading, and `climb-outline-marquee`. See the Outline numerals component.

## Ticket pages

The page sells, so every page has a path to a ticket. The festival sections make people want to come; the ticket elements make it easy to say yes now.

**Order on a ticket page:** promise and ticket card on the first screen, proof (photos, moments, quotes), the offer cards and release ladder, then a closing band with one button. Never more than two scrolls between a reason to buy and a way to buy.

**Offer cards.** Outlined cards side by side (four across on wide screens, one on phones, the picked-out one first).
- Each card: an optional pill kicker ("For you", "Add this"), the name, a big price with "inc VAT", one line of what it includes, one full-width button.
- One card is picked out: Climb Orange outline, a soft orange ring and glow, a filled kicker and the only filled button. The rest have outline buttons. It is never raised above the others at rest: that would knock its button off the row's line.
- **Buttons in a row line up.** Cards in a row are the same height, and each card is a column with its button pushed to the bottom (`margin-top: auto`), so every button in the row sits on one shared line however much text is above it. Keep at least 24px (`space-5`) between the text and the button.
- Release pricing shows "Full price" with the old price struck through, and "199 left at this price" in a soft orange pill.
- **Sold out** (only when the shop says so) keeps the card in place: dashed outline, price struck through, kicker and button both say "Sold out", the button is disabled. Never hide a sold-out option; it proves demand.

**Release ladder.** One ticket's price steps on a rail, so buyers see why now is cheapest.
- Each step has a cap, a dot on the rail, the release name, price, share of tickets and its state in words: Closed, Open now, Next, Final.
- Closed: solid grey cap, orange rail and dot, price struck through, muted. Open now: solid Climb Orange cap with a glow, a ringed dot, orange price and state, and a "left at this price" speech bubble above. Next and Final: dashed outline caps that rise with the price, the shape of what is coming.
- Wide screens: steps side by side, caps rising left to right. Phones: a vertical rail with the price on the right.
- State is never shown by colour alone: the word and the strike-through carry it too.

**Levels and stands.** Lists of levels (partner packages, stand sizes) sit in a ticket card as rows with a hairline between, the name on the left and what you get or what is left on the right. Stand cards carry a small floor-plan glyph (four outlined cells, filled to the stand's size) and a "59 left" pill; when none are left, the pill turns to an outline reading "Sold out" and the row or card stays.

**Group offer.** A Climb Orange band under the offers, Dark Brown text and button: "Bringing a team?"

Prices, release names and stock always come from the shop. Static copies are for mock-ups and campaigns that are updated by hand.

## Dark and light

- Dark first. Product and marketing pages default to preset 3 (Dark Brown) heroes with preset 1 or 2 reading sections.
- Portal, checkout and forms default to light presets for long reading and data entry.
- Respect `prefers-color-scheme` only where the whole surface supports both themes; never invert the logo by filter, use the reversed master.

## Accessibility, beyond AA

Every surface meets WCAG 2.2 AA. These rules take the brand most of the way to AAA, the highest level, without changing how it looks.

**Themes.** Four themes ship with the tokens: Dark (the default), Light, AAA-Dark and AAA-Light. The AAA themes raise every text pair to at least 7:1. Their tokens start with `aaa-`, and the themes are `theme.aaa-dark` and `theme.aaa-light`. Use them for long reading, forms and anywhere a person asks for higher contrast.

**Small text colours.** Small text means anything under 19px bold or 24px regular: eyebrows, tags, captions and links in running text.

| Ground | Small orange text and links | Ratio |
| --- | --- | --- |
| Dark Brown or Charcoal | Orange Tint `#F2AE86` | 9.93:1 and 8.35:1 |
| White | Deep Orange `#8D4419` | 7:1 |
| Light Grey | Deep Orange on Grey `#7A3B16` | 7:1 |

Climb Orange stays for large headline words, buttons and decoration. It is never used for small text.

**Focus.** Every focusable item shows a 3px ring with a 3px offset on keyboard focus. The ring is Orange Tint on dark grounds, and Dark Brown on light grounds and on Climb Orange. A card that holds a link shows the same ring around the whole card. Sticky headers never cover the item in focus.

**Targets.** Buttons, links, chips, tags and icon buttons are at least 44px by 44px (`layout-target-min`). The icon can stay 24px with padding around it. A compact 24px target (`layout-target-compact`) is allowed only where AA applies and space is tight, such as a dense row of social icons in an email signature.

**Headings.** Every section has a heading. When the design shows none, the heading is still there, visually hidden, so people using a screen reader can move from section to section.

**Links.** Link text says where it goes: "See the Climb27 lineup", not "Learn more". A link that opens a new tab says so in its text or its accessible name ("Partner terms, opens in a new tab"). No page redirects on its own, and nothing opens a new window without warning.

**Where am I.** Every page below the top level shows breadcrumbs: Home, then the section, then the page.

**Help on forms.** Every form has a way to get help: a contact route (email or phone) next to the form, and short, plain hints next to any field that needs one. Hints sit under the label, not inside the field.

**Interruptions.** Pop-ups, cookie prompts and offer banners can always be closed, and can be put off until later. They never close or move on a timer, and they never open by themselves in the middle of a task such as checkout or a form.

**Purpose.** Pages use landmarks (header, navigation, main, footer). Every icon button has a label a screen reader can read. Fields that ask for personal details (name, email, phone, company, address) carry the matching `autocomplete` value so browsers can fill them.

**Minimum text size.** No text is smaller than 13px, including micro labels and legal lines.
