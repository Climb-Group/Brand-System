<#
.SYNOPSIS
    Sets the brand wallpaper on company iPhones and iPads.

.DESCRIPTION
    Creates or updates an iOS/iPadOS device features profile "Climb - iOS - Wallpaper" with
    the brand phone wallpaper on the lock screen and home screen.

    Apple only applies this to SUPERVISED devices (enrolled through Apple Business Manager /
    automated device enrollment). Personal phones enrolled with the Company Portal, and
    unsupervised company phones, ignore it; Intune reports them as not applicable.
    The image travels inside the profile, so it must be under 750 KB.

.PARAMETER Brand
    ClimbUK (default) or Climb27. ClimbGroup has no phone wallpapers.
.PARAMETER Design
    stage-light (default), ascent, connections or contours.
.PARAMETER Location
    lockAndHomeScreens (default), lockScreen or homeScreen.
.PARAMETER ImagePath
    Use a local .jpg/.png instead of downloading from the brand centre.

.EXAMPLE
    pwsh ./22-iOS-Wallpaper.ps1 -WhatIf
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [ValidateSet('ClimbUK', 'ClimbGroup', 'Climb27')][string]$Brand = 'ClimbUK',
    [ValidateSet('stage-light', 'ascent', 'connections', 'contours')][string]$Design = 'stage-light',
    [ValidateSet('lockAndHomeScreens', 'lockScreen', 'homeScreen')][string]$Location = 'lockAndHomeScreens',
    [string]$ImagePath,
    [ValidateSet('AllDevices', 'AllUsers', 'Group', 'None')][string]$Target = 'AllDevices',
    [string[]]$GroupName,
    [string]$TenantId,
    [switch]$UseDeviceCode
)

$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'ClimbIntune.psm1') -Force
Connect-ClimbGraph -TenantId $TenantId -UseDeviceCode:$UseDeviceCode

if (-not $ImagePath) {
    $file = Get-ClimbWallpaperFile -Brand $Brand -Design $Design -Kind phone -Size '1179x2556'
    $ImagePath = Get-ClimbDownload -Url (Get-ClimbBrandFileUrl $file)
}
$bytes = [IO.File]::ReadAllBytes($ImagePath)
if ($bytes.Length -ge 750KB) { throw "$ImagePath is $([math]::Round($bytes.Length / 1KB)) KB; Intune needs under 750 KB. Pick another design or pass a smaller -ImagePath." }
$mime = if ($ImagePath -match '\.png$') { 'image/png' } else { 'image/jpeg' }
Write-ClimbStep "Wallpaper: $ImagePath ($([math]::Round($bytes.Length / 1KB)) KB) on $Location"

$name = Get-ClimbName 'iOS - Wallpaper'
$body = @{
    '@odata.type'             = '#microsoft.graph.iosDeviceFeaturesConfiguration'
    displayName               = $name
    description               = "Brand wallpaper ($Brand, $Design). Supervised devices only. Managed by 22-iOS-Wallpaper.ps1."
    wallpaperDisplayLocation  = $Location
    wallpaperImage            = @{
        '@odata.type' = '#microsoft.graph.mimeContent'
        type          = $mime
        value         = [Convert]::ToBase64String($bytes)
    }
    roleScopeTagIds           = @('0')
}

# Resolve the assignment first, so a missing group stops the run before anything is created.
$targets = Get-ClimbAssignmentTargets -Target $Target -GroupName $GroupName
$id = Set-ClimbObject -Collection 'deviceManagement/deviceConfigurations' -Name $name -Body $body -WhatIf:$WhatIfPreference
Set-ClimbAssignment -Collection 'deviceManagement/deviceConfigurations' -Id $id -Name $name -Kind deviceConfiguration -Targets $targets -WhatIf:$WhatIfPreference

Write-ClimbStep 'Done. People can still change the wallpaper afterwards unless a device restriction blocks it (left alone on purpose).'
