// Satamakaupunki – tarinatilan HUD ja ruudut. Kuuntelee moottorin tapahtumia; ei koske pelin omaan HUDiin.
// Tyyli seuraa pelin omia kortteja (tumma läpikuultava paneeli, ohut vaalea reuna).

const CSS = `
#tarina { position: fixed; inset: 0; pointer-events: none; z-index: 40; font-family: ui-sans-serif, system-ui, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: #f4f1e8; }
#tarina .pn { position: absolute; background: rgba(10,16,24,.86); border: 1px solid rgba(255,255,255,.18); border-radius: 12px; box-shadow: 0 6px 24px rgba(0,0,0,.35); }
#tarina .piilo { display: none !important; }
#tr-tavoite { left: 50%; top: 14px; transform: translateX(-50%); padding: 8px 14px; font-size: 15px; display: flex; gap: 12px; align-items: center; max-width: min(640px, 92vw); }
#tr-tavoite .nro { font: 700 12px ui-monospace, Menlo, Consolas, monospace; color: #f4c95d; letter-spacing: .04em; }
#tr-tavoite .suunta { font: 600 13px ui-monospace, Menlo, Consolas, monospace; color: #9fd3ff; white-space: nowrap; }
#tr-tavoite .suunta i { display: inline-block; font-style: normal; transition: transform .15s; }
#tr-mittari { left: 50%; top: 58px; transform: translateX(-50%); padding: 6px 12px; font: 600 13px ui-monospace, Menlo, Consolas, monospace; display: flex; gap: 12px; align-items: center; }
#tr-mittari .palkki { width: 140px; height: 8px; background: rgba(255,255,255,.15); border-radius: 4px; overflow: hidden; }
#tr-mittari .palkki b { display: block; height: 100%; background: #f4c95d; }
#tr-tahdet { right: 14px; top: 14px; padding: 6px 10px; font-size: 18px; letter-spacing: 2px; color: #ff6b6b; }
#tr-vihje { left: 50%; top: 96px; transform: translateX(-50%); padding: 6px 12px; font-size: 14px; color: #ffe08a; transition: opacity .3s; }
#tr-kehote { left: 50%; bottom: 31%; transform: translateX(-50%); padding: 8px 16px; font-size: 15px; border-color: rgba(244,201,93,.6); }
#tr-repliikki { left: 50%; bottom: 19%; transform: translateX(-50%); width: min(600px, 88vw); padding: 12px 16px; font-size: 17px; line-height: 1.42; }
#tr-repliikki .nimi { font-weight: 700; margin-right: 6px; }
#tr-repliikki .tunne { font-size: 12px; opacity: .55; margin-left: 4px; }
#tr-repliikki.soitto { border-color: rgba(129,199,132,.7); }
#tr-repliikki.soitto .nimi::before { content: "📞 "; }
#tr-repliikki .toiminta { font-style: italic; opacity: .8; }
#tr-repliikki .jatka { position: absolute; right: 10px; bottom: 6px; font-size: 11px; opacity: .45; }
#tr-viesti { right: 14px; top: 120px; width: min(300px, 70vw); padding: 10px 12px; font-size: 14px; }
#tr-viesti .kuka { font-size: 12px; opacity: .7; margin-bottom: 4px; }
#tr-viesti .kuka::before { content: "✉ "; }
#tr-valinta { left: 50%; bottom: 19%; transform: translateX(-50%); padding: 12px; display: flex; flex-direction: column; gap: 8px; width: min(520px, 88vw); pointer-events: auto; }
#tr-valinta .kys { font-size: 13px; opacity: .7; padding: 0 4px; }
#tarina button { pointer-events: auto; font: inherit; font-size: 15px; color: #f4f1e8; background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.22); border-radius: 9px; padding: 9px 12px; text-align: left; cursor: pointer; }
#tarina button:hover { background: rgba(244,201,93,.18); border-color: rgba(244,201,93,.6); }
#tarina button kbd { font: 700 12px ui-monospace, Menlo, Consolas, monospace; color: #f4c95d; margin-right: 8px; }
#tr-ruutu { left: 50%; top: 42%; transform: translate(-50%, -50%); padding: 22px 26px; text-align: center; min-width: min(420px, 86vw); pointer-events: auto; }
#tr-ruutu h2 { margin: 0 0 6px; font-size: 26px; letter-spacing: .06em; }
#tr-ruutu.lapi h2 { color: #f4c95d; }
#tr-ruutu.fail h2 { color: #ff8a80; font-size: 20px; letter-spacing: 0; }
#tr-ruutu p { margin: 6px 0; font-size: 15px; opacity: .9; }
#tr-ruutu .napit { display: flex; gap: 10px; justify-content: center; margin-top: 14px; }
#tr-ilmo { position: absolute; right: 14px; bottom: 160px; display: flex; flex-direction: column; gap: 6px; align-items: flex-end; }
#tr-ilmo div { background: rgba(10,16,24,.86); border: 1px solid rgba(244,201,93,.45); border-radius: 10px; padding: 7px 12px; font-size: 14px; animation: trIn .25s ease-out; }
@keyframes trIn { from { opacity: 0; transform: translateX(20px); } }
#tr-lb1, #tr-lb2 { position: absolute; left: 0; right: 0; height: 0; background: #000; transition: height .5s ease; }
#tr-lb1 { top: 0; } #tr-lb2 { bottom: 0; }
#tarina.cut #tr-lb1, #tarina.cut #tr-lb2 { height: 11vh; }
#tr-valikko { left: 50%; top: 50%; transform: translate(-50%, -50%); padding: 18px 20px; width: min(480px, 90vw); max-height: 80vh; overflow: auto; pointer-events: auto; }
#tr-valikko h3 { margin: 0 0 4px; font-size: 18px; }
#tr-valikko .rivi { display: flex; justify-content: space-between; gap: 10px; padding: 6px 2px; border-bottom: 1px solid rgba(255,255,255,.08); font-size: 14px; }
#tr-valikko .rivi.valmis { opacity: .55; } #tr-valikko .rivi.lukossa { opacity: .3; }
#tr-valikko .napit { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }
#tr-kehitys { left: 14px; top: 120px; padding: 8px 10px; font: 12px/1.5 ui-monospace, Menlo, Consolas, monospace; max-width: 340px; white-space: pre; }
#tr-x { right: 22px; bottom: 300px; width: 62px; height: 62px; border-radius: 50%; text-align: center !important; font-weight: 700 !important; font-size: 20px !important; background: rgba(244,201,93,.25) !important; }
`;

const TUNNE = { neutraali: '', iloinen: 'iloinen', vihainen: 'vihainen', yllattynyt: 'yllättynyt', 'yllättynyt': 'yllättynyt', huolestunut: 'huolestunut', ovela: 'ovela' };

export function luoUI(moottori, { kosketus = false, kehitys = null } = {}) {
  const M = moottori, t = M.teksti;
  const tyyli = document.createElement('style'); tyyli.textContent = CSS; document.head.appendChild(tyyli);
  const juuri = document.createElement('div'); juuri.id = 'tarina'; document.body.appendChild(juuri);
  const el = (id, luokka = 'pn piilo') => { const d = document.createElement('div'); d.id = id; d.className = luokka; juuri.appendChild(d); return d; };
  el('tr-lb1', ''); el('tr-lb2', '');
  const E = {
    tavoite: el('tr-tavoite'), mittari: el('tr-mittari'), tahdet: el('tr-tahdet'), vihje: el('tr-vihje'), kehote: el('tr-kehote'),
    repliikki: el('tr-repliikki'), viesti: el('tr-viesti'), valinta: el('tr-valinta'), ruutu: el('tr-ruutu'), ilmo: el('tr-ilmo', ''),
    valikko: el('tr-valikko'), kehitys: el('tr-kehitys')
  };
  const nayta = (e, b) => e.classList.toggle('piilo', !b);
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  let xNappi = null;
  if (kosketus) { xNappi = document.createElement('button'); xNappi.id = 'tr-x'; xNappi.className = 'pn piilo'; xNappi.textContent = 'X'; juuri.appendChild(xNappi); xNappi.onclick = () => M.toiminta(); }
  const paivitaX = () => { if (xNappi) nayta(xNappi, !E.kehote.classList.contains('piilo') || !E.repliikki.classList.contains('piilo') || !E.ruutu.classList.contains('piilo')); };

  // tavoite + suunta
  let tavoite = null;
  M.on('tavoite', d => { tavoite = d; if (!d) return nayta(E.tavoite, false);
    E.tavoite.innerHTML = `<span class="nro">${d.numero ? 'TAVOITE ' + d.numero : 'TAVOITE'}</span><span>${esc(d.teksti)}</span><span class="suunta"></span>`; nayta(E.tavoite, true); });
  function suunta(kulma, m) {   // sovitin kutsuu: kulma kameran suunnasta (rad, myötäpäivään), m = metrit
    const s = E.tavoite.querySelector('.suunta'); if (!s) return;
    if (m == null) { s.textContent = ''; return; }
    s.innerHTML = `<i style="transform:rotate(${kulma}rad)">↑</i> ${m < 1000 ? Math.round(m) + ' m' : (m / 1000).toFixed(1) + ' km'}`;
  }

  // mittarit
  M.on('mittari', d => {
    if (!d) return nayta(E.mittari, false);
    let h = '';
    if (d.laji === 'kilpa') { const ero = d.raja - d.aika; h = `🏁 ${d.portti}/${d.portteja} · ${aika(d.aika)} · ${esc(d.nimi)} maalissa ${aika(d.raja)} <span style="color:${ero < 15 ? '#ff8a80' : '#9fd3ff'}">(${aika(Math.max(0, ero))})</span>`; }
    else if (d.laji === 'laskuri') h = `${esc(d.nimi)} ${d.n}/${d.kaikki}`;
    else if (d.laji === 'palkki') h = `${esc(d.nimi)} <span class="palkki"><b style="width:${Math.round(d.arvo * 100)}%"></b></span>`;
    else if (d.laji === 'etaisyys') { const ok = d.arvo <= d.max && d.arvo >= d.min; h = `${esc(d.nimi || 'Etäisyys')} <span style="color:${ok ? '#81c784' : '#ff8a80'}">${Math.round(d.arvo)} m</span> / ${d.max} m`; }
    else if (d.teksti) h = esc(d.teksti);
    E.mittari.innerHTML = h; nayta(E.mittari, !!h);
  });
  M.on('ajastin', d => { if (!d) { if (E.mittari.dataset.aj) { delete E.mittari.dataset.aj; nayta(E.mittari, false); } return; }
    E.mittari.dataset.aj = 1; E.mittari.innerHTML = `⏱ <span style="color:${d.jaljella < 15 ? '#ff8a80' : '#f4f1e8'}">${aika(d.jaljella)}</span>`; nayta(E.mittari, true); });
  const aika = s => { s = Math.max(0, s); return Math.floor(s / 60) + ':' + String(Math.floor(s % 60)).padStart(2, '0'); };

  // vihje ja ilmoitukset
  let vihjeT = 0;
  M.on('vihje', s => { if (E.vihje.textContent === s && !E.vihje.classList.contains('piilo')) { vihjeT = 2.5; return; } E.vihje.textContent = s; nayta(E.vihje, true); vihjeT = 3; });
  const ilmoita = (s, kesto = 4000) => { const d = document.createElement('div'); d.innerHTML = s; E.ilmo.appendChild(d); setTimeout(() => d.remove(), kesto); };
  M.on('kehote', s => { E.kehote.textContent = s || ''; nayta(E.kehote, !!s); paivitaX(); });
  M.on('tarkistuspiste', () => ilmoita('✔ ' + esc(t('SYS_CHECKPOINT')), 2500));
  M.on('poimittu', d => ilmoita('＋ ' + esc(d.nimi), 2500));
  M.on('portti', d => { if (d.n < d.kaikki) ilmoita(`${d.n}/${d.kaikki}`, 1200); });

  // dialogi
  M.on('repliikki', d => {
    if (!d) { nayta(E.repliikki, false); paivitaX(); return; }
    E.repliikki.className = 'pn' + (d.tyyli === 'soitto' ? ' soitto' : '');
    const tu = TUNNE[d.tunne] ? `<span class="tunne">(${TUNNE[d.tunne]})</span>` : '';
    E.repliikki.innerHTML = d.toiminta ? `<span class="toiminta">${esc(d.teksti)}</span>`
      : `<span class="nimi" style="color:${d.vari || '#f4c95d'}">${esc(d.nimi)}</span>${tu}<br>${esc(d.teksti)}<span class="jatka">X ›</span>`;
    paivitaX();
  });
  M.on('viesti', d => { E.viesti.innerHTML = `<div class="kuka">${esc(d.nimi)}</div>${esc(d.teksti)}`; nayta(E.viesti, true); clearTimeout(E.viesti._t); E.viesti._t = setTimeout(() => nayta(E.viesti, false), 7000); });
  M.on('cut', d => juuri.classList.toggle('cut', !!(d && d.paalla)));

  // valinta
  let valintaAuki = false;
  M.on('valinta', d => {
    valintaAuki = !!d; if (!d) return nayta(E.valinta, false);
    E.valinta.innerHTML = (d.kysymys ? `<div class="kys">${esc(d.kysymys)}</div>` : '') + d.vaihtoehdot.filter(o => o.nakyy).map((o, j) => `<button data-i="${o.i}"><kbd>${j + 1}</kbd>${esc(o.teksti)}</button>`).join('');
    E.valinta.querySelectorAll('button').forEach(b => b.onclick = () => M.valitse(+b.dataset.i));
    nayta(E.valinta, true);
  });
  const valitseNro = n => { if (!valintaAuki) return false; const b = E.valinta.querySelectorAll('button')[n]; if (b) b.click(); return !!b; };

  // ruudut
  let ruutuT = null;
  M.on('epaonnistui', d => {
    clearTimeout(ruutuT); E.ruutu.className = 'pn fail';
    E.ruutu.innerHTML = `<h2>${esc(d.teksti)}</h2><p>${esc(d.nimi)}</p><div class="napit"><button data-k="x"><kbd>X</kbd>${esc(t(d.tarkistuspiste ? 'SYS_RETRY' : 'SYS_RETRY_START').replace(/^X: /, ''))}</button><button data-k="p"><kbd>P</kbd>${esc(t('SYS_ABANDON').replace(/^P: /, ''))}</button></div>`;
    E.ruutu.querySelector('[data-k=x]').onclick = () => M.uudelleen(); E.ruutu.querySelector('[data-k=p]').onclick = () => M.luovuta();
    paivitaX();
  });
  const sulje = () => { nayta(E.ruutu, false); paivitaX(); };
  M.on('jatkuu', sulje); M.on('keskeytetty', sulje);
  M.on('lapi', d => {
    E.ruutu.className = 'pn lapi';
    E.ruutu.innerHTML = `<h2>${esc(t('SYS_MISSION_PASSED'))}</h2><p>${esc(d.nimi)}</p>` + (d.palkinto ? `<p>${d.palkinto.raha ? '+' + d.palkinto.raha + ' € · ' : ''}${esc(d.palkinto.teksti || '')}</p>` : '');
    clearTimeout(ruutuT); ruutuT = setTimeout(sulje, 4500);
    setTimeout(() => d.avautui.forEach(a => ilmoita('★ ' + esc(t('SYS_UNLOCKED', { nimi: a.nimi })), 6000)), 1200);
  });
  M.on('tehtava', d => { if (d.alkaa) { sulje(); ilmoita(`<b>${esc(d.nimi)}</b>`, 3000); } });

  // varjo-mittarin tähdet (käsittelijä 'varjo_mittari' asettaa)
  const tahdet = n => { E.tahdet.textContent = '★'.repeat(n) + '☆'.repeat(Math.max(0, 5 - n)); nayta(E.tahdet, n > 0); };

  // valikko (P)
  function valikko(auki = E.valikko.classList.contains('piilo')) {
    nayta(E.valikko, auki); M.tauko(auki); if (!auki) return;
    const k = M.kaynnissa;
    const rivit = M.tehtavat().map(x => `<div class="rivi ${x.valmis ? 'valmis' : x.saatavilla ? '' : 'lukossa'}"><span>${esc(x.id)} ${esc(x.nimi)}</span><span>${x.valmis ? '✔' : x.saatavilla ? '●' : '🔒'}</span></div>`).join('');
    E.valikko.innerHTML = `<h3>${esc(t('SYS_MENU'))} – Satamakaupunki</h3><div style="opacity:.7;font-size:13px;margin-bottom:8px">${M.tila.raha} € · ${M.tila.valmiit.length}/${M.tehtavat().length} keikkaa</div>${rivit}
      <div class="napit"><button data-k="jatka"><kbd>P</kbd>Jatka</button>${k ? `<button data-k="lopeta">Lopeta tehtävä</button>` : ''}${M.kehittaja.paalla ? `<button data-k="nollaa">Nollaa tallennus</button>` : ''}</div>`;
    E.valikko.querySelector('[data-k=jatka]').onclick = () => valikko(false);
    const lo = E.valikko.querySelector('[data-k=lopeta]'); if (lo) lo.onclick = () => { M.luovuta(); valikko(false); };
    const no = E.valikko.querySelector('[data-k=nollaa]'); if (no) no.onclick = () => { if (confirm('Nollataanko tarinan tallennus?')) { M.nollaa(); valikko(false); } };
  }

  function ruutu(dt) {   // sovitin kutsuu joka ruudulla
    if (vihjeT > 0) { vihjeT -= dt; if (vihjeT <= 0) nayta(E.vihje, false); }
  }
  function kehitysTeksti(s) { E.kehitys.textContent = s; nayta(E.kehitys, !!s); }

  return { suunta, tahdet, valikko, valitseNro, ruutu, kehitysTeksti, ilmoita, get valikkoAuki() { return !E.valikko.classList.contains('piilo'); }, get ruutuAuki() { return !E.ruutu.classList.contains('piilo') && E.ruutu.classList.contains('fail'); } };
}
