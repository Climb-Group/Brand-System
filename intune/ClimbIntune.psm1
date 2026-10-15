<#
.SYNOPSIS
    Shared helpers for the Climb Intune branding scripts.

.DESCRIPTION
    Every script in this folder imports this module. It signs in to Microsoft Graph,
    finds existing Intune objects by name so re-runs update instead of duplicating,
    resolves the brand files from the public brand centre and the templates release,
    and wraps every write in ShouldProcess so -WhatIf shows the plan and changes nothing.

    Needs PowerShell 7.2 or later and the Microsoft.Graph.Authentication module.
    Only Invoke-MgGraphRequest is used, against the Graph beta endpoint, because most
    Intune objects (remediations, shell scripts, settings catalog, branding) are beta only.
#>

Set-StrictMode -Version 3.0

$script:Graph = 'https://graph.microsoft.com/beta'
$script:Prefix = 'Climb - '
$script:BrandCentre = 'https://www.climb-uk.com'
$script:TemplatesRepo = 'Climb-Group/Brand-System'
$script:Manifest = $null

$script:Scopes = @(
    'DeviceManagementConfiguration.ReadWrite.All',  # settings catalog, device configurations, remediations
    'DeviceManagementScripts.ReadWrite.All',        # macOS shell scripts
    'DeviceManagementApps.ReadWrite.All',           # Company Portal branding
    'Group.Read.All'                                # resolve assignment groups by name
)

function Write-ClimbStep {
    param([Parameter(Mandatory)][string]$Message)
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Connect-ClimbGraph {
    <#
    .SYNOPSIS
        Signs in to Graph with the scopes these scripts need. Reuses an existing session.
    .PARAMETER TenantId
        Tenant id or domain, for example contoso.onmicrosoft.com. Default: the home tenant of the account.
    .PARAMETER UseDeviceCode
        Sign in with a device code (useful on Linux without a desktop browser).
    .PARAMETER ExtraScopes
        Scopes one script needs on top of the shared set, for example Sites.Read.All.
    #>
    [CmdletBinding()]
    param(
        [string]$TenantId,
        [switch]$UseDeviceCode,
        [string[]]$ExtraScopes
    )
    if (-not (Get-Module -ListAvailable -Name Microsoft.Graph.Authentication)) {
        throw 'Microsoft.Graph.Authentication is not installed. Run 00-Prerequisites.ps1 first.'
    }
    Import-Module Microsoft.Graph.Authentication -ErrorAction Stop
    $scopes = @($script:Scopes) + @($ExtraScopes | Where-Object { $_ })
    $ctx = Get-MgContext
    $missing = if ($ctx) { $scopes | Where-Object { $_ -notin $ctx.Scopes } } else { $scopes }
    if (-not $ctx -or $missing) {
        $params = @{ Scopes = $scopes; NoWelcome = $true }
        if ($TenantId) { $params.TenantId = $TenantId }
        if ($UseDeviceCode) { $params.UseDeviceCode = $true }
        Connect-MgGraph @params | Out-Null
        $ctx = Get-MgContext
    }
    Write-ClimbStep "Signed in as $($ctx.Account) to tenant $($ctx.TenantId)"
}

function Invoke-ClimbGraph {
    <#
    .SYNOPSIS
        Calls Graph beta. Follows paging on GET collections.
    #>
    [CmdletBinding()]
    param(
        [ValidateSet('GET', 'POST', 'PATCH', 'PUT', 'DELETE')][string]$Method = 'GET',
        [Parameter(Mandatory)][string]$Path,
        $Body
    )
    $uri = if ($Path -like 'https://*') { $Path } else { "$script:Graph/$($Path.TrimStart('/'))" }
    $params = @{ Method = $Method; Uri = $uri; OutputType = 'PSObject' }
    if ($null -ne $Body) {
        $params.Body = ($Body | ConvertTo-Json -Depth 20 -Compress)
        $params.ContentType = 'application/json'
    }
    $result = Invoke-MgGraphRequest @params
    if ($Method -eq 'GET' -and $result -and ($result.PSObject.Properties.Name -contains 'value')) {
        $items = @($result.value)
        while ($result.PSObject.Properties.Name -contains '@odata.nextLink' -and $result.'@odata.nextLink') {
            $result = Invoke-MgGraphRequest -Method GET -Uri $result.'@odata.nextLink' -OutputType PSObject
            $items += @($result.value)
        }
        return $items
    }
    return $result
}

function Invoke-ClimbWrite {
    <#
    .SYNOPSIS
        A Graph write guarded by ShouldProcess. With -WhatIf it prints the request and returns $null.
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)][ValidateSet('POST', 'PATCH', 'PUT', 'DELETE')][string]$Method,
        [Parameter(Mandatory)][string]$Path,
        $Body,
        [Parameter(Mandatory)][string]$Description
    )
    if ($PSCmdlet.ShouldProcess($Description, "$Method $Path")) {
        return Invoke-ClimbGraph -Method $Method -Path $Path -Body $Body
    }
    if ($null -ne $Body) {
        $preview = $Body | ConvertTo-Json -Depth 20
        if ($preview.Length -gt 4000) { $preview = $preview.Substring(0, 4000) + "`n... (truncated)" }
        Write-Host $preview -ForegroundColor DarkGray
    }
    return $null
}

function Get-ClimbObject {
    <#
    .SYNOPSIS
        Finds one Intune object by its display name in a collection, or $null.
    .PARAMETER Collection
        For example deviceManagement/deviceHealthScripts.
    .PARAMETER NameProperty
        displayName for most collections, name for configurationPolicies.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Collection,
        [Parameter(Mandatory)][string]$Name,
        [string]$NameProperty = 'displayName'
    )
    $all = Invoke-ClimbGraph -Path "$Collection`?`$select=id,$NameProperty"
    $found = @($all | Where-Object { $_.$NameProperty -eq $Name })
    if ($found.Count -gt 1) { throw "More than one object called '$Name' in $Collection. Delete the extra ones in the Intune admin center and run again." }
    if ($found.Count -eq 1) { return $found[0] }
    return $null
}

function Get-ClimbAssignmentTargets {
    <#
    .SYNOPSIS
        Builds Graph assignment targets.
    .PARAMETER Target
        AllDevices, AllUsers, or Group (then GroupName is required).
    .PARAMETER GroupName
        One or more Entra group display names.
    #>
    [CmdletBinding()]
    param(
        [ValidateSet('AllDevices', 'AllUsers', 'Group', 'None')][string]$Target = 'AllDevices',
        [string[]]$GroupName
    )
    switch ($Target) {
        'None' { return @() }
        'AllDevices' { return @(@{ '@odata.type' = '#microsoft.graph.allDevicesAssignmentTarget' }) }
        'AllUsers' { return @(@{ '@odata.type' = '#microsoft.graph.allLicensedUsersAssignmentTarget' }) }
        'Group' {
            if (-not $GroupName) { throw '-GroupName is required with -Target Group.' }
            foreach ($g in $GroupName) {
                $escaped = $g.Replace("'", "''")
                $hits = @(Invoke-ClimbGraph -Path "https://graph.microsoft.com/v1.0/groups?`$filter=displayName eq '$escaped'&`$select=id,displayName")
                if ($hits.Count -ne 1) { throw "Expected one Entra group called '$g', found $($hits.Count)." }
                @{ '@odata.type' = '#microsoft.graph.groupAssignmentTarget'; groupId = $hits[0].id }
            }
        }
    }
}

function Get-ClimbBrandManifest {
    <#
    .SYNOPSIS
        Reads the public brand centre manifest (every published file with its download URL).
    #>
    [CmdletBinding()]
    param()
    if (-not $script:Manifest) {
        $script:Manifest = Invoke-RestMethod -Uri "$script:BrandCentre/brand/manifest.json" -ErrorAction Stop
    }
    return $script:Manifest
}

function Get-ClimbBrandFileUrl {
    <#
    .SYNOPSIS
        Returns the public HTTPS URL of a brand centre file by its file name, for example
        climbuk_desktop_stage-light_3840x2160.jpg.
    #>
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$FileName)
    $manifest = Get-ClimbBrandManifest
    $hit = @($manifest.files | Where-Object { ($_.path -split '/')[-1] -eq $FileName -or $_.url -like "*/$FileName" })
    if ($hit.Count -eq 0) {
        throw "The brand centre has no file called $FileName. Check $script:BrandCentre/brand/wallpapers for the names, or pass -ImageUrl."
    }
    return $hit[0].url
}

function Get-ClimbWallpaperFile {
    <#
    .SYNOPSIS
        Builds the brand centre file name of a wallpaper, for example
        climbuk_desktop_stage-light_3840x2160.jpg.
    .PARAMETER Brand
        ClimbUK, ClimbGroup or Climb27. ClimbGroup has no phone set, so phones fall back to ClimbUK.
    .PARAMETER Design
        stage-light, ascent, connections or contours.
    .PARAMETER Kind
        desktop or phone.
    .PARAMETER Size
        desktop: 2560x1440, 3840x2160 or 5120x2880. phone: 1179x2556 or 1440x3120.
    #>
    [CmdletBinding()]
    param(
        [ValidateSet('ClimbUK', 'ClimbGroup', 'Climb27')][string]$Brand = 'ClimbUK',
        [ValidateSet('stage-light', 'ascent', 'connections', 'contours')][string]$Design = 'stage-light',
        [Parameter(Mandatory)][ValidateSet('desktop', 'phone')][string]$Kind,
        [string]$Size
    )
    if (-not $Size) { $Size = if ($Kind -eq 'desktop') { '3840x2160' } else { '1179x2556' } }
    $b = $Brand.ToLowerInvariant()
    if ($Kind -eq 'phone' -and $b -eq 'climbgroup') {
        Write-Warning 'ClimbGroup has no phone wallpapers; using the ClimbUK one.'
        $b = 'climbuk'
    }
    return "${b}_${Kind}_${Design}_${Size}.jpg"
}

function Get-ClimbTemplatesRelease {
    <#
    .SYNOPSIS
        Returns version, URL and SHA-256 of the templates install package from the public
        GitHub release (latest templates-v* release unless -Version is given).
    #>
    [CmdletBinding()]
    param([string]$Version)
    $releases = Invoke-RestMethod -Uri "https://api.github.com/repos/$script:TemplatesRepo/releases?per_page=50" -Headers @{ 'User-Agent' = 'climb-intune' }
    $templates = $releases | Where-Object { $_.tag_name -like 'templates-v*' -and -not $_.draft -and -not $_.prerelease }
    $release = if ($Version) { $templates | Where-Object { $_.tag_name -eq "templates-v$Version" } | Select-Object -First 1 }
               else { $templates | Sort-Object { [version]($_.tag_name -replace '^templates-v', '') } -Descending | Select-Object -First 1 }
    if (-not $release) { throw "No templates release found$(if ($Version) { " for $Version" })." }
    $v = $release.tag_name -replace '^templates-v', ''
    $asset = $release.assets | Where-Object { $_.name -eq "Climb-Templates-$v.zip" } | Select-Object -First 1
    if (-not $asset) { throw "Release $($release.tag_name) has no Climb-Templates-$v.zip." }
    $sha = if ($asset.PSObject.Properties.Name -contains 'digest' -and $asset.digest -like 'sha256:*') { $asset.digest.Substring(7) } else { $null }
    if (-not $sha) {
        # Older releases have no digest: hash a download once here.
        $tmp = Join-Path ([IO.Path]::GetTempPath()) $asset.name
        Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $tmp
        $sha = (Get-FileHash -Algorithm SHA256 -Path $tmp).Hash.ToLowerInvariant()
        Remove-Item $tmp -Force
    }
    [pscustomobject]@{ Version = $v; Url = $asset.browser_download_url; Sha256 = $sha.ToLowerInvariant(); Size = $asset.size }
}

function Get-ClimbDownload {
    <#
    .SYNOPSIS
        Downloads a URL to a temp file and returns the path.
    #>
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$Url)
    $name = [IO.Path]::GetFileName(([uri]$Url).AbsolutePath)
    if (-not $name) { $name = [guid]::NewGuid().ToString() }
    $dir = Join-Path ([IO.Path]::GetTempPath()) 'climb-intune'
    # Local temp files are not tenant changes, so they are written under -WhatIf too.
    New-Item -ItemType Directory -Force -Path $dir -WhatIf:$false | Out-Null
    $out = Join-Path $dir $name
    Invoke-WebRequest -Uri $Url -OutFile $out -ErrorAction Stop
    return $out
}

function ConvertTo-ClimbBase64 {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$Text)
    [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($Text))
}

function Set-ClimbObject {
    <#
    .SYNOPSIS
        Creates or updates an Intune object by name and returns its id ($null under -WhatIf when new).
    .PARAMETER Collection
        For example deviceManagement/deviceConfigurations.
    .PARAMETER Body
        The full object. For updates the same body is sent with PATCH (or PUT when -UsePut).
    .PARAMETER UsePut
        Settings catalog policies replace their settings with PUT.
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)][string]$Collection,
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][hashtable]$Body,
        [string]$NameProperty = 'displayName',
        [switch]$UsePut
    )
    $existing = Get-ClimbObject -Collection $Collection -Name $Name -NameProperty $NameProperty
    if ($existing) {
        Write-ClimbStep "Updating '$Name'"
        $method = if ($UsePut) { 'PUT' } else { 'PATCH' }
        Invoke-ClimbWrite -Method $method -Path "$Collection/$($existing.id)" -Body $Body -Description "Update '$Name'" -WhatIf:$WhatIfPreference | Out-Null
        return $existing.id
    }
    Write-ClimbStep "Creating '$Name'"
    $created = Invoke-ClimbWrite -Method POST -Path $Collection -Body $Body -Description "Create '$Name'" -WhatIf:$WhatIfPreference
    if ($created) { return $created.id }
    return $null
}

function Set-ClimbAssignment {
    <#
    .SYNOPSIS
        Replaces an object's assignments through its assign action.
    .PARAMETER Kind
        Which body shape the assign action takes.
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)][string]$Collection,
        [string]$Id,
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][ValidateSet('deviceConfiguration', 'configurationPolicy', 'healthScript', 'shellScript')][string]$Kind,
        [Parameter(Mandatory)][AllowEmptyCollection()][object[]]$Targets,
        [hashtable]$RunSchedule
    )
    if (-not $Targets -or $Targets.Count -eq 0) { Write-ClimbStep "Leaving '$Name' unassigned"; return }
    $body = switch ($Kind) {
        'deviceConfiguration' { @{ assignments = @($Targets | ForEach-Object { @{ target = $_ } }) } }
        'configurationPolicy' { @{ assignments = @($Targets | ForEach-Object { @{ target = $_ } }) } }
        'healthScript' {
            @{ deviceHealthScriptAssignments = @($Targets | ForEach-Object {
                        @{ target = $_; runRemediationScript = $true; runSchedule = $RunSchedule } }) }
        }
        'shellScript' { @{ deviceManagementScriptAssignments = @($Targets | ForEach-Object { @{ target = $_ } }) } }
    }
    $path = if ($Id) { "$Collection/$Id/assign" } else { "$Collection/<new id>/assign" }
    Write-ClimbStep "Assigning '$Name'"
    if (-not $Id -and -not $WhatIfPreference) { throw "No id for '$Name'; cannot assign." }
    Invoke-ClimbWrite -Method POST -Path $path -Body $body -Description "Assign '$Name'" -WhatIf:$WhatIfPreference | Out-Null
}

function Get-ClimbName {
    param([Parameter(Mandatory)][string]$Suffix)
    return "$script:Prefix$Suffix"
}

Export-ModuleMember -Function *-Climb*
