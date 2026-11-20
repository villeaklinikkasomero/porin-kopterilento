// Kokemäenjoen rannat: luonnonkivikko vesirajaan ja Etelärannan laiturit – ILMAN muutoksia index.html:n rakenteisiin.
//
// Kokeilu:   await import('./ranta/ranta.js')         Pysyvästi: <script type="module" src="ranta/ranta.js"></script>
//
// Kivikko: joen rajauksen (river.js, water-kolmiot) reunaan kaista jokikiviä (saumaton tekstuuri + normal/AO/karheus), joka alkaa pinnan alta ja
//   nousee penkalle, ja sen päällä isompia lohkareita (rantakivet_blender.obj, 12 muotoa). Märkä ja tumma vesirajassa, reuna hajoaa ilmakuvaan. Ei Etelärannan muurin (RIV.quay), siltojen eikä kartan reunan kohdalle.
// Laiturit: Etelärannan ponttonilaiturit mitattuna MML:n ilmakuvasta (20.11.2026), puukansi kellukkeilla ja kulkusilta muurilta.
import * as THREE from '../three.module.min.js';
import RIV from '../river.js';
import TER from '../terrain.js';

const dec = b => { const s = atob(b), a = new Uint8Array(s.length); for (let i = 0; i < s.length; i++) a[i] = s.charCodeAt(i); return new Int16Array(a.buffer); };
const THG = dec(TER.hg), THS = dec(TER.hs);
const bil = (A, x, y) => { const fx = Math.min(TER.nx - 1.001, Math.max(0, (x - TER.x0) / TER.g)), fy = Math.min(TER.ny - 1.001, Math.max(0, (y - TER.y0) / TER.g)), i = Math.floor(fx), j = Math.floor(fy), u = fx - i, v = fy - j, k = j * TER.nx + i;
  return ((A[k] * (1 - u) + A[k + 1] * u) * (1 - v) + (A[k + TER.nx] * (1 - u) + A[k + TER.nx + 1] * u) * v) / 10; };
const TZg = (x, y) => bil(THG, x, y), TZs = (x, y) => bil(THS, x, y);
const WL = TER.wl;
const QUAY_WALK = TER.wl + 1.05;   // index.html: QUAY_WALK, Etelärannan alempi kävelytaso (absoluuttinen)
const PSIL = { x: 207.45, y: 477.95, len: 170.04, head: Math.atan2(245.85 - 207.45, 643.6 - 477.95), half: 7.4 };

function segDist(px, py, ax, ay, bx, by) { const dx = bx - ax, dy = by - ay, L2 = dx * dx + dy * dy || 1, t = Math.max(0, Math.min(1, ((px - ax) * dx + (py - ay) * dy) / L2)); return Math.hypot(ax + dx * t - px, ay + dy * t - py); }
function polyDist(px, py, P) { let d = 1e9; for (let i = 0; i + 3 < P.length; i += 2) d = Math.min(d, segDist(px, py, P[i], P[i + 1], P[i + 2], P[i + 3])); return d; }

// ------------------------------------------------------------------ kivikko
function rantaviiva() {
  const A = RIV.water, E = new Map(), key = (x, y) => Math.round(x * 20) + ',' + Math.round(y * 20);
  for (let i = 0; i < A.length; i += 6) {
    const v = [[A[i], A[i + 1]], [A[i + 2], A[i + 3]], [A[i + 4], A[i + 5]]];
    for (let k = 0; k < 3; k++) { const a = v[k], b = v[(k + 1) % 3], c = v[(k + 2) % 3], ka = key(...a), kb = key(...b), kk = ka < kb ? ka + '|' + kb : kb + '|' + ka;
      const e = E.get(kk); if (e) e.n++; else E.set(kk, { a, b, c, n: 1 }); }
  }
  const out = [];
  for (const e of E.values()) if (e.n === 1) {      // pitkät reunat paloiksi (enintään 4 m), jotta rajaukset osuvat oikeaan kohtaan
    const L = Math.hypot(e.b[0] - e.a[0], e.b[1] - e.a[1]), n = Math.max(1, Math.ceil(L / 4));
    for (let k = 0; k < n; k++) { const f0 = k / n, f1 = (k + 1) / n; out.push({ a: [e.a[0] + (e.b[0] - e.a[0]) * f0, e.a[1] + (e.b[1] - e.a[1]) * f0], b: [e.a[0] + (e.b[0] - e.a[0]) * f1, e.a[1] + (e.b[1] - e.a[1]) * f1], c: e.c }); } }
  return out;
}

function poisRajattu(mx, my) {
  if (mx > -372 && mx < -212 && my > 598 && my < 668) return true;                           // Kirjurinluodon uimaranta (hiekkaa, ei kiviä)
  if (polyDist(mx, my, RIV.quay) < 7) return true;                                            // Etelärannan muuri
  if (mx > 186 && mx < 266 && my > 462 && my < 482) return true;                              // alikulku Porinsillan eteläpään ali (index.html)
  for (const b of RIV.br) if (polyDist(mx, my, b.p) < b.w / 2 + 7) return true;               // sillat
  const ux = Math.sin(PSIL.head), uy = Math.cos(PSIL.head), dx = mx - PSIL.x, dy = my - PSIL.y, t = dx * ux + dy * uy, s = dx * uy - dy * ux;
  if (Math.abs(s) < PSIL.half + 8 && t > -20 && t < PSIL.len + 20) return true;              // Porinsilta
  if (mx < -2480 || mx > 2430 || my < -1650 || my > 1880) return true;                        // kartan reuna
  return false;
}

// korkeus o m maalle päin: seuraa maata, mutta enintään loivasti (1:2,5) vedenpinnasta ylös. Ennen kaista nousi suoraan maaston (6 m:n ruudukko)
// korkeudelle ja teki vesirajaan metrin kiviseinämän (omistaja 20.11.2026: "rantakivet vaikuttaa olevan huomattavasti korkeammalla kuin veden pinta").
const rantaZ = (x, y, o) => Math.min(Math.max(TZg(x, y) + 0.05, WL + 0.06 + o * 0.1), WL + 0.06 + o * 0.4);
const RIVIT = [-1.4, 0, 0.9, 1.9, 2.8];   // etäisyys rantaviivasta maalle päin (m); negatiivinen = veden alla
function kivikkoGeometria() {
  const P = [], D = [], I = [], U = [];
  let n = 0;
  for (const e of rantaviiva()) {
    const mx = (e.a[0] + e.b[0]) / 2, my = (e.a[1] + e.b[1]) / 2;
    if (poisRajattu(mx, my)) continue;
    let tx = e.b[0] - e.a[0], ty = e.b[1] - e.a[1]; const L = Math.hypot(tx, ty); if (L < 0.2) continue; tx /= L; ty /= L;
    let nx = ty, ny = -tx;                                                                   // normaali: kohti maata (pois kolmion kolmannesta kärjestä)
    if ((e.c[0] - mx) * nx + (e.c[1] - my) * ny > 0) { nx = -nx; ny = -ny; }
    const ext = 0.35, a = [e.a[0] - tx * ext, e.a[1] - ty * ext], b = [e.b[0] + tx * ext, e.b[1] + ty * ext];
    const base = n;
    for (const p of [a, b]) for (const o of RIVIT) {
      const x = p[0] + nx * o, y = p[1] + ny * o;
      let z;
      if (o < 0) z = WL - 0.55;
      else if (o === 0) z = WL + 0.03;
      else z = rantaZ(x, y, o);
      P.push(x, z, -y); U.push(x / TOISTO, y / TOISTO); D.push(o); n++;
    }
    const R = RIVIT.length;
    for (let k = 0; k < R - 1; k++) { const p0 = base + k, p1 = base + k + 1, q0 = base + R + k, q1 = base + R + k + 1; I.push(p0, q0, p1, p1, q0, q1); }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3));
  g.setAttribute('aRanta', new THREE.Float32BufferAttribute(D, 1));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(U, 2));
  g.setIndex(I);
  g.computeVertexNormals();
  g.computeBoundingSphere();
  return g;
}

// Pintakivikko: saumaton jokikivitekstuuri (Jokikivien saumaton tekstuuri, 20.11.2026) + siitä lasketut normal-, AO- ja karheuskartat
// (rantakivi_*.jpg). Yksi toisto = TOISTO m, toinen kierretty ja eri kokoinen näyte rikkoo toiston; märkä ja tumma vesirajassa, sammalta yläreunassa.
const TOISTO = 2.6;
const tx = (f, srgb = true) => { const t = new THREE.TextureLoader().load(new URL(f, import.meta.url).href); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; if (srgb) t.colorSpace = THREE.SRGBColorSpace; return t; };
let TEX = null; const tekstuurit = () => TEX || (TEX = { a: tx('./rantakivi_albedo.jpg'), n: tx('./rantakivi_normal.jpg', false), o: tx('./rantakivi_orm.jpg', false) });
const YHTEINEN = `
vec2 kh2(vec2 p) { p = vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3))); return fract(sin(p) * 43758.5453); }
float kh1(vec2 p) { return fract(sin(dot(p, vec2(41.3, 289.1))) * 43758.5453); }
float kno(vec2 p) { vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f); return mix(mix(kh1(i), kh1(i + vec2(1, 0)), f.x), mix(kh1(i + vec2(0, 1)), kh1(i + vec2(1, 1)), f.x), f.y); }`;
function kivikkoMateriaali() {
  const T = tekstuurit();
  const m = new THREE.MeshStandardMaterial({ map: T.a, normalMap: T.n, aoMap: T.o, roughnessMap: T.o, metalness: 0, roughness: 1, transparent: true, depthWrite: false,
    side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 });
  m.normalScale.set(1.3, 1.3);
  m.onBeforeCompile = sh => {
    sh.uniforms.uWL = { value: WL };
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nattribute float aRanta; varying float vR; varying vec3 vWk;')
      .replace('#include <project_vertex>', '#include <project_vertex>\nvR = aRanta; vWk = (modelMatrix * vec4(transformed, 1.0)).xyz;');
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>
varying float vR; varying vec3 vWk; uniform float uWL;` + YHTEINEN)
      .replace('#include <map_fragment>', `#include <map_fragment>
  vec2 P = vec2(vWk.x, -vWk.z);
  float above = vWk.y - uWL, wet = 1.0 - smoothstep(0.05, 0.4, above);
  {
    vec2 q = mat2(0.8, -0.6, 0.6, 0.8) * P / ${(TOISTO * 1.37).toFixed(2)} + 0.37;
    vec3 c2 = texture2D(map, q).rgb;
    float mixv = smoothstep(0.35, 0.65, kno(P * 0.12));
    diffuseColor.rgb = mix(diffuseColor.rgb, c2, mixv);
    diffuseColor.rgb *= 0.85 + 0.3 * kno(P * 0.05 + 3.1);                  // laajempi sävyvaihtelu
    diffuseColor.rgb = mix(diffuseColor.rgb, diffuseColor.rgb * vec3(0.5, 0.52, 0.48) + vec3(0.0, 0.012, 0.0), wet);
    diffuseColor.rgb = mix(diffuseColor.rgb, vec3(0.19, 0.24, 0.12), smoothstep(1.7, 2.7, vR) * smoothstep(0.45, 0.7, kno(P * 0.9)) * 0.75);   // sammal / ruoho
    float jit = kh1(floor(P * 1.3)) * 0.6;
    diffuseColor.a = 1.0 - smoothstep(1.9 + jit, 2.75, vR);
  }`)
      .replace('#include <roughnessmap_fragment>', '#include <roughnessmap_fragment>\n  roughnessFactor = mix(roughnessFactor, 0.28, wet * 0.85);');
  };
  m.customProgramCacheKey = () => 'ranta-kivikko-2';
  return m;
}

// Lohkareet: rantakivet_blender.obj:n 12 muotoa instansseina vesirajaan, osin veden alla. Pinta graniittimaista hienojakoista rakeisuutta
// samasta tekstuurista hyvin pienessä mittakaavassa (kolmitasoprojektio), väri MTL:n BeachStone_01..04 -sävyistä.
const KIVIVARIT = [[0.42, 0.40, 0.36], [0.34, 0.38, 0.40], [0.48, 0.43, 0.34], [0.39, 0.36, 0.35]];
function lohkareMateriaali() {
  const T = tekstuurit();
  const m = new THREE.MeshStandardMaterial({ color: 0xffffff, metalness: 0, roughness: 0.85 });
  m.onBeforeCompile = sh => {
    sh.uniforms.tKivi = { value: T.a }; sh.uniforms.uWL = { value: WL };
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 vWk; varying vec3 vWn;')
      .replace('#include <project_vertex>', '#include <project_vertex>\nvWk = (modelMatrix * instanceMatrix * vec4(transformed, 1.0)).xyz; vWn = normalize(mat3(modelMatrix * instanceMatrix) * objectNormal);');
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\nvarying vec3 vWk; varying vec3 vWn; uniform sampler2D tKivi; uniform float uWL;' + YHTEINEN)
      .replace('#include <map_fragment>', `#include <map_fragment>
  float above = vWk.y - uWL, wet = 1.0 - smoothstep(0.03, 0.3, above);
  {
    vec3 b = pow(abs(vWn), vec3(4.0)); b /= b.x + b.y + b.z;
    const float S = 3.2;                                                   // 1 / (0,31 m): tekstuurin kivet ovat ~1 cm:n rakeita
    vec3 g = texture2D(tKivi, vWk.zy * S).rgb * b.x + texture2D(tKivi, vWk.xz * S).rgb * b.y + texture2D(tKivi, vWk.xy * S).rgb * b.z;
    float l = dot(g, vec3(0.3, 0.55, 0.15));
    diffuseColor.rgb *= 0.35 + 1.9 * mix(vec3(l), g, 0.5);
    diffuseColor.rgb *= 0.85 + 0.3 * kno(vWk.xz * 1.7);
    diffuseColor.rgb = mix(diffuseColor.rgb, diffuseColor.rgb * vec3(0.48, 0.5, 0.46), wet);
    diffuseColor.rgb = mix(diffuseColor.rgb, vec3(0.2, 0.26, 0.12), smoothstep(0.55, 0.9, vWn.y) * smoothstep(0.6, 0.8, kno(vWk.xz * 2.3)) * 0.6 * (1.0 - wet));   // sammalta päällä
  }`)
      .replace('#include <roughnessmap_fragment>', '#include <roughnessmap_fragment>\n  roughnessFactor = mix(roughnessFactor, 0.25, wet * 0.9);');
  };
  m.customProgramCacheKey = () => 'ranta-lohkare-1';
  return m;
}

async function lohkareet(ryhma) {
  const { default: MUODOT } = await import('./rantakivet_mallit.js');
  const geos = MUODOT.map((m, k) => { const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(m.p, 3)); g.setIndex(m.i); g.computeVertexNormals();
    // epäsäännöllisyyttä: pinta kuprulle normaalin suuntaan (sileät kupolit näyttivät muovisilta)
    const P = g.attributes.position, N = g.attributes.normal, f = (x, y, z) => Math.sin(x * 9.1 + k) * Math.sin(y * 7.3 + 2 * k) * Math.sin(z * 8.7 - k) + 0.5 * Math.sin(x * 19 + z * 17 + k);
    for (let i = 0; i < P.count; i++) { const x = P.getX(i), y = P.getY(i), z = P.getZ(i), d = y < 0.02 ? 0 : f(x, y, z) * 0.035; P.setXYZ(i, x + N.getX(i) * d, y + N.getY(i) * d, z + N.getZ(i) * d); }
    g.computeVertexNormals(); return g; });
  let sd = 917; const rnd = () => (sd = (sd * 16807) % 2147483647) / 2147483647;
  const paikat = geos.map(() => []);
  const inCore = (x, y) => Math.abs(x) < 1012 && y > -947 && y < 1281;
  for (const e of rantaviiva()) {
    const mx = (e.a[0] + e.b[0]) / 2, my = (e.a[1] + e.b[1]) / 2; if (poisRajattu(mx, my)) continue;
    let tx_ = e.b[0] - e.a[0], ty_ = e.b[1] - e.a[1]; const L = Math.hypot(tx_, ty_); if (L < 0.2) continue; tx_ /= L; ty_ /= L;
    let nx = ty_, ny = -tx_; if ((e.c[0] - mx) * nx + (e.c[1] - my) * ny > 0) { nx = -nx; ny = -ny; }
    const tiheys = inCore(mx, my) ? 1 / 2 : 1 / 7;                                     // kiveä / m
    let n = L * tiheys; while (n > 0) { if (n < 1 && rnd() > n) break; n--;
      const f = rnd(), o = -0.7 + rnd() * 2.2, x = e.a[0] + tx_ * L * f + nx * o, y = e.a[1] + ty_ * L * f + ny * o;
      const r = rnd(), s = r < 0.75 ? 0.3 + rnd() * 0.35 : r < 0.95 ? 0.6 + rnd() * 0.35 : 0.95 + rnd() * 0.5;   // halkaisija m
      const zg = o <= 0 ? WL - 0.55 + (o + 1.4) / 1.4 * 0.58 : rantaZ(x, y, o);
      const sh = Math.floor(rnd() * geos.length), hy = s * (0.75 + rnd() * 0.35);
      paikat[sh].push([x, zg - hy * (0.15 + rnd() * 0.2), y, s * (0.85 + rnd() * 0.3), hy, s, rnd() * 6.283, Math.floor(rnd() * 4), 0.85 + rnd() * 0.3]); } }
  const mat = lohkareMateriaali(), M4 = new THREE.Matrix4(), Qn = new THREE.Quaternion(), E = new THREE.Euler(), V = new THREE.Vector3(), S = new THREE.Vector3(), C = new THREE.Color();
  let yht = 0;
  geos.forEach((g, k) => { const P = paikat[k]; if (!P.length) return;
    const im = new THREE.InstancedMesh(g, mat, P.length);
    P.forEach((p, i) => { E.set((rnd() - 0.5) * 0.25, p[6], (rnd() - 0.5) * 0.25); Qn.setFromEuler(E); im.setMatrixAt(i, M4.compose(V.set(p[0], p[1], -p[2]), Qn, S.set(p[3], p[4] / 0.45, p[5])));
      const c = KIVIVARIT[p[7]]; im.setColorAt(i, C.setRGB(c[0] * p[8], c[1] * p[8], c[2] * p[8])); });
    im.instanceMatrix.needsUpdate = true; im.instanceColor.needsUpdate = true; im.computeBoundingSphere(); im.frustumCulled = false; im.userData.noT = true; ryhma.add(im); yht += P.length; });
  return yht;
}

// ------------------------------------------------------------------ laiturit
// Mitattu ilmakuvasta: a = rannan pää, b = vesipää (karttametrit), w = leveys
const LAITURIT = [
  { a: [-68.0, 512.5], b: [-59.2, 557.8], w: 2.3 },
  { a: [-23.5, 508.8], b: [-16.1, 548.6], w: 2.3 },
  { a: [21.3, 503.3], b: [28.3, 537.5], w: 2.3 },
  { a: [166.6, 480.2], b: [170.2, 521.8], w: 2.2 },
];
const LAVA = { c: [81.6, 501.5], koko: [16.0, 12.5], kulma: -0.05, silta: [[81.4, 489.4], [81.4, 495.6]] };   // neliönmuotoinen ponttonilava

function lautaTekstuuri() {
  const c = document.createElement('canvas'); c.width = 256; c.height = 256; const x = c.getContext('2d');
  for (let i = 0; i < 16; i++) { const l = 105 + Math.floor(Math.random() * 35); x.fillStyle = `rgb(${l + 18},${l},${l - 22})`; x.fillRect(0, i * 16, 256, 15); x.fillStyle = 'rgba(40,30,20,.55)'; x.fillRect(0, i * 16 + 15, 256, 1);
    for (let k = 0; k < 6; k++) { x.fillStyle = 'rgba(60,45,30,.18)'; x.fillRect(Math.random() * 256, i * 16 + 2 + Math.random() * 10, 30 + Math.random() * 80, 1); } }
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t;
}

const PINNAT = [];   // kävelypinnat pelaajalle: { cx, cy, ux, uy, hl, hw, z0, z1 } (z0 -> z1 pituussuunnassa)
function pinta(ax, ay, bx, by, w, z0, z1) { const L = Math.hypot(bx - ax, by - ay); PINNAT.push({ cx: (ax + bx) / 2, cy: (ay + by) / 2, ux: (bx - ax) / L, uy: (by - ay) / L, hl: L / 2, hw: w / 2, z0, z1 }); }
function laiturit(ryhma) {
  const lauta = lautaTekstuuri();
  const puu = new THREE.MeshLambertMaterial({ map: lauta }), kelluke = new THREE.MeshLambertMaterial({ color: 0x3b3f42 }), teras = new THREE.MeshLambertMaterial({ color: 0x5d6064 }), musta = new THREE.MeshLambertMaterial({ color: 0x1e2022 });
  const DECK = WL + 0.45;
  const lisaa = (geo, mat, x, z, y, rot) => { const o = new THREE.Mesh(geo, mat); o.position.set(x, z, -y); o.rotation.y = rot; ryhma.add(o); return o; };
  const kansi = (cx, cy, L, W, rot, z) => {
    const g = new THREE.BoxGeometry(W, 0.18, L); const uv = g.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * W / 3, uv.getY(i) * L / 3);
    lisaa(g, puu, cx, z, cy, rot);
    lisaa(new THREE.BoxGeometry(W * 0.86, 0.5, L * 0.98), kelluke, cx, z - 0.33, cy, rot);           // kellukkeet
  };
  for (const l of LAITURIT) {
    const [ax, ay] = l.a, [bx, by] = l.b, L = Math.hypot(bx - ax, by - ay), ux = (bx - ax) / L, uy = (by - ay) / L, rot = Math.atan2(ux, -uy);
    const silta = 6.5, sx = ax + ux * silta, sy = ay + uy * silta;                                  // kulkusilta muurilta ponttonille
    const pL = L - silta, pcx = sx + ux * pL / 2, pcy = sy + uy * pL / 2;
    kansi(pcx, pcy, pL, l.w, rot, DECK); pinta(sx, sy, bx, by, l.w, DECK + 0.09, DECK + 0.09);
    const top = QUAY_WALK + 0.02, drop = top - DECK, len = Math.hypot(silta, drop); pinta(ax, ay, sx, sy, 1.4, top + 0.06, DECK + 0.06);
    const sg = new THREE.BoxGeometry(1.4, 0.12, len); const s = lisaa(sg, teras, ax + ux * silta / 2, (top + DECK) / 2, ay + uy * silta / 2, rot);
    s.rotation.order = 'YXZ'; s.rotation.x = Math.atan2(drop, silta);
    for (const sd of [-1, 1]) { const k = lisaa(new THREE.BoxGeometry(0.05, 0.05, len), musta, ax + ux * silta / 2 + uy * sd * 0.7, (top + DECK) / 2 + 0.9, ay + uy * silta / 2 - ux * sd * 0.7, rot); k.rotation.order = 'YXZ'; k.rotation.x = Math.atan2(drop, silta); }
    for (let d = 1.5; d < pL; d += 5) for (const sd of [-1, 1]) {                                   // kiinnityspollarit
      const x = sx + ux * d + uy * sd * (l.w / 2 - 0.15), y = sy + uy * d - ux * sd * (l.w / 2 - 0.15);
      lisaa(new THREE.CylinderGeometry(0.07, 0.09, 0.28, 8), musta, x, DECK + 0.23, y, 0); }
  }
  // neliön muotoinen lava
  kansi(LAVA.c[0], LAVA.c[1], LAVA.koko[1], LAVA.koko[0], LAVA.kulma, DECK);
  { const c = Math.cos(LAVA.kulma), sn = Math.sin(LAVA.kulma), h = LAVA.koko[1] / 2; pinta(LAVA.c[0] + sn * h, LAVA.c[1] - c * h, LAVA.c[0] - sn * h, LAVA.c[1] + c * h, LAVA.koko[0], DECK + 0.09, DECK + 0.09); }
  { const [[ax, ay], [bx, by]] = LAVA.silta, L = Math.hypot(bx - ax, by - ay), ux = (bx - ax) / L, uy = (by - ay) / L, rot = Math.atan2(ux, -uy);
    const top = QUAY_WALK + 0.02, drop = top - DECK, len = Math.hypot(L, drop); pinta(ax, ay, bx, by, 1.6, top + 0.06, DECK + 0.06);
    const s = lisaa(new THREE.BoxGeometry(1.6, 0.12, len), teras, (ax + bx) / 2, (top + DECK) / 2, (ay + by) / 2, rot); s.rotation.order = 'YXZ'; s.rotation.x = Math.atan2(drop, L); }
}

// ------------------------------------------------------------------ julkinen
export function luoRanta({ scene, laiturit: teeLaiturit = true }) {
  const ryhma = new THREE.Group(); ryhma.name = 'Ranta';
  const g = kivikkoGeometria();
  const kivet = new THREE.Mesh(g, kivikkoMateriaali()); kivet.renderOrder = 2; kivet.frustumCulled = false; ryhma.add(kivet);
  if (teeLaiturit) laiturit(ryhma);
  lohkareet(ryhma).then(n => { ryhma.traverse(o => { o.userData.noT = true; if (o.material) o.material.userData.noT = true; }); if (window.__ranta) window.__ranta.lohkareita = n; console.log(`[ranta] ${n} rantalohkaretta`); }).catch(e => console.log('[ranta] lohkareet', e));
  ryhma.traverse(o => { o.userData.noT = true; if (o.material) o.material.userData.noT = true; });   // absoluuttiset korkeudet, ei pelin maastonostoa
  scene.add(ryhma);
  window.__ranta = { ryhma, kivikkoKolmioita: g.index.count / 3 };
  window.__laituriZ = (x, y) => { if (x < -80 || x > 180 || y < 475 || y > 565) return null; let best = null;
    for (const p of PINNAT) { const dx = x - p.cx, dy = y - p.cy, a = dx * p.ux + dy * p.uy, b = dx * p.uy - dy * p.ux;
      if (Math.abs(a) <= p.hl && Math.abs(b) <= p.hw) { const z = p.z0 + (p.z1 - p.z0) * (a + p.hl) / (2 * p.hl); if (best === null || z > best) best = z; } }
    return best; };
  console.log(`[ranta] kivikkoa ${Math.round(g.index.count / 3)} kolmiota, ${LAITURIT.length + 1} laituria`);
  return ryhma;
}

if (typeof window !== 'undefined' && !window.__rantaKokeilu) {
  const odota = () => { const G = window.__game; if (G && G.scene) { luoRanta({ scene: G.scene }); return; } setTimeout(odota, 500); };
  odota();
}
