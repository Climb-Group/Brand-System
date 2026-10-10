// Render HTML jobs to PNG with headless Chromium.
// Usage: node render.mjs jobs.json   (jobs: [{html, out, w, h, transparent, scale}])
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require("playwright")); }
catch { ({ chromium } = require(process.env.PLAYWRIGHT_MODULE || "/opt/node22/lib/node_modules/playwright")); }
const jobs = JSON.parse(readFileSync(process.argv[2], "utf8"));
const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
const ctxs = new Map();
for (const j of jobs) {
  const s = j.scale || 1;
  if (!ctxs.has(s)) ctxs.set(s, await (await browser.newContext({ deviceScaleFactor: s })).newPage());
  const page = ctxs.get(s);
  await page.setViewportSize({ width: j.w, height: j.h });
  await page.goto(pathToFileURL(j.html).href);
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: j.out, omitBackground: !!j.transparent, clip: { x: 0, y: 0, width: j.w, height: j.h } });
}
await browser.close();
console.log(`rendered ${jobs.length}`);
