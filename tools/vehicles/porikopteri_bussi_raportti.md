# Porikopteri – kaupunkibussi: raportti (versio 2: ovet ja vauriot)

Laadittu 20.11.2026. Tiedostot: `porikopteri_bussi.py` (`--type bus`), `porikopteri_bussi.glb` (täysi), `porikopteri_bussi_low.glb` (kevyt).

## Yhteenveto

- Uutta: neljä avautuvaa ovilehteä omina solmuinaan ja vaurioportaat samalla säännöllä kuin autoissa.
- glTF-validointi: molemmat läpäisivät, 0 virhettä ja 0 varoitusta. Selaimessa tiedostoja ei ole kokeiltu.
- Kolmiot yhteensä: täysi malli 41510, kevyt malli 12024.
- Kerralla näkyvissä, täysi malli: porras 0: 30545, porras 1: 30567, porras 2: 32253, porras 3: 33695.
- Kerralla näkyvissä, kevyt malli: porras 0: 10222, porras 1: 10244, porras 2: 10462, porras 3: 10846.
- Mitat, renkaat ja materiaalit ovat ennallaan: pituus 12,12 m, leveys 2,55 m (peileineen 3,08 m), korkeus 3,23 m, akseliväli 5,90 m, renkaan säde 0,48 m, renkaat edessä ±1,10 m ja takana ±0,93 m keskilinjasta.
- Ehjän bussin ulkonäkö on sama kuin ennen. Ainoa näkyvä ero on ovilehtien musta karmi.

## Ovet

Etuovi (`DoorF`) ja keskiovi (`DoorM`) ovat oikealla kyljellä. Kummassakin on kaksi lehteä: `_A` on etummainen ja `_B` takimmainen. Lehden origo on saranan kohdalla, joten ovi avataan kiertämällä solmua pystyakselin ympäri: `rotation.y = kulma radiaaneina`. Lehdet kääntyvät sisäänpäin.

| Solmu | Saranan paikka (x; y; z) | Avauskulma | Kolmioita |
|---|---|---|---|
| `DoorF_A` | (-1,27; 0; 4,966) | -85° | 200 |
| `DoorF_B` | (-1,27; 0; 3,85) | +85° | 160 |
| `DoorM_A` | (-1,27; 0; 0,7) | -85° | 163 |
| `DoorM_B` | (-1,27; 0; -0,6) | +85° | 162 |

- Avauskulma on myös solmun lisätiedoissa (`userData.openAngleDeg`). Kiinni-asento on 0.
- Etumerkki on tarkistettu Blenderissä renderöimällä ovet auki. three.js:ssä sama kulma `rotation.y`:ssä pitäisi toimia samoin, mutta sitä ei ole kokeiltu.
- Kevyessä mallissa ovien takana on tumma laatikko, koska sisustaa ei ole: avattu ovi näyttää tummalta oviaukolta.
- Ovilehdet eivät kuulu vaurioportaisiin.

## Vaurioportaat, täysi malli (suluissa kolmiot)

| Osa | d0 | d1 | d2 | d3 |
|---|---|---|---|---|
| BumperF | `BumperF_d0` (1326) | `BumperF_d1` (1348) | – | `BumperF_d3` (1280) |
| BumperR | `BumperR_d0` (1552) | – | `BumperR_d2` (1552) | – |
| HeadlightL | `HeadlightL_d0` (20) | `HeadlightL_d1` (20) | – | – |
| HeadlightR | `HeadlightR_d0` (20) | – | – | `HeadlightR_d3` (20) |
| MirrorL | `MirrorL_d0` (80) | – | `MirrorL_d2` (12) | – |
| MirrorR | `MirrorR_d0` (80) | – | – | – |
| SideL | `SideL_d0` (192) | – | `SideL_d2` (1728) | `SideL_d3` (1728) |
| SideR | `SideR_d0` (183) | – | – | `SideR_d3` (1647) |
| TaillightL | `TaillightL_d0` (246) | – | – | – |
| TaillightR | `TaillightR_d0` (246) | – | – | `TaillightR_d3` (246) |
| Windshield | `Windshield_d0` (248) | – | `Windshield_d2` (466) | `Windshield_d3` (918) |

Portaattomat solmut: `Body`, `Details`, `DoorF_A`, `DoorF_B`, `DoorM_A`, `DoorM_B`, `Interior`, `PlateText_front`, `PlateText_rear`, `RouteText_front`, `RouteText_rear`, `Wheel_FL`, `Wheel_FR`, `Wheel_RL`, `Wheel_RR`.

## Vaurioportaat, kevyt malli

| Osa | d0 | d1 | d2 | d3 |
|---|---|---|---|---|
| BumperF | `BumperF_d0` (389) | `BumperF_d1` (411) | – | `BumperF_d3` (343) |
| HeadlightL | `HeadlightL_d0` (20) | `HeadlightL_d1` (20) | – | – |
| HeadlightR | `HeadlightR_d0` (20) | – | – | `HeadlightR_d3` (20) |
| Windshield | `Windshield_d0` (60) | – | `Windshield_d2` (278) | `Windshield_d3` (730) |

Portaattomat solmut: `Body`, `Details`, `DoorF_A`, `DoorF_B`, `DoorM_A`, `DoorM_B`, `Wheel_FL`, `Wheel_FR`, `Wheel_RL`, `Wheel_RR`.

## Mitä kullakin portaalla näkyy

Vauriot ovat vasemmassa etukulmassa ja oikeassa takakulmassa, kuten autoissa.

| Porras | Muutokset |
|---|---|
| 1 | Etupaneelin vasen pää painunut ja lommolla, naarmuja (`BumperF_d1`), vasen ajovalo rikki (`HeadlightL_d1`) |
| 2 | Tuulilasissa särötähti (`Windshield_d2`), vasen peili irronnut (`MirrorL_d2`, varren tynkä jäljellä), vasemmassa kyljessä lommo (`SideL_d2`), takapaneelin oikea pää painunut (`BumperR_d2`) |
| 3 | Etupaneeli roikkuu vasemmasta päästä ja kilpi on irronnut (`BumperF_d3`), myös oikea ajovalo rikki (`HeadlightR_d3`), tuulilasi pahoin säröillä (`Windshield_d3`), lommot molemmissa kyljissä (`SideL_d3`, `SideR_d3`), oikea takavalo rikki (`TaillightR_d3`) |

Sääntö on sama kuin autoissa: jokaisesta osasta näytetään korkein porras, joka on enintään nykyinen, ja `PlateText_front` piilotetaan portaalla 3. GLB:ssä kaikki portaat ovat oletuksena näkyvissä.

## Poikkeamat autojen rakenteesta

- **`Hood`-osaa ei ole**, koska bussissa ei ole konepeltiä. `BumperF` on koko etupaneeli tuulilasin alapuolella.
- **`FenderFL` ja `FenderFR` puuttuvat.** Niiden tilalla ovat kyljet `SideL` ja `SideR` akselien välissä (oikealla keskioven molemmin puolin).
- **`BumperR` on koko takapaneeli** takalasin alapuolella, moottoritilan säleikkö mukaan lukien.
- Kyljen lommot ovat matalia (noin 6 cm), koska sisäseinä on heti pellin takana. Ne näkyvät lähinnä valon heijastuksista.
- Kevyessä mallissa vaurio-osia ovat vain `BumperF`, `Windshield`, `HeadlightL` ja `HeadlightR`. Peilit, kyljet, takapaneeli ja takavalot ovat osa solmuja `Body` ja `Details`.
- Uudet materiaalit kuten autoissa: `GlassCracked`, `LampBroken`, `BareMetal`.
- `Body`:ssä on piilossa oleva tumma palkki etupaneelin takana, joka näkyy vasta, kun paneeli roikkuu.
- Portaalla 3 roikkuva etupaneeli ulottuu ehjää bussia pidemmälle, joten törmäyslaatikko kannattaa pitää ehjän bussin mitoissa.
- Katsottu kuvista: ovet kiinni ja auki oikealta edestä, porras 3 vasemmalta edestä ja oikealta takaa. Portaita 1 ja 2 ja kevyttä mallia ei ole katsottu kuvina.
