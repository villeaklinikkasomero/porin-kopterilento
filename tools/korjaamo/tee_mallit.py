# -*- coding: utf-8 -*-
"""Tapsan korjaamon Meshy-mallit pelin muotoon: python tee_mallit.py halli_meshy.glb ovi_meshy.glb ../../korjaamo/korjaamo_mallit.js
Pitaa verkon ja varitekstuurin (halli 2048 px, ovi 1024 px, JPEG 85), jattaa normaali- ja metallisuuskartat pois (karheus 0,9).
Korjaa Meshyn nollanormaalit (naistä tuli pelissa mustia laikkuja seiniin) laskemalla normaalit kolmioista, ja leipoo pisteväreihin (COLOR_0)
suuntavalon: pelissa on vain tasainen taivasvalo, joten ilman tata seinat ja katto ovat yhta latteaa savya. Savy viilennetaan pelin lampimalle valolle.
pip install pillow numpy"""
import sys, json, struct, io, base64
import numpy as np
from PIL import Image

VALO = np.array([0.45, 0.70, 0.55]); VALO /= np.linalg.norm(VALO)      # mallin akseleissa: edesta (ovipaaty +z), ylhaalta, hieman oikealta
SAVY = np.array([0.86, 0.90, 1.00])

def pienenna(polku, tex=1024, maa_varjo=0.0):
    b = open(polku, "rb").read(); n = struct.unpack("<I", b[12:16])[0]; j = json.loads(b[20:20 + n]); bin0 = b[20 + n + 8:]
    def view(i):
        v = j["bufferViews"][i]; return bin0[v.get("byteOffset", 0):v.get("byteOffset", 0) + v["byteLength"]]
    buf = bytearray(); views = []; accs = []
    def lisaa(data, target=None):
        while len(buf) % 4: buf.append(0)
        v = {"buffer": 0, "byteOffset": len(buf), "byteLength": len(data)}
        if target: v["target"] = target
        buf.extend(data); views.append(v); return len(views) - 1
    def acc(i, target):
        a = dict(j["accessors"][i]); v = j["bufferViews"][a["bufferView"]]; assert not v.get("byteStride"), "lomitettu puskuri"
        koko = {5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4}[a["componentType"]] * {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}[a["type"]] * a["count"]
        o = v.get("byteOffset", 0) + a.get("byteOffset", 0); a["bufferView"] = lisaa(bin0[o:o + koko], target); a.pop("byteOffset", None); accs.append(a); return len(accs) - 1
    p = j["meshes"][0]["primitives"][0]
    def luku(i, dt, n):
        a = j["accessors"][i]; v = j["bufferViews"][a["bufferView"]]; o = v.get("byteOffset", 0) + a.get("byteOffset", 0)
        return np.frombuffer(bin0, dtype=dt, count=a["count"] * n, offset=o).reshape(-1, n) if n > 1 else np.frombuffer(bin0, dtype=dt, count=a["count"], offset=o)
    P = luku(p["attributes"]["POSITION"], np.float32, 3).astype(np.float64); N0 = luku(p["attributes"]["NORMAL"], np.float32, 3).astype(np.float64)
    ia = j["accessors"][p["indices"]]; I = luku(p["indices"], {5123: np.uint16, 5125: np.uint32}[ia["componentType"]], 1).astype(np.int64).reshape(-1, 3)
    fn = np.cross(P[I[:, 1]] - P[I[:, 0]], P[I[:, 2]] - P[I[:, 0]]); N = np.zeros_like(P)
    for c in range(3): np.add.at(N, I[:, c], fn)
    ln = np.linalg.norm(N, axis=1, keepdims=True); N = np.where(ln > 1e-12, N / np.maximum(ln, 1e-12), [0.0, 1.0, 0.0])
    l0 = np.linalg.norm(N0, axis=1); huono = ~(l0 > 0.5); print("  %s: nollanormaaleja %d / %d" % (polku, int(huono.sum()), len(P)))
    Nk = np.where(huono[:, None], N, N0 / np.maximum(l0, 1e-12)[:, None])
    # kaksipuolinen pinta: valo osuu kummalle puolelle tahansa, joten seinille |n·valo| olisi vaarin -> kaytetaan ulkonormaalia (poispain mallin keskiakselista)
    kesk = np.array([0.0, P[:, 1].mean(), 0.0]); ulos = np.sign(np.einsum("ij,ij->i", Nk, P - kesk)); ulos[ulos == 0] = 1; Nu = Nk * ulos[:, None]
    v = 0.52 + 0.48 * np.clip(Nu @ VALO, 0, 1)
    if maa_varjo > 0: v *= 1 - maa_varjo * np.clip(1 - P[:, 1] / 0.9, 0, 1) ** 2      # tummempi alareuna (lika, kosketusvarjo)
    C = np.clip(v[:, None] * SAVY[None, :], 0, 1); C = np.round(np.c_[C, np.ones(len(C))] * 255).astype(np.uint8)
    def uusi(arr, ctype, typ, target, minmax=False):
        a = {"bufferView": lisaa(np.ascontiguousarray(arr).tobytes(), target), "componentType": ctype, "count": int(len(arr)), "type": typ}
        if ctype == 5121: a["normalized"] = True
        if minmax: a["min"] = arr.min(0).tolist(); a["max"] = arr.max(0).tolist()
        accs.append(a); return len(accs) - 1
    prim = {"attributes": {"POSITION": acc(p["attributes"]["POSITION"], 34962), "NORMAL": uusi(Nk.astype(np.float32), 5126, "VEC3", 34962), "TEXCOORD_0": acc(p["attributes"]["TEXCOORD_0"], 34962),
                           "COLOR_0": uusi(C, 5121, "VEC4", 34962)}, "indices": acc(p["indices"], 34963), "material": 0}
    m = j["materials"][p["material"]]; ti = m["pbrMetallicRoughness"]["baseColorTexture"]["index"]
    img = Image.open(io.BytesIO(view(j["images"][j["textures"][ti]["source"]]["bufferView"]))).convert("RGB")
    if max(img.size) > tex: img = img.resize((tex, tex), Image.LANCZOS)
    bio = io.BytesIO(); img.save(bio, "JPEG", quality=85)
    out = {"asset": {"version": "2.0", "generator": "porikopteri tee_mallit.py"}, "scene": 0, "scenes": [{"nodes": [0]}], "nodes": [{"mesh": 0}],
           "meshes": [{"primitives": [prim]}], "materials": [{"pbrMetallicRoughness": {"baseColorTexture": {"index": 0}, "metallicFactor": 0.0, "roughnessFactor": 0.9}, "doubleSided": True}],
           "textures": [{"source": 0, "sampler": 0}], "samplers": [{"magFilter": 9729, "minFilter": 9987}], "images": [{"bufferView": lisaa(bio.getvalue()), "mimeType": "image/jpeg"}],
           "accessors": accs, "bufferViews": views, "buffers": [{"byteLength": 0}]}
    while len(buf) % 4: buf.append(0)
    out["buffers"][0]["byteLength"] = len(buf); js = json.dumps(out, separators=(",", ":")).encode()
    while len(js) % 4: js += b" "
    return struct.pack("<III", 0x46546C67, 2, 28 + len(js) + len(buf)) + struct.pack("<I", len(js)) + b"JSON" + js + struct.pack("<I", len(buf)) + b"BIN\x00" + bytes(buf)

halli, ovi, ulos = sys.argv[1:4]
h, o = pienenna(halli, 2048, 0.22), pienenna(ovi, 1024, 0.12)
open(ulos, "w", encoding="utf-8", newline="").write("// Tapsan korjaamon mallit (Meshy): halli ja nosto-ovi, base64-GLB. Tehty: tools/korjaamo/tee_mallit.py\nexport default {\n  halli: \"%s\",\n  ovi: \"%s\"\n};\n" % (base64.b64encode(h).decode(), base64.b64encode(o).decode()))
print("halli %d kt, ovi %d kt -> %s" % (len(h) // 1024, len(o) // 1024, ulos))
