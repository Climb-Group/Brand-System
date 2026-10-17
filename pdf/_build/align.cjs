const { chromium } = require('playwright');
const path = require('path');

// Card rows: every price in a row of cards starts on one line, and sits inside its card. A price is a .price or a
// card's .end block; a row is the cards that share a parent and a top edge. Fails the build on a miss of more than
// 1px, so a title that wraps onto a second line can never push one price out of line again.
function scan() {
  const out = [];
  [...document.querySelectorAll('section.s')].forEach((sec, p) => {
    const rows = new Map();
    for (const price of sec.querySelectorAll('.price, .cardx .end')) {
      let card = price;
      while (card.parentElement && card.parentElement !== sec) {
        const d = getComputedStyle(card.parentElement);
        const many = card.parentElement.children.length > 1;
        if (many && (d.display.includes('grid') || (d.display.includes('flex') && !d.flexDirection.startsWith('column')))) break;
        card = card.parentElement;
      }
      if (card.parentElement === sec) continue;
      const c = card.getBoundingClientRect();
      const key = [...sec.querySelectorAll('*')].indexOf(card.parentElement) + ':' + Math.round(c.top);
      if (!rows.has(key)) rows.set(key, []);
      const r = price.getBoundingClientRect();
      rows.get(key).push({ text: price.textContent.trim().slice(0, 30), top: r.top, bottom: r.bottom, cardBottom: c.bottom });
    }
    for (const prices of rows.values()) {
      for (const x of prices) if (x.bottom > x.cardBottom + 1) out.push(`page ${p + 1}: "${x.text}" runs out of its card`);
      if (prices.length < 2) continue;
      const tops = prices.map((x) => x.top);
      if (Math.max(...tops) - Math.min(...tops) > 1)
        out.push(`page ${p + 1}: prices out of line (${prices.map((x) => `"${x.text}" at ${Math.round(x.top)}`).join(', ')})`);
    }
  });
  return out;
}

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  let bad = 0;
  for (const f of process.argv.slice(2)) {
    await page.goto('file://' + path.resolve(f));
    await page.evaluate(() => document.fonts.ready);
    for (const m of await page.evaluate(scan)) { console.log(path.basename(f) + ' ' + m); bad++; }
  }
  await browser.close();
  if (bad) { console.log(bad + ' card price problem(s)'); process.exit(1); }
  console.log('Card prices line up');
})();
