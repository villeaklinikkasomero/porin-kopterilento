# -*- coding: utf-8 -*-
"""Katulamppu (omistajan Meshy-malli, 8 m pylvas + 3 m varsi, ei tekstuuria) pelin muotoon:
python tee_katuvalo.py katuvalo_meshy.glb ../../aika/katuvalo_malli.js [kolmioita=1200]
Harventaa mallin (7 400 -> 1 200 kolmiota, lamppuja piirretaan satoja), siirtaa pylvaan tyven origoon (varsi +z-suuntaan) ja laskee normaalit.
pip install numpy fast-simplification"""
import sys, json, struct, base64
import numpy as np
import fast_simplification as fs

src, ulos = sys.argv[1:3]; maara = int(sys.argv[3]) if len(sys.argv) > 3 else 1200
b = open(src, "rb").read(); n = struct.unpack("<I", b[12:16])[0]; j = json.loads(b[20:20 + n]); bin0 = b[20 + n + 8:]
def acc(i, dt, k):
    a = j["accessors"][i]; v = j["bufferViews"][a["bufferView"]]; o = v.get("byteOffset", 0) + a.get("byteOffset", 0)
    return np.frombuffer(bin0, dtype=dt, count=a["count"] * k, offset=o).reshape(-1, k)
p = j["meshes"][0]["primitives"][0]; P = acc(p["attributes"]["POSITION"], np.float32, 3)
ia = j["accessors"][p["indices"]]; I = acc(p["indices"], {5123: np.uint16, 5125: np.uint32}[ia["componentType"]], 1).reshape(-1, 3).astype(np.int32)
P, I = fs.simplify(P.astype(np.float32), I, target_count=maara)
tyvi = P[P[:, 1] < 0.5]; P = P - np.array([tyvi[:, 0].mean(), 0.0, tyvi[:, 2].mean()], dtype=np.float32); P[:, 1] -= P[:, 1].min()
fn = np.cross(P[I[:, 1]] - P[I[:, 0]], P[I[:, 2]] - P[I[:, 0]]); N = np.zeros_like(P)
for c in range(3): np.add.at(N, I[:, c], fn)
N /= np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)
paa = P[(P[:, 2] > 2.3) & (P[:, 1] > P[:, 1].max() - 0.3)]
print("kolmioita %d, pisteita %d, korkeus %.2f, valaisimen keskikohta z %.2f, alapinta y %.2f" % (len(I), len(P), P[:, 1].max(), (paa[:, 2].min() + paa[:, 2].max()) / 2, paa[:, 1].min()))
buf = bytearray(); views = []; accs = []
def lisaa(arr, ctype, typ, target, mm=False):
    while len(buf) % 4: buf.append(0)
    views.append({"buffer": 0, "byteOffset": len(buf), "byteLength": arr.nbytes, "target": target}); buf.extend(arr.tobytes())
    a = {"bufferView": len(views) - 1, "componentType": ctype, "count": int(arr.shape[0]) if typ != "SCALAR" else int(arr.size), "type": typ}
    if mm: a["min"] = arr.min(0).tolist(); a["max"] = arr.max(0).tolist()
    accs.append(a); return len(accs) - 1
prim = {"attributes": {"POSITION": lisaa(P.astype(np.float32), 5126, "VEC3", 34962, True), "NORMAL": lisaa(N.astype(np.float32), 5126, "VEC3", 34962)}, "indices": lisaa(I.astype(np.uint16).ravel(), 5123, "SCALAR", 34963)}
out = {"asset": {"version": "2.0", "generator": "porikopteri tee_katuvalo.py"}, "scene": 0, "scenes": [{"nodes": [0]}], "nodes": [{"mesh": 0}], "meshes": [{"primitives": [prim]}],
       "accessors": accs, "bufferViews": views, "buffers": [{"byteLength": len(buf)}]}
js = json.dumps(out, separators=(",", ":")).encode()
while len(js) % 4: js += b" "
while len(buf) % 4: buf.append(0)
out["buffers"][0]["byteLength"] = len(buf); js = json.dumps(out, separators=(",", ":")).encode()
while len(js) % 4: js += b" "
g = struct.pack("<III", 0x46546C67, 2, 28 + len(js) + len(buf)) + struct.pack("<I", len(js)) + b"JSON" + js + struct.pack("<I", len(buf)) + b"BIN\x00" + bytes(buf)
open(ulos, "w", encoding="utf-8", newline="").write("// Katulamppu (Meshy, harvennettu): tools/aika/tee_katuvalo.py. Tyvi origossa, varsi +z, korkeus 8 m.\nexport default \"%s\";\n" % base64.b64encode(g).decode())
print("->", ulos, len(g) // 1024, "kt")
