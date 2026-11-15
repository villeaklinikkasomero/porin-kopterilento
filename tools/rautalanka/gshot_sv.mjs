import { createRequire } from 'module'; const { chromium } = createRequire('/home/claude/.npm-global/lib/node_modules/')('playwright');
import fs from 'fs';
// usage: ZONE=kivi1 node gshot_sv.mjs index.html outdir/ views.json   (ZONE: the bake block to wait for, window.__bl)
// exact Street View pose: x, y (game m), h heading, p pitch, fov vertical, ch camera height above the road
const [,, page_, out, viewsJson] = process.argv; const V = JSON.parse(fs.readFileSync(viewsJson));
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
await p.goto('http://localhost:8765/' + page_ + '?city', { waitUntil: 'load' });
await p.waitForFunction(() => window.__game && window.__heli, null, { timeout: 240000 });
for (const v of V){
 await p.evaluate(([x,y])=>{const g=window.__game; g.S.x=x; g.S.y=y;}, [v.x,v.y]);
 await p.waitForTimeout(1500);
 try { await p.waitForFunction(([x,y]) => window.__stream.filter(e=>Math.hypot(e.x-x,e.y-y)<260).every(e=>e.st===2||e.st===3), [v.x,v.y], { timeout: 60000, polling: 1000 }); } catch(e) { console.log('timeout',v.k); }
 try { await p.waitForFunction(() => (window.__bl||[]).includes(process.env.ZONE || 'kivi1'), null, { timeout: 120000 }); } catch(e) { console.log('nobl'); }
 await p.waitForTimeout(2000);
 const url=await p.evaluate((v)=>{const g=window.__game; if (v.back) { const a0=v.h*Math.PI/180; v.x-=v.back*Math.sin(a0); v.y-=v.back*Math.cos(a0); } const a=v.h*Math.PI/180, pp=(v.p||0)*Math.PI/180; const z=g.TZs(v.x,v.y)+(v.ch||2.5);
  g.scene.traverse(o=>{if(o.isGroup&&o.userData&&o.userData.noT&&o.rotation.order==='YXZ')o.visible=false;});
  g.camera.fov=v.fov||90; g.camera.aspect=16/9; g.camera.updateProjectionMatrix(); g.camera.position.set(v.x,z,-v.y);
  g.camera.lookAt(v.x+100*Math.sin(a)*Math.cos(pp), z+100*Math.sin(pp), -(v.y+100*Math.cos(a)*Math.cos(pp))); g.camera.updateMatrixWorld();
  g.renderer.setSize(1280,720,false); g.renderer.render(g.scene,g.camera); return g.renderer.domElement.toDataURL('image/jpeg',0.9);},v);
 fs.writeFileSync(out+v.k+'.jpg', Buffer.from(url.split(',')[1],'base64'));}
await b.close();
