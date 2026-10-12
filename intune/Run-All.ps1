<#
.SYNOPSIS
    Runs the Climb branding scripts in order. Pass -WhatIf first to see the plan.

.DESCRIPTION
    Order: Windows templates and fonts, macOS templates and fonts, the Office brand defaults
    on both, Windows wallpapers,
    macOS wallpaper, iOS wallpaper, iOS fonts, Company Portal branding. Android is skipped
    unless -IncludeAndroid. Every script is safe to re-run: it updates the objects it made
    before (matched by their "Climb - " names) instead of adding new ones.

.PARAMETER Target
    AllDevices (default), AllUsers, Group or None for every script.
.PARAMETER GroupName
    Entra group(s) when -Target Group. Recommended for a first run: a pilot group.
.PARAMETER Brand
    Wallpaper brand: ClimbUK (default), ClimbGroup or Climb27.
.PARAMETER Design
    Wallpaper design: stage-light (default), ascent, connections or contours.
.PARAMETER DefaultsBrand
    Brand new blank Word, Excel and PowerPoint files open in: ClimbGroup (default), ClimbUK or Climb27.

.EXAMPLE
    pwsh ./Run-All.ps1 -WhatIf
.EXAMPLE
    pwsh ./Run-All.ps1 -Target Group -GroupName 'Climb pilot devices'
.EXAMPLE
    pwsh ./Run-All.ps1
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [ValidateSet('AllDevices', 'AllUsers', 'Group', 'None')][string]$Target = 'AllDevices',
    [string[]]$GroupName,
    [ValidateSet('ClimbUK', 'ClimbGroup', 'Climb27')][string]$Brand = 'ClimbUK',
    [ValidateSet('stage-light', 'ascent', 'connections', 'contours')][string]$Design = 'stage-light',
    [ValidateSet('ClimbUK', 'ClimbGroup', 'Climb27')][string]$DefaultsBrand = 'ClimbGroup',
    [switch]$IncludeAndroid,
    [string]$TenantId,
    [switch]$UseDeviceCode
)

$ErrorActionPreference = 'Stop'
$common = @{ Target = $Target; TenantId = $TenantId; UseDeviceCode = $UseDeviceCode; WhatIf = $WhatIfPreference }
if ($GroupName) { $common.GroupName = $GroupName }
$look = @{ Brand = $Brand; Design = $Design }

$steps = @(
    @{ File = '10-Windows-Templates.ps1'; Extra = @{} }
    @{ File = '11-macOS-Templates.ps1'; Extra = @{} }
    @{ File = '12-Windows-Office-Defaults.ps1'; Extra = @{ Brand = $DefaultsBrand } }
    @{ File = '13-macOS-Office-Defaults.ps1'; Extra = @{ Brand = $DefaultsBrand } }
    @{ File = '20-Windows-Wallpapers.ps1'; Extra = $look }
    @{ File = '21-macOS-Wallpaper.ps1'; Extra = $look }
    @{ File = '22-iOS-Wallpaper.ps1'; Extra = $look }
    @{ File = '30-iOS-Fonts.ps1'; Extra = @{} }
)
if ($IncludeAndroid) { $steps += @{ File = '23-Android-Wallpaper.ps1'; Extra = $look } }

$failed = @()
foreach ($s in $steps) {
    Write-Host "`n#### $($s.File)" -ForegroundColor Yellow
    $extra = $s.Extra
    try { & (Join-Path $PSScriptRoot $s.File) @common @extra }
    catch { Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red; $failed += $s.File }
}

# Company Portal branding is tenant-wide (no assignment), so it takes no Target.
Write-Host "`n#### 40-CompanyPortal-Branding.ps1" -ForegroundColor Yellow
try { & (Join-Path $PSScriptRoot '40-CompanyPortal-Branding.ps1') -TenantId $TenantId -UseDeviceCode:$UseDeviceCode -WhatIf:$WhatIfPreference }
catch { Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red; $failed += '40-CompanyPortal-Branding.ps1' }

if ($failed) { Write-Host "`nFinished with failures: $($failed -join ', ')" -ForegroundColor Red; exit 1 }
Write-Host "`nAll steps finished$(if ($WhatIfPreference) { ' (dry run: nothing was changed)' })." -ForegroundColor Green
