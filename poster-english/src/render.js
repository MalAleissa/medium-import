// usage: node render.js <in.html> <out.pdf|png> [wMM hMM] [scale for png]
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [inp, out, wmm = '850', hmm = '2000', scale = '0.25'] = process.argv.slice(2);
  const browser = await chromium.launch();
  const mm2px = 96 / 25.4;
  const W = Math.round(parseFloat(wmm) * mm2px), H = Math.round(parseFloat(hmm) * mm2px);
  const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: out.endsWith('.png') ? parseFloat(scale) : 1 });
  const page = await ctx.newPage();
  await page.goto('file://' + path.resolve(inp));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);
  if (out.endsWith('.pdf')) {
    await page.pdf({ path: out, width: wmm + 'mm', height: hmm + 'mm', printBackground: true, margin: { top: 0, right: 0, bottom: 0, left: 0 }, pageRanges: '1' });
  } else {
    await page.screenshot({ path: out, clip: { x: 0, y: 0, width: W, height: H } });
  }
  await browser.close();
})();
