// ---------- Koko kartan tienpintojen korjaukset (21.11.2026) ----------
// Omistaja: "Sielläkin alikulku. Analysoi myös muu kartan alue. Ja korjaa mahdollisia muita ongelmakohtia." + "mahdollisimman oikean näköinen peli".
// Analyysi (kaikki CITY.r-tiet, 2 m välein, poikkeama 50 m mediaanista): korkeusmallin 6 m ruudukossa tiet sukelsivat kuoppiin siellä, missä tien alla
// kulkee jotain (silta puuttuu) tai on alikulku, ja aaltoilivat ojien ja rumpujen kohdalla. Tässä palassa:
//   (A) ALIK: pyörätien alikulut (OSM tunnel=yes) Tiilimäellä (Luvianpuistokatu + Helsingintie, välissä 44 m painanne) ja Luvianpuistokadun länsipäässä.
//       Maasto kaivetaan suunnitellun profiilin mukaan: lattia 3,3 m tienpinnan alla, rampit 7 %, luiskat 1:1,7. Rakenteet: js/0336_alikulut.js
//   (B) automaattiset sillat: pääkatu (k >= 2), jonka alla maa on yli 2,5 m tienpintaa alempana 6-50 m matkalla (esim. Helsingintie Ratapihantien yllä,
//       Mäntyluodontie ja Ulvilantie purojen yllä). Lisätään js/0301_sillat.js:n maasiltoihin (betoni, asfaltti, kaiteet, auto ja botit kannella).
//   (C) muiden teiden pituusprofiili: tien keskilinjan 0,3 m ylittävät kummut ja kuopat (rummut, ojat, laserin roskat) tasoitetaan 32 m mediaanilla
//       ja 26 m liukuvilla keskiarvoilla; tien kohdalta maa suoraksi 4 m:iin, 4-10 m loiva siirtymä. Ydinkeskusta, Luvianpuiston käytävä, sillat,
//       Porttaali ja alikulut jätetään rauhaan (niillä on omat pintansa).
const ALIK = [
  { nimi: 'Tiilimäki (Luvianpuistokatu ja Helsingintie)', P: [[-1194.6, -741.0], [-1197.9, -756.8], [-1202.8, -780.1], [-1204.7, -790.9], [-1214.8, -833.7], [-1216.5, -844.2], [-1226.3, -865.3], [-1232.5, -881.2]], kat: [[2, 3], [4, 5]] },
  { nimi: 'Luvianpuistokatu, Urheilutie', P: [[-1559.0, -662.0], [-1561.6, -672.7], [-1567.3, -697.3], [-1569.9, -708.5], [-1572.8, -721.0], [-1574.0, -730.8], [-1574.5, -736.0]], kat: [[2, 3]] } ];
const ALIK_W = 4.2, ALIK_H = 2.7, ALIK_KANSI = 0.6;      // kulkuaukon leveys ja vapaa korkeus, kansilaatta
{
  const G0 = THG.slice(), z0 = (x, y) => tBil(G0, x, y), ss = v => v * v * (3 - 2 * v);
  const med = (a, w) => a.map((_, i) => { const b = a.slice(Math.max(0, i - w), i + w + 1).sort((p, q) => p - q); return b[b.length >> 1]; });
  const avg = (a, w) => a.map((_, i) => { let t = 0, n = 0; for (let q = -w; q <= w; q++) { t += a[Math.max(0, Math.min(a.length - 1, i + q))]; n++; } return t / n; });
  const segD = (P, x, y) => { let d = 1e9; for (let k = 0; k + 1 < P.length; k++) { const [ax, ay] = P[k], [bx, by] = P[k + 1], dx = bx - ax, dy = by - ay, L2 = dx * dx + dy * dy || 1, t = Math.max(0, Math.min(1, ((x - ax) * dx + (y - ay) * dy) / L2)); d = Math.min(d, Math.hypot(ax + dx * t - x, ay + dy * t - y)); } return d; };
  // tunnetut sillat ja erikoisalueet (niillä on omat pintansa)
  const BR = []; for (const r of TER.bd) { const P = []; for (let k = 1; k + 2 < r.length; k += 3) P.push([r[k], r[k + 1]]); BR.push({ P, w: r[0] }); }
  for (const b of RIV.br) { const P = []; for (let i = 0; i + 1 < b.p.length; i += 2) P.push([b.p[i], b.p[i + 1]]); BR.push({ P, w: b.w / 2 }); }
  for (const S of RATA.silta || []) BR.push({ P: [S.a, S.b], w: S.w / 2 });
  { const sx = Math.sin(PSIL.head), sy = Math.cos(PSIL.head); BR.push({ P: [[PSIL.x - sx * 10, PSIL.y - sy * 10], [PSIL.x + sx * (PSIL.len + 10), PSIL.y + sy * (PSIL.len + 10)]], w: PSIL.half }); }
  const nearBr = (x, y, m) => BR.some(b => segD(b.P, x, y) < b.w + m);
  const T = RATA.tun, inPort = (x, y) => { if (!T) return false; const ux = T.b[0] - T.a[0], uy = T.b[1] - T.a[1], L = Math.hypot(ux, uy), dx = x - T.a[0], dy = y - T.a[1], t = (dx * ux + dy * uy) / L, l = (dx * uy - dy * ux) / L; return t > -80 && t < 300 && Math.abs(l) < 45; };
  const nearAlik = (x, y, m) => ALIK.some(A => segD(A.P, x, y) < m);
  const special = (x, y) => inCore(x, y) || TIE.has(x, y) || (x > -905 && x < -570 && y > -945 && y < -573) || inPort(x, y) || inRiver(x, y);
  const roads = CITY.r.filter(r => r.k).map(r => { const S = []; let s = 0; for (let i = 2; i < r.p.length; i += 2) { const ax = r.p[i - 2], ay = r.p[i - 1], bx = r.p[i], by = r.p[i + 1], L = Math.hypot(bx - ax, by - ay); if (L < 0.01) continue;
      for (let q = 0; q < L; q += 2) { const x = ax + (bx - ax) * q / L, y = ay + (by - ay) * q / L; S.push({ s: s + q, x, y, z: z0(x, y), ux: (bx - ax) / L, uy: (by - ay) / L }); } s += L; } return { r, S }; });

  // (B) automaattiset sillat
  const AUTO = []; window.__autoSillat = AUTO;
  for (const { r, S } of roads) { if (r.k < 2 || S.length < 10) continue; const z = S.map(p => p.z), n = S.length;
    const mx = (i0, i1) => { let m = -1e9; for (let i = Math.max(0, i0); i <= Math.min(n - 1, i1); i++) m = Math.max(m, z[i]); return m; };
    let i = 0; while (i < n) { const zl = mx(i - 15, i), zr = mx(i, i + 15); if (Math.min(zl, zr) - z[i] < 2.5) { i++; continue; }
      let a = i, b = i; while (b + 1 < n && Math.min(mx(b - 15, b), mx(b, b + 16)) - z[b + 1] > 1.0) b++;      // kuopan alue
      const ref = Math.min(mx(a - 15, a), mx(b, b + 15));
      while (a > 0 && z[a] < ref - 0.3) a--; while (b < n - 1 && z[b] < ref - 0.3) b++;                  // pengerten päät
      const L = S[b].s - S[a].s, p = S[Math.floor((a + b) / 2)], turn = Math.abs(S[a].ux * S[b].ux + S[a].uy * S[b].uy);
      if (L >= 6 && L <= 50 && turn > 0.96 && !special(p.x, p.y) && !nearBr(p.x, p.y, 8) && !nearAlik(p.x, p.y, 30)) {
        const za = z[a], zb = z[b], e = [r.k >= 3 ? 5.0 : 4.0]; for (let q = a; q <= b; q++) e.push(S[q].x, S[q].y, za + (zb - za) * (S[q].s - S[a].s) / L);
        if (!AUTO.some(o => Math.hypot(o[1] - e[1], o[2] - e[2]) < 4 && Math.hypot(o[o.length - 3] - e[e.length - 3], o[o.length - 2] - e[e.length - 2]) < 4)) AUTO.push(e); }
      i = b + 1; } }
  const BRA = AUTO.map(e => { const P = []; for (let k = 1; k + 2 < e.length; k += 3) P.push([e[k], e[k + 1]]); return { P, w: e[0] }; });
  const nearAuto = (x, y, m) => BRA.some(b => segD(b.P, x, y) < b.w + m);

  // (C) teiden pituusprofiili (vain selvät poikkeamat)
  const bed = new Set(); for (const tr of RATA.t || []) { const p = tr.p; for (let q = 0; q + 2 < p.length; q += 3) { const ci = Math.round((p[q] - TER.x0) / TER.g), cj = Math.round((p[q + 1] - TER.y0) / TER.g); for (let dj = -1; dj <= 1; dj++) for (let di = -1; di <= 1; di++) bed.add((cj + dj) * TER.nx + ci + di); } }
  const best = new Map();      // solmu -> [paino, kohde, etäisyys]
  let nSm = 0;
  for (const { S } of roads) { if (S.length < 6) continue; const z = S.map(p => p.z), t = avg(avg(med(z, 8), 6), 6);
    S.forEach((p, i) => { const d = t[i] - z[i]; if (Math.abs(d) < 0.3) return; if (special(p.x, p.y) || nearBr(p.x, p.y, 6) || nearAuto(p.x, p.y, 6)) return;
      const wd = ss(Math.min(1, (Math.abs(d) - 0.3) / 0.3)), i0 = Math.floor((p.x - 10 - TER.x0) / TER.g), i1 = Math.ceil((p.x + 10 - TER.x0) / TER.g), j0 = Math.floor((p.y - 10 - TER.y0) / TER.g), j1 = Math.ceil((p.y + 10 - TER.y0) / TER.g);
      for (let jj = j0; jj <= j1; jj++) for (let ii = i0; ii <= i1; ii++) { const k = jj * TER.nx + ii; if (bed.has(k)) continue; const dd = Math.hypot(TER.x0 + ii * TER.g - p.x, TER.y0 + jj * TER.g - p.y); if (dd > 10) continue;
        const w = wd * (dd <= 4 ? 1 : 1 - ss((dd - 4) / 6)), o = best.get(k); if (!o || dd < o[2]) best.set(k, [w, t[i], dd]); } }); }
  for (const [k, [w, tz]] of best) { if (w <= 0) continue; THG[k] = Math.round(((THG[k] / 10) * (1 - w) + tz * w) * 10); nSm++; }

  // (A) alikulkujen maasto: suunniteltu pinta hz (lattia, rampit, luiskat), kansi = tienpinta katetulla osuudella
  const G1 = THG.slice(), z1 = (x, y) => tBil(G1, x, y);      // maa teiden tasoituksen jälkeen, ennen kaivantoa (tie katetun osuuden päällä)
  window.__alikTie = z1;
  for (const A of ALIK) { const P = A.P, S = [0]; for (let k = 1; k < P.length; k++) S.push(S[k - 1] + Math.hypot(P[k][0] - P[k - 1][0], P[k][1] - P[k - 1][1]));
    A.S = S; A.L = S[S.length - 1]; A.kat = A.kat.map(([i, j]) => { const s0 = S[i] - 1.0, s1 = S[j] + 1.0, sm = (s0 + s1) / 2, k = i, f = (sm - S[k]) / (S[k + 1] - S[k] || 1);
      const x = P[k][0] + (P[k + 1][0] - P[k][0]) * Math.min(1, f), y = P[k][1] + (P[k + 1][1] - P[k][1]) * Math.min(1, f), zt = tBil(THG, x, y);
      return { s0, s1, zt, f: zt - ALIK_KANSI - ALIK_H - 0.05, ux: (P[j][0] - P[i][0]) / (S[j] - S[i]), uy: (P[j][1] - P[i][1]) / (S[j] - S[i]) }; });
    // projektio polulle: s, sivuetäisyys l (etumerkki), suunta
    A.proj = (x, y) => { let b = null; for (let k = 0; k + 1 < P.length; k++) { const [ax, ay] = P[k], [bx, by] = P[k + 1], dx = bx - ax, dy = by - ay, L = Math.hypot(dx, dy) || 1, t = Math.max(0, Math.min(1, ((x - ax) * dx + (y - ay) * dy) / (L * L)));
        const px = ax + dx * t, py = ay + dy * t, d = Math.hypot(x - px, y - py); if (!b || d < Math.abs(b.l)) b = { s: S[k] + t * L, l: ((x - ax) * dy - (y - ay) * dx) / L >= 0 ? d : -d, ux: dx / L, uy: dy / L }; } return b; };
    // pituusprofiili: katetut osuudet tasan f, välissä suora, päissä 7 % ramppi luonnolliseen maahan (polkua pitkin), pystykaaret 10 m
    const n = Math.ceil(A.L) + 1, raw = new Float32Array(n), nat = new Float32Array(n), at = s => { let k = 0; while (k + 2 < P.length && S[k + 1] < s) k++; const f = (s - S[k]) / (S[k + 1] - S[k] || 1); return [P[k][0] + (P[k + 1][0] - P[k][0]) * f, P[k][1] + (P[k + 1][1] - P[k][1]) * f]; };
    for (let q = 0; q < n; q++) nat[q] = z1(...at(q));
    const K = A.kat; for (let q = 0; q < n; q++) { let v;
      if (q <= K[0].s0) v = K[0].f + (K[0].s0 - q) * 0.07;
      else if (q >= K[K.length - 1].s1) v = K[K.length - 1].f + (q - K[K.length - 1].s1) * 0.07;
      else { v = null; for (let c = 0; c < K.length; c++) { if (q >= K[c].s0 && q <= K[c].s1) v = K[c].f; else if (c + 1 < K.length && q > K[c].s1 && q < K[c + 1].s0) v = K[c].f + (K[c + 1].f - K[c].f) * (q - K[c].s1) / (K[c + 1].s0 - K[c].s1); } }
      raw[q] = Math.min(v, nat[q]); }
    const prof = Float32Array.from(raw, (v, q) => { if (K.some(c => q >= c.s0 - 1 && q <= c.s1 + 1)) return v; let t = 0, m = 0; for (let d = -5; d <= 5; d++) { t += raw[Math.max(0, Math.min(n - 1, q + d))]; m++; } return Math.min(t / m, nat[q]); });
    A.at = at; A.f = s => { const q = Math.max(0, Math.min(n - 1.001, s)), i = Math.floor(q), u = q - i; return prof[i] * (1 - u) + prof[Math.min(n - 1, i + 1)] * u; };
    A.covered = s => A.kat.find(c => s >= c.s0 && s <= c.s1) || null;
    // pinta pisteessä: katetulla osuudella null (kansi = tie, maan ruudukko), muuten lattia / luiska / luonnollinen
    A.hz = (x, y) => { const p = A.proj(x, y); if (!p || p.s <= 0.01 && Math.abs(p.l) > 0 || p.s >= A.L - 0.01) return null; const al = Math.abs(p.l), f = A.f(p.s), g = z1(x, y);
      if (A.covered(p.s) && al < ALIK_W / 2 + 6) return null;
      const z = al <= ALIK_W / 2 ? f : f + (al - ALIK_W / 2) / 1.7; return z < g - 0.02 ? z : null; };
    let bx0 = 1e9, by0 = 1e9, bx1 = -1e9, by1 = -1e9; for (const [x, y] of P) { bx0 = Math.min(bx0, x); by0 = Math.min(by0, y); bx1 = Math.max(bx1, x); by1 = Math.max(by1, y); }
    A.bb = [bx0 - 16, by0 - 16, bx1 + 16, by1 + 16];
    // 1 m maski: kaivanto ja katettu osuus (+1 m), maan ruudukon solut, joihin osuu, jätetään pois ja 0336 piirtää tilalle 1 m pinnan
    const mx0 = Math.floor(A.bb[0]), my0 = Math.floor(A.bb[1]), mnx = Math.ceil(A.bb[2]) - mx0, mny = Math.ceil(A.bb[3]) - my0, M = new Uint8Array(mnx * mny);
    for (let j = 0; j < mny; j++) for (let i = 0; i < mnx; i++) { const x = mx0 + i + 0.5, y = my0 + j + 0.5, p = A.proj(x, y); if (!p) continue;
      const c = A.covered(p.s), in1 = (c && Math.abs(p.l) < ALIK_W / 2 + 6) || A.hz(x, y) !== null; if (in1) for (let dj = -1; dj <= 1; dj++) for (let di = -1; di <= 1; di++) { const ii = i + di, jj = j + dj; if (ii >= 0 && jj >= 0 && ii < mnx && jj < mny) M[jj * mnx + ii] = 1; } }
    A.M = { x0: mx0, y0: my0, nx: mnx, ny: mny, a: M };
    A.inM = (x, y) => { const i = Math.floor(x - mx0), j = Math.floor(y - my0); return i >= 0 && j >= 0 && i < mnx && j < mny && M[j * mnx + i] === 1; };
    // maan solmut kaivannon kohdalla suunniteltuun pintaan (myös tasoitettu kenttä TZs: puut ja pensaat eivät jää ilmaan)
    const i0 = Math.floor((A.bb[0] - TER.x0) / TER.g), i1 = Math.ceil((A.bb[2] - TER.x0) / TER.g), j0 = Math.floor((A.bb[1] - TER.y0) / TER.g), j1 = Math.ceil((A.bb[3] - TER.y0) / TER.g);
    for (let j = j0; j <= j1; j++) for (let i = i0; i <= i1; i++) { const x = TER.x0 + i * TER.g, y = TER.y0 + j * TER.g, h = A.hz(x, y); if (h === null) continue; const k = j * TER.nx + i;
      THG[k] = Math.min(THG[k], Math.round(h * 10)); THS[k] = Math.min(THS[k], Math.round(h * 10)); } }
  const inBB = (A, x, y, m = 0) => x > A.bb[0] - m && y > A.bb[1] - m && x < A.bb[2] + m && y < A.bb[3] + m;
  // koukut: maan 6 m solu (keskipiste) / ulkokehän 18 m solu pois, jos se osuu maskiin
  const cellHit = (cx, cy, h) => { for (const A of ALIK) { if (!inBB(A, cx, cy, h)) continue; for (let y = cy - h + 0.5; y < cy + h; y += 1) for (let x = cx - h + 0.5; x < cx + h; x += 1) if (A.inM(x, y)) return true; } return false; };
  window.__alikSkip = (cx, cy) => cellHit(cx, cy, 3);
  window.__alikSkip18 = (cx, cy) => cellHit(cx, cy, 9);
  // pinta groundTop:lle (asfaltti, roads.js, kävelijä): kaivannossa hz, katetun osuuden alla lattia vain alhaalla kulkevalle (alikZ)
  window.__alikPinta = (x, y) => { for (const A of ALIK) { if (!inBB(A, x, y)) continue; const h = A.hz(x, y); if (h !== null) return h;
      if (A.inM(x, y)) { const p = A.proj(x, y); if (p && A.covered(p.s)) return z1(x, y); } } return null; };      // katetun osuuden päällä tie (kaivetut solmut eivät painu sen alle)
  window.__alikZ = (x, y) => { for (const A of ALIK) { if (!inBB(A, x, y)) continue; const p = A.proj(x, y); if (!p) continue; const c = A.covered(p.s); if (!c || Math.abs(p.l) > ALIK_W / 2 + 0.6) continue;
      const ref = (typeof WALK !== 'undefined' && WALK.on) ? WALK.z : (typeof CAR !== 'undefined' ? CAR.z : null); if (ref !== null && ref !== undefined && ref < c.zt - 1.6) return c.f + 0.04; } return null; };
  // seinät: katetun osuuden sivuseinät (alhaalla kulkevalle), otsamuurien kaiteet ja siivet (tiellä kulkevalle: ei pudota kaivantoon)
  window.__alikSeina = (x, y, z) => { let dep = 0; for (const A of ALIK) { if (!inBB(A, x, y)) continue; const p = A.proj(x, y); if (!p) continue; const al = Math.abs(p.l);
      for (const c of A.kat) { if (p.s > c.s0 - 0.3 && p.s < c.s1 + 0.3 && z < c.zt - 1.6 && al > ALIK_W / 2 - 0.05 && al < ALIK_W / 2 + 1.2) dep = Math.max(dep, al - (ALIK_W / 2 - 0.05));
        if (z > c.zt - 1.2) for (const e of [c.s0, c.s1]) { const de = Math.abs(p.s - e); if (de < 0.5 && al < ALIK_W / 2 + 4) dep = Math.max(dep, 0.5 - de + 0.01); } } } return dep; };
  window.__maastokorjaukset = { sillat: AUTO.length, tasoitetutSolmut: nSm, alikulut: ALIK.map(A => ({ nimi: A.nimi, katettu: A.kat.map(c => [c.s0.toFixed(1), c.s1.toFixed(1), 'lattia ' + c.f.toFixed(2), 'tie ' + c.zt.toFixed(2)]) })) };
}
