"""Walking network for the NPC pedestrians (19.11.2026): python3 tools/roads/build_walk.py  ->  walk.js
From tools/roads/osm_ways_center.json (OSM, game metres): footways, sidewalks, pedestrian streets, paths, steps and cycleways.
An edge that crosses or ends on a carriageway centre line is (half of) a crossing (flag 1): there the walkers obey the traffic lights (index.html).
Components of fewer than 8 nodes are dropped. Output: export default {n: [x, y, ... in dm], e: [i, j, flag, ...]}"""
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
for w in W:
    if w['t'].get('h') not in PED or w['t'].get('tu') or len(w['g']) < 2: continue
    for a, b in zip(w['g'], w['g'][1:]):
        i, j = nid(a), nid(b)
        if i == j: continue
        L = LineString([a, b]); cross = any(roads[k].crosses(L) or roads[k].distance(Point(a)) < 0.2 or roads[k].distance(Point(b)) < 0.2 for k in tree.query(L.buffer(0.3)))
        edges[(min(i, j), max(i, j))] = 1 if cross else 0
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
out = os.path.join(here, '..', '..', 'walk.js'); open(out, 'w').write('export default ' + json.dumps({'n': N, 'e': E}, separators=(',', ':')) + ';\n')
print('nodes', len(keep), 'edges', len(E) // 3, 'crossings', sum(E[2::3]), 'bytes', os.path.getsize(out))
