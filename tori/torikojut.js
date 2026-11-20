// Kauppatorin torikojut (Meshy-mallit) – lisätään peliin ILMAN muutoksia index.html:ään.
//
// Kokeilu pelissä (selaimen konsoli):   await import('./tori/torikojut.js')
// Pysyvästi index.html:n loppuun:       <script type="module" src="tori/torikojut.js"></script>
//
// Kojut ovat pieninä ryhminä eri puolilla toria, käännetty torin reunojen suuntaan (noin 11° myötäpäivään pohjoisesta, mitattu ilmakuvasta).
// Korkeus: pelin maastonosto (terrainize) nostaa mallit maanpinnalle; lisäksi kivetyksen paksuus ROAD.pave = 0,26 m.
import * as THREE from '../three.module.min.js';
import { GLTFLoader } from '../GLTFLoader.js';
import MALLIT from './torikojut_mallit.js';

const PAVE = 0.26;                       // index.html: ROAD.pave
const KESKI = { x: 62, y: 70 };          // torin avoin keskiosa (karttametrit)
const KULMA = -0.19;                     // torin akselien kierto (rad), negatiivinen = myötäpäivään
// 20.11.2026 (omistaja: "torin myyntipöytiä voisi levittää hieman eri paikkoihin"): kojut ovat pieninä ryhminä ympäri toria eivätkä yhdessä korttelissa.
// x, y = karttametrit; suunta = mihin myyntipuoli katsoo (N, S, W, E, SW ...), kierretty torin akseleille (KULMA).
const SUUNTA = { S: 0, N: Math.PI, W: -Math.PI / 2, E: Math.PI / 2, SW: -Math.PI / 4, SE: Math.PI / 4, NW: -3 * Math.PI / 4, NE: 3 * Math.PI / 4 };
const PAIKAT = [
  { x: 53.0, y: 47.0, s: 'N', m: 'hedelmat_keltainen' }, { x: 58.6, y: 45.9, s: 'N', m: 'sininen_raita' },        // eteläreuna, Yrjönkadun puoli
  { x: 80.0, y: 40.5, s: 'N', m: 'vihannekset_vihrea' },                                                            // kaakkoiskulma
  { x: 65.5, y: 60.0, s: 'W', m: 'punainen_raita' }, { x: 66.4, y: 64.6, s: 'W', m: 'oranssi_puupoyta' },          // keskellä, paviljonkia kohti
  { x: 90.0, y: 85.0, s: 'SW', m: 'hedelmat_keltainen' },                                                           // koillisosa
  { x: 74.0, y: 98.0, s: 'S', m: 'oranssi_puupoyta' }, { x: 62.0, y: 101.0, s: 'S', m: 'sininen_raita' },           // pohjoisreuna
];

export function torikojuPaikat() {
  return PAIKAT.map(p => ({ x: p.x, y: p.y, rotY: KULMA + SUUNTA[p.s], malli: p.m }));   // malli katsoo +Z:aan = kartalla etelään (S)
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
