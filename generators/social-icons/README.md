# Social icons and signature buttons

`build_social_icons.mjs` makes the social icons, banner buttons and the date sticker for email signatures (the signature tool), footers and share kits, from the brand tokens and the glyphs in `glyphs/` (licences in `glyphs/LICENSES.md`).

```bash
node generators/social-icons/build_social_icons.mjs            # everything
node generators/social-icons/build_social_icons.mjs --outline  # only the outline icons
```

The outline set (`icon_<name>_<orange|white|charcoal>_outline`) is the signature icon row: a rounded square line with the glyph inside, including Bluesky. `--outline` keeps every other entry already in `manifest.json`.

Output goes to `icons/social/` with a `manifest.json`. The website module carries a copy, so the live site hosts every file once it is installed. How to use them, and the signature template, are in `../../guidelines/signatures.md` and `../email/signature-template.html`.
