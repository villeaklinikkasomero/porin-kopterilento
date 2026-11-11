import rasterio, numpy as np
from rasterio.merge import merge
from pyproj import Transformer
srcs = [rasterio.open(f'/mnt/user-data/uploads/Downloads/M3412{k}.tif') for k in 'CDEF']
mos, tr = merge(srcs); D = mos[0].astype(np.float32); D[D < -100] = np.nan
inv = ~tr
T = Transformer.from_crs(4326, 3067, always_xy=True)
def sample(x, y):
    lon = 21.796 + x / 53278; lat = 61.486 + y / 111437
    e, n = T.transform(lon, lat); c, r = inv * (e, n)
    c = np.clip(c - 0.5, 0, D.shape[1] - 2); r = np.clip(r - 0.5, 0, D.shape[0] - 2)
    c0 = np.floor(c).astype(int); r0 = np.floor(r).astype(int); fc = c - c0; fr = r - r0
    v = (D[r0, c0] * (1 - fc) * (1 - fr) + D[r0, c0 + 1] * fc * (1 - fr) + D[r0 + 1, c0] * (1 - fc) * fr + D[r0 + 1, c0 + 1] * fc * fr)
    return v
if __name__ == '__main__':
    for name, (x, y) in dict(tori=(31, 81), kirkko=(293, 300), river=(0, 600), eteläranta_quay=(-100, 492), kirjurinluoto=(-300, 800), asema=(-443, -930), isomaki=(-1600, -1300), viikkari=(-1100, -200), puuvilla=(160, 700), kuukkari=(-1500, 0), aittaluoto=(1177, 330)).items():
        print(name, round(float(sample(np.array([x]), np.array([y]))[0]), 2))

def build():
    import json, pickle, base64, shapely
    from shapely.geometry import box
    from scipy import ndimage
    s = open('/home/claude/pori/city.js').read(); C = json.loads(s[s.index('{'):s.rindex('}') + 1])
    OX0, OX1, OY0, OY1 = C['ox0'], C['ox1'], C['oy0'], C['oy1']
    REF = 4.0
    G = 6.0; nx = int(np.ceil((OX1 - OX0) / G)) + 1; ny = int(np.ceil((OY1 - OY0) / G)) + 1
    xs = OX0 + np.arange(nx) * G; ys = OY0 + np.arange(ny) * G; X, Y = np.meshgrid(xs, ys)
    H = sample(X.ravel(), Y.ravel()).reshape(ny, nx) - REF
    H = np.where(np.isnan(H), 0.0, H)
    R = pickle.load(open('/home/claude/river.pkl', 'rb'))
    riv = shapely.contains_xy(R, X, Y)
    WLabs = float(np.nanmedian(sample(X[riv], Y[riv]))) - REF       # water surface from the scan
    # smooth banks: signed distance to the shoreline (+ land, - water) shapes the bank so the waterline follows the
    # river outline instead of the 6 m grid; land within 10 m of the water eases down to it, the bed shelves out
    Bd = R.boundary; dist = shapely.distance(Bd, shapely.points(X.ravel(), Y.ravel())).reshape(X.shape)
    sd = np.where(riv, -dist, dist)
    bed = WLabs - np.minimum(2.6, 0.35 + 0.22 * np.maximum(0, -sd))
    bank = WLabs + 0.25 + 0.30 * sd
    Hg = H.copy()
    Hg = np.where(sd < 0, np.minimum(Hg, bed), Hg)
    near = (sd >= 0) & (sd < 10); Hg[near] = np.minimum(Hg[near], np.maximum(bank[near], WLabs + 0.05))
    Hg[(sd >= 0) & (sd < 1.5)] = (WLabs + 0.25 + 0.30 * sd)[(sd >= 0) & (sd < 1.5)]
    # object field: river filled from the banks, then smoothed, so buildings and bridges sit level
    Hs = H.copy(); idx = ndimage.distance_transform_edt(riv, return_distances=False, return_indices=True)
    Hs = Hs[idx[0], idx[1]]
    Hs = ndimage.gaussian_filter(Hs, 2.0)
    Hs = np.maximum(Hs, WLabs + 1.0)
    # Eteläranta quay strip: ground cells left out (the quay geometry fills them)
    Q = pickle.load(open('/home/claude/mmlproc/strip.pkl', 'rb'))
    cx = X + G / 2; cy = Y + G / 2; skip = shapely.contains_xy(Q, cx, cy)
    enc = lambda A: base64.b64encode(np.round(A * 10).astype('<i2').tobytes()).decode()
    res = dict(g=G, x0=OX0, y0=OY0, nx=nx, ny=ny, ref=REF, wl=round(WLabs + 0.12, 2), hg=enc(Hg), hs=enc(Hs),
               skip=base64.b64encode(np.packbits(skip.ravel())).decode())
    js = 'export default ' + json.dumps(res, separators=(',', ':')) + ';\n'
    open('/home/claude/pori/terrain.js', 'w').write(js)
    print('terrain', nx, ny, 'WL', res['wl'], 'MB', round(len(js) / 1e6, 2), 'range', round(float(H.min()), 1), round(float(H.max()), 1))
