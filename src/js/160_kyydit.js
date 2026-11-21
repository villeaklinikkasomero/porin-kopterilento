// ---------- kyydit (owner 20.11.2026: "jos botti tekee kysymyksen, pelaaja voi hyväksyä sen ja esim kuskata botin Jazzeille, jolloin kerää pisteitä") ----------
// While the player drives (car, bike: the passenger sits on the rack) or flies, now and then a lone walker nearby stops, waves (a yellow arrow
// above the head) and asks for a ride to one of the landmarks of the daily-round pool. Stop beside them (car/bike 7 m; helicopter: land within 20 m)
// and press Y (or tap the button) to take them; a green column marks the destination; stop there (30 m, helicopter 45 m) to drop them off.
// Points (owner's choice): distance + speed bonus − knocks: base = straight-line metres / 10; up to +50 % when faster than the par time for the vehicle;
// every hit point lost on the way takes 2 % (at least 20 % stays). Rides and points are kept in this browser (localStorage 'pori-kyydit').
// → koodi on nyt moduulissa moduulit/kyydit.js (21.11.2026). Tässä vain kutsu samassa kohdassa kuin ennen.
import kaynnista_kyydit from './moduulit/kyydit.js';
kaynnista_kyydit({
  TZs,
  scene,
  POOL,
  get VEH() { return VEH; },
  CAR,
  carGround,
  S,
  get started() { return started; },
  toast,
  WALK
});
