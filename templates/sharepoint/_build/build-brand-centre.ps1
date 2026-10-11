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
  -SetNavigation  adds the brand book menus to the menu bar the site shows (existing links stay)
  -ReplaceNavigation
                  saves both site menus to navigation-backup-<date>.json next to this script, removes every old link
                  from the menu bar, then adds Home and the brand book menus
  -SetHomePage    makes brand.aspx (-BrandPageName) the site home page; the old home page stays in Site Pages
  -RegisterOfficeLibraries
                  shares the site read only with everyone in the organisation (Microsoft 365 requires it), then
                  registers Brand templates and Brand Office fonts as organisation asset libraries, so the templates
                  show in Word, Excel and PowerPoint. Needs a SharePoint Administrator.
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
    [switch]$SetSiteLook,
    [switch]$RegisterOfficeLibraries,
    [switch]$ReplaceNavigation,
    [ValidateSet("Auto", "TopNavigationBar", "QuickLaunch")][string]$NavigationLocation = "Auto"
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
$solutionId = "05f5d231-1818-4b9c-a6c2-6f22bb68c843"
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

# 6. The brand book page. A brand.aspx this script made earlier (title "Brand centre") that does not show the brand
# book, because the web part was missing or empty, is cleared and given the web part. Any other page with that name
# is left alone.
$made = @()
function IsBook($control) { "$($control.WebPartId)".Trim("{", "}").ToLower() -eq $webPartId }
function BrandPage { try { return Get-PnPPage -Identity $BrandPageName -ErrorAction Stop } catch { return $null } }
function HasBook { $p = BrandPage; return [bool]($p -and @($p.Controls | Where-Object { IsBook $_ }).Count -gt 0) }
# The web part as SharePoint offers it on this site. Passing the object (not the id as text) to Add-PnPPageWebPart is
# what makes the page show it: an id the site does not offer yet adds an empty web part instead of failing.
function BookComponent {
    @(Get-PnPPageComponent -Page $BrandPageName -ListAvailable | Where-Object { "$($_.Id)".Trim("{", "}").ToLower() -eq $webPartId })[0]
}
$brandPage = BrandPage
$hasBook = HasBook
$ours = $brandPage -and $brandPage.PageTitle -eq "Brand centre"
if ($hasBook) {
    Write-Host "$BrandPageName.aspx already shows the brand book"
}
elseif ($brandPage -and -not $ours) {
    Write-Warning "Skipped $BrandPageName.aspx: a page with that name already exists and was not made by this script. Nothing on it was changed. Use -BrandPageName to build the brand book page under another name."
}
else {
    if (-not $brandPage) {
        Add-PnPPage -Name $BrandPageName -LayoutType Home | Out-Null
        Set-PnPPage -Identity $BrandPageName -Title "Brand centre" -ThumbnailUrl "$rel/$img/banners/climbuk_sharepoint-banner_home_1920x1080.jpg" | Out-Null
    }
    # A newly deployed app can take a few minutes to reach the site, so wait for it (up to 10 minutes).
    $component = BookComponent
    for ($try = 1; -not $component -and $try -le 20; $try++) {
        if ($try -eq 1) {
            Write-Host "Waiting for the ClimbUK brand book web part to reach this site..."
            try { Install-PnPApp -Identity $solutionId -Scope Tenant | Out-Null } catch { }
        }
        Start-Sleep -Seconds 30
        $component = BookComponent
    }
    if (-not $component) {
        Write-Warning "$BrandPageName.aspx is unchanged: this site does not offer the ClimbUK brand book web part. Check that 'ClimbUK brand book' shows as Enabled and Deployed in the app catalog ($(Get-PnPTenantAppCatalogUrl)), then run the script again."
    }
    else {
        $page = BrandPage
        $found = @($page.Controls | ForEach-Object { "$($_.Type)" }) -join ", "
        if ($found) {
            Write-Host "Clearing $BrandPageName.aspx (it held: $found)"
            $page.ClearPage()
            $page.Save() | Out-Null
        }
        Add-PnPPageSection -Page $BrandPageName -SectionTemplate OneColumn | Out-Null
        Add-PnPPageWebPart -Page $BrandPageName -Component $component -Section 1 -Column 1 | Out-Null
        $hasBook = HasBook
        if ($hasBook) {
            $made += $BrandPageName
            Write-Host "Built $BrandPageName.aspx with the brand book"
        }
        else {
            Write-Warning "Added the brand book web part to $BrandPageName.aspx but SharePoint does not show it on the page. Paste this output to your brand contact."
        }
    }
}
if ($hasBook) {
    Set-PnPPage -Identity $BrandPageName -CommentsEnabled:$false | Out-Null
}
if ($Publish -and $hasBook) {
    Set-PnPPage -Identity $BrandPageName -Publish | Out-Null
    Write-Host "Published $BrandPageName.aspx"
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
        -LogoUrl "$rel/$img/site/climbuk_sharepoint-site_footer-logo-white_480x160.png" | Out-Null
    Write-Host "Set the site logo, header and footer"
}
if ($SetNavigation -or $ReplaceNavigation) {
    # The menu bar a site shows depends on its type: communication sites draw it from Top navigation, sites with a
    # horizontal team site menu draw it from Quick Launch. Auto picks Quick Launch when it holds any links. The brand
    # book menus go there, and copies this script left in the other list are removed.
    $ourMenus = @($data.booknav | ForEach-Object { $_.label }) + "Files"
    $others = @{ TopNavigationBar = "QuickLaunch"; QuickLaunch = "TopNavigationBar" }
    $navLoc = $NavigationLocation
    if ($navLoc -eq "Auto") {
        $navLoc = if (@(Get-PnPNavigationNode -Location QuickLaunch).Count -gt 0) { "QuickLaunch" } else { "TopNavigationBar" }
    }
    function NavTree($nodes) {
        @(@($nodes | Where-Object { $_ }) | ForEach-Object {
            $kids = (Get-PnPNavigationNode -Id $_.Id).Children
            [ordered]@{ title = $_.Title; url = $_.Url; children = @(NavTree $kids) }
        } | Where-Object { $_ })
    }
    if ($ReplaceNavigation) {
        # Every old link in the menu bar is removed, after saving both menus to a file next to this script, so they
        # can be put back by hand.
        $backup = Join-Path $here ("navigation-backup-{0:yyyyMMdd-HHmmss}.json" -f (Get-Date))
        [ordered]@{
            site             = $SiteUrl
            QuickLaunch      = @(NavTree (Get-PnPNavigationNode -Location QuickLaunch))
            TopNavigationBar = @(NavTree (Get-PnPNavigationNode -Location TopNavigationBar))
        } | ConvertTo-Json -Depth 12 | Set-Content -Path $backup -Encoding utf8
        Write-Host "Saved the old menus to $backup"
        $gone = @(Get-PnPNavigationNode -Location $navLoc)
        foreach ($old in $gone) { Remove-PnPNavigationNode -Identity $old.Id -Force }
        Write-Host "Removed the old menu bar links ($navLoc): $(($gone | ForEach-Object { $_.Title }) -join ', ')"
    }
    foreach ($old in @(Get-PnPNavigationNode -Location $others[$navLoc] | Where-Object { $ourMenus -contains $_.Title })) {
        Remove-PnPNavigationNode -Identity $old.Id -Force
    }
    # Safe to run again: a menu or link that is already there is reused, not added twice. Links are added as external
    # so SharePoint does not check them against the page's draft or published state.
    function NavNode([string]$title, [string]$url, $parent) {
        $existing = if ($parent) { (Get-PnPNavigationNode -Id $parent.Id).Children } else { Get-PnPNavigationNode -Location $navLoc }
        $found = @($existing | Where-Object { $_.Title -eq $title })[0]
        if ($found) { return $found }
        if ($parent) {
            return Add-PnPNavigationNode -Location $navLoc -Title $title -Url $url -Parent $parent.Id -External
        }
        return Add-PnPNavigationNode -Location $navLoc -Title $title -Url $url -External
    }
    $brandUrl = "$SiteUrl/SitePages/$BrandPageName.aspx"
    if ($ReplaceNavigation) { NavNode "Home" $SiteUrl $null | Out-Null }
    foreach ($g in $data.booknav) {
        $parent = NavNode $g.label "http://linkless.header/" $null
        foreach ($l in $g.links) {
            NavNode $l.title "$($brandUrl)?brandpage=$($l.page)" $parent | Out-Null
        }
    }
    $files = NavNode "Files" "http://linkless.header/" $null
    NavNode "Marketing content" $MarketingContentUrl $files | Out-Null
    NavNode "Photo library" $PhotoLibraryUrl $files | Out-Null
    NavNode "Brand guidelines (PDF)" "$SiteUrl/BrandFiles" $files | Out-Null
    NavNode "Office templates" "$SiteUrl/BrandTemplates" $files | Out-Null
    Write-Host "Added the brand book menus and a Files menu to the site menu ($navLoc)"
}
if ($RegisterOfficeLibraries) {
    # Microsoft 365 only serves organisation asset libraries that everyone in the organisation can read, so the site
    # is shared with "Everyone except external users" as visitors (read only) first.
    $everyone = "c:0-.f|rolemanager|spo-grid-all-users/$(Get-PnPTenantId)"
    $visitors = Get-PnPGroup -AssociatedVisitorGroup
    if (-not (@(Get-PnPGroupMember -Group $visitors) | Where-Object { $_.LoginName -eq $everyone })) {
        Add-PnPGroupMember -Group $visitors -LoginName $everyone | Out-Null
        Write-Host "Shared the site with everyone in the organisation, read only"
    }
    $registered = (@(Get-PnPOrgAssetsLibrary) | ConvertTo-Json -Depth 6 -WarningAction SilentlyContinue) + ""
    foreach ($lib in @(@{U = "BrandTemplates"; T = "OfficeTemplateLibrary" }, @{U = "BrandOfficeFonts"; T = "OfficeFontLibrary" })) {
        if ($registered -match [regex]::Escape("$($rel.TrimStart("/"))/$($lib.U)")) {
            Write-Host "$($lib.U) is already registered"
            continue
        }
        try {
            Add-PnPOrgAssetsLibrary -LibraryUrl "$SiteUrl/$($lib.U)" -OrgAssetType $lib.T -CdnType Public | Out-Null
            Write-Host "Registered $($lib.U) as an organisation asset library"
        }
        catch {
            if ($_.Exception.Message -match "already") { Write-Host "$($lib.U) is already registered" }
            else { Write-Warning "Could not register $($lib.U): $($_.Exception.Message)" }
        }
    }
}
if ($SetHomePage) {
    Set-PnPHomePage -RootFolderRelativeUrl "SitePages/$BrandPageName.aspx" | Out-Null
    Write-Host "Set $BrandPageName.aspx as the site home page"
}

# 9. Check what visitors will see.
function Check([string]$what, [bool]$ok, [string]$detail) {
    $mark = if ($ok) { "OK  " } else { "FIX " }
    Write-Host "$mark $what$(if ($detail) { ": $detail" })"
}
Write-Host ""
Write-Host "Check"
Check "$BrandPageName.aspx shows the brand book" (HasBook) ""
$version = ""
try { $version = "$((Get-PnPFile -Url "$rel/SitePages/$BrandPageName.aspx" -AsListItem).FieldValues['_UIVersionString'])" } catch { }
Check "$BrandPageName.aspx is published" ($version -match '\.0$') "version $version"
$book = ""
try { $book = Get-PnPFile -Url "$rel/$bookFolder/index.html" -AsString } catch { }
Check "The brand book files are on the site" ($book -match 'id="cbb"') "$rel/$bookFolder"
$homePage = "$(Get-PnPHomePage)"
Check "The site home page" ($homePage -eq "SitePages/$BrandPageName.aspx") $homePage
foreach ($loc in "QuickLaunch", "TopNavigationBar") {
    $titles = @(Get-PnPNavigationNode -Location $loc | ForEach-Object { $_.Title })
    if ($titles.Count) { Write-Host "     Menu ($loc): $($titles -join ', ')" }
}
if ($RegisterOfficeLibraries) {
    $registered = (@(Get-PnPOrgAssetsLibrary) | ConvertTo-Json -Depth 6 -WarningAction SilentlyContinue) + ""
    foreach ($u in "BrandTemplates", "BrandOfficeFonts") {
        Check "$u is an organisation asset library" ($registered -match [regex]::Escape("$($rel.TrimStart("/"))/$u")) ""
    }
}

Write-Host ""
Write-Host "Done. Built: $($made -join ', ')"
if ($TextPages) { Write-Host "Next: add the Hero web part to $HomePageName.aspx and a Quick links row to each page (README.md)." }
if (-not $RegisterOfficeLibraries) { Write-Host "To show the templates in Word, Excel and PowerPoint, run again with -RegisterOfficeLibraries as a SharePoint Administrator." }
