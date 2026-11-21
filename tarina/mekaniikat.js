// Satamakaupunki – Luvun 1 mekaniikat (21.11.2026, omistaja: "tehdäänkö ensimmäinen luku valmiiksi"):
//   hiiviskely (M03)  myyjä kiertää Autoliike Kiillon pihaa; näkökartio, katve talojen takana, juokseminen kuuluu; huomattu-mittari täynnä = FAIL
//   vesiletku  (M04)  kolme vartijaa liimaa Purkukohde-tarroja korjaamon oviin; X pohjassa suihkuttaa (kosketus: X-nappi pohjassa),
//                     kastunut vartija liukastuu ja juoksee pois (PEGI 7: ei vahinkoa); kaikki kolme tarraa paikallaan = FAIL
//   drooni     (M05)  pelaaja lennättää droonia (W/S eteen-taakse, A/D kääntö, Q/E sivuttain, Välilyönti/R ylös, Shift alas), kuvaa Varjo-tornin työmaan
//                     kolme suunnitelmataulua (leiju taulun edessä) ja palaa ennen kuin akku loppuu; kolme törmäystä tai tyhjä akku = FAIL
// Kytkentä: peli.js  Object.assign(KASITTELIJAT, luoMekaniikat({ THREE, G, hahmot, maa, luoHahmot }))
// Pelin koukut: window.__syoteLukko (src/js/110: pelaajan ohjaus pois), window.__kameraKoukku (src/js/122: kamera droonin perään).
// Mallit ovat koodissa (drooni, taulut, nosturit, tarrat, vesisuihku); Meshyn drooni.glb voi korvata droonin myöhemmin.

import { GLTFLoader } from '../GLTFLoader.js';

export function luoMekaniikat({ THREE, G, hahmot, maa, luoHahmot }) {
  const NPC = luoHahmot(G.scene, { hahmot, korkeus: maa });      // mekaniikkojen omat hahmot (partioiva myyjä, vartijat)
  let npcLista = [];
  const npcPaivita = (dt, w) => { NPC.aseta(npcLista); NPC.paivita(dt, w); };
  const kulma = a => Math.atan2(Math.sin(a), Math.cos(a));
  const nm = (o) => { o.traverse(q => { q.userData.noT = true; if (q.material) (Array.isArray(q.material) ? q.material : [q.material]).forEach(m => m.userData.noT = true); }); return o; };
  const varmaMaa = (x, y) => { const z = maa(x, y); return z == null || !isFinite(z) ? 0 : z; };
  // näköyhteys: talo välissä katkaisee (rakennuksen katto yli 1,6 m maan yläpuolella)
  const nakyy = (ax, ay, bx, by) => { const d = Math.hypot(bx - ax, by - ay), n = Math.ceil(d); for (let i = 1; i < n; i++) { const x = ax + (bx - ax) * i / n, y = ay + (by - ay) * i / n; if (G.bldTopAt(x, y) > varmaMaa(x, y) + 1.6) return false; } return true; };
  // X pohjassa (näppäin ja kosketusnappi)
  const X = { pohjassa: false };
  addEventListener('keydown', e => { if (e.code === 'KeyX' && !e.ctrlKey && !e.metaKey) X.pohjassa = true; });
  addEventListener('keyup', e => { if (e.code === 'KeyX') X.pohjassa = false; });
  addEventListener('blur', () => { X.pohjassa = false; });
  const kosketusX = () => { const b = document.getElementById('tr-x'); if (b && !b.dataset.pito) { b.dataset.pito = 1; b.addEventListener('pointerdown', () => X.pohjassa = true); for (const t of ['pointerup', 'pointercancel', 'pointerleave']) b.addEventListener(t, () => X.pohjassa = false); } };

  // ---------------------------------------------------------------- hiiviskely
  // param: { vartijat: [{ hahmo, kierros: [[x, y], ...], nako (m), nopeus, tauko (s) }], kohde: paikka, r }
  const H = { v: [], mittari: 0, kartio: [] };
  const kartioMesh = (r, puoli) => { const g = new THREE.BufferGeometry(), P = [0, 0, 0], N = 16; for (let i = 0; i <= N; i++) { const a = -puoli + 2 * puoli * i / N; P.push(Math.sin(a) * r, 0, -Math.cos(a) * r); }
    const I = []; for (let i = 1; i <= N; i++) I.push(0, i, i + 1); g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3)); g.setIndex(I);
    return nm(new THREE.Mesh(g, new THREE.MeshBasicMaterial({ color: 0xffe066, transparent: true, opacity: 0.22, depthWrite: false, side: THREE.DoubleSide }))); };
  const hiiviskely = {
    alku(p, api) {
      H.mittari = 0; H.v = (p.vartijat || []).map((q, i) => { const K = q.kierros.map(c => Array.isArray(c) ? { x: c[0], y: c[1] } : api.paikka(c));
        const m = kartioMesh(q.nako || 12, 0.62); G.scene.add(m);
        return { id: 'hiivi:' + i, h: q.hahmo || 'VARTIJA', malli: q.malli, K, k: 1, x: K[0].x, y: K[0].y, yaw: Math.atan2(K[1].x - K[0].x, K[1].y - K[0].y), tauko: 0, nako: q.nako || 12, nopeus: q.nopeus || 1.2, taukoS: q.tauko ?? 2.5, mesh: m, nakee: false }; });
      api.vihje('Hiivi kävellen (älä juokse), pysy kartion ulkopuolella ja talojen katveessa.');
    },
    paivita(dt, w, p, api) {
      const Wk = window.__walk, juoksee = Wk && Math.abs(Wk.v) > 3.2, kohde = api.paikka(p.kohde);
      let nahty = false, lahin = 1e9;
      for (const g of H.v) {
        // partio: kävele seuraavaan pisteeseen, pisteessä pysähdy ja katso ympärille
        if (g.nakee) { g.yaw += kulma(Math.atan2(w.x - g.x, w.y - g.y) - g.yaw) * Math.min(1, dt * 5); }
        else if (g.tauko > 0) { g.tauko -= dt; g.yaw += Math.sin(performance.now() / 700 + g.k) * dt * 0.9; }
        else { const t = g.K[g.k], dx = t.x - g.x, dy = t.y - g.y, d = Math.hypot(dx, dy);
          if (d < 0.3) { g.k = (g.k + 1) % g.K.length; g.tauko = g.taukoS; }
          else { const s = Math.min(d, g.nopeus * dt); g.x += dx / d * s; g.y += dy / d * s; g.yaw += kulma(Math.atan2(dx, dy) - g.yaw) * Math.min(1, dt * 6); } }
        // näkeekö: kartio 2 × 35°, etäisyys, näköyhteys; juoksu kuuluu 7 m:iin joka suuntaan
        const dx = w.x - g.x, dy = w.y - g.y, d = Math.hypot(dx, dy); lahin = Math.min(lahin, d);
        const kartiossa = d < g.nako && Math.abs(kulma(Math.atan2(dx, dy) - g.yaw)) < 0.62, kuuluu = juoksee && d < 7;
        g.nakee = w.kulku === 'jalan' && !w.sisalla && (kartiossa || kuuluu) && nakyy(g.x, g.y, w.x, w.y);
        if (g.nakee) { nahty = true; H.mittari += dt * (0.45 + 1.6 * Math.max(0, 1 - d / g.nako)) * (juoksee ? 1.8 : 1); }
        g.mesh.position.set(g.x, varmaMaa(g.x, g.y) + 0.12, -g.y); g.mesh.rotation.y = -g.yaw;
        g.mesh.material.color.setHex(g.nakee ? 0xff5252 : H.mittari > 0.3 ? 0xffa64d : 0xffe066);
      }
      if (!nahty) H.mittari = Math.max(0, H.mittari - dt * 0.25);
      npcLista = H.v.map(g => ({ id: g.id, h: g.h, malli: g.malli, x: g.x, y: g.y, suunta: g.yaw * 180 / Math.PI, anim: g.tauko > 0 || g.nakee ? 'Idle' : 'Walk' }));
      npcPaivita(dt, w);
      api.mittari({ laji: 'palkki', nimi: H.mittari > 0.05 ? '👁 Huomattu' : '🤫 Hiivit', arvo: Math.min(1, H.mittari) });
      if (H.mittari >= 1) return 'epaonnistui';
      if (kohde && w.kulku === 'jalan' && Math.hypot(w.x - kohde.x, w.y - kohde.y) < (p.r || 2.5)) return 'valmis';
      return null;
    },
    loppu() { for (const g of H.v) { G.scene.remove(g.mesh); g.mesh.geometry.dispose(); } H.v = []; npcLista = []; NPC.aseta([]); }
  };

  // ---------------------------------------------------------------- Meshyn mallit (tarina/mallit/*.js, base64-GLB kuten npc_*.js)
  const mallit = {};
  const malli = nimi => mallit[nimi] || (mallit[nimi] = import(`./mallit/${nimi}.js`).then(K => { const bin = atob(K.default), u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
    return new Promise((ok, ei) => new GLTFLoader().parse(u.buffer, '', g => ok(g.scene), ei)); }).catch(e => { console.warn('[tarina] malli puuttuu', nimi, e); return null; }));
  // korjaamon piha: vesiletkukela seinän vieressä oven vasemmalla, sammutin oikealla (aina paikalla, M04 käyttää letkua)
  const KORJ = { kela: null, sammutin: null };
  const korjaamonVarusteet = (ovi) => { if (KORJ.tehty) return; KORJ.tehty = true; const seina = ovi.y - 3.4;
    malli('vesiletku').then(m => { if (!m) return; const o = nm(m.clone()), x = ovi.x - 3.4, y = seina + 0.35; o.position.set(x, varmaMaa(x, y), -y); o.rotation.y = 0.4; G.scene.add(o); KORJ.kela = { x, y, z: varmaMaa(x, y) + 0.28 }; });
    malli('sammutin').then(m => { if (!m) return; const o = nm(m.clone()), x = ovi.x + 2.6, y = seina + 0.18; o.scale.setScalar(1.35); o.position.set(x, varmaMaa(x, y), -y); o.rotation.y = Math.PI + 0.3; G.scene.add(o); KORJ.sammutin = o; }); };
  { const T0 = Date.now(), odota = () => { const T = window.__tarina; const q = T && T.moottori && T.moottori.paikka('LOC_KORJAAMO_OVI'); if (q) korjaamonVarusteet(q); else if (Date.now() - T0 < 60000) setTimeout(odota, 1000); }; setTimeout(odota, 1500); }
  // letku kelalta Ramin käteen: putki (painuu keskeltä) + messinkisuutin kädessä
  const L = { putki: null, suutin: null, mat: new THREE.MeshStandardMaterial({ color: 0x2f7a3a, roughness: 0.7 }) };
  const kasi = new THREE.Vector3();
  const kadenPaikka = (w, Wk) => { const b = G.walkG && (G.walkG.getObjectByName('hand_r') || G.walkG.getObjectByName('Hand_R'));
    if (b && G.walkG.visible) { b.getWorldPosition(kasi); return { x: kasi.x, y: -kasi.z, z: kasi.y }; }
    const sn = Math.sin(Wk.yaw), cs = Math.cos(Wk.yaw); return { x: w.x + sn * 0.35 + cs * 0.25, y: w.y + cs * 0.35 - sn * 0.25, z: (Wk.z || varmaMaa(w.x, w.y)) + 1.1 }; };
  function letku(w, Wk) {
    if (!KORJ.kela || !Wk) return null; const h = kadenPaikka(w, Wk), a = KORJ.kela, d = Math.hypot(h.x - a.x, h.y - a.y), pts = [];
    for (let i = 0; i <= 12; i++) { const t = i / 12, sag = Math.sin(t * Math.PI) * Math.min(0.9, d * 0.05); const x = a.x + (h.x - a.x) * t, y = a.y + (h.y - a.y) * t, g = varmaMaa(x, y) + 0.04;
      pts.push(new THREE.Vector3(x, Math.max(g, a.z + (h.z - a.z) * t - sag - (t > 0.1 && t < 0.85 ? 0.6 : 0)), -y)); }
    if (L.putki) { G.scene.remove(L.putki); L.putki.geometry.dispose(); }
    L.putki = nm(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 24, 0.022, 6), L.mat)); G.scene.add(L.putki);
    if (!L.suutin) { const g = new THREE.Group(); const m = new THREE.MeshStandardMaterial({ color: 0xb08d3c, roughness: 0.35, metalness: 0.8 }); const c = new THREE.Mesh(new THREE.CylinderGeometry(0.022, 0.03, 0.2, 10), m); c.rotation.x = Math.PI / 2; c.position.z = -0.1; g.add(c); L.suutin = nm(g); G.scene.add(L.suutin); }
    L.suutin.position.set(h.x, h.z, -h.y); L.suutin.rotation.y = -Wk.yaw; return h; }
  const letkuPois = () => { if (L.putki) { G.scene.remove(L.putki); L.putki.geometry.dispose(); L.putki = null; } if (L.suutin) { G.scene.remove(L.suutin); L.suutin = null; } };

  // ---------------------------------------------------------------- vesiletku
  // param: { paikka (piha), ovi: paikka (nosto-oven edusta), vartijoita, ovet, tarraS (s/ovi), kantama (m) }
  const V = { g: [], ovet: [], suihku: null, osat: [], aika: 0 };
  const tarraTex = (() => { let t = null; return () => { if (t) return t; const c = document.createElement('canvas'); c.width = 256; c.height = 128; const x = c.getContext('2d');
    x.fillStyle = '#ffd400'; x.fillRect(0, 0, 256, 128); x.fillStyle = '#111'; x.fillRect(0, 0, 256, 14); x.fillRect(0, 114, 256, 14);
    x.font = 'bold 40px sans-serif'; x.textAlign = 'center'; x.fillText('PURKUKOHDE', 128, 62); x.font = 'bold 20px sans-serif'; x.fillText('VARJO HOLDINGS', 128, 96);
    t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; }; })();
  const vesiletku = {
    alku(p, api) {
      const ovi = api.paikka(p.ovi || 'LOC_KORJAAMO_OVI'), n = p.vartijoita || 3, no = p.ovet || 3, seina = ovi.y - 3.4;      // korjaamon pohjoisseinä (ovi katsoo pohjoiseen)
      V.ovet = []; for (let i = 0; i < no; i++) { const dx = (i - (no - 1) / 2) * 6.5; const m = nm(new THREE.Mesh(new THREE.PlaneGeometry(1.4, 0.7), new THREE.MeshBasicMaterial({ map: tarraTex(), transparent: true, opacity: 0, side: THREE.DoubleSide })));
        const x = ovi.x + dx, y = seina + 0.06; m.position.set(x, varmaMaa(x, ovi.y) + 1.55, -y); G.scene.add(m); V.ovet.push({ x, y: seina + 0.9, p: 0, m }); }
      const mallit = ['npc_vartija', 'npc_vartija_b', 'npc_vartija_c'], alut = [[-1.6, -2.4], [-5.5, 0.5], [5, 2.5]];
      V.g = []; for (let i = 0; i < n; i++) { const a = alut[i % alut.length]; V.g.push({ id: 'letku:' + i, malli: mallit[i % 3], x: ovi.x + a[0], y: ovi.y + a[1], ovi: V.ovet[i % no], marka: 0, tila: 'menee', t: 0, yaw: Math.PI, pako: { x: ovi.x + (i - 1) * 25 + 10, y: ovi.y + 55 } }); }
      // vesisuihku: pisarat (Points), lentävät pelaajan kädestä katsesuuntaan, painovoima
      const N = 260, pos = new Float32Array(N * 3).fill(-1e4); const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
      V.suihku = nm(new THREE.Points(geo, new THREE.PointsMaterial({ color: 0xbfe6ff, size: 0.16, transparent: true, opacity: 0.85, depthWrite: false })));
      V.suihku.frustumCulled = false; G.scene.add(V.suihku); V.osat = Array.from({ length: N }, () => ({ x: 0, y: 0, z: -1e4, vx: 0, vy: 0, vz: 0, t: 9 })); V.i = 0; V.aika = 0;
      V.api = api; korjaamonVarusteet(ovi); kosketusX(); api.emit('kehote', 'Pidä X pohjassa: suihkuta vettä (käänny vartijaa kohti)');
    },
    paivita(dt, w, p, api) {
      const Wk = window.__walk, kantama = p.kantama || 9, ruiskuttaa = X.pohjassa && w.kulku === 'jalan';
      V.aika += dt;
      // pisarat
      const suu = w.kulku === 'jalan' ? letku(w, Wk) : (letkuPois(), null);
      if (ruiskuttaa && Wk) { const sn = Math.sin(Wk.yaw), cs = Math.cos(Wk.yaw), z0 = suu ? suu.z : (Wk.z || varmaMaa(w.x, w.y)) + 1.25, ox = suu ? suu.x + sn * 0.2 : w.x + sn * 0.6, oy = suu ? suu.y + cs * 0.2 : w.y + cs * 0.6;
        for (let k = 0; k < 9; k++) { const o = V.osat[V.i = (V.i + 1) % V.osat.length], h = (Math.random() - 0.5) * 0.12, s = 11 + Math.random() * 3;
          Object.assign(o, { x: ox, y: oy, z: z0, vx: (sn + cs * h) * s, vy: (cs - sn * h) * s, vz: 2.2 + Math.random() * 1.2, t: 0 }); } }
      const A = V.suihku.geometry.attributes.position.array;
      V.osat.forEach((o, i) => { if (o.t > 1.2) { A[i * 3 + 1] = -1e4; return; } o.t += dt; o.vz -= 9.8 * dt; o.x += o.vx * dt; o.y += o.vy * dt; o.z += o.vz * dt; const gz = varmaMaa(o.x, o.y); if (o.z < gz) { o.t = 9; } A[i * 3] = o.x; A[i * 3 + 1] = o.z; A[i * 3 + 2] = -o.y; });
      V.suihku.geometry.attributes.position.needsUpdate = true;
      // vartijat
      let jaljella = 0;
      for (const g of V.g) {
        if (g.tila === 'poissa') continue; jaljella++;
        const dx = g.x - w.x, dy = g.y - w.y, d = Math.hypot(dx, dy), osuu = ruiskuttaa && Wk && d < kantama && Math.abs(kulma(Math.atan2(dx, dy) - Wk.yaw)) < 0.32;
        if (osuu && g.tila !== 'liukas' && g.tila !== 'pakenee') { g.marka += dt * 0.9; if (g.marka >= 1) { g.tila = 'liukas'; g.t = 1.3; if (G.toast) G.toast('💦 Vartija liukastui!', 1.2); } }
        if (g.tila === 'menee') { const t = g.ovi, ex = t.x - g.x, ey = t.y - g.y, e = Math.hypot(ex, ey); if (e < 0.35) g.tila = 'liimaa'; else if (!osuu) { const s = Math.min(e, 1.5 * dt); g.x += ex / e * s; g.y += ey / e * s; g.yaw = Math.atan2(ex, ey); } }
        else if (g.tila === 'liimaa') { g.yaw = Math.PI; if (!osuu) g.ovi.p = Math.min(1, g.ovi.p + dt / (p.tarraS || 9)); }
        else if (g.tila === 'liukas') { g.t -= dt; if (g.t <= 0) g.tila = 'pakenee'; }
        else if (g.tila === 'pakenee') { const ex = g.pako.x - g.x, ey = g.pako.y - g.y, e = Math.hypot(ex, ey); if (e < 1) g.tila = 'poissa'; else { const s = Math.min(e, 4.6 * dt); g.x += ex / e * s; g.y += ey / e * s; g.yaw = Math.atan2(ex, ey); } }
      }
      for (const o of V.ovet) o.m.material.opacity = o.p >= 1 ? 1 : o.p * 0.7;
      npcLista = V.g.filter(g => g.tila !== 'poissa').map(g => ({ id: g.id, h: 'VARTIJA', malli: g.malli, x: g.x, y: g.y, suunta: g.yaw * 180 / Math.PI, anim: g.tila === 'pakenee' ? 'Run' : g.tila === 'menee' ? 'Walk' : 'Idle' }));
      npcPaivita(dt, w);
      const tarroja = V.ovet.filter(o => o.p >= 1).length;
      api.mittari({ teksti: `💦 Vartijoita pihalla ${jaljella}/${V.g.length} · tarroja ovissa ${tarroja}/${V.ovet.length}` });
      if (tarroja >= V.ovet.length) return 'epaonnistui';
      if (!jaljella) return 'valmis';
      return null;
    },
    loppu() { if (V.suihku) { G.scene.remove(V.suihku); V.suihku.geometry.dispose(); V.suihku = null; }
      for (const o of V.ovet) { G.scene.remove(o.m); o.m.geometry.dispose(); } V.ovet = []; V.g = []; npcLista = []; NPC.aseta([]); X.pohjassa = false;
      if (V.api) V.api.emit('kehote', null); letkuPois(); }
  };

  // ---------------------------------------------------------------- drooni
  // param: { paikka (työmaa), taulut: [[x, y], ...], akku (s), tormayksia, nopeus (m/s) }
  const D = { m: null, x: 0, y: 0, z: 0, yaw: 0, vx: 0, vy: 0, vz: 0, akku: 0, kuvat: 0, osumat: 0, suoja: 0, kotiin: null, taulut: [], kuvaa: 0 };
  let tyomaa = null;
  const tauluTex = i => { const c = document.createElement('canvas'); c.width = 512; c.height = 320; const x = c.getContext('2d');
    x.fillStyle = '#f2f0ea'; x.fillRect(0, 0, 512, 320); x.fillStyle = '#1b2a4a'; x.fillRect(0, 0, 512, 52); x.fillStyle = '#fff'; x.font = 'bold 30px sans-serif'; x.fillText('VARJO HOLDINGS', 18, 37);
    x.fillStyle = '#1b2a4a'; x.font = 'bold 26px sans-serif'; x.fillText(['KAUPPAKESKUS PORI – TORI', 'RANTAPUISTOT – PYSÄKÖINTI', 'KIRJURINLUOTO – LIIKETILAT'][i % 3], 18, 92);
    x.strokeStyle = '#3d6fb6'; x.lineWidth = 4; for (let k = 0; k < 6; k++) x.strokeRect(30 + k * 75, 120 + (k % 2) * 40, 64, 150 - (k % 2) * 40);
    x.fillStyle = '#c0392b'; x.font = 'bold 22px sans-serif'; x.fillText('LUOTTAMUKSELLINEN', 280, 300);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; };
  function rakennaTyomaa(p, api) {
    if (tyomaa) return tyomaa; const g = nm(new THREE.Group()); g.name = 'varjo-tyomaa'; const keski = api.paikka(p.paikka || 'LOC_VARJOTORNI');
    const teras = new THREE.MeshStandardMaterial({ color: 0xf2b531, roughness: 0.6, metalness: 0.3 }), puu = new THREE.MeshStandardMaterial({ color: 0x8b6a45, roughness: 0.9 });
    const taulut = (p.taulut || []).map((c, i) => { const x = c[0], y = c[1], z0 = Math.max(varmaMaa(x, y), G.bldTopAt(x, y)), m = nm(new THREE.Mesh(new THREE.PlaneGeometry(4.2, 2.6), new THREE.MeshStandardMaterial({ map: tauluTex(i), roughness: 0.8, side: THREE.DoubleSide })));
      const yaw = Math.atan2(keski.x - x, keski.y - y) + Math.PI;     // taulu katsoo työmaan keskeltä poispäin (drooni tulee ulkoa)
      m.position.set(x, z0 + 2.9, -y); m.rotation.y = -yaw + Math.PI; g.add(m);
      for (const s of [-1.7, 1.7]) { const tp = nm(new THREE.Mesh(new THREE.BoxGeometry(0.12, 4.2, 0.12), puu)); tp.position.set(x + Math.cos(yaw) * s, z0 + 2.1, -(y - Math.sin(yaw) * s)); g.add(tp); }
      return { x, y, z: z0 + 2.9, nx: Math.sin(yaw + Math.PI), ny: Math.cos(yaw + Math.PI), kuvattu: false }; });
    // kaksi tornin nosturia: masto ja puomi (törmäyskohteet)
    const nosturit = [[-22, -12, 0.6], [24, 6, 2.4]].map(([dx, dy, a]) => { const x = keski.x + dx, y = keski.y + dy, z0 = varmaMaa(x, y), H = 42, L = 38;
      const masto = nm(new THREE.Mesh(new THREE.BoxGeometry(1.6, H, 1.6), teras)); masto.position.set(x, z0 + H / 2, -y); g.add(masto);
      const puomi = nm(new THREE.Mesh(new THREE.BoxGeometry(L, 1.2, 1.2), teras)); const cx = x + Math.sin(a) * (L / 2 - 8), cy = y + Math.cos(a) * (L / 2 - 8); puomi.position.set(cx, z0 + H, -cy); puomi.rotation.y = -(a - Math.PI / 2); g.add(puomi);
      const vasta = nm(new THREE.Mesh(new THREE.BoxGeometry(3, 2.4, 2), new THREE.MeshStandardMaterial({ color: 0x777777 }))); vasta.position.set(x - Math.sin(a) * 7, z0 + H - 0.4, -(y - Math.cos(a) * 7)); g.add(vasta);
      const koppi = nm(new THREE.Mesh(new THREE.BoxGeometry(2.2, 2, 2.2), new THREE.MeshStandardMaterial({ color: 0xdddddd }))); koppi.position.set(x, z0 + H - 2.2, -y); g.add(koppi);
      return { x, y, z0, H, a, L, ax: x - Math.sin(a) * 8, ay: y - Math.cos(a) * 8, bx: x + Math.sin(a) * (L - 8), by: y + Math.cos(a) * (L - 8) }; });
    G.scene.add(g); tyomaa = { g, taulut, nosturit }; return tyomaa;
  }
  function droonimalli() {
    const g = new THREE.Group(), musta = new THREE.MeshStandardMaterial({ color: 0x1d1f22, roughness: 0.5, metalness: 0.4 }), harmaa = new THREE.MeshStandardMaterial({ color: 0x55595f, roughness: 0.5 });
    const runko = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.08, 0.3), musta); g.add(runko);
    D.roottorit = [];
    for (const [sx, sz] of [[1, 1], [-1, 1], [1, -1], [-1, -1]]) { const v = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.03, 0.3), harmaa); v.position.set(sx * 0.11, 0, sz * 0.11); v.rotation.y = sx * sz > 0 ? -Math.PI / 4 : Math.PI / 4; g.add(v);
      const r = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.006, 16), new THREE.MeshBasicMaterial({ color: 0x99a0a8, transparent: true, opacity: 0.45 })); r.position.set(sx * 0.21, 0.05, sz * 0.21); g.add(r); D.roottorit.push(r); }
    const kam = new THREE.Mesh(new THREE.SphereGeometry(0.045, 12, 8), harmaa); kam.position.set(0, -0.06, -0.12); g.add(kam);
    const valo = new THREE.Mesh(new THREE.SphereGeometry(0.02, 8, 6), new THREE.MeshBasicMaterial({ color: 0xff3030 })); valo.position.set(0, 0.05, 0.15); g.add(valo); D.valo = valo;
    g.scale.setScalar(1.6); return nm(g);
  }
  const vilkku = (() => { let el = null; return (vari = '#fff') => { if (!el) { el = document.createElement('div'); el.style.cssText = 'position:fixed;inset:0;pointer-events:none;opacity:0;transition:opacity .35s;z-index:60'; document.body.appendChild(el); }
    el.style.background = vari; el.style.transition = 'none'; el.style.opacity = 0.75; requestAnimationFrame(() => { el.style.transition = 'opacity .45s'; el.style.opacity = 0; }); }; })();
  const kamPos = new THREE.Vector3(), kamKatse = new THREE.Vector3(), t1 = new THREE.Vector3();
  const segD = (px, py, ax, ay, bx, by) => { const dx = bx - ax, dy = by - ay, L2 = dx * dx + dy * dy || 1, t = Math.max(0, Math.min(1, ((px - ax) * dx + (py - ay) * dy) / L2)); return Math.hypot(ax + dx * t - px, ay + dy * t - py); };
  const drooni = {
    alku(p, api) {
      const T = rakennaTyomaa(p, api); for (const t of T.taulut) t.kuvattu = false;
      const w = window.__walk && window.__walk.on ? window.__walk : (window.__car || window.__walk); D.kotiin = { x: w.x, y: w.y }; D.x = w.x + Math.sin(w.yaw) * 1.5; D.y = w.y + Math.cos(w.yaw) * 1.5; D.z = varmaMaa(D.x, D.y) + 1.6; D.yaw = w.yaw; D.vx = D.vy = D.vz = 0;
      D.akku = p.akku || 150; D.kuvat = 0; D.osumat = 0; D.suoja = 0; D.kuvaa = 0; D.vmax = p.nopeus || 24;
      if (!D.m) D.m = droonimalli(); G.scene.add(D.m);
      kamPos.set(D.x - Math.sin(D.yaw) * 4, D.z + 1.6, -(D.y - Math.cos(D.yaw) * 4)); kamKatse.set(D.x, D.z, -D.y);
      window.__syoteLukko = true;
      window.__kameraKoukku = (cam, dt) => { const sn = Math.sin(D.yaw), cs = Math.cos(D.yaw);
        t1.set(D.x - sn * 4.2, D.z + 1.5, -(D.y - cs * 4.2)); kamPos.lerp(t1, 1 - Math.exp(-dt * 6)); t1.set(D.x + sn * 6, D.z, -(D.y + cs * 6)); kamKatse.lerp(t1, 1 - Math.exp(-dt * 8));
        cam.position.copy(kamPos); cam.lookAt(kamKatse); return true; };
      api.vihje('Drooni: W/S eteen–taakse, A/D käänny, Q/E sivulle, Välilyönti ylös, Shift alas. Kuvaa taulu leijumalla sen edessä.');
    },
    paivita(dt, w, p, api) {
      const K = G.keys, k = c => K.has(c) ? 1 : 0, T = tyomaa;
      const f = k('KeyW') + k('ArrowUp') - k('KeyS') - k('ArrowDown'), tr = k('KeyD') + k('ArrowRight') - k('KeyA') - k('ArrowLeft'), st = k('KeyE') - k('KeyQ'), up = k('Space') + k('KeyR') - k('ShiftLeft') - k('ShiftRight');
      const tc = G.touchIn || { f: 0, t: 0, l: 0 };
      D.yaw += (tr + tc.t) * 1.9 * dt;
      const sn = Math.sin(D.yaw), cs = Math.cos(D.yaw), ff = Math.max(-1, Math.min(1, f + tc.f)), uu = Math.max(-1, Math.min(1, up + tc.l));
      D.vx += (sn * ff + cs * st) * 26 * dt; D.vy += (cs * ff - sn * st) * 26 * dt; D.vz += uu * 14 * dt;
      const dr = Math.exp(-1.6 * dt); D.vx *= dr; D.vy *= dr; D.vz *= Math.exp(-3 * dt);
      const v = Math.hypot(D.vx, D.vy); if (v > D.vmax) { D.vx *= D.vmax / v; D.vy *= D.vmax / v; } D.vz = Math.max(-7, Math.min(7, D.vz));
      let nx = D.x + D.vx * dt, ny = D.y + D.vy * dt, nz = Math.min(140, D.z + D.vz * dt);
      // törmäykset: maa, talot, nosturit
      const pinta = Math.max(varmaMaa(nx, ny), G.bldTopAt(nx, ny));
      let osui = nz < pinta + 0.25;
      if (T) for (const c of T.nosturit) { if (Math.hypot(nx - c.x, ny - c.y) < 1.4 && nz < c.z0 + c.H + 1) osui = true; if (Math.abs(nz - (c.z0 + c.H)) < 1.3 && segD(nx, ny, c.ax, c.ay, c.bx, c.by) < 1.2) osui = true; }
      if (osui) { const nopea = Math.hypot(D.vx, D.vy, D.vz) > 3.5; D.vx *= -0.4; D.vy *= -0.4; D.vz = Math.abs(D.vz) * 0.4 + 1;
        if (nz < pinta + 0.25) nz = pinta + 0.3; nx = D.x; ny = D.y;
        if (nopea && D.suoja <= 0) { D.osumat++; D.suoja = 1.2; vilkku('#ff5252'); if (G.toast) G.toast(`Drooni kolahti! (${D.osumat}/${p.tormayksia || 3})`, 1.4); } }
      D.suoja -= dt; D.x = nx; D.y = ny; D.z = nz;
      D.akku -= dt;
      // kuvaus: leiju taulun edessä (alle 14 m, edessä, kamera taulua kohti) 1,2 s
      let kohde = null; if (T) for (const t of T.taulut) { if (t.kuvattu) continue; const dx = D.x - t.x, dy = D.y - t.y, d = Math.hypot(dx, dy) + Math.max(0, Math.abs(D.z - t.z) - 8);      // 8 m korkeuseroa sallitaan
        const edessa = (dx * t.nx + dy * t.ny) > 1.5, katsoo = Math.abs(kulma(Math.atan2(t.x - D.x, t.y - D.y) - D.yaw)) < 0.7; if (d < 16 && edessa && katsoo) { kohde = t; break; } }
      if (kohde) { D.kuvaa += dt; if (D.kuvaa > 1.2) { kohde.kuvattu = true; D.kuvat++; D.kuvaa = 0; vilkku('#ffffff'); if (G.toast) G.toast(`📸 Kuva ${D.kuvat}/${T.taulut.length}`, 1.4); } } else D.kuvaa = Math.max(0, D.kuvaa - dt);
      // malli
      D.m.position.set(D.x, D.z, -D.y); D.m.rotation.set(0, -D.yaw, 0, 'YXZ'); D.m.rotation.x = -ff * 0.25; D.m.rotation.z = -(tr + st) * 0.15;
      for (const r of D.roottorit) r.rotation.y += dt * 60; D.valo.visible = Math.sin(performance.now() / 160) > 0;
      // pelaaja seisoo paikallaan ohjain kädessä
      const Wk = window.__walk; if (Wk) { Wk.v = 0; Wk.vs = 0; }
      const kaikki = T ? T.taulut.length : 3, kotona = D.kuvat >= kaikki && Math.hypot(D.x - D.kotiin.x, D.y - D.kotiin.y) < 8 && D.z < varmaMaa(D.x, D.y) + 10;
      api.mittari({ teksti: `🔋 ${Math.max(0, Math.ceil(D.akku))} s · 📸 ${D.kuvat}/${kaikki}${D.kuvaa > 0 ? ' · kuvataan…' : ''}${D.kuvat >= kaikki ? ' · palaa Ramin luo' : ''} · 💥 ${D.osumat}/${p.tormayksia || 3}` });
      if (D.osumat >= (p.tormayksia || 3)) return { epaonnistui: 'Drooni kolahti liian monta kertaa.' };
      if (D.akku <= 0) return 'epaonnistui';
      if (kotona) return 'valmis';
      return null;
    },
    loppu() { if (D.m) G.scene.remove(D.m); window.__syoteLukko = false; window.__kameraKoukku = null; },
    merkit(p) { if (!tyomaa) return []; const r = tyomaa.taulut.filter(t => !t.kuvattu).map(t => ({ x: t.x + t.nx * 6, y: t.y + t.ny * 6, r: 3, laji: 'kohde', nimi: 'Taulu' }));
      if (!r.length && D.kotiin) r.push({ x: D.kotiin.x, y: D.kotiin.y, r: 6, laji: 'tavoite', nimi: 'Rami' }); return r; }
  };
  // kohde-merkki hiiviskelylle (toimiston ovi)
  hiiviskely.merkit = p => { const T = window.__tarina; const q = T && T.moottori && T.moottori.paikka(p.kohde); return q ? [{ ...q, r: p.r || 2.5, laji: 'tavoite', nimi: 'Toimisto' }] : []; };
  return { hiiviskely, vesiletku, drooni, _tila: { H, V, D } };      // _tila: testit (node)
}
