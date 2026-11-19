import json, sys
# 585 former bus station (1955), the end towards Itsenäisyydenkatu (north face, 13.0 m, wall line from raw.pkl). Measured 19.11.2026 on
# rectified Street View (Itsenäisyydenkatu 44 pano 61.4815792, 21.7982185 -> x 118.21 y -492.56, heading 193, pitch 12; the east corner
# checked from heading 140): scale 1.0 by the eave (10.0 m at the west corner, as in the scan), s = s_measured - 0.7 (the west corner on
# the shell corner), z = z_measured - 0.1 (asphalt). PV: the game's pavement lies 0.26 m above the block's ground (as f166.py).
# Ochre-beige render under a mono-pitch roof (the eave falls about 0.9 m towards the east - the shell's own top), three large white-framed
# windows at street level, one long window behind white vertical louvres upstairs, a plinth of dark slate crazy-paving.
# Only this face is measured: the other sides keep the SPEC layout (shop fronts + window band).
A = (124.425, -502.046); B = (111.751, -499.126); L = 13.01
WALL = '#cdbd96'; WH = '#eeece4'; GL = '#566269'; SLATE = '#3c3d40'
it = []; PV = 0.26
def box(s0, s1, z0, z1, d0, d1, c, k=None): it.append(['box', round(s0, 2), round(s1, 2), round(z0 + PV, 2), round(z1 + PV, 2), d0, d1, c] + ([k] if k else []))
box(0, L, -PV, 0.9, 0.0, 0.05, SLATE)                                          # slate plinth
for a, b in ((0.9, 3.14), (3.66, 5.92), (6.44, 8.64)): it.append(['winp', a, b, 2.04 + PV, 3.9 + PV, 1, WH, GL])
it.append(['winp', 3.64, 8.66, 5.64 + PV, 7.5 + PV, 24, WH, '#4f5354'])        # long window behind vertical louvres
box(6.1, 6.2, 5.64, 7.5, 0.04, 0.07, WH)                                       # the louvre frame's middle post
e = {"id": 585, "note": "Former bus station (1955), Itsenäisyydenkatu end: ochre-beige render, three large white-framed windows, a louvred "
     "long window upstairs, dark slate plinth (SV Itsenäisyydenkatu 44 pano, rectified, 19.11.2026; other sides not measured)",
     "walls": [{"a": list(A), "b": list(B), "bare": WALL, "kind": "plaster", "items": it}]}
p = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] != 585] + [e]; open(p, 'w').write(json.dumps(F, indent=0)); print(len(it))
