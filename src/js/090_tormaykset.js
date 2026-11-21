// ---------- solid cars and people (owner 20.11.2026: "bottien läpi ei kuuluisi päästä kävelemään, eikä myöskään autojen") ----------
// Every car is a box (centre, heading, half length, half width), every walker a circle. One list per rendered frame: the traffic and race cars, the
// player's own vehicle, the car or helicopter left behind, the player on foot; the aerial-photo parked cars come from an 8 m grid (window.__parked).
//    The street furniture (window.__furn: benches, terrace tables, chairs and fences) is in the same grid.
//  - on foot the player cannot step into a car or a walker (walkHit); only a move that brings them closer is refused, so nobody gets stuck
//  - driving, the player's car cannot enter a parked car (carHit, called by carBlocked; the moving traffic was already there)
//  - a walker (npcStep) waits for a moving car, walks round a standing one by its corners, walks round the player, and steps aside from the
//    player's moving car and from the race cars (the car is not stopped by people)
//  - the traffic brakes for people on its lane (cars.update asks walkers()), and a party waits at the kerb while a car is coming (coming)
const SOLID = (() => {
  const DIM = [[2.1, 0.95], [2.3, 0.97], [2.1, 0.95], [2.45, 1.1], [2.45, 1.1], [2.45, 1.1], [2.45, 1.1]], PR = 0.3, NR = 0.35, out = [0, 0], ME = { x: 0, y: 0 };   // DIM: cars.js car0..car3 (mirrors left out)
  let dyn = [], wk = [], lastF = -1, pg = null, pn = -1, pA = null, pF = null; const NONE = [];
  // kind: 0 standing, 1 traffic, 2 the player's car when driven or a race car (people step aside), 3 the player on foot
  const mk = (x, y, yaw, hl, hw, v, kind) => ({ x, y, sn: Math.sin(yaw), cs: Math.cos(yaw), hl, hw, v, kind, me: false });
  const frame = () => { const f = renderer.info.render.frame; if (f === lastF) return; lastF = f; dyn = []; wk = [];
    try { const T = window.__sig && window.__sig.cars, foot = WALK.on;
      if (T) for (const c of T) if (c.wx !== undefined && Math.abs(c.wx - S.x) < 190 && Math.abs(c.wy - S.y) < 190) { const d = DIM[c.k || 0]; dyn.push(mk(c.wx, c.wy, c.yaw, d[0], d[1], c.s || 0, 1)); }
      if (window.__race) for (const b of window.__race.bots) if (b.wx !== undefined) dyn.push(mk(b.wx, b.wy, b.yaw, 2.1, 0.9, b.v || 0, 2));
      if (VEH === 'car') { if (carG.visible && !(foot && CAR.lifted)) { const b = mk(CAR.x, CAR.y, CAR.yaw, CAR.hl || 2.1, CAR.hw || 0.9, foot ? 0 : CAR.v, foot ? 0 : 2); b.me = !foot; dyn.push(b); } }
      else if (heli.visible && (foot || S.landed)) { const h = foot && WALK.veh ? WALK.veh : S, b = mk(h.x, h.y, h.yaw, 2.6, 1.0, 0, 0); b.me = !foot; dyn.push(b); }
      if (TAKE.left && !TAKE.left.lifted) { const l = TAKE.left, y = CARTY[l.type] || CARTY.hatch; dyn.push(mk(l.x, l.y, l.yaw, y.hl, y.hw, 0, 0)); }
      if (TAKE.heli && VEH === 'car') dyn.push(mk(TAKE.heli.x, TAKE.heli.y, TAKE.heli.yaw, 2.6, 1.0, 0, 0));
      if (foot && !WALK.in) { ME.x = WALK.x; ME.y = WALK.y; wk.push(ME); dyn.push(mk(WALK.x, WALK.y, 0, 0.12, 0.12, 0, 3)); }
      if (window.__npc) { for (const p of window.__npc.parties) for (const c of p.m) if (c.g.visible) wk.push(c); for (const c of window.__npc.sitters || []) if (c.g.visible) wk.push(c); }
    } catch (e) {} };
  const parked = (x, y, L) => { const P0 = window.__parked || NONE, F = window.__furn || NONE; if (pn !== P0.length + F.length || pA !== P0 || pF !== F) { pg = new Map(); pn = P0.length + F.length; pA = P0; pF = F; for (const p of P0.concat(F)) {      /* parked cars and the street furniture (benches, terraces) */ const k = Math.floor(p.x / 8) * 4096 + Math.floor(p.y / 8); let l = pg.get(k); if (!l) pg.set(k, l = []); if (!p.box) { const d = DIM[p.k] || DIM[0]; p.box = p.hl ? mk(p.x, p.y, p.yaw, p.hl, p.hw, 0, 0) : mk(p.x, p.y, p.yaw, d[0] * 0.97, d[1] * 0.97, 0, 0); } l.push(p); } }
    const cx = Math.floor(x / 8), cy = Math.floor(y / 8); for (let i = -1; i <= 1; i++) for (let j = -1; j <= 1; j++) { const l = pg.get((cx + i) * 4096 + cy + j); if (l) for (const p of l) if (!p.gone) L.push(p.box); } };
  const near = (x, y, r) => { frame(); const L = []; for (const b of dyn) if (Math.abs(b.x - x) < r + b.hl && Math.abs(b.y - y) < r + b.hl) L.push(b); parked(x, y, L); return L; };
  const sd = (b, x, y) => { const dx = x - b.x, dy = y - b.y, qx = Math.abs(dx * b.sn + dy * b.cs) - b.hl, qy = Math.abs(dx * b.cs - dy * b.sn) - b.hw; return Math.hypot(Math.max(qx, 0), Math.max(qy, 0)) + Math.min(Math.max(qx, qy), 0); };
  const segBox = (b, x0, y0, x1, y1, e) => { const ax = x0 - b.x, ay = y0 - b.y, bx = x1 - b.x, by = y1 - b.y, p = [ax * b.sn + ay * b.cs, ax * b.cs - ay * b.sn], q = [bx * b.sn + by * b.cs, bx * b.cs - by * b.sn], h = [b.hl + e, b.hw + e]; let t0 = 0, t1 = 1;   // segment against the box grown by e (slabs, in the box's own frame)
    for (let i = 0; i < 2; i++) { const d = q[i] - p[i]; if (Math.abs(d) < 1e-9) { if (Math.abs(p[i]) > h[i]) return false; } else { let u = (-h[i] - p[i]) / d, w = (h[i] - p[i]) / d; if (u > w) { const s = u; u = w; w = s; } if (u > t0) t0 = u; if (w < t1) t1 = w; if (t0 > t1) return false; } } return true; };
  const side = (b, x, y, r) => { const dx = x - b.x, dy = y - b.y; let lx = dx * b.sn + dy * b.cs, ly = dx * b.cs - dy * b.sn;       // the nearest point r outside the box, through a side rather than an end when it is a toss-up
    if (b.hw - Math.abs(ly) <= b.hl - Math.abs(lx) + 0.4) ly = (ly < 0 ? -1 : 1) * (b.hw + r); else lx = (lx < 0 ? -1 : 1) * (b.hl + r); out[0] = b.x + b.sn * lx + b.cs * ly; out[1] = b.y + b.cs * lx - b.sn * ly; return out; };
  const sat = (a, b) => { const dx = b.x - a.x, dy = b.y - a.y; for (const [ux, uy] of [[a.sn, a.cs], [a.cs, -a.sn], [b.sn, b.cs], [b.cs, -b.sn]]) {
      const ra = a.hl * Math.abs(a.sn * ux + a.cs * uy) + a.hw * Math.abs(a.cs * ux - a.sn * uy), rb = b.hl * Math.abs(b.sn * ux + b.cs * uy) + b.hw * Math.abs(b.cs * ux - b.sn * uy); if (Math.abs(dx * ux + dy * uy) > ra + rb) return false; } return true; };
  const toward = (c, gx, gy, st) => { const dx = gx - c.x, dy = gy - c.y, d = Math.hypot(dx, dy); if (d < 1e-6) { out[0] = out[1] = 0; return out; } const k = Math.min(d, st) / d; out[0] = dx * k; out[1] = dy * k; return out; };
  return { DIM, near, sd,
    walkers: () => { frame(); return wk; },
    // the player on foot: would the step from (ox, oy) to (nx, ny) walk into a car or a person
    walkHit: (ox, oy, nx, ny) => { for (const b of near(nx, ny, 1)) { if (b.kind === 3) continue; const d = sd(b, nx, ny); if (d < PR && d < sd(b, ox, oy) - 1e-6) return true; }
      for (const c of wk) { if (c === ME) continue; const dx = c.x - nx, dy = c.y - ny, d2 = dx * dx + dy * dy; if (d2 < 0.3 && d2 < (c.x - ox) ** 2 + (c.y - oy) ** 2 - 1e-6) return true; } return false; },
    // a car has driven onto the player on foot: the free spot beside it, or null
    pushOut: (x, y) => { for (const b of near(x, y, 1)) if (b.kind !== 3 && sd(b, x, y) < PR - 0.08) return side(b, x, y, PR); return null; },
    // the player's car at (x, y), heading (sn, cs): inside a parked car, the car left behind or the parked helicopter (only when moving closer to it)
    carHit: (x, y, sn, cs) => { const a = { x, y, sn, cs, hl: (CAR.hl || 2.1) - 0.1, hw: (CAR.hw || 0.9) - 0.05 };
      for (const b of near(x, y, 4)) { if (b.kind !== 0 || b.me) continue; if (sat(a, b) && (b.x - x) ** 2 + (b.y - y) ** 2 < (b.x - S.x) ** 2 + (b.y - S.y) ** 2 - 1e-4) return true; } return false; },
    // is a car about to drive over the crossing that starts at (ax, ay) towards (bx, by): within 3 s at its present speed
    coming: (ax, ay, bx, by) => { frame(); const ex = (bx - ax) * 2, ey = (by - ay) * 2, el = ex * ex + ey * ey || 1;
      for (const b of dyn) { if (b.kind === 0 || b.kind === 3 || Math.abs(b.v) < 2 || Math.abs(b.x - ax) > 70 || Math.abs(b.y - ay) > 70) continue;
        for (let t = 0.25; t <= 3; t += 0.25) { const px = b.x + b.sn * b.v * t - ax, py = b.y + b.cs * b.v * t - ay, u = Math.max(0, Math.min(1, (px * ex + py * ey) / el)); if (Math.hypot(px - ex * u, py - ey * u) < 2.2) return true; } } return false; },
    // one walker's step: (mx, my) is the step it would take towards its place (tx, ty) in the party, v the party's speed. Returns the step it may take.
    npcStep: (c, mx, my, tx, ty, v, dt) => { out[0] = mx; out[1] = my; const L = near(c.x, c.y, 26); if (!L.length) return out;
      for (const b of L) { if (b.kind !== 2 || Math.abs(b.v) < 0.5) continue;                 // the player's car or a race car is coming: step aside, out of its way
        const dir = b.v > 0 ? 1 : -1, zone = (x, y) => { const dx = x - b.x, dy = y - b.y, ah = (dx * b.sn + dy * b.cs) * dir; return ah > -b.hl && ah < b.hl + 1.5 + Math.abs(b.v) * 0.9 && Math.abs(dx * b.cs - dy * b.sn) < b.hw + 0.75; };
        if (zone(c.x, c.y)) { const dx = c.x - b.x, dy = c.y - b.y, lx = dx * b.sn + dy * b.cs, ly = dx * b.cs - dy * b.sn; let s = ly > 0.05 ? 1 : ly < -0.05 ? -1 : (c.sdv || (c.sdv = Math.random() < 0.5 ? 1 : -1)), gx = 0, gy = 0;
          for (let k = 0; k < 2; k++) { const gl = s * (b.hw + 1.05); gx = b.x + b.sn * lx + b.cs * gl; gy = b.y + b.cs * lx - b.sn * gl; if (walkFree(gx, gy) || Math.abs(ly) > 0.4) break; s = -s; }
          return toward(c, gx, gy, 4.5 * dt); }
        if (zone(c.x + mx, c.y + my)) { out[0] = out[1] = 0; return out; } }                     // beside its path: stand there until it has passed
      const m = Math.hypot(mx, my), vm = Math.max(2.2, v * 1.9) * dt; if (m > vm) { mx *= vm / m; my *= vm / m; out[0] = mx; out[1] = my; }      // catching up after waiting: a brisk walk, not a dash
      let hit = null, hd = 1e9; for (const b of L) if (segBox(b, c.x, c.y, tx, ty, NR)) { const d = sd(b, c.x, c.y); if (d < hd) { hd = d; hit = b; } }
      if (hit) { const b = hit;
        if (hd < NR - 0.08) { const g = side(b, c.x, c.y, NR + 0.05); return toward(c, g[0], g[1], 3 * dt); }       // a car has come onto the walker: out of it sideways
        if (Math.abs(b.v) > 0.5) { out[0] = out[1] = 0; return out; }                           // a moving car in the way: wait
        const e = NR + 0.25, C = [], ti = sd(b, tx, ty) < NR; let best = -1, bc = 1e9;          // a standing car (or the player): round it by the corners of the box grown by e
        for (let i = 0; i < 4; i++) { const lx = (i & 1 ? 1 : -1) * (b.hl + e), ly = (i & 2 ? 1 : -1) * (b.hw + e); C.push([b.x + b.sn * lx + b.cs * ly, b.y + b.cs * lx - b.sn * ly]); }
        const D = (p, x, y) => Math.hypot(p[0] - x, p[1] - y), cut = (p, x, y) => segBox(b, p[0], p[1], x, y, NR - 0.05);
        for (let i = 0; i < 4; i++) { const p = C[i], d = D(p, c.x, c.y); if (cut(p, c.x, c.y)) continue; let cost;
          if (ti) cost = D(p, tx, ty);                                                            // its place is inside the box (a car stands on the path): the corner nearest to it, and wait there
          else { if (d < 0.12) continue; if (!cut(p, tx, ty)) cost = d + D(p, tx, ty); else { cost = 1e9; for (const j of [i ^ 1, i ^ 2]) { const q = C[j], cj = d + D(p, q[0], q[1]) + D(q, tx, ty) + (cut(q, tx, ty) ? 50 : 0); if (cj < cost) cost = cj; } } }
          if (cost < bc) { bc = cost; best = i; } }
        if (best < 0) { out[0] = out[1] = 0; return out; }
        toward(c, C[best][0], C[best][1], Math.max(v, 1.2) * 1.15 * dt); mx = out[0]; my = out[1]; }
      for (const b of L) { const d = sd(b, c.x + mx, c.y + my); if (d < NR - 0.05 && d < sd(b, c.x, c.y) - 1e-6) { out[0] = out[1] = 0; return out; } }     // never into a box
      out[0] = mx; out[1] = my; return out; } };
})();
function carBlocked(x, y, yaw) {   // a corner of the car inside a house or over open water
  const sn = Math.sin(yaw), cs = Math.cos(yaw), g = TZs(x, y);
  // a traffic car in the way (19.11.2026): three circles along each car; only a move that brings the two closer is refused, so the player can always back away
  if (window.__sig && window.__sig.cars && VEH === 'car') { const C = window.__race && window.__race.bots.length ? window.__sig.cars.concat(window.__race.bots) : window.__sig.cars; for (let i = 0; i < C.length; i++) { const o = C[i]; if (o.wx === undefined) continue; const dx = o.wx - x, dy = o.wy - y, d2 = dx * dx + dy * dy; if (d2 > 30) continue;
      const os = Math.sin(o.yaw), oc = Math.cos(o.yaw); let hit = false; for (const f of [1.4, 0, -1.4]) for (const h of [1.4, 0, -1.4]) { const ex = (x + sn * f) - (o.wx + os * h), ey = (y + cs * f) - (o.wy + oc * h); if (ex * ex + ey * ey < 3.06) hit = true; }
      if (hit && d2 < (o.wx - S.x) ** 2 + (o.wy - S.y) ** 2 - 1e-4) return true; } }
  if (VEH === 'car' && !WALK.on && SOLID.carHit(x, y, sn, cs)) return true;      // a parked car, the car left behind (20.11.2026)
  if (x > HALL.bb[0] - 3 && x < HALL.bb[2] + 3 && y > HALL.bb[1] - 3 && y < HALL.bb[3] + 3) for (let f = -2.1; f < 2.11; f += 0.3) for (const r of [0.9, -0.9]) {   // near the hall: both sides sampled every 0.3 m, so its 0.4 m walls cannot slip between the corner points
    const px = x + sn * f + cs * r, py = y + cs * f - sn * r; if (!inHall(px, py) && bldTopAt(px, py) > Math.max(g, TZg(px, py)) + 1.4) return true; }
  const HL = CAR.hl || 2.1, HW = CAR.hw || 0.9;      // the box of the model being driven (van and estate are longer)
  for (const [f, r] of [[HL, HW], [HL, -HW], [-HL, HW], [-HL, -HW], [0, HW + 0.05], [0, -HW - 0.05]]) {
    const px = x + sn * f + cs * r, py = y + cs * f - sn * r;
    if (carGround(px, py) === null) return true;
    if (inHall(px, py)) { if (HALL.pil.some(q => Math.abs(px - q[0]) < 0.3 && Math.abs(py - q[1]) < 0.3)) return true; continue; }   // inside the parking hall: only its pillars stop the car
    if (onPorinsilta(px, py) === null && bldTopAt(px, py) > Math.max(g, TZg(px, py)) + 1.4) return true;
  }
  return false;
}
// the house standing exactly at (x, y), its roof height (with the ground lift), else -1e9. roofAt() samples a 3 m ring for the
// helicopter's skids, which made the car stop short of walls and at corners where nothing was (owner 18.11: invisible obstacles)
function bldTopAt(x, y) {
  const l = grid.get(gkey(Math.floor(x / GRID) + 100, Math.floor(y / GRID) + 100)); if (!l) return -1e9; const tb = TZs(x, y); let h = -1e9;
  for (const bi of l) { const b = blds[bi]; if (x < b.minx || x > b.maxx || y < b.miny || y > b.maxy || !pip(x, y, b.pts)) continue;
    const z = b.tris ? triZ(b.tris, x, y) : b.h; if (z !== null && z + tb > h) h = z + tb; }
  return h;
}
function resetCar() {
  Object.assign(CAR, { x: HOME.x - 6, y: HOME.y - 10, yaw: Math.PI * 0.5 - 0.23, v: 0, steer: 0, spin: 0 }); CAR.z = carGround(CAR.x, CAR.y) || 0;
  S.hp = 100; S.dead = 0; carG.visible = VEH === 'car';
}
function stepCar(dt, live) {
  const f = live ? input.f : 0, t = live ? input.t : 0, hb = live && keys.has('Space');
  // throttle / brake / reverse
  const fw = Math.cos(CAR.steer);
  if (f > 0) CAR.v += (CAR.v < -0.3 ? 9 : (CAR.acc || 4.2) * (1 - Math.max(0, CAR.v) / (CAR.top || 24))) * f * dt;
  else if (f < 0) CAR.v += (CAR.v > 0.3 ? 9 : 2.6 * (1 + CAR.v / 6)) * f * dt;
  CAR.v *= Math.exp(-(f === 0 ? 0.22 : 0.05) * dt); if (f === 0 && Math.abs(CAR.v) < 0.25) CAR.v = 0;
  if (hb) { CAR.v *= Math.exp(-2.2 * dt); if (Math.abs(CAR.v) < 0.4) CAR.v = 0; }
  // steering: less lock at speed
  const lock = 0.58 / (1 + Math.abs(CAR.v) / 11);
  CAR.steer += (t * lock - CAR.steer) * Math.min(1, dt * 6);
  { const ds = S.hp < 30 ? 3 : S.hp < 45 ? 2 : S.hp < 60 ? 1 : 0; if (CAR.setDmg && CAR.dmg !== ds) CAR.setDmg(ds);                 // the body shows the damage step
    const lim = S.hp < 30 ? 14 : S.hp < 60 ? 22 : 1e9; if (CAR.v > lim) CAR.v += (lim - CAR.v) * Math.min(1, dt * 2);          // a damaged car is slower
    smokeStep(dt, S.hp < 60 && !S.dead && CAR.type !== 'bike' ? (S.hp < 30 ? 0.05 : S.hp < 45 ? 0.09 : 0.16) : 0, S.hp < 30, CAR.x + Math.sin(CAR.yaw) * 1.5, CAR.y + Math.cos(CAR.yaw) * 1.5, CAR.z + 0.95); }
  const yr = CAR.v / (CAR.wb || WB) * Math.tan(CAR.steer + (S.hp < 45 ? 0.03 : 0)) * (hb ? 1.25 : 1);
  const nyaw = CAR.yaw + yr * dt, sn = Math.sin(nyaw), cs = Math.cos(nyaw);
  const nx = CAR.x + sn * CAR.v * dt * fw, ny = CAR.y + cs * CAR.v * dt * fw;
  if (carBlocked(nx, ny, nyaw)) {
    // 19.11.2026 (owner): a knock dents the car instead of wrecking it: from 4 m/s up, 2.2 points per m/s (50 km/h = 22 of the 100). Under 60 the car is
    // slower and smokes, under 45 it pulls to the right, under 30 it limps (50 km/h) under black smoke; only 0 ends the drive.
    if (Math.abs(CAR.v) > 4) { const h0 = S.hp; damage((Math.abs(CAR.v) - 4) * 2.2); if (S.hp > 0) toast(S.hp < 30 && h0 >= 30 ? 'Auto on pahasti romuna – se kulkee enää hiljaa' : S.hp < 60 && h0 >= 60 ? 'Kolari! Moottori savuaa' : 'Kolhu! Kunto ' + Math.max(0, Math.round(S.hp)) + ' %', 1.6); }
    CAR.v *= -0.25;
  } else { CAR.x = nx; CAR.y = ny; CAR.yaw = nyaw; }
  if (!tourOn && !tourDone && Math.abs(CAR.v) > 0.5) tourOn = true;
  CAR.owT = (CAR.owT || 0) - dt;
  if (CAR.v > 3 && CAR.owT <= 0 && NAV.seg) { CAR.owT = 0.5; const g = NAV.seg(CAR.x, CAR.y);
    if (g && g.d < 5) { const dir = ONEWAY.get(g.ri + ',' + g.si); if (dir) { const hx = (g.b.x - g.a.x) * (g.fwd ? 1 : -1) * dir, hy = (g.b.y - g.a.y) * (g.fwd ? 1 : -1) * dir;
      if (hx * Math.sin(CAR.yaw) + hy * Math.cos(CAR.yaw) < 0) { toast('⚠ Yksisuuntainen katu – ajat väärään suuntaan', 1.6); CAR.owT = 3; } } } }
  // body on the ground: height (kerbs lift it smoothly), pitch and roll from the four wheel contacts
  const s0 = Math.sin(CAR.yaw), c0 = Math.cos(CAR.yaw), gz = (fx, rx) => { const z = carGround(CAR.x + s0 * fx + c0 * rx, CAR.y + c0 * fx - s0 * rx); return z === null ? CAR.z : z; };
  const zf = (gz(1.32, 0.77) + gz(1.32, -0.77)) / 2, zr = (gz(-1.32, 0.77) + gz(-1.32, -0.77)) / 2, zl = (gz(1.32, 0.77) + gz(-1.32, 0.77)) / 2, zrr = (gz(1.32, -0.77) + gz(-1.32, -0.77)) / 2;
  CAR.z += ((zf + zr) / 2 - CAR.z) * Math.min(1, dt * 14);
  const tp = Math.atan2(zf - zr, CAR.wb || WB) + (live ? -f * 0.012 : 0), tr = Math.atan2(zl - zrr, 1.55) + yr * CAR.v * 0.0016;
  CAR.pitch += (tp - CAR.pitch) * Math.min(1, dt * 8); CAR.roll += (tr - CAR.roll) * Math.min(1, dt * 8);
  carG.position.set(CAR.x, CAR.z, -CAR.y); carG.rotation.set(CAR.pitch, -CAR.yaw, -CAR.roll);
  CAR.spin += CAR.v / (CAR.r || CAR_R) * dt;
  for (const w of wheels) { w.rotation.x = CAR.spin; w.rotation.y = w.userData.front ? CAR.steer : 0; }
  // keep the shared state in step: camera, HUD, tour, minimap read S
  S.x = CAR.x; S.y = CAR.y; S.alt = CAR.z; S.yaw = CAR.yaw; S.vx = Math.sin(CAR.yaw) * CAR.v; S.vy = Math.cos(CAR.yaw) * CAR.v; S.vz = 0; S.landed = Math.abs(CAR.v) < 0.5;
}

