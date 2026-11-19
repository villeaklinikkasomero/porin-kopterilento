import json, sys
# 585 former bus station (1955), the end towards Itsenäisyydenkatu (north face, 13.0 m, wall line from raw.pkl). Measured 19.11.2026 on
# rectified Street View (Itsenäisyydenkatu 44 pano 61.4815792, 21.7982185 -> x 118.21 y -492.56, heading 193, pitch 12; the east corner
# checked from heading 140): scale 1.0 by the eave (10.0 m at the west corner, as in the scan), s = s_measured - 0.7 (the west corner on
# the shell corner), z = z_measured - 0.1 (asphalt). PV: the game's pavement lies 0.26 m above the block's ground (as f166.py).
# Ochre-beige render under a mono-pitch roof (the eave falls about 0.9 m towards the east - the shell's own top), three large white-framed
# windows at street level, one long window behind white vertical louvres upstairs, a plinth of dark slate crazy-paving.
# The north-east and southern sides are not measured: they keep the SPEC layout (shop fronts + window band).
A = (124.425, -502.046); B = (111.751, -499.126); L = 13.01
WALL = '#cdbd96'; WH = '#eeece4'; GL = '#566269'; SLATE = '#3c3d40'
it = []; PV = 0.26
def box(s0, s1, z0, z1, d0, d1, c, k=None): it.append(['box', round(s0, 2), round(s1, 2), round(z0 + PV, 2), round(z1 + PV, 2), d0, d1, c] + ([k] if k else []))
box(0, L, -PV, 0.9, 0.0, 0.05, SLATE)                                          # slate plinth
for a, b in ((0.9, 3.14), (3.66, 5.92), (6.44, 8.64)): it.append(['winp', a, b, 2.04 + PV, 3.9 + PV, 1, WH, GL])
it.append(['winp', 3.64, 8.66, 5.64 + PV, 7.5 + PV, 24, WH, '#4f5354'])        # long window behind vertical louvres
box(6.1, 6.2, 5.64, 7.5, 0.04, 0.07, WH)                                       # the louvre frame's middle post
# --- west face towards Kuninkaantie (shell wall 18.06 m), measured 19.11.2026 on rectified Street View, pano Kuninkaantie (Sept 2017,
# 61.4814435, 21.7978931, headings 55 / 103 / 150, pitch 12). The pano's GPS spot gave an eave of 8.5 m; the eave is 10.0 m (scan, and the
# north face meets it at the corner), so the camera was moved to x 98.59 y -506.84 (11.2 m from the wall, bearing 137.5 to the south
# corner). Seen clearly: s 8 .. 18; s 2 .. 8 through a tree (window columns visible, details not); the three northernmost upper windows
# are repeated. Two storeys: red-brick plinth, ten bays (pitch 1.58 m) of white-framed windows, a glazed door in bay 3 from the south,
# a brick sill band and a black awning (lettering not copied) over the terrace; the raised timber terrace deck in front of the wall.
A2 = (111.798, -499.282); B2 = (107.797, -516.889); L2 = 18.06
BR = '#8a4c3c'; AWN = '#26272b'; DECK = '#5a4a3c'
iw = []
def box2(s0, s1, z0, z1, d0, d1, c, k=None): iw.append(['box', round(s0, 2), round(s1, 2), round(z0 + PV, 2), round(z1 + PV, 2), d0, d1, c] + ([k] if k else []))
box2(0, L2, -PV, 1.75, 0.0, 0.025, BR, 'brick')                               # brick plinth up to the sills
box2(1.9, L2, 5.05, 5.38, 0.0, 0.025, BR, 'brick')                            # brick sill band under the upper windows
box2(0, L2, 9.82, 10.0 - PV, 0.0, 0.12, '#2e2f31')                            # dark eave fascia
for k in range(10):
    c = 17.24 - 1.58 * k
    iw.append(['winp', round(c - 0.55, 2), round(c + 0.55, 2), 5.4 + PV, 7.3 + PV, 1, WH, GL])          # upstairs (k 7..9 repeated, unseen)
    if k == 2: iw.append(['winp', round(c - 0.58, 2), round(c + 0.58, 2), 0.9 + PV, 3.55 + PV, 1, WH, '#4a5458'])   # glazed door on the terrace
    else: iw.append(['winp', round(c - 0.55, 2), round(c + 0.55, 2), 1.8 + PV, 3.55 + PV, 1, WH, GL])
box2(8.8, 18.0, 4.3, 4.85, 0.0, 0.9, AWN)                                     # awning over the terrace
box2(2.5, 18.0, -PV, 0.85, 0.0, 3.0, DECK, 'wood')                            # raised timber terrace
e = {"id": 585, "note": "Former bus station (1955): north end to Itsenäisyydenkatu (ochre-beige render, three large white-framed windows, a louvred "
     "long window upstairs, dark slate plinth; SV Itsenäisyydenkatu 44) and west face to Kuninkaantie (brick plinth and sill band, ten bays of "
     "white-framed windows, terrace door, awning, timber terrace; SV Kuninkaantie 2017, north three upper windows repeated). Rectified 19.11.2026; "
     "the north-east and southern sides are not measured",
     "walls": [{"a": list(A), "b": list(B), "bare": WALL, "kind": "plaster", "items": it},
               {"a": list(A2), "b": list(B2), "bare": WALL, "kind": "plaster", "items": iw}]}
p = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] != 585] + [e]; open(p, 'w').write(json.dumps(F, indent=0)); print(len(it), len(iw))
