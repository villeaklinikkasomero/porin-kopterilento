"""Skydiving jump plane – detailed game asset (Cessna-182-class high-wing single).

Conventions: metres, Y up, nose toward +Z, port (left) side = +X, ground y = 0.

Animated / gameplay nodes (pivot at the hinge / rotation centre):
  propeller            spin about local Z
  door                 starboard jump door, hinged at the top: rotate about local Z, negative = open (up under the wing)
  aileron_port/_stbd   rotate about local X (hinge line ~spanwise)
  flap_port/_stbd      rotate about local X (positive = down)
  elevator             rotate about local X
  rudder               rotate about local Y
  exit_point           empty – jumper on the step, facing forward, holding the strut
  pilot_seat           empty
  seat_00..seat_03     empties – jumpers on the floor, facing aft
"""
import math, os, random
import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.ndimage import gaussian_filter
from shapely.geometry import Polygon

LITE = os.environ.get("LITE") == "1"          # lighter mesh for touch devices (hyppykone_m)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out/") + ("lite/" if LITE else ""); os.makedirs(OUT, exist_ok=True)
random.seed(7); np.random.seed(7)
REG = "OH-HPX"                      # fictional registration
YEL = (232, 172, 22); GREY = (58, 60, 64); WHITE = (238, 238, 234)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
TM = trimesh.transformations


# =================================================================== materials
def pbr(name, rgb=None, metal=0.0, rough=0.5, tex=None, mr=None, nrm=None, alpha=1.0,
        blend=False, double=False, emissive=None):
    kw = dict(name=name, metallicFactor=metal, roughnessFactor=rough, doubleSided=double)
    if tex is not None: kw["baseColorTexture"] = tex
    else: kw["baseColorFactor"] = [*[c / 255 for c in rgb], alpha]
    if mr is not None: kw["metallicRoughnessTexture"] = mr; kw["metallicFactor"] = 1.0; kw["roughnessFactor"] = 1.0
    if nrm is not None: kw["normalTexture"] = nrm
    if blend: kw["alphaMode"] = "BLEND"
    if emissive is not None: kw["emissiveFactor"] = [c / 255 for c in emissive]
    return trimesh.visual.material.PBRMaterial(**kw)


M = {
    "glass":    pbr("glass", (150, 175, 190), 0.0, 0.03, alpha=0.18, blend=True, double=True),
    "lens":     pbr("light_lens", (235, 240, 245), 0.0, 0.05, alpha=0.45, blend=True, double=True),
    "interior": pbr("interior_wall", (118, 116, 110), 0.0, 0.9),
    "headliner":pbr("headliner", (190, 186, 176), 0.0, 0.95),
    "floor":    pbr("floor_carpet", (52, 54, 58), 0.0, 1.0),
    "pad":      pbr("jump_mat", (34, 48, 82), 0.0, 0.95),
    "seat":     pbr("seat_fabric", (44, 44, 48), 0.0, 0.92),
    "metal":    pbr("alu_bare", (190, 192, 196), 1.0, 0.30),
    "chrome":   pbr("chrome", (225, 225, 228), 1.0, 0.08),
    "dark":     pbr("dark_metal", (42, 42, 44), 0.7, 0.45),
    "black":    pbr("black_plastic", (18, 18, 19), 0.0, 0.55),
    "rubber":   pbr("tyre", (22, 22, 22), 0.0, 0.92),
    "prop":     pbr("prop_black", (17, 17, 17), 0.15, 0.55),
    "proptip":  pbr("prop_tip_yellow", (245, 190, 0), 0.0, 0.45),
    "spinner":  pbr("spinner_paint", WHITE, 0.0, 0.25),
    "white":    pbr("paint_white_plain", WHITE, 0.0, 0.32),
    "navred":   pbr("nav_red", (255, 40, 30), 0.0, 0.2, emissive=(255, 30, 20)),
    "navgrn":   pbr("nav_green", (40, 240, 80), 0.0, 0.2, emissive=(20, 220, 60)),
    "strobe":   pbr("strobe_white", (250, 250, 250), 0.0, 0.2, emissive=(160, 160, 160)),
    "beacon":   pbr("beacon_red", (255, 40, 30), 0.0, 0.2, emissive=(255, 30, 20)),
    "soot":     pbr("exhaust_soot", (30, 28, 26), 0.6, 0.7),
    "jumplight_r": pbr("jumplight_red", (255, 30, 20), 0.0, 0.3, emissive=(255, 20, 10)),
    "jumplight_g": pbr("jumplight_green", (40, 255, 80), 0.0, 0.3, emissive=(10, 120, 30)),
}


def mat(mesh, m, uv=None):
    mesh.visual = trimesh.visual.TextureVisuals(uv=uv, material=m)
    return mesh


def tex_pack(base, height, rough, metal=None, strength=3.0, size=None):
    """Return (baseColor, metallicRoughness, normal) PIL images. Inputs are float arrays."""
    gy, gx = np.gradient(gaussian_filter(height, 0.7))
    n = np.dstack([-gx * strength, gy * strength, np.ones_like(height)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    nimg = Image.fromarray(((n * 0.5 + 0.5) * 255).astype(np.uint8))
    mr = np.zeros(height.shape + (3,), np.uint8)
    mr[..., 1] = np.clip(rough * 255, 0, 255)
    mr[..., 2] = 0 if metal is None else np.clip(metal * 255, 0, 255)
    imgs = [Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)), Image.fromarray(mr), nimg]
    if size: imgs = [im.resize(size, Image.LANCZOS) for im in imgs]
    return imgs


def stamp_rivets(H, pts, r=1.6, h=0.6):
    """Add small dome bumps to height map H at pixel points."""
    for x, y in pts:
        x0, y0 = int(x), int(y)
        if 2 <= x0 < H.shape[1] - 3 and 2 <= y0 < H.shape[0] - 3:
            H[y0 - 2:y0 + 3, x0 - 2:x0 + 3] += h * RIV


_yy, _xx = np.mgrid[-2:3, -2:3]
RIV = np.clip(1 - (_xx ** 2 + _yy ** 2) / 5.0, 0, 1)


# =================================================================== fuselage shape
SE = 3.4
ST = np.array([
    [4.05, 0.40, 0.40, 1.25],
    [3.85, 0.80, 0.74, 1.22],
    [3.20, 1.00, 0.95, 1.25],
    [2.40, 1.10, 0.92, 1.24],
    [2.00, 1.13, 0.94, 1.25],
    [1.50, 1.18, 1.40, 1.48],
    [1.00, 1.18, 1.40, 1.48],
    [-1.00, 1.18, 1.40, 1.48],
    [-2.00, 0.95, 1.06, 1.58],
    [-3.60, 0.55, 0.62, 1.70],
    [-5.20, 0.20, 0.30, 1.83],
])[::-1]
ZMIN, ZMAX = ST[0, 0], ST[-1, 0]
NR = 48 if LITE else 96


def sect(z, inset=0.0):
    return (np.interp(z, ST[:, 0], ST[:, 1]) - 2 * inset,
            np.interp(z, ST[:, 0], ST[:, 2]) - 2 * inset,
            np.interp(z, ST[:, 0], ST[:, 3]))


def surf_y(z, x, top=True):
    """Height of the fuselage skin at (x, z)."""
    w, h, yc = sect(z)
    nx = min(abs(x) / (w / 2), 0.999)
    ny = (1 - nx ** SE) ** (1 / SE)
    return yc + (1 if top else -1) * h / 2 * ny


def surf_x(z, y):
    w, h, yc = sect(z)
    ny = min(abs(y - yc) / (h / 2), 0.999)
    return w / 2 * (1 - ny ** SE) ** (1 / SE)


def ring(z, inset=0.0):
    w, h, yc = sect(z, inset)
    t = np.linspace(0, 2 * np.pi, NR, endpoint=False)
    c, s = np.cos(t), np.sin(t)
    return np.c_[w / 2 * np.sign(c) * np.abs(c) ** (2 / SE), yc + h / 2 * np.sign(s) * np.abs(s) ** (2 / SE), np.full(NR, z)]


def loft(zs, inset=0.0):
    rings = [ring(z, inset) for z in zs]
    V = np.vstack(rings); F = []
    for i in range(len(zs) - 1):
        a, b = i * NR, (i + 1) * NR
        for j in range(NR):
            k = (j + 1) % NR
            F += [[a + j, b + j, b + k], [a + j, b + k, a + k]]
    c0 = len(V); V = np.vstack([V, rings[0].mean(0), rings[-1].mean(0)])
    last = (len(zs) - 1) * NR
    for j in range(NR):
        k = (j + 1) % NR
        F += [[c0, k, j], [c0 + 1, last + j, last + k]]
    m = trimesh.Trimesh(V, F, process=True); trimesh.repair.fix_normals(m)
    return m


def prism_zy(poly_zy, x0, x1):
    """Extrude a polygon given in (z, y) across x0..x1."""
    p = Polygon([(z, y) for z, y in poly_zy])
    m = trimesh.creation.extrude_polygon(p, x1 - x0)       # polygon in XY, extruded along +Z
    # map (px, py, pz) -> (x = x0 + pz, y = py, z = px)
    T = np.array([[0, 0, 1, x0], [0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1]], float)
    m.apply_transform(T); trimesh.repair.fix_normals(m)
    return m


_k = 2 if LITE else 1
zs_out = np.unique(np.r_[np.arange(ZMIN, 0.9, 0.10 * _k), np.arange(0.9, 2.2, 0.02 * _k), np.arange(2.2, ZMAX, 0.08 * _k), ZMAX].round(4))
outer = loft(zs_out)
inner = loft(np.arange(-2.2, 2.30, 0.05 * _k), inset=0.035)
fus = outer.difference(inner)

# ---- openings
DOOR_Z0, DOOR_Z1, DOOR_Y0, DOOR_Y1 = -0.80, 0.22, 0.93, 2.06
doorbox = trimesh.creation.box(bounds=[[-1.0, DOOR_Y0, DOOR_Z0], [-0.2, DOOR_Y1, DOOR_Z1]])
WS_X = 0.43
ws_prism = prism_zy([(1.995, 1.645), (1.46, 1.645), (1.46, 2.40), (1.995, 2.40)], -WS_X, WS_X)
SIDE_FRONT = [(1.72, 1.63), (1.47, 2.03), (0.36, 2.03), (0.36, 1.60)]
SIDE_MID = [(0.12, 2.03), (-0.70, 2.03), (-0.70, 1.60), (0.12, 1.60)]
SIDE_REAR = [(-0.90, 2.03), (-1.62, 1.98), (-1.86, 1.76), (-0.90, 1.60)]
cutters = [ws_prism]
for sx in (1, -1):
    xa, xb = (0.40, 1.0) if sx > 0 else (-1.0, -0.40)
    cutters.append(prism_zy(SIDE_FRONT, xa, xb))
    cutters.append(prism_zy(SIDE_REAR, xa, xb))
    if sx > 0: cutters.append(prism_zy(SIDE_MID, xa, xb))       # port middle window (stbd one is in the door)
door_win = prism_zy(SIDE_MID, -1.0, -0.40)

door_panel = outer.intersection(doorbox).difference(inner).difference(door_win)
fus = fus.difference(doorbox)
glass_src = []
for c in cutters + [door_win]:
    glass_src.append(outer.intersection(c))
    fus = fus.difference(c)
print("fuselage volume ok:", fus.is_volume)


# =================================================================== fuselage textures
TW, TH = 8192, 4096          # drawn at 2x then reduced to 4096x2048
YR = (0.4, 2.4)
PXM = TW / (ZMAX - ZMIN)     # pixels per metre along z (draw scale)


def livery_side(port):
    Wd, Hd = TW, TH // 2
    base = Image.new("RGB", (Wd, Hd), WHITE); d = ImageDraw.Draw(base)
    Hm = Image.new("L", (Wd, Hd), 128); dh = ImageDraw.Draw(Hm)          # height map
    G = Image.new("L", (Wd, Hd), 0); dg = ImageDraw.Draw(G)              # grime mask
    def X(z): f = (z - ZMIN) / (ZMAX - ZMIN); return (1 - f) * Wd if port else f * Wd
    def Y(y): return (1 - (y - YR[0]) / (YR[1] - YR[0])) * Hd
    sc = Hd / (YR[1] - YR[0])
    # -- cheat lines
    def band(y_nose, y_tail, th, col):
        zz = np.linspace(ZMIN - .2, ZMAX + .2, 120)
        f = np.clip((zz - ZMIN) / (ZMAX - ZMIN), 0, 1)
        yy = y_tail + (y_nose - y_tail) * f ** 0.8
        pts = [(X(z), Y(y + th / 2)) for z, y in zip(zz, yy)] + [(X(z), Y(y - th / 2)) for z, y in zip(zz[::-1], yy[::-1])]
        d.polygon(pts, fill=col)
    band(1.12, 1.70, 0.10, YEL); band(1.02, 1.62, 0.035, GREY); band(1.21, 1.78, 0.02, GREY)
    # -- panel seams (grooves) – vertical frames
    frames = [3.86, 3.25, 2.40, 1.47, 0.30, -0.85, -2.0, -2.9, -3.8, -4.6]
    for z in frames:
        dh.line([(X(z), 0), (X(z), Hd)], fill=96, width=5)
    # cowling split line & access doors
    dh.line([(X(3.86), Y(1.25)), (X(2.40), Y(1.25))], fill=96, width=5)
    dh.rounded_rectangle([min(X(3.55), X(2.85)), Y(1.62), max(X(3.55), X(2.85)), Y(1.42)], 10, outline=92, width=5)
    # horizontal stringer lap joints
    for y in (1.05, 1.42, 1.78):
        dh.line([(X(2.40), Y(y)), (X(-4.8), Y(y + 0.10 * 0))], fill=110, width=3)
    # rivet rows along frames and laps
    pts = []
    step = 0.035 * PXM
    for z in frames[2:]:
        for y in np.arange(0.7, 2.2, 0.035):
            pts.append((X(z) + (9 if port else -9), Y(y)))
    for y in (1.05, 1.42, 1.78):
        for z in np.arange(-4.8, 2.40, 0.035):
            pts.append((X(z), Y(y) - 8))
    Ha = np.asarray(Hm).astype(np.float32)
    stamp = np.zeros_like(Ha)
    _riv = np.clip(1 - (np.mgrid[-4:5, -4:5] ** 2).sum(0) / 18.0, 0, 1)
    for x, y in pts:
        x0, y0 = int(x), int(y)
        if 4 <= x0 < Wd - 5 and 4 <= y0 < Hd - 5:
            stamp[y0 - 4:y0 + 5, x0 - 4:x0 + 5] = np.maximum(stamp[y0 - 4:y0 + 5, x0 - 4:x0 + 5], _riv)
    Ha += stamp * 26
    # door outline on stbd + door handle recess
    if not port:
        d.rectangle([min(X(DOOR_Z1), X(DOOR_Z0)), Y(DOOR_Y1), max(X(DOOR_Z1), X(DOOR_Z0)), Y(DOOR_Y0)], outline=(80, 80, 80), width=6)
    # -- registration
    f = ImageFont.truetype(FONT, int(0.30 * sc))
    tw = d.textlength(REG, font=f)
    d.text((X(-3.15) - tw / 2, Y(1.99)), REG, fill=(28, 28, 32), font=f)
    # -- small stencils
    fs = ImageFont.truetype(FONT_R, int(0.035 * sc))
    d.text((X(2.2) - 60, Y(1.12)), "OIL", fill=(80, 80, 80), font=fs)
    d.text((X(-4.4) - 140, Y(1.52)), "NO PUSH", fill=(90, 90, 90), font=fs)
    if not port:
        d.text((X(-0.05) - 120, Y(1.08)), "JUMP DOOR", fill=(150, 30, 30), font=ImageFont.truetype(FONT, int(0.04 * sc)))
    # -- grime: exhaust soot along the lower aft fuselage (exhaust exits low, port side of centre)
    soot = np.zeros((Hd, Wd), np.float32)
    zz = np.linspace(2.55, -3.5, 400)
    for z in zz:
        fade = np.clip((z + 3.5) / 6.0, 0, 1)
        yc_ = 0.82 + (2.55 - z) * 0.06
        r = (0.06 + (2.55 - z) * 0.035) * sc
        x0 = X(z); y0 = Y(yc_)
        yy0, yy1 = int(max(0, y0 - r)), int(min(Hd, y0 + r))
        xx0 = int(max(0, x0 - 6)); xx1 = int(min(Wd, x0 + 6))
        soot[yy0:yy1, xx0:xx1] = np.maximum(soot[yy0:yy1, xx0:xx1], 0.65 * fade * (1.0 if port else 0.45))
    soot = gaussian_filter(soot, 18)
    # oil streaks behind the cowling bottom
    streak = np.zeros_like(soot)
    for _ in range(25):
        z0 = random.uniform(2.3, 2.45); y0 = random.uniform(0.85, 1.15); ln = random.uniform(0.3, 1.6)
        x_a, x_b = sorted([X(z0), X(z0 - ln)])
        streak[int(Y(y0)) - 3:int(Y(y0)) + 3, int(x_a):int(x_b)] += random.uniform(0.05, 0.15)
    streak = gaussian_filter(streak, 4)
    # panel-line dirt
    seams = gaussian_filter((128 - np.asarray(Hm).astype(np.float32)).clip(0) / 32, 3)
    # general low-frequency dirt, more on the belly
    yy = np.linspace(1, 0, Hd)[:, None]
    lowf = gaussian_filter(np.random.rand(Hd // 16, Wd // 16).astype(np.float32), 2)
    lowf = np.asarray(Image.fromarray(lowf).resize((Wd, Hd), Image.BICUBIC))
    dirt = (0.10 * lowf + 0.25 * np.clip(0.45 - yy * 0.9 + 0.3, 0, 1) * lowf)
    B = np.asarray(base).astype(np.float32)
    B *= (1 - 0.55 * soot - 0.6 * streak - 0.10 * seams - 0.18 * dirt)[..., None]
    B[..., 0] -= 6 * dirt; B[..., 2] -= 10 * dirt               # slightly warm grime
    B += np.random.normal(0, 1.5, B.shape[:2])[..., None]
    rough = 0.30 + 0.35 * soot + 0.25 * dirt + 0.2 * streak + 0.05 * gaussian_filter(np.random.rand(Hd, Wd).astype(np.float32), 1)
    Ha = Ha - 30 * (128 - np.asarray(Hm).astype(np.float32) < -1)
    return B, Ha / 255.0, rough


parts_tex = [livery_side(True), livery_side(False)]
B = np.vstack([parts_tex[0][0], parts_tex[1][0]])
Hh = np.vstack([parts_tex[0][1], parts_tex[1][1]])
R = np.vstack([parts_tex[0][2], parts_tex[1][2]])
fus_base, fus_mr, fus_n = tex_pack(B, Hh, R, None, strength=6.0, size=(TW // 2, TH // 2))
for nm, im in (("base", fus_base), ("mr", fus_mr), ("normal", fus_n)): im.save(OUT + f"tex_fuselage_{nm}.png")
M["livery"] = pbr("fuselage_paint", tex=fus_base, mr=fus_mr, nrm=fus_n)


def livery_uv(v, n):
    f = (v[:, 2] - ZMIN) / (ZMAX - ZMIN)
    hv = np.clip((v[:, 1] - YR[0]) / (YR[1] - YR[0]), 0, 1)
    port = n[:, 0] >= 0
    return np.c_[np.where(port, 1 - f, f), np.where(port, 0.5 + 0.5 * hv, 0.5 * hv)]


def unweld(m):
    return trimesh.Trimesh(m.vertices[m.faces].reshape(-1, 3), np.arange(len(m.faces) * 3).reshape(-1, 3), process=False)


def outer_mask(m, tol=0.985):
    fc = m.triangles_center
    w, h, yc = sect(fc[:, 2])
    nx = np.abs(fc[:, 0]) / (w / 2); ny = np.abs(fc[:, 1] - yc) / (h / 2)
    return ((nx ** SE + ny ** SE) ** (1 / SE) > tol) | (fc[:, 2] > 3.75)


def split_fuselage(m):
    is_out = outer_mask(m)
    fc = m.triangles_center
    out = {}
    for key, sel in (("skin", is_out), ("interior", ~is_out)):
        idx = np.nonzero(sel)[0]
        sub = unweld(m.submesh([idx], append=True))
        if key == "skin":
            mat(sub, M["livery"], livery_uv(sub.vertices, np.repeat(m.face_normals[idx], 3, axis=0)))
        else:
            # headliner above window line, wall below
            mat(sub, M["interior"])
        out[key] = sub
    return out


# =================================================================== airfoils & lofting
def naca_pts(code, x):
    mm, p, t = int(code[0]) / 100, int(code[1]) / 10, int(code[2:]) / 100
    yt = 5 * t * (0.2969 * np.sqrt(x) - 0.126 * x - 0.3516 * x**2 + 0.2843 * x**3 - 0.1036 * x**4)
    if p > 0:
        yc = np.where(x < p, mm / p**2 * (2 * p * x - x**2), mm / (1 - p)**2 * ((1 - 2 * p) + 2 * p * x - x**2))
    else:
        yc = 0 * x
    return yc + yt, yc - yt


def naca_part(code, x0=0.0, x1=1.0, n=40):
    """Closed loop of the airfoil between chord fractions x0..x1 (upper x1->x0, lower x0->x1)."""
    t = (1 - np.cos(np.linspace(0, np.pi, n))) / 2
    x = x0 + (x1 - x0) * t
    up, lo = naca_pts(code, x)
    if x0 == 0.0:
        return np.vstack([np.c_[x[::-1], up[::-1]], np.c_[x[1:], lo[1:]]])
    # trailing part: front face is a rounded nose (control-surface leading edge)
    k = np.linspace(0, np.pi, 9)[1:-1]
    yu, yl = up[0], lo[0]; ym, rr = (yu + yl) / 2, (yu - yl) / 2
    nose = np.c_[x0 - 0.6 * rr * np.sin(k) / max(1, 1), ym + rr * np.cos(k)]
    return np.vstack([np.c_[x[::-1], up[::-1]], nose, np.c_[x, lo]])


def naca(code="2412", n=40):
    return naca_part(code, 0.0, 1.0, n)


def surface(sections, cap=True):
    n = len(sections[0]); V = np.vstack(sections); F = []
    for i in range(len(sections) - 1):
        a, b = i * n, (i + 1) * n
        for j in range(n):
            k = (j + 1) % n
            F += [[a + j, b + j, b + k], [a + j, b + k, a + k]]
    if cap:
        for s_i, flip in ((0, True), (len(sections) - 1, False)):
            c = len(V); V = np.vstack([V, sections[s_i].mean(0)]); base = s_i * n
            for j in range(n):
                k = (j + 1) % n
                F.append([c, base + k, base + j] if flip else [c, base + j, base + k])
    m = trimesh.Trimesh(V, F, process=True); trimesh.repair.fix_normals(m)
    return m


def sec_h(af, chord, le_z, y, x):          # horizontal surface section at span x
    return np.c_[np.full(len(af), x), y + af[:, 1] * chord, le_z - af[:, 0] * chord]


def sec_v(af, chord, le_z, y):             # vertical surface section at height y
    return np.c_[af[:, 1] * chord, np.full(len(af), y), le_z - af[:, 0] * chord]


def tube(p0, p1, r, m, sections=20, flat=1.0, roll=0.0):
    p0, p1 = np.array(p0, float), np.array(p1, float)
    L = np.linalg.norm(p1 - p0)
    c = trimesh.creation.cylinder(radius=r, height=L, sections=sections)
    c.apply_scale([1, flat, 1])
    if roll: c.apply_transform(TM.rotation_matrix(roll, [0, 0, 1]))
    c.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], (p1 - p0) / L))
    c.apply_translation((p0 + p1) / 2)
    return mat(c, m)


def box(b0, b1, m):
    return mat(trimesh.creation.box(bounds=[b0, b1]), m)


def rbox(b0, b1, m, r=0.02):
    """Rounded box (approx.) via scaled capsule-ish superquadric."""
    b0, b1 = np.array(b0, float), np.array(b1, float)
    s = trimesh.creation.icosphere(3, radius=1.0)
    v = s.vertices
    v = np.sign(v) * np.abs(v) ** 0.35                       # squarish
    s.vertices = v * (b1 - b0) / 2 + (b1 + b0) / 2
    return mat(s, m)


def disc(center, normal, r, h, m, sections=28):
    c = trimesh.creation.cylinder(radius=r, height=h, sections=sections)
    c.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], np.array(normal, float)))
    c.apply_translation(center)
    return mat(c, m)


def revolve(prof, seg=48, axis="z"):
    V = []; F = []
    for zr in prof:
        for k in range(seg):
            a = 2 * np.pi * k / seg
            V.append([zr[1] * math.cos(a), zr[1] * math.sin(a), zr[0]])
    for i_ in range(len(prof) - 1):
        for k in range(seg):
            a, b = i_ * seg + k, i_ * seg + (k + 1) % seg
            F += [[a, a + seg, b + seg], [a, b + seg, b]]
    for end in (0, len(prof) - 1):
        if prof[end][1] > 1e-4:
            c = len(V); V.append([0, 0, prof[end][0]])
            for k in range(seg):
                a, b = end * seg + k, end * seg + (k + 1) % seg
                F.append([c, b, a] if end == 0 else [c, a, b])
    m = trimesh.Trimesh(np.array(V), F, process=True); trimesh.repair.fix_normals(m)
    if axis == "x": m.apply_transform(TM.rotation_matrix(math.pi / 2, [0, 1, 0]))
    return m


# =================================================================== wing & tail textures (planar UV)
def surface_tex(Wd, Hd, u_of, v_of, ribs_u, spars_v, extra=None, stripe=None, name="wing"):
    """Generic painted-aluminium texture with ribs (rivet rows) & spars, grime."""
    Wd2, Hd2 = Wd * 2, Hd * 2
    base = Image.new("RGB", (Wd2, Hd2), WHITE); d = ImageDraw.Draw(base)
    Hm = np.full((Hd2, Wd2), 0.5, np.float32)
    if stripe:
        for (v0, v1, col) in stripe: d.rectangle([0, v0 * Hd2, Wd2, v1 * Hd2], fill=col)
    _riv = np.clip(1 - (np.mgrid[-3:4, -3:4] ** 2).sum(0) / 10.0, 0, 1)
    def rivet(x, y):
        x0, y0 = int(x), int(y)
        if 3 <= x0 < Wd2 - 4 and 3 <= y0 < Hd2 - 4:
            Hm[y0 - 3:y0 + 4, x0 - 3:x0 + 4] = np.maximum(Hm[y0 - 3:y0 + 4, x0 - 3:x0 + 4], 0.5 + 0.12 * _riv)
    for u in ribs_u:
        x = u * Wd2
        for y in np.arange(0, Hd2, 14): rivet(x, y)
    for v in spars_v:
        y = v * Hd2
        Hm[int(y) - 2:int(y) + 2, :] -= 0.10
        for x in np.arange(0, Wd2, 14): rivet(x, y + 9)
    if extra: extra(d, Hm, Wd2, Hd2)
    lowf = gaussian_filter(np.random.rand(Hd2 // 16, Wd2 // 16).astype(np.float32), 1.5)
    lowf = np.asarray(Image.fromarray(lowf).resize((Wd2, Hd2), Image.BICUBIC))
    seams = gaussian_filter(np.clip(0.5 - Hm, 0, 1) * 6, 3)
    B = np.asarray(base).astype(np.float32) * (1 - 0.10 * lowf - 0.15 * seams)[..., None]
    rough = 0.32 + 0.18 * lowf + 0.2 * seams
    imgs = tex_pack(B, Hm, rough, None, strength=10.0, size=(Wd, Hd))
    for nm, im in zip(("base", "mr", "normal"), imgs): im.save(OUT + f"tex_{name}_{nm}.png")
    return pbr(f"{name}_paint", tex=imgs[0], mr=imgs[1], nrm=imgs[2])


# wing: u = (x + HS) / 2HS (span), v = (z - (LE-1.7)) / 1.75 (chord)
WY = 2.17; DIH = math.radians(1.7); HS = 5.5
WZ0, WZ1 = -0.35, 1.50


def wing_uv(v):
    return np.c_[(v[:, 0] + HS) / (2 * HS), (v[:, 2] - WZ0) / (WZ1 - WZ0)]


def _wing_extra(d, Hm, W2, H2):
    # leading-edge de-icing-ish darker abrasion strip & "NO STEP" near flaps
    pass


ribs = [(HS + s * x) / (2 * HS) for s in (1, -1) for x in np.arange(0.7, HS, 0.33)]
M["wingpaint"] = surface_tex(2048, 512, None, None, ribs, [(1.45 - 0.30 * 1.62 - WZ0) / (WZ1 - WZ0), (1.45 - 0.72 * 1.62 - WZ0) / (WZ1 - WZ0)],
                             extra=_wing_extra, name="wing")

# tail: horizontal (top projection) and vertical (side projection)
HZ0, HZ1 = -5.6, -4.0
def htail_uv(v): return np.c_[(v[:, 0] + 2.0) / 4.0, (v[:, 2] - HZ0) / (HZ1 - HZ0)]
M["htailpaint"] = surface_tex(1024, 512, None, None, [(2.0 + s * x) / 4 for s in (1, -1) for x in np.arange(0.3, 1.8, 0.3)], [0.55], name="htail")
VY0, VY1 = 1.8, 2.95
def vtail_uv(v):
    port = v[:, 0] >= 0
    u = (v[:, 2] - HZ0 - 0.4) / (HZ1 - HZ0 + 0.8)
    return np.c_[np.where(port, 1 - u, u), (v[:, 1] - VY0) / (VY1 - VY0)]
M["vtailpaint"] = surface_tex(1024, 512, None, None, [], [0.3, 0.55],
                              stripe=[(1 - (2.67 - VY0) / (VY1 - VY0), 1 - (2.58 - VY0) / (VY1 - VY0), YEL),
                                      (1 - (2.705 - VY0) / (VY1 - VY0), 1 - (2.685 - VY0) / (VY1 - VY0), GREY)], name="vtail")


# =================================================================== assemble parts
parts = []          # (name, mesh, parent)
def add(name, m, parent="jump_plane"): parts.append((name, m, parent))

for k, v in split_fuselage(fus).items(): add(f"fuselage_{k}", v)

# glass panes = outer-skin faces of the cut pieces, pulled 4 mm inward
for i, g in enumerate(glass_src):
    if len(g.faces) == 0: continue
    sel = np.nonzero(outer_mask(g, 0.99))[0]
    if len(sel) == 0: continue
    pane = unweld(g.submesh([sel], append=True))
    nrm = np.repeat(g.face_normals[sel], 3, axis=0)
    pane.vertices = pane.vertices - nrm * 0.004
    nm = "windshield" if i == 0 else ("door_window" if i == len(glass_src) - 1 else f"window_{i:02d}")
    if nm == "door_window": DOOR_GLASS = mat(pane, M["glass"])
    else: add(nm, mat(pane, M["glass"]))

DOOR_MESH = unweld(door_panel)
DOOR_SKIN = outer_mask(door_panel)
mat(DOOR_MESH, M["livery"], livery_uv(DOOR_MESH.vertices, np.repeat(door_panel.face_normals, 3, axis=0)))

# ---- windshield frame & A-pillars (aluminium retaining strips)
def follow_edge(zs, x):
    return [np.array([x, surf_y(z, x) + 0.004, z]) for z in zs]
for sx in (1, -1):
    pts = follow_edge(np.linspace(1.99, 1.46, 14), sx * (WS_X + 0.006))
    for i in range(len(pts) - 1):
        add(f"a_pillar_{'port' if sx > 0 else 'stbd'}_{i:02d}", tube(pts[i], pts[i + 1], 0.016, M["metal"], 10, flat=0.45))
# bottom retaining strip across the cowl deck
xs_ = np.linspace(-WS_X, WS_X, 16)
zb = 1.995 - 0.0
pts = [np.array([x, max(1.645, surf_y(1.99, x)) + 0.004, 1.99 - 0.0]) for x in xs_]
for i in range(len(pts) - 1): add(f"ws_bottom_strip_{i:02d}", tube(pts[i], pts[i + 1], 0.014, M["metal"], 10, flat=0.5))
# side window frames (thin dark rubber seals)
def frame_poly(poly, x_side, name):
    loop = poly + [poly[0]]
    for i in range(len(loop) - 1):
        (z0, y0), (z1, y1) = loop[i], loop[i + 1]
        n = max(2, int(math.hypot(z1 - z0, y1 - y0) / 0.08))
        for t in range(n):
            za, ya = z0 + (z1 - z0) * t / n, y0 + (y1 - y0) * t / n
            zb_, yb = z0 + (z1 - z0) * (t + 1) / n, y0 + (y1 - y0) * (t + 1) / n
            pa = [np.sign(x_side) * surf_x(za, ya) + 0.002 * np.sign(x_side), ya, za]
            pb = [np.sign(x_side) * surf_x(zb_, yb) + 0.002 * np.sign(x_side), yb, zb_]
            add(f"{name}_{i}_{t}", tube(pa, pb, 0.009, M["black"], 8))
for sx in (1, -1):
    s_ = "port" if sx > 0 else "stbd"
    frame_poly(SIDE_FRONT, sx, f"seal_front_{s_}")
    frame_poly(SIDE_REAR, sx, f"seal_rear_{s_}")
    if sx > 0: frame_poly(SIDE_MID, sx, f"seal_mid_{s_}")

# ---- wing (front box 0..0.74c, control surfaces 0.755..1c)
AFW = "2412"
def wing_y(x): return WY + abs(x) * math.tan(DIH)
def wchord(x):
    f = max(0.0, (abs(x) - 2.5) / (HS - 2.5)); return 1.62 + (1.12 - 1.62) * f, 1.45 - 0.08 * f
HINGE = 0.74
front = naca_part(AFW, 0.0, HINGE, 34)
aft = naca_part(AFW, HINGE + 0.012, 1.0, 14)
def wsec(x, af=front):
    ch, le = wchord(x); return sec_h(af, ch, le, wing_y(x), x)
def wsec_tip(sx, k):
    x = sx * (HS * 0.97 + HS * 0.05 * k)
    p = sec_h(naca(AFW, 34), *wchord(x), wing_y(x), x)
    c = p.mean(0); sc = np.array([1, 1 - 0.75 * k ** 2, 1 - 0.25 * k ** 2])
    return (p - c) * sc + c
xs = list(np.r_[np.linspace(-HS * 0.97, -2.5, 9), np.linspace(-2.2, 2.2, 7), np.linspace(2.5, HS * 0.97, 9)])
wing = surface([wsec(x) for x in xs])
add("wing_main", mat(wing, M["wingpaint"], wing_uv(wing.vertices)))
# fixed trailing pieces: centre (over the cabin) and outboard of the ailerons
def aft_piece(xa, xb, n=4):
    m = surface([wsec(x, aft) for x in np.linspace(xa, xb, n)]); return mat(m, M["wingpaint"], wing_uv(m.vertices))
add("wing_te_centre", aft_piece(-0.60, 0.60))
for sx in (1, -1):
    s_ = "port" if sx > 0 else "stbd"
    tip = surface([wsec_tip(sx, 0.0)] + [wsec_tip(sx, k) for k in (0.3, 0.55, 0.75, 0.9, 1.0)])
    add(f"wingtip_{s_}", mat(tip, M["wingpaint"], wing_uv(tip.vertices)))
    add(f"wing_te_tip_{s_}", aft_piece(sx * 5.26, sx * HS * 0.97, 3))
    # nav + strobe lights in a small tip pod
    nl = trimesh.creation.icosphere(2, radius=0.03); nl.apply_scale([0.8, 0.8, 1.6]); nl.apply_translation([sx * (HS + 0.005), wing_y(HS) + 0.02, 1.30])
    add(f"navlight_{s_}", mat(nl, M["navred"] if sx > 0 else M["navgrn"]))
    st = trimesh.creation.icosphere(2, radius=0.022); st.apply_translation([sx * (HS + 0.005), wing_y(HS) + 0.02, 0.35])
    add(f"strobe_{s_}", mat(st, M["strobe"]))
    # strut: streamlined, with fairing cuffs
    p_f, p_w = np.array([sx * 0.56, 0.98, 0.55]), np.array([sx * 2.70, wing_y(2.7) - 0.03, 0.80])
    add(f"strut_{s_}", tube(p_f, p_w, 0.055, M["white"], 24, flat=0.32, roll=0.25 * sx))
    add(f"strut_cuff_top_{s_}", tube(p_w - (p_w - p_f) * 0.06, p_w, 0.065, M["white"], 24, flat=0.4, roll=0.25 * sx))
    add(f"strut_cuff_bot_{s_}", tube(p_f, p_f + (p_w - p_f) * 0.05, 0.07, M["white"], 24, flat=0.45, roll=0.25 * sx))
    # fuel cap (flush, chrome) on top of the wing
    ch, le = wchord(sx * 1.1); xc = (le - 1.12) / ch
    up, _ = naca_pts(AFW, np.array([xc]))
    add(f"fuel_cap_{s_}", disc([sx * 1.1, wing_y(1.1) + up[0] * ch + 0.002, 1.12], [0, 1, 0.08], 0.045, 0.008, M["chrome"]))
    # tie-down ring under the wing
    tr = trimesh.creation.torus(0.035, 0.007, major_sections=24, minor_sections=8)
    tr.apply_transform(TM.rotation_matrix(math.pi / 2, [0, 1, 0])); tr.apply_translation([sx * 2.9, wing_y(2.9) - 0.10, 0.75])
    add(f"tiedown_{s_}", mat(tr, M["metal"]))

# control surfaces as separate pivoting nodes
CS = {}
def cs_node(name, mesh, pivot):
    mesh.apply_translation(-np.array(pivot)); CS[name] = (mesh, np.array(pivot))
for sx in (1, -1):
    s_ = "port" if sx > 0 else "stbd"
    for nm, xa, xb in (("flap", 0.62, 2.95), ("aileron", 2.98, 5.24)):
        a, b = sx * xa, sx * xb
        m = surface([wsec(x, aft) for x in np.linspace(a, b, 6)]); mat(m, M["wingpaint"], wing_uv(m.vertices))
        xm = (a + b) / 2; ch, le = wchord(xm)
        pivot = [xm, wing_y(xm), le - (HINGE + 0.012) * ch]
        cs_node(f"{nm}_{s_}", m, pivot)
        if nm == "aileron":    # static wicks on the trailing edge
            for xw in np.linspace(a, b, 3)[1:]:
                chw, lew = wchord(xw)
                p0 = np.array([xw, wing_y(xw), lew - chw]); CS[f"{nm}_{s_}"] = CS[f"{nm}_{s_}"]
                parts.append((f"static_wick_{s_}_{xw:+.2f}", tube(p0 - pivot, p0 - pivot + [0, 0, -0.10], 0.003, M["black"], 6), f"{nm}_{s_}"))

# landing / taxi lights in port wing leading edge
for i, xl in enumerate((1.85, 2.05)):
    ch, le = wchord(xl)
    add(f"landing_light_lens_{i}", disc([xl, wing_y(xl) + 0.02 * ch, le + 0.004], [0, 0, 1], 0.055, 0.012, M["lens"]))
    add(f"landing_light_reflector_{i}", disc([xl, wing_y(xl) + 0.02 * ch, le - 0.010], [0, 0, 1], 0.05, 0.010, M["chrome"]))
# pitot tube under port wing
add("pitot_mast", tube([2.35, wing_y(2.35) - 0.03, 1.20], [2.35, wing_y(2.35) - 0.14, 1.28], 0.012, M["metal"], 10, flat=0.5))
add("pitot_tube", tube([2.35, wing_y(2.35) - 0.14, 1.20], [2.35, wing_y(2.35) - 0.14, 1.55], 0.009, M["chrome"], 12))
# stall warning vane slot (port LE)
add("stall_vane", box([1.40, wing_y(1.4) - 0.01, 1.448], [1.44, wing_y(1.4) + 0.01, 1.462], M["metal"]))

# ---- tail (moved aft with the stretched cabin)
TZ = -0.60
afs_f = naca_part("0012", 0.0, 0.70, 26); afs_a = naca_part("0012", 0.715, 1.0, 12); afs_full = naca("0012", 26)
def hsec(x, af):
    f = abs(x) / 1.75; ch = 1.12 + (0.78 - 1.12) * f; le = -3.55 - 0.30 * f + TZ
    return sec_h(af, ch, le, 1.74 + abs(x) * 0.02, x), ch, le
hx = np.linspace(-1.75, 1.75, 9)
stab = surface([hsec(x, afs_f)[0] for x in hx]); add("stabilizer", mat(stab, M["htailpaint"], htail_uv(stab.vertices)))
for sx in (1, -1):
    tipm = surface([hsec(sx * 1.75, afs_full)[0], hsec(sx * 1.80, afs_full)[0] * [1, 1, 1]])
    p = hsec(sx * 1.82, afs_full)[0]; c = p.mean(0); p = (p - c) * [1, 0.3, 0.8] + c
    tipm = surface([hsec(sx * 1.75, afs_full)[0], p]); add(f"stab_tip_{'port' if sx > 0 else 'stbd'}", mat(tipm, M["htailpaint"], htail_uv(tipm.vertices)))
el_parts = []
for sx in (1, -1):
    m = surface([hsec(x, afs_a)[0] for x in np.linspace(sx * 0.10, sx * 1.75, 6)]); mat(m, M["htailpaint"], htail_uv(m.vertices))
    el_parts.append(m)
_, ch0, le0 = hsec(0.0, afs_a)
EL_PIVOT = np.array([0.0, 1.74, le0 - 0.715 * ch0])
for m in el_parts: m.apply_translation(-EL_PIVOT)

def fsec(y, af):
    f = (y - 1.92) / (2.85 - 1.92); ch = 1.70 + (0.85 - 1.70) * f; le = -3.05 + (-4.45 + 3.05) * f + TZ
    return sec_v(af, ch, le, y), ch, le
fy = np.linspace(1.92, 2.85, 8)
fin = surface([fsec(y, afs_f)[0] for y in fy]); add("fin", mat(fin, M["vtailpaint"], vtail_uv(fin.vertices)))
fintip_p = fsec(2.85, afs_full)[0]; c = fintip_p.mean(0)
fintip = surface([fsec(2.85, afs_full)[0], (fintip_p - c) * [0.5, 1, 0.97] + c + [0, 0.04, 0]])
add("fin_tip", mat(fintip, M["vtailpaint"], vtail_uv(fintip.vertices)))
rud = surface([fsec(y, afs_a)[0] for y in np.linspace(1.80, 2.85, 7)]); mat(rud, M["vtailpaint"], vtail_uv(rud.vertices))
_, chm, lem = fsec(2.35, afs_a)
RU_PIVOT = np.array([0.0, 2.35, lem - 0.715 * chm]); rud.apply_translation(-RU_PIVOT)
dors = surface([sec_v(afs_full, 0.10, -1.6 + TZ, 2.09), sec_v(afs_full, 1.30, -2.0 + TZ, 2.07), sec_v(afs_full, 0.10, -3.2 + TZ, 2.15)])
add("dorsal_fin", mat(dors, M["vtailpaint"], vtail_uv(dors.vertices)))
bc = revolve([(0, 0.035), (0.03, 0.035), (0.06, 0.025), (0.075, 0.0)], 24); bc.apply_transform(TM.rotation_matrix(-math.pi / 2, [1, 0, 0]))
bc.apply_translation([0, 2.88, -5.38]); add("beacon", mat(bc, M["beacon"]))
tail_tr = trimesh.creation.torus(0.03, 0.007, major_sections=20, minor_sections=8); tail_tr.apply_transform(TM.rotation_matrix(math.pi / 2, [0, 1, 0]))
tail_tr.apply_translation([0, surf_y(-4.6, 0, top=False) - 0.04, -4.6]); add("tail_tiedown", mat(tail_tr, M["metal"]))
add("tail_tiedown_mount", tube([0, surf_y(-4.6, 0, top=False) + 0.01, -4.6], [0, surf_y(-4.6, 0, top=False) - 0.012, -4.6], 0.008, M["metal"], 8))

# ---- antennas
roof = lambda z: surf_y(z, 0)
add("com1_antenna", tube([0, roof(-1.25), -1.25], [0, roof(-1.25) + 0.42, -1.62], 0.006, M["black"], 8))
add("com1_base", disc([0, roof(-1.25), -1.25], [0, 1, 0], 0.025, 0.012, M["black"]))
add("com2_antenna", tube([0, roof(-1.85), -1.85], [0, roof(-1.85) + 0.38, -2.20], 0.006, M["black"], 8))
add("com2_base", disc([0, roof(-1.85), -1.85], [0, 1, 0], 0.025, 0.012, M["black"]))
blade = trimesh.creation.box(extents=[0.012, 0.14, 0.18]); blade.apply_transform(TM.rotation_matrix(math.radians(-25), [1, 0, 0]))
blade.apply_translation([0, surf_y(-1.5, 0, top=False) - 0.065, -1.5]); add("transponder_blade", mat(blade, M["black"]))
add("elt_antenna", tube([0, roof(-2.6), -2.6], [0, roof(-2.6) + 0.30, -2.75], 0.004, M["black"], 6))

# ---- engine: spinner, prop, cowl inlets, exhaust, oil cooler
PROP_HUB = np.array([0.0, 1.25, 4.05]); PROP_R = 1.0
def blade_mesh(r0, r1, n=22):
    secs = []
    for t in np.linspace(0, 1, n):
        r = r0 + (r1 - r0) * t; u = r / PROP_R
        chord = np.interp(u, [0.17, 0.25, 0.45, 0.75, 0.93, 0.985, 1.0], [0.065, 0.11, 0.135, 0.115, 0.085, 0.05, 0.015])
        thick = np.interp(u, [0.17, 0.3, 1.0], [2.6, 1.2, 0.7])
        pitch = math.radians(np.interp(u, [0.17, 0.4, 1.0], [42, 28, 13]))
        p = naca("4412", 22).copy(); p[:, 0] -= 0.30; p *= chord; p[:, 1] *= thick
        if u < 0.24:
            k = (0.24 - u) / 0.07
            ang = np.linspace(0, 2 * np.pi, len(p), endpoint=False)
            p = p * (1 - k) + np.c_[np.cos(ang) * 0.028, np.sin(ang) * 0.028] * k
        secs.append(np.c_[p[:, 0] * math.cos(pitch) - p[:, 1] * math.sin(pitch), np.full(len(p), r),
                          p[:, 0] * math.sin(pitch) + p[:, 1] * math.cos(pitch)])
    return surface(secs)
prop_parts = [mat(revolve([(0.0, 0.205), (0.06, 0.20), (0.14, 0.175), (0.24, 0.125), (0.33, 0.065), (0.39, 0.018), (0.40, 0.0)], 48), M["spinner"])]
prop_parts.append(mat(revolve([(-0.03, 0.21), (0.0, 0.21)], 48), M["metal"]))           # bulkhead ring
for i in range(2):
    Rm = TM.rotation_matrix(math.pi * i + 0.4, [0, 0, 1])
    b = blade_mesh(0.10, 0.90); b.apply_transform(Rm); prop_parts.append(mat(b, M["prop"]))
    t = blade_mesh(0.90, PROP_R, 8); t.apply_transform(Rm); prop_parts.append(mat(t, M["proptip"]))
for sx in (1, -1):
    # round cowl inlets either side of the spinner: dark recess + lip
    c = np.array([sx * 0.27, 1.20, 3.90])
    add(f"cowl_inlet_{'port' if sx > 0 else 'stbd'}", disc(c, [sx * 0.15, 0.1, 1], 0.075, 0.03, M["black"]))
    lip = trimesh.creation.torus(0.075, 0.012, major_sections=28, minor_sections=8)
    lip.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], [sx * 0.15, 0.1, 1])); lip.apply_translation(c + [0, 0, 0.012])
    add(f"cowl_inlet_lip_{'port' if sx > 0 else 'stbd'}", mat(lip, M["livery"].copy() if False else M["white"]))
add("exhaust_pipe", tube([0.18, 0.78, 2.75], [0.20, 0.70, 2.45], 0.032, M["dark"], 16))
add("exhaust_tip", tube([0.20, 0.70, 2.45], [0.205, 0.695, 2.40], 0.036, M["soot"], 16))
add("cowl_flap_port", box([0.08, 0.765, 2.36], [0.36, 0.778, 2.50], M["white"]))
add("cowl_flap_stbd", box([-0.36, 0.765, 2.36], [-0.08, 0.778, 2.50], M["white"]))
add("nose_landing_light", disc([0.0, 1.03, 3.93], [0, -0.3, 1], 0.04, 0.01, M["lens"]))

# ---- landing gear
def pant(center):
    p = trimesh.creation.icosphere(4, radius=1.0)
    v = p.vertices.copy(); v[:, 2] = np.where(v[:, 2] < 0, v[:, 2] * 1.25, v[:, 2])   # tapered tail
    p.vertices = v; p.apply_scale([0.11, 0.17, 0.40])
    p.apply_translation([center[0], center[1] + 0.07, center[2] - 0.02]); return mat(p, M["white"])
def wheel_set(c, r, w, tag):
    tyre = revolve([(-w / 2, r * 0.62), (-w / 2, r * 0.85), (-w * 0.42, r * 0.97), (0, r), (w * 0.42, r * 0.97), (w / 2, r * 0.85), (w / 2, r * 0.62)], 48)
    tyre.apply_transform(TM.rotation_matrix(math.pi / 2, [0, 1, 0])); tyre.apply_translation(c)
    hub = revolve([(-w * 0.52, 0.0), (-w * 0.52, r * 0.62), (w * 0.52, r * 0.62), (w * 0.52, 0.0)], 32)
    hub.apply_transform(TM.rotation_matrix(math.pi / 2, [0, 1, 0])); hub.apply_translation(c)
    out = [(f"{tag}_tyre", mat(tyre, M["rubber"])), (f"{tag}_hub", mat(hub, M["metal"]))]
    return out
add("nose_oleo_upper", tube([0, 0.86, 2.88], [0, 0.42, 2.98], 0.040, M["chrome"], 20))
add("nose_oleo_lower", tube([0, 0.50, 2.97], [0, 0.20, 3.05], 0.030, M["metal"], 20))
add("nose_fork", box([-0.07, 0.17, 2.98], [0.07, 0.30, 3.12], M["dark"]))
add("nose_shimmy_damper", tube([0.06, 0.62, 2.90], [0.06, 0.48, 3.02], 0.015, M["dark"], 10))
for n_, m_ in wheel_set([0, 0.18, 3.05], 0.18, 0.11, "nose_wheel"): add(n_, m_)
add("nosegear_pant", pant([0, 0.18, 3.05]))
for sx in (1, -1):
    s_ = "port" if sx > 0 else "stbd"
    leg_top, leg_bot = [sx * 0.42, 0.82, 0.46], [sx * 1.14, 0.22, 0.40]
    add(f"maingear_leg_{s_}", tube(leg_top, leg_bot, 0.05, M["white"], 20, flat=0.38))
    add(f"maingear_leg_fairing_{s_}", tube(leg_top, np.array(leg_top) + (np.array(leg_bot) - leg_top) * 0.25, 0.06, M["white"], 20, flat=0.45))
    for n_, m_ in wheel_set([sx * 1.22, 0.20, 0.40], 0.20, 0.12, f"main_wheel_{s_}"): add(n_, m_)
    add(f"brake_disc_{s_}", disc([sx * 1.135, 0.20, 0.40], [1, 0, 0], 0.11, 0.008, M["metal"]))
    add(f"brake_caliper_{s_}", box([sx * 1.12 - 0.02, 0.24, 0.30], [sx * 1.12 + 0.02, 0.31, 0.38], M["dark"]))
    add(f"maingear_pant_{s_}", pant([sx * 1.22, 0.20, 0.40]))

# ---- jump hardware (starboard)
add("jump_step_plate", box([-0.99, 0.565, 0.18], [-0.69, 0.585, 0.52], M["metal"]))
for z in np.arange(0.21, 0.51, 0.04):
    add(f"jump_step_tread_{z:+.2f}", box([-0.985, 0.585, z], [-0.695, 0.592, z + 0.012], M["dark"]))
add("jump_step_brace", tube([-0.84, 0.575, 0.36], [-0.95, 0.40, 0.42], 0.018, M["metal"], 12))
_sx = surf_x(-0.3, 2.08)
add("grab_handle", tube([-_sx - 0.045, 2.08, -0.65], [-_sx - 0.045, 2.08, 0.05], 0.013, M["chrome"], 14))
for z in (-0.65, 0.05): add(f"grab_mount_{z:+.2f}", tube([-_sx + 0.01, 2.08, z], [-_sx - 0.05, 2.08, z], 0.011, M["chrome"], 10))
xh = surf_x(-0.3, DOOR_Y1)
add("door_piano_hinge", tube([-xh - 0.008, DOOR_Y1 + 0.005, DOOR_Z0 + 0.03], [-xh - 0.008, DOOR_Y1 + 0.005, DOOR_Z1 - 0.03], 0.009, M["metal"], 10))
# jump lights inside above the door
add("jumplight_box", box([-0.42, 2.00, 0.25], [-0.34, 2.06, 0.40], M["black"]))
add("jumplight_red", disc([-0.38, 1.995, 0.29], [0, -1, 0], 0.016, 0.006, M["jumplight_r"]))
add("jumplight_green", disc([-0.38, 1.995, 0.36], [0, -1, 0], 0.016, 0.006, M["jumplight_g"]))

# ---- interior
FLOOR_Y = 0.92
add("cabin_floor", box([-0.40, 0.89, -1.05], [0.40, FLOOR_Y, 1.62], M["floor"]))
add("jump_mat", rbox([-0.38, FLOOR_Y - 0.005, -1.03], [0.38, FLOOR_Y + 0.035, 0.88], M["pad"]))
for z in (-0.5, 0.2):        # floor tie-down rings / seat belts anchors
    for sx in (1, -1):
        add(f"belt_anchor_{z:+.1f}_{sx}", disc([sx * 0.30, FLOOR_Y + 0.04, z], [0, 1, 0], 0.02, 0.01, M["metal"]))
# pilot seat
add("pilot_seat_cushion", rbox([0.06, FLOOR_Y + 0.22, 0.95], [0.46, FLOOR_Y + 0.34, 1.42], M["seat"]))
add("pilot_seat_back", rbox([0.06, FLOOR_Y + 0.34, 0.87], [0.46, FLOOR_Y + 0.98, 0.98], M["seat"]))
add("pilot_seat_headrest", rbox([0.14, FLOOR_Y + 0.98, 0.88], [0.38, FLOOR_Y + 1.14, 0.97], M["seat"]))
add("pilot_seat_frame", box([0.10, FLOOR_Y, 1.0], [0.42, FLOOR_Y + 0.22, 1.36], M["dark"]))
for sx_ in (0.10, 0.42): add(f"seat_rail_{sx_}", box([sx_ - 0.015, FLOOR_Y, 0.8], [sx_ + 0.015, FLOOR_Y + 0.02, 1.55], M["metal"]))
# instrument panel with a gauge texture
PW, PH = 1.0, 0.38
pi_ = Image.new("RGB", (1024, 390), (30, 31, 33)); dp = ImageDraw.Draw(pi_)
for row in range(2):
    for col in range(3):
        cx, cy = 140 + col * 120, 90 + row * 140
        dp.ellipse([cx - 52, cy - 52, cx + 52, cy + 52], fill=(8, 8, 9), outline=(150, 150, 150), width=4)
        for a in range(0, 360, 30):
            ra = math.radians(a); dp.line([(cx + 40 * math.cos(ra), cy + 40 * math.sin(ra)), (cx + 48 * math.cos(ra), cy + 48 * math.sin(ra))], fill=(230, 230, 230), width=3)
        a = math.radians(random.uniform(0, 360)); dp.line([(cx, cy), (cx + 40 * math.cos(a), cy + 40 * math.sin(a))], fill=(250, 250, 250), width=4)
dp.rectangle([520, 40, 760, 200], fill=(10, 14, 20), outline=(90, 90, 90), width=4)      # GPS/radio stack
for k in range(4): dp.rectangle([800, 40 + k * 60, 990, 90 + k * 60], fill=(18, 18, 18), outline=(80, 80, 80), width=3)
dp.text((535, 60), "COM 118.300", fill=(80, 230, 120), font=ImageFont.truetype(FONT, 26))
dp.text((535, 110), "ALT 13500", fill=(80, 230, 120), font=ImageFont.truetype(FONT, 26))
M["panel"] = pbr("instrument_panel", tex=pi_, rough=0.6)
pq = trimesh.Trimesh([[PW / 2, 0, 0], [-PW / 2, 0, 0], [-PW / 2, PH, 0], [PW / 2, PH, 0]], [[0, 1, 2], [0, 2, 3]], process=False)
pq.apply_translation([0, 1.24, 1.695]); add("instrument_panel_face", mat(pq, M["panel"], np.array([[0, 0], [1, 0], [1, 1], [0, 1]], float)))
add("instrument_panel_body", box([-0.50, 1.24, 1.70], [0.50, 1.62, 1.82], M["black"]))
add("glareshield", rbox([-0.42, 1.60, 1.62], [0.42, 1.68, 1.80], M["black"]))
# yoke (T-shaped), throttle quadrant, pedals
MOVE = {}      # cockpit controls that the game moves: name -> (meshes in node frame, pivot)
YOKE_P = np.array([0.25, 1.36, 1.68])
_y = [tube([0.25, 1.36, 1.68], [0.25, 1.36, 1.40], 0.014, M["chrome"], 12), tube([0.10, 1.39, 1.46], [0.40, 1.39, 1.46], 0.018, M["black"], 12),
      tube([0.25, 1.36, 1.46], [0.25, 1.39, 1.46], 0.03, M["black"], 12)]
for xg in (0.10, 0.40): _y.append(tube([xg, 1.28, 1.46], [xg, 1.43, 1.46], 0.021, M["black"], 12))
_y.append(disc([0.25, 1.39, 1.452], [0, 0, 1], 0.03, 0.006, M["chrome"]))
MOVE["yoke"] = (_y, YOKE_P)                       # slides aft (pull) along +z... game: position.z, rotation.z for roll
for k, (nm, col) in enumerate((("throttle_knob", (20, 20, 20)), ("prop_knob", (30, 60, 160)), ("mixture_knob", (170, 25, 25)))):
    x = -0.03 + k * 0.06; piv = np.array([x, 1.27, 1.675])
    knob = trimesh.creation.icosphere(2, radius=0.019); knob.apply_scale([1, 1, 0.8]); knob.apply_translation([x, 1.27, 1.60])
    if k == 1:   # prop knob: ribbed (a short cylinder)
        knob = trimesh.creation.cylinder(radius=0.018, height=0.024, sections=12); knob.apply_translation([x, 1.27, 1.60])
    if k == 2:   # mixture: red with a ridged rim
        knob = trimesh.creation.cylinder(radius=0.017, height=0.018, sections=10); knob.apply_translation([x, 1.27, 1.60])
    MOVE[nm] = ([mat(knob, pbr(f"knob_{nm}", col, 0.0, 0.4)), tube([x, 1.27, 1.675], [x, 1.27, 1.605], 0.004, M["chrome"], 6)], piv)
add("throttle_quadrant_plate", box([-0.08, 1.235, 1.672], [0.13, 1.305, 1.68], M["black"]))
for xp in (0.15, 0.35):
    add(f"rudder_pedal_{xp}", rbox([xp - 0.05, 0.98, 1.95], [xp + 0.05, 1.16, 1.99], M["dark"]))
# headliner panel & side wall trim
add("headliner_panel", box([-0.30, 2.10, -1.0], [0.30, 2.115, 1.42], M["headliner"]))

# =================================================================== scene graph
scene = trimesh.Scene()
root = "jump_plane"
scene.graph.update(frame_from="world", frame_to=root, matrix=np.eye(4))
def node(name, pos, parent=root):
    scene.graph.update(frame_from=parent, frame_to=name, matrix=TM.translation_matrix(pos))
node("propeller", PROP_HUB)
for i, m in enumerate(prop_parts): scene.add_geometry(m, node_name=f"propeller_part{i}", geom_name=f"propeller_part{i}", parent_node_name="propeller")
door_pivot = np.array([-surf_x((DOOR_Z0 + DOOR_Z1) / 2, DOOR_Y1) - 0.01, DOOR_Y1, (DOOR_Z0 + DOOR_Z1) / 2])   # top hinge (opens up under the wing)
node("door", door_pivot)
DOOR_MESH.apply_translation(-door_pivot); DOOR_GLASS.apply_translation(-door_pivot)
scene.add_geometry(DOOR_MESH, node_name="door_skin", geom_name="door_skin", parent_node_name="door")
scene.add_geometry(DOOR_GLASS, node_name="door_glass", geom_name="door_glass", parent_node_name="door")
dh = tube([-surf_x(-0.6, 1.5) - 0.025, 1.50, -0.68], [-surf_x(-0.6, 1.5) - 0.025, 1.50, -0.55], 0.010, M["chrome"], 10); dh.apply_translation(-door_pivot)
scene.add_geometry(dh, node_name="door_handle", geom_name="door_handle", parent_node_name="door")
for nm, (m, piv) in CS.items():
    node(nm, piv); scene.add_geometry(m, node_name=f"{nm}_mesh", geom_name=f"{nm}_mesh", parent_node_name=nm)
node("elevator", EL_PIVOT)
for i, m in enumerate(el_parts): scene.add_geometry(m, node_name=f"elevator_mesh{i}", geom_name=f"elevator_mesh{i}", parent_node_name="elevator")
node("rudder", RU_PIVOT)
for nm, (meshes, piv) in MOVE.items():
    node(nm, piv)
    for i, m in enumerate(meshes):
        m.apply_translation(-piv); scene.add_geometry(m, node_name=f"{nm}_part{i}", geom_name=f"{nm}_part{i}", parent_node_name=nm)
scene.add_geometry(rud, node_name="rudder_mesh", geom_name="rudder_mesh", parent_node_name="rudder")
for name, m, parent in parts:
    scene.add_geometry(m, node_name=name, geom_name=name, parent_node_name=parent)

def empty(name, pos, yaw_deg=0.0):
    T = TM.rotation_matrix(math.radians(yaw_deg), [0, 1, 0]); T[:3, 3] = pos
    scene.graph.update(frame_from=root, frame_to=name, matrix=T)
empty("exit_point", [-0.84, 0.59, 0.36])
empty("pilot_seat", [0.26, FLOOR_Y + 0.36, 1.15])
for n_, p_ in (("seat_00", [-0.20, FLOOR_Y + 0.04, 0.70]), ("seat_01", [-0.20, FLOOR_Y + 0.04, -0.25]),
               ("seat_02", [0.20, FLOOR_Y + 0.04, 0.25]), ("seat_03", [0.05, FLOOR_Y + 0.04, -0.85])):
    empty(n_, p_, yaw_deg=180)


def smooth_normals(m, ang=38):
    F = m.faces; P = m.vertices[F].reshape(-1, 3)
    fn = m.face_normals; area = m.area_faces
    cf = np.repeat(np.arange(len(F)), 3)
    key = np.round(P / 2e-4).astype(np.int64)
    _, inv = np.unique(key, axis=0, return_inverse=True)
    inv = inv.ravel(); order = np.argsort(inv, kind="stable"); cos = math.cos(math.radians(ang))
    N = np.zeros_like(P)
    bounds = np.r_[0, np.nonzero(np.diff(inv[order]))[0] + 1, len(order)]
    for a, b in zip(bounds[:-1], bounds[1:]):
        idx = order[a:b]
        if len(idx) == 1: N[idx] = fn[cf[idx]]; continue
        fns = fn[cf[idx]]; w = area[cf[idx]][:, None] + 1e-12
        N[idx] = ((fns @ fns.T) >= cos).astype(float) @ (fns * w)
    N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-12
    uv = None
    if getattr(m.visual, "uv", None) is not None and len(m.visual.uv) == len(m.vertices):
        uv = m.visual.uv[F].reshape(-1, 2)
    out = trimesh.Trimesh(P, np.arange(len(P)).reshape(-1, 3), process=False)
    out.visual = trimesh.visual.TextureVisuals(uv=uv, material=m.visual.material)
    out.vertex_normals = N
    return out


def merge(meshes, name):
    V, F, U, N, off = [], [], [], [], 0
    has_uv = all(getattr(m.visual, "uv", None) is not None for m in meshes)
    for m in meshes:
        V.append(m.vertices); F.append(m.faces + off); N.append(m.vertex_normals); off += len(m.vertices)
        if has_uv: U.append(m.visual.uv)
    out = trimesh.Trimesh(np.vstack(V), np.vstack(F), process=False)
    out.visual = trimesh.visual.TextureVisuals(uv=np.vstack(U) if has_uv else None, material=meshes[0].visual.material)
    out.vertex_normals = np.vstack(N)
    return out

for gname in list(scene.geometry):
    scene.geometry[gname] = smooth_normals(scene.geometry[gname])
# group root-level static meshes by material
groups = {}
for nname in list(scene.graph.nodes_geometry):
    if scene.graph.transforms.parents.get(nname) != root: continue
    T, g = scene.graph[nname]
    mesh = scene.geometry[g]
    groups.setdefault(mesh.visual.material.name, []).append((nname, g))
final = trimesh.Scene()
final.graph.update(frame_from="world", frame_to=root, matrix=np.eye(4))
keep_nodes = set()
for mname, lst in groups.items():
    nm = "static_" + mname
    final.add_geometry(merge([scene.geometry[g] for _, g in lst], nm), node_name=nm, geom_name=nm, parent_node_name=root)
# copy animated sub-trees & empties as-is
for nname in scene.graph.nodes:
    if nname in ("world", root): continue
    par = scene.graph.transforms.parents.get(nname)
    if par == root and nname in scene.graph.nodes_geometry: continue
    T = scene.graph.get(nname, par)[0] if par else np.eye(4)
    g = scene.graph.transforms.node_data[nname].get("geometry")
    if g is not None:
        final.add_geometry(scene.geometry[g], node_name=nname, geom_name=g, parent_node_name=par, transform=T)
    else:
        final.graph.update(frame_from=par, frame_to=nname, matrix=T)
def weld(m):
    uv = getattr(m.visual, "uv", None)
    N = m.vertex_normals
    key = np.c_[np.round(m.vertices / 1e-5), np.round(N / 1e-3)] if uv is None else np.c_[np.round(m.vertices / 1e-5), np.round(N / 1e-3), np.round(uv / 1e-5)]
    _, idx, inv = np.unique(key.astype(np.int64), axis=0, return_index=True, return_inverse=True)
    out = trimesh.Trimesh(m.vertices[idx], inv.ravel()[m.faces], process=False)
    out.visual = trimesh.visual.TextureVisuals(uv=None if uv is None else uv[idx], material=m.visual.material)
    out.vertex_normals = N[idx]
    return out
for g in list(final.geometry):
    final.geometry[g] = weld(final.geometry[g])
scene = final
scene.export(OUT + "hyppykone.glb", include_normals=True)
print("meshes:", len(scene.geometry), "tris:", sum(len(g.faces) for g in scene.geometry.values()))
