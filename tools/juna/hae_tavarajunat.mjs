// Porin seudun tavarajunat, vaihtotyöt ja veturiajot Digitrafficista -> juna/tavara_aikataulu.js
// Ajo projektin juuresta: node tools/juna/hae_tavarajunat.mjs [päiviä=14]
// Lähde: Fintraffic / digitraffic.fi, lisenssi CC BY 4.0. Tavarajunien kokoonpanoja (veturi, vaunut) ei julkaista.
// Ajat ovat Suomen aikaa (Europe/Helsinki), aikataulun mukaisia. Ks. juna/README.md.
import { writeFileSync } from 'node:fs';

const API = 'https://rata.digitraffic.fi/api/v1';
const H = { headers: { 'Digitraffic-User': 'porin-kopterilento' } };
const ASEMAT = ['PRI', 'MN', 'TKO', 'MN_V'];           // Pori, Mäntyluoto, Tahkoluoto, Mäntyluodon erkanemisvaihde
const PAIVIA = +(process.argv[2] || 14);
const VKP = ['ma', 'ti', 'ke', 'to', 'pe', 'la', 'su'];

export async function hae(PAIVIA, get = u => fetch(u, H).then(r => r.json())) {
  const klo = s => new Date(s).toLocaleTimeString('fi-FI', { timeZone: 'Europe/Helsinki', hour: '2-digit', minute: '2-digit' }).replace('.', ':');
  const vp = d => ['su', 'ma', 'ti', 'ke', 'to', 'pe', 'la'][new Date(d + 'T12:00:00Z').getUTCDay()];
  const nyt = Date.now(), ajot = [];
  for (let k = PAIVIA; k >= 1; k--) {
    const pv = new Date(nyt - k * 864e5).toISOString().slice(0, 10);
    for (const t of await get(`${API}/trains/${pv}`)) {
      if (t.cancelled || t.trainCategory === 'Long-distance' || t.trainCategory === 'Commuter') continue;
      const rs = t.timeTableRows.filter(r => ASEMAT.includes(r.stationShortCode)); if (!rs.length) continue;
      ajot.push({ pv, n: t.trainNumber, tyyppi: t.trainType, laji: t.trainCategory, operaattori: t.operatorShortCode,
        mista: t.timeTableRows[0].stationShortCode, minne: t.timeTableRows.at(-1).stationShortCode,
        rivit: rs.map(r => ({ asema: r.stationShortCode, tapahtuma: r.type === 'ARRIVAL' ? 'saapuu' : 'lahtee', aika: klo(r.scheduledTime), raide: r.commercialTrack || null, pysahtyy: r.trainStopping })) });
    }
  }
  const g = {}; for (const a of ajot) (g[a.n] ||= []).push(a);
  const junat = [];
  for (const [n, L] of Object.entries(g)) {
    const r = L.at(-1), osuudet = {};
    try {   // raideosuuksien varausjärjestys viimeisimmästä ajosta: reitti ratapihan läpi
      const tr = await get(`${API}/train-tracking/${r.pv}/${n}`);
      for (const e of tr.filter(e => e.type === 'OCCUPY' && ['PRI', 'MN', 'TKO'].includes(e.station)).sort((a, b) => a.timestamp.localeCompare(b.timestamp))) {
        const o = (osuudet[e.station] ||= []); if (!o.includes(e.trackSection)) o.push(e.trackSection);
      }
    } catch (e) { }
    junat.push({ juna: +n, tyyppi: r.tyyppi, laji: r.laji, operaattori: r.operaattori, mista: r.mista, minne: r.minne,
      paivat: [...new Set(L.map(x => vp(x.pv)))].sort((a, b) => VKP.indexOf(a) - VKP.indexOf(b)), kertoja: L.length, rivit: r.rivit, osuudet });
  }
  junat.sort((a, b) => a.rivit[0].aika.localeCompare(b.rivit[0].aika));
  const raideosuudet = {};
  for (const x of (await get(`${API}/metadata/track-sections`)).filter(x => ['PRI', 'MN', 'TKO'].includes(x.station)))
    raideosuudet[x.trackSectionCode] = x.ranges.map(q => ({ raide: q.startLocation.track, alku: q.startLocation.kilometres + q.startLocation.metres / 1000, loppu: q.endLocation.kilometres + q.endLocation.metres / 1000 }));
  const ens = new Date(nyt - PAIVIA * 864e5).toISOString().slice(0, 10), vik = new Date(nyt - 864e5).toISOString().slice(0, 10);
  return { jakso: [ens, vik], junat, raideosuudet };
}

if (process.argv[1]?.endsWith('hae_tavarajunat.mjs')) {
  const d = await hae(PAIVIA);
  const out = new URL('../../juna/tavara_aikataulu.js', import.meta.url);
  writeFileSync(out, `// Porin seudun tavarajunat, vaihtotyöt ja veturiajot ${d.jakso[0]}–${d.jakso[1]} (tools/juna/hae_tavarajunat.mjs).
// Lähde: Fintraffic / digitraffic.fi, lisenssi CC BY 4.0. Ajat Suomen aikaa (aikataulu). Kokoonpanoja ei julkaista.
// junat[].paivat = viikonpäivät, joina juna kulki jaksolla; kertoja = ajokerrat; rivit[].raide = kaupallinen raide (Pori 2/8xx, Mäntyluoto 9xx);
// osuudet = raideosuuksien varausjärjestys (reitti ratapihan läpi); raideosuudet = osuuden ratakilometrit (raide = ratanumeron raide).
export default ${JSON.stringify(d)};
`);
  console.log('kirjoitettu juna/tavara_aikataulu.js:', d.junat.length, 'junaa,', Object.keys(d.raideosuudet).length, 'raideosuutta');
}
