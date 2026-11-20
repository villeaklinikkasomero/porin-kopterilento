# -*- coding: utf-8 -*-
"""
Porin kauppahallin (1927) sisätila (20.11.2026): pitkä halli, mustavalkoinen ruutulattia, kojurivit molemmilla seinillä ja KESKELLÄ kojusaareke, jonka
ympäri kulkee kaksi käytävää (omistaja 20.11.2026); kermanvalkoiset puiset myyntikojut tummine katoksineen (nykyisin enimmäkseen ravintoloita ja kahviloita), pöytäryhmät kojujen edessä, valkoiset pylväät ja kattoristikot,
kattolyhdyn ikkunanauha ja pallovalaisimet.

Ajo:  python3 blender/kauppahalli_sisa.py --out DIR [--lm 2048] [--samples 24] [--shots] [--nobake]
      python3 tools/sisa_to_js.py DIR kauppahalli_sisa
Koordinaatit: X = Yrjönkadun (länsi) päädyn ovelta hallin pituussuuntaan itään kohti Isolinnankatua (suunta 100°), Y = vasemmalle (pohjoiseen), origo länsipäädyn keskellä.
Pelissä (index.html KAUH): origo (116.6, -32.7), x-akseli (0.9839, -0.1788) - jalanjäljen (city.js b 636) länsi- ja itäpäädyn keskipisteiden kautta.
Lähteet: rakenne ja värit luettu hallin omista julkaisukuvista (kuvahaun pienoiskuvat, porinkauppahalli.com), kuvia ei tallennettu. Halli ulottuu Yrjönkadulta
Isolinnankadulle (matkailu.samk.fi).
EI kopioitu: ravintoloiden ja liikkeiden nimet, kyltit, logot ja sisustukset - kojujen kylttikentät ovat tyhjiä väripintoja ja hyllyt omaa piirrosta.
Arvioitua: hallin mitat (61 x 14 m, sovitettu jalanjälkeen), kojujen määrä ja jako (8 + 8), pöytäryhmien paikat, päätyjen ikkunat, pohjoissiiven puuttuminen.
"""
import os, sys, json, math
import numpy as np
from math import sin, cos, pi, radians
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kirkko_sisa as K
from kirkko_sisa import flat, fnoise, to_img, srgb, save_tex, wall
from PIL import Image, ImageDraw
K.NAME = "kauppahalli_sisa"; K.LM_REF = 0.62
G, COL, OUT, A = K.G, K.COL, K.OUT, K.A

XA, XB, HW = 0.4, 61.0, 7.0              # päädyt, puolileveys
BAY, NBAY, XS = 6.6, 8, 4.0              # kojun jako, kojuja / sivu, ensimmäisen kojun alku
SD, IW = 2.4, 2.0                        # seinäkojun syvyys, keskisaarekkeen puolileveys (omistaja 20.11.2026: keskellä myyntikojuja, kaksi käytävää, saarekkeen voi kiertää)
ZE, ZL, ZT, LW = 5.6, 7.2, 8.4, 2.6      # katon kanta seinillä, lyhdyn alareuna, lyhdyn katto, lyhdyn puolileveys
TINT = [(0.42, 0.10, 0.08), (0.10, 0.22, 0.34), (0.12, 0.28, 0.16), (0.50, 0.34, 0.08), (0.30, 0.12, 0.30), (0.08, 0.26, 0.30), (0.46, 0.20, 0.06), (0.16, 0.16, 0.18)]

MAT = dict(kfloor=(1.6, 0), kwall=(3.0, 0), kceil=(3.0, 0), white=(2.0, 0), cream=(1.0, 0), roofg=(2.0, 0), woodd=(1.0, 0), black=(1, 0), brass=(1, 0),
           sign0=(1, 0), sign1=(1, 0), sign2=(1, 0), sign3=(1, 0), sign4=(1, 0), sign5=(1, 0), sign6=(1, 0), sign7=(1, 0), counter=(1.0, 0),
           reveal=(2.0, 0.5), glass_e=(1, 4.0), glass_l=(1.1, 3.0), shelf=(2.0, 0.9), globe=(1, 2.5), doork=(1, 0))
K.MATDEF.clear(); K.MATDEF.update(MAT); K.MI.clear(); K.MI.update({k: i for i, k in enumerate(MAT)})

def textures():
    n = 256
    save_tex("kwall", to_img(flat(n, (0.80, 0.78, 0.70), 1, 0.02, 6))); save_tex("kceil", to_img(flat(n, (0.82, 0.82, 0.80), 2, 0.015, 6)))
    save_tex("white", to_img(flat(n, (0.84, 0.84, 0.82), 3, 0.015, 8))); save_tex("roofg", to_img(flat(n, (0.10, 0.11, 0.12), 4, 0.05, 6)))
    save_tex("woodd", to_img(flat(n, (0.10, 0.055, 0.03), 5, 0.12, 3, 40))); save_tex("black", to_img(flat(64, (0.02, 0.02, 0.022), 6, 0.0)))
    save_tex("brass", to_img(flat(64, (0.55, 0.40, 0.12), 7, 0.06, 8))); save_tex("reveal", to_img(flat(n, (0.84, 0.83, 0.78), 8, 0.02, 4)))
    save_tex("counter", to_img(flat(n, (0.22, 0.12, 0.06), 9, 0.10, 40, 3))); save_tex("globe", Image.new("RGB", (16, 16), (255, 240, 205)))
    # lattia: mustavalkoinen ruutulaatta 0,4 m
    a = np.zeros((n, n, 3), np.float32)
    for j in range(4):
        for i in range(4): a[j * 64:(j + 1) * 64, i * 64:(i + 1) * 64] = (0.70, 0.69, 0.66) if (i + j) % 2 else (0.035, 0.035, 0.04)
    a *= (1 + 0.05 * fnoise(n, 10, 8))[..., None]; save_tex("kfloor", to_img(a))
    # kojun paneeli: kermanvalkoinen pystypaneeli peilein (v = 1,1 m)
    im = to_img(flat(n, (0.80, 0.76, 0.62), 11, 0.02, 6)); d = ImageDraw.Draw(im); sh = srgb((0.50, 0.46, 0.36))
    for x in range(0, n, 64): d.rectangle([x + 8, 26, x + 56, n - 30], outline=sh, width=3)
    d.rectangle([0, 0, n, 12], fill=srgb((0.86, 0.82, 0.68))); d.line([(0, 14), (n, 14)], fill=sh, width=3); d.rectangle([0, n - 18, n, n], fill=srgb((0.30, 0.28, 0.24)))
    save_tex("cream", im)
    # kylttikentät: tyhjä väripinta kehyksin (ei nimiä)
    for k, c in enumerate(TINT):
        im = to_img(flat(n, c, 20 + k, 0.04, 6)); d = ImageDraw.Draw(im); d.rectangle([4, 4, n - 5, n - 5], outline=srgb((0.80, 0.70, 0.40)), width=6); save_tex("sign%d" % k, im)
    # kojun takaseinä: tumma lämmin hyllykkö (oma piirros: hyllyt, purkit ja pullot värilaikkuina), valaiseva
    im = to_img(flat(n, (0.16, 0.09, 0.05), 12, 0.08, 6)); d = ImageDraw.Draw(im); rng = np.random.default_rng(3)
    for y in (60, 124, 188, 252): d.rectangle([0, y - 5, n, y], fill=srgb((0.34, 0.20, 0.09)))
    for y in (60, 124, 188):
        x = 6
        while x < n - 12:
            w = int(rng.integers(8, 20)); h = int(rng.integers(20, 46)); c = [(214, 180, 90), (150, 60, 40), (70, 110, 80), (226, 222, 206), (60, 80, 130), (200, 120, 50)][int(rng.integers(0, 6))]
            d.rectangle([x, y - 6 - h, x + w, y - 6], fill=c); x += w + int(rng.integers(3, 9))
    save_tex("shelf", im)
    # päätyjen kaari-ikkuna ja lyhdyn ikkunanauha (valaisevat)
    W, H = 384, 256; a = np.ones((H, W, 3)) * np.array((0.74, 0.84, 0.94))[None, None, :] * (1 + 0.05 * fnoise(512, 13, 4)[:H, :W, None]); im = to_img(a); d = ImageDraw.Draw(im); fr = (238, 236, 228)
    for x in range(0, W + 1, 48): d.line([(x, 0), (x, H)], fill=fr, width=6)
    for y in (0, 86, 172, H - 1): d.line([(0, y), (W, y)], fill=fr, width=6)
    save_tex("glass_e", im)
    a = np.ones((n, n, 3)) * np.array((0.78, 0.86, 0.92))[None, None, :] * (1 + 0.04 * fnoise(n, 14, 3)[..., None]); im = to_img(a); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, n - 1, n - 1], outline=fr, width=10); d.line([(n / 2, 0), (n / 2, n)], fill=fr, width=6); save_tex("glass_l", im)
    im = to_img(flat(n, (0.07, 0.05, 0.035), 15, 0.08, 3, 50)); d = ImageDraw.Draw(im)
    for i in range(2): d.rectangle([14 + i * 128, 14, 114 + i * 128, 170], fill=(150, 170, 180), outline=(20, 14, 10), width=4)
    d.line([(128, 0), (128, n)], fill=(12, 8, 6), width=5); save_tex("doork", im)

def build():
    LAMPS = []; wb = ((1.2, "cream"), (1e9, "kwall"))
    # --- seinät, lattia, katto ja kattolyhty
    for s in (1, -1): wall((XA, s * HW), (XB, s * HW), lambda q: ZE, (30, 0), bands=wb)
    gab = lambda y: ZE + (ZL - ZE) * (1 - max(0.0, abs(y) - LW) / (HW - LW)) if abs(y) > LW else ZT
    wall((XA, -HW), (XA, HW), lambda q: gab(-HW + q), (30, 0), [K.Win(HW, 4.4, 3.2, 4.6, 1.4, "glass_e")], bands=wb)
    wall((XB, -HW), (XB, HW), lambda q: gab(-HW + q), (30, 0), [K.Win(HW, 4.4, 3.2, 4.6, 1.4, "glass_e")], bands=wb)
    for (x, nx) in ((XA, 1), (XB, -1)):
        G.face([(x + nx * 0.06, -1.3, 0), (x + nx * 0.06, 1.3, 0), (x + nx * 0.06, 1.3, 2.5), (x + nx * 0.06, -1.3, 2.5)], "doork", uv=[(0, 0), (1, 0), (1, 1), (0, 1)], toward=(30, 0, 1))
    G.face([(XA, -HW, 0), (XB, -HW, 0), (XB, HW, 0), (XA, HW, 0)], "kfloor", up=True)
    for s in (1, -1):
        G.face([(XA, s * HW, ZE), (XB, s * HW, ZE), (XB, s * LW, ZL), (XA, s * LW, ZL)], "kceil", toward=(30, 0, 0))
        G.face([(XA, s * LW, ZL), (XB, s * LW, ZL), (XB, s * LW, ZT), (XA, s * LW, ZT)], "glass_l", uv=[(0, 0), ((XB - XA) / 1.1, 0), ((XB - XA) / 1.1, 1), (0, 1)], toward=(30, 0, 7.8))
    G.face([(XA, -LW, ZT), (XB, -LW, ZT), (XB, LW, ZT), (XA, LW, ZT)], "kceil", up=False)
    for i in range(NBAY + 1):                                                    # ristikot ja pylväät kojujen kulmissa
        x = XS + BAY * i
        G.box(x - 0.08, x + 0.08, -HW, HW, ZE - 0.25, ZE - 0.05, "white")
        for s in (1, -1):
            G.small = True
            G.face([(x - 0.06, s * HW, ZE - 0.05), (x + 0.06, s * HW, ZE - 0.05), (x + 0.06, s * LW, ZL - 0.05), (x - 0.06, s * LW, ZL - 0.05)], "white", toward=(x, 0, 0))
            for yy in (s * 4.8, s * LW): G.box(x - 0.04, x + 0.04, yy - 0.04, yy + 0.04, ZE - 0.05, gab(yy) - 0.05 if abs(yy) > LW else ZL - 0.05, "white", skip="z-z+")
            G.small = False
            G.cyl(x, s * IW, 0, ZE - 0.25, 0.13, 8, "white"); COL["circ"].append([x, s * IW, 0.2])
    # --- kojut: tiski, aukko, otsalauta kylttikenttineen, tumma katos, valaistu hyllykkö takaseinällä
    def stall(x0, x1, yf, yw, k):
        o = 1 if yf > yw else -1; tw = lambda z: (x0, yf + o * 5, z); d = abs(yf - yw)
        G.face([(x0, yf, 0), (x1, yf, 0), (x1, yf, 1.1), (x0, yf, 1.1)], "cream", uv=[(0, 0), ((x1 - x0) / 1.0, 0), ((x1 - x0) / 1.0, 1), (0, 1)], toward=tw(0.5))
        G.face([(x0, yf + o * 0.25, 1.1), (x1, yf + o * 0.25, 1.1), (x1, yf - o * 0.45, 1.1), (x0, yf - o * 0.45, 1.1)], "counter", up=True)
        G.face([(x0, yf + o * 0.25, 1.02), (x1, yf + o * 0.25, 1.02), (x1, yf + o * 0.25, 1.1), (x0, yf + o * 0.25, 1.1)], "counter", toward=tw(1))
        G.face([(x0, yf, 2.35), (x1, yf, 2.35), (x1, yf, 3.05), (x0, yf, 3.05)], "cream", uv=[(0, 0.1), ((x1 - x0) / 1.0, 0.1), ((x1 - x0) / 1.0, 0.7), (0, 0.7)], toward=tw(2.7))
        G.face([(x0 + 1.0, yf + o * 0.02, 2.45), (x1 - 1.0, yf + o * 0.02, 2.45), (x1 - 1.0, yf + o * 0.02, 2.95), (x0 + 1.0, yf + o * 0.02, 2.95)], "sign%d" % k, uv=[(0, 0), (1, 0), (1, 1), (0, 1)], toward=tw(2.7))
        G.face([(x0 - 0.25, yf + o * 0.35, 3.05), (x1 + 0.25, yf + o * 0.35, 3.05), (x1 + 0.25, yw, 3.05), (x0 - 0.25, yw, 3.05)], "roofg", up=True)
        G.face([(x0 - 0.25, yf + o * 0.35, 2.95), (x1 + 0.25, yf + o * 0.35, 2.95), (x1 + 0.25, yw, 2.95), (x0 - 0.25, yw, 2.95)], "white", up=False)
        G.face([(x0 - 0.25, yf + o * 0.35, 2.95), (x1 + 0.25, yf + o * 0.35, 2.95), (x1 + 0.25, yf + o * 0.35, 3.05), (x0 - 0.25, yf + o * 0.35, 3.05)], "roofg", toward=tw(3))
        G.face([(x0, yw + o * 0.05, 0.0), (x1, yw + o * 0.05, 0.0), (x1, yw + o * 0.05, 2.95), (x0, yw + o * 0.05, 2.95)], "shelf", uv=[(0, 0), ((x1 - x0) / 2.0, 0), ((x1 - x0) / 2.0, 1), (0, 1)], toward=tw(1.5))
        for xx in (x0, x1):
            q = [(xx, yf, 0), (xx, yw, 0), (xx, yw, 2.95), (xx, yf, 2.95)]; uvq = [(0, 0), (d, 0), (d, 2.7), (0, 2.7)]
            G.face(q, "cream", uv=uvq, toward=((x0 + x1) / 2, yf, 1.5)); G.face(q, "cream", uv=uvq, away=((x0 + x1) / 2, yf, 1.5))
            G.face([(xx - 0.25 if xx == x0 else xx, yf + o * 0.35, 2.95), (xx + 0.25 if xx == x1 else xx, yf + o * 0.35, 2.95), (xx + 0.25 if xx == x1 else xx, yw, 2.95), (xx - 0.25 if xx == x0 else xx, yw, 2.95)], "roofg", up=False) if False else None
        COL["seg"].append([x0, yf + o * 0.1, x1, yf + o * 0.1, 0.3]); COL["seg"] += [[x0, yf, x0, yw, 0.1], [x1, yf, x1, yw, 0.1]]
        LAMPS.append(((x0 + x1) / 2, yf - o * d * 0.5, 2.6, 60, (1.0, 0.86, 0.66)))
    for s in (1, -1):                                                            # seinäkojut
        for i in range(NBAY): stall(XS + BAY * i + 0.25, XS + BAY * (i + 1) - 0.25, s * (HW - SD), s * HW, (i * 3 + (0 if s > 0 else 5)) % 8)
    # --- keskisaareke: selät vastakkain olevat kojut, välissä ja päissä poikkikulut ja pöytäryhmät; saarekkeen ympäri kulkee kaksi käytävää
    def table(x, y):
        G.box(x - 0.6, x + 0.6, y - 0.38, y + 0.38, 0.72, 0.76, "woodd"); G.small = True; G.cyl(x, y, 0, 0.72, 0.05, 6, "black"); G.cyl(x, y, 0, 0.03, 0.26, 8, "black", cap=True)
        for (cx, cy) in ((x - 0.3, y - 0.62), (x + 0.3, y - 0.62), (x - 0.3, y + 0.62), (x + 0.3, y + 0.62)):
            G.box(cx - 0.2, cx + 0.2, cy - 0.2, cy + 0.2, 0.42, 0.46, "woodd"); G.box(cx - 0.2, cx + 0.2, cy + (0.16 if cy > y else -0.2), cy + (0.2 if cy > y else -0.16), 0.46, 0.9, "woodd", skip="z-")
            for (lx, ly) in ((-0.17, -0.17), (0.17, -0.17), (-0.17, 0.17), (0.17, 0.17)): G.cyl(cx + lx, cy + ly, 0, 0.42, 0.018, 4, "woodd")
        G.small = False; COL["circ"].append([x, y, 0.75])
    for i in range(NBAY):
        x0, x1 = XS + BAY * i + 0.25, XS + BAY * (i + 1) - 0.25
        if i in (1, 2, 5, 6):
            for s in (1, -1): stall(x0, x1, s * IW, 0.0, (i * 5 + (2 if s > 0 else 6)) % 8)
        elif i in (3, 4):
            for dx in (1.6, 4.6): table(x0 + dx, 0.0)
    for x in (XS + BAY * 0.5 + 1.2, XS + BAY * 7.5 - 1.2): table(x, 0.0)
    # --- pallovalaisimet molempien käytävien yllä
    G.small = True
    for x in np.arange(XS + BAY / 2, XB - 2, BAY):
        for y in (-3.3, 3.3):
            G.cyl(x, y, 4.25, gab(y), 0.012, 4, "black"); G.cyl(x, y, 3.75, 4.0, 0.0, 8, "globe", r1=0.25); G.cyl(x, y, 4.0, 4.25, 0.25, 8, "globe", r1=0.0)
            LAMPS.append((x, y, 3.5, 200, (1.0, 0.90, 0.72)))
    G.small = False
    return LAMPS

if __name__ == "__main__":
    import bpy
    textures(); LAMPS = build()
    print(len(G.F), "pintaa,", len(COL["seg"]), "janaa,", len(COL["circ"]), "ympyrää")
    objs = K.make_scene([])
    for (x, y, z, w, c) in LAMPS:
        l = bpy.data.lights.new("valo", "POINT"); l.energy = w; l.color = c; l.shadow_soft_size = 0.3
        o = bpy.data.objects.new("valo", l); o.location = (x, y, z); bpy.context.scene.collection.objects.link(o)
    if A.shots: K.shots(V=dict(ovelta=((1.6, 0.0, 1.7), (30, 0, 2.6), 14), koju=((8.0, 3.3, 1.7), (40, 2.6, 2.0), 16), ylos=((30.0, 0.5, 1.7), (50, 0, 7.0), 14)))
    LMAX = 2.0
    if not A.nobake: LMAX = K.finish_lm(K.bake(objs))
    K.export(objs)
    room = [[XA, -HW], [XB, -HW], [XB, HW], [XA, HW]]
    meta = dict(col=COL, lmax=LMAX, xw=XA, xe=XB, hw=HW, py=0.0, xs0=1e6, flz=0.0, spawn=[2.0, 0.0], exit=[1.1, 1.5], room=room, rooms=[room], ports=[])
    json.dump(meta, open("%s/%s.json" % (OUT, K.NAME), "w"))
