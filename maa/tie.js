// Maan pinta vaihe 3 (MAAN_PINTA_SUUNNITELMA.md osa C): tien pinnan yksityiskohdat lähellä pelaajaa, 21.11.2026.
// Omistaja: "maasta pelatessa … hieman maasta nousevia itemeitä" / "asfaltti näyttää asfaltilta".
//   - kaivonkannet (valurautaa, pyöreä Ø 0,66 m) ajoradan keskellä, ympärillä usein tummempi paikkausasfaltti
//   - sadevesikaivot (ritilä 0,45 × 0,55 m betonikehyksessä) ajoradan reunassa reunakiven vieressä
//   - asfalttipaikkaukset (suorakaiteet, tummempi tuore asfaltti) kaivonkansien ympärillä ja satunnaisesti ajoradoilla
// Lähde: maa/esineet.json (tools/maa/esineet.py: OSM-keskiviiva + sääntö). Peli tarkentaa paikan katugeometriaan (060 ROAD.asphAt / paveAt):
// kansi vain asfaltilla, sadevesikaivo siirretään reunakiven viereen; jos reunaa ei löydy (ulkoalueen tiet), kaivoa ei piirretä.
// Piirto: InstancedMesh per laji, vain 140 m säteellä (päivitys kun pelaaja siirtyy 15 m). Ei törmäyksiä (litteitä, 1–2 cm).
// Testaus: window.__tieYks.tila(), .pois(), .paalle().
import * as THREE from '../three.module.min.js';

export default function kaynnista(P) {
  const { scene, camera, carGround } = P;
  const tila = { kansia: 0, kaivoja: 0, paikkoja: 0, nakyvat: [0, 0, 0], valmis: false, virhe: null };
  let paalla = true;

  // ---- tekstuurit (canvas, ei ladattavia kuvia) ----
  const kanvas = (n, piirra) => { const c = document.createElement('canvas'); c.width = c.height = n; piirra(c.getContext('2d'), n);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t; };
  let sd = 12345; const rnd = () => (sd = (sd * 16807) % 2147483647) / 2147483647;
  const kansiTex = kanvas(256, (g, n) => {   // valurautakansi: reunarengas, ruutukuvio, keskellä merkintä, ruostetta ja kulumaa
    const c = n / 2; g.clearRect(0, 0, n, n);
    g.fillStyle = '#3a3836'; g.beginPath(); g.arc(c, c, c - 1, 0, 7); g.fill();
    g.strokeStyle = '#575350'; g.lineWidth = 10; g.beginPath(); g.arc(c, c, c - 8, 0, 7); g.stroke();
    g.save(); g.beginPath(); g.arc(c, c, c - 16, 0, 7); g.clip();
    g.strokeStyle = '#4e4a46'; g.lineWidth = 5; for (let k = -n; k < n; k += 18) { g.beginPath(); g.moveTo(k, 0); g.lineTo(k + n, n); g.stroke(); g.beginPath(); g.moveTo(k + n, 0); g.lineTo(k, n); g.stroke(); }
    g.fillStyle = '#34312f'; g.beginPath(); g.arc(c, c, 30, 0, 7); g.fill(); g.fillStyle = '#5a5551'; g.font = 'bold 22px sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('PORI', c, c);
    for (let k = 0; k < 900; k++) { const x = rnd() * n, y = rnd() * n, r = 1 + rnd() * 5; g.fillStyle = rnd() < 0.5 ? `rgba(110,62,34,${0.10 + rnd() * 0.25})` : `rgba(140,138,132,${0.05 + rnd() * 0.15})`; g.beginPath(); g.arc(x, y, r, 0, 7); g.fill(); }
    g.restore();
    g.strokeStyle = 'rgba(20,20,20,0.8)'; g.lineWidth = 3; g.beginPath(); g.arc(c, c, c - 2, 0, 7); g.stroke(); });
  const kaivoTex = kanvas(256, (g, n) => {   // sadevesikaivo: betonikehys, valurautaritilä raoilla, roskaa ja kosteutta
    g.fillStyle = '#8d8b86'; g.fillRect(0, 0, n, n);
    for (let k = 0; k < 1500; k++) { g.fillStyle = `rgba(${60 + rnd() * 80},${60 + rnd() * 80},${60 + rnd() * 70},0.25)`; g.fillRect(rnd() * n, rnd() * n, 2, 2); }
    const m = 44; g.fillStyle = '#2f2d2b'; g.fillRect(m, m - 10, n - 2 * m, n - 2 * m + 20);
    g.fillStyle = '#0c0c0c'; for (let k = 0; k < 9; k++) g.fillRect(m + 10 + k * 17.5, m + 4, 9, n - 2 * m - 8);
    g.fillStyle = 'rgba(70,52,30,0.5)'; for (let k = 0; k < 60; k++) g.fillRect(m + rnd() * (n - 2 * m), m + rnd() * (n - 2 * m), 3 + rnd() * 6, 2 + rnd() * 3);
    g.strokeStyle = 'rgba(30,30,30,0.6)'; g.lineWidth = 4; g.strokeRect(m - 2, m - 12, n - 2 * m + 4, n - 2 * m + 24);
    const gr = g.createRadialGradient(n / 2, n / 2, 40, n / 2, n / 2, n * 0.7); gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(1, 'rgba(20,20,20,0.35)'); g.fillStyle = gr; g.fillRect(0, 0, n, n); });
  const paikkaTex = kanvas(128, (g, n) => {   // tuore paikkausasfaltti: tummempi, hieman karkea, reunat saumattu
    g.fillStyle = '#4d4e51'; g.fillRect(0, 0, n, n);
    for (let k = 0; k < 2500; k++) { const v = 55 + rnd() * 40; g.fillStyle = `rgba(${v},${v},${v + 3},0.5)`; g.fillRect(rnd() * n, rnd() * n, 1.5, 1.5); }
    g.strokeStyle = 'rgba(30,30,32,0.8)'; g.lineWidth = 4; g.strokeRect(2, 2, n - 4, n - 4); });
  const mat = (map, alpha, off) => new THREE.MeshLambertMaterial({ map, transparent: alpha, alphaTest: alpha ? 0.5 : 0, polygonOffset: true, polygonOffsetFactor: off, polygonOffsetUnits: off });
  const MK = mat(kansiTex, true, -10), MS = mat(kaivoTex, false, -10), MP = mat(paikkaTex, false, -7);
  MP.opacity = 0.85; MP.transparent = true; MP.depthWrite = false;

  // ---- geometriat (vaaka, y ylös) ----
  const vaaka = (w, h) => { const g = new THREE.PlaneGeometry(w, h); g.rotateX(-Math.PI / 2); return g; };
  const GK = vaaka(0.70, 0.70), GS = vaaka(0.72, 0.84), GP = vaaka(1, 1);

  const N = { k: 500, s: 700, p: 600 };
  const mk = (g, m, n) => { const im = new THREE.InstancedMesh(g, m, n); im.count = 0; im.frustumCulled = false; im.userData.noT = true; im.receiveShadow = true; scene.add(im); return im; };
  const IK = mk(GK, MK, N.k), IS = mk(GS, MS, N.s), IP = mk(GP, MP, N.p);

  // ---- paikat: esineet.json -> tarkennus katugeometriaan ----
  let KA = [], SA = [], PA = [];   // [x, y, kulma, (sx, sy)]
  const odotaRoad = () => new Promise(ok => { const t = setInterval(() => { const R = window.__ROAD; if (R && R.on && R.uAB) { clearInterval(t); ok(R); } }, 500); });
  Promise.all([fetch('./maa/esineet.json').then(r => r.json()), odotaRoad()]).then(([E, R]) => {
    const asph = R.asphAt, pave = R.paveAt;
    const kk = E.pisteet.kaivonkansi || [], ss = E.pisteet.sadevesikaivo || [];
    // kaivonkansi: vain asfaltilla; 1–2 m siirto tien suuntaan satunnaisesti, kulma satunnainen (kansi pyöreä, kuvio kiertyy)
    for (let i = 0; i < kk.length; i += 3) { const x = kk[i], y = kk[i + 1]; if (!asph(x, y) || !asph(x + 0.5, y) || !asph(x - 0.5, y) || !asph(x, y + 0.5) || !asph(x, y - 0.5)) continue;
      KA.push([x, y, rnd() * 6.283]);
      if (rnd() < 0.45) { const a = kk[i + 2], L = 1.4 + rnd() * 1.6, W = 1.2 + rnd() * 1.0; PA.push([x + (rnd() - 0.5) * 0.4, y + (rnd() - 0.5) * 0.4, a, L, W]); } }
    // sadevesikaivo: kohtisuoraan tien suunnasta etsitään reunakivi (asfaltti -> jalkakäytävä), kaivo 0,45 m reunasta asfaltin puolelle
    for (let i = 0; i < ss.length; i += 3) { const x0 = ss[i], y0 = ss[i + 1], a = ss[i + 2], nx = -Math.sin(a), ny = Math.cos(a); let hit = null;
      for (const sgn of [1, -1]) { for (let d = -3; d <= 9; d += 0.25) { const x = x0 + nx * sgn * d, y = y0 + ny * sgn * d;
          if (asph(x, y) && pave(x + nx * sgn * 0.5, y + ny * sgn * 0.5)) { hit = [x - nx * sgn * 0.2, y - ny * sgn * 0.2, a]; break; } } if (hit) break; }
      if (hit && asph(hit[0], hit[1])) SA.push(hit); }
    // satunnaiset paikkaukset ajoradoilla (sadevesikaivojen viereen ja väleihin): pitkiä kapeita saumapaikkoja ja neliöitä
    for (let i = 0; i < ss.length; i += 3) { if (rnd() > 0.22) continue; const a = ss[i + 2], x = ss[i] + Math.cos(a) * (rnd() - 0.5) * 20, y = ss[i + 1] + Math.sin(a) * (rnd() - 0.5) * 20;
      if (!asph(x, y)) continue; const pitka = rnd() < 0.4; PA.push([x, y, a + (rnd() - 0.5) * 0.1, pitka ? 4 + rnd() * 8 : 1 + rnd() * 2, pitka ? 0.35 + rnd() * 0.3 : 0.9 + rnd() * 1.5]); }
    tila.kansia = KA.length; tila.kaivoja = SA.length; tila.paikkoja = PA.length; tila.valmis = true; paivita(true);
  }).catch(e => { tila.virhe = String(e); console.warn('[tie] ', e); });

  // ---- lähellä olevat instanssit ----
  const M4 = new THREE.Matrix4(), Q = new THREE.Quaternion(), Q2 = new THREE.Quaternion(), NR = new THREE.Vector3(), V = new THREE.Vector3(), SC = new THREE.Vector3(), Y = new THREE.Vector3(0, 1, 0);
  let px = 1e9, py = 1e9;
  const R2 = 140 * 140;
  const z = (x, y) => { const g = carGround(x, y, -1e9); return g === null ? null : g; };
  const tayta = (im, A, nMax, h, koko) => { let n = 0;
    for (const p of A) { const dx = p[0] - px, dy = p[1] - py; if (dx * dx + dy * dy > R2) continue; if (n >= nMax) break;
      const g = z(p[0], p[1]); if (g === null) continue;
      // kallistus maan mukaan (paikkaus 1–10 m: muuten asfaltti nousee sen läpi)
      const e = 0.6, gx = (z(p[0] + e, p[1]) ?? g) - (z(p[0] - e, p[1]) ?? g), gy = (z(p[0], p[1] + e) ?? g) - (z(p[0], p[1] - e) ?? g);
      NR.set(-gx / (2 * e), 1, gy / (2 * e)).normalize(); Q2.setFromUnitVectors(Y, NR); Q.setFromAxisAngle(Y, p[2]).premultiply(Q2);
      V.set(p[0], g + h, -p[1]); koko(p, SC); M4.compose(V, Q, SC); im.setMatrixAt(n++, M4); }
    im.count = paalla ? n : 0; im.instanceMatrix.needsUpdate = true; return n; };
  function paivita(pakota) {
    if (!tila.valmis) return; const cx = camera.position.x, cy = -camera.position.z;
    if (!pakota && Math.hypot(cx - px, cy - py) < 15) return; px = cx; py = cy;
    if (camera.position.y - (z(cx, cy) ?? 0) > 120) { IK.count = IS.count = IP.count = 0; return; }   // kopterista ylhäältä ei tarvita
    tila.nakyvat = [tayta(IK, KA, N.k, 0.03, (p, s) => s.set(1, 1, 1)), tayta(IS, SA, N.s, 0.025, (p, s) => s.set(1, 1, 1)),
      tayta(IP, PA, N.p, 0.02, (p, s) => s.set(p[3], 1, p[4]))];
  }
  setInterval(() => paivita(false), 400);
  window.__tieYks = { tila: () => tila, pois() { paalla = false; IK.count = IS.count = IP.count = 0; }, paalle() { paalla = true; paivita(true); }, paivita: () => paivita(true) };
}
