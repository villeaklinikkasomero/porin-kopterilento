// ---------- Luvianpuistokadun käytävän maapinta (21.11.2026): 6 m maaruudukosta (ydin ja tarkat ilmakuvalaatat) leikattu aukko täytetään 1 m ruudukolla ----------
// Korkeus: käytävän suunniteltu pinta (TIE.z), aukon reunoilla sama kuin viereisillä 6 m kolmioilla (groundTop ilman koukkua), joten saumaa ei näy.
// Kuva: ytimen ilmakuva (uv) ja tarkka 512 m ilmakuvalaatta (uv1, ROOFT vaihtaa sen kun laatta latautuu).
{ const D = TIE.D, LS = 512;
  const g0 = (x, y) => { const ti = Math.floor((x + 1280) / LS), tj = Math.floor((y + 1280) / LS);
    return Math.max(TZg(x, y), gridTop(x, y, -HW, YS, 6, 0), gridTop(x, y, -1280 + ti * LS, -1280 + tj * LS, 6, 0.03)); };
  const zz = (x, y) => { const t = TIE.z(x, y); return t !== null ? t : g0(x, y); };
  const cut = (x, y) => { const ci = Math.floor((x + HW) / 6), cj = Math.floor((y - YS) / 6), ti = Math.floor((x + 1280) / LS), tj = Math.floor((y + 1280) / LS),
      x0t = -1280 + ti * LS, y0t = -1280 + tj * LS, hi = Math.floor((x - x0t) / 6), hj = Math.floor((y - y0t) / 6);
    return TIE.skip(-HW + (ci + 0.5) * 6, YS + (cj + 0.5) * 6) || TIE.skip(x0t + (hi + 0.5) * 6, y0t + (hj + 0.5) * 6); };
  const per = new Map();      // ilmakuvalaatta 'i_j' -> 1 m solujen vasemmat alakulmat
  for (let j = -6; j < D.ny + 6; j++) for (let i = -6; i < D.nx + 6; i++) { const x = D.x0 + i, y = D.y0 + j; if (!cut(x + 0.5, y + 0.5)) continue;
    const key = Math.floor((x + 0.5 + 1280) / LS) + '_' + Math.floor((y + 0.5 + 1280) / LS); if (!per.has(key)) per.set(key, []); per.get(key).push(x, y); }
  let nq = 0;
  for (const [key, C] of per) { const [ti, tj] = key.split('_').map(Number), x0t = -1280 + ti * LS, y0t = -1280 + tj * LS, V = new Map(), P = [], U = [], U1 = [], I = [];
    const vid = (x, y) => { const k = x * 100003 + y; let v = V.get(k); if (v === undefined) { v = P.length / 3; V.set(k, v); P.push(x, zz(x, y), -y); U.push((x + HW) / (2 * HW), (y - YS) / YSPAN); U1.push((x - x0t) / LS, (y - y0t) / LS); } return v; };
    for (let q = 0; q < C.length; q += 2) { const x = C[q], y = C[q + 1], a = vid(x, y), b = vid(x + 1, y), c = vid(x + 1, y + 1), d = vid(x, y + 1); I.push(a, b, c, a, c, d); nq++; }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(U, 2));
    g.setAttribute('uv1', new THREE.Float32BufferAttribute(U1, 2)); g.setIndex(I);
    const me = noT(new THREE.Mesh(g, groundMat)); me.userData.fb = groundMat; me.userData.tie = key; me.userData.maa = true; scene.add(me);
    if (!ROOFT.has(key)) ROOFT.set(key, []); ROOFT.get(key).push(me);
    const e = HR.t.get(key); if (e && e.m.map) { const t = e.m.map.clone(); t.channel = 1; t.needsUpdate = true; me.material = groundTileMat(t); } }
  window.__tieMaa = nq; }
