"""Cut (45 degree) corners for the MML LoD2 shells.

The MML LoD2 models have square corners everywhere, but many older blocks in the centre have a chamfered corner (an entrance,
often a balcony or bay above).  OSM draws some of them.  Where an OSM footprint has a short diagonal side (1.5-6 m, about
45 degrees to both neighbours) and the LoD2 model has a square corner behind it, every face of the shell (ground, walls, roof)
is clipped by the vertical plane through the diagonal, and a new wall face is added along it.  build_lod2 then gives the
diagonal its own facade run like any other wall.  styles.json 'ch': [[x, y, w], ...] adds chamfers OSM does not have:
the LoD2 corner nearest (x, y) is cut so that the diagonal face is w metres wide.  (user 13.11.2026)
"""
import math

def _ang(u, v): return math.degrees(math.atan2(v[0] - u[0], v[1] - u[1]))

def osm_chamfers(pts):
    """diagonal sides of an OSM footprint: [(a, c)] in metres"""
    out = []; n = len(pts)
    for k in range(n):
        a, c = pts[k], pts[(k + 1) % n]; pa, cn = pts[k - 1], pts[(k + 2) % n]
        L = math.hypot(c[0] - a[0], c[1] - a[1])
        if not 1.5 < L < 6: continue
        if math.hypot(a[0] - pa[0], a[1] - pa[1]) < 3 or math.hypot(cn[0] - c[0], cn[1] - c[1]) < 3: continue
        a1 = (_ang(a, c) - _ang(pa, a)) % 180; a2 = (_ang(c, cn) - _ang(a, c)) % 180
        if (35 < a1 < 55 or 125 < a1 < 145) and (35 < a2 < 55 or 125 < a2 < 145): out.append((a, c))
    return out

def clip_poly(r, px, py, nx, ny):
    """keep the part of a 3D polygon with (p - P).n >= 0 (vertical cutting plane through P with horizontal normal n)"""
    out = []; m = len(r)
    for k in range(m):
        A, Bq = r[k], r[(k + 1) % m]
        da = (A[0] - px) * nx + (A[1] - py) * ny; db = (Bq[0] - px) * nx + (Bq[1] - py) * ny
        if da >= 0: out.append(tuple(A))
        if (da >= 0) != (db >= 0):
            t = da / (da - db); out.append(tuple(A[j] + (Bq[j] - A[j]) * t for j in range(3)))
    return out

def cut(parts, a, c, inside):
    """clip all parts by the line a-c, keeping the side of the point 'inside'; add the diagonal wall.  None if nothing was cut."""
    from shapely.geometry import Polygon, LineString
    tx, ty = c[0] - a[0], c[1] - a[1]; L = math.hypot(tx, ty); tx, ty = tx / L, ty / L; nx, ny = -ty, tx
    if (inside[0] - a[0]) * nx + (inside[1] - a[1]) * ny < 0: nx, ny = -nx, -ny
    G = [Polygon([(p[0], p[1]) for p in r]).buffer(0) for k, r, _ in parts if k == 'G' and len(r) >= 3]
    if not G: return None
    from shapely.ops import unary_union
    FP = unary_union(G)
    lost = sum(g.area for g in G) - sum(Polygon([(p[0], p[1]) for p in clip_poly(r, a[0], a[1], nx, ny)]).buffer(0).area
                                         for k, r, _ in parts if k == 'G' and len(r) >= 3 and len(clip_poly(r, a[0], a[1], nx, ny)) >= 3)
    if lost < 0.4 or lost > 40: return None                       # the shell has no corner there (or the line cuts through the building)
    far = 60
    seg = LineString([(a[0] - tx * far, a[1] - ty * far), (c[0] + tx * far, c[1] + ty * far)]).intersection(FP.boundary)
    pts = [(q.x, q.y) for q in getattr(seg, 'geoms', [seg]) if q.geom_type == 'Point']
    out = []; on = []
    for k, r, holes in parts:
        rr = clip_poly(r, a[0], a[1], nx, ny)
        if len(rr) < 3: continue
        out.append((k, rr, holes))
        if k not in ('G', 'R'):
            for p in rr:
                if abs((p[0] - a[0]) * nx + (p[1] - a[1]) * ny) < 0.02: on.append(p)
    if len(on) < 2: return None
    us = [((p[0] - a[0]) * tx + (p[1] - a[1]) * ty, p[2]) for p in on]
    u0, u1 = min(u for u, _ in us), max(u for u, _ in us)
    if u1 - u0 < 0.8: return None
    zb = min(z for _, z in us)
    top = lambda u0_: max(z for u, z in us if abs(u - u0_) < 0.05)
    P3 = lambda u, z: (a[0] + tx * u, a[1] + ty * u, z)
    out.append(('W', [P3(u0, zb), P3(u1, zb), P3(u1, top(u1)), P3(u0, top(u0))], []))
    return out

def apply(RAW, B, LOOK, ids=None):
    """chamfer the shells of RAW in place; returns {id: number of corners cut}"""
    done = {}
    for i in (ids if ids is not None else list(RAW)):
        if i >= len(B) or not RAW.get(i): continue
        p = B[i]['p']; pts = [(p[k] / 10, p[k + 1] / 10) for k in range(0, len(p), 2)]
        cx = sum(q[0] for q in pts) / len(pts); cy = sum(q[1] for q in pts) / len(pts)
        segs = osm_chamfers(pts)
        for x, y, w in (LOOK['b'].get(str(i)) or {}).get('ch', []):
            G = [r for k, r, _ in RAW[i] if k == 'G' and len(r) >= 3]
            best = None
            for r in G:
                for k in range(len(r)):
                    q = r[k]; dd = math.hypot(q[0] - x, q[1] - y)
                    if best is None or dd < best[0]: best = (dd, r[k - 1], q, r[(k + 1) % len(r)])
            if not best: continue
            _, pa, q, pn = best; s = w / math.sqrt(2)
            ua = (pa[0] - q[0], pa[1] - q[1]); la = math.hypot(*ua); ub = (pn[0] - q[0], pn[1] - q[1]); lb = math.hypot(*ub)
            segs.append(((q[0] + ua[0] / la * s, q[1] + ua[1] / la * s), (q[0] + ub[0] / lb * s, q[1] + ub[1] / lb * s)))
        ok = []
        for a, c in segs:
            r = cut(RAW[i], a, c, (cx, cy))
            if r: RAW[i] = r; ok.append((a, c, (cx, cy)))
        if ok: done[i] = ok
    return done

def clip_lod2(L2, done):
    """the same cuts on the game's lod2.js roof triangles (dm, relative to o): the game draws the measured roofs itself"""
    for i, segs in done.items():
        e = L2['b'].get(str(i))
        if not e or not e.get('r'): continue
        ox, oy = e['o']; r = e['r']
        tris = [[((ox + r[k + 3 * j]) / 10, (oy + r[k + 3 * j + 1]) / 10, r[k + 3 * j + 2] / 10) for j in range(3)] for k in range(0, len(r) - 8, 9)]
        for a, c, ins in segs:
            tx, ty = c[0] - a[0], c[1] - a[1]; L = math.hypot(tx, ty); nx, ny = -ty / L, tx / L
            if (ins[0] - a[0]) * nx + (ins[1] - a[1]) * ny < 0: nx, ny = -nx, -ny
            nt = []
            for t in tris:
                p = clip_poly(t, a[0], a[1], nx, ny)
                for k in range(1, len(p) - 1): nt.append([p[0], p[k], p[k + 1]])
            tris = nt
        e['r'] = [int(round(v)) for t in tris for q in t for v in ((q[0] * 10 - ox), (q[1] * 10 - oy), q[2] * 10)]
    return L2
