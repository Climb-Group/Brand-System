<!--
  Generated from ai-docs/src by tools/ai-docs/docgen.mjs. Do not edit by hand:
  edit the sources and run `node tools/ai-docs/docgen.mjs`.
-->

# climbuk-brand-pack for agents

Guidance for an AI agent working on or with this repository, assembled into one
file so it can be read in a single pass. Each example is a real file under
`ai-docs/src`, kept compiling by the repository type check. The people-facing
documentation covers the same ground in plain words; see the README.

---

## House standards

Every ClimbGroup repository follows the same standards. This section is synced from
[`Resnovas/.github`](https://github.com/Resnovas/.github); the rules come from
`AGENTS.md`, `CONTRIBUTING.md`, `AI_POLICY.md` and the PostHog skill
`coding-preferences`, and those documents win if this summary ever disagrees
with them. The sections after this one describe this repository itself.

### Code

- **Effect-TS v3 first.** TypeScript is the primary language, written with
  Effect v3: services as `Context.Tag` with `Layer`s, `Effect.gen` for
  sequencing, `Schema` to decode anything from outside the process. Load the
  PostHog skill `coding-preferences` and its `effect` reference before writing
  Effect code, and look up current APIs with Context7 rather than from memory.
- **Strict TypeScript, never `any`.** Keep `strict` on. Decode unknown input
  with `Schema` instead of casting it.
- **Typed errors.** Model failures as tagged errors (`Data.TaggedError` or
  `Schema.TaggedError`) in the error channel, so a caller sees every way a call
  can fail. Do not throw for expected failures.
- **Secrets through `Config` and `Redacted`.** Read configuration with
  Effect `Config`, and hold every secret as `Redacted` (`Config.redacted`)
  until the boundary that needs its value. Never put a secret in source, logs,
  telemetry, command-line arguments, issues or pull requests.
- **PostHog telemetry and feature flags.** Every app ships PostHog feature
  flags; new behaviour goes behind a flag with a safe default in code, never
  behind an environment variable or configuration toggle (house skill
  `feature-flags`). Telemetry events carry no secret or personal data.
- **Module boundaries.** The core package holds domain-agnostic building
  blocks only. Vendor SDKs and API clients live in
  `@climbgroup/integrations.<vendor>`. Features depend on core and
  integrations, never the other way round (`AI_POLICY.md` AI-13).
- **Comments explain why.** Constraints, trade-offs and anything surprising;
  never a restatement of the code.

### Tests

- Write tests with `@effect/vitest`. Line and branch coverage never falls
  below 90%, and most repositories hold 100%.
- **Never delete, skip or weaken a test** to make a change pass: fix the code
  (`AI_POLICY.md` AI-11). A flaky test is a bug to fix, not to retry away.
- Every bug fix comes with a regression test that fails before the fix.

### TypeScript

- Effect-TS v3 is the foundation of all production TypeScript, in every
  repository (house skill `coding-preferences`, `references/effect.md`).
  Anything that does IO, can fail, reads configuration, retries, runs
  concurrently or holds a resource is an `Effect` with `Data.TaggedError`
  failures, services as `Context.Tag` classes behind a `Layer`, input through
  `Schema`, configuration through `Config`, tests with `@effect/vitest`, in
  the shape of the module's existing code.
- Raw Promise code (`async`, `await`, `try`/`catch`, `throw`, `new Promise`,
  `.then`) lives only at a vendor boundary inside an integration module, in
  the one `Effect.tryPromise` or `Effect.try` that wraps the vendor call,
  marked with `// effect-boundary: <reason>` on the line above. The commit
  hook refuses it anywhere else in added source lines, and refuses `any`.
- A pure function with no IO and no failure path stays plain TypeScript. A
  whole feature in plain TypeScript is never an agent's decision: it is a
  house-rule override only the accountable human gives, by naming the rule.

### Files

- Every source file carries the FCL-1.0-MIT licence header from
  `tools/license/header.txt`, with its own path on the second line and the
  current year. `node tools/license/check-headers.mjs` (the `headers` package
  script) verifies it and `--fix` writes it; synced house tools carry none.
- ASCII hyphen-minus only in text an agent writes: no em or en dashes, and no
  emoji in titles or descriptions (house skill `no-em-or-en-dashes`,
  `AI_POLICY.md` AI-09).

### Commits and pull requests

- Conventional commits (`type(scope): summary`, imperative mood), one logical
  change each, and every commit signed off for the Developer Certificate of
  Origin with the commit author's name and address. An AI tool never signs off
  (`AI_POLICY.md` AI-03).
- Every commit an AI tool materially changed carries one `Co-authored-by`
  trailer per tool naming the tool and the model at the tool's attribution
  address (`AI_POLICY.md` AI-02); the commit author and the sign-off are the
  accountable human. No "Generated with" footer, robot emoji or host session
  line (house skill `commits-and-rd-evidence`). `tools/dev/commit-check.mjs`,
  installed as the commit-msg hook by setup, refuses a commit that breaks
  these rules.
- A pull request an agent opens is a draft (`AI_POLICY.md` AI-20) and states
  `AI level: autonomous` and every tool and model used (AI-01); the
  accountable human fills in `Accountable human` and `Human review` when
  marking it ready (AI-21). No "Generated with" footer or session link.
- One pull request per batch of work: one stacked branch per issue, each
  squashed to one conventional, signed-off commit naming its issue, all opened
  as a single pull request. Once a maintainer approves it, it lands as an owner
  fast-forward (its signed commits pushed onto the default branch unchanged),
  so each issue keeps its own commit; the merge queue squashes, because GitHub
  cannot sign rebased commits. Run the full gate locally first; CI is not the
  debugger.
- Deterministic gates (the repository's checks and the `smartcloud` check)
  decide a merge. AI review bots are advisory.
- Releases are cut by the synced house release workflow from `release.config.json`
  at the repository root (what the repository ships: bundles, apps, the major
  tag, error tracking project, npm package); the tools under `tools/release/`
  are synced too. The workflow runs on every push to the default branch and
  releases when the conventional commits call for it (before the first stable
  `v*` tag, the `firstRelease` version); never add a release that needs
  starting by hand. Never run `nx release` without `--dry-run`; the workflow
  is the only release path.

### Document everything twice

Every change to a feature, option, preset or workflow updates both kinds of
documentation in the same commit:

- **ELI5 docs for people.** Plain words and short sentences; what it is and why
  you would want it before how; step-by-step setup; one complete example; what
  you will see when it runs; every option with its default; common problems
  and their fixes.
- **ai-docs for agents.** The sections under `ai-docs/src`, with compiling
  examples in the codebase's own style. `LLMS.md` is generated from them by
  `node tools/ai-docs/docgen.mjs` and checked in CI with `--check`; never edit
  it by hand.

---

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

---

## The prompt library

`ai/prompts/` is a library of ready-made prompts for ClimbUK work, compiled for Microsoft 365 Copilot, Copilot Cowork, Claude, Codex, Cursor, VS Code and Gemini CLI.

### Where things live

- Source: one Markdown file per prompt in `ai/prompts/library/<task type>/<id>.md`, with front matter `title`, `description`, `display`, `task`, `department`, `apps`, `brand` and `locale`, then the prompt text. Placeholders are `{{lower_snake_case}}`.
- Brand rules: `ai/prompts/brand/voice.md` and `visual.md`, appended to a prompt's text when its `brand` is `voice`, `visual` or `both`.
- Builder: `python3 ai/prompts/build_prompts.py` validates every prompt (Microsoft's field limits and task types, the climb-voice copy checker on the visible fields, coverage of all 14 task types) and writes `ai/prompts/dist/` and the plugin and skill zips in `ai/packages/`. `--check` fails on a broken prompt or a stale output; CI runs it.

### Add a prompt

1. Copy a file in the same task type folder and change it. The file name must be unique across the library.
2. Run `python3 ai/prompts/build_prompts.py`, then `python3 -m unittest discover -s ai/tests`.
3. Commit the prompt with every file the builder wrote.

```python
import sys
sys.path.insert(0, "ai/prompts")
import build_prompts as bp

prompts = bp.load()
assert bp.validate(prompts) == []
print(bp.prompt_text(next(p for p in prompts if p["slug"] == "linkedin-post")))
```

### Rules the builder enforces

- Task type is one of Analyze, Ask, Assist, Catch up, Code, Create, Design, Edit, Execute, Find, Learn, Prepare, Schedule, Understand; `apps` uses only `Copilot web` and `Copilot work`.
- Title 35, display prompt 132, description 200, department 120 and full prompt text 8,000 characters at most; no placeholders in the title or display prompt.
- The Copilot CSV keeps Microsoft's columns and order and a UTF-8 byte order mark, and splits at 100 prompts per file.
- Cowork skill uploads have `SKILL.md` at the zip root; the Cowork plugin uses app manifest 1.28 with one `agentSkills` folder per skill, each folder named after its skill.
- The confidential copy rules (`private_rules.py`) never go into a package.
- After changing `climb-voice` or `climb-visual-style`, rebuild both `ai/agents/build_agent_kits.py` and `ai/prompts/build_prompts.py`.
