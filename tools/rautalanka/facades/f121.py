import json, sys
# 121 Palojoenkulma (1988), Itsenäisyydenkatu 39 front (40.8 m, tan brick, wall line from raw.pkl). Measured 19.11.2026 on rectified Street View
# (Itsenäisyydenkatu 39 pano 61.481935, 21.7953921 -> x -32.39 y -453.0, heading 13, pitch 25; scale 1.0, pavement at z 0). Seen: s 19 .. 34, up to z 20;
# the facade is modular, so the measured module (5.7 m between brick piers, piers at s 23.75 and 29.45) is repeated over the whole front.
# Per module: brick plinth, a street-floor window band, a projecting dark glazed bay (X-braced panels, glazing, sloping sheet roof) at z 3.6-7.9,
# a full-width window row at 8.15-9.5, then rows of two ribbon windows 2.9 m apart with a small brick pier between them.
A = (-57.077, -436.61); B = (-17.33, -445.816); L = 40.8
BR = '#c4a274'; FR = '#2f3438'; GL = '#4a5a6a'; BL = '#aeb7bd'; DK = '#3a3d40'
it = []
def box(s0, s1, z0, z1, d0, d1, c, k=None): it.append(['box', round(s0, 2), round(s1, 2), round(z0, 2), round(z1, 2), d0, d1, c] + ([k] if k else []))
P = 5.7; piers = [0.95 + P * k for k in range(8)]
for c in piers: box(max(0, c - 0.25), min(L, c + 0.25), 0.0, 21.4, 0.0, 0.15, BR, 'brick')
box(0, L, 21.0, 21.4, 0.0, 0.2, '#8f7a5a'); box(0, L, 7.9, 8.05, 0.0, 0.08, '#a88c62', 'brick')
for c0, c1 in zip(piers, piers[1:]):
    a, b = c0 + 0.25, c1 - 0.25; m = (a + b) / 2
    it.append(['winp', round(a + 0.1, 2), round(b - 0.1, 2), 1.4, 3.3, 4, FR, BL])            # street-floor window band
    for x0, x1 in ((a, a + 0.42), (b - 0.42, b)): it.append(['glass', round(x0 + 0.04, 2), round(x1 - 0.04, 2), 3.4, 6.9, '#39444e'])   # glazed strips beside the bay
    ba, bb = a + 0.45, b - 0.45
    box(ba, bb, 3.6, 5.2, 0.0, 0.8, DK)                                                     # bay: braced panels
    box(m - 0.03, m + 0.03, 3.6, 5.2, 0.8, 0.83, '#23262a'); box(ba, bb, 5.17, 5.23, 0.8, 0.84, '#23262a')
    box(ba, bb, 5.2, 6.9, 0.0, 0.78, BL); box(ba, bb, 5.2, 6.9, 0.78, 0.8, '#8fa3b5')         # bay glazing (blinds behind)
    for j in range(5): x = ba + (bb - ba) * j / 4; box(x - 0.04, x + 0.04, 5.2, 6.9, 0.8, 0.84, FR)
    for j in range(4): box(ba, bb, 6.9 + j * 0.25, 7.15 + j * 0.25, 0.0, 0.8 - j * 0.2, '#55595c')   # sloping sheet roof in four steps
    it.append(['winp', round(a + 0.1, 2), round(b - 0.1, 2), 8.15, 9.5, 4, FR, GL])           # wide row over the bay
    for z in (10.95, 13.85, 16.75, 19.65):
        it.append(['winp', round(a + 0.2, 2), round(m - 0.2, 2), z, z + 1.0, 2, FR, GL]); it.append(['winp', round(m + 0.2, 2), round(b - 0.2, 2), z, z + 1.0, 2, FR, GL])
e = {"id": 121, "note": "Palojoenkulma (1988), Itsenäisyydenkatu 39: tan brick, seven modules between brick piers - street-floor window band, projecting dark "
     "glazed bay, wide window row, four rows of paired ribbon windows (SV Itsenäisyydenkatu 39 pano, rectified, 19.11.2026; module measured at s 19-34 and "
     "repeated)", "walls": [{"a": list(A), "b": list(B), "bare": BR, "kind": "brick", "items": it}]}
p = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] != 121] + [e]; open(p, 'w').write(json.dumps(F, indent=0)); print(len(it))
