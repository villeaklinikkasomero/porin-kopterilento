# Porin kopterilento – siirto toiselle Claude-tilille (päivitetty 12.11.2026 klo 23)

Liitä tämä tiedosto uuden keskustelun alkuun. Pyydä Claudea lukemaan myös repon `SIIRTO.md`, `pipeline/README.md` ja `HANDOFF_Y-PAKKI.md` (jos repossa).
Vastaukset suomeksi, lyhyesti, ja kuvat todisteeksi muutoksista.

## Missä kaikki on
- **GitHub:** `villeaklinikkasomero/porin-kopterilento`. Paikallinen kansio `C:\Users\ville.somero\Documents\GitHub\porin-kopterilento`; käyttäjä pushaa itse GitHub Desktopilla.
  Claude kirjoittaa tiedostot käyttäjän kansioon (Claude-sovelluksen laiteyhteys) ja tarkistaa ne lukemalla takaisin. Push vain käyttäjän pyynnöstä.
- **Render:** https://porin-kopterilento.onrender.com/ (päivittyy GitHubista).
- **Claude-artifakti** "Porikopteri", slug `b9ac93cd-98e1-4f31-9f51-c80da5b7706a`, kuuluu vanhalle tilille. Uudella tilillä julkaistaan oma artifakti repon tiedostoista.
- **Kaupungin valokuvat** (SharePoint Kuvat_kopterilento, kreditointi "Porin kaupunki") ja **Y-pakki** (Satakunnan Museo, kreditointi "Satakunnan Museo, Y-pakki"):
  kuvia ei viedä GitHubiin eikä peliin, niistä luetaan vain värit, materiaalit ja muodot.

## Grafiikkaputki (Modal)
- GitHub Actions → **porikit run**, kenttään esim. `bake bepop --samples 64` (nimetyt lohkot: `tori0..5`, `bepop`, `uima`, `isokarhu`, `promenadi`, ja nyt myös `kivi0..5`, `kl0`, `kl1`, `karhu`).
  `bake`-komennot ajetaan millä tahansa vapaalla GPU:lla (L4/A10/L40S) missä tahansa, muut komennot EU:n L4:llä (kaupungin kuvat pysyvät EU:ssa).
- Kaupunkilohkot: **porikit run** `city 64 c064,c067` (lista pilkuin) tai `city 64 c` / `city 64 h`.
- Tulokset menevät Modal-levylle `results/<päivä>/game`; peliin ne tulevat vasta **porikit collect** -ajon pull requestista.
- Säästä rahaa: aja vain muuttuneet lohkot. Paikallisesti voi koepolttaa 8 näytteellä (`python3 run.py <lohko> 8`, `python3 city.py c064 8`).

## Rakennusten mallinnus (blender/)
- `zones.py`: käsin tehdyt rakennukset (`SPEC[i]`) ja nimetyt lohkot (`ZONES`). `zones2.py`: julkisivut MML:n LoD2-kuoren päälle (`build_lod2`).
  `kivi.py`: Kivi-Pori- ja Karhu-lohkot. `city.py`: automaattiset kaupunkilohkot `c###` (kerrostalot) ja `h###` (pientalot), lista `city_zones.json`.
- `build_lod2`-koukut specissä: `fit`/`fitw(layout, korkeus, katu, seinän pituus, alakorkeus)` kerrosrivit seinäkohtaisesti, `alt(x,y)` seinäpolygonin
  keskipisteen mukaan toinen spec, `runalt(x,y)` seinän pätkä toisena talona (kun MML:n yksi rakennus sisältää useita taloja), `zcap(x,y)` seinien yläraja
  (avoin tila katoksen alla), `skip(r, k)` LoD2-osien pois jättäminen, `roofmat_fn(r)` kattojen materiaali.
- `run.py`: spec `lod2=True` → nimetty lohko rakennetaan LoD2-kuoren päälle ja katot leivotaan malliin (BePOP, IsoKarhu, Promenadikeskus).
- `styles.json` (`b[i]`: w väri, k render/brick/wood, f kerrokset Ryhdistä, r katto, note, shop, lift): peli ja Blender lukevat saman tiedoston.
  Merkinnät ilman `m` ovat käyttäjän hyväksymiä tai lähteestä lukittuja: Lyseo 1351/1353, Otava 1249, Karhukortteli 1450–1515, Cafe Anton 563.
- Liiketilat (`shop:1`) vain keskustan kaupallisilla kaduilla. Katos 1202 ja kävelysilta 1243 piirretään ilmaan (`lift`).

## Tehty 12.11.2026 (koepoltettu paikallisesti, Modal-ajot käyttäjällä)
- BePOP LoD2-kuoren päälle: lasiholvi, pyöreä torni avoimine kruunuineen, Yrjönkadun katos 8 pylväällä (uurretut suppilokapiteelit),
  vinoruutuinen lasihalli, ylimmän kerroksen kolmioikkunat. Samaan kuoreen Hotelli Bepop (klinkkeri, parvekenauhat) ja Maakuntalinna (valkoinen pelti).
- Palojoenkulma (tiili, nauhaikkunat), Yrjönkatu 21 sen kuoren pohjoispäässä (vaalea okra rappaus), Keskuskartano (valkoiset nauhat, harmaat paneelit, peltipäädyt).
- IsoKarhu ja Promenadikeskus LoD2-kuoren päälle (korkeudet ja kattomuodot skannauksesta; Promenadin kaareva salikatto).
- Sokos (vaaleanharmaat levyt, pystyikkunat), Porin Talo (sininen levy, nauhaikkunat) ja Linnainmaankulman torni samasta kuoresta.
- Valtakatu 3 ja Yrjönkatu 2 b (vaalea tiililaatta, lasitetut parvekkeet) kivi5-lohkossa. Y-pakin virhekohdistus Yrjönkatu 7 → 1582 korjattu.

## Katujen läpikäynti (käyttäjän toive: kadut yksitellen keskustasta Karjarantaan päin)
- Työkalu: `python3 audit/street.py '<kadun nimi>' 12` listaa kadun talot: tekotapa (käsilohko, kaupunkilohko, maamerkki, LoD2-kuori), korkeus vs LoD2,
  kerrokset (Ryhti / Y-pakki), väri ja sen lähde. Sen jälkeen pelikuvat kadun molemmin puolin, Y-pakin tekstit ja kuvat, verkko.
- **Jokainen rakennus tarkastetaan Google Street View'tä vasten** (sovittu käyttäjän kanssa): pelikuva ja Street View -kuva samasta suunnasta rinnakkain,
  tarkistetaan väri, materiaali, kerrosluku, kattomuoto, parvekkeet ja liiketilat. Street View -kuvia ei tallenneta repoon eikä peliin; niistä luetaan vain
  ominaisuudet (kuten kaupungin ja Y-pakin kuvista). Näkymä: `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=LAT,LON&heading=H&pitch=10&fov=80`
  (katupiste lähimmältä kadulta, suunta rakennukseen).
- Tehty: Yrjönkatu, Antinkatu, Pohjois- ja Eteläpuisto. Seuraavaksi länteen: Luotsinmäenpuistokatu/Teatterikatu, Otavankatu, Annankatu,
  Katariinankatu, Vapaudenkatu, Ratakatu … kohti Karjarantaa.
- Antinkadulta korjattu: Y-pakin "puu"-materiaali oli tarttunut kerrostaloihin (Antinkatu 25, Liisankatu 8, Antinkatu 27 A:n väärä kohdistus),
  Antinkatu 21b:n oikea talo (137, hiekanvärinen nauhajulkisivu), Valtakatu 7 Valtakulma (pesubetoni/klinkkeri, 7 krs).
- Korjattu bugi: Kivi-Porin ja kl-lohkojen talot, joilla ei ole LoD2-kuorta, saivat mustan katon (katto puuttui mallista).
  Lisäksi tasakatot ja LoD2-katot käännetään aina ylöspäin.

- Pohjois-/Eteläpuistosta korjattu: Eteläpuisto 15a (1900, valkoinen 3 krs) ja 15b (1880, sininen puutalo) erotettu seinäkorkeuden mukaan,
  Eteläpuisto 19 (1891) erotettu Eteläpuisto 17:n (1968) kuoresta, tori2-lohkon talo 1312 nostettu 4,7 m laatikosta 2-kerroksiseksi aumakattoiseksi
  (skannauksen räystäs ~7 m; talo tunnistamatta, tarkista kuvasta).
- Avoin: Pohjoispuisto 1 (1985): Y-pakissa 5 krs, Ryhdissä 7, pelissä 27 m ilman LoD2-kuorta.

- **Parvekkeet:** Porissa parvekkeet ovat pääsääntöisesti sisäänvedettyjä ja lasitettuja (käyttäjä 12.11.). gen.py:n `punched`-moduulin 'B'-sarake
  tekee nyt sisäänvedetyn lasitetun parvekkeen; ulokeparveke vain `proj_balcony=True`. Koskee kaikkia lohkoja → koko kaupunki ajettava uudelleen.
- **Talojen luokittelu:** OSM merkitsee osan kerrostaloista "house"-tyypiksi; 29 tällaista (räystäs skannauksessa yli 9,5 m, jopa 30 m) oli piirretty
  puutaloina h-lohkoissa. city.py käyttää niille nyt kerrostalospeciä.
- Parveketyyppi talokohtaisesti: `styles.json` b[i].`bal` = "proj" → ulokeparvekkeet (oletus sisäänvedetty lasitettu). Käyttäjä: kaikki eivät ole
  sisäänvedettyjä → katujen läpikäynnissä parveketyyppi tarkistetaan kuvista ja merkitään.
- Kulturhuset Fiini (JKMM 2025, Eteläpuisto 15 / Mikonkatu 13) korvaa Y-pakin puretut 15a/15b: punatiili, pronssinväriset lamellit, lasi.
  LoD2-skannaus on vanhempi kuin talo, joten index.html:n `L2OLD`-joukko ohittaa sen (572) ja talo rakennetaan pohjapiirroksesta.
- Eteläpuisto 17 käyttäjän katukuvan mukaan (valkoinen, sisäänvedetyt lasitetut parvekepinot, harmaa laattapääty, näyteikkunat).

## Ajettavat (jos eivät vielä ajettu)
1. `bake bepop isokarhu promenadi uima tori0 tori1 tori2 tori3 tori4 tori5 kivi0 kivi1 kivi2 kivi3 kivi4 kivi5 kl0 kl1 --samples 64`
2. `city 64 c` (kaikki kerrostalolohkot: parvekemuutos) ja `city 64 h020,h021,h040,h057,h059,h068,h070,h071,h072,h073,h074,h084,h085,h089,h101,h134,h179`
3. **porikit collect** → PR → merge.

## Avoinna
- Promenadikeskuksen julkisivu on arvio (tumma metalli, lasiaula); tarkista katukuvasta.
- Asemanseutu puuttuu Y-pakista: tehdään ilmakuvista. Riihikedon ja Tiilimäen loput talot vinokuvista.
- Pienet: IsoKarhun kattokannen autot/LoD2-möhkäleet, BePOPin kyltit ja katon "purjeet".

## Tehty 13.11.2026
- Kasvillisuus: `trees_extra.js` (noin 53 500 puuta ilmakuvan latvustosta, `blender/veg_trees.py`); lähellä lehtikorttipuut 320 m, kauempana kevyet latvukset 1,5 km.
- Alikulut: `blender/bridges_fix.py` + `blender/osm_extract.json` → `terrain.js` saa `bd`-listan (27 maasiltaa); peli piirtää kannen ilmakuvalla,
  reunapalkit ja kaiteet, alla oleva tie/rata jää leikkaukseen. Aja aina dem_buildin tuottamaa terrain.js:ää vasten.
- Kaupunginsairaala (8388, 4758 kellanruskea tiili) ja Käppärän koulu (4139) styles.jsoniin; Riihikedon 1950-luvun talot 3 krs (7, 117).

## Tärkeät huomiot
- Koordinaatit pelimetreinä: x = (lon − 21.796) · 53278, y = (lat − 61.486) · 111437. Three.js-paikka (x, korkeus, −y). city.js-polygonit desimetreinä.
- Rakennusindeksit viittaavat `city.js`:n järjestykseen: älä generoi city.js:ää uudelleen tarkistamatta indeksejä.
- three.js-shadereissa `gl_`-etuliite on varattu. Kahta päällekkäistä pintaa ei saa leipoa (tulee mustaa).
- Lataukset vain luvalla, tiedostojen poisto käyttäjän koneelta vain luvalla. API-avaimia tai GitHub-salaisuuksia ei käsitellä.
- Käyttäjä ei halua käyttää omaa rahaa turhaan: aja Modalissa vain tarvittavat lohkot.


## k28 (12.11.2026): tiilikuvio vanhoihin punatiilitaloihin
- index.html: brickify() lisää det_brick.jpg-tiilidetaljin (Fiinin kuvio) punertaville seinäpinnoille.
  Käytössä: kirkko, landmarkit tehdas/kehraamo/puuvilla/vesitorni/kappelit, Puuvillan ja Aittaluodon piiput, proseduraalinen seinätyyli 5 (Sampo-Rosenlew ym.).
- styles.json: k='brick' -> Aittaluodon kerrostalot 1543-1546, 1645-1650, Rosenlew-museo 1591, saha 1745, voimalaitos 6289.
- Aittaluodon c-zone (c081) vaatii uudelleenbaken: city 64 c081 (sisältyy ajoon city 64 c).

## k29: Fiini-Eteläpuisto 13 väli + Eteläpuisto 13 parvekkeet
- zones.py: Fiinin huoltosisäänkäynti (8 m, kuparinväriset pystysäleet, lasi) rakennuksien 572 ja 70 väliin (SPEC[572] extra _fi_gap_extra).
- SPEC[70] Eteläpuisto 13: liiketilat katutasossa, Eteläpuiston puolella yhtenäiset sisäänvedetyt lasitetut parvekkeet harmahtavalla lasilla (MODS 'gloggia'), päädyt valkoiset.
- Vaatii: city 64 c049 (sisältyy city 64 c).
- Eteläpuisto 13 (70) ja 17 (142): katutason liiketilat sisäänvedetty parvekkeen syvyyden verran (1,5 m), MODS['shop'] + P grecess, alapuolinen soffitti.
- Eteläpuisto 13 (70): rakennetaan OSM-pohjalla (footprint, h 24, yksi tasakatto + hormit; LoD2:n porrastettu ylin kerros oli väärin). Pihan puoli: valkoinen pystyprofiilipelti, keltaiset paneelit, avoparvekepino (MODS 'rib'). index.html: L2OLD + HFIX {70: 24}.
- Eteläpuisto 11 (65, c050): SPEC[65] _e11_fit kuten 13: lasitetut parvekenauhat harmailla kaiteilla, etelapäässä 3 umpiruutua, sisäänvedetty kivijalka; LoD2-kuoren pohjoisosa (537) runalt omalla specillä.
- Vaatii: city 64 c049,c050 (sisältyy city 64 c).
- Eteläpuisto 11: käyttäjän korjaus - lasiparvekkeet myös eteläpäähän, sisäänvedetty ylin kerros valkoinen.
- Eteläpuisto 9 (537, Pohjoispuiston kulma, LoD2-kuoressa 65): 1930-luvun funkis kuvasta 7/2023 - okra rappaus, kermanväriset erkkeripinot ruskein karmein, kivijalassa tumma kivi + vihreä kuparilista (_SPEC_E9, 65:n runalt).
- Eteläpuisto 9: 13 ikkunaa + 3 kermanväristä erkkeripinoa Eteläpuiston puolella, 1 erkkeri Pohjoispuiston puolella kulmassa (1 m ulos). zones2.build_lod2: spec splitruns=True katkaisee seinäjakson kohdasta, jossa runalt vaihtuu (65/537 yhteinen LoD2-kuori).

## Katutarkastus Street View'ta vasten (13.11.2026)
Sääntö: jokainen rakennus tarkastetaan Google Street View'ta vasten. Tarkastetut on merkitty styles.json:iin `"sv": 1` (ja `m` poistettu, jotta automaattiset ajot eivät ylikirjoita).
- Otavankatu (23 rak.), Annankatu (30), Katariinankatu (36) tehty. Isoimmat korjaukset: Otavankatu 3 vaalea rappaus (ei punatiili), Otavankatu 14 valkoinen 3 krs + ullakko, Annankatu 19/25 ja Katariinankatu 15/18/19/20 puutaloja (olivat rappaus/kivi), Katariinankatu 10 6 krs (oli 2), useita värejä.
- Avoimet: kuori 5 (Otavankatu 17+19 samassa 20 m kuoressa → iso ikkunaton seinä, h085). Katariinankatu 4 uudisrakennus (1517, 1535: tumma tiili ~6 krs) on city.js:ssä 4–8 m korkea. Äestäjänkatu 10 (77) on purettu, tontti tyhjä.
- Uudelleenleivonta (Modal, vain käyttäjän luvalla). HUOM: lohkolista pilkuilla ilman välilyöntejä, ja kivi-lohkot (kl0, kl1, kivi0) ajetaan bake-komennolla, ei city-komennolla:
  - `city 64 c035,c036,c037,c038,c039,c047,c048,c049,c050,c053,h074,h075,h077,h085`
  - `bake kl0 kl1 kivi0 --samples 64`
Seuraavaksi: Luotsinmäenpuistokatu, Teatterikatu, Vapaudenkatu, Ratakatu.


## Seuraava iso työ (13.11.2026 klo 02, käyttäjän ehdotus): kaupungin kuvat oikeisiin taloihin Street View'n avulla
- Kaupungin kuvat (SharePoint Kuvat_kopterilento, haettu 11.11.) ovat työtilassa `/home/claude/photos/img/<kaupunginosa>/` – 268 kuvaa, ei GPS-tietoa,
  tiedostonimessä usein kadun nimi. Kuvat EIVÄT mene GitHubiin eikä peliin; kaupungin kuvat käsitellään EU:ssa (Modal EU tai käyttäjän kone).
  Jos uusi tili/työtila: kuvat pitää hakea SharePointista uudelleen.
- Aiemmin 43 kuvaa on jo kohdistettu ja oikaistu (`/home/claude/phw/jobs.json`: kuva -> rakennus b, seinä, kerrokset, ikkunaväli; `p*_rect.jpg`).
  Kohdistukset tehtiin ILMAN Street View'ta -> osa voi olla väärin (esim. "Keskusta 31 Eteläpuisto" -> b130?). Tarkista kaikki.
- Työnkulku: 1) tunnista kuvan talo ja kuvaussuunta vertaamalla Street View'hun (vain katsominen, Google-kuvista ei siirretä pikseleitä mihinkään –
  Googlen ehdot kieltävät johdetun aineiston), 2) 4 kulmaa -> oikaistu julkisivu (porikit review / phw), 3) luetaan ikkunarivit, ikkunaväli, kerroskorkeudet,
  parvekkeet, värit -> SPEC/styles.json, 4) kuva ja heijaste poistetaan, talo rakennetaan luvuista. Aloitus: Eteläpuiston kuvat (Keskusta 31, 32, 37).
- index.html 13.11.: brickify() koskee nyt kaikkia Blender-lohkoja (tiilikuvio punaisille ja rappausrae vaaleille seinille, koska peli pienentää
  atlakset 1024 px:iin). Fiini näkyy pelissä vasta, kun c049 on ajettu Modalissa (pelin bl_c049.js on 12.11. illalta, ennen Fiiniä).
- HUOM: pelin bl_bepop/isokarhu/promenadi/tori*/kivi*/kl* ovat 10.–12.11. aamulta -> BePOP, Cumulus, IsoKarhu, Promenadi, Sokos, Teljäntori, Keskuskartano/Amado
  näyttävät vanhoilta/rikki, kunnes bake-ajo (bepop isokarhu promenadi uima tori0-5 kivi0-5 kl0 kl1 --samples 64) + collect on tehty.


## 13.11.2026 klo 03-04 (tämä istunto)
- **Uusi ilmakuva:** MML ortokuva 2025, karttalehdet M3412C/D/E/F (tilaus 98100313634, latauslinkki käyttäjän sähköpostissa 30 pv). Alkuperäiset .jp2 kansiossa `mml_orto/` (.gitignore).
  Lehtien SW-kulmat (TM35): C 218000/6822000, E 224000/6822000, D 218000/6828000, F 224000/6828000 (6 km, 0,5 m). Pelin orto.jpg (ydin) ja outer.jpg tehty niistä: työtilan `mmlwork/orto_build.py`
  (pelikoordinaatit -> lon/lat -> EPSG:3067). Kohdistus vanhaan kuvaan tarkistettu ECC:llä (identiteetti). Lähdemaininta index.html #credit.
- **collect-korjaus:** .github/workflows/porikit-collect.yml kopioi nyt kaikki bl_*.js (ennen nimetyt lohkot ohitettiin -> bepop/tori/kivi eivät koskaan päätyneet peliin). Suojattu tiedosto: käyttäjä muokkaa itse.
- **modal_app.py:** `bake` kulkee city_zone-reitin kautta (run.py nimetyille lohkoille), lokiin [nimi] rc/md5/log tail.
- **styles.json:** toisen istunnon automaattinen väriajo oli korvannut käsin tehtyjä merkintöjä liiloilla mitatuilla väreillä (m:1) ja poistanut lift-merkinnät (Promenadin katos 1202, Sokos-IsoKarhu silta 1243). Palautettu. ÄLÄ aja väriajoa niin, että se korvaa merkintöjä ilman 'm'.
- Promenadi ja IsoKarhu uusittu Street View -kuvien mukaan (zones.py). Puuvillan tehdas: Fiinin tiili (lm.py, bl_tehdas.js poltettu paikallisesti). Kyltit poistettu liiketilojen päältä (gen.py).
- Kauppakeskus Puuvilla (1555) on peltihalli -> rakennetaan uudelleen uuden ortokuvan mukaan (seuraava työ).
- Odottaa Modal-ajoja: `bake promenadi isokarhu --samples 64`, `city 64 c048,c049,c050,c055,c064,c065,c081,h088`, sitten collect.

## Seuraava työ: keskustan katujen systemaattinen Street View -läpikäynti (käyttäjä 13.11.2026)
Järjestys: 1 Antinkatu, 2 Yrjönkatu, 3 Valtakatu, 4 Itsenäisyydenkatu, 5 Isolinnankatu, 6 Pohjoisranta + Eteläranta, 7 Hallituskatu,
8 Gallen-Kallelankatu, 9 Mikonkatu, 10 Liisankatu, 11 Otavankatu + Annankatu + Katariinankatu, 12 Länsipuisto, 13 Itäpuisto.
Joka kadulla: `python3 audit/street.py '<Katu>' 25` -> jokaisesta talosta Street View -pikkukuva (menetelmä tämän asiakirjan alussa) ->
poikkeamalista (väri, kerrokset, ikkunat, parvekkeet sisäänvedetty/ulkoneva/lasitettu, kivijalka, katto, väli naapuriin, LoD2-kuoren useat talot)
-> näytä käyttäjälle ENNEN korjauksia -> korjaa -> merkitse styles.json "sv": 1.
Kauppakeskus Puuvilla rakennettu peltihallina 13.11. (lm.py, bl_puuvilla.js, tex 'ribs').

## 13.11.2026 aamu: Antinkatu Street View'ta vasten (uusi työtapa)
- **Vertailukuvat:** pelin Render-versio sisäänrakennetussa selaimessa, kamera katutasolle JS:llä (`window.__game`, cockpit-kamera, S.x/S.y/S.yaw,
  alt = roofAt + 1,6, fov 58,7° pystyyn = Street View fov 90 vaakaan 1280×720). Selainpaneeli on usein piilossa → rAF ei pyöri: kutsu `G.step()`
  itse ja tee näkymä `renderer.render`illä (funktio `__shot(x, y, suunta)` tämän istunnon muistiinpanoissa). Rakennusten id:t tarroina kuvaan
  projisoimalla city.js-keskipisteet kameralla. Kuvaparit 60 m välein kadun molemmille puolille.
- **Paikallinen koepoltto toimii:** `pip install bpy==5.2.4` (blender/bpyurl.txt), raw.pkl yms. `pipeline/data/porikit_data.tgz` → /home/claude/mmlproc,
  blender/*.py → /home/claude, pelin tiedostot → /home/claude/pori. `python3 -c "import kivi; kivi.build_and_bake('kivi3', kivi.ZONESK['kivi3'], 4)"`
  ~100 s CPU:lla. Mustien seinien tarkistus: atlaksen lo-ruudut, joiden keskiarvo < 25 ja joiden edessä ei ole toista rakennusta.
- **Korjattu kivi.py:** (1) Kivi-Porin klassiset talot arpoivat seinävärin KIVIP-paletista eivätkä lukeneet styles.json:ia → nyt käytetään
  lukittua väriä, materiaalia (brick) ja kerroslukua `f` (merkinnät ilman `m`). (2) Yksi MML-LoD2-kuori voi sisältää useita OSM-taloja
  (1579 Hallituskatu 6 ⊃ Valtakatu 7:n torni 1581, 1603, 1583, 1716; 1566 ⊃ 1573, 1607). Talot rakennettiin kahdesti → päällekkäiset seinät →
  musta torni. Nyt `shell_parts` + `shell_runalt`: kuoren seinät talon kohdalla saavat sen talon specin. (3) 1604 keltainen jugendtalo ja 1573
  matala keltainen talo klassisiksi. (4) Uusi lohko `p1` (Antinkatu 21–25 / Mikonkatu; vanhalla bl_p1.js:llä ei ollut generaattoria).
- **zones.py:** Satarauta 1361 okrankeltaiseksi, uusi SPEC[1493] Antinkatu 9 (koristeellinen 2-kerroksinen, keltaiset pilasterit).
- **styles.json:** Antinkadun talot korjattu ja merkitty `sv: 1` (1560 lohenpunainen, 1563 valkoinen, 1566, 1604, 1573, 1361, 1493, 274, 125, 276,
  114, 255, 124, 250, 569, 118, 290 + tarkastetut 215, 604, 161, 1490, 1497, 564).
- **Ajettava Modalissa:** `bake kivi2 kivi3 kivi4 tori1 p1 --samples 64` ja `city 64 c047,c048,c051,c052,c063` → collect.
- **Avoinna Antinkadulta:** liiketilat näyttävät koko kaupungissa suljetuilta ovilta (gen.py shop-moduuli, oma työ); pelin `brickify` tekee
  punaisesta levyseinästä tiiltä (Ratsula 221); Antinlinnan (116) erkkerit; Säästöpankin (163) ja Pohjoiskauppatori 3:n (1726) värit
  epävarmoja (pilvinen kuva / kaupungin kuva); seinämaalaukset (564, Liikekulman 1497 päätyreliefi) tehdään lopuksi, kun muuten ollaan tyytyväisiä.
  Pieniä jäännös-mustia ruutuja: 1361 sisäpiha, 1286/1290 (kivi2), 135 (p1).
- Seuraava katu: Yrjönkatu (järjestyslistan 2).

## 13.11.2026 klo 8–9: Yrjönkatu Street View'ta vasten
- **kivi.py, laajennus:** `shell_parts` ottaa nyt mukaan myös pelin piilottamat talot (lod2.js `hide`), joiden ulkoasu on lukittu styles.json:iin
  (w ilman m). Ne piirretään kuoren omistajan LoD2-seinille omalla specillään; käsin tehty runalt (Eteläpuisto 9) voittaa. Koskee myös
  kaupunkilohkoja, koska city.py kutsuu kivi.build_and_bake:a: c023, c033, c037, c038, c039, c047, c048, c049, c050, c051, c064, c065, c067, c068, c110.
- **zones.py:** SPEC[238] Sampotalo (Yrjönkatu 13): 2-kerroksinen liiketalo Teljäntorin edessä, vihreä otsalista, harmaa poimulevy + ikkunanauha.
- **styles.json:** 1567/1568 okrankeltainen 2 krs (Yrjönkatu/Eteläranta kulma), 1582 Yrjönkatu 7 okra 6 krs (1579:n kuoressa), 109 Yrjönkatu 27 valkoinen.
- **Ajettava:** `bake kivi3 kivi4 kivi5 --samples 64` ja `city 64 c023,c033,c037,c038,c039,c047,c048,c049,c050,c051,c064,c065,c067,c068,c110`
  (sisältää aamun Antinkatu-ajot c047/c048/c051/c052/c063: lisää c052,c063 jos niitä ei ole vielä ajettu) → collect.
- **Avoinna Yrjönkadulta:** Airionkulma 603 (pelin valokuvajulkisivu keltainen, Street View'ssa harmaa-valkoinen raitajulkisivu – tarkista),
  Postitalo 1601 (pelissä ruskeat raidat, todellisuudessa valkoinen + harmaanvihreät nauhat; pelin tori5 on 03:10 leivottu), Kuparikonttori 269
  (tummanruskea levy → pelin brickify tekee tiiltä, sama kuin Ratsula), Yrjönkatu 25 (107) aumakatto puuttuu, Yrjönkatu 27 (109) kulmaparvekkeet.
  BePOP, IsoKarhu, Promenadi, Sokos ja Porin Talo tarkistetaan vasta, kun 12.–13.11. leivonnat ovat pelissä.
- Seuraava katu: Valtakatu.

## 13.11.2026 klo 10–10.30: käyttäjän tarkennukset
- **Airionkulma 603:** käyttäjän mukaan nykyinen valokuvajulkisivu on hyvä → ei muutettu (kokeiltu lasiverhousta, peruttu).
- **Porin Leijona 1601** (ent. Postitalo, Yrjönkatu 6, remontoitu 2025): SPEC[1601] valkoinen + vaaleanharmaanvihreät ikkunanauhat, lasitettu katutaso (tori5).
- **Ratsula 221:** punainen peltiverhous. Uusi styles-materiaali `k: 'metal'` (zones2.look_mat → MT(..., None)): punainen seinä ei enää muutu
  tiileksi (gen.detail_kind teki tummanpunaisista tiiltä). SPEC[221] nauhaikkunat + liiketilakerros (c052). Kuparikonttori 269 myös `metal` (c065).
- **Aittaluoto 1648:** vaaleanvioletti torni → punatiili kuten 1645–1650 (c081).
- **gen.py:** m_ribbon hyväksyy `wglass` (ikkunalasin väri).
- **Ehdotus odottaa päätöstä:** liiketilojen lasit (gen.py `shop_glass`, versio tallessa istunnossa work/gen_shop.py): yläosa heijastaa, alaosassa
  vaaleita esillepanoja → ei enää näytä suljetuilta ovilta. Koskee kaikkia lohkoja → vaatii koko keskustan uudelleenleivonnan.
- **Ajettava:** `bake kivi3 kivi4 kivi5 tori5 --samples 64` ja `city 64 c023,c033,c037,c038,c039,c047,c048,c049,c050,c051,c052,c063,c064,c065,c067,c068,c081,c110`.
- **10.40 Näyteikkunat hyväksytty (käyttäjä):** gen.py `shop_glass` käytössä kaikissa liiketiloissa (paitsi joissa SPEC antaa oman `gglass`):
  alaosa #363e44, yläosa heijastus #75828b, 1–3 vaaleaa esillepanoa. Vaatii kaikkien lohkojen uudelleenleivonnan.
- **Ratsula tarkistettu Street View'sta (3 suuntaa):** lasitettu liiketilakerros punaisten pilarien välissä, kerroksen korkuinen harmaa
  lasinauha, ylhäällä umpinainen punainen peltinauha (SPEC[221], top=plain).
- **Ajettava (korvaa aiemmat listat):** `bake kivi0 kivi1 kivi2 kivi3 kivi4 kivi5 kl0 kl1 tori0 tori1 tori2 tori3 tori4 tori5 p1 bepop isokarhu promenadi uima karhu --samples 64`
  ja `city 64 c` → collect. (h-lohkoissa ei liiketiloja muutamaa poikkeusta lukuun ottamatta; ne voi ajaa myöhemmin.)

## 13.11.2026 klo 10.45–11.30: syvennykset ja viistetyt kulmat (käyttäjä: "syvennykset jäävät samaan tasoon", "45 asteen kulmat")
- **gen.py build_wall: kerroskohtainen syvennys** `rowP[row]['setback'] = m`: rivin julkisivu (myös leivottavat laatat) siirtyy taaksepäin,
  yläpuolelle tulee alapinta (soffit), sisäänvedetyn ylimmän kerroksen eteen tasanne, päihin pilarit (sisäänpäin käännetty päätyseinä
  leivottiin mustaksi). Lisäksi `piers=(joka k:s väli, leveys)`, `piermat`, `soffit`, `open_ends`. Käytössä: Ratsula (liiketilakerros 1,6 m
  punaisten pilarien takana).
- **chamfer.py (uusi):** OSM:n 1,5–6 m vinot kulmasivut (≈45°) leikataan LoD2-kuoriin: kaikki pinnat (G/R/W) leikataan pystytasolla ja
  viisteelle lisätään oma seinä → build_lod2 tekee sille julkisivun. zones2 kutsuu `chamfer.apply(RAW, B, LOOK)` latauksessa.
  styles.json `ch: [[x, y, w], ...]` lisää kulman, jota OSM:ssä ei ole (lähin LoD2-kulma, viisteen leveys w).
  Leikattu nyt 24 kuorta, mm. 1560, 1563, 8385, 1572, 1574, 1559, 1285, 1287.
- **chamfer_lod2.py (uusi):** samat leikkaukset pelin lod2.js-kattoihin (vain lohkojen taloille, koska peli piirtää niiden mitatut katot).
  Ajettu kerran → lod2.js päivitetty. Ajetaan uudelleen, jos chamfer.py:n tai ch-merkintöjen lista muuttuu (toisto on harmiton).
- **Puuttuu vielä:** viisteen oma julkisivu (kulmaovi, parveke/erkkeri) – nyt viiste saa tavallisen 1 ikkunavälin tai umpiseinän.
- **Sovittu jatko (käyttäjä 10.41):** keskusta katu kadulta loppuun (Valtakatu seuraavaksi), sitten uusintakierros, sitten Riihiketo ja Isosanta.
- **Ajettava:** sama kuin edellä (kaikki nimetyt lohkot + `city 64 c`), koska gen.py ja zones2.py muuttuivat.
- **11.15 Korkeammat alakerran ikkunat (käyttäjä):** gen.py m_classic: ikkunan korkeus kasvaa kerroskorkeuden mukana (80 % vapaasta
  korkeudesta; katutaso ≤ 2,9 m, ylemmät ≤ 2,5 m, leveys kasvaa ≤ 20 %). Jos katutaso on vielä korkeampi, ylijäämä menee ikkunan alle
  (sokkelille korotettu katutaso). Kiinteä korkeus: rowP `wh_fixed=True`. Koskee kaikkia klassisia julkisivuja.
- **11.20 Kelluvat katot (käyttäjä):** sisäänvedetyn ylimmän kerroksen yläreunaan lisätään alapinta räystäslinjalta syvennykseen (muuten katto jäi raon päälle). Seinät skaalautuvat aina maasta räystääseen (build_wall: sc = seinän korkeus / rivien summa), joten kerrosluku, ikkunakorkeus ja syvennykset eivät muuta seinän korkeutta.
- **11.35 Yrjönkatu-tila + Teljäntorin sisäpiha:** Yrjönkadun katujulkisivut tarkistettu, EI vielä valmis: Sokos (Y12E, epätarkka SV-kuva),
  Kauppahalli (Y07E/Y08E), 107 aumakatto, 109 kulmaparvekkeet. Teljäntori 216: katusivut (Yrjönkatu, Antinkatu) vastaavat hyvin.
  Sisäpiha: SV:ssä vain käyttäjän 360-kuva pysäköintikannelta (sijainti/suunta epävarma) – siinä valkoiset toimistosiivet, pitkät
  harmaansiniset ikkunanauhat ja pyöreä porrastorni. Lisätty zones.py SPEC[216] (nauhaikkunat, fit). Paikallinen c067 OK.
  Live-pelissä 215:n (Kansankulma) itäpääty kannen yllä musta – paikallisessa c052-leivonnassa ei mustaa → korjautuu `city 64 c`:llä.
  Kesken: Sampotalon (238) pihasivun pyöreä porrastorni ja ruskea ylin kerros; kannen korkeus (LoD2 ~6,8 m) vs roofAt 3,1 m.
- **12.00 Yrjönkatu 20, Porin Talo (582):** SV:n tarkempi kuva → 2015 "pikseli"-kasettiverhous (lila-/sinharmaat ja valkoiset kasetit eri
  syvyyksillä, kapeat kerroskorkeat ikkunat epäsäännöllisesti), turkoosi liikeotsa. zones.py `m_pixel` + `_ptUp`. Testileivottu c067.
- **Valtakatu (kesken, V00–V11 / 22 pistettä):** styles: 1336?, 1351 (ei Lyseo vaan okra 4 krs), 1308, 1311 (SPECK, ei kaaria), 1398, 1451
  (Valtakatu 24 ruosteenpunainen), 1514, 1535/1517 (Valtakatu 26: city.js-korkeus 3,8/7,5 m väärin → uusi styles-avain `hh` = 19,5/25,5 m,
  zones2.py lukee sen; kl0 testileivottu, nyt 6 krs tiilitalo lasiparvekkein).
- **Ajettava lisäksi:** `bake kl0 kl1 kivi0 karhu`, `city 64 c` (c067 Porin Talo + Teljäntori).
- **12.35 Valtakatu läpi (V00–V20):** lisäksi SPEC: 1581 Valtakatu 7 torni (valkoinen + oranssinpunaiset ikkunavälinauhat, kivi3 testileivottu),
  1603 Valtakatu 5 (hiekanbeige, ikkunanauhat), 1731 Valtakatu 6 (oranssinpunainen tiili, vaalea katutaso), 1729 harmaanruskea betoni,
  1720 kulmapaviljonki (lasi + tummanvihreä otsa; oli umpiseinä). SPECK 1574 Valtakatu 9 (1-krs, ei kaaria; kivi1 testileivottu).
  1451 (Karhukortteli, Valtakatu 24): SV näyttää ruosteenpunaiset/harmaat levyt, mutta KARHU-värit ovat omistajan hyväksymät → ei muutettu, kysytty.
  Uusintakierrokselle: Kaupungintalon korttelin Valtakadun puoli (1294: SV:ssä 1-krs okra?), Kauppahalli/Y07–08, Sampotalon pihasivu.
- **Ajettava:** `bake kivi0 kivi1 kivi3 kl0 kl1 karhu tori0 tori1 tori5 --samples 64` + `city 64 c`.

## SEURAAVA ISTUNTO – ALOITA TÄSTÄ (handoff 13.11.2026 klo 12.10)
- **Tila:** Antinkatu ✔, Yrjönkatu ✔ (paitsi uusintakierroksen kohdat), Valtakatu ✔ (V00–V20; V21 = Kauppatorin pää, aiemmin katsottu).
  Seuraavaksi **Itsenäisyydenkatu**, sitten Isolinnankatu, Pohjoisranta/Eteläranta, Hallituskatu, Gallen-Kallelankatu, Mikonkatu, Liisankatu,
  Otavankatu/Annankatu/Katariinankatu, Länsipuisto, Itäpuisto → uusintakierros → Riihiketo ja Isosanta → seinämaalaukset viimeisenä.
- **Avoin kysymys käyttäjälle:** Valtakatu 24 (1451, Karhukortteli) – SV:ssä ruosteenpunaiset/harmaat levyt, KARHU-värit omistajan hyväksymät. Muutetaanko?
- **Uusintakierroksen lista:** 1294 Kaupungintalon kortteli Valtakadun puoli (SV 1-krs okra?), Kauppahalli Y07–Y08, Sampotalo 238 pihasivu
  (pyöreä porrastorni, tumma ylin kerros; kansi LoD2 ~6,8 m vs roofAt 3,1 m), 107 aumakatto, 109 kulmaparvekkeet, Eteläranta 4 alaikkunat,
  116 erkkerit, 163/1726 värit, viisteiden kulmaovet.
- **Työkalut** ovat nyt repossa `audit/`-kansiossa (aiemmin vain työtilassa): `street.py <Katu>` (katujen talolista), `nb.py a b`
  (selainerä views.jsonista: peli `window.__shot(x,y,h)` + Street View), `rshot.py` (leivotun glb:n renderöinti Blenderillä),
  `diag3.py <lohko>` (mustat laatat), `valta_notes.txt` (Valtakadun havainnot). Polut olettavat työtilan /home/claude-rakenteen.
- **Huom. selaimesta:** max 2 näkymää / erä (50 s raja), aloita erä `resize_window 1280x720`:lla (emulointi nollautuu virheiden jälkeen).
  Pelin `__shot` määritellään välilehteen uudelleen, jos sivu ladataan uudestaan (koodi: `audit/shot.js` – liitä se pelin välilehteen javascript_toolilla; peli: https://porin-kopterilento.onrender.com/?r=1).
- **Ajamatta (käyttäjä):** commit+push, sitten `bake kivi0 kivi1 kivi3 kl0 kl1 karhu tori0 tori1 tori5 kivi2 kivi4 kivi5 tori2 tori3 tori4 p1
  bepop isokarhu promenadi uima karhu --samples 64` ja `city 64 c`, collect → PR → merge.

### Street View -vertailun menetelmä (sama kuin Antin-, Yrjön- ja Valtakadulla)
1. **Pisteet:** `audit/`-tyyliin – kadun keskilinja city.js:n `r`-teistä (`n` = kadun nimi, koordinaatit jo metreinä), piste 40 m välein
   (ensimmäinen 8 m alusta). Jokaisesta pisteestä kaksi näkymää: kadun suunta −55° (A) ja +55° (B) → näkee molempien puolten julkisivut viistosti.
   lat = y/111437 + 61.486, lon = x/53278 + 21.796. Tulos `views.json` ({k,x,y,h,lat,lon}); Valtakadun generointi oli tämä (ks. views.json).
2. **Kuvaparit:** `python3 audit/nb.py a b` tulostaa browser_batch-listan (peli: `__shot` + kuvakaappaus 0,4; Street View:
   `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=LAT,LON&heading=H&pitch=12&fov=90`, odotus 5 s, kuvakaappaus 0,4).
   Aloita erä `resize_window seed 1280×720`. Max 2 näkymää/erä. Peli välilehdellä `tab-2`, Street View `seed`.
3. **Vertailu:** jokaisesta parista: väri, kerrosluku/korkeus, ikkunatyyppi (punched/ribbon/kaaret), katutaso (näyteikkunat), parvekkeet,
   materiaali (tiili/rappaus/levy/puu). Tunnista talo tarran id:stä + `street.py`:n listasta; epävarmassa tapauksessa katso jalanjälki
   (city.js p/10) suhteessa kameraan. Muistiinpano `audit/<katu>_notes.txt`.
4. **Korjaus:** pelkkä väri/kerrosluku/materiaali → `styles.json` (w, f, k, hh = korkeus jos city.js väärin ja ei LoD2:ta); klassinen talo
   ilman kaaria tms. → `kivi.py SPECK[id] = classic_spec(...)`; moderni julkisivu → `zones.py SPEC[id]` (lay + fit). Merkitse `"sv": 1`.
   Muista: KARHU-värit (kivi.py) omistajan hyväksymät, Airionkulma 603 valokuvajulkisivu pidetään.
5. **Tarkistus:** leivo lohko paikallisesti (`python3 kivi.py <lohko> 4` tai city-lohkolle build_and_bake) ja renderöi sama kuvakulma
   `rshot.py`:llä (absoluuttinen tulostuspolku!) ennen kuin kirjoitat tiedostot kansioon. Live-peli näyttää korjaukset vasta Modal-ajon jälkeen.
- **Käyttäjän palaute 12.42 (kuva Liisankadun yltä, live-peli):** (1) 45° viisteet puuttuvat → live-leivonnat ovat ennen chamfer.py:tä
  (bl_c*.js 09.46, bl_kivi* 05.30) – korjautuu Modal-ajolla; tarkista sen jälkeen. (2) **Katos maassa** Teljäntorin/IsoKarhun välisellä
  pysäköintialueella (punaruskea matala "talo" vaalealla katolla) – EI vielä korjattu: etsi id (`street.py Liisankatu` / tarrat),
  tee siitä katos (katto pilareilla, ei umpiseiniä maahan). (3) Teljäntorin sisäpiha rikki → SPEC[216] tehty mutta c067 leipomatta Modalissa;
  lisäksi Sampotalon pihasivu ja kannen korkeus (LoD2 ~6,8 m vs roofAt 3,1) yhä korjaamatta – ensimmäinen tehtävä seuraavassa istunnossa.
- **13.11 chamfer-korjaus:** Modal-ajo kaatui 0/127 (`No module named 'chamfer'`): pipeline/porikit/jobs.py kopioi kiinteän listan
  HOMEen, muut blender/*.py menevät HOME/blender/. zones2.py lisää nyt `./blender` sys.pathiin. Uusia blender-moduuleja lisättäessä
  muista tämä (tai lisää ne jobs.py:n listaan rivillä 62). Tarkista aina lokin lopusta `done: N/N ok`.
- **Huom. tiedostojen kirjoitus kansioon:** device_commit_files kirjoitti kerran vanhan sisällön (outputs-kansion välimuisti) →
  käytä aina uutta tiedostonimeä outputsissa ja tarkista koko device_list_dirillä kirjoituksen jälkeen.

## JATKOSUUNNITELMA: realistisuus (kun talojen muoto ja värit ovat kunnossa; käyttäjä hyväksyi 13.11.2026)
1. **Ikkunaheijastukset (tärkein):** leivonnassa lohkoille lasimaski (gen.py tietää ikkunoiden paikat; erillinen kanava/tekstuuri
   samaan atlakseen). Pelissä lasikohtiin taivaan ympäristöheijastus Fresnel-painotuksella (vinosti katsottuna vahvempi) + auringon
   välähdys; kevyt shader, toimii selaimessa. Raskaampaa SSR:ää (toisten talojen heijastus) ei todennäköisesti kannata.
   Lasimaskin voi lisätä leivontaan jo aiemmin, jotta se on valmiina kaikissa lohkoissa.
2. **Värisävytys + ilmaperspektiivi:** ACES-tyyppinen sävykartoitus, hieno usva (kaukaiset talot sinertävät). Nopea.
3. **Normal mapit:** tiilen saumat, rappauksen karheus, peltikattojen saumat valossa 3D:nä (nykyisistä det_*.jpg-tekstuureista).
4. **Ikkunoiden sisustus:** verhot, valaistut/pimeät huoneet vaihtelevasti; yhdistyy yönäkymään (`night/`).
5. **Kuluneisuus:** sadevanat, räystäsliat, sokkelit (osin jo WEATHER-asetuksella).
6. **Katutason yksityiskohdat:** markiisit, kyltit, katukalusteet.
- **Käyttäjän palaute 13.24 (uusien leivosten jälkeen) – EI korjattu, tee ensimmäisenä:**
  1. **Teljäntorin läpinäkyvä seinä** (c067): seinä näkyy vain toiselta puolelta (yksipuolinen pinta / puuttuva seinä LoD2-kuoren ja
     pysäköintikannen kohdalla). Tarkista rshot.py:llä kannen tasolta (LoD2-katto ~6,8 m) ja build_lod2:n runs/cap-logiikka (zones2.py
     ~rivi 155–165: seinät katkaistaan cap-korkeuteen → kannen yläpuolinen seinä voi jäädä pois).
  2. **Katos maassa, kaksi kohtaa:** (a) Teljäntorin ja Promenadin välissä, (b) IsoKarhun ja Sokoksen välissä (pysäköintialueita,
     punaruskea matala "talo" vaalealla katolla). Etsi id:t (`audit/shot.js` + tarrat tai city.js-jalanjäljet), tee niistä katoksia:
     katto ~2,5–3 m pilareiden varassa, ei umpiseiniä (esim. SPEC kind 'canopy' / layout plain + open_ends, tai hide + oma katosmalli).
  3. Ratsula (221) näkyi vielä tiilenä klo 13.22 – todennäköisesti Render/välimuisti; tarkista uudesta c052:sta.
