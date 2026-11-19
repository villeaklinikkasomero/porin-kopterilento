# -*- coding: utf-8 -*-
"""
Porin taidemuseon Halli (20.11.2026): pitkä valkoinen näyttelyhalli, punaruskea tiililaattalattia, jokirannan kaari-ikkunat, valkoiset teräsristikot ja
lasikatto, hoikat ruskeat pylväät, irtoseinät ja jalustat.

Ajo:  python3 blender/taidemuseo_sisa.py --out DIR [--lm 2048] [--samples 24] [--shots] [--nobake]
      python3 tools/sisa_to_js.py DIR taidemuseo_sisa
Koordinaatit: X = Etelärannan (joen puoleiselta) ovelta sisään etelään päin (suunta 193°), Y = vasemmalle (itään), Z = ylös, origo pohjoisseinän keskellä.
Pelissä (index.html TAIM): origo (-96.85, 467.4) = jalanjäljen (city.js b 1282) sisäänvedetyn pohjoisjulkisivun keskikohta.
Lähteet: rakenne ja värit luettu museon julkaisemista näyttelykuvista (kuvahaun pienoiskuvat, poriartmuseum.fi, museot.fi), kuvia ei tallennettu.
Tiedot: pakkahuone 1860 / 1897, muutos taidemuseoksi 1981 (Arkkitehdit Ky, Kristian Gullichsen), näyttelytilaa n. 800 m2 (poriartmuseum.fi).
EI kopioitu: näyttelyiden taideteokset - seinillä ja jalustoilla on OMIA abstrakteja sommitelmia. Arvioitua: hallin mitat (44 x 17 m, sovitettu jalanjälkeen),
pääoven paikka (oletettu pohjoisjulkisivun keskelle), ikkuna- ja pylväsjako, irtoseinien paikat. Muut tilat (aula, Siipi, MEDIApiste, kahvila) puuttuvat.
"""
import os, sys, json, math
import numpy as np
from math import sin, cos, pi, radians
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kirkko_sisa as K
from kirkko_sisa import flat, fnoise, to_img, srgb, save_tex, wall
from PIL import Image, ImageDraw
K.NAME = "taidemuseo_sisa"; K.LM_REF = 0.66
G, COL, OUT, A = K.G, K.COL, K.OUT, K.A

XA, XB, HY = 0.4, 17.4, 22.0             # pohjois- ja eteläseinä, hallin puolipituus
ZE, ZR = 6.0, 8.0                        # sivukaton korkeus, lasikaton harja
SX0, SX1 = 5.0, 12.8                     # lasikaton reunat
BAY = 4.4

MAT = dict(mwall=(3.0, 0), mfloor=(1.2, 0), mceil=(3.0, 0), steel=(2.0, 0), colb=(1.0, 0), lilac=(3.0, 0), plinth=(2.0, 0), wood=(1.0, 0), black=(1, 0),
           art1=(1, 0), art2=(1, 0), art3=(1, 0), art4=(1, 0), art5=(1, 0), art6=(1, 0), sc1=(1, 0), sc2=(1, 0), sc3=(1, 0),
           reveal=(2.0, 0.5), glass_a=(1, 4.0), glass_d=(1, 3.0), sky=(1.1, 2.2))
K.MATDEF.clear(); K.MATDEF.update(MAT); K.MI.clear(); K.MI.update({k: i for i, k in enumerate(MAT)})

def textures():
    n = 256
    save_tex("mwall", to_img(flat(n, (0.84, 0.84, 0.82), 1, 0.015, 6)))
    save_tex("mceil", to_img(flat(n, (0.80, 0.80, 0.78), 2, 0.015, 6)))
    save_tex("steel", to_img(flat(n, (0.84, 0.84, 0.83), 3, 0.015, 8)))
    save_tex("plinth", to_img(flat(n, (0.86, 0.86, 0.85), 4, 0.01, 8)))
    save_tex("reveal", to_img(flat(n, (0.86, 0.86, 0.84), 5, 0.02, 4)))
    save_tex("colb", to_img(flat(n, (0.20, 0.09, 0.04), 6, 0.10, 3, 40)))
    save_tex("wood", to_img(flat(n, (0.36, 0.22, 0.10), 7, 0.10, 3, 40)))
    save_tex("lilac", to_img(flat(n, (0.55, 0.42, 0.66), 8, 0.02, 6)))
    save_tex("black", to_img(flat(64, (0.02, 0.02, 0.022), 9, 0.0)))
    # lattia: punaruskea tiililaatta 0,3 x 0,15 m limittäin
    a = flat(n, (0.42, 0.17, 0.09), 10, 0.06, 6); rng = np.random.default_rng(2)
    for j in range(8):
        for i in range(5):
            x0 = (i * 64 - (32 if j % 2 else 0)) % n; k = 1 + rng.uniform(-0.16, 0.16); a[j * 32:(j + 1) * 32, x0:min(n, x0 + 64)] *= k
            if x0 + 64 > n: a[j * 32:(j + 1) * 32, 0:x0 + 64 - n] *= k
    im = to_img(a); d = ImageDraw.Draw(im); gc = srgb((0.16, 0.10, 0.07))
    for j in range(8):
        d.line([(0, j * 32), (n, j * 32)], fill=gc, width=2)
        for i in range(5): x = i * 64 - (32 if j % 2 else 0); d.line([(x, j * 32), (x, j * 32 + 32)], fill=gc, width=2)
    save_tex("mfloor", im)
    # kaari-ikkunat (valaisevat): sinertävä päivänvalo, valkoiset puitteet; ovi samalla jaolla
    for name, H in (("glass_a", 400), ("glass_d", 480)):
        W = 240; a = np.ones((H, W, 3)) * np.array((0.62, 0.76, 0.92))[None, None, :] * (1 + 0.06 * fnoise(512, 11, 4)[:H, :W, None]); im = to_img(a); d = ImageDraw.Draw(im); fr = (236, 236, 232)
        d.line([(W / 2, 0), (W / 2, H)], fill=fr, width=10); d.line([(0, 130), (W, 130)], fill=fr, width=8)
        for k in range(1, 4): d.line([(W / 2, 130), (W / 2 + 170 * cos(pi * k / 4), 130 - 170 * sin(pi * k / 4))], fill=fr, width=5)
        for x in (W / 4, 3 * W / 4): d.line([(x, 130), (x, H)], fill=fr, width=5)
        d.rectangle([0, 0, W - 1, H - 1], outline=fr, width=12); save_tex(name, im)
    # lasikatto: vaalea lasi, valkoinen puitejako (u, v = 1,1 m)
    a = np.ones((n, n, 3)) * np.array((0.80, 0.86, 0.90))[None, None, :] * (1 + 0.04 * fnoise(n, 12, 3)[..., None]); im = to_img(a); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, n - 1, n - 1], outline=(240, 240, 238), width=9); save_tex("sky", im)
    # omat abstraktit sommitelmat (ei minkään teoksen jäljennöksiä)
    pal = [(214, 60, 48), (240, 190, 40), (40, 90, 170), (30, 30, 34), (236, 232, 220), (60, 150, 110), (230, 120, 60), (150, 90, 170)]
    for k in range(6):
        rng = np.random.default_rng(40 + k); W, H = (384, 288) if k % 2 else (288, 384); im = Image.new("RGB", (W, H), pal[4 if k % 3 else 3]); d = ImageDraw.Draw(im)
        for i in range(7):
            c = pal[int(rng.integers(0, len(pal)))]; x, y, w, h = rng.uniform(0, W * 0.7), rng.uniform(0, H * 0.7), rng.uniform(W * 0.15, W * 0.55), rng.uniform(H * 0.1, H * 0.5)
            if (i + k) % 3 == 0: d.ellipse([x, y, x + min(w, h), y + min(w, h)], fill=c)
            elif (i + k) % 3 == 1: d.rectangle([x, y, x + w, y + h], fill=c)
            else: d.polygon([(x, y + h), (x + w / 2, y), (x + w, y + h)], fill=c)
        for i in range(3): d.line([(rng.uniform(0, W), rng.uniform(0, H)), (rng.uniform(0, W), rng.uniform(0, H))], fill=pal[3], width=6)
        a = np.asarray(im).astype(np.float32) / 255 * (0.95 + 0.05 * fnoise(512, 60 + k, 30)[:H, :W, None]); save_tex("art%d" % (k + 1), Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)))
    for k, c in enumerate(((0.55, 0.06, 0.05), (0.06, 0.16, 0.42), (0.62, 0.45, 0.06))): save_tex("sc%d" % (k + 1), to_img(flat(64, c, 70 + k, 0.05, 6)))

def beam(p0, p1, w, mat, small=True):
    """Ohut suorakaidepalkki kahden pisteen välillä (neljä sivua)."""
    from mathutils import Vector
    a, b = Vector(p0), Vector(p1); t = (b - a).normalized(); s = t.cross(Vector((0, 1, 0)));
    if s.length < 1e-3: s = t.cross(Vector((1, 0, 0)))
    s.normalize(); u = t.cross(s).normalized(); G.small = small
    for (e, f) in ((s, u), (u, -s), (-s, -u), (-u, s)):
        q = [a + e * w + f * w, b + e * w + f * w, b + e * w - f * w, a + e * w - f * w]; G.face([tuple(v) for v in q], mat, away=tuple((a + b) / 2))
    G.small = False

def build():
    LAMPS = []; wb = ((0.1, "wood"), (1e9, "mwall")); top = lambda q: ZE
    ys = [-HY + BAY * (i + 0.5) for i in range(10)]
    wins = [K.Win(HY + y, 2.0, 1.0, 3.0, 1.0, "glass_a") for y in ys if abs(y) > 2.3] + [K.Win(HY, 2.4, 0.03, 2.6, 1.2, "glass_d")]
    wall((XA, -HY), (XA, HY), top, (9, 0), wins, bands=wb)                                    # pohjoisseinä: kaari-ikkunat joelle, keskellä lasiovi
    wall((XB, -HY), (XB, -7.0), top, (9, 0), bands=wb); wall((XB, 7.0), (XB, HY), top, (9, 0), bands=wb)
    wall((XB, -7.0), (XB, 7.0), top, (9, 0), bands=((0.1, "wood"), (1e9, "lilac")))            # eteläseinän keskiosa värillinen
    for s in (1, -1): wall((XA, s * HY), (XB, s * HY), lambda q: ZE + max(0.0, (ZR - ZE) * (1 - abs(XA + q - (SX0 + SX1) / 2) / ((SX1 - SX0) / 2))), (9, 0), bands=wb)
    G.face([(XA, -HY, 0), (XB, -HY, 0), (XB, HY, 0), (XA, HY, 0)], "mfloor", up=True)
    G.face([(XA, -HY, ZE), (SX0, -HY, ZE), (SX0, HY, ZE), (XA, HY, ZE)], "mceil", up=False); G.face([(SX1, -HY, ZE), (XB, -HY, ZE), (XB, HY, ZE), (SX1, HY, ZE)], "mceil", up=False)
    xm = (SX0 + SX1) / 2; L = math.hypot(xm - SX0, ZR - ZE)
    for i in range(10):                                                                        # lasikatto lapeittain, ristikot jakoväleissä
        y0, y1 = -HY + BAY * i, -HY + BAY * (i + 1)
        for (xa, xb) in ((SX0, xm), (SX1, xm)):
            G.face([(xa, y0, ZE), (xa, y1, ZE), (xb, y1, ZR), (xb, y0, ZR)], "sky", uv=[(0, 0), (4, 0), (4, L / 1.1), (0, L / 1.1)], toward=(9, 0, 2))
    for i in range(11):
        y = -HY + BAY * i; y = min(max(y, -HY + 0.15), HY - 0.15)
        G.box(XA, XB, y - 0.07, y + 0.07, ZE - 0.2, ZE - 0.02, "steel", skip="")
        beam((SX0, y, ZE - 0.1), (xm, y, ZR - 0.15), 0.05, "steel"); beam((SX1, y, ZE - 0.1), (xm, y, ZR - 0.15), 0.05, "steel")
        for xx in (SX0 + 1.95, xm, SX1 - 1.95): beam((xx, y, ZE - 0.1), (xx, y, ZE + (ZR - ZE) * (1 - abs(xx - xm) / (xm - SX0)) - 0.15), 0.035, "steel")
        beam((SX0 + 1.95, y, ZE - 0.1), (xm, y, ZR - 0.15), 0.03, "steel"); beam((SX1 - 1.95, y, ZE - 0.1), (xm, y, ZR - 0.15), 0.03, "steel")
    for x in (SX0, xm, SX1): beam((x, -HY, ZE - 0.1 if x != xm else ZR - 0.15), (x, HY, ZE - 0.1 if x != xm else ZR - 0.15), 0.05, "steel")
    for x in (SX0, SX1):                                                                       # hoikat ruskeat pylväät
        for y in np.arange(-HY + 2 * BAY, HY - 1, 2 * BAY):
            G.cyl(x, y, 0, ZE - 0.2, 0.11, 10, "colb"); COL["circ"].append([x, y, 0.16])
    # irtoseinät ja teokset (omat sommitelmat)
    def art(p, n, w, h, z, mat):
        tx, ty = -n[1], n[0]; q = [(p[0] + tx * s + n[0] * 0.02, p[1] + ty * s + n[1] * 0.02, zz) for s, zz in ((-w / 2, z), (w / 2, z), (w / 2, z + h), (-w / 2, z + h))]
        G.face(q, mat, uv=[(0, 0), (1, 0), (1, 1), (0, 1)], toward=(p[0] + n[0] * 5, p[1] + n[1] * 5, z))

    for (x0, x1, y, a1, a2) in ((6.5, 12.0, -11.0, "art1", "art2"), (6.5, 12.0, 11.0, "art3", "art4")):
        G.box(x0, x1, y - 0.15, y + 0.15, 0, 3.6, "plinth", skip="z-"); COL["seg"].append([x0, y, x1, y, 0.2])
        art(((x0 + x1) / 2, y + 0.15), (0, 1), 2.4, 1.8, 1.1, a1); art(((x0 + x1) / 2, y - 0.15), (0, -1), 1.8, 2.4, 0.8, a2)
    G.box(8.8, 9.1, 14.5, 19.5, 0, 3.6, "plinth", skip="z-"); COL["seg"].append([8.95, 14.5, 8.95, 19.5, 0.2]); art((8.8, 17.0), (-1, 0), 2.4, 1.8, 1.1, "art5")
    art((XB, 0.0), (-1, 0), 3.2, 2.4, 1.2, "art6"); art((XB, -15.0), (-1, 0), 1.8, 2.4, 1.0, "art2"); art((XB, 15.0), (-1, 0), 2.4, 1.8, 1.2, "art1")
    art((9.0, -HY), (0, 1), 2.4, 1.8, 1.2, "art3"); art((9.0, HY), (0, -1), 1.8, 2.4, 1.0, "art4")
    for k, (x, y) in enumerate(((9.0, -3.0), (11.0, 4.0), (6.0, -17.0))):                       # jalustat ja pelkistetyt veistokset
        G.box(x - 0.3, x + 0.3, y - 0.3, y + 0.3, 0, 1.0, "plinth", skip="z-"); COL["circ"].append([x, y, 0.45]); m = "sc%d" % (k + 1)
        if k == 0: G.cyl(x, y, 1.0, 1.35, 0.0, 10, m, r1=0.26); G.cyl(x, y, 1.35, 1.7, 0.26, 10, m, r1=0.0)
        elif k == 1: G.box(x - 0.12, x + 0.12, y - 0.12, y + 0.12, 1.0, 1.9, m, skip="z-"); G.box(x - 0.3, x + 0.3, y - 0.08, y + 0.08, 1.5, 1.7, m)
        else: G.cyl(x, y, 1.0, 1.6, 0.22, 6, m, r1=0.1, cap=True)
    G.box(1.4, 2.2, 3.2, 6.6, 0, 1.05, "wood", skip="z-"); COL["seg"].append([1.8, 3.4, 1.8, 6.4, 0.45])       # palvelutiski oven vieressä
    for y in (-6.0, 8.0): G.box(9.0, 10.6, y - 0.22, y + 0.22, 0, 0.44, "wood", skip="z-"); COL["seg"].append([9.0, y, 10.6, y, 0.25])   # penkit
    for y in (-15.0, -5.0, 5.0, 15.0):
        for x in (2.8, 15.0): LAMPS.append((x, y, ZE - 0.6, 120, (1.0, 0.97, 0.92)))
    return LAMPS

if __name__ == "__main__":
    import bpy
    textures(); LAMPS = build()
    print(len(G.F), "pintaa,", len(COL["seg"]), "janaa,", len(COL["circ"]), "ympyrää")
    objs = K.make_scene([])
    for (x, y, z, w, c) in LAMPS:
        l = bpy.data.lights.new("valo", "POINT"); l.energy = w; l.color = c; l.shadow_soft_size = 0.4
        o = bpy.data.objects.new("valo", l); o.location = (x, y, z); bpy.context.scene.collection.objects.link(o)
    if A.shots: K.shots(V=dict(ovelta=((1.6, 0.0, 1.7), (17, 3, 2.6), 16), pitkin=((9.0, -20.5, 1.7), (9, 20, 3.4), 16), ikkunat=((14.5, 6.0, 1.7), (0, -6, 3.0), 16)))
    LMAX = 2.0
    if not A.nobake: LMAX = K.finish_lm(K.bake(objs))
    K.export(objs)
    room = [[XA, -HY], [XB, -HY], [XB, HY], [XA, HY]]
    meta = dict(col=COL, lmax=LMAX, xw=XA, xe=XB, hw=HY, py=0.0, xs0=1e6, flz=0.0, spawn=[2.0, 0.0], exit=[1.1, 1.4], room=room, rooms=[room], ports=[])
    json.dump(meta, open("%s/%s.json" % (OUT, K.NAME), "w"))
