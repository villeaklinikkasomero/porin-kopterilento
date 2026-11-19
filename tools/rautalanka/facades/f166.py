import json, sys
# 166 Itsenäisyydenkatu 47, street (south) face 22.7 m, wall line from raw.pkl (the LoD2 shell follows the eaves: the wall corners are
# seen at s 0.25 and s 21.9). Measured 19.11.2026 on rectified Street View (Itsenäisyydenkatu 47 pano 61.4823566, 21.7916471 ->
# x -231.92 y -406.1, headings 12 and 330, pitch 14). The shell corners and the eaves height gave scale 1.124 about the camera:
# rectified with the camera moved to (-232.59, -407.23) and ch 2.16, after which s and z are read directly (z from the pavement).
# PV: the game's pavement lies 0.26 m above the block's ground (ROAD.pave, streets as geometry 18.11.2026), so everything except the
# eaves is drawn PV higher - otherwise the plinth, the steps and the cellar windows are under the pavement.
# Seen: the whole face except the cellar window under the west axis (behind a traffic sign) - left out.
# Pale ochre render, three storeys; four axes of white six-pane windows (s 2.94, 7.77, 14.89, 19.88) and the entrance on the centre line:
# a panelled dark door in a red granite surround with a flat hood and steps; red granite plinth with cellar windows; plain cornice band.
A = (-244.925, -392.848); B = (-222.745, -397.730); L = 22.71
WALL = '#dccb92'; WH = '#f2f0e8'; GL = '#4f5d68'; GRA = '#8d5f52'; SUR = '#b58a7a'; COR = '#cdbb84'
it = []; PV = 0.26
def box(s0, s1, z0, z1, d0, d1, c, k=None): it.append(['box', round(s0, 2), round(s1, 2), round(z0, 2), round(z1, 2), d0, d1, c] + ([k] if k else []))
box(0, L, -PV, 0.66, 0.0, 0.06, GRA)                                        # granite plinth
box(0, L, 11.0, 11.55, 0.0, 0.1, COR); box(0, L, 11.55, 11.9, 0.0, 0.4, '#b9a877')   # cornice band and the eaves soffit
axes = [2.94, 7.77, 14.89, 19.88]
for c in axes:
    for z0, z1 in ((1.91, 3.55), (5.19, 6.83), (8.47, 10.0)):
        it.append(['winp', round(c - 0.75, 2), round(c + 0.75, 2), z0, z1, 3, WH, GL])
        zt = z0 + (z1 - z0) * 0.67; box(c - 0.75, c + 0.75, zt - 0.03, zt + 0.03, 0.04, 0.06, WH)     # transom: six panes
        box(c - 0.85, c + 0.85, z0 - 0.1, z0 - 0.03, 0.0, 0.1, '#b9ae8c')                           # sill
for c in axes[1:]: it.append(['winp', round(c - 0.6, 2), round(c + 0.6, 2), 0.11, 0.38, 1, '#5b4a44', '#2e3236'])   # cellar windows (seen)
# entrance on the centre line
box(10.06, 11.03, 0.35, 4.06, 0.0, 0.12, SUR); box(11.97, 12.38, 0.35, 4.06, 0.0, 0.12, SUR); box(11.03, 11.97, 3.25, 4.06, 0.0, 0.12, SUR)
box(9.97, 12.47, 4.06, 4.28, 0.0, 0.3, '#a9806f')                           # flat hood
it.append(['door', 11.03, 11.97, 0.35, 3.25, '#33261f']); it.append(['winp', 11.2, 11.8, 2.55, 3.1, 2, '#4a372c', '#4f5d68'])   # door and its upper lights
for j in range(2): box(10.0 - j * 0.1, 12.45 + j * 0.1, 0.18 - j * 0.18, 0.36 - j * 0.18, 0.0, 0.45 + j * 0.3, '#9a7468')   # two granite steps
box(12.75, 13.3, 2.05, 2.25, 0.0, 0.02, '#b59a55')                          # brass plate (blank)
for s in (10.1, 10.7): box(s, s + 0.14, 7.12, 7.26, 0.0, 0.02, '#6b6250')     # two small vents
for s in (0.3, 21.75): box(s, s + 0.12, 0.3, 11.55, 0.05, 0.17, '#b7b2a2')   # downpipes at the corners
for q in it:                                                                 # lift to the pavement (not the cornice / eaves)
    if not (q[0] == 'box' and q[3] >= 11.0): q[3] = round(q[3] + PV, 2); q[4] = round(q[4] + PV, 2)
e = {"id": 166, "nobrick": True, "note": "Itsenäisyydenkatu 47: pale ochre render, three storeys, four axes of white six-pane windows, central door in a red granite "
     "surround with hood and steps, red granite plinth with cellar windows (SV Itsenäisyydenkatu 47 pano, rectified, 19.11.2026; "
     "the cellar window of the west axis not seen, left out)",
     "walls": [{"a": list(A), "b": list(B), "bare": WALL, "kind": "plaster", "items": it}]}
p = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] != 166] + [e]; open(p, 'w').write(json.dumps(F, indent=0)); print(len(it))
