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
    'sr3': dict(src='loco.glb', cut=1.12, roof=3.2, L=18.1, W=3.0, zb=1.08, zt=3.95, bog=4.75, r=0.625, wb=3.0, heavy=True, tris=60000),
    'ed':  dict(src='dd.glb', cut=1.22, roof=4.6, L=25.9, W=3.18, zb=1.1, zt=5.05, bog=9.5, r=0.46, wb=2.5, heavy=False, tris=50000),
    'edo': dict(src='horizon.glb', cut=1.18, roof=4.6, flip=True, L=25.9, W=3.18, zb=1.1, zt=5.05, bog=9.5, r=0.46, wb=2.5, heavy=False, tris=50000),
}
TEX = 2048 if DET == 'high' else 1024

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
    dead = [f for f in bm.faces if f.calc_center_median().z < S['cut']]
    bmesh.ops.delete(bm, geom=dead, context='FACES')
    xs = [v.co.x for v in bm.verts]; ys = [v.co.y for v in bm.verts]; zs = [v.co.z for v in bm.verts]
    x0, x1, y0, y1, z1 = min(xs), max(xs), min(ys), max(ys), max(zs)
    sx = S['L'] / (x1 - x0); sw = S['W'] / (y1 - y0); sz = (S['zt'] - S['zb']) / (S['roof'] - S['cut'])   # katon (ei virroittimen) korkeus oikeaksi
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    for v in bm.verts:
        x, y, z = (v.co.x - cx) * sx, (v.co.y - cy) * sw, (v.co.z - S['cut']) * sz + S['zb']
        v.co = Vector((-y, x, z)) if S.get('flip') else Vector((y, -x, z))   # keula -Y (glTF +Z); ohjausvaunun ohjaamo on Meshyssä -X-päässä
    bm.to_mesh(me); bm.free()
    # harvennus
    n = len(me.polygons); r = min(1.0, S['tris'] * (1 if DET == 'high' else 0.3) / max(1, n))
    if r < 1:
        md = ob.modifiers.new('dec', 'DECIMATE'); md.ratio = r; md.use_collapse_triangulate = True
        bpy.ops.object.modifier_apply(modifier='dec')
    ob.name = name + '_kori'
    for p in me.polygons: p.use_smooth = True
    # tekstuurit pienemmiksi
    for im in bpy.data.images:
        if im.size[0] > TEX: im.scale(TEX, TEX)
    root = J.empty(name.capitalize() if name != 'edo' else 'Edo'); ob.parent = root
    # telit, puskimet, kytkimet, alustan laitteet
    J.bogie('Bogie_F', -S['bog'], S['r'], S['wb'], root, heavy=S['heavy'])
    J.bogie('Bogie_R', S['bog'], S['r'], S['wb'], root, heavy=S['heavy'])
    ye = S['L'] / 2
    for s in (-1, 1): J.buffers_coupler(root, s * (ye + 0.12), s, 1.06)
    J.box(name + '_frame', S['W'] - 0.25, S['L'] - 0.6, 0.18, (0, 0, S['zb'] + 0.02), J.BLACK(), root)
    if name == 'sr3':
        J.box('Sr3_tank', 2.2, 4.2, 0.6, (0, 0, S['zb'] - 0.38), J.BLACK(), root, 0.05)
        for s in (-1, 1): J.box(f'Sr3_plough{s}', 2.5, 0.35, 0.4, (0, s * (ye + 0.02), 0.45), J.BLACK(), root, 0.03)
    else:
        for y in (-5.0, -1.8, 1.8, 5.0): J.box(f'{name}_box{y}', 2.3, 2.2, 0.32, (0, y, S['zb'] - 0.2), J.BLACK(), root, 0.03)
    return root

os.makedirs(OUTD, exist_ok=True)
for name, S in SPEC.items():
    J.export(build(name, S), name)
