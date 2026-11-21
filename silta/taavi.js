// Taavi-silta: Kirjurinluodon ja Etelärannan välinen kelluva kävelysilta (ponttonisilta), rakennettu uudelleen 21.11.2026.
// Omistaja: "Kirjurista ei pääse Taavi-sillalle. Silta pitää rakentaa kokonaan uudelleen … Silta on 137 metriä pitkä ja neljä metriä leveä."
// Kuvien mukaan (omistajan valokuvat): betoniponttonit vedenpinnassa, puukansi pitkittäisin lankuin, galvanoidut kaiteet ristikkokuviolla (X 2 m välein),
// pallovalaisimet tolpissa, ohjauspaalut ponttonien vieressä, punaiset poijut. Kirjurinluodon päässä betonimaatuki ja luiska rannan tasolta ponttonille,
// Etelärannan päässä leveämpi ponttonilaituri ja teräsristikkoinen portaikkosilta laiturilta rannan tasolle.
// Akseli s (m) Kirjurinluodon rannasta (TAAVI.a) Etelärannalle; l (m) sivulle (+ = itään). Kävelypinta window.__taaviZ(x, y, ref) (082 carGround),
// kaiteet kiinteitä: window.__siltaKaide ketjutettu (121 wallIn, 090 carBlocked). Vanha silta poistettu RIV.br/CITY.br-listoista (010).
import * as THREE from '../three.module.min.js';
import { mergeGeometries } from '../BufferGeometryUtils.js';

export default function kaynnista(P) {
  const { scene, TZg, WL, TAAVI, noT } = P;
  const ax = TAAVI.a[0], ay = TAAVI.a[1], L0 = Math.hypot(TAAVI.b[0] - ax, TAAVI.b[1] - ay);
  const u = [(TAAVI.b[0] - ax) / L0, (TAAVI.b[1] - ay) / L0], n = [-u[1], u[0]];
  const PT = (s, l) => [ax + u[0] * s + n[0] * l, ay + u[1] * s + n[1] * l];
  const SL = (x, y) => { const dx = x - ax, dy = y - ay; return [dx * u[0] + dy * u[1], dx * n[0] + dy * n[1]]; };
  const W3 = (s, l, z) => { const [x, y] = PT(s, l); return new THREE.Vector3(x, z, -y); };

  // ---- korkeusprofiili ----
  const maaZ = (s) => { let m = -1e9; for (const l of [-1.5, 0, 1.5]) m = Math.max(m, TZg(...PT(s, l))); return m; };
  const DECK = WL + 0.58;                                    // ponttonien kansi ~0,6 m vedenpinnasta
  const S_K0 = -6, S_K1 = -2, S_P0 = 12, S_L0 = 129, S_L1 = 134, S_E1 = 143, S_E2 = 145.5;
  const zK = Math.max(DECK + 0.3, maaZ(S_K0 - 0.5) + 0.04);   // Kirjurinluodon maatuki rannan tasolla
  const zE = Math.max(DECK + 0.3, maaZ(S_E2 + 0.5) + 0.04);   // Etelärannan pää rannan tasolla
  const ss = t => t * t * (3 - 2 * t);
  const zf = s => s < S_K1 ? zK : s < S_P0 ? zK + (DECK - zK) * (s - S_K1) / (S_P0 - S_K1) : s < S_L1 ? DECK : s < S_E1 ? DECK + (zE - DECK) * (s - S_L1) / (S_E1 - S_L1) : zE;
  const hwf = s => (s >= S_L0 && s <= S_L1) ? 3.0 : (s > S_L1 && s < S_E1) ? 1.5 : 2.0;   // puolileveys (kansi): ponttoni 4 m, laituri 6 m, portaikkosilta 3 m
  const kaideOn = s => s > S_K1 - 0.01 && s < S_E1 + 0.01;

  // ---- kävely ja kaiteet ----
  window.__taaviZ = (x, y, ref) => { const [s, l] = SL(x, y); if (s < S_K0 || s > S_E2) return null; if (Math.abs(l) > hwf(s) + 0.05) return null;
    const z = zf(s); if (ref !== undefined && ref !== null && ref < z - 2.5) return null; return z + 0.02; };
  const prevK = window.__siltaKaide;
  window.__siltaKaide = (x, y, z) => { let d = prevK ? prevK(x, y, z) : 0; const [s, l] = SL(x, y);
    if (s > S_K1 - 0.5 && s < S_E1 + 0.5 && Math.abs(z - zf(Math.max(S_K1, Math.min(S_E1, s)))) < 2.2) {
      const sc = Math.max(S_K1, Math.min(S_E1, s)), inner = hwf(sc) - 0.3, al = Math.abs(l);
      if (kaideOn(s) && al > inner && al < hwf(sc) + 0.8) d = Math.max(d, al - inner); }
    return d; };

  // ---- materiaalit ----
  const tl = new THREE.TextureLoader(); const tex = (f, srgb) => { const t = tl.load(f); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; if (srgb) t.colorSpace = THREE.SRGBColorSpace; return t; };
  const puu = new THREE.MeshStandardMaterial({ map: tex('./maa/tex/puu_a.jpg', true), normalMap: tex('./maa/tex/puu_n_m.jpg'), roughness: 0.85, metalness: 0, color: 0xd2cec6 });
  puu.onBeforeCompile = sh => { sh.fragmentShader = sh.fragmentShader.replace('#include <map_fragment>', '#include <map_fragment>\n  { float lu = dot(diffuseColor.rgb, vec3(0.3, 0.55, 0.15)); diffuseColor.rgb = mix(vec3(lu) * vec3(1.0, 0.98, 0.94), diffuseColor.rgb, 0.3); }'); };   // harmaantunut puu (kuvissa)
  const betoni = new THREE.MeshStandardMaterial({ map: tex('./silta/betoni_albedo.jpg', true), normalMap: tex('./silta/betoni_normal.jpg'), roughness: 0.92, color: 0xa8a6a0 });
  const teras = new THREE.MeshStandardMaterial({ color: 0xc9cdd0, roughness: 0.5, metalness: 0.25 });   // galvanoitu (ilman ympäristökarttaa metalli tummuu ruskeaksi)
  const tumma = new THREE.MeshStandardMaterial({ color: 0x5d6163, roughness: 0.6, metalness: 0.5 });
  const pallo = new THREE.MeshStandardMaterial({ color: 0xfff6e0, emissive: 0xffe6b0, emissiveIntensity: 0.35, roughness: 0.3 });
  const poiju = new THREE.MeshStandardMaterial({ color: 0xd8202a, roughness: 0.5 });
  const G = new Map(); const lisaa = (m, g) => { if (!G.has(m)) G.set(m, []); G.get(m).push(g); };

  // laatikko kahden pisteen välille (putket, palkit): a, b Vector3, paksuus w × h
  const UP = new THREE.Vector3(0, 1, 0);
  const sauva = (m, a, b, w = 0.05, h = w) => { const d = new THREE.Vector3().subVectors(b, a), L = d.length(); if (L < 1e-4) return;
    const g = new THREE.BoxGeometry(w, h, L); const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 0, 1), d.clone().normalize());
    g.applyQuaternion(q); g.translate((a.x + b.x) / 2, (a.y + b.y) / 2, (a.z + b.z) / 2); lisaa(m, g); };
  // laatikko akselin suuntaan: s0..s1, l0..l1, z0..z1 (pohja ja katto voivat kaartua profiilin mukaan: zTop(s))
  const lohko = (m, s0, s1, l0, l1, zb, zt, uvs = 1) => { const g = new THREE.BoxGeometry(1, 1, 1); const p = g.attributes.position, uv = g.attributes.uv;
    for (let i = 0; i < p.count; i++) { const S = p.getX(i) < 0 ? s0 : s1, Lr = p.getZ(i) < 0 ? l1 : l0, top = p.getY(i) > 0, zt2 = typeof zt === 'function' ? zt(S) : zt, zb2 = typeof zb === 'function' ? zb(S) : zb;
      const v = W3(S, Lr, top ? zt2 : zb2); p.setXYZ(i, v.x, v.y, v.z); }
    // uv maailmasta (sivut ja kansi): s ja l / korkeus
    for (let i = 0; i < p.count; i++) { const x = p.getX(i), y = p.getY(i), z = p.getZ(i), [s, l] = SL(x, -z); uv.setXY(i, (s + Math.abs(l) * 0.0) / uvs, (Math.abs(g.attributes.normal.getY(i)) > 0.5 ? l : y) / uvs); }
    g.computeVertexNormals(); lisaa(m, g); };

  // ---- ponttonit (betoni) ja kansi (puu) ----
  const ZB = WL - 0.55;
  for (let s = S_P0; s < S_L0 - 0.1; s += 11.8) { const s1 = Math.min(S_L0 - 0.15, s + 11.5); lohko(betoni, s, s1, -2.0, 2.0, ZB, DECK - 0.1, 2.5); }
  lohko(betoni, S_L0, S_L1, -3.0, 3.0, ZB, DECK - 0.1, 2.5);                                           // Etelärannan ponttonilaituri
  lohko(betoni, S_K0, S_K1 + 0.6, -2.2, 2.2, Math.min(zK - 1, ZB), zK - 0.12, 2.5);                      // Kirjurinluodon maatuki
  lohko(betoni, S_E1 - 0.4, S_E2, -1.9, 1.9, zE - 1.2, zE - 0.12, 2.5);                                  // Etelärannan pään laatta
  // kansi: luiska ja ponttonit yhtenä nauhana (pitkittäiset laudat), laituri ja päät omina
  const kansi = (s0, s1, hw, step = 1) => { const p = [], uv = [], I = []; let k = 0;
    for (let s = s0; s <= s1 + 1e-6; s += step) { const sc = Math.min(s, s1), z = zf(sc); for (const l of [-hw, hw]) { const v = W3(sc, l, z); p.push(v.x, v.y, v.z); uv.push(sc / 2.4, (l + hw) / 2.4); }
      if (k) I.push(2 * k - 2, 2 * k - 1, 2 * k + 1, 2 * k - 2, 2 * k + 1, 2 * k); k++; }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(p, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); g.setIndex(I); g.computeVertexNormals();
    // kolmioiden kierto ylöspäin
    const nrm = g.attributes.normal; if (nrm.getY(0) < 0) { for (let i = 0; i < I.length; i += 3) { const t = I[i + 1]; I[i + 1] = I[i + 2]; I[i + 2] = t; } g.setIndex(I); g.computeVertexNormals(); }
    lisaa(puu, g); };
  kansi(S_K0, S_L0, 1.85, 1); kansi(S_L0, S_L1, 2.85, 1); kansi(S_L1, S_E1, 1.4, 0.5); kansi(S_E1, S_E2, 1.7, 1);
  // kannen reunalistat (tumma teräs) ponttonien ja luiskan matkalla
  for (const sd of [-1, 1]) for (let s = S_K1; s < S_L0; s += 2) { const s1 = Math.min(S_L0, s + 2); sauva(tumma, W3(s, sd * 1.92, zf(s) + 0.04), W3(s1, sd * 1.92, zf(s1) + 0.04), 0.12, 0.14); }

  // ---- kaiteet: tolpat 2 m välein, käsijohde, välijohde, alajohde ja X-ristikko jokaisessa kentässä ----
  const H = 1.1;
  const kaide = (pts) => {   // pts: [[s, l], ...] kaiteen linja (tolpat jokaisessa pisteessä)
    for (let i = 0; i < pts.length; i++) { const [s, l] = pts[i], z = zf(Math.max(S_K1, Math.min(S_E2, s))); sauva(teras, W3(s, l, z), W3(s, l, z + H), 0.06);
      if (i + 1 < pts.length) { const [s1, l1] = pts[i + 1], z1 = zf(Math.max(S_K1, Math.min(S_E2, s1)));
        for (const h of [H, H * 0.55, 0.12]) sauva(teras, W3(s, l, z + h), W3(s1, l1, z1 + h), h === H ? 0.055 : 0.035);
        sauva(teras, W3(s, l, z + 0.12), W3(s1, l1, z1 + H * 0.55), 0.025); sauva(teras, W3(s, l, z + H * 0.55), W3(s1, l1, z1 + 0.12), 0.025);
        sauva(teras, W3(s, l, z + H * 0.55), W3(s1, l1, z1 + H), 0.025); sauva(teras, W3(s, l, z + H), W3(s1, l1, z1 + H * 0.55), 0.025); } } };
  const linja = (s0, s1, l, step = 2) => { const a = []; const N = Math.max(1, Math.round((s1 - s0) / step)); for (let i = 0; i <= N; i++) a.push([s0 + (s1 - s0) * i / N, l]); return a; };
  for (const sd of [-1, 1]) {
    kaide(linja(S_K1, S_L0, sd * 1.85));                                      // luiska + ponttonit
    kaide([[S_L0, sd * 1.85], [S_L0, sd * 2.85]]); kaide(linja(S_L0, S_L1, sd * 2.85)); kaide([[S_L1, sd * 2.85], [S_L1, sd * 1.4]]);   // laituri
  }
  // Kirjurinluodon portti (kuvassa): korkeammat tolpat ja X-paneelit maatuen päässä
  for (const sd of [-1, 1]) { const z = zK; sauva(teras, W3(S_K1, sd * 1.85, z), W3(S_K1, sd * 1.85, z + 1.35), 0.09); sauva(teras, W3(S_K1 - 2.2, sd * 2.1, z), W3(S_K1 - 2.2, sd * 2.1, z + 1.1), 0.07);
    kaide([[S_K1 - 2.2, sd * 2.1], [S_K1, sd * 1.85]]); }

  // ---- portaikkosilta Etelärantaan: ristikkosivut, askelmat ----
  const S0 = S_L1, S1 = S_E1, TH = 1.35;
  for (const sd of [-1, 1]) { const l = sd * 1.45;
    const N = 6; for (let i = 0; i <= N; i++) { const s = S0 + (S1 - S0) * i / N, z = zf(s); sauva(teras, W3(s, l, z - 0.25), W3(s, l, z + TH), 0.08);
      if (i < N) { const s1 = S0 + (S1 - S0) * (i + 1) / N, z1 = zf(s1); sauva(teras, W3(s, l, z - 0.25), W3(s1, l, z1 - 0.25), 0.12, 0.2); sauva(teras, W3(s, l, z + TH), W3(s1, l, z1 + TH), 0.1);
        sauva(teras, W3(s, l, z - 0.25), W3(s1, l, z1 + TH), 0.05); sauva(teras, W3(s, l, z + TH), W3(s1, l, z1 - 0.25), 0.05); sauva(teras, W3(s, l, z + 0.95), W3(s1, l, z1 + 0.95), 0.04); } } }
  { const n2 = Math.round((S1 - S0) / 0.32); for (let i = 0; i < n2; i++) { const s = S0 + (i + 0.5) * (S1 - S0) / n2, z = zf(s); lohko(teras, s - 0.14, s + 0.14, -1.35, 1.35, z - 0.04, z + 0.035, 1); } }

  // ---- valaisimet (pallo tolpassa) ja ohjauspaalut ----
  for (let s = S_P0 + 4, k = 0; s < S_L0; s += 10, k++) { const sd = k % 2 ? 1 : -1, l = sd * 2.1, z = DECK; const b = W3(s, l, z), t = W3(s, l, z + 4.2);
    sauva(tumma, b, t, 0.1); const sp = new THREE.SphereGeometry(0.28, 14, 10); sp.translate(t.x, t.y + 0.25, t.z); lisaa(pallo, sp); }
  for (const s of [S_K1 + 1, S_L1 + 0.2]) for (const sd of [-1, 1]) { const z = zf(s), b = W3(s, sd * (s > 100 ? 3.05 : 2.05), z), t = W3(s, sd * (s > 100 ? 3.05 : 2.05), z + 4.2);
    sauva(tumma, b, t, 0.1); const sp = new THREE.SphereGeometry(0.28, 14, 10); sp.translate(t.x, t.y + 0.25, t.z); lisaa(pallo, sp); }
  for (let s = S_P0 + 10, k = 0; s < S_L0 - 4; s += 23.5, k++) { const sd = k % 2 ? 1 : -1, c = W3(s, sd * 2.35, 0); const g = new THREE.CylinderGeometry(0.16, 0.16, DECK + 2.4 - (WL - 1.5), 10); g.translate(c.x, (DECK + 2.4 + WL - 1.5) / 2, c.z); lisaa(tumma, g); }
  // punaiset poijut kuvien tapaan (venepaikkojen rajat)
  for (const [s0, s1, sd] of [[24, 60, 1], [70, 118, 1], [30, 70, -1], [86, 122, -1]]) for (let s = s0; s <= s1; s += 6) { const c = W3(s, sd * (14 + ((s * 7) % 3)), WL + 0.1); const g = new THREE.SphereGeometry(0.28, 10, 8); g.translate(c.x, c.y, c.z); lisaa(poiju, g); }

  // ---- yhdistetään materiaaleittain ----
  const ryhma = new THREE.Group(); ryhma.name = 'taavisilta';
  for (const [m, gs] of G) { const gg = mergeGeometries(gs.map(g => g.index ? g.toNonIndexed() : g).map(g => { for (const k of Object.keys(g.attributes)) if (!['position', 'normal', 'uv'].includes(k)) g.deleteAttribute(k); if (!g.attributes.uv) g.setAttribute('uv', new THREE.Float32BufferAttribute(new Float32Array(g.attributes.position.count * 2), 2)); return g; }), false);
    if (!gg) continue; const me = new THREE.Mesh(gg, m); me.castShadow = m !== poiju; me.receiveShadow = true; ryhma.add(me); }
  scene.add(noT(ryhma));
  window.__taavi = { zK, zE, DECK, L: L0, SL, zf, ryhma };
  console.log('[taavisilta] rakennettu: kansi', DECK.toFixed(2), 'Kirjuri', zK.toFixed(2), 'Eteläranta', zE.toFixed(2));
}
