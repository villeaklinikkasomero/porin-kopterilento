"""Kokemäenjoki lowered below street level: ground meshes with the river cut out, sloped natural banks (3 m) and
near-vertical stone quays along Eteläranta, a water surface, and a 4 m raster mask for the flight logic. -> pori/river.js"""
import json, pickle, base64, numpy as np, mapbox_earcut as ec
from shapely.geometry import box, Polygon, MultiPolygon, Point
from shapely.ops import unary_union
s = open('/home/claude/pori/city.js').read(); C = json.loads(s[s.index('{'):s.rindex('}') + 1])
HW, YS, YN, OX0, OX1, OY0, OY1 = C['hw'], C['ys'], C['yn'], C['ox0'], C['ox1'], C['oy0'], C['oy1']
R = pickle.load(open('/home/claude/river.pkl', 'rb')).intersection(box(OX0, OY0, OX1, OY1)).buffer(0)
WL = -2.4
QUAY = box(-420, 455, 240, 530)                      # Eteläranta: stone quay, almost vertical
inset = unary_union([R.buffer(-3.2, join_style=2), R.buffer(-0.35, join_style=2).intersection(QUAY)]).buffer(0)
inset = inset.intersection(R).buffer(0)
def parts(g): return [p for p in getattr(g, 'geoms', [g]) if p.geom_type == 'Polygon' and p.area > 0.5]
def tri(poly):
    rings = [list(poly.exterior.coords)[:-1]] + [list(h.coords)[:-1] for h in poly.interiors]
    v = np.array([p for r in rings for p in r], dtype=np.float64); ends = np.cumsum([len(r) for r in rings]).astype(np.uint32)
    idx = ec.triangulate_float64(v, ends); return [tuple(v[i]) for i in idx]
def flat(g):
    out = []
    for p in parts(g):
        for x, y in tri(p): out += [round(x, 2), round(y, 2)]
    return out
# Eteläranta (renewed 2020s): lower quay walk 1.05 m below the street, three seating steps up to street level
QSEG = box(-330, 455, 195, 530)
qline = R.exterior.intersection(QSEG)
qline = max(getattr(qline, 'geoms', [qline]), key=lambda g: g.length).simplify(0.3)
STRIP = qline.buffer(7.2, cap_style=2).difference(R).buffer(0)
pickle.dump(STRIP, open('/home/claude/mmlproc/strip.pkl', 'wb'))
core = box(-HW, YS, HW, YN)
res = {'wl': WL}
res['core'] = flat(core.difference(R).difference(STRIP))
res['outer'] = flat(box(OX0, OY0, OX1, OY1).difference(core).difference(R))
res['water'] = flat(R.buffer(3.0).intersection(box(OX0, OY0, OX1, OY1)))
# banks: river minus inset; vertex height 0 on the shore line, WL on the water edge
bank = []
edge = R.boundary
for p in parts(R.difference(inset).buffer(0)):
    for x, y in tri(p):
        z = (-1.05 if QSEG.contains(Point(x, y)) and qline.distance(Point(x, y)) < 0.5 else 0.0) if edge.distance(Point(x, y)) < 0.08 else WL
        bank += [round(x, 2), round(y, 2), z]
res['bank'] = bank
# 0.25 m tiles of the sharper photo, each with the river cut out
tiles = {}
for i in range(6):
    for j in range(5):
        x0, y0 = -1280 + i * 512, -1280 + j * 512; t = box(x0, y0, x0 + 512, y0 + 512)
        if t.intersects(R) or t.intersects(STRIP): tiles[f'{i}_{j}'] = flat(t.difference(R).difference(STRIP))
res['tiles'] = tiles
# 4 m raster of the river for heights in the flight logic
G = 4; nx = int((OX1 - OX0) / G) + 1; ny = int((OY1 - OY0) / G) + 1
import shapely
xs = OX0 + (np.arange(nx) + 0.5) * G; ys = OY0 + (np.arange(ny) + 0.5) * G
X, Y = np.meshgrid(xs, ys); M = shapely.contains_xy(R, X, Y).astype(np.uint8)
res['mask'] = {'g': G, 'nx': nx, 'ny': ny, 'b': base64.b64encode(np.packbits(M.ravel())).decode()}
W_ = dict(primary=21, secondary=12, tertiary=9, residential=7, unclassified=6, track=4, cycleway=4, footway=3.5, steps=3)
res['br'] = [{'w': W_[b['k']], 'p': b['p'], 'n': b['n']} for b in json.load(open('/home/claude/data/river_bridges.json')) if b['k'] in W_]
res['quay'] = [round(c, 2) for p in qline.coords for c in p]
js = 'export default ' + json.dumps(res, separators=(',', ':')) + ';\n'
open('/home/claude/pori/river.js', 'w').write(js)
print('MB', round(len(js) / 1e6, 2), 'core tris', len(res['core']) // 6, 'bank tris', len(bank) // 9, 'tiles', list(tiles))
