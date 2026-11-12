"""Whole-city run: every remaining apartment / commercial building (OSM buildings that are not houses or sheds) gets facades on its
measured LoD2 shell, in automatically split blocks of up to 16 buildings.
  python3 city.py split            -> <game>/city_zones.json  (zone -> building ids + centre; the game streams these blocks by distance)
  python3 city.py c012 [samples]   -> out/bl_c012.js
Buildings already in a hand-made block (ZB in index.html), landmarks, photo facades, special roofs and hidden LoD2 parts are left out."""
import sys, os, json, math, re, pickle
sys.path.insert(0, '/home/claude')
GAME = os.environ.get('PORI_GAME', '/home/claude/pori')
MAN = os.path.join(GAME, 'city_zones.json')
MAXN = 20; CELL = 400.0; G = math.radians(13)


def split(houses=False):
    from shapely.geometry import Polygon, Point
    src = open(os.path.join(GAME, 'city.js')).read(); C = json.loads(src[src.index('{'):src.rindex('}') + 1])
    html = open(os.path.join(GAME, 'index.html')).read()
    ZB = {int(k) for k, v in re.findall(r'(\d+):(\d+)', re.search(r'ZB = \{([^}]*)\}', html).group(1))}
    LM = [tuple(map(float, v)) for v in re.findall(r'\[(-?[\d.]+), (-?[\d.]+)\]', re.search(r'const LMAT = \{([^}]*)\}', html).group(1))]
    own = {int(x) for x in re.findall(r'\d{6,}', re.search(r'OWNROOF = new Set\(\[([^\]]*)\]', html).group(1))} | {1504508728, 1196441531}
    srw = {int(x) for x in re.findall(r'(\d{6,}):', re.search(r'const SRW = \{([^}]*)\}', html).group(1))}
    phs = {int(k) for k in re.findall(r'(\d+): \[\{ t:', re.search(r'let PHS = \{(.*?)\};', html).group(1))}
    pj = os.path.join(GAME, 'phs.json')
    if os.path.exists(pj): phs |= {int(k) for k in json.load(open(pj))}
    RAW = pickle.load(open('/home/claude/mmlproc/raw.pkl', 'rb'))
    L2 = json.loads(open(os.path.join(GAME, 'lod2.js')).read()[len('export default '):-2]); HIDE = set(L2['hide'])
    shells = [(i, Polygon([(p[0], p[1]) for p in r]).buffer(0)) for i, parts in RAW.items() for k, r, _ in parts if k == 'G' and len(r) >= 3]
    cand = []
    for i, b in enumerate(C['b']):
        if (b.get('k') in (1, 2)) != houses or i in ZB or i in phs or b.get('w') in own or b.get('w') in srw: continue
        pts = [(b['p'][k] / 10, b['p'][k + 1] / 10) for k in range(0, len(b['p']), 2)]
        pg = Polygon(pts).buffer(0)
        if pg.area < 25 or any(pg.contains(Point(*p)) for p in LM): continue
        c = pg.centroid
        if i in HIDE and any(j != i and s.contains(c) for j, s in shells): continue        # drawn by the neighbour's LoD2 shell
        u = c.x * math.cos(G) - c.y * math.sin(G); v = c.x * math.sin(G) + c.y * math.cos(G)
        cand.append((i, c.x, c.y, u, v))
    if houses: globals()['MAXN'] = 40
    cells = {}
    for t in cand: cells.setdefault((math.floor(t[3] / CELL), math.floor(t[4] / CELL)), []).append(t)
    def part(ts):
        if len(ts) <= MAXN: return [ts]
        us = [t[3] for t in ts]; vs = [t[4] for t in ts]; k = 3 if max(us) - min(us) >= max(vs) - min(vs) else 4
        ts = sorted(ts, key=lambda t: t[k]); h = len(ts) // 2
        return part(ts[:h]) + part(ts[h:])
    zones = {}
    for key in sorted(cells):
        for grp in part(cells[key]):
            name = ('h%03d' if houses else 'c%03d') % len(zones)
            zones[name] = dict(ids=[t[0] for t in grp], x=round(sum(t[1] for t in grp) / len(grp), 1), y=round(sum(t[2] for t in grp) / len(grp), 1))
    if houses:                                       # keep the apartment / commercial blocks, add the house blocks
        old = json.load(open(MAN))['zones'] if os.path.exists(MAN) else {}
        zones = {**{k: v for k, v in old.items() if not k.startswith('h')}, **zones}
    elif os.path.exists(MAN):
        zones = {**zones, **{k: v for k, v in json.load(open(MAN))['zones'].items() if k.startswith('h')}}
    json.dump(dict(version=1, zones=zones), open(MAN, 'w'), separators=(',', ':'))
    print('buildings', len(cand), 'zones', len(zones), '->', MAN)


# ---------------------------------------------------------------- detached houses and sheds (OSM building=house / shed ...)
HOUSEC = ['#e8d58a', '#f1efe8', '#9b3b2c', '#cfd8c4', '#b9c7cf', '#e3c9a0', '#d6b35e', '#f1efe8', '#a8463a', '#e9e2cf', '#c7cbbf', '#e8d58a']
def house_spec(i):
    import kivi
    from gen import M, MT, hexlin, offset
    b = kivi.B[i]; r = kivi.h01(i, 3); shed = b.get('k') == 2
    import zones2
    lk = zones2.LOOK; e = lk['b'].get(str(i)); wood = lk.get('wood') or []
    def wpick(r_):                                       # locked timber-house palette (oblique photos of Päärnäinen / Kuukkari)
        t = sum(w for _, w in wood); k = r_ * t
        for hx, w in wood:
            k -= w
            if k <= 0: return hx
        return wood[0][0]
    wall = e['w'] if e else '#8f3a2c' if shed and r < 0.7 else wpick(kivi.h01(i, 5)) if wood else HOUSEC[int(kivi.h01(i, 5) * len(HOUSEC))]
    W = MT(wall, 'wood', 0.9); dark = M(tuple(c * 0.62 for c in hexlin(wall)), 0.9)
    h = b['h']; nf = 1 if h < 6.8 else 2          # Kuukkari / Päärnäinen houses are mostly 1.5 storeys: one window row on the eave sides, taller plinth
    rowP = {'G': dict(plinth_h=0.7, ww=1.15, wh=1.35, nx=2), 'U': dict(ww=1.0, wh=1.15, nx=2, frieze=True)}
    def cols(c, nb):
        if nb == 1: return 'E' if not shed else 'e'
        k = 'L' if c == 0 else 'R' if c == nb - 1 else 'W'
        return k.lower() if shed or (k == 'W' and c % 3 == 2 and nb > 3) else k
    rows = [(1, 'wood', 'G')] if nf == 1 else [(1.15, 'wood', 'G'), (1, 'wood', 'U')]
    if nf == 1: rowP['G']['frieze'] = True
    layout = dict(bw=2.9 if not shed else 3.5, rows=rows, cols=cols, P={}, rowP=rowP, plain=False)
    l2 = bool(kivi.RAW.get(i))                         # measured LoD2 shell: walls and gables follow it, the game draws its measured roof
    def gable_ends(Z, pts, hh, P):                      # same pitched roof the game draws for houses: ridge along the long side
        import math
        if len(pts) > 14 or shed or l2: return
        ux, uy, a, bb, cx, cy = kivi.obb(pts); ar = abs(sum(pts[k][0] * pts[(k + 1) % len(pts)][1] - pts[(k + 1) % len(pts)][0] * pts[k][1] for k in range(len(pts)))) / 2
        if not (ar > 0.7 * 4 * a * bb and bb > 1.8): return
        rise = min(4.6, bb * 0.66); vx, vy = -uy, ux; L = lambda x, y, z: (x - Z.cx, y - Z.cy, z)
        for su in (-1, 1):
            p0 = (cx + ux * su * a - vx * bb, cy + uy * su * a - vy * bb); p1 = (cx + ux * su * a + vx * bb, cy + uy * su * a + vy * bb); pt = (cx + ux * su * a, cy + uy * su * a)
            tri = [L(p0[0], p0[1], hh), L(p1[0], p1[1], hh), L(pt[0], pt[1], hh + rise - 0.15)]
            kivi.add_solid(Z, tri if su > 0 else tri[::-1], P['wall'], 0.5)
            kivi.add_solid(Z, [L(p0[0], p0[1], hh - 0.02), L(p1[0], p1[1], hh - 0.02), L(p1[0], p1[1], hh + 0.2), L(p0[0], p0[1], hh + 0.2)], P['trim'], 0.3)
    return dict(P=dict(wall=W, trim=M('#f2f0ea', 0.8), board=dark, frame=M('#f2f0ea')), layout=layout, extra=[gable_ends], footprint=not l2)


if __name__ == '__main__':
    if sys.argv[1] == 'split': split(); sys.exit()
    if sys.argv[1] == 'split-houses': split(houses=True); sys.exit()
    import kivi
    zones = json.load(open(MAN))['zones']; name = sys.argv[1]
    kivi.build_and_bake(name, zones[name]['ids'], int(sys.argv[2]) if len(sys.argv) > 2 else 32, spec=house_spec if name.startswith('h') else kivi.spec_for)
