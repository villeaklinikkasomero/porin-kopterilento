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
