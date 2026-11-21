# tools/maa – maan pinnan työkalut (21.11.2026)

Suunnitelma: `tarvittavat_ominaisuudet/MAAN_PINTA_SUUNNITELMA.md` (tila: osa 9). **Pelissä 21.11.2026**: sävykorjattu ilmakuva `maa/ot_s/` ja
maan materiaalimoduuli `maa/maa.js` (kutsu `src/js/0337_maa.js`).

| Työkalu | Tekee | Tulos |
|---|---|---|
| `osm_maa.json` | OSM-raakadata koko pelialueelta (bbox 21.7431, 61.4515 – 21.8489, 61.5067), pelin metreinä | (lähde) |
| `maapeite.py` | 0,5 m luokkarasteri 512 m laatoissa (= ot-laatat) | `maa/peite/peite_i_j.png`, `maa/peite/peite.json`, `tools/maa/out/yleis.png` |
| `orto_savy.py` | ilmakuvan sävykorjaus ("lumi" pois), alkuperäiset ennallaan | `maa/ot_s/*.jpg`, `--vertailu i j` -> `out/savy_i_j.jpg` |
| `esineet.py` | maasta nousevien esineiden pisteet ja viivat (OSM + kaivosäännöt) | `maa/esineet.json` |
| `tekstuurit.py` | ambientCG-zipit (`tex/*.zip`, CC0) -> pelin PBR-tekstuurit | `maa/tex/<luokka>_{a,n,orm}[_m].jpg`, `maa/tex/tex.json` |
| `pisteet.py` | vaiheen 0 testipisteet (30, joista 20 keskustassa) | `tools/maa/pisteet.json` |
| `kuvat.mjs` | testikuvat jokaisesta pisteestä (silmät + maahan) | `tools/maa/kuvat/<tunniste>/`, `--koonti a b` -> vertailusivu |
| `korjaukset.json` | omistajan käsikorjaukset maapeitteeseen | luetaan `maapeite.py`:ssä viimeisenä |
| `yhteiset.py` | koordinaatit, laattaruudukko, js-datan luku | – |

Ajojärjestys (repon juuresta, Python 3 + numpy + Pillow; kuvat.mjs: Node + Playwright):
```
python tools/maa/maapeite.py          # ~5 min, 132 laattaa
python tools/maa/esineet.py
python tools/maa/tekstuurit.py        # tarvitsee tex/*.zip (ei repossa)
python tools/maa/orto_savy.py         # ~2 min, 108 + 2 kuvaa
python tools/maa/pisteet.py
node tools/maa/kuvat.mjs ennen http://localhost:8124/index.html
```

## Koordinaatit ja laatat
- Pelin metrit: x = (lon − 21,796) · 53278, y = (lat − 61,486) · 111437; three.js (x, z, −y).
- Maapeitelaatta `peite_I_J.png`: x0 = −1280 + 512 I, y0 = −1280 + 512 J, 512 m, 1024 × 1024 px (0,5 m), rivi 0 = pohjoisreuna,
  I = −3…7, J = −5…6 (132 laattaa, 3,9 Mt) = täsmälleen samat kuin `ot/ot_I_J.jpg` (033_ilmakuva_tarkka.js:n HR-lataus käy suoraan).
  Työkalu laskee sisäisesti 256 m:n osina (528 osaa); `--laatta i j` tekee yhden osan testiksi (`maa/peite/testi_i_j.png`).
- Pikselin arvo = luokka (palettikuva, esikatseluvärit). Shaderissa: `texelFetch` / NEAREST + oma 4 naapurin sekoitus (tai GPU:lle
  kanavapainot, kun luokkia on ≤ 4 per laatta – päätetään shaderia tehdessä).

## Luokat (maapeite.py LUOKAT)
0 ilmakuva (ei tietoa: vain alueen reunoilla, joissa ilmakuvaakaan ei ole) · 1 ajorata · 2 jalkakäytävä/piha · 3 kiveys · 4 pysäköinti · 5 nurmi ·
6 sora · 7 hiekka · 8 multa/istutus · 9 metsänpohja · 10 niitty/pitkä heinä · 11 rakennus · 12 vesi · 13 rata · 14 urheilu · 15 puu (laiturit)

Lähteiden järjestys ja säännöt: ks. `maapeite.py`:n alku. Ydinkeskustassa `roads.js` (pelin oma katugeometria) voittaa OSM-tiet (OSM-tiet
piirretään vain yli 20 m päähän roads.js-kolmioista), joten maapeite osuu pelin reunakiviin.

## Käsikorjaukset (`korjaukset.json`)
```json
{ "alueet": [ { "luokka": "nurmi", "p": [[x, y], [x, y], [x, y], ...], "huom": "omistaja 22.11.: tässä on nurmi" } ] }
```
Koordinaatit pelin metreinä (kehittäjätila Ctrl+Shift+D, Ctrl+Shift+K kopioi oman paikan). Aja `maapeite.py` uudelleen (tai `--laatta i j`).

## OSM-datan päivitys
Pilven verkko estää Overpassin; data haettiin sovelluksen sisäisellä selaimella `api.openstreetmap.org/api/0.6/map.json` -ruuduilla
(90 ruutua 0,012° × 0,006°, 3 rinnakkain, 400-vastauksella ruutu jaetaan neljään), tiivistettiin selaimessa (vain maan pinnan kannalta tarpeelliset
tagit, pisteet pelin metreinä 0,1 m:iin) ja siirrettiin gzip+base64-paloina (5 × 200 000 merkkiä). Sama skripti on SIIRTO-tiedostossa
(21.11.2026, maan pinta: valmistelu). Lisenssi: © OpenStreetMap contributors, ODbL – lähdemerkintä pelin tekijätietoihin, kun data on pelissä.

## Puuttuu / tiedossa
- **Tekstuurit puuttuvat 5 luokalta**: sora (ehd. ambientCG Gravel022), hiekka (Ground033), metsänpohja (Ground026), niitty (Grass001),
  puu (Planks021). Lataa 1K-JPG-zip `tex/`-kansioon ja aja `tekstuurit.py` (taulu `LAHTEET`). Rata käyttää jo `rata/sepeli_*`.
- OSM:ssä on vähän penkkejä (35) ja roska-astioita (19): puistoihin ja toreille tarvitaan sääntösijoitus (polkujen varret 40–60 m välein) pelin puolella.
- Sadevesikaivot ja kaivonkannet ovat sääntöjä OSM-keskiviivasta; peli siirtää ne reunakivelle (`ROAD.paveAt`).
- Ilmakuvaluokittelu on yksinkertainen (vihreys / hiekanväri / muu = piha): korjataan `korjaukset.json`:lla, missä vertailukuvat näyttävät väärää.
- `orto_savy.py`: samat ot-laatat ovat myös kattojen tekstuuri (033 `roofTile`), joten korjattujen käyttöönotto muuttaa kattojakin – tarkista kuvista.

## kuvat.mjs: kävelytila (21.11.2026)
Peli on yleensä kävelytilassa (`WALK.on`): pelaaja palautuu kävelijän paikkaan joka ruudulla ja 033 lataa tarkat laatat sen mukaan. kuvat.mjs siirtää nyt
kävelijän pisteeseen ja pitää sen siellä odotuksen ajan sekä piilottaa kävelijähahmon. Ilman tätä kaukaiset pisteet kuvautuivat karkealla ilmakuvalla.
Kuvat voi ottaa myös sovelluksen selaimessa omalla koneella (localhost:8000, `pelaa_paikallisesti.cmd`) – nopea oikealla näytönohjaimella.
