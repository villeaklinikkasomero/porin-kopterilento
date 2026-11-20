# vesi/ – Kokemäenjoen elävä vesi (hybridi)

Tehty 20.11.2026. **`index.html`:ää ei ole muutettu.** Moduuli etsii pelin vesipinnat (tasaiset meshit korkeudella `TER.wl`, joissa on ilmakuva)
ja vaihtaa niiden materiaalin. Geometria ja ilmakuvan UV:t säilyvät.

## Kokeilu

- **Ilman peliä:** `python -m http.server` repon juuressa ja sitten http://localhost:8000/vesi/kokeilu.html
  (hiiri kääntää, rulla vaihtaa korkeutta, W/S liikkuu). `?vanha=1` näyttää nykyisen veden vertailua varten.
  Osoitteessa voi antaa paikan: `?x=40&y=540&alt=6&yaw=-90&pit=-12`.
- **Pelissä:** aloita lento ja kirjoita konsoliin `await import('./vesi/vesi.js')`.
- **Pysyvästi:** lisää `index.html`:n loppuun `<script type="module" src="vesi/vesi.js"></script>`.
- Pois ja takaisin: `__vesi.paalla(false)` / `__vesi.paalla(true)`. Ilmakuvan osuus: `__vesi.asetus('ilmakuva', 0..1)` (oletus 1).

## Mitä tekee

| Osa | Miten |
|---|---|
| **Virtaus kohti merta** | Ladattaessa lasketaan virtauskenttä (8 m ruudukko) `river.js`:n joen rajauksesta. Etäisyys yläjuoksulta (itäpää, x ≈ 1530) uomaa pitkin, ja virran suunta on sen gradientti. Virta kulkee länteen ja delta-haaroja pohjoiseen, kiertää mutkat ja on nopein syvässä keskiuomassa ja hitain rannoilla. |
| **Aallot** | Kaksivaiheinen virtauskartta (flow map): aaltokuvio kulkee virran mukana eikä veny. Lisäksi tuulen väreily ja hidas maininki. Kaukana aallot tasoittuvat. |
| **Syvyys ja väri** | Pohjan korkeus maastomallista (`terrain.js`: `hg`, `wl`). Humuspitoinen ruskehtava joki: matalikot vaaleita ja ruskeita, syvänne tumma. |
| **Heijastus** | Fresnel-taivas ja auringon kimallus pelin auringon suunnasta. |
| **Rannat** | Liikkuva vaalea märkä- ja vaahtokaista, joka peittää joen rajauksen ja ilmakuvan pienet erot. |
| **Hybridi** | Lähellä tehty vesi, kaukana (150–900 m) ilmakuvan sumennettua sävyä enimmillään noin 70 %, jotta joki istuu maisemaan. **Ilmakuvan vaaleat kohteet** (laiturit, ponttonit, veneet, poijut) jäävät näkyviin, koska niitä ei ole vielä mallinnettu. Vesi on ilmakuvassa tummaa (luminanssi alle 0,07), ja kaikki vaaleampi säilyy. |

## Rajapinta veneelle (`window.__vesi`)

```js
__vesi.inRiver(x, y)      // joessa? (sama rajaus kuin pelin inRiver)
__vesi.virtaus(x, y)      // [vx, vy, nopeus] m/s, kohti merta – vene ajelehtii tämän mukana
__vesi.syvyys(x, y)       // m, maastomallista
__vesi.rannalle(x, y)     // etäisyys rantaan (m)
__vesi.korkeus(x, y)      // pinnan korkeus pienine aaltoineen (keinunta)
```

## Tiedossa

- Ilmakuvan ponttonit ja laiturit ovat edelleen litteitä kuvia vedessä. Ne korvataan myöhemmin malleilla, ja silloin `obj`-raja varjostimessa voidaan poistaa.
- Ei peiliheijastusta rakennuksista tai silloista (kallis). Taivas on laskettu kaava.
- Testattu vain `kokeilu.html`:ssä headless-selaimessa (SwiftShader), ei vielä oikeassa pelissä.
