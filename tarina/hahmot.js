// Satamakaupunki – tarinan hahmot pelimaailmaan. Moottori kertoo 'hahmot'-tapahtumalla, kuka seisoo missä (tehtävädatan `hahmot`,
// `antaja`, data/maailma.json); tämä tiedosto lataa mallit (repon juuren npc_*.js, sama muoto kuin pelin kävelijöillä: base64-GLB,
// klipit Idle/Walk/Run/Dance…) ja pitää ne paikallaan, kääntää puhujan pelaajaa kohti ja soittaa Idle-animaatiota.
// Mallin puuttuessa (data/hahmot.json malli: null) hahmo vain puhuu ruudulla. Sijoituksen `malli` ohittaa hahmon oletusmallin
// (vartijan muunnelmat B ja C), ja `mene` + `nopeus` panee hahmon kävelemään tai juoksemaan kohteeseen, jossa se katoaa.

import * as THREE from '../three.module.min.js';
import { GLTFLoader } from '../GLTFLoader.js';

const NAKYY = 260;        // m: kauempana hahmo piilotetaan
const ANIMOI = 120;       // m: mikseri päivitetään vain lähellä
const KAANTO = 4;         // rad/s: kääntymisnopeus pelaajaa kohti

// Suun paikka mallin sidosasennossa (m): [suuviiva y, leuan kärki y]. Mitattu 21.11.2026 kasvojen lähikuvista senttiviivaimella
// (tools/hahmo/rigaa: uusi malli → mittaa uudestaan, muuten suu ei liiku). Malleissa ei ole leukaluuta eikä suun sisusta, joten puhe on
// muodonmuutos (morph): leuka ja alahuuli valuvat alas ja maalattu suuviiva venyy auki.
const SUU = { npc_tapsa: [1.490, 1.450], npc_lumi: [1.428, 1.393], npc_terttu: [1.318, 1.285], npc_varjo: [1.657, 1.609], npc_vartija: [1.541, 1.499],
  npc_myyja: [1.461, 1.421], npc_harju: [1.574, 1.522], npc_kuriiri: [1.546, 1.509], npc_vartija_b: [1.451, 1.415], npc_vartija_c: [1.518, 1.483] };
const pehmea = (a, b, x) => { const t = Math.max(0, Math.min(1, (x - a) / (b - a))); return t * t * (3 - 2 * t); };

export function teeSuu(root, malli) {
  const m = SUU[malli]; if (!m) return null; let mesh = null; root.traverse(o => { if (o.isSkinnedMesh && !mesh) mesh = o; }); if (!mesh) return null;
  const [ys, yl] = m, p = mesh.geometry.attributes.position, n = p.count, d = new Float32Array(n * 3), A = Math.min(0.011, (ys - yl) * 0.3);
  let ze = -1e9; for (let i = 0; i < n; i++) { const y = p.getY(i); if (y < ys && y > yl && Math.abs(p.getX(i)) < 0.03) ze = Math.max(ze, p.getZ(i)); }
  let k = 0;
  for (let i = 0; i < n; i++) { const x = Math.abs(p.getX(i)), y = p.getY(i), z = p.getZ(i); if (y > ys || y < yl - 0.02 || x > 0.065 || z < ze - 0.07) continue;
    const w = pehmea(ys, ys - 0.005, y) * pehmea(yl - 0.02, yl + 0.004, y) * pehmea(0.065, 0.03, x) * pehmea(ze - 0.07, ze - 0.035, z); if (w < 0.002) continue;
    d[i * 3 + 1] = -A * w; d[i * 3 + 2] = -A * 0.3 * w; k++; }
  if (k < 8) return null;
  mesh.geometry.morphAttributes.position = [new THREE.Float32BufferAttribute(d, 3)]; mesh.geometry.morphTargetsRelative = true; mesh.updateMorphTargets(); mesh.morphTargetInfluences = [0];
  // suuaukko: tumma soikio suuviivan alle kasvojen pintaan (pään luun lapsena), korkeus kasvaa suun auetessa – näkyy myös kauempaa
  let aukko = null; const bi = mesh.skeleton.bones.findIndex(b => b.name === 'head');
  if (bi >= 0) {
    const hw = Math.min(0.02, (ys - yl) * 0.5), hh = A * 0.95, S = 14, R = 3, pv = [], ix = [];
    const pinta = (x, y) => { let z = -1e9; for (let i = 0; i < n; i++) { const dx = p.getX(i) - x, dy = p.getY(i) - y; if (dx * dx + dy * dy < 0.00005 && p.getZ(i) > z) z = p.getZ(i); } return z; };
    const z0 = pinta(0, ys - hh * 0.4);
    if (z0 > -1e8) {
      for (let r = 0; r <= R; r++) for (let c = 0; c <= S; c++) { const u = c / S * 2 - 1, v = r / R, x = u * hw, y = -v * Math.sqrt(Math.max(0, 1 - u * u)); let z = pinta(x, ys + y * hh); if (z < z0 - 0.012) z = z0 - 0.012; pv.push(x, y, z + 0.0012); }
      for (let r = 0; r < R; r++) for (let c = 0; c < S; c++) { const a = r * (S + 1) + c; ix.push(a, a + S + 1, a + 1, a + 1, a + S + 1, a + S + 2); }
      const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pv, 3)); g.setIndex(ix);
      const mat = new THREE.MeshBasicMaterial({ color: 0x2e0f0c, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 }); mat.userData.noT = true;
      aukko = new THREE.Mesh(g, mat); aukko.userData.noT = true; aukko.frustumCulled = false; aukko.visible = false; aukko.userData.hh = hh; aukko.position.y = ys;
      const kanta = new THREE.Group(); kanta.matrixAutoUpdate = false; kanta.matrix.copy(mesh.skeleton.boneInverses[bi]); kanta.userData.noT = true; kanta.add(aukko); mesh.skeleton.bones[bi].add(kanta);
    }
  }
  return { mesh, aukko, aseta(v) { mesh.morphTargetInfluences[0] = v; if (aukko) { aukko.visible = v > 0.06; aukko.scale.y = Math.max(0.001, v) * aukko.userData.hh; } } };
}

const _q = new THREE.Quaternion(), _p = new THREE.Quaternion(), _a = new THREE.Vector3(), AX = new THREE.Vector3(1, 0, 0), AY = new THREE.Vector3(0, 1, 0), AZ = new THREE.Vector3(0, 0, 1);
// luun kierto hahmon omien akselien ympäri (x = vasemmalle, y = ylös, z = eteen) klipin asennon päälle; +x = nyökkäys eteen
function kierra(root, luu, akseli, kulma) {
  if (!luu || Math.abs(kulma) < 1e-4) return; _q.setFromAxisAngle(_a.copy(akseli).applyQuaternion(root.quaternion), kulma);
  luu.parent.getWorldQuaternion(_p); luu.quaternion.premultiply(_q.multiply(_p)).premultiply(_p.invert());
}
// Elehdintä keskustelussa: puhuja liikuttaa suuta, nyökkää, kääntää päätä ja viittoo käsillä; kuulijat nyökkäilevät ja vaihtavat painoa.
export function elehdi(e, dt, puhuu, kuulee, suuAuki) {
  e.pa += ((puhuu ? 1 : 0) - e.pa) * Math.min(1, dt * 5); e.ka += ((kuulee ? 1 : 0) - e.ka) * Math.min(1, dt * 3); e.sa += ((suuAuki ? 1 : 0) - e.sa) * Math.min(1, dt * 12);
  e.et += dt; const t = e.et, f = e.vaihe, pa = e.pa, ka = e.ka, L = e.luut, r = e.root;
  if (e.suu) e.suu.aseta(e.sa * (Math.sin(t * 1.9 + f) > -0.75 ? 1 : 0) * Math.min(1, 0.12 + 0.88 * Math.abs(Math.sin(t * 9.5 + f)) * (0.6 + 0.4 * Math.sin(t * 3.1 + f * 2))));
  // AnimationMixer kirjoittaa luun asennon vain, kun klipin arvo muuttuu → edellisen ruudun ele perutaan ensin, muuten kierrot kasautuvat
  for (const k in L) { const b = L[k]; if (!b) continue; const u = b.userData; if (u.eleM && b.quaternion.equals(u.eleM)) b.quaternion.copy(u.eleP); u.eleM = null; }
  if (pa < 0.01 && ka < 0.01) return;
  for (const k in L) { const b = L[k]; if (b) (b.userData.eleP || (b.userData.eleP = new THREE.Quaternion())).copy(b.quaternion); }
  const nyok = Math.max(0, Math.sin(t * 2.7 + f)) ** 2 * (Math.sin(t * 0.45 + f * 3) > 0.2 ? 1 : 0);      // kuulijan nyökkäyssarja silloin tällöin
  kierra(r, L.spine, AY, pa * 0.07 * Math.sin(t * 0.9 + f) + ka * 0.03 * Math.sin(t * 0.5 + f)); kierra(r, L.spine, AZ, (pa * 0.02 + ka * 0.025) * Math.sin(t * 0.7 + f * 2)); kierra(r, L.spine, AX, pa * 0.03 * Math.sin(t * 1.7 + f));
  kierra(r, L.head, AX, pa * (0.05 * Math.sin(t * 5.1 + f) + 0.04 * Math.sin(t * 2.3)) + ka * 0.09 * nyok); kierra(r, L.head, AY, pa * 0.1 * Math.sin(t * 1.3 + f) + ka * 0.04 * Math.sin(t * 0.6 + f * 2)); kierra(r, L.head, AZ, pa * 0.04 * Math.sin(t * 1.1 + f * 2));
  const go = pa * pehmea(-0.2, 0.7, Math.sin(t * 1.15 + f)), gv = pa * pehmea(0.1, 0.9, Math.sin(t * 0.8 + f * 1.7 + 2));      // oikea ja vasen käsi nousevat vuorotellen
  kierra(r, L.oa, AX, -go * (0.22 + 0.05 * Math.sin(t * 6.1))); kierra(r, L.ok, AX, -go * (0.95 + 0.14 * Math.sin(t * 6.1 + f))); kierra(r, L.ok, AY, go * 0.25);
  kierra(r, L.va, AX, -gv * 0.15); kierra(r, L.vk, AX, -gv * (0.6 + 0.1 * Math.sin(t * 5.3 + f))); kierra(r, L.vk, AY, -gv * 0.2);
  for (const k in L) { const b = L[k]; if (b) b.userData.eleM = (b.userData.eleT || (b.userData.eleT = new THREE.Quaternion())).copy(b.quaternion); }
}

export function luoHahmot(scene, { hahmot = {}, korkeus = () => 0 } = {}) {
  const puskurit = {};    // malli → Promise<ArrayBuffer> (yksi lataus per malli, jokainen hahmo jäsennetään omakseen: luurangot eivät jaa)
  const elossa = new Map();   // id → { h, root, mixer, x, y, suunta, yaw, lataa }
  let puhuja = null, hiljaa = false;   // hiljaa = toimintarivi ([hakasulkeissa]): eleet ilman suun liikettä

  function puskuri(malli) {
    if (!puskurit[malli]) puskurit[malli] = import(`../${malli}.js`).then(K => {
      const bin = atob(K.default), buf = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i); return buf.buffer;
    });
    return puskurit[malli];
  }

  function luo(id, q) {
    const malli = q.malli || (hahmot[q.h] || {}).malli; if (!malli) return null;
    const e = { h: q.h, x: q.x, y: q.y, suunta: q.suunta, anim: q.anim, yaw: null, root: null, mixer: null, poistettu: false, pa: 0, ka: 0, sa: 0, et: 0, vaihe: Math.random() * 6.28, luut: {}, suu: null, kohde: q.mx !== undefined ? { x: q.mx, y: q.my } : null, nopeus: q.nopeus || 1.4, poissa: false };
    if (e.kohde && (!q.anim || q.anim === 'Idle')) e.anim = e.nopeus > 2.4 ? 'Run' : 'Walk';
    puskuri(malli).then(buf => new Promise((ok, ei) => new GLTFLoader().parse(buf.slice(0), '', ok, ei))).then(gl => {
      if (e.poistettu) return;
      const root = gl.scene;
      root.traverse(o => { o.userData.noT = true; if (o.isMesh) { o.frustumCulled = false; o.castShadow = false; if (o.material) o.material.userData.noT = true; } });
      root.userData.noT = true; root.name = 'tarina-hahmo-' + q.h;
      e.root = root; e.mixer = new THREE.AnimationMixer(root); e.klipit = gl.animations;
      const luu = n => root.getObjectByName(n); e.luut = { head: luu('head'), spine: luu('spine_02'), oa: luu('upperarm_r'), ok: luu('lowerarm_r'), va: luu('upperarm_l'), vk: luu('lowerarm_l') };
      try { e.suu = teeSuu(root, malli); } catch (err) { console.warn('[tarina] suun muodonmuutos ei onnistunut', malli, err); }
      soita(e, e.anim || 'Idle'); asetaPaikka(e); scene.add(root);
    }).catch(err => console.warn('[tarina] hahmon malli ei latautunut', q.h, malli, err));
    return e;
  }

  function soita(e, nimi) {
    if (!e.mixer) return; const c = e.klipit.find(a => a.name === nimi) || e.klipit.find(a => a.name === 'Idle'); if (!c) return;
    if (e.act) e.act.fadeOut(0.25);
    e.act = e.mixer.clipAction(c); e.act.reset().fadeIn(0.25).play(); e.act.time = Math.random() * c.duration;   // eri vaiheissa, ei synkassa
  }

  function asetaPaikka(e) { if (e.root) e.root.position.set(e.x, korkeus(e.x, e.y), -e.y); }

  // lista moottorilta: lisää uudet, poista puuttuvat, siirrä muuttuneet
  function aseta(lista) {
    const uudet = new Set(lista.map(q => q.id));
    for (const [id, e] of elossa) if (!uudet.has(id)) { e.poistettu = true; if (e.root) scene.remove(e.root); elossa.delete(id); }
    for (const q of lista) {
      const e = elossa.get(q.id);
      if (!e) { const n = luo(q.id, q); if (n) elossa.set(q.id, n); continue; }
      if (!e.kohde && (e.x !== q.x || e.y !== q.y)) { e.x = q.x; e.y = q.y; asetaPaikka(e); }
      if (!e.kohde) e.suunta = q.suunta; if (q.anim && q.anim !== e.anim) { e.anim = q.anim; soita(e, q.anim); }
    }
  }

  // yaw: kartan suunta (0 = pohjoinen, myötäpäivään). glTF katsoo +z:aan → kierto y = π − yaw (sama kuin pelin kävelijät)
  function paivita(dt, pelaaja) {
    // samaa hahmoa voi olla monta (kolme vartijaa): äänessä on niistä pelaajaa lähin, muut kuuntelevat
    let aanessa = null, ad = 1e9; if (puhuja) for (const e of elossa.values()) if (e.h === puhuja && e.root && !e.kohde) { const d = pelaaja ? Math.hypot(pelaaja.x - e.x, pelaaja.y - e.y) : 0; if (d < ad) { ad = d; aanessa = e; } }
    for (const e of elossa.values()) {
      if (!e.root) continue;
      const d = pelaaja ? Math.hypot(pelaaja.x - e.x, pelaaja.y - e.y) : 0;
      // liikkuva hahmo (sijoituksen `mene`): suoraan kohteeseen Walk/Run-klipillä, perillä pois näkyvistä (esim. kuriiri, joka katoaa)
      if (e.kohde && !e.poissa) {
        const kx = e.kohde.x - e.x, ky = e.kohde.y - e.y, km = Math.hypot(kx, ky), askel = e.nopeus * dt;
        if (km <= askel) { e.x = e.kohde.x; e.y = e.kohde.y; e.poissa = true; }
        else { e.x += kx / km * askel; e.y += ky / km * askel; e.suunta = Math.atan2(kx, ky) * 180 / Math.PI; }
        asetaPaikka(e);
      }
      e.root.visible = d < NAKYY && !e.poissa; if (!e.root.visible) continue;
      let tavoite;
      if (pelaaja && !e.kohde && (e.suunta === 'pelaaja' || puhuja === e.h) && d > 0.5 && d < 40) tavoite = Math.atan2(pelaaja.x - e.x, pelaaja.y - e.y);
      else if (typeof e.suunta === 'number') tavoite = e.suunta * Math.PI / 180;
      if (tavoite !== undefined) {
        if (e.yaw === null) e.yaw = tavoite;
        let ero = ((tavoite - e.yaw + Math.PI * 3) % (Math.PI * 2)) - Math.PI;
        e.yaw += Math.max(-KAANTO * dt, Math.min(KAANTO * dt, ero));
      }
      if (e.yaw !== null) e.root.rotation.y = Math.PI - e.yaw;
      if (d < ANIMOI && e.mixer) { e.mixer.update(dt); if (!e.kohde) elehdi(e, dt, e === aanessa, !!puhuja && e !== aanessa && d < 30, e === aanessa && !hiljaa); }
    }
  }

  return {
    aseta, paivita,
    puhuu(h, toiminta) { puhuja = h || null; hiljaa = !!toiminta; },
    get lista() { return [...elossa.entries()].map(([id, e]) => ({ id, h: e.h, x: e.x, y: e.y, ladattu: !!e.root })); }
  };
}
