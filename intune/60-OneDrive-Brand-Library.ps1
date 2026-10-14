<#
.SYNOPSIS
    Puts OneDrive on every device and syncs the brand centre library to it, kept offline.

.DESCRIPTION
    Finds the SharePoint library from -SiteUrl and -LibraryName (or takes -LibraryId as copied
    from the library's Sync > Copy library ID), then creates or updates four Intune objects:

    Windows (OneDrive is part of Windows 10 and 11):
      1. Remediation "Climb - Windows - OneDrive sign-in" (system, daily): turns on silent
         sign-in with the Windows account and Files On-Demand.
      2. Remediation "Climb - Windows - Brand library offline" (signed-in person, daily): adds
         the library to OneDrive's automatic team site sync, and once it has synced marks
         the whole folder "Always keep on this device" (attrib +P), so every file is offline.
         People without access to the library get nothing; OneDrive skips it for them.

    macOS:
      3. Shell script "Climb - macOS - OneDrive" (root, daily): installs the OneDrive app when
         it is missing and sets it to open at login.
      4. Shell script "Climb - macOS - Brand library sync" (signed-in person, daily): when the
         library is not synced yet, asks OneDrive to sync it (the same link as the library's
         Sync button). OneDrive on Mac has no setting that syncs a library automatically and
         no command that keeps files offline, so each person confirms the sync once and, to
         keep it offline, right-clicks the folder in Finder and picks Always Keep on This Device.

    Windows adds the library within 8 hours of the next sign-in. Files the person cannot open
    are never synced.

.PARAMETER SiteUrl
    The SharePoint site, for example https://contoso.sharepoint.com/sites/BrandCenter.
.PARAMETER LibraryName
    The document library on that site. Default Documents.
.PARAMETER LibraryId
    The library ID from Sync > Copy library ID, instead of -SiteUrl and -LibraryName.
    Needs -SiteTitle and -LibraryTitle too, so Macs can tell when it has synced.
.PARAMETER Target
    AllDevices (default), AllUsers, Group or None.
.PARAMETER GroupName
    Entra group name(s) when -Target Group.

.EXAMPLE
    pwsh ./60-OneDrive-Brand-Library.ps1 -SiteUrl https://contoso.sharepoint.com/sites/BrandCenter -WhatIf
#>
[CmdletBinding(SupportsShouldProcess, DefaultParameterSetName = 'Site')]
param(
    [Parameter(Mandatory, ParameterSetName = 'Site')][string]$SiteUrl,
    [Parameter(ParameterSetName = 'Site')][string]$LibraryName = 'Documents',
    [Parameter(Mandatory, ParameterSetName = 'Id')][string]$LibraryId,
    [Parameter(Mandatory, ParameterSetName = 'Id')][string]$SiteTitle,
    [Parameter(Mandatory, ParameterSetName = 'Id')][string]$LibraryTitle,
    [ValidateSet('AllDevices', 'AllUsers', 'Group', 'None')][string]$Target = 'AllDevices',
    [string[]]$GroupName,
    [string]$TenantId,
    [switch]$UseDeviceCode
)

$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'ClimbIntune.psm1') -Force
$extra = if ($PSCmdlet.ParameterSetName -eq 'Site') { @('Sites.Read.All') } else { @() }
Connect-ClimbGraph -TenantId $TenantId -UseDeviceCode:$UseDeviceCode -ExtraScopes $extra

# --- The library --------------------------------------------------------------
if ($PSCmdlet.ParameterSetName -eq 'Site') {
    $u = [uri]$SiteUrl
    $site = Invoke-ClimbGraph -Path "https://graph.microsoft.com/v1.0/sites/$($u.Host):$($u.AbsolutePath.TrimEnd('/'))"
    $drives = @(Invoke-ClimbGraph -Path "https://graph.microsoft.com/v1.0/sites/$($site.id)/drives?`$select=name,webUrl,sharepointIds")
    $drive = $drives | Where-Object { $_.name -eq $LibraryName } | Select-Object -First 1
    if (-not $drive) { throw "No library called '$LibraryName' on $SiteUrl. Libraries there: $(($drives.name) -join ', ')." }
    $ids = $drive.sharepointIds
    $tenant = (Get-MgContext).TenantId
    $webUrl = $ids.siteUrl
    $LibraryId = "tenantId=$tenant&siteId={$($ids.siteId)}&webId={$($ids.webId)}&listId={$($ids.listId)}&webUrl=$webUrl&version=1"
    $SiteTitle = $site.displayName
    $LibraryTitle = $drive.name
}
else {
    $LibraryId = [uri]::UnescapeDataString($LibraryId)
}
$parts = @{}
foreach ($kv in $LibraryId.Split('&')) { $k, $v = $kv.Split('=', 2); $parts[$k] = $v }
foreach ($k in 'tenantId', 'siteId', 'webId', 'listId', 'webUrl') {
    if (-not $parts[$k]) { throw "The library ID has no $k. Copy it again from the library's Sync > Copy library ID." }
}
$mountName = "$SiteTitle - $LibraryTitle"
Write-ClimbStep "Library: $mountName ($($parts.webUrl))"

# Same link the library's Sync button opens.
$enc = { param($s) [uri]::EscapeDataString($s) }
$odopen = 'odopen://sync/?siteId=' + (& $enc $parts.siteId) + '&webId=' + (& $enc $parts.webId) +
    '&listId=' + (& $enc $parts.listId) + '&webUrl=' + (& $enc $parts.webUrl) +
    '&webTitle=' + (& $enc $SiteTitle) + '&listTitle=' + (& $enc $LibraryTitle)

# Single quotes inside generated PowerShell and shell strings.
$psq = { param($s) $s.Replace("'", "''") }
$shq = { param($s) "'" + $s.Replace("'", "'\''") + "'" }

$targets = Get-ClimbAssignmentTargets -Target $Target -GroupName $GroupName

# --- 1. Windows: sign-in and Files On-Demand (system) -----------------------------
$detect1 = @'
# Climb OneDrive sign-in: detection. Generated by 60-OneDrive-Brand-Library.ps1.
$p = Get-ItemProperty -Path 'HKLM:\SOFTWARE\Policies\Microsoft\OneDrive' -ErrorAction SilentlyContinue
if ($p -and $p.SilentAccountConfig -eq 1 -and $p.FilesOnDemandEnabled -eq 1) { Write-Output 'OneDrive sign-in policies set'; exit 0 }
Write-Output 'OneDrive sign-in policies missing'
exit 1
'@
$remediate1 = @'
# Climb OneDrive sign-in: remediation. Generated by 60-OneDrive-Brand-Library.ps1.
$key = 'HKLM:\SOFTWARE\Policies\Microsoft\OneDrive'
New-Item -Path $key -Force | Out-Null
Set-ItemProperty -Path $key -Name 'SilentAccountConfig' -Value 1 -Type DWord
Set-ItemProperty -Path $key -Name 'FilesOnDemandEnabled' -Value 1 -Type DWord
Write-Output 'OneDrive signs in with the Windows account; Files On-Demand on'
exit 0
'@

# --- 2. Windows: library sync and keep offline (signed-in person) -------------------
$common2 = @"
`$Name = '$(& $psq $mountName)'
`$LibraryId = '$(& $psq $LibraryId)'
# OneDrive names the synced folder "<site> - <library>".
function Get-ClimbMount {
    Get-ChildItem 'HKCU:\Software\SyncEngines\Providers\OneDrive' -ErrorAction SilentlyContinue |
        ForEach-Object { Get-ItemProperty `$_.PSPath } |
        Where-Object { (`$_.PSObject.Properties.Name -contains 'MountPoint') -and (`$_.MountPoint -like "*\`$Name") } |
        Select-Object -First 1 -ExpandProperty MountPoint
}
"@
$detect2 = @"
# Climb brand library offline: detection. Generated by 60-OneDrive-Brand-Library.ps1.
$common2
`$set = (Get-ItemProperty 'HKCU:\Software\Policies\Microsoft\OneDrive\TenantAutoMount' -ErrorAction SilentlyContinue).`$Name
if (`$set -ne `$LibraryId) { Write-Output 'Library not set to sync yet'; exit 1 }
`$mount = Get-ClimbMount
if (-not `$mount -or -not (Test-Path `$mount)) { Write-Output 'Library set to sync; OneDrive has not added it yet'; exit 0 }
`$online = Get-ChildItem -Path `$mount -Recurse -Force -ErrorAction SilentlyContinue |
    Where-Object { -not (`$_.Attributes -band [IO.FileAttributes]0x80000) } | Select-Object -First 1
if (`$online) { Write-Output "Not all files are kept on this device: `$(`$online.FullName)"; exit 1 }
Write-Output "Library synced and kept on this device at `$mount"
exit 0
"@
$remediate2 = @"
# Climb brand library offline: remediation. Generated by 60-OneDrive-Brand-Library.ps1.
$common2
`$key = 'HKCU:\Software\Policies\Microsoft\OneDrive\TenantAutoMount'
New-Item -Path `$key -Force | Out-Null
Set-ItemProperty -Path `$key -Name `$Name -Value `$LibraryId -Type String
`$mount = Get-ClimbMount
if (-not `$mount -or -not (Test-Path `$mount)) { Write-Output 'Library added to OneDrive automatic sync; it appears within 8 hours of the next sign-in'; exit 0 }
# Pinned (+P) and not online-only (-U), for the folder and everything in it.
& attrib.exe +P -U "`$mount" | Out-Null
& attrib.exe +P -U "`$mount\*" /S /D | Out-Null
Write-Output "Kept on this device: `$mount"
exit 0
"@

# --- 3. macOS: install OneDrive (root) ------------------------------------------
$mac3 = @(
    '#!/bin/bash'
    '# Climb OneDrive for macOS. Generated by 60-OneDrive-Brand-Library.ps1.'
    'set -euo pipefail'
    'LOG="/Library/Logs/Climb/onedrive.log"'
    'mkdir -p "$(dirname "$LOG")"'
    'exec >>"$LOG" 2>&1'
    'echo "$(date -u +%FT%TZ) checking OneDrive"'
    'if [ ! -d "/Applications/OneDrive.app" ]; then'
    '  WORK="$(mktemp -d /tmp/climb-onedrive.XXXXXX)"'
    '  trap ''rm -rf "$WORK"'' EXIT'
    '  curl -fsSL --retry 3 -o "$WORK/OneDrive.pkg" "https://go.microsoft.com/fwlink/?linkid=823060"'
    '  pkgutil --check-signature "$WORK/OneDrive.pkg" | grep -q "Developer ID Installer: Microsoft Corporation" || { echo "OneDrive.pkg is not signed by Microsoft"; exit 1; }'
    '  installer -pkg "$WORK/OneDrive.pkg" -target /'
    '  echo "installed OneDrive"'
    'fi'
    'defaults write /Library/Preferences/com.microsoft.OneDrive OpenAtLogin -bool true'
    'echo "OneDrive ready"'
)

# --- 4. macOS: ask OneDrive to sync the library (signed-in person) -------------------
$mac4 = @(
    '#!/bin/bash'
    '# Climb brand library sync on macOS. Generated by 60-OneDrive-Brand-Library.ps1.'
    'set -uo pipefail'
    "NAME=$(& $shq $mountName)"
    "LINK=$(& $shq $odopen)"
    'LOG="$HOME/Library/Logs/Climb/brand-library.log"'
    'mkdir -p "$(dirname "$LOG")"'
    'exec >>"$LOG" 2>&1'
    'echo "$(date -u +%FT%TZ) checking $NAME"'
    'for d in "$HOME"/Library/CloudStorage/OneDrive-*/"$NAME" "$HOME"/Library/CloudStorage/OneDrive-*/*/"$NAME"; do'
    '  if [ -d "$d" ]; then echo "synced at $d"; exit 0; fi'
    'done'
    'if ! pgrep -xq OneDrive; then echo "OneDrive is not running yet; next run"; exit 0; fi'
    'if ! ls -d "$HOME"/Library/CloudStorage/OneDrive-* >/dev/null 2>&1; then echo "OneDrive is not signed in yet; next run"; exit 0; fi'
    'open "$LINK"'
    'echo "asked OneDrive to sync $NAME"'
)

# --- Write the objects --------------------------------------------------------------
$items = @(
    @{
        Collection = 'deviceManagement/deviceHealthScripts'; Kind = 'healthScript'
        Name       = Get-ClimbName 'Windows - OneDrive sign-in'
        Body       = @{
            '@odata.type'            = '#microsoft.graph.deviceHealthScript'
            description              = 'OneDrive signs in with the Windows account and uses Files On-Demand. Managed by 60-OneDrive-Brand-Library.ps1.'
            publisher                = 'ClimbGroup'; runAsAccount = 'system'; runAs32Bit = $false; enforceSignatureCheck = $false
            detectionScriptContent   = ConvertTo-ClimbBase64 $detect1
            remediationScriptContent = ConvertTo-ClimbBase64 $remediate1
            roleScopeTagIds          = @('0')
        }
    }
    @{
        Collection = 'deviceManagement/deviceHealthScripts'; Kind = 'healthScript'
        Name       = Get-ClimbName 'Windows - Brand library offline'
        Body       = @{
            '@odata.type'            = '#microsoft.graph.deviceHealthScript'
            description              = "Syncs '$mountName' with OneDrive and keeps every file on the device. Managed by 60-OneDrive-Brand-Library.ps1."
            publisher                = 'ClimbGroup'; runAsAccount = 'user'; runAs32Bit = $false; enforceSignatureCheck = $false
            detectionScriptContent   = ConvertTo-ClimbBase64 $detect2
            remediationScriptContent = ConvertTo-ClimbBase64 $remediate2
            roleScopeTagIds          = @('0')
        }
    }
    @{
        Collection = 'deviceManagement/deviceShellScripts'; Kind = 'shellScript'
        Name       = Get-ClimbName 'macOS - OneDrive'
        Body       = @{
            '@odata.type'      = '#microsoft.graph.deviceShellScript'
            description        = 'Installs OneDrive when missing and opens it at login. Log: /Library/Logs/Climb/onedrive.log. Managed by 60-OneDrive-Brand-Library.ps1.'
            fileName           = 'climb-onedrive.sh'
            scriptContent      = ConvertTo-ClimbBase64 (($mac3 -join "`n") + "`n")
            runAsAccount       = 'system'; executionFrequency = 'P1D'; retryCount = 3; blockExecutionNotifications = $true
            roleScopeTagIds    = @('0')
        }
    }
    @{
        Collection = 'deviceManagement/deviceShellScripts'; Kind = 'shellScript'
        Name       = Get-ClimbName 'macOS - Brand library sync'
        Body       = @{
            '@odata.type'      = '#microsoft.graph.deviceShellScript'
            description        = "Asks OneDrive to sync '$mountName' until it is synced. Log: ~/Library/Logs/Climb/brand-library.log. Managed by 60-OneDrive-Brand-Library.ps1."
            fileName           = 'climb-brand-library.sh'
            scriptContent      = ConvertTo-ClimbBase64 (($mac4 -join "`n") + "`n")
            runAsAccount       = 'user'; executionFrequency = 'P1D'; retryCount = 3; blockExecutionNotifications = $true
            roleScopeTagIds    = @('0')
        }
    }
)

$daily = @{ '@odata.type' = '#microsoft.graph.deviceHealthScriptDailySchedule'; interval = 1; useUtc = $false; time = '10:00:00' }
foreach ($i in $items) {
    $i.Body.displayName = $i.Name
    $id = Set-ClimbObject -Collection $i.Collection -Name $i.Name -Body $i.Body -WhatIf:$WhatIfPreference
    $assign = @{ Collection = $i.Collection; Id = $id; Name = $i.Name; Kind = $i.Kind; Targets = $targets; WhatIf = $WhatIfPreference }
    if ($i.Kind -eq 'healthScript') { $assign.RunSchedule = $daily }
    Set-ClimbAssignment @assign
}

Write-ClimbStep 'Done. Windows syncs the library within 8 hours of the next sign-in; Macs ask once OneDrive is signed in.'
