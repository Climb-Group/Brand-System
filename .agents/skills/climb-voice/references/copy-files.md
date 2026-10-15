# Copy files

Every file in the brand pack (each flyer, PDF, slide deck, spreadsheet, document, banner, image and logo) has its words in a Markdown file beside it or beside its build, named `<name>.copy.md`. People review and edit the words there, in any text editor or on GitHub, without opening the design. The build reads the file, so an edit to the words is an edit to the piece: change the file, rebuild, and the new words are in the output.

Design sections are marked with one-line HTML comments. Markdown viewers hide them, so the file reads as a clean document, and a script finds every section by its name.

## A full example

```markdown
---
copy: climb27-flyer-scaling-companies
deliverable: Climb27 A5 flyer for scaling companies, front and back
build: pdf/flyers/_build/segments.py
output: pdf/flyers/segments/climb27_flyer_scaling-companies_a5.pdf pdf/flyers/segments/svg/climb27_flyer_scaling-companies_a5_*.svg
order: 1
---

# Climb27 flyer: Scaling companies

<!-- note: [[Double brackets]] print in the highlight colour and *stars* print in italics. -->

## Front

<!-- @front.photo name=crowds_04 focus=0.5,0.35 -->

<!-- @front.headline -->
Scale with the [[right people]] in the *room*.

<!-- @button -->
<!-- note: Printed on both sides. -->
Get your *ticket*

## Back

<!-- @back.reason icon=people -->
### Find your people
Fellow founders one step ahead, advisers, partners and investors looking for real deal flow.

<!-- @back.reason icon=calendar -->
### Meetings you choose
Book meetings in the ClimbGroup Event App before you arrive.
```

## The parts

| Part | Looks like | What it does |
| --- | --- | --- |
| Front matter | `---` lines at the top with `key: value` lines between | Describes the file. `copy` (a lowercase id with hyphens, unique in the pack) and `deliverable` (what the piece is, in plain words) are required. `build` (the script that reads it) is a path from the top of the pack. `output` lists the files it covers, as paths or globs from the top of the pack separated by spaces, such as the PDF and its layered SVGs. `files` lists more, as globs from the copy file's own folder. Every path and glob must find a file. `allow` lists words the copy rules would flag but this piece must print, separated by spaces, for staff-only pieces and working files: the vendor name of an internal app (`allow: Odoo`), a `Venue` cost line in a budget, a `Draft` status in a run sheet. Never use it for customer-facing words. Any other key, such as `order`, is for that build. |
| Section marker | `<!-- @front.headline -->` on its own line | Starts a design section. The words after it, up to the next marker or a `#` or `##` heading, belong to it. |
| Section name | `front.headline`, `back.reason`, `back.qr-note` | Lowercase words with hyphens, with a dot between levels: the part of the piece, then the slot in it. The same name can repeat for a list of things in order, such as five `back.reason` sections. |
| Settings | `icon=people`, `focus=0.5,0.35`, `label="Two words"` | Design choices for that section, after its name: which icon or photo, where to crop, which layout. Quote a value that has spaces. Each key once per marker. |
| Title | `### Find your people`, the first line after a marker | The section's title, kept apart from its text. |
| Text | The rest of the section | Plain Markdown. Lines wrapped by hand join into one line. A blank line starts a new paragraph. A line ending in a backslash (`\`) breaks the line there. List items keep their own lines. |
| Example | `<!-- @rewrites.before example=avoid -->` | A section that quotes words on purpose, such as the "not this" side of a rule. The build prints it; the copy checker skips its words. Use it only for words a rule bans, never to get past the checker. |
| Note | `<!-- note: Check the app name. -->`, on its own line, may run over several lines | For reviewers only. Builds and the copy checker ignore it. Put an explanation or a question here, never words that should print. |
| Headings | `# Title`, `## Front`, `## Back` | For people reading the file. They end the open section and never print. |

Inline marks inside the text:

- `*word*`: italic (the italic word in a headline).
- `[[word]]`: the highlight: the orange word in a headline, or the piece's highlight colour or bar.
- `**word**`: bold, where the piece supports it.

Words outside a section, a marker that shares its line with other text, an unclosed comment and a section name with capitals or underscores all stop the build with the file and line.

## One copy file per set of files

A copy file covers every file that carries the same words: a flyer's PDF and its two SVGs, a template in each of its formats, a logo on each ground, an image at each size. List them all in `output` or `files`, so a script can tell which copy file holds the words of any file in the pack. The finished files stay in the pack as they are; the copy file and the layered SVG are how the team edits them.

- A file with no words of its own (a photo, an icon, a background) gets an `@alt` section with the alt text it is shown with.
- A build that cannot run here (its words live in another repository) still gets its copy file, with `source: mirror` in the front matter, holding the words exactly as they print. The tests check that a mirror parses and covers its files; the copy rules are only reported for it, and a note in it names each line that breaks a rule, to fix where the words live.
- Source code, tests, build folders (`_build`, `tools`) and generated tool files need no copy file.

Find every file in the pack that no copy file covers:

```bash
python3 .agents/skills/climb-voice/scripts/copy_md.py coverage
```

The pack's tests fail while it lists any file.

## Check a copy file

```bash
python3 .agents/skills/climb-voice/scripts/check_copy.py pdf/flyers/copy/segments/investors.copy.md
python3 .agents/skills/climb-voice/scripts/copy_md.py words pdf/flyers/copy/segments/investors.copy.md   # the words a reader sees
python3 .agents/skills/climb-voice/scripts/copy_md.py json pdf/flyers/copy/segments/investors.copy.md    # the sections, for scripts
```

The checker first checks the markers, then checks only the words (front matter, markers and notes are blanked out, so its line and column numbers still point into the file). The pack's tests run it over every copy file.

## Read one in a build

`copy_md.py` uses only the Python standard library. Put its folder on the path and load the file:

```python
import copy_md

doc = copy_md.load("pdf/flyers/copy/segments/investors.copy.md")
head = doc.one("front.headline").text               # exactly one section, or a CopyError naming the file and line
sub = doc.words("front.subline", "The Festival for Business Growth")  # optional section, with a default
reasons = [(r["icon"], r.title, r.text) for r in doc.all("back.reason")]
```

## Rules for a new piece

1. Write the copy file first, then the build that reads it. Never type a printed word in the build script; a word the layout needs (an eyebrow, a sticker, a QR note) gets its own section.
2. Name sections for where they sit (`front.headline`), not for how they look (`orange-text`).
3. Use the same section names in the editable artwork: the layer or group that holds `front.headline` is named `front.headline`. Group the artwork by what belongs together, such as one group per reason row with its icon, title and text (see the climb-visual-style skill, "Editable sources").
4. Lines that every piece in a set shares (dates, tagline, website) go in one shared copy file for the set, such as `pdf/flyers/copy/shared.copy.md`.
5. List every file the copy file covers in `output` or `files`, then run the checker and `copy_md.py coverage` before you commit.

## Common problems

- **"words outside a section"**: a line of text sits above the first marker or straight after a `##` heading. Add a marker above it, or make it a note.
- **The rebuilt piece shows the old words**: the build reads a different file. The `build` key in the front matter names the script that reads it.
- **A headline breaks in the wrong place**: end the line where it should break with a backslash.
- **"no copy file covers it"**: add the file to the `output` or `files` line of the copy file with its words, or write a copy file for it.
