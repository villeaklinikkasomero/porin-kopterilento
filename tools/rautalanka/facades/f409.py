import json, sys, math
# 409 Antinkatu 22 (flats, cream brick, c. 2000), west front on Antinkatu. Measured 19.11.2026 on rectified Street View: Antinkatu 22 pano
# 61.4827469, 21.7938609 -> x -113.96 y -362.5 (headings 55 / 103 / 150, pitch 22-25). Pavement at z 0.3, the front 24.65 m long from the
# north corner to the end of the south balcony stack; drawn on the LoD2 wall line (24.1 m incl. the set-back gateway part): s = 0.962 s_measured,
# z = z_measured - 0.3. Six storeys of 3.05 m: two window columns, a 5.8 m stack of glazed balconies on a round column, two window columns,
# a second balcony stack over the gateway to the yard. Windows are two-light with a white panel under them; grey concrete plinth.
A = (-100.174, -350.324); B0 = (-104.989, -370.985); Lb = math.hypot(B0[0] - A[0], B0[1] - A[1]); L = 24.1
B = (round(A[0] + (B0[0] - A[0]) / Lb * L, 3), round(A[1] + (B0[1] - A[1]) / Lb * L, 3))
BRICK = '#dccfb6'; WH = '#efede8'; FR = '#e8e4da'; GL = '#5d6f80'; PL = '#9b968d'; RAIL = '#b4c2bd'; BGL = '#b9c6cc'
it = []
def box(s0, s1, z0, z1, d0, d1, c, k=None): it.append(['box', round(s0, 2), round(s1, 2), round(z0, 2), round(z1, 2), d0, d1, c] + ([k] if k else []))
box(0, 20.3, 0.0, 1.2, 0.0, 0.05, PL)                                       # plinth
box(0, L, 21.45, 21.9, 0.0, 0.4, '#d9d9d6')                                 # eaves
for a, b in ((2.07, 3.27), (4.71, 6.59), (13.9, 15.87), (17.17, 19.14)):
    for k in range(6):
        z = 2.5 + 3.05 * k
        box(a, b, z - 1.15, z, 0.0, 0.03, WH)                               # white panel under the window
        it.append(['winp', a, b, z, z + 1.8, 2 if b - a > 1.5 else 1, FR, GL])
for a, b in ((13.9, 15.6), (17.3, 18.5)): it.append(['door', a + 0.1, b - 0.1, 0.3, 0.95, '#5a5d5e'])   # plinth vents
lv = [5.3 + 3.05 * k for k in range(5)]
for a, b in ((6.88, 12.7), (20.3, 23.7)):
    for z in lv + [2.25]: it.append(['winp', round(a + 0.3, 2), round(b - 0.3, 2), z + 0.1, z + 2.4, 4 if b - a > 4 else 3, FR, '#4f5f6c'])   # glazed balcony doors
    it.append(['balc', a, b, lv, 20.5, 1.5, 0.0, RAIL, BGL, 1.1, 2.85])
box(6.88, 12.7, 2.0, 2.25, 0.0, 1.5, WH)                                    # raised ground-floor terrace under the first stack
box(6.88, 12.7, 2.25, 3.25, 1.45, 1.5, BGL)
box(9.6, 10.0, 0.0, 5.1, 1.0, 1.4, '#b5b0a6')                               # round concrete column (square here)
it.append(['door', 20.5, 23.5, 0.0, 4.6, '#26282a'])                        # gateway to the yard (drawn dark)
box(21.9, 22.2, 0.0, 5.1, 1.0, 1.3, '#b5b0a6')
e = {"id": 409, "note": "Antinkatu 22, six-storey flats in cream brick: window columns with white panels, two stacks of glazed balconies, the south one "
     "over the gateway; grey plinth (SV Antinkatu 22 pano, rectified, 19.11.2026)",
     "walls": [{"a": list(A), "b": list(B), "bare": BRICK, "kind": "plaster", "items": it}]}
p = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] != 409] + [e]; open(p, 'w').write(json.dumps(F, indent=0)); print(len(it), B)
