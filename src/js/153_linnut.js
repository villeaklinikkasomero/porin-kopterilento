// 20.11.2026 (owner: "add these birds; pigeons in small flocks, gulls alone or in pairs"). Models: linnut.js (tools/props/porikopteri_linnut.py; clips Fly, Glide,
// Idle, Walk, Peck). Ground groups (pigeons 4-7, gulls 1-2) stand on pavement near the player, walk about and peck; when the player comes close (on foot 4.5 m,
// car 9 m, low helicopter 16 m) the group takes wing and lands 30-70 m away. Besides them one or two gulls circle overhead. Groups left over 140 m behind move
// to a new spot near the player; birds further than 90 m are not animated.
// → koodi on nyt moduulissa moduulit/linnut.js (21.11.2026). Tässä vain kutsu samassa kohdassa kuin ennen.
import kaynnista_linnut from './moduulit/linnut.js';
kaynnista_linnut({
  TZs,
  inRiver,
  scene,
  ROAD,
  get VEH() { return VEH; },
  carGround,
  bldTopAt,
  S,
  WALK
});
