# ClimbUK brand pack

Everything that makes ClimbUK, ClimbGroup and each edition (Climb27 and later) look and sound like themselves, for people and for AI agents. This repository holds the brand only: no website code and no platform modules. Those live in their own repositories and take their brand files from here.

## What is in it

| Folder | What it holds |
| --- | --- |
| `tokens/` | Design tokens: colours, presets, themes (Dark, Light, AAA-Dark, AAA-Light), type, spacing, radius, shadow, motion, print colours. `brand.tokens.json` is the source; `tokens.css` and `_tokens.scss` are generated. |
| `logos/` | Logo masters per brand (SVG and PNG, contact sheets) and the script that builds them. |
| `fonts/` | Montserrat and Open Sans (SIL Open Font License). |
| `illustrations/` | The house line illustrations, one SVG per object, and the background shapes in `shapes/`. |
| `icons/social/` | Social icons and signature buttons in SVG and PNG. |
| `photos/` | Consented event photography used across the brand. |
| `guidelines/` | The brand book chapters: voice, UI, motion, photography, video, print, press and partners, signatures. |
| `accessibility/` | A live demo of the AAA theme and size switches. |
| `components/` | Live HTML and CSS brand components (the brand hub), built from the website blocks. |
| `generators/` | Scripts that make call backgrounds, wallpapers, social posts, email banners, festival and poster kits. |
| `previews/` | Contact sheets and previews of the brand in use. |
| `reference/` | The original motif vectors. |
| `media-kit/` | Downloadable bundles of the whole pack. |
| `web/` | Interactive brand system pages. |
| `pdf/` | One-page key rules and the full brand guidelines book, per brand. |
| `templates/` | Office templates (Word, Excel, PowerPoint) and video templates (Premiere Pro, DaVinci Resolve). |
| `ai/` | Topics and instructions that let AI assistants use the brand. |
| `.agents/skills/` | Agent Skills: `climb-voice` (copy rules and a copy checker) and `climb-visual-style` (visual rules). `.claude/skills` points here. |

## Change a colour or a size

1. Edit `tokens/brand.tokens.json`. If you add a colour pairing that text will use, add it to `pairs` with `normal` (4.5:1), `large` (3:1), `aaa` (7:1) or `aaa-large` (4.5:1).
2. Run `python3 tokens/build_tokens.py`. It prints every pair with its ratio, fails if one is below its threshold, and rewrites `tokens.css` and `_tokens.scss`. Add `--copy-to PATH.scss` to also write a copy for a website theme or module.
3. Run the tests: `python3 -m unittest discover -s tokens/tests`.
4. Commit the JSON and the generated files together.

`python3 tokens/build_tokens.py --check` fails when a pair is below threshold or a generated file is out of date, without writing anything. CI runs it on every pull request.

## Check copy

```bash
python3 .agents/skills/climb-voice/scripts/check_copy.py path/to/copy.txt
python3 .agents/skills/climb-voice/scripts/check_copy.py --announced path/to/copy.txt   # once the Climb27 venue is public
echo "Your text" | python3 .agents/skills/climb-voice/scripts/check_copy.py -
```

## Rebuild the artwork

```bash
python3 generators/illustrations.py     # illustrations/*.svg
python3 generators/build_shapes.py      # illustrations/shapes/*.svg
python3 logos/_build/build.py           # logos/
python3 generators/catalogue.py build/assets && node generators/render.mjs build/assets   # the asset catalogue as PNG
```

Details and options for each generator are in `generators/README.md`. The component hub is rebuilt from the website blocks with `python3 components/build_components.py --module PATH/TO/climb_website_brand`.

## Common problems

- **A pair fails after a colour change.** Darken the foreground (for orange text on light grounds) or lighten it (on dark grounds) until the build passes; hover states go darker, never lighter.
- **The checker flags "Climb".** Write the full name: ClimbUK, ClimbGroup or the edition, for example Climb27.
- **The checker flags the venue.** Venue details are embargoed until ClimbUK announces them. Use `--announced` only after the announcement is live.

## Licence

The fonts are under the SIL Open Font License (`fonts/OFL-*.txt`). Everything else is the property of ClimbGroup; see `LICENSE.md`.
