// ---------- trees ----------
// OpenStreetMap trees + trees found in the aerial photo (trees_extra.js: crown cover where OSM has none; parks, woods, railway verges, gardens).
// Leaf-card models near the helicopter, cheap crowns (icosahedron / cone) further out; the visible sets are refreshed as the helicopter moves.
// → koodi on nyt moduulissa moduulit/puut.js (21.11.2026). Tässä vain kutsu samassa kohdassa kuin ennen.
import kaynnista_puut from './moduulit/puut.js';
kaynnista_puut({
  PSIL,
  inCore,
  scene,
  TREES,
  loadModel,
  get S() { return S; }
});
