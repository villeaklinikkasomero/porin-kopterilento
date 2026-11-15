"""Sharp aerial tiles ot/ot_i_j.jpg from the MML 2025 orthophoto (0.5 m, EPSG:3067 jp2 sheets M3412C-F).
Game frame: x = (lon - 21.796) * 53278, y = (lat - 61.486) * 111437; tile (i, j) covers x0 = -1280 + 512 i, y0 = -1280 + 512 j, 512 m."""
import sys, numpy as np, rasterio
from rasterio.windows import from_bounds
from pyproj import Transformer
from scipy.ndimage import map_coordinates
from PIL import Image
SRC = '/mnt/user-data/uploads/porin-kopterilento/mml_orto/M3412%s.jp2'
ds = [rasterio.open(SRC % k) for k in 'CDEF']
T = Transformer.from_crs('EPSG:4326', 'EPSG:3067', always_xy=True)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
out = sys.argv[2] if len(sys.argv) > 2 else '/home/claude/work/ot_new'
I0, I1, J0, J1 = -3, 7, -1, 6
def tile(i, j):
    x0, y0 = -1280 + 512 * i, -1280 + 512 * j
    u = (np.arange(N) + 0.5) / N * 512
    X, Y = np.meshgrid(x0 + u, y0 + 512 - u)            # row 0 = north edge
    lon = X / 53278 + 21.796; lat = Y / 111437 + 61.486
    E, Nn = T.transform(lon, lat)
    img = np.zeros((N, N, 3), np.float32); have = np.zeros((N, N), bool)
    for d in ds:
        b = d.bounds
        m = (E >= b.left) & (E < b.right) & (Nn > b.bottom) & (Nn <= b.top)
        if not m.any(): continue
        e0, e1, n0, n1 = max(E[m].min() - 2, b.left), min(E[m].max() + 2, b.right), max(Nn[m].min() - 2, b.bottom), min(Nn[m].max() + 2, b.top)
        w = from_bounds(e0, n0, e1, n1, d.transform).round_offsets().round_lengths()
        a = d.read(window=w).astype(np.float32)        # (3, h, w)
        tr = d.window_transform(w)
        col = (E[m] - tr.c) / tr.a - 0.5; row = (Nn[m] - tr.f) / tr.e - 0.5
        for c in range(3): img[..., c][m] = map_coordinates(a[c], [row, col], order=1, mode='nearest')
        have |= m
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(f'{out}/ot_{i}_{j}.jpg', quality=86)
    return have.mean()
if __name__ == '__main__':
    ij = [(int(a.split(',')[0]), int(a.split(',')[1])) for a in sys.argv[3:]] or [(i, j) for i in range(I0, I1 + 1) for j in range(J0, J1 + 1)]
    for i, j in ij: print(i, j, round(tile(i, j), 3), flush=True)
