// Moottorin testit ilman peliä: node tarina/testi.mjs
import { readFileSync } from 'node:fs';
import { luoMoottori, TALLENNUSAVAIN } from './moottori.js';
const D = new URL('./data/', import.meta.url);
const lue = p => JSON.parse(readFileSync(new URL(p, D), 'utf8'));
const tehtavat = lue('tehtavat/index.json').map(id => lue(`tehtavat/${id}.json`));
const paikat = lue('paikat.json'), hahmot = lue('hahmot.json'), tekstit = lue('fi.json');

let ok = 0, vika = 0;
const testi = (nimi, f) => { try { f(); ok++; console.log('  ✓', nimi); } catch (e) { vika++; console.log('  ✗', nimi, '\n    ', e.message); } };
const ass = (c, m) => { if (!c) throw new Error(m || 'ehto ei täyty'); };

function uusi(opts = {}) {
  const muisti = {}; const varasto = { get: k => muisti[k] ?? null, set: (k, v) => { muisti[k] = v; } };
  const m = luoMoottori({ tehtavat, paikat, hahmot, tekstit, varasto, ...opts });
  const log = []; m.on('*', (n, d) => log.push([n, d]));
  const W = { x: 0, y: 0, alt: 0, kulku: 'jalan', auto: null, rikki: false };
  const aja = (s = 1, dt = 0.05) => { for (let t = 0; t < s; t += dt) m.paivita(dt, { ...W }); };
  const mene = (p, kulku) => { const q = typeof p === 'string' ? paikat[p] : { x: p[0], y: p[1] }; W.x = q.x; W.y = q.y; if (kulku) { W.kulku = kulku; W.auto = kulku === 'auto' ? 'estate' : null; } };
  const loppuun = () => { for (let i = 0; i < 400 && m.kaynnissa && m.kaynnissa.tila === 'kaynnissa'; i++) { m.toiminta(); aja(0.3); } };
  return { m, W, aja, mene, log, muisti, varasto, loppuun, tapahtui: n => log.some(e => e[0] === n) };
}

// tarkista data
testi('kaikki paikat ja vaihetyypit löytyvät', () => {
  const tyypit = ['repliikit', 'cut', 'soitto', 'viesti', 'odota', 'aseta', 'kulku', 'mene', 'portit', 'keraa', 'pysy', 'seuraa', 'valinta', 'toiminto'];
  const viite = p => typeof p !== 'string' || paikat[p] || (() => { throw new Error('paikka puuttuu: ' + p); })();
  for (const t of tehtavat) {
    if (t.laukaisu && t.laukaisu.paikka) viite(t.laukaisu.paikka);
    for (const s of t.vaiheet) {
      ass(tyypit.includes(s.tyyppi), t.id + ' tuntematon tyyppi ' + s.tyyppi);
      for (const k of ['paikka', 'siirto', 'cpSiirto']) if (s[k]) viite(s[k]);
      for (const p of s.portit || []) viite(p);
      for (const k of s.kohteet || []) viite(k.paikka);
      for (const r of s.rivit || []) { const h = Array.isArray(r) ? r[0] : r.h; ass(hahmot[h], t.id + ' tuntematon hahmo ' + h); }
    }
  }
});

testi('alussa tarinasta vain M01 on saatavilla (lisäksi ruokapaikat) ja sen merkki näkyy', () => {
  const { m, aja, log } = uusi(); aja(0.2);
  ass(JSON.stringify(m.saatavilla().filter(t => !t.toistuva).map(t => t.id)) === '["M01"]', JSON.stringify(m.saatavilla()));
  ass(JSON.stringify(m.saatavilla().filter(t => t.toistuva).map(t => t.id).sort()) === '["K_GRILLI","K_RATTIS"]', 'alussa vain ruoka: ' + JSON.stringify(m.saatavilla()));
  const mk = log.filter(e => e[0] === 'merkit').pop()[1].filter(q => q.laji === 'tehtava'); ass(mk.length === 1 && mk[0].id === 'M01');
});

// M01 (21.11.2026): pyörällä Etelärannalta torille, siivet Rattikseen, korjaamolle → Ramin farmari. anna_ajoneuvo-käsittelijä on pelissä (talous/peli.js);
// testissä se puuttuu, joten moottori ohittaa sen.
const ohitaRepliikit = (m, aja, n = 8) => { for (let i = 0; i < n; i++) { m.toiminta(); aja(0.1); } };
testi('M01: kehote merkillä, cut, Tapsan fillari, tori, Rattis, korjaamo → läpi ja M02 avautuu', () => {
  const T = uusi(); const { m, aja, mene, tapahtui, log } = T;
  mene('LOC_ETELARANTA', 'auto'); aja(0.2); ass(!log.some(e => e[0] === 'kehote' && e[1]), 'autolla ei pidä tarjota (vaatii jalan)');
  mene('LOC_ETELARANTA', 'jalan'); aja(0.2); ass(log.some(e => e[0] === 'kehote' && e[1] && e[1].includes('Tervetuloa')), 'kehote puuttuu');
  ass(m.toiminta() === 'aloitettu'); ass(tapahtui('cut'));
  ohitaRepliikit(m, aja, 5); aja(1);                                   // cut + anna_ajoneuvo (ohitetaan)
  ass(m.kehittaja.vaihe().tyyppi === 'mene', 'odottaa torille: ' + m.kehittaja.vaihe().tyyppi);
  mene('LOC_TERTUN_KOJU', 'auto'); aja(0.3); ass(m.kehittaja.vaihe().tyyppi === 'mene', 'autolla ei pidä kelvata');
  mene('LOC_TERTUN_KOJU', 'pyora'); aja(0.3); ohitaRepliikit(m, aja, 4); aja(0.3);
  ass(m.tila.esineet.ITEM_SIIVET, 'siivet eivät tarttuneet');
  mene('LOC_RATTIS', 'pyora'); aja(0.3); ohitaRepliikit(m, aja, 3);
  mene('LOC_KORJAAMO', 'pyora'); aja(0.3); ohitaRepliikit(m, aja, 4); aja(1);
  ass(!m.kaynnissa, 'ei päättynyt: ' + JSON.stringify(m.kehittaja.vaihe() && m.kehittaja.vaihe().tyyppi)); ass(m.tila.liput.FLAG_M01_DONE); ass(!m.tila.esineet.ITEM_SIIVET);
  const l = log.find(e => e[0] === 'lapi'); ass(l && l[1].avautui.some(a => a.id === 'M02'), 'M02 ei avautunut');
});

testi('M01: fillari hajoaa → epäonnistuu, uudelleen jatkaa tarkistuspisteestä', () => {
  const T = uusi(); const { m, W, aja, mene, log } = T;
  m.kehittaja.aloita('M01'); ohitaRepliikit(m, aja, 5); aja(1);
  mene('LOC_TERTUN_KOJU', 'pyora'); aja(0.3); ohitaRepliikit(m, aja, 4); aja(0.3);
  ass(m.kehittaja.vaihe().tyyppi === 'mene');
  W.rikki = true; aja(0.1);
  ass(m.kaynnissa.tila === 'epaonnistui'); const f = log.find(e => e[0] === 'epaonnistui'); ass(f[1].teksti.includes('Tapsan fillari'), f[1].teksti); ass(f[1].tarkistuspiste);
  W.rikki = false; m.uudelleen(); ass(m.kehittaja.vaihe().tyyppi === 'mene', 'jatkaa väärästä vaiheesta');
  mene('LOC_RATTIS', 'pyora'); aja(0.3); ohitaRepliikit(m, aja, 3); mene('LOC_KORJAAMO', 'pyora'); aja(0.3); ohitaRepliikit(m, aja, 4); aja(1); ass(!m.kaynnissa);
});

testi('M02: kilpa – liian hidas häviää, nopea voittaa; valinta asettaa radion', () => {
  const T = uusi(); const { m, aja, mene } = T;
  m.kehittaja.valmiiksi('M01'); mene('LOC_KORJAAMO_OVI', 'jalan'); aja(0.1); m.toiminta();
  m.toiminta(); aja(0.1); mene('LOC_KORJAAMO', 'auto'); aja(0.2); mene('LOC_KESPA_LAHTO', 'auto'); aja(0.2);
  ass(m.kehittaja.vaihe().tyyppi === 'portit');
  aja(206); ass(m.kaynnissa.tila === 'epaonnistui', 'hidas ei hävinnyt');
  m.uudelleen(); const s = tehtavat.find(t => t.id === 'M02').vaiheet[3];
  for (const p of s.portit) { mene(p, 'auto'); aja(3); }
  ass(m.kehittaja.vaihe() && m.kehittaja.vaihe().tyyppi !== 'portit', 'portit eivät valmistuneet');
  for (let i = 0; i < 4 && m.kehittaja.vaihe().tyyppi !== 'valinta'; i++) { m.toiminta(); aja(0.1); }
  ass(m.valitse(1)); for (let i = 0; i < 3; i++) { m.toiminta(); aja(0.1); }
  ass(!m.kaynnissa, 'ei päättynyt'); ass(m.tila.muuttujat.VAR_RADIO_DEFAULT === 2); ass(m.tila.raha === 200);
});

testi('M02: kyydistä poistuminen kesken kilvan epäonnistuu', () => {
  const T = uusi(); const { m, aja, mene } = T;
  m.kehittaja.valmiiksi('M01'); m.kehittaja.aloita('M02'); m.toiminta(); aja(0.1); mene('LOC_KORJAAMO', 'auto'); aja(0.2); mene('LOC_KESPA_LAHTO', 'auto'); aja(0.2);
  ass(m.kehittaja.vaihe().tyyppi === 'portit'); mene('LOC_KESPA_LAHTO', 'jalan'); aja(13); ass(m.kaynnissa.tila === 'epaonnistui');
});

testi('M03 käynnistyy automaattisesti puheluna; puuttuva toiminto ohitetaan', () => {
  const T = uusi(); const { m, aja, mene, log } = T;
  m.kehittaja.valmiiksi('M01'); m.kehittaja.valmiiksi('M02'); aja(21);
  ass(m.kaynnissa && m.kaynnissa.id === 'M03', 'ei käynnistynyt'); ass(log.some(e => e[0] === 'soitto' && e[1].paalla));
  for (let i = 0; i < 4; i++) { m.toiminta(); aja(0.1); }
  mene('LOC_KIILTO', 'auto'); aja(0.2); mene('LOC_KIILTO', 'jalan'); aja(0.2);
  ass(m.kehittaja.vaihe().tyyppi === 'toiminto'); ass(log.some(e => e[0] === 'vihje' && /Tulossa/.test(e[1])));
  aja(4.5); ass(m.kehittaja.vaihe().tyyppi === 'keraa');
  mene('LOC_KIILTO_TOIMISTO'); aja(0.2); ass(m.tila.esineet.ITEM_KIILTO_AVAIMET);
});

testi('M03: kokonaan läpi', () => {
  const T = uusi(); const { m, aja, mene } = T;
  m.kehittaja.valmiiksi('M01'); m.kehittaja.valmiiksi('M02'); m.kehittaja.aloita('M03');
  const reitti = [['LOC_KIILTO', 'jalan'], ['LOC_KIILTO', 'jalan'], ['LOC_KIILTO_TOIMISTO', 'jalan'], ['LOC_KIILTO', 'auto'], ['LOC_KORJAAMO', 'auto'], ['LOC_KORJAAMO', 'jalan'], ['LOC_KIILTO', 'jalan'], ['LOC_KIILTO', 'auto'], ['LOC_KORJAAMO', 'auto']];
  for (const [p, k] of reitti) { mene(p, k); for (let i = 0; i < 12 && m.kaynnissa; i++) { m.toiminta(); aja(0.5); } }
  T.loppuun();
  ass(!m.kaynnissa, 'jäi kesken: ' + JSON.stringify(m.kehittaja.vaihe() && m.kehittaja.vaihe().tyyppi)); ass(m.tila.raha === 300);
});

testi('käsittelijä (vesiletku) voi onnistua ja epäonnistua', () => {
  let tulos = null;
  const kasittelijat = { vesiletku: { alku() {}, paivita: () => tulos } };
  const T = uusi({ kasittelijat }); const { m, aja, mene } = T;
  for (const id of ['M01', 'M02', 'M03']) m.kehittaja.valmiiksi(id);
  mene('LOC_KORJAAMO_OVI', 'jalan'); aja(0.1); m.toiminta(); for (let i = 0; i < 5; i++) { m.toiminta(); aja(0.1); }
  ass(m.kehittaja.vaihe().tyyppi === 'toiminto');
  tulos = 'epaonnistui'; aja(0.1); ass(m.kaynnissa.tila === 'epaonnistui');
  tulos = null; m.uudelleen(); aja(1); ass(m.kehittaja.vaihe().tyyppi === 'toiminto');
  tulos = 'valmis'; aja(0.1); mene('LOC_KORJAAMO_OVI'); aja(2.5); T.loppuun();
  ass(!m.kaynnissa); ass(m.tila.esineet.ITEM_VESILETKU);
});

testi('M04: korjaamolta poistuminen epäonnistuu', () => {
  const T = uusi(); const { m, aja, mene } = T;
  for (const id of ['M01', 'M02', 'M03']) m.kehittaja.valmiiksi(id);
  m.kehittaja.aloita('M04'); mene([500, 500]); aja(0.1); ass(m.kaynnissa.tila === 'epaonnistui');
});

testi('luovuta palauttaa tilan ennalleen', () => {
  const T = uusi(); const { m } = T; m.kehittaja.valmiiksi('M01'); const ennen = JSON.stringify(m.tila);
  m.kehittaja.aloita('M02'); m.kehittaja.aseta({ liput: ['ROSKA'] }); m.luovuta(); ass(JSON.stringify(m.tila) === ennen);
});

testi('tallennus ja lataus', () => {
  const T = uusi(); T.m.kehittaja.valmiiksi('M01'); T.m.kehittaja.valmiiksi('M02');
  const m2 = luoMoottori({ tehtavat, paikat, hahmot, tekstit, varasto: T.varasto });
  ass(m2.lataa()); ass(m2.tila.valmiit.length === 2); ass(m2.saatavilla().some(t => t.id === 'M03'));
  ass(JSON.parse(T.muisti[TALLENNUSAVAIN]).versio === 1);
});

testi('koko luku 1 kehittäjäohituksilla → FLAG_CH1_DONE', () => {
  const T = uusi(); const { m, aja, mene } = T; mene('LOC_KORJAAMO');
  for (const id of ['M01', 'M02', 'M03', 'M04', 'M05', 'M06']) { m.kehittaja.aloita(id); for (let i = 0; i < 80 && m.kaynnissa; i++) { m.kehittaja.ohita(); aja(0.05); } ass(!m.kaynnissa, id + ' jäi kesken'); }
  ass(m.tila.liput.FLAG_CH1_DONE); ass(JSON.stringify(m.saatavilla().filter(t => !t.toistuva).map(t => t.id)) === '["M07"]', JSON.stringify(m.saatavilla()));
});

testi('seuraa-vaihe: kohde karkaa jos jää jälkeen', () => {
  const t = { id: 'X', nimi: 'x', vaiheet: [{ tyyppi: 'seuraa', reitti: [[0, 0], [300, 0]], nopeus: 10, max: 40, armo: 2 }] };
  const m = luoMoottori({ tehtavat: [t], paikat: {}, tekstit });
  const log = []; m.on('epaonnistui', d => log.push(d));
  m.aloita('X'); for (let i = 0; i < 200; i++) m.paivita(0.05, { x: 0, y: 0, kulku: 'jalan' });
  ass(log.length === 1, 'ei epäonnistunut');
  m.uudelleen(); for (let i = 0; i < 700; i++) { const t2 = i * 0.05; m.paivita(0.05, { x: Math.min(300, t2 * 10 - 5), y: 0, kulku: 'jalan' }); }
  ass(!m.kaynnissa, 'ei päässyt perille');
});

testi('hahmot: antaja merkillä, tehtävän hahmot vaiheittain, maailman hahmot', () => {
  const sijoitukset = lue('maailma.json').aina;
  const m = luoMoottori({ tehtavat, paikat, hahmot, tekstit, sijoitukset });
  const W = { x: 0, y: 0, kulku: 'jalan' }; const aja = s => { for (let t = 0; t < s; t += 0.05) m.paivita(0.05, W); };
  aja(0.1); let l = m.hahmolista();
  ass(l.some(q => q.h === 'TERTTU'), 'Terttu puuttuu torilta'); ass(l.some(q => q.h === 'TAPSA' && q.id === 'antaja:M01'), 'Tapsa ei odota Etelärannalla');
  for (const id of ['M01', 'M02', 'M03']) m.kehittaja.valmiiksi(id);
  Object.assign(W, paikat.LOC_KORJAAMO_OVI); aja(0.1); m.toiminta(); aja(0.1);
  l = m.hahmolista(); ass(l.filter(q => q.h === 'VARTIJA').length === 3, 'vartijoita ei 3: ' + JSON.stringify(l));
  ass(l.filter(q => q.h === 'TAPSA').length === 1, 'Tapsa kahdesti');
  for (let i = 0; i < 6; i++) { m.toiminta(); aja(0.1); }   // cut läpi → vesiletku (ohitetaan 4 s) → vartijat lähtevät
  aja(5); l = m.hahmolista(); ass(l.filter(q => q.h === 'VARTIJA').length === 0, 'vartijat jäivät');
});


// ---------- 21.11.2026: koko tarina automaattipelaajalla, talous ja toistuvat tehtävät ----------
// Automaattipelaaja liikkuu jokaisen vaiheen paikkaan oikealla kulkuneuvolla, ohittaa repliikit ja valitsee annetun vaihtoehdon.
function kulkuneuvo(k) {
  if (!k) return null; if (Array.isArray(k)) return kulkuneuvo(k[0]);
  if (k === 'maa') return ['auto', 'estate']; if (k.startsWith('auto:')) return ['auto', k.slice(5)];
  return [k, k === 'auto' ? 'estate' : null];
}
function pelaaja(T, valinnat = {}) {
  const { m, W, aja } = T;
  const siirry = (p, k) => { const q = m.paikka(p); if (q) { W.x = q.x; W.y = q.y; } const kk = kulkuneuvo(k); if (kk) { W.kulku = kk[0]; W.auto = kk[1]; } };
  return function askel() {
    const v = m.kehittaja.vaihe(); if (!v) return;
    if (v.tila === 'epaonnistui') { m.uudelleen(); return; }
    const t = tehtavat.find(x => x.id === v.id), s = t.vaiheet[v.i];
    switch (s.tyyppi) {
      case 'mene': siirry(s.paikka, s.kulku); break;
      case 'kulku': siirry({ x: W.x, y: W.y }, s.kulku); break;
      case 'keraa': { const k = s.kohteet.find(k => !(v.v.saatu || {})[k.id]); if (k) siirry(k.paikka, k.kulku || s.kulku || 'jalan'); break; }
      case 'pysy': siirry(s.paikka, s.kulku); break;
      case 'portit': siirry(s.portit[v.v.n || 0], s.kulku); break;
      case 'seuraa': if (v.v.pos) { W.x = v.v.pos.x; W.y = v.v.pos.y; } break;
      case 'valinta': { const nakyvat = s.vaihtoehdot.map((o, i) => i); const i = valinnat[v.id + ':' + v.i] ?? 0; m.valitse(i) || m.valitse(nakyvat.find(j => m.valitse(j)) ?? 0); break; }
      default: m.toiminta();
    }
    aja(s.tyyppi === 'toiminto' ? 1 : 0.6);
  };
}
function pelaaTarina(valinnat) {
  const T = uusi(); const { m, W, aja, log } = T; const askel = pelaaja(T, valinnat);
  for (let kierros = 0; kierros < 60 && !m.tila.liput.FLAG_GAME_COMPLETE; kierros++) {
    if (!m.kaynnissa) {
      const t = tehtavat.filter(x => !x.toistuva).find(x => m.saatavilla().some(s => s.id === x.id));
      if (!t) { aja(25); continue; }                                   // automaattinen laukaisu odottaa
      if (t.laukaisu.tyyppi === 'merkki') { const q = m.paikka(t.laukaisu.paikka); W.x = q.x; W.y = q.y; const kk = kulkuneuvo(t.laukaisu.kulku); if (kk) { W.kulku = kk[0]; W.auto = kk[1]; } aja(0.2); let r = m.toiminta(); for (let j = 0; j < 12 && r === 'repliikki'; j++) r = m.toiminta(); ass(r === 'aloitettu', t.id + ' ei alkanut merkiltä: ' + r); }
      else { aja((t.laukaisu.viive || 0) + 1); ass(m.kaynnissa, t.id + ' ei alkanut itsestään'); }
    }
    for (let i = 0; i < 500 && m.kaynnissa; i++) askel();
    ass(!m.kaynnissa, 'jäi kesken: ' + JSON.stringify(m.kehittaja.vaihe() && { id: m.kehittaja.vaihe().id, i: m.kehittaja.vaihe().i, t: m.kehittaja.vaihe().tyyppi }));
  }
  return T;
}
for (const [loppu, valinnat] of [['A', { 'M25:1': 0 }], ['B', { 'M25:1': 1, 'M13:2': 1, 'M17:1': 1 }], ['C', { 'M25:1': 2, 'M23:1': 1 }]]) {
  testi(`koko tarina M01–M26 automaattipelaajalla → loppu ${loppu}`, () => {
    const { m, log } = pelaaTarina(valinnat);
    ass(m.tila.liput.FLAG_GAME_COMPLETE, 'peli ei päättynyt');
    const tarina = tehtavat.filter(t => !t.toistuva).map(t => t.id);
    ass(tarina.every(id => m.tila.valmiit.includes(id)), 'kesken: ' + tarina.filter(id => !m.tila.valmiit.includes(id)));
    ass(log.some(e => e[0] === 'cut' && e[1].id === 'END_' + loppu && e[1].paalla), 'loppu ' + loppu + ' ei näkynyt');
    ass(!log.some(e => e[0] === 'cut' && /^END_/.test(e[1].id || '') && e[1].id !== 'END_' + loppu && e[1].paalla), 'väärä loppu näkyi');
    ass(m.tila.muuttujat.VAR_AREAS_SAVED === 5, 'pelastetut alueet ' + m.tila.muuttujat.VAR_AREAS_SAVED);
    ass(m.tila.muuttujat.VAR_ALLIES === 3, 'liittolaiset ' + m.tila.muuttujat.VAR_ALLIES);
    ass(!m.tila.liput.FLAG_TAPSA_CAPTURED, 'Tapsa jäi vangiksi');
  });
}

testi('ruoka: raha ei riitä → valinta jää auki; rahalla energia nousee', () => {
  let nyt = 5e6; const T = uusi({ kello: () => nyt }); const { m, W, aja, mene, log } = T;
  m.kehittaja.aseta({ muuttujat: { ENERGIA: 20 } }); mene('LOC_GRILLIPORI', 'jalan'); aja(0.2);
  ass(m.toiminta() === 'aloitettu', 'grilli ei alkanut'); aja(0.1);
  ass(!m.valitse(0), 'ilman rahaa ei saa'); ass(log.some(e => e[0] === 'vihje' && /Rahat eivät riitä/.test(e[1])), 'vihje puuttuu');
  m.kehittaja.aseta({ raha: 20 }); ass(m.valitse(0), 'rahalla ei saa'); ohitaRepliikit(m, aja, 1); aja(0.3);
  ass(!m.kaynnissa, 'ei päättynyt'); ass(m.tila.raha === 12, 'raha ' + m.tila.raha); ass(m.tila.muuttujat.ENERGIA === 70, 'energia ' + m.tila.muuttujat.ENERGIA);
  ass(log.some(e => e[0] === 'raha' && e[1].muutos === -8), 'rahailmoitus puuttuu');
  ass(m.toiminta() !== 'aloitettu', 'kioski aukesi heti uudelleen (X ohitti repliikin)'); nyt += 3500; aja(0.2); ass(m.saatavilla().some(t => t.id === 'K_GRILLI'), 'kioski ei auennut uudelleen');
});

testi('nälkä: energia 0 estää keikat, mutta ruokapaikka toimii', () => {
  const esto = (t, ti) => (t.ruoka || t.laji === 'kauppa' || t.laji === 'korjaamo') ? null : ((ti.muuttujat.ENERGIA ?? 100) <= 0 ? 'SYS_HUNGRY' : null);
  const T = uusi({ esto }); const { m, aja, mene, log } = T;
  m.kehittaja.aseta({ muuttujat: { ENERGIA: 0 }, raha: 10 });
  mene('LOC_ETELARANTA', 'jalan'); aja(0.2); ass(m.toiminta() !== 'aloitettu', 'M01 alkoi nälkäisenä'); ass(log.some(e => e[0] === 'vihje' && /nälkäinen/.test(e[1])));
  mene('LOC_GRILLIPORI', 'jalan'); aja(0.2); ass(m.toiminta() === 'aloitettu', 'grilli ei auennut'); m.valitse(2); aja(0.3);
  ass(m.tila.muuttujat.ENERGIA === 15);
  mene('LOC_ETELARANTA', 'jalan'); aja(0.2); ass(m.toiminta() === 'aloitettu', 'syömisen jälkeen M01 ei alkanut');
});

testi('korjaus: merkki vain vaurioituneelle autolle, hinta vaurion mukaan', () => {
  let korjattu = 0; const kasittelijat = { korjaa_auto: { alku() { korjattu++; }, paivita: () => 'valmis' } };
  const T = uusi({ kasittelijat }); const { m, W, aja, log } = T;
  m.kehittaja.valmiiksi('M01'); m.kehittaja.aseta({ raha: 100 });
  const q = m.paikka({ paikka: 'LOC_KORJAAMO', dx: 5 }); W.x = q.x; W.y = q.y; W.kulku = 'auto'; W.auto = 'estate'; aja(0.2);
  ass(!m.saatavilla().some(t => t.id === 'K_KORJAUS'), 'ehjälle autolle tarjottiin korjausta');
  m.kehittaja.aseta({ muuttujat: { AUTON_VAURIO: 50 } }); aja(0.2);
  ass(m.toiminta() === 'aloitettu'); ohitaRepliikit(m, aja, 1);
  const val = log.filter(e => e[0] === 'valinta' && e[1]).pop()[1];
  ass(JSON.stringify(val.vaihtoehdot.filter(o => o.nakyy).map(o => o.i)) === '[1,3]', 'näkyvät: ' + JSON.stringify(val.vaihtoehdot.filter(o => o.nakyy)));
  ass(m.valitse(1)); ohitaRepliikit(m, aja, 2); aja(0.5);
  ass(!m.kaynnissa); ass(korjattu === 1); ass(m.tila.raha === 75); ass(m.tila.muuttujat.KORJAUS === 0);
});

testi('tuunaus: osto varaosaliikkeestä → nouto pakulla → asennus hallissa', () => {
  const kasittelijat = { tuunaa: { alku(p, api) { api.aseta({ muuttujat: { TUNE_MOOTTORI: 1 } }); }, paivita: () => 'valmis' } };
  const T = uusi({ kasittelijat }); const { m, W, aja, mene } = T; const askel = pelaaja(T);
  m.kehittaja.valmiiksi('M01'); m.kehittaja.valmiiksi('M02'); m.kehittaja.aseta({ raha: 300 });
  mene('LOC_VARAOSALIIKE', 'jalan'); aja(0.2); ass(m.toiminta() === 'aloitettu'); ohitaRepliikit(m, aja, 1);
  ass(m.valitse(4), 'viritystä ei voinut ostaa'); ohitaRepliikit(m, aja, 2); aja(0.3);
  ass(!m.kaynnissa && m.tila.raha === 20 && m.tila.esineet.ITEM_OSAT_NOUTAMATTA && m.tila.muuttujat.TILAUS === 5, JSON.stringify(m.tila));
  mene('LOC_VARAOSALIIKE', 'jalan'); aja(0.2); ass(!m.saatavilla().some(t => t.id === 'K_OSAT'), 'toinen tilaus ennen noutoa');
  mene('LOC_KORJAAMO_PIHA', 'jalan'); aja(0.2); ass(m.toiminta() === 'aloitettu', 'nouto ei alkanut');
  for (let i = 0; i < 100 && m.kaynnissa; i++) askel();
  ass(!m.kaynnissa && m.tila.esineet.ITEM_OSAT_HALLISSA && !m.tila.esineet.ITEM_OSAT_NOUTAMATTA, 'nouto: ' + JSON.stringify(m.tila.esineet));
  const q = m.paikka({ paikka: 'LOC_KORJAAMO', dx: -5 }); W.x = q.x; W.y = q.y; W.kulku = 'auto'; W.auto = 'hatch'; aja(0.2);
  ass(m.toiminta() !== 'aloitettu', 'asennus muuhun kuin farmariin');
  W.auto = 'estate'; aja(0.2); ass(m.toiminta() === 'aloitettu', 'asennus ei alkanut');
  for (let i = 0; i < 40 && m.kaynnissa; i++) askel();
  ass(!m.kaynnissa && m.tila.muuttujat.TUNE_MOOTTORI === 1 && !m.tila.esineet.ITEM_OSAT_HALLISSA && m.tila.muuttujat.TILAUS === 0);
  mene('LOC_VARAOSALIIKE', 'jalan'); aja(0.2); ass(m.saatavilla().some(t => t.id === 'K_OSAT'), 'uusi tilaus ei auennut');
});

testi('mikrotehtävä: palkkio, jäähtymisaika ja uusi kerta', () => {
  let nyt = 1e6; const T = uusi({ kello: () => nyt }); const { m, aja } = T; const askel = pelaaja(T);
  m.kehittaja.valmiiksi('M01');
  const t = tehtavat.find(x => x.id === 'S_KUKAT'); const q = m.paikka(t.laukaisu.paikka);
  const aloita = () => { T.W.x = q.x; T.W.y = q.y; T.W.kulku = 'jalan'; aja(0.2); return m.toiminta() === 'aloitettu'; };
  ass(aloita(), 'ei alkanut'); for (let i = 0; i < 80 && m.kaynnissa; i++) askel();
  ass(!m.kaynnissa && m.tila.raha === 12, 'raha ' + m.tila.raha); ass(m.tila.kerrat.S_KUKAT === 1);
  ass(!aloita(), 'alkoi heti uudelleen'); nyt += 241000; ass(aloita(), 'ei alkanut jäähtymisen jälkeen');
  for (let i = 0; i < 80 && m.kaynnissa; i++) askel(); ass(m.tila.raha === 24 && m.tila.kerrat.S_KUKAT === 2);
});

console.log(`\n${ok} läpi, ${vika} virhettä`); process.exit(vika ? 1 : 0);
