# Rataverkko – `rata/`

Lisätty 20.–21.11.2026 (omistaja: "rakennetaan pelikentälle oikeille paikoille junarata, niin autenttista kuin mahdollista").

- `rata.js`: koko kartan raiteet (56 raidetta, 26 km), ladataan index.html:n lopussa. Tekee:
  - **sepelin** (raidesepeli, saumaton 1,6 m ruutu `sepeli_a/n/orm.jpg`, luiska 1:1,5). Ratapihalla sepeli jatkuu tasaisena raiteiden väliin ja laiturin alle.
  - **B97-betonipölkyt** 0,61 m välein ja lähellä (< 70 m) **kiinnitykset**: välilevy, olakkeet ja e-jousileikkeet. Käytöstä poistetuilla raiteilla ja pistoraiteilla on puupölkyt ja aluslevyt.
  - **kiskot** 60E1-profiililla: kiiltävä kulkupinta, ruosteinen varsi. Vaihteissa on pitkät vaihdepölkyt ja kääntölaitteet.
  - **laiturit** 1 ja 2–3 OSM-monikulmioista. Raiteen puoleinen reuna on tasan 1,80 m raiteen keskeltä ja 550 mm kiskon yläpuolella. Mukana reunakivi, varoituslaatat ja turvaviiva.
  - **välilaiturin lasikatos**, **porraskatokset**, **alikulun portaali** asema-aukion puolella, **rautatiesillat**, **tasoristeysten kumilevyt**, **opastimet**, **puskimet** ja **ajojohdin** (pylväät ulokkeineen, ratapihalla portaalit, ajolanka siksakissa ja kantolanka riippuvana).
  - Etäisyystasot 200 m:n ruuduissa. Staattiset osat on yhdistetty materiaaleittain (`juna/yhdista.js`).
  - Poistaa raiteilta ilmakuvasta tunnistetut "pysäköidyt autot" (vaunuja) ja leivotusta korttelista `h084` laiturin LoD2-laatikot 2298 ja 2299.
  - `window.__laituriZ` ketjutetaan: kävelijä seisoo laiturin pinnalla.
- `rata_data.js` (generoitu, älä muokkaa käsin): raiteet 2 m välein (x, y, pölkyn yläpinnan korkeus), vaihteet, laiturit, opastimet, bottijunan reitit, maastokorjaukset `ter`, ulkokehän poistettavat 18 m solut `osk`, `hideB`, `bdSkip`.
- **index.html** (`tools/rata/patch_index.py`, voi ajaa uudelleen): `import RATA`, maastokorjaukset heti siltakumpujen jälkeen, ulkokehän 18 m ruudukosta solut pois rataverkon kohdalta, rautatiesiltojen vanhat kannet pois, LoD2-laatikot 2298 ja 2299 pois, `window.__game`iin `TZg` ja `outerMat` sekä `<script>`-rivit `rata/rata.js` ja `juna/juna.js`.

## Uudelleenrakennus (`tools/rata/`)
```
python3 tools/rata/build_data.py   # osm_rail.json + terrain.js -> rata_data.json
python3 tools/rata/mkjs.py         # -> rata/rata_data.js
python3 tools/rata/tex.py          # sepelitekstuurit (proseduraaliset)
```
`osm_rail.json` = Overpass-haku 20.11.2026 (railway=*, laiturit, asemarakennukset kartan alueelta) muunnettuna pelikoordinaateiksi.
Pilvi ei pääse Overpassiin: haku tehtiin käyttäjän selaimessa.

## Korkeudet
- Pölkyn yläpinta = MML 2 m -korkeusmalli raiteen kohdalla (mediaani + Gauss) + 0,10 m, kiskon yläpinta +0,19 m.
- **Alikulku**: korkeusmallissa aseman tunneli on 4 m syvä kaivanto koko ratapihan poikki. Rata kulkee sen yli suoraan (kuopat tunnistetaan 80 m:n mediaanista), ja kaivanto täytetään raiteiden ja laitureiden kohdalta. Asema-aukion puoleinen pää jää auki, ja siihen tulee portaali (omistaja 20.11.: "katso, että rata menee suoraan").
- Ratapenkka: maan ruudukon solmut 3,6 m:n säteellä raiteesta painetaan 0,35 m pölkyn yläpinnan alle.
- Sillat (OSM bridge=yes): korkeus suoraan päiden välillä.
