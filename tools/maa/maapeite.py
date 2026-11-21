"""Maankäyttökartta (land cover) koko aktiiviselle pelialueelle, 21.11.2026 (MAAN_PINTA_SUUNNITELMA.md, osa A).

    python tools/maa/maapeite.py                  # kaikki laatat -> maa/peite/peite_i_j.png + maa/peite/peite.json + tools/maa/out/yleis.png
    python tools/maa/maapeite.py --laatta 5 6     # yksi laatta (testi)
    python tools/maa/maapeite.py --yleis 4        # yleiskuvan tarkkuus (m/px), oletus 4

Tulos: 0,5 m:n luokkarasteri 512 m:n laatoissa (1024 x 1024, palettikuva, pikselin arvo = luokka, ks. LUOKAT). Rivi 0 = pohjoisreuna,
sarake 0 = länsireuna. Laatta peite_I_J kattaa x0 = -1280 + 512 I, y0 = -1280 + 512 J, I -3..7, J -5..6 = täsmälleen ot/ot_I_J.jpg.
Sisäisesti lasketaan 256 m:n osina (--laatta i j tekee yhden osan testiksi: maa/peite/testi_i_j.png).

Lähteet painojärjestyksessä (myöhempi peittää aiemman):
 1. ilmakuva ot/ot_i_j.jpg: vihreys -> nurmi, hiekanvärinen -> sora, muu -> piha (vain siellä, missä mikään muu ei kerro)
 2. OSM-alueet (tools/maa/osm_maa.json): landuse/natural/leisure (nurmi, niitty, metsä, istutus, leikkikenttä, kentät), vesi, pysäköinti, aukiot
 3. OSM-tiet viivoina leveyden mukaan (highway + surface) - EI ydinkeskustassa, jossa roads.js on tarkempi (maski 20 m roads.js-kolmioista)
 4. river.js-vesi, roads.js-pinnat (lawn, path, pave, kivi, medg, medp, asph), rata (OSM railway=rail)
 5. rakennusten pohjat city.js (+0,5 m)
 6. käsikorjaukset tools/maa/korjaukset.json
OSM-data: © OpenStreetMap contributors, ODbL (tekijätiedot peliin).
"""
import argparse, json, os, sys, time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(__file__))
from yhteiset import *

# luokka: (nimi, esikatseluväri)
LUOKAT = [
    ('ilmakuva', (255, 0, 255)),       # 0 ei tietoa (ei pitäisi jäädä)
    ('ajorata', (60, 60, 64)),         # 1 asfaltti, ajoneuvot
    ('jalkakaytava', (150, 150, 155)), # 2 asfaltti/betoni, kevyt liikenne, pihat
    ('kiveys', (175, 120, 95)),        # 3 noppakivi, betonilaatta, torit
    ('pysakointi', (95, 95, 120)),     # 4 asfaltoitu pysäköintialue
    ('nurmi', (90, 170, 70)),          # 5 leikattu nurmi
    ('sora', (200, 180, 140)),         # 6 sora, kivituhka, hiekkatie
    ('hiekka', (235, 215, 160)),       # 7 hiekka (leikkikentät, rannat)
    ('multa', (110, 80, 50)),          # 8 istutukset, kukkapenkit, pensasaidat
    ('metsa', (40, 95, 45)),           # 9 metsänpohja
    ('niitty', (160, 190, 90)),        # 10 pitkä heinä, pellot, joutomaa
    ('rakennus', (200, 60, 60)),       # 11 rakennuksen juuri
    ('vesi', (60, 110, 200)),          # 12 vesi
    ('rata', (120, 100, 90)),          # 13 sepeli
    ('urheilu', (200, 90, 40)),        # 14 tekonurmi / tartan / kenttä
    ('puu', (150, 110, 70)),           # 15 laiturit, puukannet
]
L = {n: k for k, (n, _) in enumerate(LUOKAT)}

PINTA = {'asphalt': None, 'paved': None, 'concrete': 'jalkakaytava', 'concrete:plates': 'kiveys', 'paving_stones': 'kiveys', 'sett': 'kiveys',
         'cobblestone': 'kiveys', 'unhewn_cobblestone': 'kiveys', 'stone': 'kiveys', 'bricks': 'kiveys', 'gravel': 'sora', 'fine_gravel': 'sora',
         'compacted': 'sora', 'unpaved': 'sora', 'ground': 'sora', 'dirt': 'sora', 'earth': 'sora', 'pebblestone': 'sora', 'sand': 'hiekka',
         'grass': 'nurmi', 'grass_paver': 'nurmi', 'wood': 'puu', 'artificial_turf': 'urheilu', 'tartan': 'urheilu', 'clay': 'urheilu',
         'woodchips': 'multa', 'rock': 'sora'}

# tien leveys (m) ja oletusluokka
TIE = {'motorway': (14, 'ajorata'), 'trunk': (9, 'ajorata'), 'primary': (9, 'ajorata'), 'secondary': (8, 'ajorata'), 'tertiary': (7, 'ajorata'),
       'motorway_link': (6, 'ajorata'), 'trunk_link': (6, 'ajorata'), 'primary_link': (6, 'ajorata'), 'secondary_link': (6, 'ajorata'),
       'tertiary_link': (6, 'ajorata'), 'residential': (6, 'ajorata'), 'unclassified': (5.5, 'ajorata'), 'living_street': (5, 'ajorata'),
       'service': (4, 'ajorata'), 'road': (5, 'ajorata'), 'busway': (7, 'ajorata'), 'track': (3, 'sora'), 'bridleway': (2.5, 'sora'),
       'cycleway': (3, 'jalkakaytava'), 'footway': (2.2, 'jalkakaytava'), 'pedestrian': (4, 'kiveys'), 'path': (1.4, 'sora'),
       'steps': (2.5, 'kiveys'), 'platform': (3, 'kiveys')}
ALUE = [  # (avain, arvo, luokka) - järjestyksessä: myöhempi peittää
    ('landuse', 'farmland', 'niitty'), ('landuse', 'meadow', 'niitty'), ('natural', 'grassland', 'niitty'), ('landuse', 'brownfield', 'niitty'),
    ('landuse', 'greenfield', 'niitty'), ('natural', 'heath', 'niitty'), ('natural', 'wetland', 'niitty'), ('landuse', 'farmyard', 'sora'),
    ('landuse', 'forest', 'metsa'), ('natural', 'wood', 'metsa'), ('natural', 'scrub', 'metsa'),
    ('leisure', 'park', 'nurmi'), ('landuse', 'grass', 'nurmi'), ('landuse', 'cemetery', 'nurmi'), ('landuse', 'village_green', 'nurmi'),
    ('landuse', 'recreation_ground', 'nurmi'), ('leisure', 'garden', 'nurmi'), ('leisure', 'dog_park', 'sora'),
    ('landuse', 'allotments', 'multa'), ('landuse', 'plant_nursery', 'multa'), ('landuse', 'flowerbed', 'multa'), ('man_made', 'planter', 'multa'),
    ('leisure', 'pitch', 'sora'), ('leisure', 'track', 'urheilu'), ('leisure', 'playground', 'hiekka'), ('natural', 'sand', 'hiekka'),
    ('natural', 'beach', 'hiekka'), ('leisure', 'miniature_golf', 'urheilu'), ('leisure', 'fitness_station', 'sora'),
    ('amenity', 'parking', 'pysakointi'), ('amenity', 'parking_space', 'pysakointi'), ('landuse', 'garages', 'jalkakaytava'),
    ('amenity', 'fuel', 'ajorata'), ('place', 'square', 'kiveys'), ('highway', 'pedestrian', 'kiveys'), ('area:highway', '*', 'jalkakaytava'),
    ('area:highway', 'traffic_island', 'nurmi'), ('man_made', 'pier', 'puu'), ('leisure', 'swimming_pool', 'vesi'),
    ('natural', 'water', 'vesi'), ('water', '*', 'vesi'), ('waterway', 'riverbank', 'vesi'),
]


def ring_join(ways):
    """liittää multipolygonin jäsenviivat renkaiksi päätepisteiden mukaan."""
    segs = [list(map(tuple, np.asarray(g).reshape(-1, 2))) for g in ways if len(g) >= 4]
    rings = []
    while segs:
        r = segs.pop(0)
        changed = True
        while changed and r[0] != r[-1]:
            changed = False
            for k, s in enumerate(segs):
                if s[0] == r[-1]: r += s[1:]
                elif s[-1] == r[-1]: r += s[::-1][1:]
                elif s[-1] == r[0]: r = s[:-1] + r
                elif s[0] == r[0]: r = s[::-1][:-1] + r
                else: continue
                segs.pop(k); changed = True; break
        if len(r) >= 3: rings.append(r)
    return rings


class Lahteet:
    def __init__(s):
        t0 = time.time()
        o = json.load(open(os.path.join(REPO, 'tools', 'maa', 'osm_maa.json'), encoding='utf-8'))
        W = {w['id']: w for w in o['w']}
        s.alueet, s.tiet, s.radat = [], [], []      # (bbox, luokka, järjestys, monikulmio/renkaat)
        jarj = {(k, v): n for n, (k, v, _) in enumerate(ALUE)}

        def alue_luokka(t):
            best = None
            for n, (k, v, c) in enumerate(ALUE):
                if k in t and (v == '*' or t[k] == v): best = (n, c)
            if best is None: return None
            n, c = best
            su = t.get('surface')
            if su in PINTA and PINTA[su] and c in ('pysakointi', 'kiveys', 'jalkakaytava', 'sora', 'urheilu', 'hiekka'): c = PINTA[su]
            if t.get('leisure') == 'pitch' and su in ('grass',): c = 'nurmi'
            return n, c
        for w in o['w']:
            t = w.get('t') or {}
            g = np.asarray(w['g'], float).reshape(-1, 2)
            closed = len(g) >= 4 and abs(g[0] - g[-1]).sum() < 0.05
            if t.get('tunnel') in ('yes', 'building_passage', 'culvert') or t.get('bridge') not in (None, 'no') or t.get('indoor') == 'yes':
                continue
            if 'highway' in t and t['highway'] in TIE and not (closed and t.get('area') == 'yes'):
                wd, c = TIE[t['highway']]
                if t.get('service') == 'parking_aisle': wd = 5
                if 'width' in t: wd = num(t['width'], wd) or wd
                elif 'lanes' in t and c == 'ajorata': wd = max(wd, 3.3 * (num(t['lanes'], 2) or 2))
                su = t.get('surface')
                if su in PINTA and PINTA[su]: c = PINTA[su]
                elif su in ('asphalt', 'paved') and c == 'sora': c = 'jalkakaytava'
                kevyt = t['highway'] in ('cycleway', 'footway', 'path', 'steps', 'pedestrian', 'track', 'bridleway', 'platform')
                s.tiet.append((bbox_of(g), L[c], wd, g, kevyt)); continue
            if t.get('railway') in ('rail', 'light_rail', 'disused') and not closed:
                s.radat.append((bbox_of(g), L['rata'], 4.4 if t['railway'] != 'disused' else 3.0, g, False)); continue
            if t.get('railway') == 'platform' and closed:
                s.alueet.append((bbox_of(g), L['kiveys'], 90, [g])); continue
            if closed:
                a = alue_luokka(t)
                if a: s.alueet.append((bbox_of(g), L[a[1]], a[0], [g]))
            elif t.get('barrier') == 'hedge' or t.get('natural') == 'tree_row':
                s.radat.append((bbox_of(g), L['multa'], 1.6, g, True))
            elif t.get('waterway') in ('ditch', 'drain', 'stream'):
                s.radat.append((bbox_of(g), L['niitty'], 2.0, g, True))
        for r in o['r']:
            a = alue_luokka(r['t'])
            if not a: continue
            outer = [W[m]['g'] for m, role in r['m'] if m in W and role in ('outer', '')]
            inner = [W[m]['g'] for m, role in r['m'] if m in W and role == 'inner']
            ro, ri = ring_join(outer), ring_join(inner)
            if ro: s.alueet.append((bbox_of([p for q in ro for p in q]), L[a[1]], a[0], [np.asarray(q) for q in ro], [np.asarray(q) for q in ri]))
        s.alueet.sort(key=lambda e: e[2])
        # river.js
        rv = load_js_default(os.path.join(REPO, 'river.js'))
        s.vesi = np.asarray(rv['water'], float).reshape(-1, 3, 2)
        s.vesi_bb = np.stack([s.vesi[:, :, 0].min(1), s.vesi[:, :, 1].min(1), s.vesi[:, :, 0].max(1), s.vesi[:, :, 1].max(1)], 1)
        # roads.js
        rd = load_js_default(os.path.join(REPO, 'roads.js'))
        s.ydin = []
        for key, c in (('lawn', 'nurmi'), ('medg', 'nurmi'), ('path', 'sora'), ('pave', 'jalkakaytava'), ('medp', 'jalkakaytava'),
                       ('kivi', 'kiveys'), ('asph', 'ajorata')):
            if key not in rd: continue
            tr = dec_i16(rd[key]).reshape(-1, 3, 2)
            bb = np.stack([tr[:, :, 0].min(1), tr[:, :, 1].min(1), tr[:, :, 0].max(1), tr[:, :, 1].max(1)], 1)
            s.ydin.append((L[c], tr, bb, key))
        # rakennukset
        cj = load_js_default(os.path.join(REPO, 'city.js'))
        s.talot = []
        for b in cj['b']:
            p = np.asarray(b['p'], float).reshape(-1, 2) / 10.0          # city.js: desimetrejä (040_rakennukset.js)
            if len(p) >= 3: s.talot.append((bbox_of(p), p))
        kp = os.path.join(REPO, 'tools', 'maa', 'korjaukset.json')
        s.korj = json.load(open(kp, encoding='utf-8')).get('alueet', []) if os.path.exists(kp) else []
        print(f'lähteet: {len(s.alueet)} aluetta, {len(s.tiet)} tietä, {len(s.radat)} viivaa, {len(s.talot)} taloa, {len(s.korj)} korjausta ({time.time() - t0:.1f} s)')


def _outer():
    if not hasattr(_outer, 'im'):
        f = os.path.join(REPO, 'outer.jpg')
        _outer.im = Image.open(f).convert('RGB') if os.path.exists(f) else None
        _outer.c = load_js_default(os.path.join(REPO, 'city.js'))
    return _outer.im


def ortoluokat(i, j):
    """ilmakuvan luokittelu (vain pohjaksi)."""
    oi, oj = int((i * T) // 512), int((j * T) // 512)    # ot-laatta, joka sisältää tämän
    f = os.path.join(REPO, 'ot', f'ot_{oi}_{oj}.jpg')
    x0, y0, x1, y1 = tile_box(i, j)
    if os.path.exists(f):
        im = Image.open(f).convert('RGB')
        sx = sy = im.size[0] / 512.0                        # px/m
        ox0, oy1 = X0 + 512 * oi, Y0 + 512 * (oj + 1)
    else:                                                   # ulkokehä: outer.jpg (~1,2 m/px), rajat city.js ox0..oy1 (030_maa_ilmakuva.js ouv)
        im = _outer()
        if im is None: return None
        c = _outer.c; sx, sy = im.size[0] / (c['ox1'] - c['ox0']), im.size[1] / (c['oy1'] - c['oy0'])
        ox0, oy1 = c['ox0'], c['oy1']
        if x0 < ox0 or x1 > c['ox1'] or y0 < c['oy0'] or y1 > oy1: return None
    box = ((x0 - ox0) * sx, (oy1 - y1) * sy, (x1 - ox0) * sx, (oy1 - y0) * sy)
    a = np.asarray(im.crop(tuple(int(round(v)) for v in box)).resize((N, N), Image.BILINEAR).filter(ImageFilter.BoxBlur(2)), np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    lum = 0.3 * r + 0.59 * g + 0.11 * b
    exg = 2 * g - r - b
    out = np.full((N, N), L['jalkakaytava'], np.uint8)
    hiekka = (r > g) & (g > b + 8) & (r - b > 25) & (lum > 120)
    out[hiekka] = L['sora']
    veg = (exg > 18) | ((g > r + 6) & (g > b + 4))
    out[veg] = L['nurmi']
    out[veg & (lum < 55)] = L['niitty']          # varjoinen/tumma kasvusto: latvukset, pensaikko
    out = np.asarray(Image.fromarray(out).filter(ImageFilter.ModeFilter(5)))
    return out


def poly(dr, pts, i, j, c):
    q = to_px(pts, i, j)
    if len(q) >= 3: dr.polygon(q, fill=int(c))


def viiva(dr, pts, i, j, c, wd):
    q = to_px(pts, i, j)
    w = max(1, int(round(wd * PPM)))
    dr.line(q, fill=int(c), width=w, joint='curve')
    r = w / 2
    for x, y in (q[0], q[-1]): dr.ellipse((x - r, y - r, x + r, y + r), fill=int(c))


def laatta(S, i, j):
    box = tile_box(i, j)
    base = ortoluokat(i, j)
    im = Image.fromarray(base if base is not None else np.zeros((N, N), np.uint8), 'L')
    dr = ImageDraw.Draw(im)
    for e in S.alueet:
        if not hits(e[0], box): continue
        if len(e) > 4 and e[4]:                       # multipolygoni sisäreikineen: maski
            mk = Image.new('1', (N, N), 0); md = ImageDraw.Draw(mk)
            for r in e[3]: poly(md, r, i, j, 1)
            for r in e[4]: poly(md, r, i, j, 0)
            im.paste(int(e[1]), mask=mk)
        else:
            for r in e[3]: poly(dr, r, i, j, e[1])
    for k in np.nonzero(hits_arr(S.vesi_bb, box))[0]: poly(dr, S.vesi[k], i, j, L['vesi'])
    # roads.js-kattavuus: OSM-tiet vain sen ulkopuolella
    ym = Image.new('L', (N, N), 0); yd = ImageDraw.Draw(ym)
    for c, tr, bb, key in S.ydin:
        for k in np.nonzero(hits_arr(bb, box, 20))[0]: poly(yd, tr[k], i, j, 255)
    ymask = np.asarray(ym.filter(ImageFilter.MaxFilter(41))) > 0          # 20 m
    tl = Image.new('L', (N, N), 255); td = ImageDraw.Draw(tl)
    for kevyt in (True, False):
        for bb, c, wd, g, kv in S.tiet:
            if kv == kevyt and hits(bb, box, 10): viiva(td, g, i, j, c, wd)
    a = np.asarray(im).copy(); t = np.asarray(tl)
    m = (t != 255) & ~ymask
    a[m] = t[m]
    im = Image.fromarray(a, 'L'); dr = ImageDraw.Draw(im)
    for bb, c, wd, g, kv in S.radat:
        if hits(bb, box, 10): viiva(dr, g, i, j, c, wd)
    for c, tr, bb, key in S.ydin:
        for k in np.nonzero(hits_arr(bb, box))[0]: poly(dr, tr[k], i, j, c)
    tm = Image.new('L', (N, N), 0); tdr = ImageDraw.Draw(tm)
    for bb, p in S.talot:
        if hits(bb, box): poly(tdr, p, i, j, 255)
    a = np.asarray(im).copy()
    a[np.asarray(tm.filter(ImageFilter.MaxFilter(3))) > 0] = L['rakennus']
    im = Image.fromarray(a, 'L'); dr = ImageDraw.Draw(im)
    for k in S.korj:
        if k.get('luokka') in L and hits(bbox_of(k['p']), box): poly(dr, k['p'], i, j, L[k['luokka']])
    return np.asarray(im)


def hits_arr(bb, box, pad=0.0):
    return ~((bb[:, 2] < box[0] - pad) | (bb[:, 0] > box[2] + pad) | (bb[:, 3] < box[1] - pad) | (bb[:, 1] > box[3] + pad))


PALETTI = sum((list(c) for _, c in LUOKAT), []) + [0] * (768 - 3 * len(LUOKAT))


def tallenna(a, f):
    im = Image.fromarray(a, 'P'); im.putpalette(PALETTI); im.save(f, optimize=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--laatta', nargs=2, type=int)
    ap.add_argument('--yleis', type=float, default=4.0)
    ap.add_argument('--ulos', default=os.path.join(REPO, 'maa', 'peite'))
    A = ap.parse_args()
    os.makedirs(A.ulos, exist_ok=True); os.makedirs(os.path.join(REPO, 'tools', 'maa', 'out'), exist_ok=True)
    S = Lahteet()
    tiles = [tuple(A.laatta)] if A.laatta else [(i, j) for j in range(J0, J1 + 1) for i in range(I0, I1 + 1)]
    k = max(1, int(round(A.yleis * PPM)))
    yl = np.zeros(((J1 - J0 + 1) * N // k, (I1 - I0 + 1) * N // k), np.uint8)
    lask = np.zeros(len(LUOKAT), np.int64)
    t0 = time.time(); osat = {}
    for n, (i, j) in enumerate(tiles):
        a = laatta(S, i, j)
        if A.laatta: tallenna(a, os.path.join(A.ulos, f'testi_{i}_{j}.png'))
        else: osat[(i, j)] = a
        lask += np.bincount(a.ravel(), minlength=len(LUOKAT))[:len(LUOKAT)]
        r0, c0 = (J1 - j) * N // k, (i - I0) * N // k
        yl[r0:r0 + N // k, c0:c0 + N // k] = a[::k, ::k]
        if n % 25 == 0: print(f'{n + 1}/{len(tiles)} laatta {i},{j}  {time.time() - t0:.0f} s', flush=True)
    if not A.laatta:
        # tallennus 512 m laattoina (1024 px), samat indeksit kuin ot/ot_i_j.jpg: peite_I_J = 256 m laatat (2I..2I+1, 2J..2J+1)
        for I in range(I0 // 2, I1 // 2 + 1):
            for J in range(J0 // 2, J1 // 2 + 1):
                big = np.zeros((2 * N, 2 * N), np.uint8)
                for di in (0, 1):
                    for dj in (0, 1):
                        if (2 * I + di, 2 * J + dj) in osat: big[(1 - dj) * N:(2 - dj) * N, di * N:(di + 1) * N] = osat[(2 * I + di, 2 * J + dj)]
                tallenna(big, os.path.join(A.ulos, f'peite_{I}_{J}.png'))
        tallenna(yl, os.path.join(REPO, 'tools', 'maa', 'out', 'yleis.png'))
        meta = {'versio': 1, 'tehty': time.strftime('%Y-%m-%d'), 'laatta_m': 2 * T, 'px_per_m': PPM, 'koko_px': 2 * N, 'x0': X0, 'y0': Y0,
                'i': [I0 // 2, I1 // 2], 'j': [J0 // 2, J1 // 2], 'huom': 'sama ruudukko kuin ot/ot_i_j.jpg (033_ilmakuva_tarkka.js HR)', 'tiedosto': 'peite_{i}_{j}.png', 'rivi0': 'pohjoinen',
                'luokat': [{'k': k_, 'nimi': n_, 'vari': c_} for k_, (n_, c_) in enumerate(LUOKAT)],
                'osuus': {LUOKAT[k_][0]: round(float(v) / lask.sum(), 4) for k_, v in enumerate(lask)},
                'lahteet': 'OSM (© OpenStreetMap contributors, ODbL) tools/maa/osm_maa.json; roads.js; river.js; city.js; ot/ ilmakuva; tools/maa/korjaukset.json'}
        json.dump(meta, open(os.path.join(A.ulos, 'peite.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(json.dumps(meta['osuus'], ensure_ascii=False))
    print(f'valmis {len(tiles)} laattaa {time.time() - t0:.0f} s')
