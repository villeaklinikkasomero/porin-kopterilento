// ---------- Laskuvarjo päähahmolle (20.11.2026; omistaja: "laskuvarjo selässä sekä kaikki vaiheet ... mahdollisimman uskottava") ----------
// makeRig(root) -> rig. root = hahmo.js:n gltf.scene (Player / PlayerMesh / luut).
//   rig.gear          reppuvaljaat, kypärä, lasit ja korkeusmittari: SkinnedMesh, joka on sidottu HAHMON OMAAN luurankoon (varusteet.js,
//                     tehty tools/hahmo/varusteet.py:llä hahmon pinnan mukaan) -> seuraa jokaista animaatiota ilman omaa koodia
//   rig.canopy        THREE.Group kohtaukseen lisättäväksi (EI hahmon lapseksi): apuvarjo, yhdyspunos, sisäpussi, kantohihnat, punokset,
//                     liukuri, ohjauspunokset ja 9-kennoinen liitovarjo. Ryhmän asento = suhteellinen tuuli: +y kupua kohti, +z lentosuunta.
//   rig.wear(on)      varusteet näkyviin / pois (kypärän alla hiukset piilotetaan)
//   rig.state         { pc: 'stowed' | 'hand' | 'out', deploy: 0..1, brakeL, brakeR: 0..1, toggles: bool, collapse: 0..1 }
//   rig.update(t)     joka ruudussa hahmon animaation jälkeen (t sekunteina; lepatus ja huojunta)
// Avautumisen vaiheet deploy-arvon mukaan: 0–0.15 apuvarjo nousee ja täyttyy, yhdyspunos kiristyy · 0.15–0.35 sisäpussi nousee repusta,
// kantohihnat ja punokset purkautuvat suoriksi · 0.35–0.5 kupu tulee pussista kapeana nauhana, liukuri ylhäällä · 0.5–1 kennot täyttyvät
// keskeltä reunoille, liukuri valuu punoksia pitkin alas kantohihnoille, apuvarjo lysähtää kuvun taakse.
import * as THREE from '../three.module.min.js';
import GEAR from './varusteet.js';

const B64 = (s, T) => { const b = atob(s), u = new Uint8Array(b.length); for (let i = 0; i < b.length; i++) u[i] = b.charCodeAt(i); return new T(u.buffer); };
const V = THREE.Vector3, ease = x => x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x), lerp = (a, b, t) => a + (b - a) * t, seg = (x, a, b) => Math.max(0, Math.min(1, (x - a) / (b - a)));
// kupu: 9 kennoa, 17,5 m2 (190 ft2), punokset 4,6 m
const SPAN = 7.0, CHORD = 2.5, CELLS = 9, ARC = 5.2, LINE = 4.6, RISER = 0.52, TRIM = -0.16, BRIDLE = 2.6;
const XS = [0.035, 0.075, 0.14, 0.24, 0.38, 0.53, 0.68, 0.84, 1.0], COL = { navy: 0x0b1638, yel: 0xedb81a, wht: 0xf2f1ec, rib: 0xd9d8d2, blk: 0x101012, web: 0x121214 };
const CELLCOL = ['navy', 'navy', 'wht', 'yel', 'yel', 'yel', 'wht', 'navy', 'navy'];
const yt = x => 5 * 0.15 * (0.2969 * Math.sqrt(x) - 0.126 * x - 0.3516 * x * x + 0.2843 * x * x * x - 0.1015 * x * x * x * x);

export function makeRig(root) {
  let sk = null; const hair = [];
  root.traverse(o => { if (o.isSkinnedMesh) { if (!sk) sk = o; if (o.material && /^Hair/.test(o.material.name || '')) hair.push(o); } });
  const bones = sk.skeleton.bones, bi = GEAR.bones.map(n => bones.findIndex(b => b.name === n)), n = GEAR.count;
  // --- varusteet hahmon luurankoon ---
  const g = new THREE.BufferGeometry(), nn = B64(GEAR.n, Int8Array), cc = B64(GEAR.c, Uint8Array), ji = B64(GEAR.ji, Uint8Array), jw = B64(GEAR.jw, Uint8Array);
  const N = new Float32Array(n * 3), C = new Float32Array(n * 3), JI = new Uint16Array(n * 4), JW = new Float32Array(n * 4), tc = new THREE.Color();
  for (let i = 0; i < n * 3; i++) N[i] = nn[i] / 127;
  for (let i = 0; i < n; i++) { tc.setRGB(cc[i * 3] / 255, cc[i * 3 + 1] / 255, cc[i * 3 + 2] / 255, THREE.SRGBColorSpace); C[i * 3] = tc.r; C[i * 3 + 1] = tc.g; C[i * 3 + 2] = tc.b; }
  for (let i = 0; i < n * 4; i++) { JI[i] = Math.max(0, bi[ji[i]]); JW[i] = jw[i] / 255; }
  g.setAttribute('position', new THREE.BufferAttribute(B64(GEAR.p, Float32Array), 3)); g.setAttribute('normal', new THREE.BufferAttribute(N, 3)); g.setAttribute('color', new THREE.BufferAttribute(C, 3));
  g.setAttribute('skinIndex', new THREE.BufferAttribute(JI, 4)); g.setAttribute('skinWeight', new THREE.BufferAttribute(JW, 4)); g.setIndex(new THREE.BufferAttribute(B64(GEAR.i, Uint16Array), 1));
  const gear = new THREE.SkinnedMesh(g, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.7, metalness: 0.08, side: THREE.DoubleSide }));
  gear.name = 'Laskuvarjovarusteet'; gear.frustumCulled = false; gear.userData.noT = true; gear.material.userData.noT = true; sk.parent.add(gear); gear.bind(sk.skeleton, sk.bindMatrix);
  // ankkurit: lepoasennon piste luun lapseksi -> maailmanpaikka missä tahansa asennossa
  const anchor = (p, bone) => { const k = bones.findIndex(b => b.name === bone), o = new THREE.Object3D(); o.position.set(p[0], p[1], p[2]).applyMatrix4(sk.bindMatrix).applyMatrix4(sk.skeleton.boneInverses[k]); bones[k].add(o); return o; };
  const A = {}; for (const k in GEAR.anchors) A[k] = anchor(GEAR.anchors[k], GEAR.anchors[k][3]);
  const hand = {}; for (const sd of ['l', 'r']) { const hb = bones.find(b => b.name === 'hand_' + sd), mb = bones.find(b => b.name === 'middle_01_' + sd) || hb; const o = new THREE.Object3D(); mb.add(o); hand[sd] = o; }

  // --- kupu ja punokset (ryhmän omissa koordinaateissa: origo olkapäiden välissä, +y ylös kupuun, +z eteen, +x hahmon vasen) ---
  const grp = new THREE.Group(); grp.name = 'Laskuvarjo'; grp.userData.noT = true;
  const lam = c => { const m = new THREE.MeshLambertMaterial({ vertexColors: true, side: THREE.DoubleSide }); m.userData.noT = true; return m; };
  // kuvun pisteiden kuvaus: asema s (0..9 ripaa pitkin), jänne x (0..1), ylä-/alapinta, pullistus
  const CV = [], CI = [], CC = [], col3 = h => { tc.setHex(h); return [tc.r, tc.g, tc.b]; };
  const addV = (s, x, top, bulge, c) => { CV.push([s, x, top, bulge]); CC.push(...c); return CV.length - 1; };
  for (let k = 0; k < CELLS; k++) { const c = col3(COL[CELLCOL[k]]), cb = col3(COL[CELLCOL[k]]).map(v => v * 0.82), st = [0, 0.25, 0.5, 0.75, 1], T = [], Bm = [];
    for (const f of st) { const b = Math.sin(Math.PI * f); T.push(XS.map(x => addV(k + f, x, 1, b, c))); Bm.push(XS.map(x => addV(k + f, x, 0, b, cb))); }
    for (let a = 0; a < st.length - 1; a++) for (let j = 0; j < XS.length - 1; j++) { CI.push(T[a][j], T[a + 1][j], T[a + 1][j + 1], T[a][j], T[a + 1][j + 1], T[a][j + 1]); CI.push(Bm[a][j], Bm[a + 1][j + 1], Bm[a + 1][j], Bm[a][j], Bm[a][j + 1], Bm[a + 1][j + 1]); } }
  for (let r = 0; r <= CELLS; r++) { const c = col3(COL.rib), t = XS.map(x => addV(r, x, 1, 0, c)), b = XS.map(x => addV(r, x, 0, 0, c)); for (let j = 0; j < XS.length - 1; j++) CI.push(t[j], b[j], b[j + 1], t[j], b[j + 1], t[j + 1]); }      // rivat (näkyvät avoimesta etureunasta)
  const stab = []; for (const r of [0, CELLS]) { const c = col3(COL.navy), a = addV(r, 0.10, 0, 0, c), b = addV(r, 0.78, 0, 0, c), d = addV(r, 0.44, 2, 0, c); CI.push(a, b, d); stab.push(d); }       // vakaajat (top = 2: riippuu alaspäin)
  const cg = new THREE.BufferGeometry(), cp = new Float32Array(CV.length * 3); cg.setAttribute('position', new THREE.BufferAttribute(cp, 3)); cg.setAttribute('color', new THREE.BufferAttribute(new Float32Array(CC), 3)); cg.setIndex(CI);
  const cm = lam(); cm.onBeforeCompile = sh => { sh.fragmentShader = sh.fragmentShader.replace('#include <emissivemap_fragment>', '#include <emissivemap_fragment>\n\ttotalEmissiveRadiance += diffuseColor.rgb * 0.34;'); };      // ohut kangas päästää valoa läpi: alapinta ei jää mustaksi
  const canopy = new THREE.Mesh(cg, cm); canopy.frustumCulled = false; grp.add(canopy);
  // kuvun piste: s = ripa-asema, x = jänne, top; tila q = { sf span, tf paksuus, cf jänne, fl lepatus, t, bl, br, col romahdus }
  const P = new V(), cpt = (s, x, top, bulge, q, out) => { const u = (s / CELLS - 0.5), side = u < 0 ? 1 : 0;      // u < 0 = hahmon oikea (−x)? ei: x = −u·…, ks. alla
    const phi = u * (SPAN / ARC) * q.sf, cx = -Math.sin(phi) * ARC, cy = RISER + LINE - ARC + Math.cos(phi) * ARC;          // kaari: kaikki A-punokset yhtä pitkiä
    const br = lerp(q.br, q.bl, seg(-u, -0.12, 0.12)), th = yt(x) * q.tf * (1 + 0.22 * bulge * q.tf), up = top === 1 ? 1.55 * th + 0.035 * bulge * q.tf * Math.sin(Math.PI * Math.min(1, x * 1.3)) : top === 0 ? -0.42 * th + 0.02 * bulge * q.tf : -0.22;
    let zc = (0.33 - x) * CHORD * q.cf, yc = up * CHORD; if (x > 0.72) yc -= br * 0.34 * CHORD * ((x - 0.72) / 0.28) ** 2;                    // jarru vetää jättöreunaa alas
    const fl = q.fl * (0.10 * Math.sin(q.t * 23 + s * 2.1 + x * 9) + 0.07 * Math.sin(q.t * 31 + s * 5.3 - x * 6)); yc += fl; zc += fl * 0.6 * Math.cos(q.t * 17 + s);
    const ct = Math.cos(TRIM), sn = Math.sin(TRIM), z2 = zc * ct - yc * sn, y2 = zc * sn + yc * ct;                                             // trimmi: etureuna alempana
    out.set(cx - Math.sin(phi) * y2, cy + Math.cos(phi) * y2, 0.30 + z2);
    if (q.col > 0) { const a = -q.col * 1.9, y = out.y, z = out.z; out.y = lerp(y * Math.cos(a) - z * Math.sin(a), -1.28 + Math.abs(x - 0.5) * 0.3 + 0.12 * bulge, q.col * q.col);      /* ryhmän origo on olkapäiden korkeudella: maa on n. 1,4 m alempana */ out.z = y * Math.sin(a) + z * Math.cos(a); out.x *= 1 - 0.35 * q.col; }   // maassa: kaatuu taakse ja lysähtää
    return out; };
  // punokset: jokaiselta rivalta A B C D, haarat yhdistyvät; ohjauspunokset jättöreunasta
  const LA = [0.08, 0.30, 0.55, 0.80], lineN = (CELLS + 1) * 2 * 3 + 2 * (5 + 2) + 2 + 4, lp = new Float32Array(lineN * 6), lg = new THREE.BufferGeometry(); lg.setAttribute('position', new THREE.BufferAttribute(lp, 3));
  const lm = new THREE.LineBasicMaterial({ color: 0xe8e6de }); lm.userData.noT = true; const lines = new THREE.LineSegments(lg, lm); lines.frustumCulled = false; grp.add(lines);
  // kantohihnat, liukuri, sisäpussi: nelikulmioita, päivitetään joka ruutu
  const qg = new THREE.BufferGeometry(), QN = 4 + 1 + 2, qp = new Float32Array(QN * 12), qc = new Float32Array(QN * 12), qi = []; for (let i = 0; i < QN; i++) qi.push(i * 4, i * 4 + 1, i * 4 + 2, i * 4, i * 4 + 2, i * 4 + 3);
  const qcol = (i, h) => { const c = col3(h); for (let k = 0; k < 4; k++) qc.set(c, (i * 4 + k) * 3); }; for (let i = 0; i < 4; i++) qcol(i, COL.web); qcol(4, COL.yel); qcol(5, 0x8a8f96); qcol(6, 0x8a8f96);
  qg.setAttribute('position', new THREE.BufferAttribute(qp, 3)); qg.setAttribute('color', new THREE.BufferAttribute(qc, 3)); qg.setIndex(qi); const quads = new THREE.Mesh(qg, lam()); quads.frustumCulled = false; grp.add(quads);
  const quad = (i, a, b, c, d) => { qp.set([a.x, a.y, a.z, b.x, b.y, b.z, c.x, c.y, c.z, d.x, d.y, d.z], i * 12); };
  // apuvarjo: kupu + verkko + kahva
  const pcg = new THREE.Group(), dome = new THREE.Mesh(new THREE.SphereGeometry(0.40, 16, 6, 0, Math.PI * 2, 0, Math.PI * 0.5), lam()), mesh = new THREE.Mesh(new THREE.ConeGeometry(0.40, 0.42, 16, 1, true), lam());
  const paint = (m, h) => { const c = col3(h), a = new Float32Array(m.geometry.attributes.position.count * 3); for (let i = 0; i < a.length; i += 3) a.set(c, i); m.geometry.setAttribute('color', new THREE.BufferAttribute(a, 3)); };
  paint(dome, COL.yel); paint(mesh, 0xc9c7bd); dome.scale.y = 0.55; mesh.rotation.x = Math.PI; mesh.position.y = -0.21; const knob = new THREE.Mesh(new THREE.SphereGeometry(0.03, 8, 6), lam()); paint(knob, 0xf06a0c); knob.position.y = 0.23; pcg.add(dome, mesh, knob); grp.add(pcg);
  const tg = new THREE.TorusGeometry(0.035, 0.008, 6, 12), tog = [new THREE.Mesh(tg, lam()), new THREE.Mesh(tg, lam())]; tog.forEach(m => { paint(m, COL.yel); grp.add(m); });

  const S = { pc: 'stowed', deploy: 0, brakeL: 0, brakeR: 0, toggles: false, collapse: 0 }, q = { sf: 1, tf: 1, cf: 1, fl: 0, t: 0, bl: 0, br: 0, col: 0 };
  const w2l = (o, out) => grp.worldToLocal(o.getWorldPosition(out)), a = new V(), b = new V(), c = new V(), d = new V(), e = new V(), sh = [new V(), new V()], link = [new V(), new V(), new V(), new V()], cen = [new V(), new V(), new V(), new V()], bag = new V(), pcp = new V(), top = new V(), hp = [new V(), new V()];
  let li = 0; const L = (p, r) => { lp[li++] = p.x; lp[li++] = p.y; lp[li++] = p.z; lp[li++] = r.x; lp[li++] = r.y; lp[li++] = r.z; };
  const rig = { gear, canopy: grp, state: S, anchors: A, worn: true,
    wear(on) { rig.worn = on; gear.visible = on; for (const h of hair) h.visible = !on; if (!on) grp.visible = false; },
    update(t) { const D = S.deploy; grp.visible = rig.worn && (S.pc !== 'stowed'); if (!grp.visible) return;
      A.riser_l.getWorldPosition(a); A.riser_r.getWorldPosition(b); a.add(b).multiplyScalar(0.5); if (grp.parent) grp.parent.worldToLocal(a); grp.position.copy(a); grp.updateMatrixWorld(true);      // ryhmän origo = olkapäiden väli
      w2l(A.riser_l, sh[0]); w2l(A.riser_r, sh[1]); w2l(A.bag, bag); w2l(hand.l, hp[0]); w2l(hand.r, hp[1]);
      // tila vaiheittain
      const rise = ease(seg(D, 0.15, 0.22)), pay = ease(seg(D, 0.18, 0.35)), outb = seg(D, 0.35, 0.5), inf = ease(seg(D, 0.5, 0.97));
      q.t = t; q.sf = lerp(lerp(0.07, 0.2, outb), 1, inf * inf * (3 - 2 * inf)); q.tf = lerp(0.16, 1, ease(seg(D, 0.52, 0.9))) * (1 - 0.85 * S.collapse); q.cf = lerp(0.55, 1, ease(seg(D, 0.4, 0.75)));
      q.fl = (D < 1 ? 0.9 * (1 - inf) + 0.06 : 0.012) + 0.25 * S.collapse * (1 - S.collapse); q.bl = S.brakeL; q.br = S.brakeR; q.col = S.collapse;
      const shown = D >= 0.35; canopy.visible = shown; if (shown) { for (let i = 0; i < CV.length; i++) { const v = CV[i]; cpt(v[0], v[1], v[2], v[3], q, P); cp[i * 3] = P.x; cp[i * 3 + 1] = P.y; cp[i * 3 + 2] = P.z; } cg.attributes.position.needsUpdate = true; cg.computeVertexNormals(); }
      // kantohihnojen yläpäät (lenkit): nousevat olkapäiltä, kun pussi lähtee
      const up = RISER * rise, sp = lerp(0.03, 0.10, rise); for (let k = 0; k < 4; k++) { const s = sh[k & 1], f = k < 2 ? 0.07 : -0.07; link[k].set(s.x * lerp(1, 1.35, rise), s.y + up, s.z + f * rise + (1 - rise) * -0.05); if (S.collapse) link[k].y -= 0.2 * S.collapse; }
      // sisäpussi ja apuvarjo
      cpt(CELLS / 2, 0.4, 1, 0, q, top); const stretch = RISER + LINE - 0.35;
      if (D < 0.35) { a.copy(bag); a.y = Math.max(bag.y, bag.y + (stretch - bag.y) * pay); a.z = lerp(bag.z, 0.2, pay); top.copy(a); }
      const bagv = D >= 0.15 && D < 0.62; if (S.pc === 'hand') pcp.copy(hp[1]); else { const k = ease(seg(D, 0, 0.13)); if (rig._rel) b.copy(rig._rel); else b.copy(hp[1]); pcp.set(lerp(b.x, top.x, k), lerp(b.y, top.y + BRIDLE, k), lerp(b.z, top.z - 0.25, k));
        if (D > 0.6) { const tr = ease(seg(D, 0.6, 0.9)); pcp.set(top.x + 0.15 * Math.sin(t * 3), top.y + lerp(BRIDLE, 0.35, tr), top.z - lerp(0.25, BRIDLE * 0.95, tr)); } if (S.collapse) { pcp.y = lerp(pcp.y, top.y, S.collapse); } }
      pcg.position.copy(pcp); const pin = S.pc === 'hand' ? 0.16 : lerp(0.3, 1, ease(seg(D, 0.02, 0.12))) * (D > 0.75 ? lerp(1, 0.5, ease(seg(D, 0.75, 0.95))) : 1); pcg.scale.set(pin, pin * (0.8 + 0.2 * pin), pin);
      c.copy(pcp).sub(top); if (S.pc === 'hand' || c.lengthSq() < 1e-6) pcg.quaternion.identity(); else pcg.quaternion.setFromUnitVectors(a.set(0, 1, 0), c.normalize()); pcg.rotateZ(0.12 * Math.sin(t * 9)); pcg.visible = true;
      // punokset
      li = 0; for (let k = 0; k < 4; k++) cen[k].set(0, 0, 0);
      for (let r = 0; r <= CELLS; r++) { const sd = r < (CELLS + 1) / 2 ? 0 : 1;      // 0 = hahmon vasen (+x)
        for (let gI = 0; gI < 2; gI++) { const lk = link[gI * 2 + sd]; if (shown) { cpt(r, LA[gI * 2], 0, 0, q, a); cpt(r, LA[gI * 2 + 1], 0, 0, q, b); } else { a.copy(top); b.copy(top); a.x += (r - 4.5) * 0.02; b.x = a.x; }
          c.copy(a).add(b).multiplyScalar(0.5).lerp(lk, 0.45); L(lk, c); L(c, a); L(c, b); cen[gI * 2 + sd].add(a).add(b); } }
      for (let k = 0; k < 4; k++) cen[k].multiplyScalar(1 / (CELLS + 1));
      for (let sd = 0; sd < 2; sd++) { const lk = link[2 + sd], br = sd ? S.brakeR : S.brakeL, held = S.toggles && D >= 1, tp = held ? hp[sd] : e.copy(lk).setY(lk.y - 0.10);      // ohjauspunos: jättöreuna -> yhdistys -> ohjain takahihnassa -> lenkki
        d.set(0, 0, 0); const ps = []; for (let j = 0; j < 5; j++) { const r = sd ? CELLS - j * 1.05 : j * 1.05; if (shown) cpt(r, 1, 0, 0, q, a); else a.copy(top); ps.push(a.clone()); d.add(a); } d.multiplyScalar(0.2).lerp(lk, 0.5); for (const p of ps) L(d, p); L(d, lk); L(lk, tp);
        tog[sd].position.copy(tp); tog[sd].visible = D >= 0.5; tog[sd].rotation.set(Math.PI / 2, 0, 0); }
      if (S.pc !== 'hand') { L(pcp, top); } else L(pcp, pcp);                                    // yhdyspunos
      for (let k = 0; k < 4; k++) L(k < 2 ? sh[k & 1] : sh[k & 1], k < 2 ? sh[k & 1] : sh[k & 1]);   // (varalla)
      while (li < lp.length) lp[li++] = pcp.x; lg.attributes.position.needsUpdate = true; lines.visible = D >= 0.15 || S.pc !== 'stowed';
      // kantohihnat
      for (let k = 0; k < 4; k++) { const s = sh[k & 1], lk = link[k], w = 0.022; quad(k, a.set(s.x - w, s.y, s.z), b.set(s.x + w, s.y, s.z), c.set(lk.x + w, lk.y, lk.z), d.set(lk.x - w, lk.y, lk.z)); }
      // liukuri: valuu punoksia pitkin kuvulta lenkeille
      const sl = 1 - ease(seg(D, 0.55, 0.96)), sv = D >= 0.35; if (sv) { const pt = (k, o) => o.copy(link[k]).lerp(cen[k], 0.06 + 0.86 * sl); quad(4, pt(0, a), pt(1, b), pt(3, c), pt(2, d)); } else quad(4, a.set(0, 0, 0), a, a, a);
      // sisäpussi
      if (bagv) { const o = D < 0.35 ? top : c.copy(top).lerp(pcp, 0.25 + 0.5 * seg(D, 0.35, 0.62)), w = 0.16, h = 0.11; quad(5, a.set(o.x - w, o.y - h, o.z), b.set(o.x + w, o.y - h, o.z), d.set(o.x + w, o.y + h, o.z), e.set(o.x - w, o.y + h, o.z)); quad(6, a.set(o.x, o.y - h, o.z - w), b.set(o.x, o.y - h, o.z + w), d.set(o.x, o.y + h, o.z + w), e.set(o.x, o.y + h, o.z - w)); }
      else { quad(5, a.set(0, 0, 0), a, a, a); quad(6, a, a, a, a); }
      qg.attributes.position.needsUpdate = true; qg.computeVertexNormals(); },
    throwPilot() { rig._rel = grp.worldToLocal(hand.r.getWorldPosition(new V())); S.pc = 'out'; } };
  return rig;
}
