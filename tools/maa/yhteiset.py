"""Yhteiset apufunktiot maan pinnan työkaluille (tools/maa/*.py), 21.11.2026.

Pelin koordinaatit: x = (lon - 21.796) * 53278, y = (lat - 61.486) * 111437 (metrejä, x itään, y pohjoiseen).
Aktiivinen pelialue = tarkkojen ilmakuvalaattojen alue (src/js/033_ilmakuva_tarkka.js: HR i -3..7, j -5..6, 512 m):
x -2816..2816, y -3840..2304. Maapeitelaatat ovat 256 m (puolet HR-laatasta), samassa ruudukossa: x0 = -1280 + 256 i, y0 = -1280 + 256 j.
"""
import base64, json, os, re
import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
LON0, LAT0, KX, KY = 21.796, 61.486, 53278.0, 111437.0
X0, Y0 = -1280.0, -1280.0          # sama origo kuin ot/ot_i_j.jpg
T = 256.0                          # maapeitelaatan koko (m)
PPM = 2                            # pikseliä metrille (0,5 m)
N = int(T * PPM)                   # 512 px
AREA = (-2816.0, -3840.0, 2816.0, 2304.0)
I0, I1 = int((AREA[0] - X0) // T), int((AREA[2] - X0) // T) - 1        # -6..15
J0, J1 = int((AREA[1] - Y0) // T), int((AREA[3] - Y0) // T) - 1        # -10..13


def game_xy(lon, lat):
    return (lon - LON0) * KX, (lat - LAT0) * KY


def tile_box(i, j):
    x0, y0 = X0 + T * i, Y0 + T * j
    return x0, y0, x0 + T, y0 + T


def to_px(pts, i, j):
    """pelin (x, y) -> laatan pikselit (sarake, rivi); rivi 0 = pohjoisreuna."""
    x0, y0, _, y1 = tile_box(i, j)
    a = np.asarray(pts, float).reshape(-1, 2)
    return [((x - x0) * PPM, (y1 - y) * PPM) for x, y in a]


def load_js_default(path):
    """export default {...}; -> dict (city.js, roads.js, river.js). Ensimmäinen JSON-olio."""
    s = open(path, encoding='utf-8').read()
    i = s.index('{')
    d, _ = json.JSONDecoder().raw_decode(s[i:])
    return d


def dec_i16(b64):
    """roads.js: base64 Int16 -> numpy (arvot /10 = metrit)."""
    return np.frombuffer(base64.b64decode(b64), dtype='<i2').astype(np.float32) / 10.0


def bbox_of(pts):
    a = np.asarray(pts, float).reshape(-1, 2)
    return a[:, 0].min(), a[:, 1].min(), a[:, 0].max(), a[:, 1].max()


def hits(bb, box, pad=0.0):
    return not (bb[2] < box[0] - pad or bb[0] > box[2] + pad or bb[3] < box[1] - pad or bb[1] > box[3] + pad)


def num(v, default=None):
    try:
        return float(re.sub(r'[^0-9.]', '', str(v).split(';')[0].replace(',', '.')))
    except Exception:
        return default
