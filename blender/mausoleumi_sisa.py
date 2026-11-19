# -*- coding: utf-8 -*-
"""
Juseliuksen mausoleumin sisätila (19.11.2026): kahdeksankulmainen halli, korkeat ruusukeikkunat, freskokentät, keskellä
pyöreä aukko kaiteineen ja sen alla krypta sarkofageineen, holvi ruoteineen.

Ajo:  python3 blender/mausoleumi_sisa.py --out DIR [--lm 2048] [--samples 40] [--shots] [--nobake]
      python3 tools/sisa_to_js.py DIR mausoleumi_sisa        (pelikansiossa -> mausoleumi_sisa.js)
Käyttää kirkko_sisa.py:n työkaluja (Geo, wall, valokartan leivonta, vienti).

Koordinaatit: X = ovelta kohti vastapäistä syvennystä, Y = vasemmalle, Z = ylös, origo hallin keskellä lattialla.
Pelissä: ulkomallin (bl_mausoleumi.js) keskipiste (-1947.81, 193.18), X-akseli suuntaan 166° (ovi on mallin itäsivulla).
Sisäkuvista (jalkipeli.net ym.) on luettu vain rakenne, värit ja materiaalit. FRESKOJA EI OLE KOPIOITU (Gallen-Kallela, Halonen):
kentissä on omat abstraktit väripinnat. Pronssiovien reliefejä ei myöskään ole jäljitelty.
"""
import os, sys, json, math
import numpy as np
from math import sin, cos, pi, sqrt, radians
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kirkko_sisa as K
from kirkko_sisa import parch, flat, fnoise, to_img, srgb, save_tex, Win, wall
from PIL import Image, ImageDraw, ImageFilter
K.NAME = "mausoleumi_sisa"; K.LM_REF = 0.70
G, COL, OUT, A = K.G, K.COL, K.OUT, K.A

AP = 4.4; RC = AP / cos(pi / 8)          # seinän etäisyys keskeltä, kulmien säde
ZS, RV = 9.0, 4.2                        # holvin kanta ja nousu
RH = 1.9                                 # lattia-aukon säde
ZC = -3.4                                # kryptan lattia

MAT = dict(marble=(2.0, 0), mdado=(1.1, 0), vaultm=(1.5, 0), ribm=(1.0, 0), mfloor=(2.0, 0), cfloor=(1.5, 0), crypt=(1.5, 0), balu=(1, 0),
           portal=(1, 0), bronze=(1, 0), fresco1=(1, 0), fresco2=(1, 0), fresco3=(1, 0), frescot=(1, 0), gold=(1.0, 0), sarco=(1.5, 0),
           glass_m=(1, 5.0), reveal=(2.0, 0.5))
K.MATDEF.clear(); K.MATDEF.update(MAT); K.MI.clear(); K.MI.update({k: i for i, k in enumerate(MAT)})

def marble(n, base, seed, vein=0.10):
    a = flat(n, base, seed, 0.03, 4)
    v = np.abs(fnoise(n, seed + 7, 5, 9) + 0.6 * fnoise(n, seed + 8, 16)); v = np.clip(1 - v / 0.22, 0, 1) ** 2
    return a * (1 - vein * v[..., None] * np.array([1.0, 0.95, 0.85])[None, None, :] * 3)

def textures():
    n = 256; lead = (38, 42, 48)
    save_tex("marble", to_img(marble(n, (0.74, 0.74, 0.71), 1)))
    save_tex("sarco", to_img(marble(n, (0.80, 0.80, 0.78), 5, 0.05)))
    save_tex("reveal", to_img(flat(n, (0.82, 0.82, 0.78), 22, 0.03, 4)))
    save_tex("gold", to_img(flat(n, (0.66, 0.47, 0.12), 4, 0.08, 12)))
    save_tex("ribm", to_img(marble(n, (0.70, 0.69, 0.64), 3, 0.04)))
    im = to_img(marble(n, (0.60, 0.61, 0.60), 2, 0.14)); d = ImageDraw.Draw(im)                 # jalusta: harmaampi marmori, yläreunassa lista
    d.rectangle([0, 0, n, 10], fill=srgb((0.80, 0.80, 0.77))); d.rectangle([0, 10, n, 15], fill=srgb((0.30, 0.30, 0.30)))
    save_tex("mdado", im)
    # holvi: lämmin kellanvalkoinen, oma tyylitelty köynnöskuvio
    im = to_img(flat(n, (0.72, 0.62, 0.40), 11, 0.05, 5)); d = ImageDraw.Draw(im); oc, gc = srgb((0.50, 0.33, 0.12)), srgb((0.35, 0.42, 0.28))
    for cx, cy in ((64, 64), (192, 192)):
        for k in range(6):
            an = k * pi / 3; d.ellipse([cx + 30 * cos(an) - 12, cy + 30 * sin(an) - 12, cx + 30 * cos(an) + 12, cy + 30 * sin(an) + 12], outline=oc, width=3)
        d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=oc)
    for cx, cy in ((192, 64), (64, 192)):
        d.arc([cx - 40, cy - 40, cx + 40, cy + 40], 20, 160, fill=gc, width=4); d.arc([cx - 40, cy - 40, cx + 40, cy + 40], 200, 340, fill=gc, width=4); d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=gc)
    save_tex("vaultm", im)
    # lattia: vaalea ja harmaa marmorilaatta ruuduittain (ruutu 2 m = 4 x 4 laattaa)
    a = marble(n, (0.62, 0.62, 0.60), 17, 0.06)
    for j in range(4):
        for i in range(4):
            if (i + j) % 2: a[j * 64:(j + 1) * 64, i * 64:(i + 1) * 64] *= 0.62
    im = to_img(a); d = ImageDraw.Draw(im)
    for k in range(0, n, 64): d.line([(k, 0), (k, n)], fill=srgb((0.18, 0.18, 0.18)), width=2); d.line([(0, k), (n, k)], fill=srgb((0.18, 0.18, 0.18)), width=2)
    save_tex("mfloor", im)
    save_tex("cfloor", to_img(marble(n, (0.30, 0.28, 0.25), 18, 0.05)))
    im = to_img(flat(n, (0.10, 0.16, 0.24), 19, 0.10, 20)); d = ImageDraw.Draw(im)              # krypta: tumma sinertävä mosaiikki, kultapisteet
    for j in range(0, n, 16):
        for i in range(0, n, 16):
            d.rectangle([i, j, i + 15, j + 15], outline=srgb((0.05, 0.08, 0.12)))
            if (i // 16 + 3 * (j // 16)) % 7 == 0: d.rectangle([i + 4, j + 4, i + 11, j + 11], fill=srgb((0.55, 0.40, 0.12)))
    save_tex("crypt", im)
    # kaide: valkoinen marmori, läpimurtokuvio maalattuna (u = yksi kenttä, v = kaiteen korkeus)
    im = to_img(marble(n, (0.80, 0.80, 0.77), 6, 0.03)); d = ImageDraw.Draw(im); hole = srgb((0.07, 0.08, 0.09)); edge = srgb((0.48, 0.48, 0.46))
    for (x0, y0, x1, y1) in ((30, 54, 122, 150), (134, 54, 226, 150), (82, 128, 174, 214)):
        d.ellipse([x0, y0, x1, y1], fill=hole, outline=edge, width=4); d.ellipse([x0 + 24, y0 + 24, x1 - 24, y1 - 24], fill=srgb((0.80, 0.80, 0.77)), outline=edge, width=3)
    for cx in (0, 256): d.ellipse([cx - 22, 150, cx + 22, 206], fill=hole, outline=edge, width=4)
    d.rectangle([0, 0, n, 34], fill=srgb((0.84, 0.84, 0.81))); d.line([(0, 36), (n, 36)], fill=edge, width=4); d.rectangle([0, n - 28, n, n], fill=srgb((0.84, 0.84, 0.81))); d.line([(0, n - 30), (n, n - 30)], fill=edge, width=4)
    save_tex("balu", im)
    # syvennyksen portaali: valkoinen marmori, suippokaariaukko pimeään
    W, H = 256, 384; a = marble(384, (0.82, 0.82, 0.79), 8, 0.03)[:H, :W]; im = to_img(a); d = ImageDraw.Draw(im)
    arch = [(70, H), (70, 190)] + [(128 - 58 * cos(t * pi / 24), 190 - 105 * sin(t * pi / 24) ** 0.8) for t in range(1, 12)] + [(128, 78)]
    arch = arch + [(256 - x, y) for x, y in reversed(arch[:-1])]
    d.polygon(arch, fill=srgb((0.015, 0.02, 0.025))); d.line(arch + [arch[0]], fill=srgb((0.45, 0.45, 0.43)), width=6)
    off = [(128 + (x - 128) * 1.22, H - (H - y) * 1.12) for x, y in arch]; d.line(off, fill=srgb((0.55, 0.55, 0.53)), width=3)
    save_tex("portal", im)
    # ulko-ovi: tumma pronssi, kehyskentät (reliefien aiheita ei ole jäljitelty)
    im = to_img(flat(n, (0.16, 0.11, 0.05), 9, 0.15, 10)); d = ImageDraw.Draw(im)
    for i in range(2):
        for j in range(4):
            d.rectangle([14 + i * 128, 12 + j * 62, 114 + i * 128, 62 + j * 62], outline=srgb((0.32, 0.23, 0.09)), width=4); d.rectangle([24 + i * 128, 20 + j * 62, 104 + i * 128, 54 + j * 62], fill=srgb((0.20, 0.15, 0.07)))
    d.line([(128, 0), (128, n)], fill=srgb((0.03, 0.02, 0.01)), width=5); d.ellipse([112, 120, 124, 132], fill=srgb((0.55, 0.42, 0.15))); d.ellipse([132, 120, 144, 132], fill=srgb((0.55, 0.42, 0.15)))
    save_tex("bronze", im)
    # freskojen paikat: abstraktit väripinnat (maa, taivas, vesi), tumma kehys. EI kopioita.
    def field(seed, cols, w=384, h=224):
        yy = np.linspace(0, 1, h)[:, None]; nz = fnoise(512, seed, 3, 6)[:h, :w]; nz2 = fnoise(512, seed + 1, 9)[:h, :w]
        t = np.clip(yy + 0.16 * nz, 0, 1); a = np.zeros((h, w, 3))
        for k in range(len(cols) - 1):
            lo, hi = k / (len(cols) - 1), (k + 1) / (len(cols) - 1); m = np.clip((t - lo) / (hi - lo), 0, 1)[..., None] * ((t >= lo)[..., None])
            a = np.where((t >= lo)[..., None], np.array(cols[k]) * (1 - m) + np.array(cols[k + 1]) * m, a)
        a *= (1 + 0.10 * nz2)[..., None]
        im = to_img(a).filter(ImageFilter.GaussianBlur(1.2)); d = ImageDraw.Draw(im); d.rectangle([0, 0, w - 1, h - 1], outline=srgb((0.16, 0.11, 0.06)), width=9); d.rectangle([9, 9, w - 10, h - 10], outline=srgb((0.50, 0.38, 0.14)), width=3)
        return im
    save_tex("fresco1", field(41, [(0.42, 0.50, 0.58), (0.62, 0.60, 0.50), (0.50, 0.36, 0.20), (0.24, 0.20, 0.13)]))
    save_tex("fresco2", field(43, [(0.55, 0.45, 0.30), (0.60, 0.50, 0.32), (0.30, 0.36, 0.24), (0.16, 0.20, 0.16)]))
    save_tex("fresco3", field(47, [(0.30, 0.38, 0.50), (0.50, 0.52, 0.52), (0.42, 0.40, 0.30), (0.20, 0.16, 0.12)]))
    save_tex("frescot", field(53, [(0.50, 0.58, 0.50), (0.36, 0.48, 0.34), (0.26, 0.38, 0.26), (0.16, 0.26, 0.18)], 192, 384))
    # ikkunat: kaksi lansettia vinoruutulasilla, kärjessä kolme pyörölasia, kiviristikko
    W, H = 224, 640; a = np.ones((H, W, 3)) * np.array((0.74, 0.80, 0.84))[None, None, :] * (1 + 0.10 * fnoise(640, 31, 14)[:H, :W, None])
    im = to_img(a); d = ImageDraw.Draw(im); st = (206, 206, 198)
    for k in range(-H, W + H, 26): d.line([(k, 0), (k + H, H)], fill=lead, width=2); d.line([(k, 0), (k - H, H)], fill=lead, width=2)
    top = 190
    d.rectangle([0, 0, W, top], fill=st)
    for (cx, cy, r) in ((W / 2, 62, 46), (W / 4 + 4, 140, 38), (3 * W / 4 - 4, 140, 38)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(196, 212, 222), outline=lead, width=3)
        for k in range(6): d.line([(cx, cy), (cx + r * cos(k * pi / 3), cy + r * sin(k * pi / 3))], fill=lead, width=2)
        d.ellipse([cx - r * 0.35, cy - r * 0.35, cx + r * 0.35, cy + r * 0.35], fill=(214, 190, 120), outline=lead, width=2)
    d.rectangle([W / 2 - 7, top, W / 2 + 7, H], fill=st); d.rectangle([0, 0, W - 1, H - 1], outline=st, width=9)
    for y in range(top + 90, H, 90): d.line([(0, y), (W, y)], fill=(70, 74, 80), width=3)
    save_tex("glass_m", im)

def build():
    corner = lambda k: (RC * cos(radians(k * 45 - 22.5)), RC * sin(radians(k * 45 - 22.5)))
    L = math.dist(corner(0), corner(1)); bands = ((1.1, "mdado"), (1e9, "marble")); top = lambda s: ZS + 0.02
    for k in range(8):
        p0, p1 = corner(k), corner(k + 1); an = radians(k * 45); nx, ny = cos(an), sin(an); tx, ty = -ny, nx
        P = lambda s, z, off=0.0: (AP * nx + tx * (s - L / 2) - nx * off, AP * ny + ty * (s - L / 2) - ny * off, z)
        if k == 0:                                             # syvennys: portaali, risti, korkea maalauskenttä
            wall(p0, p1, top, (0, 0), bands=bands)
            G.box(AP - 0.55, AP, -1.15, 1.15, 0, 3.5, "marble", skip="z-x+")
            G.face([(AP - 0.56, -1.0, 0), (AP - 0.56, 1.0, 0), (AP - 0.56, 1.0, 3.3), (AP - 0.56, -1.0, 3.3)], "portal", uv=[(1, 0), (0, 0), (0, 1), (1, 1)], toward=(0, 0, 2))
            for sx in (AP - 0.6, AP - 0.2):
                G.face([(sx, -1.35, 3.5), (sx, 1.35, 3.5), (sx, 0, 4.9)], "marble", toward=(0 if sx < AP - 0.4 else 20, 0, 4))
            for sy in (-1, 1): G.face([(AP - 0.6, sy * 1.35, 3.5), (AP - 0.2, sy * 1.35, 3.5), (AP - 0.2, 0, 4.9), (AP - 0.6, 0, 4.9)], "marble", toward=(AP - 0.4, sy * 3, 8))
            G.box(AP - 0.46, AP - 0.34, -0.06, 0.06, 4.85, 5.75, "marble"); G.box(AP - 0.46, AP - 0.34, -0.3, 0.3, 5.3, 5.42, "marble")
            n = 10; z0, z1, hw, rise = 5.0, 7.6, 0.85, 1.15
            for i in range(n):
                ya, yb = -hw + 2 * hw * i / n, -hw + 2 * hw * (i + 1) / n; ha, hb = z1 + parch(ya, hw, rise), z1 + parch(yb, hw, rise)
                uv = [(1 - (ya + hw) / (2 * hw), 0), (1 - (yb + hw) / (2 * hw), 0), (1 - (yb + hw) / (2 * hw), (hb - z0) / (z1 + rise - z0)), (1 - (ya + hw) / (2 * hw), (ha - z0) / (z1 + rise - z0))]
                G.face([(AP - 0.03, ya, z0), (AP - 0.03, yb, z0), (AP - 0.03, yb, hb), (AP - 0.03, ya, ha)], "frescot", uv=uv, toward=(0, 0, 6))
            COL["seg"].append([AP - 0.5, -1.2, AP - 0.5, 1.2, 0.2])
        elif k == 4:                                           # sisäänkäynti: pronssiovet, yläpuolella ikkuna
            wall(p0, p1, top, (0, 0), [Win(L / 2, 1.5, 4.8, 7.2, 1.0, "glass_m")], bands=bands)
            G.face([P(L / 2 - 1.0, 0, 0.04), P(L / 2 + 1.0, 0, 0.04), P(L / 2 + 1.0, 3.0, 0.04), P(L / 2 - 1.0, 3.0, 0.04)], "bronze", uv=[(0, 0), (1, 0), (1, 1), (0, 1)], toward=(0, 0, 1.5))
            for s0, s1, za, zb in ((L / 2 - 1.18, L / 2 - 1.0, 0, 3.2), (L / 2 + 1.0, L / 2 + 1.18, 0, 3.2), (L / 2 - 1.18, L / 2 + 1.18, 3.0, 3.2)):
                q = [P(s0, za, 0.1), P(s1, za, 0.1), P(s1, zb, 0.1), P(s0, zb, 0.1)]; G.face(q, "marble", toward=(0, 0, 1.5))
        else:                                                  # ikkunaseinät: korkea ikkuna, alla maalauskenttä
            wall(p0, p1, top, (0, 0), [Win(L / 2, 1.9, 4.1, 7.5, 1.35, "glass_m")], bands=bands)
            fm = "fresco%d" % (1 + (k % 3))
            G.face([P(L / 2 - 1.5, 1.55, 0.03), P(L / 2 + 1.5, 1.55, 0.03), P(L / 2 + 1.5, 3.45, 0.03), P(L / 2 - 1.5, 3.45, 0.03)], fm, uv=[(0, 0), (1, 0), (1, 1), (0, 1)], toward=(0, 0, 2.5))
        cx, cy = p0; ang = math.atan2(-cy, -cx)                # kulmapylväs
        G.cyl(cx, cy, 0, 1.1, 0.24, 8, "mdado", ang - 1.9, ang + 1.9); G.cyl(cx, cy, 1.1, ZS - 0.3, 0.15, 8, "ribm", ang - 1.9, ang + 1.9)
        G.cyl(cx, cy, ZS - 0.3, ZS + 0.05, 0.16, 8, "gold", ang - 1.9, ang + 1.9, r1=0.3)
        COL["circ"].append([cx, cy, 0.3])
    # lattia aukon ympärillä, kaide
    N = 32; rb = lambda a: AP / cos(((a + pi / 8) % (pi / 4)) - pi / 8)
    for i in range(N):
        a0, a1 = 2 * pi * i / N, 2 * pi * (i + 1) / N
        G.face([(RH * cos(a0), RH * sin(a0), 0), (rb(a0) * cos(a0), rb(a0) * sin(a0), 0), (rb(a1) * cos(a1), rb(a1) * sin(a1), 0), (RH * cos(a1), RH * sin(a1), 0)], "mfloor", up=True)
        for r, out in ((RH + 0.09, True), (RH - 0.09, False)):
            p = [(r * cos(a0), r * sin(a0), 0), (r * cos(a1), r * sin(a1), 0), (r * cos(a1), r * sin(a1), 1.0), (r * cos(a0), r * sin(a0), 1.0)]
            uv = [(i * 0.5, 0), (i * 0.5 + 0.5, 0), (i * 0.5 + 0.5, 1), (i * 0.5, 1)]
            if out: G.face(p, "balu", uv=uv, away=(0, 0, 0.5))
            else: G.face(p, "balu", uv=uv, toward=(0, 0, 0.5))
        G.face([((RH - 0.13) * cos(a0), (RH - 0.13) * sin(a0), 1.0), ((RH + 0.13) * cos(a0), (RH + 0.13) * sin(a0), 1.0), ((RH + 0.13) * cos(a1), (RH + 0.13) * sin(a1), 1.0), ((RH - 0.13) * cos(a1), (RH - 0.13) * sin(a1), 1.0)], "sarco", up=True)
        # krypta: aukon reuna, katto, seinä, lattia
        r0, r1 = RH - 0.09, 3.3
        G.face([(r0 * cos(a0), r0 * sin(a0), -0.3), (r0 * cos(a1), r0 * sin(a1), -0.3), (r0 * cos(a1), r0 * sin(a1), 0), (r0 * cos(a0), r0 * sin(a0), 0)], "marble", toward=(0, 0, -0.15))
        G.face([(r0 * cos(a0), r0 * sin(a0), -0.3), (r1 * cos(a0), r1 * sin(a0), -0.3), (r1 * cos(a1), r1 * sin(a1), -0.3), (r0 * cos(a1), r0 * sin(a1), -0.3)], "marble", up=False)
        G.face([(r1 * cos(a0), r1 * sin(a0), ZC), (r1 * cos(a1), r1 * sin(a1), ZC), (r1 * cos(a1), r1 * sin(a1), -0.3), (r1 * cos(a0), r1 * sin(a0), -0.3)], "crypt", toward=(0, 0, -2))
        G.face([(0, 0, ZC), (r1 * cos(a0), r1 * sin(a0), ZC), (r1 * cos(a1), r1 * sin(a1), ZC)], "cfloor", up=True)
    COL["circ"].append([0, 0, RH + 0.14])
    # sarkofagi kryptassa (valkoinen marmori), akseli kohti syvennystä
    G.box(-1.35, 1.35, -0.62, 0.62, ZC, ZC + 0.22, "sarco", skip="z-"); G.box(-1.15, 1.15, -0.48, 0.48, ZC + 0.22, ZC + 0.95, "sarco", skip="z-")
    G.box(-1.22, 1.22, -0.54, 0.54, ZC + 0.95, ZC + 1.08, "sarco", skip="z-")
    for sy in (-1, 1): G.face([(-1.15, sy * 0.48, ZC + 1.08), (1.15, sy * 0.48, ZC + 1.08), (1.05, 0, ZC + 1.3), (-1.05, 0, ZC + 1.3)], "sarco", up=True)
    for sx in (-1, 1): G.face([(sx * 1.15, -0.48, ZC + 1.08), (sx * 1.15, 0.48, ZC + 1.08), (sx * 1.05, 0, ZC + 1.3)], "sarco", away=(0, 0, ZC + 1.1))
    # holvi: kahdeksanlohkoinen suippoholvi, ruoteet kulmista keskelle, kultainen ruusuke
    nr = [(cos(radians(k * 45)), sin(radians(k * 45))) for k in range(8)]
    hv = lambda x, y: ZS + parch(max(x * n[0] + y * n[1] for n in nr), AP, RV)
    for k in range(8):
        p0, p1 = corner(k), corner(k + 1); M = 8
        for j in range(M):
            for i in range(M):
                def pt(jj, ii):
                    r = jj / M; x, y = (p0[0] + (p1[0] - p0[0]) * ii / M) * r, (p0[1] + (p1[1] - p0[1]) * ii / M) * r; return (x, y, hv(x, y))
                q = [pt(j, i), pt(j + 1, i), pt(j + 1, i + 1), pt(j, i + 1)]
                if j == 0: G.face(q[1:], "vaultm", up=False)
                else: G.face(q[:3], "vaultm", up=False); G.face([q[0], q[2], q[3]], "vaultm", up=False)
        G.sweep([(p0[0] * r / 12, p0[1] * r / 12, hv(p0[0] * r / 12 * 0.999, p0[1] * r / 12 * 0.999)) for r in range(13)], 0.18, 0.2, "ribm", (0, 0, 6))
        mx, my = AP * nr[k][0], AP * nr[k][1]
        G.sweep([(mx * r / 12, my * r / 12, hv(mx * r / 12, my * r / 12)) for r in range(2, 13)], 0.1, 0.08, "ribm", (0, 0, 6))
    G.cyl(0, 0, ZS + RV - 0.35, ZS + RV - 0.1, 0.7, 12, "gold", r1=0.45); G.face([(0.7 * cos(i * pi / 6), 0.7 * sin(i * pi / 6), ZS + RV - 0.35) for i in range(12)], "gold", up=False)
    return [(0, 0, -0.9, 0.5), (0, 0, 7.0, 0.35)]                 # valot: krypta ja hallin heikko täytevalo

if __name__ == "__main__":
    textures()
    LAMPS = build()
    print(len(G.F), "pintaa,", len(COL["seg"]), "janaa,", len(COL["circ"]), "ympyrää")
    objs = K.make_scene(LAMPS)
    if A.shots: K.shots(V=dict(ovelta=((-3.6, 0.0, 1.7), (4, 0, 4.2), 16), ylos=((-3.0, 1.5, 1.7), (1.5, -0.5, 12), 16), krypta=((-2.6, 0.6, 1.75), (0.3, 0, -3.2), 18)))
    LMAX = 2.0
    if not A.nobake: LMAX = K.finish_lm(K.bake(objs))
    K.export(objs)
    meta = dict(col=COL, lmax=LMAX, xw=-AP, xe=AP, hw=AP, py=0.0, xs0=1e6, flz=0.0, spawn=[-AP + 1.3, 0.0], exit=[-AP + 0.4, 1.2],
                room=[[RC * cos(radians(k * 45 - 22.5)), RC * sin(radians(k * 45 - 22.5))] for k in range(8)])
    json.dump(meta, open("%s/%s.json" % (OUT, K.NAME), "w"))
