import json
def S(s): return round((s + 1.1) * 41.0 / 43.1, 2)       # SV s (pano) -> footprint wall s (fitted: real ends at SV -1.1 and 42.0)
it = []
def box(s0, s1, z0, z1, d0, d1, c, k=None): it.append(['box', S(s0), S(s1), z0, z1, d0, d1, c] + ([k] if k else []))
WALL = '#a39582'; FR = '#4a4540'; GL = '#8d989c'; GRN = '#3f5a48'; GRAN = '#64493e'
# street floor: red-brown granite, shop glazing between granite piers, dark green glass fascia
box(-1.1, 42.0, 0.0, 3.9, 0.0, 0.04, GRAN)
for a, b in [(0.3, 4.6), (5.2, 8.5), (8.7, 10.4), (18.0, 21.3), (21.8, 24.8), (28.0, 30.8), (31.1, 35.3), (35.6, 37.2), (38.0, 41.6)]:
    it.append(['win', S(a), S(b), 0.4, 3.3, '#2b2a28', '#3b4144'])
it.append(['door', S(13.2), S(17.0), 0.0, 3.5, '#24211e'])            # gateway "Antinkatu 15" with an iron gate
it.append(['door', S(25.5), S(26.8), 0.1, 2.8, '#2a2724'])            # door 15 A
for a, b in [(12.3, 13.15), (17.0, 17.9), (21.3, 21.8), (24.8, 25.45), (26.8, 28.0), (30.8, 31.1), (35.3, 35.6), (37.2, 38.0)]:
    box(a, b, 0.0, 3.9, 0.0, 0.12, GRAN)
box(-1.1, 42.0, 3.9, 4.6, 0.0, 0.14, '#3a4740')                      # glass fascia
box(0.1, 4.8, 3.3, 3.7, 0.0, 0.9, '#c0603a')                         # orange awning, south shop
box(28.5, 34.5, 3.4, 3.95, 0.14, 0.2, '#e6e8ec')                     # shop sign on the fascia
box(13.5, 16.8, 4.75, 5.3, 0.0, 0.1, '#ececea')                      # 'barona' letters over the gate
box(27.6, 29.5, 4.7, 5.4, 0.0, 0.08, '#e9e2d6')                      # small sign board
box(25.15, 25.4, 5.2, 12.3, 0.2, 1.2, '#eeeeea')                     # white vertical sign
# storey ledges at sill level, a band over the shops, cornice
for z in (4.75, 5.4, 8.9, 12.35, 15.9): box(-1.1, 42.0, z, z + 0.14, 0.0, 0.08, '#6e655c')
box(-1.1, 42.0, 19.65, 20.0, 0.0, 0.25, '#8f857a')
box(30.95, 31.12, 0.0, 19.6, 0.06, 0.18, '#5a5a58')                   # downpipe
rows = [(5.55, 7.2), (9.05, 10.65), (12.5, 14.1), (16.05, 17.65)]
for z0, z1 in rows:
    for a, b in [(0.6, 2.4), (3.75, 5.6), (7.0, 8.8), (10.2, 12.0), (18.7, 20.5), (22.1, 23.9), (25.4, 27.2), (28.8, 30.55)]:
        it.append(['win', S(a), S(b), z0, z1, FR, GL])
    it.append(['winp', S(13.5), S(16.9), z0, z1, 3, GRN, GL])           # green-framed triple windows over the gateway
    box(13.4, 17.0, z0 - 0.12, z0, 0.0, 0.08, GRN); box(13.4, 17.0, z1, z1 + 0.12, 0.0, 0.08, GRN)
    box(13.4, 13.5, z0, z1, 0.0, 0.08, GRN); box(16.9, 17.0, z0, z1, 0.0, 0.08, GRN)
    it.append(['winp', S(33.1), S(35.4), z0, z1, 3, FR, GL])
# the bay window at the north end (projects ~0.8 m from the first floor up, window bands on its front)
box(37.9, 42.0, 4.75, 19.3, 0.0, 0.8, WALL, 'plaster')
for z0, z1 in rows:
    it.append(['glass', S(38.4), S(41.6), z0, z1, '#7f8a8e', 0.82])
    for m in (38.4, 39.5, 40.5, 41.6): box(m - 0.05, m + 0.05, z0, z1, 0.8, 0.86, FR)
    box(38.3, 41.7, z0 - 0.12, z0, 0.8, 0.88, '#6e655c')
e = {"id": 161, "note": "Antinkatu 15 A-B, Kehityksen talo (1939): warm grey-brown render, four floors of two-light windows (1.8 x 1.65 m, ~3.3 m apart) "
     "on thin dark sill ledges, a column of green-framed triple windows over the gateway 'Antinkatu 15', a projecting bay window at the north end, "
     "a red-brown granite shop floor with a dark green glass fascia, door 15 A, a white vertical sign (SV Antinkatu 15 pano, rectified, 18.11.2026; "
     "the pano reads the front 43.1 m long, fitted to the footprint edge 0-41.0 m)",
     "walls": [{"a": [-39.6, -11.3], "b": [-30.4, 28.6], "bare": WALL, "items": it}]}
F = json.load(open('/home/claude/pori/blender/facades.json'))
F = [f for f in F if f['id'] != 161] + [e]
open('/home/claude/pori/blender/facades.json', 'w').write(json.dumps(F, indent=0))
print(len(it))
