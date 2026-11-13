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
