# -*- coding: utf-8 -*-
"""
Liittaa pelin 53 luun luurangon ja NPC-animaatiot kuvasta tehtyyn (Meshy) malliin.
python rigaa.py <meshy.glb> <ulos.glb> [--lahde npc_mies_a.glb] [--run hahmo.glb]
"""
import sys, json, struct, argparse
import numpy as np
from scipy.spatial import cKDTree
from gltf import GLB, q2m, m2q, trs, rot_between

ap = argparse.ArgumentParser()
ap.add_argument("meshy"); ap.add_argument("out")
ap.add_argument("--lahde", default="npc_mies_a.glb")
ap.add_argument("--lisaklipit", default="hahmo.glb:Run")
ap.add_argument("--k", type=int, default=6)
ap.add_argument("--debug", action="store_true")
ap.add_argument("--tex", type=int, default=1024)
ap.add_argument("--nimi", default="Hahmo")
ap.add_argument("--hame", action="store_true", help="hame tai pitka helma: tasaiset painot reisien valilla")
ap.add_argument("--ei_mr", action="store_true", default=True)
ap.add_argument("--reppu", action="store_true", help="reppu tai muu iso kantamus selassa: vartalon syvyyskeskikohta mitataan reisista eika ylavartalosta")
ap.add_argument("--pituus", type=float, default=0, help="skaalaa malli tahan pituuteen (m); 0 = mallin oma pituus")
A = ap.parse_args()

# ------------------------------------------------------------------ lahde (NPC)
G = GLB(A.lahde); j = G.j
sk = j["skins"][0]; JN = sk["joints"]; NJ = len(JN)
names = [j["nodes"][i]["name"] for i in JN]
idx = {n: k for k, n in enumerate(names)}
IBn = G.acc(sk["inverseBindMatrices"]).reshape(-1, 4, 4).transpose(0, 2, 1)
Wn = np.linalg.inv(IBn)                       # NPC bind, mesh-avaruus
Pn = Wn[:, :3, 3].copy()
Rn = np.array([w[:3, :3] / np.linalg.norm(w[:3, 0]) for w in Wn])
par = {}
for i, n in enumerate(j["nodes"]):
    for c in n.get("children", []):
        par[c] = i
jparent = [idx.get(j["nodes"][par[i]]["name"], -1) if i in par else -1 for i in JN]
children = {k: [c for c in range(NJ) if jparent[c] == k] for k in range(NJ)}

prims = j["meshes"][0]["primitives"]
npos = np.concatenate([G.acc(p["attributes"]["POSITION"]) for p in prims])
njnt = np.concatenate([G.acc(p["attributes"]["JOINTS_0"]) for p in prims]).astype(int)
nwgt = np.concatenate([G.acc(p["attributes"]["WEIGHTS_0"]) for p in prims])
Hn = npos[:, 1].max()

# ------------------------------------------------------------------ kohde (Meshy)
M = GLB(A.meshy); mj = M.j
mp = mj["meshes"][0]["primitives"][0]
mpos = M.acc(mp["attributes"]["POSITION"])
node0 = mj["nodes"][mj["scenes"][0]["nodes"][0]]
Mt = trs(node0)
mpos = (np.c_[mpos, np.ones(len(mpos))] @ Mt.T)[:, :3]
mnrm = M.acc(mp["attributes"]["NORMAL"]) @ Mt[:3, :3].T
muv = M.acc(mp["attributes"]["TEXCOORD_0"])
mind = M.acc(mp["indices"]).astype(np.uint32).ravel()
mpos[:, 1] -= mpos[:, 1].min()
if A.pituus > 0:
    mpos *= A.pituus / mpos[:, 1].max()
Hm = mpos[:, 1].max()
s = Hm / Hn
print("korkeus: lahde %.3f, kohde %.3f, skaala %.3f" % (Hn, Hm, s))

# ------------------------------------------------------------------ nivelten sovitus
P = Pn * s
# z-siirto: vartalon keskikohta
def torso_c(pts, H):
    m = (pts[:, 1] > 0.5 * H) & (pts[:, 1] < 0.8 * H) & (np.abs(pts[:, 0]) < 0.12 * H / 1.8)
    return 0.5 * (np.percentile(pts[m, 2], 3) + np.percentile(pts[m, 2], 97))
dz = torso_c(mpos, Hm) - torso_c(npos * s, Hm)
if A.reppu:
    def thigh_c(pts, H):
        m = (pts[:, 1] > 0.36 * H) & (pts[:, 1] < 0.46 * H) & (np.abs(pts[:, 0]) < 0.2 * H / 1.8)
        return 0.5 * (np.percentile(pts[m, 2], 3) + np.percentile(pts[m, 2], 97))
    dz = thigh_c(mpos, Hm) - thigh_c(npos * s, Hm)
P[:, 2] += dz
P[:, 0] -= P[idx["pelvis"], 0]

def chain_fit(chain, verts, tipfrac):
    """Sovita ketju (nivelindeksit juuresta karkeen) verteksipilven paa-akselille."""
    c = verts.mean(0)
    u, sv, vt = np.linalg.svd(verts - c, full_matrices=False)
    d = vt[0]
    root = P[chain[0]]
    if np.dot(d, P[chain[-1]] - root) < 0:
        d = -d
    # juurinivel akselille lahimpaan kohtaan (vain sivusuunnassa, ei pituussuunnassa)
    t0 = np.dot(root - c, d)
    root_on = c + d * t0
    tmax = np.max((verts - root_on) @ d)
    Ln = [np.linalg.norm(Pn[chain[i + 1]] - Pn[chain[i]]) for i in range(len(chain) - 1)]
    total = sum(Ln)
    k = tmax * tipfrac / total
    new = [root_on]
    for L in Ln:
        new.append(new[-1] + d * L * k)
    return np.array(new), d, k

side = {"l": 1, "r": -1}
for sd, sg in side.items():
    # kasi
    ua, la, ha = idx["upperarm_" + sd], idx["lowerarm_" + sd], idx["hand_" + sd]
    sh_x = abs(P[ua, 0])
    armv = mpos[(mpos[:, 0] * sg > sh_x + 0.06 * s) & (mpos[:, 1] < P[ua, 1]) & (mpos[:, 1] > P[ua, 1] - 0.85 * s)]
    # karki: kasien karki ~ (olka->sormenpaa); kyynarpaa+ranne = osuus ketjusta
    Lu = np.linalg.norm(Pn[la] - Pn[ua]); Ll = np.linalg.norm(Pn[ha] - Pn[la])
    tipn = max(np.linalg.norm(Pn[idx[f"middle_03_{sd}"]] - Pn[ua]) + 0.03, Lu + Ll + 0.15)
    new, d, k = chain_fit([ua, la, ha], armv, (Lu + Ll) / tipn)
    Sa = rot_between(Pn[ha] - Pn[ua], d)
    P[ua], P[la], P[ha] = new
    # kasi + sormet jaykkana ranteen mukana
    sub = []
    st = [ha]
    while st:
        b = st.pop(); sub.append(b); st += children[b]
    Sh = rot_between(Pn[ha] - Pn[la], d)
    for b in sub:
        if b != ha:
            P[b] = P[ha] + Sh @ ((Pn[b] - Pn[ha]) * s * k)
    # solisluu kohti olkaa
    # jalka
    th, ca, fo = idx["thigh_" + sd], idx["calf_" + sd], idx["foot_" + sd]
    # jalan linja: lonkka = skaalattu lahde, nilkka = saaren kohdalla olevan viipaleen keskikohta (toimii myos hameella)
    fy = P[fo, 1]
    band = mpos[(mpos[:, 0] * sg > 0.015) & (mpos[:, 0] * sg < 0.3 * s) & (mpos[:, 1] > fy + 0.07 * s) & (mpos[:, 1] < fy + 0.2 * s)]
    bx = 0.5 * (band[:, 0].min() + band[:, 0].max()); bz = 0.5 * (band[:, 2].min() + band[:, 2].max())
    ank = np.array([bx, fy, bz])
    P[th] = np.array([0.5 * (P[th, 0] + bx), P[th, 1], P[th, 2]])
    kn = P[th] + (ank - P[th]) * (np.linalg.norm(Pn[ca] - Pn[th]) / (np.linalg.norm(Pn[ca] - Pn[th]) + np.linalg.norm(Pn[fo] - Pn[ca])))
    off_f = {b: P[b] - P[fo] for b in (idx["ball_" + sd],)}
    P[ca], P[fo] = kn, ank
    for b, o in off_f.items():
        P[b] = ank + o
    # pohjaan: ball maahan
    P[idx["ball_" + sd], 1] = max(P[idx["ball_" + sd], 1], 0.01)

# ------------------------------------------------------------------ sidosasento (bind)
prim_child = {"pelvis": "spine_01", "spine_03": "neck_01", "hand_l": "middle_01_l", "hand_r": "middle_01_r", "Root": None}
R = np.zeros_like(Rn)
order = sorted(range(NJ), key=lambda k: 0 if jparent[k] < 0 else 1 + sum(1 for _ in iter(lambda: None, 1)) if False else 0)
# topologinen jarjestys
order, seen = [], set()
def visit(k):
    if k in seen: return
    if jparent[k] >= 0: visit(jparent[k])
    seen.add(k); order.append(k)
for k in range(NJ): visit(k)
Sb = [np.eye(3)] * NJ
for k in order:
    nm = names[k]
    pc = prim_child.get(nm, "x")
    if pc is None:
        S = np.eye(3)
    else:
        ch = idx[pc] if pc in idx else (children[k][0] if children[k] else None)
        if ch is None:
            S = Sb[jparent[k]] if jparent[k] >= 0 else np.eye(3)
        else:
            S = rot_between(Pn[ch] - Pn[k], P[ch] - P[k])
    Sb[k] = S
    R[k] = S @ Rn[k]
B = np.tile(np.eye(4), (NJ, 1, 1)); B[:, :3, :3] = R; B[:, :3, 3] = P
IBm = np.linalg.inv(B)

# ------------------------------------------------------------------ painojen siirto
# NPC-verkko kohteen sidosasentoon
Xf = np.einsum("kij,kjl->kil", B, IBn)          # NPC bind -> kohteen bind
nh = np.c_[npos, np.ones(len(npos))]
dpos = np.zeros((len(npos), 3))
for c in range(4):
    T = Xf[njnt[:, c]]
    dpos += nwgt[:, c:c + 1] * np.einsum("nij,nj->ni", T, nh)[:, :3]
tree = cKDTree(dpos)
lmask = np.array([n.endswith("_l") for n in names]); rmask = np.array([n.endswith("_r") for n in names])
def transfer(pts, k):
    dist, nn = tree.query(pts, k=k)
    W = np.zeros((len(pts), NJ))
    iw = 1.0 / (dist + 1e-4) ** 2
    for c in range(k):
        for q in range(4):
            np.add.at(W, (np.arange(len(pts)), njnt[nn[:, c], q]), iw[:, c] * nwgt[nn[:, c], q])
    W[np.ix_(pts[:, 0] > 0.03, rmask)] = 0
    W[np.ix_(pts[:, 0] < -0.03, lmask)] = 0
    return W
W = transfer(mpos, A.k)
bad = W.sum(1) < 1e-9
for kk in (40, 200):
    if bad.any():
        W[bad] = transfer(mpos[bad], kk); bad = W.sum(1) < 1e-9
print("painot: korjattuja", int(bad.sum()))
if A.hame:
    # hame/esiliina: reisien valinen kangas ei saa revetä kahdeksi lahkeeksi
    W = W / W.sum(1, keepdims=True)
    pel, tl, tr = idx["pelvis"], idx["thigh_l"], idx["thigh_r"]
    y0 = 0.5 * (P[idx["calf_l"], 1] + P[idx["calf_r"], 1]) - 0.02; y1 = P[pel, 1]
    reg = (mpos[:, 1] > y0) & (mpos[:, 1] < y1) & (np.abs(mpos[:, 0]) < 0.3 * s)
    a = np.clip((y1 - mpos[reg, 1]) / (y1 - y0), 0, 1) * 0.7
    xr = np.clip(mpos[reg, 0] / (0.15 * s), -1, 1)
    new = np.zeros((reg.sum(), NJ))
    new[:, pel] = 1 - a
    new[:, tl] = a * (0.5 + 0.35 * xr)
    new[:, tr] = a * (0.5 - 0.35 * xr)
    # sekoitus: kangas (kaukana luusta) = uusi, iho/jalat sailyy
    W[reg] = new
top = np.argsort(-W, axis=1)[:, :4]
tw = np.take_along_axis(W, top, 1)
tw = tw / tw.sum(1, keepdims=True)
tw[tw < 0.01] = 0
tw = tw / tw.sum(1, keepdims=True)

# ------------------------------------------------------------------ uusi luuranko (lepo = NPC:n rotaatiot, uudet pituudet)
nodes_out = []
jnode = {}
for k in range(NJ):
    n = j["nodes"][JN[k]]
    p = jparent[k]
    if p >= 0:
        t = R[p].T @ (P[k] - P[p])
    else:
        t = P[k]
    nd = {"name": names[k], "rotation": list(map(float, n.get("rotation", [0, 0, 0, 1]))), "translation": list(map(float, t))}
    nodes_out.append(nd)
for k in range(NJ):
    ch = children[k]
    if ch:
        nodes_out[k]["children"] = ch
# NPC-rotaatio Root-tasolla: jos Root-noodilla oli rotaatio, se sailyy

# ------------------------------------------------------------------ animaatiot
def clips_from(g, wanted=None):
    jj = g.j
    nm2 = {jj["nodes"][i]["name"]: i for i in range(len(jj["nodes"]))}
    out = []
    for a in jj.get("animations", []):
        if wanted and a["name"] not in wanted:
            continue
        ch = []
        for c in a["channels"]:
            node = jj["nodes"][c["target"]["node"]].get("name")
            if node not in idx:
                continue
            smp = a["samplers"][c["sampler"]]
            ch.append((idx[node], c["target"]["path"], g.acc(smp["input"]).ravel(), g.acc(smp["output"]), smp.get("interpolation", "LINEAR")))
        out.append((a["name"], ch, g))
    return out

clips = clips_from(G)
if A.lisaklipit:
    f, names_x = A.lisaklipit.split(":")
    have = {c[0] for c in clips}
    clips += [c for c in clips_from(GLB(f), set(names_x.split(","))) if c[0] not in have]

pelvis = idx["pelvis"]; root = idx["Root"]
def rest_t(g, k):
    jj = g.j
    nd = next(n for n in jj["nodes"] if n.get("name") == names[k])
    return np.array(nd.get("translation", [0, 0, 0]))

anim_out = []
for name, chans, g in clips:
    keep = []
    for (k, path, tin, tout, interp) in chans:
        if path == "scale":
            continue
        if path == "translation":
            if k not in (pelvis, root):
                continue
            rt = rest_t(g, k)
            hs = (np.linalg.norm(nodes_out[k]["translation"]) / max(np.linalg.norm(rt), 1e-6)) if k == pelvis else s
            tout = np.array(nodes_out[k]["translation"]) + (tout - rt) * hs
        keep.append((k, path, tin, tout, interp))
    anim_out.append((name, keep))
print("klipit:", [a[0] for a in anim_out])

# ------------------------------------------------------------------ GLB:n kirjoitus
buf = bytearray(); views = []; accs = []
def add_view(data, target=None):
    while len(buf) % 4: buf.append(0)
    off = len(buf); buf.extend(data)
    v = {"buffer": 0, "byteOffset": off, "byteLength": len(data)}
    if target: v["target"] = target
    views.append(v); return len(views) - 1
def add_acc(arr, ctype, typ, target=None, minmax=False, norm=False):
    arr = np.ascontiguousarray(arr)
    v = add_view(arr.tobytes(), target)
    a = {"bufferView": v, "componentType": ctype, "count": int(arr.shape[0]), "type": typ}
    if norm: a["normalized"] = True
    if minmax:
        a["min"] = arr.min(0).tolist() if arr.ndim > 1 else [float(arr.min())]
        a["max"] = arr.max(0).tolist() if arr.ndim > 1 else [float(arr.max())]
    accs.append(a); return len(accs) - 1

a_pos = add_acc(mpos.astype(np.float32), 5126, "VEC3", 34962, True)
nl_ = np.linalg.norm(mnrm, axis=1, keepdims=True)
nn_ = np.where(nl_ > 1e-8, mnrm / np.maximum(nl_, 1e-8), [0.0, 1.0, 0.0])   # nollanormaalit (Meshyn surkastuneet kolmiot) ylospain
a_nrm = add_acc(nn_.astype(np.float32), 5126, "VEC3", 34962)
a_uv = add_acc(muv.astype(np.float32), 5126, "VEC2", 34962)
a_j = add_acc(top.astype(np.uint8), 5121, "VEC4", 34962)
a_w = add_acc(tw.astype(np.float32), 5126, "VEC4", 34962)
a_i = add_acc(mind.astype(np.uint32), 5125, "SCALAR", 34963)
a_ib = add_acc(IBm.transpose(0, 2, 1).reshape(NJ, 16).astype(np.float32), 5126, "MAT4")

# kuvat
import io
from PIL import Image as PILImage
images = []
mat0 = mj["materials"][0]
mr_tex = mat0["pbrMetallicRoughness"].get("metallicRoughnessTexture", {}).get("index")
mr_img = mj["textures"][mr_tex]["source"] if mr_tex is not None else None
for ii, im in enumerate(mj["images"]):
    data = M.view(im["bufferView"])
    if ii == mr_img and A.ei_mr:
        data = b"\xff\xd8\xff\xd9"
    img = PILImage.open(io.BytesIO(data)).convert("RGB") if len(data) > 8 else PILImage.new("RGB", (4, 4), (0, 200, 0))
    if max(img.size) > A.tex:
        img = img.resize((A.tex, A.tex), PILImage.LANCZOS)
    bio = io.BytesIO(); img.save(bio, "JPEG", quality=85)
    images.append({"bufferView": add_view(bio.getvalue()), "mimeType": "image/jpeg"})

# solmut: 0..NJ-1 luut, NJ = mesh, NJ+1 = Player
mesh_node = NJ; player = NJ + 1
nodes = nodes_out + [{"name": "PlayerMesh", "mesh": 0, "skin": 0},
                     {"name": "Player", "children": [mesh_node, root]}]
anims = []
for name, ch in anim_out:
    smp, chs = [], []
    for (k, path, tin, tout, interp) in ch:
        ai = add_acc(tin.astype(np.float32), 5126, "SCALAR", None, True)
        ao = add_acc(tout.astype(np.float32), 5126, "VEC4" if path == "rotation" else "VEC3")
        smp.append({"input": ai, "output": ao, "interpolation": interp})
        chs.append({"sampler": len(smp) - 1, "target": {"node": k, "path": path}})
    anims.append({"name": name, "samplers": smp, "channels": chs})

mat = json.loads(json.dumps(mj["materials"][0]))
mat["name"] = A.nimi
mat["doubleSided"] = False
mat["pbrMetallicRoughness"]["metallicFactor"] = 0.0
mat["pbrMetallicRoughness"]["roughnessFactor"] = 0.8
mat["pbrMetallicRoughness"].pop("metallicRoughnessTexture", None)
gj = {"asset": {"version": "2.0", "generator": "porikopteri rigaa.py"},
      "scene": 0, "scenes": [{"name": "Scene", "nodes": [player]}],
      "nodes": nodes,
      "meshes": [{"name": "PlayerMesh", "primitives": [{"attributes": {"POSITION": a_pos, "NORMAL": a_nrm, "TEXCOORD_0": a_uv, "JOINTS_0": a_j, "WEIGHTS_0": a_w},
                                                         "indices": a_i, "material": 0}]}],
      "skins": [{"joints": list(range(NJ)), "inverseBindMatrices": a_ib, "skeleton": root}],
      "materials": [mat], "textures": mj["textures"], "samplers": mj.get("samplers", []), "images": images,
      "animations": anims, "accessors": accs, "bufferViews": views, "buffers": [{"byteLength": len(buf)}]}
js = json.dumps(gj, separators=(",", ":")).encode()
while len(js) % 4: js += b" "
while len(buf) % 4: buf.append(0)
out = struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(buf)) + struct.pack("<I", len(js)) + b"JSON" + js + struct.pack("<I", len(buf)) + b"BIN\x00" + bytes(buf)
open(A.out, "wb").write(out)
print("kirjoitettu", A.out, len(out) // 1024, "kt;", len(mind) // 3, "kolmiota")
if A.debug:
    np.save("debug_P.npy", P)
if A.debug:
    bad = ~np.isfinite(tw).all(1)
    print("bad verts", bad.sum(), "x-range", mpos[bad, 0].min() if bad.any() else None, mpos[bad, 0].max() if bad.any() else None, "y", mpos[bad, 1].min() if bad.any() else None, mpos[bad, 1].max() if bad.any() else None)
    for n in ("upperarm_l", "lowerarm_l", "hand_l", "middle_03_l", "upperarm_r", "hand_r", "thigh_l", "calf_l", "foot_l", "ball_l", "head"):
        print(n, np.round(P[idx[n]], 3), np.round(Pn[idx[n]] * s, 3))
    print("deformed npc x-range", dpos[:, 0].min(), dpos[:, 0].max())
