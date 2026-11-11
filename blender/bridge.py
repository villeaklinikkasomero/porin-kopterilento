"""Porinsilta (1926): steel truss road bridge on granite piers, with portal pylons over piers 1 and 2 and curved chords sweeping
down from them and lattice lamp masts carrying twin lanterns. Shapes from Wikimedia Commons photos; pier positions, length
and alignment from the aerial image and OpenStreetMap. Local frame: +Y along the bridge (south -> north), +X to the east, Z up;
origin = the south end of the deck centre line. Exports out/bl_porinsilta.glb (+ .json with the anchor and the deck profile)."""
import bpy, bmesh, math, json, os, sys
from mathutils import Vector, Matrix
OUT = '/home/claude/blender/out'; STILL = len(sys.argv) > 1 and sys.argv[1] == 'still'
bpy.ops.wm.read_factory_settings(use_empty=True); scene = bpy.context.scene

S = (207.45, 477.95); N = (245.85, 643.6); L = math.hypot(N[0] - S[0], N[1] - S[1])
HEAD = math.atan2(N[0] - S[0], N[1] - S[1])                       # compass bearing of the bridge axis
DECK = 2.6                                                           # deck surface above the water in the game
PIERS = (42.0, 100.0, 143.0); HALF = 7.4; TR = 7.1                   # deck half-width, truss line
def deck_z(t):
    if t < -14 or t > L + 14: return 0.0
    if t < 3: return DECK * max(0.0, (t + 14) / 17.0)
    if t > L - 3: return DECK * max(0.0, (L + 14 - t) / 17.0)
    return DECK

def lin(h):
    v = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]; return tuple((c / 12.92) if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in v)
COL = {'steel': '#d3d8d9', 'asph': '#55585b', 'walk': '#9a9b98', 'granite': '#8a8580', 'gran2': '#a39d94', 'lamp': '#2d3236', 'glass': '#f3ecd2', 'conc': '#b7b5ae'}
KEYS = list(COL)
bm = bmesh.new()
def quadstrip(pts_a, pts_b, mi, flip=False):
    va = [bm.verts.new(p) for p in pts_a]; vb = [bm.verts.new(p) for p in pts_b]
    for i in range(len(va) - 1):
        f = (va[i], va[i + 1], vb[i + 1], vb[i]); f = f[::-1] if flip else f; bm.faces.new(f).material_index = mi
def box(c, size, mi, rot=None):
    g = bmesh.ops.create_cube(bm, size=1.0); vs = g['verts']
    M_ = Matrix.Diagonal((size[0], size[1], size[2], 1.0))
    if rot is not None: M_ = rot @ M_
    bmesh.ops.transform(bm, matrix=Matrix.Translation(Vector(c)) @ M_, verts=vs)
    for f in {f for v in vs for f in v.link_faces}: f.material_index = mi
def beam(a, b, w, mi, h=None):
    a, b = Vector(a), Vector(b); d = b - a; Ln = d.length
    if Ln < 1e-4: return
    z = d.normalized(); x = z.orthogonal().normalized() if abs(z.z) < 0.9 else Vector((1, 0, 0)); x = (x - z * x.dot(z)).normalized(); y = z.cross(x)
    R = Matrix((x, y, z)).transposed().to_4x4()
    box((a + b) / 2, (w, h or w, Ln), mi, R)
def prism(poly, z0, z1, mi):
    n = len(poly); a = [bm.verts.new((p[0], p[1], z0)) for p in poly]; b = [bm.verts.new((p[0], p[1], z1)) for p in poly]
    bm.faces.new(a[::-1]).material_index = mi; bm.faces.new(b).material_index = mi
    for i in range(n): bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i])).material_index = mi
M = {k: i for i, k in enumerate(KEYS)}

# ---- deck: carriageway, raised walkways, slab edges; ramps down to the banks at both ends
ts = [t / 2 for t in range(-28, int((L + 14) * 2) + 1)]
for (x0, x1, top, m) in ((-4.6, 4.6, 0.0, 'asph'), (-HALF, -4.6, 0.18, 'walk'), (4.6, HALF, 0.18, 'walk')):
    quadstrip([(x0, t, deck_z(t) + top) for t in ts], [(x1, t, deck_z(t) + top) for t in ts], M[m], flip=True)
for x in (-HALF, HALF):
    quadstrip([(x, t, deck_z(t) + 0.18) for t in ts], [(x, t, max(deck_z(t) - 0.9, -0.2)) for t in ts], M['conc'], flip=(x > 0))
quadstrip([(-HALF, t, max(deck_z(t) - 0.9, -0.2)) for t in ts], [(HALF, t, max(deck_z(t) - 0.9, -0.2)) for t in ts], M['conc'])
# ---- granite piers with a cutwater on the upstream (east) side, and abutments
for tp in PIERS:
    poly = [(-HALF - 1.0, tp - 2.6), (HALF + 1.0, tp - 2.6), (HALF + 6.5, tp), (HALF + 1.0, tp + 2.6), (-HALF - 1.0, tp + 2.6), (-HALF - 3.0, tp)]
    prism(poly, -0.4, DECK - 2.4, M['granite']); prism([(p[0] * 1.02, tp + (p[1] - tp) * 1.08) for p in poly], DECK - 2.4, DECK - 2.15, M['gran2'])
for t0, t1 in ((-3.0, 3.0), (L - 3.0, L + 3.0)):
    prism([(-HALF - 1.5, t0), (HALF + 1.5, t0), (HALF + 1.5, t1), (-HALF - 1.5, t1)], -0.4, deck_z((t0 + t1) / 2) - 0.6, M['granite'])

prism([(HALF + 0.6, L - 2.5), (HALF + 4.4, L - 2.5), (HALF + 4.4, L + 1.5), (HALF + 0.6, L + 1.5)], -0.4, DECK + 4.2, M['gran2'])
prism([(HALF + 0.4, L - 2.7), (HALF + 4.6, L - 2.7), (HALF + 4.6, L + 1.7), (HALF + 0.4, L + 1.7)], DECK + 4.2, DECK + 4.6, M['lamp'])
# ---- side trusses: Warren with verticals, top chord at railing height. Over piers 1 and 2 the trusses rise into portal pylons,
# and concave chords sweep down from each pylon head about 19 m both ways to the top chord (1971 aerial photo, Museovirasto)
PORT = (PIERS[0], PIERS[1]); PH = 7.6; PR = 19.0
def RISE(t):
    r = 0.0
    for tp in PORT:
        d = abs(t - tp)
        if d < PR: r = max(r, PH * (1 - d / PR) ** 1.8)
    return r
W_ = 0.24
for sx in (-TR, TR):
    bot = lambda t: deck_z(t) - 2.1; top = lambda t: deck_z(t) + 1.15
    beam((sx, 3, bot(3)), (sx, L - 3, bot(L - 3)), 0.34, M['steel'], 0.55)
    beam((sx, 3, top(3)), (sx, L - 3, top(L - 3)), 0.3, M['steel'])
    k = 0; t = 3.0
    while t < L - 3 - 1e-6:
        t1 = min(t + 4.0, L - 3)
        beam((sx, t, bot(t)), (sx, t, top(t)), W_, M['steel'])
        if k % 2 == 0: beam((sx, t, bot(t)), (sx, t1, top(t1)), W_, M['steel'])
        else: beam((sx, t, top(t)), (sx, t1, bot(t1)), W_, M['steel'])
        t = t1; k += 1
    beam((sx, L - 3, bot(L - 3)), (sx, L - 3, top(L - 3)), W_, M['steel'])
    for tp in PORT:
        prev = None                                                                   # the curved chord over the pier
        for i in range(77):
            t = tp - PR + i * 0.5; p = (sx, t, top(t) + RISE(t))
            if prev: beam(prev, p, 0.4, M['steel'], 0.5)
            prev = p
        beam((sx, tp - 0.6, top(tp)), (sx, tp - 0.6, top(tp) + PH), 0.55, M['steel'], 0.9)   # the pylon: a pair of posts
        beam((sx, tp + 0.6, top(tp)), (sx, tp + 0.6, top(tp) + PH), 0.55, M['steel'], 0.9)
        for j in range(1, 4):
            for sg in (-1, 1):
                t = tp + sg * 4.5 * j
                beam((sx, t, top(t)), (sx, t, top(t) + RISE(t)), 0.2, M['steel'])          # hangers
                tn = tp + sg * 4.5 * (j - 1); beam((sx, t, top(t)), (sx, tn, top(tn) + RISE(tn)), 0.16, M['steel'])
# ---- portal frames across the carriageway: crossbeam between the pylon heads with curved knee brackets underneath
for tp in PORT:
    zt = DECK + 1.15 + PH
    for dt in (-0.6, 0.6):
        beam((-TR, tp + dt, zt - 0.3), (TR, tp + dt, zt - 0.3), 0.45, M['steel'], 0.7)
        prev = None
        for i in range(25):
            a = i / 24; x = -TR + 2 * TR * a; z = zt - 0.8 - 2.6 * (1 - math.sin(a * math.pi)) ** 2
            p = (x, tp + dt, z)
            if prev: beam(prev, p, 0.32, M['steel'], 0.45)
            prev = p
    for sx in (-1, 1): box((sx * TR, tp, zt + 0.2), (0.9, 2.0, 0.4), M['steel'])

# ---- lattice lamp masts with twin lanterns
def mast(x, t, base, hgt=9.5):
    s = 0.22
    for dx, dy in ((-s, -s), (s, -s), (s, s), (-s, s)): beam((x + dx, t + dy, base), (x + dx * 0.6, t + dy * 0.6, base + hgt), 0.07, M['steel'])
    for k in range(10):
        z0 = base + k * hgt / 10; z1 = z0 + hgt / 10
        beam((x - s, t - s, z0), (x + s, t + s, z1), 0.04, M['steel']); beam((x + s, t - s, z0), (x - s, t + s, z1), 0.04, M['steel'])
    for sgn in (-1, 1):
        a = (x, t, base + hgt - 0.3); b = (x, t + sgn * 1.05, base + hgt + 0.25); c = (x, t + sgn * 1.25, base + hgt - 0.25)
        beam(a, b, 0.08, M['steel']); beam(b, c, 0.08, M['steel'])
        box((x, t + sgn * 1.25, base + hgt - 0.55), (0.42, 0.42, 0.5), M['lamp']); box((x, t + sgn * 1.25, base + hgt - 0.88), (0.3, 0.3, 0.2), M['glass'])
    box((x, t, base + hgt + 0.45), (0.12, 0.12, 0.9), M['steel'])
for t in (3.5, 22.0, 71.0, 121.5, 143.0, L - 3.5):
    for sx in (-1, 1): mast(sx * (HALF + 0.3), t, deck_z(t) + 0.2)
for tp in PORT:
    for sx in (-1, 1): box((sx * TR, tp, DECK + 1.15 + PH + 0.9), (0.3, 0.3, 1.2), M['steel'])
me = bpy.data.meshes.new('porinsilta'); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
mats = []
for k in KEYS:
    m = bpy.data.materials.new(k); m.use_nodes = True; m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (*lin(COL[k]), 1); me.materials.append(m); mats.append(m)
ob = bpy.data.objects.new('porinsilta', me); scene.collection.objects.link(ob)
print('tris', sum(len(p.vertices) - 2 for p in me.polygons))

# ---- ambient occlusion baked into vertex colours, times the paint colour
bpy.ops.mesh.primitive_plane_add(size=600, location=(0, L / 2, -0.4)); ground = bpy.context.active_object
scene.render.engine = 'CYCLES'; scene.cycles.device = 'CPU'; scene.cycles.samples = 48
col = me.color_attributes.new('Col', 'FLOAT_COLOR', 'CORNER'); me.color_attributes.active_color = col
bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active = ob
scene.render.bake.target = 'VERTEX_COLORS'; bpy.ops.object.bake(type='AO')
for p in me.polygons:
    base = mats[p.material_index].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value
    for li in p.loop_indices:
        ao = 0.45 + 0.55 * col.data[li].color[0]; col.data[li].color = (base[0] * ao, base[1] * ao, base[2] * ao, 1)
if STILL:
    w = bpy.data.worlds.new('w'); scene.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.55, 0.7, 0.9, 1)
    gm = bpy.data.materials.new('water'); gm.use_nodes = True; gm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.03, 0.04, 0.05, 1); ground.data.materials.append(gm)
    sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); scene.collection.objects.link(sun); sun.data.energy = 3.5; sun.rotation_euler = (math.radians(50), 0, math.radians(-60))
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); scene.collection.objects.link(cam); scene.camera = cam; cam.data.lens = 32
    pos = Vector((70, -25, 14)); tgt = Vector((0, 50, 4)); cam.location = pos; cam.rotation_euler = (tgt - pos).to_track_quat('-Z', 'Y').to_euler()
    scene.render.resolution_x, scene.render.resolution_y = 1100, 620; scene.cycles.samples = 32; scene.cycles.use_denoising = True; scene.view_settings.view_transform = 'Standard'
    scene.render.image_settings.file_format = 'JPEG'; scene.render.filepath = OUT + '/still_porinsilta.jpg'; bpy.ops.render.render(write_still=True)
bpy.data.objects.remove(ground)
# rotate the local frame (+Y along the bridge) onto the map so that the game can place it with a plain translation
ob.rotation_euler = (0, 0, -HEAD); bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active = ob
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
me.materials.clear(); me.materials.append(bpy.data.materials.new('vc'))
for p in me.polygons: p.material_index = 0
bpy.ops.export_scene.gltf(filepath=OUT + '/bl_porinsilta.glb', use_selection=True, export_format='GLB', export_yup=True, export_apply=False, export_vertex_color='ACTIVE', export_all_vertex_colors=False, export_materials='NONE')
json.dump({'x': S[0], 'y': S[1], 'roof': True, 'len': L, 'head': HEAD, 'deck': DECK, 'half': HALF}, open(OUT + '/bl_porinsilta.json', 'w'))
print('exported', os.path.getsize(OUT + '/bl_porinsilta.glb'))
