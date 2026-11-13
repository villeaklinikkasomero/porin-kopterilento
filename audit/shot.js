// Street View -vertailun pelikamera. Liitä koko tiedosto pelin välilehteen (javascript_tool) kerran, ja aina jos sivu ladataan uudelleen.
// Käyttö: await window.__shot(x, y, suunta_astetta)  – x,y metreinä (city.js:n rakennusten p / 10; tiet city.js:ssä jo metreinä).
// Kamera: maanpinta/katto (roofAt) + 1,6 m + ohjaamo 0,9 m. Pelin pystykenttä 58,7° ≈ Street View fov 90 vaakaan 1280×720:ssa.
// Rakennusten id:t näkyvät keltaisina tarroina (110 m säteellä).
const C = (await import('/city.js')).default;
window.__B = C.b.map((b, i) => { const p = b.p, n = p.length / 2; let x = 0, y = 0; for (let k = 0; k < p.length; k += 2) { x += p[k]; y += p[k + 1]; }
  return { i, x: x / n / 10, y: y / n / 10, h: b.h }; });
if (!window.__ov) { window.__ov = document.createElement('div'); window.__ov.style.cssText = 'position:fixed;inset:0;pointer-events:none;z-index:99;font:11px sans-serif'; document.body.appendChild(window.__ov); }
window.__labels = (on = true) => { const ov = window.__ov; ov.innerHTML = ''; if (!on) return; const G = window.__game, cam = G.camera; cam.updateMatrixWorld(); const P = window.__pose; const V = new cam.position.constructor();
  for (const b of window.__B) { const d = Math.hypot(b.x - P.x, b.y - P.y); if (d > 110) continue; const tz = G.TZs(b.x, b.y); V.set(b.x, tz + Math.min(b.h, 12) * 0.5, -b.y).project(cam); if (V.z > 1 || Math.abs(V.x) > 1 || Math.abs(V.y) > 1) continue;
    const e = document.createElement('div'); e.textContent = b.i; e.style.cssText = `position:absolute;left:${(V.x + 1) / 2 * innerWidth}px;top:${(1 - V.y) / 2 * innerHeight}px;background:#ff0;color:#000;padding:1px 4px;border:1px solid #000;transform:translate(-50%,-50%)`; ov.appendChild(e); } };
window.__shot = async (x, y, hd, dz = 0, pitch = 0.55) => { const G = window.__game, S = G.S, cam = G.camera; const z = G.roofAt(x, y) + 1.6 + dz; window.__pose = { x, y, yaw: hd * Math.PI / 180, pitch, z };
  const P = window.__pose; const put = () => { S.x = x; S.y = y; S.alt = z; S.vx = S.vy = S.vz = 0; S.yaw = P.yaw; S.pitch = P.pitch; S.roll = 0; S.yawRate = 0 };
  const sleep = ms => new Promise(r => { const ch = new MessageChannel(); const t0 = performance.now(); ch.port1.onmessage = () => { performance.now() - t0 >= ms ? r() : ch.port2.postMessage(0) }; ch.port2.postMessage(0) });
  for (let k = 0; k < 10; k++) { put(); G.step(0.016); put(); await sleep(350) }      // selainpaneeli usein piilossa → rAF ei pyöri, siksi step() itse
  const sn = Math.sin(P.yaw), cs = Math.cos(P.yaw); cam.position.set(x + sn * 1.6, z + 0.9, -y - cs * 1.6); cam.rotation.order = 'YXZ'; cam.rotation.set(P.pitch * 0.6 - 0.12, -P.yaw, 0); cam.updateMatrixWorld(); window.__labels(); return 1 };
'shot ready';
