"""Blender facades on the measured LoD2 massing (Maanmittauslaitos Rakennukset 3D).
Every LoD2 wall polygon gets a gen.py facade on its rectangular part (ground .. eave); the rest of the polygon (gables,
stepped parapets) is real geometry in the wall colour. LoD2 roofs are only shadow casters here: in the game the roofs
keep the aerial photo on the measured roof shape."""
import bpy, pickle, math, statistics, json
from shapely.geometry import Polygon, box
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from zones import *
RAW = pickle.load(open('/home/claude/mmlproc/raw.pkl', 'rb'))
ROOFOCC = M('#4f5459', 0.7)

def newell(r):
    n = Vector((0, 0, 0))
    for i in range(len(r)):
        a, b = Vector(r[i]), Vector(r[(i + 1) % len(r)]); n += Vector(((a.y - b.y) * (a.z + b.z), (a.z - b.z) * (a.x + b.x), (a.x - b.x) * (a.y + b.y)))
    return n.normalized() if n.length > 1e-9 else None

def eave_of(i):
    tops = []
    for k, r, _ in RAW[i]:
        if k == 'W': tops.append(max(p[2] for p in r) if min(p[2] for p in r) < 1.5 else None)
    tops = [t for t in tops if t]
    return statistics.median(tops) if tops else B[i]['h']

def build_lod2(Z, i, spec, upper=None):
    P = spec['P']; L = lambda x, y, z: (x - Z.cx, y - Z.cy, z); seed = 0
    from shapely.ops import unary_union
    from shapely.geometry import Point
    RF = []
    for k, r, _ in RAW[i]:
        if k != 'R' or len(r) < 3: continue
        nn = newell(r)
        if nn is None or abs(nn.z) < 0.05: continue
        RF.append((Polygon([(p[0], p[1]) for p in r]).buffer(0), nn, Vector(r[0])))
    def roofz(x, y):
        best = -1e9
        for pg, nn, p0 in RF:
            if pg.contains(Point(x, y)): best = max(best, p0.z - (nn.x * (x - p0.x) + nn.y * (y - p0.y)) / nn.z)
        return best
    FP = unary_union([Polygon([(p[0], p[1]) for p in r]).buffer(0) for k, r, _ in RAW[i] if k == 'G' and len(r) >= 3])
    for k, r, holes in RAW[i]:
        if k == 'G' or len(r) < 3: continue
        if k == 'R':
            Z.hi.append(([L(*p) for p in r], ROOFOCC)); continue
        n = newell(r)
        if n is None or abs(n.z) > 0.3: continue
        mx = sum(p[0] for p in r) / len(r); my = sum(p[1] for p in r) / len(r); nh = Vector((n.x, n.y)).normalized()
        mz = sum(p[2] for p in r) / len(r)
        fa, fb = FP.contains(Point(mx + nh.x * 0.6, my + nh.y * 0.6)), FP.contains(Point(mx - nh.x * 0.6, my - nh.y * 0.6))
        if fa and fb:                                                            # upper wall: the inner side is under a higher roof
            fa = roofz(mx + nh.x * 0.6, my + nh.y * 0.6) > mz; fb = roofz(mx - nh.x * 0.6, my - nh.y * 0.6) > mz
            if fa and fb: continue                                               # internal wall between two parts of the model
        if fa and not fb:
            n = -n; r = r[::-1]                                                  # wall stored facing inwards
        t = Vector((-n.y, n.x)).normalized(); o = Vector((r[0][0], r[0][1]))
        uz = [((Vector((p[0], p[1])) - o).dot(t), p[2]) for p in r]
        try: pg = Polygon(uz).buffer(0)
        except Exception: continue
        if pg.area < 0.3: continue
        u0, zb, u1, zt = pg.bounds
        # eave: lowest top edge across the wall
        xs = [u0 + (u1 - u0) * f for f in (0.02, 0.25, 0.5, 0.75, 0.98)]; tops = []
        for x in xs:
            seg = pg.intersection(box(x - 0.01, zb - 1, x + 0.01, zt + 1))
            tops.append(seg.bounds[3] if not seg.is_empty else zb)
        ze = min(tops); seed += 1
        W3 = lambda u, z: L(o.x + t.x * u, o.y + t.y * u, z)
        if ze - zb > 1.2 and u1 - u0 > 0.4:
            lay_ = spec['layout'] if zb < 1.5 else (upper or lay(ze - zb, 'punched', bw=3.3, fh=3.0))
            p = (o.x + t.x * u0, o.y + t.y * u0); q = (o.x + t.x * u1, o.y + t.y * u1)
            build_wall(Z, p, q, zb, ze, lay_, P, i * 31 + seed, i)
            rest = pg.difference(box(u0 - 0.01, zb - 0.01, u1 + 0.01, ze))
        else:
            rest = pg
        for part in getattr(rest, 'geoms', [rest]):
            if part.is_empty or part.area < 0.05 or part.geom_type != 'Polygon': continue
            ring = list(part.exterior.coords)[:-1]
            if len(ring) < 3: continue
            pts3 = [W3(u, z) for u, z in ring]
            if newell(pts3) is not None and newell(pts3).dot(Vector((n.x, n.y, 0))) < 0: pts3.reverse()
            add_solid(Z, pts3, P['wall'], 0.5)

HIDE = set(json.loads(open('/home/claude/pori/lod2.js').read()[len('export default '):-2])['hide']) if True else set()
def context2(Z, margin=70):
    """neighbours as plain boxes for shadows, skipping OSM parts that sit inside the zone's LoD2 shells"""
    from shapely.ops import unary_union
    from shapely.geometry import Point
    shells = unary_union([Polygon([(p[0], p[1]) for p in r]).buffer(0.3) for i in Z.ids for k, r, _ in RAW[i] if k == 'G' and len(r) >= 3])
    x0, y0, x1, y1 = Z.bbox; ids = set(Z.ids)
    for i in range(len(B)):
        if i in ids or i in HIDE: continue
        pts, a = poly(i); c = cen(pts)
        if not (x0 - margin < c[0] < x1 + margin and y0 - margin < c[1] < y1 + margin): continue
        if shells.contains(Point(c)): continue
        h = B[i]['h']; n = len(pts)
        for k in range(n):
            p, q = pts[k], pts[(k + 1) % n]
            Z.hi.append(([(p[0] - Z.cx, p[1] - Z.cy, 0), (q[0] - Z.cx, q[1] - Z.cy, 0), (q[0] - Z.cx, q[1] - Z.cy, h), (p[0] - Z.cx, p[1] - Z.cy, h)], M('#b5b0a6')))
        Z.hi.append(([(x - Z.cx, y - Z.cy, h) for x, y in pts], M('#55585c')))
    s = 400
    Z.hi.append(([(-s, -s, -0.02), (s, -s, -0.02), (s, s, -0.02), (-s, s, -0.02)], M((0.22, 0.22, 0.22))))

# Pori render colours of the 1920-60s stone centre: buff, ochre, sand, pale grey-green, salmon, light grey
PALP = ['#d9c9a3', '#cdb487', '#e2d6bb', '#c9cbbd', '#d8b9a0', '#cfcac0', '#e6dfcc', '#bfc4b8', '#d6c08e', '#c7b8a6', '#e0cfb0', '#b9b2a4']
def spec_for(i):
    sp = SPEC.get(i)
    if sp: return sp
    sp = auto(i); sp['P'] = dict(sp['P']); sp['P']['wall'] = M(PALP[(i * 7 + 3) % len(PALP)])
    return sp
