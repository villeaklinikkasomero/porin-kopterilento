"""Low-poly cars (saloon, estate/SUV, van) -> cars.js.  Body is white so the game can tint every instance; glass, wheels and lamps are dark / coloured vertex colours."""
import bpy, math, base64, os
BODY = (1, 1, 1); LOW = (0.74, 0.74, 0.74); GLASS = (0.06, 0.08, 0.10); TYRE = (0.02, 0.02, 0.02); HEAD = (1.0, 0.95, 0.75); TAIL = (0.55, 0.03, 0.03); TRIM = (0.05, 0.05, 0.06)
def car(name, body, cab, wheels_y, zb=0.3):
    F = []                                   # (pts, colour or per-vertex colours)
    def q(a, b, c, d, col): F.append(([a, b, c, d], col))
    n = len(body)
    for i in range(n - 1):
        (y0, w0, t0), (y1, w1, t1) = body[i], body[i + 1]
        for s in (1, -1):
            pts = [(s * w0, y0, zb), (s * w1, y1, zb), (s * w1, y1, t1), (s * w0, y0, t0)]
            F.append((pts if s < 0 else pts[::-1], [LOW, LOW, BODY, BODY] if s < 0 else [BODY, BODY, LOW, LOW]))
        q((-w0, y0, t0), (-w1, y1, t1), (w1, y1, t1), (w0, y0, t0), BODY)
    y, w, t = body[0]; q((w, y, zb), (-w, y, zb), (-w, y, t), (w, y, t), LOW)                     # nose
    for s in (1, -1): q((s * w * 0.95, y + 0.01, t - 0.2), (s * w * 0.45, y + 0.01, t - 0.2), (s * w * 0.45, y + 0.01, t - 0.04), (s * w * 0.95, y + 0.01, t - 0.04), HEAD)
    y, w, t = body[-1]; q((-w, y, zb), (w, y, zb), (w, y, t), (-w, y, t), LOW)                   # tail
    for s in (1, -1): q((s * w * 0.95, y - 0.01, t - 0.22), (s * w * 0.5, y - 0.01, t - 0.22), (s * w * 0.5, y - 0.01, t - 0.04), (s * w * 0.95, y - 0.01, t - 0.04), TAIL)
    (bf, wf, zf), (rf, wr, zr), (rr, _, _), (br, wb, zbk) = cab                                   # base front, roof front, roof rear, base rear
    q((wf, bf, zf), (-wf, bf, zf), (-wr, rf, zr), (wr, rf, zr), GLASS)                            # windscreen
    q((wr, rf, zr), (-wr, rf, zr), (-wr, rr, zr), (wr, rr, zr), BODY)                             # roof
    q((wr, rr, zr), (-wr, rr, zr), (-wb, br, zbk), (wb, br, zbk), GLASS)                          # rear window
    for s in (1, -1):
        pts = [(s * wf, bf, zf), (s * wr, rf, zr), (s * wr, rr, zr), (s * wb, br, zbk)]
        F.append((pts if s > 0 else pts[::-1], GLASS))
    wmax = max(b[1] for b in body)
    for wy in wheels_y:                                                                          # wheels: dark hexagons on the flanks
        for s in (1, -1):
            pts = [(s * (wmax + 0.012), wy + 0.33 * math.cos(a * math.pi / 3), 0.33 + 0.33 * math.sin(a * math.pi / 3)) for a in range(6)]
            F.append((pts if s > 0 else pts[::-1], TYRE))
    q((-wmax * 0.9, body[0][0] - 0.2, 0.16), (wmax * 0.9, body[0][0] - 0.2, 0.16), (wmax * 0.9, body[-1][0] + 0.2, 0.16), (-wmax * 0.9, body[-1][0] + 0.2, 0.16), TRIM)   # floor pan
    verts = []; faces = []; cols = []
    for pts, col in F:
        b = len(verts); verts += pts; faces.append(list(range(b, b + len(pts)))); cols += (col if isinstance(col, list) else [col] * len(pts))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    ca = me.color_attributes.new('Col', 'FLOAT_COLOR', 'CORNER')
    for i, c in enumerate(cols): ca.data[i].color = (c[0], c[1], c[2], 1)
    me.color_attributes.active_color = ca
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob); return ob
bpy.ops.wm.read_factory_settings(use_empty=True)
car('car0', [(2.2, 0.66, 0.60), (2.05, 0.86, 0.74), (0.95, 0.89, 0.90), (-1.45, 0.89, 0.93), (-2.08, 0.86, 0.88), (-2.2, 0.70, 0.64)],
    [(0.95, 0.82, 0.90), (0.2, 0.66, 1.40), (-0.95, 0.66, 1.40), (-1.7, 0.80, 0.93)], (1.38, -1.3))
car('car1', [(2.25, 0.70, 0.66), (2.1, 0.90, 0.86), (1.05, 0.92, 1.02), (-2.05, 0.92, 1.04), (-2.25, 0.86, 0.74)],
    [(1.05, 0.85, 1.02), (0.4, 0.72, 1.60), (-1.85, 0.72, 1.60), (-2.2, 0.82, 1.04)], (1.42, -1.38), zb=0.34)
car('car2', [(2.6, 0.80, 0.70), (2.5, 0.96, 0.95), (1.85, 0.98, 1.12), (-2.55, 0.98, 1.12), (-2.6, 0.94, 0.75)],
    [(1.85, 0.92, 1.12), (1.3, 0.86, 2.0), (-2.5, 0.86, 2.0), (-2.58, 0.92, 1.12)], (1.7, -1.6), zb=0.36)
out = '/home/claude/out/cars.glb'
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_yup=True, export_vertex_color='ACTIVE', export_active_vertex_color_when_no_material=True, export_normals=True)
open('/home/claude/pori/cars.js', 'w').write('export default "%s";\n' % base64.b64encode(open(out, 'rb').read()).decode())
print('cars.glb', os.path.getsize(out))
