"""Find parallel-parked cars along kerbs directly from the aerial image.
For every street (residential, tertiary, unclassified, living street; secondary only in the grid centre) and both sides,
each candidate kerb offset is scanned in 0.5 m steps. A car is a 3.6-5.6 m run of pixels that clearly differs from the
street's own asphalt but is not green (trees, grass) and not long (shadows, markings, kerbs).
The offset that holds the most cars on that side is taken as the parking lane. Output: data/kerb_cars.json"""
import json, math
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
LON0, LAT0, MX, MY = 21.796, 61.486, 53278.0, 111437.0
HW, YS, YN = 1012.282, -947.2145, 1281.5255
IMG = Image.open('/home/claude/data/orto_all.png').convert('RGB'); IW, IH = IMG.size; PX = IMG.load()
def pix(x, y):
    u, v = (x + HW) / (2 * HW) * IW, (YN - y) / (YN - YS) * IH
    if not (1 <= u < IW - 1 and 1 <= v < IH - 1): return None
    return PX[int(u), int(v)]
els = json.load(open('/home/claude/data/osm_wide.json'))['elements']
nodes = {e['id']: e for e in els if e['type'] == 'node'}
def wpts(w): return [((nodes[i]['lon'] - LON0) * MX, (nodes[i]['lat'] - LAT0) * MY) for i in w['nodes'] if i in nodes]
C = json.loads(open('/home/claude/pori/city.js').read()[len('export default '):-2])
def pip(x, y, poly):
    r = False; j = len(poly) - 1
    for i in range(len(poly)):
        a, b = poly[i], poly[j]
        if (a[1] > y) != (b[1] > y) and x < (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]: r = not r
        j = i
    return r
G = 25.0; BG = {}
for b in C['b']:
    q = b['p']; p = [(q[i] / 10, q[i + 1] / 10) for i in range(0, len(q), 2)]; xs = [a[0] for a in p]; ys = [a[1] for a in p]
    for i in range(int((min(xs) - 2) // G), int((max(xs) + 2) // G) + 1):
        for j in range(int((min(ys) - 2) // G), int((max(ys) + 2) // G) + 1): BG.setdefault((i, j), []).append(p)
def in_building(x, y): return any(pip(x, y, p) for p in BG.get((int(x // G), int(y // G)), []))
NOPARK = {}; PATHS = {}
for e in els:
    t = e.get('tags', {})
    if e['type'] != 'way': continue
    green = t.get('leisure') in ('park', 'garden', 'playground', 'pitch') or t.get('landuse') in ('grass', 'recreation_ground', 'cemetery') or t.get('place') == 'square' \
        or t.get('amenity') == 'grave_yard' or (t.get('highway') == 'pedestrian' and t.get('area') == 'yes')
    p = wpts(e)
    if len(p) < 3 and green: continue
    if green and e['nodes'][0] == e['nodes'][-1]:
        xs = [q[0] for q in p]; ys = [q[1] for q in p]
        for i in range(int(min(xs) // G), int(max(xs) // G) + 1):
            for j in range(int(min(ys) // G), int(max(ys) // G) + 1): NOPARK.setdefault((i, j), []).append(p)
    if t.get('highway') in ('footway', 'cycleway', 'path', 'pedestrian', 'steps') and len(p) >= 2:
        for a, b in zip(p[:-1], p[1:]):
            for i in range(int((min(a[0], b[0]) - 3) // G), int((max(a[0], b[0]) + 3) // G) + 1):
                for j in range(int((min(a[1], b[1]) - 3) // G), int((max(a[1], b[1]) + 3) // G) + 1): PATHS.setdefault((i, j), []).append((a, b))
def on_path(x, y, r=1.7):
    for a, b in PATHS.get((int(x // G), int(y // G)), []):
        dx, dy = b[0] - a[0], b[1] - a[1]; L2 = dx * dx + dy * dy or 1e-9; t = max(0, min(1, ((x - a[0]) * dx + (y - a[1]) * dy) / L2))
        if math.hypot(a[0] + dx * t - x, a[1] + dy * t - y) < r: return True
    return False
def in_green(x, y): return any(pip(x, y, p) for p in NOPARK.get((int(x // G), int(y // G)), []))
TG = {}
for i in range(0, len(C['t']), 2):
    x, y = C['t'][i], C['t'][i + 1]; TG.setdefault((int(x // 10), int(y // 10)), []).append((x, y))
def near_tree(x, y, r=3.2):
    return any(math.hypot(x - a, y - b) < r for i in (-1, 0, 1) for j in (-1, 0, 1) for a, b in TG.get((int(x // 10) + i, int(y // 10) + j), []))
grid_centre = lambda x, y: abs(x) < 360 and -660 < y < 520
inside_core = lambda x, y: abs(x) < HW - 5 and YS + 5 < y < YN - 5

# street segments with their junction ends (no parking within 9 m of a junction)
deg = {}
ways = []
for e in els:
    t = e.get('tags', {}); h = t.get('highway')
    if e['type'] == 'way' and h in ('residential', 'tertiary', 'unclassified', 'living_street', 'secondary', 'primary', 'trunk', 'service', 'pedestrian'):
        for nid in e['nodes']: deg[nid] = deg.get(nid, 0) + 1
        if h in ('residential', 'tertiary', 'unclassified', 'living_street', 'secondary') and t.get('area') != 'yes' and t.get('tunnel') != 'yes' and t.get('bridge') != 'yes':
            ways.append((e, h))
OFF = {'residential': (2.6, 7.0), 'unclassified': (2.6, 7.0), 'living_street': (2.2, 6.0), 'tertiary': (3.2, 8.0), 'secondary': (4.2, 9.5)}
cars = []
def colour_dist(a, b): return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))
for e, h in ways:
    p = wpts(e); ids = [i for i in e['nodes'] if i in nodes]
    junction = [((nodes[i]['lon'] - LON0) * MX, (nodes[i]['lat'] - LAT0) * MY) for i in ids if deg.get(i, 0) > 1]
    for a, b in zip(p[:-1], p[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L < 12: continue
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        if not inside_core(*mid) or (h == 'secondary' and not grid_centre(*mid)): continue
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L; nx, ny = uy, -ux                       # n points to the right of the way
        lo, hi = OFF[h]
        for side in (1, -1):
            best = None
            o = lo
            while o <= hi + 1e-6:
                ts = [k * 0.5 for k in range(int(L / 0.5) + 1)]
                samp = []
                for tt in ts:
                    x, y = a[0] + ux * tt + nx * o * side, a[1] + uy * tt + ny * o * side
                    q = [pix(x + nx * dd, y + ny * dd) for dd in (-0.45, 0, 0.45)]
                    if None in q: samp.append(None); continue
                    samp.append(tuple(sum(c[i] for c in q) / 3 for i in range(3)))
                good = [s for s in samp if s]
                if len(good) < 10: o += 0.5; continue
                ref = tuple(sorted(s[i] for s in good)[len(good) // 2] for i in range(3))     # the asphalt itself
                if max(ref) - min(ref) > 26 or ref[1] > ref[0] + 8 or ref[0] - ref[2] > 16 or not (55 < sum(ref) / 3 < 165): o += 0.5; continue   # not an asphalt lane (gravel, paving and grass are warmer or lighter)
                hit = []
                for s in samp:
                    if not s: hit.append(False); continue
                    green = s[1] > s[0] + 6 and s[1] > s[2] + 6
                    hit.append(colour_dist(s, ref) > 38 and not green)
                runs = []; k = 0
                while k < len(hit):
                    if hit[k]:
                        j = k
                        while j + 1 < len(hit) and (hit[j + 1] or (j + 2 < len(hit) and hit[j + 2])): j += 1
                        ln = (j - k + 1) * 0.5
                        if 3.4 <= ln <= 5.8: runs.append((ts[k] + ts[j]) / 2)
                        k = j + 1
                    else: k += 1
                frac_hit = sum(hit) / max(1, len(hit))
                if runs and frac_hit < 0.75 and (not best or len(runs) >= len(best[1])): best = (o, runs, ref)   # ties go to the outer lane, i.e. the kerb
                o += 0.5
            if not best or len(best[1]) < 2: continue                                           # a lone blob is more likely clutter
            o, runs, ref = best
            for tt in runs:
                x, y = a[0] + ux * tt + nx * o * side, a[1] + uy * tt + ny * o * side
                if any(math.hypot(x - jx, y - jy) < 9 for jx, jy in junction): continue
                if in_building(x, y) or near_tree(x, y) or in_green(x, y) or on_path(x, y): continue
                s = pix(x, y); col = (s[0] << 16) | (s[1] << 8) | s[2]
                hd = math.atan2(ux, uy) if side == 1 else math.atan2(-ux, -uy)                    # face the traffic on that side
                cars.append([round(x, 1), round(y, 1), round(hd, 3), col])
json.dump(cars, open('/home/claude/data/kerb_cars.json', 'w'))
print('kerbside cars', len(cars))
