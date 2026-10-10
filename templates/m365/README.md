# Microsoft 365 and Teams Premium branding

Everything needed to brand Microsoft 365 for ClimbUK, ClimbGroup and Climb27: Teams Premium meeting themes, organisation meeting backgrounds, branded meeting reactions, the Microsoft 365 organisation theme, app launcher tiles (Odoo included), a Teams app for Odoo, and the Microsoft 365 sign-in page.

Sizes and limits were checked against Microsoft's documentation on 10 October 2026. The build checks every file against its upload limit.

## What is here

| Folder | What it holds |
| --- | --- |
| `teams-themes/<Brand>/` | Meeting theme logo (dark and light, 800x800 PNG) and theme image (dark and light, 1440x810 JPG plus a 3840x2160 JPG) |
| `teams-themes/reactions/<set>/` | Branded reactions for all five slots (Like, Heart, Applause, Laugh, Surprised) in three sets: `mixed` (each reaction in its own palette so they are told apart at a glance: Like on Climb Orange, Heart on Dark Brown, Applause on Charcoal, Laugh on Orange Tint, Surprised on White), `orange` (Climb Orange disc, Dark Brown drawing) and `dark` (Dark Brown disc ringed in Climb Orange, orange drawing). Each has a static 100x100 PNG and an animated 100x5100 sprite (51 frames, 24 fps) |
| `teams-backgrounds/<Brand>/` | 14 meeting backgrounds per brand, 42 in all, 3840x2160 JPG: 10 festival layouts (stage-light, contours, connections, ascent, spotlight, summit, orbit, network, and the light pair ascent-light and contours-light) and 4 calm ones (calm-dark, calm-glow, calm-light, calm-white) |
| `org-theme/` | Navigation bar logos per brand: default (full colour reversed) and alternative (one-colour white), as SVG and as 200x48 PNG, all under 10 KB |
| `app-tiles/` | App launcher tiles at 60x60 (the upload size), 120x120 and 240x240: Odoo, climb-uk.com, Brand centre, Tickets, Media kit and a plain li monogram tile |
| `teams-app-odoo/`, `teams-app-odoo.zip` | A Teams app that opens Odoo in a personal tab: manifest, 192x192 colour icon (mark inside the 120x120 safe area) and 32x32 white outline icon |
| `sign-in-page/` | Sign-in page branding: 1920x1080 background (under 300 KB), banner and header logos (245x36), square logos (240x240, light and dark) and favicon (32x32) |
| `_build/build_m365.py` | The script that makes all of it |

## Settings to enter

| Setting | Value | Why |
| --- | --- | --- |
| Meeting theme colour, every brand | `#E8712A` Climb Orange | Teams may adjust it slightly for contrast |
| Navigation bar colour, ClimbUK (default theme) and Climb27 | `#1E0F05` Dark Brown | |
| Navigation bar colour, ClimbGroup | `#242322` Charcoal | |
| Text and icon colour | `#FFFFFF` | 18.65:1 on Dark Brown, 15.69:1 on Charcoal |
| Accent colour | `#C55308` Orange Text | 4.55:1 on white, so links and buttons pass. For AAA use `#8D4419` (7.06:1) |
| Logo on-click link | `https://www.climb-uk.com` | Or the intranet home page, once it is live |
| Sign-in page background colour | `#1E0F05` | Shown while the background image loads |

Climb Orange itself is not used as the accent: it is 3.08:1 on white and fails for the small links Microsoft colours with it.

## Where each item is uploaded

Nothing here is applied automatically. Each step below is a change to the live tenant, so make it when you are ready.

### Teams Premium meeting themes

Teams admin center > **Meetings** > **Customization policies** > open or add a policy > **Customize meeting visuals** > **Add a theme** (or **Edit meeting themes**).

1. **Logo:** dark theme `teams-themes/<Brand>/<brand>_theme-logo-dark_800x800.png`, light theme `..._theme-logo-light_800x800.png`. Limit: PNG or JPEG, at least 576x576, 5 MB.
2. **Images:** dark theme `..._theme-image-dark_1440x810.jpg`, light theme `..._theme-image-light_1440x810.jpg` (the 3840x2160 files fit too and stay sharp on 4K screens). Limit: 1024x574 to 3840x2160, 5 MB.
3. **Color:** `#E8712A`.
4. **Custom reactions:** select **Upload** next to each of Like, Heart, Applause, Laugh and Surprised. On **Static reaction** upload `teams-themes/reactions/<set>/<reaction>_static_100x100.png`, select **Next**, on **Animated reaction** upload `<reaction>_animated_100x5100.png`, select **Save**. Use one set per theme: `mixed` is the recommended set for every brand; `dark` and `orange` are single-palette alternatives. The drawings match their slot names, as Microsoft asks; **Revert** puts back the default.
5. **Preview**, **Apply**, turn **Currently active** on, **Save**.

A policy holds up to five themes. Suggested set-up: one policy per team, for example "ClimbUK" (ClimbUK theme), "ClimbGroup" (ClimbGroup theme) and "Climb27 team" (Climb27 theme), then assign each policy to its group (**Assign policies to users and groups**, or `Grant-CsTeamsMeetingBrandingPolicy` in PowerShell). The images must be uploaded in the admin center; PowerShell only assigns the policies. Only Teams Premium organisers can start a themed meeting, everyone who joins sees it, and the images do not show on mobile.

### Meeting backgrounds

Same policy > **Meeting backgrounds** > turn on **Use background images from my organization** > **+Add**, then **Save**.

Upload any of the 42 files in `teams-backgrounds/` (up to 50 per policy; 360x360 to 3840x2160, PNG or JPEG). A brand's own 14 fit in one policy with room to spare. The festival layouts carry the energy with stage glow, contours, chevrons, stickers and the house drawings; photos appear only as faded edge columns in `connections`. For quieter calls there are the four calm backgrounds, two dark and two light.

Every background keeps the middle of the frame calm for the person and puts the logo top left. Teams mirrors your own preview, so the logo reads backwards to you and the right way round to everyone else.

### Organisation theme (navigation bar, logos, colours)

Microsoft 365 admin center > **Settings** > **Org settings** > **Organization profile** > **Custom themes**. Global admins only.

1. **Default theme** (everyone): logo `org-theme/climbuk_m365-logo-default.svg`, alternative logo `climbuk_m365-logo-alternative.svg`, colours from the table above, on-click link `https://www.climb-uk.com`.
2. **Group themes** (up to four, each for up to five Microsoft 365 Groups): a ClimbGroup theme (`climbgroup_*` logos, Charcoal bar) and a Climb27 team theme (`climb27_*` logos, Dark Brown bar). People in more than one themed group see the default theme.
3. On **General**, decide whether people may override the theme and whether their name shows.

The logo can be uploaded (under 10 KB) or given as an HTTPS link that opens without signing in. SVG is scaled to 24 px high; PNG is fitted inside 200x48. Every logo here is under 10 KB.

### App launcher tiles

Microsoft 365 admin center > **Settings** > **Org settings** > **Organization profile** > **Custom tiles for Apps** > **+ Add a custom tile**.

| Tile name | URL of website | Image URL (60x60) | Description |
| --- | --- | --- | --- |
| Odoo | `https://www.climb-uk.com/odoo` | link to `app-tiles/odoo_60x60.png` | Our business system: contacts, events, tickets, website and accounts. |
| climb-uk.com | `https://www.climb-uk.com` | `app-tiles/website_60x60.png` | The public website. |
| Brand centre | the brand centre site address | `app-tiles/brand-centre_60x60.png` | Logos, colours, fonts, templates and the brand guidelines. |
| Tickets | the event ticket page | `app-tiles/tickets_60x60.png` | Event tickets and the box office. |
| Media kit | the media kit page | `app-tiles/media-kit_60x60.png` | Photos, video, press and partner downloads. |

The image must be a public HTTPS link that opens without signing in: host the PNGs on the website (for example under `/brand`) or link the files in this brand pack's public download. Tiles appear in the app launcher on the **All** tab within 24 hours; the admin adding them needs an Exchange Online mailbox they have signed in to at least once.

### Teams app for Odoo

Teams admin center > **Teams apps** > **Manage apps** > **Upload new app** > choose `teams-app-odoo.zip`. Then allow it in an app permission or setup policy, and pin it if you want it in everyone's app bar.

The app opens `https://www.climb-uk.com/odoo` in a personal tab, with an "open in browser" link. Before rolling it out, check that the Odoo login loads inside Teams: if the server refuses to be shown in a frame, change `contentUrl` in `manifest.json` to a page that allows it, or keep the app launcher tile only. The app id in the manifest is fixed so updates replace the same app; raise `version` for each change.

### Sign-in page

Microsoft Entra admin center > **Entra ID** > **Custom Branding** (Organizational Branding Administrator).

| Slot | File | Limit |
| --- | --- | --- |
| Favicon | `sign-in-page/climbuk_favicon_32x32.png` | 32x32, 5 KB |
| Background image | `climbuk_signin-background_1920x1080.jpg` | 1920x1080, 300 KB |
| Page background colour | `#1E0F05` | |
| Banner logo | `climbuk_banner-logo_245x36.png` | 245x36, 50 KB |
| Header logo | `climbuk_header-logo_245x36.png` | 245x36, 10 KB |
| Square logo, light theme | `climbuk_square-logo-light_240x240.png` | 240x240, 50 KB |
| Square logo, dark theme | `climbuk_square-logo-dark_240x240.png` | 240x240, 50 KB |

The sign-in box sits in the middle of the page, so the background is darkest there and the photo shows at the sides.

## Rebuild

```bash
python3 templates/m365/_build/build_m365.py            # HTML in build/m365, finished files in templates/m365
```

Needs Python 3 with Pillow, Node with Playwright and Chromium (as `generators/render.mjs`). The script lays out each piece as HTML from the tokens, logo masters, Climb26 candid photos and house illustrations, renders it, then saves it at the size and file-size limit of its upload slot (JPEG quality steps down until a file fits). Reactions are composed frame by frame in `_build/reactions.py` (fade in on frames 0 to 9, key moment at frame 23, fade out on 41 to 50). Four of the festival backgrounds per brand come from the asset catalogue (`generators/catalogue.py`, the `call-bg` set); the other six reuse the same pieces in new arrangements. Copy is checked with the climb-voice checker.

## Rules it follows

- Tokens only: Climb Orange `#E8712A`, Dark Brown `#1E0F05`, Charcoal `#242322`, Light Grey `#E9E9E9`, White, Orange Text `#C55308`, Orange Tint `#F2AE86`.
- climb-visual-style: dark first, one orange word and one italic word per line, the short orange rule, stickers, glow and grain; logo masters only, with clear space; stacked tile for squares 64 px and up, li monogram below that.
- climb-voice: brand lines already in use ("Find your people.", "Business with a party.", "Your business. Bigger stage."), the tagline and the Climb27 dates, with no location names.
- WCAG 2.2 AA: every text and icon colour pair above passes 4.5:1; the light theme image uses Orange Text for its orange word.
