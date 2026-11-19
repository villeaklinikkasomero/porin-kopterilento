import json, sys
# 119 Itsenäisyydenkatu 41: two-storey roughcast shop building (street face 21.2 m, LoD2 wall line from raw.pkl). Measured 19.11.2026 on rectified
# Street View (Itsenäisyydenkatu 41 pano 61.4820169, 21.7946426 -> x -72.3 y -443.9, heading 14, pitch 10): scale 1.0, pavement at z 0.3 (z = z_measured - 0.3).
# Seen: s 1.5 .. 18. The eave is at 6.8 m; the scan's wall goes up to 8.5 m (roof slope), drawn as a dark sheet band so the windows keep their true size.
# Dark-framed windows: a three-light and four two-light windows upstairs, three shop windows and two doors at street level, a red sign over the west shop.
A = (-78.99, -431.183); B = (-58.387, -436.209); L = 21.2
WALL = '#cfcbc0'; FR = '#3a3d3f'; GL = '#56626a'
it = []
def box(s0, s1, z0, z1, d0, d1, c, k=None): it.append(['box', round(s0, 2), round(s1, 2), round(z0, 2), round(z1, 2), d0, d1, c] + ([k] if k else []))
box(0, L, 6.8, 8.5, 0.0, 0.06, '#4a4f54'); box(0, L, 6.7, 6.85, 0.0, 0.3, '#3f4347')   # roof slope band and the eave
for a, b, n in ((2.2, 4.4, 3), (6.6, 7.8, 2), (8.8, 10.0, 2), (11.0, 12.2, 2), (13.3, 14.5, 2), (16.7, 17.9, 2)): it.append(['winp', a, b, 4.75, 5.85, n, FR, GL])
for a, b in ((2.2, 4.4), (7.2, 9.4), (11.8, 14.0)): it.append(['winp', a, b, 1.2, 3.4, 1, FR, '#3f4a52']); box(a - 0.1, b + 0.1, 3.4, 3.52, 0.0, 0.12, FR)
box(1.6, 4.8, 3.65, 4.0, 0.0, 0.08, '#c7352e')                              # red shop sign (plain)
for a, b in ((5.4, 6.25), (15.1, 15.8)):
    it.append(['door', a, b, 0.5, 2.7, '#4a4640']); it.append(['glass', a, b, 2.75, 3.4, '#3f4a52']); box(a - 0.3, b + 0.3, 0.0, 0.5, 0.0, 0.6, '#8f8c85')   # door, fanlight, steps
e = {"id": 119, "note": "Itsenäisyydenkatu 41, two-storey roughcast shop building: dark-framed windows, three shop windows, two doors, red sign "
     "(SV Itsenäisyydenkatu 41 pano, rectified, 19.11.2026; eave 6.8 m under the scan's 8.5 m)",
     "walls": [{"a": list(A), "b": list(B), "bare": WALL, "kind": "plaster", "items": it}]}
p = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] != 119] + [e]; open(p, 'w').write(json.dumps(F, indent=0)); print(len(it))
