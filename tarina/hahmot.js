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

export function luoHahmot(scene, { hahmot = {}, korkeus = () => 0 } = {}) {
  const puskurit = {};    // malli → Promise<ArrayBuffer> (yksi lataus per malli, jokainen hahmo jäsennetään omakseen: luurangot eivät jaa)
  const elossa = new Map();   // id → { h, root, mixer, x, y, suunta, yaw, lataa }
  let puhuja = null;

  function puskuri(malli) {
    if (!puskurit[malli]) puskurit[malli] = import(`../${malli}.js`).then(K => {
      const bin = atob(K.default), buf = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i); return buf.buffer;
    });
    return puskurit[malli];
  }

  function luo(id, q) {
    const malli = q.malli || (hahmot[q.h] || {}).malli; if (!malli) return null;
    const e = { h: q.h, x: q.x, y: q.y, suunta: q.suunta, anim: q.anim, yaw: null, root: null, mixer: null, poistettu: false, kohde: q.mx !== undefined ? { x: q.mx, y: q.my } : null, nopeus: q.nopeus || 1.4, poissa: false };
    if (e.kohde && (!q.anim || q.anim === 'Idle')) e.anim = e.nopeus > 2.4 ? 'Run' : 'Walk';
    puskuri(malli).then(buf => new Promise((ok, ei) => new GLTFLoader().parse(buf.slice(0), '', ok, ei))).then(gl => {
      if (e.poistettu) return;
      const root = gl.scene;
      root.traverse(o => { o.userData.noT = true; if (o.isMesh) { o.frustumCulled = false; o.castShadow = false; if (o.material) o.material.userData.noT = true; } });
      root.userData.noT = true; root.name = 'tarina-hahmo-' + q.h;
      e.root = root; e.mixer = new THREE.AnimationMixer(root); e.klipit = gl.animations;
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
      if (d < ANIMOI && e.mixer) e.mixer.update(dt);
    }
  }

  return {
    aseta, paivita,
    puhuu(h) { puhuja = h || null; },
    get lista() { return [...elossa.entries()].map(([id, e]) => ({ id, h: e.h, x: e.x, y: e.y, ladattu: !!e.root })); }
  };
}
