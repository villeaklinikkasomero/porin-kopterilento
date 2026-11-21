# Yhteiset apufunktiot: src/osat.txt ja @osa-merkinnät. Ks. src/README.md.
import os, re, sys

try:   # Windowsin konsoli: ääkköset eivät saa kaataa tulostusta
    sys.stdout.reconfigure(errors='replace')
except Exception:
    pass

JUURI = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(JUURI, 'src')
INDEX = os.path.join(JUURI, 'index.html')
# Merkintärivi jokaisen palan alussa (paitsi ensimmäisen: mitään ei saa olla ennen <!doctype html>:ää).
# Kommentin tyyli riippuu siitä, missä kohtaa sivua pala alkaa: CSS:n sisällä, JS:n sisällä vai HTML:ssä.
MUOTO = {'css': '/* @osa {} */', 'js': '// @osa {}', 'html': '<!-- @osa {} -->'}
MERKKI = re.compile(r'^(?:/\* @osa (\S+) \*/|// @osa (\S+)|<!-- @osa (\S+) -->)$')


def lue_osat():
    """src/osat.txt: rivi per pala järjestyksessä: <kommenttityyli> <polku src/:n alla>. Ensimmäisen palan tyyli on '-'."""
    osat = []
    with open(os.path.join(SRC, 'osat.txt'), encoding='utf-8') as f:
        for n, rivi in enumerate(f, 1):
            rivi = rivi.split('#', 1)[0].strip()
            if not rivi:
                continue
            tyyli, polku = rivi.split()
            if tyyli not in ('-', 'css', 'js', 'html'):
                sys.exit(f'src/osat.txt rivi {n}: tuntematon tyyli {tyyli}')
            osat.append((tyyli, polku))
    if not osat or osat[0][0] != '-':
        sys.exit('src/osat.txt: ensimmäisen palan tyylin pitää olla "-" (ei merkintää ennen <!doctype html>)')
    return osat


def lue(polku):
    with open(polku, 'rb') as f:   # CRLF → LF (Windowsin editori tai git autocrlf); index.html on aina LF
        return f.read().decode('utf-8').replace('\r\n', '\n')


def kirjoita(polku, teksti):
    os.makedirs(os.path.dirname(polku), exist_ok=True)
    with open(polku, 'wb') as f:
        f.write(teksti.encode('utf-8'))


def kokoa_teksti(osat):
    out = []
    for tyyli, polku in osat:
        sisalto = lue(os.path.join(SRC, polku))
        if sisalto and not sisalto.endswith('\n'):
            sisalto += '\n'
        if tyyli != '-':
            out.append(MUOTO[tyyli].format(polku) + '\n')
        out.append(sisalto)
    return ''.join(out)


def pilko_teksti(html, osat):
    """index.html → {polku: sisältö}. Palauttaa myös virhelistan."""
    rivit = html.splitlines(keepends=True)
    palat, nyk, puskuri, virheet = {}, osat[0][1], [], []
    for r in rivit:
        m = MERKKI.match(r.rstrip('\r\n'))
        if m:
            palat[nyk] = ''.join(puskuri)
            nyk, puskuri = next(g for g in m.groups() if g), []
        else:
            puskuri.append(r)
    palat[nyk] = ''.join(puskuri)
    tunnetut = [p for _, p in osat]
    for p in palat:
        if p not in tunnetut:
            virheet.append(f'index.html:ssä on pala {p}, jota ei ole src/osat.txt:ssä')
    for p in tunnetut:
        if p not in palat:
            virheet.append(f'src/osat.txt:n pala {p} puuttuu index.html:stä (merkintärivi poistettu?)')
    if [p for p in palat] != [p for p in tunnetut if p in palat]:
        virheet.append('palojen järjestys index.html:ssä ei vastaa src/osat.txt:tä')
    return palat, virheet
