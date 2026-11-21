# aika/ – pelin kello, vuorokausirytmi ja katulamput

Tehty 21.11.2026. Omistajan päätökset: **yksi pelitunti = 10 minuuttia** (vuorokausi 240 min), bussit ja junat ajavat oikeiden aikataulujen kellonaikoja pelin kellosta,
valot **lämpimän keltaisia** (katulamput, ikkunat, kaikki muu) – **paitsi neonvalot**.

| Tiedosto | Sisältö |
|---|---|
| `aika.js` | Kello (`window.__aika`), koko kuvan valosävytys, tähdet, katulamput, kello ruudulla. Ladataan `src/html/99_loppu.html`:ssä. |
| `katuvalo_malli.js` | Katulamppu (omistajan Meshy-malli, harvennettu 1 200 kolmioon): `python tools/aika/tee_katuvalo.py katuvalo_meshy.glb aika/katuvalo_malli.js` |
| Lähde | `hahmot/konseptit/3d_lahde/katuvalo/katuvalo_meshy.glb` |

## Kello: `window.__aika`

`t` (tunnit 0–24), `tunti`, `minuutti`, `paiva`, `teksti()` → "14:30", `valo` (päivänvalo 0–1), `yo` (1 − valo), `rusko` (auringonnousun/-laskun sävy 0–1),
`lamput` (ovatko valot päällä), `valilla(a, b)` (kellonaika välillä, toimii keskiyön yli: `valilla(22, 6)`), `tasatunnein(f)` (kutsu `f(tunti)` aina tunnin vaihtuessa),
`aseta(h)` (kokeiluun: `__aika.aseta(22)`), `kerroin` (ajan nopeus, 1 = normaali), `pysaytetty`.
Peli alkaa klo 9.00; aika tallentuu selaimeen (`localStorage['pori-aika-v1']`) ja jatkuu siitä.

**Aikataulut (bussi, juna, tehtävät):** lue `window.__aika.t` ja vertaa oikean aikataulun kellonaikaan. Esim. juna 14.05: lähtee, kun `t >= 14 + 5/60`.
Aamuhämärä 5.30–7.30, iltahämärä 18.30–20.30 (`paivanvalo()`); lamput syttyvät, kun päivänvaloa on alle 55 %.

## Valo

Pelin valot ja varjot on poltettu ilmakuvaan ja rakennuksiin, joten **varjot eivät käänny**. Vuorokausi tehdään yhdellä sävytyksellä koko kuvaan:
`renderer.toneMapping = CustomToneMapping`, ja three.js:n `tonemapping_pars_fragment`-palaan vaihdetaan funktio, joka kertoo värin yön sinisellä himmennyksellä
(`YO`) ja ruskon sävyllä (`RUSKO`). `toneMappingExposure` kantaa kaksi lukua (kokonaisosa = päivänvalo × 200, desimaalit = rusko / 2). Päivällä kerroin on 1, eli kuva on sama kuin ennen.

- **Hohtava pinta = materiaali, jossa `toneMapped: false`** – se ei himmene yöllä. Näin tehdään lampun lasit, valopisteet, ikkunavalot, ajovalot ja neonkyltit.
  Värinä `LAMMIN` (0xffc47a) kaikessa paitsi neonissa.
- Pelin vanhat lamput (sillat, Eteläranta, korjaamon loisteputket: MeshBasicMaterial väreillä fff3d6 / fff3c4 / fff6dc) merkitään hohtaviksi automaattisesti (`HOHTO`).
- Omat `ShaderMaterial`it, joissa ei ole `#include <tonemapping_fragment>`, eivät himmene (nyt: pilvet).

## Katulamput

Paikat lasketaan `city.js`:n katuverkosta: pääkadut 34 m välein 6,2 m keskilinjasta, kokoojakadut 40 m / 4,8 m, tonttikadut 46 m / 4,0 m (lamppu 75 % koosta), vuorotellen
kadun eri puolilla, ei 14 m lähempänä toista. Talon sisään tai jokeen osuvat jätetään pois (`bldTopAt`, `carGround`). Noin 4 600 lamppua.
Lähellä (240 m, enintään 380 kpl) piirretään malli, hohtava lasi ja valoläikkä maahan; kaikki lamput näkyvät lisäksi valopisteinä (yöllä kaupunki erottuu kopterista).
Oikeita valonlähteitä ei ole – läikkä on kuva maassa.

## Tekemättä (sovittu järjestys)

3. Ikkunoiden valot (julkisivuvarjostin tunnistaa jo lasin: `isG`) ja autojen ajo- ja takavalot. 4. Neonkyltit liiketiloihin (`styles.json` `shop`).
5. Ihmisten ja liikenteen määrä kellon mukaan, kojut ja hahmot aikataulussa, bussi ja juna oikeilla kellonajoilla.
Tiedossa: lamput eivät ole kiinteitä esteitä; lamppuja voi osua pihoille tai puiden sisään (paikat katuverkosta, ei kartoitettu); pilvet eivät himmene yöllä.
