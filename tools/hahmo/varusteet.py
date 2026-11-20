# -*- coding: utf-8 -*-
"""Paahahmon laskuvarjovarusteet: python3 tools/hahmo/varusteet.py hahmo.js laskuvarjo/varusteet.js
Rakentaa reppuvaljaat (paa- ja varavarjon reppu, kantohihnat, rintahihna, reisihihnat, lantiohihnat, irtipaastotyyny, varavarjon kahva,
3-rengaslukot, apuvarjon kahva), kyparan, lasit ja rannekorkeusmittarin hahmon PINNAN MUKAAN: hihnojen reitit ammutaan sateina hahmon
lepoasennon verkkoon ja jokainen varustepiste perii osumakohdan luupainot, joten varusteet taipuvat vaatteiden mukana kaikissa animaatioissa.
Tulos on JS-moduuli (base64-taulukot + luiden nimet); laskuvarjo/laskuvarjo.js sitoo sen pelaajan luurankoon nimien perusteella.
Aja uudestaan, jos hahmon verkko tai luusto muuttuu.  pip install numpy"""
import sys, re, json, struct, base64, math
import numpy as np

CT = {5120: ('b', 1), 5121: ('B', 1), 5122: ('h', 2), 5123: ('H', 2), 5125: ('I', 4), 5126: ('f', 4)}
NC = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}

def load(path):
    text = open(path, encoding='utf-8').read()
    b = base64.b64decode(re.search(r'"([A-Za-z0-9+/=]{1000,})"', text).group(1))
    jl = struct.unpack('<I', b[12:16])[0]; j = json.loads(b[20:20 + jl]); o = 20 + jl; bl = struct.unpack('<I', b[o:o + 4])[0]; bn = b[o + 8:o + 8 + bl]
    def acc(i):
        a = j['accessors'][i]; bv = j['bufferViews'][a['bufferView']]; f, sz = CT[a['componentType']]; n = NC[a['type']]
        off = bv.get('byteOffset', 0) + a.get('byteOffset', 0); st = bv.get('byteStride', sz * n)
        if st == sz * n:
            arr = np.frombuffer(bn, dtype='<' + f, count=a['count'] * n, offset=off).reshape(a['count'], n)
        else:
            arr = np.array([np.frombuffer(bn, dtype='<' + f, count=n, offset=off + k * st) for k in range(a['count'])])
        if a.get('normalized'):
            arr = arr.astype(np.float64) / {1: 255.0, 2: 65535.0}[sz]
        return arr
    return j, acc

class Body:
    def __init__(self, path, mats=('Skin', 'TShirt', 'Jeans', 'Shoe')):
        j, acc = load(path); self.j = j
        skin = j['skins'][0]; self.joints = [j['nodes'][i]['name'] for i in skin['joints']]
        par = {}
        for i, n in enumerate(j['nodes']):
            for c in n.get('children', []): par[c] = i
        def world(i):
            n = j['nodes'][i]; r = n.get('rotation', [0, 0, 0, 1]); t = np.array(n.get('translation', [0, 0, 0]), float)
            x, y, z, w = r; R = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
            if i in par:
                PR, PT = world(par[i]); return PR @ R, PT + PR @ t
            return R, t
        self.bone = {j['nodes'][i]['name']: world(i)[1] for i in skin['joints']}
        self.parts = {}
        P, T, J, W = [], [], [], []; base = 0
        for pr in j['meshes'][0]['primitives']:
            nm = j['materials'][pr['material']]['name']
            if nm not in mats: continue
            p = acc(pr['attributes']['POSITION']).astype(float); idx = acc(pr['indices']).reshape(-1, 3).astype(int)
            jj = acc(pr['attributes']['JOINTS_0']).astype(int); ww = acc(pr['attributes']['WEIGHTS_0']).astype(float)
            self.parts[nm] = (base, base + len(idx)); P.append(p); T.append(idx + sum(len(q) for q in P[:-1])); J.append(jj); W.append(ww); base += len(idx)
        self.P = np.vstack(P); self.T = np.vstack(T); self.J = np.vstack(J); self.W = np.vstack(W)
        self.A = self.P[self.T[:, 0]]; self.E1 = self.P[self.T[:, 1]] - self.A; self.E2 = self.P[self.T[:, 2]] - self.A
    def cast(self, o, d, far=True, tmax=1e9, parts=None):
        """Sade o + t d (t > 0): palauttaa (piste, normaali, luupainot) tai None. far=True: kaukaisin osuma (ammutaan sisalta ulos)."""
        o = np.asarray(o, float); d = np.asarray(d, float); d = d / np.linalg.norm(d)
        A, E1, E2 = self.A, self.E1, self.E2
        if parts:
            m = np.zeros(len(A), bool)
            for q in parts: m[self.parts[q][0]:self.parts[q][1]] = True
        else:
            m = np.ones(len(A), bool)
        h = np.cross(d, E2); a = (E1 * h).sum(1); ok = (np.abs(a) > 1e-12) & m
        f = np.where(ok, 1.0 / np.where(ok, a, 1), 0); s = o - A; u = f * (s * h).sum(1); q = np.cross(s, E1); v = f * (q @ d); t = f * (E2 * q).sum(1)
        ok &= (u >= -1e-9) & (v >= -1e-9) & (u + v <= 1 + 1e-9) & (t > 1e-6) & (t < tmax)
        if not ok.any(): return None
        ts = np.where(ok, t, -1 if far else 1e18); k = int(ts.argmax() if far else ts.argmin())
        n = np.cross(E1[k], E2[k]); n /= np.linalg.norm(n) + 1e-12
        if n @ d < 0: n = -n                                  # ulospain = sateen suuntaan (sisalta ammuttaessa)
        if not far: n = -n if n @ d > 0 else n
        w = {}
        for vi, bw in zip(self.T[k], (1 - u[k] - v[k], u[k], v[k])):
            for jn, jw in zip(self.J[vi], self.W[vi]):
                if jw > 0: w[int(jn)] = w.get(int(jn), 0) + bw * jw
        return o + d * t[k], n, w

class Gear:
    def __init__(self, body):
        self.b = body; self.P = []; self.N = []; self.C = []; self.JI = []; self.JW = []; self.I = []
    def v(self, p, n, col, w):
        if isinstance(w, str): w = {self.b.joints.index(w): 1.0}
        it = sorted(w.items(), key=lambda q: -q[1])[:4]; s = sum(q[1] for q in it) or 1
        ji = [q[0] for q in it] + [0] * (4 - len(it)); jw = [q[1] / s for q in it] + [0] * (4 - len(it))
        self.P.append(tuple(p)); self.N.append(tuple(n)); self.C.append(col); self.JI.append(ji); self.JW.append(jw); return len(self.P) - 1
    def quad(self, a, b, c, d): self.I += [a, b, c, a, c, d]
    def tri(self, a, b, c): self.I += [a, b, c]
    def ribbon(self, pts, width, col, lift=0.006, thick=0.004, edge=None):
        """pts: [(piste, normaali, painot)] pinnalla; nauha kulkee pisteiden kautta, leveys nauhan poikki pinnan suuntaisesti."""
        n = len(pts); rows = []
        for i, (p, nn, w) in enumerate(pts):
            t = pts[min(i + 1, n - 1)][0] - pts[max(i - 1, 0)][0]; t = t / (np.linalg.norm(t) + 1e-12)
            s = np.cross(nn, t); s /= np.linalg.norm(s) + 1e-12; nn2 = np.cross(t, s); nn2 /= np.linalg.norm(nn2) + 1e-12
            if nn2 @ nn < 0: nn2 = -nn2
            top = p + nn2 * (lift + thick); bot = p + nn2 * (lift * 0.3)
            ec = edge or tuple(c * 0.6 for c in col)
            rows.append((self.v(top - s * width / 2, nn2, col, w), self.v(top + s * width / 2, nn2, col, w),
                         self.v(top - s * width / 2, -s, ec, w), self.v(bot - s * width / 2, -s, ec, w), self.v(top + s * width / 2, s, ec, w), self.v(bot + s * width / 2, s, ec, w)))
        for a, b in zip(rows, rows[1:]):
            self.quad(a[0], b[0], b[1], a[1]); self.quad(a[3], b[3], b[2], a[2]); self.quad(a[4], b[4], b[5], a[5])
    def box(self, c, ax, ay, az, hx, hy, hz, col, w, bevel=0.0):
        """Laatikko keskipisteessa c, akselit ax ay az (yksikkovektorit), puolimitat."""
        c = np.asarray(c, float); ax, ay, az = (np.asarray(q, float) for q in (ax, ay, az))
        for n, u, v, hn, hu, hv in ((ax, ay, az, hx, hy, hz), (-ax, az, ay, hx, hz, hy), (ay, az, ax, hy, hz, hx), (-ay, ax, az, hy, hx, hz), (az, ax, ay, hz, hx, hy), (-az, ay, ax, hz, hy, hx)):
            q = [self.v(c + n * hn + u * hu * su + v * hv * sv, n, col, w) for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
            self.quad(*q)
    def lathe(self, c, axis, prof, col, w, seg=14, cols=None):
        """Pyorahdyskappale: prof = [(sade, korkeus akselia pitkin)], akseli axis pisteesta c."""
        c = np.asarray(c, float); a = np.asarray(axis, float); a /= np.linalg.norm(a); u = np.cross(a, [0.3, 0.9, 0.1]); u /= np.linalg.norm(u); v = np.cross(a, u)
        rings = []
        for k, (r, h) in enumerate(prof):
            r0, h0 = prof[max(k - 1, 0)]; r1, h1 = prof[min(k + 1, len(prof) - 1)]; dn = np.array([h1 - h0, -(r1 - r0)]); dn /= np.linalg.norm(dn) + 1e-12
            cc = cols[k] if cols else col
            rings.append([self.v(c + a * h + (u * math.cos(t) + v * math.sin(t)) * r, (u * math.cos(t) + v * math.sin(t)) * dn[0] + a * dn[1], cc, w) for t in [2 * math.pi * i / seg for i in range(seg + 1)]])
        for A, B in zip(rings, rings[1:]):
            for i in range(seg): self.quad(A[i], A[i + 1], B[i + 1], B[i])
    def torus(self, c, axis, R, r, col, w, seg=14, tube=6):
        c = np.asarray(c, float); a = np.asarray(axis, float); a /= np.linalg.norm(a); u = np.cross(a, [0.3, 0.9, 0.1]); u /= np.linalg.norm(u); v = np.cross(a, u); rings = []
        for i in range(seg + 1):
            t = 2 * math.pi * i / seg; d = u * math.cos(t) + v * math.sin(t)
            rings.append([self.v(c + d * (R + r * math.cos(s)) + a * r * math.sin(s), d * math.cos(s) + a * math.sin(s), col, w) for s in [2 * math.pi * k / tube for k in range(tube + 1)]])
        for A, B in zip(rings, rings[1:]):
            for k in range(tube): self.quad(A[k], B[k], B[k + 1], A[k + 1])
    def write(self, path, extra):
        b64 = lambda a, t: base64.b64encode(np.asarray(a, t).tobytes()).decode()
        col = np.clip(np.asarray(self.C) * 255, 0, 255)
        out = ("// Laskuvarjovarusteet paahahmolle (tools/hahmo/varusteet.py; hihnat kulkevat hahmon pintaa pitkin ja kayttavat sen luupainoja).\n"
               "// p = paikat (Float32 x3), n = normaalit (Int8 x3 / 127), c = varit (Uint8 x3, sRGB), ji = luut (Uint8 x4, indeksi listaan bones), jw = painot (Uint8 x4 / 255), i = kolmiot (Uint16).\n"
               "export default " + json.dumps({"bones": self.b.joints, "count": len(self.P), "p": b64(self.P, '<f4'), "n": b64(np.round(np.asarray(self.N) * 127), 'i1'), "c": b64(col, 'u1'),
                                                 "ji": b64(self.JI, 'u1'), "jw": b64(np.round(np.asarray(self.JW) * 255), 'u1'), "i": b64(self.I, '<u2'), **extra}, separators=(',', ':')) + ";\n")
        open(path, 'w', encoding='utf-8', newline='').write(out); print('kirjoitettu', path, len(out), 'merkkia;', len(self.P), 'pistetta,', len(self.I) // 3, 'kolmiota')

# ---------------------------------------------------------------------------------------------------------------------------
NAVY, NAVY2, YEL, BLK, WEB, RED, SIL, ORA, LENS, WHT = (0.045, 0.085, 0.22), (0.03, 0.055, 0.15), (0.93, 0.72, 0.10), (0.035, 0.035, 0.04), (0.07, 0.07, 0.08), (0.78, 0.07, 0.06), (0.72, 0.73, 0.75), (0.95, 0.42, 0.05), (0.60, 0.76, 0.86), (0.92, 0.92, 0.90)
AX = 0.035                                                    # vartalon keskiakselin z

def build(src, dst):
    B = Body(src); G = Gear(B); X, Y, Z = np.eye(3)
    T = ('TShirt', 'Jeans', 'Skin')
    def front(x, y): return B.cast((x, y, AX), Z, tmax=0.30, parts=T)
    def back(x, y): return B.cast((x, y, AX), -Z, tmax=0.30, parts=T)
    def tor(az, y):
        a = math.radians(az); return B.cast((0, y, AX), (math.sin(a), 0, math.cos(a)), tmax=0.27, parts=T)
    ok = lambda L: [q for q in L if q is not None]
    anchors = {}
    def dom(w): return B.joints[max(w.items(), key=lambda q: q[1])[0]]
    # --- reppu (paavarjo alhaalla, varavarjo ylhaalla) selassa ---
    nu, nv, x0, y0, y1 = 25, 37, 0.168, 1.035, 1.475
    grid = [[None] * nu for _ in range(nv)]
    for iv in range(nv):
        v = iv / (nv - 1); y = y0 + (y1 - y0) * v
        for iu in range(nu):
            u = -1 + 2 * iu / (nu - 1); wdt = x0 * (1.0 - 0.10 * max(0.0, v - 0.6) / 0.4)      # ylaosa hieman kapeampi
            h = back(u * wdt, y) or back(u * wdt * 0.8, y)
            p, n, w = h
            dep = (0.118 if v < 0.56 else 0.100) - 0.012 * abs(v - 0.3)
            if 0.54 < v < 0.60: dep -= 0.012 * math.sin(math.pi * (v - 0.54) / 0.06)             # sauma paa- ja varavarjon valissa
            edge = (1 - abs(u) ** 5) ** 0.5 * (1 - abs(2 * v - 1) ** 7) ** 0.5
            d = 0.010 + dep * edge
            col = NAVY
            if abs(u) < 0.34 and 0.62 < v < 0.93: col = YEL                                       # varavarjon lappa
            elif abs(u) < 0.40 and 0.10 < v < 0.50: col = NAVY2                                   # paavarjon lappa
            if abs(abs(u) - 0.62) < 0.045 and 0.05 < v < 0.95: col = YEL                          # sivuraidat
            if 0.545 < v < 0.595: col = BLK
            if edge < 0.55: col = BLK
            nn = np.array([u * 0.9 * (1 - edge), (2 * v - 1) * 0.9 * (1 - edge), -1.0]); nn /= np.linalg.norm(nn)
            grid[iv][iu] = G.v(np.array([p[0], p[1], min(p[2], -0.075)]) - Z * d, nn, col, w)
    for iv in range(nv - 1):
        for iu in range(nu - 1): G.quad(grid[iv][iu], grid[iv + 1][iu], grid[iv + 1][iu + 1], grid[iv][iu + 1])
    # --- kantohihnat: reidesta rinnan yli olkapaan paalle ja selkaan repun alle ---
    for s, sd in ((1, 'l'), (-1, 'r')):
        pts = ok([front(s * (0.118 - 0.023 * clamp01((y - 0.90) / 0.44)), y) for y in np.linspace(0.885, 1.335, 16)])
        c = (s * 0.095, 1.345, AX)
        pts += ok([B.cast(c, (0, math.sin(math.radians(t)), math.cos(math.radians(t))), tmax=0.30, parts=T) for t in np.linspace(14, 172, 16)])
        G.ribbon(pts, 0.046, WEB, lift=0.007, thick=0.005)
        r3 = front(s * 0.097, 1.355); G.torus(r3[0] + r3[1] * 0.014, r3[1], 0.021, 0.0045, SIL, r3[2]); G.torus(r3[0] + r3[1] * 0.016 + Y * 0.030, r3[1], 0.013, 0.0035, SIL, r3[2])
        anchors['riser_' + sd] = [float(q) for q in r3[0] + r3[1] * 0.02 + Y * 0.03] + [dom(r3[2])]
        # lantiohihna kantohihnan liitoksesta sivun kautta repun alakulmaan
        G.ribbon(ok([tor(s * a, 1.0 + 0.045 * (a - 34) / 110) for a in np.linspace(34, 146, 14)]), 0.042, WEB, lift=0.007)
        # reisihihna
        h0 = B.bone['thigh_' + sd]; d = B.bone['calf_' + sd] - h0; d /= np.linalg.norm(d); cc = h0 + d * 0.095; u = np.cross(d, Z); u /= np.linalg.norm(u); v = np.cross(d, u)
        ring = ok([B.cast(cc, u * math.cos(t) + v * math.sin(t), tmax=0.17, parts=('Jeans',)) for t in np.linspace(0, 2 * math.pi, 27)])
        G.ribbon(ring, 0.052, WEB, lift=0.006, thick=0.006)
        fr = max(ring, key=lambda q: q[0][2]); G.box(fr[0] + fr[1] * 0.014, fr[1], np.cross(fr[1], d), d, 0.006, 0.024, 0.017, SIL, fr[2])
    # --- rintahihna ja solki ---
    G.ribbon(ok([front(x, 1.318) for x in np.linspace(-0.098, 0.098, 11)]), 0.040, WEB, lift=0.011)
    h = front(0.035, 1.318); G.box(h[0] + h[1] * 0.019, h[1], X, Y, 0.005, 0.020, 0.024, SIL, h[2])
    # --- irtipaastotyyny (oikea, punainen) ja varavarjon kahva (vasen, metalli) ---
    h = front(-0.101, 1.255); G.box(h[0] + h[1] * 0.022, h[1], X, Y, 0.013, 0.026, 0.045, RED, h[2])
    h = front(0.101, 1.250); G.torus(h[0] + h[1] * 0.016, h[1], 0.030, 0.0055, SIL, h[2], seg=4, tube=6)
    # --- apuvarjon kahva repun oikeassa alakulmassa ---
    h = back(-0.118, 1.05); hp = np.array([h[0][0], h[0][1] - 0.035, h[0][2] - 0.085])
    G.lathe(hp, -Y, [(0.0, -0.024), (0.016, -0.019), (0.024, 0.0), (0.016, 0.019), (0.0, 0.024)], ORA, h[2], seg=10)
    anchors['hackey'] = [float(q) for q in hp] + [dom(h[2])]
    h = back(0.0, 1.20); anchors['bag'] = [float(h[0][0]), float(h[0][1]), float(h[0][2] - 0.09)] + [dom(h[2])]
    h = back(0.0, 1.40); anchors['yoke'] = [float(h[0][0]), float(h[0][1]), float(h[0][2] - 0.02)] + [dom(h[2])]
    # --- kypara (avokypara) ---
    hc = np.array([0.0, 1.725, 0.055]); S = ('Skin',)
    def hd(th, ph):
        d = np.array([math.sin(th) * math.sin(ph), math.cos(th), math.sin(th) * math.cos(ph)]); q = B.cast(hc, d, tmax=0.2, parts=S); return (q[0], d) if q else None
    nph, nth = 36, 11; rows = []
    for ip in range(nph + 1):
        ph = 2 * math.pi * ip / nph; a = abs(math.atan2(math.sin(ph), math.cos(ph)))                    # 0 = edessa, pi = takana
        ymin = 1.752 if a < 0.75 else (1.752 + (1.668 - 1.752) * clamp01((a - 0.75) / 0.45) if a < 1.2 else 1.668 + (1.628 - 1.668) * clamp01((a - 1.9) / 1.0))
        lo, hi = 0.2, 2.6
        for _ in range(22):
            mid = (lo + hi) / 2; q = hd(mid, ph)
            if q is None or q[0][1] < ymin: hi = mid
            else: lo = mid
        col = []
        for k in range(nth + 1):
            th = lo * k / nth if k else 0.0; q = hd(max(th, 1e-3), ph); p, d = q
            c = (0.075, 0.08, 0.095)
            if a > 2.45 and 0.25 < k / nth < 0.9: c = YEL                                               # keltainen raita takana
            col.append(G.v(p + d * (0.024 if k < nth else 0.012), d, c, 'head'))
        rows.append(col)
    for A_, B_ in zip(rows, rows[1:]):
        for k in range(nth): G.quad(A_[k], A_[k + 1], B_[k + 1], B_[k])
    # --- lasit ja hihna kyparan ympari ---
    def face(ph, y, lift):
        q = B.cast(np.array([0, y, 0.055]), (math.sin(ph), 0, math.cos(ph)), tmax=0.2, parts=S); return (q[0], np.array([math.sin(ph), 0, math.cos(ph)]), {B.joints.index('head'): 1.0})
    lens = [face(math.radians(a), 1.692, 0) for a in np.linspace(-66, 66, 15)]
    lens = [(p + n * (0.020 - 0.010 * abs(i - 7) / 7), n, w) for i, (p, n, w) in enumerate(lens)]
    G.ribbon(lens, 0.040, LENS, lift=0.0, thick=0.003, edge=BLK)
    G.ribbon([(p + n * 0.030, n, w) for p, n, w in [face(math.radians(a), 1.700, 0) for a in np.linspace(66, 294, 22)]], 0.022, BLK, lift=0.0, thick=0.003)
    # --- korkeusmittari vasemmassa ranteessa ---
    a0, a1 = B.bone['lowerarm_l'], B.bone['hand_l']; d = a1 - a0; L = np.linalg.norm(d); d /= L; cc = a0 + d * L * 0.88; u = np.cross(d, Y); u /= np.linalg.norm(u); v = np.cross(d, u)
    ring = ok([B.cast(cc, u * math.cos(t) + v * math.sin(t), tmax=0.07, parts=S) for t in np.linspace(0, 2 * math.pi, 17)])
    G.ribbon(ring, 0.026, BLK, lift=0.002, thick=0.003)
    top = max(ring, key=lambda q: q[1][1] - 0.6 * q[1][2])                                              # ranteen selkapuoli (ylos-taakse lepoasennossa)
    G.lathe(top[0], top[1], [(0.033, 0.0), (0.033, 0.014), (0.029, 0.018), (0.0, 0.018)], BLK, top[2], seg=16, cols=[BLK, BLK, WHT, WHT])
    G.box(top[0] + top[1] * 0.0195 + d * 0.011, top[1], d, np.cross(top[1], d), 0.0012, 0.011, 0.002, RED, top[2])       # osoitin
    G.write(dst, {"anchors": anchors})

def clamp01(x): return max(0.0, min(1.0, x))

if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2])
