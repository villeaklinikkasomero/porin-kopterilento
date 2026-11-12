import math
from gen import *

def lay(h, mod='punched', gh=0, bw=3.3, fh=3.0, cols=None, P=None, rowP=None, top=None, second=None, plain=False):
    nf = max(1, round((h - gh) / fh)); rows = ([(gh, 'shop', 'G')] if gh else [])
    for f in range(nf):
        if second and f == 0: rows.append((fh, second[0], 'S'))
        elif top and f == nf - 1: rows.append((fh, top[0], 'T'))
        else: rows.append((fh, mod, 'F'))
    rp = dict(rowP or {})
    if second: rp['S'] = second[1]
    if top: rp['T'] = top[1]
    return dict(bw=bw, rows=rows, cols=cols or (lambda c, nb: 'W'), P=P or {}, rowP=rp, plain=plain)

every = lambda k, key, off=1, other='W': (lambda c, nb: key if (c % k == off and nb > 2) else other)
def ends(key, other='W'): return lambda c, nb: key if (c == 0 or c == nb - 1) and nb > 3 else other
SIGNS = [M('#b3202a'), M('#1f4f9a'), M('#f2c230'), M('#1d7a46'), M('#e8e6df'), M('#222326'), M('#e07a1f')]
TILE = M('#a8482f', 0.7); TILE2 = M('#8f3f2c', 0.7); COPPER = M('#6fa893', 0.6); SHEET = M('#4a4f54', 0.5); LIGHTSHEET = M('#9fa5a8', 0.5)
PALW = ['#e3ddcf', '#d6cdb8', '#ece8dd', '#cfc9bd', '#d9d2c2', '#c9c4b8', '#e6dcc4', '#d2d5d3', '#dccfb5', '#bfc2c0']

def auto(i):
    """building with no reference: plausible 1950-80s Pori block by height"""
    b = B[i]; h = b['h']; r = (i * 2654435761 >> 7) % 1000 / 1000; wall = M(PALW[i % len(PALW)])
    P = dict(wall=wall)
    if h < 6.5: return dict(P=P, layout=lay(h, plain=True))
    if h < 13:
        return dict(P=dict(wall=wall, sign=SIGNS), layout=lay(h, 'punched' if r < 0.6 else 'ribbon', gh=0, bw=3.4, fh=3.3, P=dict(ww=1.7)))
    if r < 0.45:
        return dict(P=dict(wall=wall, sign=SIGNS), layout=lay(h, 'punched', gh=3.9, bw=3.5, fh=3.0, cols=every(3, 'B'), P=dict(ww=1.6, rail=M('#d9d9d4'))))
    if r < 0.8:
        return dict(P=dict(wall=wall, sign=SIGNS, spandrel=M(['#6f7b80', '#8a6f5a', '#55606a', '#b9b3a4'][i % 4])), layout=lay(h, 'ribbon', gh=3.9, bw=3.4, fh=3.0, cols=every(4, 'F', 2)))
    return dict(P=dict(wall=wall, sign=SIGNS, rail=M('#70777c'), corr=True), layout=lay(h, 'punched', gh=3.9, bw=3.6, fh=3.0, cols=every(2, 'L'), P=dict(colmod={'L': 'loggia'}, ww=1.5)))

SPEC = {}
# ---------------------------------------------------------------- tori, north side (Pohjoiskauppatori)
TERASTI = M('#b9b5a7'); TERASTI2 = M('#c6c0ae'); STONE_BK = M('#1b1c1e', 0.25); STONE_LG = M('#b9bbb9', 0.4)
# 1728  ent. Kansallis-Osake-Pankki, Pohjoiskauppatori 1 (Strömmer 1954): 7 storeys, vertical raster + black glass to the square,
#       terasti render, black / light grey stone at street level, corner entrance with a rounded canopy
def kop_canopy(Z, pts, h, P):
    # canopy over the corner entrance (SE corner of the building, towards the square and Yrjönkatu)
    c = max(pts, key=lambda p: p[0] * math.cos(GRID) + p[1] * math.sin(GRID) - (-p[0] * math.sin(GRID) + p[1] * math.cos(GRID)))
    r = 3.2; n = 10; ring = [(c[0] + r * math.cos(a * 2 * math.pi / n) - Z.cx, c[1] + r * math.sin(a * 2 * math.pi / n) - Z.cy) for a in range(n)]
    cm = M('#3d3a33', 0.4, 0.5)
    add_solid(Z, [(x, y, 4.15) for x, y in ring], cm, 0.4); add_solid(Z, [(x, y, 3.85) for x, y in ring][::-1], cm, 0.4)
    for k in range(n):
        a, b = ring[k], ring[(k + 1) % n]; add_solid(Z, [(a[0], a[1], 3.85), (b[0], b[1], 3.85), (b[0], b[1], 4.15), (a[0], a[1], 4.15)], cm, 0.5)
_kopP = dict(wall=TERASTI, gwall=STONE_LG, plinth=STONE_BK, fascia=STONE_LG, fasc_h=0.5, gframe=M('#5b4630', 0.4, 0.6), frame=M('#e8e6de'))
SPEC[1728] = dict(P=_kopP, layout=lay(27, 'punched', gh=4.6, bw=3.1, fh=3.2, P=dict(ww=1.35, wh=1.5)),
                  dirs={'S': (lay(27, 'vraster', gh=4.6, bw=2.1, fh=3.2, P=dict(frame=M('#d8d6cf'), nx=1)), 8)},
                  roof=dict(kind='flat', mat=SHEET, pent=(3.0, 2.6)), extra=[kop_canopy])
# 1726  ent. Helsingin Osakepankki, Pohjoiskauppatori 3 (Gripenberg 1956): 7 storeys, smooth render, flat roof, recessed balconies
#       with (now dark) corrugated railings, small windows in white frames, glazed street level, black columns at the corner
_hopP = dict(wall=M('#d8d0bd'), surround=WHITE, rail=M('#3a3f45'), corr=True, linner=M('#e9e4d6'), gwall=M('#2a2b2d', 0.3), plinth=STONE_BK, fascia=M('#d8d0bd'), gframe=ALU, gpier=0.12, fasc_h=0.5)
SPEC[1726] = dict(P=_hopP, layout=lay(27, 'punched', gh=4.4, bw=3.3, fh=3.2, P=dict(ww=1.3, wh=1.4)),
                  dirs={'S': (lay(27, 'punched', gh=4.4, bw=3.4, fh=3.2, cols=lambda c, nb: 'L' if c % 3 != 1 else 'W', P=dict(colmod={'L': 'loggia'}, ww=1.3, wh=1.4)), 8)},
                  roof=dict(kind='flat', mat=SHEET, pent=(3.5, 2.4)))
SPEC[1725] = dict(P=dict(_hopP), layout=lay(10, 'punched', gh=4.4, bw=3.3, fh=2.8, P=dict(ww=1.6, wh=1.4)))      # two-storey shop wing on Antinkatu
SPEC[1727] = dict(P=dict(wall=M('#d8d0bd')), layout=lay(4.7, plain=True))                                           # banking hall in the yard
# 1729/1730  Juseliuksenkulma, Yrjönkatu 7: 3-storey rendered house (Finnilä 1940) + 6-storey block (1961)
SPEC[1730] = dict(P=dict(wall=M('#e9e3d2'), sign=SIGNS, band=M('#f4f1e8')), layout=lay(10, 'punched', gh=3.6, bw=3.2, fh=3.2, P=dict(ww=1.7, wh=1.4, nx=3)))
SPEC[1729] = dict(P=dict(wall=M('#ddd9cd'), sign=SIGNS, spandrel=M('#7d8a8f')), layout=lay(23, 'ribbon', gh=3.9, bw=3.3, fh=3.15, cols=every(4, 'F', 1)), roof=dict(kind='flat', mat=SHEET))
SPEC[1621] = dict(P=dict(wall=M('#d2cdbf'), sign=SIGNS, rail=M('#e4e2da')), layout=lay(20, 'punched', gh=3.9, bw=3.5, fh=3.2, cols=every(3, 'B'), P=dict(ww=1.7)))
SPEC[1731] = dict(P=dict(wall=M('#c9c6bd'), sign=SIGNS, spandrel=M('#5d666c')), layout=lay(12, 'ribbon', gh=4.0, bw=3.6, fh=4.0, P=dict(wh=1.8, sill=1.1)))


# ---------------------------------------------------------------- west of the square, north block (Gallen-Kallelankatu north side ... Valtakatu)
# 1315/1490  ent. Pohjoismaiden Yhdyspankki, Gallen-Kallelankatu 5 (Malmio 1956): white-concrete raster, blue-grey mosaic, recessed balconies on Antinkatu
_pyp = dict(wall=M('#efede6'), panel=M('#7b8e9b', 0.5), rail=M('#e9e7e0'), linner=M('#8597a3'), gwall=M('#3a3d40', 0.3), plinth=STONE_BK, fascia=M('#efede6'), gframe=ALU, sign=SIGNS)
for i in (1315, 1490):
    SPEC[i] = dict(P=_pyp, layout=lay(27, 'punched', gh=4.4, bw=3.2, fh=3.2, P=dict(ww=1.5)),
                   dirs={'E': (lay(27, 'raster', gh=4.4, bw=3.0, fh=3.2, cols=every(3, 'L', 1)), 7), 'S': (lay(27, 'raster', gh=4.4, bw=3.0, fh=3.75), 7), 'N': (lay(27, 'raster', gh=4.4, bw=3.0, fh=3.2), 7)},
                   roof=dict(kind='flat', mat=SHEET))
# 1494  Hotelli Vaakuna, Gallen-Kallelankatu 7 (SOK / Blomstedt 1939): 5 storeys, render, window band on the first floor, recessed balconies at both ends
SPEC[1494] = dict(P=dict(wall=M('#eee8d8'), rail=M('#e2dccb'), gwall=M('#d9d3c4'), plinth=M('#4a4a48'), fascia=M('#eee8d8'), sign=[M('#1d7a46'), M('#e8e6df')], canopy=1.2, canopy_mat=M('#3c4a41')),
                  layout=lay(20, 'punched', gh=4.2, bw=3.1, fh=3.15, second=('ribbon', dict(pier=0.0, wh=1.6, nx=3)), cols=ends('L'), P=dict(colmod={'L': 'loggia'}, ww=1.5, wh=1.4, nx=2)))
# 1366  ent. Porin Seudun Osuuskassa, Gallen-Kallelankatu 9 (Blomstedt & Stenbäck 1952): 6 storeys, render, new wider balconies
SPEC[1366] = dict(P=dict(wall=M('#e4dac3'), rail=M('#d7d9d6'), sign=SIGNS), layout=lay(23, 'punched', gh=4.0, bw=3.3, fh=3.1, cols=every(3, 'B'), P=dict(ww=1.5)), roof=dict(kind='hip', inset=3.2, rise=1.6, mat=SHEET))
SPEC[1364] = dict(P=dict(wall=M('#dcd8cc'), spandrel=M('#8b8f8c'), sign=SIGNS), layout=lay(27, 'ribbon', gh=3.9, bw=3.4, fh=3.2, cols=every(3, 'F', 1)))   # Pohjoispuisto 4 (1962)
# 1361  Sataraudan talo / Vidbominkulma, Valtakatu 10 (Laaksovirta 1940): 5 storeys, render, storey bands along the window rows, bay windows at the corners
SPEC[1361] = dict(P=dict(wall=M('#e3d6b4'), band=M('#f3eedf'), sign=SIGNS, ewall=M('#f0ead9'), gwall=M('#d2c7a8')),
                  layout=lay(23, 'punched', gh=4.2, bw=3.2, fh=3.7, cols=ends('E'), P=dict(colmod={'E': 'erker'}, ww=2.0, wh=1.5, nx=3)), roof=dict(kind='hip', inset=3.5, rise=1.4, mat=SHEET))
SPEC[1367] = dict(P=dict(wall=M('#d8d4c8'), sign=SIGNS, rail=M('#6f777c'), corr=True), layout=lay(23, 'punched', gh=4.0, bw=3.5, fh=3.15, cols=every(2, 'L'), P=dict(colmod={'L': 'loggia'}, ww=1.6)))   # 1961 part (Valli)

# ---------------------------------------------------------------- west of the square, south block (Antinkatu 13-15)
# 1497/1314  Liikekulma, Antinkatu 13 (Ström & Tuomisto 1960): terasti, window bands with dark panels, french balconies; single-storey shops between
_lk = dict(wall=M('#cfcbbd'), sidepanel=0.9, sidemat=M('#3b4147', 0.4), rail=M('#3b4147'), sign=SIGNS, gwall=M('#3f4245', 0.3), fascia=M('#cfcbbd'), gframe=ALU)
SPEC[1497] = dict(P=_lk, layout=lay(23, 'ribbon', gh=4.0, bw=3.6, fh=2.7, cols=every(4, 'F', 2), P=dict(wh=1.35, sill=0.9)), roof=dict(kind='flat', mat=SHEET, pent=(3.0, 2.2)))
SPEC[1314] = dict(P=_lk, layout=lay(23, 'ribbon', gh=4.0, bw=3.6, fh=3.15, cols=every(3, 'F', 1), P=dict(wh=1.4)))
for i in (1313, 1498): SPEC[i] = dict(P=dict(wall=M('#cfcbbd'), sign=SIGNS, gwall=M('#cfcbbd'), gframe=ALU), layout=dict(bw=4.0, rows=[(4.7, 'shop', 'G')], cols=lambda c, nb: 'W', P={}, rowP={}))
# 161  Kehityksen talo, Antinkatu 15 a (Laaksovirta 1939): 5 storeys, render, storey bands, bay window at the north end, shops
SPEC[161] = dict(P=dict(wall=M('#e7dfc8'), band=M('#f5f1e6'), sign=SIGNS, ewall=M('#f1ecdd')),
                 layout=lay(20, 'punched', gh=4.0, bw=3.1, fh=3.2, P=dict(ww=1.8, wh=1.45, nx=3)),
                 dirs={'E': lay(20, 'punched', gh=4.0, bw=3.1, fh=3.2, cols=lambda c, nb: 'E' if c == nb - 1 else ('S' if c == nb // 2 else 'W'), P=dict(colmod={'E': 'erker'}, ww=1.8, wh=1.45, nx=3))},
                 roof=dict(kind='hip', inset=3.0, rise=1.2, mat=SHEET))
# 163  ent. Porin Säästöpankki, Antinkatu 15 b (Strömmer 1935/1953): render, granite at the entrance, copper-clad balconies
SPEC[163] = dict(P=dict(wall=M('#d9d2c0'), rail=COPPER, slab=COPPER, gwall=M('#8a7f78', 0.4), plinth=M('#5e5552', 0.4), sign=SIGNS),
                 layout=lay(23, 'punched', gh=4.4, bw=3.3, fh=3.1, cols=every(4, 'B', 1), P=dict(ww=1.5, wh=1.5)), roof=dict(kind='hip', inset=3.0, rise=1.3, mat=COPPER))

# ---------------------------------------------------------------- south of the square (Eteläkauppatori ... Itäpuisto)
# 604  Torilinna, Eteläkauppatori 4 (Tähtinen 1936, raised 1987): plain rendered functionalism, three lower storeys on top
_tl = dict(wall=M('#f0ece2'), sign=SIGNS, gframe=M('#6b4a2c', 0.5), gwall=M('#e4dfd3'))
SPEC[604] = dict(P=_tl, layout=dict(bw=3.2, rows=[(4.0, 'shop', 'G')] + [(3.4, 'punched', 'F')] * 3 + [(2.9, 'punched', 'T')] * 3, cols=lambda c, nb: 'W', P=dict(ww=1.7, wh=1.5, nx=3),
                                    rowP={'T': dict(ww=1.5, wh=1.2, nx=2, sill=0.9, wall=M('#e6e2d8'))}), roof=dict(kind='flat', mat=SHEET))
# 603  Eteläkauppatori 2 (1961)
SPEC[603] = dict(P=dict(wall=M('#e2dfd6'), spandrel=M('#5f6f7a', 0.5), sign=SIGNS, gwall=M('#35383b', 0.3), fascia=M('#e2dfd6'), gframe=ALU), layout=lay(30, 'ribbon', gh=4.2, bw=3.3, fh=3.2, cols=every(4, 'F', 1)), roof=dict(kind='flat', mat=SHEET, pent=(3.0, 2.4)))
# 564  Kansankulma, Antinkatu 14 (Karhulahti 1954): terasti, band of large windows on the first floor, small two-pane windows above, stone-clad street level
SPEC[564] = dict(P=dict(wall=TERASTI2, gwall=M('#9c9a92', 0.4), plinth=M('#6d6b66', 0.4), sign=SIGNS),
                 layout=lay(23, 'punched', gh=4.0, bw=2.9, fh=3.15, second=('ribbon', dict(wh=1.7, sill=0.8, nx=3, pier=0.15)), P=dict(ww=1.25, wh=1.35, nx=2)), roof=dict(kind='hip', inset=3.2, rise=1.5, mat=SHEET))
# 637  As.oy Itäpuisto 5 (Valli 1955): terasti, bay windows with brown clinker, hipped tile roof, red mosaic at street level
SPEC[637] = dict(P=dict(wall=TERASTI2, epanel=M('#6e4a35', 0.5), gwall=M('#9a3b30', 0.4), plinth=M('#5a2a25', 0.4), sign=SIGNS, fascia=TERASTI2),
                 layout=lay(23, 'punched', gh=3.9, bw=3.3, fh=3.15, cols=every(3, 'E', 1), P=dict(colmod={'E': 'erker'}, ww=1.5, wh=1.4, edepth=0.6)), roof=dict(kind='hip', inset=4.2, rise=2.6, mat=TILE))
SPEC[641] = dict(P=dict(wall=M('#e9dfc4'), band=M('#f4efe2'), sign=SIGNS), layout=lay(10, 'punched', gh=3.8, bw=3.0, fh=3.1, P=dict(ww=1.3, wh=1.6)))   # 1928 two-storey house

# ---------------------------------------------------------------- east of the square (Yrjönkatu east side)
# 602  Yrjönkymppi, ent. Porin Suomalainen Säästöpankki, Yrjönkatu 10 (Schreck 1954-55): 7 storeys, terasti, steep tiled saddle roof
SPEC[602] = dict(P=dict(wall=M('#cfc7b2'), rail=M('#b9b5a8'), gwall=M('#8f8b80', 0.4), plinth=STONE_BK, sign=SIGNS, fasc_h=1.0),
                 layout=lay(27, 'punched', gh=5.2, bw=3.2, fh=3.1, cols=every(4, 'B', 2), P=dict(ww=1.45, wh=1.45)), roof=dict(kind='hip', inset=5.6, rise=6.5, mat=TILE, ov=0.5))
SPEC[1599] = dict(P=dict(wall=M('#dedad0'), spandrel=M('#6a7479', 0.5), sign=SIGNS, gwall=M('#3a3d40', 0.3), fascia=M('#dedad0'), gframe=ALU), layout=lay(30, 'ribbon', gh=4.2, bw=3.4, fh=3.2, cols=every(3, 'F', 1)))
# Hallitalo (Viljanen): 1217 Hellmanin pilvenpiirtäjä 1927 (classicist, 5 storeys), 1218 funkis wing 1938 (shop windows, window band above)
SPEC[1217] = dict(P=dict(wall=M('#e2d3a4'), band=M('#f2ecd8'), sign=SIGNS, gwall=M('#d5c697')), layout=lay(20, 'punched', gh=4.2, bw=2.8, fh=3.15, P=dict(ww=1.15, wh=1.7, nx=2, band2=False)), roof=dict(kind='hip', inset=3.5, rise=2.2, mat=SHEET), cornice=(0.35, 0.4, M('#f2ecd8')))
SPEC[1218] = dict(P=dict(wall=M('#f1eee6'), sign=SIGNS, gframe=DARK, gwall=M('#f1eee6')), layout=lay(10, 'ribbon', gh=4.6, bw=3.4, fh=5.0, P=dict(wh=1.9, sill=1.3, nx=3, pier=0.1)))
SPEC[1219] = dict(P=dict(wall=M('#e9e7e1'), spandrel=M('#3d4347', 0.4), sign=SIGNS, gwall=M('#2f3235', 0.3), gframe=ALU, rail=M('#a9b4ba', 0.3)), layout=lay(23, 'ribbon', gh=4.2, bw=3.6, fh=3.1, cols=every(2, 'F')))


# ---------------------------------------------------------------- BePOP (Nurmela-Raimoranta-Tasa 1989)
# bluish terrazzo elements, lively changing window rhythm, monumental canopy over the entrance at the end of the pedestrian street,
# curved glass-roofed gallery through the block, round tower piercing the glass roof (positions measured from the aerial image)
import numpy as _np
def _bid(x, y):
    for i in range(len(B)):
        pts = poly(i)[0]; ins = False
        for k in range(len(pts)):
            a, b = pts[k], pts[(k + 1) % len(pts)]
            if (a[1] > y) != (b[1] > y) and x < (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]: ins = not ins
        if ins: return i
BEPOP = _bid(58.3, -382.3); UIMA = _bid(567.6, -660.3)
BP_H = 17.0
def _ring(cx, cy, r, n): return [(cx + r * math.cos(a * 2 * math.pi / n), cy + r * math.sin(a * 2 * math.pi / n)) for a in range(n)]
def bepop_extra(Z, pts, h, P):
    L = lambda x, y, z: (x - Z.cx, y - Z.cy, z)
    # gallery glass roof: circle fitted through the middle of the glass band in the aerial image
    Mp = _np.array([(41, -353), (46.4, -376), (67.1, -393.3), (96.4, -401.9)], float)
    A = _np.c_[2 * Mp, _np.ones(4)]; sol = _np.linalg.lstsq(A, (Mp ** 2).sum(1), rcond=None)[0]; cx, cy = sol[0], sol[1]; R = math.sqrt(sol[2] + cx * cx + cy * cy)
    a0 = math.atan2(Mp[0][1] - cy, Mp[0][0] - cx); a1 = math.atan2(Mp[-1][1] - cy, Mp[-1][0] - cx)
    if a1 < a0: a1 += 2 * math.pi
    if a1 - a0 > math.pi: a0, a1 = a1, a0 + 2 * math.pi
    N, J, hw, rise = 26, 6, 5.6, 3.6; g1 = M((0.05, 0.36, 0.38), 0.12); g2 = M((0.07, 0.44, 0.46), 0.12); rib = M('#e9eef0')
    def pt(i, j):
        a = a0 + (a1 - a0) * i / N; f = math.pi * j / J; r = R + hw * math.cos(f); return L(cx + r * math.cos(a), cy + r * math.sin(a), h + 0.4 + rise * math.sin(f))
    for i in range(N):
        for j in range(J): add_solid(Z, [pt(i, j), pt(i + 1, j), pt(i + 1, j + 1), pt(i, j + 1)], g1 if (i + j) % 2 else g2, 0.45)
    for i in (0, N): add_solid(Z, [pt(i, j) for j in range(J + 1)], rib, 0.4)
    for j in (0, J):                                                      # kerb under the glass
        for i in range(N):
            a, b = pt(i, j), pt(i + 1, j); add_solid(Z, [(a[0], a[1], h), (b[0], b[1], h), (b[0], b[1], h + 0.45), (a[0], a[1], h + 0.45)], rib, 0.3)
    # round tower through the glass roof, bank offices fan out around it
    tw = dict(wall=M('#e8edf0'), frame=M('#1f4a4f'), joints=M('#8f9ea8'))
    ring = _ring(55.0, -375.5, 5.4, 18)
    for k in range(18): build_wall(Z, ring[k], ring[(k + 1) % 18], h, h + 9.6, dict(bw=1.9, rows=[(3.2, 'punched', 'F')] * 3, cols=lambda c, nb: 'W', P=dict(ww=1.05, wh=1.5, nx=1, sill=0.9), rowP={}), tw, 900 + k, 0)
    add_solid(Z, [L(x, y, h + 9.6) for x, y in ring], M('#5d6d78', 0.5), 0.3)
    hat = _ring(55.0, -375.5, 6.5, 18)
    add_solid(Z, [L(x, y, h + 9.9) for x, y in hat], M('#e9eef0'), 0.3); add_solid(Z, [L(x, y, h + 9.6) for x, y in hat][::-1], M('#e9eef0'), 0.3)
    for k in range(18):
        a, b = hat[k], hat[(k + 1) % 18]; add_solid(Z, [L(a[0], a[1], h + 9.6), L(b[0], b[1], h + 9.6), L(b[0], b[1], h + 9.9), L(a[0], a[1], h + 9.9)], M('#e9eef0'), 0.4)
    small = _ring(36.5, -379.8, 2.7, 12)
    for k in range(12):
        a, b = small[k], small[(k + 1) % 12]; add_solid(Z, [L(a[0], a[1], h), L(b[0], b[1], h), L(b[0], b[1], h + 3.4), L(a[0], a[1], h + 3.4)], M('#e8edf0'), 0.4)
    add_solid(Z, [L(x, y, h + 3.4) for x, y in small], M('#5d6d78', 0.5), 0.3)
    # monumental entrance canopy at the north-west corner
    c, s_ = math.cos(GRID), math.sin(GRID); ox, oy = 33.0, -350.5; G = lambda u, v, z: L(ox + u * c - v * s_, oy + u * s_ + v * c, z)
    wh_ = M('#f2f4f4'); red = M('#c23a2e')
    def box(u0, v0, u1, v1, z0, z1, m, dn=0.5):
        add_solid(Z, [G(u0, v0, z1), G(u1, v0, z1), G(u1, v1, z1), G(u0, v1, z1)], m, dn); add_solid(Z, [G(u0, v1, z0), G(u1, v1, z0), G(u1, v0, z0), G(u0, v0, z0)], m, dn)
        add_solid(Z, [G(u0, v0, z0), G(u1, v0, z0), G(u1, v0, z1), G(u0, v0, z1)], m, dn); add_solid(Z, [G(u1, v0, z0), G(u1, v1, z0), G(u1, v1, z1), G(u1, v0, z1)], m, dn)
        add_solid(Z, [G(u1, v1, z0), G(u0, v1, z0), G(u0, v1, z1), G(u1, v1, z1)], m, dn); add_solid(Z, [G(u0, v1, z0), G(u0, v0, z0), G(u0, v0, z1), G(u0, v1, z1)], m, dn)
    box(-7.5, -6.5, 7.5, 6.5, 14.2, 15.1, wh_); box(-7.62, -6.62, 7.62, 6.62, 14.45, 14.8, red, 0.4)
    for u, v in ((-6.6, 5.6), (-6.6, -0.5), (0.5, 5.6)): box(u - 0.35, v - 0.35, u + 0.35, v + 0.35, 0, 14.2, wh_, 0.6)
_bpP = dict(wall=M('#b6c8d6'), frame=M('#1f4a4f'), joints=M('#7f95a3'), spandrel=M('#a3b8c6'), gwall=M('#8ea5b4'), plinth=M('#4d5f6b', 0.4), fascia=M('#6f8a9c'), gframe=M('#1f4a4f'), sign=SIGNS, rail=M('#c23a2e'))
_bpat = 'WWRRRWNWTTWRRWWNWWRRRRWTWNW'
SPEC[BEPOP] = dict(h=BP_H, P=_bpP, layout=lay(BP_H, 'punched', gh=4.6, bw=3.0, fh=4.1, cols=lambda c, nb: _bpat[(c + nb) % len(_bpat)],
                   P=dict(colmod={'R': 'ribbon', 'N': 'plain'}, ww=1.5, wh=1.5, nx=2, sill=1.1, wh2=1), rowP={}), cornice=(0.18, 0.55, M('#5f7f93')), extra=[bepop_extra])

# ---------------------------------------------------------------- Keskustan uimahalli (appearance inferred from the aerial image only)
def uima_extra(Z, pts, h, P):
    L = lambda x, y, z: (x - Z.cx, y - Z.cy, z)
    cx, cy, R, r = 594.6, -623.4, 4.2, 0.62; blue = M('#2f86c8', 0.4); N = 44; turns = 2.3; z0, z1 = 10.2, 1.4
    def ring(i):
        t = i / N; a = t * turns * 2 * math.pi; ctr = (cx + R * math.cos(a), cy + R * math.sin(a), z0 + (z1 - z0) * t); rad = (math.cos(a), math.sin(a))
        return [L(ctr[0] + rad[0] * r * math.cos(b * math.pi / 3), ctr[1] + rad[1] * r * math.cos(b * math.pi / 3), ctr[2] + r * math.sin(b * math.pi / 3)) for b in range(6)]
    rs = [ring(i) for i in range(N + 1)]
    for i in range(N):
        for b in range(6): add_solid(Z, [rs[i][b], rs[i + 1][b], rs[i + 1][(b + 1) % 6], rs[i][(b + 1) % 6]], blue, 0.5)
    tw = _ring(cx, cy, 1.5, 8); g = M('#c9cdcf')
    for k in range(8):
        a, b = tw[k], tw[(k + 1) % 8]; add_solid(Z, [L(a[0], a[1], 0), L(b[0], b[1], 0), L(b[0], b[1], 11.5), L(a[0], a[1], 11.5)], g, 0.4)
    add_solid(Z, [L(x, y, 11.5) for x, y in tw], g, 0.3)
_uP = dict(wall=M('#e6e8e5'), frame=M('#59636b', 0.5, 0.4), spandrel=M('#e6e8e5'), band=None)
SPEC[UIMA] = dict(h=11.5, P=_uP, layout=lay(11.5, 'ribbon', bw=4.2, fh=3.8, P=dict(sill=2.3, wh=0.9, nx=3)),
                  dirs={'W': (lay(11.5, 'ribbon', bw=4.0, fh=5.75, P=dict(sill=0.5, wh=4.6, nx=3, pier=0.25)), 14), 'S': (lay(11.5, 'ribbon', bw=4.0, fh=5.75, P=dict(sill=0.5, wh=4.6, nx=3, pier=0.25)), 14)},
                  cornice=(0.2, 0.8, M('#4f5a62')), extra=[uima_extra])

# ---------------------------------------------------------------- Yrjönkadun eteläpää (Itsenäisyydenkadun kulma) and Keskuskartano
# Sources: Y-pakki / Satakunnan Museo inventory texts (2018), Porin ruutukaavakeskustan inventointi 2019, MML LoD2 heights, user photos.
def _clip_south(pts, a, b):
    """part of a footprint on the right-hand side of the line a->b (the street side of an L-shaped plan)"""
    from shapely.geometry import Polygon as _P
    dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy); nx, ny = dy / L, -dx / L; F = 400
    half = _P([(a[0] - dx / L * F, a[1] - dy / L * F), (b[0] + dx / L * F, b[1] + dy / L * F), (b[0] + dx / L * F + nx * F, b[1] + dy / L * F + ny * F), (a[0] - dx / L * F + nx * F, a[1] - dy / L * F + ny * F)])
    g = _P(pts).buffer(0).intersection(half)
    g = max(getattr(g, 'geoms', [g]), key=lambda q: q.area)
    c = list(g.exterior.coords)[:-1]
    if _P(c).exterior.is_ccw != _P(pts).exterior.is_ccw: c = c[::-1]
    return c

def _upper_block(line, H, lay_by_dir, P, cap):
    """taller street-side part of an L-shaped building: walls from the wing's eave up to H on the street-side strip, flat roof on top"""
    def extra(Z, pts, h, P_):
        part = _clip_south(pts, *line); n = len(part); Lz = lambda x, y, z: (x - Z.cx, y - Z.cy, z)
        for k in range(n):
            p, q = part[k], part[(k + 1) % n]; dx, dy = q[0] - p[0], q[1] - p[1]; L = math.hypot(dx, dy)
            if L < 0.3: continue
            d = gdir((dy / L, -dx / L)); build_wall(Z, p, q, h, H, lay_by_dir.get(d) or lay_by_dir['*'], P, 977 + k, 0)
        Z.hi.append(([Lz(x, y, H - 0.01) for x, y in part], P['wall']))
        add_solid(Z, [Lz(x, y, H + 0.03) for x, y in part], cap, 0.25)
        po = offset(part, 0.25)                                            # coping round the roof edge
        for k in range(n):
            a, b = part[k], part[(k + 1) % n]; c, d = po[(k + 1) % n], po[k]
            if math.hypot(b[0] - a[0], b[1] - a[1]) < 0.3: continue
            add_solid(Z, [Lz(d[0], d[1], H - 0.35), Lz(c[0], c[1], H - 0.35), Lz(c[0], c[1], H + 0.12), Lz(d[0], d[1], H + 0.12)], P.get('coping', DARK), 0.4)
    return extra

# Itsenäisyydenkatu 37, Hotelli Bepop (ent. Cumulus; Matti Salmivalli 1974): 6-storey part on Itsenäisyydenkatu, 3+1-storey wing on Yrjönkatu
# (extra storey 1982); light brown clinker tiles, dark ribbon windows on floors 2-3, recessed glazed balconies on 4-6, shopfronts under
# the projecting upper floors.  Its footprint lay under the LoD2 model of BePOP and was never drawn: it is built here, in the bepop block.
HOTBP = _bid(10.0, -430.0); MAAKL = _bid(80.0, -462.0)
_klink = MT('#bfae86', 'brick', 0.8)
_hbP = dict(wall=_klink, spandrel=_klink, frame=M('#2b2d30', 0.5), gwall=M('#2e3134', 0.4), plinth=M('#2c2e31'), fascia=_klink, gframe=M('#2b2d30', 0.5),
            sign=SIGNS, rail=M('#9fb0b8', 0.15), linner=M('#d9d2bf'), coping=M('#6d6a62', 0.5, 0.3))
_hbRib = dict(sill=0.95, wh=1.45, pier=0.0, nx=3)
_hbLog = dict(colmod={'L': 'loggia'}, ldepth=1.2, lpier=0.2)
def _hb_lay(rows, cols=None, P=None): return dict(bw=3.2, rows=rows, cols=cols or (lambda c, nb: 'W'), P=P or _hbRib, rowP={'L': dict(_hbLog, colmod={'W': 'loggia'})})
_HB_WING = 14.4; _HB_TOP = 21.2
SPEC[HOTBP] = dict(h=_HB_WING, P=_hbP,
                   layout=_hb_lay([(4.2, 'shop', 'G'), (3.4, 'ribbon', 'F'), (3.4, 'ribbon', 'F'), (3.4, 'ribbon', 'F')]),
                   dirs={'S': _hb_lay([(4.2, 'shop', 'G'), (3.4, 'ribbon', 'F'), (3.4, 'ribbon', 'F'), (3.4, 'ribbon', 'L')]),
                         'E': (_hb_lay([(4.2, 'shop', 'G'), (10.2, 'plain', 'P')]), 0)},
                   roof=dict(kind='flat', mat=M('#4a4d50', 0.6)),
                   extra=[_upper_block(((20.5, -440.7), (52.5, -448.3)), _HB_TOP,
                                       {'S': _hb_lay([(3.4, 'ribbon', 'L'), (3.4, 'ribbon', 'L')]), 'E': dict(bw=3, rows=[(6.8, 'plain', 'P')], cols=lambda c, nb: 'W', P={}, rowP={}, plain=True),
                                        'W': _hb_lay([(3.4, 'ribbon', 'L'), (3.4, 'ribbon', 'F')]), '*': _hb_lay([(3.4, 'ribbon', 'F'), (3.4, 'ribbon', 'F')])},
                                       _hbP, M('#4a4d50', 0.6))])
# Itsenäisyydenkatu 35, Maakuntalinna (Veikko Malmio 1959): 6 storeys with a tall shop floor on Itsenäisyydenkatu, 2-storey wing towards
# Isolinnankatu; clad in white sheet metal since 1981 / 2000
_mlP = dict(wall=M('#e6e7e3', 0.5, 0.15), frame=M('#3a3d40', 0.5), gwall=M('#2e3134', 0.4), plinth=M('#2c2e31'), fascia=M('#d9dbd8', 0.5, 0.15), gframe=ALU, sign=SIGNS,
            joints=M('#b9bcbc', 0.5, 0.2), coping=M('#b9bcbc', 0.5, 0.3))
_ML_WING = 8.6; _ML_TOP = 22.2
_mlL = lambda rows: dict(bw=3.0, rows=rows, cols=lambda c, nb: 'W', P=dict(ww=1.6, wh=1.45, sill=0.85, nx=2), rowP={})
SPEC[MAAKL] = dict(h=_ML_WING, P=_mlP, layout=_mlL([(5.0, 'shop', 'G'), (3.6, 'punched', 'F')]), roof=dict(kind='flat', mat=M('#55585b', 0.6)),
                   extra=[_upper_block(((52.2, -449.3), (71.9, -453.7)), _ML_TOP, {'*': _mlL([(3.4, 'punched', 'F')] * 4)}, _mlP, M('#55585b', 0.6))])

# Yrjönkatu 23, Palojoenkulma (Mikael Küttner 1988): yellowish brown brick, ribbon windows on floors 2-6, shopfronts on Itsenäisyydenkatu,
# 6-storey part on Itsenäisyydenkatu, 3-storey wing on Yrjönkatu (heights from the LoD2 shell)
PALO = _bid(-30.0, -430.0)
_paW = MT('#c89f62', 'brick', 0.8)
_paP = dict(wall=_paW, spandrel=_paW, frame=M('#33312d', 0.5), gwall=M('#2f3134', 0.4), plinth=M('#3a3a38'), fascia=_paW, gframe=M('#33312d', 0.5), sign=SIGNS)
def _pa_fit(lay_, H, street, L, zb):
    gh = 4.0 if zb < 1.5 and H > 6 else 0.0; n = max(1, round((H - gh) / 3.35)); fh = (H - gh) / n
    rows = ([(gh, 'shop' if street else 'ribbon', 'G')] if gh else []) + [(fh, 'ribbon', 'F')] * n
    return dict(bw=3.0, rows=rows, cols=lambda c, nb: 'W', P=dict(sill=0.95, wh=1.45, pier=0.0, nx=3), rowP={})
SPEC[PALO] = dict(P=_paP, layout=_pa_fit(None, 21.4, True, 30, 0), fitw=_pa_fit)

# Keskusaukio 2, Keskuskartano (Charles Hagan 1962; Pori's first high-rise, Hotel Amado in the 3-storey annexe): 101 m slab, 11 storeys over
# a shop floor; white slab bands, a window and a dark grey panel in turn between them, grey sheet-metal gable ends; top floor rebuilt after
# the 2019 fire with a darker window band.  Heights from the LoD2 shell: slab 34.5 m, annexe 10.8 m, single-storey shops 4.3 m.
KKART = _bid(10.0, -590.0)
_kkP = dict(wall=M('#6a6f74', 0.6), spandrel=M('#f2f2ee'), frame=M('#e6e6e1'), gwall=M('#34373a', 0.4), plinth=M('#2c2e31'), fascia=M('#3d4044'), gframe=ALU, sign=SIGNS)
_kkGable = M('#9a9ea1', 0.45, 0.35)
def _kk_fit(lay_, H, street, L, zb):
    if H > 20 and L < 18 and zb < 1.5:                                      # gable end: sheet metal, no windows
        return dict(bw=3.0, rows=[(H, 'plain', 'P')], cols=lambda c, nb: 'W', P=dict(wall=_kkGable), rowP={}, plain=True)
    if H > 20 or zb > 3:                                                     # the slab
        gh = 3.9 if zb < 1.5 else 0.0; n = max(1, round((H - gh) / 2.85)); fh = (H - gh) / n
        rows = ([(gh, 'shop', 'G')] if gh else []) + [(fh, 'ribbon', 'F')] * (n - 1) + [(fh, 'ribbon', 'T')]
        return dict(bw=2.6, rows=rows, cols=lambda c, nb: 'W', P=dict(sill=1.1, wh=fh - 1.18, pier=0.5, nx=1),
                    rowP={'T': dict(spandrel=M('#d9dadb'), frame=M('#2c2e31'), pier=0.15, nx=3)})
    if H > 7:                                                                # annexe: shops, Hotel Amado above
        n = max(1, round((H - 4.3) / 3.25)); fh = (H - 4.3) / n
        return dict(bw=3.2, rows=[(4.3, 'shop', 'G')] + [(fh, 'ribbon', 'F')] * n, cols=lambda c, nb: 'W',
                    P=dict(wall=M('#d6d3cb'), spandrel=M('#d6d3cb'), frame=M('#2f3235', 0.5), sill=0.9, wh=1.4, pier=0.3, nx=2), rowP={})
    return dict(bw=3.6, rows=[(H, 'shop', 'G')], cols=lambda c, nb: 'W', P={}, rowP={})
SPEC[KKART] = dict(P=_kkP, layout=_kk_fit(None, 34.5, True, 100, 0), fitw=_kk_fit)


# ---------------------------------------------------------------- BePOP on its measured LoD2 shell (MML Rakennukset 3D)
# The LoD2 model of the block (one building in MML) holds BePOP, the 4-storey parking hall, Hotelli Bepop and Maakuntalinna with their real
# heights and roofs (glass vault 15-23 m, tower 27 m, entrance canopy 24-25 m).  Walls take the spec of the building they belong to;
# the vault faces are glass, the canopy white, the round tower is drawn by hand where the scan has a square one.
# Looks: Y-pakki photos and text (Satakunnan Museo 2018), finnisharchitecture.fi / DOCOMOMO: pale blue mosaic concrete, triangular and
# trapezoid openings, white canopy on slender columns at the Yrjönkatu entrance, green-framed glazed entrance, round tower through the vault.
from shapely.geometry import Polygon as _SP, Point as _SPt
_BP_CAN = _SP([(27.5, -348.4), (37.3, -350.7), (35.0, -360.6), (25.2, -358.3)])
_BP_TW = (52.0, -375.9); _BP_TWR = 5.6
_BP_HOT = _SP(poly(HOTBP)[0]).buffer(0.8); _BP_ML = _SP(poly(MAAKL)[0]).buffer(0.8)
_bpG = M('#cfe3d8', 0.08)                              # vault glass, light green-blue tint as in the aerial image
_bpGlz = dict(P=dict(wall=M('#3d7f5c', 0.4, 0.3), frame=M('#3d7f5c', 0.4, 0.3), panel=M((0.05, 0.16, 0.12), 0.08), gwall=M('#3d7f5c', 0.4, 0.3)))

def _strip(mb, a, b, w, d, mat):
    """flat bar from a to b (u, v) in the facade tile, CCW"""
    du, dv = b[0] - a[0], b[1] - a[1]; L = math.hypot(du, dv) or 1; nu, nv = -dv / L * w / 2, du / L * w / 2
    mb.hq([(a[0] - nu, a[1] - nv, d), (b[0] - nu, b[1] - nv, d), (b[0] + nu, b[1] + nv, d), (a[0] + nu, a[1] + nv, d)], mat)
def m_tri(mb, col, P):
    """BePOP: inverted triangular window under the eaves (white tile wall, dark frame, green-tinted glass)"""
    bw, fh, W = mb.bw, mb.fh, P['wall']; mb.wall([], W)
    if col == 'N': return
    m, top, tip = 0.3, fh - 0.35, max(0.3, fh * 0.12)
    mb.hq([(bw / 2, tip, 0.01), (bw - m, top, 0.01), (m, top, 0.01)], P.get('frame', DARK))
    mb.hq([(bw / 2, tip + 0.22, 0.02), (bw - m - 0.17, top - 0.1, 0.02), (m + 0.17, top - 0.1, 0.02)], M((0.12, 0.3, 0.24), 0.1))
def m_diamond(mb, col, P):
    """BePOP entrance hall: glass behind a diagonal (diamond) lattice of light green bars"""
    bw, fh = mb.bw, mb.fh; fr = P.get('frame', M('#cfe0d6', 0.4, 0.3)); gl = P.get('panel', M((0.06, 0.16, 0.13), 0.08))
    mb.q(0, 0, bw, fh, -0.2, gl)
    mb.sides(0, 0, bw, fh, 0, -0.2, fr)
    _strip(mb, (0, 0), (bw, fh), 0.09, -0.12, fr); _strip(mb, (bw, 0), (0, fh), 0.09, -0.12, fr)
    _strip(mb, (0, fh / 2), (bw / 2, fh), 0.06, -0.13, fr); _strip(mb, (bw / 2, 0), (bw, fh / 2), 0.06, -0.13, fr)
    _strip(mb, (bw, fh / 2), (bw / 2, fh), 0.06, -0.13, fr); _strip(mb, (bw / 2, 0), (0, fh / 2), 0.06, -0.13, fr)
    mb.q(0, 0, 0.12, fh, -0.1, fr); mb.q(bw - 0.12, 0, bw, fh, -0.1, fr); mb.q(0, fh - 0.1, bw, fh, -0.1, fr)
MODS['tri'] = m_tri; MODS['diamond'] = m_diamond
def _bp_fit(lay_, H, street, L, zb):
    gh = 4.6 if zb < 1.5 and H > 7 else 0.0; n = max(1, round((H - gh) / 4.0)); fh = (H - gh) / n
    rows = ([(gh, 'shop', 'G')] if gh else []) + [(fh, 'punched', 'F')] * n
    if H > 10 and n >= 2: rows[-1] = (fh, 'punched', 'T')                   # top storey: the inverted triangles of the photos
    return dict(bw=3.0, rows=rows, cols=lambda c, nb: _bpat[(c + nb) % len(_bpat)],
                P=dict(colmod={'R': 'ribbon', 'N': 'plain'}, ww=1.5, wh=1.5, nx=2, sill=1.1, wh2=1),
                rowP={'T': dict(colmod={'W': 'tri', 'R': 'tri', 'T': 'tri', 'N': 'plain'})})
def _bp_glz_fit(lay_, H, street, L, zb):
    n = max(1, round(H / 2.6)); return dict(bw=2.6, rows=[(H / n, 'diamond', 'F')] * n, cols=lambda c, nb: 'W', P=dict(frame=M('#cfe0d6', 0.4, 0.3)), rowP={})
def _hb_fit(lay_, H, street, L, zb):
    gh = 4.2 if zb < 1.5 and H > 7 else 0.0; n = max(1, round((H - gh) / 3.4)); fh = (H - gh) / n
    rows = ([(gh, 'shop', 'G')] if gh else []) + [(fh, 'ribbon', 'L' if (street and (k >= 2 or zb > 1.5)) else 'F') for k in range(n)]
    return _hb_lay(rows) if L > 2.6 else dict(bw=3, rows=[(H, 'plain', 'P')], cols=lambda c, nb: 'W', P={}, rowP={}, plain=True)
def _ml_fit(lay_, H, street, L, zb):
    gh = 5.0 if zb < 1.5 and H > 7 else 0.0; n = max(1, round((H - gh) / 3.4)); fh = (H - gh) / n
    return _mlL(([(gh, 'shop', 'G')] if gh else []) + [(fh, 'punched', 'F')] * n)
_SPEC_HB = dict(roofmat_fn=lambda r: _bp_roof(r), P=_hbP, layout=_hb_fit(None, 21, True, 20, 0), fitw=_hb_fit, cornice=(0.25, 0.4, M('#6d6a62', 0.5, 0.3)))
_SPEC_ML = dict(roofmat_fn=lambda r: _bp_roof(r), P=_mlP, layout=_ml_fit(None, 22, True, 20, 0), fitw=_ml_fit)
_SPEC_GLZ = dict(roofmat_fn=lambda r: _bp_roof(r), P=dict(wall=M('#3d7f5c', 0.4, 0.3), frame=M('#3d7f5c', 0.4, 0.3), panel=M((0.05, 0.16, 0.12), 0.08)), layout=_bp_glz_fit(None, 20, True, 10, 0), fitw=_bp_glz_fit)
def _bp_alt(x, y):
    p = _SPt(x, y)
    if _BP_CAN.buffer(0.6).contains(p): return _SPEC_GLZ
    if _BP_HOT.contains(p): return _SPEC_HB
    if _BP_ML.contains(p): return _SPEC_ML
    return None
def _bp_skip(r, k):                                     # the scan's square tower: replaced by the round one
    return all(math.hypot(q[0] - _BP_TW[0], q[1] - _BP_TW[1]) < _BP_TWR + 2.2 for q in r) and max(q[2] for q in r) > 16.5
def _bp_roof(r):
    zs = [q[2] for q in r]; cx = sum(q[0] for q in r) / len(r); cy = sum(q[1] for q in r) / len(r)
    if _BP_CAN.buffer(0.6).contains(_SPt(cx, cy)) and min(zs) > 22: return M('#f2f4f4')
    if max(zs) - min(zs) > 2.5: return _bpG
    if _BP_HOT.contains(_SPt(cx, cy)) or _BP_ML.contains(_SPt(cx, cy)): return M('#5a5c5e', 0.7)
    return M('#8e8681', 0.8) if min(zs) > 20.5 or min(zs) < 18.5 else M('#a9a69f', 0.85)     # felt roofs; the parking deck is concrete
def _bp_extra(Z, pts, h, P):
    L = lambda x, y, z: (x - Z.cx, y - Z.cy, z); wh_ = M('#f2f4f4')
    # round tower through the vault, offices fanning round it; white with dark-framed windows, light cap
    tw = dict(wall=M('#e8edf0'), frame=M('#1f4a4f'), joints=M('#8f9ea8')); ring = _ring(_BP_TW[0], _BP_TW[1], _BP_TWR, 20); z0, z1 = 16.0, 26.9
    zf = z1 - 3.4                                                            # open crown of white fins above the office floors
    for k in range(20): build_wall(Z, ring[k], ring[(k + 1) % 20], z0, zf, dict(bw=1.75, rows=[(3.7, 'punched', 'F')] * 2, cols=lambda c, nb: 'W', P=dict(ww=1.0, wh=1.6, nx=1, sill=0.9), rowP={}), tw, 900 + k, 0)
    add_solid(Z, [L(x, y, zf) for x, y in _ring(_BP_TW[0], _BP_TW[1], _BP_TWR - 0.6, 20)], M('#5d6d78', 0.5), 0.3)
    for k in range(20):
        a = 2 * math.pi * (k + 0.5) / 20; ca, sa = math.cos(a), math.sin(a); tx_, ty_ = -sa, ca
        for (r0, r1) in ((_BP_TWR - 0.9, _BP_TWR + 0.15),):
            pA = (_BP_TW[0] + ca * r0, _BP_TW[1] + sa * r0); pB = (_BP_TW[0] + ca * r1, _BP_TW[1] + sa * r1); w = 0.13
            for sgn in (1, -1):
                q0 = (pA[0] + tx_ * w * sgn, pA[1] + ty_ * w * sgn); q1 = (pB[0] + tx_ * w * sgn, pB[1] + ty_ * w * sgn)
                f = [L(q0[0], q0[1], zf), L(q1[0], q1[1], zf), L(q1[0], q1[1], z1), L(q0[0], q0[1], z1)]
                add_solid(Z, f if sgn < 0 else f[::-1], wh_, 0.4)
            add_solid(Z, [L(pB[0] - tx_ * w, pB[1] - ty_ * w, zf), L(pB[0] + tx_ * w, pB[1] + ty_ * w, zf), L(pB[0] + tx_ * w, pB[1] + ty_ * w, z1), L(pB[0] - tx_ * w, pB[1] - ty_ * w, z1)], wh_, 0.4)
    hat = _ring(_BP_TW[0], _BP_TW[1], _BP_TWR + 1.1, 20)
    add_solid(Z, [L(x, y, z1 + 0.35) for x, y in hat], wh_, 0.3); add_solid(Z, [L(x, y, z1) for x, y in hat][::-1], wh_, 0.3)
    for k in range(20):
        a, b = hat[k], hat[(k + 1) % 20]; add_solid(Z, [L(a[0], a[1], z1), L(b[0], b[1], z1), L(b[0], b[1], z1 + 0.35), L(a[0], a[1], z1 + 0.35)], wh_, 0.4)
    # entrance canopy: slender white columns with ring joints under the scanned roof (soffit and fascia added below the LoD2 plate)
    cs = list(_BP_CAN.exterior.coords)[:-1]; cx = sum(c[0] for c in cs) / 4; cy = sum(c[1] for c in cs) / 4
    big = [(cx + (x - cx) * 1.38, cy + (y - cy) * 1.38) for x, y in cs]; zc = 23.4      # the plate reaches well past the glass hall (photos)
    if _SP(big).exterior.is_ccw is False: big = big[::-1]                 # counter-clockwise: tops face up, fascias outwards (one face each: two coincident faces bake black)
    add_solid(Z, [L(x, y, 19.0) for x, y in cs], M((0.08, 0.2, 0.15), 0.1), 0.4)        # glass roof of the entrance hall under the canopy
    for k in range(4):
        a, b = big[k], big[(k + 1) % 4]; fq = [L(a[0], a[1], zc), L(b[0], b[1], zc), L(b[0], b[1], zc + 0.9), L(a[0], a[1], zc + 0.9)]
        add_solid(Z, fq, wh_, 0.4)
    add_solid(Z, [L(x, y, zc) for x, y in big][::-1], wh_, 0.4)
    add_solid(Z, [L(x, y, zc + 0.9) for x, y in big], M('#e4e7e8'), 0.3)
    pos = []
    for k in range(4):
        a, b = big[k], big[(k + 1) % 4]; pos += [a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)]
    def cyl(px_, py_, r0, r1, z0_, z1_, mat, n=12, dn=0.5):
        A = _ring(px_, py_, r0, n); Bq = _ring(px_, py_, r1, n)
        for k in range(n): add_solid(Z, [L(A[k][0], A[k][1], z0_), L(A[(k + 1) % n][0], A[(k + 1) % n][1], z0_), L(Bq[(k + 1) % n][0], Bq[(k + 1) % n][1], z1_), L(Bq[k][0], Bq[k][1], z1_)], mat, dn)
    grey = M('#8e989d', 0.5, 0.3)
    for x, y in pos:
        px_, py_ = cx + (x - cx) * 0.92, cy + (y - cy) * 0.92
        cyl(px_, py_, 0.5, 0.5, 0, 2.8, grey)                                   # lit base
        for zr in (0.7, 1.4, 2.1): cyl(px_, py_, 0.56, 0.56, zr, zr + 0.12, M('#c9ced1'), dn=0.3)
        cyl(px_, py_, 0.3, 0.3, 2.8, zc - 2.6, wh_)                             # slender shaft
        for k in range(5):                                                       # ribbed capital, an inverted cone
            za = zc - 2.6 + k * 0.52; ra = 0.3 + 0.12 * k; cyl(px_, py_, ra, ra + 0.12, za, za + 0.4, wh_, dn=0.4); cyl(px_, py_, ra + 0.12, ra + 0.1, za + 0.4, za + 0.52, grey, dn=0.3)
SPEC[BEPOP] = dict(lod2=True, runalt=lambda x, y: _SPEC_GLZ if _BP_CAN.buffer(0.3).contains(_SPt(x, y)) else _SPEC_ML if _BP_ML.contains(_SPt(x, y)) else _SPEC_HB if _BP_HOT.contains(_SPt(x, y)) else None, zcap=lambda x, y: 19.0 if _BP_CAN.buffer(0.3).contains(_SPt(x, y)) else None, P=_bpP, layout=_bp_fit(None, 18, True, 20, 0), fitw=_bp_fit, alt=_bp_alt, skip=_bp_skip, roofmat_fn=_bp_roof, extra=[_bp_extra])

# ---------------------------------------------------------------- IsoKarhu, Promenadikeskus, Sokos on their LoD2 shells (MML Rakennukset 3D)
def _flat_roof(light='#a9a69f', dark='#5f6265', glass=None):
    def f(r):
        zs = [q[2] for q in r]
        if glass and max(zs) - min(zs) > 1.2: return glass
        return M(light, 0.85) if min(zs) < 12.5 else M(dark, 0.75)          # low decks (roof parking) concrete, high roofs dark felt
    return f
def _shop_fit(gh, fh, upper, top=None, plain_short=4.0):
    """ground floor shops of height gh, storeys of about fh as the 'upper' module; walls above a lower roof get storeys only"""
    def fit(lay_, H, street, L, zb):
        g = gh if zb < 1.5 and H > gh + 1.5 else 0.0
        if H - g < 1.6: g = 0.0
        n = max(1, round((H - g) / fh)); f = (H - g) / n
        rows = ([(g, 'shop', 'G')] if g else []) + [(f, upper[0], 'F')] * n
        if top and n >= 2: rows[-1] = (f, top, 'T')
        return dict(bw=upper[1], rows=rows if L > plain_short else [(H, 'plain', 'P')], cols=upper[2], P=upper[3], rowP=upper[4] if len(upper) > 4 else {}, plain=L <= plain_short)
    return fit

# Yrjönkatu 14-16, IsoKarhu (Heikkilä & Kauppinen 1991, extensions Asmala 2001 / 2003, facade Sergej von Bagh 2014; Y-pakki 2018):
# 3- and 2-storey parts over the whole block, roof terrace and parking deck; dark panel cladding with logo bands on the upper floor,
# large unbroken shop windows at street level, light glass bands at the north-west and south-west corner entrances (Y-pakki photo).
ISOK = _bid(110.0, -169.0)
_ikP = dict(wall=M('#3e4045', 0.55, 0.25), spandrel=M('#3e4045', 0.55, 0.25), frame=M('#2a2c30', 0.4, 0.4), gwall=M('#2b2d31', 0.4), plinth=M('#26282b'),
            fascia=M('#3e4045', 0.55, 0.25), gframe=M('#2a2c30', 0.4, 0.4), sign=SIGNS + [M('#e6007e'), M('#e6007e')], joints=M('#55585e', 0.5, 0.3))
_ikUp = ('ribbon', 3.6, lambda c, nb: 'N' if (c % 5 in (1, 2) and nb > 6) else 'W', dict(sill=0.8, wh=2.0, pier=0.15, nx=2, colmod={'N': 'plain'}))
SPEC[ISOK] = dict(lod2=True, P=_ikP, layout=_shop_fit(4.6, 4.2, _ikUp)(None, 13, True, 20, 0), fitw=_shop_fit(4.6, 4.2, _ikUp), roofmat_fn=_flat_roof('#a8a59e', '#55585b'))

# Yrjönkatu 17, Promenadikeskus (1999): culture house with a concert hall (676 seats) and five cinemas; the hall rises to 17 m, the lobby
# and foyers lower round it.  Dark grey metal cladding with horizontal bands, glazed lobby at street level (no inventory text: the look
# follows the existing model and the oblique aerial photos; to be checked against a street photo).
PROME = _bid(9.2, -238.7)
_prP = dict(wall=M('#454a51', 0.5, 0.3), spandrel=M('#454a51', 0.5, 0.3), frame=M('#2b2e33', 0.4, 0.4), gwall=M('#30343a', 0.4), plinth=M('#26282b'),
            fascia=M('#5a6068', 0.5, 0.3), gframe=M('#2b2e33', 0.4, 0.4), sign=SIGNS, band=M('#7d848c', 0.5, 0.3))
_prUp = ('ribbon', 3.2, lambda c, nb: 'N' if (c % 4 == 3) else 'W', dict(sill=1.4, wh=1.2, pier=0.2, nx=2, band=M('#7d848c', 0.5, 0.3), colmod={'N': 'plain'}))
SPEC[PROME] = dict(lod2=True, P=_prP, layout=_shop_fit(5.0, 4.0, _prUp)(None, 12, True, 20, 0), fitw=_shop_fit(5.0, 4.0, _prUp), roofmat_fn=_flat_roof('#8f9396', '#4f5357'))

# Liisankatu 2-4, Sokos (Paul Autere / SOK 1973, facade Kaj Nordman 2003): shop windows at street level, light grey panels with storey-high
# vertical windows above.  The same LoD2 shell holds Yrjönkatu 20, Porin Talo (Reijo Kunnas 1978, facade 2015: blue-grey panel cladding,
# ribbon windows on floors 2-4) and the 16-storey Linnainmaankulma tower (2013, 53 m; grey-green glazed balcony faces in the oblique photos).
SOKOS = _bid(100.0, -260.0); PTALO = 582; LINNA = 1208
_soP = dict(wall=M('#c9ccce', 0.6, 0.15), spandrel=M('#c9ccce', 0.6, 0.15), frame=M('#3a3d40', 0.4, 0.4), gwall=M('#2e3134', 0.4), plinth=M('#2a2c2f'),
            fascia=M('#2e7d4f', 0.5), gframe=ALU, sign=SIGNS, joints=M('#aeb2b5', 0.5, 0.2))
_soUp = ('punched', 2.6, lambda c, nb: 'W' if c % 3 == 1 else 'N', dict(ww=1.2, wh=3.4, sill=0.3, nx=1, colmod={'N': 'plain'}))
_ptP = dict(wall=M('#8fa3b5', 0.5, 0.25), spandrel=M('#8fa3b5', 0.5, 0.25), frame=M('#2d3134', 0.4, 0.4), gwall=M('#2e3134', 0.4), plinth=M('#2a2c2f'),
            fascia=M('#6d8193'), gframe=ALU, sign=SIGNS)
_ptUp = ('ribbon', 3.0, lambda c, nb: 'W', dict(sill=0.9, wh=1.5, pier=0.0, nx=3))
_liP = dict(wall=M('#d9dcd8'), spandrel=M('#d9dcd8'), frame=M('#2f3337', 0.4, 0.4), rail=M('#7f9a94', 0.12), linner=M('#cfd2ce'), gwall=M('#2e3134', 0.4),
            plinth=M('#2a2c2f'), fascia=M('#5d6f78'), gframe=ALU, sign=SIGNS)
_liUp = ('punched', 3.0, lambda c, nb: 'L' if c % 3 != 1 else 'W', dict(ww=1.4, wh=1.5, nx=2, colmod={'L': 'loggia'}, ldepth=1.2))
_SPEC_PT = dict(P=_ptP, layout=_shop_fit(4.2, 3.4, _ptUp)(None, 14, True, 20, 0), fitw=_shop_fit(4.2, 3.4, _ptUp))
_SPEC_LI = dict(P=_liP, layout=_shop_fit(4.6, 3.1, _liUp)(None, 53, True, 20, 0), fitw=_shop_fit(4.6, 3.1, _liUp))
_SO_PT = _SP(poly(PTALO)[0]).buffer(0.8); _SO_LI = _SP(poly(LINNA)[0]).buffer(1.0)
def _so_part(x, y):
    p = _SPt(x, y)
    if _SO_LI.contains(p): return _SPEC_LI
    if _SO_PT.contains(p): return _SPEC_PT
    return None
SPEC[SOKOS] = dict(lod2=True, P=_soP, layout=_shop_fit(4.6, 4.0, _soUp)(None, 9, True, 20, 0), fitw=_shop_fit(4.6, 4.0, _soUp), runalt=_so_part,
                   skip=lambda r, k: k == 'W' and min(q[2] for q in r) > 6 and max(q[2] for q in r) - min(q[2] for q in r) < 2.2)   # cars / vents on the parking deck; c067 block: roofs stay the aerial photo on the LoD2 shell

# ---------------------------------------------------------------- Yrjönkatu: parts of a neighbour's LoD2 shell that are other houses
# Yrjönkatu 21 (north end of the Palojoenkulma shell, Mikonkatu corner): 2-3 storeys, light ochre render with shops and awnings
# (Y-pakki photo of Palojoenkulma looking north along Yrjönkatu)
_y21P = dict(wall=M('#e2c98a'), spandrel=M('#e2c98a'), frame=M('#f1efe8'), gwall=M('#3a3d40', 0.4), plinth=M('#4a4744'), fascia=M('#e2c98a'),
             gframe=M('#3a3d40', 0.4), sign=SIGNS, canopy=0.9, canopy_mat=M('#d2691e', 0.7))
_y21Up = ('punched', 3.2, lambda c, nb: 'W', dict(ww=1.3, wh=1.5, nx=2))
_SPEC_Y21 = dict(P=_y21P, layout=_shop_fit(4.0, 3.2, _y21Up)(None, 10, True, 20, 0), fitw=_shop_fit(4.0, 3.2, _y21Up))
SPEC[PALO]['runalt'] = lambda x, y: _SPEC_Y21 if y > -388.0 else None
# Valtakatu 3 (1960, 6 storeys) and, in the same shell, Yrjönkatu 2 b (Reijo Louhimo 1985): light brick-tile cladding with element joints,
# partly recessed glazed balconies at the north and south ends, shopfronts under the projecting upper floors (Y-pakki text)
VALT3 = 1620; Y2B = 1618
_v3P = dict(wall=M('#c4b08a'), spandrel=M('#c4b08a'), frame=M('#f1efe8'), gwall=M('#34373a', 0.4), plinth=M('#4a4744'), fascia=M('#c4b08a'), gframe=ALU, sign=SIGNS)
_v3Up = ('punched', 3.2, lambda c, nb: 'W', dict(ww=1.5, wh=1.45, nx=2))
_y2bP = dict(wall=MT('#d8cdbb', 'brick', 0.8), spandrel=MT('#d8cdbb', 'brick', 0.8), frame=M('#5b5148', 0.5), rail=M('#9fb0b8', 0.15), linner=M('#e6dfd2'),
             gwall=M('#34373a', 0.4), plinth=M('#6e6a64'), fascia=M('#d8cdbb'), gframe=ALU, sign=SIGNS, joints=M('#b9ad99'))
_y2bUp = ('punched', 3.0, lambda c, nb: 'L' if c in (0, nb - 1) else 'W', dict(ww=1.4, wh=1.45, nx=2, colmod={'L': 'loggia'}, ldepth=1.2))
_SPEC_Y2B = dict(P=_y2bP, layout=_shop_fit(3.8, 2.9, _y2bUp)(None, 19, True, 20, 0), fitw=_shop_fit(3.8, 2.9, _y2bUp))
_Y2B_PG = _SP(poly(Y2B)[0]).buffer(0.8)
SPEC[VALT3] = dict(P=_v3P, layout=_shop_fit(4.0, 3.2, _v3Up)(None, 21, True, 20, 0), fitw=_shop_fit(4.0, 3.2, _v3Up),
                   runalt=lambda x, y: _SPEC_Y2B if _Y2B_PG.contains(_SPt(x, y)) else None)

ZONES = {
    'tori0': [1725, 1727, 1728, 1729, 1730, 1731, 1732, 1600, 1621],
    'tori1': [1315, 1490, 1491, 1492, 1493, 1494, 1495, 1496, 1361, 1363, 1367, 1488, 1489, 1362, 1364, 1365, 1366, 1372],
    'tori2': [161, 162, 163, 207, 208, 561, 562, 1313, 1314, 1344, 1345, 1346, 1347, 1348, 1349, 1497, 1498, 1499, 1312, 1259],
    'tori3': [563, 564, 637, 638, 639, 641, 642, 1216],   # 603, 604: photo facades (Porin kaupunki photos) in the game
    'tori4': [1220, 640, 1723, 1724, 1734, 1217, 1218, 1219, 1192],
    'tori5': [1601, 1623, 1624, 1720, 1721, 1722],
    'bepop': [BEPOP], 'uima': [UIMA], 'isokarhu': [ISOK], 'promenadi': [PROME],
}
NOROOF = set()


# buildings with an approved photo facade (phs.json from the review tool) are drawn by the game itself: leave them out of the blocks
import os as _os, json as _json
if _os.environ.get('PORI_PHS') and _os.path.exists(_os.environ['PORI_PHS']):
    _ex = {int(k) for k in _json.load(open(_os.environ['PORI_PHS']))}
    ZONES = {k: [i for i in v if i not in _ex] for k, v in ZONES.items()}
