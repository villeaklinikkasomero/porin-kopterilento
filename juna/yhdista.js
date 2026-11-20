// Staattisten osien yhdistäminen materiaaleittain (piirtokutsut: rata ~2 000 -> kymmeniä, juna ~870 -> ~60)
import * as THREE from '../three.module.min.js';
import { mergeGeometries } from '../BufferGeometryUtils.js';
export function yhdista(node, stop = () => false) {
  node.updateMatrixWorld(true); const inv = node.matrixWorld.clone().invert(), groups = new Map(), rm = [], tmp = new THREE.Matrix4();
  const walk = o => { for (const c of o.children.slice()) { if (stop(c)) continue; walk(c);
    if (c.isMesh && !c.isInstancedMesh && !c.isSkinnedMesh && !c.children.length && !Array.isArray(c.material) && c.visible) {
      let g = c.geometry.clone(); if (g.index) g = g.toNonIndexed(); tmp.multiplyMatrices(inv, c.matrixWorld); g.applyMatrix4(tmp);
      if (!g.attributes.normal) g.computeVertexNormals();
      const k = c.material; if (!groups.has(k)) groups.set(k, []); groups.get(k).push({ g, noT: c.userData.noT, ro: c.renderOrder }); rm.push(c); } } };
  walk(node);
  let made = 0;
  for (const [m, L] of groups) { if (L.length < 2) { continue; }
    const names = ['position', 'normal', 'uv', 'color'].filter(a => L.every(e => e.g.attributes[a]));
    const gs = L.map(e => { const g = new THREE.BufferGeometry(); for (const a of names) { const at = e.g.attributes[a]; g.setAttribute(a, at.itemSize === (a === 'color' ? 4 : at.itemSize) ? at : at); } return g; });
    // värien koko (3/4) yhteen
    if (names.includes('color')) { const sz = gs[0].attributes.color.itemSize; if (!gs.every(g => g.attributes.color.itemSize === sz)) gs.forEach(g => g.deleteAttribute('color')); }
    const mg = mergeGeometries(gs, false); if (!mg) continue;
    const me = new THREE.Mesh(mg, m); me.userData.noT = true; me.renderOrder = L[0].ro; node.add(me); made++;
    for (const e of L) e.used = true; }
  for (const c of rm) { const L = groups.get(c.material); if (L && L.length >= 2) c.parent.remove(c); }
  return made;
}
