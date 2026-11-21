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
