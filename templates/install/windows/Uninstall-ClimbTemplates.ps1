<#
.SYNOPSIS
    Removes the Climb templates, fonts, themes and video files installed by Install-ClimbTemplates.ps1.

.DESCRIPTION
    Run as SYSTEM or elevated. Per-user settings (the Workgroup templates folder and copied
    themes) are cleared for each person at their next sign-in by Active Setup.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Continue'
$Dest = Join-Path $env:ProgramData 'Climb\Templates'
$FontKey = 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts'
$FontDir = Join-Path $env:windir 'Fonts'

# Fonts: only the files this package installed
$fonts = Get-ChildItem -Path (Join-Path $Dest 'Fonts') -Filter '*.ttf' -ErrorAction SilentlyContinue
foreach ($f in $fonts) {
    $props = Get-ItemProperty -Path $FontKey
    foreach ($p in $props.PSObject.Properties) {
        if ($p.Value -eq $f.Name) { Remove-ItemProperty -Path $FontKey -Name $p.Name -ErrorAction SilentlyContinue }
    }
    Remove-Item -Path (Join-Path $FontDir $f.Name) -Force -ErrorAction SilentlyContinue
}

# Video
foreach ($b in 'ClimbUK', 'ClimbGroup', 'Climb27') {
    Remove-Item -Path (Join-Path $env:ProgramData "Blackmagic Design\DaVinci Resolve\Fusion\Templates\$($b)_Titles.drfx") -Force -ErrorAction SilentlyContinue
}
Remove-Item -Path (Join-Path $env:ProgramData 'Blackmagic Design\DaVinci Resolve\Support\LUT\Climb') -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path (Join-Path $env:ProgramFiles 'Adobe\Common\LUTs\Creative\Climb_Grade_v1.cube') -Force -ErrorAction SilentlyContinue

# Per-user clean-up at next sign-in
$cleanup = Join-Path $env:ProgramData 'Climb\Remove-ClimbTemplatesUser.ps1'
@'
$General = 'HKCU:\Software\Microsoft\Office\16.0\Common\General'
$shared = (Get-ItemProperty -Path $General -Name 'SharedTemplates' -ErrorAction SilentlyContinue).SharedTemplates
if ($shared -like '*\Climb\Templates\*') { Remove-ItemProperty -Path $General -Name 'SharedTemplates' -ErrorAction SilentlyContinue }
$DocThemes = Join-Path $env:APPDATA 'Microsoft\Templates\Document Themes'
foreach ($b in 'ClimbUK', 'ClimbGroup', 'Climb27') { Remove-Item -Path (Join-Path $DocThemes "$b.thmx") -Force -ErrorAction SilentlyContinue }
Remove-Item -Path (Join-Path $DocThemes 'Theme Colors\Climb.xml'), (Join-Path $DocThemes 'Theme Fonts\Climb.xml') -Force -ErrorAction SilentlyContinue
Remove-Item -Path (Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Custom Office Templates\Climb') -Recurse -Force -ErrorAction SilentlyContinue
'@ | Set-Content -Path $cleanup
$ActiveSetup = 'HKLM:\SOFTWARE\Microsoft\Active Setup\Installed Components\ClimbTemplates'
New-Item -Path $ActiveSetup -Force | Out-Null
Set-ItemProperty -Path $ActiveSetup -Name '(default)' -Value 'Climb templates (removal)'
Set-ItemProperty -Path $ActiveSetup -Name 'Version' -Value ('{0:yyyy},{0:MMdd},{0:HHmm}' -f (Get-Date))
Set-ItemProperty -Path $ActiveSetup -Name 'StubPath' -Value ('powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "{0}"' -f $cleanup)

Remove-Item -Path $Dest -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path 'HKLM:\SOFTWARE\Climb\Templates' -Recurse -Force -ErrorAction SilentlyContinue
Write-Output 'Climb templates removed'
exit 0
