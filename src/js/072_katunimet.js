// ---------- roads: index + street name labels on the ground ----------
const segs = [], sgrid = new Map(), SG = 60;
{
  const texCache = new Map(), placed = [];
  const flat = new THREE.PlaneGeometry(1, 1); flat.rotateX(-Math.PI / 2);
  for (const r of CITY.r) {
    const p = r.p; let len = 0; const cum = [0];
    for (let i = 0; i + 3 < p.length; i += 2) {
      const s = { ax: p[i], ay: p[i + 1], bx: p[i + 2], by: p[i + 3], n: r.n }; const si = segs.push(s) - 1;
      const x0 = Math.floor(Math.min(s.ax, s.bx) / SG), x1 = Math.floor(Math.max(s.ax, s.bx) / SG), y0 = Math.floor(Math.min(s.ay, s.by) / SG), y1 = Math.floor(Math.max(s.ay, s.by) / SG);
      for (let a = x0; a <= x1; a++) for (let b = y0; b <= y1; b++) { const k = gkey(a + 100, b + 100); if (!sgrid.has(k)) sgrid.set(k, []); sgrid.get(k).push(si); }
      len += Math.hypot(s.bx - s.ax, s.by - s.ay); cum.push(len);
    }
    if (len < 55) continue;
    // label at the midpoint of the way
    let i = 0; while (cum[i + 1] < len / 2) i++;
    const ax = p[i * 2], ay = p[i * 2 + 1], bx = p[i * 2 + 2], by = p[i * 2 + 3], f = (len / 2 - cum[i]) / (cum[i + 1] - cum[i] || 1);
    const mx = ax + (bx - ax) * f, my = ay + (by - ay) * f;
    if (!r.n || mx < OX0 + 20 || mx > OX1 - 20 || my < OY0 + 20 || my > OY1 - 20) continue;
    if (placed.some(q => q.n === r.n && Math.hypot(q.x - mx, q.y - my) < 190)) continue;
    placed.push({ n: r.n, x: mx, y: my });
    let ang = Math.atan2(by - ay, bx - ax); if (Math.cos(ang) < 0) ang += Math.PI;
    if (!texCache.has(r.n)) texCache.set(r.n, textCanvas(r.n, { size: 48 }));
    const t = texCache.get(r.n), hgt = r.k === 3 ? 5.2 : 4.2;
    const mesh = new THREE.Mesh(flat, new THREE.MeshBasicMaterial({ map: t.tex, transparent: true, depthWrite: false, opacity: 0.92 }));
    mesh.scale.set(hgt * t.aspect, 1, hgt); mesh.position.set(mx, 0.35, -my); mesh.rotation.y = ang; mesh.renderOrder = 2; scene.add(mesh);
  }
}
function nearestStreet(x, y) {
  let best = null, bd = 48 * 48; const ci = Math.floor(x / SG), cj = Math.floor(y / SG);
  for (let a = ci - 1; a <= ci + 1; a++) for (let b = cj - 1; b <= cj + 1; b++) {
    const l = sgrid.get(gkey(a + 100, b + 100)); if (!l) continue;
    for (const si of l) { const s = segs[si]; const dx = s.bx - s.ax, dy = s.by - s.ay; let t = ((x - s.ax) * dx + (y - s.ay) * dy) / (dx * dx + dy * dy || 1); t = Math.max(0, Math.min(1, t));
      const d = (s.ax + dx * t - x) ** 2 + (s.ay + dy * t - y) ** 2; if (d < bd) { bd = d; best = s.n; } }
  }
  return best;
}

