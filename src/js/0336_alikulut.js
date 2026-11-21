// ---------- Pyörätien alikulut (21.11.2026, maasto ja data: js/0106_maastokorjaukset.js ALIK) ----------
// Omistaja: "Sielläkin alikulku" (Tiilimäki, Luvianpuistokatu). Rakenne kuten tyypillinen Porin kevyen liikenteen alikulku: betoninen kehä (seinät ja
// kansilaatta), otsamuurit kaiteineen tien reunoilla, asfalttilattia ja valonauha katossa. Rampit ja luiskat ovat maastoa (0106 kaivaa korkeusmallin).
// Maan 6 m / 18 m solut, joihin kaivanto osuu, on jätetty pois (tSkip ja ulkokehä, koukut __alikSkip, __alikSkip18): tilalle 1 m pinta ilmakuvalla,
// joka vaihtuu tarkkaan ilmakuvalaattaan (ROOFT) kun se latautuu.
{ const tl = new THREE.TextureLoader(), ld = (f, srgb, r) => { const t = tl.load(f); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; if (srgb) t.colorSpace = THREE.SRGBColorSpace; return t; };
  const mBet = new THREE.MeshStandardMaterial({ map: ld('./silta/betoni_albedo.jpg', true), normalMap: ld('./silta/betoni_normal.jpg', false), color: 0xc4c0b7, roughness: 0.92, metalness: 0, side: THREE.DoubleSide });
  const mAs = new THREE.MeshStandardMaterial({ map: ld('./road_asph.jpg', true), color: 0x8e8e8e, roughness: 0.95, metalness: 0, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -3, polygonOffsetUnits: -3 });
  const mLamp = new THREE.MeshBasicMaterial({ color: 0xfff3d6 }), mRail = new THREE.MeshStandardMaterial({ color: 0x6f7377, roughness: 0.5, metalness: 0.6 });
  const LS = 512, OS = 18, hw = ALIK_W / 2;
  const mk = (pos, uv, m) => { if (!pos.length) return; const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); if (uv) g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); g.computeVertexNormals();
    const me = noT(new THREE.Mesh(g, m)); me.receiveShadow = true; scene.add(me); return me; };
  let nq = 0;
  for (const A of ALIK) {
    const B = [], BU = [], AS = [], AU = [], LA = [];
    const pt = (s, l) => { const [x, y] = A.at(s), k = Math.max(0, Math.min(A.P.length - 2, A.S.findIndex((v, i) => i + 1 < A.S.length && A.S[i + 1] >= s))), ux = (A.P[k + 1][0] - A.P[k][0]) / (A.S[k + 1] - A.S[k] || 1), uy = (A.P[k + 1][1] - A.P[k][1]) / (A.S[k + 1] - A.S[k] || 1);
      return [x + uy * l, y - ux * l]; };
    const quad = (G, U, a, b, c, d, sc) => { for (const q of [a, b, c, a, c, d]) { G.push(q[0], q[2], -q[1]); if (U) U.push(q[3] / sc, q[4] / sc); } };
    const V = (s, l, z, u, v) => { const [x, y] = pt(s, l); return [x, y, z, u === undefined ? s : u, v === undefined ? z : v]; };
    // asfalttilattia koko kaivannon ja tunnelin matkalta
    for (let s = 0; s < A.L - 0.5; s += 1) { const s2 = Math.min(A.L, s + 1), f1 = A.f(s), f2 = A.f(s2), [cx, cy] = A.at(s + 0.5);
      if (!A.covered(s + 0.5) && A.f(s + 0.5) > window.__alikTie(cx, cy) - 0.08) continue;
      quad(AS, AU, V(s, -hw + 0.15, f1 + 0.03, s, -hw), V(s2, -hw + 0.15, f2 + 0.03, s2, -hw), V(s2, hw - 0.15, f2 + 0.03, s2, hw), V(s, hw - 0.15, f1 + 0.03, s, hw), 6); }
    for (const c of A.kat) { const f = c.f, top = f + ALIK_H, zt = c.zt;
      for (let s = c.s0; s < c.s1 - 0.01; s += 1) { const s2 = Math.min(c.s1, s + 1);
        for (const sd of [-1, 1]) { const l = sd * hw; quad(B, BU, V(s, l, f - 0.1), V(s2, l, f - 0.1), V(s2, l, top), V(s, l, top), 3);              // sivuseinät
          quad(B, BU, V(s, l, f + 0.03, s, sd * 0.3), V(s2, l, f + 0.03, s2, sd * 0.3), V(s2, l - sd * 0.3, f + 0.03, s2, 0), V(s, l - sd * 0.3, f + 0.03, s, 0), 3); }   // reunakaista
        quad(B, BU, V(s, -hw, top, s, -hw), V(s2, -hw, top, s2, -hw), V(s2, hw, top, s2, hw), V(s, hw, top, s, hw), 3);                                  // kansilaatan alapinta
        quad(LA, null, V(s, -0.12, top - 0.02), V(s2, -0.12, top - 0.02), V(s2, 0.12, top - 0.02), V(s, 0.12, top - 0.02)); }
      // otsamuurit: aukon yläpuolelta ja sivuilta tien tasoon + 1,0 m kaide; paksuus 0,35 m ulospäin, päälle kansi
      for (const [e, sg] of [[c.s0, -1], [c.s1, 1]]) { const W2 = hw + 4, e2 = e + sg * 0.35, low = f - 0.4, cap = zt + 1.0;
        for (const ee of [e, e2]) { quad(B, BU, V(ee, -hw, top, -hw, top), V(ee, hw, top, hw, top), V(ee, hw, cap, hw, cap), V(ee, -hw, cap, -hw, cap), 3);
          for (const sd of [-1, 1]) quad(B, BU, V(ee, sd * hw, low, sd * hw, low), V(ee, sd * W2, low, sd * W2, low), V(ee, sd * W2, cap, sd * W2, cap), V(ee, sd * hw, cap, sd * hw, cap), 3); }
        quad(B, BU, V(e, -W2, cap, -W2, 0), V(e2, -W2, cap, -W2, 0.35), V(e2, W2, cap, W2, 0.35), V(e, W2, cap, W2, 0), 3);
        quad(B, BU, V(e, -hw, top, -hw, 0), V(e2, -hw, top, -hw, 0.35), V(e2, hw, top, hw, 0.35), V(e, hw, top, hw, 0), 3);
        for (const sd of [-1, 1]) { quad(B, BU, V(e, sd * W2, low, 0, low), V(e2, sd * W2, low, 0.35, low), V(e2, sd * W2, cap, 0.35, cap), V(e, sd * W2, cap, 0, cap), 3);
          quad(B, BU, V(e, sd * hw, low, 0, low), V(e2, sd * hw, low, 0.35, low), V(e2, sd * hw, top, 0.35, top), V(e, sd * hw, top, 0, top), 3); }
        // kaiteen putki muurin päällä (tienpuolella)
        const pts = []; for (let l = -W2; l <= W2 + 0.01; l += 1) { const [x, y] = pt(e + sg * 0.17, l); pts.push(new THREE.Vector3(x, cap + 0.12, -y)); }
        const tg = noT(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), pts.length * 2, 0.04, 6), mRail)); scene.add(tg); } }
    mk(B, BU, mBet); mk(AS, AU, mAs); mk(LA, null, mLamp);
    // maa 1 m ruudukkona pois jätettyjen ulkokehän solujen kohdalle
    const OX = OX0, OY = OY0, i0 = Math.floor((A.bb[0] - 9 - OX) / OS), i1 = Math.floor((A.bb[2] + 9 - OX) / OS), j0 = Math.floor((A.bb[1] - 9 - OY) / OS), j1 = Math.floor((A.bb[3] + 9 - OY) / OS);
    const hrSurf = (x, y) => { const ti = Math.floor((x + 1280) / LS), tj = Math.floor((y + 1280) / LS), x0t = -1280 + ti * LS, y0t = -1280 + tj * LS, ci = Math.floor((x - x0t) / 6), cj = Math.floor((y - y0t) / 6);
      return window.__alikSkip(x0t + (ci + 0.5) * 6, y0t + (cj + 0.5) * 6) ? null : gridTop(x, y, x0t, y0t, 6, 0.03); };
    const vz = (x, y) => { const h = window.__alikPinta(x, y); if (h !== null) return h; if (A.inM(x, y)) return TZg(x, y); const g = hrSurf(x, y); return g !== null ? Math.min(g - 0.03, gridTop(x, y, OX, OY, OS, 0)) : gridTop(x, y, OX, OY, OS, 0); };
    const per = new Map();
    for (let j = j0; j <= j1; j++) for (let i = i0; i <= i1; i++) { const cx = OX + (i + 0.5) * OS, cy = OY + (j + 0.5) * OS; if (!window.__alikSkip18(cx, cy)) continue;
      for (let y = cy - 9; y < cy + 9; y += 1) for (let x = cx - 9; x < cx + 9; x += 1) {
        const c = [[x, y], [x + 1, y], [x + 1, y + 1], [x, y + 1]], pp = c.map(([px, py]) => A.proj(px, py)), cov = pp.map(p => p && A.covered(p.s) ? 1 : 0), sumc = cov[0] + cov[1] + cov[2] + cov[3];
        if (sumc > 0 && sumc < 4 && pp.some(p => p && Math.abs(p.l) < hw + 4.2)) continue;       // tunnelin suu: otsamuuri peittää
        const key = Math.floor((x + 0.5 + 1280) / LS) + '_' + Math.floor((y + 0.5 + 1280) / LS); let e = per.get(key); if (!e) per.set(key, e = { P: [], U: [], U1: [] });
        const ti = Math.floor((x + 0.5 + 1280) / LS), tj = Math.floor((y + 0.5 + 1280) / LS), x0t = -1280 + ti * LS, y0t = -1280 + tj * LS;
        for (const k of [0, 1, 2, 0, 2, 3]) { const [px, py] = c[k]; e.P.push(px, vz(px, py), -py); e.U.push((px - OX0) / OXS, (py - OY0) / OYS); e.U1.push((px - x0t) / LS, (py - y0t) / LS); } nq++; } }
    for (const [key, e] of per) { const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(e.P, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(e.U, 2)); g.setAttribute('uv1', new THREE.Float32BufferAttribute(e.U1, 2));
      const me = noT(new THREE.Mesh(g, outerMat)); me.userData.fb = outerMat; me.userData.maa = true; scene.add(me); if (!ROOFT.has(key)) ROOFT.set(key, []); ROOFT.get(key).push(me);
      const h = HR.t.get(key); if (h && h.m.map) { const t = h.m.map.clone(); t.channel = 1; t.needsUpdate = true; me.material = groundTileMat(t); } }
  }
  window.__alikulut = { maaSoluja: nq };
}
