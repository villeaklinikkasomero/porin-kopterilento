# Porikopteri – siirtotiedosto: patsaat ja muistomerkit kartalle

Tämä tiedosto on tarkoitettu annettavaksi pelin rakentavalle chatille. Se kuvaa, miten Porin tärkeimmät patsaat ja muistomerkit lisätään pelin karttaan, mitä aineistoa on valmiina ja mitä pitää vielä päättää.

- Laadittu: 19.11.2026 (versio 3, mallit lisätty)
- Lähde: [Luettelo Porin julkisista taideteoksista ja muistomerkeistä (Wikipedia)](https://fi.wikipedia.org/wiki/Luettelo_Porin_julkisista_taideteoksista_ja_muistomerkeist%C3%A4)
- Liite: `porikopteri_patsaat.json` (21 kohdetta koordinaatteineen)

## 1. Tavoite ja rajaus

Kartalla näkyvät Porin tärkeimmät patsaat oikeilla paikoillaan niin, että ne erottuvat helikopterista ja niistä saa tiedot (nimi, tekijä, vuosi), kun pelaaja on lähellä.

**Päätös:** mukaan otetaan vain tärkeimmät vapaasti seisovat teokset. Muistolaattoja, muraaleja, reliefejä, valoteoksia ja rakennusten julkisivuveistoksia ei oteta mukaan.

Toteutus on aineistopohjainen: `porikopteri_patsaat.json` määrää, mitä kartalle tulee, eikä kohteita kirjoiteta käsin pelin koodiin.

## 2. Nykytila

| Asia | Tila |
|---|---|
| Valittu aineisto | 21 kohdetta: 14 maamerkkiä (taso 1) ja 7 muuta (taso 2). Painopiste keskustassa ja Kirjurinluodossa. |
| Lähdeluettelo | Noin 190 kohdetta. Koko sivua ei saatu ladattua, joten valinta on tehty hakutuloksissa näkyneistä riveistä. Luettelossa voi olla tärkeitä teoksia, jotka puuttuvat tästä. |
| 3D-mallit | 11 mallia valmiina GLB-tiedostoina (luku 10). Vapaussodan muistomerkin oma malli puuttuu ja odottaa viitekuvaa. |

Tiedot ovat peräisin hakukoneen näyttämistä luettelon riveistä, eikä niitä ole tarkistettu itse sivulta. Tiedossa olevat epävarmuudet:
- Toriparlamentin vuosi on taulukossa 2008, mutta luettelon johdannossa 1992.
- Punaisten uhrien muistomerkin tekijän etunimi on eri lähteissä Mollu tai Marjo Heino.
- Aurinkolähteen sijainti on luettelossa merkitty likimääräiseksi.
- Vetovoima-teos (Raumansillan kupeessa) jätettiin pois, koska yhden lähteen mukaan se on purettu 2014.

## 3. Aineiston muoto

Jokainen kohde on yksi olio taulukossa `kohteet`:

```json
{
  "id": "patsas_001",
  "nimi": "Satakunnan karhu",
  "paikka": "Raatihuoneenpuisto, Hallituskatu 9 vastapäätä",
  "alue": "Linna",
  "lat": 61.4893,
  "lon": 21.7937,
  "tekija": "Emil Cedercreutz",
  "vuosi": "1938",
  "tyyppi": "patsas",
  "taso": 1,
  "malli": "oma: karhu jalustalla (näköismalli)",
  "suunta_asteet": null,
  "siirto_m": [0, 0]
}
```

- `taso`: 1 = maamerkki (näkyy kauas, oma merkki minikartalla), 2 = muu tärkeä kohde.
- `malli` ja `malli_tiedosto`: mitä 3D-mallia kohde käyttää (luvut 5 ja 10). `huom`: mallia koskeva varaus.
- `suunta_asteet`: mihin suuntaan teos katsoo. Luettelossa tätä tietoa ei ole, joten se täytetään käsin tai lasketaan (luku 4).
- `siirto_m`: käsin annettu korjaus metreinä (itä, pohjoinen), jos kohde osuu väärään paikkaan.
- `vuosi` on merkkijono.

## 4. Sijoitus kartalle

**Rajaus.** Mukaan otetaan vain pelikartan rajojen sisällä olevat kohteet. Kaukaisin valituista on lentoaseman Vampire-muistomerkki, noin 2 km keskustasta etelään.

**Koordinaattimuunnos.** Kohteet pitää muuntaa täsmälleen samalla kaavalla ja samalla origolla kuin kartan rakennukset ja tiet. Jos kartalla ei vielä ole muunnosta, pienelle alueelle riittää:

```js
const R = 6371000, rad = Math.PI / 180;
function karttaan(lat, lon) {                 // LAT0, LON0 = pelikartan origo
  const ita = (lon - LON0) * rad * R * Math.cos(LAT0 * rad);
  const pohjoinen = (lat - LAT0) * rad * R;
  return { x: ita, z: -pohjoinen };           // three.js: +X itä, -Z pohjoinen (tarkista pelin akselit)
}
```

Esimerkki: jos origo olisi kauppatorilla (61.4866, 21.7972), Satakunnan karhu (61.4893, 21.7937) olisi noin 300 m pohjoiseen ja 186 m länteen.

**Tarkkuus.** Luettelon koordinaateissa on neljä desimaalia, eli virhe voi olla noin 5–10 metriä. Siksi:
1. Jos piste osuu rakennuksen tai ajoradan sisään, siirretään se lähimmälle puisto-, aukio- tai jalkakäytäväalueelle.
2. Kirjurinluodon suihkulähde on joessa, joten sitä ei siirretä maalle.
3. Jos tulos on silti väärä, korjataan käsin kentällä `siirto_m`.
4. Keski-Porin kirkon puistossa on kolme kohdetta 20–30 metrin sisällä toisistaan. Ne kannattaa asetella käsin, etteivät ne mene päällekkäin.

**Suunta.** Oletuksena teos katsoo lähimmän kadun tai aukion keskipisteen suuntaan. Maamerkeille suunta annetaan käsin kentässä `suunta_asteet`.

## 5. Mallit

**Näköismallit.** Mallichatti ei tee näköiskopioita olemassa olevista taideteoksista. Poikkeus ovat teokset, joiden tekijän kuolemasta on yli 70 vuotta: Emil Cedercreutz kuoli 1949, joten Satakunnan karhusta ja Vapaussodan muistomerkistä voidaan tehdä tunnistettavat mallit. Muut kohteet esitetään yleismallilla, jonka koko ja jalusta sovitetaan kohteeseen, tai teoksesta hankitaan lupa oikeudenhaltijalta. Tämä on varovainen työoletus eikä oikeudellinen arvio, joten julkaistavaa peliä varten asia kannattaa tarkistaa.

**Tehtävät mallit (10 kpl):**

| Malli | Käyttö |
|---|---|
| Satakunnan karhu (näköismalli) | 1 kohde |
| Vapaussodan muistomerkki (näköismalli, tarvitsee viitekuvan) | 1 kohde |
| Seisova hahmo jalustalla | Juhana-herttua, Eetu Salin, Gallen-Kallela |
| Kolmen hahmon ryhmä | Toriparlamentti |
| Rintakuva jalustalla | Selim Palmgren |
| Abstrakti veistos A, B ja C | Taiteen tammi, Sukkula, Bass String Wings, Siluetti, Dioriittiperhe, Aurinkolähde |
| Tiilirakennelma | Porin portti |
| Muistomerkki (pystykivi laatalla) | sankarihauta, VPK, entiset kirkot, punaisten uhrit, Vampire |
| Ankkuri jalustalla | Kirjurinluodon kärki |
| Suihkulähde vedessä | Kirjurinluodon edusta |

**Mallien käytännöt** (samat kuin muissa Porikopterin malleissa):
- GLB, mitat metreinä, Y ylös, etupuoli +Z-suuntaan, origo maan tasossa jalustan keskellä.
- Tiedostonimet `porikopteri_patsas_<malli>.glb`.
- Tavoite enintään noin 1 500 kolmiota yleismallille ja 5 000 näköismallille, yksi materiaali per malli, jos mahdollista.
- Materiaalit: patinoitu pronssi, graniitti, tiili, teräs. Värin ja koon voi vaihtaa pelistä, jotta sama yleismalli näyttää eri kohteissa erilaiselta.

## 6. Pelitoiminnot

- **Tietokortti:** kun pelaaja on kohteen lähellä (esim. alle 15 m jalan tai leijuu sen yllä), näytetään nimi, tekijä, vuosi ja paikka.
- **Näkyvyys ilmasta:** pieni merkki tai valokeila, joka näkyy kauempaa ja häipyy lähellä. Tason 1 kohteille oma kuvake minikartalla.
- **Keräily (valinnainen):** "patsasbongaus", jossa käydyt kohteet merkitään ja edistyminen tallennetaan.
- **Tekijätiedot:** lähde ja lisenssi (Wikipedia, CC BY-SA 4.0) pelin tekijätietoihin.

## 7. Työnjako ja järjestys

| # | Tehtävä | Kuka |
|---|---|---|
| 1 | Koordinaattimuunnos, rajaus kartan alueelle ja sijoituksen korjaus | pelichatti |
| 2 | Mallit (10 kpl) | mallichatti |
| 3 | Suunnat ja käsikorjaukset maamerkeille | käyttäjä |
| 4 | Mallien lataus, merkit, minikartta ja tietokortit | pelichatti |
| 5 | Tarkistuslento: jokainen maamerkki käydään katsomassa | käyttäjä |

Vaiheet 1 ja 2 voidaan tehdä rinnakkain. Ennen mallien valmistumista kohteet voi näyttää paikkamerkkeinä (esim. harmaa pylväs).

## 8. Avoimet kysymykset

1. Mikä on pelikartan origo (lat, lon) ja rajat, ja mitä muunnosta rakennukset ja tiet käyttävät? (pelichatti)
2. Puuttuuko listasta jokin teos, jonka porilainen odottaisi näkevänsä? (käyttäjä)
3. Halutaanko keräilytoiminto vai pelkät tietokortit? (käyttäjä)
4. Viitekuva Vapaussodan muistomerkistä näköismallia varten. (käyttäjä)

## 9. Valitut kohteet (21)

Sama sisältö on tiedostossa `porikopteri_patsaat.json`.

| # | Nimi | Paikka | lat, lon | Tekijä | Vuosi | Taso | Malli |
|---|---|---|---|---|---|---|---|
| 001 | Satakunnan karhu | Raatihuoneenpuisto, Hallituskatu 9 vastapäätä | 61.4893, 21.7937 | Emil Cedercreutz | 1938 | 1 | oma: karhu jalustalla (näköismalli) |
| 002 | Vapaussodan v. 1918 valkoisten muistomerkki | Keski-Porin kirkon puisto, Hallituskatu 1a | 61.4894, 21.8002 | Emil Cedercreutz | 1920 | 1 | oma (näköismalli, tarvitsee viitekuvan) |
| 003 | Juhana-herttuan patsas | Hallituskatu 9a, Raatihuoneen edusta | 61.4894, 21.7944 | Sofia Saari | 2008 | 1 | yleismalli: seisova hahmo jalustalla |
| 004 | Porin portti | Eteläpuisto | 61.4852, 21.7917 | Per Kirkeby | 1993 | 1 | yleismalli: tiilirakennelma |
| 005 | Toriparlamentti | Kauppatori | 61.4866, 21.7972 | Pertti Mäkinen | 2008 | 1 | yleismalli: kolmen hahmon ryhmä, yksi karhukävelee |
| 006 | Eetu Salinin muistomerkki | Itäpuisto, Isolinnankadun risteyksen lähellä | 61.4850, 21.7990 | Aimo Tukiainen | 1955 | 1 | yleismalli: seisova hahmo jalustalla |
| 007 | Akseli Gallen-Kallelan patsas | Pohjoispuisto | 61.4873, 21.7927 | Heikki Nieminen | 1965 | 1 | yleismalli: seisova hahmo jalustalla |
| 008 | Taiteen tammi | Keskusaukio | 61.4815, 21.7970 | Terho Sakki | 1968 | 1 | yleismalli: abstrakti veistos A |
| 009 | Selim Palmgrenin rintakuva | Raatihuoneenpuisto, Valtakadun ja Pohjoispuiston risteyksen lähellä | 61.4884, 21.7936 | Lauri Leppänen | 1955 | 1 | yleismalli: rintakuva jalustalla |
| 010 | Sukkula | Pohjoisranta 11C–11D vastapäätä | 61.4921, 21.7990 | Kain Tapper | 1958 | 1 | yleismalli: abstrakti veistos B |
| 011 | Sankarihautamuistomerkki, Keski-Porin kirkko | Keski-Porin kirkon puisto, Hallituskatu 1a | 61.4889, 21.8000 | Aimo Tukiainen | 1952 | 1 | yleismalli: muistomerkki |
| 012 | Ankkuri, Porilaisen merenkulun ja satamien muistomerkki | Kirjurinluodon kärki | 61.4919, 21.7934 | – | 1994 | 1 | yleismalli: ankkuri |
| 013 | Kirjurinluodon edustan suihkulähde | Kirjurinluodon kärjen edusta (joessa) | 61.4917, 21.7945 | – | 1969 | 1 | yleismalli: suihkulähde vedessä |
| 014 | Bass String Wings | Jyrki Kankaan aukio, Kapellimestarinkatu | 61.4923, 21.7876 | Pekka ja Teija Isorättyä | 2022 | 1 | yleismalli: abstrakti veistos C |
| 015 | Porin VPK:n 150-vuotismuistomerkki | Porin VPK:n talon (Itäpuisto 13) edusta | 61.4858, 21.7932 | Sofia Saari | 2013 | 2 | yleismalli: muistomerkki |
| 016 | Porin entisten kirkkojen muistomerkki | Satakunnan Museon edusta, Hallituskatu 11 | 61.4898, 21.7914 | – | 1938 | 2 | yleismalli: muistomerkki |
| 017 | Punaisten uhrien muistomerkki | Keski-Porin kirkon puisto, Hallituskatu 1a | 61.4893, 21.7998 | Heino (etunimi lähteissä Mollu tai Marjo) | 2018 | 2 | yleismalli: muistomerkki |
| 018 | Siluetti | Kiertoliittymä Valajankatu–Vanhasahankatu–Hyväntuulentie | 61.4982, 21.8036 | Tapani Söderberg | 2019 | 2 | yleismalli: abstrakti veistos A |
| 019 | Dioriittiperhe | Kuninkaanhaan koulun piha, Kuninkaanhaanaukio 8 | 61.4796, 21.8075 | Jussi Koivusalo | 1961 | 2 | yleismalli: abstrakti veistos B |
| 020 | Aurinkolähde | Asuntomessualue (sijainti likimääräinen) | 61.4908, 21.7624 | Mirja Vallinoja | 2018 | 2 | yleismalli: abstrakti veistos C |
| 021 | Vampire-suihkuhävittäjien muistomerkki | Porin lentoasema | 61.4688, 21.7930 | Marko Tienhaara | 2013 | 2 | yleismalli: muistomerkki |

## 10. Valmiit mallit

Kaikki läpäisivät glTF-validoinnin ilman virheitä. Selaimessa niitä ei ole kokeiltu. Origo on maan tasossa jalustan keskellä, etupuoli +Z-suuntaan, mitat metreinä.

| Tiedosto | Sisältö | Korkeus | Kolmioita | Materiaalit |
|---|---|---|---|---|
| `porikopteri_patsas_karhu.glb` | Karhu neljällä jalalla graniittijalustalla | 2,65 m | 3 000 | Bronze, Granite |
| `porikopteri_patsas_hahmo.glb` | Seisova mieshahmo jalustalla | 3,64 m | 3 500 | Bronze, Granite |
| `porikopteri_patsas_hahmoryhma.glb` | Kolme hahmoa pyöreällä korokkeella: kaksi seisoo, yksi karhukävelee | 2,27 m | 7 600 | Bronze, Granite |
| `porikopteri_patsas_rintakuva.glb` | Rintakuva pylväsjalustalla | 2,49 m | 4 700 | Bronze, Granite |
| `porikopteri_patsas_muistomerkki.glb` | Graniittipaasi pronssilaatalla | 2,19 m | 650 | Granite, Bronze |
| `porikopteri_patsas_ankkuri.glb` | Laiva-ankkuri kivilaatalla | 1,99 m | 620 | Iron, Granite |
| `porikopteri_patsas_abstrakti_a.glb` | Kiertyvä pronssimuoto | 3,39 m | 1 300 | Bronze, Granite |
| `porikopteri_patsas_abstrakti_b.glb` | Kaksi lomittaista teräsrengasta | 3,14 m | 1 500 | Corten, Concrete |
| `porikopteri_patsas_abstrakti_c.glb` | Kaksi kaartuvaa terässiipeä | 3,50 m | 1 700 | Steel, Concrete |
| `porikopteri_patsas_tiiliportti.glb` | Tiilinen portti kaariaukolla (5,2 m leveä) | 4,54 m | 200 | Brick (tekstuuri), Concrete |
| `porikopteri_patsas_suihkulahde.glb` | Kelluva suihkulähde, origo vedenpinnassa | 6,31 m | 1 400 | Iron, Water (läpikuultava) |

Huomioita pelichatille:
- Yleismallit ovat omia sommitelmia eivätkä näytä oikeilta teoksilta. Kohteen tunnistaa tietokortista.
- Karhun asentoa ja jalustaa ei ole verrattu oikeaan Satakunnan karhuun.
- Sama malli on usealla kohteella. Vaihtelua saa skaalaamalla, kääntämällä ja vaihtamalla materiaalin väriä.
- Suihkulähteen vesi on paikallaan. Sen voi korvata pelin omalla hiukkasefektillä.
- Materiaalit ovat metallisia, joten ympäristökartta parantaa ulkonäköä selvästi.
