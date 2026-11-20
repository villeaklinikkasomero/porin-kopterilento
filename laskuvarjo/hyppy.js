// ---------- Laskuvarjohyppy hyppykoneesta (21.11.2026; omistaja: "kaikki vaiheet mitä tarvitaan siihen, että hahmo hyppää lentokoneesta") ----------
// Enter lentävässä koneessa (yli 250 m maasta) = hyppy. Vaiheet: ovi auki ja kyykky ovella -> ponnistus -> vapaapudotus (A/D kääntää, W liuku
// eteenpäin) -> Väli tai Enter heittää apuvarjon -> avautuminen -> kuvun alla A/D = ohjauslenkit, S tai Väli = molemmat alas (jarru, loppuveto)
// -> alastulo -> kävellen eteenpäin. Jos varjoa ei avaa, automaattilaukaisin avaa sen 300 metrissä. Kone jatkaa itsekseen ja palaa asematasolle.
// Hahmo on pelin oma kävelijä (window.__walker, klipit window.__walkerClips), varusteet ja kupu laskuvarjo.js:stä. Peli kutsuu __jump.step /
// __jump.cam / __jump.action, kun __jump.on on tosi (index.html: koukut merkitty "parachute jump"); kaikki on three-koordinaateissa kuten lento.js.
import * as THREE from '../three.module.min.js';
import { makeRig } from './laskuvarjo.js';

const V3 = THREE.Vector3, QT = THREE.Quaternion, PIV = 1.22, G0 = 9.81, VT = 53, VC = 5.0, DDUR = 3.8, UP = new V3(0, 1, 0);
const ease = x => x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x), seg = (x, a, b) => Math.max(0, Math.min(1, (x - a) / (b - a))), lerp = (a, b, t) => a + (b - a) * t;
const gm = () => window.__game;
const J = window.__jump = { on: false, ph: '', t: 0, pos: new V3(), vel: new V3(), q: new QT(), yaw: 0, D: 0, bl: 0, br: 0, bank: 0, flare: 0, sink: 0, agl: 0, hard: 0 };
let rig = null, mix = null, act = null, spot = null, hud = null, wind = null, camP = new V3(), camL = new V3(), camInit = false, relT = -1, dT = -1, opT = -1, loopT = 0, landGz = 0;
const a = new V3(), b = new V3(), c = new V3(), qa = new QT(), qb = new QT(), m4 = new THREE.Matrix4();

function ground(x, z) { const G = gm(), y = -z; let g = G.TZs(x, y); const cg = G.carGround ? G.carGround(x, y) : null; if (cg !== null && cg !== undefined) g = Math.max(g, cg); if (G.bldTopAt) { const t = G.bldTopAt(x, y); if (t > g) g = t; } return g; }
function setup() { const G = gm(), root = window.__walker; rig = makeRig(root); G.scene.add(rig.canopy); mix = new THREE.AnimationMixer(root); act = {};
  for (const cl of window.__walkerClips || []) if (/^(Jump|Freefall|Pull|Opening|Canopy|Flare|Land)/.test(cl.name)) { const A = mix.clipAction(cl); A.play(); A.setEffectiveWeight(0); act[cl.name] = A; }
  spot = new THREE.Object3D(); spot.position.set(-0.40, 0.96, 0.15); spot.rotation.y = Math.PI / 2; window.__plane.model.add(spot); }      // oviaukon lattia, kasvot ulos koneen oikealle
function pose(w) { for (const n in act) { const k = w[n]; act[n].setEffectiveWeight(k ? k[0] : 0); if (k) act[n].time = k[1]; } mix.update(0); }
function hudSet(l1, l2) { if (!hud) { hud = document.createElement('div'); hud.style.cssText = 'position:fixed;left:50%;top:14px;transform:translateX(-50%);z-index:30;pointer-events:none;text-align:center;color:#fff;font:600 15px/1.35 system-ui,sans-serif;text-shadow:0 1px 4px rgba(0,0,0,.8);background:rgba(10,18,28,.45);border:1px solid rgba(255,255,255,.18);border-radius:10px;padding:8px 16px'; document.body.appendChild(hud); }
  hud.style.display = l1 === null ? 'none' : 'block'; if (l1 !== null) hud.innerHTML = '<div style="font-size:19px;font-variant-numeric:tabular-nums">' + l1 + '</div><div style="font-weight:400;font-size:13px;opacity:.92">' + l2 + '</div>'; }
function windSound(v) { const G = gm(), ac = G.actx; if (!ac) return; try { if (!wind) { const n = ac.sampleRate * 2, buf = ac.createBuffer(1, n, ac.sampleRate), d = buf.getChannelData(0); let l = 0; for (let i = 0; i < n; i++) { l = (l + 0.04 * (Math.random() * 2 - 1)) / 1.04; d[i] = l * 6; }      // ruskea kohina = ilmavirta
      const src = ac.createBufferSource(); src.buffer = buf; src.loop = true; const f = ac.createBiquadFilter(); f.type = 'lowpass'; const g = ac.createGain(); g.gain.value = 0; src.connect(f); f.connect(g); g.connect(ac.destination); src.start(); wind = { f, g }; }
    wind.g.gain.value = G.soundOn ? Math.min(0.5, v / 53 * 0.5) : 0; wind.f.frequency.value = 250 + v * 26; } catch (e) {} }
const key = (...k) => { const K = gm().keys; return k.some(c => K.has(c)) ? 1 : 0; };

J.start = () => { const G = gm(), P = window.__plane; if (J.on || !P || !P.model) return; if (!window.__walker) { if (G.loadWalker) G.loadWalker(); P.toast('Hyppääjä pukee varjoa – yritä hetken päästä uudelleen', 2); return; }
  if (!rig) setup(); if (!act.Freefall) { P.toast('Hahmossa ei ole hyppyanimaatioita (hahmo.js)', 2.5); return; }
  P.leave(); J.on = true; J.ph = 'door'; J.t = 0; J.D = 0; J.bl = J.br = J.bank = J.flare = 0; J.hard = 0; relT = dT = opT = -1; loopT = 0; camInit = false;
  rig.wear(true); Object.assign(rig.state, { pc: 'stowed', deploy: 0, brakeL: 0, brakeR: 0, toggles: false, collapse: 0 }); rig._rel = null;
  const W = G.walkG; G.scene.add(W); W.visible = true; G.toast('🪂 Ovi auki – hyppy!', 1.6); };
J.action = () => { if (J.ph === 'fall') { J.ph = 'pull'; J.t = 0; } };      // Enter / toimintopainike: avaa varjon

J.step = dt => { const G = gm(), P = window.__plane, W = G.walkG, S = rig.state; if (dt > 0.1) dt = 0.1; J.t += dt; loopT += dt; if (P.ghost) P.ghost(dt, J.pos);
  const w = {}; let attached = false; J.att = false;
  if (J.ph === 'door') { w.JumpDoor = [1, loopT % 3]; attached = true; if (J.t > 0.9) { J.ph = 'exit'; J.t = 0; } }
  else if (J.ph === 'exit') { w.JumpExit = [1, Math.min(1.199, J.t)]; if (relT < 0 && J.t < 0.54) attached = true; else if (relT < 0) { relT = 0;      // jalat irti: koneen nopeus mukaan + ponnistus sivulle
        spot.getWorldQuaternion(J.q); spot.getWorldPosition(J.pos).add(a.set(0, PIV * 0.55, -0.5).applyQuaternion(J.q)); J.vel.copy(P.vel).add(a.set(0, 0.4, -1.8).applyQuaternion(J.q)); J.yaw = Math.atan2(P.vel.x, -P.vel.z); }
    if (J.t >= 1.2) { J.ph = 'fall'; J.t = 0; } }
  else if (J.ph === 'fall') { w.Freefall = [1, loopT % 2]; if (key('Space')) J.action(); if (J.agl < 300) { J.action(); G.toast('Automaattilaukaisin avasi varjon', 2.2); } }
  else if (J.ph === 'pull') { w.Pull = [1, Math.min(1.599, J.t)]; if (J.t > 0.64 && S.pc === 'stowed') S.pc = 'hand'; if (J.t > 0.99 && dT < 0) { dT = 0; S.pc = 'out'; G.scene.updateMatrixWorld(true); rig.throwPilot(); } if (J.t >= 1.6) { J.ph = 'open'; J.t = 0; } }
  else if (J.ph === 'open') { if (J.D < 0.33) w.Freefall = [1, loopT % 2]; else { if (opT < 0) opT = 0; opT += dt; if (opT < 2.4) w.Opening = [1, opT]; else w.Canopy = [1, loopT % 4]; } if (J.D >= 1 && opT >= 2.4) { J.ph = 'fly'; J.t = 0; S.toggles = true; G.toast('Kupu auki. A / D ohjaa, S tai Väli jarruttaa – vedä molemmat alas juuri ennen maata', 5); } }
  if (dT >= 0 && J.D < 1) { dT += dt; J.D = Math.min(1, dT / DDUR); }
  S.deploy = J.D;
  // ohjaus
  const ti = G.touchIn || { f: 0, t: 0 }, left = Math.max(key('KeyA', 'ArrowLeft'), ti.t < -0.3 ? 1 : 0), right = Math.max(key('KeyD', 'ArrowRight'), ti.t > 0.3 ? 1 : 0), fwd = Math.max(key('KeyW', 'ArrowUp'), ti.f > 0.3 ? 1 : 0), back = Math.max(key('KeyS', 'ArrowDown', 'Space'), ti.f < -0.3 ? 1 : 0);
  if (J.ph === 'fly' || J.ph === 'land') { const fl = J.ph === 'fly'; const tl = fl ? Math.max(left * 0.72, back) : 1, tr = fl ? Math.max(right * 0.72, back) : 1, b0 = Math.min(J.bl, J.br);
    J.bl += (tl - J.bl) * Math.min(1, dt * 4); J.br += (tr - J.br) * Math.min(1, dt * 4); const bs = Math.min(J.bl, J.br); J.flare = Math.min(1, J.flare * Math.exp(-dt / 1.3) + Math.max(0, bs - b0) * 1.15);
    if (fl) { J.yaw += (J.br - J.bl) * 1.25 * dt; J.bank += (0.42 * (J.bl - J.br) - J.bank) * Math.min(1, dt * 2.5); const sp = lerp(10.5, 4.5, bs), sk = Math.max(0.3, lerp(4.6, 2.9, bs) + 2.4 * Math.abs(J.bl - J.br) - J.flare * 4.2);
      a.set(Math.sin(J.yaw) * sp, -sk, -Math.cos(J.yaw) * sp); J.vel.lerp(a, Math.min(1, dt * 2.2)); J.sink = -J.vel.y;
      const wL = Math.max(0, J.bl - bs) / 0.72, wR = Math.max(0, J.br - bs) / 0.72; w.Canopy = [Math.max(0, 1 - wL - wR - bs), loopT % 4]; w.CanopyL = [wL, 0.5]; w.CanopyR = [wR, 0.5]; w.Flare = [bs, 0.5]; }
    S.brakeL = J.bl; S.brakeR = J.br; }
  // liike
  if (!attached && J.ph !== 'land') { if (J.ph !== 'fly') { const cano = ease(seg(J.D, 0.35, 0.95)), vt = lerp(VT, VC, cano), k = G0 / (vt * vt), sp = J.vel.length();      // ilmanvastus ~ v^2: loppunopeus 53 m/s vatsallaan, 5 m/s kuvun alla
      if (J.ph === 'fall' || J.ph === 'exit') { J.yaw += (right - left) * 1.5 * dt; if (fwd) J.vel.add(a.set(Math.sin(J.yaw), 0, -Math.cos(J.yaw)).multiplyScalar(5 * dt)); }
      J.vel.y -= G0 * dt; J.vel.addScaledVector(J.vel, -k * sp * dt); if (cano > 0.5) { a.set(Math.sin(J.yaw) * 10.5, J.vel.y, -Math.cos(J.yaw) * 10.5); J.vel.lerp(a, Math.min(1, dt * 1.2 * (cano - 0.5))); } }      /* kupu alkaa liitää eteenpäin */
    J.pos.addScaledVector(J.vel, dt); }
  // vartalon asento
  if (attached) { spot.getWorldQuaternion(J.q); spot.getWorldPosition(J.pos); const out = J.ph === 'exit' ? 0.45 * (J.t / 0.54) ** 2 : 0; J.pos.add(a.set(0, 0, -out).applyQuaternion(J.q)); W.quaternion.copy(J.q); W.position.copy(J.pos); J.agl = J.pos.y - ground(J.pos.x, J.pos.z); }
  else { const up = ease(seg(J.D, 0.33, 0.56)), v = a.copy(J.vel).normalize(), fh = b.set(Math.sin(J.yaw), 0, -Math.cos(J.yaw)), wv = v.y * v.y;      // vatsa suhteelliseen tuuleen (aluksi eteenpäin, sitten alas), pää menosuuntaan
    const head = c.copy(fh).multiplyScalar(wv).addScaledVector(UP, 1 - wv); head.addScaledVector(v, -head.dot(v)).normalize(); const zx = v.clone().negate(), xx = new V3().crossVectors(head, zx).normalize();
    qa.setFromRotationMatrix(m4.makeBasis(xx, head, zx)); qb.setFromAxisAngle(UP, -J.yaw).multiply(new QT().setFromAxisAngle(new V3(0, 0, 1), -J.bank)).multiply(new QT().setFromAxisAngle(new V3(1, 0, 0), up < 1 ? -0.2 * Math.sin((J.D - 0.5) * 14) * (1 - J.D) * 2 * (J.D > 0.5 ? 1 : 0) : 0));
    qa.slerp(qb, up); J.q.slerp(qa, Math.min(1, dt * (J.ph === 'exit' ? 3 : 6)));
    // maa
    const gz = ground(J.pos.x, J.pos.z); J.agl = J.pos.y - PIV - gz;
    if (J.ph !== 'land' && J.agl <= 0 && relT >= 0) { J.ph = 'land'; J.t = 0; landGz = gz; J.hard = -J.vel.y; S.toggles = true; G.toast(J.hard < 1.6 ? '🪂 Pehmeä alastulo!' : J.hard < 3.6 ? '🪂 Alastulo' : '🪂 Kova alastulo – loppuveto (S) ajoissa!', 2.6); }
    if (J.ph === 'land') { w.Land = [1, Math.min(1.599, J.t)]; J.vel.multiplyScalar(Math.exp(-dt * 5)); J.vel.y = 0; J.pos.addScaledVector(J.vel, dt); J.pos.y = ground(J.pos.x, J.pos.z) + PIV; J.bank *= Math.exp(-dt * 4); J.q.slerp(qb.setFromAxisAngle(UP, -J.yaw), Math.min(1, dt * 8)); S.collapse = ease(J.t / 2.5); if (J.t > 0.7) S.toggles = false; }
    W.quaternion.copy(J.q); W.position.copy(J.pos).add(a.set(0, -PIV, 0).applyQuaternion(J.q)); }
  if (relT >= 0) relT += dt;
  J.att = attached; pose(w); W.visible = !(G.camMode === 1 && (J.ph === 'fall' || J.ph === 'pull')); rig.gear.visible = W.visible;
  rig.canopy.quaternion.setFromAxisAngle(UP, Math.PI - J.yaw).multiply(qb.setFromAxisAngle(a.set(0, 0, 1), J.bank * 0.9)); G.scene.updateMatrixWorld(true); rig.update(loopT);
  // muu peli seuraa hyppääjää
  const St = G.S; St.x = J.pos.x; St.y = -J.pos.z; St.yaw = J.yaw; St.alt = Math.max(0, J.agl) + 1.85; St.vx = J.vel.x; St.vy = -J.vel.z; St.vz = J.vel.y; St.landed = false; St.pitch = 0; St.roll = 0; if (G.world) G.world(St.x, St.y);
  const sp = J.vel.length(); windSound(attached ? 38 : J.ph === 'land' ? 0 : sp);
  const alt = Math.max(0, Math.round(J.agl)), hint = { door: 'Ovella', exit: 'Uloshyppy', fall: 'Väli tai Enter avaa varjon · A / D käännös · W liuku', pull: 'Apuvarjo ilmavirtaan', open: 'Kupu avautuu', fly: 'A / D ohjauslenkit · S tai Väli jarru ja loppuveto', land: 'Maassa' }[J.ph];
  hudSet(alt + ' m &nbsp;·&nbsp; ' + Math.round((J.ph === 'fly' ? Math.hypot(J.vel.x, J.vel.z) : sp) * 3.6) + ' km/h' + (J.ph === 'fly' ? ' &nbsp;·&nbsp; vajoaa ' + Math.max(0, -J.vel.y).toFixed(1) + ' m/s' : ''), hint);
  if (J.ph === 'land' && J.t > 3.4) finish(); };

function finish() { const G = gm(), W = G.walkG; let x = J.pos.x, y = -J.pos.z; J.on = false; hudSet(null); windSound(0); pose({}); mix.stopAllAction(); for (const n in act) { act[n].play(); act[n].setEffectiveWeight(0); }
  rig.state.pc = 'stowed'; rig.state.deploy = 0; rig.state.collapse = 0; rig.update(0); rig.wear(false); W.quaternion.identity();
  const roof = G.bldTopAt && G.bldTopAt(x, y) > G.TZs(x, y) + 1.2;      // katolle laskeutunut tuodaan lähimpään vapaaseen kohtaan kadulle
  if (roof || (G.carGround && G.carGround(x, y) === null)) { let best = null; for (let r = 3; r < 90 && !best; r += 3) for (let k = 0; k < 16; k++) { const px = x + Math.cos(k * 0.3927) * r, py = y + Math.sin(k * 0.3927) * r; if (G.carGround(px, py) !== null && !(G.bldTopAt(px, py) > G.TZs(px, py) + 0.7)) { best = [px, py]; break; } }
    if (best) { x = best[0]; y = best[1]; G.toast(roof ? 'Kiipesit katolta alas' : 'Kahlasit rantaan', 2); } }
  G.walkOutAt(x, y, J.yaw); if (G.setCam) G.setCam(0); }

J.cam = (dt, mode) => { const cam = gm().camera, P = window.__plane, d = ease(J.D); if (cam.near !== 0.3) { cam.near = 0.3; cam.updateProjectionMatrix(); } cam.up.set(0, 1, 0);
  const fh = a.set(Math.sin(J.yaw), 0, -Math.cos(J.yaw));
  if (mode === 2) { cam.position.set(J.pos.x, J.pos.y + 45, J.pos.z + 0.5); cam.lookAt(J.pos); return; }
  if (mode === 1 && (J.ph === 'fall' || J.ph === 'pull')) { cam.position.copy(J.pos).addScaledVector(UP, 0.3); const an = 1.05; cam.lookAt(b.copy(cam.position).addScaledVector(fh, Math.cos(an) * 10).addScaledVector(UP, -Math.sin(an) * 10)); camInit = false; return; }
  let wantP, wantL;
  if (J.ph === 'door' || (J.ph === 'exit' && relT < 0.5)) { const r = b.set(1, 0, 0).applyQuaternion(P.q), f = c.set(0, 0, -1).applyQuaternion(P.q); wantP = new V3().copy(J.pos).addScaledVector(r, 5.2).addScaledVector(f, 2.4).addScaledVector(UP, 1.3); wantL = new V3().copy(J.pos).addScaledVector(UP, 0.7); }      // koneen oikealla puolella, ovi näkyy
  else { const back = lerp(7.5, 15, d), hi = lerp(3.2, 4.5, d), v = b.copy(J.vel).normalize(), mixd = J.ph === 'fly' || J.ph === 'land' ? 0 : (1 - d) * 0.55;      // takana ja yläpuolella; vapaapudotuksessa hieman putoamissuunnan yläpuolella
    wantP = new V3().copy(J.pos).addScaledVector(fh, -back).addScaledVector(UP, hi).addScaledVector(v, -mixd * 4); wantL = new V3().copy(J.pos).addScaledVector(UP, lerp(0, 2.7, d)).addScaledVector(fh, lerp(2, 0, d)); }
  if (!camInit) { camP.copy(wantP); camL.copy(wantL); camInit = true; }
  camP.add(c.copy(J.att ? P.vel : J.vel).multiplyScalar(dt)); camL.add(c);      // kamera kulkee mukana (koneen tai hyppääjän nopeudella), vain suhteellinen paikka pehmennetään
  camP.lerp(wantP, 1 - Math.exp(-dt * 3.5)); camL.lerp(wantL, 1 - Math.exp(-dt * 6));
  const gz = ground(camP.x, camP.z); if (camP.y < gz + 0.8) camP.y = gz + 0.8; cam.position.copy(camP); cam.lookAt(camL); };
