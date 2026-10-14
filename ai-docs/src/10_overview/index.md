## The ClimbUK brand pack

This repository is the ClimbUK brand: tokens, logos, illustrations, photography, guidelines, templates and two Agent Skills. It holds no website or platform code, and no TypeScript, so the house rules for Effect, Nx and feature flags have nothing to apply to here. The brand scripts are plain Python using the standard library.

### Use the brand from an agent

- Load `.agents/skills/climb-voice` for any words and `.agents/skills/climb-visual-style` for anything visual; both for an asset with words on it. Only when the target is an Odoo website or module, also load `.agents/skills/climb-odoo-pages` (pages stay editable in the website editor and take their values from the theme). Run `python3 .agents/skills/climb-voice/scripts/check_copy.py FILE` on every piece of copy.
- Every colour and size comes from `tokens/brand.tokens.json`. Never type a value that is not in it.
- `ai/tools/brand_rules.py` answers brand questions as tools (`call(tool, arguments, venue_announced)`); `ai/kit.json` lists them.

### Copy files and editable sources

- Every built piece keeps its words in `<name>.copy.md` beside its build; the build reads it, so change words there and never in the script. The Climb27 flyers' copy files are in `pdf/flyers/copy/` (`segments/`, `general/` and `shared.copy.md`).
- Mark design sections with `<!-- @part.slot key=value -->` on their own line; the words up to the next marker or `#`/`##` heading belong to it, a first `###` line is its title, and `<!-- note: ... -->` is for reviewers only. The standard is `.agents/skills/climb-voice/references/copy-files.md`.
- Read one with `copy_md.load(path)` from `.agents/skills/climb-voice/scripts/copy_md.py`: `doc.one("front.headline").text`, `doc.words("front.subline", default)`, `[(r["icon"], r.title, r.text) for r in doc.all("back.reason")]`. A broken file raises `copy_md.CopyError` with its file and line.
- `check_copy.py FILE.copy.md` checks the markers, then only the words. `python3 -m unittest discover -s ai/tests` runs it over every copy file in the pack.
- Artwork ships as a layered SVG whose layer `id` and `inkscape:label` are the copy file's section names, with live text, so it opens in Inkscape and Affinity (`climb-visual-style`, "Editable sources").

### Logos and app icons

- Every logo, icon, favicon and app tile is transparent by default; each also comes on solid White, Dark Brown and Climb Orange. Logo files take the suffix `-on-white`, `-on-ground` or `-on-orange` (`logos/ClimbUK/ClimbUK_icon-monogram-on-ground.svg`); app icons sit in `white/`, `ground/` and `orange/` subfolders of `app-icons/favicons/` and `app-icons/app-tiles/`.
- Ask the logo tool, not memory: `call("logo", {"brand": "ClimbUK", "use": "favicon"})` returns the transparent `icon-monogram` and lists the three solid versions under `on_solid`; add `"fill": "ground"` for the Dark Brown file.
- Code that wants the old Dark Brown tile uses `icon-on-ground` or `icon-monogram-on-ground`.
- Rebuild with `python3 logos/_build/build.py && python3 logos/_build/sheet.py`, then `python3 app-icons/_build/build_app_icons.py`. All need `rsvg-convert` and Pillow.

### Fonts

- Montserrat and Open Sans ship in three formats: `fonts/ttf/` (TrueType) and `fonts/otf/` (OpenType, PostScript outlines) hold every style the brand uses, named `<Family>-<Style>` (`fonts/otf/OpenSans-SemiBold.otf`); the `fonts/*.woff2` files are Latin-only web fonts for pages.
- Hand an app, an office suite or a brand centre upload the TTF or OTF file, never the WOFF2; tools that take uploaded fonts refuse WOFF2.
- `python3 fonts/_build/fetch_fonts.py` (needs fontTools) fetches the official builds at pinned commits; Open Sans has no official OTF, so its OTF files are converted from the official TTF. `python3 -m unittest discover -s fonts/tests` checks both formats with the standard library only.

### Install the skills elsewhere

- `npx skills add Climb-Group/Brand-System` offers exactly the two brand skills. The house skills synced into `.agents/skills` are listed in `skills-lock.json`, which `npx skills` treats as already installed and hides.
- `ai/open-in.json` holds the "Open in" links for Claude, Claude Code, Codex, ChatGPT, Microsoft Copilot, Gemini, Perplexity, Grok, Le Chat and DeepSeek. Most prefill a prompt; Gemini and DeepSeek have no prompt link, so their entry carries the prompt in `copy` for the page to copy first. None of these assistants has a link that installs a skill directly.
- `ai/packages/` holds a zip per skill (an assistant's skill upload), both skills together, and a Microsoft 365 Copilot agent package.

### Change the skills or the packages

1. Edit the skill under `.agents/skills/<name>/`. Keep the front matter strict YAML: quote any value holding `: ` or ` #`.
2. Run `python3 ai/agents/build_agent_kits.py` and commit `ai/packages/`, `ai/open-in.json` and `skills-lock.json` with the change.
3. Run `node --run check` and `node --run test`.

A house sync that adds or removes a house skill also needs step 2, or `--check` fails on `skills-lock.json`.

### Release the media kit exports

- `.github/workflows/media-kit.yml` renders the catalogue, builds the template package and runs the website repository's `climb_brand_media_kit/scripts/build_kit.py` to make `climb-media-kit-exports.zip`, then attaches it to a new `media-kit-<date>-<commit>` release. It needs the `MEDIA_KIT_BUILDER_TOKEN` secret (read-only on the private website repository). The builder comes from the `builder-ref` input, default `production`; never default it to a feature branch, since merged branches are deleted.
- The photo library is read from `climb-photo-library.zip` on the `photo-library-1.0` release, which `photos/_build/photo_library.py publish --source <library>` uploads from the machine with the originals (it skips the upload when the fingerprint is unchanged, holds it while any photo is new until `--approve-new`, and then starts the media kit workflow; `install-timer` runs it hourly under systemd); an optional `media-kit-exclude.txt` on the same release (one `folder/filename` per line) is passed to the builder as `--photo-exclude`; without the zip the kit has no photo library. Never put a photo with a readable name badge or a possible minor in that zip.
- The 4K motion clips and drawing PNGs are not part of this build.

### Device rollout (intune/)

- `intune/` holds PowerShell 7 scripts that create Intune objects named `Climb - ...` through Microsoft Graph beta (`Invoke-MgGraphRequest` only, helpers in `intune/ClimbIntune.psm1`). Every script is idempotent by that name and takes `-WhatIf`. Scripts 10 to 13 fetch the `templates-v<version>` release, so a change to the installers reaches devices only after a new templates release. `50-Outlook-Default-Font.ps1` uses Exchange Online PowerShell, not Graph.
- Keep the folder public-safe: no tenant ids or domains, account names or internal security settings. Tenant-specific notes and audits stay outside the repository.

### Release the templates and motion clips

- `.github/workflows/release.yml` runs on its own on every push to main; never add a manual-only step to it.
- `templates` builds `Climb-Templates-<version>.zip` and publishes the `templates-v<version>` release from `templates/install/VERSION`. A published release is immutable, so a pull request that changes the package must bump `templates/install/VERSION`; the `templates version` check fails until it does.
- `motion` renders `climb-video-motion.zip` when `templates/_build/`, `generators/motifs.py`, `tokens/`, `logos/` or the fonts change, or when no motion release exists, and publishes a new `climb-video-motion-<date>-<commit>` release.
- Every release is created as a draft, uploaded, then published; never upload to a published release.
- The package carries `payload/defaults/<Brand>/` (`Normal.dotm`, `Blank.potx`, `Book.xltx`, `Default Theme.thmx`) from `templates/_build/defaults_build.py`. The per-person scripts `install/windows/Set-ClimbDefaultsUser.ps1` and `install/macos/set-climb-defaults.sh` copy one brand's set into each person's Office folders; the default brand is ClimbGroup. Rebuild the defaults after changing the letterhead, the deck or the themes, and never edit them by hand.
