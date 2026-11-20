"""Porin rataverkko pelikoordinaatteihin: OSM-raiteet (overpass 20.11.2026) -> rata/rata_data.js

- raiteet tasoitetaan (Gauss pitkin kaarta), vaihteissa poikkeava raide lähtee tangentiaalisesti läpimenevästä
- korkeus: MML 2 m korkeusmalli (terrain.js hg), mediaani + Gauss, sillat suoraan päiden välillä, tasoristeyksissä kiskot tien tasoon
- reitit bottijunalle (Tampereen suunta -> raide 1 / 2) Dijkstralla, vaihteissa ei jyrkkiä käännöksiä
"""
import json, math, sys, heapq, os
import numpy as np
from scipy.ndimage import gaussian_filter1d, median_filter
sys.path.insert(0, os.path.dirname(__file__))
from terr import TZg, T

OX0, OX1, OY0, OY1 = -2504.1, 2450.8, -3501.6, 1894.4
D = json.load(open(os.path.join(os.path.dirname(__file__), 'osm_rail.json')))

# ---------------------------------------------------------------- raiteet
W = []
for t, g in D['W']:
    if t.get('r') not in ('rail', 'disused'):
        continue
    P = np.array(g, float).reshape(-1, 2)
    W.append(dict(t=t, P=P))

def inmap(p, m=0):
    return OX0 - m < p[0] < OX1 + m and OY0 - m < p[1] < OY1 + m

# leikkaa kartan reunaan (rajaviivan leikkauspiste)
def clip(P):
    out = []; cur = []
    for k in range(len(P)):
        a = P[k]
        if inmap(a):
            if not cur and k > 0:
                cur.append(edge(P[k - 1], a))
            cur.append(a)
        else:
            if cur:
                cur.append(edge(a, P[k - 1])); out.append(np.array(cur)); cur = []
    if cur:
        out.append(np.array(cur))
    return [c for c in out if len(c) >= 2]

def edge(outp, inp):
    # piste janalla outp->inp kartan reunalla
    lo, hi = 0.0, 1.0
    for _ in range(40):
        m = (lo + hi) / 2; p = outp + (inp - outp) * m
        if inmap(p): hi = m
        else: lo = m
    return outp + (inp - outp) * hi

W2 = []
for w in W:
    for c in clip(w['P']):
        W2.append(dict(t=w['t'], P=c))
W = W2
print('ways', len(W))

key = lambda p: (round(float(p[0]), 1), round(float(p[1]), 1))
# solmut: kaikki pisteet -> ways
NODE = {}
for i, w in enumerate(W):
    for k, p in enumerate(w['P']):
        NODE.setdefault(key(p), []).append((i, k))

def densify(P, step=1.0):
    out = [P[0]]
    for a, b in zip(P[:-1], P[1:]):
        L = np.linalg.norm(b - a); n = max(1, int(math.ceil(L / step)))
        for j in range(1, n + 1):
            out.append(a + (b - a) * j / n)
    return np.array(out)

def arclen(P):
    return np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])

def resample(P, step):
    s = arclen(P); L = s[-1]; n = max(1, int(round(L / step)))
    ss = np.linspace(0, L, n + 1)
    return np.stack([np.interp(ss, s, P[:, 0]), np.interp(ss, s, P[:, 1])], 1)

def smooth(P, sigma):
    if len(P) < 5:
        return P.copy()
    n = len(P); pad = min(n - 1, int(sigma * 3))
    A = np.concatenate([2 * P[0] - P[pad:0:-1], P, 2 * P[-1] - P[-2:-pad - 2:-1]])
    S = np.stack([gaussian_filter1d(A[:, 0], sigma, mode='nearest'), gaussian_filter1d(A[:, 1], sigma, mode='nearest')], 1)
    S = S[pad:pad + n]
    # päät kiinni
    S[0] = P[0]; S[-1] = P[-1]
    return S

def kind(t):
    if t.get('r') == 'disused': return 'x'
    if t.get('u') == 'main': return 'm'
    if t.get('u') == 'branch': return 'b'
    s = t.get('s', '')
    return {'siding': 's', 'yard': 'y', 'spur': 'p', 'crossover': 's'}.get(s, 'b' if not s else 's')

SIG = {'m': 7.0, 'b': 6.0, 's': 3.0, 'y': 3.0, 'p': 4.0, 'x': 4.0}
for w in W:
    w['k'] = kind(w['t'])
    w['D'] = densify(w['P'], 1.0)

# ---------------------------------------------------------------- vaihteet: läpimenevä suunta jokaisessa solmussa
def arm_dir(i, k, sign):
    P = W[i]['P']; p0 = P[k]; acc = 0; j = k
    while 0 <= j + sign < len(P):
        acc += np.linalg.norm(P[j + sign] - P[j]); j += sign
        if acc > 12: break
    if j == k: return None
    d = P[j] - p0; return d / (np.linalg.norm(d) + 1e-9)

JUNC = {}
for kk, lst in NODE.items():
    if len(lst) < 2: continue
    arms = []
    for i, k in lst:
        for sg in (-1, 1):
            d = arm_dir(i, k, sg)
            if d is not None:
                arms.append((i, k, sg, d))
    if len(arms) < 3: continue   # pelkkä jatkos kahden wayn välillä hoidetaan myös: 2 haaraa
    best = None
    for a in range(len(arms)):
        for b in range(a + 1, len(arms)):
            c = float(np.dot(arms[a][3], arms[b][3]))
            if best is None or c < best[0]: best = (c, a, b)
    _, a, b = best
    t = arms[a][3] - arms[b][3]; t /= np.linalg.norm(t)
    JUNC[kk] = dict(t=t, through=(arms[a][:3], arms[b][:3]), arms=arms)

# 2-haaraiset jatkokset (way loppuu, toinen alkaa)
CONT = {}
for kk, lst in NODE.items():
    if len(lst) == 2 and kk not in JUNC:
        ends = [(i, k) for i, k in lst if k == 0 or k == len(W[i]['P']) - 1]
        if len(ends) == 2:
            CONT[kk] = ends

# ---------------------------------------------------------------- tasoitus
# yhdistetään jatkuvat (2-haaraiset jatkokset) ketjuiksi ennen tasoitusta, jotta jatkoskohtaan ei jää mutkaa
used = set(); CHAINS = []
endmap = {}
for i, w in enumerate(W):
    endmap.setdefault(key(w['P'][0]), []).append((i, 0)); endmap.setdefault(key(w['P'][-1]), []).append((i, 1))
def other_cont(i, e):
    kk = key(W[i]['P'][0] if e == 0 else W[i]['P'][-1])
    if kk not in CONT: return None
    for j, k in CONT[kk]:
        if j != i:
            return (j, 0 if k == 0 else 1)
    return None
for i in range(len(W)):
    if i in used: continue
    # kulje alkuun
    cur, ce = i, 0; seen = {i}
    while True:
        o = other_cont(cur, ce)
        if not o or o[0] in seen: break
        j, je = o; seen.add(j); cur, ce = j, 1 - je
    # cur:n pää ce on ketjun alku; kulje loppuun
    chain = []; c, start = cur, ce; seen2 = set()
    while c is not None and c not in seen2:
        seen2.add(c); chain.append((c, start == 0)); used.add(c)
        o = other_cont(c, 1 - start)
        if not o: break
        c, oe = o; start = oe
    CHAINS.append(chain)
print('chains', len(CHAINS))

TR = []
for ch in CHAINS:
    pts = []; ks = []
    for i, fwd in ch:
        P = W[i]['D'] if fwd else W[i]['D'][::-1]
        if pts: P = P[1:]
        pts.extend(P); ks.extend([i] * len(P))
    P = np.array(pts)
    k0 = W[ch[0][0]]['k']
    kinds = [W[i]['k'] for i, _ in ch]
    k = min(kinds, key=lambda c: 'mbspyx'.index(c))
    TR.append(dict(P=P, src=np.array(ks), k=k, t=W[ch[0][0]]['t'], ways=[i for i, _ in ch]))

for tr in TR:
    tr['S'] = smooth(tr['P'], SIG[tr['k']])

# läpimenevän raiteen piste ja tangentti solmun kohdalla (tasoitettuna)
def track_at(kk, exclude=None):
    best = None
    p = np.array(kk)
    for ti, tr in enumerate(TR):
        if ti == exclude: continue
        S = tr['S']; d = np.linalg.norm(tr['P'] - p, axis=1); j = int(np.argmin(d))
        if d[j] > 0.2: continue
        if j == 0 or j == len(S) - 1: continue   # pää, ei läpimenevä
        a = S[max(0, j - 3)]; b = S[min(len(S) - 1, j + 3)]; t = b - a; t /= np.linalg.norm(t)
        best = (ti, j, S[j], t)
    return best

def hermite(P0, T0, P1, T1, n):
    s = np.linspace(0, 1, n)[:, None]
    h00 = 2 * s**3 - 3 * s**2 + 1; h10 = s**3 - 2 * s**2 + s; h01 = -2 * s**3 + 3 * s**2; h11 = s**3 - s**2
    return h00 * P0 + h10 * T0 + h01 * P1 + h11 * T1

TURNOUT = []
for ti, tr in enumerate(TR):
    for end in (0, 1):
        S = tr['S'] if end == 0 else tr['S'][::-1]
        kk = key(tr['P'][0] if end == 0 else tr['P'][-1])
        th = track_at(kk, ti)
        if not th: continue
        tj, j, Pn, t = th
        L = arclen(S)
        Lb = min(28.0, L[-1] * 0.45)
        m = int(np.searchsorted(L, Lb))
        if m < 4: continue
        d0 = S[min(len(S) - 1, 6)] - S[0]
        if np.dot(d0, t) < 0: t = -t
        Q = S[m]; Tq = S[min(len(S) - 1, m + 2)] - S[max(0, m - 2)]; Tq /= np.linalg.norm(Tq)
        mag = Lb
        H = hermite(Pn, t * mag, Q, Tq * mag, m + 1)
        S = np.concatenate([H, S[m + 1:]])
        if end == 1: S = S[::-1]
        tr['S'] = S
        TURNOUT.append(dict(div=ti, end=end, thr=tj, at=[float(Pn[0]), float(Pn[1])], t=[float(t[0]), float(t[1])]))
print('turnouts', len(TURNOUT))

# 2 m välein
for tr in TR:
    tr['S'] = resample(tr['S'], 2.0)

# ---------------------------------------------------------------- korkeus
BR = []   # siltojen janat (OSM bridge=yes)
for w in W:
    if w['t'].get('b') == 'yes':
        BR.append(w['P'])
LC = [np.array([x, y]) for t, x, y in D['N'] if t['r'] == 'level_crossing']

def near_poly(p, P, r):
    for a, b in zip(P[:-1], P[1:]):
        d = b - a; L2 = float(np.dot(d, d)) or 1; u = max(0, min(1, float(np.dot(p - a, d)) / L2))
        if np.linalg.norm(a + d * u - p) < r: return True
    return False

CREST = 0.10   # pölkyn yläpinta korkeusmallin yläpuolella
RAIL = 0.19    # kiskon yläpinta pölkyn yläpinnasta (60E1 172 mm + välilevy)
for tr in TR:
    S = tr['S']; z = TZg(S[:, 0], S[:, 1]).astype(float)
    bridge = np.array([any(near_poly(p, B, 2.5) for B in BR) for p in S])
    # sillan päät: 12 m kumpaankin suuntaan pois laskusta
    bb = bridge.copy()
    for i in np.where(bridge)[0]:
        bb[max(0, i - 6):i + 7] = True
    tr['bridge'] = bridge
    good = ~bb
    # leikkaukset (ali menevä tie korkeusmallissa): poikkeama mediaanista
    if good.sum() >= 2:
        zi = np.interp(np.arange(len(z)), np.where(good)[0], z[good])
    else:
        zi = z
    # leikkaukset ja alikulut (omistaja 20.11.: aseman alikulun portaalin kohdalla rata kulkee suoraan, ei seuraa maastomallin kuoppaa)
    zm = median_filter(zi, size=41, mode='nearest')
    bad = (zi < zm - 0.35)
    for _ in range(4):
        bad = bad | np.concatenate([[False], bad[:-1]]) | np.concatenate([bad[1:], [False]])
    good2 = ~bad & good
    if good2.sum() >= 2:
        zi = np.interp(np.arange(len(z)), np.where(good2)[0], zi[good2])
    zs = gaussian_filter1d(median_filter(zi, size=7, mode='nearest'), 6, mode='nearest')
    tr['zg'] = zs
    # tasoristeykset: kiskot tien tasoon (tie = maa + 0,12)
    lcm = np.zeros(len(S), bool)
    for c in LC:
        d = np.linalg.norm(S - c, axis=1); j = int(np.argmin(d))
        if d[j] < 3.0:
            lcm[max(0, j - 3):j + 4] = True
            want = float(TZg(*c)) + 0.12 - RAIL - CREST
            for i in range(len(S)):
                w = max(0, 1 - abs(i - j) * 2.0 / 30)
                zs[i] = zs[i] * (1 - w) + want * w
    tr['lc'] = lcm
    tr['crest'] = zs + CREST

# solmujen korkeudet yhteen: poikkeava raide liittyy läpimenevän korkeuteen
for to in TURNOUT:
    d, t = TR[to['div']], TR[to['thr']]
    p = np.array(to['at']); j = int(np.argmin(np.linalg.norm(t['S'] - p, axis=1)))
    ztar = t['crest'][j]
    c = d['crest'] if to['end'] == 0 else d['crest'][::-1]
    n = min(len(c), 25)
    for i in range(n):
        w = 1 - i / n
        c[i] = c[i] * (1 - w) + ztar * w
    d['crest'] = c if to['end'] == 0 else c[::-1]

# jatkokset ketjujen välillä hoidettu yhdistämällä

# ---------------------------------------------------------------- laiturit
PL = []
for t, g in D['W']:
    if t.get('r') == 'platform':
        P = np.array(g, float).reshape(-1, 2)
        PL.append(dict(ref=t.get('rf'), P=P))

# ---------------------------------------------------------------- reitit bottijunalle
# solmuverkko tasoitetuista raiteista: pisteet + yhteydet raiteiden välillä vaihteissa
nodes = []   # (track, index)
for ti, tr in enumerate(TR):
    pass
import collections
ADJ = collections.defaultdict(list)
def nid(ti, j): return ti * 100000 + j
for ti, tr in enumerate(TR):
    S = tr['S']; L = np.linalg.norm(np.diff(S, axis=0), axis=1)
    for j in range(len(S) - 1):
        ADJ[nid(ti, j)].append((nid(ti, j + 1), L[j])); ADJ[nid(ti, j + 1)].append((nid(ti, j), L[j]))
# vaihteet: poikkeavan raiteen pää <-> läpimenevän lähin piste
for to in TURNOUT:
    d, t = TR[to['div']], TR[to['thr']]
    jd = 0 if to['end'] == 0 else len(d['S']) - 1
    jt = int(np.argmin(np.linalg.norm(t['S'] - d['S'][jd], axis=1)))
    ADJ[nid(to['div'], jd)].append((nid(to['thr'], jt), 0.01)); ADJ[nid(to['thr'], jt)].append((nid(to['div'], jd), 0.01))
# jatkokset ketjujen välillä (päät samassa paikassa)
ends = []
for ti, tr in enumerate(TR):
    ends.append((ti, 0)); ends.append((ti, len(tr['S']) - 1))
for a in range(len(ends)):
    for b in range(a + 1, len(ends)):
        ta, ja = ends[a]; tb, jb = ends[b]
        if ta == tb: continue
        if np.linalg.norm(TR[ta]['S'][ja] - TR[tb]['S'][jb]) < 0.3:
            ADJ[nid(ta, ja)].append((nid(tb, jb), 0.01)); ADJ[nid(tb, jb)].append((nid(ta, ja), 0.01))

def pos(n): ti, j = divmod(n, 100000); return TR[ti]['S'][j]

def route(a, b):
    # Dijkstra tilassa (solmu, edellinen) – ei yli 25 asteen kääntöjä
    st = (a, -1); dist = {st: 0}; prev = {}; pq = [(0, a, -1)]
    while pq:
        dd, n, pr = heapq.heappop(pq)
        if n == b:
            path = [n]; s = (n, pr)
            while s in prev: s = prev[s]; path.append(s[0])
            return path[::-1]
        if dist.get((n, pr), 1e18) < dd: continue
        for m, w in ADJ[n]:
            if m == pr: continue
            if pr >= 0:
                p0, p1, p2 = pos(pr), pos(n), pos(m)
                v1 = p1 - p0; v2 = p2 - p1
                if np.linalg.norm(v1) > 0.05 and np.linalg.norm(v2) > 0.05:
                    c = np.dot(v1, v2) / np.linalg.norm(v1) / np.linalg.norm(v2)
                    if c < math.cos(math.radians(25)): continue
                pp = pr if np.linalg.norm(v2) > 0.05 or True else pr
            nd = dd + w; s = (m, n)
            if nd < dist.get(s, 1e18):
                dist[s] = nd; prev[s] = (n, pr); heapq.heappush(pq, (nd, m, n))
    return None

def nearest_node(p, kinds=None):
    best = None
    for ti, tr in enumerate(TR):
        if kinds and tr['k'] not in kinds: continue
        d = np.linalg.norm(tr['S'] - p, axis=1); j = int(np.argmin(d))
        if best is None or d[j] < best[0]: best = (d[j], nid(ti, j))
    return best[1]

# sisääntulo kaakosta: pääraiteen piste kartan reunalla
entry = None
for ti, tr in enumerate(TR):
    if tr['k'] != 'm': continue
    for j in (0, len(tr['S']) - 1):
        p = tr['S'][j]
        if p[1] < OY0 + 5: entry = nid(ti, j)
print('entry', entry, pos(entry) if entry else None)
STOP = {s['rf']: np.array([x, y]) for s, x, y in [(t, x, y) for t, x, y in D['N'] if t['r'] == 'stop']}
ROUTES = {}
for ref, p in STOP.items():
    n = nearest_node(p, 'msb')
    path = route(entry, n)
    if not path: print('NO ROUTE', ref); continue
    # jatka pysähdyspaikan ohi 60 m (junan keula pysähtyy laiturin päähän)
    P = np.array([pos(q) for q in path])
    Z = np.array([TR[q // 100000]['crest'][q % 100000] + RAIL for q in path])
    keep = np.concatenate([[True], np.linalg.norm(np.diff(P, axis=0), axis=1) > 0.05])
    P = P[keep]; Z = Z[keep]
    ROUTES[ref] = (P, Z)
    print('route', ref, len(P), round(arclen(P)[-1]))

# ---------------------------------------------------------------- ulos
def r2(v): return round(float(v), 2)
out = dict(rail=RAIL, crest=CREST, t=[], to=[], pl=[], n=[], r={})
for tr in TR:
    S = tr['S']; c = tr['crest']
    flat = []
    for p, z in zip(S, c): flat += [r2(p[0]), r2(p[1]), r2(z)]
    t = tr['t']
    out['t'].append(dict(k=tr['k'], e=int(t.get('e', 0) or 0), v=int(t.get('v', 35) or 35), p=flat,
                         b=[int(i) for i in np.where(tr['bridge'])[0]], lc=[int(i) for i in np.where(tr['lc'])[0]]))
for to in TURNOUT:
    out['to'].append(dict(d=to['div'], e=to['end'], th=to['thr'], at=[r2(v) for v in to['at']], t=[round(v, 4) for v in to['t']]))
for p in PL:
    out['pl'].append(dict(ref=p['ref'], p=[r2(v) for v in p['P'].ravel()]))
for t, x, y in D['N']:
    if t['r'] in ('signal', 'buffer_stop', 'switch', 'level_crossing', 'derail') and inmap((x, y)):
        out['n'].append([t['r'][0:2], r2(x), r2(y), t.get('rf', ''), t.get('sm', '')])
for ref, (P, Z) in ROUTES.items():
    flat = []
    for p, z in zip(P, Z): flat += [r2(p[0]), r2(p[1]), r2(z)]
    out['r'][ref] = flat
json.dump(out, open('rata_data.json', 'w'), separators=(',', ':'))
print('tracks', len(TR), 'size', len(json.dumps(out, separators=(',', ':'))))

# ---------------------------------------------------------------- maaston muokkaus (index.html soveltaa ennen maan rakentamista)
# 1) ratapenkka: ruudukon solmut alle 3,6 m raiteesta painetaan pölkyn yläpinnan alle, jotta maa ei puhkaise sepeliä
# 2) aseman alikulku: korkeusmallissa tunneli näkyy 4 m syvänä kaivantona koko ratapihan poikki. Kaivanto täytetään raiteiden ja laitureiden
#    kohdalta (maanpinta ratapihan tasoon); asema-aukion puoleinen pää jää auki portaaliksi (omistaja 20.11.2026)
from terr import HG, HS
from scipy.ndimage import grey_closing
from matplotlib.path import Path as MPath
nx, ny, g, x0, y0 = T['nx'], T['ny'], T['g'], T['x0'], T['y0']
H = HG.astype(float) / 10; Hs = HS.astype(float) / 10
newH = H.copy()
# raidepisteet tiheästi
allp = []; allz = []
for tr in TR:
    if tr['k'] == 'x': pass
    for i, (p, c) in enumerate(zip(tr['S'], tr['crest'])):
        if tr['bridge'][i]: continue
        allp.append(p); allz.append(c)
allp = np.array(allp); allz = np.array(allz)
from scipy.spatial import cKDTree
kd = cKDTree(allp)
gx = x0 + np.arange(nx) * g; gy = y0 + np.arange(ny) * g
GX, GY = np.meshgrid(gx, gy)
pts = np.stack([GX.ravel(), GY.ravel()], 1)
d, idx = kd.query(pts, distance_upper_bound=6.0)
ok = np.isfinite(d)
# alikulku: täyttö
PLP = [MPath(p['P']) for p in PL]
fillbox = (pts[:, 0] > -482) & (pts[:, 0] < -398) & (pts[:, 1] > -1062) & (pts[:, 1] < -968)
closed = grey_closing(H, size=(7, 7))
inpl = np.zeros(len(pts), bool)
for mp in PLP: inpl |= mp.contains_points(pts, radius=4.0)
fillm = fillbox & ((ok & (d < 5.5)) | inpl | ((pts[:, 0] > -477) & (pts[:, 0] < -431)))
fl = newH.ravel()
fl[fillm] = np.maximum(fl[fillm], closed.ravel()[fillm])
# yksittäiset kuopat raiteiden välissä (laiturin porraskuilu 6 m:n ruudukossa) täytetään myös
for _ in range(2):
    A = fl.reshape(ny, nx); Nb = np.minimum.reduce([np.roll(A, 1, 0), np.roll(A, -1, 0), np.roll(A, 1, 1), np.roll(A, -1, 1)])
    m2 = fillbox & (A.ravel() < Nb.ravel() - 1.0)
    fl[m2] = np.maximum(fl[m2], closed.ravel()[m2])
# penkka
cm = ok & (d < 3.6)
zc = np.where(cm, allz[np.minimum(idx, len(allz) - 1)] - 0.35, 1e9)
fl[cm] = np.minimum(fl[cm], zc[cm])
newH = fl.reshape(ny, nx)
ch = np.where(np.abs(newH - H) > 0.004)
ovr = []
for j, i in zip(*ch):
    ovr += [int(j * nx + i), int(round(newH[j, i] * 10))]
print('terrain overrides', len(ovr) // 2)
# portaali: täytetyn ja avoimen kaivannon raja asema-aukion puolella
openm = fillbox & ~fillm & (H.ravel() < 3.0)
op = pts[openm]
print('open pit cells', len(op), op.min(0) if len(op) else None, op.max(0) if len(op) else None)
out['ter'] = ovr
json.dump(out, open('rata_data.json', 'w'), separators=(',', ':'))

# ---------------------------------------------------------------- ulkokehän 18 m maaruudukko: raiteiden kohdalta solut pois (rata.js rakentaa niihin 6 m ruudukon)
OXS = 18.0; onx = int(round((OX1 - OX0) / OXS)); ony = int(round((OY1 - OY0) / OXS))
HW, YS, YN = 1012.3, -947.2, 1281.5
dense = []
for tr in TR:
    for p in resample(tr['S'], 4.0): dense.append(p)
kd2 = cKDTree(np.array(dense))
cells = []
for j in range(ony):
    for i in range(onx):
        x = OX0 + (i + 0.5) * OXS; y = OY0 + (j + 0.5) * OXS
        if abs(x) < HW - 9 and YS + 9 < y < YN - 9: continue
        if kd2.query([x, y])[0] < 17.5: cells.append(j * onx + i)
print('outer cells', len(cells))
out['osk'] = cells
json.dump(out, open('rata_data.json', 'w'), separators=(',', ':'))
