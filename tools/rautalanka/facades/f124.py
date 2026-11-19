import json, sys
# 124 Rautatienpuistokatu 5, former Teljä vocational school (1938): white render, three storeys over a brick basement, red-brown
# window frames. The street front is two wings, the north-east one set 4.7 m back. First the south-west wing (36.3 m):
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
# ---- north-east wing (50.45 m, set 4.7 m back from the south-west wing). Measured 19.11.2026 on two rectified wide frames, April 2026:
# panos "4 Rautatienpuistokatu" 61.4805093, 21.794205 (-> x -95.63 y -611.90) and "2 Rautatienpuistokatu" 61.480712, 21.794593
# (-> x -74.96 y -589.28), heading 313, pitch 18. Scale 1.09 / 1.075 about the cameras (s 10.9 and 41.55): the re-entrant corner on s 0,
# the north-east end on the shell's end, eave 15.4; the two frames disagree by about 0.7 m around s 32 (averaged).
# Eleven window axes (2.23 m apart), the entrance at s 25.0 .. 28.8 (flat canopy on side walls, tall stair window above), nine axes
# (2.16 m apart) to the north-east end. Rows as on the other wing, 0.1 .. 0.25 m higher as measured. Not measured: the portico in the
# re-entrant corner (on the south-west wing's 4.7 m end wall) and everything behind the trees' trunks (axes repeated at the same pitch).
A2 = (-114.398, -609.46); B2 = (-80.242, -572.33); L2 = 50.45; i2 = []; it0 = it; it = i2
box(0, L2, -PV, 1.67, 0.0, 0.025, BR, 'brick'); box(0, L2, 3.08, 3.17, 0.0, 0.05, WH); box(0, L2, 14.9, 15.1, 0.0, 0.25, WH)
for c in [1.27 + 2.227 * k for k in range(11)] + [32.1 + 2.16 * k for k in range(9)]:
    for z0, z1 in ((3.25, 4.95), (7.15, 8.9), (11.05, 12.75)): win(c - 0.6, c + 0.6, z0, z1, 2)
    win(c - 0.55, c + 0.55, 0.73, 1.4, 2, '#e9e6de', '#4a5257')
box(24.8, 29.0, 5.15, 5.7, 0.0, 2.0, '#d9d6cd')                                # entrance canopy
box(24.8, 25.15, -PV, 5.15, 0.0, 1.9, WH); box(28.65, 29.0, -PV, 5.15, 0.0, 1.9, WH)   # its side walls
it.append(['door', 25.6, 28.2, 0.6 + PV, 4.2 + PV, '#4a3a33']); win(25.9, 27.9, 0.9, 3.9, 3, FR, '#3f474c')   # recessed doorway, glazed doors
box(25.15, 28.65, -PV, 0.6, 0.0, 1.9, '#b9b5ab')                               # steps / landing
win(25.36, 28.45, 5.98, 9.5, 3); win(25.36, 28.45, 9.5, 13.05, 3)              # tall stair window (two tiers of three)
it = it0
e = {"id": 124, "nobrick": True, "note": "Rautatienpuistokatu 5, former Teljä vocational school (1938): white render, red-brown framed windows on three floors, brick "
     "basement with windows, sill band, cornice; south-west wing 15 axes, north-east wing 11 + 9 axes around an entrance with a canopy and a tall "
     "stair window (SV April 2026, three wide frames, rectified 19.11.2026; the portico in the re-entrant corner is not measured)",
     "walls": [{"a": list(A), "b": list(B), "bare": WH, "kind": "plaster", "items": it},
               {"a": list(A2), "b": list(B2), "bare": WH, "kind": "plaster", "items": i2}]}
p = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] != 124] + [e]; open(p, 'w').write(json.dumps(F, indent=0)); print(len(it), len(i2))
