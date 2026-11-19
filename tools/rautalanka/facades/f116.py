import json, sys
# 116 Antinlinna (1929), Itsenäisyydenkatu front (north face, 32.2 m). Measured 19.11.2026 on rectified Street View: Itsenäisyydenkatu 41 pano
# 61.4820789, 21.7940872 -> x -101.9 y -436.9 (headings 140 / 194 / 245, pitch 12). The rectified front is 33.6 m with the pavement at z 0.3:
# s = (s_measured + 1.0) * 0.952 from the east corner, z = (z_measured - 0.3) * 0.93 (eave on the scan's 13.5 m). Wall line from raw.pkl.
# Cream-ochre render over a dark plinth; eight window axes on two upper floors tied together by brown surrounds with a balustrade panel below
# and an ornament panel between (surrounds only 2.5 cm proud: a winp frame sits at 3 cm and was hidden behind thicker ones); granite main portal with two columns up to an attic block (the name plate is drawn as a plain panel),
# a smaller side portal, small street-floor windows east of the portal and two large shop windows west of it.
A = (-90.018, -451.231); B = (-121.309, -443.652); L = 32.2
WALL = '#e8cf98'; BRN = '#5a4038'; GRA = '#7a5c58'; PAN = '#ead9ac'; GRN = '#7c8a4a'; WH = '#f1efe8'; GL = '#5b6770'; PL = '#3a3634'
it = []
def box(s0, s1, z0, z1, d0, d1, c, k=None): it.append(['box', round(s0, 2), round(s1, 2), round(z0, 2), round(z1, 2), d0, d1, c] + ([k] if k else []))
box(0, L, 0.0, 0.85, 0.0, 0.06, PL)                                         # plinth
box(0, L, 5.0, 5.25, 0.0, 0.1, BRN)                                         # string course over the street floor
box(0, L, 12.9, 13.5, 0.0, 0.35, '#efdcae'); box(0, L, 13.42, 13.56, 0.0, 0.45, '#cdb98a')   # eaves cornice
for c in (2.09, 6.28, 10.38, 14.57, 17.8, 21.04, 25.13, 29.13):
    box(c - 1.05, c + 1.05, 5.25, 11.25, 0.0, 0.025, BRN)                    # brown surround tying the two floors
    box(c - 0.12, c + 0.12, 11.25, 11.6, 0.0, 0.08, BRN)                    # keystone
    box(c - 0.8, c + 0.8, 5.3, 5.78, 0.025, 0.06, PAN)                       # balustrade panel
    for j in range(6): box(c - 0.7 + j * 0.25, c - 0.58 + j * 0.25, 5.34, 5.74, 0.06, 0.08, GRN)
    box(c - 0.8, c + 0.8, 7.95, 8.9, 0.025, 0.06, PAN); box(c - 0.3, c + 0.3, 8.3, 8.5, 0.06, 0.07, GRN)   # ornament panel
    for z0, z1 in ((5.83, 7.63), (9.15, 10.88)):
        it.append(['winp', round(c - 0.75, 2), round(c + 0.75, 2), z0, z1, 3, WH, GL])
        box(c - 0.75, c + 0.75, z1 - 0.52, z1 - 0.46, 0.04, 0.07, WH)       # transom
for a, b in ((1.71, 3.05), (8.19, 9.42), (9.9, 11.04), (11.61, 12.76), (14.09, 15.23)):
    box(a - 0.22, b + 0.22, 2.2, 4.46, 0.0, 0.025, BRN); it.append(['winp', a, b, 2.42, 4.24, 2, WH, GL])   # street-floor windows
# side portal
box(4.86, 7.24, 0.0, 4.6, 0.0, 0.12, GRA); it.append(['door', 5.5, 6.6, 0.1, 3.3, '#6a4a2c']); it.append(['glass', 5.5, 6.6, 3.35, 4.0, '#4a555c'])
# main portal: granite base, two columns up to the attic, oak door
box(15.71, 20.37, 0.0, 5.25, 0.0, 0.25, GRA)
for a, b in ((15.9, 16.56), (19.33, 19.99)): box(a, b, 5.25, 12.6, 0.0, 0.45, GRA); box(a - 0.1, b + 0.1, 12.6, 12.95, 0.0, 0.55, GRA)
box(17.14, 18.37, 0.1, 3.1, 0.25, 0.28, '#7a5630'); box(17.14, 18.37, 3.15, 3.75, 0.25, 0.28, '#4a555c')   # oak door and fanlight on the granite face
box(15.85, 20.2, 13.5, 14.75, -0.3, 0.45, '#e6d3a2'); box(16.2, 19.85, 13.75, 14.3, 0.45, 0.48, '#d9c48f')   # attic block, name plate as a plain panel
box(15.85, 20.2, 14.75, 14.9, -0.35, 0.5, '#cdb98a')
for a, b in ((20.56, 24.28), (25.32, 29.32)):                               # shop windows
    box(a - 0.18, b + 0.18, 0.95, 4.2, 0.0, 0.025, BRN); it.append(['glass', a, b, 1.1, 4.0, '#39434a', 0.07])
    box((a + b) / 2 - 0.05, (a + b) / 2 + 0.05, 1.1, 4.0, 0.07, 0.1, BRN); box(a, b, 3.25, 3.33, 0.07, 0.1, BRN)
e = {"id": 116, "note": "Antinlinna (1929), Itsenäisyydenkatu front: cream-ochre render, eight window axes in brown two-storey surrounds with balustrade and "
     "ornament panels, granite main portal with two columns and an attic block, side portal, two shop windows (SV Itsenäisyydenkatu 41 pano, rectified, "
     "19.11.2026)", "walls": [{"a": list(A), "b": list(B), "bare": WALL, "kind": "plaster", "items": it}]}
p = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] != 116] + [e]; open(p, 'w').write(json.dumps(F, indent=0)); print(len(it))
