// Törmäyssääntöjen (index.html: SOLID) koe ilman peliä: node tools/solid_test.js [index.html]
// Leikkaa SOLID-lohkon index.html:stä, antaa sille tynkämaailman ja ajaa kävelijän, pelaajan ja auton tilanteet läpi.
const fs = require('fs');
const G = { renderer: { info: { render: { frame: 0 } } }, window: {}, S: { x: 0, y: 0, landed: true }, WALK: { on: false, in: false, x: 0, y: 0, veh: null }, VEH: 'car',
  CAR: { x: 1000, y: 1000, yaw: 0, v: 0, hl: 2.1, hw: 0.9 }, carG: { visible: true }, heli: { visible: false }, TAKE: { left: null, heli: null },
  CARTY: { hatch: { hl: 2.1, hw: 0.9 } }, walkFree: () => true };
const html = fs.readFileSync(process.argv[2] || require('path').join(__dirname, '..', 'index.html'), 'utf8'), i0 = html.indexOf('const SOLID = '), i1 = html.indexOf('function carBlocked(x, y, yaw) {');
const SOLID = new Function(...Object.keys(G), html.slice(i0, i1) + '\nreturn SOLID;')(...Object.values(G));
const { window, WALK, CAR, S, renderer } = G; let fails = 0; const ok = (c, m) => { console.log((c ? 'ok   ' : 'FAIL ') + m); if (!c) fails++; };
const tick = () => renderer.info.render.frame++;
const npc = (x, y) => ({ x, y, g: { visible: true }, off: 0 });
// the game's own follow rule with npcStep in between; the party's place runs from A to B at speed v
function run(c, A, B, v, T, each) { const dt = 1 / 60, L = Math.hypot(B[0] - A[0], B[1] - A[1]); let t = 0, minSd = 1e9, maxSp = 0;
  for (let i = 0; i < T * 60; i++) { tick(); t = Math.min(1, t + v * dt / L); const tx = A[0] + (B[0] - A[0]) * t, ty = A[1] + (B[1] - A[1]) * t, k = Math.min(1, dt * 4);
    if (each) each(i * dt, dt); const q = SOLID.npcStep(c, (tx - c.x) * k, (ty - c.y) * k, tx, ty, v, dt); c.x += q[0]; c.y += q[1]; maxSp = Math.max(maxSp, Math.hypot(q[0], q[1]) / dt);
    for (const b of SOLID.near(c.x, c.y, 6)) minSd = Math.min(minSd, SOLID.sd(b, c.x, c.y)); }
  return { minSd, maxSp, end: Math.hypot(c.x - B[0], c.y - B[1]) }; }
window.__npc = { parties: [] };
// 1. a parked car lies across the walker's path (path along y, car at the origin heading east)
window.__parked = [{ x: 0, y: 0, yaw: Math.PI / 2, k: 0, gone: false }];
{ const c = npc(0.2, -10); window.__npc.parties = [{ m: [c] }]; const r = run(c, [0.2, -10], [0.2, 10], 1.3, 30); ok(r.minSd > 0.28 && r.end < 0.5, `round a parked car lying across the path: min gap ${r.minSd.toFixed(2)} m, ends ${r.end.toFixed(2)} m from goal, top speed ${r.maxSp.toFixed(1)}`); }
// 2. the path runs lengthwise through the parked car
{ window.__parked = [{ x: 0, y: 0, yaw: 0, k: 3, gone: false }]; const c = npc(0, -10); window.__npc.parties = [{ m: [c] }]; const r = run(c, [0, -10], [0, 10], 1.3, 30); ok(r.minSd > 0.28 && r.end < 0.5, `round a parked van standing along the path: min gap ${r.minSd.toFixed(2)}, end ${r.end.toFixed(2)}`); }
// 3. a traffic car drives across the walker's path: the walker waits
{ window.__parked = []; const car = { wx: -14, wy: 0, yaw: Math.PI / 2, k: 0, s: 8 }; window.__sig = { cars: [car] }; const c = npc(0, -3); window.__npc.parties = [{ m: [c] }];
  const r = run(c, [0, -3], [0, 8], 1.3, 14, (t, dt) => { car.wx += car.s * dt; }); ok(r.minSd > 0.28 && r.end < 0.5, `waits for a traffic car crossing its path: min gap ${r.minSd.toFixed(2)}, end ${r.end.toFixed(2)}`); }
// 4. a queue of standing traffic cars across the path: round the nearest one
{ window.__sig = { cars: [{ wx: 0, wy: 0, yaw: Math.PI / 2, k: 0, s: 0 }, { wx: -6.5, wy: 0, yaw: Math.PI / 2, k: 1, s: 0 }, { wx: 6.5, wy: 0, yaw: Math.PI / 2, k: 0, s: 0 }] }; const c = npc(0.5, -6); window.__npc.parties = [{ m: [c] }];
  const r = run(c, [0.5, -6], [0.5, 8], 1.3, 30); ok(r.minSd > 0.28 && r.end < 0.5, `through a standing queue between the cars: min gap ${r.minSd.toFixed(2)}, end ${r.end.toFixed(2)}`); }
// 5. the player's car drives along the walker's line from behind at 12 m/s, then head on, then at 3 m/s
for (const [v, from, lbl] of [[12, -40, 'from behind 12 m/s'], [12, 60, 'head on 12 m/s'], [3, -20, 'from behind 3 m/s'], [22, -80, 'from behind 22 m/s']]) { window.__sig = { cars: [] }; G.VEH = 'car'; WALK.on = false; CAR.x = 0; CAR.y = from; CAR.yaw = from < 0 ? 0 : Math.PI; CAR.v = v;
  const c = npc(0, 0); window.__npc.parties = [{ m: [c] }]; const r = run(c, [0, 0], [0, 30], 1.3, 24, (t, dt) => { CAR.y += (from < 0 ? 1 : -1) * v * dt; });
  ok(r.minSd > 0.25 && r.end < 0.6, `steps aside from the player's car (${lbl}): min gap ${r.minSd.toFixed(2)}, back on its way (${r.end.toFixed(2)} m from goal), top speed ${r.maxSp.toFixed(1)}`); }
// 6. the player's car reverses into a standing walker
{ CAR.x = 0; CAR.y = 6; CAR.yaw = 0; CAR.v = -2.5; const c = npc(0.1, 0); const r = run(c, [0.1, 0], [0.1, 0.01], 1.3, 5, (t, dt) => { CAR.y += CAR.v * dt; }); ok(r.minSd > 0.25, `steps aside from the reversing car: min gap ${r.minSd.toFixed(2)}`); }
// 7. the player stands on the walker's path
{ CAR.x = 1000; CAR.v = 0; WALK.on = true; WALK.x = 0; WALK.y = 0; const c = npc(0, -6); window.__npc.parties = [{ m: [c] }]; let md = 1e9; const r = run(c, [0, -6], [0, 6], 1.3, 14, () => { md = Math.min(md, Math.hypot(c.x - WALK.x, c.y - WALK.y)); });
  ok(md > 0.45 && r.end < 0.5, `walks round the standing player: nearest ${md.toFixed(2)} m, end ${r.end.toFixed(2)}`); }
// 8. the player on foot against a walker, a parked car and his own car
{ tick(); const c = npc(0, 2); window.__npc.parties = [{ m: [c] }]; window.__parked = [{ x: 10, y: 0, yaw: 0, k: 0, gone: false }]; CAR.x = -10; CAR.y = 0; CAR.yaw = 0; tick();
  ok(SOLID.walkHit(0, 1.5, 0, 1.52) && !SOLID.walkHit(0, 1.52, 0, 1.4) && !SOLID.walkHit(0, 0, 0, 0.5), 'player cannot walk into a walker, can back away');
  ok(SOLID.walkHit(8.7, 0, 8.8, 0) && !SOLID.walkHit(8.8, 0, 8.6, 0) && !SOLID.walkHit(8.0, 0, 8.2, 0), 'player cannot walk into a parked car (side), can back away');
  ok(SOLID.walkHit(10, -2.5, 10, -2.3) && !SOLID.walkHit(10, -3, 10, -2.6), 'player cannot walk into a parked car (end)');
  ok(SOLID.walkHit(-8.7, 0, -8.8, 0), 'player cannot walk into his own parked car');
  const q = SOLID.pushOut(10.2, 0.5); ok(q && Math.abs(q[0] - (10 + 0.95 * 0.97 + 0.3)) < 0.02, 'player inside a car is put beside it'); ok(SOLID.pushOut(8.5, 0) === null, 'no push when outside'); }
// 9. the player's car against parked cars
{ WALK.on = false; CAR.x = 0; CAR.y = 0; CAR.yaw = 0; CAR.v = 5; S.x = 0; S.y = 0; window.__parked = [{ x: 0, y: 6, yaw: Math.PI / 2, k: 0, gone: false }, { x: 2.3, y: 0, yaw: 0, k: 0, gone: false }, { x: 40, y: 40, yaw: 0, k: 0, gone: true }]; tick();
  ok(!SOLID.carHit(0, 2.0, 0, 1), 'car: free 1 m before the parked car'); ok(SOLID.carHit(0, 3.2, 0, 1), 'car: stopped at the parked car ahead');
  S.y = 3.2; ok(!SOLID.carHit(0, 3.0, 0, 1), 'car: can back away when touching'); S.y = 0;
  ok(!SOLID.carHit(0, 0.5, 0, 1), 'car: passes a car parked 2.3 m beside (0.5 m gap)'); ok(SOLID.carHit(0.6, 0.1, 0, 1), 'car: cannot push sideways into it');
  S.x = 40; S.y = 36; ok(!SOLID.carHit(40, 38, 0, 1), 'car: a borrowed (gone) parked car is not there'); S.x = S.y = 0;
  G.TAKE.left = { x: 0, y: -6, yaw: 0, type: 'hatch' }; tick(); ok(SOLID.carHit(0, -2.1, 0, 1), 'car: the car left behind is solid'); G.TAKE.left = null; }
// 10. kerb: a car is coming / has passed / stands
{ CAR.x = 1000; CAR.v = 0; window.__parked = []; window.__sig = { cars: [{ wx: -15, wy: 2, yaw: Math.PI / 2, k: 0, s: 9 }] }; tick(); ok(SOLID.coming(0, 0, 0, 3), 'kerb: a car 15 m away at 9 m/s is coming');
  window.__sig.cars[0].wx = 6; tick(); ok(!SOLID.coming(0, 0, 0, 3), 'kerb: a car that has passed is not'); window.__sig.cars[0].wx = -4; window.__sig.cars[0].s = 0; tick(); ok(!SOLID.coming(0, 0, 0, 3), 'kerb: a standing car is not'); }
console.log(fails ? fails + ' FAILED' : 'all passed'); process.exit(fails ? 1 : 0);
