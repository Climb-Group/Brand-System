#!/bin/sh
# Commit library edits in the working tree straight to main (Jonathan, 2026-10-25: no pull request, so the
# Brand Centre updates GitHub without anyone managing a review).
#
#   GH_TOKEN=<bot token> BOT_NAME=<name> BOT_EMAIL=<email> DEFAULT_BRANCH=main sh tools/brand_centre/edits_commit.sh
#
# Run after `sync.py pull` on a checkout of main. Once the edits are on main it runs `sync.py mark`, so the next
# run looks only for newer edits. If main's rules refuse the bot's push, the edits go to the brand-centre/edits
# branch and a draft pull request instead and are not marked, so the next run finds them again; the run says so.
set -eu

git add --all -- . ':!internal' ':!.brand-centre-sync'
if git diff --cached --quiet; then
  echo "No library edits to bring in."
  python3 tools/brand_centre/sync.py mark
  exit 0
fi

count="$(git diff --cached --name-only | wc -l | tr -d ' ')"
files="$(git diff --cached --name-status | sed 's/^/    /')"
git -c user.name="$BOT_NAME" -c user.email="$BOT_EMAIL" commit --quiet --signoff \
  -m "feat(brand-centre): bring in edits made in the Brand Centre library" \
  -m "Files changed in the Brand System library since it last matched main ($count):

$files"

remote="https://x-access-token:${GH_TOKEN}@github.com/${GITHUB_REPOSITORY}.git"
if git push --quiet "$remote" "HEAD:refs/heads/$DEFAULT_BRANCH"; then
  echo "Library edits committed to $DEFAULT_BRANCH: $count file(s)."
  python3 tools/brand_centre/sync.py mark
  exit 0
fi

echo "::warning::$DEFAULT_BRANCH refused the bot's push (a branch rule or a newer commit). The edits went to a draft pull request instead; let the bot app bypass the rule to commit straight to $DEFAULT_BRANCH."
git push --quiet --force "$remote" "HEAD:refs/heads/brand-centre/edits"
if [ -z "$(gh pr list --head brand-centre/edits --state open --json number --jq '.[].number')" ]; then
  gh pr create --draft --base "$DEFAULT_BRANCH" --head brand-centre/edits \
    --title "feat(brand-centre): bring in edits made in the Brand Centre library" \
    --body "## What changed and why

Edits people made in the Brand System library, which the Brand Centre sync could not commit straight to $DEFAULT_BRANCH. The commit lists every file. Merge it to accept them.

## Evidence

The Brand Centre sync workflow run that made this commit.

## AI disclosure

AI level: unassisted
AI tools: none
Accountable human:
Human review:"
fi
