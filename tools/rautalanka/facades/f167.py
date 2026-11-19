import json, sys
# 167 Itsenäisyydenkatu 58 (corner of Otavankatu), 8 storeys: the Itsenäisyydenkatu (south) end, 14.3 m, wall line from raw.pkl.
# Measured 19.11.2026 on rectified Street View (Itsenäisyydenkatu 58 pano 61.4824474, 21.7909043 -> x -271.53 y -395.87, heading 13,
# pitch 30): scale 1.0 (the face is seen from s 0.67 to 13.67, centred on the shell; the top band ends at 25.0 against the scan's eave 25.7),
# z = z_measured - 0.17 (pavement). PV: the game's pavement lies 0.26 m above the block's ground, everything is drawn PV higher (as f166.py).
# Grey-beige roughcast; two axes of wide dark-framed windows on seven storeys 2.78 m apart, a stack of glazed corner balconies at both ends,
# glazed shop floor between concrete piers under a grey canopy band, a red-brown board band under the wide dark eaves.
# Street level (owner 19.11.2026 "miksi ei voi leikata?"): both walls use "recess" - the shop floor stands back behind the piers (1.0 m on
# Itsenäisyydenkatu, 1.5 m on Eteläpuisto) with the generator's shop glazing, so the south-west corner under the balconies is an open notch
# behind a corner pier (in reality an open colonnade about 2.2 m deep on a round column). The corner balcony stacks are drawn 0.3 m proud.
# West (Eteläpuisto 20) face, 35.0 m: far pano 61.4827021, 21.7903007 -> x -303.63 y -367.47 (heading 103, pitch 22; s read directly,
# z ran 1.068 too tall there) and near pano 61.4827418, 21.7908179 -> x -276.07 y -363.05 (heading 103, pitch 30; storey heights, street
# level s 10..18). Seen s 4.5 .. 34; north of s 4.5 behind trees - left plain, not measured. The yard (east, north) sides: SPEC layout.
A = (-274.232, -385.193); B = (-260.311, -388.447); L = 14.3
WALL = '#b9b1a3'; FR = '#3a3d40'; GL = '#566470'; PIER = '#aaa69c'; CAN = '#8c8e90'; SHOP = '#39434a'; BAND = '#96583f'; BGL = '#b9c6cc'
it = []; PV = 0.26
def box(s0, s1, z0, z1, d0, d1, c, k=None): it.append(['box', round(s0, 2), round(s1, 2), round(z0 + PV, 2), round(z1 + PV, 2), d0, d1, c] + ([k] if k else []))
# street level
for a in (2.83, 6.83, 10.83): box(a, a + 0.67, -PV, 3.4, -1.0, 0.0, PIER)       # piers in front of the recessed shop floor
box(2.83, 13.67, 3.4, 3.62, 0.0, 0.6, CAN)                                   # canopy band
# seven storeys
lv = [round(4.0 + 2.78 * k + PV, 2) for k in range(7)]
for k in range(7):
    z = 4.83 + 2.78 * k + PV
    for a, b in ((3.5, 5.33), (9.0, 10.83)): it.append(['winp', a, b, round(z, 2), round(z + 1.5, 2), 2, FR, GL])
it.append(['balc', 0.67, 2.83, lv, round(23.6 + PV, 2), 0.3, 0.0, '#a7b0b2', BGL, 1.0, 2.6])
it.append(['balc', 11.5, 13.67, lv, round(23.6 + PV, 2), 0.3, 0.0, '#a7b0b2', BGL, 1.0, 2.6])
it.append(['box', 0.67, 13.67, 23.85 + PV, 25.0, 0.0, 0.04, BAND]); it.append(['box', 0.0, L, 25.0, 25.4, 0.0, 1.2, '#38383a'])   # board band, eaves
south = {"a": list(A), "b": list(B), "bare": WALL, "kind": "plaster", "recess": [3.4 + PV, 1.0, 25.7], "items": it}
# ---- west face (Eteläpuisto 20)
A2 = (-266.251, -351.094); B2 = (-274.232, -385.193); L2 = 35.02; SP = '#9a9993'; it = []
WALL2 = '#cdc7bb'                                                              # same render; lighter here because the west face bakes in shade
box(0.0, 12.5, -PV, 3.4, -1.5, 0.0, WALL2, 'plaster')                           # north part: no recess, the wall comes down to the plinth
box(0.0, 12.5, -PV, 0.75, 0.0, 0.05, '#8f8d88')                                # grey granite plinth
for a, b in ((5.0, 6.35), (10.0, 11.6)): it.append(['winp', a, b, 2.3 + PV, 3.8 + PV, 2, FR, GL])   # street-level windows
for a, b in ((15.0, 16.2), (20.85, 21.6), (23.9, 24.7), (27.1, 27.8), (30.4, 31.15)): box(a, b, -PV, 3.4, -1.5, 0.0, PIER)
box(12.5, 34.37, 3.4, 3.62, 0.0, 0.6, CAN)                                     # canopy band
axes = [(5.0, 6.35, 7), (8.1, 8.6, 7), (10.0, 11.6, 7), (13.4, 15.0, 7), (19.0, 20.5, 5), (22.1, 23.8, 7), (24.7, 26.4, 7), (28.4, 30.3, 7)]
for a, b, n in axes:
    for k in range(n):
        z = 4.83 + 2.78 * k + PV
        it.append(['winp', a, b, round(z, 2), round(z + 1.6, 2), 2 if b - a > 1 else 1, FR, GL])
        if b - a > 1: it.append(['box', a, b, round(z - 0.6, 2), round(z - 0.03, 2), 0.0, 0.02, SP])     # grey panel under the window
lv2 = [round(4.4 + 2.78 * k + PV, 2) for k in range(7)]
it.append(['balc', 15.5, 18.9, lv2, round(24.0 + PV, 2), 1.5, 0.0, '#5a5e61', BGL, 1.0, 2.6])             # projecting glazed balcony stack
it.append(['balc', 31.15, 34.37, lv, round(23.6 + PV, 2), 0.3, 0.0, '#a7b0b2', BGL, 1.0, 2.6])            # corner stack (as on the south end)
it.append(['box', 0.65, 13.0, 23.85 + PV, 25.0, 0.0, 0.04, BAND]); it.append(['box', 0.0, L2, 25.0, 25.4, 0.0, 1.2, '#38383a'])
west = {"a": list(A2), "b": list(B2), "bare": WALL2, "kind": "plaster", "recess": [3.4 + PV, 1.5, 25.7], "items": it}
e = {"id": 167, "nobrick": True, "note": "Itsenäisyydenkatu 58, south end: grey-beige roughcast, two axes of wide dark-framed windows on seven "
     "storeys, glazed corner balcony stacks, glazed shop floor between piers under a canopy band, red-brown board band under dark eaves "
     "(SV Itsenäisyydenkatu 58 pano, rectified, 19.11.2026). West face (Eteläpuisto 20): eight window axes with grey panels, a projecting "
     "glazed balcony stack, recessed shop floor behind piers from s 12.5, windows and plinth north of it (SV Eteläpuisto 19 and 20 panos; "
     "s < 4.5 not seen, left plain). Street level recessed on both faces; yard sides not measured", "walls": [south, west]}
p = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] != 167] + [e]; open(p, 'w').write(json.dumps(F, indent=0)); print(len(south['items']), len(west['items']))
