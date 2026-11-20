// ---------- Hyppykone OH-HPX: lentomalli, ohjaus, mittaristo ja äänet (20.11.2026) ----------
// Owner 20.11.2026: "tehdään sen verran realistinen, että vauhti pitää kiihdyttää nousuun ja siihen menee realistinen aika ... mahdollisimman realistinen",
// "lentokoneessa voi olla enemmän säätimiä". A Cessna 182 type (O-470, 230 hp, constant-speed prop) as a rigid body with six degrees of freedom:
//  - aerodynamics from stability derivatives (Cessna 182 / 172 data as used in JSBSim and Roskam), stall and post-stall lift, wing drop and
//    autorotation when stalled, ground effect, flaps 0-40 deg, elevator trim, propeller slipstream over the tail (rudder works on the take-off roll);
//  - engine: manifold pressure from the throttle, governor RPM from the prop lever, mixture (best power, too lean stops it), carb heat, magnetos,
//    starter and master switch, CHT / oil temperature, fuel flow; thrust from power and propeller efficiency, P-factor, torque and windmilling drag;
//  - three tyres on springs with rolling friction, toe brakes, parking brake and nosewheel steering; wingtip, tail, propeller and belly strikes.
// Take-off at about 1290 kg: 0 -> 55 kt in roughly 15-20 s and some 250 m of runway, climb about 900 ft/min at 80 kt (POH: 795 ft ground roll,
// 924 ft/min at MTOW). Everything runs in three's frame (x east, y up, z south); the body frame is three's object frame: forward -z, right +x, up +y.
// The game (index.html) calls __plane.step / __plane.cam while the player sits in the plane; see the hooks marked "jump plane" there.
import * as THREE from '../three.module.min.js';

const V3 = THREE.Vector3, QT = THREE.Quaternion;
const KT = 1.943844, FT = 3.28084, D2R = Math.PI / 180;
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const sstep = (a, b, x) => { const t = clamp((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };

/* ---------------------------------------------------------------- aircraft data */
const AC = {
  m: 1290,                       // kg: empty 890 + pilot + 3 jumpers + 120 l fuel
  S: 16.2, b: 11.0, c: 1.49, e: 0.77,
  I: new V3(1825, 2667, 1285),   // kg m2 about body right (pitch), up (yaw), back (roll)
  cg: new V3(0, 1.25, 0.95),     // model coordinates (x port, y up, z nose) of the centre of gravity
  // longitudinal
  CL0: 0.307, CLa: 4.41, CLq: 3.9, CLde: 0.29, aStall: 0.268, CLmin: -0.75,
  CD0: 0.0245, CDde: 0.06,
  Cm0: 0.04, Cma: -0.613, Cmq: -12.4, Cmade: -7.27, Cmde: -0.75,      // Roskam gives Cmde -1.12, which would trim at 46 deg alpha with full up
                                                                   // elevator; the nose-heavy C182 just reaches the stall with the yoke fully back
  // lateral-directional
  CYb: -0.393, CYdr: 0.187,
  Clb: -0.0923, Clp: -0.484, Clr: 0.0798, Clda: 0.229, Cldr: 0.0147,
  Cnb: 0.0587, Cnp: -0.0278, Cnr: -0.0937, Cnda: -0.0216, Cndr: -0.0645,
  // control throws (rad)
  deUp: 25 * D2R, deDn: 17 * D2R, da: 20 * D2R, dr: 24 * D2R, steer: 11 * D2R,
  // flaps 0 10 20 30 40 deg: lift, drag, pitching moment, stall angle change
  flap: { deg: [0, 10, 20, 30, 40], dCL: [0, 0.25, 0.48, 0.64, 0.74], dCD: [0, 0.006, 0.016, 0.030, 0.046], dCm: [0, -0.02, -0.04, -0.055, -0.065], dAs: [0, -0.01, -0.02, -0.03, -0.035] },
  // engine / propeller
  Pmax: 171500, rpmMax: 2600, Tstatic: 2900, propR: 1.04,
};
const lerpTab = (xs, ys, x) => { if (x <= xs[0]) return ys[0]; for (let i = 1; i < xs.length; i++) if (x <= xs[i]) { const t = (x - xs[i - 1]) / (xs[i] - xs[i - 1]); return ys[i - 1] + (ys[i] - ys[i - 1]) * t; } return ys[ys.length - 1]; };
const AR = AC.b * AC.b / AC.S, Kind = 1 / (Math.PI * AC.e * AR);

// local points relative to the CG (body frame: right +x, up +y, back +z); model (x port, y up, z nose) -> local (-x, y - cg.y, cg.z - z)
const L = (mx, my, mz) => new V3(-mx, my - AC.cg.y, AC.cg.z - mz);
const WHEELS = [
  { n: 'main_port', p: L(1.22, 0, 0.40), k: 95000, c: 7500, brake: 1, steer: 0 },      // mains ~0.55 m behind the CG, under mid-chord as on the C182
  { n: 'main_stbd', p: L(-1.22, 0, 0.40), k: 95000, c: 7500, brake: 1, steer: 0 },
  { n: 'nose', p: L(0, 0, 3.05), k: 60000, c: 5200, brake: 0, steer: 1 },
  { n: 'tail', p: L(0, 1.52, -4.62), k: 40000, c: 4500, brake: 0, steer: 0, skid: true },      // tail tie-down ring: scrapes on an over-rotation
];
const STRIKE = [
  ['siivenkärki', L(5.55, 2.30, 0.80)], ['siivenkärki', L(-5.55, 2.30, 0.80)], ['pyrstö', L(0, 1.80, -5.25)],
  ['korkeusvakaaja', L(1.8, 1.76, -4.9)], ['korkeusvakaaja', L(-1.8, 1.76, -4.9)], ['vatsa', L(0, 0.78, 1.0)], ['vatsa', L(0, 0.80, -1.5)], ['konepelti', L(0, 0.80, 3.4)],
];
const HUB = L(0, 1.25, 4.05);
const EYE = L(0.27, 1.90, 1.02);      // pilot's eyes (left seat): the glareshield about 22 cm below, the panel in the lower part of the view
const MODEL_ORIGIN = L(0, 0, 0);

/* ---------------------------------------------------------------- state */
const P = window.__plane = {
  on: false, ready: false, g: null, model: null,
  pos: new V3(), vel: new V3(), q: new QT(), w: new V3(),       // CG position (three), velocity, orientation, body rates (rad/s about local axes)
  ctl: { e: 0, a: 0, r: 0, ei: 0, ai: 0, ri: 0, trim: 0.10, flapSel: 0, flap: 0, brake: 0, park: true },
  eng: { master: false, mags: 3, starter: false, crank: 0, running: false, rpm: 0, throttle: 0, prop: 1, mixture: 0, carb: false, cowl: 1, map: 29.9, cht: 15, oil: 15, oilP: 0, ff: 0, egt: 15, power: 0, thrust: 0, fuel: 64 },
  lights: { nav: false, strobe: false, land: false, beacon: false },
  assist: matchMedia('(pointer:coarse)').matches,      // touch: auto rudder, auto mixture, one-button start
  air: { V: 0, ias: 0, a: 0, b: 0, rho: 1.225, stall: 0, gload: 1, onGround: true, agl: 0, vs: 0 },
  easy: true,      // helppo ohjaus (8): nuolet kaartavat koordinoidusti, siivet oikenevat
  look: { yaw: 0, pitch: -0.2 }, dead: 0, msg: '', help: false, hornT: 0,
};
window.__planeDebug = P;
const _v = new V3(), _v2 = new V3(), _v3 = new V3(), _q = new QT(), _F = new V3(), _M = new V3();

const gm = () => window.__game;
function groundZ(x, y) { const G = gm(); const z = G.carGround ? G.carGround(x, y) : null; return z !== null && z !== undefined ? z : G.TZs(x, y); }
function atmo(h) { const t = 1 - 2.25577e-5 * Math.max(-500, h); return { rho: 1.225 * Math.pow(t, 4.2559), pa: 29.92 * Math.pow(t, 5.2559), sig: Math.pow(t, 4.2559), T: 15 - 0.0065 * h }; }

/* ---------------------------------------------------------------- set-up once the parked plane (index.html EFPO block) has loaded */
function setup() {
  const J = window.__jumpPlane; if (!J || !J.model || P.ready) return;
  P.g = J.g; P.model = J.model; const m = P.model;
  P.nodes = {}; for (const n of ['propeller', 'door', 'aileron_port', 'aileron_stbd', 'flap_port', 'flap_stbd', 'elevator', 'rudder', 'yoke', 'throttle_knob', 'prop_knob', 'mixture_knob']) P.nodes[n] = m.getObjectByName(n);
  for (const k of ['yoke', 'throttle_knob', 'prop_knob', 'mixture_knob']) if (P.nodes[k]) P.nodes[k].userData.z0 = P.nodes[k].position.z;
  // materials for the lights and the panel
  P.mats = {}; m.traverse(o => { if (o.isMesh && o.material && o.material.name) P.mats[o.material.name] = o.material; if (o.isMesh && o.material && o.material.name === 'instrument_panel') P.panelMesh = o; });
  for (const k of ['nav_red', 'nav_green', 'strobe_white', 'beacon_red', 'light_lens']) if (P.mats[k]) { P.mats[k].emissiveIntensity = 0; P.mats[k].userData.e0 = P.mats[k].emissive.clone(); }
  if (P.mats.light_lens) P.mats.light_lens.emissive.setRGB(1, 0.97, 0.88);
  // live instrument panel: the panel face gets the gauge canvas
  P.panel = document.createElement('canvas'); P.panel.width = 1024; P.panel.height = 390;
  P.panelTex = new THREE.CanvasTexture(P.panel); P.panelTex.flipY = false; P.panelTex.colorSpace = THREE.SRGBColorSpace; P.panelTex.anisotropy = 8;
  if (P.panelMesh) { const old = P.panelMesh.material; P.panelMesh.material = new THREE.MeshStandardMaterial({ map: P.panelTex, emissiveMap: P.panelTex, emissive: new THREE.Color(0.55, 0.55, 0.55), roughness: 0.6, metalness: 0 }); P.panelMesh.material.userData.noT = true; old.dispose(); }
  // propeller disc for the blur
  if (P.nodes.propeller) { const disc = new THREE.Mesh(new THREE.CircleGeometry(AC.propR, 40), new THREE.MeshBasicMaterial({ color: 0x141414, transparent: true, opacity: 0, side: THREE.DoubleSide, depthWrite: false }));
    disc.position.z = 0.02; P.nodes.propeller.add(disc); P.propDisc = disc; P.propBlades = P.nodes.propeller.children.filter(c => c !== disc && c.isMesh && !/spinner|alu/.test(c.material.name)); }
  // the soft shadow lives on the ground, not on the plane
  P.shadow = P.g.getObjectByName('planeShadow'); if (P.shadow) { P.g.remove(P.shadow); gm().scene.add(P.shadow); }
  P.park = { x: J.x, y: J.y, yaw: J.yaw };
  resetToPark(); P.ready = true;
}

function resetToPark() {
  const k = P.park, gz = groundZ(k.x, k.y);
  P.q.setFromAxisAngle(new V3(0, 1, 0), -k.yaw);
  // CG height with the tyres just loaded (static deflection about 4 cm)
  P.pos.set(k.x, gz + AC.cg.y - 0.045, -k.y); P.vel.set(0, 0, 0); P.w.set(0, 0, 0);
  Object.assign(P.ctl, { e: 0, a: 0, r: 0, ei: 0, ai: 0, ri: 0, trim: 0.10, flapSel: 0, flap: 0, brake: 0, park: true });
  Object.assign(P.eng, { master: false, mags: 3, starter: false, crank: 0, running: false, rpm: 0, throttle: 0, prop: 1, mixture: 0, carb: false, cowl: 1, cht: 15, oil: 15, oilP: 0, ff: 0, egt: 15, power: 0, thrust: 0, fuel: 64 });
  Object.assign(P.lights, { nav: false, strobe: false, land: false, beacon: false });
  P.dead = 0; place();
}

P.reset = (park) => { if (park) Object.assign(P.park, park); resetToPark(); };

/* ---------------------------------------------------------------- engine & propeller */
function stepEngine(dt, at, V) {
  const E = P.eng, c = P.ctl;
  // mixture: best power mixture leans with altitude; too lean and the engine quits, too rich runs rough
  const mBest = 0.92 * Math.sqrt(at.sig), mr = E.mixture / mBest;
  const fMix = mr < 0.55 ? 0 : mr < 1 ? 0.6 + 0.4 * Math.sin((mr - 0.55) / 0.45 * Math.PI / 2) : mr < 1.25 ? 1 - 0.1 * (mr - 1) : Math.max(0.55, 0.975 - 0.35 * (mr - 1.25));
  const magF = E.mags === 3 ? 1 : E.mags === 0 ? 0 : 0.96;
  // starter / running
  const canRun = E.master || E.running;      // magnetos fire without the battery, but starting needs it
  E.starter = E.starter && E.master;
  if (!E.running) {
    if (E.starter) { E.crank += dt; E.rpm += (260 - E.rpm) * Math.min(1, dt * 3); if (E.crank > 1.1 && magF > 0 && mr > 0.45 && mr < 1.7 && E.throttle < 0.6) { E.running = true; P.toast('Moottori käynnistyi', 1.6); } }
    else { E.crank = 0; const wm = V * 24; E.rpm += (wm - E.rpm) * Math.min(1, dt * 0.6); }
  }
  if (E.running) E.fuel = Math.max(0, E.fuel - E.ff * 3.785 / 3600 * dt / 3.785);      // US gal
  if (E.running && (magF === 0 || mr < 0.5 || E.fuel <= 0)) { E.running = false; P.toast(magF === 0 ? 'Magneetot pois – moottori sammui' : E.fuel <= 0 ? 'Polttoaine loppui' : 'Seos liian laiha – moottori sammui', 2.2); }
  // manifold pressure (inHg)
  const mapT = E.running ? 8.8 + E.throttle * (at.pa - 1.1 - 8.8) : at.pa;
  E.map += (mapT - E.map) * Math.min(1, dt * 4);
  // indicated power at the current rpm, less friction; the governor holds the prop lever's rpm when there is power to do it
  const pw = rpm => { if (!E.running) return 0; const pf = clamp((E.map - 7.5) / (29.0 - 7.5), 0, 1.1); return AC.Pmax * pf * Math.pow(rpm / AC.rpmMax, 0.85) * fMix * magF * (E.carb ? 0.9 : 1) - 9000 * Math.pow(rpm / AC.rpmMax, 2); };
  const rpmSet = 2100 + 500 * E.prop;
  if (E.running) {
    // fine-pitch absorption rises with rho and rpm^3 and falls with airspeed (advance ratio)
    const absorb = rpm => 165000 * (at.rho / 1.225) * Math.pow(rpm / AC.rpmMax, 3) * Math.max(0.2, 1 - V / (rpm / AC.rpmMax * 70));
    let r = Math.max(500, E.rpm);
    for (let i = 0; i < 6; i++) { const p = Math.max(1000, pw(r)); r = clamp(r * Math.pow(p / absorb(r), 0.25), 450, 2900); }
    const tgt = Math.min(r, rpmSet);
    E.rpm += (tgt - E.rpm) * Math.min(1, dt * 2.2);
  }
  E.power = Math.max(0, pw(E.rpm));
  // thrust: efficiency rises with speed, static thrust is capped; a windmilling or idling prop drags
  const eta = 0.88 * V / (V + 13);
  let T = E.power > 0 ? Math.min(AC.Tstatic * Math.pow(E.power / AC.Pmax, 0.85) * Math.pow(at.sig, 0.3), eta * E.power / Math.max(V, 0.5)) : 0;
  const idleDrag = 0.5 * at.rho * V * V * (E.running ? 0.045 : 0.09) * (1 - 0.6 * clamp(E.power / 40000, 0, 1));
  T -= idleDrag; E.thrust = T;
  // temperatures, oil, fuel flow
  const pr = E.power / AC.Pmax;
  E.ff = E.running ? (E.power / 745.7) * 0.46 / 6.0 * (mr > 1 ? mr : 1) + 1.2 : 0;           // US gal/h
  const egtT = E.running ? 330 + 420 * pr * (1 - 1.4 * Math.abs(mr - 0.93)) + 60 * pr + (E.carb ? -15 : 0) : at.T;      // ~650-750 C at full rich take-off power, peak near best economy
  E.egt += (egtT - E.egt) * Math.min(1, dt * 0.5);
  const chtT = E.running ? 95 + 150 * pr + 40 * clamp(1 - Math.abs(mr - 0.93) * 2, 0, 1) - 35 * E.cowl - V * 0.45 : at.T;
  E.cht += (chtT - E.cht) * Math.min(1, dt / 45);
  const oilT = E.running ? 70 + 40 * pr + 6 * (1 - E.cowl) : at.T;
  E.oil += (oilT - E.oil) * Math.min(1, dt / 160);
  E.oilP += ((E.running ? clamp(25 + E.rpm / 2600 * 45 - (E.oil - 70) * 0.15, 0, 80) : E.rpm / 2600 * 20) - E.oilP) * Math.min(1, dt * 2);
}

/* ---------------------------------------------------------------- one physics sub-step */
const RIGHT = new V3(1, 0, 0), UPV = new V3(0, 1, 0), FWD = new V3(0, 0, -1);
function physics(dt, gz, at) {
  const c = P.ctl, E = P.eng, A = P.air, qi = _q.copy(P.q).invert();
  _F.set(0, -9.80665 * AC.m, 0);           // world force: gravity
  _M.set(0, 0, 0);                          // body moment
  // ---- aerodynamics
  const vb = _v.copy(P.vel).applyQuaternion(qi);      // still air
  const V = vb.length(); A.V = V;
  const qd = 0.5 * at.rho * V * V;
  const hw = P.pos.y + 0.92 - gz;                     // wing above ground
  const ge = (() => { const x = 16 * Math.max(0.1, hw) / AC.b; return x * x / (1 + x * x); })();
  const fl = c.flap, fdeg = AC.flap.deg;
  const dCLf = lerpTab(fdeg, AC.flap.dCL, fl), dCDf = lerpTab(fdeg, AC.flap.dCD, fl), dCmf = lerpTab(fdeg, AC.flap.dCm, fl), dAs = lerpTab(fdeg, AC.flap.dAs, fl);
  // propeller slipstream over the tail (actuator disc: extra dynamic pressure T / A, about 40 % of it reaches the tail)
  const qSlip = Math.max(0, E.thrust) / (Math.PI * AC.propR * AC.propR) * 0.3;
  const qTail = qd + qSlip;
  const de = c.e >= 0 ? c.e * AC.deUp : c.e * AC.deDn;        // elevator up positive (nose up)
  const deT = -(de + c.trim * 0.18);                            // FRD elevator (trailing edge down positive); trim tab as an offset
  const da = c.a * AC.da, dr = -c.r * AC.dr;                    // FRD: aileron positive rolls right; rudder positive = trailing edge left (right pedal is negative)
  if (V > 0.6) {
    const alpha = Math.atan2(-vb.y, -vb.z), beta = Math.asin(clamp(vb.x / V, -1, 1));
    const p = -P.w.z, q = P.w.x, r = -P.w.y;                    // FRD body rates
    const pn = p * AC.b / (2 * V), qn = q * AC.c / (2 * V), rn = r * AC.b / (2 * V);
    const aS = AC.aStall + dAs, CLmax = AC.CL0 + AC.CLa * aS + dCLf;
    let CL = AC.CL0 + AC.CLa * alpha + dCLf;
    let stall = 0;
    if (alpha > aS) { stall = sstep(aS, aS + 0.10, alpha); const post = CLmax * (1 - 0.32 * stall) - (alpha - aS - 0.10) * 0.8 * stall; CL = Math.max(1.05 * Math.sin(2 * alpha), Math.min(CL, post)); }
    else if (CL < AC.CLmin) { stall = sstep(AC.CLmin, AC.CLmin - 0.3, CL); CL = Math.max(AC.CLmin * 0.8, 1.05 * Math.sin(2 * alpha)); }
    if (Math.abs(alpha) > 0.6) CL = 1.05 * Math.sin(2 * alpha);
    CL += AC.CLq * qn * (qTail / Math.max(qd, 1)) + AC.CLde * deT * clamp(qTail / Math.max(qd, 1), 1, 3);
    A.stall = stall; A.a = alpha; A.b = beta;
    const CDi = Kind * ge * Math.pow(Math.min(CL, CLmax), 2);
    const CD = AC.CD0 + dCDf + CDi + 1.25 * Math.pow(Math.sin(alpha), 2) * sstep(aS * 0.8, aS + 0.25, Math.abs(alpha)) + 0.25 * beta * beta + AC.CDde * Math.abs(deT) * 0.3;
    const CY = AC.CYb * beta + AC.CYdr * dr * (qTail / Math.max(qd, 1));
    // stalled wing: lost roll damping (autorotation) and a wing drop towards the slipping/low side
    const Clp = AC.Clp * (1 - 1.25 * stall);
    let Cl = AC.Clb * beta + Clp * pn + AC.Clr * rn + AC.Clda * da * (1 - 0.5 * stall) + AC.Cldr * dr;
    Cl += stall * (0.018 * Math.sign(beta + p * 0.05 + 1e-4) + 0.008 * Math.sin(performance.now() / 610));
    const kT = qTail / Math.max(qd, 1);
    const adot = P.lastA === undefined ? 0 : clamp((alpha - P.lastA) / dt, -3, 3); P.lastA = alpha;
    const Cm = AC.Cm0 + AC.Cma * alpha + AC.Cmq * qn * Math.sqrt(kT) + AC.Cmade * adot * AC.c / (2 * V) + AC.Cmde * deT * kT + dCmf - 0.15 * stall - 0.16 * (1 - ge);      // ground effect: less downwash on the tail -> nose-down near the ground
    const Cn = AC.Cnb * beta + AC.Cnp * pn + AC.Cnr * rn * Math.sqrt(kT) + AC.Cnda * da + AC.Cndr * dr * kT;
    // forces in the body frame
    const vh = _v2.copy(vb).divideScalar(V);
    const liftDir = _v3.crossVectors(RIGHT, vh).normalize();
    const Fb = new V3().addScaledVector(liftDir, CL * qd * AC.S).addScaledVector(vh, -CD * qd * AC.S).addScaledVector(RIGHT, CY * qd * AC.S);
    _F.add(Fb.applyQuaternion(P.q));
    _M.x += Cm * qd * AC.S * AC.c; _M.y += -Cn * qd * AC.S * AC.b; _M.z += -Cl * qd * AC.S * AC.b;
    A.CL = CL;
  } else {
    // standing still: the slipstream still lets the rudder and elevator push the tail
    _M.x += AC.Cmde * deT * qSlip * AC.S * AC.c * 0.6; _M.y += -AC.Cndr * dr * qSlip * AC.S * AC.b * 0.6; A.stall = 0; A.a = 0; A.b = 0;
  }
  // ---- engine: thrust along the crankshaft, P-factor and slipstream swirl yaw the nose left, torque rolls left
  _F.addScaledVector(_v.copy(FWD).applyQuaternion(P.q), E.thrust);
  const T = Math.max(0, E.thrust);
  _M.y += T * (0.03 + 0.25 * Math.max(0, A.a)) + 0.075 * T * Math.max(0, 1 - A.V / 45);          // left yaw (positive about up)
  _M.z += 0.22 * E.power / Math.max(30, E.rpm * Math.PI / 30);                                      // left roll (positive about back)
  // ---- landing gear
  let onG = false; A.wload = 0;
  for (const W of WHEELS) {
    const rw = _v.copy(W.p).applyQuaternion(P.q);                       // world offset
    const px = P.pos.x + rw.x, py = P.pos.y + rw.y, pz = P.pos.z + rw.z;
    const gzw = W.gz;                                                    // ground under the wheel (cached each frame)
    const pen = gzw - py; W.pen = pen;
    if (pen <= 0) { W.n = 0; continue; }
    onG = true;
    const wW = _v2.copy(P.w).applyQuaternion(P.q);                       // angular velocity in world
    const vp = _v3.crossVectors(wW, rw).add(P.vel);                      // contact point velocity
    const N = Math.max(0, W.k * pen - W.c * vp.y); W.n = N; A.wload += N;
    if (W.skid) { if (pen > 0.16 || vp.y < -2.6) { crash('Pyrstö iskeytyi maahan'); return; } if (!P.tailWarn) { P.tailWarn = 4; P.toast('Pyrstö raapaisi maata – nokka liian ylhäällä', 2); } }
    else if (pen > 0.32 || (vp.y < -4.2 && pen > 0.05)) { crash('Laskuteline petti – liian kova lasku'); return; }
    // tyre heading on the ground plane
    const st = W.steer ? c.r * AC.steer * clamp(1 - P.air.V / 30, 0.15, 1) : 0;
    const fw = new V3(Math.sin(st), 0, -Math.cos(st)).applyQuaternion(P.q); fw.y = 0; fw.normalize();
    const sd = new V3(-fw.z, 0, fw.x);                                  // right of the tyre
    const vl = vp.dot(fw), vs = vp.dot(sd);
    let br = W.brake ? Math.max(c.brake, c.park ? 1 : 0) : 0;
    if (W.brake && c.brake > 0 && Math.abs(c.r) > 0.3) br *= (W.n === 0 ? 1 : (W.p.x < 0) === (c.r < 0) ? 1 : 0.45);     // toe brakes follow the pedal you push
    const mu = W.skid ? 0.4 : 0.018 + 0.55 * br, muS = W.skid ? 0.4 : 0.75;
    const Fl = -N * mu * Math.tanh(vl / 0.08), Fs = -N * muS * Math.tanh(vs / 0.12);
    const Fw = new V3(0, N, 0).addScaledVector(fw, Fl).addScaledVector(sd, Fs);
    _F.add(Fw);
    const tq = new V3().crossVectors(rw, Fw).applyQuaternion(qi);
    _M.add(tq);
  }
  A.onGround = onG;
  // ---- integrate
  P.vel.addScaledVector(_F, dt / AC.m);
  P.pos.addScaledVector(P.vel, dt);
  const I = AC.I, w = P.w;
  const Iw = new V3(I.x * w.x, I.y * w.y, I.z * w.z), gyro = new V3().crossVectors(w, Iw);
  w.x += (_M.x - gyro.x) / I.x * dt; w.y += (_M.y - gyro.y) / I.y * dt; w.z += (_M.z - gyro.z) / I.z * dt;
  const ang = w.length() * dt; if (ang > 1e-9) { _q.setFromAxisAngle(_v.copy(w).normalize(), ang); P.q.multiply(_q).normalize(); }
  A.gload = _v.copy(_F).sub(new V3(0, -9.80665 * AC.m, 0)).applyQuaternion(qi).y / (AC.m * 9.80665);
}

function crash(why) {
  if (P.dead) return; P.dead = 3.2; P.eng.running = false; P.eng.rpm = 0; P.vel.multiplyScalar(0.2); P.w.set(0, 0, 0);
  P.toast('💥 ' + why + '. Kone hinataan takaisin asematasolle.', 3.2);
}

/* ---------------------------------------------------------------- controls */
const K = c => gm().keys.has(c);
const ONCE = new Set();
addEventListener('keydown', e => { if (!P.on || e.repeat) return; if (e.target && e.target.tagName === 'INPUT') return; ONCE.add(e.code);
  if (['Space', 'ShiftLeft', 'ShiftRight', 'KeyG', 'KeyV', 'KeyP', 'KeyO', 'KeyI', 'KeyH', 'KeyZ', 'KeyX', 'KeyK', 'KeyL', 'KeyU', 'KeyJ', 'KeyB'].includes(e.code)) e.preventDefault(); });
function readControls(dt) {
  const c = P.ctl, E = P.eng, ti = gm().touchIn || { f: 0, t: 0, l: 0 };
  const ax = (pos, neg) => (pos.some(K) ? 1 : 0) - (neg.some(K) ? 1 : 0);
  // stick: W / Up pushes (nose down), S / Down pulls (nose up); keyboard deflections build up over ~0.4 s and centre when released
  const pitchIn = clamp(ax(['KeyS', 'ArrowDown'], ['KeyW', 'ArrowUp']) - (ti.f || 0), -1, 1);
  // 20.11.2026 (omistaja: "takalaipan käännökset nuolinäppäimillä"): ← / → kääntävät sivuperäsintä (maassa nokkapyörää) ja helppo ohjaus kallistaa
  // konetta samaan suuntaan noin 25° (koordinoitu kaarto); kun nuolet päästetään, siivet oikaistaan. A / D ovat yhä siivekkeet suoraan, Q / E peräsin.
  const turn = ax(['ArrowRight'], ['ArrowLeft']);
  let rollIn = clamp(ax(['KeyD'], ['KeyA']) + (ti.t || 0), -1, 1);
  let yawIn = clamp(ax(['KeyE'], ['KeyQ']) + (ti.r || 0) + turn * (P.air.onGround ? 1 : 0.12), -1, 1);
  if (P.easy && !P.air.onGround && !ax(['KeyD'], ['KeyA']) && !(ti.t || 0)) {
    const rt = _v.set(1, 0, 0).applyQuaternion(P.q), up = _v2.set(0, 1, 0).applyQuaternion(P.q), roll = Math.atan2(-rt.y, up.y), p = -P.w.z;
    rollIn = clamp((turn * 0.44 - roll) * 2.2 - p * 0.7, -1, 1); }
  const rate = (cur, tgt, up, dn) => cur + clamp(tgt - cur, -(Math.abs(tgt) < Math.abs(cur) ? dn : up) * dt, (Math.abs(tgt) < Math.abs(cur) ? dn : up) * dt);
  // keys move the controls like hands on a yoke: the elevator builds up ~0.5 of its travel per second held (a short press = a gentle
  // rotation, holding on = full back stick and a stall), ailerons ~0.5 s; touch / analogue input is direct
  const ana = Math.abs(ti.f || 0) > 0.01; c.ei = ana ? rate(c.ei, pitchIn, 6, 6) : rate(c.ei, pitchIn * (P.air.wload > 3000 ? 0.75 : 1), 0.5, 2.5);      // on the wheels keys give at most half travel (a take-off never needs more)
  c.ai = P.easy && !P.air.onGround && !ax(['KeyD'], ['KeyA']) && !(ti.t || 0) ? rate(c.ai, rollIn, 3, 4.5) : rate(c.ai, rollIn, 2.2, 4.5);      // (20.11: this line was inside the comment above, so A / D did nothing)
  if (P.assist && !yawIn) yawIn = clamp(-P.air.b * 4 + (P.air.onGround ? 0 : 0.25 * c.ai), -1, 1);       // touch helper: keeps the ball centred
  c.ri = rate(c.ri, yawIn, 2.5, 3.5);
  c.e = c.ei; c.a = c.ai; c.r = c.ri;
  // throttle (Space more, Shift less), prop rpm (X / Z), mixture (L richer, K leaner), trim (U nose up, J nose down)
  const thr = ax(['Space'], ['ShiftLeft', 'ShiftRight']) + (ti.l || 0);
  E.throttle = clamp(E.throttle + thr * dt * 0.45, 0, 1);
  E.prop = clamp(E.prop + ax(['KeyX'], ['KeyZ']) * dt * 0.4, 0, 1);
  E.mixture = clamp(E.mixture + ax(['KeyL'], ['KeyK']) * dt * 0.35, 0, 1);
  c.trim = clamp(c.trim + ax(['KeyU'], ['KeyJ']) * dt * 0.12, -1, 1);
  c.brake = K('KeyB') || ti.brake ? 1 : 0;
  E.starter = K('KeyI') || !!ti.start;
  // one-shot switches
  for (const code of ONCE) {
    if (code === 'KeyG') { c.flapSel = Math.min(40, c.flapSel + 10); P.toast('Laipat ' + c.flapSel + '°', 1); }
    if (code === 'KeyV') { c.flapSel = Math.max(0, c.flapSel - 10); P.toast('Laipat ' + c.flapSel + '°', 1); }
    if (code === 'KeyP') { c.park = !c.park; P.toast(c.park ? 'Seisontajarru päällä' : 'Seisontajarru vapautettu', 1.3); }
    if (code === 'KeyO') { E.master = !E.master; P.toast(E.master ? 'Päävirta päällä' : 'Päävirta pois', 1.2); }
    if (code === 'KeyH') { E.carb = !E.carb; P.toast(E.carb ? 'Kaasuttimen lämmitys päällä' : 'Kaasuttimen lämmitys pois', 1.2); }
    if (code === 'KeyM' && false) {}
    if (code === 'Digit1') { P.lights.nav = !P.lights.nav; P.toast('Navigointivalot ' + (P.lights.nav ? 'päällä' : 'pois'), 1); }
    if (code === 'Digit2') { P.lights.strobe = !P.lights.strobe; P.toast('Strobot ' + (P.lights.strobe ? 'päällä' : 'pois'), 1); }
    if (code === 'Digit3') { P.lights.land = !P.lights.land; P.toast('Laskuvalo ' + (P.lights.land ? 'päällä' : 'pois'), 1); }
    if (code === 'Digit4') { P.lights.beacon = !P.lights.beacon; P.toast('Majakkavalo ' + (P.lights.beacon ? 'päällä' : 'pois'), 1); }
    if (code === 'Digit5') { E.cowl = E.cowl > 0.5 ? 0 : 1; P.toast('Jäähdytysläpät ' + (E.cowl ? 'auki' : 'kiinni'), 1); }
    if (code === 'Digit6') { E.mags = (E.mags + 1) % 4; P.toast('Magneetot: ' + ['POIS', 'R', 'L', 'MOLEMMAT'][E.mags], 1.2); }
    if (code === 'Digit8') { P.easy = !P.easy; P.toast('Helppo ohjaus ' + (P.easy ? 'päällä: ← → kaartaa, siivet oikenevat itsestään' : 'pois: ← → vain sivuperäsin'), 1.8); }
    if (code === 'Digit9') { P.assist = !P.assist; P.toast('Avustimet ' + (P.assist ? 'päällä (peräsin, seos, käynnistys)' : 'pois'), 1.6); }
    if (code === 'Digit7') { P.strip = !P.strip; P.toast('Mittaripalkki ' + (P.strip ? 'piilossa' : 'näkyvissä'), 1); }
    if (code === 'Digit0') { P.help = !P.help; helpEl().style.display = P.help ? 'block' : 'none'; }
  }
  ONCE.clear();
  // helpers (touch): automatic mixture for the altitude, one-button start
  if (P.assist) { const at = atmo(P.pos.y); if (E.running || E.starter) E.mixture += (Math.min(1, 0.92 * Math.sqrt(at.sig) * 1.05) - E.mixture) * Math.min(1, dt * 0.8);
    if (E.starter) { E.master = true; E.mags = 3; if (E.mixture < 0.6) E.mixture = 1; } }
  // electric flaps: ~4 deg/s, need the battery
  if (E.master) c.flap += clamp(c.flapSel - c.flap, -4 * dt, 4 * dt);
}

/* ---------------------------------------------------------------- per-frame step (called by index.html instead of the helicopter / car) */
let hornOsc = null;
P.step = dt => {
  if (!P.ready) return;
  const G = gm();
  if (P.dead > 0) { P.dead -= dt; if (P.dead <= 0) { G.fadeDo(() => { resetToPark(); }); } place(); return; }
  readControls(dt);
  // ground heights under the wheels once per frame
  for (const W of WHEELS) { const rw = _v.copy(W.p).applyQuaternion(P.q); W.gz = groundZ(P.pos.x + rw.x, -(P.pos.z + rw.z)); }
  const gz = groundZ(P.pos.x, -P.pos.z), at = atmo(P.pos.y); P.air.rho = at.rho;
  stepEngine(dt, at, P.air.V);
  const n = Math.max(1, Math.ceil(dt / (1 / 240))), h = dt / n;
  for (let i = 0; i < n && !P.dead; i++) physics(h, gz, at);
  if (P.dead) { place(); return; }
  // strikes and obstacles
  for (const [nm, p] of STRIKE) { const r = _v.copy(p).applyQuaternion(P.q); const x = P.pos.x + r.x, y = -(P.pos.z + r.z); if (P.pos.y + r.y < groundZ(x, y) - 0.03) { crash('Osuma maahan: ' + nm); break; } }
  { const r = _v.copy(HUB).add(new V3(0, -AC.propR, 0)).applyQuaternion(P.q); if (!P.dead && P.eng.rpm > 200 && P.pos.y + r.y < groundZ(P.pos.x + r.x, -(P.pos.z + r.z)) + 0.02) crash('Potkuri osui maahan'); }
  if (!P.dead && G.bldTopAt) { const top = G.bldTopAt(P.pos.x, -P.pos.z); if (top > gz + 2 && P.pos.y < top + 0.4) crash('Törmäys rakennukseen'); }
  const Vkt = P.air.V * KT;
  if (!P.dead && Vkt > 205) crash('Rakenne petti – nopeus yli sallitun (Vne 175 kt)');
  if (!P.dead && (P.air.gload > 5.7 || P.air.gload < -3.0)) crash('Rakenne petti – liian suuri kuormitus');
  if (!P.dead && (P.air.gload > 3.8 || P.air.gload < -1.52)) { if (!P.gWarn) { P.gWarn = 3; P.toast('Kuormitus ' + P.air.gload.toFixed(1) + ' g – sallittu +3,8 / −1,5 g', 2); } }
  if (P.gWarn) P.gWarn = Math.max(0, P.gWarn - dt); if (P.tailWarn) P.tailWarn = Math.max(0, P.tailWarn - dt);
  // flap overspeed: they jam where they are
  if (P.ctl.flap > 10.5 && Vkt > 110) { P.ctl.flapSel = P.ctl.flap; if (!P.flapWarn) { P.flapWarn = true; P.toast('Laippanopeus ylitetty (> 95 kt) – laipat juuttuivat', 2.5); } }
  P.air.agl = P.pos.y - AC.cg.y - gz; P.air.vs = P.vel.y; P.air.ias = P.air.V * Math.sqrt(at.rho / 1.225);
  place(dt); sound(dt); lights(dt);
  // the rest of the game follows the plane: map, tiles, trees
  const fw = _v.copy(FWD).applyQuaternion(P.q), yaw = Math.atan2(fw.x, -fw.z), S = G.S;
  S.x = P.pos.x; S.y = -P.pos.z; S.yaw = yaw; S.alt = P.air.agl + 1.85; S.vx = P.vel.x; S.vy = -P.vel.z; S.vz = P.vel.y; S.landed = P.air.onGround; S.pitch = 0; S.roll = 0;
  if (G.world) G.world(S.x, S.y);
  panelDraw(dt);
};

function place(dt = 1 / 60) {
  if (!P.g) return;
  P.g.quaternion.copy(P.q); P.g.position.copy(P.pos).add(_v.copy(MODEL_ORIGIN).applyQuaternion(P.q));
  const N = P.nodes, c = P.ctl;
  if (N.elevator) N.elevator.rotation.x = (c.e >= 0 ? c.e * AC.deUp : c.e * AC.deDn) + c.trim * 0.05;
  if (N.aileron_port) N.aileron_port.rotation.x = -c.a * AC.da;
  if (N.aileron_stbd) N.aileron_stbd.rotation.x = c.a * AC.da;
  if (N.flap_port) N.flap_port.rotation.x = -c.flap * D2R; if (N.flap_stbd) N.flap_stbd.rotation.x = -c.flap * D2R;
  if (N.rudder) N.rudder.rotation.y = c.r * AC.dr;
  if (N.yoke) { N.yoke.position.z = N.yoke.userData.z0 - c.e * 0.07; N.yoke.rotation.z = -c.a * 0.6; }
  for (const [k, v] of [['throttle_knob', P.eng.throttle], ['prop_knob', P.eng.prop], ['mixture_knob', P.eng.mixture]]) if (N[k]) N[k].position.z = N[k].userData.z0 + (v - 1) * 0.06;
  if (N.propeller) { N.propeller.rotation.z += P.eng.rpm / 60 * 2 * Math.PI * dt;
    const blur = sstep(350, 1100, P.eng.rpm); if (P.propDisc) P.propDisc.material.opacity = (gm().camMode === 1 ? 0.07 : 0.15) * blur; for (const b of P.propBlades || []) b.visible = blur < 0.85; }
  // shadow straight below, fading with height
  if (P.shadow) { const gz = groundZ(P.pos.x, -P.pos.z), agl = P.pos.y - AC.cg.y - gz; const fw = _v.copy(FWD).applyQuaternion(P.q);
    P.shadow.position.set(P.pos.x, gz + 0.04, P.pos.z);
    P.shadow.rotation.order = 'YXZ'; P.shadow.rotation.set(-Math.PI / 2, Math.atan2(-fw.x, -fw.z), 0);
    P.shadow.material.opacity = clamp(1 - agl / 60, 0, 1); P.shadow.visible = agl < 60; }
}
function lights(dt) {
  const t = performance.now() / 1000, Mt = P.mats || {}, E = P.eng, on = E.master;
  const set = (k, v) => { const m = Mt[k]; if (m) m.emissiveIntensity = v; };
  set('nav_red', on && P.lights.nav ? 2 : 0); set('nav_green', on && P.lights.nav ? 2 : 0);
  set('strobe_white', on && P.lights.strobe && (t % 1.2) < 0.06 ? 8 : 0);
  set('beacon_red', on && P.lights.beacon && (t % 1.0) < 0.15 ? 4 : 0);
  set('light_lens', on && P.lights.land ? 3 : 0);
}

/* ---------------------------------------------------------------- cameras */
const camPos = new V3(), camLook = new V3(), camDir = new V3();
let drag = null;
addEventListener('pointerdown', e => { if (P.on && e.target && e.target.id === 'gl') drag = { x: e.clientX, y: e.clientY }; });
addEventListener('pointermove', e => { if (!drag) return; P.look.yaw -= (e.clientX - drag.x) * 0.005; P.look.pitch = clamp(P.look.pitch - (e.clientY - drag.y) * 0.005, -1.2, 1.0); drag = { x: e.clientX, y: e.clientY }; });
addEventListener('pointerup', () => { drag = null; });
P.cam = (dt, mode) => {
  const cam = gm().camera;
  if (mode === 1) {
    if (cam.near !== 0.05) { cam.near = 0.05; cam.updateProjectionMatrix(); }
    if (!drag) { P.look.yaw *= Math.exp(-dt * 0.8); }
    cam.position.copy(P.pos).add(_v.copy(EYE).applyQuaternion(P.q));
    // small head movement with the g-load and the runway
    cam.position.y -= clamp((P.air.gload - 1) * 0.02, -0.04, 0.06);
    const lq = new QT().setFromEuler(new THREE.Euler(P.look.pitch, P.look.yaw, 0, 'YXZ'));
    cam.quaternion.copy(P.q).multiply(lq); return;
  }
  if (cam.near !== 0.3) { cam.near = 0.3; cam.updateProjectionMatrix(); }
  if (mode === 2) { cam.position.set(P.pos.x, P.pos.y + 160, P.pos.z + 1); cam.up.set(0, 1, 0); cam.lookAt(P.pos); return; }
  // chase: a constant distance behind; only the direction is smoothed (flight path in the air, the tail on the ground), so it never lags at speed
  const fw = _v.copy(FWD).applyQuaternion(P.q); const hd = new V3(fw.x, 0, fw.z).normalize();
  const want = P.air.V > 12 && !P.air.onGround ? _v2.copy(P.vel).normalize().lerp(fw, 0.35).normalize() : hd;
  if (camDir.lengthSq() === 0) camDir.copy(want); camDir.lerp(want, 1 - Math.exp(-dt * 3)).normalize();
  camPos.copy(P.pos).addScaledVector(camDir, -16).add(new V3(0, 2.0, 0));
  const gzc = groundZ(camPos.x, -camPos.z); if (camPos.y < gzc + 1.5) camPos.y = gzc + 1.5;
  camLook.copy(P.pos).addScaledVector(camDir, 10).add(new V3(0, 2.4, 0));      // the plane sits above the instrument strip
  cam.position.copy(camPos); cam.up.set(0, 1, 0); cam.lookAt(camLook);
};

/* ---------------------------------------------------------------- boarding / leaving */
P.near = (x, y) => { if (!P.ready || P.on || P.dead) return false; const d = Math.hypot(x - P.pos.x, y + P.pos.z); return d < 6.5; };
P.enter = () => { P.on = true; P.look.yaw = 0; P.look.pitch = -0.2; camDir.set(0, 0, 0); gm().setCam(1); helpEl(); ui(true);
  P.toast(P.eng.running ? 'Ohjaamossa – 0 näyttää ohjeet' : 'Ohjaamossa. Käynnistys: O päävirta, L seos rikkaaksi, Space vähän kaasua, pidä I. Ohjeet: 0', 6); };
P.exitReq = () => {
  const G = gm();
  if (!P.air.onGround && P.air.agl > 250 && window.__jump) { window.__jump.start(); return; }      // parachute jump (laskuvarjo/hyppy.js, 21.11.2026): Enter in the air above 250 m
  if (!P.air.onGround || P.air.V > 1.0) { P.toast(P.air.onGround ? 'Pysäytä kone ensin' : 'Hyppy onnistuu yli 250 m korkeudesta – nyt ' + Math.round(P.air.agl) + ' m', 1.8); return; }
  if (P.eng.running) { P.eng.mixture = 0; P.toast('Seos köyhäksi – moottori sammutettu', 1.6); }
  P.ctl.park = true; P.eng.master = false;
  const sd = new V3(1.0, 0, 0).applyQuaternion(P.q).multiplyScalar(-1);      // pilot's door is on the left
  const x = P.pos.x + sd.x * 1.6, y = -(P.pos.z + sd.z * 1.6), fw = _v.copy(FWD).applyQuaternion(P.q);
  P.on = false; ui(false); helpEl().style.display = 'none'; P.help = false; stopSound();
  G.walkOutAt(x, y, Math.atan2(fw.x, -fw.z));
};

// parachute jump (21.11.2026): the player leaves the flying plane. The door opens, the cockpit UI goes, and the plane flies on by itself (P.ghost,
// called by laskuvarjo/hyppy.js): wings level on its heading at its speed. After 50 s, or 2.5 km from the jumper, it is back on the apron.
P.leave = () => { P.on = false; ui(false); helpEl().style.display = 'none'; P.help = false; stopSound(); P.ghostOn = true; P.ghostT = 0; if (P.nodes && P.nodes.door) P.nodes.door.rotation.z = -1.5; };
P.ghost = (dt, jp) => { if (!P.ghostOn) return; P.ghostT += dt; const fw = _v.copy(FWD).applyQuaternion(P.q), yaw = Math.atan2(P.vel.x, -P.vel.z), sp = Math.max(36, Math.hypot(P.vel.x, P.vel.z));
  P.vel.set(Math.sin(yaw) * sp, P.vel.y * Math.exp(-dt * 1.5), -Math.cos(yaw) * sp); P.pos.addScaledVector(P.vel, dt); P.q.slerp(_q.setFromAxisAngle(_v2.set(0, 1, 0), -yaw), Math.min(1, dt * 1.5)); P.w.set(0, 0, 0); place(dt);
  if (P.ghostT > 50 || (jp && Math.hypot(jp.x - P.pos.x, jp.z - P.pos.z) > 2500)) { P.ghostOn = false; if (P.nodes && P.nodes.door) P.nodes.door.rotation.z = 0; resetToPark(); } };

/* ---------------------------------------------------------------- HUD: instrument strip (outside views), help, touch buttons */
let hudEl = null, hudCv = null, helpDiv = null, tbtn = null;
P.toast = (m, s) => { const G = gm(); if (G && G.toast) G.toast(m, s); };
function helpEl() {
  if (helpDiv) return helpDiv;
  helpDiv = document.createElement('div'); helpDiv.id = 'planehelp';
  helpDiv.style.cssText = 'position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);background:rgba(10,16,22,.88);color:#e8eef2;font:14px/1.45 system-ui,sans-serif;padding:16px 22px;border-radius:12px;z-index:60;display:none;max-width:640px;columns:2;column-gap:28px;pointer-events:none';
  const rows = [['Ohjaus', ''], ['W / S, ↑ / ↓', 'sauva eteen / taakse'], ['← / →', 'kaarto: sivuperäsin + kallistus (maassa nokkapyörä)'], ['A / D', 'kallistus (siivekkeet)'], ['Q / E', 'sivuperäsin ja nokkapyörä'], ['8', 'helppo ohjaus päälle / pois'], ['B', 'jarrut (pidä)'], ['P', 'seisontajarru'],
    ['Moottori', ''], ['Space / Shift', 'kaasu lisää / vähemmän'], ['X / Z', 'potkurin kierrokset + / −'], ['L / K', 'seos rikkaampi / laihempi'], ['H', 'kaasuttimen lämmitys'], ['O', 'päävirta'], ['6', 'magneetot'], ['I', 'käynnistin (pidä)'],
    ['Lentäminen', ''], ['G / V', 'laipat alas / ylös (10°)'], ['U / J', 'trimmi nokka ylös / alas'], ['1 2 3 4', 'navi, strobo, laskuvalo, majakka'], ['5', 'jäähdytysläpät'], ['9', 'avustimet'], ['C', 'kamera (ohjaamo, ulko, ylhäältä)'], ['7', 'mittaripalkki ulkokamerassa'], ['Hiiri', 'katsele ohjaamossa'], ['Enter', 'poistu (kone pysähdyksissä)'],
    ['Lentoonlähtö', ''], ['', 'Laipat 10–20°, trimmi lentoonlähtöön, kaasu täysille, oikeaa peräsintä. Nokka ylös 50 kt, nousu 70–80 kt. Laskeutuminen 65–70 kt laipat 30–40°.']];
  helpDiv.innerHTML = rows.map(([a, b]) => b === '' ? `<div style="font-weight:700;color:#ffc928;margin-top:6px;break-after:avoid">${a}</div>` : `<div><b style="display:inline-block;min-width:96px">${a}</b> ${b}</div>`).join('');
  document.body.appendChild(helpDiv); return helpDiv;
}
function ui(on) {
  if (!hudEl) {
    hudEl = document.createElement('div'); hudEl.id = 'planehud'; hudEl.style.cssText = 'position:fixed;left:50%;bottom:8px;transform:translateX(-50%);z-index:20;pointer-events:none;display:none';
    hudCv = document.createElement('canvas'); hudCv.width = 1024; hudCv.height = 350; hudCv.style.cssText = 'width:min(500px,80vw);border-radius:8px;opacity:.94'; hudEl.appendChild(hudCv); document.body.appendChild(hudEl);
    if (matchMedia('(pointer:coarse)').matches) {      // touch: flaps, brake, start
      tbtn = document.createElement('div'); tbtn.style.cssText = 'position:fixed;right:10px;top:40%;display:flex;flex-direction:column;gap:8px;z-index:30';
      const ti = () => gm().touchIn;
      const mk = (txt, down, up) => { const b = document.createElement('button'); b.textContent = txt; b.style.cssText = 'font:600 14px system-ui;padding:10px 12px;border-radius:10px;border:0;background:rgba(14,22,30,.75);color:#fff';
        b.addEventListener('pointerdown', e => { e.preventDefault(); down(); }); if (up) { b.addEventListener('pointerup', up); b.addEventListener('pointercancel', up); } tbtn.appendChild(b); };
      mk('Käynnistä', () => { ti().start = 1; }, () => { ti().start = 0; });
      mk('Laipat +', () => ONCE.add('KeyG')); mk('Laipat −', () => ONCE.add('KeyV'));
      mk('Jarru', () => { ti().brake = 1; }, () => { ti().brake = 0; }); mk('Seis.jarru', () => ONCE.add('KeyP'));
      mk('Kamera', () => gm().setCam((gm().camMode + 1) % 3)); mk('Poistu', () => P.exitReq());
      document.body.appendChild(tbtn);
    }
  }
  hudEl.style.display = on ? 'block' : 'none'; if (tbtn) tbtn.style.display = on ? 'flex' : 'none';
  document.body.classList.toggle('plane', on);
}

/* ---------------------------------------------------------------- the instrument panel (drawn on the 3D panel and on the screen strip) */
let panT = 0;
function gauge(g, cx, cy, R, label) {
  g.save(); g.translate(cx, cy);
  g.fillStyle = '#0b0c0d'; g.beginPath(); g.arc(0, 0, R, 0, 7); g.fill();
  g.strokeStyle = '#6d7276'; g.lineWidth = 5; g.beginPath(); g.arc(0, 0, R + 2, 0, 7); g.stroke();
  if (label) { g.fillStyle = '#9aa0a5'; g.font = '600 12px system-ui'; g.textAlign = 'center'; g.fillText(label, 0, R * 0.55); }
  g.restore();
}
function dial(g, cx, cy, R, v0, v1, a0, a1, ticks, labels, arcs) {
  const ang = v => a0 + (a1 - a0) * (v - v0) / (v1 - v0);
  g.save(); g.translate(cx, cy);
  for (const [s, e, col, w] of arcs || []) { g.strokeStyle = col; g.lineWidth = w || 6; g.beginPath(); g.arc(0, 0, R - 8, ang(s) - Math.PI / 2, ang(e) - Math.PI / 2); g.stroke(); }
  g.strokeStyle = '#e9e9e9'; g.fillStyle = '#e9e9e9'; g.font = '600 13px system-ui'; g.textAlign = 'center'; g.textBaseline = 'middle';
  for (let v = v0; v <= v1 + 1e-6; v += ticks) { const a = ang(v); g.lineWidth = 2; g.beginPath(); g.moveTo(Math.sin(a) * (R - 4), -Math.cos(a) * (R - 4)); g.lineTo(Math.sin(a) * (R - 13), -Math.cos(a) * (R - 13)); g.stroke(); }
  for (const [v, t] of labels || []) { const a = ang(v); g.fillText(t, Math.sin(a) * (R - 26), -Math.cos(a) * (R - 26)); }
  g.restore(); return ang;
}
function needle(g, cx, cy, a, len, w, col) { g.save(); g.translate(cx, cy); g.rotate(a); g.fillStyle = col || '#f4f4f4'; g.beginPath(); g.moveTo(-w, 6); g.lineTo(0, -len); g.lineTo(w, 6); g.closePath(); g.fill(); g.fillStyle = '#222'; g.beginPath(); g.arc(0, 0, 5, 0, 7); g.fill(); g.restore(); }
function panelDraw(dt) {
  if ((panT -= dt) > 0) return; panT = 1 / 15;
  const cv = P.panel; if (!cv) return; const g = cv.getContext('2d'), A = P.air, E = P.eng, c = P.ctl;
  g.setTransform(1, 0, 0, 1, 0, 0); g.fillStyle = '#2a2c2f'; g.fillRect(0, 0, 1024, 390);
  g.fillStyle = '#232527'; g.fillRect(0, 0, 1024, 40); g.translate(0, 40);
  const R = 66, X = [92, 242, 392], Y = [92, 244];
  const fw = new V3(0, 0, -1).applyQuaternion(P.q), up = new V3(0, 1, 0).applyQuaternion(P.q), rt = new V3(1, 0, 0).applyQuaternion(P.q);
  const pitch = Math.asin(clamp(fw.y, -1, 1)), roll = Math.atan2(-rt.y, up.y), hdg = ((Math.atan2(fw.x, -fw.z) / D2R) + 360) % 360;
  // airspeed (kt)
  gauge(g, X[0], Y[0], R, 'KNOTS'); { const an = dial(g, X[0], Y[0], R, 0, 200, -2.6, 2.6, 10, [[40, '40'], [60, '60'], [80, '80'], [100, '100'], [120, '120'], [140, '140'], [160, '160'], [180, '180']], [[41, 95, '#f2f2f2', 4], [50, 145, '#2fb34a', 6], [145, 175, '#e8c21c', 6], [174, 176, '#e2231a', 8]]); needle(g, X[0], Y[0], an(clamp(A.ias * KT, 0, 200)), R - 12, 4); }
  // attitude
  { const cx = X[1], cy = Y[0]; g.save(); g.beginPath(); g.arc(cx, cy, R, 0, 7); g.clip(); g.translate(cx, cy); g.rotate(-roll);
    const off = clamp(pitch / D2R, -30, 30) * 2.2; g.fillStyle = '#2f7fd0'; g.fillRect(-150, -150 + off, 300, 150); g.fillStyle = '#8a5a2b'; g.fillRect(-150, off, 300, 150);
    g.strokeStyle = '#fff'; g.lineWidth = 2; g.beginPath(); g.moveTo(-150, off); g.lineTo(150, off); g.stroke();
    for (const p of [-20, -10, 10, 20]) { const y = off - p * 2.2; g.beginPath(); g.moveTo(-14 - (Math.abs(p) > 10 ? 8 : 0), y); g.lineTo(14 + (Math.abs(p) > 10 ? 8 : 0), y); g.stroke(); }
    g.restore(); g.save(); g.translate(cx, cy); g.strokeStyle = '#ffb100'; g.lineWidth = 4; g.beginPath(); g.moveTo(-40, 0); g.lineTo(-14, 0); g.lineTo(-7, 8); g.moveTo(40, 0); g.lineTo(14, 0); g.lineTo(7, 8); g.stroke(); g.restore();
    g.strokeStyle = '#6d7276'; g.lineWidth = 5; g.beginPath(); g.arc(cx, cy, R + 2, 0, 7); g.stroke(); }
  // altimeter (ft, 100s and 1000s hands)
  const altFt = (P.pos.y + 0) * FT; gauge(g, X[2], Y[0], R, 'ALT');
  { const an = dial(g, X[2], Y[0], R, 0, 1000, 0, 2 * Math.PI, 100, [[0, '0'], [100, '1'], [200, '2'], [300, '3'], [400, '4'], [500, '5'], [600, '6'], [700, '7'], [800, '8'], [900, '9']]);
    needle(g, X[2], Y[0], (altFt / 10000) * 2 * Math.PI, R * 0.45, 5); needle(g, X[2], Y[0], an(((altFt % 1000) + 1000) % 1000), R - 12, 3);
    g.fillStyle = '#ddd'; g.font = '600 12px system-ui'; g.textAlign = 'center'; g.fillText(Math.round(altFt) + ' ft', X[2], Y[0] + 30); }
  // turn coordinator with the ball
  gauge(g, X[0], Y[1], R, '2 MIN'); { const tr = -P.w.y; g.save(); g.translate(X[0], Y[1] - 6); g.rotate(clamp(tr / (3 * D2R) * 0.35, -0.7, 0.7)); g.strokeStyle = '#fff'; g.lineWidth = 4; g.beginPath(); g.moveTo(-42, 0); g.lineTo(42, 0); g.moveTo(0, 0); g.lineTo(0, -10); g.stroke(); g.restore();
    g.fillStyle = '#ddd'; g.fillRect(X[0] - 40, Y[1] + 22, 80, 14); const sl = clamp(-A.b * 4 + 0, -1, 1); g.fillStyle = '#111'; g.beginPath(); g.arc(X[0] + sl * 32, Y[1] + 29, 6.5, 0, 7); g.fill(); }
  // heading indicator
  gauge(g, X[1], Y[1], R, ''); { g.save(); g.translate(X[1], Y[1]); g.rotate(-hdg * D2R); g.fillStyle = '#eee'; g.strokeStyle = '#eee'; g.font = '700 13px system-ui'; g.textAlign = 'center'; g.textBaseline = 'middle';
    for (let d = 0; d < 360; d += 10) { const a = d * D2R; g.lineWidth = d % 30 ? 1.5 : 2.5; g.beginPath(); g.moveTo(Math.sin(a) * (R - 4), -Math.cos(a) * (R - 4)); g.lineTo(Math.sin(a) * (R - (d % 30 ? 10 : 15)), -Math.cos(a) * (R - (d % 30 ? 10 : 15))); g.stroke();
      if (d % 30 === 0) { g.save(); g.rotate(a); g.fillText({ 0: 'N', 90: 'E', 180: 'S', 270: 'W' }[d] || String(d / 10), 0, -(R - 26)); g.restore(); } }
    g.restore(); g.fillStyle = '#ffb100'; g.beginPath(); g.moveTo(X[1], Y[1] - R + 2); g.lineTo(X[1] - 7, Y[1] - R + 16); g.lineTo(X[1] + 7, Y[1] - R + 16); g.fill();
    g.strokeStyle = '#ffb100'; g.lineWidth = 3; g.beginPath(); g.moveTo(X[1], Y[1] - 26); g.lineTo(X[1], Y[1] + 22); g.moveTo(X[1] - 18, Y[1]); g.lineTo(X[1] + 18, Y[1]); g.stroke(); }
  // vertical speed
  gauge(g, X[2], Y[1], R, 'VERT SPEED'); { const an = dial(g, X[2], Y[1], R, -2000, 2000, -Math.PI / 2 - 0.94 * Math.PI, -Math.PI / 2 + 0.94 * Math.PI, 500, [[-2000, '20'], [-1000, '10'], [0, '0'], [1000, '10'], [2000, '20']]);
    needle(g, X[2], Y[1], an(clamp(A.vs * FT * 60, -2000, 2000)), R - 12, 4); }
  // engine column: tach, manifold pressure / fuel flow, oil, CHT, EGT
  const ex = 560;
  gauge(g, ex, Y[0], 60, 'RPM x100'); { const an = dial(g, ex, Y[0], 60, 0, 3500, -2.4, 2.4, 500, [[0, '0'], [1000, '10'], [2000, '20'], [3000, '30']], [[2100, 2600, '#2fb34a', 6], [2590, 2610, '#e2231a', 8]]); needle(g, ex, Y[0], an(E.rpm), 48, 4);
    g.fillStyle = '#ddd'; g.font = '600 12px system-ui'; g.textAlign = 'center'; g.fillText(Math.round(E.rpm), ex, Y[0] + 24); }
  gauge(g, ex, Y[1], 60, 'MAN PRESS'); { const an = dial(g, ex, Y[1], 60, 10, 35, -2.4, 2.4, 5, [[10, '10'], [20, '20'], [30, '30']], [[15, 23, '#2fb34a', 6]]); needle(g, ex, Y[1], an(clamp(E.map, 10, 35)), 48, 4);
    g.fillStyle = '#ddd'; g.font = '600 12px system-ui'; g.textAlign = 'center'; g.fillText(E.ff.toFixed(1) + ' GPH', ex, Y[1] + 24); }
  const bar = (x, y, lab, v, lo, hi, gr0, gr1, unit) => { g.fillStyle = '#9aa0a5'; g.font = '600 12px system-ui'; g.textAlign = 'left'; g.fillText(lab, x, y - 6); g.fillStyle = '#0b0c0d'; g.fillRect(x, y, 150, 14);
    g.fillStyle = '#2fb34a'; g.fillRect(x + (gr0 - lo) / (hi - lo) * 150, y + 10, (gr1 - gr0) / (hi - lo) * 150, 4); g.fillStyle = '#f4f4f4'; const px = clamp((v - lo) / (hi - lo), 0, 1) * 150; g.fillRect(x + px - 2, y, 4, 14);
    g.fillStyle = '#ddd'; g.textAlign = 'right'; g.fillText(Math.round(v) + unit, x + 150, y - 6); };
  const bx = 660; bar(bx, 40, 'ÖLJYN LÄMPÖ', E.oil, 0, 140, 38, 116, '°C'); bar(bx, 84, 'ÖLJYN PAINE', E.oilP, 0, 100, 30, 60, ' psi'); bar(bx, 128, 'SYL. LÄMPÖ', E.cht, 0, 260, 90, 232, '°C'); bar(bx, 172, 'PAKOKAASU', E.egt, 0, 900, 0, 900, '°C');
  bar(bx, 216, 'POLTTOAINE', E.fuel, 0, 87, 20, 87, ' gal');
  // flaps, trim, switches, annunciators
  const sx = 850; g.textAlign = 'left'; g.font = '700 13px system-ui'; g.fillStyle = '#e9e9e9';
  g.fillText('LAIPAT ' + Math.round(c.flap) + '°' + (c.flapSel !== Math.round(c.flap) ? ' → ' + c.flapSel : ''), sx, 44);
  g.fillText('TRIMMI ' + (c.trim >= 0 ? '▲' : '▼') + ' ' + Math.round(Math.abs(c.trim) * 100), sx, 66);
  g.fillText('KAASU ' + Math.round(E.throttle * 100) + ' %', sx, 88); g.fillText('POTKURI ' + Math.round(2100 + 500 * E.prop), sx, 110); g.fillText('SEOS ' + Math.round(E.mixture * 100) + ' %', sx, 132);
  const lamp = (x, y, txt, on, col) => { g.fillStyle = on ? col : '#3a3d40'; g.fillRect(x, y, 70, 20); g.fillStyle = on ? '#111' : '#8a8f93'; g.font = '700 11px system-ui'; g.textAlign = 'center'; g.fillText(txt, x + 35, y + 14); g.textAlign = 'left'; };
  lamp(sx, 150, 'VIRTA', E.master, '#6fd16f'); lamp(sx + 80, 150, ['MAG POIS', 'MAG R', 'MAG L', 'MAG BOTH'][E.mags], E.mags === 3, '#6fd16f');
  lamp(sx, 176, 'SEIS.JARRU', c.park, '#ff9c2a'); lamp(sx + 80, 176, 'KAAS.LÄMP', E.carb, '#ffd84a');
  lamp(sx, 202, 'SAKKAUS', A.stall > 0.05 || A.a > 0.21, '#ff4b3e'); lamp(sx + 80, 202, 'ÖLJY', E.oilP < 20 && E.master, '#ff4b3e');
  lamp(sx, 228, 'NAVI', P.lights.nav, '#e9e9e9'); lamp(sx + 80, 228, 'STROBO', P.lights.strobe, '#e9e9e9');
  lamp(sx, 254, 'LASKUVALO', P.lights.land, '#e9e9e9'); lamp(sx + 80, 254, 'AVUSTIN', P.assist, '#79b8ff');
  g.fillStyle = '#9aa0a5'; g.font = '600 12px system-ui'; g.fillText('OH-HPX  ·  0 = ohjeet', sx, 300);
  g.fillStyle = '#d8d8d8'; g.font = '700 13px system-ui'; g.fillText('G ' + A.gload.toFixed(1) + '   GS ' + Math.round(new V3(P.vel.x, 0, P.vel.z).length() * KT) + ' kt', ex - 60, 318);
  if (P.panelTex) P.panelTex.needsUpdate = true;
  if (hudCv && hudEl.style.display !== 'none') { const cm = gm().camMode; hudEl.style.visibility = cm === 1 || P.strip ? 'hidden' : 'visible'; if (cm !== 1) hudCv.getContext('2d').drawImage(cv, 0, -40); }
}

/* ---------------------------------------------------------------- sound: engine (firing + prop), wind, stall horn, starter */
let S0 = null;
function sound(dt) {
  const G = gm(), ac = G.actx; if (!ac) return;
  if (!S0) {
    S0 = {}; const out = ac.createGain(); out.gain.value = 0; out.connect(ac.destination); S0.out = out;
    const eng = ac.createOscillator(); eng.type = 'sawtooth'; const ef = ac.createBiquadFilter(); ef.type = 'lowpass'; ef.frequency.value = 600; const eg = ac.createGain(); eg.gain.value = 0; eng.connect(ef); ef.connect(eg); eg.connect(out); eng.start(); Object.assign(S0, { eng, ef, eg });
    const prop = ac.createOscillator(); prop.type = 'triangle'; const pg = ac.createGain(); pg.gain.value = 0; prop.connect(pg); pg.connect(out); prop.start(); Object.assign(S0, { prop, pg });
    const nb = ac.createBuffer(1, ac.sampleRate * 2, ac.sampleRate), d = nb.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
    const ns = ac.createBufferSource(); ns.buffer = nb; ns.loop = true; const nf = ac.createBiquadFilter(); nf.type = 'bandpass'; nf.Q.value = 0.6; const ng = ac.createGain(); ng.gain.value = 0; ns.connect(nf); nf.connect(ng); ng.connect(out); ns.start(); Object.assign(S0, { nf, ng });
    const horn = ac.createOscillator(); horn.type = 'square'; horn.frequency.value = 2650; const hf = ac.createBiquadFilter(); hf.type = 'bandpass'; hf.frequency.value = 2650; hf.Q.value = 4; const hg = ac.createGain(); hg.gain.value = 0; horn.connect(hf); hf.connect(hg); hg.connect(out); horn.start(); Object.assign(S0, { hg });
    const st = ac.createOscillator(); st.type = 'sawtooth'; st.frequency.value = 95; const sg = ac.createGain(); sg.gain.value = 0; st.connect(sg); sg.connect(out); st.start(); Object.assign(S0, { sg, st });
  }
  const E = P.eng, cockpit = G.camMode === 1, k = Math.min(1, dt * 8), on = G.soundOn !== false;
  S0.out.gain.value += ((on && P.on ? (cockpit ? 0.9 : 0.6) : 0) - S0.out.gain.value) * k;
  const fire = E.rpm / 60 * 3;                            // six cylinders, four-stroke: 3 power strokes per turn
  S0.eng.frequency.value = Math.max(20, fire); S0.ef.frequency.value = 200 + E.rpm * 0.35 + E.power / 300;
  S0.eg.gain.value += ((E.running ? 0.05 + 0.07 * E.power / AC.Pmax : 0) - S0.eg.gain.value) * k;
  S0.prop.frequency.value = Math.max(15, E.rpm / 60 * 2); S0.pg.gain.value += (Math.min(0.08, E.rpm / 2600 * 0.08) * (E.rpm > 200 ? 1 : 0) - S0.pg.gain.value) * k;
  S0.nf.frequency.value = 300 + P.air.V * 18; S0.ng.gain.value += (Math.min(0.25, P.air.V * P.air.V / 6000) * (cockpit ? 0.6 : 1) + (P.air.onGround ? Math.min(0.05, P.air.V / 400) : 0) - S0.ng.gain.value) * k;
  const hornOn = !P.air.onGround && P.air.V > 8 && (P.air.a > 0.215 + lerpTab(AC.flap.deg, AC.flap.dAs, P.ctl.flap) || P.air.stall > 0.05) && P.eng.master;
  S0.hg.gain.value += ((hornOn ? 0.035 * (0.6 + 0.4 * Math.sin(performance.now() / 40)) : 0) - S0.hg.gain.value) * Math.min(1, dt * 20);
  S0.sg.gain.value += ((E.starter && !E.running && E.master ? 0.06 : 0) - S0.sg.gain.value) * k; S0.st.frequency.value = 80 + E.rpm * 0.15;
}
function stopSound() { if (S0) S0.out.gain.value = 0; }

/* ---------------------------------------------------------------- wait for the game and the model */
const boot = setInterval(() => { if (window.__game && window.__jumpPlane && window.__jumpPlane.model) { clearInterval(boot); setup(); } }, 300);
