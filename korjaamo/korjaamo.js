// Tapsan korjaamo – peltihalli ja nosto-ovi (omistajan Meshy-mallit, 21.11.2026) paikassa [-598.9, -443.0], Äestäjänkadun eteläpuolen tontilla.
// Ovi katsoo kadulle (suunta 8° pohjoisesta itään) ja rullautuu ylös, kun pelaaja tulee jalan tai autolla alle 10 m päähän; sulkeutuu yli 13 m päässä.
// Halliin voi kävellä ja ajaa sisään: seinät ja suljettu ovi ovat kiinteitä (window.__furn → index.html SOLID), lattian korkeus tulee
// funktiosta window.__korjaamoZ (index.html carGround kysyy sitä). Tarinan paikat LOC_KORJAAMO ja LOC_KORJAAMO_OVI: tarina/data/paikat.json.
import * as THREE from '../three.module.min.js';
import { GLTFLoader } from '../GLTFLoader.js';
import MALLIT from './korjaamo_mallit.js';

export const PAIKKA = { x: -598.9, y: -443.0 }, SUUNTA = 8 * Math.PI / 180;      // suunta = mihin ovi katsoo (0 = pohjoinen, myötäpäivään)
// mallin mitat (m, mallin omat akselit: +z = ovipääty, +x = ovelta katsoen oikea... kartalla länsi kun ovi on pohjoiseen)
const SEINA_X = 4.85, SEINA_Z = 6.1, LAATTA = { x: 5.85, z0: -7.6, z1: 7.5 }, AUKKO = { x0: -2.45, x1: 1.70, yla: 3.92, z: 6.3 }, LATTIA = 0.08, UPOTUS = 0.03;
const OVI = { lev: 6.05, kork: 4.0 }, RAMPPI = 4.5, AUKI = 10, KIINNI = 13, KESTO = 2.6;
const fx = Math.sin(SUUNTA), fy = Math.cos(SUUNTA);
const kartalle = (lx, lz) => ({ x: PAIKKA.x + lz * fx - lx * fy, y: PAIKKA.y + lz * fy + lx * fx });
const paikalliseen = (x, y) => { const dx = x - PAIKKA.x, dy = y - PAIKKA.y; return { lx: -dx * fy + dy * fx, lz: dx * fx + dy * fy }; };
export const OVI_ULKONA = kartalle((AUKKO.x0 + AUKKO.x1) / 2, SEINA_Z + 3.4);      // 3,4 m oven edessä (LOC_KORJAAMO_OVI)

const lataa = b64 => { const bin = atob(b64), buf = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i); return new Promise((ok, ei) => new GLTFLoader().parse(buf.buffer, '', ok, ei)); };
const eiNostoa = o => o.traverse(q => { q.userData.noT = true; if (q.isMesh) { q.castShadow = q.receiveShadow = false; for (const m of [].concat(q.material)) m.userData.noT = true; } });

// Sisustus ja pihan tavarat yksinkertaisista kappaleista (mallin akselit, lattia y = LATTIA): loisteputket, lattiamaalaus ja öljyläikät,
// työpöytä ja työkalutaulu, punainen työkaluvaunu, hylly purkkeineen, rengaspinot, tynnyrit, lava ja ulkovalo.
function sisustus(ox) {
  const g = new THREE.Group(), y0 = LATTIA + 0.005, M = (c, o = {}) => new THREE.MeshLambertMaterial({ color: c, ...o });
  const lisaa = (geo, mat, x, y, z, ry = 0) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.rotation.y = ry; g.add(m); return m; };
  const box = (w, h, d, mat, x, y, z, ry) => lisaa(new THREE.BoxGeometry(w, h, d), mat, x, y + h / 2, z, ry);
  const cyl = (r, h, mat, x, y, z) => lisaa(new THREE.CylinderGeometry(r, r, h, 20), mat, x, y + h / 2, z);
  // lattia: ajoruudun keltamusta raidoitus ja öljyläikät
  const c = document.createElement('canvas'); c.width = 512; c.height = 1024; const k = c.getContext('2d'); k.clearRect(0, 0, 512, 1024);
  k.lineWidth = 22; k.strokeStyle = '#d8b21c'; k.strokeRect(40, 40, 432, 944); k.save(); k.beginPath(); k.rect(29, 29, 454, 22); k.rect(29, 973, 454, 22); k.clip(); k.strokeStyle = '#1c1c1c'; k.lineWidth = 14; for (let i = -40; i < 560; i += 44) { k.beginPath(); k.moveTo(i, 0); k.lineTo(i + 60, 1024); k.stroke(); } k.restore();
  for (const [x, y, r] of [[250, 420, 90], [300, 520, 55], [200, 700, 40], [330, 250, 30]]) { const gr = k.createRadialGradient(x, y, 2, x, y, r); gr.addColorStop(0, 'rgba(20,18,16,0.75)'); gr.addColorStop(1, 'rgba(20,18,16,0)'); k.fillStyle = gr; k.fillRect(x - r, y - r, 2 * r, 2 * r); }
  const lt = new THREE.CanvasTexture(c); lt.colorSpace = THREE.SRGBColorSpace; lt.anisotropy = 4;
  const lm = lisaa(new THREE.PlaneGeometry(4.4, 8.8), new THREE.MeshLambertMaterial({ map: lt, transparent: true, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 }), ox, y0 + 0.01, 0.6); lm.rotation.x = -Math.PI / 2;
  // loisteputket harjan alla ja ulkovalo oven päällä
  const putki = new THREE.MeshBasicMaterial({ color: 0xfff6dc }), runko = M(0x6a6d70);
  for (const z of [-3.6, 0, 3.6]) { box(1.5, 0.07, 0.22, runko, 0, 4.55, z); box(1.4, 0.05, 0.07, putki, 0, 4.49, z - 0.05); box(1.4, 0.05, 0.07, putki, 0, 4.49, z + 0.05); box(0.03, 1.2, 0.03, runko, -0.6, 4.62, z); box(0.03, 1.2, 0.03, runko, 0.6, 4.62, z); }
  box(0.5, 0.12, 0.3, runko, ox, AUKKO.yla + 1.22, 6.78); box(0.42, 0.04, 0.24, putki, ox, AUKKO.yla + 1.19, 6.78);
  // työpöytä takaseinällä + ruuvipenkki + työkalutaulu
  const puu = M(0x7a5a3a), teras = M(0x4c5258), tumma = M(0x25282b);
  box(3.4, 0.08, 0.8, puu, -2.4, y0 + 0.86, -5.45); for (const x of [-4.0, -0.8]) for (const z of [-5.75, -5.15]) box(0.08, 0.86, 0.08, teras, x, y0, z); box(3.3, 0.04, 0.7, teras, -2.4, y0 + 0.25, -5.45);
  box(0.22, 0.16, 0.3, M(0x2f5f9a), -3.6, y0 + 0.94, -5.3); box(0.1, 0.1, 0.42, tumma, -3.6, y0 + 1.0, -5.3);
  box(3.0, 1.1, 0.04, M(0x8b7355), -2.4, y0 + 1.25, -5.88); const tv = [0xb03020, 0x303438, 0xd0a020, 0x303438, 0x2f5f9a, 0x303438, 0xb03020]; tv.forEach((v, i) => box(0.07, 0.3 + (i % 3) * 0.14, 0.03, M(v), -3.6 + i * 0.4, y0 + 1.5 + (i % 2) * 0.2, -5.84));
  // punainen työkaluvaunu laatikoineen
  box(0.95, 0.95, 0.5, M(0xb3261e), 0.3, y0 + 0.1, -5.5); for (let i = 0; i < 5; i++) box(0.85, 0.02, 0.02, M(0xd8d8d8), 0.3, y0 + 0.25 + i * 0.17, -5.24); for (const x of [-0.1, 0.7]) cyl(0.05, 0.1, tumma, x, y0, -5.5);
  // hylly sivuseinällä: purkit ja laatikot
  for (const z of [-3.9, -1.3]) for (const x of [4.05, 4.55]) box(0.05, 2.1, 0.05, teras, x, y0, z); for (let i = 0; i < 4; i++) box(0.55, 0.03, 2.65, teras, 4.3, y0 + 0.15 + i * 0.62, -2.6);
  const tav = [0x2f5f9a, 0xc8a040, 0x8a8f94, 0xb03020, 0x3c7a4a, 0xd8d0c0]; for (let i = 0; i < 4; i++) for (let jj = 0; jj < 5; jj++) { const h = 0.18 + ((i * 7 + jj * 3) % 4) * 0.07, v = tav[(i * 5 + jj * 2) % 6]; if ((i + jj) % 2) cyl(0.11, h, M(v), 4.3, y0 + 0.18 + i * 0.62, -3.65 + jj * 0.52); else box(0.34, h, 0.36, M(v), 4.3, y0 + 0.18 + i * 0.62, -3.65 + jj * 0.52); }
  // rengaspinot, tynnyrit, lava
  const kumi = M(0x1b1c1e), vanne = M(0x8d9196); const rengas = (x, z, n, y = y0) => { for (let i = 0; i < n; i++) { const t = lisaa(new THREE.TorusGeometry(0.24, 0.1, 10, 22), kumi, x + (i % 2) * 0.03, y + 0.1 + i * 0.2, z + (i % 3) * 0.02); t.rotation.x = Math.PI / 2; cyl(0.15, 0.12, vanne, x + (i % 2) * 0.03, y + 0.04 + i * 0.2, z + (i % 3) * 0.02); } };
  rengas(3.95, -5.35, 5); rengas(3.2, -5.4, 3); rengas(3.4, 7.1, 3, 0.1); rengas(4.1, 7.0, 2, 0.1);
  const tynn = (x, z, v, y = y0) => { cyl(0.29, 0.88, M(v), x, y, z); for (const h of [0.02, 0.3, 0.58, 0.85]) cyl(0.3, 0.03, M(0x3a3d40), x, y + h, z); };
  tynn(-4.25, 2.55, 0x2c5d8f); tynn(-4.25, 3.2, 0xa4512a); tynn(-4.2, 3.85, 0x2c5d8f);
  for (let i = 0; i < 2; i++) { box(1.2, 0.03, 0.8, puu, -3.95, 0.1 + i * 0.15 + 0.11, 7.0); for (const dx of [-0.5, 0, 0.5]) box(0.1, 0.1, 0.8, puu, -3.95 + dx, 0.1 + i * 0.15, 7.0); }
  return g;
}

export async function luoKorjaamo(G) {
  const maa = (x, y) => { const z = G.carGround(x, y); return z == null ? (G.TZs ? G.TZs(x, y) : 0) : z; };
  // lattian taso = tontin korkein kohta laatan alla (ettei maasto nouse lattian läpi); matalalla puolella sokkeli peittää raon
  let pohja = -1e9; for (const lx of [-LAATTA.x, 0, LAATTA.x]) for (const lz of [LAATTA.z0, 0, LAATTA.z1]) { const p = kartalle(lx, lz); pohja = Math.max(pohja, maa(p.x, p.y)); }
  const ox = (AUKKO.x0 + AUKKO.x1) / 2, rp = kartalle(ox, LAATTA.z1 + RAMPPI), rampinPaa = maa(rp.x, rp.y), lattia = pohja + LATTIA;
  const ryhma = new THREE.Group(); ryhma.name = 'Tapsan korjaamo'; ryhma.position.set(PAIKKA.x, pohja - UPOTUS, -PAIKKA.y); ryhma.rotation.y = Math.PI - SUUNTA;
  const [gh, go] = await Promise.all([lataa(MALLIT.halli), lataa(MALLIT.ovi)]);
  ryhma.add(gh.scene);
  // nosto-ovi: skaalattu oviaukkoon (4,15 × 3,9 m), yläreuna paikallaan → avautuessa rullautuu ylös (korkeus 100 % → 9 %)
  const ovi = go.scene, sx = (AUKKO.x1 - AUKKO.x0 + 0.3) / OVI.lev, oviK = AUKKO.yla - LATTIA + UPOTUS + 0.06, sy = oviK / OVI.kork;
  ovi.scale.set(sx, sy, 1); ovi.position.set(ox, LATTIA - 0.02, AUKKO.z); ryhma.add(ovi);
  // sokkeli laatan alle ja ajoluiska oven eteen
  const betoni = new THREE.MeshLambertMaterial({ color: 0x6f6e6a });
  const sokkeli = new THREE.Mesh(new THREE.BoxGeometry(LAATTA.x * 2 - 0.04, 1.2, LAATTA.z1 - LAATTA.z0 - 0.04), betoni); sokkeli.position.set(0, -0.6 + 0.02, (LAATTA.z0 + LAATTA.z1) / 2); ryhma.add(sokkeli);
  const lasku = pohja - UPOTUS + 0.03 - rampinPaa, rg = new THREE.BufferGeometry(), w = 3.2, z0 = LAATTA.z1 - 0.05, z1 = LAATTA.z1 + RAMPPI, y1 = 0.03 - lasku - 0.02;
  rg.setAttribute('position', new THREE.Float32BufferAttribute([ox - w, 0.03, z0, ox + w, 0.03, z0, ox + w, y1, z1, ox - w, y1, z1, ox - w, -1.2, z0, ox + w, -1.2, z0, ox + w, -1.2, z1, ox - w, -1.2, z1], 3));
  rg.setIndex([0, 2, 1, 0, 3, 2, 0, 4, 7, 0, 7, 3, 1, 2, 6, 1, 6, 5, 3, 7, 6, 3, 6, 2]); rg.computeVertexNormals();
  ryhma.add(new THREE.Mesh(rg, new THREE.MeshLambertMaterial({ color: 0x4a4a4b, side: THREE.DoubleSide })));
  // kyltti päätyyn oven yläpuolelle
  const c = document.createElement('canvas'); c.width = 1024; c.height = 192; const k = c.getContext('2d');
  k.fillStyle = '#e9e2cf'; k.fillRect(0, 0, 1024, 192); k.strokeStyle = '#8a2a1c'; k.lineWidth = 10; k.strokeRect(9, 9, 1006, 174);
  k.fillStyle = '#8a2a1c'; k.font = '900 104px Arial, Helvetica, sans-serif'; k.textAlign = 'center'; k.textBaseline = 'middle'; k.fillText('TAPSAN KORJAAMO', 512, 100);
  const kt = new THREE.CanvasTexture(c); kt.colorSpace = THREE.SRGBColorSpace; kt.anisotropy = 4;
  const kyltti = new THREE.Mesh(new THREE.PlaneGeometry(4.6, 0.86), new THREE.MeshLambertMaterial({ map: kt })); kyltti.position.set(ox, AUKKO.yla + 0.72, 6.66); ryhma.add(kyltti);
  ryhma.add(sisustus(ox));
  eiNostoa(ryhma); G.scene.add(ryhma);

  // kiinteät seinät ja ovi (SOLID lukee window.__furn-listaa: { x, y, yaw, hl = puolipituus suuntaan yaw, hw, gone })
  const laatikko = (lx, lz, pitkin, hl, hw = 0.16) => { const p = kartalle(lx, lz); return { korjaamo: true, x: p.x, y: p.y, yaw: SUUNTA + (pitkin ? 0 : Math.PI / 2), hl, hw, gone: false }; };
  const oviLaatikko = laatikko(ox, SEINA_Z + 0.1, false, (AUKKO.x1 - AUKKO.x0) / 2);
  const seinat = [laatikko(-SEINA_X, 0, true, SEINA_Z + 0.3), laatikko(SEINA_X, 0, true, SEINA_Z + 0.3), laatikko(0, -SEINA_Z, false, SEINA_X),
    laatikko((-SEINA_X + AUKKO.x0) / 2, SEINA_Z + 0.1, false, (AUKKO.x0 + SEINA_X) / 2), laatikko((SEINA_X + AUKKO.x1) / 2, SEINA_Z + 0.1, false, (SEINA_X - AUKKO.x1) / 2), oviLaatikko,
    laatikko(-1.35, -5.5, false, 3.3, 0.5), laatikko(4.3, -2.6, true, 1.4, 0.4), laatikko(3.6, -5.2, false, 0.9, 0.6), laatikko(-4.25, 2.9, true, 0.8, 0.4), laatikko(3.75, 7.05, false, 0.75, 0.45)];      // + työpöytä ja kaappi, hylly, renkaat, tynnyrit, ulkorenkaat
  const vieSeinat = () => { const F = window.__furn; if (F && !F.includes(oviLaatikko)) for (const s of seinat) F.push(s); };      // pelin penkkilohko luo listan vasta kun pelaaja on lähellä keskustaa → yritetään uudestaan
  if (!window.__furn) window.__furn = [];
  vieSeinat(); setInterval(vieSeinat, 2000);

  // lattian ja luiskan korkeus pelaajalle, autolle ja hahmoille
  window.__korjaamoZ = (x, y) => { if (Math.abs(x - PAIKKA.x) > 22 || Math.abs(y - PAIKKA.y) > 22) return null; const { lx, lz } = paikalliseen(x, y);
    if (Math.abs(lx) <= LAATTA.x && lz >= LAATTA.z0 && lz <= LAATTA.z1) return lattia;
    if (Math.abs(lx - ox) <= w && lz > LAATTA.z1 && lz <= z1) return lattia + (rampinPaa - lattia) * (lz - LAATTA.z1) / RAMPPI;
    return null; };

  // oven liike
  let auki = 0, tavoite = 0, edell = performance.now();
  const ovella = kartalle(ox, SEINA_Z);
  const pelaaja = () => { const Wk = window.__walk, C = window.__car, S = G.S; if (Wk && Wk.on && !Wk.in) return Wk; if (C && document.body.classList.contains('car')) return C; return S && (S.alt || 0) < lattia + 8 ? S : null; };
  const aseta = () => { const e = auki * auki * (3 - 2 * auki), kk = 1 - 0.91 * e; ovi.scale.y = sy * kk; ovi.position.y = LATTIA - 0.02 + oviK * (1 - kk); oviLaatikko.gone = auki > 0.55; };
  aseta();
  const kierros = nyt => { const dt = Math.min(0.1, (nyt - edell) / 1000); edell = nyt; const p = pelaaja();
    if (p) { const d = Math.hypot(p.x - ovella.x, p.y - ovella.y); if (d < AUKI) tavoite = 1; else if (d > KIINNI) tavoite = 0; }
    if (auki !== tavoite) { auki = tavoite > auki ? Math.min(1, auki + dt / KESTO) : Math.max(0, auki - dt / KESTO); aseta(); }
    requestAnimationFrame(kierros); };
  requestAnimationFrame(kierros);

  const api = { ryhma, ovi, seinat, oviLaatikko, lattia, get auki() { return auki; }, avaa(b) { tavoite = b ? 1 : 0; }, oviUlkona: OVI_ULKONA };
  window.__korjaamo = api; console.log('[korjaamo] Tapsan korjaamo paikallaan, lattia', lattia.toFixed(2), 'm'); return api;
}

if (typeof window !== 'undefined' && !window.__korjaamoKokeilu) { const odota = () => { const G = window.__game; if (G && G.scene && G.S && G.carGround) luoKorjaamo(G).catch(e => console.error('[korjaamo]', e)); else setTimeout(odota, 500); }; odota(); }
