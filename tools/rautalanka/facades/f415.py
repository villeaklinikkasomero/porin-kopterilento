import json, sys
# 415 Antinkatu 26 / Itsenäisyydenkatu 52 corner: white rendered flats, shops at street level + 3 storeys under a pitched roof (gable to Antinkatu).
# Measured 19.11.2026 on rectified Street View: Antinkatu 26 pano 61.4820247, 21.7935952 -> x -128.1 y -442.9 (heading 283, pitch 20) and
# Itsenäisyydenkatu 52 pano 61.482181, 21.7931281 -> x -153.0 y -425.6 (heading 193, pitch 18). Scale 1.0 (eave 13.3 m against the scan's 13.2 m);
# on Antinkatu s = s_measured + 0.1 from the LoD2 corner, on Itsenäisyydenkatu z = z_measured - 0.4 (pavement).
# Wall lines from raw.pkl (lod2.js rounds to 0.1 m: a line 4 cm behind the shell hid every item thinner than 5 cm).
# Not seen in the views and left plain: Antinkatu s < 1.9, Itsenäisyydenkatu s < 8.5 and s > 24.
WHT = '#ecebe6'; WH = '#f4f3ef'; FR = '#4a4f55'; GL = '#5b6a78'; GREY = '#8d8a86'; YEL = '#e0c45c'; BGL = '#b9c6cc'
def mk():
    it = []
    def box(s0, s1, z0, z1, d0, d1, c, k=None): it.append(['box', round(s0, 2), round(s1, 2), round(z0, 2), round(z1, 2), d0, d1, c] + ([k] if k else []))
    return it, box
rows = [4.4, 7.4, 10.4]
# ---- Antinkatu (east gable): two shop windows, window columns, the glazed corner balcony stack on round columns
it, box = mk()
box(0, 9.9, 0.0, 2.2, 0.0, 0.04, GREY); box(0, 9.9, 2.2, 2.3, 0.0, 0.06, WH)
it.append(['glass', 4.2, 5.85, 0.6, 3.4, '#3f4a52']); it.append(['glass', 7.3, 9.4, 0.7, 3.4, '#3f4a52'])
for a, b in ((4.2, 5.85), (7.3, 9.4)): box(a - 0.08, b + 0.08, 3.4, 3.5, 0.0, 0.05, WH)
for z in rows:
    for a, b in ((2.1, 3.2), (4.55, 5.9), (7.35, 7.7)): it.append(['winp', a, b, z, z + 1.65, 2 if b - a > 1 else 1, FR, GL])
lv = [4.2, 7.2, 10.2]
for z in lv: it.append(['winp', 10.1, 12.0, z + 0.1, z + 2.5, 2, FR, '#4f5f6c'])
it.append(['balc', 9.95, 12.2, lv, 13.2, 0.9, 0.0, '#e6e6e2', BGL, 1.0, 2.8])
box(11.75, 12.1, 0.0, 4.0, 0.5, 0.85, WH)                                   # round white column (square here)
it.append(['door', 10.2, 11.4, 0.1, 2.9, '#3f4a52'])                        # shop door under the balconies
east = {"a": [-141.659, -451.516], "b": [-138.857, -439.639], "bare": WHT, "kind": "plaster", "items": it}
# ---- Itsenäisyydenkatu (north): stair glazing over the entrance, three window columns, yellow panels, grey base
it, box = mk()
box(2.5, 26.1, 0.0, 1.9, 0.0, 0.04, GREY); box(2.5, 26.1, 1.9, 2.0, 0.0, 0.06, WH)
it.append(['glass', 8.6, 10.5, 9.0, 11.9, '#6f8196']); it.append(['glass', 9.7, 10.5, 3.6, 9.0, '#6f8196'])
for z in (6.2, 9.0): box(9.7 if z < 9 else 8.6, 10.5, z - 0.04, z + 0.04, 0.02, 0.05, FR)
it.append(['door', 10.6, 12.4, 0.1, 2.6, '#4b555c']); box(11.46, 11.54, 0.1, 2.6, 0.02, 0.05, '#d8d8d4')
box(9.5, 12.7, 2.9, 3.3, 0.0, 1.2, '#e4e4e0')                               # entrance canopy
for z in (5.35, 8.5, 11.5): it.append(['winp', 11.5, 12.7, z, z + 0.35, 1, FR, GL])   # slit windows of the stair
for k, z in enumerate(rows):
    z -= 0.1
    box(13.7, 15.2, z - 0.6, z, 0.0, 0.03, YEL)                             # yellow panel under the window
    box(20.0, 21.9, z + 1.7, z + 3.0 if k < 2 else z + 2.05, 0.0, 0.03, YEL)   # yellow strip between / above the windows
    for a, b in ((13.7, 15.2), (17.5, 18.6), (20.0, 21.9)): it.append(['winp', a, b, z, z + 1.7, 2, FR, GL])
it.append(['winp', 20.7, 21.2, 1.95, 2.75, 1, FR, GL])
box(16.3, 16.4, 0.0, 12.9, 0.05, 0.15, '#55585a')                           # downpipe
north = {"a": [-138.857, -439.639], "b": [-164.258, -433.642], "bare": WHT, "kind": "plaster", "items": it}
e = {"id": 415, "note": "Antinkatu 26 / Itsenäisyydenkatu 52: white render, shops + 3 storeys, gable to Antinkatu with a glazed corner balcony stack; "
     "Itsenäisyydenkatu: stair glazing over the entrance, yellow panels at two window columns, grey base (SV panos, rectified, 19.11.2026)", "walls": [east, north]}
p = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] != 415] + [e]; open(p, 'w').write(json.dumps(F, indent=0)); print(len(east['items']), len(north['items']))
