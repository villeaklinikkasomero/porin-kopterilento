# Tavarajuna – Meshy-promptit (21.11.2026)

Samaan putkeen kuin IC-juna (`tools/juna/meshy_juna.py`): Meshy tekee **vain korin**, Blender leikkaa Meshyn telit/alustan pois (`cut`), venyttää korin oikeisiin mittoihin ja lisää `juna_blender.py`:n telit, pyöräkerrat, puskimet ja kytkimet. Siksi promptit pyytävät yksinkertaista alustaa, ei kiskoja eikä maata.

## Meshy-asetukset (kaikille)

- **Text to 3D**, uusin malli, *Symmetry: On*, *PBR: On*, Target polycount 50–100k (harvennetaan Blenderissä).
- Tee jokainen malli **erikseen** (ei koko junaa yhteen malliin). Generoi 3–4 versiota ja valitse suorin/siistein.
- Jos Meshy-versiossa on Negative prompt -kenttä, käytä kaikissa:

```
rails, track, ground, base, platform, scenery, people, text, logos, multiple vehicles, coupled train, cartoon, toy, chibi, exaggerated proportions, bent body, asymmetric
```

- Kuormat (kontit, tukit, hake) tehdään **omina malleinaan**, jotta samaa vaunua voi käyttää tyhjänä tai eri kuormalla → enemmän erilaisia junia vähemmillä malleilla.

---

## 1. Tavarajunan veturi (kori, Meshy → `dr19.glb`)

Moderni kaksivirtaveturi (sähkö + diesel, VR:n uusien Dr19-tyyppinen). Pori–Tampere on sähköistetty, mutta Mäntyluodon satamaraide ei – kaksivirtaveturi sopii molempiin.

```
Modern European six-axle freight locomotive for Finnish broad gauge, realistic, single vehicle, side profile clearly visible. Long boxy body with two identical flat-fronted driver cabs, one at each end, large windscreens, small headlights. Body painted dark green with a wide light grey stripe and yellow-black warning stripes on both ends. Roof with one pantograph, cooling fans and exhaust housing. Smooth flat sides with ventilation grilles and small cab doors. Simple flat underframe, low detail bogies. Clean industrial PBR materials, slightly weathered.
```

Mitat Blenderiin (arvio): kori n. 21,5 × 3,1 m, katto 4,3 m, 3 kaksiakselista telia → käytä kahta kolmiakselista (`wb` 2 × 1,9 m) tai kahta telia keskiöväli ~12 m.

**Vaihtoehto** (vanhempi, punainen diesel, Dr16-henkinen – tuo vaihtelua ja sopii vaihtotyöhön):

```
Classic 1980s European diesel freight locomotive, realistic, single vehicle. Boxy body with two flat-fronted cabs at both ends, angular windows, red lower body with white upper band and grey roof, yellow warning stripes on the front ends. Roof with radiator fans and exhaust stacks, no pantograph. Side grilles along the engine room. Simple flat underframe, low detail bogies. Weathered PBR materials, dirt on lower body.
```

---

## 2. Vaunumallit

### 2a. Liukuseinävaunu (paperi, sellu) – `hbb.glb`

Porin seudun tyypillisin: paperirullat ja sellu Mäntyluotoon.

```
Realistic four-axle European covered freight wagon with sliding walls, single wagon. Long rectangular box body, full-length sliding side wall panels with vertical ribs, curved roof, steel end walls with ladders and handrails. Painted dark red-brown, slightly faded and weathered, small white stencil markings, no readable text. Simple flat underframe, low detail bogies. Side profile clearly visible, symmetric front and back.
```

Mitat: kori 21,0 × 3,2 m, katto 4,6 m.

### 2b. Konttivaunu (tyhjä tasovaunu) – `sgns.glb`

```
Realistic European four-axle container flat wagon, empty, single wagon. Long open steel frame chassis with no walls and no roof, visible I-beam side sills, container locking pins on top, small end platforms with handrails and hand brake wheel. Painted dark grey with orange-yellow accents, weathered and rusty edges. Simple low detail bogies. Side profile clearly visible, symmetric.
```

Mitat: runko 19,6 × 2,9 m, kuormataso 1,15 m.

### 2c. Säiliövaunu (kemikaalit, polttoaine) – `zas.glb`

```
Realistic European four-axle tank wagon, single wagon. Large horizontal cylindrical tank with rounded ends on a steel underframe, walkway on top with railings and a central filling dome, ladders at the middle of both sides, end platforms. Tank painted light grey with an orange hazard band around the middle, darker grey underframe, light weathering streaks. Simple low detail bogies. Side profile clearly visible, symmetric.
```

Mitat: kori 16,0 × 3,1 m, säiliön yläreuna 4,3 m.

### 2d. Pölkky-/tukkivaunu (tyhjä) – `roos.glb`

```
Realistic European four-axle timber log wagon, empty, single wagon. Long flat steel deck with tall vertical steel stakes in pairs along both sides, forming four bays, high end bulkheads made of steel mesh. Painted black and dark brown, rusty and well used. Simple low detail bogies. Side profile clearly visible, symmetric.
```

Mitat: runko 21,0 × 3,0 m, tolppien yläpää 4,2 m.

### 2e. Avovaunu / hakevaunu – `eanos.glb`

```
Realistic European four-axle open-top high-sided gondola freight wagon for wood chips and bulk cargo, single wagon. Tall rectangular open box with vertical external ribs on the sides, no roof, steel end walls with ladders. Painted rusty brown-orange with darker weathering streaks and dents. Simple flat underframe, low detail bogies. Side profile clearly visible, symmetric.
```

Mitat: kori 15,7 × 3,2 m, reunan yläpää 3,9 m.

---

## 3. Kuormat (erilliset mallit)

**40 jalan kontti** – tee 2–3 värillä (sininen, punainen, vihreä); kaksi 20' tai yksi 40' per vaunu.

```
Realistic 40 foot ISO shipping container, single object. Corrugated steel walls, double cargo doors with locking bars on one end, corner castings. Painted deep blue, faded and weathered with rust spots and dents. No logos, no text.
```

**20 jalan kontti**

```
Realistic 20 foot ISO shipping container, single object. Corrugated steel walls, double cargo doors with locking bars on one end, corner castings. Painted red, faded and weathered with rust spots. No logos, no text.
```

**Tukkikuorma** (yksi lohko, monistetaan neljään väliin)

```
Realistic stack of cut pine and spruce logs, 5 meters long, neatly piled into a rectangular block, bark visible, light log ends showing tree rings. Single object, no ground, no straps.
```

**Hakekuorma** (avovaunun täyttö)

```
Heap of light brown wood chips forming a long low mound with a flat top, rectangular footprint, realistic. Single object, no container, no ground.
```

---

## 4. Yhdistelmät (esimerkkejä `juna.js`:n `CONSIST`-listaan)

| Juna | Kokoonpano | Pituus n. |
|---|---|---|
| Paperijuna | Dr19 + 10 × liukuseinävaunu | 230 m |
| Konttijuna | Dr19 + 8 × konttivaunu (sekaisin 40'/2×20', eri värit, osa tyhjiä) | 180 m |
| Kemikaalijuna | Dr19 + 6 × säiliövaunu | 120 m |
| Puujuna | Dr19 + 7 × tukkivaunu (osa tyhjiä) + 3 × hakevaunu | 220 m |
| Sekajuna | Dr16 + 2 × säiliö + 3 × liukuseinä + 2 × konttivaunu + 2 × avovaunu | 190 m |
| Vaihtotyö (ratapiha) | Dr16 + 2–3 satunnaista vaunua | 60 m |

Lisävaihtelua ilman uusia malleja: `flip`-arvon satunnaistus, kuorman puuttuminen, ja Meshyn **Retexture**-toiminto samalle vaunulle (esim. liukuseinävaunu siniharmaana: *"same wagon, painted blue-grey, heavily weathered"*).
