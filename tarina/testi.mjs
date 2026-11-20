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

testi('alussa vain M01 on saatavilla ja sen merkki näkyy', () => {
  const { m, aja, log } = uusi(); aja(0.2);
  ass(JSON.stringify(m.saatavilla().map(t => t.id)) === '["M01"]', JSON.stringify(m.saatavilla()));
  const mk = log.filter(e => e[0] === 'merkit').pop()[1]; ass(mk.length === 1 && mk[0].id === 'M01');
});

testi('M01: kehote merkillä, cut, auto, ajo korjaamolle → läpi ja M02 avautuu', () => {
  const T = uusi(); const { m, aja, mene, tapahtui, log } = T;
  mene('LOC_ETELARANTA', 'auto'); aja(0.2); ass(!log.some(e => e[0] === 'kehote' && e[1]), 'autolla ei pidä tarjota (vaatii jalan)');
  mene('LOC_ETELARANTA', 'jalan'); aja(0.2); ass(log.some(e => e[0] === 'kehote' && e[1] && e[1].includes('Tervetuloa')), 'kehote puuttuu');
  ass(m.toiminta() === 'aloitettu'); ass(tapahtui('cut'));
  for (let i = 0; i < 6; i++) { m.toiminta(); aja(0.1); }               // ohita repliikit
  ass(m.kehittaja.vaihe().tyyppi === 'kulku', 'odottaa autoa: ' + m.kehittaja.vaihe().tyyppi);
  mene('LOC_ETELARANTA', 'auto'); aja(0.3);
  mene('LOC_KORJAAMO', 'auto'); aja(0.5);
  ass(!m.kaynnissa, 'ei päättynyt'); ass(m.tila.liput.FLAG_M01_DONE);
  const l = log.find(e => e[0] === 'lapi'); ass(l && l[1].avautui.some(a => a.id === 'M02'), 'M02 ei avautunut');
});

testi('M01: auto hajoaa → epäonnistuu, uudelleen jatkaa tarkistuspisteestä', () => {
  const T = uusi(); const { m, W, aja, mene, log } = T;
  m.kehittaja.aloita('M01'); for (let i = 0; i < 6; i++) { m.toiminta(); aja(0.1); }
  mene('LOC_ETELARANTA', 'auto'); aja(0.5);
  ass(m.kehittaja.vaihe().tyyppi === 'mene');
  W.rikki = true; aja(0.1);
  ass(m.kaynnissa.tila === 'epaonnistui'); const f = log.find(e => e[0] === 'epaonnistui'); ass(f[1].teksti.includes('Tapsan auto'), f[1].teksti); ass(f[1].tarkistuspiste);
  W.rikki = false; m.uudelleen(); ass(m.kehittaja.vaihe().tyyppi === 'mene', 'jatkaa väärästä vaiheesta');
  mene('LOC_KORJAAMO', 'auto'); aja(0.3); ass(!m.kaynnissa);
});

testi('M02: kilpa – liian hidas häviää, nopea voittaa; valinta asettaa radion', () => {
  const T = uusi(); const { m, aja, mene } = T;
  m.kehittaja.valmiiksi('M01'); mene('LOC_KORJAAMO_OVI', 'jalan'); aja(0.1); m.toiminta();
  m.toiminta(); aja(0.1); mene('LOC_KORJAAMO', 'auto'); aja(0.2);
  ass(m.kehittaja.vaihe().tyyppi === 'portit');
  aja(151); ass(m.kaynnissa.tila === 'epaonnistui', 'hidas ei hävinnyt');
  m.uudelleen(); const s = tehtavat.find(t => t.id === 'M02').vaiheet[2];
  for (const p of s.portit) { mene(p, 'auto'); aja(3); }
  ass(m.kehittaja.vaihe() && m.kehittaja.vaihe().tyyppi !== 'portit', 'portit eivät valmistuneet');
  for (let i = 0; i < 4 && m.kehittaja.vaihe().tyyppi !== 'valinta'; i++) { m.toiminta(); aja(0.1); }
  ass(m.valitse(1)); for (let i = 0; i < 3; i++) { m.toiminta(); aja(0.1); }
  ass(!m.kaynnissa, 'ei päättynyt'); ass(m.tila.muuttujat.VAR_RADIO_DEFAULT === 2); ass(m.tila.raha === 200);
});

testi('M02: kyydistä poistuminen kesken kilvan epäonnistuu', () => {
  const T = uusi(); const { m, aja, mene } = T;
  m.kehittaja.valmiiksi('M01'); m.kehittaja.aloita('M02'); m.toiminta(); aja(0.1); mene('LOC_KORJAAMO', 'auto'); aja(0.2);
  mene('LOC_KORJAAMO', 'jalan'); aja(13); ass(m.kaynnissa.tila === 'epaonnistui');
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
  ass(m.tila.liput.FLAG_CH1_DONE); ass(m.saatavilla().length === 0);
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

console.log(`\n${ok} läpi, ${vika} virhettä`); process.exit(vika ? 1 : 0);
