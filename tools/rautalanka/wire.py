"""Rautalanka: project the model's LoD2 walls (as kivi.py builds them: cuts, lowered eaves) plus the facade layout (storey lines,
window boxes) onto a Street View screenshot. Pano position / heading / pitch from the Maps URL; '90y' is the VERTICAL field of view.
usage: wire.py img lat lon heading pitch vfov camh out ids..."""
import sys, math
sys.argv, A = sys.argv[:1], sys.argv[1:]
img, lat, lon, hd, pt, vf, camh, out = A[0], *map(float, A[1:7]), A[7]; ids = [int(a) for a in A[8:]]
from PIL import Image, ImageDraw
sys.path.insert(0, "/home/claude"); import kivi
from kivi import RAW, B, kspec
cx, cy = (lon - 21.796) * 53278, (lat - 61.486) * 111437
im = Image.open(img).convert('RGB'); W, H = im.size; f = (H / 2) / math.tan(math.radians(vf / 2)); d = ImageDraw.Draw(im, 'RGBA')
ch, sh_ = math.cos(math.radians(hd)), math.sin(math.radians(hd)); cp, sp = math.cos(math.radians(pt)), math.sin(math.radians(pt))
def proj(x, y, z):
    dx, dy, dz = x - cx, y - cy, z - camh
    fw = dx * sh_ + dy * ch; rt = dx * ch - dy * sh_          # forward / right in the ground plane
    fz = fw * cp + dz * sp; up = dz * cp - fw * sp            # pitch
    if fz < 0.3: return None
    return W / 2 + f * rt / fz, H / 2 - f * up / fz
def line(a, b, c, w=2):
    # clip to the camera front by subdividing
    pts = [proj(*[a[k] + (b[k] - a[k]) * t / 20 for k in range(3)]) for t in range(21)]
    seg = []
    for q in pts:
        if q is None:
            if len(seg) > 1: d.line(seg, fill=c, width=w)
            seg = []
        else: seg.append(q)
    if len(seg) > 1: d.line(seg, fill=c, width=w)
cols = [(255, 60, 60), (60, 200, 255), (255, 220, 0), (120, 255, 120), (255, 120, 255), (255, 160, 60)]
for n, i in enumerate(ids):
    c = cols[n % len(cols)] + (230,)
    for k, r, _ in RAW.get(i, []):
        if k not in ('W', 'R'): continue
        for a in range(len(r)): line(r[a], r[(a + 1) % len(r)], c, 2)
im.save(out); print(out, 'cam', round(cx, 1), round(cy, 1))
