// IC-junat Pori–Tampere bottina pelin kellon mukaan (21.11.2026): kolme junayksikköä (Sr3-veturi, ohjausvaunu Edo ja kaksikerrosvaunut Ed)
// ajavat oikeita Porin aikatauluja (Digitraffic 14.–20.11.2026, OHJELMA alla) pelin kellosta (window.__aika, aika/aika.js; 1 pelitunti = 10 min).
// Saapuu kaakosta (Tampereen suunta) kartan reunalta, hidastaa ratapihalla 35 km/h:iin, pysähtyy raiteelle 1 tai 2 aseman laituriin,
// avaa ovet laiturin puolelle ja lähtee aikataulun mukaan takaisin Tampereen suuntaan veturi edellä (työntö-veto: tullessa ohjausvaunu edellä).
// Yöksi Poriin jää kolme junaa (raide 1 ja kaksi peräkkäin raiteelle 2); aamulla ne lähtevät 5.17, 6.12 ja 7.17. Samalle raiteelle tuleva juna
// pysähtyy edellisen taakse, ja raiteelta lähtee takimmainen. Yhteisellä pääraiteella liikkuu kerrallaan yksi juna (IC tai tavarajuna).
// Reitit: rata/rata_data.js (RATA.r '1' ja '2', kiskon yläpinta 2 m välein). Mallit: juna/*.glb (tools/juna/meshy_juna.py). Ks. juna/README.md.
import * as THREE from '../three.module.min.js';
import { GLTFLoader } from '../GLTFLoader.js';
import RATA from '../rata/rata_data.js';
import { yhdista } from './yhdista.js';

const TOUCH = typeof matchMedia !== 'undefined' && matchMedia('(pointer: coarse)').matches;
const SUF = TOUCH ? '_m' : '';
const OY0 = -3501.6, TUNTI_S = 600;
// junayksiköt: kokoonpano saapuessa keulasta alkaen (oikeasti Edo + CEd + Edfs, 99 m, tai neljä vaunua, 125 m)
const YKSIKOT = [['edo', 'ed', 'ed', 'ed'], ['edo', 'ed', 'ed'], ['edo', 'ed', 'ed']];
const MITAT = { edo: { half: 13.0, r: 0.46 }, ed: { half: 13.0, r: 0.46 }, sr3: { half: 9.25, r: 0.625 } };
const BOGIE = { sr3: 4.75, ed: 9.5, edo: 9.5 };
const V_LINE = 80 / 3.6, V_YARD = 35 / 3.6, ACC = 0.45, DEC = 0.6;
const YARD_FROM = 950;       // m ennen pysähdyspaikkaa: ratapihan nopeusrajoitus 35 km/h
// Porin aikataulu (s = saapuu Tampereelta, l = lähtee Tampereelle; raide; H = Helsingin juna). Sama joka arkipäivä 16.–20.11.2026.
const ARKI = 'l05:17/2/460 l06:12/1/462 l07:17/1/466 s07:47/1/477 l08:04/1/476 s09:40/1/461 l10:03/1/464 s11:48/1/463 l12:12/1/474 s13:44/1/465 l14:12/1/468 '
  + 's15:44/1/467 l16:12/1/470 s17:44/1/469 l18:12/1/472 s19:44/1/471 s21:45/2/473 s23:49/2/475';
const OHJELMA = {
  ma: ARKI, ti: ARKI, ke: ARKI, to: ARKI, pe: ARKI,
  la: 'l05:17/2/164H l06:12/1/462 l07:17/2/466 s09:40/1/461 l10:03/1/464 s13:44/1/465 l14:12/1/468 s15:44/1/467 l16:12/1/470 s17:44/1/175H l18:12/1/186H s19:44/1/471 s23:49/2/475',
  su: 'l07:17/2/466 l10:03/1/464 s13:44/1/465 l14:12/1/468 s15:44/1/467 l16:12/1/470 s17:44/1/469 l18:12/1/472 s19:44/1/471 s21:45/2/473 s23:49/2/475',
};
const VKP = ['ma', 'ti', 'ke', 'to', 'pe', 'la', 'su'];
const _tap = {};
const tapahtumat = vp => _tap[vp] || (_tap[vp] = OHJELMA[vp].split(' ').map(x => { const m = /^([sl])(\d\d):(\d\d)\/(\d)\/(\d+)(H?)$/.exec(x);
  return { tulo: m[1] === 's', h: +m[2] + m[3] / 60, aika: m[2] + '.' + m[3], raide: m[4], nro: +m[5], hki: !!m[6] }; }));

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

// ---------------------------------------------------------------- junat
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
  const RT = { 1: route('1'), 2: route('2') };
  const grp = new THREE.Group(); grp.name = 'juna'; G.scene.add(grp);
  const cars = [];      // kaikkien yksiköiden vaunut (sisätilat, kyydissä, törmäykset: src/js/090_tormaykset.js)
  const sets = YKSIKOT.map((V, id) => {
    const U = { id, cars: [], T: { s: 0, v: 0, mode: 'away', t: 0, doorT: 0 }, R: RT[1], raide: '1', STOP: RT[1].L - 1, doorSide: null, msg: 0, job: null, lahto: null, jarj: 0 };
    const kok = [...V, 'sr3'].map((m, i) => ({ m, ...MITAT[m], flip: m === 'ed' && i % 2 === 0 }));
    for (const c of kok) {
      const o = src[c.m].clone(true); o.traverse(q => { q.userData.noT = true; if (q.isMesh) { q.frustumCulled = true; if (q.material) q.material.userData.noT = true; } });
      const w = new THREE.Group(); w.add(o); grp.add(w); w.visible = false;
      const find = re => { const L = []; o.traverse(q => { if (re.test(q.name)) L.push(q); }); return L; };
      const car = { ...c, set: U, g: w, o, bf: o.getObjectByName('Bogie_F'), br: o.getObjectByName('Bogie_R'), wheels: find(/^Wheel_[FR]\d$/), doors: find(/^Door_[LR]\d+_[pm]\d+$/), M: new THREE.Matrix4(), Mi: new THREE.Matrix4(), open: { L: false, R: false }, bog: BOGIE[c.m] };
      U.cars.push(car); cars.push(car);
    }
    // vaunujen etäisyys keulasta (kytkimeltä kytkimelle)
    let off = 0; for (const c of U.cars) { c.off = off + c.half; off += 2 * c.half; } U.LEN = off;
    return U;
  });
  const tmp = new THREE.Vector3();
  function place(U) {
    const T = U.T, R = U.R;
    for (const c of U.cars) {
      const sc = T.s - c.off;                                   // vaunun keskikohta reitillä
      const f = at(R, sc + c.bog), r = at(R, sc - c.bog);
      const hidden = T.mode === 'away' || T.mode === 'odota' || sc + c.half < 0 || f.y < OY0 + 3;
      c.g.visible = !hidden; if (hidden) continue;
      const dx = f.x - r.x, dy = f.y - r.y, L = Math.hypot(dx, dy) || 1, yaw = Math.atan2(dx / L, -dy / L), pitch = Math.atan2(f.z - r.z, L);
      c.g.position.set((f.x + r.x) / 2, (f.z + r.z) / 2, -(f.y + r.y) / 2);
      c.g.rotation.set(-pitch, yaw + (c.flip ? Math.PI : 0), 0, 'YXZ'); c.g.updateMatrix(); c.M.copy(c.g.matrix); c.Mi.copy(c.M).invert();
      // telit seuraavat raidetta
      for (const [b, sgn] of [[c.bf, 1], [c.br, -1]]) { if (!b) continue; const bs = sc + sgn * c.bog * (c.flip ? -1 : 1), a = at(R, bs + 1.5), z = at(R, bs - 1.5);
        const by = Math.atan2((a.x - z.x), -(a.y - z.y)); b.rotation.y = by - yaw; }
    }
  }
  function doors(U, open) {
    // liukuovet (meshy_juna.py: Door_<L|R><n>_<p|m><cm>): lehti ulos 6 cm ja kylkeä pitkin, vain laiturin puolella
    for (const c of U.cars) { c.open.L = c.open.R = false;
      for (const d of c.doors) { const u = d.userData;
        if (u.z0 === undefined) { u.z0 = d.position.z; u.x0 = d.position.x; const m = /_([pm])(\d+)$/.exec(d.name); u.sl = (m[1] === 'p' ? 1 : -1) * (+m[2]) / 100;
          d.geometry.computeBoundingBox(); u.side = d.geometry.boundingBox.min.x + d.geometry.boundingBox.max.x < 0 ? -1 : 1; }
        const ok = U.doorSide !== null && c.ds !== undefined && u.side === c.ds;
        d.position.z = u.z0 - (ok ? open * u.sl : 0); d.position.x = u.x0 + (ok ? open * u.side * 0.06 : 0);
        if (ok && open > 0.85) c.open[u.side < 0 ? 'L' : 'R'] = true; } }
  }
  // laiturin puoli vaunuittain pysähdyspaikalla (rata.js:n laiturimonikulmiot); takimmaisen junan vaunut voivat olla laiturin ulkopuolella
  function findDoorSide(U) {
    const plats = window.__rata && window.__rata.plats; if (!plats) return null;
    const inPoly = (x, y, P) => { let c = false; for (let i = 0, j = P.length - 1; i < P.length; j = i++) { const [xi, yi] = P[i], [xj, yj] = P[j]; if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) c = !c; } return c; };
    for (const c of U.cars) { c.ds = undefined; c.g.updateMatrixWorld(true);
      for (const sd of [-1, 1]) { tmp.set(sd * 2.6, 1, 0); c.o.localToWorld(tmp); if (plats.some(p => inPoly(tmp.x, -tmp.z, p.poly))) c.ds = sd; } }
    return 1;
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
  const nbr = (c, end) => { const C = c.set.cars, i = C.indexOf(c), j = i + ((end < 0) !== !!c.flip ? -1 : 1), n = C[j]; return n && n.rects ? n : null; };
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

  // ---------------------------------------------------------------- aikataulu ja kulunvarmistus
  let A = window.__aika;
  const kello = () => A || window.__aika || null;
  let oma = null;       // ilman aika.js:ää oma kello klo 9 alkaen
  const viikonpaiva = p => VKP[((p - 1) % 7 + 7) % 7];
  // arvioitu ajoaika kartan reunalta pysähdyspaikalle (s): päärata 80 km/h, viimeiset 950 m 35 km/h, kiihdytys ja jarrutus
  const AJO = R => (Math.max(0, R.L - YARD_FROM) / V_LINE + YARD_FROM / V_YARD + 25) / TUNTI_S;
  const liikkuu = U => U.T.mode === 'in' || U.T.mode === 'out' || U.T.mode === 'term';
  const tavaraEstaa = () => !!(window.__tavara && window.__tavara.estaaIC());
  const saaLiikkua = U => !sets.some(V => V !== U && liikkuu(V)) && !tavaraEstaa();
  const raiteella = r => sets.filter(U => U.T.mode === 'dwell' && U.raide === r).sort((a, b) => a.jarj - b.jarj);
  let jarj = 0;
  // juna raiteelle r: pysähdyspaikka edellisten taakse
  function raiteelle(U, r) {
    U.raide = r; U.R = RT[r]; let stop = U.R.L - 1; for (const V of raiteella(r)) if (V !== U) stop -= V.LEN + 4; U.STOP = stop; U.jarj = ++jarj;
  }
  const S = { tehty: new Set(), kello: null };
  const near = () => { const s = G.S || {}, W = G.WALK || {}; const x = W.on ? W.x : s.x, y = W.on ? W.y : s.y; return Math.hypot(x + 450, y + 990) < 450; };
  const toast = t => { if (near() && G.toast) G.toast(t, 4); };
  const nimi = e => (e.hki ? 'IC ' + e.nro + (e.tulo ? ' Helsingistä' : ' Helsinkiin') : 'IC ' + e.nro + (e.tulo ? ' Tampereelta' : ' Tampereelle'));
  // tapahtuman käynnistyshetki (pelitunteina): saapuva juna lähtee kartan reunalta ajoajan verran ennen Porin aikaa
  const t0 = e => e.tulo ? e.h - AJO(RT[e.raide]) : e.h;

  function seiso(U) { const T = U.T; T.mode = 'dwell'; T.v = 0; T.t = 0; findDoorSide(U); U.doorSide = 1; place(U); }
  // pelin alku tai kellon siirto: asemalle ne junat, jotka aikataulun mukaan siellä nyt seisovat (tapahtumat edellisestä 18.15:stä alkaen;
  // viimeinen juna lähtee joka päivä 18.12, jolloin asema on tyhjä)
  function alusta() {
    const K = kello(), t = K.t, p = K.paiva;
    for (const U of sets) { U.T.mode = 'away'; U.job = null; U.lahto = null; U.raide = '1'; place(U); }
    S.tehty = new Set();
    const L = [];
    const alku = t >= 18.25 ? 0 : 1;
    for (let d = alku; d >= 0; d--) for (const e of tapahtumat(viikonpaiva(p - d))) { if (d === alku && e.h < 18.25) continue; if (d === 0 && e.h > t) continue; L.push(e); }
    for (const e of L) {
      if (e.tulo) { const U = sets.find(V => V.T.mode === 'away'); if (!U) continue; raiteelle(U, e.raide); U.T.s = U.STOP; seiso(U); }
      else { const R = raiteella(e.raide), U = R.length ? R[R.length - 1] : raiteella(e.raide === '1' ? '2' : '1').pop(); if (U) { U.T.mode = 'away'; place(U); } }
    }
    for (const e of tapahtumat(viikonpaiva(p))) if (t0(e) <= t) S.tehty.add(p + ':' + e.nro);
    S.kello = [t, p];
  }

  function step(dtf) {
    const now = performance.now(), dt = typeof dtf === 'number' ? dtf : Math.min(0.1, (now - last) / 1000); last = now;
    if (!A && window.__aika) { A = window.__aika; S.kello = null; }
    if (!A && !oma && now - alkuHetki > 20000) { let t = 9, p = 1; oma = { get t() { return t; }, get paiva() { return p; }, etene: d => { t += d / TUNTI_S; if (t >= 24) { t -= 24; p++; } } }; A = oma; S.kello = null; }
    if (oma) oma.etene(dt);
    const K = kello();
    if (K) {
      const t = K.t, p = K.paiva;
      if (!S.kello) alusta();
      else { const [ta, pa] = S.kello; if (p === pa ? (t < ta - 0.01 || t > ta + 0.25) : !(p === pa + 1 && t < 0.25)) alusta(); }
      S.kello = [K.t, K.paiva];
      // aikataulun tapahtumat
      for (const e of tapahtumat(viikonpaiva(p))) { const k = p + ':' + e.nro; if (S.tehty.has(k) || t < t0(e)) continue; S.tehty.add(k); if (t > t0(e) + 2) continue;
        if (e.tulo) { const U = sets.find(V => V.T.mode === 'away'); if (U) { U.job = e; U.T.mode = 'odota'; U.T.t = 0; } }      // (kyydissä palannut juna on jo asemalla)
        else { const vapaat = r => raiteella(r).filter(V => !V.lahto), R = vapaat(e.raide), U = R.length ? R[R.length - 1] : vapaat(e.raide === '1' ? '2' : '1').pop(); if (U) U.lahto = e; } }
    }
    for (const U of sets) {
      const T = U.T;
      if (T.mode === 'odota') {      // kartan ulkopuolella: lähtee, kun pääraide on vapaa
        T.t += dt; if (T.t > 2 * TUNTI_S) { T.mode = 'away'; U.job = null; }
        else if (saaLiikkua(U)) { raiteelle(U, U.job.raide); T.mode = 'in'; T.s = -10; T.v = V_LINE; U.msg = 0; }
      } else if (T.mode === 'in') {
        const toStop = U.STOP - T.s, lim = toStop < YARD_FROM ? V_YARD : V_LINE, brake = Math.sqrt(Math.max(0, 2 * DEC * toStop));
        const vt = Math.min(lim, brake); T.v = vt < T.v ? Math.max(vt, T.v - DEC * 1.6 * dt) : Math.min(vt, T.v + ACC * dt);
        T.s += T.v * dt;
        if (toStop < 300 && !U.msg && U.job) { U.msg = 1; toast(`${nimi(U.job)} saapuu raiteelle ${U.raide} (${U.job.aika})`); }
        if (toStop <= 0.05 || (toStop < 1.5 && T.v < 0.15)) { T.s = U.STOP; seiso(U); U.job = null; }
      } else if (T.mode === 'dwell') {
        T.t += dt;
        // ovet: auki saapuessa, kiinni lähtöön valmistauduttaessa; yöksi jäävä juna sulkee ovet minuutin päästä ja avaa ne ennen lähtöä
        const K2 = kello(), seur = U.lahto ? 0 : (K2 ? Math.min(...tapahtumat(viikonpaiva(K2.paiva)).filter(e => !e.tulo && e.h > K2.t).map(e => e.h - K2.t), 99) : 99);
        const auki = U.lahto ? 0 : (seur > 1 && T.t > 60 ? 0 : 1);
        T.doorT += Math.max(-dt / 3, Math.min(dt / 3, (T.t < 4 ? 0 : auki) - T.doorT)); doors(U, T.doorT);
        if (U.lahto && U.msg !== 2) { U.msg = 2; toast(`${nimi(U.lahto)} lähtee raiteelta ${U.raide} (${U.lahto.aika})`); }
        if (U.lahto && T.doorT <= 0 && T.t > 8 && saaLiikkua(U) && raiteella(U.raide).pop() === U) { T.mode = 'out'; T.v = 0; doors(U, 0); }
      } else if (T.mode === 'out') {
        const fromStop = U.STOP - T.s, endS = U.LEN + 25, ride = aboard() && ab.c.set === U;
        const lim = Math.min(fromStop < YARD_FROM - U.LEN ? V_YARD : V_LINE, ride ? Math.sqrt(Math.max(0, 2 * DEC * (T.s - endS))) : 1e9); T.v = lim < T.v ? Math.max(lim, T.v - DEC * 1.6 * dt) : Math.min(lim, T.v + ACC * dt); T.s -= T.v * dt;
        if (ride && T.s <= endS + 1 && T.v < 0.2) { T.mode = 'term'; T.t = 0; T.v = 0; G.toast && G.toast('Kartan reuna: juna kääntyy takaisin Poriin', 4); }
        if (T.s < -5) { T.mode = 'away'; T.t = 0; U.lahto = null; }   // koko juna ulos kartalta
      } else if (T.mode === 'term') {      // kyydissä kartan reunalle: odotus ja paluu asemalle (Tampereen suunta ei mahdu kartalle)
        T.t += dt; if (T.t > 25 && !tavaraEstaa()) { const r = U.raide; U.lahto = null; raiteelle(U, r); T.mode = 'in'; T.v = 0; U.msg = 1; }
      }
      // pyörät
      const ds = T.v * dt * (T.mode === 'out' ? -1 : 1);
      for (const c of U.cars) for (const w of c.wheels) w.rotation.x += ds / c.r * (c.flip ? -1 : 1);
    }
    // kyydissä: pelaaja vaunun mukana
    const W = G.WALK, ride = aboard() ? ab.c : null; let ryaw = 0;
    if (ride) { rv.set(W.x, W.z, -W.y).applyMatrix4(ride.Mi); ryaw = ride.g.rotation.y; }
    for (const U of sets) place(U);
    if (ride && ride.g.visible) { rv.applyMatrix4(ride.M); W.x = rv.x; W.y = -rv.z; W.z = rv.y; let dy = ride.g.rotation.y - ryaw; dy = Math.atan2(Math.sin(dy), Math.cos(dy)); W.yaw -= dy;
      if (G.S) { G.S.x = W.x; G.S.y = W.y; } }
    // sisätilat näkyviin lähellä, kamera silmien korkeudelle kyytiin noustessa
    { const S0 = G.S || {}, px = W && W.on ? W.x : S0.x, py = W && W.on ? W.y : S0.y;
      if (!sisaTila && cars.some(c => c.g.visible && Math.hypot(px - c.g.position.x, py + c.g.position.z) < 600)) loadSisa();
      for (const c of cars) if (c.sisa) c.sisa.visible = c.g.visible && Math.hypot(px - c.g.position.x, py + c.g.position.z) < 90;
      const on = aboard();
      if (on && ab.cam === null) { ab.cam = G.camMode; if (G.setCam) G.setCam(1); if (!ab.msg) { ab.msg = 1; G.toast && G.toast('Olet IC-junassa Pori–Tampere. Ovet aukeavat asemalla; kartan reunalla juna kääntyy takaisin.', 5); } }
      if (!on && ab.cam !== null && !(ab.c && performance.now() - ab.t < 1500)) { if (G.setCam && G.camMode === 1) G.setCam(ab.cam); ab.cam = null; } }
  }
  let last = performance.now(); const alkuHetki = last;
  // ensimmäinen liikkuva tai seisova yksikkö (vanha rajapinta: window.__juna.T)
  const ensim = () => sets.find(liikkuu) || sets.find(U => U.T.mode === 'dwell') || sets[0];
  window.__juna = { sets, cars, R: RT[1], RT, get T() { return ensim().T; }, get LEN() { return ensim().LEN; }, get STOP() { return ensim().STOP; }, OHJELMA, S,
    ab, junaZ, aboard,
    liikkeella: () => sets.some(liikkuu),
    // tavarajuna (juna/tavarajuna.js) saa mennä IC:n kanssa yhteiselle raiteelle: yksikään IC ei liiku eikä ole lähdössä tai tulossa 15 pelimin sisällä
    vapaaTavaralle: () => { if (sets.some(U => liikkuu(U) || U.T.mode === 'odota' || U.lahto)) return false; const K = kello(); if (!K) return true;
      return !tapahtumat(viikonpaiva(K.paiva)).some(e => { const a = t0(e); return a > K.t && a < K.t + 0.25; }); },
    // seisovien ja liikkuvien IC-vaunujen kohdat (x, y) 4 m välein tavarajunan kulunvarmistukseen
    varatut: () => { const P = []; for (const c of cars) { if (!c.g.visible) continue; const x = c.g.position.x, y = -c.g.position.z, sn = Math.sin(c.g.rotation.y), cs = -Math.cos(c.g.rotation.y);
      for (let d = -c.half; d <= c.half; d += 4) P.push({ x: x + sn * d, y: y + cs * d }); } return P; } };
  window.__walkBlock = (x, y) => junaZ(x, y) === null;
  window.__aboard = aboard;      // index.html stepWalk: kuoren sisällä vain käytävillä, ovista vain auki ollessa
  setInterval(step, 33);
  window.__juna.tick = step;
  step(0.033);
  console.log('[juna] IC-junat valmiina:', sets.map(U => U.cars.length - 1 + ' vaunua ' + Math.round(U.LEN) + ' m').join(', '),
    '· asemalla', sets.filter(U => U.T.mode === 'dwell').map(U => 'raide ' + U.raide).join(', ') || '-');
  return window.__juna;
}

if (typeof window !== 'undefined') {
  const odota = () => { const G = window.__game; if (G && G.scene && window.__rata) { luoJuna(G).catch(e => console.error('[juna]', e)); return; } setTimeout(odota, 700); };
  odota();
}
export { luoJuna };
