import json
# Measured 19.11.2026 on rectified Street View (two Antinkatu 10 panos, x 6.5 y 136.0 and x 8.9 y 146.5; they agree to 0.4 m and put the
# dark blue column on the 1490/1492 footprint corner). s below = metres along the common street line from 1490's south corner.
def mk():
    it = []
    def box(s0, s1, z0, z1, d0, d1, c, k=None): it.append(['box', round(s0, 2), round(s1, 2), round(z0, 2), round(z1, 2), d0, d1, c] + ([k] if k else []))
    return it, box
FR = '#e6e6e1'; GL = '#6f7a80'; GLB = '#b9c6cc'; MU = '#dfe1e0'

# ---------------- 1490 Antinkatu 9 (east edge -9.4,119.7 -> -4.7,140.2, 21.03 m)
# The real front is 22.4 m (it starts 1.3 m south of the footprint corner): the four three-light window columns south of the joint at
# s 14.3 are compressed by 0.915 to fit, the north part (Rosso letters, round balcony, glazed strip, blue column) is at true size.
L = 21.03; it, box = mk(); WALL = '#c2b9ae'
box(0, L, 0.0, 0.25, 0.0, 0.05, '#3e4143')
it.append(['glass', 0.2, 17.7, 0.25, 4.4, '#2c3134'])                       # restaurant glazing
k = 0.2
while k < 17.7: box(k - 0.04, k + 0.04, 0.25, 4.4, 0.0, 0.08, '#2a2d2f'); k += 1.9
box(7.55, 8.0, 0.0, 4.6, 0.0, 0.25, '#4a4f52')                              # dark column
it.append(['door', 4.6, 6.2, 0.0, 2.5, '#1b1d1f'])
it.append(['door', 15.9, 17.5, 0.0, 2.6, '#1b1d1f'])                        # north entrance
box(0.2, 17.7, 4.6, 5.05, 0.0, 0.7, '#8e2a2c')                              # Rosso's red awnings
box(17.8, 18.5, 0.0, 5.0, 0.0, 0.06, WALL)                                  # render pier
for k in range(7):                                                          # seven floors
    zb = 6.85 + 3.05 * k
    for j in range(4): it.append(['winp', round(0.5 + 3.46 * j, 2), round(3.56 + 3.46 * j, 2), round(zb, 2), round(zb + 1.5, 2), 3, FR, GL])
    if k >= 2:                                                              # north part: two two-light windows from the third floor up
        it.append(['winp', 15.4, 17.5, round(zb, 2), round(zb + 1.5, 2), 2, FR, GL])
        it.append(['winp', 18.5, 20.5, round(zb, 2), round(zb + 1.5, 2), 2, FR, GL])
it.append(['winp', 15.6, 17.7, 9.9, 11.4, 2, FR, GL])                       # window / door behind the round balcony
it.append(['winp', 18.55, 19.6, 9.95, 11.4, 1, FR, GL])                     # single window beside it
box(14.7, 17.9, 9.55, 10.9, 0.0, 1.1, '#cbbf9e')                            # the round concrete balcony: parapet
box(15.2, 17.4, 9.1, 9.55, 0.0, 0.8, '#c2b592')                             #   the bowl narrows below
box(16.2, 16.36, 9.3, 11.5, 1.1, 1.22, '#c4b894')                           #   its fin
for q in range(5): box(14.5 + 0.82 * q, 15.2 + 0.82 * q, 6.35, 7.5, 0.0, 0.06, '#b3262a')   # ROSSO letters
box(15.0, 18.0, 7.7, 7.95, 0.0, 0.05, '#6b6b6b')                            # 'Ristorante'
box(15.0, 17.9, 6.0, 6.12, 0.0, 0.05, '#6b6b6b')
it.append(['glass', 18.55, 20.62, 4.5, 8.5, '#8fa1ab'])                     # glazed strip, two storeys over the shop floor
it.append(['glass', 18.55, 20.62, 0.3, 4.5, '#2c3134'])
box(19.56, 19.64, 0.3, 8.5, 0.0, 0.06, MU)
for z in (3.6, 4.5, 5.25, 6.75, 8.42): box(18.55, 20.62, z, z + 0.08, 0.0, 0.06, MU)
box(18.55, 20.62, 4.58, 5.25, 0.02, 0.04, '#56606a')                        #   opaque spandrel
box(20.62, L, 0.0, 8.6, 0.0, 0.15, '#2b3350')                               # dark blue column on the corner
e1490 = {"id": 1490, "note": "Antinkatu 9: grey-beige render, seven floors of four three-light windows; north of the joint the ROSSO letters, the round "
         "concrete balcony, two-light windows above, a two-storey glazed strip and the dark blue corner column; restaurant glazing under red awnings "
         "(SV Antinkatu 10 panos, rectified, 19.11.2026; the real front is 22.4 m on a 21.0 m footprint edge: south part compressed 0.915)",
         "walls": [{"a": [-9.4, 119.7], "b": [-4.7, 140.2], "bare": WALL, "kind": "plaster", "items": it}]}

# ---------------- 1492 street strip (east edge -4.7,140.2 -> -3.9,143.9, 3.79 m) and its north side over the gateway
L = 3.79; it, box = mk()
it.append(['glass', 0.0, L, 0.2, 4.4, '#1e2124'])                           # dark glazed entrance under the bay (set back in reality)
for s in (0.0, 1.25, 2.5, 3.71): box(s, s + 0.08, 0.2, 4.4, 0.0, 0.06, '#2f3336')
it.append(['door', 1.33, 2.5, 0.2, 2.5, '#111314'])
box(0, L, 4.4, 4.58, 0.0, 1.08, '#dcdcd8')                                  # slab under the glazed bay
box(0, L, 4.58, 8.42, 0.0, 1.0, GLB)                                        # the glazed bay, two storeys, 1 m out over the entrance
box(0, L, 4.58, 5.25, 1.0, 1.02, '#56606a')                                 #   opaque spandrel row
for j in range(5): box(max(0, j * L / 4 - 0.04), min(L, j * L / 4 + 0.04), 4.58, 8.42, 1.0, 1.05, MU)   # four panes wide
for z in (5.25, 6.75): box(0, L, z - 0.04, z + 0.04, 1.0, 1.05, MU)
box(0, L, 8.42, 8.6, 0.0, 1.08, '#dcdcd8')                                  # slab over it
DK = '#33353c'
box(0.5, 3.6, 8.95, 9.25, 0.0, 0.05, DK)                                    # 'gastropub - bar'
for a, b in ((0.45, 0.75), (0.9, 1.2), (1.35, 1.65), (1.8, 2.1)): box(a, b, 9.9, 11.3, 0.0, 0.06, DK)   # cafe sign: dark letter strokes
box(2.3, 3.4, 10.0, 11.1, 0.0, 0.07, '#e9c79a')                             #   and its cream disc (drawn square)
box(3.45, 3.6, 9.9, 11.3, 0.0, 0.06, DK)
box(0.5, 3.6, 12.6, 13.25, 0.0, 0.05, '#79bd52')                            # green lettering
box(0.5, 3.6, 15.8, 16.6, 0.0, 0.05, '#6f78b8')                             # blue-violet lettering
box(0.6, 3.6, 19.2, 19.95, 0.0, 0.05, '#63bf45')                            # green lettering
box(0.9, 3.3, 20.1, 20.35, 0.0, 0.04, '#8a8d90'); box(0.9, 3.3, 18.65, 18.9, 0.0, 0.04, '#8a8d90')
box(0.6, 3.6, 21.7, 22.6, 0.0, 0.05, '#3c4672')                             # dark blue lettering at the top
east = {"a": [-4.7, 140.2], "b": [-3.9, 143.9], "bare": '#c2b9ae', "kind": "plaster", "items": it}
Ln = 5.53; it, box = mk()                                                   # north side wall, s from the street corner
box(0, 3.0, 4.58, 8.42, 0.0, 0.05, GLB)                                     # the bay glazing turns the corner
for s in (0.0, 1.0, 2.0, 2.96): box(s, s + 0.08, 4.58, 8.42, 0.05, 0.09, MU)
for z in (5.25, 6.75): box(0, 3.0, z - 0.04, z + 0.04, 0.05, 0.09, MU)
box(0, 3.0, 4.58, 5.25, 0.05, 0.07, '#56606a')
box(0.0, 2.6, 8.6, 23.3, 0.0, 0.8, GLB)                                     # stack of glazed balconies on the street end of the side wall
z = 8.6
while z < 23.4: box(0.0, 2.6, z, z + 0.14, 0.0, 0.85, '#d9dad6'); box(0.0, 2.6, z + 0.14, z + 1.0, 0.8, 0.82, '#7d8990'); z += 2.94
north = {"a": [-3.9, 143.9], "b": [-9.3, 145.1], "bare": '#c2b9ae', "kind": "plaster", "items": it}
e1492 = {"id": 1492, "note": "Antinkatu 9, the 3.8 m strip that reaches the street north of 1490 (Cafe Anton / office signs): dark glazed entrance, "
         "a two-storey glazed bay 1 m out, grey render above with the stacked signs (drawn as plain coloured bars), on the north side over the "
         "gateway a stack of glazed balconies (SV Antinkatu 10 panos, rectified, 19.11.2026)", "walls": [east, north]}

import sys
p = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] not in (1490, 1492)] + [e1490, e1492]; open(p, 'w').write(json.dumps(F, indent=0)); print(len(e1490['walls'][0]['items']), len(east['items']), len(north['items']))
