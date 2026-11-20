# Porikopteri – farmari: raportti

Laadittu 20.11.2026. Tiedostot: `porikopteri_autot.py` (valinta `--type estate`), `porikopteri_farmari.glb` (täysi), `porikopteri_farmari_low.glb` (kevyt).

## Yhteenveto

- Rakenne on sama kuin tiedostossa `porikopteri_auto.glb`: juurisolmu `Car`, renkaat `Wheel_FL`, `Wheel_FR`, `Wheel_RL`, `Wheel_RR`, vaurioportaat solmuina `<Osa>_d0` … `_d3` samalla origolla ja asennolla.
- glTF-validointi: molemmat läpäisivät, 0 virhettä ja 0 varoitusta. Selaimessa tiedostoja ei ole kokeiltu.
- Kolmiot yhteensä: täysi malli 66121 (raja noin 70 000), kevyt malli 12398 (raja noin 14 000).
- Kerralla näkyvissä, täysi malli: porras 0: 47874, porras 1: 47964, porras 2: 47944, porras 3: 47873.
- Kerralla näkyvissä, kevyt malli: porras 0: 8678, porras 1: 8772, porras 2: 8952, porras 3: 9406.

## Mitat (ehjä auto)

| Mitta | Täysi malli | Kevyt malli | Tavoite |
|---|---|---|---|
| Pituus | 4,72 m | 4,72 m | noin 4,7 × 1,83 × 1,47 m, akseliväli noin 2,75 m |
| Leveys peileineen | 2,10 m | 2,10 m | |
| Korin leveys ilman peilejä | 1,83 m | 1,83 m | |
| Korkeus | 1,46 m | 1,46 m | |
| Akseliväli | 2,750 m | 2,750 m | |
| Raideväli | 1,567 m | 1,567 m | nykyisessä autossa 1,550 m |
| Renkaan säde | 0,325 m | 0,325 m | 0,325 m |

- Origo on maan tasossa akselivälin puolivälissä, keula +Z, Y ylös, mitat metreinä.
- Renkaiden solmujen paikat (x, y, z): `Wheel_FL` (0.784, 0.325, 1.375), `Wheel_FR` (-0.784, 0.325, 1.375), `Wheel_RL` (0.784, 0.325, -1.375), `Wheel_RR` (-0.784, 0.325, -1.375). Renkaat pyörivät paikallisen X-akselin ympäri.
- Ohjauspyörän keskipiste (x sivulle vasemmalle, y ylös, z eteen): (0,37; 0,92; 0,53) m. Nykyisessä autossa se on (0,37; 0,92; 0,47). Istuin, kojelauta ja ohjauspyörä on siirretty yhtenä kokonaisuutena, joten kuljettajan silmien paikka suhteessa ohjauspyörään on sama kuin nykyisessä autossa: kuljettajan kameran saa siirtämällä nykyistä kameraa näiden pisteiden erotuksen verran.

## Solmut portaittain, täysi malli (suluissa kolmiot)

| Osa | d0 | d1 | d2 | d3 |
|---|---|---|---|---|
| BumperF | `BumperF_d0` (3624) | `BumperF_d1` (3688) | – | `BumperF_d3` (3620) |
| BumperR | `BumperR_d0` (2236) | – | `BumperR_d2` (2236) | – |
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

Portaattomat solmut: `Body`, `Details`, `Headliner`, `Interior`, `PlateText_front`, `PlateText_rear`, `Seams`, `Wheel_FL`, `Wheel_FR`, `Wheel_RL`, `Wheel_RR`.

## Solmut portaittain, kevyt malli

| Osa | d0 | d1 | d2 | d3 |
|---|---|---|---|---|
| BumperF | `BumperF_d0` (844) | `BumperF_d1` (912) | – | `BumperF_d3` (844) |
| HeadlightL | `HeadlightL_d0` (192) | `HeadlightL_d1` (218) | – | – |
| HeadlightR | `HeadlightR_d0` (192) | – | – | `HeadlightR_d3` (218) |
| Hood | `Hood_d0` (160) | `Hood_d1` (160) | `Hood_d2` (160) | `Hood_d3` (160) |
| Windshield | `Windshield_d0` (96) | – | `Windshield_d2` (276) | `Windshield_d3` (772) |

Portaattomat solmut: `Body`, `Details`, `Wheel_FL`, `Wheel_FR`, `Wheel_RL`, `Wheel_RR`.

## Puuttuvat osat

Mikään osa ei puutu kokonaan miltään portaalta. `MirrorL_d2` sisältää vain peilin kiinnitysjalan, ja `BumperF_d3`:sta puuttuu rekisterikilpi. `PlateText_front` piilotetaan portaalla 3.

## Materiaalit

`Alloy`, `BareMetal`, `BlackTrim`, `BrakeDisc`, `Caliper`, `CarPaint`, `Chrome`, `Glass`, `GlassCracked`, `Grille`, `Headlight`, `Headliner`, `Interior`, `LampBroken`, `Plate`, `PlateEU`, `PlateText`, `Seam`, `Seat`, `Taillight`, `Tire`, `Underbody`.

Maalipinta on `CarPaint`. Rekisterikilven teksti on ORI-789. Takalasin teippiä ei ole.

## Poikkeamat vaatimuksista ja muut huomiot

- **`PlateText_front` on vain täydessä mallissa**, kuten nykyisessäkin autossa. Kevyessä mallissa kilpi on ilman tekstiä.
- **Raideväli on eri kuin nykyisessä autossa** (1,567 m), koska kori on leveämpi. Jos pelin fysiikka olettaa 1,55 m, renkaiden paikat pitää lukea solmuista.
- **Lisäsolmut `SideL_d0` ja `SideR_d0`** kuten nykyisessä autossa: lommoinen kylki korvaa ehjän vain, jos ehjä kylki on oma solmunsa.
- **Vauriot ovat samoissa kohdissa kuin nykyisessä autossa:** vasen etukulma ja oikea takakulma. Vasen ajovalo hajoaa portaalla 1 ja oikea portaalla 3.
- Portaalla 3 roikkuva etupuskuri ulottuu ehjää autoa pidemmälle, joten törmäyslaatikko kannattaa pitää ehjän auton mitoissa.
- `Body`:ssä on kaksi piilossa olevaa täytettä (moottoritila ja palkki puskurin takana), kuten nykyisessä autossa.
- **Kattokaiteet ja antenni** ovat solmussa `Details`. Korkeus 1,46 m sisältää ne.
- Takapenkin takana on avoin tavaratila, joka näkyy takalasista. Istuimia on viisi.
- Mallit on johdettu nykyisestä autosta venyttämällä, joten keula ja ohjaamo muistuttavat sitä. Leveyssuunnan venytys (1,83 m / 1,81 m) näkyy lievänä soikeutena ohjauspyörässä.
- `.blend`-tiedostoa ei tehty, koska sitä ei pyydetty. Skripti tallentaa sen, jos valitsimen `--no-blend` jättää pois.
