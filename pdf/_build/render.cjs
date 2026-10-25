const { chromium } = require('playwright');
const path = require('path');

// Chromium prints CSS gradients as PDF function shadings (ShadingType 1),
// which several PDF viewers cannot draw: they paint a flat pink fallback
// instead. So every element with a gradient background is captured to a PNG
// and its background swapped for that image. Text and logos stay vector.
// Gradients are smooth, so the captures come from a half-resolution copy of
// the page, which keeps the PDFs small.
const VIEWPORT = { width: 1920, height: 1080 };

function tag() {
  let i = 0;
  for (const el of document.querySelectorAll('body *')) {
    if (getComputedStyle(el).backgroundImage.includes('gradient')) el.dataset.gi = i++;
  }
  return i;
}

async function open(browser, file, scale) {
  const page = await browser.newPage({ viewport: VIEWPORT, deviceScaleFactor: scale });
  await page.goto('file://' + path.resolve(file), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  return page;
}

// Chromium prints a box-shadow, filter or text-shadow as a separate soft-masked image. Chrome hides the seams,
// but Apple Preview and printers' RIPs draw them as boxes around the shape, so print pages use flat edges only.
function softEffects() {
  const found = [];
  for (const el of document.querySelectorAll('body *')) {
    const cs = getComputedStyle(el);
    if (cs.boxShadow !== 'none' || cs.filter !== 'none' || cs.textShadow !== 'none') {
      found.push(el.tagName.toLowerCase() + (el.className ? '.' + String(el.className).trim().replace(/\s+/g, '.') : ''));
    }
  }
  return [...new Set(found)];
}

async function flattenGradients(page, cap) {
  await page.evaluate(tag);
  const n = await cap.evaluate(tag);
  await cap.addStyleTag({ content:
    'html.gi-cap,html.gi-cap body{background:transparent!important}'
    + 'html.gi-cap body *{visibility:hidden!important}'
    + 'html.gi-cap [data-gi-cap]{visibility:visible!important;transform:none!important;'
    + 'border-color:transparent!important;box-shadow:none!important;outline:none!important;color:transparent!important}' });
  await cap.evaluate(() => document.documentElement.classList.add('gi-cap'));
  const shots = [];
  for (let i = 0; i < n; i++) {
    const r = await cap.evaluate((i) => {
      const el = document.querySelector('[data-gi="' + i + '"]');
      el.setAttribute('data-gi-cap', '');
      const b = el.getBoundingClientRect();
      return { x: b.left + scrollX, y: b.top + scrollY, w: b.width, h: b.height };
    }, i);
    // Clip to the document: anything above or left of it is cut off in print too.
    const x = Math.max(0, r.x), y = Math.max(0, r.y), w = r.w - (x - r.x), h = r.h - (y - r.y);
    if (w >= 1 && h >= 1) {
      const buf = await cap.screenshot({ fullPage: true, omitBackground: true, type: 'png', clip: { x, y, width: w, height: h } });
      shots.push({ url: 'data:image/png;base64,' + buf.toString('base64'), dx: x - r.x, dy: y - r.y, w, h });
    } else {
      shots.push(null);
    }
    await cap.evaluate((i) => document.querySelector('[data-gi="' + i + '"]').removeAttribute('data-gi-cap'), i);
  }
  await page.evaluate((shots) => shots.forEach((s, i) => {
    const el = document.querySelector('[data-gi="' + i + '"]');
    // The half-resolution capture has a soft edge pixel; bleed it 3px past the box so the edge never lets
    // the photo underneath show through as a seam. The element's own clip trims the bleed.
    const B = 3;
    el.style.setProperty('background', s
      ? 'url(' + s.url + ') ' + (s.dx - B) + 'px ' + (s.dy - B) + 'px / ' + (s.w + 2 * B) + 'px ' + (s.h + 2 * B) + 'px no-repeat border-box'
      : 'none', 'important');
  }), shots);
  return n;
}

(async () => {
  const browser = await chromium.launch();
  // --flat refuses a page with any soft effect; the brochures are printed, so their build passes it.
  const flat = process.argv.includes('--flat');
  for (const f of process.argv.slice(2).filter((a) => a !== '--flat')) {
    const page = await open(browser, f, 1);
    const soft = flat ? await page.evaluate(softEffects) : [];
    if (soft.length) {
      console.error(f + ': shadows or filters print as boxes outside Chrome, use a flat edge instead: ' + soft.join(', '));
      process.exit(1);
    }
    const cap = await open(browser, f, 0.5);
    const n = await flattenGradients(page, cap);
    await cap.close();
    const out = f.replace(/\.html$/, '.pdf');
    await page.pdf({ path: out, preferCSSPageSize: true, printBackground: true });
    console.log('wrote', out, '(' + n + ' gradients flattened)');
    await page.close();
  }
  await browser.close();
})();
