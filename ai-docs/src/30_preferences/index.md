## Shared preferences and memory

Every agent session on ClimbUK work learns something: a brand rule, a team habit, or how one person likes to work. This section says where each kind goes so the next session, in any thread and on any host, starts with it.

### Three homes

| Kind | Example | Home | Who can read it |
| --- | --- | --- | --- |
| Brand | "Headlines open with a positive statement" | This pack: the skills, `guidelines/`, the copy checker (AGENTS.md rule 9) | Everyone; the pack is public |
| Team | "Odoo modules take every value from the theme" | Graphify Cloud memory, repository `Climb-Group/Brand-System`, tag `pref:team` | Workspace members |
| Personal | "Lead with the answer and keep replies short" | A Markdown file on the person's own machine, indexed by a local Graphify graph | That person only |

Private brand facts that must not be public (an unannounced venue, internal targets) are team memory, plus a rule in `private_rules.py` when the copy checker can catch them.

### Tags

Every team note in Graphify Cloud carries `pref:team`, or `pref:brand` while a brand rule waits in an open pull request, and one domain tag: `voice`, `visual`, `odoo`, `tooling`, `devices` or `process`. Personal preferences are not tagged: they never leave the person's machine.

### Personal preferences, local only

Nobody needs a git or GitHub account for these. `ai/preferences/preferences.py` keeps them in `preferences.md` in the local app data folder (`%LOCALAPPDATA%\climb-preferences`, or `$XDG_DATA_HOME/climb-preferences`, default `~/.local/share/climb-preferences`; `CLIMB_PREFERENCES_DIR` overrides it), one `## Topic` heading per subject and one dated line per preference.

```bash
python3 ai/preferences/preferences.py show
python3 ai/preferences/preferences.py add "reply style" "Lead with the answer and keep it short."
python3 ai/preferences/preferences.py query "reply style"
```

After each `add` (or `index`) it runs, through the house wrapper `tools/graphify/graphify`:

1. `graphify update <folder>`: a local graph of the file, with no model.
2. `graphify global add <folder>/graphify-out/graph.json --as personal-preferences`.
3. `graphify global add graphify-out/graph.json --as climb-brand-system`.

The wrapper points Graphify's home at the user's own state folder, so the global graph (`sh tools/graphify/graphify -- global path`) holds only that person's graphs on that machine. `query` runs `graphify query` on it, so one question reaches the brand pack and the person's preferences together. This script is the only sanctioned use of `graphify global add` here; never register a graph in a shared location.

In a cloud session the file does not exist. Use the host's own memory for that person if it has one, never git, and say so.

### At session start

1. `python3 ai/preferences/preferences.py show` on the person's machine.
2. `recall(repository_id="Climb-Group/Brand-System", query="team preferences <domain>")` for the work in hand.
3. Load the brand skills. They already hold every brand decision; memory never overrides them.

### At closeout

Save each new preference in its home as one dated statement:

```text
python3 ai/preferences/preferences.py add "reply style" "Lead every reply with the answer."

remember(
  repository_id="Climb-Group/Brand-System",
  text="2026-10-14, team decision: Odoo modules take every value from the theme.",
  tags=["pref:team", "odoo"],
)
```

A brand preference goes into the pack in the same piece of work (rule 9); save it to memory as well only while the pull request is open, tagged `pref:brand`, so other sessions follow it before it merges.

### Promotion

- A personal preference two or more people state, or one a maintainer adopts for everyone, becomes `pref:team`: save the team version in words that name no one unless it matters.
- A team or personal preference about how the brand looks, sounds or is named goes into the pack.
- Saving is intake: a workspace member accepts each note under Memory, Needs review. Until then it shows only in `recall` with `profile="audit"`.

### Which wins

1. `AI_POLICY.md` and the house rules.
2. The brand pack.
3. Team memory.
4. Personal memory, which changes only how the agent works with that person, never what the brand says or looks like.

### Never store

Secrets, credentials, contact details, home addresses, health or other sensitive personal details, customer data, or a quote that names a person in the public tree. A personal preference is about working style only.

### When the memory is not there

When Graphify Cloud is not connected, or `list_repositories` does not list `Climb-Group/Brand-System`, use the host's own project memory with the same tags and say so in the final message.
