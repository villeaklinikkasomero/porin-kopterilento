import json, sys
# 1217 Hallitalo, Yrjönkatu 12 ("Hellmanin pilvenpiirtäjä", 1927; block tori4): the Yrjönkatu (west) face, 24.5 m - with the KAUPPAHALLI
# ENTRANCE: the market hall runs through the block and is entered from Yrjönkatu through this house's ground floor (owner 20.11.2026:
# "kauppahallin sisäänkäyntiä ei näy"; "kauppahalli on läpi talon, sisäänkäynti Yrjönkadulla myös").
# Measured 20.11.2026 on rectified Street View frames, pano "12 Yrjönkatu" 61.4857386, 21.7977328 (-> x 92.33 y -29.13), headings
# 58 / 103 / 148, pitch 14. Only the heading-103 frame was sharp (s 9 .. 21); the two oblique frames stayed blurred and give the ends:
# north edge s_m -0.5, south corner s_m 22.1 against the footprint's 0 .. 24.5 -> s = 15.0 + (s_m - 13.33) * 1.084, z = 1.084 z_m - 0.21.
# Cream render, five storeys; a dark red-brown ground floor under a cornice; six window axes (3.77 m apart, symmetric) on four floors;
# the hall's portal between the 2nd and 3rd axis from the north: an opening with two columns, a name board over it (lettering not
# copied) and a round-headed niche on the first floor above; shop fronts with cream sign panels (lettering not copied).
# The portal itself follows the owner's two photos (20.11.2026): an opening about 5 m wide and 3.4 m high with two pink granite
# columns, a cream name panel breaking the cornice above it, a cream vestibule with the hall's dark double doors at the back.
# Uncertain: the shop bay north of the portal and the top floor are read from blurred / cropped frames.
A = (103.0, -17.9); B = (97.5, -41.8); L = 24.5; PV = 0.26
CR = '#e2d3a4'; WH = '#f2ecd8'; GL = '#56636b'; SHOP = '#2f3538'; SIGN = '#d9cfae'
it = []
def box(s0, s1, z0, z1, d0, d1, c, k=None): it.append(['box', round(s0, 2), round(s1, 2), round(z0 + PV, 2), round(z1 + PV, 2), d0, d1, c] + ([k] if k else []))
def win(s0, s1, z0, z1, n, fr=WH, gl=GL): it.append(['winp', round(s0, 2), round(s1, 2), round(z0 + PV, 2), round(z1 + PV, 2), n, fr, gl])
G0, G1, GH = 6.45, 11.45, 3.4                                                  # the portal: 5 m wide, 3.4 m high (owner's photos 20.11.2026)
RB = '#84575a'; RBD = '#6f4648'                                                # the ground floor is a muted red-brown (owner's photo), not brick red
for a, b in ((0.0, G0), (G1, L)): box(a, b, -PV, 5.2, 0.0, 0.025, RB)           # red-brown ground floor, open at the portal
box(G0, G1, GH, 5.2, 0.0, 0.025, RB)                                           # lintel zone over the opening
for a, b in ((0.0, 7.95), (9.95, L)): box(a, b, 5.2, 5.6, 0.0, 0.25, RBD)       # cornice, broken by the cream name panel in the middle
box(7.95, 9.95, 3.75, 6.0, 0.025, 0.07, CR)                                    # name panel over the portal
box(8.2, 9.7, 5.75, 5.95, 0.0, 0.3, WH)                                        # console under the window above it
for a, b in ((6.75, 7.75), (10.15, 11.15)): box(a, b, 4.2, 4.95, 0.025, 0.06, SIGN)   # the two small cream panels beside it
for a, b in ((1.0, 5.6), (12.3, 17.2), (18.0, 23.6)):                          # shop fronts and their sign panels
    win(a, b, 0.6, 3.9, 3, RBD, SHOP); box(a, b, 4.25, 5.0, 0.025, 0.06, SIGN)
# The portal is a REAL RECESS 3 m deep (owner 20.11.2026: "tee sisäänveto kauppahallin ovelle, syvennys noin 3 metriä jonka jälkeen ovi"):
# "gate" + "fp" in the wall entry - zones.py gives the stretch a footprint edge of its own and sets its ground storey 3 m back with
# reveals, a soffit and a back wall. Items with negative d stand inside the recess: the two granite columns in the opening, the hall's
# dark double doors with lit glazing on the back wall. The side doors on the reveals are not drawn.
DP = 3.0
for c in (7.75, 10.15):
    box(c - 0.21, c + 0.21, 0.4, GH, -0.47, -0.05, '#b59a94'); box(c - 0.3, c + 0.3, -PV, 0.4, -0.56, 0.04, '#a58c86')
box(8.1, 9.8, -PV, 2.75, -DP, -DP + 0.06, '#1d1714')                            # the hall's double doors on the back wall
for a in (8.22, 9.0): box(a, a + 0.68, 0.55, 2.35, -DP + 0.06, -DP + 0.08, '#b08a4a')   # their lit glazing
box(8.25, 9.65, 2.85, 3.08, -DP, -DP + 0.05, '#3a3530')                         # name board over the inner doors (blank)
box(G0, G1, -PV, 0.14 - PV + 0.0, -DP, 0.3, '#8f8a84')                          # paving of the vestibule up to the street
# the word HALLI over the portal (owner 20.11.2026: "merkitse teksti HALLI"), plain block letters built of bars - not the real lettering
LC = '#8a7440'; lw, lg, st, lz, lh = 0.3, 0.085, 0.085, 4.25, 0.85; ls = 8.95 - (5 * lw + 4 * lg) / 2
def bar(x0, x1, z0, z1): box(ls + x0, ls + x1, lz + z0, lz + z1, 0.07, 0.1, LC)
for n_, ch in enumerate('HALLI'):
    x = n_ * (lw + lg)
    if ch == 'H': bar(x, x + st, 0, lh); bar(x + lw - st, x + lw, 0, lh); bar(x, x + lw, lh / 2 - st / 2, lh / 2 + st / 2)
    elif ch == 'A': bar(x, x + st, 0, lh); bar(x + lw - st, x + lw, 0, lh); bar(x, x + lw, lh - st, lh); bar(x, x + lw, lh * 0.4, lh * 0.4 + st)
    elif ch == 'L': bar(x, x + st, 0, lh); bar(x, x + lw, 0, st)
    elif ch == 'I': bar(x + lw / 2 - st / 2, x + lw / 2 + st / 2, 0, lh)
for k in range(6):
    c = 3.1 + 3.772 * k
    for j, (z0, z1) in enumerate(((5.95, 7.7), (9.3, 11.2), (12.9, 14.9), (16.6, 18.5))):
        win(c - 0.64, c + 0.64, z0, z1, 2)
e = {"id": 1217, "nobrick": True, "note": "Hallitalo, Yrjönkatu 12 (1927), Yrjönkatu face with the Kauppahalli portal: cream render, red-brown ground floor and cornice, "
     "six window axes on four floors, the hall's portal as a recess 3 m deep with two granite columns and the hall's doors on its back wall, the word HALLI on a cream panel breaking the cornice, shop "
     "fronts (SV pano 12 Yrjönkatu, rectified 20.11.2026; ends and top floor from blurred frames; the other sides are not measured)",
     "walls": [{"a": list(A), "b": list(B), "bare": CR, "kind": "plaster", "gate": [G0, G1, GH, DP, 20.0], "fp": True, "items": it}]}
p = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] != 1217] + [e]; open(p, 'w').write(json.dumps(F, indent=0)); print(len(it))
