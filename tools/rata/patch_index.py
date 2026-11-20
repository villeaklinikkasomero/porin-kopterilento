# index.html: rataverkon ja junan kytkentä (idempotentti). python3 patch_index.py <in> <out>
import sys
s = open(sys.argv[1], encoding='utf-8').read()
def rep(a, b, tag):
    global s
    if tag in s: return
    assert a in s, 'ankkuri puuttuu: ' + a[:60]
    s = s.replace(a, b, 1)
a = "import TER from './terrain.js';\n"
rep(a, a + "import RATA from './rata/rata_data.js';   // 20.11.2026: rataverkko (rata/rata.js); täältä vain maastokorjaukset ennen maan rakentamista\n", "import RATA from")
b = "  window.__siltaKummut = n; }\n"
rep(b, b + """// 20.11.2026 (omistaja: rata ja juna): ratapenkka painetaan sepelin alle ja aseman alikulun kaivanto täytetään raiteiden ja laitureiden kohdalta
// (korkeusmallissa tunneli näkyi 4 m syvänä kuoppana koko ratapihan poikki; rata kulkee suoraan sen yli, asema-aukion puolella portaali). juna/build/build_data.py
{ const o = RATA.ter || []; for (let k = 0; k + 1 < o.length; k += 2) { const i = o[k], v = o[k + 1], old = THG[i]; THG[i] = v; THS[i] = v > old ? Math.max(THS[i], v) : (THS[i] - old < 3 ? Math.min(THS[i], v) : THS[i]); } }
""", "RATA.ter")
c = "  scene.add(noT(new THREE.Mesh(gridGeo(OX0, OY0, OX1, OY1, 18, ouv, (x, y) => Math.abs(x) < HW - 9 && y > YS + 9 && y < YN - 9), outerMat)));"
rep(c, """  const RSK = new Set(RATA.osk || []), onx = Math.round((OX1 - OX0) / 18);   // rataverkon kohdalla 18 m solut pois: rata/rata.js rakentaa niihin 6 m ruudukon (ratapenkka painettu)
  scene.add(noT(new THREE.Mesh(gridGeo(OX0, OY0, OX1, OY1, 18, ouv, (x, y) => (Math.abs(x) < HW - 9 && y > YS + 9 && y < YN - 9) || RSK.has(Math.floor((y - OY0) / 18) * onx + Math.floor((x - OX0) / 18))), outerMat)));""", "RATA.osk")
d = "    for (const r of TER.bd) { const hw = r[0], P = [];"
rep(d, "    for (const r of TER.bd) { if ((RATA.bdSkip || []).some(([x, y]) => Math.hypot(r[1] - x, r[2] - y) < 1.5)) continue;   /* rautatiesillat: rata/rata.js rakentaa omansa */\n      const hw = r[0], P = [];", "RATA.bdSkip")
e = "    if (b.w === 1196441531) continue;   // Barco"
rep(e, "    if (RATA.hideB && RATA.hideB.includes(bIdx)) continue;   // 20.11.2026: aseman laiturikatos ja porraskatos ovat rata/rata.js:ssä (LoD2-laatikot peittivät raiteet)\n" + e, "RATA.hideB")
f = "window.__game = { touchIn, carGround,"
rep(f, "window.__game = { TZg, outerMat, touchIn, carGround,", "window.__game = { TZg, outerMat,")
g = '<script type="module" src="laskuvarjo/hyppy.js"></script>\n'
rep(g, g + '<!-- 20.11.2026: rataverkko, aseman laiturit ja alikulun portaali (rata/rata.js) sekä IC-juna (juna/juna.js) -->\n<script type="module" src="rata/rata.js"></script>\n<script type="module" src="juna/juna.js"></script>\n', 'src="rata/rata.js"')
h = "  { const qz = window.__quayZ ? window.__quayZ(x, y) : null; if (qz !== null) return qz; }      // Eteläranta's hand-built quay\n"
rep(h, h + "  { const rz = window.__rataZ ? window.__rataZ(x, y) : null; if (rz !== null) return rz; }      // 21.11.2026 (omistaja: \"pelaaja uppoaa\"): aseman laiturit ja ratapenkka (rata/rata.js)\n", "window.__rataZ")
i = "const tSkip = (x, y) => { if (!QUAY_MODEL) return false;"
rep(i, """// 21.11.2026: Porttaali-tunnelin kohdalta maan ruudukko pois (rata/rata.js rakentaa tunnelin, rampit ja reunat)
const rataTun = (x, y) => { const T = RATA.tun; if (!T) return false; const ux = T.b[0] - T.a[0], uy = T.b[1] - T.a[1], L = Math.hypot(ux, uy), dx = x - T.a[0], dy = y - T.a[1], t = (dx * ux + dy * uy) / L, l = (dx * uy - dy * ux) / L;
  return Math.abs(l) < T.w / 2 + 3 && t > T.t0 - 40 && t < T.t1 + 26; };
const tSkip = (x, y) => { if (rataTun(x, y)) return true; if (!QUAY_MODEL) return false;""", "const rataTun")
open(sys.argv[2], 'w', encoding='utf-8').write(s)
print('ok', len(s))
