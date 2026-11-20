# -*- coding: utf-8 -*-
"""
PORIKOPTERI - pelihahmo, realistisempi versio
=============================================
Noin 30-vuotias skandinaavinen mies: valkoinen t-paita, farkut, lenkkarit.

Vartalo, kasvot, kadet, luusto ja painotukset tulevat MakeHuman / MPFB2 -pohjamallista
(aineisto CC0-lisenssilla, https://github.com/makehumancommunity/mpfb2).
Vaatteet, kengat, hiukset, kulmakarvat ja animaatiot (Idle, Walk, Run, Sit) tekee tama skripti.

Ajo: blender --background --python porikopteri_hahmo.py -- --data <mpfb2>/src/mpfb/data --shots front:Idle:0
GLB:ssa hahmo katsoo +Z-suuntaan (three.js), Y on ylos, origo maassa jalkojen valissa, pituus 1,80 m.
"""
import bpy, bmesh, math, os, sys, json, gzip
from math import sin, cos, pi, radians, acos, sqrt
from mathutils import Vector, Matrix, Quaternion
from mathutils.bvhtree import BVHTree

HEIGHT      = 1.80
STUBBLE     = 0.18                      # sangen voimakkuus (0 = sileaksi ajettu)
HAIRLINE    = 0.062                     # hiusrajan korkeus silmien ylapuolella (m)
SKIN_COLOR  = (0.60, 0.35, 0.235)       # lammin, kevyesti ruskettunut
HAIR_COLOR  = (0.62, 0.42, 0.16)       # tummanvaalea
BROW_COLOR  = (0.25, 0.17, 0.09)
EYE_COLOR   = (0.10, 0.24, 0.42)        # sininen
SHIRT_COLOR = (0.88, 0.88, 0.88)
JEANS_COLOR = (0.035, 0.07, 0.18)
DENIM_BASE   = (0.040, 0.075, 0.19)    # farkkukankaan pohjavari ja vaalea lanka
DENIM_THREAD = (0.30, 0.38, 0.52)
DENIM_GAIN   = 1.6
SHOE_COLOR  = (0.82, 0.82, 0.80)
SOLE_COLOR  = (0.45, 0.45, 0.45)
FPS         = 30
TARGETS = [("macrodetails/universal-male-young-averagemuscle-averageweight", 1.0),
           ("macrodetails/caucasian-male-young", 1.0),
           # kasvojen muoto
           ("head/head-oval", 0.55), ("head/head-age-decr", 0.30), ("head/head-fat-incr", 0.12),
           ("cheek/l-cheek-volume-incr", 0.35), ("cheek/r-cheek-volume-incr", 0.35),
           ("cheek/l-cheek-bones-decr", 0.30), ("cheek/r-cheek-bones-decr", 0.30),
           ("chin/chin-bones-decr", 0.25), ("chin/chin-width-decr", 0.15),
           ("nose/nose-scale-vert-decr", 0.30), ("nose/nose-hump-decr", 0.50), ("nose/nose-point-up", 0.20),
           ("nose/nose-scale-depth-decr", 0.20), ("nose/nose-volume-decr", 0.15),
           ("mouth/mouth-lowerlip-volume-incr", 0.50), ("mouth/mouth-upperlip-volume-incr", 0.45),
           ("mouth/mouth-cupidsbow-incr", 0.30),
           ("eyes/l-eye-scale-incr", 0.25), ("eyes/r-eye-scale-incr", 0.25),
           ("eyes/l-eye-bag-decr", 0.50), ("eyes/r-eye-bag-decr", 0.50)]
(M_SKIN, M_SHIRT, M_JEANS, M_SHOE, M_SOLE, M_HAIR, M_EYE, M_IRIS, M_PUPIL, M_BROW) = range(10)
HAIR_SHELLS = 7                         # kiharakerrokset pohjakerroksen paalla
HAIR_VOLUME = 0.010                     # pohjakerroksen paksuus (m)
HAIR_STEP   = 0.0085                    # kerrosten vali (m): kerrokset x vali = kiharapilven paksuus
HAIR_LUMP   = 0.006                     # kerrosten kumpuilu (m)
HAIR_SAG    = 0.048                     # sivu- ja otsakiharoiden roikkuminen (m)
HAIR_ROOT   = (0.16, 0.10, 0.045)       # tummempi juurivari
M_HAIR1 = 10
HAIR_MATS = {M_HAIR} | set(range(M_HAIR1, M_HAIR1 + HAIR_SHELLS))

def parse_args():
    import argparse
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="/home/claude/mh/mpfb2/src/mpfb/data")
    p.add_argument("--out", default=None)
    p.add_argument("--name", default="porikopteri_hahmo")
    p.add_argument("--shots", default="")
    p.add_argument("--samples", type=int, default=64)
    p.add_argument("--res", type=int, default=1200)
    p.add_argument("--no-blend", action="store_true")
    p.add_argument("--no-glb", action="store_true")
    return p.parse_args(argv)

X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
def Q(axis, deg):
    return Quaternion(axis, radians(deg))
def clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))

# ----------------------------------------------------------------------------
def _set(bsdf, names, value):
    for n in names:
        if n in bsdf.inputs:
            bsdf.inputs[n].default_value = value
            return

def make_mat(name, color, rough=0.5, specular=0.5, sss=0.0, tex=None, nrm=None, nrm_strength=1.0, alpha=False):
    """Perusvari tulee verkon variattribuutista "Col" (kerrottuna tekstuurilla, jos sellainen on)."""
    m = bpy.data.materials.new(name)
    if m.node_tree is None:
        m.use_nodes = True
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs["Base Color"].default_value = (*color, 1.0)
    b.inputs["Roughness"].default_value = rough
    _set(b, ["Specular IOR Level", "Specular"], specular)
    attr = nt.nodes.new("ShaderNodeVertexColor")
    attr.layer_name = "Col"
    if tex is not None:
        ti = nt.nodes.new("ShaderNodeTexImage")
        ti.image = tex
        try:
            mix = nt.nodes.new("ShaderNodeMix")
            mix.data_type = 'RGBA'
            mix.blend_type = 'MULTIPLY'
            mix.inputs[0].default_value = 1.0
            nt.links.new(ti.outputs["Color"], mix.inputs[6])
            nt.links.new(attr.outputs["Color"], mix.inputs[7])
            out = mix.outputs[2]
        except Exception:
            mix = nt.nodes.new("ShaderNodeMixRGB")
            mix.blend_type = 'MULTIPLY'
            mix.inputs[0].default_value = 1.0
            nt.links.new(ti.outputs["Color"], mix.inputs[1])
            nt.links.new(attr.outputs["Color"], mix.inputs[2])
            out = mix.outputs[0]
        nt.links.new(out, b.inputs["Base Color"])
        if alpha:                                   # suortuvien valit lapinakyvia (glTF: alphaMode MASK)
            nt.links.new(ti.outputs["Alpha"], b.inputs["Alpha"])
            for attr_name, val in (("blend_method", "CLIP"), ("alpha_threshold", 0.5)):
                try:
                    setattr(m, attr_name, val)
                except Exception:
                    pass
    else:
        nt.links.new(attr.outputs["Color"], b.inputs["Base Color"])
    if nrm is not None:
        ni = nt.nodes.new("ShaderNodeTexImage")
        ni.image = nrm
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nm.inputs["Strength"].default_value = nrm_strength
        nt.links.new(ni.outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])
    if sss > 0:
        _set(b, ["Subsurface Weight", "Subsurface"], sss)
        try:
            b.inputs["Subsurface Radius"].default_value = (0.010, 0.004, 0.002)
            _set(b, ["Subsurface Scale"], 1.0)
        except Exception:
            pass
    m.diffuse_color = (*color, 1.0)
    m.roughness = rough
    return m

def make_textures(out_dir):
    """Saumattomasti toistuvat kangas- ja hiustekstuurit (vari + normaalikartta)."""
    import numpy as np
    n = 256
    def noise(seed, sx, sy):
        rng = np.random.default_rng(seed)
        f = np.fft.fft2(rng.standard_normal((n, n)))
        ky = np.fft.fftfreq(n)[:, None] * n
        kx = np.fft.fftfreq(n)[None, :] * n
        g = np.real(np.fft.ifft2(f * np.exp(-(kx / sx) ** 2 - (ky / sy) ** 2)))
        return (g - g.mean()) / g.std()
    def normal(h, strength):
        dx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * strength
        dy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * strength
        l = np.sqrt(dx * dx + dy * dy + 1)
        return np.stack([0.5 - 0.5 * dx / l, 0.5 - 0.5 * dy / l, 0.5 + 0.5 / l], -1)
    def save(name, rgb, color=True, alpha=None):
        img = bpy.data.images.new(name, n, n, alpha=alpha is not None)
        if not color:
            img.colorspace_settings.name = 'Non-Color'
        arr = np.clip(rgb, 0, 1)
        if color:
            arr = arr ** (1 / 2.2)
        px = np.concatenate([arr, np.ones((n, n, 1)) if alpha is None else alpha[..., None]], -1).astype(np.float32)
        img.pixels.foreach_set(px.ravel())
        img.filepath_raw = os.path.join(out_dir, name + ".png")
        img.file_format = 'PNG'
        img.save()
        img.pack()
        return img
    ii, jj = np.indices((n, n))
    T = {}
    # farkkukangas: toimikas-sidos, lankojen epatasaisuus, laikut
    slub, blot, fine = noise(1, 50, 2.5), noise(2, 4, 4), noise(3, 100, 100)
    twill = (((jj + ii) % 4) < 2).astype(float)
    base, thread = np.array(DENIM_BASE) * DENIM_GAIN, np.array(DENIM_THREAD) * DENIM_GAIN
    t = np.clip((0.10 + 0.14 * twill) * (1 + 0.3 * fine), 0, 1)[..., None]
    lum = (1 + 0.16 * slub + 0.10 * blot)[..., None]
    T["denim"] = save("tex_denim", base * lum * (1 - t) + thread * t)
    T["denim_n"] = save("tex_denim_normal", normal(0.55 * twill + 0.3 * slub + 0.15 * fine, 1.2), False)
    # puuvillatrikoo
    fine, soft = noise(4, 90, 90), noise(5, 5, 5)
    T["cotton"] = save("tex_cotton", np.array(SHIRT_COLOR) * (1 + 0.02 * fine + 0.010 * soft)[..., None])
    T["cotton_n"] = save("tex_cotton_normal", normal(0.6 * fine + 0.4 * np.sin(2 * np.pi * jj / 3.0), 0.5), False)
    # hiukset: pitkittaiset suortuvat (harmaasavy, vari tulee variattribuutista)
    st, st2 = noise(6, 70, 1.5), noise(7, 12, 1.0)
    g = np.clip(0.80 + 0.15 * st + 0.11 * st2, 0.40, 1.1)[..., None]
    T["hair"] = save("tex_hair", np.repeat(g, 3, -1))
    T["hair_n"] = save("tex_hair_normal", normal(0.7 * st + 0.3 * st2, 1.6), False)
    # kiharat: satunnaisia kaaria (kiehkuroita); ulommat kerrokset harvempia, valit lapinakyvia
    yy, xx = ii.astype(float), jj.astype(float)
    def curls(seed, count):
        rng = np.random.default_rng(seed)
        h = np.zeros((n, n))
        for _ in range(count):
            cx, cy = rng.uniform(0, n, 2)
            R0, th0 = rng.uniform(17, 36), rng.uniform(0, 2 * np.pi)
            span, w = rng.uniform(3.2, 5.6), rng.uniform(5.5, 9.0)
            dx = (xx - cx + n / 2) % n - n / 2
            dy = (yy - cy + n / 2) % n - n / 2
            th = (np.arctan2(dy, dx) - th0) % (2 * np.pi)
            R = R0 * (1 - 0.3 * th / span)
            prof = np.clip(1 - ((np.hypot(dx, dy) - R) / w) ** 2, 0, 1) * (th < span)
            prof = prof * np.clip(np.minimum(th, span - th) / 0.35, 0, 1)
            h = np.maximum(h, prof * rng.uniform(0.55, 1.0))
        return h
    hb = curls(20, 120)
    T["hair"] = save("tex_hair", np.repeat((0.42 + 0.58 * hb)[..., None], 3, -1))
    T["hair_n"] = save("tex_hair_normal", normal(hb * 3.0, 1.0), False)
    for k in range(1, HAIR_SHELLS + 1):
        hk = curls(20 + k, int(70 - 38 * k / HAIR_SHELLS))
        T["shell%d" % k] = save("tex_hair_shell%d" % k, np.repeat((0.28 + 0.72 * hk ** 0.8)[..., None], 3, -1),
                                alpha=(hk > 0.10).astype(float))
    return T

FLAT = None
def make_materials(T):
    global FLAT
    FLAT = {M_SHOE: SHOE_COLOR, M_SOLE: SOLE_COLOR, M_EYE: (0.80, 0.80, 0.79), M_IRIS: EYE_COLOR,
            M_PUPIL: (0.005, 0.005, 0.005), M_BROW: BROW_COLOR}
    return [make_mat("Skin", SKIN_COLOR, rough=0.52, specular=0.4, sss=0.12),
            make_mat("TShirt", SHIRT_COLOR, rough=0.85, specular=0.2, tex=T["cotton"], nrm=T["cotton_n"], nrm_strength=0.6),
            make_mat("Jeans", JEANS_COLOR, rough=0.85, specular=0.25, tex=T["denim"], nrm=T["denim_n"]),
            make_mat("Shoe", SHOE_COLOR, rough=0.6),
            make_mat("ShoeSole", SOLE_COLOR, rough=0.7),
            make_mat("Hair", HAIR_COLOR, rough=0.45, specular=0.45, tex=T["hair"], nrm=T["hair_n"]),
            make_mat("EyeWhite", (0.80, 0.80, 0.79), rough=0.2),
            make_mat("Iris", EYE_COLOR, rough=0.15),
            make_mat("Pupil", (0.005, 0.005, 0.005), rough=0.1),
            make_mat("Brow", BROW_COLOR, rough=0.6, specular=0.2)] + [
            make_mat("HairShell%d" % k, HAIR_COLOR, rough=0.5, specular=0.35, tex=T["shell%d" % k],
                     alpha=True) for k in range(1, HAIR_SHELLS + 1)]

# ----------------------------------------------------------------------------
# POHJAMALLIN LATAUS
# ----------------------------------------------------------------------------
class Base:
    def __init__(self, data):
        V, self.F, self.G = [], [], []
        cur = None
        for line in open(os.path.join(data, "3dobjs", "base.obj")):
            if line.startswith("v "):
                p = line.split()
                V.append([float(p[1]), float(p[2]), float(p[3])])
            elif line.startswith("g "):
                cur = line.split()[1]
            elif line.startswith("f "):
                self.F.append(tuple(int(t.split("/")[0]) - 1 for t in line.split()[1:]))
                self.G.append(cur)
        for name, w in TARGETS:
            path = os.path.join(data, "targets", name + ".target.gz")
            if not os.path.exists(path):
                print("Muotokohde puuttuu:", name)
                continue
            for line in gzip.open(path, "rt"):
                p = line.split()
                if len(p) == 4:
                    i = int(p[0])
                    V[i][0] += w * float(p[1]); V[i][1] += w * float(p[2]); V[i][2] += w * float(p[3])
        B = [Vector((x * 0.1, -z * 0.1, y * 0.1)) for x, y, z in V]       # MakeHuman (dm, Y ylos) -> Blender
        body = {v for f, g in zip(self.F, self.G) if g == "body" for v in f}
        self.zmin = min(B[v].z for v in body)
        self.scale = HEIGHT / (max(B[v].z for v in body) - self.zmin)
        self.P = [self.conv(b) for b in B]
        self.cubes = {}
        for f, g in zip(self.F, self.G):
            if g.startswith("joint-"):
                self.cubes.setdefault(g, set()).update(f)
        self.rig = json.load(open(os.path.join(data, "rigs", "standard", "rig.game_engine.json")))
        self.bones = list(self.rig.keys())
        wj = json.load(open(os.path.join(data, "rigs", "standard", "weights.game_engine.json")))["weights"]
        self.W = [dict() for _ in V]
        for bi, b in enumerate(self.bones):
            for vi, w in wj.get(b, []):
                self.W[vi][bi] = w
        self.dom = [self.bones[max(w, key=w.get)] if w else "" for w in self.W]
        self.J = {b: (self.joint(s["head"]), self.joint(s["tail"])) for b, s in self.rig.items()}

    def conv(self, b):
        return (Vector(b) - Vector((0, 0, self.zmin))) * self.scale

    def joint(self, spec):
        st = spec.get("strategy")
        if st == "CUBE" and spec.get("cube_name") in self.cubes:
            idx = self.cubes[spec["cube_name"]]
        elif st == "VERTEX" and "vertex_index" in spec:
            idx = [spec["vertex_index"]]
        elif st == "MEAN" and spec.get("vertex_indices"):
            idx = spec["vertex_indices"]
        else:
            return self.conv(spec["default_position"])
        return sum((self.P[i] for i in idx), Vector()) / len(idx)

    def faces(self, group):
        return [i for i, g in enumerate(self.G) if g == group]

    def centroid(self, f):
        vs = self.F[f]
        return sum((self.P[v] for v in vs), Vector()) / len(vs)

    def part(self, face_ids, mat):
        bm = bmesh.new()
        dl = bm.verts.layers.deform.verify()
        vm = {}
        for vi in sorted({v for f in face_ids for v in self.F[f]}):
            bv = bm.verts.new(self.P[vi])
            for bi, w in self.W[vi].items():
                bv[dl][bi] = w
            vm[vi] = bv
        for f in face_ids:
            try:
                bm.faces.new([vm[v] for v in self.F[f]]).material_index = mat
            except ValueError:
                pass
        bm.normal_update()
        return bm, dl

ARM_KEYS = ("upperarm", "lowerarm", "hand", "thumb", "index", "middle", "ring", "pinky")
def is_arm_bone(n):
    return any(k in n for k in ARM_KEYS)

def inflate_smooth(bm, offset_fn, iters):
    bm.normal_update()
    for v in bm.verts:
        v.co += v.normal * offset_fn(v)
    inner = [v for v in bm.verts if not v.is_boundary]
    for _ in range(iters):
        bmesh.ops.smooth_vert(bm, verts=inner, factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)

def cut(bm, co, no, geom=None):
    """Leikkaa tasolla ja poistaa normaalin puoleisen osan."""
    if geom is None:
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=Vector(co), plane_no=Vector(no).normalized(),
                           clear_outer=True, clear_inner=False)

def set_w(v, dl, w):
    for bi, wt in w.items():
        v[dl][bi] = wt

# ----------------------------------------------------------------------------
def build_character(base, col, mats):
    P, F, J, dom = base.P, base.F, base.J, base.dom
    BI = {b: i for i, b in enumerate(base.bones)}
    SH = {s: J["upperarm_" + sd][0] for sd, s in (("l", 1), ("r", -1))}
    EL = {s: J["lowerarm_" + sd][0] for sd, s in (("l", 1), ("r", -1))}
    DA = {s: (EL[s] - SH[s]).normalized() for s in (1, -1)}
    sleeve = 0.52 * (EL[1] - SH[1]).length
    th, kn, an = J["thigh_l"][0], J["calf_l"][0], J["foot_l"][0]
    nk, hd = J["neck_01"][0], J["head"][0]
    z_hem, z_waist, z_ank = th.z - 0.045, th.z + 0.07, an.z + 0.04
    col_co = Vector((0, nk.y, nk.z - 0.012))
    col_no = Vector((0, -0.36, 0.933))
    print("MAAMERKIT: olkapaa %s kyynarpaa %s lonkka %s polvi %s nilkka %s niska %s paa %s" % tuple(
        "(%.2f %.2f %.2f)" % tuple(v) for v in (SH[1], EL[1], th, kn, an, nk, hd)))

    def f_arm(f):
        return sum(1 for v in F[f] if is_arm_bone(dom[v])) * 2 > len(F[f])
    def arm_t(c):
        s = 1 if c.x > 0 else -1
        return (c - SH[s]).dot(DA[s])
    def col_d(c):
        return (c - col_co).dot(col_no)

    meshes = []
    def finish(bm):
        me = bpy.data.meshes.new("part")
        bm.normal_update()
        bm.to_mesh(me)
        bm.free()
        meshes.append(me)

    # --- iho: paa, kaula, kyynarvarret ja kadet (vaatteiden alle jaava osa poistetaan)
    body_keep = []
    for f in base.faces("body"):
        c = base.centroid(f)
        if (f_arm(f) and arm_t(c) > sleeve - 0.04) or col_d(c) > -0.04:
            body_keep.append(f)
    bm, dl = base.part(body_keep, M_SKIN)
    body_bvh = BVHTree.FromBMesh(bm)
    finish(bm)

    # --- silmat
    for g in ("helper-l-eye", "helper-r-eye"):
        ids = base.faces(g)
        ctr = sum((base.centroid(f) for f in ids), Vector()) / len(ids)
        bm, dl = base.part(ids, M_EYE)
        for face in bm.faces:
            d = (face.calc_center_median() - ctr).normalized()
            ang = math.degrees(acos(clamp(-d.y, -1, 1)))
            face.material_index = M_PUPIL if ang < 11 else (M_IRIS if ang < 27 else M_EYE)
        finish(bm)

    # --- hiukset
    eye_ids = base.faces("helper-l-eye") + base.faces("helper-r-eye")
    ez = sum((base.centroid(f).z for f in eye_ids)) / len(eye_ids)
    head_faces = [f for f in base.faces("body") if sum(1 for v in F[f] if dom[v] == "head") * 2 > len(F[f])]
    ys = [P[v].y for f in head_faces for v in F[f] if P[v].z > ez]
    yc = (min(ys) + max(ys)) / 2
    def lerp(a, b, t):
        return a + (b - a) * clamp(t)
    head_x = max(abs(P[v].x) for f in head_faces for v in F[f])
    scalp = []
    for f in head_faces:
        c = base.centroid(f)
        phi = math.degrees(math.atan2(abs(c.x), -(c.y - yc)))          # 0 = otsa, 180 = takaraivo
        if phi < 45:    thr = ez + HAIRLINE
        elif phi < 65:  thr = lerp(ez + HAIRLINE, ez + 0.035, (phi - 45) / 20)
        elif phi < 82:  thr = lerp(ez + 0.035, ez + 0.008, (phi - 65) / 12)     # pulisonki
        elif phi < 100: thr = ez + 0.032                                         # korvan ylapuoli
        else:           thr = lerp(ez + 0.032, ez - 0.070, (phi - 100) / 14)    # korvan takaa niskaan
        if abs(c.x) > head_x - 0.022 and c.z < ez + 0.030:                       # korvalehti
            continue
        if c.z > thr:
            scalp.append(f)
    def hair_layer(k):
        bm, dl = base.part(scalp, M_HAIR if k == 0 else M_HAIR1 + k - 1)
        for _ in range(8):                                   # tasoitetaan hiusrajan sahalaita
            new = {}
            for v in bm.verts:
                if v.is_boundary:
                    nb = [e.other_vert(v).co for e in v.link_edges if e.is_boundary]
                    if nb:
                        new[v] = v.co * 0.5 + sum(nb, Vector()) / len(nb) * 0.5
            for v, co in new.items():
                v.co = co
        bpts = [v.co.copy() for v in bm.verts if v.is_boundary]
        bm.normal_update()
        nz = {v: v.normal.z for v in bm.verts}
        def hair_off(v):
            d = min((v.co - p).length for p in bpts) if bpts else 0.1
            t = clamp(d / 0.035)
            t = t * t * (3 - 2 * t)
            up = 0.75 + 0.25 * clamp((v.co.z - (ez + 0.035)) / 0.07)
            return 0.002 + HAIR_VOLUME * t * up + k * HAIR_STEP * (0.35 + 0.65 * t) * up
        inflate_smooth(bm, hair_off, 2)
        if k:                                             # kumpuilu ja painovoima
            bm.normal_update()
            fr = k / HAIR_SHELLS
            for v in bm.verts:
                x, y, z = v.co
                lump = sin(165 * x + 1.7 * k) * sin(150 * y + 2.9 * k) * sin(175 * z + 4.1 * k)
                v.co += v.normal * (HAIR_LUMP * (0.3 + fr) * lump)
                v.co.z -= HAIR_SAG * fr ** 1.2 * (1 - clamp(nz[v]))
        finish(bm)
    for k in range(HAIR_SHELLS + 1):
        hair_layer(k)

    # --- t-paita (pohjamallin vartalonmyotaisesta apupinnasta, loysennettyna)
    tights = base.faces("helper-tights")
    ids = []
    for f in tights:
        c = base.centroid(f)
        if f_arm(f):
            if arm_t(c) < sleeve + 0.05:
                ids.append(f)
        elif c.z > z_hem - 0.06 and col_d(c) < 0.06:
            ids.append(f)
    bm, dl = base.part(ids, M_SHIRT)
    chest_z = SH[1].z - 0.10
    def shirt_off(v):
        return 0.012 + 0.014 * clamp((chest_z - v.co.z) / (chest_z - z_hem))
    inflate_smooth(bm, shirt_off, 5)
    arm_bi = {i for b, i in BI.items() if is_arm_bone(b)}
    for s in (1, -1):
        faces = []
        for face in bm.faces:
            c = face.calc_center_median()
            n_arm = 0
            for v in face.verts:
                it = v[dl].items()
                if it and max(it, key=lambda kv: kv[1])[0] in arm_bi:
                    n_arm += 1
            if c.x * s > 0 and n_arm * 2 > len(face.verts) and (c - SH[s]).dot(DA[s]) > sleeve * 0.45:
                faces.append(face)
        geom = set(faces)
        for face in faces:
            geom.update(face.verts); geom.update(face.edges)
        cut(bm, SH[s] + DA[s] * sleeve, DA[s], list(geom))
    cut(bm, (0, 0, z_hem), (0, 0, -1))
    cut(bm, col_co, col_no)
    finish(bm)

    # --- farkut
    ids = [f for f in tights if not f_arm(f) and z_ank - 0.05 < base.centroid(f).z < z_waist + 0.05]
    bm, dl = base.part(ids, M_JEANS)
    def jeans_off(v):
        return 0.008 + 0.009 * clamp((kn.z - v.co.z) / (kn.z - z_ank))
    inflate_smooth(bm, jeans_off, 4)
    cut(bm, (0, 0, z_waist), (0, 0, 1))
    cut(bm, (0, 0, z_ank), (0, 0, -1))
    finish(bm)

    # --- lenkkarit
    shoe = [(0.085, .020, .050), (0.070, .034, .095), (0.035, .042, .112), (-0.010, .045, .108),
            (-0.060, .048, .082), (-0.120, .052, .062), (-0.170, .048, .050), (-0.200, .034, .040),
            (-0.212, .016, .024)]
    bm = bmesh.new()
    dl = bm.verts.layers.deform.verify()
    for sd, s in (("l", 1), ("r", -1)):
        A, Bp = J["foot_" + sd][0], J["ball_" + sd][0]
        T = J["ball_" + sd][1]
        fd = Vector((T.x - A.x, T.y - A.y, 0)).normalized()
        side = Vector((-fd.y, fd.x, 0))
        u_ball = (Bp - A).dot(fd)
        loops = []
        for y, rx, h in shoe:
            sz = min(0.022, h * 0.45)
            prof = [(-.8 * rx, 0), (.8 * rx, 0), (rx, sz), (rx * .95, h * .55), (rx * .55, h),
                    (-rx * .55, h), (-rx * .95, h * .55), (-rx, sz)]
            u = -y
            wb = clamp((u - u_ball + 0.02) / 0.04)
            vs = []
            for px, pz in prof:
                v = bm.verts.new(Vector((A.x, A.y, 0)) + fd * u + side * px + Vector((0, 0, pz)))
                set_w(v, dl, {BI["foot_" + sd]: 1 - wb, BI["ball_" + sd]: wb} if 0 < wb < 1 else
                             {BI["ball_" + sd if wb >= 1 else "foot_" + sd]: 1.0})
                vs.append(v)
            loops.append(vs)
        for i in range(len(loops) - 1):
            for k in range(8):
                k2 = (k + 1) % 8
                bm.faces.new((loops[i][k], loops[i][k2], loops[i + 1][k2], loops[i + 1][k])).material_index = \
                    M_SOLE if k in (0, 1, 7) else M_SHOE
        bm.faces.new(loops[0][::-1]).material_index = M_SHOE
        bm.faces.new(loops[-1]).material_index = M_SHOE
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new("shoes")
    bm.to_mesh(me); bm.free()
    tmp = bpy.data.objects.new("shoes", me)
    col.objects.link(tmp)
    for b in base.bones:
        tmp.vertex_groups.new(name=b)
    sub = tmp.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = sub.render_levels = 2
    bpy.context.view_layer.update()
    meshes.append(bpy.data.meshes.new_from_object(tmp.evaluated_get(bpy.context.evaluated_depsgraph_get())))
    bpy.data.objects.remove(tmp)
    bpy.data.meshes.remove(me)

    # --- kulmakarvat: kapeat nauhat kasvojen pinnalla
    bm = bmesh.new()
    dl = bm.verts.layers.deform.verify()
    for sd, s in (("l", 1), ("r", -1)):
        ids = base.faces("helper-%s-eye" % sd)
        eye = sum((base.centroid(f) for f in ids), Vector()) / len(ids)
        rows = []
        N = 9
        for n in range(N):
            u = n / (N - 1)
            x = eye.x + s * (-0.019 + 0.044 * u)
            z = eye.z + 0.0185 + 0.006 * sin(pi * u ** 0.8) - 0.004 * u
            hit = body_bvh.ray_cast(Vector((x, -1.0, z)), Vector((0, 1, 0)))
            if hit[0] is None:
                continue
            rows.append((hit[0], hit[1], 0.0072 - 0.0038 * u))
        vs = []
        for n, (loc, nor, w) in enumerate(rows):
            a = rows[max(n - 1, 0)][0]; b = rows[min(n + 1, len(rows) - 1)][0]
            sdir = nor.cross(b - a).normalized()
            pr = (bm.verts.new(loc + nor * 0.0012 - sdir * w / 2), bm.verts.new(loc + nor * 0.0012 + sdir * w / 2))
            for v in pr:
                set_w(v, dl, {BI["head"]: 1.0})
            vs.append(pr)
        for (a1, a2), (b1, b2) in zip(vs[:-1], vs[1:]):
            bm.faces.new((a1, a2, b2, b1)).material_index = M_BROW
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    finish(bm)

    # --- kootaan yhdeksi verkoksi
    bm = bmesh.new()
    for me in meshes:
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
    bm.normal_update()
    dl = bm.verts.layers.deform.verify()
    cl = bm.verts.layers.float_color.new("Col")
    uvl = bm.loops.layers.uv.new("UVMap")
    hb = BI["head"]
    ut = [P[v] for f in base.faces("helper-upper-teeth") for v in F[f]]
    zm = min(p.z for p in ut) + 0.0015                    # huulten valinen linja
    teeth_y = min(p.y for p in ut)
    ex = abs(sum((base.centroid(f).x for f in base.faces("helper-l-eye"))) / len(base.faces("helper-l-eye")))
    ear_x0 = head_x - 0.017
    hair_vs = [v for v in bm.verts if v.link_faces and v.link_faces[0].material_index in HAIR_MATS]
    hedge = [v.co.copy() for v in hair_vs if v.is_boundary and v.link_faces[0].material_index == M_HAIR]
    hd = {}
    crown = Vector((0, yc + 0.02, max(v.co.z for v in hair_vs)))
    def mul(c, k, w):
        for i in range(3):
            c[i] *= 1 + (k[i] - 1) * w
    for v in bm.verts:
        if not v.link_faces:
            continue
        m = v.link_faces[0].material_index
        x, y, z = v.co
        no = v.normal
        n1 = sin(37 * x + 1.3) * sin(41 * y + 0.7) * sin(29 * z + 0.2)
        n2 = sin(113 * x + 2.1) * sin(97 * z + 0.4) * sin(89 * y)
        if m == M_SKIN:
            k = 1 + 0.05 * n1 + 0.025 * n2
            c = [SKIN_COLOR[0] * k * (1 + 0.02 * n1), SKIN_COLOR[1] * k, SKIN_COLOR[2] * k * (1 - 0.02 * n1)]
            if v[dl].get(hb, 0.0) > 0.3:
                ax = abs(x)
                wl = 0.0
                if y < teeth_y + 0.004:
                    wl = clamp(1 - ((x / 0.0265) ** 2 + ((z - (zm - 0.0015)) / 0.0098) ** 2)) ** 0.6
                zl = zm + 0.014 if ax < 0.028 else zm - 0.006 + 0.9 * (ax - 0.028)
                wb = clamp((zl - z) / 0.008) * clamp((z - (zm - 0.085)) / 0.03) * clamp((yc + 0.03 - y) / 0.03) * (1 - wl)
                we = max(clamp(1 - ((x - s * ex) ** 2 / 0.024 ** 2 + (z - ez) ** 2 / 0.014 ** 2)) for s in (1, -1))
                wc = max(clamp(1 - (((x - s * 0.046) / 0.03) ** 2 + ((z - (ez - 0.042)) / 0.026) ** 2))
                         for s in (1, -1)) * clamp((yc - y) / 0.03)
                mul(c, (0.74, 0.76, 0.82), STUBBLE * wb)             # sanki
                mul(c, (0.90, 0.86, 0.86), 0.5 * we)                 # silmakuopat
                mul(c, (1.05, 0.93, 0.92), 0.6 * wc)                 # posket
                mul(c, (1.06, 0.90, 0.88), 0.7 * clamp((ax - ear_x0) / 0.008))   # korvat
                mul(c, (0.98, 0.62, 0.60), 0.8 * wl)                 # huulet
        elif m in HAIR_MATS:
            d = min((v.co - p).length for p in hedge) if hedge else 0.1
            hd[v] = d
            k = 0 if m == M_HAIR else m - M_HAIR1 + 1
            f = clamp(d / 0.016)
            f = 1.0 if k else 0.50 + 0.50 * f * f * (3 - 2 * f)    # pehmea hiusraja
            g = (k / HAIR_SHELLS) ** 0.7                          # juuret tummat, latvat kullanvaaleat
            tone = 1 + 0.22 * sin(55 * x + 3 * k) * sin(47 * z + 2 * k) + 0.12 * n1      # vaaleammat ja tummemmat kiehkurat
            hc = [(HAIR_ROOT[i] * (1 - g) + HAIR_COLOR[i] * g) * tone for i in range(3)]
            c = [SKIN_COLOR[i] * 0.72 * (1 - f) + hc[i] * f for i in range(3)]
        elif m == M_JEANS:
            front = clamp(-no.y)
            k = 0.92 + 0.38 * front * clamp(1 - abs(z - (kn.z + 0.22)) / 0.26)      # reiden haalistuma
            k += 0.22 * front * clamp(1 - abs(z - kn.z) / 0.07)                      # polvet
            k += 0.18 * clamp(no.y) * clamp(1 - abs(z - (th.z - 0.03)) / 0.12)       # takamus
            k -= 0.12 * clamp(1 - (z - z_ank) / 0.05)                                # lahje
            k /= DENIM_GAIN
            c = [k * (1 + 0.04 * n1), k * (1 + 0.04 * n1), k * 0.97]
        elif m == M_SHIRT:
            k = 1 - 0.09 * clamp(abs(no.x)) * clamp((SH[1].z - 0.12 - z) / 0.25) + 0.008 * n1
            c = [k, k, k]
        else:
            c = list(FLAT.get(m, (1, 1, 1)))
        v[cl] = (clamp(c[0]), clamp(c[1]), clamp(c[2]), 1.0)
    for f in bm.faces:
        m = f.material_index
        if m in HAIR_MATS:
            k = 0 if m == M_HAIR else m - M_HAIR1 + 1
            n = f.normal
            ax, ay, az = abs(n.x), abs(n.y), abs(n.z)
            for l in f.loops:
                co = l.vert.co
                if az >= ax and az >= ay:
                    uv = (co.x, co.y)
                elif ax >= ay:
                    uv = (co.y, co.z)
                else:
                    uv = (co.x, co.z)
                l[uvl].uv = (uv[0] / 0.09 + 0.37 * k, uv[1] / 0.09 + 0.61 * k)
        else:
            S = 0.125 if m == M_JEANS else 0.10
            n = f.normal
            for l in f.loops:
                co = l.vert.co
                l[uvl].uv = ((co.y if abs(n.x) > abs(n.y) else co.x) / S, co.z / S)
    me = bpy.data.meshes.new("PlayerMesh")
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    try:
        me.set_sharp_from_angle(angle=radians(80))
    except AttributeError:
        pass
    ob = bpy.data.objects.new("PlayerMesh", me)
    col.objects.link(ob)
    for b in base.bones:
        ob.vertex_groups.new(name=b)
    try:
        me.color_attributes.active_color_index = 0
        me.color_attributes.render_color_index = 0
    except Exception:
        pass
    return ob

def build_armature(base, col):
    ad = bpy.data.armatures.new("PlayerRig")
    arm = bpy.data.objects.new("Player", ad)
    col.objects.link(arm)
    bpy.context.view_layer.update()
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    for name, spec in base.rig.items():
        eb = ad.edit_bones.new(name)
        eb.head, eb.tail = base.J[name]
        if (eb.tail - eb.head).length < 1e-4:
            eb.tail = eb.head + Vector((0, 0, 0.05))
        eb.roll = spec.get("roll", 0.0)
    for name, spec in base.rig.items():
        if spec.get("parent"):
            ad.edit_bones[name].parent = ad.edit_bones[spec["parent"]]
    bpy.ops.object.mode_set(mode='OBJECT')
    for pb in arm.pose.bones:
        pb.rotation_mode = 'QUATERNION'
    return arm

# ----------------------------------------------------------------------------
# ANIMAATIOT  (kierrot maailman akselien ympari lepoasennosta; eteenpain = negatiivinen X)
# ----------------------------------------------------------------------------
LEG_IN = 7.0        # pohjamalli seisoo haara-asennossa; jalkoja tuodaan sisaan (astetta) -> nilkat n. 18 cm toisistaan

LEG_REF = 0.8897    # pelaajahahmon jalan pituus lonkasta nilkkaan (m)

class Poser:
    def __init__(self, arm):
        b = arm.data.bones
        self.dU, self.dF = {}, {}
        self.H = {n: b[n].head_local.copy() for n in ("pelvis", "thigh_l", "calf_l", "foot_l", "ball_l", "thigh_r", "calf_r", "foot_r", "ball_r")}
        for sd, s in (("l", 1), ("r", -1)):
            self.dU[s] = (b["upperarm_" + sd].tail_local - b["upperarm_" + sd].head_local).normalized()
            self.dF[s] = (b["lowerarm_" + sd].tail_local - b["lowerarm_" + sd].head_local).normalized()
        a, bl = self.H["foot_l"], self.H["ball_l"]
        self.ank_h = a.z                                   # nilkan korkeus maasta, kun jalkapohja on maassa
        self.ball = (a.y - bl.y, a.z - bl.z)               # nilkka -> pakia: (eteen, alas)
        # askelluksen pituusmitat on annettu pelaajahahmon jalalle (LEG_REF); muun mittaisella luustolla (NPC:t) ne skaalataan
        self.k = ((self.H["calf_l"] - self.H["thigh_l"]).length + (self.H["foot_l"] - self.H["calf_l"]).length) / LEG_REF
        self.heel = (0.055 * self.k, a.z)

    def scaled(self, g):
        return dict(g, **{n: g[n] * self.k for n in ("stride", "lift", "clear", "width", "swing_out", "sway", "drop", "bob")})

    def arm(self, P, sd, s, fwd, bend, out=7.0):
        """Olkavarsi roikkumaan (out astetta sivulle), heilautus eteen fwd, kyynarpaan koukistus bend."""
        tU = Vector((s * sin(radians(out)), 0.03, -cos(radians(out)))).normalized()
        q_low = self.dU[s].rotation_difference(tU)
        tF = Q(X, -bend) @ Vector((s * sin(radians(out * 0.5)), 0.0, -cos(radians(out * 0.5))))
        P["upperarm_" + sd] = Q(X, -fwd) @ q_low
        P["lowerarm_" + sd] = self.dF[s].rotation_difference(q_low.inverted() @ tF)

    def common(self, P, curl=16):
        for sd, s in (("l", 1), ("r", -1)):
            for fg in ("index", "middle", "ring", "pinky"):
                for k in (1, 2, 3):
                    P["%s_0%d_%s" % (fg, k, sd)] = Q(Y, s * (curl if k > 1 else curl * 0.6))
        return P

    def idle(self, t):
        b = sin(2 * pi * t)
        P = {"spine_03": Q(X, 0.9 * b), "head": Q(X, -0.7 * b)}
        for sd, s in (("l", 1), ("r", -1)):
            self.arm(P, sd, s, 1.5 * b, 14, 7 + 0.5 * b)
            P["thigh_" + sd] = Q(Y, s * LEG_IN)
            P["foot_" + sd] = Q(Y, -s * LEG_IN)
        return self.common(P), 0.0

    # --- askellus: jalkatera kulkee maassa suoraan taaksepain, lonkka ja polvi ratkaistaan siita (kahden luun IK) ---
    @staticmethod
    def _frame(d, xh):
        ey = d.normalized()
        ex = (xh - ey * xh.dot(ey)).normalized()
        return Matrix((ex, ey, ex.cross(ey))).transposed()

    def _foot(self, u, g):
        """Nilkan paikka (eteen, ylos) vartalon suhteen ja jalkateran kallistus (astetta, + = varpaat ylos) askelvaiheessa u.
        u = 0 kantaisku, u < st tukivaihe (kanta -> koko pohja -> pakia), sen jalkeen heilahdus."""
        st, V = g["st"], g["stride"]
        bf, bd = self.ball
        hb, hd = self.heel
        def ankle(pivot_f, pivot_h, th, from_ball):
            c, s_ = cos(radians(th)), sin(radians(th))
            f, h = (-bf, bd) if from_ball else (hb, hd)
            return pivot_f + f * c - h * s_, pivot_h + f * s_ + h * c
        def ease(x):
            x = clamp(x)
            return x * x * (3 - 2 * x)
        def stance(s):
            body = V * st * (g["mid"] - s)                 # maahan kiinnitetyn pisteen paikka vartalon suhteen
            if s < g["s1"]:                                # kantakeinu
                th = g["hs"] * (1 - ease(s / g["s1"]))
                f, h = ankle(-hb, 0.0, th, False)
            elif s < g["s2"]:                              # koko pohja maassa
                th, f, h = 0.0, 0.0, hd
            else:                                          # paikiakeinu: kanta nousee, ponnistus
                th = -g["to"] * ((s - g["s2"]) / (1 - g["s2"])) ** 1.6
                f, h = ankle(bf, hd - bd, th, True)
            return body + f, h, th
        if u < st:
            return stance(u / st)
        s = (u - st) / (1 - st)
        e = 1e-3
        f0, h0, t0 = stance(1.0)
        f1, h1, t1 = stance(0.0)
        v0 = (stance(1.0)[0] - stance(1.0 - e)[0]) / e * (1 - st) / st      # nopeus jatkuu tukivaiheesta
        v1 = (stance(e)[0] - stance(0.0)[0]) / e * (1 - st) / st
        s2, s3 = s * s, s * s * s
        f = (2 * s3 - 3 * s2 + 1) * f0 + (s3 - 2 * s2 + s) * v0 + (-2 * s3 + 3 * s2) * f1 + (s3 - s2) * v1
        lift = g["lift"] * sin(pi * s ** g["lift_p"]) ** 2 + g["clear"] * sin(pi * s)
        h = h0 + (h1 - h0) * ease(s) + lift
        th = t0 + (t1 - t0) * ease((s - g["sw0"]) / (1 - g["sw0"])) - g["curl"] * sin(pi * clamp(s / g["sw0"]) * 0.5) * (1 - ease((s - g["sw0"]) / (1 - g["sw0"])))
        return f, h, th

    def gait(self, t, g):
        ph = 2 * pi * t
        c1, s1 = cos(ph), sin(ph - g["lag"])
        # lantio: kierto askeleen mukana, kallistus heilahtavan jalan puolelle, sivuttaisliike tukijalan paalle, pystyliike
        a_p = -g["twist"] * c1
        qp = Q(Z, a_p) @ Q(Y, -g["list"] * s1) @ Q(X, g["tilt"])
        off = Vector((g["sway"] * s1, 0.0, -g["drop"] + g["bob"] * cos(2 * (ph - g["bob_ph"]))))
        a_s = g["shoulder"] * c1                           # hartiat kiertyvat lantiota vastaan
        dz = a_s - a_p
        P = {"pelvis": qp,
             "spine_01": Q(Z, 0.4 * dz) @ Q(Y, 0.7 * g["list"] * s1) @ Q(X, g["lean"] * 0.5 - g["tilt"]),
             "spine_02": Q(Z, 0.35 * dz) @ Q(Y, 0.3 * g["list"] * s1) @ Q(X, g["lean"] * 0.5),
             "spine_03": Q(Z, 0.25 * dz),
             "neck_01": Q(Z, -0.4 * a_s) @ Q(X, -g["lean"] * 0.3),
             "head": Q(Z, -0.6 * a_s) @ Q(X, -g["lean"] * 0.3)}
        H = self.H
        for sd, s, du in (("l", 1, 0.0), ("r", -1, 0.5)):
            u = (t + du) % 1.0
            f, h, th = self._foot(u, g)
            hip = H["pelvis"] + off + qp @ (H["thigh_" + sd] - H["pelvis"])
            swing = clamp((u - g["st"]) / (1 - g["st"]))
            A = Vector((s * (g["width"] + g["swing_out"] * sin(pi * swing)), -f, h))
            d1, d2 = H["calf_" + sd] - H["thigh_" + sd], H["foot_" + sd] - H["calf_" + sd]
            L1, L2 = d1.length, d2.length
            n = A - hip
            D = min(n.length, (L1 + L2) * 0.9985)
            n.normalize()
            pole = Vector((s * g["knee_out"], -1.0, 0.0))  # polvi osoittaa menosuuntaan
            fw = (pole - n * pole.dot(n)).normalized()
            a = (L1 * L1 - L2 * L2 + D * D) / (2 * D)
            knee = hip + n * a + fw * sqrt(max(0.0, L1 * L1 - a * a))
            ank = hip + n * D
            ax = fw.cross(n)
            if ax.x < 0:
                ax.negate()
            qt = (self._frame(knee - hip, ax) @ self._frame(d1, X).transposed()).to_quaternion()
            qc = (self._frame(ank - knee, ax) @ self._frame(d2, X).transposed()).to_quaternion()
            qf = Q(Z, s * g["toe_out"]) @ Q(X, -th)
            P["thigh_" + sd] = qp.inverted() @ qt
            P["calf_" + sd] = qt.inverted() @ qc
            P["foot_" + sd] = qc.inverted() @ qf
            P["ball_" + sd] = Q(X, -clamp(-th, 0.0, 50.0) * (1 - swing) ** 2)   # varpaat pysyvat maassa ponnistuksessa
            sw = -cos(2 * pi * u - g["arm_lag"])           # kasi heilahtaa vastakkaisen jalan tahdissa
            self.arm(P, sd, s, g["arm_f"] * sw if sw > 0 else g["arm_b"] * sw,
                     g["elbow"] + g["elbow_a"] * max(0.0, sw), g["arm_out"])
        return self.common(P, g["curl_f"]), off

    WALK = dict(stride=1.36, st=0.61, mid=0.50, s1=0.16, s2=0.52, hs=15.0, to=52.0, lift=0.035, lift_p=0.8, clear=0.012, sw0=0.25, curl=6.0,
                width=0.062, swing_out=0.012, toe_out=6.0, knee_out=0.0, twist=5.0, list=3.0, tilt=0.0, sway=0.016, lag=0.5,
                drop=0.024, bob=-0.019, bob_ph=0.25, shoulder=4.0, lean=2.5,
                arm_f=20.0, arm_b=18.0, arm_lag=0.25, elbow=13.0, elbow_a=16.0, arm_out=7.0, curl_f=20)
    RUN = dict(stride=3.10, st=0.30, mid=0.36, s1=0.10, s2=0.42, hs=6.0, to=62.0, lift=0.30, lift_p=0.75, clear=0.03, sw0=0.45, curl=18.0,
               width=0.038, swing_out=0.01, toe_out=4.0, knee_out=0.03, twist=8.0, list=2.0, tilt=4.0, sway=0.008, lag=0.5,
               drop=0.075, bob=0.035, bob_ph=2.5, shoulder=10.0, lean=9.0,
               arm_f=38.0, arm_b=42.0, arm_lag=0.2, elbow=82.0, elbow_a=14.0, arm_out=9.0, curl_f=34)

    def walk(self, t):
        return self.gait(t, self.scaled(self.WALK))

    def run(self, t):
        return self.gait(t, self.scaled(self.RUN))

    def sit(self, t):
        P = {"spine_01": Q(X, -6), "head": Q(X, 5)}
        for sd, s in (("l", 1), ("r", -1)):
            P["thigh_" + sd] = Q(X, -82) @ Q(Y, s * 4.5)
            P["calf_" + sd] = Q(X, 78)
            P["foot_" + sd] = Q(X, 6)
            self.arm(P, sd, s, 50, 30, 10)
        return self.common(P, 30), 0.0

    def chair(self, t):
        """Istuu tuolilla tai penkilla (bottikavelijat): reidet vaakasuorassa, saaret alas, jalkapohjat maassa, kadet reisilla, hengitys ja hidas
        paan kaanto. Origo on istuinpinnan tasossa lantion alla (istuinpinta = lonkkanivel - 0,075 m), joten pelissa hahmo asetetaan istuimen korkeudelle."""
        b, b2 = sin(2 * pi * t), sin(4 * pi * t)
        qp = Q(X, -9)                                      # lantio kallistuu taakse
        P = {"pelvis": qp, "spine_01": Q(X, 5), "spine_02": Q(X, 5 + 0.6 * b2), "spine_03": Q(X, 3 + 0.8 * b2),
             "neck_01": Q(Z, 7 * b) @ Q(X, -1), "head": Q(Z, 9 * b) @ Q(X, -2 - 0.5 * b2)}
        H = self.H
        for sd, s in (("l", 1), ("r", -1)):
            qt = Q(X, -85) @ Q(Y, s * 5.5)                 # reisi eteen, polvet lonkan leveydella
            qc = qt @ Q(X, 82)                             # saari lahes pystyyn, jalkatera hieman polven edessa
            P["thigh_" + sd] = qp.inverted() @ qt
            P["calf_" + sd] = Q(X, 82)
            P["foot_" + sd] = qc.inverted() @ Q(Z, s * 9)
            self.arm(P, sd, s, 3 + 0.5 * b2, 57, 9)        # kammenet reisilla
        hip = H["pelvis"] + qp @ (H["thigh_l"] - H["pelvis"])
        return self.common(P, 26), Vector((0.0, 0.0, 0.075 - hip.z))

def bake_action(arm, name, nframes, posefn):
    act = bpy.data.actions.new(name)
    ad = arm.animation_data or arm.animation_data_create()
    ad.action = act
    prev = {}
    hips = arm.pose.bones["pelvis"]
    for f in range(nframes + 1):
        P, dz = posefn(f / nframes)
        for pb in arm.pose.bones:
            R = pb.bone.matrix_local.to_3x3()
            q = P.get(pb.name)
            ql = Quaternion() if q is None else (R.inverted() @ q.to_matrix() @ R).to_quaternion()
            if pb.name in prev and ql.dot(prev[pb.name]) < 0:
                ql.negate()
            prev[pb.name] = ql.copy()
            pb.rotation_quaternion = ql
            pb.keyframe_insert("rotation_quaternion", frame=f)
        hips.location = hips.bone.matrix_local.to_3x3().inverted() @ (Vector((0, 0, dz)) if isinstance(dz, (int, float)) else dz)
        hips.keyframe_insert("location", frame=f)
    tr = ad.nla_tracks.new()
    tr.name = name
    tr.strips.new(name, 0, act)
    ad.action = None
    return act

# ----------------------------------------------------------------------------
CAMS = {
    "front": ((1.25, -3.2, 1.30), (0.0, 0.0, 0.92), 50),
    "back":  ((-1.4, 3.1, 1.40), (0.0, 0.0, 0.92), 50),
    "walk":  ((2.5, -2.4, 1.15), (0.0, 0.0, 0.90), 50),
    "face":  ((0.30, -0.95, 1.70), (0.0, -0.02, 1.66), 70),
    "upper": ((0.55, -1.75, 1.50), (0.0, 0.0, 1.38), 50),
    "head":  ((-0.75, 0.55, 1.86), (0.0, 0.0, 1.71), 70),
    "side":  ((1.0, -0.15, 1.74), (0.0, 0.0, 1.70), 70),
}

def build_studio(col, samples, res):
    scn = bpy.context.scene
    me = bpy.data.meshes.new("Ground")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=400)
    bm.to_mesh(me); bm.free()
    g = bpy.data.objects.new("Ground", me)
    me.materials.append(make_mat("Asphalt", (0.20, 0.20, 0.21), rough=0.85))
    col.objects.link(g)
    sun = bpy.data.lights.new("Sun", 'SUN')
    sun.energy = 2.6
    sun.angle = radians(6)
    so = bpy.data.objects.new("Sun", sun)
    so.rotation_euler = (radians(52), 0, radians(38))
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
        bg.inputs[1].default_value = 1.0
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
    for look in ("AgX - Medium High Contrast", "Medium High Contrast"):
        try:
            scn.view_settings.look = look
            break
        except Exception:
            pass
    scn.render.resolution_x = int(res * 3 / 4)
    scn.render.resolution_y = res
    scn.render.fps = FPS
    return co

def set_cam(co, name):
    loc, tgt, lens = CAMS.get(name, CAMS["front"])
    co.location = loc
    co.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    co.data.lens = lens

def patch_glb(path):
    import struct
    d = open(path, "rb").read()
    jl = struct.unpack("<I", d[12:16])[0]
    j = json.loads(d[20:20 + jl])
    for m in j.get("materials", []):
        if m.get("name", "").startswith("HairShell"):
            m["alphaMode"] = "MASK"
            m["alphaCutoff"] = 0.5
            m["doubleSided"] = True
    js = json.dumps(j, separators=(",", ":")).encode()
    js += b" " * ((4 - len(js) % 4) % 4)
    rest = d[20 + jl:]
    out = b"glTF" + struct.pack("<II", 2, 12 + 8 + len(js) + len(rest)) + struct.pack("<I", len(js)) + b"JSON" + js + rest
    open(path, "wb").write(out)

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
    for blk in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights,
                bpy.data.armatures, bpy.data.actions):
        for d in list(blk):
            blk.remove(d)
    scn = bpy.context.scene
    char_col = bpy.data.collections.new("Hahmo")
    studio_col = bpy.data.collections.new("Studio")
    scn.collection.children.link(char_col)
    scn.collection.children.link(studio_col)

    base = Base(args.data)
    mats = make_materials(make_textures(out_dir))
    mesh = build_character(base, char_col, mats)
    arm = build_armature(base, char_col)
    mesh.parent = arm
    mesh.modifiers.new("Armature", 'ARMATURE').object = arm
    po = Poser(arm)
    acts = {n: bake_action(arm, n, k, fn) for n, k, fn in
            (("Idle", 90, po.idle), ("Walk", 30, po.walk), ("Run", 20, po.run), ("Sit", 30, po.sit))}
    scn.frame_start, scn.frame_end = 0, 90
    scn.render.fps = FPS
    me = mesh.data
    zs = [v.co.z for v in me.vertices]
    print("HAHMO: %d kolmiota, korkeus %.2f m, %d luuta, animaatiot: %s"
          % (sum(len(p.vertices) - 2 for p in me.polygons), max(zs) - min(zs), len(base.bones), ", ".join(acts)))
    cam = build_studio(studio_col, args.samples, args.res)
    set_cam(cam, "front")
    if not args.no_glb:
        try:
            bpy.ops.preferences.addon_enable(module="io_scene_gltf2")
        except Exception:
            pass
        for o in bpy.data.objects:
            o.select_set(o in (arm, mesh))
        bpy.context.view_layer.objects.active = arm
        path = os.path.join(out_dir, args.name + ".glb")
        kw = dict(filepath=path, export_format='GLB', use_selection=True, export_yup=True,
                  export_animations=True, export_skins=True, export_frame_range=False)
        for extra in (dict(export_animation_mode='ACTIONS', export_vertex_color='ACTIVE'),
                      dict(export_animation_mode='ACTIONS'), dict()):
            try:
                bpy.ops.export_scene.gltf(**kw, **extra)
                break
            except TypeError:
                continue
        patch_glb(path)
        print("GLB:", path, "%.0f kt" % (os.path.getsize(path) / 1024))
    arm.animation_data.action = acts["Idle"]
    scn.frame_set(0)
    if not args.no_blend:
        path = os.path.join(out_dir, args.name + ".blend")
        bpy.ops.wm.save_as_mainfile(filepath=path)
        print("BLEND:", path)
    for shot in [s for s in args.shots.split(",") if s]:
        parts = shot.split(":")
        aname = parts[1] if len(parts) > 1 else "Idle"
        arm.animation_data.action = acts[aname]
        scn.frame_set(int(parts[2]) if len(parts) > 2 else 0)
        set_cam(cam, parts[0])
        path = os.path.join(out_dir, "%s_%s_%s.png" % (args.name, parts[0], aname.lower()))
        scn.render.filepath = path
        bpy.ops.render.render(write_still=True)
        print("RENDER:", path)

if __name__ == "__main__":
    main()
