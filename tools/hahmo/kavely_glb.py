# -*- coding: utf-8 -*-
"""
Leipoo porikopteri_hahmo.py:n Poser-luokan animaatiot (Idle, Walk, Run, Sit) suoraan hahmo.js:n GLB:hen ILMAN Blenderia.
Verkko, materiaalit ja tekstuurit sailyvat tavu tavulta; vain animaatioraidat kirjoitetaan uudestaan.

Ajo:  pip install mathutils
      python tools/hahmo/kavely_glb.py hahmo.js [ulos.js] [--check]
--check: leipoo klipit mutta ei kirjoita; tulostaa eron tiedoston nykyisiin raitoihin (0 = Poser ja GLB ovat samat).
"""
import sys, os, re, json, struct, base64
from math import sin, cos, pi, radians, acos, sqrt
from mathutils import Vector, Matrix, Quaternion

HERE = os.path.dirname(os.path.abspath(__file__))
CLIPS = (("Idle", 90, "idle"), ("Walk", 30, "walk"), ("Run", 20, "run"), ("Sit", 30, "sit"))
FPS = 30

def load_poser():
    src = open(os.path.join(HERE, "porikopteri_hahmo.py"), encoding="utf-8").read()
    a = src.index("# ANIMAATIOT")
    a = src.rindex("\n", 0, src.rindex("\n", 0, a)) + 1
    b = src.index("def bake_action")
    X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
    ns = dict(Vector=Vector, Matrix=Matrix, Quaternion=Quaternion, sin=sin, cos=cos, pi=pi, radians=radians, acos=acos,
              sqrt=sqrt, X=X, Y=Y, Z=Z, Q=lambda ax, deg: Quaternion(ax, radians(deg)),
              clamp=lambda v, lo=0.0, hi=1.0: max(lo, min(hi, v)))
    exec(compile(src[a:b], "porikopteri_hahmo.py[animaatiot]", "exec"), ns)
    return ns["Poser"]

class Glb:
    def __init__(self, data):
        jl = struct.unpack("<I", data[12:16])[0]
        self.j = json.loads(data[20:20 + jl])
        o = 20 + jl
        bl = struct.unpack("<I", data[o:o + 4])[0]
        self.bin = bytearray(data[o + 8:o + 8 + bl])
    def acc(self, i):
        a = self.j["accessors"][i]; bv = self.j["bufferViews"][a["bufferView"]]
        n = {"SCALAR": 1, "VEC3": 3, "VEC4": 4}[a["type"]]
        o = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
        v = struct.unpack_from("<%df" % (n * a["count"]), self.bin, o)
        return [v[k * n:(k + 1) * n] for k in range(a["count"])]
    def add(self, rows, typ, minmax=False):
        flat = [x for r in rows for x in r]
        while len(self.bin) % 4: self.bin.append(0)
        self.j["bufferViews"].append({"buffer": 0, "byteOffset": len(self.bin), "byteLength": 4 * len(flat)})
        self.bin += struct.pack("<%df" % len(flat), *flat)
        a = {"bufferView": len(self.j["bufferViews"]) - 1, "componentType": 5126, "count": len(rows), "type": typ}
        if minmax: a["min"], a["max"] = [min(flat)], [max(flat)]
        self.j["accessors"].append(a)
        return len(self.j["accessors"]) - 1
    def compact(self):
        """Pudottaa bufferView:t joihin mikaan ei enaa viittaa (vanhat animaatioraidat)."""
        j = self.j; used = set()
        for a in j["animations"]:
            for s in a["samplers"]: used |= {s["input"], s["output"]}
        for m in j.get("meshes", []):
            for p in m["primitives"]:
                used |= set(p["attributes"].values()); used.add(p.get("indices", -1))
                for t in p.get("targets", []): used |= set(t.values())
        for s in j.get("skins", []): used.add(s.get("inverseBindMatrices", -1))
        used.discard(-1)
        keep = sorted(used); amap = {o: n for n, o in enumerate(keep)}
        j["accessors"] = [j["accessors"][o] for o in keep]
        for a in j["animations"]:
            for s in a["samplers"]: s["input"], s["output"] = amap[s["input"]], amap[s["output"]]
        for m in j.get("meshes", []):
            for p in m["primitives"]:
                p["attributes"] = {k: amap[v] for k, v in p["attributes"].items()}
                if "indices" in p: p["indices"] = amap[p["indices"]]
                for t in p.get("targets", []):
                    for k in t: t[k] = amap[t[k]]
        for s in j.get("skins", []):
            if "inverseBindMatrices" in s: s["inverseBindMatrices"] = amap[s["inverseBindMatrices"]]
        vused = {a["bufferView"] for a in j["accessors"]} | {i["bufferView"] for i in j.get("images", []) if "bufferView" in i}
        vkeep = sorted(vused); vmap = {o: n for n, o in enumerate(vkeep)}; nb = bytearray(); views = []
        for o in vkeep:
            v = dict(j["bufferViews"][o]); off = v.get("byteOffset", 0)
            while len(nb) % 4: nb.append(0)
            chunk = self.bin[off:off + v["byteLength"]]; v["byteOffset"] = len(nb); nb += chunk; views.append(v)
        j["bufferViews"] = views
        for a in j["accessors"]: a["bufferView"] = vmap[a["bufferView"]]
        for i in j.get("images", []):
            if "bufferView" in i: i["bufferView"] = vmap[i["bufferView"]]
        self.bin = nb
    def pack(self):
        while len(self.bin) % 4: self.bin.append(0)
        self.j["buffers"][0]["byteLength"] = len(self.bin)
        js = json.dumps(self.j, separators=(",", ":")).encode()
        js += b" " * ((4 - len(js) % 4) % 4)
        return (b"glTF" + struct.pack("<II", 2, 12 + 8 + len(js) + 8 + len(self.bin)) + struct.pack("<I", len(js)) + b"JSON" + js
                + struct.pack("<I", len(self.bin)) + b"BIN\x00" + bytes(self.bin))

class _Bone:
    pass
class _Arm:
    """Sen verran Blenderin armatuuria kuin Poser tarvitsee: data.bones[nimi].head_local / tail_local / matrix_local."""
    def __init__(self, g):
        j = g.j; self.data = self; self.bones = {}; self.rest = {}
        par = {}
        for i, n in enumerate(j["nodes"]):
            for c in n.get("children", []): par[c] = i
        C = Quaternion((1, 0, 0), radians(-90))            # Blender (Z ylos) -> glTF (Y ylos)
        def world(i):
            n = j["nodes"][i]; r = n.get("rotation", [0, 0, 0, 1]); q = Quaternion((r[3], r[0], r[1], r[2])); t = Vector(n.get("translation", (0, 0, 0)))
            if i in par:
                pq, pt = world(par[i]); return pq @ q, pt + pq @ t
            return q, t
        for i in j["skins"][0]["joints"]:
            n = j["nodes"][i]; q, t = world(i); b = _Bone()
            qb = C.inverted() @ q; b.matrix_local = qb.to_matrix(); b.head_local = C.inverted() @ t; b.tail_local = b.head_local + qb @ Vector((0, 0.1, 0))
            self.bones[n["name"]] = b; r = n.get("rotation", [0, 0, 0, 1])
            self.rest[n["name"]] = (i, Quaternion((r[3], r[0], r[1], r[2])), Vector(n.get("translation", (0, 0, 0))))

def bake(arm, posefn, nframes):
    """Sama laskenta kuin porikopteri_hahmo.py:n bake_action, mutta tulos glTF-solmujen paikallisina arvoina."""
    rot = {n: [] for n in arm.bones}; loc = []; prev = {}
    for f in range(nframes + 1):
        P, d = posefn(f / nframes)
        d = Vector((0, 0, d)) if isinstance(d, (int, float)) else Vector(d)
        for name, b in arm.bones.items():
            R = b.matrix_local; q = P.get(name)
            ql = Quaternion() if q is None else (R.inverted() @ q.to_matrix() @ R).to_quaternion()
            g = arm.rest[name][1] @ ql
            if name in prev and g.dot(prev[name]) < 0: g.negate()
            prev[name] = g.copy(); rot[name].append((g.x, g.y, g.z, g.w))
        _, r0, t0 = arm.rest["pelvis"]
        loc.append(tuple(t0 + r0 @ (arm.bones["pelvis"].matrix_local.inverted() @ d)))
    return rot, loc

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]; check = "--check" in sys.argv
    src = args[0]; dst = args[1] if len(args) > 1 else src
    text = open(src, encoding="utf-8").read()
    m = re.search(r'"([A-Za-z0-9+/=]{1000,})"', text)
    g = Glb(base64.b64decode(m.group(1))); arm = _Arm(g); po = load_poser()(arm)
    names = {i: n["name"] for i, n in enumerate(g.j["nodes"])}
    for clip, nfr, fn in CLIPS:
        an = next(a for a in g.j["animations"] if a["name"] == clip)
        rot, loc = bake(arm, getattr(po, fn), nfr)
        if check:
            worst = 0.0
            for c in an["channels"]:
                s = an["samplers"][c["sampler"]]; old = g.acc(s["output"]); nm = names[c["target"]["node"]]; p = c["target"]["path"]
                new = rot[nm] if p == "rotation" else loc if (p == "translation" and nm == "pelvis") else None
                if new is None or len(old) != len(new): continue
                for a, b in zip(old, new):
                    e = min(max(abs(x - y) for x, y in zip(a, b)), max(abs(x + y) for x, y in zip(a, b))) if p == "rotation" else max(abs(x - y) for x, y in zip(a, b))
                    worst = max(worst, e)
            print("%s: suurin ero nykyiseen %.6f" % (clip, worst)); continue
        tin = g.add([(f / FPS,) for f in range(nfr + 1)], "SCALAR", True)
        tin2 = g.add([(0.0,), (nfr / FPS,)], "SCALAR", True)
        def put(s, rows, typ):                             # paikallaan pysyva luu: kaksi avainta riittaa
            if max(abs(x - y) for r in rows for x, y in zip(r, rows[0])) < 1e-7:
                s.update(input=tin2, output=g.add([rows[0], rows[0]], typ), interpolation="STEP")
            else:
                s.update(input=tin, output=g.add(rows, typ), interpolation="LINEAR")
        for c in an["channels"]:
            s = an["samplers"][c["sampler"]]; nm = names[c["target"]["node"]]; p = c["target"]["path"]
            if p == "rotation" and nm in rot: put(s, rot[nm], "VEC4")
            elif p == "translation" and nm == "pelvis": put(s, loc, "VEC3")
    if check: return
    g.compact()
    out = text[:m.start(1)] + base64.b64encode(g.pack()).decode() + text[m.end(1):]
    open(dst, "w", encoding="utf-8", newline="").write(out)
    print("kirjoitettu", dst, len(out))

if __name__ == "__main__":
    main()
