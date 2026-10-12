<#
.SYNOPSIS
    Brands the Company Portal and Intune apps (Windows, macOS, iOS, Android and the website).

.DESCRIPTION
    Updates the tenant's default Company Portal branding profile
    (Tenant administration > Customization): organisation name, theme colour, the logo on
    the theme colour, the logo on light backgrounds and the brand image on the profile page.
    Logos come from the public brand pack on GitHub; the brand image is a brand centre
    wallpaper. Only the fields below change; support contacts and privacy text stay as they are
    unless you pass them.

.PARAMETER OrganizationName
    Shown in the apps. Default: ClimbGroup (the company people work for). Max 40 characters.
.PARAMETER Brand
    Whose logos to show: ClimbGroup (default) or ClimbUK.
.PARAMETER ThemeColor
    Hex colour. Default #C55308, the brand accent that keeps white text at 4.5:1 or better.
.PARAMETER ContactEmail
    IT contact email shown in the apps (optional).
.PARAMETER ContactName
    IT contact name (optional).
.PARAMETER WebsiteUrl
    Support website URL (optional).

.EXAMPLE
    pwsh ./40-CompanyPortal-Branding.ps1 -WhatIf
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [ValidateLength(1, 40)][string]$OrganizationName = 'ClimbGroup',
    [ValidateSet('ClimbGroup', 'ClimbUK')][string]$Brand = 'ClimbGroup',
    [ValidatePattern('^#?[0-9A-Fa-f]{6}$')][string]$ThemeColor = '#C55308',
    [string]$ContactEmail,
    [string]$ContactName,
    [string]$WebsiteUrl,
    [string]$TenantId,
    [switch]$UseDeviceCode
)

$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'ClimbIntune.psm1') -Force
Connect-ClimbGraph -TenantId $TenantId -UseDeviceCode:$UseDeviceCode

$raw = "https://raw.githubusercontent.com/Climb-Group/Brand-System/main/logos/$Brand/PNG"
function Get-Mime([string]$Url, [long]$MaxBytes) {
    $path = Get-ClimbDownload -Url $Url
    $bytes = [IO.File]::ReadAllBytes($path)
    if ($bytes.Length -ge $MaxBytes) { throw "$Url is $($bytes.Length) bytes; the limit is $MaxBytes." }
    $type = if ($Url -match '\.png$') { 'image/png' } else { 'image/jpeg' }
    return @{ '@odata.type' = '#microsoft.graph.mimeContent'; type = $type; value = [Convert]::ToBase64String($bytes) }
}

$hex = $ThemeColor.TrimStart('#')
$body = @{
    displayName                = $OrganizationName
    themeColor                 = @{ r = [Convert]::ToInt32($hex.Substring(0, 2), 16); g = [Convert]::ToInt32($hex.Substring(2, 2), 16); b = [Convert]::ToInt32($hex.Substring(4, 2), 16) }
    showLogo                   = $true
    showDisplayNameNextToLogo  = $false
    themeColorLogo             = Get-Mime "$raw/${Brand}_mono-white_1024.png" 750KB
    lightBackgroundLogo        = Get-Mime "$raw/${Brand}_full-colour-light_1024.png" 750KB
    landingPageCustomizedImage = Get-Mime (Get-ClimbBrandFileUrl (Get-ClimbWallpaperFile -Brand $Brand -Design 'stage-light' -Kind desktop -Size '2560x1440')) 1300KB
}
if ($ContactEmail) { $body.contactITEmailAddress = $ContactEmail }
if ($ContactName) { $body.contactITName = $ContactName }
if ($WebsiteUrl) { $body.onlineSupportSiteUrl = $WebsiteUrl; $body.onlineSupportSiteName = 'Help' }

$default = @(Invoke-ClimbGraph -Path 'deviceManagement/intuneBrandingProfiles' | Where-Object { $_.isDefaultProfile })
if ($default.Count -ne 1) { throw "Expected one default branding profile, found $($default.Count)." }
Write-ClimbStep "Updating the default Company Portal branding: $OrganizationName, #$hex, $Brand logos"
Invoke-ClimbWrite -Method PATCH -Path "deviceManagement/intuneBrandingProfiles/$($default[0].id)" -Body $body -Description 'Update default Company Portal branding' -WhatIf:$WhatIfPreference | Out-Null

Write-ClimbStep 'Done. The apps show it the next time they open (the website straight away).'
