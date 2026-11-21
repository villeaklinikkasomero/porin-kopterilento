// ---------- city bus (20.11.2026, owner: "a bus the player can drive or ride; borrowed at the Kauppatori stands or the Matkakeskus the player drives the
// line, picks up passengers and lets them off when the stop button is pressed"). Model: bussi.js / bussi_m.js (tools/vehicles/porikopteri_bussi.py, doors
// DoorF_A/B and DoorM_A/B turn about their hinges, damage steps as in the cars). Stops: OpenStreetMap (tools/bus/osm_stops.json, 20.11.2026), the 87 in the
// sharp core. Two lines of our own over real stops: 1 Kauppatori - Puuvilla and back, 2 Matkakeskus - Kauppatori and back. Parked buses wait at
// Kauppatori laituri 2 and Matkakeskus laituri 1; on foot next to one Enter takes it and starts that line.
// Live buses (smooth, 20.11.2026): drawn 2 s behind the feed, interpolated between received points and kept on our street lanes.
// Live buses: Digitransit's open MQTT feed (wss://mqtt.digitransit.fi, topic /gtfsrt/vp/Pori/#, GTFS-RT vehicle positions, no key) puts the real Pori
// buses on the streets where they are right now (only while they run). On foot next to one that stands still, Enter gets on; N (or the bell button) asks
// it to stop and the player gets off at the next halt. The live buses are drawn only - they do not collide.
// → koodi on nyt moduulissa moduulit/bussi.js (21.11.2026). Tässä vain kutsu samassa kohdassa kuin ennen.
import kaynnista_bussi from './moduulit/bussi.js';
kaynnista_bussi({
  OX0,
  OX1,
  OY0,
  OY1,
  TZs,
  isTouch,
  scene,
  camera,
  ROAD,
  get VEH() { return VEH; },
  CAR,
  get carLoading() { return carLoading; },
  CARM,
  loadCar,
  carGround,
  S,
  input,
  get started() { return started; },
  toast,
  get actx() { return actx; },
  WALK,
  walkG,
  walkFree,
  camPos,
  camLook,
  tmp,
  tmp2
});
