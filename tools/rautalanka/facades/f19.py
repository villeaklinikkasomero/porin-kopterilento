import json, sys
# 19 Rautatienpuistokatu 10 (1954, c047): brown roughcast, three storeys, two stairs (wooden double doors, stair windows half a storey
# off), white window frames, and two cream rendered bays with wide windows: one at the north-east end, one 3 m before the south-west end.
# Measured 20.11.2026 on three rectified Street View frames, April 2026, pano "9 Rautatienpuistokatu" 61.479217, 21.791768
# (-> x -225.47 y -755.88; headings 85 / 136 / 185.57, pitch 14; the middle frame full size, the two end frames at half size).
# Calibrated on the shell: both ends -> s = 17.3 + (s_m - 17.0) * 0.904; pavement and eave (12.15) -> z = (z_m - 1.05) * 1.062
# (the street lies about 1 m above the shell's base: heights may be off by about 0.5 m, as at Nos 6, 8 and 12).
# Not seen: the second stair's door and the street level around it (behind a van) - drawn like the first stair's. Basement windows and
# drainpipes left out. The bays' projection (0.4 m) is estimated.
PV = 0.26; BR = '#8f7b64'; FR = '#e9e7e0'; GL = '#5f6b73'; WOOD = '#b0824a'; PL = '#77726a'; CRM = '#d8c9a0'
S = lambda s: 17.3 + (s - 17.0) * 0.904
Zf = lambda z: (z - 1.05) * 1.062
A = (-202.228, -753.749); B = (-224.007, -778.342); L = 32.85; it = []
def box(s0, s1, z0, z1, d0, d1, c, k=None): it.append(['box', round(max(0.0, s0), 2), round(min(L, s1), 2), round(z0 + PV, 2), round(z1 + PV, 2), d0, d1, c] + ([k] if k else []))
def win(s0, s1, z0, z1, n, fr=FR, gl=GL): it.append(['winp', round(s0, 2), round(s1, 2), round(z0 + PV, 2), round(z1 + PV, 2), n, fr, gl])
ROWS = [(Zf(3.23), Zf(4.65)), (Zf(6.34), Zf(7.7)), (Zf(9.41), Zf(10.78))]
STAIR = [(Zf(4.86), Zf(6.23), 2), (Zf(7.97), Zf(9.33), 2), (Zf(10.37), Zf(10.78), 1)]
box(0, L, -PV, 0.8, 0.0, 0.025, PL); box(0, L, 11.95, 12.15, 0.0, 0.3, '#ecebe6')
for a, b, n in ((3.32, 4.14, 1), (8.8, 10.1, 2), (11.5, 12.9, 2), (15.37, 16.74, 2), (18.1, 19.46, 2), (24.09, 24.94, 1)):
    for z0, z1 in ROWS: win(S(a), S(b), z0, z1, n)
for a, b, d0, d1 in ((5.86, 7.3, 5.17, 7.84), (21.1, 22.48, 20.45, 23.12)):          # stairs (the second door is NOT seen: as the first)
    for z0, z1, n in STAIR: win(S(a), S(b), z0, z1, n)
    box(S(d0), S(d1), -PV, Zf(3.3), 0.0, 0.025, WOOD, 'wood'); it.append(['door', round(S(d0) + 0.45, 2), round(S(d1) - 0.45, 2), 0.15 + PV, 2.2 + PV, '#8a5f33'])
    win(S(d0) + 0.08, S(d0) + 0.4, 0.5, 2.2, 1, WOOD, GL); win(S(d1) - 0.4, S(d1) - 0.08, 0.5, 2.2, 1, WOOD, GL)
for b0, b1, w0, w1 in ((-2.18, 1.99, -1.37, 1.5), (25.8, 29.92, 27.22, 29.08)):       # cream rendered bays with wide windows
    box(S(b0), S(b1), -PV, 11.6, 0.0, 0.4, CRM)
    for z0, z1 in ROWS:
        box(max(0.15, S(w0) - 0.1), S(w1) + 0.1, z0 - 0.1, z1 + 0.25, 0.4, 0.43, FR); box(max(0.25, S(w0)), S(w1), z0, z1 + 0.15, 0.43, 0.45, GL)
e = {"id": 19, "nobrick": True, "note": "Rautatienpuistokatu 10 (1954): brown roughcast, three storeys, two stairs (wooden doors, offset stair windows), white "
     "frames, a cream rendered bay with wide windows at the north-east end and another near the south-west end (SV April 2026, pano "
     "9 Rautatienpuistokatu, rectified 20.11.2026; the second stair's door was behind a van and is drawn like the first; basement windows "
     "left out; the other sides are not measured)",
     "walls": [{"a": list(A), "b": list(B), "bare": BR, "kind": "plaster", "items": it}]}
p = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] != 19] + [e]; open(p, 'w').write(json.dumps(F, indent=0)); print(len(it))
