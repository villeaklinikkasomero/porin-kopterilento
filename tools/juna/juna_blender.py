# -*- coding: utf-8 -*-
"""
PORIKOPTERI – IC-juna (proseduraalinen Blender-malli): Sr3-veturi, kaksikerroksinen IC-vaunu (Ed) ja ohjausvaunu (Edo)
================================================================================================================
Ajo:  bl313/bin/python juna_blender.py -- --out ../juna  [--detail high|low]  [--shots]
Tuottaa: sr3.glb, ed.glb, edo.glb (+ _m = kevyt).  glTF: +Z eteenpäin (three.js), Y ylös, origo kiskon yläpinnan tasolla ajoneuvon keskellä.
Solmut: Bogie_F / Bogie_R (telit, kääntyvät pystyakselin ympäri; origo telin keskellä kiskon tasossa),
        Wheel_<teli><akseli> (pyöräkerrat, pyörivät paikallisen X-akselin ympäri), Panto_1 / Panto_2 (virroitin: Panto_n_Low / _Up -varret),
        Door_<L|R><n> (ovet, liukuvat paikallisen Z:n suuntaan), Lamp_F / Lamp_R (valot, emissiivinen materiaali).
Mitat (julkiset tiedot): Sr3 (Siemens Vectron AC) 18,98 m, leveys 3,0 m, korkeus 4,25 m, teliväli 9,5 m, akseliväli 3,0 m, pyörä Ø 1250 mm.
  Kaksikerrosvaunu 26,4 m, leveys 3,2 m, korkeus 5,1 m, teliväli 19,0 m, akseliväli 2,5 m, pyörä Ø 920 mm; ohjausvaunu samalla rungolla ohjaamopäällä.
Väritys: valkoinen runko, vihreä alaraita ja ohjaamopäät, tummanharmaa katto ja ikkunanauhat (ei logoja).
"""
import bpy, bmesh, math, os, sys
from math import sin, cos, pi, radians
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUT = argv[argv.index('--out') + 1] if '--out' in argv else '.'
DETAIL = argv[argv.index('--detail') + 1] if '--detail' in argv else 'high'
HI = DETAIL == 'high'
SEG = 24 if HI else 10

# ---------------------------------------------------------------- materiaalit
def srgb(h):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)
MATS = {}
def mat(name, col, metal=0.0, rough=0.5, emit=None, alpha=1.0):
    if name in MATS: return MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Metallic'].default_value = metal; b.inputs['Roughness'].default_value = rough
    if emit: b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = 3.0
    if alpha < 1: b.inputs['Alpha'].default_value = alpha; m.blend_method = 'BLEND'
    MATS[name] = m; return m
WHITE = lambda: mat('Valkoinen', srgb('#eceeed'), 0.1, 0.35)
GREEN = lambda: mat('Vihrea', srgb('#00843f'), 0.1, 0.35)
GREY = lambda: mat('Katto', srgb('#3c4043'), 0.2, 0.6)
DARK = lambda: mat('Ikkuna', srgb('#14191c'), 0.3, 0.08)
BLACK = lambda: mat('Musta', srgb('#1b1c1e'), 0.2, 0.7)
STEEL = lambda: mat('Teras', srgb('#55595c'), 0.8, 0.45)
WHEEL = lambda: mat('Pyora', srgb('#6b6e70'), 0.9, 0.35)
RUST = lambda: mat('Teli', srgb('#2b2724'), 0.3, 0.8)
LAMP = lambda: mat('Valo', (1, 1, 0.92), 0, 0.2, emit=(1, 0.97, 0.85))
RED = lambda: mat('Takavalo', (0.8, 0.02, 0.01), 0, 0.3, emit=(1, 0.02, 0.01))
RUBBER = lambda: mat('Palje', srgb('#232425'), 0, 0.9)
YEL = lambda: mat('Keltainen', srgb('#e2b42a'), 0, 0.5)
CERAMIC = lambda: mat('Eriste', srgb('#7a4a33'), 0, 0.3)
COPPER = lambda: mat('Hiili', srgb('#3a3a3a'), 0.4, 0.6)

def clear():
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)

def obj_from(bm, name, material, parent=None):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o)
    if isinstance(material, list):
        for m in material: o.data.materials.append(m)
    else: o.data.materials.append(material)
    if parent: o.parent = parent
    for p in o.data.polygons: p.use_smooth = False
    return o

def empty(name, loc=(0, 0, 0), parent=None):
    e = bpy.data.objects.new(name, None); e.location = loc; bpy.context.collection.objects.link(e)
    if parent: e.parent = parent
    return e

def box(name, sx, sy, sz, loc, material, parent=None, bevel=0.0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * sx, v.co.y * sy, v.co.z * sz)) + Vector(loc)
    if bevel > 0 and HI:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel, segments=1, affect='EDGES')
    return obj_from(bm, name, material, parent)

def cyl(name, r, length, loc, material, axis='X', parent=None, seg=None, r2=None):
    seg = seg or SEG; bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r2 if r2 is not None else r, depth=length)
    R = {'X': Matrix.Rotation(pi / 2, 4, 'Y'), 'Y': Matrix.Rotation(pi / 2, 4, 'X'), 'Z': Matrix.Identity(4)}[axis]
    bmesh.ops.transform(bm, matrix=Matrix.Translation(Vector(loc)) @ R, verts=bm.verts)
    return obj_from(bm, name, material, parent)

def loft(name, sections, material, parent=None, cap0=True, cap1=True, mat_fn=None):
    """sections: [(y, [(x, z), ...]), ...] sama pistemäärä; suljettu kehä"""
    bm = bmesh.new(); rings = []
    for y, pts in sections:
        rings.append([bm.verts.new((x, y, z)) for x, z in pts])
    n = len(rings[0])
    for a, b in zip(rings[:-1], rings[1:]):
        for k in range(n):
            f = bm.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]))
    if cap0: bm.faces.new(list(reversed(rings[0])))
    if cap1: bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = obj_from(bm, name, material if not isinstance(material, list) else material, parent)
    if mat_fn:
        for p in o.data.polygons: p.material_index = mat_fn(p.center)
    return o

def quad(name, pts, material, parent=None, thick=0.0):
    bm = bmesh.new(); vs = [bm.verts.new(p) for p in pts]; f = bm.faces.new(vs)
    if thick:
        r = bmesh.ops.extrude_face_region(bm, geom=[f]); nv = [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, verts=nv, vec=f.normal * thick)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from(bm, name, material, parent)

# runkoprofiili: puolikas (x, z) alhaalta ylös, peilataan
def body_profile(w, zb, ztop, shoulder=0.55, roofr=0.35, n_round=4):
    hw = w / 2; pts = [(0.0, zb), (hw - 0.08, zb), (hw, zb + 0.08), (hw, ztop - shoulder)]
    # olkapää ja katto: pyöristys
    cx, cz = hw - roofr, ztop - shoulder
    for k in range(1, n_round + 1):
        a = k / n_round * (pi / 2); pts.append((cx + roofr * cos(a) + 0 * k, cz + (shoulder - 0.06) * sin(a)))
    pts.append((0.0, ztop))
    full = pts[:-1] + [(-x, z) for x, z in reversed(pts[1:-1])]
    # ympäri: alaosa keskeltä -> oikea kylki -> katto -> vasen kylki
    return [(x, z) for x, z in pts[:-1]] + [(0.0, ztop)] + [(-x, z) for x, z in reversed(pts[1:-1])]

# ---------------------------------------------------------------- yhteiset osat
def wheelset(name, r, gauge, loc, parent):
    e = empty(name, loc, parent)
    for sx in (-1, 1):
        cyl(name + '_w' + ('L' if sx < 0 else 'R'), r, 0.135, (sx * 0.7175, 0, 0), WHEEL(), 'X', e)
        cyl(name + '_f' + ('L' if sx < 0 else 'R'), r + 0.028, 0.03, (sx * 0.668, 0, 0), WHEEL(), 'X', e)   # laippa
        if HI:
            cyl(name + '_d' + ('L' if sx < 0 else 'R'), r * 0.62, 0.06, (sx * 0.5, 0, 0), STEEL(), 'X', e)   # jarrulevy / navan vaihde
    cyl(name + '_axle', 0.085, 1.9, (0, 0, 0), STEEL(), 'X', e, seg=10)
    for sx in (-1, 1):
        cyl(name + '_box' + str(sx), 0.13, 0.26, (sx * 1.03, 0, 0), RUST(), 'X', e, seg=10)   # akselilaakeri
    return e

def bogie(name, y, r, wb, parent, heavy=False):
    b = empty(name, (0, y, 0), parent)
    z = r
    for k, sy in enumerate((-1, 1)):
        wheelset(f'Wheel_{name[-1]}{k + 1}', r, 1.524, (0, sy * wb / 2, z), b)
    # sivupalkit, poikkipalkki, jouset, iskunvaimentimet
    L = wb + 1.3
    for sx in (-1, 1):
        box(f'{name}_side{sx}', 0.22, L, 0.32, (sx * 1.03, 0, z + 0.22), RUST(), b, 0.03)
        for sy in (-1, 1):
            cyl(f'{name}_spring{sx}{sy}', 0.11, 0.32, (sx * 1.03, sy * wb / 2, z + 0.12 + 0.12), STEEL(), 'Z', b, seg=8)
            if HI: cyl(f'{name}_damp{sx}{sy}', 0.04, 0.45, (sx * 1.18, sy * (wb / 2 - 0.35), z + 0.25), YEL(), 'Z', b, seg=6)
        if HI: box(f'{name}_brake{sx}', 0.12, 0.35, 0.25, (sx * 0.86, 0, z + 0.05), BLACK(), b)
    box(f'{name}_trans', 2.2, 0.5 if heavy else 0.36, 0.3, (0, 0, z + 0.26), RUST(), b, 0.03)
    if heavy and HI:   # veturin telissä moottorit
        for sy in (-1, 1): cyl(f'{name}_motor{sy}', 0.32, 1.05, (0.15, sy * wb / 4, z + 0.05), BLACK(), 'X', b, seg=12)
    for sx in (-1, 1): cyl(f'{name}_airspring{sx}', 0.24, 0.22, (sx * 0.95, 0, z + 0.55), BLACK(), 'Z', b, seg=12)
    return b

def buffers_coupler(parent, y, s, zc=1.06):
    """puskimet ja ruuvikytkin pään y kohdalla, s = +1/-1 ulospäin"""
    for sx in (-1, 1):
        cyl(f'buf_body{sx}{s}', 0.11, 0.45, (sx * 0.875, y + s * 0.22, zc), BLACK(), 'Y', parent, seg=12)
        cyl(f'buf_head{sx}{s}', 0.2, 0.05, (sx * 0.875, y + s * 0.47, zc), STEEL(), 'Y', parent, seg=16)
    box(f'hook{s}', 0.12, 0.35, 0.18, (0, y + s * 0.2, zc), STEEL(), parent)
    if HI:
        for k, sx in enumerate((-0.25, 0.25)): cyl(f'hose{k}{s}', 0.03, 0.5, (sx, y + s * 0.15, zc - 0.25), RUBBER(), 'Z', parent, seg=6)

def pantograph(name, loc, parent, up=True, flip=1):
    p = empty(name, loc, parent)
    # alusta eristimineen
    box(name + '_base', 1.3, 1.6, 0.12, (0, 0, 0.32), STEEL(), p)
    for sx in (-1, 1):
        for sy in (-1, 1): cyl(name + f'_ins{sx}{sy}', 0.07, 0.28, (sx * 0.5, sy * 0.6, 0.14), CERAMIC(), 'Z', p, seg=10)
    ang = radians(38 if up else 8)
    low = empty(name + '_Low', (0, -flip * 0.6, 0.42), p)
    L1, L2 = 1.75, 1.85
    # alavarsi: kahdesta putkesta (kehys)
    for sx in (-0.35, 0.35):
        o = cyl(name + f'_low{sx}', 0.04, L1, (sx, flip * L1 / 2, 0), STEEL(), 'Y', low, seg=8)
    low.rotation_euler = (flip * ang, 0, 0)
    up_e = empty(name + '_Up', (0, flip * L1, 0), low)
    cyl(name + '_upper', 0.03, L2, (0, -flip * L2 / 2, 0), STEEL(), 'Y', up_e, seg=8)
    up_e.rotation_euler = (-flip * 2.15 * ang, 0, 0)
    head = empty(name + '_Head', (0, -flip * L2, 0), up_e)
    head.rotation_euler = (flip * 1.15 * ang, 0, 0)
    box(name + '_bow', 1.95, 0.08, 0.05, (0, 0, 0.05), COPPER(), head)
    box(name + '_bow2', 1.95, 0.08, 0.05, (0, 0.32, 0.05), COPPER(), head)
    for sx in (-1, 1): cyl(name + f'_horn{sx}', 0.02, 0.35, (sx * 1.05, 0.16, 0.0), STEEL(), 'Y', head, seg=6)
    return p

def window_band(name, parent, y0, y1, z0, z1, hw, pitch=None, frame=0.08, side=(-1, 1)):
    """tumma ikkunanauha kylkeen ja pystykarmit"""
    for sx in side:
        x = sx * (hw + 0.006)
        quad(f'{name}{sx}', [(x, y0, z0), (x, y1, z0), (x, y1, z1), (x, y0, z1)] if sx > 0 else [(x, y1, z0), (x, y0, z0), (x, y0, z1), (x, y1, z1)], DARK(), parent)
        if pitch and HI:
            n = int(round((y1 - y0) / pitch))
            for k in range(1, n):
                y = y0 + (y1 - y0) * k / n; xx = sx * (hw + 0.012)
                quad(f'{name}{sx}_m{k}', [(xx, y - frame / 2, z0), (xx, y + frame / 2, z0), (xx, y + frame / 2, z1), (xx, y - frame / 2, z1)] if sx > 0 else [(xx, y + frame / 2, z0), (xx, y - frame / 2, z0), (xx, y - frame / 2, z1), (xx, y + frame / 2, z1)], WHITE(), parent)

def stripe(name, parent, y0, y1, z0, z1, hw, material, side=(-1, 1), off=0.004):
    for sx in side:
        x = sx * (hw + off)
        quad(f'{name}{sx}', [(x, y0, z0), (x, y1, z0), (x, y1, z1), (x, y0, z1)] if sx > 0 else [(x, y1, z0), (x, y0, z0), (x, y0, z1), (x, y1, z1)], material, parent)

def door(name, parent, y, z0, z1, hw, sx, width=1.3):
    d = empty(name, (sx * (hw + 0.01), y, 0), parent)
    xx = sx * 0.0
    pts = [(0, -width / 2, z0), (0, width / 2, z0), (0, width / 2, z1), (0, -width / 2, z1)]
    if sx < 0: pts = [pts[1], pts[0], pts[3], pts[2]]
    quad(name + '_leaf', pts, GREEN(), d)
    # ikkuna ovessa
    wz0, wz1 = z0 + (z1 - z0) * 0.45, z1 - 0.18
    wp = [(sx * 0.005, -width / 2 + 0.18, wz0), (sx * 0.005, width / 2 - 0.18, wz0), (sx * 0.005, width / 2 - 0.18, wz1), (sx * 0.005, -width / 2 + 0.18, wz1)]
    if sx < 0: wp = [wp[1], wp[0], wp[3], wp[2]]
    quad(name + '_win', wp, DARK(), d)
    return d

# ---------------------------------------------------------------- Sr3
def build_sr3():
    clear(); root = empty('Sr3')
    W, L = 3.0, 18.98; hw = W / 2; yf = L / 2 - 0.45   # runko ilman puskimia
    zb, ztop = 1.08, 4.0
    # rungon leikkaukset pituussuunnassa (y negatiivinen = etupää glTF +Z)
    def sec(y, w, zt, zb2=zb, sh=0.55):
        return (y, body_profile(w, zb2, zt, sh, 0.3))
    S = []
    for s in (-1, 1):
        part = [sec(s * (yf - 0.0), 2.55, 2.35, zb, 0.4), sec(s * (yf - 0.12), 2.86, 2.55, zb, 0.45), sec(s * (yf - 0.32), 2.98, 2.85, zb, 0.5),
                sec(s * (yf - 0.75), 3.0, 3.72, zb, 0.55), sec(s * (yf - 1.05), 3.0, 3.98, zb, 0.55), sec(s * (yf - 1.5), 3.0, ztop, zb, 0.55)]
        S.append(part)
    sections = S[0] + list(reversed(S[1]))
    sections.sort(key=lambda t: t[0])
    body = loft('Sr3_body', sections, [WHITE(), GREEN(), GREY()], root,
                mat_fn=lambda c: 2 if c.z > 3.85 else (1 if (c.z < 1.55 or abs(c.y) > yf - 0.7) else 0))
    # ohjaamon tuulilasit (molemmat päät) ja sivuikkunat
    for s in (-1, 1):
        y_lo, y_hi = s * (yf - 0.32), s * (yf - 0.75)
        quad(f'Sr3_wind{s}', [(-1.32, y_lo + s * 0.02, 2.95), (1.32, y_lo + s * 0.02, 2.95), (1.28, y_hi + s * 0.02, 3.62), (-1.28, y_hi + s * 0.02, 3.62)][::(1 if s < 0 else -1)], DARK(), root)
        # ohjaamon sivuikkuna
        for sx in (-1, 1):
            x = sx * (hw + 0.006); yy0, yy1 = s * (yf - 1.05), s * (yf - 2.05)
            pts = [(x, min(yy0, yy1), 2.75), (x, max(yy0, yy1), 2.75), (x, max(yy0, yy1), 3.55), (x, min(yy0, yy1), 3.55)]
            if sx < 0: pts = [pts[1], pts[0], pts[3], pts[2]]
            quad(f'Sr3_side{s}{sx}', pts, DARK(), root)
            # ohjaamon ovi
            yd = s * (yf - 2.6); pts = [(x, yd - 0.4, 1.3), (x, yd + 0.4, 1.3), (x, yd + 0.4, 3.45), (x, yd - 0.4, 3.45)]
            if sx < 0: pts = [pts[1], pts[0], pts[3], pts[2]]
            quad(f'Sr3_cabdoor{s}{sx}', pts, GREEN(), root)
            if HI:   # kahva ja tikkaat
                for k in range(3): box(f'Sr3_step{s}{sx}{k}', 0.25, 0.5, 0.04, (sx * (hw - 0.05), yd, 0.55 + k * 0.28), STEEL(), root)
        # valot: kaksi alaa, yksi ylhäällä
        lamps = empty('Lamp_F' if s < 0 else 'Lamp_R', (0, s * yf, 0), root)
        for lx, lz in ((-0.95, 1.85), (0.95, 1.85), (0, 3.75)):
            cyl(f'Sr3_lamp{s}{lx}', 0.09, 0.06, (lx, s * 0.0 + s * (0.33 if lz < 3 else -0.72), lz), LAMP(), 'Y', lamps, seg=14)
        for lx in (-0.95, 0.95): cyl(f'Sr3_tail{s}{lx}', 0.05, 0.05, (lx * 0.8, s * 0.33, 1.85), RED(), 'Y', lamps, seg=10)
        # puskupalkki ja aura
        box(f'Sr3_beam{s}', 2.9, 0.25, 0.45, (0, s * (yf + 0.05), 1.0), GREEN(), root, 0.03)
        if HI: box(f'Sr3_plough{s}', 2.5, 0.35, 0.4, (0, s * (yf + 0.05), 0.42), BLACK(), root, 0.03)
        buffers_coupler(root, s * (yf + 0.18), s, 1.06)
    # kylkien säleiköt ja vihreä alaraita
    stripe('Sr3_stripe', root, -yf + 0.7, yf - 0.7, 1.12, 1.55, hw, GREEN())
    if HI:
        for k, y in enumerate((-4.2, -2.4, 0.0, 2.4, 4.2)):
            stripe(f'Sr3_grille{k}', root, y - 0.7, y + 0.7, 2.45, 3.4, hw, BLACK(), off=0.008)
    # alustan laitteet
    box('Sr3_frame', 2.9, L - 1.2, 0.22, (0, 0, zb - 0.05), BLACK(), root)
    box('Sr3_tank', 2.2, 4.2, 0.62, (0, 0, zb - 0.45), BLACK(), root, 0.05)
    # katto: virroittimet, katkaisija, eristimet, kattolinja
    pantograph('Panto_1', (0, -5.1, ztop), root, up=False, flip=1)
    pantograph('Panto_2', (0, 5.1, ztop), root, up=True, flip=-1)
    if HI:
        box('Sr3_breaker', 0.7, 1.2, 0.35, (0, 0, ztop + 0.18), STEEL(), root)
        cyl('Sr3_roofline', 0.05, 9.2, (0.4, 0, ztop + 0.55), COPPER(), 'Y', root, seg=8)
        for y in (-3.2, -1.2, 1.2, 3.2): cyl(f'Sr3_rins{y}', 0.06, 0.45, (0.4, y, ztop + 0.28), CERAMIC(), 'Z', root, seg=10)
        for y in (-2.0, 2.0): box(f'Sr3_hatch{y}', 2.2, 1.5, 0.08, (0, y, ztop + 0.04), GREY(), root)
    bogie('Bogie_F', -4.75, 0.625, 3.0, root, heavy=True)
    bogie('Bogie_R', 4.75, 0.625, 3.0, root, heavy=True)
    return root

# ---------------------------------------------------------------- kaksikerrosvaunu (Ed) ja ohjausvaunu (Edo)
def build_dd(cab=False):
    clear(); root = empty('Edo' if cab else 'Ed')
    W, L = 3.18, 26.4; hw = W / 2; ye = L / 2 - 0.42
    ztop = 5.05; zlow, zend = 0.42, 1.12
    tr0, tr1 = 8.55, 9.15    # matalan keskiosan ja telipäiden raja
    def sec(y, zb, zt=ztop, w=W, sh=0.62):
        return (y, body_profile(w, zb, zt, sh, 0.4, 5 if HI else 3))
    S = []
    S.append(sec(-ye, zend)); S.append(sec(-tr1, zend)); S.append(sec(-tr0, zlow)); S.append(sec(tr0, zlow)); S.append(sec(tr1, zend)); S.append(sec(ye, zend))
    if cab:   # etupää (y < 0): matalampi, viisto ohjaamo
        S = [s for s in S if s[0] > -tr1 + 0.01]
        S = [sec(-ye - 0.05, zend, 2.35, 2.6, 0.4), sec(-ye + 0.2, zend, 2.75, 2.95, 0.45), sec(-ye + 0.55, zend, 3.35, 3.12, 0.55),
             sec(-ye + 1.15, zend, 3.95, W, 0.6), sec(-ye + 1.75, zend, 4.55, W, 0.62), sec(-ye + 2.4, zend, ztop, W, 0.62), sec(-tr1, zend)] + S
    body = loft(root.name + '_body', S, [WHITE(), GREEN(), GREY()], root,
                mat_fn=lambda c: 2 if c.z > 4.75 else (1 if (c.z < 0.9 or (cab and c.y < -ye + 1.0)) else 0))
    # ikkunanauhat: ala- ja yläkerros, päiden välitaso
    window_band(root.name + '_wl', root, -tr0 + 1.6, tr0 - 1.6, 1.05, 1.85, hw, 1.45)
    window_band(root.name + '_wu', root, -ye + (2.9 if cab else 0.6), ye - 0.6, 2.85, 3.75, hw, 1.45)
    for s in (-1, 1):
        if cab and s < 0: continue
        window_band(root.name + f'_we{s}', root, min(s * (tr1 + 0.3), s * (ye - 0.6)), max(s * (tr1 + 0.3), s * (ye - 0.6)), 1.75, 2.45, hw, 1.2)
    stripe(root.name + '_stripe', root, -tr0 + 0.05, tr0 - 0.05, zlow + 0.05, 0.85, hw, GREEN())
    for s in (-1, 1):
        a, b = (s * (tr0 + 0.6), s * (ye - (1.3 if cab and s < 0 else 0.2)))
        stripe(root.name + f'_stripeE{s}', root, min(a, b), max(a, b), zend + 0.05, zend + 0.42, hw, GREEN())
    stripe(root.name + '_stripe2', root, -ye + (2.5 if cab else 0.2), ye - 0.2, 4.15, 4.3, hw, GREEN())
    # ovet: matalan osan päissä molemmin puolin (lattia 0,6 m: laiturikorkeus 550 mm)
    k = 0
    for s in (-1, 1):
        for sx in (-1, 1):
            k += 1; door(f'Door_{"L" if sx < 0 else "R"}{1 if s < 0 else 2}', root, s * (tr0 - 0.95), 0.62, 2.62, hw, sx, 1.35)
            if HI: box(f'{root.name}_step{s}{sx}', 0.2, 1.35, 0.06, (sx * (hw - 0.02), s * (tr0 - 0.95), 0.52), STEEL(), root)
    # päät: palkeet (ohjaamopäässä ei)
    for s in (-1, 1):
        if cab and s < 0: continue
        box(f'{root.name}_gang{s}', 2.2, 0.36, 2.6, (0, s * (ye + 0.16), 2.0), RUBBER(), root, 0.05)
        buffers_coupler(root, s * (ye + 0.15), s, 1.06)
    if cab:
        s = -1; yy = -ye
        # tuulilasi viistolla otsalla
        quad('Edo_wind', [(-1.3, yy + 0.15, 2.82), (1.3, yy + 0.15, 2.82), (1.3, yy + 0.5, 3.32), (-1.3, yy + 0.5, 3.32)], DARK(), root)
        quad('Edo_wind2', [(-1.25, yy + 0.53, 3.38), (1.25, yy + 0.53, 3.38), (1.2, yy + 1.03, 3.88), (-1.2, yy + 1.03, 3.88)], DARK(), root)
        lamps = empty('Lamp_F', (0, yy, 0), root)
        for lx, lz in ((-1.0, 1.75), (1.0, 1.75), (0, 4.0)):
            cyl(f'Edo_lamp{lx}{lz}', 0.09, 0.06, (lx, -0.07 if lz < 3 else 1.13, lz), LAMP(), 'Y', lamps, seg=14)
        for lx in (-0.85, 0.85): cyl(f'Edo_tail{lx}', 0.05, 0.05, (lx, -0.07, 1.75), RED(), 'Y', lamps, seg=10)
        box('Edo_beam', 2.9, 0.25, 0.45, (0, yy - 0.05, 1.0), GREEN(), root, 0.03)
        if HI: box('Edo_plough', 2.4, 0.3, 0.35, (0, yy - 0.05, 0.45), BLACK(), root, 0.03)
        buffers_coupler(root, yy - 0.15, -1, 1.06)
        for sx in (-1, 1):   # ohjaamon sivuikkuna ja ovi
            x = sx * (hw + 0.006); pts = [(x, yy + 0.9, 2.75), (x, yy + 2.2, 2.75), (x, yy + 2.2, 3.55), (x, yy + 0.9, 3.55)]
            if sx < 0: pts = [pts[1], pts[0], pts[3], pts[2]]
            quad(f'Edo_side{sx}', pts, DARK(), root)
    # alusta: matalan osan alla laitekotelot
    box(root.name + '_skirt', 2.9, 2 * tr0 - 1.0, 0.25, (0, 0, zlow - 0.02), BLACK(), root)
    if HI:
        for y in (-5.0, -1.8, 1.8, 5.0): box(f'{root.name}_box{y}', 2.3, 2.2, 0.18, (0, y, zlow - 0.2), BLACK(), root, 0.03)
        for s in (-1, 1): box(f'{root.name}_ac{s}', 1.6, 2.6, 0.32, (0, s * 10.6, ztop + 0.12), GREY(), root, 0.05)
    bogie('Bogie_F', -9.5, 0.46, 2.5, root)
    bogie('Bogie_R', 9.5, 0.46, 2.5, root)
    return root

# ---------------------------------------------------------------- vienti
def export(root, name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in bpy.data.objects: o.select_set(True)
    # Blender: eteenpäin -Y  ->  glTF +Z
    path = os.path.join(OUT, name + ('' if HI else '_m') + '.glb')
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True, export_apply=True, export_yup=True, export_image_format='JPEG', export_jpeg_quality=86)
    tris = sum(len(p.vertices) - 2 for o in bpy.data.objects if o.type == 'MESH' for p in o.data.polygons)
    print('EXPORT', path, 'tris', tris)

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    export(build_sr3(), 'sr3')
    export(build_dd(False), 'ed')
    export(build_dd(True), 'edo')
