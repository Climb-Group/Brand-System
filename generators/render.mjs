// Render the asset catalogue to PNG with headless Chromium.
// Usage: node generators/render.mjs OUT_DIR [filter]
// filter is a comma-separated list; an asset renders when any item matches. "word" matches names containing it,
// "^prefix" matches names starting with it, "group=Name" matches a manifest group, "set=name" a manifest set.
// Needs Playwright (npm i -D playwright) or a global install; set CHROMIUM_PATH to use a specific browser binary.
// Each manifest entry has a layout size (w, h), a device scale (1 or 2) and a transparent flag. One browser
// context is opened per scale, so a scale-2 asset laid out at 1128x191 is saved as a 2256x382 PNG.
// Transparent assets (lower third, garment prints) are saved with no background.
import { readFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";
import { pathToFileURL } from "node:url";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
let chromium;
try {
  ({ chromium } = require("playwright"));
} catch {
  ({ chromium } = require(join(process.env.PLAYWRIGHT_MODULE || "/opt/node22/lib/node_modules/playwright")));
}

const outDir = process.argv[2] || "build";
const filters = (process.argv[3] || "").split(",").map((f) => f.trim()).filter(Boolean);
function wanted(asset) {
  if (!filters.length) return true;
  return filters.some((f) => {
    if (f.startsWith("^")) return asset.name.startsWith(f.slice(1));
    if (f.startsWith("group=")) return asset.group === f.slice(6);
    if (f.startsWith("set=")) return asset.set === f.slice(4);
    return asset.name.includes(f);
  });
}
const manifest = JSON.parse(readFileSync(join(outDir, "manifest.json"), "utf8"));
mkdirSync(join(outDir, "png"), { recursive: true });

const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
const pages = new Map();
async function pageFor(scale) {
  if (!pages.has(scale)) {
    const context = await browser.newContext({ deviceScaleFactor: scale });
    const page = await context.newPage();
    page.setDefaultTimeout(180000);
    pages.set(scale, page);
  }
  return pages.get(scale);
}

let count = 0;
for (const asset of manifest) {
  if (!wanted(asset)) continue;
  const page = await pageFor(asset.scale || 1);
  await page.setViewportSize({ width: asset.w, height: asset.h });
  await page.goto(pathToFileURL(asset.html).href, { waitUntil: "load" });
  await page.evaluate(() => document.fonts.ready);
  // Pages that shrink lines to fit (class "fit") flag the body when they are done.
  await page.waitForFunction(() => !document.querySelector(".fit") || document.body.dataset.fit === "1");
  await page.locator(".canvas").screenshot({
    path: join(outDir, "png", `${asset.name}.png`),
    omitBackground: Boolean(asset.transparent),
  });
  count += 1;
}
await browser.close();
console.log(`[render] ${count} PNGs in ${join(outDir, "png")}`);
