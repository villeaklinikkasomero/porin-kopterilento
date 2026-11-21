// moduulit/patsaat.js – siirretty pääskriptistä (src/js/150_patsaat.js) omaksi moduulikseen 21.11.2026.
// Pääskriptin muuttujat tulevat oliossa P (getterit pitävät ne ajan tasalla); kirjastot ja data tuodaan suoraan.
// Kutsu ja P:n sisältö: src/js/150_patsaat.js. Uusi riippuvuus pääskriptiin → lisää se sinne P-olioon.
import { GLTFLoader } from '../GLTFLoader.js';

// ---------- statues and memorials (19.11.2026): patsaat.js = the owner's list (21 works, Wikipedia; ten positions refined from OpenStreetMap) and his Blender
// models (origin on the ground, front +Z). A point that falls in a building or on a carriageway is moved to the nearest free spot (spiral, 30 m); with no
// heading given the work faces the nearest street.
export default function kaynnista(P) {
{
  const ST = []; window.__statues = ST;
  import('../patsaat.js').then(K => { const D = K.default, G = {}; let left = Object.keys(D.m).length;
    const place = () => { for (const k of D.k) { if (!(k.x > P.OX0 + 8 && k.x < P.OX1 - 8 && k.y > P.OY0 + 8 && k.y < P.OY1 - 8) || !G[k.m]) continue;
        let x = k.x, y = k.y; const bld = (px, py) => P.bldTopAt(px, py) > P.TZs(px, py) + 1.2, near = (px, py) => { for (let a = 0; a < 8; a++) if (bld(px + 3 * Math.sin(a * Math.PI / 4), py + 3 * Math.cos(a * Math.PI / 4))) return true; return false; };
        const bad = (px, py) => bld(px, py) || near(px, py) || P.ROAD.asphAt(px, py) || (!k.w && (P.inRiver(px, py) || P.TZs(px, py) < -2.2));   /* not in or within 3 m of a building, not on a carriageway, not in the river bed */
        if (bad(x, y)) { let f = false; for (let r = 2; r <= 30 && !f; r += 2) for (let a = 0; a < 12 && !f; a++) { const px = k.x + r * Math.sin(a * Math.PI / 6), py = k.y + r * Math.cos(a * Math.PI / 6); if (!bad(px, py) && !bad(px + 1.5, py) && !bad(px - 1.5, py) && !bad(px, py + 1.5) && !bad(px, py - 1.5)) { x = px; y = py; f = true; } } }
        let hd = k.h; if (hd === null || hd === undefined) { hd = 180; let bd = 1e9; for (let a = 0; a < 16; a++) for (let r = 3; r <= 40; r += 1.5) if (P.ROAD.asphAt(x + r * Math.sin(a * Math.PI / 8), y + r * Math.cos(a * Math.PI / 8))) { if (r < bd) { bd = r; hd = a * 22.5; } break; } }
        const g = G[k.m].clone(), z = k.w ? P.TZs(x, y) : (P.carGround(x, y) ?? P.TZs(x, y)); g.position.set(x, z, -y); g.rotation.y = Math.PI - hd * Math.PI / 180; P.scene.add(g); ST.push({ k, x, y, z, hd, g, seen: false }); } };
    const go = () => { if (!window.__roads && (go.n = (go.n || 0) + 1) < 12) { setTimeout(go, 3000); return; } place(); };
    for (const m in D.m) { const bin = atob(D.m[m]), buf = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
      new GLTFLoader().parse(buf.buffer, '', gl => { gl.scene.traverse(q => { q.userData.noT = true; if (q.isMesh && q.material) q.material.userData.noT = true;      /* placed at its own height: no terrain lift in the shader */
        if (q.isMesh && q.material && q.material.metalness !== undefined) { q.material.metalness = Math.min(q.material.metalness, 0.3); q.material.roughness = Math.max(q.material.roughness, 0.55); } }); G[m] = gl.scene; if (!--left) go(); }, () => { if (!--left) go(); }); } }).catch(() => {});
  /* 20.11.2026 (owner): no on-screen card near a statue any more (the near-statue toast was removed). */
}
}
