# -*- coding: utf-8 -*-
"""
Porin jäähallin (Isomäen jäähalli) sisätila (20.11.2026): kaukalo, istumakatsomo pohjoissivulla, seisomakatsomo eteläsivulla, päätykatsomo idässä,
valkoinen katto palkkeineen ja ilmakanavineen, mediakuutio ja jäädytettyjen numeroiden viirit.

Ajo:  python3 blender/areena_sisa.py --out DIR [--lm 2048] [--samples 24] [--shots] [--nobake]
      python3 tools/sisa_to_js.py DIR areena_sisa
Mallinnus: X = länsiseinältä kaukalon pituussuuntaan itään (116°), Y = pohjoiseen. LOPUKSI malli käännetään pelin kehykseen: x = pohjoisen pitkän sivun PÄÄOVELTA
(Karhuhallin puoli, omistaja 20.11.2026) sisään etelään, y = vasemmalle (itään). Pelissä (index.html AREE): origo (-1611.69, -1365.72), x-akseli (-0.4384, -0.8988).
Halli on kaarihalli (kaareva katto kaukalon poikki). Katsomot: A pohjoisessa (mustat alarivit, punaiset ylärivit), SEISOMAKATSOMO etelässä ja C sen PÄÄLLÄ, eteläkulmissa
C1/C5, B-pääty lännessä (ylärivit kioskiaulan päällä), D-pääty idässä (ravintolatasot), koilliskulmassa baari; kaikki istumakatsomot nousevat samaan korkeuteen (10,8 m).
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

X0, X1, YN, YS, ZC = 0.5, 105.5, 39.0, -37.5, 17.0   # seinät ja katto (jalanjälki paikallisesti x 0...104, y -37.7...+47)
IX0, IX1, IH, IR = 22.0, 82.0, 14.0, 7.5               # jää 60 x 28 m: päät, puolileveys, kulmasäde
WK = 16.4                                              # katsomon etureuna (kulkuväylä jään ja katsomon välissä 2,4 m)
SX0, SX1 = IX0 + IR, IX1 - IR                          # sivukatsomoiden suora osa (kulmissa kaarevat kulmakatsomot)
RD, RH = 0.8, 0.45                                     # istuinrivin syvyys ja nousu
NL, NU, CA = 8, 16, 1.4                                # A-katsomo: alarivit (mustat), ylärivit (punaiset), poikkikäytävä
NT, TD, TH = 16, 0.6, 0.24                             # seisomakatsomo: askelmat, syvyys, nousu
BY, BZ, NB, BH = WK + 5.4, 6.4, 10, 0.45               # C-katsomo seisomakatsomon PÄÄLLÄ: etureuna, lattia, rivit, nousu
AIS = (40.0, 66.0)                                     # A-katsomon porraskäytävät
XD, GW = 53.2, 2.6                                     # pääovi pohjoisella pitkällä sivulla (Karhuhallin puoli) ja siitä kaukalolle johtavan käytävän puolileveys
ZE, ZK = 12.6, 19.0                                    # kaarihalli: katon kanta sivuseinillä ja laki
arc = lambda y: ZE + (ZK - ZE) * (1 - ((y - (YN + YS) / 2) / ((YN - YS) / 2)) ** 2)

MAT = dict(ice=(1, 0), conc=(3.0, 0), redc=(2.0, 0), tread=(2.0, 0), seats=(0.5, 0), seatsb=(0.5, 0), board=(2.0, 0), awall=(3.0, 0), aceil=(3.0, 0), steelw=(2.0, 0), banner=(1, 0),
           black=(2.0, 0), net=(0.2, 0), rail=(1.0, 0), doora=(1, 0), white=(2.0, 0), screen=(1, 1.2), lampg=(1, 3.0), menu=(1, 2.0), warm=(2.0, 1.5), led=(2.0, 1.0))
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
    W, H = 1280, 598; a = flat(1280, (0.84, 0.87, 0.90), 11, 0.015, 3)[:H]; im = to_img(a); d = ImageDraw.Draw(im); s = W / 60.0
    red, blue = (196, 30, 40), (30, 70, 170)
    def circ(x, y, r, col, w=4, fill=None): d.ellipse([(x - r) * s, (y - r) * s, (x + r) * s, (y + r) * s], outline=col, width=w, fill=fill)
    d.line([(30 * s, 0), (30 * s, H)], fill=red, width=7)
    for x in (30 - 7.6, 30 + 7.6): d.line([(x * s, 0), (x * s, H)], fill=blue, width=7)
    for x in (4.0, 56.0):
        d.line([(x * s, 0), (x * s, H)], fill=red, width=3); sg = 1 if x < 30 else -1
        d.pieslice([(x - 1.8) * s, (14 - 1.8) * s, (x + 1.8) * s, (14 + 1.8) * s], -90 if sg > 0 else 90, 90 if sg > 0 else 270, fill=(150, 190, 235), outline=red, width=3)
        for y in (14 - 7, 14 + 7): circ(x + sg * 6.0, y, 4.5, red); circ(x + sg * 6.0, y, 0.3, red, fill=red)
    for x in (30 - 6.1, 30 + 6.1):
        for y in (7, 21): circ(x, y, 0.3, red, fill=red)
    circ(30, 14, 4.5, blue); circ(30, 14, 0.15, blue, fill=blue)
    save_tex("ice", im)
    # viirit: punainen pohja, valkoinen numero (omistajan kuvan numerot), ei logoja; kuusi rinnakkain yhdessä kuvassa
    im = Image.new("RGB", (6 * 128, 192), (176, 24, 34)); d = ImageDraw.Draw(im)
    for k, t in enumerate(("22", "13", "12", "5", "4", "2")):
        d.rectangle([k * 128 + 3, 3, k * 128 + 124, 188], outline=(235, 235, 230), width=4); d.text((k * 128 + 64, 90), t, font=font(70), fill=(240, 240, 235), anchor="mm")
    save_tex("banner", im)
    # mediakuution näyttö: tyhjä lämmin liukuväri (valaiseva)
    yy = np.linspace(0, 1, n)[:, None, None]; a = np.array((0.75, 0.30, 0.06))[None, None, :] * (0.6 + 0.6 * yy) * np.ones((n, n, 1)); save_tex("screen", to_img(a))
    save_tex("lampg", Image.new("RGB", (16, 16), (245, 248, 255))); save_tex("white", to_img(flat(64, (0.84, 0.84, 0.82), 21, 0.01, 8)))
    save_tex("led", to_img(flat(n, (0.60, 0.02, 0.03), 23, 0.10, 3)))
    save_tex("menu", Image.new("RGB", (16, 16), (250, 240, 215))); save_tex("warm", to_img(flat(n, (0.80, 0.52, 0.26), 22, 0.10, 3)))
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
    LAMPS = []; lev = []; CXm = (IX0 + IX1) / 2
    # --- seinät, lattia, katto
    wb = ((3.0, "redc"), (1e9, "awall"))
    wall((X0, YS), (X1, YS), lambda q: ZE, (CXm, 0), bands=wb); wall((X1, YN), (X0, YN), lambda q: ZE, (CXm, 0), bands=wb)
    wall((X1, YS), (X1, YN), lambda q: arc(YS + q), (CXm, 0), bands=wb); wall((X0, YN), (X0, YS), lambda q: arc(YN - q), (CXm, 0), bands=wb)
    G.face([(X0, YS, 0), (X1, YS, 0), (X1, YN, 0), (X0, YN, 0)], "conc", up=True)
    ysg = [YS + (YN - YS) * i / 20 for i in range(21)]                                          # kaarihalli: kaareva katto kaukalon poikki, kaarikannattajat 7 m välein
    for ya, yb in zip(ysg, ysg[1:]):
        G.face([(X0, ya, arc(ya)), (X1, ya, arc(ya)), (X1, yb, arc(yb)), (X0, yb, arc(yb))], "aceil", toward=(CXm, 0, 0))
        for x in np.arange(5.0, X1, 7.0):
            G.face([(x - 0.2, ya, arc(ya) - 1.1), (x + 0.2, ya, arc(ya) - 1.1), (x + 0.2, yb, arc(yb) - 1.1), (x - 0.2, yb, arc(yb) - 1.1)], "steelw", toward=(x, 0, 0))
            for sx in (-0.2, 0.2): G.face([(x + sx, ya, arc(ya) - 1.1), (x + sx, yb, arc(yb) - 1.1), (x + sx, yb, arc(yb)), (x + sx, ya, arc(ya))], "steelw", toward=(x + sx * 40, 0, 10))
    for dx in (-1.3, 1.3):                                 # pääovet pohjoisseinässä
        G.face([(XD + dx - 1.1, YN - 0.06, 0), (XD + dx + 1.1, YN - 0.06, 0), (XD + dx + 1.1, YN - 0.06, 2.4), (XD + dx - 1.1, YN - 0.06, 2.4)], "doora", uv=[(0, 0), (1, 0), (1, 1), (0, 1)], toward=(XD, 0, 1))
    # --- jää ja laidat
    R = rink(); uv = lambda p: ((p[0] - IX0) / (IX1 - IX0), (p[1] + IH) / (2 * IH)); c = (CXm, 0.0)
    for a, b in zip(R, R[1:] + R[:1]):
        G.face([(c[0], c[1], 0.03), (*a, 0.03), (*b, 0.03)], "ice", uv=[uv(c), uv(a), uv(b)], up=True)
        if abs((a[0] + b[0]) / 2 - c[0]) < 1.2 and abs(abs(a[1]) - IH) < 0.01: continue          # portit pitkien sivujen keskellä
        L = math.dist(a, b)
        for off, kw in ((0.0, dict(toward=(c[0], c[1], 0.5))), (0.12, dict(away=(c[0], c[1], 0.5)))):
            ex = lambda p: (p[0] + (p[0] - c[0]) / math.hypot(p[0] - c[0], p[1] - c[1]) * off, p[1] + (p[1] - c[1]) / math.hypot(p[0] - c[0], p[1] - c[1]) * off)
            G.face([(*ex(a), 0.03), (*ex(b), 0.03), (*ex(b), 1.13), (*ex(a), 1.13)], "board", uv=[(0, 0), (L / 2, 0), (L / 2, 1), (0, 1)], **kw)
        COL["seg"].append([a[0], a[1], b[0], b[1], 0.1])
        G.small = True; G.cyl(a[0], a[1], 1.13, 2.9, 0.03, 4, "steelw"); G.small = False      # suojalasin pylväät (lasia ei piirretä)
    for gx, sg in ((IX0 + 4.0, 1), (IX1 - 4.0, -1)):       # maalit
        G.small = True
        for y in (-0.92, 0.92): G.cyl(gx, y, 0.03, 1.25, 0.03, 5, "redc")
        G.box(gx - 0.03, gx + 0.03, -0.92, 0.92, 1.22, 1.28, "redc")
        G.face([(gx, -0.92, 1.25), (gx, 0.92, 1.25), (gx - sg * 1.1, 0.92, 0.03), (gx - sg * 1.1, -0.92, 0.03)], "net", toward=(gx - sg * 5, 0, 3)); G.small = False
        COL["seg"].append([gx - sg * 0.5, -0.9, gx - sg * 0.5, 0.9, 0.5])
    def row(xa, xb, y0, z, sg, mat, rise=RH, tread="tread"):
        """Istuinrivi pitkällä sivulla: etureuna y0, nousee poispäin jäästä (sg = +1 pohjoinen, -1 etelä)."""
        n = max(1, round((xb - xa) / 0.5)); Y = lambda d: y0 + sg * d
        G.face([(xa, y0, z - rise), (xb, y0, z - rise), (xb, y0, z), (xa, y0, z)], tread, toward=(CXm, 0, z)); G.face([(xa, y0, z), (xb, y0, z), (xb, Y(RD), z), (xa, Y(RD), z)], tread, up=True)
        G.face([(xa, Y(0.62), z + 0.42), (xb, Y(0.62), z + 0.42), (xb, Y(0.62), z + 0.88), (xa, Y(0.62), z + 0.88)], mat, uv=[(0, 0), (n, 0), (n, 1), (0, 1)], toward=(CXm, 0, z))
        G.face([(xa, Y(0.2), z + 0.42), (xb, Y(0.2), z + 0.42), (xb, Y(0.62), z + 0.42), (xa, Y(0.62), z + 0.42)], "black" if mat == "seatsb" else "redc", up=True)
    # --- A-katsomo (pohjoinen): 9 mustaa alariviä, poikkikäytävä, 12 punaista yläriviä, kolme porraskäytävää; kaikki käveltävissä
    xs = [SX0, AIS[0] - 0.7, AIS[0] + 0.7, XD - GW, XD + GW, AIS[1] - 0.7, AIS[1] + 0.7, SX1]; HALF = ((SX0, XD - GW), (XD + GW, SX1))
    def tier(yf, z0, n, mat):
        for k in range(n):
            y0, z = yf + RD * k, z0 + RH * (k + 1)
            for xa, xb in zip(xs[0::2], xs[1::2]): row(xa, xb, y0, z, 1, mat)
            for (ha, hb) in HALF: lev.append([ha, y0, hb, y0 + RD, z])
            for a in AIS:
                G.face([(a - 0.7, y0, z - RH), (a + 0.7, y0, z - RH), (a + 0.7, y0, z), (a - 0.7, y0, z)], "conc", toward=(CXm, 0, z)); G.face([(a - 0.7, y0, z), (a + 0.7, y0, z), (a + 0.7, y0 + RD, z), (a - 0.7, y0 + RD, z)], "conc", up=True)
                G.box(a - 0.7, a + 0.7, y0 - 0.4, y0, z - RH, z - RH / 2, "conc", skip="z-y+"); lev.append([a - 0.7, y0 - 0.4, a + 0.7, y0, z - RH / 2])
    tier(WK, 0.0, NL, "seatsb"); yc = WK + RD * NL; zc = RH * NL
    for (ha, hb) in HALF: G.face([(ha, yc, zc), (hb, yc, zc), (hb, yc + CA, zc), (ha, yc + CA, zc)], "conc", up=True); lev.append([ha, yc, hb, yc + CA, zc])
    tier(yc + CA, zc, NU, "seats"); yt = yc + CA + RD * NU; zt = zc + RH * NU
    for (ha, hb) in HALF: G.face([(ha, yt, zt), (hb, yt, zt), (hb, YN, zt), (ha, YN, zt)], "conc", up=True); lev.append([ha, yt, hb, YN, zt])
    for x in (SX0, SX1, XD - GW, XD + GW):                 # katsomon päädyt ja pääoven käytävän seinät
        G.face([(x, WK, 0), (x, WK, RH), (x, yc, zc), (x, yc + CA, zc), (x, yt, zt), (x, YN, zt), (x, YN, 0)], "redc", toward=(XD if abs(x - XD) < 3 else x + (x - CXm), 25, 2)); COL["seg"].append([x, WK + 0.3, x, YN, 0.08])
    for y in (22.0, 30.0, 36.0): LAMPS.append((XD, y, 3.0, 200, (1.0, 0.92, 0.82)))
    # --- SEISOMAKATSOMO (etelä): 16 matalaa askelmaa, ei kaiteita; C-katsomo sen PÄÄLLÄ omana kerroksenaan (omistaja 20.11.2026)
    for j in range(NT):
        y0, z = -(WK + TD * j), TH * (j + 1)
        G.face([(SX0, y0, z - TH), (SX1, y0, z - TH), (SX1, y0, z), (SX0, y0, z)], "redc", toward=(CXm, 0, z))
        G.face([(SX0, y0, z), (SX1, y0, z), (SX1, y0 - TD, z), (SX0, y0 - TD, z)], "redc" if j % 2 else "tread", up=True); lev.append([SX0, y0 - TD, SX1, y0, z])
    yb, zb = -(WK + TD * NT), TH * NT                      # seisomakatsomon takaseinä C-katsomon alla
    G.face([(SX0, yb, zb), (SX1, yb, zb), (SX1, yb, BZ - 0.4), (SX0, yb, BZ - 0.4)], "redc", toward=(CXm, 0, 4)); COL["seg"].append([SX0, yb, SX1, yb, 0.06])
    G.face([(SX0, -BY, BZ - 0.4), (SX1, -BY, BZ - 0.4), (SX1, yb, BZ - 0.4), (SX0, yb, BZ - 0.4)], "black", up=False)                          # C-katsomon alapinta
    G.face([(SX0, -BY, BZ - 0.4), (SX1, -BY, BZ - 0.4), (SX1, -BY, BZ + 1.05), (SX0, -BY, BZ + 1.05)], "redc", toward=(CXm, 0, 7))               # etukaide
    G.face([(SX0, -BY + 0.03, BZ + 0.1), (SX1, -BY + 0.03, BZ + 0.1), (SX1, -BY + 0.03, BZ + 0.9), (SX0, -BY + 0.03, BZ + 0.9)], "led", toward=(CXm, 0, 7))   # valonauha C-katsomon etureunassa (tyhjä, ei mainoksia)
    G.face([(SX0, -BY, BZ + 1.05), (SX1, -BY, BZ + 1.05), (SX1, -BY - 0.12, BZ + 1.05), (SX0, -BY - 0.12, BZ + 1.05)], "redc", up=True)
    G.face([(SX0, -BY - 0.12, BZ), (SX1, -BY - 0.12, BZ), (SX1, -BY - 0.12, BZ + 1.05), (SX0, -BY - 0.12, BZ + 1.05)], "redc", away=(CXm, 0, 7))
    G.face([(SX0, -BY, BZ), (SX1, -BY, BZ), (SX1, -BY - 1.0, BZ), (SX0, -BY - 1.0, BZ)], "conc", up=True)
    for k in range(NB): row(SX0, SX1, -(BY + 1.0 + RD * k), BZ + BH * (k + 1), -1, "seats", rise=BH)
    yk = -(BY + 1.0 + RD * NB); zk = BZ + BH * NB
    G.face([(SX0, yk, zk), (SX1, yk, zk), (SX1, YS, zk), (SX0, YS, zk)], "conc", up=True)
    for x in (SX0, SX1):
        G.face([(x, -BY, BZ - 0.4), (x, -BY, BZ + 1.05), (x, -BY - 1.0, BZ + 1.05), (x, yk, zk + 1.0), (x, YS, zk + 1.0), (x, YS, BZ - 0.4)], "redc", away=(CXm, -27, 8))
        G.face([(x, -WK, 0), (x, -WK, TH), (x, yb, zb), (x, yb, 0)], "redc", away=(CXm, -20, 1)); COL["seg"].append([x, -WK - 1.5, x, yb, 0.08])
    for x in np.arange(SX0 + 4.5, SX1, 9.0):
        G.cyl(x, -BY - 0.5, TH * 9, BZ - 0.4, 0.22, 8, "awall"); COL["circ"].append([x, -BY - 0.5, 0.3]); LAMPS.append((x + 4.5, -BY - 2.0, BZ - 1.0, 260, (1.0, 0.92, 0.85)))
    # --- eteläkulmat (C1, C5): istumakatsomo kaartuu kaukalon kulman ympäri ja nousee yhtä korkealle kuin C-katsomo (omistaja 20.11.2026: "yhtä korkealle")
    SCH = [(RD * k, RH * (k + 1)) for k in range(NL)] + [(RD * NL + CA + RD * k, RH * (NL + k + 1)) for k in range(NU)]     # rivin etureunan etäisyys ja korkeus (sama kuin A-katsomossa)
    DEP = RD * NL + CA + RD * NU; ZTOP = RH * (NL + NU)
    def corner(cx, cy, a0):
        A = [radians(a0 + 90 * i / 8) for i in range(9)]; P = lambda r: [(cx + r * cos(t), cy + r * sin(t)) for t in A]; rf = IR + 2.4
        def strip(pa, pb, za, zb, mat, **kw):
            Ls = 0.0
            for i in range(8):
                l = math.dist(pa[i], pa[i + 1]); n0, n1 = Ls / 0.5, (Ls + l) / 0.5; Ls += l
                G.face([(*pa[i], za), (*pa[i + 1], za), (*pb[i + 1], zb), (*pb[i], zb)], mat, uv=[(n0, 0), (n1, 0), (n1, 1), (n0, 1)] if mat == "seats" else None, **kw)
        for k, (d, z) in enumerate(SCH):
            r0 = rf + d
            strip(P(r0), P(r0), z - RH, z, "redc" if k == 0 else "tread", toward=(cx, cy, z)); strip(P(r0), P(r0 + RD), z, z, "tread", up=True)
            strip(P(r0 + 0.62), P(r0 + 0.62), z + 0.42, z + 0.88, "seats", toward=(cx, cy, z)); strip(P(r0 + 0.2), P(r0 + 0.62), z + 0.42, z + 0.42, "redc", up=True)
        strip(P(rf + RD * NL), P(rf + RD * NL + CA), RH * NL, RH * NL, "conc", up=True)
        for t in (A[0], A[-1]):                             # päätyseinät
            q = lambda r, z: (cx + r * cos(t), cy + r * sin(t), z)
            G.face([q(rf, 0)] + [v for d, z in SCH for v in (q(rf + d, z), q(rf + d + RD, z))] + [q(rf + DEP, 0)], "redc", away=(cx + (rf + 10) * cos(radians(a0 + 45)), cy + (rf + 10) * sin(radians(a0 + 45)), 3))
            COL["seg"].append([cx + rf * cos(t), cy + rf * sin(t), cx + (rf + DEP) * cos(t), cy + (rf + DEP) * sin(t), 0.08])
        for a, b in zip(P(rf), P(rf)[1:]): COL["seg"].append([a[0], a[1], b[0], b[1], 0.08])
    corner(SX0, -IH + IR, 180); corner(SX1, -IH + IR, 270)
    # --- päädyt: alarivit kaukalon päässä (sama nousu kuin sivuilla)
    def endrows(xf, sg, ya, yb, n, rise=RH, z0=0.0, first="redc"):
        for k in range(n):
            x0, z = xf + sg * RD * k, z0 + rise * (k + 1); x1 = x0 + sg * RD; m = max(1, round((yb - ya) / 0.5))
            G.face([(x0, ya, z - rise), (x0, yb, z - rise), (x0, yb, z), (x0, ya, z)], first if k == 0 else "tread", toward=(CXm, 0, z)); G.face([(x0, ya, z), (x1, ya, z), (x1, yb, z), (x0, yb, z)], "tread", up=True)
            G.face([(x0 + sg * 0.62, ya, z + 0.42), (x0 + sg * 0.62, yb, z + 0.42), (x0 + sg * 0.62, yb, z + 0.88), (x0 + sg * 0.62, ya, z + 0.88)], "seats", uv=[(0, 0), (m, 0), (m, 1), (0, 1)], toward=(CXm, 0, z))
            G.face([(x0 + sg * 0.2, ya, z + 0.42), (x0 + sg * 0.62, ya, z + 0.42), (x0 + sg * 0.62, yb, z + 0.42), (x0 + sg * 0.2, yb, z + 0.42)], "redc", up=True)
        return xf + sg * RD * n, z0 + rise * n
    def sidewall(xa, za, xb, zb, y, zlow=0.0):
        G.face([(xa, y, zlow), (xa, y, za), (xb, y, zb), (xb, y, zlow)], "redc", toward=((xa + xb) / 2, y + 30, 2)); G.face([(xa, y, zlow), (xa, y, za), (xb, y, zb), (xb, y, zlow)], "redc", toward=((xa + xb) / 2, y - 30, 2))
    EN, ES = IH, -IH + IR                                  # päätykatsomoiden leveys: A-sivun linjalta eteläkulmaan (pohjoiskulmissa ei katsomoa: BAR ja MEDIA / kioskit)
    # länsi = B-pääty ja kioskit: alarivit (pääoven kohdalla käytävä kaukalolle), niiden takana ylärivit parvena kulkuaulan ja kioskien PÄÄLLÄ
    XL = IX0 - 2.4
    for (ya, yb) in ((2.5, EN), (ES, -2.5)):
        xe, zz = endrows(XL, -1, ya, yb, NL); G.face([(xe, ya, 0), (xe, yb, 0), (xe, yb, zz), (xe, ya, zz)], "redc", toward=(0, 0, 2))
        for y in (ya, yb): sidewall(XL, RH, xe, zz, y); COL["seg"].append([XL, y, xe, y, 0.08])
        COL["seg"] += [[XL, ya, XL, yb, 0.08], [xe, ya, xe, yb, 0.08]]
    xb0 = XL - RD * NL; zb0 = RH * NL + 0.4; nb = int((xb0 - 0.3 - X0) / RD); rb = (ZTOP + 0.1 - zb0) / nb
    G.face([(xb0, ES, zb0 - 0.4), (xb0, EN, zb0 - 0.4), (xb0, EN, zb0 + 1.05), (xb0, ES, zb0 + 1.05)], "redc", toward=(CXm, 0, 5)); G.face([(xb0, ES, zb0 + 0.1), (xb0, EN, zb0 + 0.1), (xb0, EN, zb0 + 0.9), (xb0, ES, zb0 + 0.9)][::1], "led", toward=(CXm, 0, 5)) if False else None
    G.face([(xb0 - 0.12, ES, zb0), (xb0 - 0.12, EN, zb0), (xb0 - 0.12, EN, zb0 + 1.05), (xb0 - 0.12, ES, zb0 + 1.05)], "redc", toward=(0, 0, 5))
    xw_, zw_ = endrows(xb0 - 0.3, -1, ES, EN, nb, rise=rb, z0=zb0, first="tread")
    G.face([(xb0, ES, zb0 - 0.4), (xb0, EN, zb0 - 0.4), (X0, EN, zw_ - 0.4), (X0, ES, zw_ - 0.4)], "black", up=False)             # parven alapinta = kioskiaulan katto
    for y in (ES, EN): G.face([(xb0, y, zb0 - 0.4), (xb0, y, zb0 + 1.05), (X0, y, zw_ + 1.0), (X0, y, zw_ - 0.4)], "redc", toward=(5, y + (20 if y > 0 else -20), 6)); G.face([(xb0, y, zb0 - 0.4), (xb0, y, zb0 + 1.05), (X0, y, zw_ + 1.0), (X0, y, zw_ - 0.4)], "redc", toward=(5, 0, 6))
    for y in (ES + 0.3, 2.5, -2.5, EN - 0.3): G.cyl(xb0 - 0.3, y, 0, zb0 - 0.4, 0.2, 8, "awall"); COL["circ"].append([xb0 - 0.3, y, 0.28])
    for (y0, y1) in ((4.0, 13.0), (15.5, 34.0)):           # kioskit länsiseinällä: parven alla ja luoteiskulman aulassa
        G.box(X0 + 1.6, X0 + 2.4, y0, y1, 0, 1.1, "redc", skip="z-", mats={"z+": "white"}); COL["seg"].append([X0 + 2.0, y0, X0 + 2.0, y1, 0.45])
        G.box(X0, X0 + 2.6, y0 - 0.2, y1 + 0.2, 2.9, 3.4, "redc", skip="x-")
        G.face([(X0 + 0.06, y0 + 0.4, 2.05), (X0 + 0.06, y1 - 0.4, 2.05), (X0 + 0.06, y1 - 0.4, 2.75), (X0 + 0.06, y0 + 0.4, 2.75)], "menu", uv=[(0, 0), (1, 0), (1, 1), (0, 1)], toward=(10, 0, 2))
        for yy in np.arange(y0 + 1.5, y1 - 1.0, 4.0):
            G.box(X0 + 0.1, X0 + 0.75, yy, yy + 1.2, 0, 1.9, "black", skip="z-x-", mats={"x+": "menu"}); LAMPS.append((X0 + 3.2, yy, 2.5, 150, (1.0, 0.9, 0.78)))
    for y in (-4.5, 0.0, 8.0): LAMPS.append((7.0, y, 3.0, 220, (1.0, 0.92, 0.82)))
    # itä = D-pääty: alarivit, niiden takana kaksi ravintolatasoa (valkoliinaiset pöydät, punaiset tuolit) ja ylärivit samaan korkeuteen; koilliskulmassa baari
    XR = IX1 + 2.4; xe, zz = endrows(XR, 1, ES, EN, NL)
    for y in (ES, EN): sidewall(XR, RH, xe, zz, y)
    COL["seg"] += [[XR, ES, XR, EN, 0.08], [XR, EN, X1, EN, 0.1], [XR, ES, X1, ES, 0.1]]
    for p_ in range(2):
        x0, z = xe + 3.0 * p_, zz + 0.75 * (p_ + 1); x1 = x0 + 3.0
        G.face([(x0, ES, z - 0.75), (x0, EN, z - 0.75), (x0, EN, z), (x0, ES, z)], "redc", toward=(CXm, 0, z)); G.face([(x0, ES, z), (x1, ES, z), (x1, EN, z), (x0, EN, z)], "black", up=True)
        G.small = True; G.box(x0 + 0.05, x0 + 0.1, ES, EN, z + 1.0, z + 1.06, "rail")
        for yy in np.arange(ES, EN + 0.1, 2.05): G.cyl(x0 + 0.07, yy, z, z + 1.03, 0.025, 4, "rail")
        for yy in np.arange(ES + 1.6, EN - 1.2, 2.4):
            G.box(x0 + 1.0, x0 + 1.9, yy - 0.4, yy + 0.4, z, z + 0.76, "white", skip="z-")
            for cy in (yy - 0.75, yy + 0.75): G.box(x0 + 1.2, x0 + 1.65, cy - 0.2, cy + 0.2, z, z + 0.46, "redc", skip="z-"); G.box(x0 + 1.2, x0 + 1.65, cy + (0.16 if cy > yy else -0.2), cy + (0.2 if cy > yy else -0.16), z + 0.46, z + 0.9, "redc", skip="z-")
        G.small = False
        for y in (ES, EN): G.face([(x0, y, 0), (x1, y, 0), (x1, y, z), (x0, y, z)], "redc", toward=(x0, y + 30, 1)); G.face([(x0, y, 0), (x1, y, 0), (x1, y, z), (x0, y, z)], "redc", toward=(x0, y - 30, 1))
        LAMPS.append((x0 + 1.5, 0.0, z + 2.8, 220, (1.0, 0.86, 0.66))); LAMPS.append((x0 + 1.5, 9.0, z + 2.8, 220, (1.0, 0.86, 0.66)))
    xu = xe + 6.0; zu = zz + 1.5; nu = int((X1 - 0.3 - xu) / RD); ru = (ZTOP + 0.1 - zu) / nu
    xq, zq = endrows(xu, 1, ES, EN, nu, rise=ru, z0=zu)
    for y in (ES, EN): sidewall(xu, zu, X1, zq, y)
    G.box(XR + 3.0, XR + 3.8, EN + 4.0, EN + 16.0, 0, 1.1, "black", skip="z-", mats={"z+": "white"}); COL["seg"].append([XR + 3.4, EN + 4.0, XR + 3.4, EN + 16.0, 0.45])     # baari (koilliskulma)
    G.face([(X1 - 0.06, EN + 3.0, 1.2), (X1 - 0.06, YN - 1.0, 1.2), (X1 - 0.06, YN - 1.0, 3.0), (X1 - 0.06, EN + 3.0, 3.0)], "warm", toward=(CXm, 0, 2))
    for y in (EN + 6.0, EN + 12.0, EN + 18.0): LAMPS.append((X1 - 6.0, y, 3.2, 260, (1.0, 0.85, 0.62)))
    # --- katto: poikkipalkit, ilmakanavat, valaisimet
    for y in (-10.0, 10.0):
        for i in range(10):
            a0, a1 = 2 * pi * i / 10, 2 * pi * (i + 1) / 10
            G.face([(4, y + 0.55 * cos(a0), 15.6 + 0.55 * sin(a0)), (X1 - 4, y + 0.55 * cos(a0), 15.6 + 0.55 * sin(a0)), (X1 - 4, y + 0.55 * cos(a1), 15.6 + 0.55 * sin(a1)), (4, y + 0.55 * cos(a1), 15.6 + 0.55 * sin(a1))], "steelw", away=(CXm, y, 15.6))
    G.small = True
    for x in np.arange(12.0, X1 - 6, 8.8):
        for y in (-27.0, -8.0, 8.0, 27.0):
            zl = arc(y) - 1.2
            G.face([(x - 0.6, y - 0.12, zl), (x + 0.6, y - 0.12, zl), (x + 0.6, y + 0.12, zl), (x - 0.6, y + 0.12, zl)], "lampg", uv=[(0.5, 0.5)] * 4, up=False)
            LAMPS.append((x, y, zl - 0.5, 1600 if abs(y) < 10 else 800, (0.92, 0.96, 1.0)))
    # --- mediakuutio ja viirit
    cx, z0, z1, hw = CXm, 10.0, 12.6, 2.2
    G.box(cx - hw - 0.1, cx + hw + 0.1, -hw - 0.1, hw + 0.1, z0 - 0.15, z1 + 0.15, "black")
    for (p, q) in (((cx - hw - 0.12, -hw), (cx - hw - 0.12, hw)), ((cx + hw + 0.12, hw), (cx + hw + 0.12, -hw)), ((cx - hw, hw + 0.12), (cx + hw, hw + 0.12)), ((cx + hw, -hw - 0.12), (cx - hw, -hw - 0.12))):
        G.face([(*p, z0), (*q, z0), (*q, z1), (*p, z1)], "screen", uv=[(0, 0), (1, 0), (1, 1), (0, 1)], away=(cx, 0, 10))
    for (dx, dy) in ((-1.5, -1.5), (1.5, 1.5), (-1.5, 1.5), (1.5, -1.5)): G.cyl(cx + dx, dy, z1 + 0.15, ZK - 0.3, 0.02, 4, "black")
    for k in range(6):
        x = 60.0 + 2.2 * k; G.face([(x, 12.0, 12.6), (x + 1.3, 12.0, 12.6), (x + 1.3, 12.0, 14.5), (x, 12.0, 14.5)], "banner", uv=[(k / 6, 0), ((k + 1) / 6, 0), ((k + 1) / 6, 1), (k / 6, 1)], toward=(x, 0, 6))
        G.face([(x, 12.03, 12.6), (x + 1.3, 12.03, 12.6), (x + 1.3, 12.03, 14.5), (x, 12.03, 14.5)], "banner", uv=[((k + 1) / 6, 0), (k / 6, 0), (k / 6, 1), ((k + 1) / 6, 1)], toward=(x, 40, 6))
        G.cyl(x + 0.65, 12.0, 14.5, 17.0, 0.01, 3, "black")
    G.small = False
    # --- lopuksi koko malli käännetään pelin kehykseen: x = pääovelta (pohjoisseinä) sisään etelään, y = vasemmalle (itään)
    G.V[:] = [(YN - v[1], v[0] - XD, v[2]) for v in G.V]
    COL["seg"][:] = [[YN - g[1], g[0] - XD, YN - g[3], g[2] - XD, g[4]] for g in COL["seg"]]; COL["circ"][:] = [[YN - c_[1], c_[0] - XD, c_[2]] for c_ in COL["circ"]]
    lev = [[YN - r[3], r[0] - XD, YN - r[1], r[2] - XD, r[4]] for r in lev]; LAMPS = [(YN - l[1], l[0] - XD, l[2], l[3], l[4]) for l in LAMPS]
    return LAMPS, lev

if __name__ == "__main__":
    import bpy
    textures(); LAMPS, LEV = build()
    print(len(G.F), "pintaa,", len(COL["seg"]), "janaa,", len(LEV), "tasoa")
    objs = K.make_scene([])
    for (x, y, z, w, c) in LAMPS:
        l = bpy.data.lights.new("valo", "POINT"); l.energy = w; l.color = c; l.shadow_soft_size = 0.6
        o = bpy.data.objects.new("valo", l); o.location = (x, y, z); bpy.context.scene.collection.objects.link(o)
    T = lambda p: (YN - p[1], p[0] - XD, p[2])
    V = dict(a_ylhaalta=((52.0, 36.0, 12.4), (52, -10, 2), 14), ovelta=((XD, 37.0, 1.7), (XD, 0, 2.0), 16), seisoma=((40.0, 2.0, 1.7), (56, -24, 5.5), 16), d_paaty=((66.0, 0.0, 1.7), (98, 0, 5.0), 16))
    if A.shots: K.shots(V={k: (T(a), T(b), l) for k, (a, b, l) in V.items()})
    LMAX = 2.0
    if not A.nobake: LMAX = K.finish_lm(K.bake(objs))
    K.export(objs)
    room = [[0.0, X0 - XD], [YN - YS, X0 - XD], [YN - YS, X1 - XD], [0.0, X1 - XD]]
    meta = dict(col=COL, lmax=LMAX, xw=0.0, xe=YN - YS, hw=X1 - XD, py=0.0, xs0=1e6, flz=0.0, lev=LEV, spawn=[1.8, 0.0], exit=[1.0, 1.6], room=room, rooms=[room], ports=[])
    json.dump(meta, open("%s/%s.json" % (OUT, K.NAME), "w"))
