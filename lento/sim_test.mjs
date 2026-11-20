// offline test of lento.js: take-off, climb, cruise, stall (flat ground at 0 m)
globalThis.window = globalThis; globalThis.matchMedia = () => ({ matches: false }); globalThis.addEventListener = () => {};
globalThis.document = { createElement: () => ({ getContext: () => new Proxy({}, { get: () => () => {} }), style: {}, appendChild() {} }), body: { appendChild() {}, classList: { toggle() {} } } };
globalThis.performance = { now: () => Date.now() };
const THREE = await import('../three.module.min.js');
const log = []; const ti = { f: 0, t: 0, l: 0, r: 0 };
window.__game = { keys: new Set(), touchIn: ti, carGround: () => 0, TZs: () => 0, S: {}, toast: m => log.push(m), setCam() {}, camMode: 0, camera: {}, scene: { add() {} }, world() {}, fadeDo: f => f() };
const g = new THREE.Group(), model = new THREE.Group(); g.add(model);
window.__jumpPlane = { g, model, x: 0, y: 0, yaw: 0 };      // heading north (game +y = three -z)
await import('./lento.js');
await new Promise(r => setTimeout(r, 400));
const P = window.__plane; P.on = true; clearInterval;
const dt = 1 / 60, E = P.eng, c = P.ctl, A = P.air; let t = 0;
const run = (sec, ctl) => { for (let i = 0; i < sec / dt; i++) { ctl && ctl(); P.step(dt); t += dt; if (P.dead) { console.log('DEAD', log.at(-1), t.toFixed(1)); return false; } } return true; };
const hdg = () => { const f = new THREE.Vector3(0, 0, -1).applyQuaternion(P.q); return Math.atan2(f.x, -f.z); };
const pitch = () => Math.asin(new THREE.Vector3(0, 0, -1).applyQuaternion(P.q).y);
const roll = () => { const r = new THREE.Vector3(1, 0, 0).applyQuaternion(P.q), u = new THREE.Vector3(0, 1, 0).applyQuaternion(P.q); return Math.atan2(-r.y, u.y); };
const KT = 1.943844, FPM = 196.85;
// pilot model: rudder holds the heading, ailerons the wings level, elevator a pitch target
let pT = 0, iP = 0;
const pilot = () => { ti.r = Math.max(-1, Math.min(1, -hdg() * 6 - (-P.w.y) * 3 ));
  ti.t = Math.max(-1, Math.min(1, -roll() * 3 + P.w.z * 1.5));
  if (pT !== null) { const e = pT - pitch(); iP += e * dt; ti.f = -Math.max(-1, Math.min(1, e * 4 + iP * 0.8 - P.w.x * 1.2)); } };
// 1) start
E.master = true; E.mixture = 1; E.throttle = 0.12; window.__game.keys.add('KeyI'); run(2.5); window.__game.keys.delete('KeyI');
console.log('start: running', E.running, 'rpm', Math.round(E.rpm), 'map', E.map.toFixed(1)); run(5);
console.log('idle:  rpm', Math.round(E.rpm), 'map', E.map.toFixed(1), 'thrust', Math.round(E.thrust), 'N');
// 2) take-off: flaps 20, park brake off, full power, rotate at 52 KIAS
c.park = false; c.flapSel = 20; c.flap = 20; E.throttle = 1; E.prop = 1; pT = 0;
let tRot = null, tOff = null, x0 = P.pos.clone(), t0 = t, d50 = null;
run(60, () => { pilot(); const v = A.ias * KT;
  if (tRot === null && v >= 52) { tRot = t - t0; pT = 0.13; }
  if (tOff === null && !A.onGround && tRot !== null) { tOff = t - t0; console.log('lift-off', tOff.toFixed(1), 's', Math.round(P.pos.distanceTo(x0)), 'm', Math.round(v), 'kt'); }
  if (d50 === null && A.agl > 15) { d50 = P.pos.distanceTo(x0); console.log('over 50 ft obstacle at', Math.round(d50), 'm,', (t - t0).toFixed(1), 's'); c.flapSel = 0; }
  if (t - t0 > 1 && Math.abs(t - t0 - 8) < dt / 2) console.log('  t+8s', Math.round(v), 'kt', 'rpm', Math.round(E.rpm), 'map', E.map.toFixed(1), 'T', Math.round(E.thrust));
});
console.log('rotate at', tRot && tRot.toFixed(1), 's');
// 3) climb at about 80 KIAS: pitch target adjusted for the speed
pT = 0.12; let samples = [];
run(90, () => { pilot(); const v = A.ias * KT; pT += (v - 80) * 0.0006; pT = Math.max(-0.05, Math.min(0.25, pT)); if (t > 0) samples.push([v, A.vs * FPM]); });
const last = samples.slice(-600); console.log('climb: ias', (last.reduce((a, s) => a + s[0], 0) / last.length).toFixed(0), 'kt  vs', (last.reduce((a, s) => a + s[1], 0) / last.length).toFixed(0), 'fpm  alt', Math.round(P.pos.y * 3.28), 'ft  cht', Math.round(E.cht), 'oil', Math.round(E.oil), 'stall', A.stall.toFixed(2));
// 4) cruise: 23 in / 2300 rpm, level
E.prop = 0.4; let tgtAlt = P.pos.y; pT = 0.0; iP = 0;
run(150, () => { pilot(); E.throttle = Math.min(1, E.throttle + (23 - E.map) * 0.002); pT = Math.max(-0.1, Math.min(0.15, (tgtAlt - P.pos.y) * 0.004 - A.vs * 0.02)); });
console.log('cruise: ias', Math.round(A.ias * KT), 'kt  map', E.map.toFixed(1), 'rpm', Math.round(E.rpm), 'power', Math.round(E.power / 745.7), 'hp  ff', E.ff.toFixed(1), 'gph  trim', c.trim);
// 5) stall: idle, hold altitude while it slows ~1 kt/s; at the break release back pressure, level the wings, add power
E.throttle = 0; let stallKt = null, hs = null, rec = false; iP = 0; const h0 = P.pos.y;
run(70, () => { pilot(); const v = A.ias * KT;
  if (!rec) pT = Math.min(0.45, pT + dt * 0.01 + Math.max(0, (h0 - P.pos.y)) * 0.0004);
  if (stallKt === null && A.stall > 0.3) { stallKt = v; hs = P.pos.y; rec = true; pT = -0.05; iP = 0; E.throttle = 1; console.log('stall at', Math.round(v), 'KIAS  alpha', (A.a * 57.3).toFixed(1), 'deg  roll', Math.round(roll() * 57.3)); }
  if (rec && v > 70 && pT < 0.08) pT = 0.08; });
console.log('recovered: altitude lost', Math.round((hs - Math.min(hs, P.pos.y)) * 3.28), 'ft (now', Math.round(A.vs * FPM), 'fpm)  max g ok');
console.log('after stall: ias', Math.round(A.ias * KT), 'vs', Math.round(A.vs * FPM), 'roll', Math.round(roll() * 57.3), 'pitch', Math.round(pitch() * 57.3));
console.log(log.join(' | '));
process.exit(0);
