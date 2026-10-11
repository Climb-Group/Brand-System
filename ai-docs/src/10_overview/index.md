## The ClimbUK brand pack

This repository is the ClimbUK brand: tokens, logos, illustrations, photography, guidelines, templates and two Agent Skills. It holds no website or platform code, and no TypeScript, so the house rules for Effect, Nx and feature flags have nothing to apply to here. The brand scripts are plain Python using the standard library.

### Use the brand from an agent

- Load `.agents/skills/climb-voice` for any words and `.agents/skills/climb-visual-style` for anything visual; both for an asset with words on it. Run `python3 .agents/skills/climb-voice/scripts/check_copy.py FILE` on every piece of copy.
- Every colour and size comes from `tokens/brand.tokens.json`. Never type a value that is not in it.
- `ai/tools/brand_rules.py` answers brand questions as tools (`call(tool, arguments, venue_announced)`); `ai/kit.json` lists them.

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

- `.github/workflows/media-kit.yml` renders the catalogue, builds the template package and runs the website repository's `climb_brand_media_kit/scripts/build_kit.py` to make `climb-media-kit-exports.zip`, then attaches it to a new `media-kit-<date>-<commit>` release. It needs the `MEDIA_KIT_BUILDER_TOKEN` secret (read-only on the private website repository).
- The photo library is read from `climb-photo-library.zip` on the `photo-library` release; an optional `media-kit-exclude.txt` on the same release (one `folder/filename` per line) is passed to the builder as `--photo-exclude`; without the zip the kit has no photo library. Never put a photo with a readable name badge or a possible minor in that zip.
- The 4K motion clips and drawing PNGs are not part of this build.
