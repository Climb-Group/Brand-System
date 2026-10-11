---
title: Build an on-brand web section
description: Writes an accessible HTML and CSS section in the ClimbUK style using the brand tokens, ready to drop into a page.
display: Build an on-brand ClimbUK web section
task: Code
department: Engineering
apps: Copilot web, Copilot work
brand: both
locale: en-GB
---

Build a responsive web section for ClimbUK: {{purpose}}. Content to use: {{content}}

Rules:
1. Plain semantic HTML and CSS. Use the ClimbUK token custom properties (var(--climb-...)) from tokens.css for every colour, size, space and radius; never type a raw colour value.
2. Dark first: Dark Brown ground unless the content is reading-heavy. One orange call to action per section, with a 19px bold white label.
3. Headline: Montserrat, uppercase, one word in Climb Orange and one in italic. Body in Open Sans.
4. WCAG 2.2 AA at least: one heading level in order, real buttons and links, visible focus, 44px targets, alt text, contrast from the brand presets, respects prefers-reduced-motion.
5. Every button in a row of cards shares one baseline (cards as flex columns, last block pushed down).

Return the HTML and CSS, then a short list of the accessibility checks you made.
