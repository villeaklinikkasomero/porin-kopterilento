// Kokemäenjoen rannat: luonnonkivikko vesirajaan ja Etelärannan laiturit – ILMAN muutoksia index.html:n rakenteisiin.
//
// Kokeilu:   await import('./ranta/ranta.js')         Pysyvästi: <script type="module" src="ranta/ranta.js"></script>
//
// Kivikko: joen rajauksen (river.js, water-kolmiot) reunaan kaista pyöreitä luonnonkiviä, joka alkaa pinnan alta ja nousee penkalle.
//   Märkä ja tumma vesirajassa, kuiva ylempänä, reuna hajoaa ilmakuvaan. Ei Etelärannan muurin (RIV.quay), siltojen eikä kartan reunan kohdalle.
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
const QUAY_LOW = -1.05;    // index.html: Etelärannan alempi kävelytaso suhteessa maastonostoon (LOW)
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
  for (const e of E.values()) if (e.n === 1) out.push(e);
  return out;
}

function poisRajattu(mx, my) {
  if (polyDist(mx, my, RIV.quay) < 7) return true;                                            // Etelärannan muuri
  for (const b of RIV.br) if (polyDist(mx, my, b.p) < b.w / 2 + 7) return true;               // sillat
  const ux = Math.sin(PSIL.head), uy = Math.cos(PSIL.head), dx = mx - PSIL.x, dy = my - PSIL.y, t = dx * ux + dy * uy, s = dx * uy - dy * ux;
  if (Math.abs(s) < PSIL.half + 8 && t > -20 && t < PSIL.len + 20) return true;              // Porinsilta
  if (mx < -2480 || mx > 2430 || my < -1650 || my > 1880) return true;                        // kartan reuna
  return false;
}

const RIVIT = [-1.4, 0, 0.9, 1.9, 2.8];   // etäisyys rantaviivasta maalle päin (m); negatiivinen = veden alla
function kivikkoGeometria() {
  const P = [], D = [], I = [];
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
      else z = Math.max(TZg(x, y) + 0.05, WL + 0.08 + o * 0.12);
      P.push(x, z, -y); D.push(o); n++;
    }
    const R = RIVIT.length;
    for (let k = 0; k < R - 1; k++) { const p0 = base + k, p1 = base + k + 1, q0 = base + R + k, q1 = base + R + k + 1; I.push(p0, q0, p1, p1, q0, q1); }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3));
  g.setAttribute('aRanta', new THREE.Float32BufferAttribute(D, 1));
  g.setIndex(I);
  g.computeBoundingSphere();
  return g;
}

function kivikkoMateriaali() {
  const m = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, depthWrite: false, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 });
  m.onBeforeCompile = sh => {
    sh.uniforms.uWL = { value: WL };
    sh.uniforms.uSun = { value: new THREE.Vector3(0.79, 0.81, -0.62).normalize() };
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nattribute float aRanta; varying float vR; varying vec3 vWk;')
      .replace('#include <project_vertex>', '#include <project_vertex>\nvR = aRanta; vWk = (modelMatrix * vec4(transformed, 1.0)).xyz;');
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>
varying float vR; varying vec3 vWk; uniform float uWL; uniform vec3 uSun;
vec2 kh2(vec2 p) { p = vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3))); return fract(sin(p) * 43758.5453); }
float kh1(vec2 p) { return fract(sin(dot(p, vec2(41.3, 289.1))) * 43758.5453); }
// voronoi: x = F1, y = F2, zw = solun tunniste ja kiven keskipisteen suunta
vec4 kvor(vec2 p, out vec2 cell, out vec2 toC) {
  vec2 i = floor(p), f = fract(p); float d1 = 8.0, d2 = 8.0; cell = vec2(0); toC = vec2(0);
  for (int y = -1; y <= 1; y++) for (int x = -1; x <= 1; x++) { vec2 g = vec2(x, y), o = 0.15 + 0.7 * kh2(i + g), r = g + o - f; float d = dot(r, r);
    if (d < d1) { d2 = d1; d1 = d; cell = i + g; toC = r; } else if (d < d2) d2 = d; }
  return vec4(sqrt(d1), sqrt(d2), 0.0, 0.0);
}`).replace('#include <map_fragment>', `#include <map_fragment>
{
  vec2 P = vec2(vWk.x, -vWk.z);
  vec2 cell, toC; vec4 V = kvor(P * 2.3, cell, toC);
  float h = kh1(cell), r = 0.42 + 0.18 * h;
  float edge = V.y - V.x;                                    // kivien välinen rako
  float dome = sqrt(clamp(1.0 - (V.x / (r + 0.15)) * (V.x / (r + 0.15)), 0.0, 1.0));
  vec3 N = normalize(vec3(-toC.x * 1.4, dome + 0.35, toC.y * 1.4));
  float lit = 0.45 + 0.55 * clamp(dot(N, uSun), 0.0, 1.0);
  vec3 c1 = vec3(0.42, 0.40, 0.37), c2 = vec3(0.47, 0.38, 0.33), c3 = vec3(0.30, 0.29, 0.28), c4 = vec3(0.52, 0.50, 0.46);
  vec3 col = h < 0.3 ? c1 : h < 0.55 ? c2 : h < 0.8 ? c3 : c4;
  col *= 0.85 + 0.3 * kh1(cell + 7.1);
  col *= lit;
  col *= mix(0.25, 1.0, smoothstep(0.02, 0.12, edge));      // tummat raot
  // märkä vesirajassa (aallot kastelevat ~0,3 m) ja levää aivan rajassa, kuiva ylempänä
  float above = vWk.y - uWL;
  float wet = 1.0 - smoothstep(0.05, 0.35, above);
  col = mix(col, col * vec3(0.45, 0.47, 0.42) + vec3(0.0, 0.015, 0.0), wet);
  col += wet * pow(clamp(dot(reflect(-normalize(cameraPosition - vWk), N), uSun), 0.0, 1.0), 30.0) * 0.35;
  // kuivan kivikon yläreunassa hiukan sammalta ja ruohoa raoissa
  col = mix(col, vec3(0.20, 0.25, 0.13), smoothstep(1.6, 2.6, vR) * (1.0 - smoothstep(0.02, 0.12, edge)) * 0.8);
  // reuna sulautuu ilmakuvaan epätasaisesti
  float jit = kh1(floor(P * 1.3)) * 0.6;
  float a = 1.0 - smoothstep(1.9 + jit, 2.75, vR);
  diffuseColor = vec4(col, a);
}`);
  };
  m.customProgramCacheKey = () => 'ranta-kivikko-1';
  return m;
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
    kansi(pcx, pcy, pL, l.w, rot, DECK);
    const top = TZs(ax, ay) + QUAY_LOW + 0.02, drop = top - DECK, len = Math.hypot(silta, drop);
    const sg = new THREE.BoxGeometry(1.4, 0.12, len); const s = lisaa(sg, teras, ax + ux * silta / 2, (top + DECK) / 2, ay + uy * silta / 2, rot);
    s.rotation.order = 'YXZ'; s.rotation.x = Math.atan2(drop, silta);
    for (const sd of [-1, 1]) { const k = lisaa(new THREE.BoxGeometry(0.05, 0.05, len), musta, ax + ux * silta / 2 + uy * sd * 0.7, (top + DECK) / 2 + 0.9, ay + uy * silta / 2 - ux * sd * 0.7, rot); k.rotation.order = 'YXZ'; k.rotation.x = Math.atan2(drop, silta); }
    for (let d = 1.5; d < pL; d += 5) for (const sd of [-1, 1]) {                                   // kiinnityspollarit
      const x = sx + ux * d + uy * sd * (l.w / 2 - 0.15), y = sy + uy * d - ux * sd * (l.w / 2 - 0.15);
      lisaa(new THREE.CylinderGeometry(0.07, 0.09, 0.28, 8), musta, x, DECK + 0.23, y, 0); }
  }
  // neliön muotoinen lava
  kansi(LAVA.c[0], LAVA.c[1], LAVA.koko[1], LAVA.koko[0], LAVA.kulma, DECK);
  { const [[ax, ay], [bx, by]] = LAVA.silta, L = Math.hypot(bx - ax, by - ay), ux = (bx - ax) / L, uy = (by - ay) / L, rot = Math.atan2(ux, -uy);
    const top = TZs(ax, ay) + QUAY_LOW + 0.02, drop = top - DECK, len = Math.hypot(L, drop);
    const s = lisaa(new THREE.BoxGeometry(1.6, 0.12, len), teras, (ax + bx) / 2, (top + DECK) / 2, (ay + by) / 2, rot); s.rotation.order = 'YXZ'; s.rotation.x = Math.atan2(drop, L); }
}

// ------------------------------------------------------------------ julkinen
export function luoRanta({ scene, laiturit: teeLaiturit = true }) {
  const ryhma = new THREE.Group(); ryhma.name = 'Ranta';
  const g = kivikkoGeometria();
  const kivet = new THREE.Mesh(g, kivikkoMateriaali()); kivet.renderOrder = 2; kivet.frustumCulled = false; ryhma.add(kivet);
  if (teeLaiturit) laiturit(ryhma);
  ryhma.traverse(o => { o.userData.noT = true; if (o.material) o.material.userData.noT = true; });   // absoluuttiset korkeudet, ei pelin maastonostoa
  scene.add(ryhma);
  window.__ranta = { ryhma, kivikkoKolmioita: g.index.count / 3 };
  console.log(`[ranta] kivikkoa ${Math.round(g.index.count / 3)} kolmiota, ${LAITURIT.length + 1} laituria`);
  return ryhma;
}

if (typeof window !== 'undefined' && !window.__rantaKokeilu) {
  const odota = () => { const G = window.__game; if (G && G.scene) { luoRanta({ scene: G.scene }); return; } setTimeout(odota, 500); };
  odota();
}
