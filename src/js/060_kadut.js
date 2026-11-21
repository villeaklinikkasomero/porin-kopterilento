// ---------- streets as geometry (tools/roads/build_roads.py -> roads.js, 18.11.2026): asphalt carriageways, pavements raised on granite kerbs,
// traffic islands and zebra crossings. The surfaces are procedural; the aerial photo only darkens them where it is dark (building shadows).
// heights above the true ground: the aerial-photo ground is drawn as 6 m triangles that bulge a few cm above the true ground on curved terrain,
// so the street surface needs a margin or the photo pokes through it near the camera (owner 18.11: 'asphalt vanishes under the car')
const ROAD = { asph: 0.13, pave: 0.26, mark: 0.145, on: true, paveAt: () => false, asphAt: () => false };
// top of the drawn ground at (x, y): the true ground, or the 6 m triangles of the core ground mesh / the sharper aerial tiles when they bulge above it
function gridTop(x, y, x0, y0, st, dy) { const fx = (x - x0) / st, fy = (y - y0) / st, i = Math.floor(fx), j = Math.floor(fy), u = fx - i, v = fy - j;
  const X = a => x0 + a * st, Y = b => y0 + b * st, z00 = TZg(X(i), Y(j)), z10 = TZg(X(i + 1), Y(j)), z11 = TZg(X(i + 1), Y(j + 1)), z01 = TZg(X(i), Y(j + 1));
  return (u >= v ? z00 + (z10 - z00) * u + (z11 - z10) * v : z00 + (z11 - z01) * u + (z01 - z00) * v) + dy; }
function groundTop(x, y) {
  if (window.__quayZ) { const q = window.__quayZ(x, y, 8.2); if (q !== null) return q - ROAD.pave; }   // Eteläranta: the hand-built walk and steps (the callers add the pavement height)
  const S = 512, ti = Math.floor((x + 1280) / S), tj = Math.floor((y + 1280) / S), st = 6;   // gridGeo steps exactly 6 m
  return Math.max(TZg(x, y), gridTop(x, y, -HW, YS, 6, 0), gridTop(x, y, -1280 + ti * S, -1280 + tj * S, st, 0.03));
}
// cars stand on the asphalt: the car meshes follow the smoothed field TZs, the street surface the true ground TZg
const ONEWAY = new Map();   // 'road index,segment' -> +1 driving along the way's point order, -1 against (tools/roads/build_roads.py, OSM oneway / roundabouts)
const owOk = (ri, si, fw) => { const d = ONEWAY.get(ri + ',' + si); return !d || (d > 0) === fw; };
const roadDZ = (x, y) => ROAD.on && inCore(x, y) ? groundTop(x, y) + ROAD.asph - TZs(x, y) : 0;
import('./roads.js').then(mod => {
  const R = mod.default, dec = b => new Int16Array(TDEC(b).buffer);
  const noiseTex = (seed, base, amp, spots, N = 512) => {
    const c = document.createElement('canvas'); c.width = c.height = N; const g = c.getContext('2d'), d = g.createImageData(N, N);
    let sd = seed; const rnd = () => (sd = (sd * 16807) % 2147483647) / 2147483647;
    const v = new Float32Array(N * N); for (let i = 0; i < N * N; i++) v[i] = rnd() * 0.5 + 0.5;
    for (let k = 0; k < spots; k++) { const x = rnd() * N, y = rnd() * N, r = 2 + rnd() * 18, a = (rnd() - 0.5) * 0.25;   // patches and stains
      for (let yy = -r; yy <= r; yy++) for (let xx = -r; xx <= r; xx++) if (xx * xx + yy * yy < r * r) { const q = (((y + yy) | 0) % N + N) % N * N + (((x + xx) | 0) % N + N) % N; v[q] += a * (1 - (xx * xx + yy * yy) / (r * r)); } }
    for (let i = 0; i < N * N; i++) { const q = Math.max(0, Math.min(255, (base + (v[i] - 0.75) * amp) * 255)); d.data[i * 4] = q; d.data[i * 4 + 1] = q; d.data[i * 4 + 2] = q * 1.02; d.data[i * 4 + 3] = 255; }
    g.putImageData(d, 0, 0); const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; t.colorSpace = THREE.SRGBColorSpace; return t; };
  const ld = (f, srgb = true) => { const t = new THREE.TextureLoader().load(f); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = renderer.capabilities.getMaxAnisotropy(); if (srgb) t.colorSpace = THREE.SRGBColorSpace; return t; };
  // tools/roads/make_tex.py: Pori stone-mastic asphalt (grey chips, some red granite), finer pavement asphalt, a 16 m crack / sealed-crack / patch map
  const tAO = ld('./roads_ao.png', false), uAB = new THREE.Vector4(R.bb[0], R.bb[1], R.bb[2] - R.bb[0], R.bb[3] - R.bb[1]); ROAD.tAO = tAO; ROAD.uAB = uAB;
  if (GRASS.mask) GRASS.mask(tAO, uAB);
  const tAsph = ld('./road_asph.jpg'), tPave = ld('./road_pave.jpg'), tCrack = ld('./road_crack.png', false), tMac = noiseTex(11, 0.75, 0.5, 600);
  // world-space chips (two scales, rotated, so the 1.6 m tile never shows), large-scale wear, cracks gated "here and there",
  // and the photo shade: how much darker the photo is than sunlit paving there (the houses' shadows)
  const surf = (tex, rep, tint, ref, off, crackAmt) => { const m = new THREE.MeshLambertMaterial({ color: tint, polygonOffset: true, polygonOffsetFactor: off, polygonOffsetUnits: off });
    m.onBeforeCompile = sh => { Object.assign(sh.uniforms, { tS: { value: tex }, tC: { value: tCrack }, tM: { value: tMac }, tO: { value: orto }, uC: { value: new THREE.Vector3(HW, YS, YSPAN) }, tA: { value: tAO }, uAB: { value: uAB } });
      sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 vRw;').replace('#include <project_vertex>', '#include <project_vertex>\nvRw = (modelMatrix * vec4(transformed, 1.0)).xyz;');
      sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\nvarying vec3 vRw; uniform sampler2D tS, tC, tM, tO, tA; uniform vec3 uC; uniform vec4 uAB;').replace('#include <map_fragment>', `
        vec2 wp = vec2(vRw.x, -vRw.z);
        vec2 r2 = mat2(0.8, -0.6, 0.6, 0.8) * wp;
        vec3 tx = texture2D(tS, wp * ${(1 / rep).toFixed(4)}).rgb * 0.55 + texture2D(tS, r2 * ${(0.37 / rep).toFixed(4)} + 0.31).rgb * 0.45;
        float mac = texture2D(tM, wp * 0.021).r * 0.6 + texture2D(tM, r2 * 0.0047 + 0.5).r * 0.4;          // worn / newer areas
        tx *= 0.86 + 0.28 * mac;
        float gate = smoothstep(0.52, 0.72, texture2D(tM, wp * 0.0091 + 0.13).r);                                  // cracks only in some stretches
        float ck = texture2D(tC, wp * 0.0625).r, ck2 = texture2D(tC, r2 * 0.051 + 0.47).r;
        tx *= mix(1.0, min(ck, mix(1.0, ck2, 0.6)), ${crackAmt.toFixed(2)} * (0.35 + 0.65 * gate));
        vec3 ph = texture2D(tO, vec2((wp.x + uC.x) / (2.0 * uC.x), (wp.y - uC.y) / uC.z), 2.0).rgb;
        float L = dot(ph, vec3(0.3, 0.55, 0.15)), sh_ = clamp(L / ${ref.toFixed(3)}, 0.6, 1.04);
        float ao = texture2D(tA, (wp - uAB.xy) / uAB.zw).r;                                                   // contact shade at the house walls
        diffuseColor.rgb *= tx * 1.9 * mix(1.0, sh_, 0.55) * ao;`); };
    return m; };
  const mAsph = surf(tAsph, 1.6, 0xaab0b8, 0.30, -6, 0.9), mPave = surf(tPave, 1.2, 0xd9dde2, 0.42, -6, 0.3);
  const mMark = new THREE.MeshLambertMaterial({ color: 0xe9e9e4, polygonOffset: true, polygonOffsetFactor: -8, polygonOffsetUnits: -8 });
  const mKerb = new THREE.MeshLambertMaterial({ color: 0x9a9893, side: THREE.DoubleSide });
  const flat = (a, dz) => { const P = new Float32Array(a.length / 2 * 3);
    for (let i = 0, k = 0; i < a.length; i += 2, k += 3) { const x = a[i] / 10, y = a[i + 1] / 10; P[k] = x; P[k + 1] = groundTop(x, y) + dz; P[k + 2] = -y; }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(P, 3)); g.computeVertexNormals(); return g; };
  const add = (g, m) => { const me = noT(new THREE.Mesh(g, m)); me.matrixAutoUpdate = false; scene.add(me); (window.__roadM = window.__roadM || []).push(me); return me; };
  add(flat(dec(R.asph), ROAD.asph), mAsph); add(flat(dec(R.pave), ROAD.pave), mPave); add(flat(dec(R.mark), ROAD.mark), mMark);
  // stone paving on the pedestrian streets, Eetunaukio and Kauppatori (owner's PBR set pori_kivetys_harmaanpunainen, one repeat = 2.2 m)
  if (R.kivi) {
    const g = flat(dec(R.kivi), ROAD.pave), P = g.attributes.position.array, U = new Float32Array(P.length / 3 * 2);
    for (let i = 0, k = 0; i < P.length; i += 3, k += 2) { U[k] = P[i] / 2.2; U[k + 1] = -P[i + 2] / 2.2; }
    g.setAttribute('uv', new THREE.BufferAttribute(U, 2));
    const orm = ld('./kivetys_orm.jpg', false);
    const mK = new THREE.MeshStandardMaterial({ map: ld('./kivetys_albedo.jpg'), normalMap: ld('./kivetys_normal.jpg', false), aoMap: orm, roughnessMap: orm, metalness: 0, roughness: 1,
      polygonOffset: true, polygonOffsetFactor: -6, polygonOffsetUnits: -6 });
    mK.normalScale.set(1.2, 1.2);
    mK.onBeforeCompile = sh => { sh.uniforms.tO = { value: orto }; sh.uniforms.uC = { value: new THREE.Vector3(HW, YS, YSPAN) }; sh.uniforms.tA = { value: ROAD.tAO }; sh.uniforms.uAB = { value: ROAD.uAB };
      sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 vRw;').replace('#include <project_vertex>', '#include <project_vertex>\nvRw = (modelMatrix * vec4(transformed, 1.0)).xyz;');
      sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\nvarying vec3 vRw; uniform sampler2D tO, tA; uniform vec3 uC; uniform vec4 uAB;').replace('#include <map_fragment>', `#include <map_fragment>
        { vec2 wp = vec2(vRw.x, -vRw.z); diffuseColor.rgb *= texture2D(tA, (wp - uAB.xy) / uAB.zw).r; vec3 ph = texture2D(tO, vec2((wp.x + uC.x) / (2.0 * uC.x), (wp.y - uC.y) / uC.z), 2.0).rgb;
          float L = dot(ph, vec3(0.3, 0.55, 0.15)), sh_ = clamp(L / 0.42, 0.65, 1.04); diffuseColor.rgb *= 1.38 * mix(1.0, sh_, 0.45); }`); };
    add(g, mK); ROAD.mK = mK;
  }
  // kerbs: the pavement edge (pavement on the left of a->b) drops to the asphalt / ground; a 0.15 m granite band along the top
  const K = dec(R.kerb), P = [];
  for (let i = 0; i < K.length; i += 4) { const ax = K[i] / 10, ay = K[i + 1] / 10, bx = K[i + 2] / 10, by = K[i + 3] / 10, za = groundTop(ax, ay), zb = groundTop(bx, by);
    P.push(ax, za + ROAD.pave, -ay, ax, za - 0.05, -ay, bx, zb - 0.05, -by, ax, za + ROAD.pave, -ay, bx, zb - 0.05, -by, bx, zb + ROAD.pave, -by); }
  // lowered kerbs at the crossings: the top follows the ramp (h = share of the full kerb height)
  const rz = (x, y, h) => groundTop(x, y) + ROAD.asph + 0.03 + (ROAD.pave - ROAD.asph - 0.03) * h;
  if (R.kerbh) { const KH = dec(R.kerbh);
    for (let i = 0; i < KH.length; i += 6) { const ax = KH[i] / 10, ay = KH[i + 1] / 10, ha = KH[i + 2] / 1000, bx = KH[i + 3] / 10, by = KH[i + 4] / 10, hb = KH[i + 5] / 1000, za = groundTop(ax, ay), zb = groundTop(bx, by), ta = rz(ax, ay, ha), tb = rz(bx, by, hb);
      P.push(ax, ta, -ay, ax, za - 0.05, -ay, bx, zb - 0.05, -by, ax, ta, -ay, bx, zb - 0.05, -by, bx, tb, -by); } }
  const kg = new THREE.BufferGeometry(); kg.setAttribute('position', new THREE.Float32BufferAttribute(P, 3)); kg.computeVertexNormals(); add(kg, mKerb);
  const sloped = (a, uv) => { const n = a.length / 3, Pp = new Float32Array(n * 3), U = uv ? new Float32Array(n * 2) : null;
    for (let i = 0, k = 0; i < a.length; i += 3, k++) { const x = a[i] / 10, y = a[i + 1] / 10; Pp[k * 3] = x; Pp[k * 3 + 1] = rz(x, y, a[i + 2] / 1000); Pp[k * 3 + 2] = -y; if (U) { U[k * 2] = x / 2.2; U[k * 2 + 1] = y / 2.2; } }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(Pp, 3)); if (U) g.setAttribute('uv', new THREE.BufferAttribute(U, 2)); g.computeVertexNormals(); return g; };
  if (R.rampp) add(sloped(dec(R.rampp)), mPave);
  if (R.rampk && ROAD.mK) add(sloped(dec(R.rampk), true), ROAD.mK);
  // owner's PBR grass (1.2 m repeat) and red granite gravel (0.6 m): esplanade medians on kerbs, park lawns and paths at ground level
  const pbr = (pre, rp, lawn) => { const orm = ld('./' + pre + '_orm.jpg', false);
    const m = new THREE.MeshStandardMaterial({ map: ld('./' + pre + '_albedo.jpg'), normalMap: ld('./' + pre + '_normal.jpg', false), aoMap: orm, roughnessMap: orm, metalness: 0, roughness: 1,
      polygonOffset: true, polygonOffsetFactor: -6, polygonOffsetUnits: -6 });
    m.onBeforeCompile = sh => { Object.assign(sh.uniforms, { tO: { value: orto }, uC: { value: new THREE.Vector3(HW, YS, YSPAN) }, tA: { value: tAO }, uAB: { value: uAB } });
      sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 vRw;').replace('#include <project_vertex>', '#include <project_vertex>\nvRw = (modelMatrix * vec4(transformed, 1.0)).xyz;');
      sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\nvarying vec3 vRw; uniform sampler2D tO, tA; uniform vec3 uC; uniform vec4 uAB;').replace('#include <map_fragment>', `#include <map_fragment>
        { vec2 wp = vec2(vRw.x, -vRw.z); vec3 ph = texture2D(tO, vec2((wp.x + uC.x) / (2.0 * uC.x), (wp.y - uC.y) / uC.z), 1.5).rgb;
          ${lawn ? 'float gr = ph.g - max(ph.r, ph.b) * 0.96; if (gr < 0.004) discard;   // lawn only where the photo is green: paths, sand and beds stay as photographed' : ''}
          float L = dot(ph, vec3(0.3, 0.55, 0.15)), sh_ = clamp(L / ${lawn ? '0.30' : '0.40'}, 0.62, 1.05);
          diffuseColor.rgb *= 1.25 * mix(1.0, sh_, 0.5) * texture2D(tA, (wp - uAB.xy) / uAB.zw).r; }`); };
    m.userData.rp = rp; return m; };
  const withUV = (g, rp) => { const P = g.attributes.position.array, U = new Float32Array(P.length / 3 * 2);
    for (let i = 0, k = 0; i < P.length; i += 3, k += 2) { U[k] = P[i] / rp; U[k + 1] = -P[i + 2] / rp; } g.setAttribute('uv', new THREE.BufferAttribute(U, 2)); return g; };
  const mGrass = pbr('nurmi', 1.2, false), mLawn = pbr('nurmi', 1.2, true), mGravel = pbr('sepeli', 0.6, false);
  if (R.medg) add(withUV(flat(dec(R.medg), ROAD.pave), 1.2), mGrass);
  if (R.medp) add(withUV(flat(dec(R.medp), ROAD.pave + 0.005), 0.6), mGravel);
  if (R.lawn) add(withUV(flat(dec(R.lawn), 0.05), 1.2), mLawn);
  if (R.path) add(withUV(flat(dec(R.path), 0.07), 0.6), mGravel);
  if (R.tadd && TREES.add) TREES.add(dec(R.tadd));
  { // 1 m raster of the pavements for the car: driving over a kerb lifts it onto the pavement
    const [x0, y0, x1, y1] = R.bb, nx = Math.ceil(x1 - x0), ny = Math.ceil(y1 - y0), M = new Uint8Array(nx * ny);          // bit 1 pavement, bit 2 carriageway (for the signal posts: where the kerb is)
    for (const [T, bit] of [[dec(R.pave), 1], ...(R.kivi ? [[dec(R.kivi), 1]] : []), [dec(R.asph), 2]])   /* the stone paving lies at pavement height too (19.11: walkers sank into it) */ for (let i = 0; i < T.length; i += 6) { const ax = T[i] / 10, ay = T[i + 1] / 10, bx = T[i + 2] / 10, by = T[i + 3] / 10, cx = T[i + 4] / 10, cy = T[i + 5] / 10;
      const d = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy); if (Math.abs(d) < 1e-6) continue;
      for (let gy = Math.floor(Math.min(ay, by, cy) - y0); gy <= Math.ceil(Math.max(ay, by, cy) - y0); gy++) for (let gx = Math.floor(Math.min(ax, bx, cx) - x0); gx <= Math.ceil(Math.max(ax, bx, cx) - x0); gx++) {
        if (gx < 0 || gy < 0 || gx >= nx || gy >= ny) continue; const px = x0 + gx + 0.5, py = y0 + gy + 0.5;
        const u = ((by - cy) * (px - cx) + (cx - bx) * (py - cy)) / d, v = ((cy - ay) * (px - cx) + (ax - cx) * (py - cy)) / d;
        if (u >= -0.05 && v >= -0.05 && u + v <= 1.05) M[gy * nx + gx] |= bit; } }
    ROAD.paveAt = (x, y) => { const gx = Math.floor(x - x0), gy = Math.floor(y - y0); return gx >= 0 && gy >= 0 && gx < nx && gy < ny && (M[gy * nx + gx] & 1) === 1; };
    if (R.kivi) { const T = dec(R.kivi), KI = new Int32Array(nx * ny), ZC = new Map();       // which stone triangle covers each 1 m cell (index + 1)
      const tri = i => [T[i] / 10, T[i + 1] / 10, T[i + 2] / 10, T[i + 3] / 10, T[i + 4] / 10, T[i + 5] / 10], bary = (t, px, py) => { const d = (t[3] - t[5]) * (t[0] - t[4]) + (t[4] - t[2]) * (t[1] - t[5]); if (Math.abs(d) < 1e-6) return null;
        const u = ((t[3] - t[5]) * (px - t[4]) + (t[4] - t[2]) * (py - t[5])) / d, v = ((t[5] - t[1]) * (px - t[4]) + (t[0] - t[4]) * (py - t[5])) / d; return [u, v, 1 - u - v]; };
      for (let i = 0; i < T.length; i += 6) { const t = tri(i); for (let gy = Math.floor(Math.min(t[1], t[3], t[5]) - y0); gy <= Math.ceil(Math.max(t[1], t[3], t[5]) - y0); gy++) for (let gx = Math.floor(Math.min(t[0], t[2], t[4]) - x0); gx <= Math.ceil(Math.max(t[0], t[2], t[4]) - x0); gx++) {
          if (gx < 0 || gy < 0 || gx >= nx || gy >= ny) continue; const w = bary(t, x0 + gx + 0.5, y0 + gy + 0.5); if (w && w[0] >= -0.05 && w[1] >= -0.05 && w[2] >= -0.05) KI[gy * nx + gx] = i + 1; } }
      // height of the stone paving at (x, y): the plane through its triangle's corner heights (the mesh is lifted only at the corners, and the triangles are
      // tens of metres long, so groundTop(x, y) is off by up to a few decimetres in between: walkers and the player sank or floated, 19.11.2026)
      ROAD.kiviZ = (x, y) => { const gx = Math.floor(x - x0), gy = Math.floor(y - y0); if (gx < 0 || gy < 0 || gx >= nx || gy >= ny) return null; const k = KI[gy * nx + gx]; if (!k) return null;
        const t = tri(k - 1); let w = bary(t, x, y); if (!w) return null; let z = ZC.get(k); if (!z) { z = [groundTop(t[0], t[1]), groundTop(t[2], t[3]), groundTop(t[4], t[5])]; ZC.set(k, z); }
        w = w.map(q => Math.max(0, q)); const sw = w[0] + w[1] + w[2] || 1; return (w[0] * z[0] + w[1] * z[1] + w[2] * z[2]) / sw + ROAD.pave; }; }
    ROAD.asphAt = (x, y) => { const gx = Math.floor(x - x0), gy = Math.floor(y - y0); return gx >= 0 && gy >= 0 && gx < nx && gy < ny && M[gy * nx + gx] === 2; };
    /* 20.11.2026 (owner, checked against the aerial photo): round the market hall the photo showed through where roads.js has no surface - the bus stands
       west and north of the hall become asphalt lanes, the platform under the hall's west canopy (east of x 14.5) and the strips north and south of the
       square get the stone paving. Filled per 1 m cell where nothing lies yet (not in houses), as runs of at most 4 m, a centimetre under the pavement
       level so the existing surfaces win where they overlap; the cells count as pavement for the car and the walkers (flat, no kerbs inside). */
    /* 20.11.2026 (omistaja: "torin kivetys tulisi olla koko alueella"): east of x 80 too, inside the square's outline (Kauppatori edges from the photo, 2 m out) */
    const TP = [[18, 43], [31, 39], [90, 24.5], [110, 97], [104, 113], [46, 118], [20, 118]], inTori = (x, y) => { let c = false; for (let i = 0, j = TP.length - 1; i < TP.length; j = i++) { const [xi, yi] = TP[i], [xj, yj] = TP[j]; if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) c = !c; } return c; };
    { const QA = [], QK = [], dz = ROAD.pave - 0.012, zone = (x, y) => (x < 14.5 || (y >= 106 && x < 31)) ? 1 : 2;
      const W0 = -6, H0 = 24, WN = 116, HN = 102, Z = new Uint8Array(WN * HN), cell = (x, y) => { const gx = Math.floor(x - x0), gy = Math.floor(y - y0); return gx >= 0 && gy >= 0 && gx < nx && gy < ny ? M[gy * nx + gx] : 255; };
      const house = (x, y) => bldTopAt(x + 0.5, y + 0.5) > TZs(x + 0.5, y + 0.5) + 1.5;
      for (let j = 1; j < HN - 1; j++) for (let i = 1; i < WN - 1; i++) { const x = W0 + i, y = H0 + j; if ((x > 80 && !inTori(x + 0.5, y + 0.5)) || y >= 124 || y < 25) continue; if (cell(x, y) === 0 && !house(x, y)) Z[j * WN + i] = zone(x + 0.5, y + 0.5); }
      /* one cell of overlap into the pavement round the gaps (never onto the carriageway or into houses): the drawn edge of a pavement triangle runs
         through its cells, and without this the photo showed as slivers along it */
      const Z2 = Z.slice(); for (let j = 1; j < HN - 1; j++) for (let i = 1; i < WN - 1; i++) { const x = W0 + i, y = H0 + j; if (Z[j * WN + i] || cell(x, y) !== 1 || house(x, y)) continue;
        for (let dj = -1; dj <= 1 && !Z2[j * WN + i]; dj++) for (let di = -1; di <= 1; di++) { const q = Z[(j + dj) * WN + i + di]; if (q) { Z2[j * WN + i] = q; break; } } }
      for (let j = 1; j < HN - 1; j++) { const y = H0 + j; let run = null;
        for (let i = 1; i < WN; i++) { const x = W0 + i;
          const k = i < WN - 1 ? Z2[j * WN + i] : 0;
          if (run && (k !== run.k || x - run.x >= 4)) { (run.k === 1 ? QA : QK).push([run.x, y, x, y + 1]); run = null; }
          if (k && !run) run = { x, k }; } }
      const geo = (Q, uv) => { const P = [], U = [];
        for (const [xa, ya, xb, yb] of Q) { for (const [x, y] of [[xa, ya], [xb, ya], [xb, yb], [xa, ya], [xb, yb], [xa, yb]]) { P.push(x, groundTop(x, y) + dz, -y); U.push(x / 2.2, y / 2.2); }
          for (let yy = ya; yy < yb; yy++) for (let xx = xa; xx < xb; xx++) { const gx = Math.floor(xx - x0), gy = Math.floor(yy - y0); if (gx >= 0 && gy >= 0 && gx < nx && gy < ny) M[gy * nx + gx] |= 1; } }
        const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3)); if (uv) g.setAttribute('uv', new THREE.Float32BufferAttribute(U, 2)); g.computeVertexNormals(); return g; };
      if (QA.length) add(geo(QA, false), mAsph); if (QK.length && ROAD.mK) add(geo(QK, true), ROAD.mK); ROAD.toriFill = { asph: QA.length, kivi: QK.length }; }
    /* 20.11.2026 (omistaja: "rakenne yhtenäiseksi ja asfaltti koko alueelle, Porinsiltaa pitää jatkaa"): roads.js leaves Porinsilta's south approach
       empty for 32 m (the OSM bridge way is longer than the bridge), so the car drove on the photo ground up to the deck. The carriageway (9.2 m) and
       the pavements on both sides continue from the Eteläranta street to the deck, on the ground that is levelled there (see the bridge humps above). */
    { const ux = Math.sin(PSIL.head), uy = Math.cos(PSIL.head), wx = uy, wy = -ux, CW = 4.6, HWB = PSIL.half, T0 = -48, T1 = -13.3, STP = 1.5, PA = [], PP = [], PK = [];
      /* the last 8 m rise onto the deck front (the model's slab: carriageway ~0.1 m, pavements ~0.3 m above psilDeck) */
      const ramp = (t, s, h) => { const f = Math.max(0, Math.min(1, (t - (T1 - 8)) / 8)); if (!f) return 0; const [x, y] = pt(t, s), tgt = psilDeck(T1) + (Math.abs(s) < CW + 0.01 && h < ROAD.pave ? 0.08 : 0.27); return Math.max(0, tgt - (groundTop(x, y) + h)) * f * f * (3 - 2 * f); };
      const pt = (t, s) => [PSIL.x + ux * t + wx * s, PSIL.y + uy * t + wy * s];
      const z = (t, s, h) => { const [x, y] = pt(t, s); return groundTop(x, y) + h + ramp(t, s, h); };
      for (let t = T0; t < T1 - 0.01; t += STP) { const t2 = Math.min(T1, t + STP);
        const q = (arr, s0, s1, h) => { for (const [tt, ss] of [[t, s0], [t2, s1], [t2, s0], [t, s0], [t, s1], [t2, s1]]) {      /* counter-clockwise on the map = facing up (20.11: the first version faced down and was culled) */ const [x, y] = pt(tt, ss); arr.push(x, groundTop(x, y) + h + ramp(tt, ss, h), -y); } };
        q(PA, -CW, CW, ROAD.asph); q(PP, -HWB, -CW, ROAD.pave); q(PP, CW, HWB, ROAD.pave);
        for (const sd of [-CW, CW]) { const [ax, ay] = pt(t, sd), [bx, by] = pt(t2, sd); PK.push(ax, z(t, sd, ROAD.pave), -ay, ax, z(t, sd, -0.05), -ay, bx, z(t2, sd, -0.05), -by, ax, z(t, sd, ROAD.pave), -ay, bx, z(t2, sd, -0.05), -by, bx, z(t2, sd, ROAD.pave), -by); } }
      const mk = A => { const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(A, 3)); g.computeVertexNormals(); return g; };
      add(mk(PA), mAsph); add(mk(PP), mPave); add(mk(PK), mKerb);
      for (let t = T0; t <= T1; t += 0.5) for (let sd = -HWB; sd <= HWB; sd += 0.5) { const [x, y] = pt(t, sd), gx = Math.floor(x - x0), gy = Math.floor(y - y0); if (gx >= 0 && gy >= 0 && gx < nx && gy < ny) M[gy * nx + gx] = Math.abs(sd) < CW ? 2 : 1; } }
    /* 20.11.2026 (omistaja: "tarkista etelärantaa kuvista"): the light stone-paved square between the Eteläranta quay and Porinsilta's approach
       (x 140-196, y 434-468 in the aerial photo, with the planters and the small lawn) had no surface in roads.js: paved per 1 m cell where nothing lies
       yet, not on the lawn and not under the hand-built quay. */
    { const LW = dec(R.lawn), lawn = new Uint8Array(60 * 40), LX = 138, LY = 430;
      for (let i = 0; i < LW.length; i += 6) { const ax = LW[i] / 10, ay = LW[i + 1] / 10, bx = LW[i + 2] / 10, by = LW[i + 3] / 10, cx = LW[i + 4] / 10, cy = LW[i + 5] / 10;
        if (Math.max(ax, bx, cx) < LX || Math.min(ax, bx, cx) > LX + 60 || Math.max(ay, by, cy) < LY || Math.min(ay, by, cy) > LY + 40) continue; const d = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy); if (Math.abs(d) < 1e-6) continue;
        for (let gy = 0; gy < 40; gy++) for (let gx = 0; gx < 60; gx++) { const px = LX + gx + 0.5, py = LY + gy + 0.5, u = ((by - cy) * (px - cx) + (cx - bx) * (py - cy)) / d, v = ((cy - ay) * (px - cx) + (ax - cx) * (py - cy)) / d; if (u >= 0 && v >= 0 && u + v <= 1) lawn[gy * 60 + gx] = 1; } }
      const SQ = [[140, 434], [184, 434], [197, 446], [197, 470], [140, 470]], inSq = (x, y) => { let c = false; for (let i = 0, j = SQ.length - 1; i < SQ.length; j = i++) { const [xi, yi] = SQ[i], [xj, yj] = SQ[j]; if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) c = !c; } return c; };
      const PS = [];
      for (let y = LY; y < LY + 40; y++) for (let x = LX; x < LX + 60; x++) { const cx = x + 0.5, cy = y + 0.5, gx = Math.floor(x - x0), gy = Math.floor(y - y0);
        if (!inSq(cx, cy) || lawn[(y - LY) * 60 + (x - LX)] || (gx >= 0 && gy >= 0 && gx < nx && gy < ny && M[gy * nx + gx]) || (window.__quayZ && window.__quayZ(cx, cy, 18) !== null) || inRiver(cx, cy)) continue;
        for (const [px, py] of [[x, y], [x + 1, y], [x + 1, y + 1], [x, y], [x + 1, y + 1], [x, y + 1]]) PS.push(px, groundTop(px, py) + ROAD.pave - 0.012, -py);
        if (gx >= 0 && gy >= 0 && gx < nx && gy < ny) M[gy * nx + gx] |= 1; }
      const LA = window.__laatta, ca = LA ? Math.cos(LA.kulma) : 1, sa = LA ? Math.sin(LA.kulma) : 0;
      const laattaGeo = A => { const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(A, 3)); const U = [];
        for (let i = 0; i < A.length; i += 3) { const x = A[i], y = -A[i + 2]; U.push((ca * x + sa * y) / 4, (-sa * x + ca * y) / 4); } g.setAttribute('uv', new THREE.Float32BufferAttribute(U, 2)); g.computeVertexNormals(); return g; };
      const mLaatta = LA ? new THREE.MeshLambertMaterial({ map: LA.graniitti, color: new THREE.Color().setRGB(0.74 * 1.12, 0.73 * 1.12, 0.70 * 1.12), polygonOffset: true, polygonOffsetFactor: -6, polygonOffsetUnits: -6 }) : (ROAD.mK || mPave);
      if (PS.length) add(laattaGeo(PS), mLaatta);
      ROAD.etFill = PS.length / 18;
      /* 20.11.2026 (omistaja: "maapinnat alueelle, nyt ilmakuvaa, joka tulisi peittää autenttisemmalla"): the strip between the quay's top paving (18 m
         inland) and the Eteläranta street - terraces, the pavilions' surroundings, the bridge head - showed the photo: granite slabs per 1 m cell where
         nothing lies yet (no road, lawn, path, house, quay, river or the underpass's cut). */
      { const GX = -140, GY = 440, GW = 356, GH = 82, soft = new Uint8Array(GW * GH);
        for (const key of ['lawn', 'path', 'medg', 'medp']) { if (!R[key]) continue; const T = dec(R[key]);
          for (let i = 0; i < T.length; i += 6) { const ax = T[i] / 10, ay = T[i + 1] / 10, bx = T[i + 2] / 10, by = T[i + 3] / 10, cx = T[i + 4] / 10, cy = T[i + 5] / 10;
            if (Math.max(ax, bx, cx) < GX || Math.min(ax, bx, cx) > GX + GW || Math.max(ay, by, cy) < GY || Math.min(ay, by, cy) > GY + GH) continue; const d = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy); if (Math.abs(d) < 1e-6) continue;
            for (let gy = Math.max(0, Math.floor(Math.min(ay, by, cy) - GY)); gy <= Math.min(GH - 1, Math.ceil(Math.max(ay, by, cy) - GY)); gy++) for (let gx = Math.max(0, Math.floor(Math.min(ax, bx, cx) - GX)); gx <= Math.min(GW - 1, Math.ceil(Math.max(ax, bx, cx) - GX)); gx++) {
              const px = GX + gx + 0.5, py = GY + gy + 0.5, u = ((by - cy) * (px - cx) + (cx - bx) * (py - cy)) / d, v = ((cy - ay) * (px - cx) + (ax - cx) * (py - cy)) / d; if (u >= 0 && v >= 0 && u + v <= 1) soft[gy * GW + gx] = 1; } } }
        const GP = [];
        for (let j = 0; j < GH; j++) for (let i = 0; i < GW; i++) { const x = GX + i, y = GY + j, cx = x + 0.5, cy = y + 0.5, gx = Math.floor(x - x0), gy = Math.floor(y - y0);
          if (soft[j * GW + i] || (gx >= 0 && gy >= 0 && gx < nx && gy < ny && M[gy * nx + gx]) || inRiver(cx, cy) || quayCut(cx, cy) || (window.__quayZ && window.__quayZ(cx, cy, 18) !== null)) continue;
          if (bldTopAt(cx, cy) > TZs(cx, cy) + 1.5) continue;
          for (const [px, py] of [[x, y], [x + 1, y], [x + 1, y + 1], [x, y], [x + 1, y + 1], [x, y + 1]]) GP.push(px, groundTop(px, py) + ROAD.pave - 0.012, -py);
          if (gx >= 0 && gy >= 0 && gx < nx && gy < ny) M[gy * nx + gx] |= 1; }
        if (GP.length) add(laattaGeo(GP), mLaatta);
        ROAD.etGap = GP.length / 18; console.log('[eteläranta] laattaa: aukio', ROAD.etFill, 'm², väli', ROAD.etGap, 'm²'); }
    }
  }
  if (R.ow) { const O = dec(R.ow); for (let i = 0; i < O.length; i += 3) ONEWAY.set(O[i] + ',' + O[i + 1], O[i + 2]); }
  if (R.tmv && TREES.move) { const s0 = atob(R.tmv), u8 = new Uint8Array(s0.length); for (let i = 0; i < s0.length; i++) u8[i] = s0.charCodeAt(i); TREES.move(new Int32Array(u8.buffer)); }
  ROAD.on = true; window.__roads = { asph: R.asph.length, pave: R.pave.length };
}).catch(e => console.log('roads.js not loaded', e));

