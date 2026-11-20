# tarina/ – Satamakaupungin tehtävämoottori

Tämä kansio on Satamakaupunki-tarinan (PEGI 7) tehtävämoottori Porin kopterilentoon. Tehty 20.11.2026.
**`index.html`:ää ei ole muutettu.** Moottori lukee pelin tilan jo olemassa olevista `window.__*`-olioista
ja piirtää oman käyttöliittymänsä pelin päälle.

- Käsikirjoitus: https://claude.ai/artifact/YYef6VTmqtmEmZJPU8M6mN
- Puuttuvat ominaisuudet: `../tarvittavat_ominaisuudet/README.md`

## Kokeilu

**Ilman peliä:** avaa `tarina/kokeilu.html` paikallisen palvelimen kautta, esim. `python -m http.server` repon juuressa →
http://localhost:8000/tarina/kokeilu.html. Kartta näkyy ylhäältä, ja pelaaja on pallo. Ohjaus: nuolet/WASD, **V** vaihtaa kulkuneuvoa
(jalan → auto → kopteri → pyörä) ja **B** hajottaa kulkuneuvon.

**Oikeassa pelissä ilman index.html-muutosta:** avaa peli, aloita lento ja kirjoita selaimen konsoliin
```js
await import('./tarina/peli.js')
```

**Pysyvä kytkentä** myöhemmin, kun muut chatit ovat valmiita: lisää `index.html`:n loppuun yksi rivi.
```html
<script type="module" src="tarina/peli.js"></script>
```

## Näppäimet

| Näppäin | Toiminto |
|---|---|
| **X** | Aloita tehtävä merkillä / ohita repliikki / jatka tarkistuspisteestä |
| **1–3** | Valinta (vain kun valinta on auki) |
| **P** | Tarinavalikko (tehtävät, raha). Epäonnistumisruudussa P lopettaa tehtävän. |
| **Ctrl+Shift+D** | Kehittäjätila: paikka, vaihe ja liput näkyvät. **O** ohittaa vaiheen. |
| **Ctrl+Shift+K** | Kopioi oma paikka leikepöydälle muodossa `[x, y]`. Käytä tätä paikkojen ja porttien mittaamiseen. |
| **Ctrl+Shift+R** | Nauhoita reitti: aja reitti, ja piste tallentuu 40 m välein. Toinen painallus kopioi pisteet JSON-listana leikepöydälle ja konsoliin (käy suoraan `portit`- tai `reitti`-kentäksi). |

Nämä näppäimet eivät ole pelissä muussa käytössä. Poikkeus: tapaus 1 käyttää numeroita 1–3 otsikon valintaan, ja tapaus 1 poistetaan.
Kosketuslaitteella näkyy **X**-nappi, kun sille on käyttöä.

## Tiedostot

| Tiedosto | Sisältö |
|---|---|
| `moottori.js` | Ydin: tehtävät, vaiheet, liput/muuttujat/esineet, tarkistuspisteet, epäonnistuminen, tallennus. Ei riipu pelistä. |
| `peli.js` | Sovitin: lukee `__walk`/`__car`/`__game.S` ja body-luokat `car`/`walk`, piirtää merkit `__game.sceneen`, näppäimet, oma silmukka. Pelin mekaniikat liitetään kohtaan `KASITTELIJAT`. |
| `hahmot.js` | Tarinan hahmot maailmaan (mallit npc_*.js, Idle-animaatio, kääntyminen pelaajaa kohti) |
| `ui.js` | HUD: tavoite + suuntanuoli ja metrit, mittarit, dialogi, tekstiviesti, valinnat, välianimaation mustat palkit, epäonnistumis- ja läpäisyruutu, valikko, kehittäjäpaneeli |
| `data/tehtavat/Mxx.json` | Yksi tehtävä per tiedosto (nyt Luku 1: M01–M06). Listattava tiedostoon `index.json`. |
| `data/paikat.json` | `LOC_*`-paikat pelin karttametreinä. `tarkista: true` = arvio, mittaa pelissä. |
| `data/maailma.json` | Aina paikalla olevat hahmot (Terttu torilla) |
| `data/hahmot.json`, `data/fi.json` | Hahmojen nimet/värit ja kaikki järjestelmätekstit (lokalisointi) |
| `testi.mjs` | `node tarina/testi.mjs`: 14 testiä, jotka pelaavat Luvun 1 läpi ilman selainta |
| `kokeilu.html` | Pelin korvike tehtävien kokeiluun |

Tallennus: `localStorage['pori-tarina-v1']`. Tallentuu tarkistuspisteissä ja tehtävän lopussa.

## Tehtävän muoto

```json
{
  "id": "M02", "nimi": "Kaksi kuskia", "luku": 1, "antaja": "TAPSA",
  "vaatii": ["FLAG_M01_DONE"],
  "laukaisu": { "tyyppi": "merkki", "paikka": "LOC_KORJAAMO_OVI", "r": 4, "kulku": "jalan" },
  "fail": [ { "ehto": "kulkuneuvo_rikki" }, { "ehto": "nousi_kyydista", "kulku": "auto", "viive": 12, "alkaen": 2 } ],
  "vaiheet": [ ... ],
  "asettaa": { "liput": ["FLAG_M02_DONE"], "muuttujat": { "VAR_X": "+1" }, "esineet": ["ITEM_Y"] },
  "palkinto": { "raha": 200, "teksti": "Kilpa-ajot avautuivat" }
}
```

**Laukaisu:**
- `merkki`: keltainen merkki kartalla, pelaaja tulee siihen ja painaa X
- `automaattinen`: alkaa `viive` sekuntia sen jälkeen, kun tehtävä tulee saataville (esim. puhelu)

**Paikka** voi olla `"LOC_X"`, `[x, y]` tai `{ "paikka": "LOC_X", "dx": 5, "dy": -3 }`.

**Kulkuneuvo** (`kulku`): `jalan`, `auto`, `heli`, `pyora`, `maa` (= ei kopteri) tai `auto:van` / `auto:estate` / `auto:hatch` (myöhemmin `auto:bus`, `auto:sedan`). Voi olla myös lista.

**Vaiheiden yhteiset kentät:**
- `teksti`: tavoite HUDissa (numeroidaan itse)
- `cp: true`: tarkistuspiste ennen tätä vaihetta
- `aikaraja` (s) ja `aikarajaTeksti`
- `ehto`: vaihe ohitetaan, jos ehto ei täyty, esim. `{ "lippu": "X" }`, `{ "muuttuja": "VAR_ALLIES", "vah": 2 }`
- `fail`: vaihekohtaiset epäonnistumisehdot
- `siirto` / `cpSiirto`: paikka, johon pelaaja siirretään tarkistuspisteestä jatkettaessa (vain jalan tai autossa)

**Vaihetyypit:**

| Tyyppi | Kentät | Mitä tekee |
|---|---|---|
| `cut` | `id`, `rivit`, `kamera`* | Välianimaatio: mustat palkit + repliikit |
| `repliikit` | `rivit`, `estaa` (oletus true) | Dialogi. `estaa: false` = puhuvat taustalla, kun seuraava tavoite jo on käynnissä |
| `soitto` | `soittaja`, `rivit` | Puhelu (vihreä reuna, radio hiljenee) |
| `viesti` | `lahettaja`?, `viesti`, `kesto` | Tekstiviesti oikeassa reunassa |
| `mene` | `paikka`, `r`, `kulku`, `merkki`, `korkeintaan` | Mene paikkaan (tarvittaessa tietyllä kulkuneuvolla) |
| `kulku` | `kulku` | Nouse kulkuneuvoon tai siitä pois |
| `portit` | `portit[]`, `r`, `kulku`, `kilpailija {hahmo, aika}` | Kilpa- tai reittiportit järjestyksessä; kilpailijan aika = häviöraja |
| `keraa` | `kohteet[{id, paikka, r, nimi, esine}]`, `tarvitaan` | Poimi esineitä |
| `pysy` | `paikka`, `r`, `s`, `tiukka`, `mittari` | Pysy alueella s sekuntia (esim. "revi tarra") |
| `seuraa` | `reitti[]`, `nopeus`, `min`, `max`, `armo`, `odottaa` | Liikkuva kohde reittiä pitkin, pysy etäisyydellä |
| `valinta` | `kysymys`, `vaihtoehdot[{teksti, asettaa, rivit, ehto}]` | Dialogivalinta 1–3 |
| `aseta` | `asettaa` | Aseta liput/muuttujat kesken tehtävän |
| `odota` | `s` | Tauko |
| `toiminto` | `nimi`, `param`, `failTeksti`, `puuttuuOhita` | Pelin oma mekaniikka (drooni, vesiletku, hiiviskely…). Puuttuva toiminto ohitetaan 4 s päästä, joten tarinan voi pelata läpi jo nyt. |

\* `kamera`: kameran ohjaus välianimaatiossa vaatii koukun pelin kamerasilmukkaan. Kenttä on datassa valmiina, mutta sitä ei vielä käytetä.

**Repliikki:** `["TAPSA", "iloinen", "teksti"]` tai `{ "h": "TAPSA", "tu": "iloinen", "te": "...", "toiminta": true, "kesto": 3 }`.
Tunteet: `neutraali`, `iloinen`, `vihainen`, `yllättynyt`, `huolestunut`, `ovela`.

## Uuden mekaniikan liittäminen (`toiminto`)

```js
// esim. tarina/mekaniikat/vesiletku.js, ja peli.js:ssä KASITTELIJAT.vesiletku = VESILETKU
export const VESILETKU = {
  alku(param, api) { /* luo vartijat param.paikkaan */ },
  paivita(dt, maailma, param, api) { /* ... */ return kaikkiPoissa ? 'valmis' : tarratOvissa >= param.ovet ? 'epaonnistui' : null; },
  loppu() { /* siivoa */ },
  merkit(param) { return [{ x, y, r: 3, laji: 'kohde' }]; }   // valinnainen
};
```
`api.mittari({ laji: 'palkki', nimi, arvo })` näyttää mittarin. `api.vihje(teksti)` näyttää vihjeen, ja `api.aseta({...})` asettaa liput.

## Hahmot maailmassa (`hahmot.js`)

Tarinan hahmot seisovat pelissä omilla malleillaan: `npc_tapsa`, `npc_lumi`, `npc_terttu`, `npc_varjo`, `npc_vartija` ja `npc_myyja`
(repon juuri, klipit Idle/Walk/Run/Dance…). Malli määritellään tiedostossa `data/hahmot.json` (`malli`). **Harjulla ja kuriirilla ei vielä ole mallia** (`malli: null`):
he puhuvat vain ruudulla. Rami on pelaajan oma `hahmo.js`.

Mistä hahmot tulevat (moottorin `hahmolista()` → tapahtuma `hahmot`):
1. `data/maailma.json` `aina`: aina paikalla, esim. Terttu kojullaan torilla. Valinnainen `ehto`.
2. Tehtävän `antaja` odottaa tehtävän merkin vieressä, kun tehtävä on saatavilla (`antajaPaikka`, oletus 2,5 m merkistä itään).
3. Tehtävän `hahmot` ovat paikalla tehtävän aikana. `alkaen`/`asti` = vaiheindeksit, esim. vartijat lähtevät vesiletkuvaiheen jälkeen.
4. Vaiheen `hahmot` ovat paikalla vain sen vaiheen ajan.

Sijoitus: `{ "h": "TAPSA", "paikka": { "paikka": "LOC_KORJAAMO_OVI", "dx": 2 }, "suunta": "pelaaja" | asteet (0 = pohjoinen), "anim": "Idle" }`.
Puhuva hahmo kääntyy pelaajaa kohti. Korkeus tulee pelin `roofAt`-funktiosta (katu, laituri, silta). Mallit ladataan vasta tarvittaessa, kerran per malli.
Kokeilusivulla **Z** vaihtaa lähikuvaan, jossa hahmot näkyvät.

## Raha ja päivän kierros

- **Rahan lähteet:** tehtävien palkkiot (`palkinto.raha`) ja **kyydit**. Pelin oma kyytijärjestelmä (`window.__ride`, Y-näppäin) kerää pisteitä; tarinatilassa jokainen
  kyytipisteet muutetaan rahaksi niin, että **kilometristä saa enintään 10 €** (omistaja 20.11.2026): `KYYTI_EUROA_PISTE = 10 / 150` peli.js:ssä.
  Pisteet ovat suora matka / 10 + enintään 50 % nopeusbonus − kolhut, joten 1 km tuo 6,7–10 €. Tehtävät maksavat 200–300 €.
  Moottorin rajapinta muille lähteille: `__tarina.moottori.lisaaRaha(n, 'lähde')`.
- **Rahan käyttö puuttuu vielä** (ks. `../tarvittavat_ominaisuudet/README.md`).
- **Päivän kierros** (kiertoajelun keltainen majakka ja vasemman yläkulman kortti) piilotetaan tarinatilassa, koska kaksi keltaista merkkiä sekoittaa.
  P-valikosta sen saa takaisin näkyviin (muistetaan: `localStorage['pori-tarina-kierros']`). Piilotus tehdään peli.js:ssä joka ruudulla: majakka on
  `__game.sceneen` lisätty ryhmä, jonka lapset ovat `ring` ja `ring2`, ja kortti on `#mission`. Kun index.html pilkotaan, tämä kannattaa tehdä pelin omana asetuksena.

## Tila ja rajoitukset

- **Testattu:** `node tarina/testi.mjs` (14/14), joka pelaa Luvun 1 läpi ja kokeilee epäonnistumiset, tarkistuspisteet, tallennuksen ja luovutuksen. Lisäksi `kokeilu.html` headless-selaimessa: merkit, dialogi, cut, kilpa, epäonnistumis- ja läpäisyruutu sekä valikko toimivat ilman konsolivirheitä.
- **Ei testattu oikeassa pelissä.** Sovitin olettaa, että `window.__walk.on`, `window.__car.type`, body-luokka `car` ja `__game.S.{x, y, alt, hp, dead}` toimivat kuten 20.11. koodissa.
- **Paikat ovat arvioita** (`tarkista: true`), samoin M02:n kilpaportit. Mittaa ne pelissä kehittäjätilassa (Ctrl+Shift+K).
- Tapsa, Lumi ja muut hahmot eivät vielä näy maailmassa: repliikit tulevat ruudulle, ja Tapsan kilpa on aikaraja. Hahmot tarvitsevat mallit (ks. puuttuvat ominaisuudet).
- **Puuttuvat toiminnot:** hiiviskely, vesiletku, drooni ja Varjo-mittarin varsinainen jahtaus. Ne ohitetaan automaattisesti. `varjo_mittari` näyttää nyt vain tähdet.
- **Merkkien korkeus:** pilari ulottuu 6 m maan alle ja 64 m ylös, joten maaston korkeus ei haittaa. Rengas on tasolla 0.
- **Kun index.html pilkotaan:** `peli.js`:n `maailma()` ja `siirra()` ovat ainoat kohdat, jotka lukevat pelin sisäistä tilaa.
