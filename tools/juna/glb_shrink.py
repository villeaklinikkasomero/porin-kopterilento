"""Pienentää GLB:n upotetut kuvat (sivu enintään N px, JPEG). python3 glb_shrink.py in.glb out.glb 2048 [laatu]"""
import sys, json, struct, io
from PIL import Image
src, dst, N = sys.argv[1], sys.argv[2], int(sys.argv[3]); Q = int(sys.argv[4]) if len(sys.argv) > 4 else 84
d = open(src, 'rb').read(); jl = struct.unpack('<I', d[12:16])[0]; j = json.loads(d[20:20 + jl]); b0 = 20 + jl + 8; binb = d[b0:b0 + struct.unpack('<I', d[20 + jl:24 + jl])[0]]
new = {}
for im in j.get('images', []):
    bv = j['bufferViews'][im['bufferView']]; raw = binb[bv.get('byteOffset', 0):bv.get('byteOffset', 0) + bv['byteLength']]
    I = Image.open(io.BytesIO(raw)).convert('RGB')
    if max(I.size) > N: I = I.resize((N, N) if I.size[0] == I.size[1] else (N, int(N * I.size[1] / I.size[0])), Image.LANCZOS)
    bio = io.BytesIO(); I.save(bio, 'JPEG', quality=Q); new[im['bufferView']] = bio.getvalue(); im['mimeType'] = 'image/jpeg'
out = bytearray()
for i, bv in sorted(enumerate(j['bufferViews']), key=lambda t: t[1].get('byteOffset', 0)):
    data = new.get(i, binb[bv.get('byteOffset', 0):bv.get('byteOffset', 0) + bv['byteLength']])
    while len(out) % 4: out.append(0)
    bv['byteOffset'] = len(out); bv['byteLength'] = len(data); out += data
while len(out) % 4: out.append(0)
j['buffers'][0]['byteLength'] = len(out); js = json.dumps(j, separators=(',', ':')).encode(); js += b' ' * ((4 - len(js) % 4) % 4)
open(dst, 'wb').write(b'glTF' + struct.pack('<II', 2, 12 + 8 + len(js) + 8 + len(out)) + struct.pack('<I', len(js)) + b'JSON' + js + struct.pack('<I', len(out)) + b'BIN\x00' + bytes(out))
print(dst, len(out) // 1000, 'kt')
