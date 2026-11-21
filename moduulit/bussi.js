// moduulit/bussi.js – siirretty pääskriptistä (src/js/170_bussi.js) omaksi moduulikseen 21.11.2026.
// Pääskriptin muuttujat tulevat oliossa _P (getterit pitävät ne ajan tasalla); kirjastot ja data tuodaan suoraan.
// Kutsu ja _P:n sisältö: src/js/170_bussi.js. Uusi riippuvuus pääskriptiin → lisää se sinne _P-olioon.
import * as THREE from '../three.module.min.js';
import CITY from '../city.js';

// ---------- city bus (20.11.2026, owner: "a bus the player can drive or ride; borrowed at the Kauppatori stands or the Matkakeskus the player drives the
// line, picks up passengers and lets them off when the stop button is pressed"). Model: bussi.js / bussi_m.js (tools/vehicles/porikopteri_bussi.py, doors
// DoorF_A/B and DoorM_A/B turn about their hinges, damage steps as in the cars). Stops: OpenStreetMap (tools/bus/osm_stops.json, 20.11.2026), the 87 in the
// sharp core. Two lines of our own over real stops: 1 Kauppatori - Puuvilla and back, 2 Matkakeskus - Kauppatori and back. Parked buses wait at
// Kauppatori laituri 2 and Matkakeskus laituri 1; on foot next to one Enter takes it and starts that line.
// Live buses (smooth, 20.11.2026): drawn 2 s behind the feed, interpolated between received points and kept on our street lanes.
// Live buses: Digitransit's open MQTT feed (wss://mqtt.digitransit.fi, topic /gtfsrt/vp/Pori/#, GTFS-RT vehicle positions, no key) puts the real Pori
// buses on the streets where they are right now (only while they run). On foot next to one that stands still, Enter gets on; N (or the bell button) asks
// it to stop and the player gets off at the next halt. The live buses are drawn only - they do not collide.
export default function kaynnista(_P) {
{
  const STOPS = [["Yliopistokeskus E",255.2,733.4],["Valajankatu I",542.2,652.6],["Tuomarinkatu P",-994,-214.2],["Ratakatu L",-976,-820.1],["Ratakatu I",-907.1,-841.2],["Karjapiha L",-953,356.7],["Tasavallankatu P",-387.4,-791.7],["Lyseo I",-451.1,318.9],["Cygnaeus I",-367,-385.5],["Keski-Porin kirkko P",187.8,349.2],["Poliisilaitos E",-535.6,-666],["Karhukatu L",-502.7,-516.7],["Hallituskatu L",115.2,334.4],["Antinkatu",-115.2,-352.5],["Poliisilaitos P",-514.5,-643.8],["Asema-aukio I",-272.8,-823.3],["Porilaistenkatu E",-172.5,-594.8],["Valtionsilta I",-688.9,-309.3],["Liisantori L",-429.9,-221.6],["Otava I",-239.5,269.8],["Tasavallantori P",-408.9,-425.1],["Teljäntori P",-80.9,-262],["Kampus P",-261.8,-893.7],["Valtionsilta L",-646.5,-170.8],["Antinkatu L",-159.5,-286.8],["Kampus I",-276.2,-920.8],["Kuninkaanhaka L",801.5,-630.5],["Kävelykatu L",60.8,-338.3],["Oikokatu E",159.7,-736.4],["Itsenäisyydenkatu P",-9.5,-510.6],["Vähälinnankatu I",216.8,-694.2],["Isolinnankatu E",153.4,-178.7],["Presidentinpuistokatu I",465.5,-832],["Pori Kauppatori laituri 11",-22.5,-5.7],["Keskusaukio I",33.6,-478.2],["Yrjönkatu 9",125.9,149.8],["Nuorisotalo L",262.5,13.1],["Uimahalli I",591.4,-613.1],["Presidentinpuistokatu L",368.9,-740.7],["Teljäntori E",-65.4,-129.4],["Teljänkatu L",263.3,-510.8],["Teljänkatu I",278.7,-536.3],["Yliopistokeskus P",279,741.9],["Karjapiha I",-871.8,353.7],["Keskusaukio P",96.2,-518],["Keskusaukio E",67.6,-524.1],["Oikeustalo P",366.7,171],["Eetunaukio E",152.4,-100.3],["Itäpuisto P",10.2,-71.2],["Kuninkaanhaka I",805.5,-660.6],["Porin silta L",311.2,679.3],["Valajankatu L",426.2,665.3],["Sampo L",814.9,842.4],["Sampo I",824.4,827.2],["Pori matkakeskus laituri 7",-399.1,-892.5],["Pori matkakeskus laituri 1",-370.5,-928.6],["Pori matkakeskus laituri 2",-350.8,-913.1],["Pori matkakeskus laituri 4",-360.4,-904.4],["Pori matkakeskus laituri 3",-375.7,-917.3],["Pori matkakeskus laituri 5",-384.1,-908.1],["Pori matkakeskus laituri 6",-368.6,-895.8],["Puuvilla piha",159.5,986.7],["Keskusaukio L",96.9,-580.4],["Vähälinnankatu L",198.1,-666],["Urheilutalo L",636.5,-884.1],["Urheilutalo I",664.3,-930.2],["Isosannanpuistokatu E",315,1022.8],["Yliopistokeskus L",214,702.1],["Kävelykatu P",17.5,-367.1],["Oikokatu P",200.8,-776.8],["Tasavallankatu",-266.6,-539.1],["Porilaistenkatu I",-105.4,-636.4],["Porilaistenkatu L",-161.3,-671.8],["Lyseo L",-392.9,322.8],["Taavi",-125.7,498.2],["Pelle-Hermanni",-501.5,702.1],["Hanhipuisto",-701.5,741.3],["Porin silta I",313.3,660.8],["Pohjois-Porin terveysasema",138.6,854],["Uimahalli L",593.9,-583.9],["Pori Kauppatori laituri 6",15.6,112.7],["Pori Kauppatori laituri 7",25.5,105.5],["Pori Kauppatori laituri 5",4.7,114.8],["Pori Kauppatori laituri 4",-7.2,62.5],["Pori Kauppatori laituri 3",3.8,59.5],["Pori Kauppatori laituri 2",15,57.4],["Pori Kauppatori laituri 9",-7.1,62.8]].map(([n, x, y]) => ({ n, x, y, pose: null }));
  const byName = n => STOPS.find(s => s.n === n);
  const LINES = { 1: { n: '1', to: 'Puuvilla', depot: 'Pori Kauppatori laituri 2', dp: [12.4, 57.3, 0.23], s: ['Pori Kauppatori laituri 2', 'Hallituskatu L', 'Keski-Porin kirkko P', 'Porin silta L', 'Yliopistokeskus P', 'Puuvilla piha', 'Yliopistokeskus L', 'Porin silta I', 'Yrjönkatu 9', 'Pori Kauppatori laituri 6'] },
    2: { n: '2', to: 'Kauppatori', depot: 'Pori matkakeskus laituri 1', dp: [-374.1, -924.1, 0.896], s: ['Pori matkakeskus laituri 1', 'Asema-aukio I', 'Porilaistenkatu I', 'Keskusaukio E', 'Kävelykatu P', 'Teljäntori E', 'Itäpuisto P', 'Pori Kauppatori laituri 11', 'Teljäntori P', 'Antinkatu L', 'Tasavallankatu', 'Porilaistenkatu L', 'Pori matkakeskus laituri 7'] } };
  for (const k in LINES) LINES[k].stops = LINES[k].s.map(byName);
  const short = n => n.replace(/^Pori /, '').replace(/ ([LIPE])$/, '');
  const R = { line: null, i: 0, pax: [], req: false, reqT: 0, score: 0, served: false, near: 1e9, dwell: 0, door: 0, queue: null, hp: 100, best: 0, ride: null, bell: false, still: 0 };
  try { R.best = +localStorage.getItem('pori-bussi') || 0; } catch (e) {}
  let ready = false, broken = false;

  /* stop pose: the bus stands on the carriageway next to the stop, nose along the street, the stop on its right (right-hand traffic) */
  const asph = (x, y) => _P.ROAD.asphAt(x, y);
  const pose = (st, hint) => {
    let px = st.x, py = st.y, f = asph(px, py);
    for (let r = 1; r <= 12 && !f; r++) for (let a = 0; a < 16 && !f; a++) { const x = st.x + r * Math.sin(a * Math.PI / 8), y = st.y + r * Math.cos(a * Math.PI / 8); if (asph(x, y)) { px = x; py = y; f = true; } }
    if (!f) return hint != null ? { x: st.x, y: st.y, yaw: hint } : null;
    let yaw = hint;
    if (yaw == null) { let best = -1; for (let a = 0; a < 18; a++) { const t = a * Math.PI / 18, sx = Math.sin(t), sy = Math.cos(t); let n = 0; for (const s of [1, -1]) for (let d = 1; d <= 40; d++) { if (!asph(px + sx * d * s, py + sy * d * s)) break; n++; } if (n > best) { best = n; yaw = t; } }
      if ((st.x - px) * Math.cos(yaw) - (st.y - py) * Math.sin(yaw) < 0) yaw += Math.PI; }
    const rx = Math.cos(yaw), ry = -Math.sin(yaw); let d = 0; while (d < 8 && asph(px + rx * (d + 0.5), py + ry * (d + 0.5))) d += 0.5;
    const sh = Math.max(0, d - 1.7); return { x: px + rx * sh, y: py + ry * sh, yaw };
  };

  /* stop signs at every stop: a grey pole and a yellow sign with a bus, drawn as two instanced meshes */
  const sign = () => { const cv = document.createElement('canvas'); cv.width = cv.height = 64; const g = cv.getContext('2d'); g.fillStyle = '#f2c500'; g.fillRect(0, 0, 64, 64); g.strokeStyle = '#111'; g.lineWidth = 4; g.strokeRect(2, 2, 60, 60);
    g.fillStyle = '#111'; g.fillRect(12, 18, 40, 24); g.fillStyle = '#f2c500'; g.fillRect(16, 22, 9, 8); g.fillRect(28, 22, 9, 8); g.fillRect(40, 22, 8, 8); g.fillStyle = '#111'; g.beginPath(); g.arc(21, 44, 5, 0, 7); g.arc(43, 44, 5, 0, 7); g.fill();
    const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; return t; };
  /* shelters at the Kauppatori stands (owner 20.11.2026, from the aerial photo): the lanes run along the market hall (axis 0.23 rad east of north); each
     shelter stands on the kerb side, glass back and ends, a roof, posts and a bench, open towards the lane. [stop, centre x, y, which way the open side faces] */
  const AX = 0.23, EX = [Math.cos(AX), -Math.sin(AX)], DX = [Math.sin(AX), Math.cos(AX)];
  const SHEL = [['Pori Kauppatori laituri 2', 16.4, 57.1, -1], ['Pori Kauppatori laituri 3', -3.0, 61.1, 1], ['Pori Kauppatori laituri 4', -5.7, 62.2, -1], ['Pori Kauppatori laituri 5', 8.4, 113.9, 1]];
  const SIGN = { 'Pori Kauppatori laituri 6': [10.2, 111.4], 'Pori Kauppatori laituri 7': [31.6, 105.2], 'Pori Kauppatori laituri 9': null };      /* stop points that now lie in a lane */
  for (const [n, x, y] of SHEL) { const s = byName(n); if (s) SIGN[n] = [x + DX[0] * 2.35, y + DX[1] * 2.35]; }
  const buildShelters = () => {
    const mat = (c, o) => { const m = new THREE.MeshStandardMaterial(Object.assign({ color: c, roughness: 0.5, metalness: 0.3 }, o || {})); m.userData.noT = true; return m; };
    const steel = mat(0x5d6368), roof = mat(0x3a3f44, { roughness: 0.7 }), glass = mat(0xcfe3ea, { transparent: true, opacity: 0.28, roughness: 0.05, metalness: 0, depthWrite: false }), wood = mat(0x8a6a48, { metalness: 0, roughness: 0.8 });
    const box = (g, m, w, h, d, x, y, z) => { const me = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), m); me.position.set(x, y, z); me.userData.noT = true; g.add(me); };
    for (const [n, x, y, side] of SHEL) { const g = new THREE.Group(); g.userData.noT = true;
      for (const px of [-1.95, 1.95]) for (const pz of [-0.68, 0.62]) box(g, steel, 0.07, 2.35, 0.07, px, 1.175, pz);
      box(g, roof, 4.3, 0.12, 1.75, 0, 2.4, 0); box(g, glass, 3.9, 2.0, 0.02, 0, 1.15, -0.68); for (const px of [-1.95, 1.95]) box(g, glass, 0.02, 2.0, 1.2, px, 1.15, -0.08);
      box(g, wood, 2.2, 0.06, 0.38, 0, 0.46, -0.45); box(g, steel, 0.06, 0.44, 0.3, -1, 0.22, -0.45); box(g, steel, 0.06, 0.44, 0.3, 1, 0.22, -0.45);
      const nx = EX[0] * side, ny = EX[1] * side; g.position.set(x, _P.carGround(x, y) ?? _P.TZs(x, y), -y); g.rotation.y = Math.atan2(nx, -ny); _P.scene.add(g); } };
  const buildSigns = () => {
    const poleG = new THREE.CylinderGeometry(0.04, 0.04, 2.6, 6), signG = new THREE.BoxGeometry(0.5, 0.5, 0.03);
    const pm = new THREE.MeshStandardMaterial({ color: 0x8a8f94, metalness: 0.4, roughness: 0.5 }), sm = new THREE.MeshStandardMaterial({ map: sign(), roughness: 0.6 });
    pm.userData.noT = sm.userData.noT = true; const P = new THREE.InstancedMesh(poleG, pm, STOPS.length), Q = new THREE.InstancedMesh(signG, sm, STOPS.length);
    const m = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), one = new THREE.Vector3(1, 1, 1), p = new THREE.Vector3();
    STOPS.forEach((s, i) => { const o = SIGN[s.n]; if (o === null) { m.makeScale(0, 0, 0); P.setMatrixAt(i, m); Q.setMatrixAt(i, m); return; } const sx = o ? o[0] : s.x, sy = o ? o[1] : s.y, z = _P.carGround(sx, sy) ?? _P.TZs(sx, sy), yaw = o ? AX : s.pose ? s.pose.yaw : 0;
      p.set(sx, z + 1.3, -sy); m.compose(p, q.identity(), one); P.setMatrixAt(i, m);
      e.set(0, -yaw + Math.PI / 2, 0); q.setFromEuler(e); p.set(sx, z + 2.35, -sy); m.compose(p, q, one); Q.setMatrixAt(i, m); });
    for (const I of [P, Q]) { I.frustumCulled = false; I.userData.noT = true; _P.scene.add(I); } };

  /* markers for the next stop: a blue column over the sign and a ring where the bus should stand */
  const mk = new THREE.Group(); mk.userData.noT = true; mk.visible = false; _P.scene.add(mk);
  { const c = new THREE.Mesh(new THREE.CylinderGeometry(0.6, 0.6, 30, 16, 1, true), new THREE.MeshBasicMaterial({ color: 0x3aa0ff, transparent: true, opacity: 0.28, depthWrite: false, side: THREE.DoubleSide })); c.position.y = 15; c.userData.noT = true; c.material.userData.noT = true; mk.add(c);
    const r = new THREE.Mesh(new THREE.RingGeometry(5.6, 6.4, 40), new THREE.MeshBasicMaterial({ color: 0x3aa0ff, transparent: true, opacity: 0.5, depthWrite: false, side: THREE.DoubleSide })); r.rotation.x = -Math.PI / 2; r.userData.noT = true; r.material.userData.noT = true; mk.ring = r; _P.scene.add(r); r.visible = false; mk.col = c; }

  /* a copy of the bus model for parked and live buses: undamaged, doors shut */
  const copy = () => { const g = _P.CARM.bus.root.clone(true); g.traverse(q => { if (/_d[1-3]$/.test(q.name || '')) q.visible = false; else if (/_d0$/.test(q.name || '') || q.name === 'PlateText_front') q.visible = true; if (/^Door[FM]_[AB]$/.test(q.name || '')) q.rotation.y = 0; });
    const w = new THREE.Group(); w.rotation.order = 'YXZ'; w.userData.noT = true; w.add(g); _P.scene.add(w); return w; };
  const place = (g, x, y, yaw) => { g.position.set(x, _P.carGround(x, y) ?? _P.TZs(x, y), -y); g.rotation.set(0, -yaw, 0); };

  /* parked buses at the two depots */
  const DEP = []; let paint = 0x2a6fb5;
  const setup = () => { for (const s of STOPS) s.pose = pose(s, null);
    for (const k in LINES) { const L = LINES[k], s = byName(L.depot); s.pose = { x: L.dp[0], y: L.dp[1], yaw: L.dp[2] }; DEP.push({ line: k, x: s.pose.x, y: s.pose.y, yaw: s.pose.yaw, g: null, gone: false }); }      /* depot stands on the OSM bus lanes (the square's paving is not carriageway in the game) */
    try { buildSigns(); buildShelters(); } catch (e) { console.warn('bus signs', e); }
    _P.CARM.bus.root.traverse(q => { if (q.isMesh && q.material && q.material.name === 'CarPaint') paint = q.material.color.getHex(); }); };
  const depTick = () => { const px = _P.WALK.on ? _P.WALK.x : _P.S.x, py = _P.WALK.on ? _P.WALK.y : _P.S.y;
    for (const d of DEP) { if (d.gone && !(_P.VEH === 'car' && _P.CAR.type === 'bus' && R.line === d.line) && Math.hypot(d.x - px, d.y - py) > 250) d.gone = false;
      if (!d.gone && !d.g) { d.g = copy(); place(d.g, d.x, d.y, d.yaw); } if (d.g) d.g.visible = !d.gone; } };

  /* doors of the bus the player drives */
  const doors = o => { const r = _P.CARM.bus && _P.CARM.bus.root; if (!r) return; for (const n of ['DoorF_A', 'DoorF_B', 'DoorM_A', 'DoorM_B']) { const q = r.getObjectByName(n); if (!q) continue; const a = q.userData.openAngleDeg ?? (/_A$/.test(n) ? -85 : 85); q.rotation.y = a * Math.PI / 180 * o; } };

  /* people: the walker models of the NPC module, standing at a stop or walking to the door */
  const kinds = ['nainen_a', 'nainen_b', 'mies_a', 'mies_b', 'tytto', 'poika'];
  const person = (x, y, yaw) => { const N = window.__npc; if (!N || !N.mk) return null; const k = kinds[Math.random() < 0.85 ? Math.floor(Math.random() * 4) : 4 + Math.floor(Math.random() * 2)], c = N.mk(k); if (!c) return null;
    c.x = x; c.y = y; c.yaw = yaw; N.anim(c, 'Idle'); return c; };
  const show = (c, dt, vis) => { const z = _P.carGround(c.x, c.y) ?? _P.TZs(c.x, c.y); c.g.position.set(c.x, z, -c.y); c.g.rotation.y = -c.yaw; c.g.visible = vis; if (vis) c.mix.update(dt); };
  const drop = c => { if (window.__npc && window.__npc.free) window.__npc.free(c); };

  const door = (front) => { const sn = Math.sin(_P.CAR.yaw), cs = Math.cos(_P.CAR.yaw), f = front ? 4.4 : 0.05, r = 1.75; return { x: _P.CAR.x + sn * f + cs * r, y: _P.CAR.y + cs * f - sn * r }; };
  const waitAt = s => { if (s.w) return; s.w = []; const L = LINES[R.line], depot = s === L.stops[0]; const n = depot ? 2 + Math.floor(Math.random() * 3) : [0, 0, 1, 1, 1, 2, 2, 3][Math.floor(Math.random() * 8)];
    const yaw = s.pose ? s.pose.yaw - Math.PI / 2 : 0; for (let j = 0; j < n; j++) { const a = Math.random() * 6.28, r = 0.6 + Math.random() * 1.4, c = person(s.x + Math.sin(a) * r, s.y + Math.cos(a) * r, yaw + (Math.random() - 0.5)); if (c) s.w.push(c); } };
  const clearWait = s => { if (s.w) for (const c of s.w) drop(c); s.w = null; };
  const clearAll = () => { for (const s of STOPS) clearWait(s); for (const p of R.pax) if (p.c) drop(p.c); R.pax = []; if (R.queue) for (const q of R.queue) if (q.c) drop(q.c); R.queue = null; };

  /* sound: the stop bell (two soft tones) */
  const ding = () => { try { const A = typeof _P.actx !== 'undefined' && _P.actx ? _P.actx : null; if (!A) return; const t = A.currentTime;
    for (const [f, d] of [[988, 0], [784, 0.22]]) { const o = A.createOscillator(), g = A.createGain(); o.type = 'sine'; o.frequency.value = f; g.gain.setValueAtTime(0, t + d); g.gain.linearRampToValueAtTime(0.18, t + d + 0.01); g.gain.exponentialRampToValueAtTime(0.001, t + d + 0.6); o.connect(g).connect(A.destination); o.start(t + d); o.stop(t + d + 0.7); } } catch (e) {} };

  /* HUD */
  const css = document.createElement('style'); css.textContent = '#bus { left:14px; bottom:124px; padding:6px 10px; font-size:13px; display:none; gap:10px; align-items:center; color:var(--ink); max-width:min(420px,80vw); flex-wrap:wrap; }' +
    ' #bus.on { display:flex; } #bus b { font-variant-numeric:tabular-nums; } #bus .bell { padding:1px 7px; border-radius:6px; background:#333; color:#888; font-weight:700; } #bus .bell.on { background:#e0312b; color:#fff; }' +
    ' .touch #bus { bottom:auto; top:214px; } body.walk #bus:not(.ride) { display:none !important; } #tbell { bottom:302px; display:none; } body.busride #tbell { display:flex !important; }';
  document.head.appendChild(css);
  const el = document.createElement('div'); el.id = 'bus'; el.className = 'hud panel'; document.body.appendChild(el);
  { const t = document.getElementById('touch'); if (t) { const b = document.createElement('div'); b.className = 'tb'; b.id = 'tbell'; b.textContent = '🔔'; b.setAttribute('aria-label', 'Pysähtyy'); t.appendChild(b); b.addEventListener('pointerdown', e => { e.preventDefault(); bell(); }); } }
  const arrow = (dx, dy, yaw) => { let a = Math.atan2(dx, dy) - yaw; a = Math.atan2(Math.sin(a), Math.cos(a)); return '⬆↗➡↘⬇↙⬅↖'[((Math.round(a / (Math.PI / 4)) % 8) + 8) % 8]; };
  let hudT = 0;
  const hudBus = () => { const L = LINES[R.line], s = L.stops[R.i], d = Math.hypot(s.x - _P.CAR.x, s.y - _P.CAR.y);
    el.className = 'hud panel on'; el.innerHTML = '🚌 <b>Linja ' + L.n + '</b> · Seuraava: <b>' + short(s.n) + '</b> ' + (d > 30 ? Math.round(d) + ' m ' + arrow(s.x - _P.CAR.x, s.y - _P.CAR.y, _P.CAR.yaw) : '') +
      ' · 👥 <b>' + R.pax.length + '</b>' + (s.w && s.w.length ? ' · odottaa ' + s.w.length : '') + ' <span class="bell' + (R.req ? ' on' : '') + '">PYSÄHTYY</span> · <b>' + R.score + '</b> p'; };

  /* driving the line */
  const start = line => { clearAll(); R.line = line; R.i = 0; R.req = false; R.reqT = 0; R.served = false; R.near = 1e9; R.dwell = 0; R.door = 0; R.hp = _P.S.hp; R.queue = null;
    const L = LINES[line]; waitAt(L.stops[0]); _P.toast('🚌 Linja ' + L.n + ' → ' + L.to + '. Ensimmäinen pysäkki: ' + short(L.stops[0].n), 3.5); };
  const next = () => { const L = LINES[R.line]; clearWait(L.stops[R.i]); R.i = (R.i + 1) % L.stops.length; if (R.i === 0) { R.score += 30; _P.toast('Linja ajettu! +30', 2.2); }
    R.served = false; R.near = 1e9; R.req = false; R.reqT = R.pax.some(p => p.dest === R.i) ? 2 + Math.random() * 5 : 0; save(); };
  const save = () => { if (R.score > R.best) { R.best = R.score; try { localStorage.setItem('pori-bussi', String(R.best)); } catch (e) {} } };
  const driveTick = dt => {
    const L = LINES[R.line], s = L.stops[R.i], P = s.pose || s, d = Math.min(Math.hypot(P.x - _P.CAR.x, P.y - _P.CAR.y), Math.hypot(s.x - _P.CAR.x, s.y - _P.CAR.y));
    for (const k of [0, 1]) { const q = L.stops[(R.i + k) % L.stops.length]; if (Math.hypot(q.x - _P.CAR.x, q.y - _P.CAR.y) < 260) waitAt(q); }
    if (R.reqT > 0 && (R.reqT -= dt) <= 0) { R.req = true; ding(); }
    if (_P.S.hp < R.hp) { if (R.pax.length) { R.score = Math.max(0, R.score - Math.ceil((R.hp - _P.S.hp) / 2)); if (R.hp - _P.S.hp > 4) _P.toast('Matkustajat kaatuilevat! −' + Math.ceil((R.hp - _P.S.hp) / 2), 1.6); } R.hp = _P.S.hp; } else R.hp = _P.S.hp;
    const want = R.pax.some(p => p.dest === R.i), wait = s.w ? s.w.length : 0;
    if (!R.served && d < 18 && Math.abs(_P.CAR.v) < 0.6) R.dwell += dt; else if (!R.queue) R.dwell = 0;
    if (!R.served && R.dwell > 0.5 && !R.queue) {      /* stopped at the stop: doors open, those for here get off, the waiting get on */
      R.queue = []; const off = R.pax.filter(p => p.dest === R.i); R.pax = R.pax.filter(p => p.dest !== R.i);
      for (const p of off) R.queue.push({ off: true }); for (const c of s.w || []) R.queue.push({ c }); s.w = []; R.qt = 0.9; }
    R.door += ((R.queue ? 1 : 0) - R.door) * Math.min(1, dt * 3.5); doors(R.door);
    if (R.queue) {
      if (Math.abs(_P.CAR.v) > 1.2) { const left = R.queue.filter(q => q.c).length; for (const q of R.queue) if (q.c) drop(q.c); if (left) { R.score = Math.max(0, R.score - 5 * left); _P.toast('Ajoit ovet auki pois – ' + left + ' jäi kyydistä! −' + 5 * left, 2.2); } R.queue = null; R.served = true; next(); return; }
      const q = R.queue[0];
      if (!q) { if (_P.input.f > 0.05 || (R.qt -= dt) < -1.5) { R.queue = null; R.served = true; next(); } return; }
      if (q.off) { if ((R.qt -= dt) <= 0) { const D = door(false); if (window.__npc && window.__npc.arrive) window.__npc.arrive(D.x, D.y); R.score += 10; _P.toast('Matkustaja jäi pois: ' + short(s.n) + ' +10', 1.4); R.queue.shift(); R.qt = 0.9; } return; }
      const D = door(true), dx = D.x - q.c.x, dy = D.y - q.c.y, l = Math.hypot(dx, dy); window.__npc.anim(q.c, 'Walk');
      if (l < 0.35) { drop(q.c); const n = L.stops.length; R.pax.push({ dest: (R.i + 1 + Math.floor(Math.random() * Math.min(5, n - 1))) % n }); R.score += 2; R.queue.shift(); }
      else { const v = Math.min(l, 1.35 * dt); q.c.x += dx / l * v; q.c.y += dy / l * v; q.c.yaw = Math.atan2(dx, dy); if (q.c.act.Walk) q.c.act.Walk.timeScale = 1.35 / (window.__npc.stride[q.c.k] || 1.2); }
      return; }
    R.near = Math.min(R.near, d);
    const passed = (R.near < 30 && d > R.near + 25) || Math.hypot(L.stops[(R.i + 1) % L.stops.length].x - _P.CAR.x, L.stops[(R.i + 1) % L.stops.length].y - _P.CAR.y) < 25;
    if (!R.served && passed) {
      if (want) { const n = R.pax.filter(p => p.dest === R.i).length; R.score = Math.max(0, R.score - 15 * n); _P.toast('Ohitit pysäkin, vaikka joku painoi nappia! −' + 15 * n, 2.4); for (const p of R.pax) if (p.dest === R.i) p.dest = (R.i + 1) % L.stops.length; }
      else if (wait) { R.score = Math.max(0, R.score - 5 * wait); _P.toast(wait + ' jäi odottamaan pysäkille ' + short(s.n) + ' −' + 5 * wait, 2.2); }
      next(); } };

  /* live buses (Digitransit MQTT, GTFS-RT vehicle positions) */
  const LIVE = new Map(); let ws = null, wsT = 0, wsBad = 0, buf = new Uint8Array(0), pingT = 0;
  const enc = s => new TextEncoder().encode(s), cat = (...a) => { const o = new Uint8Array(a.reduce((n, x) => n + x.length, 0)); let i = 0; for (const x of a) { o.set(x, i); i += x.length; } return o; };
  const remLen = n => { const o = []; do { let b = n % 128; n = Math.floor(n / 128); if (n > 0) b |= 128; o.push(b); } while (n > 0); return Uint8Array.from(o); };
  const str = s => { const b = enc(s); return cat(Uint8Array.from([b.length >> 8, b.length & 255]), b); };
  const pkt = (h, body) => cat(Uint8Array.from([h]), remLen(body.length), body);
  const connect = () => { if (ws || wsBad > 5) return; try { ws = new WebSocket('wss://mqtt.digitransit.fi', ['mqtt']); } catch (e) { ws = null; wsBad++; return; } ws.binaryType = 'arraybuffer';
    ws.onopen = () => { ws.send(pkt(0x10, cat(str('MQTT'), Uint8Array.from([4, 2, 0, 60]), str('porikopteri-' + Math.random().toString(36).slice(2, 10))))); ws.send(pkt(0x82, cat(Uint8Array.from([0, 1]), str('/gtfsrt/vp/Pori/#'), Uint8Array.from([0])))); };
    ws.onmessage = e => { buf = cat(buf, new Uint8Array(e.data)); parse(); };
    ws.onclose = ws.onerror = () => { if (ws) { ws.onclose = ws.onerror = null; try { ws.close(); } catch (x) {} } ws = null; wsBad++; wsT = 10 + wsBad * 10; }; };
  const parse = () => { for (;;) { if (buf.length < 2) return; let m = 1, n = 0, i = 1, b; do { if (i >= buf.length) return; b = buf[i++]; n += (b & 127) * m; m *= 128; } while (b & 128); if (buf.length < i + n) return;
      const h = buf[0], t = h >> 4, body = buf.slice(i, i + n); buf = buf.slice(i + n); if (t === 3) { const tl = (body[0] << 8) | body[1], topic = new TextDecoder().decode(body.subarray(2, 2 + tl)); let o = 2 + tl; if ((h >> 1 & 3) > 0) o += 2; try { onVP(topic, body.subarray(o)); } catch (e) {} } else if (t === 2) wsBad = 0; } };
  /* minimal protobuf reader for FeedMessage > entity > vehicle > position / trip */
  const pb = (u, f) => { const dv = new DataView(u.buffer, u.byteOffset, u.byteLength); let p = 0; const vi = () => { let r = 0, s = 1, b; do { b = u[p++]; r += (b & 127) * s; s *= 128; } while (b & 128); return r; };
    while (p < u.length) { const k = vi(), fn = Math.floor(k / 8), wt = k & 7; if (wt === 0) f(fn, 0, vi()); else if (wt === 2) { const l = vi(); f(fn, 2, u.subarray(p, p + l)); p += l; } else if (wt === 5) { f(fn, 5, dv.getFloat32(p, true)); p += 4; } else if (wt === 1) { f(fn, 1, dv.getFloat64(p, true)); p += 8; } else return; } };
  const onVP = (topic, u) => { const T = topic.split('/'), line = T[18] || T[7] || '?', head = T[9] || '', vid = T[13] || '';
    pb(u, (f, w, v) => { if (f !== 2 || w !== 2) return; pb(v, (f2, w2, v2) => { if (f2 !== 4 || w2 !== 2) return; let lat = null, lon = null, br = null, sp = 0;
      pb(v2, (f3, w3, v3) => { if (f3 === 2 && w3 === 2) pb(v3, (f4, w4, v4) => { if (f4 === 1) lat = v4; else if (f4 === 2) lon = v4; else if (f4 === 3) br = v4; else if (f4 === 5) sp = v4; }); });
      if (lat === null) return; const x = (lon - 21.796) * 53278, y = (lat - 61.486) * 111437; if (x < _P.OX0 + 50 || x > _P.OX1 - 50 || y < _P.OY0 + 50 || y > _P.OY1 - 50) { const o = LIVE.get(vid); if (o) o.t = -1e9; return; }
      const now = performance.now() / 1000; let o = LIVE.get(vid); if (!o) { o = { id: vid, x, y, yaw: br !== null ? br * Math.PI / 180 : 0, hd: br !== null ? br * Math.PI / 180 : 0, g: null, h: [] }; LIVE.set(vid, o); }
      o.sp = sp || 0; if (br !== null && (sp > 0.5 || o.br === undefined)) o.br = br * Math.PI / 180; o.line = line; o.head = head; o.t = now;
      const L = o.h[o.h.length - 1]; if (!L || now - L.t > 0.3) { o.h.push({ t: now, x, y, sp: o.sp, br: o.br || 0 }); if (o.h.length > 14) o.h.shift(); } }); }); };
  /* the street network the traffic uses (CITY.r centrelines), in a 40 m grid: a live bus is drawn on its right-hand lane, 1.7 m off the centreline like the
     traffic, on the nearest street that runs its way (the GPS point is often a few metres off our map) */
  const SEG = [], SG = new Map(), SGS = 40;
  const segInit = () => { CITY.r.forEach(r => { if (!r.k) return; for (let i = 0; i + 3 < r.p.length; i += 2) { const ax = r.p[i], ay = r.p[i + 1], bx = r.p[i + 2], by = r.p[i + 3], l = Math.hypot(bx - ax, by - ay); if (l < 0.5) continue;
      const sg = { ax, ay, bx, by, l, ux: (bx - ax) / l, uy: (by - ay) / l }; SEG.push(sg);
      for (let gi = Math.floor((Math.min(ax, bx) - 25) / SGS); gi <= Math.floor((Math.max(ax, bx) + 25) / SGS); gi++) for (let gj = Math.floor((Math.min(ay, by) - 25) / SGS); gj <= Math.floor((Math.max(ay, by) + 25) / SGS); gj++) { const k = gi + ',' + gj; let a = SG.get(k); if (!a) SG.set(k, a = []); a.push(sg); } } }); };
  const TERM = [[-2, 44, 32, 126], [-445, -975, -335, -870]];      /* bus stations (Kauppatori stands, Matkakeskus): drawn where the data says, not pulled onto a street */
  const snap = (x, y, yaw) => { if (TERM.some(b => x > b[0] && x < b[2] && y > b[1] && y < b[3])) return null; const L = SG.get(Math.floor(x / SGS) + ',' + Math.floor(y / SGS)); if (!L) return null; const fx = Math.sin(yaw), fy = Math.cos(yaw); let b = null, bs = 1e9;
    for (const q of L) { const t = Math.max(-4, Math.min(q.l + 4, (x - q.ax) * q.ux + (y - q.ay) * q.uy)), px = q.ax + q.ux * t, py = q.ay + q.uy * t, d = Math.hypot(x - px, y - py); if (d > 15) continue;
      const c = fx * q.ux + fy * q.uy, sc = d + (1 - Math.abs(c)) * 14; if (sc < bs) { bs = sc; b = { px, py, ux: c >= 0 ? q.ux : -q.ux, uy: c >= 0 ? q.uy : -q.uy }; } }
    return b && { x: b.px + b.uy * 1.7, y: b.py - b.ux * 1.7, yaw: Math.atan2(b.ux, b.uy) }; };
  const DELAY = 2.0;      /* drawn 2 s behind the data: always between two received points, so the movement is smooth */
  let pool = [];
  const liveTick = dt => { if (!document.hidden) { if (!ws && (wsT -= dt) <= 0) connect(); if (ws && ws.readyState === 1 && (pingT += dt) > 30) { pingT = 0; ws.send(Uint8Array.from([0xc0, 0])); } }
    const now = performance.now() / 1000, px = _P.WALK.on ? _P.WALK.x : _P.S.x, py = _P.WALK.on ? _P.WALK.y : _P.S.y; const vis = [];
    if (!SEG.length) segInit();
    for (const [k, o] of LIVE) { if (now - o.t > 90) { if (o.g) { o.g.visible = false; pool.push(o.g); o.g = null; } LIVE.delete(k); continue; }
      const h = o.h, rt = now - DELAY; let bx, by;
      if (rt <= h[0].t) { bx = h[0].x; by = h[0].y; }
      else if (rt >= h[h.length - 1].t) { const a = h[h.length - 1], e = Math.min(2, rt - a.t); bx = a.x + Math.sin(a.br) * a.sp * e; by = a.y + Math.cos(a.br) * a.sp * e; }      /* data late: carry on briefly */
      else { let i = h.length - 2; while (i > 0 && h[i].t > rt) i--; const a = h[i], b = h[i + 1], u = (rt - a.t) / Math.max(0.01, b.t - a.t); bx = a.x + (b.x - a.x) * u; by = a.y + (b.y - a.y) * u; }
      if (o.rx !== undefined) { const mx = bx - o.rx, my = by - o.ry; if (Math.hypot(mx, my) > 0.04) { let a = Math.atan2(mx, my) - o.hd; a = Math.atan2(Math.sin(a), Math.cos(a)); o.hd += a * Math.min(1, dt * 3); } }
      o.rx = bx; o.ry = by;
      const q = snap(bx, by, o.hd) || { x: bx, y: by, yaw: o.hd };
      if (!o.on || Math.hypot(q.x - o.x, q.y - o.y) > 30) { o.x = q.x; o.y = q.y; o.yaw = q.yaw; o.on = true; }
      else { const f = Math.min(1, dt * 5); o.x += (q.x - o.x) * f; o.y += (q.y - o.y) * f; let a = q.yaw - o.yaw; a = Math.atan2(Math.sin(a), Math.cos(a)); o.yaw += a * Math.min(1, dt * 4); }
      o.d = Math.hypot(o.x - px, o.y - py); if (o.d < 650) vis.push(o); else if (o.g) { o.g.visible = false; pool.push(o.g); o.g = null; } }
    vis.sort((a, b) => a.d - b.d); vis.forEach((o, i) => { if (i >= (_P.isTouch ? 5 : 9)) { if (o.g) { o.g.visible = false; pool.push(o.g); o.g = null; } return; }
      if (!o.g) o.g = pool.pop() || copy(); o.g.visible = true; place(o.g, o.x, o.y, o.yaw); }); };

  /* riding a live bus */
  const rideNear = (x, y) => { if (R.ride) return 'busout'; let b = null, bd = 1e9; for (const o of LIVE.values()) { if (!o.g || o.sp > 1) continue; const dx = x - o.x, dy = y - o.y, sn = Math.sin(o.yaw), cs = Math.cos(o.yaw), f = dx * sn + dy * cs, r = dx * cs - dy * sn;
      const e = Math.hypot(Math.max(0, Math.abs(f) - 6.1), Math.max(0, Math.abs(r) - 1.3)); if (e < 2.2 && e < bd) { bd = e; b = o; } } R.cand = b; return b ? 'bus' : ''; };
  const bell = () => { if (!R.ride || R.bell) return; R.bell = true; ding(); _P.toast('🔔 Pysähtyy', 1.2); };
  const getOff = msg => { const o = R.ride; R.ride = null; R.bell = false; document.body.classList.remove('busride'); el.className = 'hud panel';
    if (o) { const sn = Math.sin(o.yaw), cs = Math.cos(o.yaw); let x = o.x + cs * 2.4, y = o.y - sn * 2.4; if (!_P.walkFree(x, y)) { x = o.x - cs * 2.4; y = o.y + sn * 2.4; } _P.WALK.x = x; _P.WALK.y = y; _P.WALK.z = _P.carGround(x, y) ?? _P.TZs(x, y); _P.WALK.yaw = o.yaw + Math.PI / 2; }
    _P.walkG.visible = true; _P.camPos.set(_P.WALK.x - Math.sin(_P.WALK.yaw) * 3, _P.WALK.z + 2, -_P.WALK.y + Math.cos(_P.WALK.yaw) * 3); _P.toast(msg, 2.2); };
  const ride = () => { const o = R.cand; if (!o) return; R.ride = o; R.bell = false; R.still = 0; R.moved = false; document.body.classList.add('busride');
    _P.toast('🚌 Kyydissä: linja ' + o.line + (o.head ? ' → ' + o.head : '') + (_P.isTouch ? ' – 🔔 pysäyttää' : ' – N pysäyttää'), 3); };
  const rideTick = dt => { const o = R.ride; if (!o.g || !LIVE.has(o.id)) { getOff('Bussi poistui kartalta – jäit pois'); return; }
    _P.WALK.x = o.x; _P.WALK.y = o.y; _P.WALK.v = 0; _P.walkG.visible = false; if (o.sp > 2) R.moved = true;
    const now = performance.now() / 1000; if (o.sp < 0.4) { if (!R.st0) R.st0 = now; R.still = now - R.st0; } else { R.st0 = 0; R.still = 0; }      /* wall-clock: the halt is real time */
    if (R.bell && R.moved && R.still > 2) { getOff('Jäit pois bussista ' + o.line); return; }
    el.className = 'hud panel on ride'; el.innerHTML = '🚌 <b>Linja ' + o.line + '</b>' + (o.head ? ' → ' + o.head : '') + ' · ' + Math.round(o.sp * 3.6) + ' km/h <span class="bell' + (R.bell ? ' on' : '') + '">PYSÄHTYY</span>'; };
  const cam = dt => { const o = R.ride; if (!o) return false; const sn = Math.sin(o.yaw), cs = Math.cos(o.yaw), z = _P.carGround(o.x, o.y) ?? _P.TZs(o.x, o.y);
    _P.tmp.set(o.x - sn * 14, z + 5.5, -o.y + cs * 14); _P.camPos.lerp(_P.tmp, 1 - Math.exp(-dt * 3)); _P.tmp2.set(o.x + sn * 8, z + 1.8, -o.y - cs * 8); _P.camLook.lerp(_P.tmp2, 1 - Math.exp(-dt * 5)); _P.camera.position.copy(_P.camPos); _P.camera.lookAt(_P.camLook); return true; };

  let acc = 0;
  const tick = dt => { if (!_P.started) return;
    if (!_P.CARM.bus) { if (!_P.carLoading.bus) _P.loadCar('bus'); return; }
    if (!ready) { if (!window.__roads && (acc += dt) < 40) return; ready = true; setup(); }
    depTick(); liveTick(dt);
    if (R.ride) rideTick(dt);
    const driving = _P.VEH === 'car' && _P.CAR.type === 'bus' && !_P.WALK.on && R.line;
    if (driving) { driveTick(dt); if ((hudT -= dt) <= 0) { hudT = 0.2; hudBus(); } const L = LINES[R.line], s = L.stops[R.i], P = s.pose || s;
      mk.visible = true; mk.position.set(s.x, _P.carGround(s.x, s.y) ?? _P.TZs(s.x, s.y), -s.y); mk.ring.visible = true; mk.ring.position.set(P.x, (_P.carGround(P.x, P.y) ?? _P.TZs(P.x, P.y)) + 0.08, -P.y); }
    else { mk.visible = false; mk.ring.visible = false; if (!R.ride) el.className = 'hud panel'; if (R.door > 0.01 && !(_P.VEH === 'car' && _P.CAR.type === 'bus')) { R.door = 0; doors(0); } }
    if (R.line) { const vis = []; for (const k of [0, 1]) { const q = LINES[R.line].stops[(R.i + k) % LINES[R.line].stops.length]; if (q.w) for (const c of q.w) vis.push(c); } if (R.queue) for (const q of R.queue) if (q.c) vis.push(q.c);
      const px = _P.WALK.on ? _P.WALK.x : _P.S.x, py = _P.WALK.on ? _P.WALK.y : _P.S.y; for (const c of vis) show(c, dt, Math.hypot(c.x - px, c.y - py) < 160); } };
  window.__bus = { R, LINES, STOPS, LIVE, DEP,
    near: (x, y) => { if (!ready) return null; for (const d of DEP) { if (d.gone) continue; const dx = x - d.x, dy = y - d.y, sn = Math.sin(d.yaw), cs = Math.cos(d.yaw), f = dx * sn + dy * cs, r = dx * cs - dy * sn;
        if (Math.hypot(Math.max(0, Math.abs(f) - 6.1), Math.max(0, Math.abs(r) - 1.3)) < 2.4) return { x: d.x, y: d.y, yaw: d.yaw, hex: paint, dep: d }; } return null; },
    take: T => { T.dep.gone = true; if (T.dep.g) T.dep.g.visible = false; start(T.dep.line); },
    rideNear, ride, bell, out: () => { if (R.ride && R.ride.sp < 0.6) getOff('Jäit pois bussista'); else _P.toast(_P.isTouch ? 'Bussi liikkuu – paina 🔔' : 'Bussi liikkuu – paina N', 1.6); },
    hint: k => k === 'busout' ? 'jää pois' : R.cand ? 'nouse bussiin ' + R.cand.line + (R.cand.head ? ' → ' + R.cand.head : '') : '', cam,
    tick: dt => { if (broken) return; try { tick(dt); } catch (e) { broken = true; window.__bus.err = String(e && e.stack || e); console.warn('bussi', e); el.className = 'hud panel'; } } };
  window.__busTick = dt => window.__bus.tick(dt);
}
}
