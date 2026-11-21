// moduulit/etelaranta.js – siirretty pääskriptistä (src/js/050_etelaranta.js) omaksi moduulikseen 21.11.2026.
// Pääskriptin muuttujat tulevat oliossa _P (getterit pitävät ne ajan tasalla); kirjastot ja data tuodaan suoraan.
// Kutsu ja _P:n sisältö: src/js/050_etelaranta.js. Uusi riippuvuus pääskriptiin → lisää se sinne _P-olioon.
import * as THREE from '../three.module.min.js';
import RIV from '../river.js';
import TER from '../terrain.js';

// ---------- Eteläranta (renewed quay): lower walk by the water, seating steps with hedges, railing, pontoons, pavilions ----------
export default function kaynnista(_P) {
{
  // 20.11.2026 (omistaja: "maapinnat alueelle, nyt ilmakuvaa, joka tulisi peittää autenttisemmalla"; kuvat Etelärannalta): procedural paving, 4 m x 4 m per
  // repeat, rows along the quay. 'graniitti' = the light grey granite slabs of the promenade (0.6 m rows, 0.6-1.4 m long, grains), 'betoni' = the big
  // concrete slabs of the lower walk (1.5 m x 2-3 m, smooth). Mean brightness ~1, so the surfaces keep their colour and only gain joints and texture.
  const laattaTex = (kind, seed) => { const N = 1024, PX = N / 4, c = document.createElement('canvas'); c.width = c.height = N; const g = c.getContext('2d');
    let sd = seed; const rnd = () => (sd = (sd * 16807) % 2147483647) / 2147483647;
    const gr = kind === 'graniitti', rows = gr ? [0.6, 0.6, 0.4, 0.6, 0.6, 0.6, 0.6] : [1.5, 1.0, 1.5], jw = gr ? 2 : 3;
    const im = g.createImageData(N, N), D = im.data;
    for (let i = 0; i < N * N; i++) { const n = gr ? (rnd() - 0.5) * 34 + (rnd() < 0.05 ? -40 : 0) + (rnd() < 0.03 ? 22 : 0) : (rnd() - 0.5) * 10; const v = 240 + n; D[i * 4] = v; D[i * 4 + 1] = v; D[i * 4 + 2] = v - 2; D[i * 4 + 3] = 255; }
    g.putImageData(im, 0, 0);
    let y = 0; for (const h of rows) { let x = rnd() * 4, done = 0; const y0 = Math.round(y * PX), y1 = Math.round((y + h) * PX);
      while (done < 4 - 0.01) { const L = Math.min(gr ? 0.6 + Math.floor(rnd() * 5) * 0.2 : 2 + Math.floor(rnd() * 3) * 0.5, 4 - done), sh = (rnd() - 0.5) * (gr ? 26 : 16), wt = rnd() < 0.25 ? (rnd() - 0.5) * 18 : 0;
        for (const ox of [0, -4, 4]) { const x0 = Math.round((x + ox) * PX), x1 = Math.round((x + ox + L) * PX);
          g.fillStyle = sh > 0 ? `rgba(255,255,255,${sh / 255})` : `rgba(0,0,0,${-sh / 255})`; g.fillRect(x0, y0, x1 - x0, y1 - y0);
          if (wt) { g.fillStyle = `rgba(${wt > 0 ? '120,110,90' : '60,60,70'},${Math.abs(wt) / 255})`; g.beginPath(); g.ellipse(x0 + (x1 - x0) * rnd(), y0 + (y1 - y0) * rnd(), 20 + 60 * rnd(), 15 + 40 * rnd(), 0, 0, 7); g.fill(); }
          g.fillStyle = 'rgba(70,68,64,0.75)'; g.fillRect(x0, y0, jw, y1 - y0); }
        x += L; done += L; }
      g.fillStyle = 'rgba(70,68,64,0.75)'; g.fillRect(0, y0, N, jw); y += h; }
    const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = _P.renderer.capabilities.getMaxAnisotropy(); return t; };
  const LAATTA = { graniitti: laattaTex('graniitti', 4711), betoni: laattaTex('betoni', 913), kulma: Math.atan2(477.35 - 515.8, 195 + 143) };   // rows along the quay line
  window.__laatta = LAATTA;
  const Q = []; for (let i = 0; i < RIV.quay.length; i += 2) Q.push([RIV.quay[i], RIV.quay[i + 1]]);
  const N = Q.map((p, i) => { const a = Q[Math.max(0, i - 1)], b = Q[Math.min(Q.length - 1, i + 1)], dx = b[0] - a[0], dy = b[1] - a[1], L = Math.hypot(dx, dy); return [-dy / L, dx / L]; });
  if (_P.inRiver(Q[2][0] + N[2][0] * 3, Q[2][1] + N[2][1] * 3)) for (const n of N) { n[0] = -n[0]; n[1] = -n[1]; }   // N points inland
  const at = (i, o) => [Q[i][0] + N[i][0] * o, Q[i][1] + N[i][1] * o];
  // 20.11.2026 (omistaja: "siistitään"): rebuilt at absolute heights (noT) on the true ground. The quay line is a saw-tooth - long sections with the
  // terraces and short jogs of 3-9 m back towards the land; the old build offset every vertex by an averaged normal, so at the jogs the steps folded
  // over each other, and it stood on the smoothed field, which lies 1-1.5 m off the real ground by the river, so the photo ground showed through it.
  // Now each run of sections is built on its own with mitred offsets and closed at both ends with its cross-section (the end of a tooth is a wall into
  // the water); the lower walk is 1.05 m above the water, four seating steps rise from it to the street, whose level is the true ground 11 m inland,
  // and the top paving runs 18 m inland where the photo ground is cut out (quayCut).
  const P = [], C = [], push = (a, b, c, col) => { for (const v of [a, b, c]) { P.push(v[0], v[2], -v[1]); C.push(col[0], col[1], col[2]); } };
  const quad = (a, b, c, d, col) => { push(a, b, c, col); push(a, c, d, col); };
  const gran = [0.66, 0.65, 0.62], pave = [0.74, 0.73, 0.70], riser = [0.55, 0.54, 0.52], wallc = [0.45, 0.44, 0.42];
  const ZW = _P.QUAY_WALK, ZB = TER.wl - 0.6;                       // lower walk, foot of the wall in the water
  const sg = N[0][0] * -(Q[1][1] - Q[0][1]) + N[0][1] * (Q[1][0] - Q[0][0]) > 0 ? 1 : -1;
  const segN = i => { const dx = Q[i + 1][0] - Q[i][0], dy = Q[i + 1][1] - Q[i][1], L = Math.hypot(dx, dy); return [sg * -dy / L, sg * dx / L]; };
  const runs = []; { let cur = [0], last = 0;
    for (let i = 0; i + 1 < Q.length; i++) { const dx = Q[i + 1][0] - Q[i][0], dy = Q[i + 1][1] - Q[i][1], L = Math.hypot(dx, dy), n = segN(last);
      const jog = cur.length > 1 && L < 10 && Math.abs(dx * n[0] + dy * n[1]) / L > 0.8;
      if (jog) { runs.push(cur); cur = [i + 1]; } else { cur.push(i + 1); last = i; } }
    if (cur.length > 1) runs.push(cur); }
  const street = (x, y) => Math.max(ZW + 1.2, _P.TZg(x, y));
  const RUN = runs.map(r => { const n = r.slice(0, -1).map(i => segN(i)), M = r.map((_, k) => { const a = n[Math.max(0, k - 1)], b = n[Math.min(n.length - 1, k)], d = 1 + a[0] * b[0] + a[1] * b[1]; return [(a[0] + b[0]) / d, (a[1] + b[1]) / d]; });
    const cum = [0]; for (let k = 0; k + 1 < r.length; k++) cum.push(cum[k] + Math.hypot(Q[r[k + 1]][0] - Q[r[k]][0], Q[r[k + 1]][1] - Q[r[k]][1]));
    const pt = (k, o) => [Q[r[k]][0] + M[k][0] * o, Q[r[k]][1] + M[k][1] * o];
    const at2 = (d, o) => { let k = 0; while (k < r.length - 2 && d > cum[k + 1]) k++; const f = Math.max(0, Math.min(1, (d - cum[k]) / (cum[k + 1] - cum[k]))), a = pt(k, o), b = pt(k + 1, o);
      return [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, Math.atan2(Q[r[k + 1]][1] - Q[r[k]][1], Q[r[k + 1]][0] - Q[r[k]][0])]; };
    // cross-section of column k: [offset, height, colour of the piece that starts here]
    const prof = k => { const s = pt(k, 11), zs = street(s[0], s[1]), e = pt(k, 18), ze = Math.max(zs, _P.TZg(e[0], e[1]) + 0.03), st = i => ZW + (zs - ZW) * i / 4;
      return [[0, ZW, pave], [4.5, ZW, riser], [4.5, st(1), gran], [5.3, st(1), riser], [5.3, st(2), gran], [6.1, st(2), riser], [6.1, st(3), gran], [6.9, st(3), riser], [6.9, zs, gran], [8.2, zs, pave], [18, ze, null]]; };
    return { r, n, M, pt, at: at2, prof, len: cum[cum.length - 1] }; });
  RUN.forEach((R, ri) => {
    const PR = R.r.map((_, k) => R.prof(k)), v = (k, o, z) => { const p = R.pt(k, o); return [p[0], p[1], z]; };
    for (let k = 0; k + 1 < R.r.length; k++) {
      const A = PR[k], B = PR[k + 1];
      for (let j = 0; j + 1 < A.length; j++) quad(v(k, A[j][0], A[j][1]), v(k + 1, B[j][0], B[j][1]), v(k + 1, B[j + 1][0], B[j + 1][1]), v(k, A[j + 1][0], A[j + 1][1]), A[j][2]);
      quad(v(k, 0, ZB), v(k + 1, 0, ZB), v(k + 1, 0, ZW), v(k, 0, ZW), wallc); }
    // end caps: down into the water as far as the tooth sticks out past the next run (the jog), elsewhere just below the walk
    for (const [k, nb] of [[0, RUN[ri - 1]], [R.r.length - 1, RUN[ri + 1]]]) { const q = Q[R.r[k]], A = PR[k];
      let jl = 0; if (nb) { const o = nb.r[k === 0 ? nb.r.length - 1 : 0], m = R.n[k === 0 ? 0 : R.n.length - 1]; jl = Math.abs((Q[o][0] - q[0]) * m[0] + (Q[o][1] - q[1]) * m[1]); }
      for (let j = 0; j + 1 < A.length; j++) { const [o0, z0] = A[j], [o1, z1] = A[j + 1]; if (o1 <= o0 + 0.01) continue;
        const b0 = o0 < jl + 0.5 ? ZB : ZW - 0.3, b1 = o1 < jl + 0.5 ? ZB : ZW - 0.3;
        quad(v(k, o0, b0), v(k, o1, b1), v(k, o1, z1), v(k, o0, z0), j === 0 ? wallc : riser); } }
  });
  // 20.11.2026 (omistaja: "tuossa pitäisi olla alikulku sillan ali toiselle puolelle"): the lower walk goes on east from the end of the quay under
  // Porinsilta's south end (deck underside about 0.3 m, so 2.8 m headroom) between the bridge's river pier and the abutment, and climbs at 1:9 to the
  // riverside path east of the bridge. A retaining wall holds the land on the south side, a wall with a railing drops into the water on the north side;
  // the photo ground is cut out over the corridor (quayCut) and a capping strip covers the cut south of the wall.
  const UPS = { x0: 193, x1: 238, x2: 260, x3: 266.5, yN: 475.3, yS: 471.7, cap: 462.5, tun: [197, 216] };   // tun: the arched tunnel under the deck (x)
  const inTun = x => x > UPS.tun[0] - 0.2 && x < UPS.tun[1] + 0.2;
  const upEnd = _P.TZg(UPS.x2 + 1.5, (UPS.yN + UPS.yS) / 2) + 0.05, upZ = x => x <= UPS.x1 ? ZW : x >= UPS.x2 ? Math.max(ZW, upEnd) : ZW + (Math.max(ZW, upEnd) - ZW) * (x - UPS.x1) / (UPS.x2 - UPS.x1);
  if (_P.QUAY_MODEL) { const topS = (x, y) => Math.max(_P.TZg(x, y) + 0.05, upZ(x) + 0.25);
    for (let x = UPS.x0; x < UPS.x3 - 0.01; x += 1.5) { const x2 = Math.min(UPS.x3, x + 1.5), za = upZ(x), zb = upZ(x2);
      quad([x, UPS.yN, TER.wl - 0.04], [x2, UPS.yN, TER.wl - 0.04], [x2, 478.5, TER.wl - 0.04], [x, 478.5, TER.wl - 0.04], [0.2, 0.25, 0.28]);   // water-coloured floor out to the river surface (the ground is cut there)
      quad([x, UPS.yS, za], [x2, UPS.yS, zb], [x2, UPS.yN, zb], [x, UPS.yN, za], pave);                                                            // walk
      quad([x, UPS.yN, ZB], [x2, UPS.yN, ZB], [x2, UPS.yN, zb], [x, UPS.yN, za], wallc);                                                           // river wall
      quad([x, UPS.yS, za], [x2, UPS.yS, zb], [x2, UPS.yS, topS(x2, UPS.yS)], [x, UPS.yS, topS(x, UPS.yS)], riser);                                // retaining wall
      quad([x, UPS.yS, topS(x, UPS.yS)], [x2, UPS.yS, topS(x2, UPS.yS)], [x2, UPS.cap, topS(x2, UPS.cap)], [x, UPS.cap, topS(x, UPS.cap)], pave); }     // capping strip
    for (let x = UPS.x0; x < UPS.x3 - 0.01; x += 1.5) { const x2 = Math.min(UPS.x3, x + 1.5); quad([x, UPS.cap, ZW - 0.5], [x2, UPS.cap, ZW - 0.5], [x2, UPS.cap, topS(x2, UPS.cap)], [x, UPS.cap, topS(x, UPS.cap)], riser); }   // skirt: closes the void under the capping strip
    for (const x of [UPS.x0, UPS.x3]) quad([x, UPS.yS, x === UPS.x0 ? ZW : upZ(x)], [x, UPS.cap, x === UPS.x0 ? ZW : upZ(x)], [x, UPS.cap, topS(x, UPS.cap)], [x, UPS.yS, topS(x, UPS.yS)], riser);
    const rp = []; for (let x = UPS.x0; x < UPS.x2; x += 1.5) { const x2 = Math.min(UPS.x2, x + 1.5); if (inTun(x) || inTun(x2)) continue; for (const h of [1.05, 0.55]) rp.push(x, upZ(x) + h, -UPS.yN + 0.25, x2, upZ(x2) + h, -UPS.yN + 0.25); }
    const rg = new THREE.BufferGeometry(); rg.setAttribute('position', new THREE.Float32BufferAttribute(rp, 3)); _P.scene.add(_P.noT(new THREE.LineSegments(rg, new THREE.LineBasicMaterial({ color: 0x222528 }))));
    const upPosts = []; for (let x = UPS.x0 + 0.5; x < UPS.x2; x += 2.2) if (!inTun(x)) upPosts.push(x);
    const um = new THREE.InstancedMesh(new THREE.BoxGeometry(0.07, 1.05, 0.07), new THREE.MeshLambertMaterial({ color: 0x2a2d30 }), upPosts.length), m4 = new THREE.Matrix4();
    upPosts.forEach((x, k) => um.setMatrixAt(k, m4.makeTranslation(x, upZ(x) + 0.52, -(UPS.yN - 0.25)))); _P.scene.add(_P.noT(um)); }
  // 20.11.2026 (omistaja: "alikulku on kaarimallinen, pellillä päällystetty kulku, leveys noin 3 m"): under the deck the corridor is a corrugated-steel
  // arch 3.0 m wide (vertical sides to 0.9 m, then a half-ellipse), concrete portals at both ends, a concrete cover over it and the abutment face to the
  // river. The crown follows the bridge: at most 2.7 m, at least 0.45 m below psilDeck over the tunnel (the deck slab) - logged as window.__alikulku.
  if (_P.QUAY_MODEL) { const [X0, X1] = UPS.tun, yc = (UPS.yN + UPS.yS) / 2, HW = 1.5, HS = 0.9, TH = 0.35, ux = Math.sin(_P.PSIL.head), uy = Math.cos(_P.PSIL.head);
    let room = 9; for (let x = X0; x <= X1; x += 0.5) for (const y of [yc - HW - TH, yc + HW + TH]) { const t = (x - _P.PSIL.x) * ux + (y - _P.PSIL.y) * uy, sp = (x - _P.PSIL.x) * uy - (y - _P.PSIL.y) * ux;
      if (Math.abs(sp) < _P.PSIL.half + 0.5) room = Math.min(room, _P.psilDeck(t) - 0.45 - ZW); }
    const HC = Math.max(2.3, Math.min(2.7, room - TH)), RY = HC - HS;
    const prof = [[-HW, 0], [-HW, HS]]; for (let i = 1; i < 24; i++) { const a = Math.PI * (1 - i / 24); prof.push([HW * Math.cos(a), HS + RY * Math.sin(a)]); } prof.push([HW, HS], [HW, 0]);
    // corrugated sheet: one rib per 0.15 m around the arch (texture u along the tunnel), galvanised grey with a little patina
    const cc = document.createElement('canvas'); cc.width = 32; cc.height = 64; const cx = cc.getContext('2d');
    for (let i = 0; i < 32; i++) { const l = Math.round(150 + 55 * Math.sin(i / 32 * Math.PI * 2)); cx.fillStyle = `rgb(${l - 4},${l},${l + 2})`; cx.fillRect(i, 0, 1, 64); }
    for (let k = 0; k < 40; k++) { cx.fillStyle = `rgba(${90 + Math.random() * 40},${80 + Math.random() * 30},60,${0.05 + Math.random() * 0.08})`; cx.fillRect(Math.random() * 32, Math.random() * 64, 1 + Math.random() * 6, 2 + Math.random() * 14); }
    const ct = new THREE.CanvasTexture(cc); ct.wrapS = ct.wrapT = THREE.RepeatWrapping; ct.colorSpace = THREE.SRGBColorSpace; ct.anisotropy = 8;
    const AP = [], AU = [], AI = []; let arc = 0;
    prof.forEach((q, i) => { if (i) arc += Math.hypot(q[0] - prof[i - 1][0], q[1] - prof[i - 1][1]);
      for (const x of [X0, X1]) { AP.push(x, ZW + q[1], -(yc + q[0])); AU.push((x - X0) / 0.15, arc / 2.0); } });
    for (let i = 0; i + 1 < prof.length; i++) { const a = i * 2, b = a + 2; AI.push(a, a + 1, b + 1, a, b + 1, b); }
    const ag = new THREE.BufferGeometry(); ag.setAttribute('position', new THREE.Float32BufferAttribute(AP, 3)); ag.setAttribute('uv', new THREE.Float32BufferAttribute(AU, 2)); ag.setIndex(AI); ag.computeVertexNormals();
    _P.scene.add(_P.noT(new THREE.Mesh(ag, new THREE.MeshLambertMaterial({ map: ct, side: THREE.DoubleSide }))));
    const conc = new THREE.MeshLambertMaterial({ color: 0x9c9a95 });
    // portals: a concrete frame around the arch opening at each end
    const sh = new THREE.Shape([[-HW - TH, 0], ...prof, [HW + TH, 0], [HW + TH, HC + TH], [-HW - TH, HC + TH]].map(q => new THREE.Vector2(q[0], q[1])));   // a U around the opening (no hole)
    const pg = new THREE.ExtrudeGeometry(sh, { depth: TH, bevelEnabled: false, curveSegments: 4 });
    for (const [x, d] of [[X0 - TH, 0], [X1, 0]]) { const m = new THREE.Mesh(pg, conc); m.rotation.y = Math.PI / 2; m.position.set(x + d, ZW, -yc); _P.scene.add(_P.noT(m)); }
    // cover slab over the arch (between the portals) and the abutment face down to the river on the north side
    { const cv = new THREE.Mesh(new THREE.BoxGeometry(X1 - X0 + 2 * TH, TH, 2 * (HW + TH)), conc); cv.position.set((X0 + X1) / 2, ZW + HC + TH / 2, -yc); _P.scene.add(_P.noT(cv));
      const nf = new THREE.Mesh(new THREE.BoxGeometry(X1 - X0 + 2 * TH, HC + TH - (ZB - ZW), 0.3), conc); nf.position.set((X0 + X1) / 2, (ZB + ZW + HC + TH) / 2, -(yc + HW + TH + 0.15)); _P.scene.add(_P.noT(nf)); }
    window.__alikulku = { x: [X0, X1], leveys: 2 * HW, harja: +HC.toFixed(2), tilaKanteen: +room.toFixed(2) };
    console.log('[alikulku] kaari', window.__alikulku); }
  // the surface height for walkers and the player (groundTop): the photo ground lies up to 1 m off the walk and the steps
  if (_P.QUAY_MODEL) { const SEG = []; for (const R of RUN) { const PR = R.r.map((_, k) => R.prof(k)); for (let k = 0; k + 1 < R.r.length; k++) { const a = Q[R.r[k]], b = Q[R.r[k + 1]], L = Math.hypot(b[0] - a[0], b[1] - a[1]); SEG.push({ a, ux: (b[0] - a[0]) / L, uy: (b[1] - a[1]) / L, L, n: R.n[k], A: PR[k], B: PR[k + 1] }); } }
    const zAt = (A, o) => { for (let j = A.length - 2; j >= 0; j--) if (o >= A[j][0]) { const [o0, z0] = A[j], [o1, z1] = A[j + 1]; return o1 > o0 + 0.01 ? z0 + (z1 - z0) * Math.min(1, (o - o0) / (o1 - o0)) : z1; } return A[0][1]; };
    window.__quayZ = (x, y, maxO = 16) => { if (x >= UPS.x0 && x <= UPS.x3 && y >= UPS.yS && y <= UPS.yN + 0.3) return upZ(x);
      if (x < -150 || x > 200 || y < 465 || y > 540) return null;
      for (const s of SEG) { const dx = x - s.a[0], dy = y - s.a[1], t = dx * s.ux + dy * s.uy, o = dx * s.n[0] + dy * s.n[1]; if (t < 0 || t > s.L || o < -0.3 || o > maxO) continue;
        const f = t / s.L; return zAt(s.A, o) * (1 - f) + zAt(s.B, o) * f; } return null; }; }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3)); g.setAttribute('color', new THREE.Float32BufferAttribute(C, 3)); g.computeVertexNormals();
  // the quay's surfaces in world space: concrete slabs on the lower walk (below ZW + 0.12), granite slabs above, concrete grain on the vertical faces
  const quayMat = new THREE.MeshLambertMaterial({ vertexColors: true, side: THREE.DoubleSide });
  quayMat.onBeforeCompile = sh => { Object.assign(sh.uniforms, { tG: { value: LAATTA.graniitti }, tB: { value: LAATTA.betoni }, uZW: { value: ZW }, uK: { value: LAATTA.kulma } });
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 vRw; varying vec3 vWn;').replace('#include <project_vertex>', '#include <project_vertex>\nvRw = (modelMatrix * vec4(transformed, 1.0)).xyz; vWn = normalize(mat3(modelMatrix) * objectNormal);');
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\nvarying vec3 vRw; varying vec3 vWn; uniform sampler2D tG, tB; uniform float uZW, uK;').replace('#include <map_fragment>', `
      vec2 wp = vec2(vRw.x, -vRw.z), q = vec2(cos(uK) * wp.x + sin(uK) * wp.y, -sin(uK) * wp.x + cos(uK) * wp.y);
      vec3 tx = abs(vWn.y) > 0.6 ? (vRw.y < uZW + 0.12 ? texture2D(tB, q * 0.25).rgb : texture2D(tG, q * 0.25).rgb)
                                 : texture2D(tB, vec2(wp.x * vWn.z + wp.y * vWn.x, vRw.y) * 0.25 + 0.37).rgb;
      diffuseColor.rgb *= tx * 1.12;`); };
  if (_P.QUAY_MODEL) _P.scene.add(_P.noT(new THREE.Mesh(g, quayMat)));
  // walk along the line: railing posts, hedges on the steps, lamps on the street edge
  const segs = []; let tot = 0; for (let i = 0; i + 1 < Q.length; i++) { const L = Math.hypot(Q[i + 1][0] - Q[i][0], Q[i + 1][1] - Q[i][1]); segs.push([tot, L]); tot += L; }
  const along = (d, o) => { let i = 0; while (i < segs.length - 1 && d > segs[i][0] + segs[i][1]) i++; const f = Math.min(1, Math.max(0, (d - segs[i][0]) / segs[i][1]));
    const a = at(i, o), b = at(i + 1, o); return [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, Math.atan2(Q[i + 1][1] - Q[i][1], Q[i + 1][0] - Q[i][0])]; };
  const nearT = p => Math.abs(p[0] + 149) < 9;
  const dark = new THREE.MeshLambertMaterial({ color: 0x2a2d30 }), hedge = new THREE.MeshLambertMaterial({ color: 0x3f6b2f }), M4 = new THREE.Matrix4(), Q4 = new THREE.Quaternion(), V3 = new THREE.Vector3(), S3 = new THREE.Vector3(1, 1, 1), UP = new THREE.Vector3(0, 1, 0);
  if (false) for (const R of RUN) for (let d = 5; d + 22 < R.len - 4; d += 40) {     /* hedges per run on the second step - 20.11.2026 omistaja: "vihertävät osat voidaan rannalta poistaa" */
    const a = R.at(d, 5.7), b = R.at(d + 22, 5.7); if (nearT(a) || nearT(b)) continue; const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2, L = Math.hypot(b[0] - a[0], b[1] - a[1]);
    const s = R.at(d + 11, 11), tz = ZW + (street(s[0], s[1]) - ZW) * 2 / 4;
    const hm = new THREE.Mesh(new THREE.BoxGeometry(L, 1.0, 1.5), hedge); hm.position.set(mx, tz + 0.5, -my); hm.rotation.y = -Math.atan2(b[1] - a[1], b[0] - a[0]); _P.scene.add(_P.noT(hm));
    const bm = new THREE.Mesh(new THREE.BoxGeometry(L + 0.2, 0.5, 1.7), new THREE.MeshLambertMaterial({ color: 0x5c5a56 })); bm.position.set(mx, tz + 0.1, -my); bm.rotation.y = hm.rotation.y; _P.scene.add(_P.noT(bm)); }
  // 20.11.2026 (omistaja, kuvat Etelärannalta: "tehdään"): street furniture as in the photos - the lower walk's edge is black posts with a sagging chain
  // (not a railing), a red pole with a lifebuoy now and then, on the promenade a band of grey setts along the top of the steps, two-armed dark lamps
  // and pairs of grey metal benches facing the river.
  const topZ = (R, d, o) => { const s = R.at(d, 11), zs = _P.QUAY_MODEL ? street(s[0], s[1]) : _P.TZs(s[0], s[1]), e = R.at(d, 18), ze = Math.max(zs, _P.TZg(e[0], e[1]) + 0.03); return zs + (ze - zs) * Math.max(0, o - 8.2) / 9.8; };
  const inst = (geo, mat, list) => { if (!list.length || !_P.QUAY_MODEL) return; const im = new THREE.InstancedMesh(geo, mat, list.length); list.forEach((m, k) => im.setMatrixAt(k, m)); _P.scene.add(_P.noT(im)); };
  const place = (x, z, y, yaw, lx = 0, lz = 0, ly = 0, rx = 0) => { const m = new THREE.Matrix4().compose(V3.set(x, z, -y), Q4.setFromAxisAngle(UP, yaw), S3);
    const l = new THREE.Matrix4().makeRotationX(rx).setPosition(lx, lz, ly); return m.multiply(l); };
  // edge posts and chains
  const posts = []; for (const R of RUN) for (let d = 0.6; d < R.len - 0.5; d += 2.4) { const p = R.at(d, 0.35); if (!nearT(p)) posts.push(p); }
  inst(new THREE.CylinderGeometry(0.045, 0.05, 0.9, 10), dark, posts.map(p => place(p[0], ZW + 0.45, p[1], 0)));
  inst(new THREE.SphereGeometry(0.06, 10, 6), dark, posts.map(p => place(p[0], ZW + 0.92, p[1], 0)));
  if (_P.QUAY_MODEL) { const cp = []; for (let i = 0; i + 1 < posts.length; i++) { const a = posts[i], b = posts[i + 1]; if (Math.hypot(b[0] - a[0], b[1] - a[1]) > 3.2) continue;
      for (let k = 0; k < 8; k++) { const f0 = k / 8, f1 = (k + 1) / 8, z = f => ZW + 0.8 - 0.22 * 4 * f * (1 - f); cp.push(a[0] + (b[0] - a[0]) * f0, z(f0), -(a[1] + (b[1] - a[1]) * f0), a[0] + (b[0] - a[0]) * f1, z(f1), -(a[1] + (b[1] - a[1]) * f1)); } }
    const cg = new THREE.BufferGeometry(); cg.setAttribute('position', new THREE.Float32BufferAttribute(cp, 3)); _P.scene.add(_P.noT(new THREE.LineSegments(cg, new THREE.LineBasicMaterial({ color: 0x1c1e20 })))); }
  // lifebuoys: red pole with an orange ring, about every 45 m on the edge
  const buoy = []; for (const R of RUN) for (let d = 12; d < R.len - 4; d += 45) { const p = R.at(d, 0.7); if (!nearT(p)) buoy.push(p); }
  inst(new THREE.CylinderGeometry(0.03, 0.03, 2.6, 6), new THREE.MeshLambertMaterial({ color: 0xc22a1e }), buoy.map(p => place(p[0], ZW + 1.3, p[1], 0)));
  inst(new THREE.TorusGeometry(0.3, 0.07, 8, 18), new THREE.MeshLambertMaterial({ color: 0xff6a1a }), buoy.map(p => place(p[0], ZW + 1.25, p[1], p[2], 0, 0, 0.06)));
  // the band of setts on the promenade (offset 8.2-9.6 m), lying on the top paving
  if (_P.QUAY_MODEL) { const N = 512, c = document.createElement('canvas'); c.width = c.height = N; const g2 = c.getContext('2d'); let sd = 77; const rnd = () => (sd = (sd * 16807) % 2147483647) / 2147483647;
    g2.fillStyle = '#5d5a55'; g2.fillRect(0, 0, N, N); const cs = N / 16;            // 2 m repeat, 16 rows of 0.125 m setts
    for (let r = 0; r < 16; r++) { let x = -rnd() * cs; while (x < N) { const w = cs * (0.8 + rnd() * 0.5), l = 150 + rnd() * 70, t = rnd() * 14;
        for (const ox of [0, N, -N]) { g2.fillStyle = `rgb(${l + t - 7},${l},${l + 4 - t})`; g2.beginPath(); g2.roundRect(x + ox + 2, r * cs + 2, w - 4, cs - 4, 5); g2.fill(); }
        x += w; } }
    const tx = new THREE.CanvasTexture(c); tx.wrapS = tx.wrapT = THREE.RepeatWrapping; tx.colorSpace = THREE.SRGBColorSpace; tx.anisotropy = _P.renderer.capabilities.getMaxAnisotropy();
    const ca = Math.cos(LAATTA.kulma), sa = Math.sin(LAATTA.kulma), SP = [], SU = [];
    for (const R of RUN) for (let d = 0; d < R.len - 0.01; d += 1.5) { const d2 = Math.min(R.len, d + 1.5);
      for (const [dd, oo] of [[d, 8.2], [d2, 9.6], [d2, 8.2], [d, 8.2], [d, 9.6], [d2, 9.6]]) { const p = R.at(dd, oo); SP.push(p[0], topZ(R, dd, oo) + 0.015, -p[1]); SU.push((ca * p[0] + sa * p[1]) / 2, (-sa * p[0] + ca * p[1]) / 2); } }
    const sg2 = new THREE.BufferGeometry(); sg2.setAttribute('position', new THREE.Float32BufferAttribute(SP, 3)); sg2.setAttribute('uv', new THREE.Float32BufferAttribute(SU, 2)); sg2.computeVertexNormals();
    _P.scene.add(_P.noT(new THREE.Mesh(sg2, new THREE.MeshLambertMaterial({ map: tx, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 })))); }
  // two-armed lamps on the promenade: a 6.5 m dark pole, two arms rising out along the quay, shallow dark heads with a lit underside
  const lampPost = new THREE.MeshLambertMaterial({ color: 0x23272b }), lampGlass = new THREE.MeshBasicMaterial({ color: 0xfff3d6 }), LP = [];
  for (const R of RUN) for (let d = Math.min(8, R.len / 2); d < R.len - 2; d += 22) { const p = R.at(d, 9.1); LP.push([p[0], topZ(R, d, 9.1), p[1], p[2]]); }
  inst(new THREE.CylinderGeometry(0.07, 0.11, 6.5, 10), lampPost, LP.map(([x, z, y, a]) => place(x, z + 3.25, y, a)));
  const arm = new THREE.CylinderGeometry(0.03, 0.035, 1.05, 6); arm.rotateZ(Math.PI / 2 - 0.22);
  inst(arm, lampPost, LP.flatMap(([x, z, y, a]) => [place(x, z + 6.35, y, a, -0.5), place(x, z + 6.35, y, a + Math.PI, -0.5)]));
  const head = new THREE.SphereGeometry(0.34, 14, 6, 0, Math.PI * 2, 0, Math.PI / 2.6), disc = new THREE.CircleGeometry(0.3, 14); disc.rotateX(Math.PI / 2);
  const hp = LP.flatMap(([x, z, y, a]) => [place(x, z + 6.4, y, a, -1.0), place(x, z + 6.4, y, a + Math.PI, -1.0)]);
  inst(head, lampPost, hp); inst(disc, lampGlass, hp.map(m => m.clone().multiply(new THREE.Matrix4().makeTranslation(0, 0.1, 0))));
  // benches: grey aluminium end frames (legs + armrest), dark slatted seat and a slightly reclined back; pairs between the lamps, facing the river
  const frameM = new THREE.MeshLambertMaterial({ color: 0x8e8f8d }), slatM = new THREE.MeshLambertMaterial({ color: 0x55585a }), BN = [];
  for (const R of RUN) for (let d = Math.min(8, R.len / 2) + 11; d < R.len - 3; d += 22) for (const dx of [-1.4, 1.4]) { const p = R.at(d + dx, 10.4); if (nearT(p)) continue; const q = R.at(d + dx, 11), vx = q[0] - p[0], vy = q[1] - p[1], a = p[2] + (vx * Math.sin(p[2]) - vy * Math.cos(p[2]) < 0 ? Math.PI : 0); BN.push([p[0], topZ(R, d + dx, 10.4), p[1], a]); }
  // local frame: x along the bench (1.8 m), y up, z towards the back (inland); the bench faces -z = the river
  const parts = [];
  for (const ex of [-0.87, 0.87]) {
    parts.push([0.06, 0.45, 0.06, ex, 0.225, -0.2, 0, frameM], [0.06, 0.66, 0.06, ex, 0.33, 0.24, 0, frameM],              // front and back legs
               [0.06, 0.06, 0.5, ex, 0.62, 0.0, 0, frameM], [0.06, 0.05, 0.5, ex, 0.04, 0.02, 0, frameM],                 // armrest, foot rail
               [0.06, 0.06, 0.5, ex, 0.41, 0.0, 0, frameM], [0.06, 0.55, 0.06, ex, 0.68, 0.3, 0.2, frameM]); }      // seat rail, back post
  for (let k = 0; k < 6; k++) parts.push([1.74, 0.03, 0.06, 0, 0.45, -0.19 + k * 0.08, 0, slatM]);                                     // seat slats
  for (let k = 0; k < 5; k++) parts.push([1.74, 0.06, 0.025, 0, 0.55 + k * 0.08, 0.27 + k * 0.016, 0.2, slatM]);                     // back slats
  for (const [w, h, dpt, lx, ly, lz, rx, mat] of parts) inst(new THREE.BoxGeometry(w, h, dpt), mat, BN.map(([x, z, y, a]) => place(x, z, y, a, lx, ly, lz, rx)));
  window.__etKalusteet = { tolpat: posts.length, poijut: buoy.length, valot: LP.length, penkit: BN.length };
  // pontoon jetties with moored boats
  const pont = new THREE.MeshLambertMaterial({ color: 0x9b9890 }), hullM = new THREE.MeshLambertMaterial({ color: 0xf2f2ee }), cabM = new THREE.MeshLambertMaterial({ color: 0x32404a });
  if (false) for (const f of [64, 159, 249]) {      /* 20.11.2026: replaced by the measured pontoon jetties in ranta/ranta.js */ const p = along(Math.min(tot - 15, f), 0), ang = p[2], nx = -Math.sin(ang), ny = Math.cos(ang);
    const sgn = _P.inRiver(p[0] + nx * 6, p[1] + ny * 6) ? 1 : -1, L = 24, cx = p[0] + nx * sgn * L / 2, cy = p[1] + ny * sgn * L / 2;
    const pm2 = new THREE.Mesh(new THREE.BoxGeometry(2.6, 0.45, L), pont); pm2.position.set(cx, _P.WREL(cx, cy) + 0.2, -cy); pm2.rotation.y = -ang; _P.scene.add(pm2);
    for (const k of [-1, 1]) for (const t of [0.35, 0.75]) { const bx = p[0] + nx * sgn * L * t + Math.cos(ang) * k * 3.4, by = p[1] + ny * sgn * L * t + Math.sin(ang) * k * 3.4;
      const hl = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.9, 7.5), hullM); hl.position.set(bx, _P.WREL(bx, by) + 0.35, -by); hl.rotation.y = -ang; _P.scene.add(hl);
      const cb = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.9, 2.6), cabM); cb.position.set(bx, _P.WREL(bx, by) + 1.2, -by); cb.rotation.y = -ang; _P.scene.add(cb); } }
  // Barco, the restaurant ship moored west of Taavi-silta: Blender model at the water level
  _P.loadModel('bl_barco', (root, K) => { const m = new THREE.MeshLambertMaterial({ vertexColors: true, side: THREE.DoubleSide });   /* owner 18.11: seen from above the deck and the inner bulwarks were culled (normals outward) - the water showed inside: a sunk ship */ root.traverse(q => { if (q.isMesh) q.material = m; });
    const g = new THREE.Group(); g.position.set(K.x, TER.wl, -K.y); g.add(root); _P.scene.add(_P.noT(g)); window.__barco = true; });
  // restaurant pavilion by the river west of Rantamakasiini (SV 2026, 18.11): a low white box with a band of dark windows and a thin grey roof.
  // (The second pavilion that stood further west was not there in Street View: an open lawn.)
  const pavW = new THREE.MeshLambertMaterial({ color: 0xeef0ee }), pavG = new THREE.MeshLambertMaterial({ color: 0x2f3a42 }), pavR = new THREE.MeshLambertMaterial({ color: 0x8c9196 });
  for (const [f, w, dpt] of [[315, 12, 6]]) { const p = along(Math.min(tot - 12, f), 17), ang = p[2], gr = new THREE.Group(); gr.position.set(p[0], 0, -p[1]); gr.rotation.y = -ang; _P.scene.add(gr);
    const body = new THREE.Mesh(new THREE.BoxGeometry(w, 3.0, dpt), pavW); body.position.y = 1.5; gr.add(body);
    for (const z of [-dpt / 2 - 0.03, dpt / 2 + 0.03]) { const gl = new THREE.Mesh(new THREE.BoxGeometry(w - 1.6, 1.5, 0.06), pavG); gl.position.set(0, 1.55, z); gr.add(gl); }
    const rf = new THREE.Mesh(new THREE.BoxGeometry(w + 0.6, 0.3, dpt + 0.6), pavR); rf.position.y = 3.15; gr.add(rf); }
}
}
