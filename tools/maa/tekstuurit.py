"""Maan PBR-tekstuurit pelin muotoon, 21.11.2026 (MAAN_PINTA_SUUNNITELMA.md, osa B).

    python tools/maa/tekstuurit.py              # tex/*.zip (ambientCG 1K-JPG, CC0) -> maa/tex/<luokka>_{a,n,orm}.jpg (+ _m = 512 px puhelimelle)
    python tools/maa/tekstuurit.py --lista      # mitkä luokat ovat valmiina, mitkä puuttuvat

Pakkaus (kaikki JPG, sRGB vain albedossa):
  <luokka>_a.jpg    albedo (Color), keskisävy tasattu: laattakohtainen kirkkaus normalisoidaan KIRKKAUS-arvoon, jotta materiaalit sopivat yhteen
  <luokka>_n.jpg    normaali OpenGL-suunnassa (NormalGL), kuten three.js odottaa
  <luokka>_orm.jpg  R = AO (puuttuessa 255), G = karheus (Roughness), B = korkeus (Displacement) - korkeutta käytetään luokkien rajojen
                    korkeuspohjaiseen sekoitukseen (ruoho saumoissa, sora reunoilla); metallisuutta ei tarvita maassa
Luokkanimet ovat samat kuin tools/maa/maapeite.py:n LUOKAT. Lähde ja lisenssi kirjoitetaan maa/tex/tex.json:iin.
Uudet tekstuurit: lataa ambientCG:stä 1K-JPG-zip kansioon tex/ ja lisää rivi LAHTEET-tauluun (puuttuvat: ks. --lista).
"""
import argparse, io, json, os, sys, zipfile
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from yhteiset import REPO

# luokka -> (zip tex/:ssä, toisto metreinä, tavoitekirkkaus 0..1)
LAHTEET = {
    'ajorata': ('Asphalt025C', 3.0, 0.30),
    'pysakointi': ('Asphalt025C', 3.0, 0.33),
    'jalkakaytava': ('Concrete034', 2.5, 0.48),
    'betoni': ('Concrete031', 2.5, 0.50),
    'kiveys': ('PavingStones070', 2.0, 0.42),
    'laatoitus': ('Tiles074', 2.0, 0.50),
    'nurmi': ('Grass004', 2.0, 0.30),
    'multa': ('Ground054', 2.5, 0.25),
    # puuttuvat (ambientCG, CC0), ehdotukset: sora Gravel022 / Ground037, hiekka Ground033, metsa Ground026 / ForestGround, niitty Grass001,
    # urheilu (tekonurmi) Grass004 sävytettynä, puu Planks/WoodFloor, lehtikarike Leaves?: lisätään kun zip on tex/-kansiossa
    'sora': ('Gravel022', 2.5, 0.45),
    'hiekka': ('Ground033', 3.0, 0.55),
    'metsa': ('Ground026', 3.0, 0.22),
    'niitty': ('Grass001', 2.5, 0.32),
    'puu': ('Planks021', 2.0, 0.40),
}


def lue(z, nimi, suffix):
    for n in z.namelist():
        if n.endswith('_' + suffix + '.jpg'): return Image.open(io.BytesIO(z.read(n)))
    return None


def pakkaa(luokka, zipnimi, kirkkaus, ulos, koot=((1024, ''), (512, '_m'))):
    zp = os.path.join(REPO, 'tex', zipnimi + '_1K-JPG.zip')
    if not os.path.exists(zp): return False
    z = zipfile.ZipFile(zp)
    col = lue(z, zipnimi, 'Color').convert('RGB'); nor = lue(z, zipnimi, 'NormalGL').convert('RGB')
    ao, ro, he = lue(z, zipnimi, 'AmbientOcclusion'), lue(z, zipnimi, 'Roughness'), lue(z, zipnimi, 'Displacement')
    a = np.asarray(col, np.float32) / 255.0
    lin = a ** 2.2
    m = (0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]).mean() ** (1 / 2.2)
    a = np.clip(a * (kirkkaus / max(m, 1e-3)), 0, 1)
    col = Image.fromarray((a * 255 + 0.5).astype(np.uint8))
    S = col.size
    ch = [(ao.convert('L').resize(S) if ao else Image.new('L', S, 255)), (ro.convert('L').resize(S) if ro else Image.new('L', S, 200)),
          (he.convert('L').resize(S) if he else Image.new('L', S, 128))]
    orm = Image.merge('RGB', ch)
    for px, suf in koot:
        for im, k, q in ((col, 'a', 88), (nor, 'n', 92), (orm, 'orm', 90)):
            im.resize((px, px), Image.LANCZOS).save(os.path.join(ulos, f'{luokka}_{k}{suf}.jpg'), quality=q)
    return True


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--lista', action='store_true')
    ap.add_argument('--ulos', default=os.path.join(REPO, 'maa', 'tex'))
    A = ap.parse_args()
    os.makedirs(A.ulos, exist_ok=True)
    valmiit, puuttuu = {}, []
    for luokka, (zn, toisto, kirk) in LAHTEET.items():
        if A.lista:
            (valmiit.__setitem__(luokka, zn) if os.path.exists(os.path.join(REPO, 'tex', zn + '_1K-JPG.zip')) else puuttuu.append(f'{luokka} ({zn})'))
            continue
        if pakkaa(luokka, zn, kirk, A.ulos):
            valmiit[luokka] = {'lahde': f'ambientCG {zn} (CC0, ambientcg.com)', 'toisto_m': toisto, 'kirkkaus': kirk}
            print('ok  ', luokka, zn)
        else:
            puuttuu.append(f'{luokka} ({zn})'); print('puuttuu', luokka, zn, '-> lataa tex/' + zn + '_1K-JPG.zip')
    if A.lista:
        print('valmiina:', valmiit); print('puuttuu:', puuttuu)
    else:
        json.dump({'versio': 1, 'koot': {'': 1024, '_m': 512}, 'kanavat': {'a': 'albedo sRGB', 'n': 'normaali GL', 'orm': 'R AO, G karheus, B korkeus'},
                   'luokat': valmiit, 'puuttuu': puuttuu}, open(os.path.join(A.ulos, 'tex.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
