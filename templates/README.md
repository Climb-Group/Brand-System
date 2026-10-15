# Templates

Files to install on people's machines so documents, sheets, decks and videos start on brand, for ClimbUK, ClimbGroup and Climb27.

- `office/`: Word (`.dotx`: letterhead, report, proposal, press release, meeting notes, and the second set from memo and contract to exhibitor manual and event day pack), Excel (`.xltx`: event budget, partner pipeline, run sheet, content calendar, and the second set from invoice and cash flow to floor plan and feedback results) and PowerPoint (`.potx`: the presentation template with 19 layouts and 14 example slides, and the decks from investor pitch to stage holding slides) per brand, co-branded versions for people outside the company in each brand's `external/` folder, plus the desktop fonts, Office theme files, LibreOffice copies and previews. The full list and the install guide are in `office/README.md`.
- `video/`: 4K 25fps lower thirds, stickers, a slab wipe, title and end cards, background loops, DaVinci Resolve Fusion titles (`.drfx`), a Premiere Pro sequence, the grade LUT and caption settings. Install guide in `video/README.md`. The motion clips ship as a release download.
- `m365/`: Microsoft 365 and Teams Premium branding: meeting themes, 78 meeting backgrounds, branded reactions, the organisation theme, app launcher tiles, a Teams app for Odoo and the sign-in page, with an admin-centre setup guide in `m365/README.md`.
- `_build/`: the scripts that make all of it from the tokens, logos and photos.

Every template's words are in a copy file (`<name>.copy.md`) beside it, which the build reads: edit the words there and rebuild. `templates/brands.copy.md` holds the lines every template shares (legal line, websites, emails, tagline, edition dates). `_build/README.md` lists every copy file and what reads it.

Each template uses the token colours and the brand fonts, and meets WCAG 2.2 AA.
