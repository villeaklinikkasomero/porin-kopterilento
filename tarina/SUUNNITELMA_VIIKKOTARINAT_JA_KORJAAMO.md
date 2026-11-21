# Suunnitelma: AI-viikkotarinat ja Tapsan korjaamon laajennus

Kirjoitettu 21.11.2026. Pohjana pelin nykytila: `tarina/` (moottori, M01–M26, kaupat `K_*`, mikrotehtävät `S_*`, `talous.js`),
`korjaamo/korjaamo.js`, `radio/` + `tools/radio/speak.py` (Piper-TTS) ja `pipeline/` + `.github/workflows/porikit-collect.yml` (päivän PR -malli).

Kaksi osaa, jotka kytkeytyvät toisiinsa:

- **Osa A**: voidaanko AI:lla rikastaa tarinaa joka viikko Pori-aiheisista uutisista (esim. ampparit.com/pori) ja miten.
- **Osa B**: Tapsan korjaamon laajennus: hallin korjaus, lisäsiipi, aidattu piha ja uudet koneet. Mitä se on pelaajalle ja miten se rakennetaan.

Kytkös on luonteva: viikon uutiset tuovat korjaamolle asiakkaita ja keikkoja, ja korjaamon koneet ratkaisevat, mitä keikkoja pelaaja voi ottaa vastaan.

---

## Osa A – AI-viikkotarinat Porin uutisista

### A1. Lyhyt vastaus

**Kyllä, ja melko pienellä työllä**, koska tehtävät ovat jo dataa (`tarina/data/tehtavat/*.json`), moottori osaa toistuvat ja ehdolliset tehtävät,
radiopuhe syntyy skriptillä (`speak.py`) ja repossa on valmis malli automaattiselle, ihmisen hyväksymälle PR:lle (`porikit-collect.yml`).
AI:n ei tarvitse kirjoittaa koodia. Riittää, että se kirjoittaa viikoittain muutaman JSON-tiedoston olemassa olevassa muodossa, ja kone tarkistaa ne ennen kuin ihminen hyväksyy ne.

Kolme ehtoa:

1. **AI ei julkaise suoraan.** Jokainen viikko tulee PR:nä, jonka omistaja katsoo ja yhdistää (kuten grafiikkaputken päivän PR).
2. **Uutisesta otetaan vain aihe, ei tekstiä eikä oikeita ihmisiä.** Peli kertoo *rinnakkaistarinan*: keksityt hahmot, lempeä sävy, PEGI 7.
3. **Lähteen käyttöehdot tarkistetaan ennen automatisointia** (ks. A3). Ampparit on hyvä ideoiden lähde, mutta ei välttämättä automaattisen haun lähde.

### A2. Mitä "rinnakkaistarina" tarkoittaa pelissä

Uutinen ei tule peliin uutisena vaan **pelimaailman tapahtumana**, joka elää viikon (tai kaksi) ja häviää sitten.
Esimerkit ovat 21.11.2026 Ampparin Pori-sivun otsikoista:

| Viikon uutisaihe (lähde) | Rinnakkaistarina pelissä | Mitä pelaaja tekee | Käytetyt valmiit osat |
|---|---|---|---|
| Hakekasat syttyvät Porissa toistuvasti (Yle) | Kirjurinluodon puistotyömaan hakekasa savuaa. Terttu huomaa savun torilta. | Vie sammutin paikalle ja pysy savun äärellä 10 s. Radio kiittää "nimetöntä naapuria". | `mene`, `pysy` + mittari, `151_savu.js` (savu), myöhemmin M04:n vesiletku |
| Katuremontti parantaa pyöräilijöiden oloja (SK) | Tapsan kautta tulee viesti: kadulla on remontti, kiertotie, ja asiakkaiden renkaat ovat puhki kuopista. | Viikon pyöräkilpa kiertotietä pitkin / renkaanvaihtokeikka korjaamolla | `portit`, `S_RENKAAT`, `anna_ajoneuvo` (`bike`) |
| Isomäen pikkujoulut keräsivät väkeä (SK) | Pikkujoulukausi: kyytejä riittää. | Viikon kyyteistä saa +20 % (kyytibonus), Tapsa pyytää kyydin "korjaamon pikkujouluihin" | kyydit (`__ride`), `lisaaRaha`, `soitto` |
| Budjettiesitykseen tehtiin muutoksia (Yle) | Ei tehtävää. Korkeintaan neutraali radiolause ("kaupungin budjetti etenee"). | – | Radio |
| Henkirikosoikeudenkäynti (Kankaanpään Seutu) | **Hylätään automaattisesti** (rikos, väkivalta, oikea ihminen) | – | Suodatin |

Tuotoksia on neljää tasoa, helpoimmasta vaikeimpaan:

1. **Radio-uutinen** (Radio Porikopteri, 15–30 s): AI kirjoittaa, Piper lukee. Ei pelimekaniikkaa, joten riski on pienin.
2. **Juoru**: Terttu tai Tapsa sanoo viikon asiasta 1–3 repliikkiä, kun pelaaja käy torilla tai korjaamolla (`maailma.json`-hahmo + ehdollinen dialogi).
3. **Viikon sivutehtävä** `V_2026W48_01.json`: vain olemassa olevia vaihetyyppejä (`mene`, `keraa`, `portit`, `pysy`, `seuraa`, `valinta`, `toiminto` valmiilla käsittelijöillä). Palkkio 20–80 €.
4. **Maailman muutos**: tiesulku, savu, juhlavalot, kojut jne. Vaatii kirjaston valmiita "rekvisiitta-asetelmia", joista AI vain valitsee (AI ei tee 3D:tä).

Taso 1 ja 2 riittävät alkuun. Taso 3 tulee, kun tarkistusputki on luotettava.

### A3. Lähteet ja oikeudet

| Lähde | Huom |
|---|---|
| **ampparit.com/pori** | Alma Median uutiskooste (pääosin Satakunnan Kansa ja Yle, myös paikallislehdet ja poliisi). Sivulla ei näkynyt RSS-syötettä, ja sivu on Alma Median käyttöehtojen alainen. **Tarkista käyttöehdot ja robots.txt ennen automaattista hakua.** Jos automaattinen haku ei ole sallittu, Ampparia voi käyttää käsin: omistaja liittää viikon otsikot tiedostoon. |
| Yle (Satakunta) | Ylellä on julkisia RSS-syötteitä. Tarkista, onko Satakunnan alueelle oma syöte. |
| Porin kaupungin tiedotteet | Turvallisin lähde: kaupungin omat tapahtumat, tiet, työmaat ja juhlat. Sopii hyvin, koska paikkojen käytöstä peli sovitaan kaupungin kanssa muutenkin. |
| Porin tapahtumakalenteri | Konsertit, markkinat ja urheilu. Tämä on parasta "positiivista" sisältöä viikkotehtäviin. |

Periaatteet:

- Talteen otetaan vain **otsikko, lähteen nimi, linkki ja päivämäärä**. Uutistekstiä ei kopioida peliin eikä AI:lle anneta koko artikkelia, joten tekijänoikeusriski jää pieneksi.
- Peliin **ei tule oikeiden ihmisten nimiä** (ei poliitikkoja, urheilijoita eikä uhreja). Yritysten nimiä ei myöskään tule: peli keksii omat (vrt. "Grilli Kaksi Siivua").
- Lähdeluettelo jää PR:n kuvaukseen, ja sieltä tarkistaja näkee, mistä idea tuli.

### A4. Putki

```
 ma 05:41 (GitHub Actions, cron)
   │
   ├─ 1. hae.py         otsikot (lähteet A3) → work/viikko/2026-W48/otsikot.json   [vain otsikko, lähde, linkki, pvm]
   ├─ 2. suodata.py     sääntösuodatin: kieltolista (kuolema, rikos, onnettomuus, sairaus, vaalit, nimet...) → hylätyt näkyvät PR:ssä
   ├─ 3. kirjoita.py    Claude API, 1 kutsu, rakenteinen JSON-tuloste (schema) → 3–6 ideaa, joista paras 1–3 toteutetaan
   │                    syötteenä: otsikot + "tarinaraamattu" (hahmot, sävy, PEGI 7, paikat.json, sallitut vaihetyypit, palkkiohaarukka)
   ├─ 4. tarkista.mjs   JSON-skeema, LOC-avaimet olemassa, repliikkien pituus, kieltolista uudestaan,
   │                    ja tehtävä pelataan läpi headlessina samalla tavalla kuin tarina/testi.mjs (moottori + simuloitu pelaaja)
   ├─ 5. speak.py       radio-uutiset → radio/viikko/2026W48_*.mp3 (Piper, sama ääni)
   └─ 6. PR "Viikkotarina 2026-W48": tiedostot + lähteet + hylätyt otsikot syineen + kuvakaappaus kokeilu.html:stä
                      → omistaja lukee, muokkaa JSONia tarvittaessa, yhdistää → peli lataa sen
```

Kustannus: yksi API-kutsu viikossa (senttejä), Piper ja Actions ovat ilmaisia julkisessa repossa / pienellä käytöllä.

### A5. Muutokset peliin

**Data**

```
tarina/data/viikko/
  index.json                     [{ "viikko": "2026-W48", "alku": "2026-11-23", "loppu": "2026-12-06", "tiedostot": [...] }]
  2026-W48/
    V_2026W48_01.json            tavallinen tehtävä + kentät "viikko", "voimassa", "lahde"
    juorut.json                  { "TERTTU": [["TERTTU","huolestunut","..."]], "TAPSA": [...] }
    radio.json                   [{ "f": "viikko/2026W48_1.mp3", "d": 21.4, "t": "Viikon uutinen: ..." }]
```

**Moottori ja sovitin** (pieni työ):

- `peli.js` lataa `viikko/index.json`:n ja ne viikot, joiden `voimassa`-väli osuu tähän päivään (oikea kalenteri, ei pelin kello). Vanhentuneet tehtävät eivät näy, mutta tehdyt jäävät tallennukseen (`tila.valmiit`).
- Viikkotehtävät eivät koskaan aseta pääjuonen lippuja (`FLAG_M*`), joten ne eivät voi rikkoa tarinaa. `tarkista.mjs` vahtii tätä.
- Uusi `laji: "viikko"` ja merkki 📰, ja P-valikkoon välilehti "Tällä viikolla Porissa".
- Radio: viikon leikkeet lisätään Porikopteri-kanavan soittolistan alkuun (`radio.json` + `111_radio.js`).

### A6. AI-kehote (luonnos)

Tarinaraamattu kirjoitetaan kerran tiedostoon `tools/viikko/raamattu.md`:

- Hahmot, puhetavat (Tapsan porilaisuus, Tertun lämpö, Radio Porikopterin pirteys), PEGI 7 ja "ei poliisia, ei kuolemaa".
- Sallitut paikat (`paikat.json`), vaihetyypit ja käsittelijät, palkkiot 20–80 €, kesto 2–6 min.
- **Varjo pidetään viikkotarinoista erossa** (pääjuonen vastustaja ei saa uusia tekoja AI:lta). Poikkeus: omistaja voi viikkokohtaisesti sallia, että Varjo "sponsoroi" jotain harmitonta.
- Tuloste on JSON-skeema. Mukaan tulee 2–3 käsin tehtyä esimerkkiviikkoa, jotka AI saa mallikseen.

Kehotteen ydin: *"Tässä viikon Pori-otsikot. Valitse enintään kolme, joista syntyy hyväntuulinen, 7-vuotiaalle sopiva pelitapahtuma. Älä käytä oikeiden ihmisten tai yritysten nimiä äläkä lainaa uutistekstiä. Jos otsikko koskee rikosta, kuolemaa, onnettomuuden uhria, sairautta tai puoluepolitiikkaa, hylkää se ja kerro syy. Palauta JSON skeeman mukaan."*

### A7. Riskit ja vastatoimet

| Riski | Vastatoimi |
|---|---|
| Ikävä uutinen muuttuu viihteeksi (tulipalo, jossa oli uhreja) | Kaksi suodatinta (sääntö + AI:n oma hylkäys) ja ihminen PR:ssä. Epäselvässä tapauksessa hylätään. |
| Oikea ihminen tai yritys tunnistetaan | Nimikieltolista, yritysnimet keksitään, ja tarkistaja katsoo |
| Keksitty paikka tai paikka kartan ulkopuolella (Lavia, Ulvila) | Vain `LOC_*`-avaimet hyväksytään. Kartan ulkopuolinen aihe → vain radio. |
| Tehtävä ei ole läpäistävissä | Headless-läpipeluu `tarkista.mjs`:ssä. Hylätty tehtävä ei tule PR:ään. |
| Laatu vaihtelee | Toteutetaan enintään 1–3 ideaa viikossa, ja omistaja voi muokata JSONia PR:ssä |
| Lähde kieltää automaattisen haun | Ampparia käytetään käsin, automaattisesti vain sallitut syötteet (A3) |
| Kaupungin näkökulma | Kaupungin kanssa sovitaan etukäteen, millaiset aiheet sopivat (esim. "vain tapahtumat ja työmaat") |

### A8. Vaiheet

| Vaihe | Sisältö | Työ |
|---|---|---|
| **V0 käsin** | Omistaja liittää viikon otsikot, AI (chat) tekee radioleikkeen ja juoru- ja tehtävä-JSONit, ja ne testataan `kokeilu.html`:ssä. Näin opitaan, mikä toimii. | 1 istunto |
| **V1 radio** | `tools/viikko/` (hae, suodata, kirjoita, speak), workflow ja PR. Vain radio-uutiset ja juorut. | 1–2 istuntoa |
| **V2 tehtävät** | Viikkotehtävät, `tarkista.mjs` (läpipeluu), P-valikon välilehti ja vanheneminen | 2 istuntoa |
| **V3 maailma** | Rekvisiittakirjasto (tiesulku, savu, juhlavalot, kojut, työmaa-aita), josta AI valitsee | 2–3 istuntoa |
| **V4 korjaamo** | Uutiset tuovat korjaamolle asiakkaita (Osa B, kohta B6) | osa B:tä |

---

## Osa B – Tapsan korjaamon laajennus

### B1. Lähtötilanne (21.11.2026)

- Peltihalli 9,7 × 12,2 m Äestäjänkadulla [-598.9, -443.0], ovi pohjoiseen, nosto-ovi, ajoluiska, kyltti ja sisustus koodissa (`sisustus()`).
- Yksi kaksipilarinostin (U-näppäin), työkaluhylly, Meshy-mallit `tools/korjaamo/tee_mallit.py` → `korjaamo_mallit.js`.
- Talous: `K_KORJAUS` (10/25/45 €), `K_OSAT` (Satakunnan Varaosa) → `K_NOUTO` (pakettiauto) → `K_TUUNAUS`, `S_HINAUS`, `S_RENKAAT`. Rahaa tulee tehtävistä (200–300 €) ja kyydeistä (≤ 10 €/km).
- Tiedossa olevat puutteet: valot eivät valaise, katto ei ole kiinteä (kopterilla läpi), ovella ei ole ääntä, kävelijät eivät tunne hallia, "oma auto" puuttuu.
- `tarvittavat_ominaisuudet/README.md` 7b listaa jo rahan käyttökohteeksi "Tapsan korjaamon ja Lumin piilon päivitykset".

### B2. Idea pelaajan kannalta

Korjaamo on **pelin tukikohta, joka kasvaa pelaajan rahoilla**. Alussa se on vähän rähjäinen, ja jokainen päivitys
1) näkyy maailmassa, 2) avaa jotain uutta tekemistä ja 3) on pieni tarinahetki Tapsan kanssa. Tämä on samalla rahan pääkäyttökohde tuunauksen rinnalla.

Taso 0 on se, mikä pelissä on nyt, mutta siihen lisätään rapistumisen merkkejä (ruostelaikkuja, peltiä paikattu pressulla, rikkinäinen ikkuna, nuokkuva kyltti),
jotta korjauksen tekee mieli tehdä.

### B3. Päivityspuu

| # | Päivitys | Vaatii | Hinta* | Mitä näkyy | Mitä avautuu |
|---|---|---|---|---|---|
| 1 | **Hallin kunnostus**: katto, ikkunat, valot, oven moottori | M02 | 300 € | Uusi pelti, ruoste pois, ehjät ikkunat, valot palavat illalla, kyltti valaistu | Korjaukset halvemmat (−20 %), kiinteä katto (korjaa nykyisen vian), oven ääni |
| 2 | **Aita ja portti** | 1 + M04 | 250 € | Verkkoaita tontin ympäri, liukuportti, valonheitin, piha asfaltoitu | Pihalla on turva: Varjo-mittari laskee nopeasti ja vartijat eivät tule portista. Pihalle jätetty auto säilyy (pohja "omalle autolle"). |
| 3 | **Rengaskone + tasapainotus** | 1 | 180 € | Kaksi konetta ja rengashylly | Vanteet asennetaan hallissa, `S_RENKAAT` paremmaksi, renkaanvaihtokeikat |
| 4 | **Diagnostiikkalaite** | 1 | 150 € | Kärry näyttöineen | Vauriot näkyvät tarkemmin, ja korjaushinta lasketaan vaurion mukaan (ei kolmea hintaporrasta) |
| 5 | **Toinen nostin** | 1 | 400 € | Toinen ajoruutu | Kaksi autoa kerralla → asiakastyöt (B6) kulkevat rinnakkain oman auton kanssa |
| 6 | **Lisäsiipi: maalaamo** | 1 + 2 | 800 € | Kylkiäinen hallin sivulle ja maalauskoppi | Maalaus ja teippaus tehdään hallissa (ei enää varaosaliikkeen "maalauspakettina"), oma värivalikko |
| 7 | **Hinausauto** | 2 + M14 | 600 € | Hinuri pihalla | `S_HINAUS` hinurilla (rikkinäistä autoa ei tarvitse ajaa), valmiina M15:een (Panssariauto vaatii hinausauton) |
| 8 | **Painepesuri ja pesupaikka** | 2 | 120 € | Pesukaivo pihalla | Auton pesu (kosmeettinen), lapsille hauska suihkutus. Sama tekniikka kuin M04:n vesiletku. |
| 9 | **Taukotila ja kahvinkeitin** | 1 | 90 € | Pöytä, sohva, keitin | ENERGIA palautuu korjaamolla (vaihtoehto grillille), ja Tapsan juorut (A2) kuulee täällä |

\* Hinnat ovat ehdotuksia. Yhteensä noin 2 900 €, eli noin 10–14 tehtävää kyytien kanssa, joten päivitykset riittävät koko tarinan ajaksi.
Hinnat kuuluvat yhteen tiedostoon, jotta tasapainoa voi säätää ilman koodimuutoksia.

**Ostaminen ja rakentaminen** käyttää samaa rytmiä kuin tuunaus (osto → nouto → asennus), jotta pelaaja oppii sen kerran:

1. Tapsalta tai korjaamon ilmoitustaululta (📋-merkki) valitaan päivitys `valinta`-vaiheella, jossa on `hinta`.
2. Isoissa päivityksissä (1, 2, 6) materiaalit noudetaan pakettiautolla (pelti / aitaelementit / maalauskoppi), käyttäen olemassa olevaa `K_NOUTO`-mekaniikkaa ja uusia paikkoja (rautakauppa / Satakunnan Varaosa).
3. Rakennus = lyhyt välianimaatio (mustat palkit, Tapsa: "Anna mulle kaks päivää") + fade. Alussa ei pelillistä rakentamista.
4. Seuraavalla käynnillä päivitys on valmis, ja Radio Porikopteri tai Terttu kommentoi ("Tapsan halli kiiltää kuin uusi").

### B4. Tarinakytkökset

- **M02 jälkeen** Tapsa: "Jos tääl aiotaan tehdä töitä, katto pitää paikata." → päivitys 1 avautuu (ensimmäinen ohjattu osto).
- **M04 jälkeen** (vartijat kävivät pihalla): "Nyt laitetaan aita." → päivitys 2. Aita on tarinallisesti perusteltu.
- **M15** tarvitsee hinausauton. Joko tehtävä antaa sen lainaan, tai jos pelaaja on ostanut päivityksen 7, Tapsa sanoo: "Hyvä et ostettiin se hinuri."
- **M18–M23** (Tapsa vangittuna): korjaamo hiljenee, valot sammuvat, portti on lukossa, ja ilmoitustaulu ei toimi. Pelaaja huomaa tukikohdan merkityksen.
- **Loppu**: kaikki päivitykset valmiina → pieni lisäkohtaus lopputekstien jälkeen (korjaamon avajaiset).

### B5. Tekninen toteutus

**Data: `tarina/data/korjaamo.json`**

```json
{
  "paivitykset": [
    { "id": "KUNNOSTUS", "nimi": "Hallin kunnostus", "hinta": 300, "vaatii": ["FLAG_M02_DONE"],
      "nouto": { "paikka": "LOC_RAUTAKAUPPA", "kulku": "auto:van", "esine": "ITEM_PELTI" },
      "lippu": "KORJ_KUNNOSTUS", "vaikutus": { "korjausKerroin": 0.8 } },
    { "id": "AITA", "nimi": "Aita ja portti", "hinta": 250, "vaatii": ["KORJ_KUNNOSTUS", "FLAG_M04_DONE"], "lippu": "KORJ_AITA" }
  ]
}
```

- Ostotehtävät (`K_REMONTTI_*`) tehdään moottorin tavallisina toistuvina tehtävinä. Ne voi tehdä käsin tai pienellä generaattorilla korjaamo.json:sta. Moottoriin ei tarvita muutoksia.
- Valmistuminen asettaa lipun `KORJ_*`. Moottori tallentaa sen kuten muutkin liput.

**`korjaamo.js`: tila → ulkoasu**

- Uusi taulukko `PAIVITYKSET = { KUNNOSTUS: { rakenna(ryhma) → { nayta, piilota, laatikot } }, ... }`. Kaikki versiot rakennetaan latauksessa (tai laiskasti ensimmäisellä tarpeella), ja niitä vaihdetaan `visible`-arvolla.
- Lukee liput `window.__tarina.moottori.tila.liput` kerran sekunnissa (sama malli kuin `vieSeinat`), tai kuuntelee moottorin tapahtumaa, jos sellainen lisätään.
- Ilman tarinatilaa (vapaa lento) näytetään oletuksena kunnostettu halli, jotta vapaa pelaaja ei näe rähjää.

**Taso 0 rapistuminen ja kunnostus**

- Ruoste ja paikkaukset canvas-tekstuureina ja tarroina hallin pinnalla (sama tekniikka kuin lattian kulumassa `sisustus()`:ssa), pressu katolla laatikkona ja rikkinäinen ikkuna kuviona.
- Kunnostettu versio = tarrat pois + hallin materiaalin värin säätö (pisteväreihin leivotun sävyn kerroin) + valaistu kyltti (emissive).
- **Katto kiinteäksi:** lisätään katon korkeus `__korjaamoZ`:n rinnalle niin, että kopterin `roofAt` palauttaa katon tason hallin päällä (nykyinen vika).
- **Valot:** pelissä on vain tasainen taivasvalo, joten oikeat valot ovat kalliita. Ehdotus: loisteputket hohtavat (on jo), lattialle tulee "valolaikku"-tarrat, ja kun pelaaja on sisällä, käytetään yhtä `PointLight`ia (pois päältä yli 30 m päässä). Yövalaistus `aika/katuvalo_malli.js`:n tapaan.

**Aita ja portti**

- Tontin raja mitataan pelissä tarinan kehittäjätilan reitinnauhoituksella (**Ctrl+Shift+R** → aja tontin raja → pisteet leikepöydälle) ja tallennetaan `korjaamo.js`:ään vakioksi `AITA = [[x,y], ...]`.
  Tarkista myös `blender/osm_extract.json` / MML-rajat, jos tontin rajat löytyvät sieltä.
- Tolpat ja verkkopaneelit `InstancedMesh`inä (verkko on läpinäkyvä alfatekstuuri canvasista), noin 2,5 m paneelit.
- Törmäys: jokainen aidan osa on `__furn`-laatikko (`{x, y, yaw, hl, hw: 0.08}`). Muoto on jo tuettu.
- Liukuportti: sama logiikka kuin nosto-ovessa (avautuu alle 10 m päässä, sulkeutuu yli 13 m päässä, `gone`-lippu), mutta liike on sivuttainen.
- Tarkista, etteivät aidan linja ja naapuritalot (`bl_*`) / katuliikenne mene ristiin. Kävelijät (`moduulit/kavelijat.js`) eivät tunne hallia nytkään, joten tarvitaan sama "älä kävele tästä" -alue kuin muillekin esteille.

**Lisäsiipi (maalaamo)**

- Vaihtoehto A (nopea): sama Meshy-halli lyhennettynä ja käännettynä kyljelle. Halvin, mutta näyttää kopiolta.
- Vaihtoehto B (suositus): oma Meshy-malli "peltihallin kylkiäinen 6 × 10 m, harjakatto matalampi, ovi päädyssä". Mallipyyntö tehdään samaan tapaan kuin `tarvittavat_ominaisuudet/tuunaus_mallipyynto.md`, ja malli ajetaan `tee_mallit.py`:n läpi (normaalien korjaus ja valon leivonta tulevat mukana).
- Kylkiäinen saa oman lattiansa `__korjaamoZ`:hin, omat seinälaatikot ja oman oven. Väliseinään tehdään aukko, jotta autolla pääsee siiven ja hallin välillä.
- **Ensin tarkistetaan, mille puolelle tontilla mahtuu** (itä vai länsi): mittaa pelissä ja katso ilmakuva (`mml_orto/`).

**Koneet**

- Jokainen kone on Meshy-malli → `tee_mallit.py` (rivi `nimi=tiedosto.glb:1024:...`) → rivi `KALUSTEET`-taulukkoon. Prosessi on dokumentoitu valmiiksi `korjaamo/README.md`:ssä.
- Kone näkyy vain, kun sen lippu on päällä: `KALUSTEET`-riville kenttä `lippu: 'KORJ_RENGASKONE'`.
- Toiminnallisuus tehdään talous-tiedoston käsittelijöinä (kuten `korjaa_auto`, `tuunaa`). Esim. `vaihda_renkaat`, `maalaa` (avaa värivalikon, ks. `README.md` 7c: `CarPaint`-materiaali on jo valmis), `pese`.
- Animaatiot pidetään yksinkertaisina, esim. rengaskoneen pöytä pyörii ja maalauskopissa on sumu-sprite (`151_savu.js`), kuten nostimessa.

Ehdotetut Meshy-pyynnöt (Origin = Bottom, koko metreinä, 10–20 k kolmiota):

| Malli | Koko (l × s × k) |
|---|---|
| Rengaskone | 1,0 × 0,9 × 1,6 m |
| Tasapainotuskone | 1,2 × 0,8 × 1,4 m |
| Diagnostiikkakärry näytöllä | 0,6 × 0,5 × 1,5 m |
| Maalauskoppi (sisään ajettava kehikko) | 4,5 × 7,0 × 3,2 m |
| Painepesuri | 0,6 × 0,5 × 0,9 m |
| Hinausauto (ajettava, pakettiauton kokoluokka) | auto-pipeline, kuten muut ajoneuvot (`tools/vehicles/`) |
| Liukuportti ja aitapaneeli | koodissa, ei Meshyä |

**Testaus**

- `tarina/testi.mjs`: uudet tapaukset (osto ilman rahaa → `SYS_NO_MONEY`, osto → nouto → lippu → `korjausKerroin` vaikuttaa `K_KORJAUS`:n hintaan).
- `kokeilu.html`: korjaamo.json:n päivitykset P-valikossa.
- Kuvakaappaukset: `audit/shot.js` tai Modal `shots`-jono kustakin tasosta (0, 1, 1+2, kaikki), jotta ulkoasun muutokset näkee PR:ssä.

### B6. Kytkös viikkotarinoihin

Kun päivitys 5 (toinen nostin) on tehty, viikon uutiset voivat tuoda korjaamolle **asiakastöitä**:
AI valitsee valmiista asiakastyypeistä (renkaat, kolari, huolto, pesu) uutiseen sopivan. Esimerkiksi katuremontti → rengasvaurioita, liukas keli → kolareita, pikkujoulut → "hae asiakkaan auto ravintolan edestä".
Asiakasauto ilmestyy pihalle, ja tehtävä käyttää vain koneita, jotka pelaajalla on. `tarkista.mjs` tarkistaa vaaditut `KORJ_*`-liput.

### B7. Toteutusjärjestys

| # | Tehtävä | Riippuu | Työ |
|---|---|---|---|
| 1 | `korjaamo.json` + lippujen luku `korjaamo.js`:ssä + `K_REMONTTI_*` -tehtävät | – | 1 istunto |
| 2 | Taso 0 rapistuminen ja päivitys 1 (kunnostus, kiinteä katto, valot, oven ääni) | 1 | 1–2 istuntoa |
| 3 | Aita + portti (tontin raja mitataan ensin pelissä) | 1 | 1 istunto + mittaus |
| 4 | Taukotila, diagnostiikka ja painepesuri (pienet, nopeat voitot) | 1 | 1 istunto |
| 5 | Meshy-pyynnöt: rengaskone, tasapainotus, maalauskoppi, kylkiäinen | – | omistaja / mallichat |
| 6 | Rengaskone ja toinen nostin + asiakastyöt | 2, 5 | 1–2 istuntoa |
| 7 | Lisäsiipi ja maalaamo + värivalikko (README 7c) | 3, 5 | 2 istuntoa |
| 8 | Hinausauto (ajoneuvo + koukku) → myös M15 | 3 | 2 istuntoa |
| 9 | Tarinakytkökset (B4) ja kuvakaappaukset, hintojen tasapainotus | kaikki | 1 istunto |

### B8. Päätettävät asiat (omistaja)

1. Hinnat ja kuinka ison osan rahasta korjaamo vie tuunauksesta.
2. Lisäsiiven puoli tontilla ja kylkiäisen malli: Meshyllä vai kopio nykyisestä hallista?
3. Näkyykö vapaassa lennossa rapistunut vai kunnostettu halli? (Ehdotus: kunnostettu.)
4. Rakennetaanko pelillisesti (pelaaja nostaa peltiä paikoilleen), vai riittääkö välianimaatio + fade? (Ehdotus: aluksi fade.)
5. Osa A: mitkä lähteet hyväksytään automaattiseen hakuun, ja sovitaanko aiherajaus kaupungin kanssa.
