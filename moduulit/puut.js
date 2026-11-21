// moduulit/puut.js – siirretty pääskriptistä (src/js/070_puut.js) omaksi moduulikseen 21.11.2026.
// Pääskriptin muuttujat tulevat oliossa _P (getterit pitävät ne ajan tasalla); kirjastot ja data tuodaan suoraan.
// Kutsu ja _P:n sisältö: src/js/070_puut.js. Uusi riippuvuus pääskriptiin → lisää se sinne _P-olioon.
import * as THREE from '../three.module.min.js';
import CITY from '../city.js';
import RIV from '../river.js';

// ---------- trees ----------
// OpenStreetMap trees + trees found in the aerial photo (trees_extra.js: crown cover where OSM has none; parks, woods, railway verges, gardens).
// Leaf-card models near the helicopter, cheap crowns (icosahedron / cone) further out; the visible sets are refreshed as the helicopter moves.
export default function kaynnista(_P) {
{
  const NEAR = 320, FAR = 1500, LIST = [];   // leaf cards within 320 m: about 2700 trees at most (1.2 M triangles), the rest as cheap crowns
  let sd = 23; const r2 = () => (sd = (sd * 16807) % 2147483647) / 2147483647;
  const addTree = (x, y, k, wood) => { const sc = (wood ? 0.9 : 0.8) + r2() * 0.55, t = r2();
    LIST.push({ x, y, k, sc, sy: sc * (0.9 + r2() * 0.25), rot: r2() * 6.28, c: [0.84 + 0.16 * t, 0.88 + 0.12 * r2(), 0.8 + 0.16 * t], fc: 0.85 + r2() * 0.3 }); };
  for (let i = 0; i < CITY.t.length / 2; i++) { const v = r2(), tx = CITY.t[i * 2], ty = CITY.t[i * 2 + 1];
    if (v < 0.1 && _P.inCore(tx, ty)) continue;   // owner 18.11.2026: no spruces in the centre (they were random picks, not real spruces)
    addTree(tx, ty, v < 0.1 ? 2 : v < 0.38 ? 1 : 0, false); LIST[LIST.length - 1].i = i;
    if (Math.hypot(tx + 1942.5, ty - 191.85) < 4.5) LIST.pop(); }   // no tree in the mausoleum doorway (popped after the random draws, so the other trees keep theirs)
  for (const [tx, ty] of [[107.1, 99], [97.2, 101.1], [89.5, 102.8], [81.4, 104.5], [30.5, 116.8]]) { const i = LIST.findIndex(t => Math.hypot(t.x - tx, t.y - ty) < 0.6); if (i >= 0) LIST.splice(i, 1); }      // owner 20.11.2026: no trees (and so no ring benches) on Pohjoiskauppatori, the north edge of the square: "siellä ei ole penkkejä". Taken out after the random draws, so the other trees keep theirs
  LIST.push({ x: 93.3, y: -32.0, k: 0, sc: 1.12, sy: 1.2, rot: 2.1, c: [0.92, 0.94, 0.88], fc: 1 });      // owner 20.11.2026: one more street tree (with its ring bench) on Yrjönkatu between Itäpuisto and Nortamonkatu, in line with the others (2 m east of the centre line); fixed values, so the random draws of the other trees stay as they were
  // 20.11.2026 (omistaja: "puu pois"): no tree on a bridge deck or on Porinsilta's approaches (OSM / photo trees and the moved street trees landed there)
  const onBridgeT = t => { const ux = Math.sin(_P.PSIL.head), uy = Math.cos(_P.PSIL.head), dx = t.x - _P.PSIL.x, dy = t.y - _P.PSIL.y, a = dx * ux + dy * uy;
      if (Math.abs(dx * uy - dy * ux) < _P.PSIL.half + 2 && a > -50 && a < _P.PSIL.len + 20) return true;
      for (const b of RIV.br) { const P = b.p; for (let i = 0; i + 3 < P.length; i += 2) { const ax = P[i], ay = P[i + 1], ex = P[i + 2] - ax, ey = P[i + 3] - ay, L2 = ex * ex + ey * ey || 1, f = Math.max(0, Math.min(1, ((t.x - ax) * ex + (t.y - ay) * ey) / L2));
        if (Math.hypot(ax + ex * f - t.x, ay + ey * f - t.y) < b.w / 2 + 1.5) return true; } } return false; };
  const dropBridgeTrees = () => { for (let n = LIST.length - 1; n >= 0; n--) if (onBridgeT(LIST[n])) LIST.splice(n, 1); };
  dropBridgeTrees();
  window.__treeList = LIST;      // the ring benches (people on foot: places to sit) stand round these
  const m = new THREE.Matrix4(), q = new THREE.Quaternion(), s = new THREE.Vector3(), p = new THREE.Vector3(), c = new THREE.Color(), UPV = THREE.Object3D.DEFAULT_UP;
  // far crowns: deciduous = squashed icosahedron on a short trunk, spruce = two stacked cones (about 30 triangles each)
  const BG = (() => { const g = new THREE.IcosahedronGeometry(1, 0); g.scale(3.2, 3.4, 3.2); g.translate(0, 6.6, 0); const t = new THREE.CylinderGeometry(0.22, 0.3, 3.6, 5); t.translate(0, 1.8, 0);
    const cols = (geo, r, gg, b) => { const n = geo.attributes.position.count, a = new Float32Array(n * 3); for (let i = 0; i < n; i++) a.set([r, gg, b], i * 3); geo.setAttribute('color', new THREE.BufferAttribute(a, 3)); return geo; };
    const merge = (A, B) => { const g = new THREE.BufferGeometry(), pa = [], na = [], ca = []; for (const x of [A.toNonIndexed(), B.toNonIndexed()]) { pa.push(...x.attributes.position.array); na.push(...x.attributes.normal.array); ca.push(...x.attributes.color.array); }
      g.setAttribute('position', new THREE.Float32BufferAttribute(pa, 3)); g.setAttribute('normal', new THREE.Float32BufferAttribute(na, 3)); g.setAttribute('color', new THREE.Float32BufferAttribute(ca, 3)); return g; };
    const dec = merge(cols(g, 1, 1, 1), cols(t, 0.45, 0.36, 0.3));
    const c1 = new THREE.ConeGeometry(3.6, 8.5, 7); c1.translate(0, 6.2, 0); const c2 = new THREE.ConeGeometry(2.4, 6, 7); c2.translate(0, 10.8, 0);
    const spr = merge(cols(c1, 1, 1, 1), cols(c2, 1, 1, 1));
    return [dec, dec, spr]; })();
  const fm = new THREE.MeshLambertMaterial({ vertexColors: true, flatShading: true });
  const FARC = [[0.25, 0.4, 0.2], [0.23, 0.36, 0.24], [0.36, 0.3, 0.14]];      // HSL of the crowns in the photo: linden, birch (lighter), spruce (dark)
  let farMs = [], nearMs = null, cap = 0;
  const alloc = () => { if (LIST.length <= cap) return; cap = LIST.length;
    for (const x of farMs) { _P.scene.remove(x); x.dispose(); }
    farMs = BG.map(g => { const im = new THREE.InstancedMesh(g, fm, cap); im.count = 0; im.frustumCulled = false; _P.scene.add(im); return im; });
    if (nearMs) nearMs.forEach((im, k) => { const n2 = new THREE.InstancedMesh(im.geometry, im.material, cap); n2.count = 0; n2.frustumCulled = false; _P.scene.remove(im); _P.scene.add(n2); nearMs[k] = n2; }); };
  let last = { x: 1e9, y: 1e9 };
  _P.TREES.update = (x, y) => {
    if (Math.hypot(x - last.x, y - last.y) < 60) return; last = { x, y }; alloc();
    const nf = [0, 0, 0], nn = [0, 0, 0];
    for (const t of LIST) { const dx = t.x - x, dy = t.y - y; if (Math.abs(dx) > FAR || Math.abs(dy) > FAR) continue;
      const near = nearMs && dx * dx + dy * dy < NEAR * NEAR, im = near ? nearMs[t.k] : farMs[t.k], j = near ? nn[t.k]++ : nf[t.k]++;
      p.set(t.x, 0, -t.y); s.set(t.sc, t.sy, t.sc); q.setFromAxisAngle(UPV, t.rot); im.setMatrixAt(j, m.compose(p, q, s));
      if (near) c.setRGB(...t.c); else { const h = FARC[t.k]; c.setHSL(h[0] + (t.fc - 1) * 0.08, h[1], h[2] * t.fc); }
      im.setColorAt(j, c); }
    const fin = (arr, cnt) => arr.forEach((im, k) => { im.count = cnt[k]; im.instanceMatrix.needsUpdate = true; if (im.instanceColor) im.instanceColor.needsUpdate = true; });
    fin(farMs, nf); if (nearMs) fin(nearMs, nn);
  };
  // street trees that OSM puts on the carriageway: moved to the pavement edge (roads.js 'tmv': index, x dm, y dm; -32768 = dropped)
  _P.TREES.move = M => { const by = new Map(); for (let k = 0; k < M.length; k += 3) by.set(M[k], k);
    for (let n = LIST.length - 1; n >= 0; n--) { const t = LIST[n]; if (t.i === undefined || !by.has(t.i)) continue; const k = by.get(t.i);
      if (M[k + 1] === -32768) LIST.splice(n, 1); else { t.x = M[k + 1] / 10; t.y = M[k + 2] / 10; } }
    dropBridgeTrees();
    last = { x: 1e9, y: 1e9 }; _P.TREES.update(_P.S && _P.S.x !== undefined ? _P.S.x : 70, _P.S && _P.S.y !== undefined ? _P.S.y : 45); };
  _P.TREES.add = A => { for (let k = 0; k < A.length; k += 2) addTree(A[k] / 10, A[k + 1] / 10, 0, false); dropBridgeTrees(); last = { x: 1e9, y: 1e9 }; _P.TREES.update(_P.S.x, _P.S.y); };
  window.__treesAt = (x, y) => { last = { x: 1e9, y: 1e9 }; _P.TREES.update(x, y); };
  _P.TREES.update(70, 45);
  // trees_extra.js (aerial-photo guesses) removed 13.11.2026: wrong places; to be replaced by trees from MML laser scanning
  // leaf-card trees (blender/trees2.py: linden, birch, spruce; alpha-cut leaf atlas, bent normals, self-shadowing in vertex colours)
  _P.loadModel('trees', root => {
    const src = ['tree0', 'tree1', 'tree2'].map(k => root.getObjectByName(k)), map = src[0].material.map;
    if (map) { map.anisotropy = 8; }
    const tm = new THREE.MeshLambertMaterial({ map, vertexColors: true, alphaTest: 0.5, side: THREE.DoubleSide }); tm.color.setScalar(1.22);
    nearMs = src.map(o => { const im = new THREE.InstancedMesh(o.geometry, tm, Math.max(1, cap)); im.count = 0; im.frustumCulled = false; _P.scene.add(im); return im; });
    const l = last; last = { x: 1e9, y: 1e9 }; _P.TREES.update(l.x < 1e8 ? l.x : 70, l.x < 1e8 ? l.y : 45); window.__trees = true;
  });
}
}
