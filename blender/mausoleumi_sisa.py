# -*- coding: utf-8 -*-
"""
Juseliuksen mausoleumin sisätila (19.11.2026): kahdeksankulmainen halli, korkeat ruusukeikkunat, freskokentät, keskellä
pyöreä aukko kaiteineen ja sen alla krypta sarkofageineen, holvi ruoteineen.

Ajo:  python3 blender/mausoleumi_sisa.py --out DIR [--lm 2048] [--samples 40] [--shots] [--nobake]
      python3 tools/sisa_to_js.py DIR mausoleumi_sisa        (pelikansiossa -> mausoleumi_sisa.js)
Käyttää kirkko_sisa.py:n työkaluja (Geo, wall, valokartan leivonta, vienti).

Koordinaatit: X = ovelta kohti vastapäistä syvennystä, Y = vasemmalle, Z = ylös, origo hallin keskellä lattialla.
Pelissä: ulkomallin (bl_mausoleumi.js) keskipiste (-1947.81, 193.18), X-akseli suuntaan 166° (ovi on mallin itäsivulla).
Sisäkuvista (jalkipeli.net ym.) on luettu vain rakenne, värit ja materiaalit. Maalauskentissä on Akseli Gallen-Kallelan freskojen
esityöt/teokset (blender/tex_art/gk_*.jpg, public domain, Wikimedia Commons; omistajan lupa 19.11.2026), varalla omat piirrokset.
Pronssiovien reliefejä ei ole jäljitelty.
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
           portal=(1, 0), bronze=(1, 0), fresco1=(1, 0), fresco2=(1, 0), fresco3=(1, 0), fresco4=(1, 0), fresco5=(1, 0), fresco6=(1, 0), frescot=(1, 0), gold=(1.0, 0), sarco=(1.5, 0),
           glass_m=(1, 5.0), reveal=(2.0, 0.5))
K.MATDEF.clear(); K.MATDEF.update(MAT); K.MI.clear(); K.MI.update({k: i for i, k in enumerate(MAT)})

def marble(n, base, seed, vein=0.10):
    a = flat(n, base, seed, 0.03, 4)
    v = np.abs(fnoise(n, seed + 7, 5, 9) + 0.6 * fnoise(n, seed + 8, 16)); v = np.clip(1 - v / 0.22, 0, 1) ** 2
    return a * (1 - vein * v[..., None] * np.array([1.0, 0.95, 0.85])[None, None, :] * 3)

def frescoes():
    """Kuusi maalauskenttää ja syvennyksen korkea kenttä. Piirretään 2x koossa tasaisin väripinnoin ja tummin ääriviivoin, päälle rakeisuus."""
    W, H, S = 480, 304, 2
    OL = (38, 30, 24)
    def canvas(w=W, h=H): im = Image.new("RGB", (w * S, h * S)); return im, ImageDraw.Draw(im)
    def P(pts): return [(x * S, y * S) for x, y in pts]
    def poly(d, pts, fill, ol=OL, w=2): d.polygon(P(pts), fill=fill); d.line(P(pts) + P(pts[:1]), fill=ol, width=w * S) if ol else None
    def ell(d, x0, y0, x1, y1, fill, ol=OL, w=2): d.ellipse([x0 * S, y0 * S, x1 * S, y1 * S], fill=fill, outline=ol, width=w * S if ol else 0)
    def band(d, y0, y1, c0, c1, w=W):
        for y in range(int(y0 * S), int(y1 * S)):
            t = (y / S - y0) / max(1e-6, y1 - y0); d.line([(0, y), (w * S, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(c0, c1)))
    def person(d, x, y, h, skin, cloth, lean=0.0, sit=False, arm=0.0, legs=None, hair=(60, 40, 25)):
        """Yksinkertainen hahmo: jalat maassa (x, y), pituus h; lean = kumarrus, arm = käden kohotus."""
        u = h / 8.0; legs = legs or cloth; hx = x + lean * 3 * u; top = y - (5.2 * u if sit else 7 * u)
        if sit: poly(d, [(x - 1.2 * u, y - 2.2 * u), (x + 2.6 * u, y - 2.4 * u), (x + 2.9 * u, y), (x + 1.8 * u, y), (x + 1.5 * u, y - 1.2 * u), (x - 1.0 * u, y - 0.9 * u)], legs)
        else: poly(d, [(x - 0.9 * u, y - 3.6 * u), (x + 0.9 * u, y - 3.6 * u), (x + 1.0 * u, y), (x + 0.2 * u, y), (x, y - 2.4 * u), (x - 0.3 * u, y), (x - 1.1 * u, y)], legs)
        by = y - (2.2 * u if sit else 3.6 * u)
        poly(d, [(x - 1.0 * u, by), (x + 1.0 * u, by), (hx + 1.1 * u, top + 1.2 * u), (hx - 1.1 * u, top + 1.2 * u)], cloth)
        ax, ay = hx + (1.0 + 1.6 * abs(lean) + 0.6) * u * (1 if lean >= 0 else -1), top + (3.2 - 2.6 * arm) * u
        d.line(P([(hx + 0.8 * u * (1 if lean >= 0 else -1), top + 1.5 * u), (ax, ay)]), fill=OL, width=int(0.75 * u * S)); d.line(P([(hx + 0.8 * u * (1 if lean >= 0 else -1), top + 1.5 * u), (ax, ay)]), fill=skin, width=int(0.5 * u * S))
        ell(d, hx - 0.62 * u, top - 0.1 * u, hx + 0.62 * u, top + 1.25 * u, skin); d.pieslice([(hx - 0.68 * u) * S, (top - 0.2 * u) * S, (hx + 0.68 * u) * S, (top + 1.1 * u) * S], 180, 360, fill=hair)
    def finish(im, w=W, h=H, seed=1, frame=True):
        im = im.resize((w, h), Image.LANCZOS)
        a = np.asarray(im).astype(np.float32) / 255; g = fnoise(512, seed, 40)[:h, :w, None] * 0.035 + fnoise(512, seed + 3, 6)[:h, :w, None] * 0.03
        a = np.clip(a * (0.94 + g) + 0.01, 0, 1); im = Image.fromarray((a * 255).astype(np.uint8)); d = ImageDraw.Draw(im)
        if frame: d.rectangle([0, 0, w - 1, h - 1], outline=(52, 38, 22), width=9); d.rectangle([9, 9, w - 10, h - 10], outline=(150, 118, 52), width=3)
        return im
    R = {}
    # omistaja 19.11.2026: "voidaan käyttää oikeita" -> blender/tex_art/gk_*.jpg (Akseli Gallen-Kallela 1901-03, esityöt ja teokset, public domain,
    # Wikimedia Commons / Kansallisgalleria). Jos tiedostot puuttuvat, käytetään alla olevia omia piirroksia.
    art = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tex_art")
    names = dict(fresco1="gk_kevat", fresco2="gk_rakennus", fresco3="gk_tuonela", fresco4="gk_havitys", fresco5="gk_talvi", fresco6="gk_syksy", frescot="gk_kosmos")
    if all(os.path.exists("%s/%s.jpg" % (art, v)) for v in names.values()):
        for k, v in names.items():
            im = Image.open("%s/%s.jpg" % (art, v)).convert("RGB"); im = im.resize((512, 266) if k != "frescot" else (212, 512), Image.LANCZOS); d = ImageDraw.Draw(im)
            if k != "frescot": d.rectangle([0, 0, im.width - 1, im.height - 1], outline=(52, 38, 22), width=7); d.rectangle([7, 7, im.width - 8, im.height - 8], outline=(150, 118, 52), width=2)
            R[k] = im
        return R
    skin, skin2, white, blue = (214, 170, 132), (196, 150, 112), (226, 220, 204), (62, 84, 120)
    # 1 Kevät: vaalea niitty, koivut, valkopukuiset naiset ja lapsi kukkia poimimassa
    im, d = canvas(); band(d, 0, 120, (176, 204, 220), (222, 230, 214)); band(d, 120, H, (150, 188, 96), (96, 142, 66))
    poly(d, [(0, 128), (120, 104), (260, 118), (400, 100), (W, 116), (W, 140), (0, 146)], (104, 148, 110), None)
    rng = np.random.default_rng(4)
    for x in (40, 118, 300, 372, 446):
        poly(d, [(x - 6, H), (x - 3, 0), (x + 4, 0), (x + 7, H)], (232, 230, 220))
        for y in range(14, H, 30): d.line(P([(x - 4, y + rng.integers(0, 12)), (x + 3, y + rng.integers(0, 12))]), fill=(40, 36, 32), width=3 * S)
        for k in range(26): cx, cy = x + rng.integers(-46, 46), rng.integers(0, 84); ell(d, cx - 7, cy - 4, cx + 7, cy + 4, (176, 204, 92) if k % 3 else (140, 180, 70), None)
    for k in range(70): cx, cy = rng.integers(10, W - 10), rng.integers(170, H - 14); ell(d, cx - 2, cy - 2, cx + 2, cy + 2, [(246, 226, 110), (250, 250, 240), (226, 150, 170)][k % 3], None)
    person(d, 196, 270, 150, skin, white, lean=0.25, arm=0.2, hair=(120, 84, 40)); person(d, 262, 262, 136, skin, (236, 226, 190), lean=-0.5, arm=-0.2, hair=(90, 60, 30)); person(d, 150, 276, 78, skin, (200, 214, 226), lean=0.6, hair=(190, 150, 80))
    R["fresco1"] = finish(im, seed=1)
    # 2 Rakennus: hirsikehikko, vasemmalla äiti ja lapsi, oikealla veistäjät, taustalla mäntymetsä
    im, d = canvas(); band(d, 0, 110, (150, 160, 150), (120, 136, 110)); band(d, 110, H, (150, 124, 78), (120, 96, 60))
    for x in range(-10, W, 34): poly(d, [(x, 110), (x + 17, 18 + (x * 7) % 30), (x + 34, 110)], (52, 76, 56), None)
    for i in range(6):                                  # hirsikerrat viistossa perspektiivissä
        y = 214 - i * 27; poly(d, [(150, y), (392, y - 18), (392, y - 42), (150, y - 25)], (212, 172, 96) if i % 2 else (198, 156, 84))
        ell(d, 138, y - 27, 162, y + 2, (226, 190, 116)); poly(d, [(392, y - 18), (470, y - 2), (470, y - 26), (392, y - 42)], (176, 136, 72))
    for k in range(40): cx, cy = rng.integers(120, 470), rng.integers(232, 290); poly(d, [(cx, cy), (cx + 9, cy - 3), (cx + 11, cy + 2)], (232, 204, 140), None)
    person(d, 62, 286, 150, skin, (150, 60, 46), sit=True, legs=blue, lean=0.15, hair=(50, 34, 24)); ell(d, 84, 196, 110, 220, skin); poly(d, [(80, 214), (116, 210), (122, 236), (84, 240)], white)
    person(d, 428, 282, 156, skin2, white, lean=-0.6, arm=-0.1, legs=(96, 90, 80), hair=(70, 50, 30)); d.line(P([(380, 208), (350, 250)]), fill=(70, 56, 40), width=4 * S)
    person(d, 300, 116, 110, skin2, white, lean=0.5, arm=0.5, legs=(110, 100, 86)); 
    R["fresco2"] = finish(im, seed=2)
    # 3 Tuonelan joella: tumma virta, vene etualalla, rannalla vaalea ihmisjoukko astumassa veneeseen
    im, d = canvas(); band(d, 0, 96, (120, 124, 130), (158, 150, 140)); poly(d, [(0, 96), (160, 80), (330, 92), (W, 76), (W, 120), (0, 120)], (44, 52, 50), None)
    band(d, 112, H, (40, 54, 70), (16, 22, 34))
    for k in range(26): y = 124 + k * 7; d.line(P([(rng.integers(0, 200), y), (rng.integers(240, W), y + rng.integers(-3, 3))]), fill=(60, 78, 98), width=S)
    poly(d, [(250, H), (300, 196), (W, 168), (W, H)], (116, 100, 78))
    pale = (222, 200, 172)
    for i, (x, y, h, ln) in enumerate(((330, 262, 150, -0.35), (380, 244, 150, -0.15), (424, 232, 144, 0.0), (456, 222, 132, 0.1), (300, 280, 120, -0.75))):
        person(d, x, y, h, pale, (206, 186, 160) if i % 2 else (190, 168, 146), lean=ln, arm=0.1 * i, legs=(196, 176, 150), hair=[(60, 40, 26), (150, 110, 60), (40, 30, 24)][i % 3])
    poly(d, [(18, 250), (60, 286), (236, 290), (286, 240), (262, 236), (226, 262), (70, 258), (40, 238)], (112, 66, 36)); poly(d, [(60, 286), (236, 290), (226, 262), (70, 258)], (84, 48, 28))
    person(d, 150, 262, 138, (206, 176, 146), (120, 100, 84), lean=0.7, arm=-0.2, hair=(40, 30, 24)); d.line(P([(196, 190), (120, 300)]), fill=(60, 44, 30), width=4 * S)
    R["fresco3"] = finish(im, seed=3)
    # 4 Hävitys: palanut metsä, kaatuneet rungot ja juurakot, punainen taivas
    im, d = canvas(); band(d, 0, 150, (120, 36, 26), (232, 132, 52)); band(d, 150, H, (92, 84, 78), (52, 48, 46))
    poly(d, [(0, 150), (100, 132), (240, 146), (380, 126), (W, 142), (W, 164), (0, 166)], (58, 40, 36), None)
    for x, h in ((36, 150), (96, 96), (210, 170), (330, 120), (410, 186), (452, 104)):
        poly(d, [(x - 7, 200), (x - 3, 200 - h), (x + 2, 196 - h), (x + 8, 200)], (26, 22, 22)); d.line(P([(x, 200 - h * 0.6), (x + 26, 200 - h * 0.8)]), fill=(26, 22, 22), width=3 * S)
    poly(d, [(40, 262), (330, 214), (338, 232), (48, 284)], (44, 36, 32)); poly(d, [(210, 290), (452, 244), (458, 262), (216, 302)], (36, 30, 28))
    for an in range(0, 360, 36): d.line(P([(44, 272), (44 + 40 * cos(radians(an)), 272 + 34 * sin(radians(an)))]), fill=(30, 24, 22), width=5 * S)
    for k in range(18): cx, cy = rng.integers(0, W), rng.integers(170, H); ell(d, cx - 8, cy - 3, cx + 8, cy + 3, (120, 112, 104), None)
    for k in range(9): cx = rng.integers(20, W - 20); poly(d, [(cx - 6, 150), (cx, 120 - rng.integers(0, 30)), (cx + 6, 150)], (246, 178, 60), None)
    R["fresco4"] = finish(im, seed=4)
    # 5 Talvi: lumiset kuuset, sinivalkoinen hiljaisuus
    im, d = canvas(); band(d, 0, 140, (108, 132, 168), (190, 204, 220)); band(d, 140, H, (226, 232, 240), (176, 192, 214))
    for x, base, hh in ((70, 250, 230), (190, 236, 190), (300, 262, 250), (410, 244, 210), (140, 214, 120), (360, 210, 110)):
        for i in range(6):
            y = base - hh + i * hh / 6; wd = 14 + i * hh / 22
            poly(d, [(x - wd, y + hh / 6), (x, y - 6), (x + wd, y + hh / 6)], (44, 70, 70), None)
            ell(d, x - wd * 0.9, y + hh / 6 - 16, x + wd * 0.9, y + hh / 6 + 2, (236, 240, 246), (150, 168, 196), 1)
        ell(d, x - 12, base - hh - 12, x + 12, base - hh + 10, (240, 244, 250), (150, 168, 196), 1)
    for (x0, x1, y) in ((0, 190, 270), (150, 400, 284), (330, W, 266)): ell(d, x0, y - 22, x1, y + 40, (240, 244, 250), (160, 178, 204), 1)
    R["fresco5"] = finish(im, seed=5)
    # 6 Syksy: järvimaisema korkealta, ruskan värit, etualalla viisi ristiä
    im, d = canvas(); band(d, 0, 104, (132, 140, 150), (214, 196, 160)); band(d, 104, 190, (70, 92, 116), (112, 128, 140))
    for (x0, x1, y, c) in ((30, 170, 128, (60, 70, 52)), (220, 330, 146, (72, 76, 50)), (360, W + 20, 120, (56, 66, 50)), (-20, 110, 164, (80, 72, 44))): ell(d, x0, y - 9, x1, y + 9, c, None)
    poly(d, [(0, 104), (90, 92), (200, 100), (330, 88), (W, 98), (W, 110), (0, 112)], (74, 80, 84), None)
    poly(d, [(0, 190), (120, 174), (260, 188), (380, 170), (W, 184), (W, H), (0, H)], (176, 120, 46))
    for k in range(60): cx, cy = rng.integers(0, W), rng.integers(186, H); ell(d, cx - 12, cy - 6, cx + 12, cy + 6, [(206, 150, 50), (186, 92, 40), (150, 110, 44), (222, 180, 70)][k % 4], None)
    for i, x in enumerate((132, 186, 240, 294, 348)):
        y = 276 - (i % 2) * 10; poly(d, [(x - 4, y), (x - 4, y - 70), (x + 4, y - 70), (x + 4, y)], (48, 38, 30)); poly(d, [(x - 18, y - 54), (x + 18, y - 54), (x + 18, y - 46), (x - 18, y - 46)], (48, 38, 30))
    R["fresco6"] = finish(im, seed=6)
    # syvennyksen korkea kenttä: vihreä rinnemaisema, kiemurteleva vaalea polku kohti valoa
    w, h = 200, 420; im, d = canvas(w, h); band(d, 0, 150, (214, 222, 190), (170, 200, 160), w); band(d, 150, h, (96, 140, 92), (52, 96, 62), w)
    ell(d, 70, 30, 130, 90, (246, 240, 204), None)
    poly(d, [(0, 170), (70, 132), (140, 150), (200, 124), (200, 190), (0, 200)], (120, 160, 110), None)
    path = [(88, 420), (120, 360), (70, 310), (118, 260), (84, 216), (104, 182), (98, 160)]
    for (a, b), wd in zip(zip(path, path[1:]), (26, 22, 18, 13, 9, 6)): d.line(P([a, b]), fill=(226, 224, 200), width=wd * S)
    for x, y in ((30, 250), (160, 290), (40, 350), (168, 210)):
        poly(d, [(x - 3, y), (x - 1, y - 60), (x + 2, y - 60), (x + 4, y)], (232, 230, 220)); ell(d, x - 20, y - 86, x + 20, y - 48, (120, 170, 96), None)
    R["frescot"] = finish(im, w, h, seed=7)
    return R

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
    # maalauskentät: alkuperäisiä (Gallen-Kallela 1901-03) MUISTUTTAVAT omat piirrokset - aihe, sommittelun pääpiirteet ja väriala, ei jäljennöksiä
    for k, im in frescoes().items(): save_tex(k, im)
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
            for s0, s1, za, zb in ((L / 2 - 1.18, L / 2 - 1.0, 0, 3.0), (L / 2 + 1.0, L / 2 + 1.18, 0, 3.0), (L / 2 - 1.18, L / 2 + 1.18, 3.0, 3.2)):
                q = [P(s0, za, 0.1), P(s1, za, 0.1), P(s1, zb, 0.1), P(s0, zb, 0.1)]; G.face(q, "marble", toward=(0, 0, 1.5))
        else:                                                  # ikkunaseinät: korkea ikkuna, alla maalauskenttä
            wall(p0, p1, top, (0, 0), [Win(L / 2, 1.9, 4.1, 7.5, 1.35, "glass_m")], bands=bands)
            fm = "fresco%d" % {1: 1, 2: 2, 3: 3, 5: 4, 6: 5, 7: 6}[k]         # Kevät, Rakennus, Tuonelan joella, Hävitys, Talvi, Syksy
            G.face([P(L / 2 - 1.65, 1.6, 0.03), P(L / 2 + 1.65, 1.6, 0.03), P(L / 2 + 1.65, 3.32, 0.03), P(L / 2 - 1.65, 3.32, 0.03)], fm, uv=[(1, 0), (0, 0), (0, 1), (1, 1)], toward=(0, 0, 2.5))   # s kasvaa katsojan oikealta vasemmalle
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
