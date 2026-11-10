import sys, math, json, numpy as np, cv2
sys.path.insert(0, '/home/claude')
from lib_city import C, B, poly
im = cv2.cvtColor(cv2.imread('/home/claude/pori/orto.jpg'), cv2.COLOR_BGR2RGB); H, W = im.shape[:2]
hw, ys, yn = C['hw'], C['ys'], C['yn']; mx = 2 * hw / W; my = (yn - ys) / H; MP = (mx + my) / 2
def px(x, y): return ((x + hw) / mx, (yn - y) / my)
bm = np.zeros((H, W), np.uint8)
for i in range(len(B)):
    cv2.fillPoly(bm, [np.array([px(*p) for p in poly(i)[0]], np.int32)], 255)
bm = cv2.dilate(bm, np.ones((9, 9), np.uint8))
f = im.astype(np.int16); r, g, b = f[..., 0], f[..., 1], f[..., 2]; lum = f.sum(2) / 3; sat = f.max(2) - f.min(2)
veg = cv2.dilate(((g > r + 6) & (g > b + 6)).astype(np.uint8), np.ones((3, 3), np.uint8))
bg = np.dstack([cv2.medianBlur(cv2.resize(im[..., k], (W // 2, H // 2), interpolation=cv2.INTER_AREA), 41) for k in range(3)])
bg = cv2.resize(bg, (W, H), interpolation=cv2.INTER_LINEAR).astype(np.int16); bl = bg.sum(2) / 3; bsat = bg.max(2) - bg.min(2)
asph = (bsat < 32) & (bl > 85) & (bl < 225)
tm = np.zeros((H, W), np.uint8); T = C['t']
for i in range(0, len(T), 2):
    p = px(T[i], T[i + 1])
    if 0 <= p[0] < W and 0 <= p[1] < H: cv2.circle(tm, (int(p[0]), int(p[1])), 8, 1, -1)
E11 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)); E9 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
def nobig(msk, el): return msk & (cv2.dilate(cv2.morphologyEx(msk, cv2.MORPH_OPEN, el), np.ones((5, 5), np.uint8)) == 0)
dark = nobig((lum < bl - 38).astype(np.uint8), E11)
bright = nobig(((lum > bl + 38) & (sat < 45)).astype(np.uint8), E9)
colr = nobig(((sat > 62) & ~((r > g + 25) & (g > b + 12) & (lum > 110))).astype(np.uint8), E11)      # skip sand / brick tones
shadow = cv2.dilate(cv2.morphologyEx((lum < 80).astype(np.uint8), cv2.MORPH_OPEN, E11), np.ones((9, 9), np.uint8))
m = ((dark | bright | colr) > 0) & (shadow == 0) & asph & (bm == 0) & (veg == 0) & (tm == 0)
m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
gray = cv2.GaussianBlur(lum.astype(np.float32), (0, 0), 0.8); gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0); gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1)
n, lab, st, cen = cv2.connectedComponentsWithStats(m, connectivity=4)
from scipy.spatial import cKDTree
rp = []; ra = []
for rd in C['r']:
    p = rd['p']
    for i in range(0, len(p) - 3, 2):
        ax_, ay_, bx_, by_ = p[i], p[i + 1], p[i + 2], p[i + 3]; L = math.hypot(bx_ - ax_, by_ - ay_)
        if L < 4: continue
        for t in np.linspace(0, 1, max(2, int(L / 10))): rp.append((ax_ + (bx_ - ax_) * t, ay_ + (by_ - ay_) * t)); ra.append(math.atan2(-(by_ - ay_), bx_ - ax_))   # image-frame angle
rtree = cKDTree(np.array(rp)); ra = np.array(ra)
KW, KH = 4, 8; cars = []; comps = []
for k in range(1, n):
    a = st[k, cv2.CC_STAT_AREA]
    if a < 16 or a > 30000: continue
    x0, y0, w0, h0 = st[k, :4]; sub = (lab[y0:y0 + h0, x0:x0 + w0] == k)
    yy, xx = np.nonzero(sub)
    wx_, wy_ = (x0 + w0 / 2) * mx - hw, yn - (y0 + h0 / 2) * my
    _, ri = rtree.query((wx_, wy_)); th = ra[ri]                       # street direction here; cars lie along or across it
    d1 = np.array([math.cos(th), math.sin(th)]); d2 = np.array([-d1[1], d1[0]])
    Pq = np.stack([xx, yy], 1).astype(float); e1 = np.ptp(Pq @ d1) + 1; e2 = np.ptp(Pq @ d2) + 1
    CL = 4.6 / MP; lg, sh = max(e1, e2), min(e1, e2); along1 = e1 >= e2          # along1: blob is longer along the street direction
    if lg < 0.55 * CL: continue
    amb = False
    if sh < 0.72 * CL: ang = th if along1 else th + math.pi / 2                    # single car / kerbside parking: cars point along the blob
    elif lg > 1.7 * sh or (lg > 2.2 * CL and abs(sh / CL - round(sh / CL)) < 0.3 and lg > 1.25 * sh): ang = th + math.pi / 2 if along1 else th   # a row: cars lie across it
    else: ang = th if along1 else th + math.pi / 2; amb = True
    comps.append((k, ang, amb, wx_, wy_, th))
dec = [(c[3], c[4], (c[1] - c[5]) % math.pi > 0.5) for c in comps if not c[2] and st[c[0], cv2.CC_STAT_AREA] >= 110]
dtree = cKDTree(np.array([(d[0], d[1]) for d in dec]))
for k, ang, amb, wx_, wy_, th in comps:
    if amb or (st[k, cv2.CC_STAT_AREA] < 110 and st[k, cv2.CC_STAT_AREA] > 34):                                                                         # undecided blob: follow the nearest clear row
        dd, ii = dtree.query((wx_, wy_), k=3)
        votes = [dec[i][2] for d_, i in zip(dd, ii) if d_ < 22]
        if votes: ang = th + math.pi / 2 if sum(votes) * 2 > len(votes) else th
    x0, y0, w0, h0 = st[k, :4]; sub = (lab[y0:y0 + h0, x0:x0 + w0] == k)
    pad = 10; cw, ch = w0 + 2 * pad, h0 + 2 * pad; big = np.zeros((ch, cw), np.uint8); big[pad:pad + h0, pad:pad + w0] = sub * 255
    D = int(math.ceil(math.hypot(cw, ch))) + 2; Mr = cv2.getRotationMatrix2D((cw / 2, ch / 2), math.degrees(ang) - 90, 1.0); Mr[0, 2] += D / 2 - cw / 2; Mr[1, 2] += D / 2 - ch / 2
    rot = cv2.warpAffine(big, Mr, (D, D), flags=cv2.INTER_LINEAR).astype(np.float32) / 255       # car long axis -> vertical
    cov = cv2.boxFilter(rot, -1, (KW, KH)); ys_, xs_ = np.nonzero(cov >= 0.62)
    if not len(ys_): continue
    order = np.lexsort((xs_, ys_, -np.round(cov[ys_, xs_] * 10))); occ = np.zeros((D, D), np.uint8); Mi = cv2.invertAffineTransform(Mr)
    for o in order:
        y, x = ys_[o], xs_[o]
        if occ[max(0, y - 4):y + 4, max(0, x - 2):x + 2].sum() > 3: continue
        occ[max(0, y - 4):y + 5, max(0, x - 2):x + 3] = 1
        cx = Mi[0, 0] * x + Mi[0, 1] * y + Mi[0, 2] + x0 - pad; cy = Mi[1, 0] * x + Mi[1, 1] * y + Mi[1, 2] + y0 - pad
        col = int(round(cx)); row = int(round(cy))
        pat = im[max(0, row - 1):row + 2, max(0, col - 1):col + 2].reshape(-1, 3)
        if not len(pat): continue
        cars.append((cx * mx - hw, yn - cy * my, math.atan2(math.cos(ang), -math.sin(ang)), np.median(pat, 0)))    # yaw: 0 = north, clockwise
print('components', n, 'cars', len(cars))
out = []
for X, Y, yaw, c in cars:
    gu = X * math.cos(-0.2275) + Y * math.sin(-0.2275); gv = -X * math.sin(-0.2275) + Y * math.cos(-0.2275)
    if 20 < gu < 90 and 46 < gv < 130: continue                      # market stalls on Kauppatori are not cars
    c = np.array(c, float); g_ = c.mean(); c = g_ + (c - g_) * 1.35; c = np.clip(c * 1.55 + 12, 0, 255)   # the photo blurs paint with glass and shadow: lift it
    out += [int(round(X * 10)), int(round(Y * 10)), int(round((yaw % (2 * math.pi)) * 100)) , (int(c[0]) << 16) | (int(c[1]) << 8) | int(c[2])]
open('/home/claude/pori/parked.js', 'w').write('// parked cars found in the aerial image: x*10, y*10, heading*100, colour\nexport default ' + json.dumps(out, separators=(',', ':')) + ';\n')
np.save('/home/claude/out/cars.npy', np.array([[c[0], c[1], c[2], *c[3]] for c in cars]))
def dbg(x0, y0, x1, y1, out, z=5):
    a = px(x0, y1); b_ = px(x1, y0); cr = im[int(a[1]):int(b_[1]), int(a[0]):int(b_[0])].copy(); cr = cv2.resize(cr, None, fx=z, fy=z, interpolation=cv2.INTER_CUBIC)
    for X, Y, yaw, col in cars:
        if x0 < X < x1 and y0 < Y < y1:
            p = px(X, Y); cx_, cy_ = (p[0] - int(a[0])) * z, (p[1] - int(a[1])) * z
            dx, dy = math.sin(yaw), -math.cos(yaw); L = 2.2 / MP * z; Wd = 0.9 / MP * z
            box = np.array([[cx_ + dx * L - dy * Wd, cy_ + dy * L + dx * Wd], [cx_ + dx * L + dy * Wd, cy_ + dy * L - dx * Wd], [cx_ - dx * L + dy * Wd, cy_ - dy * L - dx * Wd], [cx_ - dx * L - dy * Wd, cy_ - dy * L + dx * Wd]], np.int32)
            cv2.polylines(cr, [box], True, (255, 255, 0), 1)
    cv2.imwrite(out, cv2.cvtColor(cr, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 85])
dbg(140, 60, 290, 170, '/home/claude/out/d1.jpg', 6); dbg(-40, 10, 110, 150, '/home/claude/out/d2.jpg', 6); dbg(-600, -500, -450, -390, '/home/claude/out/d3.jpg', 6)
