// ---------- on foot (owner 19.11.2026): Enter steps out of the parked car or the landed helicopter; the player walks the streets and
// goes into Keski-Porin kirkko through the tower door. The tour clock stops while on foot. Character: hahmo.js (Blender, MakeHuman base, CC0)
// with Idle / Walk / Run clips. The church hall is its own scene (kirkko_sisa.js: blender/kirkko_sisa.py, light baked into a lightmap), drawn
// in the model's local frame: x along the nave towards the altar, y across (left of the altar-facing visitor), floor at 0.
const WALK = { on: false, x: 0, y: 0, z: 0, yaw: 0, v: 0, vs: 0, in: false, ix: 0, iy: 0, iyaw: 0, veh: null, busy: false }; window.__walk = WALK;
const walkG = new THREE.Group(); walkG.userData.noT = true; walkG.visible = false; scene.add(walkG);
const sceneIn = new THREE.Scene(); sceneIn.background = new THREE.Color(0x0b0a09);
sceneIn.add(new THREE.HemisphereLight(0xfff0dc, 0x8a7458, 2.3)); { const d = new THREE.DirectionalLight(0xfff2e0, 0.8); d.position.set(-0.4, 1, 0.3); sceneIn.add(d); }   // only the player is lit; the hall is baked
const blobIn = new THREE.Mesh(new THREE.CircleGeometry(0.42, 20).rotateX(-Math.PI / 2), new THREE.MeshBasicMaterial({ map: blob.material.map, transparent: true, depthWrite: false, opacity: 0.8 })); blobIn.renderOrder = 5; sceneIn.add(blobIn);
// interiors (owner 19.11.2026: the church first, then Juseliuksen mausoleumi): each place is a group in sceneIn drawn in its own local frame.
// map(x, y): local -> map metres; probe: a local point just inside the outer door and the outward direction (the first free spot becomes the door)
const MAUS = { cx: -1947.81, cy: 193.18, ex: [-0.9703, 0.2419], ey: [-0.2419, -0.9703] };   // bl_mausoleumi.js: hall centre, local x runs from the east door inwards (166 deg)
const TEAT = { cx: -199.62, cy: 374.34, ex: [-0.2236, -0.9747], ey: [0.9747, -0.2236] };   // Porin Teatteri (blender/teatteri_sisa.py): origin on the hall's rear wall, 11.5 m in from the middle of the Hallituskatu front; x runs towards the stage. The upstairs café is modelled 100 m further along x and folded back for the map
const AREE = { cx: -1611.69, cy: -1365.72, ex: [-0.4384, -0.8988], ey: [0.8988, -0.4384] };   // Porin jäähalli (blender/areena_sisa.py): origin at the main doors on the north long side (Karhuhalli side), x across the rink to the south
const KAUH = { cx: 177.01, cy: -43.68, ex: [-0.9839, 0.1788], ey: [-0.1788, -0.9839] };   // Porin kauppahalli (blender/kauppahalli_sisa.py): origin in the middle of the Isolinnankatu (east) end, x along the hall to the west (the Yrjönkatu end adjoins the neighbouring house, so the game's door is on Isolinnankatu)
const TAIM = { cx: -96.85, cy: 467.4, ex: [-0.2267, -0.9740], ey: [0.9740, -0.2267] };   // Porin taidemuseo (blender/taidemuseo_sisa.py): origin in the middle of the recessed river front, x into the hall
const lin2 = T => (x, y) => [T.cx + T.ex[0] * x + T.ey[0] * y, T.cy + T.ex[1] * x + T.ey[1] * y];
const PLACES = [
  { key: 'kirkko', file: 'kirkko_sisa', name: 'Keski-Porin kirkko', room: 'kirkkosali', label: '⛪ Sisään kirkkoon', hint: 'astu Keski-Porin kirkkoon', ok: () => !!CHURCH.map, map: (x, y) => CHURCH.map(x, -y), probe: [-34, 0, -1, 0], markH: 8.2 },
  { key: 'mausoleumi', file: 'mausoleumi_sisa', name: 'Juseliuksen mausoleumi', room: 'halli ja krypta', label: '🕯 Sisään mausoleumiin', hint: 'astu Juseliuksen mausoleumiin', ok: () => true, map: (x, y) => [MAUS.cx + MAUS.ex[0] * x + MAUS.ey[0] * y, MAUS.cy + MAUS.ex[1] * x + MAUS.ey[1] * y], probe: [-5.0, 0, -1, 0], markH: 5.2 },
  { key: 'teatteri', file: 'teatteri_sisa', name: 'Porin Teatteri', room: 'aula, päänäyttämö ja kahvila', label: '🎭 Sisään teatteriin', hint: 'astu Porin Teatteriin', ok: () => true, map: (x, y) => { if (x > 50) x -= 100; return [TEAT.cx + TEAT.ex[0] * x + TEAT.ey[0] * y, TEAT.cy + TEAT.ex[1] * x + TEAT.ey[1] * y]; }, probe: [-15.8, 0, -1, 0], markH: 6 },
  { key: 'taidemuseo', file: 'taidemuseo_sisa', name: 'Porin taidemuseo', room: 'Halli', label: '🖼 Sisään taidemuseoon', hint: 'astu Porin taidemuseoon', ok: () => true, map: lin2(TAIM), probe: [-3.0, 0, -1, 0], markH: 5 },
  { key: 'areena', file: 'areena_sisa', name: 'Porin jäähalli', room: 'kaukalo ja katsomot', label: '🏒 Sisään jäähalliin', hint: 'astu Porin jäähalliin', ok: () => true, map: lin2(AREE), probe: [-6.1, 0, -1, 0], markH: 9 },
  { key: 'kauppahalli', file: 'kauppahalli_sisa', name: 'Porin kauppahalli', room: 'halli', label: '🍽 Sisään kauppahalliin', hint: 'astu Porin kauppahalliin', ok: () => true, map: lin2(KAUH), probe: [-4.3, 0, -1, 0], markH: 6 } ];
const IN = PLACES[0];
let walkMix = null, walkCur = '', walkLoading = false; const walkAct = {};
function loadWalker() { if (walkLoading) return; walkLoading = true;
  import('./hahmo.js').then(K => { const bin = atob(K.default), buf = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
    new GLTFLoader().parse(buf.buffer, '', gl => { const root = gl.scene; root.rotation.y = Math.PI;   // glTF faces +z, the game frame -z
      root.traverse(q => { q.userData.noT = true; if (q.isMesh) { q.frustumCulled = false; q.material.userData.noT = true; if (q.material.map) q.material.map.anisotropy = 4; } });
      walkG.add(root); walkMix = new THREE.AnimationMixer(root); for (const c of gl.animations) walkAct[c.name] = walkMix.clipAction(c);
      if (walkAct.Idle) { walkAct.Idle.play(); walkCur = 'Idle'; } window.__walker = root; window.__walkerClips = gl.animations;      /* the parachute jump (laskuvarjo/hyppy.js) plays its own clips on the same model */ }, () => {}); }).catch(() => { walkLoading = false; }); }
function loadInterior(P) { if (P.loading) return; P.loading = true;
  import(`./${P.file}.js`).then(K => { const bin = atob(K.default), buf = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
    const lm = new THREE.TextureLoader().load(K.lm); lm.flipY = false; lm.colorSpace = THREE.SRGBColorSpace; lm.channel = 1;
    new GLTFLoader().parse(buf.buffer, '', gl => {
      gl.scene.traverse(q => { if (!q.isMesh) return; const map = q.material.map, glow = /^glow_/.test(q.material.name); if (map) map.anisotropy = 8;
        q.material = new THREE.MeshBasicMaterial({ map, side: THREE.DoubleSide }); if (!glow) { q.material.lightMap = lm; q.material.lightMapIntensity = Math.PI * K.meta.lmax; } });
      gl.scene.visible = false; sceneIn.add(gl.scene); P.group = gl.scene; P.meta = K.meta; P.ready = true; }, () => {}); }).catch(() => { P.loading = false; }); }
// a place's outer door in map metres, and the heading out of it
const placeDoor = P => { if (!P.ok()) return null;
  if (!P.door) { const [sx, sy, dx, dy] = P.probe, b = P.map(sx - dx * 4, sy - dy * 4); let a = P.map(sx, sy);
    for (let t = 0; t < 9; t += 0.3) { a = P.map(sx + dx * t, sy + dy * t); if (walkFree(a[0], a[1])) { a = P.map(sx + dx * (t + 0.5), sy + dy * (t + 0.5)); break; } }   // first free spot in front of the door
    P.door = { x: a[0], y: a[1], out: Math.atan2(a[0] - b[0], a[1] - b[1]) }; } return P.door; };
const churchDoor = () => placeDoor(PLACES[0]);
// 21.11.2026: Porttaalin seinät ja maasiltojen kaiteet kiinteitä myös jalan (rata/rata.js __rataSeina, js/0301 __siltaKaide): askel syvemmälle estetään
function wallIn(x, y) { const z = WALK.z;
  for (const F of [window.__rataSeina, window.__siltaKaide, window.__alikSeina]) if (F && F(x, y, z) > F(WALK.x, WALK.y, z) + 1e-4) return true; return false; }
// 21.11.2026 (omistaja: "kävellessä pelaaja hyppää sillalle" (-714, -691)): jyrkkää (yli ~33°) penkkaa tai korkeaa reunaa ei kävellä ylös (Luvianpuistokadun
// 2 m pyörätiepenger, radan penkka sillalle). Katsotaan 0,8 m eteenpäin: portaat (Etelärannassa enintään 0,4 m / 0,8 m) ja reunakivet menevät.
function walkSteep(x, y) { const dx = x - WALK.x, dy = y - WALK.y, d = Math.hypot(dx, dy); if (d < 1e-6) return false;
  const ax = WALK.x + dx / d * 0.8, ay = WALK.y + dy / d * 0.8, g = carGround(ax, ay);
  return g !== null && g - WALK.z > 0.52; }
function walkFree(x, y) {
  const g = carGround(x, y); if (g === null) return false; const tb = Math.max(TZs(x, y), TZg(x, y));
  if (onPorinsilta(x, y) !== null) return true;
  for (const [dx, dy] of [[0.3, 0], [-0.3, 0], [0, 0.3], [0, -0.3]]) if (bldTopAt(x + dx, y + dy) > tb + 0.7) return false;
  return true;
}
function walkExit() {
  if (VEH === 'car' ? Math.abs(CAR.v) > 1.5 : !S.landed) { toast(VEH === 'car' ? 'Pysäytä auto ensin' : 'Laskeudu ensin maahan', 1.6); return; }
  if (VEH !== 'car' && bldTopAt(S.x, S.y) > TZs(S.x, S.y) + 1.5) { toast('Katolta ei pääse kävellen alas – laskeudu maahan', 2); return; }
  const sn = Math.sin(S.yaw), cs = Math.cos(S.yaw), w = VEH === 'car' ? (CAR.hw || 0.9) + 0.65 : 2.3; let spot = null;
  for (const [f, r] of (CAR.type === 'bus' && VEH === 'car' ? [[4.4, w], [4.4, -w], [0, w], [0, -w], [-3, w]] : [[0.2, -w], [0.2, w], [-1.2, -w], [-1.2, w], [-3.6, 0], [3.6, 0], [1.5, -w - 1], [1.5, w + 1]])) { const x = S.x + sn * f + cs * r, y = S.y + cs * f - sn * r; if (walkFree(x, y)) { spot = [x, y]; break; } }
  if (!spot) { toast('Tässä ei mahdu nousemaan ulos', 1.6); return; }
  if (VEH === 'car') CAR.v = 0;
  Object.assign(WALK, { on: true, in: false, x: spot[0], y: spot[1], z: carGround(spot[0], spot[1]), yaw: S.yaw, v: 0, vs: 0, veh: { x: S.x, y: S.y, alt: S.alt, yaw: S.yaw } });
  document.body.classList.add('walk'); scene.add(walkG); walkG.visible = true; loadWalker(); RADIO.mute();
  camera.near = 0.25; camera.updateProjectionMatrix(); if (camMode === 2) camMode = 0;
  toast('Jalan – Enter vie takaisin kyytiin', 2.2);
}
function walkBoard() {
  const v = WALK.veh; WALK.on = false; WALK.in = false; walkG.visible = false; document.body.classList.remove('walk'); $('hint').classList.remove('on');
  if (v) Object.assign(S, { x: v.x, y: v.y, alt: v.alt, yaw: v.yaw, vx: 0, vy: 0, vz: 0, landed: true });
  camera.near = 1; camera.updateProjectionMatrix(); RADIO.mute(); blob.rotation.y = 0; blob.scale.setScalar(1);
}
function walkReset() { if (WALK.on) { scene.add(walkG); walkBoard(); } }
function fadeDo(fn) { if (WALK.busy) return; WALK.busy = true; $('fade').classList.add('on'); setTimeout(() => { fn(); $('fade').classList.remove('on'); WALK.busy = false; }, 240); }
function walkNear() {   // what Enter would do here: 'in' (church door), 'out' (leave the church), 'veh' (board), or ''
  if (WALK.in) { const M = WALK.in.meta; if (WALK.ix < M.exit[0] + 1.6 && Math.abs(WALK.iy) < M.exit[1] + 0.6) return 'out';
    if (M.ports) for (const q of M.ports) if (Math.hypot(WALK.ix - q[0], WALK.iy - q[1]) < q[2]) { WALK.port = q; return 'port'; }   // inner doors that move the player (theatre: foyer <-> upstairs café): [x, y, r, to x, to y, yaw, hint]
    return ''; }
  for (const P of PLACES) { const d = placeDoor(P); if (d && Math.hypot(WALK.x - d.x, WALK.y - d.y) < 4.2) { WALK.at = P; return 'in'; } }
  if (window.__bus) { const b = window.__bus.rideNear(WALK.x, WALK.y); if (b) return b; }      // 'bus' (a live bus standing here, it will not wait) or 'busout' (riding one)
  const v = WALK.veh; if (v && !(window.__heliLukko && VEH !== 'car') && Math.hypot(WALK.x - v.x, WALK.y - v.y) < (VEH === 'car' ? (CAR.type === 'bus' ? 7.5 : 4.2) : 6)) return 'veh';   /* story lock: no boarding the helicopter */
  if (window.__plane && window.__plane.near(WALK.x, WALK.y)) return 'plane';      // the jump plane on the apron
  return takeNear();      // 'heli' (the helicopter left behind), 'take' (a parked car to borrow) or ''
}
function walkAction() {
  if (!started || S.dead > 0 || WALK.busy) return;
  if (window.__jump && window.__jump.on) { window.__jump.action(); return; }      // parachute jump: Enter / the action button opens the parachute
  if (window.__plane && window.__plane.on) { window.__plane.exitReq(); return; }
  if (!WALK.on) { walkExit(); return; }
  const k = walkNear();
  if (k === 'veh') walkBoard();
  else if (k === 'in') { const P = WALK.at; if (!P.ready) { loadInterior(P); toast(P.name + ' latautuu…', 1.5); return; }
    fadeDo(() => { const M = P.meta; for (const Q of PLACES) if (Q.group) Q.group.visible = Q === P; WALK.in = P; WALK.ix = M.spawn[0]; WALK.iy = M.spawn[1]; WALK.iyaw = Math.PI / 2; WALK.z = 0; WALK.v = 0; sceneIn.add(walkG);
      camPos.set(WALK.ix - 1, 2, 0); camLook.set(WALK.ix + 3, 1.5, 0); camera.near = 0.12; camera.updateProjectionMatrix(); toast(P.name, 2.2); }); }
  else if (k === 'out') fadeDo(() => { const d = placeDoor(WALK.in); WALK.in = false; WALK.x = d.x; WALK.y = d.y; WALK.yaw = d.out; WALK.v = 0; WALK.z = carGround(d.x, d.y) || 0; scene.add(walkG);
      camPos.set(WALK.x - Math.sin(d.out) * 3, WALK.z + 2, -WALK.y + Math.cos(d.out) * 3); camera.near = 0.25; camera.updateProjectionMatrix(); });
  else if (k === 'port') fadeDo(() => { const q = WALK.port; WALK.ix = q[3]; WALK.iy = q[4]; WALK.iyaw = q[5]; WALK.v = 0; WALK.z = inFloor(q[3], q[4]); camPos.set(q[3] - Math.sin(q[5]) * 1.5, WALK.z + 2, -(q[4] - Math.cos(q[5]) * 1.5)); });
  else if (k === 'take' || k === 'heli') takeDo(k);
  else if (k === 'plane') fadeDo(() => { WALK.on = false; walkG.visible = false; document.body.classList.remove('walk'); $('hint').classList.remove('on'); RADIO.mute(); window.__plane.enter(); });
  else if (k === 'bus') window.__bus.ride();
  else if (k === 'busout') window.__bus.out();
  else toast(VEH === 'car' ? 'Auto on liian kaukana' : 'Kopteri on liian kaukana', 1.4);
}
function walkCollide(p) {   // push the player's circle out of the hall's walls, columns, pews and rails
  const C = WALK.in.meta.col, R = 0.32;
  for (let it = 0; it < 2; it++) {
    for (const g of C.seg) { const dx = g[2] - g[0], dy = g[3] - g[1], t = Math.max(0, Math.min(1, ((p.x - g[0]) * dx + (p.y - g[1]) * dy) / (dx * dx + dy * dy || 1)));
      let ex = p.x - g[0] - dx * t, ey = p.y - g[1] - dy * t; const d = Math.hypot(ex, ey), m = R + g[4]; if (d < m && d > 1e-6) { p.x += ex / d * (m - d); p.y += ey / d * (m - d); } }
    for (const c of C.circ) { const ex = p.x - c[0], ey = p.y - c[1], d = Math.hypot(ex, ey), m = R + c[2]; if (d < m && d > 1e-6) { p.x += ex / d * (m - d); p.y += ey / d * (m - d); } }
  }
}
const inRoom = (M, x, y) => M.rooms ? M.rooms.some(r => pip(x, y, r)) : pip(x, y, M.room);
const inFloor = (x, y) => { const M = WALK.in.meta; if (M.lev) { let z = 0; for (const r of M.lev) if (x >= r[0] && x <= r[2] && y >= r[1] && y <= r[3] && r[4] > z) z = r[4]; return z; }   // floor levels as rectangles [x0, y0, x1, y1, z] (theatre stage and its steps)
  return Math.abs(y) < M.py && x > M.xs0 - 0.15 ? Math.min(M.flz, 0.15 * (Math.floor((x - M.xs0 + 0.15) / 0.4) + 1)) : 0; };
function stepWalk(dt) {
  const run = keys.has('ShiftLeft') || keys.has('ShiftRight') || touchIn.run, f = input.f, t = input.t, sd = input.s;
  const tv = f > 0 ? f * (run ? 5.4 : 1.75) : f * 1.2; WALK.v += (tv - WALK.v) * Math.min(1, dt * 9); WALK.vs += (sd * 1.3 - WALK.vs) * Math.min(1, dt * 9);
  const tr = t * (run && f > 0 ? 2.0 : 2.5) * dt, moving = Math.abs(WALK.v) > 0.05 || Math.abs(WALK.vs) > 0.05;
  if (WALK.in) {
    WALK.iyaw += tr; const sn = Math.sin(WALK.iyaw), cs = Math.cos(WALK.iyaw), p = { x: WALK.ix + (sn * WALK.v + cs * WALK.vs) * dt, y: WALK.iy + (cs * WALK.v - sn * WALK.vs) * dt };
    const ox = WALK.ix, oy = WALK.iy; walkCollide(p);
    if (inFloor(p.x, p.y) - WALK.z > 0.25) { p.x = ox; p.y = oy; }                        // no climbing the side of the chancel platform
    if (!inRoom(WALK.in.meta, p.x, p.y)) { p.x = ox; p.y = oy; }
    WALK.ix = p.x; WALK.iy = p.y; WALK.z += (inFloor(p.x, p.y) - WALK.z) * Math.min(1, dt * 12);
    walkG.position.set(WALK.ix, WALK.z, -WALK.iy); walkG.rotation.y = -WALK.iyaw; blobIn.position.set(WALK.ix, WALK.z + 0.02, -WALK.iy);
    const m0 = WALK.in.map(WALK.ix, WALK.iy), m1 = WALK.in.map(WALK.ix + sn, WALK.iy + cs); S.x = WALK.x = m0[0]; S.y = WALK.y = m0[1]; S.yaw = WALK.yaw = Math.atan2(m1[0] - m0[0], m1[1] - m0[1]);
  } else {
    WALK.yaw += tr; const sn = Math.sin(WALK.yaw), cs = Math.cos(WALK.yaw), dx = (sn * WALK.v + cs * WALK.vs) * dt, dy = (cs * WALK.v - sn * WALK.vs) * dt;
    const ride = window.__aboard && window.__aboard(), wf = (x, y) => ride ? !window.__walkBlock(x, y) : walkFree(x, y) && !walkSteep(x, y) && !SOLID.walkHit(WALK.x, WALK.y, x, y) && !(window.__walkBlock && window.__walkBlock(x, y)) && !wallIn(x, y);      // houses, and (20.11.2026) cars and people; 21.11.2026: junassa vain vaunun seinät ja penkit (juna/juna.js)
    if (moving) { if (wf(WALK.x + dx, WALK.y + dy)) { WALK.x += dx; WALK.y += dy; } else if (wf(WALK.x + dx, WALK.y)) WALK.x += dx; else if (wf(WALK.x, WALK.y + dy)) WALK.y += dy; else WALK.v *= 0.5; }
    if (!ride) { const q = SOLID.pushOut(WALK.x, WALK.y); if (q && walkFree(q[0], q[1])) { const k = Math.min(1, dt * 10); WALK.x += (q[0] - WALK.x) * k; WALK.y += (q[1] - WALK.y) * k; } }      // a car drove onto the player: step out beside it
    WALK.x = Math.max(OX0 - 100, Math.min(OX1 + 100, WALK.x)); WALK.y = Math.max(OY0 - 100, Math.min(OY1 + 100, WALK.y));
    const g = carGround(WALK.x, WALK.y); if (g !== null) WALK.z += (g - WALK.z) * Math.min(1, dt * 14);
    walkG.position.set(WALK.x, WALK.z, -WALK.y); walkG.rotation.y = -WALK.yaw;
    blob.position.set(WALK.x, WALK.z + 0.04, -WALK.y); blob.scale.set(0.075, 1, 0.075); blob.material.opacity = 0.8;
    S.x = WALK.x; S.y = WALK.y; S.yaw = WALK.yaw;
    if (performance.now() - HR.last > 500) { HR.last = performance.now(); hrUpdate(S.x, S.y); TEXLOD.update(S.x, S.y); streamUpdate(S.x, S.y); TREES.update(S.x, S.y); GRASS.update(); }
    GRASS.tick(performance.now() / 1000);
    for (const P of PLACES) { const d = placeDoor(P); if (!d) continue; if (!P.loading && Math.hypot(WALK.x - d.x, WALK.y - d.y) < 90) loadInterior(P);
      if (!P.mark) { const t = textCanvas(P.label, { size: 40, color: '#16110a', bg: 'rgba(255,201,40,.95)', pad: 18 }); P.mark = new THREE.Sprite(new THREE.SpriteMaterial({ map: t.tex, transparent: true, depthWrite: false, fog: false }));
        P.mark.scale.set(1.5 * t.aspect, 1.5, 1); P.mark.renderOrder = 3; P.mark.position.set(d.x, (carGround(d.x, d.y) || TZs(d.x, d.y)) + P.markH, -d.y); scene.add(P.mark); } }
  }
  S.alt = WALK.z + SKID; S.vx = Math.sin(S.yaw) * WALK.v; S.vy = Math.cos(S.yaw) * WALK.v; S.vz = 0;
  if (walkMix) { const sp = Math.max(Math.abs(WALK.v), Math.abs(WALK.vs)), want = sp < 0.15 ? (DANCE.on && walkAct.Dance ? 'Dance' : 'Idle') : sp < 2.8 ? 'Walk' : 'Run';
    if (want !== walkCur && walkAct[want]) { const a = walkAct[want], b = walkAct[walkCur]; a.reset().play(); if (b) a.crossFadeFrom(b, 0.22, false); walkCur = want; }
    DANCE.tick(); if (walkCur === 'Dance') DANCE.sync(walkAct.Dance, 0); else if (walkAct[walkCur]) walkAct[walkCur].timeScale = walkCur === 'Walk' ? Math.max(0.5, sp / 1.36) * (WALK.v < -0.05 ? -1 : 1) : walkCur === 'Run' ? sp / 4.65 : 1;   // clip strides (tools/hahmo/porikopteri_hahmo.py WALK/RUN): 1.36 m in 1 s, 3.10 m in 0.667 s -> the planted foot does not slide
    walkMix.update(dt); }
  walkG.visible = camMode !== 1;
  if (VEH !== 'car') { S.rotorSpd += (0 - S.rotorSpd) * Math.min(1, dt * 0.6); rotor.rotation.y -= S.rotorSpd * 38 * dt; tailRotor.rotation.x += S.rotorSpd * 55 * dt; }
  if (actx && sGain) sGain.gain.value += ((VEH !== 'car' && soundOn && !WALK.in ? 0.05 * S.rotorSpd : 0) - sGain.gain.value) * Math.min(1, dt * 4);
  const k = walkNear(), h = $('hint'), msg = k === 'in' ? WALK.at.hint : k === 'out' ? 'ulos' : k === 'port' ? WALK.port[6] : k === 'veh' ? (VEH === 'car' ? (CAR.type === 'bike' ? 'nouse pyörälle' : CAR.type === 'bus' ? 'nouse bussiin' : 'nouse autoon') : 'nouse kopteriin') : k === 'plane' ? 'nouse hyppykoneeseen' : k === 'heli' ? 'nouse kopteriin' : k === 'take' ? (TAKE.tgt && TAKE.tgt.bp ? 'aja bussia (linja ' + TAKE.tgt.bp.dep.line + ')' : TAKE.tgt && (TAKE.tgt.b || TAKE.tgt.l && TAKE.tgt.l.type === 'bike') ? 'ota pyörä' : 'ota auto') : (k === 'bus' || k === 'busout') ? window.__bus.hint(k) : '';
  if (msg) { if (h.dataset.m !== msg) { h.dataset.m = msg; h.innerHTML = (isTouch ? (window.ikoni ? window.ikoni('kavely') + ' ' : '') : '<kbd>Enter</kbd> ') + msg; } h.classList.add('on'); } else h.classList.remove('on');
}
function walkCamera(dt) {
  const ins = WALK.in, px = ins ? WALK.ix : WALK.x, py = ins ? WALK.iy : WALK.y, yaw = ins ? WALK.iyaw : WALK.yaw, sn = Math.sin(yaw), cs = Math.cos(yaw);
  if (camMode === 1) { camera.position.set(px + sn * 0.1, WALK.z + 1.68, -(py + cs * 0.1)); camera.rotation.order = 'YXZ'; camera.rotation.set(-0.02, -yaw, 0); camPos.copy(camera.position); return; }
  if (camMode === 2 && !ins) { tmp.set(px, WALK.z + 38, -py + 0.5); camPos.lerp(tmp, Math.min(1, dt * 4)); camera.position.copy(camPos); camera.up.set(sn, 0, -cs); camera.lookAt(px, WALK.z, -py); camera.up.set(0, 1, 0); return; }
  let ok = 0.5;
  if (ins && ins.meta.rooms) { const M = ins.meta;   // rooms with inner walls: the camera backs away only as far as nothing stands between it and the player
    for (let b = 0.7; b < 3.65; b += 0.29) { const cx = px - sn * b, cy = py - cs * b;
      if (!inRoom(M, cx, cy) || M.col.circ.some(c => Math.hypot(cx - c[0], cy - c[1]) < c[2] + 0.25) || M.col.seg.some(g => { const dx = g[2] - g[0], dy = g[3] - g[1], t = Math.max(0, Math.min(1, ((cx - g[0]) * dx + (cy - g[1]) * dy) / (dx * dx + dy * dy || 1))); return Math.hypot(cx - g[0] - dx * t, cy - g[1] - dy * t) < g[4] + 0.22; })) break; ok = b; } }
  else for (const back of [3.6, 2.7, 1.9, 1.2, 0.7]) { const cx = px - sn * back, cy = py - cs * back;
    const free = ins ? pip(cx, cy, WALK.in.meta.room) && !WALK.in.meta.col.circ.some(c => Math.hypot(cx - c[0], cy - c[1]) < c[2] + 0.25) && cx > WALK.in.meta.xw + 0.3 : walkFree(cx, cy);
    if (free) { ok = back; break; } }
  tmp.set(px - sn * ok, WALK.z + 1.55 + ok * 0.17, -(py - cs * ok)); camPos.lerp(tmp, 1 - Math.exp(-dt * 8));
  tmp2.set(px + sn * 3, WALK.z + 1.45, -(py + cs * 3)); camLook.lerp(tmp2, 1 - Math.exp(-dt * 10));
  camera.position.copy(camPos); camera.lookAt(camLook);
}

