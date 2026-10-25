<#
.SYNOPSIS
    Installs the ClimbUK, ClimbGroup and Climb27 templates, fonts and themes on Windows.

.DESCRIPTION
    Run as SYSTEM (Intune Win32 app, install behaviour System) or from an elevated prompt.

    Machine-wide:
      - Fonts (unless -SkipFonts): Montserrat and Open Sans into C:\Windows\Fonts,
        registered for all users.
      - Templates: Word, Excel and PowerPoint templates into
        C:\ProgramData\Climb\Templates\Office\<Brand>, themes into ...\Themes,
        LibreOffice copies into ...\LibreOffice.
      - Video (unless -SkipVideo): DaVinci Resolve titles and LUT, Premiere Pro LUT,
        and the rest of the video kit into ...\Video.
      - ONLYOFFICE Desktop Editors: templates added to its Templates list, and a start-up
        task that puts them back after an ONLYOFFICE update.
      - Active Setup entry, so Set-ClimbTemplatesUser.ps1 runs once for each person
        at their next sign-in and points Office at the shared templates.

    Re-running is safe: files are overwritten and the version is updated.

.PARAMETER SkipVideo
    Do not install the DaVinci Resolve and Premiere Pro files.

.PARAMETER SkipFonts
    Do not install the fonts, for a device manager that installs them with its own package.
    The uninstaller then leaves the fonts alone too.

.EXAMPLE
    powershell.exe -ExecutionPolicy Bypass -NoProfile -File .\Install-ClimbTemplates.ps1
#>
[CmdletBinding()]
param(
    [switch]$SkipVideo,
    [switch]$SkipFonts
)

$ErrorActionPreference = 'Stop'

$PackageRoot = Split-Path -Parent $PSScriptRoot
$Payload = Join-Path $PackageRoot 'payload'
if (-not (Test-Path $Payload)) { $Payload = Join-Path $PSScriptRoot 'payload' }
if (-not (Test-Path $Payload)) { throw "Payload folder not found next to $PSScriptRoot" }

$Version = (Get-Content -Path (Join-Path $PackageRoot 'VERSION') -ErrorAction SilentlyContinue | Select-Object -First 1)
if (-not $Version) { $Version = '@VERSION@' }  # filled in by _build/package_build.py
$Version = $Version.Trim()

$Dest = Join-Path $env:ProgramData 'Climb\Templates'
$LogDir = Join-Path $env:ProgramData 'Climb\Logs'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
Start-Transcript -Path (Join-Path $LogDir 'install.log') -Append | Out-Null

function Copy-Tree([string]$From, [string]$To) {
    if (-not (Test-Path $From)) { return }
    New-Item -ItemType Directory -Force -Path $To | Out-Null
    Copy-Item -Path (Join-Path $From '*') -Destination $To -Recurse -Force
}

function Get-FontDisplayName([string]$File) {
    # Montserrat-SemiBoldItalic.ttf -> "Montserrat SemiBold Italic (TrueType)"
    $base = [IO.Path]::GetFileNameWithoutExtension($File)
    $family, $style = $base -split '-', 2
    $family = $family -creplace '(?<=[a-z])(?=[A-Z])', ' '
    $style = $style -creplace '(?<=[a-z])(?=[A-Z])', ' '
    $style = $style -replace 'Semi Bold', 'SemiBold' -replace 'Extra Bold', 'ExtraBold'
    if ($style -eq 'Regular') { return "$family (TrueType)" }
    return "$family $style (TrueType)"
}

try {
    Write-Output "Installing Climb templates $Version from $Payload"

    # Fonts, and their reference copy (the uninstaller removes the fonts listed there)
    if (-not $SkipFonts) {
        $FontDir = Join-Path $env:windir 'Fonts'
        $FontKey = 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts'
        Get-ChildItem -Path (Join-Path $Payload 'fonts') -Filter '*.ttf' | ForEach-Object {
            $target = Join-Path $FontDir $_.Name
            if (-not (Test-Path $target)) {
                Copy-Item -Path $_.FullName -Destination $target -Force
            }
            New-ItemProperty -Path $FontKey -Name (Get-FontDisplayName $_.Name) -Value $_.Name -PropertyType String -Force | Out-Null
            Write-Output "Font: $($_.Name)"
        }
        Copy-Tree (Join-Path $Payload 'fonts') (Join-Path $Dest 'Fonts')
    }
    else {
        # Drop a reference copy left by an earlier full install, so uninstalling keeps the fonts
        Remove-Item -Path (Join-Path $Dest 'Fonts') -Recurse -Force -ErrorAction SilentlyContinue
        Write-Output 'Fonts: skipped (-SkipFonts)'
    }

    # Office templates, themes and LibreOffice copies
    Copy-Tree (Join-Path $Payload 'office') (Join-Path $Dest 'Office')
    Copy-Tree (Join-Path $Payload 'themes') (Join-Path $Dest 'Themes')
    Copy-Tree (Join-Path $Payload 'libreoffice') (Join-Path $Dest 'LibreOffice')
    Copy-Tree (Join-Path $Payload 'defaults') (Join-Path $Dest 'Defaults')
    Copy-Item -Path (Join-Path $PSScriptRoot 'Set-ClimbTemplatesUser.ps1') -Destination $Dest -Force
    Copy-Item -Path (Join-Path $PSScriptRoot 'Set-ClimbDefaultsUser.ps1') -Destination $Dest -Force

    # ONLYOFFICE Desktop Editors: add now, and again at each start-up in case an update removed them
    $OnlyOffice = Join-Path $Dest 'Add-ClimbOnlyOffice.ps1'
    Copy-Item -Path (Join-Path $PSScriptRoot 'Add-ClimbOnlyOffice.ps1') -Destination $OnlyOffice -Force
    try {
        & $OnlyOffice -Action Add -Source (Join-Path $Dest 'Office')
        $TaskAction = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument ('-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "{0}" -Action Ensure' -f $OnlyOffice)
        Register-ScheduledTask -TaskName 'Climb templates for ONLYOFFICE' -TaskPath '\Climb\' -Action $TaskAction `
            -Trigger (New-ScheduledTaskTrigger -AtStartup) -Principal (New-ScheduledTaskPrincipal -UserId 'SYSTEM' -RunLevel Highest) `
            -Settings (New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries) -Force | Out-Null
    }
    catch { Write-Warning "ONLYOFFICE step skipped: $_" }

    # Video
    if (-not $SkipVideo) {
        $Video = Join-Path $Payload 'video'
        Copy-Tree $Video (Join-Path $Dest 'Video')
        $ResolveTemplates = Join-Path $env:ProgramData 'Blackmagic Design\DaVinci Resolve\Fusion\Templates'
        $ResolveLut = Join-Path $env:ProgramData 'Blackmagic Design\DaVinci Resolve\Support\LUT\Climb'
        $PremiereLut = Join-Path $env:ProgramFiles 'Adobe\Common\LUTs\Creative'
        New-Item -ItemType Directory -Force -Path $ResolveTemplates, $ResolveLut, $PremiereLut | Out-Null
        Copy-Item -Path (Join-Path $Video 'resolve\*.drfx') -Destination $ResolveTemplates -Force
        # The logo titles load their PNGs from Templates:/Edit/Titles/<Brand>/ (Resolve cannot read images inside a .drfx)
        Get-ChildItem -Path (Join-Path $Video 'resolve') -Directory | ForEach-Object {
            $t = Join-Path $ResolveTemplates ("Edit\Titles\" + $_.Name)
            New-Item -ItemType Directory -Force -Path $t | Out-Null
            Copy-Item -Path (Join-Path $_.FullName '*.png') -Destination $t -Force
        }
        Copy-Item -Path (Join-Path $Video 'luts\*.cube') -Destination $ResolveLut -Force
        Copy-Item -Path (Join-Path $Video 'luts\*.cube') -Destination $PremiereLut -Force
        Write-Output "Video: Resolve titles, Resolve LUT and Premiere LUT installed"
    }

    # Active Setup: run the per-user step once for each person at next sign-in
    $ActiveSetup = 'HKLM:\SOFTWARE\Microsoft\Active Setup\Installed Components\ClimbTemplates'
    New-Item -Path $ActiveSetup -Force | Out-Null
    Set-ItemProperty -Path $ActiveSetup -Name '(default)' -Value 'Climb templates'
    # Date-based so a reinstall always runs again, even after an uninstall
    Set-ItemProperty -Path $ActiveSetup -Name 'Version' -Value ('{0:yyyy},{0:MMdd},{0:HHmm}' -f (Get-Date))
    Set-ItemProperty -Path $ActiveSetup -Name 'StubPath' -Value ('powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "{0}"' -f (Join-Path $Dest 'Set-ClimbTemplatesUser.ps1'))
    New-ItemProperty -Path $ActiveSetup -Name 'IsInstalled' -Value 1 -PropertyType DWord -Force | Out-Null

    # Version marker for detection
    Set-Content -Path (Join-Path $Dest 'VERSION') -Value $Version
    $Key = 'HKLM:\SOFTWARE\Climb\Templates'
    New-Item -Path $Key -Force | Out-Null
    Set-ItemProperty -Path $Key -Name 'Version' -Value $Version
    Set-ItemProperty -Path $Key -Name 'Path' -Value $Dest
    Set-ItemProperty -Path $Key -Name 'Video' -Value ([int](-not $SkipVideo))
    Set-ItemProperty -Path $Key -Name 'Fonts' -Value ([int](-not $SkipFonts))

    Write-Output "Done. People see the templates after their next sign-in."
    exit 0
}
catch {
    Write-Error $_
    exit 1
}
finally {
    Stop-Transcript | Out-Null
}
