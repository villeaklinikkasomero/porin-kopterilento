// Satamakaupunki – tehtävämoottori (ydin). Ei riipu pelistä, DOMista eikä three.js:stä: pelisovitin (peli.js) antaa
// joka ruudulla maailman tilan `paivita(dt, maailma)`-kutsulla ja piirtää moottorin lähettämät tapahtumat.
// Testit: `node tarina/testi.mjs`. Tiedostomuoto: tarina/README.md.
//
// maailma = { x, y, alt, kulku: 'jalan'|'heli'|'auto'|'pyora', auto: 'hatch'|'van'|'estate'|'bike'|..., rikki: bool, sisalla: bool }
// koordinaatit = pelin karttametrit (x itään, y pohjoiseen), samat kuin window.__walk / window.__car / __game.S

export const VERSIO = 1;
export const TALLENNUSAVAIN = 'pori-tarina-v1';

const kloonaa = o => JSON.parse(JSON.stringify(o));
const etaisyys = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);

export function luoMoottori({ tehtavat = [], paikat = {}, hahmot = {}, tekstit = {}, varasto = null, kasittelijat = {} } = {}) {
  const T = {}; for (const t of tehtavat) T[t.id] = t;
  const KUUNTELIJAT = {};
  const on = (nimi, f) => { (KUUNTELIJAT[nimi] = KUUNTELIJAT[nimi] || []).push(f); return () => { KUUNTELIJAT[nimi] = KUUNTELIJAT[nimi].filter(g => g !== f); }; };
  const emit = (nimi, d) => { for (const f of KUUNTELIJAT[nimi] || []) f(d); for (const f of KUUNTELIJAT['*'] || []) f(nimi, d); };
  const teksti = (avain, korvaa = {}) => { let s = tekstit[avain] ?? avain; for (const k in korvaa) s = s.split('{' + k + '}').join(korvaa[k]); return s; };

  const uusiTila = () => ({ liput: {}, muuttujat: {}, esineet: {}, raha: 0, valmiit: [] });
  let tila = uusiTila();
  let K = null;          // käynnissä oleva tehtävä: { t, i, v, cp: { i, tila }, alku, aika, tila: 'kaynnissa'|'epaonnistui' }
  let D = null;          // dialogi: { rivit, i, t, kesto, tyyli, kun }
  let tauolla = false, kehitys = false, viimeMerkit = '', viimeKehote = '', aikaKaikki = 0, autoOdotus = {};
  let W = { x: 0, y: 0, alt: 0, kulku: 'jalan', auto: null, rikki: false };

  // ---------- tila ----------
  const lippu = n => !!tila.liput[n];
  const muuttuja = n => tila.muuttujat[n] || 0;
  function aseta(spec) {
    if (!spec) return;
    for (const l of spec.liput || []) tila.liput[l] = true;
    for (const l of spec.poista || []) delete tila.liput[l];
    for (const k in spec.muuttujat || {}) {
      const a = spec.muuttujat[k];
      tila.muuttujat[k] = typeof a === 'string' && /^[+-]/.test(a) ? muuttuja(k) + parseFloat(a) : a;
    }
    for (const e of spec.esineet || []) tila.esineet[e] = true;
    for (const e of spec.poistaEsineet || []) delete tila.esineet[e];
    if (spec.raha) tila.raha += spec.raha;
  }
  // ehto: { lippu, eiLippua, esine, muuttuja, vah, enint, yhtakuin, kaikki: [...], jokin: [...] }
  function tayttyy(e) {
    if (!e) return true;
    if (Array.isArray(e)) return e.every(tayttyy);
    if (e.kaikki) return e.kaikki.every(tayttyy);
    if (e.jokin) return e.jokin.some(tayttyy);
    if (e.lippu && !lippu(e.lippu)) return false;
    if (e.eiLippua && lippu(e.eiLippua)) return false;
    if (e.esine && !tila.esineet[e.esine]) return false;
    if (e.muuttuja) {
      const m = muuttuja(e.muuttuja);
      if (e.vah !== undefined && m < e.vah) return false;
      if (e.enint !== undefined && m > e.enint) return false;
      if (e.yhtakuin !== undefined && m !== e.yhtakuin) return false;
    }
    return true;
  }
  const saatavilla = t => !tila.valmiit.includes(t.id) && (t.vaatii || []).every(lippu) && tayttyy(t.ehto);

  // ---------- paikat ja kulkuneuvot ----------
  function paikka(p) {
    if (!p) return null;
    if (Array.isArray(p)) return { x: p[0], y: p[1] };
    if (typeof p === 'string') { const q = paikat[p]; if (!q) { console.warn('[tarina] tuntematon paikka', p); return null; } return q; }
    if (p.paikka) { const q = paikka(p.paikka); return q && { x: q.x + (p.dx || 0), y: q.y + (p.dy || 0) }; }
    return p;
  }
  // vaatimus: 'jalan' | 'heli' | 'auto' | 'pyora' | 'maa' (ei kopteri) | 'auto:van' | [vaihtoehtoja]
  function sopii(vaatimus, w = W) {
    if (!vaatimus) return true;
    if (Array.isArray(vaatimus)) return vaatimus.some(v => sopii(v, w));
    if (vaatimus === 'maa') return w.kulku !== 'heli';
    if (vaatimus.startsWith('auto:')) return w.kulku === 'auto' && w.auto === vaatimus.slice(5);
    return w.kulku === vaatimus;
  }
  const kulkuNimi = v => Array.isArray(v) ? v.map(kulkuNimi).join(' / ') : teksti('KULKU_' + String(v).replace(':', '_').toUpperCase());

  // ---------- dialogi ----------
  function puhu(rivit, tyyli = 'puhe', kun = null) {
    const r = (rivit || []).map(x => Array.isArray(x) ? { h: x[0], tu: x[1] || 'neutraali', te: x[2] } : x);
    D = { rivit: r, i: -1, t: 0, kesto: 0, tyyli, kun };
    seuraavaRivi();
  }
  function seuraavaRivi() {
    if (!D) return;
    D.i++; D.t = 0;
    if (D.i >= D.rivit.length) { const kun = D.kun; D = null; emit('repliikki', null); if (kun) kun(); return; }
    const r = D.rivit[D.i];
    D.kesto = r.kesto || Math.max(2.2, 1.4 + 0.06 * (r.te || '').length);
    const h = hahmot[r.h] || {};
    emit('repliikki', { hahmo: r.h, nimi: h.nimi || r.h, vari: h.vari, tunne: r.tu, teksti: r.te, tyyli: D.tyyli, toiminta: !!r.toiminta, i: D.i, n: D.rivit.length });
  }

  // ---------- tehtävän kulku ----------
  function aloita(id, { pakota = false } = {}) {
    const t = T[id];
    if (!t) throw new Error('tuntematon tehtävä ' + id);
    if (K) return false;
    if (!pakota && !saatavilla(t)) return false;
    K = { t, i: -1, v: null, alku: kloonaa(tila), cp: { i: 0, tila: kloonaa(tila) }, aika: 0, tila: 'kaynnissa' };
    emit('tehtava', { id: t.id, nimi: t.nimi, luku: t.luku, alkaa: true });
    seuraavaVaihe();
    return true;
  }

  function seuraavaVaihe() {
    if (!K) return;
    K.i++;
    const vaiheet = K.t.vaiheet || [];
    while (K.i < vaiheet.length && !tayttyy(vaiheet[K.i].ehto)) K.i++;
    if (K.i >= vaiheet.length) return lapi();
    aloitaVaihe();
  }

  function aloitaVaihe() {
    const s = K.t.vaiheet[K.i];
    K.v = { t: 0, n: 0, tehty: false };
    if (s.cp) { K.cp = { i: K.i, tila: kloonaa(tila) }; tallenna(); emit('tarkistuspiste', { i: K.i }); }
    if (s.siirto) emit('siirto', { paikka: paikka(s.siirto), kulku: s.siirtoKulku || null });
    if (s.teksti) emit('tavoite', { teksti: s.teksti, numero: tavoiteNumero() });
    else if (!['repliikit', 'cut', 'soitto', 'viesti', 'aseta', 'odota'].includes(s.tyyppi)) emit('tavoite', null);
    const kasittely = VAIHEET[s.tyyppi];
    if (!kasittely) { console.warn('[tarina] tuntematon vaihetyyppi', s.tyyppi); K.v.tehty = true; return; }
    if (kasittely.alku) kasittely.alku(s, K.v);
    paivitaMerkit(true);
  }
  function tavoiteNumero() { let n = 0; for (let i = 0; i <= K.i; i++) if (K.t.vaiheet[i].teksti) n++; return n; }
  const valmis = () => { if (K && K.v) K.v.tehty = true; };

  function epaonnistu(syy) {
    if (!K || K.tila !== 'kaynnissa') return;
    K.tila = 'epaonnistui'; D = null; emit('repliikki', null); emit('cut', { paalla: false });
    emit('tavoite', null); emit('ajastin', null); emit('mittari', null);
    emit('epaonnistui', { id: K.t.id, nimi: K.t.nimi, teksti: teksti(syy || 'SYS_FAIL_CAUGHT'), tarkistuspiste: K.cp.i > 0 });
    paivitaMerkit(true);
  }
  function uudelleen() {
    if (!K || K.tila !== 'epaonnistui') return false;
    tila = kloonaa(K.cp.tila); K.tila = 'kaynnissa'; K.i = K.cp.i;
    const s = K.t.vaiheet[K.i]; const cpSiirto = s.cpSiirto || s.siirto;
    if (cpSiirto) emit('siirto', { paikka: paikka(cpSiirto), kulku: s.siirtoKulku || null });
    emit('jatkuu', { id: K.t.id, i: K.i });
    aloitaVaihe();
    return true;
  }
  function luovuta() {
    if (!K) return false;
    tila = kloonaa(K.alku); const id = K.t.id; K = null; D = null;
    emit('repliikki', null); emit('cut', { paalla: false }); emit('tavoite', null); emit('ajastin', null); emit('mittari', null);
    emit('keskeytetty', { id }); paivitaMerkit(true); return true;
  }
  function lapi() {
    const t = K.t; const ennen = new Set(Object.values(T).filter(saatavilla).map(x => x.id));
    aseta(t.asettaa); if (t.palkinto && t.palkinto.raha) tila.raha += t.palkinto.raha;
    if (!tila.valmiit.includes(t.id)) tila.valmiit.push(t.id);
    K = null; emit('tavoite', null); emit('ajastin', null); emit('mittari', null);
    tallenna();
    const avautui = Object.values(T).filter(x => saatavilla(x) && !ennen.has(x.id)).map(x => ({ id: x.id, nimi: x.nimi }));
    emit('lapi', { id: t.id, nimi: t.nimi, palkinto: t.palkinto || null, avautui });
    paivitaMerkit(true);
  }

  // ---------- vaihetyypit ----------
  // alku(s, v): kun vaihe alkaa. paivita(s, v, dt): kutsutaan joka ruudulla; kutsu valmis() kun vaihe on tehty, epaonnistu(syy) kun ei.
  // merkit(s, v): vaiheen karttamerkit.
  const VAIHEET = {
    repliikit: {
      alku(s, v) { const estaa = s.estaa !== false; puhu(s.rivit, s.tyyli || 'puhe', estaa ? valmis : null); if (!estaa) valmis(); }
    },
    cut: {
      alku(s, v) { emit('cut', { paalla: true, id: s.id, kamera: s.kamera || null }); puhu(s.rivit, 'cut', () => { emit('cut', { paalla: false, id: s.id }); valmis(); }); }
    },
    soitto: {
      alku(s, v) { emit('soitto', { soittaja: s.soittaja, nimi: (hahmot[s.soittaja] || {}).nimi || s.soittaja, paalla: true }); puhu(s.rivit, 'soitto', () => { emit('soitto', { paalla: false }); valmis(); }); }
    },
    viesti: {
      alku(s, v) { emit('viesti', { lahettaja: s.lahettaja, nimi: (hahmot[s.lahettaja] || {}).nimi || s.lahettaja || teksti('TUNTEMATON'), teksti: s.viesti }); },
      paivita(s, v) { if (v.t > (s.kesto ?? 3)) valmis(); }
    },
    odota: { paivita(s, v) { if (v.t >= (s.s || 1)) valmis(); } },
    aseta: { alku(s) { aseta(s.asettaa); valmis(); } },
    kulku: {
      paivita(s, v) { if (sopii(s.kulku)) valmis(); }
    },
    mene: {
      paivita(s, v) {
        const p = paikka(s.paikka); if (!p) return valmis();
        const d = etaisyys(W, p), lahella = d <= (s.r || 6);
        if (lahella && !sopii(s.kulku)) { vihje(teksti('SYS_NEED_VEHICLE', { kulku: kulkuNimi(s.kulku) })); return; }
        if (lahella && (s.korkeintaan === undefined || W.alt <= s.korkeintaan)) valmis();
      },
      merkit(s) { const p = paikka(s.paikka); return p ? [{ ...p, r: s.r || 6, laji: 'tavoite', nimi: s.merkki || '' }] : []; }
    },
    portit: {
      alku(s, v) { v.n = 0; if (s.kilpailija) emit('mittari', { laji: 'kilpa', nimi: (hahmot[s.kilpailija.hahmo] || {}).nimi || s.kilpailija.hahmo, aika: 0, raja: s.kilpailija.aika, portti: 0, portteja: s.portit.length }); },
      paivita(s, v) {
        if (!sopii(s.kulku)) { vihje(teksti('SYS_NEED_VEHICLE', { kulku: kulkuNimi(s.kulku) })); }
        else { const p = paikka(s.portit[v.n]); if (p && etaisyys(W, p) <= (s.r || 9)) { v.n++; emit('portti', { n: v.n, kaikki: s.portit.length }); } }
        if (s.kilpailija) {
          emit('mittari', { laji: 'kilpa', nimi: (hahmot[s.kilpailija.hahmo] || {}).nimi || s.kilpailija.hahmo, aika: v.t, raja: s.kilpailija.aika, portti: v.n, portteja: s.portit.length });
          if (v.t > s.kilpailija.aika) return epaonnistu(s.kilpailija.voitti || 'SYS_FAIL_RIVAL');
        }
        if (v.n >= s.portit.length) { emit('mittari', null); valmis(); }
      },
      merkit(s, v) { const r = [], viim = s.portit.length - 1; const a = paikka(s.portit[v.n]), b = paikka(s.portit[v.n + 1]);
        if (a) r.push({ ...a, r: s.r || 9, laji: v.n === viim ? 'maali' : 'portti' });
        if (b) r.push({ ...b, r: s.r || 9, laji: v.n + 1 === viim ? 'maali' : 'seuraava' });
        if (v.n + 1 < viim) { const m = paikka(s.portit[viim]); if (m) r.push({ ...m, r: s.r || 9, laji: 'maali', himmea: true }); }   // maali näkyy aina
        return r; }
    },
    keraa: {
      alku(s, v) { v.saatu = {}; v.n = 0; },
      paivita(s, v) {
        for (const k of s.kohteet) {
          if (v.saatu[k.id]) continue;
          const p = paikka(k.paikka);
          if (p && etaisyys(W, p) <= (k.r || 2.5) && sopii(k.kulku || s.kulku || 'jalan')) {
            v.saatu[k.id] = true; v.n++; if (k.esine) tila.esineet[k.esine] = true;
            emit('poimittu', { id: k.id, nimi: k.nimi || k.id, n: v.n, kaikki: s.kohteet.length });
          }
        }
        if (s.kohteet.length > 1) emit('mittari', { laji: 'laskuri', nimi: s.laskuri || '', n: v.n, kaikki: s.kohteet.length });
        if (v.n >= (s.tarvitaan || s.kohteet.length)) { emit('mittari', null); valmis(); }
      },
      merkit(s, v) { return s.kohteet.filter(k => !v.saatu[k.id]).map(k => ({ ...paikka(k.paikka), r: k.r || 2.5, laji: 'kohde', nimi: k.nimi || '' })); }
    },
    pysy: {
      paivita(s, v) {
        const p = paikka(s.paikka); const sisalla = etaisyys(W, p) <= (s.r || 10) && sopii(s.kulku);
        if (sisalla) v.n += v.dt; else if (s.tiukka && v.n > 0) return epaonnistu(s.poistuiTeksti || 'SYS_FAIL_LEFT');
        emit('mittari', { laji: 'palkki', nimi: s.mittari || '', arvo: Math.min(1, v.n / (s.s || 5)) });
        if (v.n >= (s.s || 5)) { emit('mittari', null); valmis(); }
      },
      merkit(s) { const p = paikka(s.paikka); return [{ ...p, r: s.r || 10, laji: 'alue' }]; }
    },
    seuraa: {
      // liikkuva kohde kulkee reittiä pitkin (pelaaja ei näe hahmoa ennen kuin sovitin piirtää sen merkkinä); pysy välillä min..max
      alku(s, v) { v.pts = s.reitti.map(paikka); v.seg = 0; v.pos = { ...v.pts[0] }; v.kaukana = 0; },
      paivita(s, v) {
        let liiku = (s.nopeus || 6) * v.dt;
        if (s.odottaa && etaisyys(W, v.pos) > (s.max || 60)) liiku = 0;   // kilpakumppani voi odottaa
        while (liiku > 0 && v.seg < v.pts.length - 1) {
          const a = v.pos, b = v.pts[v.seg + 1], d = etaisyys(a, b);
          if (d <= liiku) { v.pos = { ...b }; v.seg++; liiku -= d; } else { v.pos = { x: a.x + (b.x - a.x) * liiku / d, y: a.y + (b.y - a.y) * liiku / d }; liiku = 0; }
        }
        const d = etaisyys(W, v.pos);
        emit('mittari', { laji: 'etaisyys', nimi: s.mittari || '', arvo: d, min: s.min || 0, max: s.max || 60 });
        if (!s.odottaa && (d > (s.max || 60) || d < (s.min || 0))) { v.kaukana += v.dt; if (v.kaukana > (s.armo ?? 5)) return epaonnistu(s.karkasi || 'SYS_FAIL_LOST'); } else v.kaukana = 0;
        if (v.seg >= v.pts.length - 1) { emit('mittari', null); valmis(); }
      },
      merkit(s, v) { return v.pos ? [{ ...v.pos, r: 2, laji: 'seurattava', nimi: s.kohde || '' }] : []; }
    },
    valinta: {
      alku(s, v) { v.odottaa = true; emit('valinta', { kysymys: s.kysymys || '', vaihtoehdot: s.vaihtoehdot.map((o, i) => ({ i, teksti: o.teksti, nakyy: tayttyy(o.ehto) })) }); }
    },
    toiminto: {
      // pelin oma mekaniikka (drooni, vesiletku, hiiviskely...). Käsittelijä: { alku(param, api), paivita(dt, maailma, param, api) -> 'valmis'|'epaonnistui'|null, loppu() }
      alku(s, v) {
        const k = kasittelijat[s.nimi];
        v.k = k || null;
        if (k && k.alku) k.alku(s.param || {}, api(v));
        if (!k) { v.puuttuu = true; vihje(teksti('SYS_NOT_IMPLEMENTED', { nimi: s.nimi })); }
      },
      paivita(s, v) {
        if (v.puuttuu) { if (v.t > (s.puuttuuOhita ?? 4)) valmis(); return; }
        const r = v.k.paivita ? v.k.paivita(v.dt, W, s.param || {}, api(v)) : null;
        if (r === 'valmis') { if (v.k.loppu) v.k.loppu(); valmis(); } else if (r && r.epaonnistui) { if (v.k.loppu) v.k.loppu(); epaonnistu(r.epaonnistui); } else if (r === 'epaonnistui') { if (v.k.loppu) v.k.loppu(); epaonnistu(s.failTeksti); }
      },
      merkit(s, v) { return v.k && v.k.merkit ? v.k.merkit(s.param || {}) : (s.paikka ? [{ ...paikka(s.paikka), r: s.r || 6, laji: 'tavoite' }] : []); }
    }
  };
  const api = v => ({ emit, teksti, paikka, tila: () => tila, aseta, vihje, mittari: d => emit('mittari', d) });
  function vihje(s) { emit('vihje', s); }

  // ---------- epäonnistumisehdot ----------
  // tehtävän `fail` ja vaiheen `fail`: { ehto: 'kulkuneuvo_rikki' | 'poistui' (paikka, r) | 'nousi_kyydista' (kulku, viive) | 'kopteri' , teksti }
  function tarkistaFail(dt) {
    const s = K.t.vaiheet[K.i];
    const lista = (K.t.fail || []).concat(s.fail || []);
    for (const f of lista) {
      if (f.alkaen !== undefined && K.i < f.alkaen) continue;
      if (f.ehto === 'kulkuneuvo_rikki' && W.rikki) return epaonnistu(f.teksti || 'SYS_FAIL_VEHICLE');
      if (f.ehto === 'poistui') { const p = paikka(f.paikka); if (p && etaisyys(W, p) > f.r) return epaonnistu(f.teksti || 'SYS_FAIL_LEFT'); }
      if (f.ehto === 'nousi_kyydista') { K.v.ulkona = sopii(f.kulku) ? 0 : (K.v.ulkona || 0) + dt; if (K.v.ulkona > (f.viive ?? 10)) return epaonnistu(f.teksti || 'SYS_FAIL_ABANDONED'); }
    }
    if (s.aikaraja) {
      const j = s.aikaraja - K.v.t; emit('ajastin', { jaljella: Math.max(0, j) });
      if (j <= 0) { emit('ajastin', null); return epaonnistu(s.aikarajaTeksti || 'SYS_FAIL_TIME'); }
    }
  }

  // ---------- merkit ja kehotteet ----------
  function merkit() {
    if (K && K.tila === 'kaynnissa') { const s = K.t.vaiheet[K.i]; const k = VAIHEET[s.tyyppi]; return k && k.merkit ? k.merkit(s, K.v).filter(m => m && m.x !== undefined) : []; }
    if (K) return [];
    return Object.values(T).filter(t => saatavilla(t) && t.laukaisu && t.laukaisu.tyyppi === 'merkki')
      .map(t => ({ ...paikka(t.laukaisu.paikka), r: t.laukaisu.r || 4, laji: 'tehtava', id: t.id, nimi: t.nimi, kirjain: t.merkki || (hahmot[t.antaja] || {}).kirjain || '' }));
  }
  function paivitaMerkit(pakota) {
    const m = merkit(); const k = JSON.stringify(m.map(q => [q.laji, Math.round(q.x * 2), Math.round(q.y * 2), q.id || '']));
    if (pakota || k !== viimeMerkit) { viimeMerkit = k; emit('merkit', m); }
  }
  function lahinTehtava() {
    if (K) return null;
    for (const t of Object.values(T)) {
      if (!saatavilla(t) || !t.laukaisu || t.laukaisu.tyyppi !== 'merkki') continue;
      const p = paikka(t.laukaisu.paikka);
      if (p && etaisyys(W, p) <= (t.laukaisu.r || 4) && sopii(t.laukaisu.kulku)) return t;
    }
    return null;
  }

  // ---------- päivitys ----------
  function paivita(dt, maailma) {
    if (maailma) W = maailma;
    if (tauolla || !(dt > 0)) return;
    dt = Math.min(dt, 0.1); aikaKaikki += dt;
    if (D) { D.t += dt; if (D.t >= D.kesto) seuraavaRivi(); }
    if (!K) {
      // automaattiset tehtävät (esim. puhelu edellisen jälkeen)
      for (const t of Object.values(T)) if (saatavilla(t) && t.laukaisu && t.laukaisu.tyyppi === 'automaattinen' && !W.sisalla) {
        autoOdotus[t.id] = (autoOdotus[t.id] || 0) + dt;
        if (autoOdotus[t.id] >= (t.laukaisu.viive || 0)) { autoOdotus[t.id] = 0; aloita(t.id); break; }
      }
    }
    if (!K) { const t = lahinTehtava(); const kh = t ? teksti('SYS_START', { nimi: t.nimi }) : ''; if (kh !== viimeKehote) { viimeKehote = kh; emit('kehote', kh || null); } paivitaMerkit(false); return; }
    if (viimeKehote) { viimeKehote = ''; emit('kehote', null); }
    if (K.tila !== 'kaynnissa') return;
    K.aika += dt;
    const s = K.t.vaiheet[K.i], v = K.v;
    v.t += dt; v.dt = dt;
    tarkistaFail(dt); if (!K || K.tila !== 'kaynnissa' || K.v !== v) return;
    const k = VAIHEET[s.tyyppi];
    if (!v.tehty && k && k.paivita) k.paivita(s, v, dt);
    if (!K || K.tila !== 'kaynnissa' || K.v !== v) return;
    if (v.tehty) seuraavaVaihe();
    paivitaMerkit(false);
  }

  // pelaajan toimintonäppäin (X / kosketusnappi): aloittaa tehtävän merkillä tai ohittaa repliikin
  function toiminta() {
    if (D) { seuraavaRivi(); return 'repliikki'; }
    if (!K) { const t = lahinTehtava(); if (t) { aloita(t.id); return 'aloitettu'; } }
    if (K && K.tila === 'epaonnistui') { uudelleen(); return 'uudelleen'; }
    return null;
  }
  function valitse(i) {
    if (!K || K.tila !== 'kaynnissa') return false;
    const s = K.t.vaiheet[K.i]; if (s.tyyppi !== 'valinta' || !K.v.odottaa) return false;
    const o = s.vaihtoehdot[i]; if (!o || !tayttyy(o.ehto)) return false;
    K.v.odottaa = false; emit('valinta', null); aseta(o.asettaa);
    if (o.rivit) puhu(o.rivit, 'puhe', valmis); else valmis();
    return true;
  }

  // ---------- tallennus ----------
  function tallenna() { if (!varasto) return; try { varasto.set(TALLENNUSAVAIN, JSON.stringify({ versio: VERSIO, tila })); } catch (e) {} }
  function lataa() {
    if (!varasto) return false;
    try { const j = JSON.parse(varasto.get(TALLENNUSAVAIN) || 'null'); if (j && j.tila) { tila = Object.assign(uusiTila(), j.tila); paivitaMerkit(true); return true; } } catch (e) {}
    return false;
  }
  // raha muualta pelistä (kyydit ym.): lähde näkyy ilmoituksessa
  function lisaaRaha(n, lahde = '') { n = Math.round(n); if (!n) return; tila.raha += n; tallenna(); emit('raha', { muutos: n, raha: tila.raha, lahde }); }
  function nollaa() { tila = uusiTila(); K = null; D = null; autoOdotus = {}; tallenna(); emit('nollattu', null); paivitaMerkit(true); }

  // ---------- kehittäjä ----------
  const kehittaja = {
    get paalla() { return kehitys; }, set paalla(b) { kehitys = !!b; },
    ohita() {
      if (!K) return false; if (K.tila === 'epaonnistui') return uudelleen();
      if (D) { const kun = D.kun; D = null; emit('repliikki', null); if (kun) kun(); }
      if (K && K.v && K.v.k && K.v.k.loppu) K.v.k.loppu();
      if (K && K.v.odottaa) { K.v.odottaa = false; emit('valinta', null); }
      valmis(); emit('mittari', null); emit('ajastin', null); if (K) seuraavaVaihe(); return true;
    },
    aloita: id => aloita(id, { pakota: true }),
    valmiiksi(id) { const t = T[id]; aseta(t.asettaa); if (!tila.valmiit.includes(id)) tila.valmiit.push(id); tallenna(); paivitaMerkit(true); },
    epaonnistu: syy => epaonnistu(syy),
    aseta: spec => { aseta(spec); tallenna(); paivitaMerkit(true); },
    vaihe: () => K ? { id: K.t.id, i: K.i, tyyppi: K.t.vaiheet[K.i].tyyppi, v: K.v, tila: K.tila } : null
  };

  return {
    on, paivita, toiminta, valitse, aloita, uudelleen, luovuta, lataa, tallenna, nollaa, lisaaRaha,
    tauko(b) { tauolla = !!b; }, get tauolla() { return tauolla; },
    get tila() { return tila; }, get kaynnissa() { return K ? { id: K.t.id, nimi: K.t.nimi, vaihe: K.i, tila: K.tila } : null; },
    saatavilla: () => Object.values(T).filter(saatavilla).map(t => ({ id: t.id, nimi: t.nimi, luku: t.luku })),
    tehtavat: () => Object.values(T).map(t => ({ id: t.id, nimi: t.nimi, luku: t.luku, valmis: tila.valmiit.includes(t.id), saatavilla: saatavilla(t) })),
    merkit, paikka, sopii, kasittelijat, kehittaja, teksti
  };
}
