# -*- coding: utf-8 -*-
"""IC2-kaksikerrosvaunujen sisätilat (Ed ja Edo) peliä varten (omistaja 21.11.2026: "autenttiset junavaunut sisältä … kyytiin matkaan").
Ajo: bl313/bin/python juna_sisa.py -- --out ../juna [--detail high|low]
Tuottaa juna/ed_sisa.glb, juna/edo_sisa.glb (+ _m) ja juna/sisa.json (kävelyalueet juna.js:lle).

Lähteet (julkiset, ei kuvia peliin): Škoda/Transtech IC2-tiedot (pituus 26,4 m, leveys 3,2 m, alakerran vapaa korkeus 2,20 m,
yläkerran 2,18 m, Ed 113 paikkaa), Resiina-lehti (kolme tasoa: ala- ja yläkerta + välitaso telien päällä, eteiset ja portaat
kummassakin päässä, 2+2-penkit osin vastakkain pöydän ääressä, pieni WC ylä- ja alakerrassa, hattuhyllyt, Edo: ohjaamo välitasolla,
laitetila ohjaamon ja matkustamon välissä, 101 paikkaa).
Pelin vaunu on Meshyn kuori (ovet telien päällä, alareuna 1,25 m) -> tasot sovitettu kuoren sisään:
  alakerta 0,85 m (kiskon yläpinnasta), eteinen/välitaso 1,25 m (oven kynnys), yläkerta 3,00 m, katto 4,8 m (reunoilta kaartuva).
Koordinaatit: Blender X = leveys, Y = pituus (keula -Y), Z = ylös, 0 = kiskon yläpinta (sama kuin kuorella).
"""
import bpy, bmesh, os, sys, json, math
from mathutils import Vector, Matrix
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUTD = argv[argv.index('--out') + 1]
DET = argv[argv.index('--detail') + 1] if '--detail' in argv else 'high'
sys.argv = [sys.argv[0], '--', '--out', OUTD, '--detail', DET]
import juna_blender as J
HI = DET == 'high'

ZL, ZV, ZU = 0.85, 1.25, 2.85          # alakerta, eteinen, yläkerta (silmät 1,68 m lattiasta: yläkerrassa ikkunan korkeudella)
ZLC = 2.70                              # alakerran katto (yläkerran laatan alapinta)
XW = 1.27                               # sisäseinä
STAIR = 2.35                            # portaan pituus (eteinen -> yläkerta)
WIN_Y = [0.9, 2.7, 4.5, 6.3, 8.1]       # ikkunoiden keskikohdat (Meshyn kuori, Ed)
WIN_W = 1.25
WIN_L = (1.80, 2.62); WIN_U = (3.45, 4.50)    # sisäpuolen aukot hieman kuoren maalattuja ikkunoita suuremmat

# päät: s = -1 keula, +1 perä. v0 = eteisen sisäreuna, v1 = eteisen ulkoreuna, door = (keskikohta |Y|, leveys), xs = portaan puoli,
# kind: 'gang' = WC + yhdyskäytävä, 'cab' = ohjaamon seinä
TYPES = {
    'ed': dict(roof=(4.82, 0.85, 4.55), ends={-1: dict(v0=9.2, v1=11.7, door=(10.4, 1.0), dz=3.45, xs=1, kind='gang'),
                                               1: dict(v0=9.2, v1=11.7, door=(10.4, 1.0), dz=3.45, xs=-1, kind='gang')}),
    'edo': dict(roof=(4.70, 0.75, 4.45), ends={-1: dict(v0=8.6, v1=10.75, door=(9.62, 0.9), dz=3.40, xs=1, kind='cab'),
                                                1: dict(v0=9.0, v1=11.7, door=(9.88, 1.2), dz=3.40, xs=-1, kind='gang')}),
}
END = 12.75   # päätyseinä (yhdyskäytävän ovi)

# ---------------------------------------------------------------- materiaalit (VR IC2: vaaleat seinät, sinertävänharmaa verhoilu)
TEXD = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sisa_tex')   # sisa_tex.py
TEXSCALE = {}   # materiaali -> tekstuurin toistoväli (m), laatikkoprojisoidut UV:t join_by_material:issa
def tmat(name, img, scale, rough=0.8, metal=0.0):
    if name in J.MATS: return J.MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(os.path.join(TEXD, img + '.png')); nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    J.MATS[name] = m; TEXSCALE[name] = scale; return m
def M():
    return dict(
        wall=tmat('S_seina', 'seina', 1.8, 0.5),
        ceil=tmat('S_katto', 'katto', 0.6, 0.7),
        carpet=tmat('S_matto', 'matto', 0.7, 0.95),
        vinyl=tmat('S_muovimatto', 'muovimatto', 0.9, 0.6),
        fabric=tmat('S_verhoilu', 'verhoilu', 0.32, 0.95),
        fabric2=tmat('S_verhoilu2', 'verhoilu', 0.32, 0.95),
        grille=tmat('S_saleikko', 'saleikko', 0.16, 0.6),
        glass=J.mat('S_ikkunalasi', J.srgb('#bcd2d8'), 0.0, 0.05, alpha=0.14),
        blind=J.mat('S_verho', J.srgb('#c9c6bd'), 0.0, 0.9),
        alu=J.mat('S_alumiini', J.srgb('#b9bdc0'), 0.7, 0.35),
        plastic=J.mat('S_muovi', J.srgb('#5a5f63'), 0.0, 0.5),
        head=J.mat('S_niskatuki', J.srgb('#cfd3d6'), 0.0, 0.8),
        green=J.mat('S_vihrea', J.srgb('#5cb532'), 0.0, 0.5),
        table=tmat('S_poyta', 'poyta', 0.5, 0.35),
        steel=J.mat('S_teras', J.srgb('#9a9fa3'), 0.8, 0.35),
        dark=J.mat('S_tumma', J.srgb('#2a2d30'), 0.1, 0.6),
        frame=J.mat('S_kehys', J.srgb('#6f7477'), 0.2, 0.5),
        edge=J.mat('S_askelreuna', J.srgb('#e8b923'), 0.0, 0.6),
        lamp=J.mat('S_valo', (1, 1, 0.95), 0.0, 0.3, emit=(0.55, 0.54, 0.5)),
        screen=J.mat('S_naytto', J.srgb('#0d1a24'), 0.0, 0.3),
        text=J.mat('S_teksti', (1, 1, 1), 0.0, 0.5, emit=(0.95, 1, 0.95)),
        sign=J.mat('S_kyltti', J.srgb('#1d5d3a'), 0.0, 0.5),
    )

def B(name, x0, x1, y0, y1, z0, z1, m, parent):
    """laatikko rajoista"""
    if x1 - x0 < 1e-3 or y1 - y0 < 1e-3 or z1 - z0 < 1e-3: return None
    return J.box(name, x1 - x0, y1 - y0, z1 - z0, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), m, parent)

def text(name, s, loc, size, rotz, m, parent, extrude=0.004):
    bpy.ops.object.text_add(location=loc); t = bpy.context.active_object; t.data.body = s; t.data.size = size; t.data.extrude = 0; t.data.resolution_u = 3 if HI else 1
    t.data.align_x = 'CENTER'; t.data.align_y = 'CENTER'; t.rotation_euler = (math.pi / 2, 0, rotz); t.name = name
    bpy.ops.object.convert(target='MESH'); t = bpy.context.active_object; t.data.materials.clear(); t.data.materials.append(m)
    t.parent = parent; return t

# ---------------------------------------------------------------- osat
def rod(name, p0, p1, r, m, parent):
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0; L = d.length
    o = J.box(name, r * 2, L, r * 2, (0, 0, 0), m, parent)
    q = Vector((0, 1, 0)).rotation_difference(d.normalized())
    o.data.transform(Matrix.Translation((p0 + p1) / 2) @ q.to_matrix().to_4x4()); return o

def side_wall(name, sx, y0, y1, zf, zc, wins, mm, root):
    """kylkiseinä X = sx * XW, ikkuna-aukot [(yc, w, z0, z1)]"""
    x0, x1 = (XW, XW + 0.04) if sx > 0 else (-XW - 0.04, -XW)
    ws = sorted([w for w in wins if w[0] - w[1] / 2 > y0 - 1e-6 and w[0] + w[1] / 2 < y1 + 1e-6])
    if not ws: B(name, x0, x1, y0, y1, zf, zc, mm['wall'], root); return
    lo = min(w[2] for w in ws); hi = max(w[3] for w in ws)
    B(name + '_ala', x0, x1, y0, y1, zf, lo, mm['wall'], root)
    B(name + '_yla', x0, x1, y0, y1, hi, zc, mm['wall'], root)
    y = y0
    for i, (yc, w, za, zb) in enumerate(ws):
        B(f'{name}_p{i}', x0, x1, y, yc - w / 2, lo, hi, mm['wall'], root); y = yc + w / 2
        # ikkunan kehys ja lauta
        xi = x0 if sx > 0 else x1
        B(f'{name}_k{i}a', min(xi, xi - sx * 0.05), max(xi, xi - sx * 0.05), yc - w / 2, yc + w / 2, za - 0.05, za, mm['frame'], root)
        B(f'{name}_k{i}b', min(xi, xi - sx * 0.03), max(xi, xi - sx * 0.03), yc - w / 2, yc + w / 2, zb, zb + 0.04, mm['frame'], root)
        if HI:
            for yy in (yc - w / 2, yc + w / 2 - 0.03): B(f'{name}_k{i}c{yy}', min(xi, xi - sx * 0.03), max(xi, xi - sx * 0.03), yy, yy + 0.03, za, zb, mm['frame'], root)
    B(name + '_pl', x0, x1, y, y1, lo, hi, mm['wall'], root)
    # ikkunalasi, rullaverhon kotelo (joka neljäs verho puoliksi alhaalla) ja patterin säleikkö ikkunoiden alla
    for i, (yc, w, za, zb) in enumerate(ws):
        xg = sx * (XW + 0.025)
        B(f'{name}_lasi{i}', xg - 0.002, xg + 0.002, yc - w / 2, yc + w / 2, za, zb, mm['glass'], root)
        xa_, xb_ = (XW - 0.07, XW) if sx > 0 else (-XW, -XW + 0.07)
        J.box(f'{name}_rulla{i}', xb_ - xa_, w - 0.04, 0.06, ((xa_ + xb_) / 2, yc, zb - 0.03), mm['frame'], root, 0.02)
        if int(abs(yc) * 10 + (zf > 2) * 3 + (sx > 0)) % 4 == 0:
            xv = sx * (XW - 0.035); B(f'{name}_verho{i}', xv - 0.003, xv + 0.003, yc - w / 2 + 0.03, yc + w / 2 - 0.03, zb - 0.42, zb - 0.06, mm['blind'], root)
    xa_, xb_ = (XW - 0.05, XW) if sx > 0 else (-XW, -XW + 0.05)
    B(name + '_patteri', xa_, xb_, y0 + 0.05, y1 - 0.05, zf + 0.06, zf + 0.26, mm['grille'], root)

# istuimen sivuprofiili (u = katseen suuntaan istuinosan keskeltä, z = lattiasta): pyöristetty istuinosa, kaareva selkänoja, niskatuki
SEAT_P = [(0.25, 0.30), (0.275, 0.37), (0.265, 0.45), (0.21, 0.495), (0.0, 0.505), (-0.17, 0.49), (-0.215, 0.56), (-0.205, 0.70), (-0.235, 0.88),
          (-0.255, 1.02), (-0.235, 1.12), (-0.265, 1.215), (-0.315, 1.255), (-0.385, 1.235), (-0.37, 1.0), (-0.345, 0.70), (-0.315, 0.45), (-0.28, 0.32), (-0.05, 0.29)]
HEAD_P = [(-0.248, 0.985), (-0.228, 1.12), (-0.258, 1.222), (-0.285, 1.236), (-0.252, 1.12), (-0.272, 0.985)]
def extrude(name, prof, x0, x1, yc, f, zf, m, parent, bev=0.0):
    bm = bmesh.new()
    a = [bm.verts.new((x0, yc + f * u, zf + z)) for u, z in prof]; b = [bm.verts.new((x1, yc + f * u, zf + z)) for u, z in prof]
    n = len(prof); bm.faces.new(a[::-1]); bm.faces.new(b)
    for i in range(n): k = (i + 1) % n; bm.faces.new((a[i], a[k], b[k], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bev > 0 and HI:
        caps = [e for e in bm.edges if all(abs(v.co.x - x0) < 1e-6 for v in e.verts) or all(abs(v.co.x - x1) < 1e-6 for v in e.verts)]
        bmesh.ops.bevel(bm, geom=caps, offset=bev, segments=2, affect='EDGES', profile=0.5)
    return J.obj_from(bm, name, m, parent)

def seat_pair(name, sx, yc, f, zf, mm, root, fab=None):
    """kahden istuimen penkki: sx kylki (-1/1), yc istuinosan keskikohta, f = katseen suunta (+1 = +Y)"""
    fab = fab or mm['fabric']
    xa, xb = (0.36, 1.24) if sx > 0 else (-1.24, -0.36)
    w = (xb - xa) / 2
    for k in range(2):
        x0, x1 = xa + k * w + 0.012, xa + (k + 1) * w - 0.012
        extrude(f'{name}_s{k}', SEAT_P, x0, x1, yc, f, zf, fab, root, 0.028)
        extrude(f'{name}_n{k}', HEAD_P, x0 + 0.05, x1 - 0.05, yc, f, zf, mm['head'], root, 0.008)
    # runko: alumiininen jalusta ja kiinnitys seinään, selkänojan takana kahva käytävän puolella
    B(name + '_jalka', xa + 0.25, xb - 0.25, yc - f * 0.05 - 0.04, yc - f * 0.05 + 0.04, zf, zf + 0.30, mm['alu'], root)
    B(name + '_jalka2', xa + 0.1, xb - 0.1, yc - 0.18, yc + 0.18, zf + 0.26, zf + 0.30, mm['alu'], root)
    xr = xa if sx > 0 else xb
    rod(name + '_kahva', (xr + sx * 0.04, yc - f * 0.36, zf + 1.17), (xr + sx * 0.04, yc - f * 0.40, zf + 1.24), 0.014, mm['steel'], root)
    # käsinojat (pyöristetyt): käytävän puoli ja keskellä
    for k, xx in enumerate((xa - 0.005, xa + w - 0.025) if sx > 0 else (xb - 0.045, xa + w - 0.025)):
        o = J.box(f'{name}_kasi{k}', 0.05, 0.4, 0.055, (xx + 0.025, yc - f * 0.02, zf + 0.655), mm['plastic'], root, 0.02)
def bay(name, sx, c, zf, mm, root, table=True):
    """pöytäosasto: kaksi penkkiä vastakkain ikkunan kohdalla"""
    seat_pair(name + 'a', sx, c - 0.5, 1, zf, mm, root)
    seat_pair(name + 'b', sx, c + 0.5, -1, zf, mm, root, mm['fabric'])
    if table:
        xa, xb = (0.62, 1.25) if sx > 0 else (-1.25, -0.62)
        B(name + '_poyta', xa, xb, c - 0.22, c + 0.22, zf + 0.72, zf + 0.75, mm['table'], root)
        B(name + '_poytaj', xb - 0.05 if sx > 0 else xa, xb if sx > 0 else xa + 0.05, c - 0.05, c + 0.05, zf + 0.4, zf + 0.72, mm['steel'], root)
        J.box(name + '_poytareuna', xb - xa, 0.03, 0.035, ((xa + xb) / 2, c - 0.22, zf + 0.735), mm['plastic'], root, 0.012)
        J.box(name + '_poytareuna2', xb - xa, 0.03, 0.035, ((xa + xb) / 2, c + 0.22, zf + 0.735), mm['plastic'], root, 0.012)
        # roskis ja pistorasiat seinässä pöydän alla
        xa2, xb2 = (1.10, 1.24) if sx > 0 else (-1.24, -1.10)
        J.box(name + '_roskis', xb2 - xa2, 0.26, 0.26, ((xa2 + xb2) / 2, c, zf + 0.44), mm['plastic'], root, 0.02)
        xs_ = sx * 1.262
        for d in (-0.07, 0.07): B(f'{name}_pistorasia{d}', xs_ - 0.008, xs_ + 0.008, c + d - 0.035, c + d + 0.035, zf + 0.6, zf + 0.67, mm['dark'], root)

def light_strip(name, y0, y1, z, mm, root, w=0.12):
    return B(name, -w / 2, w / 2, y0, y1, z - 0.02, z, mm['lamp'], root)

def stairs(name, xs, ya, yb, za, zb, mm, root, n=None):
    """porras puolikkaalle leveydelle: Y ya -> yb, korkeus za -> zb"""
    n = n or max(1, int(round(abs(zb - za) / 0.19)))
    x0, x1 = (0.08, XW) if xs > 0 else (-XW, -0.08)
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        y_0, y_1 = ya + (yb - ya) * t0, ya + (yb - ya) * t1
        z = za + (zb - za) * (i + 1) / n
        B(f'{name}_{i}', x0, x1, min(y_0, y_1), max(y_0, y_1), min(za, zb) - 0.05, z, mm['vinyl'], root)
        yl = y_0 if abs(y_0 - ya) < abs(y_1 - ya) else y_1
        B(f'{name}_r{i}', x0, x1, min(yl, yl + math.copysign(0.04, yb - ya)), max(yl, yl + math.copysign(0.04, yb - ya)), z - 0.01, z + 0.002, mm['edge'], root)
    # kaide sisäreunalla
    xr = 0.1 if xs > 0 else -0.1
    p0 = Vector((xr, ya, za + 0.9)); p1 = Vector((xr, yb, zb + 0.9)); L = (p1 - p0).length
    rod(name + '_kaide', p0, p1, 0.022, mm['steel'], root)
    for t in (0.05, 0.5, 0.95):
        p = p0.lerp(p1, t); J.cyl(f'{name}_tolppa{t}', 0.018, 0.9, (p.x, p.y, p.z - 0.45), mm['steel'], 'Z', root, seg=6)

# ---------------------------------------------------------------- vaunu
def build(name):
    T = TYPES[name]; mm = M(); root = J.empty(name.capitalize() + '_sisa')
    rects = []   # kävelyalueet: [x0, x1, y0, y1, z(y0), z(y1), tyyppi]
    def R(x0, x1, y0, y1, za, zb=None, kind=0): rects.append([round(x0, 3), round(x1, 3), round(y0, 3), round(y1, 3), round(za, 3), round(za if zb is None else zb, 3), kind])
    rz, rx, rzs = T['roof']
    E = T['ends']
    # rajat Y-suunnassa (negatiivinen = keula)
    def Yof(s, u): return s * u
    Lf, Lr = E[-1]['v0'] - 2.6, E[1]['v0'] - 2.6           # alakerran täysleveä osa
    Uf, Ur = E[-1]['v0'] - STAIR, E[1]['v0'] - STAIR       # yläkerran täysleveä osa

    # --- alakerta
    B('ala_lattia', -XW, XW, -Lf, Lr, ZL - 0.05, ZL, mm['carpet'], root)
    R(-0.34, 0.34, -Lf, Lr, ZL)
    # --- yläkerta (laatta = alakerran katto)
    B('yla_lattia', -XW, XW, -Uf, Ur, ZLC, ZU, mm['carpet'], root)
    B('ala_katto', -XW, XW, -Uf, Ur, ZLC - 0.01, ZLC, mm['ceil'], root)
    R(-0.34, 0.34, -Uf, Ur, ZU)
    # yläkerran katto: tasainen keskiosa + vinot reunat
    for s in (-1, 1):
        pass
    B('yla_katto', -rx, rx, -E[-1]['v0'] + 0.2, E[1]['v0'] - 0.2, rz, rz + 0.04, mm['ceil'], root)
    for sx in (-1, 1):
        L = math.hypot(XW - rx, rz - rzs); a = math.atan2(rz - rzs, XW - rx)
        o = J.box(f'yla_vino{sx}', L + 0.02, E[-1]['v0'] + E[1]['v0'] - 0.4, 0.03, (0, (E[1]['v0'] - E[-1]['v0']) / 2, 0), mm['ceil'], root)
        o.data.transform(Matrix.Rotation(sx * a, 4, 'Y'))
        o.data.transform(Matrix.Translation(Vector((sx * (XW + rx) / 2, 0, (rz + rzs) / 2))))
    for xo in (-0.45, 0.45):      # valonauhat katon reunoissa (kuten IC2:ssa), ei häikäisevää keskinauhaa
        o = light_strip(f'yla_valo{xo}', -Uf + 0.3, Ur - 0.3, rz - 0.005, mm, root, 0.06); o.data.transform(Matrix.Translation(Vector((xo * (rx / 0.85) * 0.9, 0, 0))))
        o = light_strip(f'ala_valo{xo}', -Lf + 0.3, Lr - 0.3, ZLC - 0.012, mm, root, 0.06); o.data.transform(Matrix.Translation(Vector((xo * 1.6, 0, 0))))

    # --- penkit: pöytäosastot ikkunoiden kohdalla (molemmat kerrokset), ulommat rivit
    nseat = 0
    for zf, lim, tag in ((ZL, min(Lf, Lr), 'a'), (ZU, min(Uf, Ur), 'y')):
        for c in (-4.5, -2.7, -0.9, 0.9, 2.7, 4.5):
            if abs(c) + 0.9 > lim + 0.01: continue
            for sx in (-1, 1): bay(f'os_{tag}{c}{sx}', sx, c, zf, mm, root); nseat += 4
    # --- lukuvalot penkkien yllä ja infonäytöt matkustamon päissä
    rz_, rx_, rzs_ = T['roof']
    for zf, zc, lim, tag in ((ZL, ZLC - 0.012, min(Lf, Lr), 'a'), (ZU, None, min(Uf, Ur), 'y')):
        for c in (-4.5, -2.7, -0.9, 0.9, 2.7, 4.5):
            if abs(c) + 0.9 > lim + 0.01: continue
            for sx in (-1, 1):
                for d in (-0.5, 0.5):
                    if zc is None:
                        xl = 1.02; zl = rzs_ + (XW - xl) / (XW - rx_) * (rz_ - rzs_) - 0.03
                    else: xl, zl = 0.85, zc - 0.01
                    B(f'lukuvalo_{tag}{c}{sx}{d}', sx * xl - 0.05, sx * xl + 0.05, c + d - 0.05, c + d + 0.05, zl - 0.015, zl, mm['lamp'], root)
    nayttoT = J.mat('S_naytto_t', (1, 0.8, 0.2), 0, 0.5, emit=(1, 0.75, 0.15))
    for zc, lim, tag in ((ZLC, min(Lf, Lr), 'a'), (rz_, min(Uf, Ur), 'y')):
        for s2 in (-1, 1):
            yd = s2 * (lim - 0.4)
            B(f'info_{tag}{s2}', -0.42, 0.42, yd - 0.03, yd + 0.03, zc - 0.26, zc - 0.06, mm['screen'], root)
            B(f'info_kiinn_{tag}{s2}', -0.02, 0.02, yd - 0.01, yd + 0.01, zc - 0.07, zc, mm['steel'], root)
            text(f'info_t_{tag}{s2}', 'Seuraava: Tampere', (0, yd - s2 * 0.035, zc - 0.16), 0.07, 0 if s2 > 0 else math.pi, nayttoT, root)
    # --- päät
    for s in (-1, 1):
        e = E[s]; v0, v1, xs = e['v0'], e['v1'], e['xs']
        dc, dw = e['door']; dz = e['dz']
        ns = -xs   # porrasta vastakkainen puoli
        def nsx(a, b):  # X-väli vastakkaisella puolella (a..b etäisyys keskeltä)
            return (a, b) if ns > 0 else (-b, -a)
        def ssx(a, b):
            return (a, b) if xs > 0 else (-b, -a)
        def yr(u0, u1): a, b = s * u0, s * u1; return (min(a, b), max(a, b))
        Lx, Ux = v0 - 2.6, v0 - STAIR
        # alakerran pääty: vastakkaisella puolella avoin tila (matkatavarat / pyörätuolit) eteisen portaille asti
        x0, x1 = nsx(0.0, XW); y0, y1 = yr(Lx, v0 - 0.6)
        B(f'ala_pa{s}', x0, x1, y0, y1, ZL - 0.05, ZL, mm['carpet'], root); xr0, xr1 = nsx(0.0, 0.72); R(xr0, xr1, y0, y1, ZL)
        # alakerran askelma eteiseen (2 askelmaa)
        y0, y1 = yr(v0 - 0.6, v0)
        for i in range(2):
            ya_, yb_ = yr(v0 - 0.6 + 0.3 * i, v0 - 0.3 + 0.3 * i)
            B(f'ala_askel{s}{i}', x0, x1, ya_, yb_, ZL - 0.05, ZL + 0.2 * (i + 1), mm['vinyl'], root)
            ye = ya_ if s > 0 else yb_ - 0.04
            B(f'ala_askelr{s}{i}', x0, x1, ye, ye + 0.04, ZL + 0.2 * (i + 1) - 0.01, ZL + 0.2 * (i + 1) + 0.002, mm['edge'], root)
        R(x0, x1, y0, y1, ZL if s > 0 else ZV, ZV if s > 0 else ZL)
        # alakerran katto vastakkaisella puolella = yläkerran laajennus
        y0, y1 = yr(Ux, v0 - 0.2)
        B(f'yla_pa{s}', x0, x1, y0, y1, ZLC, ZU, mm['carpet'], root); B(f'ala_kattopa{s}', x0, x1, y0, y1, ZLC - 0.01, ZLC, mm['ceil'], root)
        xr0, xr1 = nsx(0.0, XW - 0.05); y0, y1 = yr(Ux, v0 - 1.38); R(xr0, xr1, y0, y1, ZU)
        # yläkerran poikkikäytävä portaan yläpäässä
        y0, y1 = yr(max(5.45, Ux - 0.9), Ux)
        R(-XW + 0.05, XW - 0.05, y0, y1, ZU)
        # alakerran poikkikäytävä (portaan alla oleva seinä alkaa Lx:stä)
        y0, y1 = yr(max(5.45, Lx - 0.9), Lx)
        R(-XW + 0.05, XW - 0.05, y0, y1, ZL)
        # matkatavarateline alakerran päätyyn ja yläkerran päätyyn (vastakkainen puoli, ulkoseinää vasten)
        for zf, tag in ((ZL, 'a'),):
            xa, xb = nsx(XW - 0.5, XW - 0.02); ya_, yb_ = yr(v0 - 1.75, v0 - 0.85) if tag == 'a' else yr(v0 - 1.4, v0 - 0.5)
            B(f'teline_{tag}{s}', xa, xb, ya_, yb_, zf, zf + 0.03, mm['steel'], root)
            B(f'teline_{tag}{s}b', xa, xb, ya_, yb_, zf + 0.75, zf + 0.78, mm['steel'], root)
            for yy in (ya_, yb_ - 0.03): B(f'teline_{tag}{s}p{yy}', xa, xb, yy, yy + 0.03, zf, zf + 1.4 if tag == 'a' else zf + 1.2, mm['steel'], root)
        # porras eteisestä yläkertaan
        stairs(f'porras{s}', xs, s * v0, s * Ux, ZV, ZU, mm, root)
        x0, x1 = ssx(0.08, XW); y0, y1 = yr(Ux, v0)
        R(x0, x1, y0, y1, ZU if s > 0 else ZV, ZV if s > 0 else ZU)
        # portaan alla umpinainen: seinä portaan sisäreunassa ja pääty alakertaan
        xw = 0.06 if xs > 0 else -0.10; y0, y1 = yr(Lx, v0)
        B(f'portaanalus{s}', xw, xw + 0.04, y0, y1, ZL, ZV, mm['wall'], root)
        y0b, y1b = yr(Lx, v0 - 0.6); B(f'portaanalus_k{s}', xw, xw + 0.04, y0b, y1b, ZV, ZLC, mm['wall'], root)
        x0, x1 = ssx(0.06, XW); ye = s * Lx
        B(f'portaanpaaty{s}', x0, x1, ye - 0.02, ye + 0.02, ZL, ZLC, mm['wall'], root)
        # portaan alla kolmio (porrasaukon kylki): seinä X = xs*0.06 portaan alta alakerran puolelta ... (portaan alapinta)
        y0, y1 = yr(Lx, Ux) if Ux > Lx else (0, 0)
        if y1 > y0: B(f'portaanalus_l{s}', x0, x1, y0, y1, ZL, ZLC, mm['wall'], root)
        # yläkerran kaide porrasaukon reunalla
        xr = 0.07 if xs > 0 else -0.07; y0, y1 = yr(Ux, v0 - 0.2)
        J.cyl(f'yla_kaide{s}', 0.022, y1 - y0, (xr, (y0 + y1) / 2, ZU + 0.95), mm['steel'], 'Y', root, seg=8)
        B(f'yla_kaidelasi{s}', xr - 0.01, xr + 0.01, y0, y1, ZU, ZU + 0.92, J.mat('S_lasi', J.srgb('#cfe3e6'), 0.0, 0.1, alpha=0.25), root)
        # yläkerran päätyseinä (porrasaukon yllä eteisen kohdalla) ja vastakkaisen puolen päätyseinä
        ye = s * (v0 - 0.2)
        x0, x1 = nsx(0.0, XW); B(f'yla_paaty{s}', x0, x1, ye - 0.02, ye + 0.02, ZU, rz + 0.04, mm['wall'], root)
        ye = s * v0; x0, x1 = ssx(0.0, XW); B(f'eteinen_yla{s}', x0, x1, ye - 0.02, ye + 0.02, 3.35, rz + 0.04, mm['wall'], root)
        # yläkerran WC (vastakkainen puoli, päätyseinää vasten)
        xa, xb = nsx(XW - 0.95, XW); ya_, yb_ = yr(v0 - 0.2 - 1.1 + 0.0, v0 - 0.2)
        if True:
            yi = s * (v0 - 1.3)
            B(f'wc_yla{s}', xa, xb, yi - 0.02, yi + 0.02, ZU, ZU + 1.85, mm['wall'], root)
            xi = xa if ns > 0 else xb
            B(f'wc_yla_s{s}', xi - 0.02, xi + 0.02, ya_, yb_, ZU, ZU + 1.85, mm['wall'], root)
            dx0, dx1 = nsx(XW - 0.8, XW - 0.15)
            B(f'wc_yla_ovi{s}', dx0, dx1, yi - s * 0.035 - 0.01, yi - s * 0.035 + 0.01, ZU, ZU + 1.75, mm['frame'], root)
            text(f'wc_yla_t{s}', 'WC', ((dx0 + dx1) / 2, yi - s * 0.05, ZU + 1.55), 0.12, 0 if s > 0 else math.pi, mm['text'], root)
        # eteinen
        y0, y1 = yr(v0, v1)
        B(f'eteinen_lattia{s}', -XW, XW, y0, y1, ZV - 0.05, ZV, mm['vinyl'], root)
        B(f'eteinen_katto{s}', -XW, XW, y0, y1, 3.35, 3.37, mm['ceil'], root)
        light_strip(f'eteinen_valo{s}', y0 + 0.3, y1 - 0.3, 3.345, mm, root, 0.3)
        R(-XW + 0.05, XW - 0.05, y0, y1, ZV)
        # ovien kohdat: kylkiseinässä aukko, porraskaivo ulos (kynnys 1,25 -> askelma 0,90 -> laituri 0,55)
        for sx in (-1, 1):
            dy0, dy1 = s * dc - dw / 2, s * dc + dw / 2
            xo, xi_ = (XW, 1.9) if sx > 0 else (-1.9, -XW)
            R(min(sx * (XW - 0.05), sx * 1.32), max(sx * (XW - 0.05), sx * 1.32), dy0 + 0.08, dy1 - 0.08, ZV, None, 'd' + ('R' if sx > 0 else 'L'))
            R(min(sx * 1.32, sx * 1.95), max(sx * 1.32, sx * 1.95), dy0 + 0.08, dy1 - 0.08, 0.92, None, 'd' + ('R' if sx > 0 else 'L'))
            xa, xb = (1.30, 1.55) if sx > 0 else (-1.55, -1.30)
            B(f'ovikaivo{s}{sx}', xa, xb, dy0, dy1, 0.85, 0.92, mm['vinyl'], root)
            B(f'ovikaivor{s}{sx}', xa, xb, dy0, dy1, 0.92, 0.93, mm['edge'], root)
            # oven pielet ja kynnyksen keltainen reuna
            for yy in (dy0 - 0.06, dy1):
                B(f'ovipieli{s}{sx}{yy}', min(sx * XW, sx * 1.5), max(sx * XW, sx * 1.5), yy, yy + 0.06, ZV, dz, mm['frame'], root)
            B(f'ovikynnys{s}{sx}', min(sx * 1.22, sx * 1.30), max(sx * 1.22, sx * 1.30), dy0, dy1, ZV - 0.01, ZV + 0.003, mm['edge'], root)
            B(f'oviylä{s}{sx}', min(sx * XW, sx * 1.5), max(sx * XW, sx * 1.5), dy0, dy1, dz, 3.37, mm['frame'], root)
            # kaide oven vieressä
            J.cyl(f'ovikaide{s}{sx}', 0.02, 1.2, (sx * 1.18, s * dc + (dw / 2 + 0.1) * (-1 if s > 0 else 1), ZV + 0.95), mm['steel'], 'Z', root, seg=8)
        # eteisen kylkiseinät oven ympärillä
        for sx in (-1, 1):
            side_wall(f'eteinen_seina{s}{sx}a', sx, y0, min(s * dc - dw / 2, s * dc + dw / 2) - 0.06, ZV, 3.37, [], mm, root)
            side_wall(f'eteinen_seina{s}{sx}b', sx, max(s * dc - dw / 2, s * dc + dw / 2) + 0.06, y1, ZV, 3.37, [], mm, root)
        # eteisen opasteet ja näyttö
        ys = s * (v0 + 0.02)
        x0, x1 = nsx(0.25, XW - 0.1)
        B(f'opaste_ala{s}', x0, x1, ys - 0.01 if s > 0 else ys - 0.01, ys + 0.01, 2.45, 2.75, mm['sign'], root)
        text(f'opaste_ala_t{s}', 'Alakerta  1–56' if name == 'ed' else 'Alakerta', ((x0 + x1) / 2, ys + s * 0.015, 2.6), 0.11, math.pi if s > 0 else 0, mm['text'], root)
        x0, x1 = ssx(0.25, XW - 0.1)
        B(f'opaste_yla{s}', x0, x1, ys - 0.01, ys + 0.01, 2.95, 3.25, mm['sign'], root)
        text(f'opaste_yla_t{s}', 'Yläkerta  57–113' if name == 'ed' else 'Yläkerta', ((x0 + x1) / 2, ys + s * 0.015, 3.1), 0.11, math.pi if s > 0 else 0, mm['text'], root)
        yd = s * (v1 - 0.03)
        B(f'naytto{s}', -0.55, 0.55, yd - 0.02, yd + 0.02, 2.75, 3.05, mm['screen'], root)
        text(f'naytto_t{s}', 'IC 45  Pori – Tampere', (0, yd - s * 0.025, 2.9), 0.085, 0 if s > 0 else math.pi, J.mat('S_naytto_t', (1, 0.8, 0.2), 0, 0.5, emit=(1, 0.75, 0.15)), root)
        # päätyseinä eteisen ulkoreunassa
        ye = s * v1
        if e['kind'] == 'cab':
            B(f'ohjaamo_seina{s}', -XW, XW, ye - 0.03, ye + 0.03, ZV, 3.37, mm['wall'], root)
            B(f'ohjaamo_ovi{s}', -0.42, 0.42, ye - s * 0.035 - 0.01, ye - s * 0.035 + 0.01, ZV, ZV + 1.95, mm['frame'], root)
            B(f'ohjaamo_kyltti{s}', -0.3, 0.3, ye - s * 0.05 - 0.005, ye - s * 0.05 + 0.005, ZV + 1.4, ZV + 1.6, J.mat('S_punainen', J.srgb('#b3261e'), 0, 0.5), root)
            text(f'ohjaamo_t{s}', 'Ohjaamo – pääsy kielletty', (0, ye - s * 0.058, ZV + 1.5), 0.045, 0 if s > 0 else math.pi, mm['text'], root)
        else:
            # WC ja käytävä yhdyskäytävälle
            for sx in (-1, 1):
                xa, xb = (0.45, XW) if sx > 0 else (-XW, -0.45)
                B(f'paaty_seina{s}{sx}', xa, xb, ye - 0.03, ye + 0.03, ZV, 3.37, mm['wall'], root)
            B(f'paaty_yla{s}', -0.45, 0.45, ye - 0.03, ye + 0.03, 3.25, 3.37, mm['wall'], root)
            y0, y1 = yr(v1, END)
            B(f'paaty_lattia{s}', -XW, XW, y0, y1, ZV - 0.05, ZV, mm['vinyl'], root)
            B(f'paaty_katto{s}', -XW, XW, y0, y1, 3.25, 3.27, mm['ceil'], root)
            light_strip(f'paaty_valo{s}', y0 + 0.2, y1 - 0.2, 3.245, mm, root, 0.12)
            for sx in (-1, 1):
                xa, xb = (0.45, XW) if sx > 0 else (-XW, -0.45)
                B(f'kaytava_s{s}{sx}', (xa if sx > 0 else xb - 0.04), (xa + 0.04 if sx > 0 else xb), y0, y1, ZV, 3.25, mm['wall'], root)
            # WC (Ed: molemmissa päissä alakerran tasolla), ovi käytävään
            xa, xb = ns * 0.47, ns * XW
            text(f'wc_t{s}', 'WC', (ns * 0.42, s * (v1 + 0.5), ZV + 1.6), 0.12, -math.pi / 2 * ns, mm['text'], root)
            B(f'wc_ovi{s}', min(ns * 0.43, ns * 0.47), max(ns * 0.43, ns * 0.47), s * (v1 + 0.5) - 0.32, s * (v1 + 0.5) + 0.32, ZV, ZV + 1.85, mm['frame'], root)
            # päätyovi (avoin karmi) ja yhdyskäytävä
            ye2 = s * END
            for sx in (-1, 1):
                B(f'gw_seina{s}{sx}', min(sx * 0.45, sx * XW), max(sx * 0.45, sx * XW), ye2 - 0.03, ye2 + 0.03, ZV, 3.25, mm['wall'], root)
                B(f'gw_karmi{s}{sx}', min(sx * 0.42, sx * 0.47), max(sx * 0.42, sx * 0.47), ye2 - 0.05, ye2 + 0.05, ZV, 3.2, mm['frame'], root)
            B(f'gw_yla{s}', -0.47, 0.47, ye2 - 0.05, ye2 + 0.05, 3.1, 3.25, mm['frame'], root)
            B(f'gw_lattia{s}', -0.45, 0.45, min(ye2, s * 13.02), max(ye2, s * 13.02), ZV - 0.04, ZV, mm['dark'], root)
            for sx in (-1, 1): B(f'gw_palje{s}{sx}', min(sx * 0.45, sx * 0.5), max(sx * 0.45, sx * 0.5), min(ye2, s * 13.02), max(ye2, s * 13.02), ZV, 3.15, mm['dark'], root)
            B(f'gw_palje_k{s}', -0.5, 0.5, min(ye2, s * 13.02), max(ye2, s * 13.02), 3.12, 3.17, mm['dark'], root)
            y0, y1 = yr(v1, 13.06)
            R(-0.4, 0.4, y0, y1, ZV, None, 'g' + ('+' if s > 0 else '-'))
        # vastakkaisen puolen alakerran tila: pyörätuolipaikat (Edo keula) tai matkatavarat
        if name == 'edo' and s == -1:
            x0, x1 = nsx(0.6, XW - 0.05)
            B('pyoratuoli_merkki', x0, x1, -(Lx + 0.9), -(Lx + 0.05), ZL, ZL + 0.003, J.mat('S_sininen', J.srgb('#1f5fa8'), 0, 0.6), root)
            for k in range(2):
                yy = -(Lx + 0.3 + k * 0.5)
                B(f'klaffi{k}', x0 + 0.1 if ns > 0 else x1 - 0.5, x0 + 0.5 if ns > 0 else x1 - 0.1, yy - 0.2, yy + 0.2, ZL + 0.45, ZL + 0.5, mm['fabric'], root)

    # --- kylkiseinät ja ikkunat (molemmat kerrokset, keskiosa)
    wins = [(y, WIN_W) for y in WIN_Y] + [(-y, WIN_W) for y in WIN_Y]
    for sx in (-1, 1):
        # alakerta: täysi leveys + portaattoman puolen pääty
        a0 = -E[-1]['v0'] if (sx == -E[-1]['xs']) else -Lf
        a1 = E[1]['v0'] if (sx == -E[1]['xs']) else Lr
        side_wall(f'ala_seina{sx}', sx, a0, a1, ZL, ZLC, [(y, w, *WIN_L) for y, w in wins], mm, root)
        a0 = -(E[-1]['v0'] - 0.2) if (sx == -E[-1]['xs']) else -E[-1]['v0']
        a1 = (E[1]['v0'] - 0.2) if (sx == -E[1]['xs']) else E[1]['v0']
        side_wall(f'yla_seina{sx}', sx, a0, a1, ZU, rzs + 0.02, [(y, w, *WIN_U) for y, w in wins], mm, root)
        # portaiden kohdalla kylkiseinä eteisen ja alakerran välissä (portaan puoli)
        for s in (-1, 1):
            if sx != E[s]['xs']: continue
            u0, u1 = E[s]['v0'] - 2.6, E[s]['v0']
            side_wall(f'porras_seina{s}{sx}', sx, min(s * u0, s * u1), max(s * u0, s * u1), ZL, ZU, [], mm, root)
    # alakerran päätyseinät portaattomalla puolella (askelmien ohi eteiseen on aukko) – ei tarvita
    print(name, 'istumapaikkoja', nseat, 'kävelyalueita', len(rects))
    return root, rects

def boxuv(ob, sc):
    """laatikkoprojektio: pinnan normaalin pääakselin mukaan, sc metriä per tekstuuri (kohteen kärkipisteet ovat maailman koordinaateissa)"""
    me = ob.data; M_ = ob.matrix_world
    uv = me.uv_layers[0] if me.uv_layers else me.uv_layers.new(name='UVMap')
    for p in me.polygons:
        n = p.normal; ax = max(range(3), key=lambda i: abs(n[i]))
        for li in p.loop_indices:
            v = M_ @ me.vertices[me.loops[li].vertex_index].co
            a, b = (v.x, v.y) if ax == 2 else (v.y, v.z) if ax == 0 else (v.x, v.z)
            uv.data[li].uv = (a / sc, b / sc)

def join_by_material(root):
    objs = [o for o in bpy.data.objects if o.type == 'MESH']
    by = {}
    for o in objs:
        m = o.data.materials[0].name if o.data.materials else ''
        by.setdefault(m, []).append(o)
    for m, L in by.items():
        bpy.ops.object.select_all(action='DESELECT')
        for o in L:
            mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw; o.select_set(True)
        bpy.context.view_layer.objects.active = L[0]
        if len(L) > 1: bpy.ops.object.join()
        ob = bpy.context.view_layer.objects.active; ob.name = 'sisa_' + m; ob.parent = root
        if m in TEXSCALE: boxuv(ob, TEXSCALE[m])

os.makedirs(OUTD, exist_ok=True)
meta = {}
for name in ('ed', 'edo'):
    J.clear()
    root, rects = build(name)
    join_by_material(root)
    J.export(root, name + '_sisa')
    meta[name] = dict(rects=rects, z=dict(ala=ZL, eteinen=ZV, yla=ZU))
if HI:
    json.dump(meta, open(os.path.join(OUTD, 'sisa.json'), 'w'), separators=(',', ':'))
    print('sisa.json', {k: len(v['rects']) for k, v in meta.items()})
