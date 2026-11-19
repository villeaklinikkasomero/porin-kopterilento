import json, sys
# 36 Rautatienpuistokatu 8 and 34 Rautatienpuistokatu 12 (both 1954, the same type): light brown brick, three storeys over a basement,
# two stairs with wooden double doors and stair windows half a storey off the flats' windows, white window frames, white eave board.
# Measured 19.11.2026 on a rectified wide Street View frame of No 8, April 2026: pano "8 Rautatienpuistokatu" 61.4794926, 21.7922824
# (-> x -198.07 y -725.12), heading 132, pitch 18. Calibrated on the shell: ends -> s = (s_m + 1.2) * 0.973; pavement and eave ->
# z = (z_m - 1.0) * 1.075 (the frame's own scale put the eave 0.8 m lower than the shell - heights may be off by about 0.5 m).
# No 12: its own frame stayed blurred; it shows the same ten window columns, two stairs and two doors in the same places
# (stairs at 0.255 and 0.70 of the length), so No 8's layout is REPEATED, scaled to its 32.1 m. Details of No 12 are not seen.
# No 6 (23) and No 10 (19) are NOT this layout (rendered end bays, different lengths): not done here.
PV = 0.26; BR = '#a98a70'; FR = '#e4e2dc'; GL = '#5f6b73'; WOOD = '#b0824a'; PL = '#8f8a80'
def house(A, B, L, k):
    it = []
    def box(s0, s1, z0, z1, d0, d1, c, kk=None): it.append(['box', round(s0 * k, 2), round(s1 * k, 2), round(z0 + PV, 2), round(z1 + PV, 2), d0, d1, c] + ([kk] if kk else []))
    def win(s0, s1, z0, z1, n, fr=FR, gl=GL): it.append(['winp', round(s0 * k, 2), round(s1 * k, 2), round(z0 + PV, 2), round(z1 + PV, 2), n, fr, gl])
    box(0, 31.9, -PV, 0.95, 0.0, 0.025, PL)                                    # concrete plinth
    box(0, 31.9, 11.1, 11.3, 0.0, 0.35, '#ecebe6')                             # eave board
    for a, b, n in ((1.33, 3.71, 3), (4.71, 6.06, 2), (10.2, 11.6, 2), (12.55, 13.9, 2), (16.63, 17.98, 2), (19.03, 20.39, 2), (24.66, 25.98, 2), (27.0, 28.36, 2)):
        for z0, z1 in ((2.24, 3.73), (5.52, 6.96), (8.72, 10.15)): win(a, b, z0, z1, n)
    for a, b in ((4.71, 6.06), (10.2, 11.6), (24.66, 25.98), (27.0, 28.36)): win(a, b, 0.2, 0.8, 2, PL, '#4a5257')    # basement windows
    for a, b, d0, d1 in ((7.47, 8.84, 6.87, 9.3), (21.82, 23.17, 21.28, 23.76)):                                       # the two stairs
        win(a, b, 3.88, 5.43, 2); win(a, b, 7.1, 8.6, 2); win(a, b, 9.7, 10.24, 2)
        box(d0, d1, -PV, 2.45, 0.0, 0.025, WOOD, 'wood'); it.append(['door', round((d0 + 0.5) * k, 2), round((d1 - 0.5) * k, 2), 0.15 + PV, 2.2 + PV, '#8a5f33'])
        win(d0 + 0.08, d0 + 0.45, 0.5, 2.2, 1, WOOD, GL); win(d1 - 0.45, d1 - 0.08, 0.5, 2.2, 1, WOOD, GL)            # side lights
    return {"a": list(A), "b": list(B), "bare": BR, "kind": "brick", "items": it}, len(it)
w36, n36 = house((-172.824, -720.017), (-193.953, -743.875), 31.9, 1.0)
w34, n34 = house((-232.851, -786.778), (-254.125, -810.805), 32.1, 32.1 / 31.9)
note = ("Rautatienpuistokatu %s (1954): light brown brick, three storeys, ten window columns, two stairs with wooden double doors and offset "
        "stair windows, white frames and eave board (SV April 2026, pano 8 Rautatienpuistokatu, wide frame, rectified 19.11.2026%s)")
E8 = {"id": 36, "note": note % ('8', '; the other sides are not measured'), "walls": [w36]}
E12 = {"id": 34, "note": note % ('12', '; LAYOUT REPEATED from No 8 - its own frame was blurred and only confirms the columns, stairs and doors'), "walls": [w34]}
p = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] not in (36, 34)] + [E8, E12]; open(p, 'w').write(json.dumps(F, indent=0)); print(n36, n34)
