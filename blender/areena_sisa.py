# -*- coding: utf-8 -*-
"""
Porin jäähallin (Isomäen jäähalli) sisätila (20.11.2026): kaukalo, istumakatsomo pohjoissivulla, seisomakatsomo eteläsivulla, päätykatsomo idässä,
valkoinen katto palkkeineen ja ilmakanavineen, mediakuutio ja jäädytettyjen numeroiden viirit.

Ajo:  python3 blender/areena_sisa.py --out DIR [--lm 2048] [--samples 24] [--shots] [--nobake]
      python3 tools/sisa_to_js.py DIR areena_sisa
Koordinaatit: X = länsiseinän pääovelta kaukalon pituussuuntaan itään (suunta 116°), Y = vasemmalle (pohjoiseen), Z = ylös, origo länsiseinän keskellä.
Pelissä (index.html AREE): origo (-1676.6, -1377.45) = jalanjäljen (city.js b 1975) pisimmän, läntisen seinän keskikohta - sama kohta, jossa ulkomallin punainen sisäänkäynti on.
Lähteet: rakenne ja värit luettu kuvista (Wikimedia Commons "Isomäki Areena inside.jpg" ja "Ässät Pataljoona.jpg", CC BY-SA 4.0, sekä omistajan kuva 20.11.2026);
kuvia ei tallennettu. Tiedot: seisomakatsomo on hallin eteläsivulla (Yle 2012), 6 350 paikkaa.
EI kopioitu: seuran ja mainostajien logot, laitamainokset, jään mainokset, kuution kuva. Viireissä vain numerot (omistajan kuvasta 2, 4, 5, 12, 13, 22).
Arvioitua: kaikki mitat (sovitettu jalanjälkeen 70 x 62 m), kaukalo 56 x 28 m, rivimäärät, käytävät, päätyjen ratkaisu (lännessä avoin sisääntulotasanne), kaukalon portit.
"""
import os, sys, json, math
import numpy as np
from math import sin, cos, pi, radians
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kirkko_sisa as K
from kirkko_sisa import flat, fnoise, to_img, srgb, save_tex, wall
from PIL import Image, ImageDraw, ImageFont
K.NAME = "areena_sisa"; K.LM_REF = 0.60
G, COL, OUT, A = K.G, K.COL, K.OUT, K.A

X0, X1, YN, YS, ZC = 0.5, 70.0, 31.5, -30.5, 14.0      # seinät ja katto
IX0, IX1, IH, IR = 8.0, 64.0, 14.0, 7.5                # jää: päät, puolileveys, kulmasäde
WK = 16.4                                              # katsomon etureuna (kulkuväylä jään ja katsomon välissä 2,4 m)
SX0, SX1 = 8.0, 62.0                                   # sivukatsomoiden päät
NR, RD, RH = 16, 0.8, 0.4                              # istumakatsomo: rivit, syvyys, nousu
NT, TD, TH = 20, 0.6, 0.24                             # seisomakatsomo: askelmat, syvyys, nousu
AIS = (20.0, 35.0, 50.0)                               # istumakatsomon porraskäytävät

MAT = dict(ice=(1, 0), conc=(3.0, 0), redc=(2.0, 0), tread=(2.0, 0), seats=(0.5, 0), seatsb=(0.5, 0), board=(2.0, 0), awall=(3.0, 0), aceil=(3.0, 0), steelw=(2.0, 0), banner=(1, 0),
           black=(2.0, 0), net=(0.2, 0), rail=(1.0, 0), doora=(1, 0), screen=(1, 1.2), lampg=(1, 3.0))
K.MATDEF.clear(); K.MATDEF.update(MAT); K.MI.clear(); K.MI.update({k: i for i, k in enumerate(MAT)})

def font(sz):
    try: return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", sz)
    except Exception: return ImageFont.load_default()

def textures():
    n = 256
    save_tex("conc", to_img(flat(n, (0.20, 0.20, 0.20), 1, 0.06, 6)))
    save_tex("redc", to_img(flat(n, (0.45, 0.03, 0.035), 2, 0.05, 6)))
    save_tex("tread", to_img(flat(n, (0.13, 0.12, 0.12), 3, 0.06, 6)))
    save_tex("awall", to_img(flat(n, (0.50, 0.50, 0.50), 4, 0.03, 6)))
    save_tex("aceil", to_img(flat(n, (0.80, 0.80, 0.78), 5, 0.02, 6)))
    save_tex("steelw", to_img(flat(n, (0.82, 0.82, 0.80), 6, 0.02, 8)))
    save_tex("black", to_img(flat(64, (0.015, 0.015, 0.017), 7, 0.0)))
    save_tex("rail", to_img(flat(64, (0.55, 0.55, 0.55), 8, 0.03, 8)))
    # istuinrivi: tummanpunaiset selkänojat (u = 0,5 m / istuin)
    im = to_img(flat(n, (0.10, 0.012, 0.015), 9, 0.05, 6)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([14, 18, n - 15, n + 30], radius=40, fill=srgb((0.36, 0.035, 0.045)), outline=srgb((0.16, 0.015, 0.02)), width=6)
    save_tex("seats", im)
    im = to_img(flat(n, (0.02, 0.02, 0.022), 19, 0.05, 6)); d = ImageDraw.Draw(im)                     # A-katsomon mustat istuimet
    d.rounded_rectangle([14, 18, n - 15, n + 30], radius=40, fill=srgb((0.055, 0.055, 0.06)), outline=srgb((0.01, 0.01, 0.012)), width=6); save_tex("seatsb", im)
    # laita: valkoinen, keltainen potkulista, punainen yläreuna (v = laidan korkeus 1,1 m)
    im = to_img(flat(n, (0.84, 0.84, 0.82), 10, 0.02, 8)); d = ImageDraw.Draw(im)
    d.rectangle([0, n - 44, n, n], fill=srgb((0.80, 0.62, 0.05))); d.rectangle([0, 0, n, 16], fill=srgb((0.55, 0.03, 0.04))); save_tex("board", im)
    # maaliverkko
    im = Image.new("RGB", (64, 64), (225, 225, 225)); d = ImageDraw.Draw(im)
    for k in range(0, 64, 16): d.line([(k, 0), (k, 64)], fill=(120, 120, 120), width=2); d.line([(0, k), (64, k)], fill=(120, 120, 120), width=2)
    save_tex("net", im)
    # jää: valkoinen, viivat ja ympyrät sääntöjen mukaan, ei mainoksia (u = pituus 56 m, v = leveys 28 m)
    W, H = 1280, 640; a = flat(1280, (0.84, 0.87, 0.90), 11, 0.015, 3)[:H]; im = to_img(a); d = ImageDraw.Draw(im); s = W / 56.0
    red, blue = (196, 30, 40), (30, 70, 170)
    def circ(x, y, r, col, w=4, fill=None): d.ellipse([(x - r) * s, (y - r) * s, (x + r) * s, (y + r) * s], outline=col, width=w, fill=fill)
    d.line([(28 * s, 0), (28 * s, H)], fill=red, width=7)
    for x in (28 - 7.6, 28 + 7.6): d.line([(x * s, 0), (x * s, H)], fill=blue, width=7)
    for x in (4.0, 52.0):
        d.line([(x * s, 0), (x * s, H)], fill=red, width=3); sg = 1 if x < 28 else -1
        d.pieslice([(x - 1.8) * s, (14 - 1.8) * s, (x + 1.8) * s, (14 + 1.8) * s], -90 if sg > 0 else 90, 90 if sg > 0 else 270, fill=(150, 190, 235), outline=red, width=3)
        for y in (14 - 7, 14 + 7): circ(x + sg * 6.0, y, 4.5, red); circ(x + sg * 6.0, y, 0.3, red, fill=red)
    for x in (28 - 6.1, 28 + 6.1):
        for y in (7, 21): circ(x, y, 0.3, red, fill=red)
    circ(28, 14, 4.5, blue); circ(28, 14, 0.15, blue, fill=blue)
    save_tex("ice", im)
    # viirit: punainen pohja, valkoinen numero (omistajan kuvan numerot), ei logoja; kuusi rinnakkain yhdessä kuvassa
    im = Image.new("RGB", (6 * 128, 192), (176, 24, 34)); d = ImageDraw.Draw(im)
    for k, t in enumerate(("22", "13", "12", "5", "4", "2")):
        d.rectangle([k * 128 + 3, 3, k * 128 + 124, 188], outline=(235, 235, 230), width=4); d.text((k * 128 + 64, 90), t, font=font(70), fill=(240, 240, 235), anchor="mm")
    save_tex("banner", im)
    # mediakuution näyttö: tyhjä lämmin liukuväri (valaiseva)
    yy = np.linspace(0, 1, n)[:, None, None]; a = np.array((0.75, 0.30, 0.06))[None, None, :] * (0.6 + 0.6 * yy) * np.ones((n, n, 1)); save_tex("screen", to_img(a))
    save_tex("lampg", Image.new("RGB", (16, 16), (245, 248, 255)))
    im = to_img(flat(n, (0.05, 0.05, 0.055), 12, 0.05, 6)); d = ImageDraw.Draw(im)
    for i in range(2): d.rectangle([14 + i * 128, 14, 114 + i * 128, 150], fill=(120, 140, 150), outline=(15, 15, 15), width=4)
    d.line([(128, 0), (128, n)], fill=(10, 10, 10), width=5); save_tex("doora", im)

def rink():
    """Kaukalon reunaviiva (suljettu murtoviiva) myötäpäivään: suorat sivut ja pyöristetyt kulmat."""
    P = []
    for (cx, cy, a0) in ((IX1 - IR, IH - IR, 0), (IX0 + IR, IH - IR, 90), (IX0 + IR, -IH + IR, 180), (IX1 - IR, -IH + IR, 270)):
        P += [(cx + IR * cos(radians(a0 + 90 * i / 8)), cy + IR * sin(radians(a0 + 90 * i / 8))) for i in range(9)]
    out = []
    for a, b in zip(P, P[1:] + P[:1]):                    # pitkät suorat pätkitään, jotta porttiaukot saadaan keskelle
        L = math.dist(a, b); n = max(1, round(L / 2.2)); out += [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(n)]
    return out

def build():
    LAMPS = []; lev = []
    # --- seinät, lattia, katto
    wb = ((3.0, "redc"), (1e9, "awall")); top = lambda q: ZC
    for a, b in (((X0, YS), (X1, YS)), ((X1, YS), (X1, YN)), ((X1, YN), (X0, YN)), ((X0, YN), (X0, YS))): wall(a, b, top, (35, 0), bands=wb)
    G.face([(X0, YS, 0), (X1, YS, 0), (X1, YN, 0), (X0, YN, 0)], "conc", up=True)
    G.face([(X0, YS, ZC), (X1, YS, ZC), (X1, YN, ZC), (X0, YN, ZC)], "aceil", up=False)
    for dy in (-1.3, 1.3):                                 # pääovet länsiseinässä
        G.face([(X0 + 0.06, dy - 1.1, 0), (X0 + 0.06, dy + 1.1, 0), (X0 + 0.06, dy + 1.1, 2.4), (X0 + 0.06, dy - 1.1, 2.4)], "doora", uv=[(0, 0), (1, 0), (1, 1), (0, 1)], toward=(10, 0, 1))
    # --- jää ja laidat
    R = rink(); uv = lambda p: ((p[0] - IX0) / (IX1 - IX0), (p[1] + IH) / (2 * IH))
    c = ((IX0 + IX1) / 2, 0.0)
    for a, b in zip(R, R[1:] + R[:1]):
        G.face([(c[0], c[1], 0.03), (*a, 0.03), (*b, 0.03)], "ice", uv=[uv(c), uv(a), uv(b)], up=True)
        if abs((a[0] + b[0]) / 2 - c[0]) < 1.2 and abs(abs(a[1]) - IH) < 0.01: continue          # portit pitkien sivujen keskellä
        L = math.dist(a, b)
        for off, kw in ((0.0, dict(toward=(c[0], c[1], 0.5))), (0.12, dict(away=(c[0], c[1], 0.5)))):
            ex = lambda p: (p[0] + (p[0] - c[0]) / math.hypot(p[0] - c[0], p[1] - c[1]) * off, p[1] + (p[1] - c[1]) / math.hypot(p[0] - c[0], p[1] - c[1]) * off)
            G.face([(*ex(a), 0.03), (*ex(b), 0.03), (*ex(b), 1.13), (*ex(a), 1.13)], "board", uv=[(0, 0), (L / 2, 0), (L / 2, 1), (0, 1)], **kw)
        G.face([(*a, 1.13), (*b, 1.13), (b[0] + (b[0] - c[0]) * 0.004, b[1] + (b[1] - c[1]) * 0.008, 1.13), (a[0] + (a[0] - c[0]) * 0.004, a[1] + (a[1] - c[1]) * 0.008, 1.13)], "redc", up=True)
        COL["seg"].append([a[0], a[1], b[0], b[1], 0.1])
        G.small = True; G.cyl(a[0], a[1], 1.13, 2.9, 0.03, 4, "steelw"); G.small = False      # suojalasin pylväät (lasia ei piirretä)
    for gx, sg in ((IX0 + 4.0, 1), (IX1 - 4.0, -1)):       # maalit
        G.small = True
        for y in (-0.92, 0.92): G.cyl(gx, y, 0.03, 1.25, 0.03, 5, "redc")
        G.box(gx - 0.03, gx + 0.03, -0.92, 0.92, 1.22, 1.28, "redc")
        G.face([(gx, -0.92, 1.25), (gx, 0.92, 1.25), (gx - sg * 1.1, 0.92, 0.03), (gx - sg * 1.1, -0.92, 0.03)], "net", toward=(gx - sg * 5, 0, 3)); G.small = False
        COL["seg"].append([gx - sg * 0.5, -0.9, gx - sg * 0.5, 0.9, 0.5])
    # --- istumakatsomo pohjoissivulla (16 riviä, kolme porraskäytävää), ylätasanne
    for k in range(NR):
        y0, z = WK + RD * k, RH * (k + 1)
        G.face([(SX0, y0, z - RH), (SX1, y0, z - RH), (SX1, y0, z), (SX0, y0, z)], "redc" if k == 0 else "tread", toward=(35, 0, z))
        G.face([(SX0, y0, z), (SX1, y0, z), (SX1, y0 + RD, z), (SX0, y0 + RD, z)], "tread", up=True)
        lev.append([SX0, y0, SX1, y0 + RD, z])
        xs = [SX0] + [v for a in AIS for v in (a - 0.7, a + 0.7)] + [SX1]
        for xa, xb in zip(xs[0::2], xs[1::2]):
            n = round((xb - xa) / 0.5)
            G.face([(xa, y0 + 0.62, z + 0.42), (xb, y0 + 0.62, z + 0.42), (xb, y0 + 0.62, z + 0.88), (xa, y0 + 0.62, z + 0.88)], "seatsb", uv=[(0, 0), (n, 0), (n, 1), (0, 1)], toward=(35, 0, z))
            G.face([(xa, y0 + 0.2, z + 0.42), (xb, y0 + 0.2, z + 0.42), (xb, y0 + 0.62, z + 0.42), (xa, y0 + 0.62, z + 0.42)], "black", up=True)
            G.face([(xa, y0 + 0.2, z + 0.42), (xb, y0 + 0.2, z + 0.42), (xb, y0 + 0.3, z + 0.1), (xa, y0 + 0.3, z + 0.1)], "black", toward=(35, 0, z))
        for a in AIS:                                      # väliaskelma porraskäytävässä
            G.box(a - 0.7, a + 0.7, y0 - 0.4, y0, z - RH, z - RH / 2, "conc", skip="z-y+"); lev.append([a - 0.7, y0 - 0.4, a + 0.7, y0, z - RH / 2])
    zt = RH * NR; yt = WK + RD * NR
    G.face([(SX0, yt, zt), (SX1, yt, zt), (SX1, YN, zt), (SX0, YN, zt)], "conc", up=True); lev.append([SX0, yt, SX1, YN, zt])
    for x in (SX0, SX1):                                   # katsomon päädyt
        pts = [(x, WK, 0)] + [p for k in range(NR) for p in ((x, WK + RD * k, RH * (k + 1)), (x, WK + RD * (k + 1), RH * (k + 1)))] + [(x, YN, zt), (x, YN, 0)]
        G.face(pts, "redc", away=(35, 20, 2)); COL["seg"].append([x, WK, x, YN, 0.08])
    # --- eteläsivu (C): keskellä alhaalla SEISOMAKATSOMO (12 matalaa askelmaa, kaiteet), sen yläpuolella ja päissä punaiset istuinrivit (omistajan katsomokartta 20.11.2026)
    TX0, TX1, NTL = 18.0, 54.0, 12; zt0 = TH * NTL; yt0 = WK + TD * NTL
    def seatrow(xa, xb, y0, z, mat="seats"):
        n = round((xb - xa) / 0.5)
        G.face([(xa, y0, z - RH), (xb, y0, z - RH), (xb, y0, z), (xa, y0, z)], "tread", toward=(35, 0, z)); G.face([(xa, y0, z), (xb, y0, z), (xb, y0 - RD, z), (xa, y0 - RD, z)], "tread", up=True)
        G.face([(xa, y0 - 0.62, z + 0.42), (xb, y0 - 0.62, z + 0.42), (xb, y0 - 0.62, z + 0.88), (xa, y0 - 0.62, z + 0.88)], mat, uv=[(0, 0), (n, 0), (n, 1), (0, 1)], toward=(35, 0, z))
        G.face([(xa, y0 - 0.2, z + 0.42), (xb, y0 - 0.2, z + 0.42), (xb, y0 - 0.62, z + 0.42), (xa, y0 - 0.62, z + 0.42)], "redc", up=True)
    for j in range(NTL):
        y0, z = -(WK + TD * j), TH * (j + 1)
        G.face([(TX0, y0, z - TH), (TX1, y0, z - TH), (TX1, y0, z), (TX0, y0, z)], "redc", toward=(35, 0, z))
        G.face([(TX0, y0, z), (TX1, y0, z), (TX1, y0 - TD, z), (TX0, y0 - TD, z)], "redc" if j % 2 else "tread", up=True)
        lev.append([TX0, y0 - TD, TX1, y0, z])
        if j % 4 == 2:
            G.small = True
            for x in np.arange(TX0 + 2, TX1 - 3, 6.0):
                G.box(x, x + 3.0, y0 - 0.33, y0 - 0.27, z + 1.02, z + 1.08, "rail")
                for xx in (x, x + 3.0): G.cyl(xx, y0 - 0.3, z, z + 1.05, 0.03, 4, "rail")
                COL["seg"].append([x, y0 - 0.3, x + 3.0, y0 - 0.3, 0.05])
            G.small = False
    G.face([(TX0, -yt0, zt0), (TX1, -yt0, zt0), (TX1, -yt0 - 1.2, zt0), (TX0, -yt0 - 1.2, zt0)], "conc", up=True); lev.append([TX0, -yt0 - 1.2, TX1, -yt0, zt0])
    COL["seg"].append([TX0, -yt0 - 1.2, TX1, -yt0 - 1.2, 0.06])
    for k in range(8): seatrow(TX0, TX1, -(yt0 + 1.2 + RD * k), zt0 + RH * (k + 1))
    for (xa, xb) in ((SX0, TX0), (TX1, SX1)):
        for k in range(17): seatrow(xa, xb, -(WK + RD * k), RH * (k + 1))
        for x in (xa, xb):
            pts = [(x, -WK, 0)] + [q for k in range(17) for q in ((x, -(WK + RD * k), RH * (k + 1)), (x, -(WK + RD * (k + 1)), RH * (k + 1)))] + [(x, YS, RH * 17), (x, YS, 0)]
            G.face(pts, "redc", toward=((TX0 + TX1) / 2 if x in (TX0, TX1) else x + (x - 35), -20, 1)); COL["seg"].append([x, -WK, x, YS, 0.08])
        COL["seg"].append([xa, -WK, xb, -WK, 0.08])
    # --- päätykatsomot (B lännessä, pääoven kohdalla aukko; D idässä): viisi punaista riviä
    def endstand(xf, sg, ya, yb):
        for k in range(5):
            x0, z = xf + sg * RD * k, RH * (k + 1); x1 = x0 + sg * RD
            G.face([(x0, ya, z - RH), (x0, yb, z - RH), (x0, yb, z), (x0, ya, z)], "redc" if k == 0 else "tread", toward=(35, 0, z)); G.face([(x0, ya, z), (x1, ya, z), (x1, yb, z), (x0, yb, z)], "tread", up=True)
            n = round((yb - ya) / 0.5)
            G.face([(x0 + sg * 0.62, ya, z + 0.42), (x0 + sg * 0.62, yb, z + 0.42), (x0 + sg * 0.62, yb, z + 0.88), (x0 + sg * 0.62, ya, z + 0.88)], "seats", uv=[(0, 0), (n, 0), (n, 1), (0, 1)], toward=(35, 0, z))
            G.face([(x0 + sg * 0.2, ya, z + 0.42), (x0 + sg * 0.62, ya, z + 0.42), (x0 + sg * 0.62, yb, z + 0.42), (x0 + sg * 0.2, yb, z + 0.42)], "redc", up=True)
        xe = xf + sg * RD * 5
        G.face([(xe, ya, 0), (xe, yb, 0), (xe, yb, 2.0), (xe, ya, 2.0)], "redc", away=(xf, 0, 1))
        for y in (ya, yb): G.face([(xf, y, 0), (xe, y, 0), (xe, y, 2.0), (xf + sg * RD * 4, y, 2.0), (xf, y, 0.4)], "redc", away=((xf + xe) / 2, (ya + yb) / 2, 1))
        for (a, b) in (((xf, ya), (xf, yb)), ((xe, ya), (xe, yb)), ((xf, ya), (xe, ya)), ((xf, yb), (xe, yb))): COL["seg"].append([a[0], a[1], b[0], b[1], 0.08])
    endstand(IX1 + 2.4, 1, -13, 13); endstand(IX0 - 2.4, -1, 3.0, 13); endstand(IX0 - 2.4, -1, -13, -3.0)
    # --- katto: poikkipalkit, ilmakanavat, valaisimet
    for x in np.arange(4.0, X1, 6.6):
        G.box(x - 0.2, x + 0.2, YS, YN, ZC - 1.3, ZC, "steelw", skip="z+")
    for y in (-10.0, 10.0):                                # pyöreät ilmakanavat kaukalon pituussuuntaan
        n = 10
        for i in range(n):
            a0, a1 = 2 * pi * i / n, 2 * pi * (i + 1) / n
            G.face([(3, y + 0.55 * cos(a0), ZC - 2.0 + 0.55 * sin(a0)), (X1 - 3, y + 0.55 * cos(a0), ZC - 2.0 + 0.55 * sin(a0)), (X1 - 3, y + 0.55 * cos(a1), ZC - 2.0 + 0.55 * sin(a1)), (3, y + 0.55 * cos(a1), ZC - 2.0 + 0.55 * sin(a1))], "steelw", away=(35, y, ZC - 2.0))
    G.small = True
    for x in np.arange(10.0, 64.0, 8.8):
        for y in (-22.0, -8.0, 8.0, 22.0):
            G.face([(x - 0.5, y - 0.12, ZC - 1.35), (x + 0.5, y - 0.12, ZC - 1.35), (x + 0.5, y + 0.12, ZC - 1.35), (x - 0.5, y + 0.12, ZC - 1.35)], "lampg", uv=[(0.5, 0.5)] * 4, up=False)
            LAMPS.append((x, y, ZC - 1.8, 1500 if abs(y) < 10 else 700, (0.92, 0.96, 1.0)))
    # --- mediakuutio ja viirit
    cx, z0, z1, hw = (IX0 + IX1) / 2, 8.2, 10.6, 2.0
    G.box(cx - hw - 0.1, cx + hw + 0.1, -hw - 0.1, hw + 0.1, z0 - 0.15, z1 + 0.15, "black")
    for (p, q) in (((cx - hw - 0.12, -hw), (cx - hw - 0.12, hw)), ((cx + hw + 0.12, hw), (cx + hw + 0.12, -hw)), ((cx - hw, hw + 0.12), (cx + hw, hw + 0.12)), ((cx + hw, -hw - 0.12), (cx - hw, -hw - 0.12))):
        G.face([(*p, z0), (*q, z0), (*q, z1), (*p, z1)], "screen", uv=[(0, 0), (1, 0), (1, 1), (0, 1)], away=(cx, 0, 9.4))
    for (dx, dy) in ((-1.5, -1.5), (1.5, 1.5), (-1.5, 1.5), (1.5, -1.5)): G.cyl(cx + dx, dy, z1 + 0.15, ZC, 0.02, 4, "black")
    for k in range(6):
        x = 42.0 + 2.2 * k; G.face([(x, 12.0, 9.6), (x + 1.3, 12.0, 9.6), (x + 1.3, 12.0, 11.5), (x, 12.0, 11.5)], "banner", uv=[(k / 6, 0), ((k + 1) / 6, 0), ((k + 1) / 6, 1), (k / 6, 1)], toward=(x, 0, 6))
        G.face([(x, 12.03, 9.6), (x + 1.3, 12.03, 9.6), (x + 1.3, 12.03, 11.5), (x, 12.03, 11.5)], "banner", uv=[((6 - k) / 6, 0), ((5 - k) / 6, 0), ((5 - k) / 6, 1), ((6 - k) / 6, 1)], toward=(x, 40, 6))
        G.cyl(x + 0.65, 12.0, 11.5, ZC - 1.3, 0.01, 3, "black")
    G.small = False
    LAMPS.append((4.0, 0.0, 5.0, 300, (1.0, 0.95, 0.9)))
    return LAMPS, lev

if __name__ == "__main__":
    import bpy
    textures(); LAMPS, LEV = build()
    print(len(G.F), "pintaa,", len(COL["seg"]), "janaa,", len(LEV), "tasoa")
    objs = K.make_scene([])
    for (x, y, z, w, c) in LAMPS:
        l = bpy.data.lights.new("valo", "POINT"); l.energy = w; l.color = c; l.shadow_soft_size = 0.6
        o = bpy.data.objects.new("valo", l); o.location = (x, y, z); bpy.context.scene.collection.objects.link(o)
    if A.shots: K.shots(V=dict(ovelta=((2.0, 0.0, 1.7), (36, 0, 3.0), 16), katsomosta=((35.0, 27.0, 7.6), (36, -6, 0), 16), seisoma=((36.0, -22.0, 4.7), (40, 6, 1.0), 16), jaalta=((30.0, 3.0, 1.7), (40, -20, 3.0), 16)))
    LMAX = 2.0
    if not A.nobake: LMAX = K.finish_lm(K.bake(objs))
    K.export(objs)
    room = [[X0, YS], [X1, YS], [X1, YN], [X0, YN]]
    meta = dict(col=COL, lmax=LMAX, xw=X0, xe=X1, hw=YN, py=0.0, xs0=1e6, flz=0.0, lev=LEV, spawn=[2.2, 0.0], exit=[1.2, 1.6], room=room, rooms=[room], ports=[])
    json.dump(meta, open("%s/%s.json" % (OUT, K.NAME), "w"))
