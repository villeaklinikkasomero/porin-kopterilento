"""Vaiheen 0 testipisteet (30 kpl, 20 keskustassa), 21.11.2026 -> tools/maa/pisteet.json (lukee tools/maa/kuvat.mjs).

    python tools/maa/pisteet.py

Katupisteet lasketaan OSM-keskiviivasta (tools/maa/osm_maa.json): lähin kohta annettuun arvioon, katse kadun suuntaan, sijainti jalkakäytävällä
(puoli leveyttä + 1,5 m sivuun). Paikkapisteet annetaan suoraan (x, y, katse). Katse: asteina, 0 = pohjoinen, 90 = itä.
Muokkaa listaa PISTEET ja aja uudelleen; kuvat.mjs siirtää pisteen tarvittaessa ulos rakennuksesta (spiraalihaku 20 m).
"""
import json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from yhteiset import REPO

# (tunniste, nimi, alue, ('katu', kadun nimi, arvio x, arvio y, sivu ±1) | ('paikka', x, y, katse))
PISTEET = [
    ('k01', 'Kauppatori', 'keskusta', ('paikka', 64, 65, 120)),
    ('k02', 'Yrjönkatu kävelykatu', 'keskusta', ('katu', 'Yrjönkatu', 60, -60, 0)),
    ('k03', 'Antinkatu', 'keskusta', ('katu', 'Antinkatu', -40, -150, 1)),
    ('k04', 'Eteläranta', 'keskusta', ('katu', 'Eteläranta', -60, 470, -1)),
    ('k05', 'Itäpuisto', 'keskusta', ('katu', 'Itäpuisto', 60, -50, 1)),
    ('k06', 'Länsipuisto', 'keskusta', ('paikka', -414, 31, 80)),
    ('k07', 'Kauppahallin edusta', 'keskusta', ('paikka', 40, 20, 200)),
    ('k08', 'Isosilta (sillan pää)', 'keskusta', ('paikka', 229, 520, 10)),
    ('k09', 'Satakunnankatu', 'keskusta', ('katu', 'Satakunnankatu', 300, -350, 1)),
    ('k10', 'Itsenäisyydenkatu', 'keskusta', ('katu', 'Itsenäisyydenkatu', 100, -480, -1)),
    ('k11', 'Valtakatu', 'keskusta', ('katu', 'Valtakatu', -100, 270, 1)),
    ('k12', 'Pysäköintialue (Raatihuoneen taus)', 'keskusta', ('paikka', -60, 420, 270)),
    ('k13', 'Porin teatterin edusta', 'keskusta', ('paikka', -201, 360, 0)),
    ('k14', 'Raatihuoneenpuisto', 'keskusta', ('paikka', -137, 309, 90)),
    ('k15', 'Kirjurinluodon silta (Taavi-silta, etelä)', 'keskusta', ('paikka', -149, 515, 350)),
    ('k16', 'Hallituskatu', 'keskusta', ('katu', 'Hallituskatu', -250, 300, 1)),
    ('k17', 'Isolinnankatu', 'keskusta', ('katu', 'Isolinnankatu', 180, -100, -1)),
    ('k18', 'Pohjoisranta', 'keskusta', ('katu', 'Pohjoisranta', 100, 700, 1)),
    ('k19', 'Keskusaukio', 'keskusta', ('paikka', 29, -491, 0)),
    ('k20', 'Kirkkopuisto', 'keskusta', ('paikka', 296, 340, 0)),
    ('u01', 'Asema-aukio', 'asema', ('paikka', -443, -915, 180)),
    ('u02', 'Porttaali', 'asema', ('katu', 'Porttaali', -515, -1071, 1)),
    ('u03', 'Tiilimäki', 'ulko', ('paikka', -743, -1204, 90)),
    ('u04', 'Isomäentie', 'ulko', ('katu', 'Isomäentie', -1900, -1200, 1)),
    ('u05', 'Kirjurinluoto', 'ulko', ('paikka', -420, 1000, 270)),
    ('u06', 'Tapsan korjaamo, piha', 'ulko', ('paikka', -596.4, -420, 180)),
    ('u07', 'Lentoasemantie', 'ulko', ('katu', 'Lentoasemantie', 0, -1700, 1)),
    ('u08', 'Mäntyluodontie', 'ulko', ('katu', 'Mäntyluodontie', -2300, 0, 1)),
    ('u09', 'Koillisväylä', 'ulko', ('katu', 'Koillisväylä', 2100, 200, 1)),
    ('u10', 'Linnansilta (eteläpää)', 'ulko', ('paikka', 395, 520, 0)),
]
LEV = {'trunk': 9, 'primary': 9, 'secondary': 8, 'tertiary': 7, 'residential': 6, 'unclassified': 5.5, 'service': 4, 'pedestrian': 4, 'cycleway': 3}


def main():
    o = json.load(open(os.path.join(REPO, 'tools', 'maa', 'osm_maa.json'), encoding='utf-8'))
    out = []
    for tid, nimi, alue, m in PISTEET:
        if m[0] == 'paikka':
            out.append({'id': tid, 'nimi': nimi, 'alue': alue, 'x': m[1], 'y': m[2], 'katse': m[3]}); continue
        _, katu, ax, ay, side = m
        best = None
        for w in o['w']:
            t = w.get('t') or {}
            if t.get('name') != katu or t.get('bridge') not in (None, 'no'): continue
            g = np.asarray(w['g'], float).reshape(-1, 2)
            for k in range(len(g) - 1):
                a, b = g[k], g[k + 1]; d = b - a; L2 = max((d * d).sum(), 1e-6)
                u = np.clip(((np.array([ax, ay]) - a) * d).sum() / L2, 0, 1); p = a + d * u
                e = math.hypot(p[0] - ax, p[1] - ay)
                if best is None or e < best[0]: best = (e, p, d, LEV.get(t.get('highway'), 6))
        if best is None: print('ei löydy', katu); continue
        _, p, d, wd = best
        n = np.array([-d[1], d[0]]) / max(math.hypot(*d), 1e-6)
        q = p + n * side * (wd / 2 + 1.5)
        hd = math.degrees(math.atan2(d[0], d[1])) % 360
        out.append({'id': tid, 'nimi': nimi, 'alue': alue, 'x': round(float(q[0]), 1), 'y': round(float(q[1]), 1), 'katse': round(hd, 1)})
    f = os.path.join(REPO, 'tools', 'maa', 'pisteet.json')
    json.dump(out, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f, len(out), 'pistettä')


if __name__ == '__main__':
    main()
