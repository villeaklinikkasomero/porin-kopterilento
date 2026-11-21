// 20.11.2026 (owner): car race "Kespan lenkki", 3.3 km. Start at the first lights of Mikonkatu with three bots, off on green: Mikonkatu - Otavankatu -
// Luvianpuistokatu - the police roundabout - round the Tiilimäki Neste - back the same way - Otavankatu - Itsenäisyydenkatu - Antinkatu - Liisankatu -
// Isolinnankatu - Mikonkatu. Route = road-graph nodes (KESPA.p, game metres; the Neste yard loop is OSM way 357449244), KESPA.t = [metres, arrow, name] of the
// turns. G (or the flag button) in the car puts the field on the grid. Progress is the projection on the route within a forward window, so the two passes of
// Luvianpuistokatu cannot be mixed up and no part can be skipped. Bots: pure pursuit along the route, slower into bends, pulling out past slower cars.
// Normal traffic and its lights stay on; only the start waits for green.
// → koodi on nyt moduulissa moduulit/kespan_lenkki.js (21.11.2026). Tässä vain kutsu samassa kohdassa kuin ennen.
import kaynnista_kespan_lenkki from './moduulit/kespan_lenkki.js';
kaynnista_kespan_lenkki({
  TZs,
  scene,
  get VEH() { return VEH; },
  CAR,
  carG,
  carGround,
  S,
  get started() { return started; },
  toast,
  fmtT1,
  WALK
});
