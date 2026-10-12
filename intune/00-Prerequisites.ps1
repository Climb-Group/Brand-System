<#
.SYNOPSIS
    Checks PowerShell, installs the Graph sign-in module for the current user, and signs in once.

.DESCRIPTION
    Run this first, from PowerShell 7 (pwsh) on any OS. It installs only
    Microsoft.Graph.Authentication (the scripts call Graph directly), then signs in
    with the scopes every other script needs, so you approve the consent once.

    The account needs the Intune Administrator role (or Global Administrator) and, the
    first time, must be able to consent to the Graph scopes for the Microsoft Graph
    Command Line Tools app.

.PARAMETER TenantId
    Tenant domain or id. Default: the home tenant of the account you sign in with.

.PARAMETER UseDeviceCode
    Sign in with a code at https://microsoft.com/devicelogin instead of a browser pop-up.

.EXAMPLE
    pwsh ./00-Prerequisites.ps1
.EXAMPLE
    pwsh ./00-Prerequisites.ps1 -UseDeviceCode
#>
[CmdletBinding()]
param(
    [string]$TenantId,
    [switch]$UseDeviceCode
)

$ErrorActionPreference = 'Stop'

if ($PSVersionTable.PSVersion -lt [version]'7.2') {
    throw "PowerShell 7.2 or later is needed (this is $($PSVersionTable.PSVersion)). Install it from https://aka.ms/powershell and run with pwsh."
}

if (-not (Get-Module -ListAvailable -Name Microsoft.Graph.Authentication)) {
    Write-Host 'Installing Microsoft.Graph.Authentication for the current user...'
    Install-Module Microsoft.Graph.Authentication -Scope CurrentUser -Repository PSGallery -Force -AllowClobber
}

Import-Module (Join-Path $PSScriptRoot 'ClimbIntune.psm1') -Force
Connect-ClimbGraph -TenantId $TenantId -UseDeviceCode:$UseDeviceCode

# Quick read checks: each confirms one permission works before anything is written.
$checks = [ordered]@{
    'Settings catalog policies' = 'deviceManagement/configurationPolicies?$top=1'
    'Device configurations'     = 'deviceManagement/deviceConfigurations?$top=1'
    'Remediations'              = 'deviceManagement/deviceHealthScripts?$top=1'
    'macOS shell scripts'       = 'deviceManagement/deviceShellScripts?$top=1'
    'Company Portal branding'   = 'deviceManagement/intuneBrandingProfiles?$top=1'
}
foreach ($k in $checks.Keys) {
    try {
        Invoke-ClimbGraph -Path $checks[$k] | Out-Null
        Write-Host ("  OK    {0}" -f $k) -ForegroundColor Green
    } catch {
        Write-Host ("  FAIL  {0}: {1}" -f $k, $_.Exception.Message) -ForegroundColor Red
    }
}

try {
    Invoke-RestMethod -Uri 'https://www.climb-uk.com/brand/manifest.json' | Out-Null
    Write-Host '  OK    Brand centre manifest' -ForegroundColor Green
} catch {
    Write-Host "  FAIL  Brand centre manifest: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nReady. Next: pwsh ./Run-All.ps1 -WhatIf"
