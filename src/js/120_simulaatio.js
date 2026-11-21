// ---------- simulation ----------
const DIRS = ['P', 'KO', 'I', 'KA', 'E', 'LO', 'L', 'LU'];
function step(dt) {
  readInput();
  if (window.__jump && window.__jump.on) { if (sGain) sGain.gain.value = 0; window.__jump.step(dt); return; }      // parachute jump (laskuvarjo/hyppy.js, 21.11.2026)
  if (window.__plane && window.__plane.on) { if (sGain) sGain.gain.value = 0; window.__plane.step(dt); return; }      // jump plane (lento/lento.js, 20.11.2026)
  if (S.dead > 0) { S.dead -= dt; if (S.dead <= 0) (VEH === 'car' ? resetCar : resetHeli)(); return; }
  if (WALK.on) { stepWalk(dt); return; }
  const live = started;
  if (VEH === 'car') {
    stepCar(dt, live);
    if (performance.now() - HR.last > 500) { HR.last = performance.now(); hrUpdate(S.x, S.y); TEXLOD.update(S.x, S.y); streamUpdate(S.x, S.y); TREES.update(S.x, S.y); GRASS.update(); }
    GRASS.tick(performance.now() / 1000);
    blob.position.set(CAR.x, CAR.z + 0.04, -CAR.y); blob.scale.set(0.42, 1, 0.62); blob.rotation.y = -CAR.yaw; blob.material.opacity = 0.9;
    tourTick(dt); if (started && !tourDone) NAV.update(dt, target());
    if (actx && sGain) { const sp = Math.abs(CAR.v), tgt = soundOn && started ? (0.035 + Math.min(0.06, sp / 300) + Math.abs(input.f) * 0.02) * (CAR.type === 'bike' ? 0.08 : 1) : 0; sGain.gain.value += (tgt - sGain.gain.value) * Math.min(1, dt * 4);
      sFilt.frequency.value = 140 + sp * 14 + Math.abs(input.f) * 90; sLfo.frequency.value = 22 + (sp % 9) * 5 + sp * 1.5; }
    return;
  }
  const f = live ? input.f : 0, t = live ? input.t : 0, s = live ? input.s : 0, l = live ? input.l : 0;
  S.rotorSpd += ((live ? 1 : 0.25) - S.rotorSpd) * Math.min(1, dt * 3);
  // yaw
  S.yawRate += (t * 1.55 - S.yawRate) * Math.min(1, dt * 5);
  if (!S.landed) S.yaw += S.yawRate * dt;
  const sn = Math.sin(S.yaw), cs = Math.cos(S.yaw);
  // horizontal: forward = (sn, cs) in map coords, right = (cs, -sn)
  if (!S.landed) {
    const A = 30, AS = 16;
    S.vx += (sn * f * A + cs * s * AS) * dt; S.vy += (cs * f * A - sn * s * AS) * dt;
  }
  const drag = Math.exp(-0.55 * dt); S.vx *= drag; S.vy *= drag;
  // vertical
  S.vz += (l * 20 - S.vz * 1.7) * dt;
  if (S.landed) { S.vx = S.vy = 0; if (l > 0.1 && S.rotorSpd > 0.6) { S.landed = false; if (!tourOn && !tourDone) { tourOn = true; } } else S.vz = 0; }
  const px = S.x, py = S.y;
  let nx = S.x + S.vx * dt, ny = S.y + S.vy * dt, na = S.alt + S.vz * dt;
  // world edge
  if (nx > OX1 + 150 || nx < OX0 - 150) { nx = Math.max(OX0 - 150, Math.min(OX1 + 150, nx)); S.vx *= -0.3; toast('Kartan reuna – käänny takaisin', 1.5); }
  if (ny > OY1 + 150 || ny < OY0 - 150) { ny = Math.max(OY0 - 150, Math.min(OY1 + 150, ny)); S.vy *= -0.3; toast('Kartan reuna – käänny takaisin', 1.5); }
  // buildings
  const rh = roofAt(nx, ny), floor = rh + SKID;
  if (na < floor) {
    const prevFloor = roofAt(px, py) + SKID;
    if (S.alt >= floor - 0.6 || prevFloor >= floor - 0.01) {
      // coming down onto a roof / the ground
      if (S.vz < -7.5) { damage((-S.vz - 7.5) * 9); toast('Kova lasku!', 1.2); }
      na = floor; if (S.vz < 0) S.vz = 0;
      if (l <= 0 && !S.landed && Math.hypot(S.vx, S.vy) < 7) { S.landed = true; S.vx = S.vy = 0; }
    } else {
      // flew into a wall
      const sp = Math.hypot(S.vx, S.vy);
      nx = px; ny = py; S.vx *= -0.45; S.vy *= -0.45;
      if (sp > 4) { damage(sp * 1.1); toast('Törmäys!', 1); }
      const pf = roofAt(nx, ny) + SKID; if (na < pf) na = pf;
    }
  } else if (S.landed && na > floor + 0.05) S.landed = false;
  S.x = nx; S.y = ny; S.alt = na;
  if (S.landed && S.hp < 100) S.hp = Math.min(100, S.hp + dt * 12);

  // visual attitude
  const spF = S.vx * sn + S.vy * cs, spR = S.vx * cs - S.vy * sn;
  const tp = S.landed ? 0 : -(f * 0.2 + spF * 0.0035), tr = S.landed ? 0 : -(S.yawRate * 0.14 * Math.min(1, Math.abs(spF) / 25 + 0.25) + s * 0.18 + spR * 0.004);
  S.pitch += (tp - S.pitch) * Math.min(1, dt * 4); S.roll += (tr - S.roll) * Math.min(1, dt * 4);
  heli.position.set(S.x, S.alt, -S.y); heli.rotation.set(S.pitch, -S.yaw, S.roll);
  if (performance.now() - HR.last > 500) { HR.last = performance.now(); hrUpdate(S.x, S.y); TEXLOD.update(S.x, S.y); streamUpdate(S.x, S.y); TREES.update(S.x, S.y); GRASS.update(); }
  GRASS.tick(performance.now() / 1000);
  rotor.rotation.y -= S.rotorSpd * 38 * dt; tailRotor.rotation.x += S.rotorSpd * 55 * dt;
  blob.position.set(S.x, roofAt(S.x, S.y) + 0.3, -S.y); const bs = Math.max(0.35, 1 - (S.alt - SKID) / 160); blob.scale.setScalar(bs); blob.material.opacity = bs;

  tourTick(dt);
  if (actx && sGain) { const tgt = soundOn && started ? 0.05 + 0.07 * S.rotorSpd + Math.min(0.05, Math.hypot(S.vx, S.vy) / 900) : 0; sGain.gain.value += (tgt - sGain.gain.value) * Math.min(1, dt * 4); sFilt.frequency.value = 220 + 260 * S.rotorSpd + Math.abs(l) * 120; sLfo.frequency.value = 4 + 9 * S.rotorSpd; }
}

function tourTick(dt) {
  if (tourOn && !tourDone) {
    tourT += dt; const tg = target(), d = Math.hypot(tg.x - S.x, tg.y - S.y);
    if (tg.land) {
      if (VEH === 'car' ? d < 40 && Math.abs(CAR.v) < 1.5 : d < 45 && S.landed && S.alt < roofAt(S.x, S.y) + SKID + 0.5) {
        tourDone = true; tourOn = false; const rec = !best || tourT < best; if (rec) { best = tourT; try { localStorage.setItem(BESTKEY, String(best)); } catch (e) {} } LB.submit(tourT); LB.show(true);
        toast(`Kierros valmis ajassa ${fmtT(tourT)}${rec ? ' – uusi ennätys!' : ''}  ·  N = uusi kierros`, 7); setTarget(); $('prog').firstElementChild.style.width = '100%';
      }
    } else if (d < (VEH === 'car' ? 45 : 30)) { tourIdx++; toast('✓ ' + tg.n, 1.6); setTarget(); }
  }
}


