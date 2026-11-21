// embedded Blender models: base64 glb inside a script file
// whole-city blocks: fetched when the helicopter comes within 600 m, dropped again beyond 850 m (the plain walls stay as a stand-in)
const CITY_ON = !new URLSearchParams(location.search).has('nocity') && (!isTouch || new URLSearchParams(location.search).has('city'));   // phones and tablets skip the streamed blocks (the browser ran out of memory mid-flight); ?city forces them on   // whole-city blocks (2048 px bakes); ?nocity turns them off
function shrinkMap(map, max) {   // the city atlases are 4096 px: downscale before the GPU upload (64 MB -> 4 MB per block)
  const im = map && map.image; if (!im || !(im.width > max)) return;
  const c = document.createElement('canvas'); c.width = c.height = max; c.getContext('2d').drawImage(im, 0, 0, max, max);
  if (im.close) im.close(); map.image = c; map.flipY = false; map.needsUpdate = true;
}
// One ground height per house for the baked blocks that list their houses (bl_*.js "shells", baked with a plinth skirt; owner 14.11.2026): the terrain shader lifted every vertex by the ground under it,
// so on the slopes down to the river whole houses leaned. Each vertex now takes the highest ground under its own building (OSM
// footprint, or the nearest one within 2 m); the baked plinth skirt below z = 0 fills the gap downhill, so only the plinth follows the slope.
function bldAt(x, y) {
  const L = grid.get(gkey(Math.floor(x / GRID) + 100, Math.floor(y / GRID) + 100)); if (!L) return null; let best = null, bd = 2.0;
  for (const bi of L) { const r = blds[bi]; if (x < r.minx - 2 || x > r.maxx + 2 || y < r.miny - 2 || y > r.maxy + 2) continue;
    if (pip(x, y, r.pts)) return r;
    for (let i = 0, j = r.pts.length - 1; i < r.pts.length; j = i++) { const a = r.pts[j], b = r.pts[i], dx = b[0] - a[0], dy = b[1] - a[1];
      const t = Math.max(0, Math.min(1, ((x - a[0]) * dx + (y - a[1]) * dy) / (dx * dx + dy * dy || 1))), d = Math.hypot(a[0] + dx * t - x, a[1] + dy * t - y);
      if (d < bd) { bd = d; best = r; } } }
  return best;
}
function bLift(r) { if (r.lift === undefined) { let m = -1e9; for (const q of r.pts) m = Math.max(m, TZs(q[0], q[1])); r.lift = m; } return r.lift; }
function shellAt(S, x, y, z) {   // S: houses from the bake (bl_*.js 'shells'), each a list of rings: the one containing (x, y), else the nearest within 2 m
  let best = null, bd = 2.0;
  for (const h of S) { if (x < h.bb[0] - 2 || x > h.bb[2] + 2 || y < h.bb[1] - 2 || y > h.bb[3] + 2) continue;
    if (h.zt !== undefined && z !== undefined && z > h.zt) continue;   // free walls/gates (16.11): only their own height
    for (const R of h.pts) { if (pip(x, y, R)) return h;
      for (let i = 0, j = R.length - 1; i < R.length; j = i++) { const a = R[j], b = R[i], dx = b[0] - a[0], dy = b[1] - a[1];
        const t = Math.max(0, Math.min(1, ((x - a[0]) * dx + (y - a[1]) * dy) / (dx * dx + dy * dy || 1))), d = Math.hypot(a[0] + dx * t - x, a[1] + dy * t - y);
        if (d < bd) { bd = d; best = h; } } } }
  return best;
}
function liftBlock(gr, shells) {
  gr.updateMatrixWorld(true); const v = new THREE.Vector3();
  const S = (shells || []).map(e => { const rs = e.r || e; const pts = rs.map(r => { const o = []; for (let i = 0; i < r.length; i += 2) o.push([r[i], r[i + 1]]); return o; });
    let m = -1e9; const bb = [1e9, 1e9, -1e9, -1e9]; for (const R of pts) for (const q of R) { m = Math.max(m, TZs(q[0], q[1])); bb[0] = Math.min(bb[0], q[0]); bb[1] = Math.min(bb[1], q[1]); bb[2] = Math.max(bb[2], q[0]); bb[3] = Math.max(bb[3], q[1]); }
    return { pts, bb, nb: e.nb ? 1 : 0, zt: e.zt, lift: (e.l !== undefined && e.l !== null) ? e.l : m }; });   // e.l: the house's own ground from the bake (lowest ground under it)
  gr.traverse(q => { if (!q.isMesh) return;
    if (q.geometry.index) q.geometry = q.geometry.toNonIndexed();   // one lift per triangle (its centre decides the house): a wall on a house's edge never shears
    const P = q.geometry.attributes.position, A = new Float32Array(P.count), NB = new Float32Array(P.count), w = new THREE.Vector3();
    for (let i = 0; i + 2 < P.count; i += 3) { v.set(0, 0, 0); for (let k = 0; k < 3; k++) v.add(w.fromBufferAttribute(P, i + k)); v.multiplyScalar(1 / 3).applyMatrix4(q.matrixWorld);
      const h = S.length ? shellAt(S, v.x, -v.z, v.y) : null; const r = h ? null : bldAt(v.x, -v.z); A[i] = A[i + 1] = A[i + 2] = h ? h.lift : r ? bLift(r) : TZs(v.x, -v.z); if (h && h.nb) NB[i] = NB[i + 1] = NB[i + 2] = 1; }
    q.geometry.setAttribute('tLift', new THREE.BufferAttribute(A, 1)); q.geometry.setAttribute('tNB', new THREE.BufferAttribute(NB, 1));   /* tNB: rendered brick-red house, no brick bond */ q.material.defines = Object.assign(q.material.defines || {}, { T_LIFT: '' }); });
}
function streamUpdate(x, y) {
  if (!CITY_ON) return;
  let busy = STREAM.filter(e => e.st === 1).length;
  for (const e of STREAM.slice().sort((a, b) => Math.hypot(a.x - x, a.y - y) - Math.hypot(b.x - x, b.y - y))) {
    const d = Math.hypot(e.x - x, e.y - y);
    if (d < 600 && e.st === 0 && busy < 2) { e.st = 1; busy++;
      fetch(`./bl_${e.name}.js`).then(r => r.ok ? r.text() : Promise.reject()).then(t => {
        const ax = +t.match(/x = (-?[\d.]+)/)[1], ay = +t.match(/y = (-?[\d.]+)/)[1], di = t.indexOf('export default "'), b64 = t.slice(di + 16, t.lastIndexOf('"'));
        const si = t.indexOf('export const shells = '), shells = si >= 0 && si < di ? JSON.parse(t.slice(si + 22, t.indexOf(';', si))) : null;   /* 17.11.2026: a block with a shells line was read from its first quote and fell back to plain walls (c039); 18.11: ';' not ';\n' - a bake written on Windows has CRLF lines and failed to load (Keskuskartano as hollow plain walls) */
        const bin = atob(b64), buf = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
        new GLTFLoader().parse(buf.buffer, '', gl => {
          if (e.st !== 1) return;
          gl.scene.traverse(q => { if (q.isMesh) { const map = q.material.map; if (map) { if (isTouch) { shrinkMap(map, 512); map.anisotropy = 4; } else { shrinkMap(map, 2048); map.anisotropy = 8; TEXLOD.add(map, e.x, e.y); } } q.material = brickify(glassify(new THREE.MeshBasicMaterial({ map }))); } });   /* 18.11.2026 (owner: sharper facades): desktop blocks join TEXLOD - the nearest get the full 2048 px atlas, the rest a 512 px copy (was 1024 for all) */
          const gr = new THREE.Group(); gr.position.set(ax, 0, -ay); gr.add(gl.scene); if (shells) liftBlock(gr, shells); scene.add(gr); e.me.visible = false; e.gr = gr; e.st = 2; }, () => { e.st = 0; });
      }).catch(err => { if (err) console.warn('bake ' + e.name + ': ' + err); e.st = 3; });   // not baked yet (or unreadable): keep the plain walls
    } else if (d > 850 && e.st === 2) {
      scene.remove(e.gr); e.gr.traverse(q => { if (q.isMesh) { q.geometry.dispose(); if (q.material.map) { const m_ = q.material.map; TEXLOD.L = TEXLOD.L.filter(t => t.map !== m_); m_.dispose(); } q.material.dispose(); } });
      e.gr = null; e.me.visible = true; e.st = 0;
    }
  }
}
function loadModel(name, done) {
  import(`./${name}.js`).then(K => { const bin = atob(K.default), buf = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
    new GLTFLoader().parse(buf.buffer, '', gl => done(gl.scene, K), () => {}); }).catch(() => {});
}
