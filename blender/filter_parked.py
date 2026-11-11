"""Keep only plausible parked cars from the aerial-image detections (pori/parked.js):
  * inside a mapped surface car park (OSM amenity=parking / parking_space): heading snapped to the bays,
    i.e. square to the nearest parking aisle, or to the car park's own axes when it has no aisle;
  * along a street: in the kerb lane of residential / tertiary / unclassified / living streets and
    secondary streets in the grid centre, heading parallel to the street and facing the traffic on that side.
Everything else (yards, roofs, shadows, carriageways, parks, main roads) is dropped.
python3 -I filter_parked.py  ->  pori/parked.js (original kept as data/parked_raw.js)"""
import json, math, os, shutil

SRC = '/home/claude/data/parked_raw.js'
if not os.path.exists(SRC): shutil.copy('/home/claude/pori/parked.js', SRC)
s = open(SRC).read(); A = json.loads(s[s.index('['):s.rindex(']') + 1]); N = len(A) // 4
LON0, LAT0, MX, MY = 21.796, 61.486, 53278.0, 111437.0
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
def seg_d(x, y, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; L2 = dx * dx + dy * dy or 1e-9
    t = max(0.0, min(1.0, ((x - a[0]) * dx + (y - a[1]) * dy) / L2)); px, py = a[0] + dx * t, a[1] + dy * t
    return math.hypot(x - px, y - py), dx, dy, (x - px), (y - py)
G = 25.0
def grid_add(gr, bbox, item):
    for i in range(int(bbox[0] // G), int(bbox[2] // G) + 1):
        for j in range(int(bbox[1] // G), int(bbox[3] // G) + 1): gr.setdefault((i, j), []).append(item)
def bb(p, m=0): xs = [q[0] for q in p]; ys = [q[1] for q in p]; return (min(xs) - m, min(ys) - m, max(xs) + m, max(ys) + m)

# buildings
BG = {}
for b in C['b']:
    q = b['p']; p = [(q[i] / 10, q[i + 1] / 10) for i in range(0, len(q), 2)]; grid_add(BG, bb(p, 1.2), p)
def near_building(x, y, m=1.0):
    for p in BG.get((int(x // G), int(y // G)), []):
        if pip(x, y, p): return True
        for k in range(len(p)):
            if seg_d(x, y, p[k - 1], p[k])[0] < m: return True
    return False

# car parks and their aisles
LOTS = []; LG = {}
for e in els:
    t = e.get('tags', {})
    if e['type'] == 'way' and t.get('amenity') in ('parking', 'parking_space') and t.get('parking') not in ('underground', 'multi-storey', 'rooftop') and e['nodes'][0] == e['nodes'][-1]:
        p = wpts(e)[:-1]
        if len(p) >= 3: LOTS.append({'p': p, 'street': t.get('parking') in ('street_side', 'lane')}); grid_add(LG, bb(p), len(LOTS) - 1)
AISLE = {}
ROADS = []; RG = {}
KERB = {'residential': (2.4, 6.8), 'unclassified': (2.4, 6.8), 'living_street': (2.0, 6.0), 'tertiary': (3.0, 7.5), 'secondary': (4.0, 8.5)}
for e in els:
    t = e.get('tags', {}); h = t.get('highway')
    if e['type'] != 'way' or not h: continue
    p = wpts(e)
    if len(p) < 2: continue
    if h == 'service':
        for a, b2 in zip(p[:-1], p[1:]): grid_add(AISLE, bb([a, b2], 3), (a, b2))
    if h in KERB or h in ('primary', 'trunk', 'primary_link', 'trunk_link', 'secondary_link', 'tertiary_link', 'pedestrian'):
        for a, b2 in zip(p[:-1], p[1:]): grid_add(RG, bb([a, b2], 10), (a, b2, h, t.get('oneway') == 'yes'))

def lot_axes(p):
    best = None
    for i in range(len(p)):
        a, b2 = p[i - 1], p[i]; L = math.hypot(b2[0] - a[0], b2[1] - a[1])
        if L < 2: continue
        ux, uy = (b2[0] - a[0]) / L, (b2[1] - a[1]) / L
        us = [q[0] * ux + q[1] * uy for q in p]; vs = [-q[0] * uy + q[1] * ux for q in p]; ar = (max(us) - min(us)) * (max(vs) - min(vs))
        if not best or ar < best[0]: best = (ar, math.atan2(ux, uy))
    return best[1] if best else 0.0
for L in LOTS: L['ax'] = lot_axes(L['p'])

def snap(h, base, step):
    k = round((h - base) / step); return base + k * step
grid_centre = lambda x, y: abs(x) < 360 and -660 < y < 520

from PIL import Image
Image.MAX_IMAGE_PIXELS = None
HW, YS, YN = 1012.282, -947.2145, 1281.5255
IMG = Image.open('/home/claude/data/orto_all.png').convert('RGB'); IW, IH = IMG.size; PX = IMG.load()
def pix(x, y):
    u, v = int((x + HW) / (2 * HW) * IW), int((YN - y) / (YN - YS) * IH)
    return PX[min(IW - 1, max(0, u)), min(IH - 1, max(0, v))]
def paved(x, y, ux, uy):
    # the kerb lane is asphalt: look ahead and behind the car along the street (gaps between parked cars) and towards the street
    pts = [(x + ux * d + uy * s2, y + uy * d - ux * s2) for d in (-4.5, -3.5, 3.5, 4.5) for s2 in (-0.6, 0, 0.6)]
    good = 0
    for q in pts:
        r, g, b = pix(*q); mx, mn = max(r, g, b), min(r, g, b)
        if mx - mn < 34 and g <= r + 10 and 45 < (r + g + b) / 3 < 205: good += 1
    return good >= len(pts) * 0.6
kept = []; why = {'lot': 0, 'street': 0}
for i in range(N):
    x, y, hd, col = A[i * 4] / 10, A[i * 4 + 1] / 10, A[i * 4 + 2] / 100, A[i * 4 + 3]
    if near_building(x, y, 0.8): continue
    lot = next((LOTS[k] for k in LG.get((int(x // G), int(y // G)), []) if pip(x, y, LOTS[k]['p'])), None)
    # nearest drivable road
    best = None
    for a, b2, h, ow in RG.get((int(x // G), int(y // G)), []):
        d, dx, dy, ox, oy = seg_d(x, y, a, b2)
        if not best or d < best[0]: best = (d, dx, dy, ox, oy, h, ow)
    if best and best[0] < (2.2 if best[5] != 'secondary' else 3.6): continue                 # on the carriageway itself
    if lot and not lot['street']:
        a_best = None                                                                       # bays are square to the nearest aisle
        for a, b2 in AISLE.get((int(x // G), int(y // G)), []):
            d, dx, dy, *_ = seg_d(x, y, a, b2)
            if d < 9 and (not a_best or d < a_best[0]): a_best = (d, math.atan2(dx, dy))
        base = a_best[1] + math.pi / 2 if a_best else lot['ax']
        h2 = snap(hd, base, math.pi / 2) if not a_best else snap(hd, base, math.pi)
        kept.append([x, y, h2, col, 'lot', 2.3]); why['lot'] += 1; continue
    if not best: continue
    d, dx, dy, ox, oy, h, ow = best
    if h not in KERB or (h == 'secondary' and not grid_centre(x, y)): continue
    lo, hi = KERB[h]
    if not (lo <= d <= hi) and not (lot and lot['street']): continue
    along = math.atan2(dx, dy)
    right = (dx * oy - dy * ox) < 0                                                         # car is to the right of the way's direction
    h2 = along if (right or ow) else along + math.pi                                         # face the traffic flowing on that side
    # keep the detector's own heading only if it roughly agrees with the street (rejects shadows and crossing objects)
    dd = abs(((hd - along + math.pi / 2) % math.pi) - math.pi / 2)
    if dd > math.radians(35): continue
    if not paved(x, y, math.sin(along), math.cos(along)): continue
    kept.append([x, y, h2, col, 'street', 4.6]); why['street'] += 1

# thin out overlaps: parallel parked cars need ~5 m, bays ~2.3 m
kept.sort(key=lambda c: (c[4], c[0], c[1])); out = []; OG = {}
for c in kept:
    cell = (int(c[0] // 6), int(c[1] // 6)); ok = True
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            for o in OG.get((cell[0] + i, cell[1] + j), []):
                dx, dy = c[0] - o[0], c[1] - o[1]
                ux, uy = math.sin(c[2]), math.cos(c[2]); along = abs(dx * ux + dy * uy); side = abs(-dx * uy + dy * ux)
                if along < (4.6 if c[4] == 'street' else 4.2) and side < (1.9 if c[4] == 'street' else 2.2): ok = False
    if ok: out.append(c); OG.setdefault(cell, []).append(c)
# lot cars from the detector plus kerbside cars found straight in the image
import random
random.seed(3)
out = [c for c in out if c[4] == 'lot']
for c in out: c[2] += math.pi if random.random() < 0.5 else 0          # nose in or out of the bay
for x, y, hd, col in json.load(open('/home/claude/data/kerb_cars.json')):
    if all(math.hypot(x - o[0], y - o[1]) > 3.5 for o in out if abs(x - o[0]) < 4 and abs(y - o[1]) < 4): out.append([x, y, hd, col, 'street', 4.6])
flat = []
for c in out: flat += [round(c[0] * 10), round(c[1] * 10), round(c[2] * 100), c[3]]
open('/home/claude/pori/parked.js', 'w').write('// parked cars from the aerial image, kept only in car parks and kerbside lanes: x*10, y*10, heading*100, colour\nexport default ' + json.dumps(flat, separators=(',', ':')) + ';\n')
print('raw', N, 'kept', len(out), 'lot', sum(c[4] == 'lot' for c in out), 'street', sum(c[4] == 'street' for c in out))
json.dump([[round(c[0], 1), round(c[1], 1), round(c[2], 3), c[4]] for c in out], open('/home/claude/data/parked_kept.json', 'w'))
