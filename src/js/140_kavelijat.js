// ---------- people on foot (19.11.2026): six models npc_*.js (Idle / Walk), walking only the footway network walk.js (tools/roads/build_walk.py) ----------
// Parties are spawned around the player and dropped when far. Owner's rules: a child (tytto, poika) always walks with at least one of mies_a,
// nainen_a, nainen_b; other adults walk alone or in pairs; mies_b is rare. At a signalled crossing they wait for the green man (window.__sig.ped).
// → koodi on nyt moduulissa moduulit/kavelijat.js (21.11.2026). Tässä vain kutsu samassa kohdassa kuin ennen.
import kaynnista_kavelijat from './moduulit/kavelijat.js';
kaynnista_kavelijat({
  OX0,
  OX1,
  OY0,
  OY1,
  inCore,
  TZs,
  $,
  scene,
  ROAD,
  HOME,
  carGround,
  SOLID,
  bldTopAt,
  S,
  toast,
  get soundOn() { return soundOn; },
  WALK,
  walkFree,
  get DANCE() { return DANCE; }
});
