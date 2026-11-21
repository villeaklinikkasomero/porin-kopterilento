// moduulit/kespan_lenkki.js – siirretty pääskriptistä (src/js/154_kespan_lenkki.js) omaksi moduulikseen 21.11.2026.
// Pääskriptin muuttujat tulevat oliossa _P (getterit pitävät ne ajan tasalla); kirjastot ja data tuodaan suoraan.
// Kutsu ja _P:n sisältö: src/js/154_kespan_lenkki.js. Uusi riippuvuus pääskriptiin → lisää se sinne _P-olioon.
import * as THREE from '../three.module.min.js';

// 20.11.2026 (owner): car race "Kespan lenkki", 3.3 km. Start at the first lights of Mikonkatu with three bots, off on green: Mikonkatu - Otavankatu -
// Luvianpuistokatu - the police roundabout - round the Tiilimäki Neste - back the same way - Otavankatu - Itsenäisyydenkatu - Antinkatu - Liisankatu -
// Isolinnankatu - Mikonkatu. Route = road-graph nodes (KESPA.p, game metres; the Neste yard loop is OSM way 357449244), KESPA.t = [metres, arrow, name] of the
// turns. G (or the flag button) in the car puts the field on the grid. Progress is the projection on the route within a forward window, so the two passes of
// Luvianpuistokatu cannot be mixed up and no part can be skipped. Bots: pure pursuit along the route, slower into bends, pulling out past slower cars.
// Normal traffic and its lights stay on; only the start waits for green.
export default function kaynnista(_P) {
const KESPA = {"p":[32.6,-339.0,28,-338,20,-336,14,-334,-91,-310,-99,-308,-111,-306,-248,-274,-255,-272,-266,-269,-283,-265,-291,-263,-376,-243,-386,-241,-388,-249,-402,-315,-411,-354,-413,-365,-415,-374,-425,-420,-432,-443,-434,-453,-437,-462,-441,-469,-448,-477,-451,-486,-512,-535,-517,-539,-527,-548,-551,-557,-573,-560,-578,-559,-584,-560,-590,-561,-594,-563,-599,-567,-604,-572,-606,-576,-608,-583,-609,-585,-609,-589,-620,-607,-627,-618,-637,-629,-649,-640,-709,-692,-768,-738,-773,-742,-784,-750,-823,-782,-850,-800,-845,-811,-838,-827,-836,-834,-835,-842,-836,-864,-845,-906,-828,-919,-817,-915,-778,-924,-768,-935,-772,-962,-808,-988,-845,-986,-862,-981,-845,-906,-836,-864,-835,-842,-836,-834,-838,-827,-845,-811,-816,-792,-785,-768,-776,-760,-765,-751,-702,-702,-632,-640,-618,-628,-607,-621,-590,-616,-585,-618,-577,-618,-569,-616,-563,-613,-559,-609,-555,-604,-553,-600,-551,-594,-550,-590,-551,-586,-542,-568,-527,-548,-517,-539,-512,-535,-451,-486,-448,-477,-441,-469,-437,-462,-434,-453,-432,-443,-425,-420,-415,-374,-413,-365,-402,-367,-392,-370,-384,-372,-374,-374,-321,-387,-317,-387,-303,-391,-299,-392,-281,-396,-244,-405,-235,-407,-178,-421,-135,-431,-128,-432,-126,-421,-101,-317,-99,-308,-97,-297,-74,-199,-72,-190,-64,-192,-62,-192,20,-211,28,-213,37,-215,48,-218,63,-221,137,-239,147,-241,145,-250,135,-292,133,-302,131,-310,123,-350,121,-358,111,-356,32.6,-339.0],"t":[[430,"←","Otavankatu"],[647,"↑","Luvianpuistokatu"],[884,"↑","ympyrästä suoraan"],[1219,"←","Maamiehenkatu"],[1317,"←","Nesteen ympäri"],[1531,"→","Maamiehenkatu"],[1706,"→","Luvianpuistokatu"],[2088,"↑","ympyrästä suoraan"],[2269,"↑","Otavankatu"],[2359,"→","Itsenäisyydenkatu"],[2652,"←","Antinkatu"],[2901,"→","Liisankatu"],[3126,"→","Isolinnankatu"],[3245,"→","Mikonkatu – maali"]]};
{
  const P = [], CUM = [0]; for (let i = 0; i < KESPA.p.length; i += 2) P.push([KESPA.p[i], KESPA.p[i + 1]]); for (let i = 1; i < P.length; i++) CUM.push(CUM[i - 1] + Math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]));
  const TOT = CUM[CUM.length - 1], RC = { st: 0, t: 0, s: 0, i: 0, bots: [], best: null, off: 0, seenRed: false, cd: 0, rib: null, len: TOT }; window.__race = RC;
  try { RC.best = parseFloat(localStorage.getItem('pori-kespa-best')) || null; } catch (e) {}
  const at = (s, o) => { s = Math.max(0, Math.min(TOT - 1e-3, s)); let i = o && o.i || 0; while (i < P.length - 2 && CUM[i + 1] < s) i++; while (i > 0 && CUM[i] > s) i--; const a = P[i], b = P[i + 1], L = CUM[i + 1] - CUM[i], t = (s - CUM[i]) / L, dx = (b[0] - a[0]) / L, dy = (b[1] - a[1]) / L;
    if (o) o.i = i; return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, dx, dy]; };
  const proj = (x, y, s0, win) => { let bs = s0, bd = 1e9; for (let s = Math.max(0, s0 - 6); s <= Math.min(TOT, s0 + win); s += 2) { const q = at(s), d = (q[0] - x) ** 2 + (q[1] - y) ** 2; if (d < bd) { bd = d; bs = s; } } return [bs, Math.sqrt(bd)]; };      /* nearest route point ahead of s0 */
  const gz = (x, y) => _P.carGround(x, y) ?? _P.TZs(x, y), adiff = (a, b) => { let d = a - b; while (d > Math.PI) d -= 2 * Math.PI; while (d < -Math.PI) d += 2 * Math.PI; return d; };
  const hud = document.createElement('div'); hud.style.cssText = 'position:fixed;z-index:30;display:none;left:50%;top:10px;transform:translateX(-50%);color:#fff;background:rgba(10,16,24,.88);border:1px solid rgba(255,255,255,.2);border-radius:10px;padding:8px 14px;font:700 17px system-ui,sans-serif;white-space:nowrap;text-align:center'; document.body.appendChild(hud);
  const btn = document.createElement('button'); btn.textContent = '🏁 Kespan lenkki (G)'; btn.style.cssText = 'position:fixed;z-index:30;display:none;right:14px;top:112px;color:#fff;background:rgba(10,16,24,.88);border:1px solid rgba(255,255,255,.25);border-radius:10px;padding:8px 12px;font:600 14px system-ui,sans-serif;cursor:pointer'; document.body.appendChild(btn);
  const ribbon = () => { if (RC.rib) return; const v = [], ix = []; let k = 0; for (let s = 0; s <= TOT; s += 3) { const q = at(s); v.push(q[0] - q[3] * 0.7, 0.2, -(q[1] + q[2] * 0.7), q[0] + q[3] * 0.7, 0.2, -(q[1] - q[2] * 0.7)); if (k) ix.push(k - 2, k - 1, k, k - 1, k + 1, k); k += 2; }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(v, 3)); g.setIndex(ix); RC.rib = new THREE.Mesh(g, new THREE.MeshBasicMaterial({ color: 0xffd23c, transparent: true, opacity: 0.5, depthWrite: false, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -16, polygonOffsetUnits: -16 })); RC.rib.frustumCulled = false; RC.rib.renderOrder = 3; _P.scene.add(RC.rib); };
  const COL = [0xb3261e, 0xe8e8e8, 0x1f7a3a], VM = [20.5, 22.5, 24.5], NM = ['Punainen', 'Valkoinen', 'Vihreä'];
  const mkBot = k => { const g = new THREE.Group(), body = _P.carG.children[0].clone(true), mats = new Map(); g.rotation.order = 'YXZ'; g.userData.noT = true; g.add(body); const wh = [];
    body.traverse(q => { q.userData.noT = true; if (/_d[1-3]$/.test(q.name || '')) q.visible = false; else if (/_d0$/.test(q.name || '')) q.visible = true; if (/^Wheel_/.test(q.name || '')) wh.push(q);
      if (q.isMesh && q.material && q.material.name === 'CarPaint') { if (!mats.has(q.material)) { const m = q.material.clone(); m.color.setHex(COL[k]); m.userData.noT = true; mats.set(q.material, m); } q.material = mats.get(q.material); } });
    _P.scene.add(g); return { k, g, wh, x: 0, y: 0, yaw: 0, v: 0, s: 0, i: 0, lat: 0, latT: 0, vm: VM[k], fin: 0, wx: undefined, wy: 0, o: { i: 0 } }; };
  const place = (b, s, lat) => { const q = at(s); b.x = q[0] + q[3] * lat; b.y = q[1] - q[2] * lat; b.yaw = Math.atan2(q[2], q[3]); b.s = s; b.lat = b.latT = lat; };
  const draw = b => { b.wx = b.x; b.wy = b.y; b.g.position.set(b.x, gz(b.x, b.y), -b.y); b.g.rotation.y = -b.yaw; };
  const clear = () => { for (const b of RC.bots) _P.scene.remove(b.g); RC.bots = []; if (RC.rib) RC.rib.visible = false; hud.style.display = 'none'; RC.st = 0; };
  const sigNode = () => { if (RC.sn !== undefined) return RC.sn; let n = null, bd = 16; try { for (const q of window.__sig.nodes()) { const d = Math.hypot(q.x - 20, q.y + 336); if (d < bd) { bd = d; n = q; } } } catch (e) {}
    if (n) { let f = null, fd = 1e9; for (const q of n.nb) { const d = Math.hypot(q.x - P[0][0], q.y - P[0][1]); if (d < fd) { fd = d; f = q; } } RC.sf = f; } return RC.sn = n; };
  const grid = () => { if (RC.st === 1 || RC.st === 2) { clear(); _P.toast('Kisa keskeytetty', 2); return; } if (_P.VEH !== 'car' || _P.WALK.on || _P.S.dead || !_P.carG.children.length) { _P.toast('Kespan lenkki ajetaan autolla', 2.5); return; }
    clear(); ribbon(); RC.rib.visible = true; const q = at(0.5); _P.CAR.x = q[0] + q[3] * 1.7; _P.CAR.y = q[1] - q[2] * 1.7; _P.CAR.yaw = Math.atan2(q[2], q[3]); _P.CAR.v = 0; _P.CAR.steer = 0; _P.S.x = _P.CAR.x; _P.S.y = _P.CAR.y; RC.gx = _P.CAR.x; RC.gy = _P.CAR.y; RC.gyaw = _P.CAR.yaw;
    for (let k = 0; k < 3; k++) { const b = mkBot(k); place(b, 0.5, 1.7); RC.bots.push(b); }
    /* the grid stands behind the line: slots along the last metres of the lap, mirrored back from the start point */
    const back = (b, d, lat) => { const a = at(TOT - d); b.x = a[0] + a[3] * lat; b.y = a[1] - a[2] * lat; b.yaw = Math.atan2(a[2], a[3]); b.lat = b.latT = lat; b.s = -d; b.v = 0; draw(b); };
    back(RC.bots[0], 0.5, -1.7); back(RC.bots[1], 7.5, 1.7); back(RC.bots[2], 7.5, -1.7);
    RC.st = 1; RC.t = 0; RC.s = 0; RC.off = 0; RC.seenRed = false; RC.cd = 0; RC.fin = 0; _P.toast('🏁 Kespan lenkki – lähtö kun valo vaihtuu vihreäksi', 4); };
  btn.addEventListener('click', e => { e.preventDefault(); btn.blur(); grid(); }); addEventListener('keydown', e => { if (e.code === 'KeyG' && _P.started && !e.repeat && !(e.target && e.target.tagName === 'INPUT')) grid(); });
  RC.grid = grid; RC.clear = clear; RC.at = at;
  const botStep = (b, dt) => { if (b.s < 0) { b.s = 0; b.o.i = 0; }      /* off the grid: from here on its place is measured along the route */
    const pr = proj(b.x, b.y, b.s, 40); b.s = Math.max(b.s, pr[0]); if (b.s >= TOT - 2 && !b.fin) b.fin = RC.t;
    const fx = Math.sin(b.yaw), fy = Math.cos(b.yaw); let blocked = false, slow = 1e9;
    const see = (ox, oy, ov) => { const dx = ox - b.x, dy = oy - b.y, f = dx * fx + dy * fy, l = dx * fy - dy * fx; if (f > 1 && f < 9 + b.v * 0.9 && Math.abs(l) < 2.1) { blocked = true; if (f < 7) slow = Math.min(slow, ov + (f - 4.6) * 1.5); } };
    for (const c of window.__sig.cars) if (c.wx !== undefined && Math.abs(c.wx - b.x) < 40 && Math.abs(c.wy - b.y) < 40) see(c.wx, c.wy, 0); for (const o of RC.bots) if (o !== b) see(o.x, o.y, o.v); see(_P.CAR.x, _P.CAR.y, Math.max(0, _P.CAR.v));
    b.latT = blocked ? -1.9 : 1.7; b.lat += Math.max(-2.2 * dt, Math.min(2.2 * dt, b.latT - b.lat));
    const look = 7 + b.v * 0.45, q = at(b.s + look, b.o), tx = q[0] + q[3] * b.lat, ty = q[1] - q[2] * b.lat, want = Math.atan2(tx - b.x, ty - b.y), far = at(b.s + 14 + b.v * 1.3), bend = Math.abs(adiff(Math.atan2(far[2], far[3]), b.yaw));
    let vt = b.fin ? 0 : b.vm * Math.max(0.38, 1 - bend / (1.5 + b.k * 0.3)); vt = Math.max(0, Math.min(vt, slow));
    b.v += Math.max(-9 * dt, Math.min((4.1 + b.k * 0.25) * (1 - b.v / 27) * dt, vt - b.v)); const d = adiff(want, b.yaw), mr = Math.max(0.5, b.v / 5.5) * dt; b.yaw += Math.max(-mr, Math.min(mr, d));
    b.x += Math.sin(b.yaw) * b.v * dt; b.y += Math.cos(b.yaw) * b.v * dt; for (const w of b.wh) w.rotation.x += b.v * dt / 0.325; draw(b); };
  const next = s => { for (const t of KESPA.t) if (t[0] > s + 4) return t; return [TOT, '🏁', 'maali']; };
  window.__raceTick = dt => { btn.style.display = _P.started && RC.st === 0 && _P.VEH === 'car' && !_P.WALK.on && !_P.S.dead ? 'block' : 'none'; if (!RC.st || dt <= 0) return;
    if (RC.st < 3 && (_P.WALK.on || _P.S.dead || _P.VEH !== 'car')) { clear(); _P.toast('Kisa keskeytetty', 2); return; }
    if (RC.st === 1) { _P.CAR.x = RC.gx; _P.CAR.y = RC.gy; _P.CAR.yaw = RC.gyaw; _P.CAR.v = 0; RC.cd += dt; const n = sigNode(); let go = false, txt = 'Odota vihreää…';
      if (n) { const st = window.__sig.state(n, RC.sf); if (st !== 0) RC.seenRed = true; go = st === 0 && RC.seenRed; if (st === 0 && !RC.seenRed) { go = RC.cd > 3.6; txt = String(Math.max(1, Math.ceil(3.6 - RC.cd))); } else txt = st === 1 ? 'Keltainen…' : 'Punainen – valmiina…';      /* already green: a short count instead of a whole cycle */ }
      else { go = RC.cd > 4; txt = RC.cd < 4 ? String(Math.ceil(4 - RC.cd)) : ''; }
      hud.textContent = '🏁 Kespan lenkki · ' + txt; hud.style.display = 'block'; if (go) { RC.st = 2; RC.t = 0; _P.toast('VIHREÄ – mene!', 1.6); } return; }
    RC.t += dt; for (const b of RC.bots) botStep(b, dt);
    if (RC.st === 2) { const pr = proj(_P.CAR.x, _P.CAR.y, RC.s, 45); if (pr[1] < 22) { RC.s = Math.max(RC.s, pr[0]); RC.off = 0; } else if ((RC.off += dt) > 5) { RC.off = 0; _P.toast('Palaa keltaiselle reitille', 2.5); }
      const pos = 1 + RC.bots.filter(b => b.fin || b.s > RC.s).length, t = next(RC.s);
      hud.textContent = pos + '/4 · ' + _P.fmtT1(RC.t) + ' · ' + t[1] + ' ' + Math.max(0, Math.round((t[0] - RC.s) / 10) * 10) + ' m ' + t[2];
      if (RC.s >= TOT - 2.5) { RC.st = 3; RC.fin = RC.t; RC.end = 0; const rec = !RC.best || RC.t < RC.best; if (rec) { RC.best = RC.t; try { localStorage.setItem('pori-kespa-best', String(RC.t)); } catch (e) {} }
        RC.pos = pos; hud.textContent = '🏁 Sija ' + pos + '/4 · ' + _P.fmtT1(RC.t) + (rec ? ' · oma ennätys!' : ' · ennätys ' + _P.fmtT1(RC.best)); _P.toast(pos === 1 ? 'Voitto! Kespan lenkki ' + _P.fmtT1(RC.t) : 'Maalissa ' + pos + '. · ' + _P.fmtT1(RC.t), 6); RC.rib.visible = false; } }
    else if ((RC.end += dt) > 25) clear(); };
}
}
