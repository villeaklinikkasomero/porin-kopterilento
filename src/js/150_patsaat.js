// ---------- statues and memorials (19.11.2026): patsaat.js = the owner's list (21 works, Wikipedia; ten positions refined from OpenStreetMap) and his Blender
// models (origin on the ground, front +Z). A point that falls in a building or on a carriageway is moved to the nearest free spot (spiral, 30 m); with no
// heading given the work faces the nearest street.
// → koodi on nyt moduulissa moduulit/patsaat.js (21.11.2026). Tässä vain kutsu samassa kohdassa kuin ennen.
import kaynnista_patsaat from './moduulit/patsaat.js';
kaynnista_patsaat({
  OX0,
  OX1,
  OY0,
  OY1,
  TZs,
  inRiver,
  scene,
  ROAD,
  carGround,
  bldTopAt
});
