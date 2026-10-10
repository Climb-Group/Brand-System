<#
.SYNOPSIS
    Points the signed-in person's Office at the shared Climb templates.

.DESCRIPTION
    Runs as the user (Active Setup runs it once per person after Install-ClimbTemplates.ps1,
    or deploy it as an Intune script with "Run this script using the logged on credentials").

    - Sets Office's Workgroup templates folder to C:\ProgramData\Climb\Templates\Office,
      so File, New, Shared (or Personal, on some versions) lists a folder per brand.
      If another workgroup folder is already set, it is left alone and the templates are
      copied into the person's Custom Office Templates folder instead.
    - Copies the brand themes, colours and fonts into the person's Document Themes folder,
      so they appear in Design, Themes, Colors and Fonts in every Office app.

.PARAMETER Force
    Replace an existing Workgroup templates folder setting.
#>
[CmdletBinding()]
param(
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$Dest = Join-Path $env:ProgramData 'Climb\Templates'
$Office = Join-Path $Dest 'Office'
$Themes = Join-Path $Dest 'Themes'
if (-not (Test-Path $Office)) { Write-Output "Climb templates are not installed at $Dest"; exit 0 }

# Workgroup templates (Office 2016, 2019, 2021 and Microsoft 365 all use 16.0)
$General = 'HKCU:\Software\Microsoft\Office\16.0\Common\General'
New-Item -Path $General -Force | Out-Null
$current = (Get-ItemProperty -Path $General -Name 'SharedTemplates' -ErrorAction SilentlyContinue).SharedTemplates
if (-not $current -or $current -eq $Office -or $Force) {
    Set-ItemProperty -Path $General -Name 'SharedTemplates' -Value $Office
    Write-Output "Workgroup templates: $Office"
}
else {
    $personal = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Custom Office Templates\Climb'
    New-Item -ItemType Directory -Force -Path $personal | Out-Null
    Copy-Item -Path (Join-Path $Office '*') -Destination $personal -Recurse -Force
    Write-Output "Workgroup templates already set to $current; copied templates to $personal"
}

# Themes, colour and font schemes
$DocThemes = Join-Path $env:APPDATA 'Microsoft\Templates\Document Themes'
New-Item -ItemType Directory -Force -Path (Join-Path $DocThemes 'Theme Colors'), (Join-Path $DocThemes 'Theme Fonts') | Out-Null
Copy-Item -Path (Join-Path $Themes '*.thmx') -Destination $DocThemes -Force
Copy-Item -Path (Join-Path $Themes 'Theme Colors\*.xml') -Destination (Join-Path $DocThemes 'Theme Colors') -Force
Copy-Item -Path (Join-Path $Themes 'Theme Fonts\*.xml') -Destination (Join-Path $DocThemes 'Theme Fonts') -Force
Write-Output "Themes: $DocThemes"
exit 0
