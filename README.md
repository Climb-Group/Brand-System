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
| `.agents/skills/` | Agent Skills: `climb-voice` (copy rules and a copy checker) and `climb-visual-style` (visual rules). `.claude/skills` points here. The other skills there are the shared engineering standards synced from `Resnovas/.github`; `skills-lock.json` keeps them out of `npx skills`. |

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

## Use the brand in an AI assistant

The two brand skills, `climb-voice` and `climb-visual-style`, follow the open Agent Skills format, so any assistant that reads skills can use them.

Install them into every coding agent on your machine (Claude Code, Codex, Cursor, GitHub Copilot and the rest) with the `skills` command line tool:

```bash
npx skills add Climb-Group/Brand-System                    # pick agents and skills interactively
npx skills add Climb-Group/Brand-System --list             # see what it offers: the two brand skills
npx skills add Climb-Group/Brand-System -a codex -g -y     # both skills, for Codex, for every project
```

Or open an assistant with the brand already loaded. The brand centre shows these as buttons; the links themselves are in `ai/open-in.json`:

| Assistant | What the button does |
| --- | --- |
| Claude | Opens a new chat with a prompt that has Claude read both skills first. To keep them, upload `ai/packages/climb-voice.zip` and `ai/packages/climb-visual-style.zip` under Settings, Capabilities, Skills. |
| Claude Code | Starts a session on this repository, which loads both skills from it. |
| Codex | Opens a new chat in the Codex app with a prompt that installs both skills with the command above, then loads them. |
| Microsoft Copilot | Opens Copilot with a prompt that has it read both skills first. For Microsoft 365 Copilot, `ai/packages/climbuk-brand-agent-m365.zip` is a ready-made agent: add it as a custom app in Teams, or have an admin deploy it. |

None of these vendors offers a link that installs a skill for you, so each button opens the assistant with a prompt and the packages cover the rest. Rebuild the packages and links with `python3 ai/agents/build_agent_kits.py` after changing a skill; details are in `ai/README.md`.

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

## Repository setup and checks

The repository follows the shared engineering setup from `Resnovas/.github`: the governance documents at the root (`AI_POLICY.md`, `DCO.md`, `GOVERNANCE.md` and the rest), the house workflows in `.github/workflows/house-*.yml`, the editor and agent surfaces (`.vscode/`, `.zed/`, `.run/`, `.codex/`, `.cursor/`, `.agents/`) and the commit hook. A weekly sync pull request keeps them current; lines after a `house:local` marker are this repository's own. `LICENSE` is not synced, because the brand material is ClimbGroup's.

On a fresh clone, with Node 24 and Python 3:

```bash
scripts/agent-setup    # installs the commit hook and editor actions, then runs every check
node --run check       # what CI runs: tokens, agent kits, dashes, agent files, LLMS.md
node --run test        # token and AI kit tests
```

The house release workflows (`House release`, `House nightly`, `House release preview`) do nothing here until the repository has a `release.config.json`; the template downloads are released separately, and the media kit exports by the `media kit` workflow below.

## Release the media kit exports

The rendered artwork (social, call backgrounds, wallpapers, stage and screens, print and merch, email banners), the full guideline books, the templates and the photo library run to several hundred megabytes, so they are never committed. The `media kit` workflow builds them into `climb-media-kit-exports.zip` and attaches it to a new release named `media-kit-<date>-<commit>`. The website imports that file from its link (Website > Configuration > Media kit > Import a kit).

It runs on every push to `main` that changes the artwork sources (`generators/`, `illustrations/`, `logos/`, `photos/`, `pdf/`, `templates/`, `tokens/`, `fonts/`), and by hand from the Actions tab with two options:

| Option | Default | What it does |
| --- | --- | --- |
| `builder-ref` | `claude/brand-media-kit` | The branch or tag of the website repository whose kit builder (`climb_brand_media_kit/scripts/build_kit.py`) to run. |
| `photo-library` | ticked | Adds the photo library from the `photo-library` release. |

Each run renders the catalogue (`generators/catalogue.py` and `generators/render.mjs` in headless Chromium), builds the template install package (`templates/_build/package_build.py`), downloads the fonts, then runs the kit builder. The job summary prints the import link.

### Set it up once

1. Create a read-only token for the website repository (contents: read) and save it in this repository as the secret `MEDIA_KIT_BUILDER_TOKEN`. The builder lives there, and that repository is private.
2. For the photo library, zip the library folders (one folder per group, with any excluded photos already removed) as `climb-photo-library.zip` and attach it to a release tagged `photo-library`. To leave photos out without rebuilding the zip, also attach `media-kit-exclude.txt` with one `folder/filename` line per photo. Replace the files there when the library changes. Without the zip the kit builds with no photo library and the job summary says so.

### What it cannot build

- The 4K motion clips: they are their own download (`climb-video-motion-v1`), rendered separately.
- PNG copies of the drawings: the builder takes them with `--drawing-png`, but no script in this repository renders them yet.

### Common problems

- **"Add the MEDIA_KIT_BUILDER_TOKEN secret".** The secret is missing or empty; see step 1.
- **The kit has no photos.** The `photo-library` release or its `climb-photo-library.zip` is missing; see step 2.

## Licence

The fonts are under the SIL Open Font License (`fonts/OFL-*.txt`). Everything else is the property of ClimbGroup; see `LICENSE`.
