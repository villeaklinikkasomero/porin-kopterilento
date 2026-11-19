# -*- coding: utf-8 -*-
"""
PORIKOPTERI - liikennevalotolpat (proseduraalinen Blender-malli)
================================================================
Tyypit:  yhdistelma   = tolppa: ajoneuvo-opastin + jalankulkuopastin + painonappi
         jalankulkija = lyhyt tolppa: jalankulkuopastin + painonappi
         uloke        = ulokepylvas: taustalevyllinen opastin kaistan ylla + tolpan opastimet
         kaikki       = esittelykohtaus kaikista (renderointia ja .blend-tiedostoa varten)

Ajo: blender --background --python porikopteri_liikennevalot.py -- --type yhdistelma

Mitat metreina. Origo on tolpan juuressa maan tasossa. GLB:ssa ajoneuvo-opastin nayttaa +Z-suuntaan
(three.js) eli kohti lahestyvaa autoa; ajorata (ja jalankulkuopastimen suunta, ulokkeen varsi) on -X-puolella.
Jokainen lamppu on oma solmunsa (Veh_Red, Veh_Yellow, Veh_Green, Over_*, Ped_Red, Ped_Green, Button_Light)
omalla materiaalillaan; solmun lisatiedoissa (extras) on onColor ja offColor.
"""
import bpy, bmesh, math, os, sys
from math import sin, cos, pi, radians
from mathutils import Vector, Matrix

POLE_COLOR   = (0.40, 0.42, 0.43)        # kuumasinkitty teras; tummanvihrea olisi esim. (0.02, 0.09, 0.05)
HOUSING      = (0.012, 0.012, 0.013)     # opastimen musta kotelo
BUTTON_COLOR = (0.85, 0.60, 0.02)        # painonappikotelo
EMIT         = 2.5                       # palavan lampun hehkun voimakkuus
ON  = dict(Red=(1.0, 0.04, 0.02), Yellow=(1.0, 0.50, 0.02), Green=(0.03, 1.0, 0.40), Wait=(1.0, 0.25, 0.02))
OFF = dict(Red=(0.10, 0.012, 0.010), Yellow=(0.11, 0.07, 0.01), Green=(0.01, 0.09, 0.05), Wait=(0.08, 0.03, 0.01))
DEFAULT_ON = {"Veh_Red", "Over_Red", "Ped_Green"}
Zv = Vector((0, 0, 1))
(M_POLE, M_HOUSING, M_WHITE, M_BUTTON, M_DARK) = range(5)

def parse_args():
    import argparse
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--type", default="yhdistelma", choices=["yhdistelma", "jalankulkija", "uloke", "kaikki"])
    p.add_argument("--out", default=None)
    p.add_argument("--render", action="store_true")
    p.add_argument("--samples", type=int, default=64)
    p.add_argument("--res", type=int, default=1280)
    return p.parse_args(argv)

def _set(bsdf, names, value):
    for n in names:
        if n in bsdf.inputs:
            bsdf.inputs[n].default_value = value
            return

def make_mat(name, color, metallic=0.0, rough=0.5, emission=None, strength=1.0):
    m = bpy.data.materials.new(name)
    if m.node_tree is None:
        m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs["Base Color"].default_value = (*color, 1.0)
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = rough
    if emission is not None:
        _set(b, ["Emission Color", "Emission"], (*emission, 1.0))
        _set(b, ["Emission Strength"], strength)
    m.diffuse_color = (*color, 1.0)
    return m

def frame(d):
    d = Vector(d).normalized()
    return (-d).cross(Zv).normalized(), d          # katsojan oikea, opastimen etusuunta

def tube_path(bm, pts, radii, segs, mat, cap0=True, cap1=True):
    pts = [Vector(p) for p in pts]
    n = len(pts)
    nrm = None
    rings = []
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        nrm = t.orthogonal().normalized() if nrm is None else (nrm - t * nrm.dot(t)).normalized()
        b = t.cross(nrm)
        r = radii[i] if isinstance(radii, (list, tuple)) else radii
        rings.append([bm.verts.new(p + (nrm * cos(2 * pi * k / segs) + b * sin(2 * pi * k / segs)) * r)
                      for k in range(segs)])
    for i in range(n - 1):
        for k in range(segs):
            k2 = (k + 1) % segs
            bm.faces.new((rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k])).material_index = mat
    if cap0:
        bm.faces.new(rings[0][::-1]).material_index = mat
    if cap1:
        bm.faces.new(rings[-1]).material_index = mat

def add_box(bm, size, center, r, d, mat, bevel=0.0):
    """Laatikko: size = (leveys, syvyys etusuuntaan, korkeus)."""
    tmp = bmesh.new()
    bmesh.ops.create_cube(tmp, size=1.0)
    bmesh.ops.scale(tmp, vec=Vector(size), verts=tmp.verts)
    if bevel > 0:
        bmesh.ops.bevel(tmp, geom=tmp.edges[:], offset=bevel, segments=2, profile=0.5, affect='EDGES')
    mtx = Matrix((r, d, Zv)).transposed().to_4x4()
    mtx.translation = Vector(center)
    bmesh.ops.transform(tmp, matrix=mtx, verts=tmp.verts)
    me = bpy.data.meshes.new("_tmp")
    tmp.to_mesh(me)
    tmp.free()
    n0 = len(bm.faces)
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    bm.faces.ensure_lookup_table()
    for f in bm.faces[n0:]:
        f.material_index = mat

class Pole:
    def __init__(self, name, col):
        self.name, self.col = name, col
        self.bm = bmesh.new()
        self.lamps = []

    # ---- lamput (omat solmut)
    def lamp(self, name, center, r, d, R, key, polys=None):
        bm = bmesh.new()
        L = lambda u, v, w: r * u + Zv * v + d * w
        if polys is None:                                   # kupera linssi
            segs, rings = 20, 3
            ctr = bm.verts.new(L(0, 0, R * 0.14))
            prev = None
            for j in range(1, rings + 1):
                rho = R * j / rings
                ring = [bm.verts.new(L(rho * cos(2 * pi * k / segs), rho * sin(2 * pi * k / segs),
                                       R * 0.14 * (1 - (rho / R) ** 2))) for k in range(segs)]
                for k in range(segs):
                    k2 = (k + 1) % segs
                    bm.faces.new((ctr, ring[k], ring[k2]) if prev is None else (prev[k], ring[k], ring[k2], prev[k2]))
                prev = ring
        else:                                               # jalankulkijan symboli
            for poly in polys:
                bm.faces.new([bm.verts.new(L(u, v, 0.006)) for u, v in poly])
        bm.normal_update()
        for f in bm.faces:
            if f.normal.dot(d) < 0:
                f.normal_flip()
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        on = name in DEFAULT_ON
        base = tuple(c * 0.5 for c in ON[key]) if on else OFF[key]
        me.materials.append(make_mat(name, base, rough=0.25, emission=ON[key] if on else None, strength=EMIT))
        me.polygons.foreach_set("use_smooth", [polys is None] * len(me.polygons))
        ob = bpy.data.objects.new(name, me)
        ob.location = center
        ob["onColor"] = list(ON[key])
        ob["offColor"] = list(OFF[key])
        self.col.objects.link(ob)
        self.lamps.append(ob)

    def visor(self, c, r, d, Rv, length):
        prev = None
        for n in range(15):
            a = radians(-25 + 230 * n / 14)
            rim = r * cos(a) + Zv * sin(a)
            pair = (self.bm.verts.new(c + rim * Rv),
                    self.bm.verts.new(c + rim * Rv * 1.04 + d * length * (0.30 + 0.70 * max(0.0, sin(a)))))
            if prev:
                self.bm.faces.new((prev[0], pair[0], pair[1], prev[1])).material_index = M_HOUSING
            prev = pair

    def head(self, prefix, center, facing, keys, R=0.10, ped=False, backplate=False):
        """Opastin: keys ylhaalta alas. center = kotelon keskipiste."""
        r, d = frame(facing)
        center = Vector(center)
        mod, depth = R * 2.7, R * 1.6
        n = len(keys)
        s = R / 0.10
        for i, key in enumerate(keys):
            c = center + Zv * ((n - 1) / 2 * mod - i * mod)
            add_box(self.bm, (mod * 0.97, depth, mod * 0.97), c, r, d, M_HOUSING, bevel=R * 0.16)
            fc = c + d * (depth / 2)
            self.visor(fc, r, d, R * 1.10, R * 1.8)
            tube_path(self.bm, [fc - d * 0.004, fc + d * 0.012], R * 1.10, 20, M_HOUSING, cap0=False, cap1=False)
            name = "%s_%s" % (prefix, key)
            if not ped:
                self.lamp(name, fc + d * 0.003, r, d, R, key)
            else:
                tube_path(self.bm, [fc - d * 0.002, fc + d * 0.002], R, 20, M_HOUSING)      # musta tausta
                circ = lambda cu, cv, rad: [(cu + rad * cos(2 * pi * k / 12), cv + rad * sin(2 * pi * k / 12)) for k in range(12)]
                def seg(p0, p1, w):
                    p0, p1 = Vector(p0), Vector(p1)
                    t = (p1 - p0).normalized()
                    q = Vector((-t.y, t.x)) * (w / 2)
                    return [tuple(p0 - q), tuple(p0 + q), tuple(p1 + q), tuple(p1 - q)]
                if key == "Red":                                # seisova hahmo
                    polys = [circ(0, .066, .020), seg((0, .042), (0, -.018), .052),
                             seg((-.037, .040), (-.037, -.022), .012), seg((.037, .040), (.037, -.022), .012),
                             seg((-.014, -.018), (-.014, -.088), .021), seg((.014, -.018), (.014, -.088), .021)]
                else:                                           # kaveleva hahmo
                    polys = [circ(.004, .066, .020), seg((0, .045), (.004, -.015), .040),
                             seg((.006, -.010), (.042, -.088), .020), seg((.002, -.010), (-.040, -.088), .020),
                             seg((.004, .040), (.042, .004), .012), seg((-.004, .040), (-.040, .006), .012)]
                polys = [[(u * s, v * s) for u, v in p] for p in polys]
                self.lamp(name, fc, r, d, R, key, polys)
        if backplate:                                           # musta taustalevy, valkoinen reunus
            w, h = mod + R * 3.0, n * mod + R * 3.0
            bc = center + d * (depth * 0.25)
            add_box(self.bm, (w, 0.012, h), bc, r, d, M_HOUSING, bevel=0.004)
            e = R * 0.35
            for su in (-1, 1):
                add_box(self.bm, (e, 0.006, h - 0.02), bc + r * (su * (w / 2 - e / 2 - 0.01)) + d * 0.008, r, d, M_WHITE)
                add_box(self.bm, (w - 0.02, 0.006, e), bc + Zv * (su * (h / 2 - e / 2 - 0.01)) + d * 0.008, r, d, M_WHITE)
        return mod, depth

    def clamp(self, z, pr):
        tube_path(self.bm, [(0, 0, z - 0.025), (0, 0, z + 0.025)], pr + 0.008, 20, M_POLE)

    def side_heads(self, pr, vehicle=True, z_veh=3.05, z_ped=2.36):
        """Tolppaan kiinnitetyt opastimet ja painonappi. pr(z) = tolpan sade korkeudella z."""
        if vehicle:                                             # ajoneuvo-opastin tolpan edessa
            p = pr(z_veh)
            mod, depth = 0.27, 0.16
            hc = Vector((0, -(p + 0.07 + depth / 2), z_veh))
            self.head("Veh", hc, (0, -1, 0), ["Red", "Yellow", "Green"])
            for dz in (mod, -mod):
                add_box(self.bm, (0.05, 0.07 + 0.02, 0.05), (0, -(p + 0.035), z_veh + dz), Vector((1, 0, 0)), Vector((0, -1, 0)), M_POLE)
                self.clamp(z_veh + dz, p)
        p = pr(z_ped)                                           # jalankulkuopastin ajoradan puolella
        mod, depth = 0.27, 0.16
        self.head("Ped", (-(p + 0.07 + depth / 2), 0, z_ped), (-1, 0, 0), ["Red", "Green"], ped=True)
        for dz in (mod / 2, -mod / 2):
            add_box(self.bm, (0.05, 0.07 + 0.02, 0.05), (-(p + 0.035), 0, z_ped + dz), Vector((0, -1, 0)), Vector((-1, 0, 0)), M_POLE)
            self.clamp(z_ped + dz, p)
        p = pr(1.05)                                            # painonappi jalkakaytavan puolella
        r, d = frame((1, 0, 0))
        bc = Vector((p + 0.04, 0, 1.05))
        add_box(self.bm, (0.11, 0.08, 0.22), bc, r, d, M_BUTTON, bevel=0.012)
        tube_path(self.bm, [bc + d * 0.035 - Zv * 0.045, bc + d * 0.056 - Zv * 0.045], 0.024, 16, M_HOUSING)
        add_box(self.bm, (0.07, 0.004, 0.05), bc + d * 0.041 + Zv * 0.055, r, d, M_HOUSING)
        self.lamp("Button_Light", bc + d * 0.044 + Zv * 0.055, r, d, 0.014, "Wait")
        self.clamp(0.98, p)
        self.clamp(1.12, p)

    def finish(self, location=(0, 0, 0), rot_z=0.0):
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces[:])
        me = bpy.data.meshes.new("Structure")
        self.bm.to_mesh(me)
        self.bm.free()
        for m in MATS:
            me.materials.append(m)
        me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
        try:
            me.set_sharp_from_angle(angle=radians(40))
        except AttributeError:
            pass
        st = bpy.data.objects.new("Structure", me)
        self.col.objects.link(st)
        root = bpy.data.objects.new(self.name, None)
        root.empty_display_size = 0.3
        self.col.objects.link(root)
        for o in [st] + self.lamps:
            o.parent = root
        root.location = location
        root.rotation_euler = (0, 0, rot_z)
        self.objects = [root, st] + self.lamps
        tris = sum(len(p.vertices) - 2 for o in [st] + self.lamps for p in o.data.polygons)
        print("TOLPPA %s: %d kolmiota, %d lamppua" % (self.name, tris, len(self.lamps)))
        return self

def build_simple(name, col, vehicle):
    P = Pole(name, col)
    pr, H = 0.057, 3.62 if vehicle else 2.80
    tube_path(P.bm, [(0, 0, 0), (0, 0, 0.02), (0, 0, 0.02), (0, 0, 0.32), (0, 0, 0.34), (0, 0, H - 0.015), (0, 0, H)],
              [0.125, 0.125, 0.078, 0.078, pr, pr, pr * 0.55], 24, M_POLE)
    P.side_heads(lambda z: pr, vehicle=vehicle, z_ped=2.36 if vehicle else 2.42)
    return P

def build_mast(name, col):
    P = Pole(name, col)
    pr0, pr1, zb, za, bend = 0.095, 0.075, 5.6, 6.4, 0.8
    pr = lambda z: pr0 + (pr1 - pr0) * max(0.0, min(1.0, (z - 0.5) / (zb - 0.5)))
    pts = [(0, 0, 0), (0, 0, 0.03), (0, 0, 0.03), (0, 0, 0.48), (0, 0, 0.50), (0, 0, zb)]
    rad = [0.21, 0.21, 0.135, 0.135, pr0, pr1]
    for n in range(1, 7):
        a = radians(15 * n)
        pts.append((-bend + bend * cos(a), 0, zb + bend * sin(a)))
        rad.append(pr1 - 0.012 * n / 6)
    pts += [(-2.8, 0, za), (-4.6, 0, za)]
    rad += [0.056, 0.048]
    tube_path(P.bm, pts, rad, 24, M_POLE)
    R = 0.15                                                    # ylla oleva 300 mm opastin taustalevylla
    mod = R * 2.7
    hc = Vector((-3.9, 0, za - 0.05 - 0.10 - 1.5 * mod))
    P.head("Over", hc, (0, -1, 0), ["Red", "Yellow", "Green"], R=R, backplate=True)
    add_box(P.bm, (0.08, 0.08, 0.20), (-3.9, 0, za - 0.10), Vector((1, 0, 0)), Vector((0, -1, 0)), M_POLE)
    tube_path(P.bm, [(-3.96, 0, za), (-3.84, 0, za)], 0.062, 20, M_POLE)
    P.side_heads(pr)
    return P

# ----------------------------------------------------------------------------
def build_studio(col, samples):
    scn = bpy.context.scene
    bm = bmesh.new()
    X, D = Vector((1, 0, 0)), Vector((0, -1, 0))
    asphalt, paving, white = 0, 1, 2
    add_box(bm, (400, 400, 0.1), (0, 0, -0.17), X, D, asphalt)                    # ajorata
    add_box(bm, (200, 400, 0.12), (100 - 0.5, 0, -0.06), X, D, paving, bevel=0.02)   # jalkakaytavat
    add_box(bm, (200, 400, 0.12), (-100 - 7.5, 0, -0.06), X, D, paving, bevel=0.02)
    for i in range(7):                                                            # suojatie
        add_box(bm, (0.5, 3.0, 0.004), (-1.0 - i * 1.0, 2.2, -0.118), X, D, white)
    add_box(bm, (3.0, 0.3, 0.004), (-2.3, 0.2, -0.118), X, D, white)              # pysaytysviiva
    me = bpy.data.meshes.new("Street")
    bm.to_mesh(me); bm.free()
    for m in (make_mat("Asphalt", (0.045, 0.045, 0.05), rough=0.85), make_mat("Paving", (0.22, 0.22, 0.22), rough=0.9),
              make_mat("RoadPaint", (0.75, 0.75, 0.72), rough=0.7)):
        me.materials.append(m)
    col.objects.link(bpy.data.objects.new("Street", me))
    sun = bpy.data.lights.new("Sun", 'SUN')
    sun.energy = 2.8
    sun.angle = radians(4)
    so = bpy.data.objects.new("Sun", sun)
    so.rotation_euler = (radians(55), 0, radians(-140))
    col.objects.link(so)
    w = scn.world or bpy.data.worlds.new("World")
    scn.world = w
    if w.node_tree is None:
        w.use_nodes = True
    nt = w.node_tree
    bg = next((n for n in nt.nodes if n.type == 'BACKGROUND'), None)
    if bg is not None:
        tc = nt.nodes.new("ShaderNodeTexCoord")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        mth = nt.nodes.new("ShaderNodeMath")
        mth.operation = 'MULTIPLY_ADD'
        mth.inputs[1].default_value = 0.5
        mth.inputs[2].default_value = 0.5
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        cr = ramp.color_ramp
        cr.elements[0].position = 0.40
        cr.elements[0].color = (0.16, 0.15, 0.14, 1)
        cr.elements[1].position = 1.0
        cr.elements[1].color = (0.10, 0.28, 0.75, 1)
        for pos, c in ((0.495, (0.30, 0.29, 0.28, 1)), (0.51, (0.95, 0.97, 1.0, 1)), (0.62, (0.45, 0.65, 0.95, 1))):
            cr.elements.new(pos).color = c
        nt.links.new(tc.outputs["Generated"], sep.inputs[0])
        nt.links.new(sep.outputs[2], mth.inputs[0])
        nt.links.new(mth.outputs[0], ramp.inputs[0])
        nt.links.new(ramp.outputs[0], bg.inputs[0])
    cam = bpy.data.cameras.new("Camera")
    co = bpy.data.objects.new("Camera", cam)
    col.objects.link(co)
    scn.camera = co
    scn.render.engine = 'CYCLES'
    scn.cycles.samples = samples
    try:
        scn.cycles.use_denoising = True
    except Exception:
        pass
    return co

SHOTS = {   # nimi: (kameran paikka, kohde, polttovali, kuvasuhde)
    "yleiskuva": ((-5.2, -25.0, 2.6), (-2.6, -3.0, 3.7), 32, 16 / 9),
    "lahikuva":  ((-2.3, -3.4, 2.5), (-0.08, -0.05, 2.62), 55, 3 / 4),
}

MATS = []
def main():
    args = parse_args()
    cands = [args.out, os.path.dirname(bpy.data.filepath) if bpy.data.filepath else None]
    try:
        cands.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        pass
    cands.append(os.path.expanduser("~"))
    out_dir = next(c for c in cands if c and (c == args.out or os.path.isdir(c)))
    os.makedirs(out_dir, exist_ok=True)
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    for blk in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for d in list(blk):
            blk.remove(d)
    scn = bpy.context.scene
    col = bpy.data.collections.new("Liikennevalot")
    studio = bpy.data.collections.new("Studio")
    scn.collection.children.link(col)
    scn.collection.children.link(studio)
    MATS[:] = [make_mat("PoleSteel", POLE_COLOR, metallic=0.35, rough=0.55), make_mat("Housing", HOUSING, rough=0.45),
               make_mat("BackplateBorder", (0.85, 0.85, 0.85), rough=0.6), make_mat("ButtonBox", BUTTON_COLOR, rough=0.5),
               make_mat("Dark", (0.02, 0.02, 0.02), rough=0.8)]
    builders = {"yhdistelma": lambda: build_simple("TrafficLight", col, True),
                "jalankulkija": lambda: build_simple("TrafficLight", col, False),
                "uloke": lambda: build_mast("TrafficLight", col)}
    poles = []
    if args.type == "kaikki":
        poles.append(builders["uloke"]().finish((0, -7.0, 0)))
        poles.append(builders["yhdistelma"]().finish((0, 0, 0)))
        poles.append(builders["jalankulkija"]().finish((-7.45, 0.6, 0), pi))
    else:
        poles.append(builders[args.type]().finish())
    bpy.context.view_layer.update()
    cam = build_studio(studio, args.samples)
    name = "porikopteri_liikennevalo_" + args.type
    if args.type != "kaikki":
        try:
            bpy.ops.preferences.addon_enable(module="io_scene_gltf2")
        except Exception:
            pass
        for o in bpy.data.objects:
            o.select_set(o in poles[0].objects)
        path = os.path.join(out_dir, name + ".glb")
        bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True, export_apply=True,
                                  export_yup=True, export_extras=True)
        print("GLB:", path, "%.0f kt" % (os.path.getsize(path) / 1024))
    else:
        loc, tgt, lens, asp = SHOTS["yleiskuva"]
        cam.location = loc
        cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        cam.data.lens = lens
        path = os.path.join(out_dir, "porikopteri_liikennevalot.blend")
        bpy.ops.wm.save_as_mainfile(filepath=path)
        print("BLEND:", path)
    if args.render:
        for sname, (loc, tgt, lens, asp) in SHOTS.items():
            cam.location = loc
            cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
            cam.data.lens = lens
            scn.render.resolution_x = args.res if asp > 1 else int(args.res * 0.62)
            scn.render.resolution_y = int(scn.render.resolution_x / asp)
            path = os.path.join(out_dir, "porikopteri_liikennevalot_%s.png" % sname)
            scn.render.filepath = path
            bpy.ops.render.render(write_still=True)
            print("RENDER:", path)

if __name__ == "__main__":
    main()
