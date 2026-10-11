# SharePoint brand centre

The ClimbUK brand centre on the SharePoint brand center site, looking and working like the brand centre on the website: the dark festival pages, the menus, search, the theme and text size switches, colour and type, logos, drawings, photography and the live components. One page, `brand.aspx`, shows the whole brand book through a small web part, and the site gets the ClimbUK theme, logo, header, footer and menus around it.

Everything here only adds, with one exception you ask for by name: `-ReplaceNavigation` saves the site menus to a file, then removes the old links from the menu bar. Otherwise the script never deletes a page, a file or a link, and it skips any page whose name is already taken. The steps that change the tenant or how the existing site looks (the app, theme, logo, header, footer, menu, home page) only run when you ask for them.

## What is in this folder

| Path | What it is |
| --- | --- |
| `build-brand-centre.ps1` | Uploads the brand book, images, PDFs and Office templates, builds `brand.aspx`, and (when asked) installs the web part and sets the theme, menu, home page, logo, header and footer |
| `brand-book/` | The brand book as plain files: every page, picture, font, style and script. The script uploads it to Site Assets > BrandCentre > book |
| `app/climb-brand-page.sppkg` | The ClimbUK brand book web part, for the app catalog |
| `brand-book-web-part/` | The web part source, with how to rebuild it |
| `pages.json` | The brand book menus, the ClimbUK theme colours and the twelve plain pages. The script reads it |
| `banners/` | 12 page banners, 1920x1080 JPEG under 300 KB: a festival photo with a Dark Brown fade where the page title sits |
| `quick-link-tiles/` | 16 tiles, 1200x675 JPEG: one house drawing in orange on Dark Brown, no words (the link title is live text) |
| `section-backgrounds/` | Contours on Dark Brown and on Charcoal, for full width sections |
| `site/` | Site logo (li monogram, 192x192), header background (2560x164, extended header) and footer logo (all white wordmark, transparent PNG, for the orange footer) |
| `brand-fonts/` | Montserrat and Open Sans as TTF, every weight and italic: for the brand center font package and for Word and PowerPoint |
| `licences/` | The SIL Open Font License for both fonts |
| `copy.txt` | The copy of the twelve plain pages, checked with the climb-voice copy checker |
| `_build/` | The scripts that make all of it |

## The site

| Menu | Pages |
| --- | --- |
| Brand | Overview, Colour, Type, Logos, Drawings, Icons, Photography |
| Build | Layout, Motion, Components, Design tokens, Templates |
| Artwork | Social, Call backgrounds, Wallpapers, Stage and screens, Print and merch, Email |
| Guidelines | All guidelines, Digital UI, Motion, Photography, Video, Print, merch and signage, Press and partners, Email signatures, Voice |
| Files | Marketing content, Photo library, Brand guidelines (PDF), Office templates |

Every brand book page has its own address on `brand.aspx`, for example `brand.aspx?brandpage=colour` for Colour, so each one has its own link to share. The brand book also carries the same menus at the top of the page, with search and the Downloads button.

Two new libraries hold the files: **Brand files** (the brand guidelines and one page rules as PDF) and **Brand templates** (Word, Excel and PowerPoint templates per brand), plus **Brand Office fonts** (empty until an admin publishes the fonts to it, step 5).

## Build it

### 1. Get ready (once)

1. Install PowerShell 7.4 or later, then `Install-Module PnP.PowerShell -Scope CurrentUser`.
2. Register an app for PnP sign in, as a Global Administrator or Application Administrator: `Register-PnPEntraIDAppForInteractiveLogin -ApplicationName "PnP brand centre" -Tenant <tenant>.onmicrosoft.com -Interactive`. Copy the client id it prints.
3. Clone or download the brand pack and run every command below from its `templates/sharepoint` folder.
4. Note the addresses of the brand center site and the two marketing content sites.

### 2. Install the web part and build the page

Run this as a SharePoint or Global Administrator. `-InstallApp` adds the ClimbUK brand book web part to the tenant app catalog, so it is only needed the first time and whenever the web part changes.

```powershell
./build-brand-centre.ps1 -SiteUrl https://<tenant>.sharepoint.com/sites/<brand-center-site> -ClientId <client id> `
  -MarketingContentUrl https://<tenant>.sharepoint.com/sites/<marketing-content-site> `
  -PhotoLibraryUrl https://<tenant>.sharepoint.com/sites/<photo-site> -PackPath ~/Brand-System -InstallApp
```

It uploads the brand book and the files, then builds `brand.aspx` as a draft: editors can open it, nobody else sees it. Open `https://<tenant>.sharepoint.com/sites/<brand-center-site>/SitePages/brand.aspx` to check it.

If the tenant has no app catalog yet, the script says so: create it in the SharePoint admin centre under **More features > Apps > Open**, wait for it to finish, then run the command again.

### 3. Switch the site over

When `brand.aspx` looks right, run the script again with the switches. Pages that already exist are skipped, so a second run only does the switches (and uploads the brand book again, which is how you update it):

```powershell
./build-brand-centre.ps1 -SiteUrl https://<tenant>.sharepoint.com/sites/<brand-center-site> -ClientId <client id> `
  -MarketingContentUrl https://<tenant>.sharepoint.com/sites/<marketing-content-site> `
  -PhotoLibraryUrl https://<tenant>.sharepoint.com/sites/<photo-site> -PackPath ~/Brand-System `
  -InstallApp -Publish -SetSiteLook -SetNavigation -ReplaceNavigation -SetHomePage -RegisterOfficeLibraries
```

It ends with a **Check** list: each line starts with `OK` or `FIX`, and the last lines show the menu bar. If the web part has only just been added to the app catalog, the script waits up to 10 minutes for it to reach the site before it builds `brand.aspx`.

| Switch | What it changes |
| --- | --- |
| `-InstallApp` | Adds the ClimbUK brand book web part to the tenant app catalog and makes it available on every site |
| `-Publish` | Publishes the new pages. Comments are always turned off on `brand.aspx` |
| `-SetSiteLook` | Adds the **ClimbUK** theme to the tenant (Orange Text `#C55308` with white text, 4.55:1) and applies it to this site, then sets the site logo, the extended header with the contour background, and the footer with the tagline and wordmark |
| `-SetNavigation` | Adds the Brand, Build, Artwork, Guidelines and Files menus to the menu bar the site shows (Quick Launch on sites with a team site menu, Top navigation on communication sites; force one with `-NavigationLocation`). Existing links stay unless you add `-ReplaceNavigation` |
| `-ReplaceNavigation` | Saves both site menus to `navigation-backup-<date and time>.json` next to the script, removes every old link from the menu bar (and the copies of the brand book menus in the other menu), then adds **Home** and the brand book menus. Use the backup file to put a link back by hand |
| `-SetHomePage` | Makes `brand.aspx` the site home page. The old home page stays in Site Pages, unchanged |
| `-RegisterOfficeLibraries` | Shares the site read only with everyone in the organisation (Microsoft 365 only serves organisation asset libraries everyone can read), then registers **Brand templates** and **Brand Office fonts**, so the templates show under the organisation tab in Word, Excel and PowerPoint. Needs a SharePoint Administrator |
| `-TextPages` | Also builds the twelve plain SharePoint pages from earlier (`brand-centre.aspx`, `our-brand.aspx` and so on). Not needed for the brand book |

### 4. The plain pages (only with -TextPages)

The plain pages need two web parts added by hand in the page editor:

- **Home (brand-centre.aspx):** add a **Hero** web part in a full width section at the top (layout Tiles, five tiles), using the table at the end.
- **Every page:** add a **Quick links** web part (layout Filmstrip) after the opening statement, using the tiles in each page's table at the end.

For each image, choose **Site Assets > BrandCentre** and the file named in the table.

### 5. Brand center settings

Open the brand center app on the site, then:

**Fonts.** Upload the files in `brand-fonts/` to **Brand fonts**, wait for them to process, then create a font package named **ClimbUK**:

| Slot | Font |
| --- | --- |
| Title | Montserrat ExtraBold (800) |
| Heading | Montserrat Bold (700) |
| Body | Open Sans Regular (400) |
| Interactive (buttons) | Montserrat SemiBold (600) |

Apply it in **Change the look > Font** on this site and on the marketing content sites.

**Theme.** `-SetSiteLook` adds the **ClimbUK** theme and applies it. To use it on other sites, pick it in **Change the look > Theme**. To make it in the brand center instead, use these colours:

| Use | Colour | Why |
| --- | --- | --- |
| Primary (buttons, links, strong accents) | Orange Text `#C55308` | White text on it is 4.55:1, so buttons and links pass. Climb Orange `#E8712A` is only 3.08:1 with white |
| Strong section ground | Dark Brown `#1E0F05`, accent Climb Orange `#E8712A` | Orange is 6.06:1 on Dark Brown; white text is 18.65:1 |
| Neutral section ground | Light Grey `#E9E9E9`, accent `#B04902` | The grey ground pair from the tokens |
| Soft section ground | White `#FFFFFF`, accent `#C55308` | |
| Second dark ground | Charcoal `#242322`, accent Orange Tint `#F2AE86` | For links on dark |

For an AAA version, make a second theme named **ClimbUK AAA** with Deep Orange `#8D4419` (7.06:1 with white) as the primary.

**Images.** If the brand center has an image library, add `banners/`, `quick-link-tiles/` and `section-backgrounds/` to it, so anyone building a page in Microsoft 365 can pick them.

**Register the Office libraries.** `-RegisterOfficeLibraries` in step 3 does this. To do it by hand instead: first share the site with **Everyone except external users** as visitors (Microsoft 365 refuses a library that not everyone can read), then run the commands below. This makes the templates show under the organisation tab in Word, Excel and PowerPoint, and lets PowerPoint for the web use the brand fonts. Run it as a SharePoint or Global Administrator, in the same PowerShell 7 with PnP. It signs in to the admin centre with the same app, then registers both libraries on the brand center site (all organisation asset libraries must be on that site):

```powershell
Connect-PnPOnline -Url https://<tenant>-admin.sharepoint.com -Interactive -ClientId <client id>
Add-PnPOrgAssetsLibrary -LibraryUrl https://<tenant>.sharepoint.com/sites/<brand-center-site>/BrandTemplates -OrgAssetType OfficeTemplateLibrary
Add-PnPOrgAssetsLibrary -LibraryUrl https://<tenant>.sharepoint.com/sites/<brand-center-site>/BrandOfficeFonts -OrgAssetType OfficeFontLibrary -CdnType Public
Get-PnPOrgAssetsLibrary
```

The last line lists every registered library, so you can check both are there. The changes can take up to 24 hours to show in Office.

**Fonts in Word and PowerPoint.** So the templates show Montserrat and Open Sans on every computer without installing them, the font files also need a font catalog in **Brand Office fonts**. The only command that builds it, `Set-SPOCustomFontCatalog`, is in the SharePoint Online Management Shell, which runs on Windows only. In Windows PowerShell:

```powershell
Install-Module Microsoft.Online.SharePoint.PowerShell -Scope CurrentUser
Connect-SPOService -Url https://<tenant>-admin.sharepoint.com
Set-SPOCustomFontCatalog -FontFolder <path to brand-fonts> -LibraryUrl https://<tenant>.sharepoint.com/sites/<brand-center-site>/BrandOfficeFonts
```

Both fonts are open source, so hosting them publicly is allowed by their licence.

## Common problems

- **brand.aspx is empty or says the web part is missing.** The web part is not installed yet. Run the script once with `-InstallApp` as an administrator, wait a few minutes, then run it again: it adds the brand book to the empty page it made earlier.
- **Everyone except external users needs read permission.** Registering an Office library needs the whole organisation to be able to read it. Use `-RegisterOfficeLibraries`, which shares the site read only first.
- **The brand book says it could not be loaded.** The brand book folder is missing from Site Assets > BrandCentre > book. Run the script again; it uploads the folder every time.
- **Fonts, pictures or the live previews do not show.** The brand book loads its styles, scripts and pictures from Site Assets on this site. If your tenant limits script sources, add this site to the trusted script sources in the SharePoint admin centre.
- **A page was skipped.** A page with that name already exists. The script left it alone. Rename or delete the old page by hand if you want the new one, then run the script again.
- **The PDFs or templates are missing.** Run the script with `-PackPath` pointing at the brand pack folder (the one with `pdf/` and `templates/` in it).
- **Sign in fails.** The client id must be the app from step 1, and the account needs edit rights on the brand center site.

## Rebuild it

The brand book comes from the brand centre's own build (`build_brand_book.py --standalone`), the same one that makes the website pages. The web part is rebuilt with Node 22 (see `brand-book-web-part/README.md`). Then, from this folder:

```bash
python3 _build/build_sharepoint_assets.py BRAND_PACK .
python3 _build/make_pack.py BRAND_PACK . BRAND_BOOK WEB_PART
```

Needs Python 3 with Pillow, and Node with Playwright and Chromium. Photos come from the Climb26 candid set in the brand pack, drawings and contour shapes from the house illustrations, colours from the tokens.

## The plain pages: the parts added by hand

### Brand centre (`brand-centre.aspx`)

Everything that makes ClimbUK, ClimbGroup and Climb27 look and sound like themselves, in one place.

**Hero web part** (full width section at the top, layout Tiles, five tiles):

| Tile | Image | Link | Description |
| --- | --- | --- | --- |
| Our brand | `banners/climbuk_sharepoint-banner_our-brand_1920x1080.jpg` | `SitePages/our-brand.aspx` | The name, the voice and the five visual rules. |
| Templates | `banners/climbuk_sharepoint-banner_templates_1920x1080.jpg` | `SitePages/templates.aspx` | Documents, slides and video, ready to go. |
| Logos | `banners/climbuk_sharepoint-banner_logos_1920x1080.jpg` | `SitePages/logos.aspx` | The right logo for every ground. |
| Microsoft 365 kit | `banners/climbuk_sharepoint-banner_microsoft-365_1920x1080.jpg` | `SitePages/microsoft-365.aspx` | Teams themes, backgrounds and signatures. |
| Artwork library | `banners/climbuk_sharepoint-banner_artwork-library_1920x1080.jpg` | `SitePages/artwork-library.aspx` | Every file, sorted by brand. |

**Quick links** (one column section after the first text section, layout Filmstrip):

| Title | Image | Link |
| --- | --- | --- |
| Voice | `quick-link-tiles/climbuk_sharepoint-tile_voice_1200x675.jpg` | `SitePages/voice.aspx` |
| Colour and type | `quick-link-tiles/climbuk_sharepoint-tile_colour-and-type_1200x675.jpg` | `SitePages/colour-and-type.aspx` |
| Photography | `quick-link-tiles/climbuk_sharepoint-tile_photography_1200x675.jpg` | `SitePages/photography.aspx` |
| Drawings and devices | `quick-link-tiles/climbuk_sharepoint-tile_drawings-and-devices_1200x675.jpg` | `SitePages/drawings-and-devices.aspx` |
| Guidelines | `quick-link-tiles/climbuk_sharepoint-tile_guidelines_1200x675.jpg` | `SitePages/guidelines.aspx` |
| Get help | `quick-link-tiles/climbuk_sharepoint-tile_get-help_1200x675.jpg` | `SitePages/get-help.aspx` |

### Our brand (`our-brand.aspx`)

Where the name comes from, what the brand stands for and the rules every piece follows.

**Quick links** (one column section after the first text section, layout Filmstrip):

| Title | Image | Link |
| --- | --- | --- |
| Voice | `quick-link-tiles/climbuk_sharepoint-tile_voice_1200x675.jpg` | `SitePages/voice.aspx` |
| Logos | `quick-link-tiles/climbuk_sharepoint-tile_logos_1200x675.jpg` | `SitePages/logos.aspx` |
| Colour and type | `quick-link-tiles/climbuk_sharepoint-tile_colour-and-type_1200x675.jpg` | `SitePages/colour-and-type.aspx` |
| Photography | `quick-link-tiles/climbuk_sharepoint-tile_photography_1200x675.jpg` | `SitePages/photography.aspx` |

### Voice (`voice.aspx`)

How ClimbUK sounds: headline energy with the discipline of a good adviser.

**Quick links** (one column section after the first text section, layout Filmstrip):

| Title | Image | Link |
| --- | --- | --- |
| Our brand | `quick-link-tiles/climbuk_sharepoint-tile_our-brand_1200x675.jpg` | `SitePages/our-brand.aspx` |
| Guidelines | `quick-link-tiles/climbuk_sharepoint-tile_guidelines_1200x675.jpg` | `SitePages/guidelines.aspx` |
| Templates | `quick-link-tiles/climbuk_sharepoint-tile_templates_1200x675.jpg` | `SitePages/templates.aspx` |
| Get help | `quick-link-tiles/climbuk_sharepoint-tile_get-help_1200x675.jpg` | `SitePages/get-help.aspx` |

### Logos (`logos.aspx`)

Every logo for ClimbUK, ClimbGroup and Climb27, and the right one for each ground.

**Quick links** (one column section after the first text section, layout Filmstrip):

| Title | Image | Link |
| --- | --- | --- |
| Colour and type | `quick-link-tiles/climbuk_sharepoint-tile_colour-and-type_1200x675.jpg` | `SitePages/colour-and-type.aspx` |
| Photography | `quick-link-tiles/climbuk_sharepoint-tile_photography_1200x675.jpg` | `SitePages/photography.aspx` |
| Templates | `quick-link-tiles/climbuk_sharepoint-tile_templates_1200x675.jpg` | `SitePages/templates.aspx` |
| Artwork library | `quick-link-tiles/climbuk_sharepoint-tile_artwork-library_1200x675.jpg` | `SitePages/artwork-library.aspx` |

### Colour and type (`colour-and-type.aspx`)

The palette, the five presets that keep text readable, and the two typefaces.

**Quick links** (one column section after the first text section, layout Filmstrip):

| Title | Image | Link |
| --- | --- | --- |
| Logos | `quick-link-tiles/climbuk_sharepoint-tile_logos_1200x675.jpg` | `SitePages/logos.aspx` |
| Templates | `quick-link-tiles/climbuk_sharepoint-tile_templates_1200x675.jpg` | `SitePages/templates.aspx` |
| Guidelines | `quick-link-tiles/climbuk_sharepoint-tile_guidelines_1200x675.jpg` | `SitePages/guidelines.aspx` |
| Drawings and devices | `quick-link-tiles/climbuk_sharepoint-tile_drawings-and-devices_1200x675.jpg` | `SitePages/drawings-and-devices.aspx` |

### Photography (`photography.aspx`)

Real people under real stage light: how to choose and use festival photos.

**Quick links** (one column section after the first text section, layout Filmstrip):

| Title | Image | Link |
| --- | --- | --- |
| Artwork library | `quick-link-tiles/climbuk_sharepoint-tile_artwork-library_1200x675.jpg` | `SitePages/artwork-library.aspx` |
| Drawings and devices | `quick-link-tiles/climbuk_sharepoint-tile_drawings-and-devices_1200x675.jpg` | `SitePages/drawings-and-devices.aspx` |
| Logos | `quick-link-tiles/climbuk_sharepoint-tile_logos_1200x675.jpg` | `SitePages/logos.aspx` |
| Guidelines | `quick-link-tiles/climbuk_sharepoint-tile_guidelines_1200x675.jpg` | `SitePages/guidelines.aspx` |

### Drawings and devices (`drawings-and-devices.aspx`)

The hand drawn line set, the background motifs and the festival devices that carry the energy.

**Quick links** (one column section after the first text section, layout Filmstrip):

| Title | Image | Link |
| --- | --- | --- |
| Photography | `quick-link-tiles/climbuk_sharepoint-tile_photography_1200x675.jpg` | `SitePages/photography.aspx` |
| Colour and type | `quick-link-tiles/climbuk_sharepoint-tile_colour-and-type_1200x675.jpg` | `SitePages/colour-and-type.aspx` |
| Artwork library | `quick-link-tiles/climbuk_sharepoint-tile_artwork-library_1200x675.jpg` | `SitePages/artwork-library.aspx` |
| Templates | `quick-link-tiles/climbuk_sharepoint-tile_templates_1200x675.jpg` | `SitePages/templates.aspx` |

### Templates (`templates.aspx`)

Documents, slides, spreadsheets and video templates with the fonts, colours and layouts already set.

**Quick links** (one column section after the first text section, layout Filmstrip):

| Title | Image | Link |
| --- | --- | --- |
| Microsoft 365 kit | `quick-link-tiles/climbuk_sharepoint-tile_microsoft-365_1200x675.jpg` | `SitePages/microsoft-365.aspx` |
| Colour and type | `quick-link-tiles/climbuk_sharepoint-tile_colour-and-type_1200x675.jpg` | `SitePages/colour-and-type.aspx` |
| Logos | `quick-link-tiles/climbuk_sharepoint-tile_logos_1200x675.jpg` | `SitePages/logos.aspx` |
| Get help | `quick-link-tiles/climbuk_sharepoint-tile_get-help_1200x675.jpg` | `SitePages/get-help.aspx` |

### Microsoft 365 kit (`microsoft-365.aspx`)

Teams meeting themes and backgrounds, email signatures and the brand across Microsoft 365.

**Quick links** (one column section after the first text section, layout Filmstrip):

| Title | Image | Link |
| --- | --- | --- |
| Templates | `quick-link-tiles/climbuk_sharepoint-tile_templates_1200x675.jpg` | `SitePages/templates.aspx` |
| Artwork library | `quick-link-tiles/climbuk_sharepoint-tile_artwork-library_1200x675.jpg` | `SitePages/artwork-library.aspx` |
| Logos | `quick-link-tiles/climbuk_sharepoint-tile_logos_1200x675.jpg` | `SitePages/logos.aspx` |
| Get help | `quick-link-tiles/climbuk_sharepoint-tile_get-help_1200x675.jpg` | `SitePages/get-help.aspx` |

### Artwork library (`artwork-library.aspx`)

Finished artwork and source files for every brand: social, print, stage, email and video.

**Quick links** (one column section after the first text section, layout Filmstrip):

| Title | Image | Link |
| --- | --- | --- |
| Photography | `quick-link-tiles/climbuk_sharepoint-tile_photography_1200x675.jpg` | `SitePages/photography.aspx` |
| Logos | `quick-link-tiles/climbuk_sharepoint-tile_logos_1200x675.jpg` | `SitePages/logos.aspx` |
| Templates | `quick-link-tiles/climbuk_sharepoint-tile_templates_1200x675.jpg` | `SitePages/templates.aspx` |
| Drawings and devices | `quick-link-tiles/climbuk_sharepoint-tile_drawings-and-devices_1200x675.jpg` | `SitePages/drawings-and-devices.aspx` |

### Guidelines (`guidelines.aspx`)

The full brand book chapters: voice, digital UI, motion, photography, video, print, press and signatures.

**Quick links** (one column section after the first text section, layout Filmstrip):

| Title | Image | Link |
| --- | --- | --- |
| Voice | `quick-link-tiles/climbuk_sharepoint-tile_voice_1200x675.jpg` | `SitePages/voice.aspx` |
| Colour and type | `quick-link-tiles/climbuk_sharepoint-tile_colour-and-type_1200x675.jpg` | `SitePages/colour-and-type.aspx` |
| Photography | `quick-link-tiles/climbuk_sharepoint-tile_photography_1200x675.jpg` | `SitePages/photography.aspx` |
| Get help | `quick-link-tiles/climbuk_sharepoint-tile_get-help_1200x675.jpg` | `SitePages/get-help.aspx` |

### Get help (`get-help.aspx`)

Who to ask about artwork, files, partners and press.

**Quick links** (one column section after the first text section, layout Filmstrip):

| Title | Image | Link |
| --- | --- | --- |
| Our brand | `quick-link-tiles/climbuk_sharepoint-tile_our-brand_1200x675.jpg` | `SitePages/our-brand.aspx` |
| Templates | `quick-link-tiles/climbuk_sharepoint-tile_templates_1200x675.jpg` | `SitePages/templates.aspx` |
| Artwork library | `quick-link-tiles/climbuk_sharepoint-tile_artwork-library_1200x675.jpg` | `SitePages/artwork-library.aspx` |
| Guidelines | `quick-link-tiles/climbuk_sharepoint-tile_guidelines_1200x675.jpg` | `SitePages/guidelines.aspx` |
