// ---------- ground (aerial image) ----------
const orto = new THREE.Texture();
orto.colorSpace = THREE.SRGBColorSpace;
orto.anisotropy = renderer.capabilities.getMaxAnisotropy();
const groundMat = new THREE.MeshBasicMaterial({ map: orto, color: 0x30383a });
const outerTex = new THREE.TextureLoader().load('./outer.jpg'); outerTex.colorSpace = THREE.SRGBColorSpace; outerTex.anisotropy = renderer.capabilities.getMaxAnisotropy();
const outerMat = new THREE.MeshBasicMaterial({ map: outerTex }), roofMat2 = new THREE.MeshBasicMaterial({ map: outerTex, side: THREE.DoubleSide });
{
  // ground with the river cut out: the core photo, the coarser frame around it, sloped banks / stone quays and the water
  const tris = (a, uvf, y = 0) => { const p = [], u = []; for (let i = 0; i < a.length; i += 2) { p.push(a[i], y, -a[i + 1]); u.push(...uvf(a[i], a[i + 1])); }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(p, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(u, 2)); return g; };
  const cuv = (x, y) => [(x + HW) / (2 * HW), (y - YS) / YSPAN], ouv = (x, y) => [(x - OX0) / OXS, (y - OY0) / OYS];
  // ground as height grids from the elevation model: 6 m cells in the core, 18 m around it; the Eteläranta quay strip is left open
  gridGeo = (x0, y0, x1, y1, step, uvf, skipf, dy = 0) => { const nx = Math.round((x1 - x0) / step), ny = Math.round((y1 - y0) / step), P = [], U = [], I = [];
    for (let j = 0; j <= ny; j++) for (let i = 0; i <= nx; i++) { const x = x0 + i * step, y = y0 + j * step; P.push(x, TZg(x, y) + dy, -y); U.push(...uvf(x, y)); }
    for (let j = 0; j < ny; j++) for (let i = 0; i < nx; i++) { const x = x0 + (i + 0.5) * step, y = y0 + (j + 0.5) * step; if (skipf && skipf(x, y)) continue;
      const k = j * (nx + 1) + i; I.push(k, k + 1, k + nx + 2, k, k + nx + 2, k + nx + 1); }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(U, 2)); g.setIndex(I); g.rotateX(0); return g; };
  scene.add(noT(new THREE.Mesh(gridGeo(-HW, YS, HW, YN, 6, cuv, tSkip), groundMat)));
  const RSK = new Set(RATA.osk || []), onx = Math.round((OX1 - OX0) / 18);   // rataverkon kohdalla 18 m solut pois: rata/rata.js rakentaa niihin 6 m ruudukon (ratapenkka painettu)
  scene.add(noT(new THREE.Mesh(gridGeo(OX0, OY0, OX1, OY1, 18, ouv, (x, y) => (Math.abs(x) < HW - 9 && y > YS + 9 && y < YN - 9) || RSK.has(Math.floor((y - OY0) / 18) * onx + Math.floor((x - OX0) / 18))), outerMat)));
  { const pc = [], po = [], A = RIV.water;               // the water keeps the river's own colours from the photo, with the sky in it
    for (let i = 0; i < A.length; i += 6) { const cx = (A[i] + A[i + 2] + A[i + 4]) / 3, cy = (A[i + 1] + A[i + 3] + A[i + 5]) / 3; (inCore(cx, cy) ? pc : po).push(...A.slice(i, i + 6)); }
    scene.add(noT(new THREE.Mesh(tris(pc, cuv, TER.wl), waterify(new THREE.MeshBasicMaterial({ map: orto })))));
    scene.add(noT(new THREE.Mesh(tris(po, ouv, TER.wl), waterify(new THREE.MeshBasicMaterial({ map: outerTex }))))); }
  // road and railway bridges over land (blender/bridges_fix.py, TER.bd): the ground keeps its cutting with the road or track underneath; the deck is
  // drawn at its own height with the aerial photo on it (the bridge is in the photo), concrete edge beams under it and a low parapet on both sides
  if (TER.bd && TER.bd.length) { const dc = [[], []], du = [[], []], cp = [], cm = new THREE.MeshLambertMaterial({ color: 0x9d9b94, side: THREE.DoubleSide });
    const quad = (A, B, C, D, arr) => arr.push(...A, ...B, ...C, ...A, ...C, ...D);
    for (const r of TER.bd) { if ((RATA.bdSkip || []).some(([x, y]) => Math.hypot(r[1] - x, r[2] - y) < 1.5)) continue;   /* rautatiesillat: rata/rata.js rakentaa omansa */
      const hw = r[0], P = []; for (let k = 1; k + 2 < r.length; k += 3) P.push([r[k], r[k + 1], r[k + 2]]);
      const off = P.map((p, k) => { const a = P[Math.max(0, k - 1)], b = P[Math.min(P.length - 1, k + 1)], dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy) || 1; return [dy / l * hw, -dx / l * hw]; });
      for (let k = 0; k + 1 < P.length; k++) { const [ax, ay, az] = P[k], [bx, by, bz] = P[k + 1], [ox, oy] = off[k], [px, py] = off[k + 1], zt = 0.12;
        const L1 = [ax + ox, ay + oy], R1 = [ax - ox, ay - oy], L2 = [bx + px, by + py], R2 = [bx - px, by - py], core = inCore((ax + bx) / 2, (ay + by) / 2) ? 0 : 1, uvf = core ? ouv : cuv;
        for (const [x, y, z] of [[...L1, az], [...L2, bz], [...R2, bz], [...L1, az], [...R2, bz], [...R1, az]]) { dc[core].push(x, z + zt, -y); du[core].push(...uvf(x, y)); }
        for (const [S1, S2] of [[L1, L2], [R1, R2]]) {
          quad([S1[0], az - 0.95, -S1[1]], [S2[0], bz - 0.95, -S2[1]], [S2[0], bz + zt, -S2[1]], [S1[0], az + zt, -S1[1]], cp);          // edge beam
          quad([S1[0], az + zt, -S1[1]], [S2[0], bz + zt, -S2[1]], [S2[0], bz + 1.0, -S2[1]], [S1[0], az + 1.0, -S1[1]], cp); }        // parapet
        quad([L1[0], az - 0.95, -L1[1]], [L2[0], bz - 0.95, -L2[1]], [R2[0], bz - 0.95, -R2[1]], [R1[0], az - 0.95, -R1[1]], cp); } }   // underside
    for (let c = 0; c < 2; c++) if (dc[c].length) { const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(dc[c], 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(du[c], 2)); scene.add(noT(new THREE.Mesh(g, c ? outerMat : groundMat))); }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(cp, 3)); g.computeVertexNormals(); scene.add(noT(new THREE.Mesh(g, cm))); }
  const o = new THREE.PlaneGeometry(14000, 14000); o.rotateX(-Math.PI / 2);
  const om = noT(new THREE.Mesh(o, new THREE.MeshBasicMaterial({ color: 0x74836f }))); om.position.y = -12; scene.add(om);
}

