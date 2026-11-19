import json, sys
# 276 Antinkatu 20 / Mikonkatu corner: one-storey yellow timber house on a high dark plinth. Measured 19.11.2026 on rectified Street View
# (Antinkatu 22 pano 61.4830179, 21.793986 -> x -107.3 y -332.3, headings 103 / 55): front 22.5 m (LoD2 wall 22.2 m), pavement at z 0.3,
# so s = s_measured + 0.9 from the Mikonkatu corner and z = z_measured - 0.3. Rendered plinth 1.7 m with cellar vents, horizontal boarding,
# six tall two-light windows with a transom in white casings (no door on this side), a frieze with four small attic windows, grey sheet roof.
A = (-92.928, -320.025); B = (-98.346, -342.245); L = 22.87   # wall line from raw.pkl
YEL = '#e2c06a'; WH = '#f1efe8'; GL = '#59636a'; PL = '#6f6d69'
it = []
def box(s0, s1, z0, z1, d0, d1, c, k=None): it.append(['box', round(s0, 2), round(s1, 2), round(z0, 2), round(z1, 2), d0, d1, c] + ([k] if k else []))
box(0, L, 0.0, 1.7, 0.0, 0.07, PL)                                          # rendered plinth
box(0, L, 1.7, 1.8, 0.0, 0.1, WH)                                           # water table
box(0, L, 2.6, 2.68, 0.0, 0.05, WH)                                         # sill band
box(0, L, 5.02, 5.12, 0.0, 0.05, WH)                                        # frieze band
box(0, L, 6.5, 6.9, 0.0, 0.3, '#e8e6df')                                    # eaves board
for s in (0.0, L - 0.16): box(s, s + 0.16, 1.8, 6.5, 0.0, 0.05, WH)         # corner boards
for s in (2.4, 6.1, 9.0, 12.8, 16.5, 19.6):
    box(s - 0.13, s + 1.23, 2.68, 4.82, 0.0, 0.04, WH)                      # casing
    it.append(['winp', s, s + 1.1, 2.8, 4.65, 2, WH, GL])
    box(s, s + 1.1, 4.05, 4.12, 0.04, 0.07, WH)                             # transom
for s in (2.5, 7.6, 12.9, 18.2):
    box(s - 0.08, s + 0.88, 5.42, 6.03, 0.0, 0.04, WH); it.append(['winp', s, s + 0.8, 5.5, 5.95, 2, WH, GL])   # attic windows in the frieze
for s in (0.7, 7.3, 13.3, 18.4): it.append(['door', s, s + 0.5, 0.85, 1.35, '#343434'])   # cellar vents
box(16.0, 16.1, 0.3, 6.5, 0.05, 0.15, '#d8d8d4')                            # downpipe
e = {"id": 276, "note": "Antinkatu 20, one-storey yellow timber house on a 1.7 m rendered plinth: six tall two-light windows in white casings, "
     "frieze with four attic windows, no door on Antinkatu (SV Antinkatu 22 pano, rectified, 19.11.2026)",
     "walls": [{"a": list(A), "b": list(B), "bare": YEL, "kind": "wood", "items": it}]}
p = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] != 276] + [e]; open(p, 'w').write(json.dumps(F, indent=0)); print(len(it))
