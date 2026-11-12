"""Cars for the traffic and the parked cars -> cars.js: car0 hatchback, car1 estate, car2 hatchback again (the game's third
passenger-car slot), car3 panel van.
Every car is a lofted body (cross-sections along its length: sill, flank, shoulder, glass, roof) with wheel-arch liners, round wheels with
rims, lamps, grille, number plates, mirrors, pillars and door seams.  Vertex colours carry the look; their alpha says what the game may
paint: 1 = bodywork (multiplied by the instance colour), 0 = glass, tyres, lamps, trim (kept as they are).
  python3 cars.py [out.glb] [cars.js]"""
import bpy, bmesh, math, base64, os, sys
BASE = 0.8                                                        # bodywork below white: the game's sky light is strong and washed the paint out
PAINT = (BASE, BASE, BASE, 1)
def sh(f): return (f * BASE, f * BASE, f * BASE, 1)                                   # bodywork a shade darker (sills, undersides of the bumpers)
def fx(r, g, b): return (r, g, b, 0)                             # fixed colour, never painted
GL_LO = fx(0.035, 0.05, 0.065); GL_HI = fx(0.16, 0.21, 0.26)     # glass: dark at the sill, sky in the upper edge
TYRE = fx(0.022, 0.022, 0.024); RIM = fx(0.62, 0.64, 0.66); HUB = fx(0.30, 0.31, 0.33); LINER = fx(0.012, 0.012, 0.014)
HEAD = fx(0.92, 0.93, 0.90); DRL = fx(1.0, 0.98, 0.9); TAIL = fx(0.62, 0.03, 0.03); AMBER = fx(0.85, 0.42, 0.05)
TRIM = fx(0.045, 0.047, 0.05); GRILLE = fx(0.02, 0.02, 0.022); PLATE = fx(0.93, 0.93, 0.9); SEAM = fx(0.03, 0.03, 0.035); CHROME = fx(0.55, 0.57, 0.6)
EPS = 0.014                                                       # overlays sit this far off the body (no z-fighting from the helicopter)

class Car:
    def __init__(s, name): s.name = name; s.F = []
    def face(s, pts, col, ref=None): s.F.append((list(pts), col if isinstance(col, list) else [col] * len(pts), ref))
    def both(s, pts, col, ref=None):
        """a polygon on the left side (x > 0) and its mirror image; build() turns every face outwards (away from ref, or from the car's middle)"""
        s.face(pts, col, ref); s.face([(-x, y, z) for x, y, z in pts], col, ref and (-ref[0], ref[1], ref[2]))

    def loft(s, st, zb, side, top):
        """st: stations nose -> tail, each (y, w, zbelt, wt, ztop, crown).  Profile per station (left half, bottom -> roof centre):
        0 under edge, 1 sill, 2 widest flank, 3 shoulder (window sill), 4 upper edge (roof edge / bonnet edge), 5 roof shoulder, 6 centre.
        side[i] / top[i]: colour of the strip 3-4 / of the strips 4-5-6 between station i and i + 1 ('G' = glass)."""
        s.st = st; s.zb = zb; P = []
        for y, w, zbelt, wt, ztop, crown in st:
            zm = zb + (zbelt - zb) * 0.45
            P.append([(w * 0.90, y, zb), (w * 0.985, y, zb + 0.11), (w, y, zm), (w * 0.975, y, zbelt), (wt, y, ztop), (wt * 0.55, y, ztop + crown * 0.8), (0.0, y, ztop + crown)])
        s.P = P; SH = [0.5, 0.86, 1.0, 1.0, 1.0, 1.0, 1.0]
        for i in range(len(P) - 1):
            a, b = P[i], P[i + 1]
            for k in range(6):
                q = [a[k], b[k], b[k + 1], a[k + 1]]              # counter-clockwise from outside on the left flank (nose towards +y)
                if k == 3 and side[i] == 'G': col = [GL_LO, GL_LO, GL_HI, GL_HI]
                elif k >= 4 and top[i] == 'G': col = [GL_LO, GL_LO, GL_HI, GL_HI] if a[4][2] < b[4][2] else [GL_HI, GL_HI, GL_LO, GL_LO]
                else:
                    c0 = side[i] if k == 3 else top[i] if k >= 4 else None
                    col = [c0] * 4 if isinstance(c0, tuple) else [sh(SH[k]), sh(SH[k]), sh(SH[k + 1]), sh(SH[k + 1])]
                s.both(q[::-1], col[::-1])
        for P_, flip in ((P[0], False), (P[-1], True)):           # nose and tail faces
            ring = P_ + [(-x, y, z) for x, y, z in P_[-2::-1]]
            s.face(ring if not flip else ring[::-1], [sh(0.5 if abs(z - zb) < 1e-6 else 0.93) for x, y, z in (ring if not flip else ring[::-1])])
        y0, y1 = st[0][0], st[-1][0]; w = max(t[1] for t in st) * 0.9
        s.face([(-w, y0 - 0.1, zb), (-w, y1 + 0.1, zb), (w, y1 + 0.1, zb), (w, y0 - 0.1, zb)], LINER)          # floor pan

    def at(s, y):
        """interpolated station at y -> (w, zbelt, wt, ztop, crown)"""
        st = s.st
        for i in range(len(st) - 1):
            if st[i][0] >= y >= st[i + 1][0]:
                f = (st[i][0] - y) / (st[i][0] - st[i + 1][0] or 1); return tuple(st[i][k] + (st[i + 1][k] - st[i][k]) * f for k in range(1, 6))
        return st[0][1:] if y > st[0][0] else st[-1][1:]

    def wheel(s, y, r, tw=0.21, rim=0.62, n=12):
        """arch liner on the flank, tyre, alloy rim with a dark hub"""
        w = s.at(y)[0]; zb = s.zb; xo = w + 0.02; xi = xo - tw; ra = r + 0.07
        arch = [(w + 0.006, y + ra * math.cos(a), max(zb, r + ra * math.sin(a))) for a in [math.pi * k / 10 for k in range(11)]]
        s.both(arch, LINER); ctr = ((xo + xi) / 2, y, r)
        ring = [(math.cos(2 * math.pi * k / n), math.sin(2 * math.pi * k / n)) for k in range(n)]
        for k in range(n):
            (c0, s0), (c1, s1) = ring[k], ring[(k + 1) % n]
            s.both([(xo, y + r * c0, r + r * s0), (xi, y + r * c0, r + r * s0), (xi, y + r * c1, r + r * s1), (xo, y + r * c1, r + r * s1)], TYRE, ctr)
            s.both([(xo, y + r * c0, r + r * s0), (xo, y + r * c1, r + r * s1), (xo + 0.004, y + r * rim * c1, r + r * rim * s1), (xo + 0.004, y + r * rim * c0, r + r * rim * s0)], TYRE, ctr)
        rr = r * rim
        for k in range(n):                                        # alloy: light spokes, dark gaps between them
            (c0, s0), (c1, s1) = ring[k], ring[(k + 1) % n]
            s.both([(xo - 0.012, y, r), (xo - 0.012, y + rr * c0, r + rr * s0), (xo - 0.012, y + rr * c1, r + rr * s1)], RIM if k % 2 == 0 else HUB, ctr)
        s.both([(xo - 0.004, y + rr * 0.24 * c, r + rr * 0.24 * s_) for c, s_ in ring[::2]], RIM, ctr)

    def flank_x(s, y, z):
        w, zbelt, wt, ztop, _ = s.at(y); zm = s.zb + (zbelt - s.zb) * 0.45
        if z <= zm: return w * 0.985 + (w - w * 0.985) * min(1, max(0, (z - s.zb - 0.11) / max(1e-6, zm - s.zb - 0.11)))
        if z <= zbelt: return w + (w * 0.975 - w) * (z - zm) / (zbelt - zm)
        return w * 0.975 + (wt - w * 0.975) * min(1, (z - zbelt) / max(1e-6, ztop - zbelt))
    def side_rect(s, y0, y1, z0, z1, col, off=EPS):
        """overlay on the flank between y0 > y1, following the body: split where the flank bends (widest line, shoulder) and at the stations"""
        ym = (y0 + y1) / 2; _, zbelt, _, _, _ = s.at(ym); zm = s.zb + (zbelt - s.zb) * 0.45
        zs = [z0] + [z for z in (zm, zbelt) if z0 + 1e-3 < z < z1 - 1e-3] + [z1]; ys = [y0] + [t[0] for t in s.st if y1 + 1e-3 < t[0] < y0 - 1e-3] + [y1]
        for za, zb_ in zip(zs, zs[1:]):
            for ya, yb in zip(ys, ys[1:]):
                s.both([(s.flank_x(y, z) + off, y, z) for y, z in ((ya, za), (yb, za), (yb, zb_), (ya, zb_))], col)

    def pillar(s, ya, za, yb, zb_, wid, col=PAINT):
        """strip along the glass edge from (ya, za) at the shoulder to (yb, zb_) at the roof edge (A-, C- and D-pillars)"""
        def X(y, z):
            w, zbelt, wt, ztop, _ = s.at(y); return w * 0.975 + (wt - w * 0.975) * min(1, max(0, (z - zbelt) / max(1e-6, ztop - zbelt))) + EPS
        s.both([(X(ya + wid, za), ya + wid, za), (X(ya, za), ya, za), (X(yb, zb_), yb, zb_), (X(yb + wid, zb_), yb + wid, zb_)], col)

    def end_rect(s, front, x0, x1, z0, z1, col, off=EPS, sl=0.0):
        """overlay on the nose (front) or tail face, on both halves; sl leans the top edge back"""
        y = s.st[0][0] + off if front else s.st[-1][0] - off; d = -sl if front else sl
        pts = [(x1, y, z0), (x0, y, z0), (x0, y + d, z1), (x1, y + d, z1)]
        s.both(pts if front else pts[::-1], col)

    def box(s, x0, x1, y0, y1, z0, z1, col):
        v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)): s.both([v[k] for k in f], col, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))

    def build(s):
        bm = bmesh.new(); cl = bm.loops.layers.float_color.new('Col'); vs = {}
        def V(p):
            k = (round(p[0], 4), round(p[1], 4), round(p[2], 4))
            if k not in vs: vs[k] = bm.verts.new(p)
            return vs[k]
        hw = max(t[1] for t in s.st); hl = max(abs(s.st[0][0]), abs(s.st[-1][0])); zc = (s.zb + max(t[4] for t in s.st)) / 2
        for pts, cols, ref in s.F:
            n = [0, 0, 0]; m = len(pts); c = [sum(p[k] for p in pts) / m for k in range(3)]
            for i in range(m):
                a, b = pts[i], pts[(i + 1) % m]; n[0] += (a[1] - b[1]) * (a[2] + b[2]); n[1] += (a[2] - b[2]) * (a[0] + b[0]); n[2] += (a[0] - b[0]) * (a[1] + b[1])
            d = [c[k] - ref[k] for k in range(3)] if ref else [(c[0] / hw) ** 3, (c[1] / hl) ** 3, ((c[2] - zc) / (zc - s.zb)) ** 3 if abs(c[2] - zc) > 0.02 else 0]
            if sum(n[k] * d[k] for k in range(3)) < 0: pts = pts[::-1]; cols = cols[::-1]
            vv = []; cc = []
            for p, c in zip(pts, cols):
                v = V(p)
                if v not in vv: vv.append(v); cc.append(c)
            if len(vv) < 3: continue
            try: f = bm.faces.new(vv)
            except ValueError: continue                             # the same face twice
            for lp, c in zip(f.loops, cc): lp[cl] = c
            f.smooth = True
        me = bpy.data.meshes.new(s.name); bm.to_mesh(me); bm.free()
        me.color_attributes.active_color = me.color_attributes['Col']
        try: me.set_sharp_from_angle(angle=math.radians(38))
        except Exception: pass
        ob = bpy.data.objects.new(s.name, me); bpy.context.scene.collection.objects.link(ob); return ob

def hatchback(name='car0'):
    c = Car(name); zb = 0.21
    st = [(2.13, 0.72, 0.60, 0.62, 0.66, 0.02), (2.04, 0.84, 0.66, 0.72, 0.72, 0.03), (1.55, 0.89, 0.78, 0.78, 0.84, 0.05), (0.92, 0.895, 0.90, 0.80, 0.96, 0.05),
          (0.18, 0.895, 0.92, 0.70, 1.41, 0.045), (-0.55, 0.895, 0.93, 0.70, 1.43, 0.045), (-1.20, 0.895, 0.94, 0.69, 1.41, 0.04), (-1.66, 0.89, 0.95, 0.66, 1.34, 0.03),
          (-2.05, 0.86, 0.95, 0.76, 1.00, 0.02), (-2.14, 0.80, 0.93, 0.72, 0.96, 0.015)]
    c.loft(st, zb, side=[None, None, None, 'G', 'G', 'G', None, None, None], top=[None, None, None, 'G', None, None, None, 'G', None])
    c.pillar(0.92, 0.90, 0.18, 1.41, 0.075); c.pillar(-1.20, 0.94, -1.20, 1.41, -0.07)                    # A-pillar, edge of the C-pillar
    c.side_rect(-0.44, -0.52, 0.93, 1.42, TRIM)                                                         # B-pillar
    for y in (0.60, -0.48, -1.38): c.side_rect(y, y - 0.014, zb + 0.13, 0.93, SEAM, off=0.006)          # door seams
    c.side_rect(0.36, 0.22, 0.80, 0.83, TRIM); c.side_rect(-0.72, -0.86, 0.81, 0.84, TRIM)              # door handles
    c.side_rect(2.02, -2.03, zb + 0.0, zb + 0.1, TRIM, off=0.008)                                       # sill strip
    c.wheel(1.34, 0.315); c.wheel(-1.29, 0.315)
    c.box(0.90, 1.07, 0.70, 0.84, 0.93, 1.04, PAINT); c.side_rect(0.84, 0.70, 0.95, 1.02, GL_LO, off=0.18)   # mirrors
    c.end_rect(True, 0.40, 0.71, 0.47, 0.63, HEAD, sl=0.02); c.end_rect(True, 0.42, 0.69, 0.595, 0.62, DRL, off=0.02, sl=0.02)
    c.end_rect(True, 0.0, 0.40, 0.52, 0.60, GRILLE); c.end_rect(True, 0.0, 0.56, 0.26, 0.40, GRILLE); c.end_rect(True, 0.0, 0.26, 0.41, 0.515, PLATE, off=0.02)
    c.side_rect(2.10, 1.86, 0.56, 0.66, HEAD, off=0.012)                                                  # lamp wrapping round the corner
    c.end_rect(False, 0.42, 0.78, 0.70, 0.90, TAIL); c.side_rect(-1.98, -2.12, 0.72, 0.90, TAIL, off=0.012)
    c.end_rect(False, 0.0, 0.27, 0.56, 0.67, PLATE); c.end_rect(False, 0.0, 0.62, 0.24, 0.36, TRIM); c.end_rect(False, 0.0, 0.14, 0.98, 1.0, TAIL, off=0.02)
    return c.build()

def estate():
    c = Car('car1'); zb = 0.20
    st = [(2.36, 0.74, 0.60, 0.64, 0.66, 0.02), (2.26, 0.86, 0.66, 0.74, 0.72, 0.03), (1.72, 0.91, 0.78, 0.80, 0.84, 0.05), (1.02, 0.915, 0.89, 0.82, 0.95, 0.05),
          (0.24, 0.915, 0.91, 0.71, 1.40, 0.045), (-0.60, 0.915, 0.92, 0.71, 1.43, 0.045), (-1.50, 0.915, 0.93, 0.70, 1.42, 0.04), (-2.02, 0.91, 0.94, 0.68, 1.38, 0.03),
          (-2.28, 0.88, 0.94, 0.78, 0.98, 0.02), (-2.36, 0.82, 0.92, 0.74, 0.94, 0.015)]
    c.loft(st, zb, side=[None, None, None, 'G', 'G', 'G', 'G', None, None], top=[None, None, None, 'G', None, None, None, 'G', None])
    c.pillar(1.02, 0.89, 0.24, 1.40, 0.075); c.pillar(-2.02, 0.94, -2.02, 1.38, 0.10)                     # A- and D-pillar
    c.side_rect(-0.40, -0.48, 0.92, 1.42, TRIM); c.side_rect(-1.42, -1.50, 0.93, 1.41, TRIM)              # B- and C-pillar
    for y in (0.70, -0.44, -1.52): c.side_rect(y, y - 0.014, zb + 0.13, 0.92, SEAM, off=0.006)
    c.side_rect(0.44, 0.30, 0.80, 0.83, TRIM); c.side_rect(-0.70, -0.84, 0.81, 0.84, TRIM)
    c.side_rect(2.24, -2.26, zb + 0.0, zb + 0.1, TRIM, off=0.008)
    c.wheel(1.48, 0.325); c.wheel(-1.38, 0.325)
    c.box(0.92, 1.09, 0.80, 0.94, 0.92, 1.03, PAINT); c.side_rect(0.94, 0.80, 0.94, 1.01, GL_LO, off=0.18)
    for y0, y1 in ((0.05, -1.95),): c.box(0.60, 0.64, y1, y0, 1.455, 1.49, CHROME)                        # roof rails
    c.end_rect(True, 0.40, 0.73, 0.47, 0.63, HEAD, sl=0.02); c.end_rect(True, 0.42, 0.71, 0.595, 0.62, DRL, off=0.02, sl=0.02)
    c.end_rect(True, 0.0, 0.40, 0.50, 0.61, GRILLE); c.end_rect(True, 0.0, 0.58, 0.25, 0.39, GRILLE); c.end_rect(True, 0.0, 0.26, 0.40, 0.495, PLATE, off=0.02)
    c.side_rect(2.33, 2.08, 0.56, 0.66, HEAD, off=0.012)
    c.end_rect(False, 0.34, 0.80, 0.72, 0.90, TAIL); c.side_rect(-2.20, -2.34, 0.72, 0.90, TAIL, off=0.012)
    c.end_rect(False, 0.0, 0.27, 0.54, 0.65, PLATE); c.end_rect(False, 0.0, 0.64, 0.23, 0.35, TRIM)
    return c.build()

def van():
    c = Car('car3'); zb = 0.26
    st = [(2.48, 0.80, 0.72, 0.72, 0.80, 0.02), (2.38, 0.93, 0.84, 0.84, 0.92, 0.03), (1.86, 0.97, 1.02, 0.88, 1.10, 0.04),
          (1.22, 0.975, 1.06, 0.86, 1.88, 0.05), (0.42, 0.975, 1.07, 0.86, 1.92, 0.05), (-1.20, 0.975, 1.07, 0.86, 1.92, 0.05), (-2.40, 0.975, 1.07, 0.86, 1.90, 0.04), (-2.48, 0.95, 1.07, 0.84, 1.86, 0.03)]
    c.loft(st, zb, side=[None, None, 'G', 'G', None, None, None], top=[None, None, 'G', None, None, None, None])
    c.pillar(1.86, 1.02, 1.22, 1.88, 0.09); c.side_rect(0.46, 0.38, 1.07, 1.90, PAINT)
    for y in (1.30, 0.40, -0.75): c.side_rect(y, y - 0.016, zb + 0.14, 1.86, SEAM, off=0.006)             # cab door, sliding door
    c.side_rect(0.40, -0.75, 1.03, 1.05, SEAM, off=0.006)                                                # sliding-door rail
    c.side_rect(1.0, 0.86, 0.94, 0.97, TRIM); c.side_rect(0.30, 0.16, 0.94, 0.97, TRIM)
    c.side_rect(2.36, -2.42, zb, zb + 0.16, TRIM, off=0.008)                                             # unpainted sill and bumper band
    c.wheel(1.52, 0.345, tw=0.23); c.wheel(-1.45, 0.345, tw=0.23)
    c.box(0.98, 1.20, 1.24, 1.36, 1.10, 1.36, TRIM); c.side_rect(1.36, 1.24, 1.12, 1.34, GL_LO, off=0.235)
    c.end_rect(True, 0.50, 0.78, 0.60, 0.76, HEAD, sl=0.02); c.end_rect(True, 0.0, 0.50, 0.60, 0.74, GRILLE); c.end_rect(True, 0.0, 0.78, zb, 0.52, TRIM)
    c.end_rect(True, 0.0, 0.26, 0.40, 0.50, PLATE, off=0.02); c.side_rect(2.46, 2.26, 0.66, 0.80, HEAD, off=0.012)
    c.end_rect(False, 0.80, 0.94, 0.95, 1.50, TAIL); c.end_rect(False, 0.0, 0.92, zb, 0.50, TRIM)
    c.end_rect(False, 0.06, 0.76, 1.12, 1.70, [GL_LO, GL_LO, GL_HI, GL_HI]); c.end_rect(False, 0.0, 0.012, 0.50, 1.84, SEAM, off=0.008)
    c.end_rect(False, 0.0, 0.27, 0.62, 0.73, PLATE, off=0.02)
    return c.build()

if __name__ == '__main__':
    bpy.ops.wm.read_factory_settings(use_empty=True)
    obs = [hatchback(), estate(), van()]
    o2 = bpy.data.objects.new('car2', obs[0].data); bpy.context.scene.collection.objects.link(o2)      # same mesh, second node
    for o in obs: print(o.name, 'verts', len(o.data.vertices), 'tris', sum(len(p.vertices) - 2 for p in o.data.polygons))
    out = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/out/cars.glb'; js = sys.argv[2] if len(sys.argv) > 2 else '/home/claude/pori/cars.js'
    bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_yup=True, export_vertex_color='ACTIVE', export_active_vertex_color_when_no_material=True, export_normals=True)
    open(js, 'w').write('export default "%s";\n' % base64.b64encode(open(out, 'rb').read()).decode())
    print('cars.glb', os.path.getsize(out))
