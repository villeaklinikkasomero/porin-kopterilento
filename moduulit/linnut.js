// moduulit/linnut.js – siirretty pääskriptistä (src/js/153_linnut.js) omaksi moduulikseen 21.11.2026.
// Pääskriptin muuttujat tulevat oliossa P (getterit pitävät ne ajan tasalla); kirjastot ja data tuodaan suoraan.
// Kutsu ja P:n sisältö: src/js/153_linnut.js. Uusi riippuvuus pääskriptiin → lisää se sinne P-olioon.
import * as THREE from '../three.module.min.js';
import { GLTFLoader } from '../GLTFLoader.js';

// 20.11.2026 (owner: "add these birds; pigeons in small flocks, gulls alone or in pairs"). Models: linnut.js (tools/props/porikopteri_linnut.py; clips Fly, Glide,
// Idle, Walk, Peck). Ground groups (pigeons 4-7, gulls 1-2) stand on pavement near the player, walk about and peck; when the player comes close (on foot 4.5 m,
// car 9 m, low helicopter 16 m) the group takes wing and lands 30-70 m away. Besides them one or two gulls circle overhead. Groups left over 140 m behind move
// to a new spot near the player; birds further than 90 m are not animated.
export default function kaynnista(P) {
{
  const B = { G: [], A: [], M: null, on: false }; window.__birds = B;
  const few = matchMedia('(pointer: coarse)').matches, R = Math.random, SC = 1.25, DEG = Math.PI / 180;
  const clone = src => { const map = new Map(), c = src.clone(); const wk = (a, b) => { map.set(a, b); for (let i = 0; i < a.children.length; i++) wk(a.children[i], b.children[i]); }; wk(src, c);
    src.traverse(o => { if (o.isSkinnedMesh) { const d = map.get(o); d.skeleton = new THREE.Skeleton(o.skeleton.bones.map(b => map.get(b)), o.skeleton.boneInverses); d.bind(d.skeleton, o.bindMatrix); } }); return c; };
  import('../linnut.js').then(K => { const M = {}; let left = 2;
    for (const k of ['pulu', 'lokki']) { const bin = atob(K.default[k]), buf = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
      new GLTFLoader().parse(buf.buffer, '', gl => { gl.scene.traverse(q => { q.userData.noT = true; q.frustumCulled = false; if (q.isMesh && q.material) q.material.userData.noT = true; }); M[k] = gl; if (!--left) B.M = M; }, () => {}); } }).catch(() => {});
  const mk = sp => { const g = new THREE.Group(), root = clone(B.M[sp].scene); g.add(root); g.scale.setScalar(SC); g.rotation.order = 'YXZ'; g.userData.noT = true; P.scene.add(g); const mix = new THREE.AnimationMixer(root), act = {};
    for (const c of B.M[sp].animations) act[c.name] = mix.clipAction(c); act.Idle.play(); mix.update(R() * 3); return { sp, g, mix, act, cur: 'Idle', x: 0, y: 0, z: 0, hd: R() * 360, t: R() * 2, tx: null, ty: 0, fl: null }; };
  const anim = (b, n) => { if (b.cur === n) return; b.act[n].reset().play(); b.act[b.cur].crossFadeTo(b.act[n], 0.18, false); b.cur = n; };
  const gz = (x, y) => P.carGround(x, y) ?? P.TZs(x, y);
  const ok1 = (x, y) => P.ROAD.paveAt(x, y) && !P.ROAD.asphAt(x, y) && !P.inRiver(x, y) && !(P.bldTopAt(x, y) > P.TZs(x, y) + 1.2);
  const ok = (x, y) => ok1(x, y) && ok1(x + 1.6, y) && ok1(x - 1.6, y) && ok1(x, y + 1.6) && ok1(x, y - 1.6);
  const spot = (x, y, r0, r1, ax, ay) => { for (let i = 0; i < 40; i++) { const a = R() * 6.2832, r = r0 + R() * (r1 - r0), qx = x + Math.sin(a) * r, qy = y + Math.cos(a) * r;      /* a free piece of pavement r0..r1 from (x, y), not towards (ax, ay) */
      if (ax !== undefined && (qx - x) * (ax - x) + (qy - y) * (ay - y) > 0) continue; if (ok(qx, qy)) return [qx, qy]; } return null; };
  const put = b => { b.g.position.set(b.x, b.z, -b.y); b.g.rotation.y = Math.PI - b.hd * DEG; };
  const settle = (f, x, y) => { f.cx = x; f.cy = y; f.st = 'g'; const rr = 0.9 + Math.sqrt(f.m.length) * 0.7; for (const b of f.m) { const a = R() * 6.2832, r = R() * rr; b.x = x + Math.sin(a) * r; b.y = y + Math.cos(a) * r; b.z = gz(b.x, b.y); b.fl = null; b.tx = null; b.t = R() * 2; b.g.rotation.x = b.g.rotation.z = 0; anim(b, 'Idle'); put(b); } };
  const group = (sp, n, px, py) => { const s = spot(px, py, 14, 85); if (!s) return; const f = { sp, m: [], cx: 0, cy: 0, st: 'g', rr: 0.9 + Math.sqrt(n) * 0.7 }; for (let i = 0; i < n; i++) f.m.push(mk(sp)); settle(f, s[0], s[1]); B.G.push(f); };
  const rise = (f, px, py) => { const d = spot(f.cx, f.cy, 30, 70, px, py) || spot(f.cx, f.cy, 30, 70) || [f.cx, f.cy], gull = f.sp === 'lokki'; f.st = 'f'; let k = 0;
    const sx = (R() - 0.5) * 30, sy = (R() - 0.5) * 30;
    for (const b of f.m) { const a = R() * 6.2832, r = R() * f.rr, x1 = d[0] + Math.sin(a) * r, y1 = d[1] + Math.cos(a) * r, L = Math.hypot(x1 - b.x, y1 - b.y) + 20;
      b.fl = { x0: b.x, y0: b.y, z0: b.z, x1, y1, z1: gz(x1, y1), mx: (b.x + x1) / 2 + sx, my: (b.y + y1) / 2 + sy, T: L / (gull ? 10 : 8.5), t: -0.08 * k++ - R() * 0.15, h: (gull ? 11 : 6) + R() * 5 }; }
    f.cx = d[0]; f.cy = d[1]; };
  const soar = (px, py) => { const n = R() < 0.5 ? 1 : 2, a = { m: [], cx: px + (R() - 0.5) * 120, cy: py + (R() - 0.5) * 120, r: 22 + R() * 22, alt: 24 + R() * 16, a: R() * 6.2832, dir: R() < 0.5 ? 1 : -1, t: R() * 9 };
    for (let i = 0; i < n; i++) { const b = mk('lokki'); anim(b, 'Glide'); a.m.push(b); } B.A.push(a); };
  window.__birdTick = dt => { if (!B.M || !window.__roads || dt <= 0) return; const walk = P.WALK.on && !P.WALK.in, px = P.WALK.on ? P.WALK.x : P.S.x, py = P.WALK.on ? P.WALK.y : P.S.y;
    if (!B.on) { B.on = true; for (let i = 0; i < (few ? 2 : 4); i++) group('pulu', 4 + Math.floor(R() * 4), px, py); for (let i = 0; i < (few ? 1 : 2); i++) group('lokki', R() < 0.55 ? 1 : 2, px, py); for (let i = 0; i < (few ? 1 : 2); i++) soar(px, py); }
    const scare = P.WALK.in ? 0 : walk ? 4.5 : P.VEH === 'car' ? 9 : P.S.alt - P.TZs(px, py) < 14 ? 16 : 0;
    for (const f of B.G) { const d = Math.hypot(f.cx - px, f.cy - py);
      if (d > 140 && f.st === 'g') { const s = spot(px, py, 30, 90); if (s) settle(f, s[0], s[1]); continue; }
      if (f.st === 'g' && scare && d < scare + f.rr) rise(f, px, py);
      const live = d < 90; let air = 0;
      for (const b of f.m) {
        if (b.fl) { const q = b.fl; q.t += dt; if (q.t < 0) { air++; continue; } const u = Math.min(1, q.t / q.T), e = u * u * (3 - 2 * u), i = 1 - e;
          const nx = i * i * q.x0 + 2 * i * e * q.mx + e * e * q.x1, ny = i * i * q.y0 + 2 * i * e * q.my + e * e * q.y1; if (Math.hypot(nx - b.x, ny - b.y) > 1e-3) b.hd = Math.atan2(nx - b.x, ny - b.y) / DEG;
          b.x = nx; b.y = ny; b.z = q.z0 + (q.z1 - q.z0) * e + Math.sin(Math.PI * u) * q.h; b.g.rotation.x = -0.45 * Math.cos(Math.PI * u) * Math.sin(Math.PI * Math.min(1, u * 4)); anim(b, f.sp === 'lokki' && u > 0.35 && u < 0.78 ? 'Glide' : 'Fly'); put(b);
          if (u >= 1) { b.fl = null; b.g.rotation.x = 0; b.z = q.z1; b.tx = null; b.t = 0.4 + R(); anim(b, 'Idle'); put(b); } else air++; }
        else if (live && f.st === 'g') { if (b.tx !== null) { const dx = b.tx - b.x, dy = b.ty - b.y, l = Math.hypot(dx, dy), v = (f.sp === 'lokki' ? 0.34 : 0.24) * dt;
            if (l < v + 0.02) { b.tx = null; b.t = R() < 0.6 ? 1.33 : 1 + R() * 3; anim(b, b.t === 1.33 ? 'Peck' : 'Idle'); } else { b.x += dx / l * v; b.y += dy / l * v; b.z = gz(b.x, b.y); b.hd = Math.atan2(dx, dy) / DEG; put(b); } }
          else if ((b.t -= dt) <= 0) { const a = R() * 6.2832, r = R() * f.rr, tx = f.cx + Math.sin(a) * r, ty = f.cy + Math.cos(a) * r; if (ok1(tx, ty)) { b.tx = tx; b.ty = ty; anim(b, 'Walk'); } else b.t = 0.5; } }
        if (live || b.fl) b.mix.update(dt); }
      if (f.st === 'f' && !air) f.st = 'g'; }
    for (const a of B.A) { const d = Math.hypot(a.cx - px, a.cy - py); if (d > 150) { a.cx += (px - a.cx) / d * 16 * dt; a.cy += (py - a.cy) / d * 16 * dt; }      /* left behind: the circle drifts after the player */
      a.t += dt; a.a += a.dir * 8.5 / a.r * dt; const flap = a.t % 9 < 2.2;
      a.m.forEach((b, i) => { const an = a.a - i * a.dir * 0.55, r = a.r + i * 3; b.x = a.cx + Math.sin(an) * r; b.y = a.cy + Math.cos(an) * r; b.z = P.TZs(b.x, b.y) + a.alt + i * 2.5 + Math.sin(a.t * 0.35 + i) * 2.5;
        b.hd = (an + a.dir * Math.PI / 2) / DEG; b.g.rotation.z = a.dir * 0.38; anim(b, flap ? 'Fly' : 'Glide'); put(b); if (d < 260) b.mix.update(dt); }); } };
}
}
