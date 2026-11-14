"""Orthographic elevation straight from a bl_*.js glb (exact game colours, no Blender colour management).
usage: elev2.py in.js out.png Ax Ay Bx By ppm ztop zbot   (world m; A->B = image left->right, camera on the right-hand side of A->B... normal = (u.y,-u.x))"""
import base64, re, io, sys
import numpy as np, pygltflib
from PIL import Image
src, dst = sys.argv[1:3]; Ax, Ay, Bx, By, ppm, ztop, zbot = map(float, sys.argv[3:10])
s = open(src).read(); head = s[:s.index('export default')]
cx = float(re.search(r'x = ([-\d.]+)', head).group(1)); cy = float(re.search(r'y = ([-\d.]+)', head).group(1))
g = pygltflib.GLTF2.load_from_bytes(base64.b64decode(re.search(r'export default "([^"]+)"', s).group(1))); blob = g.binary_blob()
def acc(i):
    a = g.accessors[i]; bv = g.bufferViews[a.bufferView]; n = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3}[a.type]
    dt = {5126: np.float32, 5125: np.uint32, 5123: np.uint16}[a.componentType]; off = (bv.byteOffset or 0) + (a.byteOffset or 0)
    x = np.frombuffer(blob, dt, a.count * n, off); return x.reshape(a.count, n) if n > 1 else x
A = np.array([Ax - cx, Ay - cy]); B = np.array([Bx - cx, By - cy]); L = np.linalg.norm(B - A); u = (B - A) / L; n = np.array([u[1], -u[0]])
Wd, Hd = int(round(L * ppm)), int(round((ztop - zbot) * ppm))
img = np.zeros((Hd, Wd, 3), np.float32); zb = np.full((Hd, Wd), -1e9); img[:] = (205, 212, 220)
for pr in g.meshes[0].primitives:
    P = acc(pr.attributes.POSITION).astype(np.float64); UV = acc(pr.attributes.TEXCOORD_0).astype(np.float64); I = acc(pr.indices).reshape(-1, 3)
    bv = g.bufferViews[g.images[g.textures[g.materials[pr.material].pbrMetallicRoughness.baseColorTexture.index].source].bufferView]
    T = np.asarray(Image.open(io.BytesIO(blob[bv.byteOffset:bv.byteOffset + bv.byteLength])).convert('RGB')).astype(np.float32); th, tw = T.shape[:2]
    Wp = np.stack([P[:, 0], -P[:, 2], P[:, 1]], 1)
    X = ((Wp[:, :2] - A) @ u) * ppm; Y = (ztop - Wp[:, 2]) * ppm; D = (Wp[:, :2] - A) @ n          # D: towards the camera = larger
    for t in I:
        x, y, d = X[t], Y[t], D[t]
        x0, x1 = int(max(0, np.floor(x.min()))), int(min(Wd - 1, np.ceil(x.max()))); y0, y1 = int(max(0, np.floor(y.min()))), int(min(Hd - 1, np.ceil(y.max())))
        if x1 < x0 or y1 < y0: continue
        den = (y[1] - y[2]) * (x[0] - x[2]) + (x[2] - x[1]) * (y[0] - y[2])
        if abs(den) < 1e-9: continue
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        b0 = ((y[1] - y[2]) * (xs - x[2]) + (x[2] - x[1]) * (ys - y[2])) / den; b1 = ((y[2] - y[0]) * (xs - x[2]) + (x[0] - x[2]) * (ys - y[2])) / den; b2 = 1 - b0 - b1
        m = (b0 >= 0) & (b1 >= 0) & (b2 >= 0)
        if not m.any(): continue
        dd = b0 * d[0] + b1 * d[1] + b2 * d[2]; sub = zb[y0:y1 + 1, x0:x1 + 1]; m &= dd > sub
        if not m.any(): continue
        uv = UV[t]; uu = b0 * uv[0, 0] + b1 * uv[1, 0] + b2 * uv[2, 0]; vv = b0 * uv[0, 1] + b1 * uv[1, 1] + b2 * uv[2, 1]
        tx = np.clip((uu % 1) * tw, 0, tw - 1).astype(int); ty = np.clip((vv % 1) * th, 0, th - 1).astype(int)
        sub[m] = dd[m]; img[y0:y1 + 1, x0:x1 + 1][m] = T[ty[m], tx[m]]
Image.fromarray(img.astype(np.uint8)).save(dst); print(dst, Wd, Hd)
