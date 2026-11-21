// ---------- state ----------
const SKID = 1.85;
const S = { x: HOME.x, y: HOME.y, alt: SKID, vx: 0, vy: 0, vz: 0, yaw: 0, yawRate: 0, pitch: 0, roll: 0, hp: 100, landed: true, rotorSpd: 0, dead: 0 };
const input = { f: 0, t: 0, s: 0, l: 0 };
const keys = new Set();
let started = false, camMode = 0, tourIdx = 0, tourT = 0, tourOn = false, tourDone = false, best = null;
let BESTKEY = 'pori-kopteri-best-' + DAY.key; try { best = parseFloat(localStorage.getItem(BESTKEY)) || null; } catch (e) {}

function pip(x, y, pts) { let r = false; for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) { const a = pts[i], b = pts[j]; if ((a[1] > y) !== (b[1] > y) && x < (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]) r = !r; } return r; }
const PROBE = [[0, 0], [3, 0], [-3, 0], [0, 3], [0, -3], [2.1, 2.1], [-2.1, 2.1], [2.1, -2.1], [-2.1, -2.1]];
// highest roof under the helicopter footprint at (x,y); 0 if open ground
function onPorinsilta(x, y, extra = 0) { const ux = Math.sin(PSIL.head), uy = Math.cos(PSIL.head), dx = x - PSIL.x, dy = y - PSIL.y, t = dx * ux + dy * uy, s = dx * uy - dy * ux;
  return Math.abs(s) < PSIL.half + extra && t > -14 && t < PSIL.len + 14 ? t : null; }
// Porinsilta: alkuperäisen mallin kansi maastonoston päällä (rampit päissä) ja uusi absoluuttinen kansi: suora rantakatujen välillä + kaari
function psilOld(t) { return t < 3 ? PSIL.deck * Math.max(0, Math.min(1, (t + 14) / 17)) : t > PSIL.len - 3 ? PSIL.deck * Math.max(0, Math.min(1, (PSIL.len + 14 - t) / 17)) : PSIL.deck; }
function psilDeck(t) { if (!PSIL_E) { const ux = Math.sin(PSIL.head), uy = Math.cos(PSIL.head); PSIL_E = [TZs(PSIL.x - ux * 14, PSIL.y - uy * 14), TZs(PSIL.x + ux * (PSIL.len + 14), PSIL.y + uy * (PSIL.len + 14))]; }
  const u = Math.max(0, Math.min(1, (t + 14) / (PSIL.len + 28))); return PSIL_E[0] + (PSIL_E[1] - PSIL_E[0]) * u + PSIL_NOUSU * 4 * u * (1 - u); }
function bridgeZ(x, y) { const t = onPorinsilta(x, y); if (t === null) return 0; return psilDeck(t) - TZs(x, y); }   // kannen korkeus maastonoston päällä
function triZ(T, x, y) {   // highest roof triangle under (x, y), or null
  let best = null;
  for (let k = 0; k < T.length; k += 9) {
    const ax = T[k], ay = T[k + 1], bx = T[k + 3], by = T[k + 4], cx = T[k + 6], cy = T[k + 7];
    const d = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy); if (Math.abs(d) < 1e-6) continue;
    const u = ((by - cy) * (x - cx) + (cx - bx) * (y - cy)) / d, v = ((cy - ay) * (x - cx) + (ax - cx) * (y - cy)) / d, w = 1 - u - v;
    if (u < -0.02 || v < -0.02 || w < -0.02) continue;
    const z = u * T[k + 2] + v * T[k + 5] + w * T[k + 8]; if (best === null || z > best) best = z;
  }
  return best;
}
function roofAt(x, y) {
  const tb = TZs(x, y), l = grid.get(gkey(Math.floor(x / GRID) + 100, Math.floor(y / GRID) + 100));
  let h = onPorinsilta(x, y) !== null ? bridgeZ(x, y) + tb : inRiver(x, y) ? (onBridgeDeck(x, y) ? brDeckZ(x, y) ?? tb : TER.wl) : Math.max(TZg(x, y), tb - 0.5);
  const qz = window.__quayZ ? window.__quayZ(x, y) : null;      /* 20.11.2026 (omistaja: "pelaaja uppoaa läpi"): the river mask's 4 m cells reach over the lower walk, so the player stood at the water level */
  if (qz !== null) h = qz;
  else if (window.__laituriZ) { const lz = window.__laituriZ(x, y); if (lz !== null) h = Math.max(h, lz); }      /* Etelärannan laiturit (ranta/ranta.js) */
  else if (ROAD.on && inCore(x, y) && !inRiver(x, y)) h = Math.max(h, groundTop(x, y) + (ROAD.paveAt(x, y) ? ROAD.pave : ROAD.asph));   // stand on the street surface
  if (!l) return h;
  for (const bi of l) { const b = blds[bi]; if (x < b.minx - 4 || x > b.maxx + 4 || y < b.miny - 4 || y > b.maxy + 4 || b.h + tb <= h) continue;
    if (b.tris) { for (const p of PROBE) { const z = triZ(b.tris, x + p[0], y + p[1]); if (z !== null && z + tb > h) h = z + tb; } continue; }
    for (const p of PROBE) if (pip(x + p[0], y + p[1], b.pts)) { h = b.h + tb; break; } }
  return h;
}

let toastT = 0;
function toast(msg, sec = 2.2) { const t = $('toast'); t.textContent = msg; t.classList.add('on'); toastT = sec; }
const fmtT = s => Math.floor(s / 60) + ':' + String(Math.floor(s % 60)).padStart(2, '0');
const fmtT1 = s => fmtT(s) + '.' + Math.floor(s * 10 % 10);

function resetHeli() { Object.assign(S, { x: HOME.x, y: HOME.y, alt: SKID, vx: 0, vy: 0, vz: 0, yaw: 0, yawRate: 0, hp: 100, landed: true, dead: 0 }); heli.visible = true; }
function newTour() { walkReset(); LB.show(false); tourIdx = 0; tourT = 0; tourOn = false; tourDone = false; NAV.route = null; NAV.tgt = null;
  if (VEH === 'car') { heli.visible = false; resetCar(); } else { carG.visible = false; resetHeli(); }
  setTarget(); toast(VEH === 'car' ? 'Aja valopylvään luo – navigaattori näyttää käännökset' : 'Nouse ilmaan ja lennä valopylvääseen'); }
function target() { return tourIdx < TOUR.length ? TOUR[tourIdx] : { n: VEH === 'car' ? 'Pysähdy Kirjurinluotoon' : 'Laskeudu Kirjurinluotoon', x: HOME.x, y: HOME.y, h: 0, land: true }; }
function setTarget() {
  const t = target(); beacon.position.set(t.x, 0, -t.y);
  const ry = t.land ? 3 : VEH === 'car' ? 7 : Math.max(38, Math.min(t.h, 70) + 26);
  beacon.getObjectByName('ring').position.y = ry; beacon.getObjectByName('ring2').position.y = ry;
  beacon.visible = !tourDone;
  $('mt').textContent = tourDone ? 'Vapaa lento' : t.n; $('mn').textContent = Math.min(tourIdx, TOUR.length) + '/' + TOUR.length;
  $('prog').firstElementChild.style.width = (tourIdx / (TOUR.length + 1) * 100) + '%';
}

function damage(d) {
  S.hp = Math.max(0, S.hp - d);
  if (S.hp <= 0 && !S.dead) { S.dead = 2.2; heli.visible = false; carG.visible = false; toast(VEH === 'car' ? 'Auto hajosi – palataan Kirjurinluotoon' : 'Kopteri hajosi – palataan Kirjurinluotoon', 2.2); }
}

