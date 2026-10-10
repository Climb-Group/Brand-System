# Installing the Climb templates

This package installs the ClimbUK, ClimbGroup and Climb27 Word, Excel and PowerPoint templates, the Montserrat and Open Sans fonts, the Office themes, the LibreOffice templates and the video kit (DaVinci Resolve titles, the grade LUT, Premiere Pro sequences, stills and captions) on Windows, macOS and Linux. Use it by hand on one machine, or through Intune, Jamf or any other device manager.

```
payload/   the files: fonts, office/<Brand>, themes, libreoffice/<Brand>, video
windows/   Install, Uninstall, Detect and per-user scripts (PowerShell)
macos/     install and uninstall scripts, and build-pkg.sh to make a .pkg
linux/     install and uninstall scripts
VERSION    package version
```

The 4K motion clips (600 MB) are a separate download, `climb-video-motion-v1.zip`. Unzip them next to the video kit if you edit video.

## What ends up where

| | Windows | macOS | Linux |
| --- | --- | --- | --- |
| Fonts | `C:\Windows\Fonts` | `/Library/Fonts` | `/usr/local/share/fonts/climb` |
| Office templates | `C:\ProgramData\Climb\Templates\Office\<Brand>`, set as each person's Workgroup templates folder | `/Library/Application Support/Microsoft/Office365/User Content.localized/Templates.localized` | `/opt/climb-templates/Office` |
| Office themes | each person's `Document Themes` folder | `.../User Content.localized/Themes.localized` | `/opt/climb-templates/Themes` |
| LibreOffice | `C:\ProgramData\Climb\Templates\LibreOffice` | `/Library/Application Support/Climb/Templates/LibreOffice` | linked into each person's LibreOffice template folder, one folder per brand |
| Resolve titles | `C:\ProgramData\Blackmagic Design\DaVinci Resolve\Fusion\Templates` | `/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Templates` | `~/.local/share/DaVinciResolve/Fusion/Templates` |
| LUT | Resolve `Support\LUT\Climb` and Premiere `Adobe\Common\LUTs\Creative` | Resolve `LUT/Climb` and Premiere `Adobe/Common/LUTs/Creative` | `/opt/resolve/LUT/Climb` |
| Premiere sequences, stills, captions | `C:\ProgramData\Climb\Templates\Video` | `/Library/Application Support/Climb/Templates/Video` | `/opt/climb-templates/Video` |

Skip the video files with `-SkipVideo` (Windows) or `--skip-video` (macOS, Linux).

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
- **Script.** Host the unzipped package on a share or in a pkg of your own, and run `macos/install-climb-templates.sh` from a Jamf policy as root. Put `skip-video` in parameter 4 to leave out the video files.

The templates show for every user under File, New from Template in Word, Excel and PowerPoint (Office 16.x or Microsoft 365). Quit and reopen Office after installing. To remove, run `/Library/Application Support/Climb/Templates/uninstall-climb-templates.sh` as root from a policy.

Other managers (Kandji, Mosyle, Intune for Mac) take the same `.pkg`.

## Linux

```
sudo ./linux/install-climb-templates.sh            # everyone on this machine
./linux/install-climb-templates.sh                 # just you, no sudo
```

As root it installs the fonts system-wide, puts everything in `/opt/climb-templates`, and links a folder per brand into the LibreOffice template folder of every person in `/home` and of new accounts (`/etc/skel`). Push it with Ansible, Salt, Puppet or Landscape by copying the unzipped package and running the script. The templates show in LibreOffice under File, New, Templates. To remove, run `/opt/climb-templates/uninstall-climb-templates.sh`.

## After installing

Open Word, File, New and check the brand folder is there, then start a document from the Report template and check the headings are in Montserrat. If they show in Arial or Calibri, the fonts did not install or the app was open during the install: restart the app, or sign out and back in.

## Tested

The Linux and macOS scripts were run against a test folder, and every PowerShell script parses cleanly. None of them has been run yet on a managed Windows PC, a Mac or a real Intune or Jamf tenant. Try them on one test device before you roll them out widely.
