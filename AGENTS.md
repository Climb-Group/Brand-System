# Agent guide

This is the ClimbUK brand pack: tokens, logos, illustrations, photography, guidelines, templates and the Agent Skills that teach agents the brand. It holds no website or platform code.

## Rules

1. **Load the skills.** Writing words: `.agents/skills/climb-voice`. Making anything visual: `.agents/skills/climb-visual-style`. Both, for an asset with words on it. Run the copy checker on every piece of copy you add.
2. **Tokens are the only source of values.** Never type a colour or size that is not in `tokens/brand.tokens.json`. After changing it, run `python3 tokens/build_tokens.py` and commit the generated files with it.
3. **Generated files are not edited by hand.** `tokens/tokens.css`, `tokens/_tokens.scss`, `illustrations/*.svg`, `illustrations/shapes/`, `logos/` PNGs and `components/hub/` come from scripts. Change the script and rebuild.
4. **Public documents are vendor agnostic.** `guidelines/`, `pdf/`, `web/` and `media-kit/` are read by partners, press and printers: no repository paths, internal tool names or internal notes.
5. **Accessibility.** WCAG 2.2 AA at least, AAA where it is small and easy. Every new colour pair goes in `pairs` so the build checks it.
6. **ASCII only** in text you write: no em or en dashes, no emoji. Use a hyphen-minus.
7. **Previews are real files.** Anything shown as a preview is committed here as a real file, and hub components stay live HTML and CSS.
8. **Commits and pull requests.** Conventional commit subjects (`feat(logos): ...`), one logical change each, signed off by the accountable human, with a `Co-authored-by` trailer for each AI tool that changed it. Open pull requests as drafts and disclose AI use in the template.

## Adding a deliverable

Put it in the folder the README names for it (`media-kit/`, `web/`, `pdf/`, `templates/`, `ai/`), with a README that says what it is, how to rebuild it and which tokens and skills it follows. Large binaries (video templates, archives over 50 MB) go in a release, not in the tree; commit the build script and a README that links the release.

## Checks

```bash
python3 tokens/build_tokens.py --check
python3 -m unittest discover -s tokens/tests
python3 .agents/skills/climb-voice/scripts/check_copy.py guidelines/voice.md
```
