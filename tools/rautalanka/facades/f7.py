import json, sys
# 7 Itsenäisyydenkatu 54 (1956), street (north) face 25.3 m, wall line from raw.pkl. Measured 19.11.2026 on rectified Street View
# (Itsenäisyydenkatu 54 pano 61.4822671, 21.792381 -> x -192.8 y -416.0, heading 193, pitch 14): scale 1.0, s = s_measured + 0.82 from the
# east corner, z = z_measured - 0.1. Seen: s 11 .. 25.3 (the stair bay and the five west axes); the four axes east of the stair bay are
# MIRRORED from the west ones, not seen. Yellow roughcast, three storeys 3.15 m apart, white-framed windows 2.3 m apart with a grey-green
# pebble panel under each, cellar windows, red-brown brick plinth; a white-framed stair bay with dark green balcony fronts over the entrance.
A = (-176.504, -431.306); B = (-201.162, -425.7); L = 25.29
YEL = '#e3cf7e'; WH = '#f1efe8'; GL = '#566a7c'; PEB = '#7f8a78'; BRK = '#8a4a38'; GRN = '#3d4f44'
it = []
def box(s0, s1, z0, z1, d0, d1, c, k=None): it.append(['box', round(s0, 2), round(s1, 2), round(z0, 2), round(z1, 2), d0, d1, c] + ([k] if k else []))
box(0, L, 0.0, 0.85, 0.0, 0.06, BRK, 'brick')
box(0, L, 11.85, 12.1, 0.0, 0.35, '#4a4d48')                                # eaves
west = [15.22, 17.52, 19.82, 22.12, 24.42]; east = [2 * 12.12 - c for c in west[:4]]
for c in west + east:
    for z in (3.1, 6.2, 9.35):
        box(c - 0.63, c + 0.63, z - 0.78, z - 0.03, 0.0, 0.025, PEB); it.append(['winp', round(c - 0.55, 2), round(c + 0.55, 2), z, z + 1.28, 1, WH, GL])
for c in west[:3] + east[:3]: it.append(['winp', round(c - 0.45, 2), round(c + 0.45, 2), 1.05, 1.45, 1, WH, '#4a5358'])   # cellar windows
box(23.6, 24.7, 1.0, 1.8, 0.0, 0.04, '#e9e7e2')                             # white hatch
# stair bay
box(11.05, 13.2, 2.6, 11.3, 0.0, 0.03, WH); it.append(['glass', 11.2, 13.05, 2.7, 11.2, '#5c6f84', 0.04])
for z in (2.9, 6.0, 8.5): box(11.1, 13.15, z, z + 1.5, 0.04, 0.3, GRN)       # balcony fronts
it.append(['door', 11.7, 12.6, 0.0, 2.3, '#4b555c']); box(11.05, 13.2, 2.35, 2.6, 0.0, 0.8, '#3d4f44')   # entrance and its canopy
box(L - 0.25, L - 0.13, 0.3, 11.85, 0.05, 0.15, '#5f7a6a')                  # downpipe
e = {"id": 7, "note": "Itsenäisyydenkatu 54 (1956): yellow roughcast, three storeys of white-framed windows with pebble panels, brick plinth, stair bay "
     "with green balcony fronts (SV Itsenäisyydenkatu 54 pano, rectified, 19.11.2026; the four east axes are mirrored, not seen)",
     "walls": [{"a": list(A), "b": list(B), "bare": YEL, "kind": "plaster", "items": it}]}
p = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] != 7] + [e]; open(p, 'w').write(json.dumps(F, indent=0)); print(len(it))
