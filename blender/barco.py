"""Barco: an old steel cargo ship, now a restaurant, moored on Eteläranta west of Taavi-silta.
Shapes from photos (2020s): black hull with a white band, raised forecastle with a bowsprit, two white masts,
white deckhouse aft with the BARCO sign, white railings, string lights from bowsprit over the mast tops to the stern.
Size and heading from the OpenStreetMap outline (~34 x 6.4 m). Local frame: +Y stern -> bow, Z up, z = 0 at the waterline.
Exports pori/bl_barco.js (base64 glb, anchor x/y in game metres)."""
import bpy, bmesh, math, os, sys, base64, json
from mathutils import Vector, Matrix
OUT = '/home/claude/blender/out'; STILL = len(sys.argv) > 1 and sys.argv[1] == 'still'
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True); scene = bpy.context.scene

STERN = (-253.25, 507.65); BOW = (-219.3, 511.8)
L = math.hypot(BOW[0] - STERN[0], BOW[1] - STERN[1]); HEAD = math.atan2(BOW[0] - STERN[0], BOW[1] - STERN[1])
CX, CY = (STERN[0] + BOW[0]) / 2, (STERN[1] + BOW[1]) / 2
B = 6.4
def lin(h):
    v = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]; return tuple((c / 12.92) if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in v)
COL = {'black': '#232527', 'white': '#e4e2dc', 'bottom': '#3b3430', 'deck': '#6e6558', 'house': '#e9e7e1', 'win': '#2a3138',
       'mast': '#e8e6e0', 'rope': '#3a3a38', 'bulb': '#fff2c8', 'red': '#8e2a28', 'canvas': '#2e3236', 'sign': '#f2f1ec'}
KEYS = list(COL); M = {k: i for i, k in enumerate(KEYS)}
bm = bmesh.new()

def hb(t):           # half breadth along the hull (t: 0 stern .. 1 bow)
    h = B / 2
    if t > 0.62: h *= math.sqrt(max(0.0, 1 - ((t - 0.62) / 0.38) ** 2.2))
    if t < 0.10: h *= math.sqrt(max(0.0, 1 - ((0.10 - t) / 0.10) ** 2))
    return max(h, 0.02)
def zdeck(t):        # sheer line, rising to the bow; forecastle one step up
    z = 1.75 + 0.9 * max(0, t - 0.55) ** 2 * 4 + 0.25 * max(0, 0.2 - t) / 0.2
    return z + (0.85 * min(1, max(0, (t - 0.80) / 0.02)))
def zkeel(t):
    k = -2.1
    if t > 0.82: k += (t - 0.82) / 0.18 * 3.0              # raked stem
    if t < 0.06: k += (0.06 - t) / 0.06 * 1.8              # cruiser stern
    return k

TS = [i / 120 for i in range(121)]
ZL = [-2.1, -1.7, -1.3, -0.9, -0.5, -0.2, 0.1, 0.3, 0.6, 0.95, 1.25, 1.6, 1.9, 2.2, 2.5, 2.8, 3.1, 3.4, 3.7, 4.0, 4.3]
NS = len(ZL)
def section(t):
    zt = zdeck(t) + 0.95; zk = zkeel(t); h = hb(t); pts = []
    for z in [zt] + [min(zt, max(zk, z)) for z in reversed(ZL)]:     # bulwark top, then fixed levels down to the keel
        f = max(0.0, (z - zk) / (zt - zk)); w = h * (1 - (1 - f) ** 3.2) ** 0.5 if f < 1 else h
        pts.append((w, z))
    return pts
secs = [section(t) for t in TS]
def band(z, t):
    if z < 0.3: return 'bottom'
    if 0.95 < z < 1.6: return 'white'
    return 'black'
for side in (1, -1):
    for i in range(len(TS) - 1):
        for k in range(NS):
            a, b = secs[i][k], secs[i][k + 1]; c, d = secs[i + 1][k + 1], secs[i + 1][k]
            if abs(a[1] - b[1]) < 1e-4 and abs(c[1] - d[1]) < 1e-4: continue
            vs = [bm.verts.new((side * a[0], TS[i] * L - L / 2, a[1])), bm.verts.new((side * b[0], TS[i] * L - L / 2, b[1])),
                  bm.verts.new((side * c[0], TS[i + 1] * L - L / 2, c[1])), bm.verts.new((side * d[0], TS[i + 1] * L - L / 2, d[1]))]
            if side < 0: vs = vs[::-1]
            f = bm.faces.new(vs); f.material_index = M[band((a[1] + b[1] + c[1] + d[1]) / 4, TS[i])]
# white band line is sharp: split rows at the band edges by adding thin strips (already banded per face)
# inner bulwark and deck
for i in range(len(TS) - 1):
    t0, t1 = TS[i], TS[i + 1]; y0, y1 = t0 * L - L / 2, t1 * L - L / 2
    i0, i1 = max(0.02, hb(t0) - 0.14), max(0.02, hb(t1) - 0.14)
    for side in (1, -1):
        vs = [bm.verts.new((side * hb(t0), y0, zdeck(t0) + 0.95)), bm.verts.new((side * hb(t1), y1, zdeck(t1) + 0.95)),
              bm.verts.new((side * i1, y1, zdeck(t1) + 0.95)), bm.verts.new((side * i0, y0, zdeck(t0) + 0.95))]
        if side > 0: vs = vs[::-1]
        bm.faces.new(vs).material_index = M['black']
        vs = [bm.verts.new((side * i0, y0, zdeck(t0) + 0.95)), bm.verts.new((side * i1, y1, zdeck(t1) + 0.95)),
              bm.verts.new((side * i1, y1, zdeck(t1))), bm.verts.new((side * i0, y0, zdeck(t0)))]
        if side > 0: vs = vs[::-1]
        bm.faces.new(vs).material_index = M['white']
    vs = [bm.verts.new((-i0, y0, zdeck(t0))), bm.verts.new((i0, y0, zdeck(t0))), bm.verts.new((i1, y1, zdeck(t1))), bm.verts.new((-i1, y1, zdeck(t1)))]
    bm.faces.new(vs).material_index = M['deck']

def box(c, size, mi, rot=None):
    g = bmesh.ops.create_cube(bm, size=1.0); vs = g['verts']
    Mx = Matrix.Diagonal((size[0], size[1], size[2], 1.0))
    if rot is not None: Mx = rot @ Mx
    bmesh.ops.transform(bm, matrix=Matrix.Translation(Vector(c)) @ Mx, verts=vs)
    for f in {f for v in vs for f in v.link_faces}: f.material_index = mi
def beam(a, b, w, mi):
    a, b = Vector(a), Vector(b); d = b - a; Ln = d.length
    if Ln < 1e-4: return
    z = d.normalized(); x = z.orthogonal().normalized(); x = (x - z * x.dot(z)).normalized(); y = z.cross(x)
    box((a + b) / 2, (w, w, Ln), mi, Matrix((x, y, z)).transposed().to_4x4())
def cyl(a, b, r0, r1, mi, n=8):
    a, b = Vector(a), Vector(b); d = b - a; z = d.normalized(); x = z.orthogonal().normalized(); y = z.cross(x)
    ra = [bm.verts.new(a + (x * math.cos(2 * math.pi * k / n) + y * math.sin(2 * math.pi * k / n)) * r0) for k in range(n)]
    rb = [bm.verts.new(b + (x * math.cos(2 * math.pi * k / n) + y * math.sin(2 * math.pi * k / n)) * r1) for k in range(n)]
    for k in range(n): bm.faces.new((ra[k], ra[(k + 1) % n], rb[(k + 1) % n], rb[k])).material_index = mi
    bm.faces.new(rb).material_index = mi
Y = lambda t: t * L - L / 2

# aft deckhouse (white, dark windows) with the sign board and a railing on its roof
t0, t1 = 0.08, 0.30; zd = zdeck(0.2); hw = 2.3
box((0, (Y(t0) + Y(t1)) / 2, zd + 1.1), (2 * hw, Y(t1) - Y(t0), 2.2), M['house'])
for k in range(7):
    y = Y(t0) + 0.9 + k * (Y(t1) - Y(t0) - 1.8) / 6
    for s in (1, -1): box((s * (hw + 0.01), y, zd + 1.35), (0.04, 0.85, 0.75), M['win'])
for s in (1, -1): box((s * 0.9, Y(t1) + 0.01, zd + 1.3), (0.9, 0.04, 0.8), M['win'])
box((0, Y(t1) - 1.2, zd + 2.75), (3.4, 0.12, 0.9), M['sign']); box((0, Y(t1) - 1.25, zd + 2.75), (3.0, 0.02, 0.32), M['black'])
# midship awning frame (dark canvas) and a red flag on the stern
box((0, Y(0.5), zdeck(0.5) + 2.4), (4.8, 6.5, 0.08), M['canvas'])
for sx in (-2.3, 2.3):
    for ty in (0.43, 0.57): cyl((sx, Y(ty), zdeck(ty)), (sx, Y(ty), zdeck(ty) + 2.4), 0.05, 0.05, M['mast'], 6)
cyl((0, Y(0.015), zdeck(0.02) + 0.9), (0, Y(0.015), zdeck(0.02) + 4.2), 0.04, 0.03, M['mast'], 6)
box((0, Y(0.015) - 0.55, zdeck(0.02) + 3.8), (0.03, 1.0, 0.65), M['red'])
# forecastle front wall
box((0, Y(0.80), zdeck(0.79) + 0.42), (2 * hb(0.80) - 0.3, 0.12, 0.85), M['white'])
# masts with crosstrees, a derrick boom from the foremast, bowsprit
MAST = [(0.33, 17.5), (0.66, 16.0)]; tops = []
for tm, hm in MAST:
    base = (0, Y(tm), zdeck(tm)); top = (0, Y(tm), zdeck(tm) + hm); tops.append(Vector(top))
    cyl(base, top, 0.17, 0.07, M['mast'], 10)
    beam((-1.1, Y(tm), top[2] - 4.0), (1.1, Y(tm), top[2] - 4.0), 0.08, M['mast'])
    for s in (1, -1):
        for dy in (-0.9, 0.9):
            beam(top, (s * (hb(tm + dy / L) - 0.05), Y(tm) + dy, zdeck(tm) + 0.95), 0.025, M['rope'])
beam((0.3, Y(0.66) - 0.3, zdeck(0.66) + 1.2), (0.6, Y(0.47), zdeck(0.5) + 6.5), 0.12, M['mast'])
bs0 = Vector((0, Y(0.985), zdeck(0.98) + 0.9)); bs1 = bs0 + Vector((0, 6.0 * math.cos(0.42), 6.0 * math.sin(0.42)))
cyl(bs0, bs1, 0.14, 0.07, M['mast'], 8)
beam(bs1, tops[1], 0.025, M['rope']); beam(tops[0], tops[1], 0.025, M['rope'])
stern_pt = Vector((0, Y(0.01), zdeck(0.02) + 1.0)); beam(tops[0], stern_pt, 0.025, M['rope'])
beam(bs1, Vector((0, Y(0.96), zkeel(0.96) + 1.4)), 0.025, M['rope'])
# white railing along the bulwark top and around the deckhouse roof
def rail(pts, h, mi, step=1.5):
    for a, b in zip(pts, pts[1:]):
        for hh in (h, h * 0.5): beam(a + Vector((0, 0, hh)), b + Vector((0, 0, hh)), 0.035, mi)
    acc = 0.0
    for a, b in zip(pts, pts[1:]):
        d = (b - a).length; n = max(1, int(d / step))
        for k in range(n): p = a + (b - a) * (k / n); beam(p, p + Vector((0, 0, h)), 0.04, mi)
for s in (1, -1):
    pts = [Vector((s * (hb(t) - 0.08), Y(t), zdeck(t) + 0.95)) for t in [i / 40 for i in range(3, 39)]]
    rail(pts, 0.85, M['mast'])
rp = [Vector((x, y, zd + 2.2)) for x, y in ((-hw, Y(t0)), (hw, Y(t0)), (hw, Y(t1)), (-hw, Y(t1)), (-hw, Y(t0)))]
rail(rp, 0.9, M['mast'])
# string lights: catenaries bowsprit -> foremast -> mainmast -> stern, a bulb every ~1.2 m
def chain(a, b, sag):
    n = max(2, int((b - a).length / 1.2)); prev = None
    for k in range(n + 1):
        f = k / n; p = a + (b - a) * f - Vector((0, 0, sag * 4 * f * (1 - f)))
        if prev is not None: beam(prev, p, 0.02, M['rope'])
        box(p - Vector((0, 0, 0.12)), (0.16, 0.16, 0.16), M['bulb']); prev = p
for a, b, sg in ((bs1, tops[1] - Vector((0, 0, 0.3)), 2.2), (tops[1] - Vector((0, 0, 0.3)), tops[0] - Vector((0, 0, 0.3)), 2.6), (tops[0] - Vector((0, 0, 0.3)), stern_pt + Vector((0, 0, 1.0)), 2.6)):
    chain(a, b, sg)
# mooring lines to the quay (south side = local -X when heading east)
for t in (0.08, 0.9):
    beam(Vector((-hb(t), Y(t), zdeck(t) + 0.9)), Vector((-hb(t) - 4.5, Y(t) + (2.5 if t > 0.5 else -2.5), 1.6)), 0.05, M['rope'])

me = bpy.data.meshes.new('barco'); bm.to_mesh(me); bm.free()
mats = []
for k in KEYS:
    m = bpy.data.materials.new(k); m.use_nodes = True; m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (*lin(COL[k]), 1); me.materials.append(m); mats.append(m)
ob = bpy.data.objects.new('barco', me); scene.collection.objects.link(ob)
bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active = ob
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.remove_doubles(threshold=0.002); bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode='OBJECT')
for p in me.polygons: p.use_smooth = False
print('tris', sum(len(p.vertices) - 2 for p in me.polygons))
# ambient occlusion into vertex colours (water plane under it)
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0)); ground = bpy.context.active_object
scene.render.engine = 'CYCLES'; scene.cycles.device = 'CPU'; scene.cycles.samples = 48
col = me.color_attributes.new('Col', 'FLOAT_COLOR', 'CORNER'); me.color_attributes.active_color = col
bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active = ob
scene.render.bake.target = 'VERTEX_COLORS'; bpy.ops.object.bake(type='AO')
for p in me.polygons:
    base = mats[p.material_index].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value
    glow = KEYS[p.material_index] == 'bulb'
    for li in p.loop_indices:
        ao = 1.0 if glow else 0.45 + 0.55 * col.data[li].color[0]; col.data[li].color = (base[0] * ao, base[1] * ao, base[2] * ao, 1)
if STILL:
    w = bpy.data.worlds.new('w'); scene.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.55, 0.65, 0.8, 1)
    gm = bpy.data.materials.new('water'); gm.use_nodes = True; gm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.05, 0.06, 0.07, 1); ground.data.materials.append(gm)
    sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); scene.collection.objects.link(sun); sun.data.energy = 3.5; sun.rotation_euler = (math.radians(50), 0, math.radians(-60))
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); scene.collection.objects.link(cam); scene.camera = cam; cam.data.lens = 30
    pos = Vector((-30, 22, 9)); tgt = Vector((0, 2, 4)); cam.location = pos; cam.rotation_euler = (tgt - pos).to_track_quat('-Z', 'Y').to_euler()
    scene.render.resolution_x, scene.render.resolution_y = 1100, 620; scene.cycles.samples = 32; scene.cycles.use_denoising = True; scene.view_settings.view_transform = 'Standard'
    scene.render.image_settings.file_format = 'JPEG'; scene.render.filepath = OUT + '/still_barco.jpg'; bpy.ops.render.render(write_still=True)
bpy.data.objects.remove(ground)
ob.rotation_euler = (0, 0, -HEAD); bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active = ob
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
me.materials.clear(); me.materials.append(bpy.data.materials.new('vc'))
for p in me.polygons: p.material_index = 0
glb = OUT + '/bl_barco.glb'
bpy.ops.export_scene.gltf(filepath=glb, use_selection=True, export_format='GLB', export_yup=True, export_apply=False, export_vertex_color='ACTIVE', export_all_vertex_colors=False, export_materials='NONE')
open('/home/claude/pori/bl_barco.js', 'w').write('export const x = %.2f, y = %.2f;\nexport default "%s";\n' % (CX, CY, base64.b64encode(open(glb, 'rb').read()).decode()))
print('exported', os.path.getsize(glb), 'L', round(L, 1), 'head', round(math.degrees(HEAD), 1))
