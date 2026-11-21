// moduulit/kavelijat.js – siirretty pääskriptistä (src/js/140_kavelijat.js) omaksi moduulikseen 21.11.2026.
// Pääskriptin muuttujat tulevat oliossa _P (getterit pitävät ne ajan tasalla); kirjastot ja data tuodaan suoraan.
// Kutsu ja _P:n sisältö: src/js/140_kavelijat.js. Uusi riippuvuus pääskriptiin → lisää se sinne _P-olioon.
import * as THREE from '../three.module.min.js';
import { GLTFLoader } from '../GLTFLoader.js';

// ---------- people on foot (19.11.2026): six models npc_*.js (Idle / Walk), walking only the footway network walk.js (tools/roads/build_walk.py) ----------
// Parties are spawned around the player and dropped when far. Owner's rules: a child (tytto, poika) always walks with at least one of mies_a,
// nainen_a, nainen_b; other adults walk alone or in pairs; mies_b is rare. At a signalled crossing they wait for the green man (window.__sig.ped).
export default function kaynnista(_P) {
{
  const STRIDE = { nainen_a: 1.213, nainen_b: 1.173, mies_a: 1.344, mies_b: 1.414, tytto: 0.926, poika: 1.006 };   // metres per Walk cycle of each model (printed by tools/hahmo/kavely_glb.py): the planted foot does not slide
  const KIND = ['nainen_a', 'nainen_b', 'mies_a', 'mies_b', 'tytto', 'poika'], MOD = {}, NMAX = matchMedia('(pointer: coarse)').matches ? 18 : 46, parties = [];
  let net = null, busy = [], busyE = [], sd = 4711; const rnd = () => (sd = (sd * 16807) % 2147483647) / 2147483647;
  const pickW = (ks, ws) => { let r = rnd() * ws.reduce((a, b) => a + b, 0); for (let i = 0; i < ks.length; i++) if ((r -= ws[i]) <= 0) return ks[i]; return ks[0]; };
  const adult = () => pickW(['nainen_a', 'nainen_b', 'mies_a', 'mies_b'], [0.31, 0.31, 0.31, 0.07]), guard = () => pickW(['nainen_a', 'nainen_b', 'mies_a'], [1, 1, 1]), child = () => rnd() < 0.5 ? 'tytto' : 'poika';
  const cloneSk = src => { const map = new Map(), c = src.clone(); const wk = (a, b) => { map.set(a, b); for (let i = 0; i < a.children.length; i++) wk(a.children[i], b.children[i]); }; wk(src, c);
    src.traverse(o => { if (o.isSkinnedMesh) { const d = map.get(o); d.skeleton = new THREE.Skeleton(o.skeleton.bones.map(b => map.get(b)), o.skeleton.boneInverses); d.bind(d.skeleton, o.bindMatrix); } }); return c; };
  import('../walk.js').then(K => { const n = K.default.n, e = K.default.e, N = [];
    for (let i = 0; i < n.length; i += 2) N.push({ x: n[i] / 10, y: n[i + 1] / 10, nb: [] });
    for (const i of K.default.b || []) N[i].busy = true;                          // pedestrian streets and Kauppatori: Yrjönkatu is the liveliest street in Pori (owner)
    for (const i of K.default.g || []) { N[i].grid = true; if (_P.bldTopAt(N[i].x, N[i].y) > _P.TZs(N[i].x, N[i].y) + 1.5) N[i].dead = true; }   // square grid nodes inside the market pavilion
    for (let i = 0; i < e.length; i += 3) { const a = N[e[i]], b = N[e[i + 1]], ok = p => p.x > _P.OX0 + 8 && p.x < _P.OX1 - 8 && p.y > _P.OY0 + 8 && p.y < _P.OY1 - 8; if (!ok(a) || !ok(b) || a.dead || b.dead) continue;
      a.nb.push({ n: b, c: e[i + 2] }); b.nb.push({ n: a, c: e[i + 2] }); }
    net = N.filter(p => p.nb.length); busy = net.filter(p => p.busy);
    for (const a of busy) if (!a.grid) for (const e of a.nb) if (e.n.busy && !e.n.grid) busyE.push({ a, e, w: Math.hypot(e.n.x - a.x, e.n.y - a.y) }); }).catch(() => {});
  KIND.forEach(k => import(`../npc_${k}.js`).then(K => { const bin = atob(K.default), buf = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
    new GLTFLoader().parse(buf.buffer, '', gl => { gl.scene.rotation.y = Math.PI; gl.scene.traverse(q => { q.userData.noT = true; if (q.isMesh) { q.frustumCulled = false; q.material.userData.noT = true; } }); MOD[k] = gl; }, () => {}); }).catch(() => {}));
  // every walker gets own tints for shirt, trousers, shoes and hair (owner 19.11: "aika homogeenistä porukkaa"): the part's material is cloned and its
  // colour multiplied (the texture stays); mies_b keeps his hair.
  const TINT = { TShirt: [[1, 1, 1], [1, 1, 1], [1, 0.82, 0.62], [0.5, 0.5, 0.56], [0.72, 1, 0.74], [1, 0.62, 0.6], [1, 0.95, 0.6], [0.7, 0.85, 1], [0.95, 0.7, 1], [0.32, 0.34, 0.4]],
    Jeans: [[1, 1, 1], [1, 1, 1], [0.5, 0.5, 0.56], [0.95, 0.8, 0.62], [0.75, 0.78, 0.8], [0.35, 0.36, 0.4], [0.8, 1, 0.85]], Shoe: [[1, 1, 1], [0.3, 0.3, 0.32], [0.9, 0.3, 0.25], [0.5, 0.35, 0.25]],
    Hair: [[1, 1, 1], [1, 1, 1], [0.62, 0.46, 0.32], [0.3, 0.24, 0.2], [0.95, 0.55, 0.32], [0.82, 0.82, 0.86], [0.5, 0.4, 0.3]] };
  const tintChar = (root, k) => { const pick = {}, mats = []; for (const part in TINT) pick[part] = TINT[part][Math.floor(rnd() * TINT[part].length)];
    root.traverse(o => { if (!o.isMesh || !o.material || !o.material.name) return; const n = o.material.name, part = n.startsWith('Hair') || n === 'Brow' ? 'Hair' : n; const t = pick[part];
      if (!t || (part === 'Hair' && k === 'mies_b') || (t[0] === 1 && t[1] === 1 && t[2] === 1)) return; const m = o.material.clone(); m.color.setRGB(m.color.r * t[0], m.color.g * t[1], m.color.b * t[2]); o.material = m; mats.push(m); }); return mats; };
  const mkChar = k => { const g = new THREE.Group(), root = cloneSk(MOD[k].scene), mats = tintChar(root, k); g.mats = mats; g.add(root); g.userData.noT = true; _P.scene.add(g); const mix = new THREE.AnimationMixer(root), act = {};
    for (const c of MOD[k].animations) act[c.name] = mix.clipAction(c); if (act.Walk) act.Walk.play(); return { k, g, mix, act, cur: 'Walk', x: 0, y: 0, z: 0, yaw: 0, kid: k === 'tytto' || k === 'poika' }; };
  const setAnim = (c, name) => { if (c.cur === name || !c.act[name]) return; c.act[name].reset().play(); if (c.act[c.cur]) c.act[c.cur].crossFadeTo(c.act[name], 0.25, false); c.cur = name; };
  const count = () => parties.reduce((a, p) => a + p.m.length, 0);
  const spawn = (px, py) => { let a = net[Math.floor(rnd() * net.length)], e = null, t = rnd(); const far = (x, y) => { const d = Math.hypot(x - px, y - py); return d > 18 && d < 95; };
    if (rnd() < 0.75) {                                                          // most new parties start on a pedestrian street or the square near the player:
      const ed = busyE.filter(q => far(q.a.x + (q.e.n.x - q.a.x) * t, q.a.y + (q.e.n.y - q.a.y) * t)), gr = parties.filter(q => q.b.grid).length < NMAX / 6 ? busy.filter(q => q.grid && far(q.x, q.y)) : [];   // a street by its length, so the long Yrjönkatu gets most
      if (ed.length && (rnd() < 0.75 || !gr.length)) { const q = pickW(ed, ed.map(q => q.w)); a = q.a; e = q.e; } else if (gr.length) a = gr[Math.floor(rnd() * gr.length)]; }
    if (!e) { e = a.nb[Math.floor(rnd() * a.nb.length)]; if (Math.hypot(a.x - px, a.y - py) > 150 || (!a.busy && Math.hypot(a.x - px, a.y - py) < 45)) return; }
    const r = rnd(); let ks;                                                   // 45 % alone, 20 % two adults, 35 % a family
    if (r < 0.45) ks = [adult()]; else if (r < 0.65) ks = [adult(), adult()];
    else { ks = [guard()]; if (rnd() < 0.3) ks.push(adult()); ks.push(child()); if (rnd() < 0.4) ks.push(child()); }
    if (ks.some(k => !MOD[k])) return;
    const p = { a, b: e.n, c: e.c, pc: 0, t, v: ks.length > 2 ? 1.0 : 1.15 + rnd() * 0.3, wait: false, lat: (rnd() - 0.5) * 7, m: ks.map(mkChar) };          /* lat: on a pedestrian street the party keeps its own line, not the centre line */
    p.m.forEach((c, i) => { c.off = i ? (i % 2 ? 0.6 : -0.6) * Math.ceil(i / 2) : 0; c.back = i ? 0.25 + rnd() * 0.3 : 0; c.x = a.x + (e.n.x - a.x) * t; c.y = a.y + (e.n.y - a.y) * t; c.new = true; }); parties.push(p); };      /* 20.11.2026: placed at once; a new party stood at (0, 0) until its first step and was dropped again as "over 150 m away" whenever the player was that far from the map origin, so there were no walkers outside the centre */
  const sigFor = (a, b) => { const S_ = window.__sig; if (!S_ || !S_.poles.length) return undefined; const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2, L = Math.hypot(b.x - a.x, b.y - a.y) || 1, ux = (b.x - a.x) / L, uy = (b.y - a.y) / L;
    let best = null, bd = 16; for (const q of S_.poles) { const d = Math.hypot(q.x - mx, q.y - my); if (d < bd && Math.abs(ux * q.ux + uy * q.uy) < 0.6) { bd = d; best = q; } } return best; };
  // H on foot: the nearest walker within 8 m stops, turns to the player and says something in the Pori dialect (radio/huuto_*.mp3, tools/radio/huudot.py;
  // m = man, n = woman, l = child; the text is shown too). The party stands for the length of the line.
  let HU = null, huEl = null, huT = 0; fetch('./radio/huudot.json').then(r => r.json()).then(j => { HU = j; }).catch(() => {});
  const greet = auto => { if (!HU || performance.now() < huT) return; let best = null, bp = null, bd = auto ? 2.6 : 8;
    for (const p of parties) for (const c of p.m) { const d = Math.hypot(c.x - _P.WALK.x, c.y - _P.WALK.y); if (d < bd) { bd = d; best = c; bp = p; } }
    for (const c of SITTERS) { const d = Math.hypot(c.x - _P.WALK.x, c.y - _P.WALK.y) - (auto ? 1.6 : 0); if (d < bd) { bd = d; best = c; bp = c; } }      // people sitting at a table or on a bench (the sitter itself keeps saidT and hold); they answer from a little further, behind their table
    if (!best) { if (!auto) _P.toast('Ei ketään kuuloetäisyydellä', 1.4); return; }
    if (auto && performance.now() < (bp.saidT || 0)) return; bp.saidT = performance.now() + 45000; if (auto) huT = performance.now() + 6000;      // by itself: once per party in 45 s, at most one line in 6 s
    const kid = best.kid, v = kid ? 'l' : best.k.startsWith('mies') ? 'm' : 'n', L = kid ? HU.l : v === 'n' ? HU.a.concat(HU.n || []) : HU.a, i = Math.floor(Math.random() * L.length);   /* women: the shared lines + their own (files n_13...) */
    bp.hold = 3.2; huT = Math.max(huT, performance.now() + 2500); _P.toast('💬 ' + L[i], 3);
    try { huEl = huEl || new Audio(); huEl.src = './radio/huuto_' + v + '_' + String(i + 1).padStart(2, '0') + '.mp3'; huEl.volume = _P.soundOn ? 0.9 : 0; huEl.play().catch(() => {}); } catch (e) {} };
  _P.$('thei').addEventListener('pointerdown', e => { e.preventDefault(); if (_P.WALK.on && !_P.WALK.in) greet(false); });
  // ---------- places to sit (owner 20.11.2026: "saadaanko botit istumaan tuolille"; "kartoita minkälaisia penkkejä kävelykadulla on") ----------
  // Street View (summer 2019) shows on the pedestrian street: dark backless plank benches (Eetunaukio; not placed any more), red-brown ring benches round the street trees
  // with a tree guard, and café terraces fenced with red posts and rope (light armchairs, small round tables). Built here from boxes and cylinders
  // (no model file): one instanced mesh per kind, heights from carGround. Terraces stand in front of the cafés and restaurants OpenStreetMap has
  // on the pedestrian streets and the square (POI below), park benches where OpenStreetMap has a bench. Everything goes to window.__furn, so
  // SOLID keeps the player, the walkers and the cars out of it.
  // People: some seats are taken while the player is near (SITTERS, own models with the Chair clip of npc_*.js), and a passing party of one or
  // two sits down on a free bench or at a free table for a while (p.sit) and walks on. They are alive (owner 20.11.2026: "istujat vaikuttavat kuolleilta"):
  // a sitter turns towards the player who walks up and speaks (greet), after a while gets up and walks away as a party of one (seatLeave), and the
  // seats near the player are filled only by people who walk to them (new sitters appear on seats over 30 m away).
  const SEATS = [], SITTERS = [], FURN = [], SMAX = matchMedia('(pointer: coarse)').matches ? 6 : 16; let seatsOn = false, seatTry = 0, seatFill = 0;
  const POI = [['Caffé Locale', 61.4854, 21.797822], ['Ice Cream House', 61.48524, 21.797974], ['Shots', 61.485212, 21.797929], ['Torrero', 61.485591, 21.797877], ['Petras Café', 61.4859, 21.797531], ['Kalevi', 61.485969, 21.797576],
    ['Pub Jussikka', 61.485887, 21.798099], ['Kotipizza', 61.486147, 21.796471], ['Espresso House', 61.48428, 21.797214], ['Burger King', 61.484327, 21.797255], ['Burger Company', 61.484498, 21.797339], ['Seoul Crunch', 61.484628, 21.79739],
    ['Coffee House', 61.483856, 21.797007], ['Café Teljäntori', 61.484429, 21.795921], ['Jätskibaari Vohveli', 61.484254, 21.796111], ['Cafe Anton', 61.487372, 21.795937], ['Hesburger', 61.486847, 21.796544], ['Galle', 61.487235, 21.796972],
    ['Borg', 61.48521, 21.79697], ['Cafe Europa', 61.486387, 21.798313], ['Mäkilän Leipomo', 61.486539, 21.795482], ['Päre', 61.486635, 21.795531], ['06 Tori Pizzeria', 61.48727, 21.796554], ['Rosso', 61.487186, 21.795847]];
  const OSMB = [[61.485126, 21.799022, 2], [61.485048, 21.791777, 2], [61.485078, 21.791571, 2], [61.48535, 21.791701, 2], [61.485327, 21.791918, 2], [61.482949, 21.790774, 2], [61.482973, 21.790539, 2]];      // OpenStreetMap amenity=bench: lat, lon, kind (2 = the park bench with a backrest)
  const hs = (a, b) => { let x = (Math.imul(a | 0, 73856093) ^ Math.imul(b | 0, 19349663)) >>> 0; x ^= x >>> 15; x = Math.imul(x, 2246822519) >>> 0; x ^= x >>> 13; return (x >>> 0) / 4294967296; };
  const seatBuild = () => {
    const V3 = THREE.Vector3, M4 = THREE.Matrix4, QQ = THREE.Quaternion, one = new V3(1, 1, 1), E3 = new THREE.Euler();
    const bx = (w, h, d, x, y, z, c, ry = 0, rx = 0) => [new THREE.BoxGeometry(w, h, d), new M4().compose(new V3(x, y, z), new QQ().setFromEuler(E3.set(rx, ry, 0, 'YXZ')), one), c];
    const cy = (r0, r1, h, x, y, z, c, n = 10) => [new THREE.CylinderGeometry(r0, r1, h, n), new M4().makeTranslation(x, y, z), c];
    const merge = parts => { let n = 0; const G = parts.map(([g, m, c]) => { const q = g.index ? g.toNonIndexed() : g; q.applyMatrix4(m); n += q.attributes.position.count; return [q, new THREE.Color(c)]; });
      const P = new Float32Array(n * 3), Nn = new Float32Array(n * 3), C = new Float32Array(n * 3); let o = 0;
      for (const [q, c] of G) { const k = q.attributes.position.count; P.set(q.attributes.position.array, o * 3); Nn.set(q.attributes.normal.array, o * 3); for (let i = 0; i < k; i++) { C[(o + i) * 3] = c.r; C[(o + i) * 3 + 1] = c.g; C[(o + i) * 3 + 2] = c.b; } o += k; q.dispose(); }
      const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(P, 3)); g.setAttribute('normal', new THREE.BufferAttribute(Nn, 3)); g.setAttribute('color', new THREE.BufferAttribute(C, 3)); return g; };
    // the models: y up, the sitter faces -z, width along x
    const DK = 0x2c2e30, RD = 0x7d3026, RD2 = 0x8e3028, IR = 0x2a211f, GN = 0x1f3a2a, WD = 0x8a5a33, CH = 0xcbc8c0, TB = 0xd9d6cd, BK = 0x1c1c1c, ring = [];
    for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4, s = Math.sin(a), c = Math.cos(a); ring.push(bx(0.70, 0.06, 0.44, s * 0.80, 0.42, c * 0.80, RD, a), bx(0.06, 0.39, 0.36, s * 0.80, 0.195, c * 0.80, IR, a), bx(0.30, 0.55, 0.02, s * 0.36, 0.74, c * 0.36, RD, a),
      cy(0.013, 0.013, 1.5, Math.sin(a + 0.39) * 0.39, 1.2, Math.cos(a + 0.39) * 0.39, IR, 5), bx(0.32, 0.03, 0.03, s * 0.37, 1.93, c * 0.37, IR, a), bx(0.32, 0.03, 0.03, s * 0.37, 1.25, c * 0.37, IR, a)); }
    const GEO = [
      merge([bx(1.8, 0.07, 0.13, 0, 0.415, -0.15, DK), bx(1.8, 0.07, 0.13, 0, 0.415, 0, DK), bx(1.8, 0.07, 0.13, 0, 0.415, 0.15, DK), bx(0.10, 0.38, 0.40, -0.62, 0.19, 0, DK), bx(0.10, 0.38, 0.40, 0.62, 0.19, 0, DK), bx(1.24, 0.08, 0.06, 0, 0.30, 0, DK)]),      // 0 plank bench
      merge(ring),                                                                                                                                                                                                                                  // 1 ring bench round a tree
      merge([bx(1.6, 0.035, 0.10, 0, 0.44, -0.14, WD), bx(1.6, 0.035, 0.10, 0, 0.44, -0.02, WD), bx(1.6, 0.035, 0.10, 0, 0.44, 0.10, WD), bx(1.6, 0.10, 0.03, 0, 0.62, 0.20, WD, 0, -0.2), bx(1.6, 0.10, 0.03, 0, 0.78, 0.235, WD, 0, -0.2),
        bx(0.05, 0.44, 0.05, -0.7, 0.22, -0.16, GN), bx(0.05, 0.44, 0.05, 0.7, 0.22, -0.16, GN), bx(0.05, 0.86, 0.05, -0.7, 0.43, 0.21, GN, 0, -0.1), bx(0.05, 0.86, 0.05, 0.7, 0.43, 0.21, GN, 0, -0.1), bx(0.05, 0.04, 0.42, -0.7, 0.42, 0.02, GN), bx(0.05, 0.04, 0.42, 0.7, 0.42, 0.02, GN)]),      // 2 park bench
      merge([bx(0.46, 0.05, 0.44, 0, 0.425, 0, CH), bx(0.46, 0.42, 0.04, 0, 0.68, 0.225, CH, 0, -0.14), bx(0.04, 0.04, 0.40, -0.25, 0.63, 0.02, CH), bx(0.04, 0.04, 0.40, 0.25, 0.63, 0.02, CH), bx(0.035, 0.63, 0.035, -0.25, 0.315, -0.18, CH), bx(0.035, 0.63, 0.035, 0.25, 0.315, -0.18, CH),
        bx(0.035, 0.45, 0.035, -0.22, 0.225, 0.2, CH), bx(0.035, 0.45, 0.035, 0.22, 0.225, 0.2, CH)]),                                                                                                                                            // 3 terrace armchair
      merge([cy(0.36, 0.36, 0.03, 0, 0.735, 0, TB, 16), cy(0.03, 0.03, 0.70, 0, 0.37, 0, BK, 8), cy(0.20, 0.23, 0.03, 0, 0.015, 0, BK, 12)]),                                                                                                      // 4 table
      merge([cy(0.055, 0.075, 0.82, 0, 0.41, 0, RD2, 4), cy(0.0, 0.06, 0.08, 0, 0.86, 0, RD2, 4)]),                                                                                                                                                // 5 fence post
      merge([bx(1, 0.03, 0.03, 0, 0.70, 0, BK)]) ];                                                                                                                                                                                                // 6 rope (1 m, scaled)
    const BOX = [[0.25, 0.9], [1.05, 1.05], [0.26, 0.82], [0.25, 0.25], [0.36, 0.36], [0.08, 0.08], [0.04, 0.5]], g2 = (lat, lon) => [(lon - 21.796) * 53278, (lat - 61.486) * 111437];
    const asph = (x, y) => _P.ROAD.on && _P.ROAD.asphAt && _P.ROAD.asphAt(x, y), inB = (x, y) => _P.bldTopAt(x, y) > _P.TZs(x, y) + 1.0, pad = (x, y) => Math.hypot(x - _P.HOME.x, y - _P.HOME.y) < 16;
    const clear = (x, y, r) => { for (const f of FURN) if (Math.hypot(f.x - x, f.y - y) < r + (f.r || 0)) return false; if (window.__bikes) for (const b of window.__bikes) if (Math.hypot(b.x - x, b.y - y) < r) return false; return true; };
    const ok = (x, y) => _P.walkFree(x, y) && !asph(x, y) && !pad(x, y) && _P.inCore(x, y);
    const put = (k, x, y, yaw, o = {}) => { const f = { k, x, y, yaw, sx: o.sx || 1, r: o.r || 0, hl: BOX[k][0], hw: BOX[k][1] * (o.sx || 1), gone: false }; FURN.push(f); return f; };
    const seat = (f, lx, lz, dyaw, kind, grp) => { const sn = Math.sin(f.yaw), cs = Math.cos(f.yaw); SEATS.push({ x: f.x + cs * lx + sn * lz, y: f.y - sn * lx + cs * lz, yaw: f.yaw + dyaw, h: 0.45, kind, f, g: grp || f, occ: null, st: false }); };      // lx to the sitter's right, lz forward; g: the bench, or the table the chair stands at (a party sits together)
    // 1. ring benches round the trees that stand on a pedestrian street
    const E = busyE.map(q => [q.a, q.e.n]), near = (x, y) => { let bd = 1e9, bq = null; for (const [a, b] of E) { const ex = b.x - a.x, ey = b.y - a.y, u = Math.max(0, Math.min(1, ((x - a.x) * ex + (y - a.y) * ey) / (ex * ex + ey * ey || 1))), qx = a.x + ex * u, qy = a.y + ey * u, d = Math.hypot(x - qx, y - qy); if (d < bd) { bd = d; bq = [qx, qy, ex, ey]; } } return bq && [bd, ...bq]; };
    for (const t of window.__treeList || []) { const n = near(t.x, t.y); if (!n || n[0] > 4 || !ok(t.x, t.y) || !clear(t.x, t.y, 3)) continue; const f = put(1, t.x, t.y, Math.atan2(n[3], n[4]), { r: 1.1 });
      for (let i = 0; i < 4; i++) { const a = f.yaw + Math.PI / 4 + i * Math.PI / 2, sx = t.x + Math.sin(a) * 1.5, sy = t.y + Math.cos(a) * 1.5; if (ok(sx, sy)) SEATS.push({ x: t.x + Math.sin(a) * 0.80, y: t.y + Math.cos(a) * 0.80, yaw: a, h: 0.45, kind: 1, f, g: f, occ: null, st: false }); } }
    // 2. terraces in front of the cafés: from the map point out of the house towards the street, tables along the wall
    let nt = 0; const TC = [];
    for (const [nm, la, lo] of POI) { if (nt >= 12) break; const [px, py] = g2(la, lo); let tq = near(px, py); for (const q of busy) if (q.grid) { const d = Math.hypot(q.x - px, q.y - py); if (!tq || d < tq[0]) tq = [d, q.x, q.y, 0, 0]; }
      if (!tq || tq[0] > 24 || tq[0] < 2) continue; const dx = (tq[1] - px) / tq[0], dy = (tq[2] - py) / tq[0]; let w = -1;
      for (let t = 0; t < tq[0] - 2; t += 0.25) if (!inB(px + dx * t, py + dy * t) && !inB(px + dx * (t + 0.6), py + dy * (t + 0.6)) && !inB(px + dx * (t + 1.2), py + dy * (t + 1.2))) { w = t; break; }
      if (w < 0 || tq[0] - w < 5.5) continue; const ox = px + dx * (w + 1.55), oy = py + dy * (w + 1.55), ax = dy, ay = -dx, yw = Math.atan2(dx, dy); if (TC.some(q => Math.hypot(q[0] - ox, q[1] - oy) < 11)) continue;
      const tabs = []; for (const i of [0, -1, 1]) { const tx = ox + ax * i * 2.3, ty = oy + ay * i * 2.3; if (ok(tx, ty) && ok(tx + ax * 0.8, ty + ay * 0.8) && ok(tx - ax * 0.8, ty - ay * 0.8) && ok(tx + dx * 1.3, ty + dy * 1.3) && !inB(tx - dx * 0.9, ty - dy * 0.9) && clear(tx, ty, 1.6)) tabs.push(i); }
      if (tabs.length < 2 && !tabs.includes(0)) continue; TC.push([ox, oy]); nt++; const lo_ = Math.min(...tabs), hi = Math.max(...tabs);
      for (const i of tabs) { const tx = ox + ax * i * 2.3, ty = oy + ay * i * 2.3; const tb = put(4, tx, ty, yw, { r: 1.2 });
        for (const s of [1, -1]) seat(put(3, tx + ax * s * 0.78, ty + ay * s * 0.78, Math.atan2(-ax * s, -ay * s)), 0, 0.02, 0, 3, tb);
        if (hs(nt, i + 5) < 0.5) seat(put(3, tx - dx * 0.80, ty - dy * 0.80, yw), 0, 0.02, 0, 3, tb); }
      const a0 = lo_ * 2.3 - 1.45, a1 = hi * 2.3 + 1.45, fr = 1.45, bk = -1.25, P = (a, d) => [ox + ax * a + dx * d, oy + ay * a + dy * d], rope = (p, q) => { const L = Math.hypot(q[0] - p[0], q[1] - p[1]); put(6, (p[0] + q[0]) / 2, (p[1] + q[1]) / 2, Math.atan2(q[0] - p[0], q[1] - p[1]) + Math.PI / 2, { sx: L }); };
      const n = Math.max(2, Math.round((a1 - a0) / 1.6)), fp = []; for (let i = 0; i <= n; i++) fp.push(P(a0 + (a1 - a0) * i / n, fr)); const gap = Math.floor(n / 2);      // the fence: posts along the street side with a gap to walk in, a rope back to the wall at both ends
      fp.forEach((p, i) => { put(5, p[0], p[1], yw); if (i && i - 1 !== gap) rope(fp[i - 1], p); }); for (const a of [a0, a1]) { const q = P(a, bk); put(5, q[0], q[1], yw); rope(P(a, fr), q); } }
    // (the loose dark plank benches along the streets were taken out again: owner 20.11.2026, "nuo mustat irralliset penkit voi poistaa")
    // 3. the benches OpenStreetMap knows (parks): facing the nearest footway
    for (const [la, lo, k] of OSMB) { const [x, y] = g2(la, lo); if (!_P.walkFree(x, y) || !clear(x, y, 2)) continue; let bn = null, bd = 60; for (const q of net) { const d = Math.hypot(q.x - x, q.y - y); if (d < bd && d > 0.5) { bd = d; bn = q; } }
      const f = put(k, x, y, bn ? Math.atan2(bn.x - x, bn.y - y) : 0, { r: 1 }); for (const lx of k === 2 ? [-0.4, 0.4] : [-0.6, 0, 0.6]) seat(f, lx, 0.02, 0, k); }
    // draw: one instanced mesh per kind
    const mat = new THREE.MeshLambertMaterial({ vertexColors: true }); mat.userData.noT = true; const m4 = new M4(), p3 = new V3(), q4 = new QQ(), s3 = new V3(), UPV = new V3(0, 1, 0);
    GEO.forEach((g, k) => { const L = FURN.filter(f => f.k === k); if (!L.length) return; const im = new THREE.InstancedMesh(g, mat, L.length); im.userData.noT = true; im.frustumCulled = false;
      L.forEach((f, i) => { f.z = _P.carGround(f.x, f.y) ?? _P.TZs(f.x, f.y); p3.set(f.x, f.z, -f.y); q4.setFromAxisAngle(UPV, -f.yaw); s3.set(f.sx, 1, 1); im.setMatrixAt(i, m4.compose(p3, q4, s3)); }); _P.scene.add(im); });
    SEATS.forEach((s, i) => { s.z = _P.carGround(s.x, s.y) ?? _P.TZs(s.x, s.y); s.st = hs(i, 7) < [0.2, 0.3, 0.3, 0.5][s.kind]; });
    window.__furn = FURN; seatsOn = true; seatFill = performance.now() + 8000; };
  const sitDown = (c, s) => { c.x = s.x; c.y = s.y; c.z = s.z; c.yaw = s.yaw; c.g.position.set(s.x, s.z + s.h, -s.y); c.g.rotation.y = -s.yaw; };
  const freeChar = c => { _P.scene.remove(c.g); c.mix.stopAllAction(); for (const m of c.g.mats || []) m.dispose(); if (c.seat) c.seat.occ = null; };
  const seatLeave = c => { const s = c.seat; let b = null, bd = 40; for (const q of net) { const d = Math.hypot(q.x - s.x, q.y - s.y); if (d < bd) { bd = d; b = q; } } if (!b) { c.life = 30; return; }      // a sitter gets up: from now on a walking party of one, off to the nearest footway
    const p = { a: { x: s.x + Math.sin(s.yaw) * 0.7, y: s.y + Math.cos(s.yaw) * 0.7, nb: [{ n: b, c: 0 }] }, b, c: 0, pc: 0, t: 0, v: 1.15 + rnd() * 0.3, wait: false, lat: (rnd() - 0.5) * 7, m: [c], sit: { T: 0, ph: 2, e: 0 }, satT: performance.now() + 180000 };
    c.off = 0; c.back = 0; c.new = false; c.sat = true; c.hold = 0; s.cool = performance.now() + 45000; SITTERS.splice(SITTERS.indexOf(c), 1); parties.push(p); };
  const seatTick = (px, py) => {      // four times a second
    if (!seatsOn) { if (net && KIND.every(k => MOD[k]) && (window.__roads || ++seatTry > 40) && (window.__treeList || seatTry > 40)) { try { seatBuild(); } catch (e) { seatsOn = true; console.warn('seats', e); } } return; }
    if (!MOD.mies_a.animations.some(a => a.name === 'Chair')) return; const now = performance.now();
    for (let i = SITTERS.length - 1; i >= 0; i--) { const c = SITTERS[i], d = Math.hypot(c.x - px, c.y - py); if (d > 95) { freeChar(c); SITTERS.splice(i, 1); } else if ((c.life -= 0.25) < 0 && d < 75 && !(c.hold > 0) && count() < NMAX + 8) seatLeave(c); }
    if (SITTERS.length < SMAX) for (let i = 0; i < SEATS.length; i++) { const s = SEATS[i], d = Math.hypot(s.x - px, s.y - py); if (!s.st || s.occ || d > 75 || (d < 30 && now > seatFill) || now < (s.cool || 0)) continue;      // near the player nobody pops up on a seat: those are taken by people who walk there
        const r = hs(i, 11), k = r < 0.32 ? 'nainen_a' : r < 0.62 ? 'nainen_b' : r < 0.93 ? 'mies_a' : 'mies_b', c = mkChar(k); c.seat = s; s.occ = c; sitDown(c, s); c.life = 20 + rnd() * 120;
        if (c.act.Walk) c.act.Walk.stop(); c.act.Chair.play(); c.act.Chair.time = hs(i, 13) * 6; c.cur = 'Chair'; SITTERS.push(c); break; }      /* one new sitter per tick */
    for (const p of parties) { if (p.sit || p.m.length > 2 || p.hold > 0 || p.wait || now < (p.satT || 0) || rnd() > 0.08) continue; const l = p.m[0]; if (Math.hypot(l.x - px, l.y - py) > 70) continue;
      let bg = null, bd = 7; for (const s of SEATS) { if (s.occ) continue; const d = Math.hypot(s.x - l.x, s.y - l.y); if (d < bd && SEATS.filter(q => q.g === s.g && !q.occ).length >= p.m.length) { bd = d; bg = s.g; } }
      if (!bg) continue; const fr = SEATS.filter(q => q.g === bg && !q.occ).sort((a, b) => Math.hypot(a.x - l.x, a.y - l.y) - Math.hypot(b.x - l.x, b.y - l.y));
      p.sit = { T: 14 + rnd() * 40, ph: 0, e: 0 }; p.m.forEach((c, i) => { c.seat = fr[i]; fr[i].occ = c; c.sat = false; c.at2 = false; c.ap = null; }); } };
  const seatLook = (c, s, dt, on) => { let t = s.yaw; if (on) { let a = Math.atan2(_P.S.x - c.x, _P.S.y - c.y) - s.yaw; a = Math.atan2(Math.sin(a), Math.cos(a)); t += Math.max(-0.8, Math.min(0.8, a)); }      // seated: turn towards the player (0.8 rad at most), and back
    let d = t - c.yaw; d = Math.atan2(Math.sin(d), Math.cos(d)); c.yaw += d * Math.min(1, dt * 4); c.g.rotation.y = -c.yaw; };
  // ---------- seated people move their hands (owner 20.11.2026: "saadanko istuvat botit liikuttamaan käsiään, nyt ne istuu staattisesti") ----------
  // The Chair clip is one still pose. After the mixer every visible sitter gets a small procedural layer on the arms: a slow breathing sway and, every
  // few seconds, a gesture (talking with one hand, both hands up as if reading a phone, a hand to the chin), eased in and out. The elbow bends about the
  // body's left-right axis (shoulder to shoulder, world space) in whichever direction lifts the hand, so it does not depend on the bone axes of the
  // model (the hinge from upper arm x forearm folded the arms backwards when they hang straight). The bones keep the pose the mixer gave them (base)
  // and get it back before the layer is added again, so nothing accumulates even if the Chair action does not rewrite them every frame.
  const ARMS = (() => { const V = THREE.Vector3, Q = THREE.Quaternion, b = new V(), cc = new V(), n = new V(), fo = new V(), sl = new V(), sr = new V(), pq = new Q(), wq = new Q(), dq = new Q();
    const rot = (bone, axis, ang) => { if (!ang) return; bone.parent.getWorldQuaternion(pq); bone.getWorldQuaternion(wq); dq.setFromAxisAngle(axis, ang); wq.premultiply(dq); bone.quaternion.copy(pq.invert().multiply(wq)); bone.updateMatrixWorld(true); };
    const bend = (A, S, f, tw) => { if (!f && !tw) return;
      if (f) { A.L.u.getWorldPosition(sl); A.R.u.getWorldPosition(sr); n.copy(sr).sub(sl).normalize(); S.h.getWorldPosition(cc); const y0 = cc.y; rot(S.l, n, f); S.h.getWorldPosition(cc); if (cc.y < y0) rot(S.l, n, -2 * f); }
      if (tw) { S.l.getWorldPosition(b); S.h.getWorldPosition(cc); fo.copy(cc).sub(b).normalize(); rot(S.h, fo, tw); } };
    const setup = c => { const r = c.g.children[0], g = s => r.getObjectByName(s), L = { u: g('upperarm_l'), l: g('lowerarm_l'), h: g('hand_l') }, R = { u: g('upperarm_r'), l: g('lowerarm_r'), h: g('hand_r') };
      if (![L.u, L.l, L.h, R.u, R.l, R.h].every(Boolean)) return false;
      return { L, R, B: [L.l, L.h, R.l, R.h].map(o => ({ o, base: o.quaternion.clone(), last: null })), t: 0, nx: 1 + Math.random() * 5, gs: null, ph: Math.random() * 6.3 }; };
    const ease = x => x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x);
    return (c, dt) => { if (c.arm === undefined) c.arm = setup(c); const A = c.arm; if (!A) return;
      for (const k of A.B) { if (k.last && k.o.quaternion.equals(k.last)) k.o.quaternion.copy(k.base); else k.base.copy(k.o.quaternion); }   // the mixer did not write: back to the base pose
      c.g.updateMatrixWorld(true); A.t += dt;
      let fl = 0.06 * (1 + Math.sin(A.t * 1.3 + A.ph)), fr = 0.06 * (1 + Math.sin(A.t * 1.1 + A.ph + 1)), tl = 0, tr = 0;              // breathing
      if (!A.gs && (A.nx -= dt) < 0) { const r = Math.random(); A.gs = { ty: r < 0.5 ? 'talk' : r < 0.78 ? 'phone' : 'chin', side: Math.random() < 0.6 ? 1 : -1, t: 0, d: r < 0.5 ? 2.5 + Math.random() * 3 : r < 0.78 ? 4 + Math.random() * 6 : 2 + Math.random() * 2 }; }
      const G = A.gs; if (G) { G.t += dt; const e = ease(G.t / 0.6) * ease((G.d - G.t) / 0.6), s = G.t;
        if (G.ty === 'talk') { const f = e * (1.05 + 0.25 * Math.sin(s * 7.5)), w = e * 0.5 * Math.sin(s * 5.3); if (G.side > 0) { fr += f; tr += w; } else { fl += f; tl += w; } }   // one hand explains
        else if (G.ty === 'phone') { fl += e * 1.15; fr += e * 1.15; tl += e * 0.15 * Math.sin(s * 0.7); tr -= e * 0.15 * Math.sin(s * 0.7); }                              // both hands up in front
        else { const f = e * (1.9 + 0.06 * Math.sin(s * 3)); if (G.side > 0) { fr += f; tr += e * 0.3; } else { fl += f; tl -= e * 0.3; } }                                    // hand to the chin
        if (G.t >= G.d) { A.gs = null; A.nx = 3 + Math.random() * 9; } }
      bend(A, A.L, fl, tl); bend(A, A.R, fr, tr);
      for (const k of A.B) (k.last || (k.last = new Q())).copy(k.o.quaternion); }; })();
  const seatFrame = (dt, px, py) => { let foot = false; try { foot = _P.WALK.on && !_P.WALK.in; } catch (e) {}
    for (const c of SITTERS) { const d = Math.hypot(c.x - px, c.y - py), v = d < 70; c.g.visible = v; if (c.hold > 0) c.hold -= dt; if (v) { seatLook(c, c.seat, dt, c.hold > 0 || (foot && d < 4.5)); c.mix.update(dt); if (d < 40) ARMS(c, dt); } }
    for (const p of parties) { const s = p.sit; if (!s) continue;
      if (s.ph === 0) { if (p.m.every(c => c.sat)) s.ph = 1; else if ((s.e += dt) > 25) s.ph = 2; }      // 0 walking to the bench (25 s at most), 1 sitting, 2 getting up
      else if (s.ph === 1) { if ((s.T -= dt) < 0) s.ph = 2; }
      else if (p.m.every(c => !c.seat)) { p.sit = null; p.satT = performance.now() + 180000; } } };
  const seatMove = (p, c, dt, vis) => { const s = c.seat, up = p.sit && p.sit.ph === 2; let sp = 0;
    if (!c.ap) { if (s.kind === 3) { const rx = Math.cos(s.yaw) * 0.62, ry = -Math.sin(s.yaw) * 0.62, k = Math.hypot(s.x + rx - c.x, s.y + ry - c.y) < Math.hypot(s.x - rx - c.x, s.y - ry - c.y) || c.sat ? 1 : -1; c.ap = [s.x + rx * k, s.y + ry * k]; }      // a chair at a table is entered from its side, a bench from the front
      else c.ap = [s.x + Math.sin(s.yaw) * 0.7, s.y + Math.cos(s.yaw) * 0.7]; }
    const fx = c.ap[0], fy = c.ap[1]; let gx = fx, gy = fy;      // (fx, fy): standing beside or in front of the seat
    if (up) { if (c.sat) { c.sat = false; c.at2 = true; setAnim(c, 'Idle'); c.e = 0; } if ((c.e = (c.e || 0) + dt) < 0.45) { gx = s.x; gy = s.y; } }
    else if (c.at2) { gx = s.x; gy = s.y; }
    if (!c.sat) { const dx = gx - c.x, dy = gy - c.y, d = Math.hypot(dx, dy), st = Math.min(d, (c.at2 ? 0.7 : 1.25) * dt); if (d > 1e-4) { c.x += dx / d * st; c.y += dy / d * st; sp = st / Math.max(dt, 1e-3); }
      let ty = c.at2 ? s.yaw : Math.atan2(dx, dy), a = ty - c.yaw; a = Math.atan2(Math.sin(a), Math.cos(a)); c.yaw += a * Math.min(1, dt * 7);
      if (d < 0.06) { if (up) { if (c.e >= 0.45) { s.occ = null; c.seat = null; c.at2 = false; c.zo = 0; c.ap = null; } } else if (!c.at2) c.at2 = true; else { c.sat = true; setAnim(c, 'Chair'); } } }
    const g = _P.carGround(c.x, c.y); if (g !== null) c.z += (g - c.z) * Math.min(1, dt * 10); c.zo = (c.zo || 0) + ((c.sat ? s.h : 0) - (c.zo || 0)) * Math.min(1, dt * 6);
    c.g.position.set(c.x, c.z + c.zo, -c.y); c.g.rotation.y = -c.yaw; c.g.visible = vis;
    if (c.sat) { let foot = false; try { foot = _P.WALK.on && !_P.WALK.in; } catch (e) {} seatLook(c, s, dt, p.hold > 0 || (foot && Math.hypot(_P.S.x - c.x, _P.S.y - c.y) < 4.5)); }
    if (vis) { if (!c.sat) setAnim(c, sp > 0.3 ? 'Walk' : 'Idle'); if (c.act.Walk) c.act.Walk.timeScale = Math.max(0.6, sp / STRIDE[c.k]); c.mix.update(dt); if (c.sat) ARMS(c, dt); } };
  let acc = 0;
  window.__npc = { parties, sitters: SITTERS, seats: SEATS, greet: () => greet(false), mk: k => MOD[k] ? mkChar(k) : null, free: freeChar, anim: setAnim, stride: STRIDE,      /* mk/free/anim: people waiting at bus stops (bus module) */ mk: mkChar, free: freeChar,      /* mk/free: the bicycle passenger (kyydit) is an own copy of the walker */
    arrive: (x, y, ch) => { if (!net || count() > NMAX + 6) return;      /* ch: this very walker gets off (bicycle passenger) */ let b = null, bd = 30; for (const q of net) { const d = Math.hypot(q.x - x, q.y - y); if (d < bd) { bd = d; b = q; } } if (!b) return;   // people getting out of a car that has just parked: they walk to the nearest footway
      const r = rnd(), ks = ch ? [ch.k] : r < 0.5 ? [adult()] : r < 0.8 ? [adult(), adult()] : [guard(), child()]; if (ks.some(k => !MOD[k])) return;
      const p = { a: { x, y, nb: [{ n: b, c: 0 }] }, b, c: 0, pc: 0, t: 0, v: 1.2, wait: false, lat: (rnd() - 0.5) * 7, m: ch ? [ch] : ks.map(mkChar) };
      p.m.forEach((c, i) => { c.off = i ? (i % 2 ? 0.6 : -0.6) * Math.ceil(i / 2) : 0; c.back = i ? 0.25 + rnd() * 0.3 : 0; c.x = x; c.y = y; c.z = _P.carGround(x, y) ?? 0; c.new = true; }); parties.push(p); return true; },
    update: dt => { if (!net || dt <= 0) return; const px = _P.S.x, py = _P.S.y;
    _P.DANCE.tick();
    seatFrame(dt, px, py);
    acc += dt; if (acc > 0.25) { acc = 0; seatTick(px, py); if (_P.WALK.on && !_P.WALK.in) greet(true);       /* walking up to somebody (2.6 m) makes them speak; H still calls from further away */
      if (count() < NMAX) spawn(px, py);
      else { let w = null, wd = 85; for (const q of parties) { const d = Math.hypot(q.m[0].x - px, q.m[0].y - py); if (d > wd) { wd = d; w = q; } } if (w) w.m[0].x = 1e6; }   /* full: the farthest party (over 85 m away) makes room, so the people gather where the player is */
      for (let i = parties.length - 1; i >= 0; i--) { const p = parties[i]; if (Math.hypot(p.m[0].x - px, p.m[0].y - py) > 150) { for (const c of p.m) freeChar(c); parties.splice(i, 1); } } }
    for (const p of parties) { let dx = p.b.x - p.a.x, dy = p.b.y - p.a.y, len = Math.hypot(dx, dy) || 1;
      if (p.c && !p.pc && p.t < 0.02) { if (p.sg === undefined) p.sg = sigFor(p.a, p.b); p.wait = !!p.sg && !window.__sig.ped(p.sg.n, p.sg.a); } else p.wait = false;   // at the kerb of a signalled crossing
      if (p.hold > 0) { p.hold -= dt; p.wait = true; }                         // greeted: stand and face the player
      if (p.sit) p.wait = true;                                                // sitting on a bench, or on the way to it
      if (!_P.DANCE.on) p.dn = undefined; else if (!p.sit) { const d = Math.hypot(p.m[0].x - px, p.m[0].y - py);      // music (B): 1 dancing, 0 not this one; decided when the party first comes within 13 m, not on a crossing
        if (p.dn === undefined) { if (d < 13 && !p.c && !p.wait) p.dn = Math.random() < 0.75 ? 1 : 0; } else if (d > 19) p.dn = undefined; if (p.dn) p.wait = true; }
      if (p.c && !p.pc && p.t < 0.02) { if (!p.wait && (p.gw || 0) < 6 && _P.SOLID.coming(p.a.x, p.a.y, p.b.x, p.b.y)) { p.gw = (p.gw || 0) + dt; p.wait = true; } } else p.gw = 0;      // 20.11.2026: at the kerb while a car is coming (at most 6 s; then the cars brake)
      if (!p.wait) p.t += p.v * dt / len;
      if (p.t >= 1) { const o = p.b.nb, gb = p.b.grid, e = pickW(o, o.map(q => q.n === p.a ? (o.length === 1 ? 1 : q.n.busy && !q.n.grid ? 2 : 0.02) : q.n.grid ? (gb ? 1 : 0.25) : q.n.busy ? 12 : gb ? 4 : 1)); p.a = p.b;   /* stay on the pedestrian streets; cross the square, do not circle in it */ p.b = e.n; p.pc = p.c; p.c = e.c; p.sg = undefined; p.t = 0; dx = p.b.x - p.a.x; dy = p.b.y - p.a.y; len = Math.hypot(dx, dy) || 1; }
      const ux = dx / len, uy = dy / len, lx = p.a.x + dx * p.t, ly = p.a.y + dy * p.t, near = Math.hypot(lx - px, ly - py) < 110;
      const lt = p.a.busy && p.b.busy && !p.a.grid && !p.b.grid ? p.lat : 0;
      for (const c of p.m) { if (c.seat) { seatMove(p, c, dt, near); continue; } const tx = lx + uy * (c.off + lt) - ux * c.back, ty = ly - ux * (c.off + lt) - uy * c.back, fresh = c.new, k = fresh ? 1 : Math.min(1, dt * 4); c.new = false;
        let mx = (tx - c.x) * k, my = (ty - c.y) * k; if (!fresh && near) { const q = _P.SOLID.npcStep(c, mx, my, tx, ty, p.v, dt); mx = q[0]; my = q[1]; }      // 20.11.2026: cars and the player are solid
        const sp = Math.hypot(mx, my) / Math.max(dt, 1e-3); c.x += mx; c.y += my;
        if (p.hold > 0 || (p.dn && sp < 0.3)) { let d = Math.atan2(px - c.x, py - c.y) - c.yaw; d = Math.atan2(Math.sin(d), Math.cos(d)); c.yaw += d * Math.min(1, dt * 6); }
        else if (sp > 0.15) { let d = Math.atan2(mx, my) - c.yaw; d = Math.atan2(Math.sin(d), Math.cos(d)); c.yaw += d * Math.min(1, dt * 8); }
        const g = _P.carGround(c.x, c.y); if (g !== null) c.z += (g - c.z) * Math.min(1, dt * 10);
        c.g.position.set(c.x, c.z, -c.y); c.g.rotation.y = -c.yaw; c.g.visible = near;
        if (near) { const dn = p.dn && sp < 0.3 && c.act.Dance ? (c.dk || (c.dk = Math.random() < 0.45 && c.act.Dance2 ? 'Dance2' : 'Dance')) : '';
          setAnim(c, sp > 0.3 ? 'Walk' : dn || 'Idle'); if (c.act.Walk) c.act.Walk.timeScale = Math.max(0.6, sp / STRIDE[c.k]); if (dn) _P.DANCE.sync(c.act[dn], c.dph === undefined ? (c.dph = Math.random() < 0.5 ? 0 : 2) : c.dph); c.mix.update(dt); } } } } };
}
}
