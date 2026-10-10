// Social icons and buttons for email signatures (the signature tool), footers and share kits.
// Usage: node generators/social-icons/build_social_icons.mjs            # everything
//        node generators/social-icons/build_social_icons.mjs --outline  # outline icons only
// Writes SVG and PNG (@2x and @3x) into icons/social/. The website module carries a copy, so once it is
// installed every file is hosted at https://www.climb-uk.com/climb_website_brand/static/src/img/signature/<file>.
// Colours come from the tokens; glyphs are vendored in ./glyphs (see glyphs/LICENSES.md).
// Needs Playwright and Chromium, as render.mjs does.
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { createRequire } from "node:module";

const here = dirname(fileURLToPath(import.meta.url));
const repo = join(here, "..", "..");
const out = join(repo, "icons", "social");
mkdirSync(out, { recursive: true });

const tokens = JSON.parse(readFileSync(join(repo, "docs", "brand-system", "tokens", "brand.tokens.json"), "utf8"));
const C = Object.fromEntries(Object.entries(tokens.color.brand).filter(([k]) => !k.startsWith("$")).map(([k, v]) => [k, v.$value]));
// orange, dark-brown, charcoal, light-grey, white

const ICONS = {
  linkedin: { label: "LinkedIn", kind: "fill" },
  instagram: { label: "Instagram", kind: "fill" },
  tiktok: { label: "TikTok", kind: "fill" },
  x: { label: "X", kind: "fill" },
  facebook: { label: "Facebook", kind: "fill" },
  youtube: { label: "YouTube", kind: "fill" },
  globe: { label: "Website", kind: "line", file: "website" },
  mail: { label: "Email", kind: "line", file: "email" },
  phone: { label: "Phone", kind: "line" },
  calendar: { label: "Book a meeting", kind: "line", file: "book" },
  ticket: { label: "Tickets", kind: "line", file: "tickets" },
};

// Colour schemes: ground and glyph. All glyphs meet 3:1 non-text contrast against their ground (WCAG 1.4.11);
// the mono schemes have no ground and are for placing straight onto White or Dark Brown.
const SCHEMES = {
  orange: { bg: C.orange, fg: C["dark-brown"] },
  dark: { bg: C["dark-brown"], fg: C.white },
  charcoal: { bg: C.charcoal, fg: C.orange },
  "mono-dark": { bg: null, fg: C.charcoal },
  "mono-white": { bg: null, fg: C.white },
};
const SHAPES = ["circle", "square"];

// Outline set for the signature icon row: a rounded square drawn as a 2px line at 24px, glyph inside, no ground.
// Files: icon_<name>_<colour>_outline. Orange and Charcoal for light grounds, White for dark grounds.
const OUTLINE_ICONS = {
  facebook: { label: "Facebook", kind: "fill" },
  x: { label: "X", kind: "fill" },
  bluesky: { label: "Bluesky", kind: "fill" },
  instagram: { label: "Instagram", kind: "fill" },
  linkedin: { label: "LinkedIn", kind: "fill" },
  tiktok: { label: "TikTok", kind: "fill" },
  youtube: { label: "YouTube", kind: "fill" },
  mail: { label: "Email", kind: "line", file: "email" },
  phone: { label: "Phone", kind: "line" },
  globe: { label: "Website", kind: "line", file: "website" },
  calendar: { label: "Book a meeting", kind: "line", file: "book" },
};
const OUTLINE_COLOURS = { orange: C.orange, white: C.white, charcoal: C.charcoal };

function outlineSvg(name, def, colour) {
  const fg = OUTLINE_COLOURS[colour];
  // 48 unit box shown at 24px: a 4 unit line is 2px on screen. Glyph is 24 units (12px), centred.
  const frame = `<rect x="2" y="2" width="44" height="44" rx="11" fill="none" stroke="${fg}" stroke-width="4"/>`;
  const g = glyph(name, def.kind, fg).replace('stroke-width="2.25"', 'stroke-width="2.5"');
  return `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48" role="img" aria-label="${def.label}"><title>${def.label}</title>${frame}<g transform="translate(12 12)">${g}</g></svg>`;
}

function glyph(name, kind, fg) {
  const src = readFileSync(join(here, "glyphs", `${name}.svg`), "utf8");
  const inner = src.replace(/^[\s\S]*?<svg[^>]*>/, "").replace(/<\/svg>\s*$/, "").replace(/<title>.*?<\/title>/, "");
  if (kind === "fill") return `<g fill="${fg}">${inner}</g>`;
  return `<g fill="none" stroke="${fg}" stroke-width="2.25" stroke-linecap="square" stroke-linejoin="miter">${inner}</g>`;
}

function iconSvg(name, def, scheme, shape) {
  const { bg, fg } = SCHEMES[scheme];
  const size = 48;
  const g = bg ? 22 : 30; // glyph size inside a shape, or alone
  const off = (size - g) / 2;
  let ground = "";
  if (bg && shape === "circle") ground = `<circle cx="24" cy="24" r="24" fill="${bg}"/>`;
  if (bg && shape === "square") ground = `<rect width="48" height="48" rx="10" fill="${bg}"/>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" role="img" aria-label="${def.label}"><title>${def.label}</title>${ground}<g transform="translate(${off} ${off}) scale(${g / 24})">${glyph(name, def.kind, fg)}</g></svg>`;
}

// Signature buttons: pills with a label, as images for signature banners. Dark Brown on Climb Orange passes at any size.
const BUTTONS = [
  { file: "button_tickets", label: "Get your Climb27 ticket", icon: "ticket" },
  { file: "button_meeting", label: "Book a meeting with me", icon: "calendar" },
  { file: "button_partner", label: "Partner with ClimbUK", icon: null },
  { file: "button_see-you", label: "See you at Climb27", icon: null },
];
const BUTTON_SCHEMES = {
  orange: { bg: C.orange, fg: C["dark-brown"], arrow: C["dark-brown"] },
  dark: { bg: C["dark-brown"], fg: C.white, arrow: C.orange },
};

const fontDir = pathToFileURL(join(repo, "docs", "brand-system", "fonts")).href;
const fontCss = `@font-face{font-family:Montserrat;font-weight:800;src:url('${fontDir}/montserrat-latin-800-normal.woff2')}
@font-face{font-family:Montserrat;font-weight:700;src:url('${fontDir}/montserrat-latin-700-normal.woff2')}`;

function buttonHtml(b, scheme) {
  const s = BUTTON_SCHEMES[scheme];
  const icon = b.icon ? `<span class="i">${glyph(b.icon, "line", s.fg).replace("<g", '<svg viewBox="0 0 24 24" width="18" height="18"><g').replace(/<\/g>$/, "</g></svg>")}</span>` : "";
  return `<!doctype html><html><head><meta charset="utf-8"><style>${fontCss}
html,body{margin:0;background:transparent}
.b{display:inline-flex;align-items:center;gap:10px;height:40px;padding:0 20px;border-radius:999px;background:${s.bg};color:${s.fg};
font:800 15px/1 Montserrat,sans-serif;letter-spacing:.02em;white-space:nowrap}
.i{display:inline-flex}.a{color:${s.arrow};font-weight:800}
</style></head><body><span class="b">${icon}<span>${b.label}</span><span class="a">&#8594;</span></span></body></html>`;
}

// A date sticker for the signature: tilted, as on the website.
function stickerHtml() {
  return `<!doctype html><html><head><meta charset="utf-8"><style>${fontCss}
html,body{margin:0;background:transparent}#w{display:inline-block;padding:10px}
.s{display:inline-block;transform:rotate(-4deg);background:${C.orange};color:${C["dark-brown"]};font:800 13px/1 Montserrat,sans-serif;
letter-spacing:.1em;text-transform:uppercase;padding:8px 12px;border-radius:6px}
</style></head><body><div id="w"><span class="s">Climb27 / 30 June &amp; 1 July 2027</span></div></body></html>`;
}

const require = createRequire(import.meta.url);
let chromium;
try {
  ({ chromium } = require("playwright"));
} catch {
  ({ chromium } = require(join(process.env.PLAYWRIGHT_MODULE || "/opt/node22/lib/node_modules/playwright")));
}
const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});

async function png(html, file, scale, selector) {
  const page = await browser.newPage({ deviceScaleFactor: scale, viewport: { width: 600, height: 200 } });
  await page.setContent(html, { waitUntil: "load" });
  await page.evaluate(() => document.fonts.ready);
  await page.locator(selector).screenshot({ path: join(out, file), omitBackground: true });
  await page.close();
}

const outlineOnly = process.argv.includes("--outline");
const manifest = [];
async function writeIcon(stem, svg) {
  writeFileSync(join(out, `${stem}.svg`), svg + "\n");
  // 24px on screen, so 48 and 72 pixel PNGs for sharp retina rendering in mail clients
  const html = `<!doctype html><html><body style="margin:0;background:transparent"><div id="c" style="width:24px;height:24px">${svg.replace('width="48" height="48"', 'width="24" height="24"')}</div></body></html>`;
  await png(html, `${stem}@2x.png`, 2, "#c");
  await png(html, `${stem}@3x.png`, 3, "#c");
}
for (const [name, def] of outlineOnly ? [] : Object.entries(ICONS)) {
  const base = def.file || name;
  for (const scheme of Object.keys(SCHEMES)) {
    for (const shape of SCHEMES[scheme].bg ? SHAPES : ["plain"]) {
      const stem = `icon_${base}_${scheme}${shape === "plain" ? "" : "_" + shape}`;
      await writeIcon(stem, iconSvg(name, def, scheme, shape));
      manifest.push({ file: stem, label: def.label, scheme, shape });
    }
  }
}
for (const [name, def] of Object.entries(OUTLINE_ICONS)) {
  for (const colour of Object.keys(OUTLINE_COLOURS)) {
    const stem = `icon_${def.file || name}_${colour}_outline`;
    await writeIcon(stem, outlineSvg(name, def, colour));
    manifest.push({ file: stem, label: def.label, scheme: colour, shape: "outline" });
  }
}
for (const b of outlineOnly ? [] : BUTTONS) {
  for (const scheme of Object.keys(BUTTON_SCHEMES)) {
    const stem = `${b.file}_${scheme}`;
    await png(buttonHtml(b, scheme), `${stem}@2x.png`, 2, ".b");
    manifest.push({ file: stem, label: b.label, scheme, shape: "pill" });
  }
}
if (outlineOnly) {
  // Keep every other entry of the existing manifest and replace only the outline ones.
  let old = [];
  try { old = JSON.parse(readFileSync(join(out, "manifest.json"), "utf8")); } catch {}
  manifest.unshift(...old.filter((m) => m.shape !== "outline"));
} else {
  await png(stickerHtml(), "sticker_climb27-dates@2x.png", 2, "#w");
  manifest.push({ file: "sticker_climb27-dates", label: "Climb27, 30 June and 1 July 2027", scheme: "orange", shape: "sticker" });
}
writeFileSync(join(out, "manifest.json"), JSON.stringify(manifest, null, 2) + "\n");
await browser.close();
console.log(`[social-icons] wrote ${manifest.length} items to ${out}`);
