# src/ – index.html paloina

**index.html kootaan tämän kansion paloista. Älä muokkaa index.html:ää suoraan, vaan muokkaa palaa ja kokoa.**
Jaettu 21.11.2026, jotta usea chat voi työskennellä yhtä aikaa eri tiedostoissa.

## Työtapa

```
python tools/osat/kokoa.py               # palat → index.html (aja jokaisen muutoksen jälkeen)
python tools/osat/kokoa.py --tarkista    # vastaako index.html paloja? (myös GitHubissa jokaisella pushilla)
python tools/osat/pilko.py               # index.html → palat (jos index.html:ää muokattiin suoraan, esim. tools/rata/patch_index.py)
```

1. **Yksi chat per pala kerrallaan.** Kerro siirtolokissa, mitä palaa muokkaat. Kaksi chattia samassa palassa = sama ongelma kuin ennen.
2. **Lue pala laitteelta juuri ennen muokkausta ja kirjoita heti.** Älä kirjoita vanhasta kopiosta.
3. Kokoa (`kokoa.py`) ja tarkista (`--tarkista`) ennen commitia. Commitoi sekä pala että index.html.
4. **Uusi ominaisuus omaksi palakseen** (esim. `js/1555_tuunaus.js`): lisää rivi `osat.txt`:hen oikeaan kohtaan ja kokoa.
   Vielä parempi: oma moduulikansio kuten `tarina/`, `korjaamo/`, `rata/`, ladattuna `html/99_loppu.html`:ssä.
5. Palat ovat **yhtä ja samaa moduulia**: ne näkevät toistensa muuttujat (`scene`, `S`, `WALK`, `ROAD`…) kuten ennenkin.
   Järjestyksellä on väliä samoin kuin ennen. Pala voi alkaa tai loppua kesken lohkon (esim. `150–156` ovat yhden aaltosulkulohkon osia),
   joten pala ei välttämättä ole yksinään jäsentyvää JavaScriptiä.

## Oikeat moduulit (`moduulit/`, 21.11.2026)

13 palaa on siirretty **oikeiksi ES-moduuleiksi** kansioon `moduulit/`. Niiden pala `src/js/…` on nyt vain lyhyt kutsu samassa kohdassa kuin ennen:

```js
import kaynnista_linnut from './moduulit/linnut.js';
kaynnista_linnut({ TZs, inRiver, scene, ROAD, get VEH() { return VEH; }, carGround, bldTopAt, S, WALK });
```

- Moduuli on muotoa `export default function kaynnista(P) { … }`. Pääskriptin muuttujat käytetään muodossa `P.scene`, `P.S`, `P.WALK`…
  Muuttujat, joihin pääskripti kirjoittaa myöhemmin uuden arvon (`VEH`, `started`, `camMode`, `soundOn`…), välitetään **gettereinä** (`get VEH() { return VEH; }`),
  jotta moduuli näkee aina tuoreen arvon. Jos moduuli kirjoittaa pääskriptin muuttujaan, kutsussa on myös setteri.
- Kirjastot ja data (three, GLTFLoader, city.js, roads.js…) moduuli tuo itse (`import … from '../three.module.min.js'`). `fetch`- ja tekstuuripolut ovat ennallaan
  (ne lasketaan sivun osoitteesta), mutta moduulin sisäiset dynaamiset `import()`-polut ovat muotoa `'../x.js'`.
- **Moduuli ei näe pääskriptin muuttujia suoraan.** Jos tarvitset uuden pääskriptin muuttujan moduulissa, lisää se kutsun P-olioon (palassa `src/js/…`) ja kokoa.
  Unohtunut riippuvuus näkyy konsolissa `undefined`-virheenä.
- Jos moduuli antaa jotain takaisin pääskriptille, se palauttaa olion: `tanssi.js` → `const { DANCE } = kaynnista_tanssi({…})`.
- Muokkaa moduulia suoraan (`moduulit/x.js`), **kokoamista ei tarvita**, ellet muuta kutsua. Moduulin muutokset eivät koske index.html:ää eivätkä muita paloja.

| Moduuli | Pala (kutsu) |
|---|---|
| `moduulit/kivipori_maamerkit.js` | `js/041_kivipori_maamerkit.js` |
| `moduulit/etelaranta.js` | `js/050_etelaranta.js` (Etelärannan laituri; testikopiot lukevat sen nyt täältä) |
| `moduulit/kauppatori.js` | `js/051_kauppatori.js` |
| `moduulit/puut.js` | `js/070_puut.js` |
| `moduulit/hautausmaat.js` | `js/101_hautausmaat.js` |
| `moduulit/kavelijat.js` | `js/140_kavelijat.js` |
| `moduulit/patsaat.js` | `js/150_patsaat.js` |
| `moduulit/linnut.js` | `js/153_linnut.js` |
| `moduulit/kespan_lenkki.js` | `js/154_kespan_lenkki.js` |
| `moduulit/pyorat.js` | `js/156_pyorat.js` |
| `moduulit/kyydit.js` | `js/160_kyydit.js` |
| `moduulit/tanssi.js` | `js/161_tanssi.js` |
| `moduulit/bussi.js` | `js/170_bussi.js` |

**Tarkoituksella pääskriptiin jätetyt:** `js/180_lentoasema.js` (`tools/rata/patch_index.py` hakee sen tekstistä ankkureita `const RSZ` ja `const tri`),
sekä pelin ydin (maasto, renderöijä, kadut, ajoneuvot, törmäykset, tila, simulaatio, kamera, HUD, silmukka), jota lähes kaikki muu käyttää.
Siirrä lisää samalla mallilla, kun pala alkaa olla usean chatin työmaa. Testi: pelin objektimäärä ja `window.__*`-rajapinnat ennen ja jälkeen samat.

**Merkintärivit:** index.html:ssä jokaisen palan alussa on kommentti `// @osa js/111_radio.js` (CSS:ssä `/* … */`, HTML:ssä `<!-- … -->`).
Älä poista niitä: `pilko.py` löytää palojen rajat niistä. Selaimen virheilmoituksen rivinumerosta näet palan etsimällä lähimmän `@osa`-rivin ylöspäin.

**Suojat:**
- `kokoa.py` pysähtyy, jos index.html:ää on muokattu suoraan palan jälkeen.
- `pilko.py` pysähtyy, jos pala on uudempi kuin index.html (molempia muokattu). Tällöin yhdistä käsin; `--pakota` ohittaa.

**Työkalut, jotka lukevat index.html:ää** toimivat ennallaan: `tools/solid_test.js` (SOLID on palassa `js/090_tormaykset.js`) ja
`tools/rata/patch_index.py` (muokkaa index.html:ää → aja sen jälkeen `pilko.py`).

## Palat

| Pala | Rivejä | Sisältö |
|---|---|---|
| `html/00_alku.html` | 7 | doctype, head, meta |
| `css/peli.css` | 105 | kaikki CSS (HUD, kortit, napit, kosketus) |
| `html/01_runko.html` | 75 | body-HTML: HUD-elementit, napit, intro; avaa pääskriptin |
| `js/000_tuonnit.js` | 19 | importit (three, GLTFLoader, data: city, terrain, roads, RATA…) |
| `js/010_maasto.js` | 91 | maasto TER/TZg/TZs, jokiuoma, siltakummut, `isTouch` |
| `js/0105_tie_kaytava.js` | 20 | Luvianpuistokadun/Maamiehenkadun käytävä kahdessa tasossa (`tie/tie_data.js`), roads.js-laajennus Tiilimäelle ja Isomäelle |
| `js/020_renderoija.js` | 83 | renderer, scene, kamera, valot |
| `js/030_maa_ilmakuva.js` | 45 | maa ja ilmakuva |
| `js/0301_sillat.js` | 60 | maasillat (TER.bd): betoni, asfalttikansi, maatuet, auto kannella (`silta/`) |
| `js/031_maa_nurmi.js` | 24 | nurmitekstuuri |
| `js/032_heina.js` | 71 | korkea heinä (instanssit) |
| `js/033_ilmakuva_tarkka.js` | 26 | tarkka ilmakuva (WMS-ruudut) |
| `js/0335_tie_maa.js` | 25 | käytävän 1 m maapinta 6 m ruudukon aukkoon |
| `js/040_rakennukset.js` | 314 | rakennukset (LoD2, julkisivut, katot) |
| `js/041_kivipori_maamerkit.js` | → moduuli | Kivi-Porin maamerkit, sillat (kaiteet, valot) |
| `js/050_etelaranta.js` | → moduuli | Eteläranta (laituritaso, portaat, alikulku) |
| `js/051_kauppatori.js` | → moduuli | Kauppatorin kiveys |
| `js/060_kadut.js` | 213 | kadut geometriana (roads.js), `ROAD` |
| `js/061_kaupunkilohkot.js` | 68 | kaupunkilohkot bl_*.js (suoratoisto), `loadModel` |
| `js/070_puut.js` | → moduuli | puut |
| `js/071_tekstit.js` | 12 | tekstiapurit |
| `js/072_katunimet.js` | 38 | katujen nimet maassa |
| `js/073_maamerkit_kierros.js` | 58 | maamerkit, päivän kierros (TOUR, setTarget) |
| `js/080_kopteri.js` | 47 | helikopteri |
| `js/081_auto.js` | 33 | pelaajan auto, `VEH` |
| `js/082_pysakointihalli.js` | 33 | pysäköintihalli (testi), **`carGround`** (auton/jalan maanpinta: koukut `__quayZ`, `__korjaamoZ`, `__rataZ`) |
| `js/090_tormaykset.js` | 146 | SOLID: törmäykset (tools/solid_test.js) |
| `js/091_navigaattori.js` | 58 | auton navigaattori |
| `js/092_liikenne.js` | 156 | bottiliikenne, liikennevalot |
| `js/100_tila.js` | 67 | pelin tila `S`, `roofAt`, `setTarget` |
| `js/101_hautausmaat.js` | → moduuli | hautakivet |
| `js/110_syote.js` | 42 | näppäimistö ja kosketus |
| `js/111_radio.js` | 26 | radio (2 kanavaa) |
| `js/112_aani.js` | 16 | äänet |
| `js/120_simulaatio.js` | 86 | fysiikka: kopteri ja auto, `step()` (koukku `__jump`) |
| `js/121_jalan.js` | 165 | jalan: WALK, kävely, sisätilat, kirkko |
| `js/122_kamera.js` | 39 | kamera, `updateCamera` |
| `js/123_hud.js` | 59 | HUD |
| `js/124_silmukka.js` | 12 | pääsilmukka frame() |
| `js/130_tulostaulu.js` | 87 | päivän top-10 (Firebase) |
| `js/140_kavelijat.js` | → moduuli | kävelijäbotit, istumapaikat, kädet |
| `js/150_patsaat.js` | → moduuli | patsaat |
| `js/151_savu.js` | 21 | savu |
| `js/153_linnut.js` | → moduuli | linnut |
| `js/154_kespan_lenkki.js` | → moduuli | Kespan lenkki -kilpa |
| `js/155_auton_lainaus.js` | 57 | pysäköidyn auton lainaus |
| `js/156_pyorat.js` | → moduuli | polkupyörät |
| `js/160_kyydit.js` | → moduuli | kyydit |
| `js/161_tanssi.js` | → moduuli | musiikki ja tanssi |
| `js/170_bussi.js` | → moduuli | kaupunkibussi |
| `js/180_lentoasema.js` | 230 | Porin lentoasema EFPO, hyppykone |
| `js/990_kaynnistys.js` | 8 | walkOutAt, window.__game, käynnistys |
| `html/99_loppu.html` | 19 | pääskriptin loppu + erilliset moduulit (vesi, tori, ranta, lento, laskuvarjo, rata, juna, korjaamo, tarina) |

Jako tehty lohko-otsikoiden (`// ---------- … ----------`) mukaan. Kun pala kasvaa yli ~400 rivin, jaa se: katkaise sopivasta kohdasta uudeksi tiedostoksi
ja lisää rivi `osat.txt`:hen. Tulos on sama peli, kunhan teksti pysyy samassa järjestyksessä.
