# Hyppykone OH-HPX

Cessna 182 -tyyppinen yläsiipinen laskuvarjohyppykone (20.11.2026). Peli lähtee lentokentältä, ja pelaaja hyppää koneesta pelialueen yllä.

## Tiedostot

- `../../../hyppykone.js`, `../../../hyppykone_m.js`: pelin mallit (base64-GLB kuten `heli.js` ja `vene.js`). `_m` on kevyempi kosketuslaitteille (noin 72 000 kolmiota ja 1024 px tekstuurit; täysi versio noin 106 000 kolmiota ja 2048 px).
- `build3.py`: proseduraalinen malli (trimesh, manifold3d, shapely, PIL, scipy). `LITE=1 python3 build3.py` tekee kevyen version. Tulos: `out/hyppykone.glb`.
- `make_game_js.py`: tekstuurit JPEG-muotoon ja kokorajaan. Sen jälkeen ajetaan `gltf-transform quantize` (KHR_mesh_quantization, three.js:n GLTFLoader tukee ilman dekooderia), ja lopuksi GLB kääritään `export default "..."` -moduuliksi.
- `render_blender.py`: Cycles-esikatselu (Blender 5 / bpy), `render_*.jpg`.

## Koordinaatit

Keula +Z, origo pyörien kohdalla maan tasossa, Y ylös, vasen kylki +X. Pelissä `root.rotation.y = PI` kuten helikopterilla.
Mitat: pituus 9,3 m, kärkiväli 11,1 m, korkeus 2,95 m.

## Solmut

| Solmu | Pivot | Liike |
|---|---|---|
| `propeller` | navan keskellä | pyörii paikallisen Z:n ympäri |
| `door` | yläsarana | paikallinen Z, negatiivinen = auki ylös siiven alle (Cessna 182:n hyppyovi, oikea kylki) |
| `aileron_port`, `aileron_stbd`, `flap_port`, `flap_stbd` | saranalla | paikallinen X |
| `elevator` | saranalla | paikallinen X |
| `rudder` | saranalla | paikallinen Y |
| `exit_point` | tyhjä | askelma oikean päätelineen jalassa, hyppääjä kasvot menosuuntaan |
| `pilot_seat` | tyhjä | ohjaajan istuin (vasen etu) |
| `seat_00`–`seat_03` | tyhjät | neljä hyppääjää lattialla, selkä menosuuntaan |

## Sijainti pelissä

Pieni yleisilmailun asemataso EFPO:n länsipäässä kerhohallien välissä, (x −932, y −2303), keula rullaustien W päätä kohti. Koodi on `index.html`:n EFPO-lohkossa. Ladattu malli löytyy kohdasta `window.__jumpPlane` (`g`, `model`, `prop`, `door`, `exit`, `pilot`).

## Avoimet asiat

- Ohjaamokamera (C-näppäin, camMode 1): nykyinen sisätila on tehty ikkunoista ulkoa katsottavaksi. Lentämistä varten tarvitaan oikea ohjaamo: 3D-mittaritaulu ja liikkuvat neulat, sauva ja kaasu, sisäverhoilu sekä noin 10 cm korkeampi matkustamo.
- Lentomalli, hyppy ja `door`-animaatio.
