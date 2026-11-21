// Pelin kello ja vuorokausirytmi (omistaja 21.11.2026: "yksi tunti voisi olla 10 minuuttia, joten päivän kesto olisi 240 minuuttia";
// "katulampuissa lämpimän keltainen sävy, kuten myös kaikessa muussa, paitsi neonvaloissa").
//
// 1) Kello: window.__aika (t = pelin kellonaika tunteina 0–24). Bussit, junat ja tehtävät voivat lukea sitä ja ajaa oikeiden aikataulujen kellonaikoja.
// 2) Valo: aamu, päivä, ilta ja yö koko kuvaan yhdellä sävytyksellä (rendererin CustomToneMapping). Pelin valot ja varjot on poltettu ilmakuvaan ja
//    rakennuksiin, joten varjot eivät käänny – vain valon määrä ja sävy muuttuvat. Hohtavat pinnat (toneMapped: false) eivät himmene.
// 3) Ikkunoiden haalea keltainen hohka osassa ikkunoista (window.__winGlow → julkisivuvarjostimet) ja autojen ajo- ja takavalot.
// 4) Katulamput kaikille kaduille (city.js:n katuverkko, omistajan Meshy-malli): syttyvät hämärässä, lämmin keltainen valo, valoläikkä maassa,
//    kaukaa valopisteinä.
// index.html:ään ei tarvita muuta kuin <script type="module" src="aika/aika.js"></script>.
import * as THREE from '../three.module.min.js';
import { GLTFLoader } from '../GLTFLoader.js';
import CITY from '../city.js';
import MALLI from './katuvalo_malli.js';

export const TUNTI_S = 600;                       // pelitunti = 10 min oikeaa aikaa → vuorokausi 240 min
const ALKU = 9, AVAIN = 'pori-aika-v1';
const LAMMIN = 0xffc47a;                          // katulamppujen ja ikkunoiden lämmin keltainen
const pehmea = (a, b, x) => { const t = Math.max(0, Math.min(1, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
// päivänvalo 0..1 (aamuhämärä 5.30–7.30, iltahämärä 18.30–20.30) ja auringonnousun/-laskun lämmin sävy 0..1
export const paivanvalo = t => pehmea(5.5, 7.5, t) * (1 - pehmea(18.5, 20.5, t));
export const rusko = t => Math.min(1, Math.exp(-(((t - 6.6) / 0.85) ** 2)) + Math.exp(-(((t - 19.4) / 0.85) ** 2)));
const YO = [0.04, 0.058, 0.115], RUSKO = [1.10, 0.90, 0.72];      // yön sininen himmennys ja ruskon sävy (kertoimia lineaarisessa väriavaruudessa)
const savy = (d, w) => [0, 1, 2].map(i => (YO[i] + (1 - YO[i]) * d) * (1 + (RUSKO[i] - 1) * w));

function luoKello() {
  let t = ALKU, paiva = 1; try { const s = JSON.parse(localStorage.getItem(AVAIN) || 'null'); if (s && s.t >= 0 && s.t < 24) { t = s.t; paiva = s.paiva || 1; } } catch (e) {}
  const kuulijat = [];
  const A = { kerroin: 1, pysaytetty: false,
    get t() { return t; }, get paiva() { return paiva; }, get tunti() { return Math.floor(t); }, get minuutti() { return Math.floor((t % 1) * 60); },
    get valo() { return paivanvalo(t); }, get yo() { return 1 - paivanvalo(t); }, get rusko() { return rusko(t); }, get lamput() { return paivanvalo(t) < 0.55; },
    teksti() { return String(A.tunti).padStart(2, '0') + ':' + String(A.minuutti).padStart(2, '0'); },
    aseta(h) { t = ((h % 24) + 24) % 24; tallenna(); },
    etene(dt) { if (A.pysaytetty) return; const e = t; t += dt / TUNTI_S * A.kerroin; if (t >= 24) { t -= 24; paiva++; } if (Math.floor(e) !== Math.floor(t)) for (const f of kuulijat) { try { f(Math.floor(t), A); } catch (er) {} } },
    tasatunnein(f) { kuulijat.push(f); },      // f(tunti, kello) aina kun pelitunti vaihtuu (aikataulut, kojut auki/kiinni …)
    // onko kellonaika välillä [a, b) tunteina; toimii myös keskiyön yli (22–6)
    valilla(a, b) { return a <= b ? t >= a && t < b : t >= a || t < b; } };
  const tallenna = () => { try { localStorage.setItem(AVAIN, JSON.stringify({ t, paiva })); } catch (e) {} };
  setInterval(tallenna, 10000);
  return A;
}

// ---------- valo: koko kuvan sävytys ----------
function luoValo(G, A) {
  const R = G.renderer, sc = G.scene; let kaytossa = false;
  const re = /vec3 CustomToneMapping\s*\(\s*vec3 color\s*\)\s*\{\s*return color;\s*\}/;
  if (re.test(THREE.ShaderChunk.tonemapping_pars_fragment)) {
    // toneMappingExposure kantaa kaksi lukua: kokonaisosa = päivänvalo × 200, desimaaliosa = rusko / 2
    THREE.ShaderChunk.tonemapping_pars_fragment = THREE.ShaderChunk.tonemapping_pars_fragment.replace(re,
      `vec3 CustomToneMapping( vec3 color ) { float d = floor( toneMappingExposure ) / 200.0, w = fract( toneMappingExposure ) * 2.0;
        return color * mix( vec3( ${YO.map(v => v.toFixed(3)).join(', ')} ), vec3( 1.0 ), d ) * mix( vec3( 1.0 ), vec3( ${RUSKO.map(v => v.toFixed(2)).join(', ')} ), w ); }`);
    R.toneMappingExposure = 200; R.toneMapping = THREE.CustomToneMapping; kaytossa = true;
  } else console.warn('[aika] CustomToneMapping-kohtaa ei löytynyt three.js:stä – valo ei muutu, vain kello ja lamput toimivat');
  const tausta0 = sc.background && sc.background.isColor ? sc.background.clone() : null;
  // tähdet: pisteitä kaukaisella pallolla kameran ympärillä
  const tp = [], N = 520; let sd = 11; const rnd = () => (sd = (sd * 16807) % 2147483647) / 2147483647;
  for (let i = 0; i < N; i++) { const u = rnd() * 2 - 1, a = rnd() * 6.2832, y = Math.abs(u) * 0.96 + 0.04, r = Math.sqrt(1 - y * y); tp.push(Math.cos(a) * r * 5200, y * 5200, Math.sin(a) * r * 5200); }
  const tg = new THREE.BufferGeometry(); tg.setAttribute('position', new THREE.Float32BufferAttribute(tp, 3));
  const tahdet = new THREE.Points(tg, new THREE.PointsMaterial({ color: 0xdfe8ff, size: 1.6, sizeAttenuation: false, transparent: true, opacity: 0, depthWrite: false, fog: false, toneMapped: false }));
  tahdet.frustumCulled = false; tahdet.renderOrder = -5; tahdet.userData.noT = true; tahdet.material.userData.noT = true; tahdet.visible = false; sc.add(tahdet);
  // pelin omat hohtavat pinnat (siltojen ja rannan lamput, korjaamon loisteputket) eivät saa himmetä yöllä
  const HOHTO = new Set([0xfff3d6, 0xfff3c4, 0xfff6dc]);
  const hohtavat = () => sc.traverse(o => { if (!o.material) return; for (const m of [].concat(o.material)) if (m.isMeshBasicMaterial && m.toneMapped && m.color && HOHTO.has(m.color.getHex())) { m.toneMapped = false; m.needsUpdate = true; } });
  for (const s of [4, 15, 45, 120]) setTimeout(hohtavat, s * 1000);
  let ed = -1, ew = -1;
  return { get kaytossa() { return kaytossa; },
    paivita() { const d = A.valo, w = A.rusko * 0.98; if (Math.abs(d - ed) < 0.002 && Math.abs(w - ew) < 0.004) { tahdet.position.copy(G.camera.position); return; } ed = d; ew = w;
      if (kaytossa) R.toneMappingExposure = Math.round(d * 200) + Math.min(0.49, w / 2);
      const m = kaytossa ? savy(Math.round(d * 200) / 200, w) : [1, 1, 1];
      if (tausta0) sc.background.setRGB(tausta0.r * m[0] + 0.004 * (1 - d), tausta0.g * m[1] + 0.006 * (1 - d), tausta0.b * m[2] + 0.014 * (1 - d));
      // sumu sävyttyy varjostimessa samalla kertoimella kuin muukin kuva, joten sen väriin ei kosketa
      const yo = 1 - d; tahdet.visible = yo > 0.5; tahdet.material.opacity = Math.max(0, (yo - 0.5) * 2) * 0.9; tahdet.position.copy(G.camera.position); } };
}

// ---------- katulamput ----------
const VALI = { 3: 34, 2: 40, 1: 46 }, SIVU = { 3: 6.2, 2: 4.8, 1: 4.0 }, KOKO = { 3: 1, 2: 0.9, 1: 0.75 };      // katuluokittain: lamppuväli, etäisyys keskilinjasta, mittakaava
const LAHI = 240, MAX = 380, PAA = { y: 7.74, z: 2.7 };      // lähialueen säde (m), lamppuja enintään, valaisimen alapinta mallissa

// 21.11.2026 (omistaja: "lyhtypylväät ovat kaikkialla keskellä tietä ... sijoittaa linjoille liikennevalojen mukaan"): lamppu menee reunakiven taakse
// samoin kuin liikennevalot (src/js/092): keskilinjalta sivulle niin kauan kuin ajorataa (ROAD.asphAt) riittää, ja 0,8 m reunan yli. Alle 1,5 m:n
// saarekkeen yli jatketaan. Jos ajorataa ei ole maskissa (roads.js:n ulkopuoli), käytetään katuluokan vakioetäisyyttä, mutta ei koskaan ajoradalle.
function reunanTakana(R, cx, cy, nx, ny, oletus) {
  const A = (x, y) => R && R.asphAt && R.asphAt(x, y);
  if (!A(cx, cy) && !A(cx + nx * 1.5, cy + ny * 1.5)) { const x = cx + nx * oletus, y = cy + ny * oletus; return A(x, y) ? null : { x, y }; }
  let nahty = false;
  for (let q = 0.5; q <= 18; q += 0.5) { const x = cx + nx * q, y = cy + ny * q;
    if (A(x, y)) { nahty = true; continue; }
    if (!nahty) continue;
    if (A(x + nx * 1.5, y + ny * 1.5)) continue;      // kapea saareke tai keskiviiva-alue: ajorata jatkuu
    return { x: cx + nx * (q + 0.8), y: cy + ny * (q + 0.8) }; }
  return null;
}
function lamppuPaikat(R) {
  const L = [], ruutu = new Map(), avain = (x, y) => Math.floor(x / 14) * 8192 + Math.floor(y / 14);
  const vapaa = (x, y) => { const cx = Math.floor(x / 14), cy = Math.floor(y / 14); for (let i = -1; i <= 1; i++) for (let j = -1; j <= 1; j++) { const l = ruutu.get((cx + i) * 8192 + cy + j); if (l) for (const q of l) if ((q.x - x) ** 2 + (q.y - y) ** 2 < 196) return false; } return true; };
  // isot kadut ensin, jotta risteyksissä jää ison kadun lamppu
  for (const k of [3, 2, 1]) CITY.r.forEach((r, ri) => { if (r.k !== k) return; const p = r.p, vali = VALI[k]; let matka = vali * (0.3 + ((ri * 37) % 10) / 25), puoli = ri % 2 ? 1 : -1;
    for (let i = 0; i + 3 < p.length; i += 2) { const ax = p[i], ay = p[i + 1], dx = p[i + 2] - ax, dy = p[i + 3] - ay, len = Math.hypot(dx, dy); if (len < 0.5) continue;
      while (matka <= len) { const u = matka / len, nx = dy / len, ny = -dx / len, pk = reunanTakana(R, ax + dx * u, ay + dy * u, nx * puoli, ny * puoli, SIVU[k]);
        const x = pk ? pk.x : 0, y = pk ? pk.y : 0;
        if (pk && vapaa(x, y)) { const q = { x, y, s: KOKO[k], a: Math.atan2(-nx * puoli, -ny * puoli), z: undefined, ok: undefined }; L.push(q); const kk = avain(x, y); let l = ruutu.get(kk); if (!l) ruutu.set(kk, l = []); l.push(q); }
        puoli = -puoli; matka += vali; }
      matka -= len; } });
  return L;
}

function luoLamput(G, A) {
  const sc = G.scene, L = lamppuPaikat(window.__ROAD), iso = new Map();
  for (const q of L) { const k = Math.floor(q.x / 120) * 4096 + Math.floor(q.y / 120); let l = iso.get(k); if (!l) iso.set(k, l = []); l.push(q); }
  // lamppu kelpaa, jos se ei ole talon sisällä eikä joessa; korkeus pelin omasta maanpinnasta
  const tarkista = q => { if (q.ok !== undefined) return q.ok; let z = null; try { if (G.bldTopAt && G.bldTopAt(q.x, q.y) > -1e8) return q.ok = false; z = G.carGround(q.x, q.y); } catch (e) { return false; } if (z == null) return q.ok = false; q.z = z; return q.ok = true; };
  const eiNostoa = o => { o.userData.noT = true; o.frustumCulled = false; for (const m of [].concat(o.material)) m.userData.noT = true; return o; };
  const pyorea = (sisa, ulko) => { const c = document.createElement('canvas'); c.width = c.height = 128; const k = c.getContext('2d'), g = k.createRadialGradient(64, 64, 0, 64, 64, 64); g.addColorStop(0, sisa); g.addColorStop(0.35, ulko); g.addColorStop(1, 'rgba(0,0,0,0)'); k.fillStyle = g; k.fillRect(0, 0, 128, 128); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; };
  let pylvaat = null;
  const bin = atob(MALLI), buf = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
  new GLTFLoader().parse(buf.buffer, '', gl => { let geo = null; gl.scene.traverse(o => { if (o.isMesh && !geo) geo = o.geometry; });
    pylvaat = eiNostoa(new THREE.InstancedMesh(geo, new THREE.MeshLambertMaterial({ color: 0x6f757a }), MAX)); pylvaat.count = 0; sc.add(pylvaat); }, e => console.warn('[aika] katulampun malli', e));
  const lasiM = new THREE.MeshBasicMaterial({ color: 0xd9dcde, toneMapped: false });
  const lasi = eiNostoa(new THREE.InstancedMesh(new THREE.SphereGeometry(1, 10, 6).scale(0.19, 0.045, 0.3).translate(0, PAA.y - 0.02, PAA.z), lasiM, MAX)); lasi.count = 0; sc.add(lasi);
  const laikkaM = new THREE.MeshBasicMaterial({ map: pyorea('rgba(255,206,140,0.85)', 'rgba(255,176,96,0.42)'), color: 0xffffff, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false, polygonOffset: true, polygonOffsetFactor: -3, polygonOffsetUnits: -3 });
  const laikka = eiNostoa(new THREE.InstancedMesh(new THREE.PlaneGeometry(27, 27).rotateX(-Math.PI / 2).translate(0, 0.07, PAA.z), laikkaM, MAX)); laikka.count = 0; laikka.renderOrder = 3; laikka.visible = false; sc.add(laikka);
  // kaukaa: jokainen lamppu yhtenä valopisteenä (koko kaupunki näkyy yöllä kopterista)
  const pisteM = new THREE.PointsMaterial({ map: pyorea('rgba(255,236,200,1)', 'rgba(255,190,110,0.55)'), color: LAMMIN, size: 6.5 * Math.min(2, window.devicePixelRatio || 1), sizeAttenuation: false, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false });
  pisteM.userData.noT = true; let pisteet = null, tarkistettu = 0, kelpaa = 0;
  const teePisteet = () => { const p = []; for (const q of L) if (q.ok) p.push(q.x, q.z + PAA.y * q.s, -q.y); const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(p, 3));
    if (pisteet) { sc.remove(pisteet); pisteet.geometry.dispose(); } pisteet = new THREE.Points(g, pisteM); pisteet.userData.noT = true; pisteet.frustumCulled = false; pisteet.renderOrder = 4; sc.add(pisteet); kelpaa = p.length / 3; };
  const M = new THREE.Matrix4(), Q = new THREE.Quaternion(), V = new THREE.Vector3(), S = new THREE.Vector3(), Y = new THREE.Vector3(0, 1, 0);
  let odotus = 0, px0 = 1e9, py0 = 1e9, valmis = false;
  const pelaaja = () => { const Wk = window.__walk, C = window.__car, J = window.__jump, P = window.__plane; if (J && J.on) return { x: J.pos.x, y: -J.pos.z }; if (P && P.on) return { x: P.pos.x, y: -P.pos.z }; if (Wk && Wk.on && !Wk.in) return Wk; if (C && G.carG && G.carG.visible && !(Wk && Wk.on)) return C; return G.S; };
  function paivita(dt) {
    // korkeudet ja kelpoisuus vähän kerrallaan (noin 5 000 lamppua), valopisteet rakennetaan uudestaan sitä mukaa
    if (!valmis) { const loppu = Math.min(L.length, tarkistettu + 220); for (; tarkistettu < loppu; tarkistettu++) tarkista(L[tarkistettu]); if (tarkistettu >= L.length) { valmis = true; teePisteet(); } else if (tarkistettu % 1100 < 220) teePisteet(); }
    const yo = A.yo, paalla = A.lamput, voima = paalla ? pehmea(0.45, 0.8, yo) : 0;
    lasiM.color.setHex(paalla ? 0xffe2b0 : 0xd9dcde); laikka.visible = voima > 0.02; laikkaM.opacity = voima * 0.8; if (pisteet) { pisteet.visible = voima > 0.02; pisteM.opacity = voima; }
    odotus -= dt; const p = pelaaja(); if (!p || !pylvaat) return; if (odotus > 0 && Math.hypot(p.x - px0, p.y - py0) < 25) return; odotus = 0.6; px0 = p.x; py0 = p.y;
    const cx = Math.floor(p.x / 120), cy = Math.floor(p.y / 120), lahi = [];
    for (let i = -2; i <= 2; i++) for (let j = -2; j <= 2; j++) { const l = iso.get((cx + i) * 4096 + cy + j); if (l) for (const q of l) { const d = (q.x - p.x) ** 2 + (q.y - p.y) ** 2; if (d < LAHI * LAHI && tarkista(q)) lahi.push([d, q]); } }
    lahi.sort((a, b) => a[0] - b[0]); const n = Math.min(MAX, lahi.length);
    for (let i = 0; i < n; i++) { const q = lahi[i][1]; Q.setFromAxisAngle(Y, Math.PI - q.a); M.compose(V.set(q.x, q.z, -q.y), Q, S.set(q.s, q.s, q.s)); pylvaat.setMatrixAt(i, M); lasi.setMatrixAt(i, M); laikka.setMatrixAt(i, M); }
    for (const o of [pylvaat, lasi, laikka]) { o.count = n; o.instanceMatrix.needsUpdate = true; }
  }
  return { paivita, pelaaja, lista: L, get kelpaa() { return kelpaa; }, get valmis() { return valmis; }, get lahella() { return pylvaat ? pylvaat.count : 0; } };
}

// ---------- ikkunoiden valo ----------
// Julkisivujen varjostimet (src/js/020, 040, 061: WINGLOW, yovalo) lukevat arvon window.__winGlow = (väri × voimakkuus, valaistujen ikkunoiden osuus).
// Omistaja: "ei valaista kaikkia ikkunoita ja tehdään vain haalean keltainen hohka". Väri jaetaan yön sävytyksellä, koska se lisätään kuvaan ennen sävytystä.
const HOHKA = [0.95, 0.70, 0.30], HOHKAN_VOIMA = 0.2;
export const ikkunaOsuus = t => t >= 16 && t < 22 ? 0.36 : t >= 22 ? 0.36 - 0.20 * (t - 22) / 2 : t < 1.5 ? 0.16 - 0.09 * t / 1.5 : t < 5 ? 0.07 : t < 7 ? 0.07 + 0.17 * (t - 5) / 2 : 0.24;
function luoIkkunat(A) {
  const WG = window.__winGlow = window.__winGlow || { value: new THREE.Vector4(0, 0, 0, 0) }, WB = window.__winGlowB = window.__winGlowB || { value: new THREE.Vector4(0, 0, 0, 0) };
  A.poltetutIkkunat = 1;      // poltettujen lohkojen ikkunavalon voimakkuus 0..1 (tunnistus on arvio tummasta lasista; 0 = pois)
  return { paivita() { const d = A.valo, voima = A.lamput ? pehmea(0.45, 0.8, 1 - d) : 0; if (voima <= 0) { WG.value.set(0, 0, 0, 0); WB.value.set(0, 0, 0, 0); return; }
      const m = savy(Math.round(d * 200) / 200, A.rusko * 0.98), k = HOHKAN_VOIMA * voima; WG.value.set(HOHKA[0] * k / m[0], HOHKA[1] * k / m[1], HOHKA[2] * k / m[2], ikkunaOsuus(A.t)); WB.value.copy(WG.value); WB.value.x *= A.poltetutIkkunat; WB.value.y *= A.poltetutIkkunat; WB.value.z *= A.poltetutIkkunat; } };
}

// ---------- autojen valot ----------
// Liikenteen autot (window.__sig.cars) ja pelaajan auto: kaksi lämmintä ajovaloa, kaksi punaista takavaloa ja valokeila tiessä. Pisteitä ja läikkiä, ei oikeita valoja.
function luoAjovalot(G, A) {
  const sc = G.scene, MAXA = 150, MAXK = 60;
  const pyorea = (sisa, ulko) => { const c = document.createElement('canvas'); c.width = c.height = 64; const k = c.getContext('2d'), g = k.createRadialGradient(32, 32, 0, 32, 32, 32); g.addColorStop(0, sisa); g.addColorStop(0.4, ulko); g.addColorStop(1, 'rgba(0,0,0,0)'); k.fillStyle = g; k.fillRect(0, 0, 64, 64); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; };
  const pos = new Float32Array(MAXA * 12), col = new Float32Array(MAXA * 12), geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3).setUsage(THREE.DynamicDrawUsage)); geo.setAttribute('color', new THREE.BufferAttribute(col, 3).setUsage(THREE.DynamicDrawUsage)); geo.setDrawRange(0, 0);
  const pm = new THREE.PointsMaterial({ map: pyorea('rgba(255,255,255,1)', 'rgba(255,255,255,0.5)'), vertexColors: true, size: 5 * Math.min(2, window.devicePixelRatio || 1), sizeAttenuation: false, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false });
  pm.userData.noT = true; const pts = new THREE.Points(geo, pm); pts.userData.noT = true; pts.frustumCulled = false; pts.renderOrder = 5; pts.visible = false; sc.add(pts);
  const km = new THREE.MeshBasicMaterial({ map: pyorea('rgba(255,214,150,0.9)', 'rgba(255,190,110,0.35)'), transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false, polygonOffset: true, polygonOffsetFactor: -3, polygonOffsetUnits: -3 });
  km.userData.noT = true; const keila = new THREE.InstancedMesh(new THREE.PlaneGeometry(6.5, 12).rotateX(-Math.PI / 2).translate(0, 0.08, -7.6), km, MAXK); keila.userData.noT = true; keila.frustumCulled = false; keila.count = 0; keila.renderOrder = 3; keila.visible = false; sc.add(keila);
  const M = new THREE.Matrix4(), Q = new THREE.Quaternion(), V = new THREE.Vector3(), S1 = new THREE.Vector3(1, 1, 1), Y = new THREE.Vector3(0, 1, 0), ETU = [1.0, 0.84, 0.56], TAKA = [1.0, 0.10, 0.06];
  const maa = (x, y, tarkka) => { try { if (tarkka) { const z = G.carGround(x, y); if (z != null) return z; } return G.TZs(x, y); } catch (e) { return 0; } };
  return { paivita(p) { const voima = A.lamput ? pehmea(0.35, 0.7, A.yo) : 0; pts.visible = keila.visible = voima > 0.02; if (!pts.visible || !p) return; pm.opacity = voima; km.opacity = voima * 0.4;
      const L = []; const T = window.__sig && window.__sig.cars; if (T) for (const c of T) { if (c.wx === undefined) continue; const d = (c.wx - p.x) ** 2 + (c.wy - p.y) ** 2; if (d < 450 * 450) L.push([d, c.wx, c.wy, c.yaw, null]); }
      const C = window.__car; if (C && G.carG && G.carG.visible) L.push([0, C.x, C.y, C.yaw, C.z]);
      L.sort((a, b) => a[0] - b[0]); const n = Math.min(MAXA, L.length); let k = 0, nk = 0;
      for (let i = 0; i < n; i++) { const [d, x, y, yaw, z0] = L[i], sn = Math.sin(yaw), cs = Math.cos(yaw), z = z0 ?? maa(x, y, i < 45);
        for (const [f, s, h, v] of [[1.9, 0.6, 0.66, ETU], [1.9, -0.6, 0.66, ETU], [-1.95, 0.6, 0.82, TAKA], [-1.95, -0.6, 0.82, TAKA]]) { pos[k] = x + sn * f + cs * s; pos[k + 1] = z + h; pos[k + 2] = -(y + cs * f - sn * s); col[k] = v[0]; col[k + 1] = v[1]; col[k + 2] = v[2]; k += 3; }
        if (nk < MAXK && d < 160 * 160) { Q.setFromAxisAngle(Y, -yaw); M.compose(V.set(x, z, -y), Q, S1); keila.setMatrixAt(nk++, M); } }
      geo.setDrawRange(0, k / 3); geo.attributes.position.needsUpdate = true; geo.attributes.color.needsUpdate = true; keila.count = nk; keila.instanceMatrix.needsUpdate = true; },
    get autoja() { return geo.drawRange.count / 4; } };
}

// ---------- kello ruudulle ----------
function luoNaytto(A) {
  const e = document.createElement('div'); e.id = 'aika-kello';
  e.style.cssText = 'position:fixed;top:10px;left:50%;transform:translateX(-50%);z-index:40;padding:4px 12px;border-radius:999px;background:rgba(16,22,30,.55);color:#fff;font:600 14px system-ui,sans-serif;letter-spacing:.03em;pointer-events:none;text-shadow:0 1px 2px rgba(0,0,0,.5)';
  document.body.appendChild(e); let ed = '';
  return { paivita() { const s = (A.yo > 0.5 ? '☾ ' : '☀ ') + A.teksti(); if (s !== ed) { ed = s; e.textContent = s; } } };
}

export async function kaynnista() {
  if (window.__aika) return window.__aika;
  for (let i = 0; i < 600 && !(window.__game && window.__game.scene && window.__game.carGround); i++) await new Promise(r => setTimeout(r, 100));
  const G = window.__game; if (!G) throw new Error('[aika] peliä (window.__game) ei löytynyt');
  for (let i = 0; i < 300 && !window.__ROAD; i++) await new Promise(r => setTimeout(r, 100));      // katujen ajorata-maski (lamput reunakiven taakse)
  const A = luoKello(), valo = luoValo(G, A), lamput = luoLamput(G, A), ikkunat = luoIkkunat(A), ajovalot = luoAjovalot(G, A), naytto = luoNaytto(A);
  A.valoOsa = valo; A.lamppuOsa = lamput; A.ajovaloOsa = ajovalot; window.__aika = A;
  let edell = performance.now();
  const kierros = nyt => { const dt = Math.min(0.25, (nyt - edell) / 1000); edell = nyt; A.etene(dt); valo.paivita(); ikkunat.paivita(); try { lamput.paivita(dt); ajovalot.paivita(lamput.pelaaja()); } catch (e) { console.warn('[aika] lamput', e); } naytto.paivita(); requestAnimationFrame(kierros); };
  requestAnimationFrame(kierros);
  console.log('[aika] kello', A.teksti(), '· vuorokausi', (TUNTI_S * 24 / 60) + ' min ·', lamput.lista.length, 'katulamppua ehdolla');
  return A;
}
if (typeof window !== 'undefined' && !window.__aikaKokeilu) kaynnista().catch(e => console.error(e));
