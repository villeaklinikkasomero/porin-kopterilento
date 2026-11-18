"""Turntable videos for the vehicle choice on the start screen (18.11.2026).

usage: python3 tools/vehicles/turntable.py model.glb outdir name [frames=120] [samples=64] [res=960] [still]
  Cycles, the partly-cloudy sky HDRI from blender/tex, the vehicle on Pori asphalt (road_asph.jpg), a slow full turn of the vehicle in
  `frames` frames (seamless loop), rotors spinning with motion blur. Writes outdir/name_0001.png ...; encode with ffmpeg afterwards.
"""
import sys, os, math
import bpy
from mathutils import Vector

A = sys.argv[1:]
GLB, OUT, NAME = A[0], A[1], A[2]
FR = int(A[3]) if len(A) > 3 else 120
SMP = int(A[4]) if len(A) > 4 else 64
RES = int(A[5]) if len(A) > 5 else 960
STILL = len(A) > 6 and A[6] == 'still'
GAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=GLB)
objs = [o for o in sc.objects]
roots = [o for o in objs if o.parent is None]
pivot = bpy.data.objects.new('Pivot', None); sc.collection.objects.link(pivot)
for r in roots: r.parent = pivot
bpy.context.view_layer.update()
pts = [o.matrix_world @ Vector(c) for o in objs if o.type == 'MESH' for c in o.bound_box]
lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))); hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
ctr = (lo + hi) / 2; size = max(hi.x - lo.x, hi.y - lo.y)
for r in roots: r.location.x -= ctr.x; r.location.y -= ctr.y; r.location.z -= lo.z      # stand on the ground at the origin
H = hi.z - lo.z
print('model', NAME, 'size', round(size, 2), 'height', round(H, 2))

# rotors (helicopter): spin around their own centre
rotors = []
for o in objs:
    n = o.name.lower()
    if 'mainrotor' in n or 'tailrotor' in n:
        bpy.context.view_layer.update()
        rotors.append(o)

# ---------------------------------------------------------------- world: sky HDRI
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True; nt = w.node_tree
bg = nt.nodes['Background']; env = nt.nodes.new('ShaderNodeTexEnvironment')
env.image = bpy.data.images.load(os.path.join(GAME, 'blender/tex/kloofendal_48d_partly_cloudy_puresky_2k.hdr'))
mp = nt.nodes.new('ShaderNodeMapping'); tc = nt.nodes.new('ShaderNodeTexCoord'); mp.inputs['Rotation'].default_value[2] = math.radians(140)
nt.links.new(tc.outputs['Generated'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], env.inputs['Vector']); nt.links.new(env.outputs['Color'], bg.inputs['Color'])
bg.inputs['Strength'].default_value = 1.0

# ---------------------------------------------------------------- ground: Pori asphalt, fading out into a soft haze far away
bpy.ops.mesh.primitive_plane_add(size=400); g = bpy.context.active_object
m = bpy.data.materials.new('Asphalt'); m.use_nodes = True; t = m.node_tree; b = t.nodes['Principled BSDF']
im = t.nodes.new('ShaderNodeTexImage'); im.image = bpy.data.images.load(os.path.join(GAME, 'road_asph.jpg'))
cr = t.nodes.new('ShaderNodeTexImage'); cr.image = bpy.data.images.load(os.path.join(GAME, 'road_crack.png')); cr.image.colorspace_settings.name = 'Non-Color'
tc2 = t.nodes.new('ShaderNodeTexCoord'); m1 = t.nodes.new('ShaderNodeMapping'); m1.inputs['Scale'].default_value = (1 / 1.6, 1 / 1.6, 1)
m2 = t.nodes.new('ShaderNodeMapping'); m2.inputs['Scale'].default_value = (1 / 16, 1 / 16, 1); m2.inputs['Location'].default_value = (0.37, 0.21, 0)
t.links.new(tc2.outputs['Object'], m1.inputs['Vector']); t.links.new(m1.outputs['Vector'], im.inputs['Vector'])
t.links.new(tc2.outputs['Object'], m2.inputs['Vector']); t.links.new(m2.outputs['Vector'], cr.inputs['Vector'])
mul = t.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs['Factor'].default_value = 0.45
t.links.new(im.outputs['Color'], mul.inputs['A']); t.links.new(cr.outputs['Color'], mul.inputs['B'])
gam = t.nodes.new('ShaderNodeGamma'); gam.inputs['Gamma'].default_value = 1.45
t.links.new(mul.outputs['Result'], gam.inputs['Color']); t.links.new(gam.outputs['Color'], b.inputs['Base Color'])
b.inputs['Roughness'].default_value = 0.82
bump = t.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.35; bump.inputs['Distance'].default_value = 0.004
bw = t.nodes.new('ShaderNodeRGBToBW'); t.links.new(im.outputs['Color'], bw.inputs['Color']); t.links.new(bw.outputs['Val'], bump.inputs['Height']); t.links.new(bump.outputs['Normal'], b.inputs['Normal'])
g.data.materials.append(m)

# ---------------------------------------------------------------- camera
cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); sc.collection.objects.link(cam); sc.camera = cam
cam.data.lens = 50; cam.data.sensor_width = 36
dist = size * 1.25 + 3.2; el = math.radians(6.5)
cam.location = (0, -dist * math.cos(el), H * 0.35 + dist * math.sin(el))
look = Vector((0, 0, H * 0.40)); cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True; cam.data.dof.focus_distance = (look - cam.location).length; cam.data.dof.aperture_fstop = 4.0

# ---------------------------------------------------------------- animation: one full turn, rotors spinning
sc.frame_start, sc.frame_end = 1, FR
pivot.rotation_euler = (0, 0, math.radians(-35)); pivot.keyframe_insert('rotation_euler', index=2, frame=1)
pivot.rotation_euler = (0, 0, math.radians(-35 + 360)); pivot.keyframe_insert('rotation_euler', index=2, frame=FR + 1)
def linear(o):
    ad = o.animation_data
    if not ad or not ad.action: return
    fcs = []
    try: fcs = list(ad.action.fcurves)
    except AttributeError:
        for l in ad.action.layers:
            for s in l.strips:
                for cb in s.channelbags: fcs += list(cb.fcurves)
    for fc in fcs:
        for k in fc.keyframe_points: k.interpolation = 'LINEAR'
linear(pivot)
for o in rotors:
    # the game spins the main rotor about its up axis (glTF y = Blender z) and the tail rotor about x, both about the object origin
    main = 'main' in o.name.lower(); ax = 2 if main else 0
    turns = 13 if main else 31                                # ~40 deg a frame: blurred but readable blades, no strobing
    o.rotation_mode = 'XYZ'; r0 = o.rotation_euler[ax]
    o.keyframe_insert('rotation_euler', index=ax, frame=1); o.rotation_euler[ax] = r0 + turns * 2 * math.pi; o.keyframe_insert('rotation_euler', index=ax, frame=FR + 1)
    linear(o)

# ---------------------------------------------------------------- render
r = sc.render; r.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SMP; sc.cycles.use_denoising = True
try: sc.cycles.denoiser = 'OPENIMAGEDENOISE'
except Exception: pass
r.resolution_x = RES; r.resolution_y = int(RES * 9 / 16); r.resolution_percentage = 100
r.use_motion_blur = bool(rotors); r.motion_blur_shutter = 0.5
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast' if 'AgX - Medium High Contrast' in [x for x in ['AgX - Medium High Contrast']] else 'None'
r.image_settings.file_format = 'PNG'
os.makedirs(OUT, exist_ok=True)
if STILL:
    sc.frame_set(int(FR * 0.15)); r.filepath = os.path.join(OUT, NAME + '_still.png'); bpy.ops.render.render(write_still=True)
else:
    r.filepath = os.path.join(OUT, NAME + '_'); bpy.ops.render.render(animation=True)
print('done', NAME)
