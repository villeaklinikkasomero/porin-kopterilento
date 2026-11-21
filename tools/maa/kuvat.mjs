// Vaiheen 0 testikuvat maan tasolta, 21.11.2026 (MAAN_PINTA_SUUNNITELMA.md).
//
//   node tools/maa/kuvat.mjs <tunniste> [url]          esim. node tools/maa/kuvat.mjs ennen http://localhost:8124/index.html
//   PISTEET=k01,k05,u02 node tools/maa/kuvat.mjs testi   vain osa pisteistä
//
// Lukee tools/maa/pisteet.json (tee: python tools/maa/pisteet.py). Jokaisesta pisteestä kaksi kuvaa: silmät 1,7 m katse -8° (_s)
// ja maahan päin -38° (_m). Tulos: tools/maa/kuvat/<tunniste>/<id>_s.jpg, <id>_m.jpg ja koonti.html (rinnakkain, jos kansiossa on useampi tunniste:
// node tools/maa/kuvat.mjs --koonti ennen jalkeen). Vaatii Playwrightin (npm i playwright; Chromium) ja pelin palvelimen
// (tools/palvelin.ps1 tai python -m http.server). Ilman näytönohjainta käytetään SwiftShaderia (hidas: ~1 min / piste).
import { createRequire } from 'module'; import fs from 'fs'; import path from 'path'; import { fileURLToPath } from 'url';
const require = createRequire(import.meta.url); const HERE = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);

if (args[0] === '--koonti') {      // vertailusivu
  const tags = args.slice(1), P = JSON.parse(fs.readFileSync(path.join(HERE, 'pisteet.json'), 'utf8'));
  let h = '<!DOCTYPE html><meta charset="utf-8"><title>Maan pinta: ' + tags.join(' vs ') + '</title><style>body{font:14px sans-serif;background:#222;color:#eee}img{width:' + (96 / tags.length) + 'vw;max-width:640px}td{vertical-align:top}</style><table>';
  h += '<tr><th></th>' + tags.map(t => '<th>' + t + '</th>').join('') + '</tr>';
  for (const p of P) for (const v of ['s', 'm']) h += `<tr><td>${p.id}<br>${p.nimi}<br>${v === 's' ? 'silmät' : 'maa'}</td>` + tags.map(t => `<td><img src="${t}/${p.id}_${v}.jpg" loading="lazy"></td>`).join('') + '</tr>';
  fs.writeFileSync(path.join(HERE, 'kuvat', 'koonti_' + tags.join('_') + '.html'), h + '</table>');
  console.log('koonti:', path.join(HERE, 'kuvat', 'koonti_' + tags.join('_') + '.html')); process.exit(0);
}

const { chromium } = require('playwright');
const tag = args[0] || 'nyt', URL = args[1] || process.env.URL || 'http://localhost:8124/index.html';
let P = JSON.parse(fs.readFileSync(path.join(HERE, 'pisteet.json'), 'utf8'));
if (process.env.PISTEET) { const s = new Set(process.env.PISTEET.split(',')); P = P.filter(p => s.has(p.id)); }
const OUT = path.join(HERE, 'kuvat', tag); fs.mkdirSync(OUT, { recursive: true });
const gpu = process.env.GPU === '1';
let b, pg; const logs = [];
async function avaa() {           // selain ja peli auki; kaatuessa (SwiftShader / muisti) avataan uudelleen ja jatketaan
  if (b) await b.close().catch(() => {});
  b = await chromium.launch({ args: gpu ? ['--ignore-gpu-blocklist'] : ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  pg = await b.newPage({ viewport: { width: +(process.env.W || 1280), height: +(process.env.H || 720) } });
  pg.on('pageerror', e => logs.push('pageerror: ' + e.message));
  await pg.goto(URL, { waitUntil: 'load', timeout: 180000 });
  await pg.waitForFunction(() => window.__game && window.__game.scene, null, { timeout: 180000 });
  await pg.evaluate(() => { for (const id of ['start', 'mission', 'prog', 'mapwrap', 'gauges', 'hp', 'rctl', 'rinfo', 'street', 'nav', 'toast', 'hint', 'radio', 'board', 'help', 'credit', 'touch', 'energia', 'hud']) { const e = document.getElementById(id); if (e) e.style.display = 'none'; } });
}
const meta = [];
let first = true;
await avaa();
for (const p of P) {
  if (!process.env.UUDET && fs.existsSync(path.join(OUT, `${p.id}_s.jpg`)) && fs.existsSync(path.join(OUT, `${p.id}_m.jpg`))) { console.log(p.id, 'on jo'); continue; }
  for (let yritys = 0; yritys < 3; yritys++) {
    try { await kuvaa(p); break; }
    catch (e) { console.log(p.id, 'virhe:', e.message.split('\n')[0], '-> avataan uudelleen'); logs.push(p.id + ': ' + e.message.split('\n')[0]); first = true; await avaa(); }
  }
}
async function kuvaa(p) {
  // pois rakennuksen sisältä: spiraalihaku 20 m
  const q = await pg.evaluate(([x, y]) => { const G = window.__game, ok = (a, b) => !(G.bldTopAt && G.bldTopAt(a, b) > G.TZs(a, b) + 1.2);
    if (ok(x, y)) return [x, y, 0]; for (let r = 1; r <= 20; r++) for (let k = 0; k < 16; k++) { const a = x + r * Math.cos(k * Math.PI / 8), b = y + r * Math.sin(k * Math.PI / 8); if (ok(a, b)) return [a, b, r]; } return [x, y, -1]; }, [p.x, p.y]);
  const [X, Y] = q;
  await pg.evaluate(([X, Y]) => { const G = window.__game, S = G.S; S.x = X; S.y = Y; S.alt = 1500; S.vx = S.vy = S.vz = 0; G.camera.position.set(X, G.TZs(X, Y) + 1.7, -Y); G.world(X, Y); window.__rataCam && window.__rataCam(X, Y); }, [X, Y]);
  await pg.waitForTimeout(first ? +(process.env.WAIT || 20000) : 7000); first = false;
  for (const [v, pitch] of [['s', -8], ['m', -38]]) {
    await pg.evaluate(([X, Y, hd, pt]) => { const G = window.__game; G.camera.position.set(X, G.TZs(X, Y) + 1.7, -Y); G.world(X, Y);
      const fc = G.camera.clone(); fc.fov = 65; fc.aspect = innerWidth / innerHeight; fc.near = 0.1; fc.far = 8000; fc.updateProjectionMatrix();
      const z = (window.__game.carGround ? (window.__game.carGround(X, Y, G.TZs(X, Y) + 5) ?? G.TZs(X, Y)) : G.TZs(X, Y)) + 1.7;
      fc.position.set(X, z, -Y); fc.rotation.order = 'YXZ'; fc.rotation.set(pt * Math.PI / 180, -hd * Math.PI / 180, 0); fc.updateMatrixWorld();
      G.camera.position.copy(fc.position); G.camera.quaternion.copy(fc.quaternion);
      window.__fc = fc; if (!G.renderer.__p) { const o = G.renderer.render.bind(G.renderer); G.renderer.__p = 1; G.renderer.render = (s, c) => o(s, (c === G.camera && window.__fc) ? window.__fc : c); } G.renderer.render(G.scene, fc); }, [X, Y, p.katse, pitch]);
    await pg.waitForTimeout(3000);
    await pg.screenshot({ path: path.join(OUT, `${p.id}_${v}.jpg`), type: 'jpeg', quality: 85 });
  }
  meta.push({ ...p, x_kuva: +X.toFixed(1), y_kuva: +Y.toFixed(1), siirto_m: q[2] });
  console.log(p.id, p.nimi, q[2] ? `(siirretty ${q[2]} m)` : '');
}
fs.writeFileSync(path.join(OUT, 'pisteet.json'), JSON.stringify({ tunniste: tag, url: URL, aika: new Date().toISOString(), pisteet: meta, virheet: logs.slice(0, 30) }, null, 1));
await b.close();
console.log('valmis:', OUT, logs.length ? logs.length + ' virhettä' : '');
