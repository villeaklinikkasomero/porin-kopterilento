// ---------- Luvianpuistokatu ja Maamiehenkatu kahdessa tasossa, kadut Tiilimäelle ja Isomäelle (21.11.2026) ----------
// Omistaja: "pyörätie menee ylemmällä tasolla noin 2m ja autotie kaistoineen alempana, nyt myös mäki piirretty asfaltille. Tie on todella kumpurainen".
// 6 m korkeusruudukko ei esitä 2-3 m levyistä luiskaa: ajorata kallistui reunoiltaan ja radan sillan kohdalla oli 1,4 m kumpu. tools/roads/tie_luvianpuisto.py
// suunnittelee käytävän pinnan 1 m ruudukkona (tie/tie_data.js): tasainen ajorata, yläpenkereet pyöräteille, nurmiluiskat välissä.
//   window.__tieZ(x, y)    käytävän pinta (groundTop käyttää sitä, siis myös asfaltti, auto ja jalankulkijat), muualla null
//   window.__tieSkip(x, y) 6 m maaruudukon solu (keskipiste) jätetään pois käytävän kohdalta (010_maasto.js tSkip); 0335_tie_maa.js piirtää tilalle 1 m pinnan
//   window.__tieExt(x, y)  roads.js:n katugeometria jatkuu ytimen ulkopuolelle Tiilimäelle ja Isomäelle (tools/roads/osm_ways_tie.json): auto ajaa siellä
//                          asfaltilla (082 carGround) eikä lentoaseman yksinkertaisia nauhateitä piirretä päälle (180)
import TIE_D from './tie/tie_data.js';
const TIE = (() => {
  const D = TIE_D, dec = b => new Int16Array(TDEC(b).buffer), runs = dec(D.runs), zv = dec(D.z), Z = new Float32Array(D.nx * D.ny).fill(NaN);
  let k = 0; for (let r = 0; r + 2 < runs.length; r += 3) { const j = runs[r], i0 = runs[r + 1], n = runs[r + 2]; for (let q = 0; q < n; q++) Z[j * D.nx + i0 + q] = zv[k++] / 1000; }
  const at = (i, j) => (i < 0 || j < 0 || i >= D.nx || j >= D.ny) ? NaN : Z[j * D.nx + i];
  const z = (x, y) => { const fx = x - D.x0 - 0.5, fy = y - D.y0 - 0.5, i = Math.floor(fx), j = Math.floor(fy), u = fx - i, v = fy - j;
    const a = at(i, j), b = at(i + 1, j), c = at(i, j + 1), d = at(i + 1, j + 1); if (a !== a || b !== b || c !== c || d !== d) return null;
    return (a * (1 - u) + b * u) * (1 - v) + (c * (1 - u) + d * u) * v; };
  const has = (x, y) => { const v = at(Math.floor(x - D.x0), Math.floor(y - D.y0)); return v === v; };
  const skip = (cx, cy) => { if (cx < D.x0 - 3 || cy < D.y0 - 3 || cx > D.x0 + D.nx + 3 || cy > D.y0 + D.ny + 3) return false;
    for (let dy = -2.5; dy <= 2.5; dy += 1) for (let dx = -2.5; dx <= 2.5; dx += 1) if (has(cx + dx, cy + dy)) return true; return false; };
  const ext = (x, y) => (x > -1785 && x < -768 && y > -1490 && y < -669) || (x > -1785 && x < -790 && y > -669 && y < -150) || (x > -790 && x < -560 && y > -1300 && y < -995);   // laajennetun roads.js:n OSM-alueet (osm_ways_tie.json)
  return { D, z, has, skip, ext };
})();
window.__tieZ = TIE.z; window.__tieSkip = TIE.skip; window.__tieExt = TIE.ext;
// 21.11.2026 (omistaja: "tee suoriksi tienpintaa myös Luvianpuistokadulta, Satakunnankadun poliisilaitoksen ympyrän ja Tiilimäen Hesburgerin välistä"):
// käytävän (yllä, 1 m ruudukko) länsipuolella ajorata seurasi suoraan 6 m korkeusmallia: pientä aaltoilua ja Tiilimäellä (-1204, -786) 1,7 m syvä kuoppa
// (laserkeilauksessa alikulun kohta). Ajoradalle suunnitellaan pituusprofiili kuten tiensuunnittelussa: mediaani 40 m (kuopat ja kummut pois) ja kaksi
// 60 m liukuvaa keskiarvoa (loivat pystykaaret). Molempien ajoratojen ympärillä maa 9 m:iin profiilin tasossa (ei sivukallistumaa), 9-20 m loiva luiska
// luonnolliseen maahan. Profiili liittyy käytävän päähän (s 380-420 m) ja Hesburgerin jälkeen takaisin maastoon (s 1090-1120 m).
// Vain THG (todellinen maa: groundTop, asfaltti, auto, botit, ilmakuvamaa); TZs ennallaan, joten talot ja puut eivät liiku.
{ const A = [[-575, -598], [-609, -589], [-620, -607], [-627, -618], [-637, -629], [-649, -640], [-709, -692], [-768, -738], [-773, -742], [-784, -750], [-823, -782], [-850, -800], [-867, -807], [-890, -816], [-910, -822], [-927, -825], [-948, -828], [-977, -828], [-1024, -823], [-1210, -785], [-1345, -754], [-1417, -738], [-1539, -710], [-1559, -705]];
  const B = [[-845, -811], [-862, -818], [-891, -828], [-925, -835], [-946, -836], [-976, -835], [-1024, -823]];      // eteläinen ajorata (kaksiajoratainen osuus)
  const S = []; { let s = 0; for (let i = 1; i < A.length; i++) { const [ax, ay] = A[i - 1], [bx, by] = A[i], L = Math.hypot(bx - ax, by - ay); for (let q = 0; q < L; q += 2) { const x = ax + (bx - ax) * q / L, y = ay + (by - ay) * q / L; S.push({ s: s + q, x, y, z: TIE.z(x, y) ?? TZg(x, y) }); } s += L; } }
  const med = (a, w) => a.map((_, i) => { const b = a.slice(Math.max(0, i - w), i + w + 1).sort((p, q) => p - q); return b[b.length >> 1]; });
  const avg = (a, w) => a.map((_, i) => { let t = 0, n = 0; for (let q = -w; q <= w; q++) { t += a[Math.max(0, Math.min(a.length - 1, i + q))]; n++; } return t / n; });
  const sm = avg(avg(med(S.map(p => p.z), 10), 15), 15), ss = v => v * v * (3 - 2 * v);
  const ramp = s => s <= 380 ? 0 : s < 420 ? ss((s - 380) / 40) : s <= 1090 ? 1 : s < 1120 ? 1 - ss((s - 1090) / 30) : 0;
  S.forEach((p, i) => { p.t = p.z + (sm[i] - p.z) * ramp(p.s); });
  const BS = []; for (let i = 1; i < B.length; i++) { const [ax, ay] = B[i - 1], [bx, by] = B[i], L = Math.hypot(bx - ax, by - ay); for (let q = 0; q < L; q += 2) BS.push([ax + (bx - ax) * q / L, ay + (by - ay) * q / L]); }
  const G0 = THG.slice(); let n = 0;
  const i0 = Math.floor((-1580 - TER.x0) / TER.g), i1 = Math.ceil((-870 - TER.x0) / TER.g), j0 = Math.floor((-870 - TER.y0) / TER.g), j1 = Math.ceil((-680 - TER.y0) / TER.g);
  for (let j = j0; j <= j1; j++) for (let i = i0; i <= i1; i++) { const x = TER.x0 + i * TER.g, y = TER.y0 + j * TER.g; if (x > -878) continue;
    let bp = null, bd = 1e9; for (const p of S) { const d = Math.hypot(p.x - x, p.y - y); if (d < bd) { bd = d; bp = p; } }
    let d = bd; for (const q of BS) d = Math.min(d, Math.hypot(q[0] - x, q[1] - y));      // etäisyys lähimpään ajorataan, korkeus pohjoisen ajoradan profiilista
    if (!bp || bp.s < 370 || d > 20) continue;
    const w = d <= 9 ? 1 : 1 - ss((d - 9) / 11), k = j * TER.nx + i;
    THG[k] = Math.round(((G0[k] / 10) * (1 - w) + bp.t * w) * 10); n++; }
  window.__luvianProfiili = { solmuja: n, S };
}
