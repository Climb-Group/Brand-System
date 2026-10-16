# SharePoint brand centre

A new set of pages for the brand center site in SharePoint, built from the ClimbUK brand pack: twelve pages, a top menu, page banners, quick link tiles, the site header and footer, the brand theme and the brand fonts.

Everything here only adds. The script never deletes a page, a file or a link, and it skips any page whose name is already taken. The steps that change how the existing site looks (logo, header, footer, menu, home page) only run when you ask for them.

## What is in this folder

| Path | What it is |
| --- | --- |
| `build-brand-centre.ps1` | Builds the pages, uploads the images, PDFs and Office templates, and (when asked) sets the menu, home page, logo, header and footer |
| `pages.json` | Every page, section and line of copy, written from the copy files in `pages/`. The script reads it; edit the copy files and rebuild to change a page |
| `banners/` | 12 page banners, 1920x1080 JPEG under 300 KB: a festival photo with a Dark Brown fade where the page title sits |
| `quick-link-tiles/` | 16 tiles, 1200x675 JPEG: one house drawing in orange on Dark Brown, no words (the link title is live text) |
| `section-backgrounds/` | Contours on Dark Brown and on Charcoal, for full width sections |
| `site/` | Site logo (li monogram, 192x192), header background (2560x164, extended header) and footer logo (transparent PNG) |
| `brand-fonts/` | Montserrat and Open Sans as TTF, every weight and italic: for the brand center font package and for Word and PowerPoint |
| `licences/` | The SIL Open Font License for both fonts |
| `copy.txt` | All page copy as plain text, checked with the climb-voice copy checker (no hard-rule problems, reading grade 4) |
| `_build/` | The scripts that make all of it |

## The site

| Menu | Page | File |
| --- | --- | --- |
| Home | Brand centre | `home.aspx` |
| Brand | Our brand, Voice, Logos, Colour and type | `our-brand.aspx`, `voice.aspx`, `logos.aspx`, `colour-and-type.aspx` |
| Artwork | Photography, Drawings and devices, Artwork library | `photography.aspx`, `drawings-and-devices.aspx`, `artwork-library.aspx` |
| Make | Templates, Microsoft 365 kit | `templates.aspx`, `microsoft-365.aspx` |
| Guidelines | Guidelines | `guidelines.aspx` |
| Get help | Get help | `get-help.aspx` |

Every page follows the same shape: a banner photo with the page title, a strong opening statement, the content in one to three columns, a quick links row, and a strong closing section with one next step. The **Artwork library** page and the logo, photo and drawing links point at the two marketing content sites, so the files stay where they are and the brand centre explains them.

Three new libraries: **Brand files** (the brand guidelines and one page rules as PDF), **Brand templates** (Word, Excel and PowerPoint templates per brand) and **Brand Office fonts** (empty until an admin publishes the fonts to it, step 5).

## Build it

### 1. Get ready (once)

1. Install PowerShell 7.4 or later, then `Install-Module PnP.PowerShell -Scope CurrentUser`.
2. Register an app for PnP sign in, as a Global Administrator or Application Administrator: `Register-PnPEntraIDAppForInteractiveLogin -ApplicationName "PnP brand centre" -Tenant <tenant>.onmicrosoft.com -Interactive`. Copy the client id it prints.
3. Clone or download the brand pack, so the script can upload the PDFs and Office templates.
4. Note the addresses of the brand center site and the two marketing content sites.

### 2. Build the pages as drafts

```powershell
./build-brand-centre.ps1 -SiteUrl https://<tenant>.sharepoint.com/sites/<brand-center-site> -ClientId <client id> `
  -MarketingContentUrl https://<tenant>.sharepoint.com/sites/<marketing-content-site> `
  -PhotoLibraryUrl https://<tenant>.sharepoint.com/sites/<photo-site> -PackPath ~/Brand-System
```

The pages are saved as drafts: editors can open and check them, nobody else sees them. The script prints each page it built and any it skipped.

### 3. Switch the site over

When the drafts look right, run the script again with the switches you want. Pages that already exist are skipped, so a second run only does the switches.

| Switch | What it changes |
| --- | --- |
| `-Publish` | Publishes the new pages |
| `-SetNavigation` | Adds the five brand centre menus to the top navigation. Existing links stay: remove the old ones by hand when you are happy |
| `-SetHomePage` | Makes `home.aspx` the site home page. The old home page stays in Site Pages |
| `-SetSiteLook` | Site logo, extended header with the contour background, and the footer with the tagline and wordmark |

### 4. Finish by hand

The script builds the text sections. Two web parts need their pictures picked in the page editor:

- **Home:** add a **Hero** web part in a full width section at the top (layout Tiles, five tiles), using the table below.
- **Every page:** add a **Quick links** web part (layout Filmstrip) after the opening statement, using the tiles in each page's table below.

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

**Theme.** Create a theme named **ClimbUK** from these colours:

| Use | Colour | Why |
| --- | --- | --- |
| Primary (buttons, links, strong accents) | Orange Text `#C55308` | White text on it is 4.55:1, so buttons and links pass. Climb Orange `#E8712A` is only 3.08:1 with white |
| Strong section ground | Dark Brown `#1E0F05`, accent Climb Orange `#E8712A` | Orange is 6.06:1 on Dark Brown; white text is 18.65:1 |
| Neutral section ground | Light Grey `#E9E9E9`, accent `#B04902` | The grey ground pair from the tokens |
| Soft section ground | White `#FFFFFF`, accent `#C55308` | |
| Second dark ground | Charcoal `#242322`, accent Orange Tint `#F2AE86` | For links on dark |

Check the preview: strong sections should show Dark Brown with white text. If the theme tool ties strong sections to the primary colour instead, they will show `#C55308` with white text, which still passes. For an AAA version, make a second theme named **ClimbUK AAA** with Deep Orange `#8D4419` (7.06:1 with white) as the primary.

**Images.** If the brand center has an image library, add `banners/`, `quick-link-tiles/` and `section-backgrounds/` to it, so anyone building a page in Microsoft 365 can pick them.

**Fonts in Word and PowerPoint.** So the templates show Montserrat and Open Sans on every computer without installing them, a SharePoint admin publishes the files in `brand-fonts/` to the **Brand Office fonts** library the script made on this site. All organisation asset libraries must be on the same site:

```powershell
Add-SPOOrgAssetsLibrary -LibraryUrl https://<tenant>.sharepoint.com/sites/<brand-center-site>/BrandOfficeFonts -OrgAssetType OfficeFontLibrary -CdnType Public
Set-SPOCustomFontCatalog -FontFolder <path to brand-fonts> -LibraryUrl https://<tenant>.sharepoint.com/sites/<brand-center-site>/BrandOfficeFonts
```

Both fonts are open source, so hosting them publicly is allowed by their licence.

**Templates.** Ask a SharePoint admin to register the template library, so the templates show under the organisation tab in Word, Excel and PowerPoint:

```powershell
Add-SPOOrgAssetsLibrary -LibraryUrl https://<tenant>.sharepoint.com/sites/<brand-center-site>/BrandTemplates -OrgAssetType OfficeTemplateLibrary
```

## Common problems

- **A page was skipped.** A page with that name already exists. The script left it alone. Rename or delete the old page by hand if you want the new one, then run the script again.
- **The banner looks cropped.** SharePoint crops the header to the window. Open the page, choose **Edit**, select the header and use **Set focal point**.
- **The PDFs or templates are missing.** Run the script with `-PackPath` pointing at the brand pack folder (the one with `pdf/` and `templates/` in it).
- **Sign in fails.** The client id must be the app from step 1, and the account needs edit rights on the brand center site.

## Rebuild the artwork

```bash
python3 _build/build_sharepoint_assets.py <brand pack folder> <this folder>
python3 _build/make_pack.py <brand pack folder> <this folder>
```

Needs Python 3 with Pillow, and Node with Playwright and Chromium. Photos come from the Climb26 candid set in the brand pack, drawings and contour shapes from the house illustrations, colours from the tokens.

## Page by page: the parts added by hand

