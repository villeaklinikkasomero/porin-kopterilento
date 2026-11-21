// ---------- ground (aerial image) ----------
const orto = new THREE.Texture();
orto.colorSpace = THREE.SRGBColorSpace;
orto.anisotropy = renderer.capabilities.getMaxAnisotropy();
const groundMat = new THREE.MeshBasicMaterial({ map: orto, color: 0x30383a });
const outerTex = new THREE.TextureLoader().load('./maa/ot_s/outer.jpg'); outerTex.colorSpace = THREE.SRGBColorSpace; outerTex.anisotropy = renderer.capabilities.getMaxAnisotropy();
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
  scene.add(noT(new THREE.Mesh(gridGeo(OX0, OY0, OX1, OY1, 18, ouv, (x, y) => (Math.abs(x) < HW - 9 && y > YS + 9 && y < YN - 9) || RSK.has(Math.floor((y - OY0) / 18) * onx + Math.floor((x - OX0) / 18)) || (window.__alikSkip18 && window.__alikSkip18(x, y))), outerMat)));      // 21.11.2026: alikulut (0106/0336)
  { const pc = [], po = [], A = RIV.water;               // the water keeps the river's own colours from the photo, with the sky in it
    for (let i = 0; i < A.length; i += 6) { const cx = (A[i] + A[i + 2] + A[i + 4]) / 3, cy = (A[i + 1] + A[i + 3] + A[i + 5]) / 3; (inCore(cx, cy) ? pc : po).push(...A.slice(i, i + 6)); }
    scene.add(noT(new THREE.Mesh(tris(pc, cuv, TER.wl), waterify(new THREE.MeshBasicMaterial({ map: orto })))));
    scene.add(noT(new THREE.Mesh(tris(po, ouv, TER.wl), waterify(new THREE.MeshBasicMaterial({ map: outerTex }))))); }
  // road bridges over land (TER.bd): js/0301_sillat.js (21.11.2026: betoni, asfalttikansi, auto pysyy kannella)
  const o = new THREE.PlaneGeometry(14000, 14000); o.rotateX(-Math.PI / 2);
  const om = noT(new THREE.Mesh(o, new THREE.MeshBasicMaterial({ color: 0x74836f }))); om.position.y = -12; scene.add(om);
}

