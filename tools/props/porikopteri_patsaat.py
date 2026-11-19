# -*- coding: utf-8 -*-
"""
PORIKOPTERI - patsaat ja muistomerkit (proseduraaliset Blender-mallit)
======================================================================
Ajo: blender --background --python porikopteri_patsaat.py -- --out <kansio> --render

Rakentaa kartan patsaiden mallit ja vie jokaisen omaksi GLB-tiedostokseen:
karhu, hahmo, hahmoryhma, rintakuva, abstrakti_a/b/c, tiiliportti, muistomerkki, ankkuri, suihkulahde.
Hahmopatsaat tehdaan Porikopterin hahmoskriptilla (porikopteri_hahmo.py + MPFB2-aineisto), jonka polku
annetaan valitsimella --hahmo. Ilman sita hahmopatsaat jaavat pois.

Mitat metreina. Origo maan tasossa jalustan keskella, etupuoli GLB:ssa +Z-suuntaan (three.js), Y ylos.
Yleismallit ovat omia sommitelmia, eivat kopioita Porin teoksista.
"""
import bpy, bmesh, math, os, sys, runpy
from math import sin, cos, pi, radians
from mathutils import Vector, Matrix, Quaternion

(M_BRONZE, M_GRANITE, M_CORTEN, M_STEEL, M_BRICK, M_IRON, M_WATER, M_CONCRETE) = range(8)
MATS = []
COL = None
Zv = Vector((0, 0, 1))

def parse_args():
    import argparse
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=None)
    p.add_argument("--hahmo", default="/home/claude/hahmo2/porikopteri_hahmo.py")
    p.add_argument("--render", action="store_true")
    p.add_argument("--samples", type=int, default=48)
    p.add_argument("--res", type=int, default=1400)
    p.add_argument("--shots", default="rivi1,rivi2,ryhma")
    return p.parse_args(argv)

# ----------------------------------------------------------------------------
def make_mat(name, color, metallic=0.0, rough=0.5, alpha=1.0, tex=None, emission=None):
    m = bpy.data.materials.new(name)
    if m.node_tree is None:
        m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs["Base Color"].default_value = (*color, 1.0)
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = rough
    if tex is not None:
        ti = m.node_tree.nodes.new("ShaderNodeTexImage")
        ti.image = tex
        m.node_tree.links.new(ti.outputs["Color"], b.inputs["Base Color"])
    if alpha < 1.0:
        b.inputs["Alpha"].default_value = alpha
        for a, v in (("blend_method", "BLEND"), ("surface_render_method", "BLENDED")):
            try:
                setattr(m, a, v)
            except Exception:
                pass
    if emission is not None:
        for n in ("Emission Color", "Emission"):
            if n in b.inputs:
                b.inputs[n].default_value = (*emission, 1.0)
                break
        if "Emission Strength" in b.inputs:
            b.inputs["Emission Strength"].default_value = 0.25
    m.diffuse_color = (*color, alpha)
    return m

def brick_texture(out_dir):
    import numpy as np
    w, h = 192, 128                       # 3 tiilta x 8 kerrosta
    rng = np.random.default_rng(5)
    img = np.zeros((h, w, 3))
    mortar = np.array([0.45, 0.43, 0.40])
    for row in range(8):
        off = 0 if row % 2 == 0 else 32
        for k in range(4):
            x0 = (k * 64 + off) % w
            col = np.array([0.36, 0.11, 0.07]) * rng.uniform(0.75, 1.2) + rng.uniform(-0.02, 0.02, 3)
            for dx in range(64):
                x = (x0 + dx) % w
                edge = dx < 2 or dx >= 62
                img[row * 16:(row + 1) * 16, x] = mortar if edge else col
            img[row * 16:row * 16 + 2, :] = mortar
    img *= 1 + 0.06 * rng.standard_normal((h, w, 1))
    im = bpy.data.images.new("tex_tiili", w, h, alpha=False)
    px = np.concatenate([np.clip(img, 0, 1) ** (1 / 2.2), np.ones((h, w, 1))], -1).astype(np.float32)
    im.pixels.foreach_set(px.ravel())
    im.filepath_raw = os.path.join(out_dir, "tex_tiili.png")
    im.file_format = 'PNG'
    im.save()
    im.pack()
    return im

# ----------------------------------------------------------------------------
# GEOMETRIA-APURIT
# ----------------------------------------------------------------------------
def box(bm, size, center, mat, bevel=0.0, rotz=0.0, segs=2):
    tmp = bmesh.new()
    bmesh.ops.create_cube(tmp, size=1.0)
    bmesh.ops.scale(tmp, vec=Vector(size), verts=tmp.verts)
    if bevel > 0:
        bmesh.ops.bevel(tmp, geom=tmp.edges[:], offset=bevel, segments=segs, profile=0.5, affect='EDGES')
    bmesh.ops.transform(tmp, matrix=Matrix.Translation(Vector(center)) @ Matrix.Rotation(rotz, 4, 'Z'), verts=tmp.verts)
    merge(bm, tmp, None, mat)

def merge(bm, src, mtx, mat):
    """Liittaa bmeshin tai meshin; kaikki pinnat saavat materiaalin mat."""
    if isinstance(src, bmesh.types.BMesh):
        me = bpy.data.meshes.new("_tmp")
        src.to_mesh(me)
        src.free()
    else:
        me = src
    if mtx is not None:
        me.transform(mtx)
    me.polygons.foreach_set("material_index", [mat] * len(me.polygons))
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)

def tube(bm, rings, n, mat, cap0=True, cap1=True):
    """rings = [(keskipiste, akseli a, akseli b)]"""
    loops = []
    for c, a, b in rings:
        loops.append([bm.verts.new(Vector(c) + Vector(a) * cos(2 * pi * k / n) + Vector(b) * sin(2 * pi * k / n))
                      for k in range(n)])
    for i in range(len(loops) - 1):
        for k in range(n):
            k2 = (k + 1) % n
            bm.faces.new((loops[i][k], loops[i][k2], loops[i + 1][k2], loops[i + 1][k])).material_index = mat
    if cap0:
        bm.faces.new(loops[0][::-1]).material_index = mat
    if cap1:
        bm.faces.new(loops[-1]).material_index = mat

def tube_path(bm, pts, radii, segs, mat, cap0=True, cap1=True, closed=False):
    pts = [Vector(p) for p in pts]
    n = len(pts)
    nrm, rings = None, []
    for i, p in enumerate(pts):
        a = pts[(i - 1) % n] if closed else pts[max(i - 1, 0)]
        b = pts[(i + 1) % n] if closed else pts[min(i + 1, n - 1)]
        t = (b - a).normalized()
        nrm = t.orthogonal().normalized() if nrm is None else (nrm - t * nrm.dot(t)).normalized()
        bb = t.cross(nrm)
        r = radii[i] if isinstance(radii, (list, tuple)) else radii
        rings.append([bm.verts.new(p + (nrm * cos(2 * pi * k / segs) + bb * sin(2 * pi * k / segs)) * r) for k in range(segs)])
    last = n if closed else n - 1
    for i in range(last):
        A, B = rings[i], rings[(i + 1) % n]
        for k in range(segs):
            k2 = (k + 1) % segs
            bm.faces.new((A[k], A[k2], B[k2], B[k])).material_index = mat
    if not closed:
        if cap0:
            bm.faces.new(rings[0][::-1]).material_index = mat
        if cap1:
            bm.faces.new(rings[-1]).material_index = mat

def smoothed(bm, level):
    """Palauttaa uuden bmeshin, jossa pinta on pyoristetty (subdivision)."""
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new("_cage")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("_cage", me)
    COL.objects.link(ob)
    sub = ob.modifiers.new("s", 'SUBSURF')
    sub.levels = sub.render_levels = level
    bpy.context.view_layer.update()
    out = bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(ob)
    bpy.data.meshes.remove(me)
    nb = bmesh.new()
    nb.from_mesh(out)
    bpy.data.meshes.remove(out)
    return nb

def pedestal(bm, w, d, h, mat=M_GRANITE):
    box(bm, (w + 0.36, d + 0.36, 0.16), (0, 0, 0.08), mat, bevel=0.015)
    box(bm, (w + 0.14, d + 0.14, 0.14), (0, 0, 0.23), mat, bevel=0.015)
    box(bm, (w, d, h - 0.30), (0, 0, 0.30 + (h - 0.30) / 2), mat, bevel=0.02)
    return h

# ----------------------------------------------------------------------------
# HAHMOT (Porikopterin hahmoskriptista, asento paistettuna)
# ----------------------------------------------------------------------------
FIGS = {}
def pose_karhu(arm):
    """Karhukavely: kadet ja jalat maassa, lantio ylhaalla. Asento asetetaan suoraan luihin."""
    X = Vector((1, 0, 0))
    Qx = lambda d: Quaternion(X, radians(d))
    ad = arm.animation_data
    ad.action = None
    for tr in ad.nla_tracks:
        tr.mute = True
    PITCH = 105.0
    P = {"pelvis": Qx(PITCH), "spine_01": Qx(-4), "spine_02": Qx(-4), "spine_03": Qx(-4), "neck_01": Qx(-30), "head": Qx(-35)}
    total = PITCH - 12
    b = arm.data.bones
    for sd, sg, leg, knee, fwd in (("l", 1, 28, 18, -0.30), ("r", -1, 10, 30, 0.12)):
        P["thigh_" + sd], P["calf_" + sd], P["foot_" + sd] = Qx(leg - PITCH), Qx(knee), Qx(-(leg + knee))
        dU = (b["upperarm_" + sd].tail_local - b["upperarm_" + sd].head_local).normalized()
        dF = (b["lowerarm_" + sd].tail_local - b["lowerarm_" + sd].head_local).normalized()
        dH = (b["hand_" + sd].tail_local - b["hand_" + sd].head_local).normalized()
        tU = Qx(-total) @ Vector((sg * 0.06, fwd, -1)).normalized()
        qU = dU.rotation_difference(tU)
        qF = dF.rotation_difference(qU.inverted() @ tU)
        P["upperarm_" + sd], P["lowerarm_" + sd] = qU, qF
        P["hand_" + sd] = dH.rotation_difference((qU @ qF).inverted() @ (Qx(-total) @ Vector((0, -1, -0.25)).normalized()))
    for pb in arm.pose.bones:
        R = pb.bone.matrix_local.to_3x3()
        q = P.get(pb.name)
        pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = Quaternion() if q is None else (R.inverted() @ q.to_matrix() @ R).to_quaternion()
        pb.location = (0, 0, 0)
        pb.scale = (1, 1, 1)
    bpy.context.view_layer.update()

def level_on_ground(V):
    """Kaantaa hahmoa niin, etta seka kadet etta jalat osuvat maahan, ja laskee sen maan tasoon."""
    ys = [v[1] for v in V]
    ym = (min(ys) + max(ys)) / 2
    f = min((v for v in V if v[1] < ym), key=lambda v: v[2])
    k = min((v for v in V if v[1] >= ym), key=lambda v: v[2])
    a = math.atan2(f[2] - k[2], k[1] - f[1])
    c, s_ = cos(a), sin(a)
    W = [(x, y * c - z * s_, y * s_ + z * c) for x, y, z in V]
    z0 = min(w[2] for w in W)
    return [(x, y, z - z0) for x, y, z in W]

def grab_figures(hahmo, tmp):
    if not os.path.exists(hahmo):
        print("Hahmoskriptia ei loydy, hahmopatsaat jaavat pois:", hahmo)
        return
    argv0 = sys.argv
    for preset, poses in (("mies_a", (("Idle", 0), ("Walk", 22))), ("mies_b", (("Karhu", 0),))):
        sys.argv = ["x", "--", "--preset", preset, "--out", tmp, "--no-blend", "--no-glb"]
        runpy.run_path(hahmo, run_name="__main__")
        arm, ob = bpy.data.objects["Player"], bpy.data.objects["PlayerMesh"]
        for action, frame in poses:
            if action == "Karhu":
                pose_karhu(arm)
            else:
                arm.animation_data.action = bpy.data.actions[action]
                bpy.context.scene.frame_set(frame)
            ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
            me = ev.to_mesh()
            mw = ev.matrix_world.copy()
            V = [tuple(mw @ v.co) for v in me.vertices]
            F = [tuple(p.vertices) for p in me.polygons if p.material_index < 10]     # ei hiuskerroksia
            ev.to_mesh_clear()
            if action == "Karhu":
                V = level_on_ground(V)
            FIGS["%s_%s" % (preset, action)] = (V, F)
    sys.argv = argv0

def figure_bm(key, target_tris):
    V, F = FIGS[key]
    me = bpy.data.meshes.new("_fig")
    me.from_pydata(V, [], F)
    me.update()
    ob = bpy.data.objects.new("_fig", me)
    COL.objects.link(ob)
    mod = ob.modifiers.new("d", 'DECIMATE')
    mod.ratio = min(1.0, target_tris / max(1, sum(len(f) - 2 for f in F)))
    bpy.context.view_layer.update()
    out = bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(ob)
    bpy.data.meshes.remove(me)
    bm = bmesh.new()
    bm.from_mesh(out)
    bpy.data.meshes.remove(out)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    return bm

# ----------------------------------------------------------------------------
# MALLIT
# ----------------------------------------------------------------------------
def m_karhu():
    """Karhu neljalla jalalla korkealla graniittijalustalla."""
    bm = bmesh.new()
    top = pedestal(bm, 1.5, 2.9, 1.2)
    b = bmesh.new()
    X, Y = Vector((1, 0, 0)), Vector((0, 1, 0))
    spine = [(0.80, 0.70, .09, .11), (0.68, 0.73, .26, .28), (0.42, 0.76, .33, .34), (0.05, 0.74, .34, .35),
             (-0.30, 0.79, .33, .37), (-0.52, 0.80, .25, .27), (-0.70, 0.79, .20, .20), (-0.84, 0.77, .17, .165),
             (-0.96, 0.73, .10, .095), (-1.08, 0.70, .065, .06), (-1.13, 0.695, .035, .035)]
    rings = []
    for i, (y, z, rx, rz) in enumerate(spine):
        p0, p1 = spine[max(i - 1, 0)], spine[min(i + 1, len(spine) - 1)]
        t = Vector((0, p1[0] - p0[0], p1[1] - p0[1])).normalized()
        up = t.cross(X).normalized()
        if up.z < 0:
            up = -up
        rings.append(((0, y, z), X * rx, up * rz))
    tube(b, rings, 12, M_BRONZE)
    for sx in (1, -1):
        for y0, rt, dy in ((-0.30, 0.135, 0.0), (0.48, 0.165, 0.05)):          # etu- ja takajalat
            x = sx * 0.20
            leg = [((x, y0, 0.66), X * rt, Y * rt * 1.15), ((x, y0 + dy, 0.34), X * 0.105, Y * 0.115),
                   ((x, y0, 0.10), X * 0.095, Y * 0.10), ((x, y0 - 0.07, 0.045), X * 0.105, Y * 0.15),
                   ((x, y0 - 0.10, 0.012), X * 0.09, Y * 0.13)]
            tube(b, leg, 8, M_BRONZE, cap0=False)
        bmesh.ops.create_uvsphere(b, u_segments=8, v_segments=5, radius=1.0,
                                  matrix=Matrix.Translation((sx * 0.13, -0.73, 0.955)) @ Matrix.Diagonal((0.055, 0.035, 0.06, 1)))
    b = smoothed(b, 1)
    merge(bm, b, Matrix.Translation((0, 0.16, top)) @ Matrix.Scale(1.3, 4), M_BRONZE)
    return bm

def m_hahmo():
    bm = bmesh.new()
    top = pedestal(bm, 1.0, 1.0, 1.4)
    merge(bm, figure_bm("mies_a_Idle", 3200), Matrix.Translation((0, 0, top)) @ Matrix.Scale(1.25, 4), M_BRONZE)
    return bm

def m_hahmoryhma():
    bm = bmesh.new()
    tube_path(bm, [(0, 0, 0), (0, 0, 0.22), (0, 0, 0.22), (0, 0, 0.30)], [1.75, 1.75, 1.6, 1.55], 28, M_GRANITE)
    for key, pos, target in (("mies_a_Idle", (-0.80, 0.55), (-0.1, -0.5)), ("mies_a_Walk", (0.75, 0.60), (0.1, -0.5))):
        face = math.atan2(target[1] - pos[1], target[0] - pos[0]) + pi / 2          # seisojat katsovat karhukavelijaa
        merge(bm, figure_bm(key, 2400), Matrix.Translation((pos[0], pos[1], 0.30)) @ Matrix.Rotation(face, 4, 'Z')
              @ Matrix.Scale(1.1, 4), M_BRONZE)
    V = FIGS["mies_b_Karhu"][0]                                                    # karhukavelija etualalla, kulkee sivuttain
    yc = (min(v[1] for v in V) + max(v[1] for v in V)) / 2
    merge(bm, figure_bm("mies_b_Karhu", 2600), Matrix.Translation((0, -0.62, 0.30)) @ Matrix.Rotation(pi / 2, 4, 'Z')
          @ Matrix.Scale(1.1, 4) @ Matrix.Translation((0, -yc, 0)), M_BRONZE)
    return bm

def m_rintakuva():
    bm = bmesh.new()
    top = pedestal(bm, 0.55, 0.50, 1.5)
    f = figure_bm("mies_a_Idle", 9000)
    zc = 1.27
    bmesh.ops.bisect_plane(f, geom=f.verts[:] + f.edges[:] + f.faces[:], dist=1e-5, plane_co=(0, 0, zc),
                           plane_no=(0, 0, -1), clear_outer=True, clear_inner=False)
    edges = [e for e in f.edges if e.is_boundary and all(abs(v.co.z - zc) < 1e-4 for v in e.verts)]
    try:
        bmesh.ops.edgeloop_fill(f, edges=edges)
    except Exception:
        pass
    s = 1.7
    merge(bm, f, Matrix.Translation((0, 0, top + 0.10)) @ Matrix.Scale(s, 4) @ Matrix.Translation((0, 0, -zc)), M_BRONZE)
    box(bm, (0.46, 0.34, 0.12), (0, 0.01, top + 0.05), M_BRONZE, bevel=0.02)
    return bm

def m_abstrakti_a():
    """Kiertyva, ylospain kapeneva pronssimuoto."""
    bm = bmesh.new()
    box(bm, (1.5, 1.5, 0.30), (0, 0, 0.15), M_GRANITE, bevel=0.02)
    b = bmesh.new()
    rings = []
    N = 15
    for i in range(N):
        u = i / (N - 1)
        z = 0.30 + 3.1 * u
        r = (0.46 * (1 - u ** 1.4) + 0.05) * (1 + 0.32 * sin(7.0 * u + 0.6))
        tw = 2.4 * u
        a = Vector((cos(tw), sin(tw), 0)) * r
        bb = Vector((-sin(tw), cos(tw), 0)) * r * 0.62
        rings.append(((0.22 * sin(4.2 * u), 0.16 * sin(3.1 * u + 1.0), z), a, bb))
    tube(b, rings, 10, M_BRONZE)
    merge(bm, smoothed(b, 1), None, M_BRONZE)
    return bm

def m_abstrakti_b():
    """Kaksi lomittaista terasrengasta."""
    bm = bmesh.new()
    box(bm, (3.0, 1.1, 0.25), (0, 0, 0.125), M_CONCRETE, bevel=0.02)
    R = 1.35
    arc = [(R * cos(radians(a)), 0, 1.72 + R * sin(radians(a))) for a in range(-250, 71, 10)]
    tube_path(bm, arc, 0.17, 12, M_CORTEN)
    q = Matrix.Rotation(radians(62), 3, 'Z') @ Matrix.Rotation(radians(24), 3, 'X')
    ring = [Vector((0, 0, 1.55)) + q @ Vector((0.85 * cos(radians(a)), 0, 0.85 * sin(radians(a)))) for a in range(0, 360, 12)]
    tube_path(bm, ring, 0.105, 10, M_CORTEN, closed=True)
    return bm

def m_abstrakti_c():
    """Kaksi ylospain kaartuvaa terassiipea."""
    bm = bmesh.new()
    tube_path(bm, [(0, 0, 0), (0, 0, 0.20), (0, 0, 0.20), (0, 0, 0.26)], [1.25, 1.25, 1.15, 1.1], 28, M_CONCRETE)
    b = bmesh.new()
    for sg in (1, -1):
        rings = []
        N = 12
        for i in range(N):
            u = i / (N - 1)
            c = Vector((sg * (0.22 + 0.95 * u ** 2), 0.45 * sin(1.7 * u) - 0.22 + sg * 0.12, 0.26 + 3.7 * u * (1 - 0.12 * u)))
            w = 0.62 * (1 - u) ** 0.75 + 0.05
            tw = sg * (0.5 + 0.9 * u)
            rings.append((c, Vector((cos(tw), sin(tw), 0)) * w, Vector((-sin(tw), cos(tw), 0.25 * sg)).normalized() * 0.03))
        tube(b, rings, 8, M_STEEL)
    merge(bm, smoothed(b, 1), None, M_STEEL)
    return bm

def m_tiiliportti():
    """Tiilinen porttirakennelma kaariaukolla."""
    bm = bmesh.new()
    W, H, D, ow, oh = 5.2, 4.4, 1.3, 2.2, 2.0          # leveys, korkeus, syvyys, aukon leveys, kaaren alun korkeus
    arch = ([(-ow / 2, oh)] + [(-(ow / 2) * cos(radians(a)), oh + (ow / 2) * sin(radians(a))) for a in range(15, 180, 15)]
            + [(ow / 2, oh)])
    def quad(pts):
        bm.faces.new([bm.verts.new(p) for p in pts]).material_index = M_BRICK
    def column(x0, z0, x1, z1):                         # etu- ja takaseinan pala alareunasta ylos
        for y in (-D / 2, D / 2):
            quad([(x0, y, z0), (x1, y, z1), (x1, y, H), (x0, y, H)])
    column(-W / 2, 0, -ow / 2, 0)
    column(ow / 2, 0, W / 2, 0)
    for p, q in zip(arch[:-1], arch[1:]):
        column(p[0], p[1], q[0], q[1])
    loop = [(-W / 2, 0), (-W / 2, H), (W / 2, H), (W / 2, 0), (ow / 2, 0)] + arch[::-1] + [(-ow / 2, 0)]
    for p, q in zip(loop, loop[1:] + loop[:1]):         # paadyt, katto, pohja ja aukon sisapinnat
        quad([(p[0], -D / 2, p[1]), (q[0], -D / 2, q[1]), (q[0], D / 2, q[1]), (p[0], D / 2, p[1])])
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    box(bm, (W + 0.3, D + 0.3, 0.14), (0, 0, H + 0.07), M_CONCRETE, bevel=0.01)       # peitelaatta
    return bm

def m_muistomerkki():
    """Lohkottu graniittipaasi, jossa pronssilaatta."""
    bm = bmesh.new()
    box(bm, (1.8, 1.0, 0.18), (0, 0, 0.09), M_GRANITE, bevel=0.015)
    b = bmesh.new()
    bmesh.ops.create_cube(b, size=1.0)
    bmesh.ops.scale(b, vec=(1.15, 0.42, 2.0), verts=b.verts)
    bmesh.ops.subdivide_edges(b, edges=b.edges[:], cuts=5, use_grid_fill=True)
    for v in b.verts:
        x, y, z = v.co
        k = 1 - 0.22 * (z + 1.0) / 2.0                                  # kapenee ylospain
        v.co.x, v.co.y = x * k, y * k
        v.co += Vector((sin(9 * x + 3 * z), sin(11 * y + 5 * x), sin(7 * z + 4 * y))) * 0.014
    merge(bm, b, Matrix.Translation((0, 0, 1.18)), M_GRANITE)
    box(bm, (0.62, 0.03, 0.42), (0, -0.205, 1.25), M_BRONZE, bevel=0.006)
    return bm

def m_ankkuri():
    """Vanha laiva-ankkuri kivijalustalla."""
    bm = bmesh.new()
    box(bm, (2.8, 1.8, 0.28), (0, 0, 0.14), M_GRANITE, bevel=0.02)
    a = bmesh.new()
    tube_path(a, [(0, 0, 0.25), (0, 0, 2.30)], [0.065, 0.045], 10, M_IRON)                              # varsi
    tube_path(a, [(0.13 * cos(radians(t)), 0, 2.42 + 0.13 * sin(radians(t))) for t in range(0, 360, 30)],
              0.024, 8, M_IRON, closed=True)                                                            # rengas
    tube_path(a, [(0, -0.85, 2.08), (0, -0.80, 2.08), (0, 0.80, 2.08), (0, 0.85, 2.08)], [0.06, 0.04, 0.04, 0.06], 8, M_IRON)   # poikkipuu
    arc = [(0.80 * sin(radians(t)), 0, 1.05 - 0.80 * cos(radians(t))) for t in range(-66, 67, 11)]
    tube_path(a, arc, [0.04 + 0.02 * (1 - abs(i - 6) / 6) for i in range(len(arc))], 8, M_IRON)         # kaari
    for sg in (1, -1):                                                                                  # kynnet
        end = Vector(arc[-1 if sg > 0 else 0])
        t = (end - Vector(arc[-2 if sg > 0 else 1])).normalized()
        n = t.cross(Vector((0, 1, 0))).normalized()
        tri = [end + t * 0.20, end - t * 0.24 + Vector((0, 0.17, 0)), end - t * 0.24 - Vector((0, 0.17, 0))]
        va = [a.verts.new(p + n * 0.016) for p in tri]
        vb = [a.verts.new(p - n * 0.016) for p in tri]
        a.faces.new(va).material_index = M_IRON
        a.faces.new(vb[::-1]).material_index = M_IRON
        for k in range(3):
            a.faces.new((va[k], vb[k], vb[(k + 1) % 3], va[(k + 1) % 3])).material_index = M_IRON
    bmesh.ops.transform(a, matrix=Matrix.Rotation(radians(-58), 4, 'Y') @ Matrix.Rotation(radians(18), 4, 'Z'), verts=a.verts)
    zmin = min(v.co.z for v in a.verts)
    xs = [v.co.x for v in a.verts]
    bmesh.ops.translate(a, verts=a.verts, vec=(-(max(xs) + min(xs)) / 2, 0, 0.28 - zmin))
    merge(bm, a, None, M_IRON)
    return bm

def m_suihkulahde():
    """Vedessa kelluva suihkulahde: keskisuihku ja kaarisuihkujen keha. Origo vedenpinnassa."""
    bm = bmesh.new()
    tube_path(bm, [(0.95 * cos(radians(t)), 0.95 * sin(radians(t)), 0.02) for t in range(0, 360, 20)], 0.13, 8, M_IRON, closed=True)
    tube_path(bm, [(0, 0, -0.05), (0, 0, 0.22)], [0.30, 0.22], 14, M_IRON)
    tube_path(bm, [(0, 0, 0.2), (0, 0, 2.5), (0, 0, 5.0), (0, 0, 6.2)], [0.05, 0.08, 0.15, 0.03], 8, M_WATER)
    for k in range(12):
        a = radians(30 * k)
        d = Vector((cos(a), sin(a), 0))
        pts = [d * (0.45 + 2.3 * t) + Vector((0, 0, 0.15 + 10.0 * t * (1 - t))) for t in [i / 8 for i in range(9)]]
        tube_path(bm, pts, [0.03 + 0.035 * i / 8 for i in range(9)], 5, M_WATER)
    return bm

MODELS = [("karhu", m_karhu, False), ("hahmo", m_hahmo, True), ("hahmoryhma", m_hahmoryhma, True),
          ("rintakuva", m_rintakuva, True), ("muistomerkki", m_muistomerkki, False), ("ankkuri", m_ankkuri, False),
          ("abstrakti_a", m_abstrakti_a, False), ("abstrakti_b", m_abstrakti_b, False), ("abstrakti_c", m_abstrakti_c, False),
          ("tiiliportti", m_tiiliportti, False), ("suihkulahde", m_suihkulahde, False)]
LAYOUT = {"karhu": (0, 0), "hahmo": (4.6, 0), "hahmoryhma": (10.0, 0), "rintakuva": (15.0, 0), "muistomerkki": (19.0, 0),
          "ankkuri": (24.0, 0), "abstrakti_a": (0, 40), "abstrakti_b": (5.5, 40), "abstrakti_c": (11.5, 40),
          "tiiliportti": (19.5, 40), "suihkulahde": (28.5, 40)}
SHOTS = {"rivi1": ((12.0, -25.0, 3.4), (12.0, 0.0, 1.9), 31), "rivi2": ((14.2, 12.0, 4.2), (14.2, 40.0, 2.7), 31),
         "ryhma": ((12.6, -6.4, 2.5), (10.0, -0.1, 1.15), 42)}

def finish(name, bm):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if name == "tiiliportti":                                   # tiilitekstuurin UV:t pinnan suunnan mukaan
        uvl = bm.loops.layers.uv.new("UVMap")
        for f in bm.faces:
            n = f.normal
            for l in f.loops:
                co = l.vert.co
                if abs(n.z) > 0.7:
                    l[uvl].uv = (co.x / 0.77, co.y / 0.60)
                else:
                    l[uvl].uv = ((co.y if abs(n.x) > abs(n.y) else co.x) / 0.77, co.z / 0.60)
    me = bpy.data.meshes.new("Patsas_" + name)
    bm.to_mesh(me)
    bm.free()
    for m in MATS:
        me.materials.append(m)
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    try:
        me.set_sharp_from_angle(angle=radians(38))
    except AttributeError:
        pass
    ob = bpy.data.objects.new("Patsas_" + name, me)
    COL.objects.link(ob)
    zs = [v.co.z for v in me.vertices]
    print("MALLI %-13s %5d kolmiota, korkeus %.2f m" % (name, sum(len(p.vertices) - 2 for p in me.polygons), max(zs) - min(zs)))
    return ob

def build_studio(col, samples, res):
    scn = bpy.context.scene
    me = bpy.data.meshes.new("Ground")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=300)
    bm.to_mesh(me); bm.free()
    me.materials.append(make_mat("Paving", (0.20, 0.20, 0.205), rough=0.9))
    col.objects.link(bpy.data.objects.new("Ground", me))
    sun = bpy.data.lights.new("Sun", 'SUN')
    sun.energy = 2.8
    sun.angle = radians(5)
    so = bpy.data.objects.new("Sun", sun)
    so.rotation_euler = (radians(52), 0, radians(-32))
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
    scn.render.resolution_y = int(res * 0.43)
    return co

def main():
    global COL
    args = parse_args()
    cands = [args.out, os.path.dirname(bpy.data.filepath) if bpy.data.filepath else None]
    try:
        cands.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        pass
    cands.append(os.path.expanduser("~"))
    out_dir = next(c for c in cands if c and (c == args.out or os.path.isdir(c)))
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "_tmp")
    os.makedirs(tmp, exist_ok=True)
    grab_figures(args.hahmo, tmp)

    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    for blk in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights, bpy.data.armatures,
                bpy.data.actions, bpy.data.images):
        for d in list(blk):
            blk.remove(d)
    scn = bpy.context.scene
    COL = bpy.data.collections.new("Patsaat")
    studio = bpy.data.collections.new("Studio")
    scn.collection.children.link(COL)
    scn.collection.children.link(studio)
    MATS[:] = [make_mat("Bronze", (0.105, 0.125, 0.095), metallic=0.55, rough=0.55),
               make_mat("Granite", (0.36, 0.35, 0.34), rough=0.82),
               make_mat("Corten", (0.26, 0.105, 0.05), metallic=0.4, rough=0.75),
               make_mat("Steel", (0.66, 0.67, 0.69), metallic=0.75, rough=0.28),
               make_mat("Brick", (0.36, 0.11, 0.07), rough=0.9, tex=brick_texture(out_dir)),
               make_mat("Iron", (0.02, 0.02, 0.022), metallic=0.3, rough=0.7),
               make_mat("Water", (0.75, 0.85, 0.92), rough=0.15, alpha=0.6, emission=(0.8, 0.9, 1.0)),
               make_mat("Concrete", (0.42, 0.42, 0.41), rough=0.9)]
    try:
        bpy.ops.preferences.addon_enable(module="io_scene_gltf2")
    except Exception:
        pass
    objs = {}
    for name, fn, needs_fig in MODELS:
        if needs_fig and not FIGS:
            continue
        ob = finish(name, fn())
        objs[name] = ob
        for o in bpy.data.objects:
            o.select_set(o is ob)
        bpy.context.view_layer.objects.active = ob
        path = os.path.join(out_dir, "porikopteri_patsas_%s.glb" % name)
        bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True, export_apply=True, export_yup=True)
    for name, ob in objs.items():
        ob.location = (LAYOUT[name][0], LAYOUT[name][1], 0)
    cam = build_studio(studio, args.samples, args.res)
    def aim(shot):
        loc, tgt, lens = SHOTS[shot]
        cam.location = loc
        cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        cam.data.lens = lens
    aim("rivi1")
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out_dir, "porikopteri_patsaat.blend"))
    if args.render:
        for shot, row_y in (("rivi1", 0), ("rivi2", 40), ("ryhma", 0)):
            if shot not in args.shots.split(","):
                continue
            for name, ob in objs.items():
                ob.hide_render = LAYOUT[name][1] != row_y
            aim(shot)
            scn.render.filepath = os.path.join(out_dir, "porikopteri_patsaat_%s.png" % shot)
            bpy.ops.render.render(write_still=True)
            print("RENDER:", scn.render.filepath)

if __name__ == "__main__":
    main()
