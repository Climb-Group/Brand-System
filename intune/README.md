# Climb branding through Intune

These scripts set up Intune so every company device gets the brand fonts, the Office templates, the brand wallpaper and a branded Company Portal. You run them yourself from PowerShell. Every script is safe to run more than once: it finds the objects it made before by their "Climb - " name and updates them instead of making copies. Every script also takes `-WhatIf`, which prints what it would change and changes nothing.

## What you need

- PowerShell 7.2 or later (`pwsh`). On Linux, install the `powershell` package.
- An Entra account with the Intune Administrator role (or Global Administrator) in your Microsoft 365 tenant.
- Network access to graph.microsoft.com, github.com, raw.githubusercontent.com and www.climb-uk.com.

`00-Prerequisites.ps1` installs the one module the scripts use (Microsoft.Graph.Authentication) for your user, signs you in and checks every permission. The sign-in asks for these Graph permissions: DeviceManagementConfiguration.ReadWrite.All, DeviceManagementScripts.ReadWrite.All, DeviceManagementApps.ReadWrite.All and Group.Read.All. The first time, approve them for the organisation.

## Run order

```bash
cd /path/to/brand-system/intune
pwsh ./00-Prerequisites.ps1              # add -UseDeviceCode if no browser opens
pwsh ./Run-All.ps1 -WhatIf               # read the plan; nothing changes
pwsh ./Run-All.ps1 -Target Group -GroupName 'Climb pilot devices'
# check two or three pilot devices the next day, then:
pwsh ./Run-All.ps1                       # all devices
```

Make the pilot group in Entra first (a few of your own devices on each platform). Add `-IncludeAndroid` to also set the Android wallpaper (see below). `-Brand ClimbGroup` or `-Brand Climb27` and `-Design ascent`, `connections` or `contours` change the wallpaper.

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

Every script except 40 and 50 takes `-Target AllDevices` (default), `AllUsers`, `Group` with `-GroupName`, or `None` (create it but assign nothing).

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
- The templates release the scripts expect (templates-v1.2.2, its zip name, layout and SHA-256) was checked on GitHub.
- Not tested: the brand centre manifest lookup on www.climb-uk.com was not reachable from the test machine, so the wallpaper scripts and script 40 were tested with explicit image URLs. The `-WhatIf` run on your machine will show whether each wallpaper URL resolves.

## Common problems

- **"Insufficient privileges"**: sign in with an Intune Administrator account and approve the permissions; re-run `00-Prerequisites.ps1`.
- **Remediation stays "Pending"**: confirm the licensing prompt (above); devices check in roughly every 8 hours.
- **"More than one object named ..."**: someone copied a Climb policy by hand; rename or delete the copy.
- **iOS wallpaper "not applicable"**: the device is not supervised. That is expected.
- **Wallpaper image too large**: pass a smaller `-Size`, another `-Design`, or a local `-ImagePath`.
