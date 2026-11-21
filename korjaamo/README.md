# korjaamo/ – Tapsan korjaamo

Peltihalli ja nosto-ovi (omistajan Meshy-mallit, 21.11.2026) paikassa **[-598.9, -443.0]**, Äestäjänkadun eteläpuolen tontilla. Ovi katsoo kadulle (8° pohjoisesta itään).

| Tiedosto | Sisältö |
|---|---|
| `korjaamo.js` | Sijoitus, nosto-oven liike, kyltti, sokkeli ja ajoluiska, kiinteät seinät, lattian korkeus. Ladataan `index.html`:n lopussa. |
| `korjaamo_mallit.js` | Halli ja ovi base64-GLB:nä (hallin tekstuuri 2048 px, oven 1024 px; normaalit korjattu ja suuntavalo leivottu pisteväreihin). Tehty: `python tools/korjaamo/tee_mallit.py halli_meshy.glb nosto_ovi_meshy.glb korjaamo/korjaamo_mallit.js` |
| Lähteet | `hahmot/konseptit/3d_lahde/korjaamo/` |

- **Ovi** rullautuu ylös 2,6 sekunnissa, kun pelaaja (jalan, autolla tai maassa olevalla kopterilla) on alle 10 m ovesta, ja sulkeutuu yli 13 m päässä.
  Käsin: `window.__korjaamo.avaa(true / false)`; tila `window.__korjaamo.auki` (0–1).
- **Sisään** voi kävellä ja ajaa. Seinät ja suljettu ovi ovat kiinteitä: kuusi laatikkoa listassa `window.__furn` (index.html `SOLID`), oven laatikko `gone`, kun ovi on yli puoliksi auki.
- **Lattia:** `window.__korjaamoZ(x, y)` (index.html `carGround` kysyy sitä) = tontin korkein kohta laatan alla + 8 cm; oven edessä 4,5 m ajoluiska maan tasoon.
- **Paikan tai suunnan vaihto:** `PAIKKA` ja `SUUNTA` tiedoston alussa, ja `tarina/data/paikat.json`: `LOC_KORJAAMO` = `PAIKKA`, `LOC_KORJAAMO_OVI` = konsolissa `__korjaamo.oviUlkona`.
- Mallin mitat (oviaukko 4,15 × 3,9 m, seinät 9,7 × 12,2 m) on mitattu Meshyn mallista; uusi hallimalli → vakiot `SEINA_X`, `SEINA_Z`, `LAATTA`, `AUKKO` uusiksi.

- **Ulkoasu (21.11.2026):** `tee_mallit.py` korjaa Meshyn nollanormaalit (mustat laikut seinissä) ja leipoo suuntavalon ja viileämmän sävyn pisteväreihin, koska pelissä on vain
  tasainen taivasvalo. Sisustus ja pihan tavarat tehdään koodissa (`sisustus()`): loisteputket, lattiamaalaus, työpöytä, työkaluvaunu, hylly, renkaat, tynnyrit, lava.

Tiedossa: valot eivät oikeasti valaise (hohtavat vain), ovella ei ole ääntä, katto ei ole kiinteä (kopterilla voi laskeutua läpi), kadun kävelijät eivät tunne hallia.
