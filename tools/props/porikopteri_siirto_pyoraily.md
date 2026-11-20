# Porikopteri – siirtotiedosto: pyöräily

Laadittu 20.11.2026. Peliin tarvitaan kaksi tiedostoa:

| Tiedosto | Sisältö |
|---|---|
| `porikopteri_pyora.glb` | Polkupyörä (5 100 kolmiota, 172 kt), ei animaatioita |
| `porikopteri_hahmo.glb` | Pelaajahahmo, jossa on uusi `Cycle`-animaatio. Korvaa aiemman hahmotiedoston; muut animaatiot (`Idle`, `Walk`, `Run`, `Sit`) ovat ennallaan. |

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

`Wheel_F` ja `Fork` ovat `Steering`-solmun lapsia. Rungon materiaali on `BikePaint`, joten värin voi vaihtaa.

## Polkeminen

1. Aseta hahmon juuri `Player` samaan paikkaan ja suuntaan kuin `Bike`.
2. Soita hahmolle `Cycle`. Se on sekunnin silmukka, joka vastaa yhtä kammen kierrosta. Hetkellä 0 vasen poljin on edessä vaakatasossa, kuten pyörän lepoasennossa.
3. Pidä kammet tahdissa: `Crank.rotation.x = 2 * Math.PI * (action.time / kesto)`.
4. Säädä polkemisnopeutta animaation `timeScale`-arvolla ja pyöritä renkaita ajonopeuden mukaan.

## Rajoitukset

- Kädet eivät seuraa ohjaustankoa, kun `Steering` kääntyy. Pidä kääntökulma pienenä tai hyväksy pieni liukuma.
- Pysähtyneelle pyörälle ei ole asentoa, jossa jalka on maassa. Pysähdyksissä voi pysäyttää `Cycle`-animaation.
- Vain pelaajahahmolla on `Cycle`. Kaupungin kävelijät eivät osaa polkea.
- Peukalot eivät kierry kahvan alle.
