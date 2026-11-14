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
    'p1': [125, 126, 127, 129, 169, 272, 273, 133, 135, 275, 276, 277, 290, 291],                # Antinkatu 21-25 / Mikonkatu (bl_p1.js of 11.11. had no generator left in the repo; 13.11.2026)
    'karhu': [1450, 1451, 1511, 1512, 1515],                                                 # Karhukortteli (2016-2020) on the old brewery site
    'kl0': [1261, 1336, 1337, 1338, 1351, 1357, 1368, 1369, 1370, 1446, 1447, 1448, 1449, 1458, 1461, 1462, 1516, 1517, 1525, 1535],                                                                       # west of Kivi-Pori (modern blocks)
    'kl1': [1297, 1309, 1310, 1352, 1353, 1373, 1374, 1375, 1377, 1398, 1407, 1527, 1528],
}
MODERN = set(ZONESK['kl0'] + ZONESK['kl1']) | (set(ZONESK['p1']) - {276, 133}) | {1581, 1603, 1579, 1620, 1548, 1578, 1716, 1586, 1585, 1550, 1552, 1549, 1553}   # 1573 (low yellow house on Antinkatu) and 1604 (yellow Jugend, Street View 13.11.2026) is classic

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

def klay(bw=3.5, ground=None, first=None, top=None, door_mid=True, gh=4.4, fh=3.9, pair=False, frieze=0, cols=None, nf=None):
    nf0 = nf
    def L(h):
        gh_, fh_ = gh, fh
        if nf0 and nf0 > 1 and h > 6.5:                  # storey count from styles.json (street photos / register): stretch the rows to the wall,
            nf = int(nf0); fh_ = (h - gh - frieze) / (nf - 1)   # a high ground floor (raised on its plinth) takes what a storey cannot
            if fh_ > 4.8: fh_ = 4.4; gh_ = h - frieze - fh_ * (nf - 1)
            elif fh_ < 2.9: fh_ = 2.9; gh_ = max(3.2, h - frieze - fh_ * (nf - 1))
        else:
            nf = max(1, round((h - gh - frieze) / fh) + 1) if h > 6.5 else 1
        rows = [(gh_, 'classic', 'G')] + [(fh_, 'classic', 'F' if f == 1 else 'T') for f in range(1, nf)]
        if frieze and nf > 1: rows = rows[:nf] + [(frieze, 'classic', 'T')]
        if nf0 == 1: nf = 1                              # styles.json f=1 (street photos): one storey even when the LoD2 wall is tall (high roof base, raised plinth)
        if nf == 1: rows = [(h, 'classic', 'G')]
        cols_ = cols or (lambda c, nb: 'D' if door_mid and nb >= 5 and c == nb // 2 else ('P' if pair else 'W'))
        return dict(bw=bw, rows=rows, cols=cols_, P={}, rowP={'G': dict(ground=True, **(ground or {})), 'F': first or {}, 'T': top or first or {}}, plain=False)
    return L

from zones2 import LOOK
def _klook(i):
    """styles.json entry when it is a locked one (street photos, Street View, sources): without 'm' (the automatic colour reading).
    Before 13.11.2026 the Kivi-Pori blocks drew their wall colour from KIVIP by hash and ignored styles.json."""
    e = LOOK['b'].get(str(i)) or {}
    return {} if e.get('m') else e

def classic_spec(i, wall=None, trim=None, h=None, **kw):
    r = [h01(i, k) for k in range(8)]
    lk = _klook(i)
    wall = wall or lk.get('w') or KIVIP[int(r[0] * len(KIVIP))]
    if lk.get('f') and 'nf' not in kw.get('lay', {}): kw['lay'] = dict(kw.get('lay', {}), nf=int(lk['f']))
    trim = trim or ('#f2ede1' if r[1] < 0.7 else '#e9dcc0')
    rust = kw.pop('rust', r[2] < 0.55); garch = kw.pop('garch', r[3] < 0.45); hood = kw.pop('hood', ['pediment', 'cornice', 'cornice', None][int(r[4] * 4)])
    pil = kw.pop('pil', r[5] < 0.3); bw = kw.pop('bw', 3.3 + r[6] * 0.6)
    W, T = (MT(wall, 'brick', 0.8) if lk.get('k') == 'brick' else M(wall)), M(trim)
    dark = M(tuple(c * 0.72 for c in hexlin(wall)))
    ground = dict(plinth_h=0.9, plinth=M(lk['pl'], 0.85) if lk.get('pl') else GRANITE,   # styles.json 'pl': plinth colour from the street photos (painted plinths)
                  basement=r[7] < 0.6, rust=rust, rustc=dark, arch=garch, sband=0.32, ww=1.25, wh=2.1, sill=0.85)
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

def corner_tower(cx, cy, r, z0, z1, wall, trim, dome, n=16):
    """round corner tower above the eaves with an ogee dome and a spire (the LoD2 scan cuts such towers off at the roof)"""
    def ex(Z, *a):
        L = lambda x, y, z: (x - Z.cx, y - Z.cy, z)
        ring = lambda rr: [(cx + rr * math.cos(2 * math.pi * k / n), cy + rr * math.sin(2 * math.pi * k / n)) for k in range(n)]
        def band(r0, r1, za, zb, mat):
            A, Bq = ring(r0), ring(r1)
            for k in range(n):
                a0, b0, a1, b1 = A[k], A[(k + 1) % n], Bq[k], Bq[(k + 1) % n]
                add_solid(Z, [L(*a0, za), L(*b0, za), L(*b1, zb), L(*a1, zb)], mat, 0.5)
        band(r, r, z0, z1, wall)
        for k in range(n):                                                    # dark window slits all round
            if k % 2: continue
            a = 2 * math.pi * (k + 0.5) / n; ca, sa = math.cos(a), math.sin(a); tx, ty = -sa, ca; w = 0.32; rr = r + 0.03
            q0 = (cx + ca * rr - tx * w, cy + sa * rr - ty * w); q1 = (cx + ca * rr + tx * w, cy + sa * rr + ty * w)
            add_solid(Z, [L(*q0, z0 + 0.9), L(*q1, z0 + 0.9), L(*q1, z1 - 0.7), L(*q0, z1 - 0.7)], M('#2c3136', 0.4), 0.5)
        band(r + 0.2, r + 0.2, z1, z1 + 0.35, trim); add_solid(Z, [L(x, y, z1 + 0.35) for x, y in ring(r + 0.2)], trim, 0.4)
        prof = [(r + 0.15, 0.35), (r * 1.02, 0.9), (r * 0.9, 1.6), (r * 0.62, 2.3), (r * 0.3, 2.8), (0.12, 3.15), (0.02, 4.6)]   # ogee dome and spire
        for (ra, za), (rb, zb) in zip(prof, prof[1:]): band(ra, rb, z1 + za, z1 + zb, dome)
    return ex

SPECK = {}
# Signelinna, Hallituskatu 2 (Newanderin talo, Signe Hornborg 1890s): salmon render with ochre dressings, dark granite plinth with
# basement windows, rusticated ground floor with round-arched windows, pedimented first-floor windows on ochre aprons, pilasters
_sig = '#d9ac72'
SPECK[1551] = classic_spec(1551, wall='#b5705a', trim=_sig, rust=True, garch=True, hood='pediment', pil=False, bw=3.4,
                           ground=dict(plinth_h=1.6, basement=True, rustc=M('#8c5444'), rust_step=0.36, sband=0.45, wh=2.2),
                           first=dict(apron=True, apron_mat=M(_sig), sband=0.0, wh=2.3, ww=1.25), upper_mat=M('#4e5358', 0.6),
                           top=dict(blank=True, dentils=True, panels=True, panel_mat=M('#c8875f')), lay=dict(gh=6.0, fh=5.6, frieze=2.2), cornice=(0.5, 0.6, M(_sig)))
# Hotelli Otava (von Heideken 1857, third storey and neo-renaissance dress 1891): salmon render, light dressings, dark sheet roof
SPECK[1249] = classic_spec(1249, wall='#d9967c', trim='#f1e6d6', rust=True, garch=True, hood='cornice', pil=True, bw=3.3,
                           lay=dict(gh=4.2, fh=3.8), roofmat=M('#3f4246', 0.5, 0.3))
# Porin Lyseo (street photos 2026): pink render on a grey granite plinth, white dressings, round-arched windows with white
# surrounds on both floors, moulded cornice, black sheet-metal hip roof
_ly = dict(wall='#ecc3cb', trim='#f6f1ec', rust=False, garch=True, hood='cornice', pil=True, bw=3.6, yard_same=True,
           ground=dict(plinth_h=1.5, plinth=M('#77777a', 0.8), basement=True, arch=True, ww=1.35, wh=2.4, sband=0.35),
           first=dict(arch=True, ww=1.35, wh=2.5, sband=0.25), top=dict(arch=True, ww=1.3, wh=2.2),
           lay=dict(gh=5.2, fh=4.8), cornice=(0.55, 0.8, M('#f6f1ec')), roofmat=M('#2e3033', 0.45, 0.4))
# the 1950s wing on the same footprint (west part of the north wing and the west wing): yellow render, three plain storeys, red sheet roof.
# Which part is yellow is read from the yard photo and the roof seam in the aerial image (street-grid coordinate u < -486): an estimate.
_lyy = dict(spec_for(1351)); _lyy['P'] = dict(_lyy['P'], wall=M('#e9c46a'), frame=M('#f4f2ea')); _lyy['roofmat'] = M('#a33b2e', 0.55, 0.2)
_lyy['layout'] = lay(11, 'punched', gh=0, bw=3.4, fh=3.5, P=dict(ww=1.7, wh=1.7, nx=2)); _lyy.pop('fit', None); _lyy.pop('yard', None)
_ly['alt'] = lambda x, y: _lyy if x * 0.9744 - y * 0.225 < -486.6 else None
SPECK[1351] = classic_spec(1351, **_ly); SPECK[1353] = classic_spec(1353, **dict(_ly, lay=dict(gh=4.6, fh=4.2)))
SPECK[1311] = classic_spec(1311, wall='#e3d8b4', trim='#f4f1ea', rust=False, garch=False, hood=None, pil=False)   # Valtakatu 17-19 side: long 2-storey pale yellow house, plain windows (Street View 13.11.2026)
SPECK[1574] = classic_spec(1574, wall='#e3d7b9', trim='#f4f1ea', rust=False, garch=False, hood=None, pil=False)   # Valtakatu 9: small 1-storey stucco house with a gable, plain windows (Street View 13.11.2026)
SPECK[1560] = classic_spec(1560, trim='#f4f1ea', rust=True, garch=True, hood='cornice', pil=True)   # Antinkatu 1 / Eteläranta: salmon render, white dressings (Street View 13.11.2026)
SPECK[1604] = classic_spec(1604, trim='#b0603f', rust=False, garch=False, hood='cornice', pil=False, top=dict(hood='cornice'))  # yellow Jugend house on Antinkatu: brick-red arched lintels with keystones over the windows on every floor (Street View 14.11.2026); gables from the LoD2 shell
SPECK[1284] = classic_spec(1284, wall='#e4dcc6', trim='#f3eee2', rust=True, garch=True, hood='pediment', pil=False,
                           extra=[corner_tower(-172.4, 404.9, 2.1, 9.2, 13.4, M('#e4dcc6'), M('#f3eee2'), M('#3a3f45', 0.5, 0.3))])   # Heinen talo / seurakuntatoimisto: banded rustication on the ground floor, arched ground-floor windows, pedimented upper windows (Street View 14.11.2026)
SPECK[1513] = classic_spec(1513, wall='#9b4b36', trim='#b9654c', rust=False, garch=True, hood=None, pil=True, bw=4.6, cornice=(0.3, 0.7, M('#7f3d2c')))   # brewery remnant
SPECK[1281] = classic_spec(1281, wall='#e2dcbc', trim='#f4f1e8', rust=False, garch=False, hood='cornice', pil=True)   # Eteläranta 10: pale yellow render, white pilasters, window surrounds and cornice (Street View 14.11.2026)
SPECK[1285] = classic_spec(1285, trim='#f4f1e8', rust=False, garch=True, hood='cornice', pil=True)   # Eteläranta: pale yellow, arched ground-floor windows, white surrounds (Street View 14.11.2026)
SPECK[1563] = classic_spec(1563, trim='#f4f1e8', rust=False, garch=False, hood='cornice', pil=False)   # Antinkatu 3 corner: white 2-storey, window cornices (Street View 14.11.2026); the Hallituskatu end looks yellow - two houses in one LoD2 shell?
SPECK[1447] = classic_spec(1447, wall='#9c4f3c', trim='#e6dccb', rust=False, garch=True, hood=None, pil=True, bw=3.8, first=dict(arch=True), top=dict(arch=True))   # old red-brick building at Eteläranta/Karhu: round-arched windows with light surrounds, brick pilasters (was a plain modern box; Street View 14.11.2026)
SPECK[1575] = classic_spec(1575, trim='#f4f1e8', rust=False, garch=True, hood='cornice', pil=True)   # Antinkatu/Hallituskatu corner: yellow, big round-arched shop windows, white corner quoins (Street View 14.11.2026)
SPECK[1572] = classic_spec(1572, trim='#f4f1e8', rust=False, garch=False, hood='cornice', pil=True)   # Antinkatu 2-4: ochre, white quoins and window surrounds, frieze under the eaves (Street View 14.11.2026)
SPECK[1561] = classic_spec(1561, trim='#f6f4ee', rust=False, garch=False, hood=None, pil=False)   # Antinkatu: small white gabled 1-storey house, plain windows (Street View 14.11.2026)
SPECK[1562] = classic_spec(1562, trim='#f6f4ee', rust=False, garch=False, hood='cornice', pil=False)   # Antinkatu: white 2-storey (Street View 14.11.2026)
SPECK[1573] = classic_spec(1573, trim='#f4f1e8', rust=False, garch=False, hood=None, pil=False)   # Antinkatu: low 1-storey yellow house, no arched windows; the arched gateway with columns is not modelled (Street View 14.11.2026, owner)
SPECK[1566] = classic_spec(1566, trim='#f4f1e8', rust=False, garch=False, hood='cornice', pil=False)   # Eteläranta 4 / Antinkatu 2 (1854): 2 storeys, rectangular windows with cornices, no arches (Street View 14.11.2026)
SPECK[1454] = classic_spec(1454, trim='#f7f6f1', rust=False, garch=False, hood='pediment', pil=False, ground=dict(hood='pediment'))   # Teatterikatu: white 1-storey, triangular pediments over the windows (Street View 14.11.2026)
SPECK[1292] = classic_spec(1292, trim='#f5f2ea', rust=False, garch=False, hood='cornice', pil=True)   # Selim Palmgreninkatu / Valtakatu corner: yellow 1-storey, white window surrounds with cornices, white corner pilasters (Street View 14.11.2026)

# Karhukortteli: five apartment buildings (2016-2020) where the Porin Oluttehdas stood. The LoD2 shells and the aerial image still show
# the brewery, so these are built from the OSM footprints and heights: business premises at street level, large windows,
# balconies, dark pitched metal roofs. Wall colours are estimates.
KARHU = {1450: ('#7a4535', 'brick'), 1451: ('#d9d6cf', 'render'), 1511: ('#e8e6e0', 'render'), 1512: ('#8a5a44', 'brick'), 1515: ('#cfc6b6', 'render')}   # as approved by the owner: brown-red brick and light render, dark roofs (do not re-colour from the old oblique photos, the block was built 2016-2020)
for i, (wc, kind) in KARHU.items():
    W_ = MT(wc, 'brick', 0.8) if kind == 'brick' else M(wc); rise = 3.2
    SPECK[i] = dict(h=B[i]['h'] - rise, P=dict(wall=W_, sign=SIGNS, gwall=M('#3b3f44', 0.4), fascia=M('#2d3135'), frame=M('#2f3337', 0.5), rail=M('#c9ced2', 0.3, 0.5), slab=M('#e9e9e6')),
                    layout=lay(B[i]['h'] - rise, 'punched', gh=4.4, bw=3.6, fh=3.05, cols=lambda c, nb: 'B' if c % 3 == 1 else 'W', P=dict(ww=2.1, wh=1.9, sill=0.55, nx=2)),
                    roof=dict(kind='hip', rise=rise, inset=4.2, mat=M('#34393d', 0.5, 0.3), ov=0.35), footprint=True)   # hip ring on the footprint: an OBB gable overhung the L-shaped plans

def kspec(i):
    if i in SPECK: return SPECK[i]
    if i in MODERN: return spec_for(i)
    return classic_spec(i)

# One MML LoD2 building can hold several OSM buildings (1579 Hallituskatu 6 holds the Valtakatu 7 tower 1581, 1603, 1583 and 1716).
# Built both ways, the footprint walls stood 0.1-0.8 m in front of the shell walls and the bake hit the other surface: black facades
# (the black Valtakatu tower, Street View check 13.11.2026). Now such a footprint building is not built on its own: the shell's walls
# in front of it get its spec (colour, storeys, layout) as a run of their own.
def _fp(i):
    p = B[i]['p']; return Polygon([(p[k] / 10, p[k + 1] / 10) for k in range(0, len(p), 2)]).buffer(0)
def shell_parts(ids, spec):
    from shapely.ops import unary_union
    shells = {}
    for i in ids:
        if RAW.get(i) and not spec(i).get('footprint'):
            G = [Polygon([(p[0], p[1]) for p in r]).buffer(0) for k, r, _ in RAW[i] if k == 'G' and len(r) >= 3]
            if G: shells[i] = unary_union(G)
    out = {}
    # also the OSM buildings the game hides under these shells (lod2.js 'hide'): Sampotalo 238 under Teljäntori 216 was drawn
    # with Teljäntori's spec (a six-storey white wall on Yrjönkatu instead of the two-storey shop building)
    extra = []
    if shells:
        from shapely.ops import unary_union as _uu
        allsh = _uu(list(shells.values())).buffer(1.0); bx = allsh.bounds
        for j in zones2.HIDE:
            if j in ids or j >= len(B): continue
            lk = LOOK['b'].get(str(j)) or {}
            if lk.get('m') or not lk.get('w'): continue          # only hidden buildings whose look is known (street photos, sources)
            p = B[j]['p']; xs = p[0::2]; ys = p[1::2]
            if min(xs) / 10 > bx[2] or max(xs) / 10 < bx[0] or min(ys) / 10 > bx[3] or max(ys) / 10 < bx[1]: continue
            extra.append(j)
    for j in list(ids) + extra:
        if j in shells: continue
        f = _fp(j)
        if f.area < 1: continue
        for i, g in shells.items():
            if g.intersection(f).area > 0.6 * f.area: out[j] = i; break
    return out
def shell_runalt(sp, subs, spec):
    from shapely.geometry import Point as _Pt
    zone = [(spec(j), _fp(j).buffer(1.2)) for j in sorted(subs, key=lambda j: _fp(j).area)]   # smallest first: a low wing in front of a tower;
    base = sp.get('runalt')                                                                      # one spec object per part (splitruns compares by id)
    def ra(x, y):
        r = base(x, y) if base else None                   # a hand-made runalt (Eteläpuisto 9 in 11's shell) wins
        if r: return r
        for sj, g in zone:
            if g.contains(_Pt(x, y)): return sj
        return None
    return dict(sp, runalt=ra, splitruns=True)

def build_and_bake(name, ids, samples=16, spec=None):
    spec = spec or kspec
    if os.environ.get('PORI_PHS') and os.path.exists(os.environ['PORI_PHS']):
        ex = {int(k) for k in json.load(open(os.environ['PORI_PHS']))}; ids = [i for i in ids if i not in ex]
    t = time.time()
    for i in ids:
        if RAW.get(i) and not spec(i).get('footprint'): B[i]['h'] = eave_of(i)
    zones2.ROOFBAKE = name in ZONESK and name != 'karhu'
    Z = Zone(name, ids); Z.roofflag = any(spec(i).get('roof') for i in ids)
    inside = shell_parts(ids, spec)
    for i in ids:
        if i in inside: continue                         # drawn as a stretch of the LoD2 shell it stands in (see shell_parts)
        sp = spec(i)
        if RAW.get(i) and not sp.get('footprint'):
            subs = [j for j, o in inside.items() if o == i]
            if subs: sp = shell_runalt(sp, subs, spec)
            build_lod2(Z, i, sp)
            for ex in sp.get('extra', []): ex(Z, None, B[i]['h'], None)          # hand-built parts the LoD2 scan lacks (corner towers)
        else:
            sp2 = dict(sp); sp2['layout'] = sp['fit'](sp['layout'], B[i]['h'], True) if 'fit' in sp else sp['layout']
            if zones2.ROOFBAKE and not sp2.get('roof'): sp2['roof'] = dict(kind='flat', mat=roof_mat(i))   # no LoD2 shell: the game shows no roof here, the block must
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
