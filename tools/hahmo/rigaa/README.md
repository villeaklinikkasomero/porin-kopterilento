# rigaa.py – kuvasta tehdyn mallin liittäminen pelin luurankoon

Ottaa Meshyn (tai muun kuvasta 3D:ksi -työkalun) GLB-mallin ja tekee siitä pelin NPC-hahmon:

- **Luuranko:** sama 53 luun luuranko kuin `npc_*.js`:ssä ja `hahmo.js`:ssä (pelvis, spine_01…, thigh_l…). Nivelet sovitetaan mallin mittoihin automaattisesti: kädet ja jalat mallin raajojen akselille, ja muut mittasuhteet skaalataan pituuden mukaan.
- **Painot:** siirretään `npc_mies_a`:n verkosta lähimpien pisteiden perusteella, ja vasen ja oikea puoli pidetään erillään.
- **Animaatiot:** `npc_mies_a`:n klipit (Idle, Walk, Chair, Dance, Dance2, Passenger…) ja Ramin Run. Kiertoliikkeet säilyvät sellaisinaan, ja lantion siirtymä skaalataan uuteen pituuteen.
- **Tekstuurit:** pienennetään 1024²:een, metallisuus- ja karheuskartta jätetään pois (karheus 0,8).

```
pip install numpy scipy pillow
python rigaa.py malli_meshy.glb ulos.glb --lahde ../../npc_mies_a.glb --lisaklipit ../../hahmo.glb:Run
```
`npc_mies_a.glb` ja `hahmo.glb` puretaan `.js`-tiedostoista (base64). JS-moduuliksi: `export default "<base64>"`.

Meshyn asetukset: Smart Topology, 15–20k kolmiota, Texture päällä, **Pose: A-Pose**, latauksessa Resize = hahmon pituus ja Origin = Bottom.
Älä käytä Meshyn omaa luurankoa tai animaatioita.

Rajoitukset: sormet seuraavat kättä jäykästi (NPC:n sormiasento). Ruutukuvio venyy nivelissä hieman.
Naishahmoille käytä lähteenä `npc_nainen_a`:ta tai `npc_nainen_b`:tä (`--lahde`). Hameelle tai pitkälle helmalle lisää `--hame`, joka jakaa reisien välisen kankaan painot tasaisesti, jottei helma revi kahdeksi lahkeeksi.

Lisävalinnat (21.11.2026): `--pituus 1.84` skaalaa mallin annettuun pituuteen (m) ennen sovitusta. `--reppu` on hahmolle, jolla on reppu tai muu iso
kantamus selässä: vartalon syvyyskeskikohta mitataan reisistä, ettei selkäranka siirry repun sisään. `--nimi` = materiaalin nimi.

```
python rigaa.py harju_meshy.glb harju_rig.glb --lahde npc_mies_a.glb --lisaklipit hahmo.glb:Run --nimi harju --pituus 1.84
python rigaa.py kuriiri_meshy.glb kuriiri_rig.glb --lahde npc_mies_a.glb --lisaklipit hahmo.glb:Run --nimi kuriiri --pituus 1.76 --reppu
python rigaa.py vartija_b_meshy.glb vartija_b_rig.glb --lahde npc_mies_a.glb --lisaklipit hahmo.glb:Run --nimi vartija_b --pituus 1.68
python rigaa.py vartija_c_meshy.glb vartija_c_rig.glb --lahde npc_nainen_a.glb --lisaklipit hahmo.glb:Run --nimi vartija_c --pituus 1.72
```
T-asennossa tehty malli (Harju) toimii myös: käsivarren akseli haetaan verkosta ja painot siirretään uuteen sidosasentoon.
