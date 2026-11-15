"""Mix the sharp old tiles (0.25 m, ot_old) with the MML 2025 tiles (0.5 m, ot_new): the old image is kept where the two agree,
the new one (upsampled) where the ground has changed (new buildings, the renewed quay ...). Change test on 8 m blocks:
local structure correlation of colour-normalised, blurred images."""
import sys, numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
OLD, NEW, OUT = sys.argv[1:4]; keys = sys.argv[4:]
def norm(a):
    m = a.reshape(-1, 3).mean(0); s = a.reshape(-1, 3).std(0) + 1e-3; return (a - m) / s
for k in keys:
    o = np.asarray(Image.open(f'{OLD}/ot_{k}.jpg').convert('RGB'), np.float32)          # 2048
    n = np.asarray(Image.open(f'{NEW}/ot_{k}.jpg').convert('RGB').resize((2048, 2048), Image.BICUBIC), np.float32)
    os_ = ndimage.zoom(o, (0.25, 0.25, 1), order=1); ns_ = ndimage.zoom(n, (0.25, 0.25, 1), order=1)   # 1 m px for the test
    a = ndimage.gaussian_filter(norm(os_).mean(2), 1.0); b = ndimage.gaussian_filter(norm(ns_).mean(2), 1.0)
    B = 8                                                                                  # 8 m blocks
    h = a.shape[0] // B
    A = a[:h * B, :h * B].reshape(h, B, h, B).transpose(0, 2, 1, 3).reshape(h, h, -1); Bb = b[:h * B, :h * B].reshape(h, B, h, B).transpose(0, 2, 1, 3).reshape(h, h, -1)
    A = A - A.mean(-1, keepdims=True); Bb = Bb - Bb.mean(-1, keepdims=True)
    cor = (A * Bb).sum(-1) / (np.sqrt((A * A).sum(-1) * (Bb * Bb).sum(-1)) + 1e-6)
    dm = np.abs(a[:h * B, :h * B].reshape(h, B, h, B).mean((1, 3)) - b[:h * B, :h * B].reshape(h, B, h, B).mean((1, 3)))
    tex = np.sqrt((A * A).mean(-1))
    changed = ((cor < 0.45) & (tex > 0.2)) | (dm > 0.9)
    changed = ndimage.binary_opening(changed, iterations=1)                                # lone blocks are noise (shadows, cars)
    changed = ndimage.binary_dilation(changed, iterations=2)
    m = ndimage.zoom(changed.astype(np.float32), 2048 / h, order=0)[:2048, :2048]
    m = ndimage.gaussian_filter(m, 12)[..., None]
    out = o * (1 - m) + n * m
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(f'{OUT}/ot_{k}.jpg', quality=88)
    Image.fromarray((changed * 255).astype(np.uint8)).resize((256, 256)).save(f'{OUT}/mask_{k}.png')
    print(k, round(float(changed.mean()), 3), flush=True)
