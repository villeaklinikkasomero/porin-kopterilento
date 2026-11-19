"""Walking network for the NPC pedestrians (19.11.2026): python3 tools/roads/build_walk.py  ->  walk.js
From tools/roads/osm_ways_center.json (OSM, game metres): footways, sidewalks, pedestrian streets, paths, steps and cycleways.
An edge that crosses or ends on a carriageway centre line is (half of) a crossing (flag 1): there the walkers obey the traffic lights (index.html).
Components of fewer than 8 nodes are dropped. Output: export default {n: [x, y, ... in dm], e: [i, j, flag, ...], b: [busy node indices], g: [square grid node indices]}"""
import json, os, collections
from shapely.geometry import LineString, Point
from shapely.strtree import STRtree
here = os.path.dirname(os.path.abspath(__file__)); W = json.load(open(os.path.join(here, 'osm_ways_center.json')))
PED = ('footway', 'pedestrian', 'path', 'steps', 'cycleway'); CAR = ('primary', 'secondary', 'tertiary', 'residential', 'unclassified', 'trunk', 'primary_link', 'secondary_link', 'tertiary_link', 'trunk_link')
roads = [LineString(w['g']) for w in W if w['t'].get('h') in CAR and len(w['g']) > 1]; tree = STRtree(roads)
idx = {}; nodes = []; edges = {}
def nid(p):
    k = (round(p[0] * 10), round(p[1] * 10))
    if k not in idx: idx[k] = len(nodes); nodes.append(k)
    return idx[k]
busy = set(); grid = set()                 # busy: the pedestrian streets and Kauppatori (more people are spawned there); grid: the open square
for w in W:
    if w['t'].get('h') not in PED or w['t'].get('tu') or len(w['g']) < 2: continue
    if w['t'].get('h') == 'pedestrian': busy.update(nid(q) for q in w['g'])
    for a, b in zip(w['g'], w['g'][1:]):
        i, j = nid(a), nid(b)
        if i == j: continue
        L = LineString([a, b]); cross = any(roads[k].crosses(L) or roads[k].distance(Point(a)) < 0.2 or roads[k].distance(Point(b)) < 0.2 for k in tree.query(L.buffer(0.3)))
        edges[(min(i, j), max(i, j))] = 1 if cross else 0
# Kauppatori is an open square: its outline alone would keep everybody on the edge, so a 9 m grid of nodes fills it (8-neighbour links, joined to
# the outline). The game drops the grid nodes that fall inside a building (the market pavilion).
from shapely.geometry import Polygon
for w in W:
    if w['t'].get('n') == 'Kauppatori' and w['t'].get('h') == 'pedestrian' and w['g'][0] == w['g'][-1]:
        P = Polygon(w['g']); x0, y0, x1, y1 = P.bounds; G = {}; ST = 9.0
        for ix in range(int((x1 - x0) / ST) + 1):
            for iy in range(int((y1 - y0) / ST) + 1):
                q = (x0 + 4 + ix * ST, y0 + 4 + iy * ST)
                if P.buffer(-3).contains(Point(q)): G[(ix, iy)] = nid(q); grid.add(G[(ix, iy)]); busy.add(G[(ix, iy)])
        for (ix, iy), i in G.items():
            for dx, dy in ((1, 0), (0, 1), (1, 1), (1, -1)):
                j = G.get((ix + dx, iy + dy))
                if j is not None: edges[(min(i, j), max(i, j))] = 0
        for q in w['g'][:-1]:                                  # each outline node to its nearest grid node
            i = nid(q); j = min(G.values(), key=lambda k: (nodes[k][0] / 10 - q[0]) ** 2 + (nodes[k][1] / 10 - q[1]) ** 2)
            edges[(min(i, j), max(i, j))] = 0
adj = collections.defaultdict(list)
for (i, j) in edges: adj[i].append(j); adj[j].append(i)
comp = {}; 
for s in range(len(nodes)):
    if s in comp: continue
    st = [s]; comp[s] = s; n = 1
    while st:
        u = st.pop()
        for v in adj[u]:
            if v not in comp: comp[v] = s; st.append(v); n += 1
    comp[('n', s)] = n
keep = [i for i in range(len(nodes)) if comp[('n', comp[i])] >= 8]; re = {i: k for k, i in enumerate(keep)}
N = [v for i in keep for v in nodes[i]]; E = [v for (i, j), f in edges.items() if i in re and j in re for v in (re[i], re[j], f)]
out = os.path.join(here, '..', '..', 'walk.js'); open(out, 'w').write('export default ' + json.dumps({'n': N, 'e': E, 'b': sorted(re[i] for i in busy if i in re), 'g': sorted(re[i] for i in grid if i in re)}, separators=(',', ':')) + ';\n')
print('busy', len(busy), 'grid', len(grid), 'nodes', len(keep), 'edges', len(E) // 3, 'crossings', sum(E[2::3]), 'bytes', os.path.getsize(out))
