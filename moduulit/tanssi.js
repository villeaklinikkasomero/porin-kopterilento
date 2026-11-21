// moduulit/tanssi.js – siirretty pääskriptistä (src/js/161_tanssi.js) omaksi moduulikseen 21.11.2026.
// Pääskriptin muuttujat tulevat oliossa P (getterit pitävät ne ajan tasalla); kirjastot ja data tuodaan suoraan.
// Kutsu ja P:n sisältö: src/js/161_tanssi.js. Uusi riippuvuus pääskriptiin → lisää se sinne P-olioon.


// ---------- music and dancing on foot (owner 20.11.2026: "tehdään mahdolliseksi, että botit voivat tanssia musiikin tahtiin"; started by the player's key) ----------
// B on foot (touch: the note button) starts a song of the radio (pop_*, rock_*; the next one each time) and stops it. While it plays, three parties
// out of four that come within 13 m of the player stop and dance facing him (clips Dance / Dance2 of npc_*.js), and the player's own character dances
// when it stands still (Dance of hahmo.js). In time: radio/tahti.json (tools/radio/tahti.py, librosa) has the beats of every song; the clips are
// four beats long and each frame they are set to the place of the song's beat (DANCE.sync), so nothing drifts. A song without beats: 120 BPM.
export default function kaynnista(P) {
const DANCE = { on: false, el: null, f: '', tab: null, beats: null, k: 0, idx: -1, ph: 0 }; window.__dance = DANCE;
fetch('./radio/tahti.json').then(r => r.json()).then(j => { DANCE.tab = j; }).catch(() => {});
DANCE.songs = () => { const L = [], seen = new Set(); if (P.RADIO.list) for (const k in P.RADIO.list) for (const e of P.RADIO.list[k]) if (/^(pop|rock|electric)_/.test(e.f) && !seen.has(e.f)) { seen.add(e.f); L.push(e); } return L; };
DANCE.play = () => { const L = DANCE.songs(); if (!L.length) { DANCE.on = false; P.toast('Musiikkia ei löytynyt', 1.6); return; }
  DANCE.idx = (DANCE.idx < 0 ? Math.floor(Math.random() * L.length) : DANCE.idx + 1) % L.length; const e = L[DANCE.idx], d = DANCE.tab && DANCE.tab[e.f];
  DANCE.beats = null; if (d && d.length > 8) { const b = new Float32Array(d.length); let t = 0; for (let i = 0; i < d.length; i++) { t += d[i]; b[i] = t / 1000; } DANCE.beats = b; } DANCE.k = 0; DANCE.f = e.f; DANCE.t0 = performance.now();
  try { DANCE.el = DANCE.el || new Audio(); DANCE.el.onended = () => { if (DANCE.on) DANCE.play(); }; DANCE.el.src = './radio/' + e.f; DANCE.el.volume = P.soundOn ? P.RADIO.vol : 0; DANCE.el.play().catch(() => {}); } catch (err) {}
  P.toast('🎵 ' + e.t + ' – B lopettaa', 2.6); };
DANCE.stop = () => { DANCE.on = false; if (DANCE.el) DANCE.el.pause(); };
DANCE.toggle = () => { if (!P.WALK.on || P.WALK.in) return; if (DANCE.on) { DANCE.stop(); P.toast('Musiikki pois', 1.2); } else { DANCE.on = true; DANCE.play(); } };
DANCE.tick = () => { if (!DANCE.on) return; if (!P.WALK.on || P.WALK.in) { DANCE.stop(); return; }      // the beat the song is at (DANCE.ph, counted from its first beat)
  const el = DANCE.el, b = DANCE.beats, t = el && !el.paused && !el.error && el.readyState >= 2 ? el.currentTime : (performance.now() - DANCE.t0) / 1000;      /* no sound (blocked, missing file, still loading): the dance goes on by the clock */ if (el) el.volume = P.soundOn ? P.RADIO.vol : 0;
  if (b) { let k = DANCE.k; if (k > b.length - 2 || b[k] > t) k = 0; while (k < b.length - 2 && b[k + 1] <= t) k++; DANCE.k = k; DANCE.ph = k + (t - b[k]) / (b[k + 1] - b[k]); } else DANCE.ph = t * 2; };
DANCE.sync = (a, off) => { const d = a.getClip().duration; a.timeScale = 0; a.time = ((((DANCE.ph + off) % 4) + 4) % 4) / 4 * d; };      // a four-beat clip at the song's beat
P.$('tdance').addEventListener('pointerdown', e => { e.preventDefault(); DANCE.toggle(); });

  return { DANCE };
}
