<#
.SYNOPSIS
    Makes a Climb brand the default in Word, Excel and PowerPoint for the signed-in person.

.DESCRIPTION
    Runs as the user, after Install-ClimbTemplates.ps1 (package 1.4.0 or later):

    - Word: Normal.dotm in %APPDATA%\Microsoft\Templates, so a new blank document opens on the
      brand letterhead. The person's old Normal.dotm is kept as Normal-before-Climb.dotm the first time.
    - PowerPoint: Blank.potx in the same folder, so a new blank presentation uses the brand
      master and layouts.
    - Excel: Book.xltx in %APPDATA%\Microsoft\Excel\XLSTART, so a new blank workbook uses the
      brand theme and Open Sans.

    Set once per package version and brand (HKCU:\Software\Climb\OfficeDefaults), so changes the
    person makes later stay until a new package or brand is rolled out, or -Force. When Word is
    open it does nothing and exits 1, so the next run tries again.

.PARAMETER Brand
    ClimbGroup (default), ClimbUK or Climb27.
.PARAMETER Force
    Copy the files again even when this version and brand are already set.
#>
[CmdletBinding()]
param(
    [ValidateSet('ClimbUK', 'ClimbGroup', 'Climb27')][string]$Brand = 'ClimbGroup',
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$Dest = Join-Path $env:ProgramData 'Climb\Templates'
$Source = Join-Path $Dest "Defaults\$Brand"
$Version = (Get-Content -Path (Join-Path $Dest 'VERSION') -ErrorAction SilentlyContinue | Select-Object -First 1)
foreach ($f in 'Normal.dotm', 'Blank.potx', 'Book.xltx') {
    if (-not (Test-Path (Join-Path $Source $f))) {
        Write-Output "Missing $Source\${f}: install the Climb templates 1.4.0 or later first"
        exit 1
    }
}

$Key = 'HKCU:\Software\Climb\OfficeDefaults'
$Stamp = "$Version $Brand"
$current = (Get-ItemProperty -Path $Key -Name 'Applied' -ErrorAction SilentlyContinue).Applied
if ($current -eq $Stamp -and -not $Force) { Write-Output "Already set ($Stamp)"; exit 0 }

if (Get-Process -Name WINWORD -ErrorAction SilentlyContinue) { Write-Output 'Word is open; trying again at the next run'; exit 1 }

function Set-ClimbFile([string]$From, [string]$To) {
    New-Item -ItemType Directory -Force -Path (Split-Path $To) | Out-Null
    Copy-Item -Path $From -Destination "$To.climb-new" -Force
    Move-Item -Path "$To.climb-new" -Destination $To -Force
    Write-Output "Default: $To"
}

$Templates = Join-Path $env:APPDATA 'Microsoft\Templates'
$Normal = Join-Path $Templates 'Normal.dotm'
$Backup = Join-Path $Templates 'Normal-before-Climb.dotm'
if ((Test-Path $Normal) -and -not (Test-Path $Backup)) { Copy-Item -Path $Normal -Destination $Backup }
Set-ClimbFile (Join-Path $Source 'Normal.dotm') $Normal
Set-ClimbFile (Join-Path $Source 'Blank.potx') (Join-Path $Templates 'Blank.potx')
Set-ClimbFile (Join-Path $Source 'Book.xltx') (Join-Path $env:APPDATA 'Microsoft\Excel\XLSTART\Book.xltx')

New-Item -Path $Key -Force | Out-Null
Set-ItemProperty -Path $Key -Name 'Applied' -Value $Stamp
Write-Output "$Brand set as the Word, Excel and PowerPoint default"
exit 0
