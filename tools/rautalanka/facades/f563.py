import json
def S(s): return round((s + 1.6) * 27.6 / 26.9, 2)       # pano s -> footprint edge s (front reads 26.9 m, the footprint edge 27.6 m up to 564)
it = []
def box(s0, s1, z0, z1, d0, d1, c, k=None): it.append(['box', S(s0), S(s1), z0, z1, d0, d1, c] + ([k] if k else []))
WALL = '#a9a6a0'; FR = '#2f3132'; GL = '#7f8a8e'
box(-1.6, 25.3, 0.0, 0.45, 0.0, 0.05, '#5c5a57')                         # plinth
it.append(['glass', S(-1.3), S(25.0), 0.45, 3.5, '#3d4446'])            # shop glazing
k = -1.3
while k < 25.0: box(k - 0.05, k + 0.05, 0.45, 3.5, 0.0, 0.08, '#55595a'); k += 1.48
for b in range(7): box(-1.3 + 4.43 * b - 0.35, -1.3 + 4.43 * b + 0.05, 0.0, 3.55, 0.0, 0.1, WALL)   # concrete piers at the bays
it.append(['door', S(22.9), S(24.9), 0.45, 3.0, '#1f2324'])              # recessed shop door, south end
box(-1.6, 25.3, 3.5, 3.62, 0.0, 0.12, '#8a8781')                         # canopy edge over the shops
for b in range(6):                                                       # upper floor: three-pane windows, one group per 4.43 m bay
    s0 = -1.3 + 4.43 * b; it.append(['winp', S(s0), S(s0 + 3.8), 5.4, 7.4, 3, FR, GL])
for b in range(7):                                                       # panel joints
    j = -1.3 + 4.43 * b - 0.32; box(j - 0.03, j + 0.03, 3.62, 8.7, 0.0, 0.02, '#8b8883')
for z in (4.45, 8.0): box(-1.6, 25.3, z, z + 0.05, 0.0, 0.02, '#8b8883')
box(-1.6, 25.3, 8.6, 8.9, 0.0, 0.12, '#9b988f')                          # coping
north = [['door', 1.3, 3.2, 0.0, 2.3, '#3a3d3e'], ['box', 0.0, 14.0, 0.0, 0.45, 0.0, 0.05, '#5c5a57'], ['box', 0.0, 14.0, 8.6, 8.9, 0.0, 0.12, '#9b988f'],
         ['box', 0.0, 14.0, 4.45, 4.5, 0.0, 0.02, '#8b8883'], ['box', 9.6, 9.7, 0.0, 8.6, 0.05, 0.15, '#6f6f6d']]
e = {"id": 563, "note": "Antinkatu 12 (beside 564): two-storey 1960s concrete shop building, not the yellow 'Cafe Anton' of the old note: grey panel walls, a dark glazed shop floor "
     "under a thin canopy edge, six three-pane window groups on the upper floor (4.43 m bays), panel joints, blank north end with a door (SV Antinkatu 12 and 15 panos, "
     "rectified, 18.11.2026; the front reads 26.9 m, fitted to the footprint edge, 27.6 m up to 564)",
     "walls": [{"a": [-18.8, 0.0], "b": [-25.0, -26.9], "bare": WALL, "kind": "concrete", "items": it},
               {"a": [-5.2, -3.1], "b": [-18.8, 0.0], "bare": WALL, "kind": "concrete", "items": north}]}
p = '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] != 563] + [e]; open(p, 'w').write(json.dumps(F, indent=0)); print(len(it))
