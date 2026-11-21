// ---------- radio (car and helicopter, 19.11.2026; 20.11.2026: two channels): Radio Porikopteri = talk, mock adverts and the pop/electronic songs; Rock = rock songs. Songs made by the owner with Suno Pro (20.11.2026; commercial use rights), lyrics by Claude ----------
// The channels run 'live': the place in a channel's playlist comes from the clock, so switching away and back finds it further on.
const RADIO = { ch: 0, names: ['pois', 'Porikopteri', 'Rock'], list: null, el: null, idx: -1, vol: 0.6 }; window.__radio = RADIO;
fetch('./radio/radio.json').then(r => r.json()).then(j => { RADIO.list = j; }).catch(() => {});
RADIO.pos = ch => {   // [track index, seconds into it] for channel ch now
  const L = RADIO.list[RADIO.names[ch].toLowerCase()]; const tot = L.reduce((a, t) => a + t.d, 0);
  let x = (Date.now() / 1000 + ch * 977) % tot; for (let i = 0; i < L.length; i++) { if (x < L[i].d) return [L, i, x]; x -= L[i].d; } return [L, 0, 0]; };
RADIO.play = (ch, startAt) => {
  if (!RADIO.el) { RADIO.el = new Audio(); RADIO.el.preload = 'auto'; RADIO.el.addEventListener('ended', () => { if (RADIO.ch) { const [L] = RADIO.pos(RADIO.ch); RADIO.idx = (RADIO.idx + 1) % L.length; RADIO.load(L, RADIO.idx, 0); } }); }
  if (!ch || !RADIO.list) { RADIO.el.pause(); RADIO.show(); return; }
  const [L, i, x] = RADIO.pos(ch); RADIO.idx = i; RADIO.load(L, i, startAt === undefined ? x : startAt);
};
RADIO.load = (L, i, x) => { const el = RADIO.el, t = L[i]; el.src = './radio/' + t.f; el.volume = RADIO.level();
  const go = () => { try { el.currentTime = x; } catch (e) {} el.play().catch(() => {}); el.removeEventListener('loadedmetadata', go); };
  el.addEventListener('loadedmetadata', go); RADIO.cur = t; RADIO.show(); };
RADIO.next = () => { do { RADIO.ch = (RADIO.ch + 1) % RADIO.names.length; } while (RADIO.ch && RADIO.list && !RADIO.list[RADIO.names[RADIO.ch].toLowerCase()]); RADIO.play(RADIO.ch); toast('📻 ' + (RADIO.ch ? 'Radio ' + RADIO.names[RADIO.ch] : 'Radio pois'), 1.4); };
RADIO.show = () => { const n = RADIO.ch ? 'Radio ' + RADIO.names[RADIO.ch] : 'Radio pois', t = RADIO.ch && RADIO.cur ? RADIO.cur.t : '';
  $('rch').textContent = n; $('rsong').textContent = t; $('rch2').textContent = n; $('rsong2').textContent = t; };
RADIO.prev = () => { do { RADIO.ch = (RADIO.ch + RADIO.names.length - 1) % RADIO.names.length; } while (RADIO.ch && RADIO.list && !RADIO.list[RADIO.names[RADIO.ch].toLowerCase()]); RADIO.play(RADIO.ch); };
for (const [id, f] of [['rprev', () => RADIO.prev()], ['rnext', () => RADIO.next()]]) $(id).addEventListener('click', e => { e.preventDefault(); e.currentTarget.blur(); if (started) f(); });
$('rvol').addEventListener('input', e => { RADIO.vol = +e.target.value; RADIO.mute(); }); $('rvol').addEventListener('change', e => e.target.blur());
// 21.11.2026 (owner: "radio ei mene pois päältä, kun pelaaja nousee mistään ajoneuvosta"): the volume always comes from RADIO.level(), so a new song or
// the story's dialogue ducking (RADIO.duck, tarina/peli.js) can no longer turn the radio up while the player is on foot.
RADIO.duck = 1; RADIO.level = () => soundOn && !WALK.on ? RADIO.vol * RADIO.duck : 0;
RADIO.mute = () => { if (RADIO.el) RADIO.el.volume = RADIO.level(); };
$('tradio').addEventListener('pointerdown', e => { e.preventDefault(); if (started && !WALK.on) RADIO.next(); });
$('tact').addEventListener('pointerdown', e => { e.preventDefault(); if (started) walkAction(); });
{ const el = $('trun'); el.addEventListener('pointerdown', e => { el.setPointerCapture(e.pointerId); touchIn.run = 1; el.classList.add('on'); }); const up = () => { touchIn.run = 0; el.classList.remove('on'); }; el.addEventListener('pointerup', up); el.addEventListener('pointercancel', up); }

