"""Blender builder for the Pori landmarks. Usage: python3 lm.py KEY [still]
Builds the landmark on its real footprint (map-aligned local frame: +X east, +Y north, Z up, origin = ANCHOR),
bakes colour + sun + sky light into one texture and exports out/bl_KEY.glb."""
import bpy, bmesh, math, json, sys, os
from mathutils import Vector

KEY = sys.argv[1]; STILL = len(sys.argv) > 2 and sys.argv[2] == 'still'
OUT = '/home/claude/blender/out'; os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
Z = Vector((0, 0, 1))
KIVI = KEY.startswith('kivi')
ARCH_SEG = 4 if KEY in ('tehdas', 'kehraamo') or KIVI else 8


def lin(hexs):
    v = [int(hexs[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple((c / 12.92) if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in v)


def mat(name, hexs, rough=0.85, metal=0.0, tex=None, col2=None):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    b = nt.nodes['Principled BSDF']; rgb = lin(hexs)
    b.inputs['Base Color'].default_value = (*rgb, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if tex == 'brick':
        t = nt.nodes.new('ShaderNodeTexBrick'); t.inputs['Scale'].default_value = 2.2; t.inputs['Mortar Size'].default_value = 0.012
        t.inputs['Color1'].default_value = (*rgb, 1); t.inputs['Color2'].default_value = (*[c * 0.72 for c in rgb], 1); t.inputs['Mortar'].default_value = (*[c * 0.5 + 0.08 for c in rgb], 1)
        nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
    if tex == 'diamond':                                   # diagonal lattice on vertical walls
        tc = nt.nodes.new('ShaderNodeTexCoord'); sx = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sx.inputs[0])
        s = nt.nodes.new('ShaderNodeMath'); s.operation = 'ADD'; nt.links.new(sx.outputs['X'], s.inputs[0]); nt.links.new(sx.outputs['Y'], s.inputs[1])
        a = nt.nodes.new('ShaderNodeMath'); a.operation = 'ADD'; nt.links.new(s.outputs[0], a.inputs[0]); nt.links.new(sx.outputs['Z'], a.inputs[1])
        d = nt.nodes.new('ShaderNodeMath'); d.operation = 'SUBTRACT'; nt.links.new(s.outputs[0], d.inputs[0]); nt.links.new(sx.outputs['Z'], d.inputs[1])
        cb = nt.nodes.new('ShaderNodeCombineXYZ'); nt.links.new(a.outputs[0], cb.inputs['X']); nt.links.new(d.outputs[0], cb.inputs['Y'])
        ck = nt.nodes.new('ShaderNodeTexChecker'); ck.inputs['Scale'].default_value = 1.15; ck.inputs['Color1'].default_value = (*rgb, 1); ck.inputs['Color2'].default_value = (*lin(col2), 1)
        nt.links.new(cb.outputs[0], ck.inputs['Vector']); nt.links.new(ck.outputs['Color'], b.inputs['Base Color'])
    if tex == 'rust':                                      # horizontal rustication joints
        tc = nt.nodes.new('ShaderNodeTexCoord'); sx = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sx.inputs[0])
        w = nt.nodes.new('ShaderNodeTexWave'); w.bands_direction = 'Z'; w.inputs['Scale'].default_value = 0.42; w.inputs['Distortion'].default_value = 0
        cr = nt.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].position = 0.0; cr.color_ramp.elements[0].color = (*[c * 0.55 for c in rgb], 1)
        cr.color_ramp.elements[1].position = 0.12; cr.color_ramp.elements[1].color = (*rgb, 1)
        nt.links.new(tc.outputs['Object'], w.inputs['Vector']); nt.links.new(w.outputs['Fac'], cr.inputs['Fac']); nt.links.new(cr.outputs['Color'], b.inputs['Base Color'])
    return m


MATS = {}
def M(name, hexs=None, **kw):
    if name not in MATS: MATS[name] = mat(name, hexs, **kw)
    return MATS[name]

M('stone', '#d9d0bd'); M('granite', '#8f8b84'); M('white', '#f2eee3'); M('glass', '#263442', rough=0.2); M('dark', '#22272b', rough=0.5)
M('copper', '#79b3a2', rough=0.6); M('roofdark', '#4b5157', rough=0.7); M('door', '#4a3323'); M('clock', '#e8e3d4')

objs = []
def mesh(verts, faces, m, recalc=True):
    me = bpy.data.meshes.new('m'); me.from_pydata([tuple(v) for v in verts], [], faces)
    if recalc:
        bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    me.materials.append(MATS[m] if isinstance(m, str) else m); o = bpy.data.objects.new('m', me); scene.collection.objects.link(o); objs.append(o); return o

def extrude(pts, off, m):
    n = len(pts); off = Vector(off); v = [Vector(p) for p in pts] + [Vector(p) + off for p in pts]
    return mesh(v, [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)], m)

def boxc(c, s, m):
    x, y, z = c; a, b, h = s[0] / 2, s[1] / 2, s[2] / 2
    v = [(x + i * a, y + j * b, z + k * h) for k in (-1, 1) for j in (-1, 1) for i in (-1, 1)]
    return mesh(v, [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)], m)

def obox(c, u, half_u, half_v, z0, z1, m):
    """box oriented along horizontal unit vector u, centred at c (x, y)"""
    u = Vector((u[0], u[1], 0)); v = Vector((-u.y, u.x, 0)); c = Vector((c[0], c[1], z0))
    return extrude([c + u * a * half_u + v * b * half_v for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))], (0, 0, z1 - z0), m)

def ngon(c, r, n, z, rot=0.0):
    return [(c[0] + r * math.cos(rot + i * 2 * math.pi / n), c[1] + r * math.sin(rot + i * 2 * math.pi / n), z) for i in range(n)]

def frustum(c, r0, r1, z0, z1, n, m, rot=0.0):
    a, b = ngon(c, r0, n, z0, rot), ngon(c, r1, n, z1, rot)
    return mesh(a + b, [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)], m)

def clean(pts):
    o = []; n = len(pts)
    for i in range(n):
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % n]
        cr = abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])); d = math.hypot(c[0] - a[0], c[1] - a[1]) or 1
        if cr / d > 0.5: o.append(b)
    return o if len(o) >= 3 else pts

def offset(pts, d):
    n = len(pts); o = []
    for i in range(n):
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % n]
        e1x, e1y, e2x, e2y = b[0] - a[0], b[1] - a[1], c[0] - b[0], c[1] - b[1]; l1 = math.hypot(e1x, e1y) or 1; l2 = math.hypot(e2x, e2y) or 1
        n1x, n1y = e1y / l1, -e1x / l1; mx, my = n1x + e2y / l2, n1y - e2x / l2; ml = math.hypot(mx, my) or 1; mx /= ml; my /= ml
        k = d / max(0.4, mx * n1x + my * n1y); o.append((b[0] + mx * k, b[1] + my * k))
    return o

def obb(pts):
    best = None
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]; L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L < 3: continue
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        if ux < 0: ux, uy = -ux, -uy
        us = [q[0] * ux + q[1] * uy for q in pts]; vs = [-q[0] * uy + q[1] * ux for q in pts]
        ar = (max(us) - min(us)) * (max(vs) - min(vs))
        if not best or ar < best['ar']:
            cu, cv = (max(us) + min(us)) / 2, (max(vs) + min(vs)) / 2
            best = dict(ar=ar, ux=ux, uy=uy, a=(max(us) - min(us)) / 2, b=(max(vs) - min(vs)) / 2, cx=cu * ux - cv * uy, cy=cu * uy + cv * ux)
    return best

def walls(pts, z0, z1, m):
    v = [(p[0], p[1], z0) for p in pts] + [(p[0], p[1], z1) for p in pts]; n = len(pts)
    return mesh(v, [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)], m, recalc=False)

def ledge(pts, d, z0, z1, m):
    """projecting band: outer strip plus top and bottom rings"""
    o = offset(pts, d); n = len(pts); walls(o, z0, z1, m)
    v = [(p[0], p[1], z1) for p in pts] + [(p[0], p[1], z1) for p in o]; mesh(v, [(n + i, n + (i + 1) % n, (i + 1) % n, i) for i in range(n)], m, recalc=False)
    v = [(p[0], p[1], z0) for p in pts] + [(p[0], p[1], z0) for p in o]; mesh(v, [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)], m, recalc=False)

def hip(pts, inset, z0, rise, m, eave=0.6):
    e, t = offset(pts, eave), offset(pts, -inset); n = len(pts)
    v = [(p[0], p[1], z0) for p in e] + [(p[0], p[1], z0 + rise) for p in t]
    mesh(v, [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)] + [tuple(range(n, 2 * n))], m, recalc=False)
    v = [(p[0], p[1], z0) for p in pts] + [(p[0], p[1], z0) for p in e]; mesh(v, [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)], m, recalc=False)

def cap(pts, z, m):
    mesh([(p[0], p[1], z) for p in pts], [tuple(range(len(pts)))], m, recalc=False)

def shape(o, u, w, h, z0, arch, k, nrm):
    """window outline on a wall: rectangle, or round-arched when arch is set"""
    P = lambda du, dz: o + u * du + Vector((0, 0, z0 + dz)) + nrm * k
    if not arch: return [P(-w / 2, 0), P(w / 2, 0), P(w / 2, h), P(-w / 2, h)]
    r = w / 2; sp = h - r
    return [P(-w / 2, 0), P(w / 2, 0)] + [P(r * math.cos(t), sp + r * math.sin(t)) for t in [i * math.pi / ARCH_SEG for i in range(ARCH_SEG + 1)]]

def window(o, u, nrm, w, h, z0, arch=False, frame='stone', glass='glass', fw=0.22, sill=True, mull=True):
    o, u, nrm = Vector(o), Vector(u).normalized(), Vector(nrm).normalized()
    if KIVI: sill = False; mull = False
    if frame: extrude(shape(o, u, w + 2 * fw, h + fw + (0 if arch else fw), z0 - (0 if arch else 0) - 0.0, arch, -0.03, nrm), nrm * 0.14, frame)
    extrude(shape(o, u, w, h, z0 + (fw if not arch else 0) * 0 , arch, -0.03, nrm), nrm * 0.19, glass)
    if sill and frame: extrude([o + u * a + Vector((0, 0, z0 + b)) for a, b in ((-w / 2 - fw - 0.12, -0.2), (w / 2 + fw + 0.12, -0.2), (w / 2 + fw + 0.12, 0), (-w / 2 - fw - 0.12, 0))], nrm * 0.28, frame)
    if mull and frame and w > 0.9:
        extrude([o + u * a + Vector((0, 0, z0 + b)) for a, b in ((-0.05, 0), (0.05, 0), (0.05, h * (0.8 if arch else 1)), (-0.05, h * (0.8 if arch else 1)))], nrm * 0.23, frame)
        extrude([o + u * a + Vector((0, 0, z0 + h * 0.62 + b)) for a, b in ((-w / 2, 0), (w / 2, 0), (w / 2, 0.08), (-w / 2, 0.08))], nrm * 0.23, frame)

def edges(pts):
    n = len(pts)
    for i in range(n):
        a, b = Vector((*pts[i], 0)), Vector((*pts[(i + 1) % n], 0)); d = b - a; L = d.length
        if L < 0.05: continue
        u = d / L; yield a, u, Vector((u.y, -u.x, 0)), L

def windows(pts, z0, fh, floors, bay, w, h, sill=1.0, min_len=None, pair=False, **kw):
    for a, u, nrm, L in edges(pts):
        if L < (min_len or bay * 0.6): continue
        n = max(1, round(L / bay)); step = L / n
        for k in range(n):
            o = a + u * (step * (k + 0.5))
            for f in range(floors):
                if pair:
                    for s in (-1, 1): window(o + u * s * (w * 0.5 + 0.12), u, nrm, w, h, z0 + f * fh + sill, **kw)
                else: window(o, u, nrm, w, h, z0 + f * fh + sill, **kw)

def ribbons(pts, z0, fh, floors, hgt=1.7, sill=1.0, glass='glass', frame='dark', mull=3.0, margin=0.6):
    for a, u, nrm, L in edges(pts):
        if L < 3: continue
        for f in range(floors):
            z = z0 + f * fh + sill; o = a + u * (L / 2)
            extrude(shape(o, u, L - 2 * margin, hgt, z, False, -0.03, nrm), nrm * 0.1, glass)
            n = max(1, int((L - 2 * margin) / mull))
            for k in range(n + 1):
                p = a + u * (margin + (L - 2 * margin) * k / n)
                extrude([p + u * s + Vector((0, 0, z + dz)) for s, dz in ((-0.05, 0), (0.05, 0), (0.05, hgt), (-0.05, hgt))], nrm * 0.16, frame)

def pilasters(pts, z0, z1, bay, m, w=0.5, d=0.16):
    for a, u, nrm, L in edges(pts):
        if L < bay * 0.6: continue
        n = max(1, round(L / bay))
        for k in range(n + 1):
            o = a + u * (L * k / n)
            extrude([o + u * s + Vector((0, 0, z)) for s, z in ((-w / 2, z0), (w / 2, z0), (w / 2, z1), (-w / 2, z1))], nrm * d, m)


# ---------------------------------------------------------------- footprints
CITY = json.loads(open('/home/claude/game/city.js').read()[len('export default '):-2])
LMAT = dict(raati=(-115.6, 394.1), kaupungintalo=(-57.7, 331.2), teatteri=(-201, 378), taidemuseo=(-94.8, 462.6), kauppahalli=(150, -32.8), vesitorni=(-835, -135),
            puuvilla=(230, 1000), promenadi=(9.2, -238.7), bepop=(58.3, -382.3), kirjasto=(-258, 114), museo=(-264.8, 455.9), tehdas=(160.2, 763.6), kehraamo=(85, 834), tori=(31, 81), isokarhu=(120.9, -179.4), mausoleumi=(-1946, 198.1), areena=(-1615.1, -1391.6), isokappeli=(-1809.2, 141.6), pienikappeli=(-2008.2, 191.1), harjoitushalli=(-1614.9, -1120.8))

def pip(x, y, pts):
    r = False; j = len(pts) - 1
    for i in range(len(pts)):
        a, b = pts[i], pts[j]
        if (a[1] > y) != (b[1] > y) and x < (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]: r = not r
        j = i
    return r

WID = [b.get('w') for b in CITY['b']]
KARHU = (950288076, 950288077, 950288080, 513103884, 513103888); SKOOLI = 1504508728
BLD = []
for b in CITY['b']:
    q = b['p']; BLD.append(([(q[i] / 10, q[i + 1] / 10) for i in range(0, len(q), 2)], b['h']))
GROUP = []
if KIVI:
    cell = int(KEY[4:])
    for bi, (pts, bh) in enumerate(BLD):
        cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
        c = (1 if cx > -150 else 0) + (2 if cy > 385 else 0) if (-385 < cx < 75 and 268 < cy < 505) else 4 if (75 <= cx < 200 and 380 < cy < 470) else -1
        if c == cell and not any(pip(*v, pts) for v in LMAT.values()): GROUP.append((bi, pts, bh))
    allp = [p for g in GROUP for p in g[1]]; AX, AY = round(sum(p[0] for p in allp) / len(allp), 1), round(sum(p[1] for p in allp) / len(allp), 1)
    FP = GROUP[0][1]
else:
    FP = next(p for p, h in BLD if pip(*LMAT[KEY], p))
    AX, AY = round(sum(p[0] for p in FP) / len(FP), 1), round(sum(p[1] for p in FP) / len(FP), 1)
P = clean([(p[0] - AX, p[1] - AY) for p in FP])
O = obb(P); U = Vector((O['ux'], O['uy'], 0)); R = Vector((O['uy'], -O['ux'], 0)); C = Vector((O['cx'], O['cy'], 0))   # R = right of U (southwards)
ROOF_IN_MODEL = False
TEX = 2048


def classic(wall, h, floors, bay, w, hw, arch, base=1.1, roof=None, trim='white', cornice=0.45, pil=False, **kw):
    fh = (h - base - 0.7) / floors
    walls(offset(P, 0.14), 0, base, 'granite'); cap(offset(P, 0.14), base, 'granite'); walls(P, base, h, wall)
    for f in range(1, floors): ledge(P, 0.1, base + f * fh - 0.12, base + f * fh + 0.1, trim)
    ledge(P, cornice, h - 0.7, h, trim)
    if pil: pilasters(P, base, h - 0.7, bay, trim)
    windows(P, base, fh, floors, bay, w, hw, sill=(fh - hw) * 0.42, arch=arch, **kw)
    if roof: hip(P, roof[0], h, roof[1], roof[2])


def modern(wall, h, floors, base=4.6, capc='dark'):
    walls(P, 0, h, wall); fh = (h - base - 0.5) / floors
    ribbons(P, 0, base, 1, hgt=base - 0.9, sill=0.4, mull=2.4); ribbons(P, base, fh, floors, hgt=fh * 0.48, sill=fh * 0.28)
    ledge(P, 0.3, h - 0.5, h + 0.3, capc); ledge(P, 0.3, base - 0.25, base + 0.15, capc)


def gable(c, u, a, b, z0, z1, roofm, wallm, ov=0.4, ends=True):
    """pitched roof over a rectangle: centre c, long axis u, half-length a, half-width b, eave z0, ridge z1"""
    c = Vector((c[0], c[1], 0)); u = Vector((u[0], u[1], 0)).normalized(); v = Vector((-u.y, u.x, 0)); Zv = Vector((0, 0, 1))
    A, B, Cc, D = c - u * (a + ov) - v * (b + ov) + Zv * (z0 - 0.2), c + u * (a + ov) - v * (b + ov) + Zv * (z0 - 0.2), c + u * (a + ov) + v * (b + ov) + Zv * (z0 - 0.2), c - u * (a + ov) + v * (b + ov) + Zv * (z0 - 0.2)
    R0, R1 = c - u * (a + ov) + Zv * z1, c + u * (a + ov) + Zv * z1
    for quad_ in ([A, B, R1, R0], [Cc, D, R0, R1]):
        n = (quad_[1] - quad_[0]).cross(quad_[2] - quad_[0]).normalized(); n = n if n.z > 0 else -n
        extrude(quad_, n * 0.18, roofm)
    if ends:
        for s_ in (-1, 1):
            p0, p1, p2 = c + u * s_ * a - v * b + Zv * z0, c + u * s_ * a + v * b + Zv * z0, c + u * s_ * a + Zv * (z1 - 0.1)
            extrude([p0, p1, p2], u * s_ * -0.3, wallm)

if KEY == 'mausoleumi':
    # Juseliuksen mausoleumi (Josef Stenback, 1903): cross-shaped Gothic Revival chapel of pale ashlar, four steep gables with tall
    # lancet windows, entrance porch, pointed copper dome carrying a slender spire
    M('ashlar', '#cbbd9d', tex='rust'); M('ashd', '#b3a584'); M('cu', '#6fae9c', rough=0.55); ROOF_IN_MODEL = True; TEX = 2048
    cc = (C.x, C.y); core = 4.3; arm_w = 3.1; arm_l = max(O['a'], O['b']) * 0.98; wall = 8.2; apex = 13.2
    obox(cc, U, core, core, 0, 10.2, 'ashlar'); obox(cc, U, core + 0.25, core + 0.25, 0, 1.0, 'ashd')
    front = R                                                                      # the porch side
    for d in (U, -U, R, -R):
        v2 = Vector((-d.y, d.x, 0)); L = arm_l if abs(d.dot(U)) > 0.5 else min(O['a'], O['b']) * 0.98
        prof = [C + d * core * 0.6 + v2 * sx + Vector((0, 0, z)) for sx, z in ((-arm_w, 0), (arm_w, 0), (arm_w, wall), (0, apex), (-arm_w, wall))]
        extrude(prof, d * (L - core * 0.6), 'ashlar')
        for sgn in (-1, 1):                                                         # copper roof slopes
            q = [C + d * (core * 0.5) + v2 * sgn * (arm_w + 0.35) + Vector((0, 0, wall - 0.25)), C + d * (L + 0.35) + v2 * sgn * (arm_w + 0.35) + Vector((0, 0, wall - 0.25)),
                 C + d * (L + 0.35) + Vector((0, 0, apex + 0.12)), C + d * (core * 0.5) + Vector((0, 0, apex + 0.12))]
            n = (q[1] - q[0]).cross(q[2] - q[0]).normalized(); n = n if n.z > 0 else -n; extrude(q, n * 0.14, 'cu')
        o = C + d * L
        for sx, hh in ((-0.95, 4.4), (0, 5.4), (0.95, 4.4)): window(o + v2 * sx, v2, d, 0.62, hh, 3.2 if d != front else 4.6, arch=True, frame='ashd', mull=False, sill=False)
        for sx in (-1, 1):                                                          # buttresses with copper-capped pinnacles
            b0 = C + d * (L - 0.2) + v2 * sx * (arm_w + 0.15); obox(b0[:2], d, 0.45, 0.45, 0, wall + 1.0, 'ashd'); frustum(b0[:2], 0.5, 0.04, wall + 1.0, wall + 2.6, 4, 'cu', math.pi / 4)
        frustum((C + d * L)[:2], 0.22, 0.03, apex, apex + 1.4, 4, 'cu')
    pv = Vector((-front.y, front.x, 0)); Lf = min(O['a'], O['b']) * 0.98 if abs(front.dot(U)) < 0.5 else arm_l           # porch
    prof = [C + front * Lf + pv * sx + Vector((0, 0, z)) for sx, z in ((-1.9, 0), (1.9, 0), (1.9, 3.6), (0, 5.9), (-1.9, 3.6))]; extrude(prof, front * 1.5, 'ashlar')
    window(C + front * (Lf + 1.5), pv, front, 1.5, 3.0, 0.15, arch=True, frame='ashd', glass='door', mull=False, sill=False)
    for sgn in (-1, 1):
        q = [C + front * (Lf - 0.1) + pv * sgn * 2.2 + Vector((0, 0, 3.4)), C + front * (Lf + 1.8) + pv * sgn * 2.2 + Vector((0, 0, 3.4)), C + front * (Lf + 1.8) + Vector((0, 0, 6.05)), C + front * (Lf - 0.1) + Vector((0, 0, 6.05))]
        n = (q[1] - q[0]).cross(q[2] - q[0]).normalized(); n = n if n.z > 0 else -n; extrude(q, n * 0.12, 'cu')
    for sx in (-1, 1):
        for sy in (-1, 1): pc = C + U * sx * core + R * sy * core; frustum(pc[:2], 0.55, 0.5, 0, 11.4, 6, 'ashd'); frustum(pc[:2], 0.6, 0.04, 11.4, 13.6, 6, 'cu')
    rot = math.atan2(U.y, U.x) + math.pi / 8
    frustum(cc, 4.5, 4.5, 10.2, 11.6, 8, 'ashlar', rot); frustum(cc, 4.7, 4.7, 11.6, 11.9, 8, 'ashd', rot)
    for r0, r1, z0, z1 in ((4.6, 4.2, 11.9, 13.6), (4.2, 3.3, 13.6, 15.4), (3.3, 2.2, 15.4, 17.0), (2.2, 1.25, 17.0, 18.2)): frustum(cc, r0, r1, z0, z1, 8, 'cu', rot)
    frustum(cc, 1.25, 1.15, 18.2, 20.6, 8, 'cu', rot); frustum(cc, 1.45, 1.45, 20.6, 20.85, 8, 'cu', rot)
    for i in range(8):
        a_ = rot + math.pi / 8 + i * math.pi / 4; n = Vector((math.cos(a_), math.sin(a_), 0)); window(C + n * 1.1, Vector((-n.y, n.x, 0)), n, 0.4, 1.5, 18.6, arch=True, frame=None, glass='dark')
    frustum(cc, 1.25, 0.05, 20.85, 30.0, 8, 'cu', rot); boxc((C.x, C.y, 30.6), (0.08, 0.08, 1.3), 'dark'); boxc((C.x, C.y, 30.8), (0.6, 0.08, 0.08), 'dark')
elif KEY == 'areena':
    # Isomaki Areena after the 2020s renovation: pale concrete base, dark glazed upper band, white roof fascia, red entrance
    M('conc', '#d6d6d1'); M('fasc', '#f0f0ec'); M('red', '#c8232c'); M('roofl', '#9a9da0'); M('glassd', '#1d2730', rough=0.2); ROOF_IN_MODEL = True; TEX = 2048; h = 15.0
    walls(P, 0, h, 'conc'); ribbons(P, 5.6, 7.0, 1, hgt=6.0, sill=0.4, mull=5.0, glass='glassd', margin=2.0); ribbons(P, 0, 4.5, 1, hgt=2.6, sill=0.6, mull=6.0, margin=6.0)
    ledge(P, 1.4, h - 1.3, h + 0.2, 'fasc'); ledge(P, 0.25, 5.2, 5.6, 'fasc'); cap(P, h, 'roofl')
    best = max(edges(P), key=lambda e: e[3]); a0, u0, n0, L0 = best
    obox((a0 + u0 * L0 / 2 + n0 * 1.6)[:2], u0, 9.0, 1.7, 0, 4.4, 'red'); obox((a0 + u0 * L0 / 2 + n0 * 3.35)[:2], u0, 7.0, 0.05, 0.2, 3.6, 'glassd')
elif KEY == 'harjoitushalli':
    M('metal', '#cdd1d4'); M('roofl', '#a9acae'); M('stripe', '#c8232c'); ROOF_IN_MODEL = True; TEX = 1024; h = 8.5
    walls(P, 0, h, 'metal'); pilasters(P, 0, h, 6.0, 'roofl', w=0.12, d=0.05); ledge(P, 0.2, 2.6, 2.9, 'stripe')
    gable((O['cx'], O['cy']), (O['ux'], O['uy']) if O['a'] >= O['b'] else (-O['uy'], O['ux']), max(O['a'], O['b']), min(O['a'], O['b']), h, h + min(O['a'], O['b']) * 0.22, 'roofl', 'metal', ov=0.5)
elif KEY == 'isokappeli':
    # Kapparan iso kappeli: tall A-frame hall with a white gable wall and a green copper roof running almost to the ground, low wings
    M('wht', '#efece4'); M('cu', '#5f9c84', rough=0.6); M('brickw', '#8a5a44', tex='brick'); ROOF_IN_MODEL = True; TEX = 2048
    ua = (O['ux'], O['uy']) if O['a'] >= O['b'] else (-O['uy'], O['ux']); a_, b_ = max(O['a'], O['b']), min(O['a'], O['b'])
    walls(P, 0, 3.4, 'brickw'); ribbons(P, 0, 3.4, 1, hgt=1.5, sill=1.2, mull=2.4); ledge(P, 0.3, 3.1, 3.5, 'wht'); cap(P, 3.4, 'roofdark')
    uu = Vector((ua[0], ua[1], 0)); vv = Vector((-uu.y, uu.x, 0)); hw_ = min(b_ * 0.85, 9.5); la = a_ * 0.62; apex = 17.5
    for s_ in (-1, 1):
        extrude([C + uu * s_ * la - vv * hw_ + Vector((0, 0, 1.2)), C + uu * s_ * la + vv * hw_ + Vector((0, 0, 1.2)), C + uu * s_ * la + Vector((0, 0, apex - 0.2))], uu * s_ * -0.4, 'wht')
        window(C + uu * s_ * la, vv, uu * s_, 2.4, 6.5, 2.2, arch=False, frame=None, glass='glass')
    for sgn in (-1, 1):
        q = [C - uu * (la + 0.6) + vv * sgn * (hw_ + 0.5) + Vector((0, 0, 0.8)), C + uu * (la + 0.6) + vv * sgn * (hw_ + 0.5) + Vector((0, 0, 0.8)), C + uu * (la + 0.6) + Vector((0, 0, apex)), C - uu * (la + 0.6) + Vector((0, 0, apex))]
        n = (q[1] - q[0]).cross(q[2] - q[0]).normalized(); n = n if n.z > 0 else -n; extrude(q, n * 0.2, 'cu')
    boxc((C.x + uu.x * (la + 0.5), C.y + uu.y * (la + 0.5), 12.0), (0.25, 0.25, 4.0), 'dark')
elif KEY == 'pienikappeli':
    # Kapparan pieni kappeli: red brick with white dressings, steep dark roof, round-arched windows, corner pinnacles
    M('brick', '#a5503c', tex='brick'); ROOF_IN_MODEL = True; TEX = 1024; h = 6.2
    ua = (O['ux'], O['uy']) if O['a'] >= O['b'] else (-O['uy'], O['ux']); a_, b_ = max(O['a'], O['b']), min(O['a'], O['b'])
    classic('brick', h, 1, 3.0, 1.0, 3.2, True, trim='white', frame='white', cornice=0.35, pil=True)
    gable((O['cx'], O['cy']), ua, a_, b_, h, h + b_ * 1.25, 'roofdark', 'brick', ov=0.35)
    uu = Vector((ua[0], ua[1], 0)); vv = Vector((-uu.y, uu.x, 0))
    for sx in (-1, 1):
        for sy in (-1, 1): pc = C + uu * sx * a_ + vv * sy * b_; frustum(pc[:2], 0.45, 0.45, 0, h + 1.6, 6, 'white'); frustum(pc[:2], 0.5, 0.04, h + 1.6, h + 3.4, 6, 'roofdark')
    boxc((C.x + uu.x * a_, C.y + uu.y * a_, h + b_ * 1.25 + 0.9), (0.14, 0.14, 1.8), 'white')
elif KEY == 'raati':
    M('plaster', '#efe3ba'); h, rise = 13.5, 3.0; ROOF_IN_MODEL = True
    classic('plaster', h, 3, 3.1, 1.15, 2.2, False, roof=(6.2, rise, 'copper'))
    W = 7.0; c0 = C + R * O['b']                                               # pedimented centre on the park side
    rp = [c0 - U * W, c0 + U * W, c0 + U * W + R * 1.0, c0 - U * W + R * 1.0]
    extrude([(*p[:2], 0) for p in rp], (0, 0, h - 0.7), 'plaster')
    for k in range(5):
        for f in range(3): window(c0 + R * 1.0 + U * (-5.6 + 2.8 * k), U, R, 1.15, 2.2, 1.1 + f * 3.9 + 0.7)
    for k in range(6): extrude([c0 + R * 1.0 + U * (-7 + 2.8 * k + s) + Vector((0, 0, z)) for s, z in ((-0.28, 4.6), (0.28, 4.6), (0.28, h - 0.9), (-0.28, h - 0.9))], R * 0.2, 'white')
    extrude([c0 - U * (W + 0.3) + Vector((0, 0, h - 0.9)), c0 + U * (W + 0.3) + Vector((0, 0, h - 0.9)), c0 + U * (W + 0.3) + Vector((0, 0, h - 0.1)), c0 - U * (W + 0.3) + Vector((0, 0, h - 0.1))], R * 1.5, 'white')
    extrude([c0 - U * (W + 0.3) + Vector((0, 0, h - 0.1)), c0 + U * (W + 0.3) + Vector((0, 0, h - 0.1)), c0 + Vector((0, 0, h + 2.5))], R * 1.5, 'white')
    extrude([c0 - U * (W - 0.9) + Vector((0, 0, h + 0.2)), c0 + U * (W - 0.9) + Vector((0, 0, h + 0.2)), c0 + Vector((0, 0, h + 1.95))], R * 1.56, 'plaster')
    top = h + rise - 0.6; cc = (C.x, C.y)
    obox(cc, U, 2.2, 2.2, top, top + 5.2, 'white')
    for i in range(4):
        n = (U, R, -U, -R)[i]; u2 = Vector((-n.y, n.x, 0)); o = C + n * 2.2
        extrude([o + u2 * (1.05 * math.cos(t)) + Vector((0, 0, top + 3.4 + 1.05 * math.sin(t))) for t in [k * math.pi / 10 for k in range(20)]], n * 0.1, 'dark')
        extrude([o + u2 * (0.85 * math.cos(t)) + Vector((0, 0, top + 3.4 + 0.85 * math.sin(t))) for t in [k * math.pi / 10 for k in range(20)]], n * 0.14, 'clock')
    obox(cc, U, 2.9, 2.9, top + 5.2, top + 5.5, 'white')
    for i in range(4):                                                         # balcony railing
        n = (U, R, -U, -R)[i]; u2 = Vector((-n.y, n.x, 0))
        for k in range(7): obox((C + n * 2.8 + u2 * (-2.7 + 0.9 * k))[:2], U, 0.05, 0.05, top + 5.5, top + 6.4, 'dark')
        extrude([C + n * 2.8 + u2 * s + Vector((0, 0, z)) for s, z in ((-2.8, top + 6.35), (2.8, top + 6.35), (2.8, top + 6.45), (-2.8, top + 6.45))], n * 0.08, 'dark')
    frustum(cc, 1.6, 1.5, top + 5.5, top + 9.0, 8, 'white', math.pi / 8)
    for i in range(8):
        a = math.pi / 4 * i; n = Vector((math.cos(a), math.sin(a), 0)); window(C + n * 1.45, Vector((-n.y, n.x, 0)), n, 0.6, 2.0, top + 6.3, arch=True, frame=None, glass='dark')
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=1.9, location=(C.x, C.y, top + 9.7)); d = bpy.context.object; d.scale = (1, 1, 0.95); d.data.materials.append(MATS['copper']); objs.append(d)
    frustum(cc, 0.9, 0.5, top + 11.2, top + 12.4, 8, 'copper'); frustum(cc, 0.5, 0.03, top + 12.4, top + 15.6, 8, 'copper')
elif KEY == 'kaupungintalo':
    M('rust', '#8d7f70', tex='rust'); M('diamond', '#c87850', tex='diamond', col2='#dc9a72'); M('sand', '#e3d2b8'); h = 17.0; ROOF_IN_MODEL = True
    walls(offset(P, 0.16), 0, 1.1, 'granite'); cap(offset(P, 0.16), 1.1, 'granite'); walls(offset(P, 0.08), 1.1, 6.2, 'rust'); cap(offset(P, 0.08), 6.2, 'sand'); walls(P, 6.2, h, 'diamond')
    ledge(P, 0.3, 5.9, 6.3, 'sand'); ledge(P, 0.18, 11.3, 11.6, 'sand'); ledge(P, 0.7, h - 0.9, h, 'sand'); ledge(P, 0.35, h - 1.5, h - 0.9, 'rust')
    windows(offset(P, 0.08), 1.1, 5.1, 1, 3.4, 1.3, 3.0, sill=1.2, arch=True, frame='sand')
    windows(P, 6.2, 5.2, 2, 3.4, 0.75, 2.7, sill=1.1, arch=True, frame='sand', pair=True, mull=False)
    hip(P, 3.0, h, 0.9, 'roofdark', eave=0.75)
elif KEY == 'teatteri':
    M('plaster', '#ecd9a0'); classic('plaster', 12.5, 2, 3.6, 1.35, 3.3, True, pil=True)
elif KEY == 'taidemuseo':
    M('plaster', '#d9d3c4', tex='rust'); classic('plaster', 8.2, 1, 6.2, 2.9, 5.0, True, cornice=0.5, frame='white')
elif KEY == 'kauppahalli':
    M('plaster', '#d8c88e'); classic('plaster', 8.5, 2, 4.2, 1.7, 2.3, True)
elif KEY == 'kehraamo':
    M('brick', '#9c4a38', tex='brick'); M('btrim', '#7e3a2c')
    classic('brick', 9.5, 2, 3.6, 1.3, 2.1, True, trim='btrim', frame=None, glass='dark', cornice=0.35)
elif KEY == 'tehdas':
    # Porin Puuvilla mill (August Krook, 1899-1912). Massing, roofs, pavilion lanterns and the stair tower come straight from the
    # National Land Survey LoD2 building model (Rakennukset 3D, measured by laser scanning, CC BY 4.0); on top of that the
    # red-brick walls get rows of white-framed round-arched windows like in the photos.
    import pickle
    M('brick', '#9c4a38', tex='brick'); M('btrim', '#c9a58c'); M('slate', '#3e4247', rough=0.7); ROOF_IN_MODEL = True; TEX = 4096
    MB = next(b for b in pickle.load(open('/home/claude/mmlproc/b.pkl', 'rb')) if b['id'] == 'pori_2022_370597')
    z0 = MB['z0']; L3 = lambda p: Vector((p[0] - AX, p[1] - AY, max(0.0, p[2] - z0)))
    for k, r, ins in MB['p']:
        if k == 'G' or len(r) < 3: continue
        pts = [L3(p) for p in r]
        o = mesh(pts, [tuple(range(len(pts)))], 'slate' if k == 'R' else 'brick', recalc=False)
        if k == 'W':                                                             # windows on the tall wall faces
            nrm = Vector((0, 0, 0))
            for i in range(len(pts)):
                a_, b_ = pts[i], pts[(i + 1) % len(pts)]; nrm += Vector(((a_.y - b_.y) * (a_.z + b_.z), (a_.z - b_.z) * (a_.x + b_.x), (a_.x - b_.x) * (a_.y + b_.y)))
            nrm.z = 0
            if nrm.length < 1e-6: continue
            nrm.normalize(); u = Vector((-nrm.y, nrm.x, 0))
            us = [(p - pts[0]).dot(u) for p in pts]; u0, u1 = min(us), max(us); Lw = u1 - u0
            zb = min(p.z for p in pts)
            def ztop(uu):                                                        # wall top at position uu along the face
                best = None
                for i in range(len(pts)):
                    a_, b_ = pts[i], pts[(i + 1) % len(pts)]; ua, ub = us[i], us[(i + 1) % len(pts)]
                    if (ua - uu) * (ub - uu) <= 0 and abs(ub - ua) > 1e-6:
                        z = a_.z + (b_.z - a_.z) * (uu - ua) / (ub - ua); best = z if best is None else max(best, z)
                    elif abs(ub - ua) <= 1e-6 and abs(ua - uu) < 1e-6: best = max(a_.z, b_.z) if best is None else max(best, a_.z, b_.z)
                return best
            if Lw < 3.0 or zb > 3.0: continue
            nb = max(1, round(Lw / 3.7)); base = pts[0] + nrm * 0.02
            for kb in range(nb):
                uu = u0 + Lw * (kb + 0.5) / nb; zt = min(ztop(uu - 0.9) or 0, ztop(uu + 0.9) or 0)
                if zt - zb < 6: continue
                fl = max(1, min(5, round((zt - zb - 2.2) / 4.6))); fh = (zt - zb - 2.2) / fl
                for f in range(fl):
                    z_ = zb + 1.3 + f * fh + 0.25 * fh
                    window(base + u * uu, u, nrm, 1.5, min(2.9, fh * 0.62), z_, arch=True, frame='white', glass='dark', sill=True, mull=True)
            for zz in (zb + 1.1,):                                               # plinth line
                pass
elif KEY == 'vesitorni':
    M('brick', '#8a3e2e', tex='brick'); M('band', '#cdb48e'); h = 47.0; TEX = 1024; ROOF_IN_MODEL = True
    walls(offset(P, 0.25), 0, 2.2, 'granite'); cap(offset(P, 0.25), 2.2, 'granite'); walls(P, 2.2, h + 0.9, 'brick'); cap(offset(P, -0.4), h, 'roofdark'); walls([p for p in reversed(offset(P, -0.4))], h, h + 0.9, 'brick')
    cap_ring = offset(P, -0.4); n = len(P); mesh([(p[0], p[1], h + 0.9) for p in P] + [(p[0], p[1], h + 0.9) for p in cap_ring], [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)], 'band', recalc=False)
    windows(P, 2.2, 5.5, 8, 4.9, 0.55, 1.7, sill=2.4, frame=None, glass='dark', mull=False)
    for z in (8, 15.5, 23, 30.5, 38, 45.5): ledge(P, 0.06, z, z + 0.35, 'band')
    tc = C - R * O['b']                                                        # rounded stair turret on the north side
    frustum((tc.x, tc.y), 2.5, 2.5, 0, h + 4, 20, 'brick')
    for z in (8, 15.5, 23, 30.5, 38, 45.5): frustum((tc.x, tc.y), 2.56, 2.56, z, z + 0.35, 20, 'band')
    frustum((tc.x, tc.y), 2.7, 2.7, h + 4, h + 4.5, 20, 'roofdark')
elif KEY == 'puuvilla':
    M('brick', '#a8473a', tex='brick'); M('red', '#d2232a'); M('glassd', '#2b3540'); h = 14.0
    walls(P, 0, 5, 'glassd'); walls(P, 5, h, 'brick'); ribbons(P, 0, 5, 1, hgt=4.0, sill=0.4, mull=3.0, glass='glass')
    ribbons(P, 5, 3.9, 2, hgt=1.5, sill=1.2, mull=3.0); ledge(P, 0.8, h - 1.2, h, 'red'); ledge(P, 0.8, 4.8, 5.4, 'red')
elif KEY == 'promenadi':
    TEX = 1024; M("wall", "#41464c", tex="rust"); modern('wall', 12.5, 2)
elif KEY == 'bepop':
    TEX = 1024; M("wall", "#b4bcb8"); M("capc", "#4d5a57"); modern('wall', 17.0, 3, capc='capc')
elif KEY == 'kirjasto':
    TEX = 1024; M("wall", "#bcb4a5"); M("capc", "#6b6258"); modern('wall', 10.5, 2, base=3.6, capc='capc')
elif KEY == 'museo':                                                           # 1973: closed exposed-aggregate concrete walls with vertical panel joints, recessed dark entrance glazing
    TEX = 1024; M('wall', '#a9a294'); M('joint', '#8a8477'); M('capc', '#8c8a84'); h = 10.0
    walls(P, 0, h, 'wall'); pilasters(P, 0.2, h - 0.3, 1.9, 'joint', w=0.06, d=0.03); ledge(P, 0.12, h - 0.35, h, 'capc')
    for a, u, nrm, L in edges(P):
        if L > 28:
            o = a + u * (L * 0.6); extrude(shape(o, u, L * 0.42, 2.6, 0.3, False, -0.03, nrm), nrm * 0.08, 'glass')
            for k in range(8): extrude([a + u * (L * 0.39 + L * 0.42 * k / 7 + q) + Vector((0, 0, z)) for q, z in ((-0.05, 0.3), (0.05, 0.3), (0.05, 2.9), (-0.05, 2.9))], nrm * 0.14, 'dark')
elif KEY == 'isokarhu':                                                        # glazed street level with magenta entrance band, dark panel cladding above
    M('wall', '#4b4c52', tex='rust'); M('pink', '#e6007e'); modern('wall', 13.0, 2, base=4.6)
    ledge(P, 0.9, 4.25, 4.85, 'pink'); ledge(P, 1.3, 4.85, 5.05, 'white')
elif KEY == 'tori':
    M('roofb', '#5a4636', rough=0.7); M('wood', '#c9a06b'); M('cu', '#7d4b33', rough=0.6, metal=0.3); TEX = 1024; ROOF_IN_MODEL = True
    if O['a'] < O['b']:
        U, R = Vector((-O['uy'], O['ux'], 0)), None; O['a'], O['b'] = O['b'], O['a']
        if U.x < 0: U = -U
        R = Vector((U.y, -U.x, 0))
    a, b, H, gap = O['a'], O['b'], 4.4, 3.6
    def rrect(hw, hd, r, z):
        pts = []
        for sx, sy, a0 in ((1, -1, -90), (1, 1, 0), (-1, 1, 90), (-1, -1, 180)):
            for k in range(7):
                t = math.radians(a0 + 15 * k); pts.append(C + U * (sx * (hw - r) + r * math.cos(t)) + (-R) * (sy * (hd - r) + r * math.sin(t)) + Vector((0, 0, z)))
        return pts
    extrude(rrect(a + 3.5, b + 4, 6, H + 0.25), (0, 0, 0.5), 'roofb'); extrude(rrect(a + 3.0, b + 3.5, 5.5, H + 0.12), (0, 0, 0.14), 'wood')
    full = a - 1.5 - gap; gl = full * 0.45; cu = full - gl; w = b - 1.75
    for s in (-1, 1):
        gc = C + U * s * (gap + gl / 2); obox(gc[:2], U, gl / 2, w, 0.1, H + 0.12, 'glass')
        gp = [gc + U * sa * gl / 2 + R * sb * w for sa, sb in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        for e in range(4):
            p0, p1 = gp[e], gp[(e + 1) % 4]; d = p1 - p0; L = d.length; u = d / L; nrm = Vector((u.y, -u.x, 0)); n = max(1, int(L / 1.6))
            for k in range(n + 1): extrude([p0 + u * (L * k / n + q) + Vector((0, 0, z)) for q, z in ((-0.05, 0.1), (0.05, 0.1), (0.05, H), (-0.05, H))], nrm * 0.1, 'dark')
        obox((C + U * s * (gap + gl + cu / 2))[:2], U, cu / 2, w - 0.3, 0.1, H + 0.12, 'cu')

if KIVI:
    ROOF_IN_MODEL = True; OCC = []
    PAL = ['#d9826f', '#e9dfc6', '#ecd9a0', '#d6d2c8', '#dcc48a', '#cfd4c4', '#e3b89a', '#f0ead9', '#c9b7a0', '#e6cfa6']
    def area(pts): return abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts))) / 2)
    for bi, pts, bh in GROUP:
        P = clean([(p[0] - AX, p[1] - AY) for p in pts]); wid = WID[bi]; hs = ((wid or bi) * 2654435761) % 4294967296; ar = area(P)
        wall = 'pl%d' % (hs % len(PAL)); M(wall, PAL[hs % len(PAL)])
        if wid == 171187229:                                                         # old riverside warehouse (Shots)
            M('ware', '#e2c98a'); classic('ware', bh, 1, 5.0, 2.3, 3.4, True, frame='white', cornice=0.4)
        elif wid == SKOOLI:                                                       # restaurant opened in 2026: single storey, glazed, terrace towards the river
            M('wood', '#3a332d'); O2 = obb(P); u2 = Vector((O2['ux'], O2['uy'], 0)); r2 = Vector((O2['uy'], -O2['ux'], 0)); c2 = Vector((O2['cx'], O2['cy'], 0))
            walls(P, 0, bh, 'wood'); ribbons(P, 0, bh, 1, hgt=bh - 1.3, sill=0.5, mull=1.6); ledge(P, 0.5, bh - 0.35, bh, 'dark'); cap(P, bh, 'roofdark')
            tc = c2 - r2 * (O2['b'] + 3.0); obox(tc[:2], u2, O2['a'], 3.0, 0.05, 0.3, 'stone'); obox(tc[:2], u2, O2['a'], 3.0, 0.3, 2.9, 'glass'); obox(tc[:2], u2, O2['a'] + 0.2, 3.2, 2.9, 3.05, 'dark')
            for k in range(-4, 5): obox((tc - r2 * 3.0 + u2 * (O2['a'] * k / 4))[:2], u2, 0.05, 0.05, 0.3, 2.9, 'dark')
            vc = c2 - u2 * (O2['a'] + 1.6); obox(vc[:2], u2, 1.7, 2.2, 0, 3.0, 'glass'); obox(vc[:2], u2, 1.8, 2.3, 3.0, 3.2, 'dark')
        elif wid in KARHU:                                # Karhukortteli: new apartment blocks on the old brewery site
            M('rend', '#ecebe6'); M('rend2', '#cfc9bd'); M('roofl', '#8d9094'); wm = 'rend' if wid % 2 == 0 else 'rend2'
            fl = max(2, round((bh - 0.6) / 3.1)); fh = (bh - 0.6) / fl
            walls(P, 0, bh, wm); ribbons(P, 0, fh, 1, hgt=fh - 1.0, sill=0.4, mull=2.4); windows(P, fh, fh, fl - 1, 3.4, 1.5, 1.5, sill=0.9, frame='dark')
            ledge(P, 0.25, bh - 0.3, bh + 0.2, 'dark'); cap(P, bh, 'roofl')
            pent = offset(P, -3.2); walls(pent, bh, bh + 2.9, 'rend'); cap(pent, bh + 2.9, 'roofl'); ledge(pent, 0.3, bh + 2.7, bh + 2.95, 'dark')
            for a, u, nrm, L in edges(P):                                         # protruding glazed balconies on the long sides
                if L < 14: continue
                n = max(1, round(L / 3.4)); step = L / n
                for k in range(0, n, 2):
                    for f in range(1, fl):
                        o = a + u * (step * (k + 0.5)) + Vector((0, 0, f * fh)); c = o + nrm * 0.85
                        obox(c[:2], u, 1.5, 0.85, o.z - 0.05, o.z + 0.12, 'dark'); obox((o + nrm * 1.66)[:2], u, 1.5, 0.03, o.z + 0.12, o.z + 1.15, 'glass')
        elif wid in (950288078, 950288079):                                                  # brewery-era brick buildings kept in the block
            M('obrick', '#8f4a38', tex='brick'); M('btrim', '#7e3a2c'); fl = max(1, round((bh - 1.8) / 3.9))
            classic('obrick', bh, fl, 3.4, 1.2, 2.0, True, trim='btrim', frame='stone', cornice=0.3)
        elif wid in (89689140, 89689144, 89689145):                                            # Eteläranta between Antinkatu and Yrjönkatu: long pale two-storey stone houses with a gateway
            M('ery', '#ecd9a0'); M('erc', '#e9dfc6'); fl = 2
            classic('erc' if wid == 89689145 else 'ery', bh, fl, 3.3, 1.15, 2.2, wid == 89689140, pil=True, cornice=0.5)
        elif bh < 5.5 or ar < 90:
            walls(P, 0, bh, wall); ledge(P, 0.2, bh - 0.3, bh, 'white')
            if bh >= 4.2 and ar >= 90: windows(P, 0.4, bh - 0.8, 1, 3.4, 1.0, 1.5, sill=1.0)
        else:
            fl = max(1, round((bh - 1.8) / 3.7)); fh = (bh - 1.8) / fl
            classic(wall, bh, fl, 3.2, 1.1, min(2.1, fh * 0.58), hs % 4 == 0, pil=(hs // 7) % 2 == 0)
        if wid != SKOOLI and wid not in KARHU: OCC.append((list(P), bh))
landmark = list(objs)
if KIVI:
    for pp, bh in OCC:
        o = mesh([(q[0], q[1], bh - 0.3) for q in pp], [tuple(range(len(pp)))], M('occ', '#b9ae9c'), recalc=False); objs.remove(o)

# ---------------------------------------------------------------- surroundings
gm = mat('ground', '#7d8273'); g = mesh([(-300, -300, 0), (300, -300, 0), (300, 300, 0), (-300, 300, 0)], [(0, 1, 2, 3)], gm); objs.remove(g)
BM = mat('bld', '#b9ae9c')
for pts, bh in BLD:
    cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
    if pts is not FP and not any(pts is g[1] for g in GROUP) and math.hypot(cx - AX, cy - AY) < (260 if KIVI else 170) and not pip(cx, cy, FP):
        o = extrude([(p[0] - AX, p[1] - AY, 0) for p in pts], (0, 0, min(bh, 40)), BM); objs.remove(o)
if not ROOF_IN_MODEL and not KIVI:                                             # flat roof kept from the aerial image in the game; here only as an occluder
    hh = max(v.co.z for o in landmark for v in o.data.vertices) - 0.4
    o = mesh([(p[0], p[1], hh) for p in P], [tuple(range(len(P)))], BM, recalc=False); objs.remove(o)

sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); scene.collection.objects.link(sun)
sun.data.energy = 3.6; sun.data.angle = math.radians(1.5); sun.data.color = (1.0, 0.95, 0.86)
az, el = math.radians(-35), math.radians(38)                                  # the aerial image has its shadows to the north-west
d = Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el))); sun.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
w = bpy.data.worlds.new('w'); scene.world = w; w.use_nodes = True; bg = w.node_tree.nodes['Background']; sky = w.node_tree.nodes.new('ShaderNodeTexSky')
try: sky.sun_elevation = el; sky.sun_rotation = math.pi / 2 - az; sky.sun_disc = False
except Exception as e: print('sky', e)
w.node_tree.links.new(sky.outputs['Color'], bg.inputs['Color']); bg.inputs['Strength'].default_value = 0.07
scene.render.engine = 'CYCLES'; scene.cycles.device = 'CPU'; scene.view_settings.view_transform = 'Standard'

if STILL:
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); scene.collection.objects.link(cam); scene.camera = cam; cam.data.lens = 30; cam.data.clip_end = 3000
    rad = max(O['a'], O['b']) * 2.2 + 30; pos = Vector((rad * 0.55, -rad, rad * 0.45)); tgt = Vector((0, 0, 8)); cam.location = pos; cam.rotation_euler = (tgt - pos).to_track_quat('-Z', 'Y').to_euler()
    scene.render.resolution_x, scene.render.resolution_y = 1000, 640; scene.cycles.samples = 32; scene.cycles.use_denoising = True
    scene.render.image_settings.file_format = 'JPEG'; scene.render.image_settings.quality = 85
    scene.render.filepath = OUT + '/still_%s.jpg' % KEY; bpy.ops.render.render(write_still=True)
else:
    for o in bpy.data.objects: o.select_set(False)
    for o in landmark: o.select_set(True)
    bpy.context.view_layer.objects.active = landmark[0]; bpy.ops.object.join(); ob = bpy.context.view_layer.objects.active
    print(KEY, 'faces', len(ob.data.polygons), 'anchor', AX, AY)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.002); bpy.ops.object.mode_set(mode='OBJECT')
    img = bpy.data.images.new('bake', TEX, TEX)
    for m in ob.data.materials:
        n = m.node_tree.nodes.new('ShaderNodeTexImage'); n.image = img; m.node_tree.nodes.active = n; n.select = True
    scene.cycles.samples = 20; scene.cycles.use_denoising = False; scene.render.bake.margin = 4
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR', 'DIRECT', 'INDIRECT'})
    bm_ = bpy.data.materials.new('baked'); bm_.use_nodes = True; t = bm_.node_tree.nodes.new('ShaderNodeTexImage'); t.image = img
    bm_.node_tree.links.new(t.outputs['Color'], bm_.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
    ob.data.materials.clear(); ob.data.materials.append(bm_)
    for p in ob.data.polygons: p.material_index = 0
    for o in bpy.data.objects: o.select_set(o is ob)
    kw = dict(filepath=OUT + '/bl_%s.glb' % KEY, use_selection=True, export_format='GLB', export_image_format='JPEG', export_yup=True, export_apply=True)
    try: bpy.ops.export_scene.gltf(**kw, export_jpeg_quality=78)
    except TypeError: bpy.ops.export_scene.gltf(**kw)
    json.dump({'x': AX, 'y': AY, 'roof': ROOF_IN_MODEL}, open(OUT + '/bl_%s.json' % KEY, 'w'))
    print('exported', KEY, os.path.getsize(OUT + '/bl_%s.glb' % KEY))
