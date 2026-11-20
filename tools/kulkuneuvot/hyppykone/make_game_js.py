"""Pack the GLB for the game: re-encode textures as JPEG with size caps, write
`export default "<base64>"` modules like the other vehicles (heli.js, vene.js).
usage: make_game_js.py in.glb out.js max_tex [header_comment]"""
import sys, json, struct, io, base64
from PIL import Image

src, dst, cap = sys.argv[1], sys.argv[2], int(sys.argv[3])
header = sys.argv[4] if len(sys.argv) > 4 else ""
b = open(src, "rb").read()
L = struct.unpack("<I", b[12:16])[0]
j = json.loads(b[20:20 + L])
o = 20 + L
bl = struct.unpack("<I", b[o:o + 4])[0]
binb = b[o + 8:o + 8 + bl]

views = [binb[v.get("byteOffset", 0):v.get("byteOffset", 0) + v["byteLength"]] for v in j["bufferViews"]]
# which images are normal maps / mr maps (sharper JPEG for normals)
role = {}
for m in j.get("materials", []):
    pb = m.get("pbrMetallicRoughness", {})
    if "baseColorTexture" in pb: role[pb["baseColorTexture"]["index"]] = "base"
    if "metallicRoughnessTexture" in pb: role[pb["metallicRoughnessTexture"]["index"]] = "mr"
    if "normalTexture" in m: role[m["normalTexture"]["index"]] = "normal"
img_role = {j["textures"][t]["source"]: r for t, r in role.items()}
for i, im in enumerate(j.get("images", [])):
    vi = im["bufferView"]
    pic = Image.open(io.BytesIO(views[vi])).convert("RGB")
    r = img_role.get(i, "base")
    c = cap if r != "mr" else max(256, cap // 2)
    if max(pic.size) > c:
        s = c / max(pic.size); pic = pic.resize((max(1, int(pic.size[0] * s)), max(1, int(pic.size[1] * s))), Image.LANCZOS)
    f = io.BytesIO(); pic.save(f, format="JPEG", quality=92 if r == "normal" else 85, optimize=True, subsampling=0 if r == "normal" else 2)
    views[vi] = f.getvalue(); im["mimeType"] = "image/jpeg"
# rebuild the binary chunk
out = bytearray()
for v, data in zip(j["bufferViews"], views):
    while len(out) % 4: out.append(0)
    v["byteOffset"] = len(out); v["byteLength"] = len(data); out += data
while len(out) % 4: out.append(0)
j["buffers"] = [{"byteLength": len(out)}]
js = json.dumps(j, separators=(",", ":")).encode()
while len(js) % 4: js += b" "
glb = struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(out)) + struct.pack("<II", len(js), 0x4E4F534A) + js + struct.pack("<II", len(out), 0x004E4942) + bytes(out)
open(dst.replace(".js", ".glb"), "wb").write(glb)
with open(dst, "w", encoding="utf-8") as f:
    if header: f.write("// " + header + "\n")
    f.write('export default "' + base64.b64encode(glb).decode() + '";\n')
geo = sum(len(views[v["bufferView"]]) for v in [] ) if False else sum(len(d) for k, d in enumerate(views) if k not in {im["bufferView"] for im in j.get("images", [])})
print(dst, "glb %.2f MB (geometry %.2f MB), js %.2f MB" % (len(glb) / 1e6, geo / 1e6, len(glb) * 4 / 3 / 1e6))
