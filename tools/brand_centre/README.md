# Brand Centre sync

Brings the Brand System library in the Brand Centre SharePoint site into this repository. It runs on GitHub, so it doesn't depend on any computer being on. The library is the source of truth and where the team works. GitHub only pulls from it, and keeps the history, runs the checks and publishes the releases.

- **Library to GitHub.** At noon and midnight UK time, the `Brand Centre sync` workflow looks for files that were changed, added or deleted in the library since it last matched `main`. If it finds any, it commits them straight to `main` as the bot app, with one commit that lists every file. There's no pull request to review: the library is the source of truth. If a rule on `main` refuses the bot's push, the edits go to a draft pull request from `brand-centre/edits` instead, and the run shows a warning.
- **Nothing goes from GitHub to the library.** Merging to `main` never changes the library, so nothing on GitHub can overwrite the team's work. A change made only on GitHub stays on GitHub; to make it part of the pack, make it in the library too. If the library later changes the same file, the library's version wins.
- **Internal material.** Team-only files live in a separate library that the sync's app registration cannot open. The sync also skips any `internal/` folder, and `.gitignore` keeps `internal/` out of the repository.

## How it decides what changed

`.brand-centre-sync/manifest.json` in the library holds the hash SharePoint gives each file, as `main` last took it, with that commit. The first upload saved it, and each pull whose edits reach `main` saves it again. This is the only thing the sync writes to the library. An edit is any file whose hash no longer matches the manifest, any file the manifest doesn't list, and any listed file that has gone. SharePoint adds its own metadata to HTML and Office files as it stores them, so their bytes never match the repository. Because the sync compares against SharePoint's own hashes, those files don't show up as false edits.

Leave the `.brand-centre-sync` folder alone. Files over 95 MB stay in the library and the run reports them, because GitHub refuses files over 100 MB. Use a release for large files instead.

## Run it by hand

In GitHub, open Actions, then Brand Centre sync, then Run workflow, and pick a mode:

| Mode | What it does |
| --- | --- |
| `pull` (default) | Commits library edits to `main`. |
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
5. Seed the library once, by hand: `python3 tools/brand_centre/sync.py push` with the `RCLONE_ONEDRIVE_*` variables set. It uploads the whole pack and saves the first manifest. (This was done on 2026-10-25.)

The workflow commits as the organisation's bot app (`RESNOVAS_BOT_APP_ID` and `RESNOVAS_BOT_PRIVATE_KEY`). If `main` has a branch rule or ruleset that requires pull requests, add the bot app to its bypass list, or every run falls back to a pull request. Because these commits don't go through a pull request, `check` runs on them after they land: a red run on `main` means a library edit broke a check, such as a new PDF with no copy file.

Optional: to sync as soon as a file changes instead of at noon and midnight, add a Power Automate flow on the library. Trigger it on "When a file is created or modified (properties only)", and have it send a `repository_dispatch` event of type `brand-centre-changed` to this repository.

## Common problems

- **The run fails with an access error from Graph.** The app has no grant on the library (step 2), or the drive ID belongs to another library (step 3).
- **The run says there is no manifest.** Someone deleted `.brand-centre-sync`. Pulls stop until it is rebuilt: commit the library's current files to `main` by hand, then save a fresh manifest with `sync.py mark`.
- **Runs open a pull request instead of committing.** `main` refused the bot's push. Add the bot app to the bypass list of the rule on `main`.
- **An edit keeps coming back after its fallback pull request was closed.** The library still holds that edit, and the library is the source of truth: undo it in the library.
