// Render each job's HTML .canvas to PNG. Usage: node render.mjs jobs.json OUT_DIR
import { readFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";
import { pathToFileURL } from "node:url";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "/opt/node22/lib/node_modules/playwright");
const jobs = JSON.parse(readFileSync(process.argv[2], "utf8"));
const out = process.argv[3];
mkdirSync(out, { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage();
for (const job of jobs) {
  await page.setViewportSize({ width: job.w, height: job.h });
  await page.goto(pathToFileURL(job.html).href, { waitUntil: "load" });
  await page.evaluate(() => document.fonts.ready);
  await page.locator(".canvas").screenshot({ path: join(out, `${job.name}.png`), omitBackground: job.fmt === "png" });
}
await browser.close();
