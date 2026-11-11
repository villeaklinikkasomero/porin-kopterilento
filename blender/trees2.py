"""Leaf-card trees: tree0 broadleaf (linden / maple), tree1 birch, tree2 spruce.
Crowns are clusters of alpha-cut leaf cards (texture drawn here with PIL), trunk and main limbs are real geometry.
Leaf-card normals are bent outwards from the crown centre so the hemisphere light shades the crown as one volume;
vertex colours carry the self-shadowing (darker inside and low in the crown). Exports out/trees.glb (one atlas material)."""
import bpy, bmesh, math, os, random, sys
from mathutils import Vector
from PIL import Image, ImageDraw, ImageFilter
OUT = '/home/claude/blender/out'; os.makedirs(OUT, exist_ok=True)
STILL = len(sys.argv) > 1
R = random.Random(7)

# ---------------------------------------------------------------- texture atlas 2048 x 512: linden | birch | spruce | bark (top: dark bark, bottom: birch bark)
W = 512
def leaves(cell, kind):
    im = Image.new('RGBA', (W, W), (0, 0, 0, 0)); d = ImageDraw.Draw(im); rr = random.Random(cell * 11 + 3)
    if kind == 'spruce':
        for b in range(9):                                     # needle sprays hanging from a twig
            y0 = 40 + b * 50; x0 = 30 + rr.random() * 40; L = W - 80 - rr.random() * 80
            d.line([(x0, y0), (x0 + L, y0 + rr.uniform(-10, 18))], fill=(58, 46, 34, 255), width=4)
            for k in range(int(L / 4)):
                x = x0 + k * 4; y = y0 + (k * 4) / L * 8
                for s in (-1, 1):
                    g = rr.randint(70, 110); col = (int(g * 0.45), g, int(g * 0.55), 255)
                    d.line([(x, y), (x + rr.uniform(4, 10), y + s * rr.uniform(14, 26))], fill=col, width=3)
        return im
    n, size, base = (260, 34, (98, 140, 60)) if kind == 'linden' else (330, 24, (128, 160, 70))
    for k in range(n):
        a = rr.random() * 2 * math.pi; r = (rr.random() ** 0.6) * (W * 0.46); cx = W / 2 + r * math.cos(a); cy = W / 2 + r * math.sin(a)
        s = size * rr.uniform(0.7, 1.15); ang = rr.random() * math.pi
        t = rr.uniform(0.75, 1.2); col = tuple(min(255, int(c * t)) for c in base) + (255,)
        leaf = Image.new('RGBA', (int(s * 2.2), int(s * 2.2)), (0, 0, 0, 0)); ld = ImageDraw.Draw(leaf)
        ld.ellipse([s * 0.55, s * 0.15, s * 1.65, s * 2.05], fill=col)
        ld.line([(s * 1.1, s * 0.2), (s * 1.1, s * 2.0)], fill=tuple(int(c * 0.8) for c in col[:3]) + (255,), width=2)
        leaf = leaf.rotate(math.degrees(ang), resample=Image.BICUBIC, expand=False)
        im.alpha_composite(leaf, (int(cx - s * 1.1), int(cy - s * 1.1)))
    for k in range(7):                                         # twigs
        a = rr.random() * 2 * math.pi; d.line([(W / 2, W / 2), (W / 2 + 200 * math.cos(a), W / 2 + 200 * math.sin(a))], fill=(70, 55, 40, 255), width=3)
    return im

atlas = Image.new('RGBA', (4 * W, W), (0, 0, 0, 0))
for c, k in enumerate(('linden', 'birch', 'spruce')): atlas.alpha_composite(leaves(c, k), (c * W, 0))
bark = Image.new('RGBA', (W, W // 2), (88, 70, 55, 255)); bd = ImageDraw.Draw(bark)
for k in range(400):
    x = R.random() * W; bd.line([(x, 0), (x + R.uniform(-6, 6), W // 2)], fill=(R.randint(55, 80), R.randint(45, 62), R.randint(35, 48), 255), width=R.randint(1, 4))
birchb = Image.new('RGBA', (W, W // 2), (228, 226, 216, 255)); bb = ImageDraw.Draw(birchb)
for k in range(140):
    x = R.random() * W; y = R.random() * W / 2; bb.rectangle([x, y, x + R.uniform(8, 40), y + R.uniform(2, 6)], fill=(40, 38, 36, 255))
atlas.alpha_composite(bark.filter(ImageFilter.GaussianBlur(0.6)), (3 * W, 0)); atlas.alpha_composite(birchb, (3 * W, W // 2))
# bleed leaf colours under the transparent texels so mip-maps do not turn the cut edges black
rgb = Image.new('RGBA', atlas.size, (90, 120, 60, 255)); rgb.alpha_composite(atlas)
blur = atlas.filter(ImageFilter.GaussianBlur(10)); a = atlas.getchannel('A')
out = Image.composite(atlas, Image.merge('RGBA', (*blur.convert('RGB').split(), Image.new('L', atlas.size, 0))), a)
TEXP = OUT + '/trees_atlas.png'; out.save(TEXP)

# ---------------------------------------------------------------- geometry
bpy.ops.wm.read_factory_settings(use_empty=True); scene = bpy.context.scene
CELL = {'linden': 0, 'birch': 1, 'spruce': 2}
def uvc(cell, u, v): return ((cell + u) / 4, 1 - v)          # cell-local (u, v) -> atlas uv (glTF v downwards handled by Blender export)

class G:
    def __init__(s): s.v = []; s.f = []; s.uv = []; s.col = []; s.nrm = []
    def quad(s, ps, uvs, cols, nrms):
        b = len(s.v); s.v += ps; s.f.append((b, b + 1, b + 2, b + 3)); s.uv.append(uvs); s.col.append(cols); s.nrm += nrms

def tube(g, pts, r0, r1, cellv, n=7, tint=1.0):
    for k in range(len(pts) - 1):
        a, b = Vector(pts[k]), Vector(pts[k + 1]); ra = r0 + (r1 - r0) * k / (len(pts) - 1); rb = r0 + (r1 - r0) * (k + 1) / (len(pts) - 1)
        ax = (b - a).normalized(); ref = Vector((1, 0, 0)) if abs(ax.x) < 0.9 else Vector((0, 1, 0)); e1 = ax.cross(ref).normalized(); e2 = ax.cross(e1)
        for i in range(n):
            t0, t1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
            d0 = e1 * math.cos(t0) + e2 * math.sin(t0); d1 = e1 * math.cos(t1) + e2 * math.sin(t1)
            ps = [a + d0 * ra, a + d1 * ra, b + d1 * rb, b + d0 * rb]
            v0, v1 = cellv
            uvs = [uvc(3, i / n, v0), uvc(3, (i + 1) / n, v0), uvc(3, (i + 1) / n, v1), uvc(3, i / n, v1)]
            sh = [0.55 + 0.45 * max(0.0, d.dot(Vector((0.5, -0.6, 0.6)))) for d in (d0, d1, d1, d0)]
            g.quad(ps, uvs, [(tint * x, tint * x, tint * x) for x in sh], [d0, d1, d1, d0])

def cards(g, cell, centre, rx, rz, n, size, zmin=None, shape='ellipsoid', seed=0):
    rr = random.Random(seed); C = Vector(centre)
    for k in range(n):
        while True:
            p = Vector((rr.uniform(-1, 1), rr.uniform(-1, 1), rr.uniform(-1, 1)))
            if p.length <= 1: break
        if shape == 'cone':                                    # spruce: radius shrinks with height
            h = rr.random(); rad = (1 - h) * rx; ang = rr.random() * 2 * math.pi; rr_ = rad * (0.35 + 0.65 * rr.random() ** 0.5)
            pos = Vector((rr_ * math.cos(ang), rr_ * math.sin(ang), zmin + h * rz)); out = Vector((math.cos(ang), math.sin(ang), 0.35))
            depth = rr_ / max(rad, 0.3); hgt = h
        else:
            p = p * (rr.random() ** 0.25 / max(p.length, 1e-6)) * p.length ** 0.35
            pos = C + Vector((p.x * rx, p.y * rx, p.z * rz)); out = (pos - C); out = Vector((out.x / rx, out.y / rx, out.z / rz)).normalized()
            depth = min(1.0, Vector((p.x, p.y, p.z)).length); hgt = (p.z + 1) / 2
        # card plane: roughly facing outwards, randomly rolled and tilted
        nrm = (out + Vector((rr.uniform(-.7, .7), rr.uniform(-.7, .7), rr.uniform(-.5, .5)))).normalized()
        t1 = nrm.cross(Vector((0, 0, 1))); t1 = t1.normalized() if t1.length > 1e-3 else Vector((1, 0, 0)); t2 = nrm.cross(t1)
        roll = rr.random() * 2 * math.pi; a1 = t1 * math.cos(roll) + t2 * math.sin(roll); a2 = nrm.cross(a1)
        s = size * rr.uniform(0.75, 1.25)
        if shape == 'cone': a1 = Vector((math.cos(ang), math.sin(ang), -0.25)).normalized(); a2 = Vector((-math.sin(ang), math.cos(ang), 0)); s *= 1.1
        ps = [pos - a1 * s / 2 - a2 * s / 2, pos + a1 * s / 2 - a2 * s / 2, pos + a1 * s / 2 + a2 * s / 2, pos - a1 * s / 2 + a2 * s / 2]
        uvs = [uvc(cell, 0, 1), uvc(cell, 1, 1), uvc(cell, 1, 0), uvc(cell, 0, 0)]
        k_ = (0.42 + 0.58 * depth ** 0.8) * (0.72 + 0.38 * hgt) * rr.uniform(0.9, 1.08)     # self-shadowing: inner and low cards darker
        warm = rr.uniform(0.94, 1.06)
        col = (k_ * warm, k_, k_ * (2 - warm))
        bent = [((q - C) if shape != 'cone' else Vector(((q - C).x, (q - C).y, (q.z - zmin) * 0.3 + 1.0))).normalized() * 0.75 + nrm * 0.25 for q in ps]
        g.quad(ps, uvs, [col] * 4, [b.normalized() for b in bent])

def linden(g):
    tube(g, [(0, 0, 0), (0.08, 0, 2.4), (0, 0.06, 4.8)], 0.3, 0.17, (0.0, 0.5))
    for i, (a, l, z) in enumerate(((0.4, 2.6, 3.2), (2.5, 2.4, 3.6), (4.3, 2.7, 3.0), (1.4, 2.0, 4.4), (3.4, 2.2, 4.6))):
        tube(g, [(0, 0, z), (math.cos(a) * l * 0.5, math.sin(a) * l * 0.5, z + 1.3), (math.cos(a) * l, math.sin(a) * l, z + 2.6)], 0.12, 0.05, (0.0, 0.5), n=5)
    cards(g, 0, (0, 0, 7.0), 3.3, 3.0, 150, 2.1, seed=1)

def birch(g):
    tube(g, [(0, 0, 0), (0.1, 0.03, 3.6), (0.0, 0.1, 7.2), (0.06, 0.05, 10.0)], 0.2, 0.06, (0.5, 1.0))
    for i, (a, z) in enumerate(((0.3, 5.0), (2.4, 5.8), (4.4, 6.4), (1.3, 7.4))):
        tube(g, [(0, 0, z), (math.cos(a) * 1.0, math.sin(a) * 1.0, z + 1.2), (math.cos(a) * 1.7, math.sin(a) * 1.7, z + 2.6)], 0.07, 0.03, (0.5, 1.0), n=4)
    cards(g, 1, (0, 0, 8.4), 2.2, 3.3, 130, 1.7, seed=2)

def spruce(g):
    tube(g, [(0, 0, 0), (0, 0, 7.0), (0, 0, 14.0)], 0.24, 0.05, (0.0, 0.5))
    cards(g, 2, (0, 0, 0), 3.0, 13.0, 300, 2.4, zmin=1.0, shape='cone', seed=3)

img = bpy.data.images.load(TEXP)
m = bpy.data.materials.new('trees'); m.use_nodes = True; nt = m.node_tree; bs = nt.nodes['Principled BSDF']
tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = img; nt.links.new(tx.outputs['Color'], bs.inputs['Base Color']); nt.links.new(tx.outputs['Alpha'], bs.inputs['Alpha'])
m.blend_method = 'CLIP' if hasattr(m, 'blend_method') else None
T = []
for name, fn in (('tree0', linden), ('tree1', birch), ('tree2', spruce)):
    g = G(); fn(g)
    me = bpy.data.meshes.new(name); me.from_pydata([tuple(v) for v in g.v], [], g.f); me.update()
    uvl = me.uv_layers.new(name='UVMap'); ca = me.color_attributes.new('Col', 'FLOAT_COLOR', 'CORNER')
    for pi, p in enumerate(me.polygons):
        for j, li in enumerate(p.loop_indices): uvl.data[li].uv = g.uv[pi][j]; c = g.col[pi][j]; ca.data[li].color = (c[0], c[1], c[2], 1)
    me.normals_split_custom_set([tuple(g.nrm[me.loops[li].vertex_index]) for p in me.polygons for li in p.loop_indices])
    me.materials.append(m)
    o = bpy.data.objects.new(name, me); scene.collection.objects.link(o); T.append(o)
    print(name, 'tris', 2 * len(g.f))

if STILL:
    scene.render.engine = 'CYCLES'; scene.cycles.samples = 24
    w = bpy.data.worlds.new('w'); scene.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.55, 0.7, 0.9, 1)
    sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); scene.collection.objects.link(sun); sun.data.energy = 3.5; sun.rotation_euler = (math.radians(50), 0, math.radians(35))
    for i, o in enumerate(T): o.location = (i * 9 - 9, 0, 0)
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); scene.collection.objects.link(cam); scene.camera = cam; cam.data.lens = 40
    pos = Vector((6, -34, 9)); tgt = Vector((0, 0, 6)); cam.location = pos; cam.rotation_euler = (tgt - pos).to_track_quat('-Z', 'Y').to_euler()
    scene.render.resolution_x, scene.render.resolution_y = 900, 560; scene.view_settings.view_transform = 'Standard'
    scene.render.image_settings.file_format = 'JPEG'; scene.render.filepath = OUT + '/trees2_still.jpg'; bpy.ops.render.render(write_still=True)
    for o in T: o.location = (0, 0, 0)
bpy.ops.object.select_all(action='DESELECT')
for o in T: o.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT + '/trees.glb', use_selection=True, export_format='GLB', export_yup=True, export_apply=False,
                          export_vertex_color='ACTIVE', export_all_vertex_colors=False, export_image_format='AUTO', export_normals=True)
print('exported', os.path.getsize(OUT + '/trees.glb'))
