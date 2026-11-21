// moduulit/kyydit.js – siirretty pääskriptistä (src/js/160_kyydit.js) omaksi moduulikseen 21.11.2026.
// Pääskriptin muuttujat tulevat oliossa P (getterit pitävät ne ajan tasalla); kirjastot ja data tuodaan suoraan.
// Kutsu ja P:n sisältö: src/js/160_kyydit.js. Uusi riippuvuus pääskriptiin → lisää se sinne P-olioon.
import * as THREE from '../three.module.min.js';

// ---------- kyydit (owner 20.11.2026: "jos botti tekee kysymyksen, pelaaja voi hyväksyä sen ja esim kuskata botin Jazzeille, jolloin kerää pisteitä") ----------
// While the player drives (car, bike: the passenger sits on the rack) or flies, now and then a lone walker nearby stops, waves (a yellow arrow
// above the head) and asks for a ride to one of the landmarks of the daily-round pool. Stop beside them (car/bike 7 m; helicopter: land within 20 m)
// and press Y (or tap the button) to take them; a green column marks the destination; stop there (30 m, helicopter 45 m) to drop them off.
// Points (owner's choice): distance + speed bonus − knocks: base = straight-line metres / 10; up to +50 % when faster than the par time for the vehicle;
// every hit point lost on the way takes 2 % (at least 20 % stays). Rides and points are kept in this browser (localStorage 'pori-kyydit').
export default function kaynnista(P) {
(() => {
  const WHY = { 'Kirjurinluoto': 'Jazzeille Kirjurinluotoon', 'Porin kauppahalli': 'kauppahalliin, lohisoppaa', 'Promenadikeskus': 'Promenadikeskukseen konserttiin',
    'BePop': 'BePopiin', 'Porin vesitorni': 'vesitornille', 'Porin pääkirjasto': 'kirjastoon palauttamaan kirjat', 'Porin Teatteri': 'teatteriin, näytös alkaa kohta',
    'Satakunnan Museo': 'Satakunnan Museoon', 'Taavi-silta': 'Taavi-sillalle', 'Raatihuone': 'Raatihuoneelle', 'Porinsilta': 'Porinsillalle', 'Kauppakeskus Puuvilla': 'Puuvillaan shoppailemaan',
    'Linnansilta': 'Linnansillalle', 'Keski-Porin kirkko': 'kirkkoon', 'Porin rautatieasema': 'rautatieasemalle, juna lähtee', 'SAMK-kampus': 'SAMKille luennolle',
    'Isomäki Areena': 'Isomäelle Ässien peliin', 'Porin stadion': 'stadionille', 'Juseliuksen mausoleumi': 'Juseliuksen mausoleumille', 'Aittaluodon voimalaitos': 'Aittaluotoon töihin',
    'Sampo-Rosenlew': 'Sampo-Rosenlewille', 'Keskustan uimahalli': 'uimahalliin', 'Urheilutalo': 'urheilutalolle', 'IsoKarhu': 'IsoKarhuun', 'Cygnaeuksen koulu': 'Cygnaeuksen koululle',
    'Porin oikeustalo': 'oikeustalolle', 'Barco-laiva': 'Barcolle' };
  const ASK = ['Hei! Saisinko kyydin {}?', 'Moro, viekkö mut {}?', 'Anteeks, pääsiskö mukaan {}?', 'Hei kuski! {} – ehditäänkö?'];
  const R = { st: 0, t: 8 + Math.random() * 15, c: null, p: null, d: null, t0: 0, hp0: 100, hpMin: 100, from: null };   // st 0 none, 1 offer, 2 riding
  try { Object.assign(R, { tot: 0, n: 0 }, JSON.parse(localStorage.getItem('pori-kyydit') || '{}')); } catch (e) { R.tot = 0; R.n = 0; }
  window.__ride = R;
  // HUD: counter + the offer button
  const css = document.createElement('style'); css.textContent = '#ride { left:14px; bottom:124px; padding:6px 10px; font-size:13px; display:none; gap:8px; align-items:center; color:var(--ink); max-width:min(330px,70vw); }' +
    ' #ride.on { display:flex; } #ride b { font-variant-numeric:tabular-nums; } #ride button { font:inherit; padding:4px 10px; border-radius:8px; border:0; background:#f5c400; color:#111; font-weight:700; cursor:pointer; }' +
    ' .touch #ride { bottom:auto; top:214px; } body.walk #ride { display:none !important; }';
  document.head.appendChild(css);
  const el = document.createElement('div'); el.id = 'ride'; el.className = 'hud panel'; el.innerHTML = '<span id="rtxt"></span><button id="rok" style="display:none">✔ Ota kyytiin (Y)</button>'; document.body.appendChild(el);
  const txt = el.querySelector('#rtxt'), ok = el.querySelector('#rok');
  ok.addEventListener('pointerdown', e => { e.preventDefault(); R.accept(); });
  // markers: a bobbing yellow arrow over the person asking, a green light column at the destination
  const arrow = new THREE.Mesh(new THREE.ConeGeometry(0.35, 0.8, 12), new THREE.MeshBasicMaterial({ color: 0xf5c400 })); arrow.rotation.x = Math.PI; arrow.visible = false; arrow.userData.noT = true; P.scene.add(arrow);
  const col = new THREE.Mesh(new THREE.CylinderGeometry(4, 4, 80, 24, 1, true), new THREE.MeshBasicMaterial({ color: 0x35d07f, transparent: true, opacity: 0.28, depthWrite: false, side: THREE.DoubleSide }));
  col.visible = false; col.userData.noT = true; P.scene.add(col);
  const save = () => { try { localStorage.setItem('pori-kyydit', JSON.stringify({ tot: R.tot, n: R.n })); } catch (e) {} };
  const bike = () => P.VEH === 'car' && P.CAR.type === 'bike', veh = () => P.VEH !== 'car' ? 'heli' : bike() ? 'bike' : 'car';
  const ground = (x, y) => { const g = P.carGround(x, y); return g === null || g === undefined ? P.TZs(x, y) : g; };
  const dir = (x, y) => { const a = Math.atan2(x - P.S.x, y - P.S.y) - P.S.yaw, k = Math.round(((Math.atan2(Math.sin(a), Math.cos(a)) / (Math.PI / 4)) + 8)) % 8; return ['⬆', '↗', '➡', '↘', '⬇', '↙', '⬅', '↖'][k]; };
  const show = () => { const base = '🚕 Kyydit <b>' + R.n + '</b> · <b>' + R.tot + '</b> p';
    if (R.st === 2) txt.innerHTML = '🚕 ' + R.d.n + ' · <b>' + Math.round(Math.hypot(R.d.x - P.S.x, R.d.y - P.S.y)) + ' m</b> ' + dir(R.d.x, R.d.y);
    else if (R.st === 1) txt.innerHTML = '🙋 Kyytipyyntö ' + Math.round(Math.hypot(R.c.x - P.S.x, R.c.y - P.S.y)) + ' m ' + dir(R.c.x, R.c.y);
    else txt.innerHTML = base;
    el.classList.toggle('on', P.started && !P.WALK.on && (R.st > 0 || R.n > 0)); };
  const clear = () => { arrow.visible = false; col.visible = false; ok.style.display = 'none'; };
  const offer = () => { const N = window.__npc; if (!N || !N.parties) return;
    let best = null, bd = 1e9; for (const p of N.parties) { if (p.m.length !== 1 || p.sit || p.hold > 0 || p.wait) continue; const c = p.m[0]; if (c.kid) continue;
      const d = Math.hypot(c.x - P.S.x, c.y - P.S.y); if (d < 15 || d > 70) continue; if (d < bd) { bd = d; best = p; } }
    if (!best) return; const c = best.m[0], L = P.POOL.filter(q => Math.hypot(q.x - c.x, q.y - c.y) > 350); if (!L.length) return;
    const d = L[Math.floor(Math.random() * L.length)], why = WHY[d.n] || d.n; Object.assign(R, { st: 1, c, p: best, d, t: 45 });
    P.toast('🙋 ' + ASK[Math.floor(Math.random() * ASK.length)].replace('{}', why) + ' – pysähdy viereen', 5); };
  R.accept = () => { if (R.st !== 1 || !R.c) return; const c = R.c, d = Math.hypot(c.x - P.S.x, c.y - P.S.y), v = veh();
    if (!P.S.landed || d > (v === 'heli' ? 20 : 7) || (v === 'heli' && P.S.alt > ground(P.S.x, P.S.y) + 3)) { P.toast(v === 'heli' ? 'Laskeudu lähemmäs (20 m)' : 'Pysähdy viereen (7 m)', 1.8); return; }
    R.freePc(); if (v === 'bike' && window.__npc.mk && c.act && c.act.Passenger && c.g) {      // bicycle: an own copy of this walker (same model, same tints) sits on the rack, clip Passenger (see __takeTick)
      const n = window.__npc.mk(c.k), A = [], Bm = []; c.g.traverse(o => { if (o.isMesh) A.push(o); }); n.g.traverse(o => { if (o.isMesh) Bm.push(o); }); for (const m of n.g.mats || []) m.dispose(); n.g.mats = [];
      Bm.forEach((o, i) => { if (!A[i]) return; if ((c.g.mats || []).includes(A[i].material)) { o.material = A[i].material.clone(); o.material.userData.noT = true; n.g.mats.push(o.material); } else o.material = A[i].material; });
      n.mix.stopAllAction(); for (const q of ['Passenger', 'PassengerLeanL', 'PassengerLeanR']) if (n.act[q]) { n.act[q].play(); n.act[q].weight = q === 'Passenger' ? 1 : 0; } n.cur = 'Passenger'; n.g.visible = false; R.pc = n; }
    c.x = 1e6; c.y = 1e6;                                                               // the walker leaves the street (the npc cleanup frees the model)
    Object.assign(R, { st: 2, c: null, p: null, t0: performance.now(), hp0: P.S.hp, hpMin: P.S.hp, from: { x: P.S.x, y: P.S.y }, v });
    const g = ground(R.d.x, R.d.y); col.position.set(R.d.x, g + 40, -R.d.y); col.visible = true; arrow.visible = false; ok.style.display = 'none';
    P.toast(v === 'bike' ? '🚲 Kyytiläinen hyppäsi tarakalle – ' + R.d.n : '🚕 Kyytiin! Kohde: ' + R.d.n, 3); };
  R.freePc = () => { if (R.pc) { if (window.__npc && window.__npc.free) window.__npc.free(R.pc); else P.scene.remove(R.pc.g); R.pc = null; } };
  const drop = () => { const dist = Math.hypot(R.d.x - R.from.x, R.d.y - R.from.y), secs = (performance.now() - R.t0) / 1000, par = dist / ({ heli: 14, car: 8, bike: 5 }[R.v]) + 20;
    const fast = Math.max(0, Math.min(1, (par - secs) / (par * 0.5))), dmg = Math.max(0, R.hp0 - R.hpMin), keep = Math.max(0.2, 1 - dmg * 0.02);
    const pts = Math.max(1, Math.round(dist / 10 * (1 + 0.5 * fast) * keep)); R.tot += pts; R.n++; save();
    if (R.pc) { const c = R.pc, x = P.S.x - Math.cos(P.S.yaw) * 0.7, y = P.S.y + Math.sin(P.S.yaw) * 0.7; c.mix.stopAllAction(); for (const q in c.act) c.act[q].weight = 1; c.cur = ''; c.yaw = P.S.yaw - Math.PI / 2; c.g.rotation.set(0, -c.yaw, 0); c.g.visible = true;      // the bicycle passenger hops off on the left (the side they sit facing) and walks away
      if (window.__npc && window.__npc.arrive && window.__npc.arrive(x, y, c)) R.pc = null; else R.freePc(); }
    else if (window.__npc && window.__npc.arrive) window.__npc.arrive(P.S.x, P.S.y);            // somebody gets out and walks off
    P.toast('✅ Perillä: ' + R.d.n + ' · +' + pts + ' p' + (fast > 0.05 ? ' (nopea!)' : '') + (dmg > 2 ? ' · kolhuja −' + Math.round((1 - keep) * 100) + ' %' : ''), 4);
    Object.assign(R, { st: 0, d: null, t: 15 + Math.random() * 30 }); clear(); };
  let broken = false;
  window.__rideTick = dt => { if (broken) return; try { tick(dt); } catch (e) { broken = true; clear(); el.classList.remove('on'); console.warn('kyydit', e); } };   // a bug here must not stop the game loop
  const tick = dt => { if (!P.started) return; const walking = P.WALK.on;
    if (R.st === 0) { if (!walking && !P.S.dead && !(P.VEH === 'car' && P.CAR.type === 'bus') && (R.t -= dt) < 0) { R.t = 6; offer(); } }
    else if (R.st === 1) { const c = R.c, d = c ? Math.hypot(c.x - P.S.x, c.y - P.S.y) : 1e9;
      if (!c || d > 160 || (R.t -= dt) < 0 || P.S.dead) { if (c && d < 160 && !P.S.dead) P.toast('Kyytipyyntö raukesi', 1.6); R.st = 0; R.c = R.p = null; R.t = 20 + Math.random() * 25; clear(); }
      else { R.p.hold = 1; arrow.visible = true; arrow.position.set(c.x, c.z + 2.6 + Math.sin(performance.now() / 250) * 0.15, -c.y); arrow.rotation.y += dt * 2;
        const v = veh(), near = !walking && P.S.landed && d < (v === 'heli' ? 20 : 7); ok.style.display = near ? '' : 'none'; } }
    else if (R.st === 2) { if (P.S.dead) { P.toast('Kyyti keskeytyi', 2); R.st = 0; R.t = 30; R.freePc(); clear(); }
      else { R.hpMin = Math.min(R.hpMin, P.S.hp); const d = Math.hypot(R.d.x - P.S.x, R.d.y - P.S.y);
        if (!walking && P.S.landed && d < (R.v === 'heli' ? 45 : 30) && (R.v !== 'heli' || P.S.alt < ground(P.S.x, P.S.y) + 3)) drop(); } }
    show(); };
})();
}
