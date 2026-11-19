import json, sys
# 164 Itsenäisyydenkatu 45, parking house: the street (south) face 26.4 m, wall line from raw.pkl. Measured 19.11.2026 on rectified Street
# View (Itsenäisyydenkatu 45 pano 61.4822881, 21.792202 -> x -202.35 y -413.44, headings 345 and 45, pitch 8). The west corner and the
# scan's eave (4.0 m) gave scale 1.1 about the camera: rectified with the camera at (-202.60, -414.52) and ch 2.03, s and z read directly
# (z from the pavement). PV: the game's pavement lies 0.26 m above the block's ground, everything is drawn PV higher (as f166.py).
# Light grey concrete panels, a low wall 4.3 m high between two stair towers (west 7.2 m with a dark glazed strip, east 6.0 m with a glazed
# door and a dark window strip); a grey-blue door, a sectional door with two glazed rows, and the 4.9 m wide drive-in under yellow signs.
# Simplified: the drive-in is a dark panel (no opening is cut); the signs are blank yellow boards; lamps, the concrete fin and the
# ventilation drum on the deck are left out.
A = (-216.063, -398.788); B = (-190.378, -404.806); L = 26.38
CON = '#b9b7b0'; JNT = '#9c9a94'; DK = '#3c4650'; YEL = '#e2b53a'
it = []; PV = 0.26
def box(s0, s1, z0, z1, d0, d1, c, k=None): it.append(['box', round(s0, 2), round(s1, 2), round(z0 + PV, 2), round(z1 + PV, 2), d0, d1, c] + ([k] if k else []))
for z in (2.3, 3.07): box(4.1, 21.0, z - 0.015, z + 0.015, 0.0, 0.01, JNT)                 # horizontal panel joints
for s in (6.1, 7.2, 11.05, 12.9, 13.9, 16.0): box(s - 0.015, s + 0.015, 0.0, 4.27, 0.0, 0.01, JNT)   # vertical joints (seen)
box(4.1, 21.0, 4.17, 4.27, 0.0, 0.04, '#a9a7a0')                                           # coping of the low wall
# west stair tower
it.append(['glass', 0.02, 0.64, 3.18 + PV, 6.75 + PV, DK, 0.03]); box(0.0, 4.09, 7.06, 7.16, 0.0, 0.06, '#a9a7a0')
box(0.3, 1.0, 2.2, 2.75, 0.0, 0.03, YEL)                                                   # yellow board (blank)
it.append(['door', 4.23, 5.0, PV, 2.3 + PV, '#5f7080'])
# sectional door: solid below, two glazed rows above
it.append(['door', 7.27, 10.98, PV, 2.23 + PV, '#8d9094']); it.append(['winp', 7.27, 10.98, 1.2 + PV, 2.23 + PV, 5, '#8d9094', '#6b7780'])
box(7.27, 10.98, 1.68, 1.74, 0.04, 0.06, '#8d9094')
# drive-in and its signs
it.append(['door', 16.05, 20.95, PV, 2.3 + PV, '#191b1d'])
box(16.1, 18.0, 2.35, 2.7, 0.0, 0.04, YEL); box(18.4, 19.9, 2.35, 2.7, 0.0, 0.04, YEL)
# east stair tower
it.append(['winp', 21.45, 22.8, PV, 2.27 + PV, 2, '#4a5056', '#4f5d68']); it.append(['glass', 25.45, 26.3, 3.2 + PV, 5.7 + PV, DK, 0.03])
box(21.0, L, 5.85, 5.95, 0.0, 0.06, '#a9a7a0')
e = {"id": 164, "note": "Itsenäisyydenkatu 45, parking house: light grey concrete panels, low wall between two stair towers, grey-blue door, "
     "sectional door, drive-in (dark panel) under blank yellow signs (SV Itsenäisyydenkatu 45 pano, rectified, 19.11.2026; only the street face)",
     "walls": [{"a": list(A), "b": list(B), "bare": CON, "kind": "plaster", "items": it}]}
p = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] != 164] + [e]; open(p, 'w').write(json.dumps(F, indent=0)); print(len(it))
