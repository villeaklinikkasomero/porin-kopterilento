const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const files = process.argv.slice(2);
  const b = await chromium.launch(); const p = await b.newPage();
  for (const fsvg of files) {
    const svg = fs.readFileSync(fsvg, 'utf8');
    const m = svg.match(/width="(\d+)" height="(\d+)"/);
    const w = +m[1], h = +m[2];
    await p.setViewportSize({ width: w, height: h });
    await p.setContent(`<html><body style="margin:0;background:transparent">${svg}</body></html>`);
    await p.waitForTimeout(50);
    await p.screenshot({ path: fsvg.replace(/\.svg$/, '.png'), omitBackground: true, clip: {x:0,y:0,width:w,height:h} });
  }
  await b.close();
})();
