import json, sys
# 1725 Antinkatu 10 (west edge 21.6,174.1 -> 17.1,154.3, 20.3 m), two-storey shop wing. Measured 19.11.2026 on rectified Street View
# (Antinkatu 11 pano 61.4874992, 21.7962552 -> x 13.63 y 167.06, headings 50 / 103 / 155). The pano stands only 6 m from the wall and the
# rectified front came out 18.5 m long with the pavement at z 0.9: the camera is 10 % further away than its coordinates say, so
# s = (s_measured - 0.06) * 1.1 (ends on the footprint corners) and z = 1.1 * z_measured - 0.99 (from the pavement). Eaves at 6.7 m.
L = 20.3; it = []
def box(s0, s1, z0, z1, d0, d1, c, k=None): it.append(['box', round(s0, 2), round(s1, 2), round(z0, 2), round(z1, 2), d0, d1, c] + ([k] if k else []))
TILE = '#d6cbb4'; BROWN = '#5b4b3d'; FR = '#e9e8e2'; GL = '#7d8990'; DG = '#23282b'; RED = '#b5343a'
piers = [(0.0, 0.42), (3.67, 4.11), (7.74, 8.18), (11.98, 12.36), (16.16, 16.54), (19.9, L)]
bays = [(4.11, 7.74), (8.18, 11.98), (12.36, 16.16), (16.54, 19.9)]
box(0, L, 0.0, 0.3, 0.0, 0.04, '#4a4a47')                                   # plinth
for a, b in piers: box(a, b, 0.3, 6.7, 0.0, 0.06, TILE)                     # tiled piers, full height
box(0, L, 6.05, 6.64, 0.0, 0.05, TILE); box(0, L, 6.64, 6.75, 0.0, 0.25, '#3c3f3d')   # tiled band and the dark eaves
box(0, L, 2.93, 3.37, 0.0, 0.05, TILE)                                      # tiled band over the shops
for a, b in bays:                                                           # upper floor: brown spandrel, a three-light window per bay
    w = b - a
    box(a, b, 3.37, 4.12, 0.0, 0.02, BROWN)
    for f0, f1 in ((0.02, 0.225), (0.265, 0.735), (0.775, 0.98)): it.append(['winp', round(a + f0 * w, 2), round(a + f1 * w, 2), 4.18, 6.0, 1, FR, GL])
# north bay: rough render panel with one window over the gateway to the yard
box(0.42, 3.67, 3.37, 6.05, 0.0, 0.02, '#a5a18f')
it.append(['winp', 1.42, 2.68, 4.26, 5.6, 1, FR, GL])
it.append(['door', 0.42, 3.67, 0.0, 2.93, '#1b1c1d'])                       # the gateway (drawn dark) and its bar gate
k = 0.9
while k < 3.3: box(k, k + 0.05, 0.1, 2.3, 0.02, 0.05, '#8f918f'); k += 0.3
# shops
for a, b in bays: it.append(['glass', a, b, 0.3, 2.93, DG])
it.append(['door', 4.11, 5.1, 2.15, 2.88, '#2b2320'])                       # dark sign
box(5.1, 7.74, 2.15, 2.88, 0.0, 0.05, RED)                                  # red restaurant signs
box(9.05, 11.95, 2.15, 2.88, 0.0, 0.05, RED)
box(8.18, 9.05, 2.15, 2.88, 0.0, 0.03, '#9a9a96')
it.append(['door', 8.25, 8.95, 0.1, 2.15, '#2a1f24'])                       # restaurant door
box(7.2, 10.2, 3.0, 3.71, 0.06, 0.12, '#eeeeec')                            # white sign board on the brown band
box(8.0, 10.0, 3.15, 3.5, 0.12, 0.14, '#27348b')                            #   its blue lettering
it.append(['door', 12.45, 13.3, 0.1, 2.15, '#59646b'])                      # glazed doors of the two empty shops
it.append(['door', 16.68, 17.53, 0.1, 2.15, '#3a4247'])
for a, b in bays[2:]: box(a, b, 2.13, 2.19, 0.0, 0.04, '#3a3d3e')           # transom
e = {"id": 1725, "note": "Antinkatu 10, two-storey shop wing: beige small-tile piers and bands, four bays of three-light windows over brown spandrels, "
     "a rough-render bay with one window over the yard gateway at the north end, shops with red signs (SV Antinkatu 11 pano, rectified, 19.11.2026; "
     "eaves 6.7 m)", "walls": [{"a": [21.6, 174.1], "b": [17.1, 154.3], "bare": TILE, "kind": "plaster", "items": it}]}
p = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] != 1725] + [e]; open(p, 'w').write(json.dumps(F, indent=0)); print(len(it))
