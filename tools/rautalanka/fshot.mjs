import { createRequire } from 'module'; const { chromium } = createRequire('/home/claude/.npm-global/lib/node_modules/')('playwright');
import fs from 'fs'; import path from 'path';
// Fast check render: node fshot.mjs outdir/ views.json   (same views format as gshot_sv.mjs; needs the http server on 8765 in the game folder)
// Loads only the baked blocks near each view (tools/rautalanka/fast.html), about 10 s instead of minutes. Final check: gshot_sv.mjs.
const [,, out, viewsJson] = process.argv; const V = JSON.parse(fs.readFileSync(viewsJson));
const GAME = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../..');
const NAMED = ['kivi0', 'kivi1', 'kivi2', 'kivi3', 'kivi4', 'kivi5', 'tori0', 'tori1', 'tori2', 'tori3', 'tori4', 'tori5', 'uima', 'p1', 'kl0', 'kl1', 'karhu'];
const pos = {}; for (const n of NAMED) { try { const h = fs.readFileSync(path.join(GAME, 'bl_' + n + '.js'), { encoding: 'utf8', flag: 'r' }).slice(0, 200); pos[n] = [+h.match(/x = (-?[\d.]+)/)[1], +h.match(/y = (-?[\d.]+)/)[1]]; } catch (e) {} }
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
p.on('pageerror', e => console.log('PAGEERR', String(e).slice(0, 200)));
await p.goto('http://localhost:8765/tools/rautalanka/fast.html', { waitUntil: 'load' });
await p.waitForFunction(() => window.__ready, null, { timeout: 60000 });
for (const v of V) {
  v.named = NAMED.filter(n => pos[n] && Math.hypot(pos[n][0] - v.x, pos[n][1] - v.y) < 450);
  const url = await p.evaluate(v => window.shot(v), v);
  fs.writeFileSync(out + v.k + '.jpg', Buffer.from(url.split(',')[1], 'base64')); console.log(v.k);
}
await b.close();
