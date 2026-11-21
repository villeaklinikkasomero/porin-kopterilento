// Satamakaupunki – pelisovitin. Kytkee tehtävämoottorin Porin kopterilentoon ILMAN muutoksia index.html:ään:
// lukee pelin tilan window.__walk / window.__car / window.__game.S -olioista ja body-luokista ('car', 'walk'),
// piirtää karttamerkit __game.sceneen ja pyörittää omaa requestAnimationFrame-silmukkaa.
//
// Kokeilu pelissä (selaimen konsoli, pelin sivulla):   await import('./tarina/peli.js')
// Pysyvä kytkentä myöhemmin index.html:ään yksi rivi:    <script type="module" src="tarina/peli.js"></script>
//
// Näppäimet: X = toiminto (aloita / ohita repliikki / yritä uudelleen) · 1–3 = valinta · P = tarinavalikko
//            Ctrl+Shift+D = kehittäjätila (O = ohita vaihe, Ctrl+Shift+K = kopioi oma paikka leikepöydälle)
//            Ctrl+Shift+R = nauhoita ajettu reitti (piste 40 m välein) ja kopioi se kilpaportteiksi

import * as THREE from '../three.module.min.js';
import { luoMoottori } from './moottori.js';
import { luoUI } from './ui.js';
import { luoHahmot } from './hahmot.js';
import { luoTalous } from './talous.js';
import { luoMekaniikat } from './mekaniikat.js';      // 21.11.2026: Luvun 1 hiiviskely, vesiletku, drooni

const POHJA = new URL('./data/', import.meta.url);
const hae = async p => (await fetch(new URL(p, POHJA), { cache: 'no-cache' })).json();

// Pelin oma mekaniikka liitetään tänne nimellä (vaiheen tyyppi 'toiminto', kenttä 'nimi').
// Puuttuva käsittelijä ohitetaan muutaman sekunnin päästä, joten tarinan voi pelata läpi jo nyt.
export const KASITTELIJAT = {
  // Varjo-mittarin tähdet näkyviin (varsinainen jahtaus tulee myöhemmin: vartijabotit, uutiskopteri)
  varjo_mittari: {
    alku(p, api) { if (UI) UI.tahdet(p.tahdet || 0); tahdetLoppuu = performance.now() + (p.kesto || 40) * 1000; },
    paivita() { return 'valmis'; }
  },
  // Tarina antaa pelaajalle kulkuneuvon (21.11.2026: M01 Tapsan fillari, Ramin vanha farmari). param: { paikka, dx, dy, yaw (rad, 0 = pohjoinen),
  // tyyppi: 'bike'|'hatch'|'estate'|'van', vari: '#rrggbb', viesti }. Pelaaja istuu heti kyydissä; edellinen ajoneuvo jää paikalleen (pelin __take.give).
  anna_ajoneuvo: {
    alku(p, api) {
      const T = window.__take, q = p.paikka ? api.paikka(p.paikka) : p;
      if (!T || !T.give || !q) { console.warn('[tarina] anna_ajoneuvo: pelin __take.give puuttuu'); return; }
      const ok = T.give(q.x + (p.dx || 0), q.y + (p.dy || 0), p.yaw || 0, p.tyyppi || 'hatch', p.vari ? parseInt(String(p.vari).replace('#', ''), 16) : undefined);
      if (ok && p.viesti && window.__game && window.__game.toast) window.__game.toast(p.viesti, 2.5);
    },
    paivita() { return 'valmis'; }
  },
  // Tarina antaa helikopterin (21.11.2026: omistaja "helikopteri voidaan vapauttaa käyttöön myöhemmin"; M16 ja M20). Kopteri laskeutuu pelaajan viereen
  // (param: paikka, dx, dy, yaw) ja pelaaja istuu siinä. Lippu FLAG_HELI_AUKI pitää kopterin vapaana tästä eteenpäin (peli: window.__heliLukko).
  anna_kopteri: {
    alku(p, api) {
      api.aseta({ liput: ['FLAG_HELI_AUKI'] }); window.__heliLukko = false;
      const T = window.__take, w = maailma(); const q = p.paikka ? api.paikka(p.paikka) : w;
      if (!T || !T.giveHeli || !q) return;
      T.giveHeli(q.x + (p.dx ?? 8), q.y + (p.dy ?? 0), p.yaw || 0);
      if (window.__game && window.__game.toast) window.__game.toast('🚁 Helikopteri on nyt käytössäsi', 3);
    },
    paivita() { return 'valmis'; }
  },
  // hiiviskely, vesiletku ja drooni: tarina/mekaniikat.js (liitetään käynnistyksessä, tarvitsee pelin scenen)
};
let UI = null, tahdetLoppuu = 0, NAUHA = null, kyytiPisteet = null;
// Kyydit: pelin pisteet = suora matka m / 10, enintään +50 % nopeusbonus, kolhut vähentävät → 1 km = 100–150 pistettä.
// Omistaja 20.11.2026: kilometristä enintään 10 € → 10 € / 150 pistettä (perus 1 km ≈ 6,7 €, nopea ja ehjä ≈ 10 €).
const KYYTI_EUROA_PISTE = 10 / 150;

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
      const mat = new THREE.MeshBasicMaterial({ color: vari, transparent: true, opacity: m.laji === 'seuraava' || m.himmea ? 0.12 : 0.28, depthWrite: false, side: THREE.DoubleSide });
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
      g.userData.p.material.opacity = (g.userData.m.laji === 'seuraava' || g.userData.m.himmea ? 0.1 : 0.22) + 0.08 * Math.sin(t * 3);
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
  const [ids, paikat, hahmot, tekstit, maailmaData] = await Promise.all([hae('tehtavat/index.json'), hae('paikat.json'), hae('hahmot.json'), hae('fi.json'), hae('maailma.json').catch(() => ({ aina: [] }))]);
  const tehtavat = await Promise.all(ids.map(id => hae(`tehtavat/${id}.json`)));
  const varasto = { get: k => { try { return localStorage.getItem(k); } catch (e) { return null; } }, set: (k, v) => { try { localStorage.setItem(k, v); } catch (e) {} } };
  let TAL = null;   // talous.js (energia, korjaus, tuunaus): luodaan UI:n jälkeen, esto kysyy sitä
  const M = luoMoottori({ tehtavat, paikat, hahmot, tekstit, varasto, kasittelijat: KASITTELIJAT, sijoitukset: maailmaData.aina || [], esto: (t, ti) => TAL ? TAL.esto(t, ti) : null });
  const kosketus = document.body.classList.contains('touch') || matchMedia('(pointer: coarse)').matches;
  // päivän kierros (kiertoajelun tolpat ja HUD-kortti) piilossa tarinatilassa; valikosta saa näkyviin. Muistetaan selaimessa.
  const asetukset = { kierros: varasto.get('pori-tarina-kierros') === '1' };
  const tyyli = document.createElement('style'); tyyli.textContent = 'body.tarina-ei-kierrosta #mission { display: none !important; }'; document.head.appendChild(tyyli);
  asetukset.muuttui = () => { varasto.set('pori-tarina-kierros', asetukset.kierros ? '1' : '0'); document.body.classList.toggle('tarina-ei-kierrosta', !asetukset.kierros); if (asetukset.kierros && majakka && !G.tour().tourDone) majakka.visible = true; };
  let majakka = null;
  asetukset.muuttui();
  const etsiMajakka = () => { const r = G.scene.getObjectByName('ring2'); return r && r.parent && r.parent.getObjectByName('ring') ? r.parent : null; };
  UI = luoUI(M, { kosketus, asetukset });
  const MK = luoMerkit(G.scene);
  M.on('merkit', m => MK.aseta(m));
  M.on('siirto', d => siirra(d.paikka));
  // tarinan hahmot (npc_tapsa.js ym.) maailmaan
  // Korkeus samasta funktiosta kuin pelaajan ja kävelijöiden jalat (carGround: kadun, kiveyksen, sillan ja rantamuurin pinta). roofAt jäi
  // kadulla asfaltin alle (omistaja 21.11.2026: "tapsan jalat oli asfaltin sisällä"); sitä käytetään vain joessa (laiturit) ja varalla.
  const maa = (x, y) => { try { let z = G.carGround ? G.carGround(x, y) : null; const lz = window.__laituriZ ? window.__laituriZ(x, y) : null;
    if (z == null) z = G.roofAt ? G.roofAt(x, y) : 0; if (lz !== null && lz > z) z = lz; return z; } catch (e) { return 0; } };
  const HH = luoHahmot(G.scene, { hahmot, korkeus: maa });
  M.on('hahmot', l => HH.aseta(l));
  M.on('repliikki', d => HH.puhuu(d && d.hahmo, d && d.toiminta));
  Object.assign(KASITTELIJAT, luoMekaniikat({ THREE, G, hahmot, maa, luoHahmot }));
  M.lataa(); MK.aseta(M.merkit()); HH.aseta(M.hahmolista());
  TAL = luoTalous(M, { G, ilmoita: (t, ms) => UI.ilmoita(t, ms) }); Object.assign(KASITTELIJAT, TAL.kasittelijat);

  // radio hiljaisemmalle repliikkien ajaksi
  M.on('repliikki', d => { const R = window.__radio; if (!R) return; R.duck = d ? 0.3 : 1; if (R.mute) R.mute(); });   // radio quieter during dialogue; stays off on foot (RADIO.level)

  // näppäimet
  addEventListener('keydown', e => {
    if (e.target && /INPUT|TEXTAREA/.test(e.target.tagName)) return;
    if (e.ctrlKey && e.shiftKey && e.code === 'KeyD') { M.kehittaja.paalla = !M.kehittaja.paalla; UI.ilmoita('Kehittäjätila ' + (M.kehittaja.paalla ? 'päällä' : 'pois'), 2000); if (!M.kehittaja.paalla) UI.kehitysTeksti(''); e.preventDefault(); return; }
    if (e.ctrlKey && e.shiftKey && e.code === 'KeyK') { const w = maailma(); if (w) { const s = `[${w.x.toFixed(1)}, ${w.y.toFixed(1)}]`; console.log('[tarina] paikka', s, w); navigator.clipboard && navigator.clipboard.writeText(s).catch(() => {}); UI.ilmoita('Kopioitu ' + s, 2500); } e.preventDefault(); return; }
    if (e.ctrlKey && e.shiftKey && e.code === 'KeyR') {   // reitin nauhoitus: piste 40 m välein, lopetus kopioi JSONin
      if (!NAUHA) { NAUHA = []; UI.ilmoita('● Nauhoitetaan reittiä – aja reitti, Ctrl+Shift+R lopettaa', 4000); }
      else { const w = maailma(); if (w) NAUHA.push([+w.x.toFixed(1), +w.y.toFixed(1)]); const s = JSON.stringify(NAUHA); console.log('[tarina] reitti (' + NAUHA.length + ' pistettä):', s);
        navigator.clipboard && navigator.clipboard.writeText(s).catch(() => {}); UI.ilmoita('■ Reitti kopioitu: ' + NAUHA.length + ' pistettä', 4000); NAUHA = null; }
      e.preventDefault(); return; }
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    if ((window.__plane && window.__plane.on) || (window.__jump && window.__jump.on)) return;   // hyppykoneessa X, P ja O ovat koneen omia (potkuri, seisontajarru, päävirta)
    if (e.code === 'KeyX') { M.toiminta(); return; }
    if (e.code === 'KeyP') { if (UI.ruutuAuki) M.luovuta(); else UI.valikko(); return; }
    if (/^Digit[1-9]$/.test(e.code) && UI.valitseNro(+e.code.slice(5) - 1)) { e.stopPropagation(); return; }   // kauppojen valikoissa voi olla yli 3 vaihtoehtoa
    if (e.code === 'KeyO' && M.kehittaja.paalla) { M.kehittaja.ohita(); return; }
  }, true);

  // silmukka
  // Aloitus (omistaja 21.11.2026): uusi tarina alkaa jalan Kirjurinluodon nokasta, josta Taavi-siltaa pitkin pääsee Tapsalle Etelärannalle; jatkettu tarina
  // korjaamon pihalta. Kopteri on lukossa, kunnes tarina antaa sen (FLAG_HELI_AUKI, M16) – silloin peli alkaa kuten ennenkin.
  let aloitettu = false;
  function aloitus() {
    if (M.tila.liput.FLAG_HELI_AUKI) return;
    const uusi = !M.tila.liput.FLAG_M01_DONE, p = M.paikka(uusi ? 'LOC_ALOITUS' : 'LOC_KORJAAMO_PIHA');
    if (p && G.walkOutAt) G.walkOutAt(p.x, p.y, uusi ? 3.02 : 0);
    // korvaa päivän kierroksen ilmoituksen "Nouse ilmaan ja lennä valopylvääseen" (kopteri on vielä lukossa)
    if (G.toast) setTimeout(() => G.toast(uusi ? 'Kävele Taavi-siltaa pitkin Etelärannalle – Tapsa odottaa laiturilla' : 'Tapsan korjaamon piha', 5), 300);
  }
  M.on('nollattu', () => { aloitettu = false; });
  let edell = performance.now(), dtKehitys = 0;
  const v = new THREE.Vector3();
  function kierros(nyt) {
    const dt = Math.min(0.1, (nyt - edell) / 1000); edell = nyt;
    const w = maailma();
    if (w) M.paivita(dt, w);
    if (w && TAL) TAL.paivita(dt, w);
    window.__heliLukko = !M.tila.liput.FLAG_HELI_AUKI;
    if (!aloitettu) { const st = document.getElementById('start'); if (st && st.style.display === 'none') { aloitettu = true; aloitus(); } }
    if (NAUHA && w) { const l = NAUHA[NAUHA.length - 1]; if (!l || Math.hypot(w.x - l[0], w.y - l[1]) >= 40) NAUHA.push([+w.x.toFixed(1), +w.y.toFixed(1)]); }
    UI.ruutu(dt);
    MK.animoi(nyt / 1000);
    HH.paivita(dt, w);
    if (tahdetLoppuu && nyt > tahdetLoppuu) { tahdetLoppuu = 0; UI.tahdet(0); }
    // kiertoajelun majakka pois näkyvistä (peli asettaa sen näkyväksi aina kohteen vaihtuessa, siksi joka ruudulla)
    if (!asetukset.kierros) { if (!majakka) majakka = etsiMajakka(); if (majakka) majakka.visible = false; }
    // kyydit tuovat rahaa: pelin kyytipisteet (window.__ride.tot) → 1 piste = 0,5 €
    const R = window.__ride;
    if (R && typeof R.tot === 'number') { if (kyytiPisteet === null) kyytiPisteet = R.tot; else if (R.tot > kyytiPisteet) { M.lisaaRaha((R.tot - kyytiPisteet) * KYYTI_EUROA_PISTE, 'kyyti'); kyytiPisteet = R.tot; } }
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

  const api = { moottori: M, ui: UI, merkit: MK, hahmot: HH, kasittelijat: KASITTELIJAT, maailma };
  window.__tarina = api;
  console.log('[tarina] Satamakaupunki käynnissä:', M.tehtavat().length, 'tehtävää. P = valikko, Ctrl+Shift+D = kehittäjätila.');
  return api;
}

kaynnista().catch(e => console.error(e));
