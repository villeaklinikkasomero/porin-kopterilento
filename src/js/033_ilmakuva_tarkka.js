// ---------- sharper aerial photo near the helicopter: 512 m tiles at 0.25 m/px (Porin kaupunki WMS), loaded by distance ----------
// 0.25 m/px tiles over the centre (i 0..5, j 0..4), 0.33 m/px tiles over the rest of the map (i -3..7, j -1..6)
const HR = { S: 512, X0: -1280, Y0: -1280, I0: -3, I1: 7, J0: -5, J1: 6,      /* J -2..-5: only i 0..4 (the airport, 20.11.2026) */
  t: new Map(), loader: new THREE.TextureLoader(), last: -1e9 };
// 21.11.2026: laatat ja katot sävykorjattuina maa/ot_s/ (tools/maa/orto_savy.py, omistaja hyväksyi); alkuperäiset ot/ ennallaan. Maan materiaali lähellä: maa/maa.js (0337)
const ROOFT = new Map();   // aerial tile key -> roof meshes that switch to that tile's texture
function roofTile(k, tex) {
  for (const me of ROOFT.get(k) || []) {
    if (me.material !== me.userData.fb) { if (me.material.map) me.material.map.dispose(); me.material.dispose(); }
    if (tex) { const t = tex.clone(); t.channel = 1; t.needsUpdate = true; me.material = me.userData.maa ? groundTileMat(t) : new THREE.MeshBasicMaterial({ map: t, side: THREE.DoubleSide }); }      // maa: tienleikkaus (031 roadCut)
    else me.material = me.userData.fb;
  }
}
// ladattujen laattojen suorakaiteet 030:n ulkokehän shaderille (ulkokehä ei peitä tarkkaa maata koverissa kohdissa)
function hrOuter() { let n = 0; for (const [k, e] of HR.t) { if (!e.ok || n >= 24) continue; const [i, j] = k.split('_').map(Number);
    OUTER_HR.u.value[n++].set(HR.X0 + i * HR.S, HR.Y0 + j * HR.S, HR.X0 + (i + 1) * HR.S, HR.Y0 + (j + 1) * HR.S); } OUTER_HR.n.value = n; }
function hrUpdate(x, y) {
  for (let i = HR.I0; i <= HR.I1; i++) for (let j = HR.J0; j <= HR.J1; j++) { if (j < -1 && (i < 0 || i > 4)) continue;
    const k = i + '_' + j, cx = HR.X0 + (i + 0.5) * HR.S, cy = HR.Y0 + (j + 0.5) * HR.S, d = Math.max(Math.abs(cx - x), Math.abs(cy - y)) - HR.S / 2, e = HR.t.get(k);
    if (d < (isTouch ? 200 : 330) && !e) {
      const m = grassify(new THREE.MeshBasicMaterial({ polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2, transparent: true, opacity: 0 }));
      const x0t = cx - HR.S / 2, y0t = cy - HR.S / 2, g = gridGeo(x0t, y0t, x0t + HR.S, y0t + HR.S, 6, (x, y) => [(x - x0t) / HR.S, (y - y0t) / HR.S], tSkip, 0.03); g.translate(-cx, 0, cy);
      const me = noT(new THREE.Mesh(g, m)); me.position.set(cx, 0, -cy); me.renderOrder = -1;
      const rec = { me, m, alive: true }; HR.t.set(k, rec);
      HR.loader.load(`./maa/ot_s/ot_${i}_${j}.jpg`, tex => { if (!rec.alive) { tex.dispose(); return; } tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = renderer.capabilities.getMaxAnisotropy();
        m.map = tex; m.transparent = false; m.opacity = 1; m.needsUpdate = true; scene.add(me); roofTile(k, tex); rec.ok = true; hrOuter(); });
    } else if (e && d > (isTouch ? 380 : 520)) { roofTile(k, null); e.alive = false; e.ok = false; scene.remove(e.me); e.me.geometry.dispose(); if (e.m.map) e.m.map.dispose(); e.m.dispose(); HR.t.delete(k); hrOuter(); }
  }
}

