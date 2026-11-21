// ---------- buildings ----------
const PAL = [0xe9dcc0, 0xd9c7a2, 0xf0ead9, 0xcdb593, 0xb9805e, 0xa8563f, 0xd8d5cc, 0xbfc4c6, 0xe6cf9a, 0xc7a988, 0x9aa3a8, 0xe3d6c4, 0xb46a4c, 0xdcd0b8];
const blds = [];           // {pts:[[x,y]..], h, minx,maxx,miny,maxy}
const LMAT = { kirkko: [293.4, 369.7], raati: [-115.6, 394.1], kaupungintalo: [-57.7, 331.2], teatteri: [-201, 378], taidemuseo: [-94.8, 462.6], kauppahalli: [150, -32.8], vesitorni: [-835, -135], puuvilla: [230, 1000], promenadi: [9.2, -238.7], bepop: [58.3, -382.3], kirjasto: [-258, 114], museo: [-264.8, 455.9], tehdas: [160.2, 763.6], kehraamo: [85, 834], tori: [31, 81], lava: [90, 61], lokki: [-389, 998], isokarhu: [120.9, -179.4], mausoleumi: [-1946, 198.1], areena: [-1615.1, -1391.6], isokappeli: [-1809.2, 141.6], pienikappeli: [-2008.2, 191.1], harjoitushalli: [-1614.9, -1120.8], asema: [-443.0, -954.0], samk: [-268.0, -992.0], cygnaeus: [-321.0, -491.0] };
const LMB = {}, CHURCH = {};
const GRID = 40, grid = new Map();
const gkey = (i, j) => i * 4096 + j;
const roofMat = new THREE.MeshBasicMaterial({ map: orto, color: 0x30383a, side: THREE.DoubleSide });
{
  const facade = (() => {
    const c = document.createElement('canvas'); c.width = c.height = 128; const x = c.getContext('2d');
    x.fillStyle = '#fff'; x.fillRect(0, 0, 128, 128);
    x.fillStyle = 'rgba(0,0,0,.07)'; x.fillRect(0, 120, 128, 8);
    x.fillStyle = '#2c3a48'; x.fillRect(36, 26, 56, 62);
    x.fillStyle = '#5d7890'; x.fillRect(40, 30, 22, 54); x.fillRect(66, 30, 22, 54);
    x.fillStyle = 'rgba(255,255,255,.28)'; x.fillRect(40, 30, 22, 14);
    const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace;
    t.anisotropy = 4; return t;
  })();
  const wp = [], wn = [], wu = [], wc = [], rp = [], ru = [];
  // facade modules rendered in Blender (one bay x one storey); alpha marks the wall area that takes the building's own colour
  const STY = ['classic', 'arch', 'apart', 'ribbon', 'shop', 'brick', 'wood'], BAYW = [3.2, 3.2, 3.6, 3.0, 8.0, 3.2, 2.8], FLH = [3.4, 3.4, 3.0, 3.4, 3.8, 3.4, 3.0];
  const WOODPAL = [0xd9b45f, 0x9c3d2e, 0xe8e2d0, 0xc9d2bd, 0xb9c4cc, 0xd8c08a, 0xa8563f, 0xe6d9a8, 0x9aa585, 0xd2a878, 0xefe6c4, 0x8c4a3a];   // painted timber houses
  const rp2 = [], ru2 = [];
  const obbOf = pts => { let best = null;      // smallest enclosing rectangle, long axis first
    for (let i = 0; i < pts.length; i++) { const a = pts[i], b = pts[(i + 1) % pts.length], L = Math.hypot(b[0] - a[0], b[1] - a[1]); if (L < 1.5) continue;
      const ux = (b[0] - a[0]) / L, uy = (b[1] - a[1]) / L; let u0 = 1e9, u1 = -1e9, v0 = 1e9, v1 = -1e9;
      for (const q of pts) { const u = q[0] * ux + q[1] * uy, v = -q[0] * uy + q[1] * ux; u0 = Math.min(u0, u); u1 = Math.max(u1, u); v0 = Math.min(v0, v); v1 = Math.max(v1, v); }
      const ar = (u1 - u0) * (v1 - v0); if (!best || ar < best.ar) { const cu = (u0 + u1) / 2, cv = (v0 + v1) / 2; best = { ar, ux, uy, a: (u1 - u0) / 2, b: (v1 - v0) / 2, cx: cu * ux - cv * uy, cy: cu * uy + cv * ux }; } }
    if (best && best.a < best.b) best = { ...best, ux: -best.uy, uy: best.ux, a: best.b, b: best.a };
    return best; };
  const SB = STY.map(() => ({ p: [], n: [], u: [], c: [] }));
  // photo facades from Porin kaupunki street photos: one bay-wide strip from street to eave per building (photos/build_ph.py)
  // building index -> styles; 'west' picks the second style for walls west of that x (one footprint, two facades)
  let PHS = { 603: [{ t: 'ph_603', bw: 10.16 }], 604: [{ t: 'ph_604y', bw: 4.81 }, { t: 'ph_604b', bw: 4.59, cut: 10.4 }], 1726: [{ t: 'ph_1726', bw: 8.12 }, { t: 'ph_1726g', bw: 12.59, cut: -17.612 }], 1599: [{ t: 'ph_1599', bw: 12.11 }], 602: [{ t: 'ph_602', bw: 2.23, g: 0.224, n: 5, wide: 4, shop: 3 }] };   // g, n: the photo shows the ground floor (share g of its height) and n upper storeys; wide, shop: the strip is laid out 'wide' bays side by side and its ground floor redrawn as 'shop' wide shop windows between piers
  Object.assign(PHS, PHSJ);
  const PB = {};
  const hsh = (i, k) => { let x = (i * 2654435761 + k * 40503) >>> 0; x ^= x >>> 15; x = Math.imul(x, 2246822519) >>> 0; x ^= x >>> 13; return (x >>> 0) / 4294967296; };
  const KN = ['kivi0', 'kivi1', 'kivi2', 'kivi3', 'kivi4', 'tori0', 'tori1', 'tori2', 'tori3', 'tori4', 'tori5', 'uima', 'p1', 'kivi5', 'kl0', 'kl1', 'karhu', ...CZN], KW = KN.map(() => ({ p: [], n: [], u: [], c: [] })), KWP = KN.map(() => ({ p: [], n: [], u: [], c: [] })), ZB = {1450:16,1451:16,1511:16,1512:16,1515:16,1261:14,1336:14,1337:14,1338:14,1351:14,1357:14,1368:14,1369:14,1370:14,1446:14,1447:14,1448:14,1449:14,1458:14,1461:14,1462:14,1516:14,1517:14,1525:14,1535:14,1297:15,1309:15,1310:15,1352:15,1353:15,1373:15,1374:15,1375:15,1377:15,1398:15,1407:15,1527:15,1528:15,1583:3,1311:0,1308:0,1513:0,1249:0,1284:0,1454:0,1281:0,1456:0,1292:1,1293:1,1294:1,1296:1,1341:1,1295:1,1576:1,1574:1,1577:1,1622:1,1575:1,1287:2,1288:2,1285:2,1286:2,1565:2,1289:2,1564:2,1290:2,1559:2,8386:2,1563:2,1562:2,1561:2,1560:2,1744:2,1581:3,1716:3,1586:3,1604:3,1578:3,1603:3,1579:3,1585:3,1572:4,1573:4,1607:4,1566:4,1567:4,8385:4,1553:13,1620:13,1550:13,1619:13,1552:13,1551:13,1548:13,1549:13,125:12,126:12,127:12,129:12,169:12,272:12,273:12,133:12,135:12,275:12,276:12,277:12,290:12,291:12,587:11,1725:5,1727:5,1728:5,1729:5,1730:5,1731:5,1732:5,1600:5,1621:5,1315:6,1490:6,1491:6,1492:6,1493:6,1494:6,1495:6,1496:6,1361:6,1363:6,1367:6,1488:6,1489:6,1362:6,1364:6,1365:6,1366:6,1372:6,161:7,162:7,163:7,207:7,208:7,561:7,562:7,1313:7,1314:7,1344:7,1345:7,1346:7,1347:7,1348:7,1349:7,1497:7,1498:7,1499:7,1312:7,1259:7,563:8,564:8,637:8,638:8,639:8,641:8,642:8,1216:8,1220:9,640:9,1723:9,1724:9,1734:9,1217:9,1218:9,1219:9,1192:9,1601:10,1623:10,1624:10,1720:10,1721:10,1722:10}, ZROOF = new Set([1600,1725,1726,1728,1729,1315,1490,1361,1366,161,163,1497,564,563,603,604,637,602,1217]); /* ZB: building index -> Blender-made block (blocks round the market square) */ for (const n of CZN) for (const i of CZ.zones[n].ids) if (ZB[i] === undefined) ZB[i] = KN.indexOf(n);   /* city blocks */ for (const k in PHSJ) delete ZB[k];   /* photo facades: the night bake leaves these out of the Blender blocks */ let bIdx = -1; const SKOOLI = 1504508728, OWNROOF = new Set([SKOOLI, 950288076, 950288077, 950288080, 513103884, 513103888]), karhuPts = [];   // map ids of   // buildings newer than the aerial image get a plain roof   // Kivi-Pori blocks are kept apart so Blender-made versions can replace them
  const L2Z = new Set(['p1', 'kivi0', 'kivi1', 'kivi2', 'kivi3', 'kivi4', 'kivi5', 'kl0', 'kl1', ...CZN].map(n => KN.indexOf(n)));   // Kivi-Pori and p1: facades on the LoD2 shells
  const SRW = { 1417694311: 1, 89689073: 1, 89689074: 1, 1555668839: 1, 173062122: 1, 173062127: 1, 173062123: 1, 173062124: 1, 89689063: 1, 42972643: 1, 1555668980: 2, 100026585: 3 }, SRBRICK = [0x9a4634, 0x8f4232, 0xa24c38, 0x934536];
  const col = new THREE.Color(), col2 = new THREE.Color(), rc = new THREE.Color(), LHIDE = new Set(LOD2.hide);
  const liftParts = [];
  const L2OLD = new Set([572, 70, 136]);   // Kulturhuset Fiini (2025) stands where the scanned 1880/1900 houses were; Eteläpuisto 13: the scan set back the top storey, the house has one flat roof
  const HFIX = { 70: 24.0, 136: 7.7 };   // roof height of the L2OLD houses built on their footprint in Blender
  const wpick = (L, r) => { let t = 0; for (const e of L) t += e[1]; let k = r * t; for (const e of L) { k -= e[1]; if (k <= 0) return e[0]; } return L.length ? L[0][0] : '#e6dcc2'; };
  const ROOFZ = new Set(['kivi0', 'kivi1', 'kivi2', 'kivi3', 'kivi4', 'kivi5', 'kl0', 'kl1'].map(n => KN.indexOf(n)));   // blocks whose roofs are in the Blender model
  for (const b of CITY.b) {
    bIdx++;
    if (LOOK.b[bIdx] && LOOK.b[bIdx].gone) continue;   // demolished since the map data (styles 'gone', e.g. Saukkosen talo 1748): the bake skips it, so must the plain walls (phones never load the bakes)
    if (RATA.hideB && RATA.hideB.includes(bIdx)) continue;   // 20.11.2026: aseman laiturikatos ja porraskatos ovat rata/rata.js:ssä (LoD2-laatikot peittivät raiteet)
    if (b.w === 1196441531) continue;   // Barco: the moored ship is a Blender model (below), not a building
    const pts = []; for (let i = 0; i < b.p.length; i += 2) pts.push([b.p[i] / 10, b.p[i + 1] / 10]);
    const L2raw = L2OLD.has(bIdx) ? null : LOD2.b[bIdx];   // L2OLD: the scan predates a new building on the plot
    let kc = [0, 0]; for (const q of pts) { kc[0] += q[0] / pts.length; kc[1] += q[1] / pts.length; }
    const ownBlock = ZB[bIdx] !== undefined && !L2Z.has(ZB[bIdx]);   // Blender blocks with their own heights (tori, uima)
    if (LHIDE.has(bIdx) && ZB[bIdx] === undefined) continue;   // covered by a neighbour's LoD2 model
    const L2 = L2raw && !OWNROOF.has(b.w) && (ZB[bIdx] === undefined || L2Z.has(ZB[bIdx])) ? L2raw : null;   // blocks built on the LoD2 shells keep the measured roofs
    let isLm = false; for (const k in LMAT) if (!LMB[k] && pip(LMAT[k][0], LMAT[k][1], pts)) isLm = true;
    const L2c = isLm ? null : L2;                    // landmarks are Blender models with their own height
    const lk_ = LOOK.b[bIdx];
    if (lk_ && lk_.lift) { liftParts.push([b, lk_]); continue; }   // canopies and footbridges: drawn in the air below
    let h = L2c ? L2c.h : b.h;
    if (!L2c && !isLm && ZB[bIdx] === undefined && h > 15) h = lk_ && lk_.f ? lk_.f * 3 + 1 : h * 0.76;   // level-count heights in the map data run about a third too tall (checked against the oblique photos)
    if (HFIX[bIdx]) h = HFIX[bIdx];
    const rec = { pts, h, minx: 1e9, maxx: -1e9, miny: 1e9, maxy: -1e9 };
    if (L2c) {   // collide with the measured roof surfaces, not the tallest point over the whole footprint (Sokos: 56 m tower part)
      const R = L2c.r, ox = L2c.o[0], oy = L2c.o[1], T = new Float32Array(R.length);
      for (let k = 0; k < R.length; k += 3) { T[k] = (R[k] + ox) / 10; T[k + 1] = (R[k + 1] + oy) / 10; T[k + 2] = R[k + 2] / 10; }
      rec.tris = T;
    }
    for (const q of pts) { rec.minx = Math.min(rec.minx, q[0]); rec.maxx = Math.max(rec.maxx, q[0]); rec.miny = Math.min(rec.miny, q[1]); rec.maxy = Math.max(rec.maxy, q[1]); }
    const bi = blds.push(rec) - 1;
    for (let i = Math.floor((rec.minx - 5) / GRID); i <= Math.floor((rec.maxx + 5) / GRID); i++)
      for (let j = Math.floor((rec.miny - 5) / GRID); j <= Math.floor((rec.maxy + 5) / GRID); j++) {
        const k = gkey(i + 100, j + 100); if (!grid.has(k)) grid.set(k, []); grid.get(k).push(bi);
      }
    let lk = null; for (const k in LMAT) if (!LMB[k] && pip(LMAT[k][0], LMAT[k][1], pts)) lk = k;
    if (lk) { LMB[lk] = { pts, rec }; continue; }
    let T = null; { let cx = 0, cy = 0; for (const q of pts) { cx += q[0]; cy += q[1]; } cx /= pts.length; cy /= pts.length;
      }
    if (ZB[bIdx] !== undefined) T = KW[ZB[bIdx]];
    const tp = T ? T.p : wp, tn = T ? T.n : wn, tu = T ? T.u : wu, tc = T ? T.c : wc;
    // facade style from height, colour and position (no building-type data in the map for most houses)
    const srk = SRW[b.w];   // Sampo-Rosenlew works: 1800s red brick halls, one blue press hall
    const lcol = lk_ && lk_.w && !(lk_.m && (b.k === 1 || b.k === 2)) ? lk_.w :   /* small houses: the projected measurement picked up roofs and shadows (dark brown), use the timber palette */ (b.k === 1 || b.k === 2) && !srk ? wpick(LOOK.wood, hsh(b.w || bIdx, 5)) : wpick(LOOK.pal, hsh(b.w || bIdx, 5)), lbrick = lk_ ? lk_.k === 'brick' : ['#a85a42', '#c4683f'].includes(lcol);
    const house = b.k === 1 && !srk, shed = b.k === 2 && !srk, brickish = !house && !shed && (LOOK.pal.length ? lbrick : [4, 5, 12].includes(b.i % PAL.length)), r1 = hsh(b.w || bIdx, 1), r2 = hsh(b.w || bIdx, 2);
    const sty = lk_ && lk_.st === 'classic' ? 0 : srk >= 2 ? 3 : srk ? 5 : house || shed ? 6 : h < 5 ? 0 : brickish && h < 14 ? 5 : brickish ? 2 :   /* tall brick blocks are modern flats: plain wide windows, not the old sash-window brick facade */ h >= 14 ? (r1 < 0.72 ? 2 : 3) : (r1 < 0.48 ? 0 : r1 < 0.62 ? 1 : 2);
    let bcx = 0, bcy = 0; for (const q of pts) { bcx += q[0]; bcy += q[1]; } bcx /= pts.length; bcy /= pts.length;
    const coreB = inCore(bcx, bcy), RP = coreB ? rp : rp2, RU = coreB ? ru : ru2, ruv = q => coreB ? [(q[0] + HW) / (2 * HW), (q[1] - YS) / YSPAN] : [(q[0] - OX0) / OXS, (q[1] - OY0) / OYS];
    if (house || shed) col.setHex(WOODPAL[(b.i + (shed ? 3 : 0)) % WOODPAL.length]).multiplyScalar(1.02 + (b.i % 5) * 0.03);
    const shops = !T && h >= 7 && !!(lk_ && lk_.shop);   // shop fronts only on the commercial streets of the centre (styles.json 'shop', from the street names)   // shop fronts on the ground floor in the grid centre
    // wall colour: palette tinted a little by the roof colour seen in the aerial image
    if (LOOK.pal.length) { col.set(lcol); { const hs = {}; col.getHSL(hs); if (hs.h > 0.085 && hs.h < 0.17 && hs.s > 0.4) col.setHSL(hs.h + 0.012, hs.s * 0.7, Math.min(0.8, hs.l * 1.1 + 0.04)); }   // ochre read as mustard: paler, cleaner yellow
    col.multiplyScalar(lk_ ? 1 : 0.94 + (b.i % 5) * 0.02); }
    else { col.setHex(PAL[b.i % PAL.length]); rc.setRGB(b.c[0] / 255, b.c[1] / 255, b.c[2] / 255, THREE.SRGBColorSpace); col.lerp(rc, 0.18); col.multiplyScalar(0.86 + (b.i % 7) * 0.025); }
    if (srk === 1) col.setHex(SRBRICK[b.i % SRBRICK.length]); else if (srk === 2) col.setHex(0x2f63a6); else if (srk === 3) col.setHex(0x2b4f86);
    col2.copy(col); if (lk_ && lk_.w2) col2.set(lk_.w2);   // second wall colour in wide vertical bands (two strong colours measured on the same building)
    const win = house ? true : shed ? false : h >= 5;
    if (L2 && PHS[bIdx]) {   // photo-textured walls
      const PH602CUT = [[97.5, -41.8], [111.5, -45.1], [117.1, -21.1], [103.0, -17.9]];   // footprint of 1217
      const ox = L2.o[0], oy = L2.o[1], W = L2.w, E = Math.max(2.4, L2.e || L2.h), st = PHS[bIdx];
      // the photo strip was fitted to the median eave E; parts of the building with a higher eave (Yrjönkatu 10 towards the square: 23 m against 19.8 m)
      // were left blank under the roof.  With g and n the strip is extended by whole storeys of the same height up to the highest flat-topped wall.
      let Ev = E; const S0 = st[0];
      if (S0.g && S0.n) { const gh = S0.g * E, sh = (1 - S0.g) * E / S0.n, bins = new Map(); let tot = 0;
        for (let k = 0; k < W.length; k += 12) { const ax = W[k] / 10, ay = W[k + 1] / 10, az = W[k + 2] / 10, bx = W[k + 4] / 10 - ax, by = W[k + 5] / 10 - ay, bz = W[k + 6] / 10 - az, cx = W[k + 8] / 10 - ax, cy = W[k + 9] / 10 - ay, cz = W[k + 10] / 10 - az;
          const ar = 0.5 * Math.hypot(by * cz - bz * cy, bz * cx - bx * cz, bx * cy - by * cx), zt = Math.round(Math.max(az, az + bz, az + cz)); bins.set(zt, (bins.get(zt) || 0) + ar); tot += ar; }
        let T = E; for (const [zt, ar] of bins) if (ar > 0.03 * tot && zt > T) T = zt;                 // gables and small roof structures do not count
        S0.rows = Math.max(S0.n, Math.round((T - gh) / sh)); Ev = gh + S0.rows * sh; }
      // upper walls carry no bay position (u = -1) and stayed blank.  Where such a wall stands in the plane of a facade below it, it takes that
      // facade's bay position, so the extra storey lines up with the windows underneath.
      const planes = new Map(), pkey = (x, y, z, vx, vy, vz, wx, wy, wz) => { let nx = vy * wz - vz * wy, ny = vz * wx - vx * wz; const nl = Math.hypot(nx, ny); if (nl < 1e-6) return null; nx /= nl; ny /= nl;
        if (nx < -1e-6 || (Math.abs(nx) <= 1e-6 && ny < 0)) { nx = -nx; ny = -ny; } return { k: Math.round(nx * 30) + ',' + Math.round(ny * 30) + ',' + Math.round((x * nx + y * ny) * 2), tx: -ny, ty: nx }; };
      if (S0.g && S0.n) for (let k = 0; k < W.length; k += 12) { const q = [0, 1, 2].map(j => [(W[k + j * 4] + ox) / 10, (W[k + j * 4 + 1] + oy) / 10, W[k + j * 4 + 2] / 10, W[k + j * 4 + 3] / 10]);
        if (q.some(v => v[3] < 0)) continue; const pk = pkey(q[0][0], q[0][1], q[0][2], q[1][0] - q[0][0], q[1][1] - q[0][1], q[1][2] - q[0][2], q[2][0] - q[0][0], q[2][1] - q[0][1], q[2][2] - q[0][2]); if (!pk || planes.has(pk.k)) continue;
        const pr = q.map(v => v[0] * pk.tx + v[1] * pk.ty); let a = 0, b = 1; if (Math.abs(pr[2] - pr[0]) > Math.abs(pr[1] - pr[0])) b = 2; if (Math.abs(pr[b] - pr[a]) < 0.2) continue;
        const sg = (q[b][3] - q[a][3]) / (pr[b] - pr[a]) > 0 ? 1 : -1; planes.set(pk.k, { tx: pk.tx, ty: pk.ty, sg, off: q[a][3] - sg * pr[a] }); }
      for (let k = 0; k < W.length; k += 12) {
        let ax = (W[k] + ox) / 10, ay = (W[k + 1] + oy) / 10, bx = (W[k + 4] + ox) / 10, by = (W[k + 5] + oy) / 10, cx = (W[k + 8] + ox) / 10, cy = (W[k + 9] + oy) / 10;
        const az = W[k + 2] / 10, bz = W[k + 6] / 10, cz = W[k + 10] / 10;
        // 602's LoD2 shell runs on over Hallitalo (1217): its photo walls stood 0.6 m inside that house and filled the Kauppahalli portal recess (20.11.2026).
        // Corners inside 1217's footprint move north along Yrjönkatu onto the houses' boundary. DO NOT DROP: without this the portal recess shows dark "glass".
        const mv602 = (x, y) => { if (bIdx !== 602 || !pip(x, y, PH602CUT)) return [x, y]; const d = (103.0 - x) * 0.2245 + (-17.9 - y) * 0.9755 + 0.05; return [x + 0.2245 * d, y + 0.9755 * d]; };
        [ax, ay] = mv602(ax, ay); [bx, by] = mv602(bx, by); [cx, cy] = mv602(cx, cy);
        let nx = (by - ay) * (cz - az) - (bz - az) * (cy - ay), nz = -((bz - az) * (cx - ax) - (bx - ax) * (cz - az)); const nl = Math.hypot(nx, nz) || 1; nx /= nl; nz /= nl;
        // two photo facades on one footprint meet at a party wall: cut the triangles there (choosing by triangle centre gave a diagonal seam)
        const V = [0, 1, 2].map(j => [(W[k + j * 4] + ox) / 10, (W[k + j * 4 + 1] + oy) / 10, W[k + j * 4 + 2] / 10, W[k + j * 4 + 3] / 10]);
        for (const q of V) { const m = mv602(q[0], q[1]); q[0] = m[0]; q[1] = m[1]; }
        if (planes.size && V.some(q => q[3] < 0)) { const pk = pkey(V[0][0], V[0][1], V[0][2], V[1][0] - V[0][0], V[1][1] - V[0][1], V[1][2] - V[0][2], V[2][0] - V[0][0], V[2][1] - V[0][1], V[2][2] - V[0][2]), pl = pk && planes.get(pk.k);
          if (pl) for (const q of V) q[3] = Math.max(0, pl.off + pl.sg * (q[0] * pl.tx + q[1] * pl.ty)); }
        const side = st.length > 1 ? (st[1].cut !== undefined ? q => q[0] * 0.9744 - q[1] * 0.225 - st[1].cut : q => q[0] - st[1].west) : null;
        const parts = [[], []];   // [east / default, west]
        if (!side) parts[0] = V; else for (let j = 0; j < 3; j++) { const p = V[j], q = V[(j + 1) % 3], dp = side(p), dq = side(q);
          parts[dp < 0 ? 1 : 0].push(p);
          if ((dp < 0) !== (dq < 0)) { const t = dp / (dp - dq), m = [0, 1, 2, 3].map(i => p[i] + (q[i] - p[i]) * t); if (p[3] < 0 || q[3] < 0) m[3] = -1; parts[0].push(m); parts[1].push(m); } }
        for (let pi = 0; pi < 2; pi++) { const P = parts[pi]; if (P.length < 3) continue;
          const S = st[pi], B = PB[S.t] || (PB[S.t] = { s: S, p: [], n: [], u: [], c: [] });
          for (let f = 1; f + 1 < P.length; f++) for (const v of [P[0], P[f], P[f + 1]]) { const [x, y, z, u] = v;
            B.p.push(x, z, -y); B.n.push(nx, 0, nz);
            if (u >= 0) B.u.push(u / (S.bw * (S.wide || 1)), Math.min(0.995, z / (S === S0 ? Ev : E))); else B.u.push(0.5, 0.997);
            const ao = 0.8 + 0.2 * Math.min(1, z / 3); B.c.push(ao, ao, ao); } }
      }
      if (bIdx === 1726 && PB.ph_1726g) {   // Antinkatu gable (SV 19.11.2026): the tiled end wall is 12.2 m wide, the scanned shell 11.1 m, which left a slot against Antinkatu 10 (1725). A thin end-wall fin continues the gable plane 1.42 m north; ph_1726g.jpg (tools/rautalanka/facades/f1726.py) is drawn 12.59 m wide for it
        const Bq = PB.ph_1726g, g0 = [17.2, 152.8], g1 = [17.52, 154.18], h0 = [17.59, 152.71], h1 = [17.91, 154.09];
        const fq = (a, b, ua, ub) => { const nx = b[1] - a[1], ny = a[0] - b[0], nl = Math.hypot(nx, ny);
          for (const [q, z, u] of [[a, 0, ua], [b, 0, ub], [b, E, ub], [a, 0, ua], [b, E, ub], [a, E, ua]]) { Bq.p.push(q[0], z, -q[1]); Bq.n.push(nx / nl, 0, -ny / nl); Bq.u.push(u / Bq.s.bw, Math.min(0.995, z / E)); const ao = 0.8 + 0.2 * Math.min(1, z / 3); Bq.c.push(ao, ao, ao); } };
        fq(g1, g0, -1.42, 0); fq(h1, g1, 6.4, 6.8); fq(h0, h1, 6.4, 7.8);
        for (const q of [g0, h0, h1, g0, h1, g1]) { Bq.p.push(q[0], E, -q[1]); Bq.n.push(0, 1, 0); Bq.u.push(0.5, 0.997); Bq.c.push(1, 1, 1); } }
      const R = L2.r;
      for (let k = 0; k < R.length; k += 3) { const q = [(R[k] + ox) / 10, (R[k + 1] + oy) / 10]; RP.push(q[0], R[k + 2] / 10 + 0.03, -q[1]); const uv = ruv(q); RU.push(uv[0], uv[1]); }
      continue;
    }
    if (L2) {   // measured massing: walls with the facade texture (or a Blender block), roofs with the aerial photo
      const ox = L2.o[0], oy = L2.o[1], W = L2.w, Bw = T || SB[sty], bw = BAYW[sty], E = Math.max(2.4, L2.e || L2.h);
      const nf = Math.max(1, lk_ && lk_.f && !house && !shed ? Math.min(lk_.f, Math.max(1, Math.floor(E / 2.5))) : house || shed || E < 7.5 ? Math.round((E - 0.4) / 2.9) : Math.round(E / FLH[sty])), fh = E / nf;   // storeys from the building register (Ryhti) when known   // whole storeys up to the measured eave
      // timber houses are mostly 1.5 storeys: one window row over a plinth on the eave sides, a second window only in the gable ends
      const wood15 = sty === 6 && house, wo = T ? 4000 : 0, gtop = new Map(), gu = new Map(), pkey = (x, y, nx, nz) => Math.round(nx * 20) + ',' + Math.round(nz * 20) + ',' + Math.round((x * nx - y * nz) * 2);
      if (wood15) for (let k = 0; k < W.length; k += 12) {
        const ax = (W[k] + ox) / 10, ay = (W[k + 1] + oy) / 10, bx = (W[k + 4] + ox) / 10, by = (W[k + 5] + oy) / 10, cx = (W[k + 8] + ox) / 10, cy = (W[k + 9] + oy) / 10, az = W[k + 2] / 10, bz = W[k + 6] / 10, cz = W[k + 10] / 10;
        let nx = (by - ay) * (cz - az) - (bz - az) * (cy - ay), nz = -((bz - az) * (cx - ax) - (bx - ax) * (cz - az)); const nl = Math.hypot(nx, nz) || 1; nx /= nl; nz /= nl;
        const key = pkey(ax, ay, nx, nz); gtop.set(key, Math.max(gtop.get(key) || 0, az, bz, cz));
        for (const j of [3, 7, 11]) { const u = W[k + j] / 10; if (u >= 0) { const r = gu.get(key) || [1e9, -1e9]; r[0] = Math.min(r[0], u); r[1] = Math.max(r[1], u); gu.set(key, r); } } }
      for (let k = 0; k < W.length; k += 12) {
        const ax = (W[k] + ox) / 10, ay = (W[k + 1] + oy) / 10, bx = (W[k + 4] + ox) / 10, by = (W[k + 5] + oy) / 10, cx = (W[k + 8] + ox) / 10, cy = (W[k + 9] + oy) / 10;
        const az = W[k + 2] / 10, bz = W[k + 6] / 10, cz = W[k + 10] / 10;
        let nx = (by - ay) * (cz - az) - (bz - az) * (cy - ay), nz = -((bz - az) * (cx - ax) - (bx - ax) * (cz - az)); const nl = Math.hypot(nx, nz) || 1; nx /= nl; nz /= nl;
        for (let j = 0; j < 3; j++) { const x = (W[k + j * 4] + ox) / 10, y = (W[k + j * 4 + 1] + oy) / 10, z = W[k + j * 4 + 2] / 10, u = W[k + j * 4 + 3] / 10;
          Bw.p.push(x, z, -y); Bw.n.push(nx, 0, nz);
          if (wood15) { const gk = pkey(ax, ay, nx, nz), gab = gtop.get(gk) > E + 0.8, gr = gu.get(gk) || [0, bw], two = gr[1] - gr[0] > 8.5;
            // gable ends: the upper floor has one window in the middle, two on a wide gable (never a full row)
            if (u >= 0) Bw.u.push(gab ? (u - (gr[0] + gr[1]) / 2) / bw + (two ? 1 : 0.5) + wo + (two ? 2200 : 2000) : u / bw + wo, (z - 0.7) / 3); else Bw.u.push(0.015 + wo, 5); } else
          if (win && u >= 0) Bw.u.push(u / bw, z / fh); else if (win && E >= 8) Bw.u.push((x * nz + y * nx) / bw, z / fh); else Bw.u.push(0.015, 0.015);   // walls the scan left without a facade coordinate still get windows on taller buildings (they were blank)
          const ao = 0.74 + 0.26 * Math.min(1, z / 3); Bw.c.push(col.r * ao, col.g * ao, col.b * ao); (Bw.c2 || (Bw.c2 = [])).push(col2.r * ao, col2.g * ao, col2.b * ao); }
      }
      const R = L2.r;
      if (T && ROOFZ.has(ZB[bIdx])) for (let k = 0; k < R.length; k += 3) { T.p.push((R[k] + ox) / 10, R[k + 2] / 10 + 0.03, -(R[k + 1] + oy) / 10); T.n.push(0, 1, 0); T.u.push(0.015, 0.015); T.c.push(0.3, 0.31, 0.33); }
      else for (let k = 0; k < R.length; k += 3) { const q = [(R[k] + ox) / 10, (R[k + 1] + oy) / 10]; RP.push(q[0], R[k + 2] / 10 + 0.03, -q[1]); const uv = ruv(q); RU.push(uv[0], uv[1]); }
      continue;
    }
    for (let i = 0; i < pts.length; i++) {
      const a = pts[i], c2 = pts[(i + 1) % pts.length];
      const dx = c2[0] - a[0], dy = c2[1] - a[1], len = Math.hypot(dx, dy); if (len < 0.05) continue;
      const nx = dy / len, nz = dx / len;
      const n = Math.max(1, Math.round(len / 3.6)), fl = Math.max(1, Math.round(h / 3.2));
      const u1 = win ? n : 0.02, v1 = win ? fl : 0.02, u0 = win ? 0 : 0.01, v0 = win ? 0 : 0.01;
      const quad = (B, y0, y1, uu0, uu1, vv0, vv1, aoB) => { B.p.push(a[0], y0, -a[1], c2[0], y0, -c2[1], c2[0], y1, -c2[1], a[0], y0, -a[1], c2[0], y1, -c2[1], a[0], y1, -a[1]);
        B.u.push(uu0, vv0, uu1, vv0, uu1, vv1, uu0, vv0, uu1, vv1, uu0, vv1);
        for (let k = 0; k < 6; k++) { B.n.push(nx, 0, nz); const ao = (k === 0 || k === 1 || k === 3) ? aoB : 1; B.c.push(col.r * ao, col.g * ao, col.b * ao); (B.c2 || (B.c2 = [])).push(col2.r * ao, col2.g * ao, col2.b * ao); } };   // darker towards the street
      if (T) { if (CZ.zones[KN[ZB[bIdx]]]) quad(KWP[ZB[bIdx]], 0, h, 0.01, 0.02, 0.01, 0.02, 0.74); else quad(T, 0, h, u0, u1, v0, v1, 0.74); continue; }   // streamed blocks: plain stand-in
      if (!win || len < 2.2) { quad(SB[sty], 0, h, 0.01, 0.02, 0.01, 0.02, 0.74); continue; }
      const gf = shops && len >= 7 ? 3.8 : 0;
      if (gf) quad(SB[4], 0, gf, 0, Math.max(1, Math.round(len / BAYW[4])), 0, 1, 0.8);
      const nb = Math.max(1, Math.round(len / BAYW[sty])), nf = Math.max(1, lk_ && lk_.f ? lk_.f - (gf ? 1 : 0) : Math.round((h - gf) / FLH[sty]));
      if (sty === 6) quad(SB[6], 0, h, 0, nb, -0.7 / 3, (h - 0.7) / 3, 0.74); else quad(SB[sty], gf, h, 0, nb, 0, nf, gf ? 0.9 : 0.74);
    }
    const tris = THREE.ShapeUtils.triangulateShape(pts.map(q => new THREE.Vector2(q[0], q[1])), []);
    if (OWNROOF.has(b.w) && T) { const g = b.w === SKOOLI ? 0.2 : 0.56; if (b.w !== SKOOLI) for (const q of pts) karhuPts.push(q); for (const t of tris) for (const k of t) { const q = pts[k]; tp.push(q[0], h, -q[1]); tu.push(0.02, 0.02); tn.push(0, 1, 0); tc.push(g, g, g + 0.02); } }   // new restaurant: the aerial image predates it, so no photo roof
    else if (!ZROOF.has(bIdx) && !(ZB[bIdx] !== undefined && ROOFZ.has(ZB[bIdx]))) {   // blocks with a Blender-made roof skip the photo roof (Kivi-Pori blocks too: at the wrong city.js height it showed inside the Valtakatu 26 recess, 17.11.2026)
      let gable = null;
      if (house && pts.length <= 14) { const o = obbOf(pts); let ar = 0; for (let i = 0; i < pts.length; i++) { const a = pts[i], c2 = pts[(i + 1) % pts.length]; ar += a[0] * c2[1] - c2[0] * a[1]; }
        if (o && Math.abs(ar) / 2 > 0.7 * 4 * o.a * o.b && o.b > 1.8) gable = o; }
      if (gable) {                                    // pitched roof along the long side, textured from the aerial image; gable ends in the wall colour
        const o = gable, ov = 0.45, rise = Math.min(4.6, o.b * 0.66), vx = -o.uy, vy = o.ux, P = (su, sv, e) => [o.cx + o.ux * su * (o.a + e) + vx * sv * (o.b + e), o.cy + o.uy * su * (o.a + e) + vy * sv * (o.b + e)];
        const A = P(-1, -1, ov), B = P(1, -1, ov), C = P(1, 1, ov), D = P(-1, 1, ov), R0 = P(-1, 0, ov), R1 = P(1, 0, ov), top = h + rise;
        for (const [q, y] of [[A, h], [B, h], [R1, top], [A, h], [R1, top], [R0, top], [C, h], [D, h], [R0, top], [C, h], [R0, top], [R1, top]]) { RP.push(q[0], y - (y === h ? 0.25 : 0), -q[1]); const uv = ruv(q); RU.push(uv[0], uv[1]); }
        const W = T ? (CZ.zones[KN[ZB[bIdx]]] ? KWP[ZB[bIdx]] : T) : SB[6];   // a house in a streamed block: the stand-in gable goes with the block's stand-in walls
        for (const su of [-1, 1]) { const g0 = P(su, -1, 0), g1 = P(su, 1, 0), g2 = P(su, 0, 0);
          for (const tri3 of [[g0, g1, g2], [g1, g0, g2]]) tri3.forEach((q, k) => { W.p.push(q[0], k === 2 ? top - 0.15 : h, -q[1]); W.u.push(0.015, 0.015); W.n.push(o.ux * su, 0, -o.uy * su); W.c.push(col.r, col.g, col.b); }); }
        rec.h = h + rise * 0.7;
      } else for (const t of tris) for (const k of t) { const q = pts[k]; RP.push(q[0], h, -q[1]); const uv = ruv(q); RU.push(uv[0], uv[1]); }
    }
  }
  const wg = new THREE.BufferGeometry();
  wg.setAttribute('position', new THREE.Float32BufferAttribute(wp, 3)); wg.setAttribute('normal', new THREE.Float32BufferAttribute(wn, 3));
  wg.setAttribute('uv', new THREE.Float32BufferAttribute(wu, 2)); wg.setAttribute('color', new THREE.Float32BufferAttribute(wc, 3));
  // Karhukortteli: the aerial image still shows the demolished brewery here, so cover the block with plain paving
  if (karhuPts.length > 2) {
    const P = karhuPts.slice().sort((a, b) => a[0] - b[0] || a[1] - b[1]), cr = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]), lo = [], up = [];
    for (const q of P) { while (lo.length > 1 && cr(lo[lo.length - 2], lo[lo.length - 1], q) <= 0) lo.pop(); lo.push(q); }
    for (const q of P.slice().reverse()) { while (up.length > 1 && cr(up[up.length - 2], up[up.length - 1], q) <= 0) up.pop(); up.push(q); }
    const hull = lo.slice(0, -1).concat(up.slice(0, -1)), cx = hull.reduce((a, q) => a + q[0], 0) / hull.length, cy = hull.reduce((a, q) => a + q[1], 0) / hull.length, pos = [];
    const ex = hull.map(q => { const d = Math.hypot(q[0] - cx, q[1] - cy) || 1; return [q[0] + (q[0] - cx) / d * 5, q[1] + (q[1] - cy) / d * 5]; });
    for (let i = 1; i < ex.length - 1; i++) pos.push(ex[0][0], 0.12, -ex[0][1], ex[i][0], 0.12, -ex[i][1], ex[i + 1][0], 0.12, -ex[i + 1][1]);
    const pg = new THREE.BufferGeometry(); pg.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    // the shared courtyard of the new Karhukortteli (the aerial image still shows the brewery): pavers, lawn and planting beds
    const cv = document.createElement('canvas'); cv.width = cv.height = 512; const x = cv.getContext('2d');
    x.fillStyle = '#b3aea4'; x.fillRect(0, 0, 512, 512);
    for (let i = 0; i < 2600; i++) { x.fillStyle = `rgba(${90 + Math.random() * 60 | 0},${88 + Math.random() * 55 | 0},${80 + Math.random() * 50 | 0},0.12)`; x.fillRect(Math.random() * 512, Math.random() * 512, 6, 3); }
    x.fillStyle = '#6f8f4a'; x.beginPath(); x.roundRect(150, 150, 212, 212, 40); x.fill();
    for (let i = 0; i < 900; i++) { x.fillStyle = `rgba(${60 + Math.random() * 40 | 0},${110 + Math.random() * 40 | 0},${40 + Math.random() * 30 | 0},0.35)`; x.fillRect(150 + Math.random() * 212, 150 + Math.random() * 212, 3, 3); }
    x.strokeStyle = '#c9c3b6'; x.lineWidth = 14; x.beginPath(); x.moveTo(256, 150); x.lineTo(256, 362); x.moveTo(150, 256); x.lineTo(362, 256); x.stroke();
    for (const [a, b] of [[110, 110], [400, 120], [120, 400], [395, 395]]) { x.fillStyle = '#3f5f34'; x.beginPath(); x.arc(a, b, 26, 0, 7); x.fill(); }
    const ct = new THREE.CanvasTexture(cv); ct.colorSpace = THREE.SRGBColorSpace;
    const uv = []; for (let k = 0; k < pos.length; k += 3) uv.push((pos[k] - cx) / 90 + 0.5, (-pos[k + 2] - cy) / 90 + 0.5);
    pg.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
    scene.add(new THREE.Mesh(pg, new THREE.MeshBasicMaterial({ map: ct, side: THREE.DoubleSide })));
  }
  const wallMat = new THREE.MeshLambertMaterial({ map: facade, vertexColors: true }), wallMat2 = new THREE.MeshLambertMaterial({ vertexColors: true, side: THREE.DoubleSide });   // plain stand-in walls of the streamed city blocks until their Blender block arrives (the facade texture does not map onto these)
  wallMat.onBeforeCompile = sh => { sh.fragmentShader = sh.fragmentShader.replace('#include <map_fragment>',   // stand-in timber houses: plinth, one window row, a second only in the gable ends
    'vec4 sampledDiffuseColor = texture2D( map, vMapUv ); if ( vMapUv.x > 3000.0 ) { if ( vMapUv.y < 0.0 ) sampledDiffuseColor = vec4( vec3( 0.5 ), 1.0 ); else { float gx = vMapUv.x - ( vMapUv.x > 6100.0 ? 6200.0 : 6000.0 ), gn = vMapUv.x > 6100.0 ? 2.0 : 1.0; if ( vMapUv.y > 1.0 && ! ( vMapUv.x > 5000.0 && vMapUv.y < 2.0 && gx >= 0.0 && gx < gn ) ) sampledDiffuseColor = vec4( 1.0 ); } } diffuseColor *= sampledDiffuseColor;'); };
  scene.add(new THREE.Mesh(wg, wallMat));
  for (const [b, lk] of liftParts) {   // a slab or glazed tube between lift and the top, posts down to the ground for canopies
    const pts = []; for (let k = 0; k < b.p.length; k += 2) pts.push(new THREE.Vector2(b.p[k] / 10, b.p[k + 1] / 10));
    const bridge = lk.lift >= 4.5, top = bridge ? Math.max(lk.lift + 3.2, b.h) : Math.max(lk.lift + 0.4, b.h), sh = new THREE.Shape(pts);
    const g = new THREE.ExtrudeGeometry(sh, { depth: bridge ? top - lk.lift : 0.45, bevelEnabled: false }); g.rotateX(-Math.PI / 2);
    const m = new THREE.Mesh(g, new THREE.MeshLambertMaterial({ color: new THREE.Color(lk.w || '#c9ccd0') })); m.position.y = bridge ? lk.lift : top - 0.45; scene.add(m);
    if (!bridge) { const pm = new THREE.MeshLambertMaterial({ color: 0x6b6f73 }); const pg = new THREE.CylinderGeometry(0.12, 0.12, top - 0.45, 6);
      for (let k = 0; k < pts.length; k++) { const q = pts[k], pq = pts[(k + 1) % pts.length]; if (q.distanceTo(pq) < 1.5) continue; const c = new THREE.Mesh(pg, pm); c.position.set(q.x, (top - 0.45) / 2, -q.y); scene.add(c); } }
  }
  const tl = new THREE.TextureLoader();
  STY.forEach((st, si) => { const B = SB[si]; if (!B.p.length) return;
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(B.p, 3)); g.setAttribute('normal', new THREE.Float32BufferAttribute(B.n, 3));
    g.setAttribute('uv', new THREE.Float32BufferAttribute(B.u, 2)); g.setAttribute('color', new THREE.Float32BufferAttribute(B.c, 3));
    const t = tl.load(`./f_${st}.png`); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
    if (B.c2 && B.c2.length === B.c.length) g.setAttribute('color2', new THREE.Float32BufferAttribute(B.c2, 3));
    const m = new THREE.MeshLambertMaterial({ map: t, vertexColors: true });
    m.onBeforeCompile = sh => { sh.fragmentShader = sh.fragmentShader.replace('#include <color_fragment>', '').replace('#include <map_fragment>',
      si === 6 ? 'vec4 fT = texture2D( map, vMapUv ); float tw = clamp( ( fT.a - 0.5 ) * 2.0, 0.0, 1.0 ); bool gab = vMapUv.x > 1000.0; float gx = vMapUv.x - ( vMapUv.x > 2100.0 ? 2200.0 : 2000.0 ), gn = vMapUv.x > 2100.0 ? 2.0 : 1.0; if ( vMapUv.y < 0.0 ) diffuseColor.rgb *= vec3( 0.42, 0.41, 0.39 ); else if ( vMapUv.y > 1.0 && ! ( gab && vMapUv.y < 2.0 && gx >= 0.0 && gx < gn ) ) diffuseColor.rgb *= vColor * 0.96; else diffuseColor.rgb *= mix( fT.rgb, fT.rgb * vColor, tw );'
      : 'vec4 fT = texture2D( map, vMapUv ); vec3 wC = vColor; float tw = clamp( ( fT.a - 0.5 ) * 2.0, 0.0, 1.0 ); float isG = ( 1.0 - tw ) * smoothstep( 0.42, 0.28, dot( fT.rgb, vec3( 0.3, 0.59, 0.11 ) ) ); vec3 glz = mix( fT.rgb, mix( fT.rgb, vec3( 0.52, 0.56, 0.6 ), 0.45 ) * mix( vec3( 1.0 ), wC, 0.35 ), isG ); diffuseColor.rgb *= mix( glz, fT.rgb * wC, tw );'); };   // windows lighter and tinted by the wall: from the air the facade must average to the wall colour of the photos, not to blue-grey
    if (si !== 6 && g.attributes.color2) { const ob0 = m.onBeforeCompile; m.onBeforeCompile = sh => { ob0(sh);
      sh.vertexShader = 'attribute vec3 color2; varying vec3 vC2;\n' + sh.vertexShader.replace('#include <begin_vertex>', '#include <begin_vertex>\nvC2 = color2;');
      sh.fragmentShader = 'varying vec3 vC2;\n' + sh.fragmentShader.replace('vec3 wC = vColor;', 'vec3 wC = mod( floor( vMapUv.x ), 4.0 ) < 1.5 ? vC2 : vColor;'); }; }
    { const dt = tl.load(si === 6 ? './det_wood.jpg' : si === 5 ? './det_brick.jpg' : './det_plaster.jpg'); dt.wrapS = dt.wrapT = THREE.RepeatWrapping; dt.anisotropy = 4;   // surface grain on the flat colours: render or boards (CC0, Poly Haven)
      const ob = m.onBeforeCompile, sc = si === 6 ? [BAYW[si] / 2.4, 3 / 2.4] : [BAYW[si] / 2.2, FLH[si] / 2.2], amp = si === 6 ? 0.55 : si === 5 ? 1.5 : 0.4;
      m.onBeforeCompile = sh => { ob(sh); sh.uniforms.detMap = { value: dt };
        sh.fragmentShader = 'uniform sampler2D detMap;\n' + sh.fragmentShader.replace('#include <alphamap_fragment>', `diffuseColor.rgb *= 1.0 + ( texture2D( detMap, fract( vMapUv ) * vec2( ${sc[0].toFixed(3)}, ${sc[1].toFixed(3)} ) ).r - 0.5 ) * ${amp.toFixed(2)};\n#include <alphamap_fragment>`); }; }
    { const obY = m.onBeforeCompile; m.onBeforeCompile = sh => { obY(sh); sh.uniforms.winGlow = WINGLOW;      // 21.11.2026: ikkunoiden yövalo (aika/aika.js); ruutu = julkisivun jako (väli × kerros), lasi = tumma sinertävä tekseli
        sh.vertexShader = 'varying vec3 vYW;\n' + sh.vertexShader.replace('#include <begin_vertex>', '#include <begin_vertex>\nvYW = ( modelMatrix * vec4( position, 1.0 ) ).xyz;');
        sh.fragmentShader = 'uniform vec4 winGlow;\nvarying vec3 vYW;\n' + YOHASH + sh.fragmentShader.replace('#include <tonemapping_fragment>',
          '{ float yS = dot( floor( vYW.xz / 30.0 ), vec2( 7.1, 3.3 ) ); float yG = step( dot( fT.rgb, vec3( 0.3, 0.59, 0.11 ) ), 0.34 ) * step( fT.r * 1.04, fT.b ) * step( 0.0, vMapUv.y ) * step( vMapUv.x, 900.0 );\n' +
          '  gl_FragColor.rgb += winGlow.rgb * yG * step( yoH( floor( vMapUv ), yS ), winGlow.a ) * ( 0.55 + 0.45 * yoH( floor( vMapUv ), yS + 3.1 ) ); }\n#include <tonemapping_fragment>'); }; }
    m.customProgramCacheKey = () => 'wall' + si + (g.attributes.color2 ? 'c2' : '') + 'dy';   // every style has its own shader: identical onBeforeCompile source made three.js reuse one style's program for another
    scene.add(new THREE.Mesh(g, m)); });
  Object.values(PB).forEach(B => {
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(B.p, 3)); g.setAttribute('normal', new THREE.Float32BufferAttribute(B.n, 3));
    g.setAttribute('uv', new THREE.Float32BufferAttribute(B.u, 2)); g.setAttribute('color', new THREE.Float32BufferAttribute(B.c, 3));
    const setup = t => { t.wrapS = THREE.RepeatWrapping; t.wrapT = THREE.ClampToEdgeWrapping; t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t; };
    const pm = new THREE.MeshLambertMaterial({ vertexColors: true });
    if (B.s.rows > B.s.n) {   // extended strip: ground floor, the photo's storeys, repeats of its second-highest storey, its top storey last
      const img = new Image();
      img.onload = () => { const cv = document.createElement('canvas'), w = img.width, h = img.height, gp = Math.round(B.s.g * h), rp = (h - gp) / B.s.n, R = B.s.rows, Wd = B.s.wide || 1; cv.width = w * Wd; cv.height = Math.round(gp + R * rp); const c = cv.getContext('2d');
        for (let q = 0; q < Wd; q++) { c.drawImage(img, 0, h - gp, w, gp, q * w, cv.height - gp, w, gp);
          for (let k = 0; k < R; k++) { const src = k < B.s.n - 1 ? k : k === R - 1 ? B.s.n - 1 : B.s.n - 2; c.drawImage(img, 0, h - gp - (src + 1) * rp, w, rp, q * w, cv.height - gp - (k + 1) * rp, w, rp + 0.5); } }
        if (B.s.shop) {   // shop windows: the photo's ground floor has a pier every 0.75 m; redraw it as wide sheets of glass (its own pier and glass colours, column by column) with a pier between them
          const y0 = h - gp, Y0 = cv.height - gp, uw = cv.width / B.s.shop, pw = Math.max(2, Math.round(0.34 / (B.s.bw * Wd) * cv.width));
          c.drawImage(img, 1, y0, 1, gp, 0, Y0, cv.width, gp);                                   // pier / fascia column across the whole width
          for (let q = 0; q < B.s.shop; q++) c.drawImage(img, Math.round(w * 0.26), y0, 1, gp, q * uw + pw / 2, Y0, uw - pw, gp); }   // glass column stretched over each opening
        pm.map = setup(new THREE.CanvasTexture(cv)); pm.needsUpdate = true; };
      img.src = `./${B.s.t}.jpg`;
    } else pm.map = setup(tl.load(`./${B.s.t}.jpg`));
    scene.add(new THREE.Mesh(g, pm)); });
  const kwMesh = (k, mat) => { if (!k.p.length) return null; const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(k.p, 3)); g.setAttribute('normal', new THREE.Float32BufferAttribute(k.n, 3));
    g.setAttribute('uv', new THREE.Float32BufferAttribute(k.u, 2)); g.setAttribute('color', new THREE.Float32BufferAttribute(k.c, 3)); const me = new THREE.Mesh(g, mat); scene.add(me); return me; };
  KW.forEach((k, ci) => { if (!k.p.length && !KWP[ci].p.length) return;
    const me0 = kwMesh(k, wallMat), me1 = kwMesh(KWP[ci], wallMat2), me = new THREE.Group(); for (const q of [me0, me1]) if (q) { scene.remove(q); me.add(q); } scene.add(me);
    if (CZ.zones[KN[ci]]) { const z = CZ.zones[KN[ci]]; STREAM.push({ name: KN[ci], me, x: z.x, y: z.y, st: 0, gr: null }); return; }
    loadModel('bl_' + KN[ci], (root, K) => { root.traverse(q => { if (q.isMesh) { const map = q.material.map; if (map) { map.anisotropy = 8; TEXLOD.add(map, K.x, K.y); } q.material = yovalo(glassify(new THREE.MeshBasicMaterial({ map }))); } });
      const gr = new THREE.Group(); gr.position.set(K.x, 0, -K.y); gr.add(root); if (K.shells) liftBlock(gr, K.shells); scene.add(gr); scene.remove(me); (window.__bl = window.__bl || []).push(KN[ci]); });
  });
  // roofs are cut along the 512 m aerial tiles: each piece shows the sharp 0.25 m tile once it is loaded, the coarse image until then
  for (const [P, U, fb] of [[rp, ru, roofMat], [rp2, ru2, roofMat2]]) {
    const parts = new Map();
    for (let k = 0; k < P.length; k += 9) {
      const cx = (P[k] + P[k + 3] + P[k + 6]) / 3, cy = -(P[k + 2] + P[k + 5] + P[k + 8]) / 3;
      const i = Math.floor((cx - HR.X0) / HR.S), j = Math.floor((cy - HR.Y0) / HR.S), key = i + '_' + j;
      let e = parts.get(key); if (!e) parts.set(key, e = { i, j, p: [], u: [], t: [] });
      for (let v = 0; v < 3; v++) { const x = P[k + v * 3], y = -P[k + v * 3 + 2]; e.p.push(P[k + v * 3], P[k + v * 3 + 1], P[k + v * 3 + 2]);
        e.u.push(U[(k / 3 + v) * 2], U[(k / 3 + v) * 2 + 1]); e.t.push((x - (HR.X0 + i * HR.S)) / HR.S, (y - (HR.Y0 + j * HR.S)) / HR.S); }
    }
    for (const [key, e] of parts) {
      const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(e.p, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(e.u, 2));
      g.setAttribute('uv1', new THREE.Float32BufferAttribute(e.t, 2));
      const me = new THREE.Mesh(g, fb); me.userData.fb = fb; scene.add(me);
      if (!ROOFT.has(key)) ROOFT.set(key, []); ROOFT.get(key).push(me);
    }
  }
}

