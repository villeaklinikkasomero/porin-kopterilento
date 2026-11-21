# Meshy-promptit tarinan alkuun

Kopioi prompti Meshyn **Text to 3D** -kenttään sellaisenaan. Promptit ovat englanniksi, koska Meshy ymmärtää englantia parhaiten.
Lista perustuu suunnitelmaan `PAIKAT_TARINAN_ALKU.md` (luku 7). Tehdään järjestyksessä, ensin Vauhtis ja M01:n tavarat.

## Asetukset jokaiseen malliin

- **Origin:** Bottom
- **Resize:** taulukon korkeus metreinä (Meshy skaalaa korkeuden mukaan, tarkista leveys)
- **Kolmiot:** 10–20 k (pienet esineet 5–10 k)
- **Tekstuuri:** päällä, PBR
- **Symmetria:** Auto, paitsi jos ohjeessa toisin
- **Ei tekstiä malliin.** Meshy piirtää kirjaimet sotkuisiksi. Kyltit, nimet ja hintataulun tekstit tehdään koodissa, kuten korjaamon kyltti. Promptit pyytävät tyhjää kylttipohjaa.
- **Yksi esine kerrallaan.** Meshy tekee siistimmän mallin yhdestä esineestä kuin kokonaisesta huoneesta. Huone kootaan pelissä.
- Valmis malli kansioon `hahmot/konseptit/3d_lahde/<paikka>/` (esim. `vauhtis/`), nimeksi taulukon tiedostonimi.

Yhteinen tyyli kaikissa: *stylized realistic, game-ready, clean topology, slightly worn* – sama kuin Tapsan halli ja nostin.

---

## 1. Ravintola Vauhtipyörä (Vauhtis) – sali

Rosoinen porilainen rock-baari: tumma puu, punainen nahka, messinki, vanhat keikkajulisteet.

| # | Tiedosto | Koko (l × s × k) | Prompti |
|---|---|---|---|
| 1 | `baaritiski.glb` | 4,0 × 0,8 × 1,1 m | `Long wooden bar counter for a rock bar, dark stained oak front with vertical planks, brass foot rail along the bottom, worn dark countertop, three chrome beer taps on top, simple back edge. Stylized realistic, game-ready, slightly worn, no text, no logos.` |
| 2 | `takahylly.glb` | 3,5 × 0,4 × 2,4 m | `Back bar shelf unit behind a rock bar counter, dark wooden cabinet with three glass shelves full of generic unlabeled liquor bottles, mirror panel at the back, small fridge doors at the bottom. Stylized realistic, game-ready, no text, no logos.` |
| 3 | `jukeboksi.glb` | 0,9 × 0,6 × 1,6 m | `Retro 1960s style jukebox, rounded arched top, chrome trim, warm orange and red glowing plastic panels, glass window showing records, speaker grille at the bottom. Stylized realistic, game-ready, no text, no brand logos.` |
| 4 | `poyta_tuolit.glb` | 1,2 × 0,8 × 0,75 m (tuolien kanssa noin 1,6 m leveä) | `Rectangular dark wooden pub table with two simple wooden chairs with red leather seats, chairs pushed slightly under the table, worn varnish. Stylized realistic, game-ready.` |
| 5 | `baarijakkara.glb` | 0,45 × 0,45 × 0,8 m | `Bar stool with round red leather cushion seat, black steel frame with a footrest ring, slightly scuffed. Stylized realistic, game-ready.` |
| 6 | `loosi.glb` | 1,8 × 1,4 × 1,2 m | `Pub booth seating, two facing red leather benches with high wooden backs and a dark wooden table between them, worn leather. Stylized realistic, game-ready.` |
| 7 | `seinajulisteet.glb` | 1,2 × 0,05 × 0,9 m | `Flat wall panel with a cluster of framed vintage rock concert posters and an electric guitar mounted on the wall, abstract colorful poster art without readable text. Stylized realistic, game-ready, no text.` |

## 2. Vauhtiksen keittiö

Pieni ravintolakeittiö: teräs, valkoinen laatta.

| # | Tiedosto | Koko | Prompti |
|---|---|---|---|
| 8 | `rasvakeitin.glb` | 0,6 × 0,7 × 0,9 m | `Commercial stainless steel deep fryer, floor standing, two fry baskets hanging over the oil vat, control knobs on the front, slightly greasy. Stylized realistic, game-ready, no text.` |
| 9 | `terastaso.glb` | 1,6 × 0,7 × 0,9 m | `Stainless steel restaurant kitchen prep table with an undershelf, cutting board, a few steel bowls and a knife on top. Stylized realistic, game-ready, no text.` |
| 10 | `kylmion_ovi.glb` | 1,0 × 0,2 × 2,1 m | `Walk-in cold room door with frame, brushed stainless steel insulated door, large chrome lever handle, rubber seal, plastic strip curtain visible inside. Stylized realistic, game-ready, no text.` |
| 11 | `liesi.glb` | 1,2 × 0,8 × 0,9 m | `Commercial six burner gas range with oven below, stainless steel, two pots on the burners, steel hood rail above. Stylized realistic, game-ready, no text.` |
| 12 | `takaovi.glb` | 1,0 × 0,15 × 2,1 m | `Restaurant kitchen back door, grey painted steel door with a small wired glass window, push bar, scuffed bottom, metal frame. Stylized realistic, game-ready, no text.` |

## 3. M01:n tavarat (kannettavat)

| # | Tiedosto | Koko | Prompti |
|---|---|---|---|
| 13 | `perunasakki.glb` | 0,5 × 0,3 × 0,7 m | `Full burlap sack of potatoes standing upright, top tied with string, a few potatoes peeking out, rough jute texture. Stylized realistic, game-ready.` (5–8 k kolmiota) |
| 14 | `sipulilaatikko.glb` | 0,5 × 0,35 × 0,3 m | `Wooden market crate full of yellow onions, slatted light wood sides, a few loose onion skins. Stylized realistic, game-ready, no text.` (5–8 k) |
| 15 | `pressu_auto.glb` | 4,7 × 1,8 × 1,5 m | `Old station wagon car completely covered with a dusty grey-green canvas tarp, tarp draped loosely with folds, wheels partly visible at the bottom. Stylized realistic, game-ready.` – Vaihtoehto: pressu tehdään koodissa auton päälle, jos Meshyn muoto ei osu Ramin farmariin. |
| 16 | `torilaatikot.glb` | 1,2 × 0,6 × 0,5 m | `Stack of three wooden market crates with fresh vegetables: potatoes, carrots and onions, on a small wooden pallet. Stylized realistic, game-ready, no text.` (Tertun kojun pöydän taakse) |

## 4. Grilli Kaksi Siivua

Pieni porilainen grilli: valkoinen laatta, punainen ja keltainen, loisteputkivalo.

| # | Tiedosto | Koko | Prompti |
|---|---|---|---|
| 17 | `grillitiski.glb` | 3,0 × 0,8 × 1,1 m | `Small fast food grill counter, white tiled front, stainless steel top with a cash register, glass sneeze guard, flat griddle and a fryer behind the counter side. Red and yellow accents. Stylized realistic, game-ready, no text, no logos.` |
| 18 | `hintataulu.glb` | 2,4 × 0,1 × 0,8 m | `Backlit fast food menu board panel for a wall, three blank light panels with simple food pictograms of a burger, fries and a hot dog, red frame. Stylized realistic, game-ready, no text.` (tekstit koodissa) |
| 19 | `ikkunapoyta.glb` | 2,0 × 0,4 × 1,1 m | `Narrow window bar shelf with three tall red metal stools, white laminate top, fast food style. Stylized realistic, game-ready.` |

## 5. Satakunnan Varaosa

Autotarvikeliike: harmaat metallihyllyt, oranssit hintareunat, betonilattia.

| # | Tiedosto | Koko | Prompti |
|---|---|---|---|
| 20 | `myyntitiski.glb` | 3,0 × 0,8 × 1,0 m | `Auto parts store sales counter, grey laminate with metal edges, computer monitor and keyboard, cash register, parts catalog binders, a few small boxes on top. Stylized realistic, game-ready, no text, no logos.` |
| 21 | `varaosahylly.glb` | 4,0 × 0,6 × 2,2 m | `Auto parts store metal shelving unit, grey steel, five shelves filled with generic oil cans, filter boxes, spark plug packs and wiper blades, orange price strips without text. Stylized realistic, game-ready, no text, no brand logos.` |
| 22 | `rengasteline.glb` | 2,0 × 0,6 × 1,8 m | `Tire display rack, black steel frame holding eight car tires standing upright in two rows, some with alloy rims. Stylized realistic, game-ready, no text.` |
| 23 | `pahvilaatikot.glb` | 1,2 × 0,8 × 1,0 m | `Stack of brown cardboard shipping boxes of different sizes on a wooden pallet, packing tape, generic shipping labels without text. Stylized realistic, game-ready.` (varasto ja laituri, K_NOUTO) |
| 24 | `lastauslaituri.glb` | 4,0 × 3,0 × 1,2 m | `Concrete loading dock platform with black rubber bumpers on the front, yellow and black hazard stripes on the edge, steel stairs on one side. Stylized realistic, game-ready, no text.` |
| 25 | `rullaovi.glb` | 4,0 × 0,3 × 4,0 m | `Industrial roller shutter door with steel frame, closed, horizontal grey corrugated metal slats, slightly dirty bottom edge. Stylized realistic, game-ready, no text.` |

## 6. Autoliike Kiilto

Liian kiiltävä: valkoinen, lasi, kromi – vastakohta Tapsan hallille.

| # | Tiedosto | Koko | Prompti |
|---|---|---|---|
| 26 | `myyjan_poyta.glb` | 1,6 × 0,8 × 0,75 m | `Modern car dealership salesman desk, glossy white top with chrome legs, laptop, brochure stand, business card holder, black leather office chair behind it and two guest chairs in front. Stylized realistic, game-ready, no text.` |
| 27 | `avainkaappi.glb` | 0,6 × 0,15 × 0,8 m | `Wall mounted metal key cabinet with the door open, rows of hooks with many car keys and plastic key tags. Stylized realistic, game-ready, no text.` (M03:n haettava esine, tärkein) |
| 28 | `kahviautomaatti.glb` | 0,6 × 0,6 × 1,8 m | `Office coffee vending machine, black and silver, glossy front panel, cup dispenser slot, a stack of paper cups on the side. Stylized realistic, game-ready, no text, no logos.` |
| 29 | `naytto_jalusta.glb` | 5,0 × 2,5 × 0,15 m | `Low car showroom display platform, glossy white rounded rectangle with a thin chrome edge and small spotlights built into the floor around it. Stylized realistic, game-ready, no text.` (auto pelistä päälle) |
| 30 | `lippusalot.glb` | 0,6 × 0,6 × 6,0 m | `Car dealership flagpole with a tall vertical feather banner flag in plain red and white without text, concrete base. Stylized realistic, game-ready, no text.` |

## 7. Lumin piilo – Isosannan vanha sähköasema

Vanha 1930-luvun muuntamo, jossa hakkeri asuu: teollinen + kotikutoinen tekniikka.

| # | Tiedosto | Koko | Prompti |
|---|---|---|---|
| 31 | `kojetaulu.glb` | 3,0 × 0,6 × 2,2 m | `Old 1930s electrical substation control panel, tall dark green metal cabinet wall with round analog gauges, big black switches and levers, brass details, dusty and worn. Stylized realistic, game-ready, no text.` |
| 32 | `kaapelihylly.glb` | 3,0 × 0,5 × 2,0 m | `Industrial cable tray rack mounted on steel posts, thick black and grey cables running along it, some cables hanging loose, old porcelain insulators. Stylized realistic, game-ready.` |
| 33 | `hakkeripoyta.glb` | 2,0 × 0,8 × 1,4 m | `Messy hacker workstation, long wooden table made from a door on trestles, three computer monitors with glowing blue screens, mechanical keyboard, tangled cables, energy drink cans, a small soldering station. Stylized realistic, game-ready, no text, no logos.` |
| 34 | `valkotaulu.glb` | 1,8 × 0,6 × 1,9 m | `Mobile whiteboard on a wheeled metal stand, blank white board with a few pinned photos and sticky notes, red string connecting some of them, marker tray. Stylized realistic, game-ready, no text.` (kuvat ja kartat vaihdetaan koodissa luku luvulta) |
| 35 | `sohva.glb` | 2,0 × 0,9 × 0,85 m | `Shabby old three seat sofa, faded brown corduroy fabric, sagging cushions, a folded wool blanket and a pillow on it. Stylized realistic, game-ready.` |
| 36 | `drooni.glb` | 0,5 × 0,5 × 0,15 m | `Small quadcopter drone, matte black and dark grey body, four propellers with guards, small camera gimbal underneath, a few stickers without text. Stylized realistic, game-ready, no text.` (myös M05:n paketin sisältö) |

## 8. Tapsan korjaamon toimisto ja taukotila

| # | Tiedosto | Koko | Prompti |
|---|---|---|---|
| 37 | `toimistopoyta.glb` | 1,4 × 0,7 × 0,75 m | `Old garage office desk, scratched grey metal desk with a landline phone, piles of paper invoices, a coffee mug, a desk lamp and a worn office chair. Stylized realistic, game-ready, no text.` |
| 38 | `kahvinkeitin.glb` | 0,6 × 0,5 × 1,0 m | `Small garage break corner: low cabinet with a filter coffee maker with a half full glass pot, a few mismatched mugs and a sugar jar on top. Stylized realistic, game-ready, no text, no logos.` |
| 39 | `ilmoitustaulu.glb` | 1,2 × 0,05 × 0,9 m | `Cork notice board for a car garage wall, wooden frame, pinned paper notes, a calendar page, a few car photos and business cards, all without readable text. Stylized realistic, game-ready, no text.` |
| 40 | `pakettilaatikko.glb` | 0,8 × 0,6 × 0,5 m | `Medium cardboard parcel box sealed with tape, slightly dented corner, courier shipping label without text, fragile sticker shape. Stylized realistic, game-ready, no text.` (M05:n paketti) |

## 9. Julkisivut teollisuushalleihin (vaikeimmat, tee viimeisenä)

Meshy ei osaa tehdä 40–90 m seinää kerralla. Tehdään **yksi julkisivumoduuli**, joka liimataan olemassa olevan hallin seinään; muu halli pysyy ennallaan.
Jos tulos on vino tai sotkuinen, julkisivu tehdään koodissa laatikoista ja tekstuureista (lasiseinä on koodissa helppo).

| # | Tiedosto | Koko | Prompti |
|---|---|---|---|
| 41 | `kiilto_julkisivu.glb` | 14 × 1,0 × 6,0 m | `Modern car dealership storefront facade module, flat wall section with large floor to ceiling glass windows in thin aluminium frames, glass double entrance door in the middle, white metal panel band on top with an empty sign area, no text. Flat back side. Stylized realistic, game-ready.` |
| 42 | `varaosa_julkisivu.glb` | 12 × 1,0 × 5,0 m | `Auto parts store storefront facade module for an old industrial hall, grey corrugated metal wall section with a glass entrance door, two shop windows, a small canopy over the door and an empty sign board above, no text. Flat back side. Stylized realistic, game-ready.` |
| 43 | `vauhtis_ovi.glb` | 3,0 × 0,6 × 3,2 m | `Rock bar street entrance, dark red painted wooden double door with small windows, black metal canopy above with an empty sign board, two wall lamps beside the door, worn stone steps. Flat back side. Stylized realistic, game-ready, no text.` |
| 44 | `grilli_ovi.glb` | 4,0 × 0,6 × 3,0 m | `Small fast food grill shop front, glass door and one large window with a red awning above, empty light box sign board, white tiled wall base. Flat back side. Stylized realistic, game-ready, no text, no logos.` |

---

## Jos tulos ei miellytä

- **Liian siisti:** lisää promptiin `heavily worn, dirty, scratched, used for years`.
- **Liian sarjakuvamainen:** vaihda `Stylized realistic` → `Realistic`.
- **Kirjaimia tuli silti:** Meshyn *Texture*-vaiheessa voi uudelleenteksturoida ja lisätä `blank surfaces`.
- **Väärä mittasuhde:** ota mitat taulukosta ja tarkista Meshyn Resize ennen latausta; kerro tiedosto, niin sovitan mallin koodissa.

Kun malleja on valmiina, kerro mitkä. Ajan ne `tee_mallit.py`:n kaltaisella työkalulla peliin (normaalit kuntoon, valo leivottu pisteväreihin) ja rakennan Vauhtiksen sisätilan.
