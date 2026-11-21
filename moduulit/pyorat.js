// moduulit/pyorat.js – siirretty pääskriptistä (src/js/156_pyorat.js) omaksi moduulikseen 21.11.2026.
// Pääskriptin muuttujat tulevat oliossa P (getterit pitävät ne ajan tasalla); kirjastot ja data tuodaan suoraan.
// Kutsu ja P:n sisältö: src/js/156_pyorat.js. Uusi riippuvuus pääskriptiin → lisää se sinne P-olioon.
import * as THREE from '../three.module.min.js';
import CITY from '../city.js';
import { GLTFLoader } from '../GLTFLoader.js';

// 20.11.2026 (owner: "bicycles on the market square, several parked, the same in front of SAMK, single bikes around the centre"). Model: pyora.js. All bikes
// are drawn as instances (one InstancedMesh per mesh of the model, frame paint tinted per bike). Racks: rows 0.62 m apart on free paving round Kauppatori
// (not near the helipad) and outside the wall of the SAMK campus that faces Satakunnankatu. Singles: seeded random spots on pavement within 2 m of a house
// wall, parked along the wall. Positions are found once from the game's own masks, so nothing stands on a carriageway or inside a house.
export default function kaynnista(P) {
{
  const few = false; let sd = 4711;      /* 20.11.2026 (owner: no bicycle on the phone): phones get as many bikes as desktop - they are instances, the draw calls do not grow */ const rn = () => (sd = (sd * 16807) % 2147483647) / 2147483647;
  const PAINTS = [0xb3261e, 0x1f4e8c, 0x2e6b45, 0xe9c33a, 0x1b1b1d, 0xe8e8e4, 0x7a3b8f, 0xd9772b, 0x4aa3c7, 0x8b9096];
  const bld = (x, y) => P.bldTopAt(x, y) > P.TZs(x, y) + 1.2;
  const free = (x, y) => !bld(x, y) && !P.inRiver(x, y) && !(P.ROAD.on && P.inCore(x, y) && P.ROAD.asphAt(x, y));
  const paved = (x, y) => free(x, y) && P.ROAD.paveAt(x, y);
  const B = []; window.__bikes = B;
  const add = (x, y, yaw) => { B.push({ i: B.length, gone: false, x, y, yaw, lean: 0.1 + rn() * 0.08, hex: PAINTS[Math.floor(rn() * PAINTS.length)], st: (rn() - 0.5) * 0.9 }); };
  const rack = (x, y, dir, n) => { const ux = Math.sin(dir), uy = Math.cos(dir); let k = 0; for (let i = 0; i < n; i++) { if (rn() < 0.18) continue; const px = x + ux * (i - n / 2) * 0.62, py = y + uy * (i - n / 2) * 0.62; if (!free(px, py)) continue; add(px, py, dir + Math.PI / 2 + (rn() - 0.5) * 0.22 + (rn() < 0.3 ? Math.PI : 0)); k++; } return k; };
  const build = gl => {
    /* market square: rows on the rim, at least 16 m from the helipad and 22 m from each other */
    const T = CITY.places.find(p => p.n === 'Kauppatori') || { x: 64, y: 65 }, R = []; for (let a = 0; a < 12 && R.length < (few ? 3 : 5); a++) { const an = (a * 5 % 12) * Math.PI / 6;
      for (let r = 38; r >= 18; r -= 2) { const x = T.x + Math.sin(an) * r, y = T.y + Math.cos(an) * r; if (!paved(x, y) || Math.hypot(x - P.HOME.x, y - P.HOME.y) < 16 || R.some(q => Math.hypot(q[0] - x, q[1] - y) < 22)) continue;
        let okRow = true; for (const d of [-2.5, 2.5]) if (!paved(x + Math.cos(an) * d, y - Math.sin(an) * d)) okRow = false; if (!okRow) continue; R.push([x, y]); rack(x, y, an + Math.PI / 2, few ? 6 : 9); break; } }
    /* SAMK: out of the campus footprint towards Satakunnankatu, two rows along that wall */
    const Sm = CITY.named.find(p => /SAMK-kampus/.test(p.n)); if (Sm) { const tx = -400, ty = -800, l = Math.hypot(tx - Sm.x, ty - Sm.y), dx = (tx - Sm.x) / l, dy = (ty - Sm.y) / l; let r = 4; while (r < 140 && bld(Sm.x + dx * r, Sm.y + dy * r)) r += 1;
      if (r < 140) { const dir = Math.atan2(dx, dy) + Math.PI / 2, bx = Sm.x + dx * (r + 2.2), by = Sm.y + dy * (r + 2.2); B.samk = [bx, by]; rack(bx + Math.sin(dir) * 5, by + Math.cos(dir) * 5, dir, few ? 7 : 12); rack(bx - Math.sin(dir) * 5, by - Math.cos(dir) * 5, dir, few ? 7 : 12); } }
    /* singles: on pavement, a house wall within 2 m, parked along the wall; not two within 14 m */
    const want = few ? 22 : 55, S1 = []; for (let i = 0; i < 9000 && S1.length < want; i++) { const x = (rn() * 2 - 1) * 620, y = -330 + (rn() * 2 - 1) * 520; if (!P.inCore(x, y) || !paved(x, y)) continue; let wa = -1; for (let a = 0; a < 8; a++) if (bld(x + Math.sin(a * Math.PI / 4) * 1.7, y + Math.cos(a * Math.PI / 4) * 1.7)) { wa = a * Math.PI / 4; break; }
      if (wa < 0 || bld(x + Math.sin(wa) * 0.7, y + Math.cos(wa) * 0.7) || S1.some(q => Math.hypot(q[0] - x, q[1] - y) < 14) || Math.hypot(x - P.HOME.x, y - P.HOME.y) < 14) continue; S1.push([x, y]); add(x, y, wa + Math.PI / 2 + (rn() < 0.5 ? Math.PI : 0)); }
    /* instances: every mesh of the model once, placed by bike matrix x the mesh's own matrix under Bike */
    const root = gl.scene; root.updateMatrixWorld(true); const steer = root.getObjectByName('Steering'), inv = new THREE.Matrix4().copy(root.matrixWorld).invert(), m4 = new THREE.Matrix4(), bm = new THREE.Matrix4(), sm = new THREE.Matrix4(), e = new THREE.Euler(0, 0, 0, 'YXZ'), q = new THREE.Quaternion(), p = new THREE.Vector3(), s1 = new THREE.Vector3(1, 1, 1), col = new THREE.Color();
    const meshes = []; root.traverse(o => { if (o.isMesh) { let st = false, pad = false; for (let a = o; a; a = a.parent) { if (a === steer) st = true; if (a.name === 'RackPad') pad = true; } if (!pad) meshes.push({ o, st }); } });      /* the rack pad (passenger seat) only on the bike being ridden */
    for (const { o, st } of meshes) { const paint = o.material && o.material.name === 'BikePaint', mat = o.material.clone(); if (paint) mat.color.setRGB(1, 1, 1); const im = new THREE.InstancedMesh(o.geometry, mat, B.length); im.frustumCulled = false;
      B.forEach((b, i) => { const z = (P.carGround(b.x, b.y) ?? P.TZs(b.x, b.y)) - P.TZs(b.x, b.y) + 0.01; p.set(b.x, z, -b.y); e.set(0, Math.PI - b.yaw, b.lean); q.setFromEuler(e); bm.compose(p, q, s1);      /* the terrain height comes from the lift shader, as for the parked cars */
        if (st) { sm.copy(steer.matrixWorld).premultiply(inv); const lo = new THREE.Matrix4().copy(steer.matrixWorld).invert().multiply(o.matrixWorld), ry = new THREE.Matrix4().makeRotationY(b.st); m4.copy(bm).multiply(sm).multiply(ry).multiply(lo); }      /* handlebars turned a little, each bike its own way */
        else m4.copy(bm).multiply(new THREE.Matrix4().copy(inv).multiply(o.matrixWorld)); im.setMatrixAt(i, m4); if (paint) im.setColorAt(i, col.setHex(b.hex)); });
      im.instanceMatrix.needsUpdate = true; if (im.instanceColor) im.instanceColor.needsUpdate = true; P.scene.add(im); (B.ims || (B.ims = [])).push(im); }
    B.racks = R; };
  const go = gl => { if (!window.__roads && (go.n = (go.n || 0) + 1) < 20) { setTimeout(() => go(gl), 3000); return; } try { build(gl); } catch (e) { console.warn('bikes', e); } };
  import('../pyora.js').then(K => { const bin = atob(K.default), buf = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i); new GLTFLoader().parse(buf.buffer, '', go, () => {}); }).catch(() => {});
}
}
