# Porikopteri – siirtotiedosto: pyöräily

Laadittu 20.11.2026 (versio 3: kyytiläinen ja kallistus lisätty). Peliin tarvitaan nämä tiedostot:

| Tiedosto | Sisältö |
|---|---|
| `porikopteri_pyora.glb` | Polkupyörä (5 200 kolmiota, 175 kt), ei animaatioita. Uutta: istuinpehmuste `RackPad`. |
| `porikopteri_hahmo.glb` | Pelaajahahmo, jossa on uusi `Cycle`-animaatio. Korvaa aiemman hahmotiedoston; muut animaatiot (`Idle`, `Walk`, `Run`, `Sit`) ovat ennallaan. |
| `porikopteri_npc_*.glb` (6 kpl) | Kävelijät, joissa on uusi `Passenger`-animaatio (kyydissä tavaratelineellä). Korvaavat aiemmat kävelijätiedostot; `Idle` ja `Walk` ovat ennallaan. |

Molemmat läpäisivät glTF-validoinnin ilman virheitä. Selaimessa niitä ei ole kokeiltu.

## Pyörän solmut

Juuri on `Bike`. Origo on maassa pyörien puolivälissä, keula +Z, Y ylös, mitat metreinä (pituus 1,77, leveys 0,64, korkeus 1,05, renkaan säde 0,34).

| Solmu | Käyttö |
|---|---|
| `Frame` | Runko, satula, tavarateline, takalokasuoja, ketju. Ei liiku. |
| `Wheel_F`, `Wheel_R` | Pyörivät paikallisen X-akselin ympäri, eteenpäin positiivisella kulmalla: `rotation.x += nopeus * dt / 0.34` |
| `Crank` | Kammet ja eturatas, pyörii X-akselin ympäri samaan suuntaan |
| `Pedal_L`, `Pedal_R` | `Crank`-solmun lapsia. Pidetään vaakatasossa: `rotation.x = -Crank.rotation.x` |
| `Steering` | Haarukka, ohjaustanko ja etupyörä. Käännetään asettamalla `rotation.y`, positiivinen = vasemmalle. Solmun `rotation.x` on ohjausakselin kallistus, älä muuta sitä. |

| `RackPad` | Istuinpehmuste tavaratelineellä. Oma solmunsa, jonka voi piilottaa, jos kyytiä ei käytetä. |

`Wheel_F` ja `Fork` ovat `Steering`-solmun lapsia. Rungon materiaali on `BikePaint`, joten värin voi vaihtaa.

## Polkeminen

1. Aseta hahmon juuri `Player` samaan paikkaan ja suuntaan kuin `Bike`.
2. Soita hahmolle `Cycle`. Se on sekunnin silmukka, joka vastaa yhtä kammen kierrosta. Hetkellä 0 vasen poljin on edessä vaakatasossa, kuten pyörän lepoasennossa.
3. Pidä kammet tahdissa: `Crank.rotation.x = 2 * Math.PI * (action.time / kesto)`.
4. Säädä polkemisnopeutta animaation `timeScale`-arvolla ja pyöritä renkaita ajonopeuden mukaan.

## Kyytiläinen tavaratelineellä

1. Aseta kävelijän juuri `Player` samaan paikkaan ja suuntaan kuin `Bike`, ja pidä se pyörän mukana (esim. `Bike`-solmun lapsena).
2. Soita kävelijälle `Passenger`. Se on kahden sekunnin silmukka: hahmo istuu sivuttain kasvot vasemmalle, jalat roikkuvat pyörän vasemmalla puolella ja heiluvat hieman, oikea käsi on satulan takareunalla.
3. Kävelijän juurisolmun skaalaa ei saa muuttaa. Lasten animaatio on tehty heidän omaan kokoonsa, joten hekin istuvat telineen päällä oikealla korkeudella.

Kyytiläinen istuu aina samalla puolella. Kallistus: ks. seuraava luku.

## Kallistus käännöksissä

Kallistus tehdään kahdessa osassa, ja ne voi yhdistää.

**1. Koko pyörä kallistuu (pelin koodissa, ei vaadi uusia tiedostoja).** Kierrä `Bike`-solmua eteenpäin osoittavan Z-akselin ympäri: `Bike.rotation.z = -kallistus`, jossa positiivinen `kallistus` on vasemmalle. Polkija ja kyytiläinen kallistuvat mukana, kun ne ovat `Bike`-solmun lapsia tai saavat saman kierron. Sopiva kulma on noin `atan(nopeus² / (9,81 × kaarresäde))`, käytännössä enintään 20–25 astetta.

**2. Hahmot nojaavat pyörän päällä (uudet animaatiot).**

| Hahmo | Perusanimaatio | Nojaus vasemmalle | Nojaus oikealle |
|---|---|---|---|
| Polkija (`porikopteri_hahmo.glb`) | `Cycle` | `CycleLeanL` | `CycleLeanR` |
| Kyytiläinen (`porikopteri_npc_*.glb`) | `Passenger` | `PassengerLeanL` | `PassengerLeanR` |

Nojausanimaatiot ovat samanpituisia silmukoita kuin perusanimaatio (sama polkeminen, ylävartalo noin 10 astetta sivussa; kädet ja jalat pysyvät paikoillaan). Niitä käytetään painottamalla:

```js
const w = Math.min(Math.abs(nojaus), 1);            // nojaus -1 ... 1, positiivinen = vasemmalle
cycle.setEffectiveWeight(1 - w);
leanL.setEffectiveWeight(nojaus > 0 ? w : 0);
leanR.setEffectiveWeight(nojaus < 0 ? w : 0);
leanL.time = leanR.time = cycle.time;               // kaikki kolme soivat samassa tahdissa
```

Kaikki kolme animaatiota pidetään käynnissä (`play()`), ja vain painot muuttuvat. Kyytiläiselle sama `Passenger`-animaatioilla.

## Rajoitukset

- Kädet eivät seuraa ohjaustankoa, kun `Steering` kääntyy. Pidä kääntökulma pienenä tai hyväksy pieni liukuma.
- Pysähtyneelle pyörälle ei ole asentoa, jossa jalka on maassa. Pysähdyksissä voi pysäyttää `Cycle`-animaation.
- Vain pelaajahahmolla on `Cycle`, ja vain kävelijöillä on `Passenger`. Kävelijät eivät osaa polkea, eikä pelaaja istu kyydissä.
- Peukalot eivät kierry kahvan alle.
