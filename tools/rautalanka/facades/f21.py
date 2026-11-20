import json, sys
# 21 (shell of Satakunnankatu 23, c046): the LOW THREE-STOREY WING along Rautatienpuistokatu, 36.1 m (the six-storey slab behind it keeps
# its SPEC). Grey roughcast, white window frames, wide three-part windows between narrow ones, two wooden pointed-arch doorways with
# steps, and a column of glazed balconies with light parapet panels at each end.
# Measured 20.11.2026 on three rectified Street View frames, April 2026, pano "11 Rautatienpuistokatu" 61.4785751, 21.7906462
# (-> x -285.24 y -827.43; headings 85 / 124.2 / 162.69, pitch 14; all sharp - turned by dragging in the loaded pano).
# Calibrated on the shell: both ends -> s = 1.92 + 0.939 s_m; pavement and eave (11.7) -> z = (z_m - 0.9) * 1.116. The frame's own
# scale gives the eave only 9.9 m above the pavement: the shell's base lies lower than the street, so heights may be up to 1 m too tall.
# Simplified: the doorways' pointed tops are square, the balconies are flush glazing (no depth), basement windows and pipes left out.
PV = 0.26; GR = '#8d8a82'; FR = '#ecebe6'; GL = '#5f6b73'; WOOD = '#a8743a'; PL = '#6f6c66'; PAN = '#d9d6cc'
S = lambda s: 1.92 + 0.939 * s
Zf = lambda z: (z - 0.9) * 1.116
A = (-262.543, -820.12); B = (-286.337, -847.299); L = 36.1; it = []
def box(s0, s1, z0, z1, d0, d1, c, k=None): it.append(['box', round(max(0.0, s0), 2), round(min(L, s1), 2), round(z0 + PV, 2), round(z1 + PV, 2), d0, d1, c] + ([k] if k else []))
def win(s0, s1, z0, z1, n, fr=FR, gl=GL): it.append(['winp', round(s0, 2), round(s1, 2), round(z0 + PV, 2), round(z1 + PV, 2), n, fr, gl])
G0, M0, T0 = (Zf(3.14), Zf(4.63)), (Zf(6.02), Zf(7.51)), (Zf(8.88), Zf(10.37))
box(0, L, -PV, 0.9, 0.0, 0.025, PL); box(0, L, 11.5, 11.7, 0.0, 0.35, '#ecebe6')
for a, b, n in ((3.9, 7.2, 3), (8.1, 8.9, 1), (9.8, 10.54, 1), (11.5, 14.12, 3), (15.05, 16.69, 2), (17.97, 19.6, 2), (20.56, 23.3, 3), (24.25, 24.98, 1), (25.93, 26.7, 1), (27.65, 28.4, 1), (28.85, 30.93, 3)):
    for z0, z1 in (M0, T0): win(S(a), S(b), z0, z1, n)
for a, b, n in ((3.9, 6.02, 3), (6.46, 7.2, 1), (11.5, 12.18, 1), (12.65, 14.1, 2), (15.05, 16.69, 2), (17.97, 19.6, 2), (20.56, 22.2, 2), (22.5, 23.3, 1), (27.7, 28.4, 1), (28.85, 30.93, 3)):
    win(S(a), S(b), G0[0], G0[1], n)
for a, b in ((8.25, 10.4), (24.4, 26.52)):                                       # wooden doorways with steps
    box(S(a), S(b), 0.5, Zf(4.5), 0.0, 0.025, WOOD, 'wood'); win(S(a) + 0.2, S(b) - 0.2, 0.75, Zf(4.5) - 0.25, 2, '#8a5f33', '#4f5d68')
    box(S(a) - 0.3, S(b) + 0.3, -PV, 0.5, 0.0, 0.9, '#77736c')
for a, b in ((-0.77, 2.0), (32.9, 35.9)):                                        # glazed balcony columns (flush)
    for z0, z1 in (M0, T0):
        box(S(a), S(b), z0 - 1.05, z0 - 0.1, 0.0, 0.03, PAN); win(max(0.1, S(a)), min(L - 0.1, S(b)), z0 - 0.1, z1 + 0.15, 3, '#c9c8c2', '#6d7c88')
    win(max(0.1, S(a)), min(L - 0.1, S(b)), Zf(1.3), Zf(3.9), 2, '#dcdad2', '#8a959c')
e = {"id": 21, "nobrick": True, "note": "Low three-storey wing of Satakunnankatu 23 along Rautatienpuistokatu: grey roughcast, white frames, wide and narrow windows, "
     "two wooden doorways with steps, a glazed balcony column with parapet panels at each end (SV April 2026, pano 11 Rautatienpuistokatu, "
     "three sharp frames, rectified 20.11.2026; doorways drawn square, balconies flush; the six-storey slab and other sides are not measured)",
     "walls": [{"a": list(A), "b": list(B), "bare": GR, "kind": "plaster", "items": it}]}
p = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/pori/blender/facades.json'; F = json.load(open(p))
F = [f for f in F if f['id'] != 21] + [e]; open(p, 'w').write(json.dumps(F, indent=0)); print(len(it))
