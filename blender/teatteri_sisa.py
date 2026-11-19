# -*- coding: utf-8 -*-
"""
Porin Teatterin päänäyttämön sali (19.11.2026): hevosenkengän muotoinen katsomo, salia kiertävä parvi kullattuine kaiteineen,
näyttämöaukko punaisine esirippuineen, näyttämö, kattomaalausten kehä ja kattokruunu.

Ajo:  python3 blender/teatteri_sisa.py --out DIR [--lm 2048] [--samples 32] [--shots] [--nobake]
      python3 tools/sisa_to_js.py DIR teatteri_sisa        (pelikansiossa -> teatteri_sisa.js)
Käyttää kirkko_sisa.py:n työkaluja (Geo, wall, valokartan leivonta, vienti).

Koordinaatit: X = salin takaovelta kohti näyttämöä, Y = vasemmalle, Z = ylös, origo takaseinän keskellä permannon lattialla.
Pelissä (index.html TEAT): origo (-199.62, 374.34) = Hallituskadun julkisivun keskeltä 11,5 m sisään, X-akseli suuntaan 193° (etelälounaaseen).
Vanha teatteritalo on jalanjäljen itäosa (julkisivu 23,8 m, keskirisaliitti 8,8 m); salin mitat on SOVITETTU siihen, ei mitattu.

Lähteet: rakenne, värit ja materiaalit on luettu julkaistuista sisäkuvista (akukon.fi referenssikuvat 2017), kuvia ei tallennettu.
Tiedot: 313 paikkaa, joista 79 parvella; katossa seitsemän pyöreää maalausta; näyttämöaukon yllä reliefi ja sivuilla rintakuvat (fi.wikipedia, wuoriosaatio.fi).
Kattomaalauksia (K. G. Wetterstrand / S. Wuorio 1884), reliefiä, rintakuvia ja esirippua EI ole kopioitu: tilalla on omat pelkistetyt piirrokset
(taivas, pilvet, vaalea hahmo). Arvioitua / keksittyä: permannon käytäväjako (keskikäytävä + reunakäytävät), portaat näyttämölle salin puolelta,
näyttämön takaosa, ovien tarkat paikat.
"""
import os, sys, json, math
import numpy as np
from math import sin, cos, pi, sqrt, radians, atan2, hypot
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kirkko_sisa as K
from kirkko_sisa import flat, fnoise, to_img, srgb, save_tex, wall
from PIL import Image, ImageDraw, ImageFilter
K.NAME = "teatteri_sisa"; K.LM_REF = 0.50
G, COL, OUT, A = K.G, K.COL, K.OUT, K.A

R, CX = 7.2, 7.2                         # salin puolileveys = takakaaren säde, kaaren keskipiste x
XS, XP, XI, XE = 13.2, 14.6, 15.6, 25.6  # näyttämön etureuna, näyttämöaukon seinä, aukon sisäreuna, näyttämön takaseinä
SW, ZST = 8.0, 1.0                       # näyttämön puolileveys, näyttämön lattian korkeus
ZW, ZT, CO = 8.1, 9.4, 1.1               # seinän yläreuna, katto, holkan syvyys
A0, Z0, R0 = 5.3, 5.0, 1.7               # näyttämöaukon ulkokaari: puolileveys, kanta, nousu
A1, Z1, R1 = 4.5, 4.9, 1.4               # sisäkaari
BO, BZ0, BZ1 = 2.7, 3.0, 4.2             # parven syvyys, alapinta, kaiteen yläreuna
BFA, BFB, BT = 3.3, 3.65, 1.5            # parven lattiat (etu, taka), takatason leveys
XBE = 12.6                               # parvi päättyy näyttämöaukon pieliin
XA = 40.0                                # permannon rivien kaarien keskipiste
NST, STW, STH = 7, 0.36, ZST / 7         # portaat näyttämölle: askelmia, etenemä, nousu
SY0 = 5.8                                # portaiden sisäreuna
WT, RO = 0.5, 9.9                        # salin seinän paksuus, kiertokäytävän ulkoseinän säde
XF, XFB, FH, FY, FO = -11.0, -1.6, 4.6, 10.5, 3.6   # aula: julkisivuseinä, takaseinä, korkeus, puolileveys, takaseinän aukon puolileveys
CH = 3.0                                 # käytävän ja syvennyksen korkeus
DX0, DX1, DH = 8.9, 10.3, 2.25           # salin sivuovet
PHI1 = math.degrees(math.acos((XFB - CX) / RO))     # kulma, jossa käytävän ulkoseinä kohtaa aulan takaseinän
YJ = RO * sin(radians(PHI1))
XO = 100.0                               # yläkerran kahvila on mallissa siirretty +100 m (peli siirtää pelaajan ovesta, kartta taittaa takaisin)
KW, KH = 4.6, 5.4                        # kahvilan puolileveys ja korkeus

MAT = dict(wallred=(2.0, 0), dado=(1.0, 0), frieze=(0.45, 0), cove=(0.8, 0), ceil=(1, 0), pink=(2.0, 0), cream=(2.0, 0), gold=(1.0, 0), under=(2.0, 0),
           balfront=(1.6, 0), carpet=(2.0, 0), stagefloor=(2.0, 0), seat=(1.0, 0), seatwood=(1.0, 0), prosc=(1.5, 0), jamb=(2.0, 0), archiv=(1.0, 0),
           pier=(1, 0), cartouche=(1, 0), curtain=(1.0, 0), valance=(1.0, 0), black=(2.0, 0), doord=(1, 0), doorb=(1, 0), cyc=(1, 1.6), bulb=(1, 3.0), exitl=(1, 2.0),
           corr=(3.0, 0), fwall=(2.0, 0), ftile=(1.2, 0), rcarpet=(1.5, 0), fceil=(2.0, 0), white=(2.0, 0), quote=(1, 0), doorg=(1, 0), sign=(1, 0), reveal=(2.0, 0.5), glass_f=(1, 4.0),
           mauve=(2.0, 0), cdado=(0.9, 0), ccorn=(0.45, 0), cceil=(1, 0), ccarpet=(2.4, 0), orange=(2.0, 0), marble=(0.8, 0), doorc=(1, 0), ped=(1, 0), glass_c=(1, 5.0))
K.MATDEF.clear(); K.MATDEF.update(MAT); K.MI.clear(); K.MI.update({k: i for i, k in enumerate(MAT)})

C = dict(wallred=(0.150, 0.036, 0.026), pink=(0.72, 0.30, 0.25), cream=(0.80, 0.70, 0.50), gold=(0.66, 0.47, 0.12), ochre=(0.70, 0.45, 0.11), sky=(0.34, 0.50, 0.62),
         seat=(0.27, 0.22, 0.18), red=(0.42, 0.012, 0.018), carpet=(0.050, 0.062, 0.080), wood=(0.060, 0.032, 0.018), beige=(0.50, 0.40, 0.27))

def textures():
    n = 256; gd, gh, gs = srgb(C["gold"]), srgb((0.86, 0.68, 0.26)), srgb((0.30, 0.19, 0.04)); cr = srgb(C["cream"]); crs = srgb((0.52, 0.44, 0.30))
    save_tex("wallred", to_img(flat(n, C["wallred"], 1, 0.06, 5)))
    save_tex("pink", to_img(flat(n, C["pink"], 2, 0.03, 6)))
    save_tex("cream", to_img(flat(n, C["cream"], 3, 0.03, 6)))
    save_tex("under", to_img(flat(n, (0.72, 0.64, 0.48), 4, 0.03, 6)))
    save_tex("gold", to_img(flat(n, C["gold"], 5, 0.08, 12)))
    save_tex("black", to_img(flat(64, (0.012, 0.012, 0.014), 6, 0.0)))
    save_tex("seatwood", to_img(flat(n, (0.05, 0.035, 0.028), 7, 0.10, 3, 40)))
    save_tex("seat", to_img(flat(n, C["seat"], 8, 0.05, 30, 30, 0.03)))
    # permannon ja parven matto: tumma siniharmaa, pieni vinoruutukuvio
    im = to_img(flat(n, C["carpet"], 9, 0.06, 20)); d = ImageDraw.Draw(im)
    for k in range(-n, 2 * n, 32): d.line([(k, 0), (k + n, n)], fill=srgb((0.075, 0.09, 0.11)), width=2); d.line([(k, 0), (k - n, n)], fill=srgb((0.075, 0.09, 0.11)), width=2)
    for j in range(0, n, 32):
        for i in range(0, n, 32): d.ellipse([i + 13, j - 3, i + 19, j + 3], fill=srgb((0.16, 0.12, 0.06)))
    save_tex("carpet", im)
    # näyttämön lattia: mustaksi maalattu lankku
    a = flat(n, (0.022, 0.021, 0.020), 10, 0.25, 3, 60); im = to_img(a); d = ImageDraw.Draw(im)
    for y in range(0, n, 32): d.line([(0, y), (n, y)], fill=(8, 8, 8), width=2)
    save_tex("stagefloor", im)
    # alaseinän tumma puupaneeli (v 0..1 = 1 m)
    im = to_img(flat(n, C["wood"], 11, 0.12, 3, 50)); d = ImageDraw.Draw(im)
    for x in (0, 128): d.rectangle([x + 12, 40, x + 116, n - 30], outline=srgb((0.025, 0.014, 0.008)), width=4)
    d.rectangle([0, 0, n, 14], fill=srgb((0.11, 0.065, 0.03))); d.rectangle([0, 14, n, 19], fill=srgb((0.02, 0.012, 0.008)))
    save_tex("dado", im)
    # friisi seinän yläreunassa: tumma pohja, kultainen munasauva ja hammaslista
    im = to_img(flat(n, (0.10, 0.03, 0.022), 12, 0.05, 6)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, n, 40], fill=cr); d.rectangle([0, 40, n, 48], fill=crs)
    for x in range(0, n, 32): d.rectangle([x + 4, 10, x + 22, 34], fill=gd, outline=gs)
    for x in range(0, n, 64): d.ellipse([x + 12, 84, x + 52, 168], outline=gd, width=7); d.ellipse([x + 26, 110, x + 38, 142], fill=gh); d.polygon([(x + 58, 80), (x + 64, 126), (x + 58, 172)], fill=gd)
    d.rectangle([0, 200, n, 214], fill=gd); d.rectangle([0, 214, n, n], fill=cr); d.line([(0, 236), (n, 236)], fill=crs, width=3)
    save_tex("frieze", im)
    # holkka: vaaleanpunainen kenttä, kermanvärinen kehys ja kullattu konsoli (u = 0,8 m, v = holkan poikki)
    im = to_img(flat(n, (0.74, 0.40, 0.33), 13, 0.03, 6)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, n, 22], fill=cr); d.rectangle([0, n - 30, n, n], fill=cr); d.line([(0, 24), (n, 24)], fill=gd, width=5); d.line([(0, n - 32), (n, n - 32)], fill=gd, width=5)
    d.rectangle([20, 50, 108, 200], outline=cr, width=5); d.rectangle([148, 50, 236, 200], outline=cr, width=5)
    d.polygon([(112, 36), (144, 36), (140, 150), (134, 214), (122, 214), (116, 150)], fill=gd, outline=gs); d.ellipse([110, 30, 146, 70], fill=gh, outline=gs, width=3); d.ellipse([118, 190, 138, 222], fill=gh, outline=gs, width=3)
    for y in range(84, 180, 22): d.line([(118, y), (138, y)], fill=gs, width=3)
    save_tex("cove", im)
    # parven kaide: harmahtavan kermanvärinen, keskellä kullattu köynnösreliefi (u = 1,6 m, v = kaiteen korkeus)
    W, H = 512, 256; a = flat(512, (0.62, 0.58, 0.47), 14, 0.03, 8)[:H]; im = to_img(a); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 26], fill=srgb((0.74, 0.69, 0.56))); d.line([(0, 28), (W, 28)], fill=crs, width=4); d.line([(0, 44), (W, 44)], fill=gd, width=5)
    d.rectangle([0, 58, W, 176], fill=srgb((0.30, 0.19, 0.05)))
    for k in range(4):                                       # S-kiehkurat ja lehdet
        x = k * 128
        d.arc([x + 4, 66, x + 96, 158], 180, 400, fill=gh, width=11); d.arc([x + 30, 90, x + 74, 134], 150, 420, fill=gd, width=8)
        d.arc([x + 70, 76, x + 162, 168], 0, 220, fill=gh, width=11); d.ellipse([x + 44, 104, x + 60, 120], fill=gh)
        d.polygon([(x + 96, 70), (x + 120, 88), (x + 100, 100)], fill=gd); d.polygon([(x + 100, 164), (x + 126, 150), (x + 104, 136)], fill=gd)
    for (xa, xb) in ((-64, 64), (192, 320), (448, 576)): d.rectangle([xa + 52, 54, xa + 76, 180], fill=srgb((0.62, 0.58, 0.47))); d.ellipse([xa + 46, 96, xa + 82, 136], fill=gh, outline=gs, width=3)
    d.line([(0, 58), (W, 58)], fill=gs, width=3); d.line([(0, 176), (W, 176)], fill=gs, width=3); d.line([(0, 190), (W, 190)], fill=gd, width=5)
    d.rectangle([0, 204, W, H], fill=srgb((0.70, 0.65, 0.52))); d.line([(0, 206), (W, 206)], fill=crs, width=4)
    for x in range(0, W, 32): d.rectangle([x + 6, 222, x + 22, 244], fill=srgb((0.60, 0.55, 0.43)), outline=crs)
    save_tex("balfront", im)
    # näyttämöaukon kaaren alapinta: vaaleanpunainen, pyöreät tummansiniset medaljongit kultakehyksin (u = 1,5 m kaarta pitkin, v = poikki)
    im = to_img(flat(n, C["pink"], 15, 0.03, 6)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, n, 20], fill=cr); d.rectangle([0, n - 21, n, n], fill=cr); d.line([(0, 24), (n, 24)], fill=gd, width=6); d.line([(0, n - 25), (n, n - 25)], fill=gd, width=6)
    d.ellipse([58, 58, 198, 198], fill=gd, outline=gs, width=3); d.ellipse([70, 70, 186, 186], fill=srgb((0.05, 0.12, 0.20)))
    for k in range(8):
        an = k * pi / 4; d.line([(128, 128), (128 + 50 * cos(an), 128 + 50 * sin(an))], fill=srgb((0.30, 0.42, 0.50)), width=5)
    d.ellipse([110, 110, 146, 146], fill=gh); d.ellipse([0 - 14, 114, 14, 142], fill=gd); d.ellipse([n - 14, 114, n + 14, 142], fill=gd)
    save_tex("prosc", im)
    # aukon pielet: vaaleanpunainen peili kermanvärisin kehyksin (v = 2 m)
    im = to_img(flat(n, C["pink"], 16, 0.03, 6)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 30, n], fill=cr); d.rectangle([n - 31, 0, n, n], fill=cr); d.line([(34, 0), (34, n)], fill=gd, width=5); d.line([(n - 35, 0), (n - 35, n)], fill=gd, width=5)
    d.rectangle([62, 20, n - 63, n - 21], outline=cr, width=6)
    save_tex("jamb", im)
    # kaaren kehyslista: kermanvärinen, kultaiset viivat ja helminauha (u poikki, v pitkin)
    im = to_img(flat(n, C["cream"], 17, 0.03, 6)); d = ImageDraw.Draw(im)
    for x in (30, 220): d.line([(x, 0), (x, n)], fill=gd, width=10)
    for y in range(0, n, 32): d.ellipse([112, y + 4, 144, y + 28], fill=gh, outline=gs, width=2)
    save_tex("archiv", im)
    # näyttämöaukon sivupilari (1,7 x 6,6 m): pilasterit, alhaalla pyöreä medaljonki (pelkistetty rintakuva, ei kenenkään näköinen), parven kaiteen
    # jatke ja ylhäällä kaarisyvennys
    W, H = 256, 992; a = flat(1024, C["pink"], 18, 0.03, 6)[:H, :W]; im = to_img(a); d = ImageDraw.Draw(im)
    Yz = lambda z: H - (z - 1.0) / 6.6 * H
    for x0 in (0, W - 40): d.rectangle([x0, 0, x0 + 40, H], fill=cr); d.line([(x0 + 8, 0), (x0 + 8, H)], fill=crs, width=2); d.line([(x0 + 32, 0), (x0 + 32, H)], fill=crs, width=2)
    for x0 in (0, W - 40): d.rectangle([x0 - 4, 0, x0 + 44, 46], fill=gd, outline=gs); d.rectangle([x0 - 4, H - 40, x0 + 44, H], fill=crs)
    cy = Yz(2.45); d.ellipse([128 - 62, cy - 62, 128 + 62, cy + 62], fill=cr, outline=gd, width=7); d.ellipse([128 - 48, cy - 48, 128 + 48, cy + 48], fill=srgb((0.06, 0.12, 0.19)))
    d.ellipse([128 - 15, cy - 30, 128 + 15, cy + 4], fill=srgb((0.70, 0.68, 0.62))); d.pieslice([128 - 36, cy + 2, 128 + 36, cy + 80], 180, 360, fill=srgb((0.70, 0.68, 0.62)))
    d.rectangle([40, Yz(4.2), W - 40, Yz(3.0)], fill=srgb((0.62, 0.58, 0.47))); d.rectangle([40, Yz(4.0), W - 40, Yz(3.3)], fill=gs)
    for x in range(48, W - 60, 44): d.arc([x, Yz(3.95), x + 40, Yz(3.35)], 150, 420, fill=gh, width=7)
    d.line([(40, Yz(4.2)), (W - 40, Yz(4.2))], fill=gd, width=5); d.line([(40, Yz(3.0)), (W - 40, Yz(3.0))], fill=gd, width=5)
    x0, x1, yb, ys = 66, W - 66, Yz(4.45), Yz(6.2)
    d.rectangle([x0 - 10, ys, x1 + 10, yb], fill=cr); d.pieslice([x0 - 10, ys - (x1 - x0 + 20) / 2, x1 + 10, ys + (x1 - x0 + 20) / 2], 180, 360, fill=cr)
    d.rectangle([x0, ys, x1, yb - 8], fill=srgb((0.50, 0.58, 0.66))); d.pieslice([x0, ys - (x1 - x0) / 2, x1, ys + (x1 - x0) / 2], 180, 360, fill=srgb((0.50, 0.58, 0.66)))
    d.rectangle([x0, yb - 60, x1, yb - 8], fill=srgb((0.66, 0.62, 0.52))); d.line([(x0, yb - 60), (x1, yb - 60)], fill=gd, width=4)
    save_tex("pier", im)
    # aukon yläpuolen kilpi: kehys ja kaksi pyöreää profiilimedaljonkia (pelkistetyt, ei kenenkään näköiset), välissä lyyra
    W, H = 512, 128; im = to_img(flat(512, C["cream"], 19, 0.03, 6)[:H]); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, H - 1], outline=gd, width=8)
    for cx in (110, 402):
        d.ellipse([cx - 50, 14, cx + 50, 114], fill=gd, outline=gs, width=3); d.ellipse([cx - 40, 24, cx + 40, 104], fill=srgb((0.62, 0.34, 0.28)))
        d.ellipse([cx - 14, 36, cx + 14, 70], fill=srgb((0.80, 0.76, 0.66))); d.pieslice([cx - 30, 66, cx + 30, 130], 180, 360, fill=srgb((0.80, 0.76, 0.66)))
    d.arc([226, 26, 286, 110], 20, 160, fill=gd, width=7); d.line([(240, 40), (240, 96)], fill=gd, width=4); d.line([(256, 34), (256, 100)], fill=gd, width=4); d.line([(272, 40), (272, 96)], fill=gd, width=4)
    for x in (176, 336): d.arc([x - 26, 44, x + 26, 96], 0, 360, fill=gd, width=5)
    save_tex("cartouche", im)
    # esirippu: punainen sametti, pystylaskokset (u = 1 m)
    xx = np.arange(n)[None, :] / n; fold = 0.55 + 0.45 * np.cos(xx * 2 * pi * 4) + 0.12 * np.cos(xx * 2 * pi * 9 + 1.0)
    a = np.array(C["red"])[None, None, :] * (0.35 + 0.75 * np.clip(fold, 0, 1.3))[..., None] * (1 + 0.05 * fnoise(n, 20, 3, 60))[..., None]
    save_tex("curtain", to_img(np.broadcast_to(a, (n, n, 3)).copy()))
    im = to_img(np.broadcast_to(a, (n, n, 3)).copy()); d = ImageDraw.Draw(im)        # kappa: sama sametti, alareunassa kultahapsu
    d.rectangle([0, n - 34, n, n - 24], fill=gd)
    for x in range(0, n, 6): d.line([(x + 2, n - 24), (x + 2, n)], fill=gh if (x // 6) % 2 else gd, width=3)
    save_tex("valance", im)
    # näyttämön taustakangas: sinisenä valaistu
    yy = np.linspace(0, 1, n)[:, None, None]; a = np.array((0.10, 0.30, 0.62))[None, None, :] * (0.45 + 0.9 * yy) + np.array((0.25, 0.20, 0.30))[None, None, :] * (1 - yy) ** 3 * 0.5
    save_tex("cyc", to_img(np.broadcast_to(a, (n, n, 3)).copy()))
    im = Image.new("RGB", (16, 16), (255, 236, 200)); save_tex("bulb", im)
    im = Image.new("RGB", (64, 32), (30, 150, 70)); d = ImageDraw.Draw(im); d.rectangle([24, 8, 34, 24], fill=(235, 245, 235)); d.polygon([(40, 16), (50, 8), (50, 24)], fill=(235, 245, 235)); save_tex("exitl", im)
    # ovet: permannolla tumma peiliovi, parvella vaalea harmaanbeige peiliovi
    for name, base, pan, frame in (("doord", (0.045, 0.026, 0.016), (0.07, 0.04, 0.022), (0.018, 0.01, 0.007)), ("doorb", C["beige"], (0.58, 0.47, 0.32), (0.30, 0.25, 0.20))):
        im = to_img(flat(n, base, 21, 0.08, 3, 50)); d = ImageDraw.Draw(im)
        for i in range(2):
            for (y0, y1) in ((16, 96), (108, 170), (182, 244)): d.rectangle([14 + i * 128, y0, 114 + i * 128, y1], fill=srgb(pan), outline=srgb(frame), width=4)
        d.line([(128, 0), (128, n)], fill=srgb(frame), width=5); d.rectangle([0, 0, n - 1, n - 1], outline=srgb(frame), width=6)
        d.ellipse([112, 124, 124, 136], fill=gd); d.ellipse([132, 124, 144, 136], fill=gd)
        save_tex(name, im)
    save_tex("ceil", ceiling_tex())
    foyer_textures()

def foyer_textures():
    n = 256; gd, gh, gs = srgb(C["gold"]), srgb((0.86, 0.68, 0.26)), srgb((0.30, 0.19, 0.04)); cr = srgb(C["cream"])
    from PIL import ImageFont
    def font(sz, it=False):
        for f in (("DejaVuSerif-Italic.ttf",) if it else ()) + ("DejaVuSerif-Bold.ttf", "DejaVuSerif.ttf"):
            try: return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/" + f, sz)
            except Exception: pass
        return ImageFont.load_default()
    # kiertokäytävän punainen seinä (salin ulkokaari): tasainen punainen, kultainen sapluunanauha 2,3 m korkeudella (v = 3 m)
    im = to_img(flat(512, (0.30, 0.035, 0.030), 41, 0.05, 6)); d = ImageDraw.Draw(im); Y = lambda z: 512 - z / 3.0 * 512
    d.rectangle([0, Y(0.12), 512, 512], fill=srgb((0.30, 0.19, 0.08)))
    d.line([(0, Y(2.42)), (512, Y(2.42))], fill=gd, width=4); d.line([(0, Y(2.10)), (512, Y(2.10))], fill=gd, width=4)
    for k in range(6):
        cx = k * 85.33 + 42; cy = Y(2.26)
        d.polygon([(cx, cy - 18), (cx + 14, cy), (cx, cy + 18), (cx - 14, cy)], outline=gd, width=3); d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=gh)
        for sx in (-1, 1): d.arc([cx + sx * 26 - 14, cy - 14, cx + sx * 26 + 14, cy + 14], 0, 360, fill=gd, width=3); d.line([(cx + sx * 14, cy), (cx + sx * 40, cy)], fill=gd, width=3)
    save_tex("corr", im)
    save_tex("fwall", to_img(flat(n, (0.66, 0.64, 0.46), 42, 0.03, 6)))
    save_tex("fceil", to_img(flat(n, (0.78, 0.76, 0.70), 43, 0.02, 6)))
    save_tex("white", to_img(flat(n, (0.84, 0.83, 0.79), 44, 0.02, 8)))
    save_tex("reveal", to_img(flat(n, (0.80, 0.78, 0.70), 45, 0.03, 4)))
    save_tex("mauve", to_img(flat(n, (0.36, 0.25, 0.27), 46, 0.03, 6)))
    save_tex("orange", to_img(flat(n, (0.55, 0.13, 0.05), 47, 0.04, 6)))
    # aulan lattia: tummanruskea laatta 0,3 m
    a = flat(n, (0.045, 0.030, 0.022), 48, 0.10, 6); rng = np.random.default_rng(4)
    for j in range(4):
        for i in range(4): a[j * 64:(j + 1) * 64, i * 64:(i + 1) * 64] *= 1 + rng.uniform(-0.25, 0.25)
    im = to_img(a); d = ImageDraw.Draw(im)
    for k in range(0, n, 64): d.line([(k, 0), (k, n)], fill=srgb((0.012, 0.009, 0.007)), width=2); d.line([(0, k), (n, k)], fill=srgb((0.012, 0.009, 0.007)), width=2)
    save_tex("ftile", im)
    # punainen kuviomatto (aulan takaosa ja käytävä)
    im = to_img(flat(n, (0.22, 0.035, 0.028), 49, 0.08, 14)); d = ImageDraw.Draw(im)
    for j in range(0, n, 32):
        for i in range(0, n, 32):
            ox = 16 if (j // 32) % 2 else 0; d.ellipse([i + ox + 8, j + 8, i + ox + 24, j + 24], outline=srgb((0.34, 0.10, 0.05)), width=3); d.ellipse([i + ox + 14, j + 14, i + ox + 18, j + 18], fill=srgb((0.40, 0.20, 0.08)))
    save_tex("rcarpet", im)
    # sitaattitaulu aukon yllä: Satakunta-lehden lause vuodelta 1874 (teksti omalla kirjasimella, taulun ulkoasua ei ole jäljennetty)
    W, H = 1024, 210; im = Image.new("RGB", (W, H), (236, 232, 214)); d = ImageDraw.Draw(im); d.rectangle([0, 0, W - 1, H - 1], outline=(52, 48, 44), width=8)
    f = font(44, True)
    for k, t in enumerate(("\u201dTeatteri on yht\u00e4 hy\u00f6dyllinen", "kuin kansakoulut ja yht\u00e4", "tarpeellinen kuin \u2013 sauna.\u201d")): d.text((W / 2, 40 + k * 50), t, font=f, fill=(40, 36, 30), anchor="mm")
    d.text((W - 150, H - 30), "Satakunta 14.2.1874", font=font(24, True), fill=(80, 74, 64), anchor="mm")
    save_tex("quote", im)
    im = Image.new("RGB", (256, 64), (236, 232, 214)); d = ImageDraw.Draw(im); d.rectangle([0, 0, 255, 63], outline=srgb(C["gold"]), width=5); d.text((128, 32), "KAHVILA  \u2191", font=font(30), fill=(40, 36, 30), anchor="mm"); save_tex("sign", im)
    # ulko-ovet: tumma puu, lasiruudut
    im = to_img(flat(n, (0.05, 0.028, 0.016), 50, 0.08, 3, 50)); d = ImageDraw.Draw(im)
    for i in range(2):
        d.rectangle([16 + i * 128, 14, 112 + i * 128, 150], fill=(150, 170, 180), outline=(20, 12, 8), width=4); d.line([(64 + i * 128, 14), (64 + i * 128, 150)], fill=(20, 12, 8), width=3); d.line([(16 + i * 128, 82), (112 + i * 128, 82)], fill=(20, 12, 8), width=3)
        d.rectangle([16 + i * 128, 166, 112 + i * 128, 240], outline=(20, 12, 8), width=4)
    d.line([(128, 0), (128, n)], fill=(12, 8, 6), width=5); save_tex("doorg", im)
    # kaari-ikkunat (valaisevat): vaalea lasi, puitejako
    for name, fr in (("glass_f", (225, 222, 205)), ("glass_c", (232, 228, 214))):
        W, H = 192, 400; a = np.ones((H, W, 3)) * np.array((0.86, 0.90, 0.92))[None, None, :] * (1 + 0.05 * fnoise(512, 51, 5)[:H, :W, None]); im = to_img(a); d = ImageDraw.Draw(im)
        d.line([(W / 2, 0), (W / 2, H)], fill=fr, width=9); d.line([(W / 4, 100), (W / 4, H)], fill=fr, width=4); d.line([(3 * W / 4, 100), (3 * W / 4, H)], fill=fr, width=4)
        for y in (100, 200, 300): d.line([(0, y), (W, y)], fill=fr, width=6 if y == 100 else 4)
        for k in range(1, 4): d.line([(W / 2, 100), (W / 2 + 130 * cos(pi * k / 4), 100 - 130 * sin(pi * k / 4))], fill=fr, width=4)
        d.rectangle([0, 0, W - 1, H - 1], outline=fr, width=10); save_tex(name, im)
    # kahvila: tumma oliivinruskea alapaneeli, kermanvärinen hammaslistareunus kultauksin, matto, marmori, ovet ja ovenpäällys
    im = to_img(flat(n, (0.070, 0.060, 0.040), 52, 0.08, 4, 30)); d = ImageDraw.Draw(im)
    for x in (0, 128): d.rectangle([x + 10, 34, x + 118, n - 26], outline=srgb((0.035, 0.03, 0.02)), width=4)
    d.rectangle([0, 0, n, 16], fill=srgb((0.11, 0.095, 0.065))); save_tex("cdado", im)
    im = to_img(flat(n, (0.74, 0.70, 0.58), 53, 0.03, 6)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, n, 30], fill=srgb((0.30, 0.05, 0.06))); d.line([(0, 34), (n, 34)], fill=gd, width=6)
    for x in range(0, n, 32): d.rectangle([x + 5, 60, x + 23, 100], fill=srgb((0.80, 0.76, 0.64)), outline=srgb((0.40, 0.36, 0.27)), width=2)
    for x in range(0, n, 64): d.ellipse([x + 14, 128, x + 50, 176], outline=gd, width=6); d.ellipse([x + 26, 142, x + 38, 162], fill=gh)
    d.line([(0, 116), (n, 116)], fill=srgb((0.40, 0.36, 0.27)), width=3); d.line([(0, 196), (n, 196)], fill=gd, width=5); d.rectangle([0, 226, n, n], fill=srgb((0.30, 0.22, 0.22)))
    save_tex("ccorn", im)
    N = 512; a = flat(N, (0.80, 0.79, 0.74), 54, 0.02, 6); im = to_img(a); d = ImageDraw.Draw(im)       # katto: valkoinen, viininpunainen reunanauha
    d.rectangle([14, 14, N - 15, N - 15], outline=srgb((0.25, 0.04, 0.05)), width=20); d.rectangle([40, 40, N - 41, N - 41], outline=gd, width=3); save_tex("cceil", im)
    g = fnoise(n, 55, 5); g2 = fnoise(n, 56, 14); a = np.array((0.050, 0.085, 0.080))[None, None, :] * (1 + 0.35 * g + 0.25 * g2)[..., None]
    v = np.clip(1 - np.abs(fnoise(n, 57, 7)) / 0.12, 0, 1) ** 2; a = a + v[..., None] * np.array((0.07, 0.09, 0.085))[None, None, :]
    save_tex("ccarpet", to_img(a))
    a = flat(n, (0.80, 0.78, 0.73), 58, 0.03, 4); v = np.clip(1 - np.abs(fnoise(n, 59, 6)) / 0.10, 0, 1) ** 2; save_tex("marble", to_img(a * (1 - 0.18 * v[..., None])))
    im = to_img(flat(n, (0.10, 0.060, 0.035), 60, 0.08, 3, 50)); d = ImageDraw.Draw(im)
    for i in range(2):
        for (y0, y1) in ((16, 70), (82, 170), (182, 244)): d.rectangle([14 + i * 128, y0, 114 + i * 128, y1], fill=srgb((0.13, 0.08, 0.045)), outline=srgb((0.05, 0.03, 0.018)), width=4)
    d.line([(128, 0), (128, n)], fill=srgb((0.04, 0.025, 0.015)), width=5); d.ellipse([112, 124, 124, 136], fill=gd); d.ellipse([132, 124, 144, 136], fill=gd); save_tex("doorc", im)
    W, H = 256, 96; im = to_img(flat(256, (0.62, 0.60, 0.56), 61, 0.03, 6)[:H]); d = ImageDraw.Draw(im)                 # ovenpäällys: harmaanvalkoinen lista, kullattu harjakoriste
    d.rectangle([0, 34, W, 44], fill=srgb((0.42, 0.40, 0.37))); d.rectangle([0, 60, W, 66], fill=srgb((0.42, 0.40, 0.37)))
    for x in range(6, W, 20): d.pieslice([x, 4, x + 16, 44], 180, 360, fill=gd, outline=gs); d.ellipse([x + 5, 0, x + 11, 8], fill=gh)
    for x in range(4, W, 16): d.rectangle([x, 46, x + 9, 58], fill=srgb((0.70, 0.68, 0.63)))
    save_tex("ped", im)

def ceiling_tex():
    """Katto ylhäältä katsottuna (u = x, v = y): okranvärinen ornamenttipohja, punainen kehärengas, keskellä kullattu ruusuke ja sen ympärillä
    seitsemän pyöreää taivasmaalausta. Maalaukset ovat OMIA pelkistettyjä piirroksia (taivas, pilvet, vaalea hahmo nauhoineen), eivät jäljennöksiä."""
    N = 1024; x0, x1 = CO, XP - CO; y0, y1 = -(R - CO), R - CO
    px = lambda x, y: ((x - x0) / (x1 - x0) * N, (y - y0) / (y1 - y0) * N)
    sx = N / (x1 - x0); sy = N / (y1 - y0)
    im = to_img(flat(N, C["ochre"], 31, 0.05, 8)); d = ImageDraw.Draw(im)
    gd, gh, gs, cr = srgb(C["gold"]), srgb((0.86, 0.68, 0.26)), srgb((0.30, 0.19, 0.04)), srgb(C["cream"])
    def ell(cx, cy, r, **kw): a = px(cx - r, cy - r); b = px(cx + r, cy + r); d.ellipse([a[0], a[1], b[0], b[1]], **kw)
    for k in range(60):                                    # pohjan köynnösornamentti
        an = k * 2 * pi / 60; rr = 5.0 + 0.35 * (k % 2); cx, cy = CX + rr * cos(an), rr * sin(an)
        ell(cx, cy, 0.22, outline=srgb((0.50, 0.30, 0.06)), width=4)
    for (cx, cy) in ((XP - CO - 0.9, 5.2), (XP - CO - 0.9, -5.2), (XP - CO - 0.9, 0)):
        ell(cx, cy, 0.7, fill=srgb((0.50, 0.58, 0.60)), outline=gd, width=8); ell(cx, cy, 0.3, fill=gh)
    ell(CX, 0, R - CO - 0.05, outline=srgb((0.45, 0.06, 0.05)), width=int(0.30 * sx)); ell(CX, 0, R - CO - 0.38, outline=gd, width=7); ell(CX, 0, R - CO - 0.02, outline=cr, width=6)
    rng = np.random.default_rng(5)
    hues = [(0.75, 0.20, 0.20), (0.20, 0.35, 0.65), (0.75, 0.60, 0.15), (0.25, 0.50, 0.30), (0.60, 0.30, 0.55), (0.80, 0.42, 0.18), (0.30, 0.55, 0.62)]
    for k in range(7):
        an = pi + k * 2 * pi / 7; cx, cy = CX + 3.55 * cos(an), 3.55 * sin(an); r = 1.36; S = int(2 * r * sx)
        t = Image.new("RGB", (S, S)); q = ImageDraw.Draw(t)
        for y in range(S): f = y / S; q.line([(0, y), (S, y)], fill=srgb(tuple(a * (1 - 0.55 * f) + b * 0.55 * f for a, b in zip(C["sky"], (0.80, 0.68, 0.52)))))
        for j in range(7):                                 # pilvet
            ux, uy, w = rng.uniform(0.1, 0.9) * S, rng.uniform(0.45, 0.92) * S, rng.uniform(0.16, 0.30) * S
            q.ellipse([ux - w, uy - w * 0.45, ux + w, uy + w * 0.45], fill=srgb((0.80, 0.74, 0.66)) if j % 2 else srgb((0.72, 0.62, 0.58)))
        t = t.filter(ImageFilter.GaussianBlur(S / 40)); q = ImageDraw.Draw(t)
        skin = srgb((0.78, 0.58, 0.46)); hx, hy = S * (0.5 + rng.uniform(-0.06, 0.06)), S * 0.36     # pelkistetty leijuva hahmo: pää, vartalo, siivet, värinauha
        q.ellipse([hx - S * 0.17, hy + S * 0.02, hx - S * 0.02, hy + S * 0.16], fill=srgb((0.88, 0.86, 0.80))); q.ellipse([hx + S * 0.02, hy + S * 0.02, hx + S * 0.17, hy + S * 0.16], fill=srgb((0.88, 0.86, 0.80)))
        q.ellipse([hx - S * 0.075, hy + S * 0.04, hx + S * 0.075, hy + S * 0.30], fill=skin); q.ellipse([hx - S * 0.06, hy - S * 0.08, hx + S * 0.06, hy + S * 0.05], fill=skin)
        q.pieslice([hx - S * 0.065, hy - S * 0.09, hx + S * 0.065, hy + S * 0.03], 180, 360, fill=srgb((0.50, 0.33, 0.14)))
        q.line([(hx - S * 0.06, hy + S * 0.12), (hx - S * 0.2, hy + S * 0.22)], fill=skin, width=max(3, S // 28)); q.line([(hx + S * 0.06, hy + S * 0.12), (hx + S * 0.22, hy + S * 0.06)], fill=skin, width=max(3, S // 28))
        q.arc([hx - S * 0.30, hy + S * 0.10, hx + S * 0.30, hy + S * 0.44], 10, 170, fill=srgb(hues[k]), width=max(4, S // 18))
        m = Image.new("L", (S, S), 0); ImageDraw.Draw(m).ellipse([2, 2, S - 3, S - 3], fill=255)
        t = t.rotate(-math.degrees(an) - 90, resample=Image.BICUBIC); c = px(cx, cy); im.paste(t, (int(c[0] - S / 2), int(c[1] - S / 2)), m)
        ell(cx, cy, r, outline=gd, width=11); ell(cx, cy, r + 0.07, outline=gs, width=3); ell(cx, cy, r - 0.09, outline=gh, width=3)
    for k in range(7):                                     # kehysten väliin pienet kullatut ruusukkeet
        an = pi + (k + 0.5) * 2 * pi / 7; ell(CX + 5.0 * cos(an), 5.0 * sin(an), 0.33, fill=gd, outline=gs, width=3); ell(CX + 5.0 * cos(an), 5.0 * sin(an), 0.14, fill=gh)
    ell(CX, 0, 1.75, fill=srgb((0.50, 0.30, 0.06)), outline=gd, width=9)
    for k in range(16): an = k * pi / 8; c = (CX + 1.15 * cos(an), 1.15 * sin(an)); ell(c[0], c[1], 0.36, fill=gd if k % 2 else gh, outline=gs, width=3)
    ell(CX, 0, 0.8, fill=gh, outline=gs, width=4); ell(CX, 0, 0.35, fill=gs)
    return im

# ---------------------------------------------------------------- apurit
def dpts(off, xend=None, na=28, closed=False):
    """Salin pohjan (suorat sivut + takakaari) sisäänpäin siirretty reuna: (xend, -r) -> takakaaren kautta -> (xend, +r)."""
    r = R - off; xend = XP if xend is None else xend
    p = [(xend, -r)] + [(CX + r * cos(radians(-90 - 180 * i / na)), r * sin(radians(-90 - 180 * i / na))) for i in range(na + 1)] + [(xend, r)]
    return p + [p[0]] if closed else p
inD = lambda x, y, off: (hypot(x - CX, y) < R - off) if x < CX else abs(y) < R - off
def strip(pa, pb, za, zb, mat, uvs=None, **kw):
    """Nauha kahden yhtä pitkän murtoviivan välissä (a korkeudella za, b korkeudella zb)."""
    L = 0.0
    for i in range(len(pa) - 1):
        l = math.dist(pa[i], pa[i + 1]); q = [(*pa[i], za), (*pa[i + 1], za), (*pb[i + 1], zb), (*pb[i], zb)]
        uv = None if uvs is None else [(L / uvs[0], uvs[1]), ((L + l) / uvs[0], uvs[1]), ((L + l) / uvs[0], uvs[2]), (L / uvs[0], uvs[2])]
        G.face(q, mat, uv=uv, **kw); L += l
def obox(cx, cy, ang, x0, x1, y0, y1, z0, z1, mat, skip="", taper=0.0):
    """Suuntaan ang käännetty laatikko (paikallinen x eteenpäin, y vasemmalle); taper kaventaa yläpäätä sivuilta."""
    c, s = cos(ang), sin(ang); W = lambda lx, ly, z: (cx + c * lx - s * ly, cy + s * lx + c * ly, z)
    b = [W(x0, y0, z0), W(x1, y0, z0), W(x1, y1, z0), W(x0, y1, z0)]; t = [W(x0, y0 + taper, z1), W(x1, y0 + taper, z1), W(x1, y1 - taper, z1), W(x0, y1 - taper, z1)]
    cen = W((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    for k, name in enumerate(("y-", "x+", "y+", "x-")):
        if name not in skip: G.face([b[k], b[(k + 1) % 4], t[(k + 1) % 4], t[k]], mat, away=cen)
    if "z+" not in skip: G.face(t, mat, up=True)
    if "z-" not in skip: G.face(b, mat, up=False)
def seat(x, y, ang, z, arm_r=False):
    obox(x, y, ang, -0.05, 0.42, -0.245, 0.245, z + 0.36, z + 0.47, "seat")
    obox(x, y, ang, -0.17, -0.05, -0.25, 0.25, z + 0.20, z + 0.88, "seat", skip="z+z-"); obox(x, y, ang, -0.17, -0.05, -0.25, 0.25, z + 0.88, z + 1.0, "seat", skip="z-", taper=0.09)
    obox(x, y, ang, -0.17, 0.36, 0.25, 0.30, z, z + 0.62, "seatwood", skip="z-")
    if arm_r: obox(x, y, ang, -0.17, 0.36, -0.30, -0.25, z, z + 0.62, "seatwood", skip="z-")
def door(px, py, nx, ny, w, h, z0, mat, exit_sign=True):
    """Ovi seinän edessä: (px, py) oven keskikohta seinällä, (nx, ny) normaali saliin päin."""
    tx, ty = -ny, nx; P = lambda s, z, o: (px + tx * s + nx * o, py + ty * s + ny * o, z); tw = (px + nx * 5, py + ny * 5, z0 + 1)
    G.face([P(-w / 2, z0, 0.08), P(w / 2, z0, 0.08), P(w / 2, z0 + h, 0.08), P(-w / 2, z0 + h, 0.08)], mat, uv=[(0, 0), (1, 0), (1, 1), (0, 1)], toward=tw)
    fm = "cream" if mat == "doorb" else "dado"
    for s0, s1, za, zb in ((-w / 2 - 0.14, -w / 2, z0, z0 + h), (w / 2, w / 2 + 0.14, z0, z0 + h), (-w / 2 - 0.14, w / 2 + 0.14, z0 + h, z0 + h + 0.16)):
        G.face([P(s0, za, 0.12), P(s1, za, 0.12), P(s1, zb, 0.12), P(s0, zb, 0.12)], fm, toward=tw)
    if exit_sign: G.face([P(-0.2, z0 + h + 0.28, 0.13), P(0.2, z0 + h + 0.28, 0.13), P(0.2, z0 + h + 0.46, 0.13), P(-0.2, z0 + h + 0.46, 0.13)], "exitl", uv=[(0, 0), (1, 0), (1, 1), (0, 1)], toward=tw)
arch = lambda y, a, zs, r: zs + r * sqrt(max(0.0, 1 - (y / a) ** 2))

def build():
    LAMPS = []                                             # (x, y, z, teho W, väri)
    top = lambda s: ZW + 0.01; bands = ((1.0, "dado"), (ZW - 0.45, "wallred"), (1e9, "frieze"))
    # --- salin seinät (sivuilla oviaukot kiertokäytävään), lattia, holkka ja katto
    D0 = dpts(0)
    for a, b in zip(D0[1:-1], D0[2:-1]): wall(a, b, top, (CX + 2, 0), bands=bands)
    for s in (1, -1):
        wall((CX, s * R), (DX0, s * R), top, (CX + 2, 0), bands=bands); wall((DX1, s * R), (XP, s * R), top, (CX + 2, 0), bands=bands)
        wall((DX0, s * R), (DX1, s * R), top, (CX + 2, 0), bands=((ZW - 0.45 - DH, "wallred"), (1e9, "frieze")), zbase=DH, coll=False)
        for x in (DX0, DX1):
            G.face([(x, s * R, 0), (x, s * (R + WT), 0), (x, s * (R + WT), DH), (x, s * R, DH)], "dado", toward=((DX0 + DX1) / 2, s * R, 1)); COL["seg"].append([x, s * R, x, s * (R + WT), 0.05])
        G.face([(DX0, s * R, DH), (DX1, s * R, DH), (DX1, s * (R + WT), DH), (DX0, s * (R + WT), DH)], "dado", up=False)
        G.face([(DX0, s * R, 0.004), (DX1, s * R, 0.004), (DX1, s * (R + WT), 0.004), (DX0, s * (R + WT), 0.004)], "rcarpet", up=True)
        G.face([(DX0 + 0.5, s * (R - 0.02), DH + 0.2), (DX1 - 0.5, s * (R - 0.02), DH + 0.2), (DX1 - 0.5, s * (R - 0.02), DH + 0.38), (DX0 + 0.5, s * (R - 0.02), DH + 0.38)], "exitl", uv=[(0, 0), (1, 0), (1, 1), (0, 1)], toward=(9, 0, 2))
    fl = dpts(0, XS)
    G.face([(x, y, 0) for x, y in fl], "carpet", up=True)
    for j in range(5):
        o0, o1 = CO * (1 - cos(j / 5 * pi / 2)), CO * (1 - cos((j + 1) / 5 * pi / 2)); z0, z1 = ZW + (ZT - ZW) * sin(j / 5 * pi / 2), ZW + (ZT - ZW) * sin((j + 1) / 5 * pi / 2)
        strip(dpts(o0, XP - o0, closed=True), dpts(o1, XP - o1, closed=True), z0, z1, "cove", uvs=(0.8, j / 5, (j + 1) / 5), toward=(CX, 0, 5))
    cp = dpts(CO, XP - CO); x0, x1, y0, y1 = CO, XP - CO, -(R - CO), R - CO; cuv = lambda p: ((p[0] - x0) / (x1 - x0), 1 - (p[1] - y0) / (y1 - y0))
    for a, b in zip(cp, cp[1:]): G.face([(CX + 1, 0, ZT), (*a, ZT), (*b, ZT)], "ceil", uv=[cuv((CX + 1, 0)), cuv(a), cuv(b)], up=False)
    G.face([(CX + 1, 0, ZT), (*cp[-1], ZT), (*cp[0], ZT)], "ceil", uv=[cuv((CX + 1, 0)), cuv(cp[-1]), cuv(cp[0])], up=False)
    # --- ovet: sisäänkäynti takana keskellä, sivuovet permannolla, kolme ovea parvella
    for an in (0, 42, -42):
        a = radians(180 + an); door(CX + R * cos(a) * 0.997, R * sin(a) * 0.997, -cos(a), -sin(a), 1.2, 2.2, BFB, "doorb")
    # --- parvi: alapinta, kaide, lattiatasot, päädyt
    Bf, Bi, Bt, Bw = dpts(BO, XBE), dpts(BO - 0.12, XBE), dpts(BT, XBE), dpts(0, XBE)
    strip(Bf, Bw, BZ0, BZ0, "under", up=False)
    strip(Bf, Bf, BZ0, BZ1, "balfront", uvs=(1.6, 0, 1), toward=(CX + 2, 0, 3.6))
    strip(Bi, Bi, BFA, BZ1, "cream", away=(CX + 2, 0, 3.6)); strip(Bf, Bi, BZ1, BZ1, "cream", up=True)
    strip(Bi, Bt, BFA, BFA, "carpet", up=True); strip(Bt, Bt, BFA, BFB, "dado", toward=(CX + 2, 0, 3.6)); strip(Bt, Bw, BFB, BFB, "carpet", up=True)
    for s in (1, -1):
        G.face([(XBE, s * (R - BO), BZ0), (XBE, s * R, BZ0), (XBE, s * R, BZ1), (XBE, s * (R - BO), BZ1)], "balfront", uv=[(0, 0), (BO / 1.6, 0), (BO / 1.6, 1), (0, 1)], toward=(XP + 5, 0, 3.6))
        G.face([(XBE - 0.12, s * (R - BO), BFA), (XBE - 0.12, s * R, BFA), (XBE - 0.12, s * R, BZ1), (XBE - 0.12, s * (R - BO), BZ1)], "cream", toward=(0, s * 5, 3.6))
        G.face([(XBE - 0.12, s * (R - BO), BZ1), (XBE, s * (R - BO), BZ1), (XBE, s * R, BZ1), (XBE - 0.12, s * R, BZ1)], "cream", up=True)
    G.small = True                                         # kaiteen messinkijohde ja parven alapinnan valot
    rl = dpts(BO - 0.06, XBE)
    for a, b in zip(rl, rl[1:]):
        m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2); ang = atan2(b[1] - a[1], b[0] - a[0]); L = math.dist(a, b)
        obox(m[0], m[1], ang, -L / 2, L / 2, -0.02, 0.02, BZ1 + 0.10, BZ1 + 0.14, "gold", skip="x+x-")
    def along(pts, step, s0=0.0):
        acc = -s0; out = []
        for a, b in zip(pts, pts[1:]):
            L = math.dist(a, b); t = -acc if acc < 0 else (step - acc % step) % step if acc else 0.0
            t = (-acc) if acc < 0 else ((step - (acc % step)) % step)
            while t <= L + 1e-9: out.append((a[0] + (b[0] - a[0]) * t / L, a[1] + (b[1] - a[1]) * t / L, atan2(b[1] - a[1], b[0] - a[0]))); t += step
            acc += L
        return out
    for (x, y, an) in along(dpts(1.35, XBE - 0.6), 2.3, 1.0):
        G.face([(x + 0.11 * cos(k * pi / 4), y + 0.11 * sin(k * pi / 4), BZ0 - 0.012) for k in range(8)], "bulb", uv=[(0.5, 0.5)] * 8, up=False); LAMPS.append((x, y, BZ0 - 0.25, 30, (1.0, 0.80, 0.55)))
    G.small = False
    # --- istuimet: permanto (kaarevat rivit, keskikäytävä ja reunakäytävät), parvi (kaksi riviä)
    nseat = 0
    for k in range(12):
        rho = XA - 11.4 + 0.88 * k
        for s in (1, -1):
            row = []
            for i in range(14):
                phi = s * (0.80 + 0.28 + 0.56 * i) / rho; x, y = XA - rho * cos(phi), rho * sin(phi)
                if inD(x - 0.15, y, 1.25) and inD(x + 0.4, y, 1.25) and inD(x, y + s * 0.3, 1.25): row.append((x, y, atan2(-y, XA - x)))
            for j, (x, y, an) in enumerate(row): seat(x, y, an, 0.0, arm_r=(j == 0 if s > 0 else j == len(row) - 1) or True if False else (j == (0 if s > 0 else len(row) - 1))); nseat += 1
            if row: COL["seg"].append([row[0][0] + 0.12, row[0][1] - s * 0.1, row[-1][0] + 0.12, row[-1][1] + s * 0.15, 0.36])
    nb = 0
    for off, z in ((BO - 0.62, BFA), (0.78, BFB)):
        pts = dpts(off, XBE - 0.5); S = along(pts, 0.60, 0.4)
        for j, (x, y, an) in enumerate(S):
            if off < 1 and any(hypot(x - (CX + (R - off) * cos(radians(180 + d))), y - (R - off) * sin(radians(180 + d))) < 1.0 for d in (0, 42, -42)): continue
            seat(x, y, an + pi / 2, z, arm_r=(j == 0)); nb += 1
    print("istuimia: permanto", nseat, "parvi", nb)
    # --- näyttämö: etureuna, portaat, lattia
    G.face([(XS, -SY0, 0), (XS, SY0, 0), (XS, SY0, ZST), (XS, -SY0, ZST)], "dado", toward=(0, 0, 0.5))
    G.face([(XS, -R, ZST), (XP, -R, ZST), (XP, R, ZST), (XS, R, ZST)], "stagefloor", up=True)
    G.face([(XP, -A0, ZST), (XI, -A1, ZST), (XI, A1, ZST), (XP, A0, ZST)], "stagefloor", up=True)
    G.face([(XI, -SW, ZST), (XE, -SW, ZST), (XE, SW, ZST), (XI, SW, ZST)], "stagefloor", up=True)
    lev = [[XS, -R, XP, R, ZST], [XP, -SW, XE, SW, ZST]]
    for s in (1, -1):
        ya, yb = min(s * SY0, s * R), max(s * SY0, s * R)
        for k in range(NST):
            xa = XS - (NST - k) * STW; z = STH * (k + 1)
            G.face([(xa, ya, z - STH), (xa, yb, z - STH), (xa, yb, z), (xa, ya, z)], "dado", toward=(0, s * 6, z))
            if k < NST - 1: G.face([(xa, ya, z), (xa + STW, ya, z), (xa + STW, yb, z), (xa, yb, z)], "carpet", up=True)
            G.face([(xa, s * SY0, 0), (xa + STW, s * SY0, 0), (xa + STW, s * SY0, z), (xa, s * SY0, z)], "dado", toward=(xa, 0, 0.3))
            lev.append([xa, ya, xa + STW if k < NST - 1 else XS, yb, z])
    # --- näyttämöaukon seinä: pilarit, kaari, pielet, kehyslista, kilpi
    ys = [-R + 2 * R * i / 48 for i in range(49)]
    lo = lambda y: max(ZST, arch(y, A0, Z0, R0)) if abs(y) < A0 else ZST
    for ya, yb in zip(ys, ys[1:]):
        la, lb = lo(ya), lo(yb)
        if abs((ya + yb) / 2) < A0 and min(la, lb) <= ZST + 1e-6: la, lb = max(la, Z0 if abs(ya) < A0 - 1e-6 else ZST), max(lb, Z0 if abs(yb) < A0 - 1e-6 else ZST)
        if abs((ya + yb) / 2) < A0: la, lb = arch(ya, A0, Z0, R0) if abs(ya) < A0 else Z0, arch(yb, A0, Z0, R0) if abs(yb) < A0 else Z0
        G.face([(XP, ya, la), (XP, yb, lb), (XP, yb, ZW - 0.45), (XP, ya, ZW - 0.45)], "pink", toward=(0, 0, 5))
        G.face([(XP, ya, ZW - 0.45), (XP, yb, ZW - 0.45), (XP, yb, ZW + 0.01), (XP, ya, ZW + 0.01)], "frieze", uv=[(ya / 0.45, 0), (yb / 0.45, 0), (yb / 0.45, 1.0), (ya / 0.45, 1.0)], toward=(0, 0, 5))
    for s in (1, -1):
        ya, yb = s * (A0 + 0.22), s * (R - 0.04)
        G.face([(XP - 0.03, ya, ZST), (XP - 0.03, yb, ZST), (XP - 0.03, yb, ZST + 6.6), (XP - 0.03, ya, ZST + 6.6)], "pier", uv=[(0, 0), (1, 0), (1, 1), (0, 1)], toward=(0, 0, 4))
        G.face([(XP, s * A0, ZST), (XI, s * A1, ZST), (XI, s * A1, Z1), (XP, s * A0, Z0)], "jamb", uv=[(0, 0), (1, 0), (1, (Z1 - ZST) / 2), (0, (Z0 - ZST) / 2)], toward=(XP, 0, 3))
        G.face([(XP - 0.05, s * A0, ZST), (XP - 0.05, s * (A0 + 0.36), ZST), (XP - 0.05, s * (A0 + 0.36), Z0), (XP - 0.05, s * A0, Z0)], "archiv", uv=[(0, 0), (1, 0), (1, Z0 - ZST), (0, Z0 - ZST)], toward=(0, 0, 3))
        COL["seg"] += [[XP, s * R, XP, s * A0, 0.06], [XP, s * A0, XI, s * A1, 0.06], [XI, s * A1, XI, s * SW, 0.06]]
    NA = 28; L = 0.0
    for i in range(NA):
        t0, t1 = pi * i / NA, pi * (i + 1) / NA
        o0, o1 = (XP, A0 * cos(t0), Z0 + R0 * sin(t0)), (XP, A0 * cos(t1), Z0 + R0 * sin(t1)); i0, i1 = (XI, A1 * cos(t0), Z1 + R1 * sin(t0)), (XI, A1 * cos(t1), Z1 + R1 * sin(t1))
        l = math.dist(o0, o1); G.face([o0, o1, i1, i0], "prosc", uv=[(L / 1.5, 0), ((L + l) / 1.5, 0), ((L + l) / 1.5, 1), (L / 1.5, 1)], toward=((XP + XI) / 2, 0, 3.5))
        w = 0.36; e0, e1 = (XP - 0.05, (A0 + w) * cos(t0), Z0 + (R0 + w) * sin(t0)), (XP - 0.05, (A0 + w) * cos(t1), Z0 + (R0 + w) * sin(t1))
        G.face([(XP - 0.05, o0[1], o0[2]), (XP - 0.05, o1[1], o1[2]), e1, e0], "archiv", uv=[(0, L), (0, L + l), (1, L + l), (1, L)], toward=(0, 0, 5)); L += l
    G.box(XP - 0.10, XP, -1.7, 1.7, 7.02, 7.72, "cream", skip="x+")
    G.face([(XP - 0.105, -1.6, 7.07), (XP - 0.105, 1.6, 7.07), (XP - 0.105, 1.6, 7.67), (XP - 0.105, -1.6, 7.67)], "cartouche", uv=[(1, 0), (0, 0), (0, 1), (1, 1)], toward=(0, 0, 7))
    # --- näyttämö: mustat seinät ja katto, taustakangas, sivuverhot ja kujat
    bb = ((1e9, "black"),); ZH = 10.0
    for s in (1, -1): wall((XI, s * SW), (XE, s * SW), lambda q: ZH, (20, 0), bands=bb, zbase=ZST)
    wall((XE, -SW), (XE, SW), lambda q: ZH, (20, 0), bands=bb, zbase=ZST)
    G.face([(XI, -SW, ZH), (XE, -SW, ZH), (XE, SW, ZH), (XI, SW, ZH)], "black", up=False)
    ys = [-SW + 2 * SW * i / 40 for i in range(41)]
    for ya, yb in zip(ys, ys[1:]):
        la = arch(ya, A1, Z1, R1) if abs(ya) < A1 else (Z1 if abs((ya + yb) / 2) < A1 else ZST); lb = arch(yb, A1, Z1, R1) if abs(yb) < A1 else (Z1 if abs((ya + yb) / 2) < A1 else ZST)
        G.face([(XI, ya, la), (XI, yb, lb), (XI, yb, ZH), (XI, ya, ZH)], "black", toward=(20, 0, 5))
    G.face([(XE - 0.35, -6.6, ZST), (XE - 0.35, 6.6, ZST), (XE - 0.35, 6.6, 8.6), (XE - 0.35, -6.6, 8.6)], "cyc", uv=[(0, 0), (1, 0), (1, 1), (0, 1)], toward=(20, 0, 4))
    COL["seg"].append([XE - 0.35, -6.6, XE - 0.35, 6.6, 0.08])
    for x in (18.6, 22.0):
        for s in (1, -1):
            G.face([(x, s * 5.3, ZST), (x, s * SW, ZST), (x, s * SW, ZH), (x, s * 5.3, ZH)], "black", toward=(x - 5, 0, 4)); G.face([(x + 0.02, s * 5.3, ZST), (x + 0.02, s * SW, ZST), (x + 0.02, s * SW, ZH), (x + 0.02, s * 5.3, ZH)], "black", toward=(x + 5, 0, 4))
            COL["seg"].append([x, s * 5.3, x, s * SW, 0.1])
    for x in (17.2, 20.6, 23.6): G.face([(x, -SW, 6.7), (x, SW, 6.7), (x, SW, ZH), (x, -SW, ZH)], "black", toward=(x - 5, 0, 5))
    # --- esirippu auki sivuilla ja kappa aukon yläreunassa
    xc = XI + 0.16; ys = [-A1 + 2 * A1 * i / 36 for i in range(37)]
    for ya, yb in zip(ys, ys[1:]):
        ta, tb = arch(ya, A1, Z1, R1) + 0.05, arch(yb, A1, Z1, R1) + 0.05; ba, bb_ = 5.0 + 0.28 * abs(sin(pi * ya / 1.5)), 5.0 + 0.28 * abs(sin(pi * yb / 1.5))
        if min(ta - ba, tb - bb_) < 0.02: ta, tb = max(ta, ba + 0.02), max(tb, bb_ + 0.02)
        G.face([(xc, ya, ba), (xc, yb, bb_), (xc, yb, tb), (xc, ya, ta)], "valance", uv=[(ya, 0), (yb, 0), (yb, 1), (ya, 1)], toward=(0, 0, 5))
    xc = XI + 0.34; zs = [ZST, 1.8, 2.4, 2.9, 3.6, 4.6, 5.6, 6.4]; NF = 8
    for s in (1, -1):
        yin = lambda z: 3.25 + 0.75 * math.exp(-((z - 2.6) / 0.8) ** 2) - 0.25 * (z - ZST) / 5.4
        P = lambda j, i: (xc + 0.09 * (1 if i % 2 else -1) * (0.5 + 0.5 * abs(zs[j] - 2.6) / 3.8), s * (yin(zs[j]) + (A1 + 0.5 - yin(zs[j])) * i / NF), zs[j])
        for j in range(len(zs) - 1):
            for i in range(NF):
                G.face([P(j, i), P(j, i + 1), P(j + 1, i + 1), P(j + 1, i)], "curtain", uv=[(i * 0.25, zs[j] / 2), ((i + 1) * 0.25, zs[j] / 2), ((i + 1) * 0.25, zs[j + 1] / 2), (i * 0.25, zs[j + 1] / 2)], toward=(0, s * 3, 3))
        G.small = True; obox(xc - 0.1, s * 3.95, 0, -0.03, 0.03, -0.16, 0.16, 2.5, 2.7, "gold"); G.small = False
        COL["seg"].append([xc, s * 3.3, xc, s * (A1 + 0.5), 0.2])
    # --- kattokruunu (kullattu, valkoiset kuvut) ja valotanko aukon edessä
    G.small = True
    cx, zc = CX, 6.9
    G.cyl(cx, 0, zc + 1.2, ZT, 0.025, 5, "gold"); G.cyl(cx, 0, zc - 0.55, zc + 1.2, 0.09, 8, "gold"); G.cyl(cx, 0, zc - 0.85, zc - 0.55, 0.0, 8, "gold", r1=0.22); G.cyl(cx, 0, zc + 0.2, zc + 0.55, 0.34, 8, "gold", r1=0.09)
    G.cyl(cx, 0, zc - 0.25, zc - 0.05, 0.16, 8, "gold", r1=0.42); G.cyl(cx, 0, zc - 0.05, zc + 0.2, 0.42, 8, "gold", r1=0.34)
    def globe(x, y, z, r):
        G.cyl(x, y, z - r, z, 0.0, 6, "bulb", r1=r); G.cyl(x, y, z, z + r, r, 6, "bulb", r1=0.0)
    for (rr, zz, nn, gr) in ((1.25, zc - 0.1, 12, 0.11), (0.8, zc + 0.55, 8, 0.10), (0.45, zc - 0.6, 6, 0.09)):
        for k in range(nn):
            a = 2 * pi * (k + 0.5 * (nn == 8)) / nn; ex, ey = cx + rr * cos(a), rr * sin(a)
            for sd in (1, -1): G.face([(cx, 0, zz - 0.22), (ex, ey, zz - 0.16), (ex, ey, zz - 0.09), (cx, 0, zz - 0.12)], "gold", toward=(cx + 9 * cos(a + sd * 1.57), 9 * sin(a + sd * 1.57), zz))
            G.cyl(ex, ey, zz - 0.16, zz - 0.06, 0.03, 5, "gold", r1=0.07); globe(ex, ey, zz + 0.05, gr)
    LAMPS.append((cx, 0, zc - 1.3, 1500, (1.0, 0.82, 0.60)))
    xb, zb = 11.9, 7.35
    G.box(xb - 0.03, xb + 0.03, -4.2, 4.2, zb, zb + 0.06, "black")
    for y in (-4.2, 4.2): G.cyl(xb, y, zb + 0.06, ZT - 0.2, 0.012, 4, "black")
    for k in range(9):
        y = -3.6 + 0.9 * k; G.cyl(xb + 0.05, y, zb - 0.42, zb - 0.1, 0.13, 8, "black", r1=0.11); G.face([(xb + 0.05 + 0.12 * cos(i * pi / 4), y + 0.12 * sin(i * pi / 4), zb - 0.42) for i in range(8)], "black", up=False)
    G.small = False
    for (x, y) in ((17.5, 3.2), (17.5, -3.2), (21.5, 3.2), (21.5, -3.2)): LAMPS.append((x, y, 8.6, 380, (0.80, 0.88, 1.0)))
    LAMPS.append((XP - 1.2, 0, 7.4, 260, (1.0, 0.86, 0.70)))    # etunäyttämön valo
    foyer(LAMPS); cafe(LAMPS)
    arc = [[CX + RO * cos(radians(a)), RO * sin(radians(a))] for a in np.linspace(360 - PHI1, 270, 12)]
    env = [[XF, -FY], [XFB, -FY]] + arc + [[10.8, -RO], [10.8, -R], [XP, -R], [XP, -A0], [XI, -A1], [XI, -SW], [XE, -SW]]
    env = env + [[x, -y] for x, y in reversed(env)]
    rooms = [env, [[XO + XF, -KW], [XO + XFB + 1.6, -KW], [XO + XFB + 1.6, KW], [XO + XF, KW]]]
    ports = [[-6.5, FY - 0.5, 1.3, XO - 6.55, KW - 0.75, pi, "yl\u00e4kertaan kahvilaan"], [XO - 6.55, KW - 0.4, 1.2, -6.5, FY - 1.0, pi, "alakertaan aulaan"]]
    return LAMPS, lev, rooms, ports

def foyer(LAMPS):
    """Aula ja kiertokäytävä: salin pyöreä punainen ulkoseinä näkyy aulan takaseinän aukosta, ja sen kummaltakin puolelta kierretään salin sivuoville."""
    fb = ((0.12, "dado"), (1e9, "fwall")); ft = lambda q: FH; ct = lambda q: CH
    # aula: julkisivuseinä (ikkunat, kolme ulko-ovea), päädyt, takaseinä aukkoineen
    wall((XF, -FY), (XF, FY), ft, (0, 0), [K.Win(FY + y, 1.5, 1.0, 2.9, 0.75, "glass_f") for y in (-8.3, -5.6, 5.6, 8.3)], bands=fb)
    for y in (-2.7, 0, 2.7): door(XF, y, 1, 0, 1.7, 2.6, 0.0, "doorg", exit_sign=(y == 0))
    for s in (1, -1):
        wall((XF, s * FY), (XFB, s * FY), ft, (-6, 0), bands=fb); wall((XFB, s * FO), (XFB, s * FY), ft, (-6, 0), bands=fb)
    wall((XFB, -FO), (XFB, FO), ft, (-6, 0), bands=((1e9, "fwall"),), zbase=CH, coll=False)
    G.face([(XFB - 0.03, -2.3, 3.33), (XFB - 0.03, 2.3, 3.33), (XFB - 0.03, 2.3, 4.27), (XFB - 0.03, -2.3, 4.27)], "quote", uv=[(1, 0), (0, 0), (0, 1), (1, 1)], toward=(-6, 0, 3.8))
    G.face([(XF, -FY, 0), (-4.2, -FY, 0), (-4.2, FY, 0), (XF, FY, 0)], "ftile", up=True); G.face([(-4.2, -FY, 0), (XFB, -FY, 0), (XFB, FY, 0), (-4.2, FY, 0)], "rcarpet", up=True)
    G.face([(XF, -FY, FH), (XFB, -FY, FH), (XFB, FY, FH), (XF, FY, FH)], "fceil", up=False)
    door(-6.5, FY, 0, -1, 1.3, 2.3, 0.0, "doorb", exit_sign=False)                       # ovi portaaseen: yläkerran kahvila
    G.face([(-7.0, FY - 0.13, 2.6), (-6.0, FY - 0.13, 2.6), (-6.0, FY - 0.13, 2.85), (-7.0, FY - 0.13, 2.85)], "sign", uv=[(1, 0), (0, 0), (0, 1), (1, 1)], toward=(-6.5, 0, 2.7))
    G.box(-5.45, -4.95, -FY, FY, FH - 0.42, FH, "white", skip="z+")                       # kattopalkki pylväslinjalla
    for y in (-7.7, -2.9, 2.9, 7.7):                                                    # valkoiset pylväät, messinkiset pallovalaisimet
        x = -5.2; G.cyl(x, y, 0, 0.25, 0.37, 14, "white", r1=0.33); G.cyl(x, y, 0.25, FH - 0.7, 0.30, 14, "white"); G.cyl(x, y, FH - 0.7, FH - 0.42, 0.30, 14, "white", r1=0.42)
        COL["circ"].append([x, y, 0.38])
        G.small = True; G.cyl(x, y, 2.50, 2.62, 0.33, 12, "gold")
        for k in range(4):
            a = pi / 4 + k * pi / 2; gx, gy = x + 0.52 * cos(a), y + 0.52 * sin(a)
            obox(x + 0.42 * cos(a), y + 0.42 * sin(a), a, -0.1, 0.1, -0.025, 0.025, 2.53, 2.58, "gold"); G.cyl(gx, gy, 2.58, 2.66, 0.05, 6, "gold")
            G.cyl(gx, gy, 2.66, 2.80, 0.0, 6, "bulb", r1=0.13); G.cyl(gx, gy, 2.80, 2.94, 0.13, 6, "bulb", r1=0.0)
        G.small = False
        LAMPS.append((x - 0.8, y, 2.9, 70, (1.0, 0.84, 0.62))); LAMPS.append((x + 0.8, y, 2.9, 70, (1.0, 0.84, 0.62)))
    # kiertokäytävä: sisäseinä = salin ulkopinta (punainen, kultanauha), ulkoseinä vaalea
    ri = R + WT; na = 28
    inner = [(10.8, -ri)] + [(CX + ri * cos(radians(a)), ri * sin(radians(a))) for a in np.linspace(270, 90, na + 1)] + [(10.8, ri)]
    cb = ((1e9, "corr"),)
    for a, b in zip(inner[1:-1], inner[2:-1]):
        m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2); wall(a, b, ct, (CX + (m[0] - CX) * 2, m[1] * 2), bands=cb)
    for s in (1, -1):
        for (xa, xb) in ((CX, DX0), (DX1, 10.8)): wall((xa, s * ri), (xb, s * ri), ct, (9, s * 20), bands=cb)
        wall((DX0, s * ri), (DX1, s * ri), ct, (9, s * 20), bands=cb, zbase=DH, coll=False)
        outer = [(CX + RO * cos(radians(a)), s * RO * sin(radians(a))) for a in np.linspace(PHI1, 90, 10)] + [(10.8, s * RO)]
        for a, b in zip(outer, outer[1:]): wall(a, b, ct, (CX, 0), bands=fb)
        wall((10.8, s * ri), (10.8, s * RO), ct, (9, s * 8.8), bands=fb)
        inn = [(CX + ri * cos(radians(a)), s * ri * sin(radians(a))) for a in np.linspace(PHI1, 90, 10)] + [(10.8, s * ri)]
        strip(inn, outer, 0, 0, "rcarpet", up=True); strip(inn, outer, CH, CH, "fceil", up=False)
        for (x, y) in ((CX + 8.8 * cos(radians(125)), s * 8.8 * sin(radians(125))), (8.0, s * 8.8)):
            G.small = True; G.face([(x + 0.12 * cos(k * pi / 4), y + 0.12 * sin(k * pi / 4), CH - 0.012) for k in range(8)], "bulb", uv=[(0.5, 0.5)] * 8, up=False); G.small = False
            LAMPS.append((x, y, CH - 0.3, 45, (1.0, 0.82, 0.58)))
    ia = [(CX + ri * cos(radians(a)), ri * sin(radians(a))) for a in np.linspace(PHI1, 360 - PHI1, 13)]; pl = [(XFB, YJ - 2 * YJ * i / 12) for i in range(13)]
    strip(ia, pl, 0, 0, "rcarpet", up=True); strip(ia, pl, CH, CH, "fceil", up=False)
    for y in (-1.6, 1.6):
        G.small = True; G.face([(XFB + 0.55 + 0.12 * cos(k * pi / 4), y + 0.12 * sin(k * pi / 4), CH - 0.012) for k in range(8)], "bulb", uv=[(0.5, 0.5)] * 8, up=False); G.small = False
        LAMPS.append((XFB + 0.55, y, CH - 0.3, 45, (1.0, 0.82, 0.58)))

def cafe(LAMPS):
    """Yläkerran kahvila (malli siirretty x + XO): kolme kaari-ikkunaa Hallituskadulle, harmaanvioletit seinät, hammaslistareunus, komeat ovenpäällykset,
    kristallikruunu, vihertävä matto, marmoripöydät ja mustat taivutetut tuolit; takaseinässä oranssinpunainen syvennys ja kaksi kullattua pylvästä."""
    x0, x1 = XO + XF, XO + XFB; cb = ((0.9, "cdado"), (KH - 0.45, "mauve"), (1e9, "ccorn")); ct = lambda q: KH; cen = (XO - 6.3, 0)
    wall((x0, -KW), (x0, KW), ct, cen, [K.Win(KW + y, 1.8, 0.9, 3.9, 0.9, "glass_c") for y in (-2.85, 0, 2.85)], bands=cb)
    for s in (1, -1):
        wall((x0, s * KW), (x1, s * KW), ct, cen, bands=cb); wall((x1, s * 1.7), (x1, s * KW), ct, cen, bands=cb)
        for xd in (XO - 6.55, XO - 2.75):
            door(xd, s * KW, 0, -s, 1.3, 2.5, 0.0, "doorc", exit_sign=(s > 0 and xd < XO - 5))
            G.box(xd - 0.95, xd + 0.95, min(s * KW, s * (KW - 0.2)), max(s * KW, s * (KW - 0.2)), 2.68, 3.12, "white", skip="y+" if s > 0 else "y-")
            G.face([(xd - 0.95, s * (KW - 0.205), 2.68), (xd + 0.95, s * (KW - 0.205), 2.68), (xd + 0.95, s * (KW - 0.205), 3.42), (xd - 0.95, s * (KW - 0.205), 3.42)], "ped", uv=[(0, 0.0), (1, 0.0), (1, 1), (0, 1)], toward=(xd, 0, 3))
        G.cyl(x1 - 1.0, s * 2.6, 0, 0.9, 0.16, 8, "cdado"); G.cyl(x1 - 1.0, s * 2.6, 0.9, KH - 0.7, 0.10, 10, "gold"); G.cyl(x1 - 1.0, s * 2.6, KH - 0.7, KH - 0.45, 0.10, 10, "gold", r1=0.24); COL["circ"].append([x1 - 1.0, s * 2.6, 0.2])
        wall((x1, s * 1.7), (x1 + 1.5, s * 1.7), lambda q: 2.7, (x1 + 0.7, 0), bands=((1e9, "orange"),))
        G.face([(x1 + 0.06, s * 1.7, 0), (x1 + 0.06, s * 1.2, 0), (x1 + 0.06, s * 1.35, 2.7), (x1 + 0.06, s * 1.7, 2.7)], "curtain", uv=[(0, 0), (0.5, 0), (0.35, 1.35), (0, 1.35)], toward=(XO - 6, 0, 1))
    wall((x1, -1.7), (x1, 1.7), ct, cen, bands=((KH - 0.45 - 2.7, "mauve"), (1e9, "ccorn")), zbase=2.7, coll=False)
    wall((x1 + 1.5, -1.7), (x1 + 1.5, 1.7), lambda q: 2.7, (x1, 0), bands=((1e9, "orange"),))
    G.face([(x1, -1.7, 2.7), (x1 + 1.5, -1.7, 2.7), (x1 + 1.5, 1.7, 2.7), (x1, 1.7, 2.7)], "fceil", up=False)
    G.face([(x0, -KW, 0), (x1, -KW, 0), (x1, KW, 0), (x0, KW, 0)], "ccarpet", up=True); G.face([(x1, -1.7, 0), (x1 + 1.5, -1.7, 0), (x1 + 1.5, 1.7, 0), (x1, 1.7, 0)], "ccarpet", up=True)
    G.face([(x0, -KW, KH), (x1, -KW, KH), (x1, KW, KH), (x0, KW, KH)], "cceil", uv=[(0, 0), (1, 0), (1, 1), (0, 1)], up=False)
    G.box(x1 + 0.85, x1 + 1.45, -0.75, 0.75, 0, 1.25, "seatwood", skip="z-"); G.box(x1 + 0.6, x1 + 0.85, -0.72, 0.72, 0.68, 0.76, "seatwood"); COL["seg"].append([x1 + 0.9, -0.75, x1 + 0.9, 0.75, 0.35])   # piano
    # kristallikruunu: kullattu vanne, ylä- ja alakartio valaisevaa kristallia
    cx, zr = XO - 6.3, 4.05; G.small = True
    G.cyl(cx, 0, zr + 0.95, KH, 0.02, 5, "gold"); G.cyl(cx, 0, zr - 0.04, zr + 0.06, 0.46, 14, "gold")
    G.cyl(cx, 0, zr + 0.06, zr + 0.95, 0.44, 14, "bulb", r1=0.10); G.cyl(cx, 0, zr - 0.5, zr - 0.04, 0.26, 14, "bulb", r1=0.44); G.cyl(cx, 0, zr - 0.72, zr - 0.5, 0.0, 14, "bulb", r1=0.26)
    G.small = False; LAMPS.append((cx, 0, zr - 1.1, 420, (1.0, 0.85, 0.62))); LAMPS.append((x1 + 0.6, 0, 2.3, 50, (1.0, 0.8, 0.6)))
    # pöydät (valkoinen marmori, musta jalka) ja tuolit (musta taivutettu puu, pelkistetty)
    def chair(x, y, ang):
        G.small = True; c, s = cos(ang), sin(ang)
        G.cyl(x, y, 0.44, 0.47, 0.20, 8, "seatwood", cap=True)
        for (lx, ly) in ((0.15, 0.15), (0.15, -0.15), (-0.16, 0.16), (-0.16, -0.16)): G.cyl(x + c * lx - s * ly, y + s * lx + c * ly, 0, 0.44 if lx > 0 else 0.86, 0.016, 4, "seatwood")
        obox(x, y, ang, -0.18, -0.14, -0.17, 0.17, 0.84, 0.90, "seatwood"); obox(x, y, ang, -0.175, -0.150, -0.10, 0.10, 0.58, 0.62, "seatwood")
        for ly in (-0.09, 0.09): obox(x, y, ang, -0.172, -0.152, ly - 0.012, ly + 0.012, 0.47, 0.84, "seatwood", skip="z+z-")
        G.small = False; COL["circ"].append([x, y, 0.2])
    for i, tx in enumerate((XO - 9.4, XO - 7.5, XO - 5.6, XO - 3.7)):
        for j, ty in enumerate((-3.0, 0.0, 3.0)):
            G.cyl(tx, ty, 0.71, 0.745, 0.40, 16, "marble", cap=True); G.face([(tx + 0.40 * cos(k * pi / 8), ty + 0.40 * sin(k * pi / 8), 0.71) for k in range(16)], "seatwood", up=False)
            G.small = True; G.cyl(tx, ty, 0.03, 0.71, 0.03, 6, "seatwood"); G.cyl(tx, ty, 0.0, 0.03, 0.22, 10, "seatwood", cap=True); G.small = False
            COL["circ"].append([tx, ty, 0.42]); t = 0.35 * ((i * 3 + j) % 3 - 1)
            chair(tx + 0.1 * sin(t), ty + 0.72, -pi / 2 + t); chair(tx - 0.1 * sin(t), ty - 0.72, pi / 2 + t)

if __name__ == "__main__":
    import bpy
    textures()
    LAMPS, LEV, ROOMS, PORTS = build()
    print(len(G.F), "pintaa,", len(COL["seg"]), "janaa,", len(COL["circ"]), "ympyrää")
    objs = K.make_scene([])
    for (x, y, z, w, c) in LAMPS:
        l = bpy.data.lights.new("valo", "POINT"); l.energy = w; l.color = c; l.shadow_soft_size = 0.45 if w > 100 else 0.15
        o = bpy.data.objects.new("valo", l); o.location = (x, y, z); bpy.context.scene.collection.objects.link(o)
    V = dict(aula=((-10.2, 0.0, 1.7), (0, 0, 2.2), 16), kaytava=((-0.6, 4.6, 1.7), (4, 9.5, 1.6), 16), sali=((9.6, 6.6, 1.7), (13, -3, 3.6), 14), katto=((6.0, 0.0, 1.7), (10, 0, 12), 14),
             nayttamolta=((16.5, 0.5, 2.7), (2, 0, 3.6), 16), kahvila=((XO - 2.4, 0.6, 1.7), (XO - 11, 0, 2.6), 16), kahvila2=((XO - 10.3, -3.9, 1.7), (XO - 1.6, 2, 2.2), 16))
    if A.shots: K.shots(V={k: v for k, v in V.items() if not os.environ.get("SHOTS") or k in os.environ["SHOTS"].split(",")})
    LMAX = 2.0
    if not A.nobake: LMAX = K.finish_lm(K.bake(objs))
    K.export(objs)
    meta = dict(col=COL, lmax=LMAX, xw=XF, xe=XE, hw=R, py=0.0, xs0=1e6, flz=0.0, lev=LEV, spawn=[XF + 1.4, 0.0], exit=[XF + 0.6, 1.2], room=ROOMS[0], rooms=ROOMS, ports=PORTS, fold=XO)
    json.dump(meta, open("%s/%s.json" % (OUT, K.NAME), "w"))
