import bpy,sys,math
from mathutils import Vector
a=sys.argv[sys.argv.index('--')+1:]; glb,out=a[0],a[1]; az=float(a[2]) if len(a)>2 else 200; el=float(a[3]) if len(a)>3 else 30; dist=float(a[4]) if len(a)>4 else 0
tx=float(a[5]) if len(a)>5 else None; tz=float(a[6]) if len(a)>6 else None
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
mn=Vector((1e9,)*3); mx=Vector((-1e9,)*3)
for o in bpy.context.scene.objects:
    if o.type=='MESH':
        for m in o.data.materials:
            nt=m.node_tree; bs=[n for n in nt.nodes if n.type=='BSDF_PRINCIPLED']
            if bs:
                b=bs[0]; l=b.inputs['Base Color'].links
                if l:
                    em=nt.nodes.new('ShaderNodeEmission'); nt.links.new(l[0].from_socket,em.inputs[0])
                    out_=[n for n in nt.nodes if n.type=='OUTPUT_MATERIAL'][0]; nt.links.new(em.outputs[0],out_.inputs[0])
        for c in o.bound_box:
            w=o.matrix_world@Vector(c)
            for i in range(3): mn[i]=min(mn[i],w[i]); mx[i]=max(mx[i],w[i])
c=(mn+mx)/2; c.z=mn.z+(mx.z-mn.z)*0.3
if tx is not None: c.x=tx; c.y=tz
r=dist or (mx-mn).length*0.75
az=math.radians(az); el=math.radians(el)
cam=bpy.data.cameras.new('c'); co=bpy.data.objects.new('c',cam); bpy.context.scene.collection.objects.link(co)
co.location=c+Vector((math.sin(az)*math.cos(el),-math.cos(az)*math.cos(el),math.sin(el)))*r
d=c-co.location; co.rotation_euler=d.to_track_quat('-Z','Y').to_euler(); cam.lens=35; cam.clip_end=5000
s=bpy.context.scene; s.camera=co; s.render.engine='CYCLES'; s.cycles.samples=6; s.cycles.use_denoising=False
s.render.resolution_x=1400; s.render.resolution_y=800; s.view_settings.view_transform='Standard'
w=bpy.data.worlds.new('w'); s.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(0.55,0.7,0.9,1)
s.render.filepath=out; s.render.image_settings.file_format='JPEG'; bpy.ops.render.render(write_still=True)
