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
  { m: 'edo', half: 13.0, r: 0.46, flip: false },
  { m: 'ed', half: 13.0, r: 0.46, flip: false },
  { m: 'ed', half: 13.0, r: 0.46, flip: true },
  { m: 'ed', half: 13.0, r: 0.46, flip: false },
  { m: 'sr3', half: 9.25, r: 0.625, flip: false },
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
    // Meshy-korien PBR-materiaalit pelin kirkkaaseen valaistukseen (puolipallovalo 2,65, ei sävykartoitusta): ilman tätä valkoinen puhkesi
    // ja metallikartta tummensi kyljet laikukkaiksi (ympäristökarttaa ei ole)
    o.traverse(q => { if (!q.isMesh || !q.material || !q.material.map) return; const m = q.material; m.metalness = 0; m.metalnessMap = null; m.roughness = 0.62; m.side = THREE.FrontSide;   // sisältä kuori läpinäkyvä (sisätilat, ikkunat)
      m.color.setRGB(0.74, 0.74, 0.74); if (m.normalScale) m.normalScale.set(0.6, 0.6); m.needsUpdate = true; });
    // staattiset osat yhteen: runko, telit (ilman pyöriä), pyöräkerrat ja ovet kukin omanaan
    o.traverse(q => { if (/^Wheel_[FR]\d$/.test(q.name) || /^Door_[LR]\d+_[pm]\d+$/.test(q.name)) yhdista(q); });
    o.traverse(q => { if (/^Bogie_[FR]$/.test(q.name)) yhdista(q, c => /^Wheel_/.test(c.name)); });
    yhdista(o, c => /^(Bogie_|Door_|Wheel_)/.test(c.name)); }
  const R = route('1');
  const grp = new THREE.Group(); grp.name = 'juna'; G.scene.add(grp);
  const cars = CONSIST.map(c => {
    const o = src[c.m].clone(true); o.traverse(q => { q.userData.noT = true; if (q.isMesh) { q.frustumCulled = true; if (q.material) q.material.userData.noT = true; } });
    const w = new THREE.Group(); w.add(o); grp.add(w);
    const find = re => { const L = []; o.traverse(q => { if (re.test(q.name)) L.push(q); }); return L; };
    return { ...c, g: w, o, bf: o.getObjectByName('Bogie_F'), br: o.getObjectByName('Bogie_R'), wheels: find(/^Wheel_[FR]\d$/), doors: find(/^Door_[LR]\d+_[pm]\d+$/), M: new THREE.Matrix4(), Mi: new THREE.Matrix4(), open: { L: false, R: false }, bog: BOGIE[c.m] };
  });
  // vaunujen etäisyys keulasta (kytkimeltä kytkimelle)
  let off = 0; for (const c of cars) { c.off = off + c.half; off += 2 * c.half; } const LEN = off;
  const STOP = R.L - 1.0;            // ohjausvaunun keula pysähdyspaikalle (OSM: Pori, raide 1)
  // ovet: laiturin puoli selvitetään pysähdyspaikalla (rata.js:n laiturimonikulmiot)
  let doorSide = null;
  const T = { s: -LEN, v: V_LINE, mode: 'in', t: 0, doorT: 0, dir: 1 };
  window.__juna = { T, cars, R, LEN, STOP };   // (ab ja junaZ lisätään alempana)
  const tmp = new THREE.Vector3(), UP = new THREE.Vector3(0, 1, 0);
  function place() {
    for (const c of cars) {
      const sc = T.s - c.off;                                   // vaunun keskikohta reitillä
      const f = at(R, sc + c.bog), r = at(R, sc - c.bog), m = at(R, sc);
      const hidden = sc + c.half < 0 || f.y < OY0 + 3;
      c.g.visible = !hidden; if (hidden) continue;
      const dx = f.x - r.x, dy = f.y - r.y, L = Math.hypot(dx, dy) || 1, yaw = Math.atan2(dx / L, -dy / L), pitch = Math.atan2(f.z - r.z, L);
      c.g.position.set((f.x + r.x) / 2, (f.z + r.z) / 2, -(f.y + r.y) / 2);
      c.g.rotation.set(-pitch, yaw + (c.flip ? Math.PI : 0), 0, 'YXZ'); c.g.updateMatrix(); c.M.copy(c.g.matrix); c.Mi.copy(c.M).invert();
      // telit seuraavat raidetta
      for (const [b, sgn] of [[c.bf, 1], [c.br, -1]]) { if (!b) continue; const bs = sc + sgn * c.bog * (c.flip ? -1 : 1), a = at(R, bs + 1.5), z = at(R, bs - 1.5);
        const by = Math.atan2((a.x - z.x), -(a.y - z.y)); b.rotation.y = by - yaw; }
    }
  }
  function doors(open) {
    // liukuovet (meshy_juna.py: Door_<L|R><n>_<p|m><cm>): lehti ulos 6 cm ja kylkeä pitkin, vain laiturin puolella
    for (const c of cars) { c.open.L = c.open.R = false;
      for (const d of c.doors) { const u = d.userData;
        if (u.z0 === undefined) { u.z0 = d.position.z; u.x0 = d.position.x; const m = /_([pm])(\d+)$/.exec(d.name); u.sl = (m[1] === 'p' ? 1 : -1) * (+m[2]) / 100;
          d.geometry.computeBoundingBox(); u.side = d.geometry.boundingBox.min.x + d.geometry.boundingBox.max.x < 0 ? -1 : 1; }
        const ok = doorSide === null || u.side === doorSide[c.m + (c.flip ? 'f' : '')];
        d.position.z = u.z0 - (ok ? open * u.sl : 0); d.position.x = u.x0 + (ok ? open * u.side * 0.06 : 0);
        if (ok && open > 0.85) c.open[u.side < 0 ? 'L' : 'R'] = true; } }
  }
  function findDoorSide() {
    const plats = window.__rata && window.__rata.plats; if (!plats) return null; const res = {};
    const inPoly = (x, y, P) => { let c = false; for (let i = 0, j = P.length - 1; i < P.length; j = i++) { const [xi, yi] = P[i], [xj, yj] = P[j]; if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) c = !c; } return c; };
    for (const c of cars) { const key = c.m + (c.flip ? 'f' : ''); if (res[key] !== undefined) continue; c.g.updateMatrixWorld(true);
      for (const sd of [-1, 1]) { tmp.set(sd * 2.6, 1, 0); c.o.localToWorld(tmp); if (plats.some(p => inPoly(tmp.x, -tmp.z, p.poly))) res[key] = sd; } }
    return res;
  }
  // ---------------------------------------------------------------- sisätilat ja kyydissä matkustaminen (omistaja 21.11.: "kyytiin matkaan")
  // juna/ed_sisa.glb, edo_sisa.glb (tools/juna/juna_sisa.py) vaunun lapsiksi; kävelyalueet juna/sisa.json: [x0, x1, y0, y1, z(y0), z(y1), tyyppi]
  // vaunun omissa koordinaateissa (Blender: X leveys, Y pituus keula -Y; three: x, z = -Y). Pelaajan maa (index.html carGround -> window.__rataZ)
  // haetaan täältä: lähin lattia pelaajan omasta korkeudesta (ala- ja yläkerta päällekkäin), kuoren sisällä muualla ei voi kulkea.
  // Juna kuljettaa kyydissä olevaa pelaajaa (sijainti vaunun koordinaateissa ennen ja jälkeen siirron), kamera silmien korkeudelle.
  let sisaTila = 0; const ab = { c: null, t: 0, cam: null, msg: 0 }, rv = new THREE.Vector3(), rw = new THREE.Vector3();
  async function loadSisa() {
    sisaTila = 1;
    try { const J = await (await fetch(base + 'sisa.json')).json(), lo = {};
      for (const n of ['ed', 'edo']) { lo[n] = (await loader.loadAsync(base + n + '_sisa' + SUF + '.glb')).scene;
        lo[n].traverse(q => { q.userData.noT = true; if (q.isMesh && q.material) { const m = q.material; m.userData.noT = true; if (!m.emissiveMap && m.emissive && m.emissive.r < 0.1) m.color.multiplyScalar(0.82); m.metalness = Math.min(m.metalness, 0.3); } }); }
      for (const c of cars) { if (!lo[c.m]) continue; const s2 = lo[c.m].clone(true); s2.visible = false; c.o.add(s2); c.sisa = s2; c.rects = J[c.m].rects; }
      sisaTila = 2; console.log('[juna] sisätilat ladattu'); } catch (e) { console.warn('[juna] sisätilat', e); sisaTila = 3; } }
  const nbr = (c, end) => { const i = cars.indexOf(c), j = i + ((end < 0) !== !!c.flip ? -1 : 1), n = cars[j]; return n && n.rects ? n : null; };
  function junaZ(x, y) {
    const W = G.WALK; if (!W || !W.on || W.in || Math.hypot(W.x - x, W.y - y) > 2.5) return undefined;
    for (const c of cars) { if (!c.rects || !c.g.visible) continue;
      rv.set(x, W.z, -y).applyMatrix4(c.Mi); const X = rv.x, Y = -rv.z;
      if (Math.abs(X) > 1.96 || Math.abs(Y) > 13.1) continue;
      let best = null;
      for (const r of c.rects) { if (X < r[0] || X > r[1] || Y < r[2] || Y > r[3]) continue; const k = r[6];
        if (k === 'dL' && !c.open.L || k === 'dR' && !c.open.R) continue;
        if ((k === 'g+' || k === 'g-') && Math.abs(Y) > 12.7 && !nbr(c, k === 'g+' ? 1 : -1)) continue;
        const f = r[4] + (r[5] - r[4]) * (Y - r[2]) / Math.max(1e-6, r[3] - r[2]); rw.set(X, f, -Y).applyMatrix4(c.M);
        const d = Math.abs(rw.y - W.z); if (d < 0.5 && (!best || d < best.d)) best = { z: rw.y, d }; }
      if (best) { if (Math.abs(X) < 1.5) { ab.c = c; ab.t = performance.now(); } return best.z; }
      if (Math.abs(X) < 1.62 && Math.abs(Y) < 13.0) {      // kuoren sisällä muualla: seinä / penkit
        if (Math.hypot(W.x - x, W.y - y) > 0.05) return null;
        let nb = null; for (const r of c.rects) { if (r[6] && r[6][0] === 'd') continue; const cx = Math.max(r[0], Math.min(r[1], X)), cy = Math.max(r[2], Math.min(r[3], Y)), dd = Math.hypot(cx - X, cy - Y);
          const f = r[4] + (r[5] - r[4]) * (cy - r[2]) / Math.max(1e-6, r[3] - r[2]); rw.set(cx, f, -cy).applyMatrix4(c.M); if (Math.abs(rw.y - W.z) < 0.8 && (!nb || dd < nb.d)) nb = { z: rw.y, d: dd }; }
        return nb ? nb.z : null; }
    }
    return undefined;
  }
  { let wrapped = null; setInterval(() => { const f = window.__rataZ; if (f && f === wrapped) return; const prev = f;
      wrapped = window.__rataZ = (x, y, r) => { const j = junaZ(x, y); if (j !== undefined) return j; return prev ? prev(x, y, r) : null; }; }, 500); }   // 21.11.2026: viitekorkeus r eteenpäin (rata.js: sillan alla kulkeva ei nouse ratapenkalle)
  // kyydissä: pelaaja jonkin vaunun kuoren sisällä (vaunun koordinaateissa) – ei riipu kuvataajuudesta
  const inside = c => { const W = G.WALK; rv.set(W.x, W.z, -W.y).applyMatrix4(c.Mi); return Math.abs(rv.x) < 1.5 && Math.abs(rv.z) < 13.1 && rv.y > 0.6 && rv.y < 4.6; };
  const aboard = () => { const W = G.WALK; if (!W || !W.on || W.in) return false; if (ab.c && ab.c.g.visible && inside(ab.c)) return true;
    for (const c of cars) if (c.rects && c.g.visible && inside(c)) { ab.c = c; ab.t = performance.now(); return true; } return false; };
  Object.assign(window.__juna, { ab, junaZ, aboard });
  window.__walkBlock = (x, y) => junaZ(x, y) === null;
  window.__aboard = aboard;      // index.html stepWalk: kuoren sisällä vain käytävillä, ovista vain auki ollessa
  let last = performance.now(), msg = 0;
  const near = () => { const S = G.S || {}, W = G.WALK || {}; const x = W.on ? W.x : S.x, y = W.on ? W.y : S.y; return Math.hypot(x + 450, y + 990) < 450; };
  function step(dtf) {
    const now = performance.now(), dt = typeof dtf === 'number' ? dtf : Math.min(0.1, (now - last) / 1000); last = now;
    if (T.mode === 'in') {
      const toStop = STOP - T.s, lim = toStop < YARD_FROM ? V_YARD : V_LINE, brake = Math.sqrt(Math.max(0, 2 * DEC * toStop));
      const vt = Math.min(lim, brake); T.v = vt < T.v ? Math.max(vt, T.v - DEC * 1.6 * dt) : Math.min(vt, T.v + ACC * dt);
      T.s += T.v * dt;
      if (toStop < 300 && !msg && near()) { msg = 1; G.toast && G.toast('IC-juna Tampereelta saapuu raiteelle 1', 4); }
      if (toStop <= 0.05 || (toStop < 1.5 && T.v < 0.15)) { T.s = STOP; T.v = 0; T.mode = 'dwell'; T.t = 0; if (doorSide === null) doorSide = findDoorSide(); }
    } else if (T.mode === 'dwell') {
      T.t += dt; const tt = Math.min(T.t, DWELL - 0.01); T.doorT = Math.min(1, Math.max(0, tt < DWELL - 12 ? (tt - 4) / 3 : (DWELL - 8 - tt) / 3)); doors(T.doorT);
      if (T.t > DWELL - 40 && msg === 1 && near()) { msg = 2; G.toast && G.toast('IC-juna Tampereelle lähtee raiteelta 1', 4); }
      if (T.t >= DWELL && !(window.__tavara && window.__tavara.estaaIC())) { T.mode = 'out'; T.v = 0; doors(0); }   // tavarajuna yhteisellä raiteella: odota
    } else if (T.mode === 'out') {
      const fromStop = STOP - T.s, endS = LEN + 25, ride = aboard();
      const lim = Math.min(fromStop < YARD_FROM - LEN ? V_YARD : V_LINE, ride ? Math.sqrt(Math.max(0, 2 * DEC * (T.s - endS))) : 1e9); T.v = lim < T.v ? Math.max(lim, T.v - DEC * 1.6 * dt) : Math.min(lim, T.v + ACC * dt); T.s -= T.v * dt;
      if (ride && T.s <= endS + 1 && T.v < 0.2) { T.mode = 'term'; T.t = 0; T.v = 0; G.toast && G.toast('Kartan reuna: juna kääntyy takaisin Poriin', 4); }
      if (T.s < -5) { T.mode = 'away'; T.t = 0; }   // 21.11.: koko juna ulos kartalta (ennen ohjausvaunu ja Ed-vaunut jäivät näkyviin kartan reunalle)
    } else if (T.mode === 'term') {      // kyydissä kartan reunalle: odotus ja paluu asemalle (Tampereen suunta ei mahdu kartalle)
      T.t += dt; if (T.t > 25 && !(window.__tavara && window.__tavara.estaaIC())) { T.mode = 'in'; T.v = 0; msg = 0; }
    } else if (T.mode === 'away') {
      T.t += dt; if (T.t > AWAY && !(window.__tavara && window.__tavara.estaaIC())) { T.mode = 'in'; T.s = -10; T.v = V_LINE; msg = 0; }
    }
    // pyörät
    const ds = T.v * dt * (T.mode === 'out' ? -1 : 1);
    for (const c of cars) for (const w of c.wheels) w.rotation.x += ds / c.r * (c.flip ? -1 : 1);
    // kyydissä: pelaaja vaunun mukana
    const W = G.WALK, ride = aboard() ? ab.c : null; let ryaw = 0;
    if (ride) { rv.set(W.x, W.z, -W.y).applyMatrix4(ride.Mi); ryaw = ride.g.rotation.y; }
    place();
    if (ride && ride.g.visible) { rv.applyMatrix4(ride.M); W.x = rv.x; W.y = -rv.z; W.z = rv.y; let dy = ride.g.rotation.y - ryaw; dy = Math.atan2(Math.sin(dy), Math.cos(dy)); W.yaw -= dy;
      if (G.S) { G.S.x = W.x; G.S.y = W.y; } }
    // sisätilat näkyviin lähellä, kamera silmien korkeudelle kyytiin noustessa
    { const S = G.S || {}, px = W && W.on ? W.x : S.x, py = W && W.on ? W.y : S.y;
      if (!sisaTila && Math.hypot(px - cars[0].g.position.x, py + cars[0].g.position.z) < 600) loadSisa();
      for (const c of cars) if (c.sisa) c.sisa.visible = c.g.visible && Math.hypot(px - c.g.position.x, py + c.g.position.z) < 90;
      const on = aboard();
      if (on && ab.cam === null) { ab.cam = G.camMode; if (G.setCam) G.setCam(1); if (!ab.msg) { ab.msg = 1; G.toast && G.toast('Olet IC-junassa Pori–Tampere. Ovet aukeavat asemalla; kartan reunalla juna kääntyy takaisin.', 5); } }
      if (!on && ab.cam !== null && !(ab.c && performance.now() - ab.t < 1500)) { if (G.setCam && G.camMode === 1) G.setCam(ab.cam); ab.cam = null; } }
  }
  setInterval(step, 33);
  window.__juna.tick = step;
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
