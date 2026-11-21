"""Maasta nousevien esineiden sijainnit, 21.11.2026 (MAAN_PINTA_SUUNNITELMA.md, osat C ja D).

    python tools/maa/esineet.py            # -> maa/esineet.json (+ tilastot)

Lähteet: tools/maa/osm_maa.json (© OpenStreetMap contributors, ODbL) ja säännöt:
 - OSM-pisteet: penkit, roska-astiat, pyörätelineet, pollarit, portit, puomit, lipputangot, katulamput, pysäkit, liikennevalot, suojatiet,
   hidasteet, sähköpylväät, muuntajat, piknikpöydät, taideteokset, postilaatikot, latauspisteet, kierrätys, kioskit ym.
 - OSM-viivat: aidat (fence/wall/retaining_wall/rope), pensasaidat (hedge), puurivit, ojat.
 - Säännöt (lähde 'saanto'): sadevesikaivot ajoradan reunaan 30-40 m välein vuorotellen puolelta toiselle, kaivonkannet ajoradan keskelle
   55-70 m välein, venttiilikannet jalkakäytävän reunaan. Sijainti on likimääräinen (OSM-keskiviiva + puolet leveydestä); peli tarkentaa
   reunakivelle (ROAD.paveAt / groundTop).

Muoto (kaikki pelin metreinä, kulma radiaaneina x-akselista vastapäivään):
 { "versio": 1, "lahde": "...", "pisteet": { tyyppi: [x, y, kulma, x, y, kulma, ...] }, "viivat": { tyyppi: [[x, y, x, y, ...], ...] },
   "lisa": { tyyppi: [{"i": indeksi, ...tagit}] } }
Puut (natural=tree) ovat jo pelissä trees.js:ssä, joten ne tallennetaan vain tyyppiin 'puu_osm' vertailua varten (juurikaivot, lehtikarike).
"""
import json, math, os, random, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from yhteiset import REPO, AREA, num

PISTE = [  # (avain, arvo, tyyppi)
    ('amenity', 'bench', 'penkki'), ('leisure', 'picnic_table', 'piknikpoyta'), ('amenity', 'waste_basket', 'roska'),
    ('amenity', 'waste_disposal', 'jateastia'), ('amenity', 'recycling', 'kierratys'), ('amenity', 'bicycle_parking', 'pyorateline'),
    ('barrier', 'bollard', 'pollari'), ('barrier', 'block', 'betoniporsas'), ('barrier', 'gate', 'portti'), ('barrier', 'swing_gate', 'puomi'),
    ('barrier', 'lift_gate', 'puomi'), ('barrier', 'sliding_gate', 'portti'), ('man_made', 'flagpole', 'lipputanko'),
    ('highway', 'street_lamp', 'katulamppu'), ('highway', 'bus_stop', 'pysakki'), ('highway', 'traffic_signals', 'liikennevalo'),
    ('highway', 'crossing', 'suojatie'), ('highway', 'give_way', 'vaistamis'), ('highway', 'speed_camera', 'nopeuskamera'),
    ('traffic_calming', 'table', 'korotettu'), ('traffic_calming', 'bump', 'toyssy'), ('power', 'pole', 'sahkopylvas'),
    ('power', 'tower', 'voimalinjamasto'), ('power', 'transformer', 'muuntaja'), ('man_made', 'street_cabinet', 'sahkokaappi'),
    ('emergency', 'fire_hydrant', 'palopostti'), ('tourism', 'artwork', 'taideteos'), ('tourism', 'information', 'opaste'),
    ('amenity', 'post_box', 'postilaatikko'), ('amenity', 'charging_station', 'latauspiste'), ('amenity', 'vending_machine', 'automaatti'),
    ('amenity', 'parcel_locker', 'pakettiautomaatti'), ('amenity', 'atm', 'pankkiautomaatti'), ('amenity', 'toilets', 'wc'),
    ('amenity', 'drinking_water', 'juomapiste'), ('amenity', 'fountain', 'suihkulahde'), ('man_made', 'carpet_hanger', 'mattoteline'),
    ('leisure', 'fitness_station', 'kuntoilulaite'), ('man_made', 'mast', 'masto'), ('amenity', 'shelter', 'katos'),
    ('advertising', '*', 'mainos'), ('natural', 'tree', 'puu_osm'), ('natural', 'stone', 'kivi'),
]
VIIVA = [('barrier', 'fence', 'aita'), ('barrier', 'wall', 'muuri'), ('barrier', 'retaining_wall', 'tukimuuri'), ('barrier', 'rope', 'koysi'),
         ('barrier', 'hedge', 'pensasaita'), ('natural', 'tree_row', 'puurivi'), ('barrier', 'guard_rail', 'kaide'), ('barrier', 'kerb', 'reunakivi'),
         ('waterway', 'ditch', 'oja'), ('waterway', 'drain', 'oja')]
AJO = {'trunk': 9, 'primary': 9, 'secondary': 8, 'tertiary': 7, 'residential': 6, 'unclassified': 5.5, 'living_street': 5, 'service': 4,
       'trunk_link': 6, 'primary_link': 6, 'secondary_link': 6, 'tertiary_link': 6}


def sisalla(x, y):
    return AREA[0] <= x <= AREA[2] and AREA[1] <= y <= AREA[3]


def tyyppi(t, taulu):
    for k, v, ty in taulu:
        if k in t and (v == '*' or t[k] == v): return ty
    return None


def main():
    o = json.load(open(os.path.join(REPO, 'tools', 'maa', 'osm_maa.json'), encoding='utf-8'))
    P, V, X = {}, {}, {}
    wnodes = {}
    for n in o['n']:
        ty = tyyppi(n['t'], PISTE)
        if not ty or not sisalla(n['x'], n['y']): continue
        k = float(num(n['t'].get('direction'), 0) or 0)
        P.setdefault(ty, []).extend([n['x'], n['y'], round(math.radians(90 - k), 3) if 'direction' in n['t'] else 0])
        extra = {kk: n['t'][kk] for kk in ('species', 'genus', 'leaf_type', 'crossing', 'shelter', 'bench', 'name', 'height', 'support', 'material') if kk in n['t']}
        if extra: X.setdefault(ty, []).append(dict(i=len(P[ty]) // 3 - 1, **extra))
    # suojatien suunta: lähimmän tien suunta
    rnd = random.Random(1)
    kaivo, kansi = [], []
    for w in o['w']:
        t = w.get('t') or {}
        g = np.asarray(w['g'], float).reshape(-1, 2)
        ty = tyyppi(t, VIIVA)
        if ty:
            V.setdefault(ty, []).append([round(float(v), 1) for v in g.ravel()])
            continue
        if t.get('highway') in AJO and t.get('tunnel') is None and t.get('bridge') in (None, 'no'):
            wd = num(t.get('width'), None) or max(AJO[t['highway']], 3.3 * (num(t.get('lanes'), 0) or 0))
            d = np.hypot(*np.diff(g, axis=0).T); L = d.sum()
            if L < 15: continue
            s = np.concatenate([[0], np.cumsum(d)])
            def at(u):
                k = min(np.searchsorted(s, u) - 1, len(d) - 1); k = max(k, 0)
                f = (u - s[k]) / max(d[k], 1e-6); p = g[k] + (g[k + 1] - g[k]) * f
                a = math.atan2(*(g[k + 1] - g[k])[::-1]); return p, a
            u, side = rnd.uniform(5, 20), 1
            while u < L - 3:
                p, a = at(u); off = wd / 2 - 0.35
                q = p + side * off * np.array([-math.sin(a), math.cos(a)])
                if sisalla(*q): kaivo += [round(q[0], 1), round(q[1], 1), round(a, 3)]
                side = -side; u += rnd.uniform(30, 40)
            u = rnd.uniform(10, 40)
            while u < L - 3 and t['highway'] != 'service':
                p, a = at(u)
                q = p + rnd.uniform(-0.25, 0.25) * wd * np.array([-math.sin(a), math.cos(a)])
                if sisalla(*q): kansi += [round(q[0], 1), round(q[1], 1), round(rnd.uniform(0, 6.283), 3)]
                u += rnd.uniform(55, 70)
    P['sadevesikaivo'] = kaivo; P['kaivonkansi'] = kansi
    for ty in P: P[ty] = [round(v, 3) if isinstance(v, float) else v for v in P[ty]]
    out = {'versio': 1, 'lahde': 'OSM © OpenStreetMap contributors (ODbL), tools/maa/osm_maa.json; sadevesikaivo ja kaivonkansi sääntö (tools/maa/esineet.py)',
           'saanto': ['sadevesikaivo', 'kaivonkansi'], 'pisteet': P, 'viivat': V, 'lisa': X}
    os.makedirs(os.path.join(REPO, 'maa'), exist_ok=True)
    f = os.path.join(REPO, 'maa', 'esineet.json')
    json.dump(out, open(f, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(f, os.path.getsize(f) // 1024, 'kt')
    for ty, a in sorted(P.items(), key=lambda e: -len(e[1])): print(f'  {ty:18s} {len(a) // 3}')
    for ty, a in sorted(V.items(), key=lambda e: -len(e[1])): print(f'  {ty:18s} {len(a)} viivaa, {sum(np.hypot(*np.diff(np.asarray(l).reshape(-1, 2), axis=0).T).sum() for l in a):.0f} m')


if __name__ == '__main__':
    main()
