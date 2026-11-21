"""Luvianpuistokatu ja Maamiehenkatu kahdessa tasossa (21.11.2026, omistaja: "pyörätie menee ylemmällä tasolla noin 2m ja autotie kaistoineen
alempana ... Tie on todella kumpurainen pelatessa").

Korkeusmalli on 6 m ruudukko, joten ajoradan ja 2 m ylempänä kulkevan pyörätien väliin jäävä 2-3 m luiska levisi 6 m:n kolmioiksi: ajorata kallistui
reunoiltaan, jalkakäytäväkaista peitti luiskan ja radan sillan kohdalla ajoradalla oli 1,4 m kumpu (laserkeilaus osui siltaan).
Tämä työkalu suunnittelee käytävän pinnan 1 m ruudukkona:
  - ajorata: OSM-ajoratojen (build_roads.py CARR) korkeus = tasoitettu pohja (rataskillan kumpu maskattu pois), poikkileikkaus suora
  - pyörätiet (yläpenger): pyörätien linjan ylemmän reunan korkeus tasoitettuna, 2,5 m kumpaankin suuntaan suora
  - niiden välissä luiska (nurmi, EI jalkakäytävää), muualla liu'utus luonnolliseen maahan 6 m matkalla, käytävän rajalla 15 m
Tulos: tie/tie_data.js (peli: groundTop-koukku, maan ruudukon aukko, oma maapinta) ja tools/roads/tie_rinteet.json (build_roads.py: luiskat pois
jalkakäytävästä, nurmeksi).

usage: python3 tools/roads/tie_luvianpuisto.py REPO roads_geom.pkl osm_ways.json
"""
import sys, json, base64, pickle
import numpy as np
from scipy import ndimage
from shapely.geometry import LineString, Point, Polygon, box, shape
from shapely.ops import unary_union
import shapely

REPO, GEOM, WAYS = sys.argv[1:4]
s = open(REPO + '/terrain.js').read(); T = json.loads(s[s.index('{'):s.rindex('}') + 1])
NX, NY, G, TX0, TY0 = T['nx'], T['ny'], T['g'], T['x0'], T['y0']
HG = np.frombuffer(base64.b64decode(T['hg']), dtype=np.int16).copy()
s = open(REPO + '/rata/rata_data.js').read(); RATA = json.loads(s[s.index('{'):s.rindex('}') + 1])
o = RATA.get('ter', [])
for k in range(0, len(o) - 1, 2): HG[o[k]] = o[k + 1]          # sama kuin 010_maasto.js (ratapenkka)
HG = HG.reshape(NY, NX).astype(np.float64) / 10

def TZg(x, y):
    fx = np.clip((np.asarray(x, float) - TX0) / G, 0, NX - 1.001); fy = np.clip((np.asarray(y, float) - TY0) / G, 0, NY - 1.001)
    i = np.floor(fx).astype(int); j = np.floor(fy).astype(int); u = fx - i; v = fy - j
    return (HG[j, i] * (1 - u) + HG[j, i + 1] * u) * (1 - v) + (HG[j + 1, i] * (1 - u) + HG[j + 1, i + 1] * u) * v

HW, YS = 1012.3, -947.2
def gridTop(x, y, x0, y0, st, dy):
    fx = (x - x0) / st; fy = (y - y0) / st; i = np.floor(fx); j = np.floor(fy); u = fx - i; v = fy - j
    X = lambda a: x0 + a * st; Y = lambda b: y0 + b * st
    z00 = TZg(X(i), Y(j)); z10 = TZg(X(i + 1), Y(j)); z11 = TZg(X(i + 1), Y(j + 1)); z01 = TZg(X(i), Y(j + 1))
    return np.where(u >= v, z00 + (z10 - z00) * u + (z11 - z10) * v, z00 + (z11 - z01) * u + (z01 - z00) * v) + dy
def groundTop0(x, y):   # 060_kadut.js groundTop ilman koukkua
    ti = np.floor((x + 1280) / 512); tj = np.floor((y + 1280) / 512)
    return np.maximum(np.maximum(TZg(x, y), gridTop(x, y, -HW, YS, 6, 0)), gridTop(x, y, -1280 + ti * 512, -1280 + tj * 512, 6, 0.03))

# ---------------------------------------------------------------- käytävä
AXIS = LineString([(-596, -597), (-650, -641), (-705, -696), (-770, -747), (-845, -805), (-837, -830), (-835, -864), (-845, -906), (-852, -940)])
X0, Y0, X1, Y1 = -900, -940, -575, -578          # 1 m ruudukko; etelässä ytimen raja (y -947) ei ylity
RC = AXIS.buffer(42).intersection(box(X0 + 2, Y0 + 3, X1 - 2, Y1 - 2))
nx, ny = X1 - X0, Y1 - Y0
xs = X0 + 0.5 + np.arange(nx); ys = Y0 + 0.5 + np.arange(ny)
XX, YY = np.meshgrid(xs, ys)                      # rivi j = y
def rast(geom):
    from PIL import Image, ImageDraw
    im = Image.new('L', (nx, ny), 0); d = ImageDraw.Draw(im)
    for pg in getattr(geom, 'geoms', [geom]):
        if pg.is_empty or pg.geom_type != 'Polygon': continue
        d.polygon([(x - X0, y - Y0) for x, y in pg.exterior.coords], fill=1)
        for r in pg.interiors: d.polygon([(x - X0, y - Y0) for x, y in r.coords], fill=0)
    return np.array(im, bool)
ZN = groundTop0(XX, YY)
ZG = TZg(XX, YY)
R = rast(RC)

GM = pickle.load(open(GEOM, 'rb'))
WAYS_J = {w['id']: w for w in json.load(open(WAYS))}
CORR_IDS = [4445968, 1094704807, 1094704806, 4445972, 1094704808, 1094704811, 1094704810, 87621717, 5867782, 302861262]   # Luvianpuistokatu, Maamiehenkatu
CARR = GM['CARR'].intersection(RC.buffer(20)).intersection(unary_union([LineString(WAYS_J[i]['g']).buffer(13) for i in CORR_IDS if i in WAYS_J]))   # ei Helsingintien penkereitä eikä ramppeja
MC = rast(CARR) & R

# ---------------------------------------------------------------- ajoradan pohja
RAIL = LineString([(-737, -657), (-689, -749)]).buffer(9)          # rautatiesilta ajoradan yllä: korkeusmallissa kansi -> ei näytteitä
mres = MC & ~rast(RAIL)
zs = ndimage.minimum_filter(np.where(MC, ZG, 99), size=5)          # alustava pohja penkereiden tunnistukseen (luiskan reunat eivät nosta)
zs = np.where(mres & (zs < 90), zs, 0)
def nconv(vals, mask, sig):
    a = ndimage.gaussian_filter(np.where(mask, vals, 0.0), sig, mode='nearest'); b = ndimage.gaussian_filter(mask.astype(float), sig, mode='nearest')
    return a / np.maximum(b, 1e-6), b
ZC, wc = nconv(zs, mres & (zs != 0), 9.0)

# ---------------------------------------------------------------- yläpenkereet (pyörätiet)
W = {w['id']: w for w in json.load(open(WAYS))}
def part(i, a, b):
    L = LineString(W[i]['g']); pa, pb = L.project(Point(a)), L.project(Point(b))
    return shapely.ops.substring(L, min(pa, pb), max(pa, pb))
TER0 = [part(40214524, (-640, -620), (-878, -790)),      # luoteispuoli, Luvianpuistokatu
        part(93630644, (-851, -836), (-882, -975)),      # länsipuoli, Maamiehenkatu (Helsingintien sillan ali)
        part(40320335, (-650, -666), (-766, -767))]      # kaakkoispuoli, radan sillan kohta
TW, SW = 1.75, 2.5                                       # yläpenkereen puolileveys, luiskan leveys (1:1,2 ... 1:1,5)
def zcar(x, y):
    i, j = int(np.clip(x - X0, 0, nx - 1)), int(np.clip(y - Y0, 0, ny - 1)); return ZC[j, i]
# yläreuna: luonnollisen maan suurin arvo 0-2 m pyörätieltä poispäin (6 m ruudukko vetää reunaa alas kohti kaivantoa)
zt = np.full(XX.shape, np.nan); TER = []
for L in TER0:
    n = int(L.length); run = []
    for k in range(n + 1):
        p = L.interpolate(k); q = L.interpolate(min(L.length, k + 1)); r0 = L.interpolate(max(0, k - 1))
        tx, ty = q.x - r0.x, q.y - r0.y; tl = np.hypot(tx, ty) or 1; nxv, nyv = -ty / tl, tx / tl
        c = CARR.boundary.interpolate(CARR.boundary.project(p))
        sgn = 1 if (p.x - c.x) * nxv + (p.y - c.y) * nyv > 0 else -1          # poispäin ajoradasta
        v = max(float(TZg(p.x + nxv * sgn * o, p.y + nyv * sgn * o)) for o in (0, 1, 2))
        ok = RAIL.contains(p) or v - zcar(c.x, c.y) > 0.6                       # vain siellä missä penger on oikeasti ylempänä (ei tasoristeyksiä)
        if ok: run.append((p.x, p.y))
        if (not ok or k == n) and len(run) > 1: TER.append(LineString(run)); run = []
        elif not ok: run = []
        if RAIL.contains(p): continue
        i, j = int(p.x - X0), int(p.y - Y0)
        if 0 <= i < nx and 0 <= j < ny: zt[j, i] = v if np.isnan(zt[j, i]) else max(zt[j, i], v)
TER = [L for L in TER if L.length >= 8]
TERU = unary_union([L.buffer(TW, cap_style='flat') for L in TER0])     # koko pyörätie omalla korkeudellaan (päissä loiva lasku tasoon)
CARR = CARR.difference(unary_union([L.buffer(TW + SW, cap_style='round') for L in TER]))      # ajoradan reuna luiskan alareunaan
MC = rast(CARR) & R
mres = MC & ~rast(RAIL)                                              # lopullinen ajoradan pinta: korkeusmallin näytteet leikatulta ajoradalta
ZC, _ = nconv(np.where(mres, ZG, 0), mres, 9.0)
ZC2, _ = nconv(ZC, MC, 4.0); ZC = np.where(MC, ZC2, ZC)
TS = TERU.intersection(RC)
MT = rast(TS) & R
mk = ~np.isnan(zt)
ZT0, _ = nconv(np.nan_to_num(zt), mk, 8.0)
ZT, _ = nconv(ZT0, MT, 2.0); ZT = np.where(MT, ZT, ZT0)
print('penkereet', [round(L.length) for L in TER])

# ---------------------------------------------------------------- yhdistetään
dC, iC = ndimage.distance_transform_edt(~MC, return_indices=True)
dT, iT = ndimage.distance_transform_edt(~MT, return_indices=True)
zC = ZC[iC[0], iC[1]]; zT = ZT[iT[0], iT[1]]
vCx = XX - XX[iC[0], iC[1]]; vCy = YY - YY[iC[0], iC[1]]; vTx = XX - XX[iT[0], iT[1]]; vTy = YY - YY[iT[0], iT[1]]
between = (~MC) & (~MT) & (dC + dT < SW + 2.5) & (vCx * vTx + vCy * vTy < 0)
sm = lambda t: t * t * (3 - 2 * t)
Z = ZN.copy()
near = np.where(dC <= dT, zC, zT); dn = np.minimum(dC, dT)
Z = near + (ZN - near) * sm(np.clip(dn / 6.0, 0, 1))
Z = np.where(between, (zC * dT + zT * dC) / np.maximum(dC + dT, 1e-6), Z)
Z = np.where(MT, ZT, Z); Z = np.where(MC, ZC, Z)
dR = ndimage.distance_transform_edt(R)
Z = ZN + (Z - ZN) * sm(np.clip(dR / 25.0, 0, 1))
Z = np.where(R, Z, ZN)
B = R & ((np.abs(Z - ZN) > 0.02) | MC)
B = ndimage.binary_dilation(B, iterations=2) & R
SLOPE = between & R & (np.abs(zT - zC) > 0.5)
CUT = unary_union([L.buffer(TW + SW, cap_style='round') for L in TER]).difference(TERU.buffer(-0.05)).difference(CARR.buffer(-0.05))   # build_roads: ei asfalttia eikä jalkakäytävää luiskalle

# ---------------------------------------------------------------- raportti: pituusprofiili ja pystykiihtyvyys 50 km/h
def prof(line, name):
    L = LineString(line); n = int(L.length / 0.5); P = [L.interpolate(k * 0.5) for k in range(n + 1)]
    def zat(p):
        fx = p.x - X0 - 0.5; fy = p.y - Y0 - 0.5; i = int(np.floor(fx)); j = int(np.floor(fy)); u = fx - i; v = fy - j
        return (Z[j, i] * (1 - u) + Z[j, i + 1] * u) * (1 - v) + (Z[j + 1, i] * (1 - u) + Z[j + 1, i + 1] * u) * v
    z = np.array([zat(p) for p in P]); dt = 0.5 / 14
    k = 3; zc = np.array([(z[max(0, i - k)] + z[min(len(z) - 1, i + k)]) / 2 for i in range(len(z))])
    a = np.gradient(np.gradient(zc, dt), dt)
    print(f'{name}: {L.length:.0f} m, z {z.min():.2f}..{z.max():.2f}, |a| max {np.abs(a[10:-10]).max():.2f} m/s2, rms {np.sqrt(np.mean(a[10:-10] ** 2)):.2f}')
    return z
if __name__ == '__main__':
    import os
    OUTD = sys.argv[4] if len(sys.argv) > 4 else '.'
    S = {w['id']: w['g'] for w in W.values()}
    ch = lambda ids: sum([S[i] if k == 0 else S[i][1:] for k, i in enumerate(ids)], [])
    prof(ch([4445968, 1094704807, 1094704806]), 'Luvianpuistokatu lounaaseen')
    prof(ch([4445972, 1094704808, 1094704811, 1094704810, 87621717]), 'Luvianpuistokatu koilliseen')
    prof([q for q in S[302861262] if q[1] > -930], 'Maamiehenkatu')
    # tallennus: rivit (i0, n) ja korkeudet mm
    runs, vals = [], []
    for j in range(ny):
        row = B[j]; i = 0
        while i < nx:
            if not row[i]: i += 1; continue
            i0 = i
            while i < nx and row[i]: i += 1
            runs += [j, i0, i - i0]; vals += list(np.round(Z[j, i0:i] * 1000).astype(np.int16))
    d = {'x0': X0, 'y0': Y0, 'nx': nx, 'ny': ny, 'runs': base64.b64encode(np.array(runs, np.int16).tobytes()).decode(),
         'z': base64.b64encode(np.array(vals, np.int16).tobytes()).decode()}
    os.makedirs(OUTD + '/tie', exist_ok=True)
    open(OUTD + '/tie/tie_data.js', 'w').write('// Luvianpuistokadun ja Maamiehenkadun käytävän pinta 1 m ruudukkona (tools/roads/tie_luvianpuisto.py) – älä muokkaa käsin\nexport default ' + json.dumps(d) + ';\n')
    # luiskat polygoneina build_roads.py:lle
    sp = CUT.simplify(0.2)
    json.dump(shapely.geometry.mapping(sp), open(OUTD + '/tie_rinteet.json', 'w'))
    np.savez_compressed(OUTD + '/tie_dbg.npz', Z=Z, ZN=ZN, B=B, MC=MC, MT=MT, SLOPE=SLOPE, X0=X0, Y0=Y0)
    print('B cells', B.sum(), 'slope m2', round(sp.area), 'data KB', round((len(d['runs']) + len(d['z'])) / 1024))
