"""Procedural street textures (18.11.2026), after the owner's reference photos of Pori asphalt: a light grey stone-mastic surface full of
grey chips with some pink / red granite, and cracks here and there.
  road_asph.jpg   1024 px tileable, 1.6 m: carriageway asphalt (binder + chips 3-14 mm)
  road_pave.jpg   1024 px tileable, 1.2 m: pavement asphalt (finer, lighter, more worn)
  road_crack.png  2048 px tileable, 16 m, greyscale: 255 = sound, darker = cracks, sealed cracks (bitumen bands) and patches
usage: python3 tools/roads/make_tex.py outdir
"""
import sys, math
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
rng = np.random.default_rng(7)

def fbm(n, octaves, seed):
    r = np.random.default_rng(seed); acc = np.zeros((n, n)); amp = 1.0; tot = 0
    for o in range(octaves):
        k = 2 ** (o + 2); g = r.random((k, k))
        im = Image.fromarray((g * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC)   # periodic enough after wrap blend below
        a = np.asarray(im, np.float32) / 255
        acc += a * amp; tot += amp; amp *= 0.55
    acc /= tot
    return acc

def tileable_noise(n, scale_px, seed):
    """smooth periodic noise: sum of random-phase cosines on the integer lattice (exactly tileable)"""
    r = np.random.default_rng(seed); y, x = np.mgrid[0:n, 0:n] / n * 2 * math.pi; out = np.zeros((n, n))
    kmax = max(1, int(n / scale_px))
    for _ in range(40):
        kx, ky = r.integers(-kmax, kmax + 1, 2)
        if kx == 0 and ky == 0: continue
        out += math.exp(-(kx * kx + ky * ky) / (kmax * kmax)) * np.cos(kx * x + ky * y + r.random() * 6.283)
    out -= out.min(); out /= out.max() or 1; return out

def stones(n, mm_px, base, chips, density, seed, sizes=(3, 14)):
    r = np.random.default_rng(seed)
    img = Image.new('RGB', (n, n)); a = np.zeros((n, n, 3), np.float32)
    # binder: grey with sand-fine grain
    a[:] = np.array(base, np.float32)[None, None] / 255
    a += (r.random((n, n, 1)) - 0.5) * 0.10
    a *= (0.92 + 0.16 * tileable_noise(n, n / 6, seed + 1))[..., None]
    im = Image.fromarray((a.clip(0, 1) * 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    area = 0; target = density * n * n
    cols = [c for c, w in chips for _ in range(w)]
    while area < target:
        s = r.uniform(*sizes) / mm_px; s = s * (0.6 + 0.4 * r.random()) if r.random() < 0.6 else s * 0.45
        x, y = r.random() * n, r.random() * n
        k = int(r.integers(5, 9)); ang = r.random() * 6.283
        pts = [(math.cos(ang + 2 * math.pi * i / k) * s * (0.55 + 0.45 * r.random()), math.sin(ang + 2 * math.pi * i / k) * s * (0.55 + 0.45 * r.random())) for i in range(k)]
        c = np.array(cols[int(r.integers(len(cols)))], np.float32) * (0.85 + 0.3 * r.random())
        for ox in (-n, 0, n):
            for oy in (-n, 0, n):
                if -s < x + ox < n + s and -s < y + oy < n + s:
                    P = [(x + ox + px, y + oy + py) for px, py in pts]
                    d.polygon(P, fill=tuple(int(v) for v in c.clip(0, 255)))
                    hl = [(x + ox + px * 0.55 - s * 0.12, y + oy + py * 0.55 - s * 0.12) for px, py in pts]      # light on the top face
                    d.polygon(hl, fill=tuple(int(v) for v in (c * 1.12).clip(0, 255)))
        area += math.pi * (s * 0.8) ** 2
    a = np.asarray(im, np.float32) / 255
    # binder shows between chips: soften, then a dark rim (gaps) via a small blur difference
    b = np.asarray(im.filter(ImageFilter.GaussianBlur(1.2)), np.float32) / 255
    rim = np.clip((b - a).mean(-1, keepdims=True) * 1.5, -0.1, 0.1)
    a = a - np.abs(rim) * 0.8
    a += (r.random((n, n, 1)) - 0.5) * 0.05
    film = np.array(base, np.float32)[None, None] / 255
    a = a * 0.62 + film * 0.38
    return a.clip(0, 1)

GREY = [((168, 171, 173), 8), ((150, 153, 156), 9), ((132, 135, 138), 7), ((112, 115, 118), 4), ((186, 187, 186), 3),
        ((160, 140, 134), 1), ((146, 118, 108), 1), ((92, 94, 97), 1)]
asph = stones(1024, 1.6, (128, 131, 134), GREY, 0.95, 3, (2, 11))
Image.fromarray((asph * 255).astype(np.uint8)).save(f'{OUT}/road_asph.jpg', quality=90)
pave = stones(1024, 1.2, (146, 147, 147), GREY, 0.7, 5, (1.5, 7))
Image.fromarray((pave * 255).astype(np.uint8)).save(f'{OUT}/road_pave.jpg', quality=90)

# ---------------------------------------------------------------- cracks, 16 m tile at 7.8 mm/px
N = 2048; M = 16.0 / N   # saved at 1024 px below (GPU memory)
cr = Image.new('L', (N, N), 255); d = ImageDraw.Draw(cr)
def wrapline(pts, fill, width):
    for ox in (-N, 0, N):
        for oy in (-N, 0, N):
            d.line([(x + ox, y + oy) for x, y in pts], fill=fill, width=width, joint='curve')
def crack(x, y, ang, length, w, depth=0):
    pts = [(x, y)]; L = 0
    while L < length:
        ang += rng.normal(0, 0.35); st = rng.uniform(3, 9)
        x += math.cos(ang) * st; y += math.sin(ang) * st; pts.append((x, y)); L += st
        if depth < 2 and rng.random() < 0.03: crack(x, y, ang + rng.choice([-1, 1]) * rng.uniform(0.6, 1.4), length * rng.uniform(0.2, 0.5), max(1, w - 1), depth + 1)
    wrapline(pts, 70 + 25 * depth, w)
# patches (newer, darker asphalt rectangles) and sealed cracks (smooth black bitumen bands ~5 cm) first, open cracks on top
for _ in range(5):
    x, y = rng.random() * N, rng.random() * N; w, h = rng.uniform(80, 320), rng.uniform(60, 200); a = rng.random() * 3.1416
    P = [(x + math.cos(a) * u - math.sin(a) * v, y + math.sin(a) * u + math.cos(a) * v) for u, v in ((0, 0), (w, 0), (w, h), (0, h))]
    for ox in (-N, 0, N):
        for oy in (-N, 0, N): d.polygon([(px + ox, py + oy) for px, py in P], fill=int(rng.uniform(205, 228)))
for _ in range(7):
    x, y = rng.random() * N, rng.random() * N; ang = rng.random() * 6.283; pts = [(x, y)]
    for _ in range(int(rng.uniform(40, 160))):
        ang += rng.normal(0, 0.12); x += math.cos(ang) * 8; y += math.sin(ang) * 8; pts.append((x, y))
    wrapline(pts, int(rng.uniform(40, 70)), int(rng.uniform(4, 8)))
for _ in range(22): crack(rng.random() * N, rng.random() * N, rng.random() * 6.283, rng.uniform(150, 900), int(rng.integers(1, 3)))
# alligator cracking in two small areas
for _ in range(2):
    cx, cy = rng.random() * N, rng.random() * N
    for _ in range(18): crack(cx + rng.normal(0, 60), cy + rng.normal(0, 60), rng.random() * 6.283, rng.uniform(20, 70), 1, 2)
cr = cr.filter(ImageFilter.GaussianBlur(0.6))
cr.resize((1024, 1024), Image.LANCZOS).save(f'{OUT}/road_crack.png', optimize=True)
print('ok')
