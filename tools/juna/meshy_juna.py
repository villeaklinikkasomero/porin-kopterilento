# -*- coding: utf-8 -*-
"""IC-junan korit Meshystä (omistajan mallit 21.11.2026) + skriptin telit, pyöräkerrat, puskimet ja kytkimet.
Ajo: bl313/bin/python meshy_juna.py -- --src <kansio jossa loco.glb dd.glb horizon.glb> --out ../juna [--detail high|low]
- Meshyn telit ja alusta leikataan pois (kasvot, joiden keskipiste on rungon alareunan alapuolella), koska korit venytetään oikeisiin mittoihin
  epätasaisesti (pyörät olisivat soikeita) ja pelin telien pitää kääntyä erikseen.
- Kori: harvennus (Decimate), venytys oikeisiin mittoihin, keula -Y (glTF +Z), tekstuurit 2048 / 1024 px.
"""
import bpy, bmesh, os, sys, math
from mathutils import Matrix, Vector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
SRC = argv[argv.index('--src') + 1]
OUTD = argv[argv.index('--out') + 1]
DET = argv[argv.index('--detail') + 1] if '--detail' in argv else 'high'
sys.argv = [sys.argv[0], '--', '--out', OUTD, '--detail', DET]
import juna_blender as J

# lähde, leikkauskorkeus ja katon korkeus (Meshyn y), kohdemitat: korin pituus ilman puskimia, leveys, alareuna, katon korkeus (Sr3: 3,95 m, laskettu virroitin 4,25 m)
SPEC = {
    'sr3': dict(src='sr3_vr.glb', cut=1.1, roof=4.25, L=18.1, W=3.0, zb=1.08, zt=4.25, bufo=-0.3, bog=4.75, r=0.625, wb=3.0, heavy=True, tris=60000),
    'ed':  dict(src='ic2.glb', cut=1.25, cutx=0, bufo=-0.445, roof=5.1, L=25.9, W=3.18, zb=1.25, zt=5.05, bog=9.5, r=0.46, wb=2.5, heavy=False, tris=50000),
    'edo': dict(src='edo_vr.glb', cut=1.25, cutx=0, bufo=-0.445, roof=5.1, flip=True, L=25.9, W=3.18, zb=1.25, zt=5.05, bog=9.5, r=0.46, wb=2.5, heavy=False, tris=50000),
}
# ovet (Meshyn maalattujen ovien kohdat, mitattu sivukuvasta 21.11.): keskikohta Y (keula -Y), leveys, yläreuna, lehtiä
DOORS = {'ed': [(-10.4, 1.0, 3.45, 1), (10.4, 1.0, 3.45, 1)], 'edo': [(-9.62, 0.9, 3.4, 2), (9.88, 1.2, 3.4, 2)]}
GANG = {'ed': (-1, 1), 'edo': (1,)}   # päät, joissa yhdyskäytävä seuraavaan vaunuun
ONLY = argv[argv.index('--only') + 1].split(',') if '--only' in argv else None
TEX = 4096 if DET == 'high' else 1024      # 21.11.2026 (omistaja: "saako junaa poltettua paremmaksi"): värikartta täysikokoisena (Meshy 4096)
TEXO = 2048 if DET == 'high' else 1024     # normaali- ja ORM-kartat

def build(name, S):
    J.clear()
    for im in list(bpy.data.images): bpy.data.images.remove(im)
    bpy.ops.import_scene.gltf(filepath=os.path.join(SRC, S['src']))
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    for o in meshes: o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1: bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM'); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for o in list(bpy.data.objects):
        if o.type != 'MESH': bpy.data.objects.remove(o, do_unlink=True)
    me = ob.data
    # Blender: X = pituus, Y = -leveys (glTF z), Z = korkeus
    bm = bmesh.new(); bm.from_mesh(me)
    cx0 = S.get('cutx', 0)
    dead = [f for f in bm.faces if (c := f.calc_center_median()).z < S['cut'] and abs(c.x) > cx0]   # cutx: matala keskiosa (alakerta) säilyy, telit päistä pois
    bmesh.ops.delete(bm, geom=dead, context='FACES')
    xs = [v.co.x for v in bm.verts]; ys = [v.co.y for v in bm.verts]; zs = [v.co.z for v in bm.verts]
    x0, x1, y0, y1, z1 = min(xs), max(xs), min(ys), max(ys), max(zs)
    sx = S['L'] / (x1 - x0); sw = S['W'] / (y1 - y0); sz = (S['zt'] - S['zb']) / (S['roof'] - S['cut'])   # katon (ei virroittimen) korkeus oikeaksi
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    for v in bm.verts:
        x, y, z = (v.co.x - cx) * sx, (v.co.y - cy) * sw, (v.co.z - S['cut']) * sz + S['zb']
        v.co = Vector((-y, x, z)) if S.get('flip') else Vector((y, -x, z))   # keula -Y (glTF +Z); ohjausvaunun ohjaamo on Meshyssä -X-päässä
    # sisätilat (omistaja 21.11.: "kyytiin matkaan"): ovien ja yhdyskäytävien kohdalta kuori auki
    if name in DOORS:
        bm.faces.ensure_lookup_table()
        def hole(f):
            c = f.calc_center_median()
            for (yc, w, zt, n) in DOORS[name]:
                if abs(c.x) > 1.0 and abs(c.y - yc) < w / 2 - 0.02 and 1.22 < c.z < zt - 0.03: return True
            for s in GANG[name]:
                if s * c.y > 12.2 and abs(c.x) < 0.48 and 1.22 < c.z < 3.3: return True
            return False
        bm.normal_update()
        # sisäänpäin katsovat pinnat (Meshyn ikkunakehysten sisäreunat): ulkoa ne ovat selkäpuolia eli näkymättömiä, sisältä ne näkyivät mustina kaarina ikkunoissa
        def inward(f):
            c = f.calc_center_median()
            if not (abs(c.x) > 0.8 and 1.3 < c.z < 4.9 and abs(c.y) < 12.3): return False
            nx = f.normal.x * (1 if c.x > 0 else -1)
            if nx < -0.3: return True
            # ikkunanauhoissa kehysten reunapinnat (ylös/alas/sivulle katsovat) kuoren pinnan sisäpuolella
            return nx < 0.5 and abs(c.x) < 1.49 and (1.78 < c.z < 2.85 or 3.5 < c.z < 4.5)
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if hole(f) or inward(f)], context='FACES')
    bm.to_mesh(me); bm.free()
    # harvennus
    n = len(me.polygons); r = min(1.0, S['tris'] * (5 if DET == 'high' else 0.6) / max(1, n))
    if r < 1:
        md = ob.modifiers.new('dec', 'DECIMATE'); md.ratio = r; md.use_collapse_triangulate = True; md.delimit = {'UV', 'SEAM'}   # UV-saumat säilyvät (ilman tätä tekstuuri levisi ikkunoiden alle)
        bpy.ops.object.modifier_apply(modifier='dec')
    ob.name = name + '_kori'
    for p in me.polygons: p.use_smooth = True
    # tekstuurit pienemmiksi
    base = set()
    for m in me.materials:
        if m and m.use_nodes:
            for nd in m.node_tree.nodes:
                if nd.type == 'BSDF_PRINCIPLED' and nd.inputs['Base Color'].is_linked:
                    q = nd.inputs['Base Color'].links[0].from_node
                    if q.type == 'TEX_IMAGE' and q.image: base.add(q.image.name)
    for im in bpy.data.images:
        N = TEX if im.name in base else TEXO
        if im.size[0] > N: im.scale(N, N)
    root = J.empty(name.capitalize() if name != 'edo' else 'Edo'); ob.parent = root
    # telit, puskimet, kytkimet, alustan laitteet
    J.bogie('Bogie_F', -S['bog'], S['r'], S['wb'], root, heavy=S['heavy'])
    J.bogie('Bogie_R', S['bog'], S['r'], S['wb'], root, heavy=S['heavy'])
    ye = S['L'] / 2
    bo = S.get('bufo', 0.12)
    for s in (-1, 1): J.buffers_coupler(root, s * (ye + bo), s, 1.06)
    if name != 'sr3':
        # vaunujen väli (omistaja 21.11.: "vaunujen välit liian pitkät"): kumipalje yläkerran tasolla ja helma, joka peittää Meshyn rosoisen alareunan
        for s in (-1, 1):
            if name == 'edo' and s == -1: continue   # ohjaamon pää
            J.box(f'{name}_palje{s}', 1.45, 0.16, 2.3, (0, s * (ye + 0.03), 2.35), J.BLACK(), root, 0.04)   # yhdyskäytävä välitasolla (1,25–3,25)
        # helma: alakerran lattia on 0,85 m (kuoren alareuna 1,25) -> sivu umpeen telien välissä
        for sx in (-1, 1): J.box(f'{name}_helma{sx}', 0.03, 16.4, 0.65, (sx * (S['W'] / 2 - 0.02), 0, 1.075), J.BLACK(), root)
        # päätyjen helma (Meshyn rosoinen vihreä alareuna) ovien ohi
        for (yc, w, zt, n) in DOORS[name]:
            sg = 1 if yc > 0 else -1; a0, a1 = abs(yc) - w / 2 - 0.02, abs(yc) + w / 2 + 0.02
            for sx in (-1, 1):
                for (u0, u1, z0, z1) in ((8.2, a0, 1.10, 1.40), (a1, 12.85, 1.10, 1.40), (a0, a1, 1.06, 1.24)):
                    if u1 > u0: J.box(f'{name}_helmap{sg}{sx}{u0:.1f}', 0.03, u1 - u0, z1 - z0, (sx * (S['W'] / 2 - 0.02), sg * (u0 + u1) / 2, (z0 + z1) / 2), J.BLACK(), root)
        for s in (-1, 1): J.box(f'{name}_frame{s}', S['W'] - 0.25, 4.05, 0.18, (0, s * 10.625, 1.11), J.BLACK(), root)   # päädyt: eteisen lattian alle
        # ovet: lehdet liukuvat kylkeä pitkin (nimi: Door_<L|R><n>_<p|m><siirto cm> Blenderin Y-suuntaan), juna.js avaa laiturin puolelta
        GR = J.mat('Ovi_vihrea', J.srgb('#5cb532'), 0.1, 0.4); WH = J.mat('Ovi_valk', J.srgb('#e7e8e4'), 0.1, 0.4)
        k = 0
        for (yc, w, zt, n) in DOORS[name]:
            h = zt - 1.25
            for sx in (-1, 1):
                LR = 'L' if sx < 0 else 'R'
                leaves = [(yc, w, 1 if yc > 0 else -1, w + 0.02)] if n == 1 else [(yc - w / 4, w / 2, -1, w / 2 + 0.02), (yc + w / 4, w / 2, 1, w / 2 + 0.02)]
                for (ly, lw, dirn, amt) in leaves:
                    k += 1
                    nm = f'Door_{LR}{k}_{"p" if dirn > 0 else "m"}{int(round(amt * 100))}'
                    d = J.box(nm, 0.045, lw - 0.02, h - 0.03, (sx * 1.545, ly, 1.25 + h / 2), GR if name == 'ed' else WH, root)
                    J.box(nm + '_ikkuna', 0.05, lw * 0.45, 0.75, (sx * 1.545, ly, 1.25 + h * 0.62), J.DARK(), d)
                    J.box(nm + '_reuna', 0.05, 0.03, h - 0.06, (sx * 1.545, ly + (lw / 2 - 0.03) * (1 if n == 1 else dirn), 1.25 + h / 2), J.BLACK(), d)
    else:
        J.box(name + '_frame', S['W'] - 0.25, S['L'] - 0.6, 0.18, (0, 0, S['zb'] + 0.02), J.BLACK(), root)
    if name == 'sr3':
        J.box('Sr3_tank', 2.2, 4.2, 0.6, (0, 0, S['zb'] - 0.38), J.BLACK(), root, 0.05)
        for s in (-1, 1): J.box(f'Sr3_plough{s}', 2.5, 0.35, 0.4, (0, s * (ye + bo - 0.35), 0.45), J.BLACK(), root, 0.03)
    else:
        for y in (-5.0, -1.8, 1.8, 5.0): J.box(f'{name}_box{y}', 2.3, 2.2, 0.3, (0, y, 0.6), J.BLACK(), root, 0.03)
    return root

os.makedirs(OUTD, exist_ok=True)
for name, S in SPEC.items():
    if ONLY and name not in ONLY: continue
    J.export(build(name, S), name)
