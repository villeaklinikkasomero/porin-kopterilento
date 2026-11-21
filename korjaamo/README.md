# korjaamo/ – Tapsan korjaamo

Peltihalli ja nosto-ovi (omistajan Meshy-mallit, 21.11.2026) paikassa **[-598.9, -443.0]**, Äestäjänkadun eteläpuolen tontilla. Ovi katsoo kadulle (8° pohjoisesta itään).

| Tiedosto | Sisältö |
|---|---|
| `korjaamo.js` | Sijoitus, nosto-oven liike, kyltti, sokkeli ja ajoluiska, kiinteät seinät, lattian korkeus. Ladataan `index.html`:n lopussa. |
| `korjaamo_mallit.js` | Halli, ovi, työkaluhylly ja ajoneuvonostin base64-GLB:nä (hallin tekstuuri 2048 px, oven 1024 px; normaalit korjattu ja suuntavalo leivottu pisteväreihin). Tehty `tools/korjaamo/tee_mallit.py`:llä (komento tiedoston alussa). |
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

## Uusi Meshy-kaluste halliin (esim. ajoneuvonostin)

1. Meshy: Origin = Bottom, Resize = oikea koko metreinä (kaksipilarinostin noin 3,4 m leveä × 2,8 m korkea; ajoruutu on 4,4 m leveä), 15–20 k kolmiota, tekstuuri päällä.
2. Kopioi malli kansioon `hahmot/konseptit/3d_lahde/korjaamo/` ja aja `tee_mallit.py` lisäten rivi `nostin=nostin_meshy.glb:1024:0:0.5`.
3. Lisää rivi `korjaamo.js`:n taulukkoon `KALUSTEET`: malli, paikka (x, z mallin akseleissa: ovi on +z-päädyssä, hallin keski 0, 0), kierto ja törmäyslaatikot (`laatikot: [[dx, dz, pitkin z:aa?, puolipituus, puolileveys], …]`).

Nostin ("Weathered Blue Car Lift", 4,1 × 3,8 × 3,4 m) on ajoruudun keskellä; vain pilarit ovat kiinteitä ja auto ajaa niiden välistä. Nostin ei vielä nosta.
