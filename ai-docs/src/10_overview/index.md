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
- Every file in the pack (PDF, deck, spreadsheet, document, image, logo) is covered by one copy file: its `output:` line lists paths or globs from the pack root (`pdf/flyers/segments/climb27_flyer_investors_a5.pdf pdf/flyers/segments/svg/climb27_flyer_investors_a5_*.svg`), `files:` adds globs from its own folder, and a wordless image gets an `@alt` section. `python3 .agents/skills/climb-voice/scripts/copy_md.py coverage` lists every file no copy file covers; the tests fail while it lists any.
- Artwork also ships as a layered SVG beside the finished PDF or PNG, grouped by row and block (`back > reasons > reason-1 > icon, title, text`), with group `id` and `inkscape:label` from the copy file's section names and live text, so it opens in Inkscape and Affinity (`climb-visual-style`, "Editable sources"). In a print build, tag each element with `data-layer="back/reasons/reason-1/title"` and `data-copy="back.reason"`, load `tools/svg/layered_svg.js` in the page and call `layeredSVG()`, then pass the result to `layered_svg.finish(raw, out, pack)` from `tools/svg/layered_svg.py`, which links pack photos with their crop and fades and embeds generated textures. The flyer builds do this through `write_svgs(jobs, pack)` in `pdf/flyers/_build/build.py`.

### Internal material

- Team-only material goes in `internal/`: `.gitignore` ignores `/internal/*` except `internal/README.md`, so nothing else there is ever committed or pushed. Check a path with `git check-ignore -v internal/<file>`.
- The pack's checks read only files git tracks (`git ls-files --cached --others --exclude-standard`), so `copy_md.py coverage`, `tools/check_dashes.py` and the tests skip internal files. `ai/tests/test_internal_folder.py` fails if the ignore rule stops covering the folder.
- The team's computers copy `internal/` into the brand centre library alongside the rest of the pack; nothing in the repository uploads it.

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

- `intune/` holds PowerShell 7 scripts that create Intune objects named `Climb - ...` through Microsoft Graph beta (`Invoke-MgGraphRequest` only, helpers in `intune/ClimbIntune.psm1`). Every script is idempotent by that name and takes `-WhatIf`. Scripts 10 to 13 fetch the `templates-v<version>` release, so a change to the installers reaches devices only after a new templates release. `50-Outlook-Default-Font.ps1` uses Exchange Online PowerShell, not Graph. `60-OneDrive-Brand-Library.ps1` resolves a SharePoint library ID through Graph v1.0 (`Connect-ClimbGraph -ExtraScopes Sites.Read.All`) and writes OneDrive's `TenantAutoMount` policy on Windows; macOS has no auto-mount policy, so its user script opens the library's `odopen://sync` link. `70-Claude-Tools.ps1` installs the Claude app, the ChatGPT desktop app (Codex), git, Claude Code, the Codex CLI, uv, Python and graphify and keeps a fast-forward-only clone of this repository at `~/Climb/Brand-System`, with graphify set up `--no-hooks` so the clone never goes dirty. It also registers a local-only personal preferences graph next to the brand system graph (`graphify global add ... --as personal-preferences` and `--as climb-brand-system`) and runs `graphify-mcp --transport http --host 127.0.0.1` over the combined graph from login (LaunchAgent `com.climbgroup.graphify-mcp`, Windows task `Climb graphify MCP`), with a per-person key; Claude Code reaches it as the user-scope server `graphify-climb`, Codex through a marked `[mcp_servers.graphify-climb]` block in `~/.codex/config.toml` (shared by the Codex CLI, IDE extension and desktop app), and the Claude app gets the same graph over stdio. Every run links `climb-voice`, `climb-visual-style`, `climb-odoo-pages`, `graphify` and `graphify-vendor` from the clone into `~/.claude/skills` and `~/.agents/skills` (leaving a real folder of the same name alone) and rewrites only the `<!-- climb:brand:begin -->` to `<!-- climb:brand:end -->` section of `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`; its text is `$brandNote` in the script.
- Keep the folder public-safe: no tenant ids or domains, account names or internal security settings. Tenant-specific notes and audits stay outside the repository.

### Release the templates and motion clips

- `.github/workflows/release.yml` runs on its own on every push to main; never add a manual-only step to it.
- `templates` builds `Climb-Templates-<version>.zip` and publishes the `templates-v<version>` release from `templates/install/VERSION`. A published release is immutable, so a pull request that changes the package must bump `templates/install/VERSION`; the `templates version` check fails until it does.
- `motion` renders `climb-video-motion.zip` when `templates/_build/`, `generators/motifs.py`, `tokens/`, `logos/` or the fonts change, or when no motion release exists, and publishes a new `climb-video-motion-<date>-<commit>` release.
- Every release is created as a draft, uploaded, then published; never upload to a published release.
- The package carries `payload/defaults/<Brand>/` (`Normal.dotm`, `Blank.potx`, `Book.xltx`, `Default Theme.thmx`) from `templates/_build/defaults_build.py`. The per-person scripts `install/windows/Set-ClimbDefaultsUser.ps1` and `install/macos/set-climb-defaults.sh` copy one brand's set into each person's Office folders; the default brand is ClimbGroup. Rebuild the defaults after changing the letterhead, the deck or the themes, and never edit them by hand.
