// ---------- Eteläranta (renewed quay): lower walk by the water, seating steps with hedges, railing, pontoons, pavilions ----------
// → koodi on nyt moduulissa moduulit/etelaranta.js (21.11.2026). Tässä vain kutsu samassa kohdassa kuin ennen.
import kaynnista_etelaranta from './moduulit/etelaranta.js';
kaynnista_etelaranta({
  PSIL,
  TZg,
  TZs,
  QUAY_MODEL,
  QUAY_WALK,
  WREL,
  noT,
  inRiver,
  renderer,
  scene,
  get loadModel() { return loadModel; },
  get psilDeck() { return psilDeck; }
});
