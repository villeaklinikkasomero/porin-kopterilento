# Porin kopterilento – siirtomuistio seuraavalle Claudelle

Lue tämä ensin. Zipissä on koko peli ja kaikki skriptit; mitään muuta ei tarvita.

## Mikä tämä on
Three.js-peli (`index.html`), jossa lennetään kopterilla Porin yllä. Maa ja katot tulevat ilmakuvasta (`orto.jpg` ydin 0,545 m/px, `outer.jpg` ulkokehä),
rakennusten pohjat ja korkeudet `city.js`:stä (koordinaatit metreinä, x itään, y pohjoiseen, origo torin tuntumassa; three.js:ssä z = -y).
`bl_*.js` = Blenderissä tehty GLB base64-merkkijonona (`export const x, y, roof; export default "..."`), valo paistettu tekstuuriin.

## Tilanne
- Valmiina ennestään: maamerkit, Kivi-Porin korttelit `bl_kivi0..4` (näiden skriptit ovat kadonneet).
- Tässä keskustelussa tehty:
  1. Kauppatorin ympäryskorttelit `bl_tori0..5` (75 rakennusta). Julkisivut Satakunnan Museon inventoinnin kuvausten mukaan
     (Porin ruutukaavakeskusta, modernin rakennusperinnön inventointi 2019, satakunnanmuseo.pori.fi). Rakennusten kohdistus osoitteisiin on päättelyä, värit arvioita.
  2. Autot: `cars.js` (kolme Blender-mallia, vertex-värit) ja `parked.js` (n. 13 400 ilmakuvasta tunnistettua autoa: x*10, y*10, suunta*100, väri).
  3. BePOP tehty uudelleen (`bl_bepop.js`, maamerkki, `roof = false` eli ilmakuvakatto säilyy): sinertävät elementtijulkisivut, kaareva lasikatto,
     pyöreä torni ja sisäänkäyntikatos; sijainnit mitattu ilmakuvasta, kuvaus finnisharchitecture.fi/bepop. Keskustan uimahalli (`bl_uima.js`,
     kortteli 11 `KN`:ssä, rakennus 587): ulkoasu on arvattu ilmakuvasta (lasiseinät länteen ja etelään, vesiliukumäki koilliskulmassa) – pyydä käyttäjältä valokuva.
- Käyttäjän toiveet: talot muistuttamaan oikeita kohteita, tehdään Blenderissä. Seuraavaksi luontevaa: kävelykadun varsi etelään, muut ruutukaavakorttelit.

## Ympäristön pystytys (hiekkalaatikko)
Skripteissä on kovakoodattu polku `/home/claude`: pura peli kansioon `/home/claude/pori` ja kopioi `blender/*` kansioon `/home/claude`.
bpy 5.2.4 vaatii Python 3.13:n: `uv venv -p 3.13 bl313`. Pyörä on 400 Mt ja yksittäinen lataus on hidas ja katkeaa 5 min aikarajaan:
lataa rinnakkain `dl.sh`:llä (osoite `bpyurl.txt`), aja kunnes osien summa on 402908800 tavua, yhdistä `cat part0..15` ja asenna
`uv pip install -p bl313/bin/python ./bpy-5.2.4-cp313-cp313-manylinux_2_28_x86_64.whl pillow`.
Älä käytä `pkill -f` -komentoa kuviolla, joka esiintyy omassa komentorivissä (tappaa työkalukutsun).

## Putki
- `lib_city.py` lukee `city.js`:n. `B[i]` = rakennus, `poly(i)` = pohja (CCW) ja ala. Rakennusindeksi i on se, johon kaikki viittaa.
- `gen.py`: julkisivumoduulit (`m_punched`, `m_ribbon`, `m_raster`, `m_vraster`, `m_loggia`, `m_erker`, `m_shop`), katot (`flat`, `hip`, `gable`, `pent`),
  atlaspakkaus ja paisto. Jokaisesta seinästä mallinnetaan yksi ikkunajako tarkasti ja paistetaan (selected-to-active) litteälle laatalle, jota toistetaan;
  parvekkeet, erkkerit ja katot ovat oikeaa geometriaa. Aurinko kaakosta (118°, 38°) kuten ilmakuvan varjot. Katuruudukon kulma -13,035°.
- `zones.py`: `SPEC[i]` = yhden rakennuksen määrittely (värit, kerrosjako, seinät ilmansuunnittain `dirs={'S': ...}` ruudukon suhteen, katto);
  määrittelemättömät saavat `auto(i)`:n tyyppitalon. `ZONES` = korttelin rakennuslista.
- Ajo: `bl313/bin/python run.py tori0 16` (n. 2,5 min / kortteli, 1 CPU) → `out/bl_tori0.js`, kopioi peliin.
- Katselu: `bl313/bin/python view_glb.py -- out/tori0.glb kuva.jpg <atsimuutti> <korkeuskulma> <etäisyys>`.
- Pelitesti: `python3 shot.py` (Playwright + swiftshader, koukut `window.__game`, `window.__bl`, `window.__cars`).
- Autot: `detect_cars.py` (OpenCV, kirjoittaa `pori/parked.js`), `cars.py` (mallit → `pori/cars.js`).

## Kytkentä index.html:ssä
- `KN` = Blender-kortteleiden nimet, `ZB` = rakennusindeksi → korttelin numero (5 = tori0 ...), `ZROOF` = rakennukset, joilla on oma Blender-katto
  (ilmakuvakatto jätetään pois). Uusi kortteli: lisää nimi `KN`:ään, indeksit `ZB`:hen ja katolliset `ZROOF`:iin. Nämä luotiin `zones.py`:n tiedoista.
- Autot: liikennelohkon lopussa `loadModel('cars', ...)`.

## Tunnetut puutteet
- Tunnistamatta: torin itälaidan korkea talo (1599); Eteläkauppatori 2 (603) tehty arvaamalla.
- Yksinkertaistettu: Säästöpankin (163) pyöreä kulma, HOP:n (1726) kulmapylväät, Yrjönkympin (602) satulakatto on aumana.
- Autotunnistus: arviolta runsas puolet osuu oikean auton päälle; rivien suunta paikoin 90° väärin, vääriä osumia pihoilla ja varjojen reunoilla,
  vaaleat autot vaalealla soralla puuttuvat. Vain ydinalueen ilmakuvasta.
- Zipin pakkaus: `cd pori && zip -r ../Porin_kopterilento_claude.zip .`
