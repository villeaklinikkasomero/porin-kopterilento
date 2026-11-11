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


def split():
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
        if b.get('k') in (1, 2) or i in ZB or i in phs or b.get('w') in own or b.get('w') in srw: continue
        pts = [(b['p'][k] / 10, b['p'][k + 1] / 10) for k in range(0, len(b['p']), 2)]
        pg = Polygon(pts).buffer(0)
        if pg.area < 25 or any(pg.contains(Point(*p)) for p in LM): continue
        c = pg.centroid
        if i in HIDE and any(j != i and s.contains(c) for j, s in shells): continue        # drawn by the neighbour's LoD2 shell
        u = c.x * math.cos(G) - c.y * math.sin(G); v = c.x * math.sin(G) + c.y * math.cos(G)
        cand.append((i, c.x, c.y, u, v))
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
            name = 'c%03d' % len(zones)
            zones[name] = dict(ids=[t[0] for t in grp], x=round(sum(t[1] for t in grp) / len(grp), 1), y=round(sum(t[2] for t in grp) / len(grp), 1))
    json.dump(dict(version=1, zones=zones), open(MAN, 'w'), separators=(',', ':'))
    print('buildings', len(cand), 'zones', len(zones), '->', MAN)


if __name__ == '__main__':
    if sys.argv[1] == 'split': split(); sys.exit()
    import kivi
    zones = json.load(open(MAN))['zones']; name = sys.argv[1]
    kivi.build_and_bake(name, zones[name]['ids'], int(sys.argv[2]) if len(sys.argv) > 2 else 32, spec=kivi.spec_for)
