<#
.SYNOPSIS
    Installs the brand fonts on iPhones and iPads.

.DESCRIPTION
    Takes Montserrat and Open Sans from the templates release and wraps them in Apple font
    payloads (com.apple.font). Intune custom profiles must be under 1 MB, so the fonts are
    packed into as few profiles as fit: "Climb - iOS - Brand fonts 1", "... 2" and so on
    (four with the default fonts). Re-running with fewer fonts leaves any higher-numbered
    profile in place; delete it in the admin center.
    Works on supervised and unsupervised devices. Apps that support installed fonts (such
    as Word, Excel and PowerPoint for iPad and iPhone) then list Montserrat and Open Sans.

    Android has no managed way to install fonts; the Office apps there substitute a similar
    font, and documents keep their font names.

.PARAMETER Fonts
    Font files to install. Default: the Montserrat and Open Sans weights the templates use.
.PARAMETER TemplatesVersion
    Release to take the fonts from. Default: the latest.

.EXAMPLE
    pwsh ./30-iOS-Fonts.ps1 -WhatIf
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [string[]]$Fonts = @(
        'Montserrat-Regular.ttf', 'Montserrat-Bold.ttf', 'Montserrat-ExtraBold.ttf', 'Montserrat-Black.ttf',
        'OpenSans-Regular.ttf', 'OpenSans-Italic.ttf', 'OpenSans-SemiBold.ttf', 'OpenSans-Bold.ttf'
    ),
    [string]$TemplatesVersion,
    [ValidateSet('AllDevices', 'AllUsers', 'Group', 'None')][string]$Target = 'AllDevices',
    [string[]]$GroupName,
    [string]$TenantId,
    [switch]$UseDeviceCode
)

$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'ClimbIntune.psm1') -Force
Connect-ClimbGraph -TenantId $TenantId -UseDeviceCode:$UseDeviceCode

$release = Get-ClimbTemplatesRelease -Version $TemplatesVersion
Write-ClimbStep "Taking fonts from templates $($release.Version)"
$zip = Get-ClimbDownload -Url $release.Url
if ((Get-FileHash -Algorithm SHA256 -Path $zip).Hash.ToLowerInvariant() -ne $release.Sha256) { throw 'Checksum mismatch on the templates download.' }
$work = Join-Path ([IO.Path]::GetTempPath()) "climb-fonts-$($release.Version)"
if (Test-Path $work) { Remove-Item $work -Recurse -Force -WhatIf:$false }
Expand-Archive -Path $zip -DestinationPath $work -WhatIf:$false
$fontDir = Get-ChildItem -Path $work -Recurse -Directory -Filter fonts | Where-Object { Get-ChildItem $_.FullName -Filter *.ttf } | Select-Object -First 1
if (-not $fontDir) { throw 'No fonts folder with .ttf files in the templates package.' }

function New-FontPayload([IO.FileInfo]$f) {
    $b64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes($f.FullName))
    $base = [IO.Path]::GetFileNameWithoutExtension($f.Name)
    # Stable UUID per font so re-runs do not reinstall unchanged fonts.
    $md5 = [Security.Cryptography.MD5]::HashData([Text.Encoding]::UTF8.GetBytes("climb-font-$base"))
    $id = ([guid]::new($md5)).ToString().ToUpperInvariant()
    @"
    <dict>
      <key>PayloadType</key><string>com.apple.font</string>
      <key>PayloadIdentifier</key><string>com.climb-uk.intune.fonts.$($base.ToLowerInvariant())</string>
      <key>PayloadUUID</key><string>$id</string>
      <key>PayloadVersion</key><integer>1</integer>
      <key>PayloadDisplayName</key><string>$base</string>
      <key>Name</key><string>$($f.Name)</string>
      <key>Font</key><data>$b64</data>
    </dict>
"@
}

# Pack fonts into as few profiles as fit under ~950 KB each (largest first, first bin with room).
$limit = 950KB
$payloads = foreach ($name in $Fonts) {
    $f = Get-Item (Join-Path $fontDir.FullName $name) -ErrorAction SilentlyContinue
    if (-not $f) { Write-Warning "Not in the package, skipped: $name"; continue }
    New-FontPayload $f
}
$bins = [System.Collections.Generic.List[object]]::new()
foreach ($p in ($payloads | Sort-Object Length -Descending)) {
    $bin = $bins | Where-Object { $_.Size + $p.Length -le $limit } | Select-Object -First 1
    if (-not $bin) { $bin = [pscustomobject]@{ Size = 0; Items = [System.Collections.Generic.List[string]]::new() }; $bins.Add($bin) }
    $bin.Items.Add($p); $bin.Size += $p.Length
}
$groups = @($bins | ForEach-Object { , @($_.Items) })

$targets = Get-ClimbAssignmentTargets -Target $Target -GroupName $GroupName
$i = 0
foreach ($g in $groups) {
    $i++
    # Stable profile UUID per slot so a re-run replaces the profile on the device.
    $profileUuid = "7c2e5a10-0b4d-4f6e-8a3c-{0:D12}" -f $i
    $mobileconfig = @"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>PayloadContent</key>
  <array>
$($g -join "`n")
  </array>
  <key>PayloadDisplayName</key><string>Climb brand fonts $i</string>
  <key>PayloadIdentifier</key><string>com.climb-uk.intune.fonts.$i</string>
  <key>PayloadOrganization</key><string>ClimbGroup</string>
  <key>PayloadType</key><string>Configuration</string>
  <key>PayloadUUID</key><string>$profileUuid</string>
  <key>PayloadVersion</key><integer>1</integer>
</dict>
</plist>
"@
    $bytes = [Text.Encoding]::UTF8.GetByteCount($mobileconfig)
    if ($bytes -ge 1000000) { throw "Font profile $i is $bytes bytes; Intune allows under 1,000,000. Pass fewer -Fonts." }
    $name = Get-ClimbName "iOS - Brand fonts $i"
    Write-ClimbStep "$name ($([math]::Round($bytes / 1KB)) KB, $($g.Count) fonts)"
    $body = @{
        '@odata.type'   = '#microsoft.graph.iosCustomConfiguration'
        displayName     = $name
        description     = "Montserrat and Open Sans (from templates $($release.Version)). Managed by 30-iOS-Fonts.ps1."
        payloadName     = "Climb brand fonts $i"
        payloadFileName = "climb-fonts-$i.mobileconfig"
        payload         = ConvertTo-ClimbBase64 $mobileconfig
        roleScopeTagIds = @('0')
    }
    $id = Set-ClimbObject -Collection 'deviceManagement/deviceConfigurations' -Name $name -Body $body -WhatIf:$WhatIfPreference
    Set-ClimbAssignment -Collection 'deviceManagement/deviceConfigurations' -Id $id -Name $name -Kind deviceConfiguration -Targets $targets -WhatIf:$WhatIfPreference
}

Remove-Item $work -Recurse -Force -WhatIf:$false
Write-ClimbStep "Done: $i font profile(s)."
