// Kauppatorin torikojut (Meshy-mallit) – lisätään peliin ILMAN muutoksia index.html:ään.
//
// Kokeilu pelissä (selaimen konsoli):   await import('./tori/torikojut.js')
// Pysyvästi index.html:n loppuun:       <script type="module" src="tori/torikojut.js"></script>
//
// Kojut ovat kahdessa rivissä torin avoimella kivetyksellä (entisen helikopterikentän kohdalla) toisiaan kohti, 7 m käytävä välissä.
// Rivit on käännetty torin reunojen suuntaan (noin 11° myötäpäivään pohjoisesta, mitattu ilmakuvasta).
// Korkeus: pelin maastonosto (terrainize) nostaa mallit maanpinnalle; lisäksi kivetyksen paksuus ROAD.pave = 0,26 m.
import * as THREE from '../three.module.min.js';
import { GLTFLoader } from '../GLTFLoader.js';
import MALLIT from './torikojut_mallit.js';

const PAVE = 0.26;                       // index.html: ROAD.pave
const KESKI = { x: 62, y: 70 };          // torin avoin keskiosa (karttametrit)
const KULMA = -0.19;                     // torin akselien kierto (rad), negatiivinen = myötäpäivään
const RIVI = 4.5;                        // rivin etäisyys käytävän keskeltä (m)
const PAIKAT = [                         // u = torin suuntaan, v = rivi (+ = pohjoinen rivi, katsoo etelään)
  { u: -7.5, v: +1, m: 'hedelmat_keltainen' }, { u: -3.3, v: +1, m: 'sininen_raita' }, { u: 0.9, v: +1, m: 'punainen_raita' }, { u: 5.1, v: +1, m: 'oranssi_puupoyta' },
  { u: -7.5, v: -1, m: 'vihannekset_vihrea' }, { u: -3.3, v: -1, m: 'oranssi_puupoyta' }, { u: 0.9, v: -1, m: 'hedelmat_keltainen' }, { u: 5.1, v: -1, m: 'sininen_raita' },
];

export function torikojuPaikat() {
  const ca = Math.cos(KULMA), sa = Math.sin(KULMA);
  const U = [ca, sa], V = [-sa, ca];      // karttakoordinaateissa (x itään, y pohjoiseen)
  return PAIKAT.map(p => {
    const x = KESKI.x + U[0] * p.u + V[0] * p.v * RIVI, y = KESKI.y + U[1] * p.u + V[1] * p.v * RIVI;
    // malli katsoo +Z:aan = kartalla etelään (y-); pohjoinen rivi katsoo etelään, eteläinen pohjoiseen
    const rotY = KULMA + (p.v < 0 ? Math.PI : 0);
    return { x, y, rotY, malli: p.m };
  });
}

function lataa(b64) {
  const bin = atob(b64), buf = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
  return new Promise((ok, ei) => new GLTFLoader().parse(buf.buffer, '', ok, ei));
}

export async function lisaaKojut({ scene, korkeus = () => PAVE, valta = null }) {
  const ryhma = new THREE.Group(); ryhma.name = 'Torikojut';
  const mallit = {};
  for (const [nimi, b64] of Object.entries(MALLIT)) mallit[nimi] = (await lataa(b64)).scene;
  const lisatty = [];
  for (const p of torikojuPaikat()) {
    if (valta && Math.hypot(p.x - valta.x, p.y - valta.y) < valta.r) continue;   // esim. helikopterikenttä, jos se on yhä torilla
    const o = mallit[p.malli].clone(true);
    o.position.set(p.x, korkeus(p.x, p.y), -p.y);
    o.rotation.y = p.rotY;
    o.traverse(q => { if (q.isMesh) { q.castShadow = q.receiveShadow = false; } });
    ryhma.add(o); lisatty.push(p);
  }
  scene.add(ryhma);
  window.__torikojut = { ryhma, paikat: lisatty };
  console.log(`[tori] ${lisatty.length} torikojua lisätty Kauppatorille`);
  return ryhma;
}

// automaattinen käynnistys pelissä
if (typeof window !== 'undefined' && !window.__toriKokeilu) {
  const odota = () => {
    const G = window.__game;
    if (G && G.scene && G.S) {
      // jos helikopteri seisoo vielä torilla (vanha lähtöpaikka), sen ympäriltä jätetään 12 m tyhjää
      const valta = Math.hypot(G.S.x - KESKI.x, G.S.y - KESKI.y) < 60 ? { x: G.S.x, y: G.S.y, r: 12 } : null;
      lisaaKojut({ scene: G.scene, valta });
      return;
    }
    setTimeout(odota, 500);
  };
  odota();
}
