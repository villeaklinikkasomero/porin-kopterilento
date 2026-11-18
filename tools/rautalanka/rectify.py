"""Facade rectifier (18.11.2026): turns a Street View screenshot into a straight view of one wall, in metres.

usage: python3 rectify.py sv.jpg cx cy heading pitch A_x,A_y B_x,B_y s0 s1 z0 z1 out.png [px_per_m=40] [fov=90] [ch=2.5] [d=0]
  sv.jpg     screenshot taken from the pano at game position (cx, cy) with that heading / pitch / vertical fov (any 16:9 size)
  A, B       the wall line in game metres (e.g. a LoD2 shell edge); s runs from A towards B, z up from the street at the camera
  s0..s1, z0..z1   the part of the wall to draw
  d          a plane d metres in front of the wall (right of A->B), e.g. 1.4 for balcony fronts
Every output pixel is a point on the wall plane, looked up in the photo (bilinear). A metre grid is drawn: thin lines every metre,
strong every 5 m, labels on the strong lines. Points the camera cannot see (behind it) stay black. Things standing in front of the
wall (trees, cars, balconies) are smeared onto it: read only what lies on the plane, and use d for projecting parts.
"""
import sys, math
import numpy as np
from PIL import Image, ImageDraw

def main():
    a = sys.argv[1:]
    sv, cx, cy, hd, pt = a[0], float(a[1]), float(a[2]), float(a[3]), float(a[4])
    A = tuple(map(float, a[5].split(','))); B = tuple(map(float, a[6].split(',')))
    s0, s1, z0, z1 = map(float, a[7:11]); out = a[11]
    ppm = float(a[12]) if len(a) > 12 else 40.0; fov = float(a[13]) if len(a) > 13 else 90.0
    ch = float(a[14]) if len(a) > 14 else 2.5; dd = float(a[15]) if len(a) > 15 else 0.0
    im = np.asarray(Image.open(sv).convert('RGB')).astype(np.float32); H, W = im.shape[:2]
    f = (H / 2) / math.tan(math.radians(fov / 2)); h = math.radians(hd); p = math.radians(pt)
    fwd = np.array([math.sin(h) * math.cos(p), math.cos(h) * math.cos(p), math.sin(p)])
    right = np.array([math.cos(h), -math.sin(h), 0.0]); up = np.array([-math.sin(h) * math.sin(p), -math.cos(h) * math.sin(p), math.cos(p)])
    L = math.hypot(B[0] - A[0], B[1] - A[1]); t = np.array([(B[0] - A[0]) / L, (B[1] - A[1]) / L]); n = np.array([t[1], -t[0]])
    ow, oh = int((s1 - s0) * ppm), int((z1 - z0) * ppm)
    ss = s0 + (np.arange(ow) + 0.5) / ppm; zz = z1 - (np.arange(oh) + 0.5) / ppm
    S, Zg = np.meshgrid(ss, zz)
    X = A[0] + t[0] * S + n[0] * dd - cx; Y = A[1] + t[1] * S + n[1] * dd - cy; Zr = Zg - ch    # relative to the camera
    P = np.stack([X, Y, Zr], -1)
    df = P @ fwd; u = (P @ right) / np.maximum(df, 1e-6) * f + W / 2; v = H / 2 - (P @ up) / np.maximum(df, 1e-6) * f
    ok = (df > 0.1) & (u >= 0) & (u < W - 1) & (v >= 0) & (v < H - 1)
    u0 = np.clip(np.floor(u).astype(int), 0, W - 2); v0 = np.clip(np.floor(v).astype(int), 0, H - 2); fu = (u - u0)[..., None]; fv = (v - v0)[..., None]
    img = (im[v0, u0] * (1 - fu) * (1 - fv) + im[v0, u0 + 1] * fu * (1 - fv) + im[v0 + 1, u0] * (1 - fu) * fv + im[v0 + 1, u0 + 1] * fu * fv)
    img[~ok] = 0
    o = Image.fromarray(img.clip(0, 255).astype(np.uint8)); d = ImageDraw.Draw(o)
    for k in range(math.ceil(s0), math.floor(s1) + 1):
        x = (k - s0) * ppm; strong = k % 5 == 0
        d.line([(x, 0), (x, oh)], fill=(255, 0, 0) if strong else (255, 120, 120), width=2 if strong else 1)
        if strong: d.text((x + 3, oh - 14), f's{k}', fill=(255, 255, 0))
    for k in range(math.ceil(z0), math.floor(z1) + 1):
        y = (z1 - k) * ppm; strong = k % 5 == 0
        d.line([(0, y), (ow, y)], fill=(0, 160, 255) if strong else (120, 190, 255), width=2 if strong else 1)
        if strong or k == math.ceil(z0): d.text((3, y - 14), f'z{k}', fill=(255, 255, 0))
    o.save(out); print(out, o.size)

if __name__ == '__main__':
    main()
