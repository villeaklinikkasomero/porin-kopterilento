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

# 1490 Antinkatu 9 moved to f1492.py (remeasured 19.11.2026 together with the 1492 street strip)

p = '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] != 1315] + [e1315]; open(p, 'w').write(json.dumps(F, indent=0)); print(len(e1315['walls'][0]['items']))
