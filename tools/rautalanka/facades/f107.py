import json, sys
# 107 Yrjönkatu 25 (1927), Itsenäisyydenkatu end (north face, 12.1 m, wall line from raw.pkl). Measured 19.11.2026 on rectified Street View
# (Itsenäisyydenkatu 46 pano 61.4819137, 21.7955776 -> x -22.5 y -455.4, heading 165, pitch 8): scale 1.0, s = s_measured + 0.4 from the east
# (Yrjönkatu) corner, z = z_measured - 0.6 (pavement). Seen: s 0 .. 9; the third axis is completed by symmetry (3 axes 3.1 m apart).
# Two storeys of grey-beige render under a profiled cornice: three six-pane windows upstairs, a shop window, a panelled double door with a
# fanlight and steps, a second shop window; dark plinth. The long Yrjönkatu side is not measured.
A = (-18.109, -468.035); B = (-29.905, -465.227); L = 12.13
WALL = '#d0c9b9'; FR = '#e6dfc8'; GL = '#5a646a'; PL = '#55524e'
it = []
def box(s0, s1, z0, z1, d0, d1, c, k=None): it.append(['box', round(s0, 2), round(s1, 2), round(z0, 2), round(z1, 2), d0, d1, c] + ([k] if k else []))
box(0, L, 0.0, 0.65, 0.0, 0.06, PL)
box(0, L, 7.5, 7.75, 0.0, 0.12, '#ddd6c6'); box(0, L, 7.75, 8.2, 0.0, 0.25, '#ddd6c6'); box(0, L, 8.2, 8.5, 0.0, 0.45, '#cfc8b8')   # cornice in three steps
for s in (0.0, L - 0.5): box(s, s + 0.5, 0.65, 7.5, 0.0, 0.05, '#d8d1c1')    # corner pilasters
for c in (3.1, 6.3, 9.3):
    it.append(['winp', round(c - 0.6, 2), round(c + 0.6, 2), 5.6, 7.4, 2, FR, GL])
    for z in (6.2, 6.8): box(c - 0.6, c + 0.6, z - 0.025, z + 0.025, 0.04, 0.06, FR)   # six panes
for a, b in ((1.9, 4.35), (8.1, 10.5)): it.append(['winp', a, b, 1.35, 3.55, 1, FR, '#48535a'])
it.append(['door', 5.65, 6.9, 0.45, 3.0, '#d9d2bd']); it.append(['winp', 5.65, 6.9, 3.0, 3.6, 2, FR, GL])
box(6.25, 6.3, 0.45, 3.0, 0.02, 0.05, '#bdb6a2')
for j in range(3): box(5.3 - j * 0.15, 7.25 + j * 0.15, 0.3 - j * 0.15, 0.45 - j * 0.15, 0.0, 0.35 + j * 0.3, '#8f8c85')   # steps
e = {"id": 107, "note": "Yrjönkatu 25 (1927), Itsenäisyydenkatu end: grey-beige render, profiled cornice, three six-pane windows upstairs, two shop windows "
     "and a panelled double door with steps (SV Itsenäisyydenkatu 46 pano, rectified, 19.11.2026; west axis by symmetry)",
     "walls": [{"a": list(A), "b": list(B), "bare": WALL, "kind": "plaster", "items": it}]}
p = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] != 107] + [e]; open(p, 'w').write(json.dumps(F, indent=0)); print(len(it))
