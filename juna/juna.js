// IC-juna Pori–Tampere bottina: Sr3-veturi, kolme kaksikerrosvaunua (Ed) ja ohjausvaunu (Edo) – ILMAN muutoksia index.html:n rakenteisiin.
// Saapuu kaakosta (Tampereen suunta) kartan reunalta, hidastaa ratapihalla 35 km/h:iin, pysähtyy raiteelle 1 aseman laituriin,
// avaa ovet laiturin puolelle, seisoo ja lähtee takaisin Tampereen suuntaan veturi edellä (työntö-veto: tullessa ohjausvaunu edellä).
// Reitti: rata/rata_data.js (RATA.r, kiskon yläpinta 2 m välein). Mallit: juna/*.glb (tools: juna/build/juna_blender.py). Ks. juna/README.md.
import * as THREE from '../three.module.min.js';
import { GLTFLoader } from '../GLTFLoader.js';
import RATA from '../rata/rata_data.js';
import { yhdista } from './yhdista.js';

const TOUCH = typeof matchMedia !== 'undefined' && matchMedia('(pointer: coarse)').matches;
const SUF = TOUCH ? '_m' : '';
const OY0 = -3501.6;
// kokoonpano saapuessa keulasta alkaen; puolipituus puskimineen (m), pyörän säde, telien keskiöt (m keskeltä)
const CONSIST = [
  { m: 'edo', half: 13.4, r: 0.46, flip: false },
  { m: 'ed', half: 13.4, r: 0.46, flip: false },
  { m: 'ed', half: 13.4, r: 0.46, flip: true },
  { m: 'ed', half: 13.4, r: 0.46, flip: false },
  { m: 'sr3', half: 9.7, r: 0.625, flip: false },
];
const BOGIE = { sr3: 4.75, ed: 9.5, edo: 9.5 };
const V_LINE = 80 / 3.6, V_YARD = 35 / 3.6, ACC = 0.45, DEC = 0.6, DWELL = 150, AWAY = 150;
const YARD_FROM = 950;       // m ennen pysähdyspaikkaa: ratapihan nopeusrajoitus 35 km/h

// ---------------------------------------------------------------- reitti
function route(ref) {
  const R = RATA.r[ref]; const n = R.length / 3; const P = []; let s = 0;
  for (let k = 0; k < n; k++) { const x = R[k * 3], y = R[k * 3 + 1], z = R[k * 3 + 2]; if (k) s += Math.hypot(x - P[k - 1].x, y - P[k - 1].y); P.push({ x, y, z, s }); }
  // tasoitettu korkeus (vaunu ei saa nytkähdellä 2 m:n pisteiden välillä)
  const Z = P.map(p => p.z); for (let it = 0; it < 3; it++) for (let k = 1; k + 1 < n; k++) Z[k] = (Z[k - 1] + 2 * Z[k] + Z[k + 1]) / 4; P.forEach((p, k) => p.z = Z[k]);
  return { P, L: s };
}
function at(R, s) {
  const P = R.P; s = Math.max(0, Math.min(R.L, s)); let lo = 0, hi = P.length - 1;
  while (hi - lo > 1) { const m = (lo + hi) >> 1; if (P[m].s <= s) lo = m; else hi = m; }
  const a = P[lo], b = P[hi], f = (s - a.s) / Math.max(1e-6, b.s - a.s);
  return { x: a.x + (b.x - a.x) * f, y: a.y + (b.y - a.y) * f, z: a.z + (b.z - a.z) * f };
}

// ---------------------------------------------------------------- juna
async function luoJuna(G) {
  const loader = new GLTFLoader(), base = new URL('.', import.meta.url).href;
  const load = n => loader.loadAsync(base + n + SUF + '.glb').then(g => g.scene);
  const src = {}; for (const n of ['sr3', 'ed', 'edo']) { const o = await load(n); src[n] = o;
    // staattiset osat yhteen: runko, telit (ilman pyöriä), pyöräkerrat ja ovet kukin omanaan
    o.traverse(q => { if (/^Wheel_[FR]\d$/.test(q.name) || /^Door_[LR]\d$/.test(q.name)) yhdista(q); });
    o.traverse(q => { if (/^Bogie_[FR]$/.test(q.name)) yhdista(q, c => /^Wheel_/.test(c.name)); });
    yhdista(o, c => /^(Bogie_|Door_|Wheel_)/.test(c.name)); }
  const R = route('1');
  const grp = new THREE.Group(); grp.name = 'juna'; G.scene.add(grp);
  const cars = CONSIST.map(c => {
    const o = src[c.m].clone(true); o.traverse(q => { q.userData.noT = true; if (q.isMesh) { q.frustumCulled = true; if (q.material) q.material.userData.noT = true; } });
    const w = new THREE.Group(); w.add(o); grp.add(w);
    const find = re => { const L = []; o.traverse(q => { if (re.test(q.name)) L.push(q); }); return L; };
    return { ...c, g: w, o, bf: o.getObjectByName('Bogie_F'), br: o.getObjectByName('Bogie_R'), wheels: find(/^Wheel_[FR]\d$/), doors: find(/^Door_[LR]\d$/), bog: BOGIE[c.m] };
  });
  // vaunujen etäisyys keulasta (kytkimeltä kytkimelle)
  let off = 0; for (const c of cars) { c.off = off + c.half; off += 2 * c.half; } const LEN = off;
  const STOP = R.L - 1.0;            // ohjausvaunun keula pysähdyspaikalle (OSM: Pori, raide 1)
  // ovet: laiturin puoli selvitetään pysähdyspaikalla (rata.js:n laiturimonikulmiot)
  let doorSide = null;
  const T = { s: -LEN, v: V_LINE, mode: 'in', t: 0, doorT: 0, dir: 1 };
  window.__juna = { T, cars, R, LEN, STOP };
  const tmp = new THREE.Vector3(), UP = new THREE.Vector3(0, 1, 0);
  function place() {
    for (const c of cars) {
      const sc = T.s - c.off;                                   // vaunun keskikohta reitillä
      const f = at(R, sc + c.bog), r = at(R, sc - c.bog), m = at(R, sc);
      const hidden = sc + c.half < 0 || f.y < OY0 + 3;
      c.g.visible = !hidden; if (hidden) continue;
      const dx = f.x - r.x, dy = f.y - r.y, L = Math.hypot(dx, dy) || 1, yaw = Math.atan2(dx / L, -dy / L), pitch = Math.atan2(f.z - r.z, L);
      c.g.position.set((f.x + r.x) / 2, (f.z + r.z) / 2, -(f.y + r.y) / 2);
      c.g.rotation.set(-pitch, yaw + (c.flip ? Math.PI : 0), 0, 'YXZ');
      // telit seuraavat raidetta
      for (const [b, sgn] of [[c.bf, 1], [c.br, -1]]) { if (!b) continue; const bs = sc + sgn * c.bog * (c.flip ? -1 : 1), a = at(R, bs + 1.5), z = at(R, bs - 1.5);
        const by = Math.atan2((a.x - z.x), -(a.y - z.y)); b.rotation.y = by - yaw; }
    }
  }
  function doors(open) {
    for (const c of cars) for (const d of c.doors) { if (d.userData.x0 === undefined) d.userData.x0 = d.position.z;
      const side = d.position.x < 0 ? -1 : 1, ok = doorSide === null || side === doorSide[c.m + (c.flip ? 'f' : '')];
      d.position.z = d.userData.x0 + (ok ? open * 0.72 * (d.name.endsWith('1') ? 1 : -1) : 0); d.position.x = (d.userData.px0 ?? (d.userData.px0 = d.position.x)) + (ok ? open * Math.sign(d.position.x) * 0.06 : 0); }
  }
  function findDoorSide() {
    const plats = window.__rata && window.__rata.plats; if (!plats) return null; const res = {};
    const inPoly = (x, y, P) => { let c = false; for (let i = 0, j = P.length - 1; i < P.length; j = i++) { const [xi, yi] = P[i], [xj, yj] = P[j]; if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) c = !c; } return c; };
    for (const c of cars) { const key = c.m + (c.flip ? 'f' : ''); if (res[key] !== undefined) continue; c.g.updateMatrixWorld(true);
      for (const sd of [-1, 1]) { tmp.set(sd * 2.6, 1, 0); c.o.localToWorld(tmp); if (plats.some(p => inPoly(tmp.x, -tmp.z, p.poly))) res[key] = sd; } }
    return res;
  }
  let last = performance.now(), msg = 0;
  const near = () => { const S = G.S || {}, W = G.WALK || {}; const x = W.on ? W.x : S.x, y = W.on ? W.y : S.y; return Math.hypot(x + 450, y + 990) < 450; };
  function step() {
    const now = performance.now(), dt = Math.min(0.1, (now - last) / 1000); last = now;
    if (T.mode === 'in') {
      const toStop = STOP - T.s, lim = toStop < YARD_FROM ? V_YARD : V_LINE, brake = Math.sqrt(Math.max(0, 2 * DEC * toStop));
      const vt = Math.min(lim, brake); T.v = vt < T.v ? Math.max(vt, T.v - DEC * 1.6 * dt) : Math.min(vt, T.v + ACC * dt);
      T.s += T.v * dt;
      if (toStop < 300 && !msg && near()) { msg = 1; G.toast && G.toast('IC-juna Tampereelta saapuu raiteelle 1', 4); }
      if (toStop <= 0.05 || (toStop < 1.5 && T.v < 0.15)) { T.s = STOP; T.v = 0; T.mode = 'dwell'; T.t = 0; if (doorSide === null) doorSide = findDoorSide(); }
    } else if (T.mode === 'dwell') {
      T.t += dt; T.doorT = Math.min(1, Math.max(0, T.t < DWELL - 12 ? (T.t - 4) / 3 : (DWELL - 8 - T.t) / 3)); doors(T.doorT);
      if (T.t > DWELL - 40 && msg === 1 && near()) { msg = 2; G.toast && G.toast('IC-juna Tampereelle lähtee raiteelta 1', 4); }
      if (T.t >= DWELL) { T.mode = 'out'; T.v = 0; doors(0); }
    } else if (T.mode === 'out') {
      const fromStop = STOP - T.s, lim = fromStop < YARD_FROM - LEN ? V_YARD : V_LINE; T.v = Math.min(lim, T.v + ACC * dt); T.s -= T.v * dt;
      if (T.s - LEN < -40) { T.mode = 'away'; T.t = 0; }
    } else if (T.mode === 'away') {
      T.t += dt; if (T.t > AWAY) { T.mode = 'in'; T.s = -10; T.v = V_LINE; msg = 0; }
    }
    // pyörät
    const ds = T.v * dt * (T.mode === 'out' ? -1 : 1);
    for (const c of cars) for (const w of c.wheels) w.rotation.x += ds / c.r * (c.flip ? -1 : 1);
    place();
  }
  setInterval(step, 33);
  // aloitus: juna jo laiturissa, jotta pelaaja näkee sen heti asemalla
  T.s = STOP; T.mode = 'dwell'; T.t = 20; place(); doorSide = findDoorSide();
  console.log('[juna] IC-juna valmis, reitti', Math.round(R.L), 'm, pituus', Math.round(LEN), 'm, ovet', JSON.stringify(doorSide));
  return window.__juna;
}

if (typeof window !== 'undefined') {
  const odota = () => { const G = window.__game; if (G && G.scene && window.__rata) { luoJuna(G).catch(e => console.error('[juna]', e)); return; } setTimeout(odota, 700); };
  odota();
}
export { luoJuna };
