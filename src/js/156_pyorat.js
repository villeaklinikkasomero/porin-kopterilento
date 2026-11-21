// 20.11.2026 (owner: "bicycles on the market square, several parked, the same in front of SAMK, single bikes around the centre"). Model: pyora.js. All bikes
// are drawn as instances (one InstancedMesh per mesh of the model, frame paint tinted per bike). Racks: rows 0.62 m apart on free paving round Kauppatori
// (not near the helipad) and outside the wall of the SAMK campus that faces Satakunnankatu. Singles: seeded random spots on pavement within 2 m of a house
// wall, parked along the wall. Positions are found once from the game's own masks, so nothing stands on a carriageway or inside a house.
// → koodi on nyt moduulissa moduulit/pyorat.js (21.11.2026). Tässä vain kutsu samassa kohdassa kuin ennen.
import kaynnista_pyorat from './moduulit/pyorat.js';
kaynnista_pyorat({
  inCore,
  TZs,
  inRiver,
  scene,
  ROAD,
  HOME,
  carGround,
  bldTopAt
});
