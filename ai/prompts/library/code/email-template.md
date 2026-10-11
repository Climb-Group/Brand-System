---
title: Build an on-brand email template
description: Writes a responsive, accessible HTML email in the ClimbUK style that works in the main email apps.
display: Build an on-brand ClimbUK HTML email template
task: Code
department: Engineering
apps: Copilot web, Copilot work
brand: both
locale: en-GB
---

Build a responsive HTML email for ClimbUK: {{email_type}}.

1. Table-based layout with inline CSS so it renders in Outlook, Gmail and Apple Mail; 600px wide, single column on mobile.
2. Use the ClimbUK brand colours from the tokens; light ground for reading-heavy emails, Dark Brown header band. One orange button, as a bulletproof button with a 19px bold white label.
3. Real text, not text in images. Alt text on every image. lang="en-GB", a role="presentation" on layout tables, a preheader line.
4. Copy placeholders in square brackets, written in the ClimbUK voice, with link text that says where it goes.
5. Footer: contact line, unsubscribe link and the legal company name line.

Return the full HTML and a short note on what to test before sending.
