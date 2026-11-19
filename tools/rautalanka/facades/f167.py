import json, sys
# 167 Itsenäisyydenkatu 58 (corner of Otavankatu), 8 storeys: the Itsenäisyydenkatu (south) end, 14.3 m, wall line from raw.pkl.
# Measured 19.11.2026 on rectified Street View (Itsenäisyydenkatu 58 pano 61.4824474, 21.7909043 -> x -271.53 y -395.87, heading 13,
# pitch 30): scale 1.0 (the face is seen from s 0.67 to 13.67, centred on the shell; the top band ends at 25.0 against the scan's eave 25.7),
# z = z_measured - 0.17 (pavement). PV: the game's pavement lies 0.26 m above the block's ground, everything is drawn PV higher (as f166.py).
# Grey-beige roughcast; two axes of wide dark-framed windows on seven storeys 2.78 m apart, a stack of glazed corner balconies at both ends,
# glazed shop floor between concrete piers under a grey canopy band, a red-brown board band under the wide dark eaves.
# Simplified: the street level under the west balcony stack is an open colonnade in reality - left as plain wall (no opening can be cut);
# the balcony stacks are drawn 0.3 m proud. The long Otavankatu and yard sides are not measured (SPEC layout).
A = (-274.232, -385.193); B = (-260.311, -388.447); L = 14.3
WALL = '#b9b1a3'; FR = '#3a3d40'; GL = '#566470'; PIER = '#aaa69c'; CAN = '#8c8e90'; SHOP = '#39434a'; BAND = '#96583f'; BGL = '#b9c6cc'
it = []; PV = 0.26
def box(s0, s1, z0, z1, d0, d1, c, k=None): it.append(['box', round(s0, 2), round(s1, 2), round(z0 + PV, 2), round(z1 + PV, 2), d0, d1, c] + ([k] if k else []))
# street level
for a, b in ((3.5, 6.83), (7.5, 10.83), (11.5, 13.4)): it.append(['glass', a, b, 0.15 + PV, 3.3 + PV, SHOP, 0.02])
for a in (2.83, 6.83, 10.83): box(a, a + 0.67, -PV, 3.4, 0.0, 0.15, PIER)
it.append(['door', 5.6, 6.5, 0.1 + PV, 2.45 + PV, '#2b3237'])
box(2.83, 13.67, 3.4, 3.62, 0.0, 0.6, CAN)                                   # canopy band
# seven storeys
lv = [round(4.0 + 2.78 * k + PV, 2) for k in range(7)]
for k in range(7):
    z = 4.83 + 2.78 * k + PV
    for a, b in ((3.5, 5.33), (9.0, 10.83)): it.append(['winp', a, b, round(z, 2), round(z + 1.5, 2), 2, FR, GL])
it.append(['balc', 0.67, 2.83, lv, round(23.6 + PV, 2), 0.3, 0.0, '#a7b0b2', BGL, 1.0, 2.6])
it.append(['balc', 11.5, 13.67, lv, round(23.6 + PV, 2), 0.3, 0.0, '#a7b0b2', BGL, 1.0, 2.6])
it.append(['box', 0.67, 13.67, 23.85 + PV, 25.0, 0.0, 0.04, BAND]); it.append(['box', 0.0, L, 25.0, 25.4, 0.0, 1.2, '#38383a'])   # board band, eaves
e = {"id": 167, "nobrick": True, "note": "Itsenäisyydenkatu 58, south end: grey-beige roughcast, two axes of wide dark-framed windows on seven "
     "storeys, glazed corner balcony stacks, glazed shop floor between piers under a canopy band, red-brown board band under dark eaves "
     "(SV Itsenäisyydenkatu 58 pano, rectified, 19.11.2026; open colonnade under the west balconies drawn as plain wall; other sides not measured)",
     "walls": [{"a": list(A), "b": list(B), "bare": WALL, "kind": "plaster", "items": it}]}
p = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] != 167] + [e]; open(p, 'w').write(json.dumps(F, indent=0)); print(len(it))
