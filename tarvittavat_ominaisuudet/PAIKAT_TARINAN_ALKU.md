# Tarinan alun paikat ja sisätilat (luku 1 + ensimmäiset kaupat ja keikat)

Kirjoitettu 21.11.2026. Omistaja: *"mieti, mitä paikkoja pitää tarinan alkuun rakentaa. Olisi hyvä, että jos käydään jostakin talosta hakemassa asioita, pääsisi sisälle,
eikä että menee vain talon viereen. Realistisuutta tähän."*

**Päätetty 21.11.2026 (omistaja):** 1) ravintoloille omat keksityt nimet, 2) teollisuusalueen hallit käyvät, ja niihin tehdään Meshyllä uusi julkisivu,
3) Lumin piilo Isosantaan (ei Kirjurinluodolle), 4) M01:ssä perunat ja sipulit. Tehty dataan: ks. kohta 5.

Pohjana: tarina M01–M06 + kaupat ja mikrotehtävät (`tarina/data/tehtavat/`), pelin sisätilajärjestelmä (`src/js/121_jalan.js` PLACES), Tapsan korjaamo
(`korjaamo/`), IC-junan sisätila (`juna/`), korjaamon laajennussuunnitelma (`tarina/SUUNNITELMA_VIIKKOTARINAT_JA_KORJAAMO.md`) ja pelin kello (`aika/`).

## 1. Periaate

**Jos tehtävässä haetaan tai viedään jotain rakennuksesta, mennään sisään.** Tavara on oikea esine oikeassa paikassa (laatikko keittiön lattialla, avaimet
kaapissa), ja sen luovuttaa tai vastaanottaa ihminen. Ulos jää vain se, mikä on oikeastikin ulkona: torikoju, laituri, piha, kilparata.

Lisäksi:
- **Oikea sisäänkäynti.** Tavarat kulkevat takaovesta, keittiön ovesta tai lastauslaiturilta, asiakkaat etuovesta. Lähettinä Rami menee keittiön ovelle, ei ruokasaliin.
- **Aukioloajat** pelin kellon mukaan (`window.__aika`). Vauhtis aukeaa klo 11, ja Kaksi Siivua on auki myöhään. Suljettuun paikkaan ei pääse, ja tehtävä sanoo sen.
- **Mittasuhteet oikeiksi.** Huoneet mitataan oikeista kokoluokista (ravintolasali, kioski, autoliikkeen näyttelytila), ei ylisuuriksi pelihalleiksi.
- **Oikeat paikat oikeisiin taloihin.** Keksitty liike laitetaan olemassa olevaan, tyypiltään sopivaan rakennukseen (autoliike matalaan halliin, ei kerrostaloon).

## 2. Kaksi tapaa tehdä sisätila (molemmat ovat jo pelissä)

| Tapa | Miten toimii | Pelissä nyt | Sopii |
|---|---|---|---|
| **A. Ovi + oma sisätila** | Ovi julkisivussa → häivytys → erillinen sisäscene (`*_sisa.js`) → ulos samasta ovesta. Sisäovet (`ports`) siirtävät huoneesta toiseen. | kirkko, mausoleumi, teatteri, taidemuseo, jäähalli, kauppahalli | Kortteleiden liiketilat: Vauhtis, Kaksi Siivua, varaosaliike, autoliikkeen myymälä |
| **B. Kävelykuori maailmassa** | Rakennus on avoin malli kartalla; sisään kävellään tai ajetaan ilman häivytystä, seinät ovat kiinteitä laatikoita. | Tapsan korjaamo, IC-junan vaunut | Erilliset rakennukset, joihin ajetaan autolla tai joihin näkee ikkunoista: korjaamo, Lumin piilo |

**Puuttuu tarinamoottorista** (sama työ kaikille paikoille, tehdään kerran):
- Tarina tietää nyt vain, että pelaaja on *jossain* sisällä (`sisalla: true`), ei *missä*. Tarvitaan `sisa: 'rattis'` ja sisäkoordinaatit (`WALK.ix, WALK.iy`) tarinan
  maailmatietoon. Silloin paikka voi olla myös muotoa `{ "sisa": "rattis", "x": 4.2, "y": -1.5 }`, jolloin `mene`- ja `keraa`-vaiheet toimivat sisällä.
- Hahmot ja esineet sisätiloihin (`hahmot.js` sijoittaa nyt vain kartalle).
- **Kantaminen:** laatikko käsissä tai pyörän tarakalla näkyvänä. Ensimmäinen versio voi olla pelkkä esine kädessä, ja kantaminen hidastaa kävelyä vähän.

## 3. Paikat tärkeysjärjestyksessä

### 1. Ravintola Vauhtipyörä ("Vauhtis", keksitty) – tapa A
- **Missä:** rakennus b109 Yrjönkadun ja Rautatienpuistokadun kulmassa (1926, 4 krs), katutaso. Nimi, kyltti ja sisustus ovat omia (`LOC_VAUHTIS`, `LOC_VAUHTIS_OVI` – ovi mitataan pelissä).
- **Tehtävät:** M01 (perunat ja sipulit keittiöön), K_VAUHTIS (syöminen), S_SIIVET (lähettikeikat), myöhemmin viikkotarinat.
- **Sisällä:**
  - sali, jossa baaritiski, jukeboksi, pöydät ja seinillä Porin rock-historiaa
  - pieni keittiö: rasvakeitin, kylmiö, takaovi pihalle
  - asiakas-WC:n ovi (kiinni)
  - kesäterassi ulkona
  - rosoinen ja mutkaton porilainen rock-baari, oma keksitty sisustus
- **Ihmiset:** baarimikko (myynti) ja kokki (ottaa toimitukset keittiön ovella). Iltaisin muutama kävelijähahmo asiakkaina.
- **Ovet:** etuovi Yrjönkadulta (syöminen) ja keittiön takaovi sisäpihalta (toimitukset, lähettikeikat).
- **Kello:** auki 11–22, pe–la 24. Suljettuna etuovi on lukossa ja keittiön ovi aamuisin auki (toimitukset tulevat aamulla).
- **Koko:** sali noin 12 × 9 m, keittiö 5 × 4 m.

### 2. Tapsan korjaamo – tapa B (on jo, täydennetään)
- **Tehtävät:** M01 (Ramin auto), M02, M03, M04, M05 sekä korjaus ja tuunaus. Pelin tukikohta.
- **Lisätään:**
  - **Ramin vanha farmari hallissa pressun alla.** M01:n lopussa Tapsa vetää pressun pois, ja auto annetaan hallin sisällä, ei pihalla. Realistisempi ja hienompi hetki.
  - **Toimisto ja taukotila** hallin nurkkaan (laajennussuunnitelman päivitys 9): pöytä, kahvinkeitin, puhelin, seinäkalenteri, ilmoitustaulu (📋 = korjaamon päivitykset ja keikat).
  - **M05:n paketti** ovensuuhun oikeana laatikkona, ja drooni puretaan laatikosta.
- **Puutteet:** katto ei ole kiinteä, valot eivät valaise, ja kävelijät eivät tunne hallia (`korjaamo/README.md`).

### 3. Lumin piilo: Isosannan vanha sähköasema – tapa B
- **Missä (omistaja: Isosanta):** Isosannan sähköasema (1939, punatiilinen funktionalistinen rakennus, Y-pakki), pelin rakennus b1307, 28 × 37 m, [-80, 932]. Se on noin 270 m aloituspaikalta pohjoiseen.
  Käytöstä poistunut sähköasema sopii hakkerin piiloksi: korkea halli, kaapelihyllyt, vanhat kojetaulut. `LOC_PIILO` [-80, 903] on eteläpääty (arvio), ja ovi mitataan pelissä.
  Vaihtoehto, jos sähköasema ei sovi: Valajankatu 4 (1922, tiili, 18 × 12 m) noin 100 m Pohjoisrannasta.
  Sähköasema on suojeltu rakennus, joten sen ulkoasuun ei kosketa. Piilo on sisällä.
- **Tehtävät:** M06 ja lähes jokaisen myöhemmän tehtävän briefing (luvut 3–5).
- **Sisällä:**
  - korkea muuntamohalli, vanhat kojetaulut ja kaapelihyllyt
  - Lumin näytöt, valkotaulu, jonka kuvat ja kartat muuttuvat luku luvulta
  - sohva, työpenkki, droonin laskeutumisluukku katossa
- **Miksi tapa B:** piiloon tullaan myöhemmin kopterilla (M16:n kontti) ja korkeista ikkunoista näkee ulos. Vene (luku 4) rantautuu Pohjoisrannan laituriin, josta kävellään piiloon.

### 4. Autoliike Kiilto – tapa A (myymälä) + piha
- **Missä (päätetty):** teollisuusalueen halli b557 Tapsan korjaamon naapurissa (`LOC_KIILTO` [-550, -427], ovi arvio). Halliin tehdään Meshyllä uusi julkisivu:
  näyttelyikkunat, kyltti ja liput. Korjaamo, varaosaliike ja autoliike ovat nyt samassa korttelissa, ja naapuruus sopii tarinaan (Kiilto vie Tapsan asiakkaat).
- **Tehtävät:** M03 (Takaisinhaku: hiivitään myyjän ohi ja otetaan avaimet toimistosta, sitten ajetaan Tapsan autot pihalta).
- **Sisällä:**
  - lasiseinäinen näyttelytila, jossa 2–3 autoa
  - myyjän pöytä
  - toimisto, jossa avainkaappi (tavara, joka haetaan)
  - kahviautomaatti
- **Ulkona:** aidattu myyntipiha hintalappuineen, ja siellä Tapsan "takavarikoidut" autot.
- **Ihmiset:** myyjä (`npc_myyja.js` valmiina). Hiiviskelyn näkökartio tarvitsee sisätilan, jotta tehtävä on mielekäs.

### 5. Satakunnan Varaosa – tapa A + lastauslaituri ulkona
- **Missä (päätetty):** halli b558 (90 m pitkä, 16 m korkea) korjaamolta itään, uusi julkisivu Meshyllä. `LOC_VARAOSALIIKE` [-490, -441] on myymälän ovi pohjoisseinällä ja `LOC_VARAOSA_LAITURI` [-490, -468] eteläseinän laituri (arviot).
- **Tehtävät:** K_OSAT (osto), K_NOUTO (nouto pakulla laiturilta), S_RENKAAT. Myöhemmin myös korjaamon remonttitarvikkeet (laajennussuunnitelma B3).
- **Sisällä:**
  - myyntitiski ja kassa, tilauskone
  - hyllyrivit (öljyt, suodattimet, vanteet), rengasteline
  - takana varasto, jossa tilatut laatikot
- **Ulkona:** lastauslaituri ja rullaovi talon takana. Paku peruutetaan laituriin, ja laatikko nostetaan kyytiin (lyhyt animaatio).
- **Ihmiset:** Kake (VARAOSAMYYJA, tarvitsee mallin).

### 6. Grilli Kaksi Siivua (keksitty) – tapa A, pieni
- **Missä:** yksikerroksinen rakennus b917 (25 × 9 m) Juhana Herttuan kadulla, kokoluokka sopii grilliin. Nimi on keksitty, ja Radio Porikopterilla on jo mainos ("Kaksi Siivua"). `LOC_GRILLI` [463, -273], mittaa ovi pelissä.
- **Tehtävät:** K_GRILLI (syöminen), S_GRILLI (yölähetti).
- **Sisällä:** tiski ja grilli, muutama pöytä ja baarituoli ikkunan vieressä, sekä hintataulu, jossa porilainen. Iltaisin ikkunassa haalea valo (`aika/`).
- **Kello:** auki pitkälle yöhön. Yölähetti toimii vain illalla.

### 7. Tertun torikoju – ulkona (riittää)
- Koju on oikeasti ulkona. Lisätään kojuun laatikot, joista tavara otetaan: oikea esine pöydän takana ja Terttu ojentaa sen.
- **M01 (tehty):** Vauhtis tilaa torilta perunat ja sipulit keittiöönsä, ja Rami vie ne pyörän tarakalla keittiön ovelle. Siellä kokki ottaa ne vastaan.

### 8. Vanha raatihuone – myöhemmin (tapa A, yksi sali)
- **Tehtävät:** S_KUKAT (hääkukat), M08 (hakemukset viedään kaupungintalolle, joka on eri talo: Junneliuksen palatsi).
- Ensin riittää, että kukat viedään ovella odottavalle hääkoordinaattorille. Juhlasali tehdään, kun tarinan kaupungintalo- ja raatihuonekohtaukset tulevat (luku 2).

### Jo valmiina sisältä, käytetään hyväksi
- **Porin teatteri:** S_GRILLI viedään teatterin takaovelle → kahvilaan (sisätila on jo). M09 ja M14 hakevat asuja puvustamosta, joka pitää lisätä sisäovien taakse.
- **Kauppahalli:** sopii myöhemmin ruokapaikaksi ja juoruille.

## 4. Mitä tarvitaan, jotta tarinan alku (M01–M06) on "sisältä"

| # | Työ | Kuka | Koko |
|---|---|---|---|
| 1 | Tarinamoottori: `sisa`-paikat, sisäkoordinaatit, hahmot ja esineet sisätiloihin, ovien aukiolot kellosta | koodi | 1–2 istuntoa |
| 2 | **Vauhtis**: sali + keittiö (tapa A), etu- ja takaovi, baarimikko ja kokki | malli + koodi | 2 istuntoa + mallit |
| 3 | **Korjaamo**: pressun alla oleva farmari (M01-kohtaus), toimistonurkkaus ja ilmoitustaulu | koodi + 2 Meshy-kalustetta | 1 istunto |
| 4 | **Lumin piilo**: kuori + sisustus (tapa B), b1534 tarkistus | malli + koodi | 2 istuntoa |
| 5 | **Autoliike Kiilto**: siirto oikeaan taloon, myymälä + toimisto (tapa A), piha | malli + koodi | 2 istuntoa |
| 6 | **Satakunnan Varaosa**: myymälä (tapa A) + lastauslaituri | malli + koodi | 1–2 istuntoa |
| 7 | **Kaksi Siivua**: pieni sali (tapa A) | malli + koodi | 1 istunto |
| 8 | Kantaminen (esine kädessä, tarakalla) | koodi | 1 istunto |
| 9 | M01:n tavara → perunat ja sipulit; auto pressun alta | data | pieni |

Järjestys: 1 → 2 + 9 (M01 kokonaan "sisältä") → 3 → 6 → 7 → 4 → 5.

**Mallien tekotapa:** huoneet tehdään oikeilla mitoilla koodissa tai Blenderissä samalla tavalla kuin junan sisätila (`tools/juna/juna_sisa.py`: lattia, seinät, ovet, kävelyalueet `sisa.json`),
ja kalusteet tulevat Meshystä (tiski, rasvakeitin, hyllyt, kahviautomaatti, avainkaappi, sohva, valkotaulu) `korjaamo/README.md`:n ohjeella.

## 5. Tehty 21.11.2026 päätösten jälkeen (data)

- Nimet: Rattis → **Ravintola Vauhtipyörä / Vauhtis** (`LOC_VAUHTIS`, `LOC_VAUHTIS_OVI`, `K_VAUHTIS`), Grilli-Pori → **Grilli Kaksi Siivua** (`LOC_GRILLI`, `K_GRILLI`, `S_GRILLI`).
  Uusi tekstihahmo KOKKI.
- **M01:** perunat ja sipulit (`ITEM_PERUNAT`), kokki ottaa ne vastaan keittiön ovella, ja korjaamon pihalla Tapsa vetää pressun Ramin farmarin päältä.
- **Paikat:** Kiilto → halli b557, Satakunnan Varaosa → halli b558 (ovi + laituri), Lumin piilo → Isosannan sähköasema b1307. Kaikki ovet ovat arvioita (`tarkista`).
- Testit `node tarina/testi.mjs` 23/23 (koko tarina läpi kolmella lopulla).

## 6. Teatterin näyttelijät (omistaja tekee hahmoja)

Teatterin sisätila (aula, päänäyttämö, kahvila) on jo pelissä. Näyttelijät tekevät siitä elävän ja sopivat tarinaan näin:

| Missä | Mitä näyttelijät tekevät |
|---|---|
| **Teatteri elää kellon mukaan** | Iltaisin klo 19–21 (pelin kello) esitys: näyttelijät lavalla puvuissa, yleisöä katsomossa, aulassa väliaikakahvit. Päivällä harjoitukset arkivaatteissa. Yöllä tyhjää. |
| **M09 Gaala-ilta** | Puvustaja antaa Ramille frakin puvustamossa (uusi huone sisäovien taakse) ja neuvoo, miten "näytellään rikasta". Yksi näyttelijä on gaalassa tarjoilijana ja auttaa salakuuntelussa. |
| **M14 Hotelli-ilta** | Hotellin henkilökunnan asut lainataan teatterilta. Näyttelijä harhauttaa aulassa vastaanottovirkailijaa ("kadonnut matkalaukku" -kohtaus). |
| **M24 Iso keikka** | Näyttelijät liittyvät torilaisten harhautukseen: katuteatteriesitys tornin edessä (kasvattaa harhautuksen kestoa kuten liittolaiset). |
| **Mikrotehtävät** | *Myöhästyvä näyttelijä*: kyyti esitykseen ennen klo 19 (aikaraja pelin kellosta). *Rekvisiittakeikka*: laatikko Satakunnan Varaosasta tai kauppahallista teatterin takaovelle pakulla. *Ensi-illan kukat*: Tertulta lavan taakse. *Kaksi Siivun yölähetti* (S_GRILLI) viedään kahvilaan, jossa näyttelijät syövät. |
| **Kaupunki** | Pari näyttelijää kävelee puvuissa teatterin ympäristössä ennen esitystä. Esitysilloista kuulutetaan radiossa. |
| **Viikkotarinat** | Teatterin ensi-illat ovat valmiita, hyväntuulisia aiheita (suunnitelma A2). |

Tekninen tarve: hahmot sisätiloihin (kohta 2) ja hahmojen näkyminen kellonajan mukaan (`maailma.json`-sijoitukseen ehto `kello: [19, 21]`).
Tarvitsen hahmoista nimet ja roolit (esim. ohjaaja, pääosan näyttelijä, puvustaja, näyttämömestari), jotta repliikit ja tehtävät saa kirjoitettua.

## 7. Meshy-pyynnöt tarinan alkuun

Origin = Bottom, koko metreinä, 10–20 k kolmiota (ohje: `korjaamo/README.md`).

| Malli | Koko (l × s × k) | Käyttö |
|---|---|---|
| Autoliikkeen julkisivu: lasiseinäinen näyttelytila, kyltti "Kiilto", liput | sovitetaan hallin b557 pohjoisseinään (noin 40 m leveä, 10 m) | Kiilto |
| Varaosaliikkeen julkisivu: myymälän ovi, ikkunat, kyltti, rullaovi + lastauslaituri | hallin b558 pohjois- ja eteläseinä (noin 90 m, 16 m) | Satakunnan Varaosa |
| Baaritiski + hanat + jukeboksi | 4,0 × 0,8 × 1,1 m; 0,9 × 0,6 × 1,6 m | Vauhtis |
| Ravintolan pöytä ja tuolit, baarijakkara | 1,2 × 0,8 × 0,75 m | Vauhtis, grilli |
| Rasvakeitin + teräspöytä + kylmiön ovi | 0,6 × 0,7 × 0,9 m; 1,6 × 0,7 × 0,9 m; 1,0 × 0,2 × 2,1 m | Vauhtiksen keittiö |
| Grillitiski ja hintataulu | 3,0 × 0,8 × 1,1 m | Kaksi Siivua |
| Myyntitiski ja kassa, hyllyrivi autotarvikkeille, rengasteline | 3,0 × 0,8 × 1,0 m; 4,0 × 0,6 × 2,2 m | Satakunnan Varaosa |
| Myyjän pöytä, avainkaappi seinällä, kahviautomaatti | 1,6 × 0,8 × 0,75 m; 0,6 × 0,15 × 0,8 m | Kiilto |
| Vanha sähkökojetaulu, kaapelihylly, valkotaulu jalustalla, nuhjuinen sohva | 3,0 × 0,6 × 2,2 m jne. | Lumin piilo |
| Perunasäkki + sipulilaatikko (kannettava) | 0,5 × 0,3 × 0,7 m | M01 |
| Pressu auton päällä (tai tehdään koodissa) | auton kokoinen | M01 |

## 8. Seuraavat askeleet (yhdistetty UI-konseptin kanssa, ks. `UI_KONSEPTI_PELIIN.md`)

1. **Mittaukset pelissä (sinä, 15 min, voi tehdä heti):** ovet Ctrl+Shift+D → Ctrl+Shift+K -kopioinnilla.
   Paikat: Vauhtiksen etu- ja keittiön ovi, Kaksi Siivun ovi, Kiillon ja Satakunnan Varaosan ovet, varaosaliikkeen laituri, sähköaseman ovi.
2. **UI-pohja (minä):** fontit (Nunito, Fredoka), HUD-lasi ja glyfi-ikonit.
3. **Aloitussivu tarinalle (minä):** ei ajoneuvovalintaa, *Aloita / Jatka tarinaa*, päivän kierros lukossa kopteriin (M16) asti.
4. **Tarinan UI uuteen asuun (minä):** dialogi muotokuvin, valinnat, puhelin tarinan puheluille ja viesteille, luvun otsikko.
5. **Moottorin sisätilatuki (minä):** `sisa`-paikat ja sisäkoordinaatit, hahmot ja esineet sisätiloihin, aukioloajat kellosta, kantaminen. Testataan teatterilla.
6. **Vauhtiksen sisätila** + Meshy-kalusteet (kohta 7) → M01 kokonaan sisältä.
7. **Meshy-mallit (sinä / mallichat):** kohdan 7 lista, ensin Vauhtis ja perunasäkki, sitten julkisivut b557 ja b558.
8. **Teatterin näyttelijät:** kun hahmot ovat valmiit, lähetä nimet ja roolit. Teen illan esityksen, puvustamon M09:ään ja kaksi mikrotehtävää.
9. **HUD ja VIUH** (UI-suunnitelman vaiheet 4–5): mikrotehtävät siirtyvät puhelimeen.
10. Sitten järjestyksessä: Lumin piilo (sähköasema), Satakunnan Varaosa, Kaksi Siivua, Kiilto, ja päivän kierroksen paluu (M16).
