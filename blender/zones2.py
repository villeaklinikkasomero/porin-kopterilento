"""Blender facades on the measured LoD2 massing (Maanmittauslaitos Rakennukset 3D).
Every LoD2 wall polygon gets a gen.py facade on its rectangular part (ground .. eave); the rest of the polygon (gables,
stepped parapets) is real geometry in the wall colour. LoD2 roofs are only shadow casters here: in the game the roofs
keep the aerial photo on the measured roof shape."""
import bpy, pickle, math, statistics, json
from shapely.geometry import Polygon, box
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from zones import *
RAW = pickle.load(open('/home/claude/mmlproc/raw.pkl', 'rb'))
STREET = None        # optional fn(mid_xy, normal_xy) -> True when the wall faces a street
ROOFOCC = M('#4f5459', 0.7)
ROOFBAKE = False     # True: the LoD2 roofs are baked into the block (Kivi-Pori); False: shadow casters only, the game shows the aerial photo
try: LOOK = json.load(open('/home/claude/pori/styles.json'))
except Exception: LOOK = dict(pal=[], b={})
for _k, _v in LOOK['b'].items():                     # styles 'hh': wall height when OSM / city.js has a wrong one and there is no LoD2 (13.11.2026)
    if 'hh' in _v and int(_k) < len(B): B[int(_k)]['h'] = float(_v['hh'])
import chamfer                                       # cut corners (OSM diagonals / styles 'ch') clipped into the LoD2 shells, 13.11.2026
CHAMFERED = chamfer.apply(RAW, B, LOOK)
def _h01(i, k): x = (i * 2654435761 + k * 40503) & 0xffffffff; x ^= x >> 15; x = (x * 2246822519) & 0xffffffff; x ^= x >> 13; return (x & 0xffffff) / 0xffffff
def look_wall(i):
    """locked wall colour: (hex, 'brick' | 'render'); listed buildings first, otherwise the weighted centre palette"""
    e = LOOK['b'].get(str(i))
    if e and e.get('w'): return e['w'], e.get('k', 'render')      # entries with only a storey count fall through to the palette
    if not LOOK['pal']: return None, None
    t = sum(w for _, w in LOOK['pal']); k = _h01(i, 5) * t
    for hx, w in LOOK['pal']:
        k -= w
        if k <= 0: return hx, 'brick' if hx in ('#a85a42', '#c4683f') else 'render'
    return LOOK['pal'][0][0], 'render'
def look_mat(i):
    hx, kind = look_wall(i)
    if hx is None: return None
    import colorsys                                      # ochre read as mustard: paler, cleaner yellow (same rule as in the game)
    r, g, b = (int(hx[k:k + 2], 16) / 255 for k in (1, 3, 5)); h, l, s_ = colorsys.rgb_to_hls(r, g, b)
    if 0.085 < h < 0.17 and s_ > 0.4:
        r, g, b = colorsys.hls_to_rgb(h + 0.012, min(0.8, l * 1.1 + 0.04), s_ * 0.7); hx = '#%02x%02x%02x' % (int(r * 255), int(g * 255), int(b * 255))
    if kind == 'metal': return MT(hx, None, 0.45, 0.35)   # sheet metal (Ratsula, Kuparikonttori): red walls must not turn into brick (detail_kind)
    return MT(hx, 'brick', 0.8) if kind == 'brick' else M(hx)
_ORTO = None
def roof_mat(i):
    """roof material: locked colour, else classified from the aerial image (red sheet / tile, green, dark felt, light grey)"""
    e = LOOK['b'].get(str(i)) or {}
    if e.get('r'): return M(e['r'], 0.55, 0.2)
    global _ORTO
    try:
        if _ORTO is None:
            from PIL import Image
            src = open('/home/claude/pori/city.js').read(); C = json.loads(src[src.index('{'):src.rindex('}') + 1])
            _ORTO = (Image.open('/home/claude/pori/orto.jpg').convert('RGB'), C['hw'], C['ys'], C['yn'])
        im, hw, ys, yn = _ORTO; W, H = im.size; pts, _ = poly(i); cs = []
        cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
        for p in pts + [(cx, cy)]:
            for f in (0.35, 0.7):
                x = cx + (p[0] - cx) * f; y = cy + (p[1] - cy) * f
                u = int((x + hw) / (2 * hw) * W); v = int((1 - (y - ys) / (yn - ys)) * H)
                if 0 <= u < W and 0 <= v < H: cs.append(im.getpixel((u, v)))
        cs.sort(key=lambda c: sum(c)); r, g, b = cs[len(cs) // 2]
    except Exception:
        return M('#3f4246', 0.6)
    lum = (r + g + b) / 3
    if r > 1.3 * g and r > 90: return M('#b5553a' if g > 0.52 * r else '#b8302a', 0.6)
    if g > 1.12 * r and g > 1.05 * b and lum > 70: return M('#3f9a5a', 0.55, 0.2)
    if lum < 105: return M('#3f4246', 0.6)
    if lum < 165: return M('#74787b', 0.6)
    return M('#b9bbb9', 0.6)

def newell(r):
    n = Vector((0, 0, 0))
    for i in range(len(r)):
        a, b = Vector(r[i]), Vector(r[(i + 1) % len(r)]); n += Vector(((a.y - b.y) * (a.z + b.z), (a.z - b.z) * (a.x + b.x), (a.x - b.x) * (a.y + b.y)))
    return n.normalized() if n.length > 1e-9 else None

def eave_of(i):
    tops = []
    for k, r, _ in RAW[i]:
        if k == 'W': tops.append(max(p[2] for p in r) if min(p[2] for p in r) < 1.5 else None)
    tops = [t for t in tops if t]
    return statistics.median(tops) if tops else B[i]['h']

def build_lod2(Z, i, spec, upper=None):
    P = spec['P']; L = lambda x, y, z: (x - Z.cx, y - Z.cy, z); seed = 0
    from shapely.ops import unary_union
    from shapely.geometry import Point
    RF = []
    for k, r, _ in RAW[i]:
        if k != 'R' or len(r) < 3: continue
        nn = newell(r)
        if nn is None or abs(nn.z) < 0.05: continue
        RF.append((Polygon([(p[0], p[1]) for p in r]).buffer(0), nn, Vector(r[0])))
    def roofz(x, y):
        best = -1e9
        for pg, nn, p0 in RF:
            if pg.contains(Point(x, y)): best = max(best, p0.z - (nn.x * (x - p0.x) + nn.y * (y - p0.y)) / nn.z)
        return best
    FP = unary_union([Polygon([(p[0], p[1]) for p in r]).buffer(0) for k, r, _ in RAW[i] if k == 'G' and len(r) >= 3])
    for k, r, holes in RAW[i]:
        if k == 'G' or len(r) < 3: continue
        if spec.get('skip') and spec['skip'](r, k): continue          # parts replaced by hand-built geometry (BePOP tower)
        spec_ = spec
        if spec.get('alt'):                                    # part of the shell is another building (Lyseo: 1950s wing on the same footprint)
            spec_ = spec['alt'](sum(p[0] for p in r) / len(r), sum(p[1] for p in r) / len(r)) or spec
        P_ = spec_['P']
        if k == 'R':
            rmf = spec_.get('roofmat_fn') and spec_['roofmat_fn'](r)
            if ROOFBAKE or spec_.get('roofmat') or rmf:
                nr = newell(r)
                add_solid(Z, [L(*p) for p in (r if nr is None or nr.z >= 0 else r[::-1])], rmf or spec_.get('roofmat') or roof_mat(i), 0.45)   # face up: a downward roof baked black
            else: Z.hi.append(([L(*p) for p in r], ROOFOCC))
            continue
        n = newell(r)
        if n is None or abs(n.z) > 0.3: continue
        mx = sum(p[0] for p in r) / len(r); my = sum(p[1] for p in r) / len(r); nh = Vector((n.x, n.y)).normalized()
        mz = sum(p[2] for p in r) / len(r)
        fa, fb = FP.contains(Point(mx + nh.x * 0.6, my + nh.y * 0.6)), FP.contains(Point(mx - nh.x * 0.6, my - nh.y * 0.6))
        if fa and fb:                                                            # upper wall: the inner side is under a higher roof
            fa = roofz(mx + nh.x * 0.6, my + nh.y * 0.6) > mz; fb = roofz(mx - nh.x * 0.6, my - nh.y * 0.6) > mz
            if fa and fb: continue                                               # internal wall between two parts of the model
        elif not fa and not fb:                                                  # footprint test undecided: the side with a roof over it is inside
            ra = roofz(mx + nh.x * 0.8, my + nh.y * 0.8) > -1e8; rb = roofz(mx - nh.x * 0.8, my - nh.y * 0.8) > -1e8
            if ra and not rb: fa = True
        if fa and not fb:
            n = -n; r = r[::-1]                                                  # wall stored facing inwards
        t = Vector((-n.y, n.x)).normalized(); o = Vector((r[0][0], r[0][1]))
        uz = [((Vector((p[0], p[1])) - o).dot(t), p[2]) for p in r]
        try: pg = Polygon(uz).buffer(0)
        except Exception: continue
        if pg.area < 0.3: continue
        u0, zb, u1, zt = pg.bounds
        # eave per run: where the top edge steps (a taller part, a notch), each stretch gets its own facade up to its own eave
        # (one eave for the whole wall left everything above the lowest point blank)
        ns = max(2, int((u1 - u0) / 1.0) + 1); xs = [u0 + (u1 - u0) * (0.5 + k) / ns for k in range(ns)]; tops = []
        for x in xs:
            seg = pg.intersection(box(x - 0.01, zb - 1, x + 0.01, zt + 1))
            tops.append(seg.bounds[3] if not seg.is_empty else zb)
        runs = []; k0 = 0
        for k in range(1, ns + 1):
            if k == ns or max(tops[k0:k + 1]) - min(tops[k0:k + 1]) > 1.0:
                runs.append((u0 if k0 == 0 else u0 + (u1 - u0) * k0 / ns, u1 if k == ns else u0 + (u1 - u0) * k / ns, min(tops[k0:k]))); k0 = k
        merged = []
        for r_ in runs:                                        # slivers join their neighbour
            if merged and (r_[1] - r_[0] < 2.6 or merged[-1][1] - merged[-1][0] < 2.6): merged[-1] = (merged[-1][0], r_[1], min(merged[-1][2], r_[2]))
            else: merged.append(r_)
        runs = merged; seed += 1; boxes = []
        if spec.get('splitruns') and spec.get('runalt'):             # one LoD2 shell over two houses: cut the runs where runalt changes
            ra_ = spec['runalt']; rs2 = []
            for a_, b_, ze_ in runs:
                m_ = max(1, int((b_ - a_) / 0.5)); s0 = a_; prev = None
                for k in range(m_ + 1):
                    u_ = a_ + (b_ - a_) * k / m_; lab = id(ra_(o.x + t.x * u_, o.y + t.y * u_))
                    if prev is not None and lab != prev and u_ - s0 > 1.0 and b_ - u_ > 1.0: rs2.append((s0, u_, ze_)); s0 = u_
                    prev = lab
                rs2.append((s0, b_, ze_))
            runs = rs2
        W3 = lambda u, z: L(o.x + t.x * u, o.y + t.y * u, z)
        zcap = spec.get('zcap')
        if zcap:                                                # open space under a canopy: walls end lower, loose fragments go
            runs2 = []
            for u0r, u1r, ze in runs:
                um = (u0r + u1r) / 2; cap = zcap(o.x + t.x * um, o.y + t.y * um)
                if cap is None: runs2.append((u0r, u1r, ze)); continue
                if zb < cap: runs2.append((u0r, u1r, min(ze, cap)))
                elif zb > 23.0: runs2.append((u0r, u1r, ze))
            if not runs2: continue
            capped = runs2 != runs; runs = runs2
        else: capped = False
        for u0r, u1r, ze in runs:
            if not (ze - zb > 1.2 and u1r - u0r > 0.4): continue
            seed += 1
            p = (o.x + t.x * u0r, o.y + t.y * u0r); q = (o.x + t.x * u1r, o.y + t.y * u1r)
            mid2 = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2); street = STREET is None or STREET(mid2, (n.x, n.y))
            ra = spec.get('runalt') and spec['runalt'](*mid2); s_ = ra or spec_; Pr = ra['P'] if ra else P_      # one stretch of a wall as another building part
            lay_ = (s_['layout'] if street or 'yard' not in s_ else s_['yard']) if zb < 1.5 else (s_.get('upper') or upper or lay(ze - zb, 'punched', bw=3.3, fh=3.0))
            if s_.get('fit'): lay_ = s_['fit'](lay_, ze - zb, street)
            if s_.get('fitw'): lay_ = s_['fitw'](lay_, ze - zb, street, u1r - u0r, zb)   # also by wall length and base height (gable ends, walls above a lower roof)
            build_wall(Z, p, q, zb, ze, lay_, s_.get('Pyard', Pr) if not street else Pr, i * 31 + seed, i)
            if spec_.get('cornice') and zb < 1.5 and (street or spec_.get('cornice_all')):
                cw, ch, cm = spec_['cornice']; nn = Vector((n.x, n.y)).normalized()
                for (dd, z0_, z1_) in ((cw * 0.45, ze - ch, ze - ch * 0.55), (cw, ze - ch * 0.55, ze)):
                    a = (p[0] - t.x * dd, p[1] - t.y * dd); b = (q[0] + t.x * dd, q[1] + t.y * dd)
                    a2 = (a[0] + nn.x * dd, a[1] + nn.y * dd); b2 = (b[0] + nn.x * dd, b[1] + nn.y * dd)
                    add_solid(Z, [L(a2[0], a2[1], z0_), L(b2[0], b2[1], z0_), L(b2[0], b2[1], z1_), L(a2[0], a2[1], z1_)], cm, 0.5)
                    add_solid(Z, [L(a[0], a[1], z0_), L(b[0], b[1], z0_), L(b2[0], b2[1], z0_), L(a2[0], a2[1], z0_)][::-1], cm, 0.3)
                    add_solid(Z, [L(a[0], a[1], z1_), L(b[0], b[1], z1_), L(b2[0], b2[1], z1_), L(a2[0], a2[1], z1_)], cm, 0.3)
                    for e0, e1 in ((a, a2), (b2, b)):
                        add_solid(Z, [L(e0[0], e0[1], z0_), L(e1[0], e1[1], z0_), L(e1[0], e1[1], z1_), L(e0[0], e0[1], z1_)], cm, 0.2)
            boxes.append(box(u0r - 0.01, zb - 0.01, u1r + 0.01, ze))
        rest = pg.difference(unary_union(boxes)) if boxes else pg
        ze = min(r_[2] for r_ in runs)
        for part in getattr(rest, 'geoms', [rest]):
            if part.is_empty or part.area < 0.05 or part.geom_type != 'Polygon': continue
            if zcap:
                pc = part.centroid; cap = zcap(o.x + t.x * pc.x, o.y + t.y * pc.y)
                if cap is not None and part.bounds[1] < 23.0: continue
            ring = list(part.exterior.coords)[:-1]
            if len(ring) < 3: continue
            pts3 = [W3(u, z) for u, z in ring]
            if newell(pts3) is not None and newell(pts3).dot(Vector((n.x, n.y, 0))) < 0: pts3.reverse()
            top_ = min(z for u, z in ring) >= ze - 0.2; hi_ = top_ and spec_.get('upper_mat')
            add_solid(Z, pts3, spec_['upper_mat'] if hi_ else P_['wall'], 0.5)
            if top_ and spec_.get('attic'):                             # 1.5-storey house: a window in each gable that has room for one
                pu0, pz0, pu1, pz1 = part.bounds; cu = max(ring, key=lambda q_: q_[1])[0]
                if pz1 - pz0 > 2.0 and part.contains(box(cu - 0.6, pz0 + 0.25, cu + 0.6, pz0 + 1.65)):
                    gable_window(Z, lambda u, z_, d, cu=cu, pz0=pz0: L(o.x + t.x * (cu + u) + n.x * d, o.y + t.y * (cu + u) + n.y * d, pz0 + z_), P_)

HIDE = set(json.loads(open('/home/claude/pori/lod2.js').read()[len('export default '):-2])['hide']) if True else set()
def context2(Z, margin=70):
    """neighbours as plain boxes for shadows, skipping OSM parts that sit inside the zone's LoD2 shells"""
    from shapely.ops import unary_union
    from shapely.geometry import Point
    shells = unary_union([Polygon([(p[0], p[1]) for p in r]).buffer(0.3) for i in Z.ids for k, r, _ in RAW.get(i, []) if k == 'G' and len(r) >= 3])
    x0, y0, x1, y1 = Z.bbox; ids = set(Z.ids)
    for i in range(len(B)):
        if i in ids or i in HIDE: continue
        pts, a = poly(i); c = cen(pts)
        if not (x0 - margin < c[0] < x1 + margin and y0 - margin < c[1] < y1 + margin): continue
        if shells.contains(Point(c)): continue
        try:                                                 # an OSM outline that overlaps a shell of this zone is the same building under another index:
            pg_ = Polygon(pts).buffer(0)                     # as a shadow box it buried the facade and the bake came out black
            if pg_.area > 0 and pg_.intersection(shells).area > 0.2 * pg_.area: continue
        except Exception: pass
        h = B[i]['h']; n = len(pts)
        for k in range(n):
            p, q = pts[k], pts[(k + 1) % n]
            Z.hi.append(([(p[0] - Z.cx, p[1] - Z.cy, 0), (q[0] - Z.cx, q[1] - Z.cy, 0), (q[0] - Z.cx, q[1] - Z.cy, h), (p[0] - Z.cx, p[1] - Z.cy, h)], M('#b5b0a6')))
        Z.hi.append(([(x - Z.cx, y - Z.cy, h) for x, y in pts], M('#55585c')))
    s = 400
    Z.hi.append(([(-s, -s, -0.02), (s, -s, -0.02), (s, s, -0.02), (-s, s, -0.02)], M((0.22, 0.22, 0.22))))

# Pori render colours of the 1920-60s stone centre: buff, ochre, sand, pale grey-green, salmon, light grey
PALP = ['#d9c9a3', '#cdb487', '#e2d6bb', '#c9cbbd', '#d8b9a0', '#cfcac0', '#e6dfcc', '#bfc4b8', '#d6c08e', '#c7b8a6', '#e0cfb0', '#b9b2a4']
def _bal(sp, i):
    """styles.json b[i].bal = 'proj': projecting balconies from the street photos (the default in gen.py is recessed and glazed)"""
    if (LOOK['b'].get(str(i)) or {}).get('bal') == 'proj': sp = dict(sp, P=dict(sp['P'], proj_balcony=True))
    return sp
def spec_for(i):
    sp = SPEC.get(i)
    if sp: return _bal(sp, i)
    sp = auto(i); sp['P'] = dict(sp['P']); sp['P']['wall'] = look_mat(i) or M(PALP[(i * 7 + 3) % len(PALP)])
    f = (LOOK['b'].get(str(i)) or {}).get('f')                 # storeys from the building register (Ryhti): one window row per storey
    L_ = sp.get('layout')
    if L_ and L_.get('rows') and not (LOOK['b'].get(str(i)) or {}).get('shop'):   # shop fronts only on the commercial streets of the centre
        sp['layout'] = L_ = dict(L_, rows=[(r[0], 'punched', 'F') if r[2] == 'G' and r[1] == 'shop' else r for r in L_['rows']])
    if f and L_ and not L_.get('plain') and L_.get('rows'):
        rows = L_['rows']; g = [r for r in rows if r[2] == 'G']; up = [r for r in rows if r[2] != 'G']
        n = max(1, int(f) - len(g)); gh_ = sum(r[0] for r in g); H = float(B[i]['h'])
        fh = (H - gh_) / n                                   # the rows are stretched to the wall: give them the real storey height,
        if 2.6 <= fh <= 4.6:                                 # or the ground-floor shop row grows with them (7-8 m shop fronts)
            body = [up[0]] if up and up[0][2] == 'S' else []; top = [up[-1]] if up and up[-1][2] == 'T' else []
            mid = [r for r in up if r[2] == 'F'][:1] or [(fh, 'punched', 'F')]
            new = body + mid * max(0, n - len(body) - len(top)) + top
            new = [(fh,) + tuple(r[1:]) for r in (new[:n] if len(new) > n else new)]
            sp['layout'] = dict(L_, rows=g + new)
        # else: the register count does not fit this height (wrong building matched) - keep the height-based rows
    return _bal(sp, i)
