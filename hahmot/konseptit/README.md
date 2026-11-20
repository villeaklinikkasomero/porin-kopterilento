# Satamakaupunki – hahmokonseptit

Tehty 20.11.2026. Konseptit Satamakaupunki-tarinan hahmoista (lähde: `tarina/data/hahmot.json` ja `tarina/data/tehtavat/M01–M06.json`).
Tyyli on 1960–70-luvun sarjakuva: paksu tumma ääriviiva, tasavärit ja rasteripisteet varjopuolella (valo tulee vasemmalta ylhäältä).
Harju, Varjo ja muut hahmot pukeutuvat nykyaikaan, ja tyyli tulee piirrosjäljestä. Poikkeus on autokauppias, joka on tarkoituksella 70-lukulainen.

## Sisältö

| Kansio / tiedosto | Mitä | Käyttö |
|---|---|---|
| `arkit/<id>.png/.svg` | Konseptiarkki: edestä A-asennossa ja sivulta mittaviivoin, 6 ilmettä, värit, kuvaus, siluetti ja rekvisiitta | 3D-mallinnuksen referenssi (taustakuvaksi Blenderiin: mittakaava 4,55 px/cm, lattia y=1085) |
| `mallikortit/<id>.json` | Mitat (cm), värit sRGB:nä ja Blenderin lineaarisina, MakeHuman-arvot, vaatteet, animaatiolista, mallinnusohjeet | `porikopteri_hahmo.py`-tyylisen generaattorin syöte |
| `muotokuvat/<id>_<tunne>.png` | 512×512 läpinäkyvä rintakuva, 6 tunnetta per hahmo | Dialogin muotokuvat pelissä. Tunteet ovat samat kuin tehtävämoottorissa (`neutraali, iloinen, vihainen, yllattynyt, huolestunut, ovela`). |
| `rivikuva.png/.svg` | Kaikki hahmot samassa mittakaavassa (+ vartijamuunnelmat B ja C) | Pituuksien ja siluettien vertailu |
| `muotokuvat_yhteenveto.png` | Kaikki muotokuvat yhdellä sivulla | Tarkistus |

Generaattori on kansiossa `tools/hahmo/konseptit/`: `python kokoa.py <ulos>` ja sitten `node render.js <ulos>/**/*.svg` (Playwright).
Kaikki on samaa dataa (`hahmot_data.py`), joten esimerkiksi värin vaihto päivittää arkin, muotokuvat ja mallikortin kerralla.

## Hahmot

| ID | Kuka | Pituus | Tila |
|---|---|---|---|
| RAMI | Päähahmo | 180 | 3D-malli on olemassa, ja arkki on tyyliviite muille |
| TAPSA | Korjaamon isäntä | 174 | Konsepti |
| LUMI | Tekniikkanero, drooni | 166 | Konsepti |
| TERTTU | Torikauppias | 160 | Konsepti (rooli päätelty M01:stä) |
| HARJU | Ex-satamakapteeni, venevaja | 184 | **Rooli on oletus**, ja se pitää tarkistaa käsikirjoituksesta |
| VARJO | Varjo Holdingsin toimitusjohtaja | 186 | Konsepti: nykyaikainen ja uskottava, ei korostetusti paha |
| VARTIJA | Varjo Securityn vartija (A/B/C) | 168–178 | Konsepti (B ja C näkyvät vain rivikuvassa) |
| MYYJA | Autoliike Kiillon myyjä | 172 | Konsepti |
| KURIIRI | Pyöräkuriiri | 176 | Konsepti (yhteys Lumiin on ehdotus) |

RADIO on pelkkä ääni, eikä sille tehty hahmoa.

## 3D-mallinnus (ehdotus)

1. Pohjaksi sopii lähin `npc_*`-malli tai MakeHuman/MPFB2 (`makehuman`-arvot mallikortissa) ja `porikopteri_hahmo.py`:n rakenne. Vaihda värit, vaatteet ja hiukset kortin mukaan.
2. Sarjakuvamaisuus 3D:ssä: toon-materiaali (2–3 sävyä), käänteinen kuori (inverted hull) ääriviivaksi, paksuus noin 0,5 cm (`tyyli.aariviiva_cm`), ja rasteripisteet varjopuolelle screen space -shaderilla.
   Rami tarvitsee saman materiaalin, jotta hahmot sopivat yhteen.
3. Leivo animaatiot perään kuten ennenkin: `python tools/hahmo/kavely_glb.py <hahmo>.js --add Dance,Dance2 ...`.
4. Ilmeet: kortin 6 tunnetta voivat olla blend shapeja (kulmat, luomet, suu). Muotokuvat toimivat jo sellaisenaan dialogissa.

## 2D-käyttö pelissä

- Dialogi: `ui.js` voi näyttää kuvan `hahmot/konseptit/muotokuvat/${hahmo.toLowerCase()}_${tunne}.png` repliikin vieressä (tunteen nimessä ä → a, eli `yllattynyt`). Koodia ei ole muutettu.
- Bussipysäkkimainos (M01, "Sen kasvot on joka bussipysäkillä"): `varjo_iloinen.png` + teksti sopii suoraan julistetekstuuriksi.
- Välianimaatiot sarjakuvaruutuina: arkkien ilmeruudut ovat valmiita paneeleja.

## Avoimet kysymykset

- Harjun rooli ja mahdolliset muut nimetyt hahmot luvuista 2–5: käsikirjoitusartifaktia ei voitu lukea tästä istunnosta.
- Varjon sukupuoli. Nyt mies, mutta nimi on neutraali, ja datassa sen vaihtaminen on helppoa.
- Radion nimi (Radio Kirjuri / Radio Porikopteri) ei vaikuta hahmoihin.
