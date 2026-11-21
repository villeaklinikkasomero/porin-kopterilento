// ---------- traffic: cars wandering the street network, sized like the cars in the aerial image ----------
const cars = [];
{
  const nodes = new Map(), key = (x, y) => x + ',' + y, inb = (x, y) => x > OX0 + 8 && x < OX1 - 8 && y > OY0 + 8 && y < OY1 - 8;
  const node = (x, y) => { const k = key(x, y); if (!nodes.has(k)) nodes.set(k, { x, y, nb: [] }); return nodes.get(k); };
  CITY.r.forEach((r, ri) => { if (!r.k) return;                                  // k = 0 is a pedestrian street
    for (let i = 0; i + 3 < r.p.length; i += 2) { const ax = r.p[i], ay = r.p[i + 1], bx = r.p[i + 2], by = r.p[i + 3];
      if (!inb(ax, ay) || !inb(bx, by) || (ax === bx && ay === by)) continue; const a = node(ax, ay), b = node(bx, by);
      if (!a.nb.includes(b)) { a.nb.push(b); (a.ow || (a.ow = new Map())).set(b, [ri, i / 2, true]); } if (!b.nb.includes(a)) { b.nb.push(a); (b.ow || (b.ow = new Map())).set(a, [ri, i / 2, false]); } } });
  const busyRd = (a, b) => { const e = a.ow && a.ow.get(b); return e && CITY.r[e[0]].n === 'Yrjönkatu' ? 8 : 1; };             // owner: Yrjönkatu is the busiest street
  const pickRoad = (a, opts) => { const w = opts.map(n => busyRd(a, n)); let r = rnd() * w.reduce((x, y) => x + y, 0); for (let i = 0; i < opts.length; i++) if ((r -= w[i]) <= 0) return opts[i]; return opts[0]; };
  const may = (a, b) => { const e = a.ow && a.ow.get(b); return !e || owOk(e[0], e[1], e[2]); };   // one-way streets (filled when roads.js loads)
  const list = [...nodes.values()].filter(n => n.nb.length); list.forEach((n, i) => n.id = i);
  // traffic lights (19.11.2026): signalled junctions from OpenStreetMap (tools/roads/traffic_signals.json, game metres). Every graph node with
  // three or more arms within 24 m of a junction is signalled (a lone mid-block node = a signalled pedestrian crossing); the arms are split in
  // two groups by direction. 40 s cycle: 16 s green, 3 s yellow, 1 s all red per group. The wandering cars stop at the line and queue.
  const SIGJ = [[241,167],[296,-73],[292,-123],[-94,-303],[20,-340],[172,314],[350,134],[-269,-268],[-128,-432],[-385,-241],[-3,-463],[78,-482],[-303,-385],[193,-512],[-411,-367],[643,-76],[-596,361],[522,-581],[856,303],[-766,-760],[-494,990],[-856,-809],[-927,-825],[-1230,305],[-1394,-85],[1021,-1112],[-1565,340],[1339,-1219],[-1753,-706],[1377,-2028],[-2743,-7]], SR = 9, SIGC = 40; let sigT = 0; const sigPoles = [];
  SIGJ.forEach(([jx, jy], ji) => { let c = list.filter(n => n.nb.length >= 3 && Math.hypot(n.x - jx, n.y - jy) < 24), mid = false;
    if (!c.length) { let b = null, bd = 22; for (const n of list) { const d = Math.hypot(n.x - jx, n.y - jy); if (d < bd) { bd = d; b = n; } } if (!b) return; c = [b]; mid = true; }
    const r0 = Math.atan2(c[0].nb[0].x - c[0].x, c[0].nb[0].y - c[0].y);
    for (const n of c) { if (n.sig) continue; n.sig = { j: ji, off: (ji * 7) % SIGC, mid, grp: new Map() };
      for (const a of n.nb) n.sig.grp.set(a, Math.abs(Math.cos(Math.atan2(a.x - n.x, a.y - n.y) - r0)) > 0.7071 ? 0 : 1); } });
  const sigState = (n, from) => { const g = n.sig, t = (sigT + g.off) % SIGC; if (g.mid) return t < 26 ? 0 : t < 29 ? 1 : 2;      // 0 green, 1 yellow, 2 red
    const tt = g.grp.get(from) ? (t + 20) % SIGC : t; return tt < 16 ? 0 : tt < 19 ? 1 : 2; };
  const pedGo = (n, from) => { const g = n.sig, t = (sigT + g.off) % SIGC; if (g.mid) return t >= 30 && t < 38;                      // walk across the arm 'from'
    const tt = g.grp.get(from) ? (t + 20) % SIGC : t; return tt >= 21 && tt < 34; };
  window.__sig = { state: sigState, ped: pedGo, nodes: () => list.filter(n => n.sig), poles: sigPoles, t: () => sigT, cars };
  const N = Math.min(300, list.length), L = 4.4, W = 1.8;
  const bodyG = new THREE.BoxGeometry(W, 0.62, L); bodyG.translate(0, 0.56, 0);
  const cabG = new THREE.BoxGeometry(W * 0.86, 0.5, L * 0.5); cabG.translate(0, 1.1, 0.15);
  const baseG = new THREE.BoxGeometry(W * 0.94, 0.3, L * 0.9); baseG.translate(0, 0.17, 0);
  const body = new THREE.InstancedMesh(bodyG, new THREE.MeshLambertMaterial(), N), cab = new THREE.InstancedMesh(cabG, new THREE.MeshLambertMaterial({ color: 0x1c242c }), N), base = new THREE.InstancedMesh(baseG, new THREE.MeshLambertMaterial({ color: 0x15171a }), N);
  const PAINT = [0xf2f2f0, 0xf2f2f0, 0xc9cdd1, 0xc9cdd1, 0x8b9096, 0x2c2f33, 0x2c2f33, 0x2f4f7c, 0xa3231f, 0x5b6a4d, 0xd8d2c2], col = new THREE.Color();
  let sd = 77; const rnd = () => (sd = (sd * 16807) % 2147483647) / 2147483647;
  const yrE = []; for (const a of list) for (const b of a.nb) if (busyRd(a, b) > 1) yrE.push([a, b]);
  for (let i = 0; i < N; i++) { const a = list[Math.floor(rnd() * list.length)], b = a.nb[Math.floor(rnd() * a.nb.length)];
    cars.push({ a, b, t: rnd(), v: 7 + rnd() * 6, yaw: Math.atan2(b.x - a.x, b.y - a.y) });
    if (i < 22 && yrE.length) { const e = yrE[Math.floor(rnd() * yrE.length)], c = cars[i]; c.a = e[0]; c.b = e[1]; c.yr = true; c.yaw = Math.atan2(c.b.x - c.a.x, c.b.y - c.a.y); }   /* twenty-two regulars start on Yrjönkatu */ { const hx = PAINT[Math.floor(rnd() * PAINT.length)]; cars[i].paint = hx; body.setColorAt(i, col.setHex(hx)); } }
  scene.add(body, cab, base); let parts = [body, cab, base], typed = false;
  const m4 = new THREE.Matrix4(), q4 = new THREE.Quaternion(), p3 = new THREE.Vector3(), s3 = new THREE.Vector3(1, 1, 1), UP = new THREE.Vector3(0, 1, 0);
  // doors for a car that has parked (19.11.2026): the car models are one piece, so a door leaf in the car's paint is hinged on the front door seam over the
  // body and a dark panel shows the opening behind it. Two sets are enough (pool); cars only (types 0-2), vans and lorries do not park.
  const doorPool = [], mkDoor = () => { const g = new THREE.Group(), mat = new THREE.MeshLambertMaterial({ color: 0x888888 }), dk = new THREE.MeshLambertMaterial({ color: 0x14171a }), D = { g, mat };
    for (const [side, k] of [[1, 'R'], [-1, 'L']]) { const h = new THREE.Group(); h.position.set(side * 0.93, 0, 0.58); const lg = new THREE.BoxGeometry(0.05, 0.6, 1.04); lg.translate(0, 0.68, -0.52); const wg = new THREE.BoxGeometry(0.04, 0.36, 1.0); wg.translate(0, 1.16, -0.52);   /* the car's nose is +z: hinge on the front seam, leaf towards the tail */
      h.add(new THREE.Mesh(lg, mat), new THREE.Mesh(wg, dk)); const og = new THREE.BoxGeometry(0.03, 0.92, 1.0); og.translate(side * 0.925, 0.84, 0.06); const o = new THREE.Mesh(og, dk); g.add(h, o); D[k] = h; D['o' + k] = o; }
    g.visible = false; scene.add(g); return D; };
  cars.vanish = c => { for (let k = 0; k < 60; k++) { const a = list[Math.floor(rnd() * list.length)]; if (!a.nb.length || Math.hypot(a.x - S.x, a.y - S.y) < 150) continue;      /* the player took this parked car: it starts again far away */
      if (c.pk && c.pk.door) { c.pk.door.g.visible = false; doorPool.push(c.pk.door); } c.pk = null; c.a = a; c.b = a.nb[Math.floor(rnd() * a.nb.length)]; c.t = 0; c.st = 0; c.blk = 0; c.lat = 1.7; c.s = c.v; return; } };
  cars.update = dt => {
    if (dt < 0) dt = 0; sigT += dt; const Q = new Map(); let plc = false; try { plc = VEH === 'car' && !WALK.on; } catch (e) {} const WK = SOLID.walkers();      // the player is driving: the traffic queues behind his car too
                                                // cars by street segment, the front one first
    for (let i = 0; i < N; i++) { const c = cars[i], k = c.a.id * 65536 + c.b.id; let q = Q.get(k); if (!q) Q.set(k, q = []); if (c.pk) c.mv = 0; else q.push(c); if (c.lat === undefined) c.lat = 1.7;
      c.len = Math.hypot(c.b.x - c.a.x, c.b.y - c.a.y) || 1; c.pos = c.t * c.len; if (c.s === undefined) c.s = c.v; }
    for (const q of Q.values()) { if (q.length > 1) q.sort((m, n) => n.pos - m.pos); let lead = null;
      for (const c of q) { let room = 1e9; const g = c.b.sig;
        if (g && !(c.a.sig && c.a.sig.j === g.j)) { const sp = Math.max(c.len - SR, 0), st = sigState(c.b, c.a);          // red, or a yellow it can still stop for
          if (c.pos <= sp + 0.3 && (st === 2 || (st === 1 && sp - c.pos > c.s * 1.2))) room = sp - c.pos; }
        if (!g && c.b.nb.length >= 3) { const n = c.b, sp = Math.max(c.len - 7, 0);                    // junction without lights: the node is held by one car at a time
          if (n.res && n.res !== c && sigT < n.resT) { if (c.pos <= sp + 0.3) room = Math.min(room, sp - c.pos); }      // (first come first served; freed 0.9 s after the holder has crossed, or after 5 s)
          else if (c.len - c.pos < 12) { n.res = c; n.resT = sigT + 5; } }
        if (lead) room = Math.min(room, lead.pos - 6.5 - c.pos);
        if (plc) { const ux = (c.b.x - c.a.x) / c.len, uy = (c.b.y - c.a.y) / c.len, rx = S.x - c.a.x, ry = S.y - c.a.y, ps = rx * ux + ry * uy, la = rx * uy - ry * ux; if (ps > c.pos + 1 && ps - c.pos < 45 && Math.abs(la - c.lat) < 2.0) room = Math.min(room, ps - c.pos - 6.5); }
        if (WK.length && c.wx !== undefined && Math.abs(c.wx - S.x) < 180 && Math.abs(c.wy - S.y) < 180) { const ux = (c.b.x - c.a.x) / c.len, uy = (c.b.y - c.a.y) / c.len, hl = SOLID.DIM[c.k || 0][0]; let wr = 1e9;      // 20.11.2026: people on the lane ahead (walkers, the player on foot): stop 1.6 m short of them
          for (const w of WK) { const rx = w.x - c.a.x, ry = w.y - c.a.y, ps = rx * ux + ry * uy; if (ps > c.pos + hl - 0.3 && ps - c.pos < 30 && Math.abs(rx * uy - ry * ux - c.lat) < 1.4) wr = Math.min(wr, ps - c.pos - hl - 1.6); }
          if (wr < 1e9) { if ((c.wb = (c.wb || 0) + dt) < 9) room = Math.min(room, wr); else if (c.wb > 15) c.wb = 0; } else if (c.wb > 0) c.wb = Math.max(0, c.wb - dt * 2); }      /* held up for 9 s: drive on for 6 s, the people step out of the way (SOLID.npcStep) */
        room = Math.max(room, 0); const tv = Math.min(c.v, Math.sqrt(7 * room));
        c.s = tv > c.s ? Math.min(tv, c.s + 2.5 * dt) : Math.max(tv, c.s - 7 * dt); if (room < 0.02) c.s = 0;
        c.mv = Math.min(c.s * dt, room); c.pos += c.mv; lead = c; } }
    for (let i = 0; i < N; i++) { const c = cars[i]; let dx = c.b.x - c.a.x, dy = c.b.y - c.a.y, len = Math.hypot(dx, dy) || 1;
      c.t += c.mv / len;
      if (c.pk) { const P = c.pk;                                                // 0 pulling in, 1 parked, 2 pulling out
        if (P.ph === 0) { const rem = (P.t1 - c.t) * len, tv = Math.min(c.v, Math.sqrt(Math.max(0, 5 * rem)) + 0.2); c.s += Math.max(-6 * dt, Math.min(2 * dt, tv - c.s)); c.t = Math.min(P.t1, c.t + c.s * dt / len); if (rem < 14) c.lat += (P.lat - c.lat) * Math.min(1, dt * 1.6);
          if (rem < 0.25) { c.s = 0; c.lat = P.lat; P.ph = 1; P.T = 35 + rnd() * 50; P.e = 0; P.two = rnd() < 0.4; P.door = doorPool.pop() || mkDoor(); P.door.mat.color.setHex(c.paint || 0x8b9096); } }
        else if (P.ph === 1) { P.e += dt; P.ang = P.e < 0.6 ? P.e / 0.6 : P.e < 2.6 ? 1 : P.e < 3.2 ? (3.2 - P.e) / 0.6 : 0;                 // door opens 0.6 s, people out, closes after 2.6 s
          if (P.e >= 0.6 && !P.out) { P.out = true; if (window.__npc && window.__npc.arrive) window.__npc.arrive(P.x, P.y); }
          if (P.e > 3.2 && P.door) { P.door.g.visible = false; doorPool.push(P.door); P.door = null; }
          if ((P.T -= dt) < 0) P.ph = 2; }
        else { c.lat += (1.7 - c.lat) * Math.min(1, dt * 1.2) - 0.02 * dt; if (c.lat <= 1.75) { c.lat = 1.7; c.pk = null; c.s = 0; } } }
      if (c.t >= 1) { let opts = c.b.nb.filter(n => n !== c.a && may(c.b, n)); if (!opts.length) opts = c.b.nb.filter(n => may(c.b, n)); const nx = opts.length ? pickRoad(c.b, opts) : c.a, tq = Q.get(c.b.id * 65536 + nx.id);
        if (tq && (c.blk = (c.blk || 0) + dt) < 8 && tq.some(o => o !== c && o.a === c.b && o.pos < 6.5)) { c.t = 1; c.s = 0; }      // the start of the next street is taken: wait at the corner (at most 8 s) instead of driving into that car
        else { c.blk = 0; c.a = c.b; c.b = nx; c.t = 0; if (c.a.res === c) c.a.resT = sigT + 0.9;
        if (c.yr && busyRd(c.a, c.b) === 1 && Math.hypot(c.a.x - S.x, c.a.y - S.y) > 170) { const e = yrE[Math.floor(rnd() * yrE.length)]; if (Math.hypot(e[0].x - S.x, e[0].y - S.y) > 120) { c.a = e[0]; c.b = e[1]; c.s = c.v; } }   // a Yrjönkatu regular that has strayed returns there, out of sight
        // parking (19.11.2026): now and then a car near the player pulls in to the kerb half-way along the new street (if there is a kerb 3.8-9 m from the
        // lane centre line and no parked car in the spot), people get out (window.__npc.arrive) and it drives on after 35-85 s
        if (!c.pk && !c.yr && !(c.k > 2) && ROAD.on && typeof PARKED !== 'undefined' && rnd() < 0.06) { const ex = c.b.x - c.a.x, ey = c.b.y - c.a.y, el = Math.hypot(ex, ey), mx = c.a.x + ex * 0.55, my = c.a.y + ey * 0.55;
          if (el > 30 && !c.b.sig && inCore(mx, my) && Math.hypot(mx - S.x, my - S.y) < 170) { const vx = ex / el, vy = ey / el; let dk = 0, seen = false; for (let q = 0.5; q <= 9; q += 0.5) { if (ROAD.asphAt(mx + vy * q, my - vx * q)) { seen = true; continue; } if (seen) dk = q; break; }
            const tx = mx + vy * (dk - 1.2), ty = my - vx * (dk - 1.2); let free = dk >= 3.8; if (free) for (let k = 0; k < PARKED.length; k += 4) if (Math.hypot(PARKED[k] / 10 - tx, PARKED[k + 1] / 10 - ty) < 5.5) { free = false; break; }
            if (free) for (const o of cars) if (o.pk && Math.hypot(o.pk.x - tx, o.pk.y - ty) < 9) { free = false; break; }
            if (free) c.pk = { ph: 0, t1: 0.55, lat: dk - 1.2, x: mx + vy * (dk + 1.0), y: my - vx * (dk + 1.0), T: 0 }; } }
        dx = c.b.x - c.a.x; dy = c.b.y - c.a.y; len = Math.hypot(dx, dy) || 1; } }
      const ux = dx / len, uy = dy / len, x = c.a.x + dx * c.t + uy * c.lat, y = c.a.y + dy * c.t - ux * c.lat;        // keep to the right-hand lane
      let d = Math.atan2(ux, uy) - c.yaw; d = Math.atan2(Math.sin(d), Math.cos(d)); c.yaw += d * Math.min(1, dt * 6);
      const bz = bridgeZ(x, y); p3.set(x, 0.09 + bz + (bz ? 0 : roadDZ(x, y)), -y); q4.setFromAxisAngle(UP, -c.yaw); m4.compose(p3, q4, s3); if (typed) parts[c.k].setMatrixAt(c.j, m4); else for (const q of parts) q.setMatrixAt(i, m4); c.wx = x; c.wy = y; c.st = c.s < 0.05 && !c.pk ? (c.st || 0) + dt : 0;
      if (c.st > 30 && Math.hypot(x - S.x, y - S.y) > 120) { const a = list[Math.floor(rnd() * list.length)]; if (Math.hypot(a.x - S.x, a.y - S.y) > 150) { c.a = a; c.b = a.nb[Math.floor(rnd() * a.nb.length)]; c.t = 0; c.st = 0; c.blk = 0; c.s = c.v; } }   /* stood 30 s in a jam out of the player's sight: start again somewhere else */
      if (c.pk && c.pk.door) { const D = c.pk.door, a = (c.pk.ang || 0) * 1.15; D.g.position.copy(p3); D.g.quaternion.copy(q4); D.g.visible = true; D.R.rotation.y = -a; D.L.rotation.y = c.pk.two ? a : 0; D.oR.visible = a > 0.02; D.oL.visible = c.pk.two && a > 0.02; } }
    for (const q of parts) q.instanceMatrix.needsUpdate = true;
    if (sigUpd) sigUpd();
  };
  // the signal posts: one on the right-hand kerb at each stop line (lamps face the arriving cars; a red/green pair faces across the street
  // for people on foot). Built a little after the start, when roads.js has told which streets are one-way.
  let sigUpd = null, sigTry = 0;
  const sigBuild = () => { if (!window.__roads && ++sigTry < 12) { setTimeout(sigBuild, 3000); return; }      // wait for roads.js: the pavement mask says where the kerb is
    for (const n of list) { if (!n.sig) continue;
      for (const a of n.nb) { if ((a.sig && a.sig.j === n.sig.j) || (!n.sig.mid && !may(a, n))) continue;
        const dx = n.x - a.x, dy = n.y - a.y, len = Math.hypot(dx, dy) || 1, ux = dx / len, uy = dy / len, b = Math.min(SR, len);
        let sx = n.x - ux * SR, sy = n.y - uy * SR;                                              // from the stop line sideways across the asphalt: the post stands
        const kerb = sg => { let seen = false; for (let q = 0.5; q <= 25; q += 0.5) { if (ROAD.asphAt(sx + sg * uy * q, sy - sg * ux * q)) { seen = true; continue; } if (seen && q >= 2) return q + 0.7; } return 0; };   // 0.7 m past the kerb (pavement, a grass median or an island)
        let dr = kerb(1); if (!dr) { sx -= ux * 5; sy -= uy * 5; dr = kerb(1); }                // still inside the junction: look 5 m further back
        const dl = kerb(-1), d = dr || 4.6, px = sx + uy * d, py = sy - ux * d;
        sigPoles.push({ n, a, x: px, y: py, ux, uy, pv: ROAD.paveAt(px, py), ty: dr > 6.2 ? 'uloke' : 'yhdistelma' });      // wide carriageway: the mast-arm post
        if (dl) { const qx = sx - uy * dl, qy = sy + ux * dl; sigPoles.push({ n, a, x: qx, y: qy, ux: -ux, uy: -uy, pv: ROAD.paveAt(qx, qy), ty: 'jalankulkija' }); } } }   // across the street a short post for people walking the other way
    if (!sigPoles.length) return;
    // the owner's Blender posts (tools/props/porikopteri_liikennevalot.py -> liikennevalot.js): origin at the foot, the vehicle head faces +Z (the
    // arriving car), the carriageway is on -X. Every lamp is its own node with onColor / offColor: one instanced mesh per lamp, coloured per post.
    import('./liikennevalot.js').then(K => { const TY = Object.keys(K.default), sets = {}; let left = TY.length;
      TY.forEach(ty => { const bin = atob(K.default[ty]), buf = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
        new GLTFLoader().parse(buf.buffer, '', gl => { const ps = sigPoles.filter(p => p.ty === ty), lamps = []; gl.scene.updateMatrixWorld(true);
          if (ps.length) gl.scene.traverse(o => { if (!o.isMesh) return; const g = o.geometry.clone(); g.applyMatrix4(o.matrixWorld); const lm = /^(Veh|Over|Ped)_(Red|Yellow|Green)$|^Button_Light$/.test(o.name);
            const im = new THREE.InstancedMesh(g, lm ? new THREE.MeshBasicMaterial({ color: 0xffffff }) : o.material, ps.length); scene.add(im);
            ps.forEach((p, i) => { const bz = bridgeZ(p.x, p.y); p3.set(p.x, (p.pv ? ROAD.pave - ROAD.asph : 0) + 0.09 + bz + (bz ? 0 : roadDZ(p.x, p.y)), -p.y); q4.setFromAxisAngle(UP, -Math.atan2(p.ux, p.uy)); m4.compose(p3, q4, s3); im.setMatrixAt(i, m4); });
            if (lm) { const u = o.userData, k = o.name.split('_'); lamps.push({ im, on: new THREE.Color().setRGB(...u.onColor), off: new THREE.Color().setRGB(...u.offColor), ped: k[0] === 'Ped' || k[0] === 'Button', want: k[0] === 'Button' ? 3 : k[1] === 'Red' ? 2 : k[1] === 'Yellow' ? 1 : 0 }); } });
          sets[ty] = { ps, lamps }; if (!--left) sigUpd = () => { for (const ty in sets) { const { ps, lamps } = sets[ty]; if (!lamps.length) continue;
            ps.forEach((p, i) => { const jk = p.ty === 'jalankulkija', st = sigState(p.n, p.a), go = pedGo(p.n, p.a);
              for (const L of lamps) L.im.setColorAt(i, (L.ped ? (L.want === 0 ? go : !go) : (!jk && st === L.want)) ? L.on : L.off); });
            for (const L of lamps) L.im.instanceColor.needsUpdate = true; } }; }, () => { left--; }); }); }).catch(() => {});
  }; setTimeout(sigBuild, 6000);
  cars.update(0);
  // Blender-made car models: the traffic switches to them, and one is parked on top of every car found in the aerial image
  // car models car0..car6 (hatchback, saloon, SUV, van, box lorry, flatbed lorry, refuse lorry); types missing from cars.js are skipped
  loadModel('cars', root => {
    const geo = ['car0', 'car1', 'car2', 'car3', 'car4', 'car5', 'car6'].map((k, i) => (root.getObjectByName(k) || root.getObjectByName('car' + (i % 3))).geometry), has = k => !!root.getObjectByName('car' + k), cm = new THREE.MeshLambertMaterial({ vertexColors: true }), tc = new THREE.Color();
    // vertex-colour alpha says what the paint colour may tint: 1 = bodywork, 0 = glass, tyres, lamps, grille (blender/cars.py); older models have alpha 1 everywhere
    if (geo[0].attributes.color && geo[0].attributes.color.itemSize === 4) cm.onBeforeCompile = sh => { sh.vertexShader = sh.vertexShader.replace('#include <color_vertex>', THREE.ShaderChunk.color_vertex.replace('vColor.xyz *= instanceColor.xyz;', 'vColor.xyz *= mix( vec3( 1.0 ), instanceColor.xyz, color.a );')); };
    const pick = (v, w) => { let a = 0; for (let k = 0; k < w.length; k++) { a += w[k]; if (v < a) return k; } return 0; };
    const TW = [0.27, 0.22, 0.16, 0.17, 0.08, 0.06, 0.04].map((w, k) => has(k) ? w : 0), tws = TW.reduce((a, b) => a + b, 0); TW.forEach((w, k) => TW[k] = w / tws); const LORRY = [0xf4f4f2, 0xf4f4f2, 0xd9dcdf, 0x2f5f9e, 0xb52a22, 0x2e6b45, 0xe9c33a];
    const cnt = [0, 0, 0, 0, 0, 0, 0]; for (const c of cars) { c.k = pick(rnd(), TW); c.j = cnt[c.k]++; }
    const tms = geo.map((g, k) => new THREE.InstancedMesh(g, cm, Math.max(1, cnt[k])));
    cars.forEach((c, i) => { if (c.k >= 4) tc.setHex(LORRY[Math.floor(rnd() * LORRY.length)]); else body.getColorAt(i, tc); tms[c.k].setColorAt(c.j, tc); });
    tms.forEach(t => { t.frustumCulled = false; scene.add(t); });
    scene.remove(body, cab, base); parts = tms; typed = true; cars.update(0);
    const lists = [[], [], [], []], n = PARKED.length / 4, hs = (i, k) => { let x = (i * 2654435761 + k * 40503) >>> 0; x ^= x >>> 15; x = Math.imul(x, 2246822519) >>> 0; x ^= x >>> 13; return (x >>> 0) / 4294967296; };
    // owner 18.11.2026: no parked car inside a house (the aerial-photo car spots predate some walls, and the houses are not exactly where the photo has them)
    const clear = i => { const x = PARKED[i * 4] / 10, y = PARKED[i * 4 + 1] / 10, a = PARKED[i * 4 + 2] / 100, sn = Math.sin(a), cs = Math.cos(a), g = TZs(x, y);
      for (const [f, r] of [[0, 0], [2.3, 0.95], [2.3, -0.95], [-2.3, 0.95], [-2.3, -0.95]]) if (bldTopAt(x + sn * f + cs * r, y + cs * f - sn * r) > g + 1.2) return false;
      return !(ROAD.on && inCore(x, y) && ROAD.paveAt(x, y)); };
    for (let i = 0; i < n; i++) if (clear(i)) lists[pick(hs(i, 1), [0.36, 0.28, 0.24, 0.12])].push(i);
    lists.forEach((ids, k) => { const im = new THREE.InstancedMesh(geo[k], cm, ids.length);
      ids.forEach((ci, j) => { const yaw = PARKED[ci * 4 + 2] / 100, sc = (k === 3 ? 0.9 : 0.94) + hs(ci, 3) * 0.08;      // heading already faces the traffic (kerbside) or the bay (car parks)
        p3.set(PARKED[ci * 4] / 10, 0.08 + roadDZ(PARKED[ci * 4] / 10, PARKED[ci * 4 + 1] / 10), -PARKED[ci * 4 + 1] / 10); q4.setFromAxisAngle(UP, -yaw); s3.set(sc, sc, sc); im.setMatrixAt(j, m4.compose(p3, q4, s3));
        tc.setHex(PARKED[ci * 4 + 3]); const mxc = Math.max(tc.r, tc.g, tc.b); if (mxc < 0.05) tc.setRGB(0.05, 0.055, 0.06); im.setColorAt(j, tc);
        (window.__parked || (window.__parked = [])).push({ x: PARKED[ci * 4] / 10, y: PARKED[ci * 4 + 1] / 10, yaw, hex: tc.getHex(), im, j, k, gone: false }); });      /* for takeCar: the player can borrow a parked car */
      s3.set(1, 1, 1); im.frustumCulled = false; scene.add(im); });
    window.__cars = n;
  });
}

