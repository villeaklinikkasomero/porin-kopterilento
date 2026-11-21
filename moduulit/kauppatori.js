// moduulit/kauppatori.js – siirretty pääskriptistä (src/js/051_kauppatori.js) omaksi moduulikseen 21.11.2026.
// Pääskriptin muuttujat tulevat oliossa _P (getterit pitävät ne ajan tasalla); kirjastot ja data tuodaan suoraan.
// Kutsu ja _P:n sisältö: src/js/051_kauppatori.js. Uusi riippuvuus pääskriptiin → lisää se sinne _P-olioon.
import * as THREE from '../three.module.min.js';

// ---------- Kauppatori today: brick paving with grey bands (colour from Porin kaupunki photos) over the old aerial image's parked cars ----------
export default function kaynnista(_P) {
{
  const P = [[20, 44], [31, 41], [89, 27], [105, 96], [46, 110], [22, 112]];
  const inP = (x, y) => { let c = false; for (let i = 0, j = P.length - 1; i < P.length; j = i++) { const [xi, yi] = P[i], [xj, yj] = P[j]; if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) c = !c; } return c; };
  const g = _P.gridGeo(19, 26, 106, 113, 0.5, (x, y) => [x / 8, y / 8], (x, y) => !inP(x, y), 0.09); g.computeVertexNormals();
  const t = new THREE.TextureLoader().load('./tori_pave.jpg'); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
  const m = new THREE.MeshLambertMaterial({ map: t, color: 0xffffff, polygonOffset: true, polygonOffsetFactor: -4, polygonOffsetUnits: -4 });
  const me = _P.noT(new THREE.Mesh(g, m)); me.visible = false; _P.scene.add(me);   // 18.11.2026: replaced by the stone paving in roads.js
}
}
