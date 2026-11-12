"""Road and railway bridges over land: the 2 m elevation model is bare ground, so it has the cut under every bridge, and the road or track in
the aerial photo (and the cars) sank into it.  Every OpenStreetMap bridge that is not over the river gets a deck: a straight line between the
ground beyond its two ends.  The game draws the deck with the aerial photo on it, edge beams and parapets; the ground below keeps the elevation
model, so the road or railway underneath stays in its cutting.  Only the object height field (hs: cars, trees) is lifted to the deck along it.
  python3 bridges_fix.py osm_extract.json terrain.js out_terrain.js   (run it on the terrain.js from dem_build.py, not on an already fixed one)"""
import sys, json, base64, math, numpy as np
osm, src, dst = sys.argv[1:4]
T = json.loads(open(src).read()[len('export default '):].rstrip().rstrip(';'))
nx, ny, g, x0, y0 = T['nx'], T['ny'], T['g'], T['x0'], T['y0']
dec = lambda k: np.frombuffer(base64.b64decode(T[k]), dtype='<i2').reshape(ny, nx).astype(np.float64) / 10
HG, HS = dec('hg'), dec('hs'); HG0 = HG.copy()
def bil(A, x, y):
    fx = min(nx - 1.001, max(0, (x - x0) / g)); fy = min(ny - 1.001, max(0, (y - y0) / g)); i, j = int(fx), int(fy); u, v = fx - i, fy - j
    return (A[j, i] * (1 - u) + A[j, i + 1] * u) * (1 - v) + (A[j + 1, i] * (1 - u) + A[j + 1, i + 1] * u) * v
s = open('/home/claude/pori/river.js').read(); RIV = json.loads(s[s.index('{'):s.rindex('}') + 1]); M = RIV['mask']
ra = np.unpackbits(np.frombuffer(base64.b64decode(M['b']), dtype=np.uint8))[:M['nx'] * M['ny']].reshape(M['ny'], M['nx'])
C = json.loads((lambda t: t[t.index('{'):t.rindex('}') + 1])(open('/home/claude/pori/city.js').read()))
def wet(x, y):
    i = int((x - C['ox0']) / M['g']); j = int((y - C['oy0']) / M['g']); return 0 <= i < M['nx'] and 0 <= j < M['ny'] and ra[j, i]
O = json.load(open(osm)); XY = lambda q: ((q[0] - 21.796) * 53278, (q[1] - 61.486) * 111437)
HW = dict(motorway=7, trunk=6.5, trunk_link=4, primary=6, secondary=5, tertiary=4.5, unclassified=4, residential=4, service=3, track=2.5, cycleway=2, footway=1.8, path=1.5, steps=1.5, rail=3.2)
walls = []; done = []
for kind, L in (('rail', O['rail']), ('road', O['hb'])):
    for w in L:
        if not w['b']: continue
        P = [XY(q) for q in w['g']]; Ln = sum(math.dist(a, b) for a, b in zip(P, P[1:]))
        if Ln < 6: continue
        pts = []
        for a, b in zip(P, P[1:]):
            n = max(1, int(math.dist(a, b) / 1.5)); pts += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
        pts.append(P[-1])
        if any(wet(*p) for p in pts): continue                                          # over the river: the game has its own decks there
        d0 = (P[0][0] - P[1][0], P[0][1] - P[1][1]); d1 = (P[-1][0] - P[-2][0], P[-1][1] - P[-2][1])
        e0 = (P[0][0] + d0[0] / math.hypot(*d0) * 4, P[0][1] + d0[1] / math.hypot(*d0) * 4); e1 = (P[-1][0] + d1[0] / math.hypot(*d1) * 4, P[-1][1] + d1[1] / math.hypot(*d1) * 4)
        za, zb = bil(HG0, *e0), bil(HG0, *e1)
        cum = [0.0]
        for a, b in zip(pts, pts[1:]): cum.append(cum[-1] + math.dist(a, b))
        deck = [za + (zb - za) * (c / cum[-1]) for c in cum]
        cut = max(dk - bil(HG0, *p) for dk, p in zip(deck, pts))
        if cut < 1.2: continue                                                          # no real underpass under it
        hw = HW.get(w['k'], 3.5) + 0.5; sh = 4.0
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        i0 = max(0, int((min(xs) - hw - sh - x0) / g) - 1); i1 = min(nx - 1, int((max(xs) + hw + sh - x0) / g) + 2)
        j0 = max(0, int((min(ys) - hw - sh - y0) / g) - 1); j1 = min(ny - 1, int((max(ys) + hw + sh - y0) / g) + 2)
        A = np.array(pts)
        for j in range(j0, j1 + 1):
            for i in range(i0, i1 + 1):
                X, Y = x0 + i * g, y0 + j * g
                best = None
                for k in range(len(pts) - 1):
                    ax, ay = pts[k]; bx, by = pts[k + 1]; dx, dy = bx - ax, by - ay; l2 = dx * dx + dy * dy or 1
                    t = max(0, min(1, ((X - ax) * dx + (Y - ay) * dy) / l2)); px, py = ax + dx * t, ay + dy * t; d = math.hypot(X - px, Y - py)
                    if best is None or d < best[0]: best = (d, deck[k] + (deck[k + 1] - deck[k]) * t)
                d, z = best
                if d > hw + sh: continue
                wgt = 1.0 if d <= hw else 0.5 + 0.5 * math.cos(math.pi * (d - hw) / sh)
                if HS[j, i] < z: HS[j, i] = HS[j, i] + (z - HS[j, i]) * wgt     # ground (hg) untouched: the underpass stays
        walls.append([round(hw, 2)] + [v for p, dk in zip(pts[::2] + ([pts[-1]] if (len(pts) - 1) % 2 else []), deck[::2] + ([deck[-1]] if (len(pts) - 1) % 2 else [])) for v in (round(p[0], 2), round(p[1], 2), round(dk, 2))])
        done.append((kind, w['k'], w.get('n', ''), round(Ln), round(cut, 1), round(P[0][0]), round(P[0][1])))
enc = lambda A: base64.b64encode(np.round(A * 10).astype('<i2').tobytes()).decode()
T['hg'] = enc(HG); T['hs'] = enc(HS)
T.pop('bw', None); T['bd'] = walls                                                     # bridge decks: half width, then x, y, deck z per point
open(dst, 'w').write('export default ' + json.dumps(T, separators=(',', ':')) + ';\n')
for d in sorted(done, key=lambda d: -d[4]): print(d)
print('bridges', len(done))
