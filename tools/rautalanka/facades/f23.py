import json, sys
# 23 Rautatienpuistokatu 6 (1954, c061): brown roughcast, three storeys; the street face is two shell walls - a lower north-east part
# (12.7 m, 0.4 m back) and the main part (40.0 m) - with two stairs (wooden double doors, stair windows half a storey off), white window
# frames and a cream rendered bay with wide windows near the south-west end.
# Measured 20.11.2026 on three rectified Street View frames, April 2026, pano "6 Rautatienpuistokatu" 61.4798294, 21.7929287
# (-> x -163.62 y -687.59; headings 85 / 135.49 / 186.06, pitch 14; all three sharp - turned by dragging in the loaded pano).
# Calibrated on the shell: both ends -> s = 35.2 + (s_m - 35.2) * 0.94 along the whole face; pavement and eave (12.0) ->
# z = (z_m - 0.97) * 1.034 (the street lies about 1 m above the shell's base, so heights may be off by about 0.5 m, as at Nos 8 and 12).
# Left out: basement windows, drainpipes, the small side door at the step between the parts. The bay's projection (0.4 m) is estimated.
PV = 0.26; BR = '#927a60'; FR = '#e9e7e0'; GL = '#5f6b73'; WOOD = '#b0824a'; PL = '#77726a'; CRM = '#d8c9a0'
S = lambda s: 35.2 + (s - 35.2) * 0.94
Zf = lambda z: (z - 0.97) * 1.034
def mk():
    it = []
    def box(s0, s1, z0, z1, d0, d1, c, k=None): it.append(['box', round(s0, 2), round(s1, 2), round(z0 + PV, 2), round(z1 + PV, 2), d0, d1, c] + ([k] if k else []))
    def win(s0, s1, z0, z1, n, fr=FR, gl=GL): it.append(['winp', round(s0, 2), round(s1, 2), round(z0 + PV, 2), round(z1 + PV, 2), n, fr, gl])
    return it, box, win
ROWS = [(Zf(3.26), Zf(4.66)), (Zf(6.3), Zf(7.75)), (Zf(9.36), Zf(10.8))]
STAIR = [(Zf(4.98), Zf(6.34), 2), (Zf(8.02), Zf(9.38), 2), (Zf(10.4), Zf(10.8), 1)]
# ---- north-east part: s 0 .. 12.7 of the face
A1 = (-128.432, -672.444); B1 = (-136.824, -681.927); L1 = 12.66
i1, box, win = mk()
box(0, L1, -PV, 0.8, 0.0, 0.025, PL); box(0, L1, 11.6, 11.78, 0.0, 0.3, '#ecebe6')
for a, b, n in ((0.22, 2.37, 3), (3.62, 5.05, 2), (6.38, 7.85, 2)):
    for z0, z1 in ROWS: win(S(a), S(b), z0 - 0.15, z1 - 0.15, n)
# ---- main part: s 12.7 .. 52.7, its own wall line (1.2 m in front of the first at the step)
A2 = (-138.006, -680.88); B2 = (-164.549, -710.867); L2 = 40.05; O = 12.7
i2, box, win = mk()
T = lambda s: S(s) - O
box(0, L2, -PV, 0.8, 0.0, 0.025, PL); box(0, L2, 11.8, 12.0, 0.0, 0.3, '#ecebe6')
for a, b, n in ((11.96, 13.4, 2), (15.08, 17.12, 3), (18.77, 20.9, 3), (22.49, 23.9, 2), (28.55, 29.98, 2), (31.24, 32.63, 2), (35.07, 36.5, 2), (37.68, 39.08, 2), (43.48, 44.45, 1)):
    for z0, z1 in ROWS: win(T(a), T(b), z0, z1, n)
for a, b, d0, d1 in ((25.5, 27.0, 24.9, 27.0), (40.54, 42.05, 40.1, 42.6)):          # the two stairs
    for z0, z1, n in STAIR: win(T(a), T(b), z0, z1, n)
    box(T(d0), T(d1), -PV, Zf(3.47), 0.0, 0.025, WOOD, 'wood'); i2.append(['door', round(T(d0) + 0.45, 2), round(T(d1) - 0.45, 2), 0.15 + PV, 2.2 + PV, '#8a5f33'])
    win(T(d0) + 0.08, T(d0) + 0.4, 0.5, 2.2, 1, WOOD, GL); win(T(d1) - 0.4, T(d1) - 0.08, 0.5, 2.2, 1, WOOD, GL)
box(T(45.16), T(48.84), -PV, 11.3, 0.0, 0.4, CRM)                               # cream rendered bay
for z0, z1 in ROWS: i2.append(['winp', round(T(46.6), 2), round(T(48.4), 2), round(z0 + PV, 2), round(z1 + 0.1 + PV, 2), 2, FR, GL]); i2[-1] = ['box', round(T(46.5), 2), round(T(48.5), 2), round(z0 - 0.1 + PV, 2), round(z1 + 0.2 + PV, 2), 0.4, 0.43, FR]; box(T(46.6), T(48.4), z0, z1 + 0.1, 0.43, 0.45, GL)
e = {"id": 23, "nobrick": True, "note": "Rautatienpuistokatu 6 (1954): brown roughcast, three storeys, a lower north-east part and the main part with two stairs "
     "(wooden doors, offset stair windows), white frames, a cream rendered bay with wide windows near the south-west end (SV April 2026, pano "
     "6 Rautatienpuistokatu, three sharp frames, rectified 20.11.2026; basement windows left out; the other sides are not measured)",
     "walls": [{"a": list(A1), "b": list(B1), "bare": BR, "kind": "plaster", "items": i1},
               {"a": list(A2), "b": list(B2), "bare": BR, "kind": "plaster", "items": i2}]}
p = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] != 23] + [e]; open(p, 'w').write(json.dumps(F, indent=0)); print(len(i1), len(i2))
