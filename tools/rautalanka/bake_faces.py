"""Look inside a baked block: list the triangles of bl_<zone>.js in a plan box with their height, normal and baked colour.
Finds what a strange surface in the game really is (15.11.2026: the 'red roof' of 7 Hallituskatu was a strip of wall above the cornice).
usage: python3 bake_faces.py bl_kivi1.js xmin xmax ymin ymax [zmin]     (game metres; prints faces whose colour is not grey with -red)"""
import sys, re, base64, json, struct, io
import numpy as np
from PIL import Image
f = sys.argv[1]; x0, x1, y0, y1 = map(float, sys.argv[2:6]); zmin = float(sys.argv[6]) if len(sys.argv) > 6 else -99
s = open(f).read(); K = dict(re.findall(r'(x|y) = ([-\d.]+)', s.split('\n')[0])); kx, ky = float(K['x']), float(K['y'])
b = base64.b64decode(re.search(r'default "([^"]+)"', s).group(1))
l = struct.unpack('<I', b[12:16])[0]; j = json.loads(b[20:20 + l]); off = 20 + l; bl = struct.unpack('<I', b[off:off + 4])[0]; bin_ = b[off + 8:off + 8 + bl]
def acc(i):
    a = j['accessors'][i]; v = j['bufferViews'][a['bufferView']]; n = {'VEC3': 3, 'VEC2': 2, 'SCALAR': 1}[a['type']]
    dt = {5126: np.float32, 5123: np.uint16, 5125: np.uint32}[a['componentType']]; o = v.get('byteOffset', 0) + a.get('byteOffset', 0)
    return np.frombuffer(bin_, dt, a['count'] * n, o).reshape(-1, n) if n > 1 else np.frombuffer(bin_, dt, a['count'], o)
im = j['images'][0]; v = j['bufferViews'][im['bufferView']]
A = np.asarray(Image.open(io.BytesIO(bin_[v.get('byteOffset', 0):v.get('byteOffset', 0) + v['byteLength']])).convert('RGB')); H, W = A.shape[:2]
for pr in j['meshes'][0]['primitives']:
    P = acc(pr['attributes']['POSITION']); UV = acc(pr['attributes']['TEXCOORD_0']); I = acc(pr['indices'])
    for t in I.reshape(-1, 3):
        p = P[t]; c = p.mean(0); gx, gy = c[0] + kx, -c[2] + ky          # glTF: y up, z = -game y
        if not (x0 < gx < x1 and y0 < gy < y1) or c[1] < zmin: continue
        n = np.cross(p[1] - p[0], p[2] - p[0]); n = n / (np.linalg.norm(n) + 1e-9); uv = UV[t].mean(0)
        col = A[min(H - 1, int(uv[1] * H)), min(W - 1, int(uv[0] * W))]
        print(round(gx, 1), round(gy, 1), 'z', round(float(c[1]), 2), 'n', np.round(n, 2), 'rgb', col)
