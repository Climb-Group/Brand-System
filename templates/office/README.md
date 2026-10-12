# Office templates

Word, Excel and PowerPoint templates for ClimbUK, ClimbGroup and Climb27, so every document, sheet and deck starts on brand. Each brand has the same set; pick the folder for the brand that leads the piece (an edition such as Climb27 leads on event pieces, ClimbGroup on company and legal pieces, ClimbUK everywhere else).

| Brand folder | Word (`.dotx`) | Excel (`.xltx`) | PowerPoint (`.potx`) |
| --- | --- | --- | --- |
| `ClimbUK/`, `ClimbGroup/`, `Climb27/` | Letterhead, Report, Proposal, Press release, Meeting notes | Event budget, Partner pipeline, Run sheet, Content calendar | Presentation 16:9 (19 layouts, 14 example slides) |

The second set, for any company and for the events business. "All" is every brand folder; "UK and Group" is `ClimbUK/` and `ClimbGroup/` only.

| App | All three brands | ClimbUK and ClimbGroup only |
| --- | --- | --- |
| Word | Memo, Contract, Partnership agreement, Award sponsorship agreement, Exhibitor agreement, Non-disclosure agreement, Business plan, Policy, Standard operating procedure, Case study, Fact sheet, Newsletter, Certificate (award, completion and appreciation pages), Terms and conditions, Post-event report, Exhibitor manual, Speaker brief, Host brief, Event risk assessment and method statement, Event day pack, Attendance certificate | Statement of work, Job description, Offer letter, Employee handbook, Brief, Board report |
| Excel | Invoice, Quote, Purchase order, Profit and loss, Expense claim, KPI dashboard, Project plan (Gantt), Task tracker, Risk register, Contact list, Timesheet, Speaker and session tracker, Production critical path, Supplier and crew tracker, Floor plan and stand allocation, Staff and volunteer rota, Feedback survey results | Annual budget, Cash flow forecast, Supplier register, Asset register, Leave planner, Recruitment tracker |
| PowerPoint | Investor pitch deck, Sales deck, All-hands, Org chart, Partner prospectus, Stage holding slides, Speaker slides | Quarterly business review, Board presentation, Project kick-off, Training deck |

Every deck shares the presentation template's master and layouts; the stage holding slides add Holding, Up next and Logo grid layouts. The contract is the general services agreement; the three event agreements (partnership, award sponsorship, exhibitor) are their own files with the same clause headings and a schedule each. Clause bodies are slots for the approved wording. The certificates and the attendance certificate carry mail merge fields (First_name, Last_name, Event, Date, CPD_hours) so a list of names fills them in one go.

**Co-branded versions for people outside the company** are in `<Brand>/external/`, named `External-...`: the investor pitch deck (for founders pitching at the event), the stage holding slides (for a partner stage), the speaker slides (with the speaker's own logo slot) and the exhibitor and partner risk assessment (Word and Excel, with the five steps, the 5 x 5 matrix, the scored register and example hazards). Each carries a "Your logo" slot and the brand as the host mark ("Speaking at Climb27", "Pitching at ClimbUK", "Hosted at Climb27"), fewer layouts and no internal content. In the install package they sit in the brand's folder with the other templates.

Also here:

- `_shared/fonts/`: Montserrat and Open Sans as desktop fonts (static TTF, every weight the templates use) with their licences.
- `_shared/office-theme/`: a `.thmx` theme per brand, plus the colour and font schemes on their own.
- `libreoffice/`: the same templates as `.ott`, `.ots` and `.otp` for LibreOffice.
- `previews/`: contact sheets per brand: `_Word`, `_Excel` and `_PowerPoint` for the first set, `_Word-company`, `_Word-events`, `_Excel-company`, `_Excel-events` and `_Decks` for the second set, and `_External` for the co-branded versions.
- `<Brand>/defaults/`: the files Office opens for a new blank file (`Normal.dotm` letterhead for Word, `Blank.potx` for PowerPoint on Windows, `Default Theme.thmx` for PowerPoint on Mac, `Book.xltx` for Excel). The install package sets them for each person; see "Make a brand the default" in `../install/README.md`.

## Install

1. **Fonts first.** Install every file in `_shared/fonts/` (Windows: select all, right-click, Install for all users. Mac: double-click, Install. Linux: copy to `~/.local/share/fonts` and run `fc-cache -f`). Without them Office falls back to Arial and the templates lose their look.
2. **Templates.**
   - Windows: copy the `.dotx`, `.xltx` and `.potx` files to `Documents\Custom Office Templates`. They then show under File, New, Personal (or Custom).
   - Mac: copy them to `~/Library/Group Containers/UBF8T346G9.Office/User Content/Templates`. They show under File, New from Template.
   - Microsoft 365 for the web: upload the file to OneDrive or SharePoint and open it; Save a copy for each new piece. For a whole team, an admin can publish them as organisation assets.
   - Google Docs, Sheets and Slides: upload the file and open it with Google; save it as a Google file and use Make a copy for each piece. You do not need to install the fonts there: Montserrat and Open Sans are in Google's font list.
   - LibreOffice and Collabora Office: File, Templates, Manage Templates, Import, and pick the files in `libreoffice/<Brand>/`.
   - ONLYOFFICE: open a `.dotx`, `.xltx` or `.potx` with File, Open; it starts a new file from it. The install package in `install/` adds them to the ONLYOFFICE Templates list for you.
   - WPS Office, SoftMaker Office, Apple Pages, Numbers and Keynote: see "Other office apps" in `install/README.md`.
3. **Theme (optional).** In any Office app, Design (or Page Layout), Themes, Browse for Themes, and pick the brand's `.thmx`. This puts the brand colours in every colour picker and sets Montserrat for headings and Open Sans for text in any file, not only these templates. To make the colours and fonts show in Office's lists permanently, copy `Theme Colors/Climb.xml` and `Theme Fonts/Climb.xml` into `%APPDATA%\Microsoft\Templates\Document Themes\` (Windows) or `~/Library/Group Containers/UBF8T346G9.Office/User Content/Themes/` (Mac), into the folders of the same name.

## Using them

- **Styles do the work.** Use Title, Heading 1 to 3, Eyebrow, Lead, Quote, Quote Source, Callout, Big Number, Caption and Small Print from the Home tab. Do not format by hand: headings build the contents page and let screen readers move around the document.
- **One orange word, one italic word** per headline. In Word, select the word and apply the Orange Word character style (it uses the small-text orange that passes contrast on white). In PowerPoint, colour it Climb Orange from the theme colours.
- **Dark first, light for reading.** PowerPoint opens on Dark Brown layouts; use the "(light)" layouts for slides people will read closely. Word and Excel are light because they are for reading and printing; report and proposal covers are dark.
- **Photos.** Picture placeholders in PowerPoint crop to fit. Use real, consented event photos, never stock. Give every picture alt text (right-click, View Alt Text).
- **Tables.** Word uses the Climb Table style (Dark Brown header row that repeats on each page). Excel sheets are Excel tables with drop-down status lists, totals and print setup (A4 landscape, fit to width). Light Grey cells in a workbook are the ones you fill in; every total, score, band and date header is a formula. Invoices, quotes, purchase orders and expense claims carry an editable VAT rate (20 percent by default) and the company's legal line and VAT number.
- **Risk bands.** Risk registers write the band in words (Low, Medium, High, Critical) and colour the cell as well; the colours all pass contrast, and the word is what counts.
- **Legal line.** Letterheads and documents carry the company's legal line in the footer. Keep it on anything that leaves the company.

## Accessibility

- Contrast: every text colour pair comes from the brand tokens and meets WCAG 2.2 AA (body text on white 7.1:1, White on Dark Brown 18.65:1, Orange Tint on Dark Brown 9.93:1). White on Climb Orange is used only for large text (14pt bold and up).
- Structure: real heading styles, a title on every slide (the Blank layout keeps one off the slide edge for screen readers), table header rows marked to repeat, language set to English (UK).
- Images: logos carry alt text; backgrounds and motifs are backgrounds or marked decorative so screen readers skip them.
- Before sending: run Review, Check Accessibility in Office.

## Rebuild

The templates are generated from the brand tokens, logo masters, photos and motif recipes, so a colour or logo change is a rebuild, not a redesign. See `../_build/README.md`.
