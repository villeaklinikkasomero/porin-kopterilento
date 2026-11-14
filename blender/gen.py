"""Pori centre blocks -> Blender -> baked GLB.
One bay x one storey of every facade is modelled in detail and baked (selected-to-active) onto a flat tile;
the tile is repeated along the wall. Balconies, bay windows and roofs are real geometry baked directly."""
import bpy, math, sys, os, random, base64
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
sys.path.insert(0, '/home/claude')
from lib_city import B, poly, cen

GRID = math.radians(-13.035)
ATLAS = int(os.environ.get('PORI_ATLAS', '2048'))   # 4096 on the GPU (city run)

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

# ---------------------------------------------------------------- CC0 surface detail (Poly Haven, CC0): brick, render, concrete, wood cladding
# The building's own colour stays; the photo texture only adds its pattern (mortar joints, render grain, board edges), projected on all
# faces from the object coordinates (box mapping), so it needs no UVs.  Folder: blender/tex (or PORI_TEX).
TEXDIR = next((d for d in (os.environ.get('PORI_TEX', ''), '/home/claude/tex', '/repo/blender/tex', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tex')) if d and os.path.isdir(d)), None)
TEXF = dict(brick=('red_brick_03_diff_2k.jpg', 2.2, 0.9, (0.157, 0.102, 0.085)), plaster=('plastered_wall_02_diff_2k.jpg', 2.5, 0.55, (0.494, 0.44, 0.369)),
            concrete=('concrete_wall_008_diff_2k.jpg', 3.0, 0.6, (0.266, 0.237, 0.162)), wood=('exterior_wall_cladding_diff_2k.jpg', 2.0, 0.7, (0.199, 0.175, 0.147)))
DETAIL = {}
def MT(col, kind, rough=0.85, metal=0.0):
    """material key with a surface pattern: kind in brick / plaster / concrete / wood / None"""
    k = M(col, rough, metal); DETAIL[k] = kind; return k

SURF = os.environ.get('PORI_SURF', '')                    # 'plaster': rendered walls get an even, faint render grain (brick and wood stay as they are)
SURF_K = float(os.environ.get('PORI_SURF_STRENGTH', '0.3'))
def detail_kind(k):
    r, g, b, rough, metal = k
    if k in DETAIL: return DETAIL[k]
    if metal > 0.2 or rough < 0.6: return None                      # glass, metal, polished stone
    mx, mn = max(r, g, b), min(r, g, b); lum = 0.3 * r + 0.59 * g + 0.11 * b
    if r > 2.3 * g and r > 0.06 and lum < 0.19: return 'brick'          # dark red-brown walls read as brick (salmon and pink render stays render)
    if mx - mn < 0.035 * max(mx, 0.05) * 10 and 0.08 < lum < 0.45: return 'concrete'   # unsaturated mid greys: precast concrete
    if lum > 0.12: return 'plaster'
    return None

WOODK = ('wood', 'woodv', 'woodl')      # painted boards: weatherboard, board and batten, weatherboard drawn on a flat polygon (gables)
WEATHER = float(os.environ.get('PORI_WEATHER', '0.12'))    # splash zone: walls darken towards the ground (0 = off)
def tint(k, f):
    """the same material a shade lighter / darker (keeps its surface pattern)"""
    k2 = M((k[0] * f, k[1] * f, k[2] * f), k[3], k[4])
    if k in DETAIL: DETAIL[k2] = DETAIL[k]
    return k2
_texcache = {}
def bmat(k):
    if _mats[k] is None:
        m = bpy.data.materials.new('m%d' % len(bpy.data.materials)); m.use_nodes = True
        nt = m.node_tree; b = nt.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value = (k[0], k[1], k[2], 1); b.inputs['Roughness'].default_value = k[3]; b.inputs['Metallic'].default_value = k[4]
        kind = detail_kind(k)
        if kind and not TEXDIR and kind not in WOODK: kind = None
        col = None
        if kind in WOODK:
            # painted boards: no photo (the old cladding photo read as brickwork); fine streaks along the board and soft paint patches
            tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping')
            mp.inputs['Scale'].default_value = (38.0, 38.0, 1.1) if kind == 'woodv' else (1.3, 1.3, 55.0)
            nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 1.0; nz.inputs['Detail'].default_value = 3.0
            nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], nz.inputs['Vector'])
            r1 = nt.nodes.new('ShaderNodeMapRange'); r1.inputs[1].default_value = 0.3; r1.inputs[2].default_value = 0.7; r1.inputs[3].default_value = 0.9; r1.inputs[4].default_value = 1.06
            nt.links.new(nz.outputs[0], r1.inputs[0])
            n2 = nt.nodes.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 0.9; n2.inputs['Detail'].default_value = 2.0
            nt.links.new(tc.outputs['Object'], n2.inputs['Vector'])
            r2 = nt.nodes.new('ShaderNodeMapRange'); r2.inputs[1].default_value = 0.3; r2.inputs[2].default_value = 0.7; r2.inputs[3].default_value = 0.95; r2.inputs[4].default_value = 1.04
            nt.links.new(n2.outputs[0], r2.inputs[0])
            mu = nt.nodes.new('ShaderNodeMath'); mu.operation = 'MULTIPLY'; nt.links.new(r1.outputs[0], mu.inputs[0]); nt.links.new(r2.outputs[0], mu.inputs[1])
            val = mu.outputs[0]
            if kind == 'woodl':                         # gables are flat polygons: the weatherboards are drawn (a shade ramp per board, a dark line under it)
                sz = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sz.inputs[0])
                fr = nt.nodes.new('ShaderNodeMath'); fr.operation = 'FRACT'; dv = nt.nodes.new('ShaderNodeMath'); dv.operation = 'DIVIDE'; dv.inputs[1].default_value = 0.15
                nt.links.new(sz.outputs['Z'], dv.inputs[0]); nt.links.new(dv.outputs[0], fr.inputs[0])
                cr = nt.nodes.new('ShaderNodeValToRGB'); e_ = cr.color_ramp.elements
                e_[0].position = 0.0; e_[0].color = (0.5, 0.5, 0.5, 1); e_[1].position = 0.1; e_[1].color = (1.03, 1.03, 1.03, 1)
                e2 = e_.new(1.0); e2.color = (0.94, 0.94, 0.94, 1); cr.color_ramp.interpolation = 'LINEAR'
                nt.links.new(fr.outputs[0], cr.inputs[0])
                m3 = nt.nodes.new('ShaderNodeMath'); m3.operation = 'MULTIPLY'; nt.links.new(val, m3.inputs[0]); nt.links.new(cr.outputs['Color'], m3.inputs[1]); val = m3.outputs[0]
            mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs['Factor'].default_value = 1.0
            mx.inputs[6].default_value = (k[0], k[1], k[2], 1); nt.links.new(val, mx.inputs[7]); col = mx.outputs[2]
        elif kind:
            fn, size, strength, mean = TEXF[kind]
            if SURF and kind == SURF: strength = SURF_K
            if fn not in _texcache: _texcache[fn] = bpy.data.images.load(os.path.join(TEXDIR, fn))
            tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1 / size, 1 / size, 1 / size)
            tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = _texcache[fn]; tx.projection = 'BOX'; tx.projection_blend = 0.25
            nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], tx.inputs['Vector'])
            sc = nt.nodes.new('ShaderNodeVectorMath'); sc.operation = 'MULTIPLY'; sc.inputs[1].default_value = tuple(1 / max(c, 1e-3) for c in mean)
            nt.links.new(tx.outputs['Color'], sc.inputs[0])
            mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs['Factor'].default_value = strength
            mx.inputs[6].default_value = (k[0], k[1], k[2], 1); nt.links.new(sc.outputs['Vector'], mx.inputs[7]); col = mx.outputs[2]
        if kind and WEATHER > 0:
            # rain splash and dust: the wall is a little darker just above the ground, fading out by 1.7 m (height only, so bays still tile)
            tc2 = nt.nodes.new('ShaderNodeTexCoord'); sp = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc2.outputs['Object'], sp.inputs[0])
            rz = nt.nodes.new('ShaderNodeMapRange'); rz.interpolation_type = 'SMOOTHSTEP'
            rz.inputs[1].default_value = 0.25; rz.inputs[2].default_value = 1.7; rz.inputs[3].default_value = 1.0 - WEATHER; rz.inputs[4].default_value = 1.0
            nt.links.new(sp.outputs['Z'], rz.inputs[0])
            mw = nt.nodes.new('ShaderNodeMix'); mw.data_type = 'RGBA'; mw.blend_type = 'MULTIPLY'; mw.inputs['Factor'].default_value = 1.0
            if col is not None: nt.links.new(col, mw.inputs[6])
            else: mw.inputs[6].default_value = (k[0], k[1], k[2], 1)
            nt.links.new(rz.outputs[0], mw.inputs[7]); col = mw.outputs[2]
        if col is not None: nt.links.new(col, b.inputs['Base Color'])
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
    elif col == 'B' and not P.get('proj_balcony'):
        # Pori: balconies are as a rule recessed into the facade (loggias), mostly glazed: a hole the width of the window and its door,
        # side walls in the facade colour, the back wall with a door and a window, a railing panel and slim glazing frames in front
        b0, b1 = max(0.2, bw / 2 - ww / 2 - 0.45), min(bw - 0.2, bw / 2 + ww / 2 + 0.45); dp = P.get('ldepth', 1.3); hole = (b0, 0.12, b1, fh - 0.22)
        mb.wall([hole], W)
        mb.sides(hole[0], hole[1], hole[2], hole[3], 0, -dp, P.get('linner', W))
        saved = mb.hi; mb.hi = []
        h1 = mb.window(hole[0] + 0.25, hole[1], hole[0] + 1.05, hole[1] + 2.1, W, r=0.08, curt=0, fmat=P.get('frame', WHITE))
        h2 = mb.window(hole[0] + 1.25, hole[1] + 0.8, hole[2] - 0.25, hole[1] + 2.1, W, r=0.08, nx=2, fmat=P.get('frame', WHITE)) if hole[2] - hole[0] > 2.3 else None
        mb.wall([h for h in (h1, h2) if h], P.get('linner', W), u0=hole[0], u1=hole[2], v0=hole[1], v1=hole[3])
        back = [([(q[0], q[1], q[2] - dp) for q in pts], m) for pts, m in mb.hi]; mb.hi = saved + back
        rail = P.get('rail', WHITE); mb.q(hole[0], hole[1], hole[2], hole[1] + 1.0, -0.05, rail)              # railing panel
        if P.get('glazed', True):                                                                         # balcony glazing: frames over the opening
            gl = M((0.55, 0.62, 0.66), 0.1); mb.q(hole[0], hole[1] + 1.0, hole[2], hole[3], -0.04, gl)
            nm = max(2, int((hole[2] - hole[0]) / 0.7))
            for k in range(1, nm): u = hole[0] + (hole[2] - hole[0]) * k / nm; mb.q(u - 0.02, hole[1] + 1.0, u + 0.02, hole[3], -0.03, P.get('frame', WHITE))
            mb.q(hole[0], hole[1] + 0.98, hole[2], hole[1] + 1.04, -0.03, P.get('frame', WHITE))
        return
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
    h = mb.window(e + sp_w, sill, bw - e, sill + wh, W, r=0.1, nx=P.get('nx', 2), fmat=P.get('frame', WHITE), glass=P.get('wglass'))
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

def shop_keys(cols):
    """shopfront bays in pairs: a pier only on the outer side of each pair, so the glass runs across two bays (about four of the
    old pier-and-mullion spacings); 'S<pier left><pier right>'.  Blank ('N') and door ('D') bays stay as they are and end a pair."""
    out = []; run = 0
    for c, ck in enumerate(cols):
        if ck in ('N', 'D'): out.append(ck); run = 0; continue
        nxt = c + 1 < len(cols) and cols[c + 1] not in ('N', 'D')
        out.append('S%d%d' % (run % 2 == 0, run % 2 == 1 or not nxt)); run += 1
    return out

SHOP_LO = M('#363e44', 0.1); SHOP_HI = M('#75828b', 0.1)                       # shop glass: darker below, the street and sky reflected above
SHOP_IN = [M('#d9d2c2'), M('#b79c78'), M('#8f969b'), M('#e9e4da'), M('#6d5a4a'), M('#a8b3b6')]   # lit shelves, displays, posters behind the glass
def shop_glass(mb, u0, u1, v0, v1, r):
    """a shop window that reads as glass in daylight: the old single dark sheet looked like a closed garage door (Street View, 13.11.2026).
    The upper third mirrors the bright street, the lower part shows the lit interior: a few pale displays standing behind the glass."""
    vs = v0 + (v1 - v0) * 0.64
    mb.q(u0, v0, u1, vs, -r, SHOP_LO); mb.q(u0, vs, u1, v1, -r, SHOP_HI)
    w = u1 - u0; k = mb.rnd.randrange(9973)
    n = 1 + (k % 3); x = u0 + 0.25
    for j in range(n):
        dw = min(w / n - 0.3, 0.8 + ((k >> (2 * j)) % 5) * 0.2)
        if dw < 0.3: break
        top = v0 + 1.3 + ((k >> (3 + j)) % 4) * 0.3
        mb.q(x, v0 + 0.15, x + dw, min(top, vs - 0.05), -r + 0.004, SHOP_IN[(k + j * 5) % len(SHOP_IN)])
        x += w / n

def m_shop(mb, col, P):
    """ground floor: low plinth, wide glazing, fascia.  col: 'N' blank, 'D' door, 'S11' / 'S10' / 'S01' / 'S00' glazing with a pier on
    the left / right side or running on into the next bay (shop_keys); anything else: a single bay between two piers"""
    bw, fh = mb.bw, mb.fh; W = P.get('gwall', P['wall']); pl = P.get('plinth', DARK); fas = P.get('fascia', W); fh0 = fh - P.get('fasc_h', 0.7)
    e = P.get('gpier', 0.3); fm = P.get('gframe', DARK); ph = 0.25
    if col == 'N': mb.wall([], W); mb.q(0, 0, bw, 0.35, 0.01, pl); return
    if col == 'D':
        h = mb.window(e, 0.05, bw - e, fh0, W, r=0.25, nx=2, fmat=fm, glass=GLASS, curt=0)
        mb.wall([h, (0, fh0, bw, fh)], W)
    else:
        pL, pR = (col[1] == '1', col[2] == '1') if len(col) == 3 and col[0] == 'S' else (True, True)
        u0 = e if pL else 0.0; u1 = bw - e if pR else bw; r = 0.12; fr = 0.06; jt = 0.015; gl = P.get('gglass') or GLASS
        if P.get('gglass'): mb.q(u0, ph, u1, fh0, -r, gl)                                       # one sheet of glass, no mullion
        else: shop_glass(mb, u0, u1, ph, fh0, r)
        mb.q(u0, ph, u1, ph + fr, -r + 0.02, fm); mb.q(u0, fh0 - fr, u1, fh0, -r + 0.02, fm)     # bottom and head frame
        for side, u in ((pL, u0), (pR, u1)):                                                     # frame at a pier, a thin glazing joint where the glass runs on
            wdt = fr if side else jt; a_, b_ = (u, u + wdt) if u == u0 else (u - wdt, u)
            mb.q(a_, ph + fr, b_, fh0 - fr, -r + 0.02, fm)
            if side: mb.hq([(u, ph, 0), (u, ph, -r), (u, fh0, -r), (u, fh0, 0)], W)              # reveal of the pier
        mb.hq([(u0, ph, 0), (u1, ph, 0), (u1, ph, -r), (u0, ph, -r)], W); mb.hq([(u0, fh0, 0), (u1, fh0, 0), (u1, fh0, -r), (u0, fh0, -r)], W)
        mb.wall([(u0, ph, u1, fh0), (0, fh0, bw, fh), (0, 0, bw, ph)], W)
        mb.q(0, 0, bw, ph, 0.01, pl)
    mb.q(0, fh0, bw, fh, 0.0, fas)
    # coloured sign boards over the shop windows removed (user 13.11.2026: they did not look like Pori's shop fronts); P['sign'] is ignored
    if P.get('canopy'):
        mb.s3box(0, fh0 - 0.02, bw, fh0 + 0.14, 0, P['canopy'], P.get('canopy_mat', DARK), dens=0.5)


def _arch_top(mb, u0, u1, vs, W, fmat, r=0.14, trim=None, glass=None):
    """semicircular head over a window whose rect hole runs up to vs + rad"""
    rad = (u1 - u0) / 2; uc = (u0 + u1) / 2; N = 12
    arc = [(uc + rad * math.cos(math.pi * k / N), vs + rad * math.sin(math.pi * k / N)) for k in range(N + 1)]
    mb.hq([(u, v, -r) for u, v in arc], glass or GLASS)
    ri = rad - 0.07
    for k in range(N):
        a0, a1 = math.pi * k / N, math.pi * (k + 1) / N
        mb.hq([(uc + ri * math.cos(a0), vs + ri * math.sin(a0), -r + 0.02), (uc + rad * math.cos(a0), vs + rad * math.sin(a0), -r + 0.02),
               (uc + rad * math.cos(a1), vs + rad * math.sin(a1), -r + 0.02), (uc + ri * math.cos(a1), vs + ri * math.sin(a1), -r + 0.02)], fmat)
    top = vs + rad
    mb.hq([(u0, top, 0)] + [(u, v, 0) for u, v in arc[N:N // 2 - 1:-1]], W)          # wall in the corners above the arc
    mb.hq([(u1, top, 0)] + [(u, v, 0) for u, v in arc[N // 2::-1]], W)
    if trim:                                                                           # archivolt + keystone
        ro = rad + 0.16
        for k in range(N):
            a0, a1 = math.pi * k / N, math.pi * (k + 1) / N
            mb.hq([(uc + rad * math.cos(a0), vs + rad * math.sin(a0), 0.035), (uc + ro * math.cos(a0), vs + ro * math.sin(a0), 0.035),
                   (uc + ro * math.cos(a1), vs + ro * math.sin(a1), 0.035), (uc + rad * math.cos(a1), vs + rad * math.sin(a1), 0.035)], trim)
        mb.prot(uc - 0.12, top - 0.05, uc + 0.12, top + 0.28, 0.07, trim)
    return top

def m_classic(mb, col, P):
    """19th-century rendered stone facade bay: framed window with sill, hood (cornice / pediment) or round arch,
    optional rustication, pilasters, storey band and granite plinth.  col: 'W' window, 'D' door, 'S' shop, 'N' blank, 'P' window pair"""
    bw, fh, W = mb.bw, mb.fh, P['wall']; T = P.get('trim', WHITE); fr = P.get('frame', WHITE)
    if P.get('ground') and P.get('gwall'): W = P['gwall']        # a ground floor in its own colour (grey rusticated base under a coloured house)
    ph = P.get('plinth_h', 0)                     # granite plinth at the foot of the row (ground floor)
    ww = min(P.get('ww', 1.2), bw - 0.9); wh = P.get('wh', 2.0); sill = P.get('sill', 0.95) + ph
    if not P.get('wh_fixed'):                     # windows grow with the storey: a high ground floor or piano nobile has tall windows
        top = 0.95 if P.get('hood') else 0.6      # (user 13.11.2026: the taller lower windows were drawn the same as the upper ones)
        g_ = P.get('ground'); free = fh - sill - top
        wh = min(max(wh, free * (0.8 if g_ else 0.8)), 2.9 if g_ else 2.5)
        if g_ and free - wh > 1.0: sill += (free - wh) * 0.6     # a ground floor raised on its plinth: the extra height goes under the sill
        if wh > 2.3: ww = min(bw - 0.9, ww * min(1.2, (wh / 2.0) ** 0.5))
    wh = min(wh, fh - sill - (0.75 if P.get('hood') else 0.35))
    balc = col == 'D' and not P.get('ground') and P.get('balcony')   # door onto a projecting balcony with an iron railing (corner chamfers)
    if col == 'G' and not P.get('ground'): col = 'W'
    if col in ('D', 'S') and not P.get('ground'): col = 'W'
    if balc: sill = 0.12; wh = min(fh - 0.12 - (0.75 if P.get('hood') else 0.35), 2.7)
    if P.get('blank'): col = 'N'
    arch = P.get('arch', False); holes = []; uc = bw / 2
    wins = []
    if col == 'P' and bw > 2 * ww + 0.9: wins = [(uc - ww - 0.15, uc - 0.15), (uc + 0.15, uc + ww + 0.15)]
    elif col in ('W', 'P'): wins = [(uc - ww / 2, uc + ww / 2)]
    if col == 'D':
        dw = min(1.7, bw - 0.8); dh = min(fh - ph - 0.6, 3.2) if not arch else min(fh - ph - 0.4 - dw / 2, 2.6)
        u0, u1 = uc - dw / 2, uc + dw / 2
        mb.sides(u0, ph, u1, ph + dh, 0, -0.35, W)
        mb.q(u0, ph, u1, ph + dh, -0.35, P.get('door', M('#4a3323', 0.6)))
        mb.q(uc - 0.02, ph, uc + 0.02, ph + dh, -0.33, DARK)
        top = ph + dh
        if arch: top = _arch_top(mb, u0, u1, ph + dh, W, fr, r=0.35, trim=T)
        holes.append((u0, ph, u1, top))
        mb.prot(u0 - 0.16, ph, u0, top, 0.04, T); mb.prot(u1, ph, u1 + 0.16, top, 0.04, T)
        if not arch: mb.prot(u0 - 0.3, top, u1 + 0.3, top + 0.3, 0.12, T)
    elif col == 'G':                                                       # arched gateway into the yard: dark iron gate, dressed surround
        gw = min(3.0, bw - 0.6); u0, u1 = uc - gw / 2, uc + gw / 2; gh = min(fh - ph - 0.5 - gw / 2, 2.6)
        mb.sides(u0, ph, u1, ph + gh, 0, -0.6, W)
        mb.q(u0, ph, u1, ph + gh, -0.6, P.get('gate', M('#1f2326', 0.5)))
        for k in range(1, 9): mb.q(u0 + (u1 - u0) * k / 9 - 0.015, ph, u0 + (u1 - u0) * k / 9 + 0.015, ph + gh, -0.58, M('#3a3f43', 0.5))
        top = _arch_top(mb, u0, u1, ph + gh, W, P.get('gate', M('#1f2326', 0.5)), r=0.35, trim=T)
        holes.append((u0, ph, u1, top))
        mb.prot(u0 - 0.3, ph, u0, top, 0.08, T); mb.prot(u1, ph, u1 + 0.3, top, 0.08, T)
    elif col == 'S':
        u0, u1 = 0.35, bw - 0.35
        holes.append(mb.window(u0, ph + 0.15, u1, fh - 0.5, W, r=0.15, nx=2, fmat=P.get('sframe', DARK), glass=GLASS, curt=0))
        mb.prot(0, fh - 0.5, bw, fh - 0.1, 0.05, T)
    for u0, u1 in wins:
        if arch:
            rad = (u1 - u0) / 2; vs = sill + wh - rad
            h = mb.window(u0, sill, u1, vs, W, nx=2, ny=2 if wh > 1.6 else 1, fmat=fr)
            top = _arch_top(mb, u0, u1, vs, W, fr, trim=T if P.get('archivolt', True) else None)
            holes.append((u0, sill, u1, top))
        else:
            top = sill + wh
            holes.append(mb.window(u0, sill, u1, top, W, nx=2, ny=2 if wh > 1.5 else 1, fmat=fr))
            s_ = P.get('surround', 0.13)
            if s_:
                mb.prot(u0 - s_, sill, u0, top, 0.04, T); mb.prot(u1, sill, u1 + s_, top, 0.04, T); mb.prot(u0 - s_, top, u1 + s_, top + s_, 0.04, T)
            hood = P.get('hood')
            if hood == 'cornice':
                mb.prot(u0 - s_ - 0.06, top + s_, u1 + s_ + 0.06, top + s_ + 0.22, 0.05, T)              # frieze
                mb.prot(u0 - s_ - 0.16, top + s_ + 0.22, u1 + s_ + 0.16, top + s_ + 0.36, 0.13, T)        # cap
            elif hood == 'pediment':
                b0 = top + s_ + 0.04; a0, a1 = u0 - s_ - 0.18, u1 + s_ + 0.18; ap = b0 + min(0.55, (a1 - a0) * 0.28)
                mb.prot(a0, b0 - 0.04, a1, b0 + 0.1, 0.13, T)
                mb.hq([(a0, b0 + 0.1, 0.1), (a1, b0 + 0.1, 0.1), ((a0 + a1) / 2, ap + 0.1, 0.1)], T)
                mb.hq([(a0 + 0.22, b0 + 0.16, 0.103), (a1 - 0.22, b0 + 0.16, 0.103), ((a0 + a1) / 2, ap - 0.05, 0.103)], W)
        if balc:                                                                                 # balcony slab, brackets and a dark wrought-iron railing
            b0, b1, bd = u0 - 0.55, u1 + 0.55, P.get('bd', 0.85); dk = M('#202427', 0.5)
            mb.s3box(b0, sill - 0.2, b1, sill, 0, bd, T)
            for uu in (b0 + 0.15, b1 - 0.35): mb.s3box(uu, sill - 0.75, uu + 0.2, sill - 0.2, 0, bd * 0.7, T)
            mb.s3box(b0, sill + 0.95, b1, sill + 1.0, 0, bd, dk)
            n_ = max(4, int((b1 - b0) / 0.13))
            for k in range(n_ + 1): uu = b0 + (b1 - b0) * k / n_; mb.s3box(uu - 0.012, sill, uu + 0.012, sill + 0.95, bd - 0.03, bd, dk)
            for v_ in (sill + 0.12, sill + 0.5): mb.s3box(b0, v_, b1, v_ + 0.04, bd - 0.05, bd, dk)
            continue
        mb.prot(u0 - 0.14, sill - 0.12, u1 + 0.14, sill, 0.1, T)                                 # sill
        if P.get('apron'): mb.prot(u0 - 0.05, max(ph + 0.1, sill - 0.75), u1 + 0.05, sill - 0.16, 0.03, P.get('apron_mat', T))
    mb.wall(holes + ([(0, 0, bw, ph)] if ph else []), W)
    if P.get('dentils'):                                                                         # bracket frieze under the eave cornice
        n_ = max(2, int(bw / 0.55)); dm = P.get('dentil_mat', T)
        for k in range(n_): u = (k + 0.5) * bw / n_; mb.prot(u - 0.09, fh - 0.42, u + 0.09, fh - 0.05, 0.14, dm)
        mb.prot(0, fh - 0.05, bw, fh, 0.16, dm)
    if P.get('panels'):                                                                          # recessed frieze panels
        n_ = max(1, round(bw / 1.6)); pm = P.get('panel_mat', T)
        for k in range(n_): u0 = k * bw / n_ + 0.15; mb.prot(u0, fh * 0.25, u0 + bw / n_ - 0.3, fh * 0.62, 0.025, pm)
    if P.get('rust'):                                                                            # rusticated render: horizontal joints
        rc = P.get('rustc', M('#000000')); step = P.get('rust_step', 0.42); v = ph + step
        while v < fh - 0.1:
            cuts = sorted((h[0], h[2]) for h in holes if h[1] - 0.01 <= v <= h[3] + 0.01)
            u = 0
            for a, b in cuts + [(bw, bw)]:
                if a - 0.02 > u: mb.q(u, v - 0.025, a - 0.02, v + 0.025, 0.004, rc)
                u = max(u, b + 0.02)
            v += step
    if P.get('pil'):
        pw = P.get('pil_w', 0.24); pm = P.get('pil_mat', T)
        mb.prot(0, ph, pw, fh, 0.08, pm); mb.prot(bw - pw, ph, bw, fh, 0.08, pm)
    if P.get('sband'):                                                                           # storey band at the top of the row
        mb.prot(0, fh - P['sband'], bw, fh, 0.09, P.get('sband_mat', T))
    if ph:
        pl = P.get('plinth', M('#5a5754', 0.8))
        bh = [] 
        if P.get('basement') and col in ('W', 'P'):
            for u0, u1 in wins: bh.append(mb.window(u0 + 0.1, 0.12, u1 - 0.1, ph - 0.12, pl, r=0.12, nx=2, fmat=fr, glass=GLASS2, d=0.07, curt=0))
        mb.wall(bh, pl, d=0.07, v1=ph); mb.sides(0, 0, bw, ph, 0, 0.07, pl, bottom=False)

def _spans(holes, v, x0, x1, pad=0.0):
    """solid stretches of a horizontal line at height v, outside the holes"""
    out = []; u = x0
    for h in sorted(hh for hh in holes if hh[1] - pad < v < hh[3] + pad):
        if h[0] - pad > u: out.append((u, h[0] - pad))
        u = max(u, h[2] + pad)
    if u < x1: out.append((u, x1))
    return [s for s in out if s[1] - s[0] > 1e-3]

def _lap(mb, holes, W, v0, v1, step, lap=0.02):
    """horizontal weatherboards as geometry: every board leans out at its lower edge and throws a thin shadow on the one below;
    boards differ slightly in tone, as repainted cladding does"""
    tones = [tint(W, f) for f in (0.955, 0.985, 1.0, 1.0, 1.03)]; under = tint(W, 0.5); v = v0
    while v < v1 - 1e-4:
        t = min(v + step, v1); mat = mb.rnd.choice(tones)
        cuts = sorted({v, t} | {h[k] for h in holes for k in (1, 3) if v < h[k] < t})
        for a, b in zip(cuts, cuts[1:]):
            da = lap * (1 - (a - v) / step); db = lap * (1 - (b - v) / step)
            for s0, s1 in _spans(holes, (a + b) / 2, 0, mb.bw): mb.hq([(s0, a, da), (s1, a, da), (s1, b, db), (s0, b, db)], mat)
        for s0, s1 in _spans(holes, v + 1e-3, 0, mb.bw): mb.hq([(s0, v, 0), (s1, v, 0), (s1, v, lap), (s0, v, lap)], under)
        v = t

def _batten(mb, holes, W, v0, v1, pitch=0.16, bwid=0.045, dep=0.018):
    """vertical boarding with cover battens (pystyrimalaudoitus)"""
    mb.wall(holes + ([(0, 0, mb.bw, v0)] if v0 else []), W)
    n = max(1, round(mb.bw / pitch)); sp = mb.bw / n; hi = tint(W, 1.02)
    for j in range(n):
        u = (j + 0.5) * sp; v = v0
        for h in sorted((hh for hh in holes if hh[0] - 0.02 < u < hh[2] + 0.02), key=lambda hh: hh[1]):
            if h[1] > v: mb.prot(u - bwid / 2, v, u + bwid / 2, h[1], dep, hi)
            v = max(v, h[3])
        if v < v1: mb.prot(u - bwid / 2, v, u + bwid / 2, v1, dep, hi)

def m_wood(mb, col, P):
    """Finnish wooden house bay: board cladding (P['clad']: 'h' weatherboards, 'v' board and batten, 'none' render or brick), corner
    boards and frieze, framed windows with mullions, plinth.
    col: 'W' window, 'N' blank, 'L' / 'R' / 'E' corner board left / right / both (with a window), 'l' / 'r' / 'e' the same without"""
    bw, fh, W = mb.bw, mb.fh, P['wall']; T = P.get('trim', WHITE); ph = P.get('plinth_h', 0); clad = P.get('clad', 'h')
    holes = []
    win = col in ('W', 'L', 'R', 'E') and bw > 1.6
    s_ = P.get('surround', 0.11)
    if win:
        ww = min(P.get('ww', 1.1), bw - 0.8); wh = min(P.get('wh', 1.3), fh - ph - 1.1); sill = max(ph + 0.35, (fh - wh) * 0.5 + 0.05)
        u0 = bw / 2 - ww / 2; u1 = bw / 2 + ww / 2
        holes.append(mb.window(u0, sill, u1, sill + wh, W, r=0.1, fr=0.07, nx=P.get('nx', 2), ny=P.get('ny', 2 if wh > 1.2 else 1), fmat=P.get('frame', T)))
        if s_ > 0:
            mb.prot(u0 - s_, sill, u0, sill + wh, 0.03, T); mb.prot(u1, sill, u1 + s_, sill + wh, 0.03, T)
            mb.prot(u0 - s_ - 0.04, sill + wh, u1 + s_ + 0.04, sill + wh + 0.16, 0.055, T)
        mb.prot(u0 - s_, sill - 0.09, u1 + s_, sill, 0.07, T)
    top = fh - (0.22 if P.get('frieze') else 0)
    if clad == 'h':
        _lap(mb, holes, W, ph, top, P.get('board_step', 0.15))
        if top < fh: mb.wall([], W, v0=top)
    elif clad == 'v': _batten(mb, holes, W, ph, fh)
    else: mb.wall(holes + ([(0, 0, bw, ph)] if ph else []), W)
    cw = 0.14
    if clad != 'none':
        if col in ('L', 'E', 'l', 'e'): mb.prot(0, ph, cw, fh, 0.045, T)
        if col in ('R', 'E', 'r', 'e'): mb.prot(bw - cw, ph, bw, fh, 0.045, T)
    if P.get('frieze'): mb.prot(0, fh - 0.22, bw, fh, 0.05, T)
    if P.get('wband'): mb.prot(0, 0, bw, 0.12, 0.04, T)                                       # board between the storeys
    if ph:
        pl = P.get('plinth', M('#8d8d88', 0.9)); mb.wall([], pl, d=0.03, v1=ph); mb.sides(0, 0, bw, ph, 0, 0.03, pl, bottom=False)

def gable_window(Z, F, P, ww=0.85, wh=1.0):
    """attic window on a gable (1.5-storey houses): F(u, z, d) -> local 3D point, u from the middle of the gable, z from its foot, d outwards"""
    T = P.get('trim', WHITE); z0 = 0.4; e = 0.1
    add_solid(Z, [F(-ww / 2 - e, z0 - e, 0.04), F(ww / 2 + e, z0 - e, 0.04), F(ww / 2 + e, z0 + wh + e + 0.05, 0.04), F(-ww / 2 - e, z0 + wh + e + 0.05, 0.04)], T, 1.0)
    for a, b in ((-ww / 2, -0.03), (0.03, ww / 2)):
        add_solid(Z, [F(a, z0, 0.06), F(b, z0, 0.06), F(b, z0 + wh, 0.06), F(a, z0 + wh, 0.06)], GLASS, 1.0)

MODS = dict(wood=m_wood, classic=m_classic, plain=m_plain, punched=m_punched, ribbon=m_ribbon, raster=m_raster, vraster=m_vraster, loggia=m_loggia, erker=m_erker, shop=m_shop)

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
    # set-back rows (rowP 'setback', metres behind the wall line): a recessed shop floor behind piers, a recessed attic storey.
    # The row's whole facade (its baked tiles too) moves back; a soffit / ledge and end returns close the step (user 13.11.2026:
    # recesses were drawn flush with the main face).
    def _rp(rkey): Pm = dict(P); Pm.update(layout.get('P', {})); Pm.update(layout.get('rowP', {}).get(rkey, {})); return Pm
    sbs = [(_rp(rk_).get('setback', 0) if len(rows) > 1 else 0) for _, _, rk_ in rows]
    for ri, (rh, mod, rkey) in enumerate(rows):
        fh = rh * sc; sb = sbs[ri]
        if sb > 0:
            Pr = _rp(rkey); smat = Pr.get('soffit', P['wall']); rmat = Pr.get('returnmat', P['wall'])
            nxt = sbs[ri + 1] if ri + 1 < len(rows) else None; prv = sbs[ri - 1] if ri > 0 else None
            nxt_ = nxt if nxt is not None else 0          # top row set back: the eave / roof edge stays on the wall line, so its underside
            if sb > nxt_:                                 # closes the step too (otherwise the roof would hang over a gap)
                add_solid(Z, [W(0, fh, -sb, 0, v), W(L, fh, -sb, 0, v), W(L, fh, -nxt_, 0, v), W(0, fh, -nxt_, 0, v)], smat, 0.3)
            if prv is not None and sb > prv:                                         # ledge in front of a set-back upper storey
                add_solid(Z, [W(0, 0, -prv, 0, v), W(L, 0, -prv, 0, v), W(L, 0, -sb, 0, v), W(0, 0, -sb, 0, v)], smat, 0.3)
            kk, pw = Pr.get('piers', (0, max(0.4, min(1.0, sb * 0.5)))); pm = Pr.get('piermat', rmat)
            pos = [] if Pr.get('open_ends') else [(0, pw), (L - pw, L)]                # end piers: at an outside corner their outer faces
            if kk: pos += [(c * bw - pw / 2, c * bw + pw / 2) for c in range(kk, nb, kk)]   # meet and close it (a plain return faced inwards: black)
            if True:
                for a_, b_ in pos:
                    add_solid(Z, [W(a_, 0, 0, 0, v), W(b_, 0, 0, 0, v), W(b_, fh, 0, 0, v), W(a_, fh, 0, 0, v)], pm, 0.4)
                    add_solid(Z, [W(a_, 0, -sb, 0, v), W(a_, 0, 0, 0, v), W(a_, fh, 0, 0, v), W(a_, fh, -sb, 0, v)], pm, 0.3)
                    add_solid(Z, [W(b_, 0, 0, 0, v), W(b_, 0, -sb, 0, v), W(b_, fh, -sb, 0, v), W(b_, fh, 0, 0, v)], pm, 0.3)
        groups = {}; rk = shop_keys(cols) if mod == 'shop' else cols
        for c, ck in enumerate(rk): groups.setdefault(ck if mod != 'plain' else 'W', []).append(c)
        for ck, cs in groups.items():
            rep = min(cs, key=lambda c: abs(c - (nb - 1) / 2) + (0.01 * c))
            Pm = dict(P); Pm.update(layout.get('P', {})); Pm.update(layout.get('rowP', {}).get(rkey, {}))
            mname = Pm.get('colmod', {}).get(ck, mod) if mod not in ('shop', 'plain') else mod
            mb = MB(bw, fh, seed * 131 + ri * 17 + hash(ck) % 97)
            MODS[mname](mb, ck, Pm)
            tiles = mb.tiles or [(0, 0, bw, fh, 0)]
            if sb > 0:
                tiles = [(a, b, c_, d_, e - sb) for a, b, c_, d_, e in tiles]
                mb.hi = [([(a, b, d - sb) for a, b, d in pts], mat) for pts, mat in mb.hi]
                mb.s3 = [([(a, b, d - sb) for a, b, d in pts], mat, dn) for pts, mat, dn in mb.s3]
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
                    Z.hi.append(([W(0, 0, -sb, uo, v), W(bw, 0, -sb, uo, v), W(bw, fh, -sb, uo, v), W(0, fh, -sb, uo, v)], P['wall']))
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
        sa = sum(pts[k][0] * pts[(k + 1) % len(pts)][1] - pts[(k + 1) % len(pts)][0] * pts[k][1] for k in range(len(pts)))
        add_solid(Z, [L(x, y, h + 0.02) for x, y in (pts if sa > 0 else pts[::-1])], rm, 0.25)     # face up (a clockwise outline baked black)
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
        sa = sum(i_[k][0] * i_[(k + 1) % n][1] - i_[(k + 1) % n][0] * i_[k][1] for k in range(n))
        add_solid(Z, [L(x, y, h + ph) for x, y in (i_ if sa > 0 else i_[::-1])], rm, 0.2)

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

def recompress_glb(data, q):
    """Re-encode the embedded JPEGs at quality q (Blender writes its bake at ~90 whatever the export option says)."""
    import struct, json, io
    try: from PIL import Image
    except ImportError: return data
    jl = struct.unpack('<I', data[12:16])[0]; j = json.loads(data[20:20 + jl]); b0 = 20 + jl + 8
    bl = struct.unpack('<I', data[20 + jl:24 + jl])[0]; binc = data[b0:b0 + bl]
    imgv = {im['bufferView'] for im in j.get('images', []) if 'bufferView' in im}
    out = bytearray(); views = j['bufferViews']
    for k, v in enumerate(views):
        o = v.get('byteOffset', 0); d = binc[o:o + v['byteLength']]
        if k in imgv:
            im = Image.open(io.BytesIO(d)).convert('RGB')
            try:                                                   # the bake has Cycles sample noise (the denoiser does not run on bakes): non-local means keeps edges
                import cv2, numpy as np
                im = Image.fromarray(cv2.fastNlMeansDenoisingColored(np.asarray(im), None, 11, 11, 5, 17))
            except ImportError: pass
            bio = io.BytesIO(); im.save(bio, 'JPEG', quality=q, optimize=True, progressive=True); d = bio.getvalue()
        while len(out) % 4: out.append(0)
        v['byteOffset'] = len(out); v['byteLength'] = len(d); out += d
    while len(out) % 4: out.append(0)
    j['buffers'][0]['byteLength'] = len(out)
    js = json.dumps(j, separators=(',', ':')).encode()
    while len(js) % 4: js += b' '
    return struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(out)) + struct.pack('<I', len(js)) + b'JSON' + js + struct.pack('<I', len(out)) + b'BIN\x00' + bytes(out)

def bake_zone(Z, outdir, samples=24, sun_az=118, sun_el=38):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for k in list(_mats): _mats[k] = None
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = samples; sc.cycles.use_denoising = os.environ.get('PORI_DENOISE', '1') == '1'   # denoised bake: no grain at 64 samples
    import gpu_hook; gpu_hook.enable(sc)                                        # GPU on AWS (PORI_GPU=1)
    sc.cycles.max_bounces = 3; sc.cycles.diffuse_bounces = 2; sc.cycles.glossy_bounces = 2; sc.cycles.use_adaptive_sampling = False
    try: sc.cycles.sample_clamp_indirect = 3.0
    except Exception: pass
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (0.62, 0.76, 1.0, 1); bg.inputs[1].default_value = 0.62
    hdr = os.path.join(TEXDIR, 'kloofendal_48d_partly_cloudy_puresky_2k.hdr') if TEXDIR else None
    if hdr and os.path.exists(hdr):                                               # real sky light (Poly Haven CC0) instead of one flat blue
        env = w.node_tree.nodes.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load(hdr)
        w.node_tree.links.new(env.outputs['Color'], bg.inputs[0]); bg.inputs[1].default_value = float(os.environ.get('PORI_SKY', '0.55'))
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
    bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=True, export_image_format='JPEG', export_jpeg_quality=int(os.environ.get('PORI_JPEGQ', '88')), export_yup=True, export_apply=True)
    data = open(glb, 'rb').read()
    if os.environ.get('PORI_JPEGQ'): data = recompress_glb(data, int(os.environ['PORI_JPEGQ']))
    b64 = base64.b64encode(data).decode()
    open(os.path.join(outdir, 'bl_' + Z.name + '.js'), 'w').write('export const x = %s, y = %s, roof = %s;\nexport default "%s";\n' % (Z.cx, Z.cy, 'true' if getattr(Z, 'roofflag', True) else 'false', b64))
    print('DONE', Z.name, 'verts', len(ex.data.vertices), 'glb MB', round(os.path.getsize(glb) / 1e6, 2))
