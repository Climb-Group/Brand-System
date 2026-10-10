const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const browser = await chromium.launch();
  for (const f of process.argv.slice(2)) {
    const page = await browser.newPage();
    await page.goto('file://' + path.resolve(f), { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    const out = f.replace(/\.html$/, '.pdf');
    await page.pdf({ path: out, preferCSSPageSize: true, printBackground: true });
    console.log('wrote', out);
    await page.close();
  }
  await browser.close();
})();
