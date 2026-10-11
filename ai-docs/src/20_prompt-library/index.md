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
