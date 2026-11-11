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

---

# Siirto 11.11.2026 – tilanne seuraavalle Claudelle

Peli: `index.html` + moduulit, julkaistu artefaktina "Porin kopterilento" (claude.ai/artifact/PvpEPUUtoM8XAJDq8bNvmw) ja repoon
`villeaklinikkasomero/porin-kopterilento` (käyttäjä pushaa GitHub Desktopilla, kansio `C:\Users\ville.somero\Documents\GitHub\porin-kopterilento`).
Koordinaatit: kartta-metrit, origo lon 21.796 / lat 61.486, x = (lon-21.796)*53278, y = (lat-61.486)*111437; three.js: (x, korkeus, -y).

## Uudet aineistot (kaikki avoimia, lähde näkyy pelin alalaidassa)
- **Maanmittauslaitos Rakennukset 3D (LoD2, CityGML, CC BY 4.0)**: karttalehdet M3412C/D/E/F (6×6 km, mittaus 2023).
  `blender/parse.py` (CityGML -> b.pkl pelikoordinaateissa) -> `blender/mml_city.py` -> `lod2.js`
  (kaikki ~4 200 rakennusta mitatuilla seinillä ja katoilla; ikkunat vain räystään alle, kerrosluku räystäskorkeudesta;
  `hide` = OSM-osat jotka toinen LoD2-malli peittää; `raw.pkl` = polygonit Blenderille).
  Pelissä LoD2 ei koske Kivi-Porin/torin Blender-kortteleita (ZB < 12, Kivi-suorakaide) eikä OWNROOF-taloja.
- **Maanmittauslaitos Korkeusmalli 2 m (GeoTIFF)**: samat lehdet. `blender/dem_build.py` -> `terrain.js`
  (REF = 4.0 m: pelin y = N2000 - 4; `hg` = todellinen maa 6 m ruudukko, joen pohja vedenpinnan alla;
  `hs` = jokialue täytetty + pehmennetty kenttä, jolla KAIKKI muut objektit nostetaan shaderissa `terrainize()`;
  vedenpinta `TER.wl` ≈ -3.6). Maa on ruudukkoverkko (`gridGeo`, ydin 6 m, ulko 18 m).
  Objektit joita EI nosteta merkitään `noT()` / `userData.noT` (helikopteri, varjo, vesi, maa, ponttonit suhteessa `WREL`).
  Lentologiikka: `roofAt()` käyttää TZs/TZg/TER.wl.
- **Kokemäenjoki**: OSM-relaatio 186982 (haettu selaimella) -> `river.pkl` -> `blender/river_build.py` -> `river.js`
  (vesi, 4 m maski `inRiver`, siltakannet `RIV.br`, Etelärannan rantaviiva `RIV.quay`, Etelärannan kaistale jätetty maasta pois).
- **Porin kaupungin ilmakuva-WMS** (`kartta.pori.fi/TeklaOGCWeb/WMS.ashx`, taso Ilmakuva, ~10 v vanha, natiivi ~10 cm):
  30 ruutua `ot/ot_i_j.jpg` (512 m, 0.25 m/px, x -1280..1792, y -1280..1280), ladataan helikopterin ympäriltä (`hrUpdate`).
  Haku: selaimessa kartta.pori.fi-sivulla fetch + OffscreenCanvas -> yksi bin-tiedosto Downloads-kansioon -> device_stage_files.

## Uudet mallit / koodi
- `blender/lm.py`: `mml_shell()` (LoD2-kuori Blenderiin) ja `rich_deco()` (sokkeli, kerroslistat, ikkunat, kaari-ikkunat,
  lesenat, räystäslista). Kohteet: `tehdas` (Puuvilla, LoD2 + torni + lyhdyt), `asema` (rautatieasema), `samk`,
  `cygnaeus` (Cygnaeuksen koulu, Tasavallankatu 1). Pakkaus: glb -> base64 `bl_KEY.js`, LMAT + plain-listaan index.html:ssä.
- `blender/zones2.py` + `run2.py`: Blender-julkisivut LoD2-rungoille (gen.py-moduulit), pilotti `bl_p1.js` (ZB=12).
  Ajo: `python3 run2.py NIMI '[indeksit]' 12` (~1 min / 14 taloa).
- `bridge.py`: Porinsilta (portaalit pilarien 1 ja 2 päällä, 1971 kuvan mukaan).
- Aittaluodon voimalaitoksen piiput (126 m @ (1177,322), 70 m @ (1203,300)) ja sininen voimalaitos (SRW 3), Sampo-Rosenlewin tiilet (SRW).
- Eteläranta (index.html "Eteläranta (renewed quay)"): alempi rantakäytävä -1.05, 3 porrasta, pensaat, kaide, 3 ponttonia,
  2 paviljonkia, purjelaiva. Paikat arvioitu käyttäjän kuvista.
- Nurmikko: `grassify()` (proseduraalinen nurmitekstuuri vihreisiin kohtiin), vesi: `waterify()`.

## Testit
`node shot4.mjs '[["nimi",x,y,alt,yaw]]'` (kuvat v_nimi.jpg, kestää ~2 min) ja `node logic4.mjs` (loppu "no errors").
Testipalvelin palvelee `/home/claude/pori`.

## Kesken / seuraavaksi
1. Autot paremmiksi ilmaisilla CC0-malleilla (esim. Kenney "Car Kit", Quaternius "Cars"; tarkista lisenssi) -> korvaa `cars.js`/parkkiautojen geometria.
2. Kivi-Pori uudelleen LoD2-rungoilla + rich_deco, kun kaupungin valokuvat tulevat (käyttäjä saa tällä viikolla).
3. Keskustan muut korttelit zones2-pipelinella (pilotti p1 hyväksytty suunnaksi; värit kuvista).
4. Ihantolanpiha 3 ja Kansakoulukatu 26 talot (odottaa tarkennusta), repon "– kopio"-tiedostojen siivous (käyttäjä lykkäsi).
5. Käyttäjä voi hankkia kaupungilta kerrosluvut ja uudemman ilmakuvan.

Huom: käyttöehtojen hyväksyntä (MML-tilaukset) ja GitHub-push vaativat käyttäjän luvan; MML-tilauksen viimeisen
"Tilaa tuotteet" -napin painaa käyttäjä itse.

## Päivitys 11.11.2026 klo 10.30
- **Tarkka ilmakuva koko alueelle:** 58 uutta 512 m ruutua (`ot/ot_i_j.jpg`, i −3..7, j −1..6, 1536 px = 0,33 m/px)
  keskustan 30 ruudun (2048 px) ympärille. Ladataan vasta kun kopteri on alle 420 m päässä (`HR` + `hrUpdate`).
  Haku: kartta.pori.fi-sivulla selaimessa WMS 1.1.1 GetMap (EPSG:4326, LAYERS=Ilmakuva) → OffscreenCanvas → JPEG →
  nippuna (`otbN.bin`: 4 tavun pituus + JSON-otsake + kuvat) Downloads-kansioon → device_stage_files → purku.
  XML-sivulla latauslinkki pitää luoda `createElementNS('http://www.w3.org/1999/xhtml','a')`.
- **Pehmeät joenrannat:** `blender/dem_build.py` laskee etäisyyden rantaviivaan (OSM-joki): ranta laskee loivasti veteen
  ja pohja syvenee asteittain, joten rantaviiva seuraa joen muotoa eikä 6 m ruudukkoa.
- **Eteläranta:** uudistus (portaat, kaide, pensaat, ponttonit, paviljongit) vain Porinsillalta Taavi-sillalle
  (`QSEG` x > −143 tiedostossa `blender/river_build.py`); Taavi-sillan länsipuolella vanha ranta ilmakuvan mukaan.
- **Barco-laiva:** `blender/barco.py` → `bl_barco.js` (musta runko, valkoinen raita, keula­kansi ja keulapuu, kaksi
  valkoista mastoa, valkoinen peräkansirakennus BARCO-kyltillä, kaiteet, valosarjat). OSM:n laivan "rakennus"
  (id 1196441531) ohitetaan. Paikka ja suunta OSM-ääriviivasta, vesirajaan `TER.wl` (`noT`).
- **Autot:** `cars.js` on edelleen vanha (car0–car2). Koodi hyväksyy myös 7 tyypin tiedoston. Kenneyn kokeiluversio
  (lelumainen, ei käytössä) on työtilassa. Käyttäjä haluaa myöhemmin realistiset eurooppalaiset autot Blenderissä
  (viistoperä, farmari, katumaasturi, pakettiauto, Scania-tyyppinen kuorma-auto), hillityt värit.
- Taivaalla näkyy vaalea kupolimainen haamu kaukana (vanha vika, ei korjattu).
