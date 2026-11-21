"""Jyrkät luiskat jalkakäytäväkaistalta pois (21.11.2026, omistaja: "korjataan noita huomaamasia asioita").

build_roads.py vetää 7 m jalkakäytäväkaistan ajoradan ympärille. Siltojen päissä, ratojen leikkauksissa ja penkereillä kaista peitti luiskan
(esim. Maantiekadun silta radan yli). Tämä työkalu etsii korkeusmallista (terrain.js + rata/rata_data.js ter) rinteet, joiden kaltevuus on yli
RAJA (oletus 0,25 = 14°), ja kirjoittaa ne GeoJSON-monikulmioina. build_roads.py --jyrkat=... poistaa ne jalkakäytävästä (EI ajoradalta eikä
OSM:n kävely- ja pyöräteiltä) ja tekee niistä nurmea.

usage: python3 tools/roads/jyrkat.py REPO out.json [x0 y0 x1 y1] [raja]
"""
import sys, json, base64
import numpy as np, cv2
from scipy import ndimage
from shapely.geometry import Polygon, mapping
from shapely.ops import unary_union

REPO, OUT = sys.argv[1:3]
X0, Y0, X1, Y1 = map(float, sys.argv[3:7]) if len(sys.argv) > 6 else (-1790, -1495, 900, 995)
RAJA = float(sys.argv[7]) if len(sys.argv) > 7 else 0.25
s = open(REPO + '/terrain.js').read(); T = json.loads(s[s.index('{'):s.rindex('}') + 1])
NX, NY, G, TX0, TY0 = T['nx'], T['ny'], T['g'], T['x0'], T['y0']
HG = np.frombuffer(base64.b64decode(T['hg']), dtype=np.int16).copy()
s = open(REPO + '/rata/rata_data.js').read(); RA = json.loads(s[s.index('{'):s.rindex('}') + 1]); o = RA.get('ter', [])
for k in range(0, len(o) - 1, 2): HG[o[k]] = o[k + 1]
HG = HG.reshape(NY, NX).astype(np.float32) / 10
R = 1.0                                                     # raster 1 m
xs = X0 + R / 2 + np.arange(int((X1 - X0) / R)) * R; ys = Y0 + R / 2 + np.arange(int((Y1 - Y0) / R)) * R
fx = (xs - TX0) / G; fy = (ys - TY0) / G
Z = ndimage.map_coordinates(HG, np.meshgrid(fy, fx, indexing='ij'), order=1, mode='nearest')
gy, gx = np.gradient(Z, R); S = np.hypot(gx, gy)
M = (S > RAJA).astype(np.uint8)
M = cv2.morphologyEx(M, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
cs, hier = cv2.findContours(M, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
polys = []
if hier is not None:
    hier = hier[0]
    for i, c in enumerate(cs):
        if hier[i][3] != -1 or len(c) < 3: continue
        P = lambda cc: [(X0 + (p[0][0] + 0.5) * R, Y0 + (p[0][1] + 0.5) * R) for p in cc]
        holes = []; j = hier[i][2]
        while j != -1:
            if len(cs[j]) >= 3: holes.append(P(cs[j]))
            j = hier[j][0]
        pg = Polygon(P(c), holes).buffer(0)
        if pg.area >= 6: polys.append(pg)
U = unary_union(polys).buffer(0.5).buffer(-0.5).simplify(0.4)
json.dump(mapping(U), open(OUT, 'w'))
print('jyrkät rinteet', len(polys), 'kpl', round(U.area), 'm2')
