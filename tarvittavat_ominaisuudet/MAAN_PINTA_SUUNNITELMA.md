# Maan pinta jalan ja autolla – suunnitelma (21.11.2026)

Omistaja: *"maa näyttää suht pahasti, että olisi lunta ja tapahtuu kaikkea vuotoa ilmakuvista rakennetuilla alueilla, niin nurmikolla kuin asfaltoiduilla teillä.
Pelistä pitäisi saada mahdollisimman autenttinen kokemus … miten voitaisiin maasta pelatessa käyttää monipuolisemmin tekstuureja tai hieman maasta nousevia itemeitä."*

## 1. Nykytila ja miksi maa näyttää huonolta

Maa on nyt ilmakuva, joka on venytetty korkeusmallin päälle:
- `src/js/030_maa_ilmakuva.js`: ydin (`orto.jpg`) ja ulkokehä (`outer.jpg`), 6 m / 18 m ruudukko, **MeshBasicMaterial** (ei valaistusta, ei normaaleja).
- `src/js/033_ilmakuva_tarkka.js`: tarkat 512 m laatat `ot/ot_i_j.jpg` (0,25–0,33 m/px) lähellä pelaajaa.
- `src/js/031_maa_nurmi.js` (`grassify`): proseduraalinen ruohokuvio siellä, missä kuva on vihreä; `ROADCUT` leikkaa kuvan teiden kohdalta.
- `src/js/032_heina.js`: instanssoidut heinätupsut kameran lähellä vihreillä alueilla.
- `src/js/060_kadut.js` (+ `roads.js`): ydinkeskustan kadut geometriana (asfaltti, jalkakäytävä, reunakivet, suojatiet);
  ulkoalueen tiet `src/js/180_lentoasema.js` -nauhoina.

Ongelmat maan tasolta katsottuna:
1. **"Lumi"**: ilmakuvan vaaleat kohdat (aurinkoiset betonit, kattojen heijastukset, ylivalottuneet nurmet, jäkälä, hiekka) piirretään MeshBasicilla
   täyteen kirkkauteen ilman varjostusta. 0,25 m/px kuva on maasta katsottuna 1–3 m:n etäisyydellä sumea läiskä.
2. **Vuoto**: ilmakuvaan on palanut kaikki maassa ollut: autot, varjot, puiden latvukset, kattojen reunat (rakennukset kallistuvat kuvassa),
   bussikatokset, ihmiset. Ne näkyvät nyt maahan "maalattuina" nurmella ja asfaltilla. Tie leikataan pois vain siellä, missä `roads.js` tuntee tien.
3. **Ei rajapintoja**: nurmen ja asfaltin raja on ilmakuvan sumea siirtymä – ei reunakiveä, soraa, multaa, kasvillisuuden reunaa.
4. **Ei pienkorkeutta**: maa on täysin sileä 6 m kolmioina; maasta nousevia pieniä asioita (kaivonkannet, kaivot, pollarit, aidat, pensaat, kukkapenkit,
   kiveykset, lehdet) on vähän.

## 2. Tavoite

Maasta (silmät 1,7 m) ja autosta katsottuna maa näyttää **materiaaleilta**, ei valokuvalta: nurmi, asfaltti, betonilaatta, kiveys, sora, multa, hiekka –
oikeissa paikoissa Porissa. Ilmakuva jää vain **kaukonäkymään ja värisävyn lähteeksi** (makrosävy), lähellä sen korvaavat tiilattavat PBR-tekstuurit
ja matalat 3D-esineet. Toteutus kevyenä: puhelimella yksinkertaisempi taso.

## 3. Ratkaisu kerroksittain

### A. Maankäyttökartta (land cover) – kaiken perusta
Offline-työkalu `tools/maa/maapeite.py` tekee koko kartalle 0,5 m:n luokkarasterin (laatat 256 m, PNG, 4 kanavaa painoina + luokka):

| Luokka | Lähde (paino järjestyksessä) |
|---|---|
| ajorata (asfaltti) | `roads.js` / OSM highway-alueet, `ROADCUT`-rasteri |
| jalkakäytävä / pyörätie | OSM footway/cycleway (+ leveys), `roads.js` pave |
| kiveys / laatoitus (torit, aukiot) | OSM `area:highway`, `place=square`, `surface=paving_stones`, nykyiset `kivetys_*`-alueet |
| pysäköintialue | OSM `amenity=parking` (asfaltti + maalatut ruudut) |
| nurmi | OSM `landuse=grass`, `leisure=park`, ilmakuvan vihreys (NDVI-tyyppinen G−R-indeksi) |
| sora / hiekka | OSM `surface=gravel/sand`, leikkikentät, ratapenkat (sepeli on jo `rata/`) |
| multa / istutus | OSM `landuse=flowerbed`, pensasaidat, puiden juuret |
| metsänpohja | OSM `natural=wood`, `landuse=forest` |
| rakennuksen juuri | rakennusten pohjat + 0,5 m (ilmakuvan kallistuneet katot pois) |

- Ilmakuvan luokittelu täydentää OSM:ää vain siellä, missä OSM:ssä ei ole mitään (värin ja tekstuurin perusteella, ei koneoppimista ensin).
- **Käsikorjaukset**: `tools/maa/korjaukset.json` (polygonit + luokka) – omistaja voi ilmoittaa "tässä on nurmi, ei asfalttia".
- Mahdollinen lisälähde: MML:n maastotietokanta ja Porin kaupungin avoin data (puisto- ja katualueet). Lisenssit tarkistetaan ennen käyttöä.

### B. Maan materiaali (shader) – "lumi" ja vuoto pois
Yksi `ShaderMaterial`/`onBeforeCompile`-laajennus maan ruudukoille (030, 033, 0335):
- **Lähellä (0–40 m)**: maankäyttökartan painoilla sekoitetut tiilattavat PBR-tekstuurit (albedo + normaali + ORM), 2–4 m toisto,
  **tiilauksen rikkominen** (stokastinen tiilaus / kierto + makrokohina), valaistus: Lambert/Standard + normaalikartta.
- **Keskietäisyys (40–150 m)**: samat materiaalit, mutta ilmakuva antaa värisävyn (makrosävy: kuvan väri sumeana 4–8 m skaalassa, kirkkaus rajattu,
  saturaatio säädetty) → paikallinen vaihtelu säilyy ilman autoja ja varjoja.
- **Kauas (> 150 m) ja kopterista**: nykyinen ilmakuva, mutta **sävy korjattu offline**: ylivalottuneiden kohtien kompressio, valkotasapaino,
  lievä varjojen nosto (`tools/maa/orto_savy.py` laatoille `ot/` ja `orto.jpg`).
- **Vuodon poisto**: lähietäisyydellä ilmakuvaa ei käytetä lainkaan albedona. Autot, varjot ja latvukset katoavat itsestään, koska materiaali tulee
  luokkakartasta. Puiden kohdalle (puurekisteri / `trees.js`) varjo- ja lehtikarikedekaalit.
- Siirtymä luokkien välillä: korkeuskartta-pohjainen sekoitus (esim. ruoho kasvaa kiveyksen saumoista, sora leviää reunoille), ei lineaarista sumeutta.

**Tekstuurit** (CC0, ambientCG 1K, osa jo kansiossa `tex/*.zip`):
Grass004 (nurmi), Ground054 (multa / polku), Asphalt025C (ajorata), PavingStones070 (kiveys), Concrete031/034 (betonilaatta, reunakivi),
Tiles074 (laatoitus). Lisättävät: **Gravel** (sora), **Asphalt + paikkaukset** (2. asfaltti, vaaleampi ja halkeillut), **ForestGround** (metsänpohja),
**Leaves** (syksyn lehtikarike), **Sand** (hiekka). Pakataan 512/1024 px KTX2/JPG + ORM, puhelimelle 512.

### C. Tien pinnan yksityiskohdat (asfaltti näyttää asfaltilta)
- 2–3 asfalttisävyä (uusi tumma, vanha harmaa, paikattu) katuluokan ja satunnaisen paikkauksen mukaan; **pyörän urat** kaistoilla (vaaleampi, kiillotettu),
  halkeamat ja saumat decaaleina, **kulunut tiemaalaus** (nykyinen maalaus + kulumamaski).
- **Kaivonkannet, sadevesikaivot ritilöineen, venttiilikannet** – instanssit OSM:n / kaupungin tietojen mukaan tai sääntö: kaivo 25–40 m välein reunakiven vieressä.
- Reunakivi kaikille kaduille (ydin on jo), **ulkoalueilla** asfaltin reunaan sorapiennar + nurmen reuna, ojat.
- Pysäköintialueiden ruutumaalaukset, pysäköintikiellot, hidastetöyssyt (OSM `traffic_calming`).

### D. Maasta nousevat esineet (instanssit, vain lähellä)
Rengasmainen virtautus kuten `032_heina.js` (kiinteä maailmanruudukko, ei uimista), etäisyysrajat 30/80/150 m:

| Esine | Sijoitus |
|---|---|
| heinä: 3–4 lajia, voikukat, apila, pitkä heinä reunoilla, nurmen kulumat polkujen kohdalla | luokkakartta: nurmi / reunat |
| pensaat ja pensasaidat | OSM `barrier=hedge`, `natural=scrub`, puistot |
| kukkapenkit ja istutuslaatikot | OSM, torit ja aukiot |
| aidat, kaiteet, pollarit, puomit | OSM `barrier=*` |
| lehtikarike ja oksat puiden alla | `trees.js` + vuodenaika (`aika/aika.js`) |
| kivet, lohkareet, sora reunoilla | luokkakartta (sora, metsänpohja) |
| sähkökaapit, palopostit, kyltit, roska-astiat, pyörätelineet | OSM `amenity`, `emergency=fire_hydrant`, `man_made=street_cabinet` |
| puiden juurikaivot ritilöineen | puurekisteri / katupuut |

Malleiksi omat proseduraaliset (Blender-skriptit, kuten `tools/juna/juna_sisa.py`) tai Meshy (kehotteet erikseen); kaikki matalapolygonisia ja instanssoituja.

### E. Vuodenaika (päätös omistajalle)
Kesä vai Porin marraskuu? Marraskuussa: ruskea/kellastunut nurmi, lehtikarike, märkä tumma asfaltti, kuura aamuisin. `aika/aika.js` voi vaihtaa materiaalin
sävyt ja esineet (lehdet, lumi myöhemmin). Ehdotus: aloitetaan **myöhäiskesä/alkusyksy** (vihreä nurmi, vähän lehtiä), lisätään vuodenajat myöhemmin.

## 4. Työvaiheet, arvio ja hyväksyntä

| Vaihe | Sisältö | Arvio | Valmis, kun |
|---|---|---|---|
| 0 | Testiradat: 20 vakiopistettä silmien korkeudella + autosta (keskusta, puisto, esikaupunki, parkkipaikka, asema), kuvat ennen/jälkeen (`tools/maa/kuvat.mjs`) | 2 h | kuvasarja syntyy yhdellä komennolla |
| 1 | Pikakorjaukset: ilmakuvan sävy offline (lumi pois), maan valaistus (Lambert + normaalikartta), pysäköintialueet `ROADCUT`:iin | 0,5–1 pv | vertailukuvissa ei valkoisia "lumiläiskiä" |
| 2 | Maankäyttökartta (A) + shaderi (B) 6 materiaalilla, etäisyysliuku | 2–3 pv | lähellä ei yhtään ilmakuvan autoa/varjoa; nurmi, asfaltti, kiveys tunnistettavat |
| 3 | Tien yksityiskohdat (C) | 1–2 pv | kaivot, urat, paikkaukset, reunat ulkoalueilla |
| 4 | Esineet (D) | 2–3 pv | 80 m säteellä aina jotain maasta nousevaa, FPS ennallaan |
| 5 | Vuodenaika (E), sää myöhemmin | 1 pv | omistajan valinta toteutettu |
| 6 | Suorituskyky ja puhelin: laatutasot, tekstuurikoot, instanssimäärät | 1 pv | puhelimella ≥ 30 FPS testiradalla |

Yhteensä noin 8–12 työpäivää keskustalle; koko pelialueelle +3–5 päivää (laajempi maankäyttökartta, ulkoalueen tiet ja reunat, enemmän esineitä
ja suorituskyvyn säätö isommalla alueella). Vaiheet 0–2 tuovat suurimman muutoksen (lumi ja vuoto pois).

## 5. Tiedostot ja rajapinnat (ehdotus)
- Uudet palat: `src/js/0315_maa_materiaali.js` (shaderi, korvaa `grassify`n lähietäisyydellä), `src/js/0325_maa_esineet.js` (instanssit);
  tai omat moduulit `maa/` (suositus: moduulikansio kuten `rata/`, ks. `src/README.md`).
- Data: `maa/peite_i_j.png` (luokkakartta 256 m laatoissa), `maa/tex/*` (PBR), `maa/esineet.json` (OSM-pisteet).
- Työkalut: `tools/maa/maapeite.py`, `tools/maa/orto_savy.py`, `tools/maa/esineet.py`, `tools/maa/kuvat.mjs`.
- Koordinaatit: pelin metrit (x itään, y pohjoiseen), three.js (x, z, −y); maan korkeus `TZg`, piirretty pinta `groundTop`.

## 6. Omistajan päätökset (21.11.2026)
1. **Vuodenaika: kesä.** Vihreä nurmi, kuiva asfaltti, ei lehtikariketta (paitsi vähän puiden alla). Vaihe 5 rajataan kesään; muut vuodenajat myöhemmin.
2. **Alue: koko aktiivinen pelialue** (omistaja 21.11.2026: "alue isommaksi, koko aktiivista pelialuetta koskevaksi"): ydinkeskusta, tarkkojen
   ilmakuvalaattojen alue (`033_ilmakuva_tarkka.js`: i −3…7, j −5…6, ~5,6 × 6 km), asema-alue, Porttaali, Kirjurinluoto, Tiilimäki–Isomäki, lentoasema ja
   sen tiet, tarinan paikat (`tarina/data/paikat.json`). Maankäyttökartta ja materiaali kattavat koko alueen; esineitä tiheimmin siellä, missä liikutaan
   jalan (keskusta, torit, rannat, puistot, asema, tarinan paikat), harvemmin esikaupungeissa ja teiden varsilla. Työjärjestys: keskusta → asema ja
   Porttaali → muu pelialue laatta kerrallaan (sama työkalu, ei erillistä vaihetta).
3. **Esineet Meshyllä.** Claude tekee mallit itse Meshyn verkkosivulla omistajan selaimessa (Clauden sisäänrakennettu selain työpöytäsovelluksessa tai
   Claude in Chrome), kun omistaja on kirjautunut Meshyyn siinä selaimessa. Claude ei syötä salasanoja eikä käytä API-avainta.
   - Ennen erää kysytään kerran: montako mallia (krediitit) ja lupa ladata GLB:t. Sen jälkeen Claude kirjoittaa kehotteet, odottaa, lataa,
     tarkistaa mallin (muoto, tekstuuri), harventaa, sijoittaa peliin ja ottaa testikuvat. Huono tulos → uusi versio ennen peliin vientiä.
   - Meshyn lähdemallit `maa/meshy/` (ei repoon, kuten `juna/meshy/`), pelimallit `maa/esineet/*.glb` (+ `_m` puhelimelle), instanssoituina.
   - Esinelista ja kehotteet: kirjoitetaan `tarvittavat_ominaisuudet/MESHY_PROMPTIT.md`:hen omaksi osiokseen ennen erää (penkki, roska-astia, pollari,
     palopostin, sähkökaappi, pyöräteline, kukkalaatikko, katupuun ritilä, kaivonkansi ja sadevesikaivo voidaan tehdä myös itse – ne ovat litteitä).
4. **Avoin data: saa käyttää, jos löytyy** (Porin kaupungin avoin data: puisto- ja katualueet, puurekisteri, katuvalot; MML maastotietokanta).
   Lisenssi ja lähdemerkintä tekijätietoihin (`src/html/01_runko.html` alalaidan teksti). Jos ei löydy, OSM + ilmakuvan luokittelu riittää.

## 7. Aloitus toisella tilillä (lue ensin)
1. Lue `src/README.md` (palat ja `kokoa.py`) ja tämän tiedoston osat 1–6. Uusi työ omaan moduulikansioon `maa/` + yksi kutsupala `src/js/`:hen.
2. Vaihe 0: testikuvat koko pelialueelta (30 pistettä, joista 20 keskustassa) (`tools/maa/kuvat.mjs`, Playwright; mallina `juna/test/shot.mjs`-tyyli: kamera kiinteään pisteeseen,
   korkeus `> 500` = absoluuttinen). Pisteet: Kauppatori, Yrjönkatu, Antinkatu, Eteläranta, Itäpuisto, Länsipuisto, Kauppahallin edusta, Isosilta,
   Satakunnankatu, Itsenäisyydenkatu, Valtakatu, parkkipaikka, Porin teatterin edusta, Raatihuoneen puisto, Kirjurinluodon silta;
   lisäksi asema-aukio, Porttaali, Tiilimäki, Isomäentie, Kirjurinluoto, Tapsan korjaamo, lentoaseman tie, Mäntyluodontie, Koillisväylä, Linnansilta.
3. Vaihe 1 (pikakorjaus) → näytä kuvat omistajalle → vaihe 2.
4. Muista: muut chatit muokkaavat samoja paloja (030, 031, 033, 060, 082, 090, 0301) – lue laitteelta juuri ennen muokkausta ja kirjoita heti.

## 8. Tila 21.11.2026 ilta: valmistelu ja työkalut tehty (vaiheet 0–2 data)
Kaikki työkalut ovat `tools/maa/` (ohje `tools/maa/README.md`). Peliin ei ole vielä kytketty mitään.
- **OSM-data koko pelialueelta**: `tools/maa/osm_maa.json` (10 326 viivaa/aluetta, 43 multipolygonia, 10 220 pistettä; haettu sovelluksen selaimella
  api.openstreetmap.org:sta 90 ruutuna). Sisältää tiet pintoineen, landuse/natural/leisure, pysäköinnit, aidat, pensasaidat, penkit, lamput, pysäkit, puut ym.
- **Maankäyttökartta valmis**: `maa/peite/peite_I_J.png` (132 laattaa à 512 m = samat kuin `ot/ot_I_J.jpg`, 0,5 m, 16 luokkaa, 3,9 Mt) + `maa/peite/peite.json`; yleiskuva `tools/maa/out/yleis.png`.
  Osuudet: jalkakäytävä/piha 33 %, nurmi 18 %, metsä 14 %, niitty 9 %, rakennus 7 %, ajorata 7 %, vesi 4 %, ei tietoa 4 % (vain alueen kulmat, joissa ei ilmakuvaa).
  Ydinkeskustassa roads.js voittaa OSM:n, joten rajat osuvat pelin reunakiviin.
- **Esineet**: `maa/esineet.json` – 38 pistetyyppiä (mm. 1145 katulamppua, 349 pysäkkiä, 1424 suojatietä, 11 708 sadevesikaivoa ja 4702 kaivonkantta
  säännöllä) ja viivat (aidat 40 km, pensasaidat 11,6 km, ojat, muurit). OSM:ssä vähän penkkejä (35) ja roska-astioita (19) → sääntösijoitus pelissä.
- **Tekstuurit**: `maa/tex/` 8 luokkaa valmiina (ajorata, pysäköinti, jalkakäytävä, betoni, kiveys, laatoitus, nurmi, multa), 1024 + 512 px (_m),
  ORM = AO/karheus/korkeus. **Puuttuu 5**: sora, hiekka, metsänpohja, niitty, puu → ambientCG-zipit `tex/`-kansioon (ks. README) – vaatii latausluvan.
- **Sävykorjaus**: `tools/maa/orto_savy.py` tekee `maa/ot_s/` (ei repoon ennen hyväksyntää); vertailu `python tools/maa/orto_savy.py --vertailu 2 3`.
- **Testikuvat (vaihe 0)**: `tools/maa/pisteet.json` (30 pistettä) + `node tools/maa/kuvat.mjs <tunniste> [url]`; "ennen"-sarja otettu:
  `tools/maa/kuvat/ennen/` (ei repoon).
Seuraavaksi (toinen tili): vaihe 1 (sävy käyttöön omistajan luvalla + Lambert-valaistus) ja vaihe 2: `maa/maa.js`-moduuli, joka lataa
`peite_i_j.png` + `maa/tex/*` ja korvaa 0–150 m maan materiaalin (031 grassify / 033 laatat) luokkapohjaisella PBR-sekoituksella.

## 9. Tila 21.11.2026 myöhäisilta: vaihe 1 käytössä, vaihe 2 ensimmäinen versio pelissä
- **Sävykorjaus käytössä** (omistaja: "uskon värikorjauksiin, ne voidaan toteuttaa"): `maa/ot_s/` (108 laattaa + orto.jpg + outer.jpg, `tools/maa/orto_savy.py`)
  on nyt pelin ilmakuva: 033 (laatat ja katot), 030 (outer.jpg), 130 (orto.jpg). Alkuperäiset `ot/`, `orto.jpg`, `outer.jpg` ennallaan (palautus = polut takaisin).
  `.gitignore`: `maa/ot_s/` poistettu ignoresta → menee repoon (~56 Mt).
- **`maa/maa.js` + kutsupala `src/js/0337_maa.js`** (`{ HR, renderer, isTouch }`): laajentaa 033:n tarkkojen ilmakuvalaattojen materiaalia (onBeforeCompile,
  033:a ei muutettu materiaalin osalta). Lataa laatan `maa/peite/peite_I_J.png` (palettikuva → R8-luokkatekstuuri selaimessa) ja `maa/tex/*` (8 kerrosta
  DataArrayTextureina; tietokone: albedo 1024, normaali+ORM 512; puhelin: kaikki `_m`, ei normaalikarttaa, ei toista näytettä).
  - 0–110 m materiaali, 110–150 m liuku ilmakuvaan (puhelin 60–90 m). Luokkaraja: 4 naapuritekseliä, kohinasiirto ±0,35 m, korkeussekoitus (ORM B).
  - Tiilauksen rikkominen: toinen näyte (0,857× + siirto) kohinamaskilla + makrokirkkausvaihtelu 11 m / 2,7 m.
  - Valo: aurinko (0.79, 0.81, 0.62) kuten 020, normaalikartta; tasainen maa = 1,0 (ilmakuva on valaisematon → sama taso). Yö tulee aika.js:n sävytyksestä.
  - 25–110 m: ilmakuvan sumea kirkkaus (mip 4,5) sävyttää ±20 %, jotta raja ilmakuvaan ei näy.
  - Luokat ilmakuva / vesi / rata → ilmakuva. Puuttuvat tekstuurit väliaikaisesti: sora = betoni lämmin, hiekka = jalkakäytävä sävytetty, metsä = multa,
    niitty = nurmi kellertävä, puu = laatoitus ruskea, rakennus = jalkakäytävä, urheilu = nurmi (`LUOKAT` maa.js:n alussa).
  - Vertailu pelissä: `window.__maa.pois()` / `.paalle()`, tila `window.__maa.tila()`.
  - Ei vielä: 0335:n Luvianpuistokadun käytävän 1 m täyte (näyttää ilmakuvaa), ulkokehä (18 m, alueen ulkopuolella), tien yksityiskohdat (vaihe 3), esineet (vaihe 4).
- **Testikuvat**: `tools/maa/kuvat/ennen/` ja `tools/maa/kuvat/jalkeen/` + `koonti_ennen_jalkeen.html` (otettu omistajan koneella sovelluksen selaimessa,
  localhost:8000, oikea näytönohjain). **Korjaus `kuvat.mjs`:ään**: kävelytilassa `WALK` palauttaa pelaajan paikan joka ruudulla → kävelijä siirretään pisteeseen
  ja pidetään siellä odotuksen ajan (muuten tarkat laatat eivät lataudu ja maa on karkeaa ilmakuvaa), kävelijähahmo piilotetaan kuvasta.
- Lisäksi 21.11. myöhemmin: `032_heina.js` vihreysraja 0.9/0.5 → 1.25/0.75 (sävykorjattu orto oli vihreämpi → tupsut katosivat); maa.js kattaa myös
  0335:n käytävän 1 m täytteen (ROOFT, `kaynnista_maa({ HR, ROOFT, renderer, isTouch })`); nurmen sävy 1.1/1.12/1.0.
- **Avoimet**: u03 Tiilimäki – iso sumea alue edelleen ilmakuvana (luokka tarkistamatta: ehkä vesi/ilmakuva/rata maapeitteessä, tai jokin muu verkko;
  tarkista `peite_1_0.png` px ≈ (60…140, 872)); u10 Linnansilta = sillan kansi (0301, ei maa.js:n alaa); heinätupsut ovat vaaleampia kuin uusi nurmi
  (032 värittää ilmakuvasta) → sävytä tupsut nurmitekstuurin mukaan; puhelimella ei vielä testattu; FPS ei mitattu.
- **Seuraavaksi**: (1) puuttuvat 5 ambientCG-tekstuuria (sora Gravel022, hiekka Ground033, metsä Ground026, niitty Grass001, puu Planks021) – **kysy
  latauslupa**, lataa `tex/`, aja `python tools/maa/tekstuurit.py`, lisää KERROKSET-listaan maa.js:ssä; (2) vaihe 3 tien yksityiskohdat (kaivot, urat,
  paikkaukset; esineet.json:n sadevesikaivot/kaivonkannet); (3) vaihe 4 esineet esineet.json:n mukaan + Meshy (kysy mallimäärä/krediitit ja GLB-latauslupa
  ennen erää); (4) OSM-lähdemerkintä `src/html/01_runko.html`:ään – maapeite (OSM-pohjainen) on nyt pelissä, joten "© OpenStreetMap contributors" pitää lisätä
  tekijätietoihin (EI vielä tehty).

## 10. Tila 21.11.2026 klo 22: tekstuurit valmiit, vaihe 3 alku pelissä
- Osa 9:n avoimet: **u03 Tiilimäki korjattu** (ulkokehä peitti tarkan laatan koverassa maastossa → 030/031/033 `OUTER_HR`); **heinätupsut** nurmen sävyyn (032);
  **OSM-lähdemerkintä** tekijätiedoissa (01_runko.html). u10 Linnansilta (sillan kansi) ja puhelin/FPS edelleen tarkistamatta.
- **Kaikki 13 tekstuuria** `maa/tex/` (uudet: sora, hiekka, metsä, niitty, puu) ja maa.js käyttää niitä (ei enää korvikkeita). Metsänpohja (Ground026) on tasainen tumma maa:
  vaihtoehto havu-/lehtikarike myöhemmin.
- **Vaihe 3 (osa C) aloitettu**: `maa/tie.js` (+ `src/js/0826_tie_yksityiskohdat.js`): kaivonkannet, sadevesikaivot reunakiven vieressä, asfalttipaikkaukset.
  Vielä tekemättä vaiheesta 3: pyörän urat ja asfalttisävyt (060:n `surf`-shaderiin), kulunut tiemaalaus, ulkoalueen sorapiennar/ojat, pysäköintiruudut, hidastetöyssyt (esineet.json `toyssy`, `korotettu`).
- **Seuraavaksi**: loput vaiheesta 3 → vaihe 4 esineet (esineet.json + Meshy; kysy mallimäärä/krediitit ja GLB-latauslupa ennen erää).
