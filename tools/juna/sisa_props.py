# -*- coding: utf-8 -*-
"""IC2-sisätilan kalusteet omistajan Meshy-malleista (21.11.2026): istuinpari, seinään kiinnitetty taittopöytä ja hattuhylly.
Ajo: bl313/bin/python sisa_props.py [-- --src src --out sisa_props]
Lähteet (eivät repossa, kuten muutkin Meshy-lähteet): src/istuin_meshy.glb (Twin Transit Seats), src/poyta_meshy.glb
(Wall Mounted Folding Table), src/hylly_meshy.glb (Modern Glass Wall Shelf).
Tulos sisa_props/{istuin,poyta,hylly}.glb ja _m.glb (mobiili: 35 % kolmioista, 512 px) (repoon): harvennettu, käännetty ja skaalattu oikeisiin mittoihin. Meshyn UV-atlas ei kestä harvennusta,
joten harvennetulle mallille tehdään uusi UV ja väri + normaalikartta paistetaan (Cycles) alkuperäisestä, 1024 px.
juna_sisa.py tuo nämä ja monistaa ne paikoilleen.

Normalisoidut koordinaatit (Blender, metreinä):
  istuin: katse +Y, leveys X:n suuntaan keskitettynä, lattia z = 0, origo jalanjäljen keskellä. 0,88 × 0,60 × 1,21 m.
  poyta:  seinä x = 0, pöytä -X:n suuntaan (käytävää kohti), keskitetty Y:ssä, lattia z = 0. Kansi 0,75 m:ssä, 0,60 (X) × 0,50 (Y).
  hylly:  seinä x = 0, hylly -X:n suuntaan, keskitetty Y:ssä, alapinta z = 0. 1,75 (Y) × 0,40 (X) × 0,22 m.
"""
import bpy, os, sys, math
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
SRC = argv[argv.index('--src') + 1] if '--src' in argv else os.path.join(HERE, 'src')
OUT = argv[argv.index('--out') + 1] if '--out' in argv else os.path.join(HERE, 'sisa_props')

# nimi: lähde, kierto Z (rad, Meshy -> normalisoitu), kohdemitat (X, Y, Z) tai None = ennallaan, kiinnitys, kolmiot, metal, rough
PROPS = {
    # Meshyn istuin katsoo -Y:hen -> 180°. Leveys 1,11 -> 0,88 (käytävä 0,68 m kuten ennen), syvyys 0,64 -> 0,60, korkeus 1,15 -> 1,21
    'istuin': dict(src='istuin_meshy.glb', rot=math.pi, size=(0.88, 0.60, 1.21), anchor='center', tris=3000, metal=0.0, rough=0.85),
    # Meshyn pöydän seinä +Y:ssä -> -90° (seinä +X). Kansi z 1,2–1,4 -> 0,75 m; 1,78 × 1,67 -> 0,50 × 0,60 (mahtuu vastakkaisten istuinten väliin)
    'poyta': dict(src='poyta_meshy.glb', rot=-math.pi / 2, size=(0.60, 0.50, 0.75), anchor='wall', tris=1500, metal=0.2, rough=0.5),
    # Meshyn hyllyn seinä +Y:ssä -> -90°. 2,0 × 0,47 × 0,24 -> 1,75 × 0,40 × 0,22 (yksi hylly ikkunaa / pöytäosastoa kohti)
    'hylly': dict(src='hylly_meshy.glb', rot=-math.pi / 2, size=(0.40, 1.75, 0.22), anchor='wall', tris=1200, metal=0.5, rough=0.45),
}

def bbox(o):
    P = [o.matrix_world @ v.co for v in o.data.vertices]
    return Vector([min(p[i] for p in P) for i in range(3)]), Vector([max(p[i] for p in P) for i in range(3)])

os.makedirs(OUT, exist_ok=True)
LODS = (('', 1.0, 1024), ('_m', 0.35, 512))   # (pääte, kolmiokerroin, kuvan koko): työpöytä ja mobiili
ONLY = argv[argv.index('--only') + 1].split(',') if '--only' in argv else list(PROPS)
for (name, P), (suf, kf, TEX) in [(np_, l) for np_ in PROPS.items() for l in LODS]:
    if name not in ONLY: continue
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.join(SRC, P['src']))
    ms = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    bpy.ops.object.select_all(action='DESELECT')
    for o in ms: o.select_set(True)
    bpy.context.view_layer.objects.active = ms[0]
    if len(ms) > 1: bpy.ops.object.join()
    o = bpy.context.view_layer.objects.active
    for e in [e for e in bpy.context.scene.objects if e != o]: bpy.data.objects.remove(e)
    o.parent = None
    # muunnokset kärkipisteisiin: kierto, skaalaus kohdemittoihin, origo
    o.data.transform(o.matrix_world); o.matrix_world = Matrix.Identity(4)
    o.data.transform(Matrix.Rotation(P['rot'], 4, 'Z'))
    mn, mx = bbox(o); sz = mx - mn
    s = [P['size'][i] / sz[i] for i in range(3)]
    o.data.transform(Matrix.Diagonal((*s, 1)))
    mn, mx = bbox(o)
    if P['anchor'] == 'center': off = Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))
    else: off = Vector((-mx.x, -(mn.y + mx.y) / 2, -mn.z))
    o.data.transform(Matrix.Translation(off))
    # lähdemateriaali paistoa varten: metalli pois (muuten diffuusiväri paistuu mustaksi)
    hm = o.data.materials[0]; hnt = hm.node_tree; hb = next(n for n in hnt.nodes if n.type == 'BSDF_PRINCIPLED')
    for l in list(hb.inputs['Metallic'].links): hnt.links.remove(l)
    hb.inputs['Metallic'].default_value = 0.0
    # harvennettu kopio: Meshyn UV-atlas on pirstaleinen eikä kestä harvennusta -> uusi UV ja väri + normaalit paistetaan alkuperäisestä
    lo = o.copy(); lo.data = o.data.copy(); lo.name = name; bpy.context.collection.objects.link(lo)
    n0 = sum(len(p.vertices) - 2 for p in o.data.polygons)
    # Meshyn verkko on pilkottu UV-saumoista erillisiksi kärkipisteiksi -> yhdistetään, muuten harvennus repii pinnan
    import bmesh
    bm = bmesh.new(); bm.from_mesh(lo.data); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4); bm.to_mesh(lo.data); bm.free()
    d = lo.modifiers.new('dec', 'DECIMATE'); d.ratio = min(1.0, P['tris'] * kf / n0); d.use_collapse_triangulate = True
    bpy.ops.object.select_all(action='DESELECT'); lo.select_set(True); bpy.context.view_layer.objects.active = lo
    bpy.ops.object.modifier_apply(modifier='dec')
    for p in lo.data.polygons: p.use_smooth = True
    while lo.data.uv_layers: lo.data.uv_layers.remove(lo.data.uv_layers[0])
    lo.data.uv_layers.new(name='UVMap')
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(80), island_margin=0.003, area_weight=0.0)
    bpy.ops.uv.pack_islands(margin=0.004)
    bpy.ops.object.mode_set(mode='OBJECT')
    n1 = sum(len(p.vertices) - 2 for p in lo.data.polygons)
    # uusi materiaali (M_ = Meshy-kaluste; S_poyta on vanha laminaatti)
    m = bpy.data.materials.new('M_' + name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Metallic'].default_value = P['metal']; b.inputs['Roughness'].default_value = P['rough']
    imgs = {}
    for k in ('vari', 'normaali'):
        im = bpy.data.images.new(f'{name}_{k}', TEX, TEX, alpha=False)
        if k == 'normaali': im.colorspace_settings.name = 'Non-Color'; im.generated_color = (0.5, 0.5, 1, 1)
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = im; imgs[k] = t
    lo.data.materials.clear(); lo.data.materials.append(m)
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = 4; sc.cycles.device = 'CPU'
    bk = sc.render.bake; bk.use_selected_to_active = True; bk.cage_extrusion = 0.02; bk.max_ray_distance = 0.06; bk.margin = 6
    o.hide_render = False
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); lo.select_set(True); bpy.context.view_layer.objects.active = lo
    nt.nodes.active = imgs['vari']; bk.use_pass_direct = False; bk.use_pass_indirect = False; bk.use_pass_color = True
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'})
    nt.nodes.active = imgs['normaali']
    bpy.ops.object.bake(type='NORMAL', normal_space='TANGENT')
    nt.links.new(imgs['vari'].outputs['Color'], b.inputs['Base Color'])
    nm = nt.nodes.new('ShaderNodeNormalMap'); nt.links.new(imgs['normaali'].outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
    for t in imgs.values(): t.image.pack()
    bpy.data.objects.remove(o, do_unlink=True); o = lo
    mn, mx = bbox(o)
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True)
    path = os.path.join(OUT, name + suf + '.glb')
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True, export_yup=True, export_image_format='JPEG', export_jpeg_quality=85)
    print('PROP', name + suf, 'kolmiot', n0, '->', n1, 'mitat', tuple(round(x, 3) for x in mx - mn), 'min', tuple(round(x, 3) for x in mn), os.path.getsize(path) // 1000, 'kt')
