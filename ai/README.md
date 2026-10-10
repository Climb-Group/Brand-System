# AI kit

Skills, tools and an agent that let an AI assistant (for example the one built into the website platform) write, review and design with the ClimbUK brand. Everything here is generated from, or reads straight from, the rest of the pack: the skills in `.agents/skills/`, the guidelines, `logos/README.md` and `tokens/brand.tokens.json`. Change those, and the kit follows.

## What is in it

| Path | What it is |
| --- | --- |
| `kit.json` | The manifest: every tool (name, a short progress label to show while it runs, description, JSON schema for its arguments), every skill (name, when to use it, instructions file, tools it may call) and the agent. A platform integration reads this file and creates its own records from it. |
| `skills/*.md` | Instructions for each skill: Brand voice, Copy review, Visual style, Logos, Accessibility, Campaigns and channels. Short on purpose: they tell the assistant which tool to call for facts, so no value is copied into them. |
| `agents/brand-studio.md` | System prompt for the ClimbUK Brand Studio agent, which carries all six skills. |
| `tools/brand_rules.py` | The tools, in plain Python with no dependencies. `call(tool, arguments, venue_announced)` runs any tool in `kit.json` and returns a JSON-safe dict with `ok` and the answer or a `message`. |
| `tests/` | Unit tests for the tools and the manifest. |

## The tools

| Tool | What it answers | Reads |
| --- | --- | --- |
| `check_copy` | Problems, hints and reading level for a piece of copy | `climb-voice` copy checker |
| `check_colours` | WCAG 2.2 contrast of a pair, AA and AAA verdicts, whether both are tokens, the preset for that ground | tokens |
| `palette` | The five presets, the Dark, Light, AAA Dark and AAA Light themes, and the colour rules | tokens |
| `tokens` | Any token group: colour, type, space, radius, shadow, motion, layout, print, contrast | tokens |
| `logo` | The right logo master for a brand, ground, size and use, with its files and rules | `logos/README.md` |
| `surface` | Size, safe zone, preset and notes for a surface | `climb-visual-style` surfaces |
| `audience` | An audience's needs, tone, page and headline | `climb-voice` audiences |
| `channel` | A channel's job, shape, call to action and the UTM rule | `climb-voice` channels |
| `guide` | Sections of the skills and guidelines, by topic | skills, `guidelines/`, `accessibility/` |

The venue embargo is a platform setting passed as `venue_announced`. The assistant cannot lift it by sending an argument.

## Use it

```bash
python3 -c "import sys; sys.path.insert(0, 'ai/tools'); import brand_rules as b; print(b.call('logo', {'brand': 'Climb27', 'ground': 'orange'}))"
python3 -m unittest discover -s ai/tests
```

A platform integration copies `ai/` together with the files the tools read (`.agents/skills/`, `guidelines/`, `logos/README.md`, `tokens/brand.tokens.json`) into its own package, keeping the same relative paths, and calls `brand_rules.call()` from its tool hooks. A copy may rename `.agents` to `agents`. Set `CLIMB_BRAND_PACK`, or call `brand_rules.set_root()`, when the copy is not next to `brand_rules.py`.

## Change it

- Brand rules and values change in the skills, guidelines and tokens, not here.
- A new tool: add its function and an entry in `TOOLS` in `brand_rules.py`, its entry in `kit.json`, and a test.
- Every string argument in a tool schema has a `maxLength`.
- Text is ASCII only, with no em or en dashes.
