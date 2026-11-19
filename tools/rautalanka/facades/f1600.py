import json, sys
# 1600 Antinkatu 8 (one-storey restaurant, green mansard roof with round dormers): west edge 25.1,189.4 -> 21.6,174.1, 15.7 m, s from the
# north. Measured 19.11.2026 on rectified Street View (Antinkatu 9 panos 61.4876768, 21.7963367 -> x 17.94 y 186.8 and 61.4875892,
# 21.7962959 -> x 15.76 y 177.04). Rectified length 14.9 m and pavement at z 1.0: s = 1.054 * s_m, z = 1.054 * (z_m - 1.0).
L = 15.7; K = 1.054; it = []
def box(s0, s1, z0, z1, d0, d1, c, k=None): it.append(['box', round(s0, 2), round(s1, 2), round(z0, 2), round(z1, 2), d0, d1, c] + ([k] if k else []))
WALL = '#98a28d'; PIER = '#a3ad98'; DK = '#1d2022'; FRM = '#4a564d'; ROOF = '#82937d'
piers = [(0.0, 0.3), (2.7, 3.0), (5.3, 5.9), (8.0, 8.56), (11.3, 11.8), (14.3, 14.9)]
wins = [(0.3, 2.7), (3.0, 5.3), (8.56, 11.3), (11.8, 14.3)]; door = (5.9, 8.0)
box(0, L, 0.0, 0.12, 0.0, 0.08, '#6b7263')                                   # low plinth
for a, b in wins:                                                           # shop windows: dark glass, a gridded top light, warm panel at the foot
    a, b = a * K, b * K
    it.append(['glass', round(a, 2), round(b, 2), 0.12, 2.85, DK])
    box(a, b, 0.12, 0.72, 0.02, 0.03, '#7d6344')
    box(a, b, 2.05, 2.13, 0.02, 0.07, FRM)
    for j in range(1, 6): m = a + (b - a) * j / 6; box(m - 0.025, m + 0.025, 2.13, 2.85, 0.02, 0.06, FRM)
    box(a, b, 2.45, 2.5, 0.02, 0.06, FRM)
    c = (a + b) / 2; box(c - 0.6, c + 0.6, 1.3, 1.55, 0.02, 0.035, '#e4e4de')   # white lettering on the glass
a, b = door[0] * K, door[1] * K
it.append(['door', round(a, 2), round(b, 2), 0.0, 2.85, '#131415'])         # recessed entrance behind a folding gate
k = a + 0.2
while k < b - 0.1: box(k, k + 0.03, 0.05, 2.6, 0.02, 0.04, '#3c3d3b'); k += 0.22
for a, b in piers: box(a * K, min(L, b * K), 0.0, 2.9, 0.0, 0.12, PIER)     # render piers
box(0, L, 2.95, 3.22, 0.0, 0.25, '#2c3030')                                 # dark awning box along the whole front
box(0, L, 4.1, 4.7, 0.0, 0.18, ROOF)                                        # foot of the green sheet-metal mansard
for c in (3.2, 8.0, 12.6):                                                  # three dormers with round windows (drawn square)
    box(c - 0.75, c + 0.75, 3.85, 4.95, 0.18, 0.3, ROOF); box(c - 0.5, c + 0.5, 4.95, 5.15, 0.18, 0.3, ROOF)
    box(c - 0.36, c + 0.36, 4.05, 4.77, 0.3, 0.32, '#e6e6e0'); box(c - 0.28, c + 0.28, 4.13, 4.69, 0.32, 0.33, '#4d5960')
e = {"id": 1600, "note": "Antinkatu 8, one-storey restaurant: grey-green render piers, four dark shop windows with gridded top lights, a recessed "
     "entrance with a folding gate, a dark awning box, green sheet-metal mansard with three round-windowed dormers (SV Antinkatu 9 panos, "
     "rectified, 19.11.2026)", "walls": [{"a": [25.1, 189.4], "b": [21.6, 174.1], "bare": WALL, "kind": "plaster", "items": it}]}
p = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] != 1600] + [e]; open(p, 'w').write(json.dumps(F, indent=0)); print(len(it))
