// Kokemäenjoen vesi – hybridi: tehty, elävä ja kohti merta virtaava vesi + ilmakuvan sävy kaukaa.
// Korvaa index.html:n vesipinnan materiaalin (waterify + ilmakuva) ILMAN muutoksia index.html:ään.
//
// Kokeilu pelissä (selaimen konsoli pelin sivulla, kun lento on alkanut):   await import('./vesi/vesi.js')
// Pysyvä kytkentä myöhemmin index.html:n loppuun:                          <script type="module" src="vesi/vesi.js"></script>
// Pois päältä / takaisin konsolista:                                         __vesi.paalla(false) / __vesi.paalla(true)
//
// Mitä tekee:
//  - virtauskenttä joen maskista (river.js): etäisyys yläjuoksulta (itä, x ~ 1530) kulkee uomaa pitkin kohti merta (länsi),
//    virtauksen suunta = sen gradientti. Virtaus kiertää Kirjurinluodon ja mutkat ja on nopein syvässä keskiuomassa.
//  - syvyys maastomallista (terrain.js: hg = todellinen pohja, wl = veden pinta): matalikot ruskeampia ja vaaleampia, syvänne tumma
//  - aallot: kaksivaiheinen virtauskartta (flow map) kuljettaa aaltokuviota virran mukana + tuulen väreily + Fresnel-taivas + auringon kimallus
//  - rannoilla vaahto/märkä reuna, joka peittää ilmakuvan ja maskin pienet erot
//  - hybridi: lähellä tehty vesi, kaukana (> 150 m) sekoitetaan ilmakuvan sumennettua sävyä, jotta joki istuu maisemaan
//  - window.__vesi: inRiver, virtaus(x, y), syvyys(x, y), korkeus(x, y) veneelle
import * as THREE from '../three.module.min.js';
import RIV from '../river.js';
import TER from '../terrain.js';

const RMX0 = -2504.1, RMY0 = -1671.6;          // river.js-maskin nurkka (sama kuin index.html)
const SUN = new THREE.Vector3(0.79, 0.81, -0.62).normalize();   // pelin aurinko (sun.position 0.79, 0.81, 0.62 -> maailman z = -y)

// ------------------------------------------------------------------ virtauskenttä (laskentaruudukko 8 m)
export function rakennaKentta() {
  const M = RIV.mask, raw = atob(M.b), bits = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) bits[i] = raw.charCodeAt(i);
  const inMask = (i, j) => { if (i < 0 || j < 0 || i >= M.nx || j >= M.ny) return false; const k = j * M.nx + i; return (bits[k >> 3] >> (7 - (k & 7))) & 1; };
  const S = 2, g = M.g * S, nx = Math.ceil(M.nx / S), ny = Math.ceil(M.ny / S), N = nx * ny;
  const wet = new Uint8Array(N);
  for (let j = 0; j < ny; j++) for (let i = 0; i < nx; i++) {
    let c = 0; for (let b = 0; b < S; b++) for (let a = 0; a < S; a++) c += inMask(i * S + a, j * S + b);
    wet[j * nx + i] = c >= 2 ? 1 : 0;
  }
  // etäisyys rannasta (monilahteinen BFS, 8-naapurusto, ~metreinä)
  const shore = new Float32Array(N).fill(1e9), q = new Int32Array(N); let qh = 0, qt = 0;
  for (let k = 0; k < N; k++) if (!wet[k]) { shore[k] = 0; q[qt++] = k; }
  const D8 = [[1, 0, 1], [-1, 0, 1], [0, 1, 1], [0, -1, 1], [1, 1, 1.414], [1, -1, 1.414], [-1, 1, 1.414], [-1, -1, 1.414]];
  // chamfer-etäisyys kahdella pyyhkäisyllä (tarkempi kuin BFS)
  for (let pass = 0; pass < 2; pass++) {
    const js = pass ? [ny - 1, -1, -1] : [0, ny, 1], is = pass ? [nx - 1, -1, -1] : [0, nx, 1];
    for (let j = js[0]; j !== js[1]; j += js[2]) for (let i = is[0]; i !== is[1]; i += is[2]) {
      const k = j * nx + i; if (!wet[k]) continue; let v = shore[k];
      for (const [dx, dy, w] of D8) { const a = i + dx, b = j + dy; if (a < 0 || b < 0 || a >= nx || b >= ny) { v = Math.min(v, w); continue; } v = Math.min(v, shore[b * nx + a] + w); }
      shore[k] = v;
    }
  }
  // geodeettinen etäisyys yläjuoksulta (itäisimmät märät sarakkeet) - Dijkstra-tyyppinen pyyhkäisy toistaen
  let imax = 0; for (let k = 0; k < N; k++) if (wet[k]) imax = Math.max(imax, k % nx);
  const dist = new Float32Array(N).fill(1e9);
  for (let k = 0; k < N; k++) if (wet[k] && k % nx >= imax - 3) dist[k] = 0;
  // tasainen hinta: etäisyysrintama on kohtisuorassa uomaa vastaan, joten gradientti kulkee uoman suuntaan
  const cost = k => 1;
  for (let it = 0; it < 12; it++) {
    let ch = 0;
    for (let pass = 0; pass < 2; pass++) {
      const js = pass ? [ny - 1, -1, -1] : [0, ny, 1], is = pass ? [nx - 1, -1, -1] : [0, nx, 1];
      for (let j = js[0]; j !== js[1]; j += js[2]) for (let i = is[0]; i !== is[1]; i += is[2]) {
        const k = j * nx + i; if (!wet[k]) continue; let v = dist[k];
        for (const [dx, dy, w] of D8) { const a = i + dx, b = j + dy; if (a < 0 || b < 0 || a >= nx || b >= ny) continue; const kk = b * nx + a; if (!wet[kk]) continue; const nv = dist[kk] + w * cost(k); if (nv < v) v = nv; }
        if (v < dist[k] - 1e-3) { dist[k] = v; ch++; }
      }
    }
    if (!ch) break;
  }
  // syvyys
  const THG = (() => { const r = atob(TER.hg), a = new Uint8Array(r.length); for (let i = 0; i < r.length; i++) a[i] = r.charCodeAt(i); return new Int16Array(a.buffer); })();
  const bed = (x, y) => { const fx = Math.min(TER.nx - 1.001, Math.max(0, (x - TER.x0) / TER.g)), fy = Math.min(TER.ny - 1.001, Math.max(0, (y - TER.y0) / TER.g)), i = Math.floor(fx), j = Math.floor(fy), u = fx - i, v = fy - j, k = j * TER.nx + i;
    return ((THG[k] * (1 - u) + THG[k + 1] * u) * (1 - v) + (THG[k + TER.nx] * (1 - u) + THG[k + TER.nx + 1] * u) * v) / 10; };
  // suunta = etäisyyskentän gradientti (keskeiserotus), tasoitus
  const fx = new Float32Array(N), fy = new Float32Array(N), sp = new Float32Array(N), dep = new Float32Array(N);
  const reach = k => wet[k] && dist[k] < 1e8;
  for (let j = 0; j < ny; j++) for (let i = 0; i < nx; i++) {
    const k = j * nx + i; if (!reach(k)) continue;
    const d = (a, b) => { const kk = b * nx + a; return a >= 0 && b >= 0 && a < nx && b < ny && reach(kk) ? dist[kk] : dist[k]; };
    let gx = d(i + 1, j) - d(i - 1, j), gy = d(i, j + 1) - d(i, j - 1);
    const L = Math.hypot(gx, gy) || 1; fx[k] = gx / L; fy[k] = gy / L;
    const x = RMX0 + (i + 0.5) * g, y = RMY0 + (j + 0.5) * g;
    dep[k] = Math.max(0, TER.wl - bed(x, y));
  }
  for (let it = 0; it < 4; it++) {          // tasoitus: virta ei nyi ruudukon mukaan
    const ax = fx.slice(), ay = fy.slice();
    for (let j = 1; j < ny - 1; j++) for (let i = 1; i < nx - 1; i++) {
      const k = j * nx + i; if (!reach(k)) continue; let sx = 0, sy = 0;
      for (let b = -1; b <= 1; b++) for (let a = -1; a <= 1; a++) { const kk = k + b * nx + a; if (reach(kk)) { sx += ax[kk]; sy += ay[kk]; } }
      const L = Math.hypot(sx, sy) || 1; fx[k] = sx / L; fy[k] = sy / L;
    }
  }
  for (let k = 0; k < N; k++) if (reach(k)) sp[k] = (0.25 + 0.55 * Math.min(1, dep[k] / 5)) * Math.min(1, shore[k] * g / 14);
  // RGBA: R,G = suunta, B = syvyys / 8 m, A = rannan etäisyys / 40 m
  const tex = new Uint8Array(N * 4);
  for (let k = 0; k < N; k++) {
    tex[k * 4] = Math.round((fx[k] * sp[k] * 0.5 + 0.5) * 255);
    tex[k * 4 + 1] = Math.round((fy[k] * sp[k] * 0.5 + 0.5) * 255);
    tex[k * 4 + 2] = Math.round(Math.min(1, dep[k] / 8) * 255);
    tex[k * 4 + 3] = Math.round(Math.min(1, shore[k] * g / 40) * 255);
  }
  const T = new THREE.DataTexture(tex, nx, ny, THREE.RGBAFormat);
  T.magFilter = T.minFilter = THREE.LinearFilter; T.needsUpdate = true;
  const at = (x, y) => { const i = Math.floor((x - RMX0) / g), j = Math.floor((y - RMY0) / g); return i < 0 || j < 0 || i >= nx || j >= ny ? -1 : j * nx + i; };
  return { tex: T, nx, ny, g, at, fx, fy, sp, dep, shore, wet, inMask: (x, y) => inMask(Math.floor((x - RMX0) / M.g), Math.floor((y - RMY0) / M.g)), W: nx * g, H: ny * g };
}

// ------------------------------------------------------------------ varjostin
const GLSL_NOISE = `
vec2 vhash(vec2 p) { p = vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3))); return -1.0 + 2.0 * fract(sin(p) * 43758.5453); }
// gradienttikohina + derivaatat (iq): x = arvo, yz = gradientti
vec3 gnoised(vec2 p) {
  vec2 i = floor(p), f = fract(p), u = f * f * f * (f * (f * 6.0 - 15.0) + 10.0), du = 30.0 * f * f * (f * (f - 2.0) + 1.0);
  vec2 ga = vhash(i), gb = vhash(i + vec2(1, 0)), gc = vhash(i + vec2(0, 1)), gd = vhash(i + vec2(1, 1));
  float va = dot(ga, f), vb = dot(gb, f - vec2(1, 0)), vc = dot(gc, f - vec2(0, 1)), vd = dot(gd, f - vec2(1, 1));
  return vec3(va + u.x * (vb - va) + u.y * (vc - va) + u.x * u.y * (va - vb - vc + vd),
    ga + u.x * (gb - ga) + u.y * (gc - ga) + u.x * u.y * (ga - gb - gc + gd) + du * (u.yx * (va - vb - vc + vd) + vec2(vb, vc) - va));
}
// aaltojen kallistus (gradientti) kahdella oktaavilla
vec2 waves(vec2 p) { vec3 a = gnoised(p); vec3 b = gnoised(p * 2.13 + vec2(5.2, 1.3)); return a.yz + 0.5 * b.yz * 2.13 * 0.5; }
`;

function teeMateriaali(kartta, K, uni) {
  const m = new THREE.MeshBasicMaterial({ map: kartta });
  m.onBeforeCompile = sh => {
    Object.assign(sh.uniforms, uni);
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 vW;')
      .replace('#include <project_vertex>', '#include <project_vertex>\nvW = (modelMatrix * vec4(transformed, 1.0)).xyz;');
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>
varying vec3 vW; uniform sampler2D uFlow; uniform vec4 uFR; uniform float uTime; uniform vec3 uSun; uniform float uPhotoMix;
${GLSL_NOISE}`).replace('#include <map_fragment>', `#include <map_fragment>
{
  vec2 P = vec2(vW.x, -vW.z);                               // pelin karttametrit (x itaan, y pohjoiseen)
  vec4 F = texture2D(uFlow, (P - uFR.xy) / uFR.zw);
  vec2 flow = F.rg * 2.0 - 1.0;                             // m/s-luokkaa, suunta kohti merta
  float depth = F.b * 8.0, shore = F.a * 40.0;
  // kaksivaiheinen virtauskartta: kuvio kulkee virran mukana eika veny
  float T = uTime / 6.0, p0 = fract(T), p1 = fract(T + 0.5), w0 = 1.0 - abs(2.0 * p0 - 1.0);
  vec2 adv0 = flow * (p0 - 0.5) * 6.0 * 2.2, adv1 = flow * (p1 - 0.5) * 6.0 * 2.2;
  vec2 q = P * 0.32;
  vec2 g1 = waves(q - adv0 * 0.32) * w0 + waves(q - adv1 * 0.32 + vec2(31.7, 11.3)) * (1.0 - w0);
  // pienet tuulen vareet (eivat seuraa virtaa) + suuri hidas maininki
  vec2 g2 = gnoised(P * 1.7 + uTime * vec2(0.55, 0.35)).yz * 0.35 + gnoised(P * 0.06 - uTime * vec2(0.02, 0.01)).yz * 0.6;
  float dist = length(cameraPosition - vW);
  float detail = 1.0 - smoothstep(250.0, 1400.0, dist);     // kaukana aallot tasoittuvat (ei valkoista kohinaa)
  vec2 gr = (g1 * 0.11 + g2 * 0.06) * detail;
  vec3 N = normalize(vec3(-gr.x, 1.0, gr.y));
  vec3 V = normalize(cameraPosition - vW);
  float fr = 0.02 + 0.98 * pow(1.0 - clamp(dot(N, V), 0.0, 1.0), 5.0);
  fr = clamp(fr * 1.15, 0.0, 0.95);
  vec3 R = reflect(-V, N);
  vec3 sky = mix(vec3(0.42, 0.52, 0.62), vec3(0.20, 0.33, 0.52), clamp(R.y, 0.0, 1.0));   // horisontti -> zeniitti (lineaarinen)
  float sp = pow(max(dot(R, uSun), 0.0), 700.0) * 3.0 + pow(max(dot(R, uSun), 0.0), 60.0) * 0.10;
  // vesi: humuspitoinen ruskehtava joki; matalikko vaalea ja ruskea, syvanne tumma
  vec3 deep = vec3(0.026, 0.036, 0.038), shallow = vec3(0.15, 0.125, 0.075);
  vec3 body = mix(deep, shallow, exp(-depth / 1.6));
  // hybridi: ilmakuvan savy kaukaa (mipmap-sumennus) - lahella tehty vesi
  vec3 photo = diffuseColor.rgb;
  float pm = (0.12 + 0.6 * smoothstep(150.0, 900.0, dist)) * uPhotoMix;
  body = mix(body, photo * 0.85, pm);
  vec3 col = mix(body, sky, fr * mix(1.0, 0.6, pm)) + sp * vec3(1.0, 0.92, 0.8) * detail;
  // ranta: vaahto/markaista, joka liikkuu hiukan
  float fn = gnoised(P * 0.9 + flow * uTime * 0.8).x * 0.5 + 0.5;
  float foam = (1.0 - smoothstep(0.6, 3.5 + fn * 2.0, shore)) * (0.55 + 0.45 * fn);
  col = mix(col, vec3(0.62, 0.60, 0.54), foam * 0.55);
  // ilmakuvan vaaleat kohteet (laiturit, ponttonit, veneet, poijut) jaavat nakyviin - vesi kuvassa on tummaa (lum < 0.07)
  float lum = dot(photo, vec3(0.2126, 0.7152, 0.0722));
  float obj = smoothstep(0.12, 0.17, lum);
  col = mix(col, photo, obj);
  diffuseColor.rgb = col;
}`);
    m.userData.shader = sh;
  };
  m.customProgramCacheKey = () => 'vesi-hybridi-1';
  m.needsUpdate = true;
  return m;
}

// ------------------------------------------------------------------ julkinen
export function luoVesi({ scene }) {
  const K = rakennaKentta();
  const uni = { uFlow: { value: K.tex }, uFR: { value: new THREE.Vector4(RMX0, RMY0, K.W, K.H) }, uTime: { value: 0 }, uSun: { value: SUN.clone() }, uPhotoMix: { value: 1 } };
  // pelin vesipinnat: tasaiset meshit veden korkeudella, joiden materiaalissa on ilmakuva
  const kohteet = [];
  scene.traverse(o => {
    if (!o.isMesh || !o.geometry || !o.material || !o.material.map || o.userData.vesi) return;
    const g = o.geometry; if (!g.boundingBox) g.computeBoundingBox();
    const b = g.boundingBox; if (Math.abs(b.min.y - TER.wl) < 1e-3 && Math.abs(b.max.y - TER.wl) < 1e-3) kohteet.push(o);
  });
  const vanhat = new Map();
  for (const o of kohteet) {
    vanhat.set(o, o.material);
    o.material = teeMateriaali(o.material.map, K, uni); o.material.userData.noT = true;
    o.userData.vesi = true;
    o.onBeforeRender = () => { uni.uTime.value = performance.now() / 1000; };
  }
  const API = {
    wl: TER.wl, kohteita: kohteet.length,
    inRiver: (x, y) => K.inMask(x, y),
    virtaus: (x, y) => { const k = K.at(x, y); return k < 0 ? [0, 0, 0] : [K.fx[k] * K.sp[k], K.fy[k] * K.sp[k], K.sp[k]]; },
    syvyys: (x, y) => { const k = K.at(x, y); return k < 0 ? 0 : K.dep[k]; },
    rannalle: (x, y) => { const k = K.at(x, y); return k < 0 ? 0 : K.shore[k] * K.g; },
    // pinnan korkeus veneelle (pieni, sama tuntuma kuin kuvassa): metrejä veden tason ympärillä
    korkeus: (x, y, t = performance.now() / 1000) => TER.wl + 0.04 * Math.sin(x * 0.35 + t * 1.3) * Math.cos(y * 0.29 - t * 1.1) + 0.025 * Math.sin((x + y) * 0.9 + t * 2.1),
    paalla: on => { for (const [o, vm] of vanhat) o.material = on ? o.userData.uusi : vm; },
    asetus: (nimi, arvo) => { if (nimi === 'ilmakuva') uni.uPhotoMix.value = arvo; },
    uniforms: uni,
  };
  for (const o of kohteet) o.userData.uusi = o.material;
  window.__vesi = API;
  console.log(`[vesi] ${kohteet.length} vesipintaa korvattu, virtauskenttä ${K.nx}×${K.ny} @ ${K.g} m`);
  return API;
}

// automaattinen kaynnistys pelissa
if (typeof window !== 'undefined' && !window.__vesiKokeilu) {
  const odota = () => { const G = window.__game; if (G && G.scene) { let n = 0; G.scene.traverse(o => { if (o.isMesh) n++; }); if (n > 50) { luoVesi({ scene: G.scene }); return; } } setTimeout(odota, 500); };
  odota();
}
