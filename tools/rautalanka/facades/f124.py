import json, sys
# 124 Rautatienpuistokatu 5, former Teljä vocational school (1938): white render, three storeys over a brick basement, red-brown
# window frames. The street front is two wings in a shallow V; THIS FILE HAS THE SOUTH-WEST WING ONLY (36.3 m):
# the north-east wing (-114.398,-609.46)->(-80.242,-572.33), 50.5 m, is not measured yet (browser connection lost 19.11.2026).
# Measured 19.11.2026 on a rectified Street View frame, April 2026 (leafless): pano "5 Rautatienpuistokatu" 61.4803068, 21.7938141
# -> x -116.46 y -634.75, heading 313, pitch 18, wide frame 800 x 480 (vertical fov 90; 16 px/m - coarser than the upright frames).
# Calibrated on the shell: corners s_m 2.0 / 35.0 -> s = 0.3 + (s_m - 2.0) * 1.082; pavement and eave (15.3) -> z = 1.114 z_m - 0.75.
# 15 window axes 2.07 m apart on three floors, basement windows under each axis in the brick plinth, a thin sill band under the
# ground-floor windows, plain cornice. PV as in f166.py.
A = (-135.486, -639.38); B = (-110.914, -612.67); L = 36.3; PV = 0.26
WH = '#f2f0ea'; FR = '#9c5747'; GL = '#59646b'; BR = '#a8694c'
it = []
def box(s0, s1, z0, z1, d0, d1, c, k=None): it.append(['box', round(s0, 2), round(s1, 2), round(z0 + PV, 2), round(z1 + PV, 2), d0, d1, c] + ([k] if k else []))
def win(s0, s1, z0, z1, n, fr=FR, gl=GL): it.append(['winp', round(s0, 2), round(s1, 2), round(z0 + PV, 2), round(z1 + PV, 2), n, fr, gl])
box(0, L, -PV, 1.67, 0.0, 0.025, BR, 'brick')                                  # brick basement
box(0, L, 3.08, 3.17, 0.0, 0.05, WH)                                           # sill band
box(0, L, 14.8, 15.0, 0.0, 0.25, WH)                                           # cornice
for k in range(15):
    c = 4.38 + 2.071 * k
    for z0, z1 in ((3.23, 4.82), (7.05, 8.72), (10.84, 12.5)): win(c - 0.6, c + 0.6, z0, z1, 2)
    win(c - 0.55, c + 0.55, 0.73, 1.4, 2, '#e9e6de', '#4a5257')                 # basement window
e = {"id": 124, "nobrick": True, "note": "Rautatienpuistokatu 5, former Teljä vocational school (1938), SOUTH-WEST WING ONLY: white render, 15 axes of red-brown "
     "framed windows on three floors, brick basement with windows, sill band, cornice (SV April 2026, pano 5 Rautatienpuistokatu, wide frame, "
     "rectified 19.11.2026). The north-east wing (50.5 m) is not measured",
     "walls": [{"a": list(A), "b": list(B), "bare": WH, "kind": "plaster", "items": it}]}
p = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] != 124] + [e]; open(p, 'w').write(json.dumps(F, indent=0)); print(len(it))
