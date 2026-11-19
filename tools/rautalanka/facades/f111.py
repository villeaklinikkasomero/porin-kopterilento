import json, sys
# Shell 111 (c064), the wall along Rautatienpuistokatu 43.2 m: TWO houses on one shell wall.
#   s 0 .. 31.1    111, the cream two-storey classicist house (1920s): corner strips, two arched doorways with a stair window and a lunette
#                  above each, wide three-part windows at both ends, four axes of two-part windows between the doors, grey roughcast plinth
#                  with cellar windows, white moulded cornice.
#   s 31.1 .. 43.2 109, Rautatienpuistokatu 3 / Yrjönkatu 27 (white functionalist, lod2 "hide": it has no shell of its own): two shop
#                  windows with a canopied door between them, three dark-framed windows and three attic slits above, and the corner tower
#                  (s 40.4 .. 43.2) with a projecting glazed bay over a wooden door.
# Measured 19.11.2026 on rectified Street View, April 2026 (leafless): pano "2 Rautatienpuistokatu" 61.4810783, 21.7952537, headings
# 262 / 313 / 357, pitch 15, and pano "1 Rautatienpuistokatu" 61.4812327, 21.7954845, headings 265 / 320, pitch 15 / 18.
# Calibrated on the shell: the south corner (s 0), the joint of the houses (s 31.1), the tower (40.4 .. 43.2) and the eaves (10.0 / 10.4)
# -> cameras at s 19.16, 10.96 m from the wall (k 1.09) and s 38.93, 8.42 m (k 1.13); heights z = 1.098 z_m - 0.71 (pano 2) and
# z = 1.135 z_m - 1.04 (pano 1), i.e. from the pavement at the wall. PV as in f166.py.
# Not seen / simplified: the lower window of the axis at s 20.4 .. 21.6 is behind a tree trunk (repeated); lunettes and fanlights are
# drawn square (no arches); roof dormers left out; the bay's projection (0.5 m) is estimated. Shop lettering and signs are not copied.
# The south-west end (12 m) and the Yrjönkatu side (17.5 m) of the shell are not measured.
A = (-60.156, -555.791); B = (-30.901, -523.977); L = 43.2; J = 31.1; PV = 0.26
CR = '#e9dcbe'; WH = '#f4f1ea'; PL = '#c9c5ba'; GL = '#56636b'; W2 = '#f1efe9'; DK = '#5c554a'; GR = '#cdb8ab'; DOOR = '#5b5f5c'
it = []
def box(s0, s1, z0, z1, d0, d1, c, k=None): it.append(['box', round(s0, 2), round(s1, 2), round(z0 + PV, 2), round(z1 + PV, 2), d0, d1, c] + ([k] if k else []))
def win(s0, s1, z0, z1, n, fr=WH, gl=GL): it.append(['winp', round(s0, 2), round(s1, 2), round(z0 + PV, 2), round(z1 + PV, 2), n, fr, gl])
# ---- 111, cream house
box(0, J, -PV, 1.43, 0.0, 0.025, PL)                                           # roughcast plinth
box(0, J, 9.45, 9.9, 0.0, 0.3, WH)                                             # moulded cornice
for a, b in ((0.25, 0.75), (6.1, 6.75)): box(a, b, 1.43, 9.45, 0.0, 0.06, WH)   # corner strips of the south bay
for a in (2.5, 4.05, 11.5, 14.6, 17.7, 27.4, 28.7): win(a, a + 0.5, 0.66, 1.2, 1, PL, '#3f4548')    # cellar windows
for a, b in ((2.58, 4.5), (27.4, 29.3)): win(a, b, 6.5, 8.45, 3); win(a, b, 2.7, 4.65, 3)
for a in (11.13, 14.2, 17.33, 20.45): win(a, a + 1.15, 6.5, 8.45, 2); win(a, a + 1.15, 2.7, 4.65, 2)
for c in (8.75, 24.1):                                                         # arched doorways (drawn square)
    box(c - 0.95, c - 0.5, -PV, 3.1, 0.0, 0.08, WH); box(c + 0.5, c + 0.95, -PV, 3.1, 0.0, 0.08, WH); box(c - 0.95, c + 0.95, 3.55, 3.8, 0.0, 0.1, WH)
    it.append(['door', round(c - 0.45, 2), round(c + 0.45, 2), 0.25 + PV, 2.77 + PV, DOOR]); win(c - 0.45, c + 0.45, 2.77, 3.52, 3)
    win(c - 0.55, c + 0.55, 5.09, 6.3, 2); win(c - 0.5, c + 0.5, 7.74, 8.48, 3)
# ---- 109, white house
box(J, 40.4, -PV, 10.0, 0.0, 0.02, W2); box(40.4, L, -PV, 3.85, 0.0, 0.02, W2)  # white render over the shell's single bare colour
box(J, L, -PV, 0.85, 0.02, 0.03, GR)                                           # pink granite plinth
box(J, 40.4, 10.0, 10.14, 0.0, 0.35, W2)                                       # eave slab
for a, b in ((32.05, 33.17), (34.45, 35.55), (36.8, 37.9)): win(a, b, 5.83, 7.76, 2, DK); win(a, b, 9.08, 9.6, 1, DK)
win(32.05, 35.5, 0.95, 3.9, 2, DK, '#3f4a50'); win(36.5, 40.0, 0.86, 3.87, 3, DK, '#3f4a50')      # shop windows
it.append(['door', 35.6, 36.4, 0.3 + PV, 2.5 + PV, '#3a3f42']); box(35.4, 36.6, 2.6, 2.95, 0.0, 0.9, '#6a5646')   # shop door and its canopy
box(40.4, L, 3.85, 13.1, 0.0, 0.5, W2)                                         # the projecting bay of the corner tower
for z0, z1 in ((6.1, 7.9), (10.4, 11.45)):
    it.append(['glass', 40.6, 43.0, round(z0 + PV, 2), round(z1 + PV, 2), GL, 0.52])
    for m in (40.6, 41.36, 42.16, 42.92): box(m, m + 0.08, z0, z1, 0.5, 0.56, WH)
    box(40.6, 43.0, z0 - 0.08, z0, 0.5, 0.58, WH); box(40.6, 43.0, z1, z1 + 0.08, 0.5, 0.56, WH)
it.append(['door', 41.0, 42.25, 0.2 + PV, 3.35 + PV, '#8a5a34'])               # wooden double door under the bay
box(40.8, 41.0, -PV, 3.6, 0.0, 0.06, GR); box(42.25, 42.5, -PV, 3.6, 0.0, 0.06, GR); box(40.8, 42.5, 3.35, 3.6, 0.0, 0.06, GR)
e = {"id": 111, "nobrick": True, "note": "Shell 111 along Rautatienpuistokatu: s 0..31.1 the cream classicist house (two doorways, wide end windows, four window "
     "axes, roughcast plinth, cornice), s 31.1..43.2 Rautatienpuistokatu 3 / Yrjönkatu 27 (109: white, shop windows, dark-framed windows, corner "
     "tower with a glazed bay). SV April 2026, two panos, rectified 19.11.2026; arches drawn square, one window behind a tree repeated, bay "
     "projection estimated; the south-west end and the Yrjönkatu side are not measured",
     "walls": [{"a": list(A), "b": list(B), "bare": CR, "kind": "plaster", "items": it}]}
p = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] not in (111, 109)] + [e]; open(p, 'w').write(json.dumps(F, indent=0)); print(len(it))
