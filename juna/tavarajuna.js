// Tavarajunat Porin ratapihan läpi pelin kellon mukaan (21.11.2026). Kellonajat ja raiteet todellisesta liikenteestä (Digitraffic 7.–20.11.2026,
// juna/tavara_aikataulu.js): Porin aseman saapumis- ja lähtöaika pelin kellossa (window.__aika, aika/aika.js; 1 pelitunti = 10 min).
// Reitit rata/tavara_reitit.js (tools/rata/tavara_reitit.py). Viikonpäivä: pelin päivä 1 = maanantai.
// Kalusto: veturit dr18 (diesel) ja srt (sähkö), vaunut sgns (konttivaunu), zas (säiliö), roos / roos_t (tukkivaunu tyhjänä / tukkikuormassa), hbb (liukuseinä).
// Kokoonpanot arvotaan, koska Digitraffic ei julkaise tavarajunien kokoonpanoja.
// Kulunvarmistus: juna lähtee liikkeelle vain, jos sen reitti seuraavaan pysähdykseen on vapaa muista tavarajunista, ja IC-junan (juna/juna.js)
// kanssa yhteiselle osuudelle vain, kun IC seisoo laiturissa tai on poissa; IC odottaa (window.__tavara.estaaIC), kunnes tavarajuna on ohi.
import * as THREE from '../three.module.min.js';
import { GLTFLoader } from '../GLTFLoader.js';
import RATA from '../rata/rata_data.js';
import REITIT from '../rata/tavara_reitit.js';
import { yhdista } from './yhdista.js';

const TOUCH = typeof matchMedia !== 'undefined' && matchMedia('(pointer: coarse)').matches;
const SUF = TOUCH ? '_m' : '';
const OY0 = -3501.6, TUNTI_S = 600;
const MALLIT = { dr18: 0.5, srt: 0.6, sgns: 0.46, zas: 0.46, roos: 0.46, roos_t: 0.46, hbb: 0.46 };   // pyörän säde
const V_LINJA = 70 / 3.6, V_PIHA = 35 / 3.6, ACC = 0.22, DEC = 0.45;
const PIHA = { x: -450, y: -990, r: 1050 };   // ratapihan nopeusrajoitusalue (35 km/h)
const KALUSTO = {
  HVA: { veturi: 'srt', vaunut: ['zas', 'zas', 'hbb'], n: [8, 12] },                       // Harjavalta–Mäntyluoto: säiliö- ja liukuseinävaunut
  VKA: { veturi: 'dr18', vaunut: ['roos_t', 'roos_t', 'roos', 'sgns', 'hbb'], n: [6, 10] }, // Viinikka (Tampere): puu, kontit, liukuseinä
  VAIHTO: { veturi: 'dr18', vaunut: ['hbb', 'sgns', 'roos_t'], n: [2, 4] },                // vaihtotyö Mäntyluotoon
};
const ARKI = 'ma ti ke to pe';
// tulo = saapuu Poriin (läpikulkuraiteelle tai pääteraiteelle), lahto = lähtee Porista; pysakoi = jää raiteelle, lahtee = raiteella seisova juna lähtee
const OHJELMA = [
  { nro: 53803, paivat: 'ti ke to pe', reitti: 'SE-810', kalusto: 'VKA', tulo: '04:51', pysakoi: '810', mista: 'Tampereelta' },
  { nro: 65437, paivat: ARKI, lahtee: '808', reitti: '808-NW', lahto: '05:00', minne: 'Mäntyluotoon' },
  { nro: 11203, paivat: ARKI, lahtee: '804', reitti: '804-NW', lahto: '06:18', minne: 'Mäntyluotoon' },
  { nro: 3870, paivat: ARKI, reitti: 'NW-803-SE', kalusto: 'HVA', tulo: '07:43', lahto: '08:21', mista: 'Mäntyluodosta', minne: 'Harjavaltaan' },
  { nro: 3871, paivat: ARKI, reitti: 'SE-2-NW', kalusto: 'HVA', tulo: '10:01', lahto: '10:02', mista: 'Harjavallasta', minne: 'Mäntyluotoon' },
  { nro: 3860, paivat: 'la su', lahtee: '808', reitti: '808-SE', lahto: '10:26', minne: 'Harjavaltaan' },
  { nro: 53816, paivat: 'ti ke to pe', lahtee: '810', reitti: '810-SE', lahto: '11:01', minne: 'Tampereelle' },
  { nro: 3872, paivat: ARKI, reitti: 'NW-803-SE', kalusto: 'HVA', tulo: '11:44', lahto: '11:48', mista: 'Mäntyluodosta', minne: 'Harjavaltaan' },
  { nro: 3855, paivat: 'la su', reitti: 'SE-808', kalusto: 'HVA', tulo: '13:30', pysakoi: '808', mista: 'Harjavallasta' },   // oikeasti raide 804 (siellä seisoo 65436)
  { nro: 3873, paivat: ARKI, reitti: 'SE-2-NW', kalusto: 'HVA', tulo: '14:05', lahto: '14:06', mista: 'Harjavallasta', minne: 'Mäntyluotoon' },
  { nro: 3874, paivat: ARKI, reitti: 'NW-803-SE', kalusto: 'HVA', tulo: '15:43', lahto: '15:47', mista: 'Mäntyluodosta', minne: 'Harjavaltaan' },
  { nro: 3875, paivat: ARKI, reitti: 'SE-2-NW', kalusto: 'HVA', tulo: '18:07', lahto: '18:08', mista: 'Harjavallasta', minne: 'Mäntyluotoon' },
  { nro: 3876, paivat: ARKI, reitti: 'NW-803-SE', kalusto: 'HVA', tulo: '20:09', lahto: '20:20', mista: 'Mäntyluodosta', minne: 'Harjavaltaan' },
  { nro: 65436, paivat: ARKI, reitti: 'NW-804', kalusto: 'VAIHTO', tulo: '20:42', pysakoi: '804', mista: 'Mäntyluodosta' },
  { nro: 3877, paivat: 'ma ke pe', reitti: 'SE-808', kalusto: 'HVA', tulo: '22:32', pysakoi: '808', mista: 'Harjavallasta' },
  { nro: 3879, paivat: 'ti to', reitti: 'SE-808', kalusto: 'HVA', tulo: '22:38', pysakoi: '808', mista: 'Harjavallasta' },
];
const VKP = ['ma', 'ti', 'ke', 'to', 'pe', 'la', 'su'];
const h = s => { const [a, b] = s.split(':').map(Number); return a + b / 60; };
const klo = t => String(Math.floor(t)).padStart(2, '0') + '.' + String(Math.round((t % 1) * 60) % 60).padStart(2, '0');

// ---------------------------------------------------------------- reitit
function route(flat) {
  const n = flat.length / 3, P = []; let s = 0;
  for (let k = 0; k < n; k++) { const x = flat[k * 3], y = flat[k * 3 + 1], z = flat[k * 3 + 2]; if (k) s += Math.hypot(x - P[k - 1].x, y - P[k - 1].y); P.push({ x, y, z, s }); }
  const Z = P.map(p => p.z); for (let it = 0; it < 3; it++) for (let k = 1; k + 1 < n; k++) Z[k] = (Z[k - 1] + 2 * Z[k] + Z[k + 1]) / 4; P.forEach((p, k) => p.z = Z[k]);
  return { P, L: s };
}
function idx(R, s) { const P = R.P; let lo = 0, hi = P.length - 1; while (hi - lo > 1) { const m = (lo + hi) >> 1; if (P[m].s <= s) lo = m; else hi = m; } return lo; }
function at(R, s) {
  const P = R.P; s = Math.max(0, Math.min(R.L, s)); const lo = idx(R, s), hi = Math.min(P.length - 1, lo + 1);
  const a = P[lo], b = P[hi], f = (s - a.s) / Math.max(1e-6, b.s - a.s);
  return { x: a.x + (b.x - a.x) * f, y: a.y + (b.y - a.y) * f, z: a.z + (b.z - a.z) * f };
}
const sLahin = (R, p) => { let b = 0, bd = 1e18; for (const q of R.P) { const d = (q.x - p.x) ** 2 + (q.y - p.y) ** 2; if (d < bd) { bd = d; b = q.s; } } return b; };
// pisteet reitiltä väliltä [a, b] 4 m välein
function pisteet(R, a, b) { a = Math.max(0, a); b = Math.min(R.L, b); const out = []; for (let s = a; s <= b; s += 4) out.push(at(R, s)); return out; }
function ruudukko(P) { const G = new Map(); for (const p of P) { const k = Math.floor(p.x / 8) + ',' + Math.floor(p.y / 8); if (!G.has(k)) G.set(k, []); G.get(k).push(p); } return G; }
function osuu(G, p, r) { const gx = Math.floor(p.x / 8), gy = Math.floor(p.y / 8);
  for (let i = -1; i <= 1; i++) for (let j = -1; j <= 1; j++) for (const q of G.get((gx + i) + ',' + (gy + j)) || []) if (Math.hypot(q.x - p.x, q.y - p.y) < r) return true; return false; }
// IC-junan reitin kanssa yhteiset osuudet [a, b] (m reitin alusta)
function yhteiset(R, IC) {
  const G = ruudukko(pisteet(IC, 0, IC.L)), out = []; let a = null;
  for (const p of R.P) { const on = osuu(G, p, 2.0); if (on && a === null) a = p.s; if (!on && a !== null) { out.push([a - 30, p.s + 30]); a = null; } }
  if (a !== null) out.push([a - 30, R.L + 30]);
  return out;
}

async function luoTavarajunat(G) {
  const loader = new GLTFLoader(), base = new URL('.', import.meta.url).href;
  const src = {};
  for (const n of Object.keys(MALLIT)) {
    const o = (await loader.loadAsync(base + n + SUF + '.glb')).scene; src[n] = o;
    o.traverse(q => { if (!q.isMesh || !q.material || !q.material.map) return; const m = q.material; m.metalness = 0; m.metalnessMap = null; m.roughness = 0.7;
      m.color.setRGB(0.74, 0.74, 0.74); if (m.normalScale) m.normalScale.set(0.6, 0.6); m.needsUpdate = true; });
    o.traverse(q => { if (/^Wheel_[FRM]\d$/.test(q.name)) yhdista(q); });
    o.traverse(q => { if (/^Bogie_[FRM]$/.test(q.name)) yhdista(q, c => /^Wheel_/.test(c.name)); });
    yhdista(o, c => /^(Bogie_|Wheel_)/.test(c.name));
    const b = new THREE.Box3().setFromObject(o); o.userData.half = Math.max(-b.min.z, b.max.z) + 0.05;   // puskimesta keskelle
  }
  const IC = route(RATA.r['1']);
  const R = {}; for (const [k, v] of Object.entries(REITIT)) { const r = R[k] = route(v.p); r.nimi = k; r.yht = yhteiset(r, IC); r.info = v;
    r.lim = new Float32Array(r.P.length); r.P.forEach((p, i) => r.lim[i] = Math.hypot(p.x - PIHA.x, p.y - PIHA.y) < PIHA.r ? V_PIHA : V_LINJA); }
  const limAt = (Rt, s) => Rt.lim[idx(Rt, Math.max(0, Math.min(Rt.L, s)))];
  // arvioitu ajoaika reitin alusta kohtaan s (s, oikeaa aikaa)
  const ajoaika = (Rt, s) => { let t = 40; for (let k = 1; k < Rt.P.length && Rt.P[k].s <= s; k++) t += (Rt.P[k].s - Rt.P[k - 1].s) / Rt.lim[k]; return t; };
  const grp = new THREE.Group(); grp.name = 'tavarajunat'; G.scene.add(grp);
  const rnd = (a, b) => a + Math.floor(Math.random() * (b - a + 1));

  function auto(m, flip) {
    const o = src[m].clone(true); o.traverse(q => { q.userData.noT = true; if (q.isMesh) { q.frustumCulled = true; if (q.material) q.material.userData.noT = true; } });
    const w = new THREE.Group(); w.add(o); grp.add(w); w.visible = false;
    const B = [], W = []; o.traverse(q => { if (/^Bogie_[FRM]$/.test(q.name)) B.push(q); if (/^Wheel_[FRM]\d$/.test(q.name)) W.push(q); });
    return { m, flip, g: w, o, half: src[m].userData.half, r: MALLIT[m], bogies: B, wheels: W, bo: Math.max(2, ...B.map(b => Math.abs(b.position.z))) };
  }
  function kokoa(k) { const K = KALUSTO[k], cars = [auto(K.veturi, false)], n = rnd(K.n[0], K.n[1]);
    for (let i = 0; i < n; i++) cars.push(auto(K.vaunut[Math.floor(Math.random() * K.vaunut.length)], Math.random() < 0.5)); return cars; }
  function asettele(T) { let off = 0; for (const c of T.cars) { c.off = off + c.half; off += 2 * c.half; } T.LEN = off; }
  function place(T) {
    const Rt = T.R;
    for (const c of T.cars) {
      const sc = T.s - c.off, piilo = sc + c.half < 0 || sc - c.half > Rt.L; c.g.visible = !piilo; if (piilo) continue;
      const f = at(Rt, sc + c.bo), r = at(Rt, sc - c.bo);
      if (f.y < OY0 + 3 && r.y < OY0 + 3) { c.g.visible = false; continue; }
      const dx = f.x - r.x, dy = f.y - r.y, L = Math.hypot(dx, dy) || 1, yaw = Math.atan2(dx / L, -dy / L), pitch = Math.atan2(f.z - r.z, L);
      c.g.position.set((f.x + r.x) / 2, (f.z + r.z) / 2, -(f.y + r.y) / 2);
      c.g.rotation.set(-pitch, yaw + (c.flip ? Math.PI : 0), 0, 'YXZ');
      for (const b of c.bogies) { const bs = sc + b.position.z * (c.flip ? -1 : 1), a = at(Rt, bs + 1.5), z = at(Rt, bs - 1.5);
        b.rotation.y = Math.atan2(a.x - z.x, -(a.y - z.y)) - yaw; }
    }
  }
  const poista = T => { for (const c of T.cars) grp.remove(c.g); };

  // ---------------------------------------------------------------- kello
  let A = window.__aika;
  for (let i = 0; i < 40 && !A; i++) { await new Promise(r => setTimeout(r, 500)); A = window.__aika; }
  if (!A) {   // ei kelloa (aika.js puuttuu): oma kello klo 9 alkaen
    let t = 9, p = 1; A = { get t() { return t; }, get paiva() { return p; }, oma: dt => { t += dt / TUNTI_S; if (t >= 24) { t -= 24; p++; } } };
  }
  const viikonpaiva = p => VKP[((p - 1) % 7 + 7) % 7];
  const S = { junat: [], pysak: {}, tehty: new Set(), A };
  const near = () => { const s = G.S || {}, W = G.WALK || {}; const x = W.on ? W.x : s.x, y = W.on ? W.y : s.y; return Math.hypot(x + 450, y + 990) < 700; };
  const toast = t => { if (near() && G.toast) G.toast(t, 4); };
  const ic = () => window.__juna && window.__juna.T;
  window.__tavara = { S, R, OHJELMA, estaaIC: () => S.junat.some(T => T.lupa) };

  // junan tavoite: seuraava pysähdys (läpikulkuraide) tai reitin loppu
  const kohde = T => (T.seis !== null && T.seis > -1e8) ? T.seis : T.loppu;   // pysähdyksen jälkeen seis = -1e9
  function uusi(J, Rt, cars) {
    const T = { J, R: Rt, cars, v: 0, tila: 'odota', t: 0, msg: 0, lupa: false };
    asettele(T); T.seis = J.lahto && !J.lahtee && !J.pysakoi ? Math.min(Rt.L - 5, Rt.info.s[1] - 12) : null;   // läpikulkujuna pysähtyy raiteen loppupäähän
    T.loppu = J.pysakoi ? Rt.L - 1 : Rt.L + T.LEN + 20; return T;
  }
  function pysakoi(T, raide) { T.tila = 'park'; T.v = 0; T.lupa = false; T.paat = [at(T.R, T.s), at(T.R, T.s - T.LEN)]; place(T); S.pysak[raide] = T; S.junat = S.junat.filter(x => x !== T); }
  function lahde(J) {
    const P = S.pysak[J.lahtee]; if (!P) return null; delete S.pysak[J.lahtee];
    const Rt = R[J.reitti], sA = sLahin(Rt, P.paat[0]), sB = sLahin(Rt, P.paat[1]);
    let cars = P.cars;
    if (sB > sA) { const loco = cars[0], wag = cars.slice(1).reverse(); wag.forEach(c => c.flip = !c.flip); cars = [loco, ...wag]; }   // veturi kiertää toiseen päähän
    const T = uusi(J, Rt, cars); T.s = Math.max(sA, sB); return T;
  }
  // vapaa reitti: junan liikealue nykyisestä kohdasta seuraavaan pysähdykseen ei osu muiden junien varaamaan alueeseen
  function varattu(T) { return T.tila === 'ajo' ? pisteet(T.R, T.s - T.LEN, kohde(T)) : pisteet(T.R, T.s - T.LEN, T.s); }
  function vapaa(T) {
    const Gs = ruudukko(pisteet(T.R, T.s - T.LEN, kohde(T)));
    for (const Y of [...S.junat, ...Object.values(S.pysak)]) { if (Y === T) continue; for (const p of varattu(Y)) if (osuu(Gs, p, 2.6)) return false; }
    return true;
  }
  const tarvitseeLuvan = (T, a, b) => T.R.yht.some(([za, zb]) => za < b && zb > a - T.LEN);
  function lupaOK() { const t = ic(); if (!t) return true; return t.mode === 'away' || (t.mode === 'dwell' && t.t < 100); }

  // aikataulun junan käynnistyshetki (pelitunteina): saapuva juna lähtee kartan reunalta ajoajan verran ennen Porin aikaa
  function laukaisu(J) {
    if (J.lahtee) return h(J.lahto);
    const Rt = R[J.reitti], s = J.pysakoi ? Rt.L : Math.min(Rt.L, Rt.info.s[1] - 12);
    return h(J.tulo) - ajoaika(Rt, s) / TUNTI_S;
  }
  OHJELMA.forEach(J => J.t0 = laukaisu(J));

  function kaynnista(J) {
    let T;
    if (J.lahtee) { T = lahde(J); if (!T) return; }
    else { T = uusi(J, R[J.reitti], kokoa(J.kalusto)); T.s = 0; }
    S.junat.push(T); place(T);
  }
  // pelin alku tai kellon siirto: ratapihalle seisomaan ne junat, jotka aikataulun mukaan siellä nyt ovat
  function alusta() {
    for (const T of [...S.junat, ...Object.values(S.pysak)]) poista(T);
    S.junat = []; S.pysak = {}; S.tehty = new Set();
    const t = A.t, p = A.paiva, viim = {};
    for (let d = 6; d >= 0; d--) { const vp = viikonpaiva(p - d);
      for (const J of [...OHJELMA].sort((a, b) => h(a.tulo || a.lahto) - h(b.tulo || b.lahto))) {
        if (!J.paivat.includes(vp)) continue; const tt = h(J.lahtee ? J.lahto : J.tulo); if (d === 0 && tt > t) continue;
        if (J.pysakoi) viim[J.pysakoi] = J; if (J.lahtee) viim[J.lahtee] = null; } }
    for (const [raide, J] of Object.entries(viim)) if (J) { const T = uusi(J, R[J.reitti], kokoa(J.kalusto)); T.s = T.loppu; pysakoi(T, raide); }
    for (const J of OHJELMA) if (J.t0 <= t) S.tehty.add(p + ':' + J.nro);
    S.kello = [t, p];
  }

  function askel(dt) {
    if (A.oma) A.oma(dt);
    const t = A.t, p = A.paiva, [t0, p0] = S.kello;
    const hyppy = p === p0 ? (t < t0 - 0.01 || t > t0 + 0.25) : !(p === p0 + 1 && t < 0.25);
    if (hyppy) { alusta(); return; }
    S.kello = [t, p];
    // aikataulun junat liikkeelle
    const vp = viikonpaiva(p);
    for (const J of OHJELMA) { const k = p + ':' + J.nro; if (S.tehty.has(k) || !J.paivat.includes(vp) || t < J.t0) continue;
      S.tehty.add(k); if (t < J.t0 + 3) kaynnista(J); }
    for (const T of [...S.junat]) {
      if (T.tila === 'odota') {
        T.t += dt; T.chk = (T.chk || 0) - dt; if (T.chk > 0) { place(T); continue; } T.chk = 0.5;   // tarkistus 0,5 s välein
        const k = kohde(T);
        if (T.s <= 0 && T.t > 2 * TUNTI_S) { poista(T); S.junat = S.junat.filter(x => x !== T); continue; }   // ei päässyt kahteen tuntiin: peruttu
        if (!vapaa(T)) continue;
        if (tarvitseeLuvan(T, T.s, k)) { if (!lupaOK()) continue; T.lupa = true; }
        T.tila = 'ajo'; T.t = 0;
        if (T.J.lahto && T.s > 0) toast(`Tavarajuna ${T.J.nro} ${T.J.minne} lähtee${T.J.lahtee ? ' raiteelta ' + T.J.lahtee : ''} (${T.J.lahto})`);
      } else if (T.tila === 'ajo') {
        const k = kohde(T);
        let vt = Math.min(limAt(T.R, T.s), limAt(T.R, T.s - T.LEN));
        for (let d = 20; d < 700; d += 20) vt = Math.min(vt, Math.sqrt(limAt(T.R, T.s + d) ** 2 + 2 * DEC * d));
        if (k < T.R.L + 1) vt = Math.min(vt, Math.sqrt(Math.max(0, 2 * DEC * (k - T.s))));
        T.v = vt < T.v ? Math.max(vt, T.v - DEC * 1.6 * dt) : Math.min(vt, T.v + ACC * dt);
        T.s += T.v * dt;
        if (!T.msg && !T.J.lahtee && T.J.tulo && k - T.s < 1200 && k < T.R.L + 1) { T.msg = 1; const rd = T.J.pysakoi || (T.R.info.raide === '802' ? '2' : T.R.info.raide);
          toast(`Tavarajuna ${T.J.nro} ${T.J.mista}${T.J.minne ? ' ' + T.J.minne : ''} saapuu raiteelle ${rd} (${T.J.tulo})`); }
        if (T.lupa && !tarvitseeLuvan(T, T.s, k)) T.lupa = false;   // perä ohittanut yhteisen osuuden
        if (k < T.R.L + 1 && (k - T.s <= 0.05 || (k - T.s < 1.5 && T.v < 0.15))) {
          T.s = k; T.v = 0;
          if (k === T.seis) { T.tila = 'seis'; T.t = 0; }
          else if (T.J.pysakoi) { pysakoi(T, T.J.pysakoi); continue; }
        }
        if (T.s - T.LEN > T.R.L + 5) { poista(T); S.junat = S.junat.filter(x => x !== T); continue; }
      } else if (T.tila === 'seis') {
        T.t += dt; const L0 = h(T.J.lahto);
        if (T.t >= 15 && (t >= L0 || t < L0 - 12)) { T.tila = 'odota'; T.t = 0; T.seis = -1e9; }
      }
      const ds = T.v * dt; for (const c of T.cars) for (const w of c.wheels) w.rotation.x += ds / c.r * (c.flip ? -1 : 1);
      place(T);
    }
  }
  alusta();
  let last = performance.now();
  setInterval(() => { const now = performance.now(), dt = Math.min(0.1, (now - last) / 1000); last = now; askel(dt); }, 33);
  console.log('[tavarajuna] valmis, kello', klo(A.t), viikonpaiva(A.paiva), '· seisovat', Object.keys(S.pysak).join(',') || '-',
    '· seuraavat', OHJELMA.filter(J => J.t0 > A.t && J.paivat.includes(viikonpaiva(A.paiva))).slice(0, 3).map(J => J.nro + ' ' + klo(J.t0)).join(', '));
  return window.__tavara;
}

if (typeof window !== 'undefined') {
  const odota = () => { const G = window.__game; if (G && G.scene && window.__rata && window.__juna) { luoTavarajunat(G).catch(e => console.error('[tavarajuna]', e)); return; } setTimeout(odota, 900); };
  odota();
}
export { luoTavarajunat };
