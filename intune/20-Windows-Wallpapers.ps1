<#
.SYNOPSIS
    Sets the brand desktop and lock screen wallpaper on Windows PCs.

.DESCRIPTION
    Creates or updates a settings catalog policy "Climb - Windows - Desktop and lock screen
    wallpaper" with the Personalization settings Desktop Image Url and Lock Screen Image Url.
    Windows downloads the image from the public brand centre. Works on Pro, Enterprise and
    Education. The picture is enforced: people cannot change it while the policy applies.
    Use -LockScreenOnly to brand only the lock screen and leave the desktop to each person.

.PARAMETER Brand
    ClimbUK (default), ClimbGroup or Climb27.
.PARAMETER Design
    stage-light (default), ascent, connections or contours.
.PARAMETER Size
    2560x1440, 3840x2160 (default) or 5120x2880.
.PARAMETER DesktopImageUrl
    Use this exact HTTPS .jpg/.png URL for the desktop instead of a brand centre wallpaper.
.PARAMETER LockScreenImageUrl
    Use this exact HTTPS .jpg/.png URL for the lock screen. Default: same as the desktop.
.PARAMETER LockScreenOnly
    Do not set the desktop picture.

.EXAMPLE
    pwsh ./20-Windows-Wallpapers.ps1 -WhatIf
.EXAMPLE
    pwsh ./20-Windows-Wallpapers.ps1 -Design contours -LockScreenOnly
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [ValidateSet('ClimbUK', 'ClimbGroup', 'Climb27')][string]$Brand = 'ClimbUK',
    [ValidateSet('stage-light', 'ascent', 'connections', 'contours')][string]$Design = 'stage-light',
    [ValidateSet('2560x1440', '3840x2160', '5120x2880')][string]$Size = '3840x2160',
    [string]$DesktopImageUrl,
    [string]$LockScreenImageUrl,
    [switch]$LockScreenOnly,
    [ValidateSet('AllDevices', 'AllUsers', 'Group', 'None')][string]$Target = 'AllDevices',
    [string[]]$GroupName,
    [string]$TenantId,
    [switch]$UseDeviceCode
)

$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'ClimbIntune.psm1') -Force
Connect-ClimbGraph -TenantId $TenantId -UseDeviceCode:$UseDeviceCode

if (-not $DesktopImageUrl) {
    $DesktopImageUrl = Get-ClimbBrandFileUrl (Get-ClimbWallpaperFile -Brand $Brand -Design $Design -Kind desktop -Size $Size)
}
if (-not $LockScreenImageUrl) { $LockScreenImageUrl = $DesktopImageUrl }
foreach ($u in @($DesktopImageUrl, $LockScreenImageUrl)) {
    if ($u -notlike 'https://*') { throw "Image URLs must be HTTPS: $u" }
    $r = Invoke-WebRequest -Uri $u -Method Get -SkipHttpErrorCheck
    if ($r.StatusCode -ne 200) { throw "The image is not reachable ($($r.StatusCode)): $u" }
}
Write-ClimbStep "Desktop: $(if ($LockScreenOnly) { '(not set)' } else { $DesktopImageUrl })"
Write-ClimbStep "Lock screen: $LockScreenImageUrl"

$definitions = [ordered]@{
    'device_vendor_msft_personalization_lockscreenimageurl' = $LockScreenImageUrl
}
if (-not $LockScreenOnly) { $definitions['device_vendor_msft_personalization_desktopimageurl'] = $DesktopImageUrl }

# Make sure the settings catalog still has these setting ids before writing anything.
foreach ($defId in $definitions.Keys) {
    try { Invoke-ClimbGraph -Path "deviceManagement/configurationSettings('$defId')" | Out-Null }
    catch { throw "The settings catalog has no setting '$defId'. Microsoft may have renamed it: search 'Personalization' in the settings picker and update this script." }
}

$settings = @(foreach ($defId in $definitions.Keys) {
        @{
            '@odata.type'   = '#microsoft.graph.deviceManagementConfigurationSetting'
            settingInstance = @{
                '@odata.type'       = '#microsoft.graph.deviceManagementConfigurationSimpleSettingInstance'
                settingDefinitionId = $defId
                simpleSettingValue  = @{
                    '@odata.type' = '#microsoft.graph.deviceManagementConfigurationStringSettingValue'
                    value         = $definitions[$defId]
                }
            }
        }
    })

$name = Get-ClimbName 'Windows - Desktop and lock screen wallpaper'
$body = @{
    name            = $name
    description     = "Brand wallpaper ($Brand, $Design). Managed by 20-Windows-Wallpapers.ps1."
    platforms       = 'windows10'
    technologies    = 'mdm'
    roleScopeTagIds = @('0')
    settings        = $settings
}

$id = Set-ClimbObject -Collection 'deviceManagement/configurationPolicies' -Name $name -NameProperty name -Body $body -UsePut -WhatIf:$WhatIfPreference
$targets = Get-ClimbAssignmentTargets -Target $Target -GroupName $GroupName
Set-ClimbAssignment -Collection 'deviceManagement/configurationPolicies' -Id $id -Name $name -Kind configurationPolicy -Targets $targets -WhatIf:$WhatIfPreference

Write-ClimbStep 'Done. The new picture shows after the next sync; the lock screen can need a restart.'
