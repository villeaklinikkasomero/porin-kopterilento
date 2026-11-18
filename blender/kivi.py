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
    'kivi3': [1581, 1716, 1586, 1604, 1578, 1603, 1579, 1585, 1583, 1580],                                   # Hallituskatu - Valtakatu, east
    'kivi4': [1572, 1573, 1607, 1566, 1567, 8385],                                               # river block at Yrjönkatu
    'kivi5': [1553, 1620, 1550, 1619, 1552, 1551, 1548, 1549],                                   # Signelinna block
    'p1': [125, 126, 127, 129, 169, 272, 273, 133, 135, 275, 276, 277, 290, 291],                # Antinkatu 21-25 / Mikonkatu (bl_p1.js of 11.11. had no generator left in the repo; 13.11.2026)
    'karhu': [1450, 1451, 1511, 1512, 1515],                                                 # Karhukortteli (2016-2020) on the old brewery site
    'kl0': [1261, 1336, 1337, 1338, 1351, 1357, 1368, 1369, 1370, 1446, 1447, 1448, 1449, 1458, 1461, 1462, 1516, 1517, 1525, 1535],                                                                       # west of Kivi-Pori (modern blocks)
    'kl1': [1297, 1309, 1310, 1352, 1353, 1373, 1374, 1375, 1377, 1398, 1407, 1527, 1528],
}
MODERN = set(ZONESK['kl0'] + ZONESK['kl1']) | (set(ZONESK['p1']) - {276, 133}) | {1581, 1603, 1579, 1620, 1548, 1716, 1580, 1586, 1585, 1550, 1552, 1549, 1553}   # 1573 (low yellow house on Antinkatu) and 1604 (yellow Jugend, Street View 13.11.2026) is classic

# ---------------------------------------------------------------- streets: a wall faces a street when a named street runs in front of it
_src = open('/home/claude/pori/city.js').read(); _C = json.loads(_src[_src.index('{'):_src.rindex('}') + 1])
ROADS = [LineString([(r['p'][k], r['p'][k + 1]) for k in range(0, len(r['p']), 2)]) for r in _C['r'] if r.get('n') and len(r['p']) >= 4]
def street(mid, n):
    pt = Point(mid[0] + n[0] * 6, mid[1] + n[1] * 6)
    return min(l.distance(pt) for l in ROADS) < 13
zones2.STREET = street

# ---------------------------------------------------------------- facade recipes
KIVIP = ['#e6d3a3', '#d9b98c', '#e8c9b0', '#cfd3c0', '#d8a48f', '#e9e1cc', '#c9a27a', '#e2c27d', '#c3c6bd', '#d9b2a6', '#ead8b8', '#cdbb98']
GRANITE = M('#7a7771', 0.8)   # grey granite as on the Street View plinths (was #5b5752: read as near black)
def h01(i, k): x = (i * 2654435761 + k * 40503) & 0xffffffff; x ^= x >> 15; x = (x * 2246822519) & 0xffffffff; x ^= x >> 13; return (x & 0xffffff) / 0xffffff

def klay(bw=3.5, ground=None, first=None, top=None, door_mid=True, gh=4.4, fh=3.9, pair=False, frieze=0, cols=None, nf=None, attic=None):
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
        if frieze and nf > 1: rows = rows[:nf] + [(frieze, 'classic', 'Z')]   # attic frieze: its own row key (rowP 'Z' = attic, else top)
        if nf0 == 1: nf = 1                              # styles.json f=1 (street photos): one storey even when the LoD2 wall is tall (high roof base, raised plinth)
        if nf == 1: rows = [(h - frieze, 'classic', 'G'), (frieze, 'classic', 'Z')] if frieze else [(h, 'classic', 'G')]   # one storey with a low frieze of small attic windows (4 Antinkatu)
        cols_ = cols or (lambda c, nb: 'D' if door_mid and nb >= 5 and c == nb // 2 else ('P' if pair else 'W'))
        return dict(bw=bw, rows=rows, cols=cols_, P={}, rowP={'G': dict(ground=True, **(ground or {})), 'F': first or {}, 'T': top or first or {}, 'Z': attic or top or first or {}}, plain=False)
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
    attic = kw.pop('attic', None); attic = dict(top, **attic) if attic is not None else None
    lay = kw.pop('lay', {}); nst = lay.get('nf'); L = klay(bw=bw, ground=ground, first=first, top=top, attic=attic, **lay)
    yard = dict(bw=3.2, rows=[(1, 'classic', 'Y')], cols=lambda c, nb: 'W', P={}, rowP={'Y': dict(surround=0.1, ww=1.0, wh=1.6, sill=0.9)}, plain=False)
    same = kw.pop('yard_same', False)
    def fit(lay_, hh, st):
        if not st and not same:
            nf = max(1, round(hh / 3.6))
            if nst and nf > nst and os.environ.get('KDBG'): print('CAP', i, round(hh, 1), nf, '->', nst)
            if nst: nf = min(nf, nst)                       # owner 15.11.2026: the yard side cannot have more storeys than the street front
            return dict(sp['yard'], rows=[(hh / nf if nst and nf == nst else 3.6, 'classic', 'Y')] * nf)   # sp['yard']: a spec may replace its yard layout (blank gable 1288)
        return L(hh)
    sp = dict(P=dict(wall=W, trim=T, frame=M('#f4f2ea')), layout=L(h or 10), yard=yard, fit=fit, cornice=(0.42, 0.75, T))
    sp.update(kw)
    return sp

def cut_walls(i, p0, d):
    """Split the LoD2 walls of building i with the vertical plane through p0 (x, y) whose normal is d (dx, dy), so that one shell can
    carry two houses (colour, storeys) along one street front: build_lod2 then picks the spec per piece through spec['alt']."""
    out = []
    for k, r, holes in RAW.get(i, []):
        sd = [(q[0] - p0[0]) * d[0] + (q[1] - p0[1]) * d[1] for q in r]
        if k != 'W' or min(sd) >= -0.05 or max(sd) <= 0.05: out.append((k, r, holes)); continue
        for sg in (1, -1):                                         # Sutherland-Hodgman against each half-space
            poly = []
            for a in range(len(r)):
                P, Q = r[a], r[(a + 1) % len(r)]; sp, sq = sd[a] * sg, sd[(a + 1) % len(r)] * sg
                if sp >= 0: poly.append(P)
                if (sp >= 0) != (sq >= 0):
                    t = sp / (sp - sq); poly.append(tuple(P[c] + (Q[c] - P[c]) * t for c in range(3)))
            if len(poly) >= 3: out.append((k, poly, holes))
    RAW[i] = out

def lower_eave(i, test, z_eave, depth):
    """Pull the street wall of a low house down to its real eave and give it a steep roof slope back up to the LoD2 wall top
    (the scan drew 2 Antinkatu's front as a 6.9 m wall; the house is one storey under a high roof)."""
    out = []
    for k, r, holes in RAW.get(i, []):
        if k == 'W' and test(r):
            ztop = max(q[2] for q in r); r2 = [(q[0], q[1], min(q[2], z_eave)) for q in r]; out.append((k, r2, holes))
            lo = [q for q in r if q[2] < 0.5]
            if len(lo) >= 2 and ztop > z_eave + 0.3:
                (ax, ay, _), (bx, by, _) = lo[0], lo[1]; L = math.hypot(bx - ax, by - ay); nx, ny = -(by - ay) / L, (bx - ax) / L
                _p = B[i]['p']; cxm, cym = sum(_p[0::2]) / len(_p[0::2]) / 10, sum(_p[1::2]) / len(_p[1::2]) / 10
                if (cxm - ax) * nx + (cym - ay) * ny < 0: nx, ny = -nx, -ny          # into the house
                out.append(('R', [(ax, ay, z_eave), (bx, by, z_eave), (bx + nx * depth, by + ny * depth, ztop), (ax + nx * depth, ay + ny * depth, ztop)], None))
        else: out.append((k, r, holes))
    # the scanned roof still started at the old wall top on the street line: it hung over the new slope as a loose plane
    # (2 Antinkatu, owner 14.11.2026). Its vertices on that line move back to the top of the slope.
    segs = [(q[0], q[1], q[2], q[3]) for k, q, _ in out if k == 'R' and len(q) == 4 and abs(q[0][2] - z_eave) < 1e-6 and abs(q[1][2] - z_eave) < 1e-6]
    def mv(p):
        for a, b, c, d in segs:
            ax, ay, bx, by = a[0], a[1], b[0], b[1]; L = math.hypot(bx - ax, by - ay); t = ((p[0] - ax) * (bx - ax) + (p[1] - ay) * (by - ay)) / L ** 2
            dist = abs((p[0] - ax) * (by - ay) - (p[1] - ay) * (bx - ax)) / L
            if 0.01 <= t <= 0.99 and dist < 0.4 and p[2] > z_eave + 0.3:   # strictly inside the piece: a corner shared with the next house stays
                return (ax + (bx - ax) * t + (d[0] - a[0]), ay + (by - ay) * t + (d[1] - a[1]), p[2])
        return p
    RAW[i] = [(k, [mv(p) for p in r] if k == 'R' and not (len(r) == 4 and abs(r[0][2] - z_eave) < 1e-6) else r, h) for k, r, h in out]

def squash(i, z0, k):
    """everything of building i above z0 is pressed down to k of its height above z0 (a scan whose walls and roof stand far too high)"""
    RAW[i] = [(kk, [(q[0], q[1], q[2] if q[2] <= z0 else z0 + (q[2] - z0) * k) for q in r], h) for kk, r, h in RAW.get(i, [])]

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

WALL_SHELLS = []   # free-standing walls / gates of facade_bits: their own 'houses' in the bl_*.js shells
def facade_bits(p0, p1, items):
    """hand-placed features on one street wall p0->p1 (plan x, y); n is the outward normal on the right of p0->p1 looking down.
    items: ('gable', s, w, z, h, mat) stepped brick gable over the eave; ('oriel', s, w, z0, z1, d, mat) a bay window"""
    L0 = math.hypot(p1[0] - p0[0], p1[1] - p0[1]); t = ((p1[0] - p0[0]) / L0, (p1[1] - p0[1]) / L0); n = (t[1], -t[0])
    def ex(Z, *a):
        P = lambda s_, z, d=0.0: (p0[0] + t[0] * s_ + n[0] * d - Z.cx, p0[1] + t[1] * s_ + n[1] * d - Z.cy, z)
        def quad(pts, mat, two=False):
            add_solid(Z, pts, mat, 0.5)
            if two: add_solid(Z, pts[::-1], mat, 0.3)
        for it in items:
            if it[0] == 'gable':
                _, s0, w, z, h, mat = it[:6]; st = it[6] if len(it) > 6 else 4; hw = w / 2
                prof = []
                for k in range(st + 1):                                      # stepped outline, left half then mirrored
                    u = k / st; prof.append((s0 - hw + hw * u, z + h * u))
                pts = []
                for k, (u, zz) in enumerate(prof):
                    if k: pts.append((u, prof[k - 1][1]))
                    pts.append((u, zz))
                right = [(2 * s0 - u, zz) for u, zz in reversed(pts)]
                poly = [(s0 - hw, z)] + pts + right[1:] + [(s0 + hw, z)]
                if st == 1: poly = [(s0 - hw, z), (s0, z + h), (s0 + hw, z)]          # a plain triangle
                for d in (0.12, -0.25):
                    q = [P(u, zz, d) for u, zz in poly]
                    add_solid(Z, q[::-1] if d > 0 else q, mat, 0.5)
                for (u0, z0_), (u1, z1_) in zip(poly, poly[1:] + poly[:1]):  # coping on the outline
                    if z0_ > z + 0.01 or z1_ > z + 0.01:
                        add_solid(Z, [P(u0, z0_, 0.12), P(u1, z1_, 0.12), P(u1, z1_, -0.25), P(u0, z0_, -0.25)], mat, 0.3)
            elif it[0] == 'band':                                           # a cornice band projecting d between sa and sb
                _, sa, sb, z0, z1, d, mat = it
                quad([P(sa, z0, d), P(sb, z0, d), P(sb, z1, d), P(sa, z1, d)], mat)
                quad([P(sa, z0, 0), P(sb, z0, 0), P(sb, z0, d), P(sa, z0, d)], mat)
                quad([P(sa, z1, d), P(sb, z1, d), P(sb, z1, 0), P(sa, z1, 0)], mat)
                quad([P(sa, z0, 0), P(sa, z0, d), P(sa, z1, d), P(sa, z1, 0)], mat)
                quad([P(sb, z0, d), P(sb, z0, 0), P(sb, z1, 0), P(sb, z1, d)], mat)
            elif it[0] == 'brackets':                                       # white consoles under the eave
                _, sa, sb, z, mat = it; k_ = int((sb - sa) / 0.95)
                for k in range(k_ + 1):
                    u = sa + (sb - sa) * k / max(1, k_)
                    quad([P(u - 0.09, z - 0.75, 0.22), P(u + 0.09, z - 0.75, 0.22), P(u + 0.09, z, 0.45), P(u - 0.09, z, 0.45)], mat)
                    quad([P(u - 0.09, z - 0.75, 0.0), P(u - 0.09, z - 0.75, 0.22), P(u - 0.09, z, 0.45), P(u - 0.09, z, 0.0)], mat)
                    quad([P(u + 0.09, z - 0.75, 0.22), P(u + 0.09, z - 0.75, 0.0), P(u + 0.09, z, 0.0), P(u + 0.09, z, 0.45)], mat)
            elif it[0] == 'wall':                                           # ('wall', s0, s1, z0, z1, t, mat): free-standing garden wall, in 3 m pieces (the game lifts each piece to its ground)
                _, s0, s1, z0, z1, tk, mat = it; nseg = max(1, int((s1 - s0) / 3.0))
                WALL_SHELLS.append((z1 + 0.3, [(p0[0] + t[0] * u_ - n[0] * d_, p0[1] + t[1] * u_ - n[1] * d_) for u_, d_ in ((s0 + 0.2, -0.05), (s1 - 0.2, -0.05), (s1 - 0.2, tk - 0.08), (s0 + 0.2, tk - 0.08))]))   # the game lifts this wall as one piece (a free piece was sheared per triangle on the slope)
                for k in range(nseg):
                    u0 = s0 + (s1 - s0) * k / nseg; u1 = s0 + (s1 - s0) * (k + 1) / nseg
                    quad([P(u0, z0, 0.0), P(u1, z0, 0.0), P(u1, z1, 0.0), P(u0, z1, 0.0)], mat)
                    quad([P(u1, z0, -tk), P(u0, z0, -tk), P(u0, z1, -tk), P(u1, z1, -tk)], mat)
                    quad([P(u0, z1, 0.0), P(u1, z1, 0.0), P(u1, z1, -tk), P(u0, z1, -tk)], mat)
                for u, sg in ((s0, -1), (s1, 1)):
                    quad([P(u, z0, -tk if sg > 0 else 0.0), P(u, z0, 0.0 if sg > 0 else -tk), P(u, z1, 0.0 if sg > 0 else -tk), P(u, z1, -tk if sg > 0 else 0.0)], mat)
            elif it[0] == 'cyl':                                            # ('cyl', s, d, r, z0, z1, mat): upright cylinder (silo) standing out from the wall
                _, sc, dc, r, z0, z1, mat = it[:7]; nseg = 24
                ang = [2 * math.pi * q / nseg for q in range(nseg + 1)]
                for q in range(nseg):
                    a0, a1 = ang[q], ang[q + 1]
                    quad([P(sc + r * math.cos(a1), z0, dc + r * math.sin(a1)), P(sc + r * math.cos(a0), z0, dc + r * math.sin(a0)),
                          P(sc + r * math.cos(a0), z1, dc + r * math.sin(a0)), P(sc + r * math.cos(a1), z1, dc + r * math.sin(a1))], mat)
                quad([P(sc + r * math.cos(a), z1, dc + r * math.sin(a)) for a in reversed(ang[:-1])], mat)
            elif it[0] == 'archwin':                                        # ('archwin', s0, s1, z0, zs, surround): round-headed window, glass + mullion/transom, stone surround
                _, s0, s1, z0, zs, sm = it[:6]; r = (s1 - s0) / 2; c = (s0 + s1) / 2; gw = M('#71838f', 0.05, 0.4); fr = M('#3a3530', 0.5); sw = 0.16
                arcp = [P(c + r * math.cos(math.pi * q / 12), zs + r * math.sin(math.pi * q / 12), 0.06) for q in range(13)]
                quad([P(s0, z0, 0.06), P(s1, z0, 0.06)] + arcp, gw)
                ob = [P(c + (r + sw) * math.cos(math.pi * q / 12), zs + (r + sw) * math.sin(math.pi * q / 12), 0.09) for q in range(13)]
                ib = [P(c + r * math.cos(math.pi * q / 12), zs + r * math.sin(math.pi * q / 12), 0.09) for q in range(13)]
                for q in range(12): quad([ib[q], ob[q], ob[q + 1], ib[q + 1]][::-1], sm)
                quad([P(s0 - sw, z0, 0.09), P(s0, z0, 0.09), P(s0, zs, 0.09), P(s0 - sw, zs, 0.09)], sm)
                quad([P(s1, z0, 0.09), P(s1 + sw, z0, 0.09), P(s1 + sw, zs, 0.09), P(s1, zs, 0.09)], sm)
                quad([P(s0 - sw - 0.05, z0 - 0.15, 0.16), P(s1 + sw + 0.05, z0 - 0.15, 0.16), P(s1 + sw + 0.05, z0, 0.16), P(s0 - sw - 0.05, z0, 0.16)], sm)
                quad([P(c - 0.04, z0, 0.09), P(c + 0.04, z0, 0.09), P(c + 0.04, zs + r, 0.09), P(c - 0.04, zs + r, 0.09)], fr)
                quad([P(s0, zs - 0.04, 0.09), P(s1, zs - 0.04, 0.09), P(s1, zs + 0.04, 0.09), P(s0, zs + 0.04, 0.09)], fr)
            elif it[0] == 'archgate':                                       # ('archgate', s, w, zs, mat_gate): round-arched gateway in a wall: dark arch, light board gate below the springing
                _, s0, w, zs, gm = it; r = w / 2; dk = M('#3b3a36', 0.6)
                arcp = [P(s0 + r * math.cos(math.pi * k / 10), zs + r * math.sin(math.pi * k / 10), 0.03) for k in range(11)]
                quad([P(s0 - r, 0.0, 0.03), P(s0 + r, 0.0, 0.03)] + arcp, dk)
                quad([P(s0 - r + 0.08, 0.0, 0.06), P(s0 + r - 0.08, 0.0, 0.06), P(s0 + r - 0.08, zs, 0.06), P(s0 - r + 0.08, zs, 0.06)], gm)
                ob = [P(s0 + (r + 0.35) * math.cos(math.pi * k / 10), zs + (r + 0.35) * math.sin(math.pi * k / 10), 0.05) for k in range(11)]
                for k in range(10): quad([arcp[k], ob[k], ob[k + 1], arcp[k + 1]][::-1], M('#f3f0e8'))
            elif it[0] == 'irongate':                                       # ('irongate', s, w, zs): open round arch with a wrought-iron gate: the yard shows through the bars
                _, s0, w, zs = it; r = w / 2; yd = M('#7c7f78', 0.9); ir = M('#1f2123', 0.4)
                arcp = [P(s0 + r * math.cos(math.pi * k / 12), zs + r * math.sin(math.pi * k / 12), 0.02) for k in range(13)]
                quad([P(s0 - r, 0.0, 0.02), P(s0 + r, 0.0, 0.02)] + arcp, yd)
                u = s0 - r + 0.07
                while u < s0 + r - 0.05:
                    top = zs + math.sqrt(max(0.0, r * r - (u - s0) ** 2)) - 0.05
                    quad([P(u - 0.025, 0.0, 0.08), P(u + 0.025, 0.0, 0.08), P(u + 0.025, top, 0.08), P(u - 0.025, top, 0.08)], ir)
                    u += 0.16
                for zz in (0.15, 1.1, zs):
                    quad([P(s0 - r, zz, 0.09), P(s0 + r, zz, 0.09), P(s0 + r, zz + 0.07, 0.09), P(s0 - r, zz + 0.07, 0.09)], ir)
                ob = [P(s0 + (r + 0.3) * math.cos(math.pi * k / 12), zs + (r + 0.3) * math.sin(math.pi * k / 12), 0.1) for k in range(13)]
                for k in range(12): quad([arcp[k], ob[k], ob[k + 1], arcp[k + 1]][::-1], M('#f6f4ee'))
            elif it[0] == 'spire':                                          # ('spire', s, w, z0, z1, mat): slender pyramid roof of a Jugend turret, its base square flush with the wall face
                _, s0, w, z0, z1, mat = it; hw = w / 2
                c = [(s0 - hw, 0.15), (s0 + hw, 0.15), (s0 + hw, -w + 0.15), (s0 - hw, -w + 0.15)]; ap = P(s0, z1, 0.15 - hw)
                for k in range(4):
                    (u0, d0), (u1, d1) = c[k], c[(k + 1) % 4]
                    quad([P(u0, z0, d0), P(u1, z0, d1), ap], mat, True)
            elif it[0] == 'box':                                            # ('box', sa, sb, z0, z1, d0, d1, mat): plain box in front of the wall (balcony slabs and parapets)
                _, sa, sb, z0, z1, d0, d1, mat = it
                quad([P(sa, z0, d1), P(sb, z0, d1), P(sb, z1, d1), P(sa, z1, d1)], mat)
                quad([P(sb, z0, d0), P(sa, z0, d0), P(sa, z1, d0), P(sb, z1, d0)], mat)
                quad([P(sa, z1, d1), P(sb, z1, d1), P(sb, z1, d0), P(sa, z1, d0)], mat)
                quad([P(sa, z0, d0), P(sb, z0, d0), P(sb, z0, d1), P(sa, z0, d1)], mat)
                quad([P(sa, z0, d0), P(sa, z0, d1), P(sa, z1, d1), P(sa, z1, d0)], mat)
                quad([P(sb, z0, d1), P(sb, z0, d0), P(sb, z1, d0), P(sb, z1, d1)], mat)
            elif it[0] == 'canopy':                                         # ('canopy', s, w, z, depth, mat): door canopy, a thin slab sloping out from the wall
                _, s0, w, z, dp, mat = it; hw = w / 2
                quad([P(s0 - hw, z, 0.0), P(s0 + hw, z, 0.0), P(s0 + hw, z - 0.25, dp), P(s0 - hw, z - 0.25, dp)][::-1], mat, True)
                quad([P(s0 - hw, z - 0.25, dp), P(s0 + hw, z - 0.25, dp), P(s0 + hw, z - 0.4, dp), P(s0 - hw, z - 0.4, dp)], mat, True)
            elif it[0] == 'chimney':                                        # ('chimney', s, d, z0, z1, w, mat): square stack d m behind the wall
                _, s0, dd, z0, z1, w, mat = it; hw = w / 2; c = [(s0 - hw, -dd - hw), (s0 + hw, -dd - hw), (s0 + hw, -dd + hw), (s0 - hw, -dd + hw)]
                for k in range(4):
                    (u0, d0), (u1, d1) = c[k], c[(k + 1) % 4]
                    quad([P(u0, z0, d0), P(u1, z0, d1), P(u1, z1, d1), P(u0, z1, d0)], mat, True)
                quad([P(u, z1, d) for u, d in c], mat, True)
            elif it[0] == 'vents':                                          # a row of small attic openings
                _, s0, n_, z, mat = it[:5]; dk = M('#2a2f33', 0.4); vw = it[5] if len(it) > 5 else 0.3; vh = it[6] if len(it) > 6 else 0.3   # optional size (attic windows)
                for k in range(n_):
                    u = s0 + (k - (n_ - 1) / 2) * (vw + 0.25)
                    if len(it) > 5: quad([P(u - vw / 2 - 0.08, z - 0.08, 0.12), P(u + vw / 2 + 0.08, z - 0.08, 0.12), P(u + vw / 2 + 0.08, z + vh + 0.08, 0.12), P(u - vw / 2 - 0.08, z + vh + 0.08, 0.12)], M('#f4f1e8'))
                    quad([P(u - vw / 2, z, 0.14), P(u + vw / 2, z, 0.14), P(u + vw / 2, z + vh, 0.14), P(u - vw / 2, z + vh, 0.14)], dk)
            elif it[0] == 'orielv':                                         # oriel with a triangular plan: two sides meeting at a point, windows in both
                _, s0, w, z0, z1, d, mat = it; gl = M('#47525c', 0.15); a_, b_ = s0 - w / 2, s0 + w / 2
                fr = M('#2e3a33', 0.5)
                for (u0, d0), (u1, d1) in (((a_, 0.0), (s0, d)), ((s0, d), (b_, 0.0))):
                    quad([P(u0, z0, d0), P(u1, z0, d1), P(u1, z1, d1), P(u0, z1, d0)], mat)
                    du, dd = u1 - u0, d1 - d0; Lq = math.hypot(du, dd); eu, ed = du / Lq, dd / Lq; nu, nd = -ed, eu
                    um, dm = (u0 + u1) / 2, (d0 + d1) / 2; hw_ = Lq * 0.34
                    pts = lambda off, e: [P(um - eu * (hw_ + e) + nu * off, z0 + 0.4 - e, dm - ed * (hw_ + e) + nd * off), P(um + eu * (hw_ + e) + nu * off, z0 + 0.55 - e, dm + ed * (hw_ + e) + nd * off),
                                          P(um + eu * (hw_ + e) + nu * off, z1 - 0.3 + e, dm + ed * (hw_ + e) + nd * off), P(um - eu * (hw_ + e) + nu * off, z1 - 0.3 + e, dm - ed * (hw_ + e) + nd * off)]
                    quad(pts(0.02, 0.08), fr); quad(pts(0.03, 0.0), M('#6f8598', 0.1))   # dark green frame, light glass
                zr = z1 + 0.9                                                     # roof: from the point back up into the wall
                add_solid(Z, [P(a_, z1, 0), P(s0, z1, d), P(s0, zr, 0)][::-1], mat, 0.4)
                add_solid(Z, [P(s0, z1, d), P(b_, z1, 0), P(s0, zr, 0)][::-1], mat, 0.4)
                tip = P(s0, z0 - 1.8, 0.05)
                for (u0, d0), (u1, d1) in (((a_, 0.0), (s0, d)), ((s0, d), (b_, 0.0))):              # pointed corbel
                    add_solid(Z, [P(u0, z0, d0), tip, P(u1, z0, d1)], mat, 0.4)
            elif it[0] == 'oriel3':                                         # three-sided bay window on a tapering corbel (Jugend)
                _, s0, w, z0, z1, d, mat = it; gl = M('#47525c', 0.15); a_, b_ = s0 - w / 2, s0 + w / 2; f_ = w * 0.22
                A0, A1, B1, B0 = (a_, 0.0), (a_ + f_, d), (b_ - f_, d), (b_, 0.0)
                for (u0, d0), (u1, d1) in ((A0, A1), (A1, B1), (B1, B0)):
                    quad([P(u0, z0, d0), P(u1, z0, d1), P(u1, z1, d1), P(u0, z1, d0)], mat)
                    um, dm = (u0 + u1) / 2, (d0 + d1) / 2; hw_ = 0.3 if (u1 - u0) > 1.0 else 0.18
                    du, dd = (u1 - u0), (d1 - d0); Lq = math.hypot(du, dd); eu, ed = du / Lq, dd / Lq
                    quad([P(um - eu * hw_, z0 + 0.5, dm - ed * hw_ + 0.03), P(um + eu * hw_, z0 + 0.5, dm + ed * hw_ + 0.03), P(um + eu * hw_, z1 - 0.5, dm + ed * hw_ + 0.03), P(um - eu * hw_, z1 - 0.5, dm - ed * hw_ + 0.03)], gl)
                quad([P(a_, z1, 0), P(b_, z1, 0), P(b_ - f_, z1, d), P(a_ + f_, z1, d)][::-1], mat)   # roof
                tip = P(s0, z0 - 1.8, 0.05)
                for (u0, d0), (u1, d1) in ((A0, A1), (A1, B1), (B1, B0)):                         # pointed corbel
                    add_solid(Z, [P(u0, z0, d0), tip, P(u1, z0, d1)], mat, 0.4)
            elif it[0] == 'oriel':
                _, s0, w, z0, z1, d, mat = it; a_, b_ = s0 - w / 2, s0 + w / 2; gl = M('#47525c', 0.15)
                quad([P(a_, z0, d), P(b_, z0, d), P(b_, z1, d), P(a_, z1, d)], mat)                       # front
                quad([P(a_, z0, 0), P(a_, z0, d), P(a_, z1, d), P(a_, z1, 0)], mat)                       # sides
                quad([P(b_, z0, d), P(b_, z0, 0), P(b_, z1, 0), P(b_, z1, d)], mat)
                quad([P(a_, z1, d), P(b_, z1, d), P(b_, z1, 0), P(a_, z1, 0)], mat)                       # roof
                quad([P(a_, z0, 0), P(b_, z0, 0), P(s0 + 0.3, z0 - 1.2, 0), P(s0 - 0.3, z0 - 1.2, 0)], mat)   # corbel
                quad([P(a_, z0, 0), P(s0 - 0.3, z0 - 1.2, 0), P(s0 - 0.3, z0 - 1.2, 0.15), P(a_, z0, d)][::-1], mat)
                quad([P(b_, z0, d), P(s0 + 0.3, z0 - 1.2, 0.15), P(s0 + 0.3, z0 - 1.2, 0), P(b_, z0, 0)][::-1], mat)
                quad([P(a_, z0, d), P(s0 - 0.3, z0 - 1.2, 0.15), P(s0 + 0.3, z0 - 1.2, 0.15), P(b_, z0, d)][::-1], mat)
                ww = (w - 0.6) / 2
                for k in range(2):                                                                     # two windows in front, one each side
                    u0 = a_ + 0.2 + k * (ww + 0.2)
                    quad([P(u0, z0 + 0.6, d + 0.02), P(u0 + ww, z0 + 0.6, d + 0.02), P(u0 + ww, z1 - 0.4, d + 0.02), P(u0, z1 - 0.4, d + 0.02)], gl)
                for su, sgn in ((a_, -1), (b_, 1)):
                    q = [(su + sgn * 0.02, 0.15), (su + sgn * 0.02, d - 0.15)]
                    pts = [P(su, z0 + 0.6, 0.15), P(su, z0 + 0.6, d - 0.15), P(su, z1 - 0.4, d - 0.15), P(su, z1 - 0.4, 0.15)]
                    pts = [(x + (-t[0] if sgn < 0 else t[0]) * 0.02, y + (-t[1] if sgn < 0 else t[1]) * 0.02, z) for x, y, z in pts]
                    add_solid(Z, pts if sgn > 0 else pts[::-1], gl, 0.4)
    return ex

def round_corner(cx, cy, r, eave, aout, wall, trim, stone, dome, n=20):
    """full-height round corner bay with a balcony, a crowning drum and a dark dome (Heinen talo, Hallituskatu 14; owner's
    Street View photo 15.11.2026): granite base, rusticated ground storey, balcony with a balustrade on the first floor, tall
    windows, cornice above the eave, dark sheet dome with dormers, wrought-iron crown and a flagpole"""
    def ex(Z, *a):
        zo = 0.0                                                             # the street at the corner above the house's lowest ground: the bay starts there
        if _T and HOUSES:
            h = min(HOUSES, key=lambda h: h['poly'].distance(Point(cx, cy)))
            if h['l'] is not None: zo = max(0.0, TZs(cx + math.cos(aout) * (r + 1.5), cy + math.sin(aout) * (r + 1.5)) - h['l'])
        L = lambda x, y, z: (x - Z.cx, y - Z.cy, z + zo if z < eave - 1.0 else z)
        ang = lambda k, nn=n: 2 * math.pi * k / nn
        ring = lambda rr, nn=n: [(cx + rr * math.cos(ang(k, nn)), cy + rr * math.sin(ang(k, nn))) for k in range(nn)]
        def band(r0, r1, za, zb, mat, nn=n):
            A, Bq = ring(r0, nn), ring(r1, nn)
            for k in range(nn):
                a0, b0, a1, b1 = A[k], A[(k + 1) % nn], Bq[k], Bq[(k + 1) % nn]
                add_solid(Z, [L(*a0, za), L(*b0, za), L(*b1, zb), L(*a1, zb)], mat, 0.6)
        def disc(rr, z, mat, up=True):
            pts = [L(x, y, z) for x, y in ring(rr)]
            add_solid(Z, pts if up else pts[::-1], mat, 0.4)
        def win(a, z0, z1, w, rr, mat=M('#4a5560', 0.15), fr=None):
            ca, sa = math.cos(a), math.sin(a); tx, ty = -sa, ca
            q0 = (cx + ca * rr - tx * w / 2, cy + sa * rr - ty * w / 2); q1 = (cx + ca * rr + tx * w / 2, cy + sa * rr + ty * w / 2)
            if fr:
                f = 0.16; p0 = (q0[0] - tx * f + ca * 0.01, q0[1] - ty * f + sa * 0.01); p1 = (q1[0] + tx * f + ca * 0.01, q1[1] + ty * f + sa * 0.01)
                add_solid(Z, [L(*p0, z0 - f), L(*p1, z0 - f), L(*p1, z1 + f), L(*p0, z1 + f)], fr, 0.5)
            q0 = (q0[0] + ca * 0.03, q0[1] + sa * 0.03); q1 = (q1[0] + ca * 0.03, q1[1] + sa * 0.03)
            add_solid(Z, [L(*q0, z0), L(*q1, z0), L(*q1, z1), L(*q0, z1)], mat, 0.5)
        zb = 5.4                                                             # balcony floor
        band(r + 0.12, r + 0.12, -2.5, 1.2, stone)                           # granite base (down into the slope)
        band(r, r, 1.2, eave + 0.8, wall)                                    # the drum
        for z_ in (1.9, 2.7, 3.5, 4.3): band(r + 0.04, r + 0.04, z_, z_ + 0.08, M('#d9d1bd'))   # rustication joints
        for da, w in ((0, 1.25),):                                           # one window per storey, on the diagonal (owner 15.11.2026: two windows in the corner)
            win(aout + da, 1.9, 4.4, w, r, fr=trim)
            win(aout + da, zb + 0.75 if da == 0 else zb + 1.0, zb + 3.6, w, r, fr=trim)
        band(r + 0.95, r + 0.95, zb - 0.35, zb, trim); disc(r + 0.95, zb, trim); disc(r + 0.95, zb - 0.35, trim, up=False)   # balcony slab
        band(r + 0.9, r + 0.9, zb, zb + 0.95, M('#ebe6da'))                 # balustrade
        band(r + 0.98, r + 0.98, zb + 0.95, zb + 1.08, trim)
        band(r + 0.3, r + 0.3, eave - 0.35, eave + 0.05, trim)               # the main cornice carried round
        band(r + 0.45, r + 0.45, eave + 0.8, eave + 1.15, trim); disc(r + 0.45, eave + 1.15, trim)   # crowning cornice
        z0 = eave + 1.15                                                      # dark dome
        prof = [(r - 0.05, 0.0), (r * 0.99, 0.8), (r * 0.9, 1.6), (r * 0.68, 2.4), (r * 0.36, 2.9), (0.32, 3.0)]
        for (ra, za), (rb, zb_) in zip(prof, prof[1:]): band(ra, rb, z0 + za, z0 + zb_, dome)
        for k in range(4):                                                    # dormers on the dome
            a = aout + math.pi / 4 + k * math.pi / 2; ca, sa = math.cos(a), math.sin(a); tx, ty = -sa, ca; rr = r * 0.95
            c0 = (cx + ca * rr, cy + sa * rr); w = 0.38
            pts = [(c0[0] - tx * w, c0[1] - ty * w), (c0[0] + tx * w, c0[1] + ty * w)]
            add_solid(Z, [L(*pts[0], z0 + 0.25), L(*pts[1], z0 + 0.25), L(*pts[1], z0 + 1.15), L(*pts[0], z0 + 1.15)], dome, 0.5)
            win(a, z0 + 0.4, z0 + 1.0, 0.45, rr + 0.02, M('#30353a', 0.3))
        band(0.32, 0.32, z0 + 3.0, z0 + 3.25, dome); band(0.42, 0.42, z0 + 3.25, z0 + 3.35, dome)
        iron = M('#1f2326', 0.5)
        for k in range(10):                                                   # wrought-iron crown
            a = 2 * math.pi * k / 10; ca, sa = math.cos(a), math.sin(a); tx, ty = -sa, ca; rr = 0.55
            p = (cx + ca * rr, cy + sa * rr)
            add_solid(Z, [L(p[0] - tx * 0.03, p[1] - ty * 0.03, z0 + 3.35), L(p[0] + tx * 0.03, p[1] + ty * 0.03, z0 + 3.35), L(p[0] + tx * 0.03, p[1] + ty * 0.03, z0 + 4.0), L(p[0] - tx * 0.03, p[1] - ty * 0.03, z0 + 4.0)], iron, 0.3)
        band(0.62, 0.62, z0 + 3.95, z0 + 4.03, iron, 10)
        band(0.05, 0.03, z0 + 3.35, z0 + 9.0, M('#eef0f0'), 6)              # flagpole
    return ex

SPECK = {}
# Signelinna, Hallituskatu 2 (Newanderin talo, Signe Hornborg 1890s): salmon render with ochre dressings, dark granite plinth with
# basement windows, rusticated ground floor with round-arched windows, pedimented first-floor windows on ochre aprons, pilasters
_sig = '#d9ac72'
SPECK[1551] = classic_spec(1551, wall='#b0735e', trim=_sig, rust=True, garch=True, hood='pediment', pil=False, bw=3.4,
                           ground=dict(plinth_h=1.9, plinth=M('#3b3c3d', 0.85), basement=True, rustc=M('#8c5444'), rust_step=0.36, sband=0.45, wh=2.2),
                           first=dict(apron=True, apron_mat=M(_sig), sband=0.0, wh=2.3, ww=1.25), upper_mat=M('#4e5358', 0.6),
                           top=dict(blank=True, dentils=True, panels=True, panel_mat=M('#c8875f')), lay=dict(gh=6.0, fh=5.6, frieze=2.2), cornice=(0.5, 0.6, M(_sig)))
# Signelinna (owner + Street View 17.11.2026): a square corner turret at the west end of the Hallituskatu side, standing a little out of
# both faces and rising above the eave to a slender zinc spire; behind it a zinc mansard dome with a dormer; a smaller spire turret on the
# east corner; no door on the Hallituskatu side (the generator put one in the middle)
_ZN = M('#aab2b6', 0.35, 0.6); _OC = M(_sig)   # new galvanised sheet (owner 17.11.2026)
SPECK[1551]['layout'] = dict(SPECK[1551]['layout'])
_f51 = SPECK[1551]['fit']
SPECK[1551]['fit'] = lambda lay_, hh, st: dict(_f51(lay_, hh, st), cols=(lambda c, nb, _c=_f51(lay_, hh, st)['cols']: 'W' if _c(c, nb) == 'D' else _c(c, nb)))
SPECK[1551]['roofmat'] = M('#aab2b6', 0.35, 0.6)
def _corner51(p0, p1):
    """the 45-degree corner of Signelinna (owner 17.11.2026): door at the base; from the first floor up a bay that rises through the
    eave as a turret, with an ochre top storey and the slender galvanised spire standing on it"""
    it = [('box', 0.9, 2.1, 1.9, 4.6, 0.0, 0.06, M('#5a3e2c', 0.6)), ('box', 0.7, 2.3, 4.6, 5.0, 0.0, 0.25, _OC),
          ('box', 0.2, 2.8, 5.6, 16.4, -0.6, 0.85, M('#b0735e')), ('band', 0.1, 2.9, 5.35, 5.65, 0.95, _OC), ('band', 0.1, 2.9, 10.5, 10.9, 0.95, _OC),
          ('band', 0.1, 2.9, 12.9, 13.5, 1.0, _OC), ('box', 0.1, 2.9, 16.4, 18.6, -0.7, 0.95, _OC), ('band', 0.0, 3.0, 18.4, 18.8, 1.05, _OC),
          ('box', 0.7, 2.3, 6.5, 9.6, 0.85, 0.88, M('#3c4248', 0.3)), ('box', 0.8, 2.2, 11.3, 12.6, 0.85, 0.88, M('#3c4248', 0.3)),
          ('box', 1.05, 1.95, 16.9, 18.1, 0.95, 0.98, M('#3c4248', 0.3))]
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1]); n = ((p1[1] - p0[1]) / L, -(p1[0] - p0[0]) / L)
    q0, q1 = (p0[0] + n[0] * 1.0, p0[1] + n[1] * 1.0), (p1[0] + n[0] * 1.0, p1[1] + n[1] * 1.0)
    return [facade_bits(p0, p1, it), facade_bits(q0, q1, [('spire', 1.5, 2.4, 18.8, 27.5, _ZN)])]
SPECK[1551]['extra'] = list(SPECK[1551].get('extra', [])) + [
    *_corner51((255.57, 278.25), (254.05, 280.83)), *_corner51((229.25, 287.17), (226.66, 285.65)),
    facade_bits((256.1, 280.3), (227.2, 287.7), [                 # mansard domes with round dormers over the bays next to the corners
        ('spire', 5.2, 4.2, 16.0, 19.8, _ZN), ('box', 4.6, 5.8, 16.2, 17.8, -0.3, 0.3, _OC), ('box', 4.9, 5.5, 16.5, 17.4, 0.3, 0.33, M('#3c4248', 0.3)),
        ('spire', 24.6, 4.2, 16.0, 19.8, _ZN), ('box', 24.0, 25.2, 16.2, 17.8, -0.3, 0.3, _OC), ('box', 24.3, 24.9, 16.5, 17.4, 0.3, 0.33, M('#3c4248', 0.3))])]
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
_ly['alt'] = lambda x, y: _lyy if (x * 0.9744 - y * 0.225 < -486.6) or (y > 299.5 and x < -412.0) else None   # owner 17.11: the Valtakatu front of 1351 is the yellow part too (plain windows, not the pink arched ones)
cut_walls(1353, (-405.0, 306.9), (0.9737, -0.2279))   # 1353's shell runs the whole Valtakatu front: split where the pink Lyseo ends and the yellow wing begins (owner 17.11)
SPECK[1351] = classic_spec(1351, **_ly); SPECK[1353] = classic_spec(1353, **dict(_ly, lay=dict(gh=4.6, fh=4.2)))
SPECK[1308] = classic_spec(1308, wall='#e9e6de', trim='#f6f4ee', rust=False, garch=False, hood='pediment', pil=False, bw=4.3,
                           lay=dict(nf=1, frieze=0.6, cols=lambda c, nb: 'W'), ground=dict(plinth_h=1.1, plinth=M('#5c6168', 0.85), basement=False, sill=2.1, wh=2.0, ww=1.3, wh_fixed=True, hood='pediment', sband=0.3),
                           attic=dict(blank=True))   # Valtakatu 17 (SV 2026, 17.11): pale one-storey house, six windows under pediments with red-brown sashes, patterned frieze under the eave, dark plinth, NO street door
SPECK[1308]['P']['wall'] = MT('#e9e6de', 'wood'); SPECK[1308]['P']['frame'] = M('#7b3b2c', 0.6)
SPECK[1308]['layout']['rowP']['G']['gwall'] = MT('#e9e6de', 'woodv')   # owner 17.11: wooden house - vertical boards below, horizontal above (the frieze row), decorated window surrounds
SPECK[1311] = classic_spec(1311, wall='#cdd0b6', trim='#ecebe0', rust=True, garch=False, hood='cornice', pil=False, bw=3.1,
                           lay=dict(nf=2, gh=4.6, frieze=1.2, cols=lambda c, nb: 'D' if c == 2 else 'W'), ground=dict(hood='cornice', plinth_h=0.8, plinth=M('#5d5a52', 0.85), basement=False, rustc=M('#bfc2a8'), dw=1.2),
                           first=dict(hood=None, pil=False), attic=dict(ww=0.6, wh=0.3, sill=0.45, hood=None, pil=False, wh_fixed=True))   # Valtakatu 19 (owner's photo 17.11.2026): pale grey-green, rusticated ground floor with corniced windows and a door up steps, framed upper windows, small attic windows, dark plinth (was salmon by mistake)
SPECK[1574] = classic_spec(1574, wall='#e3d7b9', trim='#f4f1ea', rust=False, garch=False, hood='cornice', pil=True, bw=3.1,
                           lay=dict(nf=1, frieze=1.3, cols=lambda c, nb: 'N' if c == nb - 2 else 'W'), ground=dict(plinth_h=1.2, basement=False, sill=1.0, wh=1.85, ww=1.0, wh_fixed=True),
                           attic=dict(ww=0.6, wh=0.3, sill=0.5, hood=None, pil=False, wh_fixed=True))   # Valtakatu 9 (SV 2026, 16.11): one storey on a high grey plinth, framed windows with cornices, a blind (former door) bay, small attic windows
SPECK[1574]['P']['frame'] = M('#7a4a2c', 0.6)   # brown window frames
SPECK[1574]['extra'] = [facade_bits((-2.4, 232.4), (2.8, 231.0), [('wall', 0.0, 5.37, -0.4, 2.3, 0.15, MT('#5a4a36', 'wood'))])]   # weathered board fence with a gate between the pink house and Valtakatu 9 (SV 2026)
def _eave_overhang(i, z_eave, ov=0.55, below=8.2):
    """hip/gable roof with a real eave: the scan's roof edge (all vertices below 'below') is levelled to z_eave and pushed out ov m past the walls
    (owner 16.11.2026: the roof falls four ways and the eave must show on the side too)"""
    G = [r for k, r, _ in RAW.get(i, []) if k == 'G'][0]; cx = sum(q[0] for q in G) / len(G); cy = sum(q[1] for q in G) / len(G)
    def mv(q):
        if q[2] >= below: return q
        dx, dy = q[0] - cx, q[1] - cy; L = math.hypot(dx, dy) or 1
        return (q[0] + dx / L * ov * 1.41, q[1] + dy / L * ov * 1.41, z_eave - 0.12)
    RAW[i] = [(k, [mv(q) for q in r] if k == 'R' else [(q[0], q[1], min(q[2], z_eave) if q[2] > 0.5 else q[2]) for q in r] if k == 'W' else r, h) for k, r, h in RAW.get(i, [])]
_eave_overhang(1294, 7.0)
SPECK[1577] = classic_spec(1577, wall='#d6a96e', trim='#e6c98a', rust=False, garch=False, hood=None, pil=True, bw=2.5,
                           lay=dict(nf=2, gh=4.2, cols=lambda c, nb: 'S' if c % 2 == 0 else 'D'), ground=dict(plinth_h=0.45, basement=False, door=M('#c9a24a', 0.6), dw=1.0),
                           first=dict(ww=0.75, wh=0.55, sill=0.9, hood=None, pil=False, wh_fixed=True))   # 7 Antinkatu (SV 2026, 16.11): ochre two-storey shop house - three big shop windows between yellow-framed doors, a low upper floor with small windows, dark low hip roof
SPECK[1293] = classic_spec(1293, wall='#e5d6a4', trim='#f3eee2', rust=False, garch=False, hood='cornice', pil=False, bw=3.4,
                           lay=dict(nf=2, gh=4.6, frieze=1.4, cols=lambda c, nb: 'W'), ground=dict(plinth_h=1.5, plinth=M('#a08a7c', 0.9), basement=False, sill=0.3, wh=2.2, ww=1.5, wh_fixed=True, hood='cornice', pil=True),
                           attic=dict(ww=0.7, wh=0.5, sill=0.45, hood=None, pil=False, wh_fixed=True))   # Valtakatu 11 (SV 2026, 16.11): cream-yellow Jugend house on a red-granite base, big ground-floor windows in heavy white surrounds, curved gables (was grey-green)
SPECK[1293]['P']['wall'] = MT('#e5d6a4', 'plaster')
SPECK[1622] = dict(spec_for(1622)); SPECK[1622].pop('extra', None)   # red board shed in the garden behind the Antinkatu fence (SV 2026, 16.11)
SPECK[1577]['extra'] = [facade_bits((26.7, 272.3), (34.7, 307.3), [('wall', 0.3, 35.6, -0.5, 2.25, 0.12, MT('#c8c5bb', 'wood'))])]   # long pale board fence along Antinkatu in front of the garden (SV 2026, 16.11)
SPECK[1294] = classic_spec(1294, wall='#e3b8a6', trim='#f4efe8', rust=False, garch=False, hood=None, pil=True, bw=2.9,
                           lay=dict(nf=1, frieze=1.2, cols=lambda c, nb: 'W'), ground=dict(plinth_h=1.3, basement=False, sill=0.95, wh=1.75, ww=1.05, wh_fixed=True),
                           attic=dict(ww=0.6, wh=0.28, sill=0.45, hood=None, pil=False, wh_fixed=True))   # pink one-storey house on a high plinth, white pilasters, small attic windows; white gable end (SV 2026, 16.11; was 2 storeys with arched windows)
_s1294 = classic_spec(1294, wall='#e3b8a6', trim='#f4efe8', rust=False, garch=False, hood=None, pil=False, bw=3.2,
                      lay=dict(nf=1, frieze=1.2, cols=lambda c, nb: 'W' if c == nb - 1 else 'N'), ground=dict(plinth_h=1.3, basement=False, sill=0.95, wh=1.75, ww=1.05, wh_fixed=True),
                      attic=dict(blank=True), yard_same=True)   # its east side wall along the yard gap: blank (sunlit, it reads white), one window at the far (north) end, the eave cornice runs on round the corner (SV 2026, 16.11)
SPECK[1294]['alt'] = lambda x, y: _s1294 if x > -3.0 else None
# Eteläranta / Antinkatu corner (Street View 14.11.2026, owner): three tall storeys with small windows in the top storey. The salmon
# corner house (white dressings, grey rusticated ground floor) has the 45-degree chamfer with the door and three window bays on the
# Eteläranta side; west of it (the shell's roof steps at x = 52) the Eteläranta front is a pale grey-green house. One LoD2 shell holds
# both: its Eteläranta wall is cut at x = 52 and the pieces get their spec by position.
cut_walls(1560, (52.0, 439.2), (0.9732, -0.2298))
cut_walls(1560, (59.6, 413.7), (0.2257, 0.9742))
lower_eave(1560, lambda r: all(q[1] < 413.8 and q[0] > 55 for q in r) and min(q[2] for q in r) < 0.5, 4.2, 2.6)   # its Antinkatu wall also runs along the low white house 2 Antinkatu: cut where the wall steps up
_k1560 = dict(lay=dict(nf=3, gh=5.6, frieze=1.4), ground=dict(rustc=M('#9fa29e')), top=dict(wh=1.35, ww=1.1, sill=0.9, hood=None))
_e1560 = classic_spec(1560, wall='#c9cfc6', trim='#f2f1ec', rust=True, garch=False, hood='cornice', pil=True, bw=2.85, **dict(_k1560, lay=dict(_k1560['lay'], cols=lambda c, nb: 'W')))   # grey-green Eteläranta house: nine narrow window bays, no door on the street (wireframe 14.11.2026)
_ks1560 = dict(_k1560, ground=dict(rustc=M('#c4c1b8'), gwall=M('#e9e6dd')), attic=dict(wall=M('#ece8de')))   # salmon corner house: white rusticated ground floor, white attic frieze (wireframe 14.11.2026)
SPECK[1560] = classic_spec(1560, wall='#d98a6c', trim='#f4f1ea', rust=True, garch=True, hood='cornice', pil=True, **_ks1560)
_a1560 = classic_spec(1560, wall='#d98a6c', trim='#f4f1ea', rust=True, garch=True, hood='cornice', pil=True, **dict(_ks1560, bw=4.1, lay=dict(_k1560['lay'], cols=lambda c, nb: 'G' if c == 0 else 'D' if c == 2 else 'W')))   # Antinkatu front: five bays, arched gateway at the south end, door in the 3rd bay
_c1560 = classic_spec(1560, wall='#d98a6c', trim='#f4f1ea', rust=True, garch=True, hood='cornice', pil=True, bw=2.6,
                      **dict(_ks1560, lay=dict(_k1560['lay'], cols=lambda c, nb: 'D'), first=dict(balcony=True, hood='cornice')))      # the chamfer: corner door, windows above
_w1561 = classic_spec(1561, wall='#efede6', trim='#f7f6f1', rust=False, garch=False, hood=None, pil=False, lay=dict(nf=1))   # the low white house 2 Antinkatu lies inside the corner house's LoD2 shell
SPECK[1560]['alt'] = lambda x, y: _w1561 if y < 413.6 else (_c1560 if 62.3 < x < 64.8 and 433.5 < y < 437.2 else _e1560 if x < 52.0 and y > 430.0 else _a1560 if x > 59.0 and y < 433.5 else None)
SPECK[1286] = classic_spec(1286, trim='#f4f1ea', rust=False, garch=False, hood='pediment', pil=False, lay=dict(nf=3, gh=5.2, frieze=1.4),
                           top=dict(wh=1.35, ww=1.1, sill=0.9, hood=None))   # Hallituskatu: salmon, pediments on the first floor, small top-floor windows (owner 14.11.2026)
squash(1578, 6.6, 0.06)   # 6 Antinkatu / Hallituskatu (1578): a LOW one-storey house; the scan's walls reach 9-18 m (owner 16.11, Street View 2026)
SPECK[1578] = classic_spec(1578, wall='#d6b27a', trim='#f1ede2', rust=False, garch=False, hood=None, pil=True, bw=3.3,
                           lay=dict(nf=1, frieze=1.1, cols=lambda c, nb: 'W'), ground=dict(plinth_h=0.7, plinth=M('#9b978e', 0.85), basement=False, sill=0.9, wh=2.1, ww=1.3, wh_fixed=True),
                           attic=dict(ww=0.5, wh=0.28, sill=0.45, hood=None, pil=False, wh_fixed=True))   # ochre, white rusticated pilaster strips, white window surrounds, small attic windows under the cornice
SPECK[1578]['extra'] = [facade_bits((57.6, 327.4), (51.8, 302.6), [('vents', 1.05, 1, 5.5, None, 0.55, 0.3), ('vents', 3.15, 1, 5.5, None, 0.55, 0.3), ('vents', 5.25, 1, 5.5, None, 0.55, 0.3), ('vents', 7.35, 1, 5.5, None, 0.55, 0.3), ('vents', 9.45, 1, 5.5, None, 0.55, 0.3), ('vents', 11.55, 1, 5.5, None, 0.55, 0.3), ('vents', 13.65, 1, 5.5, None, 0.55, 0.3), ('vents', 15.75, 1, 5.5, None, 0.55, 0.3), ('vents', 17.85, 1, 5.5, None, 0.55, 0.3), ('vents', 19.95, 1, 5.5, None, 0.55, 0.3), ('vents', 22.05, 1, 5.5, None, 0.55, 0.3), ('vents', 24.15, 1, 5.5, None, 0.55, 0.3)])]   # the row of small attic windows under the cornice (Antinkatu)
SPEC[1581]['P'] = dict(SPEC[1581]['P'], wall=M('#5c7377', 0.35, 0.1), spandrel=M('#4b6266', 0.35, 0.1))   # Valtakatu 7 tower: blue-green glass mosaic since the renovation (Street View 2026, 16.11; the white/orange note of 13.11 was older imagery)
RAW[1579] = [(k, [(q[0], q[1], 20.6 + (q[2] - 20.6) * 0.15 if q[1] > 280.0 and q[0] > 60.0 and q[2] > 20.6 else q[2]) for q in r], h) for k, r, h in RAW.get(1579, [])]   # Hallituskatu 6 (1963): 5 floors over an open ground floor - the scan stood a storey too high (SV 2026, 16.11)
RAW[1579] = [(k, [(q[0], q[1], 21.6 + (q[2] - 21.6) * 0.1 if q[1] < 240.0 and q[0] > 95.0 and q[2] > 21.6 else q[2]) for q in r], h) for k, r, h in RAW.get(1579, [])]   # Valtakatu 5 (1603): five floors over the shops, ~21.5 m - the scan stood two storeys too high (SV 2026, 16.11)
import zones as _zn; _V5P = _zn._V5P
_zn._SPEC_Y2B['P'].update(wall=MT('#ebe8e0', 'plaster'), spandrel=MT('#ebe8e0', 'plaster'), fascia=M('#ebe8e0'), joints=M('#d9d5cb'), frame=M('#3a3f44', 0.5))   # Yrjönkatu 2 b (1618) reads white in Street View 2026 (17.11), not brick
SPEC[_zn.VALT3]['P'].update(wall=M('#e9e6de'), spandrel=M('#cdb98e'), fascia=M('#e9e6de'))   # Valtakatu 3: white with beige bands under the windows (SV 2026, 17.11)
_e1548 = classic_spec(1548, wall='#b08d58', trim='#9ea3a6', rust=False, garch=False, hood=None, pil=False, bw=4.25,
                      lay=dict(nf=7, gh=3.6, fh=3.0, cols=lambda c, nb: 'P' if c == nb // 2 else 'N'), ground=dict(gwall=M('#3a3d40', 0.5), plinth_h=0.2, basement=False, blank=True),
                      first=dict(ww=1.25, wh=1.5, sill=0.95, hood=None, pil=False, wh_fixed=True), top=dict(ww=1.25, wh=1.5, sill=0.95, hood=None, pil=False, wh_fixed=True), yard_same=True)
_e1548['P']['wall'] = MT('#b08d58', 'brick', 0.8); _e1548['P']['frame'] = M('#9ea3a6', 0.5)
SPECK[1548] = dict(spec_for(1548)); SPECK[1548]['alt'] = lambda x, y: _e1548 if y < 181.5 or y > 236.0 else None   # Valtakatu 1 (1965) end walls: yellow-brown brick with one central column of windows over grey panels, open ground floor on pilotis (SV 2026, 17.11)
SPECK[1548]['extra'] = list(SPECK[1548].get('extra', [])) + [facade_bits((219.8, 180.8), (232.3, 177.9), [('box', 4.30, 8.50, 3.4, 22.6, 0.0, 0.85, M('#8d9396', 0.6)), ('box', 4.55, 8.25, 4.80, 6.30, 0.85, 0.9, M('#3d4a52', 0.15, 0.3)), ('box', 4.30, 4.35, 4.80, 6.30, 0.0, 0.9, M('#3d4a52', 0.15, 0.3)), ('box', 4.55, 8.25, 7.80, 9.30, 0.85, 0.9, M('#3d4a52', 0.15, 0.3)), ('box', 4.30, 4.35, 7.80, 9.30, 0.0, 0.9, M('#3d4a52', 0.15, 0.3)), ('box', 4.55, 8.25, 10.80, 12.30, 0.85, 0.9, M('#3d4a52', 0.15, 0.3)), ('box', 4.30, 4.35, 10.80, 12.30, 0.0, 0.9, M('#3d4a52', 0.15, 0.3)), ('box', 4.55, 8.25, 13.80, 15.30, 0.85, 0.9, M('#3d4a52', 0.15, 0.3)), ('box', 4.30, 4.35, 13.80, 15.30, 0.0, 0.9, M('#3d4a52', 0.15, 0.3)), ('box', 4.55, 8.25, 16.80, 18.30, 0.85, 0.9, M('#3d4a52', 0.15, 0.3)), ('box', 4.30, 4.35, 16.80, 18.30, 0.0, 0.9, M('#3d4a52', 0.15, 0.3)), ('box', 4.55, 8.25, 19.80, 21.30, 0.85, 0.9, M('#3d4a52', 0.15, 0.3)), ('box', 4.30, 4.35, 19.80, 21.30, 0.0, 0.9, M('#3d4a52', 0.15, 0.3))]), facade_bits((245.9, 236.4), (234.2, 239.1), [('box', 3.90, 8.10, 3.4, 22.6, 0.0, 0.85, M('#8d9396', 0.6)), ('box', 4.15, 7.85, 4.80, 6.30, 0.85, 0.9, M('#3d4a52', 0.15, 0.3)), ('box', 3.90, 3.95, 4.80, 6.30, 0.0, 0.9, M('#3d4a52', 0.15, 0.3)), ('box', 4.15, 7.85, 7.80, 9.30, 0.85, 0.9, M('#3d4a52', 0.15, 0.3)), ('box', 3.90, 3.95, 7.80, 9.30, 0.0, 0.9, M('#3d4a52', 0.15, 0.3)), ('box', 4.15, 7.85, 10.80, 12.30, 0.85, 0.9, M('#3d4a52', 0.15, 0.3)), ('box', 3.90, 3.95, 10.80, 12.30, 0.0, 0.9, M('#3d4a52', 0.15, 0.3)), ('box', 4.15, 7.85, 13.80, 15.30, 0.85, 0.9, M('#3d4a52', 0.15, 0.3)), ('box', 3.90, 3.95, 13.80, 15.30, 0.0, 0.9, M('#3d4a52', 0.15, 0.3)), ('box', 4.15, 7.85, 16.80, 18.30, 0.85, 0.9, M('#3d4a52', 0.15, 0.3)), ('box', 3.90, 3.95, 16.80, 18.30, 0.0, 0.9, M('#3d4a52', 0.15, 0.3)), ('box', 4.15, 7.85, 19.80, 21.30, 0.85, 0.9, M('#3d4a52', 0.15, 0.3)), ('box', 3.90, 3.95, 19.80, 21.30, 0.0, 0.9, M('#3d4a52', 0.15, 0.3))])]   # owner 17.11: the window column on each end wall is a projecting bay (grey panels, glass bands), not flush
_blankw = classic_spec(1553, wall='#ecebe6', trim='#ecebe6', rust=False, garch=False, hood=None, pil=False, bw=4.0, lay=dict(nf=1, cols=lambda c, nb: 'N'), ground=dict(plinth_h=0.2, basement=False, blank=True, sband=0), yard_same=True)
SPEC[_zn.VALT3]['alt'] = lambda x, y: _blankw if (178.0 < x < 203.5 and 197.0 < y < 205.0) or (x > 199.5 and 186.0 < y < 199.0) else None   # owner 17.11: the white house's south side (over the pavilion) has no windows
SPECK[1398] = classic_spec(1398, wall='#8f8076', trim='#d9d4cb', rust=False, garch=False, hood=None, pil=False, bw=3.4,
                           lay=dict(nf=7, gh=3.4, fh=2.9, cols=lambda c, nb: 'W' if c == 1 else 'X'), ground=dict(plinth_h=0.3, basement=False, sill=1.5, wh=0.6, ww=0.9, wh_fixed=True),
                           first=dict(ww=1.4, wh=1.4, sill=0.9, hood=None, pil=False, wh_fixed=True), top=dict(ww=1.4, wh=1.4, sill=0.9, hood=None, pil=False, wh_fixed=True), yard_same=True)
SPECK[1398]['P']['wall'] = MT('#8f8076', 'brick', 0.8)
SPECK[1398]['extra'] = [facade_bits((-183.2, 250.8), (-208.5, 256.6), [('box', 21.0, 24.2, 3.5, 21.0, 0.0, 0.9, MT('#8f8076', 'brick', 0.8)), ('box', 21.2, 24.0, 4.7, 6.1, 0.9, 0.95, M('#3d4a52', 0.15, 0.3)), ('box', 21.2, 24.0, 7.6, 9.0, 0.9, 0.95, M('#3d4a52', 0.15, 0.3)), ('box', 21.2, 24.0, 10.5, 11.9, 0.9, 0.95, M('#3d4a52', 0.15, 0.3)), ('box', 21.2, 24.0, 13.4, 14.8, 0.9, 0.95, M('#3d4a52', 0.15, 0.3)), ('box', 21.2, 24.0, 16.3, 17.7, 0.9, 0.95, M('#3d4a52', 0.15, 0.3)), ('box', 21.2, 24.0, 19.2, 20.6, 0.9, 0.95, M('#3d4a52', 0.15, 0.3))])]   # owner 17.11: one small window in the base; a projecting bay starts ~2 m from the west corner
SPECK[1352] = classic_spec(1352, wall='#d8b48c', trim='#efede7', rust=False, garch=False, hood=None, pil=False, bw=3.2,
                           lay=dict(nf=6, gh=3.4, fh=2.95, cols=lambda c, nb: 'W'), ground=dict(gwall=MT('#efede7', 'plaster'), plinth_h=0.4, basement=False, ww=1.6, wh=1.5, wh_fixed=True),
                           first=dict(ww=1.6, wh=1.5, sill=0.8, hood=None, pil=False, sband=0.9, wh_fixed=True), top=dict(ww=1.6, wh=1.5, sill=0.8, hood=None, pil=False, sband=0.9, wh_fixed=True), yard_same=True)
SPECK[1352]['P']['wall'] = MT('#d8b48c', 'brick', 0.8); SPECK[1352]['P']['trim'] = MT('#efede7', 'plaster')   # owner 17.11: light brick with white render bands; glazed balconies (below)
SPECK[1352]['extra'] = [facade_bits((-375.3, 212.0), (-376.5, 206.4), [('box', 0.0, 5.70, 3.40, 3.58, 0.0, 2.40, M('#3b3f42', 0.6)), ('box', 0.0, 5.70, 3.58, 6.15, 2.32, 2.40, M('#4a5a63', 0.1, 0.3)), ('box', 0.0, 5.70, 3.58, 4.50, 2.30, 2.42, M('#1f2123', 0.4)), ('box', 0.0, 5.70, 6.35, 6.53, 0.0, 2.40, M('#3b3f42', 0.6)), ('box', 0.0, 5.70, 6.53, 9.10, 2.32, 2.40, M('#4a5a63', 0.1, 0.3)), ('box', 0.0, 5.70, 6.53, 7.45, 2.30, 2.42, M('#1f2123', 0.4)), ('box', 0.0, 5.70, 9.30, 9.48, 0.0, 2.40, M('#3b3f42', 0.6)), ('box', 0.0, 5.70, 9.48, 12.05, 2.32, 2.40, M('#4a5a63', 0.1, 0.3)), ('box', 0.0, 5.70, 9.48, 10.40, 2.30, 2.42, M('#1f2123', 0.4)), ('box', 0.0, 5.70, 12.25, 12.43, 0.0, 2.40, M('#3b3f42', 0.6)), ('box', 0.0, 5.70, 12.43, 15.00, 2.32, 2.40, M('#4a5a63', 0.1, 0.3)), ('box', 0.0, 5.70, 12.43, 13.35, 2.30, 2.42, M('#1f2123', 0.4)), ('box', 0.0, 5.70, 15.20, 15.38, 0.0, 2.40, M('#3b3f42', 0.6)), ('box', 0.0, 5.70, 15.38, 17.95, 2.32, 2.40, M('#4a5a63', 0.1, 0.3)), ('box', 0.0, 5.70, 15.38, 16.30, 2.30, 2.42, M('#1f2123', 0.4)), ('box', 0.0, 5.70, 18.15, 18.33, 0.0, 2.40, M('#3b3f42', 0.6))]), facade_bits((-377.0, 203.2), (-378.0, 199.0), [('box', 0.0, 4.30, 3.40, 3.58, 0.0, 2.45, M('#3b3f42', 0.6)), ('box', 0.0, 4.30, 3.58, 6.15, 2.37, 2.45, M('#4a5a63', 0.1, 0.3)), ('box', 0.0, 4.30, 3.58, 4.50, 2.35, 2.47, M('#1f2123', 0.4)), ('box', 0.0, 4.30, 6.35, 6.53, 0.0, 2.45, M('#3b3f42', 0.6)), ('box', 0.0, 4.30, 6.53, 9.10, 2.37, 2.45, M('#4a5a63', 0.1, 0.3)), ('box', 0.0, 4.30, 6.53, 7.45, 2.35, 2.47, M('#1f2123', 0.4)), ('box', 0.0, 4.30, 9.30, 9.48, 0.0, 2.45, M('#3b3f42', 0.6)), ('box', 0.0, 4.30, 9.48, 12.05, 2.37, 2.45, M('#4a5a63', 0.1, 0.3)), ('box', 0.0, 4.30, 9.48, 10.40, 2.35, 2.47, M('#1f2123', 0.4)), ('box', 0.0, 4.30, 12.25, 12.43, 0.0, 2.45, M('#3b3f42', 0.6)), ('box', 0.0, 4.30, 12.43, 15.00, 2.37, 2.45, M('#4a5a63', 0.1, 0.3)), ('box', 0.0, 4.30, 12.43, 13.35, 2.35, 2.47, M('#1f2123', 0.4)), ('box', 0.0, 4.30, 15.20, 15.38, 0.0, 2.45, M('#3b3f42', 0.6)), ('box', 0.0, 4.30, 15.38, 17.95, 2.37, 2.45, M('#4a5a63', 0.1, 0.3)), ('box', 0.0, 4.30, 15.38, 16.30, 2.35, 2.47, M('#1f2123', 0.4)), ('box', 0.0, 4.30, 18.15, 18.33, 0.0, 2.45, M('#3b3f42', 0.6))])]   # owner 17.11: glazed balconies stacked in the three recesses of the Annankatu front
SPECK[1527] = classic_spec(1527, wall='#e3d8b6', trim='#f3f1ea', rust=False, garch=False, hood=None, pil=False, bw=3.0,
                           lay=dict(nf=2, gh=3.6, fh=3.4, cols=lambda c, nb: 'W'), ground=dict(plinth_h=0.4, basement=False, ww=1.6, wh=1.3, sill=0.9, wh_fixed=True), first=dict(ww=2.2, wh=1.2, sill=1.2, hood=None, wh_fixed=True), yard_same=True)
SPECK[1527]['P']['wall'] = MT('#e3d8b6', 'brick', 0.8)   # Annankatu school: light yellow brick, white-framed windows, a band of windows upstairs (owner 17.11)
SPECK[1535] = dict(spec_for(1535)); SPECK[1535]['extra'] = [facade_bits((-469.6, 343.0), (-412.8, 329.6), [('box', 49.7, 55.3, 3.60, 3.82, 0.0, 1.4, M('#e9e8e3')), ('box', 49.7, 55.3, 3.82, 4.80, 1.33, 1.4, M('#a9bcbd', 0.1, 0.2)), ('box', 49.7, 55.3, 6.80, 7.02, 0.0, 1.4, M('#e9e8e3')), ('box', 49.7, 55.3, 7.02, 8.00, 1.33, 1.4, M('#a9bcbd', 0.1, 0.2)), ('box', 49.7, 55.3, 10.00, 10.22, 0.0, 1.4, M('#e9e8e3')), ('box', 49.7, 55.3, 10.22, 11.20, 1.33, 1.4, M('#a9bcbd', 0.1, 0.2)), ('box', 49.7, 55.3, 13.20, 13.42, 0.0, 1.4, M('#e9e8e3')), ('box', 49.7, 55.3, 13.42, 14.40, 1.33, 1.4, M('#a9bcbd', 0.1, 0.2)), ('box', 49.7, 55.3, 16.40, 16.62, 0.0, 1.4, M('#e9e8e3')), ('box', 49.7, 55.3, 16.62, 17.60, 1.33, 1.4, M('#a9bcbd', 0.1, 0.2)), ('box', 23.7, 28.3, 3.60, 3.82, 0.0, 1.4, M('#e9e8e3')), ('box', 23.7, 28.3, 3.82, 4.80, 1.33, 1.4, M('#a9bcbd', 0.1, 0.2)), ('box', 23.7, 28.3, 6.80, 7.02, 0.0, 1.4, M('#e9e8e3')), ('box', 23.7, 28.3, 7.02, 8.00, 1.33, 1.4, M('#a9bcbd', 0.1, 0.2)), ('box', 23.7, 28.3, 10.00, 10.22, 0.0, 1.4, M('#e9e8e3')), ('box', 23.7, 28.3, 10.22, 11.20, 1.33, 1.4, M('#a9bcbd', 0.1, 0.2)), ('box', 23.7, 28.3, 13.20, 13.42, 0.0, 1.4, M('#e9e8e3')), ('box', 23.7, 28.3, 13.42, 14.40, 1.33, 1.4, M('#a9bcbd', 0.1, 0.2)), ('box', 23.7, 28.3, 16.40, 16.62, 0.0, 1.4, M('#e9e8e3')), ('box', 23.7, 28.3, 16.62, 17.60, 1.33, 1.4, M('#a9bcbd', 0.1, 0.2))])]   # Valtakatu 26: two stacks of projecting balconies with glass parapets (SV 2026, 17.11)

def _glazed_stack(sa, sb, f0=1, f1=7, fh=3.1875, d=1.5):
    """a stack of glazed balconies (frameless glass, frosted railing band, dark slabs) on floors f0..f1"""
    sl, gl, fr = M('#2f3336', 0.6), M('#5d7078', 0.08, 0.25), M('#b7c4c6', 0.35)
    out = []
    for k in range(f0, f1 + 1):
        z = k * fh
        out += [('box', sa, sb, z - 0.05, z + 0.22, 0.0, d, sl),             # slab, dark edge
                ('box', sa + 0.05, sb - 0.05, z + 0.22, z + 1.1, d - 0.08, d - 0.02, fr),   # frosted railing band
                ('box', sa + 0.03, sb - 0.03, z + 0.22, z + fh - 0.05, 0.0, d - 0.06, gl)]  # glazing
    out.append(('box', sa, sb, (f1 + 1) * fh - 0.05, (f1 + 1) * fh + 0.2, 0.0, d, sl))       # cap over the top balcony
    return out
# Valtakatu 26 (owner 17.11.2026): pitched roof along Valtakatu, dark glazed gable at the Katariinankatu corner; at the west end of the
# Valtakatu side a two-storey recess (white soffit, brown metal back wall) behind a brick corner pier (Street View s 1.0-3.7 m from the corner)
B[1535]['p'] = [-4097, 3426, -4665, 3561, -4688, 3466, -4694, 3440, -4696, 3430, -4686, 3428, -4660, 3422, -4128, 3296]
SPECK[1535]['roof'] = dict(kind='gable', rise=4.5, ov=0.3, mat=M('#3a3e42', 0.5, 0.3), gablemat=M('#41505a', 0.1, 0.3))
_l35 = dict(SPECK[1535]['layout']); _r35 = list(_l35['rows'])
_l35['rows'] = [(_r35[0][0] + _r35[1][0], 'plain', 'R')] + _r35[2:]
_l35['rowP'] = dict(_l35.get('rowP', {}), R=dict(setback=3.7, soffit=M('#ecebe7'), wall=M('#6e4b36', 0.5, 0.2), open_ends=True))
SPECK[1535]['walls'] = {2: _l35, 5: _l35}   # owner 17.11: the recess runs round the corner (both streets), a brick pier stands at the corner
SPECK[1535]['extra'] = list(SPECK[1535]['extra']) + [facade_bits((-469.6, 343.0), (-412.8, 329.6), [('box', 0.0, 1.0, 0.0, 6.5, -1.0, 0.0, MT('#5a3f35', 'brick', 0.8))])]   # inner faces of the corner pier
SPECK[1516] = dict(spec_for(1516)); SPECK[1516]['roof'] = dict(kind='flat', mat=M('#3a3e42', 0.5), pent=(0.8, 3.0), pentmat=M('#9aaab3', 0.15, 0.3))   # glazed top storey, light grey-blue (SV 17.11.2026)
_lt16 = dict(SPECK[1516]['layout']); _lt16['rows'] = list(_lt16['rows'][:-1]) + [(_lt16['rows'][-1][0], _lt16['rows'][-1][1], 'T')]
_lt16['rowP'] = dict(_lt16.get('rowP', {}), T=dict(wall=M('#b4bfc5', 0.4)))   # owner 17.11: the two top storeys are clad in a light grey-blue material
SPECK[1516]['layout'] = _lt16; SPECK[1516]['roof']['pentmat'] = M('#b4bfc5', 0.4)
_l16 = dict(SPECK[1516]['layout']); _l16['cols'] = lambda c, nb: 'B' if c == 0 else 'W'; _l16['P'] = dict(_l16.get('P', {}), rail=M('#b7c4c6', 0.35), ldepth=1.6)
SPECK[1516]['walls'] = {2: _l16}   # owner 17.11: the glazed balconies at the NW corner (Katariinankatu side) are recessed loggias
# Valtakatu 24 / LoD2 shell (Street View 17.11.2026): white rendered west part, a glazed stair column, orange-red brick east part with dark window bands,
# grey panel cladding along the whole ground floor; the east end grey with balconies
def _s58(wall):
    s = dict(spec_for(1458)); s['P'] = dict(s['P'], wall=wall); l = dict(s['layout']); l['plain'] = True; s['layout'] = l; return s
_S58 = [_s58(M('#ecebe7')), _s58(M('#2f4252', 0.1, 0.3)), _s58(MT('#9c4f39', 'brick', 0.8)), _s58(M('#4d5154', 0.5))]
def _ra58(x, y, A=(-412.8, 329.6), t=(0.9709, -0.2393)):
    s = (x - A[0]) * t[0] + (y - A[1]) * t[1]; d = (x - A[0]) * t[1] - (y - A[1]) * t[0]
    if abs(d) > 2.5: return None                         # only the Valtakatu side
    return _S58[0] if s < 11.4 else _S58[1] if s < 14.0 else _S58[2] if s < 19.6 else _S58[3]
GLASS_SKY = M('#71838f', 0.05, 0.4)   # window glass as Street View shows it: grey-blue sky reflection, not black
def kwin(it, s0, s1, z0, z1, wall, panes=None, sill=True, frame=None, dd=0.0):
    """a modern window on a plain wall: a wall-coloured reveal standing 0.14 m out (so the glass reads as set back), dark frame,
    sky-grey glass split into panes by mullions, a light sill flashing below"""
    fr = frame or M('#34383b', 0.5); w = s1 - s0; n = panes or max(1, min(3, round(w / 0.95))); B_ = lambda *a: a[:5] + (a[5] + dd, a[6] + dd) + a[7:]
    it += [B_('box', s0 - 0.12, s0, z0, z1, 0.0, 0.14, wall), B_('box', s1, s1 + 0.12, z0, z1, 0.0, 0.14, wall),
           B_('box', s0 - 0.12, s1 + 0.12, z1, z1 + 0.12, 0.0, 0.14, wall),
           B_('box', s0, s1, z0, z1, 0.0, 0.03, fr), B_('box', s0 + 0.06, s1 - 0.06, z0 + 0.06, z1 - 0.06, 0.03, 0.045, GLASS_SKY)]
    for q in range(1, n): u = s0 + w * q / n; it.append(B_('box', u - 0.035, u + 0.035, z0, z1, 0.03, 0.06, fr))
    if sill: it.append(B_('box', s0 - 0.06, s1 + 0.06, z0 - 0.06, z0, 0.0, 0.18, M('#c9cbcc', 0.4)))
def _x58():
    """Valtakatu 24 street side, measured on the Street View pose (owner 17.11.2026: windows, stair column, garage door, entrance,
    ground-floor windows, the stair under the balconies). Ground storey 5.5 m, then four storeys of 2.95 m. East of the LoD2 shell
    (s 22.3-29.3, up to Karhukortteli 1451) a recessed bay: dark wall 2 m back, balconies with dark slatted rails, a stair under them."""
    fr, gp, dk = M('#34383b', 0.5), M('#7f8386', 0.5), M('#26282a', 0.6)
    WH, BR, BG = M('#ecebe7'), MT('#9c4f39', 'brick', 0.8), M('#4d5154', 0.5)
    it = []
    it.append(('box', 0.9, 19.6, 0.0, 5.5, 0.0, 0.02, gp))                                   # grey panel cladding along the ground storey
    for zz in (1.4, 2.8, 4.2): it.append(('box', 0.9, 19.6, zz - 0.02, zz + 0.02, 0.02, 0.035, M('#6c7073', 0.5)))   # panel joints
    it += [('box', 5.8, 9.9, 0.0, 3.0, 0.02, 0.04, dk), ('box', 5.6, 10.1, 3.0, 3.2, 0.0, 0.7, gp)]   # garage door + its canopy
    for zz in (0.5, 1.0, 1.5, 2.0, 2.5): it.append(('box', 5.8, 9.9, zz - 0.015, zz + 0.015, 0.04, 0.05, M('#3a3c3e', 0.5)))   # door sections
    kwin(it, 6.8, 9.0, 4.1, 5.0, gp, panes=2)                                                   # small window over the garage
    it += [('box', 11.4, 15.6, 0.0, 3.0, 0.02, 0.04, GLASS_SKY), ('box', 11.1, 15.9, 3.0, 3.25, 0.0, 0.9, M('#3a3d40', 0.5))]   # glazed entrance, canopy
    for u in (11.45, 12.45, 13.5, 14.55, 15.55): it.append(('box', u - 0.05, u + 0.05, 0.0, 3.0, 0.04, 0.07, fr))
    it.append(('box', 11.4, 15.6, 2.3, 2.38, 0.04, 0.07, fr))
    it.append(('box', 12.0, 13.6, 3.6, 4.6, 0.02, 0.05, M('#5c6064', 0.5)))                 # the "19D" plate
    kwin(it, 16.5, 17.2, 2.9, 4.8, gp, panes=1); kwin(it, 17.8, 19.2, 2.9, 4.9, gp, panes=2)   # ground-storey windows of the brick part
    it.append(('box', 16.9, 19.1, 1.7, 2.5, 0.02, 0.06, M('#3e4245', 0.5)))                  # house-name plate
    for fl in range(4):
        z = 5.5 + fl * 2.95
        if fl == 0: kwin(it, 4.6, 9.3, z + 0.35, z + 2.6, WH, panes=4)
        else: kwin(it, 4.8, 7.6, z + 0.6, z + 2.4, WH, panes=2); kwin(it, 8.6, 10.2, z + 0.6, z + 2.4, WH, panes=1)
        it.append(('box', 11.4, 14.0, z - 0.08, z + 0.08, 0.0, 0.06, fr))                    # stair column: floor lines in the glazing
        kwin(it, 14.7, 15.8, z + 0.55, z + 2.35, BR, panes=1)                                  # brick part: window | dark panel | window, brick bands between
        it.append(('box', 15.9, 17.8, z + 0.55, z + 2.35, 0.0, 0.03, M('#3c3f42', 0.5))); kwin(it, 17.9, 19.2, z + 0.55, z + 2.35, BR, panes=2)
        # east bay (owner 17.11): two recessed balconies whose fronts stand in line with Karhukortteli 1451 (d -1.7), back wall at d -3.5
        if fl < 4:
            for s0, s1 in ((22.35, 25.7), (25.8, 29.15)):
                it += [('box', s0, s1, z - 0.22, z, -3.5, -1.7, M('#3a3e42', 0.5)), ('box', s0, s1, z, z + 1.05, -1.78, -1.7, M('#3f4448', 0.5))]
                for q in range(int((s1 - s0) / 0.25)): u = s0 + 0.1 + 0.25 * q; it.append(('box', u, u + 0.06, z + 0.05, z + 1.0, -1.84, -1.78, M('#2f3336', 0.5)))
                kwin(it, s0 + 0.4, s0 + 1.3, z + 0.1, z + 2.5, BG, panes=1, sill=False, dd=-3.5); kwin(it, s0 + 1.6, s1 - 0.3, z + 0.9, z + 2.5, BG, panes=2, sill=False, dd=-3.5)
    it.append(('box', 22.3, 29.2, 0.0, 17.6, -3.55, -3.5, BG))                               # back wall of the bay (no LoD2 here)
    it.append(('box', 25.7, 25.8, 0.0, 17.6, -3.5, -1.7, BG))                                # fin between the two balconies
    it.append(('box', 22.3, 29.2, 17.6, 17.9, -3.55, -1.7, M('#3a3e42', 0.5)))               # roof edge
    for q in range(9):                                                                         # stair under the west balcony, rising inwards (north) to a door
        it.append(('box', 22.4, 25.6, 0.0, 0.17 * (q + 1), -0.3 - 0.3 * (q + 1), -0.3 - 0.3 * q, M('#9a9b98', 0.6)))
    it += [('box', 22.4, 25.6, 0.0, 1.53, -3.5, -3.0, M('#9a9b98', 0.6)), ('box', 25.55, 25.6, 1.0, 2.6, -3.3, -0.3, fr)]   # landing, rail
    it += [('box', 23.3, 24.7, 1.53, 3.8, -3.5, -3.47, dk)]                                   # door at the top of the stair
    it += [('box', 26.6, 28.4, 0.0, 2.5, -3.5, -3.46, GLASS_SKY), ('box', 26.5, 28.5, 2.5, 2.6, -3.5, -3.44, fr), ('box', 27.48, 27.52, 0.0, 2.5, -3.46, -3.44, fr)]   # entrance under the east balcony
    return facade_bits((-412.8, 329.6), (-391.7, 324.4), it)
SPECK[1458] = dict(_S58[0], runalt=_ra58, splitruns=True, extra=[_x58()])
SPECK[1517] = dict(spec_for(1517)); SPECK[1517]['extra'] = [facade_bits((-456.9, 392.0), (-463.1, 365.4), _glazed_stack(24.0, 27.3) + _glazed_stack(17.4, 21.0))]   # Katariinankatu 4 (Street View 17.11.2026): two stacks of glazed balconies on the Katariinankatu side, one at the SW corner; floors 1-7
_l17 = dict(SPECK[1517]['layout']); _l17['cols'] = lambda c, nb: 'B' if c < 3 else 'W'; _l17['P'] = dict(_l17.get('P', {}), rail=M('#b7c4c6', 0.35), ldepth=1.6)
SPECK[1517]['walls'] = {1: _l17}   # owner 17.11: the east half of the north side is all glazed loggias, only brick piers between them
SPECK[1553] = classic_spec(1553, wall='#e9e8e3', trim='#e9e8e3', rust=False, garch=False, hood=None, pil=False, bw=4.0,
                           lay=dict(nf=1, frieze=1.0, cols=lambda c, nb: 'S'), ground=dict(plinth_h=0.3, basement=False), yard_same=True)
SPECK[1553]['alt'] = lambda x, y: _blankw if y > 191.5 else None   # its tall back wall (part of the white house over it) is blank
# on Valtakatu: shopfronts under a white fascia (SV 2026, 17.11)
SPEC[1603] = dict(SPEC[1603]); SPEC[1603]['layout'] = lay(21, 'ribbon', gh=4.6, bw=3.0, fh=3.35, P=_V5P); SPEC[1603]['fit'] = lambda lay_, H, street: lay(H, 'ribbon', gh=4.6 if H > 6 else 0, bw=3.0, fh=3.35, P=_V5P)
_H6P = dict(sill=0.85, wh=1.45, nx=3, frame=M('#3a3d40', 0.4, 0.4))
SPEC[1579] = dict(P=dict(wall=M('#e2ddcf', 0.8), spandrel=M('#c8c5bd', 0.7), sign=SIGNS, gwall=M('#3b3e41', 0.5), fascia=M('#d9d3c3', 0.8), gframe=ALU),
                  layout=lay(20, 'ribbon', gh=4.6, bw=3.0, fh=3.2, P=_H6P), fit=lambda lay_, H, street: lay(H, 'ribbon', gh=4.6 if H > 6 else 0, bw=3.0, fh=3.2, P=_H6P))   # pale buff brick, window bands with light panels, dark open ground floor
cut_walls(1579, (100.6, 317.3), (0.974, -0.227))   # split the Hallituskatu wall where the tall house really ends (the yard passage begins)
def _hand_over(src, dst, strip, moves):
    """give a strip of building src's LoD2 shell to building dst: src's walls/roofs there are dropped, dst's corner points move out to the new end
    (owner 16.11.2026: the yellow 1578 runs on to Hallituskatu 6 and must look the same all the way)"""
    from shapely.geometry import Polygon as _P, Point as _Pt
    S = _P(strip).buffer(0.3)
    out = []
    for k, r, h in RAW.get(src, []):
        c = _Pt(sum(q[0] for q in r) / len(r), sum(q[1] for q in r) / len(r))
        if k in ('W', 'R') and S.contains(c): continue
        if k == 'G':
            d = _P([(q[0], q[1]) for q in r]).buffer(0).difference(_P(strip).buffer(0))
            if d.geom_type == 'Polygon' and d.area > 1: r = [(x, y, 0.0) for x, y in list(d.exterior.coords)[:-1]]
        out.append((k, r, h))
    RAW[src] = out
    def mv(q):
        for (ax, ay), (bx, by) in moves:
            if math.hypot(q[0] - ax, q[1] - ay) < 0.4: return (bx, by, q[2])
        return q
    RAW[dst] = [(k, [mv(q) for q in r], h) for k, r, h in RAW.get(dst, [])]
_hand_over(1579, 1578, [(91.8, 306.4), (98.6, 304.8), (100.6, 317.3), (94.4, 318.8)], [((94.4, 318.8), (100.6, 317.3)), ((91.8, 306.4), (98.6, 304.8))])
_H6X = facade_bits((148.0, 306.3), (94.4, 318.8), [('box', 15.0, 46.5, 0.4, 5.3, 0.0, 0.06, M('#34383b', 0.6)), ('box', 15.25, 15.75, 0.4, 5.3, 0.06, 0.5, MT('#eeece6', 'plaster')), ('box', 21.25, 21.75, 0.4, 5.3, 0.06, 0.5, MT('#eeece6', 'plaster')), ('box', 27.25, 27.75, 0.4, 5.3, 0.06, 0.5, MT('#eeece6', 'plaster')), ('box', 33.25, 33.75, 0.4, 5.3, 0.06, 0.5, MT('#eeece6', 'plaster')), ('box', 39.25, 39.75, 0.4, 5.3, 0.06, 0.5, MT('#eeece6', 'plaster')), ('box', 45.25, 45.75, 0.4, 5.3, 0.06, 0.5, MT('#eeece6', 'plaster')), ('box', 45.75, 46.25, 0.4, 5.3, 0.06, 0.5, MT('#eeece6', 'plaster'))])   # owner 16.11: shop front only at the east end; the rest of the ground floor is open behind white columns (garage gates); yard passage at the west end
SPECK_X1581 = facade_bits((40.3, 236.6), (37.2, 223.2), [('box', -0.3, 14.0, 6.6, 25.8, 0.0, 0.12, M('#86a19f', 0.3, 0.15)), ('box', 10.4, 15.2, 6.90, 7.10, 0.0, 1.55, M('#1d1f21', 0.4)), ('box', 10.4, 15.2, 7.10, 9.45, 1.45, 1.55, M('#3c4a52', 0.12, 0.3)), ('box', 10.4, 10.5, 7.10, 9.45, 0.0, 1.55, M('#3c4a52', 0.12, 0.3)), ('box', 10.4, 15.2, 9.45, 9.85, 1.43, 1.57, M('#1d1f21', 0.4)), ('box', 10.4, 15.2, 7.95, 8.02, 1.43, 1.57, M('#1d1f21', 0.4)), ('box', 10.4, 15.2, 9.85, 10.05, 0.0, 1.55, M('#1d1f21', 0.4)), ('box', 10.4, 15.2, 10.05, 12.40, 1.45, 1.55, M('#3c4a52', 0.12, 0.3)), ('box', 10.4, 10.5, 10.05, 12.40, 0.0, 1.55, M('#3c4a52', 0.12, 0.3)), ('box', 10.4, 15.2, 12.40, 12.80, 1.43, 1.57, M('#1d1f21', 0.4)), ('box', 10.4, 15.2, 10.90, 10.97, 1.43, 1.57, M('#1d1f21', 0.4)), ('box', 10.4, 15.2, 12.80, 13.00, 0.0, 1.55, M('#1d1f21', 0.4)), ('box', 10.4, 15.2, 13.00, 15.35, 1.45, 1.55, M('#3c4a52', 0.12, 0.3)), ('box', 10.4, 10.5, 13.00, 15.35, 0.0, 1.55, M('#3c4a52', 0.12, 0.3)), ('box', 10.4, 15.2, 15.35, 15.75, 1.43, 1.57, M('#1d1f21', 0.4)), ('box', 10.4, 15.2, 13.85, 13.92, 1.43, 1.57, M('#1d1f21', 0.4)), ('box', 10.4, 15.2, 15.75, 15.95, 0.0, 1.55, M('#1d1f21', 0.4)), ('box', 10.4, 15.2, 15.95, 18.30, 1.45, 1.55, M('#3c4a52', 0.12, 0.3)), ('box', 10.4, 10.5, 15.95, 18.30, 0.0, 1.55, M('#3c4a52', 0.12, 0.3)), ('box', 10.4, 15.2, 18.30, 18.70, 1.43, 1.57, M('#1d1f21', 0.4)), ('box', 10.4, 15.2, 16.80, 16.87, 1.43, 1.57, M('#1d1f21', 0.4)), ('box', 10.4, 15.2, 18.70, 18.90, 0.0, 1.55, M('#1d1f21', 0.4)), ('box', 10.4, 15.2, 18.90, 21.25, 1.45, 1.55, M('#3c4a52', 0.12, 0.3)), ('box', 10.4, 10.5, 18.90, 21.25, 0.0, 1.55, M('#3c4a52', 0.12, 0.3)), ('box', 10.4, 15.2, 21.25, 21.65, 1.43, 1.57, M('#1d1f21', 0.4)), ('box', 10.4, 15.2, 19.75, 19.82, 1.43, 1.57, M('#1d1f21', 0.4)), ('box', 10.4, 15.2, 21.65, 21.85, 0.0, 1.55, M('#1d1f21', 0.4)), ('box', 10.4, 15.2, 21.85, 24.20, 1.45, 1.55, M('#3c4a52', 0.12, 0.3)), ('box', 10.4, 10.5, 21.85, 24.20, 0.0, 1.55, M('#3c4a52', 0.12, 0.3)), ('box', 10.4, 15.2, 24.20, 24.60, 1.43, 1.57, M('#1d1f21', 0.4)), ('box', 10.4, 15.2, 22.70, 22.77, 1.43, 1.57, M('#1d1f21', 0.4)), ('box', 0.15, 0.65, 1.6, 6.6, 0.25, 0.75, MT('#f1efe9', 'plaster')), ('box', 9.95, 10.45, 1.6, 6.6, 0.25, 0.75, MT('#f1efe9', 'plaster')), ('box', 13.35, 13.85, 1.6, 6.6, 0.25, 0.75, MT('#f1efe9', 'plaster'))])   # owner 16.11: tower face = copper-green ceramic tile, no windows; glazed corner balconies stacked at the south end; white pilotis under it
_V80P = dict(sill=0.8, wh=1.75, nx=4, frame=M('#2f3436', 0.4, 0.4))
SPEC[1580] = dict(P=dict(wall=M('#3e544e', 0.6), spandrel=M('#e9e7e0'), sign=SIGNS, gwall=M('#3e544e', 0.6), fascia=M('#e9e7e0'), gframe=ALU),
                  layout=lay(7.7, 'ribbon', gh=3.8, bw=3.0, fh=3.9, P=_V80P), fit=lambda lay_, H, street: lay(H, 'ribbon', gh=3.8, bw=3.0, fh=3.9, P=_V80P))   # Antinkatu 1960s house: dark green panels, a white ribbon-window band upstairs
cut_walls(1604, (43.7, 268.0), (0.228, 0.973))   # 1604's LoD2 shell runs on over the low 1960s house 1580 south of it (SV 2026, 16.11)
SPECK[1604] = classic_spec(1604, trim='#b0603f', rust=False, garch=False, hood='cornice', pil=False, top=dict(hood='cornice'),
                           lay=dict(cols=lambda c, nb: 'G' if c == 0 else 'D' if c == 1 else 'W'))   # yellow Jugend house on Antinkatu: brick-red lintels on every floor; wooden yard gate in the north bay, entrance next to it (Street View 2026, 16.11)
SPECK[1604]['extra'] = [facade_bits((51.8, 302.6), (39.0, 248.0), [('gable', 1.9, 4.6, 14.4, 3.2, MT('#ead9a6', 'plaster'), 3),   # north risalit with its stepped gable
                                                                   ('spire', 1.9, 1.6, 17.0, 21.5, M('#4a4f53', 0.5, 0.2)),                # and the pointed turret roof on it
                                                                   ('gable', 16.0, 4.0, 14.4, 2.2, MT('#ead9a6', 'plaster'), 1), ('spire', 16.0, 1.4, 16.2, 20.2, M('#4a4f53', 0.5, 0.2))]),
                        facade_bits((39.0, 248.0), (51.5, 245.0), [('box', -0.05, 12.85, -0.5, 8.2, 0.0, 0.1, M('#3e544e', 0.6))])]   # owner 16.11: the south end of the 1960s house 1580 is a blank dark-green panel wall, no windows   # second turret mid-facade
RAW[1576] = [(k, [(q[0], q[1], 6.3 if 5.5 < q[2] < 7.4 else q[2]) for q in r], h) for k, r, h in RAW.get(1576, [])]   # the scan's eave wobbles 6.0-7.0 m: a strip of red wall stood above the cornice (owner 15.11.2026). One eave at 6.3 m.
cut_walls(1284, (-170.4, 407.5), (0.204, 0.981))     # Heinen talo: the two street walls are cut 2.4 m from the corner; the round corner bay
cut_walls(1284, (-173.3, 405.5), (-0.986, 0.168))    # stands there, so those stretches stay blank (owner 15.11.2026: windows and clutter behind the tower)
_b1284 = classic_spec(1284, wall='#e4dcc6', trim='#f3eee2', rust=True, garch=False, hood=None, pil=False, lay=dict(cols=lambda c, nb: 'N'))
_b1284['yard'] = _b1284['layout']
SPECK[1284] = classic_spec(1284, wall='#e4dcc6', trim='#f3eee2', rust=True, garch=True, hood='pediment', pil=False,
                           extra=[round_corner(-171.5, 405.9, 2.0, 13.2, math.atan2(-0.827, 0.563), M('#e9e1cb'), M('#f5f1e6'), M('#8d8a84', 0.85), M('#2e3337', 0.45, 0.4))])   # Heinen talo / seurakuntatoimisto: banded rustication on the ground floor, arched ground-floor windows, pedimented upper windows (Street View 14.11.2026)
SPECK[1284]['alt'] = lambda x, y: _b1284 if math.hypot(x + 170.9, y - 405.1) < 2.6 else None
SPECK[1513] = classic_spec(1513, wall='#9b4b36', trim='#b9654c', rust=False, garch=True, hood=None, pil=True, bw=4.6, cornice=(0.3, 0.7, M('#7f3d2c')))   # brewery remnant
SPECK[1281] = classic_spec(1281, wall='#e2dcbc', trim='#f4f1e8', rust=False, garch=False, hood='cornice', pil=True)   # Eteläranta 10: pale yellow render, white pilasters, window surrounds and cornice (Street View 14.11.2026)
_t1281 = classic_spec(1281, wall='#e8e0bf', trim='#f6f3ea', rust=False, garch=False, hood='cornice', pil=False, bw=3.3,
                      lay=dict(nf=2, gh=5.8, cols=lambda c, nb: 'W'), ground=dict(plinth_h=1.6, basement=False, sill=0.6, wh=1.8, ww=1.15, wh_fixed=True), first=dict(ww=1.1, wh=1.7, sill=0.9, wh_fixed=True), yard_same=True)
SPECK[1281]['alt'] = lambda x, y: _t1281 if y < 466.5 else None   # Teatterikatu side (SV 2026, 17.11): two rows of framed windows over a high base, not three storeys
SPECK[1285] = classic_spec(1285, wall='#e8ddb6', trim='#f6f4ee', rust=False, garch=True, hood='cornice', pil=True, lay=dict(nf=2, gh=6.4, frieze=1.4, cols=lambda c, nb: 'W'), ground=dict(plinth_h=1.9), top=dict(blank=True))   # wireframe 14.11.2026: high plinth with cellar windows, ground 4.5 m, first 4.8 m, plain frieze 1.4 m under the cornice   # Eteläranta / S. Palmgreninkatu: very light cream, TWO storeys, arched ground-floor windows (owner + Street View 14.11.2026); chamfered corner with a balcony not modelled yet
_c1285 = classic_spec(1285, wall='#e8ddb6', trim='#f6f4ee', rust=False, garch=True, hood='cornice', pil=False, bw=2.2, lay=dict(nf=2, gh=6.4, frieze=1.4, cols=lambda c, nb: 'D'), ground=dict(plinth_h=1.9), top=dict(blank=True),
                      first=dict(balcony=True, hood='cornice'))
_w1285 = classic_spec(1285, wall='#e8ddb6', trim='#f6f4ee', rust=False, garch=True, hood='cornice', pil=True, bw=2.9, lay=dict(nf=2, gh=6.4, frieze=1.4, cols=lambda c, nb: 'W'), ground=dict(plinth_h=0.8, basement=False), top=dict(blank=True))   # S. Palmgreninkatu side: the street is higher, a low plinth (wireframe 14.11.2026)
SPECK[1285]['alt'] = lambda x, y: _c1285 if -39.6 < x < -36.5 and 457.8 < y < 460.2 else _w1285 if x < -39.5 and y < 457.0 else None   # the corner chamfer: door below, balcony above (block walk 14.11.2026)
# 3 Antinkatu / 10 Hallituskatu (block walk 14.11.2026): the whole Antinkatu front is white, the Hallituskatu front yellow
_w1563 = classic_spec(1563, wall='#e6cf8f', trim='#f4f1e8', rust=False, garch=False, hood='cornice', pil=False, lay=dict(nf=2, frieze=0.9, cols=lambda c, nb: 'W'), ground=dict(plinth_h=0.6, plinth=GRANITE), top=dict(ww=0.6, wh=0.3, sill=0.3, hood=None, pil=False, wh_fixed=True))   # 3 Antinkatu (wireframe 14.11.2026): grey plinth (the ochre patch on the wall is paint), no street door, small vents under the eave
SPECK[1576] = classic_spec(1576, wall='#a5513d', trim='#ece6da', rust=False, garch=False, hood=None, pil=False, bw=3.3,
                           lay=dict(nf=1, frieze=0.9, cols=lambda c, nb: 'W' if c % 2 == 0 else 'Y'), ground=dict(plinth_h=0.7, plinth=M('#7e3d2e', 0.85), basement=False, ww=1.15, wh=1.85, sband=0),
                           attic=dict(ww=0.45, wh=0.25, sill=0.35, hood=None, pil=False, wh_fixed=True))   # Hallituskatu south side: brick-red RENDERED one-storey house (owner 15.11.2026: rapattu, ei tiili), five windows in white surrounds, three small vents under the white cornice (Street View 15.11.2026)
SPECK[1576]['roofmat'] = M('#3d4247', 0.55, 0.2); SPECK[1576]['nobrick'] = True; SPECK[1576]['P']['wall'] = MT('#a5513d', 'plaster')   # owner 15.11.2026: rendered, not brick (the bake and the game would read this red as brick)
SPECK[1576]['extra'] = [facade_bits((23.5, 335.0), (7.3, 339.0), [('chimney', 8.0, 2.6, 6.0, 8.8, 0.6, M('#3b3634')), ('chimney', 11.9, 2.6, 6.0, 8.8, 0.6, M('#3b3634'))]),
                        facade_bits((23.5, 335.0), (7.3, 339.0), [('vents', 1.7, 1, 4.95, None, 0.5, 0.22), ('vents', 8.35, 1, 4.95, None, 0.5, 0.22), ('vents', 15.0, 1, 4.95, None, 0.5, 0.22)]),
                        facade_bits((7.3, 339.0), (-43.7, 351.7), [('wall', 0.2, 51.6, -0.6, 2.3, 0.45, MT('#d8d3c7', 'plaster'))])]   # owner 15.11.2026: the free-standing light rendered garden wall along Hallituskatu between this house and the Kaupungintalo
SPECK[1563] = classic_spec(1563, wall='#e6cf8f', trim='#f4f1e8', rust=False, garch=False, hood='cornice', pil=False, bw=2.7, lay=dict(nf=2, frieze=1.2, cols=lambda c, nb: 'D' if c == 0 else 'N' if c == 3 else 'W'), attic=dict(ww=0.6, wh=0.3, sill=0.45, hood=None, pil=False, wh_fixed=True))   # 10 Hallituskatu (wireframe 14.11.2026): five bays, door with a dressed surround at the west end, blind 4th bay, vents in the frieze
SPECK[1563]['alt'] = lambda x, y: _w1563 if x > 44.0 else None
SPECK[1447] = classic_spec(1447, wall='#8e4a3c', trim='#e6dccb', rust=False, garch=True, hood=None, pil=True, bw=3.8, first=dict(arch=True), top=dict(arch=True))   # old red-brick building at Eteläranta/Karhu: round-arched windows with light surrounds, brick pilasters (was a plain modern box; Street View 14.11.2026)
def _s1575(bw):
    return classic_spec(1575, wall='#e6d29c', trim='#f4f1e8', rust=False, garch=True, hood='cornice', pil=True, bw=bw,
                        lay=dict(nf=2, frieze=1.1, cols=lambda c, nb: 'W'), ground=dict(plinth_h=0.55, basement=False, ww=1.85, wh=2.95, sill=0.15, wh_fixed=True),
                        attic=dict(ww=0.55, wh=0.3, sill=0.4, hood=None, pil=False, wh_fixed=True))
SPECK[1575] = _s1575(3.07)   # 5 Antinkatu / Hallituskatu corner (wireframe 15.11.2026): eight bays on Antinkatu, NO door there; big round-arched shop windows from just above the low brick-red plinth, framed windows with cornices above, a small attic window over every bay
_h1575 = _s1575(3.6)         # Hallituskatu end: three bays
_b1575 = classic_spec(1575, wall='#e6d29c', trim='#f4f1e8', rust=False, garch=False, hood=None, pil=False, bw=3.0,
                     lay=dict(nf=1, cols=lambda c, nb: 'N'), ground=dict(plinth_h=0.55, basement=False, blank=True, sband=0, rust=False), yard_same=True)
SPECK[1575]['alt'] = lambda x, y: _h1575 if y > 331.0 else _b1575 if y < 311.0 else None
SPECK[1575]['extra'] = [facade_bits((28.8, 333.9), (23.5, 335.0), [('wall', 0.0, 5.4, -0.6, 5.4, 0.5, MT('#f1eee6', 'plaster')), ('archgate', 2.9, 3.4, 3.1, MT('#ece3c4', 'wood'))]),
                        facade_bits((34.7, 307.3), (40.1, 331.4), [('vents', 1.54, 1, 8.95, None, 0.55, 0.3), ('vents', 4.61, 1, 8.95, None, 0.55, 0.3), ('vents', 7.69, 1, 8.95, None, 0.55, 0.3), ('vents', 10.76, 1, 8.95, None, 0.55, 0.3), ('vents', 13.84, 1, 8.95, None, 0.55, 0.3), ('vents', 16.91, 1, 8.95, None, 0.55, 0.3), ('vents', 19.99, 1, 8.95, None, 0.55, 0.3), ('vents', 23.06, 1, 8.95, None, 0.55, 0.3)]), facade_bits((40.1, 331.4), (28.8, 333.9), [('vents', 1.93, 1, 8.95, None, 0.55, 0.3), ('vents', 5.80, 1, 8.95, None, 0.55, 0.3), ('vents', 9.67, 1, 8.95, None, 0.55, 0.3)])]   # small attic windows in the frieze over every bay   # white arched gateway to the yard between 1575 and 1576 (Street View 15.11.2026)
SPECK[1575].setdefault('extra', []).append(facade_bits((23.2, 309.9), (34.7, 307.3), [('band', 0.0, 11.8, 8.9, 9.25, 0.2, M('#f4f1e8')), ('brackets', 0.6, 11.2, 9.25, M('#f4f1e8'))]))   # only the ornamental eave cornice on that blank end (owner 16.11)   # owner 16.11: its south end wall over the garden is blank (no windows), only the cornice runs round   # Hallituskatu end: three bays
SPECK[1572] = classic_spec(1572, wall='#c9b07a', trim='#efe9da', rust=True, garch=False, hood=None, pil=False, bw=2.8, lay=dict(nf=2, cols=lambda c, nb: 'D' if c == 8 else 'Y' if c == 3 else 'W'),   # 'Y': no wall window upstairs behind the oriel (owner 15.11.2026)
                          
                           ground=dict(plinth_h=0.8, plinth=M('#8f8a80', 0.85), basement=False, rustc=M('#b39c68'), sband=0.3, darch=True, dw=1.6, door=M('#2b241e', 0.6)), first=dict(ww=1.2, sband=0))   # 8 Hallituskatu (owner photos 15.11.2026): buff rendered Jugend house, ashlar-lined ground floor, white dentil band, pointed-arch entrance under the east gable
SPECK[1572]['P']['frame'] = M('#2e3a33', 0.5)   # owner 15.11.2026: rendered, not brick
_b1572 = M('#c9b07a')
_w1572 = M('#f2efe6')
def cross_gable(i, p0, p1, s0, w, z_e, z_r, depth):
    """a cross gable in the scanned roof: the gable on the wall p0->p1 at s0 (width w) gets two roof planes from its eave corners
    up to a ridge that runs back from its peak to the main ridge (owner 15.11.2026: the roof rises with the gables)"""
    L0 = math.hypot(p1[0] - p0[0], p1[1] - p0[1]); t = ((p1[0] - p0[0]) / L0, (p1[1] - p0[1]) / L0); inw = (-t[1], t[0])
    F = lambda s_: (p0[0] + t[0] * s_, p0[1] + t[1] * s_)
    a, c, m = F(s0 - w / 2), F(s0 + w / 2), F(s0); r = (m[0] + inw[0] * depth, m[1] + inw[1] * depth)
    RAW[i] = RAW[i] + [('R', [(a[0], a[1], z_e), (m[0], m[1], z_r), (r[0], r[1], z_r)], None), ('R', [(m[0], m[1], z_r), (c[0], c[1], z_e), (r[0], r[1], z_r)], None)]
for _s in (9.9, 23.6): cross_gable(1572, (64.2, 347.6), (94.2, 340.4), _s, 5.0, 11.1, 14.6, 6.65)
SPECK[1572].pop('cornice', None)   # the eave cornice is drawn in pieces between the gables (facade_bits 'band'), the wall runs up into the gables (owner 15.11.2026)
SPECK[1572]['extra'] = [facade_bits((64.2, 347.6), (94.2, 340.4), [('gable', 9.9, 5.0, 11.1, 3.5, _b1572, 1), ('gable', 23.6, 5.0, 11.1, 3.5, _b1572, 1),
                                                                     ('vents', 9.9, 2, 12.0, _b1572), ('vents', 23.6, 4, 11.6, _b1572),
                                                                     ('band', 0.0, 7.4, 10.75, 11.15, 0.45, _w1572), ('band', 12.4, 21.1, 10.75, 11.15, 0.45, _w1572), ('band', 26.1, 30.9, 10.75, 11.15, 0.45, _w1572),
                                                                     ('brackets', 0.6, 7.2, 11.0, _w1572), ('brackets', 12.6, 20.9, 11.0, _w1572), ('brackets', 26.3, 30.3, 11.0, _w1572),
                                                                     ('orielv', 9.9, 2.6, 6.6, 10.7, 1.1, _b1572)])]   # triangular oriel in the middle of the west gable, windows in both sides, roof sloping back into the wall (owner 15.11.2026)   # small plain gables and an upper-floor oriel that runs into the eave, all in the wall render   # stepped gables and the white oriel on Hallituskatu (Street View 15.11.2026)
SPECK[1571] = classic_spec(1571, wall='#d9d7cd', trim='#efeee8', rust=False, garch=False, hood='cornice', pil=False, lay=dict(nf=2, cols=lambda c, nb: 'D' if c == nb // 2 else 'W'),
                           ground=dict(plinth_h=0.5, basement=False, sill=0.6, wh=2.2, wh_fixed=True))   # 3 Hallituskatu: pale grey render, two storeys, cornices over the windows, door in the middle (Street View 15.11.2026)
SPECK[8385] = classic_spec(8385, wall='#d8b660', trim='#efe6c8', rust=False, garch=False, hood='pediment', pil=True, lay=dict(nf=2, cols=lambda c, nb: 'D' if c == nb // 2 + 1 else 'W'),
                           ground=dict(plinth_h=0.3, basement=False, ww=2.0, wh=2.5, sill=0.15, wh_fixed=True, frame=M('#6e2b22', 0.5), door=M('#6e2b22', 0.5), door_z=0.05), first=dict(hood='pediment'))   # Yrjönkatu / Hallituskatu: yellow, pediments over the upper windows, tall shop windows with dark red frames at street level (Street View 15.11.2026)
SPECK[1568] = classic_spec(1568, wall='#e2c77a', trim='#f2ecd8', rust=False, garch=False, hood='pediment', pil=True, lay=dict(nf=2, cols=lambda c, nb: 'D' if c == 2 else 'W'),
                           ground=dict(plinth_h=0.3, basement=False, ww=1.6, wh=2.4, sill=0.3, wh_fixed=True, door_z=0.05), first=dict(hood='pediment'))   # 3 Yrjönkatu (Eteläranta corner): yellow, pediments, large ground-floor windows, door at street level in the 3rd bay
_c1568 = classic_spec(1568, wall='#e2c77a', trim='#f2ecd8', rust=False, garch=False, hood='pediment', pil=False, bw=2.4, lay=dict(nf=2, cols=lambda c, nb: 'D'),
                      ground=dict(plinth_h=0.3, basement=False, door_z=0.05), first=dict(hood='pediment'))   # the 45-degree corner towards Eteläranta: door below, window above (owner 15.11.2026)
SPECK[1561] = classic_spec(1561, wall='#efede6', trim='#f7f6f1', rust=False, garch=False, hood=None, pil=False, lay=dict(nf=1))   # 2 Antinkatu: low white one-storey house (block walk 14.11.2026)
SPECK[1562] = classic_spec(1562, wall='#efede6', trim='#f7f6f1', rust=False, garch=False, hood='cornice', pil=False, lay=dict(nf=1, frieze=1.4), ground=dict(plinth_h=1.6), top=dict(blank=True))   # white ONE-storey house on a high plinth, plain wall up to the eave (wireframe on Street View 14.11.2026, owner: 'yksitasoinen, korkea kivijalka')
cut_walls(1566, (70.8, 383.4), (0.2297, 0.9738))   # 4 Antinkatu (1573) is the south end of 1566's long Antinkatu wall: cut where its footprint ends
lower_eave(1566, lambda r: all(q[1] < 383.6 and q[0] < 72.0 for q in r) and min(q[2] for q in r) < 0.5 and max(q[1] for q in r) - min(q[1] for q in r) > 10, 5.6, 15.0)   # one storey and an attic frieze under the eave (owner 14.11.2026)
def _low_strip(i, j, zc, extra=None):
    """the low house j stands inside building i's LoD2 shell: walls of i over j's footprint are cut to zc(x, y), i's roofs are clipped
    away there and j gets its own low roof (owner 15./16.11.2026: the 1566 roof floated over a black open box above 4 Antinkatu, 1573)"""
    from shapely.geometry import Polygon as _P, Point as _Pt
    import numpy as _np
    if j is None: F0 = _P(extra).buffer(0)
    else:
        p = B[j]['p']; F0 = _P([(p[k] / 10, p[k + 1] / 10) for k in range(0, len(p), 2)]).buffer(0)
        if extra: F0 = F0.union(_P(extra).buffer(0))          # e.g. the shell's sliver over a gate passage next to j
    F = F0.buffer(0.6)
    zf = zc if callable(zc) else (lambda x, y: zc)
    out = []
    for k, r, h in RAW.get(i, []):
        cx, cy = sum(q[0] for q in r) / len(r), sum(q[1] for q in r) / len(r)
        if k == 'W':
            if F.contains(_Pt(cx, cy)): r = [(q[0], q[1], zf(q[0], q[1]) if q[2] > 3.0 else q[2]) for q in r]
            out.append((k, r, h)); continue
        if k == 'R':
            g = _P([(q[0], q[1]) for q in r]).buffer(0)
            if g.is_empty or not g.intersects(F0): out.append((k, r, h)); continue
            A = _np.array([[q[0], q[1], 1.0] for q in r]); z = _np.array([q[2] for q in r]); c_ = _np.linalg.lstsq(A, z, rcond=None)[0]   # roof plane
            d = g.difference(F0)
            for gg in ([d] if d.geom_type == 'Polygon' else list(getattr(d, 'geoms', []))):
                if gg.geom_type == 'Polygon' and gg.area > 0.5:
                    out.append((k, [(x, y, float(c_[0] * x + c_[1] * y + c_[2])) for x, y in list(gg.exterior.coords)[:-1]], None))
            continue
        out.append((k, r, h))
    RAW[i] = out
    G = [_P([(q[0], q[1]) for q in r]).buffer(0) for k, r, _ in RAW[i] if k == 'G' and len(r) >= 3]
    cap = G[0].intersection(F0) if G else None
    for g in ([cap] if cap is not None and cap.geom_type == 'Polygon' else list(getattr(cap, 'geoms', []))):
        if g.area > 4: RAW[i].append(('R', [(x, y, zf(x, y)) for x, y in list(g.exterior.coords)[:-1]], None))

SPECK[1573] = classic_spec(1573, wall='#e9d6a0', trim='#f4f1e8', rust=False, garch=False, hood=None, pil=False, bw=3.08,
                           lay=dict(nf=1, frieze=2.0, cols=lambda c, nb: 'D' if c == 2 else 'N' if c == nb - 1 else 'W'),   # 16.11: W W D W W; the last (south) bay lies behind the gateway
                           ground=dict(plinth_h=1.0, plinth=M('#a7a49c', 0.85), sill=0.8, wh=2.6, ww=1.3, wh_fixed=True, dw=1.0, door=M('#c9ccc6', 0.4)), first=dict(hood=None),
                           attic=dict(ww=0.9, wh=0.42, sill=0.6, hood=None, pil=False, wh_fixed=True))   # 4 Antinkatu (wireframe on SV 2026, 16.11): high grey plinth, eave ~6.9 m above the street, small double attic windows in a tall frieze
SPECK[1566] = classic_spec(1566, wall='#e3dfcf', trim='#efece2', rust=True, garch=False, hood='cornice', pil=True, bw=3.6,
                           ground=dict(hood='cornice', basement=False, plinth_h=1.1, plinth=M('#8d8c87', 0.85), rustc=M('#c9c4b3')),
                           top=dict(ww=0.9, wh=0.45, sill=0.35, hood=None), lay=dict(nf=2, frieze=1.1, cols=lambda c, nb: 'W'), roofmat=M('#4b5552', 0.5, 0.3))
_e1566 = classic_spec(1566, wall='#e3dfcf', trim='#efece2', rust=True, garch=False, hood='cornice', pil=True, bw=3.6,
                      ground=dict(hood='cornice', basement=False, plinth_h=1.1, plinth=M('#8d8c87', 0.85), rustc=M('#c9c4b3')),
                      top=dict(ww=0.9, wh=0.45, sill=0.35, hood=None), lay=dict(nf=2, frieze=1.1, cols=lambda c, nb: 'G' if c == 1 else 'W'), roofmat=M('#4b5552', 0.5, 0.3))   # Eteläranta front: arched gateway in the second bay from the east, no street door (wireframe 15.11.2026)
SPECK[1566]['alt'] = lambda x, y: _e1566 if y > 418.0 and x > 85.0 else None
_gate1573 = facade_bits((66.13, 367.04), (64.50, 359.74), [   # white gateway between 4 Antinkatu and 1572 (SV 2026), 7.5 m, set 0.6 m in front of the house line so it covers the shell's south end
    ('wall', 0.0, 7.48, -0.6, 5.0, 0.6, MT('#f2efe6', 'plaster')), ('band', 0.0, 7.48, -0.6, 0.45, 0.06, M('#b9b6ae', 0.85)),
    ('irongate', 3.05, 3.6, 2.9), ('archgate', 6.45, 0.85, 2.0, M('#2a2b2c', 0.5)),
    ('band', 0.35, 0.85, 0.45, 4.6, 0.14, MT('#f2efe6', 'plaster')), ('band', 5.0, 5.5, 0.45, 4.6, 0.14, MT('#f2efe6', 'plaster')), ('band', 7.0, 7.48, 0.45, 4.6, 0.14, MT('#f2efe6', 'plaster')),   # pilasters
    ('band', -0.1, 7.58, 4.6, 5.0, 0.3, M('#f7f5ef')),                                                                       # cornice
    ('gable', 3.05, 4.6, 5.0, 0.85, MT('#f2efe6', 'plaster'), 1)])   # drawn with 1566 (4 Antinkatu is a stretch of 1566's shell, its own extras never run)
SPECK[1566].setdefault('extra', []).append(_gate1573)
# Eteläranta 4 / Antinkatu 2 (owner photo 14.11.2026): pale cream render, two storeys, block-rusticated ground floor, straight cornices
# over every window, a strong string course, rusticated corners, small attic windows in the frieze, grey stone plinth, dark sheet roof;
# a gateway at the Antinkatu end (not modelled)
SPECK[1569] = dict(P=dict(wall=M('#dedcd5'), spandrel=M('#dedcd5'), frame=M('#5b3f2c', 0.6), sign=SIGNS), cornice=(0.7, 0.2, M('#2f3437', 0.5)),
                   layout=lay(7.5, 'ribbon', gh=0, bw=1.3, fh=3.4))   # Antinkatu, mid-20th-century infill (owner photo 14.11.2026): light grey render, two long window bands with brown wooden frames, dark fascia
squash(1287, 8.5, 0.15)   # (16.11: eave was 1.6 m too high on the wireframe) the scan's walls reach 14-17 m; Street View: 2 storeys + attic frieze, eave about 8 m above the street, low roof (wireframe 14.11.2026)
SPECK[1287] = classic_spec(1287, wall='#e6d9bb', trim='#f6f4ee', rust=True, garch=False, hood='cornice', pil=False, bw=2.7, lay=dict(nf=2, frieze=1.3, cols=lambda c, nb: 'W'), attic=dict(ww=0.6, wh=0.4, sill=0.45, hood=None, pil=False, wh_fixed=True))   # 12 Hallituskatu / 3 S. Palmgreninkatu: pale cream, banded ground floor, cornices over the upper windows, small attic windows, eight bays
_h1287 = classic_spec(1287, wall='#e6d9bb', trim='#f6f4ee', rust=True, garch=False, hood='cornice', pil=False, bw=2.07, lay=dict(nf=2, frieze=1.3, cols=lambda c, nb: 'Y' if c == 1 else 'W'), ground=dict(plinth_h=0.35, basement=False, sill=0.1, wh=2.3, wh_fixed=True), attic=dict(ww=0.6, wh=0.4, sill=0.45, hood=None, pil=False, wh_fixed=True))   # Hallituskatu front: seven narrow bays, the second blind; tall ground-floor windows from just above the pavement, no cellar windows (owner 14.11.2026)
_c1287 = classic_spec(1287, wall='#e6d9bb', trim='#f6f4ee', rust=True, garch=False, hood='cornice', pil=False, bw=4.2, lay=dict(nf=2, frieze=1.3, cols=lambda c, nb: 'D'), ground=dict(plinth_h=0.35, basement=False, dw=1.1), attic=dict(ww=0.6, wh=0.4, sill=0.45, hood=None, pil=False, wh_fixed=True))   # owner 16.11: the corner wall: door with a canopy below, one window above
SPECK[1287]['alt'] = lambda x, y: _c1287 if math.hypot(x + 57.35, y - 377.55) < 1.5 else _h1287 if y < 377.0 else None
SPECK[1287]['extra'] = [facade_bits((-58.5, 379.4), (-56.2, 375.7), [('canopy', 2.15, 1.9, 4.25, 1.1, M('#3d4146', 0.5))])]
_gw = MT('#e8e2cf', 'plaster')
SPECK[1286].setdefault('extra', []).append(facade_bits((-42.0, 372.1), (-27.2, 369.1), [   # yard gate '7' between 1287 (s=0) and 1286 (s=15.1), street face south (owner 15.11.2026, Street View 16.11)
    ('wall', 0.0, 5.0, -0.6, 4.6, 0.5, _gw), ('archgate', 2.4, 1.0, 2.2, MT('#6a5d4c', 'wood')),                 # low cream wing with a door
    ('wall', 5.0, 11.1, -0.6, 6.6, 0.7, _gw), ('archgate', 8.05, 3.6, 3.4, M('#3a3a36', 0.6)),                # big open round arch (passage into the yard)
    ('archgate', 5.55, 0.8, 2.0, MT('#6a5d4c', 'wood')), ('archgate', 10.55, 0.8, 2.0, MT('#6a5d4c', 'wood')),   # small arched doors in the piers
    ('wall', 11.1, 15.1, -0.6, 3.8, 0.4, _gw)]))                                                             # low wall up to 1286
cut_walls(1288, (-47.7, 423.5), (0.2350, 0.9720))   # S. Palmgreninkatu: red 1½-storey house to the south, pale yellow 2-storey house to the north (block walk 14.11.2026)
_n1288 = classic_spec(1288, wall='#e2d6aa', trim='#f4f1e8', rust=False, garch=False, hood='cornice', pil=False, lay=dict(nf=2), ground=dict(ww=1.1, wh=1.5, sill=1.0, wh_fixed=True), first=dict(wh=1.9, wh_fixed=True))   # ground-floor windows lower than the upper ones (owner 15.11.2026)
SPECK[1288] = classic_spec(1288, wall='#c9675f', trim='#f4f1ea', rust=False, garch=False, hood=None, pil=True, bw=2.5, lay=dict(nf=1, cols=lambda c, nb: 'W'))   # red one-storey house: five narrow window bays (wireframe 14.11.2026)
_g1288 = classic_spec(1288, wall='#e2d6aa', trim='#f4f1e8', rust=False, garch=False, hood='cornice', pil=False, lay=dict(nf=2, cols=lambda c, nb: 'N'))   # its north gable towards 1 Eteläranta's gate: blank wall (owner 15.11.2026)
_g1288['yard'] = _g1288['layout']
SPECK[1288]['alt'] = lambda x, y: _g1288 if y > 438.0 and x < -35.5 else _n1288 if y > 423.5 else None
SPECK[1565] = classic_spec(1565, wall='#dcdbe2', trim='#f4f3f2', rust=False, garch=False, hood='cornice', pil=False, bw=2.65, lay=dict(nf=2, frieze=1.2, cols=lambda c, nb: 'W'), top=dict(ww=0.9, wh=0.55, sill=0.4, hood=None))   # 5 Hallituskatu: pale lilac-grey, 2 storeys + small attic windows (block walk 14.11.2026)
SPECK[1559] = classic_spec(1559, wall='#c8764e', trim='#f4f1ea', rust=True, garch=True, hood='cornice', pil=True, bw=4.4, lay=dict(nf=2, gh=4.7, frieze=2.5, cols=lambda c, nb: 'W' if c == nb // 2 else 'D'), ground=dict(gwall=M('#cfcbc1'), rustc=M('#aaa69c'), plinth=M('#8d8a84', 0.85), plinth_h=0.8, ww=1.6, wh=2.5, sill=0.1, wh_fixed=True, dw=1.6, basement=False), first=dict(ww=1.2, wh=2.1, sill=0.5, wh_fixed=True), top=dict(ww=0.8, wh=0.55, sill=0.9, hood=None, pil=False, wh_fixed=True, wall=M('#ece8de')))   # 6 Eteläranta, measured with the wireframe on Street View (owner 14.11.2026: stone ground / orange upper about 50/50): light stone ground floor 4.6 m with arched door, arched window, arched door; terracotta first floor; light attic frieze 1.5 m with three small windows
SPECK[1567] = classic_spec(1567, wall='#dcc27e', trim='#f4f1e8', rust=False, garch=False, hood='cornice', pil=True, lay=dict(nf=3, cols=lambda c, nb: 'D' if c in (1, nb - 2) else 'W'))   # 2 Eteläranta: ochre, 3 storeys, white pilasters (block walk 14.11.2026)
SPECK[1567]['runalt'] = lambda x, y: _c1568 if math.hypot(x - 182.9, y - 408.3) < 1.8 else None   # the corner chamfer cut by styles.json 'ch'
SPECK[1619] = classic_spec(1619, wall='#ece0b4', trim='#f5f2ea', rust=False, garch=False, hood=None, pil=True, bw=3.5, first=dict(arch=True, apron=False, hood=None), top=dict(arch=True), lay=dict(nf=2))   # 4 Hallituskatu / 5 Yrjönkatu: pale yellow, smooth render, round-arched windows upstairs, plain rectangular ground floor, white corner pilasters (Street View 14.11.2026, owner)
# east end on Hallituskatu (owner + Street View 17.11.2026): rectangular windows upstairs in flat white surrounds, ground-floor windows
# under cornice hoods, a strong band between the storeys and a low attic frieze of small horizontal windows under the eave
_e1619 = classic_spec(1619, wall='#ece0b4', trim='#f5f2ea', rust=False, garch=False, hood='cornice', pil=True, bw=3.5,
                      first=dict(arch=False, apron=False, hood=None, sband=0.35), top=dict(arch=False, hood=None),
                      attic=dict(ww=1.2, wh=0.45, sill=0.35, hood=None, wh_fixed=True), lay=dict(nf=2, frieze=1.3, door_mid=False))
SPECK[1619]['runalt'] = lambda x, y: _e1619 if x > 192.0 else None; SPECK[1619]['splitruns'] = True
squash(1454, 8.0, 0.4)   # Teatterikatu 3: a 1½-storey wooden house - the scan stood 9-11 m (SV 2026, 17.11)
SPECK[1454] = classic_spec(1454, trim='#f7f6f1', rust=False, garch=False, hood='pediment', pil=False, bw=3.4,
                           lay=dict(nf=1, frieze=0.9, cols=lambda c, nb: 'W'), ground=dict(hood='pediment', plinth_h=0.7, plinth=M('#b9b7b0', 0.85), basement=False, sill=1.6, wh=1.9, ww=1.05, wh_fixed=True),
                           attic=dict(ww=0.6, wh=0.45, sill=0.25, hood=None, pil=False, wh_fixed=True))   # white wooden house: tall windows under triangular pediments, small attic window in the gable
SPECK[1454]['P']['wall'] = MT('#f1efe9', 'wood')
_w1454 = classic_spec(1454, wall='#f3f2ee', trim='#f7f6f1', rust=False, garch=False, hood=None, pil=False, bw=3.6,
                      lay=dict(nf=1, cols=lambda c, nb: 'W' if c == 0 else 'N'), ground=dict(plinth_h=0.6, plinth=M('#b9b7b0', 0.85), basement=False, sill=1.0, wh=1.1, ww=1.1, wh_fixed=True), yard_same=True)
_w1454['P']['wall'] = MT('#f3f2ee', 'wood')
SPECK[1454]['alt'] = lambda x, y: _w1454 if x < -172.5 else None   # the low white board-clad wing west of the main house (one small window)   # Teatterikatu 3 (SV 2026, 17.11): white WOODEN house, board-clad, pediments over the windows
SPECK[1281].setdefault('extra', []).append(facade_bits((-185.0, 461.6), (-155.5, 459.6), [('wall', 0.0, 29.5, -0.4, 1.25, 0.08, MT('#f4f3ef', 'wood')), ('box', 0.0, 29.5, 1.25, 1.65, 0.0, 0.05, M('#f4f3ef'))]))   # white board fence with a lattice top in front of the garden (SV 2026)
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

def _x1451():
    """Valtakatu 19 (Karhukortteli, owner 17.11.2026 / Street View): balcony bands across the whole street side, projecting 2 m over the
    pavement, glazed above a dark slatted rail, white soffits; they turn the SE corner, where two round columns stand under them
    (geometry only: the Karhukortteli colours stay as approved)"""
    sc = 23.8 / 22.7; zs = [4.4 * sc + q * 3.05 * sc for q in range(6)]; fh = 3.05 * sc
    sl, rl, gl = M('#eeeeea', 0.5), M('#2f3336', 0.5), M('#9fb0ba', 0.05, 0.35)
    def bands(L, a=0.0):
        it = []
        for z in zs:
            it += [('box', a, L, z - 0.25, z, 0.0, 2.0, sl), ('box', a, L, z, z + 1.0, 1.93, 2.0, rl), ('box', a, L, z + 1.0, z + fh - 0.3, 1.97, 2.0, gl)]
            for q in range(int((L - a) / 0.22)): u = a + 0.08 + 0.22 * q; it.append(('box', u, u + 0.05, z + 0.05, z + 0.95, 1.88, 1.93, rl))
            for u in [a + (L - a) * r / max(1, round((L - a) / 1.6)) for r in range(1, round((L - a) / 1.6))]: it.append(('box', u - 0.03, u + 0.03, z + 1.0, z + fh - 0.3, 1.95, 2.02, rl))
        it.append(('box', a, L, zs[-1] + fh - 0.3, zs[-1] + fh, 0.0, 2.0, sl))
        return it
    south = bands(15.4)                                                                      # 13.4 m wall + 2 m round the corner
    south += [('box', 14.9, 15.4, 0.0, zs[0] - 0.25, 1.35, 1.85, M('#7d8184', 0.5))]   # column under the corner
    east = bands(4.0)
    east += [('box', 3.4, 3.9, 0.0, zs[0] - 0.25, 1.35, 1.85, M('#7d8184', 0.5))]
    return [facade_bits((-383.0, 324.0), (-369.9, 321.0), south), facade_bits((-369.9, 321.0), (-361.9, 356.0), east)]
SPECK[1451] = dict(SPECK[1451]); SPECK[1451]['extra'] = list(SPECK[1451].get('extra', [])) + _x1451()

SPECK[1446] = classic_spec(1446, wall='#e8a593', trim='#f3f1eb', rust=False, garch=False, hood=None, pil=False, bw=3.4,
                           lay=dict(nf=3, gh=3.6, fh=3.2, door_mid=False), ground=dict(plinth_h=0.45, plinth=M('#36383a', 0.6), basement=False, sband=0, ww=1.3, wh=1.75, sill=0.9),
                           first=dict(ww=1.2, wh=1.6, sill=0.9, sband=0), top=dict(ww=1.2, wh=1.5, sill=0.9), cornice=(0.3, 0.25, M('#45484a', 0.5)))
SPECK[1446]['extra'] = [facade_bits((-421.6, 440.1), (-444.6, 445.7), [('canopy', 1.5, 2.2, 3.1, 1.0, M('#2a2b2d', 0.5)), ('box', 0.9, 2.1, 0.45, 2.8, 0.0, 0.05, M('#9a6a3c', 0.6)),
                                                                     ('box', 2.6, 3.4, 1.4, 2.5, 0.0, 0.05, M('#5a4030', 0.6))])]   # 22 Hallituskatu (Street View 17.11.2026): salmon render, white-framed windows, restaurant door with a dark canopy at the west end, menu board
# 1447 (old brick building on Hallituskatu, owner 17.11.2026 / Street View): the tall east part has only tall round-headed windows over a
# light stone plinth, a stone cornice and a triangular pediment with a window in the middle; the low wing has short round-headed windows
_ST47 = M('#cbc2b0', 0.7)
SPECK[1447]['cornice'] = (0.16, 0.3, _ST47)
_P47 = dict(SPECK[1447]); _l47 = dict(_P47['layout']); _l47['plain'] = True; _P47['layout'] = _l47; _P47.pop('fit', None)
def _ra47(x, y, A=(-370.4, 427.9), t=(-0.9755, 0.2197)):
    d = (x - A[0]) * t[1] - (y - A[1]) * t[0]
    return _P47                                          # all walls plain: the generator's windows on the back mass and gables were wrong
SPECK[1447] = dict(SPECK[1447], runalt=_ra47, splitruns=True)
def _x47():
    """measured on the owner's frontal photo of the old power station (17.11.2026), scaled to the LoD2 widths (tall part 17.6 m, eave 10.2 m)"""
    BR = MT('#8e4a3c', 'brick', 0.8); J = M('#a9a092', 0.7); ST = _ST47; it = []
    it.append(('box', 0.0, 29.8, 0.0, 1.75, 0.0, 0.07, M('#a8a59f', 0.8)))                     # grey granite plinth, flush
    for zz in (0.58, 1.16): it.append(('box', 0.0, 29.8, zz - 0.02, zz + 0.02, 0.07, 0.08, J))
    for q in range(1, 40): u = q * 0.8 + (0.4 if q % 2 else 0); it.append(('box', u - 0.015, u + 0.015, 0.0, 1.75, 0.07, 0.08, J)) if u < 29.8 else None
    it.append(('box', 0.0, 29.8, 1.72, 1.85, 0.0, 0.12, ST))                                   # plinth cap
    for s0, s1 in ((0.0, 0.8), (6.4, 7.4), (16.8, 17.6)):                                       # stone pilasters with alternating quoins
        it.append(('box', s0 + 0.1, s1 - 0.1, 1.85, 9.2, 0.0, 0.08, ST))
        for q in range(int((9.2 - 1.85) / 0.42)):
            z = 1.85 + q * 0.42; e = 0.1 if q % 2 else 0.0
            it.append(('box', s0 - e, s1 + e, z + 0.02, z + 0.4, 0.0, 0.09, ST))
    it.append(('band', 0.0, 17.6, 4.95, 5.2, 0.08, ST))                                         # string course at the arch springing
    it += [('band', 0.0, 17.6, 9.2, 9.75, 0.1, ST), ('band', 0.0, 17.6, 9.75, 10.2, 0.18, ST)]   # stone entablature under the roof
    for c in (3.6, 9.6, 14.4):                                                                  # three tall round-headed windows, stone surrounds + keystone
        s0, s1 = c - 0.9, c + 0.9
        it += [('archwin', s0, s1, 1.95, 5.1, ST), ('box', c - 0.2, c + 0.2, 5.95, 6.45, 0.0, 0.15, ST)]
    it += [('gable', 12.1, 5.0, 10.0, 4.6, BR, 1), ('box', 11.45, 12.75, 9.5, 11.9, 0.12, 0.2, ST), ('box', 11.6, 12.6, 9.65, 11.75, 0.2, 0.22, M('#71838f', 0.05, 0.4)),
           ('box', 11.95, 12.25, 14.6, 15.3, 0.0, 0.25, M('#3d4246', 0.5))]                      # central gable with its window and finial
    for c in (19.6, 23.7, 27.8):                                                                # low wing: short round-headed windows
        s0, s1 = c - 0.8, c + 0.8
        it += [('archwin', s0, s1, 1.95, 2.9, ST), ('box', c - 0.17, c + 0.17, 3.6, 3.95, 0.0, 0.12, ST)]
    it += [('band', 17.6, 29.8, 2.85, 3.0, 0.06, ST), ('band', 17.6, 29.8, 4.25, 4.6, 0.14, ST)]
    return facade_bits((-370.4, 427.9), (-399.7, 434.5), it)
SPECK[1447]['extra'] = [_x47()]   # positions measured on Street View with px2wall
# 22 Hallituskatu east gable (owner 17.11.2026): far fewer windows than the generator drew, and a long dark balcony on the 2nd floor
_P46 = dict(SPECK[1446]); _l46 = dict(_P46['layout']); _l46['plain'] = True; _P46['layout'] = _l46; _P46.pop('fit', None)
def _ra46(x, y, A=(-424.3, 427.8), t=(0.2147, 0.9767)):
    d = (x - A[0]) * t[1] - (y - A[1]) * t[0]
    return _P46 if abs(d) < 1.5 and (x - A[0]) * t[0] + (y - A[1]) * t[1] > -0.5 else None
SPECK[1446]['runalt'] = _ra46; SPECK[1446]['splitruns'] = True
_x46 = []; _W46 = M('#e8a593')
kwin(_x46, 4.9, 5.9, 0.9, 2.3, _W46, panes=2); kwin(_x46, 3.9, 4.5, 4.4, 5.9, _W46, panes=1); kwin(_x46, 5.1, 6.2, 4.4, 5.9, _W46, panes=3); kwin(_x46, 6.7, 7.4, 4.4, 5.9, _W46, panes=2)
kwin(_x46, 4.8, 5.4, 7.9, 8.9, _W46, panes=1); kwin(_x46, 6.8, 7.6, 7.1, 9.3, _W46, panes=1); kwin(_x46, 5.6, 5.9, 10.6, 11.3, _W46, panes=1); kwin(_x46, 6.2, 6.5, 10.6, 11.3, _W46, panes=1)
_x46 += [('box', 1.9, 2.9, 0.45, 2.6, 0.0, 0.05, M('#e9e6df', 0.5)), ('canopy', 2.4, 1.4, 2.9, 0.6, M('#4a3a30', 0.5)),
         ('box', 6.0, 7.1, 0.4, 2.7, 0.0, 0.04, M('#26282a', 0.6)), ('box', 5.95, 7.15, 2.7, 2.85, 0.0, 0.08, M('#26282a', 0.6)),
         ('box', 3.3, 8.6, 6.75, 6.95, 0.0, 1.3, M('#2e3134', 0.5)), ('box', 3.3, 8.6, 6.95, 8.0, 1.22, 1.3, M('#363a3e', 0.5)),
         ('box', 3.3, 3.38, 6.95, 8.0, 0.0, 1.3, M('#363a3e', 0.5)), ('box', 8.52, 8.6, 6.95, 8.0, 0.0, 1.3, M('#363a3e', 0.5))]
SPECK[1446]['extra'] = list(SPECK[1446]['extra']) + [facade_bits((-424.3, 427.8), (-421.6, 440.1), _x46)]
# 1516 north side towards Hallituskatu (owner 17.11.2026 / Street View): recessed glazed balconies between four brick-clad concrete
# columns and brick floor beams, from the east: column | 3 glazed bays | column | 3 bays | column | 1 bay | column; the top storey and
# the glazed attic light grey (as on the Katariinankatu side)
def _x16n():
    fh = 3.1875; BRK, LT = MT('#5e4639', 'brick', 0.8), M('#b4bfc5', 0.4); fr = M('#34383b', 0.5); it = []
    W = 32.6; cw = 1.0; bw = (W - 4 * cw) / 7
    cols = [(0.0, cw), (cw + 3 * bw, 2 * cw + 3 * bw), (2 * cw + 6 * bw, 3 * cw + 6 * bw), (W - cw, W)]
    bays = [(cw + q * bw, cw + (q + 1) * bw) for q in range(3)] + [(2 * cw + 3 * bw + q * bw, 2 * cw + 3 * bw + (q + 1) * bw) for q in range(3)] + [(3 * cw + 6 * bw, W - cw)]
    for fl in range(8):
        z = fl * fh; m = BRK if fl < 7 else LT
        it.append(('box', 0.0, W, z - 0.1, z + 0.5, 0.0, 0.15, m))
        for a, b in bays:
            it += [('box', a, b, z + 0.5, z + fh - 0.1, 0.0, 0.03, M('#8d9aa2', 0.06, 0.35))]
            for q in range(1, 4): u = a + (b - a) * q / 4; it.append(('box', u - 0.03, u + 0.03, z + 0.5, z + fh - 0.1, 0.03, 0.06, fr))
    it.append(('box', 0.0, W, 8 * fh - 0.3, 8 * fh, 0.0, 0.14, LT))
    for a, b in cols: it += [('box', a, b, 0.0, 7 * fh, 0.0, 0.3, BRK), ('box', a, b, 7 * fh, 8 * fh, 0.0, 0.3, LT)]
    return facade_bits((-408.7, 410.6), (-440.5, 417.9), it)
_l16n = dict(SPECK[1516]['layout']); _l16n['plain'] = True; _l16n['P'] = dict(_l16n.get('P', {}), wall=M('#3a3d40', 0.5))
SPECK[1516]['walls'] = {**SPECK[1516]['walls'], 1: _l16n}; SPECK[1516]['extra'] = list(SPECK[1516].get('extra', [])) + [_x16n()]
SPECK[1338] = dict(spec_for(1338)); _l38 = dict(SPECK[1338]['layout']); _l38['cols'] = lambda c, nb: 'W'; SPECK[1338]['layout'] = _l38   # no loggias (Street View 17.11.2026)
def _x38():
    """1338 Katariinankatu side (owner + Street View 17.11.2026): two columns of French balconies (tall door, grey rail) on floors 1-4"""
    fh = 16.43 / 5; it = []; rl = M('#6c7175', 0.5)
    for fl in range(1, 5):
        z = fl * fh
        for c in (2.75, 12.2):
            it += [('box', c - 0.45, c + 0.45, z + 0.05, z + 2.25, 0.0, 0.03, GLASS_SKY), ('box', c - 0.55, c + 0.55, z + 0.05, z + 0.12, 0.0, 0.25, rl),
                   ('box', c - 0.55, c + 0.55, z + 0.95, z + 1.02, 0.18, 0.25, rl)]
            for q in range(9): u = c - 0.5 + q * 0.125; it.append(('box', u, u + 0.025, z + 0.12, z + 0.95, 0.2, 0.23, rl))
    return facade_bits((-485.6, 350.4), (-481.5, 369.1), it)
SPECK[1338]['extra'] = list(SPECK[1338].get('extra', [])) + [_x38()]
def _x57():
    """1357 (owner + Street View 17.11.2026): two stacks of glazed balconies with blue spandrel panels on the south side, floors 1-3:
    one right at the SE corner, the other about three windows further west; the south end of the Katariinankatu side is windowless"""
    fh = 13.37 / 4; it = []; WH = M('#ecebe6', 0.5)
    for s0, s1 in ((33.7, 37.9), (20.5, 24.7)):
        for fl in range(1, 4):
            z = fl * fh
            it += [('box', s0, s1, z - 0.2, z, 0.0, 1.6, WH), ('box', s0, s1, z, z + 1.05, 1.52, 1.6, M('#2f4f8f', 0.4)),
                   ('box', s0 + 0.05, s1 - 0.05, z + 1.05, z + fh - 0.2, 1.55, 1.6, M('#8fa3b0', 0.05, 0.35))]
            for e in (s0, s1 - 0.08): it += [('box', e, e + 0.08, z, z + 1.05, 0.0, 1.6, M('#2f4f8f', 0.4)), ('box', e, e + 0.08, z + 1.05, z + fh - 0.2, 0.0, 1.6, M('#8fa3b0', 0.05, 0.35))]
            for q in (1, 2): u = s0 + (s1 - s0) * q / 3; it.append(('box', u - 0.03, u + 0.03, z + 1.05, z + fh - 0.2, 1.6, 1.63, M('#34383b', 0.5)))
        it.append(('box', s0, s1, 4 * fh - 0.2, 4 * fh, 0.0, 1.6, WH))
    east = [('box', 0.2, 6.8, 13.37 / 4, 13.37, 0.0, 0.06, WH)]                                    # windowless south end of the east side (above the recessed ground storey)
    return [facade_bits((-513.1, 397.2), (-476.3, 388.1), it), facade_bits((-476.3, 388.1), (-472.1, 405.1), east)]
SPECK[1357] = dict(spec_for(1357)); SPECK[1357]['extra'] = list(SPECK[1357].get('extra', [])) + _x57()
_s57e = dict(spec_for(1357)); _l = dict(_s57e['layout']); _r = list(_l['rows']); _r[0] = (_r[0][0], 'shop', 'G'); _l['rows'] = _r
_l['rowP'] = dict(_l.get('rowP', {}), G=dict(setback=1.5, soffit=M('#ecebe6', 0.5))); _s57e['layout'] = _l
def _ra57(x, y, A=(-476.3, 388.1), t=(0.2398, 0.9708)):
    d = (x - A[0]) * t[1] - (y - A[1]) * t[0]
    return _s57e if abs(d) < 1.5 else None
SPECK[1357]['runalt'] = _ra57; SPECK[1357]['splitruns'] = True   # owner 17.11.2026: the ground storey of the Katariinankatu side is recessed under the floors above
# 1336 Valtakatu 30 (Street View 17.11.2026): light grey render, yellow tiled ground storey, loggia columns at both ends with yellow tiled
# parapets, a central stair column of narrow windows over the entrance canopy, three windows per storey between
_s36 = dict(spec_for(1336)); _l = dict(_s36['layout']); _l['plain'] = True; _s36['layout'] = _l
def _ra36(x, y, A=(-568.2, 365.7), t=(0.9734, -0.2290)):
    d = (x - A[0]) * t[1] - (y - A[1]) * t[0]; s = (x - A[0]) * t[0] + (y - A[1]) * t[1]
    return _s36 if abs(d) < 1.5 and -0.5 < s < 20.6 else None
def _x36():
    fh = (15.49 - 2.8) / 4; WL, TL, WT = M('#cdcbc4'), M('#d9cba0', 0.5), M('#ecebe6', 0.5); it = []
    it.append(('box', 0.0, 20.1, 0.0, 2.8, 0.0, 0.05, TL))
    for s0, s1 in ((1.2, 4.2), (14.8, 17.9)):
        it.append(('box', s0, s1, 0.0, 2.6, 0.05, 0.07, WT))                                     # light recessed bays under the loggias
        for fl in range(4):
            z = 2.8 + fl * fh
            it += [('box', s0, s1, z + 1.15, z + fh - 0.08, 0.0, 0.02, M('#4f565c', 0.4)), ('box', s0, s1, z - 0.08, z + 0.08, 0.0, 0.1, WT),
                   ('box', s0, s1, z + 0.08, z + 1.15, 0.0, 0.09, TL)]                              # loggia: dark opening, slab edge, tiled parapet
            kwin(it, s0 + 0.35, s1 - 0.35, z + 1.3, z + fh - 0.3, M('#4f565c', 0.4), panes=3, sill=False, dd=0.02)
        it += [('box', s0 - 0.1, s0, 2.8, 15.49, 0.0, 0.1, WL), ('box', s1, s1 + 0.1, 2.8, 15.49, 0.0, 0.1, WL)]
    for fl in range(4):
        z = 2.8 + fl * fh
        for c in (5.6, 8.6, 13.3): kwin(it, c - 0.8, c + 0.8, z + 0.9, z + 2.4, WL, panes=2)
        it.append(('box', 10.4, 11.3, z + 0.3, z + 2.6, 0.0, 0.04, M('#b7c3c6', 0.2, 0.2)))  # glass-block strip of the stair
    it += [('box', 10.1, 11.6, 0.0, 2.4, 0.04, 0.06, GLASS_SKY), ('canopy', 10.85, 2.8, 2.75, 1.4, M('#9fb0ba', 0.05, 0.3))]
    for c in (5.6, 8.6, 13.3): kwin(it, c - 0.5, c + 0.5, 1.5, 2.3, TL, panes=2, sill=False)
    return facade_bits((-568.2, 365.7), (-548.6, 361.1), it)
SPECK[1336] = dict(spec_for(1336), runalt=_ra36, splitruns=True, extra=[_x36()])
# 1368 (Street View 17.11.2026): dark grey-brown point block; the north gable is blank but for a central column of windows with red panels
_s68 = dict(spec_for(1368)); _l = dict(_s68['layout']); _l['plain'] = True; _s68['layout'] = _l
def _ra68(x, y, A=(-561.7, 329.2), t=(-0.9708, 0.2412)):
    d = (x - A[0]) * t[1] - (y - A[1]) * t[0]
    return _s68 if abs(d) < 1.5 else None
def _x68():
    it = []; fh = 28.92 / 9; W = M('#6f6a62')
    for fl in range(9):
        z = fl * fh
        it.append(('box', 7.4, 8.4, z + 0.5, z + 2.6, 0.0, 0.05, M('#a8322c', 0.5)))
        kwin(it, 8.6, 10.9, z + 0.8, z + 2.4, W, panes=2)
    return facade_bits((-561.7, 329.2), (-578.2, 333.3), it)
SPECK[1368] = dict(spec_for(1368), runalt=_ra68, splitruns=True, extra=[_x68()])
# 1337 Hallituskatu 26 (Street View 17.11.2026): white rendered two-storey block on a low basement, large multi-pane windows in brown frames,
# dark hipped roof with chimneys (no LoD2 here)
SPECK[1337] = classic_spec(1337, wall='#e8e6df', trim='#e8e6df', rust=False, garch=False, hood=None, pil=False, bw=3.9,
                           lay=dict(nf=2, gh=5.0, fh=4.4, door_mid=False), ground=dict(plinth_h=0.8, plinth=M('#8d8f90', 0.7), basement=True, sband=0, ww=1.55, wh=2.0, sill=1.5, wh_fixed=True),
                           first=dict(ww=1.55, wh=1.9, sill=0.9, sband=0, wh_fixed=True), top=dict(ww=1.55, wh=1.9, sill=0.9, wh_fixed=True), cornice=(0.3, 0.3, M('#e8e6df')))
SPECK[1337]['P'] = dict(SPECK[1337]['P'], frame=M('#6b3a2a', 0.6))
SPECK[1337]['roof'] = dict(kind='hip', rise=3.4, inset=5.0, mat=M('#45484b', 0.5), ov=0.45)
# 1370 Vapaudenkatu (owner + Street View 17.11.2026): precast block clad in cream brick tiles; west side towards Vapaudenkatu: two stacks of
# glazed balconies in the north part, the south part blank but for one window pair and small windows per storey, the ground storey blank
# but for the entrance door; a white loggia column at the SW corner on the south gable
_s70 = dict(spec_for(1370)); _l = dict(_s70['layout']); _l['plain'] = True; _s70['layout'] = _l
def _ra70(x, y):
    for A, t in (((-599.9, 285.3), (-0.2235, -0.9747)), ((-609.3, 244.3), (0.9750, -0.2237))):
        if abs((x - A[0]) * t[1] - (y - A[1]) * t[0]) < 1.5: return _s70
    return None
def _x70():
    fh = 15.28 / 5; TL, WH = MT('#e9dbbd', 'brick', 0.8), M('#f1f0ec', 0.5); w = []; s = []
    for fl in range(1, 5):
        z = fl * fh
        for s0, s1 in ((15.0, 20.0), (23.5, 29.5)):
            w += [('box', s0, s1, z - 0.2, z, 0.0, 1.4, WH), ('box', s0, s1, z, z + 1.0, 1.32, 1.4, M('#d9dee0', 0.3)),
                  ('box', s0 + 0.04, s1 - 0.04, z + 1.0, z + fh - 0.2, 1.35, 1.4, M('#8fa3b0', 0.05, 0.35))]
            for e in (s0, s1 - 0.08): w.append(('box', e, e + 0.08, z, z + fh - 0.2, 0.0, 1.4, WH))
            for q in (1, 2, 3): u = s0 + (s1 - s0) * q / 4; w.append(('box', u - 0.03, u + 0.03, z + 1.0, z + fh - 0.2, 1.4, 1.43, WH))
            kwin(w, s0 + 0.6, s0 + 1.5, z + 0.1, z + 2.4, TL, panes=1, sill=False); kwin(w, s0 + 1.9, s1 - 0.6, z + 0.9, z + 2.4, TL, panes=2, sill=False)
        for c in (3.0, 7.0, 11.0): kwin(w, c - 0.7, c + 0.7, z + 0.9, z + 2.3, TL, panes=2)
        kwin(w, 33.4, 35.6, z + 0.8, z + 2.2, TL, panes=3)
        if fl <= 2: kwin(w, 30.9, 31.4, z + 1.2, z + 1.7, TL, panes=1, sill=False); kwin(w, 31.9, 32.4, z + 1.2, z + 1.7, TL, panes=1, sill=False)
    for s0, s1 in ((15.0, 20.0), (23.5, 29.5)): w.append(('box', s0, s1, 5 * fh - 0.2, 5 * fh, 0.0, 1.4, WH))
    w += [('box', 27.0, 28.4, 0.0, 2.3, 0.0, 0.05, GLASS_SKY), ('box', 26.9, 28.5, 2.3, 2.42, 0.0, 0.08, M('#34383b', 0.5))]   # entrance door
    s.append(('box', 0.0, 3.2, 0.0, 15.28, 0.0, 0.35, WH))                                     # white loggia column, SW corner
    for fl in range(5):
        z = fl * fh; s.append(('box', 0.35, 2.85, z + 0.9, z + fh - 0.35, 0.35, 0.37, M('#4f565c', 0.4)))
    return [facade_bits((-599.9, 285.3), (-609.3, 244.3), w), facade_bits((-609.3, 244.3), (-598.4, 241.8), s)]
SPECK[1370] = dict(spec_for(1370), runalt=_ra70, splitruns=True, extra=_x70())
# 1261 Vapaudenkatu 4 (owner 17.11.2026): a long loading dock with a canopy along the Vapaudenkatu side of the low wing
SPECK[1261] = dict(SPECK.get(1261) or spec_for(1261))
def _fit61(lay_, hh, st):
    n = max(1, round((hh - 4.4) / 3.2)); bw = 3.4
    return dict(bw=bw, rows=[(4.4, 'shop', 'G')] + [(3.2, 'punched', 'F')] * n, cols=lambda c, nb: 'W',
                P=dict(ww=bw - 0.3, wh=1.25, sill=1.0, nx=3), rowP={})
SPECK[1261]['fit'] = _fit61; SPECK[1261]['layout'] = _fit61(None, 10.8, True)   # owner 17.11.2026: two storeys of long window bands over the shop storey (was five)
SPECK[1261]['extra'] = list(SPECK[1261].get('extra', [])) + [facade_bits((-641.0, 266.4), (-624.4, 337.6), [
    ('box', 4.5, 56.0, 0.0, 1.0, 0.0, 3.6, M('#b3b1aa', 0.8)), ('box', 4.5, 56.0, 0.98, 1.05, 3.4, 3.65, M('#3a3d40', 0.5)),
    ('box', 4.0, 56.5, 4.0, 4.45, 0.0, 4.6, M('#ecebe6', 0.5)), ('box', 4.0, 56.5, 3.75, 4.0, 4.4, 4.6, M('#ecebe6', 0.5)),   # deep cantilevered canopy
    ('box', 40.0, 45.0, 0.0, 0.33, 3.6, 4.6, M('#5fa38f', 0.6)), ('box', 40.0, 45.0, 0.33, 0.66, 3.6, 4.3, M('#5fa38f', 0.6)),   # green steps up to the dock
    ('box', 18.0, 21.0, 1.05, 2.0, 2.0, 2.15, M('#c8312c', 0.5)), ('box', 30.0, 33.0, 1.05, 2.0, 2.0, 2.15, M('#c8312c', 0.5))])]   # red sale banners
# Porin Siilo (1261, owner's photos 17.11.2026): north end of the tower = four slender white silo cylinders (2.4 m, 19.6 m high, on a grey
# base) carrying a cream top storey with three small windows (the 22.7 m LoD2 part), a brick chimney at the joint, and west of them a
# cream five-storey block with grey-framed window pairs
_C61 = M('#ebe4c4', 0.6)
_s61w = dict(SPECK[1261]); _l = dict(_s61w['layout']); _l['plain'] = True; _s61w['layout'] = _l; _s61w['P'] = dict(_s61w['P'], wall=M('#eeede8', 0.6)); _s61w.pop('fit', None)
_s61c = dict(SPECK[1261]); _s61c['P'] = dict(_s61c['P'], wall=_C61); _s61c.pop('fit', None)
_s61c['layout'] = dict(bw=3.4, rows=[(3.6, 'punched', 'G')] + [(3.4, 'punched', 'F')] * 4, cols=lambda c, nb: 'W', P=dict(ww=2.0, wh=1.35, sill=0.95, nx=2, frame=M('#6c7175', 0.5)), rowP={})
def _ra61(x, y, A=(-624.4, 337.6), t=(-0.9737, 0.2275)):
    d = (x - A[0]) * t[1] - (y - A[1]) * t[0]; s = (x - A[0]) * t[0] + (y - A[1]) * t[1]
    if abs(d) > 1.5: return None
    return _s61w if s < 12.0 else _s61c
SPECK[1261]['runalt'] = _ra61; SPECK[1261]['splitruns'] = True
_sil = [('box', 1.9, 11.9, 0.0, 1.3, 0.0, 1.6, M('#9a9c9c', 0.7))]
for q in range(4): _sil.append(('cyl', 3.3 + q * 2.4, 0.3, 1.2, 1.3, 19.6, M('#eeede8', 0.6)))
_sil += [('box', 1.5, 12.3, 19.6, 22.7, 0.0, 0.12, _C61), ('box', 1.5, 12.3, 22.6, 22.9, 0.0, 0.25, M('#d9d6c8', 0.5)),
         ('box', 11.9, 12.9, 0.0, 24.2, 0.0, 1.0, MT('#8b4a36', 'brick', 0.8))]
for c in (4.6, 6.9, 9.2): _sil += [('box', c - 0.45, c + 0.45, 20.6, 21.6, 0.12, 0.15, M('#3c4248', 0.3))]
_sil += [('box', 14.7, 16.8, 0.0, 18.1, 0.0, 0.15, _C61), ('box', 17.6, 19.0, 0.0, 18.1, 0.0, 0.15, _C61)]                                   # close the jog between the LoD2 wall pieces (it baked black)
for q in range(4): kwin(_sil, 14.9, 16.6, 3.6 + q * 3.4 + 0.95, 3.6 + q * 3.4 + 2.3, _C61, panes=2, frame=M('#6c7175', 0.5), dd=0.15)
SPECK[1261]['extra'] = list(SPECK[1261]['extra']) + [facade_bits((-624.4, 337.6), (-642.8, 341.9), _sil)]
# 1552 (Street View 17.11.2026): a low dark timber shed, open towards Hallituskatu between posts, behind a white board fence with a gate
SPECK[1552] = dict(spec_for(1552)); _l = dict(SPECK[1552]['layout']); _l['plain'] = True; SPECK[1552]['layout'] = _l
SPECK[1552]['P'] = dict(SPECK[1552]['P'], wall=M('#6a5444', 0.8))
_fen = [('box', 0.0, 23.0, 0.0, 2.2, 0.0, 0.08, M('#eeeeea', 0.7))]
for q in range(0, 23): _fen.append(('box', q + 0.0, q + 0.06, 0.0, 2.2, 0.08, 0.1, M('#d8d8d4', 0.7)))
_fen += [('box', 9.0, 9.25, 0.0, 2.4, -0.1, 0.2, M('#d8d8d4', 0.7)), ('box', 12.75, 13.0, 0.0, 2.4, -0.1, 0.2, M('#d8d8d4', 0.7))]   # gate posts
SPECK[1552]['extra'] = [facade_bits((214.6, 286.1), (208.6, 287.3), [('box', 0.3, 5.8, 0.0, 2.9, 0.0, 0.02, M('#2a2622', 0.8)), ('box', 0.2, 0.4, 0.0, 2.9, 0.0, 0.2, M('#6a5444', 0.8)),
                                                                    ('box', 2.95, 3.15, 0.0, 2.9, 0.0, 0.2, M('#6a5444', 0.8)), ('box', 5.7, 5.9, 0.0, 2.9, 0.0, 0.2, M('#6a5444', 0.8))]),
                        facade_bits((226.0, 287.8), (203.0, 292.4), _fen)]
def kspec(i):
    if i in SPECK: return SPECK[i]
    if i in MODERN: return spec_for(i)
    return classic_spec(i)
SPECK[1579] = dict(spec_for(1579)); SPECK[1579]['extra'] = list(SPECK[1579].get('extra', [])) + [SPECK_X1581, _H6X, facade_bits((37.2, 223.2), (135.9, 200.1), [('box', 59.3, 101.3, 5.25, 5.8, 0.0, 1.1, M('#cfbd93')), ('box', 59.3, 59.6, 1.2, 5.25, 0.0, 1.1, M('#cfbd93')), ('box', 101.0, 101.3, 1.2, 5.25, 0.0, 1.1, M('#cfbd93'))])]   # owner 16.11: Valtakatu 5's shops sit back under the upper floors - an overhanging band with end piers gives the recess   # Hallituskatu 6 shell carries the tower face


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
    zone = [(spec(j), _fp(j).buffer(2.0)) for j in sorted(subs, key=lambda j: _fp(j).area)]   # smallest first: a low wing in front of a tower;
    base = sp.get('runalt')                                                                      # one spec object per part (splitruns compares by id)
    def ra(x, y):
        r = base(x, y) if base else None                   # a hand-made runalt (Eteläpuisto 9 in 11's shell) wins
        if r: return r
        for sj, g in zone:
            if g.contains(_Pt(x, y)): return sj
        return None
    return dict(sp, runalt=ra, splitruns=True)

# ---------------------------------------------------------------- ground under the houses (the game's smoothed terrain field, terrain.js 'hs')
import base64 as _b64
try:
    _tt = open('/home/claude/pori/terrain.js').read(); _T = json.loads(_tt[_tt.index('{'):_tt.rindex('}') + 1])
    import numpy as _np
    _HS = _np.frombuffer(_b64.b64decode(_T['hs']), dtype=_np.int16).reshape(_T['ny'], _T['nx']) / 10.0
except Exception as _e:
    print('terrain.js not read:', _e); _T = None
def TZs(x, y):
    fx = min(_T['nx'] - 1.001, max(0, (x - _T['x0']) / _T['g'])); fy = min(_T['ny'] - 1.001, max(0, (y - _T['y0']) / _T['g']))
    i, j = int(fx), int(fy); u, v = fx - i, fy - j
    return float((_HS[j, i] * (1 - u) + _HS[j, i + 1] * u) * (1 - v) + (_HS[j + 1, i] * (1 - u) + _HS[j + 1, i + 1] * u) * v)
_low_strip(1566, 1573, 7.5, extra=[(64.0, 363.2), (77.5, 360.3), (78.5, 366.4), (65.4, 369.0)])   # owner 16.11: the uphill (south) end was right at 5.6 m above the street; the roof line runs level from there (north end on its high plinth)   # owner 16.11: Antinkatu climbs south - eave 5.6 m above the STREET in front (house base 2.61 = lowest ground)
_low_strip(1454, None, 4.3, extra=[(-172.6, 444.3), (-208.5, 456.9), (-212.0, 441.5), (-174.2, 433.0)])   # the wing and the rest of the long scan behind the fence: one low storey
_low_strip(1604, 1580, 8.2)   # owner 16.11: was too low
_low_strip(1579, 1716, 5.5)
def house_list(ids, spec, inside):
    """the houses of a block: LoD2 shells (split where one shell holds two houses on different ground) with their ground height.
    An MML LoD2 model stands on the LOWEST ground of its footprint (mml_parse z0), so a house is lifted to the lowest ground under it
    and, on its uphill sides, the facade starts at the street (zones2.ZBASE) with plinth below (owner 14.11.2026: Hallituskatu side too tall)."""
    out = []
    for i in ids:
        if i in inside: continue
        G = [r for kk, r, _ in RAW.get(i, []) if kk == 'G' and len(r) >= 3] if not spec(i).get('footprint') else []
        if not G: p = B[i]['p']; G = [[(p[c] / 10, p[c + 1] / 10) for c in range(0, len(p), 2)]]
        parts = [G]
        for p0, dd in SHELL_SPLIT.get(i, []):                  # one LoD2 shell, two houses at different ground levels (2 Antinkatu in 1560's)
            hp = lambda sg: Polygon([(p0[0] + sg * dd[0] * 200 - dd[1] * 200, p0[1] + sg * dd[1] * 200 + dd[0] * 200), (p0[0] - dd[1] * 200, p0[1] + dd[0] * 200),
                                     (p0[0] + dd[1] * 200, p0[1] - dd[0] * 200), (p0[0] + sg * dd[0] * 200 + dd[1] * 200, p0[1] + sg * dd[1] * 200 - dd[0] * 200)])
            new = []
            for rs in parts:
                for sg in (1, -1):
                    rr = []
                    for r in rs:
                        g_ = Polygon([(q[0], q[1]) for q in r]).buffer(0).intersection(hp(sg))
                        for gp in getattr(g_, 'geoms', [g_]):
                            if gp.geom_type == 'Polygon' and gp.area > 1: rr.append(list(gp.exterior.coords)[:-1])
                    if rr: new.append(rr)
            parts = new
        for rs in parts:
            poly = unary_union_([Polygon([(q[0], q[1]) for q in r]).buffer(0) for r in rs])
            lift = None
            if _T:
                pts = []
                for r in rs:
                    for a in range(len(r)):
                        P, Q = r[a], r[(a + 1) % len(r)]; m = max(1, int(math.hypot(Q[0] - P[0], Q[1] - P[1])))
                        pts += [(P[0] + (Q[0] - P[0]) * k / m, P[1] + (Q[1] - P[1]) * k / m) for k in range(m)]
                lift = round(min(TZs(x, y) for x, y in pts), 2)
            out.append(dict(i=i, rings=rs, poly=poly, l=lift))
    return out
def unary_union_(g):
    from shapely.ops import unary_union
    return unary_union(g)
HOUSES = []
def zbase(i, mid, n):
    """street level above the house's ground at this wall (0 on the downhill side)"""
    if not _T or not HOUSES: return 0.0
    pt = Point(mid)
    hs = [h for h in HOUSES if h['l'] is not None]
    if not hs: return 0.0
    h = min(hs, key=lambda h: h['poly'].distance(pt))
    return TZs(mid[0] + n[0] * 1.5, mid[1] + n[1] * 1.5) - h['l']
zones2.ZBASE = zbase; zones2.ZBASE_MAT = GRANITE

SKIRT = 2.6
SHELL_SPLIT = {1560: [((59.6, 413.7), (0.2257, 0.9742))], 1566: [((70.8, 383.4), (0.2297, 0.9738))]}
def skirt(Z, i, sp):
    """Plinth below z = 0 under every LoD2 wall. The game now lifts each house by ONE height (the highest ground under it) instead of
    the ground under every vertex, which leaned whole houses on the slopes down to the river (owner 14.11.2026): downhill this skirt
    shows as a taller plinth whose foot follows the street."""
    lay = sp.get('layout'); lay = lay if isinstance(lay, dict) else {}
    pm = (lay.get('rowP', {}).get('G') or {}).get('plinth') or GRANITE
    L = lambda q, z: (q[0] - Z.cx, q[1] - Z.cy, z)
    for k, r, _ in RAW.get(i, []):
        if k != 'W': continue
        for a in range(len(r)):
            P, Q = r[a], r[(a + 1) % len(r)]
            if P[2] < 0.05 and Q[2] < 0.05 and math.hypot(Q[0] - P[0], Q[1] - P[1]) > 0.3:
                add_solid(Z, [L(P, -SKIRT), L(Q, -SKIRT), L(Q, 0), L(P, 0)], pm, 0.3)

# Isolinnankatu 16 (1222, in shell 1221): one-storey timber house under a hip roof (SV 2026, 18.11). The scan wall on the street runs to 7.9 m.
lower_eave(1221, lambda r: max(q[0] for q in r) < 210.5 and min(q[2] for q in r) < 0.5 and max(q[2] for q in r) > 7.0, 4.1, 4.5)

def build_and_bake(name, ids, samples=16, spec=None):
    spec = spec or kspec
    if os.environ.get('PORI_PHS') and os.path.exists(os.environ['PORI_PHS']):
        ex = {int(k) for k in json.load(open(os.environ['PORI_PHS']))}; ids = [i for i in ids if i not in ex]
    ids = [i for i in ids if not (LOOK['b'].get(str(i)) or {}).get('gone')]   # styles 'gone': demolished since the map data (Saukkosen talo 1748, SV 2026)
    t = time.time()
    for i in ids:
        if RAW.get(i) and not spec(i).get('footprint'): B[i]['h'] = eave_of(i)
    zones2.ROOFBAKE = name in ZONESK and name != 'karhu'
    Z = Zone(name, ids); Z.roofflag = any(spec(i).get('roof') for i in ids)
    inside = shell_parts(ids, spec)
    global HOUSES
    HOUSES = house_list(ids, spec, inside)
    for i in ids:
        if i in inside: continue                         # drawn as a stretch of the LoD2 shell it stands in (see shell_parts)
        sp = spec(i)
        if RAW.get(i) and not sp.get('footprint'):
            subs = [j for j, o in inside.items() if o == i]
            if subs: sp = shell_runalt(sp, subs, spec)
            build_lod2(Z, i, sp)
            for ex in sp.get('extra', []): ex(Z, None, B[i]['h'], None)          # hand-built parts the LoD2 scan lacks (corner towers)
            skirt(Z, i, sp)
        else:
            sp2 = dict(sp); sp2['layout'] = sp['fit'](sp['layout'], B[i]['h'], True) if 'fit' in sp else sp['layout']
            if zones2.ROOFBAKE and not sp2.get('roof'): sp2['roof'] = dict(kind='flat', mat=roof_mat(i))   # no LoD2 shell: the game shows no roof here, the block must
            build_building(Z, i, sp2)
    shells = [dict(l=h['l'], r=[[round(v, 1) for q in r for v in (q[0], q[1])] for r in h['rings']], **({'nb': 1} if spec(h['i']).get('nobrick') else {})) for h in HOUSES]   # nb: rendered house in brick red, no brick bond in the game   # the game lifts each house by l
    for zt, ring in WALL_SHELLS:     # zt: only triangles below the wall top take its lift (a house cornice next to it keeps the house's)
        if _T: shells.append(dict(l=round(min(TZs(x, y) for x, y in ring), 2), zt=round(zt, 2), r=[[round(v, 1) for q in ring for v in q]]))
    Z.shells = shells
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
