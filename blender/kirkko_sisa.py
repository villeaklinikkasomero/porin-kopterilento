# -*- coding: utf-8 -*-
"""
Keski-Porin kirkon sisätila (19.11.2026): kolmilaivainen halli, lehterit, urut, kuori ja alttari.

Ajo:  python3 blender/kirkko_sisa.py [--out DIR] [--lm 2048] [--samples 48] [--shots] [--nobake]
Tulos: DIR/kirkko_sisa.glb (geometria + toistuvat pintakuviot, UV0 = kuvio, UV1 = valokartta),
       DIR/kirkko_sisa_lm.jpg (Cyclesilla leivottu valo: ikkunat + kruunut), DIR/kirkko_sisa.json (törmäykset pelille)
       ja pelikansioon kirkko_sisa.js (tools/sisa_to_js.py).

Koordinaatit (Blender): X = itään kohti alttaria, Y = pohjoiseen (alttarille katsoen vasen), Z = ylös, origo lattialla
ulkomallin (kirkko.js) origossa. Mitat on sovitettu ulkomallin runkoon: tornin seinä x = -22, tukipilarit 5,54 m välein,
kuori x > 24,3. Sisäkuvista (seurakunnan ja Ylen kuvat) on luettu vain rakenne, värit ja materiaalit; alttaritaulua ja
lasimaalauksia EI ole kopioitu, niiden tilalla on omat abstraktit pinnat.
"""
import bpy, bmesh, math, os, sys, json
import numpy as np
from math import sin, cos, pi, sqrt, radians, ceil
from mathutils import Vector
from PIL import Image, ImageDraw, ImageFilter, ImageFont

def args():
    import argparse
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="/home/claude/out_sisa")
    p.add_argument("--lm", type=int, default=2048)
    p.add_argument("--samples", type=int, default=48)
    p.add_argument("--shots", action="store_true")
    p.add_argument("--nobake", action="store_true")
    return p.parse_args(argv)
A = args()
OUT = A.out
NAME = "kirkko_sisa"                     # tulostiedostojen nimi; muut sisätilat (mausoleumi_sisa.py) vaihtavat tämän
os.makedirs(OUT + "/tex", exist_ok=True)

# ---------------------------------------------------------------- mitat
XW, XE, HW, CY = -22.0, 24.32, 11.0, 4.6           # länsiseinä, itäseinä (kuorin kaari), sisäleveyden puolikas, pylväslinja
BAY = 5.54
XB = [-20.0 + BAY * i for i in range(9)]            # pylväsjaot (ulkomallin tukipilarit)
ZS, RN, RA, RX = 9.6, 6.0, 4.6, 5.0                 # holvin kanta; nousut: keskilaiva, sivulaiva, pituussuunta
GZ0, GZ1, GP = 4.45, 4.7, 5.85                      # lehterin alapinta, lattia, kaiteen yläreuna
APX, APR, ZSA, RAP = XE + 2.5, 4.9, 10.4, 4.8       # kuorin monikulmion keskipiste, säde, holvin kanta ja nousu
PY, XS0, FLZ = 4.9, XE - 3.4, 0.45                  # kuorikorokkeen puolileveys, portaiden alku, korkeus
AYC, AHS = (CY + HW) / 2, (HW - CY) / 2             # sivulaivan keskilinja ja puolijänne

def parch(d, s, r):
    """Suippokaaren korkeus kannasta etäisyydellä d keskeltä (puolijänne s, nousu r >= s)."""
    d = min(abs(d), s); c = (r * r - s * s) / (2 * s); R = s + c
    return sqrt(max(0.0, R * R - (d + c) ** 2))

# ---------------------------------------------------------------- pintakuviot (itse piirretyt, saumattomasti toistuvat)
def fnoise(n, seed, sx, sy=None):
    sy = sy or sx
    rng = np.random.default_rng(seed)
    f = np.fft.fft2(rng.standard_normal((n, n)))
    ky = np.fft.fftfreq(n)[:, None] * n; kx = np.fft.fftfreq(n)[None, :] * n
    g = np.real(np.fft.ifft2(f * np.exp(-(kx / sx) ** 2 - (ky / sy) ** 2)))
    return (g - g.mean()) / (g.std() + 1e-9)

def flat(n, col, seed=1, amp=0.03, sx=10, sy=None, fine=0.012):
    k = 1 + amp * fnoise(n, seed, sx, sy) + fine * fnoise(n, seed + 50, 90)
    return np.clip(np.array(col)[None, None, :] * k[..., None], 0, 1)

def to_img(a):
    return Image.fromarray((np.clip(a, 0, 1) ** (1 / 2.2) * 255).astype(np.uint8))   # lineaarinen -> sRGB
def lin(c):
    return tuple((v / 255) ** 2.2 for v in c)
def srgb(c):
    return tuple(int(255 * max(0, min(1, v)) ** (1 / 2.2)) for v in c)

TEX = {}
def save_tex(name, img):
    p = "%s/tex/%s.png" % (OUT, name); img.convert("RGB").save(p); TEX[name] = p

def make_textures():
    C = dict(wall=(0.80, 0.73, 0.58), vault=(0.83, 0.78, 0.63), rib=(0.60, 0.36, 0.33), pink=(0.72, 0.47, 0.40),
             cream=(0.80, 0.74, 0.58), ochre=(0.70, 0.50, 0.16), dado=(0.20, 0.27, 0.33), stone=(0.36, 0.35, 0.33),
             gold=(0.66, 0.47, 0.12), organ=(0.62, 0.38, 0.12), pipe=(0.52, 0.53, 0.52), red=(0.33, 0.035, 0.05),
             white=(0.82, 0.81, 0.77), dark=(0.10, 0.065, 0.04), black=(0.02, 0.02, 0.022))
    n = 256
    save_tex("wall", to_img(flat(n, C["wall"], 1, 0.035, 5)))
    save_tex("cream", to_img(flat(n, C["cream"], 2, 0.03, 6)))
    save_tex("reveal", to_img(flat(n, (0.80, 0.77, 0.66), 22, 0.04, 4)))
    save_tex("pink", to_img(flat(n, C["pink"], 3, 0.05, 3, 14)))
    save_tex("gold", to_img(flat(n, C["gold"], 4, 0.08, 12)))
    save_tex("pipe", to_img(flat(n, C["pipe"], 5, 0.05, 2, 60)))
    save_tex("white", to_img(flat(n, C["white"], 6, 0.02, 8)))
    save_tex("dark", to_img(flat(n, C["dark"], 7, 0.10, 3, 50)))
    save_tex("black", to_img(flat(64, C["black"], 8, 0.0)))
    save_tex("organ", to_img(flat(n, C["organ"], 9, 0.07, 3, 60)))
    save_tex("ochre", to_img(flat(n, C["ochre"], 10, 0.06, 60, 3)))
    # holvi: vaalea kalkkimaali, tähtikuvio limittäin 0,5 m välein (ruutu = 1 m)
    a = flat(n, C["vault"], 11, 0.03, 5); im = to_img(a); d = ImageDraw.Draw(im)
    star = srgb((0.42, 0.33, 0.27))
    for cx, cy in ((64, 64), (192, 192), (64, 192), (192, 64), (0, 0), (128, 128), (128, 0), (0, 128)):
        big = (cx + cy) % 128 == 0
        for ox in (-n, 0, n):
            for oy in (-n, 0, n):
                x, y = cx + ox, cy + oy; r = 7 if big else 3
                if big: d.polygon([(x, y - r), (x + 2, y - 2), (x + r, y), (x + 2, y + 2), (x, y + r), (x - 2, y + 2), (x - r, y), (x - 2, y - 2)], fill=star)
                else: d.ellipse([x - r, y - r, x + r, y + r], fill=star)
    save_tex("vault", im)
    # ruoteet ja kaaret: punaruskea, vaaleat reunaviivat (u poikki)
    a = flat(n, C["rib"], 12, 0.04, 6); im = to_img(a); d = ImageDraw.Draw(im)
    for x in (22, 234): d.line([(x, 0), (x, n)], fill=srgb((0.78, 0.70, 0.55)), width=5)
    for y in range(0, n, 64): d.ellipse([118, y + 22, 138, y + 42], fill=srgb((0.78, 0.70, 0.55)))
    save_tex("rib", im)
    # pylvään koristekenttä: harmaanvihreä pohja, vaalea köynnös (u = kentän leveys, v = 1 m)
    a = flat(n, (0.27, 0.34, 0.30), 13, 0.05, 6); im = to_img(a); d = ImageDraw.Draw(im)
    lc, bc = srgb((0.74, 0.70, 0.52)), srgb((0.55, 0.30, 0.26))
    d.rectangle([0, 0, 26, n], fill=bc); d.rectangle([n - 27, 0, n, n], fill=bc)
    d.line([(34, 0), (34, n)], fill=lc, width=3); d.line([(n - 35, 0), (n - 35, n)], fill=lc, width=3)
    for k in range(2):
        y0 = k * 128
        d.polygon([(128, y0 + 8), (158, y0 + 64), (128, y0 + 120), (98, y0 + 64)], outline=lc); d.ellipse([116, y0 + 52, 140, y0 + 76], fill=lc)
        for s in (-1, 1):
            d.arc([128 + s * 20 - 34, y0 + 4, 128 + s * 20 + 34, y0 + 60], 200 if s < 0 else 280, 260 if s < 0 else 340, fill=lc, width=3)
            d.ellipse([128 + s * 52 - 7, y0 + 96 - 7, 128 + s * 52 + 7, y0 + 96 + 7], fill=lc)
    save_tex("colpanel", im)
    # alaseinän paneeli: siniharmaa, yläreunassa okralista (v = 0..1 = 1,3 m)
    a = flat(n, C["dado"], 14, 0.05, 8); im = to_img(a); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, n, 12], fill=srgb((0.50, 0.36, 0.14))); d.rectangle([0, 12, n, 18], fill=srgb((0.10, 0.12, 0.15)))
    d.rectangle([0, n - 26, n, n], fill=srgb((0.12, 0.15, 0.19)))
    for x in (0, 128): d.rectangle([x + 10, 34, x + 118, n - 40], outline=srgb((0.14, 0.19, 0.24)), width=3)
    save_tex("dado", im)
    # friisi: okranauha ja ruusukkeet (v = 0..1)
    a = flat(n, (0.62, 0.47, 0.20), 15, 0.05, 6); im = to_img(a); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, n, 14], fill=srgb(C["rib"])); d.rectangle([0, n - 15, n, n], fill=srgb(C["rib"]))
    for cx in (64, 192):
        d.ellipse([cx - 44, 84, cx + 44, 172], outline=srgb((0.30, 0.22, 0.12)), width=5)
        for k in range(8):
            an = k * pi / 4; d.ellipse([cx + 26 * cos(an) - 11, 128 + 26 * sin(an) - 11, cx + 26 * cos(an) + 11, 128 + 26 * sin(an) + 11], fill=srgb((0.45, 0.20, 0.16)))
        d.ellipse([cx - 10, 118, cx + 10, 138], fill=srgb((0.80, 0.72, 0.50)))
    save_tex("frieze", im)
    # lehterin kaide: sokea suippokaaristo (u = yksi kaari 0,58 m, v = kaiteen korkeus)
    a = flat(n, (0.76, 0.66, 0.40), 16, 0.03, 8); im = to_img(a); d = ImageDraw.Draw(im)
    sh, hi = srgb((0.50, 0.40, 0.20)), srgb((0.86, 0.78, 0.55))
    d.rectangle([0, 0, n, 22], fill=hi); d.rectangle([0, 22, n, 30], fill=sh); d.rectangle([0, n - 30, n, n], fill=hi); d.rectangle([0, n - 36, n, n - 30], fill=sh)
    arch = [(36, 214), (36, 120)] + [(36 + 92 * (1 - cos(t / 12 * pi / 2.6)), 120 - 70 * sin(t / 12 * pi / 2.6) / sin(pi / 2.6)) for t in range(13)]
    arch = arch[:-1] + [(128, 46)] + [(256 - x, y) for x, y in reversed(arch[:-1])]
    d.polygon(arch, fill=srgb((0.66, 0.55, 0.30))); d.line(arch + [arch[0]], fill=sh, width=5)
    d.rectangle([0, 34, 8, 220], fill=sh); d.rectangle([n - 8, 34, n, 220], fill=sh)
    save_tex("galfront", im)
    # lattia: harmaa kalkkikivi, laatat 1,0 x 0,5 m limittäin (ruutu 2 m)
    a = flat(512, C["stone"], 17, 0.06, 6);
    rng = np.random.default_rng(3)
    for j in range(4):
        for i in range(2):
            x0 = (i * 256 + (128 if j % 2 else 0)) % 512; y0 = j * 128; k = 1 + rng.uniform(-0.09, 0.09)
            for xx in ((x0, min(512, x0 + 256)), (0, max(0, x0 + 256 - 512))):
                a[y0:y0 + 128, xx[0]:xx[1]] *= k
    im = to_img(a); d = ImageDraw.Draw(im)
    for j in range(4):
        d.line([(0, j * 128), (512, j * 128)], fill=srgb((0.16, 0.155, 0.15)), width=3)
        for i in range(3):
            x = i * 256 + (128 if j % 2 else 0); d.line([(x, j * 128), (x, j * 128 + 128)], fill=srgb((0.16, 0.155, 0.15)), width=3)
    save_tex("floor", im.resize((384, 384), Image.LANCZOS))
    # käytävämatto: tummanpunainen, reunaraita (u poikki)
    a = flat(n, C["red"], 18, 0.06, 40); im = to_img(a); d = ImageDraw.Draw(im)
    for x in (14, 234): d.rectangle([x, 0, x + 8, n], fill=srgb((0.16, 0.02, 0.03)))
    save_tex("carpet", im)
    # ovet: tumma lankkuovi, raudat
    a = flat(n, (0.16, 0.09, 0.045), 19, 0.10, 3, 60); im = to_img(a); d = ImageDraw.Draw(im)
    for x in range(0, n, 32): d.line([(x, 0), (x, n)], fill=srgb((0.06, 0.035, 0.02)), width=3)
    d.line([(128, 0), (128, n)], fill=srgb((0.02, 0.015, 0.01)), width=6)
    for y in (60, 196): d.rectangle([8, y, n - 8, y + 9], fill=srgb((0.03, 0.03, 0.03)))
    d.ellipse([108, 122, 120, 134], fill=srgb(C["gold"])); d.ellipse([136, 122, 148, 134], fill=srgb(C["gold"]))
    save_tex("door", im)
    # virsitaulu: musta taulu, kultakehys, numerot
    im = Image.new("RGB", (192, 256), srgb((0.015, 0.015, 0.018))); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 191, 255], outline=srgb(C["gold"]), width=12)
    try: f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 54)
    except Exception: f = ImageFont.load_default()
    for k, t in enumerate(("301", "462", "105")): d.text((96, 52 + k * 68), t, font=f, fill=srgb((0.85, 0.72, 0.35)), anchor="mm")
    save_tex("hymn", im)
    # alttaritaulu: R. W. Ekmanin luonnos Keski-Porin kirkon alttaritauluun (Kansallisgalleria, CC0; blender/tex_art/ekman_luonnos.jpg, omistajan lupa 19.11.2026).
    # Jos tiedosto puuttuu: abstrakti valo tummalla pohjalla.
    artf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tex_art", "ekman_luonnos.jpg")
    if os.path.exists(artf):
        im = Image.open(artf).convert("RGB"); w, h = im.size; cw = int(h * 0.694); im = im.crop(((w - cw) // 2, 0, (w - cw) // 2 + cw, h)).resize((356, 512), Image.LANCZOS)
    else:
        yy, xx = np.mgrid[0:512, 0:256] / np.array([512, 256])[:, None, None]
        glow = np.exp(-(((xx - 0.5) / 0.22) ** 2 + ((yy - 0.36) / 0.20) ** 2)); low = np.exp(-(((xx - 0.5) / 0.45) ** 2 + ((yy - 0.95) / 0.22) ** 2))
        a = np.stack([0.06 + 0.75 * glow + 0.10 * low, 0.045 + 0.55 * glow + 0.06 * low, 0.04 + 0.28 * glow + 0.05 * low], -1) * (1 + 0.08 * fnoise(512, 21, 6)[:, :256, None])
        im = to_img(a)
    d = ImageDraw.Draw(im); d.rectangle([0, 0, im.width - 1, im.height - 1], outline=srgb(C["gold"]), width=14); d.rectangle([14, 14, im.width - 15, im.height - 15], outline=srgb((0.25, 0.16, 0.05)), width=3)
    save_tex("altar", im)
    # ---- ikkunat (valaisevat pinnat)
    lead = (30, 32, 36)
    def quarries(w, h, tint, step=32):
        a = np.ones((h, w, 3)) * np.array(tint)[None, None, :] * (1 + 0.10 * fnoise(max(w, h), 31, 14)[:h, :w, None])
        im = to_img(a); d = ImageDraw.Draw(im)
        for k in range(-h, w + h, step):
            d.line([(k, 0), (k + h, h)], fill=lead, width=2); d.line([(k, 0), (k - h, h)], fill=lead, width=2)
        return im, d
    # alaikkuna: kirkas vinoruutulasi, puitejako
    im, d = quarries(192, 256, (0.80, 0.84, 0.80), 28)
    d.rectangle([0, 0, 191, 255], outline=(190, 180, 150), width=9); d.line([(96, 0), (96, 256)], fill=(190, 180, 150), width=7); d.line([(0, 96), (192, 96)], fill=(190, 180, 150), width=7)
    save_tex("glass_low", im)
    # yläikkuna: vaalea ruutulasi, kaksi lansettia, kärjessä värilasit (oma geometrinen sommitelma)
    W, H = 192, 640
    im, d = quarries(W, H, (0.78, 0.82, 0.80), 30)
    fr = (196, 186, 156)
    top = int(H * 0.26)
    d.rectangle([0, 0, W, top], fill=(60, 70, 110))
    for k in range(-2, 9):                                   # kärjen värilasit: sininen pohja, punaiset ja keltaiset vinoneliöt
        for j in range(-1, 6):
            cx, cy = k * 30 + (15 if j % 2 else 0), j * 30
            d.polygon([(cx, cy - 15), (cx + 15, cy), (cx, cy + 15), (cx - 15, cy)], fill=[(36, 62, 170), (30, 50, 140), (170, 34, 40), (36, 62, 170), (215, 160, 50)][(k * 3 + j * 2) % 5], outline=lead)
    d.ellipse([W / 2 - 40, top - 96, W / 2 + 40, top - 16], fill=(235, 190, 60), outline=lead, width=4)
    d.ellipse([W / 2 - 18, top - 74, W / 2 + 18, top - 38], fill=(200, 30, 40), outline=lead, width=3)
    d.line([(W / 2, top), (W / 2, H)], fill=fr, width=9); d.line([(0, top), (W, top)], fill=fr, width=8)
    for y in range(top + 122, H, 122): d.line([(0, y), (W, y)], fill=fr, width=5)
    d.rectangle([0, 0, W - 1, H - 1], outline=fr, width=9)
    save_tex("glass_up", im)
    # kuorin ikkunat: Enckellin (1925) lasimaalauksia MUISTUTTAVA oma piirros - sininen viittahahmo sädekehineen, punaiset ja kullanväriset
    # reunat, kärjessä ruusuke. Vapaata kuvaa alkuperäisistä ei löytynyt (Commons, Finna 19.11.2026), joten tämä ei ole jäljennös.
    W, H, S2 = 160, 640, 2; im = Image.new("RGB", (W * S2, H * S2), (20, 30, 90)); d = ImageDraw.Draw(im); rng = np.random.default_rng(9)
    Q = lambda pts: [(x * S2, y * S2) for x, y in pts]
    blues = [(24, 44, 150), (18, 32, 112), (34, 70, 178), (46, 96, 190), (22, 60, 130)]
    for j in range(-1, H // 16 + 2):
        for i in range(-1, W // 16 + 2):
            cx, cy = i * 16 + (8 if j % 2 else 0), j * 16
            d.polygon(Q([(cx, cy - 16), (cx + 8, cy), (cx, cy + 16), (cx - 8, cy)]), fill=blues[int(rng.integers(0, 5))], outline=lead)
    d.ellipse([34 * S2, 22 * S2, 126 * S2, 114 * S2], fill=(170, 26, 36), outline=lead, width=3 * S2)                      # kärjen ruusuke
    for k in range(8):
        an = k * pi / 4; d.polygon(Q([(80, 68), (80 + 40 * cos(an - 0.25), 68 + 40 * sin(an - 0.25)), (80 + 46 * cos(an), 68 + 46 * sin(an)), (80 + 40 * cos(an + 0.25), 68 + 40 * sin(an + 0.25))]), fill=(236, 230, 214) if k % 2 else (228, 176, 60), outline=lead)
    d.ellipse([66 * S2, 54 * S2, 94 * S2, 82 * S2], fill=(228, 176, 60), outline=lead, width=2 * S2)
    d.polygon(Q([(30, 190), (80, 140), (130, 190), (130, 200), (30, 200)]), fill=(196, 150, 50), outline=lead)                 # katos hahmon yllä
    d.ellipse([50 * S2, 196 * S2, 110 * S2, 256 * S2], fill=(236, 196, 80), outline=lead, width=3 * S2)                     # sädekehä
    d.ellipse([66 * S2, 208 * S2, 94 * S2, 246 * S2], fill=(226, 196, 170), outline=lead, width=2 * S2)                     # kasvot
    d.polygon(Q([(62, 216), (80, 202), (98, 216), (96, 232), (64, 232)]), fill=(120, 84, 50), outline=lead)                    # hiukset / huntu
    d.ellipse([70 * S2, 216 * S2, 90 * S2, 244 * S2], fill=(226, 196, 170))
    d.polygon(Q([(50, 262), (80, 244), (110, 262), (128, 520), (32, 520)]), fill=(26, 52, 168), outline=lead)                  # sininen viitta
    d.polygon(Q([(66, 262), (80, 250), (94, 262), (100, 520), (60, 520)]), fill=(168, 30, 40), outline=lead)                   # punainen alusvaate
    for x0, x1 in ((44, 62), (98, 116)): d.line(Q([(x0 + 6, 290), (x0, 500)]), fill=(60, 100, 200), width=4 * S2); d.line(Q([(x1 - 6, 290), (x1, 500)]), fill=(16, 30, 110), width=4 * S2)
    d.polygon(Q([(58, 330), (80, 316), (102, 330), (92, 352), (68, 352)]), fill=(226, 196, 170), outline=lead)                 # kädet rinnalla
    d.rectangle([24 * S2, 520 * S2, 136 * S2, 536 * S2], fill=(196, 150, 50), outline=lead)
    for i in range(4):                                                                                                         # alakentän vinoneliöt
        cx = 38 + i * 28; d.polygon(Q([(cx, 544), (cx + 14, 578), (cx, 612), (cx - 14, 578)]), fill=(170, 26, 36) if i % 2 else (228, 176, 60), outline=lead)
    for y in range(128, H, 96): d.line(Q([(0, y), (W, y)]), fill=lead, width=2 * S2)                                           # lyijypuitteet
    d.line(Q([(80, 520), (80, H)]), fill=lead, width=2 * S2)
    d.rectangle([0, 0, W * S2 - 1, H * S2 - 1], outline=(170, 26, 36), width=10 * S2); d.rectangle([10 * S2, 10 * S2, (W - 10) * S2, (H - 10) * S2], outline=(228, 176, 60), width=3 * S2)
    save_tex("glass_apse", im.resize((W, H), Image.LANCZOS))
    im = Image.new("RGB", (16, 16), (255, 214, 150)); save_tex("bulb", im)

# materiaali: (ruudun koko m, valovoima; 0 = tavallinen pinta)
MATDEF = dict(wall=(3.0, 0), cream=(2.0, 0), pink=(1.5, 0), gold=(1.0, 0), pipe=(1.0, 0), white=(2.0, 0), dark=(1.5, 0), black=(1, 0),
              organ=(1.5, 0), ochre=(1.2, 0), vault=(1.0, 0), rib=(1.0, 0), colpanel=(1.0, 0), dado=(1.3, 0), frieze=(1.2, 0),
              galfront=(1.0, 0), floor=(2.0, 0), carpet=(1.0, 0), door=(1.0, 0), hymn=(1.0, 0), altar=(1.0, 0),
              glass_low=(1, 5.0), glass_up=(1, 5.0), glass_apse=(1, 7.0), bulb=(1, 3.0),
              reveal=(2.0, 0.5))                      # ikkunasyvennykset: päivänvalossa kylpevä pinta, ei valokarttaa
MI = {k: i for i, k in enumerate(MATDEF)}

# ---------------------------------------------------------------- geometrian kokoaja
class Geo:
    def __init__(s): s.V = []; s.F = []; s.UV = []; s.M = []; s.S = []; s.small = False   # small: pikkuosat, joille ei leivota omaa valokarttaa
    def face(s, pts, mat, uv=None, toward=None, away=None, up=None):
        pts = [Vector(p) for p in pts]
        n = Vector((0, 0, 0)); c = sum(pts, Vector()) / len(pts)
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            n += Vector(((a.y - b.y) * (a.z + b.z), (a.z - b.z) * (a.x + b.x), (a.x - b.x) * (a.y + b.y)))
        if n.length < 1e-9: return
        n.normalize()
        want = None
        if up is not None: want = Vector((0, 0, 1 if up else -1))
        elif toward is not None: want = Vector(toward) - c
        elif away is not None: want = c - Vector(away)
        flip = want is not None and n.dot(want) < 0
        if uv is None:
            sc = MATDEF[mat][0]; nn = -n if flip else n
            if abs(nn.z) > 0.7: uv = [(p.x / sc, p.y / sc) for p in pts]
            else:
                t = Vector((-nn.y, nn.x, 0)); t = t.normalized() if t.length > 1e-6 else Vector((1, 0, 0))
                uv = [(p.dot(t) / sc, p.z / sc) for p in pts]
        if flip: pts = pts[::-1]; uv = list(uv)[::-1]
        b = len(s.V); s.V += [tuple(p) for p in pts]; s.F.append(tuple(range(b, b + len(pts)))); s.UV.append(list(uv)); s.M.append(MI[mat]); s.S.append(s.small)
    def box(s, x0, x1, y0, y1, z0, z1, mat, skip="", mats=None):
        c = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2); m = lambda k: (mats or {}).get(k, mat)
        if "x-" not in skip: s.face([(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)], m("x-"), away=c)
        if "x+" not in skip: s.face([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], m("x+"), away=c)
        if "y-" not in skip: s.face([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], m("y-"), away=c)
        if "y+" not in skip: s.face([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], m("y+"), away=c)
        if "z-" not in skip: s.face([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)], m("z-"), away=c)
        if "z+" not in skip: s.face([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], m("z+"), away=c)
    def cyl(s, cx, cy, z0, z1, r, n, mat, a0=0.0, a1=2 * pi, r1=None, cap=False, vscale=None):
        r1 = r if r1 is None else r1; sc = vscale or MATDEF[mat][0]
        for i in range(n):
            t0, t1 = a0 + (a1 - a0) * i / n, a0 + (a1 - a0) * (i + 1) / n
            p = [(cx + r * cos(t0), cy + r * sin(t0), z0), (cx + r * cos(t1), cy + r * sin(t1), z0), (cx + r1 * cos(t1), cy + r1 * sin(t1), z1), (cx + r1 * cos(t0), cy + r1 * sin(t0), z1)]
            uv = [(t0 * r / sc, z0 / sc), (t1 * r / sc, z0 / sc), (t1 * r / sc, z1 / sc), (t0 * r / sc, z1 / sc)]
            s.face(p, mat, uv=uv, away=(cx, cy, (z0 + z1) / 2))
        if cap: s.face([(cx + r1 * cos(a0 + (a1 - a0) * i / n), cy + r1 * sin(a0 + (a1 - a0) * i / n), z1) for i in range(n)], mat, up=True)
    def sweep(s, path, w, d, mat, ref):
        """Ruode: polku holvin pinnalla, leveys w, syvyys d pinnasta kohti viitepistettä ref (tilan sisään)."""
        P = [Vector(p) for p in path]; L = [0.0]
        for a, b in zip(P, P[1:]): L.append(L[-1] + (b - a).length)
        sec = []
        for i, p in enumerate(P):
            t = (P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]).normalized()
            side = t.cross(Vector((0, 0, 1)))
            if side.length < 1e-4: side = t.cross(Vector(ref) - p)
            side.normalize(); nrm = side.cross(t).normalized()
            if nrm.dot(Vector(ref) - p) < 0: nrm = -nrm
            sec.append((p + side * w / 2, p - side * w / 2, p + side * w / 2 + nrm * d, p - side * w / 2 + nrm * d))
        sc = MATDEF[mat][0]
        for i in range(len(P) - 1):
            a, b = sec[i], sec[i + 1]; v0, v1 = L[i] / sc, L[i + 1] / sc; c = (a[0] + a[1] + b[0] + b[1]) / 4
            s.face([a[2], a[3], b[3], b[2]], mat, uv=[(0, v0), (1, v0), (1, v1), (0, v1)], away=c)
            s.face([a[0], a[2], b[2], b[0]], mat, uv=[(0, v0), (0.2, v0), (0.2, v1), (0, v1)], away=(a[1] + b[1]) / 2)
            s.face([a[1], a[3], b[3], b[1]], mat, uv=[(1, v0), (0.8, v0), (0.8, v1), (1, v1)], away=(a[0] + b[0]) / 2)
G = Geo()
COL = dict(seg=[], circ=[])          # törmäykset pelille: janat [x0,y0,x1,y1,r] ja ympyrät [x,y,r]

class Win:
    def __init__(s, sc, w, z0, z1, rise, mat): s.sc, s.w, s.z0, s.z1, s.rise, s.mat = sc, w, z0, z1, rise, mat
    def head(s, x): return s.z1 + (parch(x - s.sc, s.w / 2, s.rise) if s.rise else 0.0)

def wall(p0, p1, top, inward, wins=(), bands=((1.3, "dado"), (1e9, "wall")), depth=0.45, coll=True, zbase=0.0):
    d = Vector((p1[0] - p0[0], p1[1] - p0[1])); L = d.length; t = d / L
    nin = Vector((-t.y, t.x)); mid = (Vector(p0) + Vector(p1)) / 2
    if nin.dot(Vector(inward[:2]) - mid) < 0: nin = -nin
    P = lambda s, z, off=0.0: (p0[0] + t.x * s - nin.x * off, p0[1] + t.y * s - nin.y * off, z)
    ref = lambda s, z: (p0[0] + t.x * s + nin.x * 5, p0[1] + t.y * s + nin.y * 5, z)
    cuts = {0.0, L}
    for w in wins: cuts |= {w.sc - w.w / 2, w.sc + w.w / 2}
    ss = sorted(cuts); fine = []
    for a, b in zip(ss, ss[1:]):
        n = max(1, ceil((b - a) / 0.42)); fine += [a + (b - a) * i / n for i in range(n)]
    fine.append(L)
    def emit(a, b, lo, hi):
        cur = lo
        for zb, mat in bands:
            zb = zb + zbase if zb < 1e8 else zb
            if zb <= max(cur) + 1e-6: continue
            last = zb >= min(hi) - 1e-6
            h = hi if last else (zb, zb)
            if max(h[0] - cur[0], h[1] - cur[1]) > 1e-4:
                sc = MATDEF[mat][0]
                uv = [(a / sc, (cur[0] - zbase) / sc), (b / sc, (cur[1] - zbase) / sc), (b / sc, (h[1] - zbase) / sc), (a / sc, (h[0] - zbase) / sc)]
                G.face([P(a, cur[0]), P(b, cur[1]), P(b, h[1]), P(a, h[0])], mat, uv=uv, toward=ref((a + b) / 2, (cur[0] + h[0]) / 2))
            if last: break
            cur = (zb, zb)
    for a, b in zip(fine, fine[1:]):
        m = (a + b) / 2; lo = (zbase, zbase)
        for w in sorted([w for w in wins if abs(m - w.sc) < w.w / 2], key=lambda w: w.z0):
            emit(a, b, lo, (w.z0, w.z0)); lo = (w.head(a), w.head(b))
        emit(a, b, lo, (top(a), top(b)))
    for w in wins:
        a0, a1 = w.sc - w.w / 2, w.sc + w.w / 2; n = 10 if w.rise else 1; ztop = w.z1 + w.rise; cm = (w.sc, (w.z0 + w.z1) / 2)
        cen = P(w.sc, (w.z0 + w.z1) / 2, depth / 2)
        G.face([P(a0, w.z0), P(a1, w.z0), P(a1, w.z0, depth), P(a0, w.z0, depth)], "reveal", toward=cen)
        for sx in (a0, a1): G.face([P(sx, w.z0), P(sx, w.z1), P(sx, w.z1, depth), P(sx, w.z0, depth)], "reveal", toward=cen)
        for i in range(n):
            a, b = a0 + (a1 - a0) * i / n, a0 + (a1 - a0) * (i + 1) / n
            G.face([P(a, w.head(a)), P(b, w.head(b)), P(b, w.head(b), depth), P(a, w.head(a), depth)], "reveal", toward=cen)
            uv = [((a - a0) / w.w, 0), ((b - a0) / w.w, 0), ((b - a0) / w.w, (w.head(b) - w.z0) / (ztop - w.z0)), ((a - a0) / w.w, (w.head(a) - w.z0) / (ztop - w.z0))]
            G.face([P(a, w.z0, depth), P(b, w.z0, depth), P(b, w.head(b), depth), P(a, w.head(a), depth)], w.mat, uv=uv, toward=ref(m, w.z0))
    if coll: COL["seg"].append([p0[0], p0[1], p1[0], p1[1], 0.05])

def vault(x0, x1, y0, y1, rx, ry, zs, nx=10, ny=10, barrel=False):
    xc, yc, a, b = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
    h = lambda x, y: zs + max(0.0 if barrel else parch(x - xc, a, rx), parch(y - yc, b, ry))
    for i in range(nx):
        for j in range(ny):
            xa, xb_, ya, yb = x0 + (x1 - x0) * i / nx, x0 + (x1 - x0) * (i + 1) / nx, y0 + (y1 - y0) * j / ny, y0 + (y1 - y0) * (j + 1) / ny
            q = [(xa, ya, h(xa, ya)), (xb_, ya, h(xb_, ya)), (xb_, yb, h(xb_, yb)), (xa, yb, h(xa, yb))]
            # jaetaan kolmioiksi harjan suuntaan, jotta lävistäjäsaumat pysyvät terävinä
            if (i < nx / 2) == (j < ny / 2): tris = [(q[0], q[1], q[2]), (q[0], q[2], q[3])]
            else: tris = [(q[0], q[1], q[3]), (q[1], q[2], q[3])]
            for tr in tris: G.face(tr, "vault", up=False)
    return h

def column(x, y, z1=ZS, plinth=True):
    R = 0.40
    for k in range(8):                                   # kahdeksankulmainen ydin: lävistäjäsivuilla koristekenttä
        a0, a1 = (k - 0.5) * pi / 4, (k + 0.5) * pi / 4
        p0, p1 = (x + R * cos(a0), y + R * sin(a0)), (x + R * cos(a1), y + R * sin(a1))
        if k % 2:
            G.face([(*p0, 1.1), (*p1, 1.1), (*p1, z1 - 0.5), (*p0, z1 - 0.5)], "colpanel", uv=[(0, 1.1), (1, 1.1), (1, z1 - 0.5), (0, z1 - 0.5)], away=(x, y, 5))
    for k in range(4):                                   # neljä pyöreää puolipylvästä pääilmansuunnissa
        a = k * pi / 2; G.cyl(x + 0.36 * cos(a), y + 0.36 * sin(a), 1.1, z1 - 0.5, 0.19, 10, "pink", a - 2.0, a + 2.0)
    if plinth:
        G.cyl(x, y, 0.0, 0.85, 0.62, 8, "cream", pi / 8, 2 * pi + pi / 8); G.cyl(x, y, 0.85, 1.1, 0.62, 8, "cream", pi / 8, 2 * pi + pi / 8, r1=0.5)
    for za, zb, ra, rb in ((z1 - 0.5, z1 - 0.32, 0.50, 0.60), (z1 - 0.32, z1 - 0.08, 0.60, 0.60), (z1 - 0.08, z1 + 0.12, 0.60, 0.72), (z1 + 0.12, z1 + 0.2, 0.72, 0.72)):
        G.cyl(x, y, za, zb, ra, 12, "cream", r1=rb)
    G.cyl(x, y, z1 - 0.62, z1 - 0.5, 0.52, 12, "gold")
    for za in (GZ0 - 0.2,):                              # vyö lehterin kohdalla
        G.cyl(x, y, za, za + 0.12, 0.50, 12, "cream", r1=0.56); G.cyl(x, y, za + 0.12, za + 0.34, 0.56, 12, "cream"); G.cyl(x, y, za + 0.34, za + 0.46, 0.56, 12, "cream", r1=0.50)
    COL["circ"].append([x, y, 0.66])

def respond(x, y, ang, z1=ZS, r=0.2):
    G.cyl(x, y, 0.0, 1.1, r + 0.1, 8, "cream", ang - pi / 2, ang + pi / 2)
    G.cyl(x, y, 1.1, z1 - 0.3, r, 8, "pink", ang - pi / 2, ang + pi / 2)
    G.cyl(x, y, z1 - 0.3, z1 + 0.1, r + 0.02, 8, "cream", ang - pi / 2, ang + pi / 2, r1=r + 0.16)
    COL["circ"].append([x, y, r + 0.12])

# ---------------------------------------------------------------- rakennus
def build():
    # --- lattia, kuorikoroke, matto
    G.face([(XW, -HW, 0), (XS0, -HW, 0), (XS0, HW, 0), (XW, HW, 0)], "floor", up=True)
    for s in (1, -1): G.face([(XS0, s * PY, 0), (XE, s * PY, 0), (XE, s * HW, 0), (XS0, s * HW, 0)], "floor", up=True)
    for k in range(3):
        xa = XS0 + 0.4 * k; z = 0.15 * (k + 1); xb_ = xa + 0.4 if k < 2 else XE
        G.face([(xa, -PY, z - 0.15), (xa, PY, z - 0.15), (xa, PY, z), (xa, -PY, z)], "cream", toward=(XS0 - 5, 0, 1))
        G.face([(xa, -PY, z), (xb_, -PY, z), (xb_, PY, z), (xa, PY, z)], "floor", up=True)
        for s in (1, -1): G.face([(xa, s * PY, 0), (XE, s * PY, 0), (XE, s * PY, z), (xa, s * PY, z)], "cream", toward=(xa, s * 9, 0.2))
    ap = [(APX + APR * cos(radians(a)), APR * sin(radians(a))) for a in (90, 54, 18, -18, -54, -90)]
    G.face([(XE, PY, FLZ), (XE, -PY, FLZ)] + [(x, y, FLZ) for x, y in reversed(ap)], "floor", up=True)
    for s in (1, -1): COL["seg"].append([XS0 + 0.8, s * PY, XE, s * PY, 0.08])
    G.face([(XW + 0.4, -0.85, 0.012), (XS0 - 0.05, -0.85, 0.012), (XS0 - 0.05, 0.85, 0.012), (XW + 0.4, 0.85, 0.012)], "carpet",
           uv=[(0, 0), (0, 40), (1, 40), (1, 0)], up=True)
    for k in range(3):
        xa = XS0 + 0.4 * k; z = 0.15 * (k + 1) + 0.012; xb_ = xa + 0.4 if k < 2 else APX + 1.2
        G.face([(xa - 0.012, -0.85, z - 0.15), (xa - 0.012, 0.85, z - 0.15), (xa - 0.012, 0.85, z), (xa - 0.012, -0.85, z)], "carpet", uv=[(0, 0), (1, 0), (1, .15), (0, .15)], toward=(XS0 - 5, 0, 1))
        G.face([(xa, -0.85, z), (xb_, -0.85, z), (xb_, 0.85, z), (xa, 0.85, z)], "carpet", uv=[(0, 0), (0, xb_ - xa), (1, xb_ - xa), (1, 0)], up=True)

    # --- sivuseinät ikkunoineen
    def side_top(s_to_x):
        def f(s):
            x = s_to_x(s)
            if x <= XB[0]: return ZS + 0.02
            i = min(7, int((x - XB[0]) / BAY)); return ZS + parch(x - (XB[i] + BAY / 2), BAY / 2, RX) + 0.02
        return f
    for sgn in (1, -1):
        wins = []
        for i in range(8):
            sc = XB[i] + BAY / 2 - XW
            wins += [Win(sc, 1.5, 2.0, 3.9, 0, "glass_low"), Win(sc, 2.0, 6.3, 11.2, 1.5, "glass_up")]
        wall((XW, sgn * HW), (XE, sgn * HW), side_top(lambda s: XW + s), (0, 0), wins)
        for i in range(9): respond(XB[i], sgn * HW, -sgn * pi / 2)
    # --- länsiseinä (tornin puoli), ovet
    def west_top(s):
        y = -HW + s
        if abs(y) <= CY: return ZS + parch(y, CY, RN) + 0.02
        return ZS + parch(abs(y) - AYC, AHS, RA) + 0.02
    wall((XW, -HW), (XW, HW), west_top, (0, 0))
    def door(x, y, w, h, nx, face_x=True):
        e = 0.04 * nx
        G.face([(x + e, y - w / 2, 0), (x + e, y + w / 2, 0), (x + e, y + w / 2, h), (x + e, y - w / 2, h)], "door", uv=[(0, 0), (1, 0), (1, 1), (0, 1)], toward=(x + nx * 5, y, 1))
        for yy in (y - w / 2 - 0.12, y + w / 2): G.box(x, x + 0.1 * nx, yy, yy + 0.12, 0, h + 0.12, "cream") if nx > 0 else G.box(x + 0.1 * nx, x, yy, yy + 0.12, 0, h + 0.12, "cream")
        if nx > 0: G.box(x, x + 0.1, y - w / 2 - 0.12, y + w / 2 + 0.12, h, h + 0.14, "cream")
        else: G.box(x - 0.1, x, y - w / 2 - 0.12, y + w / 2 + 0.12, h, h + 0.14, "cream")
    door(XW, 0, 2.4, 3.3, 1); door(XW, AYC, 1.3, 2.5, 1); door(XW, -AYC, 1.3, 2.5, 1)
    # --- itäseinä sivulaivojen päässä, sakastin ovet ja virsitaulut
    for sgn in (1, -1):
        wall((XE, sgn * PY), (XE, sgn * HW), lambda s: ZS + parch(PY + s - AYC, AHS, RA) + 0.02, (0, sgn * 8))
        door(XE, sgn * (AYC + 0.6), 1.2, 2.4, -1)
        y = sgn * 6.1; G.box(XE - 0.07, XE, y - 0.55, y + 0.55, 2.9, 4.3, "gold", skip="x+")
        G.face([(XE - 0.075, y - 0.5, 2.95), (XE - 0.075, y + 0.5, 2.95), (XE - 0.075, y + 0.5, 4.25), (XE - 0.075, y - 0.5, 4.25)], "hymn",
               uv=[(1, 0), (0, 0), (0, 1), (1, 1)], toward=(0, y, 3))
    # --- kuorin seinät: suora osa + viisi monikulmion sivua, ikkunat
    abands = ((2.6, "dado"), (3.5, "frieze"), (1e9, "wall"))
    atop = lambda s: ZSA + 0.02
    for sgn in (1, -1): wall((XE, sgn * PY), (APX, sgn * PY), atop, (APX, 0), bands=abands, zbase=FLZ)
    for k in range(5):
        p0, p1 = ap[k], ap[k + 1]; L = math.dist(p0, p1)
        wall(p0, p1, atop, (APX, 0), [Win(L / 2, 1.5, 4.6, 8.9, 1.1, "glass_apse")], bands=abands, zbase=FLZ)
        respond(p0[0], p0[1], math.atan2(-p0[1], APX - p0[0]), ZSA, 0.16)
    respond(ap[5][0], ap[5][1], pi / 2, ZSA, 0.16)

    # --- holvit
    for i in range(8):
        vault(XB[i], XB[i + 1], -CY, CY, RX, RN, ZS, 10, 14)
        for sgn in (1, -1): vault(XB[i], XB[i + 1], min(sgn * CY, sgn * HW), max(sgn * CY, sgn * HW), RX, RA, ZS, 10, 10)
    vault(XW, XB[0], -CY, CY, RX, RN, ZS, 2, 14, barrel=True)
    for sgn in (1, -1): vault(XW, XB[0], min(sgn * CY, sgn * HW), max(sgn * CY, sgn * HW), RX, RA, ZS, 2, 10, barrel=True)
    vault(XE, APX, -PY, PY, RX, RAP, ZSA, 3, 14, barrel=True)
    apo = APR * cos(radians(18)); nrm = [(cos(radians(a)), sin(radians(a))) for a in (72, 36, 0, -36, -72)]
    def hap(x, y):
        t = max((x - APX) * n[0] + y * n[1] for n in nrm) / apo
        return ZSA + parch(t * PY, PY, RAP)
    C = (APX, 0)
    for k in range(5):
        p0, p1 = ap[k], ap[k + 1]; N = 7
        for j in range(N):
            for i in range(N):
                def pt(jj, ii):
                    r = jj / N; e = (p0[0] + (p1[0] - p0[0]) * ii / N, p0[1] + (p1[1] - p0[1]) * ii / N)
                    x, y = C[0] + (e[0] - C[0]) * r, C[1] + (e[1] - C[1]) * r; return (x, y, hap(x, y))
                q = [pt(j, i), pt(j + 1, i), pt(j + 1, i + 1), pt(j, i + 1)]
                if j == 0: G.face(q[1:], "vault", up=False)
                else: G.face(q[:3], "vault", up=False); G.face([q[0], q[2], q[3]], "vault", up=False)
        G.sweep([(C[0] + (p0[0] - C[0]) * r / 10, (p0[1]) * r / 10, hap(C[0] + (p0[0] - C[0]) * r / 10 * 0.999, p0[1] * r / 10 * 0.999)) for r in range(11)], 0.16, 0.2, "rib", (APX, 0, 6))
    G.sweep([(APX, -PY + 2 * PY * r / 16, ZSA + parch(-PY + 2 * PY * r / 16, PY, RAP)) for r in range(17)], 0.2, 0.22, "rib", (APX, 0, 6))
    G.cyl(APX, 0, ZSA + RAP - 0.3, ZSA + RAP - 0.12, 0.45, 12, "gold", r1=0.3); G.face([(APX + 0.45 * cos(i * pi / 6), 0.45 * sin(i * pi / 6), ZSA + RAP - 0.3) for i in range(12)], "gold", up=False)
    # ruoteet: lävistäjät, poikkikaaret, arkadikaaret, seinäkaaret
    def ribs(x0, x1, y0, y1, ry, diag=True):
        xc, yc, a, b = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
        h = lambda x, y: ZS + max(parch(x - xc, a, RX), parch(y - yc, b, ry)); ref = (xc, yc, 4)
        if diag:
            for (xa, ya, xb_, yb) in ((x0, y0, x1, y1), (x0, y1, x1, y0)):
                G.sweep([(xa + (xb_ - xa) * t / 20, ya + (yb - ya) * t / 20, h(xa + (xb_ - xa) * t / 20, ya + (yb - ya) * t / 20)) for t in range(21)], 0.15, 0.2, "rib", ref)
            G.cyl(xc, yc, ZS + max(RX, ry) - 0.28, ZS + max(RX, ry) - 0.1, 0.36, 10, "gold", r1=0.24)
            G.face([(xc + 0.36 * cos(i * pi / 5), yc + 0.36 * sin(i * pi / 5), ZS + max(RX, ry) - 0.28) for i in range(10)], "gold", up=False)
    for i in range(8):
        ribs(XB[i], XB[i + 1], -CY, CY, RN)
        for sgn in (1, -1): ribs(XB[i], XB[i + 1], min(sgn * CY, sgn * HW), max(sgn * CY, sgn * HW), RA)
        xc = XB[i] + BAY / 2
        for yl, w, d in ((CY, 0.5, 0.42), (-CY, 0.5, 0.42), (HW - 0.02, 0.2, 0.16), (-HW + 0.02, 0.2, 0.16)):   # pituussuunnan kaaret
            G.sweep([(XB[i] + BAY * t / 16, yl, ZS + parch(XB[i] + BAY * t / 16 - xc, BAY / 2, RX)) for t in range(17)], w, d, "rib", (xc, yl * 0.8, 4))
    for i in range(9):                                                                                              # poikkikaaret
        x = XB[i] if i < 8 else XB[8] - 0.2
        G.sweep([(x, -CY + 2 * CY * t / 20, ZS + parch(-CY + 2 * CY * t / 20, CY, RN)) for t in range(21)], 0.36 if i < 8 else 0.7, 0.3 if i < 8 else 0.6, "rib", (x, 0, 4))
        for sgn in (1, -1):
            G.sweep([(x if i < 8 else XE - 0.1, sgn * (CY + 2 * AHS * t / 14), ZS + parch(CY + 2 * AHS * t / 14 - AYC, AHS, RA)) for t in range(15)], 0.3, 0.26, "rib", (x, sgn * AYC, 4))
    # kuorin kaari: seinä keskilaivan holvin ja kuorin holvin välissä
    for t in range(16):
        ya, yb = -CY + 2 * CY * t / 16, -CY + 2 * CY * (t + 1) / 16
        na, nb = ZS + parch(ya, CY, RN), ZS + parch(yb, CY, RN); ca, cb = ZSA + parch(ya, PY, RAP), ZSA + parch(yb, PY, RAP)
        if max(na - ca, nb - cb) > 0.02: G.face([(XE, ya, min(ca, na)), (XE, yb, min(cb, nb)), (XE, yb, nb), (XE, ya, na)], "wall", toward=(0, 0, 12))
        if max(ca - na, cb - nb) > 0.02: G.face([(XE, ya, min(ca, na)), (XE, yb, min(cb, nb)), (XE, yb, cb), (XE, ya, ca)], "wall", toward=(APX + 3, 0, 12))
    for sgn in (1, -1):                         # kuorin kaaren ja kuorin seinän välinen kaista (y 4,6..4,9)
        G.face([(XE, sgn * CY, ZS - 0.4), (XE, sgn * PY, ZS - 0.4), (XE, sgn * PY, ZSA + 2.6), (XE, sgn * CY, ZSA + 2.6)], "wall", toward=(APX + 3, 0, 10))

    # --- pylväät
    for i in range(8):
        for sgn in (1, -1): column(XB[i], sgn * CY)
    for sgn in (1, -1):
        column(XB[8] - 0.25, sgn * CY)
        respond(XW, sgn * CY, 0)

    # --- lehterit
    def gal_front(p0, p1, nrm):
        (x0, y0), (x1, y1) = p0, p1; L = math.dist(p0, p1); c = ((x0 + x1) / 2 + nrm[0] * 3, (y0 + y1) / 2 + nrm[1] * 3, 5)
        e = (nrm[0] * 0.06, nrm[1] * 0.06)
        G.face([(x0, y0, GZ0 - 0.3), (x1, y1, GZ0 - 0.3), (x1, y1, GZ1 + 0.02), (x0, y0, GZ1 + 0.02)], "cream", toward=c)
        n = max(1, round(L / 0.58))
        G.face([(x0, y0, GZ1 + 0.02), (x1, y1, GZ1 + 0.02), (x1, y1, GP), (x0, y0, GP)], "galfront", uv=[(0, 0), (n, 0), (n, 1), (0, 1)], toward=c)
        G.face([(x0 + e[0], y0 + e[1], GP), (x1 + e[0], y1 + e[1], GP), (x1 - 2 * e[0], y1 - 2 * e[1], GP), (x0 - 2 * e[0], y0 - 2 * e[1], GP)], "ochre", up=True)
        G.face([(x0 - 2 * e[0], y0 - 2 * e[1], GZ1), (x1 - 2 * e[0], y1 - 2 * e[1], GZ1), (x1 - 2 * e[0], y1 - 2 * e[1], GP), (x0 - 2 * e[0], y0 - 2 * e[1], GP)], "ochre", away=c)
        G.face([(x0, y0, GZ0 - 0.3), (x1, y1, GZ0 - 0.3), (x1 - 4 * e[0], y1 - 4 * e[1], GZ0 - 0.3), (x0 - 4 * e[0], y0 - 4 * e[1], GZ0 - 0.3)], "cream", up=False)
    yf = CY + 0.08
    for sgn in (1, -1):
        G.face([(XB[1], sgn * yf, GZ0), (XE, sgn * yf, GZ0), (XE, sgn * HW, GZ0), (XB[1], sgn * HW, GZ0)], "cream", up=False)
        G.face([(XB[1], sgn * yf, GZ1), (XE, sgn * yf, GZ1), (XE, sgn * HW, GZ1), (XB[1], sgn * HW, GZ1)], "ochre", up=True)
        for i in range(1, 8):
            x1 = XB[i + 1] - (0.5 if i < 7 else 0.75)
            gal_front((XB[i] + 0.5, sgn * yf), (x1, sgn * yf), (0, -sgn))
            for x in (XB[i] + 2.77,):                     # poikkipalkki lehterin alla
                G.box(x - 0.1, x + 0.1, min(sgn * (yf + 0.3), sgn * HW), max(sgn * (yf + 0.3), sgn * HW), GZ0 - 0.22, GZ0, "cream", skip="z+")
        for r in range(3):                               # lehterin penkit (näkyvät kaiteen yli vain selkänojina)
            y = sgn * (yf + 1.3 + r * 1.6)
            G.box(XB[1] + 0.6, XE - 0.6, y - 0.04, y + 0.04, GZ1 + 0.3 * r, GZ1 + 0.3 * r + 0.95, "ochre", skip="z-")
    xg = XB[1] - 0.08                                     # urkulehteri länsipäässä
    G.face([(XW, -HW, GZ0), (XB[1], -HW, GZ0), (XB[1], HW, GZ0), (XW, HW, GZ0)], "cream", up=False)
    G.face([(XW, -HW, GZ1), (XB[1], -HW, GZ1), (XB[1], HW, GZ1), (XW, HW, GZ1)], "ochre", up=True)
    gal_front((xg + 0.16, -CY + 0.5), (xg + 0.16, CY - 0.5), (1, 0))
    for y in (-2.3, 0, 2.3): G.box(XW, XB[1], y - 0.1, y + 0.1, GZ0 - 0.22, GZ0, "cream", skip="z+")

    # --- urut (Paschen 2007 -tyyppinen kullanruskea kaappi, kolme tornia ja pillikentät)
    ox0, ox1 = XW + 0.5, XW + 2.9
    G.box(ox0, ox1, -4.3, 4.3, GZ1, 7.5, "organ", skip="z-x-")
    G.box(ox0, ox1 + 0.12, -4.45, 4.45, 7.5, 7.72, "gold", skip="x-")
    G.box(ox0, ox1 - 0.9, -4.3, 4.3, 7.72, 11.6, "organ", skip="z-x-")
    def pipes(y0, y1, zb, hts, r):
        n = len(hts); G.small = True
        for k, hh in enumerate(hts):
            y = y0 + (y1 - y0) * (k + 0.5) / n
            G.cyl(ox1 - 0.45, y, zb, zb + 0.35, 0.02, 8, "pipe", -pi / 2, pi / 2, r1=r); G.cyl(ox1 - 0.45, y, zb + 0.35, zb + hh, r, 8, "pipe", -pi / 2, pi / 2)
            G.face([(ox1 - 0.45 + r * 0.99, y - r * 0.5, zb + 0.42), (ox1 - 0.45 + r * 0.99, y + r * 0.5, zb + 0.42), (ox1 - 0.45 + r * 0.99, y + r * 0.5, zb + 0.5), (ox1 - 0.45 + r * 0.99, y - r * 0.5, zb + 0.5)], "black", toward=(0, y, zb))
        G.small = False
    def tower(yc, w, zt, np_):
        for sy in (-1, 1): G.box(ox1 - 0.9, ox1 - 0.2, yc + sy * w / 2 - 0.09, yc + sy * w / 2 + 0.09, 7.72, zt, "organ", skip="z-")
        G.box(ox1 - 0.9, ox1 - 0.1, yc - w / 2 - 0.16, yc + w / 2 + 0.16, zt, zt + 0.3, "organ")
        G.box(ox1 - 0.8, ox1 - 0.25, yc - w / 2, yc + w / 2, zt - 0.5, zt, "gold", skip="z+")
        for k in range(4):
            a0, a1 = k * pi / 2 + pi / 4, (k + 1) * pi / 2 + pi / 4; cx = ox1 - 0.5
            G.face([(cx + 0.72 * w * cos(a0), yc + 0.72 * w * sin(a0), zt + 0.3), (cx + 0.72 * w * cos(a1), yc + 0.72 * w * sin(a1), zt + 0.3), (cx, yc, zt + 0.3 + w * 1.5)], "organ", away=(cx, yc, zt))
        G.cyl(ox1 - 0.5, yc, zt + 0.3 + w * 1.5 - 0.1, zt + 0.3 + w * 1.5 + 0.35, 0.05, 6, "gold", r1=0.0)
        pipes(yc - w / 2 + 0.1, yc + w / 2 - 0.1, 7.9, [zt - 8.6 - 0.25 * abs(k - (np_ - 1) / 2) for k in range(np_)], (w - 0.2) / np_ / 2 * 0.86)
    tower(0, 1.5, 13.2, 5); tower(-3.55, 1.3, 12.5, 5); tower(3.55, 1.3, 12.5, 5)
    for sgn in (1, -1):
        y0, y1 = sgn * 0.9, sgn * 2.8; ya, yb = min(y0, y1), max(y0, y1)
        hts = [2.0 + 1.5 * abs(k - 5.5) / 5.5 for k in range(12)]
        pipes(ya, yb, 7.9, hts, 0.068)
        for k in range(12):                               # kullatut pilliverhot
            y = ya + (yb - ya) * k / 12; hh = 7.9 + max(hts[k], hts[min(11, k + 1)])
            G.box(ox1 - 0.52, ox1 - 0.36, y, y + (yb - ya) / 12, hh - 0.05, hh + 0.28, "gold", skip="x-")
        G.box(ox1 - 0.9, ox1 - 0.3, ya, yb, 11.3, 11.6, "organ")
        for t in range(6):                                # päätykolmio pillikentän päällä
            G.box(ox1 - 0.75, ox1 - 0.4, ya + (yb - ya) * t / 12, yb - (yb - ya) * t / 12, 11.6 + t * 0.14, 11.6 + (t + 1) * 0.14, "organ", skip="z-")
    G.box(ox1, ox1 + 0.9, -0.9, 0.9, GZ1, GZ1 + 1.3, "organ", skip="z-x-")    # soittopöytä

    # --- penkit
    def pew(x, y0, y1):
        G.box(x - 0.24, x + 0.22, y0 + 0.07, y1 - 0.07, 0.40, 0.45, "ochre")
        G.box(x - 0.30, x - 0.25, y0 + 0.07, y1 - 0.07, 0.12, 0.98, "ochre", skip="z-")
        G.box(x - 0.42, x - 0.30, y0 + 0.07, y1 - 0.07, 0.72, 0.75, "ochre")
        for y in (y0, y1 - 0.07):
            G.box(x - 0.36, x + 0.26, y, y + 0.07, 0.0, 0.92, "ochre", skip="z-"); G.box(x - 0.36, x - 0.18, y, y + 0.07, 0.92, 1.10, "ochre", skip="z-")
    px0, npew = XB[1] + 1.6, 0
    x = px0
    while x < XS0 - 2.2:
        for (ya, yb) in ((1.0, CY - 0.75), (-CY + 0.75, -1.0), (CY + 0.9, HW - 1.3), (-HW + 1.3, -CY - 0.9)):
            pew(x, ya, yb); npew += 1
        x += 0.98
    xl = x - 0.98
    for (ya, yb) in ((1.0, CY - 0.75), (-CY + 0.75, -1.0), (CY + 0.9, HW - 1.3), (-HW + 1.3, -CY - 0.9)):
        for (a, b) in (((px0 - 0.45, ya), (xl + 0.3, ya)), ((px0 - 0.45, yb), (xl + 0.3, yb)), ((px0 - 0.45, ya), (px0 - 0.45, yb)), ((xl + 0.3, ya), (xl + 0.3, yb))):
            COL["seg"].append([a[0], a[1], b[0], b[1], 0.02])

    # --- saarnatuoli (pohjoispuolen viimeisen pylvään edessä)
    pxc, pyc = XB[7] - 0.2, CY - 1.25
    G.cyl(pxc, pyc, 0, 1.5, 0.22, 8, "dark"); G.cyl(pxc, pyc, 1.5, 1.95, 0.22, 8, "dark", r1=0.95)
    G.cyl(pxc, pyc, 1.95, 3.05, 0.95, 8, "ochre", pi / 8, 2 * pi + pi / 8); G.cyl(pxc, pyc, 3.05, 3.13, 1.02, 8, "gold", pi / 8, 2 * pi + pi / 8)
    G.cyl(pxc, pyc, 1.95, 2.03, 1.0, 8, "gold", pi / 8, 2 * pi + pi / 8)
    G.face([(pxc + 0.95 * cos(i * pi / 4 + pi / 8), pyc + 0.95 * sin(i * pi / 4 + pi / 8), 1.95) for i in range(8)], "dark", up=False)
    G.cyl(pxc, pyc, 5.3, 5.5, 1.15, 8, "ochre", pi / 8, 2 * pi + pi / 8); G.cyl(pxc, pyc, 5.5, 6.9, 1.05, 8, "ochre", pi / 8, 2 * pi + pi / 8, r1=0.0)
    G.face([(pxc + 1.15 * cos(i * pi / 4 + pi / 8), pyc + 1.15 * sin(i * pi / 4 + pi / 8), 5.3) for i in range(8)], "cream", up=False)
    G.cyl(pxc, pyc, 6.85, 7.25, 0.05, 6, "gold", r1=0.0)
    G.box(pxc - 0.06, pxc + 0.06, CY - 0.5, CY - 0.38, 3.0, 5.3, "ochre")
    for k in range(7):                                    # portaat pylvään takaa
        G.box(pxc + 0.9 + k * 0.3, pxc + 1.2 + k * 0.3, pyc - 0.1, pyc + 0.75, 1.9 - (k + 1) * 0.27, 1.9 - k * 0.27, "ochre")
    COL["circ"].append([pxc, pyc, 1.0]); COL["seg"].append([pxc + 0.9, pyc + 0.3, pxc + 3.0, pyc + 0.3, 0.45])

    # --- alttari, alttarilaite, alttarikaide
    ax = APX + 2.5
    G.box(ax, ax + 1.0, -1.35, 1.35, FLZ, FLZ + 1.05, "white", skip="z-"); G.box(ax - 0.01, ax, -0.5, 0.5, FLZ + 0.1, FLZ + 1.0, "carpet", skip="x+z-z+")
    G.box(ax + 1.0, ax + 1.6, -1.7, 1.7, FLZ, FLZ + 1.7, "dark", skip="z-")
    zb, zt = FLZ + 1.7, FLZ + 5.6
    G.box(ax + 1.2, ax + 1.5, -1.5, 1.5, zb, zt, "gold", skip="z-", mats={"x-": "gold"})
    G.face([(ax + 1.19, -1.25, zb + 0.15), (ax + 1.19, 1.25, zb + 0.15), (ax + 1.19, 1.25, zt - 0.15), (ax + 1.19, -1.25, zt - 0.15)], "altar", uv=[(1, 0), (0, 0), (0, 1), (1, 1)], toward=(0, 0, 3))
    G.face([(ax + 1.2, -1.6, zt), (ax + 1.2, 1.6, zt), (ax + 1.2, 0, zt + 1.5)], "gold", toward=(0, 0, 6)); G.face([(ax + 1.5, -1.6, zt), (ax + 1.5, 1.6, zt), (ax + 1.5, 0, zt + 1.5)], "gold", toward=(60, 0, 6))
    G.cyl(ax + 1.35, 0, zt + 1.4, zt + 2.0, 0.06, 6, "gold", r1=0.0)
    for sgn in (1, -1):
        G.box(ax + 1.15, ax + 1.55, sgn * 1.5 - 0.17, sgn * 1.5 + 0.17, zb, zt + 0.6, "gold", skip="z-")
        G.cyl(ax + 1.35, sgn * 1.5, zt + 0.6, zt + 1.7, 0.24, 4, "gold", pi / 4, 2 * pi + pi / 4, r1=0.0)
        G.cyl(ax + 0.5, sgn * 0.95, FLZ + 1.05, FLZ + 1.5, 0.035, 6, "white"); G.cyl(ax + 0.5, sgn * 0.95, FLZ + 1.5, FLZ + 1.58, 0.03, 6, "bulb", r1=0.0)
    G.box(ax + 0.42, ax + 0.48, -0.03, 0.03, FLZ + 1.05, FLZ + 1.65, "gold"); G.box(ax + 0.42, ax + 0.48, -0.2, 0.2, FLZ + 1.43, FLZ + 1.49, "gold")
    COL["seg"].append([ax + 0.2, -1.6, ax + 0.2, 1.6, 0.25]); COL["seg"].append([ax + 1.2, -1.7, ax + 1.2, 1.7, 0.5])
    G.small = True
    rc, rr = (APX + 0.9, 0.0), 3.3                         # kaide: kaari, portti keskellä
    angs = [radians(100 + 160 * k / 28) for k in range(29)]
    rp = [(rc[0] + rr * cos(a), rc[1] + rr * sin(a)) for a in angs]
    rp = [(rp[0][0] + 0.9, PY)] + rp + [(rp[-1][0] + 0.9, -PY)]
    for (a, b) in zip(rp, rp[1:]):
        if abs((a[1] + b[1]) / 2) < 0.62: continue
        dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy); nx, ny = -dy / L * 0.05, dx / L * 0.05
        for z0, z1, m in ((FLZ + 0.88, FLZ + 0.96, "gold"), (FLZ + 0.08, FLZ + 0.14, "dark")):
            c = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (z0 + z1) / 2)
            q = [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]
            G.face([(*p, z1) for p in q], m, up=True); G.face([(*p, z0) for p in q], m, up=False)
            G.face([(*q[0], z0), (*q[1], z0), (*q[1], z1), (*q[0], z1)], m, away=c); G.face([(*q[3], z0), (*q[2], z0), (*q[2], z1), (*q[3], z1)], m, away=c)
        n = max(2, round(L / 0.16))
        for k in range(n):
            x, y = a[0] + dx * (k + 0.5) / n, a[1] + dy * (k + 0.5) / n; G.cyl(x, y, FLZ + 0.14, FLZ + 0.88, 0.022, 4, "dark" if k % 2 else "gold")
        COL["seg"].append([a[0], a[1], b[0], b[1], 0.08])
    # kattokruunut (messinki), kynttilät valaisevat
    LAMPS = []
    def chandelier(x, y, z, r, top):
        G.cyl(x, y, z + 1.3, top, 0.02, 4, "dark"); G.cyl(x, y, z - 0.5, z + 1.3, 0.06, 8, "gold"); G.cyl(x, y, z - 0.75, z - 0.5, 0.0, 8, "gold", r1=0.16); G.cyl(x, y, z + 0.1, z + 0.4, 0.2, 8, "gold", r1=0.06)
        for tier, (rr_, zz, n) in enumerate(((r, z, 12), (r * 0.62, z + 0.75, 8))):
            for k in range(n):
                a0, a1 = 2 * pi * k / n, 2 * pi * (k + 1) / n; am = (a0 + a1) / 2
                p0, p1 = (x + rr_ * cos(a0), y + rr_ * sin(a0)), (x + rr_ * cos(a1), y + rr_ * sin(a1))
                G.face([(*p0, zz - 0.03), (*p1, zz - 0.03), (*p1, zz + 0.03), (*p0, zz + 0.03)], "gold", away=(x, y, zz)); G.face([(*p0, zz - 0.03), (*p1, zz - 0.03), (*p1, zz + 0.03), (*p0, zz + 0.03)], "gold", toward=(x, y, zz))
                cx, cy = x + rr_ * cos(a0), y + rr_ * sin(a0)
                G.face([(x, y, zz - 0.25), (cx, cy, zz - 0.03), (cx, cy, zz + 0.02), (x, y, zz - 0.18)], "gold", toward=(x + 9 * cos(a0 + 1.57), y + 9 * sin(a0 + 1.57), zz))
                G.face([(x, y, zz - 0.25), (cx, cy, zz - 0.03), (cx, cy, zz + 0.02), (x, y, zz - 0.18)], "gold", toward=(x - 9 * cos(a0 + 1.57), y - 9 * sin(a0 + 1.57), zz))
                G.cyl(cx, cy, zz + 0.03, zz + 0.2, 0.018, 5, "white"); G.cyl(cx, cy, zz + 0.2, zz + 0.3, 0.028, 5, "bulb", r1=0.0)
        LAMPS.append((x, y, z + 0.4, r))
    G.small = True
    for i in (1, 3, 5): chandelier(XB[i] + BAY / 2, 0, 7.4, 1.05, ZS + RN - 0.3)
    chandelier(APX - 0.6, 0, 7.6, 0.8, ZSA + RAP - 0.3)
    G.small = False
    return LAMPS

# ---------------------------------------------------------------- Blender-kohtaus
def make_scene(LAMPS):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scn = bpy.context.scene
    mats = []
    for name, (sc, glow) in MATDEF.items():
        m = bpy.data.materials.new(("glow_" if glow else "") + name); m.use_nodes = True; nt = m.node_tree
        for n in list(nt.nodes): nt.nodes.remove(n)
        out = nt.nodes.new("ShaderNodeOutputMaterial"); uvn = nt.nodes.new("ShaderNodeUVMap"); uvn.uv_map = "UVMap"
        ti = nt.nodes.new("ShaderNodeTexImage"); ti.image = bpy.data.images.load(TEX[name]); ti.name = "albedo"
        nt.links.new(uvn.outputs[0], ti.inputs[0])
        b = nt.nodes.new("ShaderNodeBsdfPrincipled"); b.inputs["Roughness"].default_value = 0.85
        for k in ("Specular IOR Level", "Specular"):
            if k in b.inputs: b.inputs[k].default_value = 0.15; break
        nt.links.new(ti.outputs[0], b.inputs["Base Color"])
        if glow:
            for k in ("Emission Color", "Emission"):
                if k in b.inputs: nt.links.new(ti.outputs[0], b.inputs[k]); break
            b.inputs["Emission Strength"].default_value = glow
        nt.links.new(b.outputs[0], out.inputs[0])
        mats.append(m)
    objs = {}
    names = list(MATDEF)
    for kind in ("lit", "small", "glow"):
        idx = [i for i in range(len(G.F)) if ("glow" if MATDEF[names[G.M[i]]][1] > 0 else "small" if G.S[i] else "lit") == kind]
        bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap")
        for i in idx:
            vs = [bm.verts.new(G.V[v]) for v in G.F[i]]
            try: f = bm.faces.new(vs)
            except ValueError: continue
            f.material_index = G.M[i]
            for l, uv in zip(f.loops, G.UV[i]): l[uvl].uv = uv
        bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.0005)
        me = bpy.data.meshes.new("sisa_" + kind); bm.to_mesh(me); bm.free()
        for m in mats: me.materials.append(m)
        me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
        try: me.set_sharp_from_angle(angle=radians(35))
        except AttributeError: pass
        if kind == "small":
            l2 = me.uv_layers.new(name="LM")
            for d in l2.data: d.uv = (0.004, 0.004)
            me.uv_layers["UVMap"].active_render = True
        ob = bpy.data.objects.new("sisa_" + kind, me); scn.collection.objects.link(ob); objs[kind] = ob
        print(kind, len(me.polygons), "pintaa")
    for (x, y, z, r) in LAMPS:
        l = bpy.data.lights.new("kruunu", "POINT"); l.energy = 420 * r; l.color = (1.0, 0.78, 0.50); l.shadow_soft_size = 0.5
        o = bpy.data.objects.new("kruunu", l); o.location = (x, y, z); scn.collection.objects.link(o)
    w = bpy.data.worlds.new("w"); scn.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[1].default_value = 0.0
    scn.render.engine = "CYCLES"; scn.cycles.device = "CPU"; scn.cycles.samples = A.samples
    scn.cycles.max_bounces = 6; scn.cycles.diffuse_bounces = 5; scn.cycles.caustics_reflective = False; scn.cycles.caustics_refractive = False
    scn.cycles.sample_clamp_indirect = 4.0; scn.cycles.sample_clamp_direct = 12.0
    try: scn.cycles.use_denoising = True
    except Exception: pass
    return objs

def shots(tag="", V=None):
    scn = bpy.context.scene
    cam = bpy.data.cameras.new("c"); co = bpy.data.objects.new("c", cam); scn.collection.objects.link(co); scn.camera = co
    scn.render.resolution_x, scn.render.resolution_y = 960, 600
    scn.view_settings.view_transform = "Standard"; scn.view_settings.exposure = 0.0
    V = V or dict(alttarille=((-17.5, 0.0, 1.7), (20, 0, 5.5), 20), uruille=((14, 0.5, 1.7), (-20, 0, 7.5), 20), sivulaiva=((-10, 8.2, 1.7), (20, 5, 4.0), 22),
             kuori=((17.5, 0.0, 2.2), (30, 0, 4.6), 24), lehteri=((0, -3.0, 1.7), (12, 9, 6.5), 20))
    for k, (loc, tgt, lens) in V.items():
        co.location = loc; co.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler(); cam.lens = lens; cam.clip_start = 0.1
        scn.render.filepath = "%s/shot_%s%s.png" % (OUT, k, tag); bpy.ops.render.render(write_still=True)

def bake(objs):
    scn = bpy.context.scene; ob = objs["lit"]; me = ob.data
    for o in bpy.data.objects: o.select_set(False)
    ob.select_set(True); bpy.context.view_layer.objects.active = ob
    lm = me.uv_layers.new(name="LM"); me.uv_layers.active = lm
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=radians(62), island_margin=0.0012, area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    me = ob.data; lm = me.uv_layers["LM"]                                           # muokkaustila varaa verkon uudelleen: vanha viite on kuollut
    for d in lm.data: d.uv = (0.012 + d.uv[0] * 0.988, 0.012 + d.uv[1] * 0.988)     # vasen alakulma varataan pikkuosien vakiovalolle
    me.uv_layers["UVMap"].active_render = True
    img = bpy.data.images.new("LM", A.lm, A.lm, alpha=False, float_buffer=True)
    for m in me.materials:
        nt = m.node_tree; n = nt.nodes.new("ShaderNodeTexImage"); n.image = img; n.name = "LMNODE"
        u = nt.nodes.new("ShaderNodeUVMap"); u.uv_map = "LM"; nt.links.new(u.outputs[0], n.inputs[0])
        for q in nt.nodes: q.select = False
        n.select = True; nt.nodes.active = n
    scn.cycles.bake_type = "DIFFUSE"; bs = scn.render.bake
    bs.use_pass_direct = True; bs.use_pass_indirect = True; bs.use_pass_color = False; bs.margin = 6; bs.use_clear = True
    try: bs.margin_type = "EXTEND"
    except Exception: pass
    import time; t = time.time()
    bpy.ops.object.bake(type="DIFFUSE")
    print("leivonta %.0f s" % (time.time() - t))
    a = np.array(img.pixels[:], dtype=np.float32).reshape(A.lm, A.lm, 4)[::-1, :, :3]
    np.save(OUT + "/lm_raw.npy", a)
    for m in me.materials:
        nt = m.node_tree; nt.nodes.remove(nt.nodes["LMNODE"]); nt.nodes.active = nt.nodes["albedo"]
    return a

LM_REF = 0.62                            # valokartan 80. prosenttipisteen tavoitetaso
def finish_lm(a):
    a = np.nan_to_num(a)
    """Valokartan viimeistely: kohinanpoisto (pehmeä valo kestää sen), mitoitus ja sRGB-pakkaus alueelle 0..LMAX."""
    import cv2
    lum = a.mean(-1); ok = lum > 1e-5
    ref = float(np.percentile(lum[ok], 80)); k = LM_REF / ref; LMAX = 2.0
    b = np.clip(a * k, 0, LMAX * 2).astype(np.float32)
    try: b = cv2.medianBlur(b, 3); b = cv2.bilateralFilter(b, 9, 0.30, 3.5)
    except Exception as e: print("ei kohinanpoistoa:", e)
    n8 = int(len(b) * 0.009); b[len(b) - n8:, :n8] = (0.85, 0.80, 0.70)               # pikkuosien vakiovalo (kuvan alareuna = v 0)
    b = np.clip(b / LMAX, 0, 1) ** (1 / 2.2)
    Image.fromarray((b * 255 + 0.5).astype(np.uint8)).save("%s/%s_lm.jpg" % (OUT, NAME), quality=90)
    return LMAX

def export(objs):
    for o in bpy.data.objects: o.select_set(o.type == "MESH")
    bpy.context.view_layer.objects.active = objs["lit"]
    bpy.ops.export_scene.gltf(filepath="%s/%s.glb" % (OUT, NAME), export_format="GLB", use_selection=True, export_yup=True, export_apply=True,
                              export_image_format="JPEG", export_image_quality=88, export_animations=False, export_normals=False, export_lights=False, export_cameras=False)
    print("GLB %.0f kt" % (os.path.getsize("%s/%s.glb" % (OUT, NAME)) / 1024))

if __name__ == "__main__":
    make_textures()
    LAMPS = build()
    print(len(G.F), "pintaa,", len(COL["seg"]), "janaa,", len(COL["circ"]), "ympyrää")
    objs = make_scene(LAMPS)
    if A.shots: shots()
    LMAX = 2.0
    if not A.nobake: LMAX = finish_lm(bake(objs))
    export(objs)
    meta = dict(col=COL, lmax=LMAX, xw=XW, xe=XE, hw=HW, py=PY, xs0=XS0, flz=FLZ, apx=APX, apr=APR, spawn=[XW + 1.6, 0.0], exit=[XW + 1.0, 1.7],
                room=[[XW, -HW], [XE, -HW], [XE, -PY]] + [[APX + APR * cos(radians(a)), APR * sin(radians(a))] for a in (-90, -54, -18, 18, 54, 90)] + [[XE, PY], [XE, HW], [XW, HW]])
    json.dump(meta, open(OUT + "/kirkko_sisa.json", "w"))
