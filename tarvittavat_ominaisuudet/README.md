# Tarvittavat ominaisuudet – Satamakaupunki-tarinatila Porin kopterilentoon

Päivitetty 20.11.2026. Lista perustuu käsikirjoitukseen *Satamakaupunki – käsikirjoitus* (tehtävät M01–M26)
ja pelin nykytilaan (`index.html`, `SIIRTO_TOISELLE_TILILLE.md` 20.11. asti).

**Prioriteetit**
- **P1** = tarvitaan Luku 1:n (M01–M06) pelattavaan versioon
- **P2** = luvut 2–3
- **P3** = luvut 4–5, sivutehtävät ja viimeistely

**Tila**
- ✅ on jo
- 🟡 osittain, laajennettava
- ❌ puuttuu

---

## 0. Päätettävä ensin

| Asia | Miksi |
|---|---|
| ~~Satamakaupunki vs. "Outojen asioiden toimitus"~~ | **Päätetty 20.11.2026 (omistaja): "Outojen asioiden toimituksesta" luovutaan.** Satamakaupunki on pelin ainoa tarina. Tapaus 1:n koodista (`window.__case`) käytetään tehtävämoottorin pohjana vain tekniikkaa (soitto, tekstitys, valinnat, tallennus), ei sisältöä. Ks. kohta 1 "Tapaus 1 pois". |
| Radion nimi | Pelissä radio on "Radio Porikopteri", käsikirjoituksessa kertoja on "Radio Kirjuri". Pitää valita toinen. |
| Pelaajan hahmo | `hahmo.js` on geneerinen pelaaja. Tarinaa varten pelaaja on Rami Koski. |
| Tiedostorakenne | `index.html` on 390 kt ja kaksi istuntoa on jo tallentanut sen toistensa päälle (loki 20.11.). Tehtävät, dialogit ja hahmot kannattaa tehdä omiin tiedostoihinsa (`missions/`, `dialog/`), ennen kuin tarinaa kirjoitetaan koodiin. |

## 1. Tehtävämoottori (P1, kriittisin)

> **20.11.2026: tehty kansioon `tarina/`** (ks. `tarina/README.md`). index.html ei muuttunut. Valmiina: data-ohjattu moottori, liput/muuttujat/esineet,
> tarkistuspisteet, epäonnistumisruutu, tallennus, HUD-tavoite + suuntanuoli, karttamerkit, avautumisjärjestys, kehittäjätila, `kokeilu.html`
> ja node-testit. Lisäksi kohdasta 2 dialogi, valinnat, puhelu, tekstiviesti ja välianimaation palkit (kameraa ei vielä ohjata).
> Luku 1 (M01–M06) on datana. Vielä puuttuu: iso kartta / minikartta, kytkentä index.html:ään (1 rivi) ja tapaus 1:n poisto.

| Ominaisuus | Tila | Tarvitaan | Huom |
|---|---|---|---|
| Data-ohjattu tehtävämoottori (ID, VAATII, LAUKAISU, OBJ, CP, FAIL, ASETTAA, PALKINTO) | 🟡 | kaikki | `window.__case` on tapaus 1:lle kovakoodattu tilakone. Se yleistetään lukemaan `missions/Mxx.json`. |
| Tapaus 1 pois ("Karhu katsoo väärään suuntaan") | 🟡 | P1 | Konseptista luovuttu. Poistetaan pelistä: soitto käynnistyy nyt 40 s aloituksesta, tallennus `localStorage['pori-tapaus-1']`, juttu radion soittolistalla, karhupatsaan vilkuilu ja `greet`in koukku `__case.ask`. Tiedostot `radio/tapaus1*.mp3/json` ja `tools/radio/tapaus1.json` voi poistaa tai arkistoida. Tehtävämoottori säilyttää tekniikan. |
| Liput ja muuttujat (`FLAG_*`, `VAR_*`, `ITEM_*`) | ❌ | kaikki | Yksi tila-olio, tallennus localStorageen |
| Tallennus ja lataus (pelastuskohdat korjaamo/piilo, useampi tallennuspaikka) | 🟡 | kaikki | localStorage on jo käytössä (tapaus, Kespa-ennätys) |
| Tarkistuspisteet (CP) ja uusintayritys | ❌ | kaikki | Pelaajan, kulkuneuvon ja tavoitteen tila tallennetaan CP:ssä |
| Epäonnistumisehdot ja -ruutu (`SYS_FAIL_*`) | ❌ | kaikki | Teksti "Ammattilaisia ei jää kiinni", ei kuolemaa |
| HUD: tavoiterivi, ajastin ja mittarit (akku, etäisyys, naamioituminen, kuuntelu) | 🟡 | M02–M26 | Kespan lenkin yläpalkki (sija/aika/käännös) toimii pohjana |
| Tehtävämerkit kartalla ja reittiviiva | 🟡 | kaikki | `TOUR`/`target()` ja Kespan keltainen nauha yleistetään |
| Karttanäkymä (iso kartta) ja minikartta | ❌ | kaikki | Myös aluevärit (Luku 2: sininen → keltainen) |
| Tehtävien avautuminen ja lukujärjestys | ❌ | kaikki | |
| Kehittäjätila: hyppää tehtävään tai CP:hen, aseta liput | ❌ | testaus | Lisäksi headless-käynnistys: lokin mukaan `begin()` ei käynnisty headlessina, joten tehtäviä ei voi testata pilvessä |

## 2. Tarina ja esitys

| Ominaisuus | Tila | Prio | Tarvitaan | Huom |
|---|---|---|---|---|
| Dialogijärjestelmä (`HAHMO (tunne): repliikki`), tekstitys ja puhekupla | 🟡 | P1 | kaikki | Tapaus 1:n tekstityskortti ja `greet` toimivat pohjana |
| Dialogivalinnat | 🟡 | P2 | M09, M21, M25 | Tapaus 1:n otsikkovalinta (napit 1–3) yleistetään |
| Välianimaatiot: kameran ajot, hahmojen sijoittelu, letterbox, ohitus | ❌ | P1 | CUT_M01_A ja muut | Esim. `cutscenes/*.json` (kameran avainkohdat + repliikit) |
| Puhelin: soitot ja tekstiviestit | 🟡 | P1 | M03, M05 | Tapauksen soitto on olemassa (puhelinsuodin), tekstiviesti-UI puuttuu |
| Ääninäyttely | 🟡 | P2 | kaikki | `tools/radio/tapaukset.py` + onnx-TTS toimii, tarvitaan äänet hahmoille (Tapsa porilaisittain) |
| RADIO-kertoja reagoi tehtäviin | 🟡 | P2 | M01, M11–M13, M19, M20, loput | Radio Porikopterin puhekanava on olemassa, lisätään tapahtumaleikkeet |
| Tunne → ilme/ele-animaatiot | ❌ | P2 | kaikki | neutraali, iloinen, vihainen, yllättynyt, huolestunut, ovela |

## 3. Hahmot

| Ominaisuus | Tila | Prio | Huom |
|---|---|---|---|
| Nimetyt hahmot: Rami, Tapsa, Lumi, Terttu, Harju, Varjo | ❌ | P1 (Rami, Tapsa, Lumi) | `npc_*.js` (6 geneeristä mallia) + `porikopteri_hahmo.py` toimivat pohjana. Muista leipoa Walk/Run/Dance perään (`kavely_glb.py`). |
| Vartijat (Varjon univormu), myyjä, kuriiri, ovimies, torikauppiaat | ❌ | P1–P2 | Muunnelmat npc-malleista |
| Hiiviskely (kyykky, hidas kävely) | ❌ | P1 | M03, M13, M14, M17, M22 |
| Liukastuminen, nousu ja pako | ❌ | P1 | M04, vartijoiden reaktio vesisuihkuun |
| Kyydissä istuminen auton matkustajana | 🟡 | P1 | M01 (Tapsa kuljettaa). Pyörän kyytiläinen on tehty (20.11.), autoon lisätään sama. |
| Botti seuraa tai ajaa tarinahahmona | 🟡 | P1 | M02 (Tapsa kilpakuskina): Kespan kisabotit toimivat pohjana |
| Laskuvarjo- ja lentoreppuasennot | ❌ | P3 | M17, M20, M22, M23 |

## 4. Kulkuneuvot

Valmiina: kävely, polkupyörä, helikopteri, bussi, farmari, pakettiauto ja sedan. Lentokone on tekeillä.

| Kulkuneuvo / ominaisuus | Tila | Prio | Tarvitaan | Huom |
|---|---|---|---|---|
| Jokivene (Rami saapuu, botti ajaa) | ❌ | P1 | M01 (välianimaatio riittää) | |
| **Vesifysiikka ja ajettava vene** | ❌ | P3 | M19, M20 (lentokentältä paluu), M26 | Joki on jo mallinnettu (`river.js`), mutta veneitä ei ole |
| Soutuvene ja soutukilpa | ❌ | P3 | M19 | |
| Varjon pikavene ja poliisivene (botit) | ❌ | P3 | M26 | |
| Juna, raide ja liikkuva vaunu | ❌ | P2 | M07 | `bl_asema` on jo, raiteet ja junamalli puuttuvat |
| Avoauto | ❌ | P2 | M07 | Voi olla farmarin variantti |
| Hinausauto ja magneetti | ❌ | P2 | M15 | |
| Panssariauto (botti) | ❌ | P2 | M15 | |
| Moottoripyörä | ❌ | P2 | M13 (äänekäs tapa) | |
| Varjon kuorma-autot (liikkuvat botit) | 🟡 | P2 | M10 | Bottiliikenne on olemassa, uusi malli ja reitti puuttuvat |
| Kopterin vaijeri ja ripustettu kuorma (kontti heiluu) | ❌ | P2 | M16 | |
| Kauko-ohjattava drooni ja akku | ❌ | P1 | M05 | Voi pohjautua kopterin fysiikkaan, pieni malli |
| RC-lentokone ja pudotus | ❌ | P2 | M10 | Lentokoneen ohjaus on tekeillä, joten sitä voi hyödyntää |
| Kauko-ohjattava pikkuauto | ❌ | P3 | M23 | |
| Lentokone tehtäväkäytössä (yksityiskone botti, nousu ja paluu) | 🟡 | P3 | M20 | Tekeillä |
| Bussi tehtäväkäytössä tai sivutehtävänä | 🟡 | P3 | – | Bussilinja / "kuljeta matkustajat" -sivutehtävä |
| Kulkuneuvon vaihto kesken tehtävän | 🟡 | P1 | M01–M05 | `takeNear`/`takeDo`/`setCarType` ovat jo olemassa |

## 5. Pelimekaniikat

| Mekaniikka | Tila | Prio | Tarvitaan | Huom |
|---|---|---|---|---|
| **Varjo-mittari** (0–5 tähteä): vartijat autoilla ja jalan, uutiskopteri, karistaminen, katveet | ❌ | P1 | M03, M13, M18, M26 | Ei poliisia. Kiinni jääminen → epäonnistumisruutu. Bottiautojen reititys (`cars.update`) toimii pohjana. |
| NPC-havainnointi: näkökartiot, epäily → hälytys | ❌ | P1 | M03, M09, M13, M14, M17, M22 | |
| Vesiletku ja sammutinvaahto (suihku, osumat) | ❌ | P1 | M04 | Partikkelit voivat pohjautua savujärjestelmään (`smokeStep`) |
| Paintball: ammus, osuma, väriroiske, joukkueet, lipunryöstö | ❌ | P2 | M12 | |
| Saippuakuplat, värisavu, ilotulitus | 🟡 | P2 | M13, loput | Spritesavu (c27) on olemassa |
| Valepuvut ja naamioitumismittari | ❌ | P2 | M09, M13, M14, M17 | Hahmon materiaalin tai mallin vaihto |
| Kuuntelumittari (pysy kuuloetäisyydellä) | ❌ | P2 | M09 | |
| Ajoitusnappi (QTE): haavi, magneetti, salkku | ❌ | P2 | M07, M15, M20 | Yksi yleinen komponentti |
| Minipelit: johdot, rytmilukko, tiirikka, kassakaappi | ❌ | P2–P3 | M14, M23, M24 | |
| Esineiden poiminta ja kantaminen (avaimet, hakemukset, korut, kansio) | ❌ | P1 | M03, M08, M13 | Ml. pudotus törmäyksessä (M08) |
| Kuvaaminen droonilla (kohde näkyvissä + etäisyys) | ❌ | P1 | M05 | |
| Kuljetus aikarajassa | 🟡 | P2 | M08 | Kespan ajastin toimii pohjana |
| Seuraa kohdetta / pysy rinnalla (etäisyysmittari) | ❌ | P2 | M07, M09, M20 | |
| Laskuvarjo ja tarkkuuslasku | ❌ | P3 | M17, M20 | |
| Lentoreppu | ❌ | P3 | M22, M23 | |
| Osien keruu ja korjaus | ❌ | P3 | M19 | |
| Liittolaisten määrä vaikuttaa finaaliin (`VAR_ALLIES`) | ❌ | P3 | M19, M24 | |
| Kilpa-ajo tarinatehtävänä | ✅ | P1 | M02, M11 | Kespan lenkki: botit, reitti, ajanotto. Reitti ja botit tarvitsevat parametrit. |
| Auton vauriot ja hajoaminen | ✅ | – | M01 (FAIL) | |

## 6. Kartta ja paikat

| Paikka | Tila | Prio | Tarvitaan | Huom |
|---|---|---|---|---|
| Eteläranta, Isosilta, Pohjoisranta, Kauppatori, Raatihuone, Kirjurinluoto | ✅ | – | | |
| Porin teatteri (puvustamo puuttuu) | 🟡 | P2 | M09, M14 | Sisätila (aula, sali, kahvila) on jo |
| Taidemuseo, sisätila gaalaksi | 🟡 | P2 | M09 | Sisätila on, gaala-asetelma (vieraat, pöydät) puuttuu |
| Satakunnan Museo (takaovi) | 🟡 | P2 | M13 | `bl_museo` on olemassa |
| Junneliuksen palatsi (kaupungintalo) | ✅ | P2 | M08 | Ulkoa |
| Rautatieasema ja raiteet ulos kaupungista | 🟡 | P2 | M07 | |
| Porin lentoasema ja tie sinne | ❌ | P3 | M20 | Omistaja: lisätään |
| **Tapsan korjaamo** (keksitty, Pohjoisranta, piha + halli) | ❌ | P1 | M01–M05 | Tukikohta |
| **Lumin piilo** (tiilivarasto) | ❌ | P1 | M06 + suunnittelutaulu | |
| **Varjo-tornin työmaa** (nosturit, suunnitelmataulut) | ❌ | P1 | M05 | |
| Varjo-torni (näyttelykerros, 12. ja 20. krs, kattoravintola, hissit) | ❌ | P2 | M13, M17, M21, M24, M25 | Sijainti valittava, esim. tyhjä tontti |
| Hotelli Varjo (aula, käytävät, holvi) | ❌ | P2 | M14 | |
| Varjon varasto (kontit, kellarilaboratorio, kattoikkuna) | ❌ | P2–P3 | M16, M22, M23 | |
| Autoliike Kiilto (piha, toimisto) | ❌ | P1 | M03 | |
| Vanha tehdasalue paintballiin | 🟡 | P2 | M12 | `bl_tehdas` on jo olemassa, joten käytetäänkö sitä? |
| Venevaja ja laituri Etelärannalla | ❌ | P3 | M01, M19 | |
| Juhlalava ja iso näyttö torilla / Kirjurinluodolla | ❌ | P3 | M25, loput | |
| Joen suu / kartan reuna | ❌ | P3 | M20, M26 | |
| Kerroksiin ja huoneisiin siirtyminen (ovet, hissit) | 🟡 | P2 | M14, M17, M24 | Sisätilojen siirtymä on olemassa (`interior`) |

## 7. Sivutehtävät ja keräiltävät (P3)

| Ominaisuus | Tila | Huom |
|---|---|---|
| Taksi / bussikuski | 🟡 | Kyydit ovat jo pelissä ja tuottavat rahaa (kohta 7b). Bussilinja puuttuu. |
| Ensihoito (ambulanssi) | ❌ | Uusi malli |
| Palokunta (paloauto, tulipalot) | ❌ | Uusi malli + liekit |
| Pizzalähetti (skootteri) | ❌ | |
| Stunttihypyt | ❌ | |
| 50 lokkipatsasta + tietoiskut (`SYS_FACT_POPUP`) | ❌ | `linnut.js`:n lokista patsasversio. Tietoiskujen tekstit sovitaan kaupungin kanssa. |
| Satunnaiset tapahtumat | ❌ | Käsikirjoituksen ohikulkijat (hukattu lompakko, karannut koira). Tehdään samalla tehtävämoottorilla. |
| Rallikisat / katukisat | 🟡 | Kespan lenkki + uudet reitit |
| Päivän tulostaulu | 🟡 | Kespan "Ei vielä" -lista |

## 7b. Raha (omistaja 20.11.2026: "pelaaja voi kerätä rahaa esim. kyyditsemällä porukkaa")

| Ominaisuus | Tila | Prio | Huom |
|---|---|---|---|
| Raha tehtävistä | ✅ | – | `palkinto.raha` (tarina/) |
| Raha kyydeistä | ✅ | – | Pelin kyydit (`window.__ride`) → enintään 10 € / km (omistaja 20.11.); `KYYTI_EUROA_PISTE` tarina/peli.js:ssä |
| Raha muista sivutehtävistä (taksi, pizzalähetti, kilpa-ajot, ensihoito) | ❌ | P3 | `__tarina.moottori.lisaaRaha(n, lähde)` |
| **Mihin rahaa käytetään** | 🟡 | P2 | **Päätetty: auton maalaus ja tuunaus Tapsan korjaamolla (kohta 7c).** Muita ehdotuksia: autojen ostaminen, korjaus kesken tehtävän, valepuvut teatterin puvustamosta, Tapsan korjaamon ja Lumin piilon päivitykset, kahvit torilla (kunto takaisin). Ei uhkapelejä eikä ostoja oikealla rahalla (ikäraja 7). |
| Raha näkyviin HUDiin | 🟡 | P2 | Nyt vain P-valikossa ja ilmoituksena (+50 € · kyyti) |
| Kyydit tarinan sivutehtäväksi | 🟡 | P3 | Pelin kyydit toimivat jo; tarinaan voi lisätä nimettyjä kyytejä (Terttu torille, Tapsa korjaamolle) |

## 7c. Auton maalaus ja tuunaus (omistaja 20.11.2026: "Autoa voi maalata ja tuunata")

Osat pyydetään mallichatista; pyyntöteksti: `tuunaus_mallipyynto.md` (tämä kansio).

| Ominaisuus | Tila | Prio | Huom |
|---|---|---|---|
| Maalaus (väri + pinta: kiiltävä, metallinen, matta) | 🟡 | P2 | `CarPaint`-materiaali on jo kaikissa autoissa ja lainaus vaihtaa sen värin → maalaus on vain väri + roughness/metalness. Ei vaadi uusia malleja. |
| Teippaukset ja raidat | ❌ | P2 | Mallichat: teippikuviot tekstuureina tai erillisinä ohuina verkkoina |
| Tuunausosat (vanteet, spoileri, helmat, puskurit, kattoteline/-boksi, pakoputki, lisävalot) | ❌ | P2 | Mallichat: osat + kiinnityspisteet jokaiseen automalliin |
| Korjaamon tuunausvalikko (osa, hinta, esikatselu, osto) | ❌ | P2 | Tarinatilaan: korjaamon merkki → valikko, raha `tila.raha`sta, valinnat tallennetaan autokohtaisesti |
| Oma auto (tuunattu auto säilyy) | ❌ | P2 | Nyt jokainen lainattu auto on uusi. Tarvitaan "oma auto" korjaamolle, joka säilyttää maalin ja osat (tallennus localStorageen). |
| Osien vaikutus ajoon | ❌ | P3 | Esim. vanteet/renkaat +pito, spoileri vain ulkonäkö. Pidetään pienenä (±5–10 %). |
| Hinnasto | ❌ | P2 | Ehdotus: maalaus 120 €, metalli/matta +60 €, teippaus 80 €, vanteet 250 €, spoileri 180 €, helmat 150 €, puskurit 200 €, kattoboksi 90 €, lisävalot 70 €, pakoputki 60 €. Tehtävä 200–300 €, kyyti ≤ 10 €/km. |

## 8. Yleiset järjestelmät

| Ominaisuus | Tila | Prio | Huom |
|---|---|---|---|
| Päävalikko, tauko ja asetukset (ääni, grafiikka, ohjaimet, tekstitykset) | ❌ | P1 | |
| Uusi peli / jatka / tehtävävalinta | ❌ | P1 | |
| Lokalisointiavaimet (`SYS_*`, repliikit) | ❌ | P2 | Kaikki tekstit tiedostoon `lang/fi.json` |
| Peliohjainten tuki (gamepad) | ❌ | P2 | Kosketus ja näppäimistö ovat olemassa |
| Vuorokaudenaika (aamu, ilta, juhla-ilta) | 🟡 | P2 | Yöleivonta on olemassa (`night/`). Tehtävät tarvitsevat ajan asetuksen (M01 aamu, M18 ilta, finaali ilta). |
| Pelin kello (M08 klo 16) | ❌ | P2 | |
| Ääniefektit: vesisuihku, juna, veneet, hälytys, kuplat | ❌ | P2 | |
| Tehtävämusiikki (jännitys, takaa-ajo, voitto) | ❌ | P2 | Suno-kappaleet + `tahti.py`-putki |
| Saavutukset | ❌ | P3 | |
| Linnut väistävät kulkuneuvoja / ääni | 🟡 | P3 | Lokin "ei vielä" |

## 9. Tunnetut avoimet viat, jotka vaikuttavat tehtäviin

Lähde: `SIIRTO_TOISELLE_TILILLE.md`.

- Botti–pelaaja-sivutörmäykset ja kulmasta kääntyvä liikenneauto menevät läpi. Tämä vaikuttaa takaa-ajoihin (Varjo-mittari).
- Polkupyörät ja patsaat eivät ole esteitä.
- Kävelijät eivät väistä toisiaan.
- Pyörän kääntösäde on auton, ja ajajan jalat eivät ole maassa pysähdyksissä.
- Savu jäätyy, kun pelaaja nousee autosta (`smokeStep(dt, 0)` pääsilmukkaan).
- Kespan botit kloonaavat pelaajan mallin. Tarinan kilpaa varten tarvitaan omat kilpa-automallit.
- Moni ominaisuus on testattu vain headlessina, joten se pitää koepelata.

## 10. Ehdotettu järjestys (pystysuora siivu = Luku 1)

1. Tiedostorakenne: `missions/`, `dialog/`, `cutscenes/`, `lang/`
2. Tehtävämoottori, liput, CP, tallennus, HUD-tavoite, karttamerkki (tapaus 1:n tekniikka pohjaksi, sen sisältö pois)
3. Dialogi ja yksinkertainen välianimaatio (kameran avainkohdat)
4. Hahmot Rami, Tapsa ja Lumi + matkustajana istuminen
5. Paikat: korjaamo, Lumin piilo, työmaa, Autoliike Kiilto
6. M01–M02 (ajo, kilpa: olemassa olevat järjestelmät)
7. Hiiviskely ja Varjo-mittari, kevyt versio → M03
8. Vesiletku → M04
9. Drooni → M05
10. M06 ja koepeluu → sen jälkeen Luku 2
