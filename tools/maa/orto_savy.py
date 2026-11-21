"""Ilmakuvan sävykorjaus "lumen" poistamiseksi, 21.11.2026 (MAAN_PINTA_SUUNNITELMA.md, vaihe 1).

    python tools/maa/orto_savy.py                     # ot/ot_i_j.jpg -> maa/ot_s/ot_i_j.jpg (+ orto.jpg, outer.jpg -> maa/ot_s/)
    python tools/maa/orto_savy.py --vertailu 2 3      # tools/maa/out/savy_2_3.jpg: ennen | jälkeen rinnakkain
    python tools/maa/orto_savy.py --vahvuus 0.8       # 0..1 (oletus 1)

Alkuperäisiin ei kosketa. Peli ottaa korjatut käyttöön vaihtamalla polun 033_ilmakuva_tarkka.js:ssä (`./ot/` -> `./maa/ot_s/`), kun omistaja
on hyväksynyt vertailukuvat. HUOM: samoja ot-laattoja käytetään myös kattojen tekstuurina (roofTile), joten katot muuttuvat samalla.

Mitä tehdään (pikseleittäin, ei koneoppimista):
 1. ylivalottuneiden kohtien pehmeä kompressio (kirkkaus > 0,72 painetaan polvikäyrällä; valkoiset betonit, katot ja jäkälä eivät enää näytä lumelta)
 2. harmaan kylmän sävyn lämmitys (MML-ortokuvassa sininen vivahde), valkotasapaino laattakohtaisen harmaan keskiarvon mukaan
 3. varjojen lievä nosto (gamma tummissa)
 4. kasvillisuuden saturaation lisäys kesäiseksi (vihreä, ei keltainen), muun saturaation lievä lasku
"""
import argparse, glob, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from yhteiset import REPO


def korjaa(a, v=1.0):
    x = a.astype(np.float32) / 255.0
    lum = 0.2126 * x[..., 0] + 0.7152 * x[..., 1] + 0.0722 * x[..., 2]
    mx, mn = x.max(-1), x.min(-1)
    sat = (mx - mn) / np.maximum(mx, 1e-3)
    # 2. valkotasapaino harmaista (matala saturaatio, keskikirkkaus)
    m = (sat < 0.12) & (lum > 0.25) & (lum < 0.7)
    if m.sum() > 1000:
        g = x[m].mean(0); g = g / g.mean()
        x = x / (1 + (g - 1) * 0.7 * v)
    # 4. saturaatio: kasvillisuus +, muu -
    lum = (0.2126 * x[..., 0] + 0.7152 * x[..., 1] + 0.0722 * x[..., 2])[..., None]
    veg = ((2 * x[..., 1] - x[..., 0] - x[..., 2]) > 0.06)[..., None]
    k = np.where(veg, 1 + 0.25 * v, 1 - 0.12 * v)
    x = lum + (x - lum) * k
    # 1. polvikompressio kirkkaille + 3. varjojen nosto
    l2 = np.clip(0.2126 * x[..., 0] + 0.7152 * x[..., 1] + 0.0722 * x[..., 2], 1e-4, None)
    knee, top = 0.72, 0.86
    lo = l2 + v * 0.06 * np.clip(0.25 - l2, 0, None) / 0.25 * (1 - l2)        # tummat ylös hieman
    hi = np.where(lo > knee, knee + (top - knee) * (1 - np.exp(-(lo - knee) / (top - knee))), lo)
    x = x * (hi / l2)[..., None]
    return (np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--vertailu', nargs=2, type=int)
    ap.add_argument('--vahvuus', type=float, default=1.0)
    ap.add_argument('--ulos', default=os.path.join(REPO, 'maa', 'ot_s'))
    A = ap.parse_args()
    if A.vertailu:
        i, j = A.vertailu
        a = np.asarray(Image.open(os.path.join(REPO, 'ot', f'ot_{i}_{j}.jpg')).convert('RGB'))
        b = korjaa(a, A.vahvuus)
        os.makedirs(os.path.join(REPO, 'tools', 'maa', 'out'), exist_ok=True)
        f = os.path.join(REPO, 'tools', 'maa', 'out', f'savy_{i}_{j}.jpg')
        Image.fromarray(np.concatenate([a, b], 1)).save(f, quality=88); print(f)
        sys.exit()
    os.makedirs(A.ulos, exist_ok=True)
    fs = sorted(glob.glob(os.path.join(REPO, 'ot', 'ot_*.jpg'))) + [os.path.join(REPO, n) for n in ('orto.jpg', 'outer.jpg') if os.path.exists(os.path.join(REPO, n))]
    for n, f in enumerate(fs):
        im = Image.open(f).convert('RGB')
        Image.fromarray(korjaa(np.asarray(im), A.vahvuus)).save(os.path.join(A.ulos, os.path.basename(f)), quality=90)
        if n % 20 == 0: print(n + 1, '/', len(fs), os.path.basename(f), flush=True)
    print('valmis', len(fs), '->', A.ulos)
