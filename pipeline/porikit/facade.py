"""Automatic photo facade extraction for Porin kopterilento.

photo -> line segments -> vertical + horizontal vanishing points -> virtual camera rotation to a frontal,
metric view -> floor and bay periods by autocorrelation -> tile grid cut at wall (not window) lines ->
tiles that disagree with the rest (trees, lamp posts, tents, people) dropped -> clean storey module ->
full-height strip for the game (ground floor shopfront + storeys + parapet).

Everything is plain OpenCV/numpy so it runs on any machine; the GPU only matters for the optional
segmentation/inpainting stage (porikit.clean) and for Blender bakes.
"""
from __future__ import annotations
import json, math
from dataclasses import dataclass, asdict, field
import numpy as np
import cv2


# ---------------------------------------------------------------- geometry
def segments(img: np.ndarray, max_side: int = 1600):
    """LSD line segments on a downscaled grey image; returns (N,4) in full-image pixels and the scale."""
    h, w = img.shape[:2]; s = min(1.0, max_side / max(h, w))
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    g = cv2.resize(g, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA) if s < 1 else g
    lsd = cv2.createLineSegmentDetector(cv2.LSD_REFINE_STD)
    L = lsd.detect(g)[0]
    if L is None: return np.zeros((0, 4)), s
    L = L.reshape(-1, 4) / s
    keep = np.hypot(L[:, 2] - L[:, 0], L[:, 3] - L[:, 1]) > max(h, w) * 0.025
    return L[keep], s


def _line(seg):
    p = np.array([seg[0], seg[1], 1.0]); q = np.array([seg[2], seg[3], 1.0]); l = np.cross(p, q)
    return l / (np.linalg.norm(l[:2]) + 1e-12)


def vanishing_point(segs: np.ndarray, iters: int = 1500, tol_deg: float = 1.2, rng=None):
    """RANSAC vanishing point of a family of segments; returns (vp homogeneous, inlier mask)."""
    rng = rng or np.random.default_rng(1)
    if len(segs) < 2: return None, np.zeros(len(segs), bool)
    lines = np.array([_line(s) for s in segs]); mids = np.c_[(segs[:, 0] + segs[:, 2]) / 2, (segs[:, 1] + segs[:, 3]) / 2, np.ones(len(segs))]
    dirs = np.c_[segs[:, 2] - segs[:, 0], segs[:, 3] - segs[:, 1]]; dirs /= np.linalg.norm(dirs, axis=1, keepdims=True) + 1e-12
    lens = np.hypot(dirs[:, 0], dirs[:, 1]) * np.hypot(segs[:, 2] - segs[:, 0], segs[:, 3] - segs[:, 1])
    best, bm = None, None; tol = math.radians(tol_deg)
    def score(vp):
        # angle between each segment and the ray from its midpoint to the vp
        if abs(vp[2]) < 1e-9: r = np.tile(vp[:2], (len(segs), 1))
        else: r = vp[:2] / vp[2] - mids[:, :2]
        r = r / (np.linalg.norm(r, axis=1, keepdims=True) + 1e-12)
        a = np.arccos(np.clip(np.abs((r * dirs).sum(1)), 0, 1)); m = a < tol
        return (lens * m).sum(), m
    for _ in range(iters):
        i, j = rng.choice(len(segs), 2, replace=False); vp = np.cross(lines[i], lines[j])
        if np.linalg.norm(vp) < 1e-12: continue
        sc, m = score(vp)
        if best is None or sc > best: best, bm, bv = sc, m, vp
    if bm is None or bm.sum() < 2: return None, np.zeros(len(segs), bool)
    # least squares refine on inliers: vp = smallest singular vector of the stacked lines
    A = lines[bm] * lens[bm, None]; vp = np.linalg.svd(A)[2][-1]
    return vp, score(vp)[1]


@dataclass
class Rectification:
    H: list                      # 3x3 homography photo -> frontal view
    size: tuple                  # output (w, h)
    f: float                     # focal length used (px)
    frontal: bool                # photo was already near frontal (no reliable horizontal vp)
    tilt_deg: float              # camera tilt that was removed
    yaw_deg: float               # facade angle that was removed
    region: tuple = ()           # facade area in the output (x0, y0, x1, y1)


def horizontal_vps(hor: np.ndarray, n: int = 4, min_frac: float = 0.05):
    """Sequential RANSAC: up to n horizontal vanishing points (one per visible facade), strongest first."""
    out, left = [], hor.copy(); total = np.hypot(hor[:, 2] - hor[:, 0], hor[:, 3] - hor[:, 1]).sum() + 1e-9
    for _ in range(n):
        if len(left) < 6: break
        vp, inl = vanishing_point(left)
        if vp is None: break
        ln = np.hypot(left[inl, 2] - left[inl, 0], left[inl, 3] - left[inl, 1]).sum()
        if ln / total < min_frac: break
        out.append((vp, left[inl])); left = left[~inl]
    return out


def rectify_all(img: np.ndarray, f_guess: float | None = None, max_out: int = 4096, n: int = 4):
    """One frontal, metric rectification per visible facade (virtual camera rotation H = K R K^-1)."""
    h, w = img.shape[:2]; c = np.array([w / 2, h / 2])
    L, _ = segments(img)
    ang = np.degrees(np.arctan2(L[:, 3] - L[:, 1], L[:, 2] - L[:, 0])) % 180
    vert = L[np.abs(ang - 90) < 25]; hor = L[(ang < 35) | (ang > 145)]
    vv, _ = vanishing_point(vert)
    out = []
    for hv, hseg in horizontal_vps(hor, n):
        f = f_guess or 1.1 * max(w, h); frontal = True
        if abs(hv[2]) > 1e-9 and np.linalg.norm(hv[:2] / hv[2] - c) < 12 * max(w, h): frontal = False
        if vv is not None and abs(vv[2]) > 1e-9 and not frontal and f_guess is None:
            d = -np.dot(vv[:2] / vv[2] - c, hv[:2] / hv[2] - c)
            if d > 0: f = float(np.clip(math.sqrt(d), 0.6 * max(w, h), 3.0 * max(w, h)))
        K = np.array([[f, 0, c[0]], [0, f, c[1]], [0, 0, 1.0]]); Ki = np.linalg.inv(K)
        up = Ki @ vv if vv is not None else np.array([0, -1.0, 0]); up = up / np.linalg.norm(up)
        if up[1] > 0: up = -up
        right = np.array([1.0, 0, 0]) if frontal else Ki @ hv
        right = right / np.linalg.norm(right)
        if right[0] < 0: right = -right
        right = right - up * np.dot(right, up); right /= np.linalg.norm(right)
        fwd = np.cross(right, -up); fwd /= np.linalg.norm(fwd)
        H = K @ np.stack([right, -up, fwd]) @ Ki
        # canvas: fit the facade's own segments (plus margin) rather than the whole photo
        P = np.c_[np.r_[hseg[:, 0], hseg[:, 2]], np.r_[hseg[:, 1], hseg[:, 3]], np.ones(2 * len(hseg))].T
        q = H @ P; q = q[:2] / q[2]
        fx0, fx1 = np.percentile(q[0], 2), np.percentile(q[0], 98); fy0, fy1 = np.percentile(q[1], 2), np.percentile(q[1], 98)
        mx, my = 0.08 * (fx1 - fx0), 0.15 * (fy1 - fy0)
        x0, x1, y0, y1 = fx0 - mx, fx1 + mx, fy0 - my, fy1 + my
        sc = min(1.0, max_out / max(x1 - x0, y1 - y0))
        T = np.array([[sc, 0, -x0 * sc], [0, sc, -y0 * sc], [0, 0, 1]])
        rec = Rectification((T @ H).tolist(), (int((x1 - x0) * sc), int((y1 - y0) * sc)), f, frontal,
                            math.degrees(math.asin(np.clip(-up[2], -1, 1))), math.degrees(math.atan2(right[2], right[0])))
        rec.region = (int((fx0 - x0) * sc), int((fy0 - y0) * sc), int((fx1 - x0) * sc), int((fy1 - y0) * sc))
        out.append(rec)
    return out


def rectify(img, f_guess=None, max_out=4096):
    r = rectify_all(img, f_guess, max_out, 1)
    if not r: raise ValueError('no facade lines found')
    return r[0]


def warp(img, rec: Rectification):
    return cv2.warpPerspective(img, np.array(rec.H), rec.size, flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))


def warp_quad(img, quad, out_w: int, out_h: int):
    """Manual override from the review UI: the four facade corners (TL, TR, BR, BL) -> out_w x out_h."""
    dst = np.float32([[0, 0], [out_w, 0], [out_w, out_h], [0, out_h]])
    H = cv2.getPerspectiveTransform(np.float32(quad), dst)
    return cv2.warpPerspective(img, H, (out_w, out_h), flags=cv2.INTER_CUBIC), H


# ---------------------------------------------------------------- rhythm
def _period(sig: np.ndarray, lo: int, hi: int):
    s = sig - sig.mean(); n = len(s); hi = min(hi, n // 2)
    if hi <= lo + 2: return None, 0.0
    ac = np.array([(s[:-k] * s[k:]).mean() for k in range(lo, hi)]) / (s.var() + 1e-9)
    # first strong local maximum (avoids picking 2x the period)
    peaks = [i for i in range(1, len(ac) - 1) if ac[i] >= ac[i - 1] and ac[i] >= ac[i + 1] and ac[i] > 0.25]
    if not peaks: k = int(np.argmax(ac))
    else:
        top = max(ac[i] for i in peaks); k = next(i for i in peaks if ac[i] > 0.7 * top)
    # parabolic sub-pixel refinement
    if 0 < k < len(ac) - 1:
        a, b, c = ac[k - 1], ac[k], ac[k + 1]; d = (a - c) / (2 * (a - 2 * b + c) + 1e-12)
    else: d = 0.0
    return lo + k + float(np.clip(d, -0.5, 0.5)), float(ac[k])


def _phase(energy: np.ndarray, period: float):
    """Offset in [0, period) where a cut line crosses the least edge energy (a wall band, not a window)."""
    n = int(period); best, bo = None, 0
    for o in range(n):
        idx = np.arange(o, len(energy), period).astype(int); idx = idx[idx < len(energy)]
        v = energy[idx].mean() if len(idx) else 1e9
        if best is None or v < best: best, bo = v, o
    return bo


@dataclass
class Module:
    floor_px: float
    bay_px: float
    x0: float
    y0: float
    tiles_used: int
    tiles_total: int
    score_floor: float
    score_bay: float
    region: tuple = field(default_factory=tuple)
    single: bool = False


def _best_period(sig: np.ndarray, lo: int, hi: int):
    """Autocorrelation period; prefers the fundamental (a strong peak at p/2 wins over p)."""
    s = sig - sig.mean(); n = len(s); hi = min(hi, n // 2)
    if hi <= lo + 2: return None, 0.0
    ac = np.array([(s[:-k] * s[k:]).mean() for k in range(1, hi)]) / (s.var() + 1e-9)   # ac[k-1] = lag k
    peaks = [k for k in range(max(lo, 2), hi - 1) if ac[k - 1] >= ac[k - 2] and ac[k - 1] >= ac[k] and ac[k - 1] > 0.15]
    if not peaks: return None, 0.0
    k = max(peaks, key=lambda q: ac[q - 1])
    for d in (2, 3):                                          # fundamental check
        cand = [q for q in peaks if abs(q - k / d) <= max(2, k * 0.04)]
        if cand and ac[cand[0] - 1] > 0.8 * ac[k - 1]: k = cand[0]
    a, b, c = ac[k - 2], ac[k - 1], ac[k]; dd = (a - c) / (2 * (a - 2 * b + c) + 1e-12)
    return k + float(np.clip(dd, -0.5, 0.5)), float(ac[k - 1])


def find_module(rect: np.ndarray, region=None, floor_range=(40, 400), bay_range=(30, 900)):
    """Floor and bay period + phase inside region (x0,y0,x1,y1) of a rectified facade."""
    if region is None:
        valid = (rect.sum(2) > 0).astype(np.uint8); ys, xs = np.nonzero(valid)
        region = (int(np.percentile(xs, 3)), int(np.percentile(ys, 3)), int(np.percentile(xs, 97)), int(np.percentile(ys, 97)))
    x0, y0, x1, y1 = [int(v) for v in region]
    g = cv2.cvtColor(rect[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY).astype(np.float32)
    ok = g > 0
    rows = np.array([r[m].mean() if m.sum() > 10 else 0 for r, m in zip(g, ok)])
    # columns: only the upper part (tents, trees and people sit low)
    gu = g[: max(10, int(g.shape[0] * 0.6))]; oku = gu > 0
    cols = np.array([c[m].mean() if m.sum() > 10 else 0 for c, m in zip(gu.T, oku.T)])
    fp, fs = _best_period(rows, *floor_range); bp, bs = _best_period(cols, *bay_range)
    single = fp is None or fp > 0.8 * (y1 - y0)                 # one storey (wooden houses): the whole selection is the module
    if single: fp = float(y1 - y0)
    if bp is None: bp = float(x1 - x0)
    # half / double ambiguity: shift the facade by the candidate period and compare it with itself;
    # the true period is the smallest shift that lines the facade up as well as twice that shift does
    def shift_diff(c, axis):
        k = int(round(c)); A = g if axis == 0 else gu
        if axis == 0: a, b = A[:-k], A[k:]
        else: a, b = A[:, :-k], A[:, k:]
        m = (a > 0) & (b > 0)
        return float(np.abs(a - b)[m].mean()) if m.sum() > 100 else 1e9
    for axis, rng_ in (((1, bay_range),) if single else ((0, floor_range), (1, bay_range))):
        p = fp if axis == 0 else bp; lim = (y1 - y0) if axis == 0 else (x1 - x0)
        cand = [c for c in (p / 2, p, p * 2) if rng_[0] <= c <= rng_[1] and c * 2 <= lim]
        dv = {c: shift_diff(c, axis) for c in cand}; best = min(dv.values())
        p = min(c for c in cand if dv[c] <= best * 1.1)
        if axis == 0: fp = p
        else: bp = p
    gy = np.abs(cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)); gx = np.abs(cv2.Sobel(gu, cv2.CV_32F, 1, 0, ksize=3))
    oy = _phase(gy.mean(1), fp); ox = _phase(gx.mean(0), bp)
    oy = 0 if single else oy
    m = Module(fp, bp, x0 + ox, y0 + oy, 0, 0, fs, bs, (x0, y0, x1, y1)); m.single = single
    return m


def extract_tile(rect: np.ndarray, m: Module, keep: float = 0.5):
    """Cut the facade into floor x bay tiles, drop the ones that disagree (occluders), median the rest."""
    fw, fh = int(round(m.bay_px)), int(round(m.floor_px)); x0, y0, x1, y1 = m.region
    tiles, pos = [], []
    j = 0
    while m.y0 + (j + 1) * m.floor_px <= y1 + 1:
        i = 0
        while m.x0 + (i + 1) * m.bay_px <= x1 + 1:
            M = np.float32([[1, 0, -(m.x0 + i * m.bay_px)], [0, 1, -(m.y0 + j * m.floor_px)]])
            t = cv2.warpAffine(rect, M, (fw, fh), flags=cv2.INTER_LINEAR).astype(np.float32)
            if (t.sum(2) == 0).mean() < 0.02: tiles.append(t); pos.append((i, j))
            i += 1
        j += 1
    if not tiles: raise ValueError('facade too small for a module')
    if len(tiles) == 1:                                           # one wall section (low houses): use it as it is
        m.tiles_used, m.tiles_total = 1, 1; return tiles[0].clip(0, 255).astype(np.uint8), pos, np.zeros(1)
    T = np.stack(tiles); med = np.median(T, 0)
    dev = np.abs(T - med).mean((1, 2, 3)); order = np.argsort(dev)
    n = max(2, int(math.ceil(len(T) * keep))); best = T[order[:n]]
    tile = np.median(best, 0)
    m.tiles_used, m.tiles_total = n, len(T)
    return tile.clip(0, 255).astype(np.uint8), [pos[k] for k in order[:n]], dev


def seamless(t: np.ndarray, b: int = 6):
    t = t.astype(np.float32).copy(); w = t.shape[1]; b = min(b, w // 6)
    for k in range(b):
        a = (k + 1) / (b + 1); t[:, w - b + k] = t[:, w - b + k] * (1 - a) + t[:, 0] * a
    return t.clip(0, 255).astype(np.uint8)


def wall_colour(tile: np.ndarray):
    """Most common bright-ish colour of a storey tile (the wall, not glass)."""
    p = tile.reshape(-1, 3).astype(np.float32); lum = p.mean(1)
    sel = p[lum > np.percentile(lum, 40)]
    return np.median(sel, 0)


def shopfront(w: int, h: int, wall, glass=(60, 52, 44), frame=(200, 205, 205)):
    """Generic ground floor (BGR): sign band, glazing with a sky reflection gradient, mullions, plinth."""
    wall = np.array(wall, np.float32); g = np.zeros((h, w, 3), np.float32); g[:] = wall
    fb = int(h * 0.16); g[:fb] = wall * 0.55; gl = np.array(glass, np.float32)
    for y in range(fb + 4, h - 6):
        t = (y - fb) / max(1, h - fb); g[y, 6:w - 6] = gl * (0.8 + 0.5 * (1 - t)) + np.array([26, 22, 18]) * (1 - t)
    n = max(2, int(round(w / 45)))
    for x in np.linspace(6, w - 7, n + 1).astype(int): g[fb + 4:h - 6, max(0, x - 2):x + 2] = frame
    g[h - 6:] = wall * 0.7
    return g.clip(0, 255).astype(np.uint8)


def build_strip(tile: np.ndarray, eave_m: float, floor_m: float | None = None, ground_m: float = 4.5, top: np.ndarray | None = None):
    if eave_m < 7.5:                                            # houses: one or two storeys straight from the photo
        return tile, {'bay_m': round(tile.shape[1] / tile.shape[0] * eave_m, 3), 'floor_m': eave_m, 'floors': 1, 'ground_m': 0, 'eave_m': eave_m}
    """One bay wide, street to eave. floor_m defaults to a whole number of ~3.1 m storeys above the ground floor."""
    nf = max(1, round((eave_m - ground_m) / (floor_m or 3.1))); floor_m = (eave_m - ground_m) / nf
    ph, w = tile.shape[:2]; pxm = ph / floor_m
    gfp = int(round(ground_m * pxm)); total = int(round(eave_m * pxm)); rest = max(4, total - gfp - nf * ph)
    wall = wall_colour(tile)
    tp = np.zeros((rest, w, 3), np.uint8); tp[:] = wall.astype(np.uint8)
    if top is not None: tp = cv2.resize(top, (w, rest))
    strip = np.concatenate([tp] + [tile] * nf + [shopfront(w, gfp, wall)], 0)
    return strip, {'bay_m': round(w / pxm, 3), 'floor_m': round(floor_m, 3), 'floors': nf, 'ground_m': ground_m, 'eave_m': eave_m}


# ---------------------------------------------------------------- one call
def process(photo_path: str, out_prefix: str, eave_m: float | None = None, quad=None, region=None, f_guess=None, floor_mul: float = 1.0, bay_mul: float = 1.0):
    """Whole automatic chain for one photo. Writes <out>_rect.jpg, <out>_tile.png, <out>.json (+ <out>_strip.jpg when eave_m is given)."""
    img = cv2.imread(photo_path)
    if img is None: raise FileNotFoundError(photo_path)
    if quad is not None:
        q = np.float32(quad); wq = int(max(np.linalg.norm(q[1] - q[0]), np.linalg.norm(q[2] - q[3]))); hq = int(max(np.linalg.norm(q[3] - q[0]), np.linalg.norm(q[2] - q[1])))
        rect, H = warp_quad(img, quad, wq, hq); info = {'mode': 'quad', 'H': H.tolist()}
        m = find_module(rect, region)
        if eave_m and eave_m < 7.5:                                   # low house: board cladding is not a storey rhythm
            m.single = True; m.floor_px = float(m.region[3] - m.region[1]); m.y0 = float(m.region[1])
            m.bay_px = float(m.region[2] - m.region[0]); m.x0 = float(m.region[0])   # the whole selected wall section repeats
        m.floor_px *= floor_mul; m.bay_px *= bay_mul
        tile, used, dev = extract_tile(rect, m); cands = []
    else:
        cands = []
        for k, rec in enumerate(rectify_all(img, f_guess)):
            try:
                r = warp(img, rec); mm = find_module(r, region or rec.region); t, u, d = extract_tile(r, mm)
                cover = (mm.region[2] - mm.region[0]) * (mm.region[3] - mm.region[1]) / (r.shape[0] * r.shape[1])
                sc = mm.score_floor * mm.score_bay * (0.5 + cover)
                cands.append((sc, k, rec, r, mm, t, u))
            except ValueError: continue
        if not cands: raise ValueError('no facade with a regular window rhythm')
        cands.sort(key=lambda c: -c[0]); sc, k, rec, rect, m, tile, used = cands[0]
        info = {'mode': 'auto', 'candidate': k, 'score': sc, **{kk: v for kk, v in asdict(rec).items()}, 'alternatives': [
            {'candidate': c[1], 'score': c[0], 'yaw_deg': c[2].yaw_deg, 'floor_px': c[4].floor_px, 'bay_px': c[4].bay_px} for c in cands[1:]]}
        for c in cands[1:]: cv2.imwrite(f"{out_prefix}_alt{c[1]}_rect.jpg", c[3], [cv2.IMWRITE_JPEG_QUALITY, 80])
    cv2.imwrite(out_prefix + '_rect.jpg', rect, [cv2.IMWRITE_JPEG_QUALITY, 88]); cv2.imwrite(out_prefix + '_tile.png', tile)
    meta = {'photo': photo_path, **info, 'module': asdict(m), 'tile_px': list(tile.shape[:2]), 'used': used}
    if eave_m:
        strip, sm = build_strip(tile, eave_m if not m.single or eave_m < 7.5 else eave_m); cv2.imwrite(out_prefix + '_strip.jpg', strip, [cv2.IMWRITE_JPEG_QUALITY, 90]); meta['strip'] = sm
    json.dump(meta, open(out_prefix + '.json', 'w'), indent=1, default=float)
    return meta
