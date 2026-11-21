// moduulit/kivipori_maamerkit.js – siirretty pääskriptistä (src/js/041_kivipori_maamerkit.js) omaksi moduulikseen 21.11.2026.
// Pääskriptin muuttujat tulevat oliossa _P (getterit pitävät ne ajan tasalla); kirjastot ja data tuodaan suoraan.
// Kutsu ja _P:n sisältö: src/js/041_kivipori_maamerkit.js. Uusi riippuvuus pääskriptiin → lisää se sinne _P-olioon.
import * as THREE from '../three.module.min.js';
import CITY from '../city.js';
import RIV from '../river.js';
import TER from '../terrain.js';
import { GLTFLoader } from '../GLTFLoader.js';

// ---------- Kivi-Porin maamerkit: yksilölliset mallit ----------
export default function kaynnista(_P) {
{
  const add = (g, m) => { const o = new THREE.Mesh(g, m); _P.scene.add(o); return o; };
  const lam = (c, o = {}) => new THREE.MeshLambertMaterial({ color: c, ...o });
  const STONE = lam(0x8f8b84), TRIM = lam(0xf2eee3), DS = { side: THREE.DoubleSide };
  const fattr = (a, n) => new THREE.Float32BufferAttribute(a, n);
  function clean(pts) {
    const o = [], n = pts.length;
    for (let i = 0; i < n; i++) { const a = pts[(i + n - 1) % n], b = pts[i], c = pts[(i + 1) % n];
      const cr = Math.abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])), d = Math.hypot(c[0] - a[0], c[1] - a[1]) || 1;
      if (cr / d > 0.5) o.push(b); }
    return o.length >= 3 ? o : pts;
  }
  function offset(pts, d) { // d > 0 grows a counter-clockwise polygon
    const n = pts.length, o = [];
    for (let i = 0; i < n; i++) { const a = pts[(i + n - 1) % n], b = pts[i], c = pts[(i + 1) % n];
      const e1x = b[0] - a[0], e1y = b[1] - a[1], e2x = c[0] - b[0], e2y = c[1] - b[1], l1 = Math.hypot(e1x, e1y) || 1, l2 = Math.hypot(e2x, e2y) || 1;
      const n1x = e1y / l1, n1y = -e1x / l1; let mx = n1x + e2y / l2, my = n1y - e2x / l2; const ml = Math.hypot(mx, my) || 1; mx /= ml; my /= ml;
      const k = d / Math.max(0.4, mx * n1x + my * n1y); o.push([b[0] + mx * k, b[1] + my * k]); }
    return o;
  }
  function wallGeo(pts, y0, y1, bay = 0, floors = 1) {
    const p = [], nn = [], u = [], n = pts.length;
    for (let i = 0; i < n; i++) { const a = pts[i], c = pts[(i + 1) % n], dx = c[0] - a[0], dy = c[1] - a[1], len = Math.hypot(dx, dy); if (len < 0.05) continue;
      const ub = !bay ? 1 : len < bay * 0.6 ? 0.04 : Math.max(1, Math.round(len / bay));
      p.push(a[0], y0, -a[1], c[0], y0, -c[1], c[0], y1, -c[1], a[0], y0, -a[1], c[0], y1, -c[1], a[0], y1, -a[1]);
      u.push(0, 0, ub, 0, ub, floors, 0, 0, ub, floors, 0, floors); for (let k = 0; k < 6; k++) nn.push(dy / len, 0, dx / len); }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', fattr(p, 3)); g.setAttribute('normal', fattr(nn, 3)); g.setAttribute('uv', fattr(u, 2)); return g;
  }
  const tri = pts => THREE.ShapeUtils.triangulateShape(pts.map(q => new THREE.Vector2(q[0], q[1])), []);
  function capGeo(pts, y, orto = false) {
    const p = [], u = []; for (const t of tri(pts)) for (const k of t) { p.push(pts[k][0], y, -pts[k][1]); u.push((pts[k][0] + _P.HW) / (2 * _P.HW), (pts[k][1] - _P.YS) / _P.YSPAN); }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', fattr(p, 3)); if (orto) g.setAttribute('uv', fattr(u, 2)); g.computeVertexNormals(); return g;
  }
  function hipGeo(e, t, y0, y1) {
    const p = [], n = e.length;
    for (let i = 0; i < n; i++) { const j = (i + 1) % n, a = e[i], b = e[j], c = t[j], d = t[i];
      p.push(a[0], y0, -a[1], b[0], y0, -b[1], c[0], y1, -c[1], a[0], y0, -a[1], c[0], y1, -c[1], d[0], y1, -d[1]); }
    for (const tr of tri(t)) for (const k of tr) p.push(t[k][0], y1, -t[k][1]);
    const g = new THREE.BufferGeometry(); g.setAttribute('position', fattr(p, 3)); g.computeVertexNormals(); return g;
  }
  function obb(pts) {
    let best = null;
    for (let i = 0; i < pts.length; i++) { const a = pts[i], b = pts[(i + 1) % pts.length], L = Math.hypot(b[0] - a[0], b[1] - a[1]); if (L < 3) continue;
      let ux = (b[0] - a[0]) / L, uy = (b[1] - a[1]) / L; if (ux < 0) { ux = -ux; uy = -uy; }
      let u0 = 1e9, u1 = -1e9, v0 = 1e9, v1 = -1e9; for (const q of pts) { const u = q[0] * ux + q[1] * uy, v = -q[0] * uy + q[1] * ux; u0 = Math.min(u0, u); u1 = Math.max(u1, u); v0 = Math.min(v0, v); v1 = Math.max(v1, v); }
      const ar = (u1 - u0) * (v1 - v0); if (!best || ar < best.ar) { const cu = (u0 + u1) / 2, cv = (v0 + v1) / 2; best = { ar, ux, uy, a: (u1 - u0) / 2, b: (v1 - v0) / 2, cx: cu * ux - cv * uy, cy: cu * uy + cv * ux }; } }
    return best;
  }
  // local frame: +X along the footprint axis, +Z to its right (southwards when the axis points east)
  function frame(o) { const g = new THREE.Group(); g.position.set(o.cx, 0, -o.cy); g.rotation.y = Math.atan2(o.uy, o.ux); _P.scene.add(g); return g; }
  const toMap = (o, lx, lz) => [o.cx + o.ux * lx + o.uy * lz, o.cy + o.uy * lx - o.ux * lz];
  function block(x, y, r, h) { const rec = { pts: [[x - r, y - r], [x + r, y - r], [x + r, y + r], [x - r, y + r]], h, minx: x - r, maxx: x + r, miny: y - r, maxy: y + r };
    const bi = _P.blds.push(rec) - 1; for (let i = Math.floor((x - r - 5) / _P.GRID); i <= Math.floor((x + r + 5) / _P.GRID); i++) for (let j = Math.floor((y - r - 5) / _P.GRID); j <= Math.floor((y + r + 5) / _P.GRID); j++) { const k = _P.gkey(i + 100, j + 100); if (!_P.grid.has(k)) _P.grid.set(k, []); _P.grid.get(k).push(bi); } }

  // one window bay per texture tile
  function facade({ wall, trim = '#f2eee3', glass = '#2a3846', arch = true, win = [0.3, 0.17, 0.4, 0.62], pil = true, course = true, brick = false, band = false, diamond = null, pair = false, rust = false }) {
    const W = 128, H = 176, c = document.createElement('canvas'); c.width = W; c.height = H; const x = c.getContext('2d');
    x.fillStyle = wall; x.fillRect(0, 0, W, H);
    if (brick) { x.strokeStyle = 'rgba(0,0,0,.16)'; x.lineWidth = 1; for (let y = 0; y < H; y += 6) { x.beginPath(); x.moveTo(0, y + .5); x.lineTo(W, y + .5); x.stroke(); for (let bx = (y / 6 % 2) * 8; bx < W; bx += 16) { x.beginPath(); x.moveTo(bx + .5, y); x.lineTo(bx + .5, y + 6); x.stroke(); } } }
    if (diamond) { x.strokeStyle = diamond; x.lineWidth = 2.2; for (let k = -H; k < W + H; k += 16) { x.beginPath(); x.moveTo(k, 0); x.lineTo(k + H, H); x.stroke(); x.beginPath(); x.moveTo(k, H); x.lineTo(k + H, 0); x.stroke(); } }
    if (rust) { x.fillStyle = 'rgba(0,0,0,.16)'; for (let y = 0; y < H; y += 22) x.fillRect(0, y, W, 3); }
    if (pil) { x.fillStyle = trim; x.globalAlpha = brick ? 0.0 : 0.6; x.fillRect(0, 0, 9, H); x.globalAlpha = 1; x.fillStyle = 'rgba(0,0,0,.10)'; x.fillRect(9, 0, 2, H); }
    if (band) { x.fillStyle = glass; x.fillRect(0, H * 0.25, W, H * 0.5); x.fillStyle = trim; for (let i = 0; i < W; i += 32) x.fillRect(i, H * 0.25, 5, H * 0.5); }
    else {
      const wx = W * win[0], wy = H * win[1], ww = W * win[2], wh = H * win[3], r = ww / 2, m = 6;
      const shape = (g) => { x.beginPath(); if (arch) { x.moveTo(wx - g, wy + wh + g); x.lineTo(wx - g, wy + r); x.arc(wx + r, wy + r, r + g, Math.PI, 0); x.lineTo(wx + ww + g, wy + wh + g); } else x.rect(wx - g, wy - g, ww + 2 * g, wh + 2 * g); x.closePath(); };
      x.fillStyle = trim; shape(m); x.fill(); x.fillStyle = 'rgba(0,0,0,.18)'; x.fillRect(wx - m, wy + wh + m, ww + 2 * m, 3);
      x.fillStyle = glass; shape(0); x.fill();
      const gr = x.createLinearGradient(0, wy, 0, wy + wh); gr.addColorStop(0, 'rgba(160,190,215,.55)'); gr.addColorStop(0.5, 'rgba(160,190,215,0)'); x.fillStyle = gr; shape(0); x.fill();
      x.fillStyle = trim; x.fillRect(wx + r - (pair ? 4 : 1.5), wy, pair ? 8 : 3, wh); for (const f of [0.38, 0.69]) x.fillRect(wx, wy + wh * f, ww, 2.5);
      x.fillRect(wx - m - 4, wy + wh + m - 2, ww + 2 * m + 8, 5);
    }
    if (course) { x.fillStyle = trim; x.fillRect(0, 0, W, 7); x.fillStyle = 'rgba(0,0,0,.2)'; x.fillRect(0, 7, W, 2); }
    const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return new THREE.MeshLambertMaterial({ map: t });
  }

  // plinth + windowed walls + cornice + roof for a stone-town building
  function styled(L, { h, floors, bay, mat, roof, base, trim = TRIM }) {
    const pts = clean(L.pts);
    add(wallGeo(offset(pts, 0.14), 0, 1.1), STONE); const y0 = base ? base.h : 1.1; if (base) { add(wallGeo(offset(pts, 0.08), 1.1, y0, bay, 1), base.mat); add(wallGeo(offset(pts, 0.3), y0 - 0.35, y0, 0, 1), TRIM); }
    add(wallGeo(pts, y0, h - 0.7, bay, floors), mat);
    const co = offset(pts, 0.45); add(wallGeo(co, h - 0.7, h), trim); add(capGeo(co, h - 0.03), trim);
    if (roof) { add(hipGeo(offset(pts, 0.6), offset(pts, -roof.inset), h, h + roof.rise), lam(roof.color, DS)); L.rec.h = h + roof.rise; }
    else { add(capGeo(pts, h + 0.03, true), _P.roofMat); L.rec.h = h; }
    return pts;
  }

  // Blender-built models (sunlight and soft shadows baked into one texture) replace the code-built ones once they have loaded
  const LM_ONE = new Set(['kaupungintalo']);   // landmarks lifted as one piece (owner 15.11: the museum on its slope sank and lost its roof when all were)
  function track(key, fn) {
    const start = _P.scene.children.length; fn(); const proc = _P.scene.children.slice(start);
    import(`../bl_${key}.js`).then(K => {
      const bin = atob(K.default), buf = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
      new GLTFLoader().parse(buf.buffer, '', gl => {
        gl.scene.traverse(q => { if (q.isMesh) { const map = q.material.map; if (map) { map.anisotropy = 8; _P.TEXLOD.add(map, K.x, K.y); } q.material = _P.brickify(_P.glassify(new THREE.MeshBasicMaterial({ map }))); } });
        const g = new THREE.Group(); const L0 = _P.LMB[key]; let z0 = null; if (L0 && L0.pts && LM_ONE.has(key)) { z0 = 1e9; z0 = 0; for (const q of L0.pts) z0 += _P.TZs(q[0], q[1]) / L0.pts.length; if (!isFinite(z0)) z0 = null; }   /* owner 15.11.2026: the Kaupungintalo stood with its stone ground floor under the street - a landmark stands as one piece on the mean ground under it */
        g.position.set(K.x, z0 === null ? 0 : z0, -K.y); g.add(gl.scene); _P.scene.add(z0 === null ? g : _P.noT(g));
        for (const q of proc) if (K.roof || q.material !== _P.roofMat) _P.scene.remove(q);
        (window.__bl = window.__bl || []).push(key);
      }, () => {});
    }).catch(() => {});
  }
  // landmarks outside the core: plain stand-ins until their Blender models have loaded
  const plain = (L, h, c) => { const pts = clean(L.pts); add(wallGeo(pts, 0, h), lam(c)); add(capGeo(pts, h), lam(0x8a8d90)); L.rec.h = h; };
  for (const [k, h, c] of [['mausoleumi', 12, 0xd9d4c8], ['areena', 16, 0xcfd3d6], ['isokappeli', 9, 0xe8e2d2], ['pienikappeli', 7, 0xe8e2d2], ['harjoitushalli', 10, 0xcfd3d6], ['asema', 12.6, 0xe8d7a0], ['samk', 28, 0xd8dadb], ['cygnaeus', 22.9, 0xd8b56a]]) if (_P.LMB[k]) track(k, () => plain(_P.LMB[k], h, c));
  // Raatihuone (C. L. Engel, 1841): cream empire facade, three rows of windows, pedimented centre, tall clock tower
  if (_P.LMB.raati) track('raati', () => {
    const L = _P.LMB.raati, h = 13.5, rise = 3, wallC = 0xefe3ba;
    const pts = styled(L, { h, floors: 3, bay: 3.1, mat: facade({ wall: '#efe3ba', arch: false, win: [0.33, 0.2, 0.34, 0.56] }), roof: { inset: 6.2, rise, color: 0x7fb7a6 } });
    const o = obb(pts), g = frame(o), W = 14, z = o.b;
    const m = (geo, mat, x, y, zz) => { const q = new THREE.Mesh(geo, mat); q.position.set(x, y, zz); g.add(q); return q; };
    const ris = m(new THREE.BoxGeometry(W, h - 0.7, 1.0), facade({ wall: '#efe3ba', arch: false, win: [0.33, 0.2, 0.34, 0.56] }), 0, (h - 0.7) / 2, z + 0.5);
    { const uv = ris.geometry.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * 5, uv.getY(i) * 3); }
    for (const cx of [-7, -4.2, -1.4, 1.4, 4.2, 7]) m(new THREE.BoxGeometry(0.55, h - 5, 0.25), TRIM, cx * 0.97, 4.4 + (h - 5) / 2 - 0.4, z + 1.08);
    m(new THREE.BoxGeometry(W + 0.5, 0.8, 1.5), TRIM, 0, h - 0.5, z + 0.6);
    const sh = new THREE.Shape(); sh.moveTo(-W / 2 - 0.3, 0); sh.lineTo(W / 2 + 0.3, 0); sh.lineTo(0, 2.6); sh.closePath();
    m(new THREE.ExtrudeGeometry(sh, { depth: 1.5, bevelEnabled: false }), TRIM, 0, h - 0.1, z - 0.2);
    const top = h + rise - 0.6, green = lam(0x6fae9c), dark = lam(0x1d2630);
    const wallM = lam(wallC);                                                                             // clock tower (14.11.2026): base + balcony, tall yellow stage, bell roof, lantern
    m(new THREE.BoxGeometry(5.2, 2.3, 5.2), wallM, 0, top + 1.15, 0);
    m(new THREE.BoxGeometry(5.9, 0.25, 5.9), TRIM, 0, top + 2.42, 0);
    m(new THREE.BoxGeometry(5.8, 0.9, 5.8), new THREE.MeshLambertMaterial({ color: 0x2a2f33, wireframe: true }), 0, top + 3.0, 0);
    m(new THREE.BoxGeometry(3.5, 6.85, 3.5), wallM, 0, top + 5.97, 0);
    for (const [sx, sz] of [[-1, -1], [1, -1], [1, 1], [-1, 1]]) m(new THREE.BoxGeometry(0.48, 6.85, 0.48), TRIM, sx * 1.6, top + 5.97, sz * 1.6);
    for (let i = 0; i < 4; i++) { const q = m(new THREE.CircleGeometry(0.68, 20), lam(0xe8e3d4), Math.sin(i * Math.PI / 2) * 1.77, top + 7.9, Math.cos(i * Math.PI / 2) * 1.77); q.rotation.y = i * Math.PI / 2; }
    m(new THREE.BoxGeometry(3.94, 0.3, 3.94), TRIM, 0, top + 9.55, 0);
    { const pr = []; for (let k = 0; k <= 6; k++) { const t = k / 6; pr.push(new THREE.Vector2(0.6 + (2.0 - 0.6) * Math.sqrt(Math.max(0, 1 - Math.pow(t, 1.6))), t * 2.1)); }
      m(new THREE.LatheGeometry(pr, 8), green, 0, top + 9.7, 0).rotation.y = Math.PI / 8; }
    m(new THREE.CylinderGeometry(0.6, 0.6, 1.2, 8), green, 0, top + 12.4, 0);
    m(new THREE.CylinderGeometry(0.1, 0.5, 1.1, 8), green, 0, top + 13.6, 0);
    m(new THREE.ConeGeometry(0.06, 2.2, 6), dark, 0, top + 15.2, 0);
    L.rec.h = h + rise; const tc = toMap(o, 0, 0); block(tc[0], tc[1], 3, top + 13);
  });
  // Kaupungintalo, Junneliuksen palatsi (1895): Venetian palazzo, diamond-patterned brick above a rusticated stone ground floor
  if (_P.LMB.kaupungintalo) track('kaupungintalo', () => {
    const L = _P.LMB.kaupungintalo, h = 17;
    styled(L, { h, floors: 2, bay: 3.4, base: { h: 6.2, mat: facade({ wall: '#8d7f70', trim: '#b9ad9c', rust: true, pil: false, course: false, win: [0.3, 0.2, 0.4, 0.6] }) },
      mat: facade({ wall: '#c87850', trim: '#ead9c0', diamond: 'rgba(250,222,190,.85)', pair: true, pil: false, win: [0.24, 0.2, 0.52, 0.56] }), roof: { inset: 3, rise: 0.9, color: 0x4b5157 } });
  });
  // Porin Teatteri (1884): yellow neo-renaissance
  if (_P.LMB.teatteri) track('teatteri', () => styled(_P.LMB.teatteri, { h: 12.5, floors: 2, bay: 3.6, mat: facade({ wall: '#ecd9a0', arch: true, win: [0.3, 0.14, 0.4, 0.66] }) }));
  // Porin taidemuseo: former customs warehouse, pale rusticated plaster and tall arched openings
  if (_P.LMB.taidemuseo) track('taidemuseo', () => styled(_P.LMB.taidemuseo, { h: 8.2, floors: 1, bay: 6.2, mat: facade({ wall: '#d9d3c4', trim: '#ece8dd', rust: true, arch: true, glass: '#22303a', win: [0.26, 0.2, 0.48, 0.7] }) }));
  // Kauppahalli (1927)
  if (_P.LMB.kauppahalli) track('kauppahalli', () => styled(_P.LMB.kauppahalli, { h: 8.5, floors: 2, bay: 4.2, mat: facade({ wall: '#d8c88e', arch: true, win: [0.26, 0.16, 0.48, 0.62] }) }));
  // Vesitorni (Bertel Strömmer, 1935): dark red-brick slab with a rounded stair turret
  if (_P.LMB.vesitorni) track('vesitorni', () => {
    const L = _P.LMB.vesitorni, pts = clean(L.pts), h = 47, o = obb(pts), g = frame(o), brickM = lam(0x8a3e2e);
    add(wallGeo(offset(pts, 0.25), 0, 2.2), STONE);
    add(wallGeo(pts, 2.2, h, 4.9, 8), facade({ wall: '#8a3e2e', trim: '#cdb48e', brick: true, arch: false, pil: false, win: [0.44, 0.3, 0.12, 0.34] }));
    add(capGeo(pts, h), lam(0x5a4a44)); add(wallGeo(offset(pts, 0.25), h - 0.5, h + 0.9), brickM);
    const tur = new THREE.Mesh(new THREE.CylinderGeometry(2.5, 2.5, h + 4, 18), brickM); tur.position.set(0, (h + 4) / 2, -o.b); g.add(tur);
    for (let y = 8; y < h; y += 7.5) { const r = new THREE.Mesh(new THREE.CylinderGeometry(2.56, 2.56, 0.35, 18), lam(0xcdb48e)); r.position.set(0, y, -o.b); g.add(r); }
    const cap = new THREE.Mesh(new THREE.CylinderGeometry(2.7, 2.7, 0.5, 18), lam(0x4a3a35)); cap.position.set(0, h + 4.2, -o.b); g.add(cap);
    L.rec.h = h + 1; const tc = toMap(o, 0, -o.b); block(tc[0], tc[1], 3, h + 4.5);
  });
  // Kauppakeskus Puuvilla (2014): red brick and glass, red canopy band
  if (_P.LMB.puuvilla) track('puuvilla', () => {
    const L = _P.LMB.puuvilla, pts = clean(L.pts), h = 14;
    add(wallGeo(pts, 0, 5, 6, 1), facade({ wall: '#2b3540', trim: '#55626e', glass: '#3f5568', arch: false, pil: false, course: false, win: [0.06, 0.1, 0.88, 0.8] }));
    add(wallGeo(pts, 5, h - 1.2, 6, 2), facade({ wall: '#a8473a', trim: '#8c382e', brick: true, arch: false, pil: false, course: false, glass: '#33414d', win: [0.3, 0.3, 0.4, 0.36] }));
    const co = offset(pts, 0.8); add(wallGeo(co, h - 1.2, h), lam(0xd2232a)); add(capGeo(co, h - 0.03), lam(0xd2232a)); add(wallGeo(co, 4.8, 5.4), lam(0xd2232a));
    add(capGeo(pts, h + 0.03, true), _P.roofMat); L.rec.h = h;
  });
  // Keski-Porin kirkko (1863): red-brick Gothic Revival, 72 m tower with a cast-iron spire
  if (_P.LMB.kirkko) {
    const procStart = _P.scene.children.length;
    const L = _P.LMB.kirkko, pts = L.pts, o = obb(pts), g = frame(o), a = o.a, b = o.b, eave = 15, ridge = 27.5;
    _P.CHURCH.map = (lx, lz) => toMap(o, lx, lz);   // model-local (x along the nave towards the altar, z across) -> map metres
    const BR = 0x9a4a36, brick = lam(BR), slate = lam(0x79a892, DS), copper = lam(0x79a892, DS), iron = lam(0x2a3331, { flatShading: true }), pale = lam(0x8a4030);
    add(wallGeo(offset(pts, 0.2), 0, 1.4), STONE);
    add(wallGeo(pts, 1.4, eave, 5.6, 1), facade({ wall: '#9a4a36', trim: '#d8ccb6', brick: true, arch: true, course: false, win: [0.36, 0.14, 0.28, 0.7] }));
    add(capGeo(pts, eave), lam(0x6a5a52));
    const m = (geo, mat, x, y, z) => { const q = new THREE.Mesh(geo, mat); q.position.set(x, y, z); g.add(q); return q; };
    const hw = b - 2.8, x0 = -a + 11, x1 = a - 10;
    { const P = { A: [x0, eave, hw], B: [x1, eave, hw], C: [x1, ridge, 0], D: [x0, ridge, 0], E: [x0, eave, -hw], F: [x1, eave, -hw] };
      const f = s => s.split('').flatMap(k => P[k]);
      const rg = new THREE.BufferGeometry(); rg.setAttribute('position', fattr(f('ABCACDFEDFDC'), 3)); rg.computeVertexNormals(); g.add(new THREE.Mesh(rg, slate));
      const gg = new THREE.BufferGeometry(); gg.setAttribute('position', fattr(f('BFCEAD'), 3)); gg.computeVertexNormals(); g.add(new THREE.Mesh(gg, lam(BR, DS))); }
    m(new THREE.ConeGeometry(hw, 11, 10, 1, true, 0, Math.PI), copper, x1, eave + 5.5, 0);            // apse roof
    for (let x = x0 + 2.5; x < x1 - 1; x += 5.6) for (const s of [-1, 1]) {                              // buttresses + pinnacles
      m(new THREE.BoxGeometry(1.3, eave + 1.5, 1.8), brick, x, (eave + 1.5) / 2, s * (b - 1.1));
      m(new THREE.ConeGeometry(0.85, 3.6, 4), pale, x, eave + 3.3, s * (b - 1.1)).rotation.y = Math.PI / 4;
    }
    const tx = -a + 5.4, th = 40, tw = 9.6;                                                              // west tower
    m(new THREE.BoxGeometry(tw, th, tw), brick, tx, th / 2, 0);
    for (let i = 0; i < 4; i++) { const sx = Math.sin(i * Math.PI / 2), cz = Math.cos(i * Math.PI / 2);
      const op = m(new THREE.PlaneGeometry(2.4, 6.5), lam(0x1c2228), tx + sx * (tw / 2 + 0.06), 31, cz * (tw / 2 + 0.06)); op.rotation.y = i * Math.PI / 2;
      const cl = m(new THREE.CircleGeometry(1.5, 20), lam(0xe9e4d6), tx + sx * (tw / 2 + 0.07), 23, cz * (tw / 2 + 0.07)); cl.rotation.y = i * Math.PI / 2; }
    m(new THREE.BoxGeometry(tw + 0.9, 0.9, tw + 0.9), lam(0xd8ccb6), tx, th, 0);
    for (const sx of [-1, 1]) for (const sz of [-1, 1]) m(new THREE.ConeGeometry(1.0, 8, 6), iron, tx + sx * 4.3, th + 4.4, sz * 4.3);
    const spire = new THREE.ConeGeometry(4.5, 31, 8, 6); m(spire, iron, tx, th + 15.9, 0).rotation.y = Math.PI / 8;
    const ln = new THREE.LineSegments(new THREE.WireframeGeometry(spire), new THREE.LineBasicMaterial({ color: 0x8fa39c, transparent: true, opacity: 0.6 })); ln.position.set(tx, th + 15.9, 0); ln.rotation.y = Math.PI / 8; g.add(ln);
    m(new THREE.BoxGeometry(0.16, 2.6, 0.16), lam(0xd9c36a), tx, th + 32.4, 0); m(new THREE.BoxGeometry(1.3, 0.16, 0.16), lam(0xd9c36a), tx, th + 32.8, 0);
    L.rec.h = 22; const tc = toMap(o, tx, 0); block(tc[0], tc[1], 5.5, 60);
    // Blender-built model with baked sunlight replaces the simple one once it has loaded
    const proc = _P.scene.children.slice(procStart);
    import('../kirkko.js').then(K => { const bin = atob(K.default), buf = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i); new GLTFLoader().parse(buf.buffer, '', gl => {
      gl.scene.traverse(q => { if (q.isMesh) { const map = q.material.map; if (map) { map.anisotropy = 8; _P.TEXLOD.add(map, _P.LMAT.kirkko[0], _P.LMAT.kirkko[1]); } q.material = _P.brickify(_P.glassify(new THREE.MeshBasicMaterial({ map }))); } });
      for (const q of proc) _P.scene.remove(q); frame(o).add(gl.scene);
    }, () => {}); }).catch(() => {});
  }
  // modern blocks: glazed ground floor, ribbon windows above
  function modern(L, { h, floors, wall, stripes = false, cap = 0x3a3f44, base = 4.6 }) {
    const pts = clean(L.pts);
    add(wallGeo(pts, 0, base, 6, 1), facade({ wall: '#27313b', trim: '#59666f', glass: '#41586a', arch: false, pil: false, course: false, win: [0.05, 0.12, 0.9, 0.8] }));
    add(wallGeo(pts, base, h - 0.5, 6.4, floors), facade({ wall, trim: '#6d7880', glass: '#2c3c4a', band: true, pil: false, course: false, rust: stripes }));
    const co = offset(pts, 0.3); add(wallGeo(co, h - 0.5, h + 0.3), lam(cap)); add(wallGeo(co, base - 0.25, base + 0.15), lam(cap));
    add(capGeo(pts, h + 0.03, true), _P.roofMat); L.rec.h = h + 0.3;
  }
  if (_P.LMB.promenadi) track('promenadi', () => modern(_P.LMB.promenadi, { h: 12.5, floors: 2, wall: '#41464c', stripes: true }));
  if (_P.LMB.bepop) track('bepop', () => modern(_P.LMB.bepop, { h: 17, floors: 3, wall: '#b4bcb8', cap: 0x4d5a57 }));
  if (_P.LMB.kirjasto) track('kirjasto', () => modern(_P.LMB.kirjasto, { h: 10.5, floors: 2, wall: '#bcb4a5', cap: 0x6b6258, base: 3.6 }));
  if (_P.LMB.museo) track('museo', () => modern(_P.LMB.museo, { h: 10, floors: 1, wall: '#a9a294', cap: 0x8c8a84, base: 3 }));
  if (_P.LMB.isokarhu) track('isokarhu', () => modern(_P.LMB.isokarhu, { h: 13, floors: 2, wall: '#4b4c52', stripes: true }));
  // Porin Puuvilla: the old cotton mill, red brick with arched windows
  { const millM = facade({ wall: '#9c4a38', trim: '#c9a58c', brick: true, arch: true, pil: false, course: false, win: [0.3, 0.2, 0.4, 0.58] }), bt = lam(0x7e3a2c);
    if (_P.LMB.tehdas) track('tehdas', () => styled(_P.LMB.tehdas, { h: 15, floors: 4, bay: 3.6, mat: millM, trim: bt }));
    if (_P.LMB.kehraamo) track('kehraamo', () => styled(_P.LMB.kehraamo, { h: 9.5, floors: 2, bay: 3.6, mat: millM, trim: bt })); }

  // ---------- bridges: railings, trusses and lamp posts on top of the aerial image ----------
  {
    const trussTex = (() => { const c = document.createElement('canvas'); c.width = 128; c.height = 128; const x = c.getContext('2d');
      x.strokeStyle = '#cfd6d8'; x.lineWidth = 9; x.strokeRect(0, 5, 128, 118); x.lineWidth = 6; x.beginPath(); x.moveTo(0, 123); x.lineTo(64, 5); x.lineTo(128, 123); x.moveTo(64, 5); x.lineTo(64, 123); x.stroke();
      const t = new THREE.CanvasTexture(c); t.wrapS = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t; })();
    const trussM = new THREE.MeshBasicMaterial({ map: trussTex, transparent: true, alphaTest: 0.35, side: THREE.DoubleSide });
    const concrete = new THREE.MeshLambertMaterial({ color: 0xc9c9c2, side: THREE.DoubleSide }), postM = lam(0x3a4045), lampM = new THREE.MeshBasicMaterial({ color: 0xfff3c4 });
    // vertical strip from a to b (map coords); hf(t) gives its height along the way
    function rail(a, b, hf, mat, rep) {
      const N = 40, p = [], u = [], len = Math.hypot(b[0] - a[0], b[1] - a[1]);
      for (let i = 0; i < N; i++) { const t0 = i / N, t1 = (i + 1) / N, x0 = a[0] + (b[0] - a[0]) * t0, y0 = a[1] + (b[1] - a[1]) * t0, x1 = a[0] + (b[0] - a[0]) * t1, y1 = a[1] + (b[1] - a[1]) * t1, h0 = hf(t0), h1 = hf(t1), u0 = t0 * len / rep, u1 = t1 * len / rep;
        const o0 = (_P.brDeckZ(x0, y0, 2) ?? _P.TZs(x0, y0)) - _P.TZs(x0, y0), o1 = (_P.brDeckZ(x1, y1, 2) ?? _P.TZs(x1, y1)) - _P.TZs(x1, y1);   /* kansi nostettu */
        p.push(x0, 0.2 + o0, -y0, x1, 0.2 + o1, -y1, x1, h1 + o1, -y1, x0, 0.2 + o0, -y0, x1, h1 + o1, -y1, x0, h0 + o0, -y0); u.push(u0, 0, u1, 0, u1, 1, u0, 0, u1, 1, u0, 1); }
      const g = new THREE.BufferGeometry(); g.setAttribute('position', fattr(p, 3)); g.setAttribute('uv', fattr(u, 2)); g.computeVertexNormals(); add(g, mat);
    }
    function lamps(a, b, off, step, h) {
      const len = Math.hypot(b[0] - a[0], b[1] - a[1]), dx = (b[0] - a[0]) / len, dy = (b[1] - a[1]) / len;
      for (let d = step / 2; d < len; d += step) for (const s of off) { const x = a[0] + dx * d + dy * s, y = a[1] + dy * d - dx * s;
        const oz = (_P.brDeckZ(x, y, 3) ?? _P.TZs(x, y)) - _P.TZs(x, y); const po = add(new THREE.CylinderGeometry(0.1, 0.14, h, 6), postM); po.position.set(x, h / 2 + oz, -y); const l = add(new THREE.SphereGeometry(0.38, 8, 6), lampM); l.position.set(x, h + 0.2 + oz, -y); }
    }
    const side = (a, b, s) => { const len = Math.hypot(b[0] - a[0], b[1] - a[1]), nx = (b[1] - a[1]) / len, ny = -(b[0] - a[0]) / len; return [[a[0] + nx * s, a[1] + ny * s], [b[0] + nx * s, b[1] + ny * s]]; };
    for (const br of CITY.br || []) {
      const P = br.p, a = [P[0], P[1]], b = [P[P.length - 2], P[P.length - 1]], len = Math.hypot(b[0] - a[0], b[1] - a[1]); if (len < 40) continue;
      if (_P.onPorinsilta((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 12)) continue;   // Porinsilta is a Blender model (below)
      if (false) {
      } else if (br.n === 'Taavi-silta') { for (const s of [-2.2, 2.2]) { const e = side(a, b, s); rail(e[0], e[1], () => 1.5, trussM, 1.5); } lamps(a, b, [2.4], 18, 4.5); }
      else if (!br.n) { for (const s of [-2, 2]) { const e = side(a, b, s); rail(e[0], e[1], () => 1.4, trussM, 1.4); } }
    }
    // Porinsilta (1926): Blender model with the truss, the raised bowstring span, portal arches, granite piers and lattice lamp masts
    _P.loadModel('bl_porinsilta', (root, K) => { const m = new THREE.MeshLambertMaterial({ vertexColors: true }); root.traverse(q => { if (q.isMesh) q.material = m; });
      /* 20.11.2026: mallin kansi (2,6 m maastonoston päällä, rampit päissä) taivutetaan absoluuttiseen kaareen psilDeck(t); pilarien alapäät veteen */
      const ux = Math.sin(_P.PSIL.head), uy = Math.cos(_P.PSIL.head); root.updateMatrixWorld(true);
      root.traverse(q => { if (!q.isMesh) return; const P = q.geometry.attributes.position, M = q.matrixWorld, iM = new THREE.Matrix4().copy(M).invert(), v = new THREE.Vector3();
        for (let i = 0; i < P.count; i++) { v.fromBufferAttribute(P, i).applyMatrix4(M); const mx = K.x + v.x, my = K.y - v.z, t = (mx - _P.PSIL.x) * ux + (my - _P.PSIL.y) * uy;
          v.y = v.y < -0.3 ? TER.wl - 1.0 : v.y - _P.psilOld(t) + _P.psilDeck(t); v.applyMatrix4(iM); P.setXYZ(i, v.x, v.y, v.z); }
        P.needsUpdate = true; q.geometry.computeBoundingSphere(); q.geometry.computeBoundingBox(); });
      const g = new THREE.Group(); g.position.set(K.x, 0, -K.y); g.add(root); _P.scene.add(_P.noT(g)); window.__porinsilta = true; });
    // decks over the lowered river (the bridges are in the aerial photo, so the deck keeps the photo), concrete edge beams and piers
    { const dp = [], du = [], fp = [], conc = lam(0x9a9890);
      for (const b of RIV.br) { const P = b.p;
        if (_P.onPorinsilta((P[0] + P[P.length - 2]) / 2, (P[1] + P[P.length - 1]) / 2, 12)) continue;
        const P0 = P; const Q = [];   /* owner 15.11.2026: the ground rose through the long deck pieces - cut the deck into <= 3 m pieces so it follows the terrain levels */
        for (let i = 0; i + 3 < P0.length; i += 2) { const L0 = Math.hypot(P0[i + 2] - P0[i], P0[i + 3] - P0[i + 1]), n = Math.max(1, Math.ceil(L0 / 3));
          for (let k = 0; k < n; k++) Q.push(P0[i] + (P0[i + 2] - P0[i]) * k / n, P0[i + 1] + (P0[i + 3] - P0[i + 1]) * k / n); }
        Q.push(P0[P0.length - 2], P0[P0.length - 1]);
        for (let i = 0; i + 3 < Q.length; i += 2) { const ax = Q[i], ay = Q[i + 1], bx = Q[i + 2], by = Q[i + 3], L = Math.hypot(bx - ax, by - ay); if (L < 0.05) continue;
          const nx = (by - ay) / L * b.w / 2, ny = -(bx - ax) / L * b.w / 2, q = [[ax + nx, ay + ny], [bx + nx, by + ny], [bx - nx, by - ny], [ax + nx, ay + ny], [bx - nx, by - ny], [ax - nx, ay - ny]];
          const off = (x, y) => (_P.brDeckZ(x, y, b.w) ?? _P.TZs(x, y)) - _P.TZs(x, y);   /* nostettu kansi suhteessa maastonostoon */
          for (const [x, y] of q) { dp.push(x, 0.05 + off(x, y), -y); du.push(_P.inCore(x, y) ? (x + _P.HW) / (2 * _P.HW) : 0, _P.inCore(x, y) ? (y - _P.YS) / _P.YSPAN : 0); }
          for (const sg of [1, -1]) { const e = [[ax + nx * sg, ay + ny * sg], [bx + nx * sg, by + ny * sg]];
            const oa = off(e[0][0], e[0][1]), ob = off(e[1][0], e[1][1]);
            fp.push(e[0][0], 0.05 + oa, -e[0][1], e[1][0], 0.05 + ob, -e[1][1], e[1][0], -0.95 + ob, -e[1][1], e[0][0], 0.05 + oa, -e[0][1], e[1][0], -0.95 + ob, -e[1][1], e[0][0], -0.95 + oa, -e[0][1]); }
          if (i % 16 === 0) for (let d = 1.5; d < L; d += 24) { const x = ax + (bx - ax) * d / L, y = ay + (by - ay) * d / L; if (!_P.inRiver(x, y)) continue;
            const wr = _P.WREL(x, y), oz = off(x, y), pr = add(new THREE.BoxGeometry(1.2, oz - wr - 0.9, b.w * 0.8), conc); pr.position.set(x, (wr + oz - 0.95) / 2, -y); pr.rotation.y = Math.atan2(by - ay, bx - ax); } } }
      const dg = new THREE.BufferGeometry(); dg.setAttribute('position', new THREE.Float32BufferAttribute(dp, 3)); dg.setAttribute('uv', new THREE.Float32BufferAttribute(du, 2));
      add(dg, new THREE.MeshBasicMaterial({ map: _P.orto, side: THREE.DoubleSide }));
      const fg = new THREE.BufferGeometry(); fg.setAttribute('position', new THREE.Float32BufferAttribute(fp, 3)); fg.computeVertexNormals(); add(fg, new THREE.MeshLambertMaterial({ color: 0x8f8d86, side: THREE.DoubleSide })); }
    { const a = [396, 442], b = [396, 652];                              // Linnansilta (1974): concrete girder bridge
      for (const s of [-11, 11]) { const e = side(a, b, s); rail(e[0], e[1], () => 1.3, concrete, 1); } lamps(a, b, [0], 30, 11); }
  }
  // Kauppatori: the 2022 market pavilion (two glazed pavilions under one long curved-edge roof, passage through the middle)
  if (_P.LMB.tori) track('tori', () => {
    const L = _P.LMB.tori; let o = obb(L.pts);
    if (o.a < o.b) { let ux = -o.uy, uy = o.ux; if (ux < 0) { ux = -ux; uy = -uy; } o = { ...o, ux, uy, a: o.b, b: o.a }; }
    const g = frame(o), a = o.a, b = o.b, H = 4.4, gap = 3.6;
    const m = (geo, mat, x, y, z) => { const q = new THREE.Mesh(geo, mat); q.position.set(x, y, z); g.add(q); return q; };
    const rr = (w, d, r) => { const sh = new THREE.Shape(), x = -w / 2, y = -d / 2; sh.moveTo(x + r, y); sh.lineTo(x + w - r, y); sh.quadraticCurveTo(x + w, y, x + w, y + r); sh.lineTo(x + w, y + d - r); sh.quadraticCurveTo(x + w, y + d, x + w - r, y + d); sh.lineTo(x + r, y + d); sh.quadraticCurveTo(x, y + d, x, y + d - r); sh.lineTo(x, y + r); sh.quadraticCurveTo(x, y, x + r, y); return sh; };
    const slab = (w, d, r, t, y, c) => { const ge = new THREE.ExtrudeGeometry(rr(w, d, r), { depth: t, bevelEnabled: false, curveSegments: 8 }); ge.rotateX(-Math.PI / 2); return m(ge, lam(c), 0, y, 0); };
    slab(2 * a + 7, 2 * b + 8, 6, 0.5, H + 0.25, 0x4b3b30); slab(2 * a + 6, 2 * b + 7, 5.5, 0.12, H + 0.14, 0xc9a06b);
    const glassM = facade({ wall: '#2a3540', trim: '#1e2429', glass: '#3d566a', arch: false, pil: false, course: false, win: [0.05, 0.05, 0.9, 0.9] }), copper = lam(0x7d4b33);
    const box = (len, w, x, mat, rep) => { const q = m(new THREE.BoxGeometry(len, H, w), mat, x, H / 2 + 0.1, 0); if (rep) { const uv = q.geometry.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setX(i, uv.getX(i) * rep); } };
    const full = a - 1.5 - gap, gl = full * 0.45, cu = full - gl, w = 2 * b - 3.5;
    for (const sgn of [-1, 1]) { box(gl, w, sgn * (gap + gl / 2), glassM, Math.round(gl / 2.4)); box(cu, w - 0.6, sgn * (gap + gl + cu / 2), copper); }
    L.rec.h = H + 0.8;
  });
  // Kohtaamislava Satakieli: open stage canopy on the east side of the square
  if (_P.LMB.lava) { const L = _P.LMB.lava, pts = clean(L.pts);
    add(hipGeo(offset(pts, 1.2), offset(pts, -2.5), 4.4, 5.3), lam(0xe9e6de, DS)); add(wallGeo(pts, 0, 0.9), lam(0x4a4f55));
    for (const q of pts) { const po = add(new THREE.CylinderGeometry(0.16, 0.16, 4.4, 8), lam(0x3a4045)); po.position.set(q[0], 2.2, -q[1]); } L.rec.h = 5.3; }
  // Lokki-lava, Kirjurinluoto: white tent-roofed bandstand
  if (_P.LMB.lokki) { const L = _P.LMB.lokki, pts = clean(L.pts);
    add(hipGeo(offset(pts, 0.8), offset(pts, -8.5), 5, 11), lam(0xf4f2ec, DS)); add(wallGeo(pts, 0, 1.2), lam(0x55595c));
    for (const q of pts) { const po = add(new THREE.CylinderGeometry(0.22, 0.22, 5, 8), lam(0xdedbd2)); po.position.set(q[0], 2.5, -q[1]); } L.rec.h = 11; }
  // Puuvillan savupiippu (54 m)
  { const ch = add(new THREE.CylinderGeometry(1.5, 2.7, 54, 14), _P.brickify(lam(0x9a4f3a))); ch.position.set(165.3, 27, -792.6); block(165.3, 792.6, 3, 54); }
  // Aittaluodon voimalaitos (Pori Energia): the 126 m chimney of 1937 is the tallest point of Pori's skyline, with the
  // 70 m steel stack of the auxiliary boiler beside it (heights: Porin korkean rakentamisen selvitys 2019, ympäristölupa 2020)
  { const stack = (x, y, h, rb, rt, col, cap, capC) => {
      const ch = add(new THREE.CylinderGeometry(rt, rb, h, 20), _P.brickify(lam(col))); ch.position.set(x, h / 2, -y);
      const c2 = add(new THREE.CylinderGeometry(rt * 1.08, rt * 1.08, cap, 20), lam(capC)); c2.position.set(x, h - cap / 2, -y);
      const ring = add(new THREE.CylinderGeometry(rt * 1.35, rt * 1.35, 0.35, 20), lam(0x3a3b3c)); ring.position.set(x, h - cap - 1.2, -y);
      block(x, y, rb + 0.5, h); };
    stack(1177, 322, 126, 5.2, 2.6, 0x6e4636, 4, 0x2f2f30);
    stack(1203, 300, 70, 1.6, 1.4, 0x5a4136, 5, 0xb8bcbf); }
}
}
