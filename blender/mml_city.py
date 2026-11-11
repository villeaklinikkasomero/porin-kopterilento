"""LoD2 buildings (Maanmittauslaitos Rakennukset 3D) -> pori/lod2.js for the game.
Every LoD2 building is tied to the city.js (OpenStreetMap) building it overlaps most; buildings with no good match are dropped
(demolished since the scan) and city.js buildings with no LoD2 keep their old extrusion (built after the scan).
Output per city.js index: roof triangles (x, y, z in dm) and wall triangles (x, y, z, u in dm; u runs along the wall)."""
import pickle, json, math, numpy as np, mapbox_earcut as ec
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
from shapely.strtree import STRtree
LB = pickle.load(open('/home/claude/mmlproc/b.pkl', 'rb'))
s = open('/home/claude/pori/city.js').read(); C = json.loads(s[s.index('{'):s.rindex('}') + 1])['b']
cp = []
for b in C:
    q = b['p']; pts = [(q[k] / 10, q[k + 1] / 10) for k in range(0, len(q), 2)]
    try: P = Polygon(pts).buffer(0)
    except Exception: P = Polygon()
    cp.append(P)
tree = STRtree(cp)

def newell(r):
    n = np.zeros(3)
    for i in range(len(r)):
        a, b = np.array(r[i]), np.array(r[(i + 1) % len(r)])
        n += [(a[1] - b[1]) * (a[2] + b[2]), (a[2] - b[2]) * (a[0] + b[0]), (a[0] - b[0]) * (a[1] + b[1])]
    l = np.linalg.norm(n); return n / l if l > 1e-9 else None

def eave(walls):
    """building eave: median of the lowest top edge of the ground-standing walls"""
    tops = []
    for R, H, n in walls:
        zb = min(p[2] for p in R)
        if zb > 1.5: continue
        t = np.array([-n[1], n[0]]); tl = np.linalg.norm(t)
        if tl < 1e-6: continue
        t /= tl; uz = [((p[0] - R[0][0]) * t[0] + (p[1] - R[0][1]) * t[1], p[2]) for p in R]
        try: pg = Polygon(uz).buffer(0)
        except Exception: continue
        if pg.is_empty or pg.area < 1: continue
        u0, _, u1, zt = pg.bounds; best = zt
        for f in (0.03, 0.25, 0.5, 0.75, 0.97):
            x = u0 + (u1 - u0) * f; seg = pg.intersection(box(x - 0.01, -50, x + 0.01, zt + 1))
            if not seg.is_empty: best = min(best, seg.bounds[3])
        tops.append((best, u1 - u0))
    if not tops: return 3.0
    tops.sort(); tot = sum(w for _, w in tops); acc = 0
    for z, w in tops:
        acc += w
        if acc >= tot / 2: return z
    return tops[-1][0]

def tri(ring, holes, f2, n=None):
    """earcut in a 2D projection; triangles re-wound to face along n (outwards / up)"""
    rings = [ring] + holes; v2 = np.array([f2(p) for r in rings for p in r], dtype=np.float64).reshape(-1, 2)
    ends = np.cumsum([len(r) for r in rings]).astype(np.uint32)
    idx = ec.triangulate_float64(v2, ends); allp = [p for r in rings for p in r]; out = []
    for k in range(0, len(idx), 3):
        a, b, c = allp[idx[k]], allp[idx[k + 1]], allp[idx[k + 2]]
        if n is not None:
            t = np.cross(np.subtract(b, a), np.subtract(c, a))
            if np.dot(t, n) < 0: b, c = c, b
        out += [a, b, c]
    return out

out = {}; owner_of = {}; stats = [0, 0]
for lb in LB:
    g = [Polygon([(p[0], p[1]) for p in r]).buffer(0) for k, r, _ in lb['p'] if k == 'G' and len(r) >= 3]
    if not g: continue
    G = unary_union(g)
    if G.area < 4: continue
    best, ba = None, 0
    for i in tree.query(G):
        a = cp[i].intersection(G).area
        if a > ba: best, ba = int(i), a
    if best is None or ba < 0.4 * min(G.area, cp[best].area): stats[1] += 1; continue
    stats[0] += 1
    z0 = lb['z0']; o = out.setdefault(best, {'r': [], 'w': [], 'h': 0, 'g': [], 'raw': []}); o['g'].append(G)
    o['raw'] += [(k, [(p[0], p[1], p[2] - z0) for p in r], [[(p[0], p[1], p[2] - z0) for p in h] for h in hs]) for k, r, hs in lb['p']]
    for k, r, holes in lb['p']:
        if k == 'G' or len(r) < 3: continue
        n = newell(r)
        if n is None: continue
        R = [(p[0], p[1], p[2] - z0) for p in r]; H = [[(p[0], p[1], p[2] - z0) for p in h] for h in holes if len(h) >= 3]
        o['h'] = max(o['h'], max(p[2] for p in R))
        if k == 'R' and abs(n[2]) > 0.08:
            for p in tri(R, H, lambda p: (p[0], p[1]), n if n[2] > 0 else -n): o['r'] += [round(p[0] * 10), round(p[1] * 10), round(p[2] * 10)]
        else:
            o.setdefault('wl', []).append((R, H, n))
    # walls: windows only below the eave; gables and parapets above it are plain wall (u = -1)
    E = eave(o['wl'])
    o['e'] = E; o['f'] = None
    for R, H, n in o.pop('wl', []):
        t = np.array([-n[1], n[0], 0.0]); tl = np.linalg.norm(t)
        if tl < 1e-6: continue
        t /= tl; x0, y0 = R[0][0], R[0][1]
        uf = lambda p: (p[0] - x0) * t[0] + (p[1] - y0) * t[1]
        us = [uf(p) for p in R]; umin = min(us)
        try: pg = Polygon([(uf(p), p[2]) for p in R]).buffer(0)
        except Exception: continue
        if pg.is_empty: continue
        lo = pg.intersection(box(-1e4, -50, 1e4, E)); hi = pg.difference(box(-1e4, -50, 1e4, E))
        back = lambda u, z: (x0 + t[0] * u, y0 + t[1] * u, z)
        for part, flag in ((lo, 0), (hi, 1)):
            for g in getattr(part, 'geoms', [part]):
                if g.is_empty or g.geom_type != 'Polygon' or g.area < 0.01: continue
                ring = [back(u, z) for u, z in list(g.exterior.coords)[:-1]]; holes = [[back(u, z) for u, z in list(h.coords)[:-1]] for h in g.interiors]
                for p in tri(ring, holes, lambda p: (uf(p), p[2]), n):
                    o['w'] += [round(p[0] * 10), round(p[1] * 10), round(p[2] * 10), -10 if flag else round((uf(p) - umin) * 10)]
# city.js buildings covered by someone else's LoD2 model are hidden
hide = []
for i, P in enumerate(cp):
    if i in out or P.area < 1: continue
    for j in tree.query(P):
        j = int(j)
        if j in out and j != i:
            if any(P.intersection(G).area > 0.5 * P.area for G in out[j]['g']): hide.append(i); break
def rel(o):                                                  # coordinates relative to the first vertex keep the file small
    a = o['r'] or o['w']; bx, by = a[0], a[1]
    return {'o': [bx, by], 'r': [v - (bx if k % 3 == 0 else by if k % 3 == 1 else 0) for k, v in enumerate(o['r'])],
            'w': [v - (bx if k % 4 == 0 else by if k % 4 == 1 else 0) for k, v in enumerate(o['w'])], 'h': round(o['h'], 1), 'e': round(o['e'], 1)}
res = {'b': {str(i): rel(o) for i, o in out.items()}, 'hide': hide}
pickle.dump({i: o['raw'] for i, o in out.items()}, open('/home/claude/mmlproc/raw.pkl', 'wb'))
js = 'export default ' + json.dumps(res, separators=(',', ':')) + ';\n'
open('/home/claude/pori/lod2.js', 'w').write(js)
print('matched', stats, 'owners', len(out), 'hidden', len(hide), 'MB', round(len(js) / 1e6, 2),
      'roof tris', sum(len(o['r']) for o in out.values()) // 9, 'wall tris', sum(len(o['w']) for o in out.values()) // 12)
