// Satamakaupunki – pelisovitin. Kytkee tehtävämoottorin Porin kopterilentoon ILMAN muutoksia index.html:ään:
// lukee pelin tilan window.__walk / window.__car / window.__game.S -olioista ja body-luokista ('car', 'walk'),
// piirtää karttamerkit __game.sceneen ja pyörittää omaa requestAnimationFrame-silmukkaa.
//
// Kokeilu pelissä (selaimen konsoli, pelin sivulla):   await import('./tarina/peli.js')
// Pysyvä kytkentä myöhemmin index.html:ään yksi rivi:    <script type="module" src="tarina/peli.js"></script>
//
// Näppäimet: X = toiminto (aloita / ohita repliikki / yritä uudelleen) · 1–3 = valinta · P = tarinavalikko
//            Ctrl+Shift+D = kehittäjätila (O = ohita vaihe, Ctrl+Shift+K = kopioi oma paikka leikepöydälle)

import * as THREE from '../three.module.min.js';
import { luoMoottori } from './moottori.js';
import { luoUI } from './ui.js';

const POHJA = new URL('./data/', import.meta.url);
const hae = async p => (await fetch(new URL(p, POHJA), { cache: 'no-cache' })).json();

// Pelin oma mekaniikka liitetään tänne nimellä (vaiheen tyyppi 'toiminto', kenttä 'nimi').
// Puuttuva käsittelijä ohitetaan muutaman sekunnin päästä, joten tarinan voi pelata läpi jo nyt.
export const KASITTELIJAT = {
  // Varjo-mittarin tähdet näkyviin (varsinainen jahtaus tulee myöhemmin: vartijabotit, uutiskopteri)
  varjo_mittari: {
    alku(p, api) { if (UI) UI.tahdet(p.tahdet || 0); tahdetLoppuu = performance.now() + (p.kesto || 40) * 1000; },
    paivita() { return 'valmis'; }
  }
  // tulossa: hiiviskely, vesiletku, drooni (ks. tarvittavat_ominaisuudet/README.md)
};
let UI = null, tahdetLoppuu = 0;

const VARIT = { tehtava: 0xf4c95d, tavoite: 0x4fc3f7, portti: 0xffd54f, seuraava: 0xffd54f, maali: 0x81c784, kohde: 0xff8a65, seurattava: 0xff5252, alue: 0x4fc3f7 };

function maailma() {
  const G = window.__game, Wk = window.__walk, C = window.__car, S = G && G.S, b = document.body.classList;
  const rikki = !!(S && (S.dead > 0 || S.hp <= 0));
  if (Wk && Wk.on) return { x: Wk.x, y: Wk.y, alt: 0, kulku: 'jalan', auto: null, rikki: false, sisalla: !!Wk.in };
  if (C && b.contains('car')) return { x: C.x, y: C.y, alt: 0, kulku: C.type === 'bike' ? 'pyora' : 'auto', auto: C.type || null, rikki, sisalla: false };
  if (S) return { x: S.x, y: S.y, alt: S.alt || 0, kulku: 'heli', auto: null, rikki, sisalla: false };
  return null;
}

function siirra(p) {   // tarkistuspisteen siirto: vain jos pelaaja on jalan tai autossa (kopterin siirto jätetään pelille)
  if (!p) return; const Wk = window.__walk, C = window.__car;
  if (Wk && Wk.on && !Wk.in) { Wk.x = p.x; Wk.y = p.y; Wk.v = 0; return; }
  if (C && document.body.classList.contains('car')) { C.x = p.x; C.y = p.y; C.v = 0; }
}

// ---------- karttamerkit ----------
function luoMerkit(scene) {
  const ryhma = new THREE.Group(); ryhma.name = 'tarina-merkit'; ryhma.userData.noT = true; scene.add(ryhma);
  const pilari = new THREE.CylinderGeometry(1, 1, 1, 28, 1, true);
  const rengas = new THREE.RingGeometry(0.86, 1, 48).rotateX(-Math.PI / 2);
  let lista = [];
  function aseta(merkit) {
    for (const o of lista) { ryhma.remove(o); o.traverse(q => q.material && q.material.dispose()); }
    lista = merkit.map(m => {
      const g = new THREE.Group(); const vari = VARIT[m.laji] ?? 0xffffff; const r = Math.max(1.2, m.r || 4);
      const leveys = m.laji === 'alue' ? r : Math.min(r, m.laji === 'kohde' ? 1.2 : 3.2);
      const korkeus = m.laji === 'seuraava' ? 18 : m.laji === 'kohde' ? 6 : 70;
      const mat = new THREE.MeshBasicMaterial({ color: vari, transparent: true, opacity: m.laji === 'seuraava' ? 0.12 : 0.28, depthWrite: false, side: THREE.DoubleSide });
      mat.userData.noT = true;
      const p = new THREE.Mesh(pilari, mat); p.scale.set(leveys, korkeus, leveys); p.position.y = korkeus / 2 - 6; g.add(p);
      const rm = new THREE.MeshBasicMaterial({ color: vari, transparent: true, opacity: 0.55, depthWrite: false, side: THREE.DoubleSide }); rm.userData.noT = true;
      const ri = new THREE.Mesh(rengas, rm); ri.scale.setScalar(r); ri.position.y = 0.25; g.add(ri);
      g.position.set(m.x, 0, -m.y); g.userData = { m, p, ri, noT: true }; g.renderOrder = 4;
      ryhma.add(g); return g;
    });
  }
  function animoi(t, maaKorkeus) {
    for (const g of lista) {
      g.userData.p.material.opacity = (g.userData.m.laji === 'seuraava' ? 0.1 : 0.22) + 0.08 * Math.sin(t * 3);
      if (g.userData.m.laji === 'seurattava') g.position.set(g.userData.m.x, 0, -g.userData.m.y);
      if (maaKorkeus) g.userData.ri.position.y = maaKorkeus(g.userData.m.x, g.userData.m.y) + 0.25;
    }
  }
  return { aseta, animoi, get lista() { return lista.map(g => g.userData.m); } };
}

// ---------- käynnistys ----------
export async function kaynnista() {
  if (window.__tarina) return window.__tarina;
  for (let i = 0; i < 600 && !(window.__game && window.__game.scene); i++) await new Promise(r => setTimeout(r, 100));
  const G = window.__game; if (!G) throw new Error('[tarina] peliä (window.__game) ei löytynyt');
  const [ids, paikat, hahmot, tekstit] = await Promise.all([hae('tehtavat/index.json'), hae('paikat.json'), hae('hahmot.json'), hae('fi.json')]);
  const tehtavat = await Promise.all(ids.map(id => hae(`tehtavat/${id}.json`)));
  const varasto = { get: k => { try { return localStorage.getItem(k); } catch (e) { return null; } }, set: (k, v) => { try { localStorage.setItem(k, v); } catch (e) {} } };
  const M = luoMoottori({ tehtavat, paikat, hahmot, tekstit, varasto, kasittelijat: KASITTELIJAT });
  const kosketus = document.body.classList.contains('touch') || matchMedia('(pointer: coarse)').matches;
  UI = luoUI(M, { kosketus });
  const MK = luoMerkit(G.scene);
  M.on('merkit', m => MK.aseta(m));
  M.on('siirto', d => siirra(d.paikka));
  M.lataa(); MK.aseta(M.merkit());

  // radio hiljaisemmalle repliikkien ajaksi
  M.on('repliikki', d => { const R = window.__radio; if (R && R.el) R.el.volume = (R.vol ?? 0.6) * (d ? 0.3 : 1); });

  // näppäimet
  addEventListener('keydown', e => {
    if (e.target && /INPUT|TEXTAREA/.test(e.target.tagName)) return;
    if (e.ctrlKey && e.shiftKey && e.code === 'KeyD') { M.kehittaja.paalla = !M.kehittaja.paalla; UI.ilmoita('Kehittäjätila ' + (M.kehittaja.paalla ? 'päällä' : 'pois'), 2000); if (!M.kehittaja.paalla) UI.kehitysTeksti(''); e.preventDefault(); return; }
    if (e.ctrlKey && e.shiftKey && e.code === 'KeyK') { const w = maailma(); if (w) { const s = `[${w.x.toFixed(1)}, ${w.y.toFixed(1)}]`; console.log('[tarina] paikka', s, w); navigator.clipboard && navigator.clipboard.writeText(s).catch(() => {}); UI.ilmoita('Kopioitu ' + s, 2500); } e.preventDefault(); return; }
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.code === 'KeyX') { M.toiminta(); return; }
    if (e.code === 'KeyP') { if (UI.ruutuAuki) M.luovuta(); else UI.valikko(); return; }
    if (/^Digit[1-3]$/.test(e.code) && UI.valitseNro(+e.code.slice(5) - 1)) { e.stopPropagation(); return; }
    if (e.code === 'KeyO' && M.kehittaja.paalla) { M.kehittaja.ohita(); return; }
  }, true);

  // silmukka
  let edell = performance.now(), dtKehitys = 0;
  const v = new THREE.Vector3();
  function kierros(nyt) {
    const dt = Math.min(0.1, (nyt - edell) / 1000); edell = nyt;
    const w = maailma();
    if (w) M.paivita(dt, w);
    UI.ruutu(dt);
    MK.animoi(nyt / 1000);
    if (tahdetLoppuu && nyt > tahdetLoppuu) { tahdetLoppuu = 0; UI.tahdet(0); }
    // suuntanuoli lähimpään tavoitemerkkiin kameran suunnasta
    const kohteet = MK.lista.filter(m => m.laji !== 'seuraava' && m.laji !== 'tehtava');
    if (w && kohteet.length && M.kaynnissa) {
      let paras = null, pd = 1e9; for (const m of kohteet) { const d = Math.hypot(m.x - w.x, m.y - w.y); if (d < pd) { pd = d; paras = m; } }
      G.camera.getWorldDirection(v); const kyaw = Math.atan2(v.x, -v.z), tyaw = Math.atan2(paras.x - w.x, paras.y - w.y);
      UI.suunta(tyaw - kyaw, pd);
    } else UI.suunta(0, null);
    if (M.kehittaja.paalla && (dtKehitys += dt) > 0.25) {
      dtKehitys = 0; const k = M.kehittaja.vaihe();
      UI.kehitysTeksti(`KEHITTÄJÄ  (O ohita · Ctrl+Shift+K kopioi paikka)\npaikka  ${w ? w.x.toFixed(1) + ', ' + w.y.toFixed(1) : '-'}  ${w ? w.kulku + (w.auto ? ':' + w.auto : '') : ''}${w && w.sisalla ? ' (sisällä)' : ''}\n` +
        (k ? `${k.id} vaihe ${k.i} ${k.tyyppi} ${k.tila} t=${k.v.t.toFixed(1)}` : 'ei tehtävää') + `\nsaatavilla ${M.saatavilla().map(x => x.id).join(' ') || '-'}\nraha ${M.tila.raha} €  liput ${Object.keys(M.tila.liput).length}`);
    }
    requestAnimationFrame(kierros);
  }
  requestAnimationFrame(kierros);

  const api = { moottori: M, ui: UI, merkit: MK, kasittelijat: KASITTELIJAT, maailma };
  window.__tarina = api;
  console.log('[tarina] Satamakaupunki käynnissä:', M.tehtavat().length, 'tehtävää. P = valikko, Ctrl+Shift+D = kehittäjätila.');
  return api;
}

kaynnista().catch(e => console.error(e));
