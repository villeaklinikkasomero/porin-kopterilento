"""Kivi-Pori (the stone blocks on Eteläranta, Hallituskatu and Valtakatu, built after the 1852 fire) on the measured LoD2 shells.
Usage: python3 kivi.py ZONE [samples]   (ZONE = kivi0 .. kivi5, or 'list')
Neo-classical / neo-renaissance rendered facades: granite plinth, rusticated ground floor, framed windows with hoods,
storey bands and an eave cornice on the street sides; plainer walls towards the yards."""
import sys, time, json, math
sys.path.insert(0, '/home/claude')
from zones2 import *
import zones2
from shapely.geometry import LineString, Point

ZONESK = {
    'kivi0': [1513, 1249, 1284, 1454, 1281, 1456, 1311, 1308],                       # brewery block, Hotelli Otava, seurakuntatoimisto
    'kivi1': [1292, 1293, 1294, 1296, 1341, 1295, 1576, 1574, 1577, 1622, 1575],                 # Kaupungintalo block
    'kivi2': [1287, 1288, 1285, 1286, 1565, 1289, 1564, 1290, 1559, 8386, 1563, 1562, 1561, 1560, 1744],   # river block east of the Raatihuone
    'kivi3': [1581, 1716, 1586, 1604, 1578, 1603, 1579, 1585, 1583],                                   # Hallituskatu - Valtakatu, east
    'kivi4': [1572, 1573, 1607, 1566, 1567, 8385],                                               # river block at Yrjönkatu
    'kivi5': [1553, 1620, 1550, 1619, 1552, 1551, 1548, 1549],                                   # Signelinna block
    'karhu': [1450, 1451, 1511, 1512, 1515],                                                 # Karhukortteli (2016-2020) on the old brewery site
    'kl0': [1261, 1336, 1337, 1338, 1351, 1357, 1368, 1369, 1370, 1446, 1447, 1448, 1449, 1458, 1461, 1462, 1516, 1517, 1525, 1535],                                                                       # west of Kivi-Pori (modern blocks)
    'kl1': [1297, 1309, 1310, 1352, 1353, 1373, 1374, 1375, 1377, 1398, 1407, 1527, 1528],
}
MODERN = set(ZONESK['kl0'] + ZONESK['kl1']) | {1581, 1603, 1579, 1620, 1548, 1604, 1578, 1716, 1586, 1585, 1550, 1552, 1549, 1553, 1573}

# ---------------------------------------------------------------- streets: a wall faces a street when a named street runs in front of it
_src = open('/home/claude/pori/city.js').read(); _C = json.loads(_src[_src.index('{'):_src.rindex('}') + 1])
ROADS = [LineString([(r['p'][k], r['p'][k + 1]) for k in range(0, len(r['p']), 2)]) for r in _C['r'] if r.get('n') and len(r['p']) >= 4]
def street(mid, n):
    pt = Point(mid[0] + n[0] * 6, mid[1] + n[1] * 6)
    return min(l.distance(pt) for l in ROADS) < 13
zones2.STREET = street

# ---------------------------------------------------------------- facade recipes
KIVIP = ['#e6d3a3', '#d9b98c', '#e8c9b0', '#cfd3c0', '#d8a48f', '#e9e1cc', '#c9a27a', '#e2c27d', '#c3c6bd', '#d9b2a6', '#ead8b8', '#cdbb98']
GRANITE = M('#5b5752', 0.8)
def h01(i, k): x = (i * 2654435761 + k * 40503) & 0xffffffff; x ^= x >> 15; x = (x * 2246822519) & 0xffffffff; x ^= x >> 13; return (x & 0xffffff) / 0xffffff

def klay(bw=3.5, ground=None, first=None, top=None, door_mid=True, gh=4.4, fh=3.9, pair=False, frieze=0, cols=None):
    def L(h):
        nf = max(1, round((h - gh - frieze) / fh) + 1) if h > 6.5 else 1
        rows = [(gh, 'classic', 'G')] + [(fh, 'classic', 'F' if f == 1 else 'T') for f in range(1, nf)]
        if frieze and nf > 1: rows = rows[:nf] + [(frieze, 'classic', 'T')]
        if nf == 1: rows = [(h, 'classic', 'G')]
        cols_ = cols or (lambda c, nb: 'D' if door_mid and nb >= 5 and c == nb // 2 else ('P' if pair else 'W'))
        return dict(bw=bw, rows=rows, cols=cols_, P={}, rowP={'G': dict(ground=True, **(ground or {})), 'F': first or {}, 'T': top or first or {}}, plain=False)
    return L

def classic_spec(i, wall=None, trim=None, h=None, **kw):
    r = [h01(i, k) for k in range(8)]
    wall = wall or KIVIP[int(r[0] * len(KIVIP))]
    trim = trim or ('#f2ede1' if r[1] < 0.7 else '#e9dcc0')
    rust = kw.pop('rust', r[2] < 0.55); garch = kw.pop('garch', r[3] < 0.45); hood = kw.pop('hood', ['pediment', 'cornice', 'cornice', None][int(r[4] * 4)])
    pil = kw.pop('pil', r[5] < 0.3); bw = kw.pop('bw', 3.3 + r[6] * 0.6)
    W, T = M(wall), M(trim)
    dark = M(tuple(c * 0.72 for c in hexlin(wall)))
    ground = dict(plinth_h=0.9, plinth=GRANITE, basement=r[7] < 0.6, rust=rust, rustc=dark, arch=garch, sband=0.32, ww=1.25, wh=2.1, sill=0.85)
    first = dict(hood=hood, apron=hood == 'pediment', pil=pil, ww=1.2, wh=2.1, sill=0.85, sband=0.18 if r[6] < 0.5 else 0)
    top = dict(hood=None, pil=pil, ww=1.15, wh=1.85, sill=0.8)
    ground.update(kw.pop('ground', {})); first.update(kw.pop('first', {})); top.update(kw.pop('top', {}))
    L = klay(bw=bw, ground=ground, first=first, top=top, **kw.pop('lay', {}))
    yard = dict(bw=3.2, rows=[(1, 'classic', 'Y')], cols=lambda c, nb: 'W', P={}, rowP={'Y': dict(surround=0.1, ww=1.0, wh=1.6, sill=0.9)}, plain=False)
    same = kw.pop('yard_same', False)
    def fit(lay_, hh, st):
        if not st and not same:
            nf = max(1, round(hh / 3.6)); return dict(yard, rows=[(3.6, 'classic', 'Y')] * nf)
        return L(hh)
    sp = dict(P=dict(wall=W, trim=T, frame=M('#f4f2ea')), layout=L(h or 10), yard=yard, fit=fit, cornice=(0.42, 0.75, T))
    sp.update(kw)
    return sp

SPECK = {}
# Signelinna, Hallituskatu 2 (Newanderin talo, Signe Hornborg 1890s): salmon render with ochre dressings, dark granite plinth with
# basement windows, rusticated ground floor with round-arched windows, pedimented first-floor windows on ochre aprons, pilasters
_sig = '#d9ac72'
SPECK[1551] = classic_spec(1551, wall='#b5705a', trim=_sig, rust=True, garch=True, hood='pediment', pil=False, bw=3.4,
                           ground=dict(plinth_h=1.6, basement=True, rustc=M('#8c5444'), rust_step=0.36, sband=0.45, wh=2.2),
                           first=dict(apron=True, apron_mat=M(_sig), sband=0.0, wh=2.3, ww=1.25), upper_mat=M('#4e5358', 0.6),
                           top=dict(blank=True, dentils=True, panels=True, panel_mat=M('#c8875f')), lay=dict(gh=6.0, fh=5.6, frieze=2.2), cornice=(0.5, 0.6, M(_sig)))
SPECK[1249] = classic_spec(1249, wall='#e4d09d', trim='#f3eee2', rust=True, garch=True, hood='pediment', pil=False)   # Hotelli Otava
SPECK[1284] = classic_spec(1284, wall='#e7dcc3', trim='#f3eee2', hood='cornice')                                      # Keski-Porin seurakuntatoimisto
SPECK[1513] = classic_spec(1513, wall='#9b4b36', trim='#b9654c', rust=False, garch=True, hood=None, pil=True, bw=4.6, cornice=(0.3, 0.7, M('#7f3d2c')))   # brewery remnant

# Karhukortteli: five apartment buildings (2016-2020) where the Porin Oluttehdas stood. The LoD2 shells and the aerial image still show
# the brewery, so these are built from the OSM footprints and heights: business premises at street level, large windows,
# balconies, dark pitched metal roofs. Wall colours are estimates.
KARHU = {1450: ('#7a4535', 'brick'), 1451: ('#d9d6cf', 'render'), 1511: ('#e8e6e0', 'render'), 1512: ('#8a5a44', 'brick'), 1515: ('#cfc6b6', 'render')}
for i, (wc, kind) in KARHU.items():
    W_ = M(wc, 0.8); rise = 3.2
    SPECK[i] = dict(h=B[i]['h'] - rise, P=dict(wall=W_, sign=SIGNS, gwall=M('#3b3f44', 0.4), fascia=M('#2d3135'), frame=M('#2f3337', 0.5), rail=M('#c9ced2', 0.3, 0.5), slab=M('#e9e9e6')),
                    layout=lay(B[i]['h'] - rise, 'punched', gh=4.4, bw=3.6, fh=3.05, cols=lambda c, nb: 'B' if c % 3 == 1 else 'W', P=dict(ww=2.1, wh=1.9, sill=0.55, nx=2)),
                    roof=dict(kind='gable', rise=rise, mat=M('#34393d', 0.5, 0.3), ov=0.35), footprint=True)

def kspec(i):
    if i in SPECK: return SPECK[i]
    if i in MODERN: return spec_for(i)
    return classic_spec(i)

def build_and_bake(name, ids, samples=16, spec=None):
    spec = spec or kspec
    if os.environ.get('PORI_PHS') and os.path.exists(os.environ['PORI_PHS']):
        ex = {int(k) for k in json.load(open(os.environ['PORI_PHS']))}; ids = [i for i in ids if i not in ex]
    t = time.time()
    for i in ids:
        if RAW.get(i) and not spec(i).get('footprint'): B[i]['h'] = eave_of(i)
    Z = Zone(name, ids); Z.roofflag = any(spec(i).get('roof') for i in ids)
    for i in ids:
        sp = spec(i)
        if RAW.get(i) and not sp.get('footprint'): build_lod2(Z, i, sp)
        else:
            sp2 = dict(sp); sp2['layout'] = sp['fit'](sp['layout'], B[i]['h'], True) if 'fit' in sp else sp['layout']
            build_building(Z, i, sp2)
    context2(Z); pack(Z)
    print('hi', len(Z.hi), 'lo', len(Z.lo), 'exp', len(Z.exp))
    bake_zone(Z, '/home/claude/out', samples=samples)
    print('time', round(time.time() - t))

if __name__ == '__main__':
    name = sys.argv[1]
    if name == 'list':
        for k, v in ZONESK.items(): print(k, v)
        sys.exit()
    build_and_bake(name, ZONESK[name], int(sys.argv[2]) if len(sys.argv) > 2 else 16)
