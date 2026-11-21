// ---------- music and dancing on foot (owner 20.11.2026: "tehdään mahdolliseksi, että botit voivat tanssia musiikin tahtiin"; started by the player's key) ----------
// B on foot (touch: the note button) starts a song of the radio (pop_*, rock_*; the next one each time) and stops it. While it plays, three parties
// out of four that come within 13 m of the player stop and dance facing him (clips Dance / Dance2 of npc_*.js), and the player's own character dances
// when it stands still (Dance of hahmo.js). In time: radio/tahti.json (tools/radio/tahti.py, librosa) has the beats of every song; the clips are
// four beats long and each frame they are set to the place of the song's beat (DANCE.sync), so nothing drifts. A song without beats: 120 BPM.
// → koodi on nyt moduulissa moduulit/tanssi.js (21.11.2026). Tässä vain kutsu samassa kohdassa kuin ennen.
import kaynnista_tanssi from './moduulit/tanssi.js';
const { DANCE } = kaynnista_tanssi({
  $,
  toast,
  RADIO,
  get soundOn() { return soundOn; },
  WALK
});
