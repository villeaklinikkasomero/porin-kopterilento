"""Give AI facade elevations their OWN texture inside a baked zone/landmark glb (bl_*.js): the matching wall triangles move to a
new primitive whose UVs map straight onto the elevation image (planar), so the facade keeps the elevation's full resolution.
usage: proj2.py in.js out.js spec.json
spec: [{img, A:[x,y], B:[x,y] (world m, along the facade = image left->right), H, ppm?, u0?, ztop?, img_rows_full?, depth?, auto_plane?,
        match?: elevation png -> per-channel colour match to it, maxw?: downscale the texture to this width}]"""
import base64, re, io, json, sys
import numpy as np, pygltflib
from PIL import Image
src, dst, specf = sys.argv[1:4]
s = open(src).read(); head = s[:s.index('export default')]
cx = float(re.search(r'x = ([-\d.]+)', head).group(1)); cy = float(re.search(r'y = ([-\d.]+)', head).group(1))
g = pygltflib.GLTF2.load_from_bytes(base64.b64decode(re.search(r'export default "([^"]+)"', s).group(1)))
blob = g.binary_blob()
def acc(i):
    a = g.accessors[i]; bv = g.bufferViews[a.bufferView]; n = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3}[a.type]
    dt = {5126: np.float32, 5125: np.uint32, 5123: np.uint16}[a.componentType]; off = (bv.byteOffset or 0) + (a.byteOffset or 0)
    x = np.frombuffer(blob, dt, a.count * n, off); return x.reshape(a.count, n) if n > 1 else x
pr = g.meshes[0].primitives[0]
P = acc(pr.attributes.POSITION).copy(); N = acc(pr.attributes.NORMAL).copy(); UV = acc(pr.attributes.TEXCOORD_0).copy(); I = acc(pr.indices).reshape(-1, 3).astype(np.int64)
W = np.stack([P[:, 0], -P[:, 2], P[:, 1]], 1).astype(np.float64)
keep = np.ones(len(I), bool); news = []
for sp in json.load(open(specf)):
    im = Image.open(sp['img']).convert('RGB')
    if sp.get('match'):                                  # keep the measured paint colour: per-channel mean/std transfer from our render
        a = np.asarray(im).astype(np.float32); r = np.asarray(Image.open(sp['match']).convert('RGB').resize(im.size)).astype(np.float32)
        k = sp.get('match_k', 1.0)
        for c in range(3):
            t = (a[..., c] - a[..., c].mean()) / (a[..., c].std() + 1e-3) * a[..., c].std() + r[..., c].mean()
            a[..., c] = a[..., c] * (1 - k) + t * k
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    iw0, ih0 = im.size
    A = np.array([sp['A'][0] - cx, sp['A'][1] - cy]); B = np.array([sp['B'][0] - cx, sp['B'][1] - cy])
    L = np.linalg.norm(B - A); u = (B - A) / L; n = np.array([u[1], -u[0]])
    if sp.get('auto_plane'):
        ds, ws = [], []
        for t in I:
            p = W[t]; nn = np.cross(p[1] - p[0], p[2] - p[0]); a2 = np.linalg.norm(nn)
            if a2 < 1e-6: continue
            nn /= a2
            if nn[0] * n[0] + nn[1] * n[1] > 0.9 and abs(nn[2]) < 0.2: ds.append((p.mean(0)[:2] - A) @ n); ws.append(a2)
        o = np.argsort(ds); cw = np.cumsum(np.array(ws)[o]); dm = np.array(ds)[o][np.searchsorted(cw, cw[-1] / 2)]; A = A + n * dm; B = B + n * dm
    S = max(L, sp['H']) * 1.04; ppm = sp.get('ppm', iw0 / S); u0 = sp.get('u0', L / 2 - (iw0 / ppm) / 2)
    ztop = sp.get('ztop', sp['H'] / 2 + (sp.get('img_rows_full', ih0) / ppm) / 2)
    sel = []
    for ti, t in enumerate(I):
        if not keep[ti]: continue
        p = W[t]; nn = np.cross(p[1] - p[0], p[2] - p[0]); a2 = np.linalg.norm(nn)
        if a2 < 1e-6: continue
        nn /= a2
        if nn[0] * n[0] + nn[1] * n[1] < 0.8 or abs(nn[2]) > 0.3: continue
        c = p.mean(0); d = (c[:2] - A) @ n
        if abs(d) > sp.get('depth', 1.8): continue
        qu = (p[:, :2] - A) @ u; px = (qu - u0) * ppm; py = (ztop - p[:, 2]) * ppm
        if px.min() < -1 or px.max() > iw0 + 1 or py.min() < -1 or py.max() > ih0 + 1: continue
        sel.append(ti)
    if not sel: print('no faces for', sp['img']); continue
    if sp.get('atlas_match', 0) > 0:                 # scale the AI colours so their mean equals the baked atlas over the same wall
        if 'atlas' not in globals():
            ib = g.images[0].bufferView; bv0 = g.bufferViews[ib]
            globals()['atlas'] = np.asarray(Image.open(io.BytesIO(blob[bv0.byteOffset:bv0.byteOffset + bv0.byteLength])).convert('RGB')).astype(np.float32)
        AT = globals()['atlas']; ah, aw = AT.shape[:2]; ai = np.asarray(im).astype(np.float32); sa = []; sb = []
        rng = np.random.default_rng(1)
        for ti in sel:
            t = I[ti]; p = W[t]
            for _ in range(4):
                w = rng.dirichlet([1, 1, 1]); q = w @ p; uvq = w @ UV[t]
                qu_ = (q[:2] - A) @ u; x = int((qu_ - u0) * ppm); y = int((ztop - q[2]) * ppm)
                if 0 <= x < iw0 and 0 <= y < ih0:
                    sa.append(AT[min(ah - 1, int(uvq[1] * ah)), min(aw - 1, int(uvq[0] * aw))]); sb.append(ai[y, x])
        gain = np.array(sa).mean(0) / (np.array(sb).mean(0) + 1e-3); k = sp['atlas_match']; gain = 1 + (gain - 1) * k
        print('colour gain', gain.round(3))
        im = Image.fromarray(np.clip(ai * gain, 0, 255).astype(np.uint8))
    keep[sel] = False
    T = I[sel]; vid = T.reshape(-1)
    qu = (W[vid, :2] - A) @ u; uvn = np.stack([((qu - u0) * ppm) / iw0, ((ztop - W[vid, 2]) * ppm) / ih0], 1)
    if sp.get('maxw') and iw0 > sp['maxw']: im = im.resize((sp['maxw'], round(ih0 * sp['maxw'] / iw0)), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'JPEG', quality=sp.get('q', 85)); news.append((P[vid], N[vid], uvn.astype(np.float32), b.getvalue()))
    print(sp['img'].split('/')[-1], 'faces', len(sel), 'tex', im.size, len(b.getvalue()) // 1024, 'KB')
# ---- rebuild the binary: old views (index view replaced by the kept indices), then the new primitives
I2 = I[keep].reshape(-1).astype(np.uint32)
views = []
for k, v in enumerate(g.bufferViews):
    views.append(blob[(v.byteOffset or 0):(v.byteOffset or 0) + v.byteLength])
iacc = g.accessors[pr.indices]; views[iacc.bufferView] = I2.tobytes(); iacc.componentType = 5125; iacc.count = len(I2); iacc.byteOffset = 0
mat0 = g.materials[0]
for (pp, nn_, uu, jpg) in news:
    def addview(data, target=None):
        g.bufferViews.append(pygltflib.BufferView(buffer=0, byteOffset=0, byteLength=len(data), target=target)); views.append(data); return len(g.bufferViews) - 1
    def addacc(arr, typ, ct=5126, target=34962):
        v = addview(arr.tobytes(), target); a = pygltflib.Accessor(bufferView=v, componentType=ct, count=len(arr), type=typ)
        if typ == 'VEC3': a.min = arr.min(0).tolist(); a.max = arr.max(0).tolist()
        g.accessors.append(a); return len(g.accessors) - 1
    ap = addacc(pp.astype(np.float32), 'VEC3'); an = addacc(nn_.astype(np.float32), 'VEC3'); au = addacc(uu, 'VEC2')
    ai = addacc(np.arange(len(pp), dtype=np.uint32), 'SCALAR', 5125, 34963)
    iv = addview(jpg); g.images.append(pygltflib.Image(bufferView=iv, mimeType='image/jpeg'))
    g.samplers.append(pygltflib.Sampler(magFilter=9729, minFilter=9987, wrapS=33071, wrapT=33071))
    g.textures.append(pygltflib.Texture(sampler=len(g.samplers) - 1, source=len(g.images) - 1))
    m = pygltflib.Material(name='aifacade', doubleSided=True, pbrMetallicRoughness=pygltflib.PbrMetallicRoughness(
        baseColorFactor=[1, 1, 1, 1], metallicFactor=0.0, roughnessFactor=0.5, baseColorTexture=pygltflib.TextureInfo(index=len(g.textures) - 1)))
    g.materials.append(m)
    g.meshes[0].primitives.append(pygltflib.Primitive(attributes=pygltflib.Attributes(POSITION=ap, NORMAL=an, TEXCOORD_0=au), indices=ai, material=len(g.materials) - 1))
parts = []; off = 0
for k, v in enumerate(g.bufferViews):
    data = views[k]; pad = (-off) % 4; parts.append(b'\0' * pad); off += pad; v.byteOffset = off; v.byteLength = len(data); parts.append(data); off += len(data)
nb = b''.join(parts); nb += b'\0' * ((-len(nb)) % 4); g.buffers[0].byteLength = len(nb); g.set_binary_blob(nb)
out = b''.join(g.save_to_bytes()); open(dst, 'w').write(head + 'export default "' + base64.b64encode(out).decode() + '";\n')
print('wrote', dst, len(out) // 1024, 'KB')
