# -*- coding: utf-8 -*-
"""
PORIKOPTERI - farmari ja pakettiauto (proseduraaliset Blender-mallit)
=====================================================================
Valinta: --type estate (farmari) tai --type van (pakettiauto); --detail high tai low.
Esim.:   blender --background --python porikopteri_autot.py -- --type van --detail high --shots front:0,front:3,rear:3
Rakenne, solmunimet, materiaalit ja vaurioportaat ovat samat kuin tiedostossa porikopteri_auto.py.

Ajo Blenderissa:    Scripting-valilehti -> Open -> Run Script  (HUOM: tyhjentaa nykyisen scenen)
Ajo komentorivilta: blender --background --python porikopteri_auto.py -- --detail high --render
Testattu Blender 4.2 ja 5.0.

Skripti rakentaa auton, valot ja kameran, tallentaa .blend-tiedoston
ja vie auton GLB-muotoon (glTF 2.0) selainpelia varten.

Vauriot: kori on jaettu osiin, ja vaurioituvista osista on porrasversiot samassa GLB:ssa
(solmut <Osa>_d0 ... _d3, ks. osio VAURIOT). Molemmat mallit: aja kahdesti, --detail high ja --detail low.
Kuvat portaista: --shots front:0,front:1,front:2,front:3,rear:3

Mitat metreina. GLB:ssa auton keula osoittaa +Z-suuntaan (three.js), Y on ylos,
origo on maan tasossa auton keskella. Renkaat ovat omia solmujaan
(Wheel_FL, Wheel_FR, Wheel_RL, Wheel_RR) ja pyorivat paikallisen X-akselin ympari.
"""
import bpy, bmesh, math, os, sys
from math import sin, cos, pi, radians, sqrt
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

# ----------------------------------------------------------------------------
# ASETUKSET
# ----------------------------------------------------------------------------
DETAIL      = "high"                  # "high" = pelaajan auto sisustoineen, "low" = kevyt (~7k kolmiota)
PAINT_COLOR = (0.015, 0.11, 0.42)     # maalin vari (lineaarinen RGB)
PLATE_TEXT  = "POR-123"
STICKER_TEXT  = "Porikopteri"         # takalasin teippi ("" = ei teippia)
STICKER_WIDTH = 0.80                  # teipin leveys metreina
STICKER_Z     = 1.275                 # teipin keskikohdan korkeus maasta
OUT_DIR     = None                    # None = skriptin / .blend-tiedoston kansio
EXPORT_GLB  = True
SAVE_BLEND  = True

# Auton paamitat
WHEELBASE   = 2.64
AXLE_F      =  WHEELBASE / 2
AXLE_R      = -WHEELBASE / 2
TRACK       = 1.55
WHEEL_R     = 0.325
ARCH_R      = 0.385
CREASE_SHOULDER = 0.8
CREASE_ROOF     = 0.6
CREASE_GLASS    = 0.6
GLASS_ALPHA     = 0.42                # lasin peittavyys tarkassa versiossa

# ----------------------------------------------------------------------------
def parse_args():
    import argparse
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--detail", default=DETAIL, choices=["high", "low"])
    p.add_argument("--out", default=OUT_DIR)
    p.add_argument("--name", default=None)
    p.add_argument("--render", action="store_true")
    p.add_argument("--cam", default="front")
    p.add_argument("--samples", type=int, default=96)
    p.add_argument("--res", type=int, default=1600)
    p.add_argument("--no-blend", action="store_true")
    p.add_argument("--no-glb", action="store_true")
    p.add_argument("--type", default="estate", choices=["estate", "van"])
    p.add_argument("--shots", default="", help="kamera:vaurioporras, esim. front:0,front:3,rear:3")
    return p.parse_args(argv)

# Auton koordinaatisto rakennusvaiheessa: x eteen, y vasemmalle, z ylos.
# Lopuksi kaikki kaannetaan Blenderin koordinaatistoon, jossa keula on -Y.
M_CONV = Matrix(((0, 1, 0, 0), (-1, 0, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)))

# ----------------------------------------------------------------------------
# MATERIAALIT
# ----------------------------------------------------------------------------
def _set(bsdf, names, value):
    for n in names:
        if n in bsdf.inputs:
            bsdf.inputs[n].default_value = value
            return

def make_mat(name, color, metallic=0.0, rough=0.5, coat=0.0, coat_rough=0.03,
             emission=None, emission_strength=1.0, specular=0.5, alpha=1.0, cull=False):
    m = bpy.data.materials.new(name)
    if m.node_tree is None:
        m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs["Base Color"].default_value = (*color, 1.0)
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = rough
    _set(b, ["Specular IOR Level", "Specular"], specular)
    if coat > 0:
        _set(b, ["Coat Weight", "Clearcoat"], coat)
        _set(b, ["Coat Roughness", "Clearcoat Roughness"], coat_rough)
    if emission is not None:
        _set(b, ["Emission Color", "Emission"], (*emission, 1.0))
        _set(b, ["Emission Strength"], emission_strength)
    if alpha < 1.0:                              # lapinakyva (glTF: alphaMode BLEND)
        b.inputs["Alpha"].default_value = alpha
        for attr, val in (("blend_method", "BLEND"), ("surface_render_method", "BLENDED")):
            try:
                setattr(m, attr, val)
            except Exception:
                pass
    m.use_backface_culling = cull
    m.diffuse_color = (*color, alpha)
    m.metallic = metallic
    m.roughness = rough
    return m

def make_materials(hi=True):
    M = {}
    M["paint"]   = make_mat("CarPaint", PAINT_COLOR, metallic=0.35, rough=0.35, coat=1.0)
    M["glass"]   = make_mat("Glass", (0.012, 0.016, 0.02), metallic=0.0, rough=0.04, specular=1.0,
                            alpha=GLASS_ALPHA if hi else 1.0)
    M["trim"]    = make_mat("BlackTrim", (0.012, 0.012, 0.013), rough=0.3)
    M["head"]    = make_mat("Headlight", (0.85, 0.87, 0.90), metallic=0.3, rough=0.12,
                            emission=(1.0, 0.96, 0.88), emission_strength=0.6)
    M["tail"]    = make_mat("Taillight", (0.35, 0.008, 0.008), rough=0.15,
                            emission=(1.0, 0.03, 0.02), emission_strength=0.5)
    M["grille"]  = make_mat("Grille", (0.01, 0.01, 0.011), metallic=0.2, rough=0.55)
    M["under"]   = make_mat("Underbody", (0.02, 0.02, 0.022), rough=0.85)
    M["chrome"]  = make_mat("Chrome", (0.75, 0.76, 0.78), metallic=0.85, rough=0.08)
    M["tire"]    = make_mat("Tire", (0.018, 0.018, 0.019), rough=0.88)
    M["alloy"]   = make_mat("Alloy", (0.66, 0.68, 0.70), metallic=0.7, rough=0.28)
    M["disc"]    = make_mat("BrakeDisc", (0.32, 0.32, 0.33), metallic=0.7, rough=0.45)
    M["plate"]   = make_mat("Plate", (0.9, 0.9, 0.88), rough=0.45)
    M["plateeu"] = make_mat("PlateEU", (0.0, 0.08, 0.5), rough=0.45)
    M["text"]    = make_mat("PlateText", (0.01, 0.01, 0.01), rough=0.5)
    M["seam"]    = make_mat("Seam", (0.004, 0.004, 0.005), rough=0.7)
    M["interior"] = make_mat("Interior", (0.035, 0.035, 0.038), rough=0.7)
    M["seat"]     = make_mat("Seat", (0.23, 0.20, 0.17), rough=0.55)
    M["liner"]    = make_mat("Headliner", (0.16, 0.16, 0.165), rough=0.9, cull=True)
    M["caliper"]  = make_mat("Caliper", (0.55, 0.02, 0.02), rough=0.35)
    M["sticker"]  = make_mat("Sticker", (0.92, 0.92, 0.92), rough=0.4)
    return M

# ----------------------------------------------------------------------------
# APUFUNKTIOT
# ----------------------------------------------------------------------------
def shade_smooth(me, angle=40):
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    try:
        me.set_sharp_from_angle(angle=radians(angle))      # Blender 4.1+
    except AttributeError:
        me.use_auto_smooth = True                          # Blender 3.x
        me.auto_smooth_angle = radians(angle)
    me.update()

def bm_to_obj(name, bm, mats, col, angle=40):
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    shade_smooth(me, angle)
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    return ob

def lathe(bm, prof, segs, mat):
    """Pyorahdyskappale Y-akselin ympari. prof = [(aksiaalinen, sade)].
    Normaali osoittaa profiilin kulkusuunnasta katsoen 'oikealle'."""
    rings = []
    for a, r in prof:
        if r < 1e-6:
            rings.append([bm.verts.new((0, a, 0))])
        else:
            rings.append([bm.verts.new((r * cos(2 * pi * s / segs), a, r * sin(2 * pi * s / segs)))
                          for s in range(segs)])
    out = []
    for p in range(len(prof) - 1):
        A, B = rings[p], rings[p + 1]
        for s in range(segs):
            s2 = (s + 1) % segs
            if len(A) == 1 and len(B) == 1:
                continue
            if len(A) == 1:
                vs = [A[0], B[s], B[s2]]
            elif len(B) == 1:
                vs = [A[s], B[0], A[s2]]
            else:
                vs = [A[s], B[s], B[s2], A[s2]]
            f = bm.faces.new(vs)
            f.material_index = mat
            out.append(f)
    return out

def lathe_at(bm, prof_mats, segs, origin, axis):
    """Pyorahdyskappale, jonka akseli osoittaa suuntaan 'axis' ja origo on kohdassa 'origin'."""
    n0 = len(bm.verts)
    for prof, mat in prof_mats:
        lathe(bm, prof, segs, mat)
    bm.verts.ensure_lookup_table()
    q = Vector((0, 1, 0)).rotation_difference(Vector(axis).normalized())
    mtx = Matrix.Translation(Vector(origin)) @ q.to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=mtx, verts=bm.verts[n0:])

def add_box(bm, size, loc=(0, 0, 0), rot=None, mat=0, bevel=0.0, segs=2):
    """Laatikko (valinnainen pyoristys). Palauttaa luodut pinnat."""
    tmp = bmesh.new()
    bmesh.ops.create_cube(tmp, size=1.0)
    bmesh.ops.scale(tmp, vec=Vector(size), verts=tmp.verts)
    if bevel > 0:
        bmesh.ops.bevel(tmp, geom=tmp.edges[:], offset=bevel, segments=segs,
                        profile=0.5, affect='EDGES')
    mtx = Matrix.Translation(Vector(loc))
    if rot is not None:
        mtx = mtx @ rot
    bmesh.ops.transform(tmp, matrix=mtx, verts=tmp.verts)
    me = bpy.data.meshes.new("_tmp")
    tmp.to_mesh(me)
    tmp.free()
    n0 = len(bm.faces)
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    bm.faces.ensure_lookup_table()
    faces = bm.faces[n0:]
    for f in faces:
        f.material_index = mat
    return faces

# ----------------------------------------------------------------------------
# KORI
# ----------------------------------------------------------------------------
NJ, NK = 4, 5
FB = (0.0, 0.30, 0.60, 0.86, 1.0)                 # pohjan leveysjako
CAB_LOW = [(0.84, 0.19), (0.90, 0.32), (0.905, 0.60)]

# Poikkileikkausasemat keulasta peraan. side = kyljen pisteet (y, z) alhaalta ylos,
# zc = ylapinnan korkeus keskilinjalla, w = keulan/peran pyoristyksen paino,
# bow = ylapinnan kaarevuus ylhaalta katsoen, ft = ylapinnan leveysjako.
STATIONS = [
    dict(x=2.20, w=1.00, bow=0.00, zc=0.815, ft=(0, .30, .60, .86, 1),   # 0 keulan pinta
         side=[(0.72, 0.21), (0.82, 0.33), (0.85, 0.48), (0.85, 0.62), (0.83, 0.735), (0.77, 0.785)]),
    dict(x=2.10, w=0.80, bow=0.00, zc=0.850, ft=(0, .30, .60, .86, 1),   # 1
         side=[(0.76, 0.20), (0.86, 0.33), (0.885, 0.48), (0.885, 0.635), (0.87, 0.75), (0.80, 0.81)]),
    dict(x=1.82, w=0.35, bow=0.00, zc=0.910, ft=(0, .30, .60, .87, 1),   # 2
         side=[(0.82, 0.19), (0.89, 0.32), (0.90, 0.52), (0.90, 0.73), (0.885, 0.825), (0.82, 0.875)]),
    dict(x=1.32, w=0.00, bow=0.02, zc=0.958, ft=(0, .31, .61, .89, 1),   # 3 etuakseli
         side=CAB_LOW + [(0.90, 0.83), (0.885, 0.895), (0.82, 0.928)]),
    dict(x=0.95, w=0.00, bow=0.13, zc=0.990, ft=(0, .32, .63, .92, 1),   # 4 tuulilasin alareuna
         side=CAB_LOW + [(0.895, 0.875), (0.87, 0.925), (0.80, 0.955)]),
    dict(x=0.58, w=0.00, bow=0.11, zc=1.235, ft=(0, .32, .64, .93, 1),   # 5 tuulilasin keskikohta
         side=CAB_LOW + [(0.895, 0.880), (0.857, 0.940), (0.71, 1.19)]),
    dict(x=0.20, w=0.00, bow=0.09, zc=1.435, ft=(0, .33, .65, .93, 1),   # 6 katon etureuna
         side=CAB_LOW + [(0.895, 0.885), (0.855, 0.945), (0.63, 1.385)]),
    dict(x=-0.32, w=0.00, bow=0.00, zc=1.458, ft=(0, .33, .65, .93, 1),  # 7 B-pilari
         side=CAB_LOW + [(0.895, 0.895), (0.855, 0.955), (0.625, 1.41)]),
    dict(x=-0.74, w=0.00, bow=0.00, zc=1.455, ft=(0, .33, .65, .93, 1),  # 8 takaoven keskikohta
         side=CAB_LOW + [(0.895, 0.908), (0.856, 0.968), (0.62, 1.408)]),
    dict(x=-1.15, w=0.00, bow=0.00, zc=1.440, ft=(0, .33, .65, .93, 1),  # 9 takaoven lasin loppu
         side=CAB_LOW + [(0.895, 0.925), (0.857, 0.985), (0.615, 1.395)]),
    dict(x=-1.55, w=0.15, bow=-0.04, zc=1.400, ft=(0, .33, .65, .93, 1), # 10 katon takareuna
         side=[(0.84, 0.19), (0.90, 0.33), (0.905, 0.62), (0.89, 0.945), (0.86, 1.00), (0.61, 1.36)]),
    dict(x=-1.80, w=0.45, bow=-0.06, zc=1.205, ft=(0, .32, .64, .92, 1), # 11 takalasin keskikohta
         side=[(0.82, 0.21), (0.89, 0.35), (0.90, 0.62), (0.885, 0.94), (0.86, 0.99), (0.70, 1.17)]),
    dict(x=-2.00, w=0.80, bow=-0.02, zc=1.010, ft=(0, .31, .62, .89, 1), # 12
         side=[(0.78, 0.24), (0.86, 0.38), (0.88, 0.58), (0.875, 0.78), (0.85, 0.93), (0.76, 0.99)]),
    dict(x=-2.10, w=1.00, bow=0.00, zc=0.965, ft=(0, .30, .60, .86, 1),  # 13 peran pinta
         side=[(0.74, 0.25), (0.83, 0.38), (0.85, 0.56), (0.85, 0.76), (0.83, 0.90), (0.76, 0.95)]),
]
NI = len(STATIONS)

# ----------------------------------------------------------------------------
# MALLIT: farmari ja pakettiauto
# ----------------------------------------------------------------------------
# Auto rakennetaan "suunnittelukoordinaateissa", joissa ohjaamo, ovet ja keula ovat samoissa kohdissa kuin
# alkuperaisessa viistoperassa. Lopuksi kaikki pisteet venytetaan todellisiin mittoihin (ks. Warp): pituussuunnassa
# venytetaan vain pyorankaarien ulkopuolisia alueita ja korkeussuunnassa vain kaarien ylapuolista osaa, joten
# pyorankaaret pysyvat pyoreina ja renkaan sade on sama 0,325 m.
_F = [   # yhteinen keula ja ohjaamo (asemat 0-9), sama kuin viistoperassa
    dict(x=2.20, w=1.00, bow=0.00, zc=0.815, ft=(0, .30, .60, .86, 1),
         side=[(0.72, 0.21), (0.82, 0.33), (0.85, 0.48), (0.85, 0.62), (0.83, 0.735), (0.77, 0.785)]),
    dict(x=2.10, w=0.80, bow=0.00, zc=0.850, ft=(0, .30, .60, .86, 1),
         side=[(0.76, 0.20), (0.86, 0.33), (0.885, 0.48), (0.885, 0.635), (0.87, 0.75), (0.80, 0.81)]),
    dict(x=1.82, w=0.35, bow=0.00, zc=0.910, ft=(0, .30, .60, .87, 1),
         side=[(0.82, 0.19), (0.89, 0.32), (0.90, 0.52), (0.90, 0.73), (0.885, 0.825), (0.82, 0.875)]),
    dict(x=1.32, w=0.00, bow=0.02, zc=0.958, ft=(0, .31, .61, .89, 1), side=CAB_LOW + [(0.90, 0.83), (0.885, 0.895), (0.82, 0.928)]),
    dict(x=0.95, w=0.00, bow=0.13, zc=0.990, ft=(0, .32, .63, .92, 1), side=CAB_LOW + [(0.895, 0.875), (0.87, 0.925), (0.80, 0.955)]),
    dict(x=0.58, w=0.00, bow=0.11, zc=1.235, ft=(0, .32, .64, .93, 1), side=CAB_LOW + [(0.895, 0.880), (0.857, 0.940), (0.71, 1.19)]),
    dict(x=0.20, w=0.00, bow=0.09, zc=1.435, ft=(0, .33, .65, .93, 1), side=CAB_LOW + [(0.895, 0.885), (0.855, 0.945), (0.63, 1.385)]),
    dict(x=-0.32, w=0.00, bow=0.00, zc=1.458, ft=(0, .33, .65, .93, 1), side=CAB_LOW + [(0.895, 0.895), (0.855, 0.955), (0.625, 1.41)]),
    dict(x=-0.74, w=0.00, bow=0.00, zc=1.455, ft=(0, .33, .65, .93, 1), side=CAB_LOW + [(0.895, 0.908), (0.856, 0.968), (0.62, 1.408)]),
    dict(x=-1.15, w=0.00, bow=0.00, zc=1.440, ft=(0, .33, .65, .93, 1), side=CAB_LOW + [(0.895, 0.925), (0.857, 0.985), (0.615, 1.395)]),
]
_R = [(0.84, 0.19), (0.90, 0.33), (0.905, 0.62)]
STATIONS_ESTATE = _F + [
    dict(x=-1.62, w=0.00, bow=0.00, zc=1.425, ft=(0, .33, .65, .93, 1), side=_R + [(0.892, 0.94), (0.858, 0.992), (0.612, 1.38)]),    # 10 takakaaren kohta
    dict(x=-2.08, w=0.30, bow=-0.03, zc=1.390, ft=(0, .33, .65, .93, 1),                                                             # 11 katon takareuna
         side=[(0.82, 0.21), (0.89, 0.35), (0.90, 0.62), (0.885, 0.945), (0.858, 0.995), (0.62, 1.345)]),
    dict(x=-2.21, w=0.55, bow=-0.05, zc=1.200, ft=(0, .32, .64, .92, 1),                                                             # 12 takalasin keskikohta
         side=[(0.81, 0.22), (0.885, 0.36), (0.895, 0.60), (0.88, 0.90), (0.855, 0.97), (0.70, 1.165)]),
    dict(x=-2.31, w=0.80, bow=-0.02, zc=1.010, ft=(0, .31, .62, .89, 1),                                                             # 13
         side=[(0.78, 0.24), (0.86, 0.38), (0.88, 0.58), (0.875, 0.78), (0.85, 0.93), (0.76, 0.99)]),
    dict(x=-2.36, w=1.00, bow=0.00, zc=0.965, ft=(0, .30, .60, .86, 1),                                                              # 14 peran pinta
         side=[(0.74, 0.25), (0.83, 0.38), (0.85, 0.56), (0.85, 0.76), (0.83, 0.90), (0.76, 0.95)]),
]
_VS = [(0.895, 0.96), (0.86, 1.035), (0.76, 1.412)]
STATIONS_VAN = [
    dict(x=2.20, w=1.00, bow=0.00, zc=0.950, ft=(0, .30, .60, .86, 1),
         side=[(0.72, 0.21), (0.82, 0.33), (0.85, 0.50), (0.85, 0.72), (0.83, 0.86), (0.77, 0.92)]),
    dict(x=2.10, w=0.80, bow=0.00, zc=0.965, ft=(0, .30, .60, .86, 1),
         side=[(0.76, 0.20), (0.86, 0.33), (0.885, 0.50), (0.885, 0.735), (0.87, 0.875), (0.80, 0.935)]),
    dict(x=1.82, w=0.35, bow=0.00, zc=0.985, ft=(0, .30, .60, .87, 1),
         side=[(0.82, 0.19), (0.89, 0.32), (0.90, 0.52), (0.90, 0.80), (0.885, 0.91), (0.82, 0.96)]),
    dict(x=1.32, w=0.00, bow=0.02, zc=1.012, ft=(0, .31, .61, .89, 1), side=CAB_LOW + [(0.90, 0.88), (0.885, 0.955), (0.82, 0.99)]),
    dict(x=0.95, w=0.00, bow=0.10, zc=1.035, ft=(0, .32, .63, .92, 1), side=CAB_LOW + [(0.895, 0.93), (0.872, 0.985), (0.82, 1.01)]),     # tuulilasin alareuna
    dict(x=0.70, w=0.00, bow=0.08, zc=1.265, ft=(0, .32, .64, .93, 1), side=CAB_LOW + [(0.895, 0.95), (0.862, 1.02), (0.79, 1.22)]),
    dict(x=0.42, w=0.00, bow=0.06, zc=1.452, ft=(0, .33, .65, .93, 1), side=CAB_LOW + [(0.895, 0.955), (0.86, 1.03), (0.765, 1.40)]),     # katon etureuna
    dict(x=-0.32, w=0.00, bow=0.00, zc=1.462, ft=(0, .33, .65, .93, 1), side=CAB_LOW + _VS),
    dict(x=-0.74, w=0.00, bow=0.00, zc=1.462, ft=(0, .33, .65, .93, 1), side=CAB_LOW + _VS),
    dict(x=-1.15, w=0.00, bow=0.00, zc=1.462, ft=(0, .33, .65, .93, 1), side=CAB_LOW + _VS),
    dict(x=-1.62, w=0.00, bow=0.00, zc=1.462, ft=(0, .33, .65, .93, 1), side=_R + _VS),
    dict(x=-1.95, w=0.15, bow=0.00, zc=1.460, ft=(0, .33, .65, .93, 1),
         side=[(0.83, 0.20), (0.895, 0.34), (0.90, 0.62), (0.892, 0.96), (0.858, 1.035), (0.758, 1.41)]),
    dict(x=-2.04, w=0.50, bow=0.00, zc=1.458, ft=(0, .32, .64, .92, 1),
         side=[(0.80, 0.22), (0.875, 0.36), (0.89, 0.60), (0.885, 0.93), (0.80, 1.25), (0.755, 1.405)]),
    dict(x=-2.08, w=0.80, bow=0.00, zc=1.455, ft=(0, .31, .62, .89, 1),
         side=[(0.78, 0.24), (0.86, 0.38), (0.88, 0.58), (0.875, 0.90), (0.795, 1.25), (0.75, 1.40)]),
    dict(x=-2.10, w=1.00, bow=0.00, zc=1.445, ft=(0, .30, .60, .86, 1),
         side=[(0.74, 0.25), (0.83, 0.38), (0.85, 0.56), (0.85, 0.90), (0.775, 1.25), (0.74, 1.39)]),
]
_ARC = None
TYPES = {
    "estate": dict(
        name="porikopteri_farmari", plate="ORI-789", stations=STATIONS_ESTATE, axle_f=1.32, axle_r=-1.32,
        wheelbase=2.75, front_overhang=0.90, rear_overhang=1.05, body_w=1.83, top_z=1.43, z0=0.80, int_dz=0.0,
        side_glass=tuple(range(4, 11)), rear_glass=(11, 12), tail_j=2, roof_crease=11, rear_plan=0.13, rear_lean=0.25,
        front_lean=0.30, pillars=(-0.325, -1.15), mirror_dz=0.0, plate_z=(0.54, 0.665), antenna=True, rear_wiper=True,
        handles={1: ((-0.19, 0.865), (-1.01, 0.89)), -1: ((-0.19, 0.865), (-1.01, 0.89))},
        slats=((0.660, 0.5), (0.695, 0.5), (0.368, 0.72), (0.405, 0.72), (0.442, 0.72)),
        badges=(("front", 0.765), ("rear", 0.835)), rails=True, interior="estate", tail_zmax=0.97, head_dz=0.0,
        rear_doors=False, cowl_z=0.955, door_front=((0.80, 0.265), (0.80, 0.66), (0.84, 0.84), (0.905, 0.915)), cam=1.10),
    "van": dict(
        name="porikopteri_pakettiauto", plate="PRI-456", stations=STATIONS_VAN, axle_f=1.05, axle_r=-1.32,
        wheelbase=3.00, front_overhang=0.93, rear_overhang=0.97, body_w=1.95, top_z=1.95, z0=0.78, int_dz=0.30,
        side_glass=(4, 5, 6), rear_glass=(), tail_j=3, roof_crease=None, rear_plan=0.07, rear_lean=0.04,
        front_lean=0.16, pillars=(), mirror_dz=0.045, plate_z=(0.60, 0.47), antenna=False, rear_wiper=False,
        handles={1: ((-0.19, 0.93),), -1: ((-0.19, 0.93), (-0.44, 0.93))},
        slats=((0.765, 0.5), (0.805, 0.5), (0.368, 0.72), (0.405, 0.72), (0.442, 0.72)),
        badges=(("front", 0.89),), rails=False, interior="van", tail_zmax=1.32, head_dz=0.12,
        rear_doors=True, cowl_z=1.01, door_front=((0.64, 0.265), (0.655, 0.50), (0.74, 0.665), (0.80, 0.75), (0.84, 0.88), (0.905, 0.945)),
        cam=1.22),
}
T = TYPES["estate"]

def apply_type(name):
    global T, STATIONS, NI, AXLE_F, AXLE_R, PLATE_TEXT, STICKER_TEXT
    T = TYPES[name]
    STATIONS = T["stations"]
    NI = len(STATIONS)
    AXLE_F, AXLE_R = T["axle_f"], T["axle_r"]
    PLATE_TEXT = T["plate"]
    STICKER_TEXT = ""                               # lainatuissa autoissa ei ole teippia

class Warp:
    """Suunnittelukoordinaatit -> todelliset mitat. Tasoitettu, jotta pintoihin ei tule taitteita."""
    def __init__(self, x_front, x_rear, z_top):
        import numpy as np
        self.np = np
        F, R = T["axle_f"], T["axle_r"]
        self.sy = T["body_w"] / 1.81
        xs = np.arange(-3.2, 3.2, 0.002)
        def table(slopes):
            sn, sc, sr = slopes
            raw = np.ones_like(xs)
            raw[xs > F + 0.47] = sn                    # keula
            raw[(xs > R + 0.47) & (xs < -0.32)] = sc   # kylki B-pilarin takana
            raw[xs < R - 0.47] = sr                    # pera
            k = np.ones(61) / 61.0
            sm_ = np.convolve(np.pad(raw, 30, mode="edge"), k, mode="valid")
            m = np.cumsum(sm_) * 0.002
            return sm_, m
        at = lambda m, x: float(np.interp(x, xs, m))
        sl = [1.0, 1.0, 1.0]
        for _ in range(8):                             # ratkaistaan venytykset akselivalin ja ylitysten mukaan
            sm_, m = table(sl)
            sl[0] += (T["front_overhang"] - (at(m, x_front) - at(m, F))) / max(0.05, x_front - F - 0.47)
            sl[1] += (T["wheelbase"] - (at(m, F) - at(m, R))) / (-0.32 - R - 0.47)
            sl[2] += (T["rear_overhang"] - (at(m, R) - at(m, x_rear))) / max(0.05, R - 0.47 - x_rear)
        sm_, m = table(sl)
        self.xs, self.mx, self.sx = xs, m - (at(m, F) + at(m, R)) / 2, sm_
        zs = np.arange(-0.2, 2.2, 0.002)
        kz = 1.0
        for _ in range(8):
            raw = np.where(zs > T["z0"], kz, 1.0)
            smz = np.convolve(np.pad(raw, 25, mode="edge"), np.ones(51) / 51.0, mode="valid")
            mz = np.cumsum(smz) * 0.002
            mz = mz - float(np.interp(0.0, zs, mz))
            kz += (T["top_z"] - float(np.interp(z_top, zs, mz))) / (z_top - T["z0"])
        self.zs, self.mz, self.sz = zs, mz, smz
        print("VENYTYS: keula %.2f, kylki %.2f, pera %.2f, korkeus %.2f, leveys %.3f" % (sl[0], sl[1], sl[2], kz, self.sy))
    def X(self, x):
        return float(self.np.interp(x, self.xs, self.mx))
    def apply(self, ob, rigid_z=False):
        np = self.np
        me = ob.data
        if not len(me.polygons):
            return
        cn = np.array(corner_normals(me))
        co = np.array([v.co[:] for v in me.vertices])
        sx = np.interp(co[:, 0], self.xs, self.sx)
        sz = np.ones(len(co)) if rigid_z else np.interp(co[:, 2], self.zs, self.sz)
        new = np.column_stack([np.interp(co[:, 0], self.xs, self.mx), co[:, 1] * self.sy,
                               co[:, 2] + T["int_dz"] if rigid_z else np.interp(co[:, 2], self.zs, self.mz)])
        me.vertices.foreach_set("co", new.ravel())
        me.update()
        lv = np.array([l.vertex_index for l in me.loops])
        n = cn / np.column_stack([sx[lv], np.full(len(lv), self.sy), sz[lv]])
        n /= np.linalg.norm(n, axis=1)[:, None] + 1e-12
        try:
            me.normals_split_custom_set(n.tolist())
        except Exception as e:
            print("Normaalien asetus ei onnistunut:", ob.name, e)

(M_PAINT, M_GLASS, M_TRIM, M_HEAD, M_TAIL, M_GRILLE, M_UNDER) = range(7)

def station_point(i, j, k):
    s = STATIONS[i]
    side = s["side"]
    y0, z0 = side[0]
    y5, z5 = side[NK]
    ft = s["ft"]
    top_z = lambda y: z5 + (s["zc"] - z5) * (1 - (y / y5) ** 2)
    if j == NJ:
        y, z = side[k]
    elif k == 0:
        y, z = FB[j] * y0, z0
    elif k == NK:
        y = ft[j] * y5
        z = top_z(y)
    else:                                   # keulan / peran pinnan sisapisteet
        yk, zk = side[k]
        t = (zk - z0) / (z5 - z0)
        y = (FB[j] + (ft[j] - FB[j]) * t) * yk
        z = z0 + (top_z(ft[j] * y5) - z0) * t
    x = s["x"]
    if k == NK and j < NJ:
        x += s["bow"] * (1 - (y / y5) ** 2)
    plan = (y / 0.85) ** 3
    if i <= 3:
        x -= s["w"] * 0.20 * plan
    else:
        x += s["w"] * T["rear_plan"] * plan
    if i == 0:
        if z > 0.62: x -= T["front_lean"] * (z - 0.62)
        if z < 0.40: x -= 0.25 * (0.40 - z)
    if i == NI - 1:
        if z > 0.60: x += T["rear_lean"] * (z - 0.60)
        if z < 0.45: x += 0.30 * (0.45 - z)
    return (x, y, z)

def strip_mat(i, n):
    if n <= 3:
        return M_UNDER
    if n == 8:                                   # sivulasit
        if i in T["side_glass"]: return M_GLASS
    if n == 7:
        if i in (0, 1): return M_HEAD
        if i == NI - 2: return M_TAIL
    if n >= 10:
        if i in (4, 5): return M_GLASS           # tuulilasi
        if i in T["rear_glass"]: return M_GLASS    # takalasi
    return M_PAINT

def cap_mat(front, j, k):
    if k == 0:
        return M_UNDER
    if front:
        if k == 1: return M_GRILLE if j <= 2 else M_PAINT
        if k == 3: return M_GRILLE if j <= 1 else M_HEAD
    else:
        if k == 3 and j >= T["tail_j"]: return M_TAIL
    return M_PAINT

def build_body(M, col, level, arch_segs):
    bm = bmesh.new()
    V = {}
    def vert(i, j, k):
        key = (i, j, k)
        if key not in V:
            V[key] = bm.verts.new(station_point(i, j, k))
        return V[key]
    ring = ([(j, 0) for j in range(NJ + 1)] + [(NJ, k) for k in range(1, NK + 1)]
            + [(j, NK) for j in range(NJ - 1, -1, -1)])
    for i in range(NI - 1):
        for n in range(len(ring) - 1):
            a, b = ring[n], ring[n + 1]
            f = bm.faces.new((vert(i, *a), vert(i, *b), vert(i + 1, *b), vert(i + 1, *a)))
            f.material_index = strip_mat(i, n)
    for i, front in ((0, True), (NI - 1, False)):
        for j in range(NJ):
            for k in range(NK):
                f = bm.faces.new((vert(i, j, k), vert(i, j + 1, k), vert(i, j + 1, k + 1), vert(i, j, k + 1)))
                f.material_index = cap_mat(front, j, k)
    # muotolinjat (crease)
    try:
        cl = bm.edges.layers.float.get("crease_edge") or bm.edges.layers.float.new("crease_edge")
    except Exception:
        cl = bm.edges.layers.crease.verify()
    def crease(a, b, val):
        e = bm.edges.get((vert(*a), vert(*b)))
        if e is not None:
            e[cl] = val
    for i in range(NI - 1):
        if 2 <= i <= NI - 4: crease((i, NJ, 3), (i + 1, NJ, 3), CREASE_SHOULDER)
        if 1 <= i <= NI - 3: crease((i, NJ, 0), (i + 1, NJ, 0), 0.5)
    for j in range(NJ):
        if T["roof_crease"] is not None:
            crease((T["roof_crease"], j, NK), (T["roof_crease"], j + 1, NK), CREASE_ROOF)
        crease((0, j, NK), (0, j + 1, NK), 0.3)
    bmesh.ops.mirror(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], axis='Y', merge_dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])

    # Lasien, valojen ja sakeikon kehykset
    for mat, thick, depth, border, cr in ((M_GLASS, 0.018, 0.004, M_TRIM, CREASE_GLASS),
                                          (M_HEAD, 0.010, 0.0, M_TRIM, 0.5),
                                          (M_TAIL, 0.008, 0.0, M_TRIM, 0.5),
                                          (M_GRILLE, 0.018, 0.02, M_TRIM, 0.4)):
        faces = [f for f in bm.faces if f.material_index == mat]
        fset = set(faces)
        for f in faces:                      # alueen ulkoreuna teravammaksi
            for e in f.edges:
                if sum(1 for lf in e.link_faces if lf in fset) == 1:
                    e[cl] = max(e[cl], cr)
        r = bmesh.ops.inset_region(bm, faces=faces, thickness=thick, depth=-depth,
                                   use_boundary=True, use_even_offset=True)
        for f in r["faces"]:
            f.material_index = border
        if mat == M_HEAD:                    # tumma linssi, jonka keskella LED-nauha
            faces = [f for f in bm.faces if f.material_index == mat]
            r = bmesh.ops.inset_region(bm, faces=faces, thickness=0.02, depth=0.0,
                                       use_boundary=True, use_even_offset=True)
            for f in r["faces"]:
                f.material_index = M_GLASS

    mats = [M["paint"], M["glass"], M["trim"], M["head"], M["tail"], M["grille"], M["under"]]
    cage = bm_to_obj("BodyCage", bm, mats, col)
    sub = cage.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = sub.render_levels = level

    # Pyorakotelot leikataan sylintereilla
    cb = bmesh.new()
    for ax in (AXLE_F, AXLE_R):
        for sgn in (1, -1):
            r = bmesh.ops.create_cone(cb, cap_ends=True, segments=arch_segs,
                                      radius1=ARCH_R, radius2=ARCH_R, depth=0.60)
            mtx = Matrix.Translation((ax, sgn * 0.85, WHEEL_R)) @ Matrix.Rotation(pi / 2, 4, 'X')
            bmesh.ops.transform(cb, matrix=mtx, verts=r["verts"])
    for f in cb.faces:
        f.material_index = 0
    cutter = bm_to_obj("ArchCutter", cb, [M["under"]], col)
    boo = cage.modifiers.new("Arches", 'BOOLEAN')
    boo.operation = 'DIFFERENCE'
    boo.object = cutter
    boo.solver = 'EXACT'
    try:
        boo.material_mode = 'TRANSFER'
    except Exception:
        pass
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(cage.evaluated_get(dg))
    me.name = "Body"
    body = bpy.data.objects.new("Body", me)
    col.objects.link(body)
    for o in (cage, cutter):
        d = o.data
        bpy.data.objects.remove(o)
        bpy.data.meshes.remove(d)
    shade_smooth(me, 40)
    return body

# ----------------------------------------------------------------------------
# PYORAT
# ----------------------------------------------------------------------------
def build_wheel(name, M, col, left, hi):
    bm = bmesh.new()
    T, A, D, DK = 0, 1, 2, 3          # rengas, vanne, jarrulevy, tumma
    seg_t = 56 if hi else 16
    seg_r = 40 if hi else 12
    R = WHEEL_R
    if hi:
        half = [(0.000, R), (0.014, R), (0.017, R - 0.007), (0.025, R - 0.007), (0.028, R),
                (0.046, R), (0.049, R - 0.007), (0.057, R - 0.007), (0.060, R),
                (0.076, R - 0.001), (0.094, R - 0.007), (0.106, R - 0.023), (0.111, R - 0.047),
                (0.109, R - 0.072), (0.101, R - 0.092), (0.094, R - 0.103), (0.090, R - 0.109)]
    else:
        half = [(0.000, R), (0.075, R - 0.001), (0.104, R - 0.02), (0.110, R - 0.06), (0.090, R - 0.109)]
    prof = [(-a, r) for a, r in reversed(half[1:])] + half
    lathe(bm, prof, seg_t, T)
    # vanteen reuna, sisapinta ja takalevy
    lathe(bm, [(0.094, 0.218), (0.101, 0.214), (0.101, 0.204)], seg_r, A)
    lathe(bm, [(0.101, 0.204), (0.086, 0.198), (-0.085, 0.196), (-0.085, 0.0)], seg_r, DK)
    # napa
    lathe(bm, [(0.040, 0.066), (0.078, 0.062), (0.082, 0.056), (0.082, 0.030), (0.088, 0.026), (0.088, 0.0)],
          seg_r, A)
    if hi:                                   # pyoranpultit
        for n in range(5):
            al = 2 * pi * n / 5 + pi / 2 + pi / 5
            r = bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.0075, radius2=0.0075, depth=0.012)
            mtx = Matrix.Translation((0.043 * cos(al), 0.086, 0.043 * sin(al))) @ Matrix.Rotation(-pi / 2, 4, 'X')
            bmesh.ops.transform(bm, matrix=mtx, verts=r["verts"])
            for f in {f for v in r["verts"] for f in v.link_faces}:
                f.material_index = DK
    if hi:
        lathe(bm, [(0.012, 0.160), (0.034, 0.160), (0.034, 0.055)], seg_r, D)
    # puolat: 5 x V-pari
    for n in range(5):
        base = 2 * pi * n / 5 + pi / 2
        for d in (-1, 1):
            th1 = base + d * radians(5)
            th2 = base + d * radians(21)
            r1, r2 = 0.040, 0.203
            c1 = Vector((r1 * cos(th1), 0, r1 * sin(th1)))
            c2 = Vector((r2 * cos(th2), 0, r2 * sin(th2)))
            axis = (c2 - c1).normalized()
            tan = Vector((0, 1, 0)).cross(axis).normalized()
            ends = []
            for c, w, a_out, th in ((c1, 0.030, 0.076, 0.030), (c2, 0.022, 0.092, 0.024)):
                ends.append([bm.verts.new(c + tan * (w / 2 * sx) + Vector((0, a, 0)))
                             for sx, a in ((-1, a_out - th), (1, a_out - th), (0.7, a_out), (-0.7, a_out))])
            mid = (c1 + c2) / 2 + Vector((0, 0.07, 0))
            for q in range(4):
                q2 = (q + 1) % 4
                f = bm.faces.new((ends[0][q], ends[0][q2], ends[1][q2], ends[1][q]))
                f.material_index = A
                f.normal_update()
                ctr = f.calc_center_median()
                ap = c1 + axis * (ctr - c1).dot(axis) + Vector((0, 0.07, 0))
                if f.normal.dot(ctr - ap) < 0:
                    f.normal_flip()
    if not left:
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(pi, 3, 'Z'), verts=bm.verts)
    ob = bm_to_obj(name, bm, [M["tire"], M["alloy"], M["disc"], M["under"]], col, angle=35)
    return ob

# ----------------------------------------------------------------------------
# YKSITYISKOHDAT
# ----------------------------------------------------------------------------
class Surface:
    """Sateenheitto valmiiseen koriin (auton koordinaatistossa)."""
    def __init__(self, body):
        me = body.data
        self.bvh = BVHTree.FromPolygons([v.co.copy() for v in me.vertices],
                                        [tuple(p.vertices) for p in me.polygons])
        self.mat = [p.material_index for p in me.polygons]
        self.last_mat = None
    def cast(self, mode, a, b, sgn=1):
        if mode == "side":   o, d = (a, sgn * 1.6, b), (0, -sgn, 0)
        elif mode == "top":  o, d = (a, sgn * b, 2.6), (0, 0, -1)
        elif mode == "rear": o, d = (-3.6, sgn * a, b), (1, 0, 0)
        else:                o, d = (3.6, sgn * a, b), (-1, 0, 0)
        return self.ray(o, d)
    def ray(self, o, d):
        loc, nor, idx, _ = self.bvh.ray_cast(Vector(o), Vector(d))
        self.last_mat = self.mat[idx] if idx is not None else None
        return loc, nor

def resample(pts, step, closed=False):
    pts = [Vector(p) for p in pts]
    if closed:
        pts = pts + [pts[0]]
    out = []
    for p, q in zip(pts[:-1], pts[1:]):
        n = max(1, int(round((q - p).length / step)))
        out += [p.lerp(q, t / n) for t in range(n)]
    out.append(pts[-1])
    return out

def smooth_path(pts, it=2):
    """Pyoristaa murtoviivan kulmat (Chaikin)."""
    pts = [Vector(p) for p in pts]
    for _ in range(it):
        new = [pts[0]]
        for p, q in zip(pts[:-1], pts[1:]):
            new += [p.lerp(q, 0.25), p.lerp(q, 0.75)]
        new.append(pts[-1])
        pts = new
    return pts

def project_strip(bm, surf, pts, mode, sgn=1, width=0.007, lift=0.003, mat=0, step=0.03, closed=False,
                  only=None):
    hits = []
    for p in resample(pts, step, closed):
        loc, nor = surf.cast(mode, p[0], p[1], sgn)
        if loc is not None and (only is None or surf.last_mat in only):
            hits.append((loc, nor))
    if len(hits) < 2:
        return
    rows = []
    for n, (loc, nor) in enumerate(hits):
        a = hits[max(n - 1, 0)][0]
        b = hits[min(n + 1, len(hits) - 1)][0]
        if closed and n in (0, len(hits) - 1):
            a, b = hits[-2][0], hits[1][0]
        side = nor.cross(b - a)
        if side.length < 1e-9:
            side = Vector((0, 0, 1))
        side.normalize()
        base = loc + nor * lift
        rows.append((bm.verts.new(base - side * width / 2), bm.verts.new(base + side * width / 2), nor))
    for (a1, a2, n1), (b1, b2, _) in zip(rows[:-1], rows[1:]):
        f = bm.faces.new((a1, a2, b2, b1))
        f.material_index = mat
        f.normal_update()
        if f.normal.dot(n1) < 0:
            f.normal_flip()

def bar_along(bm, surf, pts, mode, w, h, lift, mat, sgn=1, step=0.15):
    """Kapea tanko, joka seuraa pintaa (esim. pyyhkijan sulka)."""
    hits = []
    for p in resample(pts, step):
        loc, nor = surf.cast(mode, p[0], p[1], sgn)
        if loc is not None:
            hits.append((loc, nor))
    for (a, na), (b, nb) in zip(hits[:-1], hits[1:]):
        n = (na + nb).normalized()
        xax = (b - a).normalized()
        yax = n.cross(xax).normalized()
        zax = xax.cross(yax)
        rot = Matrix((xax, yax, zax)).transposed().to_4x4()
        add_box(bm, ((b - a).length + 0.004, w, h), (a + b) / 2 + n * lift, rot, mat=mat)

def build_interior(M, col, body):
    """Sisusta: lattia, ovipaneelit, kojelauta, ohjauspyora, istuimet ja sisakatto."""
    bm = bmesh.new()
    IN, SE = 0, 1
    def quad(pts, mat=IN):
        f = bm.faces.new([bm.verts.new(p) for p in pts])
        f.material_index = mat
    FZ, BZ, HZ = 0.32, 0.915, 0.72          # lattia, vyotarolinja, pyorakotelon paalinen
    X0, X1, X2, X3 = 1.0, -0.92, -1.30, -1.90
    kind = T["interior"]
    if kind == "van":                        # ohjaamo, valiseina ja tyhja tavaratila
        XB, XR, ZT = -0.42, -2.00, 1.52
        quad([(X0, -0.80, FZ), (X0, 0.80, FZ), (XB, 0.80, FZ), (XB, -0.80, FZ)])
        quad([(XB, -0.80, FZ), (XB, 0.80, FZ), (XB, 0.80, 1.0), (XB, 0.70, ZT), (XB, -0.70, ZT), (XB, -0.80, 1.0)])      # valiseina
        quad([(XB - 0.02, -0.80, FZ), (XB - 0.02, 0.80, FZ), (XR, 0.74, FZ), (XR, -0.74, FZ)])                         # tavaratilan lattia
        quad([(XB - 0.02, -0.70, ZT), (XB - 0.02, 0.70, ZT), (XR, 0.66, ZT), (XR, -0.66, ZT)])                         # katto
        for s in (1, -1):
            quad([(X0, s * 0.80, FZ), (XB, s * 0.80, FZ), (XB, s * 0.80, BZ), (X0, s * 0.80, BZ)])
            quad([(X0, s * 0.80, BZ), (XB, s * 0.80, BZ), (XB, s * 0.85, BZ), (X0, s * 0.85, BZ)])
            quad([(XB - 0.02, s * 0.80, FZ), (XR, s * 0.74, FZ), (XR, s * 0.74, 1.0), (XB - 0.02, s * 0.80, 1.0)])
            quad([(XB - 0.02, s * 0.80, 1.0), (XR, s * 0.74, 1.0), (XR, s * 0.66, ZT), (XB - 0.02, s * 0.70, ZT)])
    else:
        quad([(X0, -0.80, FZ), (X0, 0.80, FZ), (X1, 0.80, FZ), (X1, -0.80, FZ)])
        quad([(X1, -0.54, FZ), (X1, 0.54, FZ), (X2, 0.54, FZ), (X2, -0.54, FZ)])
        quad([(X2, -0.80, FZ), (X2, 0.80, FZ), (X2, 0.80, HZ if kind == "estate" else BZ), (X2, -0.80, HZ if kind == "estate" else BZ)])
        if kind == "estate":                 # avoin tavaratila, nakyy takalasista
            XC = -2.19
            quad([(X2, -0.80, HZ), (X2, 0.80, HZ), (XC, 0.66, HZ), (XC, -0.66, HZ)])
            quad([(XC, -0.66, HZ), (XC, 0.66, HZ), (XC, 0.66, BZ), (XC, -0.66, BZ)])
            for s in (1, -1):
                quad([(X2, s * 0.80, HZ), (XC, s * 0.66, HZ), (XC, s * 0.66, BZ), (X2, s * 0.80, BZ)])
        else:
            quad([(X2, -0.80, BZ), (X2, 0.80, BZ), (X3, 0.66, BZ), (X3, -0.66, BZ)])          # hattuhylly
        for s in (1, -1):
            quad([(X0, s * 0.80, FZ), (X1, s * 0.80, FZ), (X1, s * 0.80, BZ), (X0, s * 0.80, BZ)])
            quad([(X0, s * 0.80, BZ), (X2, s * 0.80, BZ), (X2, s * 0.85, BZ), (X0, s * 0.85, BZ)])
            quad([(X1, s * 0.80, HZ), (X2, s * 0.80, HZ), (X2, s * 0.80, BZ), (X1, s * 0.80, BZ)])
            quad([(X1, s * 0.54, HZ), (X1, s * 0.80, HZ), (X2, s * 0.80, HZ), (X2, s * 0.54, HZ)])
            quad([(X1, s * 0.54, FZ), (X1, s * 0.80, FZ), (X1, s * 0.80, HZ), (X1, s * 0.54, HZ)])
            quad([(X1, s * 0.54, FZ), (X2, s * 0.54, FZ), (X2, s * 0.54, HZ), (X1, s * 0.54, HZ)])
    # kojelauta, mittaristo, keskikonsoli
    add_box(bm, (0.50, 1.52, 0.32), (0.83, 0, 0.76), mat=IN, bevel=0.04)
    add_box(bm, (0.15, 0.36, 0.07), (0.66, 0.37, 0.945), mat=IN, bevel=0.02)
    add_box(bm, (0.95, 0.20, 0.22), (0.22, 0, 0.43), mat=IN, bevel=0.02)
    add_box(bm, (0.03, 0.26, 0.17), (0.575, 0.0, 0.86), Matrix.Rotation(radians(20), 4, 'Y'), mat=IN, bevel=0.008, segs=1)
    # ohjauspyora (vasen puoli)
    ctr = Vector((0.47, 0.37, 0.92))
    axis = Vector((-0.906, 0, 0.423))
    rim = [(0.016 * sin(2 * pi * t / 8), 0.185 + 0.016 * cos(2 * pi * t / 8)) for t in range(9)]
    lathe_at(bm, [(rim, IN)], 24, ctr, axis)
    rot = Matrix.Rotation(radians(25), 4, 'Y')
    add_box(bm, (0.02, 0.36, 0.035), ctr, rot, mat=IN)
    add_box(bm, (0.04, 0.10, 0.10), ctr, rot, mat=IN, bevel=0.01, segs=1)
    add_box(bm, (0.26, 0.05, 0.05), ctr - axis * 0.125, rot, mat=IN)
    # etuistuimet
    tilt = Matrix.Rotation(radians(-15), 4, 'Y')
    for s in (1, -1):
        add_box(bm, (0.50, 0.50, 0.14), (0.02, s * 0.37, 0.47), mat=SE, bevel=0.035)
        add_box(bm, (0.13, 0.48, 0.62), (-0.27, s * 0.37, 0.80), tilt, mat=SE, bevel=0.035)
        add_box(bm, (0.10, 0.27, 0.17), (-0.375, s * 0.37, 1.20), tilt, mat=SE, bevel=0.03)
    if kind != "van":                        # takapenkki
        add_box(bm, (0.50, 1.06, 0.15), (-0.92, 0, 0.50), mat=SE, bevel=0.035)
        add_box(bm, (0.13, 1.06, 0.60), (-1.21, 0, 0.82), Matrix.Rotation(radians(-18), 4, 'Y'), mat=SE, bevel=0.035)
        for s in (1, -1):
            add_box(bm, (0.09, 0.24, 0.15), (-1.33, s * 0.30, 1.165), tilt, mat=SE, bevel=0.03)
    interior = bm_to_obj("Interior", bm, [M["interior"], M["seat"]], col, angle=50)

    # sisakatto: korin ylaosan sisapinta (nakyy vain sisalta)
    hb = bmesh.new()
    hb.from_mesh(body.data)
    keep = set(f for f in hb.faces if f.material_index in (M_PAINT, M_TRIM)
               and min(v.co.z for v in f.verts) > 1.0 and -2.6 < f.calc_center_median().x < 1.02)
    bmesh.ops.delete(hb, geom=[f for f in hb.faces if f not in keep], context='FACES')
    hb.normal_update()
    for v in hb.verts:
        v.co -= v.normal * 0.015
    bmesh.ops.reverse_faces(hb, faces=hb.faces[:])
    for f in hb.faces:
        f.material_index = 0
    liner = bm_to_obj("Headliner", hb, [M["liner"]], col)
    return [interior, liner]

def build_seams(M, col, surf):
    bm = bmesh.new()
    cx, cz = AXLE_R, WHEEL_R
    arc = [(cx + 0.47 * cos(radians(a)), cz + 0.47 * sin(radians(a))) for a in range(-6, 61, 6)]
    side_lines = [smooth_path(list(T["door_front"])),                                    # etuoven etureuna
                  [(-0.325, 0.265), (-0.325, 0.925)],                                  # etuoven takareuna
                  [(T["door_front"][0][0], 0.265), (cx + 0.47 * cos(radians(-6)), 0.265)]]   # kynnys
    if not T["rear_doors"]:
        side_lines.append(smooth_path(arc + [(-1.185, 0.84), (-1.20, 0.955)], 1))      # takaoven takareuna
    for sgn in (1, -1):
        for ln in side_lines:
            project_strip(bm, surf, ln, "side", sgn)
    if T["rear_doors"]:                                                                # pakettiauto: liukuovi oikealla, pariovet takana
        for ln in ([(-0.36, 0.265), (-0.36, 1.40)], [(-0.83, 0.265), (-0.83, 1.40)], [(-0.36, 1.40), (-0.83, 1.40)],
                   [(-0.83, 0.995), (-1.97, 0.995)]):
            project_strip(bm, surf, ln, "side", -1)
        project_strip(bm, surf, [(-0.60, 0.265), (-0.60, 1.40)], "side", 1)
        for ln in ([(0.0, 0.60), (0.0, 1.40)], [(-0.66, 0.60), (-0.66, 1.40)], [(0.66, 0.60), (0.66, 1.40)],
                   [(-0.66, 0.598), (-0.01, 0.598)], [(0.01, 0.598), (0.66, 0.598)], [(-0.66, 1.402), (-0.01, 1.402)], [(0.01, 1.402), (0.66, 1.402)]):
            project_strip(bm, surf, ln, "rear", 1)
    # tankin luukku (oikea kylki)
    flap = [(-1.56 + 0.075 * cos(radians(a)), 0.845 + 0.075 * sin(radians(a))) for a in range(0, 360, 20)]
    project_strip(bm, surf, flap, "side", -1, width=0.005, step=0.02, closed=True)
    # konepelti
    half = smooth_path([(2.085, 0.0), (2.07, 0.30), (2.01, 0.56), (1.90, 0.70), (1.50, 0.755), (1.12, 0.775), (0.99, 0.775)])
    full = [(p[0], -p[1]) for p in reversed(half[1:])] + list(half)
    project_strip(bm, surf, full, "top")
    if not T["rear_doors"]:                                                            # takaluukku
        half = smooth_path([(0.0, 0.575), (0.50, 0.575), (0.56, 0.60), (0.565, 0.74)], 1)
        full = [(-p[0], p[1]) for p in reversed(half[1:])] + list(half)
        project_strip(bm, surf, full, "rear")
        for sgn in (1, -1):
            project_strip(bm, surf, smooth_path([(0.565, 0.915), (0.60, 0.96), (0.66, 0.985)], 1), "rear", sgn)
    return bm_to_obj("Seams", bm, [M["seam"]], col)

def build_details(M, col, surf, hi):
    bm = bmesh.new()
    P, TR, CH, PL, EU, HD, TL, CA, DK = range(9)
    for sgn in (1, -1):
        # sivupeilit
        mz = T["mirror_dz"]
        loc, _ = surf.cast("side", 0.80, 0.955 + mz, sgn)
        y0 = abs(loc.y) if loc is not None else 0.86
        add_box(bm, (0.05, 0.10, 0.022), (0.80, sgn * (y0 + 0.02), 0.955 + mz), mat=TR, bevel=0.006)
        rot = Matrix.Rotation(sgn * radians(-8), 4, 'Z')
        add_box(bm, (0.075, 0.17, 0.11), (0.775, sgn * (y0 + 0.115), 0.99 + mz), rot, mat=P, bevel=0.022,
                segs=3 if hi else 1)
        add_box(bm, (0.004, 0.14, 0.084), (0.775 - 0.0385, sgn * (y0 + 0.115 + 0.005), 0.99 + mz), rot, mat=CH)
        # ovenkahvat
        for hx, hz in T["handles"][sgn]:
            loc, _ = surf.cast("side", hx, hz, sgn)
            if loc is None:
                continue
            rot = Matrix.Rotation(radians(-2.5), 4, 'Y')
            add_box(bm, (0.17, 0.03, 0.028), (hx, loc.y + sgn * 0.004, hz), rot, mat=P, bevel=0.008,
                    segs=2 if hi else 1)
    # lokasuojan kaaren reunat
    for ax in (AXLE_F, AXLE_R):
        rr = ARCH_R + 0.019
        arc = [(ax + rr * cos(radians(a)), WHEEL_R + rr * sin(radians(a))) for a in range(-14, 195, 4 if hi else 12)]
        for sgn in (1, -1):
            project_strip(bm, surf, arc, "side", sgn, width=0.034, lift=0.007, mat=P, step=0.5)
    # B-pilarin musta peitelevy lasin paalla
    for sgn in (1, -1):
        for px in T["pillars"]:
            project_strip(bm, surf, [(px, 0.90), (px, 1.45)], "side", sgn, width=0.085, lift=0.004,
                          mat=TR, step=0.04, only=(M_GLASS, M_TRIM))
    # rekisterikilvet
    for mode, z in (("front", T["plate_z"][0]), ("rear", T["plate_z"][1])):
        loc, nor = surf.cast(mode, 0.0, z)
        if loc is None:
            continue
        d = 1 if mode == "front" else -1
        tilt = math.atan2(nor.z, abs(nor.x))
        rot = Matrix.Rotation(-d * tilt, 4, 'Y')
        ctr = loc + nor * 0.012
        add_box(bm, (0.016, 0.47, 0.13), ctr, rot, mat=TR, bevel=0.003, segs=1)
        add_box(bm, (0.004, 0.445, 0.112), ctr + nor * 0.0085, rot, mat=PL)
        add_box(bm, (0.004, 0.04, 0.112), ctr + nor * 0.0095 + Vector((0, -d * 0.2025, 0)), rot, mat=EU)
    # kattoantenni
    if T["rails"]:                                           # kattokaiteet
        for sgn in (1, -1):
            bar_along(bm, surf, [(0.05, 0.535), (-0.70, 0.54), (-1.40, 0.535), (-2.02, 0.515)], "top", 0.024, 0.020, 0.038, CH, sgn, step=0.2)
            for fx, fy in ((0.05, 0.535), (-0.98, 0.538), (-2.02, 0.515)):
                loc, nor = surf.cast("top", fx, fy, sgn)
                if loc is not None:
                    add_box(bm, (0.075, 0.03, 0.042), (loc.x, loc.y, loc.z + 0.018), mat=TR, bevel=0.006, segs=1)
    if T["rear_doors"]:                                      # takaoven kahva (vasen ovi)
        loc, nor = surf.cast("rear", 0.075, 0.96)
        if loc is not None:
            add_box(bm, (0.03, 0.035, 0.17), (loc.x - 0.012, loc.y, loc.z), mat=TR, bevel=0.008, segs=1)
    loc, nor = surf.cast("top", -1.30, 0.0)
    if loc is not None and T["antenna"]:
        z = loc.z - 0.004
        vs = [bm.verts.new(v) for v in ((-1.22, 0.024, z), (-1.22, -0.024, z), (-1.39, -0.028, z), (-1.39, 0.028, z),
                                        (-1.335, 0.006, z + 0.058), (-1.335, -0.006, z + 0.058),
                                        (-1.385, -0.007, z + 0.052), (-1.385, 0.007, z + 0.052))]
        for idx in ((0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0), (4, 7, 6, 5)):
            f = bm.faces.new([vs[n] for n in idx])
            f.material_index = TR
        bmesh.ops.recalc_face_normals(bm, faces=[f for f in bm.faces if f.material_index == TR])
    if hi:
        # tuulilasinpyyhkijat ja takalasin pyyhkija
        for pts, mode in [([(0.94, 0.62), (1.02, 0.06)], "top"), ([(1.02, -0.03), (0.945, -0.60)], "top")] + (
                [([(0.0, 1.085), (0.34, 1.075)], "rear")] if T["rear_wiper"] else []):
            bar_along(bm, surf, pts, mode, 0.014, 0.02, 0.016, TR)
        # sakeikon rimat, sumuvalot, takaheijastimet
        for z, hw in T["slats"]:
            project_strip(bm, surf, [(-hw, z), (hw, z)], "front", width=0.011, lift=0.007, mat=TR, only=(M_GRILLE,))
        for sgn in (1, -1):
            project_strip(bm, surf, [(0.745, 0.405), (0.80, 0.40)], "front", sgn, width=0.022, lift=0.004, mat=HD)
            project_strip(bm, surf, [(0.50, 0.455), (0.68, 0.455)], "rear", sgn, width=0.026, lift=0.004, mat=TL)
        # pakoputken paat
        for y in (-0.46, -0.54):
            loc, nor = surf.cast("rear", y, 0.305)
            if loc is not None:
                lathe_at(bm, [([(-0.06, 0.031), (0.035, 0.031), (0.035, 0.025)], CH),
                              ([(0.035, 0.025), (-0.03, 0.024), (-0.03, 0.0)], DK)], 20, loc, (-1, 0, 0))
        # merkit keulassa ja perassa
        for mode, z in T["badges"]:
            loc, nor = surf.cast(mode, 0.0, z)
            if loc is not None:
                lathe_at(bm, [([(0.0, 0.036), (0.005, 0.034), (0.007, 0.0)], CH)], 20, loc, nor)
        # jarrusatulat (eivat pyori renkaan mukana)
        for ax, ang in ((AXLE_F, 150), (AXLE_R, 30)):
            for sgn in (1, -1):
                ctr = (ax + 0.135 * cos(radians(ang)), sgn * (TRACK / 2 + 0.030), WHEEL_R + 0.135 * sin(radians(ang)))
                add_box(bm, (0.065, 0.044, 0.14), ctr, Matrix.Rotation(-radians(ang), 4, 'Y'), mat=CA, bevel=0.008, segs=1)
    ob = bm_to_obj("Details", bm, [M["paint"], M["trim"], M["chrome"], M["plate"], M["plateeu"],
                                   M["head"], M["tail"], M["caliper"], M["under"]], col, angle=50)
    return ob

def build_plate_text(M, col, surf):
    obs = []
    for mode, z in (("front", T["plate_z"][0]), ("rear", T["plate_z"][1])):
        loc, nor = surf.cast(mode, 0.0, z)
        if loc is None:
            continue
        try:
            cu = bpy.data.curves.new("PlateTextCurve", 'FONT')
            cu.body = PLATE_TEXT
            cu.align_x = 'CENTER'
            cu.align_y = 'CENTER'
            cu.size = 0.105
            tmp = bpy.data.objects.new("PlateTextTmp", cu)
            col.objects.link(tmp)
            bpy.context.view_layer.update()
            me = bpy.data.meshes.new_from_object(tmp.evaluated_get(bpy.context.evaluated_depsgraph_get()))
            bpy.data.objects.remove(tmp)
            bpy.data.curves.remove(cu)
        except Exception as e:
            print("Kilven tekstia ei voitu luoda:", e)
            return obs
        d = 1 if mode == "front" else -1
        tilt = math.atan2(nor.z, abs(nor.x))
        # tekstin taso (X oikealle, Y ylos, normaali +Z) -> auton pinta
        basis = Matrix(((0, 0, d, 0), (d, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
        mtx = (Matrix.Translation(loc + nor * 0.0235 + Vector((0, d * 0.018, 0)))
               @ Matrix.Rotation(-d * tilt, 4, 'Y') @ basis)
        me.transform(mtx)
        me.name = "PlateText"
        me.materials.clear()
        me.materials.append(M["text"])
        ob = bpy.data.objects.new("PlateText_" + mode, me)
        col.objects.link(ob)
        obs.append(ob)
    return obs

def build_sticker(M, col, surf):
    """Takalasin teippi: teksti asetellaan lasin tasoon ja painetaan lasin pintaa pitkin."""
    if not STICKER_TEXT:
        return []
    p0, n = surf.cast("rear", 0.0, STICKER_Z)
    if p0 is None:
        return []
    try:
        cu = bpy.data.curves.new("StickerCurve", 'FONT')
        cu.body = STICKER_TEXT
        cu.align_x = 'CENTER'
        cu.align_y = 'CENTER'
        cu.size = 1.0
        cu.offset = 0.012                      # hieman lihavampi kirjain
        try:
            cu.fill_mode = 'FRONT'
        except Exception:
            pass
        tmp = bpy.data.objects.new("StickerTmp", cu)
        col.objects.link(tmp)
        bpy.context.view_layer.update()
        me = bpy.data.meshes.new_from_object(tmp.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        bpy.data.objects.remove(tmp)
        bpy.data.curves.remove(cu)
    except Exception as e:
        print("Teippia ei voitu luoda:", e)
        return []
    xs = [v.co.x for v in me.vertices]
    sc = STICKER_WIDTH / (max(xs) - min(xs))
    u = Vector((0, -1, 0))                     # lukijan oikea takaa katsottuna
    v = u.cross(n)
    if v.z < 0:
        v = -v
    v.normalize()
    for vert in me.vertices:
        q = p0 + u * (vert.co.x * sc) + v * (vert.co.y * sc)
        hit, hn = surf.ray(q + n * 0.3, -n)
        if hit is None:
            hit, hn = q, n
        vert.co = hit + hn * 0.004
    me.name = "Sticker"
    me.materials.clear()
    me.materials.append(M["sticker"])
    me.update()
    ob = bpy.data.objects.new("Sticker", me)
    col.objects.link(ob)
    return [ob]

# ----------------------------------------------------------------------------
# VAURIOT: kori jaetaan osiin ja vaurioituvista osista tehdaan porrasversiot (_d0.._d3)
# ----------------------------------------------------------------------------
# Solmut nimetaan <Osa>_d<N>. Peli nayttaa kustakin osasta korkeimman portaan, joka on enintaan auton
# nykyinen vaurioporras. Kaikilla portailla on sama origo ja asento, joten vaihto tehdaan pelkalla nakyvyydella.
# Nakyvat vauriot ovat auton vasemmassa etukulmassa ja oikeassa takakulmassa.
HOOD_OUTLINE = [(2.085, 0.0), (2.07, 0.30), (2.01, 0.56), (1.90, 0.70), (1.50, 0.755), (1.12, 0.775), (0.99, 0.775)]
DAMAGE_PARTS_LOW = ("Hood", "BumperF", "Windshield", "HeadlightL", "HeadlightR")

def corner_normals(me):
    try:
        return [tuple(n.vector) for n in me.corner_normals]            # Blender 4.1+
    except AttributeError:
        me.calc_normals_split()
        return [tuple(l.normal) for l in me.loops]

class Src:
    """Lahdeverkko: pisteet, pinnat, kulmanormaalit ja materiaalit talteen ennen jakamista."""
    def __init__(self, ob):
        me = ob.data
        self.V = [v.co.copy() for v in me.vertices]
        cn = corner_normals(me)
        self.P = [(tuple(p.vertices), [cn[i] for i in range(p.loop_start, p.loop_start + p.loop_total)],
                   me.materials[p.material_index], Vector(p.center), Vector(p.normal)) for p in me.polygons]
    def islands(self):
        """Erilliset kappaleet: [(pintojen indeksit, keskipiste, materiaalien nimet)]"""
        parent = list(range(len(self.V)))
        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a
        for idx, *_ in self.P:
            r = find(idx[0])
            for i in idx[1:]:
                parent[find(i)] = r
        groups = {}
        for f, (idx, *_r) in enumerate(self.P):
            groups.setdefault(find(idx[0]), []).append(f)
        out = []
        for fids in groups.values():
            c = sum((self.P[f][3] for f in fids), Vector()) / len(fids)
            out.append((fids, c, {self.P[f][2].name for f in fids}))
        return out

def piece(src, fids):
    remap, F = {}, []
    for f in fids:
        idx, nrm, mat = src.P[f][:3]
        F.append((tuple(remap.setdefault(i, len(remap)) for i in idx), nrm, mat))
    V = [None] * len(remap)
    for i, k in remap.items():
        V[k] = src.V[i].copy()
    return {"V": V, "F": F}

def bm_piece(bm, mat):
    bm.verts.index_update()
    pc = {"V": [v.co.copy() for v in bm.verts], "F": [(tuple(v.index for v in f.verts), None, mat) for f in bm.faces]}
    bm.free()
    return pc

def deform(pc, fn, keep_normals=False):
    return {"V": [fn(v.copy()) for v in pc["V"]], "F": [(i, n if keep_normals else None, m) for i, n, m in pc["F"]]}

def remat(pc, mp):
    return {"V": pc["V"], "F": [(i, n, mp.get(m.name, m)) for i, n, m in pc["F"]]}

def make_mesh(name, pieces, angle=40):
    V, F, N, MI, mats = [], [], [], [], []
    for pc in pieces:
        off = len(V)
        V += pc["V"]
        for idx, nrm, mat in pc["F"]:
            F.append(tuple(i + off for i in idx))
            N.append(nrm)
            if mat not in mats:
                mats.append(mat)
            MI.append(mats.index(mat))
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in V], [], F)
    for m in mats:
        me.materials.append(m)
    me.polygons.foreach_set("material_index", MI)
    me.polygons.foreach_set("use_smooth", [True] * len(F))
    me.update()
    try:
        me.set_sharp_from_angle(angle=radians(angle))
    except AttributeError:
        pass
    if any(n is not None for n in N):                       # ehjan auton varjostus sailyy tasmalleen samana
        auto = corner_normals(me)
        out, k = [], 0
        for f, n in zip(F, N):
            for c in range(len(f)):
                out.append(n[c] if n is not None else auto[k])
                k += 1
        try:
            me.normals_split_custom_set(out)
        except Exception as e:
            print("Normaalien asetus ei onnistunut:", name, e)
    return me

def sm(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)

def hood_half_width(x):
    pts = sorted(HOOD_OUTLINE)
    if x <= pts[0][0]:
        return pts[0][1]
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return -1.0

def hood_front_x(y):
    pts = sorted(HOOD_OUTLINE, key=lambda p: p[1])
    y = abs(y)
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        if y <= y1 and y1 > y0:
            return x0 + (x1 - x0) * (y - y0) / (y1 - y0)
    return pts[-1][0]

def build_damage(M, col, surf, body, details, seams, hi):
    M["glasscracked"] = make_mat("GlassCracked", (0.62, 0.66, 0.68), rough=0.35, alpha=0.9 if hi else 1.0)
    M["lampbroken"] = make_mat("LampBroken", (0.03, 0.03, 0.035), rough=0.6)
    M["baremetal"] = make_mat("BareMetal", (0.42, 0.43, 0.45), metallic=0.7, rough=0.45)
    B, D = Src(body), Src(details)
    S = Src(seams) if seams is not None else None
    want = (lambda n: True) if hi else (lambda n: n in DAMAGE_PARTS_LOW)

    # ---- korin pintojen luokittelu osiin
    groups = {}
    for f, (idx, nrm, mat, c, n) in enumerate(B.P):
        mn, side = mat.name, ("L" if c.y > 0 else "R")
        part = "Body"
        if mn == "Glass" and c.x > 0.15 and abs(n.y) < 0.6 and c.z > 0.9:
            part = "Windshield"
        elif mn in ("Headlight", "Glass", "BlackTrim") and c.x > 1.55 and abs(c.y) > 0.503 and 0.57 < c.z < 0.95:
            part = "Headlight" + side
        elif mn in ("Taillight", "BlackTrim") and c.x < -1.75 and abs(c.y) > 0.40 and c.z < T["tail_zmax"]:
            part = "Taillight" + side
        elif mn == "CarPaint" and c.x > 0.9 and n.z > 0.3 and abs(c.y) < hood_half_width(c.x):
            part = "Hood"
        elif T["rear_doors"] and n.x < -0.5 and c.x < -1.98 and c.z > 0.585 and abs(c.y) < 0.70:
            part = "RearDoor" + side
        elif c.x > 1.80:
            part = "BumperF"
        elif c.x < -1.74 and c.z < 0.585:
            part = "BumperR"
        elif mn == "CarPaint" and 0.80 < c.x <= 1.80 and abs(c.y) > 0.35:
            part = "FenderF" + side
        elif mn == "CarPaint" and -1.12 < c.x <= 0.80 and abs(c.y) > 0.55 and 0.24 < c.z < 0.905 and abs(n.y) > 0.35:
            part = "Side" + side
        if not want(part):
            part = "Body"
        groups.setdefault(part, []).append(f)
    P = {k: [piece(B, v)] for k, v in groups.items()}

    # ---- pienosat (Details) ja saumat (Seams) mukaan niihin osiin, joiden mukana niiden pitaa liikkua
    plate = []
    rest_d = []
    for fids, c, names in D.islands():
        side = "L" if c.y > 0 else "R"
        tgt = None
        if c.x > 1.85:
            tgt = "BumperF"
        elif abs(c.y) > 0.84 and 0.70 < c.x < 0.90 and c.z > 0.92:
            tgt = "Mirror" + side
        elif abs(c.y) > 0.80 and 0.85 < c.x < 1.80 and c.z < 0.80:
            tgt = "FenderF" + side
        elif abs(c.y) > 0.85 and -1.15 < c.x < 0.0 and 0.80 < c.z < 0.93:
            tgt = "Side" + side
        elif c.x < -1.90 and c.z < 0.50:
            tgt = "BumperR"
        if tgt is None or not want(tgt):
            rest_d += fids
            continue
        pc = piece(D, fids)
        if tgt == "BumperF" and abs(c.y) < 0.30 and 0.47 < c.z < 0.61:
            plate.append(pc)                               # rekisterikilpi pidikkeineen (irtoaa portaalla 3)
        elif tgt.startswith("Mirror"):
            P.setdefault(tgt, []).append(pc)
            if names == {"BlackTrim"}:
                P.setdefault(tgt + "_stub", []).append(pc)     # pelkka kiinnitysjalka
        else:
            P.setdefault(tgt, []).append(pc)
    rest_s = []
    if S is not None:
        for fids, c, names in S.islands():
            side = "L" if c.y > 0 else "R"
            tgt = None
            if T["rear_doors"] and c.x < -1.95 and c.z > 0.58:
                tgt = "RearDoor" + side                     # takaovien saumat
            elif c.x > 0.95 and c.z > 0.70 and abs(c.y) < 0.45:
                tgt = "Hood"                                # konepellin reunasauma
            elif abs(c.y) > 0.80 and -1.25 < c.x < 0.85 and c.z < 0.95:
                tgt = "Side" + side                         # ovien saumat
            if tgt is None or not want(tgt):
                rest_s += fids
            else:
                P.setdefault(tgt, []).append(piece(S, fids))

    # ---- piiloon jaavat taytteet: moottoritila konepellin alla ja palkki etupuskurin takana
    bay = bmesh.new()
    NG = 9
    grid = []
    for iy in range(NG):
        y = -0.72 + 1.44 * iy / (NG - 1)
        x0 = 1.0 + 0.11 * (1 - (y / 0.80) ** 2) + 0.03
        x1 = min(hood_front_x(y), 2.085) - 0.04
        row = []
        for ix in range(NG):
            x = x0 + (x1 - x0) * ix / (NG - 1)
            loc, _ = surf.cast("top", x, y)
            row.append(bay.verts.new((x, y, (loc.z if loc is not None and loc.z < 1.0 else 0.9) - 0.04)))
        grid.append(row)
    for iy in range(NG - 1):
        for ix in range(NG - 1):
            bay.faces.new((grid[iy][ix], grid[iy][ix + 1], grid[iy + 1][ix + 1], grid[iy + 1][ix]))
    add_box(bay, (0.08, 1.56, 0.44), (1.86, 0, 0.50))
    P["Body"].append(bm_piece(bay, M["under"]))

    out = []
    def node(name, pieces, angle=40):
        if not any(pc["F"] for pc in pieces):
            print("VAROITUS: osa jai tyhjaksi:", name)
            return
        ob = bpy.data.objects.new(name, make_mesh(name, pieces, angle))
        col.objects.link(ob)
        out.append(ob)
    def strips(specs, mode, mat, only, sgn=1):
        bm = bmesh.new()
        for pts, w in specs:
            project_strip(bm, surf, pts, mode, sgn, width=w, lift=0.0025, mat=0, step=0.03, only=only)
        return bm_piece(bm, mat)

    # ---- vauriomuodot (auton koordinaatit: x eteen, y vasemmalle, z ylos)
    def hood_fn(level):
        dent, push, wr, ang, tw, shift = {1: (0.040, 0.0, 0.0, 0.0, 0.0, 0.0), 2: (0.065, 0.07, 0.022, 2.6, 1.2, 0.01),
                                          3: (0.075, 0.14, 0.040, 9.0, 3.0, 0.035)}[level]
        def fn(v):
            x, y, z = v
            t = math.hypot(x - 1.70, y - 0.34) / 0.32
            if t < 1:
                z -= dent * (1 - t * t) ** 2                                  # lommo
            wf = sm((x - 1.22) / 0.80)
            z += wr * wf * (sin(27 * (x - 1.2) + 2.6 * y) + 0.5 * sin(49 * x - 7 * y)) # rypyt
            x -= push * wf * wf
            y += shift * wf
            a = radians(ang + tw * y / 0.75)                                  # sarana takareunassa
            hz = T["cowl_z"]
            dx, dz = x - 1.02, z - hz
            return Vector((1.02 + dx * cos(a) - dz * sin(a), y, hz + dx * sin(a) + dz * cos(a)))
        return fn
    def bumper_f1(v):
        x, y, z = v
        w = sm((y - 0.27) / 0.5)
        z -= 0.035 * w
        x -= 0.025 * w
        t = (Vector((x, y, z)) - Vector((2.03, 0.60, 0.46))).length / 0.30
        if t < 1:
            k = (1 - t * t) ** 2
            x -= 0.075 * k
            y -= 0.02 * k
        return Vector((x, y, z))
    def bumper_f3(v):                                       # kiinni oikeasta paasta, vasen paa roikkuu
        v = bumper_f1(v)
        py, a, b = -0.80, radians(6.4), radians(7.0)
        dy = v.y - py
        return Vector((v.x + dy * sin(b) * 0.9, py + dy * cos(a), v.z - dy * sin(a) + 0.012 * sin(9 * v.y)))
    def bumper_r2(v):
        x, y, z = v
        w = sm((-y - 0.2) / 0.6)
        t = (Vector((x, y, z)) - Vector((-2.0, -0.62, 0.45))).length / 0.28
        k = (1 - t * t) ** 2 if t < 1 else 0.0
        return Vector((x - 0.03 * w + 0.05 * k, y + 0.015 * k, z - 0.065 * w))
    def fender_l2(v):
        x, y, z = v
        t = math.hypot(x - (AXLE_F + 0.18), z - 0.62) / 0.42
        k = (1 - t * t) ** 2 if t < 1 and y > 0.5 else 0.0
        return Vector((x - 0.03 * sm((x - AXLE_F - 0.18) / 0.3), y - 0.075 * k - 0.008 * k * sin(34 * z), z))
    def side_fn(dents):
        def fn(v):
            x, y, z = v
            sg = 1 if y > 0 else -1
            for cx, cz, r, d in dents:
                t = math.hypot(x - cx, z - cz) / r
                if t < 1:
                    k = (1 - t * t) ** 2
                    y -= sg * (d * k + 0.006 * k * sin(31 * x + 9 * z))
            return Vector((x, y, z))
        return fn
    lamp_in = lambda v: Vector((v.x - 0.012, v.y, v.z))
    broken = {"Headlight": M["lampbroken"], "Taillight": M["lampbroken"], "Glass": M["lampbroken"]}
    def lamp_cracks(sg):                                    # sarot rikkoutuneen ajovalon linssissa
        h = T["head_dz"]
        return deform(strips([([(0.56, 0.665 + h), (0.66, 0.700 + h), (0.74, 0.672 + h)], 0.005),
                              ([(0.62, 0.712 + h), (0.66, 0.700 + h), (0.69, 0.640 + h)], 0.004),
                              ([(0.72, 0.690 + h), (0.80, 0.705 + h)], 0.004)], "front", M["glasscracked"], (M_HEAD, M_GLASS, M_TRIM), sg), lamp_in)

    def cracks(impacts, long_cracks, seed):
        rng = __import__("random").Random(seed)
        specs = []
        for cx, cy, n, lmax in impacts:
            for k in range(n):
                a = 2 * pi * (k + rng.uniform(-0.3, 0.3)) / n
                L = rng.uniform(0.35, 1.0) * lmax
                pts, nseg = [(cx, cy)], rng.randint(3, 5)
                for j in range(1, nseg + 1):
                    r = L * j / nseg
                    a2 = a + rng.uniform(-0.22, 0.22)
                    pts.append((cx + r * cos(a2) * 0.8, cy + r * sin(a2)))
                specs.append((pts, rng.uniform(0.0035, 0.006)))
            for rr in (0.045, 0.10):
                a0 = rng.uniform(0, 6.28)
                ring = [(cx + rr * rng.uniform(0.85, 1.15) * cos(a0 + 0.6 * j) * 0.8, cy + rr * rng.uniform(0.85, 1.15) * sin(a0 + 0.6 * j))
                        for j in range(rng.randint(5, 9))]
                specs.append((ring, 0.004))
        for pts in long_cracks:
            specs.append((pts, 0.0045))
        return strips(specs, "top", M["glasscracked"], (M_GLASS,))
    def shatter(cx, cy, r, seed):                           # samea murskakohta iskukohdassa
        rng = __import__("random").Random(seed)
        bm = bmesh.new()
        ring = []
        for j in range(12):
            a = 2 * pi * j / 12
            rr = r * rng.uniform(0.7, 1.15)
            loc, nor = surf.cast("top", cx + rr * cos(a) * 0.8, cy + rr * sin(a))
            if loc is not None and surf.last_mat == M_GLASS:
                ring.append(bm.verts.new(loc + nor * 0.002))
        loc, nor = surf.cast("top", cx, cy)
        if loc is not None and len(ring) >= 3:
            c = bm.verts.new(loc + nor * 0.002)
            for a, b in zip(ring, ring[1:] + ring[:1]):
                bm.faces.new((c, a, b))
        return bm_piece(bm, M["glasscracked"])

    # ---- solmut portaittain
    node("Hood_d0", P["Hood"])
    for lv in (1, 2, 3):
        node("Hood_d%d" % lv, [deform(pc, hood_fn(lv)) for pc in P["Hood"]])
    scratch = []
    for sg in (1, -1):
        scratch.append(strips([([(0.50 + 0.04 * k, 0.40 + 0.03 * k), (0.78, 0.47 + 0.035 * k)], 0.008 + 0.003 * (k % 2)) for k in range(4)]
                              + [([(0.62, 0.30), (0.80, 0.36)], 0.012)], "front", M["baremetal"], (M_PAINT,), sg))
    node("BumperF_d0", P["BumperF"] + plate)
    node("BumperF_d1", [deform(pc, bumper_f1) for pc in P["BumperF"] + scratch] + plate)
    node("BumperF_d3", [deform(pc, bumper_f3) for pc in P["BumperF"] + scratch])
    node("Windshield_d0", P["Windshield"])
    node("Windshield_d2", P["Windshield"] + [cracks([(0.74, 0.30, 11, 0.30)], [], 3)])
    node("Windshield_d3", P["Windshield"] + [cracks([(0.74, 0.30, 15, 0.42), (0.58, -0.28, 12, 0.34)],
                                                    [[(0.95, -0.55), (0.80, -0.20), (0.72, 0.05), (0.60, 0.50)],
                                                     [(0.38, -0.50), (0.45, -0.10), (0.40, 0.30)]], 7),
                                             shatter(0.74, 0.30, 0.10, 1), shatter(0.58, -0.28, 0.075, 2)])
    for sd in "LR":
        node("Headlight%s_d0" % sd, P["Headlight" + sd])
    node("HeadlightL_d1", [remat(deform(pc, lamp_in, True), broken) for pc in P["HeadlightL"]] + [lamp_cracks(1)])
    node("HeadlightR_d3", [remat(deform(pc, lamp_in, True), broken) for pc in P["HeadlightR"]] + [lamp_cracks(-1)])
    if hi:
        node("BumperR_d0", P["BumperR"])
        node("BumperR_d2", [deform(pc, bumper_r2) for pc in P["BumperR"]])
        for sd in "LR":
            node("FenderF%s_d0" % sd, P["FenderF" + sd])
            node("Taillight%s_d0" % sd, P["Taillight" + sd])
            node("Mirror%s_d0" % sd, P["Mirror" + sd], 50)
            node("Side%s_d0" % sd, P["Side" + sd])
        node("FenderFL_d2", [deform(pc, fender_l2) for pc in P["FenderFL"]])
        node("MirrorL_d2", P.get("MirrorL_stub", []), 50)                     # peili irronnut, jalka jaljella
        node("TaillightR_d3", [remat(pc, broken) for pc in P["TaillightR"]])
        node("SideL_d3", [deform(pc, side_fn([(0.27, 0.56, 0.40, 0.065), (-0.70, 0.50, 0.33, 0.05)])) for pc in P["SideL"]])
        node("SideR_d3", [deform(pc, side_fn([(-0.05, 0.60, 0.46, 0.075), (-0.82, 0.48, 0.28, 0.04)])) for pc in P["SideR"]])
        if T["rear_doors"] and "RearDoorL" in P and "RearDoorR" in P:      # pakettiauton pariovet; oikea raollaan portaalla 3
            node("RearDoorL_d0", P["RearDoorL"])
            node("RearDoorR_d0", P["RearDoorR"])
            def door_ajar(v):
                a, xh, yh = radians(13.0), -2.06, -0.70
                dx, dy = v.x - xh, v.y - yh
                return Vector((xh + dx * cos(a) - dy * sin(a), yh + dx * sin(a) + dy * cos(a), v.z))
            node("RearDoorR_d3", [deform(pc, door_ajar) for pc in P["RearDoorR"]])

    # ---- alkuperaisiin solmuihin jaa vain se, mika ei vaurioidu
    for ob, pieces, angle in ((body, P["Body"], 40), (details, [piece(D, rest_d)], 50),
                              (seams, [piece(S, rest_s)] if S is not None else None, 40)):
        if ob is None:
            continue
        old = ob.data
        ob.data = make_mesh(ob.name, pieces, angle)
        bpy.data.meshes.remove(old)
    return out

def set_stage(n):
    """Nayttaa renderoinnissa portaan n osat samalla saannolla kuin peli."""
    best = {}
    for o in bpy.data.objects:
        if "_d" in o.name and o.name[-1].isdigit() and o.name[-3:-1] == "_d":
            base, lv = o.name[:-3], int(o.name[-1])
            if lv <= n and lv >= best.get(base, -1):
                best[base] = lv
    for o in bpy.data.objects:
        if o.name[-3:-1] == "_d" and o.name[-1].isdigit():
            o.hide_render = int(o.name[-1]) != best.get(o.name[:-3])
        elif o.name == "PlateText_front":
            o.hide_render = n >= 3                         # kilpi irtoaa etupuskurin mukana

# ----------------------------------------------------------------------------
# STUDIO (ei viedä peliin)
# ----------------------------------------------------------------------------
CAMS = {   # Blenderin koordinaatit (keula -Y)
    "front": ((3.9, -5.4, 1.75), (0.0, 0.1, 0.62), 50),
    "rear":  ((-3.8, 5.6, 1.9), (0.0, -0.1, 0.62), 50),
    "side":  ((7.5, 0.0, 1.0), (0.0, 0.0, 0.66), 50),
    "top":   ((0.01, -1.0, 11.0), (0.0, 0.0, 0.5), 35),
    "f":     ((0.0, -7.0, 1.0), (0.0, 0.0, 0.66), 50),
    "sticker": ((-1.5, 5.3, 2.35), (0.0, 1.75, 1.05), 50),
    "r":     ((0.0, 7.0, 1.0), (0.0, 0.0, 0.66), 50),
}

def build_studio(col, cam_name, samples, res):
    scn = bpy.context.scene
    me = bpy.data.meshes.new("Ground")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=400)
    bm.to_mesh(me); bm.free()
    g = bpy.data.objects.new("Ground", me)
    me.materials.append(make_mat("Asphalt", (0.11, 0.11, 0.115), rough=0.85))
    col.objects.link(g)

    sun = bpy.data.lights.new("Sun", 'SUN')
    sun.energy = 3.2
    sun.angle = radians(3)
    so = bpy.data.objects.new("Sun", sun)
    so.rotation_euler = (radians(52), 0, radians(38))
    col.objects.link(so)

    w = scn.world or bpy.data.worlds.new("World")
    scn.world = w
    if w.node_tree is None:
        w.use_nodes = True
    nt = w.node_tree
    bg = next((n for n in nt.nodes if n.type == 'BACKGROUND'), None)
    if bg is not None:                      # liukuvaritaivas (toimii kaikissa versioissa)
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
            e = cr.elements.new(pos)
            e.color = c
        nt.links.new(tc.outputs["Generated"], sep.inputs[0])
        nt.links.new(sep.outputs[2], mth.inputs[0])
        nt.links.new(mth.outputs[0], ramp.inputs[0])
        nt.links.new(ramp.outputs[0], bg.inputs[0])
        bg.inputs[1].default_value = 1.0

    cam = bpy.data.cameras.new("Camera")
    co = bpy.data.objects.new("Camera", cam)
    col.objects.link(co)
    loc, tgt, lens = CAMS.get(cam_name, CAMS["front"])
    co.location = loc
    co.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    cam.lens = lens
    scn.camera = co

    scn.render.engine = 'CYCLES'
    scn.cycles.samples = samples
    try:
        scn.cycles.use_denoising = True
    except Exception:
        pass
    scn.render.resolution_x = res
    scn.render.resolution_y = int(res * 9 / 16)
    scn.render.film_transparent = False

# ----------------------------------------------------------------------------
def main():
    args = parse_args()
    apply_type(args.type)
    hi = args.detail == "high"
    cands = [args.out, os.path.dirname(bpy.data.filepath) if bpy.data.filepath else None]
    try:
        cands.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        pass
    cands.append(os.path.expanduser("~"))
    out_dir = next(c for c in cands if c and (c == args.out or os.path.isdir(c)))
    os.makedirs(out_dir, exist_ok=True)
    name = args.name or (T["name"] + ("" if hi else "_low"))

    # tyhjenna scene
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    for blk in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights, bpy.data.curves):
        for d in list(blk):
            blk.remove(d)
    scn = bpy.context.scene
    car_col = bpy.data.collections.new("Auto")
    studio_col = bpy.data.collections.new("Studio")
    scn.collection.children.link(car_col)
    scn.collection.children.link(studio_col)

    M = make_materials(hi)
    body = build_body(M, car_col, level=2 if hi else 1, arch_segs=64 if hi else 20)
    surf = Surface(body)
    parts = [body]
    parts.append(build_details(M, car_col, surf, hi))
    if hi:
        parts += build_interior(M, car_col, body)
        parts += build_sticker(M, car_col, surf)
        parts.append(build_seams(M, car_col, surf))
        parts += build_plate_text(M, car_col, surf)
    parts += build_damage(M, car_col, surf, body, parts[1], next((o for o in parts if o.name == "Seams"), None), hi)
    wheels = []
    for nm, ax, left in (("Wheel_FL", AXLE_F, True), ("Wheel_FR", AXLE_F, False),
                         ("Wheel_RL", AXLE_R, True), ("Wheel_RR", AXLE_R, False)):
        w = build_wheel(nm, M, car_col, left, hi)
        w.location = (ax, (1 if left else -1) * TRACK / 2, WHEEL_R)
        wheels.append(w)
    # venytys todellisiin mittoihin (pyorat siirretaan, ei venyteta)
    bx = [v.co.x for v in body.data.vertices]
    all_x = [v.co.x for o in parts if o.name.startswith(("BumperF_d0", "BumperR_d0", "Body")) for v in o.data.vertices]
    all_z = [v.co.z for o in parts if o.name in ("Body", "Hood_d0") or o.name.startswith("RearDoor") for v in o.data.vertices]
    warp = Warp(max(all_x), min(all_x), max(all_z))
    for o in parts:
        warp.apply(o, rigid_z=(o.name == "Interior"))
    for w in wheels:
        w.location = (warp.X(w.location.x), w.location.y * warp.sy, WHEEL_R)
    print("MITAT: akselivali %.3f m, raidevali %.3f m, ohjauspyoran keskipiste (eteen %.3f, sivulle %.3f, ylos %.3f) m" % (
        warp.X(AXLE_F) - warp.X(AXLE_R), TRACK * warp.sy, warp.X(0.47), 0.37 * warp.sy, 0.92 + T["int_dz"]))

    # auton koordinaatit -> Blender (keula -Y), kaikki yhden juurisolmun alle
    root = bpy.data.objects.new("Car", None)
    root.empty_display_size = 0.5
    car_col.objects.link(root)
    for o in parts + wheels:
        loc = o.location.copy()
        o.data.transform(M_CONV)
        o.data.update()
        o.location = M_CONV @ loc
        o.parent = root
    bpy.context.view_layer.update()

    tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in parts + wheels)
    xs = [(o.matrix_world @ v.co) for o in parts + wheels if not (o.name[-3:-1] == "_d" and o.name[-1] in "123")
          for v in o.data.vertices]                      # ehjan auton ulkomitat (portaat 1-3 eivat mukana)
    dims = [max(v[n] for v in xs) - min(v[n] for v in xs) for n in range(3)]
    print("AUTO: %d kolmiota, leveys %.2f m, pituus %.2f m, korkeus %.2f m" % (tris, dims[0], dims[1], dims[2]))

    build_studio(studio_col, args.cam, args.samples, args.res)

    set_stage(0)                                           # .blend avautuu ehjana; GLB:ssa ovat kaikki portaat
    if EXPORT_GLB and not args.no_glb:
        try:
            bpy.ops.preferences.addon_enable(module="io_scene_gltf2")
        except Exception:
            pass
        for o in bpy.data.objects:
            o.select_set(o.name in car_col.objects)
        path = os.path.join(out_dir, name + ".glb")
        bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True,
                                  export_apply=True, export_yup=True)
        print("GLB:", path, "%.0f kt" % (os.path.getsize(path) / 1024))
    if SAVE_BLEND and not args.no_blend:
        path = os.path.join(out_dir, name + ".blend")
        bpy.ops.wm.save_as_mainfile(filepath=path)
        print("BLEND:", path)
    for shot in [x for x in args.shots.split(",") if x]:
        cam_name, stage = shot.split(":")
        set_stage(int(stage))
        loc, tgt, lens = CAMS[cam_name]
        loc, tgt = Vector(loc) * T["cam"], Vector((tgt[0], tgt[1], tgt[2] * T["cam"]))
        scn.camera.location = loc
        scn.camera.rotation_euler = (tgt - loc).to_track_quat('-Z', 'Y').to_euler()
        scn.camera.data.lens = lens
        path = os.path.join(out_dir, "%s_vaurio%s_%s.png" % (name, stage, cam_name))
        scn.render.filepath = path
        bpy.ops.render.render(write_still=True)
        print("RENDER:", path)
    if args.render:
        set_stage(0)
        path = os.path.join(out_dir, "%s_%s.png" % (name, args.cam))
        scn.render.filepath = path
        bpy.ops.render.render(write_still=True)
        print("RENDER:", path)

if __name__ == "__main__":
    main()
