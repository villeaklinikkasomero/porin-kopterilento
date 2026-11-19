# Porikopteri – pelaajan auton vauriot: raportti

Laadittu 19.11.2026. Tiedostot: `porikopteri_auto.py`, `porikopteri_auto.glb` (täysi), `porikopteri_auto_low.glb` (kevyt).

## Yhteenveto

- Molemmissa GLB-tiedostoissa on kaikki neljä porrasta samassa tiedostossa omina nimettyinä solmuinaan. Juurisolmu on `Car`.
- glTF-validointi: molemmat läpäisivät, 0 virhettä ja 0 varoitusta. Selaimessa tiedostoja ei ole kokeiltu.
- Kolmiot yhteensä: täysi malli 63900 (raja noin 70 000), kevyt malli 11554 (raja noin 14 000).
- Kerralla näkyvissä, täysi malli: porras 0: 46265, porras 1: 46355, porras 2: 46335, porras 3: 46307.
- Kerralla näkyvissä, kevyt malli: porras 0: 7834, porras 1: 7928, porras 2: 8108, porras 3: 8562.
- Ehjä auto (porras 0): ulkomitat ovat täsmälleen samat kuin ennen (2,08 × 4,33 × 1,48 m), ja pinnat ja niiden varjostus ovat samat. Kolmioita on 140 enemmän, koska koriin lisättiin kaksi piilossa olevaa täytettä (ks. Poikkeamat).

## Pelin sääntö

Jokaisesta osasta näytetään korkein porras, joka on enintään auton nykyinen vaurioporras, ja muut saman osan portaat piilotetaan. GLB:ssä kaikki solmut ovat oletuksena näkyvissä, joten peli piilottaa portaat 1–3 heti latauksen jälkeen. Kaikilla porrassolmuilla on sama origo ja asento (ei siirtoa eikä kiertoa), joten vaihto tehdään pelkällä näkyvyydellä.

Lisäsääntö: `PlateText_front` piilotetaan portaalla 3, koska rekisterikilpi irtoaa roikkuvan etupuskurin mukana.

## Solmut portaittain, täysi malli (suluissa kolmiot)

| Osa | d0 | d1 | d2 | d3 |
|---|---|---|---|---|
| BumperF | `BumperF_d0` (3624) | `BumperF_d1` (3688) | – | `BumperF_d3` (3620) |
| BumperR | `BumperR_d0` (1624) | – | `BumperR_d2` (1624) | – |
| FenderFL | `FenderFL_d0` (563) | – | `FenderFL_d2` (563) | – |
| FenderFR | `FenderFR_d0` (563) | – | – | – |
| HeadlightL | `HeadlightL_d0` (768) | `HeadlightL_d1` (794) | – | – |
| HeadlightR | `HeadlightR_d0` (768) | – | – | `HeadlightR_d3` (794) |
| Hood | `Hood_d0` (888) | `Hood_d1` (888) | `Hood_d2` (888) | `Hood_d3` (888) |
| MirrorL | `MirrorL_d0` (308) | – | `MirrorL_d2` (108) | – |
| MirrorR | `MirrorR_d0` (308) | – | – | – |
| SideL | `SideL_d0` (902) | – | – | `SideL_d3` (902) |
| SideR | `SideR_d0` (902) | – | – | `SideR_d3` (902) |
| TaillightL | `TaillightL_d0` (352) | – | – | – |
| TaillightR | `TaillightR_d0` (352) | – | – | `TaillightR_d3` (352) |
| Windshield | `Windshield_d0` (384) | – | `Windshield_d2` (564) | `Windshield_d3` (1060) |

Portaattomat solmut (aina näkyvissä): `Body`, `Details`, `Headliner`, `Interior`, `PlateText_front`, `PlateText_rear`, `Seams`, `Sticker`, `Wheel_FL`, `Wheel_FR`, `Wheel_RL`, `Wheel_RR`.

## Solmut portaittain, kevyt malli

| Osa | d0 | d1 | d2 | d3 |
|---|---|---|---|---|
| BumperF | `BumperF_d0` (844) | `BumperF_d1` (912) | – | `BumperF_d3` (844) |
| HeadlightL | `HeadlightL_d0` (192) | `HeadlightL_d1` (218) | – | – |
| HeadlightR | `HeadlightR_d0` (192) | – | – | `HeadlightR_d3` (218) |
| Hood | `Hood_d0` (160) | `Hood_d1` (160) | `Hood_d2` (160) | `Hood_d3` (160) |
| Windshield | `Windshield_d0` (96) | – | `Windshield_d2` (276) | `Windshield_d3` (772) |

Portaattomat solmut: `Body`, `Details`, `Wheel_FL`, `Wheel_FR`, `Wheel_RL`, `Wheel_RR`. Kevyessä mallissa peilit, lokasuojat, kyljet, takapuskuri ja takavalot ovat edelleen osa solmuja `Body` ja `Details`.

## Mitä kullakin portaalla näkyy

Vauriot ovat auton vasemmassa etukulmassa ja oikeassa takakulmassa.

| Porras | Muutokset |
|---|---|
| 1 | Etupuskurin vasen pää painunut ja lommolla, naarmuja molemmissa etukulmissa (`BumperF_d1`), vasen ajovalo rikki (`HeadlightL_d1`), konepellissä lommo (`Hood_d1`) |
| 2 | Konepelti rypyssä ja raollaan (`Hood_d2`), tuulilasissa särötähti (`Windshield_d2`), vasen etulokasuoja painunut (`FenderFL_d2`), vasen sivupeili irronnut (`MirrorL_d2`), takapuskurin oikea pää roikkuu (`BumperR_d2`) |
| 3 | Konepelti selvästi koholla (`Hood_d3`), etupuskuri kiinni vain oikeasta päästä ja ilman kilpeä (`BumperF_d3`), myös oikea ajovalo rikki (`HeadlightR_d3`), tuulilasi pahoin säröillä (`Windshield_d3`), lommot molemmissa kyljissä (`SideL_d3`, `SideR_d3`), oikea takavalo rikki (`TaillightR_d3`) |

## Puuttuvat osat

Mikään osa ei puutu kokonaan miltään portaalta, joten varasääntö (lähin alempi porras) toimii kaikille osille.

- `MirrorL_d2`: peilin kotelo ja lasi puuttuvat, solmussa on vain kiinnitysjalka. Tämä on tehty tarkoituksella solmuksi, jotta peli ei palaa ehjään peiliin.
- `BumperF_d3`: rekisterikilpi ja sen pidike puuttuvat.

## Materiaalit

Nykyiset materiaalit ovat samoilla nimillä. Uusia on kolme: `GlassCracked` (säröt ja murskakohdat), `LampBroken` (sammunut valo) ja `BareMetal` (naarmut). Kaikki lommoiset osat käyttävät samaa `CarPaint`-materiaalia kuin ehjä kori. Vauriot ovat geometriaa porrassolmuissa, eivät tekstuureissa.

## Poikkeamat vaatimuksista ja muut huomiot

1. **Lisäsolmut `SideL_d0` ja `SideR_d0`.** Kylkien lommot voivat korvata ehjän kyljen vain, jos ehjä kylki on oma solmunsa. Nimiä ei ollut listassa.
2. **`PlateText_front` portaalla 3.** Tarvitsee yllä kuvatun lisäsäännön. Portailla 1–2 kilven kohta pysyy paikallaan, joten teksti on oikeassa kohdassa.
3. **`Body` sisältää kaksi uutta piilossa olevaa täytettä** (140 kolmiota): tumma moottoritila konepellin alla ja palkki etupuskurin takana. Ne näkyvät vasta, kun konepelti nousee tai puskuri roikkuu.
4. **`Details` ja `Seams` ovat pienempiä kuin ennen.** Osa niiden kappaleista siirtyi sen osan solmuun, jonka mukana niiden pitää liikkua: peilit, etukilpi, säleikön rimat, sumuvalot ja keulan merkki (`BumperF`), takaheijastimet ja pakoputket (`BumperR`), etupyöränkaarien reunat (`FenderF`), ovenkahvat ja ovisaumat (`Side`), konepellin sauma (`Hood`).
5. **Portaalla 3 etupuskuri ulottuu noin 8 cm ehjää autoa pidemmälle.** Törmäyslaatikko kannattaa pitää ehjän auton mitoissa.
6. **Piirtokutsut.** Jokainen porrassolmu on oma verkkonsa, ja usealla on monta materiaalia. Näkyvien piirtokutsujen määrä kasvaa siksi aiemmasta.
7. Renkaisiin ei ole koskettu.

## Tiedostokoot

- `porikopteri_auto.glb`: 1485 kt (ennen 1 094 kt)
- `porikopteri_auto_low.glb`: 301 kt (ennen 192 kt)
