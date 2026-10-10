<#
.SYNOPSIS
Builds the ClimbUK brand centre on the SharePoint brand center site.

.DESCRIPTION
Adds only: new pages, new document libraries, and files. It never deletes anything and never changes an existing
page: a page whose name is already taken is skipped and reported.

By default it uploads the brand book (brand-book/) and the page images, PDFs and Office templates, and builds one
page, brand.aspx, that shows the brand book full width through the ClimbUK brand book web part: the same pages,
menus, search, themes and live components as the brand centre on the website.

Changes to the tenant and the existing site are opt in:
  -InstallApp     adds the ClimbUK brand book web part (app/climb-brand-page.sppkg) to the tenant app catalog and
                  makes it available on every site. Needs a SharePoint or Global Administrator. Run it once, before
                  the page can show the brand book.
  -TextPages      also builds the twelve plain SharePoint pages (brand-centre.aspx, our-brand.aspx and so on)
  -SetSiteLook    adds the ClimbUK theme to the tenant and applies it here (needs a SharePoint Administrator), then
                  sets the site logo, the extended header with its background, and the footer
  -SetNavigation  adds the brand book menus to the top navigation (existing links stay)
  -SetHomePage    makes brand.aspx (-BrandPageName) the site home page; the old home page stays in Site Pages
  -Publish        publishes the new pages (otherwise they stay as drafts only editors see)

Needs PowerShell 7.4 or later and PnP.PowerShell 3 (Install-Module PnP.PowerShell -Scope CurrentUser), plus an
Entra app registration for PnP sign in (see README.md, step 1).

.EXAMPLE
./build-brand-centre.ps1 -SiteUrl https://contoso.sharepoint.com/sites/BrandGuide -ClientId <app id> `
  -MarketingContentUrl https://contoso.sharepoint.com/sites/Marketing `
  -PhotoLibraryUrl https://contoso.sharepoint.com/sites/Photos -PackPath ~/Brand-System -InstallApp
#>
param(
    [Parameter(Mandatory)][string]$SiteUrl,
    [Parameter(Mandatory)][string]$ClientId,
    [Parameter(Mandatory)][string]$MarketingContentUrl,
    [Parameter(Mandatory)][string]$PhotoLibraryUrl,
    [string]$PackPath,
    [string]$BrandPageName = "brand",
    [string]$HomePageName = "brand-centre",
    [string]$PackUrl = "https://github.com/Climb-Group/Brand-System/archive/refs/heads/main.zip",
    [switch]$InstallApp,
    [switch]$TextPages,
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

# 3. The brand book: every page, picture, font, style and script, in its own folder.
$bookRoot = Join-Path $here "brand-book"
$bookFolder = "$img/book"
$n = 0
foreach ($f in Get-ChildItem $bookRoot -Recurse -File) {
    $sub = [System.IO.Path]::GetRelativePath($bookRoot, $f.DirectoryName).Replace("\", "/")
    $folder = if ($sub -eq ".") { $bookFolder } else { "$bookFolder/$sub" }
    Add-PnPFile -Path $f.FullName -Folder $folder | Out-Null
    $n++
}
Write-Host "Uploaded the brand book ($n files)"

# 4. PDFs and Office templates from a local copy of the brand pack.
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

# 5. The brand book web part, once per tenant.
$webPartId = "ba7831b6-7e3c-4201-ae39-39617ced1e61"
if ($InstallApp) {
    $catalog = Get-PnPTenantAppCatalogUrl
    if (-not $catalog) {
        Write-Warning "This tenant has no app catalog yet. Create it in the SharePoint admin centre (More features > Apps > Open), then run again with -InstallApp."
    }
    else {
        Add-PnPApp -Path (Join-Path $here "app/climb-brand-page.sppkg") -Scope Tenant -Publish -SkipFeatureDeployment -Overwrite | Out-Null
        Write-Host "Added the ClimbUK brand book web part to the app catalog ($catalog)"
    }
}

# 6. The brand book page.
$made = @()
if (PageExists $BrandPageName) {
    Write-Warning "Skipped $BrandPageName.aspx: a page with that name already exists. Nothing on it was changed."
}
else {
    Add-PnPPage -Name $BrandPageName -LayoutType Home | Out-Null
    Set-PnPPage -Identity $BrandPageName -Title "Brand centre" -ThumbnailUrl "$rel/$img/banners/climbuk_sharepoint-banner_home_1920x1080.jpg" | Out-Null
    Add-PnPPageSection -Page $BrandPageName -SectionTemplate OneColumnFullWidth | Out-Null
    try {
        Add-PnPPageWebPart -Page $BrandPageName -Component $webPartId -Section 1 -Column 1 `
            -WebPartProperties @{ page = "index"; bookUrl = "" } | Out-Null
    }
    catch {
        Write-Warning "Built $BrandPageName.aspx without the brand book: the web part is not installed yet. Run once with -InstallApp, then delete $BrandPageName.aspx by hand and run again."
    }
    if ($Publish) { Set-PnPPage -Identity $BrandPageName -Publish | Out-Null }
    $made += $BrandPageName
    Write-Host "Built $BrandPageName.aspx"
}

# 7. The plain SharePoint pages, only when asked.
foreach ($p in $(if ($TextPages) { $data.pages } else { @() })) {
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

# 8. Opt in: site look, navigation, home page.
if ($SetSiteLook) {
    $palette = @{}
    $data.theme.palette.PSObject.Properties | ForEach-Object { $palette[$_.Name] = $_.Value }
    Add-PnPTenantTheme -Identity $data.theme.name -Palette $palette -IsInverted $false -Overwrite | Out-Null
    Set-PnPWebTheme -Theme $data.theme.name | Out-Null
    Write-Host "Added and applied the $($data.theme.name) theme"
    Set-PnPWebHeader -SiteLogoUrl "$rel/$img/site/climbuk_sharepoint-site_logo_192x192.png" `
        -SiteThumbnailUrl "$rel/$img/site/climbuk_sharepoint-site_logo_192x192.png" `
        -HeaderLayout Extended -HeaderEmphasis Strong -LogoAlignment Left `
        -HeaderBackgroundImageUrl "$rel/$img/site/climbuk_sharepoint-site_header-background_2560x164.jpg" | Out-Null
    Set-PnPFooter -Enabled:$true -Layout Extended -BackgroundTheme Strong -Title "The Festival for Business Growth" `
        -LogoUrl "$rel/$img/site/climbuk_sharepoint-site_footer-logo_480x160.png" | Out-Null
    Write-Host "Set the site logo, header and footer"
}
if ($SetNavigation) {
    $brandUrl = "$SiteUrl/SitePages/$BrandPageName.aspx"
    foreach ($g in $data.booknav) {
        $parent = Add-PnPNavigationNode -Location TopNavigationBar -Title $g.label -Url "http://linkless.header/"
        foreach ($l in $g.links) {
            Add-PnPNavigationNode -Location TopNavigationBar -Title $l.title -Url "$($brandUrl)?brandpage=$($l.page)" -Parent $parent.Id | Out-Null
        }
    }
    $files = Add-PnPNavigationNode -Location TopNavigationBar -Title "Files" -Url "http://linkless.header/"
    Add-PnPNavigationNode -Location TopNavigationBar -Title "Marketing content" -Url $MarketingContentUrl -Parent $files.Id | Out-Null
    Add-PnPNavigationNode -Location TopNavigationBar -Title "Photo library" -Url $PhotoLibraryUrl -Parent $files.Id | Out-Null
    Add-PnPNavigationNode -Location TopNavigationBar -Title "Brand guidelines (PDF)" -Url "$SiteUrl/BrandFiles" -Parent $files.Id | Out-Null
    Add-PnPNavigationNode -Location TopNavigationBar -Title "Office templates" -Url "$SiteUrl/BrandTemplates" -Parent $files.Id | Out-Null
    Write-Host "Added the brand book menus and a Files menu to the top navigation"
}
if ($SetHomePage) {
    Set-PnPHomePage -RootFolderRelativeUrl "SitePages/$BrandPageName.aspx" | Out-Null
    Write-Host "Set $BrandPageName.aspx as the site home page"
}

Write-Host ""
Write-Host "Done. Built: $($made -join ', ')"
if ($TextPages) { Write-Host "Next: add the Hero web part to $HomePageName.aspx and a Quick links row to each page (README.md)." }
Write-Host "A SharePoint admin registers the template library so it shows in Word, Excel and PowerPoint:"
Write-Host "  Add-PnPOrgAssetsLibrary -LibraryUrl $SiteUrl/BrandTemplates -OrgAssetType OfficeTemplateLibrary"
