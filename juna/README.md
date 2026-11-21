# IC-juna – `juna/`

- `juna.js`: bottijuna. Kokoonpano Edo-ohjausvaunu + 3 kaksikerrosvaunua + Sr3-veturi, 127 m (omistajan valinta 20.11.2026: "Sr3 + vaunut + ohjausvaunu", vain botti).
  - Reitti `RATA.r['1']`: kartan kaakkoisreunalta pääraidetta (Tampereen suunta, 80 km/h) ratapihalle (35 km/h) ja raiteelle 1. Ohjausvaunun keula pysähtyy OSM:n pysähdyspaikkaan (Pori, raide 1).
  - Juna seisoo 150 s ja avaa ovet laiturin puolelle. Sitten se lähtee takaisin veturi edellä, on poissa 150 s ja tulee uudelleen. Pelin alussa juna on jo laiturissa.
  - Telit kääntyvät raiteen mukaan, pyörät pyörivät, ja vaunu kallistuu pituussuunnassa kahden telin korkeuseron mukaan.
  - Ilmoitukset (`toast`), kun pelaaja on alle 450 m:n päässä asemasta.
  - `window.__juna`: `T` (`s` = keulan kohta reitillä, `v`, `mode` = in/dwell/out/away), `cars`, `R`, `STOP`.
- Mallit (21.11.2026): **korit omistajan Meshy-malleista** (Blue Steel Locomotive -> Sr3, Double Decker Train -> Ed, Blue Horizon Express -> Edo), sinivalkooranssi väritys.
  `tools/juna/meshy_juna.py`: Meshyn telit/alusta leikataan pois, kori harvennetaan (Sr3 64 000, vaunut 54 000 kolmiota; `_m` 17–20 000) ja venytetään oikeisiin mittoihin
  (Sr3 kori 18,1 × 3,0 m, katto 3,95 m, virroitin ylhäällä n. 5,5 m; vaunut 25,9 × 3,18 m, katto 5,05 m). Ohjausvaunun ohjaamo on Meshy-mallissa -X-päässä (`flip`).
  Telit, pyöräkerrat, puskimet ja kytkimet tulevat `juna_blender.py`:stä. Tekstuurit `tools/juna/glb_shrink.py`: 2048 px (`_m` 1024 px).
  Ajo: `bl313/bin/python tools/juna/meshy_juna.py -- --src <kansio: loco.glb dd.glb horizon.glb> --out juna --detail high|low`, sitten glb_shrink.py.
  Meshyn lähdemallit (23–71 Mt) eivät ole repossa.
- **Tavarajunan veturi `dr18.glb` / `dr18_m.glb`** (21.11.2026): Dr18-tyyppinen keskiohjaamoinen diesel, omistajan Meshy image-to-3D -malli (vihreä/harmaa).
  Lähde `tools/juna/src/dr18_vr.glb` (83 Mt, ei repossa). `meshy_juna.py --only dr18`: mitat pidetään Meshyn metreinä (15,5 m, katto 3,9 m, pakoputki 4,3 m),
  leveys 3,0 m, telit ±3,95 m (akseliväli 2,95, pyörä r 0,5). Meshyn puskimet ja kytkimet säilyvät. Ei vielä käytössä `juna.js`:ssä.
- **Tavarajunan sähköveturi `srt.glb` / `srt_m.glb`** (21.11.2026): omistajan Meshy-malli, vihreä/harmaa, kolme teliä (B-B-B), virroitin nostettuna (n. 5,4 m).
  Lähde `tools/juna/src/srt_vr.glb` (77 Mt, ei repossa). Kori 18,0 × 3,1 m, katto 4,1 m; telit `Bogie_F/R` ±5,8 m ja `Bogie_M` keskellä
  (`Wheel_M1/2` – `juna.js`:n pyöräregex `/^Wheel_[FR]\d$/` pitää laajentaa `[FRM]`:ksi, kun veturi otetaan käyttöön). Ei vielä käytössä `juna.js`:ssä.
  Vaunujen Meshy-promptit: `tools/juna/meshy_tavarajuna_promptit.md`.
- Vanhat proseduraaliset mallit: `tools/juna/juna_blender.py`
  (`bl313/bin/python tools/juna/juna_blender.py -- --out juna --detail high|low`). Solmut: `Bogie_F/R`, `Wheel_*`, `Door_*`, `Panto_1/2`, `Lamp_F/R`.
  Esikatselu: `tools/juna/view.html?f=edo,ed,sr3&az=40&el=10&d=40` pelin palvelimelta.
- `yhdista.js`: staattiset osat yhteen materiaaleittain (myös rata.js käyttää).

## Meshy (omistajan kysymys 20.11.)
Korit voi tehdä Meshyllä: kolme erillistä image-to-3D-mallia (Sr3, kaksikerrosvaunu, Edo). Ne skaalataan Blenderissä oikeisiin mittoihin
(Sr3 18,98 m, vaunu 26,4 m, origo kiskon tasossa, +Z eteen). Telit, pyöräkerrat, ovet ja virroittimet otetaan `juna_blender.py`:stä samoilla solmunimillä, jolloin `juna.js` toimii sellaisenaan.

## Tavarajunat – `tavarajuna.js` (21.11.2026)
- Junat kulkevat **pelin kellon** (`window.__aika`, aika/aika.js; 1 pelitunti = 10 min) mukaan todellisilla kellonajoilla ja raiteilla (`OHJELMA`,
  Digitraffic 7.–20.11.2026). Viikonpäivä: pelin päivä 1 = maanantai. Ma–pe: Harjavalta–Mäntyluoto 3870–3876 (raiteet 803 ja 2), Viinikan juna 53803 (ti–pe 4.51 raiteelle 810)
  ja 53816 (11.01 pois), vaihtotyöt 65437 (5.00 raiteelta 808 Mäntyluotoon), 11203 (6.18 raiteelta 804) ja 65436 (20.42 raiteelle 804), illalla 3877/3879 raiteelle 808.
  La–su: 3860 lähtee 10.26 raiteelta 808 ja 3855 saapuu 13.30 (oikeasti raiteelle 804, pelissä 808, koska 804:llä seisoo viikonlopun yli 65436).
  Junaa ei ole kartalla ennen aikataulua: saapuva juna lähtee kartan reunalta arvioidun ajoajan verran ennen Porin aikaa. Läpikulkujuna lähtee aikataulun lähtöaikana.
  Pelin alussa ja kellon siirron jälkeen (`__aika.aseta`) ratapihalle asetetaan ne junat, jotka aikataulun mukaan siellä seisovat. Ilman aika.js:ää oma kello klo 9 alkaen.
- Kulunvarmistus: juna lähtee liikkeelle vain, jos reitti seuraavaan pysähdykseen on vapaa muiden tavarajunien varaamista raiteista, ja IC-junan reitille vain,
  kun IC seisoo laiturissa (alle 100 s) tai on poissa; IC odottaa (`window.__tavara.estaaIC()`). Siksi junat voivat myöhästyä muutaman pelikymmenen minuuttia.
  Testattu simuloimalla koko arkipäivä ja lauantai: ei päällekkäisiä junia; saapumiset 0–10 pelimin myöhässä, 803:lta lähtö enintään ~25 pelimin myöhässä.
- Kalusto: veturit `dr18` (diesel) ja `srt` (sähkö, kolme teliä), vaunut `sgns` (konttivaunu, tyhjä), `zas` (säiliö), `roos` / `roos_t` (tukkivaunu tyhjä / tukkikuorma), `hbb` (liukuseinä).
  `KALUSTO`: HVA = srt + 8–12 säiliö- ja liukuseinävaunua, VKA = dr18 + 6–10 puu-, kontti- ja liukuseinävaunua, VAIHTO = dr18 + 2–4 vaunua. Kokoonpano ja vaunujen suunta arvotaan.
  Seisovan junan lähtiessä vastakkaiseen suuntaan veturi siirtyy junan toiseen päähän.
- Nopeus 70 km/h, ratapihalla (1 050 m aseman ympäriltä) 35 km/h, jarrutus ennakoiden. Telit kääntyvät ja pyörät pyörivät (myös srt:n keskiteli `Bogie_M`).
- `juna.js` 21.11.: IC odottaa tavarajunaa (`estaaIC`) ja siirtyy tilaan away vasta, kun koko juna on kartan ulkopuolella (ennen ohjausvaunu ja kaksi vaunua jäivät 150 s:ksi kartan reunalle).
- Mallit `meshy_juna.py`: `--only sgns,zas,roos,roos_t,hbb` (lähteet `tools/juna/src/*_vr.glb`, tukkipino ensin gltfpackilla, ks. SPEC). Desktop-mallit yht. n. 64 Mt, mobiili n. 9 Mt.
- Junat ovat kiinteitä esteitä (21.11.2026, `src/js/090_tormaykset.js`, `SOLID`): IC:n ja tavarajunien vaunut 3,1 m leveinä laatikoina; kävelijä ei astu vaunuun,
  liikkuva juna työntää kävelijän sivuun ja pelaajan auto ei aja vaunuun.
- `window.__tavara`: `S.junat` (liikkeellä: `J.nro`, `tila` odota/ajo/seis, `s`, `v`, `lupa`), `S.pysak` (seisovat junat raiteittain), `R` (reitit), `OHJELMA` (`t0` = kartalle tulon pelitunti).

## Tavarajunien todellinen liikenne (avoin data, 21.11.2026)
- `tavara_aikataulu.js`: Porin, Mäntyluodon ja Tahkoluodon kautta kulkeneet tavarajunat, vaihtotyöt ja veturiajot 7.–20.11.2026 (50 junanumeroa)
  ja 83 raideosuuden ratakilometrit. Päivitys: `node tools/juna/hae_tavarajunat.mjs [päiviä]` (Node 18+, verkkoyhteys). Lähde Fintraffic / digitraffic.fi, CC BY 4.0
  – lähdemaininta pelin tietoihin, jos dataa käytetään.
- Säännöllinen arkiliikenne (ma–pe): Harjavalta (HVA) ↔ Mäntyluoto (MN) 3871/3873/3875 satamaan (Porissa raide 2, pysähdys ~1 min) ja 3870/3872/3874/3876
  satamasta (Porissa raide 803, seisoo 4–40 min); 3877 Harjavallasta Poriin 22.32 (raide 808). Vaihtotyöt Pori–Aittaluoto (ATL) 5.00–6.00 ja 12.00–12.45 (raide 804),
  Pori–Mäntyluoto 5.00 (808) ja paluu 20.04, veturi Pori–Mäntyluoto 6.18. Viikonloppuna vain 3860 (Pori–Harjavalta 10.26) ja 3855 (Harjavalta–Pori 13.30).
  Harvemmin: Viinikka (VKA, Tampere) ↔ Pori (raiteet 807–810), Kouvola ↔ Aittaluoto (operaattori ferfi). Tahkoluotoon ei junia jaksolla.
- Ei saatavilla: tavarajunien kokoonpanot (veturi, vaunut, pituus) ja ratapihalla seisovat vaunut – nämä keksitään (Meshy-mallit + `meshy_tavarajuna_promptit.md`).
- `osuudet` kertoo reitin ratapihan läpi (esim. Tampereen suunnasta raiteelle 803: PRI_838 → 837 → V813 → 820 → V823 → 821 → V825 → V831 → V829 → 803).
  Pelin raiteet: OSM:n `railway:track_ref` on sama numero kuin Digitrafficin raideosuus, ja reitit ovat valmiina `rata/tavara_reitit.js`:ssä (ks. rata/README.md).
