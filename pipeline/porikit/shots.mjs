// Screenshots of the game for checking a night's work: node shots.mjs <game dir> <out dir> '[["name",x,y,alt,yaw],...]'
// On a GPU instance Chrome renders with the real GPU (EGL); elsewhere it falls back to SwiftShader.
import puppeteer from 'puppeteer-core'; import http from 'http'; import fs from 'fs'; import path from 'path';
const [root, out, viewsJson] = process.argv.slice(2); const views = JSON.parse(viewsJson);
const mime = { '.html': 'text/html', '.js': 'text/javascript', '.jpg': 'image/jpeg', '.png': 'image/png', '.json': 'application/json' };
const srv = http.createServer((q, r) => { const f = path.join(root, q.url === '/' ? 'index.html' : decodeURIComponent(q.url.split('?')[0]));
  fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'content-type': mime[path.extname(f)] || 'application/octet-stream' }); r.end(d); }); }).listen(8767);
const gpu = fs.existsSync('/dev/nvidia0');
const b = await puppeteer.launch({ executablePath: process.env.CHROME || '/usr/bin/google-chrome', headless: 'new',
  args: ['--no-sandbox', ...(gpu ? ['--use-gl=angle', '--use-angle=gl-egl', '--enable-gpu', '--ignore-gpu-blocklist'] : ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'])] });
const p = await b.newPage(); await p.setViewport({ width: 1600, height: 900 });
const errs = []; p.on('pageerror', e => errs.push(e.message));
await p.goto('http://localhost:8767/'); await p.waitForFunction('window.__ready===true', { timeout: 180000 });
await p.evaluate(() => { __game.begin(); for (const id of ['mission', 'mapwrap', 'gauges', 'help', 'toast', 'street', 'board']) { const e = document.getElementById(id); if (e) e.style.display = 'none'; } });
for (const [name, x, y, alt, yaw] of views) {
  await p.evaluate((x, y, alt, yaw) => { Object.assign(__game.S, { x, y, alt, vx: 0, vy: 0, vz: 0, yaw, landed: false }); __game.snap && __game.snap(); }, x, y, alt, yaw);
  await new Promise(r => setTimeout(r, gpu ? 2500 : 9000));
  await p.screenshot({ path: path.join(out, `v_${name}.jpg`), quality: 85 });
}
console.log(JSON.stringify({ gpu, errors: errs }));
await b.close(); srv.close();
