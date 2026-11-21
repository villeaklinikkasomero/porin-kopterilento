#!/usr/bin/env python3
"""Kokoaa index.html:n src/-kansion paloista (järjestys src/osat.txt).

  python tools/osat/kokoa.py              kokoa ja kirjoita index.html
  python tools/osat/kokoa.py --tarkista   vain tarkista, että index.html vastaa paloja (exit 1 jos ei)
  python tools/osat/kokoa.py --pakota     kirjoita vaikka index.html:ää olisi muokattu suoraan (muutokset katoavat!)

Jos index.html:ää on muokattu suoraan (esim. tools/rata/patch_index.py), aja ensin tools/osat/pilko.py.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from osat_yhteinen import INDEX, SRC, lue_osat, lue, kirjoita, kokoa_teksti, pilko_teksti

osat = lue_osat()
uusi = kokoa_teksti(osat)
vanha = lue(INDEX) if os.path.exists(INDEX) else ''

if uusi == vanha:
    print(f'index.html on ajan tasalla ({len(osat)} palaa, {len(uusi.encode())} tavua)')
    sys.exit(0)

# mitkä palat eroavat
palat, virheet = pilko_teksti(vanha, osat) if vanha else ({}, [])
erot = [p for _, p in osat if palat.get(p) is not None and palat[p] != lue(os.path.join(SRC, p))]

if '--tarkista' in sys.argv:
    print('index.html EI vastaa src/-paloja.')
    for v in virheet: print('  ' + v)
    for p in erot: print('  eroaa: src/' + p)
    print('Muokkasitko paloja? → python tools/osat/kokoa.py   Muokkasitko index.html:ää suoraan? → python tools/osat/pilko.py')
    sys.exit(1)

# suoja: index.html on uudempi kuin yksikään eroava pala → joku muokkasi sitä suoraan
if vanha and '--pakota' not in sys.argv and not virheet:
    t_index = os.path.getmtime(INDEX)
    suoraan = [p for p in erot if os.path.getmtime(os.path.join(SRC, p)) < t_index]
    if suoraan:
        print('SEIS: index.html on muuttunut näissä kohdissa palan muokkauksen jälkeen (joku muokkasi index.html:ää suoraan):')
        for p in suoraan: print('  src/' + p)
        print('Aja ensin: python tools/osat/pilko.py   (tai --pakota, jos index.html:n muutokset saa hävittää)')
        sys.exit(2)

kirjoita(INDEX, uusi)
print(f'index.html kirjoitettu ({len(osat)} palaa, {len(uusi.encode())} tavua); muuttuneet palat: ' + (', '.join(erot) or 'rakenne'))
