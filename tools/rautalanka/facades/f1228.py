import json, sys
# 1228 Itsenäisyydenkatu 33 corner tower (white tiles, 6 storeys). The house has no shell of its own (lod2.js 'hide'): it is the west end
# (s 0 .. 12) of the south wall of the LoD2 shell of 1229 (Lääkäritalo, c064), so the entry is written under id 1229 with "bare_s"
# (measure the rest of 1229 into this same entry). Measured 19.11.2026 on rectified Street View (Itsenäisyydenkatu 44 pano 61.4815792,
# 21.7982185 -> x 118.21 y -492.56, heading 20, pitch 24): scale 1.08 by the shell's top (23.8 m): s = 1.54 + (s_measured - 1.54) * 1.08,
# z = z_measured * 1.08 - 0.41 (pavement). PV as in f166.py. The tower's west edge lies 1.8 m west of the shell wall's start (the shell
# is notched there): the west window pair is cut at s 0.
# White tiles; four upper floors 3.65 m apart with a window pair + a small window on each side of a blue vertical stripe; a window band
# with blue posts on the first floor; shop windows at street level; a green and a blue sign (blank boards).
A = (120.8, -474.625); B = (179.257, -488.221); LT = 11.97
WHT = '#eceeed'; ALU = '#d6d9d9'; GL = '#56626c'; BLUE = '#2f4fa8'
it = []; PV = 0.26
def box(s0, s1, z0, z1, d0, d1, c, k=None): it.append(['box', round(s0, 2), round(s1, 2), round(z0 + PV, 2), round(z1 + PV, 2), d0, d1, c] + ([k] if k else []))
for zb in (8.75, 12.4, 16.05, 19.7):
    for a, b, n in ((0.05, 0.92, 1), (1.17, 1.78, 1), (2.99, 3.56, 1), (3.87, 5.47, 2)): it.append(['winp', a, b, round(zb + PV, 2), round(zb + 1.6 + PV, 2), n, ALU, GL])
box(2.2, 2.42, 7.2, 21.4, 0.0, 0.06, BLUE)                                     # blue vertical stripe
for a, b in ((1.09, 5.21), (6.64, 10.77)): it.append(['winp', a, b, round(5.09 + PV, 2), round(6.84 + PV, 2), 3, ALU, GL])   # first-floor band
for s in (1.71, 2.68, 8.24, 9.12): box(s - 0.06, s + 0.06, 4.1, 7.15, 0.04, 0.12, BLUE)                                      # blue posts
for a, b in ((0.05, 5.21), (6.64, 10.77)): it.append(['glass', a, b, 0.48 + PV, 3.02 + PV, '#4a5a5e', 0.02])                 # shop windows
box(0.05, 5.2, 7.55, 8.3, 0.0, 0.05, '#7ed321')                                # green sign board (blank)
box(11.5, 11.9, 9.6, 13.9, 0.0, 0.15, BLUE)                                    # blue vertical sign (blank)
box(0, LT, -PV, 0.45, 0.0, 0.03, '#b9bbb9')                                    # light grey plinth
e = {"id": 1229, "note": "1228, the white-tiled corner tower at the west end of the Lääkäritalo shell (1229): four upper floors with windows on "
     "both sides of a blue stripe, first-floor window band with blue posts, shop windows, blank sign boards (SV Itsenäisyydenkatu 44 pano, "
     "rectified, 19.11.2026; only s 0..12 of the south wall - the rest of 1229 and the tower's west face are not measured)",
     "walls": [{"a": list(A), "b": list(B), "bare": WHT, "kind": "plaster", "bare_s": [0.0, LT + 0.1], "items": it}]}
p = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] not in (1228, 1229)] + [e]; open(p, 'w').write(json.dumps(F, indent=0)); print(len(it))
