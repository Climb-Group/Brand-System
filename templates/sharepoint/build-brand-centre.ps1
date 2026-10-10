<#
.SYNOPSIS
Builds the ClimbUK brand centre pages on the SharePoint brand center site.

.DESCRIPTION
Adds only: new pages, new document libraries, and files (banners, tiles, PDFs, Office templates). It never
deletes anything and never changes an existing page: a page whose name is already taken is skipped and reported.

Changes to the existing site are opt in:
  -SetSiteLook    site logo, extended header with its background, and the footer
  -SetNavigation  adds the brand centre menus to the top navigation (existing links stay)
  -SetHomePage    makes the new home page (-HomePageName, default brand-centre.aspx) the site home page;
                  the old home page stays in Site Pages
  -Publish        publishes the new pages (otherwise they stay as drafts only editors see)

Needs PowerShell 7.4 or later and PnP.PowerShell 3 (Install-Module PnP.PowerShell -Scope CurrentUser), plus an
Entra app registration for PnP sign in (see README.md, step 1).

.EXAMPLE
./build-brand-centre.ps1 -SiteUrl https://contoso.sharepoint.com/sites/BrandGuide -ClientId <app id> `
  -MarketingContentUrl https://contoso.sharepoint.com/sites/Marketing `
  -PhotoLibraryUrl https://contoso.sharepoint.com/sites/Photos -PackPath ~/Brand-System
#>
param(
    [Parameter(Mandatory)][string]$SiteUrl,
    [Parameter(Mandatory)][string]$ClientId,
    [Parameter(Mandatory)][string]$MarketingContentUrl,
    [Parameter(Mandatory)][string]$PhotoLibraryUrl,
    [string]$PackPath,
    [string]$HomePageName = "brand-centre",
    [string]$PackUrl = "https://github.com/Climb-Group/Brand-System/archive/refs/heads/main.zip",
    [switch]$Publish,
    [switch]$SetHomePage,
    [switch]$SetNavigation,
    [switch]$SetSiteLook
)
$ErrorActionPreference = "Stop"
$here = $PSScriptRoot
$SiteUrl = $SiteUrl.TrimEnd("/")

Connect-PnPOnline -Url $SiteUrl -Interactive -ClientId $ClientId
$rel = (Get-PnPWeb).ServerRelativeUrl.TrimEnd("/")
$data = Get-Content (Join-Path $here "pages.json") -Raw | ConvertFrom-Json

function PageExists([string]$name) {
    try { return [bool](Get-PnPPage -Identity $name -ErrorAction Stop) } catch { return $false }
}

function Expand([string]$html) {
    $html.Replace("{SITE}", $SiteUrl).Replace("{A}", $MarketingContentUrl).Replace("{B}", $PhotoLibraryUrl).Replace("{P}", $PackUrl)
}

# 1. Libraries: Site Assets (page images), Brand files (PDFs), Brand templates (Office templates), Brand Office fonts.
foreach ($lib in @(@{T = "Site Assets"; U = "SiteAssets" }, @{T = "Brand files"; U = "BrandFiles" }, @{T = "Brand templates"; U = "BrandTemplates" }, @{T = "Brand Office fonts"; U = "BrandOfficeFonts" })) {
    if (-not (Get-PnPList -Identity $lib.U -ErrorAction SilentlyContinue)) {
        if (-not (Get-PnPList -Identity $lib.T -ErrorAction SilentlyContinue)) {
            New-PnPList -Title $lib.T -Url $lib.U -Template DocumentLibrary | Out-Null
            Write-Host "Created library $($lib.T)"
        }
    }
}

# 2. Images for pages, tiles and the site header.
$img = "SiteAssets/BrandCentre"
foreach ($folder in "banners", "quick-link-tiles", "section-backgrounds", "site") {
    foreach ($f in Get-ChildItem (Join-Path $here $folder) -File) {
        Add-PnPFile -Path $f.FullName -Folder "$img/$folder" | Out-Null
    }
    Write-Host "Uploaded $folder"
}

# 3. PDFs and Office templates from a local copy of the brand pack.
if ($PackPath) {
    foreach ($f in Get-ChildItem (Join-Path $PackPath "pdf") -Recurse -Filter *.pdf) {
        Add-PnPFile -Path $f.FullName -Folder "BrandFiles" | Out-Null
    }
    foreach ($brand in "ClimbUK", "Climb27", "ClimbGroup") {
        $src = Join-Path $PackPath "templates/office/$brand"
        foreach ($f in Get-ChildItem $src -Recurse -Include *.dotx, *.potx, *.xltx) {
            Add-PnPFile -Path $f.FullName -Folder "BrandTemplates/$brand" | Out-Null
        }
    }
    Write-Host "Uploaded brand guidelines and Office templates"
}
else {
    Write-Warning "No -PackPath: upload the PDFs to Brand files and the Office templates to Brand templates by hand."
}

# 4. Pages.
$made = @()
foreach ($p in $data.pages) {
    $name = if ($p.slug -eq "home" ) { $HomePageName } else { $p.slug }
    if (PageExists $name) {
        Write-Warning "Skipped $name.aspx: a page with that name already exists. Nothing on it was changed."
        continue
    }
    $banner = "$rel/$img/banners/$($p.banner)"
    if ($p.slug -eq "home" ) {
        Add-PnPPage -Name $name -LayoutType Home | Out-Null
    }
    else {
        Add-PnPPage -Name $name -LayoutType Article -HeaderLayoutType FullWidthImage | Out-Null
        Set-PnPPage -Identity $name -HeaderType Custom -ServerRelativeImageUrl $banner -TranslateX 0 -TranslateY 0 | Out-Null
    }
    Set-PnPPage -Identity $name -Title $p.title -ThumbnailUrl $banner | Out-Null
    $i = 0
    foreach ($s in $p.sections) {
        $i++
        Add-PnPPageSection -Page $name -SectionTemplate $s.layout -ZoneEmphasis $s.emphasis | Out-Null
        $c = 0
        foreach ($html in $s.columns) {
            $c++
            Add-PnPPageTextPart -Page $name -Section $i -Column $c -Text (Expand $html) | Out-Null
        }
    }
    try {
        $item = Get-PnPListItem -List "SitePages" -Query "<View><Query><Where><Eq><FieldRef Name='FileLeafRef'/><Value Type='Text'>$name.aspx</Value></Eq></Where></Query></View>"
        Set-PnPListItem -List "SitePages" -Identity $item.Id -Values @{ Description = $p.description } -UpdateType SystemUpdate | Out-Null
    }
    catch { Write-Warning "Could not set the description on $name.aspx: $($_.Exception.Message)" }
    if ($Publish) { Set-PnPPage -Identity $name -Publish | Out-Null }
    $made += $name
    Write-Host "Built $name.aspx"
}

# 5. Opt in: site look, navigation, home page.
if ($SetSiteLook) {
    Set-PnPWebHeader -SiteLogoUrl "$rel/$img/site/climbuk_sharepoint-site_logo_192x192.png" `
        -SiteThumbnailUrl "$rel/$img/site/climbuk_sharepoint-site_logo_192x192.png" `
        -HeaderLayout Extended -HeaderEmphasis Strong -LogoAlignment Left `
        -HeaderBackgroundImageUrl "$rel/$img/site/climbuk_sharepoint-site_header-background_2560x164.jpg" | Out-Null
    Set-PnPFooter -Enabled:$true -Layout Extended -BackgroundTheme Strong -Title "The Festival for Business Growth" `
        -LogoUrl "$rel/$img/site/climbuk_sharepoint-site_footer-logo_480x160.png" | Out-Null
    Write-Host "Set the site logo, header and footer"
}
if ($SetNavigation) {
    foreach ($g in $data.nav) {
        if ($g.pages.Count -eq 1) {
            Add-PnPNavigationNode -Location TopNavigationBar -Title $g.label -Url "$SiteUrl/SitePages/$($g.pages[0]).aspx" | Out-Null
            continue
        }
        $parent = Add-PnPNavigationNode -Location TopNavigationBar -Title $g.label -Url "http://linkless.header/"
        foreach ($slug in $g.pages) {
            $title = ($data.pages | Where-Object slug -eq $slug).title
            Add-PnPNavigationNode -Location TopNavigationBar -Title $title -Url "$SiteUrl/SitePages/$slug.aspx" -Parent $parent.Id | Out-Null
        }
    }
    Write-Host "Added the brand centre menus to the top navigation"
}
if ($SetHomePage) {
    Set-PnPHomePage -RootFolderRelativeUrl "SitePages/$HomePageName.aspx" | Out-Null
    Write-Host "Set $HomePageName.aspx as the site home page"
}

Write-Host ""
Write-Host "Done. Built: $($made -join ', ')"
Write-Host "Next: add the Hero web part to $HomePageName.aspx and a Quick links row to each page (README.md, step 4)."
Write-Host "A SharePoint admin registers the template library so it shows in Word, Excel and PowerPoint:"
Write-Host "  Add-SPOOrgAssetsLibrary -LibraryUrl $SiteUrl/BrandTemplates -OrgAssetType OfficeTemplateLibrary"
