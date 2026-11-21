// ---------- sound ----------
let actx = null, sGain = null, sFilt = null, sLfo = null, soundOn = true;
function initSound() {
  try {
    actx = new (window.AudioContext || window.webkitAudioContext)();
    const buf = actx.createBuffer(1, actx.sampleRate * 2, actx.sampleRate), d = buf.getChannelData(0); let last = 0;
    for (let i = 0; i < d.length; i++) { last = (last + 0.04 * (Math.random() * 2 - 1)) / 1.04; d[i] = last * 4; }
    const src = actx.createBufferSource(); src.buffer = buf; src.loop = true;
    sFilt = actx.createBiquadFilter(); sFilt.type = 'lowpass'; sFilt.frequency.value = 300;
    const chop = actx.createGain(); chop.gain.value = 0.55; sLfo = actx.createOscillator(); sLfo.type = 'sawtooth'; sLfo.frequency.value = 12;
    const lg = actx.createGain(); lg.gain.value = 0.45; sLfo.connect(lg); lg.connect(chop.gain);
    sGain = actx.createGain(); sGain.gain.value = 0; src.connect(sFilt); sFilt.connect(chop); chop.connect(sGain); sGain.connect(actx.destination); src.start(); sLfo.start();
  } catch (e) { actx = null; }
}
function toggleSound() { soundOn = !soundOn; RADIO.mute(); toast(soundOn ? 'Ääni päällä' : 'Ääni pois', 1); }

