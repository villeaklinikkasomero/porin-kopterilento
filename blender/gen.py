"""Pori centre blocks -> Blender -> baked GLB.
One bay x one storey of every facade is modelled in detail and baked (selected-to-active) onto a flat tile;
the tile is repeated along the wall. Balconies, bay windows and roofs are real geometry baked directly."""
import bpy, math, sys, os, random, base64
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
sys.path.insert(0, '/home/claude')
from lib_city import B, poly, cen

GRID = math.radians(-13.035)
ATLAS = 2048

def hexlin(hx):
    hx = hx.lstrip('#'); c = [int(hx[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4) for v in c)

_mats = {}
def M(col, rough=0.85, metal=0.0):
    """material key"""
    if isinstance(col, str): col = hexlin(col)
    k = (round(col[0], 4), round(col[1], 4), round(col[2], 4), rough, metal)
    _mats.setdefault(k, None); return k

GLASS = M((0.035, 0.05, 0.065), 0.08)
GLASS2 = M((0.10, 0.12, 0.14), 0.15)
CURT = M((0.55, 0.52, 0.46), 0.6)
BLACKGL = M((0.012, 0.014, 0.018), 0.06)
WHITE = M('#f1efe8'); DARK = M('#2c2e31'); ALU = M('#9aa0a3', 0.5, 0.6)

def bmat(k):
    if _mats[k] is None:
        m = bpy.data.materials.new('m%d' % len(bpy.data.materials)); m.use_nodes = True
        b = m.node_tree.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value = (k[0], k[1], k[2], 1); b.inputs['Roughness'].default_value = k[3]; b.inputs['Metallic'].default_value = k[4]
        _mats[k] = m
    return _mats[k]

# ---------------------------------------------------------------- module builder
class MB:
    def __init__(s, bw, fh, seed=0):
        s.bw, s.fh = bw, fh; s.hi = []; s.s3 = []; s.tiles = None; s.rnd = random.Random(seed)
    def hq(s, pts, mat): s.hi.append((pts, mat))
    def q(s, u0, v0, u1, v1, d, mat):
        if u1 - u0 < 1e-4 or v1 - v0 < 1e-4: return
        s.hi.append(([(u0, v0, d), (u1, v0, d), (u1, v1, d), (u0, v1, d)], mat))
    def sides(s, u0, v0, u1, v1, d0, d1, mat, bottom=True, top=True):
        s.hi.append(([(u0, v0, d0), (u0, v0, d1), (u0, v1, d1), (u0, v1, d0)], mat))
        s.hi.append(([(u1, v0, d0), (u1, v0, d1), (u1, v1, d1), (u1, v1, d0)], mat))
        if bottom: s.hi.append(([(u0, v0, d0), (u1, v0, d0), (u1, v0, d1), (u0, v0, d1)], mat))
        if top: s.hi.append(([(u0, v1, d0), (u1, v1, d0), (u1, v1, d1), (u0, v1, d1)], mat))
    def prot(s, u0, v0, u1, v1, d, mat, d0=0):
        """box sticking out of the wall (captured in the tile)"""
        s.q(u0, v0, u1, v1, d, mat); s.sides(u0, v0, u1, v1, d0, d, mat)
    def wall(s, holes, mat, d=0, u0=0, u1=None, v0=0, v1=None):
        u1 = s.bw if u1 is None else u1; v1 = s.fh if v1 is None else v1
        us = sorted(set([u0, u1] + [h[0] for h in holes] + [h[2] for h in holes])); vs = sorted(set([v0, v1] + [h[1] for h in holes] + [h[3] for h in holes]))
        us = [u for u in us if u0 - 1e-6 <= u <= u1 + 1e-6]; vs = [v for v in vs if v0 - 1e-6 <= v <= v1 + 1e-6]
        for j in range(len(vs) - 1):
            run = None
            for i in range(len(us) - 1):
                cu, cv = (us[i] + us[i + 1]) / 2, (vs[j] + vs[j + 1]) / 2
                solid = not any(h[0] < cu < h[2] and h[1] < cv < h[3] for h in holes)
                if solid: run = [us[i], us[i + 1]] if run is None else [run[0], us[i + 1]]
                if (not solid or i == len(us) - 2) and run is not None:
                    s.q(run[0], vs[j], run[1], vs[j + 1], d, mat); run = None
    def window(s, u0, v0, u1, v1, wallmat, r=0.14, fr=0.06, fmat=WHITE, nx=1, ny=1, glass=None, d=0, curt=0.3):
        """recessed window; returns the hole rect for wall()"""
        s.sides(u0, v0, u1, v1, d, d - r, wallmat)
        g = d - r
        for i in range(nx):
            for j in range(ny):
                a0, a1 = u0 + (u1 - u0) * i / nx, u0 + (u1 - u0) * (i + 1) / nx; b0, b1 = v0 + (v1 - v0) * j / ny, v0 + (v1 - v0) * (j + 1) / ny
                gm = glass or (CURT if s.rnd.random() < curt * 0.5 else GLASS2 if s.rnd.random() < 0.35 else GLASS)
                s.q(a0 + fr, b0 + fr, a1 - fr, b1 - fr, g, gm)
                if s.rnd.random() < curt and glass is None and (a1 - a0) > 0.5:   # half-drawn curtain
                    s.q(a0 + fr, b0 + fr, a0 + fr + (a1 - a0 - 2 * fr) * 0.3, b1 - fr, g + 0.005, CURT)
                s.q(a0, b0, a1, b0 + fr, g + 0.02, fmat); s.q(a0, b1 - fr, a1, b1, g + 0.02, fmat)
                s.q(a0, b0 + fr, a0 + fr, b1 - fr, g + 0.02, fmat); s.q(a1 - fr, b0 + fr, a1, b1 - fr, g + 0.02, fmat)
        return (u0, v0, u1, v1)
    # real geometry (kept in the exported mesh)
    def s3q(s, pts, mat, dens=1.0): s.s3.append((pts, mat, dens))
    def s3box(s, u0, v0, u1, v1, d0, d1, mat, top=True, bottom=True, dens=1.0, topmat=None):
        s.s3q([(u0, v0, d1), (u1, v0, d1), (u1, v1, d1), (u0, v1, d1)], mat, dens)
        s.s3q([(u0, v0, d0), (u0, v0, d1), (u0, v1, d1), (u0, v1, d0)], mat, dens)
        s.s3q([(u1, v0, d1), (u1, v0, d0), (u1, v1, d0), (u1, v1, d1)], mat, dens)
        if bottom: s.s3q([(u0, v0, d0), (u1, v0, d0), (u1, v0, d1), (u0, v0, d1)], mat, dens)
        if top: s.s3q([(u0, v1, d1), (u1, v1, d1), (u1, v1, d0), (u0, v1, d0)], topmat or mat, dens)
    def tile(s, u0, v0, u1, v1, d=0):
        if s.tiles is None: s.tiles = []
        s.tiles.append((u0, v0, u1, v1, d))

# ---------------------------------------------------------------- facade modules: f(mb, col, P)
def m_plain(mb, col, P):
    mb.wall([], P['wall'])

def m_punched(mb, col, P):
    """rendered wall, one window per bay.  col: 'W' window, 'B' balcony, 'S' stair, 'N' blank"""
    bw, fh, W = mb.bw, mb.fh, P['wall']
    ww = min(P.get('ww', 1.5), bw - 0.7); wh = P.get('wh', 1.45); sill = P.get('sill', 0.85)
    holes = []
    if col == 'N': mb.wall([], W); return
    if col == 'S':
        holes.append(mb.window(bw / 2 - 0.6, 0.2, bw / 2 + 0.6, fh - 0.25, W, nx=1, ny=3, fmat=P.get('frame', WHITE), curt=0))
    elif col == 'B':
        holes.append(mb.window(bw / 2 - ww / 2, sill, bw / 2 + ww / 2 - 0.75, sill + wh, W, nx=P.get('nx', 2) - 1 or 1, fmat=P.get('frame', WHITE)))
        holes.append(mb.window(bw / 2 + ww / 2 - 0.7, 0.12, bw / 2 + ww / 2, sill + wh, W, fmat=P.get('frame', WHITE), curt=0))
        bd = P.get('bd', 1.1); rail = P.get('rail', WHITE); b0, b1 = max(0.15, bw / 2 - ww / 2 - 0.4), min(bw - 0.15, bw / 2 + ww / 2 + 0.4)
        mb.s3box(b0, 0.0, b1, 0.14, 0, bd, P.get('slab', WHITE))
        mb.s3box(b0, 0.14, b1, 1.05, 0, bd, rail, top=False, bottom=False)
        mb.s3q([(b0, 0.14, bd - 0.04), (b0, 1.05, bd - 0.04), (b1, 1.05, bd - 0.04), (b1, 0.14, bd - 0.04)], rail, 0.6)
    else:
        holes.append(mb.window(bw / 2 - ww / 2, sill, bw / 2 + ww / 2, sill + wh, W, nx=P.get('nx', 2), fmat=P.get('frame', WHITE)))
    mb.wall(holes, W)
    if P.get('joints'):                     # prefabricated panel joints
        mb.q(0, 0, 0.035, fh, 0.004, P['joints']); mb.q(0, 0, bw, 0.035, 0.004, P['joints'])
    if P.get('band'):                       # storey band under the windows (Laaksovirta)
        mb.prot(0, sill - 0.14, bw, sill - 0.02, 0.07, P['band'])
        if P.get('band2', True): mb.prot(0, sill + wh + 0.02, bw, sill + wh + 0.14, 0.07, P['band'])
    if P.get('surround'):                   # light render frame round the window
        s_ = 0.12; h = holes[0]
        mb.prot(h[0] - s_, h[1] - s_, h[2] + s_, h[1], 0.03, P['surround']); mb.prot(h[0] - s_, h[3], h[2] + s_, h[3] + s_, 0.03, P['surround'])
        mb.prot(h[0] - s_, h[1], h[0], h[3], 0.03, P['surround']); mb.prot(h[2], h[1], h[2] + s_, h[3], 0.03, P['surround'])

def m_ribbon(mb, col, P):
    """window band across the bay with a spandrel panel below"""
    bw, fh, W = mb.bw, mb.fh, P['wall']; sill = P.get('sill', 0.9); wh = P.get('wh', 1.5); sp = P.get('spandrel', W)
    if col == 'N': mb.wall([], W); return
    e = P.get('pier', 0.0); sp_w = P.get('sidepanel', 0)
    h = mb.window(e + sp_w, sill, bw - e, sill + wh, W, r=0.1, nx=P.get('nx', 2), fmat=P.get('frame', WHITE))
    if sp_w: mb.q(e, sill, e + sp_w, sill + wh, -0.03, P.get('sidemat', DARK)); h = (e, sill, bw - e, sill + wh)
    mb.wall([h, (0, 0, bw, sill)] if sp != W else [h], W)
    if sp != W: mb.q(0, 0, bw, sill, -0.02, sp); mb.q(0, sill - 0.05, bw, sill, 0.0, W)
    if P.get('band'): mb.prot(0, sill - 0.12, bw, sill, 0.06, P['band']); mb.prot(0, sill + wh, bw, sill + wh + 0.12, 0.06, P['band'])
    if col == 'F':                           # french balcony
        mb.prot(0.3, 0.1, bw - 0.3, 1.0, 0.1, P.get('rail', DARK))

def m_raster(mb, col, P):
    """projecting concrete grid, window + coloured panel in every field"""
    bw, fh, W = mb.bw, mb.fh, P['wall']; fin = P.get('fin', 0.22); dp = P.get('fdepth', 0.22); sill = P.get('sill', 0.95); pan = P.get('panel', W)
    if col == 'L':                            # recessed balcony field
        m_loggia(mb, col, P)
    else:
        h = mb.window(fin / 2, sill, bw - fin / 2, fh - 0.14, W, r=0.08, nx=P.get('nx', 2), fmat=P.get('frame', WHITE), d=0)
        mb.q(fin / 2, 0, bw - fin / 2, sill, 0, pan)
        mb.wall([h, (fin / 2, 0, bw - fin / 2, sill)], W)
    if P.get('vfin', True): mb.prot(-0.001, 0, fin / 2, fh, dp, W); mb.prot(bw - fin / 2, 0, bw + 0.001, fh, dp, W)
    if P.get('hfin', True): mb.prot(0, fh - 0.14, bw, fh, dp, W); mb.prot(0, 0, bw, 0.05, dp, W)

def m_vraster(mb, col, P):
    """KOP: slender vertical ribs, glass and black glass panels between"""
    bw, fh, W = mb.bw, mb.fh, P['wall']; fin = P.get('fin', 0.6); dp = 0.3; sill = 1.0
    n = P.get('nx', 2)
    h = mb.window(fin / 2, sill, bw - fin / 2, fh, W, r=0.05, nx=n, fmat=P.get('frame', DARK))
    mb.q(fin / 2, 0, bw - fin / 2, sill, -0.03, P.get('panel', BLACKGL))
    mb.wall([h, (fin / 2, 0, bw - fin / 2, sill)], W)
    mb.prot(-0.001, 0, fin / 2, fh, dp, W); mb.prot(bw - fin / 2, 0, bw + 0.001, fh, dp, W)

def m_loggia(mb, col, P):
    """recessed balcony"""
    bw, fh, W = mb.bw, mb.fh, P['wall']; dp = P.get('ldepth', 1.3); e = P.get('lpier', 0.25); rail = P.get('rail', DARK)
    hole = (e, 0.12, bw - e, fh - 0.2)
    mb.wall([hole], W)
    mb.sides(hole[0], hole[1], hole[2], hole[3], 0, -dp, P.get('linner', W))
    # back wall with door + window
    saved = mb.hi; mb.hi = []
    h1 = mb.window(hole[0] + 0.3, hole[1], hole[0] + 1.1, hole[1] + 2.1, W, r=0.08, curt=0)
    h2 = mb.window(hole[0] + 1.3, hole[1] + 0.8, hole[2] - 0.3, hole[1] + 2.1, W, r=0.08, nx=2) if hole[2] - hole[0] > 2.4 else None
    mb.wall([h for h in (h1, h2) if h], P.get('linner', W), u0=hole[0], u1=hole[2], v0=hole[1], v1=hole[3])
    back = [([(p[0], p[1], p[2] - dp) for p in pts], m) for pts, m in mb.hi]; mb.hi = saved + back
    mb.q(hole[0], hole[1], hole[2], hole[1] + 1.0, -0.03, rail)              # railing
    if P.get('corr'):                                                        # corrugated sheet look
        n = int((hole[2] - hole[0]) / 0.16)
        for i in range(n): mb.prot(hole[0] + i * 0.16, hole[1] + 0.04, hole[0] + i * 0.16 + 0.07, hole[1] + 0.96, -0.005, rail, d0=-0.03)

def m_erker(mb, col, P):
    """functionalist rectangular bay window"""
    bw, fh, W = mb.bw, mb.fh, P['wall']; dp = P.get('edepth', 0.7); e = P.get('epier', 0.35); EW = P.get('ewall', W)
    sill = P.get('sill', 0.85); wh = P.get('wh', 1.45)
    mb.wall([(e, 0, bw - e, fh)], W)
    h = mb.window(e + 0.25, sill, bw - e - 0.25, sill + wh, EW, nx=P.get('enx', 3), fmat=P.get('frame', WHITE), d=dp)
    mb.wall([h], EW, d=dp, u0=e, u1=bw - e)
    if P.get('epanel'): mb.q(e + 0.25, 0.15, bw - e - 0.25, sill - 0.1, dp + 0.01, P['epanel'])
    mb.tile(0, 0, e, fh, 0); mb.tile(e, 0, bw - e, fh, dp); mb.tile(bw - e, 0, bw, fh, 0)
    mb.s3q([(e, 0, 0), (e, 0, dp), (e, fh, dp), (e, fh, 0)], EW, 0.6); mb.s3q([(bw - e, 0, dp), (bw - e, 0, 0), (bw - e, fh, 0), (bw - e, fh, dp)], EW, 0.6)
    mb.s3q([(e, 0, 0), (bw - e, 0, 0), (bw - e, 0, dp), (e, 0, dp)], EW, 0.4)
    mb.s3q([(e, fh, dp), (bw - e, fh, dp), (bw - e, fh, 0), (e, fh, 0)], EW, 0.4)

def m_shop(mb, col, P):
    """ground floor: plinth, big glazing, fascia"""
    bw, fh = mb.bw, mb.fh; W = P.get('gwall', P['wall']); pl = P.get('plinth', DARK); fas = P.get('fascia', W); fh0 = fh - P.get('fasc_h', 0.7)
    e = P.get('gpier', 0.3)
    if col == 'N': mb.wall([], W); mb.q(0, 0, bw, 0.35, 0.01, pl); return
    if col == 'D':
        h = mb.window(e, 0.05, bw - e, fh0, W, r=0.25, nx=2, fmat=P.get('gframe', DARK), glass=GLASS, curt=0)
    else:
        h = mb.window(e, 0.45, bw - e, fh0, W, r=0.12, nx=P.get('gnx', 2), fmat=P.get('gframe', DARK), glass=P.get('gglass'), curt=0)
    mb.wall([h, (0, fh0, bw, fh), (0, 0, bw, 0.4)] if col != 'D' else [h, (0, fh0, bw, fh)], W)
    if col != 'D': mb.q(0, 0, bw, 0.4, 0.01, pl)
    mb.q(0, fh0, bw, fh, 0.0, fas)
    if P.get('sign') and mb.rnd.random() < 0.7:
        sc = mb.rnd.choice(P['sign']); mb.prot(0.5, fh0 + 0.12, bw - 0.5, fh - 0.12, 0.05, sc)
    if P.get('canopy'):
        mb.s3box(0, fh0 - 0.02, bw, fh0 + 0.14, 0, P['canopy'], P.get('canopy_mat', DARK), dens=0.5)

MODS = dict(plain=m_plain, punched=m_punched, ribbon=m_ribbon, raster=m_raster, vraster=m_vraster, loggia=m_loggia, erker=m_erker, shop=m_shop)

# ---------------------------------------------------------------- geometry collectors
class Zone:
    def __init__(s, name, ids):
        s.name = name; s.ids = ids
        xs = []; ys = []
        for i in ids:
            for p in poly(i)[0]: xs.append(p[0]); ys.append(p[1])
        s.cx = round((min(xs) + max(xs)) / 2, 1); s.cy = round((min(ys) + max(ys)) / 2, 1)
        s.bbox = (min(xs), min(ys), max(xs), max(ys))
        s.rects = []          # (w, h, dens)
        s.hi = []             # (pts world, mat)
        s.lo = []             # (pts world, rect, flip)
        s.s3rep = []          # (pts world, mat, rect)
        s.s3copy = []         # (pts world, mat)
        s.exp = []            # (pts world, rect)   quads / tris with explicit uv01 inside the rect
    def rect(s, w, h, dens=1.0):
        s.rects.append((max(w, 0.05), max(h, 0.05), dens)); return len(s.rects) - 1

def offset(pts, d):
    """offset a CCW polygon outwards by d (mitred)"""
    n = len(pts); out = []
    for i in range(n):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]
        e1 = Vector((p1[0] - p0[0], p1[1] - p0[1])); e2 = Vector((p2[0] - p1[0], p2[1] - p1[1]))
        if e1.length < 1e-6 or e2.length < 1e-6: out.append(p1); continue
        e1.normalize(); e2.normalize(); n1 = Vector((e1.y, -e1.x)); n2 = Vector((e2.y, -e2.x))
        k = 1 + n1.dot(n2); k = max(k, 0.35)
        m = (n1 + n2) / k
        out.append((p1[0] + m.x * d, p1[1] + m.y * d))
    return out

def unit01(pts3):
    """planar unwrap of a polygon into the unit square; returns uv list, width, height"""
    p = [Vector(q) for q in pts3]
    nrm = Vector((0, 0, 0))
    for i in range(len(p)): a, b = p[i], p[(i + 1) % len(p)]; nrm += Vector(((a.y - b.y) * (a.z + b.z), (a.z - b.z) * (a.x + b.x), (a.x - b.x) * (a.y + b.y)))
    if nrm.length < 1e-9: nrm = Vector((0, 0, 1))
    nrm.normalize()
    ex = None
    if abs(nrm.z) < 0.999:
        ex = Vector((-nrm.y, nrm.x, 0)).normalized()        # horizontal axis
    else:
        best = 0
        for i in range(len(p)):
            e = p[(i + 1) % len(p)] - p[i]
            if e.length > best: best = e.length; ex = e.normalized()
    ey = nrm.cross(ex)
    us = [q.dot(ex) for q in p]; vs = [q.dot(ey) for q in p]
    u0, v0 = min(us), min(vs); w, h = max(max(us) - u0, 1e-3), max(max(vs) - v0, 1e-3)
    return [((u - u0) / w, (v - v0) / h) for u, v in zip(us, vs)], w, h

def add_solid(Z, pts3, mat, dens=1.0):
    """unique real-geometry polygon (roofs, gables, cornices)"""
    uv, w, h = unit01(pts3); r = Z.rect(w, h, dens)
    if len(pts3) <= 4:
        Z.s3rep.append((pts3, mat, r, uv)); Z.exp.append((pts3, r, uv))
    else:
        tris = tessellate_polygon([[Vector(q) for q in pts3]])
        for t in tris:
            tp = [pts3[k] for k in t]; tu = [uv[k] for k in t]
            Z.s3rep.append((tp, mat, r, tu)); Z.exp.append((tp, r, tu))

Q01 = [(0, 0), (1, 0), (1, 1), (0, 1)]

def build_wall(Z, p, q, z0, z1, layout, P, seed, bid):
    """layout: dict(bw, rows=[(height, modname, rowkey)], cols=fn(c, nb)->colkey)"""
    dx, dy = q[0] - p[0], q[1] - p[1]; L = math.hypot(dx, dy)
    if L < 0.05: return
    t = (dx / L, dy / L); n = (t[1], -t[0])
    W = lambda u, v, d, uo=0, vo=0: (p[0] + t[0] * (u + uo) + n[0] * d - Z.cx, p[1] + t[1] * (u + uo) + n[1] * d - Z.cy, z0 + v + vo)
    rows = layout['rows']; tot = sum(r[0] for r in rows); sc = (z1 - z0) / tot
    nb = max(1, round(L / layout['bw'])); bw = L / nb
    if L < 2.6 or layout.get('plain'):
        rows = [(tot, 'plain', 'P')]; nb = 1; bw = L
    cols = [layout['cols'](c, nb) if not (L < 2.6 or layout.get('plain')) else 'W' for c in range(nb)]
    v = 0
    for ri, (rh, mod, rkey) in enumerate(rows):
        fh = rh * sc
        groups = {}
        for c, ck in enumerate(cols): groups.setdefault(ck if mod != 'plain' else 'W', []).append(c)
        for ck, cs in groups.items():
            rep = min(cs, key=lambda c: abs(c - (nb - 1) / 2) + (0.01 * c))
            Pm = dict(P); Pm.update(layout.get('P', {})); Pm.update(layout.get('rowP', {}).get(rkey, {}))
            mname = Pm.get('colmod', {}).get(ck, mod) if mod not in ('shop', 'plain') else mod
            mb = MB(bw, fh, seed * 131 + ri * 17 + hash(ck) % 97)
            MODS[mname](mb, ck, Pm)
            tiles = mb.tiles or [(0, 0, bw, fh, 0)]
            dens = 0.25 if mname == 'plain' else 1.0
            trects = [Z.rect(tl[2] - tl[0], tl[3] - tl[1], dens if mname != 'plain' else min(1, 6 / max(bw, fh))) for tl in tiles]
            srects = []
            for pts, mat, dn in mb.s3:
                a = Vector(pts[1]) - Vector(pts[0]); b = Vector(pts[3]) - Vector(pts[0]); srects.append(Z.rect(a.length, b.length, dn))
            for c in cs:
                uo = c * bw
                for tl, r in zip(tiles, trects):
                    quad = [W(tl[0], tl[1], tl[4], uo, v), W(tl[2], tl[1], tl[4], uo, v), W(tl[2], tl[3], tl[4], uo, v), W(tl[0], tl[3], tl[4], uo, v)]
                    Z.exp.append((quad, r, Q01))
                    if c == rep: Z.lo.append((quad, r, Q01))
                for (pts, mat, dn), r in zip(mb.s3, srects):
                    quad = [W(a, b, d, uo, v) for a, b, d in pts]
                    Z.exp.append((quad, r, Q01))
                    if c == rep: Z.s3rep.append((quad, mat, r, Q01))
                    else: Z.s3copy.append((quad, mat))
                if c == rep:
                    for pts, mat in mb.hi: Z.hi.append(([W(a, b, d, uo, v) for a, b, d in pts], mat))
                else:
                    Z.hi.append(([W(0, 0, 0, uo, v), W(bw, 0, 0, uo, v), W(bw, fh, 0, uo, v), W(0, fh, 0, uo, v)], P['wall']))
        v += fh

def gdir(n):
    """wall direction in the street-grid frame: 'N','E','S','W'"""
    c, s = math.cos(GRID), math.sin(GRID); u = n[0] * c + n[1] * s; v = -n[0] * s + n[1] * c
    return ('E' if u > 0 else 'W') if abs(u) > abs(v) else ('N' if v > 0 else 'S')

def obb(pts):
    best = None
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]; L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L < 1.5: continue
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        us = [q[0] * ux + q[1] * uy for q in pts]; vs = [-q[0] * uy + q[1] * ux for q in pts]
        ar = (max(us) - min(us)) * (max(vs) - min(vs))
        if best is None or ar < best[0]:
            cu, cv = (max(us) + min(us)) / 2, (max(vs) + min(vs)) / 2
            best = (ar, ux, uy, (max(us) - min(us)) / 2, (max(vs) - min(vs)) / 2, cu * ux - cv * uy, cu * uy + cv * ux)
    ar, ux, uy, a, b, cx, cy = best
    if a < b: ux, uy, a, b = -uy, ux, b, a
    return ux, uy, a, b, cx, cy

def build_roof(Z, pts, h, R, P):
    kind = R.get('kind'); L = lambda x, y, z: (x - Z.cx, y - Z.cy, z)
    rm = R.get('mat', M('#5a5f63', 0.6))
    if kind == 'flat':
        add_solid(Z, [L(x, y, h + 0.02) for x, y in pts], rm, 0.25)
    elif kind == 'hip':
        ov = R.get('ov', 0.4); ins = R['inset']; rise = R['rise']
        o = offset(pts, ov); i_ = offset(pts, -ins); n = len(pts)
        for k in range(n):
            a, b, c, d = o[k], o[(k + 1) % n], i_[(k + 1) % n], i_[k]
            if math.hypot(b[0] - a[0], b[1] - a[1]) < 0.05: continue
            add_solid(Z, [L(a[0], a[1], h), L(b[0], b[1], h), L(c[0], c[1], h + rise), L(d[0], d[1], h + rise)], rm, 0.6)
        add_solid(Z, [L(x, y, h + rise) for x, y in i_], R.get('topmat', rm), 0.25)
    elif kind == 'gable':
        ux, uy, a, b, cx, cy = obb(pts); ov = R.get('ov', 0.4); rise = R.get('rise', b * 0.8); vx, vy = -uy, ux
        Pt = lambda su, sv, e, z: L(cx + ux * su * (a + e) + vx * sv * (b + e), cy + uy * su * (a + e) + vy * sv * (b + e), z)
        add_solid(Z, [Pt(-1, -1, ov, h), Pt(1, -1, ov, h), Pt(1, 0, ov, h + rise), Pt(-1, 0, ov, h + rise)], rm, 0.6)
        add_solid(Z, [Pt(1, 1, ov, h), Pt(-1, 1, ov, h), Pt(-1, 0, ov, h + rise), Pt(1, 0, ov, h + rise)], rm, 0.6)
        for su in (-1, 1):
            add_solid(Z, [Pt(su, -su, 0, h), Pt(su, su, 0, h), Pt(su, 0, 0, h + rise)], P['wall'], 0.5)
    if R.get('pent'):                                    # set-back attic / plant room
        ins, ph = R['pent']; i_ = offset(pts, -ins); n = len(i_); pm = R.get('pentmat', P['wall'])
        for k in range(n):
            a, b = i_[k], i_[(k + 1) % n]
            if math.hypot(b[0] - a[0], b[1] - a[1]) < 0.05: continue
            add_solid(Z, [L(a[0], a[1], h), L(b[0], b[1], h), L(b[0], b[1], h + ph), L(a[0], a[1], h + ph)], pm, 0.4)
        add_solid(Z, [L(x, y, h + ph) for x, y in i_], rm, 0.2)

def build_building(Z, i, spec):
    pts, area = poly(i); h = spec.get('h', B[i]['h']); P = spec['P']
    n = len(pts)
    for k in range(n):
        p, q = pts[k], pts[(k + 1) % n]; dx, dy = q[0] - p[0], q[1] - p[1]; L = math.hypot(dx, dy)
        if L < 0.05: continue
        d = gdir((dy / L, -dx / L))
        lay = spec.get('walls', {}).get(k) or spec.get('dirs', {}).get(d) or spec['layout']
        if isinstance(lay, tuple):                      # (layout, min length) -> fall back to the default for short walls
            lay = lay[0] if L >= lay[1] else spec['layout']
        build_wall(Z, p, q, 0, h, lay, P, i * 31 + k, i)
    # massing cap for shadows + optional roof
    Z.hi.append(([(x - Z.cx, y - Z.cy, h - 0.01) for x, y in pts], P['wall']))
    if spec.get('cornice'):
        cw, ch, cm = spec['cornice']
        o = offset(pts, cw)
        for k in range(n):
            a, b, c, d = pts[k], pts[(k + 1) % n], o[(k + 1) % n], o[k]
            if math.hypot(b[0] - a[0], b[1] - a[1]) < 0.3: continue
            Lc = lambda x, y, z: (x - Z.cx, y - Z.cy, z)
            add_solid(Z, [Lc(d[0], d[1], h - ch), Lc(c[0], c[1], h - ch), Lc(c[0], c[1], h + 0.05), Lc(d[0], d[1], h + 0.05)], cm, 0.4)
            add_solid(Z, [Lc(a[0], a[1], h - ch), Lc(b[0], b[1], h - ch), Lc(c[0], c[1], h - ch), Lc(d[0], d[1], h - ch)], cm, 0.3)
            add_solid(Z, [Lc(d[0], d[1], h + 0.05), Lc(c[0], c[1], h + 0.05), Lc(b[0], b[1], h + 0.05), Lc(a[0], a[1], h + 0.05)], cm, 0.3)
    if spec.get('roof'): build_roof(Z, pts, h, spec['roof'], P)
    for extra in spec.get('extra', []): extra(Z, pts, h, P)

def context(Z, margin=70):
    """neighbouring buildings as plain boxes so that they cast shadows; ground plane"""
    x0, y0, x1, y1 = Z.bbox; ids = set(Z.ids); g = M((0.22, 0.22, 0.22))
    for i in range(len(B)):
        if i in ids: continue
        pts, a = poly(i); c = cen(pts)
        if not (x0 - margin < c[0] < x1 + margin and y0 - margin < c[1] < y1 + margin): continue
        h = B[i]['h']; n = len(pts)
        for k in range(n):
            p, q = pts[k], pts[(k + 1) % n]
            Z.hi.append(([(p[0] - Z.cx, p[1] - Z.cy, 0), (q[0] - Z.cx, q[1] - Z.cy, 0), (q[0] - Z.cx, q[1] - Z.cy, h), (p[0] - Z.cx, p[1] - Z.cy, h)], M('#b5b0a6')))
        Z.hi.append(([(x - Z.cx, y - Z.cy, h) for x, y in pts], M('#55585c')))
    s = 400
    Z.hi.append(([(-s, -s, -0.02), (s, -s, -0.02), (s, s, -0.02), (-s, s, -0.02)], g))

# ---------------------------------------------------------------- atlas
def pack(Z):
    rs = Z.rects; PAD = 2
    def attempt(s):
        items = sorted(((max(3, round(w * s * d)), max(3, round(h * s * d)), i) for i, (w, h, d) in enumerate(rs)), key=lambda t: -t[1])
        x = y = 0; sh = 0; out = [None] * len(rs)
        for w, h, i in items:
            w = min(w, ATLAS - 2 * PAD)
            if x + w + 2 * PAD > ATLAS: x = 0; y += sh; sh = 0
            if y + h + 2 * PAD > ATLAS: return None
            out[i] = (x + PAD, y + PAD, w, h); x += w + 2 * PAD; sh = max(sh, h + 2 * PAD)
        return out
    lo, hi = 1.0, 80.0; best = None
    for _ in range(18):
        mid = (lo + hi) / 2; r = attempt(mid)
        if r: best, lo = r, mid
        else: hi = mid
    print('atlas scale px/m', round(lo, 1), 'rects', len(rs)); Z.px = best; Z.scale = lo

def uvof(Z, r, uv01):
    x, y, w, h = Z.px[r]
    return [((x + 0.5 + u * (w - 1)) / ATLAS, (y + 0.5 + v * (h - 1)) / ATLAS) for u, v in uv01]

# ---------------------------------------------------------------- blender objects
def mkobj(name, faces, uvs=None, mats=None):
    verts = []; fs = []
    for f in faces:
        b = len(verts); verts.extend(f); fs.append(list(range(b, b + len(f))))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], fs); me.update()
    if uvs is not None:
        l = me.uv_layers.new(name='UVMap'); k = 0
        for f in uvs:
            for uv in f: l.data[k].uv = uv; k += 1
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    if mats is not None:
        keys = []; idx = {}
        for m in mats:
            if m not in idx: idx[m] = len(keys); keys.append(m)
        for k in keys: me.materials.append(bmat(k))
        me.polygons.foreach_set('material_index', [idx[m] for m in mats])
    return ob

def bake_zone(Z, outdir, samples=24, sun_az=118, sun_el=38):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for k in list(_mats): _mats[k] = None
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = samples; sc.cycles.use_denoising = False
    sc.cycles.max_bounces = 3; sc.cycles.diffuse_bounces = 2; sc.cycles.glossy_bounces = 2; sc.cycles.use_adaptive_sampling = False
    try: sc.cycles.sample_clamp_indirect = 3.0
    except Exception: pass
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (0.62, 0.76, 1.0, 1); bg.inputs[1].default_value = 0.62
    sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 1.55; sun.angle = math.radians(3); sun.color = (1.0, 0.95, 0.86)
    so = bpy.data.objects.new('sun', sun); sc.collection.objects.link(so)
    az, el = math.radians(sun_az), math.radians(sun_el)
    d = -Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    so.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    img = bpy.data.images.new('bake', ATLAS, ATLAS, alpha=False); img.generated_color = (0.5, 0.5, 0.5, 1)
    def imgnode(mat):
        nt = mat.node_tree; n = nt.nodes.new('ShaderNodeTexImage'); n.image = img; nt.nodes.active = n; n.select = True; return n
    hi = mkobj('hi', [f[0] for f in Z.hi], mats=[f[1] for f in Z.hi])
    s3c = mkobj('s3copy', [f[0] for f in Z.s3copy], mats=[f[1] for f in Z.s3copy]) if Z.s3copy else None
    s3r = mkobj('s3rep', [f[0] for f in Z.s3rep], uvs=[uvof(Z, f[2], f[3]) for f in Z.s3rep], mats=[f[1] for f in Z.s3rep]) if Z.s3rep else None
    lo = mkobj('lo', [f[0] for f in Z.lo], uvs=[uvof(Z, f[1], f[2]) for f in Z.lo])
    bm = bpy.data.materials.new('bakemat'); bm.use_nodes = True; imgnode(bm); lo.data.materials.append(bm)
    for m in bpy.data.materials:
        if m is not bm: imgnode(m)
    bk = sc.render.bake; bk.margin = 2; bk.use_clear = False
    try: bk.margin_type = 'EXTEND'
    except Exception: pass
    # pass A: facade tiles, selected-to-active
    bpy.ops.object.select_all(action='DESELECT'); hi.select_set(True); lo.select_set(True); bpy.context.view_layer.objects.active = lo
    bk.use_selected_to_active = True; bk.cage_extrusion = 0.34; bk.max_ray_distance = 2.2
    lo.visible_shadow = False; lo.visible_diffuse = False; lo.visible_glossy = False; lo.visible_camera = False; lo.visible_transmission = False
    bpy.ops.object.bake(type='COMBINED')
    # pass B: real geometry
    if s3r:
        lo.hide_render = True
        bpy.ops.object.select_all(action='DESELECT'); s3r.select_set(True); bpy.context.view_layer.objects.active = s3r
        bk.use_selected_to_active = False
        bpy.ops.object.bake(type='COMBINED')
    png = os.path.join(outdir, Z.name + '_bake.png'); img.filepath_raw = png; img.file_format = 'PNG'; img.save()
    # export mesh
    for o in list(sc.collection.objects): bpy.data.objects.remove(o, do_unlink=True)
    ex = mkobj('m', [f[0] for f in Z.exp], uvs=[uvof(Z, f[1], f[2]) for f in Z.exp])
    em = bpy.data.materials.new('baked'); em.use_nodes = True; em.use_backface_culling = False
    n = em.node_tree.nodes.new('ShaderNodeTexImage'); n.image = bpy.data.images.load(png)
    b = em.node_tree.nodes['Principled BSDF']; em.node_tree.links.new(n.outputs[0], b.inputs['Base Color'])
    ex.data.materials.append(em)
    bpy.ops.object.select_all(action='DESELECT'); ex.select_set(True); bpy.context.view_layer.objects.active = ex
    bpy.ops.object.shade_flat()
    glb = os.path.join(outdir, Z.name + '.glb')
    bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=True, export_image_format='JPEG', export_jpeg_quality=88, export_yup=True, export_apply=True)
    b64 = base64.b64encode(open(glb, 'rb').read()).decode()
    open(os.path.join(outdir, 'bl_' + Z.name + '.js'), 'w').write('export const x = %s, y = %s, roof = %s;\nexport default "%s";\n' % (Z.cx, Z.cy, 'true' if getattr(Z, 'roofflag', True) else 'false', b64))
    print('DONE', Z.name, 'verts', len(ex.data.vertices), 'glb MB', round(os.path.getsize(glb) / 1e6, 2))
