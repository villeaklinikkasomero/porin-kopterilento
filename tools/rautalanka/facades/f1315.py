import json
# ---------------- 1315 Antinkatu 11 (east edge -14.3,98.2 -> -9.4,119.7, 22.05 m)
L = 22.05; it = []
def box(s0, s1, z0, z1, d0, d1, c, k=None): it.append(['box', round(s0, 2), round(s1, 2), round(z0, 2), round(z1, 2), d0, d1, c] + ([k] if k else []))
COL = '#dcdcd6'; PAN = '#5a6683'; FR = '#e4e4df'; GL = '#6d7880'; DK = '#2f3436'
P0, PB = -0.85, 2.22                                                        # 10 bays of 2.22 m
cols = [P0 + PB * j for j in range(11)]
box(0, L, 0.0, 0.3, 0.0, 0.05, '#45484a')                                   # plinth
it.append(['glass', 0.0, L, 0.3, 3.4, '#33393a'])                           # shopfronts
box(0, L, 3.4, 5.05, 0.0, 0.03, '#cfcbbf')                                  # light transom band
for c in cols:
    if 0 <= c <= L: box(max(0, c - 0.18), min(L, c + 0.18), 0.3, 5.05, 0.0, 0.12, '#d6d3ca')   # piers under the raster columns
it.append(['door', 17.6, 19.0, 0.0, 2.6, '#1d2022'])                        # entrance
box(0, L, 5.05, 5.75, 0.0, 0.1, '#c8bd92')                                  # beige fascia band
box(3.6, 12.0, 5.2, 5.6, 0.1, 0.12, '#a8924f')                              # gilt lettering
box(3.9, 12.5, 3.0, 3.9, 0.0, 0.9, '#1f4a35')                               # Beer Hunter's green awning
box(4.2, 8.6, 3.25, 3.6, 0.9, 0.92, '#e8e4d6')                              #   its white lettering
for k in range(6):                                                          # six floors: blue-grey mosaic panel under a two-light window
    zp = 6.05 + 3.0 * k; zw = zp + 1.0
    for j in range(10):
        a, b = cols[j] + 0.18, cols[j + 1] - 0.18
        if b < 0 or a > L: continue
        a, b = max(a, 0.02), min(b, L - 0.02)
        if j == 8:                                                          # the column of recessed loggias
            it.append(['door', a, b, zp - 0.05, zp + 2.85, '#3a3c3a'])
            box(a, b, zp - 0.05, zp + 0.95, 0.0, 0.04, '#8c8f8e')           # concrete parapet
            continue
        box(a, b, zp, zp + 0.85, 0.0, 0.02, PAN)
        it.append(['winp', round(a, 2), round(b, 2), round(zw, 2), round(zw + 1.85, 2), 2, FR, GL])
    box(0, L, zp - 0.15, zp, 0.0, 0.1, COL)                                 # floor beam
for c in cols:
    if 0 <= c <= L: box(max(0, c - 0.18), min(L, c + 0.18), 5.75, 24.0, 0.0, 0.12, COL)   # raster columns
box(0, L, 23.95, 25.0, 0.0, 0.12, '#a9a9a4')                                # grey top band
e1315 = {"id": 1315, "note": "Antinkatu 11 (ent. PYP, 1956): white concrete raster of 10 bays x 2.22 m, six floors of two-light windows over blue-grey "
         "mosaic panels, a column of recessed loggias in the 9th bay, beige fascia band, Beer Hunter's green awning, shopfronts below "
         "(SV Antinkatu pano, rectified, 19.11.2026)",
         "walls": [{"a": [-14.3, 98.2], "b": [-9.4, 119.7], "bare": COL, "kind": "concrete", "items": it}]}

# ---------------- 1490 Antinkatu 9 (east edge -9.4,119.7 -> -4.7,140.2, 21.03 m)
L = 21.03; it = []
WALL = '#c2b9ae'
box(0, L, 0.0, 0.25, 0.0, 0.05, '#3e4143')
it.append(['glass', 0.2, L - 0.1, 0.25, 4.4, '#2c3134'])                    # restaurant glazing
k = 0.2
while k < L: box(k - 0.04, k + 0.04, 0.25, 4.4, 0.0, 0.08, '#2a2d2f'); k += 1.9
box(7.55, 8.0, 0.0, 4.6, 0.0, 0.25, '#4a4f52')                              # dark column
it.append(['door', 4.6, 6.2, 0.0, 2.5, '#1b1d1f'])
box(0.2, 16.0, 4.6, 5.05, 0.0, 0.7, '#8e2a2c')                              # Rosso's red awnings
for k in range(7):                                                          # seven floors
    zb = 6.85 + 3.05 * k
    for j in range(4): it.append(['winp', round(0.6 + 3.85 * j, 2), round(3.96 + 3.85 * j, 2), round(zb, 2), round(zb + 1.5, 2), 3, '#e6e6e1', '#6f7a80'])
    if k >= 3:
        it.append(['winp', 15.9, 17.8, round(zb, 2), round(zb + 1.5, 2), 2, '#e6e6e1', '#6f7a80'])
        it.append(['winp', 18.7, 20.6, round(zb, 2), round(zb + 1.5, 2), 2, '#e6e6e1', '#6f7a80'])
it.append(['winp', 19.0, 20.4, 13.05, 14.55, 2, '#e6e6e1', '#6f7a80'])
it.append(['door', 17.3, 18.5, 9.1, 11.4, '#3a3d3e'])                      # door onto the round balcony
box(16.4, 19.4, 9.0, 10.1, 0.0, 1.1, '#cbbf9e')                           # the round concrete balcony
for q in range(5): box(16.2 + 0.86 * q, 16.92 + 0.86 * q, 7.0, 8.1, 0.0, 0.06, '#b3262a')   # ROSSO letters
box(16.8, 19.6, 8.25, 8.55, 0.0, 0.05, '#6b6b6b')                             # 'Ristorante'
e1490 = {"id": 1490, "note": "Antinkatu 9: grey-beige render, seven floors of four three-light windows, at the north end paired windows, a round "
         "concrete balcony and the ROSSO letters, restaurant glazing under red awnings (SV Antinkatu panos, rectified, 19.11.2026)",
         "walls": [{"a": [-9.4, 119.7], "b": [-4.7, 140.2], "bare": WALL, "kind": "plaster", "items": it}]}

p = '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] not in (1315, 1490)] + [e1315, e1490]; open(p, 'w').write(json.dumps(F, indent=0)); print(len(e1315['walls'][0]['items']), len(e1490['walls'][0]['items']))
