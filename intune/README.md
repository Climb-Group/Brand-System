# Climb branding through Intune

These scripts set up Intune so every company device gets the brand fonts, the Office templates, the brand wallpaper and a branded Company Portal. You run them yourself from PowerShell. Every script is safe to run more than once: it finds the objects it made before by their "Climb - " name and updates them instead of making copies. Every script also takes `-WhatIf`, which prints what it would change and changes nothing.

## What you need

- PowerShell 7.2 or later (`pwsh`). On Linux, install the `powershell` package.
- An Entra account with the Intune Administrator role (or Global Administrator) in your Microsoft 365 tenant.
- Network access to graph.microsoft.com, github.com, raw.githubusercontent.com and www.climb-uk.com.

`00-Prerequisites.ps1` installs the one module the scripts use (Microsoft.Graph.Authentication) for your user, signs you in and checks every permission. The sign-in asks for these Graph permissions: DeviceManagementConfiguration.ReadWrite.All, DeviceManagementScripts.ReadWrite.All, DeviceManagementApps.ReadWrite.All and Group.Read.All. The first time, approve them for the organisation.

## Run order

Run these one at a time, on separate days where it says so. Do not paste them as one block: the last step changes every device.

1. Sign in and install the modules. Add `-UseDeviceCode` if no browser opens.

   ```bash
   cd /path/to/brand-system/intune
   pwsh ./00-Prerequisites.ps1
   ```

2. Read the plan. Nothing changes in the tenant.

   ```bash
   pwsh ./Run-All.ps1 -WhatIf
   ```

3. Make an Entra security group called `Climb pilot devices` with a few of your own devices on each platform, then send everything to that group only. A script stops before creating anything when the group is missing.

   ```bash
   pwsh ./Run-All.ps1 -Target Group -GroupName 'Climb pilot devices'
   ```

4. The next day, check two or three pilot devices. Only then send it to every device:

   ```bash
   pwsh ./Run-All.ps1
   ```

Re-running a step is safe: each script updates its own "Climb - " policies by name. Running step 4 after step 3 moves the assignment from the pilot group to all devices. Company Portal branding (script 40) has no assignment, so it changes for everyone at step 3.

Add `-IncludeAndroid` to also set the Android wallpaper (see below). `-Brand ClimbGroup` or `-Brand Climb27` and `-Design ascent`, `connections` or `contours` change the wallpaper.

Before the first run, open Intune admin center > Devices > Scripts and remediations > Remediations once and confirm the Windows Enterprise licensing prompt. E5 includes it, but Intune will not run remediations until that is ticked.

## What each script does

| Script | Makes | Platforms | Notes |
| --- | --- | --- | --- |
| `10-Windows-Templates.ps1` | Remediation "Climb - Windows - Brand fonts and Office templates" | Windows 10 and 11 | Runs daily at 09:00. Downloads the latest templates release from GitHub, checks its SHA-256, installs fonts and Word, Excel and PowerPoint templates for every user. Re-runs only when a new release is out. |
| `11-macOS-Templates.ps1` | Shell script "Climb - macOS - Brand fonts and Office templates" | macOS | Same package, run as root daily. |
| `12-Windows-Office-Defaults.ps1` | Remediation "Climb - Windows - Office brand defaults" | Windows 10 and 11 | Runs daily at 12:30 as the signed-in person. New blank Word documents open on the letterhead; new decks and workbooks use the brand master, theme and Open Sans. `-Brand` ClimbGroup (default), ClimbUK or Climb27. Needs templates 1.3.0 or later from script 10. |
| `13-macOS-Office-Defaults.ps1` | Shell script "Climb - macOS - Office brand defaults" | macOS | Same, run as root daily for every person on the Mac. PowerPoint on Mac gets the brand colours and fonts as its default theme, not the full deck. Needs templates 1.3.0 or later from script 11. |
| `20-Windows-Wallpapers.ps1` | Settings catalog "Climb - Windows - Desktop and lock screen wallpaper" | Windows 10 and 11 | Desktop and lock screen from the brand centre. People cannot change it while the policy applies. `-LockScreenOnly` leaves the desktop free. |
| `21-macOS-Wallpaper.ps1` | Shell script "Climb - macOS - Download brand wallpaper" and profile "Climb - macOS - Desktop picture" | macOS | The script saves the picture; the profile sets it. `-DownloadOnly` saves it without forcing it. |
| `22-iOS-Wallpaper.ps1` | Device features "Climb - iOS - Wallpaper" | iPhone, iPad | Supervised devices only (Apple Business Manager). Personal phones show "not applicable". |
| `23-Android-Wallpaper.ps1` | Device restrictions "Climb - Android - Launcher wallpaper" | Android fully managed | Only through Microsoft Launcher, so it also needs Launcher deployed from Managed Google Play. Personal phones with a work profile cannot be given a wallpaper. Opt-in. |
| `30-iOS-Fonts.ps1` | Custom profiles "Climb - iOS - Brand fonts 1" to "4" | iPhone, iPad | Montserrat and Open Sans for the Office apps. Works without supervision. Android has no managed font install. |
| `40-CompanyPortal-Branding.ps1` | Updates the default Company Portal branding | All | Name ClimbGroup, colour #C55308, ClimbGroup logos, brand image. Pass `-ContactEmail`, `-ContactName` and `-WebsiteUrl` to fill the support details. |
| `60-OneDrive-Brand-Library.ps1` | Remediations "Climb - Windows - OneDrive sign-in" and "Climb - Windows - Brand library offline"; shell scripts "Climb - macOS - OneDrive" and "Climb - macOS - Brand library sync" | Windows 10 and 11, macOS | Syncs one SharePoint library (the brand centre) with OneDrive for everyone who can open it. See below. |
| `70-Claude-Tools.ps1` | Remediations "Climb - Windows - Claude app and Git" and "Climb - Windows - Claude Code and brand tools"; shell scripts "Climb - macOS - Claude app and Git" and "Climb - macOS - Claude Code and brand tools" | Windows 10 and 11, macOS | The Claude and ChatGPT (Codex) desktop apps, Claude Code, the Codex CLI, uv, Python 3.13, graphify, a daily-updated copy of the brand system, a local personal graph and an always-on graphify MCP server. See below. |

Every script except 40 and 50 takes `-Target AllDevices` (default), `AllUsers`, `Group` with `-GroupName`, or `None` (create it but assign nothing).

## Brand centre library in OneDrive

`60-OneDrive-Brand-Library.ps1` syncs one SharePoint document library to every device whose person can open it. Name the site and the library; the script reads the library ID from Microsoft Graph (it asks for the extra Sites.Read.All permission once):

```bash
pwsh ./60-OneDrive-Brand-Library.ps1 -SiteUrl https://contoso.sharepoint.com/sites/BrandCenter -LibraryName Documents -WhatIf
pwsh ./60-OneDrive-Brand-Library.ps1 -SiteUrl https://contoso.sharepoint.com/sites/BrandCenter -LibraryName Documents
```

Or pass `-LibraryId` (from the library's Sync > Copy library ID) with `-SiteTitle` and `-LibraryTitle`.

- **Windows**: OneDrive signs in with the Windows account, the library is added to its automatic sync (within 8 hours of the next sign-in), and once it has synced the whole folder is marked "Always keep on this device", so every file is on the laptop.
- **Mac**: the script installs OneDrive when it is missing and opens it at login. OneDrive on Mac has no setting that syncs a library automatically, so the daily script opens the library's sync link until it is synced; each person confirms it once. Mac also has no way to keep files offline by script: each person right-clicks the synced folder in Finder and picks Always Keep on This Device, once.
- People without access to the library get nothing; OneDrive skips it for them.

## Claude, Claude Code and the brand tools

`70-Claude-Tools.ps1` installs, on Windows and Mac:

- the Claude desktop app and the ChatGPT desktop app, which holds Codex, for every person (both update themselves),
- git (Git for Windows; the Apple Command Line Tools on Mac),
- for each signed-in person: Claude Code (updates itself), the Codex CLI (updated every day), uv, Python 3.13 as `python` and `python3`, and graphify,
- a copy of the brand system at `~/Climb/Brand-System` (Windows: `%USERPROFILE%\Climb\Brand-System`), pulled every day. The pull only fast-forwards; a copy with local edits is fetched and left alone. graphify is set up without git hooks so the copy stays clean.

```bash
pwsh ./70-Claude-Tools.ps1 -WhatIf
pwsh ./70-Claude-Tools.ps1
```

`-PythonVersion` (default 3.13) and `-RepoUrl` (default this repository) change what is installed. Logs: `/Library/Logs/Climb/claude-app.log` and `~/Library/Logs/Climb/claude-tools.log` on Mac; the remediation output in Intune on Windows. The person-level step waits until git is installed, so the first full run can take two days.

### Personal graph and graphify for agents

The same person-level step sets up graphify so agents can read the brand system and the person's own preferences together:

- **Personal preferences, local only.** `preferences.md` in the person's local app data folder (`~/.local/share/climb-preferences` on Mac, `%LOCALAPPDATA%\climb-preferences` on Windows). It never goes into git or a synced folder, so nobody needs a git account. The preferences tool proposed in pull request 35 adds to it; until then agents can edit the file directly.
- **One combined graph.** Every day the step rebuilds the personal graph and registers it with the brand system graph through `graphify global add`, as `personal-preferences` and `climb-brand-system`.
- **An always-on MCP server.** graphify serves the combined graph from login: a LaunchAgent (`com.climbgroup.graphify-mcp`) on Mac and a logon task (`Climb graphify MCP`) on Windows, restarted if it stops. It listens on `127.0.0.1` only, on port 8765 (`-McpPort` changes it), and every request needs the person's own key, made once and readable only by them (`~/.local/share/climb-graphify/mcp-key`, Windows `%LOCALAPPDATA%\climb-graphify\mcp-key`).
- **Claude Code** is registered with the server as `graphify-climb` for every project, and so is **Codex**: a marked block in `~/.codex/config.toml`, which the Codex CLI, the IDE extension and the ChatGPT desktop app all read. The script only replaces its own block; the rest of the file is left alone. **The Claude app** only runs local servers it starts itself, so it gets the same combined graph over stdio under the same name.

Check it on a device:

```bash
claude mcp get graphify-climb        # Status: Connected
codex mcp list                       # graphify-climb is listed
```

The server log on Mac is `~/Library/Logs/Climb/graphify-mcp.log`. If the port is taken by another program, re-run the script with another `-McpPort`.

## Default font in Outlook

`50-Outlook-Default-Font.ps1` is not an Intune script: the compose font in Outlook on the web and the new Outlook is a mailbox setting, so it uses Exchange Online PowerShell and an Exchange Administrator account. It sets Open Sans, size 2 (10pt) and Slate #4A5878 on every user mailbox, and installs the ExchangeOnlineManagement module for you if it is missing.

```bash
pwsh ./50-Outlook-Default-Font.ps1 -Identity you@climb-uk.com -WhatIf   # see the change for one mailbox
pwsh ./50-Outlook-Default-Font.ps1 -Identity you@climb-uk.com           # try it on yours
pwsh ./50-Outlook-Default-Font.ps1                                      # everyone
```

People can change their own font afterwards; re-run it after adding people. Classic Outlook for Mac and Windows keep their own font setting on the device and are not changed. Recipients without Open Sans installed see Arial.

## Templates in Office on the web and on phones

Intune puts the templates and the brand defaults on Windows and Mac. For the template picker in PowerPoint on the web and in the desktop apps across the organisation, use the SharePoint organisation assets library that the brand centre SharePoint kit already sets up (`templates/sharepoint/` in this repository). Word and Excel on the web and the mobile apps do not show organisation templates; people open them from the SharePoint library instead.

## Updating later

- New templates: publish a new templates release; Windows and Mac pick it up within a day. Pin one with `-TemplatesVersion 1.2.2`.
- New wallpaper: re-run 20 to 23 with another `-Design` or `-Brand`.
- Remove everything: delete the "Climb - " objects in the admin center. Installed fonts and templates stay on devices.

## How it was tested

- Every script parses in PowerShell 7.4 with no errors.
- 12 and 13 ran with `-WhatIf` and for real against the mock; `set-climb-defaults.sh` ran against a test folder (sets each person once, keeps their old Normal.dotm, skips people who never opened Office). The ClimbGroup letterhead Normal.dotm was opened in LibreOffice, not yet in Word. 50 parses but has not run against Exchange.
- Every script ran end to end, both with `-WhatIf` and for real, against a mock of the Graph module that records each call, so the bodies and assignment shapes were checked against the Graph beta reference. Nothing has run against the real tenant yet.
- The generated bash scripts pass `bash -n`; the generated Apple profiles parse as valid property lists. The iOS font profiles come to 837 KB, 829 KB, 489 KB and 488 KB, under the 1 MB limit.
- 70's generated Mac script ran end to end in a test home with git, Claude Code and graphify (launchctl and xcode-select stubbed): it built the personal graph, registered both graphs, wrote the key (mode 600), the LaunchAgent (a valid property list) and the Claude app entry, and registered Claude Code. Started as the LaunchAgent would, the server refused requests without the key (401), and `claude mcp get graphify-climb` reported Connected. A second run changed nothing, and an existing `~/.codex/config.toml` kept its own servers with the `graphify-climb` block added once (it parses as TOML). The Windows steps parse but have not run on Windows yet.
- The templates release the scripts expect (templates-v1.2.2, its zip name, layout and SHA-256) was checked on GitHub.
- Not tested: the brand centre manifest lookup on www.climb-uk.com was not reachable from the test machine, so the wallpaper scripts and script 40 were tested with explicit image URLs. The `-WhatIf` run on your machine will show whether each wallpaper URL resolves.

- 60 and 70 ran for real against the same mock; their generated bash scripts pass `bash -n` and their generated PowerShell parses. The Mac brand tools script ran in a test home with a local copy of this repository: it cloned, then on the next run fetched without touching the copy. Neither has run against the real tenant or a real device yet.

## Common problems

- **"Insufficient privileges"**: sign in with an Intune Administrator account and approve the permissions; re-run `00-Prerequisites.ps1`.
- **Remediation stays "Pending"**: confirm the licensing prompt (above); devices check in roughly every 8 hours.
- **"More than one object named ..."**: someone copied a Climb policy by hand; rename or delete the copy.
- **iOS wallpaper "not applicable"**: the device is not supervised. That is expected.
- **Wallpaper image too large**: pass a smaller `-Size`, another `-Design`, or a local `-ImagePath`.
