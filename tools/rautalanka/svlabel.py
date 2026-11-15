"""Draw building ids onto a Street View screenshot: footprint corners projected with the pano position/heading/pitch from the URL.
usage: svlabel.py img.jpg lat lon heading pitch out.jpg [ids...]"""
import sys, json, math
from PIL import Image, ImageDraw
img, lat, lon, hd, pt, out = sys.argv[1], *map(float, sys.argv[2:6]), sys.argv[6]; ids = [int(a) for a in sys.argv[7:]]
s = open('/home/claude/pori/city.js').read(); C = json.loads(s[s.index('{'):s.rindex('}') + 1])
cx, cy = (lon - 21.796) * 53278, (lat - 61.486) * 111437
im = Image.open(img).convert('RGB'); W, H = im.size; f = (W / 2) / math.tan(math.radians(45)); d = ImageDraw.Draw(im)
def proj(x, y, z):
    dx, dy = x - cx, y - cy; b = math.degrees(math.atan2(dx, dy)); a = (b - hd + 540) % 360 - 180
    if abs(a) > 80: return None
    dist = math.hypot(dx, dy) * math.cos(math.radians(a)); u = W / 2 + f * math.tan(math.radians(a))
    el = math.degrees(math.atan2(z - 2.5, dist)) - pt; v = H / 2 - f * math.tan(math.radians(el)) / math.cos(math.radians(a)) * 1.0
    return u, v
cols = [(255, 60, 60), (60, 200, 255), (255, 220, 0), (120, 255, 120), (255, 120, 255), (255, 160, 60)]
for n, i in enumerate(ids or range(len(C['b']))):
    e = C['b'][i]; p = e['p']; pts = [(p[k] / 10, p[k + 1] / 10) for k in range(0, len(p), 2)]
    if min(math.hypot(x - cx, y - cy) for x, y in pts) > 60: continue
    c = cols[n % len(cols)]; segs = []
    for k in range(len(pts)):
        a, b = pts[k], pts[(k + 1) % len(pts)]
        A, B = proj(*a, 0), proj(*b, 0)
        if A and B: d.line([A, B], fill=c, width=2)
    vis = [proj(x, y, e['h']) for x, y in pts]; vis = [q for q in vis if q and 0 <= q[0] < W]
    if vis:
        u = sum(q[0] for q in vis) / len(vis); v = min(q[1] for q in vis)
        d.rectangle([u - 16, v - 2, u + 16, v + 11], fill=(0, 0, 0)); d.text((u - 14, v), str(i), fill=c)
im.save(out); print(out)
