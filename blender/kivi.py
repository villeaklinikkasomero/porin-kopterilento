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
                for k in range(nseg):
                    u0 = s0 + (s1 - s0) * k / nseg; u1 = s0 + (s1 - s0) * (k + 1) / nseg
                    quad([P(u0, z0, 0.0), P(u1, z0, 0.0), P(u1, z1, 0.0), P(u0, z1, 0.0)], mat)
                    quad([P(u1, z0, -tk), P(u0, z0, -tk), P(u0, z1, -tk), P(u1, z1, -tk)], mat)
                    quad([P(u0, z1, 0.0), P(u1, z1, 0.0), P(u1, z1, -tk), P(u0, z1, -tk)], mat)
                for u, sg in ((s0, -1), (s1, 1)):
                    quad([P(u, z0, -tk if sg > 0 else 0.0), P(u, z0, 0.0 if sg > 0 else -tk), P(u, z1, 0.0 if sg > 0 else -tk), P(u, z1, -tk if sg > 0 else 0.0)], mat)
            elif it[0] == 'archgate':                                       # ('archgate', s, w, zs, mat_gate): round-arched gateway in a wall: dark arch, light board gate below the springing
                _, s0, w, zs, gm = it; r = w / 2; dk = M('#3b3a36', 0.6)
                arcp = [P(s0 + r * math.cos(math.pi * k / 10), zs + r * math.sin(math.pi * k / 10), 0.03) for k in range(11)]
                quad([P(s0 - r, 0.0, 0.03), P(s0 + r, 0.0, 0.03)] + arcp, dk)
                quad([P(s0 - r + 0.08, 0.0, 0.06), P(s0 + r - 0.08, 0.0, 0.06), P(s0 + r - 0.08, zs, 0.06), P(s0 - r + 0.08, zs, 0.06)], gm)
                ob = [P(s0 + (r + 0.35) * math.cos(math.pi * k / 10), zs + (r + 0.35) * math.sin(math.pi * k / 10), 0.05) for k in range(11)]
                for k in range(10): quad([arcp[k], ob[k], ob[k + 1], arcp[k + 1]][::-1], M('#f3f0e8'))
            elif it[0] == 'chimney':                                        # ('chimney', s, d, z0, z1, w, mat): square stack d m behind the wall
                _, s0, dd, z0, z1, w, mat = it; hw = w / 2; c = [(s0 - hw, -dd - hw), (s0 + hw, -dd - hw), (s0 + hw, -dd + hw), (s0 - hw, -dd + hw)]
                for k in range(4):
                    (u0, d0), (u1, d1) = c[k], c[(k + 1) % 4]
                    quad([P(u0, z0, d0), P(u1, z0, d1), P(u1, z1, d1), P(u0, z1, d0)], mat, True)
                quad([P(u, z1, d) for u, d in c], mat, True)
            elif it[0] == 'vents':                                          # a row of small attic openings
                _, s0, n_, z, mat = it; dk = M('#2a2f33', 0.4)
                for k in range(n_):
                    u = s0 + (k - (n_ - 1) / 2) * 0.55
                    quad([P(u - 0.15, z, 0.14), P(u + 0.15, z, 0.14), P(u + 0.15, z + 0.3, 0.14), P(u - 0.15, z + 0.3, 0.14)], dk)
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
SPECK[1604] = classic_spec(1604, trim='#b0603f', rust=False, garch=False, hood='cornice', pil=False, top=dict(hood='cornice'))  # yellow Jugend house on Antinkatu: brick-red arched lintels with keystones over the windows on every floor (Street View 14.11.2026); gables from the LoD2 shell
cut_walls(1284, (-170.4, 407.5), (0.204, 0.981))     # Heinen talo: the two street walls are cut 2.4 m from the corner; the round corner bay
cut_walls(1284, (-173.3, 405.5), (-0.986, 0.168))    # stands there, so those stretches stay blank (owner 15.11.2026: windows and clutter behind the tower)
_b1284 = classic_spec(1284, wall='#e4dcc6', trim='#f3eee2', rust=True, garch=False, hood=None, pil=False, lay=dict(cols=lambda c, nb: 'N'))
_b1284['yard'] = _b1284['layout']
SPECK[1284] = classic_spec(1284, wall='#e4dcc6', trim='#f3eee2', rust=True, garch=True, hood='pediment', pil=False,
                           extra=[round_corner(-171.5, 405.9, 2.0, 13.2, math.atan2(-0.827, 0.563), M('#e9e1cb'), M('#f5f1e6'), M('#8d8a84', 0.85), M('#2e3337', 0.45, 0.4))])   # Heinen talo / seurakuntatoimisto: banded rustication on the ground floor, arched ground-floor windows, pedimented upper windows (Street View 14.11.2026)
SPECK[1284]['alt'] = lambda x, y: _b1284 if math.hypot(x + 170.9, y - 405.1) < 2.6 else None
SPECK[1513] = classic_spec(1513, wall='#9b4b36', trim='#b9654c', rust=False, garch=True, hood=None, pil=True, bw=4.6, cornice=(0.3, 0.7, M('#7f3d2c')))   # brewery remnant
SPECK[1281] = classic_spec(1281, wall='#e2dcbc', trim='#f4f1e8', rust=False, garch=False, hood='cornice', pil=True)   # Eteläranta 10: pale yellow render, white pilasters, window surrounds and cornice (Street View 14.11.2026)
SPECK[1285] = classic_spec(1285, wall='#e8ddb6', trim='#f6f4ee', rust=False, garch=True, hood='cornice', pil=True, lay=dict(nf=2, gh=6.4, frieze=1.4, cols=lambda c, nb: 'W'), ground=dict(plinth_h=1.9), top=dict(blank=True))   # wireframe 14.11.2026: high plinth with cellar windows, ground 4.5 m, first 4.8 m, plain frieze 1.4 m under the cornice   # Eteläranta / S. Palmgreninkatu: very light cream, TWO storeys, arched ground-floor windows (owner + Street View 14.11.2026); chamfered corner with a balcony not modelled yet
_c1285 = classic_spec(1285, wall='#e8ddb6', trim='#f6f4ee', rust=False, garch=True, hood='cornice', pil=False, bw=2.2, lay=dict(nf=2, gh=6.4, frieze=1.4, cols=lambda c, nb: 'D'), ground=dict(plinth_h=1.9), top=dict(blank=True),
                      first=dict(balcony=True, hood='cornice'))
_w1285 = classic_spec(1285, wall='#e8ddb6', trim='#f6f4ee', rust=False, garch=True, hood='cornice', pil=True, bw=2.9, lay=dict(nf=2, gh=6.4, frieze=1.4, cols=lambda c, nb: 'W'), ground=dict(plinth_h=0.8, basement=False), top=dict(blank=True))   # S. Palmgreninkatu side: the street is higher, a low plinth (wireframe 14.11.2026)
SPECK[1285]['alt'] = lambda x, y: _c1285 if -39.6 < x < -36.5 and 457.8 < y < 460.2 else _w1285 if x < -39.5 and y < 457.0 else None   # the corner chamfer: door below, balcony above (block walk 14.11.2026)
# 3 Antinkatu / 10 Hallituskatu (block walk 14.11.2026): the whole Antinkatu front is white, the Hallituskatu front yellow
_w1563 = classic_spec(1563, wall='#efede6', trim='#f7f6f1', rust=False, garch=False, hood='cornice', pil=False, lay=dict(nf=2, frieze=0.9, cols=lambda c, nb: 'W'), ground=dict(plinth_h=0.6, plinth=GRANITE), top=dict(ww=0.6, wh=0.3, sill=0.3, hood=None, pil=False, wh_fixed=True))   # 3 Antinkatu (wireframe 14.11.2026): grey plinth (the ochre patch on the wall is paint), no street door, small vents under the eave
SPECK[1576] = classic_spec(1576, wall='#a5513d', trim='#ece6da', rust=False, garch=False, hood=None, pil=False, bw=3.3,
                           lay=dict(nf=1, frieze=0.9, cols=lambda c, nb: 'W' if c % 2 == 0 else 'Y'), ground=dict(plinth_h=0.7, plinth=M('#7e3d2e', 0.85), basement=False, ww=1.15, wh=1.85),
                           attic=dict(ww=0.45, wh=0.25, sill=0.35, hood=None, pil=False, wh_fixed=True))   # Hallituskatu south side: brick-red RENDERED one-storey house (owner 15.11.2026: rapattu, ei tiili), five windows in white surrounds, three small vents under the white cornice (Street View 15.11.2026)
SPECK[1576]['nobrick'] = True; SPECK[1576]['P']['wall'] = MT('#a5513d', 'plaster')   # owner 15.11.2026: rendered, not brick (the bake and the game would read this red as brick)
SPECK[1576]['extra'] = [facade_bits((23.5, 335.0), (7.3, 339.0), [('chimney', 8.0, 2.6, 6.0, 8.8, 0.6, M('#3b3634')), ('chimney', 11.9, 2.6, 6.0, 8.8, 0.6, M('#3b3634'))]),
                        facade_bits((7.3, 339.0), (-43.7, 351.7), [('wall', 0.2, 51.6, -0.6, 2.3, 0.45, MT('#d8d3c7', 'plaster'))])]   # owner 15.11.2026: the free-standing light rendered garden wall along Hallituskatu between this house and the Kaupungintalo
SPECK[1563] = classic_spec(1563, wall='#e6cf8f', trim='#f4f1e8', rust=False, garch=False, hood='cornice', pil=False, bw=2.7, lay=dict(nf=2, frieze=1.2, cols=lambda c, nb: 'D' if c == 0 else 'N' if c == 3 else 'W'), attic=dict(ww=0.6, wh=0.3, sill=0.45, hood=None, pil=False, wh_fixed=True))   # 10 Hallituskatu (wireframe 14.11.2026): five bays, door with a dressed surround at the west end, blind 4th bay, vents in the frieze
SPECK[1563]['alt'] = lambda x, y: _w1563 if x > 44.0 else None
SPECK[1447] = classic_spec(1447, wall='#9c4f3c', trim='#e6dccb', rust=False, garch=True, hood=None, pil=True, bw=3.8, first=dict(arch=True), top=dict(arch=True))   # old red-brick building at Eteläranta/Karhu: round-arched windows with light surrounds, brick pilasters (was a plain modern box; Street View 14.11.2026)
def _s1575(bw):
    return classic_spec(1575, wall='#e6d29c', trim='#f4f1e8', rust=False, garch=True, hood='cornice', pil=True, bw=bw,
                        lay=dict(nf=2, frieze=1.1, cols=lambda c, nb: 'W'), ground=dict(plinth_h=0.55, basement=False, ww=1.85, wh=2.95, sill=0.15, wh_fixed=True),
                        attic=dict(ww=0.55, wh=0.3, sill=0.4, hood=None, pil=False, wh_fixed=True))
SPECK[1575] = _s1575(3.07)   # 5 Antinkatu / Hallituskatu corner (wireframe 15.11.2026): eight bays on Antinkatu, NO door there; big round-arched shop windows from just above the low brick-red plinth, framed windows with cornices above, a small attic window over every bay
_h1575 = _s1575(3.6)         # Hallituskatu end: three bays
SPECK[1575]['alt'] = lambda x, y: _h1575 if y > 331.0 else None   # Hallituskatu end: three bays
SPECK[1575]['extra'] = [facade_bits((28.8, 333.9), (23.5, 335.0), [('wall', 0.0, 5.4, -0.6, 5.4, 0.5, MT('#f1eee6', 'plaster')), ('archgate', 2.9, 3.4, 3.1, MT('#ece3c4', 'wood'))])]   # white arched gateway to the yard between 1575 and 1576 (Street View 15.11.2026)
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
SPECK[1573] = classic_spec(1573, trim='#f4f1e8', rust=False, garch=False, hood=None, pil=False, bw=3.08,
                           lay=dict(nf=1, frieze=1.6, cols=lambda c, nb: 'D' if c == 2 else 'X' if c == nb - 2 else 'W'),
                           ground=dict(plinth_h=0.6, sill=0.93, wh=2.07, ww=1.15, wh_fixed=True, dw=1.15, door=M('#c9ccc6', 0.4)), first=dict(hood=None),
                           top=dict(ww=0.6, wh=0.37, sill=0.26, hood=None, pil=False, wh_fixed=True))   # 4 Antinkatu, measured with the wireframe on Street View (14.11.2026): eave 5.6 m, windows 1.5-3.6 m, plinth 0.6 m, six attic vents 4.3-4.6 m; door third from the north, no window in the fifth bay
SPECK[1566] = classic_spec(1566, wall='#e3dfcf', trim='#efece2', rust=True, garch=False, hood='cornice', pil=True, bw=3.6,
                           ground=dict(hood='cornice', basement=False, plinth_h=1.1, plinth=M('#8d8c87', 0.85), rustc=M('#c9c4b3')),
                           top=dict(ww=0.9, wh=0.45, sill=0.35, hood=None), lay=dict(nf=2, frieze=1.1, cols=lambda c, nb: 'W'), roofmat=M('#4b5552', 0.5, 0.3))
_e1566 = classic_spec(1566, wall='#e3dfcf', trim='#efece2', rust=True, garch=False, hood='cornice', pil=True, bw=3.6,
                      ground=dict(hood='cornice', basement=False, plinth_h=1.1, plinth=M('#8d8c87', 0.85), rustc=M('#c9c4b3')),
                      top=dict(ww=0.9, wh=0.45, sill=0.35, hood=None), lay=dict(nf=2, frieze=1.1, cols=lambda c, nb: 'G' if c == 1 else 'W'), roofmat=M('#4b5552', 0.5, 0.3))   # Eteläranta front: arched gateway in the second bay from the east, no street door (wireframe 15.11.2026)
SPECK[1566]['alt'] = lambda x, y: _e1566 if y > 418.0 and x > 85.0 else None
# Eteläranta 4 / Antinkatu 2 (owner photo 14.11.2026): pale cream render, two storeys, block-rusticated ground floor, straight cornices
# over every window, a strong string course, rusticated corners, small attic windows in the frieze, grey stone plinth, dark sheet roof;
# a gateway at the Antinkatu end (not modelled)
SPECK[1569] = dict(P=dict(wall=M('#dedcd5'), spandrel=M('#dedcd5'), frame=M('#5b3f2c', 0.6), sign=SIGNS), cornice=(0.7, 0.2, M('#2f3437', 0.5)),
                   layout=lay(7.5, 'ribbon', gh=0, bw=1.3, fh=3.4))   # Antinkatu, mid-20th-century infill (owner photo 14.11.2026): light grey render, two long window bands with brown wooden frames, dark fascia
squash(1287, 10.0, 0.25)   # the scan's walls reach 14-17 m; Street View: 2 storeys + attic frieze, eave about 8 m above the street, low roof (wireframe 14.11.2026)
SPECK[1287] = classic_spec(1287, wall='#e9e4d2', trim='#f6f4ee', rust=True, garch=False, hood='cornice', pil=False, bw=2.7, lay=dict(nf=2, frieze=1.3, cols=lambda c, nb: 'W'), attic=dict(ww=0.6, wh=0.4, sill=0.45, hood=None, pil=False, wh_fixed=True))   # 12 Hallituskatu / 3 S. Palmgreninkatu: pale cream, banded ground floor, cornices over the upper windows, small attic windows, eight bays
_h1287 = classic_spec(1287, wall='#e9e4d2', trim='#f6f4ee', rust=True, garch=False, hood='cornice', pil=False, bw=2.07, lay=dict(nf=2, frieze=1.3, cols=lambda c, nb: 'N' if c == 1 else 'W'), ground=dict(plinth_h=0.35, basement=False, sill=0.1, wh=2.3, wh_fixed=True), attic=dict(ww=0.6, wh=0.4, sill=0.45, hood=None, pil=False, wh_fixed=True))   # Hallituskatu front: seven narrow bays, the second blind; tall ground-floor windows from just above the pavement, no cellar windows (owner 14.11.2026)
SPECK[1287]['alt'] = lambda x, y: _h1287 if y < 377.0 else None
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
