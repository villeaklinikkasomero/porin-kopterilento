# Porikopteri – pakettiauto: raportti

Laadittu 20.11.2026. Tiedostot: `porikopteri_autot.py` (valinta `--type van`), `porikopteri_pakettiauto.glb` (täysi), `porikopteri_pakettiauto_low.glb` (kevyt).

## Yhteenveto

- Rakenne on sama kuin tiedostossa `porikopteri_auto.glb`: juurisolmu `Car`, renkaat `Wheel_FL`, `Wheel_FR`, `Wheel_RL`, `Wheel_RR`, vaurioportaat solmuina `<Osa>_d0` … `_d3` samalla origolla ja asennolla.
- glTF-validointi: molemmat läpäisivät, 0 virhettä ja 0 varoitusta. Selaimessa tiedostoja ei ole kokeiltu.
- Kolmiot yhteensä: täysi malli 65389 (raja noin 70 000), kevyt malli 11308 (raja noin 14 000).
- Kerralla näkyvissä, täysi malli: porras 0: 46948, porras 1: 47022, porras 2: 47002, porras 3: 46994.
- Kerralla näkyvissä, kevyt malli: porras 0: 7724, porras 1: 7798, porras 2: 7978, porras 3: 8336.

## Mitat (ehjä auto)

| Mitta | Täysi malli | Kevyt malli | Tavoite |
|---|---|---|---|
| Pituus | 4,90 m | 4,94 m | noin 4,9 × 1,95 × 1,95 m, akseliväli noin 3,0 m |
| Leveys peileineen | 2,30 m | 2,30 m | |
| Korin leveys ilman peilejä | 1,95 m | 1,95 m | |
| Korkeus | 1,95 m | 1,95 m | |
| Akseliväli | 3,000 m | 3,000 m | |
| Raideväli | 1,670 m | 1,670 m | nykyisessä autossa 1,550 m |
| Renkaan säde | 0,325 m | 0,325 m | 0,325 m |

- Origo on maan tasossa akselivälin puolivälissä, keula +Z, Y ylös, mitat metreinä.
- Renkaiden solmujen paikat (x, y, z): `Wheel_FL` (0.835, 0.325, 1.5), `Wheel_FR` (-0.835, 0.325, 1.5), `Wheel_RL` (0.835, 0.325, -1.5), `Wheel_RR` (-0.835, 0.325, -1.5). Renkaat pyörivät paikallisen X-akselin ympäri.
- Ohjauspyörän keskipiste (x sivulle vasemmalle, y ylös, z eteen): (0,40; 1,22; 0,92) m. Nykyisessä autossa se on (0,37; 0,92; 0,47). Istuin, kojelauta ja ohjauspyörä on siirretty yhtenä kokonaisuutena, joten kuljettajan silmien paikka suhteessa ohjauspyörään on sama kuin nykyisessä autossa: kuljettajan kameran saa siirtämällä nykyistä kameraa näiden pisteiden erotuksen verran.

## Solmut portaittain, täysi malli (suluissa kolmiot)

| Osa | d0 | d1 | d2 | d3 |
|---|---|---|---|---|
| BumperF | `BumperF_d0` (3624) | `BumperF_d1` (3672) | – | `BumperF_d3` (3604) |
| BumperR | `BumperR_d0` (2212) | – | `BumperR_d2` (2212) | – |
| FenderFL | `FenderFL_d0` (557) | – | `FenderFL_d2` (557) | – |
| FenderFR | `FenderFR_d0` (557) | – | – | – |
| HeadlightL | `HeadlightL_d0` (768) | `HeadlightL_d1` (794) | – | – |
| HeadlightR | `HeadlightR_d0` (768) | – | – | `HeadlightR_d3` (794) |
| Hood | `Hood_d0` (880) | `Hood_d1` (880) | `Hood_d2` (880) | `Hood_d3` (880) |
| MirrorL | `MirrorL_d0` (308) | – | `MirrorL_d2` (108) | – |
| MirrorR | `MirrorR_d0` (308) | – | – | – |
| RearDoorL | `RearDoorL_d0` (560) | – | – | – |
| RearDoorR | `RearDoorR_d0` (614) | – | – | `RearDoorR_d3` (614) |
| SideL | `SideL_d0` (739) | – | – | `SideL_d3` (739) |
| SideR | `SideR_d0` (923) | – | – | `SideR_d3` (923) |
| TaillightL | `TaillightL_d0` (256) | – | – | – |
| TaillightR | `TaillightR_d0` (256) | – | – | `TaillightR_d3` (256) |
| Windshield | `Windshield_d0` (384) | – | `Windshield_d2` (564) | `Windshield_d3` (964) |

Portaattomat solmut: `Body`, `Details`, `Headliner`, `Interior`, `PlateText_front`, `PlateText_rear`, `Seams`, `Wheel_FL`, `Wheel_FR`, `Wheel_RL`, `Wheel_RR`.

## Solmut portaittain, kevyt malli

| Osa | d0 | d1 | d2 | d3 |
|---|---|---|---|---|
| BumperF | `BumperF_d0` (844) | `BumperF_d1` (892) | – | `BumperF_d3` (824) |
| HeadlightL | `HeadlightL_d0` (192) | `HeadlightL_d1` (218) | – | – |
| HeadlightR | `HeadlightR_d0` (192) | – | – | `HeadlightR_d3` (218) |
| Hood | `Hood_d0` (160) | `Hood_d1` (160) | `Hood_d2` (160) | `Hood_d3` (160) |
| Windshield | `Windshield_d0` (96) | – | `Windshield_d2` (276) | `Windshield_d3` (676) |

Portaattomat solmut: `Body`, `Details`, `Wheel_FL`, `Wheel_FR`, `Wheel_RL`, `Wheel_RR`.

## Puuttuvat osat

Mikään osa ei puutu kokonaan miltään portaalta. `MirrorL_d2` sisältää vain peilin kiinnitysjalan, ja `BumperF_d3`:sta puuttuu rekisterikilpi. `PlateText_front` piilotetaan portaalla 3.

## Materiaalit

`Alloy`, `BareMetal`, `BlackTrim`, `BrakeDisc`, `Caliper`, `CarPaint`, `Chrome`, `Glass`, `GlassCracked`, `Grille`, `Headlight`, `Headliner`, `Interior`, `LampBroken`, `Plate`, `PlateEU`, `PlateText`, `Seam`, `Seat`, `Taillight`, `Tire`, `Underbody`.

Maalipinta on `CarPaint`. Rekisterikilven teksti on PRI-456. Takalasin teippiä ei ole.

## Poikkeamat vaatimuksista ja muut huomiot

- **`PlateText_front` on vain täydessä mallissa**, kuten nykyisessäkin autossa. Kevyessä mallissa kilpi on ilman tekstiä.
- **Raideväli on eri kuin nykyisessä autossa** (1,670 m), koska kori on leveämpi. Jos pelin fysiikka olettaa 1,55 m, renkaiden paikat pitää lukea solmuista.
- **Lisäsolmut `SideL_d0` ja `SideR_d0`** kuten nykyisessä autossa: lommoinen kylki korvaa ehjän vain, jos ehjä kylki on oma solmunsa.
- **Vauriot ovat samoissa kohdissa kuin nykyisessä autossa:** vasen etukulma ja oikea takakulma. Vasen ajovalo hajoaa portaalla 1 ja oikea portaalla 3.
- Portaalla 3 roikkuva etupuskuri ulottuu ehjää autoa pidemmälle, joten törmäyslaatikko kannattaa pitää ehjän auton mitoissa.
- `Body`:ssä on kaksi piilossa olevaa täytettä (moottoritila ja palkki puskurin takana), kuten nykyisessä autossa.
- **Takaovet:** `RearDoorL_d0` ja `RearDoorR_d0` ovat pariovet. Portaalla 3 oikea ovi on raollaan (`RearDoorR_d3`), ja raosta näkyy tyhjä tavaratila. Kevyessä mallissa takaovet ovat osa solmua `Body` eivätkä aukea.
- **Takalasia ei ole** (umpiovet), joten takalasin pyyhkijää ei myöskään ole. Takakilpi on takapuskurissa, ei ovessa, jotta se ei liiku oven mukana.
- **Liukuovi** on oikealla kyljellä saumoina, kahvana ja liukukiskona. Se ei ole oma solmunsa eikä aukea.
- **Keula on melko pitkä** pakettiautoksi (konepelti noin metrin), eli muoto on lähempänä puolinokkaista pakettiautoa kuin tasanokkaista.
- Ohjaamossa on kaksi istuinta ja väliseinä, tavaratila on tyhjä laatikko. Sisustaa ei ole tarkistettu kuvista.
- Mallit on johdettu nykyisestä autosta venyttämällä, joten keula ja ohjaamo muistuttavat sitä. Leveyssuunnan venytys (1,95 m / 1,81 m) näkyy lievänä soikeutena ohjauspyörässä.
- `.blend`-tiedostoa ei tehty, koska sitä ei pyydetty. Skripti tallentaa sen, jos valitsimen `--no-blend` jättää pois.
