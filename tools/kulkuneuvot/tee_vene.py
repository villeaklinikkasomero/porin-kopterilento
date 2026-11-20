# -*- coding: utf-8 -*-
"""Meshyn veneen kasittely peliin: kaanto (keula +Z kuten autoissa), skaalaus, kevennys tekstuurit sailyttaen, istuin- ja moottorimerkit."""
import sys, io, json, struct, argparse
import numpy as np, pymeshlab as ml
from PIL import Image
from gltf import GLB
ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out")
ap.add_argument("--pituus", type=float, default=4.8)
ap.add_argument("--keula", default="-x", help="mihin suuntaan keula osoittaa lahdemallissa")
ap.add_argument("--kolmiot", type=int, default=16000)
ap.add_argument("--korkeus", type=float, default=0, help="skaalaa korkeuden mukaan (pituuden sijaan)")
ap.add_argument("--perämoottori", dest="moottori", action="store_true", help="origo kiinnikkeeseen, ei istuinmerkkeja")
ap.add_argument("--nimi", default="Vene")
ap.add_argument("--tex", type=int, default=1024)
ap.add_argument("--tapa", default="yhd", help="yhd = saumat yhdistetaan (siistimpi, kevyempi), saumat = UV-saarten reunat lukitaan")
ap.add_argument("--uvpaino", type=float, default=8)
A = ap.parse_args()
G = GLB(A.src); j = G.j; pr = j["meshes"][0]["primitives"][0]
V = G.acc(pr["attributes"]["POSITION"]); UV = G.acc(pr["attributes"]["TEXCOORD_0"]); F = G.acc(pr["indices"]).astype(np.int64).reshape(-1, 3)
# kaanto: keula -> +Z
rot = {"-x": np.array([[0, 0, -1], [0, 1, 0], [1, 0, 0]]).T, "+x": np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]]).T, "+z": np.eye(3), "-z": np.diag([-1, 1, -1])}[A.keula]
# rot: sarakkeet; tarkistetaan suunta erikseen
def R(v):
    if A.keula == "-x": return np.c_[v[:, 2], v[:, 1], -v[:, 0]]
    if A.keula == "+x": return np.c_[-v[:, 2], v[:, 1], v[:, 0]]
    if A.keula == "-z": return np.c_[-v[:, 0], v[:, 1], -v[:, 2]]
    return v
V = R(V)
L = V[:, 2].max() - V[:, 2].min(); s = A.pituus / L
if A.korkeus: s = A.korkeus / (V[:, 1].max() - V[:, 1].min())
V = V * s; V[:, 1] -= V[:, 1].min(); V[:, 0] -= 0.5 * (V[:, 0].max() + V[:, 0].min()); V[:, 2] -= 0.5 * (V[:, 2].max() + V[:, 2].min())
if A.moottori:
    # kiinnike: etuosan ylaosa (C-puristin peraspeilin paalla); ohjaus kaantyy taman pisteen kautta
    up = (V[:, 1] > 0.55 * V[:, 1].max()) & (V[:, 1] < 0.8 * V[:, 1].max())
    zf = np.percentile(V[up, 2], 97)
    cl = up & (V[:, 2] > zf - 0.06)
    piv = np.array([0.0, np.percentile(V[cl, 1], 90), np.percentile(V[cl, 2], 30)])
    V = V - piv
    print("kiinnike (origo) siirretty, alaosa %.2f m origon alapuolella" % -V[:, 1].min())
print("mitat (m): leveys %.2f korkeus %.2f pituus %.2f" % tuple(V.max(0) - V.min(0)))
ms = ml.MeshSet()
m = ml.Mesh(vertex_matrix=V, face_matrix=F, v_tex_coords_matrix=UV)
ms.add_mesh(m)
ms.compute_texcoord_transfer_vertex_to_wedge()
# UV-saarten reunat sailyvat (ei yhdisteta saumoja), jolloin tekstuuri ei sotkeudu
if A.tapa == "saumat":
    ms.meshing_decimation_quadric_edge_collapse_with_texture(targetfacenum=A.kolmiot, qualitythr=0.5, extratcoordw=4, preserveboundary=True, boundaryweight=3, preservenormal=True, planarquadric=True)
else:
    ms.meshing_merge_close_vertices(threshold=ml.PercentageValue(0.001))
    ms.meshing_decimation_quadric_edge_collapse_with_texture(targetfacenum=A.kolmiot, qualitythr=0.5, extratcoordw=A.uvpaino, preserveboundary=False, preservenormal=True, planarquadric=True)
cm = ms.current_mesh()
Vd = cm.vertex_matrix(); Fd = cm.face_matrix(); W = cm.wedge_tex_coord_matrix().reshape(-1, 3, 2)
print("kolmioita", len(Fd))
# vertex per (pos, uv)
key = {}; P2 = []; T2 = []; F2 = np.zeros_like(Fd)
for fi in range(len(Fd)):
    for c in range(3):
        vi = Fd[fi, c]; uv = W[fi, c]
        k = (vi, round(float(uv[0]), 5), round(float(uv[1]), 5))
        if k not in key:
            key[k] = len(P2); P2.append(Vd[vi]); T2.append(uv)
        F2[fi, c] = key[k]
P2 = np.array(P2); T2 = np.array(T2)
# normaalit: pinnan normaalit painotettuina, terava kulma (>50 astetta) erottaa
fn = np.cross(P2[F2[:, 1]] - P2[F2[:, 0]], P2[F2[:, 2]] - P2[F2[:, 0]])
N = np.zeros_like(P2)
for c in range(3): np.add.at(N, F2[:, c], fn)
N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-12
# alkuperaiset sileat normaalit lahimmasta alkuperaisesta pisteesta (piilottaa kevennyksen ryppyja)
from scipy.spatial import cKDTree
N0 = R(G.acc(pr["attributes"]["NORMAL"]))
d0, i0 = cKDTree(V).query(P2, k=4)
Nt = (N0[i0] * (1 / (d0 + 1e-5))[..., None]).sum(1)
Nt /= np.linalg.norm(Nt, axis=1, keepdims=True) + 1e-12
ok = (Nt * N).sum(1) > 0.3
N[ok] = Nt[ok]
# tekstuurit
imgs = []
for im in j["images"]:
    imgs.append(Image.open(io.BytesIO(G.view(im["bufferView"]))).convert("RGB"))
base = imgs[j["textures"][j["materials"][0]["pbrMetallicRoughness"]["baseColorTexture"]["index"]]["source"]]
nrm = imgs[j["textures"][j["materials"][0]["normalTexture"]["index"]]["source"]]
# istuimet: tummanruskeat pisteet kannen ylapuolella
bw, bh = base.size; ba = np.asarray(base).astype(int)
px = np.clip((T2[:, 0] % 1) * bw, 0, bw - 1).astype(int); py = np.clip((T2[:, 1] % 1) * bh, 0, bh - 1).astype(int)
col = ba[py, px]
dark = (col.sum(1) < 200) & (not A.moottori) & (col[:, 0] > col[:, 2]) & (np.abs(P2[:, 0]) < 0.75)
merkit = {}
up = N[:, 1] > 0.7
if dark.sum() > 20:
    floor = np.percentile(P2[dark & up, 1], 10)
    seat = dark & up & (P2[:, 1] > floor + 0.15) & (P2[:, 1] < floor + 0.6)
    D = P2[seat]
    zf = np.percentile(D[:, 2], 55)
    for nm, cond in (("Istuin_kuljettaja", (D[:, 0] < -0.12) & (D[:, 2] > zf)), ("Istuin_matkustaja", (D[:, 0] > 0.12) & (D[:, 2] > zf))):
        Q = D[cond]
        if len(Q):
            merkit[nm] = [float(np.median(Q[:, 0])), float(np.percentile(Q[:, 1], 60)), float(np.median(Q[:, 2]))]
    if "Istuin_kuljettaja" in merkit and "Istuin_matkustaja" in merkit:
        a, b = merkit["Istuin_kuljettaja"], merkit["Istuin_matkustaja"]
        xm = 0.5 * (abs(a[0]) + abs(b[0])); ym = 0.5 * (a[1] + b[1]); zm = 0.5 * (a[2] + b[2])
        merkit["Istuin_kuljettaja"] = [-xm, ym, zm]; merkit["Istuin_matkustaja"] = [xm, ym, zm]
    Q = D[D[:, 2] < np.percentile(D[:, 2], 25)]
    if len(Q): merkit["Penkki_taka"] = [0.0, float(np.percentile(Q[:, 1], 60)), float(np.median(Q[:, 2]))]
    merkit["_lattia_y"] = float(floor)
st = P2[P2[:, 2] < P2[:, 2].min() + 0.05]
if not A.moottori: merkit["Moottori_kiinnitys"] = [0.0, float(np.percentile(st[:, 1], 80)), float(P2[:, 2].min())]
print("merkit", json.dumps(merkit))
# GLB
buf = bytearray(); views = []; accs = []
def view(data, target=None):
    while len(buf) % 4: buf.append(0)
    o = len(buf); buf.extend(data); v = {"buffer": 0, "byteOffset": o, "byteLength": len(data)}
    if target: v["target"] = target
    views.append(v); return len(views) - 1
def acc(arr, ct, typ, target=None, mm=False):
    arr = np.ascontiguousarray(arr); a = {"bufferView": view(arr.tobytes(), target), "componentType": ct, "count": int(arr.shape[0]), "type": typ}
    if mm: a["min"] = arr.min(0).tolist(); a["max"] = arr.max(0).tolist()
    accs.append(a); return len(accs) - 1
ap_ = acc(P2.astype(np.float32), 5126, "VEC3", 34962, True); an = acc(N.astype(np.float32), 5126, "VEC3", 34962)
at = acc(T2.astype(np.float32), 5126, "VEC2", 34962); ai = acc(F2.astype(np.uint32).ravel(), 5125, "SCALAR", 34963)
def jpg(img):
    img = img.resize((A.tex, A.tex), Image.LANCZOS) if max(img.size) > A.tex else img
    b = io.BytesIO(); img.save(b, "JPEG", quality=85); return b.getvalue()
iv0 = view(jpg(base)); iv1 = view(jpg(nrm))
nodes = [{"name": "Runko" if not A.moottori else "Moottori", "mesh": 0}]
for nm, p in merkit.items():
    if not nm.startswith("_"): nodes.append({"name": nm, "translation": p})
nodes.append({"name": A.nimi, "children": list(range(len(nodes)))})
gj = {"asset": {"version": "2.0", "generator": "porikopteri tee_vene.py"}, "scene": 0, "scenes": [{"nodes": [len(nodes) - 1]}], "nodes": nodes,
      "meshes": [{"name": "Runko", "primitives": [{"attributes": {"POSITION": ap_, "NORMAL": an, "TEXCOORD_0": at}, "indices": ai, "material": 0}]}],
      "materials": [{"name": A.nimi, "pbrMetallicRoughness": {"baseColorTexture": {"index": 0}, "metallicFactor": 0.0, "roughnessFactor": 0.45}, "normalTexture": {"index": 1}, "doubleSided": True}],
      "textures": [{"source": 0, "sampler": 0}, {"source": 1, "sampler": 0}], "samplers": [{"magFilter": 9729, "minFilter": 9987}],
      "images": [{"bufferView": iv0, "mimeType": "image/jpeg"}, {"bufferView": iv1, "mimeType": "image/jpeg"}],
      "accessors": accs, "bufferViews": views, "buffers": [{"byteLength": len(buf)}]}
js = json.dumps(gj, separators=(",", ":")).encode()
while len(js) % 4: js += b" "
while len(buf) % 4: buf.append(0)
open(A.out, "wb").write(struct.pack("<III", 0x46546C67, 2, 28 + len(js) + len(buf)) + struct.pack("<I", len(js)) + b"JSON" + js + struct.pack("<I", len(buf)) + b"BIN\x00" + bytes(buf))
print("kirjoitettu", A.out)
