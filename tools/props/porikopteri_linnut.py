# -*- coding: utf-8 -*-
"""
PORIKOPTERI - pulu ja lokki (proseduraalinen Blender-malli)
===========================================================
Ajo: blender --background --python porikopteri_linnut.py -- --species pulu     (tai lokki)

Rakentaa linnun, luuston ja animaatiot (Fly, Glide, Idle, Walk, Peck) ja vie GLB:n selainpelia varten.
Mitat metreina. GLB:ssa lintu katsoo +Z-suuntaan (three.js), Y on ylos, origo on maassa jalkojen valissa.
Siipia on kaksi sarjaa: levitetyt (lento) ja supussa olevat (maassa). Animaatiot skaalaavat tarpeettoman
sarjan piiloon, joten oikeat siivet nakyvat automaattisesti. Koko lintu on yksi materiaali (varit verkossa).
"""
import bpy, bmesh, math, os, sys
from math import sin, cos, pi, radians
from mathutils import Vector, Matrix, Quaternion
from mathutils.bvhtree import BVHTree

LEVEL = 1          # pinnan jakotaso: 1 = noin 3 000 kolmiota, 2 = noin 10 000
FPS = 30
X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
def Q(axis, deg):
    return Quaternion(axis, radians(deg))
def clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))
def mix(a, b, t):
    t = clamp(t)
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))

# osat (materiaali-indeksi toimii rakennusvaiheessa osatunnisteena)
(P_BODY, P_WING, P_TAIL, P_FOLD, P_THIGH, P_LEG, P_EYE, P_PUPIL, P_CERE) = range(9)

SPEC = {
    "pulu": dict(
        size=0.35,
        # selkaranka pyrstontyvesta nokan karkeen: (y, z, puolileveys, puolikorkeus)
        body=[(0.105, 0.108, .018, .014), (0.085, 0.108, .034, .030), (0.050, 0.106, .050, .046),
              (0.005, 0.103, .056, .054), (-0.040, 0.106, .054, .052), (-0.072, 0.118, .044, .044),
              (-0.088, 0.142, .030, .031), (-0.094, 0.166, .022, .024), (-0.100, 0.186, .021, .022),
              (-0.114, 0.192, .017, .017), (-0.126, 0.190, .008, .008), (-0.146, 0.186, .003, .003)],
        neck_y=-0.072, head_y=-0.097, beak_y=-0.124,
        wing=dict(x0=0.04, L=0.29, z=0.128,       # (s, etureunan y, jannevali, paksuus)
                  table=[(0.00, -0.050, .100, .020), (0.20, -0.062, .135, .016), (0.45, -0.070, .135, .012),
                         (0.70, -0.055, .115, .008), (0.88, -0.025, .075, .005), (1.00, 0.020, .015, .003)]),
        tail=[(0.085, 0.108, .028, .012), (0.12, 0.106, .036, .006), (0.17, 0.103, .040, .004), (0.20, 0.101, .036, .003)],
        fold=[(-0.065, .040, .118, .022, .006), (-0.02, .054, .118, .040, .008), (0.05, .050, .120, .038, .008),
              (0.11, .030, .122, .024, .006), (0.165, .012, .118, .010, .004), (0.185, .008, .116, .004, .003)],
        leg=dict(x=0.022, y=0.015, top=0.058, hock=0.036, r=0.0042, toe=0.028, web=False),
        eye=(-0.106, 0.190, 0.0042), cere=(-0.123, 0.1975),
        flap=8, amp=48, sweep=25, pitch=16, step=16),
    "lokki": dict(
        size=0.62,
        body=[(0.19, 0.195, .028, .022), (0.15, 0.195, .058, .050), (0.08, 0.192, .082, .075),
              (0.00, 0.188, .090, .086), (-0.08, 0.192, .086, .082), (-0.135, 0.212, .066, .066),
              (-0.160, 0.255, .044, .046), (-0.170, 0.295, .034, .036), (-0.182, 0.328, .033, .034),
              (-0.210, 0.336, .027, .027), (-0.232, 0.332, .013, .015), (-0.262, 0.326, .010, .013),
              (-0.286, 0.318, .004, .006)],
        neck_y=-0.135, head_y=-0.176, beak_y=-0.228,
        wing=dict(x0=0.07, L=0.62, z=0.225,
                  table=[(0.00, -0.085, .160, .030), (0.18, -0.115, .190, .024), (0.42, -0.135, .175, .018),
                         (0.65, -0.090, .140, .012), (0.85, -0.020, .095, .007), (1.00, 0.060, .020, .004)]),
        tail=[(0.15, 0.195, .045, .020), (0.22, 0.192, .060, .009), (0.31, 0.188, .066, .005), (0.36, 0.185, .060, .004)],
        fold=[(-0.11, .066, .215, .036, .010), (-0.03, .088, .212, .064, .013), (0.09, .082, .214, .060, .012),
              (0.20, .050, .215, .040, .009), (0.31, .020, .205, .018, .006), (0.39, .010, .198, .006, .004)],
        leg=dict(x=0.040, y=0.030, top=0.115, hock=0.078, r=0.0065, toe=0.052, web=True),
        eye=(-0.196, 0.336, 0.0055), cere=None,
        flap=14, amp=32, sweep=15, pitch=6, step=22),
}

def parse_args():
    import argparse
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--species", default="pulu", choices=list(SPEC))
    p.add_argument("--level", type=int, default=LEVEL)
    p.add_argument("--out", default=None)
    p.add_argument("--shots", default="")
    p.add_argument("--samples", type=int, default=64)
    p.add_argument("--res", type=int, default=1000)
    p.add_argument("--no-blend", action="store_true")
    return p.parse_args(argv)

def interp(table, s, col):
    for a, b in zip(table[:-1], table[1:]):
        if s <= b[0]:
            t = (s - a[0]) / (b[0] - a[0])
            return a[col] + (b[col] - a[col]) * clamp(t)
    return table[-1][col]

# ----------------------------------------------------------------------------
# LUUSTO
# ----------------------------------------------------------------------------
def bone_defs(S):
    b, w, lg = S["body"], S["wing"], S["leg"]
    D = [("Root", (0, 0, 0), (0, 0, 0.03), None),
         ("Body", (0, lg["y"], lg["top"] + 0.004), (0, b[4][0], b[4][1]), "Root"),
         ("Neck", (0, b[5][0], b[5][1]), (0, b[7][0], b[7][1] + 0.006), "Body"),
         ("Head", (0, b[7][0], b[7][1] + 0.006), (0, b[-1][0], b[-1][1]), "Neck"),
         ("Tail", (0, S["tail"][0][0], S["tail"][0][1]), (0, S["tail"][-1][0], S["tail"][-1][1]), "Body"),
         ("Folded", (0, 0, b[3][1]), (0, 0.05, b[3][1]), "Body")]
    def wp(s, sg):
        return (sg * (w["x0"] + s * w["L"]), interp(w["table"], s, 1) + 0.3 * interp(w["table"], s, 2), w["z"])
    for sd, sg in (("L", 1), ("R", -1)):
        D += [("Wing_%s1" % sd, wp(0.0, sg), wp(0.20, sg), "Body"),
              ("Wing_%s2" % sd, wp(0.20, sg), wp(0.45, sg), "Wing_%s1" % sd),
              ("Wing_%s3" % sd, wp(0.45, sg), wp(1.0, sg), "Wing_%s2" % sd)]
        x = sg * lg["x"]
        D += [("Leg_" + sd, (x, lg["y"], lg["top"] + 0.012), (x, lg["y"] + 0.008, lg["hock"]), "Root"),
              ("Shank_" + sd, (x, lg["y"] + 0.008, lg["hock"]), (x, lg["y"] - 0.004, lg["r"] * 1.6), "Leg_" + sd),
              ("Foot_" + sd, (x, lg["y"] - 0.004, lg["r"] * 1.6), (x, lg["y"] - 0.004 - lg["toe"], lg["r"]), "Shank_" + sd)]
    return D

# ----------------------------------------------------------------------------
# VERKKO
# ----------------------------------------------------------------------------
def build_mesh(S, col, level):
    BD = bone_defs(S)
    BONES = [d[0] for d in BD]
    GI = {n: i for i, n in enumerate(BONES)}
    bm = bmesh.new()
    dl = bm.verts.layers.deform.verify()
    def setw(v, w):
        for n, x in w.items():
            v[dl][GI[n]] = x
    def tube(rings, n, part, cap0=False, cap1=False):
        loops = []
        for c, a, b, w in rings:
            vs = []
            for k in range(n):
                t = 2 * pi * k / n
                v = bm.verts.new(Vector(c) + Vector(a) * cos(t) + Vector(b) * sin(t))
                setw(v, w)
                vs.append(v)
            loops.append(vs)
        for i in range(len(loops) - 1):
            for k in range(n):
                k2 = (k + 1) % n
                bm.faces.new((loops[i][k], loops[i][k2], loops[i + 1][k2], loops[i + 1][k])).material_index = part
        if cap0:
            bm.faces.new(loops[0][::-1]).material_index = part
        if cap1:
            bm.faces.new(loops[-1]).material_index = part

    # vartalo, kaula, paa ja nokka yhtena putkena selkarankaa pitkin
    b = S["body"]
    rings = []
    for i, (y, z, rx, rz) in enumerate(b):
        p0, p1 = b[max(i - 1, 0)], b[min(i + 1, len(b) - 1)]
        t = Vector((0, p1[0] - p0[0], p1[1] - p0[1])).normalized()
        up = t.cross(X).normalized()
        if up.z < 0:
            up = -up
        if y >= S["neck_y"]:
            w = {"Body": 1}
        elif y > S["head_y"]:
            k = (S["neck_y"] - y) / (S["neck_y"] - S["head_y"])
            w = {"Body": 0.5, "Neck": 0.5} if k < 0.5 else {"Neck": 1}
        elif y > S["head_y"] - 0.012:
            w = {"Neck": 0.3, "Head": 0.7}
        else:
            w = {"Head": 1}
        rings.append(((0, y, z), X * rx, up * rz, w))
    tube(rings, 12, P_BODY, cap0=True, cap1=True)
    # pyrsto
    tube([((0, y, z), X * hw, Z * ht, {"Body": 0.5, "Tail": 0.5} if i == 0 else {"Tail": 1})
          for i, (y, z, hw, ht) in enumerate(S["tail"])], 8, P_TAIL, cap1=True)
    W = S["wing"]
    for sd, sg in (("L", 1), ("R", -1)):
        # levitetty siipi: poikkileikkaukset tyvesta karkeen
        rings = []
        for s, yle, ch, th in W["table"]:
            t1, t2 = clamp((s - 0.13) / 0.14), clamp((s - 0.38) / 0.14)
            w = {"Wing_%s1" % sd: 1 - t1, "Wing_%s2" % sd: t1 * (1 - t2), "Wing_%s3" % sd: t1 * t2}
            if s < 0.02:
                w = {"Body": 0.35, "Wing_%s1" % sd: 0.65}
            rings.append(((sg * (W["x0"] + s * W["L"]), yle + ch / 2, W["z"]), Y * (ch / 2), Z * (th / 2),
                          {k: v for k, v in w.items() if v > 0.001}))
        tube(rings, 8, P_WING, cap1=True)
        # supussa oleva siipi vartalon kyljella
        tube([((sg * xc, y, zc), Z * hz, X * tx, {"Folded": 1}) for y, xc, zc, hz, tx in S["fold"]], 8, P_FOLD,
             cap0=True, cap1=True)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new("Cage")
    bm.to_mesh(me)
    bm.free()
    cage = bpy.data.objects.new("Cage", me)
    col.objects.link(cage)
    for n in BONES:
        cage.vertex_groups.new(name=n)
    sub = cage.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = sub.render_levels = level
    bpy.context.view_layer.update()
    sm = bpy.data.meshes.new_from_object(cage.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(cage)
    bpy.data.meshes.remove(me)

    bm = bmesh.new()
    bm.from_mesh(sm)
    bpy.data.meshes.remove(sm)
    dl = bm.verts.layers.deform.verify()
    bvh = BVHTree.FromBMesh(bm)
    def add(kind, mtx, part, w):
        if kind == "sphere":
            r = bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=5, radius=1.0, matrix=mtx)
        else:
            r = bmesh.ops.create_cube(bm, size=1.0, matrix=mtx)
        for v in r["verts"]:
            setw(v, w)
        for f in {f for v in r["verts"] for f in v.link_faces}:
            f.material_index = part
    def path(pts, radii, segs, part, w):
        n0 = len(bm.verts)
        pts = [Vector(p) for p in pts]
        nrm, rings = None, []
        for i, p in enumerate(pts):
            t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
            nrm = t.orthogonal().normalized() if nrm is None else (nrm - t * nrm.dot(t)).normalized()
            bb = t.cross(nrm)
            rings.append([bm.verts.new(p + (nrm * cos(2 * pi * k / segs) + bb * sin(2 * pi * k / segs)) * radii[i])
                          for k in range(segs)])
        for i in range(len(pts) - 1):
            for k in range(segs):
                k2 = (k + 1) % segs
                bm.faces.new((rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k])).material_index = part
        bm.faces.new(rings[-1]).material_index = part
        for ring in rings:
            for v in ring:
                setw(v, w)
    # silmat (ja pulun vahanahka nokan tyvella)
    ey, ez, er = S["eye"]
    for sg in (1, -1):
        hit = bvh.ray_cast(Vector((sg, ey, ez)), Vector((-sg, 0, 0)))[0]
        hx = hit.x if hit is not None else sg * 0.02
        add("sphere", Matrix.Translation((hx - sg * er * 0.35, ey, ez)) @ Matrix.Diagonal((er, er, er, 1)), P_EYE, {"Head": 1})
        add("sphere", Matrix.Translation((hx + sg * er * 0.30, ey, ez)) @ Matrix.Diagonal((er * .5, er * .55, er * .55, 1)),
            P_PUPIL, {"Head": 1})
    if S["cere"]:
        cy, cz = S["cere"]
        add("sphere", Matrix.Translation((0, cy, cz)) @ Matrix.Diagonal((0.0065, 0.0075, 0.0042, 1)), P_CERE, {"Head": 1})
    # jalat ja varpaat
    lg = S["leg"]
    r = lg["r"]
    for sd, sg in (("L", 1), ("R", -1)):
        x = sg * lg["x"]
        hock = (x, lg["y"] + 0.008, lg["hock"])
        ank = Vector((x, lg["y"] - 0.004, r * 1.6))
        path([(x, lg["y"], lg["top"] + 0.02), hock], [r * 2.6, r * 1.3], 6, P_THIGH, {"Leg_" + sd: 1})
        path([hock, ank], [r, r * 0.9], 6, P_LEG, {"Shank_" + sd: 1})
        tips = []
        for ang, ln in ((-30, 0.9), (0, 1.0), (30, 0.9), (180, 0.42)):
            a = radians(ang)
            tip = ank + Vector((sin(a) * sg, -cos(a), 0)) * (lg["toe"] * ln)
            tip.z = r * 0.5
            path([ank, tip], [r * 0.8, r * 0.35], 4, P_LEG, {"Foot_" + sd: 1})
            if ang != 180:
                tips.append(tip)
        if lg["web"]:                                          # lokin raapylat
            for t0, t1 in zip(tips[:-1], tips[1:]):
                vs = [bm.verts.new(p + Vector((0, 0, r * 0.3))) for p in (ank, t0, t1)]
                for v in vs:
                    setw(v, {"Foot_" + sd: 1})
                bm.faces.new(vs).material_index = P_LEG
    bm.normal_update()
    # varitys verkon variattribuuttiin
    cl = bm.verts.layers.float_color.new("Col")
    paint = PAINT[S["name"]]
    for v in bm.verts:
        if v.link_faces:
            c = paint(S, v.link_faces[0].material_index, v.co, v.normal)
            v[cl] = (clamp(c[0]), clamp(c[1]), clamp(c[2]), 1.0)
    for f in bm.faces:
        f.material_index = 0
    zmin = min(v.co.z for v in bm.verts)
    me = bpy.data.meshes.new("BirdMesh")
    bm.to_mesh(me)
    bm.free()
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    try:
        me.set_sharp_from_angle(angle=radians(60))
    except AttributeError:
        pass
    ob = bpy.data.objects.new("BirdMesh", me)
    col.objects.link(ob)
    for n in BONES:
        ob.vertex_groups.new(name=n)
    try:
        me.color_attributes.active_color_index = 0
        me.color_attributes.render_color_index = 0
    except Exception:
        pass
    return ob, BD

# ----------------------------------------------------------------------------
# HOYHENPUVUN VARIT
# ----------------------------------------------------------------------------
def wing_uv(S, co):
    W = S["wing"]
    s = clamp((abs(co.x) - W["x0"]) / W["L"])
    return s, clamp((co.y - interp(W["table"], s, 1)) / max(interp(W["table"], s, 2), 1e-4))

def paint_pulu(S, part, co, no):
    grey, light, dark, black = (0.30, 0.33, 0.39), (0.47, 0.50, 0.55), (0.11, 0.11, 0.13), (0.025, 0.025, 0.03)
    x, y, z = co
    if part == P_BODY:
        c = mix(grey, light, (no.z - 0.2) * 2 if -0.06 < y < 0.06 else 0)        # selka vaaleampi
        c = mix(c, (0.66, 0.68, 0.71), clamp((y - 0.06) / 0.02) * clamp(no.z * 2))  # ylapera vaalea
        hn = clamp((S["neck_y"] + 0.004 - y) / 0.016)
        c = mix(c, (0.15, 0.17, 0.23), hn)                                         # paa ja kaula tummat
        if hn > 0 and y > S["beak_y"]:                                             # kaulan vihrea-violetti kiilto
            side = clamp(abs(x) / 0.02)
            c = mix(c, (0.07, 0.30, 0.19), 0.85 * side * clamp(1 - abs(z - 0.160) / 0.014))
            c = mix(c, (0.30, 0.11, 0.30), 0.85 * clamp(0.4 + side) * clamp(1 - abs(z - 0.134) / 0.016))
        if y < S["beak_y"]:
            c = (0.05, 0.045, 0.04)
        return c
    if part == P_WING:
        s, cf = wing_uv(S, co)
        if no.z < -0.1:                                                            # alapinta
            return mix(mix((0.70, 0.71, 0.73), dark, (s - 0.82) / 0.1), dark, (cf - 0.9) / 0.06)
        c = mix(light, dark, (s - 0.60) / 0.12)
        if s < 0.66 and (0.50 < cf < 0.63 or 0.79 < cf < 0.92):                    # kaksi mustaa siipijuovaa
            c = black
        return mix(c, dark, (cf - 0.95) / 0.03)
    if part == P_FOLD:
        c = light
        if 0.040 < y < 0.062 or 0.086 < y < 0.106:
            c = black
        return mix(c, dark, (y - 0.118) / 0.012)
    if part == P_TAIL:
        return mix((0.20, 0.21, 0.24), black, (y - 0.162) / 0.012)
    return {P_THIGH: grey, P_LEG: (0.55, 0.09, 0.09), P_EYE: (0.85, 0.24, 0.02), P_PUPIL: (0.01, 0.01, 0.01),
            P_CERE: (0.82, 0.82, 0.80)}[part]

def paint_lokki(S, part, co, no):
    white, grey, black = (0.86, 0.86, 0.84), (0.42, 0.45, 0.50), (0.02, 0.02, 0.025)
    x, y, z = co
    if part == P_BODY:
        c = mix(white, grey, clamp((no.z - 0.25) * 3) * clamp((y + 0.10) / 0.03) * clamp((0.17 - y) / 0.03))   # harmaa selka
        if y < S["beak_y"]:
            c = (0.85, 0.60, 0.04)                                                 # keltainen nokka
            if -0.280 < y < -0.256 and no.z < 0.1:
                c = (0.75, 0.04, 0.02)                                             # punainen tapla alanokassa
        return c
    if part == P_WING:
        s, cf = wing_uv(S, co)
        tip = clamp((s - 0.78) / 0.05)
        if no.z < -0.1:
            return mix(white, (0.10, 0.10, 0.11), tip * 0.9)
        c = mix(grey, white, (cf - 0.90) / 0.04)                                   # valkoinen takareuna
        c = mix(c, white, (0.05 - cf) / 0.03)
        c = mix(c, black, tip)                                                     # mustat siivenkarjet
        if 0.895 < s < 0.945 or s > 0.985:
            c = white                                                              # valkoiset karkilaikut
        return c
    if part == P_FOLD:
        c = mix(grey, black, (y - 0.235) / 0.02)
        if 0.295 < y < 0.315 or 0.345 < y < 0.362 or y > 0.383:
            c = white
        return c
    if part == P_TAIL:
        return white
    return {P_THIGH: white, P_LEG: (0.72, 0.47, 0.42), P_EYE: (0.80, 0.72, 0.28), P_PUPIL: (0.01, 0.01, 0.01),
            P_CERE: white}[part]

PAINT = {"pulu": paint_pulu, "lokki": paint_lokki}

# ----------------------------------------------------------------------------
# ANIMAATIOT (kierrot maailman akselien ympari lepoasennosta; eteen kallistus = positiivinen X)
# ----------------------------------------------------------------------------
HIDE = 0.001
def pose_base(flying):
    P = {}
    Sc = {"Folded": HIDE if flying else 1.0, "Wing_L1": 1.0 if flying else HIDE, "Wing_R1": 1.0 if flying else HIDE,
          "Tail": (1.5, 1, 1) if flying else 1.0}
    if flying:
        for sd in "LR":
            P["Leg_" + sd], P["Shank_" + sd], P["Foot_" + sd] = Q(X, 78), Q(X, -15), Q(X, 55)
    return P, Sc

def make_anims(S):
    A, SW, PT = S["amp"], S["sweep"], S["pitch"]
    k = S["size"] / 0.35
    def fly(t):
        ph = 2 * pi * t
        P, Sc = pose_base(True)
        up = max(0.0, cos(ph))                                     # ylosveto: siipi taittuu hieman
        for sd, sg in (("L", 1), ("R", -1)):
            P["Wing_%s1" % sd] = Q(Y, -sg * (0.75 * A * sin(ph) + 6))
            P["Wing_%s2" % sd] = Q(Y, -sg * 0.45 * A * sin(ph - 0.7)) @ Q(Z, sg * SW * up)
            P["Wing_%s3" % sd] = Q(Y, -sg * 0.60 * A * sin(ph - 1.3)) @ Q(Z, sg * 1.2 * SW * up)
        P["Neck"], P["Head"] = Q(X, 22), Q(X, -14)
        P["Tail"] = Q(X, 4 * sin(ph))
        return P, Sc, -0.012 * k * sin(ph)
    def glide(t):
        b = sin(2 * pi * t)
        P, Sc = pose_base(True)
        for sd, sg in (("L", 1), ("R", -1)):
            P["Wing_%s1" % sd] = Q(Y, -sg * (9 + 3 * b))
            P["Wing_%s2" % sd] = Q(Y, sg * 4) @ Q(Z, sg * 8)
            P["Wing_%s3" % sd] = Q(Y, sg * (6 - 2 * b)) @ Q(Z, sg * 14)
        P["Neck"], P["Head"] = Q(X, 22), Q(X, -14 + 3 * b)
        return P, Sc, 0.004 * k * b
    def idle(t):
        P, Sc = pose_base(False)
        b = sin(2 * pi * t)
        P["Body"] = Q(X, -PT + 0.8 * b)
        P["Neck"] = Q(X, PT * 0.6)
        P["Head"] = Q(Z, 22 * sin(2 * pi * t * 2) * (1 if t < 0.5 else 0.3)) @ Q(X, PT * 0.3)
        return P, Sc, 0.0
    def walk(t):
        ph = 2 * pi * t
        P, Sc = pose_base(False)
        P["Body"] = Q(Z, 3 * sin(ph)) @ Q(X, -PT)
        bob = (2 * t) % 1.0                                        # paa nykii eteen joka askeleella
        P["Neck"] = Q(X, PT * 0.6 + 14 * (bob - 0.5))
        P["Head"] = Q(X, PT * 0.3 - 10 * (bob - 0.5))
        for sd, off in (("L", 0.0), ("R", pi)):
            s_ = sin(ph + off)
            P["Leg_" + sd] = Q(X, -24 * s_)
            P["Shank_" + sd] = Q(X, 26 * max(0.0, cos(ph + off)))
            P["Foot_" + sd] = Q(X, 18 * s_ - 18 * max(0.0, cos(ph + off)))
        return P, Sc, 0.003 * k * abs(sin(ph))
    def peck(t):
        P, Sc = pose_base(False)
        d = sin(pi * t) ** 2
        tap = d * (1 + 0.12 * sin(2 * pi * t * 4))
        P["Body"] = Q(X, -PT + 34 * tap)
        P["Neck"] = Q(X, PT * 0.6 + 48 * tap)
        P["Head"] = Q(X, PT * 0.3 + 18 * tap)
        P["Tail"] = Q(X, -12 * d)
        return P, Sc, 0.0
    return [("Fly", S["flap"], fly), ("Glide", 60, glide), ("Idle", 90, idle), ("Walk", S["step"], walk), ("Peck", 40, peck)]

def build_armature(BD, col):
    ad = bpy.data.armatures.new("BirdRig")
    arm = bpy.data.objects.new("Bird", ad)
    col.objects.link(arm)
    bpy.context.view_layer.update()
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    for name, head, tail, parent in BD:
        eb = ad.edit_bones.new(name)
        eb.head, eb.tail = Vector(head), Vector(tail)
        if parent:
            eb.parent = ad.edit_bones[parent]
    bpy.ops.object.mode_set(mode='OBJECT')
    for pb in arm.pose.bones:
        pb.rotation_mode = 'QUATERNION'
    return arm

def bake_action(arm, name, nframes, posefn):
    act = bpy.data.actions.new(name)
    ad = arm.animation_data or arm.animation_data_create()
    ad.action = act
    prev = {}
    body = arm.pose.bones["Body"]
    for f in range(nframes + 1):
        P, Sc, dz = posefn(f / nframes)
        for pb in arm.pose.bones:
            R = pb.bone.matrix_local.to_3x3()
            q = P.get(pb.name)
            ql = Quaternion() if q is None else (R.inverted() @ q.to_matrix() @ R).to_quaternion()
            if pb.name in prev and ql.dot(prev[pb.name]) < 0:
                ql.negate()
            prev[pb.name] = ql.copy()
            pb.rotation_quaternion = ql
            pb.keyframe_insert("rotation_quaternion", frame=f)
            if pb.name in Sc:
                s = Sc[pb.name]
                pb.scale = s if isinstance(s, tuple) else (s, s, s)
                pb.keyframe_insert("scale", frame=f)
        body.location = body.bone.matrix_local.to_3x3().inverted() @ Vector((0, 0, dz))
        body.keyframe_insert("location", frame=f)
    tr = ad.nla_tracks.new()
    tr.name = name
    tr.strips.new(name, 0, act)
    ad.action = None
    return act

# ----------------------------------------------------------------------------
def build_studio(col, samples, res):
    scn = bpy.context.scene
    me = bpy.data.meshes.new("Ground")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=200)
    bm.to_mesh(me); bm.free()
    m = bpy.data.materials.new("Paving")
    bsdf = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED') if m.node_tree else None
    if bsdf is None:
        m.use_nodes = True
        bsdf = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs["Base Color"].default_value = (0.16, 0.16, 0.165, 1)
    bsdf.inputs["Roughness"].default_value = 0.9
    me.materials.append(m)
    col.objects.link(bpy.data.objects.new("Ground", me))
    sun = bpy.data.lights.new("Sun", 'SUN')
    sun.energy = 2.8
    sun.angle = radians(5)
    so = bpy.data.objects.new("Sun", sun)
    so.rotation_euler = (radians(50), 0, radians(35))
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
    scn.render.resolution_x = res
    scn.render.resolution_y = int(res * 3 / 4)
    scn.render.fps = FPS
    return co

SHOTS = {   # kamera ja kohde linnun koon kerrannaisina, linnun korkeus maasta
    "maassa": ((1.7, -2.3, 0.95), (0.0, -0.05, 0.42), 60, 0.0),
    "lento":  ((2.3, -2.9, 3.6), (0.0, 0.0, 2.0), 50, 2.0),
    "sivu":   ((3.2, 0.0, 0.5), (0.0, 0.0, 0.42), 60, 0.0),
}

def main():
    args = parse_args()
    S = dict(SPEC[args.species], name=args.species)
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
    for blk in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights, bpy.data.armatures, bpy.data.actions):
        for d in list(blk):
            blk.remove(d)
    scn = bpy.context.scene
    col = bpy.data.collections.new("Lintu")
    studio = bpy.data.collections.new("Studio")
    scn.collection.children.link(col)
    scn.collection.children.link(studio)

    mesh, BD = build_mesh(S, col, args.level)
    m = bpy.data.materials.new("Feathers")
    if m.node_tree is None:
        m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs["Roughness"].default_value = 0.62
    attr = m.node_tree.nodes.new("ShaderNodeVertexColor")
    attr.layer_name = "Col"
    m.node_tree.links.new(attr.outputs["Color"], bsdf.inputs["Base Color"])
    mesh.data.materials.append(m)
    arm = build_armature(BD, col)
    mesh.parent = arm
    mesh.modifiers.new("Armature", 'ARMATURE').object = arm
    acts = {n: bake_action(arm, n, k, fn) for n, k, fn in make_anims(S)}
    scn.frame_start, scn.frame_end = 0, 90
    scn.render.fps = FPS
    me = mesh.data
    xs, ys = [v.co.x for v in me.vertices], [v.co.y for v in me.vertices]
    print("LINTU %s: %d kolmiota, pituus %.2f m, siipivali %.2f m, %d luuta, animaatiot: %s" % (
        args.species, sum(len(p.vertices) - 2 for p in me.polygons), max(ys) - min(ys), max(xs) - min(xs),
        len(BD), ", ".join(acts)))
    cam = build_studio(studio, args.samples, args.res)
    name = "porikopteri_" + args.species
    try:
        bpy.ops.preferences.addon_enable(module="io_scene_gltf2")
    except Exception:
        pass
    for o in bpy.data.objects:
        o.select_set(o in (arm, mesh))
    bpy.context.view_layer.objects.active = arm
    path = os.path.join(out_dir, name + ".glb")
    kw = dict(filepath=path, export_format='GLB', use_selection=True, export_yup=True, export_animations=True,
              export_skins=True, export_frame_range=False)
    for extra in (dict(export_animation_mode='ACTIONS', export_vertex_color='ACTIVE'), dict(export_animation_mode='ACTIONS'), dict()):
        try:
            bpy.ops.export_scene.gltf(**kw, **extra)
            break
        except TypeError:
            continue
    print("GLB:", path, "%.0f kt" % (os.path.getsize(path) / 1024))
    arm.animation_data.action = acts["Idle"]
    scn.frame_set(0)
    if not args.no_blend:
        path = os.path.join(out_dir, name + ".blend")
        bpy.ops.wm.save_as_mainfile(filepath=path)
        print("BLEND:", path)
    sz = S["size"]
    for shot in [s for s in args.shots.split(",") if s]:
        parts = shot.split(":")
        loc, tgt, lens, lift = SHOTS[parts[0]]
        aname = parts[1] if len(parts) > 1 else "Idle"
        arm.animation_data.action = acts[aname]
        arm.location = (0, 0, lift * sz)
        scn.frame_set(int(parts[2]) if len(parts) > 2 else 0)
        cam.location = Vector(loc) * sz
        cam.rotation_euler = (Vector(tgt) * sz - cam.location).to_track_quat('-Z', 'Y').to_euler()
        cam.data.lens = lens
        path = os.path.join(out_dir, "%s_%s_%s.png" % (name, parts[0], aname.lower()))
        scn.render.filepath = path
        bpy.ops.render.render(write_still=True)
        print("RENDER:", path)

if __name__ == "__main__":
    main()
