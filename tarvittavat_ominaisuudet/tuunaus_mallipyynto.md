# Mallipyyntö: auton tuunausosat (Porin kopterilento / Satamakaupunki)

*Kopioi tämä teksti mallichattiin. Päivitetty 20.11.2026.*

Tee pelin henkilöautoille tuunausosia, joita pelaaja voi ostaa Tapsan korjaamolta. Peli on perheystävällinen (PEGI 7), ja tyyli on sama kuin nykyisissä automalleissa. Osat tehdään samalla Blender-skriptityylillä kuin `tools/vehicles/porikopteri_autot.py`.

## Automallit, joihin osien pitää sopia

- viistoperä `auto.js`
- farmari `auto_est.js`
- pakettiauto `auto_van.js`
- sedan (kun se on valmis)

Bussi ei tarvitse tuunausta. Polkupyörälle riittää maalaus.

## Nykyiset käytännöt (älä muuta)

- **Koordinaatisto:** glTF, nokka +z, maa y = 0. Renkaat `Wheel_FL/FR/RL/RR` pyörivät oman x-akselinsa ympäri.
- **Maali:** maalattavat pinnat käyttävät materiaalia nimeltä `CarPaint`. Peli vaihtaa sen värin.
- **Vauriot:** vaurioituvat osat on nimetty portaittain `Osa_d0 … Osa_d3`. Peli näyttää osasta korkeimman portaan, joka on ≤ nykyinen.
- **Kevytversio:** jokaisesta mallista tehdään kevytversio `_m` kosketuslaitteille.
- **Toimitus:** base64-GLB `.js`-tiedostona kuten nykyiset mallit, sekä raportti `.md` (mitat, kolmiomäärät, kiinnityspisteet).

## 1. Kiinnityspisteet jokaiseen automalliin

Lisää jokaiseen automalliin tyhjät objektit (Empty) näillä nimillä, jotta osat asettuvat oikein jokaiseen korimalliin:

| Nimi | Paikka |
|---|---|
| `Mount_Spoiler` | takaluukun/katon takareuna |
| `Mount_Roof` | katon keskikohta (kattoteline/-boksi) |
| `Mount_BumperF`, `Mount_BumperR` | etu- ja takapuskurin keskikohta |
| `Mount_SkirtL`, `Mount_SkirtR` | kynnysten keskikohta |
| `Mount_Exhaust` | pakoputken pää |
| `Mount_LightsF` | etusäleikön / puskurin alareuna lisävaloille |

Lisäksi:
- Raportoi jokaisesta mallista renkaan halkaisija ja leveys, jotta vanteet skaalautuvat.
- Jos osa ei sovi johonkin korimalliin (esim. spoileri pakettiautoon), merkitse se raporttiin.

## 2. Osat (`tuunaus.js` + `tuunaus_m.js`, yksi GLB, jokainen osa omana juuriobjektinaan)

| Ryhmä | Vaihtoehdot (objektien nimet) | Huom |
|---|---|---|
| **Vanteet** | `Rim_Sport` (5-puolainen), `Rim_Classic` (pelti + kapselit), `Rim_Mesh` (ristikko), `Rim_Off` (maasturi) | Origo akselilla, mitoitus 1 m halkaisijalle (peli skaalaa). Vanne ja rengas erikseen: `…_Rim` ja `…_Tire`. |
| **Spoilerit** | `Spoiler_Lip` (pieni huulispoileri), `Spoiler_Wing` (siipi) | Origo = `Mount_Spoiler` |
| **Helmat** | `Skirt_Sport` (vasen + oikea peilikuvina) | |
| **Etu-/takapuskurit** | `BumperF_Sport`, `BumperR_Sport`, `BumperF_Bull` (puskuriraudat) | Vauriotasot `_d0…_d3` kuten nykyisissä puskureissa |
| **Katto** | `Roof_Rack` (teline), `Roof_Box` (suksiboksi) | |
| **Pakoputki** | `Exhaust_Twin`, `Exhaust_Big` | |
| **Lisävalot** | `Lights_Fog` (2 pyöreää), `Lights_Bar` (LED-palkki) | Valolle oma materiaali `LightGlow` (peli sytyttää yöllä) |

**Materiaalit:**
- Korin väriä noudattavat osat käyttävät `CarPaint`-materiaalia (spoilerit, helmat, puskurit).
- Muut osat käyttävät materiaaleja `TrimBlack`, `Chrome` ja `Rubber`.

## 3. Teippaukset (`tuunaus_teipit.js` tai tekstuurit)

Tee 4 teippikuviota, jotka sopivat kaikkiin korimalleihin:
- kaksi kilpaviivaa konepellistä takaluukkuun
- sivuraita
- liekit tai aallot (Porin teema: joki ja meri)
- "Tapsan Korjaamo" -sponsoritarra

Tekniikan saa valita, kunhan peli voi vaihtaa sen pois päältä yhdellä asetuksella. Vaihtoehdot:
- ohut verkko 2 mm korin päällä
- tai `CarPaint`-materiaalin päälle kerrostettava tekstuuri, jos UV:t sallivat

## 4. Budjetti

- Yksi osa enintään 1 500 kolmiota (kevytversio 500).
- Vanteet 4 kpl / auto, joten vannemalli enintään 800 kolmiota (kevytversio 250).
- Koko `tuunaus.js` mieluiten alle 1,5 Mt.

## 5. Tarkistuskuvat raporttiin

Jokainen osa jokaisella korimallilla sivusta ja 3/4-kulmasta, sekä yksi kuva "täysin tuunatusta" viistoperästä.
