// ---------- daily top-10: one document per player (runs/<their id>) with a field per day, d<YYYYMMDD> = best seconds, n = nickname
const LB = { open: false, rows: [], uid: null, ref: null, field: 'd' + DAY.key, saved: null, err: '' };
{
  $('dday').textContent = DAY.label; $('bsub').textContent = DAY.label + ' · ' + TOUR.length + ' maamerkkiä';
  $('droute').textContent = TOUR.map(t => t.n).join(' → ') + ' → Kauppatori';
  const nk = $('nick'), clean = v => (v || '').toUpperCase().replace(/[^A-Z0-9ÅÄÖ]/g, '').slice(0, 5);
  try { nk.value = clean(localStorage.getItem('pori-kopteri-nick')); } catch (e) {}
  nk.addEventListener('input', () => { const c = clean(nk.value); if (c !== nk.value) nk.value = c; try { localStorage.setItem('pori-kopteri-nick', c); } catch (e) {} });
  const note = m => { $('note1').textContent = m; };
  const render = () => { for (const id of ['top1']) { const ol = $(id); ol.textContent = '';
      LB.rows.forEach((r, i) => { const li = document.createElement('li'); if (r.id === LB.uid) li.className = 'me';
        for (const [c, v] of [['r', i + 1 + '.'], ['n', r.n], ['t', fmtT1(r.t)]]) { const sp = document.createElement('span'); sp.className = c; sp.textContent = v; li.appendChild(sp); }
        ol.appendChild(li); });
      if (!LB.rows.length) { const li = document.createElement('li'); li.textContent = 'Ei vielä tuloksia tänään – ole ensimmäinen!'; li.style.color = 'var(--dim)'; ol.appendChild(li); } } };
  LB.show = on => { LB.open = on; $('board').style.display = on ? 'block' : 'none'; };
  // at the finish: only a time that makes today's top-10 asks for a nickname
  LB.pending = null;
  LB.submit = t => {
    $('nickrow').style.display = 'none'; LB.pending = null;
    if (t < 30) return;
    const others = LB.rows.filter(r => r.id !== LB.uid), tenth = others.length >= 10 ? others[9].t : Infinity;
    const own = LB.saved !== null ? LB.saved : Infinity;
    if (t >= tenth) { note('Aikasi ' + fmtT1(t) + '. Listalle pääsi tänään ' + fmtT1(tenth) + ':llä. N = uusi yritys.'); return; }
    if (t >= own) { note('Päivän paras aikasi on ' + fmtT1(own) + '. N = uusi yritys.'); return; }
    if (!LB.ref) { note('Aikasi ' + fmtT1(t) + ' riittäisi listalle, mutta ' + (LB.err || 'tulostaulu ei ole käytössä tässä näkymässä.')); return; }
    LB.pending = t; $('nickrow').style.display = 'flex'; note('Aikasi ' + fmtT1(t) + ' riittää päivän top-10:een.');
    if (nk.value) { LB.save(); } else setTimeout(() => nk.focus(), 50);
  };
  LB.save = async () => {
    const t = LB.pending, n = clean(nk.value); if (t === null || !LB.ref) return;
    if (!n) { note('Anna nimimerkki (1–5 merkkiä).'); nk.focus(); return; }
    const body = { n, [LB.field]: Math.round(t * 10) / 10, at: Date.now() };
    try { const cur = await LB.ref.get(); if (cur.exists) await LB.ref.update(body); else await LB.ref.set(body); LB.saved = body[LB.field]; LB.pending = null; $('nickrow').style.display = 'none'; note('Aika ' + fmtT1(t) + ' tallennettu nimimerkillä ' + n + '.'); }
    catch (e) { note(e && e.code === 'invalid_argument' ? 'Sinulla ei ole oikeutta tallentaa tuloksia tähän peliin.' : 'Tuloksen tallennus ei onnistunut.'); }
  };
  $('nicksave').addEventListener('click', () => LB.save());
  // one list per vehicle: d<YYYYMMDD> helicopter, c<YYYYMMDD> car
  LB.listen = () => {
    const db = LB.db; if (!db) return; if (LB.unsub) { try { LB.unsub(); } catch (e) {} LB.unsub = null; }
    const field = LB.field;
    if (LB.ref) LB.ref.get().then(d => { const v = d.exists ? d.data()[field] : null; if (typeof v === 'number' && field === LB.field) LB.saved = v; }).catch(() => {});
    const timer = setTimeout(() => note('Tulostaulua ei saada juuri nyt yhteyttä.'), 10000);
    LB.unsub = db.collection('runs').where(field, '>', 0).orderBy(field).limit(10).onSnapshot(snap => {
      if (!snap.metadata.fromCache) clearTimeout(timer); if (field !== LB.field) return;
      LB.rows = snap.docs.map(d => { const v = d.data(); return { id: d.id, n: String(v.n || '?????').slice(0, 5), t: +v[field] }; }).filter(r => r.t > 0);
      render(); if ($('note1').textContent.startsWith('Ladataan') || $('note1').textContent.startsWith('Tulostaulua ei saada')) note('');
    }, () => { clearTimeout(timer); note('Tulostaulua ei voitu ladata.'); });
  };
  LB.useField = f => { if (LB.field === f) return; LB.field = f; LB.saved = null; LB.rows = []; render();
    $('bsub').textContent = DAY.label + ' · ' + TOUR.length + ' maamerkkiä · ' + (f[0] === 'c' ? 'autolla' : 'kopterilla'); LB.listen(); };
  render(); note('Ladataan tulostaulua…');
  (async () => {
    const db = window.claude ? await window.claude.use('db') : null, user = window.claude ? await window.claude.use('user') : null;
    if (!db) { note('Tulostaulu toimii, kun peli on avattu kirjautuneena Claudessa.'); return; }
    try { LB.uid = user ? await user.id() : null; } catch (e) {}
    if (LB.uid) LB.ref = db.collection('runs').doc(LB.uid); else LB.err = 'Tuloksia ei voi tallentaa tässä näkymässä.';
    try { if (user && (await user.can('data.write')) === false && !LB.uid) LB.ref = null; } catch (e) {}
    LB.db = db; LB.listen();
  })();
}
// 21.11.2026 aloitussivu tarinalle (UI_KONSEPTI_PELIIN.md): pääpainike aloittaa tai jatkaa tarinaa ilman ajoneuvovalintaa. Kopteri/auto-valinta ja
// päivän kierros (#kierros-osa) näkyvät vasta, kun tarina on antanut kopterin (FLAG_HELI_AUKI). window.__aloitus tulee aloitussivun skriptistä (01_runko.html).
const ALOITUS = window.__aloitus || { alkanut: false, heli: false };
let PELITILA = 'tarina';
function pickVeh(v, muista = true) {
  VEH = v; if (muista) try { localStorage.setItem('pori-veh', v); } catch (e) {}
  document.body.classList.toggle('car', v === 'car');
  $('vheli').setAttribute('aria-pressed', String(v === 'heli')); $('vcar').setAttribute('aria-pressed', String(v === 'car'));
  heli.visible = v === 'heli'; carG.visible = v === 'car'; if (v === 'car') { loadCar(); resetCar(); }
  goTeksti();
}
function goTeksti(virhe) {
  const t = $('go-t'), kt = $('gotour').querySelector('span');
  if ($('go').disabled) return;
  t.textContent = (virhe ? '(ei ilmakuvaa) ' : '') + (ALOITUS.alkanut ? 'Jatka tarinaa' : 'Aloita tarina');
  kt.textContent = VEH === 'car' ? 'Aja päivän kierros' : 'Lennä päivän kierros';
}
$('vheli').addEventListener('click', () => pickVeh('heli')); $('vcar').addEventListener('click', () => pickVeh('car'));
pickVeh(ALOITUS.heli ? VEH : 'heli', false);
function begin(tila) {
  if (started) return; started = true; $('start').style.display = 'none'; document.body.classList.add('aloitettu');
  PELITILA = tila === 'kierros' && ALOITUS.heli ? 'kierros' : 'tarina';
  if (PELITILA === 'tarina' && !ALOITUS.heli && VEH !== 'heli') pickVeh('heli', false);   // kopteri on lukossa ja piilossa (155 __heliLukko); tarina laittaa pelaajan jalan aloituspaikkaan
  window.__pelitila = PELITILA; dispatchEvent(new CustomEvent('pori-aloita', { detail: { tila: PELITILA } }));   // tarina/peli.js: kierroksen HUD-kortti näkyviin vain kierroksella
  if (VEH === 'car') { BESTKEY = 'pori-auto-best-' + DAY.key; try { best = parseFloat(localStorage.getItem(BESTKEY)) || null; } catch (e) { best = null; } LB.useField('c' + DAY.key); }
  camPos.copy(camera.position); camLook.set(HOME.x, 5, -HOME.y);
  initSound(); newTour();
  { const go = () => { if (RADIO.list) { RADIO.ch = 1; RADIO.play(1); } else setTimeout(go, 500); }; go(); }   // Radio Porikopteri is on at the start, in the helicopter too
}
$('go').addEventListener('click', () => begin('tarina'));
$('gotour').addEventListener('click', () => begin('kierros'));
// Aloita alusta: kaksivaiheinen varmistus sivulla (ei selaimen confirm-ikkunaa)
$('alusta').addEventListener('click', () => { $('alusta').hidden = true; $('alusta-varmista').hidden = false; $('alusta-kylla').focus(); });
$('alusta-peru').addEventListener('click', () => { $('alusta-varmista').hidden = true; $('alusta').hidden = false; });
$('alusta-kylla').addEventListener('click', () => {
  try { localStorage.removeItem('pori-tarina-v1'); localStorage.removeItem('pori-tarina-yhteenveto'); } catch (e) {}
  const T = window.__tarina; if (T && T.moottori) T.moottori.nollaa();
  Object.assign(ALOITUS, { alkanut: false, heli: false }); document.body.classList.remove('tarina-alkanut', 'kierros-auki');
  $('alusta-varmista').hidden = true; $('tall-tiedot').textContent = 'Luku 1 · Eteläranta'; $('kierros-osa').hidden = true;
  const k = $('tapa-kierros'); k.classList.add('lukossa'); k.querySelector('use').setAttribute('href', '#ik-lukko'); $('kierros-t').textContent = 'Avautuu tarinan edetessä.';
  pickVeh('heli', false); goTeksti(); $('go').focus();
});
for (const id of ['mission', 'mapwrap', 'gauges', 'street', 'help', 'radio']) $(id).style.visibility = 'visible';

// load the aerial image
{
  const img = new Image();
  img.onload = () => { orto.image = img; orto.needsUpdate = true; groundMat.color.set(0xffffff); roofMat.color.set(0xffffff); groundMat.needsUpdate = roofMat.needsUpdate = true; $('go').disabled = false; $('gotour').disabled = false; goTeksti(); window.__ready = true; };
  img.onerror = () => { $('go').disabled = false; $('gotour').disabled = false; goTeksti(true); groundMat.map = null; roofMat.map = null; groundMat.color.set(0x6f7a70); roofMat.color.set(0x8a8f92); groundMat.needsUpdate = roofMat.needsUpdate = true; };
  img.src = './maa/ot_s/orto.jpg';   // 21.11.2026 sävykorjattu (tools/maa/orto_savy.py)
}
setTarget();
