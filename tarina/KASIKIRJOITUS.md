<!-- Kopio Claude-dokumentista "Satamakaupunki – käsikirjoitus" (https://claude.ai/artifact/YYef6VTmqtmEmZJPU8M6mN, versio 20), viety repoon 21.11.2026,
     jotta käsikirjoitus kulkee mukana myös toiselle Claude-tilille (alkuperäistä dokumenttia ei voi lukea toiselta tililtä).
     TÄMÄ TIEDOSTO ON NYT PÄÄVERSIO: muokkaa tätä, ei dokumenttia. -->

> **Muutokset käsikirjoituksen jälkeen (pelin data on ajantasaisempi kuin tämä teksti):**
> - **M01** (21.11.2026): alkaa jalan Kirjurinluodon nokasta, Taavi-silta → Eteläranta → Tapsan fillari → tori (Terttu, perunat ja sipulit) → Ravintola Vauhtipyörän (Vauhtis) keittiö → korjaamo → Tapsa vetää pressun Ramin vanhan farmarin päältä. Repliikit: `tarina/data/tehtavat/M01.json`.
> - **Keksityt paikat** (omistaja 21.11.2026): ravintolat Vauhtis ja Grilli Kaksi Siivua, Lumin piilo Isosannan vanhassa sähköasemassa, Kiilto ja Satakunnan Varaosa teollisuusalueen halleissa korjaamon vieressä. Kopteri käyttöön vasta M16:ssa.
> - **M02:** Kespan lenkki Mikonkadun valoilta (ei Kirjurinluoto → tori). Ajetaan Ramin farmarilla.
> - **Tapsan korjaamo** on Äestäjänkadulla [-598.9, -443.0], ei joen pohjoispuolella. Paikkojen koordinaatit: `tarina/data/paikat.json`.
> - **Radio Kirjuri** on pelissä kanava "Porikopteri"; vanha "Outojen asioiden toimitus" -konsepti (tapaus 1) on poistettu.
> - Ajoneuvot etenevät tarinassa helpoimmasta vaikeimpaan: pyörä → auto → jalan + auto → drooni → myöhemmin pakettiauto/bussi, vene, kopteri, lentokone ja hyppy.

# Satamakaupunki – käsikirjoitus

Nov 20, 2026 · @Ville

Peli sijoittuu Porin keskustaan ja alkaa Kokemäenjoen Etelärannalta. Käsikirjoituksen tehtävät M01–M26 noudattavat tehtävälistaa, ja ikärajatavoite on PEGI 7.

## Merkinnät

Jokainen tehtävä on kirjoitettu samassa muodossa, jotta sen voi siirtää suoraan moottorin tehtävädataksi (esim. JSON tai YAML). Kenttänimet ovat moottorin kenttiä, ja suomenkieliset repliikit ovat lokalisointiavaimien oletustekstiä.

| Kenttä | Merkitys | Esimerkki |
| --- | --- | --- |
| `ID` | Tehtävän tunniste | `M01` |
| `SIJAINTI` | Aloituspaikan ID (ks. Paikat) | `LOC_ETELARANTA` |
| `VAATII` | Liput, joiden pitää olla päällä ennen avautumista | `FLAG_M01_DONE` |
| `LAUKAISU` | Mikä käynnistää tehtävän | Pelaaja astuu merkkiin |
| `CUT` | Välianimaatio, jossa on oma ID | `CUT_M01_A` |
| `OBJ` | Tavoite, jonka HUD näyttää (numeroitu) | `OBJ 1: Mene Tapsan autolle.` |
| `CP` | Tarkistuspiste, josta epäonnistunut yritys jatkuu | `CP1` |
| `FAIL` | Epäonnistumisehto | Varjo-mittari täyttyy |
| `ASETTAA` | Tehtävän läpäisyn asettamat liput | `FLAG_M01_DONE` |
| `PALKINTO` | Raha, esineet ja avautuvat asiat | 500 € ja Tapsan korjaamo |

**Repliikkien muoto:** `HAHMO_ID (tunne):` repliikki. Tunne ohjaa animaatiota ja ääninäyttelijää. Sallitut arvot: neutraali, iloinen, vihainen, yllättynyt, huolestunut, ovela.

**Toimintarivit** kirjoitetaan *kursiivilla* hakasulkeissa, esim. *\[Kamera kiertää Isosillan yli.\]*

**Varjo-mittari** korvaa wanted-tähdet. Siinä on 0–5 tähteä, ja jahtaajina toimivat Varjon vartijat ja uutiskopterit, eivät koskaan poliisi.

## Hahmot

| ID | Nimi | Rooli | Ääni ja puhetapa |
| --- | --- | --- | --- |
| `RAMI` | Rami Koski | Päähenkilö, entinen rallikuski, 30 v | Rauhallinen, kuiva huumori, vähän sanoja |
| `TAPSA` | Tapani "Tapsa" Laine | Ramin lapsuudenystävä, korjaamon omistaja | Nopea ja äänekäs, ja puheessa kuuluu leveä porilainen murre ("Kyl sää tiärät") |
| `LUMI` | Lumi Aalto | Hakkeri ja porukan suunnittelija | Täsmällinen, sarkastinen, puhuu kuulokkeisiin |
| `HARJU` | Hanna Harju | Varjon talousjohtaja, joka vaihtaa puolta | Kohtelias ja varovainen, omatunto alkaa kolkuttaa |
| `VARJO` | Viktor Varjo | Päävastus, Varjo Holdingsin omistaja | Hymyilevä myyntipuhe, hermostuu pinnan alla |
| `TERTTU` | Terttu Salo | Torikauppias, 70 v, kaupunginosien ääni | Lämmin ja suorasanainen |
| `VARTIJA` | Varjon vartijat (geneerinen) | Jahtaajat | Kankea yritysjargon ("Tilanne on hallinnassa, toistan, hallinnassa") |
| `RADIO` | Radio Kirjuri -juontaja | Taustakertoja, joka uutisoi pelaajan teoista | Pirteä aamujuontaja |

## Paikat

Kartta kattaa Porin keskustan Kokemäenjoen molemmin puolin. Lisäksi mukana on Porin lentoasema, johon keskustasta johtaa tie. Oikeat kohteet näkyvät omilla nimillään, ja keksityt paikat on merkitty taulukkoon. Oikeiden kohteiden ulkonäkö ja käyttö pelissä kannattaa sopia kaupungin kanssa.

| ID | Paikka | Tyyppi | Käyttö pelissä |
| --- | --- | --- | --- |
| `LOC_ETELARANTA` | Eteläranta | Oikea | Pelin aloitus joen rannalla, laituri ja veneet |
| `LOC_ISOSILTA` | Isosilta | Oikea | Joen yli kulkeva pääreitti ja kilpareitin maamerkki |
| `LOC_POHJOISRANTA` | Pohjoisranta | Oikea | Rantabulevardi, takaa-ajot |
| `LOC_TORI` | Kauppatori | Oikea | Tertun kojut, Luku 2:n keskus |
| `LOC_RAATIHUONE` | Vanha raatihuone | Oikea | Kaupungin juhlan näyttö lopussa |
| `LOC_KAUPUNGINTALO` | Junneliuksen palatsi (kaupungintalo) | Oikea | Lupahakemusten toimitus (M08) |
| `LOC_TEATTERI` | Porin teatteri | Oikea | Puvustamo, valepuvut keikkoihin |
| `LOC_KIRKKO` | Keski-Porin kirkko | Oikea | Maamerkki ja korkea näköalapaikka, ei tehtäväkäyttöä |
| `LOC_KIRJURINLUOTO` | Kirjurinluoto | Oikea | Puisto, kesän jazzjuhlat ja finaalin juhla |
| `LOC_ASEMA` | Rautatieasema | Oikea | Tavarajuna (M07) |
| `LOC_LENTOASEMA` | Porin lentoasema | Oikea | Vapaapudotus (M20): terminaali, huoltohalli ja kiitotie |
| `LOC_MUSEO` | Satakunnan Museo | Oikea | Varjon "lainaamat" esineet palautetaan sinne (M13) |
| `LOC_TAIDEMUSEO` | Porin taidemuseo | Oikea | Varjon gaala-ilta (M09) |
| `LOC_KORJAAMO` | Tapsan korjaamo | Keksitty | Porukan tukikohta joen pohjoispuolella |
| `LOC_PIILO` | Lumin piilo | Keksitty | Vanha tiilivarasto joen rannalla |
| `LOC_VARJOTORNI` | Varjo-torni | Keksitty | Varjo Holdingsin lasinen pääkonttori, finaali |
| `LOC_HOTELLI` | Hotelli Varjo | Keksitty | Luksushotelli ja holvi (M14) |
| `LOC_VARASTO` | Varjon varasto | Keksitty | Satamakontit ja Tapsan vankila (M23) |
| `LOC_TEHDAS` | Vanha tehdasalue | Keksitty | Paintball-turnaus (M12) |

## Luku 1: Paluu kotiin

### M01 Tervetuloa takaisin

- `SIJAINTI`: `LOC_ETELARANTA` · `VAATII`: – · `LAUKAISU`: pelin aloitus
- `ASETTAA`: `FLAG_M01_DONE` · `PALKINTO`: Tapsan korjaamo tukikohdaksi ja pelastuskohta

**CUT\_M01\_A: Aamu joella**

*\[Aamuhetki. Kamera liukuu Kokemäenjoen pintaa pitkin Isosillan alta. Pieni jokivene rantautuu Etelärannan laituriin. Rami nousee laiturille kassi olalla.\]*

RADIO (iloinen): Huomenta, Pori! Radio Kirjurissa on taas aamu, ja aurinko paistaa joelle. Kaupungilla kerrotaan, että Varjo Holdings esittelee tänään uuden kauppakeskushankkeensa...

*\[Tapsa nojaa vanhaan farmariautoon laiturin päässä.\]*

TAPSA (iloinen): No kato! Rami Koski. Mitä sää siellä rallimaailmalla teit, unohdit tien kottiin?

RAMI (neutraali): Tulin katsomaan, onko joki vielä paikallaan.

TAPSA (ovela): On se. Mut kaikki muu ei kohta oo. Hyppy kyytiin, mennään korjaamolle.

**Pelattava osuus**

- `OBJ 1`: Kävele Tapsan autolle. *(ohjeistus: liikkuminen ja kamera)*
- `OBJ 2`: Aja korjaamolle Isosillan yli. *(ohjeistus: ajaminen ja kartta, reittiviiva näkyy)* · `CP1`
- `OBJ 3`: Pysäköi korjaamon pihaan merkkiin.

TAPSA (huolestunut, ajon aikana): Varjo ostaa talo kerrallaan. Tertun torikoju, uimarannan kioski, mun korjaamo seuraavana listalla.

RAMI (neutraali): Kuka Varjo?

TAPSA (vihainen): Kyl sää vielä tiärät. Sen kasvot on joka bussipysäkillä.

- `FAIL`: auto romuttuu ("Tapsan auto ei kestänyt") → `CP1`

### M02 Kaksi kuskia

- `SIJAINTI`: `LOC_KORJAAMO` · `VAATII`: `FLAG_M01_DONE` · `LAUKAISU`: puhu Tapsalle
- `ASETTAA`: `FLAG_M02_DONE` · `PALKINTO`: 200 €, radiokanavan valinta, kilpa-ajot avautuvat kartalle

TAPSA (ovela): Katotaan, oot sää vielä nopee. Korjaamolta Kirjurinluodon kautta torille. Häviiäjä tarjoaa makkaraperät.

- `OBJ 1`: Voita Tapsa kilpa-ajossa torille. 8 tarkistusporttia: Pohjoisranta → Kirjurinluodon silta → Isosilta → Kauppatori.
- `FAIL`: Tapsa ehtii maaliin ensin ("Tapsa voitti tällä kertaa") → uusi lähtö

TAPSA (yllättynyt, maalissa): No niin, ei oo ruoste vielä vienyt. Sun valinta, radio vai mun mixtape?

*\[Pelaaja valitsee oletusradiokanavan. Valinta tallennetaan muuttujaan `VAR_RADIO_DEFAULT`.\]*

### M03 Takaisinhaku

- `SIJAINTI`: `LOC_KORJAAMO` · `VAATII`: `FLAG_M02_DONE` · `LAUKAISU`: puhelu Tapsalta
- `ASETTAA`: `FLAG_M03_DONE` · `PALKINTO`: 300 € ja hiiviskelykyky avautuu

TAPSA (vihainen, puhelimessa): Autoliike Kiilto myi kahdelle mun asiakkaalle autot ja vei ne sit takasin "maksuhäiriön" takia. Paperit on kunnossa, autot vaan on väärässä paikassa.

- `OBJ 1`: Mene Autoliike Kiillon pihaan.
- `OBJ 2`: Hiivi myyjän ohi ja ota avaimet toimistosta. *(ohjeistus: hiiviskely ja näkökartiot)* · `CP1`
- `OBJ 3`: Aja molemmat autot korjaamolle. Varjo-mittari: 1 tähti. · `CP2`
- `FAIL`: myyjä huomaa pelaajan ennen avaimia → `CP1`

MYYJÄ (vihainen, jos huomaa pelaajan): Hei! Tää on yksityisalue!

RAMI (ovela, läpäisyssä): Kaupat purettu.

### M04 Korjaamon puolustus

- `SIJAINTI`: `LOC_KORJAAMO` · `VAATII`: `FLAG_M03_DONE` · `LAUKAISU`: palaa korjaamolle
- `ASETTAA`: `FLAG_M04_DONE` · `PALKINTO`: vesiletku ja sammutin varusteiksi

**CUT\_M04\_A**

*\[Kolme Varjon vartijaa seisoo korjaamon pihalla. Yksi kiinnittää oveen keltaista "Purkukohde"-tarraa.\]*

VARTIJA (neutraali): Kiinteistö siirtyy Varjo Holdingsin hallintaan. Tilanne on hallinnassa. Toistan: hallinnassa.

TAPSA (vihainen): Kohta on märkääkin hallinnassa. Rami, letku!

- `OBJ 1`: Aja vartijat pois pihalta vesiletkulla ja sammutinvaahdolla. *(osuma → vartija liukastuu, nousee ja pakenee. Ei vahinkoa.)*
- `OBJ 2`: Revi purkutarra ovesta.
- `FAIL`: vartijat saavat tarrat kaikkiin kolmeen oveen → uusi yritys

VARTIJA (huolestunut, paetessa): Vetäydytään! Pukuni on märkä!

### M05 Pikkukopteri

- `SIJAINTI`: `LOC_KORJAAMO` · `VAATII`: `FLAG_M04_DONE` · `LAUKAISU`: tuntematon tekstiviesti
- `ASETTAA`: `FLAG_M05_DONE` · `PALKINTO`: drooni ja Lumin yhteystieto

*\[Tekstiviesti tuntemattomasta numerosta: "Haluatko tietää, mitä Varjo rakentaa? Ota laatikko ovelta." Ovella on laatikko, jossa on drooni.\]*

- `OBJ 1`: Lennä drooni Varjo-tornin työmaalle.
- `OBJ 2`: Kuvaa kolme suunnitelmataulua. `CP1` jokaisen kuvan jälkeen.
- `OBJ 3`: Lennä takaisin ennen kuin akku loppuu (90 s).
- `FAIL`: akku loppuu tai drooni törmää kolmesti → viimeisin `CP`

LUMI (ovela, kuulokkeissa): Hyvä. Varo nosturia. Ei, toista nosturia.

### M06 Vanha ystävä

- `SIJAINTI`: `LOC_PIILO` · `VAATII`: `FLAG_M05_DONE` · `LAUKAISU`: mene kartan merkkiin
- `ASETTAA`: `FLAG_M06_DONE`, `FLAG_CH1_DONE` · `PALKINTO`: Luku 2 avautuu ja Lumin piilo pelastuskohdaksi

**CUT\_M06\_A**

*\[Vanha tiilivarasto joen rannalla. Sisällä näyttöjä ja kaapeleita. Lumi kääntyy tuolissaan.\]*

LUMI (neutraali): Rami Koski. Sinulla on hyvät refleksit ja huono tapa olla väärässä paikassa. Se sopii minulle.

RAMI (neutraali): Sinä lähetit droonin.

LUMI (ovela): Ja sinä lennätit sen. Katso.

*\[Näytöllä näkyy Varjon suunnitelma: tori, rantapuistot ja Kirjurinluoto kauppakeskuksen alla.\]*

LUMI (vihainen): Varjo ostaa maat väärennetyillä papereilla. Jos todistamme sen, kaikki kaupat purkautuvat.

TAPSA (iloinen): Elikkä tehdään keikka?

LUMI (ovela): Tehdään monta.

## Luku 2: Kaupunginosat takaisin

Luvun tehtävät M08–M12 avautuvat kaikki kerralla, kun M07 on läpäisty. Jokainen läpäisty tehtävä värittää kartalta yhden alueen sinisestä väristä (Varjo) keltaiseksi (asukkaat). Muuttuja: `VAR_AREAS_SAVED` 0–5.

### M07 Tavarajuna

- `SIJAINTI`: `LOC_ASEMA` · `VAATII`: `FLAG_CH1_DONE` · `ASETTAA`: `FLAG_M07_DONE`, `ITEM_KAUPPAKIRJAT_1`

LUMI (ovela): Varjo lähettää alkuperäiset kauppakirjat Helsinkiin tavarajunassa. Kansio on viimeisen vaunun avoimella lavalla.

TAPSA (iloinen): Mää ajan, sää nappaat. Mul on haavi takakontissa.

- `OBJ 1`: Hypää Tapsan avoautoon asemalla.
- `OBJ 2`: Pysy junan rinnalla radan viereisellä huoltotiellä (etäisyysmittari). · `CP1`
- `OBJ 3`: Nappaa kansio haavilla, kun mittari on vihreällä (ajoitusnappi).
- `FAIL`: juna ehtii kaupungin rajalle → `CP1`

TAPSA (yllättynyt): Saatiin se! Kalastan tästä lähtien vaan paperia.

### M08 Toripaniikki

- `SIJAINTI`: `LOC_TORI` · `VAATII`: `FLAG_M07_DONE` · `ASETTAA`: `FLAG_M08_DONE`, `VAR_AREAS_SAVED +1`

TERTTU (huolestunut): Varjo sai meijjän torilupien uusinnat "hukkumaan". Hakemukset pitää olla kaupungintalolla neljältä, tai torikesä on mennyttä.

- `OBJ 1`: Kerää hakemukset viideltä kojulta torilla.
- `OBJ 2`: Vie ne Junneliuksen palatsiin ennen kuin kello on 16.00 (pelin kello, 3 min). Jokainen törmäys pudottaa yhden hakemuksen tielle, ja sen voi poimia takaisin.
- `FAIL`: aika loppuu → uusi yritys

TERTTU (iloinen, läpäisyssä): Pojat, huomenna kahvit talon piikkiin.

### M09 Gaala-ilta

- `SIJAINTI`: `LOC_TEATTERI` → `LOC_TAIDEMUSEO` · `VAATII`: `FLAG_M07_DONE` · `ASETTAA`: `FLAG_M09_DONE`, `VAR_AREAS_SAVED +1`

LUMI (ovela): Varjo pitää sijoittajagaalan taidemuseolla. Hae teatterin puvustamosta frakki ja nimeä itsesi joksikin, mikä kuulostaa rahalta.

- `OBJ 1`: Hae valepuku Porin teatterin puvustamosta.
- `OBJ 2`: Pääse ovimiehen ohi. Dialogivalinta: \["Olen Kuusinen-sijoitusten edustaja."\] / \["Tulin korjaamaan kaiuttimia."\] / \["Olen taiteilija."\] Kaikki pääsevät sisään, mutta seuraava osuus muuttuu valinnan mukaan.
- `OBJ 3`: Seuraa Varjoa salissa ja pysy kuuloetäisyydellä (kuuntelumittari 100 %). · `CP1`
- `FAIL`: Varjo huomaa pelaajan kolme kertaa → `CP1`

VARJO (ovela, sijoittajille): Pori saa kauppakeskuksen, jollaista ei ole nähty. Kukaan ei kaipaa vanhaa toria, kun on liukuportaat.

HARJU (huolestunut, hiljaa): Viktor, ne kauppakirjat... eikö niissä ollut jotain epäselvää?

VARJO (vihainen): Hanna. Hymyile.

### M10 Pienoislentokone

- `SIJAINTI`: `LOC_KORJAAMO` · `VAATII`: `FLAG_M09_DONE` · `ASETTAA`: `FLAG_M10_DONE`, `VAR_AREAS_SAVED +1`
- `OBJ 1`: Ohjaa RC-lentokonetta Pohjoisrannan yllä.
- `OBJ 2`: Pudota lähetin kolmen Varjon kuorma-auton katolle liikkeessä.
- `FAIL`: lentokone törmää tai polttoaine loppuu (120 s) → uusi yritys

LUMI (iloinen): Signaali on kunnossa. Nyt näemme, minne Varjo vie tavaransa.

### M11 Sillankilpa

- `SIJAINTI`: `LOC_ISOSILTA` · `VAATII`: `FLAG_M07_DONE` · `ASETTAA`: `FLAG_M11_DONE`, `ITEM_KULKUKORTTI`, `VAR_AREAS_SAVED +1`

RADIO (iloinen): Kaupungin syysajot käynnistyvät! Reitti on suljettu muulta liikenteeltä, ja yhtenä kuljettajana on Varjo Holdingsin oma kuski!

- `OBJ 1`: Voita kolmen kierroksen kilpa: Isosilta → Eteläranta → Pohjoisranta.
- `OBJ 2`: Maalissa Varjon kuski pudottaa kulkukorttinsa. Poimi se.
- `FAIL`: sijoitus heikompi kuin 1. → uusi yritys

RAMI (neutraali): Hyvä auto. Huono kuski.

### M12 Paintball-turnaus

- `SIJAINTI`: `LOC_TEHDAS` · `VAATII`: `FLAG_M08_DONE`, `FLAG_M10_DONE` · `ASETTAA`: `FLAG_M12_DONE`, `FLAG_CH2_DONE`, `VAR_AREAS_SAVED +1`

TAPSA (ovela): Varjo osti nuorisotalon ja haastaa sen avaimista. Paintball, kaks joukkuetta, kolme erää. Ei mikään ongelma.

- `OBJ 1`: Voita kaksi kolmesta erästä (lipun ryöstö -pelimuoto). Värijälki jää pinnoille, ja osuman saanut pelaaja palaa lähtöön.
- `FAIL`: kaksi hävittyä erää → uusi turnaus

VARTIJA (yllättynyt): Minuun osui. Toistan: minuun osui.

RADIO (iloinen): Nuorisotalon avaimet palasivat nuorille! Varjolle ei tänään mennyt hyvin.

## Luku 3: Isot keikat

Jokainen keikka kulkee samassa rytmissä: suunnittelu Lumin piilossa, 1–2 valmistelutehtävää ja itse keikka. Pelaaja valitsee suunnittelutaululta tavan, joka tallentuu muuttujaan `VAR_APPROACH_Mxx` = `HILJAINEN` | `AANEKAS`. Kumpikin tapa on aina läpäistävissä ilman vahinkoja.

**CUT\_CH3\_A: suunnittelutaulu (käytetään jokaisessa keikassa)**

*\[Lumin piilo. Valkotaululle on kiinnitetty kuvia ja karttoja. Kamera zoomaa kohteeseen.\]*

LUMI (ovela): Kaksi tapaa. Hiljainen: kukaan ei huomaa mitään. Äänekäs: kaikki huomaavat, mutta liian myöhään.

### M13 Korukeikka

- `SIJAINTI`: `LOC_VARJOTORNI` (näyttelykerros) · `VAATII`: `FLAG_CH2_DONE` · `ASETTAA`: `FLAG_M13_DONE`, museoesineet palautettu
- Valmistelu `M13_PREP`: hae tuholaistorjujan haalarit ja pakettiauto (`HILJAINEN`) tai moottoripyörät Tapsan korjaamolta (`AANEKAS`).

LUMI (vihainen): Varjo "lainasi" Satakunnan Museolta vanhat hopeakorut omaan näyttelyynsä. Laina-aika on päättynyt, ja palautamme ne.

- `OBJ 1` (`HILJAINEN`): Mene sisään tuholaistorjujana. Käynnistä saippuakuplakone, joka saa vartijat jahtaamaan kuplia, ja kerää 6 vitriiniä.
- `OBJ 1` (`AANEKAS`): Laukaise värilliset savuverhot, kerää 6 vitriiniä 90 sekunnissa.
- `OBJ 2`: Pakene ja vie korut museon takaovelle. Varjo-mittari: 2 (`HILJAINEN`) / 4 (`AANEKAS`). · `CP1`
- `FAIL`: kiinni jääminen → `CP1`

RADIO (iloinen): Satakunnan Museon kadonneet korut löytyivät aamulla ovelta pakattuina rusetilla!

### M14 Hotelli-ilta

- `SIJAINTI`: `LOC_HOTELLI` · `VAATII`: `FLAG_M13_DONE`, `ITEM_KULKUKORTTI` · `ASETTAA`: `FLAG_M14_DONE`, `ITEM_KAUPPAKIRJAT_2`
- Valmistelut: `M14_PREP_A` hae hotellin henkilökunnan asut teatterilta. `M14_PREP_B` Lumi hakkeroi kamerat (minipeli: yhdistä johdot).
- `OBJ 1`: Kulje hotellin aulan läpi henkilökunnan asussa ja tarjoile kolmelle vieraalle (naamioitumismittari).
- `OBJ 2`: Avaa holvi kulkukortilla ja Lumin koodilla (rytmiminipeli). · `CP1`
- `OBJ 3`: Vie kauppakirjat ulos pyykkikärryssä.
- `FAIL`: naamioitumismittari tyhjenee → `CP1`

HARJU (yllättynyt, käytävällä): Te ette ole hotellin henkilökuntaa.

RAMI (neutraali): Emme.

HARJU (huolestunut, hetken tauko): ...Toinen ovi vasemmalla on nopeampi.

*\[Asettaa muuttujan `FLAG_HARJU_DOUBT`. Vaikuttaa loppuun C.\]*

### M15 Panssariauto

- `SIJAINTI`: `LOC_POHJOISRANTA` · `VAATII`: `FLAG_M14_DONE` · `ASETTAA`: `FLAG_M15_DONE`, `ITEM_TALLENTEET`

TAPSA (iloinen): Varjon panssariauto kuljettaa kokoustallenteet. Magneetti kiinni, ja Lumi sammuttaa moottorin kauko-ohjauksella. Kukaan ei ees huomaa.

- `OBJ 1`: Aja hinausautolla panssariauton perään Pohjoisrannalla.
- `OBJ 2`: Kiinnitä magneetti (ajoitusnappi, kun etäisyys on alle 3 m). · `CP1`
- `OBJ 3`: Hinaa panssariauto korjaamolle. Kuljettaja nousee ulos ja lähtee kävelemään kotiin, eikä hänelle tapahdu mitään.
- `FAIL`: panssariauto pakenee joen yli → `CP1`

### M16 Satamalaituri

- `SIJAINTI`: `LOC_VARASTO` · `VAATII`: `FLAG_M15_DONE` · `ASETTAA`: `FLAG_M16_DONE`, `ITEM_PIENOISMALLI`

LUMI (ovela): Varjon kontissa on kauppakeskuksen pienoismalli ja kokousmuistiot. Kontti on liian painava autolle, joten se nostetaan ilmaan.

- `OBJ 1`: Hae helikopteri Lumin tuttavalta Etelärannan laiturilta. *(ohjeistus: lentäminen)*
- `OBJ 2`: Laske vaijeri ja kiinnitä kontti (tarkkuuslasku). · `CP1`
- `OBJ 3`: Lennä kontti joen yli Lumin piilolle. Kontti heiluu tuulessa, joten vältä nostureita.
- `FAIL`: kontti osuu maahan kolmesti → `CP1`

### M17 Pilvenpiirtäjä

- `SIJAINTI`: `LOC_VARJOTORNI` · `VAATII`: `FLAG_M16_DONE` · `ASETTAA`: `FLAG_M17_DONE`, `FLAG_CH3_DONE`, `ITEM_PALVELINDATA`
- Tapa: `HILJAINEN` = siivoojiksi soluttautuminen. `AANEKAS` = laskuvarjohyppy katolle helikopterista.
- `OBJ 1`: Pääse tornin 12. kerrokseen.
- `OBJ 2`: Suojaa Lumia 60 s, kun hän kopioi palvelimen. Ohjaa vartijat harhaan äänillä ja hissien kutsunapeilla. · `CP1`
- `OBJ 3`: Poistu tornista: käytä pyykkikuilua (`HILJAINEN`) tai liidä joen yli ja laskeudu Kirjurinluodolle (`AANEKAS`).
- `FAIL`: vartija ehtii palvelinhuoneeseen → `CP1`

LUMI (yllättynyt): Sain sen. Ja löysin jotain muutakin. Varjo tietää, kuka te olette.

## Luku 4: Petos

Koska maaseutua ei ole kartalla, tehtävälistan maaseutuosuus on siirretty joelle, ja M19 on nyt "Piilossa joella". M20 "Vapaapudotus" tapahtuu Porin lentoasemalla.

### M18 Ansa

- `SIJAINTI`: `LOC_TORI` · `VAATII`: `FLAG_CH3_DONE` · `ASETTAA`: `FLAG_M18_DONE`, `FLAG_TAPSA_CAPTURED`

**CUT\_M18\_A**

*\[Ilta torilla. Varjo seisoo kojujen keskellä hymyillen. Kameramiehiä on joka puolella.\]*

VARJO (ovela): Rami Koski! Ja hänen kummallisesti kadonneet museokorunsa. Hups, tarkoitin minun.

*\[Varjon vartijat nostavat Tapsan auton takakontista "varastettuja" esineitä. Ne ovat väärennettyjä kopioita. Uutiskopteri kuvaa.\]*

TAPSA (vihainen): Rami, ne on feikkejä! Juokse!

- `OBJ 1`: Pakene torilta. Varjo-mittari: 5 tähteä.
- `OBJ 2`: Karista Varjo-mittari. Vinkki: kulje sillan alta ja pysy uutiskopterin katveessa. · `CP1`
- `OBJ 3`: Mene Lumin piilolle.
- `FAIL`: kiinni jääminen → `CP1`

LUMI (huolestunut): Tapsa on poissa. Ja koko kaupunki luulee sinua varkaaksi. Sinun pitää kadota hetkeksi.

### M19 Piilossa joella

- `SIJAINTI`: `LOC_ETELARANTA` (venevaja) · `VAATII`: `FLAG_M18_DONE` · `ASETTAA`: `FLAG_M19_DONE`, `VAR_ALLIES +3`

TERTTU (iloinen): Mun miehen vanha venevaja. Kukaan ei ole käynyt siellä sitten -98. Korjaa itsellesi vene, niin pääset liikkumaan joella.

- `OBJ 1`: Korjaa vene (osien keräys rannalta, 4 kpl).
- `OBJ 2`: Auta kolmea rantalaista: kalastajan verkko, kadonnut koira ja soutukilpa joella. Jokainen apu nostaa `VAR_ALLIES` +1.

RADIO (huolestunut): Huhut Rami Koskesta jakavat kaupunkia. Torikauppiaat sanovat, että hän on hyvä poika.

### M20 Vapaapudotus

- `SIJAINTI`: `LOC_LENTOASEMA` · `VAATII`: `FLAG_M19_DONE` · `ASETTAA`: `FLAG_M20_DONE`, `ITEM_KOPIOTODISTE` · `PALKINTO`: laskuvarjo varusteeksi ja laskuvarjohypyt sivutehtäviksi

LUMI (huolestunut): Varjon kuriiri vie todisteet väärennöksistä Varjon yksityiskoneella pois maasta. Kone lähtee lentoasemalta viidentoista minuutin päästä.

RAMI (neutraali): Sitten se ei lähde.

LUMI (ovela): Se lähtee. Mutta se tulee takaisin. Minulla on suunnitelma. Toivottavasti sinulla ei ole korkean paikan kammoa.

- `OBJ 1`: Aja keskustasta lentoasemalle (aikaraja 3 min). Kone rullaa kiitotielle juuri kun saavut.
- `OBJ 2`: Mene huoltohalliin, jossa Lumin tuttava odottaa helikopterin kanssa. · `CP1`
- `OBJ 3`: Seuraa konetta ilmassa ja pysy etäisyysmittarin vihreällä alueella 60 s, kunnes Lumi saa yhteyden koneen autopilottiin. · `CP2`
- `OBJ 4`: Kone kääntyy takaisin. Hyppää helikopterista ja laskeudu laskuvarjolla kiitotien merkkiin ennen kuin kone laskeutuu (tarkkuuslasku). *(ohjeistus: laskuvarjo)* · `CP3`
- `OBJ 5`: Ota salkku kuriirilta koneen portailla.
- `FAIL`: kone ehtii lähteä ennen saapumistasi, etäisyys katkeaa yli 10 s tai laskeudut kiitotien ulkopuolelle → viimeisin `CP`

KURIIRI (yllättynyt, portailla): Kone kääntyi itsestään ympäri. Ja sinä tulit taivaalta.

RAMI (ovela): Salkku, kiitos.

KURIIRI (huolestunut): ...Ihan reilua. En minä edes pidä lentämisestä.

RADIO (iloinen): Porin lentoasemalla nähtiin tänään laskuvarjohyppy kiitotielle. Lentoaseman mukaan kenelläkään ei ole hätää, ja lennot jatkuvat normaalisti.

### M21 Neuvottelu

- `SIJAINTI`: `LOC_VARJOTORNI` (kattoravintola) · `VAATII`: `FLAG_M20_DONE` · `ASETTAA`: `FLAG_M21_DONE`, `VAR_VARJO_CONFESSION` 0–3

VARJO (ovela): Rami. Istu. Tarjoan sinulle sitä, mitä kukaan ei voi kieltäytyä: kauppakeskuksen hienoimman liiketilan.

- `OBJ 1`: Dialogipeli, kolme kierrosta. Jokaisella kierroksella pelaaja valitsee bluffin, joka joko saa Varjon kertomaan jotain (`VAR_VARJO_CONFESSION +1`) tai ärsyttää hänet.
  - Kierros 1: \["Tapsalla on muitakin kavereita."\] / \["Ehkä haluan liiketilan."\] / \["Lumi näkee kaiken."\]
  - Kierros 2: \["Kauppakirjat on jo lehdistöllä."\] / \["Harju ei ole puolellasi."\] / \["Mitä jos torilla ei olekaan kauppakeskusta?"\]
  - Kierros 3: \["Missä Tapsa on?"\] (paljastaa aina varaston sijainnin)
- `FAIL`: ei epäonnistumista. Tulos vaikuttaa finaalin vaikeuteen.

VARJO (vihainen, lopuksi): Tapsasi on turvassa varastollani. Niin kauan kuin sinä olet hiljaa.

### M22 Salainen hanke

- `SIJAINTI`: `LOC_VARASTO` (kellarilaboratorio) · `VAATII`: `FLAG_M21_DONE` · `ASETTAA`: `FLAG_M22_DONE`, `ITEM_LENTOREPPU`
- `OBJ 1`: Hiivi varaston kellariin. Väistä hälytyslaserit tai sammuta ne sähkökaapista.
- `OBJ 2`: Ota prototyyppilentoreppu. *(ohjeistus: lentoreppu)*
- `OBJ 3`: Lennä ulos kattoikkunasta. · `CP1`

### M23 Tapsan vapautus

- `SIJAINTI`: `LOC_VARASTO` · `VAATII`: `FLAG_M22_DONE` · `ASETTAA`: `FLAG_M23_DONE`, `FLAG_CH4_DONE`, `FLAG_TAPSA_CAPTURED = false`
- `OBJ 1`: Lennä lentorepulla kattoikkunalle.
- `OBJ 2`: Valitse tapa: harhauta vartijat kauko-ohjattavalla autolla (hiljainen) tai kytke päälle kaikki varaston kaiuttimet ja valot (äänekäs).
- `OBJ 3`: Avaa Tapsan varastohuoneen lukko (tiirikkaminipeli) ja pakene yhdessä.

TAPSA (iloinen): Mitä sulla on selkässä? Hetkinen. Mul on kysymyksiä. Ja haluun kokeilla.

## Luku 5: Finaali

Järjestys on M24 → M25 (valinta) → M26 (versio valinnan mukaan) → lopetusanimaatio `END_A`, `END_B` tai `END_C`. Finaali sijoittuu kaupungin syysjuhlan iltaan, jolloin tori ja Kirjurinluoto ovat täynnä ihmisiä.

### M24 Iso keikka

- `SIJAINTI`: `LOC_VARJOTORNI` · `VAATII`: `FLAG_CH4_DONE`, `ITEM_KAUPPAKIRJAT_1`, `ITEM_KAUPPAKIRJAT_2`, `ITEM_TALLENTEET`, `ITEM_PALVELINDATA` · `ASETTAA`: `FLAG_M24_DONE`, `ITEM_ALKUPERAISET`

**CUT\_M24\_A**

*\[Lumin piilo. Koko porukka on koolla: Rami, Tapsa, Lumi, Terttu ja ne rantalaiset, joita Rami auttoi M19:ssä (määrä = `VAR_ALLIES`).\]*

LUMI (ovela): Meillä on kopiot kaikesta. Mutta alkuperäiset väärennetyt kauppakirjat ovat Varjon omassa kassakaapissa, 20. kerroksessa. Ilman niitä Varjo kiistää kaiken.

TERTTU (iloinen): Me torilaiset hoidetaan harhautus. Kukaan ei vartioi ovia, kun ilmaisia munkkeja jaetaan.

- `OBJ 1`: Terttu ja liittolaiset harhauttavat vartijat (animaatio, kesto `VAR_ALLIES` × 10 s).
- `OBJ 2`: Tapsa: aja pakettiauto lastauslaiturille (pelaaja ohjaa Tapsaa). · `CP1`
- `OBJ 3`: Rami: nouse 20. kerrokseen. Vartijoiden määrä = 6 − `VAR_VARJO_CONFESSION`. · `CP2`
- `OBJ 4`: Avaa kassakaappi (Lumin ohjaama kolmivaiheinen minipeli). · `CP3`
- `FAIL`: kiinni jääminen → viimeisin `CP`

### M25 Valinta

- `SIJAINTI`: `LOC_VARJOTORNI` (Varjon toimisto) · `ASETTAA`: `VAR_ENDING` = `A` | `B` | `C`

**CUT\_M25\_A**

*\[Rami avaa kassakaapin. Takana on Harju, kansio kädessä.\]*

HARJU (huolestunut): Minä tiedän, mitä noissa lukee. Allekirjoitin osan itse.

HARJU (neutraali): Antakaa ne minulle. Varjo luopuu hankkeesta hiljaisesti, eikä kukaan joudu ongelmiin. Myöskään minä.

LUMI (ovela, kuulokkeissa): Tai näytämme ne koko kaupungille. Juhlassa on iso näyttö torilla.

- Valinta A: \["Ota ne. Kunhan tori säilyy."\] → `VAR_ENDING = A`
- Valinta B: \["Kaupunki ansaitsee tietää."\] → `VAR_ENDING = B`
- Valinta C (näkyy vain, jos `FLAG_HARJU_DOUBT` on päällä): \["Tule meidän puolellemme. Kerro itse."\] → `VAR_ENDING = C`

### M26 Viimeinen takaa-ajo

- `SIJAINTI`: `LOC_VARJOTORNI` → Kokemäenjoki → `LOC_KIRJURINLUOTO` · `ASETTAA`: `FLAG_GAME_COMPLETE`

*\[Varjo tajuaa, mitä on tapahtunut, ja yrittää paeta yksityisveneellään ennen kuin totuus leviää.\]*

VARJO (vihainen): Ette te mitään todista! Ilman minua tämä kaupunki on pelkkä vanha tori ja joki!

RAMI (neutraali): Hyvä tori. Hyvä joki.

- `OBJ 1`: Aja tornilta Etelärannan laiturille. Varjo-mittari: 5.
- `OBJ 2`: Seuraa Varjon venettä joella. · `CP1`
- `OBJ 3`: Ohjaa vene Kirjurinluodon rantaan, jossa juhlakansa odottaa.
- Versioerot: **A** = Varjon vene pääsee karkuun joen suulle. **B** = vene juuttuu matalikolle Kirjurinluodolla, juhlakansan katsellessa. **C** = Harju on jo soittanut poliisille, ja poliisivene odottaa joen mutkassa.
- `FAIL`: Varjo katoaa näköpiiristä 30 sekunniksi → `CP1`

### Loput

**END\_A: Hyvä sopimus**

*\[Aamu torilla. Kojut auki. Varjo-tornin kyltti puretaan. Radio puhuu taustalla.\]*

RADIO (iloinen): Varjo Holdings ilmoitti peräytyvänsä kauppakeskushankkeesta. Viktor Varjo ei ole tavoitettavissa kommentteja varten, ja hänen kerrotaan lähteneen pitkälle lomalle.

TAPSA (huolestunut): Ja jos se tulee takas?

RAMI (ovela): Sitten tiedämme, mistä hänet löytää.

*\[Jatko-osan vihje: postikortti ulkomailta, allekirjoitus V.\]*

**END\_B: Kaikki julki**

*\[Juhlan iso näyttö torilla. Lumi painaa nappia. Näytölle ilmestyvät väärennetyt allekirjoitukset. Juhlakansa haukkoo henkeään.\]*

RADIO (yllättynyt): Ennenkuulumatonta! Viktor Varjo saapui poliisilaitokselle vastaamaan kysymyksiin kauppakirjoista. Myös talousjohtaja Hanna Harjun osuutta selvitetään.

TERTTU (iloinen): Kahvit koko kaupungille!

**END\_C: Kolmas tie (paras loppu)**

*\[Harju astuu juhlan lavalle mikrofoni kädessä.\]*

HARJU (huolestunut → iloinen): Minä olen Hanna Harju. Työskentelin Varjo Holdingsille. Tänään kerron, mitä näin.

*\[Ruudun ulkopuolella: poliisi saattaa Varjon pois veneeltä. Kaupunki ilmoittaa ostavansa purettavaksi aiotut paikat asukkaiden käyttöön. Ilotulitus Kokemäenjoen yllä.\]*

LUMI (iloinen): Seuraavaksi pitää keksiä, mitä tehdä tälle kaikelle vapaa-ajalle.

TAPSA (iloinen): Kyl sää tiärät. Sillankilpa.

*\[Lopputekstit. Kamera nousee Kirjurinluodolta joen yli koko keskustan näkymään.\]*

## Järjestelmätekstit

| Avain | Teksti |
| --- | --- |
| `SYS_FAIL_CAUGHT` | Ammattilaisia ei jää kiinni. Yritä uudelleen? |
| `SYS_FAIL_TIME` | Aika loppui. Kello ei odota ketään, ei edes Ramia. |
| `SYS_FAIL_VEHICLE` | Kulkuneuvo ei kestänyt. Tapsa korjaa sen, mutta ei ilahdu. |
| `SYS_FAIL_SPOTTED` | Sinut huomattiin. Hiiviskely onnistuu paremmin varjoissa. |
| `SYS_RETRY` | Jatka tarkistuspisteestä |
| `SYS_MISSION_PASSED` | KEIKKA ONNISTUI |
| `SYS_AREA_SAVED` | Alue pelastettu! Asukkaat kiittävät. |
| `SYS_VARJO_METER_UP` | Varjon väki on kannoillasi. |
| `SYS_VARJO_METER_LOST` | Karistit jahtaajat. |
| `SYS_SAVE` | Tallennetaan... Älä sammuta laitetta. |
| `SYS_COLLECTIBLE` | Löysit lokkipatsaan! (`{n}`/50) |
| `SYS_FACT_POPUP` | Tiesitkö? `{fact_text}` *(kohdekohtainen tietoisku, teksti sovitaan kaupungin kanssa)* |

**Latausruutujen vihjeet:**

- Isosilta on nopein reitti joen yli, mutta Kirjurinluodon kautta pääset jahtaajilta piiloon.
- Varjo-mittari laskee nopeammin, kun pysyttelet poissa uutiskopterin näköpiiristä.
- Tapsan korjaamolla auto korjaantuu ilmaiseksi. Tapsa ei sano mitään. Melkein.
- Torin kojuilta saa voimaa palauttavia herkkuja.
- Jokainen pelastettu alue avaa uuden sivutehtäviksi.
