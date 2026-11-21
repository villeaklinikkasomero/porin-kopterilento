// ---------- landmarks ----------
const find = n => CITY.named.find(d => d.n === n) || CITY.places.find(d => d.n === n);
const KIRJURI = { n: 'Kirjurinluoto', x: -755, y: 690, h: 0 };
// landmark pool: every day a new route of 10 is drawn from it (same for everyone, Finnish date as the seed)
const POOL = ['Porin kauppahalli', 'Promenadikeskus', 'BePop', 'Porin vesitorni', 'Porin pääkirjasto', 'Porin Teatteri', 'Satakunnan Museo', 'Kirjurinluoto',
  'Taavi-silta', 'Raatihuone', 'Porinsilta', 'Kauppakeskus Puuvilla', 'Linnansilta', 'Keski-Porin kirkko']
  .map(n => n === 'Kirjurinluoto' ? KIRJURI : find(n)).filter(Boolean).map(d => ({ n: d.n, x: d.x, y: d.y, h: d.h || 0 }))
  .concat([['Porin rautatieasema', -443, -956, 12], ['SAMK-kampus', -260, -997, 18], ['Isomäki Areena', -1615, -1392, 14], ['Porin stadion', -1187, -1058, 0],
    ['Juseliuksen mausoleumi', -1946, 198, 10], ['Aittaluodon voimalaitos', 1177, 322, 70], ['Sampo-Rosenlew', 570, 827, 8], ['Keskustan uimahalli', 568, -660, 12],
    ['Urheilutalo', 676, -806, 10], ['IsoKarhu', 121, -179, 12], ['Cygnaeuksen koulu', -321, -491, 23], ['Porin oikeustalo', 290, 189, 16], ['Barco-laiva', -236, 510, 6],
    ['Herralahden kenttä', 667, 99, 0], ['Antinpuisto', 832, -446, 0], ['Länsipuisto', -414, 31, 0], ['Pormestarinsilta', -462, 1196, 4], ['Keskuspuisto', -26, -817, 0],
    ['Porin taidemuseo', -95, 463, 8], ['Vanha hautausmaa', -921, -73, 0], ['Sofianpuisto', 50, 972, 0], ['Karhuhalli', -1669, -1040, 9]].map(([n, x, y, h]) => ({ n, x, y, h })));
const DAY = (() => { const p = Object.fromEntries(new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Helsinki', year: 'numeric', month: '2-digit', day: '2-digit' }).formatToParts(new Date()).map(q => [q.type, q.value]));
  return { key: p.year + p.month + p.day, label: +p.day + '.' + +p.month + '.' + p.year }; })();
const TOUR = (() => {
  let sd = +DAY.key * 2654435761 >>> 0; const rnd = () => { sd = (sd + 0x6D2B79F5) >>> 0; let t = sd; t = Math.imul(t ^ t >>> 15, t | 1); t ^= t + Math.imul(t ^ t >>> 7, t | 61); return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  const bag = POOL.slice(); for (let i = bag.length - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [bag[i], bag[j]] = [bag[j], bag[i]]; }
  const pick = []; for (const p of bag) { if (pick.length === 10) break; if (pick.every(q => Math.hypot(q.x - p.x, q.y - p.y) > 160)) pick.push(p); }
  // flying order: nearest neighbour from the market square, then 2-opt on the closed loop back to it
  const H = { x: 70, y: 45 }, d = (a, b) => Math.hypot(a.x - b.x, a.y - b.y); let cur = H; const ord = [], left = pick.slice();
  while (left.length) { let bi = 0; left.forEach((p, i) => { if (d(cur, p) < d(cur, left[bi])) bi = i; }); cur = left.splice(bi, 1)[0]; ord.push(cur); }
  const len = r => { let s = d(H, r[0]) + d(r[r.length - 1], H); for (let i = 1; i < r.length; i++) s += d(r[i - 1], r[i]); return s; };
  let r = ord, imp = true; while (imp) { imp = false; for (let i = 0; i < r.length - 1; i++) for (let j = i + 1; j < r.length; j++) { const c = r.slice(0, i).concat(r.slice(i, j + 1).reverse(), r.slice(j + 1)); if (len(c) < len(r) - 0.01) { r = c; imp = true; } } }
  return r; })();
const TORI = find('Kauppatori') || { n: 'Kauppatori', x: 64, y: 65 };
const HOME = { x: -862, y: 1222 };   // 20.11.2026 (omistaja): lähtöpaikka Kirjurinluodon areenan asfaltilla (Pori Jazzin areenan luoteiskulma); ennen Kauppatori { x: 70, y: 45 }
{
  const seen = new Set(); var sprites = [];
  const labels = [...TOUR, { n: 'Kauppatori', x: TORI.x, y: TORI.y, h: 0 }, ...CITY.named.filter(d => d.a > 900), ...CITY.places.filter(p => /puisto|aukio|tori/i.test(p.n))];
  for (const d of labels) {
    if (seen.has(d.n) || labels.indexOf(d) > 60) continue; seen.add(d.n);
    const big = TOUR.includes(d) || d.n === 'Kauppatori';
    const t = textCanvas(d.n, { size: 40, color: big ? '#16110a' : '#f4f1e8', bg: big ? 'rgba(255,201,40,.95)' : 'rgba(14,22,30,.72)', pad: 18 });
    const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: t.tex, transparent: true, depthWrite: false, fog: false }));
    const hh = big ? 9 : 6.5; s.scale.set(hh * t.aspect, hh, 1); s.position.set(d.x, TZs(d.x, d.y) + Math.min((d.h || 0), 70) + (big ? 16 : 11), -d.y); s.renderOrder = 3; s.userData.big = big; sprites.push(s); scene.add(s);
  }
}

// helipad on the market square
{
  const c = document.createElement('canvas'); c.width = c.height = 256; const x = c.getContext('2d');
  x.fillStyle = 'rgba(30,40,50,.55)'; x.beginPath(); x.arc(128, 128, 122, 0, 7); x.fill();
  x.strokeStyle = '#ffc928'; x.lineWidth = 10; x.beginPath(); x.arc(128, 128, 112, 0, 7); x.stroke();
  x.fillStyle = '#fff'; x.font = '700 150px ui-sans-serif, system-ui, Arial'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText('H', 128, 136);
  const g = new THREE.PlaneGeometry(17, 17); g.rotateX(-Math.PI / 2);
  const m = new THREE.Mesh(g, new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(c), transparent: true, depthWrite: false })); m.material.polygonOffset = true; m.material.polygonOffsetFactor = -8; m.material.polygonOffsetUnits = -8; m.position.set(HOME.x, groundTop(HOME.x, HOME.y) + ROAD.pave + 0.03, -HOME.y); m.renderOrder = 1; scene.add(noT(m));
}

// checkpoint beacon
const beacon = new THREE.Group();
{
  const beam = new THREE.Mesh(new THREE.CylinderGeometry(9, 9, 420, 20, 1, true), new THREE.MeshBasicMaterial({ color: 0xffc928, transparent: true, opacity: 0.2, side: THREE.DoubleSide, depthWrite: false, blending: THREE.AdditiveBlending, fog: false }));
  beam.position.y = 210; beacon.add(beam);
  const ring = new THREE.Mesh(new THREE.TorusGeometry(26, 1.3, 8, 40), new THREE.MeshBasicMaterial({ color: 0xffc928, fog: false })); ring.rotation.x = Math.PI / 2; ring.name = 'ring'; beacon.add(ring);
  const ring2 = new THREE.Mesh(new THREE.TorusGeometry(26, 0.6, 6, 40), new THREE.MeshBasicMaterial({ color: 0xffffff, fog: false, transparent: true, opacity: 0.7 })); ring2.rotation.x = Math.PI / 2; ring2.name = 'ring2'; beacon.add(ring2);
  beacon.renderOrder = 4; scene.add(beacon);
}

