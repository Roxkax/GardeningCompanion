// Usage: node shot.js <input.html> <output.png> [width] [height]
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const [input, output, w = '520', h = '980'] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: 3 });
  await page.goto('file://' + path.resolve(input));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(500);
  const figtree = await page.evaluate(() => document.fonts.check('700 16px Figtree'));
  console.log('Figtree loaded:', figtree);
  await page.screenshot({ path: output });
  await browser.close();
})();
