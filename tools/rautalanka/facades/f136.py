import json, sys, math
# 136 Antinkatu 21a (1979), two-storey concrete commercial building at the Liisankatu corner. Measured 19.11.2026 on rectified Street View:
# Antinkatu 21 pano 61.484163, 21.7946236 -> x -73.33 y -204.7 (headings 283 / 245), Liisankatu 10 pano 61.484379, 21.7941287 (heading 195).
# The rectified Antinkatu front came out 24.9 m long with the eave at 8.5 m: the front stands nearer the camera than the footprint line, so
# s = (s_measured + 1.5) * 0.879 (ends on the footprint corners) and z = (z_measured - 0.1) * 0.92 (eave on the scan's 7.7 m).
# The LoD2 shell is much smaller than the house (east wall 16.3 m against 21.9 m), so 136 is built on its footprint (zones.py SPEC[136],
# index.html L2OLD / HFIX); the street floor is set back under the upper floor in the SPEC, everything else is drawn here.
# Upper floor: precast eave band with ribbed relief panels between tapered piers (module 2.4 m), a ribbon of dark-framed windows, two per module,
# brown spandrel, a red sign fascia hung in front (orange on the west part of Liisankatu), dark soffit; terrace railing on Antinkatu.
CONC = '#9a958c'; CONL = '#b7b2a8'; DARK = '#3a3835'; BRN = '#4a4540'; FR = '#2e2c2a'; GL = '#6f7b80'; RED = '#b3262b'; ORA = '#e07a1f'; WH = '#efece6'
def wall(a, b, red_to, plain0, rail):
    L = math.hypot(b[0] - a[0], b[1] - a[1]); n = round(L / 2.43); m = L / n; it = []
    def box(s0, s1, z0, z1, d0, d1, c, k=None): it.append(['box', round(s0, 2), round(s1, 2), round(z0, 2), round(z1, 2), d0, d1, c] + ([k] if k else []))
    box(0, L, 6.62, 7.7, 0.0, 0.25, CONC)                                       # eave band
    box(0, L, 7.62, 7.74, 0.0, 0.3, '#5a5a58')                                  # flashing
    box(0, L, 6.35, 6.62, 0.0, 0.1, DARK)                                       # shadow beam over the windows
    box(0, L, 4.78, 5.2, 0.0, 0.05, BRN)                                        # spandrel
    box(0, L, 3.5, 3.77, 0.0, 0.35, '#2a2a2a')                                  # soffit edge
    for k in range(n):
        s0, s1 = k * m, (k + 1) * m
        box(s0 + 0.3, s1 - 0.3, 6.86, 7.46, 0.25, 0.28, CONL)                   # ribbed relief panel
        for j in range(1, 6): box(s0 + 0.3, s1 - 0.3, 6.86 + j * 0.1 - 0.012, 6.86 + j * 0.1 + 0.012, 0.28, 0.29, '#8e897f')
        it.append(['winp', round(s0 + 0.1, 2), round(s1 - 0.1, 2), 5.2, 6.35, 2, FR, GL])
        if k * m < plain0: box(s0, s1, 3.77, 4.78, 0.0, 0.1, CONL)              # the plain bay next to the neighbour: concrete panel, no sign
    for k in range(n + 1):
        c = min(max(k * m, 0.16), L - 0.16); box(c - 0.16, c + 0.16, 6.62, 7.7, 0.25, 0.42, CONC)   # tapered piers of the eave band
    r0 = math.ceil(plain0 / m) * m
    box(r0, min(L, red_to), 3.77, 4.78, 0.0, 0.35, RED)
    if red_to < L: box(red_to, L, 3.77, 4.78, 0.0, 0.35, ORA)
    c = r0 + 2.4
    while c + 1.2 < L:                                                          # lettering as plain light bars (no logo copied)
        box(c - 1.0, c + 1.0, 4.17, 4.38, 0.35, 0.37, WH); c += 5.2
    if rail: box(rail[0], rail[1], 0.0, 1.05, 0.25, 0.3, '#26282a'); box(rail[0], rail[1], 0.0, 0.25, 0.3, 0.35, '#3a3a3a')
    if plain0:                                                                  # gateway bay: wall panel and a light bar gate
        box(0, r0, 0.0, 3.5, 0.0, 0.06, CONL); it.append(['door', 0.45, r0 - 0.35, 0.0, 2.9, '#55585a'])
        s = 0.55
        while s < r0 - 0.4: box(s, s + 0.04, 0.05, 2.85, 0.03, 0.06, '#d9d9d6'); s += 0.16
    return {"a": list(a), "b": list(b), "items": it}
e = {"id": 136, "nobrick": True, "note": "Antinkatu 21a (1979), corner of Liisankatu: two-storey concrete building, upper floor carried over a set-back glazed street floor; "
     "precast eave band with ribbed relief panels, window ribbon, red / orange sign fascia (SV Antinkatu 21 and Liisankatu 10 panos, rectified, 19.11.2026; "
     "built on the footprint, eave 7.7 m)",
     "walls": [wall((-91.2, -217.2), (-86.4, -195.8), 99, 2.0, (2.6, 18.2)), wall((-86.4, -195.8), (-124.3, -187.3), 21.9, 0, None)]}
p = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] != 136] + [e]; open(p, 'w').write(json.dumps(F, indent=0)); print(sum(len(w['items']) for w in e['walls']))
