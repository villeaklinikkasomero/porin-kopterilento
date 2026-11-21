// ---------- the player's car (owner 18.11.2026: drive the daily tour by car; porikopteri_auto.py, Blender) ----------
// Arcade bicycle model on the street surface: W/S throttle and brake/reverse, A/D steer, Space handbrake. Buildings and the river stop it.
let VEH = 'heli'; try { VEH = localStorage.getItem('pori-veh') === 'car' ? 'car' : 'heli'; } catch (e) {}
const CAR = { x: 0, y: 0, yaw: 0, v: 0, steer: 0, z: 0, pitch: 0, roll: 0, spin: 0 }, WB = 2.64, CAR_R = 0.325; window.__car = CAR;
const carG = new THREE.Group(); carG.rotation.order = 'YXZ'; carG.userData.noT = true; carG.visible = false; scene.add(carG);
let wheels = [], carLoading = {};
// 20.11.2026 (owner: "a van and an estate need proper models when the player drives one"): three drivable models - hatch (the player's own, auto.js),
// van (auto_van.js) and estate (auto_est.js; tools/vehicles/porikopteri_autot.py), each with its light _m version for touch devices. CARTY = file, half
// length and width of the collision box, acceleration and top speed, and the driver's eye shift [left, up, forward] from the hatch (steering wheel positions
// in the model reports). A borrowed parked car picks its model by type: hatch -> hatch, saloon and SUV -> estate, van -> van.
const CARM = {}, CARTY = { hatch: { f: 'auto', hl: 2.1, hw: 0.9, acc: 4.2, top: 24, cam: [0, 0, 0] }, van: { f: 'auto_van', hl: 2.4, hw: 0.97, acc: 3.3, top: 21, cam: [0.03, 0.3, 0.45] }, estate: { f: 'auto_est', hl: 2.3, hw: 0.91, acc: 4.0, top: 24, cam: [0, 0, 0.06] },
  bike: { f: 'pyora', one: true, hl: 0.85, hw: 0.28, acc: 2.2, top: 8.5, cam: [-0.37, 0.42, 0.3] },
  bus: { f: 'bussi', hl: 6.0, hw: 1.28, acc: 1.7, top: 16, cam: [0.38, 1.2, 5.1], wb: 5.9, r: 0.48 } };      // 20.11.2026 city bus (bussi.js / bussi_m.js): 12 m long, wheelbase 5.9 m, wheels r 0.48 m, about 58 km/h, driver high up at the front left      // a borrowed bicycle rides on the car physics: small box, 30 km/h, the rider is the walker model (Cycle clip), see TAKE
let carEnv = null;
const useCar = t => { const M = CARM[t], Y = CARTY[t]; if (!M) return false; CAR.type = t; CAR.hl = Y.hl; CAR.hw = Y.hw; CAR.acc = Y.acc; CAR.top = Y.top; CAR.cam = Y.cam; CAR.wb = Y.wb || WB; CAR.r = Y.r || CAR_R; wheels = M.wheels; CAR.setDmg = M.setDmg; CAR.dmg = -1; carG.clear(); carG.add(M.root); if (window.__take) window.__take.applied = null; return true; };
const setCarType = t => { CAR.want = t; if (!useCar(t)) loadCar(t); };
const loadCar = (t = CAR.want || 'hatch') => { if (CARM[t] || carLoading[t]) return; carLoading[t] = true; loadModel(CARTY[t].f + (isTouch && !CARTY[t].one ? '_m' : ''), root0 => {   // glTF: nose +z, wheels Wheel_FL/FR/RL/RR spinning about their local x, ground at y 0
  const root = new THREE.Group(); root.add(root0); root0.rotation.y = Math.PI;   // game frame: nose -z, like the helicopter
  const envS = new THREE.Scene(), eg = new THREE.SphereGeometry(50, 32, 16), ec = [];
  for (let i = 0; i < eg.attributes.position.count; i++) { const y = eg.attributes.position.getY(i) / 50; const c = y > 0 ? new THREE.Color(0xbfd3e6).lerp(new THREE.Color(0xffffff), Math.max(0, 1 - y * 2.5)) : new THREE.Color(0x77736c); ec.push(c.r, c.g, c.b); }
  eg.setAttribute('color', new THREE.Float32BufferAttribute(ec, 3)); envS.add(new THREE.Mesh(eg, new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.BackSide })));
  const sunB = new THREE.Mesh(new THREE.SphereGeometry(3, 12, 8), new THREE.MeshBasicMaterial({ color: new THREE.Color(8, 7.5, 6.5) })); sunB.position.set(30, 32, 24); envS.add(sunB);
  const envTex = carEnv || (carEnv = new THREE.PMREMGenerator(renderer).fromScene(envS, 0.02).texture);
  root0.traverse(q => { if (q.isMesh) { const m = q.material; if (m && m.isMeshStandardMaterial) { m.envMap = envTex; m.envMapIntensity = 1.0; m.needsUpdate = true; } q.frustumCulled = false; } });
  const wh = ['Wheel_FL', 'Wheel_FR', 'Wheel_RL', 'Wheel_RR', 'Wheel_F', 'Wheel_R'].map(n => root0.getObjectByName(n)).filter(Boolean);
  for (const w of wh) { w.rotation.order = 'YXZ'; w.userData.front = /F[LR]$/.test(w.name); }
  // damage steps (20.11.2026, model: tools/vehicles/porikopteri_auto.py): parts named Part_d0..d3 share origin and pose; of each part the highest step that is
  // not above the car's step is shown, the others hidden. Step 3 also hides the front plate text (the plate goes with the hanging bumper).
  { const parts = {}; root0.traverse(q => { const m = /^(.+)_d([0-3])$/.exec(q.name || ''); if (m) (parts[m[1]] || (parts[m[1]] = []))[+m[2]] = q; }); const plate = root0.getObjectByName('PlateText_front');
    const setDmg = st => { CAR.dmg = st; for (const k in parts) { let best = -1; for (let i = 0; i <= st; i++) if (parts[k][i]) best = i; parts[k].forEach((q, i) => { if (q) q.visible = i === best; }); } if (plate) plate.visible = st < 3; }; setDmg(0);
    CARM[t] = { root, wheels: wh, setDmg }; }
  if ((CAR.want || 'hatch') === t) useCar(t);
}); };   // loaded only when the car is chosen
