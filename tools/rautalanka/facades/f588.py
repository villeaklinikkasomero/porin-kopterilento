import json, sys
# 601 Itsenäisyydenkatu 35, Maakuntalinna (1959, white sheet-metal cladding): the street (south) face 34.6 m.
# The house has no shell of its own: it is the east stretch (s 47.2 .. 81.9) of the south wall of BePOP's LoD2 shell (588), so the entry
# is written under id 588 with "bare_s" (the hotel, 600, is the west stretch of the same wall: add its walls to this entry, not a new one).
# Below, s is measured from the house's own west corner (49.5, -461.3); S0 moves it onto the shell wall.
# Measured 19.11.2026 on rectified Street View (Itsenäisyydenkatu 35 pano 61.4816727, 21.7972856 -> x 68.50 y -482.2, heading 13,
# pitch 18). The east corner and the roof edge (22.2 m, zones.py _ML_TOP) gave scale 1.107 about the camera:
# s = 23.2 + (s_measured - 23.2) * 1.107, z = z_measured * 1.107 (from the pavement). PV as in f166.py.
# Five window bands 3.15 m apart (1.73 m high) between white sheet-metal bands: modules of 4.54 m = a grey louvre field 1.14 m + three
# windows; a tall shop floor under a white fascia: shop glazing, the entrance, two piers at the east shop. Seen: s 7.5 .. 34.6;
# the modules west of s 7.5 are REPEATED, not seen, and the street level there is left plain. Signs are blank boards.
A = (3.51, -450.606); B = (83.248, -469.351); S0 = 47.2; L = 34.59
WHT = '#e6e7e3'; ALU = '#c9cdcd'; GL = '#586672'; LOU = '#8f969b'; SHOP = '#3a444c'; PIER = '#dcdcd6'
it = []; PV = 0.26
def box(s0, s1, z0, z1, d0, d1, c, k=None): it.append(['box', round(s0, 2), round(s1, 2), round(z0 + PV, 2), round(z1 + PV, 2), d0, d1, c] + ([k] if k else []))
for z in (6.67, 9.83, 13.02, 16.12, 19.27):
    z1 = z + 1.73
    lou = [29.94 - 4.54 * k for k in range(7)]
    for l0 in lou:
        box(l0, l0 + 1.14, z, z1, 0.0, 0.03, LOU)
        it.append(['winp', round(l0 + 1.14, 2), round(min(l0 + 4.54, L - 0.2), 2), round(z + PV, 2), round(z1 + PV, 2), 3, ALU, GL])
    it.append(['winp', 0.2, round(lou[-1], 2), round(z + PV, 2), round(z1 + PV, 2), 2, ALU, GL])       # west end (repeated, not seen)
# shop floor
it.append(['glass', 8.0, 22.0, 0.4 + PV, 3.3 + PV, SHOP, 0.02]); it.append(['glass', 22.3, 25.2, 0.3 + PV, 4.3 + PV, SHOP, 0.02])
it.append(['door', 23.2, 24.4, 0.1 + PV, 2.4 + PV, '#2c3338'])
for a, b in ((26.4, 29.9), (31.0, 34.2)): it.append(['glass', a, b, 0.3 + PV, 3.6 + PV, SHOP, 0.02])
for a, b in ((25.3, 26.37), (29.94, 30.99)): box(a, b, -PV, 5.05, 0.0, 0.12, PIER)
box(26.4, 34.2, 4.0, 4.6, 0.0, 0.05, '#3b5fb8')                                # sign board of the east shop (blank)
box(0, L, -PV, 0.3, 0.0, 0.04, '#55585a')                                      # dark plinth
for q in it: q[1] = round(q[1] + S0, 2); q[2] = round(q[2] + S0, 2)
ml = {"a": list(A), "b": list(B), "bare": WHT, "kind": "plaster",   # "sheet" (metallic) baked grey on this sunlit face
       "bare_s": [S0, S0 + L + 0.3], "items": it}
# ---- 600 Itsenäisyydenkatu 37, Hotelli Bepop (1974): the west stretch s 0 .. 47.2 of the same shell wall. Measured 19.11.2026 on rectified
# Street View (Itsenäisyydenkatu 37 pano 61.4818218, 21.7963801 -> x 20.25 y -465.75, heading 13, pitch 18), scale 1.0 (roof edge 20.2 m).
# Owner 19.11.2026 "ihmeellistä hyppyä tasaisissa nauhoissa": the generated ribbon rows stepped from run to run; here the five window
# bands run level across the whole stretch (2.77 m apart, 1.4 m high, mullions 1.5 m apart, blue curtains on the two lower bands), light
# brown clinker between them, a dark red-brown fascia over the shop floor, shop glazing and the gate passage (dark panel).
# Seen: s 9.5 .. 28; the bands and the shop glazing are REPEATED over the rest of the stretch, not seen. The shell is taller (25.7 m) than
# the street face (20.2 m): the wall above the roof edge stays plain clinker.
KL = '#bfae86'; DB = '#3b332d'; it = []; LH = 47.0
for k in range(5):
    z = 5.9 + 2.77 * k
    it.append(['winp', 0.3, LH - 0.3, round(z + PV, 2), round(z + 1.4 + PV, 2), 31, DB, '#5f79a8' if k < 2 else '#4a5560'])
box(0.0, LH, 3.84, 4.76, 0.0, 0.08, '#6b3a30')                                 # fascia over the shop floor
it.append(['glass', 1.0, 17.0, 0.6 + PV, 3.7 + PV, SHOP, 0.02]); it.append(['glass', 19.9, 46.0, 0.6 + PV, 3.0 + PV, SHOP, 0.02])
box(19.9, 46.0, 3.0, 3.6, 0.0, 0.03, '#e9e8e2')                                # white sign strip over the shops (blank)
it.append(['door', 17.1, 19.6, PV, 3.6 + PV, '#1d1f21'])                       # gate passage to the yard (dark panel)
box(0, LH, -PV, 0.5, 0.0, 0.04, '#3a3b3d')
hot = {"a": list(A), "b": list(B), "bare": KL, "kind": "brick", "bare_s": [0.0, S0], "items": it}
e = {"id": 588, "nobrick": True, "note": "Itsenäisyydenkatu 37, Hotelli Bepop: clinker, five level window bands, fascia, shop glazing, gate (SV Itsenäisyydenkatu 37 pano; seen s 9.5..28, rest repeated). Itsenäisyydenkatu 35, Maakuntalinna: white sheet metal, five window bands (modules of a grey louvre field and three "
     "windows), tall shop floor with glazing, entrance and two piers (SV Itsenäisyydenkatu 35 pano, rectified, 19.11.2026; modules west of "
     "s 7.5 repeated, street level there plain; other sides not measured)",
     "walls": [ml, hot]}
p = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] not in (601, 588)] + [e]; open(p, 'w').write(json.dumps(F, indent=0)); print(len(ml['items']), len(hot['items']))
