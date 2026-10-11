# AGENT-SETUP

Machine-only. People: `README.md`, `AGENTS.md`.

## Needs

- Node 24+ (`engines.node`) for the house tools, Python 3.10+ for the brand scripts. No dependencies, no install step, no services, no database.
- Pillow only to rebuild artwork (`generators/`, `logos/_build`, `--icons`), optional.
- `uv` only for the code graph (`sh tools/graphify/graphify setup`), optional.

## Env

- None required. No token for setup, build, test or check.

## Setup

- `scripts/agent-setup`. Idempotent. Steps: Node and Python check, `node --run setup` (editor surfaces, commit hook), `node --run check`.
- Success: last line `agent-setup: ok`. A few seconds.

## Run

| Job | Cmd |
| --- | --- |
| tokens | `python3 tokens/build_tokens.py` |
| agent kits, skill zips, open-in links | `node --run agent-kits` |
| media kit exports ZIP | Actions > media kit > Run workflow (needs `MEDIA_KIT_BUILDER_TOKEN`) |
| test | `node --run test` |
| all CI | `node --run check` |
| copy check | `python3 .agents/skills/climb-voice/scripts/check_copy.py FILE` |
| agent files | `node tools/dev/surfaces.mjs sync` after editing `.agents/` |

## Breaks

| Break | Cause | Fix |
| --- | --- | --- |
| `ai/packages ... out of date` | a brand skill or `ai/agents/` changed | `node --run agent-kits` |
| `skills-lock.json ... out of date` | a house sync added or removed a house skill | `node --run agent-kits` |
| `The house commit hook is not installed` | fresh clone | `node --run setup` |
| `LLMS.md is out of date` | `ai-docs/src` changed | `node --run ai-docs` |
