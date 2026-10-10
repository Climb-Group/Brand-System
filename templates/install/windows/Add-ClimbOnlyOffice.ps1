<#
.SYNOPSIS
    Adds the Climb templates to the ONLYOFFICE Desktop Editors Templates list, or removes them.

.DESCRIPTION
    ONLYOFFICE lists every file under converter\templates\<language>\ in its program folder,
    so the templates go in a Climb\<Brand> folder inside each language folder. Run as SYSTEM
    or from an elevated prompt.

    Install-ClimbTemplates.ps1 runs this once and registers a scheduled task that runs it
    with -Action Ensure at every start-up, so the templates come back after an ONLYOFFICE
    update replaces its program folder.

.PARAMETER Action
    Add (replace), Ensure (add only where missing) or Remove.

.PARAMETER Source
    Folder holding <Brand>\*.dotx, *.xltx and *.potx. Defaults to
    C:\ProgramData\Climb\Templates\Office.
#>
[CmdletBinding()]
param(
    [ValidateSet('Add', 'Ensure', 'Remove')]
    [string]$Action = 'Add',
    [string]$Source = (Join-Path $env:ProgramData 'Climb\Templates\Office')
)

$Status = 0
$Apps = @(
    @($env:ProgramFiles, 'ONLYOFFICE\DesktopEditors'),
    @(${env:ProgramFiles(x86)}, 'ONLYOFFICE\DesktopEditors'),
    @($env:LOCALAPPDATA, 'Programs\ONLYOFFICE\DesktopEditors')
) | Where-Object { $_[0] } | ForEach-Object { Join-Path $_[0] $_[1] } |
    Where-Object { Test-Path (Join-Path $_ 'converter') } | Select-Object -Unique

if (-not $Apps) {
    Write-Output 'ONLYOFFICE Desktop Editors not found; skipped'
    exit 0
}

foreach ($app in $Apps) {
    $tpl = Join-Path $app 'converter\templates'
    New-Item -ItemType Directory -Force -Path $tpl | Out-Null
    # one target per language folder, or the templates folder itself when it has none
    $targets = @(Get-ChildItem -Path $tpl -Directory | Where-Object Name -ne 'Climb' | ForEach-Object FullName)
    if (-not $targets) { $targets = @($tpl) }
    foreach ($t in $targets) {
        $climb = Join-Path $t 'Climb'
        if ($Action -eq 'Ensure' -and (Test-Path $climb)) { continue }
        if (Test-Path $climb) { Remove-Item -Path $climb -Recurse -Force }
        if ($Action -eq 'Remove') { continue }
        try {
            Get-ChildItem -Path $Source -Directory | ForEach-Object {
                $to = Join-Path $climb $_.Name
                New-Item -ItemType Directory -Force -Path $to | Out-Null
                Get-ChildItem -Path $_.FullName -File |
                    Where-Object Extension -in '.dotx', '.xltx', '.potx' |
                    Copy-Item -Destination $to -Force
            }
        }
        catch {
            Write-Warning "ONLYOFFICE: could not copy into ${t}: $_"
            $Status = 1
        }
    }
    Write-Output "ONLYOFFICE: $Action done in $tpl"
}
exit $Status
