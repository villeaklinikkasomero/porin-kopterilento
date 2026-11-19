import json, sys
# 13 the long four-storey slab on the south-east side of Rautatienpuistokatu (79.4 m, c061; address not identified). Street face:
# four window bands in dark navy strips between light grey ribbed spandrels, dark plinth.
# Measured 19.11.2026 on rectified wide Street View frames, April 2026: pano "4 Rautatienpuistokatu" 61.4805093, 21.794205
# (-> x -95.63 y -611.90, s 34.5, 14.9 m from the wall; sharp) and, for the two ends only (frames stayed blurred), panos
# 61.480712, 21.794593 and 61.4803068, 21.7938141; heading 132, pitch 18. Horizontal scale 1.0 (ends at s -0.2 and 80.0 against the
# shell's 0 and 79.4); heights z = 1.13 z_m - 1.36 (pavement at the wall and the shell's eave 15.05 - the frame's own scale put the
# eave at 14.5, so the heights may be up to 0.5 m off).
# Windows: a module of 15.3 m read at s 11 .. 59 (two wide windows, three narrow ones) and REPEATED to both ends, not seen sharply there.
# Left out: the small basement windows in the plinth, doors (none seen on this face).
A = (-61.531, -596.099); B = (-114.441, -655.249); L = 79.4; PV = 0.26
SP = '#c3c6cc'; NAVY = '#2c3140'; FR = '#e8e8e6'; GL = '#75838f'
it = []
def box(s0, s1, z0, z1, d0, d1, c, k=None): it.append(['box', round(s0, 2), round(s1, 2), round(z0 + PV, 2), round(z1 + PV, 2), d0, d1, c] + ([k] if k else []))
box(0, L, -PV, 0.7, 0.0, 0.03, '#3a3c40'); box(0, L, 14.6, 14.78, 0.0, 0.12, '#33363b')        # plinth, eave line
mod = ((0.0, 2.8, 2), (4.0, 6.75, 2), (8.1, 9.4, 1), (10.3, 11.8, 1), (13.1, 14.4, 1))
for z0, z1 in ((2.0, 3.65), (5.19, 6.86), (8.36, 9.97), (11.6, 13.25)):
    box(0.3, L - 0.3, z0, z1, 0.0, 0.02, NAVY)
    for k in range(-1, 6):
        for a, b, n in mod:
            s0 = max(14.0 + 15.3 * k + a, 0.5); s1 = min(14.0 + 15.3 * k + b, L - 0.5)
            if s1 - s0 > 0.9: it.append(['winp', round(s0, 2), round(s1, 2), round(z0 + 0.12 + PV, 2), round(z1 - 0.12 + PV, 2), n, FR, GL])
e = {"id": 13, "nobrick": True, "note": "Four-storey slab on Rautatienpuistokatu (south-east side): four window bands in dark navy strips between light grey "
     "spandrels, dark plinth (SV April 2026, pano 4 Rautatienpuistokatu, wide frame, rectified 19.11.2026; the window module is read at "
     "s 11..59 and repeated to the ends; basement windows left out; the other sides are not measured)",
     "walls": [{"a": list(A), "b": list(B), "bare": SP, "kind": "plaster", "items": it}]}
p = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] != 13] + [e]; open(p, 'w').write(json.dumps(F, indent=0)); print(len(it))
