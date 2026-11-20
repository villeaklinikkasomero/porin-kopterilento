# Laskuvarjo päähahmolle (laskuvarjo/)

Päähahmon hyppyvarusteet ja kaikki hypyn vaiheet. **Ei vielä kytketty peliin** – katso vaiheet esikatselusta:
käynnistä pelin paikallinen palvelin ja avaa `/laskuvarjo/esikatselu.html` (aikajana, vaihepainikkeet, vapaa kamera).

## Tiedostot

| Tiedosto | Sisältö |
|---|---|
| `laskuvarjo.js` | `makeRig(root)`: sitoo varusteet hahmon luurankoon ja rakentaa kuvun, punokset, liukurin, kantohihnat, apuvarjon ja sisäpussin |
| `varusteet.js` | Reppuvaljaat, kypärä, lasit ja rannekorkeusmittari verkkona luupainoineen (tehty `tools/hahmo/varusteet.py`:llä) |
| `esikatselu.html` | Koko hyppy 29,5 s aikajanana: hahmo, varusteet, kupu ja hyppykone (`../hyppykone_m.js`) |
| `../hahmo.js` | Uudet klipit: `JumpDoor`, `JumpExit`, `Freefall`, `Pull`, `Opening`, `Canopy`, `CanopyL`, `CanopyR`, `Flare`, `Land` |

## Varusteet

Hihnat on ammuttu säteinä hahmon lepoasennon verkkoon ja jokainen piste perii osumakohdan luupainot, joten valjaat taipuvat
vaatteiden mukana jokaisessa animaatiossa (myös vanhoissa: kävely, juoksu, istuminen). Mukana: pää- ja varavarjon reppu, kantohihnat
olkapäiden yli, rintahihna solkineen, lantiohihnat, reisihihnat, 3-rengaslukot, punainen irtipäästötyyny (oikea), varavarjon
metallikahva (vasen), oranssi apuvarjon kahva repun oikeassa alakulmassa, avokypärä, lasit ja korkeusmittari vasemmassa ranteessa.
Kypärän alla hiukset piilotetaan (`rig.wear(true)`).

Jos hahmon verkko tai luusto muuttuu: `python3 tools/hahmo/varusteet.py hahmo.js laskuvarjo/varusteet.js` (numpy).
Jos hahmo tehdään uudestaan: `python tools/hahmo/kavely_glb.py hahmo.js --add JumpDoor,JumpExit,Freefall,Pull,Opening,Canopy,CanopyL,CanopyR,Flare,Land --clips JumpDoor,JumpExit,Freefall,Pull,Opening,Canopy,CanopyL,CanopyR,Flare,Land`.

## Käyttö pelissä (kun kytketään)

```js
import { makeRig } from './laskuvarjo/laskuvarjo.js';
const rig = makeRig(walkerRoot);          // hahmo.js:n gltf.scene
scene.add(rig.canopy);                    // EI hahmon lapseksi: ryhmä asettuu itse olkapäiden väliin
rig.wear(true);
// joka ruudussa hahmon AnimationMixerin jälkeen:
rig.state.deploy = d;                     // 0..1
rig.canopy.quaternion.copy(q);            // +y kupua kohti (= suhteellista tuulta vastaan), +z lentosuunta
rig.update(seconds);
```

`rig.state`: `pc` (`'stowed'` reppu kiinni · `'hand'` apuvarjo oikeassa kädessä · `'out'` heitetty; kutsu `rig.throwPilot()` heittohetkellä),
`deploy` 0..1, `brakeL` / `brakeR` 0..1 (jättöreuna taipuu, ohjauspunos seuraa kättä kun `toggles` on tosi), `collapse` 0..1 (maassa).

### Vaiheet ja ajoitus (esikatselun mukaan)

| Vaihe | Klippi | Varjo | Vartalon asento |
|---|---|---|---|
| Ovella | `JumpDoor` (silmukka 3 s) | reppu kiinni | pysty, kääntöpiste jaloissa |
| Uloshyppy | `JumpExit` (1,2 s; jalat irti 0,45 kohdalla) | – | kääntyy vatsa maata kohti (pitch 0 → 83°) |
| Vapaapudotus | `Freefall` (silmukka 2 s) | – | vatsa maata kohti; 50 m/s kolmen sekunnin jälkeen |
| Avaus | `Pull` (1,6 s) | `pc = 'hand'` kohdassa 0,40, `throwPilot()` kohdassa 0,62 | – |
| Avautuminen | `Freefall` → `Opening` (2,4 s, alkaa kun `deploy` = 0,33) | `deploy` 0 → 1 noin 4,2 s | pystyyn välillä `deploy` 0,33–0,56, pieni heilahdus |
| Kuvun alla | `Canopy` + `CanopyL` / `CanopyR` painoilla | `brakeL/R` ≤ 0,72, `toggles = true` | kallistus käännökseen ±0,42 rad |
| Loppuveto | `Flare` | `brakeL = brakeR = 1` | vajoaminen 4,6 → 0 m/s sekunnissa |
| Alastulo | `Land` (1,6 s) | `collapse` 0 → 1 noin 2,5 s, `toggles = false` | pysty, kääntöpiste jaloissa |

`deploy`-arvon sisältö: 0–0,15 apuvarjo nousee ja täyttyy · 0,15–0,35 sisäpussi nousee, kantohihnat ja punokset suoriksi · 0,35–0,5 kupu
pussista kapeana, liukuri ylhäällä · 0,5–1 kennot täyttyvät, liukuri valuu alas, apuvarjo lysähtää kuvun taakse.

## Mitat

Kupu 9 kennoa, kärkiväli 7,0 m, jänne 2,5 m (17,5 m², noin 190 ft²), punokset 4,6 m, kantohihnat 0,52 m, yhdyspunos 2,6 m,
apuvarjon säde 0,40 m. Punokset A–D jokaiselta rivalta, A+B etu- ja C+D takakantohihnaan, ohjauspunokset viidestä jättöreunan pisteestä.

## Tiedossa

Kupu on proseduraalinen verkko (ei kangassimulaatiota): avautuminen on käsin ohjattu muodonmuutos lepatuksella. Kangas ei laskostu
maassa, vaan litistyy. Hahmolla on omat vaatteensa (ei hyppyhaalaria). Varavarjoa ja irtipäästöä ei ole animoitu.

## Pelissä (`hyppy.js`)

Kytketty peliin 21.11.2026. Lennä hyppykoneella yli 250 m korkeuteen ja paina **Enter**:

| Vaihe | Näppäimet |
|---|---|
| Vapaapudotus | **Väli** tai **Enter** avaa varjon · A / D kääntää · W liuku eteenpäin |
| Kuvun alla | **A / D** ohjauslenkit · **S** tai **Väli** molemmat alas (jarru; vedä pohjaan 3–5 m ennen maata) |

Automaattilaukaisin avaa varjon 300 m korkeudessa. Kone jatkaa itsekseen ja palaa platalle. Alastulon jälkeen peli jatkuu kävellen.
Moduuli: `window.__jump` (`on`, `ph`, `pos`, `vel`, `agl`, `start()`, `action()`, `step(dt)`, `cam(dt, mode)`); koukut `index.html`issä ja `lento/lento.js`issä.
