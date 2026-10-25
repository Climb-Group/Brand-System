#!/bin/sh
# Turn library edits in the working tree into the one "Brand Centre edits" draft pull request.
#
#   GH_TOKEN=<bot token> BOT_NAME=<name> BOT_EMAIL=<email> sh tools/brand_centre/edits_pr.sh
#
# Run after `sync.py pull` on a checkout of main. The branch is rebuilt from main on every run with every
# edit not yet merged, so the pull request always shows the library as it is now. Nothing to commit: nothing
# changes, and an open pull request is left as it is.
set -eu

BRANCH="brand-centre/edits"
git add --all -- . ':!internal' ':!.brand-centre-sync'
if git diff --cached --quiet; then
  echo "No library edits to propose."
  exit 0
fi

count="$(git diff --cached --name-only | wc -l | tr -d ' ')"
files="$(git diff --cached --name-status | sed 's/^/    /')"
git -c user.name="$BOT_NAME" -c user.email="$BOT_EMAIL" commit --quiet --signoff \
  -m "feat(brand-centre): bring in edits made in the Brand Centre library" \
  -m "Files changed in the Brand System library since it last matched main ($count):

$files"
git push --quiet --force "https://x-access-token:${GH_TOKEN}@github.com/${GITHUB_REPOSITORY}.git" "HEAD:refs/heads/$BRANCH"

if [ -z "$(gh pr list --head "$BRANCH" --state open --json number --jq '.[].number')" ]; then
  gh pr create --draft --base main --head "$BRANCH" \
    --title "feat(brand-centre): bring in edits made in the Brand Centre library" \
    --body "## What changed and why

Edits people made in the Brand System library in the Brand Centre, brought into the repository by the Brand Centre sync. The commit lists every file. This pull request is rebuilt from main on each sync run while it stays open, so it always shows the library as it is now.

Merge it to accept the edits: main then goes back to the library. To drop them instead, close it and run the Brand Centre sync workflow with mode restore, which puts main back over the library.

## Evidence

The Brand Centre sync workflow run that made this commit.

## AI disclosure

AI level: unassisted
AI tools: none
Accountable human:
Human review:"
fi
echo "Library edits proposed: $count file(s)."
