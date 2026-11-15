// Which meshes of the running game cover a plan point? (to find who draws a surface: Blender block, landmark, LoD2 roof drape, stand-in)
// usage: node scene_meshes.mjs X Y [zone]    (game metres; local server on 8765 serving the game folder)
import { createRequire } from 'module'; const { chromium } = createRequire('/home/claude/.npm-global/lib/node_modules/')('playwright');
const [,, X, Y, Z] = process.argv; const x = +X, y = +Y;
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const p = await b.newPage(); await p.goto('http://localhost:8765/index.html?city'); await p.waitForFunction(() => window.__game, null, { timeout: 240000 });
await p.evaluate(([x, y]) => { const g = window.__game; g.S.x = x; g.S.y = y; }, [x, y]);
await p.waitForFunction(z => (window.__bl || []).includes(z), Z || 'kivi1', { timeout: 120000 }); await p.waitForTimeout(3000);
console.log(await p.evaluate(([x, y]) => { const out = []; const sc = window.__game.scene; sc.updateMatrixWorld(true);
  sc.traverse(o => { if (!o.isMesh || !o.visible) return; const g = o.geometry; if (!g.boundingBox) g.computeBoundingBox(); const bb = g.boundingBox.clone().applyMatrix4(o.matrixWorld);
    if (bb.min.x < x && bb.max.x > x && bb.min.z < -y && bb.max.z > -y && bb.max.x - bb.min.x < 1000) out.push([o.material.type, !!o.material.map, (o.parent && o.parent.type) || '', bb.min.y.toFixed(1), bb.max.y.toFixed(1), (bb.max.x - bb.min.x).toFixed(0), g.attributes.position.count]); });
  return JSON.stringify(out, null, 1); }, [x, y]));
await b.close();
