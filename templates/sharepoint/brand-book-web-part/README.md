# ClimbUK brand book web part

A SharePoint web part that shows the ClimbUK brand book on a SharePoint page, full width: the same pages, menus, search, theme and text size switches and live component previews as the brand centre on the website.

It holds no brand content itself. It reads the standalone brand book from a folder on the site (by default `Site Assets/BrandCentre/book`), so updating the brand book means uploading the new folder, not a new app.

## How it works

- The page to show comes from the address (`brand.aspx?brandpage=colour`), or from the web part setting **Page to open first**. Every brand book link becomes a link to the same SharePoint page with a new `brandpage`, so each page has its own address and the back button works.
- The brand book styles (tokens, fonts, the book) load from the brand book folder. Pictures and files load from there too.
- SharePoint downloads `.html` files from a library rather than showing them, so pages and component previews are read as text. Previews are shown through `srcdoc` with a base address in the folder.
- `src/webparts/climbBrandPage/book/brandBook.ts` is the brand book script, copied in by `scripts/sync-book.mjs`, which changes four lines so that addresses resolve against the folder. Do not edit it by hand.

## Build it

Needs Node 22.14 or later on the 22 line.

```bash
npm install
node scripts/sync-book.mjs <standalone brand book folder>
npm run build
```

The package is `sharepoint/solution/climb-brand-page.sppkg`. The brand centre build script installs it with `-InstallApp`.

## Settings

| Setting | Default | What it does |
| --- | --- | --- |
| Page to open first | Overview | The brand book page shown when the address has no `brandpage` |
| Brand book folder | empty: `Site Assets/BrandCentre/book` on this site | Another folder holding the standalone brand book |

## Accessibility

The brand book carries its own WCAG 2.2 AA checks, keyboard support, focus styles and reduced motion. The web part adds a status line while a page loads and an alert if it cannot be loaded.
