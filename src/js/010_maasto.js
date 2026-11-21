// ---------- terrain: true ground (river bed below the water) and a smoothed, river-filled field that lifts everything else ----------
const TDEC = b => { const s = atob(b), a = new Uint8Array(s.length); for (let i = 0; i < s.length; i++) a[i] = s.charCodeAt(i); return a; };
const THG = new Int16Array(TDEC(TER.hg).buffer), THS = new Int16Array(TDEC(TER.hs).buffer), TSKIP = TDEC(TER.skip);
function tBil(A, x, y) { const fx = Math.min(TER.nx - 1.001, Math.max(0, (x - TER.x0) / TER.g)), fy = Math.min(TER.ny - 1.001, Math.max(0, (y - TER.y0) / TER.g)), i = Math.floor(fx), j = Math.floor(fy), u = fx - i, v = fy - j, k = j * TER.nx + i;
  return ((A[k] * (1 - u) + A[k + 1] * u) * (1 - v) + (A[k + TER.nx] * (1 - u) + A[k + TER.nx + 1] * u) * v) / 10; }
const TZg = (x, y) => tBil(THG, x, y), TZs = (x, y) => tBil(THS, x, y);
// 20.11.2026 (omistaja: "sillat pitää tarkastaa ja ne alueet"): the laser elevation model has the bridge abutments and ramps in it, so the true ground
// rose 2-3 m in a hump at the bridge ends (Porinsilta, Linnansilta, Kirjurinluodontie, Pormestarinsilta, Niittäjänsilta...) and stuck through the deck.
// The ground grid is lowered under every bridge to just below its deck line (straight between the street levels at its ends) and, past the ends, kept
// at street level for 12 m and then allowed to rise at 1:6 back to the natural ground; sideways it rises 1:2 from 2 m outside the deck edge.
{ const lines = [];
  const psx = Math.sin(PSIL.head), psy = Math.cos(PSIL.head), pa = [PSIL.x - psx * 14, PSIL.y - psy * 14], pb = [PSIL.x + psx * (PSIL.len + 14), PSIL.y + psy * (PSIL.len + 14)];
  lines.push([pa, pb, PSIL.half * 2]);
  for (const b of RIV.br) { const P = b.p, a = [P[0], P[1]], c = [P[P.length - 2], P[P.length - 1]], mx = (a[0] + c[0]) / 2 - PSIL.x, my = (a[1] + c[1]) / 2 - PSIL.y;
    if (Math.abs(mx * psy - my * psx) < 12 && mx * psx + my * psy > -20 && mx * psx + my * psy < PSIL.len + 20) continue;      /* Porinsilta itse */
    lines.push([a, c, b.w]); }
  let n = 0;
  for (const [a, c, w] of lines) { const dx = c[0] - a[0], dy = c[1] - a[1], L = Math.hypot(dx, dy) || 1, ux = dx / L, uy = dy / L, E0 = TZs(a[0], a[1]), E1 = TZs(c[0], c[1]), hw = w / 2;
    const R = 45 + hw + 14, i0 = Math.max(0, Math.floor((Math.min(a[0], c[0]) - R - TER.x0) / TER.g)), i1 = Math.min(TER.nx - 1, Math.ceil((Math.max(a[0], c[0]) + R - TER.x0) / TER.g));
    const j0 = Math.max(0, Math.floor((Math.min(a[1], c[1]) - R - TER.y0) / TER.g)), j1 = Math.min(TER.ny - 1, Math.ceil((Math.max(a[1], c[1]) + R - TER.y0) / TER.g));
    for (let j = j0; j <= j1; j++) for (let i = i0; i <= i1; i++) { const x = TER.x0 + i * TER.g, y = TER.y0 + j * TER.g, t = (x - a[0]) * ux + (y - a[1]) * uy, s = Math.abs((x - a[0]) * uy - (y - a[1]) * ux);
      const beyond = Math.max(-t, t - L, 0), lat = Math.max(0, s - hw - 2); if (beyond > 45 || lat > 14) continue;
      const u = Math.max(0, Math.min(1, t / L)), lim = E0 + (E1 - E0) * u - 0.12 + Math.max(0, beyond - 12) / 6 + lat / 2, k = j * TER.nx + i;
      if (THG[k] / 10 > lim) { THG[k] = Math.round(lim * 10); n++; } } }
  window.__siltaKummut = n; }
// 20.11.2026 (omistaja: rata ja juna): ratapenkka painetaan sepelin alle ja aseman alikulun kaivanto täytetään raiteiden ja laitureiden kohdalta
// (korkeusmallissa tunneli näkyi 4 m syvänä kuoppana koko ratapihan poikki; rata kulkee suoraan sen yli, asema-aukion puolella portaali). juna/build/build_data.py
{ const o = RATA.ter || []; for (let k = 0; k + 1 < o.length; k += 2) { const i = o[k], v = o[k + 1], old = THG[i]; THG[i] = v; THS[i] = v > old ? Math.max(THS[i], v) : (THS[i] - old < 3 ? Math.min(THS[i], v) : THS[i]); } }
{ const o = RATA.terS || []; for (let k = 0; k + 1 < o.length; k += 2) THS[o[k]] = Math.min(THS[o[k]], o[k + 1]); }   // 21.11.2026: Porttaalin jatke vt 2:n siltojen ali (pinta todelliseen maahan)
const QUAY_MODEL = true;    // 20.11.2026 (omistaja: "Etelärannan pinnat pitänee rakentaa myös itse, ilmakuva ei toimi tuossa"): the hand-built walk, steps, hedges and railing are back and the photo ground is cut out under them (15.11 they were off for the MML 2025 photo)
const QUAY_WALK = TER.wl + 1.05;   // Etelärannan alempi kävelytaso (absoluuttinen), myös ranta/ranta.js:n kulkusillat
function quayCut(x, y) { if (x > 190 && x < 263 && y > 467 && y < 478) return true;      /* the underpass under Porinsilta (Eteläranta block) */
  const Q = RIV.quay; let d = 1e9; for (let i = 0; i + 3 < Q.length; i += 2) { const ax = Q[i], ay = Q[i + 1], dx = Q[i + 2] - ax, dy = Q[i + 3] - ay, L2 = dx * dx + dy * dy || 1, t = ((x - ax) * dx + (y - ay) * dy) / L2;
    if (t < -0.05 || t > 1.05) continue; d = Math.min(d, Math.hypot(ax + dx * t - x, ay + dy * t - y)); }      /* beside the quay only: past its ends the cut left holes (20.11) */
  return d < 13 && !inRiver(x, y); }   // photo ground cells under the hand-built quay (cell centres within 13 m of the quay line, on land)
// 21.11.2026: Porttaali-tunnelin kohdalta maan ruudukko pois (rata/rata.js rakentaa tunnelin, rampit ja reunat)
const rataTun = (x, y) => { const T = RATA.tun; if (!T) return false; const ux = T.b[0] - T.a[0], uy = T.b[1] - T.a[1], L = Math.hypot(ux, uy), dx = x - T.a[0], dy = y - T.a[1], t = (dx * ux + dy * uy) / L, l = (dx * uy - dy * ux) / L;
  return t > T.t0 - 40 && t < T.t1 + 36 && l < T.w / 2 + 4.5 && l > -(T.w / 2 + 4.5 + (t > T.t1 ? 4.5 + Math.max(0, t - T.t1 - 20) * 0.25 : 0)); };
const tSkip = (x, y) => { if (rataTun(x, y)) return true; if (window.__tieSkip && window.__tieSkip(x, y)) return true;      /* 21.11.2026: Luvianpuistokadun käytävä (0105/0335) */ if (!QUAY_MODEL) return false; if (x > -160 && x < 265 && y > 460 && y < 545 && quayCut(x, y)) return true; const i = Math.floor((x - TER.x0) / TER.g), j = Math.floor((y - TER.y0) / TER.g); if (i < 0 || j < 0 || i >= TER.nx || j >= TER.ny) return false; const k = j * TER.nx + i; return (TSKIP[k >> 3] >> (7 - (k & 7))) & 1; };
let gridGeo;
const WREL = (x, y) => TER.wl - TZs(x, y);          // water level relative to the lifted objects at (x, y)
const terrainTex = (() => { const n = TER.nx * TER.ny, d = new Uint16Array(n); for (let i = 0; i < n; i++) d[i] = THREE.DataUtils.toHalfFloat(THS[i] / 10);
  const t = new THREE.DataTexture(d, TER.nx, TER.ny, THREE.RedFormat, THREE.HalfFloatType); t.minFilter = t.magFilter = THREE.LinearFilter; t.needsUpdate = true; return t; })();
function terrainize(mat) {
  if (mat.userData.tDone || mat.userData.noT || mat.isShaderMaterial || mat.isSpriteMaterial) return; mat.userData.tDone = true;
  const prev = mat.onBeforeCompile;
  mat.onBeforeCompile = (sh, r) => { if (prev) prev.call(mat, sh, r);
    sh.uniforms.tHeight = { value: terrainTex }; sh.uniforms.tGrid = { value: new THREE.Vector4(TER.x0, TER.y0, TER.g, 0) }; sh.uniforms.tSize = { value: new THREE.Vector2(TER.nx, TER.ny) };
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nuniform sampler2D tHeight; uniform vec4 tGrid; uniform vec2 tSize;\n#ifdef T_LIFT\nattribute float tLift;\n#endif').replace('#include <project_vertex>', `
      vec4 mvPosition = vec4( transformed, 1.0 );
      #ifdef USE_INSTANCING
        mvPosition = instanceMatrix * mvPosition;
      #endif
      vec4 tWp = modelMatrix * mvPosition;
      vec2 tUv = vec2(((tWp.x - tGrid.x) / tGrid.z + 0.5) / tSize.x, ((-tWp.z - tGrid.y) / tGrid.z + 0.5) / tSize.y);
      #ifdef T_LIFT
        tWp.y += tLift;
      #else
        tWp.y += texture2D(tHeight, tUv).r;
      #endif
      mvPosition = viewMatrix * tWp;
      gl_Position = projectionMatrix * mvPosition;`);
  };
  mat.customProgramCacheKey = () => 'terrain' + (prev ? prev.toString().length : 0);
  mat.needsUpdate = true;
}
function terrainizeScene() { const walk = o => { if (o.userData.noT) return; const m = o.material; if (m) for (const q of Array.isArray(m) ? m : [m]) terrainize(q); for (const c of o.children) walk(c); }; walk(scene); }
const noT = o => { o.traverse(q => { q.userData.noT = true; const m = q.material; if (m) for (const x of Array.isArray(m) ? m : [m]) x.userData.noT = true; }); return o; };
const RMASK = (() => { const M = RIV.mask, b = atob(M.b), a = new Uint8Array(b.length); for (let i = 0; i < b.length; i++) a[i] = b.charCodeAt(i); return { ...M, a }; })();
const RMX0 = -2504.1, RMY0 = -1671.6;      // the river mask keeps the map's original corner (the map grew 1.8 km south for the airport, 20.11.2026)
function inRiver(x, y) { const i = Math.floor((x - RMX0) / RMASK.g), j = Math.floor((y - RMY0) / RMASK.g); if (i < 0 || j < 0 || i >= RMASK.nx || j >= RMASK.ny) return false; const k = j * RMASK.nx + i; return (RMASK.a[k >> 3] >> (7 - (k & 7))) & 1; }
// 20.11.2026 (omistaja): sillat korkeammalle. Tasoitettu maastokenttä (TZs) notkahtaa joen kohdalla, joten sitä seuraavat kannet painuivat
// lähes veteen. Kansi kulkee nyt suoraan rantojen tasojen välillä ja kaartuu keskeltä loivasti ylös (risteilyveneet mahtuvat alta).
const BRK = new Map();   // silta -> [ax, ay, bx, by, E0, E1, kaari]
function brLine(b) { let q = BRK.get(b); if (q) return q; const P = b.p, ax = P[0], ay = P[1], bx = P[P.length - 2], by = P[P.length - 1], L = Math.hypot(bx - ax, by - ay);
  q = [ax, ay, bx, by, TZs(ax, ay), TZs(bx, by), Math.min(1.2, L * 0.008)]; BRK.set(b, q); return q; }
function brDeckZ(x, y, extra = 0.5) {   // absoluuttinen kannen korkeus RIV.br-sillalla (Porinsilta erikseen), muuten null
  for (const b of RIV.br) { const P = b.p; let hit = false;
    if (b.psil === undefined) b.psil = onPorinsilta((P[0] + P[P.length - 2]) / 2, (P[1] + P[P.length - 1]) / 2, 12) !== null;   /* Porinsilta omalla kaarellaan */
    if (b.psil) continue;
    for (let i = 0; i + 3 < P.length && !hit; i += 2) { const ax = P[i], ay = P[i + 1], dx = P[i + 2] - ax, dy = P[i + 3] - ay, L2 = dx * dx + dy * dy, t = Math.max(0, Math.min(1, ((x - ax) * dx + (y - ay) * dy) / L2));
      if (Math.hypot(ax + dx * t - x, ay + dy * t - y) < b.w / 2 + extra) hit = true; }
    if (!hit) continue; const [ax, ay, bx, by, E0, E1, k] = brLine(b), dx = bx - ax, dy = by - ay, L2 = dx * dx + dy * dy || 1, u = Math.max(0, Math.min(1, ((x - ax) * dx + (y - ay) * dy) / L2));
    return Math.max(TZs(x, y), E0 + (E1 - E0) * u + k * 4 * u * (1 - u)); }
  return null; }
function onBridgeDeck(x, y) { for (const b of RIV.br) { const P = b.p; for (let i = 0; i + 3 < P.length; i += 2) { const ax = P[i], ay = P[i + 1], dx = P[i + 2] - ax, dy = P[i + 3] - ay, L2 = dx * dx + dy * dy, t = Math.max(0, Math.min(1, ((x - ax) * dx + (y - ay) * dy) / L2));
  if (Math.hypot(ax + dx * t - x, ay + dy * t - y) < b.w / 2 + 0.5) return true; } } return false; }
const $ = id => document.getElementById(id);
const isTouch = matchMedia('(pointer:coarse)').matches;
if (isTouch) document.body.classList.add('touch');

