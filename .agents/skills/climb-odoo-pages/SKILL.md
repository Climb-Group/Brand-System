---
name: climb-odoo-pages
description: Platform rules for putting the ClimbUK, ClimbGroup and Climb27 brand on an Odoo website - pages, website blocks (snippets), QWeb templates, generated brand pages and Odoo modules - so every page stays editable in the Odoo website editor and follows the website theme. Load it only when the target is an Odoo website or an Odoo module, together with climb-visual-style and climb-voice. Do not load it for other platforms; their rules stay vendor neutral.
license: Proprietary
metadata:
  owner: ClimbGroup marketing
  applies-to: Odoo 19 and Odoo 20 websites
  version: "1.0"
---

# ClimbUK on an Odoo website

The brand rules (`climb-visual-style`, `climb-voice`) say what a page looks and sounds like on any platform. This skill adds what an Odoo website needs on top, and only there: the marketing team must be able to open any page we ship, click **Edit**, change the words, links and images, and save. A page that looks right but cannot be edited is a failed delivery.

## The rules

1. **Copy lives in a view.** Every word, link and image someone may want to change sits in the arch of a QWeb view: a `website.page`, or a `<template>` the controller renders with `request.render()`. Never put page copy into the page as a string: no `t-out`/`t-raw` of an HTML string, no `Markup(...)` read from a file, a field or a generator at request time, no copy written by JavaScript. The editor can only save to a view; anything else is shown but locked, and the whole page reads as broken.
2. **Generate views, not strings.** When pages are built by a script (brand book pages, generated guidelines), the script writes the view XML (one view per page, valid XML, SVG names in their own case) at build time, and the controller renders that view. Never read generated HTML from disk in a controller.
3. **Keep live data in small islands.** Records, counts, prices and media-kit cards come in through `t-out`, `t-field`, `t-foreach` or `t-call` on the smallest element that holds them. Odoo brands the static parts around them for the editor; an element that contains a `t-*` directive is not itself editable, its static children are. So a `t-if` on a whole section locks nothing, but a `t-out` on a section wrapper locks everything inside it.
4. **Lock what scripts change.** Anything a script changes as people use the page (search panels, theme or size switches, filters, contrast checkers, sliders, copy buttons, menus that open) carries `t-ignore="true"` on its outermost element, or is its own `t-call` template marked `o_not_editable`. Otherwise an edit saved while the script had changed it freezes that state (a class, a hidden panel, a filled-in result) into the page for good. Form controls, frames, scripts and code samples are locked the same way.
5. **Give the editor room.** Every page has at least one empty `<div class="oe_structure" id="oe_structure_<page>"/>` with a unique id, where blocks can be dropped in. Website blocks we ship are real snippets (a `section` with `data-snippet` and the theme's colour classes), so they can be moved, copied and restyled.
6. **Use the theme, never hard-coded values.** In an Odoo module, colours, fonts and spacing come from the website theme: colour combinations (`o_cc1` to `o_cc5`), the theme's CSS variables (`--o-color-1` to `--o-color-5`, Bootstrap variables) and its fonts, which are set to the brand tokens. Never type a hex value, font name or pixel size in a module's templates or SCSS, so a theme change reaches every page. A self-contained brand page that ships the token stylesheet (`tokens.css`) is the one exception, and it still takes every value from the tokens.
7. **Same on Odoo 19 and Odoo 20.** Build and test on both until the move to Odoo 20 is done. Only the manifest version and the access file may differ; features and markup are the same.
8. **Edits on the website are copies.** When someone saves a page in the editor, Odoo keeps a website-specific copy of that view. A later module update changes the original, not the copy. Say so in the module README, and make lasting changes in the source (the brand pack or the module) as well as on the page.
9. **Copy stays translatable and on brand.** Text in views goes through the website translator, so keep copy in the arch, not in JavaScript or CSS `content:`. Run the `climb-voice` checker on it like any other public copy.

## How to check a page before you call it done

On a local Odoo 19 and Odoo 20 with the module installed or upgraded:

1. As a logged-out visitor, the page answers 200 and looks right.
2. As a website designer, view the page source: the headings and paragraphs you expect to be editable carry `data-oe-model="ir.ui.view"` and a `data-oe-id`; nothing a script changes carries them.
3. Click **Edit**, change a word in the body, save, and reload as a visitor: the change shows. Check that the locked tools cannot be edited. Then delete the website copy of the view (developer mode, **Settings > Technical > Views**, the copy with a website set) to put the page back.
4. Cover it with a test: an `HttpCase` that fetches the page as an admin and asserts the branding on a heading and its absence on the scripted parts, and one that saves through `ir.ui.view.save()` at the heading's `data-oe-xpath` and finds the change on the page.

Say in your final message which pages you checked, on which versions, and what you found.
