## Shared preferences and memory

Every agent session on ClimbUK work learns something: a brand rule, a team habit, or how one person likes to work. This section says where each kind goes so the next session, in any thread and on any host, starts with it.

### Three homes

| Kind | Example | Home | Who can read it |
| --- | --- | --- | --- |
| Brand | "Headlines open with a positive statement" | This pack: the skills, `guidelines/`, the copy checker (AGENTS.md rule 9) | Everyone; the pack is public |
| Team | "Odoo modules take every value from the theme" | Graphify Cloud memory, repository `Climb-Group/Brand-System`, tag `pref:team` | Workspace members |
| Personal | "Lead with the answer and keep replies short" | Graphify Cloud memory, same repository, tags `pref:personal` and `person:<github-login>` | Workspace members |

Private brand facts that must not be public (an unannounced venue, internal targets) are team memory, plus a rule in `private_rules.py` when the copy checker can catch them.

### Tags

Every saved preference carries:

- one kind tag: `pref:brand` (waiting to go into the pack), `pref:team` or `pref:personal`;
- `person:<github-login>` on a personal preference, and on any preference so its source is known;
- one domain tag: `voice`, `visual`, `odoo`, `tooling`, `devices` or `process`.

### At session start

1. `recall(repository_id="Climb-Group/Brand-System", query="preferences for <github-login>")` for the person you work for.
2. `recall(repository_id="Climb-Group/Brand-System", query="team preferences <domain>")` for the work in hand.
3. Load the brand skills. They already hold every brand decision; memory never overrides them.

### At closeout

Save each new preference as one statement with its date and source:

```text
remember(
  repository_id="Climb-Group/Brand-System",
  text="2026-10-14, example-user said: lead every reply with the answer and keep it short.",
  tags=["pref:personal", "person:example-user", "process"],
)
```

A brand preference goes into the pack in the same piece of work (rule 9); save it to memory as well only while the pull request is open, tagged `pref:brand`, so other sessions follow it before it merges.

### Promotion

- A personal preference two or more people state, or one a maintainer adopts for everyone, becomes `pref:team`: save the team version and say which personal notes it replaces.
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
