// 19.11.2026 (owner: "more believable smoke"): soft camera-facing puffs instead of solid balls. One procedural texture (overlapping radial blobs, so the edge is
// ragged), each puff turns, swells, drifts with the wind, rises ever slower and thins out; it starts dark at the engine and pales as it spreads.
const SMOKE = { P: [], t: 0, tex: null };
function smokeStep(dt, every, dark, x, y, z) {
  if (every > 0) { SMOKE.t -= dt; if (SMOKE.t <= 0) { SMOKE.t = every * (0.7 + Math.random() * 0.6);
    if (!SMOKE.tex) { const c = document.createElement('canvas'); c.width = c.height = 128; const g = c.getContext('2d');
      for (let i = 0; i < 16; i++) { const a = Math.random() * 6.283, r = i ? 10 + Math.random() * 26 : 0, bx = 64 + Math.cos(a) * r, by = 64 + Math.sin(a) * r, br = 20 + Math.random() * 16, gr = g.createRadialGradient(bx, by, 0, bx, by, br);
        gr.addColorStop(0, 'rgba(255,255,255,0.5)'); gr.addColorStop(0.55, 'rgba(255,255,255,0.2)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, 128, 128); }
      SMOKE.tex = new THREE.CanvasTexture(c); }
    let m = SMOKE.P.find(q => q.life <= 0); if (!m && SMOKE.P.length < 40) { m = new THREE.Sprite(new THREE.SpriteMaterial({ map: SMOKE.tex, transparent: true, depthWrite: false })); m.userData.noT = true; m.material.userData.noT = true; m.life = 0; m.renderOrder = 5; scene.add(m); SMOKE.P.push(m); }
    if (m) { m.life = 1; m.rate = 0.3 + Math.random() * 0.18; m.dark = dark; m.s0 = 0.8 + Math.random() * 0.4; m.rot = (Math.random() - 0.5) * 1.6; m.material.rotation = Math.random() * 6.283;
      m.vx = 0.4 + (Math.random() - 0.5) * 0.7; m.vz = 0.2 + (Math.random() - 0.5) * 0.7; m.vy = 1.5 + Math.random() * 0.9;
      m.position.set(x + (Math.random() - 0.5) * 0.5, z + 0.1 + Math.random() * 0.15, -y + (Math.random() - 0.5) * 0.5); m.visible = true; } } }
  for (const m of SMOKE.P) if (m.life > 0) { m.life -= dt * m.rate; const a = 1 - m.life;
    m.vy = Math.max(0.35, m.vy - dt * 0.35); m.position.x += m.vx * dt * (0.4 + a); m.position.z += m.vz * dt * (0.4 + a); m.position.y += m.vy * dt;
    m.scale.setScalar(m.s0 + Math.pow(a, 0.7) * (m.dark ? 4.2 : 3.2)); m.material.rotation += m.rot * dt;
    m.material.opacity = Math.min(1, a * 9) * Math.pow(Math.max(0, m.life), 1.4) * (m.dark ? 0.85 : 0.5);
    const k = m.dark ? 0.07 + a * 0.26 : 0.5 + a * 0.32; m.material.color.setRGB(k, k, k * 1.02);
    if (m.life <= 0) m.visible = false; }
}
window.__smoke = smokeStep;
