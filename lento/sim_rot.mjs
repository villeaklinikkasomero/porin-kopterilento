// keyboard-style take-off: full back stick held from 52 kt until 30 ft, then stick neutral
globalThis.window = globalThis; globalThis.matchMedia = () => ({ matches: false }); globalThis.addEventListener = () => {};
globalThis.document = { createElement: () => ({ getContext: () => new Proxy({}, { get: () => () => {} }), style: {}, appendChild() {} }), body: { appendChild() {}, classList: { toggle() {} } } };
globalThis.performance = { now: () => Date.now() };
const THREE = await import('../three.module.min.js');
const log = []; const ti = { f: 0, t: 0, l: 0, r: 0 };
window.__game = { keys: new Set(), touchIn: ti, carGround: () => 0, TZs: () => 0, S: {}, toast: m => log.push(m), setCam() {}, camMode: 0, camera: {}, scene: { add() {} }, world() {}, fadeDo: f => f() };
const g = new THREE.Group(), model = new THREE.Group(); g.add(model); window.__jumpPlane = { g, model, x: 0, y: 0, yaw: 0 };
await import('./lento.js'); await new Promise(r => setTimeout(r, 400));
const P = window.__plane; P.on = true; const E = P.eng, c = P.ctl, A = P.air, dt = 1 / 60; let t = 0;
const pitch = () => Math.asin(new THREE.Vector3(0, 0, -1).applyQuaternion(P.q).y) * 57.3;
const hdg = () => { const f = new THREE.Vector3(0, 0, -1).applyQuaternion(P.q); return Math.atan2(f.x, -f.z); };
E.master = true; E.mixture = 1; E.running = true; E.rpm = 900; c.park = false; c.flapSel = c.flap = 10; E.throttle = 1;
let maxP = 0, off = null;
for (let i = 0; i < 60 / dt; i++) { const kt = A.ias * 1.944;
  ti.r = Math.max(-1, Math.min(1, -hdg() * 6 + P.w.y * 3)); ti.t = 0;
  const MODE = process.argv[2] || 'hold'; window.__game.keys[(MODE === 'hold' ? kt > 52 && A.agl < 9 : kt > 52 && pitch() < (A.onGround ? 8 : 6) && A.agl < 40) ? 'add' : 'delete']('KeyS');      // hold S from 52 kt / pulse it to hold ~8 deg
  P.step(dt); t += dt; if (P.dead) { console.log('DEAD', t.toFixed(1), log.at(-1)); break; }
  maxP = Math.max(maxP, pitch()); if (kt > 50 && i % 15 === 0 && A.agl < 3) console.log(t.toFixed(2), Math.round(kt), "kt pitch", pitch().toFixed(1), "ei", P.ctl.ei.toFixed(2), "alpha", (A.a*57.3).toFixed(1), "N", P.air.wload.toFixed(0), "wx", P.w.x.toFixed(3)); if (off === null && !A.onGround && kt > 40) { off = t; console.log('lift-off', t.toFixed(1), 's', Math.round(kt), 'kt pitch', pitch().toFixed(1)); }
  if (A.agl > 60) { console.log('60 m at', t.toFixed(1), 's, max pitch', maxP.toFixed(1), 'ias', Math.round(kt)); break; } }
console.log(log.filter(m => !/käynnist/.test(m)).join(' | ')); process.exit(0);
