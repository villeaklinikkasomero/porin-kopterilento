// moduulit/hautausmaat.js – siirretty pääskriptistä (src/js/101_hautausmaat.js) omaksi moduulikseen 21.11.2026.
// Pääskriptin muuttujat tulevat oliossa P (getterit pitävät ne ajan tasalla); kirjastot ja data tuodaan suoraan.
// Kutsu ja P:n sisältö: src/js/101_hautausmaat.js. Uusi riippuvuus pääskriptiin → lisää se sinne P-olioon.
import * as THREE from '../three.module.min.js';
import CITY from '../city.js';

// ---------- cemeteries: rows of gravestones ----------
export default function kaynnista(P) {
{
  const spots = [];
  for (const c of CITY.cem || []) { const pts = []; for (let i = 0; i < c.p.length; i += 2) pts.push([c.p[i], c.p[i + 1]]);
    let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9; for (const q of pts) { x0 = Math.min(x0, q[0]); x1 = Math.max(x1, q[0]); y0 = Math.min(y0, q[1]); y1 = Math.max(y1, q[1]); }
    const big = (x1 - x0) * (y1 - y0) > 60000, sx = big ? 3.4 : 2.8, sy = big ? 6.5 : 5.2; let sd = 5; const rnd = () => (sd = (sd * 16807) % 2147483647) / 2147483647;
    for (let y = y0 + 3; y < y1 - 3; y += sy) for (let x = x0 + 3; x < x1 - 3; x += sx) { if (rnd() < 0.22) continue; const px = x + (rnd() - 0.5) * 0.5, py = y + (rnd() - 0.5) * 0.4;
      if (P.pip(px, py, pts) && !P.roofAt(px, py)) spots.push([px, py, rnd()]); } }
  const n = Math.min(spots.length, 9000), g = new THREE.BoxGeometry(0.7, 0.95, 0.16); g.translate(0, 0.47, 0);
  const im = new THREE.InstancedMesh(g, new THREE.MeshLambertMaterial(), n), m = new THREE.Matrix4(), c = new THREE.Color(), SC = [0x3a3d42, 0x55585c, 0x8a8d90, 0x6a3f38, 0xb9b6ae, 0x2a2c30];
  for (let i = 0; i < n; i++) { const s = spots[i], k = 0.8 + s[2] * 0.5; m.makeScale(k, 0.7 + s[2] * 0.8, 1); m.setPosition(s[0], 0, -s[1]); im.setMatrixAt(i, m); im.setColorAt(i, c.setHex(SC[Math.floor(s[2] * 97) % SC.length])); }
  P.scene.add(im); window.__stones = n;
}
}
