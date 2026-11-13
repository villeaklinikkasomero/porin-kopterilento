import bpy, sys, math, re
from mathutils import Vector
glb, cx, cy, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
views = [tuple(map(float, v.split(','))) for v in sys.argv[5:]]   # x,y,z,heading,pitch
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
for m in bpy.data.materials:
    if not m.use_nodes: continue
    nt = m.node_tree; tex = [n for n in nt.nodes if n.type == 'TEX_IMAGE']
    if not tex: continue
    out_ = [n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'][0]; em = nt.nodes.new('ShaderNodeEmission')
    nt.links.new(tex[0].outputs[0], em.inputs[0]); nt.links.new(em.outputs[0], out_.inputs[0])
sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = 1; sc.render.resolution_x = 960; sc.render.resolution_y = 540
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[0].default_value = (0.6, 0.75, 1, 1)
cam = bpy.data.cameras.new('c'); cam.angle = math.radians(90); co = bpy.data.objects.new('c', cam); sc.collection.objects.link(co); sc.camera = co
for k, (x, y, z, h, p) in enumerate(views):
    co.location = (x - cx, y - cy, z)
    co.rotation_euler = (math.radians(90 + p), 0, -math.radians(h))
    sc.render.filepath = f'{out}_{k}.png'; bpy.ops.render.render(write_still=True)
