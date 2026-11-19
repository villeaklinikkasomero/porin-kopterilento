import json
L = 50.9; it = []
def box(s0, s1, z0, z1, d0, d1, c, k=None): it.append(['box', round(s0, 2), round(s1, 2), z0, z1, d0, d1, c] + ([k] if k else []))
WALL = '#b9b0a6'; FR = '#d5d6d1'; GL = '#6f7a80'; PAN = '#4f5655'
box(0, L, 0.0, 0.35, 0.0, 0.05, '#3c3f41')                                   # plinth
it.append(['glass', 0.3, L - 0.3, 0.35, 3.55, '#3f494a'])                    # shop glazing, teal-grey frames
k = 0.3
while k < L - 0.3: box(k - 0.05, k + 0.05, 0.35, 3.55, 0.0, 0.08, '#3d6a6e'); k += 1.8
it.append(['door', 20.2, 23.8, 0.0, 3.6, '#1c1f21'])                         # drive-through gate 'B' to the yard
box(0, L, 3.55, 5.9, 0.0, 0.05, '#51575c')                                   # dark stone band under the first floor windows
k = 0.5
while k < L: box(k - 0.02, k + 0.02, 3.55, 5.9, 0.05, 0.07, '#43484c'); k += 0.9
box(14.2, 18.8, 3.75, 4.35, 0.05, 0.12, '#e8eef4')                           # barber's sign
box(27.5, 33.0, 3.75, 4.3, 0.05, 0.12, '#2b2f33'); box(27.8, 32.7, 3.85, 4.2, 0.12, 0.13, '#e9e6dc')   # bakery sign
for zb in (5.95, 9.0, 12.07, 15.13, 18.2, 21.25):                            # six floors of window bands: 3.6 m bays of a two-light window, a narrow light and a dark panel
    h = 1.7 if zb < 6 else 1.6
    b = 0.5
    while b + 3.5 < L:
        it.append(['win', round(b, 2), round(b + 2.0, 2), zb, zb + h, FR, GL])
        it.append(['win', round(b + 2.05, 2), round(b + 2.75, 2), zb, zb + h, FR, GL])
        box(b + 2.78, b + 3.58, zb, zb + h, 0.0, 0.03, PAN)
        b += 3.6
    box(0, L, zb - 0.12, zb, 0.0, 0.05, '#c9c1b6')                             # sill ledge
box(0, L, 23.2, 23.6, 0.0, 0.15, '#a9a198')                                  # roof edge
e = {"id": 1497, "note": "Antinkatu 13, Liikekulma (1960): light grey terrazzo, six floors of window bands in 3.6 m bays (two-light window, narrow light, dark grey panel), "
     "a dark stone band under the first floor, shop glazing with teal frames all along the street, the drive-through gate B, barber's and bakery signs "
     "(SV Antinkatu 12 pano, rectified, 18.11.2026; footprint edge 50.9 m)",
     "walls": [{"a": [-30.4, 28.6], "b": [-18.5, 78.1], "bare": WALL, "kind": "concrete", "items": it}]}
p = '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] != 1497] + [e]; open(p, 'w').write(json.dumps(F, indent=0)); print(len(it))
