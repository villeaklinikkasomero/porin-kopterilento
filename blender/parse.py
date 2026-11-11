# Parse MML Rakennukset 3D (CityGML LoD2) into game-map coordinates: per building a list of (type, ring[, holes]) polygons
import sys, pickle
from lxml import etree
from pyproj import Transformer
T = Transformer.from_crs(3067, 4326, always_xy=True)
MX, MY, LON0, LAT0 = 53278.0, 111437.0, 21.796, 61.486
NS = {'gml': 'http://www.opengis.net/gml', 'bldg': 'http://www.opengis.net/citygml/building/2.0'}
B = '{http://www.opengis.net/citygml/building/2.0}'
def ring(el):
    v = list(map(float, el.text.split())); pts = [(v[i], v[i + 1], v[i + 2]) for i in range(0, len(v), 3)]
    if pts and pts[0] == pts[-1]: pts = pts[:-1]
    return pts
out = []
X0, X1, Y0, Y1 = float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
for f in sys.argv[6:]:
    for ev, b in etree.iterparse(f, tag=B + 'Building', huge_tree=True):
        polys = []
        for kind in ('RoofSurface', 'WallSurface', 'GroundSurface'):
            for s in b.iter(B + kind):
                for pg in s.iter('{http://www.opengis.net/gml}Polygon'):
                    ex = pg.find('gml:exterior/gml:LinearRing/gml:posList', NS)
                    ins = [ring(e) for e in pg.findall('gml:interior/gml:LinearRing/gml:posList', NS)]
                    polys.append((kind[0], ring(ex), ins))
        if not polys: b.clear(); continue
        allp = [p for _, r, _ in polys for p in r]
        e = sum(p[0] for p in allp) / len(allp); n = sum(p[1] for p in allp) / len(allp)
        lon, lat = T.transform(e, n); cx, cy = (lon - LON0) * MX, (lat - LAT0) * MY
        if X0 <= cx <= X1 and Y0 <= cy <= Y1:
            # local linearisation around the building centre (sub-cm error over a building)
            lo2, la2 = T.transform(e + 100, n); lo3, la3 = T.transform(e, n + 100)
            ax, ay = ((lo2 - lon) * MX / 100, (la2 - lat) * MY / 100); bx, by = ((lo3 - lon) * MX / 100, (la3 - lat) * MY / 100)
            def cv(p): de, dn = p[0] - e, p[1] - n; return (cx + ax * de + bx * dn, cy + ay * de + by * dn, p[2])
            zg = min(p[2] for k, r, _ in polys if k == 'G' for p in r) if any(k == 'G' for k, _, _ in polys) else min(p[2] for p in allp)
            h = b.find('bldg:measuredHeight', NS); rt = b.find('bldg:roofType', NS)
            out.append({'id': b.get('{http://www.opengis.net/gml}id'), 'c': (cx, cy), 'z0': zg, 'h': float(h.text) if h is not None else None,
                        'rt': rt.text if rt is not None else None, 'p': [(k, [cv(p) for p in r], [[cv(p) for p in hh] for hh in ins]) for k, r, ins in polys]})
        b.clear()
        while b.getprevious() is not None: del b.getparent()[0]
pickle.dump(out, open(sys.argv[1], 'wb')); print(len(out))
