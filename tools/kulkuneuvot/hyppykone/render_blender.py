"""Cycles render of the GLB. usage:
bpyenv/bin/python render_blender.py model.glb out.png "ex,ey,ez" "tx,ty,tz" [focal_mm] [door_open_deg] [W H samples]
Coordinates are given in the glTF frame (Y up, nose +Z) and converted here."""
import sys, math
import bpy, addon_utils
from mathutils import Vector, Matrix

a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
glb, out = a[0], a[1]
g2b = lambda v: Vector((v[0], -v[2], v[1]))               # glTF -> Blender axes
eye = g2b([float(x) for x in a[2].split(",")]); tgt = g2b([float(x) for x in a[3].split(",")])
focal = float(a[4]) if len(a) > 4 else 50
door = float(a[5]) if len(a) > 5 else 0
W = int(a[6]) if len(a) > 6 else 1600; H = int(a[7]) if len(a) > 7 else 900
SPP = int(a[8]) if len(a) > 8 else 96
sun_az = float(a[9]) if len(a) > 9 else 215

addon_utils.enable("cycles", default_set=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=glb)

# open the jump door around its hinge (object origin)
for ob in bpy.data.objects:
    if ob.name == "door" and door:
        p = ob.matrix_world.translation.copy()
        ob.matrix_world = Matrix.Translation(p) @ Matrix.Rotation(math.radians(door), 4, "Y") @ Matrix.Translation(-p) @ ob.matrix_world

# ground: concrete/asphalt apron with procedural variation
bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, 0))
gp = bpy.context.object
gm = bpy.data.materials.new("apron"); gm.use_nodes = True
nt = gm.node_tree; bsdf = nt.nodes["Principled BSDF"]
tc = nt.nodes.new("ShaderNodeTexCoord")
noise = nt.nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 0.6; noise.inputs["Detail"].default_value = 8
noise2 = nt.nodes.new("ShaderNodeTexNoise"); noise2.inputs["Scale"].default_value = 60; noise2.inputs["Detail"].default_value = 4
ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].color = (0.10, 0.10, 0.095, 1); ramp.color_ramp.elements[1].color = (0.22, 0.215, 0.205, 1)
mix = nt.nodes.new("ShaderNodeMath"); mix.operation = "MULTIPLY_ADD"
mix.inputs[1].default_value = 0.35
nt.links.new(tc.outputs["Object"], noise.inputs["Vector"]); nt.links.new(tc.outputs["Object"], noise2.inputs["Vector"])
nt.links.new(noise.outputs["Fac"], mix.inputs[0]); nt.links.new(noise2.outputs["Fac"], mix.inputs[2])
nt.links.new(mix.outputs[0], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
bsdf.inputs["Roughness"].default_value = 0.85
bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.25
nt.links.new(noise2.outputs["Fac"], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
# painted yellow taxi line
line = nt.nodes.new("ShaderNodeTexWave")
gp.data.materials.append(gm)

# sky + sun
world = bpy.data.worlds.new("sky"); sc.world = world; world.use_nodes = True
wn = world.node_tree; bg = wn.nodes["Background"]
sky = wn.nodes.new("ShaderNodeTexSky")
try:
    sky.sky_type = "NISHITA"
except Exception:
    pass
if hasattr(sky, "sun_disc"): sky.sun_disc = False
for attr, val in (("sun_elevation", math.radians(38)), ("sun_rotation", math.radians(sun_az)), ("altitude", 100), ("air_density", 1.0), ("dust_density", 1.5)):
    if hasattr(sky, attr): setattr(sky, attr, val)
wn.links.new(sky.outputs["Color"], bg.inputs["Color"]); bg.inputs["Strength"].default_value = 0.12
sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 3.2; sun.angle = math.radians(1.2)
so = bpy.data.objects.new("sun", sun); sc.collection.objects.link(so)
so.rotation_euler = (math.radians(52), 0, math.radians(sun_az - 180))

# camera
cam = bpy.data.cameras.new("cam"); cam.lens = focal; cam.sensor_width = 36
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
co.location = eye
d = (tgt - eye); co.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
cam.dof.use_dof = True; cam.dof.focus_distance = d.length; cam.dof.aperture_fstop = 8

r = sc.render; r.engine = "CYCLES"; r.resolution_x = W; r.resolution_y = H; r.film_transparent = False
sc.cycles.device = "CPU"; sc.cycles.samples = SPP; sc.cycles.use_denoising = True
sc.cycles.max_bounces = 6; sc.cycles.transparent_max_bounces = 8
try: sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
except Exception: pass
sc.view_settings.exposure = -0.6
r.filepath = out; r.image_settings.file_format = "PNG"
bpy.ops.render.render(write_still=True)
print("rendered", out)
