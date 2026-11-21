// ---------- helicopter ----------
const heli = new THREE.Group(); heli.rotation.order = 'YXZ'; heli.userData.noT = true;
let rotor, tailRotor;
{
  const yel = new THREE.MeshLambertMaterial({ color: 0xffc928 }), dark = new THREE.MeshLambertMaterial({ color: 0x1d2b3a }), glass = new THREE.MeshLambertMaterial({ color: 0x25394d, emissive: 0x16283a });
  const body = new THREE.Mesh(new THREE.SphereGeometry(1.5, 16, 12), yel); body.scale.set(1, 1, 1.9); body.position.set(0, 0, -0.4); heli.add(body);
  const nose = new THREE.Mesh(new THREE.SphereGeometry(1.32, 16, 12, 0, Math.PI * 2, 0, Math.PI * 0.62), glass); nose.rotation.x = -Math.PI / 2.25; nose.scale.set(1, 1.5, 1); nose.position.set(0, 0.22, -1.25); heli.add(nose);
  const boom = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.5, 5.6, 8), yel); boom.rotation.x = Math.PI / 2; boom.position.set(0, 0.45, 4.6); heli.add(boom);
  const fin = new THREE.Mesh(new THREE.BoxGeometry(0.14, 1.9, 1.0), dark); fin.position.set(0, 1.15, 7.2); fin.rotation.x = -0.35; heli.add(fin);
  const stab = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.1, 0.7), dark); stab.position.set(0, 0.5, 6.4); heli.add(stab);
  const mast = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.2, 0.9, 8), dark); mast.position.set(0, 1.75, -0.2); heli.add(mast);
  const eng = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.7, 2.6), dark); eng.position.set(0, 1.25, 0.5); heli.add(eng);
  rotor = new THREE.Group(); rotor.position.set(0, 2.25, -0.2);
  const bm = new THREE.MeshBasicMaterial({ color: 0x15191d, transparent: true, opacity: 0.6, side: THREE.DoubleSide });
  for (let i = 0; i < 2; i++) { const b = new THREE.Mesh(new THREE.BoxGeometry(11.6, 0.05, 0.42), bm); b.rotation.y = i * Math.PI / 2; rotor.add(b); }
  const disc = new THREE.Mesh(new THREE.CircleGeometry(5.8, 28), new THREE.MeshBasicMaterial({ color: 0x15191d, transparent: true, opacity: 0.13, side: THREE.DoubleSide, depthWrite: false })); disc.rotation.x = -Math.PI / 2; rotor.add(disc);
  heli.add(rotor);
  tailRotor = new THREE.Mesh(new THREE.BoxGeometry(0.05, 2.1, 0.22), bm); tailRotor.position.set(0.28, 1.2, 7.3); heli.add(tailRotor);
  for (const sx of [-1, 1]) {
    const skid = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.09, 4.6, 6), dark); skid.rotation.x = Math.PI / 2; skid.position.set(sx * 1.25, -1.75, -0.3); heli.add(skid);
    for (const sz of [-1.4, 0.8]) { const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.07, 1.1, 5), dark); leg.position.set(sx * 1.05, -1.3, sz); leg.rotation.z = sx * 0.35; heli.add(leg); }
  }
  scene.add(heli);
  // Blender-made helicopter replaces the simple one once loaded
  loadModel(isTouch ? 'heli_m' : 'heli', root0 => {   // Porikopteri (owner 17.11.2026): textured PBR model, nose +z, skids at y 0; the mobile file is lighter
    const root = new THREE.Group(); root.add(root0); root0.rotation.y = Math.PI; root0.position.y = -1.85;   // game frame: nose -z, skids at -1.85 (as the old model)
    // studio-like reflections for the PBR paint, glass and metal (owner 17.11: in the game it looked flat next to the Blender render): a small sky/ground
    // gradient scene turned into an environment map, used by the helicopter only - the baked city keeps its own light
    const envS = new THREE.Scene(), eg = new THREE.SphereGeometry(50, 32, 16), ec = [];
    for (let i = 0; i < eg.attributes.position.count; i++) { const y = eg.attributes.position.getY(i) / 50; const c = y > 0 ? new THREE.Color(0xbfd3e6).lerp(new THREE.Color(0xffffff), Math.max(0, 1 - y * 2.5)) : new THREE.Color(0x8a8378).lerp(new THREE.Color(0xd8d2c6), 1 + y * 3); ec.push(c.r, c.g, c.b); }
    eg.setAttribute('color', new THREE.Float32BufferAttribute(ec, 3)); envS.add(new THREE.Mesh(eg, new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.BackSide })));
    const sunB = new THREE.Mesh(new THREE.SphereGeometry(3, 12, 8), new THREE.MeshBasicMaterial({ color: new THREE.Color(8, 7.5, 6.5) })); sunB.position.set(30, 32, 24); envS.add(sunB);
    const envTex = new THREE.PMREMGenerator(renderer).fromScene(envS, 0.02).texture;
    root0.traverse(q => { if (q.isMesh) { const m = q.material; if (m) { if (m.map) m.map.anisotropy = 4; if (m.isMeshStandardMaterial) { m.envMap = envTex; m.envMapIntensity = 1.0; m.needsUpdate = true; } } q.frustumCulled = false; } });
    const nr = root0.getObjectByName('MainRotor'), nt = root0.getObjectByName('TailRotor'); if (!nr || !nt) return;
    const disc = new THREE.Mesh(new THREE.CircleGeometry(5.1, 32), new THREE.MeshBasicMaterial({ color: 0x15191d, transparent: true, opacity: 0.12, side: THREE.DoubleSide, depthWrite: false })); disc.rotation.x = -Math.PI / 2; nr.add(disc);
    heli.clear(); heli.add(root); rotor = nr; tailRotor = nt; window.__heli = true;
  });
}
// soft shadow blob under the helicopter
const blob = (() => {
  const c = document.createElement('canvas'); c.width = c.height = 64; const x = c.getContext('2d'); const g = x.createRadialGradient(32, 32, 2, 32, 32, 30);
  g.addColorStop(0, 'rgba(0,0,0,.55)'); g.addColorStop(1, 'rgba(0,0,0,0)'); x.fillStyle = g; x.fillRect(0, 0, 64, 64);
  const p = new THREE.PlaneGeometry(13, 13); p.rotateX(-Math.PI / 2);
  const m = new THREE.Mesh(p, new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(c), transparent: true, depthWrite: false })); m.renderOrder = 5; m.userData.noT = true; scene.add(m); window.__blob = m; return m;
})();

