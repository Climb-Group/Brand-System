# Installing the Climb templates

This package installs the ClimbUK, ClimbGroup and Climb27 Word, Excel and PowerPoint templates, the Montserrat and Open Sans fonts, the Office themes, the LibreOffice templates and the video kit (DaVinci Resolve titles, the grade LUT, Premiere Pro sequences, stills and captions) on Windows, macOS and Linux. Use it by hand on one machine, or through Intune, Jamf or any other device manager.

```
payload/   the files: fonts, office/<Brand> (the External-* files are the co-branded versions for people outside the company), themes, libreoffice/<Brand>, video
windows/   Install, Uninstall, Detect and per-user scripts (PowerShell)
macos/     install and uninstall scripts, and build-pkg.sh to make a .pkg
linux/     install and uninstall scripts
VERSION    package version
```

The 4K motion clips (600 MB) are a separate download, `climb-video-motion.zip` on the newest `climb-video-motion-<date>-<commit>` release. Unzip them next to the video kit if you edit video.

## What ends up where

| | Windows | macOS | Linux |
| --- | --- | --- | --- |
| Fonts | `C:\Windows\Fonts` | `/Library/Fonts` | `/usr/local/share/fonts/climb` |
| Office templates | `C:\ProgramData\Climb\Templates\Office\<Brand>`, set as each person's Workgroup templates folder | `/Library/Application Support/Microsoft/Office365/User Content.localized/Templates.localized` | `/opt/climb-templates/Office` |
| Office themes | each person's `Document Themes` folder | `.../User Content.localized/Themes.localized` | `/opt/climb-templates/Themes` |
| ONLYOFFICE | `converter\templates\<language>\Climb` in its program folder | the same folder inside `ONLYOFFICE.app` | `/opt/onlyoffice/desktopeditors/converter/templates/<language>/Climb` |
| LibreOffice | `C:\ProgramData\Climb\Templates\LibreOffice` | `/Library/Application Support/Climb/Templates/LibreOffice` | linked into each person's LibreOffice template folder, one folder per brand |
| Resolve titles | `C:\ProgramData\Blackmagic Design\DaVinci Resolve\Fusion\Templates` | `/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Templates` | `~/.local/share/DaVinciResolve/Fusion/Templates` |
| LUT | Resolve `Support\LUT\Climb` and Premiere `Adobe\Common\LUTs\Creative` | Resolve `LUT/Climb` and Premiere `Adobe/Common/LUTs/Creative` | `/opt/resolve/LUT/Climb` |
| Brand defaults (Normal.dotm, Blank.potx, Book.xltx, Default Theme.thmx) | `C:\ProgramData\Climb\Templates\Defaults\<Brand>`, plus `Set-ClimbDefaultsUser.ps1` next to it | `/Library/Application Support/Climb/Templates/Defaults/<Brand>`, plus `set-climb-defaults.sh` next to it | not installed |
| Premiere sequences, stills, captions | `C:\ProgramData\Climb\Templates\Video` | `/Library/Application Support/Climb/Templates/Video` | `/opt/climb-templates/Video` |

The Resolve titles come with their logo PNGs, which go in `Fusion/Templates/Edit/Titles/<Brand>/` next to the titles: the Lower Third Festival and End Card load them from there, because Resolve cannot read images from inside a `.drfx`. The Resolve project and render presets are in `payload/video/resolve-presets/`; import them in Resolve (Project Settings and Deliver page, the ... menu, Import Preset).

## ONLYOFFICE

The installers add the Word, Excel and PowerPoint templates to the Templates list on the ONLYOFFICE Desktop Editors start screen (version 8.2 or later), in a folder per brand. ONLYOFFICE keeps that list inside its own program folder, so an ONLYOFFICE update can remove the templates. The installers put them back:

- Windows: a start-up task, `\Climb\Climb templates for ONLYOFFICE`, runs `Add-ClimbOnlyOffice.ps1 -Action Ensure`.
- macOS: a LaunchDaemon, `com.climb-uk.templates.onlyoffice`, runs `climb-onlyoffice.sh ensure` whenever `ONLYOFFICE.app` changes. On macOS 13 and later, writing inside another app needs App Management permission. If the log says the copy failed, give your mobile device management (MDM) agent App Management in a privacy (PPPC) profile, or have people use File, Open on the templates in `/Library/Application Support/Climb/Templates/Office`.
- Linux: deb and rpm upgrades leave the templates alone. The Snap and Flatpak builds are read-only, so people using those open the templates with File, Open from `/opt/climb-templates/Office`.

If ONLYOFFICE is installed after the templates, run the helper on its own, from the unzipped package or the install folder: `windows\Add-ClimbOnlyOffice.ps1` as admin (the start-up task also does this at the next restart), or `sudo ./macos/climb-onlyoffice.sh` or `sudo ./linux/climb-onlyoffice.sh`. To take them out again, add `remove` (macOS, Linux) or `-Action Remove` (Windows).

ONLYOFFICE uses the fonts installed by this package, so nothing else is needed.

## Other office apps

These apps open the `.dotx`, `.xltx` and `.potx` files but have no folder an installer can fill, so each person adds the templates once. The files are in the `Office` folder of the install (paths in the table above).

| App | How to add the templates |
| --- | --- |
| Collabora Office | Built on LibreOffice: File, Templates, Manage, Import, and pick the brand folder in the `LibreOffice` install folder. |
| WPS Office | Open a template file. WPS starts a new document from it. To keep it in WPS, use Save As and pick the WPS template file type. |
| SoftMaker Office and FreeOffice | Open a template file, then Save As in the TextMaker, PlanMaker or Presentations template format, into the template folder shown in Settings, Files. |
| Apple Pages, Numbers and Keynote | Open a template file, then File, Save as Template, Add to Template Chooser. If Keynote will not open the `.potx`, rename a copy to `.pptx` first. |
| Google Docs, Sheets and Slides | Upload the files to Drive and open them with Google Docs, Sheets or Slides. An admin can then add them to the organisation's template gallery (Template gallery, Submit template). Montserrat and Open Sans are Google Fonts, so the type comes through. |
| Microsoft 365 on the web and mobile | A SharePoint admin can upload the templates to an organisation assets library set up as an Office template library, so they show in Word, Excel and PowerPoint on every device. |

Skip the video files with `-SkipVideo` (Windows) or `--skip-video` (macOS, Linux).

Skip the fonts with `-SkipFonts` (Windows) or `--skip-fonts` (macOS, Linux) when your device manager installs Montserrat and Open Sans with a package of its own. The templates still use those fonts, so install them some other way first. With the option, the package leaves no copy of the fonts in its install folder, so its uninstaller leaves the fonts in place (on Linux, the uninstaller still removes `/usr/local/share/fonts/climb`). Both options default to off.

## Windows with Intune

1. Unzip the package. Wrap the whole folder with the Microsoft Win32 Content Prep Tool, with `windows\Install-ClimbTemplates.ps1` as the setup file:
   `IntuneWinAppUtil.exe -c <package folder> -s windows\Install-ClimbTemplates.ps1 -o <output folder>`
2. In Intune, Apps, Windows, Add, Windows app (Win32), and upload the `.intunewin`.
3. Program:
   - Install command: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\windows\Install-ClimbTemplates.ps1`
   - Uninstall command: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\windows\Uninstall-ClimbTemplates.ps1`
   - Install behaviour: System. Device restart behaviour: No specific action.
4. Requirements: 64-bit, Windows 10 1809 or later.
5. Detection rules: Use a custom detection script, `windows\Detect-ClimbTemplates.ps1`.
6. Assign to a device group.

The install runs as SYSTEM. It installs the fonts and files for the whole machine and registers an Active Setup step, so `Set-ClimbTemplatesUser.ps1` runs once for each person at their next sign-in. That step points Office's Workgroup templates folder at the brand templates (they show under File, New, in a Shared or Custom tab with a folder per brand) and copies the themes into the person's Document Themes folder. If someone already has a Workgroup templates folder, it is left alone and the templates are copied into their Custom Office Templates folder instead.

To see the templates straight away without signing out, run `Set-ClimbTemplatesUser.ps1` as the signed-in person, for example as an Intune platform script with "Run this script using the logged on credentials" set to Yes. If you already manage Office through the Settings Catalog, you can set "Workgroup templates path" (Microsoft Office 2016, Shared paths) to `C:\ProgramData\Climb\Templates\Office` instead.

The log is at `C:\ProgramData\Climb\Logs\install.log`.

## macOS with Jamf

Two ways, pick one:

- **Package (recommended).** On a Mac, unzip the package and run `macos/build-pkg.sh`. This makes `Climb-Templates-<version>.pkg`; set `SIGN_IDENTITY` to your Developer ID Installer certificate name to sign it. Upload it in Jamf Pro (Settings, Computer management, Packages) and add it to a policy (trigger Recurring Check-in or Enrollment Complete, frequency Once per computer, scoped to the computers you want). The pkg's postinstall runs the install script.
- **Script.** Host the unzipped package on a share or in a pkg of your own, and run `macos/install-climb-templates.sh` from a Jamf policy as root. Put `skip-video` in parameter 4 to leave out the video files. Put `skip-fonts` in another parameter (for example parameter 5) to leave out the fonts.

The templates show for every user under File, New from Template in Word, Excel and PowerPoint (Office 16.x or Microsoft 365). Quit and reopen Office after installing. To remove, run `/Library/Application Support/Climb/Templates/uninstall-climb-templates.sh` as root from a policy.

Other managers (Kandji, Mosyle, Intune for Mac) take the same `.pkg`.

## Linux

```
sudo ./linux/install-climb-templates.sh            # everyone on this machine
./linux/install-climb-templates.sh                 # just you, no sudo
```

As root it installs the fonts system-wide, puts everything in `/opt/climb-templates`, and links a folder per brand into the LibreOffice template folder of every person in `/home` and of new accounts (`/etc/skel`). Push it with Ansible, Salt, Puppet or Landscape by copying the unzipped package and running the script. The templates show in LibreOffice under File, New, Templates. To remove, run `/opt/climb-templates/uninstall-climb-templates.sh`.

## Make a brand the default

Installing the package adds the templates to File, New but leaves Office's blank files plain. A second, per-person step makes one brand the default, so:

- a new blank Word document opens on the brand letterhead (header, footer, legal line, page margins and styles, with an empty body),
- a new blank PowerPoint presentation uses the brand master and layouts (Windows) or the brand colours and fonts (Mac),
- a new blank Excel workbook uses the brand theme and Open Sans 11pt.

| | Windows | macOS |
| --- | --- | --- |
| Run | `Set-ClimbDefaultsUser.ps1 [-Brand ClimbGroup] [-Force]` as the signed-in person | `sudo set-climb-defaults.sh [--brand ClimbGroup] [--user NAME] [--force]`; it sets every person on the Mac |
| Word | `%APPDATA%\Microsoft\Templates\Normal.dotm` | `~/Library/Group Containers/UBF8T346G9.Office/User Content/Templates/Normal.dotm` |
| PowerPoint | `%APPDATA%\Microsoft\Templates\Blank.potx` | `.../User Content/Themes/Default Theme.thmx` |
| Excel | `%APPDATA%\Microsoft\Excel\XLSTART\Book.xltx` | `.../User Content/Startup/Excel/Book.xltx` |

Both scripts are in the install folder after installing (`C:\ProgramData\Climb\Templates` and `/Library/Application Support/Climb/Templates`). Options and defaults:

- **Brand**: `ClimbGroup` (default), `ClimbUK` or `Climb27`.
- **Force**: copy the files again even when this package version and brand are already set. Off by default.
- **User** (macOS only): set one person only. Default: everyone with a home folder in `/Users`.

Each person is set once per package version and brand, so a change they make to their own Normal template later stays until a new package version or another brand is rolled out. Their old `Normal.dotm` is kept the first time as `Normal-before-Climb.dotm`; to go back, delete `Normal.dotm` and rename the backup. Run either script every day from your device manager (an Intune remediation running as the user on Windows, a daily root script on macOS): people whose Word is open, or who have never opened Office on that Mac, are skipped and picked up on a later run.

Example, Windows, as the person: `powershell -NoProfile -ExecutionPolicy Bypass -File "C:\ProgramData\Climb\Templates\Set-ClimbDefaultsUser.ps1" -Brand ClimbGroup`

Common problems:

- **New documents still open plain**: Word was open when the script ran. Quit Word; the next run sets it, or run the script again now.
- **The letterhead is on every new document, including notes**: that is what the default does. Start notes from the Meeting notes template instead, or pick another brand with `-Brand`.
- **Someone lost their own macros or styles**: they were in their old `Normal.dotm`. Copy them from `Normal-before-Climb.dotm` with Word's Organizer (Developer, Document Template, Organizer).

The email compose font is a mailbox setting, not a file on the device, so it is set by the mail administrator for Outlook on the web and the new Outlook, not by this package.

## After installing

Open Word, File, New and check the brand folder is there, then start a document from the Report template and check the headings are in Montserrat. If they show in Arial or Calibri, the fonts did not install or the app was open during the install: restart the app, or sign out and back in.

## Tested

The Linux and macOS scripts, including the ONLYOFFICE step and `set-climb-defaults.sh`, were run against a test folder; `Add-ClimbOnlyOffice.ps1` was run under PowerShell 7 against a test folder; and every PowerShell script parses cleanly. The ONLYOFFICE template folder comes from the ONLYOFFICE Desktop Editors source code, not from a run in the app. The steps for the other office apps have not been tried. The default files were opened in LibreOffice (the letterhead `Normal.dotm` renders with its header and footer) but not yet in Microsoft Office. None of them has been run yet on a managed Windows PC, a Mac or a real Intune or Jamf tenant. Try them on one test device before you roll them out widely.
