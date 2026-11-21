// ---------- Maasillat (TER.bd): betoni, asfalttikansi, auto pysyy kannella (21.11.2026) ----------
// Omistaja: "maantienkadun junaradan ylittävä silta on väärin ... voidaanko rakentaa kaikki tällaiset sillat samanlaisella betonitekstuurilla ja vain pidentää
// siltaa. Sillan pinta tulee myös asfaltoida ja pitää pinta sillä tasolla."
// Ennen: kansi oli ilmakuvaa, reunat tasaväriä ja auto ajoi kannen läpi alla olevaan leikkaukseen (Maantiekatu: kansi 7,8 m, auto 1,4 m).
// Nyt jokainen TER.bd-maasilta (rautatiesillat tekee rata/rata.js) rakennetaan samoin osin:
//   - kansi jatketaan kummastakin päästä niin pitkälle, että se kohtaa penkereen (6 m korkeusmalli pehmentää leikkauksen reunat), enintään 12 m
//   - asfalttipinta (road_asph.jpg), betoninen reunapalkki, kaide (betonimuuri) ja alapinta, päissä betoniset maatuet leikkauksen pohjaan asti
//   - betoni: tex/Concrete034 (ambientCG, CC0) -> silta/betoni_albedo.jpg, silta/betoni_normal.jpg
//   - window.__siltaZ(x, y): kannen pinta, jos piste on kannella ja auto/kävelijä on kannen tasolla (alla ajava jää alas); 082 carGround käyttää
const SILTA = { list: [] }; window.__SILTA = SILTA;
{ const tl = new THREE.TextureLoader(), ld = (f, srgb) => { const t = tl.load(f); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; if (srgb) t.colorSpace = THREE.SRGBColorSpace; return t; };
  const mBet = new THREE.MeshStandardMaterial({ map: ld('./silta/betoni_albedo.jpg', true), normalMap: ld('./silta/betoni_normal.jpg', false), color: 0xc9c5bc, roughness: 0.92, metalness: 0, side: THREE.DoubleSide });
  const mAs = new THREE.MeshStandardMaterial({ map: ld('./road_asph.jpg', true), color: 0x9a9a9a, roughness: 0.95, metalness: 0, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 });
  const mViiva = new THREE.MeshBasicMaterial({ color: 0xe9e6dc, polygonOffset: true, polygonOffsetFactor: -4, polygonOffsetUnits: -4 });
  const B = { p: [], u: [] }, A = { p: [], u: [] }, V = { p: [] }, TA = 0.13, PH = 0.95, PW = 0.3, BH = 1.0;
  // nelikulmio kolmesta-neljästä 3D-pisteestä (pelin x, y, z) ja uv metreinä (betoni 3 m / kuva, asfaltti 6 m / kuva)
  const quad = (G, a, b, c, d, s) => { const P = [a, b, c, a, c, d]; for (const q of P) { G.p.push(q[0], q[2], -q[1]); if (G.u) G.u.push(q[3] / s, q[4] / s); } };
  for (const r of TER.bd) { if ((RATA.bdSkip || []).some(([x, y]) => Math.hypot(r[1] - x, r[2] - y) < 1.5)) continue;   /* rautatiesillat: rata/rata.js */
    const hw = r[0], P = []; for (let k = 1; k + 2 < r.length; k += 3) P.push([r[k], r[k + 1], r[k + 2]]);
    if (P.length < 2) continue;
    // pidennys: kulje päästä ulospäin niin kauan kuin maa on selvästi kannen alapuolella
    for (const end of [0, 1]) { const e = end ? P[P.length - 1] : P[0], f = end ? P[P.length - 2] : P[1], dx = e[0] - f[0], dy = e[1] - f[1], l = Math.hypot(dx, dy) || 1, ux = dx / l, uy = dy / l;
      let s = 0; while (s < 12) { const x = e[0] + ux * (s + 0.5), y = e[1] + uy * (s + 0.5), g = Math.max(TZg(x, y), TZg(x - uy * hw * 0.8, y + ux * hw * 0.8), TZg(x + uy * hw * 0.8, y - ux * hw * 0.8)); if (g > e[2] - 0.15) break; s += 0.5; }
      if (s > 0) { const q = [e[0] + ux * (s + 1), e[1] + uy * (s + 1), e[2]]; if (end) P.push(q); else P.unshift(q); } }
    const off = P.map((p, k) => { const a = P[Math.max(0, k - 1)], b = P[Math.min(P.length - 1, k + 1)], dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy) || 1; return [dy / l, -dx / l]; });
    const S = [0]; for (let k = 1; k < P.length; k++) S.push(S[k - 1] + Math.hypot(P[k][0] - P[k - 1][0], P[k][1] - P[k - 1][1]));
    SILTA.list.push({ P, hw, S, bb: [Math.min(...P.map(p => p[0])) - hw - 1, Math.min(...P.map(p => p[1])) - hw - 1, Math.max(...P.map(p => p[0])) + hw + 1, Math.max(...P.map(p => p[1])) + hw + 1] });
    const at = (k, w, dz) => { const [x, y, z] = P[k], [ox, oy] = off[k]; return [x + ox * w, y + oy * w, z + dz, S[k], w]; };   // uv: pituus, leveys
    for (let k = 0; k + 1 < P.length; k++) {
      const wi = hw - PW;      // asfaltti kaiteiden välissä
      { const a = at(k, wi, TA), b = at(k + 1, wi, TA), c = at(k + 1, -wi, TA), d = at(k, -wi, TA); quad(A, a, b, c, d, 6); }
      if (hw >= 4) { const m0 = S[k], m1 = S[k + 1];       // keskiviiva katkoviivana (3 m viiva, 3 m väli)
        for (let s = Math.ceil(m0 / 6) * 6; s < m1; s += 6) { const t0 = (s - m0) / (m1 - m0), t1 = Math.min(1, (s + 3 - m0) / (m1 - m0)), L = (t, w) => { const a = at(k, w, TA + 0.01), b = at(k + 1, w, TA + 0.01); return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t]; };
          quad(V, L(t0, 0.06), L(t1, 0.06), L(t1, -0.06), L(t0, -0.06), 1); } }
      for (const sg of [1, -1]) {
        const o0 = at(k, sg * hw, 0), o1 = at(k + 1, sg * hw, 0), i0 = at(k, sg * wi, 0), i1 = at(k + 1, sg * wi, 0), z = (q, dz) => [q[0], q[1], q[2] + dz, q[3], q[2] + dz];
        quad(B, z(o0, -PH), z(o1, -PH), z(o1, TA + BH), z(o0, TA + BH), 3);      // ulkopinta: reunapalkki + kaide yhtenä betonina
        quad(B, z(i0, TA), z(i1, TA), z(i1, TA + BH), z(i0, TA + BH), 3);         // kaiteen sisäpinta
        { const a = z(o0, TA + BH), b = z(o1, TA + BH), c = z(i1, TA + BH), d = z(i0, TA + BH); a[4] = sg * hw; b[4] = sg * hw; c[4] = sg * wi; d[4] = sg * wi; quad(B, a, b, c, d, 3); }   // kaiteen yläpinta
      }
      { const a = at(k, hw, -PH), b = at(k + 1, hw, -PH), c = at(k + 1, -hw, -PH), d = at(k, -hw, -PH); quad(B, a, b, c, d, 3); }   // alapinta
    }
    // maatuet: päätyseinä kannen alta leikkauksen pohjaan (ja reunat kaiteen korkeudelle asti päättyvät siihen)
    for (const k of [0, P.length - 1]) { const [x, y, z] = P[k]; let gmin = z; for (let s = 0; s <= 8; s += 1) { const kk = k ? -1 : 1, q = P[k + kk] || P[k], dx = q[0] - x, dy = q[1] - y, l = Math.hypot(dx, dy) || 1;
        for (const w of [-hw, 0, hw]) gmin = Math.min(gmin, TZg(x + dx / l * s + off[k][0] * w, y + dy / l * s + off[k][1] * w)); }
      const zb = Math.min(z - PH, gmin - 0.5), a = at(k, hw + 0.4, -PH), b = at(k, -hw - 0.4, -PH);
      quad(B, [a[0], a[1], zb, 0, zb], [b[0], b[1], zb, 2 * hw, zb], [b[0], b[1], z - PH, 2 * hw, z - PH], [a[0], a[1], z - PH, 0, z - PH], 3);
      // seinän paksuus 0,6 m sillan sisään päin
      const kk = k ? -1 : 1, q = P[k + kk], dx = q[0] - x, dy = q[1] - y, l = Math.hypot(dx, dy) || 1, t = 0.6, A2 = [a[0] + dx / l * t, a[1] + dy / l * t], B2 = [b[0] + dx / l * t, b[1] + dy / l * t];
      quad(B, [A2[0], A2[1], zb, 0, zb], [B2[0], B2[1], zb, 2 * hw, zb], [B2[0], B2[1], z - PH, 2 * hw, z - PH], [A2[0], A2[1], z - PH, 0, z - PH], 3);
      for (const [E, F] of [[a, A2], [b, B2]]) quad(B, [E[0], E[1], zb, 0, zb], [F[0], F[1], zb, t, zb], [F[0], F[1], z - PH, t, z - PH], [E[0], E[1], z - PH, 0, z - PH], 3); }
  }
  const mk = (G, m) => { if (!G.p.length) return; const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(G.p, 3)); if (G.u) g.setAttribute('uv', new THREE.Float32BufferAttribute(G.u, 2)); g.computeVertexNormals(); const me = noT(new THREE.Mesh(g, m)); me.receiveShadow = true; scene.add(me); return me; };
  mk(B, mBet); mk(A, mAs); mk(V, mViiva);
  // kannen pinta pisteessä (x, y), tai null; viite = auton / kävelijän nykyinen korkeus: kannelle vain jos ollaan suunnilleen kannen tasolla
  SILTA.deck = (x, y) => { for (const b of SILTA.list) { if (x < b.bb[0] || y < b.bb[1] || x > b.bb[2] || y > b.bb[3]) continue; const P = b.P;
      for (let k = 0; k + 1 < P.length; k++) { const ax = P[k][0], ay = P[k][1], dx = P[k + 1][0] - ax, dy = P[k + 1][1] - ay, L2 = dx * dx + dy * dy || 1, t = ((x - ax) * dx + (y - ay) * dy) / L2;
        if (t < -0.02 || t > 1.02) continue; const tc = Math.min(1, Math.max(0, t)), px = ax + dx * tc, py = ay + dy * tc; if (Math.hypot(x - px, y - py) > b.hw - 0.05) continue;
        return P[k][2] + (P[k + 1][2] - P[k][2]) * tc + TA; } } return null; };
  window.__siltaZ = (x, y) => { const d = SILTA.deck(x, y); if (d === null) return null; const ref = (typeof WALK !== 'undefined' && WALK.on) ? WALK.z : (typeof CAR !== 'undefined' ? CAR.z : d);
    return (ref === undefined || ref === null || ref > d - 2.2) ? d : null; };
}
