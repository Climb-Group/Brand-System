---
name: openverse-search
description: Pointer to toosean's openverse skill (github.com/toosean/skills), which searches Openverse for openly licensed images and audio and returns each result's licence, creator, source and attribution text. It has no licence, so this repository holds no copy. Use when a task needs a Creative Commons or public domain image, illustration, sound or music track, or the licence and credit line for one. Gives the commit that was reviewed, how to run it for one session or install it for yourself, and the house rules on API keys, licences and brand photos. For sound effects and music on a video, use openverse-sfx instead.
license: Proprietary
metadata:
  owner: ClimbGroup marketing
  version: "1.0"
---
# Openverse search (pointer)

A pointer to toosean's `openverse` skill. It searches the Openverse API (`api.openverse.org`) for openly licensed images and audio and prints each result's licence, creator, source, links and attribution text.

**Posture: pointer only.** The skill has no licence, so this repository holds no copy of it. Use it from its own repository at the commit below, which was read in full before it was listed here: one Python script, standard library only, that calls nothing but `api.openverse.org`.

## The rules that bite hardest

1. **It needs Openverse API keys.** Put `OPENVERSE_CLIENT_ID` and `OPENVERSE_CLIENT_SECRET` in the environment of the one command that runs it, straight from your password manager. Never write them into a file in a repository. Without keys it stops; it never falls back to anonymous requests. `openverse-sfx` needs no keys for audio.
2. **Use the reviewed commit.** Pin `fd32ba523158fff27e7755f1926654b9595c2ea8`. Nobody here has read a newer commit; read its diff before you use it.
3. **Commercial licences for anything we publish.** Search with `--license-type commercial`, and `--license-type modification` when the image will be cropped or recoloured. Keep each result's attribution text with the file, and credit CC BY material where it appears.
4. **Brand photos come from the pack.** `climb-visual-style` asks for real, consented photos of actual attendees and no stock, so an Openverse photo of people never goes on a ClimbUK, ClimbGroup or Climb27 asset. Anything else from Openverse on a brand asset still has to pass that skill.

## How to use it

For one session, fetch the script into a new, empty folder and run it in Python's isolated mode, with the two keys set for that command only:

```bash
dir=$(mktemp -d)
curl -fsSL -o "$dir/openverse_search.py" \
  https://raw.githubusercontent.com/toosean/skills/fd32ba523158fff27e7755f1926654b9595c2ea8/openverse/scripts/openverse_search.py
python3 -I "$dir/openverse_search.py" search --media image --query "lantern" --license-type commercial --format markdown
python3 -I "$dir/openverse_search.py" detail --media image --id "<openverse-id>" --format markdown
python3 -I "$dir/openverse_search.py" related --media audio --id "<openverse-id>" --page-size 5
```

Useful filters: `--license cc0` for the fewest conditions; for images `--category photograph|illustration|digitized_artwork`, `--aspect-ratio square|tall|wide` and `--size large|medium|small`; for audio `--category sound_effect|music` and `--length shortest|short|medium|long`. Every parameter is in its `references/openverse-api.md`, at the same commit. Results default to JSON; `--format markdown` gives a short list.

To install it for yourself, in every project on your own machine only:

```bash
npx skills add toosean/skills#fd32ba523158fff27e7755f1926654b9595c2ea8 --skill openverse -g
```

Openverse issues the keys: register an application through its API (`/v1/auth_tokens/register/`, documented at <https://api.openverse.org/v1/>) and confirm the email it sends.

## Source

Repository <https://github.com/toosean/skills>, folder `openverse/`, reviewed at commit `fd32ba523158fff27e7755f1926654b9595c2ea8` (9 May 2026). No licence file: never copy its files into this or any other repository.

## Companions

- `openverse-sfx`: music and sound effects for a video from Openverse, with loudness checks and a credits file. No keys needed. Copied into this repository under its MIT licence.
- `climb-visual-style`: whether, and how, an image can go on a brand asset.

## Maintaining this skill

Keep it a pointer. To move the pin, read the upstream diff since the pinned commit, then change the commit everywhere it appears in this file. If the author adds an open licence, copy the skill in like the other community skills (see `COMMUNITY_SKILLS` in `ai/agents/build_agent_kits.py`) and retire this pointer.
