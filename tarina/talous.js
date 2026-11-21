// Satamakaupunki – talous: energia ja ruoka, auton korjaus ja tuunaus (RAUTALANKA 21.11.2026).
// Omistaja 21.11.2026: "autot pitää korjata tapsan hallissa, samoin kaikki tuunaukset. Tuning osia ostetaan rahalla, jota saadaan mikrotehtävistä
// ja tehtävistä. Tuning-osia pitää käydä ostamassa autovaraosaliikkeestä ja tavarat noutaa pakettiautolla. Ramin tarvitsee myös syödä, tai
// energiatasot tippuvat. Tätä varten tarvitaan rahaa, jolla hakea porilainen Grilli-Porista tai Wingsejä Rattiksesta."
//
// Kaupat, korjaus, osien nouto ja asennus ovat tavallisia toistuvia tehtäviä (data/tehtavat/K_*.json); tämä tiedosto hoitaa vain sen, mikä ei ole dataa:
//  - ENERGIA (muuttuja 0–100): laskee pelatessa, ruoka nostaa (tehtävän valinta: "muuttujat": { "ENERGIA": "+50" }). 0 → uudet keikat eivät ala (moottorin esto).
//  - AUTON_VAURIO (muuttuja 0–100) = 100 − auton kunto, päivittyy ajaessa → korjaamon merkki näkyy vain kun autossa on korjattavaa.
//  - käsittelijät 'korjaa_auto' ja 'tuunaa' sekä tuunausten vaikutus Ramin farmariin (estate).
// Ravintolat ovat pelissä keksittyjä (omistaja 21.11.2026): Grilli Kaksi Siivua (K_GRILLI) ja Ravintola Vauhtipyörä (K_VAUHTIS).
// HUD-elementti #tr-energia on tarkoituksella pelkistetty: ulkoasu suunnitellaan toisessa langassa (viestien ja HUDin konsepti).

export const ENERGIA = {
  alku: 100,
  laskuMin: 3.3,                 // energiaa / pelattu minuutti autossa tai kopterissa (100 → 0 noin 30 min)
  kerroin: { jalan: 1.5, pyora: 1.8, auto: 1, heli: 1 },   // liikkuminen omin voimin kuluttaa enemmän
  varoitus: [30, 10]
};

// tilauskoodi (muuttuja TILAUS, varaosaliikkeen valinta) → tuunaus
export const OSAT = {
  1: { muuttuja: 'TUNE_MAALI', nimi: 'maalaus (helmiäismusta)', vari: 0x1a1c22 },
  2: { muuttuja: 'TUNE_VANTEET', nimi: 'urheiluvanteet', malli: 'Rim_Sport' },
  3: { muuttuja: 'TUNE_SPOILERI', nimi: 'takaspoileri', malli: 'Spoiler_Wing' },
  4: { muuttuja: 'TUNE_PAKO', nimi: 'tuplapakoputki', malli: 'Exhaust_Twin' },
  5: { muuttuja: 'TUNE_MOOTTORI', nimi: 'moottorin viritys', kiihtyvyys: 1.25, huippu: 1.12 },
  6: { muuttuja: 'TUNE_VALOT', nimi: 'lisävalot', malli: 'Lights_Fog' }
};

export function luoTalous(M, { G, ilmoita = () => {} } = {}) {
  const m = k => M.tila.muuttujat[k];
  if (m('ENERGIA') === undefined) M.asetaMuuttuja('ENERGIA', ENERGIA.alku);
  let cutPaalla = false; M.on('cut', d => { cutPaalla = !!(d && d.paalla); });
  let edellinen = null, tallennusT = 0, viimeTyyppi = null, perus = null;

  // HUD (rautalanka)
  const el = document.createElement('div'); el.id = 'tr-energia';
  el.style.cssText = 'position:fixed;left:50%;top:8px;transform:translateX(-50%);z-index:40;font:600 12px system-ui,sans-serif;color:#fff;background:rgba(10,16,24,.7);border-radius:8px;padding:3px 8px;pointer-events:none;display:flex;gap:6px;align-items:center';
  el.innerHTML = '<span>⚡</span><span class="pal" style="width:70px;height:6px;background:rgba(255,255,255,.2);border-radius:3px;overflow:hidden"><span class="t" style="display:block;height:100%;background:#8bd17c"></span></span><span class="n"></span>';
  document.body.appendChild(el);
  const pal = el.querySelector('.t'), num = el.querySelector('.n');
  const piirra = e => { pal.style.width = e + '%'; pal.style.background = e > 30 ? '#8bd17c' : e > 10 ? '#f4c95d' : '#ff6b6b'; num.textContent = Math.round(e); };

  // moottorin esto: nälkäisenä uudet keikat eivät ala (kaupat ja korjaamo toimivat aina)
  const esto = t => (t.ruoka || t.laji === 'kauppa' || t.laji === 'korjaamo') ? null : ((m('ENERGIA') ?? 100) <= 0 ? 'SYS_HUNGRY' : null);

  const kasittelijat = {
    korjaa_auto: {
      alku() { const S = G && G.S; if (S) { S.hp = 100; S.dead = 0; } M.asetaMuuttuja('AUTON_VAURIO', 0); ilmoita('🔧 Auto korjattu', 2500); },
      paivita() { return 'valmis'; }
    },
    tuunaa: {
      alku() { const o = OSAT[m('TILAUS')]; if (!o) return; M.asetaMuuttuja(o.muuttuja, 1);
        ilmoita('🔧 Asennettu: ' + o.nimi + (o.malli ? ' (näkyy, kun osamallit valmistuvat)' : ''), 4000); },
      paivita() { return 'valmis'; }
    }
  };

  function paivita(dt, w) {
    if (!w || M.tauolla) return;
    // energia
    let e = m('ENERGIA'); if (e === undefined) e = ENERGIA.alku;
    if (e > 100) { e = 100; M.asetaMuuttuja('ENERGIA', e); }
    if (!cutPaalla && !w.sisalla) { e = Math.max(0, e - ENERGIA.laskuMin / 60 * (ENERGIA.kerroin[w.kulku] || 1) * dt); M.asetaMuuttuja('ENERGIA', e); }
    if (edellinen !== null) for (const v of ENERGIA.varoitus) if (edellinen > v && e <= v) ilmoita(M.teksti(v > 10 ? 'SYS_ENERGY_LOW' : 'SYS_ENERGY_VERY_LOW'), 5000);
    if (edellinen !== null && edellinen > 0 && e <= 0) ilmoita(M.teksti('SYS_HUNGRY'), 6000);
    edellinen = e;
    piirra(e);
    // auton vauriot korjaamon merkkiä varten
    const S = G && G.S, C = window.__car;
    if (w.kulku === 'auto' && S) M.asetaMuuttuja('AUTON_VAURIO', Math.max(0, Math.round(100 - S.hp)));
    // tuunaukset vaikuttavat Ramin farmariin (estate). Rautalanka: mikä tahansa farmari, jolla pelaaja ajaa.
    if (C && document.body.classList.contains('car')) {
      if (C.type !== viimeTyyppi) { viimeTyyppi = C.type; perus = { acc: C.acc, top: C.top }; }
      const ramin = C.type === 'estate', T = window.__take;
      if (ramin && m('TUNE_MAALI') && T && T.hex !== OSAT[1].vari) T.hex = OSAT[1].vari;
      const mo = ramin && m('TUNE_MOOTTORI') ? OSAT[5] : null;
      C.acc = mo ? (perus.acc || 4.2) * mo.kiihtyvyys : perus.acc; C.top = mo ? (perus.top || 24) * mo.huippu : perus.top;
    }
    // energia tallennetaan välillä (moottori tallentaa muuten vain tarkistuspisteissä)
    if ((tallennusT += dt) > 20) { tallennusT = 0; M.tallenna(); }
  }

  return { esto, kasittelijat, paivita };
}
