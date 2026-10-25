# Brand Centre sync

Brings edits made in the Brand System library in the Brand Centre SharePoint site into this repository. The library is the source of truth: the team works there, and the sync only pulls. It runs on GitHub, so it doesn't depend on any computer being on. GitHub keeps the history, runs the checks and publishes the releases.

- **Library to GitHub.** At noon and midnight UK time, the `Brand Centre sync` workflow looks for files that were changed, added or deleted in the library since its last run. If it finds any, it commits them straight to `main` as the bot app, with one commit that lists every file. There's no pull request to review. If a rule on `main` refuses the bot's push, the edits go to a draft pull request from `brand-centre/edits` instead, and the run shows a warning.
- **Nothing goes from GitHub to the library.** A change made on GitHub, such as a merged pull request, stays on GitHub. To change the pack, change it in the library. The one exception is `seed`, which you start by hand to fill a new or emptied library.
- **Internal material.** Team-only files and the internal tools that use and extend the brand system live in `internal` folders in the Brand System library, so everything stays in one place: one at the top, or one beside the part of the pack a tool extends (for example `templates/internal`). The sync never reads a folder named `internal` at any depth, `seed` never writes to one, and `.gitignore` keeps them out of the repository as well. Anyone who can open the library can open these folders, so keep the library team-only or give the `internal` folders their own permissions. Files `.gitignore` keeps out elsewhere, such as the private copy rules, also stay in the library.

## How it decides what changed

The workflow keeps the hash SharePoint gives each file in `.brand-centre-sync/manifest.json` in the library. An edit is any file whose hash no longer matches the manifest, any file the manifest doesn't list, and any listed file that has gone. Once a run's edits are on `main`, it saves the listing it compared as the new manifest, so the next run only finds newer edits. SharePoint adds its own metadata to HTML and Office files as it stores them, so their bytes never match the repository. Because the sync compares against SharePoint's own hashes, those files don't show up as false edits.

Leave the `.brand-centre-sync` folder alone. Files over 95 MB stay in the library and the run reports them, because GitHub refuses files over 100 MB. Use a release for large files instead.

## Run it by hand

In GitHub, open Actions, then Brand Centre sync, then Run workflow, and pick a mode:

| Mode | What it does |
| --- | --- |
| `pull` (default) | Commits library edits to `main`. |
| `status` | Lists the library edits and changes nothing. |
| `seed` | Commits library edits to `main`, then copies `main` into the library and saves a fresh manifest. Use it only for a new or emptied library, or after the manifest was deleted. It copies only the files the library lacks and never replaces one that is there. |

Locally, with rclone and the same `RCLONE_ONEDRIVE_*` variables: `python3 tools/brand_centre/sync.py status`. Set `BRAND_CENTRE_REMOTE` to use a named rclone remote instead, for example `BRAND_CENTRE_REMOTE=brand-system:`.

## Set it up once

Until `BRAND_CENTRE_CLIENT_ID` is set, the workflow skips every run.

1. In the Brand Centre site, create a document library named **Brand System**, with an `internal` folder at its top for team-only material.
2. In Microsoft Entra, register an app named "Brand Centre sync".
   - Add the Microsoft Graph application permission `Lists.SelectedOperations.Selected` and grant admin consent.
   - Grant the app `write` on the Brand System library only: `POST /sites/{site-id}/lists/{list-id}/permissions` with `{"roles":["write"],"grantedTo":{"application":{"id":"<client id>","displayName":"Brand Centre sync"}}}`. Write is needed for the manifest and for `seed`.
   - Create a client secret, and note its expiry date: the sync stops when it expires.
3. Find the library's drive ID: `GET /sites/{site-id}/lists/{list-id}/drive`.
4. In this repository's Settings, Secrets and variables, Actions, add:
   - the variables `BRAND_CENTRE_TENANT_ID`, `BRAND_CENTRE_CLIENT_ID` and `BRAND_CENTRE_DRIVE_ID`;
   - the secret `BRAND_CENTRE_CLIENT_SECRET`.
5. Run the workflow with mode `seed`. It copies the pack into the library and saves the first manifest.

The workflow commits as the organisation's bot app (`RESNOVAS_BOT_APP_ID` and `RESNOVAS_BOT_PRIVATE_KEY`). If `main` has a branch rule or ruleset that requires pull requests, add the bot app to its bypass list, or every run falls back to a pull request. Because these commits don't go through a pull request, `check` runs on them after they land: a red run on `main` means a library edit broke a check, such as a new PDF with no copy file.

Optional: to sync as soon as a file changes instead of at noon and midnight, add a Power Automate flow on the library. Trigger it on "When a file is created or modified (properties only)", and have it send a `repository_dispatch` event of type `brand-centre-changed` to this repository.

## Common problems

- **The run fails with an access error from Graph.** The app has no grant on the library (step 2), the drive ID belongs to another library (step 3), or the client secret has expired.
- **Every file shows as an edit.** The manifest is missing, for example because someone deleted `.brand-centre-sync`. Run mode `seed`. Every library file counts as an edit first and is committed to `main`, so check that commit.
- **Runs open a pull request instead of committing.** `main` refused the bot's push. Add the bot app to the bypass list of the rule on `main`.
- **A change merged on GitHub isn't in the library.** That is by design: the library is the source of truth. Make the change in the library too, or the next library edit to that file replaces it on `main`.
