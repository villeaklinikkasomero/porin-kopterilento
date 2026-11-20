# Porin kopterilento – siirto toiselle Claude-tilille (päivitetty 15.11.2026; UUSIN TILA: osio "15.11.2026 – ALOITA TÄSTÄ" aivan lopussa)

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

## 14.11.2026: Itsenäisyydenkatu Street View'ta vasten (toinen tili)
- Tarkastettu 19 taloa, korjattu styles.json (`sv: 1`): 1229/1230 Terveystalo (valkoinen + tummansininen nauha), 192, 796/794/805/800 puutalot
  (Itsenäisyydenkatu 15–19: vaaleankeltainen, valkoinen, siniharmaa), 1231 kerma 3 krs, 35 puutalo 1,5 krs, 223 okra, 199, 415 valkoinen+keltaiset
  paneelit, 7 keltainen, 665/1204/1206 uudisrakennukset (valkoinen/oranssi tiili/punatiili, tumma sokkeli), 634 vaalea tiili, 116 Antinlinna okra, 113 matala.
- Tarkastamatta: 585 (vanha linja-autoasema), 1207 (kuoressa).
- Leivottavat: city 64 c035,c036,c048,c063,c064,c076,c077,h085,h125.
- Teljäntorin läpinäkyvä seinä ja maahan jääneet katokset: ei vielä paikannettu (käyttäjältä odotetaan kuvakaappausta).
- Seuraavaksi: Mikonkatu, Liisankatu, Pohjoisranta/Eteläranta, Länsipuisto, Itäpuisto.


## 13.11.2026 ilta: Itsenäisyydenkatu tarkalla menetelmällä (kuvaparit 40 m välein, ±55°)
- Käyty I00–I12A (26/90 näkymää), muistiinpanot audit/itsenaisyys_notes.txt (pilvityötilassa; kopio keskustelussa).
- zones.py: SPEC[167] (lasitetut parvekepinot + liiketilat), SPEC[118] (Antinkatu 24, nauhaikkunat, lasitettu katutaso).
- styles.json: 4, 119, 121, 166, 167, 512, 1228, 115 (uusi).
- Paikallisesti bakettu ja tarkistettu: c048, c063, c064, h074 → Modal: `city 64 c048,c063,c064,h074`.
- 600 Bepop ja 601 (It.k 35): valkoiset nauhaikkunat, lasiset liiketilat, ei c-lohkoissa (landmark) → kesken.
- Live-peli näyttää vanhaa bakea: vertaa SV:tä styles.jsoniin / paikalliseen bakeen.
- Jatko: I12B → I44, sitten Isolinnankatu jne.


## 14.11.2026 – ALOITA TÄSTÄ (Kivi-Pori, Raatihuone, rautalanka, mäkiset kadut)
Tarkemmat havainnot: `audit/kivipori_notes.txt` (lopussa TYÖOHJE: rautalanka-vertailu) ja `audit/kivipori_kortteli_eteläranta_antinkatu.txt`.

### Uusi pääsääntöinen työtapa: rautalanka-vertailu (korvaa kuvaparit ±55°)
1. Street View -kuva selaimella tunnetusta paikasta: `https://www.google.com/maps/@LAT,LON,3a,90y,SUUNTAh,KALLISTUSt`
   (`90t` = vaakasuora, `102t` = 12° ylös). **`90y` on PYSTYSUUNTAINEN kuvakulma.** Lue kameran todellinen paikka URL:sta latauksen jälkeen.
   Viewport 1280×720 → kuvakaappaus 800×450.
2. Peli samasta paikasta, suunnasta ja kuvakulmasta: `tools/rautalanka/gshot_sv.mjs` (näkymät JSON: k, x, y, h, p, fov 90, ch 2.5).
   Skripti odottaa, että korttelin bake on latautunut (`window.__bl`) – muuten kuvassa on karkea varaseinä (kehyksettömät ikkunat).
3. `tools/rautalanka/ov.py SV.jpg peli.jpg ulos.jpg`: mallin reunat punaisena SV-kuvan päällä. Lue erot: kerroskorkeudet,
   ikkuna-akselit, räystäs, sokkeli, värialueiden osuudet (mittakaava = seinän tunnettu pituus / pikselit).
4. Korjaa SPECK-mitat, bakea paikallisesti (`python3 kivi.py kivi2 8`), toista kunnes reunat osuvat. Tunnista talo osoitteella ja
   `work/svlabel.py`-projektiolla ennen muutosta (useita väärin tunnistettuja taloja 14.11: 1561, 1562, 1563, 1566).
- **Opit:** LoD2-seinän korkeus sisältää usein ullakkofriisin (1559: 12 m = 4,7 kivi + 4,8 oranssi + 2,5 ullakko) – älä jaa sitä kerroksille.
  Modal-bake ei sisällä puskemattomia muutoksia – tarkista tiedoston aika ennen vertailua. Pelin kuvausskripti voi ottaa kuvan ennen latautumista.

### Mäkiset kadut: talo suorassa, kivijalka vinossa (uutta 14.11)
- Ennen pelin maastoshader nosti jokaista pistettä erikseen → koko talo kallistui rinteessä.
- Nyt bake kirjoittaa `bl_*.js`:ään `export const shells` (talojen ääriviivat) ja lisää jokaisen seinän alle 2,6 m kivijalkahelman (`kivi.py skirt`).
  Peli (`index.html liftBlock/shellAt`) nostaa jokaisen talon yhdellä korkeudella (korkein maasto talon alla), kolmio kerrallaan (keskipiste ratkaisee).
  Käytössä vain lohkoissa, joiden bl-tiedostossa on `shells` (nyt kivi2, kivi4); muut toimivat entiseen tapaan kunnes ne bakeataan uudelleen.
- Saman LoD2-kuoren erilliset talot: `SHELL_SPLIT` kivi.py:ssä (1560 / 2 Antinkatu, 1566 / 4 Antinkatu).
- Graniitti vaalennettu `#5b5752 → #7a7771`.

### Uudet työkalut kivi.py / gen.py
- `cut_walls(i, p0, d)` leikkaa LoD2-seinät pystytasolla (kaksi taloa samassa kuoressa → `SPECK[i]['alt'](x, y)` valitsee specin).
- `lower_eave(i, test, z_eave, depth)` laskee matalan talon katuseinän räystääseen + lappeen; poistaa vanhan katon irtopalan.
- `corner_tower(...)` (Heinen talon kulmatorni), `extra=[...]` specissä.
- `classic_spec`: `ground/first/top` dictit (gwall = maantason oma väri, plinth_h, sill, wh, ww, wh_fixed, dw = oven leveys, door = oven materiaali,
  basement=False, blank, wall), `lay=dict(nf, gh, frieze, cols)`. nf=1 + frieze → yksi kerros + ullakkoikkunarivi.
- Sarakekoodit: `W` ikkuna, `D` ovi (yläkerroksissa ikkuna; `first=dict(balcony=True)` → parvekeovi + kaide viistokulmissa), `G` kaariportti,
  `X` maantasossa umpiseinä / yläpuolella ikkuna, `N` umpi, `P` ikkunapari, `S` liiketila.
- styles.json: uusi avain `pl` (sokkelin väri).
- `pipeline/modal_app.py`: `landmarks <nimi>` tekee nyt bl_<nimi>.js:n (uusi `landmark`-funktio).

### Raatihuone ja AI
- `lm.py raati`: kellotorni keltainen, korkeampi, parveke ja rautakaide, kellokerros, kellomainen kuparikatto + lyhty, alkuperäinen katon väri.
  Yhteinen AI-kuparikattomateriaali myöhemmin.
- AI-julkisivut: `pipeline/aitex.py` (Modal SDXL + canny ControlNet), syötteet `tex/ai_in/*.png + .json` (englanninkielinen materiaalikuvaus).
  Paras: ControlNet 0.55 + strength 0.95 + värilukitus (`pipeline/aiface/lock.py`) + projektio (`proj2.py`). Projektio katoaa rebakessa →
  tarvitaan pysyvä bake-jälkeinen vaihe (pygltflib puuttuu requirementsistä). AI-syötteeksi vain omat renderit + teksti.

### Tila ja avoimet (Eteläranta–Antinkatu–Hallituskatu–S. Palmgreninkatu -kortteli)
- Rautalangalla mitattu: 1573 (4 Antinkatu, räystäs 5,6, ovi 3. akselilla, 6 ullakkoikkunaa), 1562 (1 krs korkealla sokkelilla), 1559 (6 Eteläranta).
- Avoimet: 1573 viimeinen ikkuna ~1,4 m väärässä (tasajako) ja tumma katon jäänne yllä; 2 Antinkadun harmaa loiva peltikatto ja liian korkea sokkeli;
  1559 keskikaari pienempi kuin ovet; 1566 portti; 8385 liiketilat + porrastorni; 1286 keskirisaliitti; pohjoisjulkisivut bakessa liian tummia.
- Seuraavaksi: koko kortteli rautalangalla, sitten Hallituskatu–Valtakatu ja muut Kivi-Porin kadut (Yrjönkatu, Teatterikatu, Otavankatu, Annankatu,
  Katariinankatu, Vapaudenkatu).
- **Ajamatta (käyttäjä):** commit + push, sitten `porikit run` → `bake kivi2 kivi4` (paikalliset 8 näytteen baket ovat jo kansiossa);
  myöhemmin muut kivi-lohkot uudelleen, jotta vino kivijalka (shells + skirt) tulee niihinkin.


## 15.11.2026 – ALOITA TÄSTÄ (viikon tauko; jatko toisella tilillä)
Lue ensin tämä osio, sitten 14.11-osio yllä ja `audit/kivipori_notes.txt` (lopussa korttelikohtaiset havainnot).

### Pysyvät säännöt (käyttäjä)
- Vastaa suomeksi ja lyhyesti. Näytä muutoksesta aina kuva (peli + rautalanka). Älä ole tyytyväinen ennen kuin rautalanka osuu.
- API-avaimia tai GitHub-salaisuuksia ei käsitellä. Push ja Modal-ajot tekee käyttäjä (GitHub Desktop / GitHub Actions → porikit run).
- Street View-, kaupungin- ja Y-pakin kuvia EI viedä GitHubiin eikä peliin. Niistä luetaan vain värit, materiaalit ja muodot.
  SV:tä sisältävät rautalankakuvat saa tallentaa vain kansioon `Claude outputs/` (gitignore).
- Lukittuja ei muuteta kysymättä: KARHU-värit (kivi.py), Airionkulman 603/602/604 valokuvajulkisivut.
- Säästä rahaa: Modalissa ajetaan vain muuttuneet lohkot; kokeilut bakeataan paikallisesti 8 näytteellä.
- Tunnista talo AINA osoitteesta ja projisoidusta ID:stä (`tools/rautalanka/svlabel.py`) ennen kuin muutat sitä.
- Lataukset vain luvalla, tiedostojen poisto käyttäjän koneelta vain luvalla.

### Rautalanka – miten se on rakennettu (tools/rautalanka/)
Idea: Street View -kuva ja peli kuvataan TÄSMÄLLEEN samasta paikasta, suunnasta, kallistuksesta ja kuvakulmasta. Pelikuvan reunat
piirretään punaisena SV-kuvan päälle. Kun punaiset viivat osuvat oikean talon ikkunoihin, räystääseen ja sokkeliin, malli on oikein.

1. **SV-kuva paikasta, jonka koordinaatit tiedät.** Laske pelikoordinaateista lat/lon:
   `lon = 21.796 + x/53278`, `lat = 61.486 + y/111437` (peli: `x = (lon-21.796)*53278`, `y = (lat-61.486)*111437`; city.js `p` on desimetreinä).
   Avaa selaimessa (sovelluksen sisäinen selain, viewport 1280×720):
   `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=LAT,LON&heading=SUUNTA&pitch=KALLISTUS&fov=90`
   – tämä muoto hyppää lähimpään panoraamaan (pelkkä `@LAT,LON,3a,...`-URL jää usein mustaksi).
   Odota 4–5 s, lue panoraaman TODELLINEN paikka osoiteriviltä (`@61.4891517,21.7963296,12a,80y,200h,95t`) ja ota kuvakaappaus
   (scale 1 → 800×450, scale 0.6 → 480×270). **`80y`/`90y` on PYSTYSUUNTAINEN kuvakulma**, `95t` = 5° ylöspäin (`90t` = vaaka).
2. **Näkymä JSON:iin** pelikoordinaateissa (esimerkki `tools/rautalanka/examples/hallituskatu_etela.json`):
   `{"k":"H1576b","x":17.5,"y":351.4,"h":200,"p":5,"fov":80,"ch":2.5}` – x,y = panon todellinen paikka, h = suunta, p = kallistus (95t → 5),
   fov = pystykulma (y-luku), ch = kameran korkeus maasta (SV ≈ 2.5 m). `back` (m) siirtää kameraa taaksepäin.
3. **Pelikuva:** `ZONE=kivi1 node tools/rautalanka/gshot_sv.mjs index.html ulos/ näkymät.json` (paikallinen `python3 -m http.server 8765`
   pelikansiossa; playwright + swiftshader). Skripti siirtää helikopterin paikalle, odottaa katulohkot ja korttelin baken (`window.__bl`
   sisältää ZONE-nimen) ja asettaa kameran: `z = TZs(x,y) + ch`. Ilman odotusta kuvaan jää karkea varaseinä.
4. **Rautalanka:** `python3 tools/rautalanka/ov.py SV.jpg peli.jpg ulos.jpg` → ylhäällä pelikuva, alhaalla SV-kuva + mallin reunat
   (Pillow FIND_EDGES, kynnys 40, punainen). Kaikki kerralla: `ZONE=kivi1 tools/rautalanka/runov.sh näkymät.json koonti.jpg H1576b:/polku/sv.jpg ...`
5. **ID:t kuvaan:** `python3 tools/rautalanka/svlabel.py sv.jpg LAT LON SUUNTA KALLISTUS ulos.jpg [id...]` piirtää city.js-pohjat ja ID:t SV-kuvaan.
   Toinen variantti `wire.py` projisoi kivi.py:n LoD2-seinät ja julkisivurivit suoraan (ei tarvitse pelikuvaa).
6. **Diagnostiikka, kun pinta on outo:** `bake_faces.py bl_kivi1.js xmin xmax ymin ymax [zmin]` listaa baken kolmiot (korkeus, normaali, väri);
   `scene_meshes.mjs X Y zone` kertoo mitkä pelin meshit peittävät pisteen (Blender-lohko / maamerkki / ilmakuvakatto / varaseinä).
   Esimerkki: 7 Hallituskadun "punainen katto" oli 1 m kaistale seinää räystäslistan yläpuolella (LoD2-räystäs heitteli 6,0–7,0 m).
7. **Korjaus → paikallinen bake → uusi rautalanka**, kunnes osuu: `python3 blender/kivi.py kivi1 8` (≈140 s; kirjoittaa `out/bl_kivi1.js`),
   maamerkit `python3 blender/lm.py kaupungintalo` + `python3 tools/lm_to_js.py kaupungintalo` (`lm.py KEY still` = nopea esikatselukuva).

**Rautalangan lukeminen (esimerkit 15.11):**
- `Claude outputs/rautalanka_esimerkit/rautalanka_o13.jpg` (vain paikallisesti, sisältää SV:tä): 7 Hallituskatu. Ensin malli piirsi 4 kaari-ikkunaa,
  beige vaakaurat → SV:ssä 5 suorakaideikkunaa valkoisin pielin, punainen rappaus, 3 tuuletusaukkoa, 2 piippua. Punaiset ikkunareunat osuvat nyt pieliin.
- `rautalanka_oa4.jpg`: Antinkatu 5. Malli 6 akselia + ovi → SV 8 akselia, ei ovea, isot kaari-ikkunat matalan sokkelin päällä. Mittakaava = seinän
  pituus (LoD2 24,6 m) / pikselit → bw 3,07 m. Hallituskadun pääty 11,6 m = 3 akselia (alt-spec bw 3,6).
- `rautalanka_o12.jpg`: Kaupungintalo. Malli näytti 2 kerrosta, koska kivinen pohjakerros oli kadun alla (maamerkki seisoi z=0:ssa, maasto 6 m).
- Pelkät pelikuvat samoista näkymistä: `tools/rautalanka/examples/peli_*.jpg` (saa olla GitHubissa).
- Lue aina: akselimäärä, ikkunan muoto (kaari/suora/pari), kerrosrajat, räystään korkeus, sokkelin korkeus, ovien paikat, värialueet.
  Ihmissilmä (käyttäjä) huomaa: väärä materiaali (rappaus vs tiili), irralliset muurit/portit, katon väri, ullakkoikkunat.

### Tehty 15.11.2026
- **Ilmakuva:** `ot/` 88 ruutua MML 2025 (0,5 m). 27 ruutuun, joissa ei muutosta, palautettu vanha tarkka 0,25 m kuva värisovitettuna
  (Lab-keskiarvo/hajonta MML:ään) → saumat eivät näy. Muuttuneet (Karjaranta/Puuvilla, Eteläranta, Kirjurinluodon länsiosa, uudisrakennukset,
  hakkuut) ovat MML 2025. Työkalut `tools/ot_tilefrac.py` (muutososuus ruuduittain) ja `tools/mk_ot_mix.py` (pikselisekoitus, hylätty: laikukas).
  Tarkempaa avointa ilmakuvaa ei löytynyt (MML avoin 0,5 m). Porin kaupungin oma ortokuvarajapinta (vanhojen 0,25 m ruutujen lähde) – uudempi vuosi tarkistamatta.
- **Pelin `index.html`:** (1) maamerkit (lm.py-mallit) seisovat yhtenä kappaleena maaston keskikorkeudella jalanjälkensä alla (`noT` + `TZs`-keskiarvo);
  aiemmin maastoshader nosti ne pisteittäin ja Kaupungintalon pohjakerros jäi kadun alle. (2) Rapatut punaiset talot: shellin `nb:1` → `tNB`-attribuutti
  → `brickify` ei piirrä tiilikuviota. Bakessa `MT(väri, 'plaster')` estää gen.py:n värin perusteella tehdyn tiilitunnistuksen (r > 2,3·g).
- **kivi.py uutta:** `facade_bits`-osat `chimney` (s, syvyys, z0, z1, leveys), `wall` (irrallinen muuri 3 m paloina), `archgate` (kaariportti),
  `vents` valinnaisella koolla (ullakkoikkunat valkoisin kehyksin). Spec-avaimet `nobrick`, `roofmat`. Sisäpihan kerrosmäärä ≤ kadun puolen
  kerrosmäärä (`fit`: nst = lay.nf / styles `f`). `RAW[i]`-muokkaus suoraan (1576 räystäs tasattu 6,3 m).
- **Korjatut talot (rautalanka):** 1576 (7 Hallituskatu, punainen rapattu 1 krs), muuri 1576–Kaupungintalo, 1575 (Antinkatu 5 / Hallituskatu kulma, 8+3 akselia,
  ullakkoikkunat, kaariportti 1575–1576), Kaupungintalo (lm.py: 3 krs, harmaa kivinen pohjakerros, buffi tiili punaisin vinoneliöin, gotiikkaparikkunat
  terävän kaaren alla `gothic_pair`).
- **Kaupungintalossa vielä:** pääovi puuttuu, pohjakerros hieman liian korkea (malli 1,1–6,2 m), koristeelliset ikkunakehykset yksinkertaisia.

### Tila: Kivi-Pori
- Rautalangalla tarkistettu ~23 / 109 rakennuksesta: Eteläranta–Antinkatu–Hallituskatu–S. Palmgreninkatu -kortteli (19) +
  Hallituskadun eteläpuoli S. Palmgreninkatu–Antinkatu (1576, muuri, 1575, Kaupungintalo).
- **Seuraavaksi:** Antinkadun itäpuoli (kivi3: 1578, 1579, 1583, 1585, 1586, 1603, 1604, 1716, 1581 Valtakatu 7 torni), sitten kivi1 loput
  (1292, 1293, 1294, 1296, 1341, 1574, 1577, 1622), kivi0 (Teatterikatu–Otavankatu), kivi5, kl0, kl1, p1.
- Avoimet vanhat: 1573 viimeinen ikkuna ~1,4 m; 2 Antinkatu katto + sokkeli; 1285 viistokulman parveke; 8385 liiketilat + porrastorni;
  1286 keskirisaliitti; pohjois-/länsiseinät bakessa liian tummia.

### Ajamatta (käyttäjä)
1. Commit + push (kaikki yllä oleva on jo kansiossa; paikalliset 8 näytteen baket bl_kivi1.js, bl_kivi4.js, bl_kaupungintalo.js mukana).
2. Modal `porikit run`: `bake kivi0 kivi2` (uusi sisäpihan kerroslogiikka + shells), myöhemmin `bake kivi1 kivi3 kivi4 kivi5 kl0 kl1 p1` 64 näytteellä.
   Kaupungintalolle: `landmarks kaupungintalo` (paikallinen bake on jo kansiossa).
3. Ilmakuvat (`ot/`) ovat valmiina, ei Modal-ajoa.

### Ympäristö uudella tilillä
- Tarvitaan: Blender Python (`bpy`) paikallisesti bakeihin, node + playwright (polku `gshot_sv.mjs`:n alussa `/home/claude/.npm-global/...` – vaihda),
  python3 + Pillow + numpy + shapely + scipy (+ rasterio/pyproj ilmakuviin). Data: `/home/claude/pori/` = repon kopio (city.js, terrain.js, styles.json,
  lod2.js, orto.jpg); `svlabel.py` lukee `/home/claude/pori/city.js`.
- Paikallinen bake-tulos: `/home/claude/out/bl_<lohko>.js` → kopioi repon juureen.

### Sovittu jatkosuunnitelma: AI-fotorealismi (käyttäjä hyväksyi 15.11.2026)
1. Ensin muodot ja värit rautalangalla koko Kivi-Poriin (geometria = kerroksellisuus, syvennykset, listat, ikkunat).
2. Sitten AI vain **seinämateriaaliksi** yhdessä korttelissa (testi: kivi2), ennen/jälkeen-pelikuvat:
   - syöte = oma render + teksti (ControlNet pitää ikkunat ja kerrosrajat paikallaan),
   - lasit ja karmit maskataan pois AI-kerroksesta (mallin omat, heijastus pelissä),
   - AI:lta vain materiaali (rappauksen rakeisuus, tiilen saumat, likaantuminen), AI-kuvan omat varjot vaimennetaan – valo tulee bakesta,
   - pysyvä bake-jälkeinen vaihe (pygltflib Modalin requirementsiin), ettei projektio katoa rebakessa.
3. Rautalanka toimii edelleen tarkistuksena (mittaa geometriaa, ei tekstuuria).

### Omistajan vikalista 15.11.2026 ilta (kuvat: `Claude outputs/vikalista_15_11/`, vain paikallisesti – sisältää SV:tä)
Korjaa nämä ENSIN, ennen Antinkadun itäpuolta. Tunnista jokainen talo ID:llä (svlabel.py) ennen korjausta.
1. **`1_linna_irtokatot.png`** – Hallituskatu / paikka "Linna" (city.js places: Linna x 28, y 211), suunta KO, korkeus 17 m:
   vasemmalla keltaisen talon läpi pistää tumma kalteva kattolaatta + kattolaatikko; oikealla talon katto leijuu mustan avoimen
   rungon päällä (seinät jäävät katon alapuolelle). Todennäköisesti eri talojen eri nosto (shells/liftBlock) tai vanha bake ilman shellejä (kivi3 14.11).
   Etsi paikka: renderöi `gshot_sv.mjs`-näkymiä x 0–140, y 200–330, h 45, ch 20.
2. **`2_taidemuseo_varit_puuttuu.png`** – Taidemuseon (lm museo −264.8, 455.9 / taidemuseo −94.8, 462.6) lähellä: talot valkoisia/harmaita
   ("taitaa puuttua värit"). Tarkista styles.json w-arvot ja onko `m:1` (automaattinen) → SPECK ilman väriä → KIVIP-hash. Kivi0-lohko.
3. **`3_1576_kulma_puuttuu.png`** – 7 Hallituskatu (1576) itäpää porttikäytävän vieressä: kulma puuttuu (katto/seinä porttimuurin kohdalla).
   Syy luultavasti 15.11 räystään tasaus `RAW[1576]` (5,5<z<7,4 → 6,3) tai porttimuurin `wall`-pala 1575 extrassa. Tarkista bake_faces.py:llä.
4. **`4_sv_1287_kermanvalkoinen.png` + `4_peli_1287.png`** – 12 Hallituskatu / S. Palmgreninkatu (1287): oikeasti kermanvalkoinen, harmaa
   loiva katto, 6+ piippua, maantasossa suorat ikkunat ja sisäänkäynnin lippa, ullakkoikkunat räystään alla. Pelissä harmaa ja liian
   tumma, maantason kellari-ikkunat. → väri vaaleammaksi/lämpimämmäksi, basement=False, lippa, piiput (facade_bits chimney).
5. **`5_sv_1286_portti7.png` + `5_peli_1286.png`** – 7 Hallituskatu (1286, lohenpunainen 3 krs): pihaportti "7" – vaalea rapattu
   kaariportti + pieni kaariovi + muuri talon länsipäässä (kivi.py `wall` + `archgate`), yläkerran ikkunoissa otsalistat,
   valkoinen rustikoitu sokkelinauha, 2 isoa piippua. Pelissä portti puuttuu.
6. **`6_museo_katto_irti.png`** – Satakunnan Museo (lm museo): katto irti ja etuosa liian matalalla. SYY: 15.11 maamerkkien
   yhden kappaleen nosto (index.html track). KORJATTU 15.11 ilta: yhden kappaleen nosto vain `LM_ONE = {'kaupungintalo'}` – tarkista pelissä.

#### Vikalistan tila 16.11.2026
- 3 (1576 kulma): räystään tasauksen jälkeen kulma ja lonkka kunnossa – omistaja tarkistaa.
- 4 (1287): räystäs 1,6 m liian korkea → squash(1287, 8.5, 0.15); väri lämpimämpi #e6d9bb. Rautalanka osuu.
- 5 (portti 7): 1286–1287 väliin kaariportti, sivupilarien kaariovet, matala muuri (kivi.py SPECK[1286]['extra']). Rautalanka osuu.
- Irralliset muurit/portit saavat oman nostonsa (`WALL_SHELLS` → shells, `zt` = vain muurin korkeuteen asti; index.html shellAt(S,x,y,z)).
  Ilman tätä muuri vääntyi rinteessä kolmio kerrallaan ja viereisen talon räystäspala nousi irti.
- 1 (Linna/Antinkatu): 1563 Antinkadun puoli KELTAINEN (omistaja 16.11; vanha SV näytti valkoista). 1573:n päällä leijunut 1566:n katto
  leikattu 6,2 m:iin `_low_strip(1566, 1573, 6.2)` + litteä katto. Omistaja: "oikealla rakennus liian matala, kun katto kelluu" – tarkista näkymä
  (`Claude outputs/antinkatu_nyt.jpg`), takana näkyy vielä 1566:n kaltevia kattopintoja ja 1572:n viereinen keltainen pala.
- 2 (taidemuseon lähellä värit): todennäköisesti 1287 (näytti valkoiselta) – väri korjattu; tarkista muut.
- Sillat: kannet pilkottu ≤ 3 m paloiksi (index.html), seuraavat maastoa. Porinsilta (Blender-malli) ennallaan.

#### 16.11.2026 jatko (kivi3 / Antinkatu, Hallituskatu, Valtakatu)
- Uudet kivi.py-työkalut: `_low_strip(i, j|None, zc, extra=polygon)` (talo j toisen kuoren sisällä → kuoren seinät/katot leikataan zc:hen, oma litteä katto),
  `_hand_over(src, dst, strip, moves)` (kaistale kuoresta toiselle talolle, jotta ulkonäkö jatkuu samana), facade_bits-osat `box`, `spire`, `irongate`, `canopy`.
  Vapaat muurit/portit: `WALL_SHELLS` (zt = korkeusraja) + index.html `shellAt(S,x,y,z)`.
- Korjattu rautalangalla: 1573 Antinkatu 4 (vaakasuora räystäs, 5 akselia, portti 1573–1572 rautaportteineen), 1287 kulmaovi+lippa, portti "7" 1286–1287,
  1563 Antinkadun puoli keltainen (omistaja), 1578 Antinkatu 6 matala okra (oli moderni 4 krs), 1604 jugend (pihaportti, ovi, porraspääty, 2 suippotornia),
  1580 (1960-l. tummanvihreä nauhaikkunatalo 1604:n kuoresta erotettu, umpinainen pääty), 1716 matala liikepaviljonki, 1581 Valtakatu 7 torni
  (kuparinvihreä kaakeli ilman ikkunoita Antinkadulle, lasitetut kulmaparvekkeet, valkoiset pilarit), 1579 Hallituskatu 6 (5 krs + avoin pilarikerros,
  vaalea nauhajulkisivu, päättyy oikeaan kohtaan; keltainen 1578 jatkuu siihen asti), 1603 Valtakatu 5 (5 krs liiketilojen päällä).
- Seuraavaksi: kivi3 sisäpiha (1585, 1586), sitten kivi1 loput (1292–1296, 1341, 1574, 1577, 1622), kivi0, kivi5, kl0, kl1.


## 17.11.2026 ilta: keskustan heittävät ikkunarivit (aloitus Isolinnankatu)
- **Syy:** build_wall venytti jokaisen seinäpätkän rivit omaan räystääseensä (z0..z1). LoD2-seinien yläreunat vaihtelevat samassa talossa
  (esim. 656: 19,6 / 22,2 m; 609: 21,5 / 24,4 m) → samat kerrosrivit eri korkeudella → rivit hyppäävät kulmissa ja seinäpätkien välillä.
- **Korjaus (gen.py + zones2.py + city.py):** `zones2.GRID` (city.py: päällä, `PORI_GRID=0` pois). build_lod2 laskee talolle päärääystään
  (maaseinien pituuspainotettu mediaani) → layout `grid=(0, HREF/rivien summa)`. build_wall pitää rivit absoluuttisilla korkeuksilla:
  matalampi seinä päättyy umpinauhaan, korkeampi saa räystäsnauhan, alemman katon päällä oleva seinä jatkaa samoja kerroksia.
  Ei koske specejä, joilla on fit/fitw/runalt/nogrid (Kivi-Pori ja käsilohkot ennallaan). Debug: `GDBG=1`.
- **Pelin bugi korjattu (index.html streamUpdate):** uudet bake-tiedostot alkavat rivillä `export const shells = ...`; striimaus luki base64:n
  ensimmäisestä lainausmerkistä → parse epäonnistui → lohko jäi pelin tasaisiksi seiniksi (c039 nyt pelissä). Nyt luetaan `export default`,
  ja shells → liftBlock kuten nimetyissä lohkoissa. ILMAN tätä kaikki tämän päivän koodilla leivotut c-lohkot näkyisivät tyhjinä.
- Paikallinen koepoltto tarvitsee tekstuurit: `ln -s /home/claude/pori/blender/tex /home/claude/tex` (muuten tiili puuttuu).
- **18.11 aamu:** (1) Sokoksen ja IsoKarhun välissä maassa ollut vaaleanvihreä laatikko = vanha bl_h100 (leivottu ennen kuin
  kävelysilta 1243 sai `lift`-merkinnän; pelin bl_h100:n origo 153.3,-270.4 ≠ nykyinen jako). Uusi h100-poltto poistaa sen.
  city.py house_spec.gable_ends kaatui LoD2-taloihin (pts None) → h-lohkojen poltto kaatui; korjattu.
  (2) 1219 Itäpuisto 1 / Isolinnankatu (SV): ikkunaton 2-kerroksinen jalusta + valkoiset taidepaneelit, yllä 6 krs: eteläosa beige
  rappaus, pohjoisosa tummansininen levy + tiheä ikkunajako + lasitetut kulmaparvekkeet. zones.py SPEC[1219], uusi moduuli `artpanel`,
  itäseinään lisätty piste (1744,-715). Avoinna: sinisen osan katto ehkä matalampi, Kauppahallin väri pelissä keltainen (todellisuudessa vaalea).
- **18.11 klo 9–10, Isolinnankatu itäpuoli rautalangalla (11 SV-kuvaa, massat osuvat, julkisivut korjattu):** zones.py SPEC 1741 (valkoinen,
  korkeat kapeat ikkunat), 1617 (tiili + ikkunanauha), 656 (kulmien ulokeparvekkeet, tiilinen katutaso), 607 (valkoinen levy, liiketila),
  606, 608/651/652/1225 (valkoiset nauhaikkunatoimistot, sininen katutaso), 659 (käyttäjä: kahden kerroksen syvennys betonipylväineen
  puolessa talosta, sitten liiketila; runalt x < 162), 609 (vaalea ruskeankeltainen tiili). styles: 1748 Saukkosen talo `gone` (tontti tyhjä),
  1222 ja 661 puutaloiksi, 1225 `gone` (sen julkisivu on 652:n LoD2-kuoressa; h100 piirsi siihen tyhjän puutaloseinän).
  kivi.py: `gone`-suodatin build_and_bakeen, lower_eave(1221) Isolinnankatu 16:n puutalon räystäs 4,1 m. city.py: hspec käyttää SPECiä.
  zones2.py: ruudukko myös runalt-pätkille. Avoinna: 661:n harjakatto (peli piirtää LoD2-katon), 606:n pyöreä lasiparvekepino.
- **18.11 klo 10–11, Isolinnankadun länsipuoli:** 1623 ja 1724 rautalanka osuu (ikkunarivit kohdallaan). 640: pohjoispää (y > 14)
  sinisenharmaata peltiä, isot ikkunat ja lasikaiteiset ulokeparvekkeet kulmassa, muu osa vaalea rappaus (zones.py SPEC[640], tori4 rakentaa
  jalanjäljestä → `walls` reunaindekseittäin). Isolinnankatu valmis tältä erää; seuraavaksi listan 6: Pohjoisranta + Eteläranta.
- **18.11 klo 11–12, Eteläranta (käyttäjä: ravintolarakennukset Shots / Skooli väärin):** Rantamakasiini 8386 (Eteläranta 5, 1896) oli
  vaaleanpunainen kivitalo → nyt vaalea harmaanvihreä puupaviljonki, valkoiset listat, korkeat ikkunat, keskellä päätykolmio ja lasiovet,
  vihreä peltikatto; lower_eave(8386) räystäs 4,0 m (skannauksen seinä 6,5 m). Varoitus: facade_bits-laatikko seinän edessä mustasi koko
  julkisivun (jaettu "rep"-ruutu leivottiin laatikon takaa) → ovi tehty 'S'-sarakkeena. 1744 matala paviljonki (ei 2-krs). index.html: pelin
  kaksi koodilla piirrettyä ravintolapaviljonkia (vihreät aumakatot, aurinkovarjot): läntinen (-106, 500) poistettu (SV: nurmikko),
  itäinen (-3, 487) valkoinen matala laatikko (SV). Bärco ja muut Etelärannan talot kunnossa.
- **Bärco (käyttäjä 18.11):** ylhäältä kansi ja laitojen sisäpinnat puuttuivat (takapinnat karsittiin) → vesi näkyi laivan sisällä. index.html: Bärcon materiaali DoubleSide.
- **18.11 iltapäivä, Yrjönkatu koko pituudelta (28 SV-kuvaa, rautalanka):** Kivi-Porin pää ja valokuvajulkisivut (602, 603, 1599) kunnossa.
  Korjattu: 1729 Yrjönkatu 7 / OP-kortteli ruskeankeltainen tiili + sininen pankkikerros (oli harmaa nauha) ja musta pystylaatta
  1728/1729-saumassa → gen.py `_hidden_wall`: jalanjäljestä rakennettu seinä, jonka ulkopuoli on toisen talon sisällä, jätetään pois
  (koskee kaikkia jalanjälkilohkoja). 238 Sampotalo piirtyi Teljäntorin (216) kuoressa tyhjäksi seinäksi: ruudukko (GRID) venytti
  toisen talon runalt-pätkän 216:n räystääseen → zones2: ruudukko runalt-pätkille vain `gridalt=True` (659). 637 Itäpuisto 5
  tummempi terasti. 121 Palojoenkulma: torni ruskea tiili, Yrjönkadun siipi valkoinen nauhaikkunoin (runalt y > -433,5).
  Huom. gshot ZONE odottaa vain yhtä nimettyä lohkoa: muut nimetyt lohkot voivat näkyä kuvassa vielä pelin varamalleina.
- **Antinkatu 9 (1493, käyttäjä 18.11: "ihan erinäköinen"; SV laskettu kuvasta):** 5 akselia, okra seinä, kermanvalkoiset parilliset
  pilasterit ja ikkunanpuitteet, ylhäällä korkeat ikkunat päätyfrontonein, katutasossa kaaret ja vihreät markiisit, raskas räystäslista,
  tasakatto (ilman kattoa peli piirsi ilmakuvakaton vinoksi laataksi). Taustan 1492 harmaa betoni, vasen 1490 harmaa-beige (olivat
  valkoisia parveketaloja). Käyttäjä: "älä keksi olemattomia, vaan vertaa kuvaan" → vain kuvassa näkyvät piirteet.
  gen.py `_hidden_wall`: vain jos naapuri on vähintään yhtä korkea. Kaaret näkyviin (`wh_fixed`, leveämmät aukot), markiisit kaarten
  sisään. 1361:n eteläpäätyseinä (9:n yllä, leipoutui mustaksi) → yksi koko seinän laatta (`SPEC[1361]['walls']`).
- **Ajettava:** `bake tori0 tori1 tori3 tori4 kivi2 --samples 64` ja `city 64 c064,c065,c067,c069,h100`. Koko keskusta hyötyy ruudukosta → lopuksi `city 64 c`.
- **18.11 ilta, Antinkatu (SV + rautalanka):** index.html: lohkon shells-rivi luetaan `;`-merkkiin asti (Windowsin CRLF-bake ei latautunut →
  Keskuskartano ym. tavallisina seininä, katot irti), latausvirhe konsoliin. Purettu talo (styles `gone`) jätetään pois myös tavallisista
  seinistä (mobiili ei lataa bakeja: Saukkosen talo näkyi). 116 Antinlinna: 3 krs, 8 akselia kuvasta mitattuna, pilasterit vain oven vieressä,
  valkoinen palomuuripääty 3 yläikkunalla. 114 puutalo: isot 6-ruutuiset ikkunat, punatiilisokkeli (styles `win`, `pl`, city.py).
  522 Antinkatu 31 + 414 Antinkatu 29 (yksi LoD2-kuori): rapattu tasainen seinä + mitatut ikkunat, ovet, laattapilarit, 3 ulkonevaa lasitettua
  parvekepinoa pyöristetyin kulmin; 414 kerma, porrasoven suora lippa ja lasitiilinauha lähes räystäälle. gen.py: sarake `d` (ovi, yllä tyhjä), `wmarg`.
- **Ajettava:** `city 64 c048`.

## 18.11.2026 ilta – ALOITA TÄSTÄ: Antinkatu julkisivu kerrallaan (facades.json + rectify)

### Uusi työtapa (käyttäjä hyväksyi: "jos pystyt tuollaisella tasolla tekemään kaikki muut julkisivut, voidaan jatkaa")
1. **Tunnista talo** osoitteesta + ID:stä (`who.py x y`, `rays.py cx cy h0 h1 step`, styles-notet). LoD2-kuoren seinälinja: `raw.pkl` (W-rivit),
   jalanjälkitalo: `zones.poly(i)`. **Tärkeää:** jalanjäljestä rakennettu talo (SPECissä `walls`, esim. 564, 163) → käytä jalanjäljen reunaa,
   ei LoD2-linjaa (564:n päädyssä 0,2 m ero kätki ohuet laatikot seinän sisään).
2. **SV-kuva** Claude_Browser browser_batch (navigate → wait 6 → screenshot 0.1 → wait 3 → screenshot 1, 800×450). Panon oikea paikka URL:n `@lat,lon`.
3. **`tools/rautalanka/rectify.py`**: `python3 rectify.py sv.jpg cx cy heading pitch Ax,Ay Bx,By s0 s1 z0 z1 out.png [ppm] [fov] [ch] [d]`
   → suoristettu seinäkuva metriruudukolla (s alkaa A:sta, ulkopuoli A→B:n oikealla; rectifyssa puoli ei väliä). Mittaa ikkunat/kerrokset siitä.
   Panon paikka voi heittää 1–2 m / mittakaava 4–6 % → vertaa kahta panoa, sovita LoD2-seinän pituuteen (kulmasta kulmaan).
   Käyttäjien 360-kuvien (2e10) asento epäluotettava → käytä vain lukumääriin.
4. **`blender/facades.json`** (yksi talo / rivi, `json.dumps(lista, indent=0)` – käyttäjän tiedoston muoto): `{"id", "note", "walls":[{"a","b","bare","kind",
   "items":[...]}], "nobrick"}`. Itemit (s, z metreinä; d ulospäin seinästä):
   `["win",s0,s1,z0,z1,frame,glass]` (keskipuite jos >1 m), `["winp",s0,s1,z0,z1,n,frame,glass]` (n ruutua, uusi), `["wins",[keskikohdat],w,[z-alat],h]`,
   `["door",s0,s1,z0,z1,väri]`, `["glass",s0,s1,z0,z1,väri,(d)]` (uusi, lasinauha), `["box",s0,s1,z0,z1,d0,d1,väri,(kind)]` (d0 saa olla negatiivinen
   syvennyksessä), `["balc",s0,s1,[tasot],top,D,r,kaide,lasi,ph,gh]`. Seinän avaimet: `bare` (seinän pohjaväri → runalt tasainen),
   `kind` (plaster/brick/concrete/woodv/**sheet** = sileä pelti, uusi), `bare_s` [u0,u1], `side:"left"`, **`recess:[gh, sb, h]`** (uusi: katutaso gh m korkea
   sb m sisäänvedetty, pilarit itemeinä d -sb..0), `shop_bw`. Talotason **`nobrick: true`** → peli ei piirrä tiilikuviota (Ratsula: pelti!).
5. Poltto 8 näytteellä: c-lohkot `PYTHONPATH=/home/claude python3 city.py c052 8`, nimetyt `python3 run.py tori3 8` (ZONES zones.py:ssä),
   kivi-lohkot `kivi.build_and_bake(...)`. Lohko: `city_zones.json` / zones.ZONES / kivi.ZONESK.
6. Tarkistus: `bash tools/rautalanka/runov_fast.sh views.json out.jpg KEY:sv.jpg ...` (3 s), lopuksi oikea peli `ZONE=- node tools/rautalanka/gshot_sv.mjs`.
   Pikarenderin vino vaalea juova isoissa tasaisissa seinissä on vain pikarenderin virhe (ei pelissä). Länteen katsovat seinät jäävät bakessa
   tummiksi (aurinko 118°) → vaaleampi `bare`.

### Tehty 18.11 ilta (kaikki käyttäjän kansiossa)
- **215 Antinkatu 14 Kansankulma (c052):** harmaa rappaus, 2,5 m ikkunat ryhmissä 2-4-4-2 + porraskäytävien pikkuikkunaparit, 1. krs leveät/pienet,
  tumma kivijalka, Nuovon harmaat ja kulman punainen markiisi, 2 syöksytorvea.
- **221 Ratsula (c052):** punainen **pelti** (ei tiiltä, käyttäjä muistutti uudelleen), 4 m lasinauha 2,75 m puittein, punainen otsalauta,
  liiketilat 1,4 m sisään punaisten pilarien (7,65 m välein) takana. LoD2-seinän ensimmäiset 3,5 m eivät näy kuvassa punaisena.
- **564 Itäpuisto 7 / Antinkatu 12 (tori3):** Antinkadun pääty: muraali pelkkinä väripintoina (taideteosta EI kopioida), sininen pystykyltti,
  vaalea kylttitaulu; Itäpuiston julkisivu: 11 pilariväliä, 3-ruutuiset ikkunat 5 krs, liikkeet + sininen/vaalea otsavyö.
- **163 Antinkatu 15 / Itäpuisto 9 funkis (tori2):** 4-ruutuiset ikkunat 5 krs (4 + 5 saraketta), vihreät kulmaparvekkeet, graniittinen katutaso,
  Taito-liike raidallisen markiisin alla, ovi 15 C, punainen pystykyltti. Pohjapiirroksessa kulma viisto (todellisuudessa pyöreä).
- **index.html:** tietokoneella c-lohkot mukaan TEXLODiin: lähimmät 8 mallia 2048 px, muut 512 px (ennen kaikki lohkot 1024) → terävämmät
  julkisivut; lohkon poistuessa tekstuuri poistetaan TEXLOD-listalta. Mobiili ennallaan (512). Jos GPU-muisti loppuu: pienennä `TEXLOD.N`.
- **zones.py:** `_bare_mat`, `_bare_w` (recess, sheet), `winp`, `glass`, `nobrick` facades.jsonista.

### Opittua
- **Tallennus käyttäjän kansioon:** device_commit_files saattaa kirjoittaa vanhan välimuistiversion, jos stagedPath-nimi on käytetty aiemmin
  (zones.py kirjoittui kahdesti vanhana!). Käytä aina uutta nimeä (`/mnt/user-data/outputs/cN/zones_xxx.py`) ja tarkista staging + cmp jälkeenpäin.
  Ennen kirjoitusta: `.git`issa ei `MERGE_HEAD`, stage + diff (vain omat rivit), expectedMtimeMs.
- device_bash ei aina ole saatavilla → stage/commit-tiedostotyökalut riittävät.

### Ajettava (käyttäjä, Modal)
- `city 64 c048,c051,c052,c067`
- `bake p1 tori2 tori3 --samples 64`
- (aiemmat, jos ajamatta: `bake tori0 tori1 tori4 kivi2`, `city 64 c064,c065,c069,h100`)

### Seuraavaksi
- Antinkatu pohjoiseen: 161 (OO Studio, Antinkatu 13; pelissä valkoinen ja liikaa ikkunoita, todellisuudessa tummempi ruskeanbeige),
  563 (564:n pohjoispuolinen osa / Cafe Anton), sitten Antinkatu 10 (lasitoimisto torin kulmassa) ja Airionkulma 602/603/604
  (käyttäjä: lukitutkin saa tehdä uudelleen, jos näyttävät vääriltä). Sen jälkeen muut keskustan kadut (Pohjoisranta, Hallituskatu ...).
- Oikean pelin tarkistus (gshot) vielä tekemättä: 274, 137, 255, 216, 569/570, 564, 163.
- Myöhemmin: mobiiliversiot bakeista, Teljäntorin putkikatos, 569/570 päätyikkunat, 163:n pyöreä kulma.

### 18.11 ilta: kadut geometriana, autotila, pyöritysvideot
- **Kadut (tools/roads/build_roads.py -> roads.js):** OSM-tiet api.openstreetmap.org:sta (pilven verkko estää Overpassin; haettu sisäisellä selaimella,
  javascript_tool-tulos tallentuu levylle kun se on iso) -> `tools/roads/osm_ways_center.json` (x -790…900, y -995…995). Ajoradan reuna mitataan kummallekin
  puolelle: jalkakäytävä-/pyörätieviiva on jalkakäytävän keskellä -> reunakivi = 2·viiva − julkisivu. Jalkakäytävät +0,13 m reunakivellä, saarekkeet,
  suojatiet, katkoviivat. Kivetys (`kivi`, omistajan PBR `kivetys_*.jpg`, 2,2 m toisto): Yrjönkadun ja Itäpuiston kävelykadut (Eetunaukio) ja Kauppatori;
  vanha tori_pave-mesh piilotettu. Kirjurinluotoon EI katuja (omistaja: siellä ei asfalttia). Pinnat: tools/roads/make_tex.py (road_asph/pave/crack).
- **Autotila (index.html):** aloitusruudussa valinta kopteri/auto (videot veh_*.webm/mp4, posterit jpg). Auto = omistajan porikopteri_auto.py (tools/vehicles/;
  auto.js korkea sisustoineen, auto_m.js matala mobiiliin, ladataan vain autoa valittaessa). Ajomalli `stepCar`, korkeus `carGround` (asfaltti/jalkakäytävä-
  rasteri/sillat), talot ja joki pysäyttävät. Navigaattori `NAV`: Dijkstra CITY.r-verkossa, nuoli + matka + katu (#nav), reitti minikartalla. Autolle oma
  top-10 (kenttä c<YYYYMMDD>) ja oma ennätys. Kamera C: takaa / kuljettajan paikka / ylhäältä.
- **Pyöritysvideot:** `python3 tools/vehicles/turntable.py malli.glb out nimi 96 24 640` (Cycles CPU ~12 s/kuva, HDRI blender/tex, alla road_asph) + ffmpeg.
- Avoinna: suojateiden madallukset, autot (liikenne) eivät väistä pelaajaa, sillat autolla karkeasti (deck = vedenpinta + 2,2 m), mobiilissa ei käsijarrua.

### 18.11 klo 21–22.30: suojatiet, yksisuuntaiset, korjaukset
- **Madalletut reunakivet** suojateiden päissä (build_roads.py `RAMPS`, `ramp_h`): jalkakäytävä laskee 3 cm:iin asfaltista suojatien levyltä, nousee 1,4 m sisään
  ja 1,0 m sivuille; roads.js `rampp`/`rampk` (x, y dm, h·1000), reunakivet `kerb` (täysi) ja `kerbh` (korkeus päissä).
- **"Asfaltti katoaa auton alta"**: ilmakuvamaa piirretään 6 m kolmioina, jotka pullistuvat todellisen maan (TZg) yli jopa 13 cm (99 %) -> kuva puski läpi
  lähellä kameraa. Korjaus: `groundTop(x,y)` = max(TZg, ytimen maaverkko, 0,25 m ilmakuvalaatat) ja pinnat sen päälle (asfaltti +0,13, jalkakäytävä +0,26).
  Reunakivien pystypinnat maahan asti. Kopteri ja auto seisovat katupinnalla (roofAt, carGround).
- **Näkymättömät esteet autolla**: roofAt kokeili 3 m kehää (kopterin jalakset). Autolle `bldTopAt` (vain piste talon pohjan sisällä).
- **Kuuset pois keskustasta** (ne olivat satunnaisia 10 %:n arvontoja, ei oikeita kuusia).
- **Puut ajoradalla** (OSM) siirretään jalkakäytävän reunaan 0,8 m reunakivestä (roads.js `tmv`, 749 puuta), kaukana jalkakäytävästä olevat poistetaan.
- **Nurmikkotupsut** eivät kasva katupinnoilla (roads_ao.png G-kanava, GRASS-shader). R-kanava = kontaktivarjo talojen seinien juurella (talot eivät näytä leijuvan).
- **Yksisuuntaiset kadut**: OSM oneway + liikenneympyrät (ROUND-lista, junction-tagia ei ollut aineistossa) -> CITY.r-pätkät (`ow`, 1111 kpl). Navigaattori ajaa
  vain sallittuun suuntaan (varalla ilman rajoitusta), liikenteen autot noudattavat, pelaajalle varoitus väärästä suunnasta.
- **Paistot**: Antinkadun mitatut julkisivut (facades.json) eivät olleet leivottuina -> paikalliset 8 näytteen baket c052, c048, c051, c067, tori3, p1 (tori2 jo).
  Huom: 8 Gt muistissa kaksi bakea yhtä aikaa (tai bake + Chromium) kaatuu (exit 137) – aja yksi kerrallaan.
- Ajettava Modal 64: `city 64 c048,c051,c052,c067` ja `bake p1 tori2 tori3 --samples 64`.

### 18.11 klo 22.30–23: autoradio
- **Radio Porikopteri** (index.html `RADIO`, kansio `radio/`): kanavat Pop, Electric, Rock, 3 omaa kappaletta + jingle kullakin (radio.json: tiedosto, kesto, nimi).
  Kappaleet sävelletty säännöillä MIDIksi ja soitettu FluidSynthillä (FluidR3_GM, MIT): `python3 tools/radio/compose.py ulos/` (apt: fluidsynth fluid-soundfont-gm,
  pip: mido). Kanavat soivat "suorana": kohta lasketaan kellosta. R / 📻-nappi vaihtaa kanavaa, M mykistää. Käynnistyy Popilla autolla lähdettäessä.
  Huom: python -m http.server ei tue Range-pyyntöjä -> kelaus ei toimi paikallisesti, GitHub Pagesissa toimii.
- GPU-muistin säästö: roads_ao.png 1 m/px (1690×1990), kivetys_albedo 1024 px, road_crack 1024 px.
- Avoinna: omistaja: "Keskuskartanosta puuttuu taas seiniä" – pilven pelissä c064 näkyy ehjänä; odotetaan kuvakaappausta (epäily GPU-muisti tai CRLF-bake).

### 18.11 klo 23: puistotiet, nurmi, sepeli
- **Puistoteiden keskikaistat** (Itä-, Länsi-, Etelä-, Pohjoispuisto; build_roads.py `MED`): alue kahden vastakkaissuuntaisen ajoradan välissä (puolitesti suunta huomioiden),
  korotettu reunakivelle, pintana omistajan nurmi (`nurmi_*`, 1,2 m) ja keskellä 4 m punagraniittisepelikäytävä (`sepeli_*`, 0,6 m). Vanhat puut pois, tilalle
  lehmusrivit ±3,6 m käytävästä 8 m välein (roads.js `tadd`). Suojatiet ja madallukset myös keskikaistan poikki.
- **Nurmi muualla:** OSM-nurmikot ja puistot (`lawn`) maan tasossa; shader näyttää nurmen vain siellä missä ilmakuva on vihreä (polut, hiekka, kukkapenkit jäävät kuvaan).
  Puistopolut (`path`) sepelillä.
- Asfaltti ulottuu 0,35 m reunakiven alle (rako näkyi sinisenä viivana).

### Sovittu 18.11.2026 klo 23 (omistaja): polttojen työnjako
- Paikallinen 8 näytteen poltto vain omaan tarkistukseen (rautalanka) – EI viedä käyttäjän kansioon, ellei omistaja pyydä.
- Modal-poltto (64 näytettä) vasta kun on kertynyt tarpeeksi valmista. Pidä alla olevaa listaa ajan tasalla ja kerro se omistajalle, kun on sopiva hetki.
- **Modal-jono nyt:** `city 64 c048,c051,c052,c067` · `bake p1 tori2 tori3 --samples 64` · `bake tori0 tori1 tori4 kivi2 --samples 64` · `city 64 c064,c065,c069,h100`
  (myöhemmin mahdollisesti koko keskusta `city 64 c`).

### 18.11 klo 23.30: Antinkatu jatkuu
- **563 Antinkatu 12** (tori3): EI keltainen Cafe Anton (vanha merkintä väärä) vaan 2-kerroksinen 1960-l. betoninen liiketalo: tumma lasitettu liiketila-
  kerros, ylhäällä toimistot, kuusi kolmiruutuista ikkunaryhmää 4,43 m välein, elementtisaumat, pohjoispäässä umpiseinä ja ovi. facades.json (jalanjäljen reunat),
  zones.py SPEC[563] + B[563]['h'] = 8.9 (ilman SPECiä run.py käytti auto-speciä eikä facades.jsonia), index.html ZROOF += 563 (ilmakuvakatto leijui 10 m:ssä).
  Rautalanka osuu. Huom: nimetyissä lohkoissa (run.py) facades.json vaatii SPEC-merkinnän.
- Pysäköidyt autot: ei talon sisään eikä jalkakäytävälle (bldTopAt). Liikenne- ja pysäköityjen autojen korkeus +6 cm (pyörät upposivat).
- Modal-jonoon kuuluu tori3 jo (563 näkyy pelissä vasta Modal-polton jälkeen).

### 19.11 klo 00.20: torin länsilaita, 1315 ja 1490 (tori1)
- **1315 Antinkatu 11** (ent. PYP 1956): valkoinen betoniraster 10 × 2,22 m, kuusi kerrosta kaksiruutuisia ikkunoita sinharmaiden mosaiikkipaneelien päällä,
  9. ruudussa sisäänvedetyt parvekkeet, beige otsanauha kultakirjaimin, Beer Hunter'sin vihreä markiisi. facades.json, bare-seinä.
- **1490 Antinkatu 9**: harmaanbeige rappaus, seitsemän kerrosta, neljä kolmiruutuista ikkunaa, pohjoispäässä parikkunat, pyöreä betoniparveke ja ROSSO-kirjaimet,
  ravintolan lasitus punaisten markiisien alla.
- **Cafe Anton on olemassa**: lasijulkisivuinen talo heti 1490:n pohjoispuolella (Antinkatu 7?) – pelissä siinä nyt harmaa reikäikkunatalo + keltainen talo; tarkistettava seuraavaksi.
- Rautalanka: `Claude outputs/rautalanka_1315_1490.jpg`. Modal-jonossa tori1 on jo (`bake tori0 tori1 tori4 kivi2`).

---

## 19.11.2026 – ALOITA TÄSTÄ (uusi chat)

Vastaa suomeksi, lyhyesti, ja näytä jokaisesta muutoksesta kuva. Lue tämä luku ensin, sitten tarvittaessa luvut 18.11 (Antinkatu, tiet, auto, radio).

### Tilanne
- **Kaikki koodi on synkassa käyttäjän kansiossa** (tarkistettu cmp:llä 19.11 klo 00.30): index.html, roads.js, blender/zones.py, blender/facades.json,
  styles.json, tools/roads/build_roads.py. Pilvessä ei jäänyt mitään viemätöntä paitsi paikalliset 8 näytteen testipoltot (ei viedä).
- **Push ja Modal-ajot tekee käyttäjä.** Ennen niitä ei mikään facades.json-muutos näy pelissä.

### Modal-jono (kun käyttäjä sanoo, että poltetaan)
```
city 64 c048,c051,c052,c067
bake p1 tori2 tori3 --samples 64
bake tori0 tori1 tori4 kivi2 --samples 64
city 64 c064,c065,c069,h100
```
(myöhemmin mahdollisesti koko keskusta `city 64 c`).

**Mistä puuttuu Modal-poltto (64 näytettä), tarkistettu 19.11:**

| Lohko | Miksi | Talot / muutokset |
|---|---|---|
| tori1 | facades.json 19.11 | 1315 Antinkatu 11, 1490 Antinkatu 9 (Rosso) |
| tori2 | facades.json 18.11 | 163 Antinkatu 15, 161 Antinkatu 13 (OO Studio), 1497 Liikekulma |
| tori3 | facades.json + SPEC 18.11 | 564 Itäpuisto 7, 563 Antinkatu 12 (h 8,9) |
| p1 | facades.json 18.11 | Antinkadun mitatut talot (paikallinen 8 näytteen bake tehty) |
| c048, c051, c052, c067 | facades.json 18.11 | 118, 126, 133, 135, 290, 274, 137, 255, 216 (Teljäntorin sisäpiha), 221 Ratsula, 215 |
| tori0, tori4, kivi2 | ikkunarivit 17.11 (ruudukko) | aiemmin jonossa, ajamatta |
| c064, c065, c069, h100 | ikkunarivit 17.11 | c064 = Keskuskartano |

Ei polttoa tarvitse: kadut, kivetys, nurmi, puut, autotila, radio, pysäköidyt autot (index.html / roads.js, näkyvät heti pushin jälkeen).

### Pysyvät säännöt (omistaja)
- API-avaimia/GitHub-salaisuuksia ei käsitellä. Push ja Modal käyttäjälle.
- Street View-, kaupungin- ja Y-pakin kuvia EI viedä GitHubiin eikä peliin; niistä luetaan vain värit, materiaalit, muodot. SV-rautalankakuvat vain kansioon `Claude outputs/`.
- Lukittuja ei muuteta kysymättä: KARHU-värit, Airionkulman 603/602/604 valokuvajulkisivut.
- Lataukset ja tiedostojen poisto käyttäjän koneelta vain luvalla.
- Tunnista talo AINA osoitteesta ja projisoidusta ID:stä ennen muutosta. Älä keksi olemattomia – vertaa kuvaan. Taideteoksia (muraalit) ei kopioida.
- Paikallinen 8 näytteen poltto vain omaan tarkistukseen; Modal-poltto vasta kun on kertynyt tarpeeksi.

### Julkisivun työtapa (facades.json)
1. Street View sovelluksen omassa selaimessa: `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=LAT,LON&heading=H&pitch=P&fov=90`
   (kuvakaappaus 743×418). Panon todellinen paikka luetaan URL:sta (`@lat,lon,...,Hh,Tt` → pitch = T−90).
2. Muunnos: x = (lon − 21.796)·53278, y = (lat − 61.486)·111437.
3. Talon jalanjälki: `cd blender; python3 -c "import zones; print(zones.poly(ID))"` – käytä jalanjäljen reunaa seinälinjana (a→b, ulkopuoli oikealla).
4. Oikaisu: `python3 tools/rautalanka/rectify.py sv.jpg cx cy heading pitch Ax,Ay Bx,By s0 s1 z0 z1 out.png 22` (pystykulma 90°), mittaa ruudukosta.
5. Kirjoita generaattoriskripti (mallit `tools/rautalanka/facades/f161.py, f563.py, f1497.py, f1315.py`; polku p skriptin lopussa osoittaa pilven
   /home/claude/pori – vaihda tarvittaessa). Itemit: win, winp (n ruutua), glass, door, box (s0,s1,z0,z1,d0,d1,väri[,kind]), balc, wins. `bare`+`kind` poistaa generoidut ikkunat seinältä.
6. Nimetyssä lohkossa (run.py tori*/p1/kivi*) talolla pitää olla SPEC zones.py:ssä, muuten facades.json ohitetaan. Jos ilmakuvakatto leijuu, lisää ID index.html:n ZROOFiin.
7. Testipoltto (yksi kerrallaan, 8 GB muisti!): `cd blender; python3 run.py tori1 8` → tulos `/home/claude/out/bl_tori1.js` → kopioi pelikansioon testiä varten.
   c-lohkot: `PYTHONPATH=/home/claude python3 blender/city.py c052 8`, kivi: `kivi.py p1 8`.
8. Rautalanka: `python3 -m http.server 8765` pelikansiossa, sitten `ZONE=tori1 node tools/rautalanka/gshot_sv.mjs index.html out/ views.json`
   (views: `[{"k":"a","x":..,"y":..,"h":..,"p":..,"fov":90}]`), vertaa SV:hen rinnakkain.
9. Vienti käyttäjälle: stage → tarkista että laitteen tiedosto = pohjasi → device_commit_files (expectedMtimeMs, uusi nimi /mnt/user-data/outputs/cN/) → stage uudelleen ja cmp.
   Aja `node --check` index.html:n skriptille jokaisen muokkauksen jälkeen (18.11 sed-kommentti rikkoi pelin).

### Antinkatu – tehty
161, 563 (Antinkatu 12, 2-krs liiketalo), 1497 (Antinkatu 13 Liikekulma), 1315 (Antinkatu 11, valkoinen raster + Beer Hunter's), 1490 (Antinkatu 9, Rosso).
Aiemmin: 118, 126, 133, 135, 290, 274, 137, 255, 216, 221, 215, 564, 163.

### Seuraavaksi
1. **Cafe Anton -talo** heti 1490:n pohjoispuolella (lasijulkisivu, "anton gastropub & cafe", vieressä Hotel Torni/"TORGO"-katos). Pelissä siinä nyt harmaa reikäikkunatalo
   ja keltainen talo – tunnista ID (todennäköisesti tori1:n 1491–1496) ja mittaa. Hyvä pano: Antinkatu 10, 61.4872248, 21.7961243, heading 255, pitch 16
   (peli x≈6.6, y≈136.4; gshot-asento ei osunut aivan tarkasti – tarkista).
   Huom: omistaja kysyi aiemmin "ethän poistanut cafe antonin muotoa?" – 563:n Cafe Anton -merkintä oli väärässä talossa, oikea on tämä.
2. Antinkadun lista jatkuu: 1725, 1726, 1600 (Yrjönkadun kulma), 136 (Antinkatu 21a), 409, 570, 276, 415.
3. Keskuskartano (c064) seinät puuttuvat omistajan koneella – pilvessä ehjä; odotetaan kuvakaappausta (epäily GPU-muisti tai CRLF-bake).
4. Kun riittävästi kertynyt: pyydä omistajaa pushaamaan ja ajamaan Modal-jono.

### Muistiinpanoja
- Pilven tiedostot ovat väliaikaisia: uusi chat aloittaa tyhjästä. Hae repo käyttäjän koneelta (device_bash/stage) tai GitHubista; blender-paistoon tarvitaan
  bpy-moduuli (`pip install bpy`), datat (OSM, LoD2, ilmakuvat) ks. luvut 14.–15.11.
- OSM-haku onnistuu sovelluksen selaimella api.openstreetmap.org:sta (Overpass estetty pilvestä).

### 19.11 aamu: radion puhekanava
- Uusi kanava **Puhe** (index.html RADIO.names; R kiertää Pop, Electric, Rock, Puhe, pois; kanava ohitetaan jos radio.jsonissa ei ole sitä).
- Käsikirjoitus `tools/radio/puhe.json` (13 Pori-puhetta + 7 keksityn yrityksen mainosta, numerot auki kirjoitettuna), generaattori
  `python3 tools/radio/speak.py radio/voice/fi_FI-harri-medium.onnx radio/` → radio/puhe_*.mp3 (4 Mt, 8,2 min silmukka) + radio.json "puhe".
- Ääni: Piper (`pip install "piper-tts>=1.5"`, MIT), malli fi_FI-harri-medium (MIT, aineisto CC0). Malli (63 Mt) on käyttäjän koneella `radio/voice/`,
  .gitignoressa – ei GitHubiin. Hugging Face on estetty pilvestä; malli haettiin sovelluksen selaimella.
- Mainosten alla radion oma pop hiljaa (−16 LUFS), puheet loudnorm −16 LUFS. Lisää puheita: lisää puhe.json:iin ja aja speak.py uudelleen (id:t uniikkeja!).

### 19.11 aamu: Cafe Anton -kohta (1492 katukaistale, 1493, 1490 pohjoispää) – tehty, polttamatta
- **Tunnistus:** "Cafe Anton -talo" = kaksi taloa. Kyltti on **1492:n 3,8 m katukaistaleella** (-4.7,140.2 → -3.9,143.9; lasiuloke, kylttipino),
  itse kahvila on **keltaisen 1493:n** katutasossa. Niiden välissä on todellisuudessa **3,2 m avoin porttikäytävä** (Torget-katos), jonka
  city.js:n jalanjälki oli laskenut 1493:ään (talo 15,6 m, jalanjälki 18,1 m).
- **zones.py:** 1493:n eteläpää siirretty 3,2 m pohjoiseen (`B[1493]['p']`, `_a9S`), 5 aukkoa (bw 2,95), **vasen aukko ovi** (omistaja 19.11),
  etelpääty paljas, musta katos portin päälle (`_a9_awnings`). 1492:n takaseinään lisätty kärki (-8.6,148.2), jotta portin kohta ei jää piiloseinäksi.
- **facades.json / `tools/rautalanka/facades/f1492.py`:** 1492 (tumma lasisisäänkäynti, 2-krs lasiuloke 1 m ulkona, kyltit värilaattoina,
  pohjoissivulla lasiparvekepino) ja **1490 mitattu uudelleen** (f1315.py:stä poistettu): Rosso-kirjaimet, parveke ja ikkunat olivat ~1,3 m liian
  pohjoisessa; lisätty 2-krs lasikaista ja tummansininen kulmapilari. Todellinen julkisivu 22,4 m / jalanjälki 21,0 m → eteläosan 4 ikkunasaraketta
  tiivistetty 0,915:llä, pohjoisosa oikeassa mitassa.
- **Panot:** Antinkatu 10: (61.4872248, 21.7961243) → peli x 6.51, y 136.01 (korjattu 0,4 m) ja (61.4873143, 21.7961676) → x 8.93, y 146.5.
  Sovelluksen selaimen ikkuna on nyt 743×1026 (pysty-FOV 90 pätee edelleen; älä käytä resize_window alle 768 px – Maps vaihtuu mobiiliksi).
- **Ympäristö:** `git clone` GitHubista toimii pilvestä (+ uudemmat tiedostot koneelta stage), `pip install bpy shapely opencv-python-headless`,
  gshot_sv.mjs: playwright on polussa `/opt/npm-tools/node_modules/`. tori1 8 näytteellä ~135 s.
- **Modal:** tori1 on jo jonossa (`bake tori0 tori1 tori4 kivi2`) – ei uusia lohkoja. Vertailukuva: `Claude outputs/cafe_anton_vertailu_19_11.jpg`.
- **Auki:** portin kohdalla maassa vaalea laatta (pelin puolen pohja vanhasta jalanjäljestä?) – tarkista Modal-polton jälkeen. Seuraavaksi lista: 1725, 1726, 1600, 136, 409, 570, 276, 415.

### 19.11 klo 9–10: 1725 Antinkatu 10 (Royal Mustang -siipi) – tehty, polttamatta
- `tools/rautalanka/facades/f1725.py` + facades.json: beiget laattapilarit ja -vyöt, 4 aukkoa (kolmijakoinen ikkuna + ruskea rintapaneeli),
  pohjoispäässä roiskerappauskenttä + yksi ikkuna portin päällä (portti piirretty tummana + säleportti), punaiset kyltit, valkoinen kylttilevy.
- **Korkeus 6,7 m** (city.js 10): `B[1725]['h'] = 6.7` zones.py:ssä ja **1725 lisätty index.html:n ZROOFiin** (ilmakuvakatto leijui 10 m:ssä).
- Pano Antinkatu 11 (61.4874992, 21.7962552 → x 13.63, y 167.06) on vain 6 m seinästä: oikaisu antoi 18,5 m ja jalkakäytävän z 0,9 → kamera 10 %
  kauempana; korjaus s = (s−0,06)·1,1, z = 1,1·z − 0,99 (päät osuvat jalanjäljen kulmiin). Läheltä otetuissa panoissa tarkista aina maan z ja pituus.
- **Modal:** tori0 on jo jonossa. Vertailukuva `Claude outputs/antinkatu10_1725_vertailu_19_11.jpg`.
- **Havaittu, tekemättä:** 1726:n Antinkadun pääty on oikeasti tummanpunaista laattaa, 2 ikkunasaraketta, tumma liiketila (pelissä beige parvekepääty);
  1600 (Dante-baari, vihreä mansardikatto, pyöreät kattoikkunat) on pelissä pelkkä laatikko. Seuraavaksi nämä, sitten 136, 409, 570, 276, 415.

### 19.11 klo 10–11: 1600 Antinkatu 8 (Dante-ravintola) – tehty, polttamatta
- `tools/rautalanka/facades/f1600.py` + facades.json: harmaanvihreät rappauspilarit, 4 tummaa näyteikkunaa (ruudutettu yläosa), sisäänvedetty ovi
  säleportilla, tumma markiisilaatikko, vihreän peltimansardin juuri + 3 kattolyhtyä (pyöreät ikkunat piirretty neliöinä).
- zones.py: `SPEC[1600]` (muut seinät paljaat, vihreä aumakatto); **1600 lisätty index.html:n ZROOFiin**. 1725:n rappauskenttää vaalennettu.
- Panot Antinkatu 9: (61.4876768, 21.7963367 → x 17.94, y 186.8) ja (61.4875892, 21.7962959 → x 15.76, y 177.04). Jalkakäytävä z 1,0, pituus 14,9/15,7 m
  → s = 1,054·s, z = 1,054·(z − 1,0). Street View -ruudut latautuvat hitaasti: odota 15–25 s ennen kuvakaappausta (muuten sumea/musta).
- Huom: index.html muuttuu myös toisessa istunnossa (radio) – stage aina juuri ennen muokkausta. Modal: tori0 jonossa.
- Vertailukuva `Claude outputs/antinkatu8_1600_vertailu_19_11.jpg`. Seuraavaksi: 1726:n punainen laattapääty Antinkadulle, sitten 136, 409, 570, 276, 415.

## 19.11.2026 klo 11 – ALOITA TÄSTÄ (uusi chat, korvaa luvun "19.11.2026 – ALOITA TÄSTÄ" kohdan "Seuraavaksi")

Vastaa suomeksi, lyhyesti, kuva jokaisesta muutoksesta. Säännöt ja julkisivun työtapa: luku "19.11.2026 – ALOITA TÄSTÄ (uusi chat)" yllä;
tämän päivän työt ja opit: sen alaluvut "19.11 aamu: Cafe Anton", "klo 9–10: 1725", "klo 10–11: 1600".

- **Tila:** kaikki koodi on käyttäjän kansiossa (takaisinluvulla tarkistettu klo 11): blender/zones.py, blender/facades.json, index.html,
  tools/rautalanka/facades/f1492.py, f1725.py, f1600.py, f1315.py. Pushaamatta ja Modal-polttamatta (käyttäjä tekee). Modal-jono ennallaan
  (tori0 ja tori1 ovat siinä jo) – tämän päivän talot 1490, 1492, 1493, 1725, 1600 tulevat peliin niistä.
- **Tehty tänään:** 1492 (Cafe Anton -kyltin kaistale) + 1493 lyhennys/portti/ovi + 1490 uudelleenmittaus; 1725 (Antinkatu 10); 1600 (Dante).
- **Seuraavaksi:** 1) 1726:n Antinkadun pääty (17.1,154.3 → 14.4,142.9): tummanpunainen laatta, 2 ikkunasaraketta, tumma liiketila; selvitä ensin
  missä lohkossa 1726 poltetaan (ei tori0:ssa; ZONES/kivi). 2) 136, 409, 570, 276, 415. 3) Keskuskartano c064 (odottaa omistajan kuvakaappausta).
- **Auki omistajalle:** 1600:n ikkunoiden valkoiset tekstipalkit (pois?), portin kohdan vaalea maalaatta 1492/1493 välissä (tarkista Modal-polton jälkeen),
  1725:n portti ja 1492:n sisäänkäynti on piirretty tummina pintoina, ei aukkoina.
- **Ympäristö uudessa chatissa (pilvi tyhjä):** `git clone https://github.com/villeaklinikkasomero/porin-kopterilento.git /home/claude/pori` +
  stage koneelta GitHubia uudemmat tiedostot (yllä luetellut + styles.json) → `pip install bpy shapely opencv-python-headless scipy pillow --break-system-packages`
  → `python3 -m http.server 8765` (kuolee vuorojen välissä, käynnistä uudelleen) → gshot_sv.mjs: vaihda playwright-polku `/opt/npm-tools/node_modules/`.
  Poltto `cd blender; python3 run.py tori0 8` ~130 s. Laiteyhteys ja selain voivat katketa hetkeksi: vie tiedostot heti kun talo on valmis.

### 19.11 klo 11.30–12: 1726 Antinkadun pääty (punainen laatta) – tehty, EI tarvitse polttoa
- **1726 ei ole polttolohkossa:** se on pelin itse piirtämä valokuvajulkisivutalo (index.html `PHS[1726]`, kuvakaista `ph_1726.jpg` toistui joka seinällä,
  myös päädyssä → "beige parvekepääty"). Siksi pääty on **piirretty tekstuuri**, ei facades.json: `python3 tools/rautalanka/facades/f1726.py [pelikansio]`
  → `ph_1726g.jpg` (512×1024, koko pääty kerran, 12,59 × 24,2 m; mitoista ja väreistä piirretty, SV-kuvaa ei käytetä).
- **index.html:** `1726: [{ t: 'ph_1726', bw: 8.12 }, { t: 'ph_1726g', bw: 12.59, cut: -17.612 }]` (cut = sama mekanismi kuin 604:llä: leikkauslinjan
  länsipuoliset seinät eli vain pääty saavat toisen tyylin) + lohko `if (bIdx === 1726 && PB.ph_1726g)`: **ohut päätyseinän jatke** (1,42 m pohjoiseen,
  0,4 m paksu, koko korkeus), koska LoD2-kuoren pääty on 11,09 m ja jätti 1,5 m raon 1725:n ja 1726:n väliin (pihalle näki läpi). SV:ssä laattapääty on 12,2 m.
- **Mitat (panot Antinkatu 10: 8.93,146.5 h85 p42 / h55 p3 / h103 p5 ja 6.51,136.01 h40 p25):** raaka s −1,0…11,2, jalkakäytävä z 0,85, laatan alareuna 3,65,
  yläreuna 21,4; 6 riviä × 2 ikkunaa pohjoispäässä (raaka s 0,56–1,60 ja 2,6–4,14, korkeus 1,3, kerrosväli 2,87), eteläiset 60 % umpilaattaa;
  laatat 12 rinnakkain, 7 riviä/kerros. Katutaso: musta pubin julkisivu (otsapanta, 3 ikkunakenttää, mustat rintapaneelit), kulmassa avoin arkadi ja
  mustalaattainen pyöreä pylväs. Pystysuunta on sovitettu valokuvakaistan kerroslinjoihin (4,48 + 3,287·i), jotta rivit jatkuvat kulman ympäri.
- **Havainto, ei muutettu:** talo on pelissä 24,2 m (LoD2-räystäs), mutta oikaistuissa SV-kuvissa laattaseinä on vain n. 20,5 m (kerrosväli 2,9 m, ei 3,25).
  Kaksi eri panoa antaa saman → koko 1726 on pelissä luultavasti ~3,5 m liian korkea. Omistajan päätettävä (vaikuttaa myös torin puolen valokuvakaistaan).
- Ei Modal-polttoa: näkyy heti pushin jälkeen (index.html + ph_1726g.jpg). Vertailukuva `Claude outputs/antinkatu_1726_paaty_vertailu_19_11.jpg`.
- Ympäristöhuomio: Street View -kuvakaappaus tallentuu pilveen polkuun `/tmp/claude-tool-results/…/*.jpg` (743×1026) – kopioi sieltä rectify.py:lle.
  Selaimen browser_batch katkeaa 50 s:ssa: yksi pano per erä (navigate + 2×10 s odotus + screenshot).
- **Seuraavaksi:** 136 (Antinkatu 21a), 409, 570, 276, 415.

## 19.11.2026 klo 12–13 – Jalankulku ja Keski-Porin kirkon sisätila (uusi ominaisuus, omistajan pyyntö)

Omistaja: "autosta tai helikopterista voi nousta pelaajana ulos ja tiettyihin rakennuksiin pääsee tutustumaan sisälle kävellen. Aloitetaan kirkosta."

### Mitä tehtiin (kaikki käyttäjän kansiossa, pushaamatta; EI vaadi Modal-polttoa)
- **Jalankulku (index.html, lohko "on foot", haku `WALK`)**: **Enter** (tai F autossa/jalan, kosketuksella 🚶-nappi) nousee ulos pysähtyneestä autosta tai
  maahan laskeutuneesta kopterista (katolta ei pääse). W/S kävely, A/D käännös, Q/E sivuaskel, Shift juoksu (kosketuksella 🏃), C vaihtaa kameran
  (takaa / silmistä / ylhäältä). Enter kulkuneuvon vieressä (auto 4,2 m, kopteri 6 m) vie takaisin kyytiin. Kierroksen kello seisoo jalan. N palauttaa kyytiin.
  Törmäys: talot (`bldTopAt`), joki (`carGround` null); maan korkeus = `carGround`. Kamera `walkCamera`, near 0,25 (sisällä 0,12), kyydissä 1.
- **Hahmo `hahmo.js`** = omistajan `porikopteri_hahmo.glb` base64-moduulina (skripti talteen: `tools/hahmo/porikopteri_hahmo.py`). Animaatiot Idle/Walk/Run
  vaihtuvat nopeuden mukaan (AnimationMixer, ristihäivytys 0,22 s); Sit on mallissa mutta ei vielä käytössä. Ladataan vasta ensimmäisellä ulosnousulla.
- **Kirkon sisätila `kirkko_sisa.js`** (5 Mt, ladataan kun kävelijä on alle 90 m ovesta): oma kohtaus `sceneIn`, piirretään mallin paikalliskoordinaateissa
  (x alttarille päin, y poikittain, lattia 0). Sisään tornin länsiovesta (keltainen kyltti "Sisään kirkkoon", vihje "Enter astu Keski-Porin kirkkoon"),
  ulos sisäoven edestä; siirtymässä 0,24 s häivytys. Minikartta ja kadunnimi seuraavat (`CHURCH.map` = ulkomallin kehys → karttametrit).
- **Malli `blender/kirkko_sisa.py`** (Blender/bpy, ~25 000 pintaa): kolmilaivainen halli 8 holvijaksoa (jako 5,54 m = ulkomallin tukipilarit), suippokaariset
  ristiholvit ruoteineen, 18 kimppupylvästä koristekenttineen, sivulehterit ja urkulehteri, urut (3 tornia + pillikentät), penkit 4 korttelia, saarnatuoli
  katoksineen, kuori (5 monikulmion sivua, 5 ikkunaa), koroke + portaat, alttari ja kehys, alttarikaide, 4 kattokruunua, virsitaulut, ovet.
  Mitat ulkomallista (kirkko.js: runko x −22…24,3, leveys ±11, kuori x > 24,3); rakenne ja värit luettu seurakunnan ja Ylen sisäkuvista
  (kirkkoporissa.fi kirkkosalikuva, rondo.fi urkukuva) – kuvia ei tallennettu. **Alttaritaulua (Ekman) ja lasimaalauksia (Enckell) EI kopioitu**: tilalla
  omat abstraktit pinnat (sääntö: taideteoksia ei kopioida).
- **Valo**: Cycles-leivonta valokartaksi (`kirkko_sisa_lm.jpg` 2048², UV1; DIFFUSE suora + epäsuora ilman väriä; ikkunat ja kruunut valaisevat),
  pintakuviot toistuvina tekstuureina UV0:ssa (kaikki itse piirrettyjä, PIL). Pelissä `MeshBasicMaterial({ map, lightMap })`,
  `lightMapIntensity = π · meta.lmax` (three r160 jakaa π:llä). `glow_`-materiaalit (lasit, kynttilät, ikkunasyvennykset) ilman valokarttaa.
  Pikkuosat (kruunut, kaide, pillit) ovat omassa `sisa_small`-verkossa ja käyttävät valokartan vasemman alakulman vakioväriä.
- **Törmäykset sisällä**: `meta.col` = janat [x0,y0,x1,y1,r] ja ympyrät [x,y,r] (seinät, pylväät, penkkikorttelit, kaide, alttari, saarnatuoli), `meta.room` = huoneen
  monikulmio; pelaaja r 0,32 työnnetään ulos (`walkCollide`). Kuorikorokkeelle noustaan vain portaista.

### Uudelleenajo
```
pip install bpy pillow numpy opencv-python-headless --break-system-packages
python3 blender/kirkko_sisa.py --out /home/claude/out_sisa --lm 2048 --samples 40      # ~12 min kahdella ytimellä (leivonta 10 min)
python3 tools/sisa_to_js.py /home/claude/out_sisa                                       # -> kirkko_sisa.js (aja pelikansiossa)
# esikatselu ilman leivontaa: --nobake --shots --samples 24 (5 kuvaa, 1,5 min / kuva)
```
Testi: `python3 -m http.server 8765` + playwright (`/opt/npm-tools/node_modules/`), `window.__game.walkAction()`, `window.__walk` (x, y, in, ix, iy, iyaw),
`window.__game.door()`, `window.__game.IN.ready`. Kuvat: `Claude outputs/kirkko_sisa_19_11/`.

### Auki / seuraavaksi (omistaja päättää)
- Lehtereille ei vielä pääse (portaat ja kaksitasoinen törmäys puuttuvat). Eteinen/torni puuttuu: ovesta tullaan suoraan saliin.
- Ulkomallin ikkunat ovat yksi korkea ikkuna / jakso, sisällä ala- ja yläikkuna (kuten oikeasti) – ulkomallia ei muutettu.
- Hahmo ei istu autossa/kopterissa näkyvästi (Sit-animaatio on valmiina), ovet eivät aukea, askelääniä ei ole.
- Muut kohteet samalla tekniikalla: sisätila omaksi `blender/<kohde>_sisa.py`:ksi, ovi `CHURCH`-tyyliin; `walkNear`/`walkAction` yleistettävä ovilistaksi.
- Valokartan pakkaus on väljä (tuhansia saarekkeita); 4096² tai parempi pakkaus terävöittäisi varjoja. Modalissa leivonta olisi nopeampi, mutta ei tarpeen.
- Antinkadun jono (toinen istunto teki 1726:n päädyn klo 11.30–12): 136, 409, 570, 276, 415.

## 19.11.2026 klo 12–14 – Antinkadun loput talot 136, 409, 570, 276, 415 – tehty, polttamatta → **ANTINKATU VALMIS**
Älä aloita näitä uudelleen uudessa chatissa. Jäljellä vain omistajan korjauskierros (alla "Auki") ja Modal-poltot.
- **136 Antinkatu 21a (c051):** `f136.py` + `SPEC[136]` (zones.py). LoD2-kuori on paljon taloa pienempi (itäseinä 16,3 m / 21,9 m) → rakennetaan
  **jalanjäljelle** (`footprint=True`, h 7,7) ja index.html: `L2OLD` + `HFIX {136: 7.7}`. Katutaso 1,5 m sisäänvedetty lasi (SPEC), yläkerta facades.json:
  elementtiräystäs reliefipaneeleineen (moduuli 2,43 m), ikkunanauha 2/moduuli, punainen kylttinauha (Liisankadulla länsiosa oranssi), `nobrick`.
  Panot: Antinkatu 21 (61.484163, 21.7946236 → x −73.33, y −204.7), Liisankatu 10 (61.484379, 21.7941287). Oikaisu: s = (s+1,5)·0,879, z = (z−0,1)·0,92.
- **409 Antinkatu 22 (c051):** `f409.py`: 6 krs, kaksi ikkunasaraketta + lasitettu parvekepino pylväällä + kaksi saraketta + parvekepino porttikäytävän päällä,
  valkoiset paneelit ikkunoiden alla, harmaa sokkeli. styles.json 409: `w #dccfb6` (kermanvaalea; oli harmaa). Tiilimateriaali (`kind brick`) tummui pelissä
  harmaaksi → käytössä `plaster`. Pano Antinkatu 22 (61.4827469, 21.7938609 → x −113.96, y −362.5), mittakaava ~1,0, jalkakäytävä z 0,3.
- **570 Antinkatu 27 B (c051):** oli tehty 18.11 (`_f570` zones.py); korjattu vain: parveketasot 5,6 + 2,75·k (ennen 3,6 + 3,05·k: katutason lasin ja
  parvekkeiden välissä on valkoinen vyö), pylväät 5,4 m, pohjoispään 3,3 m valkoinen kaista + kapea ikkunasarake (parvekkeet päättyvät s 17,6).
- **276 Antinkatu 20 (p1):** `f276.py`: keltainen puutalo, 1,7 m rapattu sokkeli, 6 korkeaa T-ikkunaa valkoisin vuorilaudoin, friisissä 4 ullakkoikkunaa,
  ei ovea Antinkadulla (pelissä oli keksitty ovi). Pano Antinkatu 22 (61.4830179, 21.793986 → x −107.3, y −332.3). Mikonkadun sivu mittaamatta.
- **415 Antinkatu 26 / Itsenäisyydenkatu 52 (c048):** `f415.py`: valkoinen rappaus, liiketila + 3 krs (SPEC 17,6 → 13,2 m, styles f 5 → 4), Antinkadulle pääty:
  2 näyteikkunaa, ikkunasarakkeet, kulman lasitettu parvekepino; Itsenäisyydenkatu: porrashuoneen lasi + katos, 3 saraketta, keltaiset paneelit, harmaa sokkeli.
  Panot Antinkatu 26 (61.4820247, 21.7935952 → x −128.1, y −442.9) ja Itsenäisyydenkatu 52 (61.482181, 21.7931281 → x −153.0, y −425.6).
- **Opit:** (1) LoD2-kuorelle piirrettävän seinän `a`/`b` pitää ottaa **raw.pkl:stä** (lod2.js pyöristää 0,1 m: 4 cm kuoren takana oleva linja piilotti
  kaikki alle 5 cm paksut itemit – 415). (2) c-lohkon poltto: `tar xzf pipeline/data/porikit_data.tgz` → siirrä `data/mmlproc/*` → `/home/claude/mmlproc/`,
  sitten `cd blender; PYTHONPATH=/home/claude python3 city.py c051 8` (~140 s). (3) gshot: `ZONE=-` striimatuille c-lohkoille (ZONE=c051 jäi odottamaan 180 s/kuva).
  (4) Länteen/pohjoiseen katsovat seinät jäävät poltossa varjoon – vaalea väri näyttää harmaalta, ei ole materiaalivirhe.
- **Modal:** ei uusia lohkoja – c048, c051 ja p1 ovat jo jonossa (`city 64 c048,c051,c052,c067`, `bake p1 …`).
- **Auki omistajalle (korjauskierros):** 1726:n korkeus (24,2 → ~20,5 m); 136:n LoD2/jalanjälki-ratkaisu ja katto; 409:n ylin 2 m umpiseinää (kuori 21,9 m,
  ikkunat loppuvat 19,6 m); 415:n näkemättömät osat (Antinkatu s < 1,9, Itsenäisyydenkatu s < 8,5 ja > 24); 276:n Mikonkadun sivu; 570:n eteläkappaleen
  ikkunat tarkistamatta; aiemmat: 1600:n tekstipalkit, portin vaalea maalaatta 1492/1493, tummina piirretyt portit.

## 19.11.2026 klo 14–15 – Juseliuksen mausoleumin sisätila + sisätilat listaksi (omistaja: "juseliuksen mauselium")

- **index.html:** sisätilat ovat nyt lista `PLACES` (haku `PLACES`): `{ key, file, name, room, label, hint, ok(), map(x, y), probe, markH }`. `WALK.in` = paikka (tai false),
  `WALK.at` = ovi jonka luona ollaan. `placeDoor(P)` etsii oven edestä ensimmäisen vapaan kohdan (`probe` = paikallinen piste oven sisäpuolella + suunta ulos),
  `loadInterior(P)` lataa `P.file + '.js'` omaksi ryhmäkseen `sceneIn`:iin (näkyvissä vain se, jossa ollaan). Kyltti (`P.mark`) syntyy kun kävelijä on alle 90 m ovesta.
  **Uusi kohde = yksi rivi PLACES-listaan + `blender/<nimi>_sisa.py` + `tools/sisa_to_js.py DIR <nimi>_sisa`.**
- **Mausoleumi:** ovi on ulkomallin (bl_mausoleumi.js) itäsivun kuistissa; hallin keskipiste kartalla (−1947.81, 193.18), sisätilan x-akseli suuntaan 166°
  (`MAUS`). Oven edessä ollut kuusi poistettu (`LIST.pop()` puusilmukassa satunnaislukujen jälkeen, muut puut ennallaan).
- **`blender/mausoleumi_sisa.py`** (käyttää kirkko_sisa.py:n työkaluja: `import kirkko_sisa as K`, `K.NAME`, `K.MATDEF` vaihdetaan): kahdeksankulmainen halli
  (seinän etäisyys 4,4 m, holvin kanta 9 m, laki 13,2 m), 6 korkeaa ruusukeikkunaa + ikkuna oven päällä, marmoriseinät ja kulmapylväät, maalauskentät ikkunoiden alla,
  vastapäinen syvennys (portaali, risti, korkea maalauskenttä), pronssiovet, keskellä pyöreä aukko (r 1,9 m) kaiteineen, alla krypta (lattia −3,4 m) ja valkoinen
  sarkofagi, kahdeksanlohkoinen holvi ruoteineen. 2 400 pintaa, valokartta 2048² (leivonta 6 min, 32 näytettä) → `mausoleumi_sisa.js` 1,3 Mt.
  **Freskoja (Gallen-Kallela, Halonen) ja pronssiovien reliefejä EI kopioitu** – kentissä omat abstraktit väripinnat. Huom. omistajalle: taiteilijat kuolivat
  1931/1933/1939, joten teosten tekijänoikeus on Suomessa päättynyt; jos halutaan oikeat aiheet, tarvitaan omat tai vapaasti lisensoidut valokuvat ja omistajan päätös.
- kirkko_sisa.py: lisätty `NAME` ja `LM_REF` (tulosnimet ja valokartan taso), `shots(V=...)`; tools/sisa_to_js.py sai nimiargumentin. Kirkon tulos ei muuttunut.
- Rakenne luettu kuvista (jalkipeli.net ym. kuvahaun kautta), kuvia ei tallennettu. Kryptaan ei pääse kävellen (näkyy aukosta); eteinen puuttuu.
- Testattu pilvessä: ovelle, sisään, ulos, sen jälkeen kirkkoon sisään (vain oikea ryhmä näkyvissä). Kuvat `Claude outputs/mausoleumi_sisa_19_11/`.
- Ei Modal-polttoa. Pushattavat: index.html, mausoleumi_sisa.js, blender/mausoleumi_sisa.py, blender/kirkko_sisa.py, tools/sisa_to_js.py (+ aiemmat hahmo.js, kirkko_sisa.js).

### 19.11 klo 12: puhekanavaan 20 uutta osaa
- `tools/radio/puhe.json`: +10 Pori-puhetta (kirjurinluoto, assat, raatihuone, marssi, suisto, ilmailu, tori, saa, muistilista, jokiranta) ja
  +10 keksityn yrityksen mainosta (lokkivakuutus, vastatuuli, hiekkalinna, yksisuuntainen, loylykopteri, ketjut, patjapori, karhunkammen, mutteri,
  sininennuotti). Yhteensä 40 osaa, silmukka 17,1 min. Uudet radio/puhe_*.mp3 (4,5 Mt) ja radio.json viety käyttäjän kansioon; ei kuunneltu pilvessä.
- `tools/radio/speak.py` tekee nyt vain osat, joita ei ole radio.jsonin "puhe"-listassa (`--all` tekee kaikki). Malli haetaan koneelta stagella
  (`radio/voice/fi_FI-harri-medium.onnx`, 63 Mt), `pip install "piper-tts>=1.5"`.

### 19.11.2026 klo 15.30 – mausoleumin maalauskentät: alkuperäisiä muistuttavat piirrokset (omistaja: "näissä voidaan tehdä muistuttavia freskoja")
- `blender/mausoleumi_sisa.py` `frescoes()`: kuusi kenttää (Kevät, Rakennus, Tuonelan joella, Hävitys, Talvi, Syksy) + syvennyksen korkea kenttä piirretään PIL:llä
  (tasaiset väripinnat, tummat ääriviivat, rakeisuus): aihe, sommittelun pääpiirteet ja väriala alkuperäisistä, ei valokuvia eikä jäljennöksiä.
  Seinät: k=1,2,3 → fresco1–3, k=5,6,7 → fresco4–6 (oikea järjestys hallissa tarkistamatta). Uudelleenleivottu (6 min) → `mausoleumi_sisa.js` 1,5 Mt.
- Lupa koskee mausoleumia; kirkon alttaritaulu ja lasimaalaukset ovat edelleen abstrakteja. Tyyli on pelkistetty – tarkempi jälki vaatisi käsin maalatut tekstuurit.
- index.html ei muuttunut. Kuva `Claude outputs/mausoleumi_sisa_19_11/maus_freskot.jpg`.

## 19.11.2026 klo 14–15 – ITSENÄISYYDENKATU, keskustan erä (omistaja: "keskusta ensin", 15 isoa taloa) – ALOITA TÄSTÄ

Kadun varrella on 62 rakennusta (33 kerros-/liiketaloa, 29 puutaloa/piharakennusta); värit ja kerrosluvut tarkistettu 13.–14.11 (styles `sv`).
Mitattu julkisivu (facades.json) tehdään ensin näille 15:lle. **Tee vain rivit, joissa lukee TEKEMÄTTÄ – valmiita ei aloiteta uudelleen.**

| ID | Mikä | Lohko | Tila |
|---|---|---|---|
| 415 | Itsenäisyydenkatu 52 / Antinkatu 26 | c048 | VALMIS 19.11 (f415.py) |
| 118 | Antinkatu 24 | c048 | VALMIS 18.11 |
| 116 | Antinlinna, Itsenäisyydenkadun julkisivu | c048 | VALMIS 19.11 (f116.py) |
| 119 | Itsenäisyydenkatu 41 | c063 | VALMIS 19.11 (f119.py) |
| 113 | matala keltainen talo 116:n itäpuolella | c063 | AUKI: LoD2-kuoressa on vain eteläosa, kadulle näkyvä matala lasikuistiosa puuttuu → vaatii jalanjälkiratkaisun (kuten 136) |
| 115 | kioskipaviljonki | c063 | VÄRI KORJATTU 19.11 (keltainen), julkisivu mittaamatta |
| 107 | Yrjönkatu 25 (1927) | c064 | VALMIS 19.11 (f107.py; vain Itsenäisyydenkadun pääty, Yrjönkadun pitkä sivu mittaamatta) |
| 121 | Palojoenkulma, Yrjönkatu 23 | c064 | VALMIS 19.11 (f121.py) |
| 600 | Hotelli Bepop, Itsenäisyydenkatu 37 | bepop (nimetty lohko, kuori 588) | VALMIS 19.11 (f588.py; katujulkisivu, nähty s 9,5–28, loput toistettu) |
| 601 | Itsenäisyydenkatu 35, Maakuntalinna (1959) | bepop (nimetty lohko, kuori 588) | VALMIS 19.11 (f588.py; katujulkisivu, nähty s 7,5–34,6, länsipää toistettu) |
| 585 | vanha linja-autoasema | c064 | OSITTAIN 19.11 (f585.py: Itsenäisyydenkadun pääty 13 m + Kuninkaantien länsisivu 18 m; koillis- ja eteläiset sivut mittaamatta) |
| 1228 | valkoinen 6 krs kulmatorni (1229-kuoren länsipää) | c064 (kuori 1229) | VALMIS 19.11 (f1228.py; vain Itsenäisyydenkadun sivu, tornin länsisivu mittaamatta) |
| 569 | Antinkatu 27 A | c048 | EI KADUN VARRESSA: eteläsivu on 10 m sisäänvedetty lautaaidan takana (aita tehty 18.11) – jätetään |
| 164 | Itsenäisyydenkatu 45, pysäköintitalo (569:n länsipuolella) | c051 | VALMIS 19.11 (f164.py; katujulkisivu + Mikonkadun pää, ajoaukot oikeina aukkoina, läpiajotesti – ks. luku "PYSÄKÖINTIHALLI 164") |
| 7 | Itsenäisyydenkatu 54 (1956) | c048 | VALMIS 19.11 (f7.py; itäiset 4 akselia peilattu, näkemättä) |
| 166 | Itsenäisyydenkatu 47, okrankeltainen 3 krs | c048 | VALMIS 19.11 (f166.py; koko katujulkisivu nähty) |
| 167 | Itsenäisyydenkatu 58, 8 krs, lasitetut parvekkeet (SPEC 13.11) | c048 | VALMIS 19.11 (f167.py; Itsenäisyydenkadun pääty + Eteläpuiston länsisivu, katutaso sisäänvedetty; länsisivun s < 4,5 ja pihan sivut mittaamatta) |

Sen jälkeen (omistajan päätöksellä): loput 18 isoa taloa (itään 1229–693, länteen 141–265), viimeisenä puutalot.

- **116 Antinlinna:** pylväsportaali ja nimikilpi ovat **Itsenäisyydenkadun** julkisivussa (seinä (−90.018,−451.231)→(−121.309,−443.652), 32,2 m), eivät Antinkadulla:
  aiempi `_al_pil` (pilasterit Antinkadun seinässä) poistettu SPEC[116]:n extrasta. `f116.py`: 8 ikkuna-akselia ruskeissa kaksikerroksisissa kehyksissä
  (kaidepaneeli + koristepaneeli), graniittiportaali + 2 pylvästä + attikalohko (nimi piirretty tyhjänä paneelina), sivuportaali, 2 näyteikkunaa.
  Pano Itsenäisyydenkatu 41 (61.4820789, 21.7940872 → x −101.9, y −436.9; h 140/194/245 p 12); s = (s+1,0)·0,952, z = (z−0,3)·0,93.
  zones.py: facades-silmukka ketjuttaa nyt aiemman `runalt`in (116:n palomuuripääty säilyy).
- **119:** `f119.py`: 2 krs roiskerappaus, tummat ikkunanpuitteet, 3 näyteikkunaa, 2 ovea, punainen kyltti. Räystäs 6,8 m, kuori 8,5 m → väli piirretty
  tummana kattokaistana. Pano (61.4820169, 21.7946426 → x −72.3, y −443.9; h 14 p 10). Näkyi vain s 1,5–18.
- **Opit:** (1) `winp`-kehys on 3 cm seinästä: sen alle jäävä `box` saa olla enintään 2,5 cm paksu, muuten ikkuna jää piiloon (116). (2) `tools`-apuri
  kadunpuoleisen seinän hakuun ei ole luotettava (W-polygonit): lue seinät `lod2.js`:stä ja tarkenna päätepisteet raw.pkl:stä. (3) Street View latautuu
  tarkalla pano-osoitteella 45–60 s: navigate + 5×10 s odotus + erillinen screenshot. Pohjoisjulkisivut jäävät poltossa varjoon (tummuvat).
- **Modal:** c048 on jo jonossa; **lisää c063** (119): `city 64 c048,c051,c052,c063,c064,c065,c067,c069,h100`.
- Vertailukuva `Claude outputs/itsenaisyydenkatu_116_119_vertailu_19_11.jpg`.

(Huom: toinen istunto kirjoitti tämän tiedoston välillä vanhemman pohjan päälle ja Itsenäisyydenkadun luku katosi – palautettu tähän. Stage aina juuri ennen vientiä.)

## 19.11.2026 klo 15–16 – MODAL-POLTOISTA PUUTTUIVAT MITATUT JULKISIVUT (korjattu) + 121

- **Vika:** omistaja ajoi jonon (PR #61, 15 lohkoa "ok"), mutta peliin ei tullut yhtään facades.json-julkisivua. Syy: Modalissa `pipeline/porikit/jobs.py`
  KOPIOI `zones.py`:n kansioon /home/claude (ei symlinkkiä) eikä kopioinut `facades.json`:ia; `zones.py` etsi sitä vain omasta kansiostaan ja jätti
  julkisivut hiljaa pois (`FACADES = {}`). Todiste: Modalin bl_c051.js 10 345 kärkeä, paikallinen 17 977; tori0 4 652 / 6 708. Koskee kaikkea 18.11 jälkeen.
- **Korjaus:** `blender/zones.py` etsii facades.json:n myös `$PORI_REPO/blender/` ja `$PORI_GAME/blender/` -kansioista ja tulostaa lokiin
  `facades.json: <polku>` tai `NOT FOUND`; `jobs.py` kopioi `blender/*.json` zones.py:n viereen. Testattu simuloimalla kopioitu asetelma (28 julkisivua löytyy).
- **Omistajan ajettava:** push → odota että Actions-työ **"porikit image"** on vihreä (rakentaa Modal-kuvan uudesta koodista) → vasta sitten
  `bake p1 tori0 tori1 tori2 tori3 tori4 kivi2 --samples 64` ja `city 64 c048,c051,c052,c063,c064,c065,c067,c069,h100` → "porikit collect" → yhdistä PR.
  **Tarkistus polton jälkeen:** bl_c051.js:n pitää kasvaa selvästi (kärkiä ~18 000); jos ei, katso Modal-lokista rivi `facades.json:`.
- **121 Palojoenkulma (c064):** `f121.py`: ruskeankeltainen tiili, 7 moduulia (5,7 m) tiilipilarien välissä: katutason ikkunanauha, ulkoneva tumma lasierkkeri,
  leveä ikkunarivi, 4 riviä nauhaikkunapareja. Pano Itsenäisyydenkatu 39 (61.481935, 21.7953921 → x −32.39, y −453.0; h 13 p 25), mittakaava 1,0.
  Moduuli mitattu kohdasta s 19–34 ja toistettu; päädyt ja ylin kerros näkemättä.
- **115:** vain väri (seinät keltaiset, SPEC + styles). **113:** ks. taulukko. Seuraavaksi taulukon TEKEMÄTTÄ-rivit: 107, 600, 601, 585, 1228, 569, 164, 7, 166, 167.
- SV-huomio: toinen ja kolmas suunta samasta panosta latautuvat hitaasti (60–90 s sumeana) – ota ensin leveä kuva ja mittaa moduuli, jos julkisivu toistuu.

### 19.11 klo 15: liikennevalot (index.html, ei polttoa)
- Data: `tools/roads/traffic_signals.json` (OSM, 124 solmua → 31 risteystä; haettu sovelluksen selaimella www.openstreetmap.org/api/0.6/map.json
  -ruuduilla, koska Overpass antaa 406 / CSP estää). index.html:ssä risteyskeskipisteet vakiona `SIGJ` liikennelohkossa (`cars`).
- Logiikka: jokainen katuverkon solmu, jolla ≥3 haaraa ja joka on <24 m risteyksestä, on valo-ohjattu (28 risteystä osuu verkkoon, 96 pylvästä);
  haarat kahteen ryhmään suunnan mukaan; kierto 40 s (16 vihreä, 3 keltainen, 1 kaikki punaisella). `sigState(n, from)`, `pedGo(n, from)`, `window.__sig`.
- Bottiautot: pysähtyvät 9 m ennen solmua punaiseen/keltaiseen, jonottavat 6,5 m välein, kiihdytys 2,5 ja jarrutus ≤7 m/s² (aiemmin vakionopeus).
  Simuloitu 120 s: 0 punaisia päin, pisin seisonta 21 s, ei lukkiutumia. Pelaajaa valot eivät sido.
- Pylväät rakennetaan 9 s käynnistyksen jälkeen (yksisuuntaisuus tulee roads.js:stä); autolle 3 valoa, kadun yli jalankulkijan punainen/vihreä.
- **Pelissä ei ole bottikävelijöitä** (vain pelaaja kävelee) – jos niitä tehdään, `pedGo` kertoo saako haaran ylittää.

### 19.11.2026 klo 16 – oikeat maalaukset (omistaja: "niissäkin voidaan käyttää oikeita"; latauslupa kysytty ja saatu 8 kuvalle)
- **Lähteet `blender/tex_art/`** (vapaat, saa olla GitHubissa): `gk_kevat, gk_rakennus, gk_tuonela, gk_havitys, gk_talvi, gk_syksy, gk_kosmos.jpg` = Akseli Gallen-Kallelan
  teokset/esityöt Juseliuksen mausoleumin freskoihin 1901–03 (Wikimedia Commons, public domain; osa Kansallisgallerian kokoelmista) ja `ekman_luonnos.jpg` =
  R. W. Ekman, "Kristuksen ylösnousemus, nykyisen Keski-Porin kirkon alttaritaulun luonnos" (Kansallisgalleria, Finna `kansallisgalleria.7E7BA4F7E0D580BB618DCBA12F84FFA6`, CC0).
  Koko n. 739 px: pilvi ei pääse Wikimediaan/Finnaan (proxy 403), joten kuvat otettiin sovelluksen selaimen kuvakaappauksina (`?width=700`) ja rajattiin.
  Huom: nämä ovat ESITÖITÄ/luonnoksia, eivät valokuvia itse seinäfreskoista tai valmiista alttaritaulusta; Tuonelan joella -työssä on alastomia hahmoja kuten alkuperäisessä.
- **Mausoleumi:** `frescoes()` käyttää tex_art-kuvia jos ne ovat olemassa (muuten omat piirrokset varalla); kentät 3,3 × 1,72 m, syvennyksessä Kosmos. Uudelleenleivottu.
  Kenttien järjestys seinillä edelleen tarkistamatta.
- **Kirkko:** alttaritauluna Ekmanin luonnos (rajattu kehykseen 0,694). **Enckellin lasimaalauksista ei löytynyt vapaata kuvaa** (Commons, Finna) → kuorin ikkunoissa
  alkuperäisiä muistuttava oma piirros (sininen viittahahmo, sädekehä, ruusuke). Jos omistaja kuvaa ikkunat itse, ne voi vaihtaa samalla tavalla.
  Kirkkoa EI leivottu uudelleen: `tools/glb_swap_images.py in.glb out.glb altar=... glass_apse=...` vaihtaa GLB:n upotetut kuvat geometriaan koskematta.
  kirkko_sisa.py tuottaa samat tekstuurit seuraavassa täydessä ajossa.
- **index.html:** tekijätietoriville (#credit) lisätty maalausten lähdemaininta. Pushattavat: index.html, kirkko_sisa.js, mausoleumi_sisa.js, blender/tex_art/*,
  blender/kirkko_sisa.py, blender/mausoleumi_sisa.py, tools/glb_swap_images.py. Kuva `Claude outputs/mausoleumi_sisa_19_11/oikeat_maalaukset.jpg`.

### 19.11 klo 16: bottikävelijät (index.html + walk.js + npc_*.js, ei polttoa)
- Mallit omistajalta: `npc_nainen_a/nainen_b/mies_a/mies_b/tytto/poika.js` (GLB base64:nä kuten hahmo.js; Idle 3 s, Walk 1 s, 53 luuta, ~11–12k kolmiota).
- Verkko: `python3 tools/roads/build_walk.py` → `walk.js` (OSM footway, sidewalk, pedestrian, path, steps, cycleway; 3970 solmua, 4522 särmää;
  särmä joka ylittää tai päättyy ajoradan keskiviivaan = suojatien puolikas, lippu 1). Kävelijät liikkuvat VAIN tässä verkossa.
- index.html: lohko "people on foot" ennen `window.__game`-riviä, `window.__npc` (`update(dt)` pääsilmukassa cars.update:n jälkeen). Enintään 30 hahmoa
  (kosketuslaitteella 14), ryhmät syntyvät 45–150 m pelaajasta ja poistuvat >185 m; animaatio vain <110 m.
- **Omistajan säännöt:** lapsi (tytto/poika) kulkee aina vähintään yhden huoltajan kanssa (mies_a, nainen_a tai nainen_b); muut aikuiset yksin tai pareittain;
  mies_b harvoin (paino 0,07). Jako: 45 % yksin, 20 % kaksi aikuista, 35 % perhe (huoltaja, 30 % +toinen aikuinen, 1–2 lasta).
- Valot: suojatien reunalla ryhmä etsii lähimmän valopylvään (<16 m, kadun suunta poikittain) ja odottaa `__sig.ped`-vihreää; valottomat suojatiet
  ylitetään suoraan (autot eivät väistä kävelijöitä, eivätkä kävelijät autoja). Simuloitu 5 min: ei virheitä, ei lapsia ilman huoltajaa, pisin odotus 20 s.
- Auki: OSM-polku voi olla pari metriä sivussa pelin kivetyksestä (puistossa nurmella); kävelijät eivät väistä pelaajaa eivätkä toisiaan.

### 19.11 klo 16.30: valopylväät jalkakäytävän reunaan
- `sigBuild` odottaa roads.js:ää (`window.__roads`) ja hakee pysäytysviivalta oikealle ensimmäisen jalkakäytäväruudun (`ROAD.paveAt`, 0,5 m askelin, enint. 25 m),
  pylväs 0,7 m sen sisään ja jalkakäytävän korkeudelle. Testissä (haku 15 m) 49/96 osui jalkakäytävälle; loput ovat pääosin katugeometrian
  ydinalueen ulkopuolella, missä jalkakäytävämaskia ei ole → vanha arvaus 4,6 m keskiviivasta. Keskustassa arvaukselle jäi 7 (Itsenäisyydenkatu, Mikonkatu).

### 19.11 klo 17: liikennevalot omistajan Blender-malleilla
- `liikennevalot.js` = {yhdistelma, uloke, jalankulkija}: GLB:t base64:nä (lähde `tools/props/porikopteri_liikennevalot.py`, ajo
  `blender --background --python … -- --type yhdistelma|jalankulkija|uloke`; origo tolpan juuressa, ajoneuvo-opastin +Z, ajorata −X).
- index.html `sigBuild`: laatikkopylväät poistettu. Jokainen mallin mesh on InstancedMesh; lamppusolmut (Veh_/Over_/Ped_*, Button_Light) saavat
  MeshBasicMaterialin ja pylväskohtaisen värin solmun extras onColor/offColor -arvoista (`sigUpd` joka ruudulla).
- Tyypit: oikean reunan pylväs `yhdistelma`, tai `uloke` kun jalkakäytävä on >6,2 m kaistan keskiviivasta; lisäksi vastakkaiselle reunalle `jalankulkija`
  (180° käännettynä), jos sieltä löytyy jalkakäytävä. Yhteensä 144 pylvästä. Painonapin valo palaa, kun jalankulkijalla on punainen.

### 19.11 klo 17.30: valopylväät reunakiven taakse myös keskikaistoilla (Mikonkatu)
- Syy: pylväs haki oikealta JALKAKÄYTÄVÄÄ; puistokadun keskikaistalla (nurmi) sitä ei ole → jäi arvaukseen 4,6 m = keskelle ajorataa.
- Korjaus: roads-rasteri `M` on nyt bittimaski (1 jalkakäytävä, 2 ajorata), uusi `ROAD.asphAt`. `sigBuild` kulkee pysäytysviivalta (aina 9 m ennen solmua,
  tarvittaessa 14 m) sivulle asfaltin yli ja panee pylvään 0,7 m ensimmäisen ei-asfalttiruudun taakse (jalkakäytävä, nurmikeskikaista tai saareke);
  sama vasemmalle jalankulkijapylväälle. Ytimen 54 pääpylväästä arvaukselle jäi 2: (-312,-379) Itsenäisyydenkatu/Eteläpuisto ja (206,-514)
  Itsenäisyydenkatu/Vähälinnankatu. Yhteensä 150 pylvästä (52 yhdistelmä, 44 uloke, 54 jalankulkija).

### 19.11 klo 18: Radio Porikopteri = puhe + pop, radio myös kopteriin
- Kanavat nyt: **Radio Porikopteri** (1., käynnistyy alussa sekä autossa että kopterissa), Electric, Rock, pois. Pop-kanava ja erillinen Puhe poistettu.
- radio.json: avaimet `porikopteri`, `electric`, `rock`. `porikopteri` = 40 puheosaa, joka neljännen jälkeen tunnus + pop_1..3 vuorotellen (60 riviä, 40,9 min).
  `tools/radio/speak.py` rakentaa lomituksen (kappaleet luetaan vanhasta pop-listasta tai porikopteri-listan pop_*-riveistä).
- puhe.json: avaus ja loppu kirjoitettu uudelleen (id:t `avaus2`, `loppu2`; ei enää "puhekanava"). Vanhat radio/puhe_avaus.mp3 ja puhe_loppu.mp3 jäivät
  kansioon käyttämättöminä (poisto vain omistajan luvalla).
- index.html: `RADIO.names = ['pois', 'Porikopteri', 'Electric', 'Rock']`; R-näppäin, ◀▶-painikkeet ja 📻-kosketuspainike toimivat myös kopterissa
  (luokka `ride-only`: näkyy autossa ja kopterissa, ei kävellessä; kopterissa 📻 on ▲▼🚶-painikkeiden yläpuolella, bottom 232 px). Ei testattu selaimessa.
- 19.11 klo 18.15 (omistaja): Radio Porikopterin järjestys on nyt **spiikki, mainos, spiikki, mainos, tunnus + kappale**, ja sama alusta. 23 spiikkiä käydään
  järjestyksessä kerran, 17 mainosta kiertää (6 kuullaan kahdesti), pop_1..3 vuorotellen: 66 riviä, 44,8 min. Vain radio.json ja speak.py muuttuivat.

## 19.11.2026 klo 16–17 – Itsenäisyydenkatu jatkuu: 107 ja 7 (testipoltettu, Modal-polttamatta)
- **Modal toimii nyt** (PR #62: facades.json mukana, c051 17 977 kärkeä). Omistaja ilmoitti "katot irti seinistä keskustassa" – EI toistunut pilvessä
  (GitHubin versio c3af284, 9 näkymää; vanhat vs uudet lohkot identtiset katoiltaan; shells-nostot samat). Odottaa omistajan kuvakaappausta.
- **107 Yrjönkatu 25:** `f107.py`, pohjoispääty 12,1 m: harmaanbeige rappaus, profiloitu räystäslista, 3 kuusiruutuista ikkunaa, 2 näyteikkunaa, pariovi + portaat.
  Pano Itsenäisyydenkatu 46 (61.4819137, 21.7955776 → x −22.5, y −455.4; h 165 p 8). Länsiakseli symmetrian perusteella.
- **7 Itsenäisyydenkatu 54:** `f7.py`, 25,3 m: keltainen roiskerappaus, 3 krs, valkopuitteiset ikkunat 2,3 m välein + harmaanvihreä kivirouhepaneeli alla,
  kellari-ikkunat, tiilisokkeli, porrashuonesyvennys vihrein parvekelevyin. Pano Itsenäisyydenkatu 54 (61.4822671, 21.792381 → x −192.8, y −416.0; h 193 p 14).
- Kaksi c-lohkon polttoa yhtä aikaa kaatuu muistiin (8 Gt) – aja peräkkäin. **Modal:** `city 64 c048,c064` (107 ja 7 lisätty).
- Jäljellä taulukosta: 600, 601, 585, 1228, 164, 166, 167 (+113 auki, 115 mittaamatta).
- 19.11 klo 18.30 (omistaja: kappaleet ovat pitkiä): Radio Porikopterissa nyt **kolme** spiikki + mainos -paria ennen tunnusta ja kappaletta
  (`PAIRS = 3` speak.py:ssä). 22 spiikkiä, 18 mainosta (4 kahdesti), 8 kappaleen soittoa: 60 riviä, 37,4 min. Vain radio.json ja speak.py.

## SISÄTILAT JA JALANKULKU – ALOITA TÄSTÄ (kooste 19.11.2026; yksityiskohdat luvuissa "klo 12–13 Jalankulku", "klo 14–15 Juseliuksen mausoleumi", "klo 15.30" ja "klo 16 oikeat maalaukset")

- **Tila:** kaikki on omistajan kansiossa, pushaamatta. **Ei Modal-polttoa** – näkyy heti pushin jälkeen.
  Pushattavat: `index.html`, `hahmo.js`, `kirkko_sisa.js`, `mausoleumi_sisa.js`, `blender/kirkko_sisa.py`, `blender/mausoleumi_sisa.py`, `blender/tex_art/*.jpg`,
  `tools/sisa_to_js.py`, `tools/glb_swap_images.py`, `tools/hahmo/porikopteri_hahmo.py`.
- **Pelissä:** Enter (F autossa/jalan, kosketuksella 🚶) = ulos pysähtyneestä autosta tai maahan laskeutuneesta kopterista, takaisin kyytiin, ovesta sisään/ulos.
  W/S, A/D, Q/E, Shift juoksu, C kamera. Kierroksen kello seisoo jalan. Koodi: index.html, haku `WALK` ja `PLACES`.
- **Valmiit sisätilat:** Keski-Porin kirkko (tornin länsiovi), Juseliuksen mausoleumi (itäsivun kuisti) ja **Porin Teatteri** (Hallituskadun julkisivun keskeltä; ks. alaluku "Porin Teatteri"). Kumpikin on oma moduulinsa (GLB + valokartta + törmäykset),
  ladataan kun kävelijä on alle 90 m ovesta.
- **Uusi kohde:** 1) `blender/<nimi>_sisa.py` (malli: mausoleumi_sisa.py, käyttää kirkko_sisa.py:n työkaluja), 2) `python3 blender/<nimi>_sisa.py --out DIR --lm 2048 --samples 32`,
  3) pelikansiossa `python3 tools/sisa_to_js.py DIR <nimi>_sisa`, 4) yksi rivi `PLACES`-listaan (map = paikallinen → karttametrit, probe = oven kohta ja suunta ulos).
  Pelkkä tekstuurin vaihto ilman leivontaa: `tools/glb_swap_images.py`. Ympäristö: `pip install bpy pillow numpy opencv-python-headless --break-system-packages`.
- **Taideteokset (omistajan päätökset 19.11):** mausoleumissa Gallen-Kallelan esityöt (public domain, Commons), kirkossa Ekmanin alttaritaulun luonnos (Kansallisgalleria, CC0);
  lähdemaininta on #credit-rivillä. Enckellin lasimaalauksista ei löytynyt vapaata kuvaa → kuorin ikkunoissa muistuttava oma piirros.
  Pilvi ei pääse Wikimediaan/Finnaan: kuvat sovelluksen selaimen kuvakaappauksina. Lataukset edelleen vain luvalla.
- **Auki (omistaja päättää):** seuraava kohde; kirkon lehterit ja eteinen; mausoleumin kryptaan kävely; freskojen oikea järjestys seinillä; Tuonelan joella -työn alastomat
  hahmot (pidetäänkö); Enckellin ikkunat omista valokuvista; hahmo näkyviin kulkuneuvoon (Sit-animaatio), askeläänet, ovien avautuminen.

### 19.11.2026 klo 19–20.30 – Porin Teatteri: aula, kiertokäytävä, päänäyttämön sali, näyttämö ja yläkerran kahvila (omistaja: "Porin Teatteri seuraavaksi")
- **Tila:** kansiossa, pushaamatta, ei Modal-polttoa. Pushattavat: `index.html`, `teatteri_sisa.js` (4,8 Mt), `blender/teatteri_sisa.py`. Kuvat `Claude outputs/teatteri_sisa_19_11/`.
- **Omistajan ohjeet ja kuvat (chatissa 19.11):** aulan takaosassa pyöreä punainen seinä, jonka molemmilta puolilta kierretään saliin (kuva: valkoiset pylväät
  messinkipalloineen, sitaattitaulu, VASEN/OIKEA); yläkerran kahvila (2 kuvaa: kolme kaari-ikkunaa, harmaanvioletit seinät, ovenpäällykset, kristallikruunu,
  marmoripöydät ja mustat tuolit, takana oranssi syvennys ja kullatut pylväät); linkki jalkipeli.net "Porissa sijaitsee mahdollisesti Suomen upein teatterirakennus"
  (EI vielä luettu – käytä seuraavalla kierroksella). Salin rakenne ja värit luettu akukon.fi:n referenssikuvista. Kuvia ei tallennettu peliin eikä GitHubiin.
- **Sijainti:** vanha teatteritalo on jalanjäljen (city.js b 1358) ITÄOSA: Hallituskadun julkisivu (−208.6, 388.2)…(−185.5, 382.9), 23,8 m, keskirisaliitti 8,8 m.
  index.html `TEAT`: origo (−199.62, 374.34) = salin takaseinän keskikohta 11,5 m julkisivusta, x-akseli kohti näyttämöä (suunta 193°), y vasemmalle (itään).
  Ulko-ovi löytyi kohdasta (−196.6, 387.3). Ulkomallissa (bl_teatteri.js) ei ole ovea tällä kohtaa – vain kyltti.
- **Malli `blender/teatteri_sisa.py`** (10 900 pintaa, valokartta 3072², leivonta 8 min 24 näytteellä; ajo `--out DIR --lm 3072 --samples 24`, esikatselu
  `SHOTS=aula,sali --nobake --shots --samples 14`): aula x −11…−1,6 (4 pylvästä, 3 ulko-ovea, sitaattitaulu), takaseinän aukosta näkyy salin pyöreä ulkoseinä
  (säde 7,7 m, punainen + kultanauha); kiertokäytävä (ulkosäde 9,9 m) vie kummaltakin puolelta salin sivuoville (x 8,9…10,3). Sali: puolileveys 7,2 m, takakaari,
  katto 9,4 m, parvi (kullattu kaide, 83 istuinta), permanto 186 istuinta kaarevissa riveissä, näyttämöaukko (kori­kaari, medaljongit, punainen esirippu ja kappa),
  näyttämö +1,0 m (portaat salin etukulmista), sininen taustakangas, kattomaalausten kehä (7 pyöreää) ja kattokruunu.
- **Kahvila** on mallissa siirretty **x + 100 m** (`XO`); aulan itäpäädyn ovesta (kyltti KAHVILA ↑) Enter siirtää sinne ja takaisin. Kartta taittaa x > 50 takaisin (PLACES.map).
- **index.html, uudet yleiset ominaisuudet (toimivat kaikille sisätiloille, vanhat ennallaan):** `meta.lev` = lattiatasot suorakulmioina [x0,y0,x1,y1,z] (`inFloor`),
  `meta.rooms` = useita huonemonikulmioita (`inRoom`), `meta.ports` = sisäovet [x, y, r, kohde x, y, suunta, vihje] (`walkNear` → 'port'), ja kamera pysähtyy
  seiniin (`col.seg`) kun `meta.rooms` on olemassa. Näillä saa myös kirkon lehterit ja mausoleumin kryptan (siirretty kopio + ovi).
- **EI kopioitu / omaa:** kattomaalaukset (Wetterstrand / Wuorio 1884 – tekijänoikeus päättynyt, oikeat voi vaihtaa jos omistaja haluaa ja kuvat saadaan),
  näyttämöaukon reliefi ja rintakuvat (pelkistetyt, ei kenenkään näköiset), julisteet ja muotokuvat (jätetty pois). Sitaattitaulun teksti (Satakunta 14.2.1874)
  on kirjoitettu omalla kirjasimella – omistaja päättää, pidetäänkö.
- **Arvioitua (ei mitattu):** kaikki mitat (sovitettu jalanjälkeen), permannon käytäväjako, portaat näyttämölle, näyttämön takaosa, kahvilan koko ja ovien paikat,
  aulan ikkunat ja pylväsjako. Kahvilaan mennään ovesta ilman näkyvää porrasta.
- **Auki:** parvelle ei pääse (onnistuisi `ports`-ovella); lämpiö/ravintolasali ja Pieni näyttämö puuttuvat; ulkomalliin oikea pääovi; jalkipeli.net-artikkelin
  kuvien läpikäynti ja korjauskierros omistajan kanssa; testattu vain pilvessä (ovi, aula, käytävä, sali, näyttämö, kahvila ja takaisin; ei konsolivirheitä).

### 19.11.2026 klo 21 – teatterin kattoon oikeat maalaukset vapaasta valokuvasta (omistaja: "katsotaan löytyykö vapaita, jos löytyy niin voidaan käyttää")
- **Vapaat lähteet (Finna, Satakunnan Museo, CC BY 4.0 – lähde mainittava):** DIA4374 (Sven Raita 1955, värikuva koko katosta, `satakunnanmuseo.75655844-4677-40AD-8786-46E364600409`)
  = KÄYTETTY; SATO3203 (1932, mv, kolme maalausta ja kulmamaalaus läheltä, `…532F3B2A-BC3C-4FAD-B26C-127CA81F27B3`), SMK1800:1 (1956, mv, sali taaksepäin + katto,
  `…37A1A46D-5F42-4ECE-B25F-D3AB5D458EEB`) ja SMK1801:1 (1956, parvi ja näyttämöaukko, `…FBAD1E88-C9AB-4F1B-9FEC-1BFEB9AB83F7`) = käyttämättä, hyviä jatkoon.
  **EI vapaa:** Satakunnan Kansan kuva-arkiston SK1051:3492 (1953, "tekijänoikeuden piirissä, käyttö maksullista"). Wikimedia Commonsissa vain ulkokuvia.
- **Tehty:** DIA4374 otettu sovelluksen selaimesta kahtena 1:1-kuvakaappauksena (pilvi ei pääse Finnaan), oikaistu homografialla ylhäältä katsotuksi (kehän 8 pistettä,
  keskiritilä ja kuuden maalauksen keskipisteet; rms 8 px), dian violetti sävy korjattu, kattokruunun häikäisy tasoitettu → `blender/tex_art/teatteri_katto_dia4374.jpg` (900², rivi 0 =
  näyttämön puoli). `teatteri_sisa.py` `ceiling_tex()` käyttää sitä pyöreässä kentässä (varalla omat piirrokset). GLB:n kuva vaihdettu `tools/glb_swap_images.py … ceil=…` – EI uutta leivontaa.
- **Puutteet:** takimmainen (seitsemäs, pienin) maalaus jää kuvassa kattokruunun taakse → tasainen vaalea läiskä; erottelu n. 1,5 cm/px ja 1955 värit (haalistunut dia), ei nykyinen
  restauroitu asu; kulmamaalauksia ei ole (tasainen pohja). Tarkempi: SATO3203:n kolme maalausta mustavalkoisina tai omistajan omat valokuvat.
- **Kuvista opittua, korjaamatta:** permannon takaseinässä on VIISI ovea käytävään ja parven alla konsolit + valorivi (SMK1800:1) – pelissä ovet ovat vain sivuilla;
  keskellä kattoa on pyöreä ritilä punaisine kehineen (nyt mukana kuvassa).
- index.html: #credit-riville lähdemaininta. Pushattavat lisäksi: `blender/tex_art/teatteri_katto_dia4374.jpg`. Kuva `Claude outputs/teatteri_sisa_19_11/katto_vertailu.jpg`.

### 19.11.2026 klo 22 – Porin Teatterin ULKOASU uusittu (omistaja: "teatterin ulkoasu pitää päivittää", 5 valokuvaa chatissa + "tarkista että portaat tulevat ovelle")
- **Tila:** kansiossa, pushaamatta. `blender/lm.py` (haara `teatteri` + `mml_shell(..., zoff=)` ja materiaali funktiona), `bl_teatteri.js` (paikallinen leivonta 4096², 20 näytettä,
  2,6 Mt), `index.html` (teatterin oven kohta portaiden juureen: `probe: [-15.8, …]`). Kuva `Claude outputs/teatteri_sisa_19_11/teatteri_ulko_vertailu.jpg` (sisältää SV:tä, vain paikallisesti).
- **Ennen:** koko jalanjälki yhtenä keltaisena laatikkona (`classic`, h 12,5). **Nyt:** MML:n LoD2-kuori (rakennus 1358) puettuna: vanha teatteri (itäosa) keltainen `#e7c886`,
  keskirisaliitti (8,9 m): valkoinen rustikoitu alakerta, kolme ruskeaa kaariovea, viisi askelmaa, yläkerrassa kolme korkeaa kaari-ikkunaa ja pylväät, valkoinen palkisto ja
  attika + tyhjä kilpi (nimikilpiä ei kopioida); siivet: 2 ikkuna-akselia, alhaalla suorat valkoiset kehykset, ylhäällä kehys + kaaripääty, valkoinen kerrosvyö ja räystäs, harmaa sokkeli.
  Laajennus (1974, länsi): ruskeanharmaa `#8f8273`, seinät paljaat, nauhaikkunat vain Hallituskadun päädyssä (SV).
- **Mitat Street View -kuvasta** (pano 61.4895954, 21.7923958 → x −192,0 y 400,7, h 193 p 8, huhti 2026; syvyys siipiin 15,9 m, risaliittiin 14,1 m, seinän juuri 1,64 m kameran alla):
  siiven räystäs 10,2 m, attikan yläreuna 12,2 m, kerrosvyö 4,3–5,3, alaikkuna 1,35–3,45, yläikkuna 5,4–7,7, ovet 0,75–3,4 (jako 2,1 m), isot ikkunat 5,0–8,1 (jako 2,06 m).
- **Kaksi korkeusoppia:** (1) LoD2-kuoren nolla on koko korttelin alin maanpinta (laajennuksen syvennetty piha): Hallituskadulla kuori oli **3,1 m liian korkea** (räystäs 13,3 vs 10,2)
  → `zoff=3.1`. (2) Pelissä jalkakäytävä on tässä n. 0,6 m mallin nollan yläpuolella (portaat ja sokkeli jäivät piiloon) → koko malli nostettu 0,6 m ja alle tasainen sokkelihelma.
  Sama tarkistus kannattaa tehdä muille `mml_shell`-maamerkeille.
- **Portaat ja ovi:** viisi askelmaa nousee oville; pelaajan ovipiste (−196,0, 390,2) on portaiden juurella ovien edessä (testattu: vihje näkyy, sisään pääsee). Portaille ei nousta
  (ulkona ei ole porrastörmäystä) – sisään mennään juurelta.
- **Näkemättä / oletettu:** vanhan osan itä- ja takaseinän sekä näyttämötornin ikkunat (toistettu siipien akseleilla), laajennuksen Teatterikadun ja takapuolen seinät, lasikäytävä
  ja terassi lipunmyynnin edessä (omistajan kuvissa näkyy – tekemättä), lyhdyt, lipputangot, katon rautakoriste. Katto tummanruskea pelti (omistajan kuva).
- **Sisätila vs. kuori:** vanhan osan salilohkon ulkoseinä on kuoressa 9,2 m akselista, sisätilan kiertokäytävä ulottuu 9,9 m:iin → sisätila on n. 0,7 m liian leveä (korjaamatta).
- **Modal (valinnainen):** paikallinen leivonta on kansiossa ja riittää; tarkempi saadaan komennolla `landmarks teatteri` pushin jälkeen.

### 20.11.2026 yö – uudet sisätilat: Porin jäähalli ja Porin taidemuseo (omistaja: "tehdään jäähalli ja taidemuseo")
- **Tila:** kansiossa, pushaamatta, ei Modal-polttoa. Pushattavat: `index.html`, `areena_sisa.js` (1,4 Mt), `taidemuseo_sisa.js` (1,0 Mt), `blender/areena_sisa.py`,
  `blender/taidemuseo_sisa.py`. Kuva `Claude outputs/sisatilat_20_11/jaahalli_taidemuseo_pelissa.jpg`. Kumpikin: valokartta 2048², 24 näytettä (leivonta 8 / 12 min).
- **index.html:** PLACES-listaan kaksi riviä + `AREE`, `TAIM` ja apuri `lin2(T)` (paikallinen → kartta). Ei muita muutoksia.
- **Jäähalli (`areena_sisa.py`):** origo länsiseinän keskellä (−1676.6, −1377.45) = ulkomallin punainen sisäänkäynti, x kaukalon pituussuuntaan (116°). Kaukalo 56 × 28 m
  (viivat ja ympyrät, EI mainoksia), laidat ja portit pitkien sivujen keskellä (jäälle pääsee), **eteläsivulla SEISOMAKATSOMO** keskellä alhaalla (12 askelmaa, kaiteet,
  käveltävä) ja punaiset C-istuinrivit sen yllä ja päissä, pohjoissivulla A-katsomon mustat istuimet (16 riviä, 3 porraskäytävää, käveltävä ylätasanteelle asti),
  päädyissä punaiset rivit (lännessä aukko pääoven kohdalla), valkoinen katto palkkeineen ja ilmakanavineen, mediakuutio (tyhjä näyttö), kuusi numeroviiriä (22, 13, 12, 5, 4, 2,
  ilman logoja). Katsomot käyttävät `meta.lev`-tasoja.
- **Omistajan kuvat ja kartta (chatissa 20.11):** katsomokartta (A alhaalla musta, C ylhäällä + seisomakatsomo, D ja B päädyissä, BAR ja MEDIA kulmissa), D-päädyn ravintolaterassit,
  D-käytävä (baari, punainen parvi), kuvat A-katsomosta ja D-päädystä; "seisomakatsomo on hallin sydän". **Tekemättä näistä:** D-päädyn ravintolatasot, D-käytävä ja baari,
  kulmakatsomot (C1, C5, D5, B5), aitiotaso ja LED-nauha, suojalasit ja -verkot. Kumpi pääty on D: oletettu ITÄ (kartan mukaan seisomakatsomolta katsoen oikealla) – tarkista.
- **Taidemuseo (`taidemuseo_sisa.py`):** Halli 44 × 17 m, origo sisäänvedetyn pohjoisjulkisivun keskellä (−96.85, 467.4), x sisään etelään. Punaruskea tiililaattalattia, valkoiset
  seinät, kaari-ikkunat joelle, lasikatto ja valkoiset teräsristikot, ruskeat pylväät, kolme irtoseinää, jalustat, tiski. **Teokset ovat omia abstrakteja sommitelmia** (ei kopioita).
  Ovipiste (−96.1, 470.8) on 3,4 m seinästä kadulla: lähempänä pelaaja jäi ulkomallin räystään alle / katolle (`probe: [-3.0, …]`).
- **Arvioitua:** kaikki mitat (sovitettu jalanjälkiin), taidemuseon pääoven paikka (oletettu pohjoisjulkisivun keskelle – tarkista), jäähallin pääovi (ulkomallin mukaan lännessä).
- **Testi (pilvi):** jäähalli: ulkoa ovelle, sisään, jäälle, seisomakatsomoon (z 1,9), A-katsomon ylätasanteelle (z 5,8), ei virheitä. Taidemuseo: sisään ovipisteestä ja kolme
  näkymää; kyydistä nousua museon edessä EI saatu testattua (testiajuri hidas Kivi-Porin lohkojen latautuessa) – kokeile pelissä.

## ILLAN MODAL-JONO (omistaja polttaa illalla – PÄIVITÄ TÄTÄ LISTAA, älä tee uutta)
(Sisätilat ja jalankulku eivät kuulu tähän jonoon: ne eivät tarvitse polttoa, vain pushin – ks. edellinen luku "SISÄTILAT JA JALANKULKU".)
Viimeisin onnistunut poltto: PR #62 klo 12.18 (sisältää kaiken 19.11 klo 12 mennessä viedyn). Sen jälkeen kertyneet:

| Lohko | Talot | Lisätty |
|---|---|---|
| c048 | 7 (Itsenäisyydenkatu 54), 166 (Itsenäisyydenkatu 47), 167 (Itsenäisyydenkatu 58) | 19.11 klo 17; 166 lisätty myöhemmin 19.11 |
| c064 | 107 (Yrjönkatu 25), 585 (vanha linja-autoasema, pohjoispääty + länsisivu), 1228 (kulmatorni, kuori 1229), 111 + 109 (Rautatienpuistokatu 3) | 19.11 klo 17; 585 lisätty myöhemmin 19.11 |
| c051 | 164 (Itsenäisyydenkatu 45, pysäköintitalo) | 19.11 |
| c063 | 124 (Rautatienpuistokatu 5, molemmat siivet) | 19.11 |
| c061 | 13 (lamelli Rautatienpuistokadun kaakkoispuolella) | 19.11 |
| c047 | 36 (Rautatienpuistokatu 8) | 19.11 |
| c046 | 34 (Rautatienpuistokatu 12) | 19.11 |

Ajettava illalla (push ensin, odota "porikit image" vihreäksi): `city 64 c046,c047,c048,c051,c061,c063,c064` **ja** `bake bepop --samples 64` (600 ja 601)

## 19.11.2026 klo 17 – (VANHA aloitusluku; korvattu tiedoston LOPUN luvulla "19.11.2026 ilta – ALOITA TÄSTÄ") JULKISIVUINVENTAARIO, Itsenäisyydenkatu jatkuu

Vastaa suomeksi, lyhyesti, kuva jokaisesta muutoksesta (Street View vasemmalla, peli oikealla). Tämä luku riittää aloitukseen; yksityiskohdat ovat
ylempänä luvuissa "ITSENÄISYYDENKATU, keskustan erä" (taulukko), "MODAL-POLTOISTA PUUTTUIVAT…", "Antinkadun loput talot" ja "ILLAN MODAL-JONO".

### Tilanne
- **Antinkatu VALMIS.** Itsenäisyydenkadun keskustan 15 talosta valmiina 415, 118, 116, 119, 121, 107, 7, 166, 167, 164 ja 585:n pohjoispääty. **Tekemättä: 600 (Bepop), 601, 1228 ja 585:n muut sivut.**
  **Omistaja 19.11: kun Itsenäisyydenkatu on tehty, jatketaan RAUTATIENPUISTOKADULLE.** 113 auki (vaatii jalanjälkiratkaisun kuten 136), 115 vain väri korjattu, 569 jätetty (aidan takana).
  Päivitä taulukon Tila-sarake jokaisen talon jälkeen – valmiita ei tehdä uudelleen.
- Kaikki koodi on käyttäjän kansiossa (takaisinluvulla tarkistettu). Modal toimii (PR #62). **Omistaja polttaa illalla:** lisää jokainen uusi lohko
  lukuun "ILLAN MODAL-JONO" (nyt `city 64 c046,c047,c048,c051,c061,c063,c064`).
- **Auki omistajalta:** "katot irti seinistä keskustassa" – ei toistunut pilvessä, odottaa kuvakaappausta ja paikkaa. Korjauskierroksen lista on luvussa
  "Antinkadun loput talot" (1726:n korkeus ym.).

### Säännöt (omistaja)
- Push ja Modal-ajot tekee omistaja; avaimia/salaisuuksia ei käsitellä. Lataukset ja poistot vain luvalla.
- Street View -kuvia ei viedä peliin eikä GitHubiin: niistä luetaan vain mitat, värit, materiaalit. Vertailukuvat vain kansioon `Claude outputs/` (gitignore).
- Tunnista talo ID:stä ja osoitteesta ennen muutosta. Älä keksi olemattomia: näkemätön osa jätetään paljaaksi tai merkitään "peilattu/symmetria" skriptiin
  ja taulukkoon. Logoja, nimikilpiä ja taideteoksia ei kopioida (kyltit tyhjinä väripintoina). Lukittuja (KARHU-värit, 603/602/604) ei muuteta.
- **Toinen chat muokkaa samaa kansiota (radio, jalankulku, sisätilat):** stage `index.html`, `SIIRTO_TOISELLE_TILILLE.md`, `zones.py`, `facades.json`,
  `styles.json` AINA juuri ennen vientiä, tee muutos laitteen versioon ja käytä `expectedMtimeMs`. Tämä tiedosto on kerran ylikirjoitettu vanhalla pohjalla.

### Ympäristö (pilvi alkaa tyhjänä, ~5 min)
```
git clone https://github.com/villeaklinikkasomero/porin-kopterilento.git /home/claude/pori      # + stage koneelta GitHubia uudemmat tiedostot
pip install bpy shapely opencv-python-headless scipy pillow --break-system-packages
mkdir -p /home/claude/mmlproc /home/claude/out && cd /home/claude/mmlproc && tar xzf /home/claude/pori/pipeline/data/porikit_data.tgz && mv data/mmlproc/* .
cd /home/claude/pori && nohup python3 -m http.server 8765 &        # kuolee vuorojen välissä: käynnistä uudelleen ennen gshotia
sed -i "s#/home/claude/.npm-global/lib/node_modules/#/opt/npm-tools/node_modules/#" tools/rautalanka/gshot_sv.mjs     # ÄLÄ vie tätä muutosta kansioon
```
Poltto (YKSI kerrallaan, 8 Gt muisti – kaksi yhtä aikaa kaatuu): c-lohko `cd blender; PYTHONPATH=/home/claude python3 city.py c048 8` (~140 s),
nimetty lohko `python3 run.py tori0 8`. Tulos `/home/claude/out/bl_<lohko>.js` → kopioi `/home/claude/pori/` testiä varten (EI kansioon; Modal tekee 64 näytettä).
Pelikuva: `ZONE=- node tools/rautalanka/gshot_sv.mjs index.html out/ views.json` (`[{"k":"a","x":..,"y":..,"h":..,"p":..,"fov":90}]`).

### Yhden talon työtapa (15–20 min)
1. **Seinälinja:** kadunpuoleinen seinä `lod2.js`:stä (apuri: lue W-kolmiot, tulosta janat joissa z alkaa 0:sta), päätepisteet tarkennetaan `raw.pkl`:stä
   (3 desimaalia). `a`→`b` niin että katu on oikealla. lod2.js pyöristää 0,1 m: 4 cm kuoren takana oleva linja piilottaa itemit.
2. **Street View** sovelluksen selaimella: `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=LAT,LON&heading=H&pitch=P&fov=90`, missä
   lat = 61.486 + y/111437, lon = 21.796 + x/53278 (pano kadun keskilinjalta seinän kohdalta, heading kohtisuoraan seinään). Yksi erä = navigate + 4×10 s
   odotus (erän raja 50 s), sitten ERILLINEN screenshot; jos sumea, odota 15–25 s ja ota uusi. Lue panon todellinen paikka URL:sta (`@lat,lon`).
   Kuva tallentuu pilveen `/tmp/claude-tool-results/*/…jpg` (743×1026, pysty-FOV 90).
3. **Oikaisu:** `python3 tools/rautalanka/rectify.py kuva.jpg cx cy heading pitch Ax,Ay Bx,By s0 s1 z0 z1 out.png 36`. Tarkista mittakaava: julkisivun
   pituus vs. seinälinja ja räystäs vs. LoD2 `e`; jalkakäytävän z (0–1 m) vähennetään. Jos poikkeaa, skaalaa s ja z ja kirjaa kaava skriptin alkuun.
4. **Skripti** `tools/rautalanka/facades/f<ID>.py` (mallit f7.py, f121.py, f116.py, f409.py, f136.py): itemit `box`, `winp`, `glass`, `door`, `balc`;
   seinälle `bare` + `kind` (plaster / brick / wood). `box` ikkunan alla enintään 2,5 cm paksu (winp-kehys on 3 cm). Punainen/oranssi pinta: `"nobrick": True`.
   Toistuva julkisivu: mittaa yksi moduuli ja toista. Kuori taloa pienempi → `footprint=True` SPEC + index.html `L2OLD`/`HFIX` (136).
5. **Testipoltto 8 näytettä**, pelikuva samasta panosta, vertailukuva rinnakkain. Pohjois- ja länsiseinät jäävät poltossa varjoon (tummuvat) – ei vika.
6. **Vienti:** stage → muutos laitteen versioon → `device_commit_files` (expectedMtimeMs) → stage uudelleen ja `cmp`. `node --check` index.html:n
   module-skriptille jos sitä muutettiin. Päivitä taulukko ja ILLAN MODAL-JONO.

### Modal (omistaja)
Push → odota Actions "porikit image" vihreäksi → Actions "porikit run": `city 64 <lohkot>` / `bake <nimetyt> --samples 64` → "porikit collect" → yhdistä PR.
Tarkistus: lohkon kärkimäärä kasvaa (git show origin/main:bl_cXXX.js, glb:n POSITION-count); Modal-lokissa rivi `facades.json: <polku>`.

### 19.11 klo 19: lisää väkeä kävelykadulle ja torille, lisää autoja Yrjönkadulle (omistaja: Yrjönkatu on Porin vilkkain katu)
- `build_walk.py` → walk.js: uudet listat `b` (vilkkaat solmut = OSM highway=pedestrian: Yrjönkadun kävelykatu, Kauppatori, Itäpuisto ym.) ja `g`
  (Kauppatorin 9 m ruudukko, 39 solmua, 8-naapurit; peli pudottaa rakennuksen sisään osuvat = paviljonki).
- Kävelijät (index.html): enintään 46 hahmoa (kosketus 18); 75 % uusista ryhmistä syntyy vilkkaalle väylälle 18–95 m pelaajasta (kävelykadun särmä
  pituuden mukaan painotettuna, tori enint. 1/6 ryhmistä); solmuvalinnassa vilkas väylä paino 4, toriruudukkoon sisään 0,25; kävelykadulla ryhmällä oma
  sivusiirtymä (±3,5 m) eikä kaikki kulje keskiviivaa; poisto >150 m.
- Autot: 22 "Yrjönkadun vakioautoa" (`c.yr`) aloittaa Yrjönkadulta ja palaa sinne näkymättömissä (>170 m pelaajasta), jos on eksynyt muualle;
  lisäksi risteyksessä Yrjönkadun haaran paino 30. Simulaatio 5 min: Yrjönkadulla 16–21 autoa (ennen 0–2).
- Lopullinen kävelijälogiikka: solmuvalinnassa vilkas väylä paino 12, paluu samaa kävelykatua 2 (muuten 0,02), toriruudukkoon sisään 0,25; ja kun hahmoja on
  täysi määrä, kauimmainen ryhmä (>85 m pelaajasta) poistetaan 0,25 s välein → väki kerääntyy sinne missä pelaaja on. Simulaatio 5 min pelaaja
  kävelykadulla: 33/48 hahmoa kävelykadulla (ennen 0–3). Torilla seistessä sama logiikka tuo väen torille ja sen laidoille.

## 19.11.2026 (klo 17 -luvun jatko) – Itsenäisyydenkatu jatkuu: 166 (testipoltettu, Modal-polttamatta)
- **166 Itsenäisyydenkatu 47 (c048):** `f166.py`, eteläjulkisivu 22,7 m, seinä (−244.925,−392.848)→(−222.745,−397.730): vaalea okrarappaus, 3 krs, neljä
  akselia valkoisia kuusiruutuisia ikkunoita (s 2,94 / 7,77 / 14,89 / 19,88), keskellä ovi punagraniittikehyksessä (lippa + 2 porrasta), punagraniittisokkeli
  ja kellari-ikkunat, räystäslista. Pano Itsenäisyydenkatu 47 (61.4823566, 21.7916471 → x −231.92, y −406.1; h 12 ja 330, p 14). Koko julkisivu nähty
  (länsiakselin kellari-ikkuna liikennemerkin takana → jätetty pois). Vertailukuva `Claude outputs/itsenaisyydenkatu_166_vertailu_19_11.jpg`.
- **Mittakaavaoppi:** LoD2-kuori seuraa räystästä (kuori 22,7 m, seinän nurkat s 0,25 ja 21,9), joten pelkkä kuoren pituus ei kelpaa mittakaavaksi. Tässä
  kuoren nurkat + räystäskorkeus antoivat kertoimen 1,124 kameran suhteen → oikaisu tehtiin siirtämällä kamera paikkaan (−232.59, −407.23) ja `ch 2.16`
  (rectify.py:n 15. argumentti), minkä jälkeen s ja z luetaan suoraan.
- **Jalkakäytävä peittää julkisivun alaosan (koskee kaikkia mitattuja julkisivuja):** kadut geometriana (18.11) nostivat jalkakäytävän 0,26 m maaston
  yläpuolelle (`ROAD.pave` index.html:ssä), mutta lohko nostetaan talon maanpintaan → z 0…0,26 jää jalkakäytävän alle (sokkeli, portaat, kellari-ikkunat).
  f166.py:ssä kaikki paitsi räystäs on nostettu `PV = 0.26`. Aiempia taloja EI ole muutettu. **Omistajan päätös 19.11: "jätetään vanhat ennalleen"** –
  vanhoja julkisivuja ei nosteta eikä zones.py:hyn tehdä yleistä nostoa; UUSISSA taloissa z mitataan jalkakäytävästä ja itemit nostetaan `PV = 0.26` (malli f166.py).
- **Uusi: `"nobrick": true` toimii nyt myös taloille ilman SPECiä** (c-lohkojen automaattitalot): `zones.py` kerää ne joukkoon `NOBRICK`, `zones2.spec_for`
  asettaa `sp['nobrick']` → shells `nb` → peli ei piirrä tiilisaumaa punaiseen pintaan (166:n graniitti näkyi tiilenä). Muutos 3 riviä, c048 testipoltettu
  (23 329 kärkeä).
- **Modal:** ks. ILLAN MODAL-JONO (c048 sisältää nyt myös 166:n ja 167:n; c051 lisätty 164:n takia). zones.py ja zones2.py muuttuivat → push ja "porikit image" vihreäksi ennen ajoa.
- **167 Itsenäisyydenkatu 58 (c048, Otavankadun kulma – SPEC-kommentin "Antinkatu corner" on väärin):** `f167.py`, eteläpääty 14,3 m, seinä
  (−274.232,−385.193)→(−260.311,−388.447): harmaanbeige roiskerappaus, 2 akselia leveitä tummapuitteisia ikkunoita 7 kerroksessa (kerrosväli 2,78 m),
  lasitettu kulmaparvekepino kummassakin päässä, lasitettu liikekerros betonipilarien välissä + harmaa lippanauha, punaruskea lautavyö leveän tumman
  räystään alla. Pano Itsenäisyydenkatu 58 (61.4824474, 21.7909043 → x −271.53, y −395.87; h 13 p 30), mittakaava 1,0, z = z − 0,17, + PV.
  Yksinkertaistettu: länsiparvekkeiden alla oleva avoin pylväikkö on piirretty umpiseinänä; parvekepinot 0,3 m ulkonevina. `nobrick` (lautavyö).
  Vertailukuva `Claude outputs/itsenaisyydenkatu_167_vertailu_19_11.jpg`. c048 testipoltettu (24 405 kärkeä).
- **167 täydennetty (omistaja: "miksi ei voi leikata?"):** katutaso on nyt sisäänvedetty facades.jsonin valmiilla seinäavaimella
  `"recess": [gh, sb, h]` (zones.py `_bare_w`: liikekerros gh korkea, sb metriä seinälinjan takana, generoitu näyteikkunalasitus + alapinta + päätypilarit):
  eteläpääty sb 1,0, länsisivu sb 1,5 → lounaiskulma on avoin lovi kulmapilarin takana (oikeasti n. 2,2 m syvä pylväikkö pyöreällä pylväällä).
  Pilarit ovat `box`eja d −sb…0; osa seinästä ilman sisäänvetoa täytetään `box`illa d −sb…0 koko katutason korkeudelta (länsisivu s 0–12,5).
  **Länsisivu = Eteläpuisto 20 (ei Otavankatu), 35,0 m**, seinä (−266.251,−351.094)→(−274.232,−385.193): 8 ikkuna-akselia harmain alapaneelein,
  ulkoneva lasitettu parvekepino s 15,5–18,9 (1,5 m), kulmapino s 31,15–34,37, lippanauha ja pilarit s 12,5→, pohjoisosassa 2 katutason ikkunaa ja
  graniittisokkeli. Panot: kaukaa Eteläpuisto 19 (61.4827021, 21.7903007 → x −303.63, y −367.47; h 103 p 22; s suoraan, z oli 1,068-kertainen) ja
  läheltä Eteläpuisto 20 (61.4827418, 21.7908179 → x −276.07, y −363.05; h 103 p 30). s < 4,5 puiden takana → jätetty paljaaksi.
  Länsiseinä leipoutuu varjoon ja näkyy 8 näytteen testissä tummana ja läikikkäänä (seinän väri vaalennettu `#cdc7bb`) – tarkista 64 näytteen Modal-poltosta.
  c048 testipoltettu (27 017 kärkeä). Vertailukuva päivitetty (3 paria + kulmanäkymä).
- **164 Itsenäisyydenkatu 45, pysäköintitalo (c051):** `f164.py`, eteläjulkisivu 26,4 m, seinä (−216.063,−398.788)→(−190.378,−404.806): vaaleanharmaat
  betonielementit, matala muuri 4,3 m kahden porrastornin välissä (länsi 7,2 m + tumma lasinauha, itä 6,0 m + lasiovi ja ikkunanauha), harmaansininen ovi,
  nosto-ovi kahdella lasirivillä, 4,9 m ajoaukko (tumma levy – aukkoa ei leikattu) keltaisten tyhjien kylttien alla. Pano Itsenäisyydenkatu 45
  (61.4822881, 21.792202 → x −202.35, y −413.44; h 345 ja 45, p 8); mittakaava 1,1 → kamera (−202.60, −414.52), ch 2.03. LoD2-kuori seuraa torneja oikein.
  Pois jätetty: valaisimet, vino betonilapa, kannen ilmanvaihtorumpu. Vertailukuva `Claude outputs/itsenaisyydenkatu_164_vertailu_19_11.jpg`.
  c051 testipoltettu (18 321 kärkeä). **Modal-jono nyt `city 64 c046,c047,c048,c051,c061,c063,c064`.**
- Jäljellä taulukosta: 600 (maamerkkilohko bepop), 601 ja 1228 (ei lohkoa – selvitä ensin missä ne poltetaan), 585 (c064) (+113 auki, 115 mittaamatta).

### 19.11 klo 20: patsaat ja muistomerkit kartalle (omistajan zip porikopteri_kaikki.zip)
- Lähde: `tools/props/porikopteri_patsaat.json` (21 kohdetta, Wikipedia CC BY-SA 4.0), `porikopteri_patsaat.py` (mallit) ja `porikopteri_siirto_patsaat.md` (mallichatin ohje).
- **Sijainnit:** 10 kohteelle tarkka paikka OpenStreetMapista (tourism=artwork / historic=memorial, haettu api/0.6/map.json-ruuduilla): 001 karhu, 004 Portti,
  006 Eetu Salin, 007 Gallen-Kallela, 008 Taiteen tammi, 010 Sukkula, 012 Ankkuri, 013 suihkulähde, 014 Bass String Wings (= OSM "Jyrki Kankaan muistomerkki"),
  020 Aurinkolähde (siirtyi ~300 m). JSONiin kenttä `sijainti_lahde`. Loput 11 ovat luettelon 4 desimaalin koordinaateilla (virhe 5–10 m). 011:lle OSM:ssä
  on "Hautamuistomerkit 1939-40 & 1941-44" 100 m etelämpänä (61.487985, 21.799381) – ei käytetty, koska en varmistanut että se on sama teos.
- **Peli:** `patsaat.js` = {k: kohteet pelikoordinaatteina, m: 11 GLB:tä base64}. index.html-lohko "statues and memorials" ennen `window.__game`-riviä:
  rakennukseen/ajoradalle osuva piste siirretään lähimpään vapaaseen kohtaan (spiraali ≤30 m; 003 siirtyi 4 m, 015 8 m), suunta = lähin katu jos
  `suunta_asteet` puuttuu, korkeus carGround/TZs + `noT`-liput (muuten maaston nosto tulee kahdesti → patsas leijuu). 20/21 kartalla; 021 Vampire
  (lentoasema) on pelialueen ulkopuolella. Lähellä (kävellen 14 m, autolla 20 m, kopterilla 32 m) toast "🗿 nimi – tekijä, vuosi". `window.__statues`.
- Tekemättä ohjeen listalta: minikartan merkit, valokeila/merkki ilmasta, keräily, tekijätiedot (Wikipedia/OSM) pelin tietoihin, omistajan tarkistuslento ja suunnat.
- 19.11 klo 20.30: patsaiden asettelu tarkistettu pelikuvista (kaikki 20). Korjattu: sijoitussääntöön 3 m väli rakennuksiin ja joenpohjan esto
  (016 irtosi museon seinästä 2 m), 012 Ankkuri käsin `siirto_m: [-14, 1]` (pelin jokiraja on idempänä kuin OSM:n piste, ankkuri oli vedessä).
  Tarkistuskuvat lähetetty chatissa. Auki omistajalle: 003 Juhana-herttua seisoo jalkakäytävän kulmassa (luettelon koordinaatti, ei varmistettu),
  004 Portin suunta (aukko kohti katua, puistokäytävä ei kulje sen läpi), 005 Toriparlamentti keskellä toria, 019 vieressä ilmakuvatalon vino seinä.
- 19.11 klo 20.45 (omistaja): 001 Satakunnan karhu katsoo itään (`suunta_asteet: 90`; patsaat.js-kenttä h). Muut suunnat edelleen arvauksia (lähin katu).

## PYSÄKÖINTIHALLI 164 – LÄPIAJOTESTI (omistaja 19.11: "tehdään testi, ulos taitaa päästä Mikonkadun päästä")
- **Mitä:** autolla voi ajaa Itsenäisyydenkadun ajoaukosta halliin ja ulos Mikonkadun päästä (Street View: Mikonkadun aukossa kielletty ajosuunta -merkki,
  eli oikeasti sisään etelästä, ulos pohjoisesta; pelissä kumpaankin suuntaan). Testipoltettu ja ajolinja tarkistettu pilvessä; **omistaja ei ole vielä ajanut**.
- **Poltto (uusi seinäavain facades.jsonissa): `"gate": [s0, s1, gh, depth, h]`** = oikea aukko seinässä (pielet + alapinta, ei takaseinää).
  `kivi.py` jakaa kuoren seinän aukon pielistä (`cut_walls`), `zones.py` `_gate_w` antaa aukkopätkälle sisäänvedetyn rivin, `gen.py`: rivi jolla
  `noback` jätetään piirtämättä. 164: etelä s 16,05–20,95 (h 2,3) ja Mikonkatu s 14,2–19,0 (h 2,5; **mittakaava kalibroimatta**, pano Mikonkatu 10:
  61.4834211, 21.7927058 → x −175.51, y −287.40, h 193 p 8). Mikonkadun seinä (−161.577,−304.078)→(−186.75,−298.116) on nyt paljas betoni + lasiovi + nosto-ovi.
- **Peli (index.html, haku `HALL`):** hallin sisus piirretään three.js:llä ilman leivontaa (lattia, katto, seinät, 12 pilaria keskilinjalla, ruutuviivat) –
  **vain aukot on mitattu, hallin koko = kuoren jalanjälki 0,4 m sisäänvedettynä, pilarit ja ruudut arvioita.** `inHall()` vapauttaa auton talotörmäyksestä
  hallin sisällä ja aukkokaistoilla (pilarit pysäyttävät; seinät otetaan 0,3 m välein auton kyljistä), `carGround` palauttaa hallin lattian
  (`hallZ`: tasainen luiska etelän jalkakäytävän tasosta pohjoisen tasoon, 3,97 → 3,77), seurantakamera laskeutuu katon alle (4,6 m taakse, 1,9 m ylös).
  Testikoukku `window.__hallTest`. Hallin geometria on laskettu pilvessä jalanjäljestä (shapely) ja upotettu `HALL`-vakioon.
- **Tiedossa / auki:** länsiseinän juuressa maasto pilkistää lattian läpi vihreänä kaistana; sisus on tasaväristä (ei valoja, ei varjoja, ei pysäköityjä
  autoja); kopteri/kävelijä/liikenneautot eivät tunne hallia; katolta katsoen ei muutosta. Jos testi kelpaa: sisus Blender-moduuliksi (kuten sisätilat),
  oikeat mitat omistajan kuvista, ja sama `gate` + `HALL`-rakenne muihin halleihin.
- **Viety kansioon:** `index.html`, `blender/gen.py`, `blender/kivi.py`, `blender/zones.py`, `blender/facades.json`, `tools/rautalanka/facades/f164.py`,
  kuva `Claude outputs/pysakointihalli_164_testi_19_11.jpg`. Modal-jono ennallaan `city 64 c046,c047,c048,c051,c061,c063,c064` (c051 = 164 aukkoineen); gen.py/kivi.py/zones.py
  muuttuivat → push ja "porikit image" vihreäksi ennen ajoa. **Ennen Modal-polttoa aukot eivät näy pelissä** (vanha bl_c051.js: umpiseinä), mutta läpi voi jo ajaa.

### 19.11 klo 21: kävelijät upposivat kivetykseen + porilaiset huudahdukset (H)
- **Uppoaminen:** kävelykadun ja torin kivetys (R.kivi) piirretään jalkakäytävän korkeudelle (ROAD.pave 0,26), mutta korkeusmaskissa oli vain R.pave →
  `carGround` antoi asfaltin tason (0,13) ja kävelijät, pelaaja ja autot upposivat 13 cm. Korjaus: R.kivi mukaan maskin bittiin 1 (index.html, roads-rasteri).
- **Huudahdukset:** kävellessä **H** (kosketus 💬) → lähin kävelijä (<8 m) pysähtyy 3 s, kääntyy pelaajaan ja sanoo repliikin (ääni + toast). `window.__npc.greet`.
  Tekstit `tools/radio/huudot.json` (12 aikuisten, 4 lasten), generaattori `tools/radio/huudot.py` → `radio/huuto_{m,n,l}_NN.mp3` + `radio/huudot.json`.
  Piperissä on suomeksi vain miesääni: naisääni = sama 1,22× sävelkorkeus, lapsi 1,45× (asetrate+atempo). Ei kuunneltu pilvessä; murreasu on Clauden arvio.
- **Auki:** omistajan kuvakaappaus (Liisankatu-kyltti, harmaa talo jonka kulmassa näkyy läpi puistoon) – kohtaa ei löytynyt Liisankadun ja Eteläpuiston
  kulmasta (talot 65, 70, 253, 158); tarvitaan tarkempi paikka. Ei liity tämän päivän muutoksiin (bl_*.js-polttoja ei ole viety).

## 19.11.2026 – 585 vanha linja-autoasema, pohjoispääty (testipoltettu) + SEURAAVA KATU
- **585 (c064):** `f585.py`, Itsenäisyydenkadun puoleinen pääty 13,0 m, seinä (124.425,−502.046)→(111.751,−499.126): okranbeige rappaus pulpettikaton alla
  (räystäs laskee n. 0,9 m itään – kuoren oma yläreuna), 3 isoa valkopuitteista ikkunaa katutasossa, yläkerrassa pitkä ikkuna valkoisten pystysäleiden
  takana, tumma liuskekivisokkeli. Pano Itsenäisyydenkatu 44 (61.4815792, 21.7982185 → x 118.21, y −492.56; h 193 p 12; itänurkka h 140).
  Mittakaava 1,0 räystäästä, s = s − 0,7, z = z − 0,1, + PV. Vertailukuva `Claude outputs/itsenaisyydenkatu_585_vertailu_19_11.jpg`. c064 testipoltettu (16 962 kärkeä).
  **Muut sivut mittaamatta** (SPEC-asettelu: näyteikkunat + ikkunanauha): länsi (111.798,−499.282)→(107.797,−516.889) 18,1 m, koillinen
  (148.262,−528.19)→(122.247,−511.786) 30,8 m ym. – seinälista raw.pkl:stä.
- **Jäljellä Itsenäisyydenkadun keskustan erästä:** 600 (Bepop, maamerkkilohko `bepop`), 601 ja 1228 (ei lohkoa – selvitä ensin missä ne poltetaan),
  585:n muut sivut, 113 (auki), 115 (mittaamatta).
- **OMISTAJAN OHJE 19.11: Itsenäisyydenkadun jälkeen jatketaan Rautatienpuistokadulle.** (Talolistaa ei ole vielä tehty: poimi kadun varren talot
  city.js/lod2.js:stä kuten Itsenäisyydenkadulla ja tee taulukko ID / osoite / lohko / tila ennen ensimmäistä taloa.)

### 19.11 klo 22: kivetyksen korkeus kolmioista, värivaihtelu, automaattinen tervehdys, lisää huudahduksia
- **Uppoaminen kävelykadulla jatkui pelaajalla** (omistajan kuva). Maskikorjaus (R.kivi → paveAt) ei riittänyt: kivetys on muutamia kymmenien metrien
  kolmioita, jotka nostetaan maastoon vain kulmistaan, joten pinta EI ole groundTop(x,y)+pave kolmion keskellä. Uusi `ROAD.kiviZ(x, y)` = kolmion
  kulmakorkeuksien (groundTop kulmissa) tasointerpolaatio + ROAD.pave; `carGround` käyttää sitä kivetyksellä (kävelijät, pelaaja, auto).
  Oletus: varjostin nostaa kivetyksen vain kärjistä. Pelaajan uppoamista ei saatu toistettua pilvessä (begin() ei käynnisty headless) – omistaja tarkistaa.
- **Länkisäärikävely:** pelaajan ja NPC:iden Walk-klippi on sama (hahmo.js = zipin hahmo.glb); jalkaterät kulkevat ±10–15 cm keskilinjasta. Vika on
  mallichatin animaatiossa, ei pelin koodissa – ei korjattu.
- **Värit:** `tintChar` kloonaa hahmolle TShirt/Jeans/Shoe/Hair(+HairShell, Brow) -materiaalit ja kertoo värin satunnaisella sävyllä (`TINT`-taulukko);
  mies_b:n hiuksia ei sävytetä; kloonit vapautetaan poistossa. Tekstuuri säilyy, joten sävytys on kertova (tumma tekstuuri ei vaalene).
- **Tervehdys itsestään:** kun pelaaja kävelee <2,6 m päähän, kävelijä puhuu (ryhmä kerran / 45 s, enintään yksi repliikki / 6 s). H ja 💬 toimivat edelleen 8 m asti.
- **Huudahdukset:** huudot.json sai listan `n` (vain naiset, tiedostot huuto_n_13–18: Hyvä Ässät!, Mennääks jazzeil?, Lähdetääks Yyterii?, Torilt saa hyvää
  kahvii., Kyl Pori on kaunis kesäl., Onks toi sun kopteris?) ja lapsille 5 lisää (huuto_l_05–09). Yhteensä 39 äänitiedostoa.

## 19.11.2026 – 600 Hotelli Bepop ja 601 Maakuntalinna (testipoltettu, nimetty lohko `bepop`)
- **Rakenne (tärkeä):** 600 ja 601 ovat lod2.js:n `hide`-listalla eikä niillä ole omaa kuorta: ne ovat **BePOPin LoD2-kuoren (588) eteläseinän pätkiä**
  (seinä (3.51,−450.606)→(83.248,−469.351), 81,9 m; hotelli s 0–47,2, Maakuntalinna s 47,2–81,9; zones.py `_SPEC_HB` / `_SPEC_ML` runaltina).
  facades.json-merkintä on siksi **id 588**, kaksi seinää samalla janalla ja `bare_s`; skripti `tools/rautalanka/facades/f588.py` kirjoittaa molemmat
  (älä tee erillistä id 600/601 -merkintää – se ei vaikuta). Poltto: `cd blender; python3 run.py bepop 8`.
- **600 (omistaja: "ihmeellistä hyppyä tasaisissa nauhoissa"):** generoidut nauhaikkunarivit porrastuivat seinäpätkittäin. Nyt 5 tasaista ikkunanauhaa
  koko pätkällä (väli 2,77 m, korkeus 1,4 m, puitejako 1,5 m, kaksi alinta sinisin verhoin), klinkkeri välissä, tumma punaruskea otsanauha liikekerroksen
  päällä, näyteikkunat, porttikäytävä s 17,1–19,6 (tumma levy). Pano Itsenäisyydenkatu 37 (61.4818218, 21.7963801 → x 20.25, y −465.75; h 13 p 18),
  mittakaava 1,0. Nähty s 9,5–28; loput toistettu. Kuori (25,7 m) on katujulkisivua (20,2 m) korkeampi → yläosa paljasta klinkkeriä.
- **601:** valkoinen pelti, 5 ikkunanauhaa (väli 3,15 m, korkeus 1,73 m; moduuli 4,54 m = harmaa sälekenttä 1,14 m + 3 ikkunaa), korkea liikekerros:
  näyteikkunat, sisäänkäynti, 2 pilaria, tyhjä sininen kylttilevy. Pano Itsenäisyydenkatu 35 (61.4816727, 21.7972856 → x 68.50, y −482.2; h 13 p 18),
  mittakaava 1,107 (s = 23,2 + (s − 23,2)·1,107, z = z·1,107). Nähty s 7,5–34,6; länsipää toistettu. Seinä `plaster` (metallinen `sheet` leipoutui harmaaksi).
- Vertailukuva `Claude outputs/itsenaisyydenkatu_600_601_vertailu_19_11.jpg`. bepop testipoltettu (14 839 kärkeä). **Modal: `bake bepop --samples 64`.**
- **Jäljellä:** 1228 (lod2 `hide`, ei missään lohkossa, ei SPECiä – peli piirtää sen yleisellä city.js-talolla; mitattu julkisivu vaatii ensin lohkon tai
  selvityksen minkä kuoren pätkä se on), 585:n muut sivut, 113 (auki), 115. Sen jälkeen Rautatienpuistokatu.

## 19.11.2026 – 1228 valkoinen kulmatorni (testipoltettu, c064)
- **Rakenne:** 1228 on lod2.js:n `hide`-listalla; se on **Lääkäritalon kuoren 1229 (c064) eteläseinän länsipää** (seinä (120.8,−474.625)→(179.257,−488.221),
  60 m; torni s 0–12). facades.json-merkintä on siksi **id 1229** + `bare_s [0, 12.07]`; skripti `f1228.py` (1229:n loppuosa mitataan samaan merkintään).
- **Julkisivu:** valkoinen laatta, 4 yläkerrosta (väli 3,65 m): ikkunapari + pieni ikkuna sinisen pystyraidan kummallakin puolella, 1. kerroksen ikkunanauha
  sinisin pystytolpin, näyteikkunat, vihreä ja sininen kyltti tyhjinä levyinä. Pano Itsenäisyydenkatu 44 (61.4815792, 21.7982185 → x 118.21, y −492.56;
  h 20 p 24), mittakaava 1,08 kuoren huipusta (s = 1,54 + (s − 1,54)·1,08, z = 1,08·z − 0,41). Tornin länsireuna on 1,8 m kuoren seinän alun länsipuolella
  (kuoressa lovi) → läntisin ikkunapari katkeaa kohtaan s 0. Tornin länsisivu ja 1229:n loppu mittaamatta.
- Vertailukuva `Claude outputs/itsenaisyydenkatu_1228_vertailu_19_11.jpg`. c064 testipoltettu (17 342 kärkeä). Modal-jono ennallaan (c064 mukana).
- **Itsenäisyydenkadun keskustan erästä jäljellä:** 585:n muut sivut, 113 (jalanjälkiratkaisu), 115 (julkisivu mittaamatta). Sitten Rautatienpuistokatu.

## 19.11.2026 – 585 vanha linja-autoasema, länsisivu Kuninkaantielle (testipoltettu, c064)
- **Seinä** (111.798,−499.282)→(107.797,−516.889), 18,06 m (katu oikealla = länsi). `f585.py` kirjoittaa nyt KAKSI seinää (pohjoispääty ennallaan).
- **Julkisivu:** okranbeige rappaus, punatiilisokkeli sillien alle (z 0–1,75), 10 akselia valkopuitteisia ikkunoita (jako 1,58 m, leveys 1,1 m;
  alhaalla z 1,8–3,55, ylhäällä 5,4–7,3), 3. akselissa etelästä lasiovi terassille, tiilinen sillinauha z 5,05–5,38, musta markiisi s 8,8–18
  (teksti jätetty pois), tumma räystäslista, puinen terassikansi seinän edessä (s 2,5–18, 3 m ulos, 0,85 m korkea).
- **Pano** Kuninkaantie, syys 2017 (61.4814435, 21.7978931 → x 100.86, y −507.76; h 55 / 103 / 150, p 12). **Kalibrointi:** GPS-paikalla räystäs tuli
  8,5 m:iin; räystäs on 10,0 m (keilaus, ja pohjoispääty kohtaa sen nurkassa), joten kamera siirretty paikkaan x 98.59, y −506.84 (11,2 m seinästä,
  etelänurkan suunta 137,5°). EPÄVARMA: vaakasuunnassa GPS-paikka sopi paremmin (tornin 1228 suunnat), eli mitat voivat olla jopa 20 % liian
  suuria – tarkista jos saadaan lehdetön pano. Nähty selvästi s 8–18, puun läpi s 2–8; pohjoisimmat 3 yläikkunaa toistettu.
- Vertailukuva `Claude outputs/itsenaisyydenkatu_585_lansi_vertailu_19_11.jpg`. c064 testipoltettu (17 558 kärkeä). Modal-jono ennallaan (c064 mukana).
- **585:n mittaamattomat sivut** (raw.pkl): pohjoispäädyn itäsivu (124.425,−502.046)→(122.247,−511.786) 10,0 m; koillinen (122.247,−511.786)→(148.262,−528.19)
  30,8 m; itäpää (148.262,−528.19)→(144.32,−533.694) 6,8 m; etelään (144.32,−533.694)→(121.953,−528.546) 23,0 m; korkea osa länteen
  (105.464,−516.321)→(100.951,−535.198) 19,4 m (z 11,4); eteläsiipi y −535…−569 (8 seinää). Kuori kattaa koko korttelin (y −499…−569).

## 19.11.2026 – RAUTATIENPUISTOKATU – talotaulukko (omistaja: "mennään rautatienpuistikkoa kohden, keskusta-alue ensiksi")
Katu city.js:ssä (−24,−533) → (−289,−829), n. 400 m lounaaseen. Rakennukset alle 28 m katulinjasta (city.js-jalanjäljet), järjestys pohjoisesta etelään.
Länsi-/luoteispuoli = parittomat, itä-/kaakkoispuoli = parilliset. **Tee vain rivit, joissa lukee TEKEMÄTTÄ.**

| ID | Mikä | Puoli | Lohko | Kuori | Kadunpuoleinen seinä (raw.pkl) | Tila |
|---|---|---|---|---|---|---|
| 109 | Rautatienpuistokatu 3 / Yrjönkatu 27, valkoinen funkis + kulmatorni | luode | c064 | **kuoren 111 pätkä** (lod2 hide), s 31,1–43,2 | sama seinä kuin 111 | VALMIS 19.11 (f111.py; Yrjönkadun sivu 17,5 m mittaamatta) |
| 111 | kermanvärinen 2 krs klassistinen talo (Rautatienpuistokatu 3:n eteläpuoli) | luode | c064 | oma | (−60.156,−555.791)→(−30.901,−523.977) 43,2 m | VALMIS 19.11 (f111.py; lounaispääty 12 m mittaamatta) |
| 2 | **Keskuskartano** (Keskusaukio 2, 1962; SPEC KKART zones.py) + Hotel Amado -siipi; kadulle näkyy lamellin peltipääty ja matalat liikesiivet | kaakko | c064 | oma | matalat siivet (−37.2,−574.9)→(−20.3,−551.6) murtoviivana; torni (−40.4,−589.3)→(−37.2,−574.9) 14,7 m | POHJOISSIVU KORJATTU 19.11 (kivi.py `_kk_north`, ks. alla); mitattu julkisivu TEKEMÄTTÄ |
| 122 | pieni piharakennus 51 m² | kaakko | c064 | ei kuorta | – | JÄTETÄÄN |
| 124 | Rautatienpuistokatu 5, ent. Teljän ammattikoulu (1938), valkoinen 3 krs | luode | c063 | oma | (−114.398,−609.46)→(−80.242,−572.33) 50,5 m ja (−135.486,−639.38)→(−110.914,−612.67) 36,3 m | VALMIS 19.11 (f124.py: molemmat siivet; sisänurkan portiikki mittaamatta) |
| 13 | 4 krs lamelli | kaakko | c061 | oma | (−114.441,−655.249)→(−61.531,−596.099) 79,4 m | VALMIS 19.11 (f13.py; ikkunamoduuli luettu s 11–59, päät toistettu) |
| 23 | Rautatienpuistokatu 6 (1954) | kaakko | c061 | oma | (−164.549,−710.867)→(−138.006,−680.88) 40,0 m + (−136.824,−681.927)→(−128.432,−672.444) 12,7 m | TEKEMÄTTÄ – EI sama asettelu kuin 8/12 (pidempi, rapattu päätykaista); tarvitsee terävän kuvan, pano 61.4798294, 21.7929287 |
| 15 | iso koulurakennus (Rautatienpuistokatu 7, ent. poikien ammattikoulu?) | luode | c047 | oma | ei seinää alle 22 m kadusta (puiston takana) | TARKISTA näkyykö kadulle |
| 36 | Rautatienpuistokatu 8 (1954) | kaakko | c047 | oma | (−193.953,−743.875)→(−172.824,−720.017) 31,9 m | VALMIS 19.11 (f36.py) |
| 19 | Rautatienpuistokatu 10 (1954) | kaakko | c047 | oma | (−224.007,−778.342)→(−202.228,−753.749) 32,9 m | TEKEMÄTTÄ – EI sama asettelu kuin 8/12 (rapatut parvekekaistat molemmissa päissä); tarvitsee terävän kuvan, pano 61.479217, 21.791768 |
| 34 | Rautatienpuistokatu 12 (1954) | kaakko | c046 | oma | (−254.125,−810.805)→(−232.851,−786.778) 32,1 m | VALMIS 19.11 (f36.py; asettelu TOISTETTU nro 8:sta, oma kuva sumea) |
| 21 | Satakunnankatu 23, 6 krs beige lamelli (pääty kadulle) | kaakko | c046 | oma | (−286.337,−847.299)→(−262.543,−820.12) 36,1 m | TEKEMÄTTÄ |

Seinät on annettu raw.pkl:n päätepisteinä; **käännä suunta niin että katu on oikealla** (luoteispuolen taloilla a = lounaispää, kaakkoispuolella a = koillispää).
6, 8, 10 ja 12 ovat saman sarjan taloja (1954): mittaa yksi huolella ja tarkista muista erot.

### 36 ja 34: Rautatienpuistokatu 8 ja 12 (testipoltettu, c047 ja c046)
- `f36.py` kirjoittaa molemmat (funktio `house`): vaaleanruskea tiili (`kind: brick`), 3 kerrosta, 10 ikkunasaraketta, 2 porrasta (puiset pariovet
  sivuvaloineen, porrasikkunat puoli kerrosta sivussa), kellari-ikkunat, valkoinen räystäslauta.
- Nro 8 mitattu terävästä leveästä kuvasta: pano "8 Rautatienpuistokatu" 61.4794926, 21.7922824 (h 132, p 18). s = (s + 1,2)·0,973,
  z = (z − 1,0)·1,075 (kuvan oma mittakaava antoi räystään 0,8 m kuorta alemmas → korkeudet ±0,5 m).
- Nro 12: oma kuva jäi sumeaksi mutta näyttää samat sarakkeet, portaat (0,255 ja 0,70 pituudesta) ja ovet → nro 8:n asettelu TOISTETTU, skaalattu 32,1 m:iin.
- **Nro 6 (23) ja nro 10 (19) eivät ole samaa asettelua** (sumeista kuvista: nro 10:ssä vaaleaksi rapatut parvekekaistat molemmissa päissä, nro 6 on
  52,7 m pitkä kahdessa osassa ja siinä on rapattu kaista lounaispäässä) → jätetty tekemättä, tarvitaan terävät kuvat.
- **Street View latautui leveänä tänään ~90 s / pano** ja kolme neljästä jäi sumeaksi: seuraavalla kerralla kokeile pystykuvaa (kaksi kuvaa / talo)
  tai odota kunnes URL:ssa on panoid ennen zoomia.
- Luoteisseinät leipoutuivat 8 näytteellä tummiksi ja laikukkaiksi – katso 64 näytteen poltosta.
- Vertailukuva `Claude outputs/rautatienpuistokatu_8_12_vertailu_19_11.jpg`. c047 (16 324 kärkeä) ja c046 (8 275) testipoltettu. **Modal-jonoon c046, c047.**

### 13 nelikerroksinen lamelli kadun kaakkoispuolella (testipoltettu, c061)
- Seinä a (−61.531,−596.099) → b (−114.441,−655.249), 79,4 m. `f13.py`: 4 ikkunanauhaa tummansinisissä kaistoissa, vaaleanharmaat rihlatut
  välikaistat, tumma sokkeli. Ikkunamoduuli 15,3 m (2 leveää + 3 kapeaa) luettu kohdasta s 11–59 ja TOISTETTU molempiin päihin.
- Pano "4 Rautatienpuistokatu" 61.4805093, 21.794205 (h 132, p 18, leveä kuva, terävä); päiden panot jäivät sumeiksi (käytetty vain päätyjen
  paikkaan: s −0,2 ja 80,0 → vaakamittakaava 1,0). Korkeus z = 1,13·z − 1,36 (räystäs kuoresta 15,05; kuvan oma mittakaava antoi 14,5 → ±0,5 m).
- Kellari-ikkunat jätetty pois; ovia ei näkynyt. Osoitetta ei tunnistettu. **Seinä on luoteeseen ja leipoutui 8 näytteellä hyvin tummaksi**
  (välikaistat tummanharmaat) – katso 64 näytteen poltosta ennen värin säätöä.
- **Leveän kuvan oppi:** Street View latautuu leveänä hitaasti (60–90 s): navigate + 4×10 s, sitten ERI kutsussa 2×10 s + `zoom`; jos URL:ssa ei
  vielä ole panoid:tä (`…,0a,…`), kuva on sumea – odota lisää, älä siirry seuraavaan.
- Vertailukuva `Claude outputs/rautatienpuistokatu_13_vertailu_19_11.jpg`. c061 testipoltettu (7 886 kärkeä). **Modal-jonoon c061.**

### 124 Rautatienpuistokatu 5, molemmat siivet (testipoltettu, c063)
- Katujulkisivu on kaksi siipeä, koillissiipi 4,7 m sisempänä. Lounaissiipi (−135.486,−639.38)→(−110.914,−612.67): valkoinen rappaus,
  15 ikkuna-akselia (jako 2,07 m) kolmessa kerroksessa punaruskein puittein, tiilinen kellarikerros ikkunoineen, sillinauha, räystäslista.
- **Pano** "5 Rautatienpuistokatu" 61.4803068, 21.7938141 (→ x −116.46, y −634.75; h 313, p 18), huhti 2026. Kalibrointi kuoresta:
  s = 0,3 + (s − 2,0)·1,082, z = 1,114·z − 0,75.
- **Uusi kikka: leveä kuva.** `resize_window` 1500×900 ennen navigointia → screenshot 800×480, pystykuvakulma yhä 90°, vaakaan ±60°: koko 36 m siipi
  yhdellä kuvalla 11 m päästä (16 px/m – riittää säännölliseen ruudukkoon, ei pieniin yksityiskohtiin). Ensimmäinen screenshot on sumea: odota
  vielä 10 s ja ota `zoom` koko alueesta. Palauta lopuksi `preset: desktop`.
- **Koillissiipi** (−114.398,−609.46)→(−80.242,−572.33), 50,45 m, sama merkintä (toinen seinä): 11 akselia (jako 2,23 m), sisäänkäynti s 25,0–28,8
  (lippa sivuseinineen, korkea porrasikkuna yllä), 9 akselia (jako 2,16 m). Panot "4 Rautatienpuistokatu" 61.4805093, 21.794205 ja
  "2 Rautatienpuistokatu" 61.480712, 21.794593 (h 313, p 18, leveä kuva); k 1,09 / 1,075 kameroiden suhteen. Kuvat erosivat n. 0,7 m kohdassa s 32
  (keskiarvo); runkojen takana olevat akselit toistettu samalla jaolla. **Mittaamatta: sisänurkan portiikki** (lounaissiiven 4,7 m päätyseinässä).
- Vertailukuvat `Claude outputs/rautatienpuistokatu_124_lounaissiipi_vertailu_19_11.jpg` ja `…_124_koillissiipi_vertailu_19_11.jpg`. c063 testipoltettu
  (4 524 kärkeä). **c063 on Modal-jonossa.**

### Keskuskartano (2): pohjoissivun reiät ja "aaltoilu" korjattu (omistaja 19.11: kuvakaappaus + "julkisivu aaltoilee", "totaalisen rikki")
- **Syy (toistui pilvessä, ei GPU/CRLF):** keilaus piirtää pitkän pohjoissivun irrallisina ulokkeina 1,1–1,6 m taustatason edessä, ja taustatasossa
  ei ole seinää 5,5 m yläpuolella kohdissa s 78,8–86,4 ja s 92–101,3 (reiät lamellin läpi itäpäässä). Ulokkeiden syvyys vaihteli = aaltoilu.
- **Korjaus `blender/kivi.py` `_kk_north()`** (RAW[2] paikataan ennen polttoa): pohjoissivun ulokkeet, niiden katot ja reikäinen taustataso poistetaan;
  tilalle YKSI suora seinä 1,3 m taustatason edessä koko 101,3 m:n matkalle (z 4,2–34,5) ja kattokaista. **Ei torneja.**
- **1. yritys hylätty (omistaja: "sun poltossakin rikki"):** keilauksen 4 porrastornia (2,1 m ulkona, katto 33,7 m) säilytettiin → jokainen
  seinäpätkä sovitti omat ikkunarivinsä (eri korkeus/alareuna) ja nauhat porrastuivat pätkästä toiseen. Opit: (1) saman julkisivun pätkillä pitää
  olla sama alareuna ja räystäs, muuten `_kk_fit` jakaa kerrokset eri tavoin; (2) seinämonikulmio, jonka keskipisteen edessä on korkeampi katto,
  hylätään "sisäseinänä" (zones2 build_lod2:n roofz-testi).
- **EI tarkistettu valokuvasta:** onko pohjoissivu oikeasti täysin sileä (keilauksessa 4 porrastornia s 12,8–17,7 / 49,6–54,7 / 68,4–78,8 / 86,5–92,1).
- c064 testipoltettu (19 371 kärkeä), nauhat tasaiset koko matkalla kuten eteläsivulla. Kuva `Claude outputs/keskuskartano_pohjoissivu_ennen_jalkeen_19_11.jpg`. **kivi.py muuttui → push ja "porikit image"
  vihreäksi ennen Modal-ajoa** (c064 on jonossa).

### 111 + 109 (testipoltettu, c064)
- **Rakenne:** 109 on lod2 `hide` -listalla; se on kuoren 111 Rautatienpuistokadun seinän pohjoispää. Kuoren seinä on YKSI monikulmio (s 0–31,1 räystäs 10,0;
  31,1–40,4 räystäs 10,4; torni 40,4–43,2 huippu 13,4), joten `bare_s` ei erota taloja: merkintä id 111, yksi seinä, pohjaväri kerma, ja 109:n valkoinen
  pinta on 2 cm `box` seinän päällä. Skripti `tools/rautalanka/facades/f111.py` (70 itemiä).
- **111:** kermanvärinen rappaus, harmaa roiskerapattu sokkeli kellari-ikkunoin, valkoinen räystäslista, 2 kaariovea (piirretty suorakulmaisina) joiden yllä
  porrasikkuna ja lunetti, leveät 3-osaiset ikkunat päissä, 4 akselia 2-osaisia ikkunoita ovien välissä, eteläpään nurkkaliseenit.
- **109:** valkoinen rappaus, punagraniittisokkeli, 2 näyteikkunaa ja katosovi välissä, 3 tummapuitteista ikkunaa + 3 ullakkorakoa, kulmatornissa
  ulkoneva lasierkkeri (2 ikkunanauhaa, ulkonema 0,5 m arvioitu) ja puinen pariovi. Liikkeiden tekstejä ei kopioitu.
- **Panot** (huhti 2026, lehdetön): "2 Rautatienpuistokatu" 61.4810783, 21.7952537 (h 262 / 313 / 357, p 15) ja "1 Rautatienpuistokatu" 61.4812327,
  21.7954845 (h 265 / 320, p 15 / 18). **Kalibrointi kuoresta** (etelänurkka s 0, talojen sauma 31,1, torni 40,4–43,2, räystäät): kamerat s 19,16 /
  10,96 m seinästä (k 1,09) ja s 38,93 / 8,42 m (k 1,13); korkeus z = 1,098·z − 0,71 ja z = 1,135·z − 1,04 (jalkakäytävästä seinän juurella).
  Oppi: kahden panon välinen GPS-ero heitti 2,7 m – sido aina kuoren kiintopisteisiin, älä toiseen panoon.
- Akselin s 20,4–21,6 alaikkuna oli puunrungon takana (toistettu). Kattolyhdyt jätetty pois. Vertailukuva `Claude outputs/rautatienpuistokatu_111_109_vertailu_19_11.jpg`.
  c064 testipoltettu (19 000 kärkeä; ennen 17 558).

## 19.11.2026 ilta – ALOITA TÄSTÄ (uusi chat: JULKISIVUINVENTAARIO, Itsenäisyydenkadun loput → Rautatienpuistokatu)

Vastaa suomeksi, lyhyesti, kuva jokaisesta muutoksesta (Street View vasemmalla, peli oikealla). Tämä luku riittää aloitukseen ja korvaa luvun
"klo 17 – ALOITA TÄSTÄ"; yksityiskohdat ovat ylempänä talokohtaisissa luvuissa (19.11: 166, 167, 164, 585, 600/601, 1228, PYSÄKÖINTIHALLI 164).

### Tilanne
- **Itsenäisyydenkadun keskustan erä** (taulukko luvussa "ITSENÄISYYDENKATU, keskustan erä"): valmiina 415, 118, 116, 119, 121, 107, 7, 166, 167, 164, 600, 601,
  1228 sekä 585:n pohjoispääty ja länsisivu. **Jäljellä: 585:n koillis- ja eteläiset sivut** (seinälista luvussa "585 … länsisivu"), **113** (kuoresta puuttuu kadulle näkyvä
  lasikuistiosa → jalanjälkiratkaisu kuten 136), **115** (kioskipaviljonki, vain väri korjattu). 569 jätetty (aidan takana).
- **OMISTAJAN OHJE 19.11 (uusin): Itsenäisyydenkadun loput (585:n muut sivut, 113, 115) jätetään myöhemmäksi – NYT RAUTATIENPUISTOKATU**, pohjoispäästä
  (keskusta) etelään. Talotaulukko on luvussa "RAUTATIENPUISTOKATU – talotaulukko": tee vain rivit joissa lukee TEKEMÄTTÄ.
- Kaikki 19.11 tehty on omistajan kansiossa (takaisinluvulla tarkistettu) ja **Modal-polttamatta**. GitHubin commit `itsenäisyydenkatu` (19.11 klo 16.33)
  sisältää julkisivutyöt 1228:aa edeltävään asti; **pushaamatta: 1228, 585:n länsisivu, 111/109, Keskuskartanon korjaus (f1228.py, f585.py, f111.py, facades.json, kivi.py) ja tämä tiedosto**. Päivitä taulukon Tila-sarake ja
  ILLAN MODAL-JONO jokaisen talon jälkeen – valmiita ei tehdä uudelleen.
- **Modal-jono nyt:** `city 64 c046,c047,c048,c051,c061,c063,c064` ja `bake bepop --samples 64` (c064:ssä nyt myös 111/109). zones.py, zones2.py, gen.py, kivi.py muuttuivat 19.11 → push ja Actions
  "porikit image" vihreäksi ENNEN ajoa. Tarkistus: lohkon kärkimäärä kasvaa; Modal-lokissa rivi `facades.json: <polku>`.
- **Auki omistajalta:** (1) pysäköintihallin 164 läpiajotesti – omistaja ei ole vielä ajanut; ennen c051:n Modal-polttoa aukot eivät näy (auto ajaa umpiseinän
  läpi). Jos kelpaa: sisus Blender-moduuliksi omistajan kuvista. (2) "katot irti seinistä keskustassa" – ei toistunut, odottaa kuvakaappausta.
  (3) 167:n länsiseinä leipoutuu tummaksi – katso 64 näytteen poltosta ennen värin säätöä. (4) Korjauskierroksen lista luvussa "Antinkadun loput talot".

### Säännöt (omistaja)
- Push ja Modal-ajot tekee omistaja; avaimia/salaisuuksia ei käsitellä. Lataukset ja poistot vain luvalla.
- Street View -kuvia ei viedä peliin eikä GitHubiin: niistä luetaan vain mitat, värit, materiaalit. Vertailukuvat vain kansioon `Claude outputs/` (gitignore).
- Tunnista talo ID:stä ja osoitteesta ennen muutosta. Älä keksi olemattomia: näkemätön osa jätetään paljaaksi tai merkitään "toistettu / peilattu" skriptiin
  ja taulukkoon. Logoja, nimikilpiä ja taideteoksia ei kopioida (kyltit tyhjinä väripintoina). Lukittuja (KARHU-värit, 603/602/604) ei muuteta.
- **Omistajan päätös 19.11: vanhoja julkisivuja ei nosteta**; UUSISSA taloissa z mitataan jalkakäytävästä ja itemit nostetaan `PV = 0.26` (malli f166.py),
  koska pelin jalkakäytävä on 0,26 m lohkon maanpinnan yläpuolella.
- **Toinen chat muokkaa samaa kansiota (radio, jalankulku, sisätilat, index.html):** stage `index.html`, `SIIRTO_TOISELLE_TILILLE.md`, `zones.py`,
  `facades.json`, `styles.json` AINA juuri ennen vientiä, tee muutos laitteen versioon, käytä `expectedMtimeMs`, ja lue takaisin + `cmp`.

### Ympäristö (pilvi alkaa tyhjänä, ~5 min)
```
git clone https://github.com/villeaklinikkasomero/porin-kopterilento.git /home/claude/pori      # + stage koneelta GitHubia uudemmat tiedostot (ainakin
#   index.html, blender/{facades.json,zones.py,zones2.py,gen.py,kivi.py}, tools/rautalanka/facades/*.py, tämä tiedosto) ja kopioi ne kloonin päälle
pip install bpy shapely opencv-python-headless scipy pillow --break-system-packages
mkdir -p /home/claude/mmlproc /home/claude/out /home/claude/w && cd /home/claude/mmlproc && tar xzf /home/claude/pori/pipeline/data/porikit_data.tgz && mv data/mmlproc/* .
cd /home/claude/pori && nohup python3 -m http.server 8765 &        # kuolee vuorojen välissä: käynnistä uudelleen ennen gshotia
sed -i "s#/home/claude/.npm-global/lib/node_modules/#/opt/npm-tools/node_modules/#" tools/rautalanka/gshot_sv.mjs     # ÄLÄ vie tätä muutosta kansioon
```
Poltto (YKSI kerrallaan, 8 Gt): c-lohko `cd blender; PYTHONPATH=/home/claude python3 city.py c048 8` (~75 s), nimetty lohko `python3 run.py bepop 8`.
Tulos `/home/claude/out/bl_<lohko>.js` → kopioi `/home/claude/pori/` testiä varten (EI kansioon). Pelikuva:
`ZONE=- node tools/rautalanka/gshot_sv.mjs index.html out/ views.json` (`[{"k":"a","x":..,"y":..,"h":..,"p":..,"fov":90}]`; pysty-SV 743×1026 ↔ pelikuvan keskirajaus).

### Yhden talon työtapa (15–25 min)
1. **Onko talolla oma kuori?** `raw.pkl`:ssä `raw[ID]` ('W'-monikulmiot, z 0 = seinän alareuna, 3 desimaalia). Jos ID on `lod2.js`:n `hide`-listalla eikä
   raw:ssa, talo on **toisen talon kuoren pätkä**: etsi kuori jonka 'G'-monikulmio peittää jalanjäljen (600/601 → 588 `bepop`, 1228 → 1229 c064).
   Silloin facades.json-merkintä tehdään KUOREN id:lle, seinälle `bare_s: [s0, s1]`, ja kaikki saman kuoren talot samaan merkintään/skriptiin (f588.py).
2. **Seinälinja** raw.pkl:stä, `a`→`b` niin että katu on oikealla.
3. **Street View** sovelluksen selaimella: `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=LAT,LON&heading=H&pitch=P&fov=90`,
   lat = 61.486 + y/111437, lon = 21.796 + x/53278. Yksi erä = navigate + 4×10 s odotus (erän raja 50 s), sitten ERILLINEN screenshot; uusi suunta samasta
   panosta voi olla sumea 30–60 s. Panon todellinen paikka URL:sta (`@lat,lon`). Kuva tallentuu pilveen `/tmp/claude-tool-results/*/…jpg`.
4. **Oikaisu ja mittakaava:** `python3 tools/rautalanka/rectify.py kuva.jpg cx cy heading pitch Ax,Ay Bx,By s0 s1 z0 z1 out.png 36 90 ch`.
   **Älä luota pelkkään kuoren pituuteen: kuori seuraa räystästä** (0,3–0,8 m seinää pidempi päistään). Kalibroi kahdesta: nurkat JA räystäskorkeus
   (lod2 `e` / seinän top) → kerroin k kameran suhteen; helpointa siirtää kamera k-kertaiselle etäisyydelle ja asettaa `ch` niin että jalkakäytävä on z 0
   (166, 164), tai kirjata kaava skriptin alkuun (601: k 1,107). Pano-GPS heittää 1–2 m.
5. **Skripti** `tools/rautalanka/facades/f<ID>.py` (uusimmat mallit: f166.py perus, f167.py recess + parvekepinot + kaksi seinää, f164.py gate,
   f588.py kuoren pätkät + bare_s, f1228.py). Itemit `box`, `winp` (n ruutua – myös pitkä nauha/säleikkö), `glass`, `door`, `balc`; seinälle `bare` + `kind`
   (plaster / brick / wood; `sheet` leipoutuu harmaaksi). Seinäavaimet: **`"recess": [gh, sb, h]`** = koko seinän katutaso sisäänvedetty (pilarit `box` d −sb…0,
   sisäänvedoton osa täytetään `box`illa); **`"gate": [s0, s1, gh, depth, h]`** = oikea aukko seinässä (yksi per seinä); **`"nobrick": true`** merkinnässä =
   punainen pinta ilman tiilisaumaa (toimii nyt myös SPEC-ttömille). `box` ikkunan alla enintään 2,5 cm paksu.
6. **Testipoltto 8 näytettä**, pelikuva samasta panosta, vertailukuva rinnakkain kansioon `Claude outputs/`. Pohjois- ja länsiseinät tummuvat poltossa – ei vika.
7. **Vienti:** stage → muutos laitteen versioon → `device_commit_files` (expectedMtimeMs) → stage uudelleen ja `cmp`. Päivitä taulukko ja ILLAN MODAL-JONO.

### Pysäköintihalli 164 (testi, ks. luku "PYSÄKÖINTIHALLI 164")
index.html, haku `HALL`: `inHall` / `hallZ` / muutokset `carBlocked`, `carGround`, seurantakamera; sisus three.js:llä ilman leivontaa. Poltossa `gate`-aukot
(zones.py `_gate_w`, kivi.py cut_walls-silmukka, gen.py `noback`). Älä laajenna ennen kuin omistaja on kokeillut.

### 19.11 klo 23: bottiautot pysäköivät ja ihmiset nousevat ulos
- index.html liikennelohko: kun botti (ei Yrjönkadun vakioauto) vaihtaa katuosuudelle, 6 % todennäköisyydellä se pysäköi osuuden puoliväliin, jos osuus on
  >30 m, ytimessä, <170 m pelaajasta, ei pääty valoihin, reunakivi on 3,8–9 m kaistan keskiviivasta (`ROAD.asphAt`), eikä kohdassa ole ilmakuvan pysäköityä
  autoa (PARKED, 5,5 m) tai toista pysäköivää bottia (9 m). `c.pk = {ph 0 sisään, 1 seisoo 35–85 s, 2 ulos}`, sivusiirtymä `c.lat` (oletus 1,7).
  Pysäköivä auto on jonologiikan ulkopuolella (takaa tulevat voivat ajaa sen läpi hidastuksen aikana).
- Pysähtyessä `window.__npc.arrive(x, y)`: 50 % yksi aikuinen, 30 % kaksi, 20 % huoltaja + lapsi syntyy reunakiven taakse ja kävelee lähimpään
  kävelyverkon solmuun (<30 m). Ovet eivät aukea eikä hahmoa näy autossa ennen pysähdystä. Auto lähtee tyhjänä; kukaan ei palaa siihen.
- Simulaatio 400 s pelaaja keskustassa: 6 pysäköintiä, 6 ulosnousua, kaikki autot lähtivät, ei virheitä. Lisäksi `cars.update`: negatiivinen dt nollataan.

### 19.11 klo 23.30: pysäköivän auton ovi aukeaa + törmäykset liikenteen kanssa
- **Ovi:** automallit ovat yksi kappale (blender/cars.py piirtää ovisaumat vain viivoina), joten mallia ei muutettu. Pelissä pysäköineen auton päälle
  asetetaan auton värinen ovilehti (sarana etuoven etusaumassa, auton nokka = paikallinen +z) ja tumma aukkopaneeli; `mkDoor`/`doorPool` liikennelohkossa.
  Jalkakäytävän puolen ovi aukeaa aina, kadun puolen 40 %:ssa (`P.two`). Aikajana `P.e`: 0–0,6 s aukeaa, 0,6 s ihmiset ulos (`__npc.arrive`),
  2,6–3,2 s sulkeutuu. Vain henkilöautot (tyypit 0–2) pysäköivät. Mitat on tehty viistoperälle; farmarissa ja muissa ovi voi olla hieman sivussa saumasta.
- **Törmäys:** `carBlocked` estää pelaajan autoa ajamasta liikenteen auton sisään (kolme ympyrää/auto, säde 1,75 m; vain lähentävä liike estetään, joten
  peruuttaa voi aina). Botit jarruttavat ja jonottavat pelaajan auton taakse, kun se on samalla katuosuudella niiden kaistalla (<45 m edessä).
  Botit tallentavat sijaintinsa `c.wx, c.wy`. Tekemättä: botti–botti-väistö risteyksissä (ajavat yhä ristiin toistensa läpi valottomissa risteyksissä),
  botin sivutörmäys pelaajaan, kopteri ja kävelijät eivät vaikuta autoihin. Törmäystä ei testattu ajamalla (headless ei käynnistä peliä).
- Huom: laitteen index.html:ssä oli c23:n jälkeen taas vanha rivi `if (dt > 0) sigT += dt` – korvattu uudelleen muotoon `if (dt < 0) dt = 0; sigT += dt`.

### 20.11 klo 00: bottien väistäminen, ruuhkien purku, pelaajan auton asteittainen vaurio
- **Risteykset ilman valoja:** solmu (≥3 haaraa) on kerrallaan yhden botin varaama (`n.res`, `n.resT`; varaus <12 m ennen solmua, muut pysähtyvät 7 m ennen;
  vapautuu 0,9 s ylityksen jälkeen tai 5 s kuluttua). Ensin tullut ajaa ensin – ei oikealta tulevan sääntöä.
- **Pinoutuminen:** botti ei aja seuraavalle osuudelle, jos sen alussa (<6,5 m) on auto (odottaa kulmassa enint. 8 s, `c.blk`). Yrjönkadun paino 30 → 8
  (paino 30 + 22 vakioautoa teki lyhyelle osuudelle pysyvän ruuhkan: 4–6 autoa päällekkäin yli 4 min). Botti, joka seisoo >30 s yli 120 m pelaajasta,
  siirretään satunnaiseen solmuun (`c.st`). Simulaatio 6 min: päällekkäisiä autopareja 18 → 2,3 / näyte, pisin seisonta 346 s → 30 s.
- **Pelaajan auto:** kolhun vahinko (|v|−4)·2,2 (ennen (|v|−5)·4): 50 km/h ≈ 22 %. Kunto <60: huippunopeus 22 m/s + harmaa savu; <45: ohjaus vetää
  oikealle (0,03 rad); <30: 14 m/s + musta savu; 0 = hajoaa kuten ennen. Savu = `CAR.smoke` (≤14 läpikuultavaa palloa, noT). Ei korjaantumista ajon aikana.
  Ei testattu ajamalla (headless ei käynnistä peliä).

### 19.11 klo 24: pelaajan kävely ja juoksu uusiksi (länkisääret pois) – hahmo.js, index.html, tools/hahmo/
- **Syy:** vanha askellus heilutti lonkkaa ja polvea siniaalloilla; nilkat kulkivat 26 cm toisistaan (lonkkanivelet 23 cm), jalat olivat ilmassa
  kaksoistukivaiheessa ja liukuivat maata pitkin. Sama klippi on yhä NPC:illä (`npc_*.js`) – niitä EI muutettu.
- **Uusi askellus** (`Poser.gait` + `_foot`, parametrit `Poser.WALK` / `Poser.RUN`): jalkaterän rata määrätään ensin (kantaisku → koko pohja →
  päkiäponnistus → heilahdus), lonkka ja polvi ratkaistaan siitä kahden luun IK:lla, polvi osoittaa menosuuntaan. Nilkat 12 cm (kävely) / 8 cm
  (juoksu) toisistaan, varpaat 6° ulos, varvasluu (`ball_*`) taipuu ponnistuksessa. Lantio: kierto, kallistus, sivuttaisliike tukijalan päälle,
  pystyliike; hartiat kiertyvät vastaan; juoksussa lentovaihe. Mitattu: tukijalan päkiä pysyy paikallaan < 1 mm (kävely ja juoksu).
- Idle: `LEG_IN` 4,5 → 7,0 (nilkat 26 → 19 cm), ettei asento levene pysähtyessä. Sit ennallaan (4,5).
- **index.html:** `timeScale` vastaa klippien askelpituutta: Walk `sp / 1.36` (ennen 1.45), Run `sp / 4.65` (ennen 4.3). Jos WALK/RUN `stride`
  muuttuu, muuta nämä: Walk = stride, Run = stride / 0,667.
- **Uusi työkalu `tools/hahmo/kavely_glb.py`** (`pip install mathutils`): lukee `Poser`-luokan porikopteri_hahmo.py:stä ja leipoo Idle/Walk/Run/Sit
  suoraan hahmo.js:n GLB:hen ilman Blenderia (verkko ja tekstuurit eivät muutu). `--check` vertaa skriptiä ja GLB:tä (0 = samat). hahmo.js on
  tehty tällä; Blender-skriptiä EI ajettu uudelleen (sama Poser-koodi, `bake_action` hyväksyy nyt myös siirtymävektorin).
- Tarkistettu pilvessä renderöimällä klipit edestä ja sivusta (three.js headless); pelissä ei testattu (begin() ei käynnisty headless).
- Auki: sivuaskel (Q/E) käyttää Walk-klippiä. (NPC:t korjattu, ks. seuraava merkintä.)

### 20.11 klo 00.30: sama askellus bottikävelijöille (npc_*.js, index.html, tools/hahmo/)
- Kaikkien kuuden mallin Walk ja Idle leivottu uudestaan `kavely_glb.py`:llä (sama `Poser` kuin pelaajalla; NPC:iden vanhat klipit olivat täsmälleen
  vanhan Poserin tulos, tarkistettu `--check`). Verkot ja tekstuurit ennallaan. Nilkat kävellessä 8–13 cm toisistaan (ennen 21–34 cm).
- `Poser` skaalaa askelluksen pituusmitat jalan pituuteen (`LEG_REF` 0,8897 m = pelaaja, `Poser.scaled`). Tämän takia myös hahmo.js leivottiin
  uudestaan (ero < 0,1 mm). `kavely_glb.py` ohittaa puuttuvat klipit, `--clips Walk,Idle` rajaa, ja tulostaa askelparin pituuden pelin mittakaavassa.
- **index.html:** bottien `timeScale = max(0.6, sp / STRIDE[c.k])` (ennen `(kid ? 1.25 : 1) * sp / 1.25`); `STRIDE` = nainen_a 1,213, nainen_b 1,173,
  mies_a 1,344, mies_b 1,414, tytto 0,926, poika 1,006 m. Jos mallin skaala tai WALK.stride muuttuu, aja työkalu ja päivitä taulukko.
- Tarkistettu renderöimällä kaikki kuusi edestä ja sivusta; tukijalan liukuma < 1 mm. Pelissä ei testattu.
- VAROITUS (tiedostosilta): `device_commit_files` kirjoitti kerran saman stagedPath-polun VANHAN sisällön (index.html palasi hetkeksi versioon ilman
  20.11 klo 00 -automuutoksia; korjattu heti, nyt mukana). Käytä jokaisella tallennuksella uutta polkua ja tarkista koko jälkikäteen.

---

## 20.11.2026 klo 01 – Auton vaurioportaat näkyviin (c26)

**Tehty (viety koneelle, EI pushattu):**
- `auto.js` ja `auto_m.js` vaihdettu mallichatin uusiin GLB:ihin, joissa osat ovat portaittain: `Osa_d0 … Osa_d3`
  (Hood, BumperF/R, FenderFL/FR, HeadlightL/R, TaillightL/R, MirrorL/R, SideL/R, Windshield – 14 osaa).
  Lähde: `tools/vehicles/porikopteri_auto.py`, raportti `tools/vehicles/porikopteri_auto_vauriot.md`.
- `index.html`, `loadCar`: `CAR.setDmg(st)` kerää osat nimestä `/^(.+)_d([0-3])$/` ja näyttää kustakin osasta
  **korkeimman portaan, joka on ≤ nykyinen** (kaikilla osilla ei ole joka porrasta). `PlateText_front` piiloon portaalla 3.
- Auton askeleessa porras kunnosta: hp < 60 → 1, < 45 → 2, < 30 → 3 (samat rajat kuin nopeusrajoitus ja savu).
- Törmäyslaatikkoa ei muutettu, vaikka portaan 3 puskuri on 8 cm pidempi.

**Tarkistettu:** headless-kuva pelin sisältä portaista 0–3 (`Claude outputs`-tyyppinen koekuva `auton_vauriot_19_11.jpg`), ei konsolivirheitä.
**EI testattu:** ajaminen ja törmäys selaimessa (headless ei pysty `begin()`iin) – omistaja kokeilee. Korjautuuko malli, kun kunto palautuu
(uusi auto / respawn): `setDmg` kutsutaan aina kun porras muuttuu, myös alaspäin, joten pitäisi.
**Huomio:** osia on enemmän → hieman enemmän piirtokutsuja; jos kännykällä nykii, kevytmallista (`auto_m.js`) voi pudottaa portaat 1–2.

---

## 20.11.2026 klo 02 – Pehmeä savu ja huntupilvet (c27)

**Tehty (viety koneelle, EI pushattu), vain `index.html`:**
- **Savu:** kiinteät pallot pois. `smokeStep(dt, every, dark, x, y, z)` + `SMOKE` (ennen `window.__game`-riviä): kameraan kääntyvät spritet,
  yksi proseduraalinen canvas-tekstuuri (16 päällekkäistä pehmeää läiskää → repaleinen reuna). Jokainen pöllähdys pyörii, paisuu, ajautuu tuulen mukana,
  nousee hidastuen ja ohenee; tumma savu vaalenee levitessään. Tahti: hp < 60 → 0,16 s, < 45 → 0,09 s, < 30 → 0,05 s ja musta. Enintään 40 spriteä.
  Testikoukku `window.__smoke`.
- **Huntupilvet:** taivaskupolin sisään toinen kuori (r 5900, ShaderMaterial, ei tekstuuria): venytetty fbm-kohina, kerran vääristetty, ohenee horisonttiin,
  liikkuu hitaasti (`onBeforeRender` päivittää ajan). Määrä säädetään `smoothstep(0.46, 0.78, c)` -rajoista ja lopun kertoimesta 0.62.

**Tarkistettu:** headless-kuva (`savu_ja_pilvet_19_11.jpg`), ei konsolivirheitä. **EI testattu:** savu ajossa (päivittyy vain auton askeleessa, kuten ennenkin –
jos pelaaja nousee autosta, pöllähdykset jäätyvät paikoilleen; korjaus olisi kutsua `smokeStep(dt, 0)` pääsilmukasta).

---

## 20.11.2026 klo 03 – Uusi pelikonsepti + pilottitapaus "Karhu katsoo väärään suuntaan" (c28)

**Konsepti (omistaja hyväksyi):** "Outojen asioiden toimitus". Pelaaja on Radio Porikopterin kenttäreportteri; Porin slogan "Todella outo, ehdottoman uniikki".
Suunnitelma: https://claude.ai/artifact/TMz2BXrs6MPJaUxXA6bXwA (12 tapausta, outousasteet, viisi mekaniikkaa). Omistaja: murteesta ja sloganin luvasta ei tarvitse huolehtia.

**Tehty (viety koneelle, EI pushattu):**
- `index.html`: lohko `window.__case` / `window.__caseTick` (heti `window.__smoke`-rivin jälkeen), kutsu pääsilmukassa `__statueTick`in perässä, koukku kävelijöiden `greet`issä (`__case.ask(v)`).
  Tilat `st`: 0 odottaa (40 s aloituksesta) → 1 soitto soi (3 leikettä, tekstitys kortissa, radio vaimenee) → 2 etsintä (ei karttamerkkiä; ohikulkija neuvoo nuolella
  kameran suhteen; **K** = selkosuomi, **L** = soitto uudestaan) → 3 nauhuri (jalan < 11 m karhusta: 1/2 = katso 3 s; karhu kääntyy pelaajaa kohti 55°/s VAIN kun
  sitä ei katsota; 2/2 = katso uudelleen kun asento muuttunut > 25°) → 4 otsikon valinta (napit tai **1–3**) → 5 juontaja lukee jutun → 9 valmis:
  tallennus `localStorage['pori-tapaus-1'] = {k, n, plain}`, juttu lisätään Radio Porikopterin soittolistaan, karhu vilkuilee pysyvästi. Kuulijat 14 + 3 / 17 / 1.
  Testaus: `__case.reset()` nollaa, `__case.test = true` ohittaa `started`-ehdon.
- Tekstit `tools/radio/tapaus1.json` → `tools/radio/tapaukset.py <onnx> radio/ 1` → `radio/tapaus1.json` + 11 mp3:ää (`tapaus1_soitto_1–3`, `_neuvo_{m,n,l}_N`, `_juttu_{a,b,c}`).
  Soittaja = naisääni 1,22x + puhelinsuodin. Uusi tapaus = uusi `tapausN.json` + oma lohko tai moottorin yleistys (nyt karhun logiikka on kovakoodattu).

**Tarkistettu:** headless-simulaatio koko ketjusta (kuva `tapaus1_karhu_19_11.jpg`), tallennus ja soittolistalisäys toimivat, ei konsolivirheitä.
**EI testattu:** oikea pelaaminen (kävely karhulle, katseen tunnistus pelin omalla kameralla, äänet). Nauhurin rivi (oikea yläkulma, top 74 px) voi mennä muun HUDin päälle.
**Seuraavaksi:** omistajan koepeluu → säädöt → tapausmoottorin yleistys ja tapaukset 2–4 (lokki, aina vihreä, kanava jota ei ole).

---

## 20.11.2026 klo 04 – Pulut ja lokit (c29)

**Tehty (viety koneelle, EI pushattu):**
- `linnut.js` (`{pulu, lokki}` base64-GLB; lähde `tools/props/porikopteri_linnut.py`, animaatiot Fly, Glide, Idle, Walk, Peck; värit verkon väriattribuutissa).
- `index.html`: lohko `window.__birds` / `window.__birdTick` juuri ennen `window.__game`-riviä, kutsu pääsilmukassa `__caseTick`in perässä.
  - Maaryhmät `B.G`: puluparvia 4 (kosketuslaitteella 2), koko 4–7; lokkiryhmiä 2 (1), koko 1–2. Paikka = vapaa jalkakäytävän/kiveyksen kohta 14–85 m pelaajasta
    (`ROAD.paveAt`, ei ajorataa, jokea eikä taloa). Linnut kävelevät (pulu 0,24 m/s) ja nokkivat.
  - Pako: pelaaja jalan 4,5 m, autolla 9 m, kopterilla alle 14 m korkeudessa 16 m → ryhmä nousee viiveellä lintu kerrallaan ja laskeutuu 30–70 m päähän
    pelaajasta poispäin (Bezier-kaari, korkeus pulu 6–11 m, lokki 11–16 m; lokki liitää kaaren keskiosan).
  - Kaartelevat lokit `B.A`: 2 ryhmää (1), koko 1–2, ympyrä r 22–44 m, korkeus 24–40 m, välillä siiveniskuja. Jos pelaaja etääntyy yli 150 m, ympyrä ajautuu perään.
  - Yli 140 m taakse jäänyt maaryhmä siirtyy pelaajan lähelle; yli 90 m päässä olevia ei animoida. Mittakaava 1,25.

**Tarkistettu:** headless-kuva (`linnut_20_11.jpg`), nousu ja laskeutuminen simuloituna, ei konsolivirheitä.
**EI testattu:** pelaaminen; suorituskyky puhelimella (enimmillään n. 30 luurankomallia). Linnut eivät väistä bottiautoja eivätkä kävelijöitä, ei ääniä.
**Jatko:** tapaus 2 "Lokki ja porilainen" voi käyttää samaa lokkia (`mk('lokki')`, lento `rise`-kaarella katolle `bldTopAt`).

---

## 20.11.2026 klo 06 – Autokilpailu "Kespan lenkki" (c30) + konseptin suunta

**Konseptikeskustelu (omistaja):** mainosmyynti ei ole ongelma (kuvina/äänenä peliin); tavoite on päivittäinen paluu ("putki ei katkea"). Käyty läpi: päivän lähetys,
karhu karannut, kaupunginosat vastakkain, pelaa lokkina, **Asu Porissa** (oma ikkuna jonka valo palaa käyntipäivinä, torin päivän koju, päivän kala), illan visa klo 19,
puhuvat tekoälyasukkaat. Omistaja: "tehdään" + ensin autokilpailu. **Seuraavaksi: Asu Porissa -pienin versio (ikkuna, koju, kala).**

**Tehty (viety koneelle, EI pushattu), vain `index.html`:**
- `KESPA` (reitti 3,34 km, 140 pistettä pelimetreinä + käännösohjeet `[metri, nuoli, nimi]`) ja lohko `window.__race` / `window.__raceTick` ennen `window.__game`-riviä;
  kutsu pääsilmukassa `__birdTick`in perässä; `carBlocked` ottaa mukaan kisabotit.
- Reitti (omistajan sanelema): lähtö Mikonkadun ensimmäisistä valoista (solmu 20,-336; viiva 13 m ennen) → Mikonkatu länteen → Otavankatu → Luvianpuistokatu →
  poliisilaitoksen ympyrä (-580,-590, vastapäivään) → Luvianpuistokatu → Maamiehenkatu → Tiilimäen Nesteen pihan ympäri (OSM-way 357449244) → Maamiehenkatu →
  Luvianpuistokatu → ympyrä → Otavankatu → Itsenäisyydenkatu → Antinkatu → Liisankatu → Isolinnankatu → Mikonkatu → maali lähtöviivalla.
  Laskettu `CITY.r`-tieverkosta Dijkstralla katu kerrallaan (ympyrän kaaret suunnattuina); Liisankadun kävelyosuudet (k=0) otettu mukaan.
- Käyttö: autossa **G** tai nappi "🏁 Kespan lenkki" → pelaaja ja 3 bottia (punainen, valkoinen, vihreä; pelaajan automallin kloonit) ruudukkoon. Lähtö kun valo vaihtuu
  vihreäksi (jos jo vihreä: 3 s lasku). Keltainen nauha näyttää reitin, yläreunassa sija, aika ja seuraava käännös. Eteneminen = projektio reitille 45 m ikkunassa
  eteenpäin (ei voi oikaista eikä sekoittaa meno- ja paluuosuutta). Maalissa sija ja aika; oma ennätys `localStorage['pori-kespa-best']`. G uudestaan tai autosta
  nousu keskeyttää.
- Botit: pure pursuit reittiä pitkin, huippu 20,5 / 22,5 / 24,5 m/s, hidastavat mutkiin, ohittavat hitaamman vasemmalta. Muu liikenne ja valot toimivat normaalisti.

**Tarkistettu:** headless-simulaatio koko kierroksesta (pelaaja 17,5 m/s tasaisesti = 3:10, botit n. 3:30), ruudukko- ja ympyräkuva (`kespan_lenkki_20_11.jpg`), ei konsolivirheitä.
**EI testattu:** oikea ajaminen; bottien tasapaino ihmistä vastaan; törmäys bottiin; Nesteen pihan ajettavuus (rakennus/katos voi olla tiellä); jonottava muu liikenne
lähtöruudukossa. **Ei vielä:** päivän tulostaulu verkossa (LB käyttää kierroksen kenttää – tarvitsee oman kentän 'k'+päivä), bottien vauriot, kierrosmäärän valinta.

---

## 20.11.2026 klo 07 – Pysäköidyn auton lainaus (c31)

**Tehty (viety koneelle, EI pushattu), vain `index.html`** (yhdistetty toisen istunnon taidemuseo/jäähalli-muutosten päälle):
- `window.__parked`: ilmakuvan pysäköidyt autot rekisteriin (x, y, yaw, väri, instanssi) siinä missä ne piirretään. `cars.vanish(c)`: liikenteen auto alkaa uudelleen kaukaa.
- `walkNear()` palauttaa oman kulkuneuvon jälkeen `takeNear()`: `'heli'` (jätetty kopteri < 6 m) tai `'take'` (pysäköity auto < 3,4 m: ilmakuvan auto, parkissa seisova
  liikenteen auto tai aiemmin jätetty oma auto). Vihje "ota auto", Enter/F → `takeDo`.
- `takeDo`: pelaajan automalli siirtyy auton paikalle ja suuntaan ja saa sen värin (`CarPaint`-materiaali), pysäköity instanssi piilotetaan. Siihen asti ajettu auto jää
  kopiona paikalleen (`TAKE.left`, yksi kerrallaan, vauriot ja väri tallessa) ja sen saa takaisin. Uusi auto alkaa ehjänä (hp 100).
- Kopterista: `VEH` vaihtuu autoksi kesken pelin, kopteri jää laskeutumispaikalle (`TAKE.heli`) ja siihen noustaan kävellen takaisin; maamerkkikierros on tauolla sen ajan.
  Kespan lenkin voi ajaa lainatulla autolla.

**Tarkistettu:** headless (`auton_lainaus_20_11.jpg`): lainaus kopterista, toinen lainaus (edellinen jää kopioksi hp 55), paluu kopteriin; ei konsolivirheitä.
**EI testattu:** pelaaminen; N (uusi kierros) ja auton hajoaminen lainatulla autolla kopteri-istunnossa (kopteri pakotetaan näkyviin `__takeTick`issä, mutta kierroksen
tila voi sekoilla). Pysäköityihin autoihin ei edelleenkään voi törmätä. Omistajan huuto on vain teksti ruudulla, ei ääntä.

---

## 20.11.2026 klo 09 – Pakettiauto ja farmari ajettaviksi (c32)

**Tehty (viety koneelle, EI pushattu):**
- Uudet mallit mallichatista: `auto_van.js` / `auto_van_m.js` (pakettiauto) ja `auto_est.js` / `auto_est_m.js` (farmari); lähde `tools/vehicles/porikopteri_autot.py`
  (`--type van|estate`), raportit `tools/vehicles/porikopteri_pakettiauto_raportti.md` ja `…farmari_raportti.md`. Sama rakenne kuin `auto.js` (Wheel_*, `_d0…_d3`, `CarPaint`).
- `index.html`: `loadCar(t)` lataa tyypin kerrallaan muistiin `CARM[t] = {root, wheels, setDmg}`; `useCar(t)` vaihtaa `carG`:n mallin, renkaat, vauriofunktion ja
  tyypin arvot `CARTY`: törmäyslaatikon puolipituus/-leveys (`CAR.hl/hw`: viistoperä 2,1/0,9, paku 2,4/0,97, farmari 2,3/0,91), kiihtyvyys ja huippunopeus
  (`CAR.acc/top`: paku 3,3 ja 21 m/s, muut 4,2/4,0 ja 24), kuljettajakameran siirto (`CAR.cam`, raporttien ohjauspyöräpisteistä). `setCarType(t)` = toive + lataus.
- Lainaus valitsee mallin pysäköidyn auton tyypistä (`window.__parked[].k`, liikenteen `c.k`): 0 viistoperä → viistoperä, 1 sedan ja 2 katumaasturi → farmari, 3 → pakettiauto.
  Jätetty auto muistaa tyyppinsä (`TAKE.left.type`).

**Tarkistettu:** headless (`paku_ja_farmari_20_11.jpg`): paku ja farmari lainattu, väri siirtyy, vaurioporras 3 vaihtuu, ei konsolivirheitä.
**EI testattu:** ajaminen; kuljettajakameran paikka pakussa (laskettu raportin luvuista, kuvassa näyttää olevan ohjaamossa mutta ei varmistettu ajossa); kevytmallit puhelimella.
**Tiedossa:** kadulla seisovat autot ovat yhä vanhoja kevytmalleja (cars.js), joten katumaasturi muuttuu lainatessa farmariksi. Kespan lenkin botit kloonaavat
pelaajan senhetkisen mallin (pakulla ajaessa botitkin ovat pakuja).
