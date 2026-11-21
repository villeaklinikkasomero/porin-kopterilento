#!/usr/bin/env python3
"""Päivittää src/-palat index.html:stä (kun index.html:ää on muokattu suoraan, esim. tools/rata/patch_index.py).

  python tools/osat/pilko.py            kirjoita muuttuneet palat
  python tools/osat/pilko.py --pakota   kirjoita vaikka pala olisi uudempi kuin index.html (palan omat muutokset katoavat!)

Palojen rajat luetaan index.html:n @osa-merkintäriveistä. Uuden palan lisäys: lisää rivi src/osat.txt:hen ja tiedosto, aja kokoa.py.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from osat_yhteinen import INDEX, SRC, lue_osat, lue, kirjoita, pilko_teksti

osat = lue_osat()
palat, virheet = pilko_teksti(lue(INDEX), osat)
if virheet:
    print('SEIS: index.html:n merkintärivit eivät vastaa src/osat.txt:tä:')
    for v in virheet: print('  ' + v)
    sys.exit(1)

t_index = os.path.getmtime(INDEX)
muuttui, estetty = [], []
for _, p in osat:
    polku = os.path.join(SRC, p)
    vanha = lue(polku) if os.path.exists(polku) else None
    if vanha == palat[p]:
        continue
    if vanha is not None and os.path.getmtime(polku) > t_index and '--pakota' not in sys.argv:
        estetty.append(p); continue
    kirjoita(polku, palat[p]); muuttui.append(p)

for p in muuttui: print('päivitetty: src/' + p)
if estetty:
    print('EI päivitetty – pala on uudempi kuin index.html (molempia muokattu?). Yhdistä käsin tai --pakota:')
    for p in estetty: print('  src/' + p)
    sys.exit(2)
print('palat ajan tasalla' if not muuttui else f'{len(muuttui)} palaa päivitetty')
