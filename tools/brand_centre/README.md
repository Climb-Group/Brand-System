# Brand Centre sync

Keeps the Brand System library in the Brand Centre SharePoint site and this repository in step. It runs on GitHub, so it doesn't depend on any computer being on. The library is where the team works. GitHub keeps the history, runs the checks and publishes the releases.

- **Library to GitHub.** At noon and midnight UK time, the `Brand Centre sync` workflow looks for files that were changed, added or deleted in the library since it last matched `main`. If it finds any, it commits them straight to `main` as the bot app, with one commit that lists every file. There's no pull request to review: the library is the source of truth. If a rule on `main` refuses the bot's push, the edits go to a draft pull request from `brand-centre/edits` instead, and the run shows a warning.
- **GitHub to library.** After every push to `main`, the workflow uploads the changed files to the library and removes the deleted ones. It commits any library edits first, so a push never overwrites an edit that isn't in git yet.
- **Internal material.** Team-only files live in a separate library that the sync's app registration cannot open. The sync also skips any `internal/` folder, and `.gitignore` keeps `internal/` out of the repository.

## How it decides what changed

After each upload, the workflow saves the hash SharePoint gives each file to `.brand-centre-sync/manifest.json` in the library, together with the commit the library matches. An edit is any file whose hash no longer matches the manifest, any file the manifest doesn't list, and any listed file that has gone. SharePoint adds its own metadata to HTML and Office files as it stores them, so their bytes never match the repository. Because the sync compares against SharePoint's own hashes, those files don't show up as false edits.

Leave the `.brand-centre-sync` folder alone. Files over 95 MB stay in the library and the run reports them, because GitHub refuses files over 100 MB. Use a release for large files instead.

## Run it by hand

In GitHub, open Actions, then Brand Centre sync, then Run workflow, and pick a mode:

| Mode | What it does |
| --- | --- |
| `pull` (default) | Commits library edits to `main`. |
| `push` | Commits library edits, then sends `main` to the library. |
| `restore` | Puts `main` back over every library edit that isn't in git yet, for example after the bot's push was refused and you closed the fallback pull request. |
| `status` | Lists the library edits and changes nothing. |

Locally, with rclone and the same `RCLONE_ONEDRIVE_*` variables: `python3 tools/brand_centre/sync.py status`. Set `BRAND_CENTRE_REMOTE` to use a named rclone remote instead, for example `BRAND_CENTRE_REMOTE=brand-system:`.

## Set it up once

Until `BRAND_CENTRE_CLIENT_ID` is set, the workflow skips every run.

1. In the Brand Centre site, create a document library named **Brand System**. Keep internal material in another library.
2. In Microsoft Entra, register an app named "Brand Centre sync".
   - Add the Microsoft Graph application permission `Lists.SelectedOperations.Selected` and grant admin consent.
   - Grant the app `write` on the Brand System library only: `POST /sites/{site-id}/lists/{list-id}/permissions` with `{"roles":["write"],"grantedTo":{"application":{"id":"<client id>","displayName":"Brand Centre sync"}}}`.
   - Create a client secret.
3. Find the library's drive ID: `GET /sites/{site-id}/lists/{list-id}/drive`.
4. In this repository's Settings, Secrets and variables, Actions, add:
   - the variables `BRAND_CENTRE_TENANT_ID`, `BRAND_CENTRE_CLIENT_ID` and `BRAND_CENTRE_DRIVE_ID`;
   - the secret `BRAND_CENTRE_CLIENT_SECRET`.
5. Run the workflow with mode `push`. The first run uploads the whole pack and saves the first manifest.

The workflow commits as the organisation's bot app (`RESNOVAS_BOT_APP_ID` and `RESNOVAS_BOT_PRIVATE_KEY`). If `main` has a branch rule or ruleset that requires pull requests, add the bot app to its bypass list, or every run falls back to a pull request. Because these commits don't go through a pull request, `check` runs on them after they land: a red run on `main` means a library edit broke a check, such as a new PDF with no copy file.

Optional: to sync as soon as a file changes instead of at noon and midnight, add a Power Automate flow on the library. Trigger it on "When a file is created or modified (properties only)", and have it send a `repository_dispatch` event of type `brand-centre-changed` to this repository.

## Common problems

- **The run fails with an access error from Graph.** The app has no grant on the library (step 2), or the drive ID belongs to another library (step 3).
- **Every file shows as an edit.** The manifest is missing, for example because someone deleted `.brand-centre-sync`. Run mode `push` to send `main` and save a fresh manifest. Every library file then counts as an edit and is committed first, so check the commit it makes.
- **Runs open a pull request instead of committing.** `main` refused the bot's push. Add the bot app to the bypass list of the rule on `main`.
- **An edit keeps coming back after its fallback pull request was closed.** The library still holds that edit. Run mode `restore`.
