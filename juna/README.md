# IC-juna – `juna/`

- `juna.js`: bottijuna. Kokoonpano Edo-ohjausvaunu + 3 kaksikerrosvaunua + Sr3-veturi, 127 m (omistajan valinta 20.11.2026: "Sr3 + vaunut + ohjausvaunu", vain botti).
  - Reitti `RATA.r['1']`: kartan kaakkoisreunalta pääraidetta (Tampereen suunta, 80 km/h) ratapihalle (35 km/h) ja raiteelle 1. Ohjausvaunun keula pysähtyy OSM:n pysähdyspaikkaan (Pori, raide 1).
  - Juna seisoo 150 s ja avaa ovet laiturin puolelle. Sitten se lähtee takaisin veturi edellä, on poissa 150 s ja tulee uudelleen. Pelin alussa juna on jo laiturissa.
  - Telit kääntyvät raiteen mukaan, pyörät pyörivät, ja vaunu kallistuu pituussuunnassa kahden telin korkeuseron mukaan.
  - Ilmoitukset (`toast`), kun pelaaja on alle 450 m:n päässä asemasta.
  - `window.__juna`: `T` (`s` = keulan kohta reitillä, `v`, `mode` = in/dwell/out/away), `cars`, `R`, `STOP`.
- Mallit: `sr3.glb`, `ed.glb`, `edo.glb` (+ kevyet `_m` kosketuslaitteille), tehty proseduraalisesti: `tools/juna/juna_blender.py`
  (`bl313/bin/python tools/juna/juna_blender.py -- --out juna --detail high|low`). Solmut: `Bogie_F/R`, `Wheel_*`, `Door_*`, `Panto_1/2`, `Lamp_F/R`.
  Esikatselu: `tools/juna/view.html?f=edo,ed,sr3&az=40&el=10&d=40` pelin palvelimelta.
- `yhdista.js`: staattiset osat yhteen materiaaleittain (myös rata.js käyttää).

## Meshy (omistajan kysymys 20.11.)
Korit voi tehdä Meshyllä: kolme erillistä image-to-3D-mallia (Sr3, kaksikerrosvaunu, Edo). Ne skaalataan Blenderissä oikeisiin mittoihin
(Sr3 18,98 m, vaunu 26,4 m, origo kiskon tasossa, +Z eteen). Telit, pyöräkerrat, ovet ja virroittimet otetaan `juna_blender.py`:stä samoilla solmunimillä, jolloin `juna.js` toimii sellaisenaan.
