"""Streets as geometry (18.11.2026): carriageways, raised pavements with kerbs, traffic islands and zebra crossings for the game.

usage: python3 tools/roads/build_roads.py ways.json out_roads.js [x0 y0 x1 y1]
  ways.json  OSM ways in game metres: [{"id", "t": {h: highway, f: footway, l: lanes, a: area:highway, o: oneway, n: name, br, tu, ly ...},
             "g": [[x, y], ...]}] (fetched from api.openstreetmap.org map.json, see the handoff notes)
Widths: the carriageway edge (kerb) on each side of a road is measured, not guessed, wherever OSM has the sidewalk / cycle path mapped as its
own line: that line runs in the middle of the pavement, the pavement reaches the facade, so kerb = 2 * line - facade (clamped). Without a line
the kerb sits 3 m out from the facade, and with neither the lane count decides. Pavement = the strip between kerb and facade + every footway /
cycleway line buffered to its width, minus buildings, parks and lawns. Output: flat 2D triangles (dm, base64 Int16) the game drapes on its
ground: 'asph' carriageway, 'pave' pavements and islands, 'kerb' pavement edge segments, 'mark' white paint.
"""
import sys, json, math, base64, collections
import numpy as np
from shapely.geometry import LineString, Polygon, MultiPolygon, Point, box
from shapely.ops import unary_union
import shapely, time
T0 = time.time()
def tick(m): print(f'{time.time() - T0:6.1f}s', m, flush=True)

A = sys.argv[1:]
W = json.load(open(A[0])); OUT = A[1]
BB = tuple(map(float, A[2:6])) if len(A) >= 6 else (-1012, -1000, 1012, 1000)
G = '/home/claude/pori'
s = open(G + '/city.js').read(); C = json.loads(s[s.index('{'):s.rindex('}') + 1])
ST = json.load(open(G + '/styles.json'))['b']
CLIP = box(*BB)

# ---------------------------------------------------------------- inputs
blds = []
for i, b in enumerate(C['b']):
    if ST.get(str(i), {}).get('gone'): continue
    p = b['p']; pts = [(p[k] / 10, p[k + 1] / 10) for k in range(0, len(p), 2)]
    if len(pts) < 3: continue
    pg = Polygon(pts)
    if not pg.is_valid: pg = pg.buffer(0)
    if pg.intersects(CLIP.buffer(60)): blds.append(pg)
BLD = unary_union(blds)
BTREE = shapely.STRtree(blds)
tick('BTREE')

veg = json.load(open(G + '/blender/osm_extract.json'))['veg']
def gm(lon, lat): return ((lon - 21.796) * 53278, (lat - 61.486) * 111437)
greens = []
for v in veg:
    if v['v'] not in ('lu:grass', 'le:park', 'na:wood', 'lu:forest', 'le:playground', 'lu:flowerbed', 'lu:meadow', 'na:grassland', 'na:scrub', 'le:pitch'): continue
    g = [gm(*q) for q in v['g']]
    if len(g) < 3: continue
    pg = Polygon(g)
    if not pg.is_valid: pg = pg.buffer(0)
    if pg.intersects(CLIP.buffer(30)): greens.append(pg)
GREEN = unary_union(greens)
tick('GREEN')

MOTOR = {'primary': 2, 'secondary': 2, 'tertiary': 2, 'residential': 2, 'unclassified': 2, 'living_street': 2, 'trunk': 2,
         'primary_link': 1, 'secondary_link': 1, 'tertiary_link': 1, 'trunk_link': 1}
DEFHW = {'primary': 4.5, 'secondary': 4.5, 'tertiary': 4.0, 'residential': 3.5, 'unclassified': 3.25, 'living_street': 3.0, 'trunk': 5.0}
roads, sidel, walks, islands, squares, parking, pedl, peda = [], [], [], [], [], [], [], []
for w in W:
    t = w['t']; g = [tuple(q) for q in w['g']]
    if len(g) < 2: continue
    h = t.get('h')
    if t.get('a') == 'traffic_island' and len(g) >= 4: islands.append(Polygon(g).buffer(0)); continue
    if t.get('pl') == 'square' or (h == 'pedestrian' and t.get('ar') == 'yes'):
        if len(g) >= 4: squares.append(Polygon(g).buffer(0))
        continue
    if h == 'pedestrian' and t.get('am') == 'marketplace' and len(g) >= 4: peda.append(Polygon(g).buffer(0)); continue   # Kauppatori
    if h == 'pedestrian' and t.get('su') == 'paving_stones' and not t.get('tu'): pedl.append(LineString(g))           # Yrjönkatu, Itäpuisto (Eetunaukio)
    if t.get('am') == 'parking':
        if len(g) >= 4: parking.append(Polygon(g).buffer(0))
        continue
    if t.get('br') or t.get('tu') or (t.get('ly') and t.get('ly') != '0'): continue
    L = LineString(g)
    if not L.intersects(CLIP.buffer(40)): continue
    if h in MOTOR: roads.append((L, t))
    elif h in ('footway', 'cycleway', 'path', 'pedestrian', 'steps'):
        wd = 3.0 if h == 'cycleway' else (2.4 if t.get('f') == 'sidewalk' else 2.0)
        if h == 'pedestrian': wd = 4.0
        walks.append((L, t, wd))
        if t.get('f') in ('sidewalk',) or h == 'cycleway' or (h == 'footway' and t.get('f') != 'crossing'): sidel.append(L)
SQ = unary_union(squares) if squares else Polygon()
PK = unary_union(parking) if parking else Polygon()
STREE = shapely.STRtree(sidel)
tick('STREE')

def ray_hit(p, n, geoms, tree, dmin, dmax):
    """distance along the ray p + n*d (dmin..dmax) to the first geometry hit, or None"""
    seg = LineString([(p[0] + n[0] * dmin, p[1] + n[1] * dmin), (p[0] + n[0] * dmax, p[1] + n[1] * dmax)])
    best = None
    for k in tree.query(seg):
        x = seg.intersection(geoms[k].boundary if geoms[k].geom_type == 'Polygon' else geoms[k])
        if x.is_empty: continue
        for part in getattr(x, 'geoms', [x]):
            for cx, cy in part.coords:
                d = math.hypot(cx - p[0], cy - p[1])
                if best is None or d < best: best = d
    return best

# ---------------------------------------------------------------- carriageways: measured half widths per side
carr = []; log = []
for L, t in roads:
    h = t['h']; lanes = int(t['l']) if t.get('l', '').isdigit() else None
    one = t.get('o') == 'yes'
    dflt = DEFHW.get(h, 3.0) if not one else max(2.75, 1.6 * (lanes or 1) + 0.6)
    if lanes and not one: dflt = max(dflt, 1.6 * lanes + 0.4)
    if h.endswith('_link'): dflt = 3.0
    lo, hi = (2.6 if not one else 2.2), dflt + 4.5
    side = {1: [], -1: []}
    n = max(2, int(L.length / 3))
    for k in range(n):
        a = L.interpolate((k + 0.5) / n, normalized=True); b = L.interpolate(min(L.length, (k + 0.5) / n * L.length + 0.5))
        c0 = L.interpolate(max(0, (k + 0.5) / n * L.length - 0.5))
        dx, dy = b.x - c0.x, b.y - c0.y; ll = math.hypot(dx, dy) or 1; nx, ny = -dy / ll, dx / ll    # left normal
        for sg in (1, -1):
            nn = (nx * sg, ny * sg)
            ds = ray_hit((a.x, a.y), nn, sidel, STREE, 2.0, 16.0)
            db = ray_hit((a.x, a.y), nn, blds, BTREE, 2.5, 30.0)
            if ds is not None and db is not None and db > ds and db - ds < 6.5: kb = 2 * ds - db       # line in the middle of a pavement up to the facade
            elif ds is not None: kb = ds - 1.6
            elif db is not None and db < dflt + 7: kb = db - 3.0
            else: kb = None
            if kb is not None: side[sg].append(min(hi, max(lo, kb)))
    hw = {}
    for sg in (1, -1):
        v = sorted(side[sg]); hw[sg] = v[len(v) // 2] if len(v) >= 2 else dflt
    log.append((t.get('n'), h, round(hw[1], 1), round(hw[-1], 1)))
    left = L.buffer(hw[1], cap_style='flat', join_style='round', single_sided=True)
    right = L.buffer(-hw[-1], cap_style='flat', join_style='round', single_sided=True)
    carr.append(unary_union([left, right]).buffer(0.05))
    # round end caps where the way just ends (dead ends, map edge): a disc keeps junction pieces connected
    for e in (L.coords[0], L.coords[-1]): carr.append(Point(e).buffer(min(hw[1], hw[-1]) * 0.98))
CARR = unary_union(carr)
tick('CARR')
CARR = CARR.buffer(2.5, join_style='round').buffer(-2.5, join_style='round')      # kerb radii at the junctions
CARR = CARR.difference(BLD.buffer(0.8)).difference(SQ)
ISL = unary_union([i.intersection(CARR.buffer(1)) for i in islands]) if islands else Polygon()
CARR = CARR.difference(ISL)
tick('CARR')

# ---------------------------------------------------------------- stone paving (owner 18.11.2026): the pedestrian streets wall to wall, Eetunaukio, Kauppatori
STONE = unary_union([L.buffer(13.0, cap_style='flat') for L in pedl] + [Point(17.7, -72.8).buffer(30)] + [a.buffer(1.0) for a in peda]) if pedl or peda else Polygon()
STONE = STONE.difference(CARR.buffer(0.2)).difference(BLD).difference(GREEN.buffer(-0.3)).intersection(CLIP)
STONE = unary_union([g for g in getattr(STONE, 'geoms', [STONE]) if g.area > 30]).buffer(-0.3).buffer(0.3).simplify(0.2) if not STONE.is_empty else STONE

# ---------------------------------------------------------------- pavements
walkp = [L.buffer(wd / 2, cap_style='flat') for L, t, wd in walks]
WALK = unary_union(walkp) if walkp else Polygon()
strip = CARR.buffer(7.0, join_style='mitre').difference(CARR)
PAVE = unary_union([strip, WALK.intersection(CARR.buffer(12.0)), ISL])
PAVE = PAVE.difference(CARR).difference(BLD).difference(GREEN.buffer(-0.3)).difference(SQ).difference(PK)
PAVE = PAVE.difference(STONE).buffer(-0.35).buffer(0.35)
tick('PAVE')
PAVE = PAVE.intersection(CLIP).simplify(0.25); CARR = CARR.intersection(CLIP).simplify(0.2)
FLATW = WALK.difference(CARR.buffer(12.0)).difference(BLD).intersection(CLIP).buffer(-0.2).buffer(0.2)   # paths in parks: flat, not raised

# ---------------------------------------------------------------- zebra crossings: footway/cycleway lines crossing the carriageway
marks = []; RAMPS = []   # crossing ends: (kerb point, inward unit, lateral unit, half width)
for L, t, wd in walks:
    x = L.intersection(CARR)
    for part in getattr(x, 'geoms', [x]):
        if part.is_empty or part.geom_type != 'LineString' or part.length < 4 or part.length > 30: continue
        (ax, ay), (bx, by) = part.coords[0], part.coords[-1]; dx, dy = bx - ax, by - ay; ll = math.hypot(dx, dy)
        ux, uy = dx / ll, dy / ll; nx, ny = -uy, ux; hw = 1.5 if t.get('h') != 'cycleway' else 1.75
        RAMPS.append((ax, ay, -ux, -uy, nx, ny, hw)); RAMPS.append((bx, by, ux, uy, nx, ny, hw))      # kerb drops at both ends
        k = 0.4
        while k + 0.5 < ll - 0.4:
            a0, a1 = k, k + 0.5
            marks.append(Polygon([(ax + ux * a0 + nx * hw, ay + uy * a0 + ny * hw), (ax + ux * a1 + nx * hw, ay + uy * a1 + ny * hw),
                                  (ax + ux * a1 - nx * hw, ay + uy * a1 - ny * hw), (ax + ux * a0 - nx * hw, ay + uy * a0 - ny * hw)]))
            k += 1.0
# dashed white centre lines on roads with two marked lanes or more
for L, t in roads:
    if not (t.get('l', '').isdigit() and int(t['l']) >= 2): continue
    d = 2.0
    while d + 3 < L.length:
        seg = shapely.ops.substring(L, d, d + 3.0); marks.append(seg.buffer(0.06, cap_style='flat')); d += 9.0
MARK = unary_union(marks).intersection(CARR.buffer(-0.3)) if marks else Polygon()
tick('MARK')

# ---------------------------------------------------------------- lowered kerbs at the crossings (owner 18.11.2026)
# The pavement dips to 3 cm above the asphalt over the crossing width (+ 0.25 m), climbs back over RD m inwards and over RF m to the sides.
RD, RF = 1.4, 1.0
rz = []
for ex, ey, ux, uy, nx, ny, hw in RAMPS:
    RW_ = hw + 0.25 + RF
    rz.append(Polygon([(ex - ux * 0.4 + nx * RW_, ey - uy * 0.4 + ny * RW_), (ex + ux * RD + nx * RW_, ey + uy * RD + ny * RW_),
                       (ex + ux * RD - nx * RW_, ey + uy * RD - ny * RW_), (ex - ux * 0.4 - nx * RW_, ey - uy * 0.4 - ny * RW_)]))
RZ = unary_union(rz) if rz else Polygon()
RTREE = shapely.STRtree(rz) if rz else None
def ramp_h(x, y):
    """height share of the full kerb at (x, y): 0 = lowered, 1 = full pavement height"""
    h = 1.0
    if RTREE is None: return h
    for k in RTREE.query(Point(x, y).buffer(0.01)):
        ex, ey, ux, uy, nx, ny, hw = RAMPS[k]; px, py = x - ex, y - ey
        din, lat = px * ux + py * uy, abs(px * nx + py * ny)
        h = min(h, max(min(1.0, max(0.0, din) / RD), min(1.0, max(0.0, lat - hw - 0.25) / RF)))
    return h
RAMP_P = PAVE.intersection(RZ); RAMP_K = STONE.intersection(RZ)
PAVE = PAVE.difference(RZ); STONE = STONE.difference(RZ)
tick('RAMPS ' + str(len(RAMPS)))

# ---------------------------------------------------------------- triangulate (max ~4 m triangles so they follow the ground) and pack
def tri(geom, step=6.0):
    out = []
    geom = geom.buffer(0)
    if geom.is_empty: return out
    x0, y0, x1, y1 = geom.bounds
    cells = []
    for gx in np.arange(math.floor(x0 / 48) * 48, x1, 48):
        for gy in np.arange(math.floor(y0 / 48) * 48, y1, 48):
            c = geom.intersection(box(gx, gy, gx + 48, gy + 48))
            if not c.is_empty: cells.append(c)
    for c in cells:
        c = shapely.segmentize(c, step)
        for pg in getattr(c, 'geoms', [c]):
            if pg.geom_type != 'Polygon' or pg.area < 0.02: continue
            T = shapely.constrained_delaunay_triangles(pg)
            for tr in T.geoms:
                q = list(tr.exterior.coords)[:3]
                # orient counter-clockwise
                if (q[1][0] - q[0][0]) * (q[2][1] - q[0][1]) - (q[1][1] - q[0][1]) * (q[2][0] - q[0][0]) < 0: q = [q[0], q[2], q[1]]
                for x, y in q: out += [round(x * 10), round(y * 10)]
    return out

def edges(geom, step=8.0):
    """pavement outline segments, oriented with the pavement on the left (dm)"""
    out = []; BB3 = BLD.buffer(0.3); shapely.prepare(BB3)
    geom = shapely.segmentize(geom.buffer(0), step); geom = shapely.geometry.polygon.orient(geom, 1.0) if geom.geom_type == 'Polygon' else MultiPolygon([shapely.geometry.polygon.orient(p, 1.0) for p in geom.geoms])
    for pg in getattr(geom, 'geoms', [geom]):
        for ring in [pg.exterior] + list(pg.interiors):
            c = list(ring.coords)
            for a, b in zip(c[:-1], c[1:]):
                m = Point((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
                if BB3.contains(m): continue            # against a facade: no kerb face
                out += [round(a[0] * 10), round(a[1] * 10), round(b[0] * 10), round(b[1] * 10)]
    return out

def tri_h(geom, step=0.9):
    """fine triangles with a height share per vertex: x dm, y dm, h * 1000"""
    out = []; g = shapely.segmentize(geom.buffer(0), step)
    for pg in getattr(g, 'geoms', [g]):
        if pg.geom_type != 'Polygon' or pg.area < 0.02: continue
        # interior points too, so the slope is smooth inside
        x0, y0, x1, y1 = pg.bounds; pts = [Point(x, y) for x in np.arange(x0 + step / 2, x1, step) for y in np.arange(y0 + step / 2, y1, step)]
        inner = [q for q in pts if pg.buffer(-0.08).contains(q)]
        T = shapely.delaunay_triangles(shapely.MultiPoint(list(pg.exterior.coords)[:-1] + [c for r in pg.interiors for c in list(r.coords)[:-1]] + [(q.x, q.y) for q in inner]))
        for tr in T.geoms:
            if not pg.buffer(0.02).contains(tr.centroid): continue
            q = list(tr.exterior.coords)[:3]
            if (q[1][0] - q[0][0]) * (q[2][1] - q[0][1]) - (q[1][1] - q[0][1]) * (q[2][0] - q[0][0]) < 0: q = [q[0], q[2], q[1]]
            for x, y in q: out += [round(x * 10), round(y * 10), round(ramp_h(x, y) * 1000)]
    return out

def edges_h(geom):
    """kerb segments with the kerb top height share at both ends: x1 y1 h1 x2 y2 h2; densified where the kerb is lowered"""
    out, full = [], []; BB3 = BLD.buffer(0.3); shapely.prepare(BB3); RZp = RZ.buffer(0.5); shapely.prepare(RZp)
    geom = shapely.segmentize(geom.buffer(0), 8.0)
    geom = shapely.geometry.polygon.orient(geom, 1.0) if geom.geom_type == 'Polygon' else MultiPolygon([shapely.geometry.polygon.orient(p, 1.0) for p in geom.geoms])
    for pg in getattr(geom, 'geoms', [geom]):
        for ring in [pg.exterior] + list(pg.interiors):
            c = list(ring.coords)
            for a, b in zip(c[:-1], c[1:]):
                m = Point((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
                if BB3.contains(m): continue
                seg = LineString([a, b]); n = max(1, int(seg.length / 0.8)) if RZp.intersects(seg) else 1
                P = [seg.interpolate(k / n, normalized=True) for k in range(n + 1)]
                for q0, q1 in zip(P[:-1], P[1:]):
                    h0, h1 = ramp_h(q0.x, q0.y), ramp_h(q1.x, q1.y)
                    if h0 > 0.999 and h1 > 0.999: full += [round(q0.x * 10), round(q0.y * 10), round(q1.x * 10), round(q1.y * 10)]
                    else: out += [round(q0.x * 10), round(q0.y * 10), round(h0 * 1000), round(q1.x * 10), round(q1.y * 10), round(h1 * 1000)]
    return full, out

# ---------------------------------------------------------------- one-way streets for the game's street graph (CITY.r segments)
ROUND = {4445264,5071122,5071124,5410262,46115386,302861256,302861258,302861265,302861267,302861268,302861271,302923083,302923093,519692022,519692026,
         519692027,525420999,525421000,1137365068,1137365069,1231162792,1238644900,1238644901,1240126246,1240362611,1187426430,6022401,41757090,46124957,
         46128379,46128380,302770115,302772031,302772033,302923105,383336587,386333303,386333304,386333305,386333306,1240398064,5867771,23898487,302709989,
         302709994,302755559,302760330,302923080,302923082,302923117,302923119,1240088656,1240375897,1240376442}   # junction=roundabout (implies one-way)
ONE = []
for w in W:
    t = w['t']
    if t.get('h') not in MOTOR or len(w['g']) < 2: continue
    o = t.get('o'); sg = 1 if (o in ('yes', '1', 'true') or w['id'] in ROUND) else -1 if o == '-1' else 0
    if sg: ONE.append((LineString(w['g']), sg))
OTREE = shapely.STRtree([L for L, _ in ONE]) if ONE else None
ow = []
for ri, r in enumerate(C['r']):
    if not r.get('k') or OTREE is None: continue
    P = r['p']
    for si in range(len(P) // 2 - 1):
        ax, ay, bx, by = P[si * 2], P[si * 2 + 1], P[si * 2 + 2], P[si * 2 + 3]; L = math.hypot(bx - ax, by - ay)
        if L < 0.5: continue
        m = Point((ax + bx) / 2, (ay + by) / 2); best = None
        for k in OTREE.query(m.buffer(4.0)):
            Lw, sg = ONE[k]; d = Lw.distance(m)
            if d > 4.0: continue
            u = Lw.project(m); q0, q1 = Lw.interpolate(max(0, u - 1)), Lw.interpolate(min(Lw.length, u + 1))
            tx, ty = q1.x - q0.x, q1.y - q0.y; tl = math.hypot(tx, ty) or 1
            c = ((bx - ax) * tx + (by - ay) * ty) / (L * tl)
            if abs(c) > 0.85 and (best is None or d < best[0]): best = (d, sg * (1 if c > 0 else -1))
        if best: ow += [ri, si, best[1]]
print('one-way segments', len(ow) // 3)

# ---------------------------------------------------------------- trees standing on the carriageway: to the pavement edge, 0.8 m in from the kerb
tmv = []
PI = PAVE.buffer(-0.8); shapely.prepare(CARR)
from shapely.ops import nearest_points
for i in range(len(C['t']) // 2):
    x, y = C['t'][i * 2], C['t'][i * 2 + 1]; pt = Point(x, y)
    if not CLIP.contains(pt) or not CARR.contains(pt): continue
    q = nearest_points(PI, pt)[0]
    if q.distance(pt) < 9: tmv += [i, round(q.x * 10), round(q.y * 10)]
    else: tmv += [i, -32768, -32768]                    # nowhere near a pavement: drop it
print('trees moved', len(tmv) // 3)

# ---------------------------------------------------------------- 0.5 m raster: R = contact shade at the house walls, G = street surface (no grass tufts there)
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt
PX = 0.5; RW, RH = int((BB[2] - BB[0]) / PX), int((BB[3] - BB[1]) / PX)
def rast(geoms, img=None):
    img = img or Image.new('L', (RW, RH), 0); d = ImageDraw.Draw(img)
    for g in geoms:
        for pg in getattr(g, 'geoms', [g]):
            if pg.geom_type != 'Polygon' or pg.is_empty: continue
            d.polygon([((x - BB[0]) / PX, (BB[3] - y) / PX) for x, y in pg.exterior.coords], fill=255)
            for r in pg.interiors: d.polygon([((x - BB[0]) / PX, (BB[3] - y) / PX) for x, y in r.coords], fill=0)
    return img
bm = np.asarray(rast(blds)) > 0
dist = distance_transform_edt(~bm) * PX
ao = 1.0 - 0.42 * np.exp(-dist / 0.8)
sm = np.asarray(rast([CARR, PAVE, STONE, RAMP_P, RAMP_K, ISL]))
Image.fromarray(np.stack([(ao * 255).astype(np.uint8), sm, np.zeros_like(sm)], -1)).save(OUT.replace('.js', '_ao.png'), optimize=True)

def b64(a): return base64.b64encode(np.array(a, dtype=np.int16).tobytes()).decode()
KF, KH = edges_h(unary_union([PAVE, STONE, RAMP_P, RAMP_K]))
R = dict(asph=tri(CARR), pave=tri(PAVE), kivi=tri(STONE), kerb=KF, kerbh=KH, mark=tri(MARK, 50),
         rampp=tri_h(RAMP_P), rampk=tri_h(RAMP_K))
js = 'export default ' + json.dumps({k: b64(v) for k, v in R.items()} | {'bb': BB, 'ow': b64(ow), 'tmv': base64.b64encode(np.array(tmv, dtype=np.int32).tobytes()).decode(), 'aopx': PX}) + ';\n'
open(OUT, 'w').write(js)
print('carriageway m2', round(CARR.area), 'pavement m2', round(PAVE.area), 'paths', round(FLATW.area), 'marks', round(MARK.area),
      {k: len(v) for k, v in R.items()}, 'KB', len(js) // 1024)
json.dump(log, open('/home/claude/work/road_widths.json', 'w'), ensure_ascii=False, indent=0)
import pickle; pickle.dump(dict(RAMPS=RAMPS, STONE=STONE, CARR=CARR, PAVE=PAVE, FLATW=FLATW, MARK=MARK, ISL=ISL), open('/home/claude/work/roads_geom.pkl', 'wb'))
