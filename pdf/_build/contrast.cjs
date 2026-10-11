const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// Contrast check for the printed pages. For every run of text it records the
// text colour, size and box, then hides all text and captures each page, so
// the background behind the words (photos, fades, stickers) can be measured.
// contrast.py reads the result and reports anything under WCAG 2.2 AA.
const VIEWPORT = { width: 1920, height: 1080 };

function collect() {
  const pages = [...document.querySelectorAll('section.s')];
  return pages.map((sec, p) => {
    const s = sec.getBoundingClientRect();
    const runs = [];
    const walk = document.createTreeWalker(sec, NodeFilter.SHOW_TEXT);
    while (walk.nextNode()) {
      const t = walk.currentNode;
      if (!t.textContent.trim()) continue;
      const el = t.parentElement;
      if (el.closest('svg')) continue;
      // Decorative texture, such as the faint marquee rows, is marked aria-hidden and skipped.
      if (el.closest('[aria-hidden="true"]')) continue;
      const cs = getComputedStyle(el);
      if (cs.visibility === 'hidden' || cs.display === 'none') continue;
      const range = document.createRange();
      range.selectNodeContents(t);
      for (const r of range.getClientRects()) {
        if (r.width < 2 || r.height < 2) continue;
        runs.push({
          text: t.textContent.trim().slice(0, 40), color: cs.color, size: parseFloat(cs.fontSize),
          weight: parseInt(cs.fontWeight, 10), stroke: cs.webkitTextStrokeWidth, opacity: cs.opacity,
          x: r.left - s.left, y: r.top - s.top, w: r.width, h: r.height,
        });
      }
    }
    return { page: p + 1, runs };
  });
}

(async () => {
  const out = process.argv[2];
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const report = {};
  for (const f of process.argv.slice(3)) {
    const page = await browser.newPage({ viewport: VIEWPORT });
    await page.goto('file://' + path.resolve(f), { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    const pages = await page.evaluate(collect);
    await page.addStyleTag({ content: '*{color:transparent!important;-webkit-text-stroke-color:transparent!important;text-shadow:none!important;text-decoration-color:transparent!important;caret-color:transparent!important}' });
    const name = path.basename(f, '.html');
    const secs = await page.$$('section.s');
    for (let i = 0; i < secs.length; i++) {
      await secs[i].screenshot({ path: path.join(out, name + '-' + (i + 1) + '.png') });
    }
    report[name] = pages;
    await page.close();
  }
  fs.writeFileSync(path.join(out, 'runs.json'), JSON.stringify(report));
  await browser.close();
})();
