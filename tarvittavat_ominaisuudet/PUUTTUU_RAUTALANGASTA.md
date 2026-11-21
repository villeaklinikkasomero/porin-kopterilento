# Mitä tarinasta puuttuu – rautalangan jälkeen (21.11.2026)

Koko tarina **M01–M26** on nyt pelissä rautalankana (`tarina/data/tehtavat/`). Mukana ovat myös kaupat, korjaamo, tuunaus ja mikrotehtävät.
Kaiken voi pelata läpi alusta kaikkiin kolmeen loppuun: puuttuva mekaniikka näkyy ruudulla tekstinä "[Tulossa: …]" ja ohitetaan 3 sekunnissa.
Testit: `node tarina/testi.mjs`. Automaattipelaaja pelaa koko tarinan läpi kolmella eri lopulla, ja lisäksi testataan ruoka, nälkä, korjaus, tuunaus ja mikrotehtävät.

Tämä lista on koottu tehtävädatasta. Kun mekaniikka valmistuu, lisää käsittelijä `tarina/peli.js`:n `KASITTELIJAT`-olioon samalla nimellä (ohje: `tarina/README.md`).

## 1. Mekaniikat (toiminto-vaiheet, joilla ei vielä ole käsittelijää)

Järjestetty sen mukaan, kuinka moni tehtävä hyötyy ja kuinka aikaisin ne tulevat vastaan.

| Prioriteetti | Toiminto | Tehtävät | Mitä tarvitaan |
|---|---|---|---|
| **1** | Varjo-mittarin jahti (`varjo_mittari` näyttää nyt vain tähdet) + `karista_jahtaajat` | M03, M13, M18, M26 | Vartijabotit ja uutiskopteri jahtaavat; tähdet laskevat katveessa/sillan alla; kiinni jäänti = FAIL "Ammattilaisia ei jää kiinni". PEGI 7: ei vahinkoa, vain kiinniotto. |
| **1** | `hiiviskely` | M03, M22 (+ M13, M14, M17 käyttävät samaa) | Näkökartiot (vartija, myyjä), kyykky/hidas kävely, huomattu-mittari, laserit (M22). |
| **2** | `vene` + `veneen_takaa_ajo` + `soutukilpa` | M19, M26 | Vene on pelissä (vene.js, perämoottori). Tarvitaan kulku `vene` moottoriin (`maailma()` peli.js:ssä), veneeseen nousu tarinasta ja Varjon veneen botti joella. |
| **2** | `anna_kopteri` | M16, M20 | Kopteri siirretään annettuun paikkaan, ja pelaaja nousee siihen (kuten `__take.give` autoille). |
| **2** | `torni_sisatila`, `torni_kerros20`, `kassakaappi` | M13, M17, M21, M24 | Varjo-tornin sisätila (näyttelykerros, 12. krs palvelinsali, 20. krs toimisto, kattoravintola) – sisätilajärjestelmä on jo olemassa (kirkko, teatteri, kauppahalli). |
| **2** | `hakkerointi`, `holvi_rytmipeli`, `tiirikka`, `kassakaappi` | M14, M23, M24 | Minipelit (johtojen yhdistäminen, rytmi, tiirikka, kolmivaiheinen kassakaappi). Yksi yhteinen minipelikehys riittää. |
| **3** | `vesiletku` | M04 | Vesisuihku, vartija liukastuu ja pakenee, tarran repiminen. |
| **3** | `drooni` | M05 | Drooni kulkuneuvona (kameranäkymä, akku 90 s, valokuvaus). |
| **3** | `juna_rinnalla`, `nappaa_kansio` | M07 | Juna on pelissä (juna/). Tarvitaan junan aikataulu tehtävään, huoltotie radan vieressä ja etäisyysmittari. |
| **3** | `salakuuntelu` | M09 | Kuuloetäisyysmittari, Varjo kävelee salissa reittiä (moottorin `seuraa`-vaihe käy pohjaksi). |
| **3** | `seuraa_konetta`, `hyppy_kiitotielle` | M20 | AI-lentokone kiitotiellä ja ilmassa; hyppy kopterista laskuvarjolla (laskuvarjo/hyppy.js on olemassa); kiitotiemerkki. |
| **3** | `magneetti` | M15 | Hinausauto + panssariauto, magneetin kiinnitys, hinaus. |
| **3** | `vaijeri` | M16 | Kopterin vaijeri, kontti roikkuu (fysiikka), tuuli ja nosturit esteinä. |
| **3** | `lentoreppu` | M22, M23 | Uusi liikkumistapa (lentoreppu). |
| **4** | `rc_lentokone`, `rc_auto` | M10, M23 | Kauko-ohjattavat pienoislaitteet (kamera seuraa laitetta). |
| **4** | `paintball` | M12 | Oma pelimuoto: väripistooli, lipunryöstö, joukkuebotit, 3 erää. |
| **4** | `moottoripyora` | M13 | Moottoripyörä kulkuneuvona (malli + ajo). |
| **4** | `saippuakupla`, `savuverhot`, `naamioituminen`, `pyykkikuilu`, `laskuvarjo_katolta`, `katkaise_sahkot`, `torilaiset_harhauttavat` | M13, M14, M17, M23, M24 | Tehtäväkohtaiset efektit ja välianimaatiot. |

**Kilpailijat ja reitit:** M11 Sillankilpa ja M02 Kespan lenkki käyttävät ajastinta. Oikea kilpa-auto radalla (bottikuski reittiä pitkin) puuttuu. M15 panssariauto näkyy nyt vain merkkinä.

## 2. Talous (tehty rautalankana) – mitä vielä puuttuu

Tehty (`tarina/talous.js` + `K_*`-tehtävät):
- **Energia** 0–100 laskee pelatessa (jalan ×1,5, pyörällä ×1,8). Varoitukset 30 ja 10. Nollassa uudet keikat eivät ala, mutta kaupat ja korjaamo toimivat.
- **Ruoka:** Grilli-Pori (porilainen 8 €, lihapiirakka 6 €, ranskalaiset 3 €) ja Rattis (wingsit 12 €, wings-kori 16 €, kahvi ja munkki 4 €).
- **Korjaus** Tapsan hallissa: Tapsa veloittaa vain osat (10/25/45 € vaurion mukaan). Auto ei korjaannu muualla.
- **Tuunaus:**
  - Osat ostetaan Satakunnan Varaosasta (60–280 €) ja noudetaan Tapsan pakulla lastauslaiturilta.
  - Asennus tehdään hallissa Ramin farmariin.
  - Maalaus ja moottorin viritys vaikuttavat jo ajoon ja ulkonäköön.
- **Mikrotehtävät** (12–30 €):
  - Tertun kukkalähetys pyörällä, Rattiksen siipilähetti, Grilli-Porin yölähetti
  - asiakkaan auto korjaamolle, rengaskuljetus pakulla
  - liikennekuvaus kopterilla Radio Kirjurille
  - Lisäksi pelin omat kyydit tuovat rahaa (enintään 10 €/km).

Puuttuu:
- **Osamallit:** vanteet, spoileri, pakoputki ja lisävalot asennetaan jo, mutta ne eivät näy, ennen kuin mallit valmistuvat (`tuunaus_mallipyynto.md`).
- **Tuunaus koskee nyt mitä tahansa farmaria,** jolla pelaaja ajaa. Tarvitaan "Ramin farmari" omana pysyvänä autonaan: tallennus, paikka korjaamon pihalla ja kutsuminen.
- **Tapsan paku** ilmestyy pihalle vasta, kun noutotehtävä alkaa. Pysyvä pysäköity paku pihalla puuttuu.
- **Energian vaikutus pelaamiseen:** nyt nälkä vain estää keikat. Esimerkiksi juoksun estäminen tai hitaampi pyöräily matalalla energialla puuttuu.
- **Kauppojen aukioloajat** (Rattis 11–22/24, Grilli-Pori yöhön) ja pelin kellonaika puuttuvat.
- **Tasapaino:** palkkiot ja hinnat ovat arvioita, ja ne pitää testata pelaamalla.
- **Keräiltävät:** 50 lokkipatsasta (`SYS_COLLECTIBLE`) ja "tiesitkö"-faktat puuttuvat.

## 3. Kuvitus ja mallit

### Hahmot
| Hahmo | Tilanne |
|---|---|
| Tapsa, Lumi, Terttu, Harju, Varjo, vartija (3 muunnelmaa), myyjä, kuriiri | Mallit valmiina (`npc_*.js`) |
| **Grilli-Porin myyjä** (GRILLI) | puuttuu – nyt vain tekstinä |
| **Rattiksen baarimikko** (BAARIMIKKO) | puuttuu |
| **Kake, Satakunnan Varaosan myyjä** (VARAOSAMYYJA) | puuttuu |
| **Radio Kirjurin juontaja** (RADIO) | ääni riittää; kasvokuva viestipaneeliin, jos UI-konsepti tarvitsee |
| Liittolaiset M19: kalastaja, koiranomistaja + koira, soutaja | puuttuvat |
| Asut: Varjo ja Harju juhla-asussa (M09), Ramin hotelliasu (M14), tuholaistorjujan haalari (M13) | puuttuvat |

### Paikat ja rakennukset
| Paikka | Tarvitaan |
|---|---|
| Grilli-Pori (Juhana Herttuan katu 19) | grillikioskin luukku/kyltti; paikka mitattava (nyt arvio) |
| Rattis (Yrjönkatu 27) | kyltti ja ovi; sisätila (valinnainen); oven paikka mitattava |
| Satakunnan Varaosa (keksitty, Äestäjänkatu) | liikerakennus + lastauslaituri korjaamon lähelle |
| Lumin piilo (vanha tiilivarasto) | rakennus + sisätila (briefing-valkotaulu) |
| Varjo-torni (keksitty) | korkea torni + työmaa, sisätilat (ks. mekaniikat) |
| Hotelli Varjo (keksitty) | aula, holvi, pyykkiovi |
| Varjon varasto / satamakontit | kontit, kellari, kattoikkuna |
| Autoliike Kiilto | piha, toimisto |
| Tuholaistorjuja Ötökkä-Oy (keksitty) | piha + paku |
| Kirjurinluoto | jazzlava ja juhlan iso näyttö (loppu B) |
| Lentoasema | huoltohalli ja Varjon yksityiskone |

**Mitattavat paikat** (`"tarkista": true` tiedostossa `paikat.json`): mittaa kehittäjätilassa, ensin Ctrl+Shift+D ja sitten Ctrl+Shift+K. Listalla ovat Pohjoisranta, Kirjurinluoto, asema, lentoasema, Rattis + ovi, Grilli-Pori, varaosaliike + laituri, hotelli, varasto, tuholaistorjuja, museon takaovi, lentoaseman halli, piilo, Varjo-torni ja Kiilto.

### Kulkuneuvot ja esineet
- **Kulkuneuvot:** moottoripyörä, hinausauto, panssariauto, Varjon yksityisvene, Varjon yksityiskone (AI), RC-lentokone, RC-auto, drooni, lentoreppu, Tertun miehen vanha vene.
- **Esineet maailmassa:**
  - jokaiselle `keraa`-kohteelle näkyvä esine: hakemukset, frakki, siipilaatikot, kukat, korut, kulkukortti, salkku, veneen osat
  - Varjon kauppakirjakansio, purkutarra, kontti

### Välianimaatiot
- Kamera-ajot välianimaatioille: CUT_M01_B, CUT_CH3_A, CUT_M09_A, CUT_M14_A, CUT_M18_A, CUT_M24_A, CUT_M25_A, CUT_M26_A ja loput END_A/B/C. Nyt kohtaukset ovat repliikkejä ruudulla, ja kamera on vain M01:ssä.
- Toimintarivit (KERTOJA) kertovat, mitä kohtauksessa tapahtuu: ne ovat käsikirjoituksen hakasulkuohjeita ja korvautuvat animaatioilla.

## 4. Käyttöliittymä (toisessa langassa konseptoitava)

Rautalanka käyttää nykyistä `tarina/ui.js`:ää. Uudet, tarkoituksella pelkistetyt osat:
- **`#tr-energia`** (talous.js): energiapalkki ruudun yläreunassa.
- **Kauppojen valikot:** tavallinen valinta-paneeli. Näppäimet 1–9; hinta näkyy tekstissä, ja jos rahat eivät riitä, tulee vihje.
- **Karttamerkkien lajit:** tarina (`tehtava`), kaupat (`kauppa`: 🍔 🍗 ⚙), korjaamo (`korjaamo`: 🔧 🚐) ja mikrotehtävät (`sivu`: €). Merkit piirtyvät nyt samannäköisinä, ja UI-konsepti päättää niiden ulkoasun.
- **Valikon laskuri** "x/y keikkaa" laskee nyt mukaan myös toistuvat tehtävät. Tarina ja sivutehtävät kannattaa erottaa.
- **Puuttuu:** inventaario (esineet, osat), tuunausvalikko (asennettujen osien vaihto ja poisto), kartta-/puhelinnäkymä mikrotehtävien listalle.
