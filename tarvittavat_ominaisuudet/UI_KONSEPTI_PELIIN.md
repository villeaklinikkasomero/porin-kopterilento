# UI-konsepti peliin: tyyli 2010, HUD ja VIUH (suunnitelma 21.11.2026)

Lähde: omistajan kanvaasi **"Porikopteri – tyylikonsepti 2010 ja VIUH-kuljetussovellus"** (https://claude.ai/artifact/75MbscYSPQzHZ9wPUCMYkw, yksityinen).
Kanvaasissa on yhdeksän työpöytää: tyylitaulu, fontit, glyfi-ikonit, HUD, VIUH-näkymät, VIUH-keikat, tulostaulu ja dialogi ja puhelu, AI-kuvien promptit ja aloitussivu.

**Omistajan linjaus 21.11.2026:** *"autoa ja helikopteria ei tarvitse nyt alussa valita, koska pelistä tulee tarinallinen"*.

## 1. Mitä konseptista otetaan sellaisenaan

- **Tyyli:** vuosi 2011. HUD on tummaa läpikuultavaa lasia (#24282E, 86 %), jossa 1 px valoreuna ja pehmeä varjo. Kiilto on vain palkeissa ja painikkeissa, pyöristys 6–10 px. Valkoinen teksti, kontrasti yli 7:1.
- **Paletti:** Viuh-oranssi #FF6A13, kopterinsininen #1E2D6E, kultaraita #E0A526, rahan vihreä #7BD957, varoitus #E5483B, linkki #3B7DD8.
- **Fontit:** Nunito kaikkeen luettavaan, Fredoka isoihin ilmoituksiin ja kapeisiin numeroihin. Molemmat SIL OFL, ja ne tallennetaan repoon `fonts/`-kansioon, ei Google-linkkinä.
- **Ikonit:** glyfi-ikonisarja (24 px, viiva 2,2 px, currentColor) tiedostoon `ikonit.js`. **Emojit pois kaikkialta**, myös tarinan karttamerkeistä: rautalangan 🍔 🍗 ⚙ 🔧 🚐 € vaihdetaan glyfeiksi (ruoka, kauppa, korjaamo, nouto, raha).
- **Yksi puhelin:** VIUH-keikat, tarinan puhelut (`soitto`) ja viestit (`viesti`) tulevat samaan puhelimeen. Moottorissa nämä vaiheet ovat jo valmiina, joten muuttuu vain niiden ulkoasu.
- **Dialogi:** lasipaneeli, jossa puhujan muotokuva (`hahmot/konseptit/muotokuvat`), sekä numeroidut vastausvaihtoehdot. Tarinan `valinta` käyttää jo näppäimiä 1–9.
- **Isot ilmoitukset:** Fredoka (rahat, PERILLÄ, luvun otsikko "LUKU 1 · ETELÄRANTA").

## 2. Mitä muutetaan tarinapainotteiseksi

### Aloitussivu
Konseptin aloitussivussa on valinta Helikopteri / Auto ja painike "Pelaa kopterilla". **Valinta poistetaan.**

- **Pääpainike:** *Aloita tarina*. Jos tallennus on olemassa, painike on *Jatka tarinaa*, ja sen alla näkyvät luku, raha ja pelin kello tallennuksesta.
  Pienellä linkillä *Aloita alusta*, ja se kysyy varmistuksen.
- **Tausta:** Rami Kirjurinluodolla katsomassa Taavi-siltaa ja jokea, eli pelin oikea aloituspaikka. Konseptissa tausta on Eteläranta.
- **Teksti:** "Lennä, aja ja kävele koko Porin keskustassa" painottaa nyt kopteria. Uusi järjestys:
  1. tarina ("Kymmenen vuotta poissa…")
  2. kävely, pyörä ja auto kaupungissa
  3. kopteri "myöhemmin tarinassa"
- **"Kolme tapaa pelata":** Tarina → VIUH-keikat → Päivän kierros. Päivän kierroksessa on lukko ja teksti "Avautuu, kun saat kopterin (luku 3)".
- **Päivän kierros ja top-10:** avautuvat, kun `FLAG_HELI_AUKI` on tallennuksessa. Vasta silloin kopterin ja auton valinta palaa, ja vain kierrokselle.
- Kirjautuminen tai nimimerkki top-10:tä varten kysytään vasta, kun kierros avautuu.

### HUD
| Konseptin osa | Pelissä nyt | Muutos |
|---|---|---|
| 1 Tehtäväpaneeli | `#mission` (päivän kierros) + tarinan tavoiterivi (ui.js) | **Yksi paneeli:** tarinan tavoite ja tarkistuspisteen edistyminen kultapalkkina; päivän kierros vain kun se on päällä |
| 2 VIUH-nauha | – | Keikan aikana (uusi) |
| 3 Minikartta | on (kopterikartta) | Pyöreä, vaalennettu ilmakuva, reitti ja kohde oranssilla. Tarinan merkit ovat glyfejä. |
| 4 Ilmoitus | toast + tarinan ilmoitus | Fredoka-iso, ja selite lasipillerissä |
| 5 Mittaristo | nopeus ja korkeus | Nopeus, kunto (10 palaa) **+ ENERGIA** (konseptista puuttuu, `talous.js` → korvaa rautalangan `#tr-energia`). Korkeus vain kopterissa |
| 6 Radio | `#gradio`, `#radio` | Kanavan kansikuva, kappale ja napit. Jalan radio on hiljaa (korjattu). |
| 7 Kadunnimi | on | Iso valkoinen teksti varjolla. Sisätiloissa rakennus ja huone (sisätilatuki, ks. PAIKAT_TARINAN_ALKU.md). |
| 8 Puhelin | – | VIUH + tarinan puhelut ja viestit |
| Kosketusnapit | emojinapit | Glyfi-ikonit ja kiiltävät neliöt. Kopterinapit (nouse/laskeudu) näkyvät vasta, kun kopteri on auki. |

### VIUH ja tarina
- **Tarinan mikrotehtävät siirtyvät VIUHiin:** ne eivät ole enää karttamerkkejä, vaan keikkapyyntöjä puhelimessa.

  | Nykyinen | VIUH-tyyppi |
  |---|---|
  | S_SIIVET | KYLMÄ (lämpö laskee) |
  | S_GRILLI | PYÖRÄ / KIIRE |
  | S_KUKAT | ARKA (Tertun kukat, ehjyys) |
  | S_RENKAAT | PAKETTI, pakettiautolla |
  | S_ILMAKUVA | ILMA, vasta kun kopteri on auki |
  | kadun kyydit | HENKILÖ |

- **Tarinan sisällä pysyvät ennallaan:** kaupat (Kaksi Siivua, Vauhtis, Satakunnan Varaosa) ja korjaamo (korjaus, tuunaus, nouto). Niissä käydään paikan päällä, ja niihin mennään sisään.
- **VIUH avautuu tarinassa:** M01:n jälkeen Tapsa asentaa Ramin puhelimeen VIUHin ("Tällä saat bensarahat"). Ensimmäiset keikat tehdään pyörällä, autolla M02:n jälkeen ja kopterilla M16:n jälkeen,
  eli sama ajoneuvojen eteneminen kuin tarinassa.
- **Raha:** VIUH maksaa samaan kukkaroon kuin tehtävät (`tila.raha`). Konseptin kaava on suora matka/10, nopeuslisä enintään +50 % ja kolhut −2 %/hp, eli sama kuin kyydeissä nyt.
- **Hopeakuski** (10 keikkaa, arvio yli 4,5) avaa ARKA-keikat. ILMA-keikat vaativat lisäksi `FLAG_HELI_AUKI`.
- **Energia:** VIUH-keikka ei ala nälkäisenä, samoin kuin muut keikat. Puhelin näyttää "Syö ensin – lähin: Kaksi Siivua 600 m".

## 3. Toteutusjärjestys

**Tehty 21.11.2026 (vaiheet 1 ja 2):**
- `fonts/nunito.woff2`, `fonts/fredoka.woff2` (latin, muuttuvat fontit, @fontsource-variable 5.3.0) + `fonts/OFL.txt`. `@font-face` ja CSS-muuttujat (`--viuh`, `--sininen`, `--kulta`, `--raha`, `--lasi`, `--kiilto` …) tiedoston `src/css/peli.css` alussa; apuluokat `.ik`, `.iso` (Fredoka-otsikot), `.kapea` (numerot), `.lab`.
- `.panel` = konseptin lasi (tumma liukuväri 86 %, 1 px valoreuna, varjo). Mittariston numerot, kadunnimi, ilmoitus ja navigaattorin matka Fredokalla; edistymispalkki kultaa.
- `ikonit.js` (tavallinen skripti `<body>`:n alussa): konseptin 25 glyfiä + 15 lisättyä samaan tyyliin (ruoka, kauppa, korjaamo, pakettiauto, auto, kopteri, lukko, energia, tarina, kartta, kello, varoitus, toisto, edellinen, alas).
  HTML: `<svg class="ik"><use href="#ik-radio"/></svg>`, JS: `window.ikoni('radio')`. Kosketusnapit, radio ja kävelyvihje käyttävät niitä; emojit poistettu niistä.
- **Aloitussivu** (`src/html/01_runko.html` #start, logiikka `src/js/130_tulostaulu.js`): vasemmalla sarjakuvaruutu (Rami ja Tapsa, omistajan Gemini-renderöinnit `ui/hahmot/`), oikealla sininen ruutu: otsikko, tarinateksti,
  pääpainike *Aloita tarina* / *Jatka tarinaa* (Enter), tallennuksen rivi "Luku 3 · tehtävän nimi · 340 €" ja *Aloita alusta* (varmistus sivulla). "Kolme tapaa pelata" -kortit; päivän kierros lukossa.
  Kun tallennuksessa on `FLAG_HELI_AUKI`, näkyvät kopteri/auto-valinta, päivän reitti ja painike *Lennä/Aja päivän kierros* (`begin('kierros')`). Näppäimet kokoontaitettavana.
- `begin(tila)`: `window.__pelitila` = 'tarina' | 'kierros' ja tapahtuma `pori-aloita`; `tarina/peli.js` näyttää kierroksen kortin ja majakan vain kierroksella. Tarinassa ajoneuvoksi pakotetaan kopteri (piilossa lukon takia) eikä `pori-veh`-valintaa muuteta.
- `tarina/peli.js` kirjoittaa 2 s välein `localStorage['pori-tarina-yhteenveto']` = { luku, nimi } aloitussivua varten. HUD on piilossa, kunnes peli alkaa (`body.aloitettu`).
- Omistajan linjaus: **käyttöliittymässä vain renderöidyt kuvat** (ei piirrettyjä muotokuvia `hahmot/konseptit/muotokuvat`).

| # | Työ | Tiedostot | Koko |
|---|---|---|---|
| 1 ✅ | **Pohja:** fontit repoon, HUD-lasin CSS-muuttujat ja -luokat, `ikonit.js` (konseptin sarja) | `src/css/peli.css`, `fonts/`, `ikonit.js` | 1 istunto |
| 2 ✅ | **Aloitussivu tarinalle:** ei ajoneuvovalintaa, Aloita/Jatka tarinaa, päivän kierros lukossa M16:een | `src/html/01_runko.html`, `src/js/130_tulostaulu.js` (`begin`), `src/js/081_auto.js` (`pori-veh`) | 1 istunto |
| 3 | **Tarinan UI uuteen asuun:** dialogi muotokuvin, valinta, luvun otsikko, ilmoitukset, puhelin tarinan puheluille ja viesteille | `tarina/ui.js`, `tarina/peli.js` | 1–2 istuntoa |
| 4 | **HUD:** tehtäväpaneeli, mittaristo + kunto + energia, radio, kadunnimi, kosketusnapit glyfeinä, karttamerkit glyfeinä | `src/js/123_hud.js`, `111_radio.js`, `tarina/talous.js`, `tarina/ui.js` | 2 istuntoa |
| 5 | **VIUH:** `moduulit/viuh.js` (logiikka), `viuh/puhelin.js` (UI), `viuh/keikat.json`. Mikrotehtävät S_* siirretään, ja kyydit kulkevat puhelimen kautta. | uusi + `moduulit/kyydit.js` | 2–3 istuntoa |
| 6 | **Top-10 ja päivän kierros** uuteen asuun, avautuvat M16:ssa | `src/js/130_tulostaulu.js` | 1 istunto |

Vaiheet 1–3 ennen sisätilatyötä (PAIKAT_TARINAN_ALKU.md kohta 8), koska Vauhtiksen ja korjaamon kohtaukset näyttävät silloin heti oikealta.

**Työnjako keskustelujen kesken:** konsepti tehtiin toisessa langassa. Jotta kaksi istuntoa ei kirjoita samoja tiedostoja, jokaisella tiedostolla on yksi tekijä kerrallaan.
Kirjataan SIIRTO-tiedostoon, kuka tekee vaiheet 1–6.
