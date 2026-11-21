// Porin rataverkko: raiteet koko pelikartalle, aseman laiturit, alikulun portaali, ajojohdin – ILMAN muutoksia index.html:n rakenteisiin
// (index.html:ssä vain: rata_data.js:n maastokorjaukset ennen maan rakentamista ja tämän moduulin <script>-rivi).
//
// Aineisto: OpenStreetMap (raiteet, vaihteet, opastimet, laiturit; haettu 20.11.2026), korkeus MML 2 m (terrain.js). Ks. rata/README.md.
// Rakenne raiteelta alhaalta ylös:
//   sepeli (raidesepeli 31,5/63 graniittia, saumaton tekstuuri + normaalikartta; luiska 1:1,5, kiskojen välissä ruosteisempi)
//   betonipölkky B97 (2,6 m, jako 0,61 m), lähellä kiinnitykset: välilevy, valetut olakkeet ja Pandrolin e-jousileikkeet
//   kisko 60E1 (pääraiteet) / 54E1 (sivuraiteet) – kiiltävä kulkupinta, ruosteinen varsi ja jalka
//   vaihteissa pitkät vaihdepölkyt, kääntölaite ja kielet; käytöstä poistetuilla raiteilla puupölkyt ja ruoho
// Etäisyystasot: alle 70 m kiinnitykset, alle 650 m pölkyt, kiskot tarkka/kevyt, sepeli aina.
import * as THREE from '../three.module.min.js';
import RATA from './rata_data.js';
import CITY from '../city.js';
import { yhdista } from '../juna/yhdista.js';

const TAU = Math.PI * 2;
const RAIL = RATA.rail, CREST = RATA.crest;
const GAUGE_HALF = 0.7985;            // kiskon keskilinja raiteen keskeltä (1524 mm raideleveys kulkureunojen välillä + puoli kiskon kantaa)
const TILE = 200;                     // ruudut (m), joihin geometria kootaan
const NEAR = 70, MID = 650, RAILHI = 260;
const PLAT_H = 0.55;                  // laiturin korkeus kiskon yläpinnasta (550 mm)
const PLAT_EDGE = 1.80;               // laiturin reuna raiteen keskeltä

const tracks = RATA.t.map((t, i) => {
  const n = t.p.length / 3, P = new Float32Array(n * 2), Z = new Float32Array(n), S = new Float32Array(n);
  for (let k = 0; k < n; k++) { P[k * 2] = t.p[k * 3]; P[k * 2 + 1] = t.p[k * 3 + 1]; Z[k] = t.p[k * 3 + 2]; if (k) S[k] = S[k - 1] + Math.hypot(P[k * 2] - P[k * 2 - 2], P[k * 2 + 1] - P[k * 2 - 1]); }
  const B = new Uint8Array(n), LC = new Uint8Array(n), TN = new Uint8Array(n); for (const j of t.b) B[j] = 1; for (const j of t.lc) LC[j] = 1; for (const j of t.tn || []) TN[j] = 1;
  return { i, k: t.k, e: t.e, v: t.v, n, P, Z, S, B, LC, TN, L: S[n - 1], wood: t.k === 'x' || t.k === 'p', main: t.k === 'm' || t.k === 'b' };
});
// piste ja suunta kaaren pituudella s
function at(tr, s) {
  s = Math.max(0, Math.min(tr.L, s)); let lo = 0, hi = tr.n - 1;
  while (hi - lo > 1) { const m = (lo + hi) >> 1; if (tr.S[m] <= s) lo = m; else hi = m; }
  const f = (s - tr.S[lo]) / Math.max(1e-6, tr.S[hi] - tr.S[lo]), P = tr.P;
  const x = P[lo * 2] + (P[hi * 2] - P[lo * 2]) * f, y = P[lo * 2 + 1] + (P[hi * 2 + 1] - P[lo * 2 + 1]) * f, z = tr.Z[lo] + (tr.Z[hi] - tr.Z[lo]) * f;
  // suunta tasoitettuna kolmen pisteen yli (ei nykäyksiä 2 m:n välein)
  const a = Math.max(0, lo - 1), b = Math.min(tr.n - 1, hi + 1); let dx = P[b * 2] - P[a * 2], dy = P[b * 2 + 1] - P[a * 2 + 1]; const l = Math.hypot(dx, dy) || 1; dx /= l; dy /= l;
  return { x, y, z, dx, dy, i: lo, f, br: tr.B[lo] || tr.B[hi], tn: tr.TN[lo] || tr.TN[hi], lc: tr.LC[lo] || tr.LC[hi] };
}
function nearestOn(tr, x, y) { let best = 1e18, bi = 0; for (let k = 0; k < tr.n; k++) { const d = (tr.P[k * 2] - x) ** 2 + (tr.P[k * 2 + 1] - y) ** 2; if (d < best) { best = d; bi = k; } }
  // tarkennus janalle
  let bs = tr.S[bi], bd = Math.sqrt(best);
  for (const k of [bi - 1, bi]) { if (k < 0 || k + 1 >= tr.n) continue; const ax = tr.P[k * 2], ay = tr.P[k * 2 + 1], ex = tr.P[k * 2 + 2] - ax, ey = tr.P[k * 2 + 3] - ay, L2 = ex * ex + ey * ey || 1, u = Math.max(0, Math.min(1, ((x - ax) * ex + (y - ay) * ey) / L2)), d = Math.hypot(ax + ex * u - x, ay + ey * u - y);
    if (d < bd) { bd = d; bs = tr.S[k] + u * Math.sqrt(L2); } }
  return { s: bs, d: bd }; }

// ---------------------------------------------------------------- tekstuurit
const texL = new THREE.TextureLoader();
const T = n => { const t = texL.load(new URL(n, import.meta.url).href); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; return t; };
const sepA = T('sepeli_a.jpg'), sepN = T('sepeli_n.jpg'), sepO = T('sepeli_orm.jpg'); sepA.colorSpace = THREE.SRGBColorSpace;
function canvasTex(w, h, draw, srgb = true) { const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h); const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; if (srgb) t.colorSpace = THREE.SRGBColorSpace; return t; }
const rnd = (() => { let s = 12345; return () => (s = (s * 1664525 + 1013904223) >>> 0) / 4294967296; })();
// betoni: hienoa raetta ja tummia pisteitä
const concTex = canvasTex(256, 256, (g, w, h) => { g.fillStyle = '#b9b8b2'; g.fillRect(0, 0, w, h); const im = g.getImageData(0, 0, w, h);
  for (let i = 0; i < w * h; i++) { const v = (rnd() - 0.5) * 26 + (rnd() < 0.02 ? -40 : 0); im.data[i * 4] += v; im.data[i * 4 + 1] += v; im.data[i * 4 + 2] += v * 0.9; } g.putImageData(im, 0, 0); });
// laiturin pinta: harmaat betonilaatat (0,5 m)
const platTex = canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#9d9d98'; g.fillRect(0, 0, w, h); const im = g.getImageData(0, 0, w, h);
  for (let i = 0; i < w * h; i++) { const v = (rnd() - 0.5) * 18; im.data[i * 4] += v; im.data[i * 4 + 1] += v; im.data[i * 4 + 2] += v; } g.putImageData(im, 0, 0);
  for (let a = 0; a < 4; a++) for (let b = 0; b < 4; b++) { g.fillStyle = `rgba(${120 + rnd() * 30 | 0},${120 + rnd() * 30 | 0},${118 + rnd() * 30 | 0},0.25)`; g.fillRect(a * 128 + 2, b * 128 + 2, 124, 124); }
  g.strokeStyle = 'rgba(60,60,58,0.55)'; g.lineWidth = 2; for (let k = 0; k <= 4; k++) { g.beginPath(); g.moveTo(k * 128, 0); g.lineTo(k * 128, h); g.stroke(); g.beginPath(); g.moveTo(0, k * 128); g.lineTo(w, k * 128); g.stroke(); } });
// kohokuvioitu varoituslaatta
const tactTex = canvasTex(128, 128, (g, w, h) => { g.fillStyle = '#c9c7bd'; g.fillRect(0, 0, w, h); g.fillStyle = '#a9a79c'; for (let k = 0; k < 8; k++) g.fillRect(k * 16 + 4, 0, 7, h); });
// tasoristeyksen kumilevyt
const rubberTex = canvasTex(128, 128, (g, w, h) => { g.fillStyle = '#26282a'; g.fillRect(0, 0, w, h); g.fillStyle = '#1b1c1e'; for (let k = 0; k < 16; k++) g.fillRect(0, k * 8, w, 3); });

// ---------------------------------------------------------------- materiaalit
const M = {};
M.ballast = new THREE.MeshStandardMaterial({ map: sepA, normalMap: sepN, aoMap: sepO, aoMapIntensity: 0.6, color: 0x9a9a9a, roughness: 0.95, metalness: 0, vertexColors: true, normalScale: new THREE.Vector2(1.6, 1.6) });   // pelin valot ovat kirkkaat (puolipallovalo 2,65): pohjaväri tummennetaan
M.conc = new THREE.MeshStandardMaterial({ map: concTex, color: 0x868d94, roughness: 0.9, metalness: 0, vertexColors: true });
M.wood = new THREE.MeshStandardMaterial({ color: 0x4a3a2c, roughness: 0.95, vertexColors: true });
M.rail = new THREE.MeshStandardMaterial({ vertexColors: true, color: 0x8a8a8a, roughness: 0.4, metalness: 0.3 });
M.steel = new THREE.MeshStandardMaterial({ color: 0x3d3f41, roughness: 0.55, metalness: 0.4 });
M.clip = new THREE.MeshStandardMaterial({ color: 0x2b2d2f, roughness: 0.6, metalness: 0.3 });
M.pad = new THREE.MeshStandardMaterial({ color: 0x141516, roughness: 0.9 });
M.castIron = new THREE.MeshStandardMaterial({ color: 0x55504a, roughness: 0.85, metalness: 0.2 });
M.yellow = new THREE.MeshStandardMaterial({ color: 0xd8b21c, roughness: 0.6 });
M.plat = new THREE.MeshStandardMaterial({ map: platTex, color: 0x9a9a9a, roughness: 0.9 });
M.platSide = new THREE.MeshStandardMaterial({ map: concTex, color: 0x9c9b96, roughness: 0.9 });
M.tact = new THREE.MeshStandardMaterial({ map: tactTex, color: 0xa0a0a0, roughness: 0.85 });
M.white = new THREE.MeshStandardMaterial({ color: 0xbdbdba, roughness: 0.7 });
M.rubber = new THREE.MeshStandardMaterial({ map: rubberTex, roughness: 0.95 });
M.bridge = new THREE.MeshStandardMaterial({ map: concTex, color: 0x8e8d88, roughness: 0.9 });
M.glass = new THREE.MeshStandardMaterial({ color: 0x9fb8c4, roughness: 0.08, metalness: 0.1, transparent: true, opacity: 0.38, depthWrite: false, side: THREE.DoubleSide });
M.frame = new THREE.MeshStandardMaterial({ color: 0x2f3438, roughness: 0.5, metalness: 0.5 });
M.dark = new THREE.MeshBasicMaterial({ color: 0x0b0c0d });
M.mast = new THREE.MeshStandardMaterial({ color: 0x6c7176, roughness: 0.55, metalness: 0.45 });
M.insul = new THREE.MeshStandardMaterial({ color: 0x6d4a35, roughness: 0.4 });
M.wire = new THREE.LineBasicMaterial({ color: 0x2a2826, transparent: true, opacity: 0.85 });
M.sigBlack = new THREE.MeshStandardMaterial({ color: 0x151617, roughness: 0.7 });
M.sigRed = new THREE.MeshBasicMaterial({ color: 0xff2a1a });
M.sigGreen = new THREE.MeshBasicMaterial({ color: 0x3dff6a });
M.sigWhite = new THREE.MeshBasicMaterial({ color: 0xfff6e0 });
M.grass = new THREE.MeshStandardMaterial({ color: 0x5f6b3a, roughness: 1, vertexColors: true });
for (const m of Object.values(M)) m.userData.noT = true;

// ---------------------------------------------------------------- perusgeometriat
// kisko 60E1 (mm, puoli profiilista alhaalta ylös); 54E1 skaalataan
const RP = [[0, 0], [75, 0], [75, 11], [45, 19], [11, 32], [8.25, 42], [8.25, 116], [13, 125], [36, 131], [36, 158], [34, 166], [24, 171.5], [0, 172]];
const RAILPROF = (() => { const R = RP.map(([x, y]) => [x / 1000, y / 1000]); const L = R.slice(1, -1).reverse().map(([x, y]) => [-x, y]); return [...R, ...L]; })();   // suljettu kehä
const RAILPROF_LO = [[0.075, 0], [0.036, 0.172], [-0.036, 0.172], [-0.075, 0]];
const HEAD = y => y > 0.165;   // kulkupinta
// B97-betonipölkky: loft pituuden yli (u = -1,3 ... 1,3)
function sleeperB97() {
  const st = [[-1.3, 0.150, 0.105, 0.200], [-1.08, 0.150, 0.110, 0.220], [-0.55, 0.150, 0.110, 0.220], [-0.36, 0.128, 0.095, 0.185], [0.36, 0.128, 0.095, 0.185], [0.55, 0.150, 0.110, 0.220], [1.08, 0.150, 0.110, 0.220], [1.3, 0.150, 0.105, 0.200]];
  const pos = [], col = [], idx = [], uv = [];
  // jokaisella asemalla 4 kulmaa: alhaalla vasen/oikea, ylhäällä oikea/vasen (y = 0 on pölkyn yläpinta raidepaikalla)
  const ring = (u, wb, wt, h) => [[u, -h, -wb], [u, -h, wb], [u, 0 - (0.22 - h) * 0.5, wt], [u, 0 - (0.22 - h) * 0.5, -wt]];
  const R = st.map(s => ring(...s));
  const push = (p, c) => { pos.push(...p); col.push(c, c, c * 0.98); uv.push(p[0] * 0.8, p[1] * 2 + p[2] * 2); return pos.length / 3 - 1; };
  for (let a = 0; a + 1 < R.length; a++) for (let f = 0; f < 4; f++) {
    const A = R[a][f], B = R[a][(f + 1) % 4], C = R[a + 1][(f + 1) % 4], D = R[a + 1][f];
    const sh = f === 2 ? 1.0 : f === 0 ? 0.55 : 0.8;   // yläpinta vaaleampi, kyljet ja pohja likaisemmat
    const i0 = push(A, sh), i1 = push(B, sh), i2 = push(C, sh), i3 = push(D, sh); idx.push(i0, i2, i1, i0, i3, i2); }
  for (const [r, s] of [[R[0], 1], [R[R.length - 1], -1]]) { const i = r.map(p => push(p, 0.8)); if (s > 0) idx.push(i[0], i[1], i[2], i[0], i[2], i[3]); else idx.push(i[0], i[2], i[1], i[0], i[3], i[2]); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); g.setIndex(idx); g.computeVertexNormals(); return g;
}
function boxG(w, h, d, x = 0, y = 0, z = 0, c = 1) { const g = new THREE.BoxGeometry(w, h, d); g.translate(x, y, z); const n = g.attributes.position.count; g.setAttribute('color', new THREE.Float32BufferAttribute(new Array(n * 3).fill(c), 3)); return g; }
function merge(list) {   // pieni mergeGeometries (sama attribuuttijoukko)
  const keys = ['position', 'normal', 'color', 'uv'].filter(k => list.every(g => g.attributes[k])); const out = new THREE.BufferGeometry(); const idx = []; let off = 0;
  for (const k of keys) { const arr = []; for (const g of list) arr.push(...g.attributes[k].array); out.setAttribute(k, new THREE.Float32BufferAttribute(arr, list[0].attributes[k].itemSize)); }
  for (const g of list) { const n = g.attributes.position.count; if (g.index) for (const i of g.index.array) idx.push(i + off); else for (let i = 0; i < n; i++) idx.push(i + off); off += n; }
  out.setIndex(idx); if (!out.attributes.normal) out.computeVertexNormals(); return out; }
const G_SLEEPER = sleeperB97();
const G_SLEEPER_LO = boxG(2.6, 0.2, 0.26, 0, -0.1, 0, 0.8);
const G_WOOD = (() => { const g = boxG(2.6, 0.16, 0.23, 0, -0.08, 0, 1); return g; })();
// kiinnitykset yhdelle pölkylle (molemmat kiskot): välilevy, olakkeet, e-leikkeet
const G_FAST = (() => { const parts = [], clips = [], pads = [];
  for (const sx of [-1, 1]) { const cx = sx * GAUGE_HALF;
    pads.push(boxG(0.165, 0.012, 0.19, cx, 0.006, 0));
    for (const sd of [-1, 1]) { parts.push(boxG(0.05, 0.075, 0.13, cx + sd * 0.103, 0.025, 0, 1));
      const cv = new THREE.CatmullRomCurve3([[0.103, 0.06, -0.045], [0.125, 0.075, -0.01], [0.112, 0.07, 0.035], [0.085, 0.045, 0.045], [0.07, 0.03, 0.01], [0.082, 0.026, -0.03]].map(([a, b, c]) => new THREE.Vector3(cx + sd * a, b - 0.01, c)));
      const tg = new THREE.TubeGeometry(cv, 8, 0.0095, 4, false); tg.deleteAttribute('uv'); const n = tg.attributes.position.count; tg.setAttribute('color', new THREE.Float32BufferAttribute(new Array(n * 3).fill(1), 3)); clips.push(tg); } }
  return { iron: merge(parts.map(g => { g.deleteAttribute('uv'); return g; })), clip: merge(clips), pad: merge(pads.map(g => { g.deleteAttribute('uv'); return g; })) }; })();
// puupölkyn aluslevyt ja naulat
const G_TIEPLATE = merge([-1, 1].flatMap(sx => [boxG(0.34, 0.015, 0.19, sx * GAUGE_HALF, 0.0075, 0), boxG(0.02, 0.02, 0.02, sx * GAUGE_HALF + 0.11, 0.025, 0.05), boxG(0.02, 0.02, 0.02, sx * GAUGE_HALF - 0.11, 0.025, -0.05)]).map(g => { g.deleteAttribute('uv'); return g; }));

// ---------------------------------------------------------------- ruudut
const tiles = new Map();
const tkey = (x, y) => Math.floor(x / TILE) + ',' + Math.floor(y / TILE);
function tile(x, y) { const k = tkey(x, y); let t = tiles.get(k); if (!t) { t = { k, cx: (Math.floor(x / TILE) + 0.5) * TILE, cy: (Math.floor(y / TILE) + 0.5) * TILE,
  bal: { p: [], c: [], u: [], i: [] }, rail: { p: [], c: [], i: [] }, railLo: { p: [], c: [], i: [] }, sl: [], slw: [], fast: [], tp: [], misc: [], g: null }; tiles.set(k, t); } return t; }
const W = (x, y, z) => [x, z, -y];   // kartta -> three.js

// sepelipenkan poikkileikkaus: [sivuetäisyys, korkeus pölkyn yläpinnasta, värikerroin]
function ballastProfile(tr, br, ext) {
  const c = tr.main ? 1.75 : 1.55, dep = tr.main ? 0.55 : 0.38, s = dep * 1.5;
  if (ext && !br) {   // naapuriraide lähellä: sepeli jatkuu tasaisena puoliväliin asti (ratapiha)
    const cl = Math.max(c, ext[0]), cr = Math.max(c, ext[1]), sl = ext[0] > c ? 0.35 : s, sr = ext[1] > c ? 0.35 : s, dl = ext[0] > c ? 0.25 : dep, dr = ext[1] > c ? 0.25 : dep;
    return [[-cl - sl - 0.05, -dl - 0.9, 0.8], [-cl - sl, -dl, 0.85], [-cl, -0.05, 0.92], [-1.05, -0.02, 1.0], [-0.55, -0.05, 0.72], [0.55, -0.05, 0.72], [1.05, -0.02, 1.0], [cr, -0.05, 0.92], [cr + sr, -dr, 0.85], [cr + sr + 0.05, -dr - 0.9, 0.8]]; }
  if (br) return [[-2.05, -0.7, 0.75], [-2.05, -0.06, 0.9], [-0.95, -0.03, 0.95], [-0.55, -0.05, 0.72], [0.55, -0.05, 0.72], [0.95, -0.03, 0.95], [2.05, -0.06, 0.9], [2.05, -0.7, 0.75]];
  return [[-c - s - 0.05, -dep - 0.9, 0.8], [-c - s, -dep, 0.85], [-c, -0.04, 0.95], [-1.05, -0.02, 1.0], [-0.55, -0.05, 0.72], [0.55, -0.05, 0.72], [1.05, -0.02, 1.0], [c, -0.04, 0.95], [c + s, -dep, 0.85], [c + s + 0.05, -dep - 0.9, 0.8]];
}

function buildTrack(tr) {
  const wood = tr.wood, rust = tr.k === 'x';
  // ---- sepeli: renkaat 2 m välein (kaarteessa tihein), katkaistaan tasoristeyksissä
  let prev = null;
  const step = 2;
  for (let s = 0; s <= tr.L + 1e-3; s += step) {
    const s1 = Math.min(s, tr.L), a = at(tr, s1), t = tile(a.x, a.y), B = t.bal;
    if (a.lc) { prev = null; continue; }
    const nx = a.dy, ny = -a.dx, ext = [0, 0];
    for (const [k, sd] of [[0, -1], [1, 1]]) { let best = 1e9; for (const o of [2.5, 3.5, 4.5, 5.5, 7, 8.5, 10]) { const h = NEARIDX(a.x + nx * sd * o, a.y + ny * sd * o, 1.6, tr); if (h) { const lat = Math.abs((h.a.x - a.x) * nx + (h.a.y - a.y) * ny); if (lat > 2.2 && lat < best) best = lat; } }
      if (best < 12) ext[k] = best / 2 + 0.2;
      else for (const pl of PLPOLY) if (inPoly(a.x + nx * sd * 2.6, a.y + ny * sd * 2.6, pl)) ext[k] = 2.3; }   // laiturin alle asti
    const prof = ballastProfile(tr, a.br || a.tn, ext);
    const base = B.p.length / 3;
    for (const [o, h, c] of prof) { B.p.push(...W(a.x + nx * o, a.y + ny * o, a.z + h)); const cc = rust ? c * 0.85 : c; B.c.push(cc * (rust ? 1.02 : 1), cc * (rust ? 0.95 : 1), cc * (rust ? 0.85 : 1)); B.u.push(o / 1.6, s1 / 1.6); }
    if (prev && prev.t === t && prev.n === prof.length) for (let k = 0; k + 1 < prof.length; k++) { const a0 = prev.base + k, a1 = prev.base + k + 1, b0 = base + k, b1 = base + k + 1; B.i.push(a0, a1, b0, a1, b1, b0); }
    else if (prev && prev.n === prof.length) {   // ruudun raja: toista edellinen rengas tähän ruutuun
      const pb = B.p.length / 3; for (let k = 0; k < prof.length; k++) { B.p.push(...prev.pts[k]); B.c.push(...prev.cols[k]); B.u.push(...prev.uvs[k]); }
      for (let k = 0; k + 1 < prof.length; k++) { const a0 = pb + k, a1 = pb + k + 1, b0 = base + k, b1 = base + k + 1; B.i.push(a0, a1, b0, a1, b1, b0); } }
    prev = { t, base, n: prof.length, pts: prof.map((_, k) => B.p.slice((base + k) * 3, (base + k) * 3 + 3)), cols: prof.map((_, k) => B.c.slice((base + k) * 3, (base + k) * 3 + 3)), uvs: prof.map((_, k) => B.u.slice((base + k) * 2, (base + k) * 2 + 2)) };
    if (s1 >= tr.L) break;
  }
  // ---- kiskot (kaksi), tarkka ja kevyt profiili
  for (const side of [-1, 1]) for (const [prof, key, st] of [[RAILPROF, 'rail', 1.0], [RAILPROF_LO, 'railLo', 4.0]]) {
    let pr = null;
    const sc = tr.main ? 1 : 0.93;
    for (let s = 0; s <= tr.L + 1e-3; s += st) {
      const s1 = Math.min(s, tr.L), a = at(tr, s1), t = tile(a.x, a.y), R = t[key], nx = a.dy, ny = -a.dx, cx = a.x + nx * side * GAUGE_HALF, cy = a.y + ny * side * GAUGE_HALF, z0 = a.z + 0.012;
      const base = R.p.length / 3;
      const ring = prof.map(([px, py]) => { const p = W(cx + nx * px * sc, cy + ny * px * sc, z0 + py * sc); const c = HEAD(py) ? (rust ? [0.42, 0.3, 0.22] : [0.86, 0.86, 0.87]) : py > 0.12 ? [0.36, 0.28, 0.22] : [0.33, 0.2, 0.12]; return [p, c]; });
      for (const [p, c] of ring) { R.p.push(...p); R.c.push(...c); }
      const N = prof.length, closed = key === 'rail';
      const link = (pb) => { for (let k = 0; k < N - (closed ? 0 : 1); k++) { const k1 = (k + 1) % N; R.i.push(pb + k, base + k, pb + k1, pb + k1, base + k, base + k1); } };
      if (pr && pr.t === t) link(pr.base);
      else if (pr) { const pb = R.p.length / 3; for (const [p, c] of pr.ring) { R.p.push(...p); R.c.push(...c); } link(pb); }
      pr = { t, base, ring };
      if (s1 >= tr.L) break;
    }
  }
  // ---- pölkyt (vaihteiden kohdalla ohitetaan, ks. turnouts())
  const sp = wood ? 0.65 : 0.61;
  for (let s = 0.3; s < tr.L; s += sp) {
    if (tr.skip && tr.skip.some(([a, b]) => s >= a && s <= b)) continue;
    const a = at(tr, s); if (a.lc) continue; const t = tile(a.x, a.y);
    const yaw = Math.atan2(a.dx, a.dy), jit = wood ? (rnd() - 0.5) * 0.05 : (rnd() - 0.5) * 0.008;
    (wood ? t.slw : t.sl).push([a.x, a.y, a.z + (wood ? 0.005 : 0.02), yaw + jit, 1, 0, 0.85 + rnd() * 0.2]);
  }
}

// vaihteet: poikkeavan raiteen alku pölkyttä, läpimenevän raiteen pölkyt pitkiksi vaihdepölkyiksi; kääntölaite
const TO_LEN = 26;
let NEARIDX = null;
const PLPOLY = RATA.pl.map(pl => { const P = []; for (let k = 0; k + 1 < pl.p.length; k += 2) P.push([pl.p[k], pl.p[k + 1]]); return P; });
function turnouts() {
  for (const to of RATA.to) {
    const d = tracks[to.d], th = tracks[to.th]; if (!d || !th) continue;
    const sd = to.e === 0 ? 0 : d.L, dir = to.e === 0 ? 1 : -1;
    (d.skip || (d.skip = [])).push(to.e === 0 ? [0, TO_LEN] : [d.L - TO_LEN, d.L]);
    const n0 = nearestOn(th, to.at[0], to.at[1]); const a0 = at(th, n0.s);
    // läpimenevän raiteen suunta vaihteen kärjestä poikkeavan raiteen puolelle
    const p1 = at(d, sd + dir * 10), fw = Math.sign((p1.x - a0.x) * a0.dx + (p1.y - a0.y) * a0.dy) || 1;
    (th.skip || (th.skip = [])).push(fw > 0 ? [n0.s - 0.2, n0.s + TO_LEN] : [n0.s - TO_LEN, n0.s + 0.2]);
    for (let u = 0.3; u < TO_LEN; u += 0.6) {
      const a = at(th, n0.s + fw * u), q = at(d, sd + dir * u), nx = a.dy, ny = -a.dx, off = (q.x - a.x) * nx + (q.y - a.y) * ny;
      const len = 2.6 + Math.abs(off), mid = off / 2, t = tile(a.x, a.y);
      (th.wood ? t.slw : t.sl).push([a.x + nx * mid, a.y + ny * mid, a.z + 0.02, Math.atan2(a.dx, a.dy), len / 2.6, 0, 0.9]);
    }
    // kääntölaite (keltainen kotelo ja vetotanko) kärjen kohdalla raiteen ulkopuolella
    const nx = a0.dy, ny = -a0.dx, sideS = Math.sign((p1.x - a0.x) * nx + (p1.y - a0.y) * ny) || 1, t = tile(a0.x, a0.y);
    const ax = a0.x + a0.dx * fw * 1.2 - nx * sideS * 1.65, ay = a0.y + a0.dy * fw * 1.2 - ny * sideS * 1.65;
    t.misc.push({ g: 'machine', x: ax, y: ay, z: a0.z, yaw: Math.atan2(a0.dx, a0.dy) });
  }
}

// ---------------------------------------------------------------- muut rakenteet
const G_MACHINE = (() => { const a = boxG(0.42, 0.32, 1.1, 0, 0.0, 0); const b = boxG(1.5, 0.04, 0.06, 0.95, -0.08, 0.3); a.deleteAttribute('uv'); b.deleteAttribute('uv'); return { box: a, rod: b }; })();
function addMisc(t, grp) {
  for (const m of t.misc) {
    if (m.g === 'machine') { const o = new THREE.Group(); o.position.set(...W(m.x, m.y, m.z)); o.rotation.y = m.yaw + Math.PI / 2;
      const b = new THREE.Mesh(G_MACHINE.box, M.yellow); b.position.y = 0.0; o.add(b); const r = new THREE.Mesh(G_MACHINE.rod, M.steel); o.add(r); grp.add(o); }
  }
}

function finishTile(t, root) {
  const grp = new THREE.Group(); grp.userData = { t }; t.g = grp;
  const mk = (D, mat, uv) => { if (!D.i.length) return null; const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(D.p, 3)); g.setAttribute('color', new THREE.Float32BufferAttribute(D.c, 3));
    if (uv) g.setAttribute('uv', new THREE.Float32BufferAttribute(D.u, 2)); g.setIndex(D.i); g.computeVertexNormals(); g.computeBoundingSphere(); const m = new THREE.Mesh(g, mat); return m; };
  t.mBal = mk(t.bal, M.ballast, true); if (t.mBal) { t.mBal.geometry.setAttribute('uv1', t.mBal.geometry.attributes.uv); grp.add(t.mBal); }
  t.mRail = mk(t.rail, M.rail); if (t.mRail) grp.add(t.mRail);
  t.mRailLo = mk(t.railLo, M.rail); if (t.mRailLo) grp.add(t.mRailLo);
  const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), p = new THREE.Vector3(), s = new THREE.Vector3(), c = new THREE.Color(), UP = new THREE.Vector3(0, 1, 0);
  const inst = (geo, mat, list, fn) => { if (!list.length) return null; const im = new THREE.InstancedMesh(geo, mat, list.length);
    list.forEach((r, i) => { fn(r, i, im); }); im.instanceMatrix.needsUpdate = true; if (im.instanceColor) im.instanceColor.needsUpdate = true; im.computeBoundingSphere(); grp.add(im); return im; };
  const put = (r, im, i, sx = 1, dy = 0) => { p.set(r[0], r[2] + dy, -r[1]); q.setFromAxisAngle(UP, -r[3]); s.set(sx, 1, 1); im.setMatrixAt(i, m4.compose(p, q, s)); };
  // pölkyt: lähellä B97-muoto, kauempana laatikko
  t.mSl = inst(G_SLEEPER, M.conc, t.sl, (r, i, im) => { put(r, im, i, r[4]); c.setRGB(r[6], r[6], r[6] * 0.98); im.setColorAt(i, c); });
  t.mSlLo = inst(G_SLEEPER_LO, M.conc, t.sl, (r, i, im) => { put(r, im, i, r[4]); c.setRGB(r[6], r[6], r[6]); im.setColorAt(i, c); });
  t.mWood = inst(G_WOOD, M.wood, t.slw, (r, i, im) => { put(r, im, i, r[4]); c.setRGB(r[6], r[6] * 0.95, r[6] * 0.9); im.setColorAt(i, c); });
  const fl = t.sl.filter(r => r[4] === 1), wl = t.slw.filter(r => r[4] === 1);
  t.mPad = inst(G_FAST.pad, M.pad, fl, (r, i, im) => put(r, im, i));
  t.mIron = inst(G_FAST.iron, M.castIron, fl, (r, i, im) => put(r, im, i));
  t.mClip = inst(G_FAST.clip, M.clip, fl, (r, i, im) => put(r, im, i));
  t.mTp = inst(G_TIEPLATE, M.steel, wl, (r, i, im) => put(r, im, i));
  addMisc(t, grp);
  for (const o of grp.children) { o.userData.noT = true; o.frustumCulled = true; }
  // vapautetaan rakennusdata
  t.bal = t.rail = t.railLo = null;
  root.add(grp);
}

// ---------------------------------------------------------------- laiturit
function platformZ(x, y) {   // lähimmän raiteen kiskon taso + 550 mm
  let best = null;
  for (const tr of tracks) { if (tr.k === 'x') continue; const n = nearestOn(tr, x, y); if (!best || n.d < best.d) best = { d: n.d, z: at(tr, n.s).z + RAIL, tr, s: n.s }; }
  return best;
}
function buildPlatforms(root) {
  const out = [];
  for (const pl of RATA.pl) {
    const P = []; for (let k = 0; k + 1 < pl.p.length; k += 2) P.push([pl.p[k], pl.p[k + 1]]);
    if (P.length > 2 && P[0][0] === P[P.length - 1][0] && P[0][1] === P[P.length - 1][1]) P.pop();
    // reunat raiteen viereen tarkalleen 1,80 m keskeltä
    const info = P.map(([x, y]) => { const b = platformZ(x, y); return b; });
    const Q = P.map(([x, y], i) => { const b = info[i]; if (b.d < 2.8) { const a = at(b.tr, b.s), nx = a.dy, ny = -a.dx, sd = Math.sign((x - a.x) * nx + (y - a.y) * ny) || 1; return [a.x + nx * sd * PLAT_EDGE, a.y + ny * sd * PLAT_EDGE, true]; } return [x, y, false]; });
    const z = Math.max(...info.map(b => b.z)) + PLAT_H;
    // yläpinta
    const shape = new THREE.Shape(Q.map(([x, y]) => new THREE.Vector2(x, y)));
    const g = new THREE.ShapeGeometry(shape); g.rotateX(-Math.PI / 2); const pa = g.attributes.position;
    const uv = []; for (let i = 0; i < pa.count; i++) { uv.push(pa.getX(i) / 2, pa.getZ(i) / 2); pa.setY(i, z); }
    // ShapeGeometry (x, y) -> rotateX(-90°) -> (x, 0, -y): sama kuin pelin koordinaatit
    g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); g.computeVertexNormals();
    const top = new THREE.Mesh(g, M.plat); root.add(top);
    // reunat: pystypinta maahan, raiteen puolella reunakivi ja valkoinen turvaviiva + varoituslaatta
    const side = [], sideI = [], deco = { w: [], t: [], e: [] };
    for (let i = 0; i < Q.length; i++) { const a = Q[i], b = Q[(i + 1) % Q.length], L = Math.hypot(b[0] - a[0], b[1] - a[1]); if (L < 0.05) continue;
      const nb = side.length / 3; const za = info[i].z - RAIL - 0.6, zb = info[(i + 1) % Q.length].z - RAIL - 0.6;
      side.push(...W(a[0], a[1], z), ...W(b[0], b[1], z), ...W(b[0], b[1], zb), ...W(a[0], a[1], za)); sideI.push(nb, nb + 2, nb + 1, nb, nb + 3, nb + 2);
      if (a[2] && b[2] && L > 1) {   // raiteen puoleinen reuna
        const ux = (b[0] - a[0]) / L, uy = (b[1] - a[1]) / L; let ix = -uy, iy = ux;   // sisäänpäin (CCW-monikulmio: vasen)
        const mx = (a[0] + b[0]) / 2 + ix * 3, my = (a[1] + b[1]) / 2 + iy * 3, inside = new THREE.ShapePath();
        if (!THREE.ShapeUtils.isClockWise(Q.map(([x, y]) => new THREE.Vector2(x, y))) === false) { ix = -ix; iy = -iy; }
        const strip = (o0, o1, arr, dz) => { const n = arr.length / 3; for (const [px, py, o] of [[a[0], a[1], o0], [b[0], b[1], o0], [b[0], b[1], o1], [a[0], a[1], o1]]) arr.push(...W(px + ix * o, py + iy * o, z + dz)); return n; };
        deco.e.push([a, b, ix, iy]);
        strip(0.0, 0.32, deco.w, 0.004);           // reunakivi (vaalea)
        strip(0.55, 0.95, deco.t, 0.006);          // varoituslaatat
        strip(1.05, 1.15, deco.w, 0.005);          // valkoinen turvaviiva
      } }
    const sg = new THREE.BufferGeometry(); sg.setAttribute('position', new THREE.Float32BufferAttribute(side, 3)); sg.setIndex(sideI); sg.computeVertexNormals();
    root.add(new THREE.Mesh(sg, M.platSide));
    for (const [arr, mat] of [[deco.w, M.white], [deco.t, M.tact]]) { if (!arr.length) continue; const g2 = new THREE.BufferGeometry(); g2.setAttribute('position', new THREE.Float32BufferAttribute(arr, 3));
      const I = [], U = []; for (let k = 0; k < arr.length / 12; k++) { const b = k * 4; I.push(b, b + 2, b + 1, b, b + 3, b + 2); U.push(0, 0, 1, 0, 1, 1, 0, 1); }
      g2.setIndex(I); g2.setAttribute('uv', new THREE.Float32BufferAttribute(U, 2)); g2.computeVertexNormals(); const m = new THREE.Mesh(g2, mat); m.material.side = THREE.DoubleSide; root.add(m); }
    out.push({ ref: pl.ref, Q, z, poly: Q.map(([x, y]) => [x, y]) });
  }
  return out;
}
const inPoly = (x, y, P) => { let c = false; for (let i = 0, j = P.length - 1; i < P.length; j = i++) { const [xi, yi] = P[i], [xj, yj] = P[j]; if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) c = !c; } return c; };

// lasiset porraskatokset (alikulun portaat laitureilla) ja alikulun portaali asema-aukion puolella
function buildUnderpass(root, plats, TZg) {
  for (const [x, y, len, wid] of RATA.glass) {
    const pz = plats.find(p => inPoly(x, y, p.poly)) || plats[0]; const z = pz.z; const tr = platformZ(x, y), a = at(tr.tr, tr.s); const yaw = Math.atan2(a.dx, a.dy);
    const o = new THREE.Group(); o.position.set(...W(x, y, z)); o.rotation.y = -yaw;
    const h = 2.6, box = new THREE.Mesh(new THREE.BoxGeometry(wid, h, len), M.glass); box.position.y = h / 2; o.add(box);
    const roof = new THREE.Mesh(new THREE.BoxGeometry(wid + 0.3, 0.12, len + 0.3), M.frame); roof.position.y = h + 0.06; o.add(roof);
    for (let k = 0; k <= Math.round(len / 1.5); k++) for (const sx of [-1, 1]) { const m = new THREE.Mesh(new THREE.BoxGeometry(0.06, h, 0.06), M.frame); m.position.set(sx * wid / 2, h / 2, -len / 2 + k * len / Math.round(len / 1.5)); o.add(m); }
    const pit = new THREE.Mesh(new THREE.BoxGeometry(wid - 0.2, 0.02, len - 0.2), M.dark); pit.position.y = 0.01; o.add(pit);   // portaikon aukko
    root.add(o);
  }
  // (vanha jalankulkuportaali poistettu 21.11.2026: alikulku on Porttaali-ajotunneli, buildTunnel)
}

// Porttaali (omistaja 21.11.2026: "menee junaraiteiden alla, täällä kulkee myös citylinjan bussi"): ajotunneli raiteiden ja laitureiden ali.
// Katettu osa RATA.tun.t0..t1 akselilla, koillispäässä ramppi asema-aukiolle tukimuureineen, lattia korkeusmallin kaivannon pohjasta.
const TUN = RATA.tun;
const tunT = (x, y) => { if (!TUN) return null; const ux = TUN.b[0] - TUN.a[0], uy = TUN.b[1] - TUN.a[1], L = Math.hypot(ux, uy), dx = x - TUN.a[0], dy = y - TUN.a[1]; return { t: (dx * ux + dy * uy) / L, l: (dx * uy - dy * ux) / L }; };
const tunFloor = t => { const k = (t - TUN.ft0) / 2, i = Math.max(0, Math.min(TUN.fz.length - 2, Math.floor(k))), f = Math.max(0, Math.min(1, k - i)); return TUN.fz[i] * (1 - f) + TUN.fz[i + 1] * f; };
// käytävä (maa pois): katettu osa, koillisramppi ja lounaan ajorata Ratapihantielle (kääntyy -l-suuntaan)
const tunIn = (c, m) => c && c.t > TUN.t0 - 40 && c.t < TUN.t1 + 36 && c.l < TUN.w / 2 + m && c.l > -(TUN.w / 2 + m + (c.t > TUN.t1 ? 4.5 + Math.max(0, c.t - TUN.t1 - 20) * 0.25 : 0));
const inTun = (x, y, m = 0) => { const c = tunT(x, y); return tunIn(c, 0.8 + m) ? c : null; };
const tunOff = t => t <= TUN.t1 + 6 ? 0 : -4.2 * Math.min(1, (t - TUN.t1 - 6) / 28) ** 2;   // lounaan ajoradan kaarre Ratapihantielle (buildTunnel)
// 21.11.2026: Porttaalin seinät kiinteiksi (ennen auto ajoi laattaseinän läpi ja hyppäsi ratapihan tasolle). Palauttaa, kuinka syvällä (m) piste (x, y) on
// seinävyöhykkeessä, kun kulkija on korkeudella z seinän yläreunan alapuolella; 0 = vapaa. carBlocked (js/090) estää liikkeen, joka vie syvemmälle.
function tunWallDepth(x, y, z, TZ) { const c = tunT(x, y); if (!c) return 0; const tA = TUN.t0 - 38; if (c.t < tA - 0.5 || c.t > TUN.t1 + 8) return 0;
  const hw = TUN.w / 2, al = Math.abs(c.l), d = al - (hw - 0.05); if (d <= 0 || al > hw + 1.2) return 0;
  const f = tunFloor(c.t), cov = c.t >= TUN.t0 && c.t <= TUN.t1, P = window.__porttaali;
  const top = cov ? (P ? P.ceil : f + 4) : Math.max(f + 0.3, TZ ? TZ(x, y) : f) + 0.25 + (c.t < TUN.t0 ? 1.25 : 0);   // rampin tukimuuri + kaide
  if (z > top + 0.2) return 0;                          // ylhäällä (ratapihalla, kannella): seinä on alapuolella
  return d; }
function buildTunnel(root, G, plats) {
  if (!TUN) return; const TZ = G.TZg || G.TZs;
  const ux = (TUN.b[0] - TUN.a[0]), uy = (TUN.b[1] - TUN.a[1]), L = Math.hypot(ux, uy), u = [ux / L, uy / L], nrm = [u[1], -u[0]];
  const P = (t, l) => [TUN.a[0] + u[0] * t + nrm[0] * l, TUN.a[1] + u[1] * t + nrm[1] * l];
  let top = 1e9; for (const tr of tracks) for (let k = 0; k < tr.n; k++) if (tr.TN[k]) top = Math.min(top, tr.Z[k]);
  const slabTop = top - 0.72, ceil = slabTop - 0.45, hw = TUN.w / 2;
  const asph = new THREE.MeshStandardMaterial({ map: concTex, color: 0x3a3c3f, roughness: 0.9 }), wallM = new THREE.MeshStandardMaterial({ map: concTex, color: 0x9a9a95, roughness: 0.9, side: THREE.DoubleSide }),
    ceilM = new THREE.MeshStandardMaterial({ map: concTex, color: 0x6d6e6c, roughness: 0.9, side: THREE.DoubleSide }), lampM = new THREE.MeshBasicMaterial({ color: 0xfff1d0 }), lineM = new THREE.MeshBasicMaterial({ color: 0xd9d9d2 });
  const tileTex = canvasTex(240, 240, (g, w, h) => {   // omistaja 21.11.: "kirkkaan valkoista kiiltävää laattaa 10x15" -> ruutu 0,6 × 0,6 m = 6 × 4 laattaa
    g.fillStyle = '#ffffff'; g.fillRect(0, 0, w, h); g.strokeStyle = '#d4d6d8'; g.lineWidth = 2;
    for (let k = 0; k <= 6; k++) { g.beginPath(); g.moveTo(k * 40, 0); g.lineTo(k * 40, h); g.stroke(); }
    for (let k = 0; k <= 4; k++) { g.beginPath(); g.moveTo(0, k * 60); g.lineTo(w, k * 60); g.stroke(); }
    for (let i = 0; i < 6; i++) for (let j = 0; j < 4; j++) { const gr = g.createLinearGradient(i * 40, j * 60, i * 40 + 40, j * 60 + 60); gr.addColorStop(0, 'rgba(255,255,255,0.6)'); gr.addColorStop(0.5, 'rgba(235,238,240,0.0)'); gr.addColorStop(1, 'rgba(225,228,232,0.35)'); g.fillStyle = gr; g.fillRect(i * 40 + 1, j * 60 + 1, 38, 58); } });
  const tileM = new THREE.MeshStandardMaterial({ map: tileTex, color: 0xffffff, emissive: 0x9aa0a6, emissiveMap: tileTex, roughness: 0.08, metalness: 0.0, side: THREE.DoubleSide });   // kirkkaan valkoinen kiiltävä laatta 10 × 15 cm
  const glowM = new THREE.MeshBasicMaterial({ color: 0xfdfcf6, side: THREE.DoubleSide });                                                    // valaistu valkoinen taustaseinä
  const glassM = new THREE.MeshStandardMaterial({ color: 0xdfeef2, roughness: 0.04, metalness: 0.2, transparent: true, opacity: 0.18, depthWrite: false, side: THREE.DoubleSide });
  const deckM = new THREE.MeshStandardMaterial({ map: platTex, color: 0x9a9a9a, roughness: 0.9, side: THREE.DoubleSide });
  const frameM = new THREE.MeshStandardMaterial({ color: 0xc8ccd0, roughness: 0.3, metalness: 0.6, side: THREE.DoubleSide });
  const quads = new Map(); const Q = (m, a, b, c, d) => { let L2 = quads.get(m); if (!L2) quads.set(m, L2 = []); L2.push(a, b, c, a, c, d); };
  const V = (t, l, z) => { const [x, y] = P(t, l); return W(x, y, z); };
  const tA = TUN.t0 - 38, tB = TUN.t1 + 36, st = 2;
  // lounaispää (omistaja 21.11.: "lounaispään liittymä"): ajorata jatkuu portaalista 34 m ja kääntyy Ratapihantien päähän (akselilla t 134, sivussa -7 m)
  const off = t => t <= TUN.t1 + 6 ? 0 : -4.2 * Math.min(1, (t - TUN.t1 - 6) / 28) ** 2;
  const zr = t => t <= TUN.t1 ? tunFloor(t) : Math.max(tunFloor(t), TZ(...P(t, off(t))) + 0.04);
  for (let t = tA; t < tB; t += st) { const t2 = Math.min(tB, t + st), f1 = tunFloor(t), f2 = tunFloor(t2), cov = t >= TUN.t0 && t2 <= TUN.t1 + 0.01;
    const r1 = zr(t), r2 = zr(t2), o1 = off(t), o2 = off(t2), fl1 = t > TUN.t1 + 20 ? 1 + (t - TUN.t1 - 20) * 0.25 : 0, fl2 = t2 > TUN.t1 + 20 ? 1 + (t2 - TUN.t1 - 20) * 0.25 : 0;   // levennys liittymään
    // ajorata + jalkakäytävä (1,4 m, +0,15) koillisen puolella
    Q(asph, V(t, o1 - hw - fl1, r1 + 0.04), V(t2, o2 - hw - fl2, r2 + 0.04), V(t2, o2 + hw - 1.4, r2 + 0.04), V(t, o1 + hw - 1.4, r1 + 0.04));
    Q(wallM, V(t, o1 + hw - 1.4, r1 + 0.19), V(t2, o2 + hw - 1.4, r2 + 0.19), V(t2, o2 + hw, r2 + 0.19), V(t, o1 + hw, r1 + 0.19));
    Q(wallM, V(t, o1 + hw - 1.4, r1 + 0.04), V(t2, o2 + hw - 1.4, r2 + 0.04), V(t2, o2 + hw - 1.4, r2 + 0.19), V(t, o1 + hw - 1.4, r1 + 0.19));
    if (Math.floor(t / 6) % 2 === 0 && t < TUN.t1 + 22) Q(lineM, V(t, o1 - 0.76, r1 + 0.05), V(t2, o2 - 0.76, r2 + 0.05), V(t2, o2 - 0.64, r2 + 0.05), V(t, o1 - 0.64, r1 + 0.05));   // keskiviiva
    // seinät: katetussa osassa kattoon asti, rampeissa maanpinnan tasoon (tukimuuri)
    if (cov) { for (const sd of [-1, 1]) {   // omistaja 21.11.: "seinät kiiltävää valkoista laattaa, yläosa kirkasta lasia, jonka takana valkoinen seinä ja valoa"
        const l = sd * (hw + 0.01), lb = sd * (hw + 0.2), mid1 = f1 + 2.2, mid2 = f2 + 2.2;
        Q(tileM, V(t, l, f1), V(t2, l, f2), V(t2, l, mid2), V(t, l, mid1));
        Q(tileM, V(t, l, mid1), V(t2, l, mid2), V(t2, lb, mid2), V(t, lb, mid1));                        // laattareunan hylly
        Q(glowM, V(t, lb, mid1), V(t2, lb, mid2), V(t2, lb, ceil), V(t, lb, ceil));                      // valaistu valkoinen seinä lasin takana
        Q(glassM, V(t, l, mid1 + 0.02), V(t2, l, mid2 + 0.02), V(t2, l, ceil - 0.02), V(t, l, ceil - 0.02));   // kirkas lasi
        Q(frameM, V(t, l * 1.002, mid1), V(t + 0.06, l * 1.002, mid1), V(t + 0.06, l * 1.002, ceil), V(t, l * 1.002, ceil));   // lasin karmi 2 m välein
        Q(frameM, V(t, l * 1.002, mid1 - 0.03), V(t2, l * 1.002, mid2 - 0.03), V(t2, l * 1.002, mid1 + 0.05), V(t, l * 1.002, mid1 + 0.05)); } }
    else if (t < TUN.t1 + 8) for (const sd of [-1, 1]) { const e1 = sd < 0 ? fl1 : 0, e2 = sd < 0 ? fl2 : 0, la = o1 + sd * (hw + 0.01 + e1), lb = o2 + sd * (hw + 0.01 + e2), b1 = Math.min(f1, r1), b2 = Math.min(f2, r2);
      const g1 = cov ? ceil : Math.max(r1 + 0.3, TZ(...P(t, la + sd * 1.2))), g2 = cov ? ceil : Math.max(r2 + 0.3, TZ(...P(t2, lb + sd * 1.2)));
      Q(wallM, V(t, la, b1), V(t2, lb, b2), V(t2, lb, g2 + (cov ? 0 : 0.25)), V(t, la, g1 + (cov ? 0 : 0.25)));
      if (!cov && g1 - r1 > 0.6) Q(wallM, V(t, la, g1 + 0.25), V(t2, lb, g2 + 0.25), V(t2, lb + sd * 0.3, g2 + 0.25), V(t, la + sd * 0.3, g1 + 0.25)); }
    if (cov) { Q(ceilM, V(t, -hw - 0.3, ceil), V(t2, -hw - 0.3, ceil), V(t2, hw + 0.3, ceil), V(t, hw + 0.3, ceil));
      Q(lampM, V(t, -0.12, ceil - 0.02), V(t2 - 0.6, -0.12, ceil - 0.02), V(t2 - 0.6, 0.12, ceil - 0.02), V(t, 0.12, ceil - 0.02)); }
  }
  // otsamuurit (portaalit) katetun osan päissä: aukon yläpuolelta kiskojen tasoon ja sivuilta maahan
  for (const [t0, s] of [[TUN.t0, -1], [TUN.t1, 1]]) { const f = tunFloor(t0);
    Q(wallM, V(t0, -hw - 1.0, ceil), V(t0, hw + 1.0, ceil), V(t0, hw + 1.0, top + 0.35), V(t0, -hw - 1.0, top + 0.35));   // otsapalkki
    Q(wallM, V(t0 + s * 0.6, -hw - 1.0, top + 0.35), V(t0 + s * 0.6, hw + 1.0, top + 0.35), V(t0, hw + 1.0, top + 0.35), V(t0, -hw - 1.0, top + 0.35));
    for (const sd of [-1, 1]) Q(wallM, V(t0, sd * hw, f - 0.2), V(t0, sd * (hw + 12.0), f - 0.2), V(t0, sd * (hw + 12.0), top + 0.35), V(t0, sd * hw, top + 0.35));   // siipimuurit: penkka ei valu portaalin sivuilta
    Q(wallM, V(t0, -hw - 7.0, top + 0.35), V(t0, hw + 12.0, top + 0.35), V(t0 + s * 0.6, hw + 12.0, top + 0.35), V(t0 + s * 0.6, -hw - 7.0, top + 0.35)); }
  // kansilaatan yläpinta ja sivut (raiteiden ja laitureiden alla, ei näy ylhäältä)
  Q(ceilM, V(TUN.t0, -hw - 1, slabTop), V(TUN.t1, -hw - 1, slabTop), V(TUN.t1, hw + 1, slabTop), V(TUN.t0, hw + 1, slabTop));
  // kansi aukkojen päälle (omistaja 21.11.: "aukkojen kohdalle voisi lisätä kantta, päädyissä sulkea myös muodolla"): maan ruudukko on leikattu 8,3 m akselista,
  // joten kansi jatkuu tunnelin sivuille 9 m:iin kiveyksenä ratapihan tasossa, ja sen reunat suljetaan pystypinnalla maahan asti
  const dk = slabTop + 0.55, DW = hw + 9;
  for (let t = TUN.t0; t < TUN.t1; t += 2) { const t2 = Math.min(TUN.t1, t + 2);
    for (const sd of [-1, 1]) { Q(deckM, V(t, sd * (hw + 0.6), dk), V(t2, sd * (hw + 0.6), dk), V(t2, sd * DW, dk), V(t, sd * DW, dk));
      const g1 = Math.min(dk - 0.3, TZ(...P(t, sd * (DW + 0.8)))), g2 = Math.min(dk - 0.3, TZ(...P(t2, sd * (DW + 0.8))));
      Q(wallM, V(t, sd * DW, g1 - 0.4), V(t2, sd * DW, g2 - 0.4), V(t2, sd * DW, dk), V(t, sd * DW, dk)); } }
  for (const [t0, s] of [[TUN.t0, -1], [TUN.t1, 1]]) for (const sd of [-1, 1])   // päätypinnat kannen reunalle portaalin vierestä
    Q(wallM, V(t0, sd * (hw + 0.6), dk), V(t0, sd * DW, dk), V(t0, sd * DW, tunFloor(t0) - 0.2), V(t0, sd * (hw + 0.6), tunFloor(t0) - 0.2));
  for (const [m, arr] of quads) { const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(arr.flat(), 3));
    const sc = m === tileM ? 0.6 : 2, uv = []; for (let i = 0; i < arr.length; i++) uv.push(m === tileM ? (arr[i][0] * u[0] - arr[i][2] * u[1]) / sc : (arr[i][0] + arr[i][2]) / sc, arr[i][1] / sc); g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); g.computeVertexNormals();
    const me = new THREE.Mesh(g, m); m.side = THREE.DoubleSide; me.userData.noT = true; root.add(me); }
  // kaide rampin tukimuurien päälle
  const rails = []; for (const sd of [-1, 1]) { const pts = []; for (let t = tA; t <= TUN.t0; t += 2) { const g = Math.max(tunFloor(t) + 0.3, TZ(...P(t, sd * (hw + 1.2)))); pts.push(new THREE.Vector3(...V(t, sd * (hw + 0.15), g + 1.25))); }
    if (pts.length > 1) { const m = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), pts.length * 2, 0.03, 5), M.frame); m.userData.noT = true; root.add(m); } }
  const sign = canvasTex(512, 96, (g, w, h) => { g.fillStyle = '#1d4f91'; g.fillRect(0, 0, w, h); g.fillStyle = '#fff'; g.font = 'bold 54px sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('Porttaali', w / 2, h / 2 + 3); });
  const sm = new THREE.Mesh(new THREE.PlaneGeometry(3.2, 0.6), new THREE.MeshBasicMaterial({ map: sign, side: THREE.DoubleSide })); const [sx, sy] = P(TUN.t0 - 0.05, 0); sm.position.set(...W(sx, sy, (ceil + top) / 2)); sm.rotation.y = Math.atan2(u[0], -u[1]) + Math.PI; sm.userData.noT = true; root.add(sm);
  // maa rampin muurien takana (maan ruudukko on leikattu käytävän kohdalta): 1 m:n kaistat ilmakuvalla
  const OX0 = -2504.1, OY0 = -3501.6, OXS = 4954.9, OYS = 5396.0, gp = [], gu = [];
  for (const [ta, tb] of [[tA, TUN.t0], [TUN.t1, tB]]) for (let t = ta; t < tb; t += 2) { const t2 = Math.min(tb, t + 2);
    for (const sd of [-1, 1]) for (let l = hw + 0.3; l < hw + 6.6; l += 1.2) { const l2 = l + 1.2, ex = tt => off(tt) + (sd < 0 && tt > TUN.t1 + 20 ? -(1 + (tt - TUN.t1 - 20) * 0.25) : 0), pts = [[t, l], [t2, l], [t2, l2], [t, l2]].map(([tt, ll]) => { const [x, y] = P(tt, ex(tt) + sd * ll); return [x, y, TZ(x, y) + 0.02]; });
      for (const k of (sd > 0 ? [0, 1, 2, 0, 2, 3] : [0, 2, 1, 0, 3, 2])) { const [x, y, z] = pts[k]; gp.push(x, z, -y); gu.push((x - OX0) / OXS, (y - OY0) / OYS); } } }
  { const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(gp, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(gu, 2)); g.computeVertexNormals();
    const m = new THREE.Mesh(g, new THREE.MeshBasicMaterial({ map: G.outerMat ? G.outerMat.map : null, color: 0xffffff })); m.userData.noT = true; root.add(m); }
  // nurmiluiskat lounaispään portaalin sivuilla (omistaja 21.11.: "pitäisikö lisätä nurmikkoa"): pelin oma nurmitekstuuri (nurmi_albedo/normal/orm.jpg)
  if (TUN.gr) { const ld = n => { const t = texL.load(new URL('../' + n, import.meta.url).href); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; return t; };
    const na = ld('nurmi_albedo.jpg'); na.colorSpace = THREE.SRGBColorSpace;
    const gm = new THREE.MeshStandardMaterial({ map: na, normalMap: ld('nurmi_normal.jpg'), aoMap: ld('nurmi_orm.jpg'), color: 0xb8c0a8, roughness: 0.95, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -6, polygonOffsetUnits: -6 }); gm.userData.noT = true;
    const gp = [], gu = [], gI = []; const S = 1.5;
    for (const [T0g, LEN, WID] of [[TUN.t1 - 0.5, 34, 25.5], [TUN.t0 - 38, 37.5, 7.5]]) for (const sd of [-1, 1]) { const NT = Math.round(LEN / S), NL = Math.round(WID / S), base = gp.length / 3;   // lounaan luiskat ja koillisrampin reunat
      for (let i = 0; i <= NT; i++) for (let j = 0; j <= NL; j++) { const t = T0g + i * S, l = sd * (hw + (T0g < TUN.t0 ? 0.35 : 0.4) + j * S) + (sd < 0 && t > TUN.t1 ? off(t) - (t > TUN.t1 + 20 ? 1 + (t - TUN.t1 - 20) * 0.25 : 0) : 0), [x, y] = P(t, l); gp.push(...W(x, y, TZ(x, y) + 0.06)); gu.push(x / 3, y / 3); }
      for (let i = 0; i < NT; i++) for (let j = 0; j < NL; j++) { const a = base + i * (NL + 1) + j, b = a + NL + 1; if (sd > 0) gI.push(a, b, b + 1, a, b + 1, a + 1); else gI.push(a, b + 1, b, a, a + 1, b + 1); } }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(gp, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(gu, 2)); g.setIndex(gI); g.computeVertexNormals();
    const m = new THREE.Mesh(g, gm); m.userData.noT = true; root.add(m); }
  window.__porttaali = { top, ceil, slabTop };
  console.log('[rata] Porttaali: lattia', tunFloor(50).toFixed(2), 'katto', ceil.toFixed(2), 'vapaa korkeus', (ceil - tunFloor(50)).toFixed(2), 'm');
}

// Helsingintien sillat Porttaalin lounaispään yli (RATA.silta; index.html nostaa tienpinnan suoraksi päiden välille): kansi, reunapalkit, kaiteet, maatuet
function buildRoadBridges(root, G) {
  const TZ = G.TZg || G.TZs, conc = M.bridge;
  for (const S of RATA.silta || []) { const dx = S.b[0] - S.a[0], dy = S.b[1] - S.a[1], L = Math.hypot(dx, dy), u = [dx / L, dy / L], n = [u[1], -u[0]], hw = S.w / 2;
    const P = (t, l) => [S.a[0] + u[0] * t + n[0] * l, S.a[1] + u[1] * t + n[1] * l], Z = t => S.za + (S.zb - S.za) * t / L + 0.12;
    const tg = p => (p[0] - S.a[0]) * u[0] + (p[1] - S.a[1]) * u[1], t0 = tg(S.ga) - 4, t1 = tg(S.gb) + 4;   // kansi OSM-sillan päistä 4 m yli
    const tp = [], tu = [], tI = [];
    const p = [], I = []; const quad = (a, b, c, d) => { const k = p.length / 3; p.push(...a, ...b, ...c, ...d); I.push(k, k + 1, k + 2, k, k + 2, k + 3, k, k + 2, k + 1, k, k + 3, k + 2); };
    const V = (t, l, dz) => { const [x, y] = P(t, l); return W(x, y, Z(t) + dz); };
    for (let t = t0; t < t1; t += 2) { const t2 = Math.min(t1, t + 2);
      { const k = tp.length / 3; for (const [tt, ll] of [[t, -hw], [t2, -hw], [t2, hw], [t, hw]]) { const v = V(tt, ll, 0.02); tp.push(...v); tu.push((v[0] + 2504.1) / 4954.9, (-v[2] + 3501.6) / 5396.0); } tI.push(k, k + 1, k + 2, k, k + 2, k + 3, k, k + 2, k + 1, k, k + 3, k + 2); }   // kannen pinta: ilmakuvan tie
      quad(V(t, -hw, -1.0), V(t2, -hw, -1.0), V(t2, hw, -1.0), V(t, hw, -1.0));                // alapinta
      for (const sd of [-1, 1]) { const l = sd * hw; quad(V(t, l, -1.0), V(t2, l, -1.0), V(t2, l, 0.75), V(t, l, 0.75)); quad(V(t, l, 0.75), V(t2, l, 0.75), V(t2, l - sd * 0.35, 0.75), V(t, l - sd * 0.35, 0.75)); } }
    // maatuet OSM-sillan päihin: seinä maasta kanteen
    for (const tt of [tg(S.ga) - 0.5, tg(S.gb) + 0.5]) { const [x0, y0] = P(tt, 0), g = TZ(x0, y0); quad(V(tt, -hw - 1, -1.0), V(tt, hw + 1, -1.0), V(tt, hw + 1, g - Z(tt) - 0.3), V(tt, -hw - 1, g - Z(tt) - 0.3)); }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(p, 3)); g.setIndex(I); g.computeVertexNormals();
    const m = new THREE.Mesh(g, conc); m.userData.noT = true; root.add(m);
    { const g2 = new THREE.BufferGeometry(); g2.setAttribute('position', new THREE.Float32BufferAttribute(tp, 3)); g2.setAttribute('uv', new THREE.Float32BufferAttribute(tu, 2)); g2.setIndex(tI); g2.computeVertexNormals();
      const m2 = new THREE.Mesh(g2, new THREE.MeshBasicMaterial({ map: G.outerMat ? G.outerMat.map : null })); m2.userData.noT = true; root.add(m2); }
    for (const sd of [-1, 1]) { const pts = []; for (let t = t0; t <= t1; t += 2) pts.push(new THREE.Vector3(...V(t, sd * (hw - 0.17), 1.75)));
      const tg2 = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), pts.length * 2, 0.04, 5), M.frame); tg2.userData.noT = true; root.add(tg2); }
  }
}

// sillat: kansilaatta, reunapalkit ja kaiteet sepelin alle
function buildBridges(root) {
  const p = [], I = [], rails = [];
  for (const tr of tracks) { let run = [];
    const flush = () => { if (run.length > 1) {
      for (let k = 0; k + 1 < run.length; k++) { const a = run[k], b = run[k + 1];
        for (const [o0, o1, h0, h1] of [[-2.35, 2.35, -0.72, -0.72], [-2.35, -2.35, -1.6, 0.45], [2.35, 2.35, -1.6, 0.45], [-2.35, -2.05, 0.45, 0.45], [2.05, 2.35, 0.45, 0.45], [-2.05, -2.05, -0.7, 0.45], [2.05, 2.05, -0.7, 0.45], [-2.35, 2.35, -1.6, -1.6]]) {
          const n = p.length / 3, an = [a.dy, -a.dx], bn = [b.dy, -b.dx];
          p.push(...W(a.x + an[0] * o0, a.y + an[1] * o0, a.z + h0), ...W(b.x + bn[0] * o0, b.y + bn[1] * o0, b.z + h0), ...W(b.x + bn[0] * o1, b.y + bn[1] * o1, b.z + h1), ...W(a.x + an[0] * o1, a.y + an[1] * o1, a.z + h1));
          I.push(n, n + 1, n + 2, n, n + 2, n + 3, n, n + 2, n + 1, n, n + 3, n + 2); } }
      for (const sd of [-1, 1]) rails.push(run.map(a => W(a.x + a.dy * sd * 2.2, a.y - a.dx * sd * 2.2, a.z + 1.45))); }
      run = []; };
    for (let s = 0; s <= tr.L; s += 2) { const a = at(tr, s); if (a.br) run.push(a); else flush(); } flush(); }
  if (!p.length) return;
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(p, 3)); g.setIndex(I); g.computeVertexNormals();
  const m = new THREE.Mesh(g, M.bridge); m.userData.noT = true; root.add(m);
  for (const r of rails) { const c = new THREE.CatmullRomCurve3(r.map(v => new THREE.Vector3(...v))); const tg = new THREE.TubeGeometry(c, r.length * 2, 0.03, 5, false); const mm = new THREE.Mesh(tg, M.frame); mm.userData.noT = true; root.add(mm);
    for (const v of r) { const post = new THREE.Mesh(new THREE.BoxGeometry(0.05, 1.0, 0.05), M.frame); post.position.set(v[0], v[1] - 0.5, v[2]); post.userData.noT = true; root.add(post); } }
}

// tasoristeykset: kumilevyt kiskojen välissä ja ulkopuolella kiskon tasossa
function buildCrossings(root) {
  const p = [], I = [], U = [];
  for (const tr of tracks) { let run = [];
    const flush = () => { if (run.length > 1) for (let k = 0; k + 1 < run.length; k++) { const a = run[k], b = run[k + 1];
      for (const [o0, o1] of [[-2.0, -GAUGE_HALF - 0.05], [-GAUGE_HALF + 0.05, GAUGE_HALF - 0.05], [GAUGE_HALF + 0.05, 2.0]]) { const n = p.length / 3;
        for (const [q, o] of [[a, o0], [b, o0], [b, o1], [a, o1]]) { p.push(...W(q.x + q.dy * o, q.y - q.dx * o, q.z + RAIL - 0.005)); U.push(o, q.s / 2); }
        I.push(n, n + 2, n + 1, n, n + 3, n + 2); } } run = []; };
    for (let s = 0; s <= tr.L; s += 1) { const a = at(tr, s); a.s = s; if (a.lc) run.push(a); else flush(); } flush(); }
  if (!p.length) return;
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(p, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(U, 2)); g.setIndex(I); g.computeVertexNormals();
  const m = new THREE.Mesh(g, M.rubber); m.material.side = THREE.DoubleSide; m.userData.noT = true; root.add(m);
}

// opastimet, puskimet
function buildSignals(root) {
  const mast = new THREE.CylinderGeometry(0.07, 0.08, 1, 8); mast.translate(0, 0.5, 0);
  for (const [k, x, y, ref, sm] of RATA.n) {
    if (k !== 'si' && k !== 'bu') continue;
    let best = null; for (const tr of tracks) { const n = nearestOn(tr, x, y); if (!best || n.d < best.d) best = { tr, ...n }; }
    if (!best || best.d > 4) continue; const a = at(best.tr, best.s);
    if (k === 'bu') {   // puskin: teräspalkit ja punavalkoinen kilpi
      const o = new THREE.Group(); o.position.set(...W(a.x, a.y, a.z + RAIL)); o.rotation.y = -Math.atan2(a.dx, a.dy);
      const beam = new THREE.Mesh(new THREE.BoxGeometry(2.0, 0.3, 0.3), M.steel); beam.position.set(0, 0.75, 0); o.add(beam);
      for (const sx of [-1, 1]) { const st = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.9, 1.6), M.steel); st.position.set(sx * GAUGE_HALF, 0.35, 0.6); st.rotation.x = 0.45; o.add(st); }
      const pl = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.5, 0.03), M.sigRed); pl.position.set(0, 1.2, -0.05); o.add(pl);
      o.traverse(c => c.userData.noT = true); root.add(o); continue; }
    // opastin raiteen oikealla puolella; pääopastin korkealla mastossa, muut matalia
    const tall = sm === 'FI:Po' && /^[EPT]/.test(ref || '') || (ref && /^[EPT]/.test(ref));
    const nx = a.dy, ny = -a.dx, side = 2.4, o = new THREE.Group(); o.position.set(...W(a.x + nx * side, a.y + ny * side, a.z));
    o.rotation.y = -Math.atan2(a.dx, a.dy);
    const h = tall ? 4.2 : 0.9; const m = new THREE.Mesh(mast, M.mast); m.scale.y = h; o.add(m);
    const head = new THREE.Mesh(new THREE.BoxGeometry(0.36, tall ? 1.0 : 0.5, 0.18), M.sigBlack); head.position.set(0, h + (tall ? 0.5 : 0.25), 0); o.add(head);
    const lamp = new THREE.Mesh(new THREE.CircleGeometry(0.065, 12), tall ? M.sigRed : M.sigWhite); lamp.position.set(0, h + (tall ? 0.75 : 0.32), 0.095); o.add(lamp);
    if (tall) { const l2 = new THREE.Mesh(new THREE.CircleGeometry(0.065, 12), M.sigBlack); l2.position.set(0, h + 0.45, 0.095); o.add(l2); }
    const back = new THREE.Mesh(new THREE.BoxGeometry(0.5, tall ? 1.15 : 0.6, 0.02), M.sigBlack); back.position.set(0, h + (tall ? 0.5 : 0.25), -0.1); o.add(back);
    o.traverse(c => c.userData.noT = true); root.add(o);
  }
}

// ---------------------------------------------------------------- ajojohdin (25 kV): pylväät ulokkeineen, ratapihalla portaalit; ajo- ja kantolanka
const WIRE_H = 6.15, MESS_H = 7.45, SPAN = 55;
function buildCatenary(root) {
  const el = tracks.filter(t => t.e && t.k !== 'x'); if (!el.length) return { wires: [] };
  const lines = [], wires = [];
  const supports = el.map(() => []);
  const mastG = new THREE.BoxGeometry(0.22, 1, 0.22); mastG.translate(0, 0.5, 0);
  const placed = [];
  for (const [ti, tr] of el.entries()) {
    for (let s = 6; s < tr.L - 3; s += SPAN) {
      const a = at(tr, s); if (a.lc) continue; const nx = a.dy, ny = -a.dx;
      if (placed.some(p => Math.hypot(p[0] - a.x, p[1] - a.y) < 12)) { supports[ti].push(s); continue; }   // jo portaalissa
      // poikkiviiva: muut sähköistetyt raiteet ±40 m
      const hits = [];
      for (const [tj, t2] of el.entries()) { const n = nearestOn(t2, a.x, a.y); if (n.d > 45) continue; const b = at(t2, n.s); const off = (b.x - a.x) * nx + (b.y - a.y) * ny, along = (b.x - a.x) * a.dx + (b.y - a.y) * a.dy;
        if (Math.abs(along) < 4) hits.push({ tj, off, b, s: n.s }); }
      hits.sort((u, v) => u.off - v.off);
      // ryhmä: peräkkäiset alle 7 m välein
      let lo = hits.findIndex(h => h.tj === ti), hi = lo; while (lo > 0 && hits[lo].off - hits[lo - 1].off < 7.5) lo--; while (hi < hits.length - 1 && hits[hi + 1].off - hits[hi].off < 7.5) hi++;
      const grp = hits.slice(lo, hi + 1);
      const z0 = Math.max(...grp.map(h => h.b.z)) + RAIL;
      if (grp.length === 1) {   // yksittäinen pylväs ulokkeineen, sille puolelle missä tilaa
        const sd = (hits[lo - 1] && !hits[hi + 1]) ? 1 : -1; const px = a.x + nx * sd * 3.3, py = a.y + ny * sd * 3.3;
        const o = new THREE.Group(); o.position.set(...W(px, py, a.z - 0.3)); o.rotation.y = -Math.atan2(a.dx, a.dy) + (sd > 0 ? Math.PI : 0);
        const m = new THREE.Mesh(mastG, M.mast); m.scale.y = 8.6; o.add(m);
        const arm = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 3.6, 6), M.mast); arm.rotation.z = Math.PI / 2 - 0.06; arm.position.set(-1.75, WIRE_H + 0.6 - a.z * 0 + 0.3, 0); o.add(arm);
        const arm2 = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 3.9, 6), M.mast); arm2.rotation.z = Math.PI / 2 + 0.35; arm2.position.set(-1.8, MESS_H + 0.55, 0); o.add(arm2);
        const ins = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.07, 0.5, 8), M.insul); ins.rotation.z = Math.PI / 2; ins.position.set(-0.4, WIRE_H + 0.95, 0); o.add(ins);
        o.traverse(c => c.userData.noT = true); root.add(o);
      } else if (grp.length > 1) {   // portaali ryhmän yli
        const f = grp[0], l = grp[grp.length - 1];
        const A = [a.x + nx * (f.off - 3.3), a.y + ny * (f.off - 3.3)], B = [a.x + nx * (l.off + 3.3), a.y + ny * (l.off + 3.3)];
        const o = new THREE.Group(); root.add(o);
        for (const [x, y] of [A, B]) { const m = new THREE.Mesh(mastG, M.mast); m.scale.y = 8.8; m.position.set(...W(x, y, z0 - RAIL - 0.3)); o.add(m); }
        const L = Math.hypot(B[0] - A[0], B[1] - A[1]); const beam = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.5, L), M.mast); beam.position.set(...W((A[0] + B[0]) / 2, (A[1] + B[1]) / 2, z0 - RAIL + 8.2)); beam.rotation.y = -Math.atan2(B[0] - A[0], B[1] - A[1]); o.add(beam);
        for (const h of grp) { const hx = a.x + nx * h.off, hy = a.y + ny * h.off; const dr = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 8.2 - (WIRE_H + 0.05) + RAIL, 5), M.mast); dr.position.set(...W(hx, hy, z0 + (WIRE_H + 8.2 - RAIL) / 2 - 0.02)); o.add(dr); }
        o.traverse(c => c.userData.noT = true);
        placed.push([a.x, a.y]); for (const h of grp) placed.push([h.b.x, h.b.y]);
      }
      supports[ti].push(s);
    }
  }
  // langat: siksak ±0,25 m tukien välillä, kantolanka riippuu (kaari) ja tiputtimet 5 m välein
  const pos = [];
  for (const [ti, tr] of el.entries()) {
    const W2 = []; let zig = 1; const sup = supports[ti].length ? supports[ti] : [0, tr.L];
    const st = [0, ...sup, tr.L];
    for (let k = 0; k + 1 < st.length; k++) { const s0 = st[k], s1 = st[k + 1], n = Math.max(1, Math.round((s1 - s0) / 5));
      for (let j = 0; j <= n; j++) { if (k && !j) continue; const s = s0 + (s1 - s0) * j / n, a = at(tr, s), f = j / n, off = zig * 0.25 * (1 - 2 * f) * (k % 2 ? -1 : 1), sag = Math.sin(f * Math.PI) * 0.9;
        const cw = W(a.x + a.dy * off, a.y - a.dx * off, a.z + RAIL + WIRE_H), mw = W(a.x + a.dy * off * 0.3, a.y - a.dx * off * 0.3, a.z + RAIL + MESS_H - sag);
        W2.push([cw, mw, a]); } }
    for (let k = 0; k + 1 < W2.length; k++) { pos.push(...W2[k][0], ...W2[k + 1][0], ...W2[k][1], ...W2[k + 1][1]); pos.push(...W2[k][0], ...W2[k][1]); }
    wires.push({ tr, pts: W2.map(w => w[0]) });
  }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  const ls = new THREE.LineSegments(g, M.wire); ls.userData.noT = true; ls.frustumCulled = false; root.add(ls);
  return { wires };
}

// ulkokehän maa raiteiden kohdalla: 18 m solujen tilalle 6 m ruudukko painetun ratapenkan mukaan (index.html jättää solut RATA.osk pois)
function buildOuterGround(root, G) {
  const OX0 = -2504.1, OY0 = -3501.6, OX1 = 2450.8, OY1 = 1894.4, OXS = OX1 - OX0, OYS = OY1 - OY0, onx = Math.round(OXS / 18), st = 6;
  const p = [], u = [], I = []; const TZ = G.TZg || G.TZs;
  for (const c of RATA.osk || []) { const i = c % onx, j = Math.floor(c / onx), x0 = OX0 + i * 18, y0 = OY0 + j * 18, b = p.length / 3;
    for (let b2 = 0; b2 <= 3; b2++) for (let a2 = 0; a2 <= 3; a2++) { const x = x0 + a2 * st, y = y0 + b2 * st; p.push(x, TZ(x, y), -y); u.push((x - OX0) / OXS, (y - OY0) / OYS); }
    for (let b2 = 0; b2 < 3; b2++) for (let a2 = 0; a2 < 3; a2++) { const c = tunT(x0 + (a2 + 0.5) * st, y0 + (b2 + 0.5) * st); if (tunIn(c, 4.5)) continue;   // Porttaali
      const k = b + b2 * 4 + a2; I.push(k, k + 1, k + 5, k, k + 5, k + 4); } }
  if (!p.length) return;
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(p, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(u, 2)); g.setIndex(I);
  const m = new THREE.Mesh(g, G.outerMat || new THREE.MeshBasicMaterial({ color: 0x777777 })); m.userData.noT = true; root.add(m);
}

// sepelikenttä koko rata-alueelle (omistaja 21.11.: "sepeliä voisi levittää laajemmalle, valkoista vuotaa ilmakuvista"):
// 2 m:n ruudut alle 7,5 m raiteista maan pinnan päälle; ei laitureille eikä tasoristeyksiin. Tiet (roads.js, +0,12) ja penkat jäävät päälle.
function buildBallastField(root, G, plats) {
  // vain asema-alueella (omistaja 21.11.: "tarkoituksena oli vain asema-alueella lisätä seisakkeiden paikalle"): laitureiden kohta ja 45 m niiden ympäriltä.
  // Reuna häivytetään (pikselikohtainen läpinäkyvyys), ei sahalaitaa.
  const near = trackIndex(2), C = 2, R = 9, TZ = G.TZg || G.TZs, LC = RATA.n.filter(n => n[0] === 'le').map(n => [n[1], n[2]]);
  const pdist = (x, y) => { let d = 1e9; for (const p of plats) { if (inPoly(x, y, p.poly)) return 0; for (const [px, py] of p.poly) d = Math.min(d, Math.hypot(px - x, py - y)); } return d; };
  const yard = (x, y) => pdist(x, y) < 45;
  const ycache = new Map(), isYard = (x, y) => { const k = Math.floor(x / 20) + ',' + Math.floor(y / 20); if (!ycache.has(k)) ycache.set(k, yard((Math.floor(x / 20) + 0.5) * 20, (Math.floor(y / 20) + 0.5) * 20)); return ycache.get(k); };
  const cells = new Set();
  for (const tr of tracks) for (let s = 0; s <= tr.L; s += 1.5) { const a = at(tr, s); if (a.br || !isYard(a.x, a.y)) continue;
    for (let i = Math.floor((a.x - R) / C); i <= Math.floor((a.x + R) / C); i++) for (let j = Math.floor((a.y - R) / C); j <= Math.floor((a.y + R) / C); j++) cells.add(i + ',' + j); }
  const dil = new Set(cells); for (const k of cells) { const [i, j] = k.split(',').map(Number); for (let a = -5; a <= 5; a++) for (let b = -5; b <= 5; b++) if (a * a + b * b <= 25) dil.add((i + a) + ',' + (j + b)); }
  const clo = new Set(cells); for (const k of dil) { const [i, j] = k.split(',').map(Number); let ok = true; for (let a = -5; a <= 5 && ok; a++) for (let b = -5; b <= 5; b++) if (a * a + b * b <= 25 && !dil.has((i + a) + ',' + (j + b))) { ok = false; break; } if (ok) clo.add(k); }
  const keep = new Set();
  for (const key of clo) { const [i, j] = key.split(',').map(Number), cx = (i + 0.5) * C, cy = (j + 0.5) * C;
    const b = near(cx, cy, 25); if (b && b.a.br && b.d < 6) continue;
    if (LC.some(([x, y]) => Math.hypot(x - cx, y - cy) < 7)) continue;
    const tc = inTun(cx, cy, 6); if (tc && !(tc.t > TUN.t0 + 0.5 && tc.t < TUN.t1 - 0.5)) continue;
    keep.add(key); }   // myös laiturin alle: reunan alta ei saa näkyä ilmakuvaa
  // reunasolmut läpinäkyviksi: solmu on sisällä, jos kaikki sen neljä solua ovat mukana
  const inner = (i, j) => keep.has((i - 1) + ',' + (j - 1)) && keep.has(i + ',' + (j - 1)) && keep.has((i - 1) + ',' + j) && keep.has(i + ',' + j);
  const chunks = new Map();
  for (const key of keep) { const [i, j] = key.split(',').map(Number), cx = (i + 0.5) * C, cy = (j + 0.5) * C;
    const ck = Math.floor(cx / 400) + ',' + Math.floor(cy / 400); let ch = chunks.get(ck); if (!ch) chunks.set(ck, ch = { p: [], u: [], c: [], i: [], m: new Map() });
    const v = (vi, vj) => { const k = vi + ',' + vj; let n = ch.m.get(k); if (n === undefined) { const x = vi * C, y = vj * C; n = ch.p.length / 3; ch.m.set(k, n); const tq = inTun(x, y, 6), zz = tq && tq.t > TUN.t0 - 0.5 && tq.t < TUN.t1 + 0.5 && window.__porttaali ? window.__porttaali.slabTop + 0.6 : TZ(x, y) + 0.06; ch.p.push(x, zz, -y); ch.u.push(x / 1.6, y / 1.6);
        const d = near(x, y, 25), f = d ? Math.min(1, d.d / 25) : 1, sh = 0.78 - 0.12 * f; ch.c.push(sh, sh * 0.97, sh * 0.93, inner(vi, vj) ? 1 : 0); } return n; };
    const a = v(i, j), b2 = v(i + 1, j), c = v(i + 1, j + 1), d = v(i, j + 1);
    ch.i.push(a, b2, c, a, c, d); }
  const mat = M.ballast.clone(); mat.polygonOffset = true; mat.polygonOffsetFactor = -4; mat.polygonOffsetUnits = -4; mat.userData.noT = true;
  mat.transparent = true; mat.depthWrite = false; mat.vertexColors = true;
  let n = 0;
  for (const ch of chunks.values()) { const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(ch.p, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(ch.u, 2));
    g.setAttribute('color', new THREE.Float32BufferAttribute(ch.c, 4)); g.setIndex(ch.i); g.computeVertexNormals(); const m = new THREE.Mesh(g, mat); m.renderOrder = -1; m.userData.noT = true; m.userData.field = true; root.add(m); n += ch.i.length / 3; }
  console.log('[rata] sepelikenttä (asema-alue)', n, 'kolmiota');
}

// ---------------------------------------------------------------- kokoaminen peliin
function luoRata({ scene, TZg, G }) {
  const root = new THREE.Group(); root.name = 'rata'; root.userData.noT = true;
  buildOuterGround(root, G);
  turnouts();
  NEARIDX = trackIndex(1);
  for (const tr of tracks) buildTrack(tr);
  for (const t of tiles.values()) finishTile(t, root);
  const plats = buildPlatforms(root);
  buildUnderpass(root, plats, TZg);
  buildCanopy(root, plats);
  buildTunnel(root, G, plats);
  buildRoadBridges(root, G);
  buildBallastField(root, G, plats);
  buildBridges(root);
  buildCrossings(root);
  buildSignals(root);
  const cat = buildCatenary(root);
  yhdista(root, o => !!o.userData.t || o.isLineSegments || o.material === G.outerMat || o.userData.field);
  root.traverse(o => { if (o.material !== G.outerMat) o.userData.noT = true; });
  scene.add(root);
  // etäisyystasot
  const upd = (cx, cy) => { for (const t of tiles.values()) { const d = Math.max(0, Math.hypot(t.cx - cx, t.cy - cy) - TILE * 0.71);
      if (t.mRail) t.mRail.visible = d < RAILHI; if (t.mRailLo) t.mRailLo.visible = d >= RAILHI;
      const near = d < NEAR, mid = d < MID;
      if (t.mSl) t.mSl.visible = d < 160; if (t.mSlLo) t.mSlLo.visible = d >= 160 && mid; if (t.mWood) t.mWood.visible = mid;
      for (const m of [t.mPad, t.mIron, t.mClip, t.mTp]) if (m) m.visible = near; } };
  // kävely: laiturit ja sepelipenkka (kiskon / pölkyn taso), ketjutetaan ranta.js:n laitureiden kanssa
  const prevZ = window.__laituriZ;
  window.__laituriZ = (x, y) => { let h = prevZ ? prevZ(x, y) : null;
    for (const p of plats) if (inPoly(x, y, p.poly)) h = Math.max(h ?? -1e9, p.z);
    return h; };
  // kävely ja ajo: laiturin pinta, sepelipenkalla pölkkyjen taso (index.html carGround kysyy window.__rataZ)
  const NZ = trackIndex(1);
  // vt 2:n sillat Porttaalin jatkeen yllä (omistaja 21.11.: "sillan alta ei voi kulkea portaalissa vaan se hyppää päälle"): kannen kohdalla kansi vain
  // sille, joka on jo kannen tasolla; alhaalla tulevalle (kävelijä tai pelaajan auto alle 2 m kannen alapuolella) maa = kaivannon pohja (index.html)
  const SIL = (RATA.silta || []).map(S => { const dx = S.b[0] - S.a[0], dy = S.b[1] - S.a[1], L = Math.hypot(dx, dy), u = [dx / L, dy / L];
    const tg = p => (p[0] - S.a[0]) * u[0] + (p[1] - S.a[1]) * u[1]; return { S, L, u, hw: S.w / 2, t0: tg(S.ga) - 4, t1: tg(S.gb) + 4 }; });
  const silZ = (x, y) => { for (const B of SIL) { const dx = x - B.S.a[0], dy = y - B.S.a[1], t = dx * B.u[0] + dy * B.u[1], l = dx * B.u[1] - dy * B.u[0];
      if (t < B.t0 || t > B.t1 || Math.abs(l) > B.hw) continue; const dz = B.S.za + (B.S.zb - B.S.za) * t / B.L + 0.14;
      const W2 = G.WALK, C = window.__car; let ref = null;
      if (W2 && W2.on && Math.hypot(W2.x - x, W2.y - y) < 25) ref = W2.z; else if (C && Math.hypot(C.x - x, C.y - y) < 25) ref = C.z;
      return ref !== null && ref < dz - 2 ? null : dz; } return undefined; };
  // 21.11.2026 (omistaja: "auto törmäilee näkymättömään, hyppii oudosti tiellä"): ajopinta on täsmälleen piirretty asfaltti (buildTunnel zr + 0,04, lounaassa
  // kaarre tunOff) eikä pelkkä tunFloor, jonka alle auto ennen painui lounaan rampissa. Maasto on tasoitettu (010_maasto.js), joten ero on pieni.
  const TZr = G.TZg || G.TZs;
  window.__rataZ = (x, y) => { { const s = silZ(x, y); if (s !== undefined) return s; } const c = inTun(x, y);
    if (c) { const fl = c.t <= TUN.t1 ? tunFloor(c.t) : Math.max(tunFloor(c.t), TZr(x, y) + 0.04), f = fl + 0.04, W2 = G.WALK; const up = c.t > TUN.t0 && c.t < TUN.t1 && W2 && W2.on && W2.z > f + 2.2;   // tunnelissa: lattia, paitsi kävelijä ylhäällä laiturilla
      if (!up) { const l = c.l - tunOff(c.t); return f + (l > TUN.w / 2 - 1.4 && l < TUN.w / 2 + 0.3 ? 0.15 : 0); } }
    for (const p of plats) if (inPoly(x, y, p.poly)) return p.z;
    const b = NZ(x, y, 2.3); if (b && !b.a.lc) return b.a.z + 0.02; return null; };
  window.__rataSeina = (x, y, z) => tunWallDepth(x, y, z, TZr);
  // bottiautot (js/092): vt 2:n sillan kansi, jos piste on kannella ja auto ajaa sillan suuntaan (alla Ratapihantietä ajava jää alas)
  window.__rataSiltaAjo = (x, y, yaw) => { const sx = Math.sin(yaw), sy = Math.cos(yaw);
    for (const B of SIL) { const dx = x - B.S.a[0], dy = y - B.S.a[1], t = dx * B.u[0] + dy * B.u[1], l = dx * B.u[1] - dy * B.u[0];
      if (t < B.t0 || t > B.t1 || Math.abs(l) > B.hw + 1.5 || Math.abs(sx * B.u[0] + sy * B.u[1]) < 0.7) continue; return B.S.za + (B.S.zb - B.S.za) * t / B.L + 0.14; } return null; };
  window.__rata = { tracks, at, nearestOn, plats, wires: cat.wires, upd, root, RATA, RAIL };
  console.log('[rata] raiteita', tracks.length, 'ruutuja', tiles.size, 'laitureita', plats.length);
  return root;
}

// raidealueen pinnat pois roads.js:n kerroksista (OSM:n alueet / kivetykset ulottuivat ratapihan päälle ja peittivät sepelin)
function trackIndex(step = 1) { const H = new Map(), C = 4; const k = (x, y) => Math.floor(x / C) + ',' + Math.floor(y / C);
  for (const tr of tracks) for (let s = 0; s <= tr.L; s += step) { const a = at(tr, s); a.tr = tr; if (a.lc) continue; const key = k(a.x, a.y); let l = H.get(key); if (!l) H.set(key, l = []); l.push(a); }
  return (x, y, r, ex) => { let best = null; const i0 = Math.floor((x - r) / C), i1 = Math.floor((x + r) / C), j0 = Math.floor((y - r) / C), j1 = Math.floor((y + r) / C);
    for (let i = i0; i <= i1; i++) for (let j = j0; j <= j1; j++) { const l = H.get(i + ',' + j); if (l) for (const a of l) { if (ex && a.tr === ex) continue; const d = Math.hypot(a.x - x, a.y - y); if (d < r && (!best || d < best.d)) best = { d, a }; } } return best; }; }
function clearRoadsOnTracks(scene, root) {
  const near = trackIndex(); let cut = 0, meshes = 0;
  scene.traverse(m => { if (!m.isMesh || m.isInstancedMesh || !m.userData.noT || !m.material || m.material.type !== 'MeshStandardMaterial') return;
    let p = m; while (p) { if (p === root) return; p = p.parent; }
    const g = m.geometry, P = g.attributes.position; if (!P || !g.index || m.matrixWorld.elements[13] !== 0) return; const I = g.index.array; const keep = []; let c0 = 0;
    for (let t = 0; t < I.length; t += 3) { let inside = 0;
      for (let v = 0; v < 3; v++) { const k = I[t + v], x = P.getX(k), y = -P.getZ(k), h = P.getY(k), b = near(x, y, 2.9); if (b && h < b.a.z + 0.6 && h > b.a.z - 3) inside++; }
      if (inside === 3) c0++; else keep.push(I[t], I[t + 1], I[t + 2]); }
    if (c0) { g.setIndex(keep); cut += c0; meshes++; } });
  console.log('[rata] raidealueelta poistettu kolmioita', cut, 'kerroksista', meshes);
}

// laiturikatos (Porin aseman välilaiturin lasikatos) LoD2-laatikon 2298 jalanjäljelle; laatikko ja porraskatos 2299 poistetaan
const HIDE_FP = (RATA.hideB || []).map(i => { const p = CITY.b[i].p, P = []; for (let k = 0; k < p.length; k += 2) P.push([p[k] / 10, p[k + 1] / 10]); return P; });
function cutBakedBlocks() {
  for (const e of window.__stream || []) { if (!e.gr || e.gr.userData.rataCut) continue; e.gr.userData.rataCut = true; let n = 0;
    const ox = e.gr.position.x, oz = e.gr.position.z;
    e.gr.traverse(m => { if (!m.isMesh) return; const g = m.geometry, P = g.attributes.position; m.updateMatrixWorld(true); const M4 = m.matrixWorld, v = new THREE.Vector3();
      const idx = g.index ? Array.from(g.index.array) : [...Array(P.count).keys()]; const keep = []; let cut = 0;
      for (let t = 0; t < idx.length; t += 3) { let cx = 0, cy = 0; for (let k = 0; k < 3; k++) { v.fromBufferAttribute(P, idx[t + k]).applyMatrix4(M4); cx += v.x / 3; cy += -v.z / 3; }
        if (HIDE_FP.some(F => inPoly(cx, cy, F) || F.some(([x, y]) => Math.hypot(x - cx, y - cy) < 0.6))) cut++; else keep.push(idx[t], idx[t + 1], idx[t + 2]); }
      if (cut) { g.setIndex(keep); n += cut; } });
    if (n) console.log('[rata] laiturin LoD2-laatikot poistettu leivotusta korttelista', e.name, n); }
}
function buildCanopy(root, plats) {
  const F = HIDE_FP[0]; if (!F) return;
  // suorakaide: pisin sivu = pituussuunta
  let best = 0, ax = 0, ay = 0; for (let i = 0; i < F.length; i++) { const a = F[i], b = F[(i + 1) % F.length], L = Math.hypot(b[0] - a[0], b[1] - a[1]); if (L > best) { best = L; ax = (b[0] - a[0]) / L; ay = (b[1] - a[1]) / L; } }
  const cx = F.reduce((s, p) => s + p[0], 0) / F.length, cy = F.reduce((s, p) => s + p[1], 0) / F.length;
  let l0 = 1e9, l1 = -1e9, w0 = 1e9, w1 = -1e9; for (const [x, y] of F) { const u = (x - cx) * ax + (y - cy) * ay, w = -(x - cx) * ay + (y - cy) * ax; l0 = Math.min(l0, u); l1 = Math.max(l1, u); w0 = Math.min(w0, w); w1 = Math.max(w1, w); }
  const pl = plats.find(p => inPoly(cx, cy, p.poly)) || plats[0], z = pl.z, H = 3.4, len = l1 - l0, wid = Math.min(w1 - w0, 6.5);
  const o = new THREE.Group(); o.position.set(...W(cx + ax * (l0 + l1) / 2, cy + ay * (l0 + l1) / 2, z)); o.rotation.y = Math.atan2(ax, ay) * -1 + Math.PI; root.add(o);
  // paikallinen z = pituus, x = leveys
  const roof = new THREE.Mesh(new THREE.BoxGeometry(wid, 0.05, len), M.glass); roof.position.y = H + 0.15; o.add(roof);
  for (const sx of [-1, 1]) { const e = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.3, len), M.frame); e.position.set(sx * wid / 2, H + 0.05, 0); o.add(e); }
  const spine = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.45, len), M.frame); spine.position.y = H; o.add(spine);
  const n = Math.max(2, Math.round(len / 8));
  for (let k = 0; k <= n; k++) { const zz = -len / 2 + k * len / n;
    const c = new THREE.Mesh(new THREE.CylinderGeometry(0.11, 0.11, H, 10), M.frame); c.position.set(0, H / 2, zz); o.add(c);
    const r = new THREE.Mesh(new THREE.BoxGeometry(wid, 0.12, 0.12), M.frame); r.position.set(0, H + 0.08, zz); o.add(r);
    if (k % 2 === 0 && k < n) { const b = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.45, 1.8), M.frame); b.position.set(0, 0.45, zz + len / n / 2); o.add(b); }   // penkki
  }
  // aikataulunäyttö
  const sg = canvasTex(256, 64, (g, w, h) => { g.fillStyle = '#10161d'; g.fillRect(0, 0, w, h); g.fillStyle = '#ffd24a'; g.font = 'bold 26px sans-serif'; g.textBaseline = 'middle'; g.fillText('IC  Tampere', 10, h / 2); g.fillStyle = '#fff'; g.fillText('1', w - 30, h / 2); });
  for (const s of [-1, 1]) { const d = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.42, 0.08), [M.frame, M.frame, M.frame, M.frame, new THREE.MeshBasicMaterial({ map: sg }), new THREE.MeshBasicMaterial({ map: sg })]); d.position.set(0, H - 0.5, s * len * 0.3); o.add(d); }
  o.traverse(c => c.userData.noT = true);
}

// pysäköidyt "autot" raiteilla (ilmakuvan tunnistus luuli vaunuja autoiksi) pois
function clearCars() {
  const P = window.__parked; if (!P || !P.length) return false; let n = 0; const z = new THREE.Matrix4().makeScale(0, 0, 0);
  for (const c of P) { if (c.gone) continue; for (const tr of tracks) { const q = nearestOn(tr, c.x, c.y); if (q.d < 3.2) { c.gone = true; c.im.setMatrixAt(c.j, z); c.im.instanceMatrix.needsUpdate = true; n++; break; } } }
  console.log('[rata] raiteilta poistettu pysäköityjä autoja', n); return true;
}

if (typeof window !== 'undefined' && !window.__rataNoAuto) {
  const odota = () => { const G = window.__game; if (G && G.scene) { luoRata({ scene: G.scene, TZg: G.TZg || G.TZs, G });
      const tick = () => { const c = window.__rataPin ? { position: { x: window.__rataPin[0], z: -window.__rataPin[1] } } : G.camera; if (c && window.__rata) window.__rata.upd(c.position.x, -c.position.z); };
      setInterval(tick, 400); tick(); window.__rataCam = (x, y) => { window.__rataPin = [x, y]; window.__rata.upd(x, y); };
      const cc = () => { if (!clearCars()) setTimeout(cc, 2000); }; setTimeout(cc, 3000);
      setTimeout(() => clearRoadsOnTracks(G.scene, window.__rata.root), 4000);
      setInterval(cutBakedBlocks, 1500);
      return; } setTimeout(odota, 500); };
  odota();
}
export { luoRata, tracks, at, nearestOn };
