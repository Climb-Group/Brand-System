<#
.SYNOPSIS
    Sets the brand wallpaper on company-owned, fully managed Android phones (optional).

.DESCRIPTION
    Android Enterprise has no wallpaper setting for personal phones (work profile). On fully
    managed company phones Intune can set the wallpaper only through Microsoft Launcher, so
    this profile also turns on Microsoft Launcher configuration. Run-All skips it unless you
    pass -IncludeAndroid, because it changes the home screen app on those phones.

    Creates or updates "Climb - Android - Launcher wallpaper" (Android Enterprise, fully
    managed device restrictions) with the brand phone wallpaper URL.

.PARAMETER AllowUserChange
    Let people change the wallpaper afterwards. Default: they can.
.PARAMETER Brand
    ClimbUK (default) or Climb27.
.PARAMETER Design
    stage-light (default), ascent, connections or contours.
.PARAMETER Size
    1179x2556 or 1440x3120 (default).

.EXAMPLE
    pwsh ./23-Android-Wallpaper.ps1 -WhatIf
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [ValidateSet('ClimbUK', 'ClimbGroup', 'Climb27')][string]$Brand = 'ClimbUK',
    [ValidateSet('stage-light', 'ascent', 'connections', 'contours')][string]$Design = 'stage-light',
    [ValidateSet('1179x2556', '1440x3120')][string]$Size = '1440x3120',
    [bool]$AllowUserChange = $true,
    [string]$ImageUrl,
    [ValidateSet('AllDevices', 'AllUsers', 'Group', 'None')][string]$Target = 'AllDevices',
    [string[]]$GroupName,
    [string]$TenantId,
    [switch]$UseDeviceCode
)

$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'ClimbIntune.psm1') -Force
Connect-ClimbGraph -TenantId $TenantId -UseDeviceCode:$UseDeviceCode

if (-not $ImageUrl) { $ImageUrl = Get-ClimbBrandFileUrl (Get-ClimbWallpaperFile -Brand $Brand -Design $Design -Kind phone -Size $Size) }
Write-ClimbStep "Wallpaper: $ImageUrl"

$name = Get-ClimbName 'Android - Launcher wallpaper'
$body = @{
    '@odata.type'                                         = '#microsoft.graph.androidDeviceOwnerGeneralDeviceConfiguration'
    displayName                                           = $name
    description                                           = "Brand wallpaper through Microsoft Launcher ($Brand, $Design). Fully managed devices only. Managed by 23-Android-Wallpaper.ps1."
    enrollmentProfile                                     = 'fullyManaged'
    microsoftLauncherConfigurationEnabled                 = $true
    microsoftLauncherCustomWallpaperEnabled               = $true
    microsoftLauncherCustomWallpaperImageUrl              = $ImageUrl
    microsoftLauncherCustomWallpaperAllowUserModification = $AllowUserChange
    roleScopeTagIds                                       = @('0')
}

$id = Set-ClimbObject -Collection 'deviceManagement/deviceConfigurations' -Name $name -Body $body -WhatIf:$WhatIfPreference
$targets = Get-ClimbAssignmentTargets -Target $Target -GroupName $GroupName
Set-ClimbAssignment -Collection 'deviceManagement/deviceConfigurations' -Id $id -Name $name -Kind deviceConfiguration -Targets $targets -WhatIf:$WhatIfPreference

Write-ClimbStep 'Done. Microsoft Launcher must also be deployed to those phones (Apps > Android > Managed Google Play).'
