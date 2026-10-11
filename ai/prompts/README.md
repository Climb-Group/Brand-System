# Prompt library

Ready-made prompts for ClimbUK, ClimbGroup and Climb27 work, for Microsoft 365 Copilot, Claude, Codex, Cursor, GitHub Copilot, Gemini and any other assistant. There is at least one set of prompts for every Copilot task type: Analyze, Ask, Assist, Catch up, Code, Create, Design, Edit, Execute, Find, Learn, Prepare, Schedule and Understand. Each prompt carries the brand rules it needs, so the answer comes back on brand even in an assistant that has never seen the brand pack.

The prompt files are the source. Every other file here is built from them, so the copies never drift apart.

## What is in it

| Path | What it is |
| --- | --- |
| `library/<task type>/<name>.md` | One prompt per file: front matter, then the prompt text. The source of truth. |
| `brand/voice.md`, `brand/visual.md` | The short brand rules added to the end of every prompt that needs them. |
| `build_prompts.py` | Checks every prompt and builds everything below. Standard library only. |
| `dist/copilot/climbuk-prompts.csv` | The Microsoft 365 Copilot organisational prompts import file. |
| `dist/PROMPTS.md` | The whole library as one page to read and copy from. |
| `dist/prompts.json` | The whole library as data, for any tool. |
| `dist/claude-code-commands.zip` | Slash commands for Claude Code (`.claude/commands/climb/`). |
| `dist/codex-prompts.zip` | Custom prompts for Codex (`prompts/`). |
| `dist/cursor-commands.zip` | Commands for Cursor (`.cursor/commands/`). |
| `dist/vscode-prompt-files.zip` | Prompt files for GitHub Copilot in VS Code (`.github/prompts/`). |
| `dist/gemini-cli-commands.zip` | Custom commands for Gemini CLI (`.gemini/commands/climb/`). |
| `../packages/climb-prompts.zip` | The library as an Agent Skill, one folder with `SKILL.md` inside, for Claude and other skill uploads. |
| `../packages/cowork/*.zip` | `climb-voice`, `climb-visual-style` and `climb-prompts` with `SKILL.md` at the top, for a Copilot Cowork skill upload. |
| `../packages/climbuk-brand-plugin-m365.zip` | A Copilot Cowork plugin with all three skills. |
| `../packages/climbuk-brand-plugin.zip` | A Claude plugin with all three skills and every prompt as a command. |

## A prompt file

Every field is required. The file name is the prompt's id, in kebab-case, and the file sits in the folder for its task type.

```markdown
---
title: Write a LinkedIn post
description: Writes a LinkedIn post for ClimbUK or Climb27, for one audience, with a clear next step and tagged link.
display: Write a ClimbUK LinkedIn post for one audience
task: Create
department: Marketing
apps: Copilot web, Copilot work
brand: voice
locale: en-GB
---

Write a LinkedIn post for ClimbUK about {{topic}}, for {{audience}}.

1. A first line that works like a festival poster headline.
2. Three to five short lines on what the reader gets.
3. One next step with a link placeholder [LINK with UTM tags].
```

| Field | What it is | Rules |
| --- | --- | --- |
| `title` | The name on the prompt card | 35 characters at most |
| `description` | What the prompt does. Copilot shows it to admins only. | 200 characters at most |
| `display` | The short line people see and pick | 132 characters at most, no placeholders |
| `task` | The task type | One of the 14 task types above, spelt as shown |
| `department` | Who it is mainly for | 120 characters at most |
| `apps` | Copilot surfaces it appears in | `Copilot work` (can use the person's emails, chats and files), `Copilot web`, or both separated by a comma |
| `brand` | Which brand rules to add | `voice`, `visual`, `both` or `none` |
| `locale` | The language it is written in | `en-GB` by default |

The prompt text is everything after the front matter, 8,000 characters at most including the brand rules. Write a placeholder as `{{lower_snake_case}}`. The builder turns it into each tool's own form: `[topic]` with `$ARGUMENTS` for Claude Code, `$TOPIC` for Codex, `${input:topic:topic}` for VS Code and `[topic]` with `{{args}}` for Gemini CLI.

The title, description, display prompt and department pass the climb-voice copy checker, so the words people see follow the brand too.

## Change or add a prompt

1. Edit or add a file under `library/<task type>/`.
2. Run `python3 ai/prompts/build_prompts.py`. It stops and lists the problem if a prompt breaks a rule.
3. Run `python3 -m unittest discover -s ai/tests`.
4. Commit the prompt file together with everything the builder wrote. CI runs `python3 ai/prompts/build_prompts.py --check` and fails while anything is out of date.

## Use the prompts

### Microsoft 365 Copilot (organisational prompts)

You need the AI Administrator or Search Editor role.

1. Go to the Microsoft 365 admin center, then Copilot, then Prompts.
2. Select Import prompts and upload `dist/copilot/climbuk-prompts.csv`.
3. Check the validation preview, then import and publish.
4. Pin up to four prompts as Suggested for everyone.

Published prompts appear in Copilot Chat and the prompt gallery after about three hours. A tenant holds up to 1,000 prompts and an import takes up to 100; when the library passes 100, the builder writes `climbuk-prompts-1.csv`, `climbuk-prompts-2.csv` and so on.

### Microsoft 365 Copilot Cowork (skills and plugins)

- A skill: in Cowork select +, then Customize, then Skills. Select the arrow next to Add, then Upload skill, and pick a zip from `../packages/cowork/`. Upload `climb-prompts.zip` for the prompt library and the other two for the brand voice and visual style.
- The plugin: on the Plugins tab select Upload plugin and pick `../packages/climbuk-brand-plugin-m365.zip`. It carries all three skills.
- Share either from its detail page with Share, then Specific users in your organization. Use Re-share after uploading a new version.

### Claude

- Claude apps: add `../packages/climb-prompts.zip` (with `climb-voice.zip` and `climb-visual-style.zip`) under Settings, Capabilities, Skills.
- Claude Code plugin: unzip `../packages/climbuk-brand-plugin.zip` into a folder named `climbuk-brand` and start Claude Code with `claude --plugin-dir ./climbuk-brand`. Run a prompt as `/climbuk-brand:linkedin-post` followed by your details.
- Claude Code commands only: unzip `dist/claude-code-commands.zip` in a project (or in your home folder for every project) and run `/linkedin-post` followed by your details.

### Codex

Unzip `dist/codex-prompts.zip` into `~/.codex`, so the files land in `~/.codex/prompts/`, then restart Codex. Run a prompt as `/prompts:climb-linkedin-post TOPIC="the agenda" AUDIENCE="founders"`.

### Cursor, VS Code and Gemini CLI

Unzip the matching zip at the top of a project:

- Cursor: `dist/cursor-commands.zip`, then type `/climb-linkedin-post` in chat.
- GitHub Copilot in VS Code: `dist/vscode-prompt-files.zip`, then type `/climb-linkedin-post` in Copilot Chat; it asks for each placeholder.
- Gemini CLI: `dist/gemini-cli-commands.zip` (or unzip into your home folder for every project), then run `/climb:linkedin-post` followed by your details.

### ChatGPT, Gemini, Perplexity and the rest

Copy a prompt from `dist/PROMPTS.md` and replace each `{{placeholder}}`. To keep the library to hand, add `dist/PROMPTS.md` as a file to a ChatGPT project or custom GPT, or to a Gem.

## Common problems

- **The Copilot import rejects a locale.** The supported locales are listed in the import flyout under View all supported locales. If `en-GB` is not there for your tenant, change `locale: en-GB` to `locale: en-US` in the prompt files and rebuild.
- **The Copilot import rejects the whole file.** Every row must use a supported task type and supported apps, and the columns must stay in Microsoft's order. Do not add columns such as `Last Updated` from an export.
- **Prompts do not show in Copilot.** Wait about three hours after publishing. People need a Microsoft 365 Copilot licence to see organisational prompts.
- **A `Copilot work` prompt finds nothing in Copilot web.** Copilot web has no access to emails, chats and files. Prompts that read them list `Copilot work` only.
- **A Cowork skill gets a number on its name.** A skill with the same name was already there. Delete the old one, or keep both.
- **The builder says a field is too long or breaks a copy rule.** Shorten it or reword it; the message names the file, the field and the rule.
