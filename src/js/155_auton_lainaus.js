// 20.11.2026 (owner: "can a parked car be taken into use"): on foot next to a parked car (the aerial-photo ones in window.__parked, a traffic car standing
// parked, or the car the player left earlier) Enter borrows it: the player's car model moves to its place and heading and takes its colour, the parked one
// disappears (a traffic car starts again far away). The car driven until then stays where it was as a copy (TAKE.left, one at a time, its damage kept) and
// can be taken back. From the helicopter the game switches to driving; the helicopter waits where it landed (TAKE.heli) and is boarded again on foot -
// the landmark round pauses meanwhile, so a car cannot finish a helicopter round.
const TAKE = { left: null, heli: null, hex: null, applied: null, tgt: null }; window.__take = TAKE;
const takeType = T => T.l ? T.l.type : T.bp ? 'bus' : T.b ? 'bike' : ['hatch', 'estate', 'estate', 'van'][T.p ? T.p.k : T.c.k] || 'hatch';      /* parked types: hatch, saloon, SUV, van */
function takeNear() { const x = WALK.x, y = WALK.y; if (TAKE.heli && VEH === 'car' && !window.__heliLukko && Math.hypot(TAKE.heli.x - x, TAKE.heli.y - y) < 6) return 'heli';
  let best = null, bd = 3.4; if (TAKE.left && Math.hypot(TAKE.left.x - x, TAKE.left.y - y) < 4.2) { TAKE.tgt = { l: TAKE.left }; return 'take'; }
  if (window.__parked) for (const p of window.__parked) { if (p.gone) continue; const dx = p.x - x; if (dx > 3.4 || dx < -3.4) continue; const d = Math.hypot(dx, p.y - y); if (d < bd) { bd = d; best = { p }; } }
  for (const c of cars) if (c.pk && c.pk.ph === 1 && c.wx !== undefined) { const d = Math.hypot(c.wx - x, c.wy - y); if (d < bd) { bd = d; best = { c }; } }
  if (window.__bikes) { let kd = 2.0; for (const b of window.__bikes) { if (b.gone) continue; const dx = b.x - x; if (dx > 2 || dx < -2) continue; const d = Math.hypot(dx, b.y - y); if (d < kd) { kd = d; best = { b }; } } }      /* a parked bicycle, closer than any car */
  if (window.__bus) { const q = window.__bus.near(x, y); if (q) best = { bp: q }; }      /* a parked bus at Kauppatori or the Matkakeskus */
  TAKE.tgt = best; if (best) loadCar(takeType(best));      /* fetch that car's model as soon as the offer shows */
  return best ? 'take' : ''; }
function takeLeave() {      /* the car driven so far stays behind as a copy */
  if (TAKE.left) { scene.remove(TAKE.left.g); TAKE.left = null; } if (!carG.children.length) return;
  const g = new THREE.Group(), body = carG.children[0].clone(true), mats = new Map(); g.rotation.order = 'YXZ'; g.userData.noT = true; g.add(body); let hex = 0x103070;
  body.traverse(q => { if (q.isMesh && q.material && /^(Car|Bike)Paint$/.test(q.material.name)) { if (!mats.has(q.material)) { const m = q.material.clone(); m.userData.noT = true; mats.set(q.material, m); hex = m.color.getHex(); } q.material = mats.get(q.material); } });
  g.position.set(CAR.x, CAR.z, -CAR.y); g.rotation.set(0, -CAR.yaw, CAR.type === 'bike' ? 0.13 : 0); body.rotation.z = 0; scene.add(g); TAKE.left = { x: CAR.x, y: CAR.y, yaw: CAR.yaw, hp: S.hp, hex, g, type: CAR.type || 'hatch' }; }
function takeDo(k) { if (window.__race && (window.__race.st === 1 || window.__race.st === 2)) return;
  if (k === 'heli') { const H = TAKE.heli; takeLeave(); carG.visible = false; VEH = 'heli'; document.body.classList.remove('car'); heli.visible = true; S.hp = H.hp; tourOn = H.tour; TAKE.heli = null; WALK.veh = H; walkBoard(); toast('Takaisin kopterissa', 1.8); return; }
  const T = TAKE.tgt; if (!T) return; let x, y, yaw, hex, hp = 100; const ty = takeType(T);
  if (T.l) { ({ x, y, yaw, hex, hp } = T.l); scene.remove(T.l.g); TAKE.left = null; if (VEH === 'car') takeLeave(); }
  else { if (VEH === 'car') takeLeave(); if (T.p) { ({ x, y, yaw, hex } = T.p); T.p.gone = true; T.p.im.setMatrixAt(T.p.j, new THREE.Matrix4().makeScale(0, 0, 0)); T.p.im.instanceMatrix.needsUpdate = true; }
    else if (T.bp) { ({ x, y, yaw, hex } = T.bp); }
    else if (T.b) { ({ x, y, yaw, hex } = T.b); T.b.gone = true; const z0 = new THREE.Matrix4().makeScale(0, 0, 0); for (const im of window.__bikes.ims) { im.setMatrixAt(T.b.i, z0); im.instanceMatrix.needsUpdate = true; } }
    else { x = T.c.wx; y = T.c.wy; yaw = T.c.yaw; hex = T.c.paint || 0x8b9096; cars.vanish(T.c); } }
  if (VEH !== 'car') { const h = WALK.veh || { x: S.x, y: S.y, alt: S.alt, yaw: S.yaw }; TAKE.heli = { x: h.x, y: h.y, alt: h.alt, yaw: h.yaw, hp: S.hp, tour: tourOn };      /* WALK.veh is unset when the game started on foot (story) */ tourOn = false; VEH = 'car'; document.body.classList.add('car'); }
  setCarType(ty);
  carG.visible = true; Object.assign(CAR, { x, y, yaw, v: 0, steer: 0, pitch: 0, roll: 0 }); CAR.z = carGround(x, y) ?? TZs(x, y); S.hp = hp; TAKE.hex = hex; TAKE.tgt = null;
  WALK.veh = { x, y, alt: CAR.z, yaw }; walkBoard(); if (T.bp) { window.__bus.take(T.bp); return; } toast(T.l ? (ty === 'bike' ? 'Takaisin pyörän selässä' : 'Takaisin edellisessä autossa') : (ty === 'bike' ? '🚲 Lainasit pyörän' : ty === 'van' ? '🚐 Lainasit pakettiauton' : ty === 'estate' ? '🚗 Lainasit farmarin' : '🚗 Lainasit auton') + (ty !== 'bike' && Math.random() < 0.4 ? ' – "Hei! Se o mnuu auto!"' : ''), 2.6); }
TAKE.near = takeNear; TAKE.do = takeDo;
// 21.11.2026 (owner: the story starts on Tapsa's bicycle and moves on to Rami's old car): TAKE.give puts the player straight into a vehicle the story hands
// over (tarina/peli.js handler 'anna_ajoneuvo'): type 'bike' | 'hatch' | 'estate' | 'van', at x, y facing yaw (0 = north), paint hex. Works on foot, in a car
// or on a bike (the old one stays behind like a borrowed one); from the helicopter the helicopter waits where it is.
TAKE.give = (x, y, yaw, type, hex) => { if (window.__race && (window.__race.st === 1 || window.__race.st === 2)) return false;
  if (VEH === 'car') takeLeave();
  else { const h = WALK.veh || { x: S.x, y: S.y, alt: S.alt, yaw: S.yaw }; TAKE.heli = { x: h.x, y: h.y, alt: h.alt, yaw: h.yaw, hp: S.hp, tour: tourOn }; tourOn = false; VEH = 'car'; document.body.classList.add('car'); }
  setCarType(type || 'hatch');
  carG.visible = true; Object.assign(CAR, { x, y, yaw: yaw || 0, v: 0, steer: 0, pitch: 0, roll: 0 }); CAR.z = carGround(x, y) ?? TZs(x, y); S.hp = 100; TAKE.hex = hex ?? 0x8b9096; TAKE.applied = null; TAKE.tgt = null;
  WALK.veh = { x, y, alt: CAR.z, yaw: yaw || 0 }; if (!WALK.on) { WALK.on = true; scene.add(walkG); } walkBoard(); return true; };
// 21.11.2026 (owner: "helikopteri voidaan vapauttaa käyttöön myöhemmin, kun pelaaja on edennyt pelissä"): the story keeps window.__heliLukko on until it
// hands the helicopter over (tarina M16, handler 'anna_kopteri'): while locked the parked helicopter is hidden and cannot be boarded.
// TAKE.giveHeli lifts the lock, lands the helicopter at x, y and puts the player in it (the car or bike stays behind like a borrowed one).
TAKE.giveHeli = (x, y, yaw) => { window.__heliLukko = false; TAKE.lukkoPiilotti = false;
  if (VEH === 'car') { takeLeave(); carG.visible = false; VEH = 'heli'; document.body.classList.remove('car'); }
  const alt = roofAt(x, y) + SKID; Object.assign(S, { x, y, alt, yaw: yaw || 0, vx: 0, vy: 0, vz: 0, landed: true, hp: 100, dead: 0 }); heli.visible = true; TAKE.heli = null;
  WALK.veh = { x, y, alt, yaw: yaw || 0 }; if (!WALK.on) { WALK.on = true; scene.add(walkG); } walkBoard(); return true; };
window.__takeTick = dt => {
  if (window.__heliLukko) { if (heli.visible && (WALK.on || VEH === 'car')) { heli.visible = false; TAKE.lukkoPiilotti = true; } }      /* story: helicopter locked and hidden until the story hands it over */
  else if (TAKE.lukkoPiilotti) { TAKE.lukkoPiilotti = false; if (VEH !== 'car' || TAKE.heli) heli.visible = true; } if (TAKE.hex !== TAKE.applied && carG.children.length) { carG.traverse(q => { if (q.isMesh && q.material && /^(Car|Bike)Paint$/.test(q.material.name)) q.material.color.setHex(TAKE.hex); }); TAKE.applied = TAKE.hex; }
  if (TAKE.heli && VEH === 'car' && !S.dead && !heli.visible) heli.visible = true;
  /* riding a bicycle: the walker model sits on it and pedals (clip Cycle, one crank turn a second at 5 m/s), cranks and pedals in step with the clip, the
     handlebar follows the steering, bike and rider lean into the bend */
  const riding = VEH === 'car' && CAR.type === 'bike' && !WALK.on && !S.dead && carG.children.length > 0 && CARM.bike && carG.children[0] === CARM.bike.root;
  if (riding) { loadWalker(); const R = CARM.bike.root; if (!TAKE.bk) TAKE.bk = { st: R.getObjectByName('Steering'), cr: R.getObjectByName('Crank'), pl: R.getObjectByName('Pedal_L'), pr: R.getObjectByName('Pedal_R'), pad: R.getObjectByName('RackPad'), sx: R.getObjectByName('Steering').rotation.x };
    const K = TAKE.bk, yr = CAR.v / WB * Math.tan(CAR.steer), lean = Math.max(-0.35, Math.min(0.35, Math.atan(CAR.v * yr / 9.81))); TAKE.lean = (TAKE.lean || 0) + (lean - (TAKE.lean || 0)) * Math.min(1, dt * 6);
    R.rotation.z = -TAKE.lean; K.st.rotation.y = -CAR.steer * 0.55;      /* 0.9 -> 0.55 (20.11): the hands do not follow the bar (no such clip), a smaller visible turn keeps them near the grips */
    if (walkG.parent !== scene) scene.add(walkG); walkG.rotation.order = 'YXZ'; walkG.position.set(CAR.x, CAR.z, -CAR.y); walkG.rotation.set(0, -CAR.yaw, -TAKE.lean); walkG.visible = camMode !== 1; TAKE.rider = true;
    if (walkMix && walkAct.Cycle) { const a = walkAct.Cycle; if (walkCur !== 'Cycle') { const b = walkAct[walkCur]; a.reset().play(); if (b) a.crossFadeFrom(b, 0.15, false); walkCur = 'Cycle'; }
      a.timeScale = input.f > 0.05 ? Math.max(0.35, Math.min(2.2, Math.abs(CAR.v) / 5)) : 0;
      const LL = walkAct.CycleLeanL, LR = walkAct.CycleLeanR; if (LL && LR) { if (!TAKE.leanOn) { TAKE.leanOn = true; LL.reset().play(); LR.reset().play(); }      /* the rider leans on top of the bike's own tilt: the three clips run in step, only the weights change (TAKE.lean > 0 = right) */
        const w = Math.min(1, Math.abs(TAKE.lean) / 0.3); a.weight = 1 - w; LL.weight = TAKE.lean < 0 ? w : 0; LR.weight = TAKE.lean > 0 ? w : 0; LL.timeScale = LR.timeScale = a.timeScale; LL.time = LR.time = a.time; }
      walkMix.update(dt); const d = a.getClip().duration, ang = 2 * Math.PI * ((a.time % d) / d); K.cr.rotation.x = ang; if (K.pl) K.pl.rotation.x = -ang; if (K.pr) K.pr.rotation.x = -ang; } }
  else if (TAKE.rider) { TAKE.rider = false; walkG.rotation.z = 0; if (!WALK.on) walkG.visible = false; if (CARM.bike) CARM.bike.root.rotation.z = 0;
    if (TAKE.leanOn) { TAKE.leanOn = false; walkAct.CycleLeanL.stop(); walkAct.CycleLeanR.stop(); walkAct.Cycle.weight = 1; } }
  /* passenger on the rack (kyydit, 20.11.2026): the walker copy __ride.pc follows the bike with clip Passenger; its root scale is never touched. Off the bike it
     stays sitting on the bike left behind. The rack pad shows only with a passenger. */
  const pc = window.__ride && window.__ride.pc, own = !riding && VEH === 'car' && CAR.type === 'bike' && !S.dead, src = pc ? (riding ? walkG : own ? carG : TAKE.left && TAKE.left.type === 'bike' ? TAKE.left.g : null) : null;
  if (TAKE.bk && TAKE.bk.pad) TAKE.bk.pad.visible = !!pc;
  if (pc) { pc.g.visible = !!src; if (src) { if (own) { pc.g.position.set(CAR.x, CAR.z, -CAR.y); pc.g.rotation.set(0, -CAR.yaw, 0); } else { pc.g.position.copy(src.position); pc.g.rotation.copy(src.rotation); } const l = riding ? TAKE.lean : 0, w = Math.min(1, Math.abs(l) / 0.3), P = pc.act;
      if (P.PassengerLeanL && P.PassengerLeanR) { P.Passenger.weight = 1 - w; P.PassengerLeanL.weight = l < 0 ? w : 0; P.PassengerLeanR.weight = l > 0 ? w : 0; P.PassengerLeanL.time = P.PassengerLeanR.time = P.Passenger.time; }
      pc.mix.update(dt); } } };

